<script setup lang="ts">
import {
  NButton, NDataTable, NIcon, NInput,
  NModal, NSelect, NSpace, NUpload,
  useNotification,
  type DataTableBaseColumn, type DataTableColumns,
  type SelectOption,
  type UploadCustomRequestOptions,
} from 'naive-ui';
import { CloudCircleFilled, UploadFileFilled } from '@vicons/material';
import {
  computed, h, reactive, ref, watch,
  type ComputedRef, type VNodeChild,
} from 'vue';

import MediaItem from './MediaItem.vue';
import {
  db, ACCEPTED, MEDIA_TYPES,
  type Media,
} from '../../db/media';
import {
  AUDIO_PATH_PREFIX, IMAGE_PATH_PREFIX,
} from '../../types/assets';

import backgroundPresets from '../../assets/backgrounds.json';
import audioPresets from '../../assets/audio.json';

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
  db.addMedia(props.type, name, file)
    .then(() => options.onFinish())
    .catch(() => options.onError());
  options.onProgress({ percent: 10 });
}

type Preset = {
  url: string;
};
const notify = useNotification();
function importPreset(preset: Preset) {
  const url = `${
    props.type === 'audio' ? AUDIO_PATH_PREFIX : IMAGE_PATH_PREFIX
  }${preset.url}`;
  db.addMedia(props.type, url.substring(url.lastIndexOf('/') + 1), url)
    .then(() => notify.info({
      content: `已导入 ${preset.url}`,
    }))
    .catch((e) => notify.error({ content: `导入错误 ${e}` }));
}
const showPresetModal = ref(false);
const presetUrlColumn: DataTableBaseColumn<Preset> = reactive({
  title: '资源路径',
  key: 'url',
  filterOptionValue: '',
  filter: (v, row) => row.url.toLowerCase().includes((v as string).toLowerCase()),
});
const presetFilter = ref('');
watch(() => presetFilter.value, (filter) => {
  presetUrlColumn.filterOptionValue = filter;
});
const presetColumns: DataTableColumns<Preset> = [
  presetUrlColumn,
  {
    title: '预览',
    key: 'url',
    render: (preset) => h(
      MediaItem,
      {
        url: `${
          props.type === 'audio' ? AUDIO_PATH_PREFIX : IMAGE_PATH_PREFIX
        }${preset.url}`,
      },
    ),
  },
  {
    title: '导入',
    key: 'actions',
    render: (preset) => h(
      NButton,
      { onClick: () => importPreset(preset) },
      { default: () => '导入' },
    ),
  },
];
const presets: ComputedRef<Preset[]> = computed(
  () => [...new Set(
    Object.values(props.type === 'audio' ? audioPresets : backgroundPresets),
  )].map((url) => ({
    url,
  })),
);
</script>

<template>
  <n-modal v-model:show="showPresetModal" preset="card">
    <n-input v-model:value="presetFilter" placeholder="搜索"></n-input>
    <n-data-table :columns="presetColumns" :data="presets" :pagination="{ pageSize: 10 }">
    </n-data-table>
  </n-modal>
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
      <n-space align="center">
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
        <n-button type="warning" v-if="type !== 'sprite'" @click="showPresetModal = true">
          <n-icon><cloud-circle-filled></cloud-circle-filled></n-icon>使用预设
        </n-button>
      </n-space>
    </template>
  </n-select>
</template>
