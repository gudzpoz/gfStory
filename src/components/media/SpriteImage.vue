<script setup lang="ts">
import type { SpriteImage } from '../../story/interpreter';

const props = defineProps<{
  sprite: SpriteImage,
  center: number,
  container: HTMLDivElement,
  framed?: boolean,
}>();

const idealRatio = 0.6;
const idealCenterTop = 0.4;

function computeImageProperties() {
  const { sprite } = props;
  const { naturalWidth, naturalHeight } = sprite.image;
  const { clientWidth, clientHeight } = props.container;

  const idealWidth = clientWidth * idealRatio;
  const idealHeight = clientHeight * idealRatio;
  const idealScale = Math.min(idealWidth / naturalWidth, idealHeight / naturalHeight);
  const scale = idealScale * (sprite.scale > 0 ? sprite.scale : 1);

  const width = scale * naturalWidth;
  const height = scale * naturalHeight;

  const [centerX, centerY] = sprite.center;
  const left = -scale * (centerX > 0 ? centerX : naturalWidth / 2);
  const top = clientHeight * idealCenterTop - scale * (centerY > 0 ? centerY : naturalHeight / 2);

  return [width, height, left, top];
}

const [width, height, left, top] = computeImageProperties();
</script>

<template>
  <div class="sprite"
    :style="{ left: `${center}px` }"
  >
    <div class="sprite-frame"
      :style="{
        left: `${left}px`,
        top: `${top}px`,
        width: `${width}px`,
        height: `${height}px`,
      }"
    >
      <img :src="sprite.image.src" />
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
  width: 100%;
  height: 100%;
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
