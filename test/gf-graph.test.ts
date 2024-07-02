import { assert, test } from 'vitest';

import {
  type GfChaptersInfo,
} from '../src/types/assets';
import { CHAPTER_EDGES, CHAPTER_GROUPS } from '../src/components/simulator/edges';

import jsonChapterPresets from '../src/assets/chapters.json';

const chapterPresets: GfChaptersInfo = jsonChapterPresets;

test('no missing graph node ids', () => {
  const ids = Object.values(CHAPTER_EDGES)
    .flatMap((edges) => edges.flatMap((e) => [e.source, e.target]))
    .concat(Object.values(CHAPTER_GROUPS).flat().flat());
  const allIds = new Set(
    Object.values(chapterPresets).flat()
      .flatMap((chapter) => chapter.stories)
      .map((story) => (typeof story.files[0] === 'string' ? story.files[0] : story.files[0][0])),
  );
  ids.forEach((id) => assert(allIds.has(id), `${id} not found in presets`));
});
