import dataclasses
import json
import logging
import re
import typing

import hjson

from gfunpack.stories import Stories
from gfunpack.manual_chapters import (
    Chapter, Story, add_extra_chapter_mappings,
    get_block_list, get_recorded_chapters, post_insert,
    is_manual_processed, manually_process, manual_naming,
    fill_in_chapter_info,
)

_logger = logging.getLogger('gfunpack.prefabs')
_warning = _logger.warning

_chapter_info_file = 'story_playback.hjson'
_event_info_file = 'story_util.hjson'
_bonding_chapter_file = 'fetter.hjson'
_bonding_info_file = 'fetter_story.hjson'
_gun_info_file = 'gun.hjson'
_npc_info_file = 'npc.hjson'
_sangvis_info_file = 'sangvis.hjson'
_skins_info_file = 'skin.hjson'
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
    tag: str = ''
    order: int = 1000000


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


class Chapters:
    stories: Stories

    chapters: list[ChapterInfo]

    main_events: list[EventStoryInfo]

    bonding_chapters: list[BondingChapter]

    bonding_events: list[BondingEvent]

    all_chapters: dict[str, list[Chapter]]

    upgrading_events: list[UpgradingEvent]

    gun_info: list[dict[str, typing.Any]]
    npc_info: list[dict[str, typing.Any]]
    sangvis_info: list[dict[str, typing.Any]]
    skin_info: list[dict[str, typing.Any]]
    guns: dict[int, dict[str, typing.Any]]
    npcs: dict[int, dict[str, typing.Any]]
    sangvis: dict[int, dict[str, typing.Any]]
    skins: dict[int, dict[str, typing.Any]]

    def __init__(self, stories: Stories) -> None:
        self.stories = stories
        self.chapters = self._fetch(_chapter_info_file, ChapterInfo)
        self.main_events = self._fetch(_event_info_file, EventStoryInfo)
        self.bonding_chapters = self._fetch(_bonding_chapter_file, BondingChapter)
        self.bonding_events = self._fetch(_bonding_info_file, BondingEvent)
        self.upgrading_events = self._fetch(_upgrade_info_file, UpgradingEvent)
        self.gun_info, self.guns = self._fetch_and_index(_gun_info_file)
        self.npc_info, self.npcs = self._fetch_and_index(_npc_info_file)
        self.sangvis_info, self.sangvis = self._fetch_and_index(_sangvis_info_file)
        self.skin_info, self.skins = self._fetch_and_index(_skins_info_file)
        self.all_chapters = self.categorize_stories()

    def _fetch(self, file: str, item_type: typing.Type[T]) -> list[T]:
        with self.stories.gf_data_directory.joinpath('formatted', file).open() as f:
            data = hjson.loads(f.read())
            assert isinstance(data, list)
            return [item_type(**item) for item in data]

    def _fetch_and_index(self, file: str):
        items = self._fetch(file, dict)
        index = dict((int(i['id']), i) for i in items)
        return items, index

    @classmethod
    def _parse_point_scripts(cls, point: str):
        return [s.split(':')[1].strip() for s in point.split(',') if s != '']

    @classmethod
    def _parse_event_stories(cls, story: EventStoryInfo, mapped_files: set[str]):
        scripts = [s.strip() for s in story.scripts.split(',')]
        if story.first != '' and story.first not in scripts:
            scripts.insert(0, story.first)
        if story.start != '' and story.start not in scripts:
            scripts.insert(0, story.start)
        for extra in (story.point, story.step_start_story, story.round):
            scripts.extend(s for s in cls._parse_point_scripts(extra) if s not in scripts)
        if story.end != '' and story.end not in scripts:
            scripts.append(story.end)
        all_files = [f'{s.strip().lower()}.txt' for s in scripts if s.strip() != '']
        filtered = [f for f in all_files if f not in mapped_files]
        if len(filtered) != 0 and len(filtered) != len(all_files):
            _warning('potential duplicate story entries: %s (%s != %s)', story.title, filtered, all_files)
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

    def _categorize_anniversary(self, directory: str = 'anniversary'):
        categories: dict[str, list[tuple[int, str, str]]] = {}
        for path in self.stories.extracted.keys():
            if not path.startswith(f'{directory}/'):
                continue
            _, filename = path.split('/')
            name = filename.split('.')[0]
            if name.startswith('default_'):
                name = name[len('default_'):]
            if name.isdigit() and int(name) in self.guns:
                i = int(name)
                name = self.guns[i]['name']
                t = '人形'
            elif name.startswith('-') and int(name) in self.npcs:
                i = int(name)
                name = self.npcs[i]['name']
                t = '人类协助者'
            elif name.startswith('s') and int(name[2:]) in self.sangvis:
                i = int(name[2:])
                name = self.sangvis[i]['name']
                t = '协议同归'
            else:
                i = 0
                t = '未知'
            if t not in categories:
                categories[t] = []
            categories[t].append((i, path, name))
        chapters: list[Chapter] = []
        for name, roles in categories.items():
            chapter = Chapter(name=name, description='', stories=[])
            chapters.append(chapter)
            for _, path, name in sorted(roles):
                chapter.stories.append(Story(name=name, description='', files=[path]))
        return chapters

    def _categorize_skins(self):
        chapters: dict[int, Chapter] = {}
        for path in self.stories.extracted.keys():
            if not path.startswith('skin/'):
                continue
            _, filename = path.split('/')
            name = filename.split('.')[0]
            skin = self.skins[int(name)]
            gun_id = skin['fit_gun']
            name = skin['name']
            description = skin['dialog']
            note = skin.get('note', '')
            if gun_id not in chapters:
                if gun_id > 0:
                    character = self.guns[gun_id]['name']
                else:
                    character = self.npcs[gun_id]['name']
                chapters[gun_id] = Chapter(name=character, description='', stories=[])
            chapters[gun_id].stories.append(Story(
                name=name, description=description + '\n' + note, files=[path],
            ))
        return [v for _, v in sorted(chapters.items())]

    def _categorize_main_stories(self):
        chapters, id_mapping, mapped_files = get_recorded_chapters()

        # 已经进入剧情回放的章节的信息录入
        for chapter in self.chapters:
            if chapter.id in chapters:
                continue
            chapters[chapter.id] = Chapter(
                name=('' if chapter.tag == '' else f'{chapter.tag} {chapter.chapter} ') + chapter.name,
                description=chapter.chapter,
                stories=[],
            )
            for campaign_id in chapter.story_campaign_id.split(','):
                id_mapping[campaign_id] = chapter.id

        add_extra_chapter_mappings(id_mapping)

        # 已经进入剧情回放的剧情录入对应章节
        blocked = get_block_list()
        for story in sorted(self.main_events, key=lambda e: (abs(e.campaign), e.id)):
            files = [f for f in self._parse_event_stories(story, mapped_files)
                     if not is_manual_processed(f) and f not in blocked]
            if len(files) == 0:
                continue
            info = Story(
                name=files[0] if story.title == '' else story.title,
                description=story.description,
                files=typing.cast(list[str | tuple[str, str]], files),
            )
            manual_naming(info, story.campaign)
            campaign = str(story.campaign)
            # 没有的自动套一个名字
            if campaign not in id_mapping:
                chapter_id, chapter = self._unknown_chapter(story.campaign, info.name)
                chapters[chapter_id], id_mapping[campaign] = chapter, chapter_id
            chapters[id_mapping[campaign]].stories.append(info)

        post_insert(chapters, mapped_files)
        manually_process(chapters, id_mapping, mapped_files)

        others = set(self.stories.extracted.keys()) - mapped_files

        # 其它的看起来命名比较规律的东西
        for file in sorted(others):
            if file in blocked:
                continue
            if 'battleavg/' in file:
                match = _chapter_file_name_regex.match(file.split('/')[-1])
            elif '/' in file:
                continue
            else:
                match = _chapter_file_name_regex.match(file)
            if match is None:
                continue
            campaign = match.group(1)
            if campaign not in id_mapping:
                chapter_id, chapter = self._unknown_chapter(int(campaign), campaign)
                chapters[chapter_id], id_mapping[campaign] = chapter, chapter_id
            else:
                _warning('unknown story: %s', file)
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
        for story in self.upgrading_events:
            gun_id = int(story.gun_id) % 20000
            if gun_id not in chapters:
                chapters[gun_id] = Chapter(
                    name=self.guns[gun_id]['name'],
                    description='',
                    stories=[],
                )
            chapters[gun_id].stories.append(Story(
                name=f'阶段 {story.stage_id}',
                description=self.guns[gun_id]['name'] + ' 心智升级',
                files=[f'memoir/{story.scripts}.txt'],
            ))
        return [v for _, v in sorted(chapters.items(), key=lambda e: e[0])]

    def _categorize_help_letters(self):
        chapters = self._categorize_anniversary('letters')
        for chapter in chapters:
            for story in chapter.stories:
                files = story.files
                files_with_info = []
                for file in files:
                    if isinstance(file, str) and 'default_' in file:
                        file = (file, '默认')
                    files_with_info.append(file)
                story.files = files_with_info
        return chapters

    def categorize_stories(self):
        all_chapters: dict[str, list[Chapter]] = {}
        stories = self._categorize_main_stories()
        main: list[Chapter] = []
        events: list[Chapter] = []
        colab: list[Chapter] = []
        for s in stories:
            if s.description.isdigit() and 2000 < int(s.description) < 2100:
                events.append(s)
            elif '联动内容' in s.description:
                colab.append(s)
            else:
                main.append(s)
        events.sort(key=lambda e: int(e.description))
        events.extend(filter(lambda e: e.name.startswith('未知: '), main))
        main = list(filter(lambda e: not e.name.startswith('未知: '), main))
        fill_in_chapter_info(main, events)
        all_chapters['main'] = main
        all_chapters['event'] = events
        all_chapters['colab'] = colab
        all_chapters['bonding'] = self._categorize_bonding_stories()
        all_chapters['upgrading'] = self._categorize_upgrading_stories()
        all_chapters['anniversary'] = self._categorize_anniversary()
        all_chapters['anniversary4'] = self._categorize_anniversary('anniversary4')
        all_chapters['anniversary5'] = self._categorize_anniversary('anniversary5')
        all_chapters['anniversary6'] = self._categorize_anniversary('anniversary6')
        all_chapters['help'] = self._categorize_help_letters()
        all_chapters['skin'] = self._categorize_skins()
        return all_chapters

    def save(self):
        all_chapters: dict[str, list[dict]] = {}
        all_file_list: list[str] = []
        for chapters in self.all_chapters.values():
            for chapter in chapters:
                for story in chapter.stories:
                    story.files = list(filter(lambda f: (f if isinstance(f, str) else f[0]) in self.stories.extracted, story.files))
                    all_file_list.extend((f if isinstance(f, str) else f[0]) for f in story.files)
        all_files = set(all_file_list)
        others = set(self.stories.extracted.keys()) - all_files - get_block_list()
        self.all_chapters['event'].append(Chapter(
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
