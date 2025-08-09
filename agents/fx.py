from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FxStatus:
    allowed: bool
    reason: str


class FxGuard:
    def __init__(self, config: Any) -> None:
        self.config = config

    def evaluate(self, *, slippage_pips: float) -> FxStatus:
        fx = self.config.fx
        if slippage_pips > fx.max_slippage_pips:
            return FxStatus(False, f"fx_slippage>{fx.max_slippage_pips}")
        return FxStatus(True, "ok")

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
