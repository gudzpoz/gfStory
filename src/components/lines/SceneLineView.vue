<script setup lang="ts">
import {
  NForm, NFormItem, NRadioButton, NRadioGroup,
  NTooltip,
} from 'naive-ui';

import MediaSelector from '../media/MediaSelector.vue';
import { type SceneLine } from '../../types/lines';

const props = defineProps<{
  modelValue: SceneLine,
}>();

if (!props.modelValue.scene) {
  // eslint-disable-next-line vue/no-mutating-props
  props.modelValue.scene = 'background';
  // eslint-disable-next-line vue/no-mutating-props
  props.modelValue.style = 'width';
}
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-form>
    <n-form-item label="类型" path="scene">
      <n-radio-group :value="modelValue.scene" @update:value="(v) => modelValue.scene = v">
        <n-radio-button value="background">背景图片</n-radio-button>
        <n-radio-button value="audio">背景音乐</n-radio-button>
        <n-radio-button value="se">音效</n-radio-button>
      </n-radio-group>
    </n-form-item>
    <n-form-item v-if="modelValue.scene === 'background'" label="显示方式" path="style">
      <n-radio-group :value="modelValue.style" @update:value="(v) => modelValue.style = v">
        <n-radio-button value="cover">
          <n-tooltip trigger="hover">
            <template #trigger>
              <n-button>图片填满页面</n-button>
            </template>
            可能无法完整显示图片
          </n-tooltip>
        </n-radio-button>
        <n-radio-button value="contain">
          <n-tooltip trigger="hover">
            <template #trigger>
              <n-button>图片完整显示</n-button>
            </template>
            可能有黑边
          </n-tooltip>
        </n-radio-button>
      </n-radio-group>
    </n-form-item>
    <n-form-item label="媒体文件" path="media">
      <media-selector :type="modelValue.scene === 'se' ? 'audio' : modelValue.scene"
        :modelValue="modelValue.media" @update:model-value="(v) => modelValue.media = v">
      </media-selector>
    </n-form-item>
  </n-form>
</template>
