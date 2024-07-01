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

function genId(e: { source: string, target: string }) {
  return { ...e, id: `${e.source}_${e.target}` };
}

const EP_10_5: Edge[] = [
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
].map(genId);

const EP_10_5_GROUPS: string[][] = [
  ['battleavg/-18-day3-6b.txt', '-16-2-1.txt', '-16-16-1.txt'],
  ['-17-1-1.txt', '-17-18-1.txt', '-18-8-1.txt'],
  ['-18-1-1.txt', '-18-7-1.txt'],
];

const EP_10_75: Edge[] = [
  { source: '-24-1-1.txt', target: '-24-2-1.txt' },
  { source: '-24-2-1.txt', target: '-24-3-2first.txt' },
  { source: '-24-2-1.txt', target: '-24-4-1.txt' },
  { source: '-24-4-1.txt', target: '-24-5-1.txt' },
  { source: '-24-5-1.txt', target: '-24-6-1.txt' },
  { source: '-24-6-1.txt', target: '-24-7-1.txt' },
  { source: '-24-7-1.txt', target: '-24-9-2first.txt' },
  { source: '-24-6-1.txt', target: '-24-8-1.txt' },
  { source: '-24-8-1.txt', target: '-24-10-1.txt' },
  { source: '-24-10-1.txt', target: '-24-11-1.txt' },
  { source: '-24-11-1.txt', target: '-24-12-1.txt' },
  { source: '-24-12-1.txt', target: '-24-13-1.txt' },
  { source: '-24-13-1.txt', target: '-24-14-1.txt' },
  { source: '-24-14-1.txt', target: '-24-15-1.txt' },
  { source: '-25-1-1.txt', target: '-25-2-1.txt' },
  { source: '-25-2-1.txt', target: '-25-12-2first.txt' },
  { source: '-25-2-1.txt', target: '-25-3-1.txt' },
  { source: '-25-3-1.txt', target: '-25-4-1.txt' },
  { source: '-25-4-1.txt', target: '-25-13-2first.txt' },
  { source: '-25-4-1.txt', target: '-25-5-1.txt' },
  { source: '-25-5-1.txt', target: '-25-7-1.txt' },
  { source: '-25-5-1.txt', target: '-25-6-1.txt' },
  { source: '-25-7-1.txt', target: '-25-6-1.txt' },
  { source: '-25-7-1.txt', target: '-25-8-1.txt' },
  { source: '-25-8-1.txt', target: '-25-10-1.txt' },
  { source: '-25-10-1.txt', target: '-25-11-1.txt' },
  { source: '-25-6-1.txt', target: '-25-9-1.txt' },
  { source: '-25-9-1.txt', target: '-25-11-1.txt' },
  { source: '-25-11-1.txt', target: '-25-14-2first.txt' },
  { source: '-25-11-1.txt', target: '-25-15-2first.txt' },
  { source: '-25-11-1.txt', target: '-25-16-2first.txt' },
  { source: '-26-1-1.txt', target: '-26-2-1.txt' },
  { source: '-26-2-1.txt', target: '-26-3-1.txt' },
  { source: '-26-3-1.txt', target: '-26-15-2first.txt' },
  { source: '-26-3-1.txt', target: '-26-4-1.txt' },
  { source: '-26-2-1.txt', target: '-26-4-1.txt' },
  { source: '-26-4-1.txt', target: '-26-5-1.txt' },
  { source: '-26-5-1.txt', target: '-26-15-2first.txt' },
  { source: '-26-5-1.txt', target: '-26-7-1.txt' },
  { source: '-26-4-1.txt', target: '-26-6-1.txt' },
  { source: '-26-6-1.txt', target: '-26-7-1.txt' },
  { source: '-26-7-1.txt', target: '-26-8-2first.txt' },
  { source: '-26-7-1.txt', target: '-26-9-1.txt' },
  { source: '-26-9-1.txt', target: '-26-10-2first.txt' },
  { source: '-26-9-1.txt', target: '-26-11-1.txt' },
  { source: '-26-11-1.txt', target: '-26-12-1.txt' },
  { source: '-26-12-1.txt', target: '-26-18-2first.txt' },
  { source: '-26-12-1.txt', target: '-26-13-1.txt' },
  { source: '-26-13-1.txt', target: '-26-14-1.txt' },
  { source: '-26-14-1.txt', target: '-28-1-1.txt' },
].map(genId);

const EP_10_75_GROUPS: string[][] = [
  ['-24-1-1.txt'],
  ['-25-1-1.txt'],
  ['-26-1-1.txt', '-27-1-1.txt'],
];

export const CHAPTER_EDGES: Record<string, Edge[]> = {
  'EP. 10.5': EP_10_5,
  'EP. 10.75': EP_10_75,
};

export const CHAPTER_GROUPS: Record<string, string[][]> = {
  'EP. 10.5': EP_10_5_GROUPS,
  'EP. 10.75': EP_10_75_GROUPS,
};
