import { getCollection } from 'astro:content';
import { ui, type Lang } from '../i18n/ui';

export function formatDate(date: Date, lang: Lang, month: 'long' | 'short' = 'long'): string {
  return date.toLocaleDateString(ui[lang]['article.date'], { year: 'numeric', month, day: 'numeric' });
}

export async function getArticlesForLang(lang: Lang) {
  return (await getCollection('articles', ({ data, id }) => !data.draft && id.startsWith(`${lang}/`)))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}
