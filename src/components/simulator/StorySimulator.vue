<script setup lang="ts">
import { micromark } from 'micromark';
import { CheckCircleOutlineFilled, PlayArrowFilled } from '@vicons/material';
import { directive, directiveHtml } from 'micromark-extension-directive';
import {
  NAlert, NButton, NCheckbox, NConfigProvider, NFlex,
  NDrawer, NDrawerContent,
  NModal, NModalProvider,
  darkTheme, zhCN,
  type MenuInst,
} from 'naive-ui';
import {
  computed, onMounted, ref, watch,
} from 'vue';

import StoryList from './StoryList.vue';
import { useReadingProgress } from './progress';
import nextStory from './playback';
import chapterPresets from '../../assets/chapters.json';
import { isStoryId } from '../../db/progress';
import StoryTeller from '../viewer/StoryTeller.vue';
import { compileMarkdown } from '../../story/compiler';
import {
  STORY_PATH_PREFIX,
} from '../../types/assets';

const progress = useReadingProgress();
const {
  read: readStories, recent, ready, error: progressError, busy,
} = progress;
const backupInput = ref<HTMLInputElement>();
const notice = ref('');
async function importBackup(event: Event) {
  notice.value = '';
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file && await progress.importBackup(file)) notice.value = '进度已合并';
  input.value = '';
}
const continuous = ref(false);
const skipRead = ref(false);
const unreadOnly = ref(false);
const autoPlay = ref(false);
const autoSpeed = ref(1);
const finishedFile = ref('');
const savingFinished = ref(false);
const playbackNotice = ref('');
const chapters = Object.values(chapterPresets).flat();
let continuationTarget = '';
const activeFile = ref('');
const loadError = ref('');
const chunk = ref('');
const html = ref('');
const loading = ref(false);
let request = 0;
async function switchStory(file: string) {
  request += 1;
  const current = request;
  activeFile.value = '';
  chunk.value = '';
  html.value = '';
  loading.value = true;
  loadError.value = '';
  try {
    if (!isStoryId(file)) throw new Error('剧情编号无效');
    const response = await fetch(STORY_PATH_PREFIX + file);
    if (!response.ok) throw new Error('剧情加载失败，请重试');
    const markdown = await response.text();
    if (!markdown.trim()) throw new Error('剧情内容为空');
    const compiled = await compileMarkdown(markdown);
    if (current !== request) return;
    html.value = micromark(markdown, {
      allowDangerousHtml: true,
      extensions: [directive()],
      htmlExtensions: [directiveHtml({
        // eslint-disable-next-line func-names
        '*': function (d) {
          this.tag('<span');
          this.tag(` class="${d.name} directive"`);
          this.tag('>');
          this.raw(d.label ?? '');
          this.tag('</span>');
          return true;
        },
      })],
    });
    activeFile.value = file;
    chunk.value = compiled;
    loading.value = false;
    await progress.remember(file);
  } catch (e) {
    if (current !== request) return;
    autoPlay.value = false;
    loadError.value = e instanceof Error ? e.message : '剧情加载失败';
    loading.value = false;
  }
}

const showMenu = ref(false);

