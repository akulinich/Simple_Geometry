import { defineConfig } from 'astro/config';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkWikiLink from 'remark-wiki-link';
import remarkObsidianImage from './src/plugins/remark-obsidian-image.js';

export default defineConfig({
  site: 'https://akulinich.github.io',
  base: '/Simple_Geometry',
  markdown: {
    remarkPlugins: [
      remarkMath,
      [remarkWikiLink, {
        pageResolver: (name) => [name.toLowerCase().replace(/ /g, '-')],
        // hardcoded base — if repo is renamed, update here too
        hrefTemplate: (permalink) => `/Simple_Geometry/articles/${permalink}`,
      }],
      remarkObsidianImage,
    ],
    rehypePlugins: [
      rehypeKatex,
    ],
  },
});
