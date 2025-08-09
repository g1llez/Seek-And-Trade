from orchestrator.config_loader import load_config
from agents.risk import RiskGuard


def test_risk_guard_limits_ok(tmp_path):
    cfg = load_config("/app/config/config.json")
    rg = RiskGuard(cfg)
    status = rg.evaluate_proposed_trade(
        {
            "proposed_risk_pct": 0.05,
            "portfolio_risk_pct": 0.10,
            "sector_risk_pct": 0.10,
            "corr_cluster_risk_pct": 0.10,
            "underlying_risk_pct": 0.10,
        },
        portfolio_state=None,
    )
    assert status.allowed is True


def test_risk_guard_limits_violate_any():
    cfg = load_config("/app/config/config.json")
    rg = RiskGuard(cfg)
    status = rg.evaluate_proposed_trade(
        {
            "proposed_risk_pct": cfg.risk.max_per_trade_pct + 0.01,
            "portfolio_risk_pct": 0.10,
            "sector_risk_pct": 0.10,
            "corr_cluster_risk_pct": 0.10,
            "underlying_risk_pct": 0.10,
        },
        portfolio_state=None,
    )
    assert status.allowed is False
    assert "proposed_risk_pct" in status.reason


