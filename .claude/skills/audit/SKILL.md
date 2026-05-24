---
name: audit
description: >-
  Scan this Obsidian vault for content that's drifted from the conventions
  in `CLAUDE.md` (status↔folder drift, missing required fields, naming
  violations, stale active items, frontmatter health issues, orphan
  wikilinks). Produces a categorized report and offers per-finding fix
  actions — never auto-bulk-fixes. Use this skill whenever the user says
  any of: "audit the vault", "audit", "what's broken", "check for
  issues", "validate the vault", "run a checkup", "find inconsistencies",
  "any drift?", "lint the vault", "fix orphan links", "check schema",
  "is everything in order", "sanity check the vault", "tidy up", or any
  similar request for a vault-wide health check. The actual scanning is
  bundled in `scripts/audit.py` (deterministic, fast, no side effects);
  this skill formats its output and walks through fixes one at a time.
---

# Audit the vault

Scan this Obsidian vault for drift from the `CLAUDE.md` schema. The
scanning is bundled in `scripts/audit.py` — a read-only Python script
that walks the vault, parses frontmatter, runs each check, and prints a
structured JSON report. This skill's job is to call the script, format
the output for the conversation, and walk through fixes interactively
when the user wants them.

For per-category details (what each check looks for, how to fix it,
severity), read `references/categories.md` once at the start of a
session that uses this skill. Don't re-read on every invocation.

## Workflow

### 1. Determine scope

Parse the user's request:
- "audit the vault" / no args → full scan
- "audit projects/" / "check the wiki" → pass `--scope <folder>`
- "any orphan links?" / "fix naming" → pass `--category <name>`
  - Categories: `drift`, `fields`, `naming`, `stale`, `frontmatter`,
    `wikilinks`

### 2. Run the scan

```
.claude/skills/audit/scripts/audit.py [--scope <folder>] [--category <name>]
```

The script prints a JSON object:
```json
{
  "summary": {"drift": 2, "fields": 0, "naming": 1, "stale": 3, ...},
  "findings": [
    {
      "category": "drift",
      "severity": "error",
      "file": "projects/Project - X.md",
      "rule": "status-folder-mismatch",
      "detail": "File has status: archived but is in projects/ (expected archives/<year>/projects/)",
      "fix": {"kind": "invoke-skill", "skill": "archive", "args": "..."}
    },
    ...
  ]
}
```

### 3. Format the report

Print a categorized summary in the conversation. Use a tight layout:

```
Audit report (15 findings across 4 categories):

drift (2 errors)
  • projects/Project - Foo.md — status: archived but in projects/ → invoke `/archive` to relocate
  • archives/2025/projects/Project - Bar.md — status: active but in archives/ → invoke `/archive unarchive`

fields (1 warning)
  • goals/Goal - Baz.md — missing required: target_completion_date

naming (3 errors)
  • projects/foo.md — filename doesn't match `Project - <Human Name>.md`
  ...
```

One line per finding, file path first, rule short-name, then a brief
"how to fix" hint. Group by category. Severity order: error first, then
warning, then info. Don't dump every detail — the script's JSON has the
full context if the user wants to dig in.

If there are zero findings: "Vault is clean — no drift detected." End.

### 4. Offer per-finding fix actions (only if user asks)

If the user says "fix them" / "walk me through them" / "let's clean up"
after seeing the report, iterate through findings whose `fix.kind` is
set, asking the user via AskUserQuestion for each:

- `invoke-skill`: "Run the suggested skill for this finding?" → yes
  invokes the named skill via the Skill tool with the recorded args.
- `edit-frontmatter`: "Apply the suggested frontmatter edit?" → yes uses
  Edit on the file.
- `rename`: "Rename to the suggested filename?" → yes uses `obsidian
  rename`.
- `manual`: no fix offered — surface to the user and move on.

**Never apply a fix without explicit per-finding confirmation.** Even
when the user said "fix them all", ask per finding — the user has been
burned by silent bulk operations elsewhere and explicitly trusts the
per-finding-confirm pattern.

If the user wants to skip the interactive fixes: "Run again with `--fix`
later, or invoke individual skills (`/archive`, `/create-page`) as
needed." End.

### 5. Close

One short summary: "Audit done — 15 findings reported, 3 fixed." Or, if
no fix loop: "Audit done — 15 findings reported."

## Rules

- **Read-only by default.** The script never mutates. Fix actions happen
  through this skill orchestrating Edit / Skill calls based on the
  script's recommendations — not through the script itself.
- **One fix per AskUserQuestion.** Don't batch fixes into multi-select
  questions. The user needs to see each one in context to decide
  responsibly.
- **The script is the source of truth for what's "wrong".** Don't
  re-implement checks in Claude. If a check needs to change, update the
  script (`scripts/audit.py`) and `references/categories.md`. Drift
  between the two breaks the skill.
- **Skip body wikilinks for v1.** The script checks frontmatter
  wikilinks for orphans (the `areas`, `goals` etc. fields). Body
  wikilinks are out of scope — Obsidian's own "Show unresolved links"
  view handles those. If the user explicitly asks "scan body links too",
  decline and suggest the native view.
- **Stale active items are flagged, not auto-archived.** A past
  `due_date` doesn't mean a Project should be archived — it might just
  be late. Surface the finding and let the user decide (often the right
  fix is pushing the date forward, not archiving).
