# Morning workflow

The morning flow has five jobs in order:
1. Open today's daily note and read what's already there.
2. Look back at the most recent prior daily note for undone work.
3. Carry that work forward to today **automatically — no prompt**.
4. Insert today's habit-driven tasks into `## Habits`.
5. If a calendar source is available, insert today's events into `## Schedule`.

## Step 1: Open today, read context

```
obsidian daily
```

This opens (and creates, if missing) today's `daily/YYYY-MM-DD.md`,
applying the Templater folder template. Then read the file to capture:
- Anything the user has already written in `## Notes` or `## Highlights`
  beyond the template placeholders.
- Any inline `- [ ]` tasks written directly into the body.

Don't act on what's already there — just hold it as context. The user may
have started their day already and you're joining mid-flow.

## Step 2: Find the most recent prior daily note

```
obsidian files folder=daily
```

Filter to ISO-date filenames (`YYYY-MM-DD.md`), strip the extension, sort
descending, pick the first one *before* today's date. That's the
"previous daily" — could be yesterday, could be Friday-before-a-Monday,
could be from a week ago if the user missed days.

If there's no prior daily (this is the first one in the vault), skip
step 3 entirely — there's nothing to carry forward.

## Step 3: Find what didn't get done

Two sources for "didn't get done":

**(A) Tasks across the vault that were due on or before the prior
daily's date and are still not done.** Run:

```
.claude/skills/daily-review/scripts/past_due.py <prior-daily-date>
```

Returns `{"tasks": [{"file": "...", "line": "N", "date": "YYYY-MM-DD", "text": "- [ ] ..."}]}`.
An empty list is the authoritative answer that nothing is past due.

**(B) Inline `- [ ]` checkboxes written directly in the prior daily's
body** (not Tasks-plugin queries, but actual checkbox lines in `## Todo`,
`## Notes`, or `## Highlights`). Read the prior daily file and grep for
`- [ ]` lines in the body. These are second-class — they don't have a due
date — so treat them as "stuff the user jotted down and never finished".

**Explicitly exclude the prior daily's `## Habits` section** from this
scan. Habit tasks have their own cadence-driven scheduling (see Step 5);
yesterday's unchecked habit task either fires again today on its own
cadence or it doesn't — carrying it forward as an inline checkbox would
double-insert.

## Step 4: Carry forward (automatic — no prompt)

If both lists are empty, skip silently. Otherwise just do it — don't
ask. The user wants frictionless mornings; the prompt was friction.
They can manually delete anything they don't want in today's `## Todo`
after the fact.

For (A) explicitly-dated tasks returned by `past_due.py`: Edit
`task.file` to replace the emoji-date in that line with today's date.
These are project/goal tasks elsewhere in the vault; rescheduling moves
them forward without duplication. (`past_due.py` already excludes
`daily/` files, so no risk of mutating yesterday's daily record.)

For (B) inline `- [ ]` checkboxes in the prior daily's body (excluding
`## Habits`): copy each verbatim into today's daily's `## Todo` section,
appending after any existing checkboxes. Yesterday's daily is left as
the historical record; today's gets a fresh copy.

If anything was carried, mention the counts in the close summary. Don't
list every item — the user can read their own Todo section.

## Step 5: Insert today's habit-driven tasks

Run the habits script in morning mode:

```
.claude/skills/daily-review/scripts/habits.py morning <today>
```

It walks every active habit page, parses each `- [ ]` line in `## Tasks`
as `<name> - <cadence>[ - last: <date>]`, and emits a JSON list of tasks
whose cadence fires today (interval cadences fire when `(today - last)
>= N` or `last:` is empty; weekday cadences fire when today's weekday
matches).

Insert each fired task into today's daily under `## Habits` as a plain
`- [ ] <name>` line. Use Edit, appending after the `## Habits` heading
in the order the script returned them. Before inserting, dedup against
any `- [ ]` or `- [x]` line already in today's `## Habits` (case-
insensitive name match) — this makes re-running morning review
idempotent.

If today's daily was created before the template update and lacks a
`## Habits` section, insert one (between `## Todo` and `## Notes`) before
adding the fired tasks. Don't reload the file or restart Obsidian —
plain Edit suffices.

If the script returns an empty list, do nothing. Don't print "no habits
today" — the empty `## Habits` section speaks for itself.

## Step 5.5: Auto-check "Morning review"

