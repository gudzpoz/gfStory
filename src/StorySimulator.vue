<script setup lang="ts">
import {
  NButton, NDrawer, NDrawerContent,
  NInput, NTree,
  type TreeOption,
} from 'naive-ui';
import { h, ref } from 'vue';

import StoryTeller from './components/StoryTeller.vue';
import { compileMarkdown } from './story/compiler';
import { STORY_PATH_PREFIX } from './types/assets';

import storyPresets from './assets/stories.json';

const chunk = ref('');
function switchStory(path: string) {
  fetch(path).then((res) => res.text()).then(compileMarkdown).then((compiled) => {
    chunk.value = compiled;
  });
}

const showMenu = ref(false);
const menuSearch = ref('');
const data: TreeOption[] = Object.keys(storyPresets).sort().map((name) => ({
  label: name,
  key: name,
  prefix: () => h(
    NButton,
    {
      onClick: () => switchStory(`${STORY_PATH_PREFIX}${
        (storyPresets as Record<string, string>)[name]
      }`),
    },
    { default: () => '选择' },
  ),
}));
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
