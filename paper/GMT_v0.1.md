# Gradient-Memory Transport on Finite Networks
## A proposed coupled model, theorem package, and reproducible numerical study

**Project attribution:** Mrityunjay K  
**Version:** 0.1.0  
**Date:** 13 October 2026  
**Status:** Exploratory mathematical research; not peer reviewed; not an established physical law.

## Abstract

This note specifies a finite-dimensional transport model in which node states diffuse over an undirected graph while edge conductances respond to a bounded, first-order memory of the squared state difference across each edge. The response is saturating, and its internal memory evolves on a tunable timescale. Under explicit positivity and regularity assumptions, the model has a unique global solution; memory remains in a unit interval; capacity-weighted mass is conserved; a quadratic deviation functional is nonincreasing; and, on a connected graph, the state converges exponentially to a capacity-weighted consensus. A maximum principle provides an additional state bound. A Python implementation, automated tests, and graph-based numerical experiments accompany the mathematics.

The contribution claimed here is deliberately limited to documenting this specific coupled formulation and its proof-and-computation package. Adaptive diffusion, consensus systems, graph Laplacians, Lyapunov functions, and ordinary differential equation methods have substantial prior literature. No claim of complete global novelty, empirical validity, or universal physical law is made.

## 1. Motivation and research question

Many network models describe transport with fixed edge conductances. Other models allow edges or node interactions to adapt. GMT studies a minimal mechanism that combines transport with an internal edge variable that relaxes toward a bounded response to the current squared endpoint difference.

The mathematical question is: **what can be proved about conservation, boundedness, and long-time behavior when conductance adapts through this memory state?** The initial model prioritizes properties that admit exact proofs and numerical verification rather than making an unsupported claim about a particular material.

Possible electrical or thermal analogies are discussed only as hypotheses. An analogy does not establish that a real physical element obeys this constitutive law.

## 2. Graph and variables

Let an undirected graph have n nodes and m edges. Fix an arbitrary orientation for each edge and let B be its m-by-n incidence matrix; each row contains one -1 and one +1. Thus B times the all-ones vector is zero. The orientation is bookkeeping only.

Define:
- u(t) in R^n: node states;
- C = diag(c_1,...,c_n), with c_i > 0: node capacities;
- a(t) in [0,1]^m: edge-memory states;
- tau > 0: memory relaxation timescale;
- theta > 0: saturation scale;
- 0 < g_min <= g_max < infinity: conductance limits.

For edge e, define conductance g_e(a_e) = g_min + (g_max - g_min) a_e, and let G(a) be the diagonal matrix of all edge conductances. The model state domain is finite u and a in the unit cube.

## 3. Governing equations

The proposed system is

```text
C du/dt = -B^T G(a) B u
tau da_e/dt = r((B u)_e) - a_e
r(z) = z^2 / (theta + z^2)
g_e(a_e) = g_min + (g_max - g_min) a_e
```

The response r is continuous and smooth, satisfies 0 <= r(z) < 1 for every finite real z, and is zero at z = 0. It increases with |z| and saturates toward 1 as |z| grows. Squaring the gradient makes the memory forcing independent of the chosen orientation of an undirected edge.

Interpretation: a_e is a first-order low-pass memory of a bounded edge signal. The timescale tau controls how fast memory tracks the current target. This structure is a modeling choice, not a microscopic derivation from first principles.

## 4. Assumptions

1. The graph is finite and undirected, with fixed topology during a run.
2. C is diagonal and strictly positive.
3. tau and theta are finite and strictly positive.
4. Conductances satisfy 0 < g_min <= g_max < infinity.
5. Initial states u(0) are finite and a(0) belongs to [0,1]^m.
6. The base system has no external sources, sinks, or stochastic forcing.

The connectedness condition is additionally required for global convergence to one common consensus. If the graph is disconnected, each component has its own conserved weighted mass.

## 5. Main theoretical results

The full derivations are in `proofs/PROOFS.md`. The main results are summarized here.

### 5.1 Memory invariance

For each edge, the memory equation has the variation-of-constants solution

```text
a_e(t) = exp(-t/tau) a_e(0)
       + (1/tau) integral_0^t exp(-(t-s)/tau) r((B u(s))_e) ds.
```

Since both the initial memory and the response lie in [0,1], and the weights in this expression are nonnegative with total weight one, a_e(t) remains in [0,1]. Consequently every conductance remains between g_min and g_max.

### 5.2 Capacity-weighted conservation

The quantity M(t) = 1^T C u(t) is constant because B 1 = 0. The invariant weighted mean is

```text
u_bar = (1^T C u(0)) / (1^T C 1).
```

### 5.3 Lyapunov dissipation

Let v = u - u_bar 1 and E = (1/2) v^T C v. Then

```text
dE/dt = -(B u)^T G(a) (B u)
      = -sum_e g_e(a_e) ((B u)_e)^2 <= 0.
```

The result follows from positive conductances and provides a rigorous nonincreasing quadratic deviation functional.

### 5.4 Exponential convergence

For a connected graph define the capacity-weighted spectral gap

```text
lambda_C = min ||Bv||_2^2 / (v^T C v),
           over v != 0 with 1^T C v = 0.
```

Then lambda_C > 0 and

```text
E(t) <= E(0) exp(-2 g_min lambda_C t).
```

