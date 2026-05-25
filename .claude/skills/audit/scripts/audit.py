#!/usr/bin/env python3
"""Vault-wide schema validator. Read-only. Prints JSON findings grouped by category.

Categories: drift, fields, naming, stale, frontmatter, wikilinks, habits

Usage:
    audit.py [--scope <folder>] [--category <name>]
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path


# Script lives at <vault>/.claude/skills/audit/scripts/audit.py
# parents[0]=scripts, [1]=audit, [2]=skills, [3]=.claude, [4]=vault
VAULT_ROOT = Path(__file__).resolve().parents[4]

ACTIVE_FOLDER_TYPE = {
    "goals": "goal",
    "projects": "project",
    "areas": "area",
    "habits": "habit",
    "wiki": "wiki",
    "daily": "daily",
}

# Folders under archives/<year>/ — the archive system mirrors active subfolders
ARCHIVE_FOLDER_TYPE = {
    "goals": "goal",
    "projects": "project",
    "habits": "habit",
}

VALID_TYPES = set(ACTIVE_FOLDER_TYPE.values())

REQUIRED_FIELDS_ACTIVE = {
    "goal": ["type", "status", "areas", "next_assessment_date", "target_completion_date"],
    "project": ["type", "status", "areas", "goals", "due_date"],
    "habit": ["type", "status", "goals", "start_date"],
    "area": ["type"],
    "wiki": ["type"],
    "daily": ["type", "date"],
}

COMPLETION_DATE_FIELDS = {
    "goal": "actual_completion_date",
    "project": "completion_date",
    "habit": "established_date",
}

NAMING_PATTERNS = {
    "goal": re.compile(r"^Goal - .+\.md$"),
    "project": re.compile(r"^Project - .+\.md$"),
    "area": re.compile(r"^Area - .+\.md$"),
    "habit": re.compile(r"^Habit - .+\.md$"),
    "daily": re.compile(r"^\d{4}-\d{2}-\d{2}\.md$"),
    "wiki": None,  # freeform
}

ASSESSMENT_OVERDUE_DAYS = 7

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
STALE_ALIAS_RE = re.compile(r"^(Goal|Area|Project|Habit)\s*-\s*$")

# --- Habit task parsing (mirrors .claude/skills/daily-review/scripts/habits.py) ---
HABIT_TASK_RE = re.compile(r"^- \[[ xX]\] (.+)$")
HABIT_LAST_RE = re.compile(r"\s-\s*last:\s*(.*)$")
HABIT_WEEKDAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
HABIT_SMUSHED = {"mwf", "tth", "mth", "mtwthf", "satsun", "weekdays", "weekends"}
HABIT_STALE_MULTIPLIER = 3  # interval task is "stale" if last > N * cadence ago
HABIT_DONE_SUFFIX_RE = re.compile(r"\s*✅\s+\d{4}-\d{2}-\d{2}\s*$")


def parse_frontmatter(text):
    """Parse our well-controlled frontmatter format.

    Handles scalars, block-style lists, inline-empty `[]`, and quoted strings.
    Returns dict mapping key → str or list[str], or None if no frontmatter.
    """
    m = FM_RE.match(text)
    if not m:
        return None
    fm = {}
    lines = m.group(1).split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith("#"):
            i += 1
            continue
        if line[0] in (" ", "\t"):
            i += 1  # orphan indented line; already consumed by parent list
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if value == "" and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("- "):
            items = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("- "):
                items.append(lines[j].lstrip()[2:].strip().strip('"'))
                j += 1
            fm[key] = items
            i = j
            continue

        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fm[key] = [x.strip().strip('"') for x in inner.split(",")] if inner else []
            i += 1
            continue

        fm[key] = value.strip('"') if value else ""
        i += 1
    return fm


def classify_file(rel_path):
    """Return (folder_label, expected_type, in_archives) or None to skip."""
    parts = rel_path.split("/")
    if len(parts) < 2:
        return None
    top = parts[0]
    if top in ("templates", "bases", "temp"):
        return None
    if top.startswith("."):
        return None
    if top == "archives":
        # Expected layout: archives/<year>/<type-folder>/<filename>
        if len(parts) < 4:
            return None
        type_folder = parts[2]
        if type_folder in ARCHIVE_FOLDER_TYPE:
            return (f"archives/{parts[1]}/{type_folder}", ARCHIVE_FOLDER_TYPE[type_folder], True)
        return None
    if top in ACTIVE_FOLDER_TYPE:
        return (top, ACTIVE_FOLDER_TYPE[top], False)
    return None


def parse_date(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value.strip())
    except ValueError:
        return None


def parse_habit_task_line(line):
    """Parse `- [<status>] <name> - <cadence>[ - last: <date>]`.

    Returns (name, cadence_str, last_str_or_None) or None.
    """
    m = HABIT_TASK_RE.match(line)
    if not m:
        return None
    rest = m.group(1)
    last_str = None
    m_last = HABIT_LAST_RE.search(rest)
    if m_last:
        last_str = m_last.group(1).strip() or None
        rest = rest[: m_last.start()]
    sep_idx = rest.rfind(" - ")
    if sep_idx == -1:
        return None
    name = rest[:sep_idx].strip()
    cadence_str = rest[sep_idx + 3 :].strip()
    cadence_str = HABIT_DONE_SUFFIX_RE.sub("", cadence_str).strip()
    if not name or not cadence_str:
        return None
    return (name, cadence_str, last_str)


def parse_habit_cadence(token):
    """Returns ('interval', N_days) or ('weekdays', set) or None."""
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
    for p in parts:
        if p not in HABIT_WEEKDAYS and p not in HABIT_SMUSHED:
            return None
    return ("weekdays", set(parts))


def extract_section_lines(text, heading):
    """Return list of lines under `heading` until next `## ` or EOF, or None if missing."""
    out = []
    in_section = False
    for line in text.splitlines():
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            out.append(line)
    return out if in_section else None


def make_finding(category, severity, file, rule, detail, fix):
    return {
        "category": category,
        "severity": severity,
        "file": file,
        "rule": rule,
        "detail": detail,
        "fix": fix,
    }


def check_file(rel_path, abs_path, all_filenames, today):
    findings = []
    classification = classify_file(rel_path)
    if classification is None:
        return findings
    folder_label, expected_type, in_archives = classification

    try:
        text = abs_path.read_text()
    except Exception as e:
        findings.append(make_finding("frontmatter", "error", rel_path, "read-error",
            f"Could not read file: {e}", None))
        return findings

    fm = parse_frontmatter(text)
    if fm is None:
        findings.append(make_finding("frontmatter", "error", rel_path, "no-frontmatter",
            "File has no frontmatter block", None))
        return findings

    # frontmatter health
    actual_type = fm.get("type", "")
    if actual_type and actual_type not in VALID_TYPES:
        findings.append(make_finding("frontmatter", "error", rel_path, "unknown-type",
            f"type='{actual_type}' is not one of {sorted(VALID_TYPES)}", None))

    aliases = fm.get("aliases")
    if isinstance(aliases, list):
        for a in aliases:
            if isinstance(a, str) and STALE_ALIAS_RE.match(a):
                findings.append(make_finding("frontmatter", "info", rel_path, "stale-alias-placeholder",
                    f"Stale alias placeholder '{a}' — `aliases` field is no longer used; consider removing",
                    {"kind": "edit-frontmatter", "action": "remove-property", "name": "aliases"}))
                break

    # drift: only meaningful for archivable types (goal/project/habit)
    if expected_type in ("goal", "project", "habit"):
        status = fm.get("status", "")
        if in_archives and status != "archived":
            findings.append(make_finding("drift", "error", rel_path, "status-folder-mismatch",
                f"File is under archives/ but status='{status}' (expected 'archived')",
                {"kind": "invoke-skill", "skill": "archive", "args": f"unarchive {rel_path}"}))
        if not in_archives and status == "archived":
            findings.append(make_finding("drift", "error", rel_path, "status-folder-mismatch",
                f"File has status='archived' but is at {folder_label}/ (expected archives/<year>/{folder_label}/)",
                {"kind": "invoke-skill", "skill": "archive", "args": rel_path}))
        if status == "archived":
            date_field = COMPLETION_DATE_FIELDS[expected_type]
            if not fm.get(date_field):
                findings.append(make_finding("drift", "warning", rel_path, "missing-completion-date",
                    f"status='archived' but {date_field} is empty",
                    {"kind": "edit-frontmatter", "action": "set-date", "name": date_field}))

    # type-folder mismatch
    if actual_type and actual_type != expected_type:
        findings.append(make_finding("drift", "error", rel_path, "type-folder-mismatch",
            f"type='{actual_type}' but file is in {folder_label}/ (expected type='{expected_type}')",
            None))

    # required fields
    fields_type = actual_type if actual_type in REQUIRED_FIELDS_ACTIVE else expected_type
    if fields_type in REQUIRED_FIELDS_ACTIVE:
        for field in REQUIRED_FIELDS_ACTIVE[fields_type]:
            value = fm.get(field)
            if value is None or value == "" or value == []:
                findings.append(make_finding("fields", "warning", rel_path, "missing-required-field",
                    f"Missing required field '{field}' for type='{fields_type}'",
                    {"kind": "edit-frontmatter", "action": "set-field", "name": field}))

    # naming
    pattern = NAMING_PATTERNS.get(expected_type)
    if pattern and not pattern.match(abs_path.name):
        findings.append(make_finding("naming", "error", rel_path, "wrong-filename-format",
            f"Filename doesn't match expected pattern for type='{expected_type}'", None))

    # stale (only for active items)
    if not in_archives and fm.get("status") == "active":
        if expected_type == "project":
            due = parse_date(fm.get("due_date"))
            if due and due < today:
                findings.append(make_finding("stale", "warning", rel_path, "project-overdue",
                    f"Project with status=active has due_date={due.isoformat()} in the past", None))
        elif expected_type == "goal":
            target = parse_date(fm.get("target_completion_date"))
            if target and target < today:
                findings.append(make_finding("stale", "warning", rel_path, "goal-target-overdue",
                    f"Goal with status=active has target_completion_date={target.isoformat()} in the past", None))
            assess = parse_date(fm.get("next_assessment_date"))
            if assess and (today - assess).days > ASSESSMENT_OVERDUE_DAYS:
                findings.append(make_finding("stale", "info", rel_path, "goal-assessment-overdue",
                    f"Goal next_assessment_date={assess.isoformat()} is {(today - assess).days} days in the past", None))

    # habits: per-task checks (active habit pages only)
    if expected_type == "habit" and not in_archives and fm.get("status") == "active":
        body = extract_section_lines(text, "## Tasks")
        if body is not None:
            for line in body:
                if not line.startswith("- ["):
                    continue
                parsed = parse_habit_task_line(line)
                if parsed is None:
                    findings.append(make_finding("habits", "error", rel_path, "malformed-habit-task",
                        f"Task line doesn't parse: '{line.strip()}'", None))
                    continue
                name, cadence_str, last_str = parsed
                cadence = parse_habit_cadence(cadence_str)
                if cadence is None:
                    findings.append(make_finding("habits", "error", rel_path, "unknown-cadence",
                        f"Cadence '{cadence_str}' not recognized for task '{name}'", None))
                    continue
                if last_str:
                    d = parse_date(last_str)
                    if d is None:
                        findings.append(make_finding("habits", "error", rel_path, "invalid-last-date",
                            f"last:'{last_str}' is not ISO YYYY-MM-DD for task '{name}'", None))
                        continue
                    kind, value = cadence
                    if kind == "interval":
                        age = (today - d).days
                        threshold = value * HABIT_STALE_MULTIPLIER
                        if age > threshold:
                            findings.append(make_finding("habits", "warning", rel_path, "habit-task-stale",
                                f"Task '{name}' (cadence {cadence_str}) last:{d.isoformat()} is {age} days ago — past {HABIT_STALE_MULTIPLIER}x cadence threshold ({threshold} days). Either you're missing it or evening write-back isn't running.",
                                None))

    # wikilinks (frontmatter orphans)
    for field_name in ("areas", "goals"):
        items = fm.get(field_name)
        if not items:
            continue
        if isinstance(items, str):
            items = [items]
        for item in items:
            m = WIKILINK_RE.search(str(item))
            if not m:
                continue
            target = m.group(1).strip()
            target_md = f"{target}.md"
            if target_md not in all_filenames:
                findings.append(make_finding("wikilinks", "error", rel_path, "orphan-frontmatter-link",
                    f"Field '{field_name}' has wikilink [[{target}]] but no file with that name exists", None))

    return findings


def check_habit_collisions(vault_root):
    """Cross-file: flag task names that appear in multiple active habits."""
    occurrences = {}  # name_lower -> list[(rel_path, original_name)]
    for path in sorted((vault_root / "habits").glob("*.md")):
        text = path.read_text()
        fm = parse_frontmatter(text)
        if not fm or fm.get("type") != "habit" or fm.get("status") != "active":
            continue
        body = extract_section_lines(text, "## Tasks")
        if body is None:
            continue
        rel_path = str(path.relative_to(vault_root))
        for line in body:
            parsed = parse_habit_task_line(line)
            if parsed is None:
                continue
            name = parsed[0]
            occurrences.setdefault(name.lower(), []).append((rel_path, name))

    findings = []
    for occ in occurrences.values():
        if len(occ) < 2:
            continue
        files = sorted({rel for rel, _ in occ})
        for rel_path, original in occ:
            others = [f for f in files if f != rel_path]
            findings.append(make_finding("habits", "warning", rel_path, "habit-task-collision",
                f"Task '{original}' has the same name (case-insensitive) as a task in: {', '.join(others)}. Evening write-back uses first match; rename one to disambiguate.",
                None))
    return findings


def collect_all_filenames(vault_root):
    """Set of all .md filenames (basenames) in the vault, excluding dotfile paths and templates/."""
    names = set()
    for path in vault_root.rglob("*.md"):
        rel_parts = path.relative_to(vault_root).parts
        if any(p.startswith(".") for p in rel_parts):
            continue
        if rel_parts and rel_parts[0] == "templates":
            continue
        names.add(path.name)
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scope", help="Limit scan to a folder (vault-relative)")
    parser.add_argument("--category", choices=["drift", "fields", "naming", "stale", "frontmatter", "wikilinks", "habits"])
    args = parser.parse_args()

    today = datetime.date.today()

    scope = VAULT_ROOT
    if args.scope:
        scope = VAULT_ROOT / args.scope
        if not scope.exists():
            sys.exit(f"ERROR: scope path does not exist: {args.scope}")

    all_filenames = collect_all_filenames(VAULT_ROOT)

    findings = []
    for path in sorted(scope.rglob("*.md")):
        rel_parts = path.relative_to(VAULT_ROOT).parts
        if any(p.startswith(".") for p in rel_parts):
            continue
        rel_path = str(path.relative_to(VAULT_ROOT))
        findings.extend(check_file(rel_path, path, all_filenames, today))

    findings.extend(check_habit_collisions(VAULT_ROOT))

    if args.category:
        findings = [f for f in findings if f["category"] == args.category]

    summary = {}
    for f in findings:
        summary[f["category"]] = summary.get(f["category"], 0) + 1

    print(json.dumps({"summary": summary, "findings": findings}, indent=2))


if __name__ == "__main__":
    main()
