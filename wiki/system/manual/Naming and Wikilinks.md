---
type: wiki
---

# Naming and Wikilinks

The naming convention is the single most consequential decision in the vault — it determines how links resolve, how pages display, and how queries behave. Most of the gotchas live here.

## Filenames

| Type | Filename pattern | Example |
|---|---|---|
| [[Goal]] | `Goal - <Human Name>.md` (Title Case) | `goals/Goal - Grow Online Presence.md` |
| [[Area]] | `Area - <Human Name>.md` | `areas/Area - Productivity.md` |
| [[Project]] | `Project - <Human Name>.md` | `projects/Project - Set Up Obsidian PARA System.md` |
| [[Habit]] | `Habit - <Human Name>.md` | `habits/Habit - Daily Walk.md` |
| [[Daily]] | `YYYY-MM-DD.md` (ISO date) | `daily/2026-05-23.md` |
| [[Wiki]] | freeform Title Case, no Type prefix | `wiki/system/manual/PARA Method.md` |
| Templates / `.base` files | snake_case (config, not content) | `templates/goal.md`, `bases/goals.base` |
| `bases/*.md` dashboards | Title Case (user-facing) | `bases/Project Todos.md` |

**Separator is a plain hyphen with surrounding spaces** (`Type - Name`), not a colon. Colon is forbidden in Obsidian filenames.

## The big rule: filename IS the display name

For the four structured types, the filename matches what you want to see everywhere — tabs, file explorer, graph, Properties UI link chips, [[Bases and Dataview|Bases tables, Dataview output]]. **No `aliases` field is needed.**

This is a deliberate inversion of the more common Obsidian pattern (short filename + alias for display). Why we made the inversion: read on.

## The Obsidian alias gotcha (DON'T re-litigate this)

Obsidian's link resolver consults **filenames only** (`uniqueFileLookup`). It does NOT consult `aliases:` frontmatter for link target resolution. A bare `[[some alias]]` will not resolve and will create a new file on click — even when an existing file has that alias.

Verified against Obsidian 1.12.7. There's a long forum thread about it (the moderator stated: aliases are intentionally for autocomplete + display, not link resolution).

This means alias-based wikilink conventions silently break. Specifically, `[[Goal: X]]` (the original convention I tried) fails for two reasons:
1. The `:` is forbidden in filenames, so clicking errors out.
2. Even with a hyphen, `[[Goal - X]]` still wouldn't resolve unless a file with that exact filename exists.

**Resolution: just make the filename what you want to see.** Then `[[Goal - X]]` works because there's literally a file named `Goal - X.md`.

## Wikilinks

Always written against the **filename** (which IS the human name now). In frontmatter and body alike:

```yaml
areas:
  - "[[Area - Productivity]]"
goals:
  - "[[Goal - Establish Daily Productivity Routines]]"
```

```markdown
See [[Goal - Establish Daily Productivity Routines]] for context.
```

No aliases needed. No pipe-display syntax needed.

## Front Matter Title plugin (removed)

Was installed briefly when we used an alias-based naming convention. **Removed** once we adopted "filename IS the display name", because FMT's `alias.strategy: "ensure"` was injecting synthetic aliases into Obsidian's metadata cache for files that had no `aliases:` field — including the templates in `templates/`. The injected values were wrong (e.g., `templates/area.md` got `aliases: "Area - Productivity"` in cache, the name of an unrelated instance file) and would have polluted Bases queries that read `note.aliases`.

If you ever return to an alias-based or Zettelkasten-style ID-only naming pattern, reinstall FMT — but disable the `alias.ensure` injection.

## See also

- [[PARA Method]] — the six types
- [[Bases and Dataview]] — how queries reference these names
- [[Skills]] — `create-page` enforces this naming, `audit` detects violations
