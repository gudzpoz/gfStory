import fs from 'fs/promises';
import pathlib from 'path';

import { bigram } from 'n-gram';
import MiniSearch from 'minisearch';

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

const files = (await allTxtFiles(directory)).map((f) => pathlib.relative(directory, f));

const index = new MiniSearch({
  fields: ['text'],
  storeFields: ['id'],
  tokenize: bigram,
});

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
        text = text.replace(/^.+?(?:<p>|$)/mg, '').replace(/<\/p>$/mg, '');
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
        index.add({
          id: path,
          text,
        });
        return path;
      }));
    }));
  })),
));
const processed = new Set(results.flat().flat().flat());
const unprocessed = files.filter((f) => !processed.has(f));
if (unprocessed.length !== 0) {
  // eslint-disable-next-line no-console
  console.warn(`Some files were not indexed: ${unprocessed}`);
}

await fs.mkdir(output, { recursive: true });
const serialization = JSON.stringify(index);

function split(s: string, maxLength: number): string[] {
  const result: string[] = [];
  let start = 0;
  while (start < s.length) {
    result.push(s.slice(start, start + maxLength));
    start += maxLength;
  }
  return result;
}

const chunks = split(serialization, 4 * 1024 * 1024);
await Promise.all(chunks.map(
  async (chunk, i) => fs.writeFile(`${output}/index.json.${i}`, chunk),
));

fs.writeFile(`${output}/index.json`, JSON.stringify(chunks.map((_, i) => `./index.json.${i}`)));
