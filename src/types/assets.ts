import { MEDIA_TYPES } from '../db/media';

export type AudioInfo = {
  [audioIdentifier: string]: string;
};

export type BackgroundInfo = {
  [backgroundIdentifier: string]: string;
};

export interface GfSpriteInfo {
  path: string;
  scale: number;
  offset: readonly [number, number];
}

export type GfCharacterInfo = {
  [id: string]: GfSpriteInfo;
};

export type GfCharactersInfo = {
  [identifier: string]: GfCharacterInfo;
};

export const IMAGE_PATH_PREFIX = '/images/';
export const AUDIO_PATH_PREFIX = '/audio/';
export const STORY_PATH_PREFIX = '/stories/';

export function getUrlType(s: string): typeof MEDIA_TYPES[number] {
  if (s.startsWith(IMAGE_PATH_PREFIX)) {
    return 'background';
  }
  if (s.startsWith(AUDIO_PATH_PREFIX)) {
    return 'audio';
  }
  if (s.startsWith('background/')) {
    return 'background';
  }
  if (s.startsWith('bgm/') || s.startsWith('se/')) {
    return 'audio';
  }
  return 'sprite';
}

export type ChapterType = (
  'main' | 'event' | 'colab' | 'bonding' | 'upgrading'
  | 'anniversary' | 'anniversary6' | 'anniversary5' | 'anniversary4' | 'skin'
  | 'help'
);
export type Story = {
  name: string;
  description: string;
  files: (string | string[])[];
};
export type Chapter = {
  name: string;
  description: string;
  stories: Story[];
};
export type GfChaptersInfo = Record<ChapterType, Chapter[]>;
