# GMT simulation package

The solver is in `gmt_model.py`; automated tests are in `test_gmt_model.py`; the reproducible topology, timescale, and stress experiments are run by `run_experiments.py`.

From repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s simulation -p "test_*.py" -v
python simulation/run_experiments.py
```

Results are written to `simulation/results/`. Numerical results support implementation checks only; they are not experimental validation of a physical law.
