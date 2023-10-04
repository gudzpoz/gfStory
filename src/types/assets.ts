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
