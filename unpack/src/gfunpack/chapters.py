import dataclasses
import json
import logging
import typing
import urllib.request

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

_info_download_url = 'https://cdn.jsdelivr.net/gh/gf-data-tools/gf-data-ch@main/formatted/'


T = typing.TypeVar('T')

@dataclasses.dataclass
class ChapterInfo:
    id: int = 0
    name: str = ''
    type: int = 0
    story_campaign_id: str = '0'
    chapter: str = '0'


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

    @classmethod
    def _fetch(cls, file: str, item_type: typing.Type[T]) -> list[T]:
        with urllib.request.urlopen(_info_download_url + file) as f:
            data = hjson.loads(f.read().decode('utf-8'))
            assert isinstance(data, list)
            return [item_type(**item) for item in data]

    def _categorize_main_stories(self):
        chapters: dict[int, Chapter] = {}
        id_mapping: dict[str, int] = {}
        for chapter in self.chapters:
            chapters[chapter.id] = Chapter(
                name=chapter.name,
                stories=[],
            )
            id_mapping[chapter.story_campaign_id] = chapter.id
        for story in sorted(self.main_events, key=lambda e: e.id):
            campaign = str(story.campaign)
            if campaign not in id_mapping:
                auto_id = 10000
                if int(campaign) > 0:
                    auto_id += int(campaign)
                else:
                    auto_id += 10000 + (-int(campaign))
                id_mapping[campaign] = auto_id
                chapters[auto_id] = Chapter(
                    name=f'未知: {story.title}',
                    stories=[],
                )
            if story.scripts.strip() == '':
                continue
            chapters[id_mapping[campaign]].stories.append(Story(
                name=story.title,
                description=story.description,
                files=[f'{s.strip().lower()}.txt' for s in story.scripts.split(',')],
            ))
        return [v for _, v in sorted(chapters.items(), key=lambda e: e[0])]

    def _categorize_bonding_stories(self):
        chapters: dict[int, Chapter] = {}
        for chapter in self.bonding_chapters:
            chapters[chapter.id] = Chapter(
                name=chapter.name,
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
        for chapters in self.all_chapters.values():
            for chapter in chapters:
                for story in chapter.stories:
                    story.files = [f for f in story.files if f in self.stories.extracted]
        for k, chapters in self.all_chapters.items():
            chapter_dicts = [dataclasses.asdict(c) for c in chapters]
            all_chapters[k] = chapter_dicts
        with self.stories.destination.joinpath('chapters.json').open('w') as f:
            f.write(json.dumps(all_chapters, ensure_ascii=False))