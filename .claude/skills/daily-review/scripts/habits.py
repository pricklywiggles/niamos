#!/usr/bin/env python3
"""Compute habit-driven tasks for the daily-review skill.

Two modes:
    habits.py morning <YYYY-MM-DD>
        Emit JSON {fired: [{name, habit_file, cadence}, ...]} for tasks
        whose cadence fires on the given date. Skill orchestrator dedupes
        against today's daily and inserts under ## Habits.

    habits.py evening <YYYY-MM-DD>
        Scan daily/<date>.md's ## Habits section for completed tasks
        (`- [x] ... ✅ <date>` or `- [x] ...`), match each name
        (case-insensitive) against active-habit task lines, and rewrite
        the matching habit-page line's `- last:` to <date>. Emits JSON
        {updated: [...], unchecked: [...]}.

Cadence vocabulary:
    daily              -> interval=1d, anchored on `last:`
    weekly             -> interval=7d, anchored on `last:`
    every Nd / every Nw -> interval=N days / N*7 days
    mon/tue/wed/thu/fri/sat/sun -> calendar weekday
    mon,wed,fri        -> multiple weekdays
    mwf / tth / mth / mtwthf / satsun -> common smushed forms
    weekdays / weekends -> mon-fri / sat-sun aliases
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path


# Script lives at <vault>/.claude/skills/daily-review/scripts/habits.py
VAULT_ROOT = Path(__file__).resolve().parents[4]

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# Match a task line under ## Tasks (habit) or ## Habits (daily).
# Captures: status (' ' or 'x'), rest-of-line.
TASK_LINE_RE = re.compile(r"^- \[([ xX])\] (.+)$")

# Trailing `- last: <maybe-date>` segment on a habit task line.
LAST_SUFFIX_RE = re.compile(r"\s-\s*last:\s*(.*)$")

# Trailing `✅ YYYY-MM-DD` on a completed task in the daily.
DONE_DATE_RE = re.compile(r"\s+✅\s+(\d{4}-\d{2}-\d{2})\s*$")

WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
SMUSHED = {
    "mwf": ["mon", "wed", "fri"],
    "tth": ["tue", "thu"],
    "mth": ["mon", "thu"],
    "mtwthf": ["mon", "tue", "wed", "thu", "fri"],
    "satsun": ["sat", "sun"],
    "weekdays": ["mon", "tue", "wed", "thu", "fri"],
    "weekends": ["sat", "sun"],
}

# Tasks plugin decorates clicked checkboxes with `✅ YYYY-MM-DD`. If a user
# accidentally clicks a habit-page checkbox, this trailing emoji can glue
# onto the cadence segment. Strip it before cadence parsing.
DONE_SUFFIX_RE = re.compile(r"\s*✅\s+\d{4}-\d{2}-\d{2}\s*$")


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return None
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" not in line or line.startswith((" ", "\t", "#")):
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"')
    return fm


def extract_section(text, heading):
    """Return the body lines under `heading` (a string like '## Tasks'), up to the next `## ` heading or EOF.

    Returns list[str] or None if the heading is missing.
    """
    lines = text.splitlines()
    body = []
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            body.append(line)
    return body if in_section else None


def parse_task_line(line):
    """Parse a habit-page task line: `- [<status>] <name> - <cadence>[ - last: <date>]`.

    Returns (status, name, cadence_str, last_str_or_None) or None if the line
    doesn't have the `- <cadence>` segment.
    """
    m = TASK_LINE_RE.match(line)
    if not m:
        return None
    status = m.group(1)
    rest = m.group(2)

    last_str = None
    m_last = LAST_SUFFIX_RE.search(rest)
    if m_last:
        last_str = m_last.group(1).strip() or None
        rest = rest[: m_last.start()]

    sep_idx = rest.rfind(" - ")
    if sep_idx == -1:
        return None
    name = rest[:sep_idx].strip()
    cadence_str = rest[sep_idx + 3 :].strip()
    cadence_str = DONE_SUFFIX_RE.sub("", cadence_str).strip()
    if not name or not cadence_str:
        return None
    return (status, name, cadence_str, last_str)


def parse_cadence(token):
    """Returns ('interval', N_days) or ('weekdays', set[int 0..6]) or None."""
    token = token.strip().lower()
    if token == "daily":
        return ("interval", 1)
    if token == "weekly":
        return ("interval", 7)

    m = re.match(r"^every\s+(\d+)\s*d$", token)
    if m:
        return ("interval", int(m.group(1)))
    m = re.match(r"^every\s+(\d+)\s*w$", token)
    if m:
        return ("interval", int(m.group(1)) * 7)

    parts = [p.strip() for p in token.split(",")] if "," in token else [token]
    weekdays = set()
    for p in parts:
        if p in WEEKDAYS:
            weekdays.add(WEEKDAYS[p])
        elif p in SMUSHED:
            for w in SMUSHED[p]:
                weekdays.add(WEEKDAYS[w])
        else:
            return None
    return ("weekdays", weekdays) if weekdays else None


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.date.fromisoformat(s.strip())
    except ValueError:
        return None


def is_fired(cadence, last_date, today):
    kind, value = cadence
    if kind == "interval":
        if last_date is None:
            return True
        return (today - last_date).days >= value
    if kind == "weekdays":
        return today.weekday() in value
    return False


def iter_active_habits():
    """Yield (rel_path, abs_path, frontmatter, text) for each active habit file."""
    for path in sorted((VAULT_ROOT / "habits").glob("*.md")):
        text = path.read_text()
        fm = parse_frontmatter(text)
        if not fm or fm.get("type") != "habit" or fm.get("status") != "active":
            continue
        yield (str(path.relative_to(VAULT_ROOT)), path, fm, text)


def cmd_morning(today):
    fired = []
    for rel_path, _, _, text in iter_active_habits():
        body = extract_section(text, "## Tasks")
        if body is None:
            continue
        for line in body:
            parsed = parse_task_line(line)
            if parsed is None:
                continue
            _, name, cadence_str, last_str = parsed
            cadence = parse_cadence(cadence_str)
            if cadence is None:
                continue
            last_date = parse_iso(last_str)
            if is_fired(cadence, last_date, today):
                fired.append({
                    "name": name,
                    "habit_file": rel_path,
                    "cadence": cadence_str,
                })
    print(json.dumps({"fired": fired}, indent=2))


def collect_completed_names(daily_text, today):
    """Scan the daily's ## Habits section. Return (completed_names_lower, unchecked_names)."""
    body = extract_section(daily_text, "## Habits")
    if body is None:
        return ([], [])
    completed = []
    unchecked = []
    for line in body:
        m = TASK_LINE_RE.match(line)
        if not m:
            continue
        status, rest = m.group(1), m.group(2)
        # Strip trailing ✅ date if present
        m_done = DONE_DATE_RE.search(rest)
        done_date = None
        if m_done:
            done_date = m_done.group(1)
            rest = rest[: m_done.start()]
        name = rest.strip()
        if not name:
            continue
        if status.lower() == "x":
            # Only credit completions actually marked today (or undated, treat as today).
            if done_date is None or done_date == today.isoformat():
                completed.append(name.lower())
        else:
            unchecked.append(name)
    return (completed, unchecked)


