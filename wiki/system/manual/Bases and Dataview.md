---
type: wiki
---

# Bases and Dataview

The vault uses **two parallel query mechanisms** for surfacing content, each playing a different role.

## bases/ — standalone dashboards (open them directly)

Files in `bases/` are saved queries you navigate to as their own pages. Two kinds:

### `.base` files (Obsidian Bases plugin — core 1.9+)

Vault-wide YAML queries that render as interactive tables. One per content type:

- `bases/goals.base` — active [[Goal]]s
- `bases/areas.base` — all [[Area]]s
- `bases/projects.base` — active [[Project]]s
- `bases/habits.base` — active [[Habit]]s
- `bases/archives.base` — everything `status: archived`, regardless of type (uses a formula to display the right completion date per type)

All `.base` files exclude `templates/` so the template files themselves don't pollute the indexes.

### `.md` Tasks-query dashboards (Obsidian Tasks plugin)

Aggregators that scan `- [ ]` checkboxes vault-wide:

- `bases/Project Todos.md` — every open task in `projects/`
- `bases/Work Todos.md` — every task tagged `#work` (and nested `#work/...`)
- `bases/Personal Todos.md` — every task tagged `#personal`

## Page-local slices — baked into templates

Some templates ship with their own Dataview blocks that surface "what's relevant *here*". These are NOT in `bases/` — they live inside the content page itself:

- [[Goal]] pages: `## Active Projects` and `## Active Habits` blocks (Projects and Habits whose frontmatter wikilinks point back to this Goal)
- [[Area]] pages: `## Active Goals` and `## Active Projects` blocks (same idea, transitively)
- [[Daily]] notes: `## Today` (Dataview — Goals/Projects with a date matching this daily) and `## Tasks` (Tasks plugin — items due/scheduled today)

The query pattern for "things linking to me" is `FROM [[]]` (the empty wikilink is Dataview's "this file" idiom). The query pattern for date-matching is `WHERE field = date(this.file.name)` (the daily filename is parsed as a date).

## Tasks plugin specifics

Two configured behaviors worth knowing:

1. **`useFilenameAsScheduledDate` is enabled, scoped to `daily/`** — any `- [ ]` task written in a daily note automatically inherits that day as its scheduled date, no `📅` emoji required. Tasks in other folders need explicit dates.
2. **Date syntax in tasks** — Tasks plugin parses these emojis on task lines:
   - `📅 YYYY-MM-DD` — due date
   - `⏳ YYYY-MM-DD` — scheduled date
   - `✅ YYYY-MM-DD` — completion date (set automatically when checked)
   - `🛫 YYYY-MM-DD` — start date

   The [[Skills|daily-review skill]] (morning carry-forward flow) reschedules undone tasks by rewriting the `📅` or `⏳` date in the source file.

## Source-of-truth conventions

- **For "is this archived?" queries**: filter by the `status` property (`status: archived` or `status: active`), never by folder path. Status-based queries survive folder layout changes; folder-based queries don't. [[Archives]] explains why.
- **For "what type is this?"**: filter by the `type` property, not the folder.

## The Dataview inline-DQL gotcha

When writing prose **in this vault** (CLAUDE.md, wiki pages, etc.) about Dataview queries, **never start an inline backtick code span with an equals sign**. Dataview's inline DQL feature treats backtick-equals as a query prefix — it consumes the leading equals and tries to parse the rest as an expression, then errors out in reading view if parsing fails.

Examples (the unsafe one is shown inside a fenced code block below, so it doesn't itself trigger the bug — fenced blocks are immune to inline-DQL parsing):

```
Unsafe inline span:  `== "active"`   ← Dataview eats the first = and chokes on the second.
Safe inline span:    `status == "archived"`   ← Doesn't start with =, so Dataview ignores it.
```

Rule of thumb: if you need to talk about an equality comparison in an inline span, lead with the field name (`field == value`), not the operator. Or use a fenced code block instead of inline backticks.

## See also

- [[Plugin Stack]] — what's installed and why
- [[Naming and Wikilinks]] — link resolution rules that determine what these queries match
- [[Skills]] — `audit` flags Bases that filter by folder instead of status
