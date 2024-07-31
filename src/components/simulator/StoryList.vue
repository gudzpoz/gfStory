<script setup lang="ts">
import MiniSearch, { type SearchResult } from 'minisearch';
import {
  NButton, NEllipsis, NFlex, NIcon,
  NInput, NMenu, NModal, NPopover, NSpin,
  type MenuOption, type TreeSelectOption,
} from 'naive-ui';
import { bigram } from 'n-gram';
import { SearchFilled } from '@vicons/material';
import {
  computed, h, ref, onMounted, nextTick, watch,
} from 'vue';

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

const searcher = ref<MiniSearch>();
const searchImported = ref('下载索引文件中……');
const searchResults = ref<SearchResult[]>([]);
const reverseTitleIndex = ref<Record<string, string>>({});
async function search() {
  showSearch.value = true;
  if (searchImported.value !== '') {
    const keys = (await (await fetch('/search/index.json')).json()) as string[];
    const text = (await Promise.all(keys.map(async (key) => {
      const path = `/search/${key}`;
      const t = (await fetch(path)).text();
      searchImported.value += '.';
      return t;
    }))).join('');
    searchImported.value = '正在将索引文件加载入内存……（可能需要半分钟）';
    searcher.value = await MiniSearch.loadJSONAsync(text, {
      fields: ['text'],
      storeFields: ['id'],
      tokenize: bigram,
    });
    searchImported.value = '正在关联章节名称……';
    reverseTitleIndex.value = Object.fromEntries(
      Object.values(chapterPresets)
        .flat()
        .flatMap((chapter) => chapter.stories.flatMap((story) => story.files.map((f, i) => {
          if (typeof f === 'string') {
            return [f, `${chapter.name} - ${story.name} - ${i}`];
          }
          return [f[0], `${chapter.name} - ${story.name} - ${f[1]}`];
        }))),
    );
    searchImported.value = '';
  }
  const results = searcher.value!.search(filter.value);
  searchResults.value = results;
}
function joinBigramTerms(terms: string[]): string {
  return terms.reduce((joined, append) => {
    const intersection = append.substring(0, 1);
    if (joined.endsWith(intersection)) {
      return `${joined}${append.substring(1)}`;
    }
    return `${joined}, ${append}`;
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
  <n-modal v-model:show="showSearch" preset="card" size="huge">
    <n-spin v-if="searchImported !== ''" />
    <span v-if="searchImported !== ''">{{ searchImported }}</span>
    <ul class="search-results">
      <li v-for="result in searchResults" :key="result.id" @click="selectItem(result.id)">
        <span>{{ reverseTitleIndex[result.id] ?? result.id }}</span>
        : {{ joinBigramTerms(result.terms) }}
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
</style>
