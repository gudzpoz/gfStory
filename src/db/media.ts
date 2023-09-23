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

  constructor() {
    super('media');
    this.version(1).stores(Object.fromEntries(MEDIA_TYPES.map((type) => [type, 'name, blob'])));
  }

  liveQueryAll(type: typeof MEDIA_TYPES[number]) {
    return liveQuery(async () => this[type].toArray());
  }

  async toDataUrl(s: string) {
    const [type, name] = s.split(':', 2);
    const media = await this[type as (typeof MEDIA_TYPES)[number]].where('name').equals(name).first();
    return (media ? URL.createObjectURL(media.blob) : '');
  }
}

export const db = new MediaDatabase();
