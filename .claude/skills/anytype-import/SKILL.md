---
name: anytype-import
description: >-
  Import a page from the user's self-hosted Anytype into this Niamos Obsidian
  vault, page-by-page, recursing into children only when the user explicitly
  says so. Fetches over the local REST API at :31009, cleans the markdown,
  carries icons (emoji or file) onto the vault page, maps tag-based grouping
  onto folder placement, and flags the API's known cover gap so banners can be
  handled out-of-band. Use this skill whenever the user says any of: "import
  from anytype", "import the <name> page", "transfer the <name> page",
  "migrate <name> from anytype", "pull <name> over from anytype", "anytype:
  <something>", "bring this anytype page in", or any variant of "move this
  Anytype thing into the vault". Defaults to Wiki type and never imports
  silently — every page write and every child recursion is explicitly
  confirmed. Talks to the official `mcp__anytype__*` MCP for navigation and
  to the bundled `scripts/anytype.py` for deterministic extraction.
---

# Import a page from Anytype

The user is gradually migrating their self-hosted Anytype content into this
vault. They have explicitly rejected bulk export — every page comes over with
deliberate framing, with the chance to inspect children before recursing.
This skill is the per-page workflow that backs that.

The vault's content-type schemas live in [[../../wiki/system/manual/Wiki|Wiki]]
and the rest of `wiki/system/manual/`; the naming and folder conventions live
in [[../../wiki/system/manual/Naming and Wikilinks|Naming and Wikilinks]]; the
operating rules live in [[../../CLAUDE.md|the vault operating guide]]. Don't
duplicate those here — link to them.

## How the work is split

| Layer | What it owns |
|---|---|
| `scripts/anytype.py` | All Anytype API IO: fetch a page's cleaned markdown, download icon files, enumerate outgoing references (`children`), build the full transitive reachability plan for a recursive import (`plan`), search by name, slug names into vault-safe filenames. Deterministic, JSON output, clean error messages. Never writes vault files. |
| The MCP (`mcp__anytype__*`) | Optional live navigation when you need to disambiguate (e.g. multiple spaces have a page with the same name). The script's `search` subcommand covers the common case; reach for the MCP when you need richer filtering. |
| This skill (in conversation) | Resolving what the user meant, deciding target folder, assembling frontmatter, writing the vault file via Obsidian CLI, asking before recursing into children. |

## Workflow

### 1. Resolve the page

Take what the user gave you and turn it into `(space_id, object_id)`.

- **Page name** ("import the Pasta Carbonara page") → run `search`:
  ```
  .claude/skills/anytype-import/scripts/anytype.py search "<name>"
  ```
  Parse the JSON. One hit → use it. Multiple hits → ask via AskUserQuestion
  (show name, space_id prefix, snippet) for which one. Zero hits → tell the
  user and stop; don't guess.
- **Anytype deeplink** (`anytype://object?objectId=...&spaceId=...`) → parse
  out the IDs.
- **Bare IDs** → trust them, proceed.

### 2. Fetch and summarize

```
.claude/skills/anytype-import/scripts/anytype.py fetch <space_id> <object_id>
```

The JSON has everything you need for one page. Show the user a brief summary
in conversation (not the full body):

- Title
- Icon (emoji / file URL / none)
- Type and layout (page / collection / set)
- Body length
- Any tags it carries in Anytype
- Number of children enumerated (run `children` to count — don't list them yet)

### 3. Flag the cover gap

The Anytype REST API does **not** expose page covers — see
[[../../memory/project_anytype_migration|the project memory]] for why. The
script can't fetch them.

Ask the user once per page: "Does this page have a cover banner you want to
keep?" If yes, instruct them to save the image from Anytype desktop into
`wiki/assets/banners/` and tell you the filename — you'll add the frontmatter
in step 5. If no or they don't care, skip.

Never silently skip a cover. The point of asking is to surface the limitation
so we don't lose content quietly.

### 4. Decide target type and folder

For each page:

- **Default type: Wiki.** Most Anytype pages map cleanly to vault Wikis. The
  script doesn't carry Anytype tags onto the page (per
  [[../../CLAUDE.md|vault rules]] — tags are task-only) — instead the tag
  drives folder placement.
