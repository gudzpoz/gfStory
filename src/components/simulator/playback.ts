import type { Chapter } from '../../types/assets';
import { isStoryId } from '../../db/progress';

export default function nextStory(
  chapters: readonly Chapter[],
  current: string,
  read: Set<string>,
  skipRead: boolean,
): string | undefined {
  const sequences = chapters.map((chapter) => [...new Set(
    chapter.stories.flatMap((story) => story.files.map(
      (file) => (typeof file === 'string' ? file : file[0]),
    )).filter(isStoryId),
  )]);
  const sequence = sequences.find((files) => files.includes(current));
  if (!sequence) return undefined;
  return sequence.slice(sequence.indexOf(current) + 1)
    .find((id) => !skipRead || !read.has(id));
}
