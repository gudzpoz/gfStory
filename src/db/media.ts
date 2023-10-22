import Dexie, { liveQuery, type Table } from 'dexie';
import { ref, type Ref } from 'vue';

export const MEDIA_TYPES = ['audio', 'background', 'sprite'] as const;

export const ACCEPTED: Record<typeof MEDIA_TYPES[number], string> = {
  audio: 'audio/*',
  background: 'image/*',
  sprite: 'image/*',
};

export interface RawMedia {
  name: string;
  /**
   * Either a local resource (blob) or a remote resource (link).
   */
  blob: Blob | string;
}

export interface Media extends RawMedia {
  type: typeof MEDIA_TYPES[number];
  value: string;
}

export type MediaUrl = string;

export class MediaDatabase extends Dexie {
  private audio!: Table<RawMedia>;

  private background!: Table<RawMedia>;

  private sprite!: Table<RawMedia>;

  private cache: Record<typeof MEDIA_TYPES[number], Record<MediaUrl, string>>;

  private refs: Record<typeof MEDIA_TYPES[number], Ref<Media[]>>;

  constructor() {
    super('media');
    this.version(1).stores(Object.fromEntries(MEDIA_TYPES.map((type) => [type, 'name, blob'])));
    this.cache = { audio: {}, background: {}, sprite: {} };
    this.refs = {
      audio: this.liveQueryAll('audio'),
      background: this.liveQueryAll('background'),
      sprite: this.liveQueryAll('sprite'),
    };
  }

  getMediaItems(type: typeof MEDIA_TYPES[number]) {
    return this.refs[type];
  }

  // eslint-disable-next-line class-methods-use-this
  getMediaUrl(type: typeof MEDIA_TYPES[number], name: string): MediaUrl {
    return `${type}:${name}`;
  }

  /**
   * Calls the listener whenever the database updates.
   *
   * @param type the type of media changes to listen to
   * @param listener the callback
   * @returns a handle that cancels the subscription when called
   */
  private liveQueryAll(type: typeof MEDIA_TYPES[number]) {
    const items = ref<Media[]>([]);
    liveQuery(async () => this[type].toArray())
      .subscribe((raw) => {
        items.value = raw.map((r) => ({
          type,
          value: this.getMediaUrl(type, r.name),
          ...r,
        }));
      });
    return items;
  }

  getMediaDataUrl(type: typeof MEDIA_TYPES[number], media: RawMedia) {
    if (typeof media.blob === 'string') {
      return media.blob;
    }
    const url = URL.createObjectURL(media.blob);
    this.cache[type][media.name] = url;
    return url;
  }

  // eslint-disable-next-line class-methods-use-this
  splitMediaUrl(s: MediaUrl): [typeof MEDIA_TYPES[number], string] {
    return s.split(':', 2) as [typeof MEDIA_TYPES[number], string];
  }

  // eslint-disable-next-line class-methods-use-this
  isMediaUrl(s: MediaUrl) {
    return !s.startsWith('/') && s.includes(':');
  }

  async toDataUrl(s: MediaUrl) {
    if (!this.isMediaUrl(s)) {
      return s;
    }
    const [t, name] = this.splitMediaUrl(s);
    const type = t as typeof MEDIA_TYPES[number];
    if (this.cache[type][name]) {
      return this.cache[type][name];
    }
    const media = await this[type].where('name').equals(name).first();
    if (!media) {
      return '';
    }
    return this.getMediaDataUrl(type, media);
  }

  deleteMedia(type: typeof MEDIA_TYPES[number], name: string) {
    delete this.cache[type][name];
    return this[type].delete(name);
  }
}

export const db = new MediaDatabase();
