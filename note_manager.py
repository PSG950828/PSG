#!/usr/bin/env python3
import os
import argparse
import shutil
from uuid import uuid4
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
try:
    from PIL import ImageGrab, Image, ImageTk
except Exception:  # Pillow may not be installed
    ImageGrab = None
    Image = None
    ImageTk = None

# Allow using '~' or absolute paths in NOTES_DIR so the same setting works
# on Windows, macOS, and Linux.
NOTES_DIR = os.path.expanduser(os.environ.get('NOTES_DIR', 'notes'))
DEFAULT_FONT_SIZE = 12


def slugify(title):
    return ''.join(c.lower() if c.isalnum() else '-' for c in title).strip('-')


def ensure_notes_dir():
    if not os.path.isdir(NOTES_DIR):
        os.makedirs(NOTES_DIR)


def list_notes():
    ensure_notes_dir()
    files = sorted(os.listdir(NOTES_DIR))
    notes = []
    for fname in files:
        if fname.endswith('.txt'):
            parts = fname[:-4].split('_', 1)
            if len(parts) == 2 and parts[0].isdigit():
                notes.append((int(parts[0]), parts[1]))
    return notes


def next_id():
    notes = list_notes()
    return max([nid for nid, _ in notes], default=0) + 1


def note_path(nid, slug=None):
    if slug is None:
        # find by id
        for fname in os.listdir(NOTES_DIR):
            if fname.startswith(f"{nid}_") and fname.endswith('.txt'):
                return os.path.join(NOTES_DIR, fname)
        return None
    else:
        return os.path.join(NOTES_DIR, f"{nid}_{slug}.txt")


def read_multiline(prompt):
    print(prompt)
    print('(end input with a single "." on a line)')
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == '.':
            break
        lines.append(line)
    return '\n'.join(lines)


def add_note(title, body=None):
    """Create a new note with the given title and optional body."""
    ensure_notes_dir()
    nid = next_id()
    slug = slugify(title)
    if body is None:
        body = read_multiline('Enter note text:')
    path = note_path(nid, slug)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"Note {nid} saved.")


def view_note(nid):
    path = note_path(nid)
    if not path or not os.path.exists(path):
        print('Note not found.')
        return
    with open(path, 'r', encoding='utf-8') as f:
        print(f.read())


def edit_note(nid, new_body=None):
    """Edit an existing note by id."""
    path = note_path(nid)
    if not path or not os.path.exists(path):
        print('Note not found.')
        return
    if new_body is None:
        with open(path, 'r', encoding='utf-8') as f:
            current = f.read()
        print('Current text (edit below, leave blank to keep unchanged):')
        print('-'*40)
        print(current)
        print('-'*40)
        new_body = read_multiline('New text:')
        if new_body.strip() == '':
            print('No changes made.')
            return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_body)
    print('Note updated.')


def delete_note(nid):
    path = note_path(nid)
    if not path or not os.path.exists(path):
        print('Note not found.')
        return
    os.remove(path)
    print('Note deleted.')


