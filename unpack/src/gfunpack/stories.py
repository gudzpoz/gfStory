import json
import logging
import os
import pathlib
import re
import typing

import UnityPy
from UnityPy.classes import TextAsset

from gfunpack import mapper, utils

_logger = logging.getLogger('gfunpack.prefabs')
_warning = _logger.warning

_text_asset_regex = re.compile('^assets/resources/dabao/avgtxt/(.+.txt)$')

_speaker_regex = re.compile('<speaker>(.*)</speaker>', re.IGNORECASE)
_sprite_regex = re.compile('^([^()<>]*)\\((\\d*)\\)')
_effect_tag_regex = re.compile('</?([^<>]+)>')
_line_replace_templates = [
    (
        re.compile('<color=(#\\w+)>', re.IGNORECASE),
        lambda match: f'<span style="color: {match.group(1)}">',
    ),
    (
        re.compile('<size=(\\d+)>', re.IGNORECASE),
        lambda match: f'<span style="font-size: {int(match.group(1)) / 50}em">',
    ),
    (
        re.compile('<c>', re.IGNORECASE),
        '</p><p>选项：',
    ),
    (
        re.compile('</size>|</color>', re.IGNORECASE),
        '</span>',
    )
]

class StoryTranspiler:
    audio: dict[str, str]
    backgrounds: dict[str, str]
    characters: dict[str, dict[str, mapper.SpriteDetails]]
    tag_collection: set[str]

    def __init__(self, audio_json: pathlib.Path, background_json: pathlib.Path,
                 character_json: pathlib.Path) -> None:
        self.audio = json.load(audio_json.open())
        self.backgrounds = json.load(background_json.open())
        self.characters = json.load(character_json.open())
        self.tag_collection = set()
        for character in self.characters.values():
            for k, sprite in character.items():
                character[k] = mapper.SpriteDetails(**sprite)

    @classmethod
    def _convert_content_line(cls, line: str):
        for pattern, replacement in _line_replace_templates:
            line = re.sub(pattern, replacement, line)
        return line

    @classmethod
    def _convert_content(cls, content: str, tags: str | None = None):
        tags = '' if tags is None else f'{tags} '
        return [
            f'{tags}<p>{cls._convert_content_line(line)}</p>'
            for line in content.split('+')
        ]

    def _parse_narrators(self, narrators: str):
        sprites: list[tuple[str, int, dict[str, str]]] = []
        speakers = []
        for narrator in narrators.split(';'):
            match = re.search(_speaker_regex, narrator)
            if match is not None:
                speakers.append(match.group(1))
                narrator = re.sub(_speaker_regex, '', narrator)
            sprite = _sprite_regex.match(narrator)
            if sprite is None:
                _warning('unrecognized sprite `%s` in `%s`', narrator, narrators)
                continue
            if sprite.group(1) == '' or sprite.group(2) == '':
                sprites.append(('', 0, {}))
            else:
                attrs = self._parse_effects(narrator)
                sprites.append((sprite.group(1), int(sprite.group(2)), attrs))
        return sprites, ' & '.join(speakers)
    
    def _parse_effects(self, effects: str):
        tags = re.findall(_effect_tag_regex, effects)
        parsed: dict[str, str] = dict((tag, '') for tag in tags)
        for tag in parsed.keys():
            if f'</{tag}>' in effects:
                try:
                    full_tag = f'<{tag}>'
                    start = effects.index(full_tag)
                    end = effects.index(f'</{tag}>')
                    parsed[tag] = effects[start + len(full_tag) : end]
                except ValueError:
                    _warning('tag %s wrong in `%s`', tag, effects)
        result = dict((k.lower(), v) for k, v in parsed.items())
        self.tag_collection.update(result.keys())
        return result
    
    def _get_sprite_info(self, character: str, sprite: int):
        c = self.characters.get(character)
        if c is not None:
            s = c.get(str(sprite))
            if s is not None:
                return {
                    'name': sprite,
                    'url': f'/images/{s.path}',
                    'scale': -1,
                    'center': (-1, -1),
                }
        return {
            'name': sprite,
            'url': '',
            'scale': -1,
            'center': (-1, -1),
        }
    
    def _inject_lua_scripts(self, characters: dict[str, dict[int, str]]):
        character_list = []
        for name, sprites in characters.items():
            character_list.append({
                'name': name,
                'sprites': [
                    self._get_sprite_info(name, sprite_name)
                    for sprite_name in sprites.keys()
                ],
            })
        serialized = json.dumps(json.dumps(character_list, ensure_ascii=False), ensure_ascii=False)
        return f'```lua global\nprint.defineCharacters({serialized})\n```\n\n';
    
    def _generate_bg_line(self, bg: str, effects: dict[str, str], filename: str):
        if bg == '':
            _warning('invalid bg in %s', filename)
        bg_path = self.backgrounds.get(bg)
        if bg_path is None or bg_path == '':
            _warning('background not found for `%s` in %s', bg, filename)
            bg_path = f'background/{bg}.png'
        night = 'night' if 'night' in effects else '!night'
        return f':background[] :classes[{night}] /images/{bg_path}'

    def decode(self, script: str, filename: str):
        if filename in ['avgplaybackprofiles.txt', 'profiles.txt']:
            return script
        markdown: list[str] = []
        characters: dict[str, dict[int, str]] = {}
        remote_narrators: set[str] = set()
        for line in script.split('\n'):
            line = line.strip()
            if line == '':
                continue
            line = line.replace('：', ': ') # 中文冒号……
            if ':' not in line:
                _warning('unrecognized line `%s` in %s', line, filename)
                continue
            metadata, content = line.split(':', 1)
            if '||' not in metadata:
                _warning('unrecognized line metadata `%s` in %s', line, filename)
                continue
            narrator_string, effect_string = metadata.split('||', 1)
            sprites, speaker = self._parse_narrators(narrator_string)
            effects = self._parse_effects(effect_string)
            if 'bin' in effects:
                markdown.append(self._generate_bg_line(effects['bin'], effects, filename))
            if 'bgm' in effects:
                bgm = self.audio.get(effects['bgm'], f'bgm/{effects["bgm"]}.m4a')
                markdown.append(f':audio[] /audio/{bgm}')
            if 'se' in effects or 'se1' in effects or 'se2' in effects or 'se3' in effects:
                se =  effects.get('se') or effects.get('se1') or effects.get('se2') or effects.get('se3') or ''
                se = self.audio.get(se, f'se/{se}.m4a')
                markdown.append(f':se[] /audio/{se}')
            if 'cg' in effects:
                for i, cg in enumerate(effects['cg'].split(','), 1):
                    if cg.strip() == '':
                        continue
                    markdown.append(self._generate_bg_line(cg.strip(), effects, filename))
                    markdown.append('……' * i)
            if '黑屏1' in effects or '黑屏2' in effects:
                pass
            options = content.split('<c>')
            content, options = options[0], options[1:]
            sprite_string = '|'.join(f'{character}/{sprite}' for character, sprite, _ in sprites)
            remote_narrators = set(character for character, _, attrs in sprites if '通讯框' in attrs or character in remote_narrators)
            remote_string = '|'.join(f'{character}/{sprite}' for character, sprite, _ in sprites if character in remote_narrators)
            if '分支' in effects:
                branching = f'`branch == {effects["分支"]}` '
            else:
                branching = ''
            for character, sprite, _ in sprites:
                if character not in characters:
                    characters[character] = {}
                characters[character][sprite] = ''

            tags = f'{branching} :sprites[{sprite_string}] :remote[{remote_string}] :narrator[{speaker}] :color[#fff]'
            markdown.extend(self._convert_content(content, tags))
            if len(options) != 0:
                for i, option in enumerate(options, 1):
                    markdown.append(f'- {self._convert_content(option)}\n\n  `branch = {i}`')
        return self._inject_lua_scripts(characters) + '\n\n'.join(markdown)


