<script setup lang="ts">
import { nextTick, ref, watch } from 'vue';

const props = defineProps<{
  html: string,
  durationMs?: number,
  animating?: boolean,
}>();
const emit = defineEmits<{
  'update:animating': [value: boolean],
}>();
const textBox = ref<HTMLDivElement>();

function extractAllTexts(div: HTMLElement) {
  const texts: [Text, string][] = [];
  function process(node: HTMLElement) {
    node.childNodes.forEach((n) => {
      if (n.nodeName === '#text') {
        const text = n as Text;
        texts.push([text, text.nodeValue ?? '']);
        text.nodeValue = '\u200B';
      } else {
        process(n as HTMLElement);
      }
    });
  }
  process(div);
  return texts;
}

let timer: ReturnType<typeof setTimeout> | undefined;
let currentTexts: ReturnType<typeof extractAllTexts> = [];
function startAnimation() {
  if (timer) {
    clearTimeout(timer);
    timer = undefined;
  }
  const div = textBox.value;
  if (!div) {
    emit('update:animating', false);
    return;
  }
  emit('update:animating', true);
  div.style.display = 'none';
  div.innerHTML = props.html;
  const texts = extractAllTexts(div);
  currentTexts = texts;
  function popChar(i: number, n: number) {
    if (i >= texts.length) {
      timer = undefined;
      emit('update:animating', false);
      return;
    }
    const [text, s] = texts[i];
    if (n >= s.length) {
      popChar(i + 1, 0);
      return;
    }
    text.nodeValue = s.substring(0, n + 1);
    timer = setTimeout(
      () => requestAnimationFrame(() => popChar(i, n + 1)),
      props.durationMs ?? 42,
    );
  }
  div.style.display = '';

  nextTick(() => requestAnimationFrame(() => popChar(0, 0)));
}
startAnimation();
watch(() => props.html, startAnimation);
watch(() => props.animating, (animating) => {
  if (animating) {
    return;
  }
  if (timer !== undefined) {
    clearTimeout(timer);
    timer = undefined;
    // eslint-disable-next-line no-param-reassign
    currentTexts.forEach(([text, s]) => { text.nodeValue = s; });
  }
});
</script>

<template>
  <div ref="textBox"></div>
</template>
