from dataclasses import dataclass
from typing import Any

@dataclass
class ExecutionResult:
    accepted: bool
    reason: str
    order_id: str | None

class ExecutionAgent:
    def __init__(self, config: Any) -> None:
        self.config = config
    def place_multi_leg(self, symbol: str, legs: Any, limits: Any) -> ExecutionResult:
        raise NotImplementedError
