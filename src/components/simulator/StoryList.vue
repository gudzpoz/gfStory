<script setup lang="ts">
import initJieba, { cut as cutJieba } from 'jieba-wasm';
import {
  NButton, NEllipsis, NFlex, NIcon,
  NInput, NMenu, NModal, NPopover, NSpin,
  type MenuOption, type TreeSelectOption,
} from 'naive-ui';
import { SearchFilled } from '@vicons/material';
import {
  computed, h, ref, onMounted, nextTick, watch,
} from 'vue';

// eslint-disable-next-line import/no-unresolved
import jiebaUrl from '@/../node_modules/jieba-wasm/pkg/web/jieba_rs_wasm_bg.wasm?url';

import {
  type Chapter, type ChapterType, type GfChaptersInfo,
} from '../../types/assets';
import { MAPPED_CHAPTERS } from './edges';
import StoryChart from './StoryChart.vue';

import jsonChapterPresets from '../../assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

const props = defineProps<{
  value: string,
  setTitleWhenSelected?: boolean,
}>();
const emit = defineEmits<{
  'update:value': [value: string],
}>();

const filter = ref('');
const preventAutofocus = ref(true);
onMounted(() => nextTick(() => {
  preventAutofocus.value = false;
}));
const showMap = ref(false);

function generateLeafOption(
  pair: string | string[],
  i: number,
): MenuOption & TreeSelectOption {
  const description = '';
  if (typeof pair === 'string') {
    return { key: pair, label: `阶段 ${i + 1}`, description };
  }
  return { key: pair[0], label: pair[1], description };
}

function generateStoryOptions(chapter: Chapter) {
  const stories: (MenuOption & TreeSelectOption)[] = chapter.stories.map((story) => {
    const key = typeof story.files[0] === 'string' ? story.files[0] : story.files[0][0];
    if (story.files.length === 0) {
      return { key, label: story.name, disabled: true };
    }
    if (story.files.length === 1) {
      return { key, label: story.name, description: story.description };
    }
    return {
      key: `:${key}`,
      label: story.name,
      description: story.description,
      children: story.files.map((file, k) => generateLeafOption(file, k)),
    };
  });
  const ep = MAPPED_CHAPTERS.find((s) => chapter.name.startsWith(`${s} `));
  if (ep) {
    stories.unshift(generateLeafOption([`map|${ep}`, '选关界面'], 0));
  }
  return stories;
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
      children: generateStoryOptions(chapter),
    })),
  };
}

const rawData: (MenuOption & TreeSelectOption)[] = [
  generateChapterOption('main', '主线剧情'),
  generateChapterOption('event', '小型活动'),
  generateChapterOption('colab', '联动'),
  generateChapterOption('upgrading', '心智升级'),
  generateChapterOption('bonding', '格里芬往事'),
  generateChapterOption('anniversary', '七周年周年庆'),
  generateChapterOption('anniversary6', '六周年周年庆'),
  generateChapterOption('anniversary5', '五周年周年庆'),
  generateChapterOption('anniversary4', '四周年周年庆'),
  generateChapterOption('help', '求救回信'),
  generateChapterOption('skin', '皮肤故事'),
];
function filterOptions(
  options: (MenuOption & TreeSelectOption)[],
): (MenuOption & TreeSelectOption)[] {
  return options.map((option) => {
    if (option.label?.includes(filter.value)) {
      return option;
    }
    if (option.children) {
      const filtered = filterOptions(option.children);
      if (filtered.length > 0) {
        return { ...option, children: filtered };
      }
    }
    return null;
  }).filter((x): x is (MenuOption & TreeSelectOption) => x !== null);
}
const data = computed(() => {
  if (filter.value === '') {
    return rawData;
  }
  return filterOptions(rawData);
});
function getKeys(options: (MenuOption & TreeSelectOption)[]): string[] {
  return options.flatMap((option) => {
    if (option.children) {
      return [option.key as string, ...getKeys(option.children)];
    }
    return [option.key as string];
  });
}
const expandedKeys = computed(() => {
  if (filter.value === '') {
    return undefined;
  }
  const keys = getKeys(data.value);
  if (keys.length > 16) {
    return undefined;
  }
  return keys;
});

function renderLabel(option: MenuOption & TreeSelectOption) {
  const label = h('span', { className: 'story-heading' }, { default: () => option.label });
  if (!option.description || (option.description as string).trim() === '') {
    return label;
  }
  return h(NEllipsis, { trigger: 'hover' }, {
    default: () => [label, option.description as string],
  });
}

