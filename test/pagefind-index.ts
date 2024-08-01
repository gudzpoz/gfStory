import fs from 'fs/promises';
import pathlib from 'path';

import * as pagefind from 'pagefind';

import chapters from '../src/assets/chapters.json';
import type { GfChaptersInfo } from '../src/types/assets';

const typedChapters = chapters as GfChaptersInfo;

function assert(v: unknown, msg: string) {
  if (!v) {
    throw new Error(msg);
  }
}

const directory = process.argv[2];
const output = process.argv[3];
assert(
  directory && (await fs.stat(directory)).isDirectory() && output,
  'Usage: vite-node flex-index.ts <story_directory> <output_directory>',
);

async function allTxtFiles(path: string): Promise<string[]> {
  const files = await fs.readdir(path);
  return (
    await Promise.all(
      files.map(async (f) => {
        const p = `${path}/${f}`;
        const stat = await fs.stat(p);
        if (stat.isDirectory()) {
          return allTxtFiles(p);
        }
        if (stat.isFile() && f.toLowerCase().endsWith('.txt')) {
          return [p];
        }
        return [];
      }),
    )
  ).flat();
}

const index = (await pagefind.createIndex({})).index!;

const results = await Promise.all(Object.values(typedChapters).map(
  async (category) => Promise.all(category.map(async (chapter) => {
    let firstStory = true;
    return Promise.all(chapter.stories.map(async (story) => {
      let firstFile = true;
      return Promise.all(story.files.map(async (file) => {
        const path = typeof file === 'string' ? file : file[0];
        let text = await fs.readFile(`${directory}/${path}`, 'utf-8');
        const start = text.indexOf('```', text.indexOf('```lua') + 6) + 3;
        text = text.slice(start);
        const narrators = new Set([...text.matchAll(/:narrator\[([^\]]+)]/g)].map((m) => m[1]));
        text = text.replace(/^.+?(?:<p>|$)/mg, '').replace(/<[^>]+?>/mg, '');
        text = `${[...narrators].join(' ')} ${text}`;
        if (typeof file !== 'string') {
          text = `${file[1]} ${text}`;
        }
        if (firstFile) {
          text = `${story.name} ${story.description} ${text}`;
          firstFile = false;
        }
        if (firstStory) {
          text = `${chapter.name} ${chapter.description} ${text}`;
          firstStory = false;
        }
        await index.addCustomRecord({
          url: path,
          content: text,
          language: 'zh',
        });
        return path;
      }));
    }));
  })),
));

const processed = new Set(results.flat().flat().flat());
const files = (await allTxtFiles(directory)).map((f) => pathlib.relative(directory, f));
const unprocessed = files.filter((f) => !processed.has(f));
if (unprocessed.length !== 0) {
  // eslint-disable-next-line no-console
  console.warn(`Some files were not indexed: ${unprocessed}`);
}

await fs.mkdir(output, { recursive: true });
await index.writeFiles({
  outputPath: output,
});
await pagefind.close();
