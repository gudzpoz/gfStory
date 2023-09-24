import { BrocatelCompiler } from '@brocatel/mdc';

import { type Line } from '../types/lines';
import { db } from '../db/media';

function resolveBlobImage(s: string) {
  return db.toDataUrl(s);
}

export async function linesToMarkdown(lines: Line[], resolveImage = resolveBlobImage) {
  const segments = await Promise.all(lines.map(async (line) => {
    switch (line.type) {
      case 'text': {
        const sprites = (await Promise.all(
          line.sprites.map(resolveImage),
        ));
        return `[sprites] ${sprites.join('|')}
        
[narrator] [color:${line.narratorColor}] ${line.narrator}

${line.text}`;
      }
      case 'scene':
        return `[${line.scene}] [style:${line.style}] ${await resolveImage(line.image)}`;
      default:
        return '';
    }
  }));
  return `${segments.join('\n\n')}\n`;
}

const compiler = new BrocatelCompiler({});

export async function compileMarkdown(markdown: string) {
  const file = await compiler.compileAll('main', async () => markdown);
  return file.toString();
}
