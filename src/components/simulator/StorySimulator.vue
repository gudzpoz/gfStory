<script setup lang="ts">
import {
  NConfigProvider,
  NDrawer, NDrawerContent,
  NModalProvider,
  darkTheme, zhCN,
  type MenuInst,
} from 'naive-ui';
import {
  onMounted, ref, watch,
} from 'vue';

import StoryList from './StoryList.vue';
import StoryTeller from '../viewer/StoryTeller.vue';
import { compileMarkdown } from '../../story/compiler';
import {
  STORY_PATH_PREFIX,
} from '../../types/assets';

const chunk = ref('');
const loading = ref(false);
async function switchStory(path: string) {
  loading.value = true;
  try {
    const markdown = await fetch(path).then((res) => res.text());
    chunk.value = await compileMarkdown(markdown);
    loading.value = false;
  } catch (e) {
    loading.value = false;
  }
}

const showMenu = ref(false);

const value = ref('');
const menu = ref<MenuInst>();
watch(() => value.value, (file) => {
  menu.value?.showOption(file);
  const url = new URL(window.location.toString());
  if (url.searchParams.get('story') !== file) {
    url.searchParams.set('story', file);
    window.history.pushState({}, '', url);
  }
  showMenu.value = false;
  switchStory(`${STORY_PATH_PREFIX}${file}`);
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
</script>

<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN">
    <n-modal-provider>
      <n-drawer v-model:show="showMenu" :width="Math.min(width * 0.8, 400)" placement="left"
        display-directive="show"
      >
        <n-drawer-content title="剧情选择" :native-scrollbar="false">
          <story-list v-model:value="value" set-title-when-selected />
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
      <story-teller menu-button @menu="showMenu = true" :chunk="chunk" :loading="loading">
      </story-teller>
    </n-modal-provider>
  </n-config-provider>
</template>

<style>
#app, .story-background {
  height: 100vh;
}
.story-heading {
  font-weight: bold;
  margin-right: 1em;
}
.n-drawer a {
  color: #63e2b7;
}
</style>
