export interface CharacterSprite {
  /**
   * The sprite name.
   */
  name: string;
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
  sprites: CharacterSprite[];
}

function isUnique(name: string, objects: { name: string }[], limit: number) {
  return objects.filter((o) => o.name === name).length <= limit;
}

export function getUniqueName(name: string, objects: { name: string }[], limit = 1) {
  if (isUnique(name, objects, limit)) {
    return undefined;
  }
  let i = 1;
  let unique;
  do {
    unique = `${name}_${i}`;
    i += 1;
  } while (!isUnique(unique, objects, limit));
  return unique;
}
