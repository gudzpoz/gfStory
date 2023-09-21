import { fileURLToPath, URL } from 'node:url'

import ckeditor5 from '@ckeditor/vite-plugin-ckeditor5';
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    ckeditor5({ theme: require.resolve('@ckeditor/ckeditor5-theme-lark') }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
