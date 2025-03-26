import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'parseHtml'
})
export class ParseHtmlPipe implements PipeTransform {
  transform(value: string): string {
    if (value) {
      const regex = /<br\s*\/?>/gi;
      return this.limitTextToLines(value.replace(regex, '\n').replace(/\n{2,}/g, '\n'), 3);
    } else {
      return '';
    }
  }

  private limitTextToLines(value: string, maxLines: number): string {
    const lines = value.split('\n');
    if(lines.length > maxLines) {
      let truncatedLines = lines.slice(0, maxLines);
      truncatedLines.push('......')
      return truncatedLines.join('\n');
    } else {
      const truncatedLines = lines.slice(0, maxLines);
      return truncatedLines.join('\n');
    }
  }
}
