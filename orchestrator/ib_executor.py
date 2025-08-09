from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from orchestrator.config_types import IBConfig


@dataclass
class IbHealth:
    ok: bool
    reason: Optional[str] = None


class IbExecutor:
    def __init__(self, cfg: IBConfig) -> None:
        self.cfg = cfg

    def check_health(self, timeout: float = 2.0) -> IbHealth:
        try:
            # Lazy import so unit tests can monkeypatch cleanly without package installed
            from ib_insync import IB  # type: ignore
        except Exception as e:  # pragma: no cover
            return IbHealth(ok=False, reason=f"import_error:{e}")

        ib = IB()
        try:
            ib.connect(self.cfg.host, int(self.cfg.port), clientId=int(self.cfg.client_id), timeout=timeout)
            if not ib.isConnected():
                return IbHealth(ok=False, reason="not_connected")
            # In paper mode, TWS/Gateway should be started with paper settings; we just validate link
            return IbHealth(ok=True)
        except Exception as e:
            return IbHealth(ok=False, reason=str(e))
        finally:
            try:
                if ib.isConnected():
                    ib.disconnect()
            except Exception:
                pass


