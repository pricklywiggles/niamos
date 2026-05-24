---
name: create-page
description: >-
  Create a new Goal, Area, Project, Habit, or Wiki page in this Obsidian vault.
  Triggers when the user says any of: "create a goal/area/project/habit", "new
  <type>", "add a project for X", "start a habit", "make a wiki page about X",
  or any similar new-page intent for one of those five types. Picks the right
  folder, generates a snake_case filename, applies the type's template via
  Templater, fills the alias, prompts for required relationship and date fields
  (offering existing pages as choices for relationships), and opens the file in
  Obsidian. Does not seed body content.
---

# Create a page

The vault `CLAUDE.md` at the repo root is the authoritative spec for folders,
schemas, naming, and conventions. Read it before acting if you have not loaded
it. This skill executes the *create-a-new-page* workflow against that spec.

## Workflow

### 1. Determine type

Goal / Area / Project / Habit / Wiki. If the user's request makes it obvious
("create a goal for X"), use that. Otherwise ask with AskUserQuestion.

### 2. Determine human name

Use the name the user gave. If absent, ask.

### 3. Generate filename

For Goal/Area/Project/Habit: `<Type> - <Human Name>.md` (Title Case, plain
hyphen, ` - ` separator with spaces). Preserve acronyms (PARA, API) as the
user typed them; title-case the rest. Strip filename-forbidden characters
(`:`, `\`, `/`, `*`, `?`, `<`, `>`, `|`, `"`).

Examples:
- `"Grow online presence"` (Goal) → `Goal - Grow Online Presence.md`
- `"Set up obsidian PARA system"` (Project) → `Project - Set Up Obsidian PARA System.md`

For Wiki: freeform filename matching the human name, Title Case.
Example: `"Sourdough hydration"` → `Sourdough Hydration.md`.

Target folder by type:
- Goal → `goals/`
- Area → `areas/`
- Project → `projects/`
- Habit → `habits/`
- Wiki → handled by the `place-wiki` skill (skip steps 3-7 of this
  workflow for Wiki; see "Wiki delegation" below).

If the file already exists at that path, stop. Ask whether to open the
existing one, pick a different name, or cancel.

**Wiki delegation:** if the requested type is Wiki, do not create the file
here. Instead, invoke the `place-wiki` skill via the Skill tool with the
human topic name. `place-wiki` decides the right subfolder, creates the
file at the chosen path, and opens it. This skill's job ends after the
delegating Skill call. Don't pre-create a flat file and then move it —
that's two operations where one suffices, and the move would orphan any
hand-written links.

### 4. Create the file

For Goal, Area, Project, Habit — apply the type template via Templater:

```
obsidian templater:create-from-template template="templates/<type>.md" file="<folder>/<filename>.md"
```

After creation, read the file to confirm the expected `type:` line is present.
If not, Templater did not fire correctly — surface this to the user and stop.
Do not proceed with patches against an unexpected file shape.

### 5. (No alias patch needed)

Filenames carry the display name across every surface (tabs, file explorer,
Properties chips, Bases, Dataview output), so there is no separate `aliases`
field to fill. Skip to step 6.

### 6. Collect required fields

One AskUserQuestion per missing field. Per type:

| Type    | Relationship fields           | Date fields                                  |
|---------|-------------------------------|----------------------------------------------|
| Goal    | `areas`                       | `next_assessment_date`, `target_completion_date` |
| Area    | (none)                        | (none)                                       |
| Project | `areas`, `goals`              | `due_date`                                   |
| Habit   | `goals`                       | `start_date`                                 |
| Wiki    | (none)                        | (none)                                       |

**Relationship fields** (`areas`, `goals`): list existing pages of that type
and present them as multi-select options. Discover with
`obsidian files folder=<target_folder>`. The filename (sans `.md`) IS the
human-readable label and IS the wikilink target. Always include an
"Other — create new" option that recursively invokes this skill for the
missing type, then resumes.

**Date defaults applied silently** (no question asked):
- Goal `next_assessment_date` = today + 4 weeks (ISO `yyyy-mm-dd`).
- Habit `start_date` = today (ISO `yyyy-mm-dd`).

For `target_completion_date` (Goal) and `due_date` (Project), always ask. ISO
format only.

### 7. Patch the frontmatter

Apply the collected values via Edit, targeting one field at a time. Date
fields become bare YAML dates (`due_date: 2026-08-15`). Relationship fields
become YAML lists of wikilink strings — the target is the filename (sans
`.md`), which IS the human-readable name:

```yaml
areas:
  - "[[Area - Productivity]]"
  - "[[Area - Professional Development]]"
```

When replacing `areas: []` (empty placeholder) with a populated list, edit the
full line. Same shape for `goals`.

Do not touch the body. Leave Success Metrics, Reassessment Logs, Weekly
Progress, Todos, Notes, Direction, etc. blank for the user to fill.

### 8. Open the file

```
obsidian open path="<folder>/<filename>.md"
```

Return control with at most one short sentence ("Created and opened `<file>`.").

## Rules

- **Never seed body content.** No example metrics, todos, prose, or links
  beyond the required relationship fields.
- **Stop on dangling references.** If the user wants to link an Area that
  doesn't exist, offer to create it first via this same skill, then continue.
  Never silently create a wikilink to a nonexistent file.
- **One side of each relationship.** Project declares `areas` and `goals`;
  Goal does not declare projects. Habit declares `goals`; Goal does not
  declare habits. Area declares nothing. Match the vault `CLAUDE.md` schemas
  exactly.
- **Templater must apply for the four structured types.** If the post-create
  file lacks the expected `type:` line, halt and report — do not proceed.
- **No improvising new fields.** Stick to the fields in `CLAUDE.md`. If the
  user asks for a field that doesn't exist in the schema, push back and ask
  whether the schema should change (that's a different conversation, not this
  skill's job).
