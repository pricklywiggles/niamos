#!/usr/bin/env python3
"""Find past-due vault tasks for the daily-review morning flow.

Usage:
    past_due.py <YYYY-MM-DD>

Emits JSON:
    {
      "tasks": [
        {"file": "projects/...", "line": "23", "date": "2026-06-05", "text": "- [ ] task ..."}
      ]
    }

Only includes incomplete tasks from non-daily/ files with a due (📅) or
scheduled (⏳) date on or before the given cutoff date. Daily notes are
excluded because their inline items are handled separately by the
carryover logic. An empty tasks list is the authoritative answer that
nothing is past due — not a query failure.
"""

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[4]
DATE_RE = re.compile(r"[📅⏳] (\d{4}-\d{2}-\d{2})")


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: past_due.py YYYY-MM-DD")

    try:
        cutoff = datetime.date.fromisoformat(sys.argv[1])
    except ValueError:
        sys.exit(f"ERROR: invalid ISO date: {sys.argv[1]}")

    result = subprocess.run(
        ["obsidian", "tasks", "todo", "verbose", "format=json"],
        capture_output=True, text=True, cwd=str(VAULT_ROOT),
    )
    if result.returncode != 0:
        sys.exit(f"ERROR: obsidian tasks query failed: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: could not parse tasks JSON: {e}")

    raw = data if isinstance(data, list) else data.get("tasks", [])

    past_due = []
    for t in raw:
        text = t.get("text", "")
        file_path = t.get("file", "")
        line = t.get("line", "")

        if "daily/" in file_path:
            continue

        m = DATE_RE.search(text)
        if not m:
            continue

        try:
            task_date = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            continue

        if task_date <= cutoff:
            past_due.append({
                "file": file_path,
                "line": line,
                "date": m.group(1),
                "text": text.strip(),
            })

    print(json.dumps({"tasks": past_due}, indent=2))


if __name__ == "__main__":
    main()
