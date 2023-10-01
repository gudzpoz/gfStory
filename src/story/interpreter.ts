import { fengari } from '@brocatel/mdc';
import vm from '@brocatel/mdc/dist/vm-bundle.lua?raw';

import type { Character, CharacterSprite } from '../types/character';

const {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  js, lauxlib, lua, lualib, to_luastring, tojs,
} = fengari;

export interface StoryLine {
  text: string;
  tags: {
    narrator?: string,
    color?: string,

    background?: string,
    style?: string,

    audio?: string,

    sprites?: string,
    remote?: string,
  };
}

export interface SpriteImage extends CharacterSprite {
  image: HTMLImageElement;
}

export class StoryInterpreter {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  L: any;

  loaded: boolean;

  characters: Character[];

  resources: string[];

  preloadedImages: Record<string, SpriteImage>;

  constructor() {
    this.loaded = false;
    this.characters = [];
    this.resources = [];
    this.preloadedImages = {};

    this.L = lauxlib.luaL_newstate();
    lualib.luaL_openlibs(this.L);
    lauxlib.luaL_requiref(this.L, 'js', js.luaopen_js, false);
    this.run(vm);
    lua.lua_setglobal(this.L, 'vm');

    js.push(this.L, () => {
      this.characters = JSON.parse(js.tojs(this.L, -1));
      this.characters.forEach((character) => {
        const c = character;
        c.id = c.name;
        c.sprites.forEach((sprite) => {
          const s = sprite;
          s.id = `${c.name}/${s.name}`;
        });
      });
    });
    lua.lua_setglobal(this.L, 'defineCharacters');
    js.push(this.L, () => {
      this.resources = JSON.parse(js.tojs(this.L, -1));
    });
    lua.lua_setglobal(this.L, 'preloadResources');
  }

  async reload(chunk: string) {
    lua.lua_pushstring(this.L, to_luastring(chunk));
    lua.lua_setglobal(this.L, 's');
    /*
     * This is a work-around: only "print" and "require"
     * are allowed to get injected into the brocatel env.
     *
     * TODO: Should fix that in brocatel soon.
     */
    this.run(`story=vm.load_vm(s, nil, {
      print = {
        defineCharacters = defineCharacters,
        preloadResources = preloadResources,
      }
    })`);
    await this.preloadResources();
    this.loaded = true;
  }

  getImage(s: string): SpriteImage {
    return this.preloadedImages[s];
  }

  async preloadResources() {
    this.preloadedImages = {};
    const images = this.characters.flatMap((c) => c.sprites.map((s) => {
      const image = new Image();
      return new Promise<[string, SpriteImage]>((resolve, reject) => {
        image.src = s.url;
        const sprite = s as SpriteImage;
        sprite.image = image;
        image.onload = () => resolve(
          [`${c.name}/${s.name}`, sprite],
        );
        image.onerror = reject;
      });
    }));
    this.preloadedImages = Object.fromEntries(await Promise.all(images));
  }

  next(option?: number): StoryLine | undefined {
    if (!this.loaded) {
      return undefined;
    }
    if (option) {
      lua.lua_pushnumber(this.L, option);
    } else {
      lua.lua_pushnil(this.L);
    }
    lua.lua_setglobal(this.L, 'option');
    this.run('return story:next(option)');
    const content = tojs(this.L, -1);
    lua.lua_pop(this.L, 1);
    return content;
  }

  private run(code: string) {
    if (lauxlib.luaL_dostring(this.L, to_luastring(code)) !== lua.LUA_OK) {
      throw new Error(`error running ${code}: ${lua.lua_tojsstring(this.L, -1)}`);
    }
  }
}
