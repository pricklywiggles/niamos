---
type: wiki
---

# Habit

A **Habit** is a recurring behavior becoming automatic. The opposite of a [[Project]] — instead of a finite deliverable, a Habit is an ongoing practice that "graduates" when integrated into normal life. Habits drive [[Goal]]s.

## Frontmatter schema

```yaml
---
type: habit
status: active                # active | archived
goals: ["[[Goal - <name>]]"]  # list of Goal wikilinks
start_date:                   # date — when you started practicing it
established_date:             # date — filled when archived ("graduated")
---
```

Note: Habits only declare `goals`, not `areas`. The [[Area]] membership comes transitively through the Goal.

Filename: `Habit - <Human Name>.md` in `habits/`. See [[Naming and Wikilinks]].

## Body sections

- `## Tasks` — the recurring behaviors that make up this habit. Each line is a checkbox in a strict format (see below) that the [[Daily|daily review]] morning flow reads to decide what to surface today, and the evening flow writes back to.
- `## Notes` — prose, observations about the habit's progress. The [[Skills|archive skill]] prepends to this section when archiving with a reason.

Habits are intentionally light on structure outside `## Tasks` — the practice is what matters, not the documentation.

## The `## Tasks` section format

Each task is one line:

```
- [ ] <name> - <cadence> - last: <YYYY-MM-DD or empty>
```

The checkbox stays `- [ ]` on the habit page (master template). Completion happens in the daily note, and the evening review writes the date back into `- last:` here.

**Cadences:**

| Token | Fires when | Anchor |
|---|---|---|
| `daily` | `(today - last) >= 1` or `last:` empty | last completion |
| `weekly` | `(today - last) >= 7` or `last:` empty | last completion |
| `every Nd` | `(today - last) >= N` | last completion |
| `every Nw` | `(today - last) >= N*7` | last completion |
| `mon`, `tue`, … `sun` | today's weekday matches | calendar |
| `mon,wed,fri` | today's weekday is in the set | calendar |
| `weekdays` | Mon–Fri | calendar |
| `weekends` | Sat+Sun | calendar |
| `mwf`, `tth`, `mth`, `mtwthf`, `satsun` | smushed shorthands | calendar |

**Anything else** — use the comma-separated form (`mon,wed,fri`). The smushed forms above are the only ones recognized; novel combos like `mw` or `wf` will fail audit. If you find yourself wanting a new one often, add it to `SMUSHED` in both `.claude/skills/daily-review/scripts/habits.py` and `.claude/skills/audit/scripts/audit.py`.

**Do not check off tasks on the habit page.** The habit page is the master template — checkboxes stay `- [ ]` forever. If you click one in reading mode, the Tasks plugin will glue ` ✅ <date>` onto the cadence string. The parser tolerates a one-off slip (strips the trailing `✅ <date>` before evaluating), but the intended workflow is: check items off in the **daily note's `## Habits` section** and let evening review write back `- last:` to the habit page.

**Bootstrap:** an empty (or missing) `- last:` means "fire today." A new habit task fires on the next morning review, then settles into its cadence from then on.

**Snooze a cycle:** edit `- last:` to a future date. The task won't fire until `(today - last) >= N`, even if N is small.

**Calendar cadences also update `last:` on completion** — uniform data model. The completion date isn't *used* for firing on calendar cadences, but it's tracked so the [[Skills|audit skill]] can flag a `mon` task that hasn't been completed in 3 weeks.

## The morning/evening loop

- **Morning review** reads every active habit's `## Tasks` section, evaluates each line's cadence against today, and copies firing tasks into today's daily under `## Habits` as plain `- [ ] <name>` lines (the cadence and last-date suffix are dropped — the daily is just "things to do today").
- **Evening review** scans today's daily's `## Habits` section for `- [x]` lines and rewrites the matching habit-page task line's `- last:` to today. The contract: check off your completed habits in the daily before running evening review. Evening review prompts you if any are still unchecked.

Name match between daily and habit page is case-insensitive and exact. Two habits with the same task name would collide — the [[Skills|audit skill]] flags that case as `habit-task-collision`.

## Relationship to other types

- **Declares**: `goals`.
- **Is discovered by**: [[Goal]] (via the Goal's `## Active Habits` Dataview slice).
- **Does NOT declare**: `areas`. Transitive through Goal.

## Lifecycle and the "established" semantics

- Born `status: active` with a `start_date`. Lives during the active formation period.
- "Archived" is a misnomer for Habits — it's really **graduated**. The Habit is now automatic, integrated, no longer requiring active attention. `established_date` records when this transition happened.
- Mechanically the same as archiving anything else: the [[Skills|archive skill]] flips `status` to `archived`, fills `established_date`, moves the file to `archives/<year>/habits/`. See [[Archives]].
- A Habit could also be abandoned (not established, just stopped). The schema treats both endings the same — `status: archived` with `established_date` set. The body notes are where you record *which* kind of ending it was.

## See also

- [[PARA Method]] — where Habits fit
- [[Goal]] — the upstream type Habits declare
- [[Archives]] — terminal state
- [[Skills]] — `create-page` builds them, `archive` graduates them
