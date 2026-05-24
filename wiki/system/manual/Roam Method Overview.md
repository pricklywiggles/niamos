# My Organization Method

This document describes how I currently organize my work and life. I run this method in **Roam Research** today (the screenshots are Roam), and I want to migrate it to **Obsidian**. It is a conceptual overview, not an implementation spec. The purpose is to give an agent enough understanding of both my intent and the Roam features the method relies on, so it can codify the method in Obsidian, find the plugins or functionality that reproduce those features, and keep things consistent over time.

## Lineage and where I diverge

The method is PARA (Projects, Areas, Resources, Archives) with two changes:

- I add **Goals** as a first-class content type. Goals are about measurable outcomes; Projects are about the work that drives them.
- What PARA calls **Resources** I call the **Wiki**. It plays the same role: durable reference material that outlives any single project.

So my content types are **Goals, Areas, Projects, Habits, Wiki, and Archives**. Habits sit alongside Projects as the second kind of work that drives a Goal.

## Core mechanics that apply everywhere

A few vault-wide conventions hold across all content types:

- **Linking is the connective tissue.** Pages reference each other by link, and every page surfaces an automated **Linked References** section showing where it is mentioned across the vault. This backlinking is what lets a Goal know its Projects, an Area know its Goals, and so on, without manually maintaining both ends of the relationship.
- **Dates are links to daily notes.** Any date (assessment dates, due dates, progress entries) is a link to that day's daily note, so context lives in two places at once: on the topic page and in the day it happened. This is a deep enough part of the method to get its own section below.
- **Keywords are tags that drive grouping.** Tags like `#Areas`, `#Projects`, and `#Archives` let pages roll up automatically into index pages and let me filter by type and status. Keywords are doing real structural work, not just decoration.

A note on consistency: my actual vault is not perfectly uniform. Habit keywords follow a `#Habit-Name` pattern while area keywords sometimes appear inline as `#Area: Name`. When helping me codify this, treat the *intent* below as load-bearing and the exact current spelling as something to normalize rather than preserve.

## Why this works: the Roam features the method depends on

The whole method rests on three Roam capabilities. Most of the value is not in the page templates themselves but in the fact that relationships and lists assemble themselves automatically. An agent reproducing this in Obsidian needs to match these capabilities (likely via core backlinks plus a query plugin such as Dataview), not just the page shapes.

- **Backlinks (Linked References).** Every page automatically shows where it is referenced from anywhere else in the vault. I only declare a relationship once, from one side, and it becomes visible from both. A Project lists the Goals it serves, and each Goal's page then shows that Project under Linked References without my touching the Goal. This is what keeps the graph consistent: there is no second copy of a relationship to fall out of sync. Crucially this is **block-level**: the reference list shows the specific block that mentioned the page along with its surrounding context, not just "this page is mentioned somewhere." That per-block context is load-bearing, it is what makes a Linked References list readable and useful rather than a bare list of page names. This is the feature most at risk in migration: a target tool that only does page-level backlinks loses the context, and Obsidian's block referencing works differently from Roam's (where every block is addressable by default), so the agent should treat reaching parity here as a known hard problem, not an assumption.

- **Keywords as queryable tags.** Tags like `#Areas`, `#Projects`, and `#Archives` are not labels, they are membership. Tagging a page with `#Areas` is what puts it on the master Areas index. Moving a project to `#Archives` is what removes it from active views. The tag *is* the mechanism, so the index pages never need manual maintenance.

- **Filtering reference lists.** This is the piece that turns the above into real functionality. Roam lets me filter a page's Linked References by tag, so a single Goal page can answer "show only the active Projects referencing this" or "only the Habits," and an Area page can show only the Projects in it that aren't archived. The combination of automatic backlinks plus filtering is what lets one page act as a live, queryable dashboard instead of a static document. When the agent picks Obsidian tooling, the ability to filter and query these lists (by tag, by status, by type) is the requirement that matters most.

The takeaway for the agent: replicate *automatic, filterable, two-way relationships*, not just the headings. If the target tool can only produce static backlinks with no filtering, much of the method's usefulness is lost and a query plugin is required to recover it.


---

## Goal

A Goal defines a measurable outcome and tracks progress toward it over a fixed period. It is the most structured content type because it is the one I assess on a schedule.

A Goal page has these sections:

**Metadata**
- *Success metrics:* a bulleted list of well-written, measurable conditions that define what "done" means. These should be concrete enough to answer yes/no or hit a number (e.g. an average, a count, a trend), and they can include a subjective check-in question.
- *Associated Projects/Habits:* links to the Project and Habit pages that drive this goal. This is how a Goal connects to the work underneath it.
- *Next assessment date:* a daily-note link marking when I will next review progress.
- *Goal completion date:* a daily-note link for the intended finish.
- *Actual completion date:* a daily-note link, filled in when actually done. The gap between intended and actual is itself useful signal.

