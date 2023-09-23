<script setup lang="ts">
import {
  NColorPicker, NForm, NFormItem, NSelect,
} from 'naive-ui';
import { inject, ref, type Ref } from 'vue';

import SpriteSelector from './SpriteSelector.vue';
import ClassicEditor from './editor';
import { type TextLine } from '../../types/lines';

const props = defineProps<{
  modelValue: TextLine,
}>();
const narrators = inject<Ref<{ value: string }[]>>('narrators')!;

const color = ref(props.modelValue.narratorColor);
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-form inline :modelValue="modelValue" style="flex-wrap: wrap">
    <n-form-item label="名称显示" path="narrator" class="narrator">
      <n-select
        :value="modelValue.narrator"
        @update:value="(v) => modelValue.narrator = v ?? ''"
        :style="{ '--narrator-text-color': color }"
        :options="narrators"
        clearable
        filterable
        tag
      ></n-select>
    </n-form-item>
    <n-form-item label="名称颜色" path="narratorColor">
      <n-color-picker
        :value="modelValue.narratorColor"
        :modes="['hex']"
        @update:value="(v) => color = modelValue.narratorColor = v"
      ></n-color-picker>
    </n-form-item>
    <n-form-item label="立绘" path="tachie">
      <sprite-selector :modelValue="modelValue.sprites"></sprite-selector>
    </n-form-item>
    <n-form-item class="n-ck-editor" label="文字内容">
      <ckeditor :editor="ClassicEditor"
        :modelValue="modelValue.text"
        @update:modelValue="(v) => modelValue.text = v"
      ></ckeditor>
    </n-form-item>
  </n-form>
</template>

<style>
@import './editor.css';

.n-form {
  flex-wrap: wrap;
}
.n-ck-editor {
  flex-basis: 100%;
}
.ck-editor {
  max-width: 100%;
}

.n-form .narrator .n-base-selection .n-base-selection-label .n-base-selection-overlay {
  color: var(--narrator-text-color, var(--n-text-color));
}
</style>
