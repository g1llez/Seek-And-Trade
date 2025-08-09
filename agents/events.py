from dataclasses import dataclass
from typing import Any

@dataclass
class EventStatus:
    allowed: bool
    reason: str

class EventAgent:
    def __init__(self, config: Any) -> None:
        self.config = config
    def evaluate_open_window(self, symbol: str, calendar: Any) -> EventStatus:
        raise NotImplementedError
