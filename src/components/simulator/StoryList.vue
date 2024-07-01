<script setup lang="ts">
import {
  NEllipsis, NIcon,
  NInput, NMenu, NModal,
  type MenuOption, type TreeSelectOption,
} from 'naive-ui';
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
function selectItem(v: string) {
  if (v.startsWith('map|')) {
    const chapter = v.split('|')[1];
    showMap.value = true;
    chapterEp.value = chapter;
    return;
  }
  showMap.value = false;
  setTitle(v);
  emit('update:value', v);
}
watch(chartSelected, (v) => {
  selectItem(v);
});
</script>

<template>
  <n-input v-model:value="filter" placeholder="搜索" clearable :disabled="preventAutofocus">
    <template #prefix>
      <n-icon :component="SearchFilled" />
    </template>
  </n-input>
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
</template>
