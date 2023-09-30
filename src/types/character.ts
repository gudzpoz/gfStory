export interface CharacterSprite {
  /**
   * Internal representation of the image, used by the database.
   */
  url: string;
  /**
   * The center of the image `[left, top]` in pixels.
   */
  center: readonly [number, number];
  /**
   * The scale.
   */
  scale: number;
}

export interface Character {
  /**
   * The default display name for the character.
   */
  name: string;
  /**
   * The sprites.
   */
  sprites: Record<string, CharacterSprite>;
}
