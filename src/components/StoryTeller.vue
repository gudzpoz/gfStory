<script setup lang="ts">
import type { SelectLine, TextLine } from '@brocatel/mdc';
import {
  computed, onUnmounted, ref, watch,
} from 'vue';
import { HistoryFilled, MenuFilled } from '@vicons/material';

import StoryScene from './StoryScene.vue';
import { StoryInterpreter, type SpriteImage, type Tags } from '../story/interpreter';

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
      .map((s) => (s === '' ? null : story.getImage(s)))
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
  options.value = [];
  backgroundMusic?.pause();
  backgroundMusic = null;
  history.splice(0);
  await story.reload(s);
  preloading.value = false;
  nextLine();
}
updateStory(props.chunk);
watch(() => props.chunk, updateStory);

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
    :options="options"
    @click="nextLine"
    @choose="(v) => nextLine(v)"
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
  </story-scene>
</template>
