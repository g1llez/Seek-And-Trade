from __future__ import annotations

import os
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from orchestrator.config_loader import load_config, MissingConfigError
from orchestrator.policy_bandit import LinUCBBandit
from orchestrator.logging_utils import append_jsonl
from orchestrator.confidence import ConfidenceInput, compute_confidence
from agents.risk import RiskGuard
from agents.liquidity import LiquidityGuard
from agents.events import EventGuard
from agents.fx import FxGuard


class RiskInputs(BaseModel):
    proposed_risk_pct: float
    portfolio_risk_pct: float
    sector_risk_pct: float
    corr_cluster_risk_pct: float
    underlying_risk_pct: float


class LiquidityInputs(BaseModel):
    leg_spread: float
    open_interest: int
    chain_volume: int


class EventInputs(BaseModel):
    macro_buffer_days: float
    earnings_buffer_days: float


class FxInputs(BaseModel):
    slippage_pips: float


class DecisionRequest(BaseModel):
    features: list[float] = Field(min_length=1)
    # Confiance: toutes les valeurs sont requises (règle stricte, pas de fallback)
    dte: int
    short_delta: float
    distance_atr: float
    ivr_norm: float
    theta_captured: float
    event_buffer: float
    gamma_risk: float
    # Vetos (toutes requises; sinon 422 par validation Pydantic)
    risk: RiskInputs
    liquidity: LiquidityInputs
    events: EventInputs
    fx: FxInputs

class RiskEvalRequest(BaseModel):
    proposed_risk_pct: float
    portfolio_risk_pct: float
    sector_risk_pct: float
    corr_cluster_risk_pct: float
    underlying_risk_pct: float


class SeekerAPI:
    def __init__(self, config_path: str) -> None:
        self.cfg = load_config(config_path)
        self.actions: List[str] = self.cfg.strategies.enabled
        self.bandit = LinUCBBandit(
            actions=self.actions,
            alpha=self.cfg.bandit.alpha,
            feature_dim=self.cfg.bandit.feature_dim,
        )
        self.data_dir = Path("/app/data")
        self.decisions_file = self.data_dir / "decisions.jsonl"

    def choose(self, features: np.ndarray) -> str:
        return self.bandit.select(features)


def create_app(config_path: str) -> FastAPI:
    api = SeekerAPI(config_path)
    app = FastAPI(title="Seek and Trade — Seeker API")
    risk_guard = RiskGuard(api.cfg)
    liquidity_guard = LiquidityGuard(api.cfg)
    event_guard = EventGuard(api.cfg)
    fx_guard = FxGuard(api.cfg)
    # UI static (dark) served at /ui
    app.mount("/ui", StaticFiles(directory="/app/ui", html=True), name="ui")

    @app.get("/")
    def root_index() -> FileResponse:
        return FileResponse("/app/ui/index.html")

    @app.get("/index.html")
    def root_index_html() -> FileResponse:
        return FileResponse("/app/ui/index.html")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "actions": api.actions, "feature_dim": api.cfg.bandit.feature_dim}

    @app.post("/decision")
    def decision(req: DecisionRequest) -> dict:
        try:
            x = np.array(req.features, dtype=float).reshape(-1, 1)
            if x.shape[0] != api.cfg.bandit.feature_dim:
                raise HTTPException(status_code=400, detail=f"features must have length {api.cfg.bandit.feature_dim}")
            # Vetos stricts: aucune valeur par défaut; les entrées sont requises au schéma
            risk_status = risk_guard.evaluate_proposed_trade(
                proposed={
                    "proposed_risk_pct": req.risk.proposed_risk_pct,
                    "portfolio_risk_pct": req.risk.portfolio_risk_pct,
                    "sector_risk_pct": req.risk.sector_risk_pct,
                    "corr_cluster_risk_pct": req.risk.corr_cluster_risk_pct,
                    "underlying_risk_pct": req.risk.underlying_risk_pct,
                },
                portfolio_state=None,
            )
            if not risk_status.allowed:
                raise HTTPException(status_code=400, detail=f"risk_veto:{risk_status.reason}")

            lq_status = liquidity_guard.evaluate(
                leg_spread=req.liquidity.leg_spread,
                open_interest=req.liquidity.open_interest,
                chain_volume=req.liquidity.chain_volume,
            )
            if not lq_status.allowed:
                raise HTTPException(status_code=400, detail=f"liquidity_veto:{lq_status.reason}")

            ev_status = event_guard.evaluate(
                macro_buffer_days=req.events.macro_buffer_days,
                earnings_buffer_days=req.events.earnings_buffer_days,
            )
            if not ev_status.allowed:
                raise HTTPException(status_code=400, detail=f"event_veto:{ev_status.reason}")

            fx_status = fx_guard.evaluate(slippage_pips=req.fx.slippage_pips)
            if not fx_status.allowed:
                raise HTTPException(status_code=400, detail=f"fx_veto:{fx_status.reason}")

            chosen = api.choose(x)
            # Confiance (champs requis)
            ci = ConfidenceInput(
                dte=req.dte,
                short_delta=req.short_delta,
                distance_atr=req.distance_atr,
                ivr_norm=req.ivr_norm,
                theta_captured=req.theta_captured,
                event_buffer=req.event_buffer,
                gamma_risk=req.gamma_risk,
            )
            conf = compute_confidence(ci)
            record = {
                "chosen": chosen,
                "features": req.features,
                "actions": api.actions,
                "confidence": {"score": conf.score, "components": conf.components},
            }
            append_jsonl(api.decisions_file, record)
            return record
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/risk/evaluate")
    def risk_evaluate(req: RiskEvalRequest) -> dict:
        status = risk_guard.evaluate_proposed_trade(
            proposed={
                "proposed_risk_pct": req.proposed_risk_pct,
                "portfolio_risk_pct": req.portfolio_risk_pct,
                "sector_risk_pct": req.sector_risk_pct,
                "corr_cluster_risk_pct": req.corr_cluster_risk_pct,
                "underlying_risk_pct": req.underlying_risk_pct,
            },
            portfolio_state=None,
        )
        return {"allowed": status.allowed, "reason": status.reason}

    @app.get("/history")
    def history(limit: int = 20) -> dict:
        path = api.decisions_file
        if not path.exists():
            return {"items": []}
        # Read last N lines efficiently
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        items = []
        for line in lines[-max(limit, 1):]:
            try:
                items.append(json.loads(line))
            except Exception:
                continue
        return {"items": items[::-1]}  # newest first

    return app


def app_factory() -> FastAPI:
    config_path = os.environ.get("CONFIG_PATH")
    if not config_path:
        raise RuntimeError("Missing CONFIG_PATH")
    return create_app(config_path)


