# 검안사 실무 백서

This project provides a simple command-line tool for managing text notes.
Notes are stored in the `notes` directory as numbered text files by default.
Set the environment variable `NOTES_DIR` to point to a shared folder if you
want multiple computers to use the same set of notes. `NOTES_DIR` may include
a `~` to reference the user's home directory so the same path works on
Windows and macOS alike.

## Usage

Running the script with no arguments opens a Tkinter window titled
"검안사 실무 백서". Notes are listed in a table with a search box for quickly
filtering titles. Buttons on the side (표시된 한글 이름: **보기**, **추가**, **수정**, **삭제**, **새로고침**, **종료**) let you manage notes. Font size controls are shown inside the add and
edit windows rather than on the main screen.
You can double-click a note or use the **View** button to open it in a
separate read-only window. Insert images with the **이미지 삽입** button or by pasting from the clipboard (requires Pillow). Images are scaled to fit when viewing a note. You can
also use command-line subcommands:

```
python note_manager.py list
python note_manager.py add "Note title"
python note_manager.py view <id>
python note_manager.py edit <id>
python note_manager.py delete <id>
```

Each note is identified by an incrementing ID. The `add` command lets you
type the note text in your terminal. To finish entering text, put a single
period (`.`) on a new line.

## Requirements

This program only depends on Python's standard library. Any Python 3.8+
installation with Tkinter available should work. On Linux systems you may
need to install `tk` packages separately. Running the script without the
`DISPLAY` environment variable will fall back to the command-line mode.
If you set `NOTES_DIR` to a shared network path, make sure every machine
has permissions to access that folder.

## Troubleshooting
If you open `note_manager.py` inside VS Code and see errors about missing names or syntax near text like `diff --git`, you may have opened a patch file instead of the actual script. Open the file from the repository directly to avoid such false errors.

## Windows and macOS

The script works the same on Windows and macOS as long as Python 3.8+ with Tkinter is installed.  Run it from a terminal using `python note_manager.py`. If you want every computer to share the same notes, set the `NOTES_DIR` environment variable to a shared location accessible to both systems, such as a network drive or a cloud‑synced folder.
