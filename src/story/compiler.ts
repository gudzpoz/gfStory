import { BrocatelCompiler } from '@brocatel/mdc';

import { type Character } from '../types/character';
import { type GfStory } from '../types/lines';
import { db } from '../db/media';

function resolveBlobImage(s: string) {
  return db.toDataUrl(s);
}

function exportCharacters(characters: Character[]) {
  const json = JSON.stringify(characters);
  return `\`\`\`lua global
print.defineCharacters(${JSON.stringify(json)})
\`\`\``;
}

function exportPreloaded(urls: string[]) {
  const content = JSON.stringify(urls);
  return `\`\`\`lua global
print.preloadResources(${JSON.stringify(content)})
\`\`\`
`;
}

export async function linesToMarkdown(story: GfStory, resolveImage = resolveBlobImage) {
  const preloaded: string[] = [];
  const characters: Character[] = await Promise.all(story.characters.map(async (c) => ({
    name: c.name,
    sprites: await Promise.all(c.sprites.map(async (s) => {
      const copy = { ...s };
      copy.url = await resolveImage(copy.url);
      return copy;
    })),
  })));
  const segments = await Promise.all(story.lines.map(async (line) => {
    switch (line.type) {
      case 'text': {
        return `:sprites[${line.sprites.join('|')}] \
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

const compiler = new BrocatelCompiler({});

export async function compileMarkdown(markdown: string) {
  const file = await compiler.compileAll('main', async () => markdown);
  return file.toString();
}
