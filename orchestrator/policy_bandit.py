from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class BanditState:
    A: Dict[str, np.ndarray]
    b: Dict[str, np.ndarray]


class LinUCBBandit:
    """Simple contextual LinUCB bandit for strategy selection.

    actions: list of strategy names
    alpha: exploration parameter (>0)
    feature_dim: number of contextual features (must match x shape)
    """

    def __init__(self, actions: List[str], alpha: float, feature_dim: int) -> None:
        if feature_dim <= 0:
            raise ValueError("feature_dim must be > 0")
        if not actions:
            raise ValueError("actions must be non-empty")
        self.actions = list(actions)
        self.alpha = float(alpha)
        self.d = int(feature_dim)
        self.state = BanditState(
            A={a: np.eye(self.d) for a in self.actions},
            b={a: np.zeros((self.d, 1)) for a in self.actions},
        )

    def _theta(self, a: str) -> np.ndarray:
        A = self.state.A[a]
        b = self.state.b[a]
        # Solve A theta = b (A is positive definite)
        theta = np.linalg.solve(A, b)
        return theta

    def select(self, x: np.ndarray) -> str:
        """Pick the action with largest UCB score for context x (shape (d,1))."""
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        if x.shape != (self.d, 1):
            raise ValueError(f"features shape must be ({self.d},1), got {x.shape}")
        best_action = None
        best_score = -np.inf
        for a in self.actions:
            A = self.state.A[a]
            theta = self._theta(a)
            mean = float(theta.T @ x)
            # variance term: x^T A^{-1} x using solve for stability
            var = float(x.T @ np.linalg.solve(A, x))
            ucb = mean + self.alpha * np.sqrt(max(var, 0.0))
            if ucb > best_score:
                best_score = ucb
                best_action = a
        assert best_action is not None
        return best_action

    def update(self, a: str, x: np.ndarray, reward: float) -> None:
        if a not in self.actions:
            raise KeyError(f"unknown action {a}")
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        if x.shape != (self.d, 1):
            raise ValueError(f"features shape must be ({self.d},1), got {x.shape}")
        self.state.A[a] = self.state.A[a] + (x @ x.T)
        self.state.b[a] = self.state.b[a] + (float(reward) * x)


