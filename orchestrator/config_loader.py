from __future__ import annotations
import json
from pathlib import Path
from dataclasses import asdict
from typing import Union

from orchestrator.config_types import (
    AppConfig,
    RiskConfig,
    LiquidityConfig,
    EventsConfig,
    FxConfig,
    StrategiesConfig,
    BanditConfig,
    IBConfig,
)

class MissingConfigError(Exception):
    pass

REQUIRED_NUMERIC = [
    ("risk", "max_per_trade_pct"),
    ("risk", "max_portfolio_pct"),
    ("risk", "max_sector_pct"),
    ("risk", "max_corr_cluster_pct"),
    ("risk", "max_per_underlying_pct"),
    ("liquidity", "max_leg_spread"),
    ("liquidity", "min_open_interest"),
    ("liquidity", "min_chain_volume"),
    ("events", "macro_buffer_days"),
    ("events", "earnings_buffer_days"),
    ("fx", "max_slippage_pips"),
    ("bandit", "alpha"),
    ("bandit", "feature_dim"),
]

ALLOWED_STRATEGIES = {
    "credit_spread",
    "iron_condor",
    "diagonal",
    "iron_fly",
    "broken_wing_butterfly",
}

def load_config(path: Union[str, Path]) -> AppConfig:
    p = Path(path)
    data = json.loads(p.read_text())

    for section, key in REQUIRED_NUMERIC:
        if data.get(section, {}).get(key, None) is None:
            raise MissingConfigError(f"Missing required config: {section}.{key}")

    enabled = data.get("strategies", {}).get("enabled", [])
    if not enabled or any(s not in ALLOWED_STRATEGIES for s in enabled):
        raise MissingConfigError("Invalid strategies.enabled")

    # IB config required
    ib_cfg = data.get("ib")
    if not ib_cfg or not all(k in ib_cfg for k in ("host", "port", "client_id", "paper")):
        raise MissingConfigError("Missing required config: ib.{host,port,client_id,paper}")

    return AppConfig(
        risk=RiskConfig(**data["risk"]),
        liquidity=LiquidityConfig(**data["liquidity"]),
        events=EventsConfig(**data["events"]),
        fx=FxConfig(**data["fx"]),
        strategies=StrategiesConfig(enabled=enabled),
        bandit=BanditConfig(**data["bandit"]),
        ib=IBConfig(**ib_cfg),
    )
