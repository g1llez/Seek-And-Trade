from dataclasses import dataclass
from typing import Any

@dataclass
class LiquidityStatus:
    tradable: bool
    reason: str

class LiquidityAgent:
    def __init__(self, config: Any) -> None:
        self.config = config
    def check_option_chain(self, chain_snapshot: Any) -> LiquidityStatus:
        raise NotImplementedError
