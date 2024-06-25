import { StoryRunner } from '@brocatel/mdc';

import type { Character, CharacterSprite } from '../types/character';

export type Tags = {
  classes?: string,

  narrator?: string,
  color?: string,

  background?: string,
  style?: string,

  audio?: string,

  se?: string;

  sprites?: string,
  remote?: string,
};

export interface SpriteImage extends CharacterSprite {
  image: HTMLImageElement;
}

function fetchSpriteImage(character: string, s: CharacterSprite) {
  const image = new Image();
  return new Promise<[string, SpriteImage]>((resolve) => {
    image.src = s.url;
    const sprite = s as SpriteImage;
    sprite.image = image;
    const result = [`${character}/${s.name}`, sprite] as [string, SpriteImage];
    image.onload = () => resolve(result);
    image.onerror = () => {
      if (image.src !== '') {
        image.classList.add('failed');
      }
      resolve(result);
    };
  });
}

export class StoryInterpreter {
  story: StoryRunner;

  characters: Character[];

  resources: string[];

  preloadedImages: Record<string, SpriteImage>;

  constructor() {
    this.characters = [];
    this.resources = [];
    this.preloadedImages = {};

    this.story = new StoryRunner();
  }

  async reload(chunk: string, preload: boolean = true) {
    await this.story.loadStory(chunk, undefined, {
      defineCharacters: (characters: string) => {
        this.characters = JSON.parse(characters);
        this.characters.forEach((character) => {
          const c = character;
          c.id = c.name;
          c.sprites.forEach((sprite) => {
            const s = sprite;
            s.id = `${c.name}/${s.name}`;
          });
        });
      },
      preloadResources: (resources: string) => {
        this.resources = JSON.parse(resources);
      },
    });
    if (preload) {
      await this.preloadResources();
    }
  }

  getImage(s: string): SpriteImage {
    return this.preloadedImages[s];
  }

  async preloadResources() {
    this.preloadedImages = {};
    const images = this.characters.flatMap((c) => c.sprites.map(
      (s) => fetchSpriteImage(c.name, s),
    ));
    this.preloadedImages = Object.fromEntries(await Promise.all(images.concat(
      this.resources.map((s) => fetchSpriteImage(s, {
        name: '',
        url: s,
        center: [0, 0],
        scale: 0,
        id: '',
      })),
    )));
  }

  next(option?: number) {
    if (!this.story.isLoaded()) {
      return null;
    }
    const line = this.story.next(option);
    return line;
  }
}
