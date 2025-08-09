from dataclasses import dataclass
from typing import Optional, List

@dataclass
class RiskConfig:
    max_per_trade_pct: float
    max_portfolio_pct: float
    max_sector_pct: float
    max_corr_cluster_pct: float
    max_per_underlying_pct: float

@dataclass
class LiquidityConfig:
    max_leg_spread: float
    min_open_interest: int
    min_chain_volume: int

@dataclass
class EventsConfig:
    macro_buffer_days: int
    earnings_buffer_days: int

@dataclass
class FxConfig:
    max_slippage_pips: float

@dataclass
class StrategiesConfig:
    enabled: List[str]

@dataclass
class BanditConfig:
    alpha: float
    feature_dim: int

@dataclass
class AppConfig:
    risk: RiskConfig
    liquidity: LiquidityConfig
    events: EventsConfig
    fx: FxConfig
    strategies: StrategiesConfig
    bandit: BanditConfig
    ib: 'IBConfig'

@dataclass
class IBConfig:
    host: str
    port: int
    client_id: int
    paper: bool
