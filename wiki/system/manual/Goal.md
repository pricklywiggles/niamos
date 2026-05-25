---
type: wiki
---

# Goal

A **Goal** is a measurable outcome with an assessment loop. It's the "why" behind active work. Goals belong to one or more [[Area]]s and are driven by [[Project]]s and [[Habit]]s.

## Frontmatter schema

```yaml
---
type: goal
status: active                # active | archived
areas: ["[[Area - <name>]]"]  # list of Area wikilinks (by filename)
next_assessment_date:         # date — when to reassess progress
target_completion_date:       # date — when the goal is supposed to land
actual_completion_date:       # date — filled when archived
---
```

Filename: `Goal - <Human Name>.md` in `goals/`. See [[Naming and Wikilinks]].

## Body sections

The template ships these sections, in order:

- `## Success Metrics` — bullets capturing how you'd know the goal is met. The owner-stated test for a good metric: "Is it easy to enter all your current projects? Do you feel like you know where everything is at? Is it frictionless enough that you're doing it every day?" (these are the success metrics for [[PARA Method|this vault's own foundational goal]]).
- `## Reassessment Logs` — dated log entries. The [[Skills|archive skill]] prepends to this section when archiving with a reason.
- `## Weekly Progress` — narrative notes by week.
- `## Active Projects` — Dataview block listing Projects whose `goals:` frontmatter points to this Goal.
- `## Active Habits` — same for Habits.
- `## Completed Projects and Habits` — combined Dataview list of archived Projects and Habits that pointed to this Goal, sorted by ended date (newest first). Uses `default(completion_date, established_date)` to sort across the two types' different completion-date fields.

The Dataview blocks use `FROM [[]]` (the empty-wikilink "this file" idiom) — they surface backlinks from Projects/Habits that declared this Goal in their frontmatter. The owner doesn't have to list children manually. Archived children still surface in the completed block even though the file moved to `archives/<year>/<type>/`, because the wikilink in their frontmatter is preserved across the move and the query filters by `status: archived` (not folder path) per the [[Archives]] query convention.

## Relationship to other types

- **Declares**: `areas` (which Area(s) this Goal serves).
- **Discovers**: active Projects and Habits, via the Dataview slices above.
- **Does NOT declare**: Projects or Habits. Those declare *upward* to this Goal.

## Lifecycle

- Born `status: active`. Lives until reached, abandoned, or pivoted.
- Archived via the [[Skills|archive skill]]: flips `status` to `archived`, fills `actual_completion_date`, optionally appends a reason to `## Reassessment Logs`, moves the file to `archives/<year>/goals/`. See [[Archives]].
- `next_assessment_date` is the cadence marker — the [[daily review]] surfaces Goals whose assessment is due today, and the [[Skills|audit skill]] flags Goals where assessment is more than 7 days overdue.

## See also

- [[PARA Method]] — where Goals fit in the six-type model
- [[Area]] — the parent type
- [[Project]] and [[Habit]] — the child types that drive Goals
- [[Archives]] — terminal state
- [[Skills]] — `create-page`, `archive`, `audit`, and `daily-review` all touch Goals
