---
name: open-page
description: >-
  Search for and open a page in Obsidian by name, description, or keywords.
  Triggers when the user says any of: "open <page>", "open the <name> page",
  "go to <topic>", "show me <something>", "pull up <name>", "find and open
  <X>", or any variant asking to locate and display a vault page. Uses the
  Obsidian CLI for all operations — never raw filesystem reads. Searches across
  the entire vault including untracked files (Git-ignored pages are still in
  Obsidian). If multiple candidates exist, present them as options. If none
  found, offer to create it.
---

# Open a page

Search for a file by name or description and open it in Obsidian using the
Obsidian CLI (`obsidian`). This skill handles untracked files, spaces in
names, special characters, and ambiguous results.

## Workflow

### 1. Extract search terms

From the user's request, pull out the page name or topic keywords. If the
user gave no specifics (e.g., "open a page"), ask what they want.

### 2. Search for the file

Apply strategies from `references/search-strategies.md` in order:

**A. Exact filename match:**
```
obsidian files | grep -i "<name>"
```
This is the fastest and most reliable — it lists every file the vault knows
about, including Git-ignored ones. The Obsidian CLI reads the filesystem
directly.

**B. Wikilink resolution (if A fails):**
```
obsidian file file="<Name>"
```
The `file=` parameter resolves like a wikilink — handles spaces and special
characters automatically if quoted properly.

**C. Content search (if A and B fail):**
```
obsidian search query="<keywords>" limit=10 format=json
```
Searches inside file contents. Use this when the filename might differ from
what the user described (e.g., "carbonara recipe" → `Pasta Carbonara.md`).

**D. Folder-scope check (if you have a strong hunch):**
```
obsidian files folder=<folder>
```
Only use when the user's description implies a domain — e.g., "recipes"
suggests `wiki/recipes/`, "books" suggests `wiki/books/`.

### 3. Handle results

**Single match:** Proceed to step 4.

**Multiple matches:** Present via AskUserQuestion with the full relative path
as each option's description. Include up to 5 candidates. Always include
"Other — not listed" as a fallback option.

**No matches:** Report that no file was found. Offer to create it via the
`create-page` skill if appropriate, or ask for different search terms.

### 4. Open the file

```
obsidian open path="<relative-path>"
```

Use `path=` (not `file=`) since you already know the exact relative path from
the search results. This avoids any wikilink-resolution ambiguity.

If the user wants it in a new tab, add `newtab`:
```
obsidian open path="<relative-path>" newtab
```

### 5. Report

Return one short sentence: "Opened `<display-name>`."
Do not include extra context unless asked.

## Rules

- **Always use the Obsidian CLI.** Never read files directly with `cat` or `Read` just to find them — that's what this skill is for. Reading the content after opening is fine.
- **Quote paths with spaces.** Pasta Carbonara → `path="wiki/recipes/Pasta Carbonara.md"`. The Obsidian CLI requires proper quoting for spaces and special characters.
- **Use relative paths** (vault-root-relative), never absolute filesystem paths, in CLI commands.
- **Never assume a file exists** — always search first. Even if you "know" the path from prior context, verify it still exists before opening.
- **One question at a time.** If you need clarification (which folder? which page?), ask one AskUserQuestion — don't chain multiple questions.
- **Don't open duplicate tabs.** Before opening, check `obsidian tabs` to see if the file is already open. If so, just report it's already open instead of creating a new tab.
