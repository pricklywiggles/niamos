---
type: goal
status: active
areas: []
next_assessment_date: 
target_completion_date: 
actual_completion_date: 
---

## Success Metrics
- 

## Reassessment Logs

## Weekly Progress
*Template:* 

## Active Projects
```dataview
LIST
FROM [[]]
WHERE type = "project" AND status = "active"
```

## Active Habits
```dataview
LIST
FROM [[]]
WHERE type = "habit" AND status = "active"
```

## Completed Projects and Habits
```dataview
LIST
FROM [[]]
WHERE (type = "project" OR type = "habit") AND status = "archived"
SORT default(completion_date, established_date) DESC
```
