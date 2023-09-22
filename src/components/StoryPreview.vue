<script setup lang="ts">
import { watch } from 'vue';

import StoryInterpreter from '../story/interpreter';

const props = defineProps<{
  story: string,
}>();

const s = new StoryInterpreter();

watch(() => props.story, (story) => {
  if (story.trim() === '') {
    return;
  }
  s.reload(story);
  console.log(s.next());
});
</script>

<template>
  <div>{{ story }}</div>
</template>
