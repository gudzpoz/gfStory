import { liveQuery } from 'dexie';
import { onUnmounted, ref, shallowRef } from 'vue';
import { isStoryId, ProgressDatabase, type RecentStory } from '../../db/progress';

export interface ProgressNode {
  key?: string | number;
  disabled?: boolean;
  children?: ProgressNode[];
}

export function formatProgress(read: number, total: number): string {
  const count = `${read} / ${total}`;
  if (read === 0 || total === 0) return count;
  const percent = read === total ? 100 : Math.min(99.9, Math.round((read * 1000) / total) / 10);
  return `${count} · ${percent}%`;
}

export function storyKeys(nodes: ProgressNode[]): Set<string> {
  return new Set(nodes.flatMap((node): string[] => {
    if (node.children) return [...storyKeys(node.children)];
    const id = node.key;
    if (node.disabled || !isStoryId(id)) return [];
    return [id];
  }));
}
export function filterUnread<T extends ProgressNode>(nodes: T[], read: Set<string>): T[] {
  return nodes.flatMap((node): T[] => {
    if (node.children) {
      const children = filterUnread(node.children, read);
      return children.length ? [{ ...node, children }] : [];
    }
    return node.disabled || !isStoryId(node.key) || read.has(node.key) ? [] : [node];
  });
}

const db = new ProgressDatabase();
export function useReadingProgress() {
  const read = shallowRef(new Set<string>());
  const recent = shallowRef<RecentStory>();
  const ready = ref(false);
  const error = ref('');
  const busy = ref(false);
  const subscription = liveQuery(() => db.snapshot()).subscribe({
    next: (snapshot) => {
      read.value = new Set(snapshot.records.map((record) => record.id));
      recent.value = snapshot.recent;
      ready.value = true;
    },
    error: () => {
      ready.value = false;
      error.value = '无法读取进度，请检查浏览器是否允许网站保存数据。';
    },
  });
  onUnmounted(() => subscription.unsubscribe());
  async function run(action: () => Promise<void>): Promise<boolean> {
    error.value = '';
    try {
      await action();
      return true;
    } catch (e) {
      error.value = e instanceof Error ? e.message : '无法保存阅读进度';
      return false;
    }
  }
  async function setRead(id: string, state: boolean) {
    return run(() => db.setRead(id, state));
  }
  async function remember(id: string) {
    return run(() => db.remember(id));
  }
  async function exportBackup() {
    busy.value = true;
    await run(async () => {
      const backup = await db.snapshot();
      const url = URL.createObjectURL(new Blob([JSON.stringify(backup, null, 2)], {
        type: 'application/json',
      }));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'gfstory-progress.json';
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    busy.value = false;
  }
  async function importBackup(file: File) {
    busy.value = true;
    const ok = await run(async () => {
      if (file.size > 5 * 1024 * 1024) throw new Error('进度文件不能超过 5 MB');
      await db.restore(await file.text());
    });
    busy.value = false;
    return ok;
  }
  return {
    read, recent, ready, error, busy, setRead, remember, exportBackup, importBackup,
  };
}