const value = ref('');
const currentRead = computed(() => readStories.value.has(activeFile.value));
const nextFile = computed(
  () => nextStory(chapters, activeFile.value, readStories.value, skipRead.value),
);
async function continueStory(manual = false) {
  const file = activeFile.value;
  if (!file || finishedFile.value !== file || value.value !== file || savingFinished.value) return;
  const currentRequest = request;
  savingFinished.value = true;
  const saved = await progress.setRead(file, true);
  if (currentRequest !== request || activeFile.value !== file || value.value !== file) return;
  savingFinished.value = false;
  if (!saved) {
    autoPlay.value = false;
    playbackNotice.value = '进度保存失败，已暂停';
    return;
  }
  if (!manual && !continuous.value) return;
  const next = nextStory(chapters, file, readStories.value, skipRead.value);
  if (!next) {
    autoPlay.value = false;
    playbackNotice.value = skipRead.value ? '本目录没有后续未读剧情' : '已到当前目录末尾';
    return;
  }
  continuationTarget = next;
  value.value = next;
}
async function markEnded(file: string, automatic: boolean) {
  if (file !== activeFile.value || file !== value.value || loading.value) return;
  finishedFile.value = file;
  autoPlay.value = automatic;
  await continueStory();
}
const menu = ref<MenuInst>();
watch(() => value.value, (file) => {
  if (file !== continuationTarget) autoPlay.value = false;
  continuationTarget = '';
  finishedFile.value = '';
  savingFinished.value = false;
  playbackNotice.value = '';
  menu.value?.showOption(file);
  const url = new URL(window.location.toString());
  if (url.searchParams.get('story') !== file) {
    url.searchParams.set('story', file);
    window.history.pushState({}, '', url);
  }
  showMenu.value = false;
  switchStory(file);
});

function updateFromLocation() {
  const search = new URLSearchParams(window.location.search);
  const story = search.get('story');
  if (story && story !== '') {
    value.value = story;
  }
}

// StorySimulator should never get unmounted, so not registering unmount hooks to remove listeners.
const width = ref(window.innerWidth);
onMounted(() => {
  updateFromLocation();
  window.addEventListener('popstate', () => {
    updateFromLocation();
  });
  window.addEventListener('resize', () => {
    width.value = window.innerWidth;
  });
});

const showText = ref(false);
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN">
    <n-modal-provider>
      <n-drawer
        v-model:show="showMenu" :width="Math.min(width * 0.8, 400)"
        placement="left" display-directive="show"
      >
        <n-drawer-content title="剧情选择" :native-scrollbar="false">
          <n-flex vertical style="margin-top: 16px">
            <n-flex>
              <n-checkbox v-model:checked="continuous">连续播放</n-checkbox>
              <n-checkbox v-model:checked="skipRead" :disabled="!ready">跳过已读</n-checkbox>
              <n-checkbox v-model:checked="unreadOnly" :disabled="!ready">只看未读</n-checkbox>
            </n-flex>
            <n-button
              v-if="recent && recent.id !== value"
              :disabled="!ready || busy" @click="value = recent.id"
            >打开最近阅读</n-button>
            <n-flex>
              <n-button :disabled="!ready || busy" @click="progress.exportBackup()">导出进度</n-button>
              <n-button :disabled="!ready || busy" @click="backupInput?.click()">导入进度</n-button>
            </n-flex>
            <input
              ref="backupInput" type="file" accept=".json,application/json" hidden
              @change="importBackup"
            />
            <small>进度保存在当前浏览器；清除网站数据会删除记录。导入会合并已读记录。</small>
            <n-alert v-if="progressError" type="error">{{ progressError }}</n-alert>
            <span v-if="notice" role="status">{{ notice }}</span>
          </n-flex>
          <story-list
            v-model:value="value" set-title-when-selected :read="ready ? readStories : undefined"
            :unread-only="unreadOnly" :progress-busy="busy"
            @set-read="(id, checked) => progress.setRead(id, checked)"
          />
          <slot name="footer" id="footer">
            <p>
              补剧情的顺序可以参考
              <a href="https://nga.178.com/read.php?tid=37662006&rand=406" target="_blank">
                [剧情] [整理] 少女前线云玩家补剧情指北
              </a>。
              剧情模拟器的代码可以在
              <a href="https://github.com/gudzpoz/gfStory" target="_blank">GitHub</a>
              上找到。
              如果遇到了什么问题，欢迎到 GitHub 上提问题或者直接到论坛里的
              <a href="https://gf2-bbs.sunborngame.com/threadInfo?id=4511" target="_blank">
                少女前线一代剧情模拟器发布！（再次）
              </a>
              这个发布贴里面评论提。
            </p>
            <p>
              目前还有部分剧情没有标好对应的标题（主要是一些局内的点位剧情），
              这个我正在慢慢对照着录屏视频以及常驻活动来手动汇总标注，但是进展速度有限……
              （我也会尽量删掉一些只是游玩提示的无剧情内容的点位事件。）
              如果有人知道某些未标注事件的具体关卡和位点，欢迎直接告诉我！
            </p>
          </slot>
        </n-drawer-content>
      </n-drawer>
      <div v-if="!activeFile" class="story-start">
        <div>
          <p v-if="loading" role="status">剧情加载中……</p>
          <n-button @click="showMenu = true">选择剧情</n-button>
        </div>
      </div>
      <n-alert v-if="loadError" type="error" class="story-error">
        {{ loadError }}
        <n-button :disabled="loading" @click="switchStory(value)">重试</n-button>
        <n-button @click="showMenu = true">选择剧情</n-button>
      </n-alert>
      <story-teller
        v-if="activeFile" :key="activeFile"
        menu-button text-button
        v-model:auto-play="autoPlay" v-model:auto-speed="autoSpeed"
        @ended="(automatic) => markEnded(activeFile, automatic)"
        @menu="showMenu = true" @text="showText = true"
        :chunk="chunk"
        :loading="loading"
      >
        <template #navigation>
          <button
            :disabled="!ready || busy || loading || savingFinished"
            :class="{ toggled: currentRead }" :aria-pressed="currentRead"
            :title="currentRead ? '取消已读标记' : '标记当前剧情为已读'"
            @click="progress.setRead(activeFile, !currentRead)"
          ><check-circle-outline-filled></check-circle-outline-filled><span>已读</span></button>
          <button
            v-if="finishedFile === activeFile && nextFile"
            :disabled="savingFinished || loading"
            @click="continueStory(true)"
          ><play-arrow-filled></play-arrow-filled><span>下一段</span></button>
          <span v-if="playbackNotice" role="status">{{ playbackNotice }}</span>
        </template>
      </story-teller>
      <n-modal
        v-model:show="showText" preset="card" size="huge"
        style="max-width: 90vw; max-height: 90vh; overflow-y: auto"
      >
        <div class="plain-text" v-html="html"></div>
      </n-modal>
    </n-modal-provider>
  </n-config-provider>
