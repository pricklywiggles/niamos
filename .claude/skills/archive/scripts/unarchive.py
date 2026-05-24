#!/usr/bin/env python3
"""Atomically un-archive a Goal/Project/Habit page.

Flips status back to active, clears the type-specific completion date, and
moves the file back to its original `<type>/` folder. Cleans up empty
`archives/<year>/<type>/` and `archives/<year>/` directories left behind.

Does NOT remove the historical log entry from the archive event — that's
preserved as a record of what happened. If the user wants to scrub the log
they can do it manually.

Usage:
    unarchive.py --path "archives/2026/projects/Project - X.md"

Prints the new vault-relative path on success (so the caller can open it).
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


# Script lives at <vault>/.claude/skills/archive/scripts/unarchive.py
# parents[0]=scripts, [1]=archive, [2]=skills, [3]=.claude, [4]=vault
VAULT_ROOT = Path(__file__).resolve().parents[4]

TYPE_DATE_FIELDS = {
    "goal": "actual_completion_date",
    "project": "completion_date",
    "habit": "established_date",
}

TYPE_FOLDER = {
    "goal": "goals",
    "project": "projects",
    "habit": "habits",
}


def run_obsidian(*args):
    """Run the Obsidian CLI; raise on non-zero exit. Returns stdout (stripped)."""
    result = subprocess.run(["obsidian", *args], capture_output=True, text=True)
    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"obsidian {' '.join(args)}: {msg}")
    return result.stdout.strip()


def read_property(rel_path, name):
    return run_obsidian("property:read", f"name={name}", f"path={rel_path}")


def set_property(rel_path, name, value, ptype=None):
    args = ["property:set", f"name={name}", f"value={value}", f"path={rel_path}"]
    if ptype:
        args.append(f"type={ptype}")
    run_obsidian(*args)


def clear_property_value(abs_path, name):
    """Empty a property's value while keeping the key for template consistency.

    The Obsidian CLI's `property:set value=""` does not reliably empty a value
    (behavior varies), so we do a direct YAML edit. Only touches the matching
    `name: value` line; leaves other frontmatter alone.
    """
    body = abs_path.read_text()
    pattern = re.compile(rf"^({re.escape(name)}:)\s*\S.*$", re.MULTILINE)
    if pattern.search(body):
        new_body = pattern.sub(rf"\1 ", body, count=1)
        abs_path.write_text(new_body)


def move_file(rel_path, dest_folder):
    """Move file to dest_folder (vault-relative). Returns new vault-relative path.

    Same caveats as archive.py: `obsidian move` doesn't mkdir parents and exits 0
    even on ENOENT, so we pre-create the destination and verify post-move.
    """
    (VAULT_ROOT / dest_folder).mkdir(parents=True, exist_ok=True)
    run_obsidian("move", f"path={rel_path}", f"to={dest_folder}/")
    new_rel = f"{dest_folder}/{Path(rel_path).name}"
    if not (VAULT_ROOT / new_rel).is_file():
        raise RuntimeError(
            f"obsidian move reported success but {new_rel} does not exist. "
            "This usually means the move silently failed (CLI returns exit 0 on ENOENT)."
        )
    if (VAULT_ROOT / rel_path).exists():
        raise RuntimeError(
            f"obsidian move reported success but the source file {rel_path} still exists. "
            "File state is inconsistent."
        )
    return new_rel


def cleanup_empty_dirs(start_rel):
    """Walk upward from start_rel removing empty directories, stopping at the vault root.

    `.DS_Store` is treated as ignorable noise — a directory containing only it counts
    as empty for cleanup purposes (macOS sprinkles them everywhere).
    """
    p = (VAULT_ROOT / start_rel).resolve()
    vault = VAULT_ROOT.resolve()
    while p != vault and p.is_dir():
        contents = [c for c in p.iterdir() if c.name != ".DS_Store"]
        if contents:
            break
        ds_store = p / ".DS_Store"
        if ds_store.exists():
            try:
                ds_store.unlink()
            except OSError:
                break
        try:
            p.rmdir()
        except OSError:
            break
        p = p.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="Vault-relative path, e.g. archives/2026/projects/Project - X.md")
    args = parser.parse_args()

    rel_path = args.path
    abs_path = VAULT_ROOT / rel_path

    if not abs_path.is_file():
        sys.exit(f"ERROR: file not found at vault-relative path: {rel_path}")

    if not rel_path.startswith("archives/"):
        sys.exit(f"ERROR: {rel_path} is not under archives/ — refusing to un-archive a file that wasn't archived.")

    page_type = read_property(rel_path, "type")
    status = read_property(rel_path, "status")

    if page_type not in TYPE_DATE_FIELDS:
        sys.exit(f"ERROR: type '{page_type}' is not a recognized archivable type (goal/project/habit).")
    if status != "archived":
        sys.exit(f"ERROR: current status is '{status}', not 'archived'. Nothing to un-archive.")

    date_field = TYPE_DATE_FIELDS[page_type]
    dest_folder = TYPE_FOLDER[page_type]
    original_parent = str(Path(rel_path).parent)

    snapshot = abs_path.read_text()
    moved = False
    new_rel_path = rel_path

    try:
        set_property(rel_path, "status", "active")
        clear_property_value(abs_path, date_field)
        new_rel_path = move_file(rel_path, dest_folder)
        moved = True
        cleanup_empty_dirs(original_parent)
    except Exception as e:
        if moved:
            try:
                run_obsidian("move", f"path={new_rel_path}", f"to={original_parent}/")
            except Exception:
                pass
        restore_target = VAULT_ROOT / rel_path
        if restore_target.exists():
            restore_target.write_text(snapshot)
        sys.exit(f"ERROR: {e}. Attempted rollback.")

    print(new_rel_path)


if __name__ == "__main__":
    main()