**Reassessment Logs**
- A list of date links, each followed by notes from that day. Entries are added on assessment dates to record progress, course corrections, or new ideas. This is the narrative history of the goal.

**Weekly Progress**
- A *template* showing the format each weekly entry should follow.
- A list of dates, each followed by that week's numbers against the metrics, plus a recurring subjective question (e.g. "Do I feel better?"). The weekly cadence is lighter-weight than reassessment; it is for tracking the metrics, not rethinking the goal.

**Linked References**
- The automated list of everywhere this goal is mentioned across the vault.

The defining feature of a Goal is the loop: metrics define the target, weekly progress measures against it, and reassessment logs decide whether the target or the approach needs to change.

See `temp/goal.png` for an example.

## Area

An Area is an ongoing sphere of responsibility with no end date (e.g. Productivity, Health, Professional Development). Goals and Projects are temporary; Areas are permanent. An Area is intentionally lightweight.

An Area page has one real section:

**Metadata**
- *Keywords:* a list of tags. This **must include `#Areas`** so the page is automatically linked into the master Areas index.
- *Goals:* plain-English sentences describing what I am trying to accomplish in this area. These are aspirational and qualitative, in contrast to a Goal page's hard metrics.

**Linked References**
- The automated list of everywhere this area is referenced. In practice this is how an Area stays useful: Projects and Wiki pages tag themselves with the area, and the Area page becomes a live index of everything that belongs to it.

The key distinction: an Area's "Goals" field is a sentence about direction, whereas a Goal page is a measured commitment. They are different concepts that happen to share a word.

See `temp/area.png` for an example.

## Project

A Project is a finite body of work with a deliverable and a due date. Projects are where Goals get executed.

A Project page has these sections:

**Metadata**
- *Keywords:* `#Projects` while active. When a project is finished or deprecated it is moved to Archives and tagged `#Archives` (see the Archives section).
- *Due Date:* a daily-note link.
- *Completion date:* a daily-note link.
- *Goals:* links to the Goal pages this project serves. This is the upward connection that lets a Goal see its driving projects via backlinks.

**Project Todos**
- A checklist of actionable items for the project.

**Notes**
- Freeform working notes, including "nice to have" ideas and dated reflections.

A Project is distinguished from a Goal by what it tracks: a Project tracks *tasks and a deliverable*, a Goal tracks *metrics and an outcome*. A single Goal may be served by several Projects and Habits.

See `temp/project.png` for an example.

## Habit

A Habit is a recurring behavior I am trying to make automatic. Like an Area, the page is minimal; unlike an Area, a Habit has a finish line of sorts. A Habit drives Goals the way a Project does, but it tracks *repetition becoming routine* rather than tasks toward a deliverable.

A Habit page has one section:

**Metadata**
- *Goals:* links to the Goal pages this habit serves. A single habit can serve more than one goal.
- *Start:* a daily-note link for when I began establishing the habit.
- *Declared established:* a daily-note link, filled in when the habit has become such an integral part of my day that I no longer need to track it. This is the Habit's equivalent of a completion date, and reaching it is what triggers archiving the habit, the same way finishing a project archives it.

**Linked References**
- The automated list of everywhere this habit is referenced. In practice the habit's keyword (e.g. `#Habit-OnlineOutreach`) is what links it back to the Goals that list it under Associated Projects/Habits.

The lifecycle is the distinguishing feature: a Habit runs from *Start* until *Declared established*, the point where it has become integral enough that tracking is unnecessary. Reaching that point is treated like finishing a project: the habit is archived rather than "completed" like a project or "achieved" like a goal.

See the Habit-OnlineOutreach example.



The Wiki is durable reference material: everything I learn, collect, or want to come back to that is not tied to a deadline. This is the largest and least structured part of the vault, and the part where I most want an agent's help.

Characteristics of the Wiki:

- **Content is varied.** It holds learning references (e.g. notes while learning vector databases or git), how-to guides, vocabulary lists, inspiration boards, favorite artists, programming notes, and more.
- **Pages connect both ways.** Wiki pages are often referenced from Goals, Projects, and Areas, but many also stand alone as pure reference I return to later.
- **It tends toward entropy.** The root is currently a grab-bag with no strong organizing principle. This is the core problem to manage.

What I need from an agent working in the Wiki:

- **Find the right home.** When I produce a reference document (e.g. "everything I'm learning about vector databases"), help me place it where it logically belongs rather than dumping it at the root.
- **Resist the kitchen drawer.** Actively push back when the structure is degrading into an unsorted pile. Suggest grouping, hierarchy, or links that keep related material discoverable.
- **Stay flexible.** Do not impose a rigid taxonomy. The Wiki has to accommodate genuinely unrelated topics. The goal is *navigability*, not a perfect tree.