</template>

<style>
.story-start { display: grid; place-items: center; height: 100vh; }
.story-error { position: fixed; top: 0; left: 0; right: 0; z-index: 2000; }
#app,
.story-background {
  height: 100vh;
}

.story-heading {
  font-weight: bold;
  margin-right: 1em;
}

.n-drawer a {
  color: #63e2b7;
}

.plain-text {
  max-width: 90vw;
}

.plain-text .directive.audio::before {
  content: "背景音乐：";
}
.plain-text .directive.background::before {
  content: "背景: ";
}
.plain-text .directive.se::before {
  content: "音效: ";
}
.plain-text .directive.audio::before,
.plain-text .directive.background::before,
.plain-text .directive.se::before {
  font-style: italic;
}

.plain-text .directive.classes,
.plain-text .directive.color,
.plain-text .directive.remote,
.plain-text .directive.sprites,
.plain-text pre code.language-lua {
  display: none;
}
.plain-text > p {
  margin-left: 2em;
}
.plain-text .directive.narrator:not(:empty) {
  font-size: 1.1em;
  font-weight: bold;
  margin-left: -2em;
  border-left: 2px solid orange;
  padding-left: 0.5em;
}

.plain-text > ul::before {
  content: "选项：";
  font-weight: bold;
  font-style: italic;
  margin-left: -2em;
}

.plain-text p > code {
  font-size: 0.8em;
}
.plain-text p > code:last-child::before {
  content: "跳转至分支：";
  font-weight: bold;
  font-style: italic;
}
.plain-text p > code:first-child:not(:last-child)::before {
  content: "分支：";
  font-weight: bold;
  font-style: italic;
  margin-left: -2em;
}
.plain-text p > code:first-child::after {
  display: block;
  content: "";
}
</style>
