---
type: wiki
---

```dataviewjs
const archived = dv.pages('"archives"').where(p => p.status === "archived");
const n = archived.length;
const itemWord = n === 1 ? "item" : "items";
const verb = n === 1 ? "has" : "have";
dv.paragraph(`**${n}** ${itemWord} ${verb} been archived. The source of truth is the \`status\` property; items also live under \`archives/<year>/<type>/\` for browsing.`);
```

---

### Recently archived (last 10)

```dataview
TABLE WITHOUT ID
  file.link AS "Item",
  type AS "Type",
  ended AS "Ended"
WHERE status = "archived"
FLATTEN choice(type = "goal", actual_completion_date, choice(type = "project", completion_date, established_date)) AS ended
SORT ended DESC
LIMIT 10
```

---

### Projects

```dataview
TABLE WITHOUT ID
  file.link AS "Project",
  completion_date AS "Shipped"
FROM ""
WHERE type = "project" AND status = "archived"
SORT completion_date DESC
```

### Goals

```dataview
TABLE WITHOUT ID
  file.link AS "Goal",
  actual_completion_date AS "Ended"
FROM ""
WHERE type = "goal" AND status = "archived"
SORT actual_completion_date DESC
```

### Habits

```dataview
TABLE WITHOUT ID
  file.link AS "Habit",
  established_date AS "Established / Stopped"
FROM ""
WHERE type = "habit" AND status = "archived"
SORT established_date DESC
```

---

### Browse by folder

`archives/` is organized as `archives/<year>/<type>/`. Open the file explorer to browse by year.
