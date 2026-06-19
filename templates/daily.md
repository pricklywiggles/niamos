---
type: daily
date: <% tp.file.title %>
---
## Todo

## Habits

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

## Past due tasks
```tasks
not done
(due before <% tp.file.title %>) OR (scheduled before <% tp.file.title %>)
path does not include daily/
path does not include archives/
```
