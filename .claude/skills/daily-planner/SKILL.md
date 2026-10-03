---
name: daily-planner
description: Build a plan for today from open tasks. Use when the user asks to plan their day, what to do today, or for a schedule.
---

# Daily planner

1. Read `data/tasks.json`. Ignore tasks with status `done`.
2. Pick today's tasks: anything overdue or due today, then `in_progress` tasks, then the highest-priority `todo` tasks. Aim for 3 to 6 items.
3. Order them with the most important or time-bound first. Put quick wins after the hard task.
4. Set the status of the first task to `in_progress` only if the user asked to start. Otherwise do not modify the file.
5. Reply with a numbered plan: id, title, why it is on today's list.
