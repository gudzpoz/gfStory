import type { Character } from './character';

export const LINE_TYPES = ['text', 'scene'] as const;

interface LineType {
  type: typeof LINE_TYPES[number];
  id: string;
}

export interface TextLine extends LineType {
  type: 'text';
  narrator: string;
  text: string;
  narratorColor: string;
  sprites: string[];
}

export interface SceneLine extends LineType {
  type: 'scene';
  scene: 'background' | 'audio';
  media: string;
  style: string;
}

export type Line = TextLine | SceneLine;

let id = 0;
export function initUniqueId(previous: Line[]) {
  id = previous.map((line) => parseInt(line.id, 10)).reduce((a, b) => Math.max(a, b));
}
export function nextId() {
  id += 1;
  return `${id}`;
}

export function defaultLine(): TextLine {
  return {
    type: 'text',
    id: nextId(),
    narrator: '',
    text: '',
    narratorColor: '#ffffff',
    sprites: [],
  };
}

export interface GfStory {
  characters: Character[];
  lines: Line[];
}
