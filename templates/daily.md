---
type: daily
date: <% tp.file.title %>
---

## Notes
- 

## Highlights
- 

## Today
```dataview
LIST
FROM ""
WHERE (type = "goal" AND next_assessment_date = date(this.file.name))
   OR (type = "goal" AND target_completion_date = date(this.file.name))
   OR (type = "project" AND due_date = date(this.file.name))
```

## Tasks
```tasks
(due on <% tp.file.title %>) OR (scheduled on <% tp.file.title %>)
```
