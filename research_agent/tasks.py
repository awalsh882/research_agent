"""Task progress tracking system for the Research Agent.

Provides persistent task state that survives across sessions, with support for
subtask dependencies, status tracking, and audit logging.

Usage:
    from research_agent.tasks import TaskProgress

    # Load or create progress file
    progress = TaskProgress.load()

    # Initialize a new main task
    progress.set_main_task("Add user authentication", status="in_progress")

    # Add subtasks
    progress.add_subtask("t1", "Install auth dependencies")
    progress.add_subtask("t2", "Create User model", dependencies=["t1"])
    progress.add_subtask("t3", "Implement JWT tokens", dependencies=["t1"])

    # Update status as work progresses
    progress.update_status("t1", "complete")
    progress.update_status("t2", "in_progress")

    # Check completion
    if progress.is_complete():
        print("All tasks done!")

    # Save changes
    progress.save()
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

# Task status types
TaskStatus = Literal["pending", "in_progress", "complete", "blocked", "skipped"]

# Default progress file location (project root)
DEFAULT_PROGRESS_FILE = Path(".task-progress.json")


@dataclass
class Subtask:
    """A single subtask within a larger task."""

    id: str
    name: str
    description: str = ""
    status: TaskStatus = "pending"
    dependencies: list[str] = field(default_factory=list)
    started_at: str | None = None
    completed_at: str | None = None
    files_modified: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "dependencies": self.dependencies,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "files_modified": self.files_modified,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Subtask:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            dependencies=data.get("dependencies", []),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            files_modified=data.get("files_modified", []),
            notes=data.get("notes", ""),
        )


@dataclass
class MainTask:
    """The main task being tracked."""

    description: str
    status: TaskStatus = "pending"
    priority: str = "normal"
    estimated_subtasks: int | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "estimated_subtasks": self.estimated_subtasks,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MainTask:
        """Create from dictionary."""
        return cls(
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            priority=data.get("priority", "normal"),
            estimated_subtasks=data.get("estimated_subtasks"),
        )


@dataclass
class AuditEntry:
    """An entry in the audit log."""

    timestamp: str
    task_id: str
    action: str
    from_status: str | None = None
    to_status: str | None = None
    details: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        entry = {
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "action": self.action,
        }
        if self.from_status:
            entry["from"] = self.from_status
        if self.to_status:
            entry["to"] = self.to_status
        if self.details:
            entry["details"] = self.details
        return entry

    @classmethod
    def from_dict(cls, data: dict) -> AuditEntry:
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            task_id=data["task_id"],
            action=data["action"],
            from_status=data.get("from"),
            to_status=data.get("to"),
            details=data.get("details"),
        )


class TaskProgress:
    """Manages task progress tracking with persistence.

    Stores progress in a JSON file that survives across sessions.
    Supports subtask dependencies, status tracking, and audit logging.
    """

    VERSION = "1.0"

    def __init__(self, file_path: Path | None = None):
        """Initialize task progress tracker.

        Args:
            file_path: Path to the progress file. Defaults to .task-progress.json
        """
        self.file_path = file_path or DEFAULT_PROGRESS_FILE
        self.created_at: str | None = None
        self.updated_at: str | None = None
        self.session_id: str | None = None
        self.main_task: MainTask | None = None
        self.subtasks: dict[str, Subtask] = {}
        self.context: dict = {"key_decisions": [], "blockers_encountered": []}
        self.audit_log: list[AuditEntry] = []

    @classmethod
    def load(cls, file_path: Path | None = None) -> TaskProgress:
        """Load progress from file, or create new if doesn't exist.

        Args:
            file_path: Path to the progress file.

        Returns:
            TaskProgress instance with loaded or fresh state.
        """
        progress = cls(file_path)
        path = progress.file_path

        if path.exists():
            try:
                data = json.loads(path.read_text())
                progress._load_from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                # Invalid file - start fresh but log warning
                print(f"Warning: Could not load {path}: {e}")
                progress._initialize_new()
        else:
            progress._initialize_new()

        return progress

    def _initialize_new(self) -> None:
        """Initialize a new progress file."""
        now = datetime.now(timezone.utc).isoformat()
        self.created_at = now
        self.updated_at = now

    def _load_from_dict(self, data: dict) -> None:
        """Load state from dictionary."""
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.session_id = data.get("session_id")

        if "main_task" in data and data["main_task"]:
            self.main_task = MainTask.from_dict(data["main_task"])

        for subtask_data in data.get("subtasks", []):
            subtask = Subtask.from_dict(subtask_data)
            self.subtasks[subtask.id] = subtask

        self.context = data.get("context", {"key_decisions": [], "blockers_encountered": []})

        for entry_data in data.get("audit_log", []):
            self.audit_log.append(AuditEntry.from_dict(entry_data))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.VERSION,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "session_id": self.session_id,
            "main_task": self.main_task.to_dict() if self.main_task else None,
            "subtasks": [st.to_dict() for st in self.subtasks.values()],
            "context": self.context,
            "audit_log": [e.to_dict() for e in self.audit_log],
        }

    def save(self) -> None:
        """Save progress to file."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.file_path.write_text(json.dumps(self.to_dict(), indent=2))

    def set_main_task(
        self,
        description: str,
        status: TaskStatus = "in_progress",
        priority: str = "normal",
        estimated_subtasks: int | None = None,
    ) -> None:
        """Set or update the main task.

        Args:
            description: What the main task is about.
            status: Current status.
            priority: Task priority (low, normal, high).
            estimated_subtasks: Expected number of subtasks.
        """
        self.main_task = MainTask(
            description=description,
            status=status,
            priority=priority,
            estimated_subtasks=estimated_subtasks,
        )
        self._add_audit("main", "created", to_status=status, details=description)

    def add_subtask(
        self,
        task_id: str,
        name: str,
        description: str = "",
        dependencies: list[str] | None = None,
    ) -> Subtask:
        """Add a new subtask.

        Args:
            task_id: Unique identifier for the subtask.
            name: Short name for the subtask.
            description: Detailed description.
            dependencies: List of task IDs this depends on.

        Returns:
            The created Subtask.
        """
        subtask = Subtask(
            id=task_id,
            name=name,
            description=description,
            dependencies=dependencies or [],
        )
        self.subtasks[task_id] = subtask
        self._add_audit(task_id, "created", to_status="pending", details=name)
        return subtask

    def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        notes: str | None = None,
        files_modified: list[str] | None = None,
    ) -> None:
        """Update a subtask's status.

        Args:
            task_id: ID of the subtask to update.
            status: New status.
            notes: Optional notes about the change.
            files_modified: Optional list of files modified.
        """
        if task_id not in self.subtasks:
            raise KeyError(f"Subtask {task_id} not found")

        subtask = self.subtasks[task_id]
        old_status = subtask.status
        subtask.status = status

        now = datetime.now(timezone.utc).isoformat()

        if status == "in_progress" and not subtask.started_at:
            subtask.started_at = now
        elif status == "complete":
            subtask.completed_at = now

        if notes:
            subtask.notes = notes
        if files_modified:
            subtask.files_modified.extend(files_modified)

        self._add_audit(task_id, "status_change", from_status=old_status, to_status=status)

    def get_subtask(self, task_id: str) -> Subtask | None:
        """Get a subtask by ID."""
        return self.subtasks.get(task_id)

    def get_incomplete(self) -> list[Subtask]:
        """Get all incomplete subtasks."""
        return [st for st in self.subtasks.values() if st.status not in ("complete", "skipped")]

    def get_available(self) -> list[Subtask]:
        """Get subtasks that are ready to work on (pending with dependencies met)."""
        available = []
        for subtask in self.subtasks.values():
            if subtask.status != "pending":
                continue
            # Check if all dependencies are complete
            deps_met = all(
                self.subtasks.get(dep_id, Subtask(id="", name="")).status == "complete"
                for dep_id in subtask.dependencies
            )
            if deps_met:
                available.append(subtask)
        return available

    def is_complete(self) -> bool:
        """Check if all subtasks are complete (or skipped)."""
        if not self.subtasks:
            return self.main_task is None or self.main_task.status == "complete"
        return all(st.status in ("complete", "skipped") for st in self.subtasks.values())

    def mark_main_complete(self) -> None:
        """Mark the main task as complete."""
        if self.main_task:
            self.main_task.status = "complete"
            self._add_audit("main", "status_change", from_status="in_progress", to_status="complete")

    def add_decision(self, decision: str) -> None:
        """Add a key decision to the context."""
        self.context["key_decisions"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
        })

    def add_blocker(self, blocker: str, resolved: bool = False) -> None:
        """Add a blocker to the context."""
        self.context["blockers_encountered"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "blocker": blocker,
            "resolved": resolved,
        })

    def _add_audit(
        self,
        task_id: str,
        action: str,
        from_status: str | None = None,
        to_status: str | None = None,
        details: str | None = None,
    ) -> None:
        """Add an entry to the audit log."""
        self.audit_log.append(AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            details=details,
        ))

    def get_summary(self) -> str:
        """Get a human-readable summary of progress."""
        if not self.main_task:
            return "No task in progress."

        complete = [st for st in self.subtasks.values() if st.status == "complete"]
        in_progress = [st for st in self.subtasks.values() if st.status == "in_progress"]
        pending = [st for st in self.subtasks.values() if st.status == "pending"]
        blocked = [st for st in self.subtasks.values() if st.status == "blocked"]

        lines = [
            f"## Task Progress: {self.main_task.description}",
            f"**Status:** {self.main_task.status}",
            f"**Progress:** {len(complete)}/{len(self.subtasks)} subtasks complete",
            "",
        ]

        if complete:
            lines.append(f"**Completed ({len(complete)}):**")
            for st in complete:
                lines.append(f"- ✓ {st.name}")
            lines.append("")

        if in_progress:
            lines.append(f"**In Progress ({len(in_progress)}):**")
            for st in in_progress:
                lines.append(f"- ⚡ {st.name}")
            lines.append("")

        if pending:
            lines.append(f"**Pending ({len(pending)}):**")
            for st in pending:
                lines.append(f"- ○ {st.name}")
            lines.append("")

        if blocked:
            lines.append(f"**Blocked ({len(blocked)}):**")
            for st in blocked:
                lines.append(f"- ⚠ {st.name}: {st.notes}")
            lines.append("")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all progress and delete the file."""
        self.main_task = None
        self.subtasks.clear()
        self.audit_log.clear()
        self.context = {"key_decisions": [], "blockers_encountered": []}
        if self.file_path.exists():
            self.file_path.unlink()
