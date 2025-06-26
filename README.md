# Note Manager

This project provides a simple command-line tool for managing text notes.
Notes are stored in the `notes` directory as numbered text files.

## Usage

Run the script with Python and one of the following commands:

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
