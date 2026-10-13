"""Unit, invariant, convergence, and validation tests for GMT."""
import unittest
import numpy as np

from gmt_model import (GMTParameters, incidence_matrix, path_edges, cycle_edges,
                       complete_edges, simulate, conductances, response,
                       generalized_spectral_gap)


class TestGMTModel(unittest.TestCase):
    def setUp(self):
        self.B = incidence_matrix(7, path_edges(7))
        self.u0 = np.array([1.0, 0.4, -0.5, 0.2, 0.9, -0.2, 0.1])
        self.a0 = np.linspace(0.0, 1.0, self.B.shape[0])
        self.c = np.array([0.7, 1.0, 1.3, 1.7, 0.9, 1.4, 1.1])
        self.p = GMTParameters(tau=0.45, theta=0.2, g_min=0.12, g_max=1.6)

    def test_incidence_matrix_has_zero_row_sums(self):
        for B in (self.B, incidence_matrix(8, cycle_edges(8)), incidence_matrix(5, complete_edges(5))):
            np.testing.assert_allclose(B @ np.ones(B.shape[1]), 0.0, atol=0.0)

    def test_weighted_mass_is_conserved_with_unequal_capacities(self):
        r = simulate(self.B, self.u0, self.a0, self.c, self.p, t_end=12, n_samples=301)
        self.assertLess(np.max(np.abs(r["mass"] - r["mass"][0])), 2e-9)

    def test_lyapunov_energy_is_nonincreasing(self):
        r = simulate(self.B, self.u0, self.a0, self.c, self.p, t_end=12, n_samples=301)
        self.assertLess(np.max(np.diff(r["energy"])), 2e-10)
        self.assertLess(r["energy"][-1], r["energy"][0])

    def test_memory_remains_in_unit_interval(self):
        r = simulate(self.B, self.u0, self.a0, self.c, self.p, t_end=12, n_samples=301)
        self.assertGreaterEqual(float(np.min(r["a"])), -2e-8)
        self.assertLessEqual(float(np.max(r["a"])), 1.0 + 2e-8)

    def test_conductances_are_positive_and_bounded(self):
        g = conductances(np.linspace(0, 1, 9), self.p)
        self.assertTrue(np.all(g >= self.p.g_min))
        self.assertTrue(np.all(g <= self.p.g_max))
        self.assertTrue(np.all(g > 0))

    def test_response_saturation(self):
        values = response(np.array([0.0, 1e-6, 0.1, 1.0, 100.0]), self.p.theta)
        self.assertEqual(values[0], 0.0)
        self.assertTrue(np.all(values >= 0))
        self.assertTrue(np.all(values < 1))
        self.assertTrue(np.all(np.diff(values) >= 0))

    def test_equilibrium_constant_potential_stays_constant(self):
        u = np.full(7, 3.25)
        r = simulate(self.B, u, np.full(6, 0.6), self.c, self.p, t_end=5, n_samples=101)
        np.testing.assert_allclose(r["u"], np.repeat(u[None, :], len(r["t"]), axis=0), atol=1e-12, rtol=0)
        self.assertLess(float(np.max(r["energy"])), 1e-24)

    def test_consensus_convergence(self):
        r = simulate(self.B, self.u0, self.a0, self.c, self.p, t_end=200, n_samples=401)
        self.assertLess(r["energy"][-1], 1e-5 * r["energy"][0])
        target = np.dot(self.c, self.u0) / np.sum(self.c)
        self.assertLess(np.max(np.abs(r["u"][-1] - target)), 2e-3)

    def test_proved_exponential_energy_bound(self):
        gap = generalized_spectral_gap(self.B, self.c)
        r = simulate(self.B, self.u0, self.a0, self.c, self.p, t_end=10, n_samples=251)
        bound = r["energy"][0] * np.exp(-2 * self.p.g_min * gap * r["t"])
        self.assertLessEqual(float(np.max(r["energy"] - bound)), 5e-8)

    def test_graph_orientation_does_not_change_solution(self):
        edges = path_edges(7)
        B = incidence_matrix(7, edges)
        B_reversed = incidence_matrix(7, [(j, i) for i, j in edges])
        r1 = simulate(B, self.u0, self.a0, self.c, self.p, t_end=6, n_samples=121)
        r2 = simulate(B_reversed, self.u0, self.a0, self.c, self.p, t_end=6, n_samples=121)
        np.testing.assert_allclose(r1["u"], r2["u"], atol=1e-9, rtol=1e-9)
        np.testing.assert_allclose(r1["energy"], r2["energy"], atol=1e-9, rtol=1e-9)

    def test_maximum_principle_keeps_values_in_initial_range(self):
        r = simulate(self.B, self.u0, self.a0, self.c, self.p, t_end=20, n_samples=401)
        self.assertGreaterEqual(float(np.min(r["u"])), float(np.min(self.u0)) - 2e-8)
        self.assertLessEqual(float(np.max(r["u"])), float(np.max(self.u0)) + 2e-8)

    def test_zero_gradient_memory_relaxes_exponentially(self):
        u = np.full(7, 2.0)
        a0 = np.linspace(0.1, 0.9, 6)
        r = simulate(self.B, u, a0, self.c, self.p, t_end=2.0, n_samples=101)
        expected = a0[None, :] * np.exp(-r["t"][:, None] / self.p.tau)
        np.testing.assert_allclose(r["a"], expected, atol=2e-10, rtol=2e-9)

    def test_validation_rejects_nonpositive_capacity(self):
        with self.assertRaises(ValueError):
            simulate(self.B, self.u0, self.a0, [1, 1, 0, 1, 1, 1, 1], self.p)

    def test_validation_rejects_bad_memory(self):
        with self.assertRaises(ValueError):
            simulate(self.B, self.u0, np.full(6, 1.2), self.c, self.p)

    def test_validation_rejects_duplicate_edges(self):
        with self.assertRaises(ValueError):
            incidence_matrix(3, [(0, 1), (1, 0)])

    def test_disconnected_graph_gap_is_zero(self):
        B = incidence_matrix(4, [(0, 1), (2, 3)])
        self.assertEqual(generalized_spectral_gap(B, np.ones(4)), 0.0)

    def test_parameter_sweep_remains_stable(self):
        rng = np.random.default_rng(71)
        for tau in (0.05, 0.2, 1.0, 5.0):
            p = GMTParameters(tau=tau, theta=0.08, g_min=0.05, g_max=2.0)
            r = simulate(self.B, rng.normal(size=7), rng.uniform(0, 1, 6), self.c, p,
                         t_end=8, n_samples=161, rtol=2e-9, atol=2e-11)
            self.assertLess(np.max(np.diff(r["energy"])), 2e-8)
            self.assertLess(np.max(np.abs(r["mass"] - r["mass"][0])), 2e-8)
            self.assertGreaterEqual(np.min(r["a"]), -2e-7)
            self.assertLessEqual(np.max(r["a"]), 1+2e-7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
