# Search strategies for open-page skill

When the user provides a page name or description, try these search strategies in order. Stop at first match.

## Strategy 1: Exact filename match (obsidian files)

```
obsidian files | grep -i "<name>"
```

Fastest path — checks every file in the vault including untracked ones. Works regardless of Git status.

## Strategy 2: Obsidian CLI search

```
obsidian search query="<keywords>" limit=5 format=json
```

Searches file contents, not just filenames. Use when the filename might differ from what the user described.

## Strategy 3: Folder-scope files listing

If you have a strong hunch about the folder (e.g., "recipes" → `wiki/recipes/`), list that folder directly:

```
obsidian files folder=<folder>
```

This is faster than a full vault search when you can narrow the scope.

## Strategy 4: obsidian file command by name

Try resolving the page name like a wikilink:

```
obsidian file file="<Name>"
```

If this returns info, the file exists and you have its path. Use it to open.

## Tie-breaking

- Prefer exact filename match (Strategy 1 or 4) over content search.
- If multiple results appear, present them to the user via AskUserQuestion with the full path as context.
- If no results from any strategy, report "not found" and suggest creating it.
