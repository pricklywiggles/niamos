---
type: wiki
---

# Skills

Vault-local Claude skills live in `.claude/skills/`. Each one wraps a workflow that's tedious to do by hand and benefits from determinism. Skills call the [[Plugin Stack|Obsidian CLI]] and, where atomicity matters, delegate to Python scripts with rollback.

## The five skills

| Skill | What it does | Triggers on |
|---|---|---|
| **create-page** | Creates a [[Goal]], [[Area]], [[Project]], [[Habit]], or [[Wiki]] page with the right template, fills required fields interactively, opens the file. For Wiki, delegates to `place-wiki` for subfolder choice. | "create a goal/area/project/habit", "new <type>", "add a project for X", "start a habit", "make a wiki page about X" |
| **place-wiki** | Picks a topical subfolder under `wiki/` for a new or existing Wiki page. Pushes back against root dumping. Sometimes invoked standalone, sometimes chained after create-page. | "place wiki", "organize wiki", "where should this go", "move this wiki page", "find a home for X" |
| **archive** | Archives a Goal/Project/Habit (status flip + completion date + optional log entry + file move to `archives/<year>/<type>/`), atomically via `scripts/archive.py`. Also handles un-archive via `scripts/unarchive.py`. See [[Archives]]. | "archive this", "mark done", "shipped", "finished", "wrap up" / "unarchive", "reopen", "reactivate" |
| **daily-review** | Morning or evening flow on the daily note. Morning: find prior daily, surface what didn't get done, offer to carry forward. Evening: surface what got done, prompt for highlights, preview tomorrow. See [[Daily]]. | "morning planning", "let's plan today" → morning / "evening review", "wrap up the day", "what's tomorrow" → evening |
| **audit** | Vault-wide schema validator. Scans for drift (status↔folder mismatch), missing required fields, naming violations, stale active items, frontmatter health, orphan wikilinks. Read-only by default; offers per-finding fix actions on request. Uses `scripts/audit.py`. | "audit", "what's broken", "check for issues", "validate the vault", "find drift" |

## Common patterns across skills

- **Always use the Obsidian CLI** for file ops, property mutations, queries. The CLI goes through Obsidian's API and keeps the metadata cache in sync; raw filesystem ops can desync.
- **Templater must apply for the four structured types.** If the post-create file lacks the expected `type:` line, halt and surface — don't proceed with patches against an unexpected shape.
- **Use AskUserQuestion at decision points**, not for things the skill should figure out from context (existing files, today's date, etc.).
- **Per-finding confirmation on destructive actions.** Even when the user says "fix them all", ask per item — the owner explicitly trusts this pattern after being burned by silent bulk operations elsewhere.

## Why scripts for `archive` and `audit`

Both have multi-step deterministic logic where atomicity (archive) or scan reusability (audit) justifies pulling the work out of SKILL.md into Python. Both scripts:
- Live at `.claude/skills/<skill>/scripts/<name>.py`
- Use the same `run_obsidian()` helper pattern (subprocess wrapper)
- Print structured output (path on success for archive; JSON findings for audit)
- Handle errors with rollback (archive) or report-only semantics (audit)

The other three skills are thin SKILL.md instructions — the work is interactive prompting and individual CLI calls, not deterministic batch work.

## See also

- [[PARA Method]] — what the skills operate on
- [[Naming and Wikilinks]] — the conventions create-page enforces and audit checks
- [[Archives]] — the hybrid model the archive skill implements
- [[Daily]] — the workflow daily-review walks through
