---
type: wiki
---

Permanent spheres of responsibility — no status, no end date.

---

### Active children per area

```dataviewjs
const areas = dv.pages('"areas"').sort(a => a.file.name);
const rows = areas.values.map(a => {
  const path = a.file.path;
  const goals = dv.pages('"goals"').where(g =>
    g.status === "active" && g.areas && g.areas.some(x => x && x.path === path)
  ).length;
  const projects = dv.pages('"projects"').where(p =>
    p.status === "active" && p.areas && p.areas.some(x => x && x.path === path)
  ).length;
  return [a.file.link, goals, projects];
});
dv.table(["Area", "Active Goals", "Active Projects"], rows);
```

---

### Active Goals by area

```dataview
TABLE WITHOUT ID
  areas[0] AS "Area",
  file.link AS "Goal",
  target_completion_date AS "Target"
FROM "goals"
WHERE status = "active"
SORT areas[0] ASC, file.name ASC
```

---

### Active Projects by area

```dataview
TABLE WITHOUT ID
  areas[0] AS "Area",
  file.link AS "Project",
  due_date AS "Due"
FROM "projects"
WHERE status = "active"
SORT areas[0] ASC, due_date ASC
```