- **Folder by tag** (current convention; expand as the user adds more):
  - `recipes` tag → `wiki/recipes/` (illustrative — substitute the user's actual tag→folder mappings as they accumulate)
  - No tag, or unfamiliar tag → invoke the [[../../wiki/system/manual/Skills|place-wiki]] skill (or ask the user) to pick a subfolder under `wiki/`. Don't dump into `wiki/` root.
- **Goal/Project/Habit/Area imports** — the schemas need declared relationships
  (areas, goals, dates) that don't translate from Anytype's free-form pages.
  Punt: tell the user "I'll handle Wiki imports directly. For a
  Goal/Project/Habit/Area import, run `/create-page` first to scaffold the
  frontmatter, then I'll paste the body content into the right section." Don't
  try to invent the relationships.

Generate the filename:
```
.claude/skills/anytype-import/scripts/anytype.py slug "<page title>"
```
Use that + `.md` as the leaf. For Wiki this is freeform Title Case, no Type
prefix.

### 5. Handle the icon

If the fetch JSON shows an icon:

- **Emoji** (`format: emoji`) → take the emoji value directly. No file
  download.
- **File** (`format: file`) → download to `wiki/assets/icons/`:
  ```
  .claude/skills/anytype-import/scripts/anytype.py download-icon \
    <space_id> <object_id> --to wiki/assets/icons/
  ```
  The script prints the saved filename on stdout. Use the page-title slug as
  the basename so the file is identifiable in the vault.
- **None** → omit the `icon:` frontmatter line entirely.

### 6. Assemble and write the file

Build the frontmatter in this order (omit any line whose value is empty):

```yaml
---
type: wiki
icon: <emoji or filename>
banner: <filename if user supplied one in step 3>
---
```

Then a blank line, then the cleaned body markdown from `fetch`.

Pre-flight: if the target file already exists, **ask the user before
overwriting**. Don't silently clobber. If they say no, stop and report what
would have happened.

Write via Obsidian CLI to keep the metadata cache in sync:
```
obsidian create path="<target>" content="..."
```

`obsidian create` interprets `\n` and `\t` in the content arg. If the body
has many backticks, backslashes, or other escape-prone characters (e.g.
Windows paths like `"C:\Program Files\App\config.json"` or LaTeX with
`\frac{a}{b}`), fall back to the Write tool — content there is byte-exact
and avoids escape ambiguity.

### 7. Recurse — two modes

After writing the current page, surface its children. *How* you surface them
depends on what the user asked for at invocation:

**Mode A — per-page (default).** Use this when the user said "import the X
page" without mentioning children, or said "and also bring its sub-pages"
without specifying scope. Run:

```
.claude/skills/anytype-import/scripts/anytype.py children <space_id> <object_id>
```

Show the list in conversation. Ask **per-page** via AskUserQuestion whether
to import each one. When accepted, repeat from step 2 for that child.

**Mode B — plan-then-execute (recursive).** Use this when the user said
anything like "import recursively", "the whole subtree", "everything under
this", "all of them", "import the entire collection", or pointed you at a
collection/set with the obvious intent of pulling its members. Don't descend
page-by-page asking each time — that's prompt fatigue without insight.

Instead, build the full plan first:

```
.claude/skills/anytype-import/scripts/anytype.py plan <space_id> <object_id> \
    [--max-depth N] [--include-sources collection,property]
```

The script walks breadth-first, dedupes by ID, caps at 500 pages, and
returns JSON with every reachable page (depth, name, type, tag_keys). It
follows `collection`/`set` membership by default; pass
`--include-sources collection,property` to also follow object-valued
relations.

Then in one message, show the user the full plan:

```
Recursive import plan from "Recipe Collection" (13 pages):

  Root: Recipe Collection (set, tags: recipes)
  ├─ Pasta Carbonara               (page, → wiki/recipes/)
  ├─ Sourdough Bread               (page, → wiki/recipes/) ⚠ exists
  ├─ Caesar Salad                  (page, → wiki/recipes/) ⚠ exists
  ├─ Beef Stew                     (page, → wiki/recipes/)
  └─ ... (8 more)

Each will be imported as a Wiki note. Covers can't be detected via API —
I'll list any pages that look like they might have one so you can supply
the image after.
```

Things to call out in the plan message:
- **Target folder per page** (driven by tag, same logic as step 4)
- **Existing-file conflicts** — for each page, check whether the target file
  already exists in the vault, and mark `⚠ exists` so the user can decide
  upfront whether to overwrite or skip
- **Excluded pages** — anything that doesn't map cleanly to a Wiki (e.g.
  a Goal/Project/Habit/Area type) should be excluded with a note: "Skipping
  3 pages of type goal/project — those need `/create-page` scaffolding"
