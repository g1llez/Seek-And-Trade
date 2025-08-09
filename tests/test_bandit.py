import numpy as np
import pytest

from orchestrator.policy_bandit import LinUCBBandit


def test_bandit_select_shape_validation():
    bandit = LinUCBBandit(actions=["a", "b"], alpha=0.5, feature_dim=3)
    with pytest.raises(ValueError):
        bandit.select(np.zeros((2, 1)))


def test_bandit_select_and_update_cycle():
    bandit = LinUCBBandit(actions=["a", "b"], alpha=0.1, feature_dim=2)
    x = np.zeros((2, 1))
    a = bandit.select(x)
    assert a in {"a", "b"}
    # Update should not raise and should keep shapes consistent
    bandit.update(a, x, reward=1.0)
    a2 = bandit.select(x)
    assert a2 in {"a", "b"}


