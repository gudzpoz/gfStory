<script setup lang="ts">
import { NButton, NList } from 'naive-ui';

import MediaSelector from './MediaSelector.vue';

defineProps<{
  modelValue: string[],
}>();
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-list>
    <media-selector v-for="media, i in modelValue" :key="i" type="sprite"
      :modelValue="media"
      @update:modelValue="(v) => modelValue[i] = v">
    </media-selector>
  </n-list>
  <n-button @click="modelValue.push('')">添加</n-button>
</template>
