"""Reproducible GMT graph, memory-timescale, and randomized stress experiments."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE))

from gmt_model import (GMTParameters, incidence_matrix, path_edges, cycle_edges,
                       complete_edges, simulate, generalized_spectral_gap)


def write_csv(path: Path, rows: list[dict]) -> None:
    if rows:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def main() -> None:
    params = GMTParameters(tau=0.65, theta=0.16, g_min=0.18, g_max=1.4)
    n = 9
    B = incidence_matrix(n, path_edges(n))
    u0 = np.zeros(n)
    u0[0] = 1.0
    r = simulate(B, u0, capacities=np.ones(n), params=params, t_end=18, n_samples=361)
    mean = float(r["weighted_mean"][0])
    mass_drift = float(np.max(np.abs(r["mass"] - r["mass"][0])))

    fig, ax = plt.subplots(figsize=(9, 5))
    for i in range(0, n, 2):
        ax.plot(r["t"], r["u"][:, i], label=f"node {i}")
    ax.set(title="GMT on a 9-node path", xlabel="time", ylabel="node state")
    ax.legend(ncol=3)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "path_potentials.png", dpi=160)
    plt.close(fig)

    gap = generalized_spectral_gap(B, np.ones(n))
    bound = r["energy"][0] * np.exp(-2 * params.g_min * gap * r["t"])
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(r["t"], np.maximum(r["energy"], 1e-18), label="measured E(t)")
    ax.semilogy(r["t"], np.maximum(bound, 1e-18), "--", label="proved exponential bound")
    ax.set(title="Lyapunov energy and analytic bound", xlabel="time", ylabel="energy (log scale)")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "energy_bound.png", dpi=160)
    plt.close(fig)

    topology_rows = []
    topologies = {
        "path": path_edges(8),
        "cycle": cycle_edges(8),
        "complete": complete_edges(8),
    }
    u_top = np.array([1.0, -0.5, 0.2, 0.9, -0.2, 0.7, -0.8, 0.1])
    caps = np.array([0.8, 1.0, 1.2, 1.4, 0.9, 1.6, 1.1, 0.7])
    for name, edges in topologies.items():
        Bg = incidence_matrix(8, edges)
        q = simulate(Bg, u_top, capacities=caps, params=params, t_end=22, n_samples=221)
        topology_rows.append({
            "topology": name, "nodes": 8, "edges": len(edges),
            "spectral_gap": generalized_spectral_gap(Bg, caps),
            "initial_energy": float(q["energy"][0]),
            "final_energy": float(q["energy"][-1]),
            "max_mass_drift": float(np.max(np.abs(q["mass"] - q["mass"][0]))),
        })
    write_csv(OUT / "topology_sweep.csv", topology_rows)

    B10 = incidence_matrix(10, path_edges(10))
    tau_rows = []
    fig, ax = plt.subplots(figsize=(8, 5))
    for tau in (0.08, 0.25, 0.8, 2.5, 8.0):
        pp = GMTParameters(tau=tau, theta=0.16, g_min=0.18, g_max=1.4)
        initial = np.linspace(1.0, -0.4, 10)
        q = simulate(B10, initial, capacities=np.ones(10), params=pp, t_end=20, n_samples=401)
        half = np.flatnonzero(q["energy"] <= q["energy"][0] / 2)
        t_half = float(q["t"][half[0]]) if len(half) else float("nan")
        tau_rows.append({"tau": tau, "time_to_half_energy": t_half,
                         "final_energy": float(q["energy"][-1])})
        ax.plot(q["t"], np.maximum(q["energy"], 1e-18), label=f"tau={tau}")
    ax.set(title="Memory-timescale sweep", xlabel="time", ylabel="energy (log scale)")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "tau_sweep.png", dpi=160)
    plt.close(fig)
    write_csv(OUT / "adaptation_time_sweep.csv", tau_rows)

    rng = np.random.default_rng(20261013)
    stress_rows = []
    for trial in range(50):
        edges = path_edges(7)
        candidates = [(i, j) for i in range(7) for j in range(i + 2, 7)
                      if (i, j) not in edges]
        rng.shuffle(candidates)
        edges += candidates[:int(rng.integers(0, 6))]
        Bg = incidence_matrix(7, edges)
        c = rng.uniform(0.5, 1.8, 7)
        uu = rng.normal(size=7)
        aa = rng.uniform(0, 1, len(edges))
        pp = GMTParameters(tau=float(10**rng.uniform(-1.3, 0.8)),
                           theta=float(10**rng.uniform(-1.4, 0.3)),
                           g_min=0.05, g_max=2.0)
        q = simulate(Bg, uu, aa, c, pp, t_end=8, n_samples=161, rtol=2e-9, atol=2e-11)
        stress_rows.append({
            "trial": trial, "nodes": 7, "edges": len(edges), "tau": pp.tau,
            "theta": pp.theta, "initial_energy": float(q["energy"][0]),
            "final_energy": float(q["energy"][-1]),
            "max_mass_drift": float(np.max(np.abs(q["mass"] - q["mass"][0]))),
            "min_memory": float(np.min(q["a"])), "max_memory": float(np.max(q["a"])),
            "max_energy_increment": float(np.max(np.diff(q["energy"]))),
        })
    write_csv(OUT / "random_stress_50.csv", stress_rows)

    summary = {
        "model": "Gradient-Memory Transport (GMT)",
        "attribution": "Mrityunjay K",
        "status": "proposed model; not empirically validated",
        "seed": 20261013,
        "path_initial_energy": float(r["energy"][0]),
        "path_final_energy": float(r["energy"][-1]),
        "path_weighted_mean": mean,
        "path_max_mass_drift": mass_drift,
        "topologies_tested": list(topologies),
        "tau_values_tested": [row["tau"] for row in tau_rows],
        "random_stress_trials": len(stress_rows),
        "stress_max_mass_drift": max(row["max_mass_drift"] for row in stress_rows),
        "stress_max_energy_increment": max(row["max_energy_increment"] for row in stress_rows),
        "stress_memory_min": min(row["min_memory"] for row in stress_rows),
        "stress_memory_max": max(row["max_memory"] for row in stress_rows),
        "interpretation": "Numerical consistency checks, not physical validation or proof of global novelty."
    }
    (OUT / "experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
