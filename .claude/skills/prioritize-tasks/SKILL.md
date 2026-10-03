---
name: prioritize-tasks
description: Rank open tasks by due date and priority and update their priority fields. Use when the user asks what to work on first, to prioritise, or to reorder tasks.
---

# Prioritize tasks

1. Read `data/tasks.json`. Consider only tasks whose status is not `done`.
2. Rank them: overdue first, then soonest due date, then `high` > `medium` > `low`. Tasks with no due date go last within their priority.
3. Raise `priority` to `high` for anything overdue or due within 2 days. Change nothing else without saying so.
4. Write the file back as valid JSON, keeping every field of every task.
5. Reply with the ranked list (id, title, due, priority) and a one-line reason for any priority change.
