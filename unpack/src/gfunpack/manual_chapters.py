import dataclasses
import pathlib
import shutil
import subprocess


@dataclasses.dataclass
class Story:
    name: str
    description: str
    files: list[str | tuple[str, str]]


@dataclasses.dataclass
class Chapter:
    name: str
    description: str
    stories: list[Story]


def _chapter_starting():
    return Chapter(
        name='开局剧情',
        description='首次进入游戏自动播放',
        stories=[
            Story(name=f'第 {i + 1} 节', description='',
                  files=[f'startavg/start{i}.txt'])
            for i in range(11 + 1)
        ],
    )


def _extra_stories_va11():
    return [
        (
            '迪吉里杜管吹奏指南',
            '',
            [
                ('-32-1-1.txt', '阶段 1'),
                ('battleavg/-32-specialbattletips-fly.txt', '小游戏提示 1'),
                ('battleavg/-32-specialbattletips-spdup.txt', '小游戏提示 2'),
                ('-32-1-2first.txt', '阶段 2'),
                ('va11/va11_1.txt', '调酒'),
            ],
        ),
        (
            '青春期',
            '',
            [
                ('-32-2-1.txt', '阶段 1'),
                ('-32-ext-2-1-point94524.txt', '点位事件'),
                ('-32-10-4-point12875.txt', '点位事件'),
                ('-32-2-2first.txt', '阶段 2'),
                ('va11/va11_2.txt', '调酒'),
            ],
        ),
        (
            '先驱者',
            '',
            [
                ('-32-3-1.txt', '阶段 1'),
                ('-32-3-2first.txt', '阶段 2'),
                ('va11/va11_3.txt', '调酒'),
            ],
        ),
        (
            '音爆',
            '',
            [
                ('-32-4-1.txt', '阶段 1'),
                ('-32-ext-4-1.txt', '点位事件'),
                ('-32-12-4-point12932.txt', '点位事件'),
                ('-32-4-2first.txt', '阶段 2'),
                ('va11/va11_4.txt', '调酒'),
            ],
        ),
        (
            '鸡胸肉',
            '',
            [
                ('-32-5-1.txt', '阶段 1'),
                ('-32-13-4-point12945.txt', '点位事件'),
                ('-32-5-2first.txt', '阶段 2'),
                ('va11/va11_5.txt', '调酒'),
            ],
        ),
        (
            '公众演讲恐惧症',
            '',
            [
                ('-32-6-1.txt', '阶段 1'),
                ('-32-ext-6-1.txt', '点位事件'),
                ('-32-6-2first.txt', '阶段 2'),
                ('va11/va11_6.txt', '调酒'),
            ],
        ),
        (
            '真心话大冒险',
            '',
            [
                ('-32-7-1.txt', '阶段 1'),
                ('-32-15-4-point13027.txt', '点位事件'),
                ('-32-7-2first.txt', '阶段 2'),
                ('va11/va11_7.txt', '调酒'),
            ],
        ),
        (
            '世上的最后一场雨',
            '',
            [
                ('-32-8-1.txt', '阶段 1'),
                ('-32-16-4-point13052.txt', '点位事件'),
                ('-32-8-4-point12833.txt', '点位事件'),
                ('-32-8-2first.txt', '阶段 2'),
                ('-32-8-2end.txt', '阶段 3'),
                ('va11/va11_8.txt', '调酒'),
            ],
        ),
    ]


def _extra_stories_cocoon():
    return [
        ('凉夜廻', '', ['-42-1-1first.txt']),
        ('雨夜谈', '', ['-42-1-2.txt']),
        ('倒影', '', ['-42-2-1first.txt']),
        ('追忆', '', ['-42-2-2.txt']),
        ('无名之人', '', [
            ('-42-3-1first.txt', '剧情'),
            ('-42-3-2.txt', '记忆碎片 1'),
            ('-42-3-3.txt', '记忆碎片 2'),
            ('-42-3-4.txt', '记忆碎片 3'),
            ('-42-3-5.txt', '记忆碎片 4'),
            ('-42-3-6.txt', '记忆碎片 5'),
            ('-42-3-7.txt', '记忆碎片 6'),
        ]),
        ('无痕之泪', '', ['-42-3-8.txt']),
        ('蝶影消散', '', ['-42-4-1first.txt']),
        ('破茧时分', '', ['-42-4-2.txt']),
    ]