def run_gui():
    """Launch a simple Tkinter interface for managing notes."""
    ensure_notes_dir()

    root = tk.Tk()
    root.title('검안사 실무 백서')
    root.geometry('900x600')
    root.minsize(800, 500)
    root.maxsize(1200, 800)

    base_font = tkfont.Font(family='Arial', size=DEFAULT_FONT_SIZE)

    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass
    style.configure('Treeview', font=base_font)
    style.configure('TButton', font=base_font)
    style.configure('TLabel', font=base_font)
    style.configure('TEntry', font=base_font)

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    top = ttk.Frame(frame)
    top.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0,5))
    ttk.Label(top, text='검색:').pack(side='left')
    search_var = tk.StringVar()
    search_entry = ttk.Entry(top, textvariable=search_var)
    search_entry.pack(side='left', fill='x', expand=True)

    tree = ttk.Treeview(frame, columns=('title',), show='headings', selectmode='browse', height=15)
    tree.heading('title', text='제목')
    vsb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=1, column=0, sticky='nsew')
    vsb.grid(row=1, column=1, sticky='ns')

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=1, column=2, sticky='nsw', padx=(10,0))

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    def refresh(*args):
        query = search_var.get().lower()
        tree.delete(*tree.get_children())
        for nid, slug in list_notes():
            title = slug.replace('-', ' ')
            if query in title.lower():
                tree.insert('', 'end', iid=str(nid), values=(title,))

    search_var.trace_add('write', refresh)

    def add_gui():
        win = tk.Toplevel(root)
        win.title('메모 추가')
        font_var = tk.IntVar(value=DEFAULT_FONT_SIZE)
        edit_font = tkfont.Font(family='Arial', size=font_var.get())

        def update_font(*args):
            edit_font.configure(size=font_var.get())

        top = ttk.Frame(win)
        top.pack(fill=tk.X)
        ttk.Label(top, text='글씨 크기:').pack(side='left')
        tk.Spinbox(top, from_=8, to=24, textvariable=font_var,
                   width=4, command=update_font).pack(side='left')

        ttk.Label(win, text='제목:', font=edit_font).pack(anchor='w')
        title_entry = ttk.Entry(win, width=40, font=edit_font)
        title_entry.pack(fill=tk.X)
        text = tk.Text(win, width=60, height=20, font=edit_font)
        text.pack()

        def insert_image():
            path = filedialog.askopenfilename(
                title='Select Image',
                filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.gif')])
            if path:
                ext = os.path.splitext(path)[1].lower()
                dest = f'img_{uuid4().hex}{ext}'
                shutil.copy(path, os.path.join(NOTES_DIR, dest))
                text.insert(tk.INSERT, f'[[image:{dest}]]')

        def paste_image():
            if ImageGrab is None:
                messagebox.showerror('Error', 'Pillow not available for clipboard images.')
                return
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                dest = f'img_{uuid4().hex}.png'
                img.save(os.path.join(NOTES_DIR, dest), 'PNG')
                text.insert(tk.INSERT, f'[[image:{dest}]]')
            else:
                messagebox.showinfo('Paste', 'Clipboard does not contain an image.')

        def save():
            title = title_entry.get().strip()
            body = text.get('1.0', tk.END).rstrip()
            if title:
                add_note(title, body)
                win.destroy()
                refresh()

        btn_bar = ttk.Frame(win)
        btn_bar.pack(pady=4)
        ttk.Button(btn_bar, text='이미지 삽입', command=insert_image).pack(side='left', padx=2)
        ttk.Button(btn_bar, text='붙여넣기', command=paste_image).pack(side='left', padx=2)
        ttk.Button(btn_bar, text='저장', command=save).pack(side='left', padx=2)

    def edit_gui():
        sel = tree.selection()
        if not sel:
            return
        nid = int(sel[0])
        path = note_path(nid)
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            body = f.read()
        title = os.path.basename(path)[path.find('_')+1:-4].replace('-', ' ')

        win = tk.Toplevel(root)
        win.title('메모 수정')

        font_var = tk.IntVar(value=DEFAULT_FONT_SIZE)
        edit_font = tkfont.Font(family='Arial', size=font_var.get())

        def update_font(*args):
            edit_font.configure(size=font_var.get())

        top = ttk.Frame(win)
        top.pack(fill=tk.X)
        ttk.Label(top, text='글씨 크기:').pack(side='left')
        tk.Spinbox(top, from_=8, to=24, textvariable=font_var,
                   width=4, command=update_font).pack(side='left')

        ttk.Label(win, text='제목:', font=edit_font).pack(anchor='w')
        title_entry = ttk.Entry(win, width=40, font=edit_font)
        title_entry.insert(0, title)
        title_entry.pack(fill=tk.X)
        text = tk.Text(win, width=60, height=20, font=edit_font)
        text.insert('1.0', body)
        text.pack()

        def insert_image():
            path = filedialog.askopenfilename(
                title='Select Image',
                filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.gif')])
            if path:
                ext = os.path.splitext(path)[1].lower()
                dest = f'img_{uuid4().hex}{ext}'
                shutil.copy(path, os.path.join(NOTES_DIR, dest))
                text.insert(tk.INSERT, f'[[image:{dest}]]')

        def paste_image():
            if ImageGrab is None:
                messagebox.showerror('Error', 'Pillow not available for clipboard images.')
                return
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                dest = f'img_{uuid4().hex}.png'
                img.save(os.path.join(NOTES_DIR, dest), 'PNG')
                text.insert(tk.INSERT, f'[[image:{dest}]]')
            else:
                messagebox.showinfo('Paste', 'Clipboard does not contain an image.')

        def save():
            new_title = title_entry.get().strip()
            new_body = text.get('1.0', tk.END).rstrip()
            if new_title:
                slug = slugify(new_title)
                new_path = note_path(nid, slug)
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(new_body)
                if new_path != path:
                    os.remove(path)
                win.destroy()
                refresh()

        btn_bar = ttk.Frame(win)
        btn_bar.pack(pady=4)
        ttk.Button(btn_bar, text='이미지 삽입', command=insert_image).pack(side='left', padx=2)
        ttk.Button(btn_bar, text='붙여넣기', command=paste_image).pack(side='left', padx=2)
        ttk.Button(btn_bar, text='저장', command=save).pack(side='left', padx=2)

    def view_gui():
        sel = tree.selection()
        if not sel:
            return
        nid = int(sel[0])
        path = note_path(nid)
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            body = f.read()
        title = os.path.basename(path)[path.find('_')+1:-4].replace('-', ' ')

        win = tk.Toplevel(root)
        win.title('메모 보기')
        ttk.Label(win, text=title, font=base_font).pack(anchor='w')
        text = tk.Text(win, width=60, height=20, font=base_font)

        photos = []
        pos = 0
        while True:
            start = body.find('[[image:', pos)
            if start == -1:
                text.insert(tk.END, body[pos:])
                break
            text.insert(tk.END, body[pos:start])
            end = body.find(']]', start)
            if end == -1:
                text.insert(tk.END, body[start:])
                break
            img_name = body[start+8:end]
            img_path = os.path.join(NOTES_DIR, img_name)
            if os.path.exists(img_path):
                try:
                    if Image and ImageTk:
                        img_obj = Image.open(img_path)
                        max_w = 500
                        max_h = 400
                        img_obj.thumbnail((max_w, max_h))
                        img = ImageTk.PhotoImage(img_obj)
                    else:
                        img = tk.PhotoImage(file=img_path)
                    text.image_create(tk.END, image=img)
                    photos.append(img)
                except Exception:
                    text.insert(tk.END, f'[missing image {img_name}]')
            pos = end + 2
        text.config(state=tk.DISABLED)
        text.pack()
        text.image_refs = photos
        ttk.Button(win, text='닫기', command=win.destroy).pack(pady=4)

    def delete_gui():
        sel = tree.selection()
        if not sel:
            return
        nid = int(sel[0])
        if messagebox.askyesno('삭제', '선택한 메모를 삭제할까요?'):
            delete_note(nid)
            refresh()

    tree.bind('<Double-Button-1>', lambda e: view_gui())
    ttk.Button(btn_frame, text='보기', command=view_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='추가', command=add_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='수정', command=edit_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='삭제', command=delete_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='새로고침', command=refresh).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='종료', command=root.destroy).pack(fill=tk.X, pady=2)

    refresh()
    root.mainloop()


def list_command():
    notes = list_notes()
    if not notes:
        print('No notes found.')
    else:
        for nid, slug in notes:
            print(f"{nid}: {slug.replace('-', ' ')}")


def main():
    parser = argparse.ArgumentParser(description='Simple shared note manager')
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('list')

    add_p = sub.add_parser('add')
    add_p.add_argument('title')

    view_p = sub.add_parser('view')
    view_p.add_argument('id', type=int)

    edit_p = sub.add_parser('edit')
    edit_p.add_argument('id', type=int)

    del_p = sub.add_parser('delete')
    del_p.add_argument('id', type=int)

    args = parser.parse_args()

    if args.cmd is None:
        run_gui()
        return

    if args.cmd == 'add':
        add_note(args.title)
    elif args.cmd == 'view':
        view_note(args.id)
    elif args.cmd == 'edit':
        edit_note(args.id)
    elif args.cmd == 'delete':
        delete_note(args.id)
    elif args.cmd == 'list':
        list_command()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