This is a conservative lower-conductance rate bound, not a claim that the adaptive model beats all fixed-conductance baselines.

### 5.5 Maximum principle and global well-posedness

At a node attaining the current maximum, every neighboring state difference points inward or tangent; positive conductance therefore prevents an outward increase. The corresponding argument holds at a minimum. The state stays within the initial range. Smoothness gives local existence and uniqueness; invariant memory, conserved mean, and bounded Lyapunov deviation prevent finite-time blow-up, giving a unique global solution.

## 6. Numerical implementation and tests

The numerical prototype uses Python, NumPy, SciPy, and DOP853 integration. It implements explicit graph incidence matrices and unequal positive node capacities. The conductance evaluation clips only tiny numerical excursions of a solver's internal memory estimate; the exact mathematical system does not require clipping because its vector field points inward at the interval boundaries.

The automated test suite checks graph construction, mass conservation, energy nonincrease, memory bounds, conductance bounds, response saturation, constant-state equilibria, consensus convergence, the exponential rate bound, orientation invariance, invalid inputs, disconnected-graph spectral gap, zero-gradient memory relaxation, maximum principle, and variation across memory timescales.

The experiment script compares path, cycle, and complete graphs; evaluates several tau values; and runs 50 seeded stress trials with randomized states and positive capacities. The PDF release artifact includes the proof bundle and plotted numerical summaries. Exact floating-point discrepancies should be interpreted relative to solver tolerance.

## 7. Numerical results: correct interpretation

A tiny observed mass drift is a numerical error diagnostic. A decreasing energy curve is a finite-trajectory consistency check. Neither proves a theorem; the proofs do that under the stated assumptions. Neither validates the model in nature.

The project does not contain a physical measurement campaign, parameter fit to laboratory data, uncertainty-calibrated predictions, or evidence that GMT is better than simpler baselines. The next empirical study should pre-register a measurable system, estimate parameters on training data, compare held-out predictions against at least a fixed-conductance baseline, and report uncertainty and negative results.

## 8. Possible physical analogies

A capacitive electrical network or thermal network can motivate a graph-balance equation, but adopting GMT would require a real mechanism for the memory-dependent conductance. For an electrical platform, one would need a measured device whose conductance dynamics are approximately described by the edge-memory equation. For heat transport, one would additionally need a thermodynamically consistent constitutive law. Until then the physical readings remain analogies, not validations.

The quadratic function E is a Lyapunov functional measuring deviation from consensus; it should not be called physical stored energy unless variables and constitutive quantities justify that interpretation.

## 9. Limitations and falsification plan

- Adaptive diffusion and nonlinear network consensus are established fields; broad conceptual novelty is not claimed.
- Equation-level novelty comparison against papers, theses, patents, and unpublished material is incomplete.
- The phenomenological memory rule may not correspond to a natural material.
- Fixed, undirected, finite graphs exclude directed, spatially embedded, random, and rewiring systems.
- Noise, external driving, model uncertainty, and parameter identifiability are not handled here.
- Finite automated tests cannot cover every graph, initial state, solver, or parameter.
- A fixed-conductance model already has strong convergence properties. Adaptation should be justified by a measured predictive or control benefit that offsets added complexity.

A serious continuation should identify the nearest prior models, compare equations after nondimensionalization and change of variables, and seek independent review. A physical test should be planned prospectively, use a credible mechanism, fit on part of the data, evaluate held-out conditions, and compare against simpler competing models.

## 10. Next mathematical problems

1. **Forced GMT:** add a source vector and derive input-to-state bounds, revising conservation claims appropriately.
2. **Noisy memory:** determine whether invariant domains and expected-energy bounds survive carefully specified stochastic perturbations.
3. **Parameter inference:** establish identifiability for tau, theta, and conductance scale before proposing estimators.
4. **Continuum limit:** specify a graph sequence and scaling, then prove convergence of solutions and energies before claiming a PDE limit.
5. **Graph design:** optimize a named objective under edge-cost or robustness constraints and compare to standard spectral methods.

These are research proposals, not results established by version 0.1.0.

## 11. Conclusion

GMT is a fully specified candidate system for gradient-memory-modulated transport on a finite graph. The stated assumptions support proofs of memory invariance, weighted-mass conservation, energy dissipation, a maximum principle, global well-posedness, and exponential consensus on connected graphs. A reproducible implementation and numerical checks accompany the theory.

The responsible conclusion is bounded: the model's mathematical behavior has been formalized and tested numerically; empirical validity, comparative usefulness, and global novelty remain open questions.

## References and neighboring work

1. D. G. Tiglea, R. Candido, and M. T. M. Silva, “Adaptive diffusion networks: An overview,” *Signal Processing* 223 (2024), 109570. https://doi.org/10.1016/j.sigpro.2024.109570
2. R. Bonetto and H. Jardón Kojakhmetov, “Nonlinear diffusion on networks: Perturbations and consensus dynamics,” *Networks and Heterogeneous Media* 19(3) (2024), 1344–1380. https://doi.org/10.3934/nhm.2024058 ; preprint https://arxiv.org/abs/2206.04442
3. “Adaptive rewiring evolves brain-like structure in weighted networks,” *Scientific Reports* (2020). https://doi.org/10.1038/s41598-020-62204-7

These works show neighboring research areas; they do not, by themselves, decide whether the exact GMT formulation is equivalent to prior art.
