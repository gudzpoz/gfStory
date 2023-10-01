<script setup lang="ts">
import type { SpriteImage } from '../../story/interpreter';

const props = defineProps<{
  sprite: SpriteImage,
  center: number,
  container: HTMLDivElement,
  framed?: boolean,
}>();

const idealHeightRatio = 0.6;
const idealWHRatio = 11 / 16;
const idealCenterTop = 0.4;

function computeImageProperties() {
  const { sprite } = props;
  const { naturalWidth, naturalHeight } = sprite.image;
  const { clientHeight } = props.container;

  const idealHeight = clientHeight * idealHeightRatio;
  const idealWidth = idealHeight * idealWHRatio;
  const idealScale = idealHeight / naturalHeight;
  const scale = idealScale * (sprite.scale > 0 ? sprite.scale : 1);

  const width = scale * naturalWidth;
  const height = scale * naturalHeight;
  const [centerX, centerY] = sprite.center;

  if (!props.framed) {
    const left = -scale * (centerX > 0 ? centerX : naturalWidth / 2);
    const top = clientHeight * idealCenterTop - scale * (centerY > 0 ? centerY : naturalHeight / 2);

    return [width, height, width, height, left, top, 0, 0, 'none'];
  }
  const boxLeft = -idealWidth / 2;
  const boxTop = clientHeight * idealCenterTop - idealHeight / 2;
  const left = idealWidth / 2 - scale * (centerX > 0 ? centerX : naturalWidth / 2);
  const top = idealHeight / 2 - scale * (centerY > 0 ? centerY : naturalHeight / 2);
  return [
    idealWidth, idealHeight, width, height,
    boxLeft, boxTop, left, top,
    `polygon(${-left}px ${-top}px, ${idealWidth - left}px ${-top}px, \
${idealWidth - left}px ${idealHeight - top}px, ${-left}px ${idealHeight - top}px)`,
  ];
}

const [
  boxWidth, boxHeight, width, height,
  boxLeft, boxTop, left, top, clipPath,
] = computeImageProperties();
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
      <img :src="sprite.image.src"
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
@keyframes scan-line {
  from, 20% {
    top: -10%;
  }
  80%, to {
    top: 110%;
  }
}
.sprite .sprite-frame .frame-foreground::after {
  display: block;
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  box-shadow: 0 1px 3px aqua, 0 -1px 3px aqua, 0 0 6px aqua inset;
  animation: scan-line 15s linear 5s infinite;
}
</style>
