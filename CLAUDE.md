# Niamos vault — operating guide

A personal Obsidian vault using a modified PARA method. The full system documentation lives in `wiki/system/manual/` (browsable in Obsidian, also loaded into Claude's context via the `@` includes below). Day-to-day navigation lives in `wiki/system/dashboards/` — start at `wiki/system/dashboards/Control Panel.md` (pinned in the sidebar). That file is gitignored (it's the owner's personal dashboard with private wikilinks); a `Control Panel (example).md` ships alongside as the template.

## System reference

Loaded into context (read these first):

@wiki/system/manual/PARA Method.md
@wiki/system/manual/Naming and Wikilinks.md
@wiki/system/manual/Bases and Dataview.md
@wiki/system/manual/Plugin Stack.md
@wiki/system/manual/Skills.md

## Content type schemas

@wiki/system/manual/Goal.md
@wiki/system/manual/Area.md
@wiki/system/manual/Project.md
@wiki/system/manual/Habit.md
@wiki/system/manual/Wiki.md
@wiki/system/manual/Daily.md
@wiki/system/manual/Archives.md

## Folder layout

```
goals/                       # type: goal pages (active)
areas/                       # type: area pages (no status)
projects/                    # type: project pages (active)
habits/                      # type: habit pages (active)
archives/<year>/<type>/      # archived goals/projects/habits, e.g. archives/2026/projects/
wiki/                        # durable reference, topical subfolders
                             # wiki/system/manual/ holds this guide; wiki/system/dashboards/ holds navigation pages
daily/                       # daily notes, flat, YYYY-MM-DD.md
templates/                   # one .md per content type
bases/                       # .base files + .md index pages with Tasks/Dataview queries
temp/                        # scratch and reference material — never a content target
```

## Tag vocabulary

Tags are used **on tasks**, not on pages. Membership for pages is the `type` property.

- `#work` — work-related tasks
- `#personal` — personal tasks
- Nest for specificity: `#work/cohort-feature`, `#personal/health`.

Tags expand by deliberate choice, not drift.

## Working in this vault — for Claude

These are Claude-specific operational rules that don't belong in the human-facing wiki:

- **Do not seed example content.** The owner is building this from scratch and does not want sample Goals/Projects/etc. created based on the Roam screenshots in `temp/`. Those are conceptual references only.
- **Prefer the Obsidian CLI over Write** when creating, opening, deleting, moving, renaming, or querying files. It uses Obsidian's own APIs and keeps state (Templater, indexes, FMT) consistent. Raw filesystem ops can desync the metadata cache.
- **One side of each relationship.** Add a wikilink only on the owning side per the schema in each content type's wiki page. Backlinks handle the reverse.
- **Wiki placement matters.** When placing a new Wiki page, use the `place-wiki` skill — find the right subfolder home, suggest organization, push back against root-dumping. Stay flexible — the Wiki holds genuinely unrelated topics; navigability matters more than a clean taxonomy.
- **Legacy inconsistency exists and is OK to normalize.** `wiki/system/manual/Roam Method Overview.md` notes uneven tag/keyword usage in the old Roam vault. Normalize as you go; don't preserve legacy spelling for its own sake.
- **Don't reload Obsidian.** Claude usually runs inside the Obsidian Terminal plugin — `obsidian reload` severs the session. If a plugin config change needs a reload to take effect, tell the user and let them restart manually.
- **Bootstrap Control Panel on fresh clones.** `wiki/system/dashboards/Control Panel.md` is gitignored. If it doesn't exist on disk, tell the user to copy `Control Panel (example).md` to `Control Panel.md` and personalize from there — don't write the file silently and don't edit the example as if it were the live dashboard.
