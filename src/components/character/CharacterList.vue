<script setup lang="ts">
import {
  NButton, NDataTable, NIcon, NInput,
  NList, NListItem, NModal,
  NSpace, NTag,
  type DataTableBaseColumn, type DataTableColumns,
} from 'naive-ui';
import {
  h, reactive, ref, watch,
} from 'vue';
import {
  AddFilled, EditFilled, ImportContactsFilled, RemoveFilled,
} from '@vicons/material';

import CharacterSettings from './CharacterSettings.vue';
import MediaItem from '../media/MediaItem.vue';
import { IMAGE_PATH_PREFIX, type GfCharactersInfo } from '../../types/assets';
import { getUniqueName, type Character } from '../../types/character';

import assetCharacterPresets from '../../assets/characters.json';

const characterPresets = assetCharacterPresets as unknown as GfCharactersInfo;

const props = defineProps<{
  show: boolean,
  modelValue: Character[],
}>();
const characters = ref(props.modelValue);

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'update:show', show: boolean): void,
  (event: 'update:modelValue', modelValue: Character[]): void,
}>();

function update() {
  emit('update:modelValue', characters.value);
}
watch(() => props.show, update);

function addCharacter() {
  const name = '角色';
  const unique = getUniqueName(name, characters.value, 0) ?? name;
  characters.value.push({
    /*
     * Unique ids are generated when editing is done for all.
     */
    id: '',
    name: unique,
    sprites: [],
    imported: false,
  });
}

type Preset = {
  name: string;
  image: string;
  image_count: number;
};
function importPreset(preset: Preset) {
  const character = characterPresets[preset.name];
  const unique = getUniqueName(preset.name, characters.value, 0) ?? preset.name;
  characters.value.push({
    id: '',
    name: unique,
    imported: true,
    sprites: Object.entries(character).map(([name, sprite]) => ({
      name,
      id: '',
      url: `${IMAGE_PATH_PREFIX}${sprite.path}`,
      scale: sprite.scale,
      center: [-1, -1],
    })),
  });
}
const showPresetModal = ref(false);
const presetNameColumn: DataTableBaseColumn<Preset> = reactive({
  title: '代号',
  key: 'name',
  filterOptionValue: '',
  filter: (v, row) => row.name.toLowerCase().includes((v as string).toLowerCase()),
});
const presetColumns: DataTableColumns<Preset> = [
  presetNameColumn,
  {
    title: '预览',
    key: 'image',
    render: (preset) => h(
      MediaItem,
      { url: `${IMAGE_PATH_PREFIX}${preset.image}` },
    ),
  },
  { title: '大致立绘数量', key: 'image_count' },
  {
    title: '操作',
    key: 'actions',
    render: (preset) => h(
      NButton,
      { onClick: () => importPreset(preset) },
      { default: () => '导入' },
    ),
  },
];
const presetData: Preset[] = Object.entries(characterPresets).map(([c, v]) => {
  const keys = Object.keys(v);
  return {
    name: c,
    image: v[keys[0]].path,
    image_count: keys.length,
  };
});
const presetFilter = ref('');
watch(() => presetFilter.value, (filter) => {
  presetNameColumn.filterOptionValue = filter;
});
function showPresets() {
  showPresetModal.value = true;
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
    @update:show="update()"
  >
  </character-settings>
  <n-modal :show="showPresetModal" @update:show="(v) => showPresetModal = v"
    preset="card" title="预设人物"
  >
    <n-input v-model:value="presetFilter" placeholder="搜索"></n-input>
    <n-data-table :columns="presetColumns" :data="presetData" :pagination="{ pageSize: 10 }">
    </n-data-table>
  </n-modal>
  <n-modal :show="show" @update:show="(v) => { update(); emit('update:show', v); }"
    preset="card" title="人物列表"
  >
    <n-list>
      <n-list-item v-for="character, i in characters" :key="character.name">
        <n-space align="center">
          <n-button type="warning" @click="edit(character)" :disabled="character.imported">
            <n-icon><edit-filled></edit-filled></n-icon>
          </n-button>
          <n-button type="error" @click="characters.splice(i, 1) && update()">
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
        <n-button type="success" @click="showPresets">
          <n-icon><import-contacts-filled></import-contacts-filled></n-icon>导入预设
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
