import 'fake-indexeddb/auto';
import {
  afterEach, describe, expect, it, vi,
} from 'vitest';
import { ProgressDatabase, parseProgressBackup } from '../src/db/progress';
import { filterUnread, storyKeys } from '../src/components/simulator/progress';

const databases: ProgressDatabase[] = [];
function database(name = `progress-test-${databases.length}`) {
  const db = new ProgressDatabase(name);
  databases.push(db);
  return db;
}
afterEach(async () => {
  await Promise.all(databases.map((db) => db.delete()));
  databases.length = 0;
});
function backup(records: { id: string; readAt: string }[]) {
  return JSON.stringify({ format: 'gfstory-reading-progress', version: 1, records });
}
describe('reading progress', () => {
  it('persists independent read states and recent story across reopening', async () => {
    const db = database();
    await db.setRead('-1-1.txt', true);
    await db.setRead('-1-3.txt', true);
    const original = await db.records.get('-1-3.txt');
    await db.setRead('-1-3.txt', true);
    expect(await db.records.get('-1-3.txt')).toEqual(original);
    await db.setRead('-1-1.txt', false);
    await db.remember('-1-2.txt');
    const { name } = db;
    db.close();
    const reopened = database(name);
    const snapshot = await reopened.snapshot();
    expect(snapshot.records.map((r) => r.id)).toEqual(['-1-3.txt']);
    expect(snapshot.recent?.id).toBe('-1-2.txt');
    expect(await reopened.records.get('-1-2.txt')).toBeUndefined();
  });

  it('merges backups without removing local or unknown story records', async () => {
    const db = database();
    await db.setRead('-local.txt', true);
    await db.records.put({ id: '-shared.txt', readAt: '2026-10-11T00:00:00.000Z' });
    await db.restore(backup([
      { id: '-shared.txt', readAt: '2020-01-01T00:00:00.000Z' },
      { id: 'battleavg/-unknown.txt', readAt: '2025-01-01T00:00:00.000Z' },
    ]));
    expect((await db.records.get('-shared.txt'))?.readAt).toBe('2026-10-11T00:00:00.000Z');
    expect((await db.snapshot()).records).toHaveLength(3);
    const copy = database();
    await copy.restore(JSON.stringify(await db.snapshot()));
    expect(await copy.snapshot()).toEqual(await db.snapshot());
  });

  it('rejects the entire malformed backup before changing stored progress', async () => {
    const db = database();
    await db.setRead('-old.txt', true);
    await db.remember('-old.txt');
    const before = await db.snapshot();
    const valid = { id: '-new.txt', readAt: '2025-01-01T00:00:00.000Z' };
    await Promise.all([
      { id: '../bad.txt', readAt: valid.readAt },
      { id: '-bad.txt', readAt: 'yesterday' },
      valid,
    ].map(async (invalid) => {
      await expect(db.restore(backup([valid, invalid]))).rejects.toThrow();
      expect(await db.snapshot()).toEqual(before);
    }));
    expect(() => parseProgressBackup(JSON.stringify({
      format: 'gfstory-reading-progress', version: 2, records: [],
    }))).toThrow();
  });

  it('rolls back all imported records if a database write fails', async () => {
    const db = database();
    await db.setRead('-old.txt', true);
    await db.remember('-old.txt');
    const before = await db.snapshot();
    const put = vi.spyOn(db.metadata, 'put').mockRejectedValueOnce(new Error('disk full'));
    await expect(db.restore(JSON.stringify({
      format: 'gfstory-reading-progress',
      version: 1,
      records: [{ id: '-new.txt', readAt: '2025-01-01T00:00:00.000Z' }],
      recent: { id: '-new.txt', openedAt: '2099-01-01T00:00:00.000Z' },
    }))).rejects.toThrow('disk full');
    put.mockRestore();
    expect(await db.snapshot()).toEqual(before);
  });

  it('preserves original script filenames containing spaces', async () => {
    const db = database();
    const id = '-44-t2-3-ex .txt';
    await db.setRead(id, true);
    const saved = await db.snapshot();
    const copy = database();
    await copy.restore(JSON.stringify(saved));
    expect((await copy.records.get(id))?.id).toBe(id);
    expect([...storyKeys([{ key: id }])]).toEqual([id]);
  });

  it('counts unique scripts and filters unread leaves without marking earlier scripts', () => {
    const nodes = [{
      key: 'event',
      children: [
        { key: '-1.txt' }, { key: '-2.txt' },
        { key: 'split', children: [{ key: '-2.txt' }, { key: '-3.txt' }] },
        { key: 'map|1' }, { key: '-empty.txt', disabled: true },
      ],
    }];
    const read = new Set(['-2.txt']);
    expect([...storyKeys(nodes)]).toEqual(['-1.txt', '-2.txt', '-3.txt']);
    expect([...storyKeys(filterUnread(nodes, read))]).toEqual(['-1.txt', '-3.txt']);
    expect(filterUnread(nodes, new Set(storyKeys(nodes)))).toEqual([]);
  });
});
