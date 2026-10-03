---
name: task-breakdown
description: Split a large task into concrete subtasks and add them to the task list. Use when the user asks to break down, decompose, or plan the steps of a task.
---

# Task breakdown

1. Read `data/tasks.json` and find the parent task by id or title. If it does not exist, create it first with the next unused id.
2. Propose 3 to 7 subtasks. Each must be a small, actionable step that can be finished in one sitting.
3. Add each as a new task with the next unused ids, `status: "todo"`, `parent_id` set to the parent's id, the parent's `priority`, and a `due` no later than the parent's due date.
4. Write the file back as valid JSON, keeping every existing task unchanged.
5. Reply with the list of subtasks you added (id, title).
