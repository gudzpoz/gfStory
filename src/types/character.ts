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
  /**
   * The id.
   */
  id: string;
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
  /**
   * The id.
   */
  id: string;
  /**
   * Readonly.
   */
  imported: boolean;
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

export type NamePath = readonly [string, string];

export type SpritePath = readonly [Character, CharacterSprite];

export function getNamePath(path: SpritePath): NamePath {
  return [path[0].name, path[1].name];
}

export function getNumericPath(path: NamePath, characters: Character[]): number[] {
  if (path.length !== 2) {
    return [];
  }
  const i = characters.findIndex((c) => c.name === path[0]);
  if (i === -1) {
    return [];
  }
  const character = characters[i];
  const j = character.sprites.findIndex((s) => s.name === path[1]);
  if (j === -1) {
    return [];
  }
  return [i, j];
}

export function getSprite(path: NamePath, characters: Character[]) {
  const [i, j] = getNumericPath(path, characters);
  if (i !== undefined && j !== undefined) {
    return characters[i].sprites[j];
  }
  return null;
}

export function labelCharactersWithIds(characters: Character[]): Character[] {
  let id = 0;
  return characters.map((c) => {
    id += 1;
    return {
      id: `${id}`,
      name: c.name,
      imported: false,
      sprites: c.sprites.map((s) => {
        id += 1;
        return {
          ...s,
          id: `${id}`,
        };
      }),
    };
  });
}
