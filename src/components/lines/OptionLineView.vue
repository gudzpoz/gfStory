<script setup lang="ts">
import { NDynamicInput, NForm, NFormItem } from 'naive-ui';
import { ref, watch } from 'vue';

import type { OptionLine } from '../../types/lines';

const props = defineProps<{
  modelValue: OptionLine,
}>();
const options = ref(props.modelValue.options);

function fixValue() {
  const value = props.modelValue;
  if (!value.options) {
    value.options = [];
  }
  return value.options;
}
fixValue();

watch(() => options.value, (v) => {
  const current = fixValue();
  current.splice(0);
  current.push(...v.filter((e) => typeof e.key === 'string' && typeof e.value === 'string'));
});
</script>

<template>
  <n-form inline :modelValue="modelValue">
    <n-form-item label="选项" path="options">
      <n-dynamic-input
        v-model:value="options"
        preset="pair"
        key-placeholder="选项名称"
        value-placeholder="选项标识符（暂时没用）"
      />
    </n-form-item>
  </n-form>
</template>
