<script setup lang="ts">
import {
  NButton, NCard, NIcon,
  NSpace,
} from 'naive-ui';
import { ref } from 'vue';
import {
  AddFilled,
  MoveUpFilled, MoveDownFilled, RemoveFilled,
} from '@vicons/material';

import CharacterSelector from './CharacterSelector.vue';
import type { Character } from '../../types/character';

const props = defineProps<{
  modelValue: string[],
  remote: Record<string, boolean>,
  characters: Character[],
}>();
const selected = ref<string[]>(props.modelValue);

function exchange(i: number, j: number) {
  const arr = selected.value;
  if (i >= 0 && i < j && j < arr.length) {
    const item = arr[i];
    arr[i] = arr[j];
    arr[j] = item;
  }
}
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-card>
    <n-space vertical>
      <n-space v-for="sprite, i in selected" :key="sprite">
        <character-selector :modelValue="sprite" :characters="characters"
          :remoteRecord="remote" @update:modelValue="(v) => modelValue[i] = v"
        >
        </character-selector>
        <n-button @click="exchange(i - 1, i)">
          <n-icon><move-up-filled></move-up-filled></n-icon>
        </n-button>
        <n-button @click="exchange(i, i + 1)">
          <n-icon><move-down-filled></move-down-filled></n-icon>
        </n-button>
        <n-button @click="selected.splice(i, 1)">
          <n-icon><remove-filled></remove-filled></n-icon>
        </n-button>
      </n-space>
      <n-button @click="selected.push('')">
          <n-icon><add-filled></add-filled></n-icon>
      </n-button>
    </n-space>
  </n-card>
</template>
