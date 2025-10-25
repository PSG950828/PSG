#!/usr/bin/env python3
import os
import argparse
import tkinter as tk
from tkinter import ttk, messagebox

NOTES_DIR = 'notes'


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
    root.title('Note Manager')

    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=('title',), show='headings', selectmode='browse', height=15)
    tree.heading('title', text='Title')
    vsb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=0, column=2, sticky='nsw', padx=(10,0))

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    def refresh():
        tree.delete(*tree.get_children())
        for nid, slug in list_notes():
            tree.insert('', 'end', iid=str(nid), values=(slug.replace('-', ' '),))

    def add_gui():
        win = tk.Toplevel(root)
        win.title('Add Note')
        ttk.Label(win, text='Title:').pack(anchor='w')
        title_entry = ttk.Entry(win, width=40)
        title_entry.pack(fill=tk.X)
        text = tk.Text(win, width=60, height=20)
        text.pack()

        def save():
            title = title_entry.get().strip()
            body = text.get('1.0', tk.END).rstrip()
            if title:
                add_note(title, body)
                win.destroy()
                refresh()

        ttk.Button(win, text='Save', command=save).pack(pady=4)

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
        win.title('Edit Note')
        ttk.Label(win, text='Title:').pack(anchor='w')
        title_entry = ttk.Entry(win, width=40)
        title_entry.insert(0, title)
        title_entry.pack(fill=tk.X)
        text = tk.Text(win, width=60, height=20)
        text.insert('1.0', body)
        text.pack()

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

        ttk.Button(win, text='Save', command=save).pack(pady=4)

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
        win.title('View Note')
        ttk.Label(win, text=title).pack(anchor='w')
        text = tk.Text(win, width=60, height=20)
        text.insert('1.0', body)
        text.config(state=tk.DISABLED)
        text.pack()
        ttk.Button(win, text='Close', command=win.destroy).pack(pady=4)

    def delete_gui():
        sel = tree.selection()
        if not sel:
            return
        nid = int(sel[0])
        if messagebox.askyesno('Delete', 'Delete selected note?'):
            delete_note(nid)
            refresh()

    tree.bind('<Double-Button-1>', lambda e: view_gui())
    ttk.Button(btn_frame, text='View', command=view_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='Add', command=add_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='Edit', command=edit_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='Delete', command=delete_gui).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='Refresh', command=refresh).pack(fill=tk.X, pady=2)
    ttk.Button(btn_frame, text='Quit', command=root.destroy).pack(fill=tk.X, pady=2)

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
