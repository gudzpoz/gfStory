<script setup lang="ts">
import type { SelectLine, TextLine } from '@brocatel/mdc';
import {
  computed, onUnmounted, ref, watch,
} from 'vue';
import { HistoryFilled, MenuFilled, PlayArrowFilled } from '@vicons/material';

import StoryScene from './StoryScene.vue';
import { StoryInterpreter, type SpriteImage, type Tags } from '../../story/interpreter';

const props = defineProps<{
  chunk?: string,

  loading?: boolean,
  menuButton?: boolean,
}>();

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'menu'): void,
}>();

const story = new StoryInterpreter();
let backgroundMusic: HTMLAudioElement | null = null;
const background = ref('');
const classes = ref<string[]>([]);
const style = ref<string>('cover');
const narrator = ref('');
const narratorColor = ref('');
const narratorHtml = computed(() => `<span style="color: ${narratorColor.value}">${narrator.value}</span>`);
const sprites = ref<SpriteImage[]>([]);
const remote = ref<Set<string>>(new Set<string>());
const text = ref('');
const ended = ref(false);
const auto = ref(false);
const autoSpeed = ref(1);
const options = ref<SelectLine['select']>([]);
const history: [string, string][] = [];

function toText(s: string) {
  return s.trim().replace(/\\/g, '');
}

const showingHistory = ref<[string, string][]>();
function showHistory() {
  showingHistory.value = history;
}

function updateClasses(classString: string) {
  const classUpdates = classString.split(' ').map((s) => s.trim()).filter((s) => s !== '');
  const newClasses = classes.value.concat(classUpdates.filter((s) => !s.startsWith('!')));
  classUpdates.filter((s) => s.startsWith('!')).forEach((s) => {
    const name = s.substring(1);
    let i = newClasses.indexOf(name);
    while (i !== -1) {
      newClasses.splice(i, 1);
      i = newClasses.indexOf(name);
    }
  });
  classes.value = newClasses;
}

function updateAudio(audio: string) {
  if (backgroundMusic !== null) {
    backgroundMusic.pause();
    backgroundMusic = null;
  }
  if (audio !== '') {
    backgroundMusic = new Audio(audio);
    backgroundMusic.loop = true;
    try {
      backgroundMusic.play();
    } catch (_) { /* empty */ }
  }
}

function playAudio(audio: string) {
  const sePlayer = new Audio(audio);
  sePlayer.loop = false;
  try {
    sePlayer.play();
  } catch (_) { /* empty */ }
}

function updateLine(line: string, tags: Record<string, string>) {
  narrator.value = toText(tags.narrator ?? '');
  narratorColor.value = tags.color ?? '';
  if (tags.sprites !== undefined) {
    sprites.value = tags.sprites.split('|').map(toText)
      .map((s) => {
        const [name, n, effects] = s.split('/');
        const image = s === '' ? null : story.getImage(`${name}/${n}`);
        if (effects === '') {
          return image;
        }
        return {
          ...image,
          effects: effects.split(','),
        };
      })
      .filter((s) => s) as SpriteImage[];
  }
  if (tags.remote !== undefined) {
    remote.value = new Set(tags.remote.split('|').map(toText));
  }
  text.value = line;
  history.push([narrator.value, line]);
}

function nextLine(option?: number) {
  if (showingHistory.value) {
    showingHistory.value = undefined;
    return;
  }
  if (option === undefined && options.value.length > 0) {
    return;
  }

  let l = story.next(option);
  while (l) {
    if ((l as SelectLine).select) {
      const line = l as SelectLine;
      options.value = line.select;
      return;
    }
    options.value = [];

    const line = l as TextLine;
    const tags = line.tags as Tags;
    if (tags.classes) {
      updateClasses(tags.classes);
    }

    if (tags.background !== undefined) {
      background.value = toText(line.text);
      const display = tags.background.trim();
      style.value = display;
    } else if (tags.se !== undefined) {
      playAudio(toText(line.text));
    } else if (tags.audio !== undefined) {
      updateAudio(toText(line.text));
    } else {
      updateLine(line.text, tags);
      return;
    }
    l = story.next();
  }
  text.value = '<i>故事结束</i>';
  ended.value = true;
}

async function getGlobalStory() {
  const script = document.head.querySelector('script[type="application/lua"]');
  return script?.innerHTML ?? await fetch('./sample.lua').then((res) => res.text()) ?? '';
}

