import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import difflib
import json
import os
import re
import shutil
import threading
import subprocess
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / 'settings.json'
PROJECT_ROOT  = Path(__file__).parent.parent
ARTICLES_DIR  = PROJECT_ROOT / 'src' / 'content' / 'articles'
RU_DIR        = ARTICLES_DIR / 'ru'
EN_DIR        = ARTICLES_DIR / 'en'
IMAGES_DIR    = PROJECT_ROOT / 'public' / 'images'


# ─── Settings ────────────────────────────────────────────────────────────────

def load_settings():
    try:
        with open(SETTINGS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'notes_folder': '', 'images_folder': ''}


def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


# ─── Markdown helpers ─────────────────────────────────────────────────────────

def find_images_in_md(content):
    images = set()
    for m in re.finditer(r'!\[\[([^\]|]+)', content):
        images.add(m.group(1).strip())
    for m in re.finditer(r'!\[.*?\]\(([^)]+)\)', content):
        p = m.group(1)
        if not p.startswith('http'):
            images.add(Path(p).name)
    return images


# ─── Frontmatter helpers ──────────────────────────────────────────────────────

def read_frontmatter(path):
    """Return dict of simple key: value frontmatter fields."""
    try:
        content = path.read_text(encoding='utf-8')
        m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not m:
            return {}
        result = {}
        for line in m.group(1).splitlines():
            if ':' in line and not line.startswith(' '):
                k, _, v = line.partition(':')
                result[k.strip()] = v.strip().strip('"\'')
        return result
    except Exception:
        return {}


def set_frontmatter_field(path, field, value):
    """Add or update a scalar field in YAML frontmatter."""
    content = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)

    def quoted(v):
        if any(c in str(v) for c in ':#{}[]|>&*!,?@`"\''):
            return f'"{v}"'
        return str(v)

    if not m:
        path.write_text(f'---\n{field}: {quoted(value)}\n---\n\n{content}',
                        encoding='utf-8', newline='\n')
        return

    yaml_block = m.group(1)
    rest = content[m.end():]
    pat = re.compile(rf'^{re.escape(field)}:.*$', re.MULTILINE)
    if pat.search(yaml_block):
        yaml_block = pat.sub(f'{field}: {quoted(value)}', yaml_block)
    else:
        yaml_block = f'{field}: {quoted(value)}\n{yaml_block}'
    path.write_text(f'---\n{yaml_block}\n---{rest}', encoding='utf-8', newline='\n')


# ─── Article list ─────────────────────────────────────────────────────────────

def get_all_articles(notes_folder, id_map, path_to_id):
    """
    id_map     : {id → obsidian_rel_path}
    path_to_id : {obsidian_rel_path → id}
    Returns list of (display_path, status, id_or_None).
    status: 'new' | 'imported' | 'site_only'
    """
    ru_ids = {f.stem for f in RU_DIR.glob('*.md')} if RU_DIR.exists() else set()
    result = []

    if notes_folder and Path(notes_folder).exists():
        root = Path(notes_folder)
        for f in root.rglob('*.md'):
            rel = str(f.relative_to(root))
            aid = path_to_id.get(rel)
            status = 'imported' if aid and aid in ru_ids else 'new'
            result.append((rel, status, aid))

    if RU_DIR.exists():
        for f in RU_DIR.glob('*.md'):
            if f.stem not in id_map:
                result.append((f.name, 'site_only', f.stem))

    return sorted(result, key=lambda x: x[0])


# ─── Pipeline dialog ──────────────────────────────────────────────────────────

