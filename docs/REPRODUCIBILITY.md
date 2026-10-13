# Reproducibility guide

## Environment

Python 3.10+ with NumPy, SciPy, Matplotlib, and ReportLab. Dependency floors are listed in `requirements.txt`; exact versions can differ by platform.

## Run tests and simulations

From repository root:

```bash
python -m pip install -r requirements.txt
cd simulation
python -m unittest -v test_gmt_model.py
python run_experiments.py
```

The experiment script uses fixed random seeds so input generation is reproducible. Minor floating-point differences may occur across BLAS, SciPy, or operating-system versions.

## Experiments

- Path, cycle, and complete graph comparisons.
- Memory-time parameter sweep.
- Seeded randomized stress trials.
- Energy and node-state plots plus machine-readable CSV/JSON summaries.

## Interpretation

The tests check incidence-matrix conventions, weighted-mass conservation, energy dissipation, memory range, positive conductances, fixed equilibria, consensus, an analytic rate bound, orientation invariance, validation of invalid input, disconnected graphs, and robustness across selected memory times.

They do not prove theorems (the proofs do), validate a physical system, show superiority to standard diffusion, establish GPU scalability, or prove global novelty. Numerical solver output is approximate and should be assessed against tolerance.
