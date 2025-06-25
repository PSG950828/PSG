import os
import argparse
import textwrap

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


def add_note(title):
    ensure_notes_dir()
    nid = next_id()
    slug = slugify(title)
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


def edit_note(nid):
    path = note_path(nid)
    if not path or not os.path.exists(path):
        print('Note not found.')
        return
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
