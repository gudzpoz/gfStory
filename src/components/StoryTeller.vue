<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import StoryScene from './StoryScene.vue';
import { StoryInterpreter } from '../story/interpreter';

const props = defineProps<{
  chunk: string,
}>();

const story = new StoryInterpreter();
const background = ref('');
const narrator = ref('');
const narratorColor = ref('');
const narratorHtml = computed(() => `<span style="color: ${narratorColor.value}">${narrator.value}</span>`);
const sprites = ref<string[]>([]);
const text = ref('');

function nextLine() {
  let line = story.next();
  while (line) {
    if (line.tags.narrator !== undefined) {
      narrator.value = line.text.trim();
      narratorColor.value = line.tags.color ?? '';
    } else if (line.tags.background !== undefined) {
      background.value = line.text.trim().replace(/\\/g, '');
    } else if (line.tags.sprites !== undefined) {
      sprites.value = line.text.split('|').map((s) => s.trim().replace(/\\/g, ''));
    } else {
      text.value = line.text;
      return;
    }
    line = story.next();
  }
}

watch(() => props.chunk, (s) => {
  if (s.trim() === '') {
    return;
  }
  background.value = '';
  narrator.value = '';
  narratorColor.value = '';
  text.value = '';
  story.reload(s);
  nextLine();
});
</script>

<template>
  <story-scene
    :background-url="background"
    :narrator-html="narratorHtml"
    :sprites="sprites"
    :text-html="text"
    @click="nextLine"
  >
  </story-scene>
</template>
