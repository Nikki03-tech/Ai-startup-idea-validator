"""Planning Tool

Task planning and execution tracking utility for agent orchestration.
"""

from typing import List, Dict, Any


def create_execution_plan(tasks: List[str] | Dict[str, Any]) -> List[Dict[str, Any]]:
    """Formats task input into executable pipeline dictionaries."""
    if isinstance(tasks, list):
        return [{"task": task, "status": "pending"} for task in tasks]

    return tasks.get("tasks", [])