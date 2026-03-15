"""
Self-Reflection Module — Learn from successes and failures.

CRADLE/Reflexion pattern: after each action, record what happened.
Before similar actions, retrieve past reflections to avoid repeating mistakes.

Game-agnostic: works with any task/workflow system.
"""
import json
import os
import time


class ReflectionLog:
    """Persistent failure analysis and learning system."""

    def __init__(self, filepath: str = "reflections.json",
                 max_entries: int = 200, log_fn=None):
        self.filepath = filepath
        self.max_entries = max_entries
        self.log = log_fn or print
        self.entries = self._load()

    def _load(self) -> list:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self):
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        with open(self.filepath, "w") as f:
            json.dump(self.entries, f, indent=2)

    def record_success(self, task: str, details: dict = None):
        self.entries.append({
            "type": "success",
            "task": task,
            "details": details or {},
            "time": time.time(),
        })
        self._save()

    def record_failure(self, task: str, error: str, analysis: str,
                       fix_applied: str = "", details: dict = None):
        self.entries.append({
            "type": "failure",
            "task": task,
            "error": error,
            "analysis": analysis,
            "fix_applied": fix_applied,
            "details": details or {},
            "time": time.time(),
        })
        self._save()
        self.log(f"REFLECT: {task} failed — {analysis}")

    def get_reflections_for(self, task: str, limit: int = 5) -> list:
        """Retrieve recent failures relevant to a task."""
        task_type = task.split(":")[0] if ":" in task else task
        task_target = task.split(":", 1)[1] if ":" in task else ""

        relevant = []
        for entry in reversed(self.entries):
            if entry["type"] != "failure":
                continue
            e_type = entry["task"].split(":")[0] if ":" in entry["task"] else entry["task"]
            e_target = entry["task"].split(":", 1)[1] if ":" in entry["task"] else ""
            if e_type == task_type or e_target == task_target:
                relevant.append(entry)
                if len(relevant) >= limit:
                    break
        return relevant

    def success_rate(self, task_type: str, window: int = 20) -> float:
        relevant = [e for e in self.entries[-100:]
                     if e["task"].startswith(task_type)][-window:]
        if not relevant:
            return 0.5
        successes = sum(1 for e in relevant if e["type"] == "success")
        return successes / len(relevant)

    def get_stats(self) -> dict:
        total = len(self.entries)
        successes = sum(1 for e in self.entries if e["type"] == "success")
        return {
            "total": total,
            "successes": successes,
            "failures": total - successes,
            "rate": f"{successes/total*100:.0f}%" if total > 0 else "n/a",
        }
