import process from 'node:process';
import { fileURLToPath, URL } from 'node:url';

import ckeditor5 from '@ckeditor/vite-plugin-ckeditor5';
import { viteSingleFile } from 'vite-plugin-singlefile';
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const BUILD_VIEWER = process.env.BUILD_TARGET === 'viewer';

// https://vitejs.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    ckeditor5({ theme: require.resolve('@ckeditor/ckeditor5-theme-lark') }),
    vue(),
    BUILD_VIEWER && viteSingleFile({}),
  ],
  build: {
    outDir: BUILD_VIEWER ? 'viewer' : 'dist',
    rollupOptions: {
      input: BUILD_VIEWER ? {
        viewer: fileURLToPath(new URL('./viewer.html', import.meta.url)),
      } : {
        editor: fileURLToPath(new URL('./index.html', import.meta.url)),
        simulator: fileURLToPath(new URL('./simulator.html', import.meta.url)),
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
