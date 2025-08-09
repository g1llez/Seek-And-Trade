from typing import Any

class PostTradeAnalyst:
    def __init__(self) -> None:
        ...
    def log_decision(self, decision_snapshot: Any) -> None:
        raise NotImplementedError
    def log_outcome(self, outcome_snapshot: Any) -> None:
        raise NotImplementedError
