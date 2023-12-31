<script setup lang="ts">
import { saveAs } from 'file-saver';
import JSZip from 'jszip';
import {
  darkTheme, zhCN,
  NConfigProvider, NDialogProvider,
  NLayout, NLayoutContent, NLayoutSider,
  NNotificationProvider,
} from 'naive-ui';
import { ref } from 'vue';

import LineList from './components/lines/LineList.vue';
import StoryTeller from './components/viewer/StoryTeller.vue';
import {
  defaultLine, initUniqueId, type GfStory,
} from './types/lines';
import { compileMarkdown, linesToMarkdown } from './story/compiler';
import { db } from './db/media';

const chunk = ref('');

function loadStorageOrDefault(): GfStory {
  const saved = localStorage.getItem('story');
  if (saved) {
    const parsed = JSON.parse(saved);
    if (!(parsed instanceof Array)) {
      return parsed as GfStory;
    }
  }
  return {
    characters: [],
    lines: [defaultLine()],
  };
}
const story = loadStorageOrDefault();
initUniqueId(story);

async function updateStory(s: GfStory) {
  /*
   * "story" and "s" should actually be the same object.
   * We are doing the following... for fun.
   */
  story.characters = s.characters;
  story.lines = s.lines;
  chunk.value = await compileMarkdown(await linesToMarkdown(story));
  localStorage.setItem('story', JSON.stringify(story));
}

async function exportMarkdown() {
  saveAs(new Blob([await linesToMarkdown(story, async (s) => {
    if (s.includes(':')) {
      return db.toDataUrl(s);
    }
    return new URL(s, document.baseURI).href;
  })], {
    type: 'text/markdown',
  }), 'story.md');
}

async function exportJson() {
  saveAs(new Blob([JSON.stringify(story)], {
    type: 'application/json',
  }), 'story.json');
}

async function exportStory(format: string) {
  if (format === 'markdown') {
    await exportMarkdown();
    return;
  }
  if (format === 'json') {
    exportJson();
    return;
  }

  const root = new JSZip();
  const zip = root.folder('story');
  if (!zip) {
    throw new Error('zip error');
  }
  const compiled = await compileMarkdown(await linesToMarkdown(story, async (s) => {
    if (!s.includes(':')) {
      return new URL(s, document.baseURI).href;
    }
    const [type, name] = db.splitMediaUrl(s);
    if (!type) {
      return s;
    }
    const directory = zip.folder(type);
    if (!directory) {
      throw new Error('unable to write to zip');
    }
    if (!directory.file(name)) {
      const file = await db.findRawMediaByName(type, name);
      if (!file) {
        throw new Error('no such media found');
      }
      if (typeof file.blob === 'string') {
        if (file.blob.startsWith('/')) {
          return new URL(file.blob, document.baseURI).href;
        }
        return file.blob;
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
    <n-dialog-provider>
      <n-notification-provider>
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
      </n-notification-provider>
    </n-dialog-provider>
  </n-config-provider>
</template>

<style>
#app .n-layout-sider .n-layout-toggle-button {
  z-index: 3;
}
</style>
