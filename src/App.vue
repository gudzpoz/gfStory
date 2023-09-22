<script setup lang="ts">
import {
  darkTheme, NConfigProvider, NLayout, NLayoutContent, NLayoutSider,
} from 'naive-ui';
import { ref } from 'vue';

import LineList from './components/LineList.vue';
import StoryPreview from './components/StoryPreview.vue';
import { type Line, defaultLine } from './types/lines';
import { compileMarkdown, linesToMarkdown } from './story/compiler';

const markdown = ref('');

async function updateStory(story: Line[]) {
  markdown.value = await compileMarkdown(linesToMarkdown(story));
}
</script>

<template>
  <n-config-provider :theme="darkTheme">
    <n-layout has-sider sider-placement="right" style="height: 100vh">
      <n-layout-content>
        <line-list :modelValue="[defaultLine()]" @update:modelValue="updateStory"></line-list>
      </n-layout-content>
      <n-layout-sider show-trigger="arrow-circle">
        <story-preview :story="markdown"></story-preview>
      </n-layout-sider>
    </n-layout>
  </n-config-provider>
</template>

<style scoped></style>
