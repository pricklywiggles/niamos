---
type: wiki
---

# Wiki

A **Wiki** note is durable reference material — topical, freeform. The "Resources" half of original PARA. Examples: a guide to sourdough hydration, a list of useful CLI commands, a writeup of a specific home maintenance task. Anything you want to remember and refer back to that isn't tied to a specific [[Goal]]/[[Project]]/[[Habit]].

## Frontmatter schema

```yaml
---
type: wiki
---
```

Minimal. Wiki notes don't have status, dates, or declared relationships. The `type: wiki` field exists so the [[Skills|audit skill]] can classify the file and [[Bases and Dataview|Bases]] can query for "all wiki notes".

Filename: freeform Title Case, no Type prefix. See [[Naming and Wikilinks]].

## Body

Whatever the content needs to be. No required sections. The note is the content.

## Organization

Wiki notes live under `wiki/`, organized into topical subfolders. The [[Skills|place-wiki skill]] picks the right subfolder for each new note — it pushes back against dumping everything in `wiki/` root, since unbounded root growth makes the wiki unbrowsable. Heuristics live in `.claude/skills/place-wiki/references/placement-heuristics.md`.

The current subfolders grow organically as topical clusters emerge. Examples in this vault:
- `wiki/system/manual/` — these very docs (operating guide for the vault itself); `wiki/system/dashboards/` holds navigation pages
- `wiki/homelab/` — homelab/sysadmin reference (e.g., "How to install Proxmox on an SBC")

## Lifecycle

Wiki notes don't have one. They're durable. If a Wiki note becomes wrong, edit it. If it becomes obsolete, delete it (or leave it as a historical record). There's no "archived" state — that concept belongs to Goal/Project/Habit, not reference material.

## See also

- [[PARA Method]] — where Wiki fits
- [[Skills]] — `create-page` invokes `place-wiki` automatically for Wiki type
- [[Naming and Wikilinks]] — naming convention (freeform, no Type prefix)
