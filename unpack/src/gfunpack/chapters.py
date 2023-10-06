import dataclasses
import json
import logging
import re
import typing

import hjson

from gfunpack.stories import Stories

_logger = logging.getLogger('gfunpack.prefabs')
_warning = _logger.warning

_chapter_info_file = 'story_playback.hjson'
_event_info_file = 'story_util.hjson'
_bonding_chapter_file = 'fetter.hjson'
_bonding_info_file = 'fetter_story.hjson'
_gun_info_file = 'gun.hjson'
_upgrade_info_file = 'mindupdate_story_info.hjson'

_chapter_file_name_regex = re.compile('^(-?\\d+)-')


T = typing.TypeVar('T')

@dataclasses.dataclass
class ChapterInfo:
    id: int = 0
    name: str = ''
    type: int = 0
    story_campaign_id: str = '0'
    chapter: str = '0'


_extra_chapters = {
    '-8': '猎兔行动',
    '-14,-15': '独法师',
    '-19,-20,-22': '荣耀日',
    '-32': '瓦尔哈拉',
    '-38': '梦间剧',
    '-43': '暗金潮',
    '-46': '小邪神前线',
    '-57': '雪浪映花颜',
}
_extra_stories = {
    '-32': {
        '迪奥杜里管吹奏指南-调酒': 'va11/va11_1.txt',
        '青春期-调酒': 'va11/va11_2.txt',
        '先驱者-调酒': 'va11/va11_3.txt',
        '音爆-调酒': 'va11/va11_4.txt',
        '鸡胸肉-调酒': 'va11/va11_5.txt',
        '公众演讲恐惧症-调酒': 'va11/va11_6.txt',
        '真心话大冒险-调酒': 'va11/va11_7.txt',
        '世上的最后一场雨-调酒': 'va11/va11_8.txt',
    },
}


@dataclasses.dataclass
class EventStoryInfo:
    id: int = 0
    mission_id: str = '0'
    description: str = ''
    scripts: str = ''
    bgm: str = ''
    title: str = ''
    start: str = ''
    first: str = ''
    end: str = ''
    is_util: int = 0
    campaign: int = 0
    point: str = ''
    round: str = ''
    step_start_story: str = ''


@dataclasses.dataclass
class UpgradingEvent:
    id: str = '0'
    gun_id: str = '0'
    stage_id: str = '0'
    scripts: str = ''
    prize_id: str = ''


@dataclasses.dataclass
class BondingChapter:
    id: int = 0
    name: str = ''
    actor: str = ''
    code: str = ''
    milestone1: int = 0
    milestone1_reward: str = ''
    milestone2: int = 0
    milestone2_reward: str = ''
    milestone3: int = 0
    milestone3_reward: str = ''
    milestone4: int = 0
    milestone4_reward: str = ''
    milestone5: int = 0
    milestone5_reward: str = ''


@dataclasses.dataclass
class BondingEvent:
    id: int = 0
    fetter_id: int = 0
    actor: str = ''
    milestone: int = 0
    reward: int = 0
    name: str = ''
    description: str = ''


@dataclasses.dataclass
class Story:
    name: str
    description: str
    files: list[str]


@dataclasses.dataclass
class Chapter:
    name: str
    description: str
    stories: list[Story]


