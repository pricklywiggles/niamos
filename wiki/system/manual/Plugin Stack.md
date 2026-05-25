---
type: wiki
---

# Plugin Stack

The vault deliberately uses a small set of plugins. Every addition is a future migration cost — adding plugins is easy, removing them is hard once content depends on their syntax.

## Core (built into Obsidian)

### Bases (core 1.9+)
Vault-wide YAML queries rendered as interactive tables. Used in `bases/*.base` files. See [[Bases and Dataview]].

### Daily Notes (core)
Configured: `folder=daily`, `format=YYYY-MM-DD`, `template=""` (intentionally blank — Templater owns templating via folder-template triggers). The `obsidian daily` CLI command (and the in-app hotkey) creates today's daily.

### Obsidian CLI (built-in v1.12.4+, GA Feb 2026)
The `obsidian` command on the shell. Primary automation surface for the [[Skills|skills]] in this vault. Commands used heavily: `daily`, `open`, `move`, `rename`, `create`, `delete`, `property:set`, `property:read`, `properties`, `tasks`, `task`, `files`, `templater:create-from-template`, `reload`.

Quirk worth knowing: `obsidian move` returns exit code 0 even when the rename fails with ENOENT (e.g., destination folder doesn't exist). Scripts must pre-create destination folders and verify the file actually moved post-call.

## Community plugins

### Tasks
Checkbox tasks with due/scheduled/recurring syntax. Settings: `useFilenameAsScheduledDate: true`, scoped to `daily/` (so tasks in daily notes inherit their date implicitly). See [[Bases and Dataview]] for the date emoji syntax.

### Dataview
Used narrowly: the page-local "what links to me" slices baked into [[Goal]] and [[Area]] templates, and the date-matching `## Today` block in [[Daily]]. Not used for primary indexing (that's Bases). Datacore is a future migration target — don't paint into a corner.

### Templater
Applies templates on file creation via folder-template triggers. Configured in `.obsidian/plugins/templater-obsidian/data.json` with `trigger_on_file_creation: true`. Folder→template mappings: `goals/` → `templates/goal.md`, etc. The [[Skills|create-page skill]] uses `obsidian templater:create-from-template` to apply templates explicitly.

### Icon Folder
Folder-icon customization. Cosmetic only.

### Excalidraw
Optional. Drawing tool. Doesn't interact with the PARA structure.

### Terminal
Embedded terminal. Convenience for running `obsidian` CLI inside Obsidian itself. **Note**: Claude usually runs inside this terminal — restarting Obsidian severs the session.

### Calendar
Sidebar calendar view of daily notes. Cosmetic navigation aid; clicking a date opens (or creates) that day's daily.

### Pretty Properties
Renders frontmatter as styled property pills, plus banner/icon/cover frontmatter handling. Banner images come from `wiki/assets/banners/`, icons from `wiki/assets/icons/` (configured in `data.json`).

### Markdown Table Checkboxes
Renders `- [ ]` syntax inside markdown tables as interactive checkboxes. Used in habit task tables and ad-hoc inline checklists.

### Hot Reload (dev-only, optional)
Auto-reloads in-development plugins on file change. Not needed unless you're writing Obsidian plugins. Gitignored — install via [BRAT](https://github.com/TfTHacker/obsidian42-brat) from `https://github.com/pjeby/hot-reload` if you want it.

## What's intentionally NOT installed

- **Front Matter Title (FMT)** — was installed briefly while we used an alias-based naming convention. Removed once we adopted "filename IS the display name" ([[Naming and Wikilinks]]). FMT's `alias.strategy: "ensure"` mode was *injecting* synthetic aliases into Obsidian's metadata cache for files that didn't have one, polluting Bases queries and template files. Don't reinstall unless the naming convention changes.
- **Datacore** — heir-apparent to Dataview. Watch for stable release. Migration target only.
- **Kanban** — not needed; Bases + Tasks cover what it'd do for this workflow.
- **Sync plugins** — using iCloud Drive for sync (vault path is under `iCloud~md~obsidian/`).

## Config locations

| Plugin | Config path |
|---|---|
| Templater | `.obsidian/plugins/templater-obsidian/data.json` |
| Tasks | `.obsidian/plugins/obsidian-tasks-plugin/data.json` |
| Pretty Properties | `.obsidian/plugins/pretty-properties/data.json` |
| Icon Folder | `.obsidian/plugins/obsidian-icon-folder/data.json` |
| Daily Notes (core) | `.obsidian/daily-notes.json` |

Plugin code (`main.js`, `styles.css`) is gitignored — only `data.json` and `manifest.json` are tracked, so configs survive a fresh clone but the user must install each plugin from the community store. See the README's setup section for the install list.

## See also

- [[Bases and Dataview]] — how Bases, Dataview, and Tasks queries work
- [[Skills]] — the skills layer on top of the CLI
- [[Naming and Wikilinks]] — why FMT isn't needed (and why having it active was harmful)
