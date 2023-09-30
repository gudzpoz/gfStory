<script setup lang="ts">
import {
  NAvatar, NButton, NIcon, NIconWrapper, NImage, NPopover, NSpace,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import {
  CloseFilled, PlayArrowFilled, PauseFilled, QuestionMarkFilled,
} from '@vicons/material';

import 'vue-advanced-cropper/dist/style.css';

import { db, type MediaUrl } from '../../db/media';

const props = defineProps<{
  wide?: boolean,
  removable?: boolean,
  url: MediaUrl,
}>();

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'remove'): void,
}>();

const dataUrl = ref('');
const updateDataUrl = () => {
  if (props.url !== '') {
    db.toDataUrl(props.url).then((s) => {
      dataUrl.value = s;
    });
  } else {
    dataUrl.value = '';
  }
};
watch(() => props.url, updateDataUrl);
updateDataUrl();

const playing = ref(false);
const name = computed(() => db.splitMediaUrl(props.url)[1]);
const type = computed(() => db.splitMediaUrl(props.url)[0]);

const player = ref<HTMLAudioElement>();
function play(state: boolean) {
  playing.value = state;
  if (player.value) {
    player.value.pause();
    player.value = undefined;
  }
  if (state) {
    player.value = new Audio(dataUrl.value);
    player.value.play();
  }
}
</script>

<template>
  <n-space align="center" class="media-item" :wrap="false">
    <n-button type="error" size="tiny"
      @click.stop="emit('remove')" v-if="wide && removable !== false"
    >
      <n-icon><close-filled></close-filled></n-icon>
    </n-button>
    <n-icon-wrapper v-if="type === 'audio'" class="n-avatar"
      @mouseenter="play(true)" @mouseleave="play(false)"
    >
      <n-icon>
        <pause-filled v-show="playing"></pause-filled>
        <play-arrow-filled v-show="!playing"></play-arrow-filled>
      </n-icon>
    </n-icon-wrapper>
    <n-icon-wrapper v-else-if="!dataUrl || dataUrl === ''" class="n-avatar"
      color="grey"
      :size="35"
    >
      <n-icon>
        <question-mark-filled></question-mark-filled>
      </n-icon>
    </n-icon-wrapper>
    <n-popover v-else trigger="hover">
      <n-image :src="dataUrl" width="200"></n-image>
      <template #trigger>
        <n-avatar :src="dataUrl"></n-avatar>
      </template>
    </n-popover>
    <span v-if="wide">{{ name }}</span>
  </n-space>
</template>

<style>
.n-space.media-item .n-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0.2em;
  width: 35px;
  height: 35px;
  pointer-events: all;
}
.n-space.media-item .n-avatar img {
  width: fit-content;
  height: fit-content;
  max-width: 35px;
  max-height: 35px;
  object-fit: cover;
}
.n-select .n-space.media-item .n-button {
  display: none;
}
</style>