class Stories:
    directory: pathlib.Path

    gf_data_directory: pathlib.Path

    destination: pathlib.Path

    resource_file: pathlib.Path

    transpiler: StoryTranspiler

    extracted: dict[str, pathlib.Path]

    def __init__(self, directory: str, destination: str, *, gf_data_directory: str | None = None, root_destination: str | None = None) -> None:
        self.directory = utils.check_directory(directory)
        self.destination = utils.check_directory(destination, create=True)
        self.resource_file = list(self.directory.glob('*assettextavg.ab'))[0]
        root = self.destination.parent if root_destination is None else pathlib.Path(root_destination)
        self.transpiler = StoryTranspiler(
            root.joinpath('audio', 'audio.json'),
            root.joinpath('images', 'backgrounds.json'),
            root.joinpath('images', 'characters.json'),
        )
        self.gf_data_directory = root.joinpath('gf-data-ch') if gf_data_directory is None else pathlib.Path(gf_data_directory)
        self.extracted = self.extract_all()
        self.copy_missing_pieces()

    def extract_all(self):
        assets = UnityPy.load(str(self.resource_file))
        extracted: dict[str, pathlib.Path] = {}
        for o in assets.objects:
            if o.container is None or o.type.name != 'TextAsset':
                continue
            match = _text_asset_regex.match(o.container)
            if match is None:
                continue
            name = match.group(1)
            text = typing.cast(
                TextAsset,
                o.read(),
            )
            content: str = text.m_Script.tobytes().decode()
            path = self.destination.joinpath(*name.split('/'))
            os.makedirs(path.parent, exist_ok=True)
            with path.open('w') as f:
                f.write(self.transpiler.decode(content, name))
            extracted[name] = path
        return extracted

    def copy_missing_pieces(self):
        directory = utils.check_directory(self.gf_data_directory.joinpath('asset', 'avgtxt'))
        for file in directory.glob('**/*.txt'):
            rel = file.relative_to(directory)
            name = str(rel)
            if name not in self.extracted:
                _warning('filling in %s', name)
                path = self.destination.joinpath(rel)
                with path.open('w') as f:
                    with file.open() as content:
                        f.write(self.transpiler.decode(content.read(), name))
                self.extracted[name] = path

    def save(self):
        path = self.destination.joinpath('stories.json')
        with path.open('w') as f:
            f.write(json.dumps(
                dict((k, str(p.relative_to(self.destination))) for k, p in self.extracted.items()),
                ensure_ascii=False,
            ))
            