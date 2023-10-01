<script setup lang="ts">
import {
  onMounted, reactive, ref, watch,
} from 'vue';

// eslint-disable-next-line import/no-unresolved
import circleSvg from '../assets/circle.svg?raw';
// eslint-disable-next-line import/no-unresolved
import gfSystemSvg from '../assets/G.F.system.svg?raw';

import type { CharacterSprite } from '../types/character';

const props = defineProps<{
  backgroundUrl: string,
  backgroundStyle: 'auto' | 'width',
  narratorHtml: string,
  sprites: CharacterSprite[],
  textHtml: string,
  textHeight?: string,
}>();

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'click'): void,
}>();

let clickX = 0;
let clickY = 0;
function setDownPosition(event: MouseEvent) {
  clickX = event.clientX;
  clickY = event.clientY;
}
function emitClick(event: MouseEvent) {
  const dx = clickX - event.clientX;
  const dy = clickY - event.clientY;
  const distance = dx * dx + dy * dy;
  if (distance < 9) {
    emit('click');
  }
}

const backgroundSpace = ref<HTMLDivElement>();
const background = ref<HTMLImageElement>();
const width = ref('');
const height = ref('');
function rescaleImage() {
  const div = backgroundSpace.value!;
  const image = background.value!;
  const ratio = image.naturalWidth / image.naturalHeight;
  let w = div.clientWidth;
  let h = w / ratio;
  if (props.backgroundStyle === 'auto' && h > div.clientHeight) {
    h = div.clientHeight;
    w = h * ratio;
  }
  width.value = `${w}px`;
  height.value = `${h}px`;
}
onMounted(() => {
  background.value!.onload = rescaleImage;
});

interface Sprite extends CharacterSprite {
  left: number;
  opacity: number;
}

const spritesOnStage = ref<Sprite[]>([]);
let removingHandle: ReturnType<typeof setTimeout> | null = null;
watch(() => props.sprites, (sprites) => {
  if (removingHandle) {
    clearTimeout(removingHandle);
  }
  const stillOnStage = new Set(sprites.map((s) => s.id));
  spritesOnStage.value.filter((s) => !stillOnStage.has(s.id))
    // eslint-disable-next-line no-param-reassign
    .forEach((s) => { s.left -= 20; s.opacity = 0; });
  removingHandle = setTimeout(() => {
    spritesOnStage.value = spritesOnStage.value.filter((s) => stillOnStage.has(s.id));
    removingHandle = null;
  }, 200);

  const div = backgroundSpace.value!;
  const unit = div.clientWidth / sprites.length / 2;

  sprites.forEach((sprite, i) => {
    const left = (2 * i + 1) * unit;
    const existing = spritesOnStage.value.find((s) => s.id === sprite.id);
    if (existing) {
      existing.left = left;
      existing.opacity = 1;
    } else {
      const item: Sprite = reactive({
        left: left - 20,
        opacity: 0,
        ...sprite,
      });
      spritesOnStage.value.push(item);
      setTimeout(() => {
        item.left = left;
        item.opacity = 1;
      }, 16);
    }
  });
});
</script>

<template>
  <div class="story-background">
    <img v-show="backgroundUrl"
      ref="background"
      :src="backgroundUrl" :style="{ width, height }" />
    <div ref="backgroundSpace" class="story"
      @click="emitClick"
      @mousedown="setDownPosition"
    >
      <div class="sprites">
        <div class="sprite" v-for="sprite in spritesOnStage" :key="sprite.id"
          :style="{ left: `${sprite.left}px`, opacity: sprite.opacity }"
        >
          <img :src="sprite.url" />
        </div>
      </div>
      <div class="dialog">
        <div class="narrator-box">
          <div class="narrator" v-html="narratorHtml"></div>
          <div class="narrator-corner"></div>
        </div>
        <div class="text" :style="{ height: textHeight ?? '6em' }" v-html="textHtml"></div>
        <div class="corner">
          <span class="loaded-circle" v-html="circleSvg" />
          <span v-html="gfSystemSvg" />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap');

.story-background, .story {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.story-background > img {
  position: absolute;
  margin: auto;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
}

.story {
  filter: drop-shadow(1px 1px 3px black);
}

.sprites .sprite {
  transition: all 0.2s;
  position: absolute;
  width: 100%;
  height: 100%;
  margin: auto;
  display: flex;
  justify-content: center;
  transform: translate(-50%, 0);
}
.sprites .sprite img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.dialog {
  position: absolute;
  bottom: 0;
  min-width: 300px;
  min-height: 7em;
  margin: 1em;
  width: calc(100% - 2em);

  border: 1.5px solid #cccc;
  box-shadow: inset 0 0 1px black;
  background-image: radial-gradient(#cccc 0, #0006 0.6px);
  background-size: 4px 4px;
  clip-path: polygon(0 0, 0 100%, 100% 100%, 100% 18px, 258px 18px, 240px 0);

  font-family: 'Noto Sans SC', sans-serif;
  color: white;
}
.dialog .corner {
  position: absolute;
  right: 0;
  bottom: 0;
  padding: 0 7px 0 0;
}

.dialog .text {
  font-size: 1.1em;
  margin: 0.5em 1.2em 1.2em 1.2em;
  word-wrap: break-word;
  overflow-y: scroll;
}
.dialog .text p {
  margin: 0;
}

.loaded-circle svg {
  display: block;
  margin-left: auto;
  margin-right: 6px;
  width: 12px;
  height: 12px;
}

.narrator-box {
  height: 24px;
}
.narrator-box .narrator {
  display: inline-block;
  height: 24px;
  vertical-align: top;
}
.narrator-box .narrator span {
  font-size: 1.2em;
  margin-left: 1em;
}
.narrator-box .narrator-corner {
  display: inline-block;
  position: absolute;
  top: 0;
  right: 0;
  height: 24px;
  width: calc(100% - 238px);
  background: linear-gradient(0.25turn, #cccc 0, #cccc 18px, #fdb300c0 19px);
  clip-path: polygon(0 0, 25px 25px, 100% 25px, 100% 0);
  box-shadow: 0 0 2px black;
}
</style>
