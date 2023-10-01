<script setup lang="ts">
import {
  computed, onUnmounted, ref, watch,
} from 'vue';

import StoryScene from './StoryScene.vue';
import { StoryInterpreter } from '../story/interpreter';
import type { CharacterSprite } from '../types/character';

const props = defineProps<{
  chunk?: string,
}>();

const story = new StoryInterpreter();
let backgroundMusic: HTMLAudioElement | null = null;
const background = ref('');
const style = ref<'auto' | 'width'>('auto');
const narrator = ref('');
const narratorColor = ref('');
const narratorHtml = computed(() => `<span style="color: ${narratorColor.value}">${narrator.value}</span>`);
const sprites = ref<CharacterSprite[]>([]);
const text = ref('');

function nextLine() {
  let line = story.next();
  while (line) {
    if (line.tags.background !== undefined) {
      background.value = line.text.trim().replace(/\\/g, '');
      const display = line.tags.background.trim();
      if (display === 'auto' || display === 'width') {
        style.value = display;
      }
    } else if (line.tags.audio !== undefined) {
      const audio = line.text.trim().replace(/\\/g, '');
      if (backgroundMusic !== null) {
        backgroundMusic.pause();
        backgroundMusic = null;
      }
      if (audio !== '') {
        backgroundMusic = new Audio(audio);
        backgroundMusic.loop = true;
        backgroundMusic.play();
      }
    } else {
      narrator.value = line.tags.narrator ?? '';
      narratorColor.value = line.tags.color ?? '';
      if (line.tags.sprites !== undefined) {
        sprites.value = line.tags.sprites.split('|')
          .map((s) => s.trim().replace(/\\/g, ''))
          .map((s) => (s === '' ? null : story.getImage(s)))
          .filter((s) => s) as CharacterSprite[];
      }
      text.value = line.text;
      return;
    }
    line = story.next();
  }
}

async function getGlobalStory() {
  const script = document.head.querySelector('script[type="application/lua"]');
  return script?.innerHTML ?? await fetch('./sample.lua').then((res) => res.text()) ?? '';
}

async function updateStory(chunk?: string) {
  const s = chunk ?? await getGlobalStory();
  if (s.trim() === '') {
    return;
  }
  background.value = '';
  sprites.value = [];
  narrator.value = '';
  narratorColor.value = '';
  text.value = '';
  backgroundMusic?.pause();
  backgroundMusic = null;
  await story.reload(s);
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
    :narrator-html="narratorHtml"
    :sprites="sprites"
    :text-html="text"
    @click="nextLine"
  >
  </story-scene>
</template>
