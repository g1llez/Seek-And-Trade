from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ConfidenceInput:
    dte: int
    short_delta: float
    distance_atr: float
    ivr_norm: float
    theta_captured: float
    event_buffer: float
    gamma_risk: float


@dataclass
class ConfidenceResult:
    score: float  # 0..100
    components: Dict[str, float]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def compute_confidence(ci: ConfidenceInput) -> ConfidenceResult:
    # Weights (initial, simple)
    w_t = 0.35
    w_delta = 0.20
    w_dist = 0.15
    w_ivr = 0.10
    w_pnl = 0.10
    w_evt = 0.10
    w_gamma = 0.10

    # Components normalized 0..1
    g_time = (ci.dte if ci.dte > 0 else 0) / 45.0
    g_time = g_time ** 0.5  # concave, more weight early
    g_time = clamp(g_time, 0.0, 1.0)

    f_delta = clamp((0.30 - ci.short_delta) / 0.30, 0.0, 1.0)
    f_dist = clamp(ci.distance_atr / 2.0, 0.0, 1.0)  # saturate at 2x ATR
    f_ivr = clamp(ci.ivr_norm, 0.0, 1.0)
    f_pnl = clamp(ci.theta_captured, 0.0, 1.0)
    f_evt = clamp(ci.event_buffer, 0.0, 1.0)
    f_gamma = clamp(ci.gamma_risk, 0.0, 1.0)

    raw = (
        w_t * g_time
        + w_delta * f_delta
        + w_dist * f_dist
        + w_ivr * f_ivr
        + w_pnl * f_pnl
        + w_evt * f_evt
        - w_gamma * f_gamma
    )
    score = clamp(100.0 * raw, 0.0, 100.0)
    return ConfidenceResult(
        score=score,
        components={
            "time": g_time,
            "delta": f_delta,
            "distance_atr": f_dist,
            "ivr": f_ivr,
            "theta": f_pnl,
            "event_buffer": f_evt,
            "gamma": f_gamma,
        },
    )


