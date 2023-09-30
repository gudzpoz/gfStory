<script setup lang="ts">
import {
  NButton, NIcon, NList, NSpace,
} from 'naive-ui';
import { AddFilled, DeleteFilled } from '@vicons/material';

import MediaSelector from '../media/MediaSelector.vue';

defineProps<{
  modelValue: string[],
}>();
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-list bordered>
    <n-space class="sprite-item" align="center" v-for="media, i in modelValue" :key="i">
      <media-selector type="sprite"
        :modelValue="media"
        @update:modelValue="(v) => modelValue[i] = v">
      </media-selector>
      <n-button @click="modelValue.splice(i, 1)">
        <n-icon><delete-filled></delete-filled></n-icon>
      </n-button>

    </n-space>
    <template #footer>
      <n-button @click="modelValue.push('')">
        <n-icon><add-filled></add-filled></n-icon>添加
      </n-button>
    </template>
  </n-list>
</template>

<style>
.sprite-item {
  margin: 0.2em;
}
</style>
