<script setup lang="ts">
import { ref } from 'vue';
import LineList from './components/LineList.vue';
import { type Line, defaultLine } from './types/lines';

const story = ref<Array<Line>>([defaultLine()]);
</script>

<template>
  <div>
    <line-list v-model="story"></line-list>
  </div>
</template>

<style scoped></style>
