<script setup lang="ts">
import {
  NButton, NButtonGroup, NCard, NCollapse, NCollapseItem, NIcon, NSpace, NTag,
} from 'naive-ui';
import {
  AddFilled, DeleteFilled, MoveDownFilled, MoveUpFilled, RefreshFilled,
} from '@vicons/material';
import { computed, provide, ref } from 'vue';

import StoryLineView from './lines/StoryLineView.vue';
import { type Line, defaultLine, type TextLine } from '../types/lines';

const props = withDefaults(defineProps<{
  modelValue?: Array<Line>,
}>(), {
  modelValue: () => [],
});
const lines = ref(props.modelValue);
provide('narrators', computed(() => {
  const narrators = lines.value
    .filter((line) => line.type === 'text' && line.narrator !== '')
    .map((line) => (line as TextLine).narrator);
  return [...new Set(narrators)]
    .map((narrator) => ({
      label: narrator,
      value: narrator,
    }));
}));

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

function pruneHtml(html: string, limit = 10) {
  const container = document.createElement('div');
  container.innerHTML = html;
  const text = container.innerText;
  return text.length > limit ? `${text.substring(0, limit)}...` : text;
}
</script>

<template>
  <n-card class="list-operations">
    <n-button-group>
      <n-button @click="appendDefaultLine" type="primary">
        <n-icon><add-filled></add-filled></n-icon>添加节点
      </n-button>
      <n-button @click="removeLine" type="error">
        <n-icon><delete-filled></delete-filled></n-icon>移除当前
      </n-button>
      <n-button @click="moveUp" secondary type="primary">
        <n-icon><move-up-filled></move-up-filled></n-icon>上移
      </n-button>
      <n-button @click="moveDown" secondary type="primary">
        <n-icon><move-down-filled></move-down-filled></n-icon>下移
      </n-button>
      <n-button @click="emit('update:modelValue', lines)" type="warning">
        <n-icon><refresh-filled></refresh-filled></n-icon>预览故事
      </n-button>
    </n-button-group>
  </n-card>
  <n-collapse display-directive="if" accordion v-model:expanded-names="names">
    <n-collapse-item v-for="line in lines" :key="line.id" :name="line.id">
      <story-line-view :modelValue="line"></story-line-view>
      <template #header>
        <n-space v-if="line.type === 'text'">
          <n-tag type="success">文本节点</n-tag>
          <n-tag v-if="line.narrator !== ''" type="info">{{ line.narrator }}</n-tag>
          <span class="text-preview" v-text="pruneHtml(line.text)"></span>
        </n-space>
        <n-tag v-else type="success">
          {{ '功能节点' }}
        </n-tag>
      </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style>
.n-collapse {
  padding: 12px;
  width: auto;
}
.n-collapse .n-collapse-item {
  padding: 12px;
  transition: background-color 0.3s;
}
.n-collapse-item--active {
  border-radius: 12px;
  background-color: black;
}

.list-operations {
  position: sticky;
  top: 0;
  z-index: 1;
}
.text-preview {
  line-height: 2em;
}
</style>
