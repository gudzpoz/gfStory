<script setup lang="ts">
import {
  NConfigProvider,
  NDrawer, NDrawerContent,
  darkTheme, zhCN,
  type MenuInst,
} from 'naive-ui';
import {
  onMounted, ref, watch,
} from 'vue';

import StoryList from './components/StoryList.vue';
import StoryTeller from './components/StoryTeller.vue';
import { compileMarkdown } from './story/compiler';
import {
  STORY_PATH_PREFIX,
} from './types/assets';

const chunk = ref('');
const loading = ref(false);
async function switchStory(path: string) {
  loading.value = true;
  try {
    const markdown = await fetch(path).then((res) => res.text());
    chunk.value = await compileMarkdown(markdown);
    loading.value = false;
  } catch (e) {
    loading.value = false;
  }
}

const showMenu = ref(false);

const value = ref('');
const menu = ref<MenuInst>();
watch(() => value.value, (v) => {
  menu.value?.showOption(v);
  if (v.includes('|')) {
    const [title, file] = v.split('|');
    const url = new URL(window.location.toString());
    if (url.searchParams.get('story') !== v) {
      url.searchParams.set('story', v);
      window.history.pushState({}, '', url);
    }
    document.title = title;
    switchStory(`${STORY_PATH_PREFIX}${file}`);
  }
});

function updateFromLocation() {
  const search = new URLSearchParams(window.location.search);
  const story = search.get('story');
  if (story && story !== '') {
    value.value = story;
  }
}

// StorySimulator should never get unmounted, so not registering unmount hooks to remove listeners.
const width = ref(window.innerWidth);
onMounted(() => {
  updateFromLocation();
  window.addEventListener('popstate', () => {
    updateFromLocation();
  });
  window.addEventListener('resize', () => {
    width.value = window.innerWidth;
  });
});
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN">
    <n-drawer v-model:show="showMenu" :width="Math.min(width * 0.8, 400)" placement="left"
      display-directive="show"
    >
      <n-drawer-content title="剧情选择" :native-scrollbar="false">
        <story-list v-model:value="value"></story-list>
      </n-drawer-content>
    </n-drawer>
    <story-teller menu-button @menu="showMenu = true" :chunk="chunk" :loading="loading">
    </story-teller>
  </n-config-provider>
</template>

<style>
#app, .story-background {
  height: 100vh;
}
.story-heading {
  font-weight: bold;
  margin-right: 1em;
}
</style>
