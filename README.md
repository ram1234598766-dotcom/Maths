# Maths — Mrityunjay K's Mathematical Physics Research Archive

**Author attribution:** Mrityunjay K  
**Research note:** Gradient-Memory Transport (GMT), v0.1.0  
**Status:** Proposed mathematical model; exploratory numerical verification; not peer reviewed or validated as a physical law.  
**Research snapshot:** 13 October 2026

## Overview

GMT is a candidate model for transport on a finite undirected network. Each node carries a scalar state and positive capacity; each edge has a positive conductance modulated by a bounded internal memory state responding to the squared difference between endpoint states.

The model is

```text
C u_dot = -B^T G(a) B u
tau a_dot_e = ( (B u)_e^2 / (theta + (B u)_e^2) ) - a_e
g_e(a_e) = g_min + (g_max - g_min) a_e
```

Here B is an oriented incidence matrix, C is a positive diagonal capacity matrix, G(a) is the diagonal conductance matrix, and each memory coordinate a_e starts in [0,1].

## Main mathematical results

Under the assumptions stated in `paper/GMT_v0.1.md` and `proofs/PROOFS.md`, the project proves:
- forward invariance of each memory variable in [0,1];
- conservation of capacity-weighted mass;
- nonincrease of a quadratic Lyapunov functional;
- exponential convergence to capacity-weighted consensus on a connected graph;
- a maximum principle for node values;
- existence and uniqueness of a global solution.

## Repository contents

- `paper/GMT_v0.1.md` — formulation, assumptions, interpretation, limitations, and research plan.
- `proofs/PROOFS.md` — theorem statements and proofs.
- `simulation/gmt_model.py` — numerical solver and graph utilities.
- `simulation/test_gmt_model.py` — automated tests of invariants and numerical behavior.
- `simulation/run_experiments.py` — reproducible topology, memory-timescale, and randomized stress simulations.
- `docs/NOVELTY_AND_SCOPE.md` — initial, non-exhaustive prior-art and originality audit.
- `docs/REPRODUCIBILITY.md` — setup, experiments, and interpretation of test results.
- `release/GMT_Proofs_and_Simulations.pdf` — generated proof-and-simulation report, also attached to GitHub Release `v0.1.0`.
- `RIGHTS_AND_ATTRIBUTION.md` — attribution and rights statement.

## Reproduce

Python 3.10 or newer:

```bash
python -m pip install -r requirements.txt
cd simulation
python -m unittest -v test_gmt_model.py
python run_experiments.py
```

The workflow `.github/workflows/publish-release.yml` runs tests, builds the PDF, and publishes or updates the `v0.1.0` release when a commit reaches `main`.

## Scientific scope and novelty

This project does **not** claim “100% global novelty.” Adaptive diffusion, nonlinear graph dynamics, consensus, graph Laplacians, and Lyapunov analysis are established research areas. The exact GMT formulation is a candidate for further study; determining whether it provides a novel contribution requires equation-level literature comparison and independent mathematical review.

Simulations test whether the implementation behaves consistently with the equations; they do not validate the model as a law of nature. No physical experiment is claimed.

## Attribution

Prepared for **Mrityunjay K**. Attribution in a repository is a provenance statement, not a guarantee of legal exclusivity or priority over independently created or earlier work. See the rights and novelty documents before making legal or scientific novelty claims.
