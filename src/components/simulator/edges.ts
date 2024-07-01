import { type Edge } from '@vue-flow/core';

export const MAPPED_CHAPTERS = [
  'EP. 10.5',
  'EP. 10.75',
  'EP. 11.5',
  'EP. 11.75',
  'EP. 12.5',
  'EP. 13.25',
  'EP. 13.5',
  'EP. 13.75',
];

export const EP_10_5: Edge[] = [
  { source: '-16-2-1.txt', target: '-16-3-1.txt' },
  { source: '-16-3-1.txt', target: '-16-4-1.txt' },
  { source: '-16-3-1.txt', target: '-16-8-4-point5627.txt' },
  { source: '-16-4-1.txt', target: '-16-5-2first.txt' },
  { source: '-16-5-2first.txt', target: '-16-6-2first.txt' },
  { source: '-16-6-2first.txt', target: '-16-7-2first.txt' },
  { source: '-16-8-4-point5627.txt', target: '-16-9-2first.txt' },
  { source: '-16-9-2first.txt', target: '-16-10-1.txt' },
  { source: '-16-10-1.txt', target: '-16-11-2first.txt' },
  { source: '-16-10-1.txt', target: '-16-12-2first.txt' },
  { source: '-16-12-2first.txt', target: '-16-13-2first.txt' },
  { source: '-16-13-2first.txt', target: '-16-14-2first.txt' },
  { source: '-16-14-2first.txt', target: '-16-15-2first.txt' },
  { source: '-17-1-1.txt', target: '-17-2-1.txt' },
  { source: '-17-2-1.txt', target: '-17-3-1.txt' },
  { source: '-17-3-1.txt', target: '-17-4-1.txt' },
  { source: '-17-4-1.txt', target: '-17-5-2first.txt' },
  { source: '-17-4-1.txt', target: '-17-6-2first.txt' },
  { source: '-17-6-2first.txt', target: '-17-7-2first.txt' },
  { source: '-17-7-2first.txt', target: '-17-8-2first.txt' },
  { source: '-17-8-2first.txt', target: '-17-9-2first.txt' },
  { source: '-17-1-1.txt', target: '-17-10-1.txt' },
  { source: '-17-10-1.txt', target: '-17-11-1.txt' },
  { source: '-17-11-1.txt', target: '-17-12-2first.txt' },
  { source: '-17-12-2first.txt', target: '-17-13-1.txt' },
  { source: '-17-12-2first.txt', target: '-17-14-1.txt' },
  { source: '-17-14-1.txt', target: '-17-15-1.txt' },
  { source: '-17-15-1.txt', target: '-17-16-1.txt' },
  { source: '-17-16-1.txt', target: '-17-17-1.txt' },
  { source: '-18-1-1.txt', target: '-18-2-1.txt' },
  { source: '-18-2-1.txt', target: '-18-3-1.txt' },
  { source: '-18-3-1.txt', target: '-18-4-1.txt' },
  { source: '-18-4-1.txt', target: '-18-5-1.txt' },
  { source: '-18-5-1.txt', target: '-18-6-1.txt' },
].map((e) => ({ ...e, id: `${e.source}_${e.target}` }));

export const EP_10_5_GROUPS: string[][] = [
  ['battleavg/-18-day3-6b.txt', '-16-2-1.txt', '-16-16-1.txt'],
  ['-17-1-1.txt', '-17-18-1.txt', '-18-8-1.txt'],
  ['-18-1-1.txt', '-18-7-1.txt'],
];

export const CHAPTER_EDGES: Record<string, Edge[]> = {
  'EP. 10.5': EP_10_5,
};

export const CHAPTER_GROUPS: Record<string, string[][]> = {
  'EP. 10.5': EP_10_5_GROUPS,
};
