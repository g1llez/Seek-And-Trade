from dataclasses import dataclass
from typing import Any

@dataclass
class FxDecision:
    allowed: bool
    reason: str
    venue: str  # 'US' or 'CA'

class FxRouter:
    def __init__(self, config: Any) -> None:
        self.config = config
    def choose_venue(self, candidates: Any, fx_quotes: Any) -> FxDecision:
        raise NotImplementedError
