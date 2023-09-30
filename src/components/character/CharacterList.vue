<script setup lang="ts">
import {
  NButton, NIcon,
  NList, NListItem, NModal,
  NSpace, NTag,
} from 'naive-ui';
import { ref } from 'vue';
import {
  AddFilled, EditFilled, RemoveFilled,
} from '@vicons/material';

import CharacterSettings from './CharacterSettings.vue';
import MediaItem from '../media/MediaItem.vue';
import { getUniqueName, type Character } from '../../types/character';

const props = defineProps<{
  show: boolean,
  modelValue: Character[],
}>();
const characters = ref(props.modelValue);

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'update:show', show: boolean): void,
}>();

function addCharacter() {
  const name = '角色';
  const unique = getUniqueName(name, characters.value, 0) ?? name;
  characters.value.push({
    name: unique,
    sprites: [],
  });
}

const currentCharacter = ref<Character>();
const showEditor = ref(false);
function edit(character: Character) {
  currentCharacter.value = character;
  showEditor.value = true;
}
</script>

<template>
  <character-settings v-if="currentCharacter" v-model="currentCharacter"
    v-model:show="showEditor" :characters="characters"
  >
  </character-settings>
  <n-modal :show="show" @update:show="(v) => emit('update:show', v)"
    preset="card" title="人物列表"
  >
    <n-list>
      <n-list-item v-for="character, i in characters" :key="character.name">
        <n-space align="center">
          <n-button type="warning" @click="edit(character)">
            <n-icon><edit-filled></edit-filled></n-icon>
          </n-button>
          <n-button type="error" @click="characters.splice(i, 1)">
            <n-icon><remove-filled></remove-filled></n-icon>
          </n-button>
          <n-tag type="info">{{ character.name }}</n-tag>
          <media-item v-for="sprite in character.sprites" :key="sprite.url"
            :url="sprite.url"
          >
          </media-item>
        </n-space>
      </n-list-item>
    </n-list>
    <template #header-extra>
      <n-space>
        <n-button type="success" @click="addCharacter">
          <n-icon><add-filled></add-filled></n-icon>添加人物
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<style>
.n-card.n-modal {
  margin: 3em;
}
</style>