class PipelineDialog(tk.Toplevel):
    STEP_DEFS = [
        (0, 'Предобработка', 'Убрать фон картинок'),
        (1, 'Предобработка', 'Заменить е → ё'),
        (2, 'Предобработка', 'Исправить орфографию и пунктуацию'),
        (3, 'Предобработка', 'Заполнить id'),
        (4, 'Предобработка', 'Заполнить title'),
        (5, 'Анализ',        'Анализ текста'),
        (6, 'Анализ',        'Анализ картинок'),
        (7, 'Перевод',       'Перевести на английский'),
        (8, 'Копирование',   'Копирование файлов'),
    ]
    AI_STEPS       = {1, 2, 3, 5, 6, 7}
    AUTO_STEPS     = {0, 8}
    EDITABLE_STEPS = {3, 4, 7}

    def __init__(self, parent, filename, notes_folder, images_folder, on_done):
        super().__init__(parent)
        self.title(Path(filename).stem)
        self.geometry('760x580')
        self.resizable(True, True)
        self.grab_set()

        self.filename      = filename
        self.notes_folder  = Path(notes_folder)
        self.images_folder = Path(images_folder)
        self.on_done       = on_done

        self._step_queue  = []
        self._queue_pos   = 0
        self._yo_result      = None
        self._yo_original    = None
        self._spell_result   = None
        self._spell_original = None
        self._text_readonly = True

        fm = read_frontmatter(self.notes_folder / self.filename)
        self._article_id = fm.get('id', '').strip() or None

        self._build_prep()
        self._build_pipeline()
        self._show_prep()

    # ── Prep screen ───────────────────────────────────────────────────────────

    def _build_prep(self):
        self._prep_frame = ttk.Frame(self)
        self._step_vars  = {}

        groups = {}
        for step_id, group, label in self.STEP_DEFS:
            groups.setdefault(group, []).append((step_id, label))

        for group_name, steps in groups.items():
            ttk.Label(self._prep_frame, text=group_name,
                      font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=18, pady=(14, 2))
            for step_id, label in steps:
                var = tk.BooleanVar(value=True)
                state = 'disabled' if step_id == 7 else 'normal'
                ttk.Checkbutton(self._prep_frame, text=label,
                                variable=var, state=state).pack(anchor='w', padx=36, pady=2)
                self._step_vars[step_id] = var

        btn_row = ttk.Frame(self._prep_frame)
        btn_row.pack(anchor='w', padx=18, pady=(20, 0))
        ttk.Button(btn_row, text='Начать',   command=self._start).pack(side='left')
        ttk.Button(btn_row, text='Отменить', command=self.destroy).pack(side='left', padx=8)

    def _show_prep(self):
        self._pipeline_frame.pack_forget()
        self._prep_frame.pack(fill='both', expand=True)

    def _start(self):
        self._step_queue = [sid for sid, var in sorted(self._step_vars.items()) if var.get()]
        self._queue_pos  = 0
        self._prep_frame.pack_forget()
        self._pipeline_frame.pack(fill='both', expand=True)
        self._run_step()

    # ── Pipeline screen ───────────────────────────────────────────────────────

    def _build_pipeline(self):
        self._pipeline_frame = ttk.Frame(self)

        top = ttk.Frame(self._pipeline_frame)
        top.pack(fill='x', padx=14, pady=(14, 4))
        self.step_label = ttk.Label(top, text='', font=('Segoe UI', 11, 'bold'))
        self.step_label.pack(side='left')

        self.text = scrolledtext.ScrolledText(
            self._pipeline_frame, wrap='word', font=('Segoe UI', 10), background='#f7f7f7')
        self.text.pack(fill='both', expand=True, padx=14, pady=6)
        self.text.bind('<Key>', self._on_text_key)

        bottom = ttk.Frame(self._pipeline_frame)
        bottom.pack(fill='x', padx=14, pady=(4, 14))

        self.ready_btn = ttk.Button(bottom, text='Готово →', state='disabled', command=self._next_step)
        self.ready_btn.pack(side='left')
        self.skip_btn  = ttk.Button(bottom, text='Пропустить', state='disabled', command=self._next_step)
        self.skip_btn.pack(side='left', padx=6)
        self.retry_btn = ttk.Button(bottom, text='Повторить', state='disabled', command=self._retry)
        self.retry_btn.pack(side='left', padx=6)
        ttk.Button(bottom, text='Отменить', command=self.destroy).pack(side='left')

        self.status_var = tk.StringVar()
        ttk.Label(bottom, textvariable=self.status_var, foreground='gray').pack(side='left', padx=10)

    def _on_text_key(self, e):
        if e.char == '\x03':
            try:
                text = e.widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                e.widget.clipboard_clear()
                e.widget.clipboard_append(text)
            except tk.TclError:
                pass
            return 'break'
        if e.char == '\x01':
            e.widget.tag_add(tk.SEL, '1.0', 'end')
            return 'break'
        if self._text_readonly:
            if not e.char:
                return None
            return 'break'
        return None

    def _write(self, text):
        self.text.insert('end', text)
        self.text.see('end')

    def _clear(self):
        self.text.delete('1.0', 'end')

    def _current_step(self):
        return self._step_queue[self._queue_pos]

    def _set_ready(self, status=''):
        step = self._current_step()
        self.ready_btn.config(state='normal')
        self.status_var.set(status)
        if step in self.AI_STEPS:
            self.retry_btn.config(state='normal')
        if step not in self.AUTO_STEPS:
            self.skip_btn.config(state='normal')

    def _next_step(self):
        self._text_readonly = True
        self.ready_btn.config(text='Готово →', command=self._next_step)
        self._yo_result = None
        self._queue_pos += 1
        self.ready_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        self.retry_btn.config(state='disabled')
        self._run_step()

    def _retry(self):
        self.ready_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        self.retry_btn.config(state='disabled')
        self._clear()
        self.status_var.set('')
        step = self._current_step()
        {1: self._step_fix_yo,   2: self._step_fix_spell,
         3: self._step_fill_id,  5: self._step_text,
         6: self._step_images,   7: self._step_translate}[step]()

    def _run_step(self):
        if self._queue_pos >= len(self._step_queue):
            self._finish()
            return
        step = self._current_step()
        pos, total = self._queue_pos + 1, len(self._step_queue)
        _, _, label = self.STEP_DEFS[step]
        self.step_label.config(text=f'Шаг {pos} из {total} — {label}')
        self._clear()
        self.status_var.set('')
        self._text_readonly = step not in self.EDITABLE_STEPS
        {0: self._step_remove_bg,
         1: self._step_fix_yo,
         2: self._step_fix_spell,
         3: self._step_fill_id,
         4: self._step_fill_title,
         5: self._step_text,
         6: self._step_images,
         7: self._step_translate,
         8: self._step_copy}[step]()

    # ── Shared CLI runner ─────────────────────────────────────────────────────

    def _run_claude_cmd(self, cmd, on_done_msg='', on_captured=None):
        def worker():
            output = []
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding='utf-8', errors='replace')
                for line in proc.stdout:
                    output.append(line)
                    self.after(0, self._write, line)
                proc.wait()
            except FileNotFoundError:
                self.after(0, self._write, 'Ошибка: команда claude не найдена.\n')
            except Exception as e:
                self.after(0, self._write, f'Ошибка: {e}\n')
            finally:
                if on_captured:
                    self.after(0, on_captured, ''.join(output))
                self.after(0, self._set_ready, on_done_msg)
                self.after(0, lambda: self.skip_btn.config(state='normal'))
        threading.Thread(target=worker, daemon=True).start()

    # ── Step 0: remove background ─────────────────────────────────────────────

    def _step_remove_bg(self):
        self.status_var.set('Обрабатываю...')
        threading.Thread(target=self._run_remove_bg, daemon=True).start()

    def _run_remove_bg(self):
        try:
            from PIL import Image
        except ImportError:
            self.after(0, self._write, 'Нужен Pillow: pip install Pillow\n')
            self.after(0, self._set_ready)
            return

        content = (self.notes_folder / self.filename).read_text(encoding='utf-8')
        names   = find_images_in_md(content)
        pngs    = [self.images_folder / n for n in names
                   if (self.images_folder / n).exists() and n.lower().endswith('.png')]

        if not pngs:
            self.after(0, self._write, 'PNG-картинок нет — пропускаю.\n')
            self.after(0, self._set_ready)
            return

        THRESHOLD = 240
        for path in pngs:
            try:
                img = Image.open(path).convert('RGBA')
                pixels = [
                    (r, g, b, 0) if r >= THRESHOLD and g >= THRESHOLD and b >= THRESHOLD
                    else (r, g, b, a)
                    for r, g, b, a in img.getdata()
                ]
                img.putdata(pixels)
                img.save(path)
                self.after(0, self._write, f'✓  {path.name}\n')
            except Exception as e:
                self.after(0, self._write, f'⚠  {path.name}: {e}\n')

        self.after(0, self._set_ready)

    # ── Step 1: fix е→ё ──────────────────────────────────────────────────────

    def _step_fix_yo(self):
        self.status_var.set('Анализирую...')
        self._yo_original = (self.notes_folder / self.filename).read_text(encoding='utf-8')
        prompt = (
            "В тексте ниже замени 'е' на 'ё' везде, где это требуется по правилам русского языка. "
            "Верни ТОЛЬКО исправленный текст, без объяснений и без форматирования markdown.\n\n"
            + self._yo_original
        )
        self._run_claude_cmd(
            ['claude', '-p', prompt],
            on_done_msg='«Применить» — сохранить в файл.  «Пропустить» — не сохранять.',
            on_captured=self._on_yo_done,
        )

    def _on_yo_done(self, text):
        self._yo_result = text.strip()
        self.ready_btn.config(text='Применить →', command=self._apply_yo_and_next)
        self._show_yo_diff()

    def _show_yo_diff(self):
        if not self._yo_original or not self._yo_result:
            return
        self._clear()
        self.text.tag_configure('yo_change', foreground='#c0392b', font=('Segoe UI', 10, 'bold'))
        matcher = difflib.SequenceMatcher(None, self._yo_original, self._yo_result, autojunk=False)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            chunk = self._yo_result[j1:j2]
            if op == 'equal':
                self.text.insert('end', chunk)
            elif op in ('replace', 'insert'):
                self.text.insert('end', chunk, 'yo_change')

    def _apply_yo_and_next(self):
        if self._yo_result:
            try:
                (self.notes_folder / self.filename).write_text(self._yo_result, encoding='utf-8')
                messagebox.showinfo('Готово', 'Исправления сохранены в файл.')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Не удалось сохранить: {e}')
        self.ready_btn.config(text='Готово →', command=self._next_step)
        self._next_step()

    # ── Step 2: fix spelling & punctuation ───────────────────────────────────

    def _step_fix_spell(self):
        self.status_var.set('Анализирую...')
        self._spell_original = (self.notes_folder / self.filename).read_text(encoding='utf-8')
        prompt = (
            "Исправь в тексте следующее:\n"
            "1. Явные орфографические ошибки и ошибки пунктуации.\n"
            "2. Замени дефисы на тире (—) там, где это требуется по правилам русского языка "
            "(между частями предложения, в значении «это», после обращений и т.д.). "
            "Дефисы внутри слов и составных слов не трогай.\n"
            "3. Замени кавычки на русские «ёлочки» («»). "
            "Если внутри уже стоят «ёлочки», используй для вложенных кавычек „лапки" („").\n"
            "Не трогай формулы LaTeX и математические обозначения. "
            "Не меняй стиль, структуру или формулировки. "
            "Верни ТОЛЬКО исправленный текст без объяснений и без форматирования markdown.\n\n"
            + self._spell_original
        )
        self._run_claude_cmd(
            ['claude', '-p', prompt],
            on_done_msg='«Применить» — сохранить в файл.  «Пропустить» — не сохранять.',
            on_captured=self._on_spell_done,
        )

    def _on_spell_done(self, text):
        self._spell_result = text.strip()
        self.ready_btn.config(text='Применить →', command=self._apply_spell_and_next)
        self._show_spell_diff()

    def _show_spell_diff(self):
        if not self._spell_original or not self._spell_result:
            return
        self._clear()
        self.text.tag_configure('spell_change', foreground='#c0392b', font=('Segoe UI', 10, 'bold'))
        matcher = difflib.SequenceMatcher(None, self._spell_original, self._spell_result, autojunk=False)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            chunk = self._spell_result[j1:j2]
            if op == 'equal':
                self.text.insert('end', chunk)
            elif op in ('replace', 'insert'):
                self.text.insert('end', chunk, 'spell_change')

    def _apply_spell_and_next(self):
        if self._spell_result:
            try:
                (self.notes_folder / self.filename).write_text(
                    self._spell_result, encoding='utf-8')
                messagebox.showinfo('Готово', 'Исправления сохранены в файл.')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Не удалось сохранить: {e}')
        self.ready_btn.config(text='Готово →', command=self._next_step)
        self._next_step()

    # ── Step 3: fill id ───────────────────────────────────────────────────────

    def _step_fill_id(self):
        if self._article_id:
            self._write(f'{self._article_id}\n')
            self._text_readonly = False
            self.ready_btn.config(text='Применить →', state='normal', command=self._apply_id_and_next)
            self.skip_btn.config(state='normal')
            self.status_var.set('id уже задан — отредактируйте или нажмите «Применить»')
            return

        self.status_var.set('Генерирую slug...')
        stem = Path(self.filename).stem
        prompt = (
            f"Generate a concise URL-friendly slug in English for a Russian math article "
            f"with filename '{stem}'. "
            f"Return ONLY the slug (lowercase Latin letters, digits, hyphens, max 50 chars). "
            f"No explanation, no quotes, no newlines."
        )
        self._run_claude_cmd(
            ['claude', '-p', prompt],
            on_done_msg='Проверьте slug, отредактируйте при необходимости и нажмите «Применить».',
            on_captured=self._on_id_done,
        )

    def _on_id_done(self, text):
        slug = re.sub(r'[^a-z0-9-]', '', text.strip().lower())
        self._clear()
        self._write(slug)
        self._text_readonly = False
        self.ready_btn.config(text='Применить →', command=self._apply_id_and_next)

    def _apply_id_and_next(self):
        raw  = self.text.get('1.0', 'end').strip().split('\n')[0]
        slug = re.sub(r'[^a-z0-9-]', '', raw.lower())
        if not slug:
            messagebox.showerror('Ошибка', 'Пустой id. Введите корректный slug.')
            return
        if (RU_DIR / f'{slug}.md').exists() and slug != self._article_id:
            messagebox.showwarning('Дубликат', f'Статья с id "{slug}" уже есть на сайте.')
            return
        try:
            set_frontmatter_field(self.notes_folder / self.filename, 'id', slug)
            self._article_id = slug
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось сохранить id: {e}')
            return
        self.ready_btn.config(text='Готово →', command=self._next_step)
        self._next_step()

    # ── Step 3: fill title ────────────────────────────────────────────────────

    def _step_fill_title(self):
        fm = read_frontmatter(self.notes_folder / self.filename)
        existing = fm.get('title', '').strip()
        suggested = existing or Path(self.filename).stem.replace('-', ' ').replace('_', ' ')
        self._write(suggested)
        self._text_readonly = False
        self.ready_btn.config(text='Применить →', state='normal', command=self._apply_title_and_next)
        self.skip_btn.config(state='normal')
        msg = 'title уже задан' if existing else 'Отредактируйте заголовок'
        self.status_var.set(f'{msg} → нажмите «Применить»')

    def _apply_title_and_next(self):
        title = self.text.get('1.0', 'end').strip()
        if not title:
            messagebox.showerror('Ошибка', 'Заголовок не может быть пустым.')
            return
        try:
            set_frontmatter_field(self.notes_folder / self.filename, 'title', title)
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось сохранить title: {e}')
            return
        self.ready_btn.config(text='Готово →', command=self._next_step)
        self._next_step()

    # ── Step 5: text analysis ─────────────────────────────────────────────────

    def _step_text(self):
        self.status_var.set('Анализирую...')
        content = (self.notes_folder / self.filename).read_text(encoding='utf-8')
        prompt  = (
            "Проверь следующую математическую статью на ошибки грамматики, пунктуации и синтаксиса LaTeX. "
            "Выдай пронумерованный список замечаний с точной цитатой из текста. "
            "Если формулу LaTeX можно улучшить — дай рекомендации. "
            "Важно: статья намеренно написана с элементами разговорного стиля — это часть авторского замысла, "
            "чтобы сделать текст менее сухим. Не считай разговорные обороты ошибками. "
            "Наоборот, если видишь места где уместно было бы добавить живости или неформального тона — "
            "предложи это отдельным пунктом. "
            "Если ошибок нет — скажи об этом.\n\n"
            f"Статья:\n{content}"
        )
        self._run_claude_cmd(
            ['claude', '-p', prompt],
            on_done_msg='Исправьте замечания и нажмите «Готово»',
        )

    # ── Step 6: image analysis ────────────────────────────────────────────────

    def _step_images(self):
        content  = (self.notes_folder / self.filename).read_text(encoding='utf-8')
        names    = find_images_in_md(content)
        existing = [(n, self.images_folder / n) for n in names if (self.images_folder / n).exists()]

        if not existing:
            self._write('Картинок в статье нет.\n')
            self._set_ready()
            return

        self.status_var.set('Анализирую картинки...')
        paths  = ', '.join(str(p) for _, p in existing)
        prompt = (
            f"Посмотри на картинки по путям: {paths}\n\n"
            "Проверь каждую: что на ней изображено и соответствует ли она тексту статьи? "
            "Укажи конкретно если что-то не так.\n\n"
            f"Текст статьи:\n{content}"
        )
        self._run_claude_cmd(
            ['claude', '-p', prompt, '--allowedTools', 'Read'],
            on_done_msg='Проверьте замечания и нажмите «Готово»',
        )

    # ── Step 7: translate ─────────────────────────────────────────────────────

    def _step_translate(self):
        self.status_var.set('Перевожу...')
        content = (self.notes_folder / self.filename).read_text(encoding='utf-8')
        prompt  = (
            "Translate this math article from Russian to English. "
            "Preserve all LaTeX formulas unchanged. "
            "In YAML frontmatter: translate title, description, and tags to English; "
            "keep id, date (must stay in YYYY-MM-DD format), draft, and references unchanged. "
            "Return ONLY the complete translated markdown, no explanation, no code fences.\n\n"
            + content
        )
        self._run_claude_cmd(
            ['claude', '-p', prompt],
            on_done_msg='Отредактируйте при необходимости и нажмите «Применить».',
            on_captured=self._on_translate_done,
        )

    def _on_translate_done(self, text):
        self._clear()
        self._write(text.strip())
        self._text_readonly = False
        self.ready_btn.config(text='Применить →', command=self._apply_translate_and_next)

    def _apply_translate_and_next(self):
        text = self.text.get('1.0', 'end').strip()
        if text:
            aid = self._article_id
            if not aid:
                aid = read_frontmatter(self.notes_folder / self.filename).get('id', '').strip()
            if not aid:
                messagebox.showerror('Ошибка', 'id не задан. Пройдите шаг «Заполнить id».')
                return
            try:
                EN_DIR.mkdir(parents=True, exist_ok=True)
                (EN_DIR / f'{aid}.md').write_text(text, encoding='utf-8', newline='\n')
                messagebox.showinfo('Готово', f'Английская версия сохранена: en/{aid}.md')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Не удалось сохранить: {e}')
                return
        self.ready_btn.config(text='Готово →', command=self._next_step)
        self._next_step()

    # ── Step 8: copy ──────────────────────────────────────────────────────────

    def _step_copy(self):
        aid = self._article_id
        if not aid:
            aid = read_frontmatter(self.notes_folder / self.filename).get('id', '').strip()
        if not aid:
            self._write('⚠ id не задан. Пройдите шаг «Заполнить id».\n')
            self.ready_btn.config(text='Закрыть', state='normal', command=self._finish)
            return

        try:
            content = (self.notes_folder / self.filename).read_text(encoding='utf-8')
            RU_DIR.mkdir(parents=True, exist_ok=True)
            IMAGES_DIR.mkdir(parents=True, exist_ok=True)

            shutil.copy2(self.notes_folder / self.filename, RU_DIR / f'{aid}.md')
            self._write(f'✓  ru/{aid}.md\n')

            copied, missing = [], []
            for img in find_images_in_md(content):
                src = self.images_folder / img
                if src.exists():
                    shutil.copy2(src, IMAGES_DIR / img)
                    copied.append(img)
                else:
                    missing.append(img)

            if copied:  self._write(f'✓  Картинки: {", ".join(copied)}\n')
            if missing: self._write(f'⚠  Не найдены: {", ".join(missing)}\n')

            self.ready_btn.config(text='Закрыть', state='normal', command=self._finish)
        except Exception as e:
            self._write(f'Ошибка: {e}\n')
            self.ready_btn.config(text='Закрыть', state='normal', command=self._finish)

    def _finish(self):
        self.on_done()
        self.destroy()


# ─── Main window ──────────────────────────────────────────────────────────────

class ImportTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Obsidian → Simple Geometry')
        self.geometry('700x520')
        self.resizable(True, True)
        self.settings    = load_settings()
        self._all_articles = []
        self._filtered   = []
        self._id_map     = {}   # {id → rel_path}
        self._path_to_id = {}   # {rel_path → id}
        self._queue      = []
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        pad = {'padx': 14, 'pady': 6}

        sf = ttk.LabelFrame(self, text='Настройки', padding=10)
        sf.pack(fill='x', **pad)
        sf.columnconfigure(1, weight=1)

        ttk.Label(sf, text='Папка с заметками:').grid(row=0, column=0, sticky='w')
        self.notes_var = tk.StringVar(value=self.settings.get('notes_folder', ''))
        ttk.Entry(sf, textvariable=self.notes_var).grid(row=0, column=1, sticky='ew', padx=6)
        ttk.Button(sf, text='…', width=3, command=self._browse_notes).grid(row=0, column=2)

        ttk.Label(sf, text='Папка с картинками:').grid(row=1, column=0, sticky='w', pady=(6, 0))
        self.images_var = tk.StringVar(value=self.settings.get('images_folder', ''))
        ttk.Entry(sf, textvariable=self.images_var).grid(row=1, column=1, sticky='ew', padx=6, pady=(6, 0))
        ttk.Button(sf, text='…', width=3, command=self._browse_images).grid(row=1, column=2, pady=(6, 0))

        ttk.Button(sf, text='Сохранить', command=self._save_settings).grid(
            row=2, column=1, sticky='e', pady=(8, 0))

        af = ttk.LabelFrame(self, text='Статьи для импорта', padding=10)
        af.pack(fill='both', expand=True, **pad)

        btn_row = ttk.Frame(af)
        btn_row.pack(fill='x', pady=(0, 6))
        ttk.Button(btn_row, text='Обновить', command=self._refresh_list).pack(side='left')
        ttk.Button(btn_row, text='Выбрать все', command=self._select_all).pack(side='left', padx=6)
        ttk.Button(btn_row, text='Снять все', command=self._deselect_all).pack(side='left')

        self.show_not_imported_var = tk.BooleanVar(value=self.settings.get('show_not_imported', True))
        ttk.Checkbutton(btn_row, text='Не импортированные',
                        variable=self.show_not_imported_var,
                        command=self._on_filter_toggle).pack(side='left', padx=(12, 4))
        self.show_imported_var = tk.BooleanVar(value=self.settings.get('show_imported', False))
        ttk.Checkbutton(btn_row, text='Импортированные',
                        variable=self.show_imported_var,
                        command=self._on_filter_toggle).pack(side='left', padx=4)
        self.show_site_only_var = tk.BooleanVar(value=self.settings.get('show_site_only', False))
        ttk.Checkbutton(btn_row, text='Только на сайте',
                        variable=self.show_site_only_var,
                        command=self._on_filter_toggle).pack(side='left', padx=4)

        self.count_label = ttk.Label(btn_row, text='', foreground='gray')
        self.count_label.pack(side='right')

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add('write', lambda *_: self._apply_filter())
        ttk.Entry(af, textvariable=self.filter_var, font=('Segoe UI', 10)).pack(fill='x', pady=(0, 6))

        list_frame = ttk.Frame(af)
        list_frame.pack(fill='both', expand=True)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        self.listbox = tk.Listbox(
            list_frame, selectmode='multiple', yscrollcommand=scrollbar.set,
            activestyle='none', font=('Segoe UI', 10), relief='solid', borderwidth=1)
        self.listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)

        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=14, pady=(0, 14))
        ttk.Button(bottom, text='Импортировать выбранные', command=self._import).pack(side='left')
        ttk.Button(bottom, text='Удалить с сайта', command=self._delete_from_site).pack(side='left', padx=8)
        self.status_var = tk.StringVar()
        ttk.Label(bottom, textvariable=self.status_var, foreground='gray').pack(side='left', padx=12)

    def _browse_notes(self):
        folder = filedialog.askdirectory(title='Папка с заметками Obsidian')
        if folder:
            self.notes_var.set(folder)

    def _browse_images(self):
        folder = filedialog.askdirectory(title='Папка с картинками')
        if folder:
            self.images_var.set(folder)

    def _on_filter_toggle(self):
        self.settings['show_imported']     = self.show_imported_var.get()
        self.settings['show_not_imported'] = self.show_not_imported_var.get()
        self.settings['show_site_only']    = self.show_site_only_var.get()
        save_settings(self.settings)
        self._apply_filter()

    def _save_settings(self):
        self.settings = {
            'notes_folder':      self.notes_var.get(),
            'images_folder':     self.images_var.get(),
            'show_imported':     self.show_imported_var.get(),
            'show_not_imported': self.show_not_imported_var.get(),
            'show_site_only':    self.show_site_only_var.get(),
        }
        save_settings(self.settings)
        self.status_var.set('Настройки сохранены.')
        self._refresh_list()

    def _refresh_list(self):
        self._id_map     = {}
        self._path_to_id = {}
        folder = self.notes_var.get()
        if folder and Path(folder).exists():
            root = Path(folder)
            for f in root.rglob('*.md'):
                aid = read_frontmatter(f).get('id', '').strip()
                if aid:
                    rel = str(f.relative_to(root))
                    self._id_map[aid]     = rel
                    self._path_to_id[rel] = aid
        self._all_articles = get_all_articles(folder, self._id_map, self._path_to_id)
        self.filter_var.set('')
        self._apply_filter()
        self.status_var.set('')

    def _apply_filter(self):
        query    = self.filter_var.get().lower()
        show_new  = self.show_not_imported_var.get()
        show_imp  = self.show_imported_var.get()
        show_site = self.show_site_only_var.get()
        self._filtered = [
            (path, status, aid) for path, status, aid in self._all_articles
            if ((show_new  and status == 'new')
             or (show_imp  and status == 'imported')
             or (show_site and status == 'site_only'))
            and query in path.lower()
        ]
        self.listbox.delete(0, 'end')
        for path, status, _ in self._filtered:
            if status == 'imported':
                self.listbox.insert('end', f'✓ {path}')
                self.listbox.itemconfig('end', foreground='#999')
            elif status == 'site_only':
                self.listbox.insert('end', f'◆ {path}')
                self.listbox.itemconfig('end', foreground='#2980b9')
            else:
                self.listbox.insert('end', path)
        n, total = len(self._filtered), len(self._all_articles)
        self.count_label.config(text=f'{n} из {total}')

    def _select_all(self):
        self.listbox.select_set(0, 'end')

    def _deselect_all(self):
        self.listbox.select_clear(0, 'end')

    def _import(self):
        chosen     = [self._filtered[i] for i in self.listbox.curselection()]
        importable = [(p, s, a) for p, s, a in chosen if s != 'site_only']
        site_only  = [p for p, s, a in chosen if s == 'site_only']
        if site_only:
            messagebox.showinfo(
                'Пропущено',
                f'Пропущено {len(site_only)} статей — они есть только на сайте, источника в Obsidian нет.')
        if not importable:
            if not site_only:
                messagebox.showwarning('Ничего не выбрано', 'Выберите хотя бы одну статью.')
            return
        self._queue = [p for p, s, a in importable]
        self._process_next()

    def _delete_from_site(self):
        chosen    = [self._filtered[i] for i in self.listbox.curselection()]
        deletable = [(p, s, a) for p, s, a in chosen if s in ('imported', 'site_only')]
        if not deletable:
            messagebox.showwarning('Ничего не выбрано', 'Выберите статьи, которые есть на сайте.')
            return

        names = [a or p for p, s, a in deletable]
        if not messagebox.askyesno(
                'Подтверждение удаления',
                f'Удалить с сайта {len(deletable)} статей (ru/ + en/) и их неиспользуемые картинки?\n\n'
                + '\n'.join(names)):
            return

        deletable_ids = {a for _, _, a in deletable if a}

        images_in_use = set()
        for d in [RU_DIR, EN_DIR]:
            if d.exists():
                for f in d.glob('*.md'):
                    if f.stem not in deletable_ids:
                        images_in_use |= find_images_in_md(
                            f.read_text(encoding='utf-8', errors='ignore'))

        deleted_articles, deleted_images, errors = [], [], []

        for _, _, article_id in deletable:
            if not article_id:
                errors.append('нет id у одной из статей')
                continue
            article_images = set()
            for d in [RU_DIR, EN_DIR]:
                f = d / f'{article_id}.md'
                if f.exists():
                    try:
                        article_images |= find_images_in_md(
                            f.read_text(encoding='utf-8', errors='ignore'))
                        f.unlink()
                        deleted_articles.append(f.name)
                    except Exception as e:
                        errors.append(f'{f.name}: {e}')
            for img in article_images - images_in_use:
                img_path = IMAGES_DIR / img
                if img_path.exists():
                    try:
                        img_path.unlink()
                        deleted_images.append(img)
                    except Exception as e:
                        errors.append(f'{img}: {e}')

        self._refresh_list()
        msg = f'Удалено файлов: {len(deleted_articles)}'
        if deleted_images:
            msg += f'\nУдалено картинок: {len(deleted_images)}'
        if errors:
            msg += '\nОшибки:\n' + '\n'.join(errors)
        messagebox.showinfo('Готово', msg)

    def _process_next(self):
        if not self._queue:
            self._refresh_list()
            self.status_var.set('Готово.')
            return
        filename = self._queue.pop(0)
        PipelineDialog(
            self, filename,
            self.notes_var.get(), self.images_var.get(),
            on_done=self._process_next,
        )


if __name__ == '__main__':
    app = ImportTool()
    app.mainloop()
