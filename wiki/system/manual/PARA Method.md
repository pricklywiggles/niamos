---
type: wiki
---

# PARA Method (Niamos variant)

This vault uses a modified PARA method, migrated from a Roam Research setup. The original PARA — Projects, Areas, Resources, Archives — is reorganized here into **six content types** that better match how this vault actually gets used.

## The six types

1. **[[Goal]]** — measurable outcome with an assessment loop. Lives under one or more Areas. The "why" behind active work.
2. **[[Area]]** — permanent sphere of responsibility (Productivity, Health, etc.). No status, no end date. The "where" of life-organization.
3. **[[Project]]** — finite deliverable with a due date. Drives one or more Goals. The "what" being built right now.
4. **[[Habit]]** — recurring behavior becoming automatic. Drives a Goal. Graduates when established.
5. **[[Wiki]]** — durable reference material. Topical, freeform. The "Resources" half of PARA.
6. **[[Archives]]** — not a folder, a *state*. Anything done becomes `status: archived` and moves to `archives/<year>/<type>/`.

## Lifecycle

![[PARA Method.excalidraw|900]]

- **Goals, Projects, Habits** start `status: active` and end `status: archived`.
- **Areas** have no status — they exist as long as that sphere of life does.
- **Wiki** notes are durable and don't move through states.
- **[[Daily]]** notes are a separate temporal record, not part of the PARA flow.

## Relationships are declared once

To avoid duplication and drift:
- **Goal** declares `areas`.
- **Project** declares `areas` AND `goals`.
- **Habit** declares `goals` only (Areas come transitively through the Goal).
- **Area** declares nothing — discovers everything via [[Bases and Dataview|backlinks and Dataview queries]].

The opposite direction (Area → its Goals, Goal → its Projects, etc.) is surfaced at view time, not stored.

## Where to look next

- For the rules on how things are filed and linked: [[Naming and Wikilinks]]
- For the query and dashboard architecture: [[Bases and Dataview]]
- For the plugins underpinning all this: [[Plugin Stack]]
- For the automation around create / archive / daily flows: [[Skills]]
- For per-type schemas and conventions: [[Goal]], [[Area]], [[Project]], [[Habit]], [[Wiki]], [[Daily]], [[Archives]]
