from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from orchestrator.api import create_app


def test_health_and_decision():
    # Use the config baked in the image path; when running in container, it's /app/config/config.json
    app = create_app("/app/config/config.json")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body and body["status"] == "ok"

    payload = {
        "features": [0.0] * body["feature_dim"],
        "dte": 45,
        "short_delta": 0.12,
        "distance_atr": 1.5,
        "ivr_norm": 0.6,
        "theta_captured": 0.0,
        "event_buffer": 1.0,
        "gamma_risk": 0.2,
    }
    r2 = client.post("/decision", json=payload)
    assert r2.status_code == 200
    out = r2.json()
    assert out["chosen"] in out["actions"]


