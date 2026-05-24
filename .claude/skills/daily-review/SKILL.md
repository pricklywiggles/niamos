---
name: daily-review
description: >-
  Run the morning planning or evening review flow against today's daily note
  in this Obsidian vault. **Morning** opens the daily, reads what's already
  there, finds the most recent prior daily note, surfaces tasks that didn't
  get done (overdue + inline incomplete from the prior daily), and offers
  to carry them forward. **Evening** opens the daily, surfaces what got
  done today, prompts for the day's highlights and appends them to
  `## Highlights`, and previews tomorrow's commitments (tasks/meetings/
  events due tomorrow). Use this skill whenever the user says: "morning
  review", "morning planning", "let's plan today", "what's on today", "start
  my day", "daily plan" → morning; "evening review", "wrap up the day",
  "end of day", "daily review", "what got done today", "what's tomorrow"
  → evening; or the ambiguous "daily review" / "daily" → ask which.
  Accepts an explicit date argument (`for 2026-05-21`, `yesterday`, etc.)
  to operate on a non-today daily; defaults to today otherwise. The skill's
  whole reason for existing is that the owner's "Establish Daily
  Productivity Routines" goal lives or dies on whether this is frictionless
  enough to do every day — keep the flow tight, don't over-prompt, surface
  signal not noise.
---

# Daily review

This skill drives the daily-note workflow. Today's daily note (and the
previous one) carry most of the state; the skill's job is to read them,
surface what needs attention, and capture the human-only inputs
(highlights, "yes carry this forward", etc.).

For the detailed flow of each mode, read the appropriate reference file
once at the start of the session:
- Morning: `references/morning.md`
- Evening: `references/evening.md`

Don't re-read on every invocation within a single session.

## Workflow

### 1. Determine mode

Read the user's intent:
- "morning", "plan", "start my day", "what's on today" → **morning**
- "evening", "wrap up", "review", "what got done", "tomorrow" → **evening**
- "daily review" / "daily" alone is ambiguous → ask via AskUserQuestion

### 2. Determine target date

Default: today (ISO `YYYY-MM-DD`).

If the user mentions a specific date or relative date ("yesterday",
"Monday", "last Friday", "2026-05-21"), resolve it to an ISO date.

The target date drives which daily note to open:
- Today: `obsidian daily` (this creates the file if missing, applying the
  Templater folder template).
- Any other date: `obsidian open path="daily/YYYY-MM-DD.md"`. If the file
  doesn't exist, ask whether to create one — for past dates this is rare
  (usually you're reviewing an existing note); for future dates it's a
  pre-planning move worth confirming.

### 3. Run the mode-specific workflow

Read the appropriate reference file:
- `references/morning.md` for morning mode
- `references/evening.md` for evening mode

These reference docs spell out the specific steps for each mode (what to
query, what to surface, what to prompt for, how to write back to the
note). Follow them.

### 4. Close out

The mode-specific flow ends with a single short summary line ("Carried
forward 3 tasks. 5 due today.") and leaves the daily note open in
Obsidian for the user to continue with.

## Rules

- **Frictionless every day is the goal.** This skill's existence is
  justified only if the user keeps doing it. Over-prompting kills the
  habit. Default to silent progress: ask only for the human-only inputs
  (highlights, carryover yes/no), surface everything else briefly without
  awaiting confirmation.
- **The daily note is the source of truth.** Don't reach for separate
  scratch files, conversation memory, or external tools to track what got
  said. If something matters, it goes in the daily note (Highlights,
  Notes, or as a Tasks-syntax checkbox). If it doesn't end up in the note,
  it doesn't exist.
- **Use the Obsidian CLI for queries.** `obsidian tasks todo verbose
  format=json` is the right tool for finding undone tasks across the
  vault. Don't shell out to `grep` for task discovery — the CLI parses
  Tasks plugin syntax properly and stays in sync with the metadata cache.
- **Carrying tasks forward = rescheduling, not re-creating.** When the
  user wants to move a task forward, edit the task line in its source
  file to update the `📅 YYYY-MM-DD` emoji-date. Don't add a duplicate
  task to the daily note. Use Edit, not the CLI, because the CLI's `task`
  command toggles done/todo status but doesn't reschedule.
- **Inline tasks in the prior daily's body are second-class.** If the
  user wrote `- [ ] thing` directly into the previous daily's `## Notes`,
  surface them but don't try to migrate them via task-line editing —
  instead, show them to the user and let them decide whether to copy the
  line into today's note, leave it in the old daily, or convert it to a
  proper Tasks-syntax checkbox with a due date.
- **Don't fabricate "tomorrow's commitments".** The evening preview should
  show only what's actually in the vault (Tasks with due/scheduled =
  tomorrow). If there's nothing, say "nothing on the books for
  tomorrow" — don't invent suggestions. Empty days are valid.
