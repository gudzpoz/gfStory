<script setup lang="ts">
import {
  darkTheme, NConfigProvider, NLayout, NLayoutContent, NLayoutSider,
} from 'naive-ui';
import { ref } from 'vue';

import LineList from './components/LineList.vue';
import { type Line, defaultLine } from './types/lines';

const story = ref<Array<Line>>([defaultLine()]);
</script>

<template>
  <n-config-provider :theme="darkTheme">
    <n-layout has-sider sider-placement="right" style="height: 100vh">
      <n-layout-content>
        <line-list v-model="story"></line-list>
      </n-layout-content>
      <n-layout-sider show-trigger="arrow-circle">
      </n-layout-sider>
    </n-layout>
  </n-config-provider>
</template>

<style scoped></style>
