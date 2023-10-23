<script setup lang="ts">
import {
  NCascader, NCheckbox, NSpace, type CascaderOption,
} from 'naive-ui';
import { computed, h, ref } from 'vue';

import MediaItem from '../media/MediaItem.vue';
import {
  getNamePath, getSprite,
  type Character, type CharacterSprite,
  type NamePath, type SpritePath,
} from '../../types/character';

const props = defineProps<{
  modelValue: string,
  remoteRecord: Record<string, boolean>,
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

const emit = defineEmits<{
  'update:modelValue': [modelValue: string],
}>();

const remote = ref(!!props.remoteRecord[props.modelValue]);
function updateSelected(_v: never, _option: never, path: SpritePath) {
  namePath.value = getNamePath(path);
  emit('update:modelValue', namePath.value.join('/'));
}
function updateRemote(r: boolean) {
  remote.value = r;
  // eslint-disable-next-line vue/no-mutating-props
  props.remoteRecord[namePath.value.join('/')] = r;
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
    <n-checkbox :checked="remote" @update:checked="updateRemote">
      电子外观
    </n-checkbox>
  </n-space>
</template>
