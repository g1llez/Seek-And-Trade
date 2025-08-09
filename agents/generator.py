from dataclasses import dataclass
from typing import Any, List

@dataclass
class StrategyCandidate:
    name: str
    params: dict
    score: float

class StrategyGenerator:
    def __init__(self, config: Any) -> None:
        self.config = config
    def propose(self, features: Any) -> List[StrategyCandidate]:
        raise NotImplementedError
