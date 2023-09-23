<script setup lang="ts">
import {
  NCheckbox, NForm, NFormItem, NRadioButton, NRadioGroup,
} from 'naive-ui';

import MediaSelector from './MediaSelector.vue';
import { type SceneLine } from '../../types/lines';

const props = defineProps<{
  modelValue: SceneLine,
}>();

if (!props.modelValue.scene) {
  // eslint-disable-next-line vue/no-mutating-props
  props.modelValue.scene = 'background';
}
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-form>
    <n-form-item label="类型" path="scene">
      <n-radio-group :value="modelValue.scene" @update:value="(v) => modelValue.scene = v">
        <n-radio-button value="background">背景图片</n-radio-button>
      </n-radio-group>
    </n-form-item>
    <n-form-item label="图片" path="image">
      <media-selector :type="modelValue.scene"
        :modelValue="modelValue.image" @update:model-value="(v) => modelValue.image = v">
      </media-selector>
    </n-form-item>
    <n-form-item label="控制" path="noSkipping">
      <n-checkbox
        :checked="modelValue.noSkipping"
        @update:checked="(v) => modelValue.noSkipping = v"
      >
        阻止快进
      </n-checkbox>
    </n-form-item>
  </n-form>
</template>
