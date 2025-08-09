import os
import sys
from typing import List
import numpy as np
from orchestrator.config_loader import load_config, MissingConfigError
from orchestrator.policy_bandit import LinUCBBandit


class Seeker:
    def __init__(self, actions: list[str], alpha: float, feature_dim: int) -> None:
        self.bandit = LinUCBBandit(actions=actions, alpha=alpha, feature_dim=feature_dim)

    def choose_strategy(self, features: "np.ndarray") -> str:
        return self.bandit.select(features)


def main() -> int:
    # Chemin de config obligatoire: pas de valeurs de repli
    config_path = os.environ.get("CONFIG_PATH")
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    if not config_path:
        print("ERROR: Missing CONFIG_PATH or argv[1]", file=sys.stderr)
        return 1
    try:
        cfg = load_config(config_path)
    except MissingConfigError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: invalid config: {e}", file=sys.stderr)
        return 3
    # Seeker (bandit LinUCB) — démo
    actions: List[str] = cfg.strategies.enabled
    seeker = Seeker(actions=actions, alpha=cfg.bandit.alpha, feature_dim=cfg.bandit.feature_dim)
    x = np.zeros((cfg.bandit.feature_dim, 1))  # features fictives
    chosen = seeker.choose_strategy(x)
    print(f"Config loaded; Seeker ready; chosen action for demo: {chosen}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
