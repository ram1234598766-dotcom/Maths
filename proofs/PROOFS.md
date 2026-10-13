# Appendix A — Theorem statements and proofs

## A.1 Definitions and assumptions

Let B be the oriented incidence matrix of a finite undirected graph; hence B 1 = 0. Let C = diag(c_i) with every c_i > 0. Let tau > 0, theta > 0, and 0 < g_min <= g_max < infinity. For edge e,

```text
C u_dot = -B^T G(a) B u
tau a_dot_e = r((B u)_e) - a_e
r(z) = z^2 / (theta + z^2)
g_e(a_e) = g_min + (g_max - g_min) a_e
```

Assume u(0) is finite and a(0) is in [0,1]^m.

## Lemma A.1 — response bounds and smoothness

For each real z, 0 <= r(z) < 1, r(0)=0, and r is continuously differentiable.

**Proof.** z^2 >= 0 and theta + z^2 > z^2 because theta > 0. The ratio is therefore nonnegative and strictly less than one. At z=0 it is zero. Differentiation gives r'(z) = 2 z theta / (theta + z^2)^2, continuous on the real line. QED.

## Theorem A.2 — forward invariance of edge memory

If every a_e(0) belongs to [0,1], then every a_e(t) belongs to [0,1] for all t >= 0.

**Proof.** Rewrite an edge equation as a_dot_e + a_e/tau = r((B u)_e)/tau. Multiplying by exp(t/tau) and integrating gives

```text
a_e(t) = exp(-t/tau) a_e(0)
       + (1/tau) integral_0^t exp(-(t-s)/tau) r((B u(s))_e) ds.
```

The initial value is nonnegative and the integrand is nonnegative, so a_e(t) >= 0. Since a_e(0) <= 1 and r <= 1,

```text
a_e(t) <= exp(-t/tau) + (1/tau) integral_0^t exp(-(t-s)/tau) ds
        = exp(-t/tau) + 1 - exp(-t/tau) = 1.
```

Thus [0,1] is forward invariant. QED.

## Corollary A.3 — conductance bounds

For every edge and all t >= 0, g_min <= g_e(a_e(t)) <= g_max.

**Proof.** The conductance is an affine interpolation between g_min and g_max with interpolation parameter a_e in [0,1]. QED.

## Theorem A.4 — conservation of capacity-weighted mass

M(t) = 1^T C u(t) is constant.

**Proof.**

```text
M_dot = 1^T C u_dot
      = -1^T B^T G(a) B u
      = -(B 1)^T G(a) B u
      = 0,
```

because B 1 = 0. The conserved weighted mean is u_bar = (1^T C u(0))/(1^T C 1). QED.

## Theorem A.5 — Lyapunov energy dissipation

Let v = u - u_bar 1 and E = (1/2) v^T C v. Then E_dot = -(B u)^T G(a)(B u) <= 0.

**Proof.** Theorem A.4 makes u_bar constant, so v_dot = u_dot. Also Bv = Bu because B1=0. Therefore

```text
E_dot = v^T C u_dot
      = -v^T B^T G(a) B u
      = -(Bv)^T G(a) (B u)
      = -(B u)^T G(a) (B u)
      = -sum_e g_e(a_e) ((B u)_e)^2 <= 0.
```

Each summand is nonnegative before the minus sign because each conductance is positive. QED.

## Theorem A.6 — exponential consensus for connected graphs

Assume the graph is connected. Define

```text
lambda_C = min ||Bv||_2^2 / (v^T C v),
           over v != 0 with 1^T C v = 0.
```

Then lambda_C > 0 and E(t) <= E(0) exp(-2 g_min lambda_C t).

**Proof.** From Theorem A.5 and g_e >= g_min,

```text
E_dot <= -g_min ||Bv||_2^2
       <= -g_min lambda_C v^T C v
       = -2 g_min lambda_C E.
```

Hence the derivative of exp(2 g_min lambda_C t) E(t) is nonpositive, proving the bound. Connectedness makes the nullspace of B precisely the constant vectors; on the capacity-weighted-mean-zero subspace, the quotient has a strictly positive minimum. The energy tends to zero, and positive definiteness of C gives v -> 0. QED.

## Theorem A.7 — maximum principle

For all nodes i and times t >= 0,

```text
min_i u_i(0) <= u_j(t) <= max_i u_i(0).
```

**Proof.** The node balance is c_i u_dot_i = sum over neighbors j of g_ij(t)(u_j-u_i). At a node currently attaining a maximum, all neighbor differences are nonpositive, so the derivative is nonpositive. At a node attaining a minimum, the derivative is nonnegative. A first-exit argument prevents the solution from crossing the initial range. Time dependence of conductance does not change this sign argument. QED.

## Theorem A.8 — global existence and uniqueness

There is a unique solution for every finite t >= 0 under the assumptions above.

**Proof.** The vector field is continuously differentiable: theta + z^2 never vanishes and all remaining operations are smooth in finite dimensions. It is locally Lipschitz, giving local existence and uniqueness. Theorem A.2 bounds a. Theorem A.4 fixes the weighted mean, and Theorem A.5 bounds the quadratic deviation because E never exceeds E(0). Since C is positive definite, bounded mean and bounded deviation imply bounded u. The full state therefore remains bounded on every finite interval; the standard ODE continuation theorem rules out finite-time blow-up. Uniqueness follows from local Lipschitz continuity. QED.

## Proposition A.9 — memory relaxation for a fixed edge input

If (Bu)_e = z_* is constant on [t_0,t], then

```text
a_e(t) = r(z_*) + (a_e(t_0)-r(z_*)) exp(-(t-t_0)/tau).
```

**Proof.** The right-hand side satisfies the linear equation tau a_dot = r(z_*) - a and the initial condition; uniqueness proves the formula. QED.

## Proposition A.10 — invariance to edge orientation

Reversing an edge flips the corresponding row b_e of B to -b_e. Its squared difference is unchanged, while the transport contribution b_e^T g_e b_e is invariant under the sign flip. Thus node dynamics and memory forcing for the same undirected edge are independent of arbitrary orientation. QED.

## Disconnected graph qualification

For a disconnected graph, each component conserves its own capacity-weighted mass and may approach its own component mean. A single global consensus and a positive global spectral gap are not guaranteed.

## What the proofs do not establish

The proofs establish properties of this mathematical system under its assumptions. They do not establish that a material or natural system follows GMT, that the model is useful compared with simpler alternatives, or that the formulation is globally novel.
