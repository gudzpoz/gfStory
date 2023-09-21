<script setup lang="ts">
import {
  NColorPicker, NForm, NFormItem, NSelect,
} from 'naive-ui';

import { type TextLine } from '../../types/lines';

defineProps<{
  modelValue: TextLine,
}>();
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-form inline :modelValue="modelValue">
    <n-form-item label="Narrator" path="narrator">
      <n-select
        :value="modelValue.narrator"
        @update:value="(v) => modelValue.narrator = v"
        filterable
        tag
      ></n-select>
    </n-form-item>
    <n-form-item label="Narrator Color" path="narratorColor">
      <n-color-picker
        :value="modelValue.narratorColor"
        :modes="['hex']"
        @update:value="(v) => modelValue.narratorColor = v"
      ></n-color-picker>
    </n-form-item>
  </n-form>
</template>
