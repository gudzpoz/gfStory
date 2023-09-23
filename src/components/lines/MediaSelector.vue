<script setup lang="ts">
import {
  NAvatar, NButton, NIcon,
  NSelect, NSpace, NUpload,
  type UploadCustomRequestOptions,
} from 'naive-ui';
import { CloseFilled, UploadFileFilled } from '@vicons/material';
import {
  h, ref, watch, type VNodeChild,
} from 'vue';

import { db, ACCEPTED, MEDIA_TYPES } from '../../db/media';

const props = defineProps<{
  type: typeof MEDIA_TYPES[number],
  multiple?: boolean,
  modelValue?: string,
}>();

// eslint-disable-next-line no-spaced-func
const emit = defineEmits<{
  (event: 'update:modelValue', modelValue: string): void,
}>();

type Option = { label: string, value: string, url: string };
const items = ref<Option[]>([]);

const subscribe = () => db.liveQueryAll(props.type).subscribe((media) => {
  items.value = media.map((m) => {
    const url = URL.createObjectURL(m.blob);
    return {
      label: m.name,
      value: `${props.type}:${m.name}`,
      url,
    };
  });
});
let subscription = subscribe();
watch(() => props.type, () => {
  subscription.unsubscribe();
  subscription = subscribe();
});

const renderLabel = (option: Option): VNodeChild => (
  h(NSpace, { align: 'center' }, () => [
    h(NButton, {
      onClick(e) {
        e.stopPropagation();
        db[props.type].delete(option.label);
      },
    }, () => [h(NIcon, {}, () => [h(CloseFilled)])]),
    h(NAvatar, { src: option.url }),
    option.label,
  ])
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

<style>
.n-space .n-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0.2em;
  width: 2.5em;
  height: 2.5em;
}
.n-space .n-avatar img {
  width: fit-content;
  height: fit-content;
  max-width: 2.5em;
  max-height: 2.5em;
}
.n-select .n-space .n-button {
  display: none;
}
</style>
