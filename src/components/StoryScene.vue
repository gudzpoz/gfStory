<script setup lang="ts">
import { ref } from 'vue';

import SpriteImageView from './media/SpriteImage.vue';
import type { SpriteImage } from '../story/interpreter';

// eslint-disable-next-line import/no-unresolved
import circleSvg from '../assets/circle.svg?raw';
// eslint-disable-next-line import/no-unresolved
import gfSystemSvg from '../assets/G.F.system.svg?raw';
// eslint-disable-next-line import/no-unresolved
import boxLayerSvg from '../assets/box-layer.svg?raw';

const boxLayerSvgUrl = `url("${
  URL.createObjectURL(new Blob([boxLayerSvg], {
    type: 'image/svg+xml',
  }))
}")`;

const props = defineProps<{
  backgroundUrl: string,
  backgroundStyle: 'contain' | 'cover',
  narratorHtml: string,
  sprites: SpriteImage[],
  remote: Set<string>,
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

function computeCenter(i: number) {
  const div = backgroundSpace.value!;
  const unit = div.clientWidth / props.sprites.length / 2;
  return (2 * i + 1) * unit;
}
</script>

<template>
  <div class="story-background">
    <img v-show="backgroundUrl"
      :src="backgroundUrl"
      :style="{ objectFit: backgroundStyle }"
    />
    <div ref="backgroundSpace" class="story"
      @click="emitClick"
      @mousedown="setDownPosition"
    >
      <transition-group name="sprite" tag="div" class="sprites">
        <sprite-image-view
          v-for="sprite, i in sprites"
          :sprite="sprite"
          :center="computeCenter(i)"
          :container="backgroundSpace!"
          :framed="remote.has(sprite.id)"
          :key="sprite.id"
        >
        </sprite-image-view>
      </transition-group>
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
  width: 100%;
  height: 100%;
}

.story {
  filter: drop-shadow(1px 1px 3px black);
}

.sprites {
  --box-border-image-source: v-bind(boxLayerSvgUrl);
}

.dialog {
  position: absolute;
  bottom: 0;
  min-width: 300px;
  min-height: 7em;
  margin: 1em;
  width: calc(100% - 2em);

  border: 1.5px solid #ccca;
  box-shadow: inset 0 0 1px black;
  background-image: radial-gradient(#ccc8 0, #000a 0.6px);
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
  background: linear-gradient(0.25turn, #ccca 0, #ccca 18px, #fdb300c0 19px);
  clip-path: polygon(0 0, 25px 25px, 100% 25px, 100% 0);
  box-shadow: 0 0 2px black;
}
</style>
