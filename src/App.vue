<script setup lang="ts">
import {
  darkTheme, zhCN,
  NConfigProvider, NLayout, NLayoutContent, NLayoutSider,
} from 'naive-ui';
import { ref } from 'vue';

import LineList from './components/LineList.vue';
import StoryTeller from './components/StoryTeller.vue';
import { type Line, defaultLine } from './types/lines';
import { compileMarkdown, linesToMarkdown } from './story/compiler';

const markdown = ref('');

async function updateStory(story: Line[]) {
  markdown.value = await compileMarkdown(linesToMarkdown(story));
}
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN">
    <n-layout has-sider sider-placement="right" style="height: 100vh">
      <n-layout-content>
        <line-list :modelValue="[defaultLine()]" @update:modelValue="updateStory"></line-list>
      </n-layout-content>
      <n-layout-sider show-trigger="arrow-circle" width="500px" bordered>
        <story-teller :chunk="markdown"></story-teller>
      </n-layout-sider>
    </n-layout>
  </n-config-provider>
</template>

<style scoped></style>
