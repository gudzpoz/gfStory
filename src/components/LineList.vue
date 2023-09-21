<script setup lang="ts">
import {
  NButton, NButtonGroup, NCard, NCollapse, NCollapseItem, NIcon, NTag,
} from 'naive-ui';
import {
  AddFilled, DeleteFilled, MoveDownFilled, MoveUpFilled, RefreshFilled,
} from '@vicons/material';
import { ref } from 'vue';

import StoryLineView from './lines/StoryLineView.vue';
import { type Line, defaultLine } from '../types/lines';

const props = withDefaults(defineProps<{
  modelValue?: Array<Line>,
}>(), {
  modelValue: () => [],
});
const lines = ref(props.modelValue);

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event:'update:modelValue', modelValue:Array<Line>): void,
}>();

const names = ref<Array<string>>([]);

function findIndexByCurrentName() {
  if (names.value.length === 0) {
    return -1;
  }
  const id = names.value[0];
  return lines.value.findIndex((line) => line.id === id);
}

function removeLine() {
  const i = findIndexByCurrentName();
  if (i !== -1) {
    lines.value.splice(i, 1);
  }
}

function moveUp() {
  const i = findIndexByCurrentName();
  if (i > 0) {
    const upper = lines.value[i - 1];
    lines.value[i - 1] = lines.value[i];
    lines.value[i] = upper;
  }
}

function moveDown() {
  const i = findIndexByCurrentName();
  if (i !== -1 && i + 1 < lines.value.length) {
    const lower = lines.value[i + 1];
    lines.value[i + 1] = lines.value[i];
    lines.value[i] = lower;
  }
}

function appendDefaultLine() {
  const line = defaultLine();
  lines.value.push(line);
  names.value = [line.id];
}
</script>

<template>
  <n-card class="list-operations">
    <n-button-group>
      <n-button @click="appendDefaultLine" type="primary">
        <n-icon><add-filled></add-filled></n-icon>
      </n-button>
      <n-button @click="removeLine" type="error">
        <n-icon><delete-filled></delete-filled></n-icon>
      </n-button>
      <n-button @click="moveUp" secondary type="primary">
        <n-icon><move-up-filled></move-up-filled></n-icon>
      </n-button>
      <n-button @click="moveDown" secondary type="primary">
        <n-icon><move-down-filled></move-down-filled></n-icon>
      </n-button>
      <n-button @click="emit('update:modelValue', lines)" type="warning">
        <n-icon><refresh-filled></refresh-filled></n-icon>
      </n-button>
    </n-button-group>
  </n-card>
  <n-collapse display-directive="if" accordion v-model:expanded-names="names">
    <n-collapse-item v-for="line in lines" :key="line.id" :name="line.id">
      <story-line-view :modelValue="line"></story-line-view>
      <template #header>
        <n-tag type="success">
          {{ line.type === 'text' ? '文本节点' : '功能节点' }}
        </n-tag>
      </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style>
.n-collapse {
  padding: 24px;
  width: auto;
}

.list-operations {
  position: sticky;
  top: 0;
  z-index: 1;
}
</style>
