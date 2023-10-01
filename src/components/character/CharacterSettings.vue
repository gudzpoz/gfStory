<script setup lang="ts">
import {
  NButton, NForm, NFormItem, NFormItemRow,
  NIcon, NInput, NModal,
  NSpace,
  type FormRules,
  useNotification,
} from 'naive-ui';
import { ref, watch } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import { AddFilled, CropFilled, RemoveFilled } from '@vicons/material';

import MediaSelector from '../media/MediaSelector.vue';
import { getUniqueName, type Character, type CharacterSprite } from '../../types/character';
import { db } from '../../db/media';

import 'vue-advanced-cropper/dist/style.css';
import 'vue-advanced-cropper/dist/theme.compact.css';

const props = defineProps<{
  show: boolean,
  modelValue: Character,
  characters: Character[],
}>();
const sprites = ref(props.modelValue.sprites);
watch(() => props.modelValue, (v) => {
  sprites.value = v.sprites;
});
const names = ref<string[]>(sprites.value.map((s) => s.name));
watch(() => sprites.value, (ss) => {
  names.value = ss.map((s) => s.name);
});

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'update:show', show: boolean): void,
}>();

const rules: FormRules = {
  name: {
    validator: (_, s) => props.characters.filter((c) => c.name === s).length <= 1,
    message: '名称不应重名或为空',
    required: true,
    trigger: ['input', 'blur'],
  },
};

function addSprite() {
  const name = '立绘';
  const unique = getUniqueName(name, sprites.value, 0) ?? name;
  sprites.value.push({
    /**
     * Unique ids are generated after editing is done for all.
     */
    name: unique,
    id: '',
    url: '',
    center: [-1, -1],
    scale: -1,
  });
  names.value.push(unique);
}

const notify = useNotification();

function makeNameUnique() {
  const { name } = props.modelValue;
  const unique = getUniqueName(name, props.characters);
  if (unique) {
    notify.warning({
      duration: 3000,
      content: `人物出现重名，自动重命名为 ${name}`,
    });
  }
  // eslint-disable-next-line vue/no-mutating-props
  props.modelValue.name = unique ?? name;
}

function updateName(i: number) {
  const name = names.value[i];
  const unique = getUniqueName(name, sprites.value);
  if (!unique) {
    sprites.value[i].name = name;
    return;
  }
  names.value[i] = unique;
  sprites.value[i].name = unique;
  notify.warning({
    duration: 3000,
    content: `立绘出现重名，自动重命名为 ${unique}`,
  });
}

const showCropper = ref(false);
const cropperImage = ref<CharacterSprite>();
const cropperImageUrl = ref('');
async function cropImage(sprite: CharacterSprite) {
  const url = await db.toDataUrl(sprite.url);
  if (!showCropper.value) {
    cropperImage.value = sprite;
    cropperImageUrl.value = url;
    showCropper.value = true;
  }
}
function cropCurrentImage(v: unknown) {
  const sprite = cropperImage.value;
  if (!sprite) {
    return;
  }
  const {
    width, height, left, top,
  } = (
    v as { coordinates: { [key: string]: number } }
  ).coordinates;
  sprite.center = [left + width / 2, top + height / 2];
  sprite.scale = (v as { image: { height: number } }).image.height / height;
}
</script>

<template>
  <!-- eslint-disable vue/no-mutating-props -->
  <n-modal v-model:show="showCropper" preset="card" bordered
  >
    <cropper
      :src="cropperImageUrl"
      @change="cropCurrentImage"
      :stencil-props="{
        handlers: {},
        movable: false,
        resizable: false,
      }"
      :stencil-size="{
        width: 220,
        height: 320,
      }"
      image-restriction="stencil"
    >
    </cropper>
  </n-modal>
  <n-modal :show="show" @update:show="(v) => emit('update:show', v)"
    preset="card" embedded bordered @close="makeNameUnique"
  >
    <n-form :model="modelValue" :rules="rules">
      <n-form-item label="显示名称" path="name">
        <n-input :value="modelValue.name" @update:value="(v) => modelValue.name = v"
          type="text" placeholder="人物默认名称" @blur="makeNameUnique"
        >
        </n-input>
      </n-form-item>
      <n-form-item-row>
        <n-space vertical>
          <n-space class="sprite-item" align="center"
            v-for="sprite, i in sprites" :key="sprite.name"
          >
            <n-button @click="sprites.splice(i, 1) && names.splice(i, 1)">
              <n-icon><remove-filled></remove-filled></n-icon>
            </n-button>
            <n-form-item label="立绘名称">
              <n-input :value="names[i]" @update:value="(v) => names[i] = v"
                @blur="updateName(i)"
              >
              </n-input>
            </n-form-item>
            <n-form-item label="立绘图片">
              <media-selector
                type="sprite"
                :modelValue="sprite.url"
                @update:modelValue="(v) => sprite.url = v"
              >
              </media-selector>
            </n-form-item>
            <n-button @click="cropImage(sprite)">
              <n-icon><crop-filled></crop-filled></n-icon>
            </n-button>
          </n-space>
        </n-space>
      </n-form-item-row>
    </n-form>
    <template #header-extra>
      <n-button type="success" @click="addSprite">
        <n-icon><add-filled></add-filled></n-icon>添加立绘
      </n-button>
    </template>
  </n-modal>
</template>

<style>
.sprite-item {
  border: 1px solid var(--n-border-color);
  border-radius: 3px;
  padding: 1em;
}
.n-card .vue-advanced-cropper {
  height: 60vh;
  overflow: hidden;
}
</style>
