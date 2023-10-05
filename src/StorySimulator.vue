<script setup lang="ts">
import {
  NButton, NDrawer, NDrawerContent,
  NInput, NTree,
  type TreeOption,
} from 'naive-ui';
import { h, ref } from 'vue';

import StoryTeller from './components/StoryTeller.vue';
import { compileMarkdown } from './story/compiler';
import {
  STORY_PATH_PREFIX,
  type ChapterType, type GfChaptersInfo,
} from './types/assets';

import jsonChapterPresets from './assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

const chunk = ref('');
function switchStory(path: string) {
  fetch(path).then((res) => res.text()).then(compileMarkdown).then((compiled) => {
    chunk.value = compiled;
  });
}

const showMenu = ref(false);
const menuSearch = ref('');
function generateLeafOption(key: string, label: string, story: string): TreeOption {
  return {
    key,
    label,
    prefix: () => h(
      NButton,
      { onClick: () => switchStory(`${STORY_PATH_PREFIX}${story}`) },
      { default: () => '选择' },
    ),
  };
}
function generateChapterOption(label: ChapterType, name: string): TreeOption {
  const chapters = chapterPresets[label];
  return {
    key: label,
    label: name,
    children: chapters.map((chapter, i) => ({
      key: `${label}-${i}`,
      label: chapter.name,
      children: chapter.stories.map((story, j) => {
        const key = `${label}-${i}-${j}`;
        if (story.files.length === 0) {
          return { key, label: story.name };
        }
        if (story.files.length === 1) {
          return generateLeafOption(key, story.name, story.files[0]);
        }
        return {
          key,
          label: story.name,
          children: story.files.map((file, k) => generateLeafOption(`${key}/${file}`, `阶段 ${k}`, file)),
        };
      }),
    })),
  };
}
const data: TreeOption[] = [
  generateChapterOption('main', '主线支线活动故事'),
  generateChapterOption('upgrading', '心智升级故事'),
  generateChapterOption('bonding', '格里芬往事'),
];
</script>

<template>
  <n-drawer v-model:show="showMenu" :width="500" placement="left">
    <n-drawer-content title="剧情选择">
      <n-input v-model:value="menuSearch" placeholder="搜索"></n-input>
      <n-tree :pattern="menuSearch" :data="data"
        virtual-scroll
        :show-irrelevant-nodes="false"
      >
      </n-tree>
    </n-drawer-content>
  </n-drawer>
  <story-teller menu-button @menu="showMenu = true" :chunk="chunk"></story-teller>
</template>

<style>
#app {
  height: 100vh;
}
</style>
