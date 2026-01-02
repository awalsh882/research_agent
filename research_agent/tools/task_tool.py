"""Task management tool for the Research Agent.

Provides a TodoWrite-style interface for tracking task progress.
The agent calls this tool to update tasks, similar to Claude Code's built-in TodoWrite.

Usage:
    # Agent calls the tool with a list of todos
    update_tasks({
        "todos": [
            {"content": "Research DocuSign", "status": "complete"},
            {"content": "Research Adobe", "status": "in_progress"},
            {"content": "Compare metrics", "status": "pending"}
        ]
    })
"""

from typing import Any

from research_agent.tasks import TaskProgress
from research_agent.tools.registry import registered_tool


@registered_tool(
    name="update_tasks",
    description="Update the task progress list. Use this to track multi-step tasks. "
    "The UI displays task progress in real-time. Status can be: pending, in_progress, complete.",
    parameters={
        "main_task": "Brief description of the overall task (optional, updates main task if provided)",
        "todos": "List of task objects with 'content' (task description) and 'status' (pending/in_progress/complete)",
    },
    parameter_types={
        "main_task": str,
        "todos": list,
    },
)
async def update_tasks(args: dict[str, Any]) -> dict[str, Any]:
    """Update task progress, similar to Claude Code's TodoWrite.

    Args:
        args: Dictionary with optional 'main_task' and required 'todos' list.
              Each todo has 'content' (str) and 'status' (str).

    Returns:
        MCP-formatted response confirming the update.
    """
    main_task = args.get("main_task")
    todos = args.get("todos", [])

    # Load existing progress or create new
    progress = TaskProgress.load()

    # Update main task if provided
    if main_task:
        progress.set_main_task(main_task, status="in_progress")

    # Clear existing subtasks and add new ones
    progress.subtasks.clear()

    for i, todo in enumerate(todos):
        content = todo.get("content", "")
        status = todo.get("status", "pending")

        # Validate status
        valid_statuses = {"pending", "in_progress", "complete", "blocked", "skipped"}
        if status not in valid_statuses:
            status = "pending"

        task_id = f"t{i + 1}"
        subtask = progress.add_subtask(task_id, content)
        progress.update_status(task_id, status)

    # Check if all tasks are complete
    if progress.is_complete() and progress.main_task:
        progress.mark_main_complete()

    # Save to file
    progress.save()

    # Build summary
    complete_count = sum(1 for t in todos if t.get("status") == "complete")
    in_progress_count = sum(1 for t in todos if t.get("status") == "in_progress")
    pending_count = sum(1 for t in todos if t.get("status") == "pending")

    summary = f"Tasks updated: {complete_count} complete, {in_progress_count} in progress, {pending_count} pending"

    return {
        "content": [
            {
                "type": "text",
                "text": summary,
            }
        ]
    }


@registered_tool(
    name="clear_tasks",
    description="Clear all task progress. Use when starting fresh or when all tasks are done.",
    parameters={},
    parameter_types={},
)
async def clear_tasks(args: dict[str, Any]) -> dict[str, Any]:
    """Clear all task progress.

    Args:
        args: Empty dictionary (no parameters needed).

    Returns:
        MCP-formatted response confirming the clear.
    """
    progress = TaskProgress.load()
    progress.clear()

    return {
        "content": [
            {
                "type": "text",
                "text": "Task progress cleared.",
            }
        ]
    }
