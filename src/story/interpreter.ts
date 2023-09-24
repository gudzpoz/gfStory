import { fengari } from '@brocatel/mdc';
import vm from '@brocatel/mdc/dist/vm-bundle.lua?raw';

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
  };
}

export class StoryInterpreter {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  L: any;

  loaded: boolean;

  constructor() {
    this.loaded = false;
    this.L = lauxlib.luaL_newstate();
    lualib.luaL_openlibs(this.L);
    lauxlib.luaL_requiref(this.L, 'js', js.luaopen_js, false);
    this.run(vm);
    lua.lua_setglobal(this.L, 'vm');
  }

  reload(chunk: string) {
    lua.lua_pushstring(this.L, to_luastring(chunk));
    lua.lua_setglobal(this.L, 's');
    this.run('story=vm.load_vm(s)');
    this.loaded = true;
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
