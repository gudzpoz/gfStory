/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  'extends': [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    'airbnb-base',
    'airbnb-typescript/base',
    '@vue/eslint-config-typescript/recommended',
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    project: ['./tsconfig.app.json'],
    ecmaVersion: 'latest',
  },
  plugins: [
    '@typescript-eslint',
  ],
  ignorePatterns: [
    'vite.config.ts',
    '.eslintrc.cjs',
  ],
};
