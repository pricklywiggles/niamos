#!/usr/bin/env python3
"""Atomically archive a Goal/Project/Habit page.

Flips status to archived, sets the type-specific completion date, optionally
prepends a dated log entry, and moves the file to archives/<year>/<type>/.
All mutations go through the Obsidian CLI so the metadata cache stays in sync.

On any failure mid-sequence, attempts rollback: file content is restored from
the pre-flight snapshot, and if the file was already moved it's moved back.

Usage:
    archive.py --path "projects/Project - X.md" --date 2026-05-23 [--reason "..."]

Prints the new vault-relative path on success (so the caller can open it).
"""

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path


# Script lives at <vault>/.claude/skills/archive/scripts/archive.py
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

TYPE_LOG_SECTION = {
    "goal": "## Reassessment Logs",
    "project": "## Notes",
    "habit": "## Notes",
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


def insert_log_line(abs_path, section, log_line):
    """Insert log_line immediately after the section heading (most-recent-first)."""
    body = abs_path.read_text()
    pattern = re.compile(rf"({re.escape(section)}\n)")
    if not pattern.search(body):
        raise RuntimeError(f"Section '{section}' not found; cannot append log entry.")
    new_body = pattern.sub(rf"\1{log_line}\n", body, count=1)
    abs_path.write_text(new_body)


def move_file(rel_path, dest_folder):
    """Move file to dest_folder (vault-relative). Returns new vault-relative path.

    `obsidian move` does not create intermediate directories and — worse — exits 0
    even when the rename fails with ENOENT. So we mkdir -p the destination
    ourselves and then verify the file actually landed there.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="Vault-relative path, e.g. projects/Project - X.md")
    parser.add_argument("--date", required=True, help="Completion date YYYY-MM-DD")
    parser.add_argument("--reason", default="", help="Optional reason; appended as a dated log entry")
    args = parser.parse_args()

    rel_path = args.path
    abs_path = VAULT_ROOT / rel_path

    if not abs_path.is_file():
        sys.exit(f"ERROR: file not found at vault-relative path: {rel_path}")

    try:
        completion = datetime.date.fromisoformat(args.date)
    except ValueError:
        sys.exit(f"ERROR: invalid date (need YYYY-MM-DD): {args.date}")

    page_type = read_property(rel_path, "type")
    status = read_property(rel_path, "status")

    if page_type not in TYPE_DATE_FIELDS:
        sys.exit(f"ERROR: type '{page_type}' is not archivable. Allowed: goal, project, habit.")
    if status != "active":
        sys.exit(f"ERROR: current status is '{status}', not 'active'. Refusing to re-archive.")

    date_field = TYPE_DATE_FIELDS[page_type]
    type_folder = TYPE_FOLDER[page_type]
    dest_folder = f"archives/{completion.year}/{type_folder}"

    snapshot = abs_path.read_text()
    moved = False
    new_rel_path = rel_path

    try:
        set_property(rel_path, "status", "archived")
        set_property(rel_path, date_field, args.date, ptype="date")

        if args.reason:
            log_line = f"- [[{args.date}]] {args.reason}"
            insert_log_line(abs_path, TYPE_LOG_SECTION[page_type], log_line)

        new_rel_path = move_file(rel_path, dest_folder)
        moved = True
    except Exception as e:
        # Best-effort rollback: undo the move (if any), restore content from snapshot.
        if moved:
            try:
                run_obsidian("move", f"path={new_rel_path}", f"to={os.path.dirname(rel_path)}/")
            except Exception:
                pass
        restore_target = VAULT_ROOT / rel_path
        if restore_target.exists():
            restore_target.write_text(snapshot)
        sys.exit(f"ERROR: {e}. Attempted rollback.")

    print(new_rel_path)


if __name__ == "__main__":
    main()
