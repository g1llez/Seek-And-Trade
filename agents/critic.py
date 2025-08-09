from dataclasses import dataclass
from typing import Any, List

@dataclass
class Critique:
    name: str
    score: float
    reason: str

class StrategyCritic:
    def __init__(self, config: Any) -> None:
        self.config = config
    def stress_and_score(self, candidates: List[Any], context: Any) -> List[Critique]:
        raise NotImplementedError