function setTitle(key: string) {
  if (!props.setTitleWhenSelected) {
    return;
  }
  function find(
    children: (MenuOption & TreeSelectOption)[],
  ): (MenuOption & TreeSelectOption)[] | null {
    return children.map((child) => {
      if (child.key === key) {
        return [child];
      }
      if (child.children) {
        const found = find(child.children);
        if (found) {
          found.unshift(child);
          return found;
        }
      }
      return null;
    }).filter((x): x is (MenuOption & TreeSelectOption)[] => x !== null)[0];
  }
  const found = find(data.value);
  if (found) {
    const label = found.slice(1).map((x) => x.label).join(' > ');
    document.title = label;
  } else {
    document.title = key;
  }
}
const chapterEp = ref('');
const chartSelected = ref('');
const showSearch = ref(false);
function selectItem(v: string) {
  if (v.startsWith('map|')) {
    const chapter = v.split('|')[1];
    showMap.value = true;
    chapterEp.value = chapter;
    return;
  }
  showSearch.value = false;
  showMap.value = false;
  setTitle(v);
  emit('update:value', v);
}
watch(chartSelected, (v) => {
  selectItem(v);
});

interface PageFindResult {
  url: string;
  raw_url: string;
  content: string;
  excerpt: string;
  locations: number[];
}
interface PageFind {
  init: () => Promise<void>;
  options: (options: {
    ranking: {
      pageLength?: number;
      termFrequency?: number;
      termSimilarity?: number;
      termSaturation?: number;
    },
  }) => Promise<void>;
  search: (text: string) => Promise<{
    results: {
      id: string,
      data: () => Promise<PageFindResult>,
      score: number,
      words: number[],
    }[],
  }>;
}
const pagefind = ref<PageFind>();
const searchResults = ref<PageFindResult[]>([]);
const reverseTitleIndex = ref<Record<string, string>>({});
async function search() {
  showSearch.value = true;
  if (!pagefind.value) {
    const base = window.location.href;
    await initJieba(jiebaUrl);
    const pf: PageFind = await import(/* @vite-ignore */ new URL('/search/pagefind.js', base).href);
    await pf.options({
      ranking: {
        pageLength: 0,
        termFrequency: 0,
      },
    });
    await pf.init();
    pagefind.value = pf;
    reverseTitleIndex.value = Object.fromEntries(
      Object.values(chapterPresets)
        .flat()
        .flatMap((chapter) => chapter.stories.flatMap((story) => story.files.map((f) => {
          if (typeof f === 'string') {
            return [f, `${chapter.name} - ${story.name}`];
          }
          return [f[0], `${chapter.name} - ${story.name} - ${f[1]}`];
        }))),
    );
  }
  const index = await pagefind.value!.search(cutJieba(filter.value, false).join(' '));
  const results = await Promise.all(index.results.map((result) => result.data()));
  searchResults.value = results.sort((a, b) => {
    const aRank = a.content.includes(filter.value) ? 1 : 0;
    const bRank = b.content.includes(filter.value) ? 1 : 0;
    return bRank - aRank;
  });
}
</script>

<template>
  <n-flex>
    <n-input
      v-model:value="filter"
      placeholder="搜索"
      clearable
      autosize
      :disabled="preventAutofocus"
      style="flex: 1"
    >
      <template #prefix>
        <n-icon :component="SearchFilled" />
      </template>
    </n-input>
    <n-popover trigger="hover">
      <template #trigger>
        <n-button @click="search()">全文搜索</n-button>
      </template>
      <span>初始化会很~~卡~~</span>
    </n-popover>
  </n-flex>
  <n-modal v-model:show="showMap" preset="card" size="huge">
    <template #header>
      <span>剧情前后连接</span>
    </template>
    <story-chart :ep-name="chapterEp" v-model:value="chartSelected" />
  </n-modal>
  <n-menu
    ref="menu"
    :options="data"
    :value="value"
    @update-value="selectItem"
    :accordion="filter === '' || expandedKeys === undefined"
    :expanded-keys="expandedKeys"
    :root-indent="24"
    :indent="12"
    :render-label="(v) => renderLabel(v as MenuOption & TreeSelectOption)"
  >
  </n-menu>
  <n-modal
    v-model:show="showSearch" preset="card" size="huge"
    style="max-width: 90vw; max-height: 90vh; overflow-y: auto;"
  >
    <n-spin v-if="!pagefind" />
    <ul class="search-results">
      <li v-for="result in searchResults" :key="result.raw_url" @click="selectItem(result.raw_url)">
        <span class="title">{{ reverseTitleIndex[result.raw_url] ?? result.raw_url }}</span>
        <p class="excerpt" v-html="result.excerpt" />
      </li>
    </ul>
  </n-modal>
</template>
<style scoped>
.search-results li {
  cursor: pointer;
}
.search-results li:hover {
  background-color: #222;
}
.search-results li span.title {
  font-size: 1.4em;
}
.search-results li p.excerpt {
  font-size: 0.9em;
}
.search-results li p.excerpt mark {
  text-decoration: underline;
}
</style>
