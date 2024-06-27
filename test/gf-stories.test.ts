import fs from 'fs/promises';

import { assert, test } from 'vitest';

import { compileMarkdown } from '../src/story/compiler';
import { StoryInterpreter } from '../src/story/interpreter';

async function readAllDir(dir: string): Promise<string[]> {
  const files = await fs.readdir(dir);
  return (await Promise.all(files.map(async (file) => {
    const path = `${dir}/${file}`;
    const stat = await fs.stat(path);
    if (stat.isDirectory()) {
      return readAllDir(path);
    }
    return [path];
  }))).flat();
}

const stories = await readAllDir('public/stories');
const excluded = [
  'public/stories/avgplaybackprofiles.txt',
  'public/stories/profiles.txt',
  'public/stories/chapters.json',
  'public/stories/stories.json',
];
stories.forEach((story) => {
  if (excluded.includes(story)) {
    return;
  }
  test(`running ${story}`, async () => {
    const markdown = await fs.readFile(story, 'utf-8');
    const lua = await compileMarkdown(markdown);
    const interpreter = new StoryInterpreter();
    await interpreter.reload(lua, false);
    const line = interpreter.next();
    assert.ok(line, 'story should have a first line');
  });
});
