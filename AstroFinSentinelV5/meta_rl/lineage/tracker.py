"""meta_rl/lineage/tracker.py -- Strategy lineage tracking"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import json

@dataclass
class LineageNode:
    strategy_id: str
    parent_ids: tuple[str, ...]
    generation: int
    created_at: str
    metrics: dict
    source: str  # "crossover", "mutation", "seed"

class LineageTracker:
    def __init__(self, storage_path: str = "data/meta_rl/lineage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.nodes: dict[str, LineageNode] = {}
        self._load()

    def _load(self):
        fp = os.path.join(self.storage_path, "lineage.json")
        if os.path.exists(fp):
            data = json.loads(open(fp).read())
            self.nodes = {k: LineageNode(**v) for k, v in data.items()}

    def _save(self):
        fp = os.path.join(self.storage_path, "lineage.json")
        open(fp, "w").write(json.dumps({k: vars(v) for k, v in self.nodes.items()}, indent=2))

    def add(self, strategy_id: str, parent_ids: tuple, generation: int, metrics: dict, source: str = "seed"):
        self.nodes[strategy_id] = LineageNode(
            strategy_id=strategy_id,
            parent_ids=parent_ids,
            generation=generation,
            created_at=datetime.utcnow().isoformat(),
            metrics=metrics,
            source=source
        )
        self._save()

    def get_ancestry(self, strategy_id: str) -> list[LineageNode]:
        result = []
        seen = set()
        queue = [strategy_id]
        while queue:
            sid = queue.pop(0)
            if sid in seen or sid not in self.nodes:
                continue
            seen.add(sid)
            node = self.nodes[sid]
            result.append(node)
            queue.extend(list(node.parent_ids))
        return result

    def get_depth(self, strategy_id: str) -> int:
        ancestry = self.get_ancestry(strategy_id)
        return max((n.generation for n in ancestry), default=0)

    def prune(self, min_fitness: float):
        to_remove = [k for k, v in self.nodes.items() if v.metrics.get("fitness", -999) < min_fitness]
        for k in to_remove:
            del self.nodes[k]
        self._save()
        return len(to_remove)
