---
type: wiki
---

```dataviewjs
const goals = dv.pages('"goals"').where(p => p.status === "active");
const n = goals.length;
const areaSet = new Set();
goals.forEach(g => { if (g.areas) g.areas.forEach(a => { if (a && a.path) areaSet.add(a.path); }); });
const a = areaSet.size;
const goalWord = n === 1 ? "goal" : "goals";
const areaWord = a === 1 ? "area" : "areas";
dv.paragraph(`You have **${n}** active ${goalWord} across **${a}** ${areaWord}.`);
```

---

### Active, by area

```dataview
TABLE WITHOUT ID
  areas[0] AS "Area",
  file.link AS "Goal",
  target_completion_date AS "Target",
  next_assessment_date AS "Next review"
FROM "goals"
WHERE status = "active"
SORT areas[0] ASC, target_completion_date ASC
```

---

### Target date passed

```dataview
TABLE WITHOUT ID
  file.link AS "Goal",
  target_completion_date AS "Target was",
  date(today) - target_completion_date AS "Late by"
FROM "goals"
WHERE status = "active" AND target_completion_date < date(today)
SORT target_completion_date ASC
```

---

### Reassessment overdue (>7 days)

```dataview
TABLE WITHOUT ID
  file.link AS "Goal",
  next_assessment_date AS "Was due",
  date(today) - next_assessment_date AS "Overdue by"
FROM "goals"
WHERE status = "active" AND next_assessment_date < (date(today) - dur(7 days))
SORT next_assessment_date ASC
```
