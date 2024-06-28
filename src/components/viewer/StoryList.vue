<script setup lang="ts">
import {
  NEllipsis, NIcon, NInput, NMenu,
  type MenuOption, type TreeSelectOption,
} from 'naive-ui';
import { SearchFilled } from '@vicons/material';
import { computed, h, ref } from 'vue';

import {
  type ChapterType, type GfChaptersInfo,
} from '../../types/assets';

import jsonChapterPresets from '../../assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

defineProps<{
  value: string,
}>();
const emit = defineEmits<{
  'update:value': [value: string],
}>();

const filter = ref('');

function generateLeafOption(
  key: string,
  pair: string[] | string,
  i: number,
  name?: string,
  description?: string,
): MenuOption & TreeSelectOption {
  const file = typeof pair === 'string' ? pair : pair[0];
  const label = name ?? (typeof pair === 'string' ? `阶段 ${i + 1}` : pair[1]);
  return {
    key: `${key}|${file}`,
    label,
    description,
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
          return generateLeafOption(key, story.files[0], 0, story.name, story.description);
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

const rawData: (MenuOption & TreeSelectOption)[] = [
  generateChapterOption('main', '主线剧情'),
  generateChapterOption('event', '小型活动'),
  generateChapterOption('colab', '联动'),
  generateChapterOption('upgrading', '心智升级'),
  generateChapterOption('bonding', '格里芬往事'),
  generateChapterOption('anniversary', '周年庆'),
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
</script>

<template>
  <n-input v-model:value="filter" placeholder="搜索" clearable>
    <template #prefix>
      <n-icon :component="SearchFilled" />
    </template>
  </n-input>
  <n-menu
    ref="menu"
    :options="data"
    :value="value"
    @update-value="(v) => emit('update:value', v)"
    :accordion="filter === '' || expandedKeys === undefined"
    :expanded-keys="expandedKeys"
    :root-indent="24"
    :indent="12"
    :render-label="(v) => renderLabel(v as MenuOption & TreeSelectOption)"
  >
  </n-menu>
</template>
