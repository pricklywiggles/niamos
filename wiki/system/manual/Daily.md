---
type: wiki
---

# Daily

A **Daily note** is a temporal record for one calendar day. Not part of the [[PARA Method]] content flow per se — it's a separate temporal layer that records what happened on a specific day, surfaces what's due, and captures highlights.

## Frontmatter schema

```yaml
---
type: daily
date: YYYY-MM-DD          # = file.name, filled by Templater
---
```

Filename: `YYYY-MM-DD.md` in `daily/`. ISO date, no Type prefix. See [[Naming and Wikilinks]].

The Core Daily Notes plugin (configured `folder=daily`, `format=YYYY-MM-DD`, blank template) handles opening today's daily on hotkey. Templater applies the actual template via its folder-template trigger.

## Body sections (template ships these, in order)

- `## Todo` — checkbox tasks for the day. Seeded with `- [ ] Morning review`. The morning daily-review flow appends carried-forward unfinished items from yesterday's body (excluding `## Habits` — those re-derive from cadence).
- `## Habits` — auto-populated by morning daily-review with today's firing habit tasks (see [[Habit]] for cadence semantics). Plain `- [ ] <name>` lines. Check items off here as you do them; evening daily-review writes the completion date back to the habit page's `- last:` field.
- `## Notes` — prose, scratch space, inline `- [ ]` checkboxes for ad-hoc thoughts.
- `## Highlights` — what's worth remembering from this day. Captured by the [[Skills|daily-review skill]] in its evening flow.
- `## Today` — Dataview block surfacing items hitting their date marker today: [[Goal]]s whose `next_assessment_date` or `target_completion_date` is today, [[Project]]s whose `due_date` is today. See [[Bases and Dataview]] for query syntax.
- `## Tasks` — Tasks plugin query block: `(due on <date>) OR (scheduled on <date>)`. Shows all tasks for the day regardless of done/not-done status — completed items render with a strikethrough so they're visually distinct. Renders live in reading mode.
- `## Past due tasks` — Tasks plugin query block: `not done`, `(due before <date>) OR (scheduled before <date>)`, `path does not include daily/`, `path does not include archives/`. Surfaces overdue tasks from `projects/`, `goals/`, `habits/`, and `wiki/` — anywhere with explicit `📅` or `⏳` dates that have slipped. Daily-note tasks are excluded because morning review's auto-carryover already handles them; archives are excluded because finished/abandoned items shouldn't pull attention.

## Injected sections (conditional, not in template)

- `## Schedule` — markdown table of today's calendar events, inserted at the top of the daily (immediately after frontmatter, before `## Todo`) by morning daily-review when at least one calendar source is available. Two columns: `Time` (`All-day` or `H:MM AM/PM` local) and `Event` (title, optionally suffixed with ` — <location>`). Re-running morning review replaces the section in place rather than stacking duplicates. Sources are detected per-session: the `mcp__mcp-ical__list_events` tool (macOS Calendar / EventKit) and the `gws calendar +agenda` CLI (Google Workspace). If neither is available the section is skipped entirely — its absence is not an error.

## The Tasks plugin date inference (important)

The Tasks plugin has `useFilenameAsScheduledDate: true` enabled, scoped to `daily/`. This means: any `- [ ]` task you write directly in a daily note **automatically inherits that day as its scheduled date**, no `📅` or `⏳` emoji required. So an inline checkbox in today's daily shows up in the `## Tasks` block of today's daily without extra work.

Tasks elsewhere (in [[Project]] files, etc.) need explicit date emojis to surface in daily Tasks blocks.

## The daily-review skill

The [[Skills|daily-review skill]] is the main workflow for working with Daily notes. Two modes:
- **Morning**: opens today, finds the most recent prior daily, **automatically** carries forward unfinished inline items (excluding the prior daily's `## Habits` section — no prompt; the user manages overflow by deleting from today's `## Todo` themselves), inserts today's firing habit tasks into `## Habits`, and (if any calendar source is available) inserts today's events into `## Schedule` at the top of the daily.
- **Evening**: opens today, prompts to mark any unchecked `## Habits` complete, writes back completion dates to each matching habit page's `- last:` field, prompts for highlights, and surfaces a 7-day look-ahead (events from any available calendar source + tasks due in that window) in chat — no file edits.

## Lifecycle

Daily notes have no status. They're temporal records — they don't get archived, don't move folders, don't end. Once a date passes, that daily is historical (read but rarely edit).

## See also

- [[PARA Method]] — where Daily fits in the broader scheme
- [[Skills]] — `daily-review` is the primary skill for Daily workflow
- [[Bases and Dataview]] — Dataview/Tasks query mechanics used in the template
- [[Plugin Stack]] — Tasks plugin filename-as-date setting
