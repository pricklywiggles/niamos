# Wiki placement heuristics

Guidance for the `place-wiki` skill on choosing or creating a subfolder
under `wiki/`. The owner's stated principle (CLAUDE.md): *"navigability
matters more than a clean taxonomy."* Subfolders exist so they don't have
to scroll through a flat list of dozens of Wiki notes. They are not a
formal ontology.

## The kitchen-drawer rule

Root-level dumping is the failure mode to resist. Once `wiki/` accumulates
20+ loose files at the root, finding anything by browsing the file tree
becomes painful — the whole point of subfolders is lost. Every Wiki note
should sit in a subfolder by default. The exceptions are narrow (see
*Defensible root placement* below).

## Prefer existing folders

A new subfolder is only justified when **no existing folder genuinely
matches**. "Genuine match" means the topic shares a meaningful organizing
dimension with the folder's other contents — domain, activity, tool, life
area — not just an incidental keyword.

Examples:
- New topic "Sourdough Hydration", existing `cooking/` containing
  `Knife Skills.md`, `Pasta Dough Basics.md` → fits. Propose `cooking/`.
- New topic "Vim Macros", existing `programming/` containing
  `Git Rebase Notes.md`, `Rust Lifetimes.md` → fits. Propose `programming/`.
- New topic "Tax Filing Checklist", existing `cooking/` and `programming/`
  → no fit. Propose a new folder like `finance/` or `admin/`.

## Avoiding near-duplicate folders

Before proposing a new folder, scan existing folder names for near-synonyms
or overlapping scopes. Common collisions:

- `cooking/` vs `recipes/` vs `food/`
- `programming/` vs `code/` vs `dev/`
- `finance/` vs `money/` vs `taxes/`
- `health/` vs `fitness/` vs `wellness/`
- `notes/` (a meaningless catch-all — never propose this; it's a kitchen
  drawer disguised as a folder)

When you detect a near-duplicate, **don't create the new folder**. Either:
1. Propose the existing-but-slightly-off folder with a rationale ("This is
   the closest existing home; `cooking/` already contains food topics
   broadly").
2. Or ask the user to pick whether to merge into the existing folder or
   genuinely split.

## When a new folder *is* justified

- The topic clearly belongs to a distinct domain not yet represented (the
  first note about home maintenance when the Wiki has only programming and
  cooking folders).
- The topic would be the second or third member of an obvious cluster
  currently scattered in the root (two root-level files about gardening
  warrant a `gardening/` folder; one doesn't yet).
- The user explicitly says "make a new folder for X".

Pick the folder name based on the **broadest plausible domain** the topic
sits in, not the most specific. `programming/` is better than `python/`
because the next note might be about Rust. Specificity can be added later
via deeper subfolders if a cluster genuinely accumulates.

## Subfolder depth

Default to flat — `wiki/<topic>/` only. Two-level nesting
(`wiki/programming/python/`) is a sign the first level grew large enough to
warrant a split, which is a deliberate reorganization decision, not
something to introduce on first placement of a single note. If asked to
place a note inside an existing deep subfolder that already has siblings,
that's fine; just don't *create* a second level on first placement.

## Empty state

If `wiki/` has no subfolders yet (first or second Wiki note in the vault):

- Default behavior: place the first 2-3 Wiki notes at `wiki/` root and
  revisit when a cluster emerges. One isolated note doesn't usually justify
  a folder.
- **Cluster-signal override**: if the topic itself strongly signals an
  obvious domain that's almost certain to attract siblings (e.g. a
  homelab/sysadmin note like "How to install Proxmox on an SBC", or a
  cooking technique when the user has mentioned other recipes they want to
  capture), it's fine to proactively propose a broad subfolder anyway.
  Present both the subfolder and the root option in AskUserQuestion and let
  the user pick. Don't auto-pick the folder; surface the judgment.
- Once a 2-or-3-note cluster is visible at root, propose pulling them into
  a subfolder together.

Root placement during empty state is defensible; root placement once
clusters exist needs the explicit justification described below.

## Defensible root placement (post-empty-state)

After the empty-state window closes, root placement is only defensible for:

- **Genuine one-offs** — topics that share no organizing dimension with any
  existing cluster and aren't likely to spawn siblings (e.g., a single
  short reference about a specific apartment's wifi password — even then,
  ask the user).
- **Top-level index pages** — a `wiki/README.md` or `wiki/Index.md` meant
  to orient navigation across the whole Wiki.

In both cases, surface the root choice as an explicit option in
AskUserQuestion with the rationale; never default to root silently.

## What this skill is not for

- **Bulk reorganization.** Moving multiple files at once, splitting a folder,
  merging folders — that's an audit/reorg task, not a placement task.
  Decline politely and suggest the user invoke the `audit` skill (when it
  exists) or do it manually.
- **Naming the file.** That's `create-page`'s job. By the time
  `place-wiki` runs, the filename is already decided.
- **Editing the file's content.** Placement only affects path, not body.
