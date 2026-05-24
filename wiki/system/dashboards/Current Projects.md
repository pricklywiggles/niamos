---
type: wiki
---

```dataviewjs
const projects = dv.pages('"projects"').where(p => p.status === "active");
const n = projects.length;
const areaSet = new Set();
projects.forEach(p => { if (p.areas) p.areas.forEach(a => { if (a && a.path) areaSet.add(a.path); }); });
const a = areaSet.size;
const projectWord = n === 1 ? "project" : "projects";
const areaWord = a === 1 ? "area" : "areas";
dv.paragraph(`You have **${n}** active ${projectWord} across **${a}** ${areaWord}.`);
```

---

### Active, by area

```dataview
TABLE WITHOUT ID
  areas[0] AS "Area",
  file.link AS "Project",
  due_date AS "Due",
  length(filter(file.tasks, (t) => !t.completed)) AS "Open todos"
FROM "projects"
WHERE status = "active"
SORT areas[0] ASC, due_date ASC
```

---

### Past due

```dataview
TABLE WITHOUT ID
  file.link AS "Project",
  due_date AS "Was due",
  date(today) - due_date AS "Late by"
FROM "projects"
WHERE status = "active" AND due_date < date(today)
SORT due_date ASC
```

---

### Without a due date

```dataview
LIST WITHOUT ID file.link
FROM "projects"
WHERE status = "active" AND !due_date
```
