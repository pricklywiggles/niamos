# Morning workflow

The morning flow has three jobs in order:
1. Open today's daily note and read what's already there.
2. Look back at the most recent prior daily note for undone work.
3. Offer to carry that work forward to today, then leave the user to it.

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
daily's date and are still not done.** Use:

```
obsidian tasks todo verbose format=json
```

This returns every incomplete task in the vault with its file path and
line number. The Tasks plugin's date format is `📅 YYYY-MM-DD` (due
date) or `⏳ YYYY-MM-DD` (scheduled date). Parse each task line for
either emoji-date and filter to those where the date is ≤ prior-daily's
date.

**(B) Inline `- [ ]` checkboxes written directly in the prior daily's
body** (not Tasks-plugin queries, but actual checkbox lines in `## Notes`
or `## Highlights`). Read the prior daily file and grep for `- [ ]` lines
in the body. These are second-class — they don't have a due date — so
treat them as "stuff the user jotted down and never finished".

## Step 4: Surface and ask

If both lists are empty: say "nothing to carry forward from
`<prior-date>`" and end. No question needed.

If non-empty, present a single AskUserQuestion with the options:
- **Carry everything forward** — reschedule all (A) to today, copy all
  (B) into today's note's `## Notes` as new inline checkboxes.
- **Pick which** — present a second multi-select AskUserQuestion listing
  each item; carry forward only the selected ones.
- **Carry nothing forward** — leave the prior note alone, do nothing.

Keep the option descriptions tight. The user is doing this every day; they
shouldn't have to read a paragraph.

## Step 5: Execute the carry-forward

For (A) tasks (rescheduling): for each chosen task, Edit the source file
to replace the existing `📅 YYYY-MM-DD` or `⏳ YYYY-MM-DD` emoji-date
with today's date. If the task has no date emoji, add `📅 <today>` at
the end of the line. The task stays in its source file — the Tasks
plugin block in today's daily will pick it up automatically because the
new date matches today.

For (B) inline checkboxes: copy each one verbatim into today's daily
note's `## Notes` section. Edit the today daily, inserting the lines
right after `## Notes`. Optionally suggest the user convert them to
proper Tasks-syntax (with a due date) but don't do it for them — that's
a judgment call about whether the task is real or just a thought.

## Step 6: Close

One short summary line: "Carried forward 3 tasks, 1 inline note.
`<today>` is open." Or, if no carryover: "Nothing to carry. `<today>`
is open."

Don't list everything you did. The summary's job is "yes, I did the
thing", not "here's a detailed receipt".
