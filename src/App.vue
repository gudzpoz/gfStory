<script setup lang="ts">
import { saveAs } from 'file-saver';
import JSZip from 'jszip';
import {
  darkTheme, zhCN,
  NConfigProvider, NLayout, NLayoutContent, NLayoutSider,
} from 'naive-ui';
import { ref } from 'vue';

import LineList from './components/LineList.vue';
import StoryTeller from './components/StoryTeller.vue';
import { type Line, defaultLine } from './types/lines';
import { compileMarkdown, linesToMarkdown } from './story/compiler';
import { db, MEDIA_TYPES } from './db/media';

const chunk = ref('');

function loadStorageOrDefault() {
  const saved = localStorage.getItem('story');
  if (saved) {
    const parsed = JSON.parse(saved);
    if (parsed instanceof Array) {
      return parsed as Line[];
    }
  }
  return [defaultLine()];
}
let story: Line[] = loadStorageOrDefault();

async function updateStory(s: Line[]) {
  story = s;
  chunk.value = await compileMarkdown(await linesToMarkdown(s));
  localStorage.setItem('story', JSON.stringify(s));
}

async function exportStory() {
  const root = new JSZip();
  const zip = root.folder('story');
  if (!zip) {
    throw new Error('zip error');
  }
  const compiled = await compileMarkdown(await linesToMarkdown(story, async (s) => {
    const [type, name] = s.split(':', 2);
    const directory = zip.folder(type);
    if (!directory) {
      throw new Error('unable to write to zip');
    }
    if (!directory.file(name)) {
      const file = await db[type as typeof MEDIA_TYPES[number]].where('name').equals(name).first();
      if (!file) {
        throw new Error('no such media found');
      }
      directory.file(name, file.blob);
    }
    return `./${type}/${name}`;
  }));
  const viewer = await fetch('./viewer.html').then((res) => res.text());
  // Using <(slash)script> directly will cause problems...
  const tag = 'script';
  zip.file(
    'viewer.html',
    viewer.replace(
      '<!-- LUA_INJECTION_POINT -->',
      `<script type="application/lua">${compiled}</${tag}>`,
    ),
  );
  saveAs(await root.generateAsync({ type: 'blob' }), 'story.zip');
}
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN">
    <n-layout has-sider sider-placement="right" style="height: 100vh">
      <n-layout-content>
        <line-list :modelValue="story"
          @update:modelValue="updateStory"
          @export="exportStory"
        >
        </line-list>
      </n-layout-content>
      <n-layout-sider show-trigger="arrow-circle" width="500px" bordered>
        <story-teller :chunk="chunk"></story-teller>
      </n-layout-sider>
    </n-layout>
  </n-config-provider>
</template>

<style scoped></style>
