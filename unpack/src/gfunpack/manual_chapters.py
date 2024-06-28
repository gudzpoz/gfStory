import dataclasses
import pathlib
import shutil
import subprocess
import typing
from urllib import request


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


def _extra_stories_sac2045():
    return [
        ('陌生人的礼物', '', ['-64-1-0.txt']),
        ('栗子树下', '', ['-64-2-0.txt']),
        ('早安，新世界', '', ['-64-3-0.txt']),
        ('土豆传说', '', ['-64-3-1.txt']),
        ('网瘾戒断', '', ['-64-3-2.txt']),
        ('伯爵金特调', '', ['-64-3-3.txt']),
        ('葡萄果汁', '', ['-64-3-4.txt']),
        ('樱花和你', '', ['-64-4-0.txt']),
        ('少校的委托', '', ['-64-5-1.txt']),
        ('自由的囚徒', '', ['-64-5-2.txt']),
        ('重回开端', '', ['-64-6-0.txt']),
        ('升格失败', '', ['-64-6-1.txt']),
        ('祝你幸福', '', ['-64-7-1.txt']),
        ('藏在合照背后', '', ['-64-7-2.txt']),
        ('怒火', '', ['-64-8-1.txt']),
        ('频道里的幽灵', '', ['-64-8-2.txt']),
        ('流眼泪的布丁', '', ['-64-9-1.txt']),
        ('只属于我的战争', '', ['-64-9-2.txt']),
        ('世界尽头的落日', '', ['-64-10-0.txt']),
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
    ('-64', '镜扉的永恒', '《攻壳机动队：SAC_2045》联动内容', _extra_stories_sac2045()),
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

_attached_stories_motor_race = [
    '-31-3c3-1.txt',
    'battleavg/-31-specialbattletips-1.txt',
    'battleavg/-31-specialbattletips-3.txt',
    'battleavg/-31-specialbattletips-4.txt',
    'battleavg/-31-specialbattletips-5.txt',
    'battleavg/-31-specialbattletips-6.txt',
    'battleavg/-31-specialbattletips-fly.txt',
    'battleavg/-31-specialbattletips-spdup.txt',
    'battleavg/-31-specialbattletips-lose.txt',
    'battleavg/-31-specialbattletips-victory.txt',
]
_attached_stories: list[tuple[str, str, str]] = [
    ('0-2-1.txt', '0-2-3round2.txt'),
    ('-2-1-1.txt', '-2-1-4-point2207.txt'),

    # 焙炒爱意，白色庆典位点剧情
    ('-50-1-4.txt', '-50-3-1.txt', '送错巧克力'),
    ('-50-3-1.txt', '-50-3-2.txt', '刘易斯'),
    ('-50-3-2.txt', '-50-3-3.txt', '隼'),
    ('-50-3-3.txt', '-50-3-4.txt', '79式'),
    ('-50-3-4.txt', '-50-3-5.txt', '97式'),
    ('-50-3-5.txt', '-50-3-6.txt', '猎手'),
    ('-50-3-6.txt', '-50-3-7.txt', 'LWMMG'),
    ('-50-3-7.txt', '-50-3-8.txt', 'K5'),
    ('-50-3-8.txt', '-50-3-9.txt', '加兰德'),
    ('-50-3-9.txt', '-50-3-10.txt', 'P22'),
    ('-50-3-10.txt', '-50-3-11.txt', 'T77'),
    ('-50-3-11.txt', '-50-3-12.txt', '帕斯卡'),
    # 焙炒爱意，小怪
    ('-50-1-4.txt', '-50-ext-1-4-1.txt', '甜点魔蚁'),
    ('-50-ext-1-4-1.txt', '-50-ext-1-4-2.txt', '末日点心犬'),
    ('-50-ext-1-4-2.txt', '-50-ext-1-4-3.txt', '卡路里炸弹（巧克力）'),
    ('-50-ext-1-4-3.txt', '-50-ext-1-4-4.txt', '卡路里炸弹（巧苏鲁）'),
    ('-50-ext-1-4-4.txt', '-50-ext-1-4-5.txt', '可可新世界'),
    ('-50-ext-1-4-5.txt', '-50-ext-1-4-6.txt', '巧苏鲁'),
    # 焙炒爱意，巧克力制作
    ('-50-1-3.txt', '-50-ext-1-3-2.txt', '配方表'),
    ('-50-ext-1-3-2.txt', '-50-ext-1-3.txt', '配方表？'),
    ('-50-ext-1-3.txt', '-50-ext-0-1.txt', '薄荷世家'),
    ('-50-ext-0-1.txt', '-50-ext-0-2.txt', '甜蜜军刀'),
    ('-50-ext-0-2.txt', '-50-ext-0-3.txt', '命运之吻'),
    ('-50-ext-0-3.txt', '-50-ext-0-4.txt', '巧克力二重奏'),
    ('-50-ext-0-4.txt', '-50-ext-0-5.txt', '经典记忆'),
    ('-50-ext-0-5.txt', '-50-ext-0-6.txt', '可可新世界'),
    ('-50-ext-0-6.txt', '-50-ext-0-7.txt', '巧苏鲁'),

    # 里坎禁猎区
    ('-52-1-1.txt', 'battleavg/-52-dxg.txt', '打西瓜'),

    # 盲拆法则：感觉应该是第二周目的变化？
    ('-7-1-3round1.txt', '-7-1-3round2.txt', '阶段2.5'),
    ('-7-2-3round1.txt', '-7-2-3round2.txt', '阶段2.5'),
    ('-7-3-3round1.txt', '-7-3-3round2.txt', '阶段2.5'),
    ('-7-4-3round1.txt', '-7-4-3round2.txt', '阶段2.5'),

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

    # 裂变链接
    # ('-33-59-4-point13290.txt', '-33-59-4-point80174.txt'), # 两个点位事件一样
    ('-33-59-4-point13290.txt', 'battleavg/-33-24-1first.txt'),

    # 偏振光
    ('-36-5-ex.txt', 'battleavg/-36-specialbattletips.txt'),
] + [ # 异构体飙车小游戏局内剧情
    (prev, after)
    for prev, after in zip(
        _attached_stories_motor_race[:-1],
        _attached_stories_motor_race[1:],
    )
]
_attached_events: list[tuple[str, Story]] = [
    # 裂变链接：吞噬一切的花海-战斗
    ('-33-42-1first.txt', Story(
        name="吞噬一切的花海-战斗",
        description="小游戏说明",
        files=['battleavg/-33-44-1first.txt'],
    )),
    # 愚人节
    ('1-1-1.txt', Story(
        name="演习训练-愚人节版",
        description="欢迎回来，父亲大人。",
        files=['always-404-1-1-1.txt', 'always-404-1-1-2.txt', 'always-404-1-1-3.txt'],
    )),
    # 里坎禁猎区
    ('-52-0-1.txt', Story(
        name='抉择之箱',
        description='',
        files=['-52-7-1.txt'],
    )),
    ('-52-6-1.txt', Story(
        name='夏日终章（WA2000）',
        description='',
        files=['-52-e-1.txt'],
    )),
    ('-52-e-1.txt', Story(
        name='夏日终章（春田）',
        description='',
        files=['-52-e-1-springfield.txt'],
    )),
    # 雪浪映花颜
    ('-57-0-1.txt', Story(
        name='第一天·上午',
        description='',
        files=[
            ('-57-a1-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-c1-1.txt', '练歌房 多-唻-咪'),
            ('-57-w1-1.txt', '浴场 咕嘟咕嘟'),
            ('-57-x1-1.txt', '快餐店 兹-哗-唰'),
            ('-57-d1-1.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-1-1.txt', Story(
        name='第一天·夜晚',
        description='',
        files=[
            ('-57-w1-2.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-x1-2.txt', '练歌房 多-唻-咪'),
            ('-57-a1-2.txt', '浴场 咕嘟咕嘟'),
            ('-57-d1-2.txt', '快餐店 兹-哗-唰'),
            ('-57-l1-2.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-1-2.txt', Story(
        name='第二天·上午',
        description='',
        files=[
            ('-57-x2-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-y2-1.txt', '练歌房 多-唻-咪'),
            ('-57-c2-1.txt', '浴场 咕嘟咕嘟'),
            ('-57-l2-1.txt', '快餐店 兹-哗-唰'),
            ('-57-d2-1.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-2-1.txt', Story(
        name='第二天·夜晚',
        description='',
        files=[
            ('-57-l2-2.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-c2-2.txt', '练歌房 多-唻-咪'),
            ('-57-w2-2.txt', '浴场 咕嘟咕嘟'),
            ('-57-x2-2.txt', '快餐店 兹-哗-唰'),
            ('-57-y2-2.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-2-2.txt', Story(
        name='第三天·上午',
        description='',
        files=[
            ('-57-l3-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-y3-1.txt', '练歌房 多-唻-咪'),
            ('-57-w3-1.txt', '浴场 咕嘟咕嘟'),
            ('-57-x3-1.txt', '快餐店 兹-哗-唰'),
            ('-57-d3-1.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-3-1.txt', Story(
        name='第三天·夜晚',
        description='',
        files=[
            ('-57-3-point1.txt', '练歌房 多-唻-咪'),
            ('-57-3-point2.txt', '快餐店 兹-哗-唰'),
        ],
    )),
    ('-57-3-2.txt', Story(
        name='第四天·上午',
        description='',
        files=[
            ('-57-a4-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-c4-1.txt', '练歌房 多-唻-咪'),
            ('-57-y4-1.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-4-1.txt', Story(
        name='第四天·夜晚',
        description='',
        files=[
            ('-57-l4-2.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-y4-2.txt', '练歌房 多-唻-咪'),
            ('-57-a4-2.txt', '浴场 咕嘟咕嘟'),
            ('-57-x4-2.txt', '快餐店 兹-哗-唰'),
            ('-57-d4-2.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-4-2.txt', Story(
        name='第五天·上午',
        description='',
        files=[
            ('-57-l5-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-a5-1.txt', '练歌房 多-唻-咪'),
            ('-57-w5-1.txt', '浴场 咕嘟咕嘟'),
            ('-57-x5-1.txt', '快餐店 兹-哗-唰'),
            ('-57-d5-1.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-5-1.txt', Story(
        name='第五天·夜晚',
        description='',
        files=[
            ('-57-w5-2.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-d5-2.txt', '练歌房 多-唻-咪'),
            ('-57-x5-2.txt', '浴场 咕嘟咕嘟'),
            ('-57-l5-2.txt', '快餐店 兹-哗-唰'),
            ('-57-c5-2.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-5-2.txt', Story(
        name='第六天·上午',
        description='',
        files=[
            ('-57-a6-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-c6-1.txt', '练歌房 多-唻-咪'),
            ('-57-w6-1.txt', '浴场 咕嘟咕嘟'),
            ('-57-x6-1.txt', '快餐店 兹-哗-唰'),
            ('-57-d6-1.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-6-1.txt', Story(
        name='第六天·夜晚',
        description='',
        files=[
            ('-57-6-point1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-6-point2.txt', '便利店 欢迎光临'),
        ],
    )),
    ('-57-6-2.txt', Story(
        name='第七天·上午',
        description='',
        files=[
            ('-57-a7-1.txt', '练舞厅 抬头-挺胸-扭胯'),
            ('-57-l7-1.txt', '练歌房 多-唻-咪'),
            ('-57-d7-1.txt', '浴场 咕嘟咕嘟'),
            ('-57-w7-1.txt', '快餐店 兹-哗-唰'),
            ('-57-y7-1.txt', '便利店 欢迎光临'),
        ],
    )),
]


_extra_chapter_mapping = {
    '-27': '-24',  # 有序紊流：飓风营救
    '-45': '-24',  # 飓风营救复刻
    '-99': '-58',  # 慢休克 END
}


def add_extra_chapter_mappings(id_mapping: dict[str, int]):
    for extra, mapping in _extra_chapter_mapping.items():
        id_mapping[extra] = id_mapping[mapping]

_manual_processed = set().union(
)
def is_manual_processed(file: str):
    return file in _manual_processed
def manually_process(chapters: dict[int, Chapter], id_mapping: dict[str, int], mapped_files: set[str]):
    # 佐贺
    c = chapters[id_mapping['-57']]
    specials = {
        '源樱': ['请勿靠近！', '吉光片羽', '樱之蕊'],
        '二阶堂咲': ['暴走电台！', '暴走回忆！', '暴走的毕业礼'],
        '水野爱': ['雨间庭', '月见海', '闪耀之爱'],
        '绀野纯子': ['共在异乡为异客', '明月何年初照人', '烟波相望各西东'],
        '夕雾': ['时间旅人', '海之声', '直至太阳下山'],
        '星川莉莉': ['完美陌生人', '王牌特工', '长日留痕'],
        '山田多惠': ['奇妙夜游记', '赠礼者', '“请不要走”'],
    }
    endings = [
        '笑与泪的夜',
        '荧光色的夜',
        '乘风而起的夜',
        '灰白色的夜',
        '松动的背景板',
        '歌声不停，舞步不休',
        '肩与肩的距离',
        '加油，打工人！',
        '巅峰！狂飙！',
        '灵感！泉涌！',
    ]
    files: dict[str, str] = {}
    names = set(n for ns in specials.values() for n in ns)
    for s in c.stories:
        if s.name in names:
            assert len(s.files) == 1
            file = s.files[0]
            assert isinstance(file, str)
            files[s.name] = file
    c.stories = [s for s in c.stories if s.name not in names]
    for s in c.stories:
        if s.name in endings:
            s.description = f'结局 {endings.index(s.name) + 1}'
    for character, stories in specials.items():
        c.stories.append(Story(
            name=character,
            description='剧情',
            files=[(files[name], name) for name in stories],
        ))


def manual_naming(story: Story, campaign: int):
    if campaign == -43:  # 暗金潮命名有问题
        story.name, story.description = story.description, story.name
        if story.description == '破茧时分':  # 这个是 -42 茧中蝶影的介绍，应该是复制错了
            story.description = ''
    if campaign == -38:  # 梦间剧，有问题
        story.name = story.description
        story.description = ''


def _index_of_file(story: Story, file: str):
    for i, f in enumerate(story.files):
        if isinstance(f, str):
            if f == file:
                return i
        else:
            if f[0] == file:
                return i
    raise ValueError(f'{file} not found in {story}')


def post_insert(chapters: dict[int, Chapter], mapped_files: set[str]):
    stories: dict[str, tuple[Chapter, Story]] = {}
    for chapter in chapters.values():
        for story in chapter.stories:
            for file in story.files:
                stories[file if isinstance(file, str) else file[0]] = (chapter, story)
    for attachment in _attached_stories:
        file, attached = attachment[0:2]
        assert attached not in mapped_files, attached
        c, story = stories[file]
        assert isinstance(story.files[0], str)
        stories[attached] = (c, story)
        story.files.insert(
            _index_of_file(story, file) + 1,
            attached if len(attachment) == 2 else (attached, attachment[2]),
        )
        mapped_files.add(attached)
    for file, attached in _attached_events:
        assert all(f not in mapped_files and f[0] not in mapped_files for f in attached.files)
        c, story = stories[file]
        c.stories.insert(c.stories.index(story) + 1, attached)
        for f in attached.files:
            if not isinstance(f, str):
                f = f[0]
            stories[f] = (c, attached)
            mapped_files.add(f)


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

            # 裂变链接，两个点位事件内容是一样的
            '-33-59-4-point80174.txt',

            # 各种秃洞复刻提示
            '-39-ex1-4-point91502.txt',
            '-55-ext.txt',
            '-60-tips.txt',
            '-63-tips.txt',
            '-65-tips.txt',
            '-65-tips2.txt',
            '-404-ext-1-1.txt',
            # 飓风营救复刻 (-45 -> -24)
            "-45-ext-04.txt",
            "-45-ext-01.txt",
            "-45-ext-02.txt",
            "-45-ext-03.txt",

            # 盲拆法则：这些是英文版
            '-7-1-4-point3498.txt',
            '-7-2-4-point3342.txt',
            '-7-3-4-point3533.txt',
            '-7-4-4-point3612.txt',

            # 神枪少女联动，和 -38-ex-point91829.txt 内容一样
            '-38-ex-point91820.txt',

            # 一币之遥，游戏提示
            '-49-3-1-point94780.txt',
            '-49-ext-1-1.txt',
            '-49-ext-4-1.txt',

            # 捩浪人，游戏提示
            '-47-2-skill-1.txt',
            '-47-2-skill-2.txt',
            '-47-2-skill-3.txt',

            # 焙炒爱意，“文本待替换”
            '-50-ext-0.txt',
            '-50-ext-1-4-0.txt',

            # 里坎禁猎区，小游戏提示文本
            '-52-ext-2-1.txt',
            '-52-ext-3-1.txt',
            '-52-ext-4-1.txt',
            '-52-ext-5-1.txt',
            '-52-ext-5-2.txt',
            '-52-ext-5-3.txt',
            '-52-pachinko0.txt',
            '-52-pachinko1.txt',
            '-52-pachinko2.txt',
            '-52-pachinko3.txt',
            '-52-pachinko4.txt',
            '-52-pachinko5.txt',
            '-52-pachinko6.txt',
            '-52-pachinko7.txt',
            '-52-pachinko8.txt',
            '-52-pachinko9.txt',
            '-52-pachinkornd2.txt',

            # 许可！二次加载
            '-62-sangvis-tutorial-4kill.txt',
            '-62-sangvis-tutorial-8kill.txt',
            '-62-sangvis-tutorial-missionstart.txt',

            # 佐贺联动
            '-57-ext-5.txt',
            '-57-ext-6.txt',
            '-57-ext-7-00.txt',
            '-57-ext-7-01.txt',
            '-57-ext-7-11.txt',
            '-57-ext-7-12.txt',
            '-57-ext-7-13.txt',
            '-57-ext-7-14.txt',
            '-57-ext-7-15.txt',
            '-57-ext-7-16.txt',
            '-57-ext-7-17.txt',
            '-57-ext-7-24.txt',
            '-57-ext-7-26.txt',
            '-57-ext-7-27.txt',
            '-57-ext-7-36.txt',
            '-57-ext-7-41.txt',
            '-57-ext-7-42.txt',
            '-57-ext-7-43.txt',
            '-57-ext-7-44.txt',
            '-57-ext-7-45.txt',
            '-57-ext-7-46.txt',
            '-57-ext-7-47.txt',
            '-57-ext-7-48.txt',
            '-57-ext-7-51.txt',
            '-57-ext-7-54.txt',
            '-57-ext-7-57.txt',
            '-57-ext-7-61.txt',
            '-57-ext-7-62.txt',
            '-57-ext-7-63.txt',
            '-57-ext-7-64.txt',
            '-57-ext-7-65.txt',
            '-57-ext-7-66.txt',
            '-57-ext-7-67.txt',
            '-57-ext-7-68.txt',
            '-57-ext-7-71.txt',
            '-57-ext-7-74.txt',
            '-57-ext-7-77.txt',
            '-57-ext-7-78.txt',
            '-57-ext-7-81.txt',
            '-57-ext-7-82.txt',
            '-57-ext-7-83.txt',
            '-57-ext-7-84.txt',
            'battleavg/-57-dance.txt',
            'battleavg/-57-sing.txt',
            'battleavg/-57-work.txt',

            # SAC 2045
            '-64-ext-1.txt',
            '-64-ext-2.txt',
            '-64-ext-3.txt',
        ]
    )


def get_extra_stories(destination: pathlib.Path):
    downloadables = [
        (
            'https://gcore.jsdelivr.net/gh/gf-data-tools/gf-data-ch@42b067b833a5e10a8f9cedf198fe182f1df122f1/asset/avgtxt/-52-e-1.txt',
            '-52-e-1-springfield.txt',
        ),
    ]
    for url, file in downloadables:
        path = destination.joinpath(file)
        if not path.is_file():
            request.urlretrieve(url, path)


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
        # 四周年的残留？
        dup = destination.joinpath('anniversary6/55-102686.txt')
        if dup.is_file():
            dup.unlink()
