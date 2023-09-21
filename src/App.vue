<script setup lang="ts">
import { darkTheme, NConfigProvider } from 'naive-ui';
import { ref } from 'vue';

import LineList from './components/LineList.vue';
import { type Line, defaultLine } from './types/lines';

const story = ref<Array<Line>>([defaultLine()]);
</script>

<template>
  <n-config-provider :theme="darkTheme">
    <line-list v-model="story"></line-list>
  </n-config-provider>
</template>

<style scoped></style>
