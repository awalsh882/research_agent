"""Hook for automatic task plan creation on user prompt submission.

This hook analyzes incoming prompts and creates initial task plans for
multi-step requests, firing BEFORE the agent starts processing.

Usage:
    hook = TaskPlanningHook()
    analysis = hook.analyze_prompt("Compare DocuSign vs Adobe Sign")
    if analysis.should_plan:
        await hook.execute(query, preserve_existing=True)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from research_agent.tasks import TaskProgress


@dataclass
class PlanningAnalysis:
    """Result of analyzing a prompt for planning needs."""

    should_plan: bool
    reason: str
    suggested_tasks: list[str] = field(default_factory=list)


class TaskPlanningHook:
    """Hook that analyzes prompts and creates initial task plans.

    Uses heuristics to detect multi-step requests:
    - Enumeration patterns (1., 2., bullet points)
    - Sequence words (first, then, next, finally)
    - Multiple action verbs (analyze, compare, research)
    - Explicit planning phrases (step by step, break down)
    - Comparison requests (vs, compare X to Y)
    """

    # Patterns indicating multi-step work
    ENUMERATION_PATTERN = re.compile(r"(?:^|\n)\s*(?:\d+[.)]|\*|-)\s+", re.MULTILINE)

    SEQUENCE_WORDS = {"first", "then", "next", "finally", "after", "before", "step"}

    ACTION_VERBS = {
        "analyze",
        "compare",
        "research",
        "create",
        "generate",
        "build",
        "write",
        "summarize",
        "investigate",
        "review",
        "evaluate",
        "assess",
        "examine",
    }

    EXPLICIT_PLAN_PHRASES = [
        "create a plan",
        "break down",
        "step by step",
        "multiple steps",
        "list of tasks",
        "in order to",
    ]

    def __init__(self, min_prompt_length: int = 100):
        """Initialize the hook.

        Args:
            min_prompt_length: Minimum prompt length for length-based heuristic.
        """
        self._min_prompt_length = min_prompt_length

    def analyze_prompt(self, prompt: str) -> PlanningAnalysis:
        """Analyze whether a prompt warrants automatic task planning.

        Args:
            prompt: The user's input prompt.

        Returns:
            PlanningAnalysis with should_plan flag and reasoning.
        """
        prompt_lower = prompt.lower()
        words = set(prompt_lower.split())
        reasons: list[str] = []
        suggested: list[str] = []

        # Check for explicit planning requests
        for phrase in self.EXPLICIT_PLAN_PHRASES:
            if phrase in prompt_lower:
                reasons.append(f"explicit planning request: '{phrase}'")

        # Check for enumeration patterns
        if self.ENUMERATION_PATTERN.search(prompt):
            reasons.append("contains enumerated items")

        # Check for sequence words (need 2+ for planning)
        found_seq = self.SEQUENCE_WORDS & words
        if len(found_seq) >= 2:
            reasons.append(f"sequence words: {sorted(found_seq)}")

        # Check for multiple action verbs
        found_verbs = self.ACTION_VERBS & words
        if len(found_verbs) >= 2:
            reasons.append(f"multiple actions: {sorted(found_verbs)}")
            suggested.extend([f"{v.title()} task" for v in sorted(found_verbs)])

        # Check for comparison requests
        if " vs " in prompt_lower or " versus " in prompt_lower:
            reasons.append("comparison request (vs)")
        elif "compare" in prompt_lower and " to " in prompt_lower:
            reasons.append("comparison request (compare...to)")

        # Length-based heuristic for complex requests
        if len(prompt) > self._min_prompt_length and "," in prompt:
            # Count clauses by commas and conjunctions
            clause_indicators = prompt_lower.count(",") + prompt_lower.count(" and ")
            if clause_indicators >= 2:
                reasons.append("long prompt with multiple clauses")

        should_plan = len(reasons) >= 1
        return PlanningAnalysis(
            should_plan=should_plan,
            reason="; ".join(reasons) if reasons else "simple request",
            suggested_tasks=suggested,
        )

    async def execute(self, query: str, preserve_existing: bool = True) -> bool:
        """Execute the hook - create task plan if needed.

        Args:
            query: The user's prompt.
            preserve_existing: If True, append to existing tasks rather than replace.

        Returns:
            True if a task plan was created/modified, False otherwise.
        """
        analysis = self.analyze_prompt(query)

        if not analysis.should_plan:
            return False

        progress = TaskProgress.load()

        # Determine starting task number
        existing_count = len(progress.subtasks)

        if preserve_existing and existing_count > 0:
            # Don't clear existing tasks, just set main task if not set
            if not progress.main_task:
                # Truncate query to reasonable length for main task
                main_desc = query[:100] + "..." if len(query) > 100 else query
                progress.set_main_task(main_desc, status="in_progress")
        else:
            # Fresh start for new task
            main_desc = query[:100] + "..." if len(query) > 100 else query
            progress.set_main_task(main_desc, status="in_progress")

        # Add suggested subtasks if we have them
        for i, task in enumerate(analysis.suggested_tasks, start=existing_count + 1):
            progress.add_subtask(f"t{i}", task)

        progress.save()
        return True