def rewrite_habit_tasks(text, completed_lower, today, seen_global):
    """Walk a habit page's ## Tasks section. Rewrite matched lines' `- last:` to today.

    Returns (new_text, list_of_changed_names).
    """
    lines = text.splitlines()
    out = []
    in_tasks = False
    changes = []
    for line in lines:
        if line.strip() == "## Tasks":
            in_tasks = True
            out.append(line)
            continue
        if in_tasks and line.startswith("## "):
            in_tasks = False
        if in_tasks:
            parsed = parse_task_line(line)
            if parsed is not None:
                _, name, cadence_str, _ = parsed
                name_lower = name.lower()
                if name_lower in completed_lower and name_lower not in seen_global:
                    seen_global.add(name_lower)
                    out.append(f"- [ ] {name} - {cadence_str} - last: {today.isoformat()}")
                    changes.append(name)
                    continue
        out.append(line)
    new_text = "\n".join(out)
    if text.endswith("\n") and not new_text.endswith("\n"):
        new_text += "\n"
    return (new_text, changes)


def cmd_evening(today):
    daily_path = VAULT_ROOT / "daily" / f"{today.isoformat()}.md"
    if not daily_path.exists():
        sys.exit(f"ERROR: daily note not found: daily/{today.isoformat()}.md")

    completed_lower, unchecked = collect_completed_names(daily_path.read_text(), today)

    updated = []
    seen_global = set()
    for rel_path, abs_path, _, text in iter_active_habits():
        new_text, changes = rewrite_habit_tasks(text, completed_lower, today, seen_global)
        if changes:
            abs_path.write_text(new_text)
            for name in changes:
                updated.append({"habit_file": rel_path, "name": name})

    print(json.dumps({"updated": updated, "unchecked": unchecked}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["morning", "evening"])
    parser.add_argument("date", help="ISO date YYYY-MM-DD")
    args = parser.parse_args()

    today = parse_iso(args.date)
    if today is None:
        sys.exit(f"ERROR: invalid ISO date: {args.date}")

    if args.mode == "morning":
        cmd_morning(today)
    else:
        cmd_evening(today)


if __name__ == "__main__":
    main()
