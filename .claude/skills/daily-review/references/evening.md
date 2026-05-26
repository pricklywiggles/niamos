# Evening workflow

The evening flow has four jobs:
1. Open today's daily note and surface what got done.
2. Write back habit completions to their habit pages.
3. Capture the day's highlights.
4. Preview tomorrow's commitments.

## Step 1: Open today, surface what got done

```
obsidian daily
```

Then query tasks completed today across the vault:

```
obsidian tasks done verbose format=json
```

This returns every completed task. The Tasks plugin marks completion
with `✅ YYYY-MM-DD`. Parse each task line for that emoji-date and
filter to today's date.

Surface the count and a couple representative lines: "You finished 6
tasks today, including: [task 1], [task 2]." Don't dump the full list —
the user already lived through the day; a snapshot is enough.

If zero tasks completed: say "no completed tasks logged today" without
judgment. Some days are like that, and the skill shouldn't moralize.

## Step 1.5: Habit write-back

Before prompting for highlights, conditionally handle unchecked habits
and write back completions.

First, check today's daily's `## Habits` section:
- If any `- [ ]` lines remain (uncompleted habit tasks), prompt the user
  via AskUserQuestion: "N habit tasks are still unchecked: <names>. Want
  to mark any complete?" with options: "All of them done", "None — leave
  unchecked", "Other" (free-form: "1, 3" to mark specific ones).
- For each task the user wants to mark done, Edit today's daily to flip
  `- [ ]` → `- [x]` and append ` ✅ <today>` to the line.
- If `## Habits` is missing entirely, or every line is already checked,
  skip the prompt.

Then run the habits script in evening mode:

```
.claude/skills/daily-review/scripts/habits.py evening <today>
```

It scans today's daily's `## Habits` section for `- [x]` lines, matches
each name (case-insensitive) against active-habit task lines, and
rewrites the matching `- last:` to today's date — atomically per habit
page. Returns JSON `{updated: [...], unchecked: [...]}`.

Surface the count briefly: "Wrote back N habit completions." If the
script reports collisions (same name across two habits), the audit skill
catches that — don't try to disambiguate at evening-review time.

## Step 2: Prompt for highlights

Read today's daily note's `## Highlights` section. If it already has
content beyond the template placeholder, skip the prompt (the user
already captured them).

If empty, ask via AskUserQuestion with a single free-form question:
"What's worth remembering from today?" — leave Other open so the user
can type a free-form answer. If they say "nothing" or skip, just move
on; some days don't warrant a highlight.

If they give content, append each highlight as a bullet to the
`## Highlights` section. Format: `- <highlight text>`. Use Edit to
insert after the heading.

## Step 3: Look ahead 7 days

The evening preview pulls calendar events and tasks for the next 7 days
(tomorrow through tomorrow + 6) and surfaces them in chat. **No file
edits** — this is a heads-up briefing, not something that gets
persisted. The user will run morning review tomorrow to materialize
tomorrow's slice into the daily note.

Calendar sources (same detection as morning Step 7 — use whichever
subset is available; skip silently if neither is):

- **mcp-ical** — call `mcp__mcp-ical__list_events` with
  `start_date=<tomorrow>T00:00:00` and `end_date=<tomorrow+6>T23:59:59`.
  Convert UTC times to the user's local timezone.
- **gws** — run `gws calendar +agenda --days 7 --format json` via Bash.

Also query tasks due in the window:

```
obsidian tasks todo verbose format=json
```

Filter to tasks with `📅` or `⏳` dates in `[tomorrow, tomorrow+6]`.

Display in chat, grouped by day, in date order. Each day gets a header
line; days with nothing show `— nothing scheduled` so gaps are visible
too:

```
Mon
  - All-day: Federal holiday
  - 10:00 AM: Team standup
  - 📅 Task: file taxes

Tue
  - All-day: Conference travel

Wed
  — nothing scheduled

...
```

Also check if `daily/<tomorrow>.md` or other future daily notes exist —
if any do, mention them at the end ("Pre-planned daily exists for Tue.")
so the user knows there's prior context they wrote earlier.

If neither calendar source is available, fall back to tasks-only —
still group by day, still surface empty days.

Keep it tight. The point is mental prep, not an exhaustive briefing —
trim event details (no meet links, no notes) and clip locations past
~40 chars.

## Step 4: Close

One short summary: "Day reviewed. <N> highlights captured. Tomorrow:
<short shape>."

Don't ask if there's anything else; the user can keep adding to the
daily note in Obsidian directly if they want. The skill's job is the
prompt-and-capture cycle, not babysitting.
