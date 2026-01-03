"""Task plan management tools - additive operations.

These tools provide granular task management without replacing the entire list:
- update_task_plan: Add new tasks or modify existing ones (ADDITIVE)
- mark_task_complete: Mark a single task as complete (lightweight)

Unlike update_tasks which clears all tasks on each call, these tools
preserve existing task state.

Usage:
    # Add new tasks discovered during work
    update_task_plan({
        "add_tasks": ["Research competitor pricing", "Create comparison chart"],
        "main_task": "Competitive Analysis"
    })

    # Mark individual task complete
    mark_task_complete({
        "task_id": "t1",
        "notes": "Found 5 key data points"
    })
"""

from typing import Any

from research_agent.tasks import TaskProgress
from research_agent.tools.registry import registered_tool


@registered_tool(
    name="update_task_plan",
    description=(
        "Add new tasks or modify existing tasks in the current plan. "
        "This is ADDITIVE - it does not replace existing tasks. "
        "Use this when you discover additional work is needed during execution. "
        "To replace the entire plan, use clear_tasks first."
    ),
    parameters={
        "add_tasks": "List of new task descriptions to add (strings)",
        "modify_tasks": "List of {id, name?, status?, notes?} to modify existing tasks",
        "main_task": "Optional: Set or update the main task description",
    },
    parameter_types={
        "add_tasks": list,
        "modify_tasks": list,
        "main_task": str,
    },
)
async def update_task_plan(args: dict[str, Any]) -> dict[str, Any]:
    """Add or modify tasks without clearing existing ones.

    Args:
        args: Dictionary with:
            - add_tasks: List of task name strings to add
            - modify_tasks: List of {id, name?, status?, notes?} dicts
            - main_task: Optional main task description update

    Returns:
        MCP-formatted response with summary of changes.
    """
    add_tasks = args.get("add_tasks", [])
    modify_tasks = args.get("modify_tasks", [])
    main_task = args.get("main_task")

    progress = TaskProgress.load()
    changes: list[str] = []

    # Update main task if provided
    if main_task:
        progress.set_main_task(main_task, status="in_progress")
        truncated = main_task[:50] + "..." if len(main_task) > 50 else main_task
        changes.append(f"Set main task: {truncated}")

    # Add new tasks - find next available ID
    existing_ids = set(progress.subtasks.keys())
    next_num = 1
    while f"t{next_num}" in existing_ids:
        next_num += 1

    for task_name in add_tasks:
        if not isinstance(task_name, str) or not task_name.strip():
            continue
        task_id = f"t{next_num}"
        progress.add_subtask(task_id, task_name.strip())
        truncated = task_name[:40] + "..." if len(task_name) > 40 else task_name
        changes.append(f"Added [{task_id}]: {truncated}")
        next_num += 1
        existing_ids.add(task_id)

    # Modify existing tasks
    for mod in modify_tasks:
        if not isinstance(mod, dict):
            continue
        task_id = mod.get("id")
        if not task_id or task_id not in progress.subtasks:
            continue

        subtask = progress.subtasks[task_id]
        modified_fields = []

        if "name" in mod and mod["name"]:
            subtask.name = mod["name"]
            modified_fields.append("name")

        if "status" in mod:
            progress.update_status(task_id, mod["status"], notes=mod.get("notes"))
            modified_fields.append(f"status={mod['status']}")

        if modified_fields:
            changes.append(f"Modified [{task_id}]: {', '.join(modified_fields)}")

    # Check if all tasks are complete
    if progress.is_complete() and progress.main_task:
        progress.mark_main_complete()
        changes.append("All tasks complete - marked main task done")

    progress.save()

    if not changes:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "No changes made. Provide add_tasks or modify_tasks.",
                }
            ]
        }

    return {
        "content": [
            {
                "type": "text",
                "text": f"Task plan updated ({len(changes)} changes):\n"
                + "\n".join(f"  - {c}" for c in changes),
            }
        ]
    }


@registered_tool(
    name="mark_task_complete",
    description=(
        "Mark a specific task as complete. Call this immediately when you finish a subtask. "
        "Much lighter than update_tasks - just specify the task ID or name."
    ),
    parameters={
        "task_id": "The task ID (e.g., 't1', 't2') OR the task name to match",
        "notes": "Optional notes about what was accomplished",
        "files_modified": "Optional list of files that were created/modified",
    },
    parameter_types={
        "task_id": str,
        "notes": str,
        "files_modified": list,
    },
)
async def mark_task_complete(args: dict[str, Any]) -> dict[str, Any]:
    """Mark a single task as complete.

    Args:
        args: Dictionary with:
            - task_id: Task ID or name to find
            - notes: Optional completion notes
            - files_modified: Optional list of files

    Returns:
        MCP-formatted response confirming completion.
    """
    task_identifier = args.get("task_id", "")
    notes = args.get("notes")
    files_modified = args.get("files_modified", [])

    if not task_identifier:
        return {
            "content": [{"type": "text", "text": "Error: task_id is required"}],
            "is_error": True,
        }

    progress = TaskProgress.load()

    # Find task by ID or name
    target_task = None
    target_id = None

    # Try direct ID match first
    if task_identifier in progress.subtasks:
        target_id = task_identifier
        target_task = progress.subtasks[task_identifier]
    else:
        # Search by name (case-insensitive partial match)
        task_lower = task_identifier.lower()
        for tid, subtask in progress.subtasks.items():
            if task_lower in subtask.name.lower():
                target_id = tid
                target_task = subtask
                break

    if not target_task:
        available = list(progress.subtasks.keys())
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Task not found: '{task_identifier}'. Available: {available}",
                }
            ],
            "is_error": True,
        }

    # Check if already complete
    if target_task.status == "complete":
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Task '{target_task.name}' is already complete.",
                }
            ]
        }

    # Mark complete
    progress.update_status(
        target_id,
        "complete",
        notes=notes,
        files_modified=files_modified if files_modified else None,
    )

    # Check if all done
    all_complete = False
    if progress.is_complete() and progress.main_task:
        progress.mark_main_complete()
        all_complete = True

    progress.save()

    remaining = len(progress.get_incomplete())
    message = f"Marked '{target_task.name}' as complete."
    if all_complete:
        message += " All tasks complete!"
    elif remaining > 0:
        message += f" {remaining} task(s) remaining."

    return {"content": [{"type": "text", "text": message}]}
