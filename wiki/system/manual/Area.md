---
type: wiki
---

# Area

An **Area** is a permanent sphere of responsibility — Productivity, Health, Finances, Relationships, whatever organizing dimension you want to track. The "where" of life-organization. Unlike Goals/Projects/Habits, Areas have no status, no end date, and no completion — they exist as long as the sphere does.

## Frontmatter schema

```yaml
---
type: area
---
```

That's it. Areas declare nothing about their relationships — they discover Goals, Projects, etc. via [[Bases and Dataview|backlinks and Dataview queries]].

Filename: `Area - <Human Name>.md` in `areas/`. See [[Naming and Wikilinks]].

## Body sections

The template ships:
- `## Direction` — prose bullets capturing the ongoing intent of this Area. Not goals (those are separate notes); more like "what does success in this area look like in general?"
- `## Active Goals` — Dataview block listing Goals whose `areas:` frontmatter points to this Area.
- `## Active Projects` — Dataview block listing Projects whose `areas:` frontmatter points to this Area.

Both Dataview blocks use `FROM [[]]` — they surface backlinks. The owner doesn't list active children manually.

## Relationship to other types

- **Declares**: nothing.
- **Discovers**: active [[Goal]]s and [[Project]]s via the Dataview slices above. [[Habit]]s come transitively — they belong to a Goal, which belongs to one or more Areas.
- **Is declared by**: [[Goal]] (in its `areas:`) and [[Project]] (in its `areas:`).

## Lifecycle

Areas don't have one. They're permanent. There's no status field, no archived state. If an Area genuinely stops mattering (you sell the house, you leave the field), you delete the page — but that's rare and deliberate, not a workflow.

## See also

- [[PARA Method]] — the six types and where Areas fit
- [[Goal]] and [[Project]] — the types that declare their Area membership
- [[Bases and Dataview]] — how the backlink discovery works
