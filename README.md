# Simple Geometry

Personal notes on geometry, topology, and computational algorithms. Built as a static site in the style of a mathematical typeset book.

**Live site:** https://akulinich.github.io/Simple_Geometry

---

## Stack

- **[Astro](https://astro.build)** — static site generator with Content Collections
- **[KaTeX](https://katex.org)** — math rendering via `remark-math` + `rehype-katex`
- **EB Garamond** — book-style serif font
- **GitHub Actions** — automatic deployment on push to `main`

## Structure

```
src/
  content/articles/
    ru/        ← Russian articles
    en/        ← English translations
  pages/
    ru/        ← Russian pages
    en/        ← English pages
  i18n/ui.ts  ← static UI text
public/images/ ← article images (shared between languages)
tools/
  import_tool.py  ← Obsidian import desktop app
```

## Running locally

```bash
npm install
npm run dev
```