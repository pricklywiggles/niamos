---
type: wiki
---

# Project

A **Project** is a finite deliverable with a due date. The "what" being built right now. Projects drive one or more [[Goal]]s and belong to one or more [[Area]]s.

## Frontmatter schema

```yaml
---
type: project
status: active                  # active | archived
areas: ["[[Area - <name>]]"]    # list of Area wikilinks
goals: ["[[Goal - <name>]]"]    # list of Goal wikilinks
due_date:                       # date — when the deliverable should land
completion_date:                # date — filled when archived
---
```

Filename: `Project - <Human Name>.md` in `projects/`. See [[Naming and Wikilinks]].

## Body sections

- `## Todos` — checkbox tasks using the [[Bases and Dataview|Tasks plugin]] syntax. Tasks here surface in [[Daily]] notes via due/scheduled date matching, and in the `bases/Project Todos.md` aggregator.
- `## Notes` — prose, links, anything supporting the Project. The [[Skills|archive skill]] prepends to this section when archiving with a reason.

## Relationship to other types

- **Declares**: `areas` (which Area(s) the Project lives under) and `goals` (which Goal(s) it drives).
- **Is discovered by**: [[Goal]] (via the Goal's `## Active Projects` Dataview slice) and [[Area]] (same).

## Lifecycle

- Born `status: active`. Lives until shipped, cancelled, or pivoted.
- Archived via the [[Skills|archive skill]]: flips `status` to `archived`, fills `completion_date`, optionally appends a reason to `## Notes`, moves the file to `archives/<year>/projects/`. See [[Archives]].
- Past-due Projects are flagged by the [[Skills|audit skill]] as stale — but past-due doesn't mean done. Often the right fix is pushing the date forward, not archiving.

## See also

- [[PARA Method]] — where Projects fit in the six-type model
- [[Goal]] and [[Area]] — the upstream types Projects declare
- [[Archives]] — terminal state
- [[Skills]] — `create-page` builds them, `archive` ends them, `daily-review` surfaces their due-today tasks
