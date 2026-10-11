import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: { include: ['test/progress.test.ts', 'test/playback.test.ts'], environment: 'node' },
});
