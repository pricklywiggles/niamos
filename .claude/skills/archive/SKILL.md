---
name: archive
description: >-
  Archive or un-archive a Goal, Project, or Habit in this Obsidian vault.
  **Archiving** flips `status: active` → `status: archived`, fills the
  type-specific completion-date field (Goal → `actual_completion_date`,
  Project → `completion_date`, Habit → `established_date`), optionally
  prepends a dated reason to the page's log section, and moves the file to
  `archives/<year>/<type>/`. **Un-archiving** is the inverse: flips status
  back, clears the date, moves the file back to its original `<type>/`
  folder, and cleans up empty archive subdirectories. Use this skill
  whenever the user says: "archive this", "archive <name>", "mark done",
  "this is finished", "complete this goal/project", "this habit is
  established", "we shipped X", "I finished X", "wrap this up", "abandon
  this goal" → archive direction; "unarchive this", "unarchive <name>",
  "reopen this project", "reactivate this goal", "this isn't done yet",
  "actually this is still active", "revive this", "bring this back" → 
  un-archive direction. Validates type and current status, refuses politely
  for Areas (permanent) and Wiki/Daily (not archivable), and opens the file
  at its new location so the user can verify. All multi-step mutations
  happen atomically via bundled scripts with best-effort rollback — drift
  between status and folder location is prevented by design.
---

# Archive / un-archive a page

The vault `CLAUDE.md` "Status semantics" is the authoritative source for
how endings are represented. This skill executes either *flip-to-archived-
and-move* or its inverse, depending on user intent.

The actual file mutations are bundled in two scripts:
- `scripts/archive.py` — active → archived
- `scripts/unarchive.py` — archived → active

Both handle status flip + date set/clear + (for archive) optional log
insert + file move as an atomic sequence with best-effort rollback. Don't
reimplement these operations in Claude — always call the script.

## Workflow

### 1. Determine direction

Read the user's intent from their message:

- "archive", "mark done", "shipped", "finished", "abandon", "wrap up",
  "complete this" → **archive** (active → archived).
- "unarchive", "reopen", "reactivate", "revive", "bring back", "actually
  still active", "not done yet" → **unarchive** (archived → active).

If ambiguous, ask via AskUserQuestion before proceeding.

### 2. Identify the target file

Pick the file path based on what the user gave you:

- **Explicit vault-relative path** (`projects/Project - X.md` or
  `archives/2026/projects/Project - X.md`): use as-is.
- **Filename or wikilink-style name** (`Project - X`): resolve via
  `obsidian properties file="<name>"` to get the path. If the CLI returns
  nothing, stop and ask the user to disambiguate.
- **No target given** (the user said "archive this" / "I'm done" / 
  "reopen this"): use the active file. `obsidian properties active`
  returns its metadata including the path.

### 3. Pre-flight check (friendly refusals for non-archivable types)

Read the type so you can give a type-aware refusal *before* invoking the
script. The script also validates, but its error messages are terse.

```
obsidian property:read name=type path="<path>"
```

| type        | What to do                                                       |
|-------------|------------------------------------------------------------------|
| `goal`      | Proceed                                                          |
| `project`   | Proceed                                                          |
| `habit`     | Proceed                                                          |
| `area`      | Refuse: "Areas are permanent spheres of responsibility (per CLAUDE.md) — they don't get archived. If the area is no longer relevant, the underlying Goals/Projects/Habits get archived instead." |
| `wiki`      | Refuse: "Wiki notes are reference material — they're durable. If the content is wrong, edit or delete it; archiving doesn't apply." |
| `daily`     | Refuse: "Daily notes are temporal records — they don't have an active/archived state." |
| (missing)   | Refuse: "This file has no `type` property — can't tell what it is. Either it's not a vault content page, or its frontmatter is malformed." |

### 4. Archive-specific inputs (skip for un-archive)

**Completion date** — default today (ISO `YYYY-MM-DD`). Only ask for an
alternate if the user mentioned one in their original message ("we shipped
this last Friday" → resolve to that date). Don't reflexively prompt — most
archives happen on the day of completion.

**Reason** (optional) — if the user supplied a reason in their original
message ("we're killing this because the API was deprecated"), capture it
as a single line. If they didn't, don't prompt — the reason is genuinely
optional, and the date field records *when* regardless.

### 5. Call the appropriate script

**Archive direction:**
```
.claude/skills/archive/scripts/archive.py --path "<path>" --date <YYYY-MM-DD> [--reason "<reason>"]
```

The script will: re-validate type and active status → snapshot the file →
set `status: archived` → set the type-specific date field as `type=date`
→ insert `- [[YYYY-MM-DD]] <reason>` after the section heading if reason
supplied (`## Reassessment Logs` for Goal; `## Notes` for Project/Habit)
→ move the file to `archives/<year>/<type>/`. On any failure, restore
snapshot and move file back to original location.

**Un-archive direction:**
```
.claude/skills/archive/scripts/unarchive.py --path "<path>"
```

The script will: validate the file is under `archives/`, type is
goal/project/habit, status is archived → snapshot → flip status to
active → clear the type-specific date field (keeps the YAML key with an
empty value, matching the template) → move file back to its original
`<type>/` folder → clean up empty `archives/<year>/<type>/` and
`archives/<year>/` directories left behind. On failure, same rollback.

**Note**: un-archive does NOT remove the historical log entry from the
archive event. That stays as a record of what happened. If the user
explicitly wants it scrubbed, do it via Edit after the script returns.

On success either script prints the new vault-relative path. Capture that
for step 6.

### 6. Open the file

```
obsidian open path="<new-path-from-script>"
```

Return one short sentence:
- Archive: "Archived `<filename>` → `<new-path>` as of `<date>`."
- Un-archive: "Un-archived `<filename>` → `<new-path>`."

## Rules

- **Three archivable types only.** Goal, Project, Habit. Refuse for Area
  (permanent), Wiki (durable reference, not archivable), Daily (temporal,
  no status). Refusals should briefly explain *why* — the user may not
  know the semantics.
- **Always call the script for mutations.** Don't reach for individual
  `property:set` / `move` CLI calls from Claude. The scripts' value is
  atomicity: either all operations land together, or none do (modulo the
  small partial-state window during rollback). Bypassing them reintroduces
  drift between status and folder.
- **Never bulk-archive or bulk-unarchive.** One file per invocation. If
  the user asks "archive everything I finished this quarter" or "unarchive
  all my abandoned goals", that's an audit/reorg pass — decline and
  suggest doing it one at a time or invoking the `audit` skill (when it
  exists).
- **Date field is the source of truth for *when*.** The archive script
  uses `type=date` so Bases' `formula.ended_on` and the Properties UI
  treat it as a real Date. Don't write the date inside the body and skip
  the property.
- **Un-archive preserves history.** The log entry from the original
  archive event is intentionally left intact — it remains true that the
  page *was* archived on date X, even if it's now active again. If the
  user wants the log scrubbed, that's a separate manual edit.
- **Obsidian CLI quirk worth remembering**: `obsidian move` returns exit
  code 0 even when the rename fails with ENOENT (e.g., destination folder
  doesn't exist). The scripts work around this by pre-creating the
  destination and verifying the file actually moved post-call. Any other
  skill using `move` should do the same.
