import './assets/main.css';

import 'vfonts/Lato.css';
import 'vfonts/FiraCode.css';

import CKEditor from '@ckeditor/ckeditor5-vue';
import { createApp } from 'vue';
import App from './App.vue';

createApp(App).use(CKEditor).mount('#app');
