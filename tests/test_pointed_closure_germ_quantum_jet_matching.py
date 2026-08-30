from __future__ import annotations

import json
import subprocess
import sys
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import build_pointed_closure_germ_quantum_jet_matching as t36


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "pointed_closure_germ_quantum_jet_matching.packet.json"


class PointedClosureGermQuantumJetMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_pointed_closure_germ_quantum_jet_matching.py"],
            cwd=ROOT,
            check=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_claim_and_builder_ledger(self) -> None:
        self.assertEqual(self.packet["claim_id"], "CBF.T36")
        self.assertTrue(all(self.packet["checks"].values()))

    def test_even_counterterm_jet_map_is_invertible(self) -> None:
        point = Fraction(9, 7)
        matrix = t36.jet_matrix(point)
        self.assertEqual(t36.det3(matrix), 16 * point**3)
        self.assertNotEqual(t36.det3(matrix), 0)

    def test_jet_retraction_is_exact_and_idempotent(self) -> None:
        point = Fraction(5, 4)
        polynomial = [Fraction(value) for value in (3, -2, 7, 11, -5, 13)]
        _, _, remainder = t36.retract_jet(polynomial, point)
        self.assertEqual(t36.jet(remainder, point), [Fraction(0)] * 3)
        _, _, second = t36.retract_jet(remainder, point)
        self.assertEqual(second, remainder)

    def test_jet_retraction_is_natural_under_radial_scaling(self) -> None:
        witness = self.packet["pointed_jet_retraction"]["exact_witness"]
        self.assertTrue(witness["target_counterterm_equals_scaled_source"])
        self.assertTrue(witness["target_remainder_equals_scaled_source"])
        self.assertEqual(witness["target_remainder_jet"], ["0", "0", "0"])

    def test_generic_gaussian_pushforward_shifts_the_vacuum_jet(self) -> None:
        odd = self.packet["gaussian_pushforward_no_go"]["odd_coupling"]
        self.assertNotEqual(odd["jet_at_zero"][1], "0")
        self.assertNotEqual(odd["jet_at_zero"][2], "0")
        self.assertTrue(odd["finite_gaussian_pushforward_exact"])

    def test_reflection_symmetry_protects_tadpole_not_hessian(self) -> None:
        even = self.packet["gaussian_pushforward_no_go"]["even_coupling"]
        self.assertEqual(even["jet_at_zero"][1], "0")
        self.assertNotEqual(even["jet_at_zero"][2], "0")
        self.assertTrue(even["reflection_symmetry_preserved"])

    def test_measure_normalization_is_an_independent_zero_jet(self) -> None:
        measure = self.packet["gaussian_pushforward_no_go"]["measure_normalization"]
        self.assertNotEqual(measure["effective_action_jet_shift"][0], "0")
        self.assertEqual(measure["effective_action_jet_shift"][1:], ["0", "0"])
        self.assertTrue(measure["normalized_nongravitational_correlators_unchanged"])
        self.assertFalse(measure["gravitational_vacuum_energy_unchanged"])

    def test_relative_T35_remainder_is_independent_of_delta_omega(self) -> None:
        numeric = self.packet["t35_reduction"]["numerical_execution"]
        with localcontext() as context:
            context.prec = 80
            point = Decimal(numeric["H_over_Lambda"])
            q4 = Decimal(numeric["q4_star"])
            kappa = Decimal(numeric["test_kappa_F"])
            l4 = Decimal("18.176066017544062361087042190541135501620313031067563880808957659162441858734842")
            for record in numeric["sample_records"]:
                h = Decimal(record["h_over_H"]) * point
                mu = Decimal(record["mu_over_Lambda"])
                scheme = Decimal(record["c_scheme"])
                omega = Decimal(record["delta_Omega_over_Lambda4"])
                corrected_h = t36.corrected_first_second(
                    h, point, mu, scheme, kappa, q4, l4, omega
                )
                corrected_point = t36.corrected_first_second(
                    point, point, mu, scheme, kappa, q4, l4, omega
                )
                expected = t36.universal_relative_remainder(h, point, kappa, q4)
                self.assertLess(
                    abs((corrected_h - corrected_point) - expected),
                    Decimal("1e-70"),
                )

    def test_three_certificates_are_obligations_not_fit_parameters(self) -> None:
        clauses = self.packet["matching_clause_classification"]
        self.assertEqual(clauses["certificate_count"], 3)
        self.assertFalse(clauses["these_are_scalar_fit_parameters"])
        self.assertFalse(clauses["QJ0"]["selected_by_existing_sources"])
        self.assertFalse(clauses["QJ1"]["selected_by_existing_sources"])
        self.assertFalse(clauses["QJ2"]["selected_by_existing_sources"])

    def test_parameter_and_physical_boundaries_do_not_inflate(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_physical_parameters"], 0)
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
