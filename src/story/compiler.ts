import { BrocatelCompiler } from '@brocatel/mdc';

import { type Line } from '../types/lines';

export function linesToMarkdown(lines: Line[]) {
  const segments = lines.map((line) => {
    switch (line.type) {
      case 'text':
        return `[narrator] [color: ${line.narratorColor}] ${line.narrator}

${line.text}`;
      case 'scene':
        return `[${line.scene}] [style: ${line.style}] ${line.image}`;
      default:
        return '';
    }
  });
  return `${segments.join('\n\n')}\n`;
}

const compiler = new BrocatelCompiler({});

export async function compileMarkdown(markdown: string) {
  const file = await compiler.compileAll('main', async () => markdown);
  return file.toString();
}
