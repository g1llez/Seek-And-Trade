from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LiquidityStatus:
    allowed: bool
    reason: str


class LiquidityGuard:
    def __init__(self, config: Any) -> None:
        self.config = config

    def evaluate(self, *, leg_spread: float, open_interest: int, chain_volume: int) -> LiquidityStatus:
        lq = self.config.liquidity
        checks = [
            (leg_spread <= lq.max_leg_spread, f"leg_spread>{lq.max_leg_spread}"),
            (open_interest >= lq.min_open_interest, f"open_interest<{lq.min_open_interest}"),
            (chain_volume >= lq.min_chain_volume, f"chain_volume<{lq.min_chain_volume}"),
        ]
        for ok, reason in checks:
            if not ok:
                return LiquidityStatus(False, reason)
        return LiquidityStatus(True, "ok")
