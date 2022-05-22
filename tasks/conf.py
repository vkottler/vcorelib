"""
A module for project-specific task registration.
"""

# built-in
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.target.resolver import TargetResolver
from vcorelib.task.manager import TaskManager


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    # Ensure that the task manager can't resolve the virtual environment
    # target.
    del manager.tasks["venv"]
    del manager.dependencies["venv"]
    manager.resolver = TargetResolver()

    del project
    del cwd
    del substitutions
    return True
