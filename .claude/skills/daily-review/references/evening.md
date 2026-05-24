# Evening workflow

The evening flow has three jobs:
1. Open today's daily note and surface what got done.
2. Capture the day's highlights.
3. Preview tomorrow's commitments.

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

## Step 3: Preview tomorrow

Compute tomorrow's ISO date. Query tasks due/scheduled tomorrow:

```
obsidian tasks todo verbose format=json
```

Filter to tasks with `📅 <tomorrow>` or `⏳ <tomorrow>`. Also check if
`daily/<tomorrow>.md` exists — if it does, the user has pre-planned
something there; mention that.

Surface as a tight one-liner: "Tomorrow: 3 tasks due (including
[representative]), no pre-planned daily note." Or "Tomorrow: nothing on
the books." Don't pad. The point is to seed mental prep for tomorrow,
not exhaustively brief the user.

If there's a calendar plugin or event source in the vault (likely
none, but check), include events/meetings. If not, only tasks.

## Step 4: Close

One short summary: "Day reviewed. <N> highlights captured. Tomorrow:
<short shape>."

Don't ask if there's anything else; the user can keep adding to the
daily note in Obsidian directly if they want. The skill's job is the
prompt-and-capture cycle, not babysitting.
