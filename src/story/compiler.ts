import { BrocatelCompiler } from '@brocatel/mdc';

import { type Character, type CharacterSprite } from '../types/character';
import { type GfStory, type SceneLine, type TextLine } from '../types/lines';
import { db } from '../db/media';

export type CompactSprite = Omit<CharacterSprite, 'id'> & { id?: unknown };
export type CompactCharacter = Omit<Omit<Omit<Character, 'sprites'>, 'imported'> & { sprites: CompactSprite[] }, 'id'>;

function resolveBlobImage(s: string) {
  return db.toDataUrl(s);
}

function exportCharacters(characters: CompactCharacter[]) {
  const json = JSON.stringify(characters);
  return `\`\`\`lua global
extern.defineCharacters(${JSON.stringify(json)})
\`\`\``;
}

function exportPreloaded(urls: string[]) {
  const content = JSON.stringify(urls);
  return `\`\`\`lua global
extern.preloadResources(${JSON.stringify(content)})
\`\`\`
`;
}

export async function linesToMarkdown(story: GfStory, resolveImage = resolveBlobImage) {
  const preloaded: string[] = [];
  const characters: CompactCharacter[] = await Promise.all(story.characters.map(async (c) => ({
    name: c.name,
    sprites: await Promise.all(c.sprites.map(async (s) => {
      const copy: CompactSprite = { ...s };
      delete copy.id;
      copy.url = await resolveImage(copy.url);
      return copy;
    })),
  })));
  const segments = await Promise.all(story.lines.map(async (line) => {
    switch (line.type) {
      case 'text': {
        return `:sprites[${line.sprites.join('|')}] \
:remote[${Object.entries(line.remote).filter((e) => e[1]).map((e) => e[0]).join('|')}] \
:narrator[${line.narrator}] \
:color[${line.narratorColor}] \
${line.text}`;
      }
      case 'scene': {
        const url = await resolveImage(line.media);
        preloaded.push(url);
        return `:${line.scene}[${line.style}] ${url}`;
      }
      default:
        return '';
    }
  }));
  return `
${exportCharacters(characters)}

${exportPreloaded(preloaded)}

${segments.join('\n\n')}
`;
}

function parseLine(line: string) {
  const tags: Record<string, string> = {};
  let l = line;
  while (l.startsWith(':')) {
    const result = /^:(\w+)\[([^\]]*)\]\s+/.exec(l);
    if (!result) {
      break;
    }
    l = l.substring(result[0].length).trim();
    // eslint-disable-next-line prefer-destructuring
    tags[result[1]] = result[2];
  }
  const type = ['background', 'se', 'audio'].find((t) => tags[t] !== undefined);
  if (type) {
    return {
      type: 'scene',
      scene: type,
      media: l.replace(/\\/g, ''),
      style: tags[type],
    } as SceneLine;
  }
  return {
    type: 'text',
    remote: Object.fromEntries((tags.remote ?? '').split('|').filter((s) => s !== '')
      .map((s) => [s, true])),
    narrator: tags.narrator ?? '',
    narratorColor: tags.color ?? '',
    sprites: (tags.sprites ?? '').split('|').filter((s) => s !== ''),
    text: l.replace(/\\/g, ''),
  } as TextLine;
}

export function importMarkdownString(markdown: string) {
  const markdownLines = markdown.split('\n');
  const characterLine = markdownLines.find((s) => s.startsWith('extern.defineCharacters'));
  const resourceLine = markdownLines.find((s) => s.startsWith('extern.preloadResources'));
  if (!characterLine || !resourceLine) {
    return null;
  }
  const characters = (JSON.parse(JSON.parse(
    characterLine.substring('extern.defineCharacters'.length + 1, characterLine.length - 1),
  )) as CompactCharacter[]).filter((s) => s.name !== '');
  const resources = JSON.parse(JSON.parse(
    resourceLine.substring('extern.preloadResources'.length + 1, resourceLine.length - 1),
  )) as string[];
  const lines = markdownLines
    .map((s) => s.replace(/.*`/g, ''))
    .filter((s) => s.startsWith(':'))
    .map(parseLine);
  return { lines, characters, resources };
}

const compiler = new BrocatelCompiler({});

export async function compileMarkdown(markdown: string) {
  const file = await compiler.compileAll('main', async () => markdown);
  return file.toString();
}
