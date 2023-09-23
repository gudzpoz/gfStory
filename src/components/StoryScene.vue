<script setup lang="ts">
import { defineEmits, onMounted, ref } from 'vue';

import circleSvg from '../assets/circle.svg';
import gfSystemSvg from '../assets/G.F.system.svg';

defineProps<{
  backgroundUrl: string,
  narratorHtml: string,
  sprites: string[],
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
  if (h > div.clientHeight) {
    h = div.clientHeight;
    w = h * ratio;
  }
  width.value = `${w}px`;
  height.value = `${h}px`;
}
onMounted(() => {
  background.value!.onload = rescaleImage;
});
</script>

<template>
  <div ref="backgroundSpace" class="story"
    @click="emitClick"
    @mousedown="setDownPosition"
  >
    <img v-show="backgroundUrl"
      ref="background" class="story-background"
      :src="backgroundUrl" :style="{ width, height }" />
    <div class="dialog">
      <div class="narrator-box">
        <div class="narrator" v-html="narratorHtml"></div>
        <div class="narrator-corner"></div>
      </div>
      <div class="text" :style="{ height: textHeight ?? '6em' }" v-html="textHtml"></div>
      <div class="corner">
        <img class="loaded-circle" :src="circleSvg" />
        <img :src="gfSystemSvg" />
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap');

.story {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: black;
}

.dialog {
  position: absolute;
  bottom: 0;
  min-width: 300px;
  min-height: 7em;
  margin: 1em;
  width: calc(100% - 2em);

  box-shadow: inset 0 0 1px gray;
  background-image: radial-gradient(#555c 0, #111c 1px);
  background-size: 5px 5px;
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

.loaded-circle {
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
  width: 240px;
  vertical-align: top;
}
.narrator-box .narrator span {
  font-size: 1.2em;
  margin-left: 1em;
}
.narrator-box .narrator-corner {
  display: inline-block;
  height: 24px;
  width: calc(100% - 240px);
  background: linear-gradient(0.25turn, gray 0, gray 18px, #fdb300c0 18px);
  box-shadow: 0 0 1px gray;
  clip-path: polygon(0 0, 25px 25px, 100% 25px, 100% 0);
}

img.story-background {
  position: absolute;
  margin: auto;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
}
</style>