_extra_chapters: list[tuple[str, str, str, list]] = [
    ('-42', '茧中蝶影', '2020', _extra_stories_cocoon()),
    ('-50', '焙炒爱意', '2022', []),
    ('-52', '里坎禁猎区', '2022', []),
    ('-59', '迷笼猜想', '2023', []),
    ('-61', '思域迷航', '2023', []),
    ('-62', '许可！二次加载', '2023', []),

    ('-8', '猎兔行动', '《苍翼默示录》x《罪恶装备》联动内容', []),
    ('-14,-15', '独法师', '《崩坏学园2》联动内容', []),
    ('-19,-20,-22', '荣耀日', '《DJMAX RESPECT》联动内容', []),
    ('-32', '瓦尔哈拉', '《VA-11 HALL-A》联动内容', _extra_stories_va11()),
    ('-38', '梦间剧', '《神枪少女》联动内容', []),
    ('-43', '暗金潮', '《全境封锁》联动内容', []),
    ('-46', '小邪神前线', '《邪神与厨二病少女》联动内容', []),
    ('-57', '雪浪映花颜', '《佐贺偶像是传奇 卷土重来》联动内容', []),
]


def _get_extra_chapters():
    return dict(
        (
            (i + 5000),
            Chapter(name, description,
                    [Story(s[0], s[1], s[2]) for s in stories]),
        )
        for i, (_, name, description, stories) in enumerate(_extra_chapters)
    )


def _get_extra_chapter_mapping():
    mapping: dict[str, int] = {}
    for i, chapter in enumerate(_extra_chapters):
        for j in chapter[0].split(','):
            mapping[j] = i + 5000
    return mapping


def get_recorded_chapters():
    chapters: dict[int, Chapter] = {
        0: _chapter_starting(),
    }
    id_mapping: dict[str, int] = {'0': 0}

    chapters.update(_get_extra_chapters())
    id_mapping.update(_get_extra_chapter_mapping())

    recorded_files: set[str] = set()
    for chapter in chapters.values():
        for story in chapter.stories:
            recorded_files.update((f if isinstance(f, str) else f[0])
                                  for f in story.files)
    return chapters, id_mapping, recorded_files


_attached_stories = [
    ('0-2-1.txt', '0-2-3round2.txt'),
    ('-2-1-1.txt', '-2-1-4-point2207.txt'),

    # 盲拆法则
    ('-7-1-3round1.txt', '-7-1-3round2.txt'),
    ('-7-1-3round2.txt', '-7-1-4-point3498.txt'),

    ('-7-2-3round1.txt', '-7-2-3round2.txt'),
    ('-7-2-3round2.txt', '-7-2-4-point3342.txt'),

    ('-7-3-3round1.txt', '-7-3-3round2.txt'),
    ('-7-3-3round2.txt', '-7-3-4-point3533.txt'),

    ('-7-4-3round1.txt', '-7-4-3round2.txt'),
    ('-7-4-3round2.txt', '-7-4-4-point3612.txt'),

    # 有序紊流
    ('-24-2-1.txt', '-24-2-2.txt'),
    ('-24-3-2first.txt', '-24-3-2.txt'),
    ('-24-4-2first.txt', '-24-4-2.txt'),
    ('-24-6-1.txt', '-24-6-2.txt'),
    ('-24-7-2first.txt', '-24-7-2.txt'),
    ('-24-8-2first.txt', '-24-8-2.txt'),
    ('-24-9-2first.txt', '-24-9-2.txt'),
    ('-24-10-2first.txt', '-24-10-2.txt'),
    ('-24-11-2first.txt', '-24-11-2.txt'),
    ('-24-12-2first.txt', '-24-12-2.txt'),
    ('-24-13-2first.txt', '-24-13-2.txt'),
    ('-24-14-2first.txt', '-24-14-2.txt'),
    ('-24-15-1.txt', '-24-15-2first.txt'),
    ('-24-15-2first.txt', '-24-15-2.txt'),
]


