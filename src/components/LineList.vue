<script setup lang="ts">
import {
  NButton, NButtonGroup, NCard, NCollapse,
  NCollapseItem, NIcon, NModal, NMenu,
  NSpace, NTag, NUpload, useDialog,
  type MenuOption, type UploadCustomRequestOptions,
} from 'naive-ui';
import {
  AddFilled, ContentPasteFilled, DeleteFilled, DownloadFilled,
  HelpCenterFilled, MoveDownFilled, MoveUpFilled, PeopleFilled,
  RefreshFilled, UploadFilled,
} from '@vicons/material';
import {
  computed, h, provide, ref,
} from 'vue';

import CharacterList from './character/CharacterList.vue';
import StoryLineView from './lines/StoryLineView.vue';
import StoryList from './StoryList.vue';
import {
  defaultLine, nextId, type GfStory, type TextLine,
} from '../types/lines';
import { labelCharactersWithIds, type Character } from '../types/character';
import { importMarkdownString } from '../story/compiler';
import { db } from '../db/media';

const props = defineProps<{
  modelValue: GfStory,
}>();
const characters = ref(props.modelValue.characters);
const lines = ref(props.modelValue.lines);

provide('characters', computed(() => labelCharactersWithIds(characters.value)));
provide('narrators', computed(() => {
  const narrators = lines.value
    .filter((line) => line.type === 'text' && line.narrator !== '')
    .map((line) => (line as TextLine).narrator);
  return ['', ...new Set(narrators)]
    .map((narrator) => ({
      label: narrator,
      value: narrator,
    }));
}));

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  'update:modelValue': [value: GfStory],
  'export': [type: 'json' | 'markdown' | 'zip'],
  'import': [type: 'json' | 'markdown'],
}>();

const shouldShowCharacterList = ref(false);
function showCharacterList() {
  shouldShowCharacterList.value = true;
}

const names = ref<Array<string>>([]);

function findIndexByCurrentName() {
  if (names.value.length === 0) {
    return -1;
  }
  const id = names.value[0];
  return lines.value.findIndex((line) => line.id === id);
}

function removeLine() {
  const i = findIndexByCurrentName();
  if (i !== -1) {
    lines.value.splice(i, 1);
  }
}

function moveUp() {
  const i = findIndexByCurrentName();
  if (i > 0) {
    const upper = lines.value[i - 1];
    lines.value[i - 1] = lines.value[i];
    lines.value[i] = upper;
  }
}

function moveDown() {
  const i = findIndexByCurrentName();
  if (i !== -1 && i + 1 < lines.value.length) {
    const lower = lines.value[i + 1];
    lines.value[i + 1] = lines.value[i];
    lines.value[i] = lower;
  }
}

function appendDefaultLine() {
  const line = defaultLine();
  const ls = lines.value;
  for (let i = ls.length - 1; i >= 0; i -= 1) {
    const last = ls[i];
    if (last.type === 'text') {
      line.sprites = [...last.sprites];
      break;
    }
  }
  lines.value.push(line);
  names.value = [line.id];
}

function copyCurrent() {
  const i = findIndexByCurrentName();
  if (i !== -1) {
    const line = JSON.parse(JSON.stringify(lines.value[i]));
    line.id = nextId();
    lines.value.splice(i + 1, 0, line);
    names.value = [line.id];
  }
}

function pruneHtml(html: string, limit = 10) {
  const container = document.createElement('div');
  container.innerHTML = html;
  const text = container.innerText;
  return text.length > limit ? `${text.substring(0, limit)}...` : text;
}

function canMove(end: number) {
  const i = findIndexByCurrentName();
  return i !== -1 && i !== end;
}

const dialog = useDialog();
function showHelpDialog() {
  dialog.info({
    content: () => h('ol', {
      title: '简单使用说明',
      innerHTML: `
        <li>使用“编辑角色”按钮来创建角色并添加立绘，需要先添加角色才能在对话中使用立绘。</li>
        <li>使用“新增节点”按钮来创建剧情对话，也可以用节点来设置背景图片或是背景音乐。</li>
        <li>使用“暂存并预览”按钮暂存故事，此时在右侧可以预览故事。</li>
        <li>请务必在刷新页面或是退出浏览器之前使用“暂存并预览”按钮，否则改动将不会被保存。</li>
        <li>使用“导出故事”按钮将故事导出为一个压缩包，解压后用浏览器打开里面的网页即可直接运行故事。</li>
        <li>另外，导出的故事应该也可以直接上传到 Itch 上（一个独立游戏发布网站），但我还未测试。</li>
        <li>另外再说一句，建议把 BGM 播放放在第一句文本之后，因为现在大多数浏览器会禁止一打开网页就播放音乐这种行为。</li>
      `,
    }),
  });
}