class Chapters:
    stories: Stories

    chapters: list[ChapterInfo]

    main_events: list[EventStoryInfo]

    bonding_chapters: list[BondingChapter]

    bonding_events: list[BondingEvent]

    all_chapters: dict[str, list[Chapter]]

    upgrading_events: list[UpgradingEvent]

    gun_info: list[dict[str, typing.Any]]

    def __init__(self, stories: Stories) -> None:
        self.stories = stories
        self.chapters = self._fetch(_chapter_info_file, ChapterInfo)
        self.main_events = self._fetch(_event_info_file, EventStoryInfo)
        self.bonding_chapters = self._fetch(_bonding_chapter_file, BondingChapter)
        self.bonding_events = self._fetch(_bonding_info_file, BondingEvent)
        self.upgrading_events = self._fetch(_upgrade_info_file, UpgradingEvent)
        self.gun_info = self._fetch(_gun_info_file, dict)
        self.all_chapters = self.categorize_stories()

    def _fetch(self, file: str, item_type: typing.Type[T]) -> list[T]:
        with self.stories.gf_data_directory.joinpath('formatted', file).open() as f:
            data = hjson.loads(f.read())
            assert isinstance(data, list)
            return [item_type(**item) for item in data]

    @classmethod
    def _parse_point_scripts(cls, point: str):
        return [s.split(':')[1] for s in point.split(',') if s != '']

    @classmethod
    def _parse_event_stories(cls, story: EventStoryInfo, mapped_files: set[str]):
        scripts = [s.strip().lower() for s in story.scripts.split(',')]
        if story.first != '' and story.first not in scripts:
            scripts.insert(0, story.first)
        if story.start != '' and story.start not in scripts:
            scripts.insert(0, story.start)
        for extra in (story.point, story.step_start_story, story.round):
            scripts.extend(cls._parse_point_scripts(extra))
        if story.end != '' and story.end not in scripts:
            scripts.append(story.end)
        all_files = [f'{s.strip().lower()}.txt' for s in scripts if s.strip() != '']
        filtered = [f for f in all_files if f not in mapped_files]
        mapped_files.update(all_files)
        return filtered
    
    @classmethod
    def _unknown_chapter(cls, campaign: int, title: str):
        auto_id = 10000
        if campaign > 0:
            auto_id += campaign
        else:
            auto_id += 10000 + (-campaign)
        return auto_id, Chapter(
            name=f'未知: {title}',
            description='未能解析活动名称',
            stories=[],
        )

    def _categorize_main_stories(self):
        chapters: dict[int, Chapter] = {}
        id_mapping: dict[str, int] = {}
        mapped_files: set[str] = set()
        for keys, name in _extra_chapters.items():
            chapter_id = -int(int(keys.split(',')[0])) + 5000
            chapters[chapter_id] = Chapter(name=name, description='', stories=[])
            for key in keys.split(','):
                id_mapping[key] = chapter_id
        for chapter in self.chapters:
            chapters[chapter.id] = Chapter(
                name=chapter.name,
                description=chapter.chapter,
                stories=[],
            )
            for campaign_id in chapter.story_campaign_id.split(','):
                id_mapping[campaign_id] = chapter.id
        for story in sorted(self.main_events, key=lambda e: e.id):
            files = self._parse_event_stories(story, mapped_files)
            if len(files) == 0:
                continue
            if story.campaign == -43: # 暗金潮命名有问题
                story.title, story.description = story.description, story.title
            campaign = str(story.campaign)
            if campaign not in id_mapping:
                chapter_id, chapter = self._unknown_chapter(story.campaign, story.title)
                chapters[chapter_id], id_mapping[campaign] = chapter, chapter_id
            chapters[id_mapping[campaign]].stories.append(Story(
                name=files[0] if story.title == '' else story.title,
                description=story.description,
                files=files,
            ))
        for chapter_str, stories in _extra_stories.items():
            chapter_id = id_mapping[chapter_str]
            chapter = chapters[chapter_id]
            for name, file in stories.items():
                if file not in mapped_files:
                    chapter.stories.append(Story(
                        name=name,
                        description=file,
                        files=[file],
                    ))
        others = set(self.stories.extracted.keys()) - mapped_files
        for file in sorted(others):
            if '/' in file:
                continue
            match = _chapter_file_name_regex.match(file)
            if match is None:
                continue
            campaign = match.group(1)
            if campaign not in id_mapping:
                chapter_id, chapter = self._unknown_chapter(int(campaign), campaign)
                chapters[chapter_id], id_mapping[campaign] = chapter, chapter_id
            chapters[id_mapping[campaign]].stories.append(Story(
                name=file,
                description='',
                files=[file],
            ))

        return [v for _, v in sorted(chapters.items(), key=lambda e: e[0])]

    def _categorize_bonding_stories(self):
        chapters: dict[int, Chapter] = {}
        for chapter in self.bonding_chapters:
            chapters[chapter.id] = Chapter(
                name=chapter.name,
                description='',
                stories=[],
            )
        for story in sorted(self.bonding_events, key=lambda e: e.id):
            if story.fetter_id not in chapters:
                continue
            chapters[story.fetter_id].stories.append(Story(
                name=story.name,
                description=story.description,
                files=[f'fetter/{story.fetter_id}/{story.id}.txt'],
            ))
        return [v for _, v in sorted(chapters.items(), key=lambda e: e[0])]

    def _categorize_upgrading_stories(self):
        chapters: dict[int, Chapter] = {}
        guns = dict((int(gun['id']), gun) for gun in self.gun_info)
        for story in self.upgrading_events:
            gun_id = int(story.gun_id) % 20000
            if gun_id not in chapters:
                chapters[gun_id] = Chapter(
                    name=guns[gun_id]['name'],
                    description='',
                    stories=[],
                )
            chapters[gun_id].stories.append(Story(
                name=f'阶段 {story.stage_id}',
                description=guns[gun_id]['name'] + ' 心智升级',
                files=[f'memoir/{story.scripts}.txt'],
            ))
        return [v for _, v in sorted(chapters.items(), key=lambda e: e[0])]

    def categorize_stories(self):
        all_chapters: dict[str, list[Chapter]] = {}
        all_chapters['main'] = self._categorize_main_stories()
        all_chapters['bonding'] = self._categorize_bonding_stories()
        all_chapters['upgrading'] = self._categorize_upgrading_stories()
        return all_chapters

    def save(self):
        all_chapters: dict[str, list[dict]] = {}
        all_file_list: list[str] = []
        for chapters in self.all_chapters.values():
            for chapter in chapters:
                for story in chapter.stories:
                    story.files = [f for f in story.files if f in self.stories.extracted]
                    all_file_list.extend(story.files)
        all_files = set(all_file_list)
        others = set(self.stories.extracted.keys()) - all_files
        self.all_chapters['main'].append(Chapter(
            name='未能归类',
            description='程序未能自动归类的故事',
            stories=[
                Story(name=file, description='', files=[file])
                for file in sorted(others)
            ],
        ))
        for k, chapters in self.all_chapters.items():
            chapter_dicts = [dataclasses.asdict(c) for c in chapters]
            all_chapters[k] = chapter_dicts
        with self.stories.destination.joinpath('chapters.json').open('w') as f:
            f.write(json.dumps(all_chapters, ensure_ascii=False))
