import { ClassicEditor as ClassicEditorBase } from '@ckeditor/ckeditor5-editor-classic';
import { Alignment } from '@ckeditor/ckeditor5-alignment';
import { Bold, Code, Italic } from '@ckeditor/ckeditor5-basic-styles';
import { Essentials } from '@ckeditor/ckeditor5-essentials';
import {
  FontBackgroundColor, FontColor, FontFamily, FontSize,
} from '@ckeditor/ckeditor5-font';
import { Paragraph } from '@ckeditor/ckeditor5-paragraph';

export default class ClassicEditor extends ClassicEditorBase {
  public static override builtinPlugins = [
    Alignment,
    Bold,
    Code,
    Essentials,
    FontBackgroundColor,
    FontColor,
    FontFamily,
    FontSize,
    Italic,
    Paragraph,
  ];

  public static override defaultConfig = {
    toolbar: {
      items: [
        'fontSize',
        'fontFamily',
        'fontColor',
        'fontBackgroundColor',
        '|',
        'bold',
        'italic',
        'code',
        '|',
        'alignment',
        '|',
        'undo',
        'redo',
      ],
    },
    language: 'zh-cn',
  };
}
