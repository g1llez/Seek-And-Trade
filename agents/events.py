from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EventStatus:
    allowed: bool
    reason: str


class EventGuard:
    def __init__(self, config: Any) -> None:
        self.config = config

    def evaluate(self, *, macro_buffer_days: float, earnings_buffer_days: float) -> EventStatus:
        ev = self.config.events
        checks = [
            (macro_buffer_days >= ev.macro_buffer_days, f"macro_buffer<{ev.macro_buffer_days}"),
            (earnings_buffer_days >= ev.earnings_buffer_days, f"earnings_buffer<{ev.earnings_buffer_days}"),
        ]
        for ok, reason in checks:
            if not ok:
                return EventStatus(False, reason)
        return EventStatus(True, "ok")

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