async function importJson(options: UploadCustomRequestOptions) {
  const { file } = options.file;
  if (!file) {
    return;
  }
  const story: GfStory = JSON.parse(await file.text());
  if (!Array.isArray(story.characters) || !Array.isArray(story.lines)) {
    return;
  }
  if (!story.characters.every((c) => c.id && c.name && Array.isArray(c.sprites)
    && c.sprites.every((s) => s.id && s.name && s.url))) {
    return;
  }
  if (!story.lines.every((l) => l.id && l.type)) {
    return;
  }
  const s = props.modelValue;
  s.characters.splice(0);
  s.characters.push(...story.characters);
  s.lines.splice(0);
  s.lines.push(...story.lines);
  emit('update:modelValue', props.modelValue);
}
async function importMarkdownFile(markdown: string) {
  const parsed = importMarkdownString(markdown);
  if (!parsed) {
    return;
  }
  const s = props.modelValue;
  parsed.lines.forEach((l) => {
    // eslint-disable-next-line no-param-reassign
    l.id = nextId();
  });
  (parsed.characters as Character[]).forEach((c) => {
    // eslint-disable-next-line no-param-reassign
    c.imported = true;
  });
  await db.importResources(parsed.resources);
  s.lines.splice(0);
  s.lines.push(...parsed.lines);
  s.characters.splice(0);
  s.characters.push(...labelCharactersWithIds(parsed.characters as Character[]));
  emit('update:modelValue', props.modelValue);
  lines.value = [];
  lines.value = props.modelValue.lines;
}
async function importMarkdown(options: UploadCustomRequestOptions) {
  const { file } = options.file;
  if (!file) {
    return;
  }
  await importMarkdownFile(await file.text());
}
const showStorySelect = ref(false);
async function importStory(file: string) {
  showStorySelect.value = false;
  const [, path] = file.split('|');
  await importMarkdownFile(await fetch(`/stories/${path}`).then((res) => res.text()));
}
const ioOptions: MenuOption[] = [
  {
    title: '导出',
    icon: () => h(DownloadFilled),
    key: 'export',
    children: [
      { title: '导出为 JSON', key: 'json' },
      { title: '导出为 Markdown', key: 'markdown' },
      { title: '导出为完整压缩包', key: 'zip' },
    ],
  },
  {
    title: '导入',
    icon: () => h(UploadFilled),
    key: 'import',
    children: [
      {
        title: () => h(NUpload, {
          customRequest: importJson,
          accept: 'application/json',
        }, { default: () => '导入 JSON（实验性）' }),
        key: 'import-json',
      },
      {
        title: () => h(NUpload, {
          customRequest: importMarkdown,
          accept: 'text/plain',
        }, { default: () => '尝试导入 Markdown（更加实验性）' }),
        key: 'import-markdown',
      },
      {
        title: '尝试导入剧情模拟器 Markdown（更加实验性）',
        key: 'import-simulator',
      },
    ],
  },
];
function doIo(v: string) {
  switch (v) {
    case 'json':
    case 'markdown':
    case 'zip':
      emit('update:modelValue', props.modelValue);
      emit('export', v);
      break;
    case 'import-simulator':
      showStorySelect.value = true;
      break;
    default:
      break;
  }
}
</script>

<template>
  <character-list v-model:show="shouldShowCharacterList" :modelValue="characters"
    @update:modelValue="(v) => characters = v"
  >
  </character-list>
  <n-modal v-model:show="showStorySelect" preset="card">
    <story-list value="" @update:value="importStory"></story-list>
  </n-modal>
  <n-card class="list-operations">
    <n-space :wrap="false" justify="start" style="width: fit-content;">
      <n-button-group>
        <n-button @click="showCharacterList" type="warning">
          <n-icon><people-filled></people-filled></n-icon>编辑角色
        </n-button>
        <n-button @click="appendDefaultLine" type="primary">
          <n-icon><add-filled></add-filled></n-icon>添加节点
        </n-button>
        <n-button @click="copyCurrent" type="warning" :disabled="!canMove(-1)"
          title="复制节点"
        >
          <n-icon><content-paste-filled></content-paste-filled></n-icon>
        </n-button>
        <n-button @click="removeLine" type="error" :disabled="!canMove(-1)"
          title="移除当前"
        >
          <n-icon><delete-filled></delete-filled></n-icon>
        </n-button>
        <n-button @click="moveUp" secondary type="primary" :disabled="!canMove(0)"
          title="上移"
        >
          <n-icon><move-up-filled></move-up-filled></n-icon>
        </n-button>
        <n-button @click="moveDown" secondary type="primary" :disabled="!canMove(lines.length - 1)"
          title="下移"
        >
          <n-icon><move-down-filled></move-down-filled></n-icon>
        </n-button>
        <n-button @click="emit('update:modelValue', modelValue)" type="warning">
          <n-icon><refresh-filled></refresh-filled></n-icon>暂存并预览
        </n-button>
        <n-button @click="showHelpDialog" type="info" title="帮助">
          <n-icon><help-center-filled></help-center-filled></n-icon>
        </n-button>
      </n-button-group>
      <n-menu @update:value="doIo" mode="horizontal" :options="ioOptions"></n-menu>
    </n-space>
  </n-card>
  <n-collapse display-directive="if" accordion v-model:expanded-names="names">
    <n-collapse-item v-for="line in lines" :key="line.id" :name="line.id">
      <story-line-view :modelValue="line"></story-line-view>
      <template #header>
        <n-space v-if="line.type === 'text'">
          <n-tag type="success">文本节点</n-tag>
          <n-tag v-if="line.narrator !== ''" type="info">{{ line.narrator }}</n-tag>
          <span class="text-preview" v-text="pruneHtml(line.text)"></span>
        </n-space>
        <n-space v-else>
          <n-tag type="success">
            {{ '功能节点' }}
          </n-tag>
          <n-tag type="warning">{{ line.scene === 'background' ? '背景图' : '背景音乐' }}</n-tag>
          <span class="text-preview">{{ line.media }}</span>
        </n-space>
      </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style>
.n-collapse {
  width: auto;
}
.n-collapse .n-collapse-item {
  --n-title-padding: 0;
  padding: 12px 12px 0 12px;
  transition: background-color 0.3s;
}
.n-collapse-item--active {
  border-radius: 12px;
  background-color: black;
}

.list-operations {
  position: sticky;
  overflow-x: auto;
  top: 0;
  z-index: 1;
}
.text-preview {
  line-height: 2em;
}
</style>
