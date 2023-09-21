<script setup lang="ts">
import {
  NButton, NCollapse, NCollapseItem, NIcon,
} from 'naive-ui';
import { AddFilled, CloseFilled } from '@vicons/material';
import { ref } from 'vue';

import StoryLineView from './lines/StoryLineView.vue';
import { type Line, defaultLine } from '../types/lines';

const props = withDefaults(defineProps<{
  modelValue?: Array<Line>,
}>(), {
  modelValue: () => [],
});

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event:'update:modelValue', modelValue:Array<Line>): void,
}>();

function flushLines(lines: Array<Line>) {
  emit('update:modelValue', lines);
}

function removeLine(id: string) {
  const lines = props.modelValue;
  const i = lines.findIndex((line) => line.id === id);
  lines.splice(i, 1);
  flushLines(lines);
}

function appendDefaultLine() {
  const lines = props.modelValue;
  lines.push(defaultLine());
  flushLines(lines);
}

const expandedNames = ref<Array<string | number>>([]);
function expandOnlyOne(name: string | number, expanded: boolean) {
  if (expanded) {
    expandedNames.value = [name];
  } else {
    expandedNames.value = [];
  }
}
</script>

<template>
  <n-collapse display-directive="if"
    :expanded-names="expandedNames"
    @item-header-click="(info) => expandOnlyOne(info.name, info.expanded)"
  >
    <n-collapse-item v-for="line in modelValue" :key="line.id">
      <story-line-view :modelValue="line"></story-line-view>
      <template #header-extra>
        <n-button @click="removeLine(line.id)">
          <n-icon><close-filled></close-filled></n-icon>
        </n-button>
      </template>
    </n-collapse-item>
  </n-collapse>
  <n-button @click="appendDefaultLine()">
    <n-icon><add-filled></add-filled></n-icon>
  </n-button>
</template>
