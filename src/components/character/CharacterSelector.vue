<script setup lang="ts">
import { NCascader, NSpace, type CascaderOption } from 'naive-ui';
import { computed, h, ref } from 'vue';

import MediaItem from '../media/MediaItem.vue';
import {
  getNamePath, getSprite,
  type Character, type CharacterSprite,
  type NamePath, type SpritePath,
} from '../../types/character';

const props = defineProps<{
  modelValue: string,
  characters: Character[],
}>();
const namePath = ref<readonly string[]>(props.modelValue.split('/'));
const id = computed(() => (getSprite(
  namePath.value as [string, string],
  props.characters,
) as CharacterSprite)?.id);

function renderLabel(o: CascaderOption) {
  const option = o as unknown as Character | CharacterSprite;
  let sprite: CharacterSprite | undefined;
  if ((option as CharacterSprite).url) {
    sprite = option as CharacterSprite;
  } else {
    [sprite] = (option as Character).sprites;
  }
  if (!sprite) {
    return option.name;
  }
  return h(NSpace, { align: 'center', noWrap: true }, {
    default: () => [
      h(MediaItem, { url: sprite!.url }),
      option.name,
    ],
  });
}

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'update:modelValue', modelValue: string): void,
}>();

function updateSelected(_v: never, _option: never, path: SpritePath) {
  namePath.value = getNamePath(path);
  emit('update:modelValue', namePath.value.join('/'));
}
const url = computed(() => {
  if (namePath.value.length !== 2) {
    return '';
  }
  return getSprite(namePath.value as NamePath, props.characters)?.url ?? '';
});
</script>

<template>
  <n-space align="center">
    <media-item :url="url"></media-item>
    <n-cascader
      :options="(characters as unknown as CascaderOption[])"
      :value="id"
      @update:value="updateSelected"
      label-field="name"
      value-field="id"
      children-field="sprites"
      check-strategy="child"
      expand-trigger="hover"
      filterable
      :render-label="renderLabel"
    >
    </n-cascader>
  </n-space>
</template>
