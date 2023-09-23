export const LINE_TYPES = ['text', 'scene'] as const;

interface LineType {
  type: typeof LINE_TYPES[number];
  id: string;
  noSkipping: boolean;
}

export interface TextLine extends LineType {
  type: 'text';
  narrator: string;
  text: string;
  narratorColor: string;
}

export interface SceneLine extends LineType {
  type: 'scene';
  scene: 'background' | 'sprite';
  image: string;
  style: string;
}

export type Line = TextLine | SceneLine;

let id = 0;
export function nextId() {
  id += 1;
  return id;
}

export function defaultLine(): Line {
  return {
    type: 'text',
    id: `${nextId()}`,
    noSkipping: false,
    narrator: '',
    text: '',
    narratorColor: '#ffffff',
  };
}
