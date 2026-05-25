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

## The Tasks plugin date inference (important)

The Tasks plugin has `useFilenameAsScheduledDate: true` enabled, scoped to `daily/`. This means: any `- [ ]` task you write directly in a daily note **automatically inherits that day as its scheduled date**, no `📅` or `⏳` emoji required. So an inline checkbox in today's daily shows up in the `## Tasks` block of today's daily without extra work.

Tasks elsewhere (in [[Project]] files, etc.) need explicit date emojis to surface in daily Tasks blocks.

## The daily-review skill

The [[Skills|daily-review skill]] is the main workflow for working with Daily notes. Two modes:
- **Morning**: opens today, finds the most recent prior daily, carries forward unfinished inline items (excluding the prior daily's `## Habits` section), inserts today's firing habit tasks into `## Habits`.
- **Evening**: opens today, prompts to mark any unchecked `## Habits` complete, writes back completion dates to each matching habit page's `- last:` field, prompts for highlights, previews tomorrow's commitments.

## Lifecycle

Daily notes have no status. They're temporal records — they don't get archived, don't move folders, don't end. Once a date passes, that daily is historical (read but rarely edit).

## See also

- [[PARA Method]] — where Daily fits in the broader scheme
- [[Skills]] — `daily-review` is the primary skill for Daily workflow
- [[Bases and Dataview]] — Dataview/Tasks query mechanics used in the template
- [[Plugin Stack]] — Tasks plugin filename-as-date setting
