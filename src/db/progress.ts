import Dexie, { type Table } from 'dexie';

export interface ReadRecord {
  id: string;
  readAt: string;
}
export interface RecentStory {
  id: string;
  openedAt: string;
}
export interface ProgressBackup {
  format: 'gfstory-reading-progress';
  version: 1;
  records: ReadRecord[];
  recent?: RecentStory;
}

export function isStoryId(value: unknown): value is string {
  return typeof value === 'string' && value.length <= 512
    && /^[A-Za-z0-9_./ -]+\.txt$/.test(value)
    && !value.startsWith('/') && !value.split('/').includes('..');
}
function isTimestamp(value: unknown): value is string {
  return typeof value === 'string' && Number.isFinite(Date.parse(value))
    && new Date(value).toISOString() === value;
}
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('进度文件格式无效');
  }
  return value as Record<string, unknown>;
}
export function parseProgressBackup(input: string): ProgressBackup {
  if (new TextEncoder().encode(input).length > 5 * 1024 * 1024) {
    throw new Error('进度文件不能超过 5 MB');
  }
  const data = object(JSON.parse(input));
  if (data.format !== 'gfstory-reading-progress' || data.version !== 1
    || !Array.isArray(data.records) || data.records.length > 100000) {
    throw new Error('进度文件格式或版本不支持');
  }
  const seen = new Set<string>();
  const records = data.records.map((item: unknown) => {
    const record = object(item);
    if (!isStoryId(record.id) || !isTimestamp(record.readAt) || seen.has(record.id)) {
      throw new Error('进度文件包含无效或重复的记录');
    }
    seen.add(record.id);
    return { id: record.id, readAt: record.readAt };
  });
  let recent: RecentStory | undefined;
  if (data.recent !== undefined) {
    const item = object(data.recent);
    if (!isStoryId(item.id) || !isTimestamp(item.openedAt)) {
      throw new Error('最近阅读记录无效');
    }
    recent = { id: item.id, openedAt: item.openedAt };
  }
  return {
    format: 'gfstory-reading-progress', version: 1, records, recent,
  };
}

export class ProgressDatabase extends Dexie {
  records!: Table<ReadRecord, string>;

  metadata!: Table<{ key: string; value: RecentStory }, string>;

  constructor(name = 'gfstory-reading-progress') {
    super(name);
    this.version(1).stores({ records: 'id', metadata: 'key' });
  }

  async setRead(id: string, read: boolean) {
    if (!isStoryId(id)) throw new Error('剧情编号无效');
    if (read) {
      await this.transaction('rw', this.records, async () => {
        if (!await this.records.get(id)) {
          await this.records.put({ id, readAt: new Date().toISOString() });
        }
      });
    } else {
      await this.records.delete(id);
    }
  }

  async remember(id: string) {
    if (!isStoryId(id)) throw new Error('剧情编号无效');
    await this.metadata.put({
      key: 'recent', value: { id, openedAt: new Date().toISOString() },
    });
  }

  async snapshot(): Promise<ProgressBackup> {
    return this.transaction('r', this.records, this.metadata, async () => ({
      format: 'gfstory-reading-progress' as const,
      version: 1 as const,
      records: await this.records.toArray(),
      recent: (await this.metadata.get('recent'))?.value,
    }));
  }

  async restore(input: string) {
    // Validate the entire backup before opening the write transaction.
    const backup = parseProgressBackup(input);
    await this.transaction('rw', this.records, this.metadata, async () => {
      const current = new Map((await this.records.toArray()).map((r) => [r.id, r]));
      const additions = backup.records.filter((record) => {
        const old = current.get(record.id);
        return !old || old.readAt < record.readAt;
      });
      await this.records.bulkPut(additions);
      const recent = (await this.metadata.get('recent'))?.value;
      if (backup.recent && (!recent || recent.openedAt < backup.recent.openedAt)) {
        await this.metadata.put({ key: 'recent', value: backup.recent });
      }
    });
  }
}
