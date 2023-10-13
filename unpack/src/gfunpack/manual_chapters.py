import dataclasses


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


_chapter_starting = lambda: Chapter(
    name='开局剧情',
    description='首次进入游戏自动播放',
    stories=[
        Story(name=f'第 {i + 1} 节', description='', files=[f'startavg/start{i}.txt'])
        for i in range(11 + 1)
    ],
)


_extra_stories_va11 = lambda: [
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


_extra_stories_cocoon = lambda: [
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
    ('无痕之泪', '',['-42-3-8.txt']),
    ('蝶影消散', '', ['-42-4-1first.txt']),
    ('破茧时分', '', ['-42-4-2.txt']),
]


_extra_chapters: list[tuple[str, str, str, list]] = [
    ('-42', '茧中蝶影', '2020', _extra_stories_cocoon()),

    ('-8', '猎兔行动', '《苍翼默示录》x《罪恶装备》联动内容', []),
    ('-14,-15', '独法师', '《崩坏学园2》联动内容', []),
    ('-19,-20,-22', '荣耀日', '《DJMAX RESPECT》联动内容', []),
    ('-32', '瓦尔哈拉', '《VA-11 HALL-A》联动内容', _extra_stories_va11()),
    ('-38', '梦间剧', '《神枪少女》联动内容', []),
    ('-43', '暗金潮', '《全境封锁》联动内容', []),
    ('-46', '小邪神前线', '《邪神与厨二病少女》联动内容', []),
    ('-57', '雪浪映花颜', '《佐贺偶像是传奇 卷土重来》联动内容', []),
]


_get_extra_chapters = lambda: dict(
    ((i + 5000), Chapter(name, description, [Story(s[0], s[1], s[2]) for s in stories]))
    for i, (_, name, description, stories) in enumerate(_extra_chapters)
)


def _get_extra_chapter_mapping():
    mapping: dict[str, int] = {}
    for i, chapter in enumerate(_extra_chapters):
        for j in chapter[0].split(','):
            mapping[j] = i + 5000
    return mapping


def get_block_list():
    return set(
        [
            '0-0-0.txt',  # 空白，“替代剧情”
            '0-0-1.txt',  # 空白，“替代教程”
            'profiles.txt',
            'avgplaybackprofiles.txt',
        ]
    )


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
            recorded_files.update((f if isinstance(f, str) else f[0]) for f in story.files)
    return chapters, id_mapping, recorded_files
