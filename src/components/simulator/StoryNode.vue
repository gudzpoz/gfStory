<script setup lang="ts">
import { NIcon } from 'naive-ui';
import { Handle, Position } from '@vue-flow/core';
import { computed } from 'vue';

// eslint-disable-next-line import/no-unresolved
import circSvg from '../../assets/map-circ.svg?raw';
// eslint-disable-next-line import/no-unresolved
import starSvg from '../../assets/map-star.svg?raw';
// eslint-disable-next-line import/no-unresolved
import squareSvg from '../../assets/map-square.svg?raw';

const props = defineProps<{
  data: {
    type?: 'circ' | 'star' | 'square',
    label: string,
    group?: number;
  },
}>();
const svg = computed(() => {
  switch (props.data.type) {
    case 'circ':
      return circSvg;
    case 'star':
      return starSvg;
    default:
      return squareSvg;
  }
});
const color = computed(() => `#${(props.data.group ?? 0).toString(16).repeat(3)}`);
</script>
<template>
  <div class="story-node" :style="{ backgroundColor: color }">
    <handle type="target" :position="Position.Left" />
    <n-icon size="20"><span v-html="svg"></span></n-icon>
    <span class="label">{{ data.label }}</span>
    <handle type="source" :position="Position.Right" />
  </div>
</template>
<style>
.story-node {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.story-node > * {
  display: block;
}
.story-node > .label {
  margin-left: 5px;
}
</style>
