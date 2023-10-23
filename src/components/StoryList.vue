<script setup lang="ts">
import {
  NEllipsis, NMenu, NTreeSelect,
  type MenuOption, type TreeSelectOption,
} from 'naive-ui';
import { h } from 'vue';

import {
  type ChapterType, type GfChaptersInfo,
} from '../types/assets';

import jsonChapterPresets from '../assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

defineProps<{
  value: string,
}>();
const emit = defineEmits<{
  'update:value': [value: string],
}>();

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
  generateChapterOption('main', '主线剧情'),
  generateChapterOption('event', '小型活动'),
  generateChapterOption('colab', '联动'),
  generateChapterOption('upgrading', '心智升级'),
  generateChapterOption('bonding', '格里芬往事'),
  generateChapterOption('anniversary', '周年庆'),
  generateChapterOption('anniversary6', '六周年周年庆'),
  generateChapterOption('anniversary5', '五周年周年庆'),
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
</script>

<template>
  <n-tree-select :options="data"
    :value="value" @update-value="(v) => emit('update:value', v)"
    placeholder="搜索" filterable show-path :render-label="(v) => renderLabel(v.option)"
  >
  </n-tree-select>
  <n-menu ref="menu" :options="data"
    :value="value" @update-value="(v) => emit('update:value', v)"
    :root-indent="24" :indent="12"
    accordion :render-label="(v) => renderLabel(v as MenuOption & TreeSelectOption)"
  >
  </n-menu>
</template>
