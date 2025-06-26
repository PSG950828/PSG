# PSG Notes Manager

This repository hosts a minimal notes manager application. It provides a GUI and CLI interface for managing notes.

## Launching the application

* **GUI**: Run `python3 note_manager.py` to open the graphical interface.
* **CLI**: Use the command-line scripts provided in this repository to manage notes from the terminal.

## NOTES_DIR environment variable

The application stores its data in a directory specified by the `NOTES_DIR` environment variable. If this variable is not set, the application will default to a `notes` folder in the repository.

## Clipboard image paste

Copying images directly into the note editor requires the Pillow package (`pip install Pillow`). This feature is supported only on Windows and macOS.
