<script setup lang="ts">
import { NTabs, NTabPane } from 'naive-ui';

import OptionLineView from './OptionLineView.vue';
import SceneLineView from './SceneLineView.vue';
import TextLineView from './TextLineView.vue';
import type {
  Line, OptionLine, SceneLine, TextLine,
} from '../../types/lines';

defineProps<{
  modelValue: Line,
}>();
</script>

<template>
  <!-- eslint-disable-next-line vue/no-mutating-props -->
  <n-tabs :value="modelValue.type" @update:value="(v) => modelValue.type = v">
    <n-tab-pane name="text" tab="文本内容">
      <text-line-view :modelValue="(modelValue as TextLine)"></text-line-view>
    </n-tab-pane>
    <n-tab-pane name="scene" tab="场景">
      <scene-line-view :modelValue="(modelValue as SceneLine)"></scene-line-view>
    </n-tab-pane>
    <n-tab-pane name="option" tab="选项">
      <option-line-view :modelValue="(modelValue as OptionLine)"></option-line-view>
    </n-tab-pane>
  </n-tabs>
</template>