The act of running this skill *is* the morning review. After habit
insertion, flip `- [ ] Morning review` in today's `## Habits` section to
`- [x] Morning review ✅ <today>` via Edit. Skip silently if the line
isn't there (habit doesn't exist, or already checked) — don't error.

Evening's habit write-back script will pick this up tomorrow morning when
it scans for `- [x]` lines in the prior daily — no separate write-back
needed here. The habit page's `- last:` updates on the next evening
review.

## Step 6: Insert today's calendar events

Calendar data comes from two optional sources. Detect what's available
*in this session* and use whichever subset responds:

- **mcp-ical** (macOS Calendar via EventKit) — check if the
  `mcp__mcp-ical__list_events` tool is in the loaded tool list. If
  present, call it with `start_date=<today>T00:00:00` and
  `end_date=<today>T23:59:59`. Event times come back in UTC; convert to
  the user's local timezone.
- **gws** (Google Workspace CLI) — try `gws calendar +agenda --today
  --format json` via Bash. If the binary is missing or auth fails, treat
  as unavailable; don't surface the error.

If neither source returns events (or neither is available), skip this
step entirely — don't create an empty `## Schedule` section.

Otherwise, build a markdown table and insert it at the top of the daily
note, immediately after the frontmatter and before `## Todo`:

```
## Schedule

| Time | Event |
|---|---|
| All-day | Federal holiday |
| 10:00 AM | Team standup |
| 6:30 PM | Dinner — Riverside Bistro |
```

Formatting rules:
- Sort rows by start time, all-day events first.
- Time column: `All-day` for all-day events; `H:MM AM/PM` otherwise (no
  leading zero on the hour; local timezone).
- Event column: the event title. If the event has a location, append
  ` — <location>` after the title; truncate location to ~40 chars if
  longer. Don't include notes, attendees, or meet links — the daily
  shows what's happening, not the full event payload.
- If both sources return overlapping events (same time, similar title),
  list them once — but don't fight to dedup perfectly; near-duplicates
  are a sign that two accounts have the same event and that's fine.

Idempotency: if `## Schedule` already exists in today's daily, Edit
**replaces** the entire section (heading + table + trailing blank line)
rather than appending a second one. Re-running morning review should
refresh the calendar, not stack new tables.

## Step 7: Force-refresh Dataview views

After all writes are done (carryover, habits, calendar), refresh every
markdown leaf that has Dataview content (block queries or inline DQL):

```bash
obsidian dev:cdp method=Runtime.evaluate params='{"expression": "(() => { const leaves = app.workspace.getLeavesOfType(\"markdown\").filter(l => l.view && l.view.contentEl && l.view.contentEl.querySelector(\".block-language-dataview, span.dataview\")); const prev = app.workspace.activeLeaf; leaves.forEach(leaf => { app.workspace.setActiveLeaf(leaf, {focus: false}); app.commands.executeCommandById(\"dataview:dataview-rebuild-current-view\"); }); if (prev) app.workspace.setActiveLeaf(prev, {focus: false}); return \"rebuilt \" + leaves.length + \" leaves\"; })()", "returnByValue": true}'
```

Why this and not the simpler `dataview:dataview-force-refresh-views`
command: that command doesn't refresh leaves pinned in the sidebar
(empirically verified — the Control Panel stayed on yesterday's date
across morning runs). The targeted approach works around this by
iterating every markdown leaf that contains Dataview content, briefly
making each one the "active" leaf without taking focus, then running
`dataview:dataview-rebuild-current-view` against it. The previous
active leaf is restored at the end, so the user's focus is undisturbed.

Dataview caches rendered output per-leaf and doesn't auto-flush when
`date(today)` rolls over at midnight, because no underlying *file*
changed — Dataview's invalidation is metadata-driven, not clock-driven.
Without this step, the Control Panel's `### Today` block and the
daily's own `## Today` / `## Tasks` blocks can keep showing yesterday's
results even though today's daily exists.

If the iteration ever proves too slow on a large vault, fall back to
`dataview:dataview-drop-cache` (heavier — drops the whole index, slower
re-render on next view, but reliable).

## Step 8: Close

One short summary line: "Carried forward 3 tasks, 1 inline note.
4 habits queued, 2 events on the calendar. `<today>` is open." Or, if
nothing: "Nothing to carry. `<today>` is open."

Don't list everything you did. The summary's job is "yes, I did the
thing", not "here's a detailed receipt".