_extra_chapter_mapping = {
    '-27': '-24',  # 有序紊流：飓风营救
    '-45': '-24',  # 飓风营救复刻
    '-99': '-58',  # 慢休克 END
}


def add_extra_chapter_mappings(id_mapping: dict[str, int]):
    for extra, mapping in _extra_chapter_mapping.items():
        id_mapping[extra] = id_mapping[mapping]


def post_insert(chapters: dict[int, Chapter], mapped_files: set[str]):
    stories: dict[str, Story] = {}
    for chapter in chapters.values():
        for story in chapter.stories:
            for file in story.files:
                stories[file if isinstance(file, str) else file[0]] = story
    for file, attached in _attached_stories:
        assert attached not in mapped_files, attached
        story = stories[file]
        assert isinstance(story.files[0], str)
        stories[attached] = story
        story.files.append(attached)
        mapped_files.add(attached)


def get_block_list():
    return set(
        [
            '0-0-0.txt',  # 空白，“替代剧情”
            '0-0-1.txt',  # 空白，“替代教程”
            'profiles.txt',
            'avgplaybackprofiles.txt',

            # 魔方行动，例如 -6-1-1 和 -1-1-1 的内容是一模一样的……
            '-6-1-1.txt',
            '-6-1-2first.txt',
            '-6-2-1.txt',
            '-6-2-2end.txt',
            '-6-2-2first.txt',
            '-6-3-1.txt',
            '-6-3-2end.txt',
            '-6-3-2first.txt',
            '-6-4-1.txt',
            '-6-4-2end.txt',
            '-6-4-2first.txt',
        ]
    )


def get_extra_anniversary_stories(destination: pathlib.Path):
    directory = pathlib.Path('GFLData', 'ch', 'text', 'avgtxt', 'anniversary')
    old_directory = pathlib.Path('GirlsFrontlineData', 'zh-CN', 'asset_textes', 'avgtxt', 'anniversary')
    if not pathlib.Path('GFLData').is_dir():
        subprocess.run([
            'git', 'clone', 'https://github.com/randomqwerty/GFLData.git',
        ], stdout=subprocess.DEVNULL).check_returncode()
    if not pathlib.Path('GirlsFrontlineData').is_dir():
        subprocess.run([
            'git', 'clone', 'https://github.com/Dimbreath/GirlsFrontlineData.git',
        ], stdout=subprocess.DEVNULL).check_returncode()
    if not destination.joinpath('anniversary4').is_dir():
        subprocess.run([
            'git', 'checkout', '41793e107cb4697de10ac5bf507f1909f1c47030',
        ], cwd='GirlsFrontlineData').check_returncode()
        shutil.copytree(old_directory, destination.joinpath('anniversary4'))
    if not destination.joinpath('anniversary5').is_dir():
        subprocess.run([
            'git', 'checkout', '9d0dae0066ccf1bc9e32abf35401d5ef7eaf7746',
        ], cwd='GFLData').check_returncode()
        shutil.copytree(directory, destination.joinpath('anniversary5'))
    if not destination.joinpath('anniversary6').is_dir():
        subprocess.run([
            'git', 'checkout', '93e4c8dd9a236f57b6869cf5c88c93c1cc79255c',
        ], cwd='GFLData').check_returncode()
        shutil.copytree(directory, destination.joinpath('anniversary6'))
