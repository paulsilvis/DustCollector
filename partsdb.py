#!/usr/bin/env python3

"""
stash - A simple command-line personal database.

Features:
- Add, edit, delete, and find items by location, description, or tags.
- Data stored in plain JSON file with automatic backups.
- Clean text-based interface using prompt_toolkit for easy editing.

Originally designed for small parts/tool storage tracking.
"""

import os
import sys
import json
import shlex
import shutil
from prompt_toolkit import prompt

DB_FILE = "simple_db.json"
BACKUP_FILE = "simple_db_backup.json"


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        upgraded = []
        for entry in data:
            if isinstance(entry, str):
                upgraded.append({"location": "", "description": entry, "tag": []})
            else:
                upgraded.append({
                    "location": entry.get("location", ""),
                    "description": entry.get("description", ""),
                    "tag": entry.get("tag", [])
                    if isinstance(entry.get("tag", []), list)
                    else [entry.get("tag", "")],
                })
        return upgraded
    return []


def save_db(db):
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


def add_entry(db, raw_input):
    parts = [p.strip() for p in raw_input.split(":")]
    if len(parts) == 2:
        location, description = parts
        tag = []
    elif len(parts) == 3:
        location, description, tag_str = parts
        tag = [t.strip() for t in tag_str.split(",") if t.strip()]
    else:
        print("Warning: Expected 'LOCATION: DESCRIPTION' or"
              " 'LOCATION: DESCRIPTION : TAG1, TAG2'. Treating as description only.")
        location = ""
        description = raw_input.strip()
        tag = []
    db.append({"location": location, "description": description, "tag": tag})
    print(f"Added: [{location}] {description} {{{', '.join(tag)}}}")


def find_entries(db, keywords):
    keywords = [k.lower() for k in keywords]
    results = []
    for idx, entry in enumerate(db, start=1):
        combined = (
            entry.get("location", "") + " " +
            entry.get("description", "") + " " +
            " ".join(entry.get("tag", []))
        ).lower()
        if all(k in combined for k in keywords):
            results.append((idx, entry))

    if not results:
        print("No matches found.")
        return

    max_loc = max((len(e['location']) for _, e in results), default=0)
    for idx, entry in sorted(results, key=lambda x: x[1]["description"].lower()):
        tag_display = f"{{{', '.join(entry['tag'])}}}" if entry['tag'] else ""
        print(f"{idx:3}: [{entry['location']:<{max_loc}}] {entry['description']} {tag_display}")


def list_entries(db, sort=True):
    if not db:
        print("Database is empty.")
        return

    entries = sorted(db, key=lambda e: e["description"].lower()) if sort else db
    max_loc = max((len(entry['location']) for entry in entries), default=0)
    for idx, entry in enumerate(entries, start=1):
        tag_display = f"{{{', '.join(entry['tag'])}}}" if entry['tag'] else ""
        print(f"{idx:3}: [{entry['location']:<{max_loc}}] {entry['description']} {tag_display}")


def delete_entry(db, num_str):
    try:
        num = int(num_str)
    except ValueError:
        print("Please provide a valid number.")
        return False

    if not (1 <= num <= len(db)):
        print("Invalid entry number.")
        return False

    entry = db[num - 1]
    print(f"Delete this entry?\n{num}: [{entry['location']}] {entry['description']} "
          f"{{{', '.join(entry['tag'])}}}")
    confirm = prompt("Confirm delete (y/n)? ").strip().lower()
    if confirm == "y":
        del db[num - 1]
        print("Entry deleted.")
        return True
    print("Deletion cancelled.")
    return False


def edit_entry(db, num_str):
    try:
        num = int(num_str)
    except ValueError:
        print("Please provide a valid number.")
        return False

    if not (1 <= num <= len(db)):
        print("Invalid entry number.")
        return False

    entry = db[num - 1]
    print(f"Editing entry:\n{num}: [{entry['location']}] {entry['description']} "
          f"{{{', '.join(entry['tag'])}}}")

    new_location = prompt(f"New location (was '{entry['location']}'): ").strip() or entry['location']
    new_description = prompt(f"New description (was '{entry['description']}'): ").strip() or entry['description']
    new_tag_input = prompt(f"New tags comma-separated (was '{', '.join(entry['tag'])}'): ").strip()

    new_tags = [t.strip() for t in new_tag_input.split(",") if t.strip()] if new_tag_input else entry['tag']

    print(f"Updated entry:\n[{new_location}] {new_description} {{{', '.join(new_tags)}}}")
    confirm = prompt("Confirm update (y/n)? ").strip().lower()
    if confirm == "y":
        db[num - 1] = {"location": new_location, "description": new_description, "tag": new_tags}
        print("Entry updated.")
        return True
    print("Edit cancelled.")
    return False


def print_help(extended=False):
    if extended:
        print(f"""
STASH COMMAND CHEAT SHEET

Start Stash:
  stash                 # normal mode (shows banner)
  stash -q              # quiet mode (no banner)

Add an entry:
  a LOCATION: DESCRIPTION
  a LOCATION: DESCRIPTION : TAG1, TAG2

List entries:
  l                     # list all entries alphabetically
  ls                    # list entries unsorted

Find entries:
  f KEYWORDS

Edit and delete:
  e NUMBER              # edit an entry
  d NUMBER              # delete an entry

Other:
  q                     # quit and save
  ? or h or help        # short help
  ? all or help all     # full cheat sheet

Notes:
- Partial keyword search (case-insensitive)
- Multiple tags allowed (comma-separated)
- Auto-save on Ctrl+C
Database: {DB_FILE}
""")
    else:
        print(f"""
Commands:
  a LOCATION: DESCRIPTION
  a LOCATION: DESCRIPTION : TAG1, TAG2
  f KEYWORDS
  l                      (list alphabetically)
  ls                     (list unsorted)
  e NUMBER
  d NUMBER
  q
  ? or h or help
Notes:
  - Type 'help all' for full cheat sheet
  - Database: {DB_FILE}
""")


def main():
    if not (len(sys.argv) > 1 and sys.argv[1] in ("-q", "--quiet")):
        print("""
  ____  _           _     
 / ___|| | __ _ ___| |__  
 \___ \| |/ _` / __| '_ \ 
  ___) | | (_| \__ \ | | |
 |____/|_|\__,_|___/_| |_|

Simple personal stash database
""")

    db = load_db()
    dirty = False

    while True:
        try:
            cmd = prompt(f"[{DB_FILE}] > ").strip()
            if not cmd:
                continue
            if cmd.lower() == "q":
                if dirty:
                    save_db(db)
                break
            elif cmd.lower() == "l":
                list_entries(db)
            elif cmd.lower() == "ls":
                list_entries(db, sort=False)
            elif cmd.lower().startswith("a "):
                add_entry(db, cmd[2:].strip())
                dirty = True
            elif cmd.lower().startswith("f "):
                find_entries(db, shlex.split(cmd[2:].strip()))
            elif cmd.lower().startswith("d "):
                if delete_entry(db, cmd[2:].strip()):
                    dirty = True
            elif cmd.lower().startswith("e "):
                if edit_entry(db, cmd[2:].strip()):
                    dirty = True
            elif cmd.lower() in ("? all", "help all"):
                print_help(extended=True)
            elif cmd.lower() in ("?", "h", "help"):
                print_help()
            else:
                print("Unknown command. Use '?' to see available commands.")
        except KeyboardInterrupt:
            print("\nExiting.")
            if dirty:
                save_db(db)
            break


if __name__ == "__main__":
    main()