const preloading = ref(false);
async function updateStory(chunk?: string) {
  const s = chunk ?? await getGlobalStory();
  if (s.trim() === '') {
    return;
  }
  preloading.value = true;
  background.value = '';
  style.value = 'cover';
  classes.value = [];
  sprites.value = [];
  remote.value = new Set();
  narrator.value = '';
  narratorColor.value = '';
  text.value = '';
  ended.value = false;
  options.value = [];
  backgroundMusic?.pause();
  backgroundMusic = null;
  history.splice(0);
  await story.reload(s);
  preloading.value = false;
  auto.value = false;
  // autoSpeed.value = 1; // Do not reset autoSpeed
  nextLine();
}
updateStory(props.chunk);
watch(() => props.chunk, updateStory);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let autoHandle: any = 0;
function scheduleAuto() {
  if (auto.value) {
    autoHandle = setTimeout(nextLine, (text.value.length / 20) * (5000 / autoSpeed.value));
  } else if (autoHandle !== 0) {
    clearTimeout(autoHandle);
    autoHandle = 0;
  }
}
watch(auto, scheduleAuto);

onUnmounted(() => {
  backgroundMusic?.pause();
  backgroundMusic = null;
});
</script>

<template>
  <story-scene
    :background-url="background"
    :background-style="style"
    :classes="classes"
    :narrator-html="narratorHtml"
    :sprites="sprites"
    :remote="remote"
    :text-html="text"
    :pop-char-animation-interval="auto ? 42 / autoSpeed : 42"
    :options="options"
    @click="() => { auto = false; nextLine(); }"
    @choose="(v) => nextLine(v)"
    @animation-finished="scheduleAuto"
    :loading="loading || preloading"
    :history="showingHistory"
    :text-height="showingHistory ? 'calc(100vh - 6em - 24px)' : undefined"
  >
    <button v-if="menuButton" @click="emit('menu')">
      <menu-filled></menu-filled><span>菜单</span>
    </button>
    <button @click="showHistory">
      <history-filled></history-filled><span>回放</span>
    </button>
    <button v-if="!ended" @click="auto = !auto" :class="{ toggled: auto }">
      <play-arrow-filled></play-arrow-filled><span>自动</span>
    </button>
    <div class="auto-speed">
      <span v-if="auto">{{ autoSpeed }}</span>
      <input v-if="auto" type="range" min="1" max="10" v-model="autoSpeed" />
    </div>
  </story-scene>
</template>

<style>
.auto-speed {
  margin-left: 1em;
  position: relative;
  height: 45px;
  width: 90px;
  color: white;
  display: flex;
  align-items: center;
  opacity: 0.7;
}
.auto-speed > span::before {
  content: "X";
  transform: scaleX(0.8);
  display: inline-block;
}
.auto-speed > span {
  position: absolute;
  font-size: small;
  left: 0;
  top: -0.5em;
}
.auto-speed > input {
  margin: 0;
}
</style>

<style scoped>
/* https://css-tricks.com/styling-cross-browser-compatible-range-inputs-css/ */
input[type=range] {
  -webkit-appearance: none; /* Hides the slider so that custom slider can be made */
  appearance: none;
  width: 100%; /* Specific width is required for Firefox. */
  background: transparent; /* Otherwise white in Chrome */
}

input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
}

input[type=range]:focus {
  /* Removes the blue border.
   * You should probably do some kind of focus styling for accessibility reasons though.
   */
  outline: none;
}

input[type=range]::-ms-track {
  width: 100%;
  cursor: pointer;

  /* Hides the slider so custom styles can be added */
  background: transparent;
  border-color: transparent;
  color: transparent;
}

/* Special styling for WebKit/Blink */
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
  border: 1px solid #000000;
  height: 18px;
  width: 12px;
  border-radius: 2px;
  background: #ffffff;
  cursor: pointer;
  /* You need to specify a margin in Chrome, but in Firefox and IE it is automatic */
  margin-top: -14px;
  box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d; /* Add cool effects to your sliders! */
}

/* All the same stuff for Firefox */
input[type=range]::-moz-range-thumb {
  box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;
  border: 1px solid #000000;
  height: 18px;
  width: 12px;
  border-radius: 3px;
  background: #ffffff;
  cursor: pointer;
}

/* All the same stuff for IE */
input[type=range]::-ms-thumb {
  box-shadow: 1px 1px 1px #000000, 0px 0px 1px #0d0d0d;
  border: 1px solid #000000;
  height: 18px;
  width: 12px;
  border-radius: 3px;
  background: #ffffff;
  cursor: pointer;
}

input[type=range]::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  cursor: pointer;
  border-radius: 1.3px;
  border: 0.2px solid white;
}

input[type=range]::-moz-range-track {
  width: 100%;
  height: 3px;
  cursor: pointer;
  border-radius: 1.3px;
  border: 0.2px solid white;
}

input[type=range]::-ms-track {
  width: 100%;
  height: 8.4px;
  cursor: pointer;
  background: transparent;
  border-color: transparent;
  border-width: 16px 0;
  color: transparent;
}
input[type=range]::-ms-fill-lower {
  border: 0.2px solid white;
  border-radius: 2.6px;
}
input[type=range]::-ms-fill-upper {
  border: 0.2px solid white;
  border-radius: 2.6px;
}
</style>
