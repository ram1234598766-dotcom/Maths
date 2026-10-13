"""Gradient-Memory Transport (GMT), a proposed mathematical model.

The module uses an oriented incidence matrix for a finite undirected graph.
It is a research prototype, not a validated physical law.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class GMTParameters:
    """Parameters; theta has units of state squared."""
    tau: float = 0.8
    theta: float = 0.25
    g_min: float = 0.2
    g_max: float = 1.5

    def __post_init__(self) -> None:
        if not np.isfinite(self.tau) or self.tau <= 0:
            raise ValueError("tau must be finite and positive")
        if not np.isfinite(self.theta) or self.theta <= 0:
            raise ValueError("theta must be finite and positive")
        if not np.isfinite(self.g_min) or self.g_min <= 0:
            raise ValueError("g_min must be finite and positive")
        if not np.isfinite(self.g_max) or self.g_max < self.g_min:
            raise ValueError("g_max must be finite and at least g_min")


def incidence_matrix(n_nodes: int, edges: Iterable[tuple[int, int]]) -> FloatArray:
    """Return B (m x n); each row has -1 at i and +1 at j."""
    if not isinstance(n_nodes, int) or n_nodes < 1:
        raise ValueError("n_nodes must be a positive integer")
    edge_list = list(edges)
    B = np.zeros((len(edge_list), n_nodes), dtype=float)
    seen: set[tuple[int, int]] = set()
    for k, edge in enumerate(edge_list):
        if len(edge) != 2:
            raise ValueError("each edge must contain exactly two node indices")
        i, j = edge
        if not (isinstance(i, (int, np.integer)) and isinstance(j, (int, np.integer))):
            raise ValueError(f"edge indices must be integers: {edge}")
        if i == j or i < 0 or j < 0 or i >= n_nodes or j >= n_nodes:
            raise ValueError(f"invalid edge {(i, j)} for {n_nodes} nodes")
        key = (min(i, j), max(i, j))
        if key in seen:
            raise ValueError(f"duplicate undirected edge {key}")
        seen.add(key)
        B[k, i] = -1.0
        B[k, j] = 1.0
    return B


def path_edges(n: int) -> list[tuple[int, int]]:
    if n < 1:
        raise ValueError("n must be positive")
    return [(i, i + 1) for i in range(n - 1)]


def cycle_edges(n: int) -> list[tuple[int, int]]:
    if n < 3:
        raise ValueError("a simple cycle needs at least 3 nodes")
    return [(i, (i + 1) % n) for i in range(n)]


def complete_edges(n: int) -> list[tuple[int, int]]:
    if n < 1:
        raise ValueError("n must be positive")
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def validate_state(u: Sequence[float], a: Sequence[float], B: FloatArray,
                   capacities: Sequence[float]) -> tuple[FloatArray, FloatArray, FloatArray]:
    u_arr = np.asarray(u, dtype=float)
    a_arr = np.asarray(a, dtype=float)
    c_arr = np.asarray(capacities, dtype=float)
    if B.ndim != 2:
        raise ValueError("B must be a 2D incidence matrix")
    if u_arr.shape != (B.shape[1],):
        raise ValueError("u shape must match the node count")
    if a_arr.shape != (B.shape[0],):
        raise ValueError("a shape must match the edge count")
    if c_arr.shape != (B.shape[1],):
        raise ValueError("capacities shape must match the node count")
    if not (np.all(np.isfinite(u_arr)) and np.all(np.isfinite(a_arr)) and np.all(np.isfinite(c_arr))):
        raise ValueError("state and capacities must be finite")
    if np.any(c_arr <= 0):
        raise ValueError("all node capacities must be positive")
    if np.any(a_arr < 0) or np.any(a_arr > 1):
        raise ValueError("memory state a must lie in [0, 1]")
    return u_arr, a_arr, c_arr


def response(du: FloatArray, theta: float) -> FloatArray:
    """Bounded response r = du^2/(theta + du^2)."""
    square = np.square(du)
    return square / (theta + square)


def conductances(a: Sequence[float], params: GMTParameters) -> FloatArray:
    a_arr = np.asarray(a, dtype=float)
    if np.any(~np.isfinite(a_arr)) or np.any(a_arr < 0) or np.any(a_arr > 1):
        raise ValueError("a must be finite and lie in [0, 1]")
    return params.g_min + (params.g_max - params.g_min) * a_arr


def rhs(_t: float, y: FloatArray, B: FloatArray, capacities: FloatArray,
        params: GMTParameters) -> FloatArray:
    n = B.shape[1]
    u, a = y[:n], y[n:]
    # Clip only during conductance evaluation to protect against roundoff drift.
    a_eval = np.clip(a, 0.0, 1.0)
    delta = B @ u
    g = conductances(a_eval, params)
    du_dt = -(B.T @ (g * delta)) / capacities
    da_dt = (response(delta, params.theta) - a) / params.tau
    return np.concatenate((du_dt, da_dt))


def simulate(B: FloatArray, u0: Sequence[float], a0: Sequence[float] | None = None,
             capacities: Sequence[float] | None = None,
             params: GMTParameters = GMTParameters(), t_end: float = 10.0,
             n_samples: int = 501, rtol: float = 1e-10,
             atol: float = 1e-12) -> dict[str, FloatArray]:
    """Integrate GMT with DOP853 and return sampled trajectories/observables."""
    B = np.asarray(B, dtype=float)
    if B.ndim != 2 or B.shape[1] < 1 or not np.all(np.isfinite(B)):
        raise ValueError("B must be a finite 2D matrix with at least one node")
    n, m = B.shape[1], B.shape[0]
    u0_arr = np.asarray(u0, dtype=float)
    a0_arr = np.zeros(m, dtype=float) if a0 is None else np.asarray(a0, dtype=float)
    c = np.ones(n, dtype=float) if capacities is None else np.asarray(capacities, dtype=float)
    u0_arr, a0_arr, c = validate_state(u0_arr, a0_arr, B, c)
    if t_end <= 0 or not np.isfinite(t_end):
        raise ValueError("t_end must be finite and positive")
    if not isinstance(n_samples, int) or n_samples < 2:
        raise ValueError("n_samples must be an integer >= 2")
    t_eval = np.linspace(0.0, float(t_end), n_samples)
    y0 = np.concatenate((u0_arr, a0_arr))
    sol = solve_ivp(rhs, (0.0, float(t_end)), y0, args=(B, c, params),
                    method="DOP853", t_eval=t_eval, rtol=rtol, atol=atol)
    if not sol.success:
        raise RuntimeError(f"integration failed: {sol.message}")
    u, a = sol.y[:n].T, sol.y[n:].T
    weighted_mean = (u0_arr @ c) / np.sum(c)
    deviation = u - weighted_mean
    energy = 0.5 * np.einsum("ti,i,ti->t", deviation, c, deviation)
    du = (B @ u.T).T
    g = params.g_min + (params.g_max - params.g_min) * np.clip(a, 0.0, 1.0)
    dissipation = np.sum(g * np.square(du), axis=1)
    mass = u @ c
    return {
        "t": sol.t, "u": u, "a": a,
        "mean": np.full_like(sol.t, weighted_mean),
        "energy": energy, "mass": mass,
        "edge_differences": du, "conductances": g,
        "dissipation": dissipation,
        "weighted_mean": np.array([weighted_mean]),
    }


def generalized_spectral_gap(B: FloatArray, capacities: Sequence[float]) -> float:
    """Return the graph's capacity-weighted nonzero spectral gap."""
    B = np.asarray(B, dtype=float)
    c = np.asarray(capacities, dtype=float)
    if B.ndim != 2 or c.shape != (B.shape[1],) or np.any(~np.isfinite(c)) or np.any(c <= 0):
        raise ValueError("invalid B/capacities")
    n = B.shape[1]
    if n < 2:
        return float("inf")
    L = B.T @ B
    C_inv_sqrt = np.diag(1.0 / np.sqrt(c))
    eigenvalues = np.linalg.eigvalsh(C_inv_sqrt @ L @ C_inv_sqrt)
    positives = eigenvalues[eigenvalues > 1e-10]
    if len(positives) < n - 1:
        return 0.0
    return float(positives[0])
