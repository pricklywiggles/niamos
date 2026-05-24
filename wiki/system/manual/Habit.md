---
type: wiki
---

# Habit

A **Habit** is a recurring behavior becoming automatic. The opposite of a [[Project]] — instead of a finite deliverable, a Habit is an ongoing practice that "graduates" when integrated into normal life. Habits drive [[Goal]]s.

## Frontmatter schema

```yaml
---
type: habit
status: active                # active | archived
goals: ["[[Goal - <name>]]"]  # list of Goal wikilinks
start_date:                   # date — when you started practicing it
established_date:             # date — filled when archived ("graduated")
---
```

Note: Habits only declare `goals`, not `areas`. The [[Area]] membership comes transitively through the Goal.

Filename: `Habit - <Human Name>.md` in `habits/`. See [[Naming and Wikilinks]].

## Body sections

- `## Notes` — prose, observations about the habit's progress. The [[Skills|archive skill]] prepends to this section when archiving with a reason.

That's it. Habits are intentionally light on structure — the practice is what matters, not the documentation.

## Relationship to other types

- **Declares**: `goals`.
- **Is discovered by**: [[Goal]] (via the Goal's `## Active Habits` Dataview slice).
- **Does NOT declare**: `areas`. Transitive through Goal.

## Lifecycle and the "established" semantics

- Born `status: active` with a `start_date`. Lives during the active formation period.
- "Archived" is a misnomer for Habits — it's really **graduated**. The Habit is now automatic, integrated, no longer requiring active attention. `established_date` records when this transition happened.
- Mechanically the same as archiving anything else: the [[Skills|archive skill]] flips `status` to `archived`, fills `established_date`, moves the file to `archives/<year>/habits/`. See [[Archives]].
- A Habit could also be abandoned (not established, just stopped). The schema treats both endings the same — `status: archived` with `established_date` set. The body notes are where you record *which* kind of ending it was.

## See also

- [[PARA Method]] — where Habits fit
- [[Goal]] — the upstream type Habits declare
- [[Archives]] — terminal state
- [[Skills]] — `create-page` builds them, `archive` graduates them
