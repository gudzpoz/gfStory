<script setup lang="ts">
import {
  NButton, NIcon,
  NSelect, NUpload,
  type SelectOption,
  type UploadCustomRequestOptions,
} from 'naive-ui';
import { UploadFileFilled } from '@vicons/material';
import {
  computed, h, watch, type VNodeChild,
} from 'vue';

import MediaItem from './MediaItem.vue';
import {
  db, ACCEPTED, MEDIA_TYPES,
  type Media,
} from '../../db/media';

const props = defineProps<{
  type: typeof MEDIA_TYPES[number],
  multiple?: boolean,
  modelValue?: string,
}>();

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'update:modelValue', modelValue: string): void,
}>();

type Options = (SelectOption & Media)[];
const items = computed(() => db.getMediaItems(props.type).value as Options);
watch(() => props.type, () => emit('update:modelValue', ''));

const renderLabel = (media: Media): VNodeChild => (
  h(MediaItem, {
    wide: true,
    url: media.value,
    onRemove: () => db.deleteMedia(media.type, media.name),
  })
);

function upload(options: UploadCustomRequestOptions) {
  const { name, file } = options.file;
  if (!file) {
    options.onError();
    return;
  }
  options.onProgress({ percent: 0 });
  db[props.type].add({ name, blob: file })
    .then(() => options.onFinish())
    .catch(() => options.onError());
  options.onProgress({ percent: 10 });
}
</script>

<template>
  <n-select
    :options="items"
    :render-label="renderLabel"
    :multiple="multiple"
    :value="modelValue"
    @update:value="(v) => emit('update:modelValue', v)"
    :fallback-option="false"
    clearable
    filterable
    class="media-select"
    size="large"
  >
    <template #action>
      <n-upload
        :custom-request="upload"
        :accept="ACCEPTED[type]"
        :show-cancel-button="false"
        :show-file-list="false"
        :show-remove-button="false"
      >
        <n-button type="info">
          <n-icon><upload-file-filled></upload-file-filled></n-icon>添加文件
        </n-button>
      </n-upload>
    </template>
  </n-select>
</template>