- **Plan caps** — if `capped: true` came back from the script, tell the
  user they're at the 500-page ceiling and ask whether to raise it or narrow
  the scope

Then ask **one** AskUserQuestion: proceed with all, pick a subset, or
cancel. Subset selection: if the list is ≤4 pages use multiSelect; if
larger, ask the user to list the pages to *exclude* in free text and parse
that.

After confirmation, execute the plan in BFS order. During execution, don't
re-prompt per page — the user already approved the scope. Do show progress
("3/13: imported `Margherita Pizza` → `wiki/recipes/Margherita Pizza.md`")
and surface any per-page failures without aborting the whole batch.

Banner handling in recursive mode: skipping the per-page cover prompt
would lose covers silently. Instead, at the end of execution, print a
"covers to supply manually" list so the user can drop those images into
`wiki/assets/banners/` and run `obsidian property:set name=banner ...`
themselves — or ask you to do that as a follow-up pass.

### 8. Close

One short summary: "Imported `<title>` → `<vault-path>`. Children offered: N.
Imported additional: M."

## Rules

- **The user always sees the full scope before any writes.** In Mode A this
  is implicit (one page at a time, one confirm at a time). In Mode B the
  plan output IS the consent surface — show every page that would land,
  flag existing-file conflicts, then get one yes. Never auto-recurse.
  Never write a page the user hasn't seen named in the plan.
- **Default to Wiki type.** Anytype pages don't carry the declared
  relationships needed for Goal/Project/Habit/Area frontmatter. For those
  types, defer to `/create-page` and only paste the body in after.
- **Don't carry Anytype page-tags into page frontmatter.** The vault rule
  in [[../../CLAUDE.md|CLAUDE.md]] is that tags are task-only. The Anytype
  tag drives the *folder placement* (e.g. `recipes` → `wiki/recipes/`) and
  then is dropped.
- **Surface the cover gap, don't hide it.** The API can't fetch covers —
  ask the user to drop the image into `wiki/assets/banners/` themselves
  and pass the filename in. Never just skip the cover silently.
- **Obsidian CLI for file ops where practical.** It keeps the metadata
  cache in sync (matters for plugins like Pretty Properties and Bases).
  Fall back to Write only when content makes the CLI's `\n`/`\t` escape
  parser awkward (heavy backticks/backslashes).
- **Never run `obsidian reload`.** Standing vault rule — see
  [[../../CLAUDE.md|CLAUDE.md]] and the user's memory.
- **Markdown body is preserved verbatim.** The script strips trailing
  whitespace per line (Anytype emits `   \n` everywhere) and collapses
  3+ blank lines down to 2. It does **not** taste-edit: no capitalization
  fixes, no section restructuring, no code-fence language tags unless the
  source already had them.

## Reference

- **Anytype API cover gap** — `cover_id` is an internal relation in
  `anytype-heart` but not exposed via REST. Tracked upstream as
  [`anyproto/anytype-api#16`](https://github.com/anyproto/anytype-api/issues/16). Until that
  lands, covers are user-supplied.
- **Gateway URL pattern** — file icons live at
  `http://127.0.0.1:47800/image/<hash>`. The script downloads from there and
  refuses to follow any URL that isn't loopback HTTP.
- **Emoji surrogate decoding** — Anytype's JSON returns emojis as UTF-16
  surrogate pairs (e.g. `🪟` for 🪟). Python's `json.loads`
  handles this natively; the script preserves the decoded character.
- **Collection / set membership** — requires two API calls: list the views
  for the list, then enumerate objects per view. The script's `children`
  subcommand does both transparently.
- **Auth** — relies on `ANYTYPE_API_KEY` in the shell env (sourced from
  macOS Keychain via `~/.zshenv`). If you're hitting 401s, the shell that
  started Claude Code predates the keychain export; restart Claude from a
  fresh terminal.
