---
name: place-wiki
description: >-
  Decide where in `wiki/` to place a new or existing Wiki page, picking a
  topical subfolder rather than dumping it at the root. Use this skill
  whenever the user creates a Wiki note, asks where a topic should live, wants
  to relocate an existing Wiki page, or says anything like "place wiki",
  "organize wiki", "where should this wiki go", "move this wiki page", "find a
  home for X", "this should probably live somewhere else". Also invoked
  automatically by the `create-page` skill for Wiki type. Reads existing
  `wiki/` subfolders to ground placement, proposes 1-2 candidate homes, pushes
  back against kitchen-drawer root dumping, and executes the move/create via
  Obsidian CLI so the link index stays intact.
---

# Place a wiki page

The vault `CLAUDE.md` at the repo root describes the Wiki type and the
folder layout. This skill executes the *pick-a-home-for-a-Wiki-note*
workflow.

For the heuristics behind subfolder choice, read
`references/placement-heuristics.md` once at the start of a session that
will use this skill. Don't re-read it on every invocation.

## Workflow

### 1. Determine input mode

Two modes:

- **Existing file**: A path like `wiki/<filename>.md` or
  `wiki/<some-folder>/<filename>.md` was passed in. The file exists. The job
  is to (possibly) move it.
- **New topic**: A human topic string was passed in but no file exists yet.
  The job is to pick a subfolder, then create the file there.

If the input is ambiguous (e.g., the user said "place wiki for sourdough"
without saying whether a file exists), check whether
`wiki/Sourdough.md` or any `wiki/**/Sourdough.md` exists. If found, treat as
existing-file mode. If not, treat as new-topic mode.

### 2. Survey existing wiki structure

```
obsidian files folder=wiki
```

Group results into:
- **Subfolders** present under `wiki/` (e.g. `wiki/cooking/`,
  `wiki/programming/`).
- **Root-level files** directly in `wiki/`.

If `wiki/` is empty or has only the file you're placing, you're in
empty-state mode — see `references/placement-heuristics.md` § Empty state.

### 3. Propose candidate homes

Apply the heuristics in `references/placement-heuristics.md` to come up with
**1-2 candidate subfolders** that fit the topic. Prefer existing folders
when there's a real semantic fit. Only propose a new folder if no existing
folder genuinely matches — and when you do, sanity-check the proposed name
against existing siblings to avoid near-duplicates (e.g., don't propose
`recipes/` when `cooking/` already exists).

For each candidate, have a one-sentence rationale ready.

### 4. Present the choice

Use AskUserQuestion with up to four options:

1. Best-fit candidate (existing or new subfolder)
2. Alternate candidate, if a meaningful second exists
3. "Keep at `wiki/` root" — only include this option if the topic genuinely
   resists categorization (a true one-off, an index page, a stub). When
   included, the description should briefly say *why* you think root might be
   defensible. Otherwise omit this option entirely so the user has to engage
   with the choice.
4. "Other — I'll specify" (always include)

Each option's description must be one short sentence — the *rationale* for
that placement, not just the path.

### 5. Execute the placement

**Existing-file mode (move):**
```
obsidian move path="<current-path>" to="wiki/<chosen-subfolder>/"
```
`obsidian move` goes through Obsidian's API, so incoming wikilinks are
updated automatically. If the destination subfolder doesn't exist yet,
Obsidian creates it.

**New-topic mode (create):**
```
obsidian create path="wiki/<chosen-subfolder>/<Filename>.md" content="---\ntype: wiki\n---\n"
```
Filename is Title Case matching the human topic (e.g.,
`Sourdough Hydration.md`), no Type prefix (Wiki doesn't use one per
CLAUDE.md "Naming").

### 6. Open the file

```
obsidian open path="wiki/<chosen-subfolder>/<Filename>.md"
```

Return control with one short sentence stating the chosen home.

## Rules

- **Never silently dump to `wiki/` root.** Root placement is only valid when
  the user explicitly picks it after seeing the alternatives, or when the
  topic is a genuine one-off (e.g., a top-level index for the whole Wiki).
  Even then, surface the choice — don't take it without asking.
- **Prefer existing subfolders.** A new folder is justified only when no
  existing one fits. Otherwise, the Wiki fragments into single-occupant
  folders and loses navigability.
- **One folder = one topic cluster.** Don't propose splitting an existing
  folder mid-flight ("`cooking/` is getting too big, let's split into
  `cooking/baking/` and `cooking/grilling/`"). That's reorganization work
  and belongs in a separate user-initiated pass (a future `audit` skill
  task).
- **Use the Obsidian CLI for all file ops** — `obsidian move`, `obsidian
  create`, `obsidian open`. Raw filesystem moves bypass Obsidian's link
  updater and orphan incoming wikilinks. Verified: `rename` only renames
  in-folder, `move` is the right command for relocation across folders.
- **Stop on ambiguity.** If you can't confidently classify the topic from
  the user's input (e.g., "place wiki for engagement"), ask one
  AskUserQuestion to clarify the domain before proposing folders. Don't
  guess.
