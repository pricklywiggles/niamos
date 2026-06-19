---
type: wiki
---

# Save to Niamos (global skill backup)

A reference copy of the global Claude Code skill `save-to-niamos`, which lets the user save arbitrary content (conversation snippets, architecture decisions, recipes, code snippets, anything) into this vault from any context — a coding project, a standalone chat, another vault, or from inside Niamos itself.

The live skill is **not** under version control because it lives in the user's home directory, outside this repo. This page is the backup so it can be restored on a fresh machine.

**Live location:** `~/.claude/skills/save-to-niamos/SKILL.md`

## How to restore on a fresh machine

```bash
mkdir -p ~/.claude/skills/save-to-niamos
```

Then write the content between the four-backtick fences below into `~/.claude/skills/save-to-niamos/SKILL.md`. Claude Code auto-discovers global skills at session start, so once the file is in place the skill becomes available in every project — no further setup needed.

## Relationship to vault-local skills

This is the *external* analog of the vault-local [[Skills|place-wiki]] skill:

- **`place-wiki`** (vault-local, lives in `.claude/skills/place-wiki/`) — picks the right `wiki/` subfolder during in-vault workflows; invoked by `create-page` when the user makes a Wiki note from inside the vault.
- **`save-to-niamos`** (global, lives in `~/.claude/skills/save-to-niamos/`) — the external entry point. Finds the vault, scans the taxonomy, proposes placement, writes the file — all without assuming the caller has any vault context.

## SKILL.md verbatim

````
---
name: save-to-niamos
description: >-
  Save arbitrary content — a conversation snippet, an architecture
  decision, a recipe, a code snippet, a useful artifact, context for
  future-you, anything — into the Niamos Obsidian vault. The skill's
  job is **placement and write**, not content authoring: it finds the
  vault, scans the existing `wiki/` taxonomy, proposes 1–3 candidate
  subfolders (or a new one when nothing fits), lets the user pick,
  gives gentle non-blocking feedback on form, and writes the file with
  `type: wiki` frontmatter. Use this skill whenever the user says any
  of: "save this to niamos / my vault / my wiki", "stash this in
  niamos", "add this to my notes", "I want to keep / remember this",
  "save this decision / snippet / convo / artifact", "put this in the
  wiki", or any variant that means "preserve this piece of content in
  my personal knowledge base". Works from anywhere — the user might
  invoke it from a coding project, a standalone chat, another vault,
  or from inside Niamos itself; the skill is self-contained and never
  assumes vault context.
---

# Save to Niamos

The Niamos vault is the user's personal Obsidian-based PARA knowledge
base. Reference material lives under `wiki/` in topical subfolders. The
taxonomy is meant to stay **tight but flexible** — bias toward existing
folders, propose new ones only when nothing fits, and use the
`wiki/uncategorized/` escape hatch for "I'll decide later".

This skill is the external entry point for landing content in the
vault. It is **not** responsible for the content itself (no rewriting,
no summarizing, no editing of substance) — only for *where it lands*
and *how it lands* (filename, frontmatter, light hygiene).

## Vault location

