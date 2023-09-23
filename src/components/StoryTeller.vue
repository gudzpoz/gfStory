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
const text = ref('');

function nextLine() {
  let line = story.next();
  while (line) {
    if (line.tags.narrator !== undefined) {
      narrator.value = line.text.trim();
      narratorColor.value = line.tags.color;
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
  story.reload(s);
  nextLine();
});
</script>

<template>
  <story-scene
    :background-url="background"
    :narrator-html="narratorHtml"
    :text-html="text"
    @click="nextLine"
  >
  </story-scene>
</template>
