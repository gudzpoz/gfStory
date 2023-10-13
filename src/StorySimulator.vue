<script setup lang="ts">
import {
  NConfigProvider,
  NDrawer, NDrawerContent,
  NEllipsis, NMenu, NTreeSelect,
  darkTheme, zhCN,
  type MenuInst, type MenuOption, type TreeSelectOption,
} from 'naive-ui';
import {
  h, onMounted, ref, watch,
} from 'vue';

import StoryTeller from './components/StoryTeller.vue';
import { compileMarkdown } from './story/compiler';
import {
  STORY_PATH_PREFIX,
  type ChapterType, type GfChaptersInfo,
} from './types/assets';

import jsonChapterPresets from './assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

const chunk = ref('');
const loading = ref(false);
function switchStory(path: string) {
  loading.value = true;
  fetch(path).then((res) => res.text()).then(compileMarkdown)
    .then((compiled) => {
      loading.value = false;
      chunk.value = compiled;
    })
    .catch(() => {
      loading.value = false;
    });
}

const showMenu = ref(false);
function generateLeafOption(key: string, pair: string[] | string, i: number, name?: string)
  : MenuOption & TreeSelectOption {
  const file = typeof pair === 'string' ? pair : pair[0];
  const label = name ?? (typeof pair === 'string' ? `阶段 ${i + 1}` : pair[1]);
  return {
    key: `${key}|${file}`,
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
          return generateLeafOption(key, story.files[0], 0, story.name);
        }
        return {
          key,
          label: story.name,
          description: story.description,
          children: story.files.map((file, k) => generateLeafOption(key, file, k)),
        };
      }),
    })),
  };
}
const data: (MenuOption & TreeSelectOption)[] = [
  generateChapterOption('main', '主线支线活动故事'),
  generateChapterOption('upgrading', '心智升级故事'),
  generateChapterOption('bonding', '格里芬往事'),
  generateChapterOption('anniversary', '周年庆'),
  generateChapterOption('skin', '皮肤故事'),
];
function renderLabel(option: MenuOption & TreeSelectOption) {
  const label = h('span', { className: 'story-heading' }, { default: () => option.label });
  if (!option.description || (option.description as string).trim() === '') {
    return label;
  }
  return h(NEllipsis, { trigger: 'hover' }, {
    default: () => [label, option.description as string],
  });
}
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
onMounted(() => {
  updateFromLocation();
  window.addEventListener('popstate', () => {
    updateFromLocation();
  });
});
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN">
    <n-drawer v-model:show="showMenu" :width="300" max-width="80vw" placement="left"
      display-directive="show"
    >
      <n-drawer-content title="剧情选择" :native-scrollbar="false">
        <n-tree-select :options="data" v-model:value="value"
          placeholder="搜索" filterable show-path :render-label="(v) => renderLabel(v.option)"
        >
        </n-tree-select>
        <n-menu ref="menu" :options="data" v-model:value="value"
          :root-indent="24" :indent="12"
          accordion :render-label="(v) => renderLabel(v as MenuOption & TreeSelectOption)"
        >
        </n-menu>
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