The tension to manage: the Wiki must be open enough to hold anything, but organized enough that I can find things and that links from Goals/Projects/Areas point somewhere sensible.

## Archives

Archives is where finished or deprecated things go: a completed project, a goal that has run its course, anything no longer active but worth keeping. It is a holding area, not a content type with its own page structure. A project that moves to Archives keeps its original shape; it is simply marked (e.g. tagged `#Archives`) and is no longer treated as active.

The point of Archives is to keep the active workspace clean without losing history. Backlinks still resolve, so an archived project remains visible from the Goals it served, but it drops out of any view that lists current work.

---

## Index pages

Each type has a master index page: **Goals, Areas, Projects, Habits, and Archives**. Together these are the top-level view of the whole system, the entry point I navigate from. I start at an index, reach a Goal, and from there follow links down to its Projects, Habits, and the Wiki pages they reference. Everything in the vault is reachable from these five pages, so they function as the navigational spine, not just convenience lists.

These are not hand-maintained lists. Each one is an automated, filtered query that collects every page of its type, built directly on the keyword-as-membership mechanic. Tagging a page `#Projects` is what makes it appear on the Projects index; no second step.

The filtering is what keeps these pages meaningful:

- The active-type indexes (Projects, Habits, Goals, Areas) show only items that are still active, excluding anything that has moved to Archives.
- The **Archives** index is the inverse: it collects everything tagged `#Archives` regardless of its original type, so a finished project and an established habit both surface there.

This is the most visible payoff of the whole system. Because membership and status are expressed as tags and the lists are generated by query, an item appears in exactly the right index the moment I tag it and moves between indexes the moment its status changes, with no manual list-keeping. For the agent, these index pages are the clearest test of whether the chosen Obsidian tooling is sufficient: reproducing them requires querying the vault by tag and filtering by status, which is precisely the Dataview-style capability called out earlier.

---

## Daily notes

Every date in the vault is a link to a daily note. In Roam, writing a date like `[[March 2nd, 2026]]` creates a link that resolves to that day's page: if the page does not exist yet, it is created the first time I click through; if it does, the link just takes me there. There is no separate step to make the day's page, the link is the page.

The power comes from the same backlink mechanic the type pages use, pointed at a day. A daily note shows its own Linked References, so opening any day surfaces everything across the vault that points at it: goals being assessed that day, projects due, habits started, weekly progress entries, plus whatever freeform notes I add directly to the day. The day's page becomes an automatic agenda assembled from the rest of the system, without my collecting anything by hand.

This is what powers planning, weekly reviews, and other recurring workflows (the details of which we can leave for later). The point for now is that daily notes are not a journaling add-on; they are a core surface that the date fields throughout the method feed into.

Two behaviors the agent needs to find analogues for:

- **Link-creates-the-page.** A date link should resolve to a daily note, creating it on demand rather than requiring me to make the page first. Obsidian's daily-note handling differs from Roam's here (date links do not autogenerate identically, and this typically depends on a daily-notes plugin and a consistent date format), so this is a specific behavior to reproduce, not an assumption.
- **Backlinks as agenda.** The daily note must show what references it, filtered usefully, so the day reads as a to-do/assessment view rather than a raw mention list. This is the same filtered-backlink requirement as the index pages, applied to dates.

---

## How the types relate

The shape of the system, in one pass:

- **Areas** are permanent buckets of responsibility. They sit at the top and rarely change.
- **Goals** live under Areas and define measurable outcomes with a deadline and an assessment loop.
- **Projects** live under Goals and do the actual work, tracked as todos against a due date.
- **Habits** also live under Goals but track a recurring behavior from *Start* to *Declared established*, rather than tasks toward a deliverable.
- **The Wiki** is referenced by all of the above and also stands on its own, holding the durable knowledge that supports everything.
- **Archives** sits to the side. When a Goal, Project, or Habit is done or abandoned it moves here, preserving history while staying out of active views.

Backlinks tie it together: I generally only have to declare a relationship from one side (e.g. a Project lists its Goals), and the automated Linked References section makes the relationship visible from the other side too.

## Notes for the agent

- This document describes the *current* state and intent, not a finished standard. Expect inconsistency in the live vault and help me converge it.
- When in doubt, preserve the conceptual distinctions (Goal = measured outcome, Area = ongoing responsibility, Project = finite deliverable, Habit = behavior becoming automatic, Wiki = durable reference, Archives = inactive but kept) even if you normalize the surface conventions (keyword spelling, section ordering, date formats).
- There is more to this method than is captured here; treat this as a foundation to build on.
