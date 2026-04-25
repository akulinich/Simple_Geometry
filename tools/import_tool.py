import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import re
import shutil
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent / 'settings.json'
PROJECT_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = PROJECT_ROOT / 'src' / 'content' / 'articles'
IMAGES_DIR = PROJECT_ROOT / 'public' / 'images'


def load_settings():
    try:
        with open(SETTINGS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'notes_folder': '', 'images_folder': ''}


def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def find_images_in_md(content):
    images = set()
    for m in re.finditer(r'!\[\[([^\]|]+)', content):
        images.add(m.group(1).strip())
    for m in re.finditer(r'!\[.*?\]\(([^)]+)\)', content):
        p = m.group(1)
        if not p.startswith('http'):
            images.add(Path(p).name)
    return images


def get_importable_articles(notes_folder):
    if not notes_folder or not Path(notes_folder).exists():
        return []
    root = Path(notes_folder)
    imported = set(os.listdir(ARTICLES_DIR)) if ARTICLES_DIR.exists() else set()
    files = [f for f in root.rglob('*.md') if f.name not in imported]
    return sorted(str(f.relative_to(root)) for f in files)


class ImportTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Obsidian → Simple Geometry')
        self.geometry('700x520')
        self.resizable(True, True)
        self.settings = load_settings()
        self._all_articles = []
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        pad = {'padx': 14, 'pady': 6}

        # Settings
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

        # Articles list
        af = ttk.LabelFrame(self, text='Статьи для импорта', padding=10)
        af.pack(fill='both', expand=True, **pad)

        btn_row = ttk.Frame(af)
        btn_row.pack(fill='x', pady=(0, 6))
        ttk.Button(btn_row, text='Обновить', command=self._refresh_list).pack(side='left')
        ttk.Button(btn_row, text='Выбрать все', command=self._select_all).pack(side='left', padx=6)
        ttk.Button(btn_row, text='Снять все', command=self._deselect_all).pack(side='left')
        self.count_label = ttk.Label(btn_row, text='', foreground='gray')
        self.count_label.pack(side='right')

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add('write', lambda *_: self._apply_filter())
        ttk.Entry(af, textvariable=self.filter_var, font=('Segoe UI', 10)).pack(
            fill='x', pady=(0, 6))

        list_frame = ttk.Frame(af)
        list_frame.pack(fill='both', expand=True)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        self.listbox = tk.Listbox(
            list_frame, selectmode='multiple', yscrollcommand=scrollbar.set,
            activestyle='none', font=('Segoe UI', 10), relief='solid', borderwidth=1)
        self.listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Bottom bar
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=14, pady=(0, 14))
        ttk.Button(bottom, text='Импортировать выбранные', command=self._import).pack(side='left')
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

    def _save_settings(self):
        self.settings = {
            'notes_folder': self.notes_var.get(),
            'images_folder': self.images_var.get(),
        }
        save_settings(self.settings)
        self.status_var.set('Настройки сохранены.')
        self._refresh_list()

    def _refresh_list(self):
        self._all_articles = get_importable_articles(self.notes_var.get())
        self.filter_var.set('')
        self._apply_filter()
        self.status_var.set('')

    def _apply_filter(self):
        query = self.filter_var.get().lower()
        filtered = [a for a in self._all_articles if query in a.lower()]
        self.listbox.delete(0, 'end')
        for a in filtered:
            self.listbox.insert('end', a)
        n = len(filtered)
        total = len(self._all_articles)
        if query:
            self.count_label.config(text=f'{n} из {total}')
        else:
            self.count_label.config(text=f'{total} шт.' if total else 'нет новых')

    def _select_all(self):
        self.listbox.select_set(0, 'end')

    def _deselect_all(self):
        self.listbox.select_clear(0, 'end')

    def _import(self):
        selected = [self.listbox.get(i) for i in self.listbox.curselection()]
        if not selected:
            messagebox.showwarning('Ничего не выбрано', 'Выберите хотя бы одну статью.')
            return

        notes_folder = Path(self.notes_var.get())
        images_folder = Path(self.images_var.get())
        ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        copied_articles = 0
        copied_images = 0
        missing_images = []

        for rel_path in selected:
            src = notes_folder / rel_path
            filename = Path(rel_path).name
            content = src.read_text(encoding='utf-8')
            shutil.copy2(src, ARTICLES_DIR / filename)
            copied_articles += 1

            for img in find_images_in_md(content):
                src = images_folder / img
                if src.exists():
                    shutil.copy2(src, IMAGES_DIR / img)
                    copied_images += 1
                else:
                    missing_images.append(img)

        self._refresh_list()

        msg = f'Импортировано: {copied_articles} ст., {copied_images} картинок.'
        if missing_images:
            msg += f'\nНе найдены: {", ".join(missing_images)}'
            messagebox.showwarning('Готово с предупреждениями', msg)
        else:
            self.status_var.set(msg)


if __name__ == '__main__':
    app = ImportTool()
    app.mainloop()
