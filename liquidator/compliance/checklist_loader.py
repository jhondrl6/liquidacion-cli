"""
Carga el checklist legal desde JSON y convierte cada regla
en un objeto Rule ejecutable.
"""

import json
from pathlib import Path

from .rule_evaluator import RuleEvaluator


class ChecklistLoader:
    """Load & parse legal-compliance checklist."""

    def __init__(self, checklist_path: Path | None = None):
        # Default to the checklist in params if no path provided
        if checklist_path is None:
            from liquidator.params.params_loader import ParamsLoader
            params_loader = ParamsLoader()
            self.path = Path(params_loader.params_dir) / "checklist.json"
        else:
            self.path = Path(checklist_path)

    def load(self) -> list[dict]:
        """Return list of rule-dicts with an `evaluator: Callable` key."""
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        rules = []
        for rule_meta in raw["rules"]:
            rule_id = rule_meta["id"]
            evaluator = RuleEvaluator.build(rule_id, rule_meta)
            rules.append({**rule_meta, "evaluator": evaluator})
        return rules
