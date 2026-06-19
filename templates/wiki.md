---
type: wiki
tag_filter: 
---

---
```dataviewjs
const tag = "#" + dv.current().tag_filter;
const results = [];

for (const page of dv.pages().sort(p => p.file.name, 'desc')) {
  if (page.file.path === dv.current().file.path) continue;
  for (const item of page.file.lists) {
    if (item.tags && item.tags.some(t => t.toLowerCase() === tag.toLowerCase())) {
      results.push([page.file.link, item.text]);
    }
  }
}

if (results.length > 0) {
  dv.header(3, "Tagged references");
  dv.table(["Page", "Note"], results);
}
```
