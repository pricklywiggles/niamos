# Audit categories

Reference for each check the audit script runs. Use this to understand
what a finding means and what the appropriate fix is.

## drift

The hybrid archive model says `status: archived` ↔ file lives at
`archives/<year>/<type>/`. Drift means the two indicators disagree, or
the type-specific completion date is missing.

| Rule | What it detects | Fix |
|---|---|---|
| `status-folder-mismatch` (error) | `status: archived` but file is NOT in `archives/`, OR file IS in `archives/` but `status` is `active` (or missing) | Invoke `archive` skill (`/archive <name>` or `/archive unarchive <name>`) — the script will sort the status flip, date set, and move atomically |
| `missing-completion-date` (warning) | `status: archived` but the type-specific date field (`actual_completion_date` / `completion_date` / `established_date`) is empty | Prompt user for the date, then Edit the frontmatter (CLI's `property:set` with `type=date`) |
| `type-folder-mismatch` (error) | File in `archives/2026/projects/` whose `type` is `goal` (folder says project, frontmatter says goal) | Manual — usually means a file was moved to the wrong subfolder; user picks the correct destination |

## fields

Required frontmatter fields per type are listed in CLAUDE.md "Frontmatter
schemas". Missing fields don't break Obsidian, but they break Bases and
the skill workflows that read them.

| Type | Required for active | Required when archived (additional) |
|---|---|---|
| Goal | `type`, `status`, `areas`, `next_assessment_date`, `target_completion_date` | `actual_completion_date` |
| Project | `type`, `status`, `areas`, `goals`, `due_date` | `completion_date` |
| Habit | `type`, `status`, `goals`, `start_date` | `established_date` |
| Area | `type` | (Areas have no archived state) |
| Wiki | `type` | (Wiki not archivable) |
| Daily | `type`, `date` | (Daily not archivable) |

| Rule | Fix |
|---|---|
| `missing-required-field` (warning) | Prompt user for the value, then Edit the frontmatter (use CLI `property:set` so the metadata cache updates) |

## naming

Conventions from CLAUDE.md "Naming":
- Goal/Area/Project/Habit: `<Type> - <Human Name>.md` (Title Case, plain
  hyphen separator with spaces)
- Daily: `YYYY-MM-DD.md` (ISO date)
- Wiki: freeform Title Case, no Type prefix
- Templates and `.base` files: snake_case (config, not content)

| Rule | What it detects | Fix |
|---|---|---|
| `wrong-filename-format` (error) | A content file whose filename doesn't match its type's convention | Propose a corrected filename, use `obsidian rename` (which updates incoming wikilinks) |
| `type-folder-mismatch-by-folder` (error) | File in `goals/` whose `type` property isn't `goal` (etc.) | Manual — could mean the type is wrong, or the file is in the wrong folder. User decides. |

## stale

Active items past their date markers. NOT auto-archived — past-due
doesn't mean done; often the right fix is pushing the date.

| Rule | What it detects | Fix |
|---|---|---|
| `project-overdue` (warning) | Project with `status: active` and `due_date` < today | Surface; user decides: archive (if done), update due_date (if pushed), or leave (if known late) |
| `goal-target-overdue` (warning) | Goal with `status: active` and `target_completion_date` < today | Same — user decides |
| `goal-assessment-overdue` (info) | Goal with `status: active` and `next_assessment_date` more than 7 days in the past | Suggest the user run their reassessment cycle; advance the date to the next interval |

## frontmatter

Health of the YAML frontmatter itself, independent of which specific
fields it should have.

| Rule | What it detects | Fix |
|---|---|---|
| `no-frontmatter` (error) | Content file with no frontmatter block at all | Manual — usually means the user created a file without the template firing. Offer to apply the right template via Templater. |
| `unknown-type` (error) | `type` field has a value that isn't one of `goal`/`area`/`project`/`habit`/`wiki`/`daily` | Manual — typo or schema drift; user fixes the value |
| `stale-alias-placeholder` (info) | `aliases` field present with values like `"Goal - "` (trailing space, no name) — leftover from the alias-saga refactor where the field was removed from templates but old files still have it | Remove the `aliases` field via `obsidian property:remove` |

## wikilinks

Frontmatter wikilink integrity. The skill checks list-fields (`areas`,
`goals`) for links to non-existent files. Body wikilinks are out of
scope — Obsidian's native "Show unresolved links" view handles those.

| Rule | What it detects | Fix |
|---|---|---|
| `orphan-frontmatter-link` (error) | A wikilink in a frontmatter list field whose target file doesn't exist in the vault | Two paths: (a) remove the link if it shouldn't be there; (b) create the missing page via `/create-page`. User picks. |

## severity legend

- `error` — schema violation that breaks queries or workflows. Fix
  recommended.
- `warning` — something to be aware of; might be intentional. User decides.
- `info` — informational; flagging for context, no action required.
