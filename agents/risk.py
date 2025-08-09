from dataclasses import dataclass
from typing import Any

@dataclass
class RiskStatus:
    allowed: bool
    reason: str

class RiskGuard:
    def __init__(self, config: Any) -> None:
        self.config = config
    def evaluate_portfolio_limits(self, portfolio_state: Any) -> RiskStatus:
        # Placeholder: Always true until portfolio_state model is defined
        return RiskStatus(True, "ok")
    def evaluate_proposed_trade(self, proposed: Any, portfolio_state: Any) -> RiskStatus:
        # Strict rule checks using config; no fallback values
        r = self.config.risk
        p = proposed
        checks = [
            (p["proposed_risk_pct"] <= r.max_per_trade_pct, f"proposed_risk_pct>{r.max_per_trade_pct}"),
            (p["portfolio_risk_pct"] <= r.max_portfolio_pct, f"portfolio_risk_pct>{r.max_portfolio_pct}"),
            (p["sector_risk_pct"] <= r.max_sector_pct, f"sector_risk_pct>{r.max_sector_pct}"),
            (p["corr_cluster_risk_pct"] <= r.max_corr_cluster_pct, f"corr_cluster_risk_pct>{r.max_corr_cluster_pct}"),
            (p["underlying_risk_pct"] <= r.max_per_underlying_pct, f"underlying_risk_pct>{r.max_per_underlying_pct}"),
        ]
        for ok, reason in checks:
            if not ok:
                return RiskStatus(False, reason)
        return RiskStatus(True, "ok")