Default path (iCloud-synced Obsidian vault on the user's Mac):

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Niamos
```

Override with the `NIAMOS_VAULT_PATH` env var if the vault ever moves.

Resolve at the start of every invocation:

```bash
VAULT="${NIAMOS_VAULT_PATH:-~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Niamos}"
test -d "$VAULT/wiki" || { echo "Niamos vault not found at: $VAULT"; echo "Set NIAMOS_VAULT_PATH or move the vault back."; exit 1; }
```

If the resolved path has no `wiki/` subdirectory, fail loudly with the
message above — do **not** silently create it.

## Workflow

### 1. Resolve the vault

Run the resolution snippet above. Hold `$VAULT` as the absolute base
for the rest of the flow. Every Bash and Write call should use absolute
paths under `$VAULT/wiki/...` so the skill works regardless of the
caller's cwd.

### 2. Establish what's being saved

The content can arrive three ways:

- **Pasted in the user's message** — the most common case. Take it
  verbatim.
- **A file path** the user references (e.g. "save the ADR in
  `docs/2026-05-decision.md`"). Read that file.
- **Conversation context** — e.g. "save this conversation" referring
  to the chat itself. Grab the relevant slice. If unclear which slice,
  ask one focused question before proceeding.

Don't summarize, rewrite, or trim. The user's content is the user's
content.

### 3. Scan the existing wiki taxonomy

```bash
ls -d "$VAULT/wiki"/*/ 2>/dev/null | xargs -n1 basename
```

Hold this list. The skill biases hard toward placing content into one
of these existing folders. Note: `wiki/system/` is **reserved** for
vault meta-documentation (manual, dashboards) — never propose it for
user content.

### 4. Categorize and propose placement

Match the content's nature against existing folders. These mappings
are heuristics, not rules — read the actual current subfolder list each
time:

| Content kind | Likely fit |
|---|---|
| Recipe / food / cooking | `wiki/recipes/` |
| Homelab / self-hosted infra / sysadmin notes | `wiki/homelab/` |
| Code snippet, useful pattern, CLI invocation | `wiki/snippets/` |
| Architecture doc, ADR, design decision from a project | `wiki/projects/<project-name>/` |
| AI conversation / chat log worth preserving | `wiki/conversations/` |
| Reference doc on a specific topic | matching topical folder if one exists |
| Grocery / shopping reference | `wiki/groceries/` |
| Genuinely doesn't fit anywhere obvious | `wiki/uncategorized/` |

Present via `AskUserQuestion` with **at most 4 options**:

1. **Best existing match** (always first if there's a reasonable one)
2. **Second match** (if applicable, otherwise skip)
3. **Create new: `wiki/<suggested-name>/`** (only when no existing
   folder is a clean fit; the suggested name should be short, lowercase,
   hyphenated)
4. **`wiki/uncategorized/`** (always last, framed as "decide later")

If the user picks **Other**, accept any path **under `wiki/`**:
- Validate it starts with `wiki/`
- Reject `..` segments
- Reject absolute paths
- Reject `wiki/system/` (reserved)
- If the user wants a deeper nested path (e.g. `wiki/projects/sanum/architecture/`), allow it

### 5. Pick a filename

Niamos Wiki naming convention:
- Title Case, freeform
- **No** Type prefix (Goals/Projects/Habits use `Type - Name.md`, Wiki
  doesn't)
- Spaces, ampersands, apostrophes are fine — Obsidian handles them
- `.md` extension

Suggest a filename derived from the content:
- If the content has a top-level heading (`# Title`), use that
- Otherwise summarize the topic in 3–6 words

Surface the suggestion in the same step as placement OR as a quick
free-text question. Let the user override.

If a file at the target path already exists, **ask before
overwriting**. Don't silently clobber.

### 6. Gentle content feedback (non-blocking)

Before writing, scan once for issues that would frustrate future-self
when they revisit this page. Surface them as suggestions, **never as
gates**:

- **No title heading**: suggest adding `# <Title>` at the top
- **Bare snippet without context**: suggest a 1–2 sentence intro
  ("Captured from <source> while working on <X>; useful for <Y>")
- **Code without a language tag on fences**: suggest adding the
  language (` ```python ` etc.) so highlighting works
- **Mentioned name matches a known vault page**: suggest a `[[wikilink]]`
- **Massive wall of text with no headings**: suggest light section
  breaks

After surfacing, ask one concise question: "Proceed as-is, or want to
revise first?" Default to proceed. The cost of a slightly-imperfect
saved page is much lower than the cost of friction at save time — when
in doubt, just write it.

### 7. Assemble and write

Build the final file content:

```
---
type: wiki
---

<user's content, verbatim>
```

If the user's content already has YAML frontmatter, **preserve their
fields** and only add `type: wiki` if missing. Don't reorder or rewrite
their frontmatter.

Create the target subfolder if needed:

```bash
mkdir -p "$VAULT/wiki/<folder>"
```

Write the file. **Prefer the Obsidian CLI** (keeps the metadata cache
in sync — Bases / Dataview / Pretty Properties all read from it):

```bash
obsidian create vault=Niamos path="wiki/<folder>/<Filename>.md" content="..."
```

The `vault=Niamos` flag is important — it targets Niamos even when the
user has other Obsidian vaults open.

**Fall back to the Write tool** if:
- `obsidian` CLI isn't on PATH (test with `command -v obsidian`)
- The content has many backticks, backslashes, or other escape-prone
  characters that make the CLI's `\n`/`\t` parser awkward (e.g. code
  with PowerShell paths, regex, LaTeX)

The Write tool writes byte-exact and avoids escape ambiguity. Just
write to the absolute path: `$VAULT/wiki/<folder>/<Filename>.md`.

### 8. Close

One short confirmation line:

```
Saved → wiki/<folder>/<Filename>.md
```

Include the absolute path on a second line **if the user invoked this
from outside the vault**, so they can navigate to it if they want:

```
Saved → wiki/recipes/Pasta Carbonara.md
        ~/.../Niamos/wiki/recipes/Pasta Carbonara.md
```

Don't try to open Obsidian or surface the file in their current
environment — the user invoked this from elsewhere and probably wants
to stay where they are.

## Rules

- **Placement is the user's call, not yours.** Suggest, don't decide.
  The taxonomy belongs to the user and shapes over time.
- **Bias hard toward existing folders.** Each new top-level subfolder
  is a long-term commitment. Only propose one when nothing existing is
  a reasonable home.
- **`uncategorized/` is the escape hatch, never the default.** Always
  offer it last in the options list. It exists so the user can defer
  the classification decision; suggesting it first would invite the
  whole vault to drift there.
- **Don't propose `wiki/system/`.** That subfolder is reserved for
  Niamos's own operating manual and dashboards. User content never
  goes there.
- **Never modify content substance.** Frontmatter additions, code-fence
  language hints, and section-heading suggestions are OK; rewriting,
  summarizing, or "improving" the user's actual words is not.
- **Self-contained: assume zero vault context.** The caller (a coding
  agent in some other repo, a chat session, whatever) doesn't know
  where Niamos is or how it's organized. Resolve the path. Scan the
  structure. Make the user's choices clear. Don't make them re-explain.
- **No hard gates on form.** Feedback is a single non-blocking pass
  before the write. If the user says "just save it", write it.
- **Filenames don't carry dates.** Wiki pages are durable reference;
  the topic is the name, not the date. Git history captures *when*.
- **Path validation is strict.** Refuse `..` segments, absolute paths,
  anything outside `wiki/`, and `wiki/system/`. The skill writes only
  into user-content territory under `wiki/`.
- **Prefer Obsidian CLI when practical.** It keeps the metadata cache
  coherent (matters for Bases, Dataview, Pretty Properties, Icon
  Folder). Fall back to Write only when escape ambiguity makes the CLI
  awkward.
- **Never run `obsidian reload`** or any command that would restart
  Obsidian. The vault may be open in the user's Obsidian app with
  unsaved state in other tabs.

## Related skills (Niamos-internal)

When operating inside the Niamos vault, the user has these vault-local
skills that overlap conceptually but aren't reachable from outside:

- `place-wiki` — picks the right subfolder for a new Wiki page during
  in-vault workflows (called by `create-page` when the user makes a
  Wiki note from inside the vault). `save-to-niamos` is the *external*
  analog.
- `create-page` — scaffolds Goals / Areas / Projects / Habits / Wikis
  with frontmatter and templates.

If the user invokes `save-to-niamos` from inside the Niamos vault
itself (rare but possible), the skill still works — no special-casing
needed.
````
