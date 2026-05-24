---
type: wiki
---

# Archives

Archives is a **state**, not a content type — anything done becomes `status: archived` in its frontmatter AND moves to a folder under `archives/`. This page documents the hybrid model and why it's structured the way it is.

## What gets archived

Only the three terminal-state types: [[Goal]], [[Project]], [[Habit]]. [[Area]] is permanent (no status). [[Wiki]] is durable reference material. [[Daily]] is temporal record. None of those four have an archived state.

## The hybrid model

When a Goal/Project/Habit is archived, **two things happen atomically**:

1. **Status flip**: `status: active` → `status: archived` in the frontmatter
2. **File move**: the file moves from `<type>/` to `archives/<year>/<type>/`, where `<year>` comes from the relevant completion date

Plus the type-specific completion date field is filled:
- [[Goal]] → `actual_completion_date`
- [[Project]] → `completion_date`
- [[Habit]] → `established_date`

Plus, if a reason was supplied, a dated log entry is prepended to the appropriate section (Reassessment Logs for Goal, Notes for Project/Habit).

All four mutations happen as one operation via the [[Skills|archive skill]]'s bundled Python script (`scripts/archive.py`) with best-effort rollback on failure.

## Why hybrid, why not just status?

Pros of moving the file:
- Browsing the active folder (e.g., `projects/`) shows only active work, no archived clutter
- Over years, active sets stay small and scannable
- `archives/<year>/<type>/` is naturally browsable by date

Pros of also keeping the status field:
- Queries can filter by `status: archived` independent of folder path
- If the folder layout ever changes, queries don't break
- [[Bases and Dataview|Bases and Dataview]] filter on status, not folder

The cost of hybrid is **drift risk**: status and folder could disagree if one is updated without the other. Mitigations: archive script does both atomically; [[Skills|audit skill]] checks for drift.

## Source of truth conventions

- **For queries** ("show me everything archived"): use `status: archived`. Location-independent, robust to layout changes.
- **For browsing** ("let me find that project from 2026"): navigate to `archives/2026/projects/`. Folder location is the visual filing system.

## Un-archiving

Rare but supported. The [[Skills|archive skill]] also handles unarchive (via `scripts/unarchive.py`): flips status back, clears the completion date, moves the file back to its active folder, cleans up empty `archives/<year>/<type>/` and `archives/<year>/` directories. Historical log entries are preserved — it's still true that the page was once archived on date X.

## The archives.base index

`bases/archives.base` is the master view of everything archived, regardless of type. It filters by `note.status == "archived"` and uses a formula column `ended_on` to display whichever completion date is set (`actual_completion_date` / `completion_date` / `established_date`).

## See also

- [[PARA Method]] — the six types and where Archives sits
- [[Goal]], [[Project]], [[Habit]] — the three archivable types
- [[Skills]] — the archive skill that orchestrates this
- [[Bases and Dataview]] — the `archives.base` index and the status-vs-folder query rule
