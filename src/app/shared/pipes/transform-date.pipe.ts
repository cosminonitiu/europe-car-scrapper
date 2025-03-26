import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'transformDate'
})
export class TransformDatePipe implements PipeTransform {
  transform(value: string): string {
    if (value) {
      const date = new Date(value);
      const day = date.getDate();
      const month = date.toLocaleString('default', { month: 'short' });
      const year = date.getFullYear();
      return `${day} ${month}, ${year}`;
    } else {
      return '';
    }
  }
}
