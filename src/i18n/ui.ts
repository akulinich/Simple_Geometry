export const ui = {
  en: {
    'nav.articles': 'Articles',
    'nav.about': 'About',
    'home.latest': 'Recent articles',
    'home.intro': 'Hi. My name is Sasha. I work on software related to geometry, and in my free time I read books and articles on mathematics and algorithms. This site is my personal collection of notes and ideas that I found interesting.',
    'articles.heading': 'Articles',
    'meta.description': 'Notes on geometry',
    'article.date': 'en-US',
  },
  ru: {
    'nav.articles': 'Статьи',
    'nav.about': 'Об авторе',
    'home.latest': 'Последние статьи',
    'home.intro': 'Привет. Меня зовут Саша. Я занимаюсь разработкой программ, связанных с геометрией. В свободное время читаю книги и статьи по математике и алгоритмам. Этот сайт — мой личный сборник заметок и идей, которые показались мне интересными.',
    'articles.heading': 'Статьи',
    'meta.description': 'Заметки о геометрии',
    'article.date': 'ru-RU',
  },
} as const;

export type Lang = keyof typeof ui;
export type TranslationKey = keyof typeof ui['en'];

export function useTranslations(lang: Lang) {
  return (key: TranslationKey): string => ui[lang][key];
}
