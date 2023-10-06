<script setup lang="ts">
import {
  NDrawer, NDrawerContent,
  NMenu, NTooltip, NTreeSelect,
  type MenuInst, type MenuOption, type TreeSelectOption,
} from 'naive-ui';
import { h, ref, watch } from 'vue';

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
function generateLeafOption(key: string, label: string)
  : MenuOption & TreeSelectOption {
  return {
    key,
    label,
  };
}
function generateChapterOption(label: ChapterType, name: string): MenuOption & TreeSelectOption {
  const chapters = chapterPresets[label];
  return {
    key: label,
    label: name,
    children: chapters.map((chapter, i) => ({
      key: `${label}-${i}`,
      label: chapter.name,
      description: chapter.description,
      children: chapter.stories.map((story, j) => {
        const key = `${label}-${i}-${j}`;
        if (story.files.length === 0) {
          return { key, label: story.name, disabled: true };
        }
        if (story.files.length === 1) {
          return generateLeafOption(`${key}|${story.files[0]}`, story.name);
        }
        return {
          key,
          label: story.name,
          description: story.description,
          children: story.files.map((file, k) => generateLeafOption(`${key}|${file}`, `阶段 ${k}`)),
        };
      }),
    })),
  };
}
const data: (MenuOption & TreeSelectOption)[] = [
  generateChapterOption('main', '主线支线活动故事'),
  generateChapterOption('upgrading', '心智升级故事'),
  generateChapterOption('bonding', '格里芬往事'),
];
function renderLabel(option: MenuOption & TreeSelectOption) {
  if (!option.description || (option.description as string).trim() === '') {
    return option.label;
  }
  return h(NTooltip, { trigger: 'hover' }, {
    default: () => option.description,
    trigger: () => option.label,
  });
}
const value = ref('');
const menu = ref<MenuInst>();
watch(() => value.value, (v) => {
  menu.value?.showOption(v);
  if (v.includes('|')) {
    const [, file] = v.split('|');
    switchStory(`${STORY_PATH_PREFIX}${file}`);
  }
});
</script>

<template>
  <n-drawer v-model:show="showMenu" :width="300" max-width="80vw" placement="left"
    display-directive="show"
  >
    <n-drawer-content title="剧情选择" :native-scrollbar="false">
      <n-tree-select :options="data" v-model:value="value"
        placeholder="搜索" filterable show-path :render-label="(v) => renderLabel(v.option)"
      >
      </n-tree-select>
      <n-menu ref="menu" :options="data" v-model:value="value"
        :root-indent="36" :indent="12"
        accordion :render-label="(v) => renderLabel(v as MenuOption & TreeSelectOption)"
      >
      </n-menu>
    </n-drawer-content>
  </n-drawer>
  <story-teller menu-button @menu="showMenu = true" :chunk="chunk"></story-teller>
</template>

<style>
#app {
  height: 100vh;
}
</style>
