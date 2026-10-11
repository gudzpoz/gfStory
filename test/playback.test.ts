import { describe, expect, it } from 'vitest';
import nextStory from '../src/components/simulator/playback';
import type { Chapter } from '../src/types/assets';

const chapters: Chapter[] = [
  {
    name: '开局剧情',
    description: '',
    stories: [
      { name: '第一节', description: '', files: ['startavg/start0.txt'] },
      {
        name: '第二节',
        description: '',
        files: [['startavg/start1.txt', '前篇'], ['startavg/start2.txt', '后篇']],
      },
      { name: '重复引用', description: '', files: ['startavg/start1.txt'] },
      { name: '空项', description: '', files: [] },
      { name: '末节', description: '', files: ['-44-t2-3-ex .txt'] },
    ],
  },
  {
    name: '另一活动',
    description: '',
    stories: [{ name: '序幕', description: '', files: ['-other.txt'] }],
  },
];
describe('continuous playback sequence', () => {
  it('uses directory order across stories and their individual script parts', () => {
    expect(nextStory(chapters, 'startavg/start0.txt', new Set(), false))
      .toBe('startavg/start1.txt');
    expect(nextStory(chapters, 'startavg/start1.txt', new Set(), false))
      .toBe('startavg/start2.txt');
    expect(nextStory(chapters, 'startavg/start2.txt', new Set(), false))
      .toBe('-44-t2-3-ex .txt');
  });

  it('skips read scripts only when requested and does not change read records', () => {
    const read = new Set(['startavg/start1.txt', 'startavg/start2.txt']);
    expect(nextStory(chapters, 'startavg/start0.txt', read, false)).toBe('startavg/start1.txt');
    expect(nextStory(chapters, 'startavg/start0.txt', read, true)).toBe('-44-t2-3-ex .txt');
    expect([...read]).toEqual(['startavg/start1.txt', 'startavg/start2.txt']);
  });

  it('stops at the current chapter boundary and never wraps or enters another activity', () => {
    expect(nextStory(chapters, '-44-t2-3-ex .txt', new Set(), false)).toBeUndefined();
    expect(nextStory(chapters, '-other.txt', new Set(), false)).toBeUndefined();
    expect(nextStory(chapters, '-unknown.txt', new Set(), false)).toBeUndefined();
  });

  it('stops when all later scripts are read, including duplicated script references', () => {
    const read = new Set(['startavg/start1.txt', 'startavg/start2.txt', '-44-t2-3-ex .txt']);
    expect(nextStory(chapters, 'startavg/start0.txt', read, true)).toBeUndefined();
  });
});
