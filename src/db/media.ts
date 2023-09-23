import Dexie, { liveQuery, type Table } from 'dexie';

export const MEDIA_TYPES = ['audio', 'background', 'sprite'] as const;

export const ACCEPTED: { [key in typeof MEDIA_TYPES[number]]: string } = {
  audio: 'audio/*',
  background: 'image/*',
  sprite: 'image/*',
};

export interface Media {
  name: string;
  blob: Blob;
}

export class MediaDatabase extends Dexie {
  audio!: Table<Media>;

  background!: Table<Media>;

  sprite!: Table<Media>;

  cache: { [key in typeof MEDIA_TYPES[number]]: { [key: string]: string } };

  constructor() {
    super('media');
    this.version(1).stores(Object.fromEntries(MEDIA_TYPES.map((type) => [type, 'name, blob'])));
    this.cache = { audio: {}, background: {}, sprite: {} };
  }

  liveQueryAll(type: typeof MEDIA_TYPES[number]) {
    return liveQuery(async () => this[type].toArray());
  }

  async toDataUrl(s: string) {
    const [t, name] = s.split(':', 2);
    const type = t as typeof MEDIA_TYPES[number];
    if (this.cache[type][name]) {
      return this.cache[type][name];
    }
    const media = await this[type].where('name').equals(name).first();
    if (!media) {
      return '';
    }
    const url = URL.createObjectURL(media.blob);
    this.cache[type][name] = url;
    return url;
  }

  deleteMedia(type: typeof MEDIA_TYPES[number], name: string) {
    delete this.cache[type][name];
    return this[type].delete(name);
  }
}

export const db = new MediaDatabase();
