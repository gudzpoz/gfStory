<script setup lang="ts">
import { NCheckbox, NForm, NFormItem } from 'naive-ui';

import { type SceneLine } from '../../types/lines';

defineProps<{
  modelValue: SceneLine,
}>();
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-form>
    <n-form-item label="Control" path="noSkipping">
      <n-checkbox
        :checked="modelValue.noSkipping"
        @update:checked="(v) => modelValue.noSkipping = v"
      >
        Stop Skipping
      </n-checkbox>
    </n-form-item>
  </n-form>
</template>
