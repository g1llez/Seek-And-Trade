from orchestrator.confidence import ConfidenceInput, compute_confidence


def test_confidence_basic_monotonicity():
    ci_lo = ConfidenceInput(
        dte=10,
        short_delta=0.25,
        distance_atr=0.5,
        ivr_norm=0.3,
        theta_captured=0.0,
        event_buffer=0.0,
        gamma_risk=0.5,
    )
    ci_hi = ConfidenceInput(
        dte=45,
        short_delta=0.10,
        distance_atr=2.0,
        ivr_norm=0.8,
        theta_captured=0.5,
        event_buffer=1.0,
        gamma_risk=0.1,
    )
    r1 = compute_confidence(ci_lo)
    r2 = compute_confidence(ci_hi)
    assert r2.score >= r1.score


