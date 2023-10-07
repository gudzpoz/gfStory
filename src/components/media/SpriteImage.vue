<script setup lang="ts">
import {
  onMounted, onUnmounted, ref, watch,
} from 'vue';

import type { SpriteImage } from '../../story/interpreter';

const props = defineProps<{
  sprite: SpriteImage,
  center: number,
  container: HTMLDivElement,
  framed?: boolean,
}>();

const idealHeightRatio = 1;
const idealWHRatio = 11 / 16;
const idealCenterTop = 0.70;
const framedAdjustment = 0.6;
const framedTopPadding = 0.10;

function computeImageProperties() {
  const { sprite } = props;
  const { naturalWidth, naturalHeight } = sprite.image;
  const { clientHeight } = props.container;

  const idealHeight = clientHeight * idealHeightRatio;
  const idealScale = idealHeight / naturalHeight;
  const scale = idealScale * (sprite.scale > 0 ? sprite.scale : 1);

  const width = scale * naturalWidth;
  const height = scale * naturalHeight;
  const [centerX, centerY] = sprite.center;

  const centerRatio = idealCenterTop;

  if (!props.framed) {
    const left = -scale * (centerX > 0 ? centerX : naturalWidth / 2);
    const top = clientHeight * centerRatio - scale * (centerY > 0 ? centerY : naturalHeight / 2);

    return [width, height, width, height, left, top, 0, 0, 'none'];
  }

  const boxHeight = idealHeight * framedAdjustment;
  const boxWidth = boxHeight * idealWHRatio;
  const boxLeft = -boxWidth / 2;
  const top = idealHeight * framedTopPadding;
  const boxTop = clientHeight * centerRatio - idealHeight / 2 - top;
  const left = boxWidth / 2 - scale * (centerX > 0 ? centerX : naturalWidth / 2);
  return [
    boxWidth, boxHeight, width, height,
    boxLeft, boxTop, left, top,
    `polygon(${-left}px ${-top}px, ${boxWidth - left}px ${-top}px, \
${boxWidth - left}px ${boxHeight - top}px, ${-left}px ${boxHeight - top}px)`,
  ];
}

const boxWidth = ref(0);
const boxHeight = ref(0);
const width = ref(0);
const height = ref(0);
const boxLeft = ref(0);
const boxTop = ref(0);
const left = ref(0);
const top = ref(0);
const clipPath = ref('');

function updateImageProperties() {
  const properties = computeImageProperties();
  clipPath.value = properties[8] as string;
  [
    boxWidth.value, boxHeight.value, width.value, height.value,
    boxLeft.value, boxTop.value, left.value, top.value,
  ] = properties as number[];
}
updateImageProperties();
onMounted(() => window.addEventListener('resize', updateImageProperties));
onUnmounted(() => window.removeEventListener('resize', updateImageProperties));
watch(() => props.framed, updateImageProperties);
</script>

<template>
  <div class="sprite"
    :style="{ left: `${center}px` }"
  >
    <div class="sprite-frame"
      :style="{
        left: `${boxLeft}px`,
        top: `${boxTop}px`,
        width: `${boxWidth}px`,
        height: `${boxHeight}px`,
      }"
    >
      <img :src="sprite.image.classList.contains('failed') ? '' : sprite.image.src"
        :style="{
          left: `${left}px`,
          top: `${top}px`,
          width: `${width}px`,
          height: `${height}px`,
          clipPath: clipPath as string,
        }"
      />
      <div class="frame-foreground" v-if="framed"></div>
      <div class="frame-background" v-if="framed"></div>
    </div>
  </div>
</template>

<style>
.sprite.sprite-enter-from, .sprite.sprite-leave-to {
  opacity: 0;
  transform: translateX(calc(-50% - 20px));
}
.sprite {
  transition: all 0.2s ease;
  transform: translateX(-50%);
  overflow: visible;
  position: absolute;
  user-select: none;
}
.sprite .sprite-frame {
  position: absolute;
}
.sprite .sprite-frame img {
  position: absolute;
}
.sprite .sprite-frame .frame-background {
  position: relative;
  z-index: -1;
  border-image-source: var(--box-border-image-source);
  border-image-repeat: stretch;
  border-image-slice: fill 37.5% 37.5% 60% 60%;
  border-style: solid;
  border-width: 37.5px 37.5px 60px 60px;
  /* This random pixel counts are computed from the border image. */
  left: -18.15px;
  top: -5.75px;
  width: calc(100% - 73.85px);
  height: calc(100% - 68.35px);
}
.sprite .sprite-frame .frame-foreground::before {
  display: block;
  content: "";
  position: absolute;
  z-index: 2;
  left: 1px;
  top: 1px;
  width: 16px;
  height: 16px;
  background-color: #fdb300;
}
.sprite .sprite-frame .frame-foreground {
  display: block;
  content: "";
  position: absolute;
  z-index: 1;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#cccc 0, #0ff3 0.6px);
  background-size: 3px 3px;
  overflow: hidden;
}

.sprite img[src=""] {
  opacity: 0;
}
</style>
