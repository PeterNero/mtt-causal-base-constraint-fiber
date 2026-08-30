from __future__ import annotations

import json
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"


def frac(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", maxsplit=1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text))


class QuantumRadialAnchorTadpoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_ledger_is_green(self) -> None:
        self.assertTrue(all(self.packet["checks"].values()))
        summary = self.packet["check_summary"]
        self.assertEqual(summary["passed"], summary["total"])
        self.assertEqual(summary["failed"], [])

    def test_pushforward_derivative_contains_measure_term(self) -> None:
        witness = self.packet["differentiated_pushforward_identity"][
            "exact_finite_witness"
        ]
        weights = [frac(value) for value in witness["fiber_probabilities_at_reference"]]
        action = [frac(value) for value in witness["action_radial_derivatives"]]
        anomaly = [frac(value) for value in witness["log_density_radial_derivatives"]]
        derivative = sum(
            (
                weight * (ds - da)
                for weight, ds, da in zip(weights, action, anomaly)
            ),
            Fraction(0),
        )
        self.assertEqual(derivative, 1)
        self.assertNotEqual(anomaly, [0, 0])

    def test_centered_involution_is_sufficient_but_not_present(self) -> None:
        witness = self.packet["differentiated_pushforward_identity"][
            "exact_finite_witness"
        ]
        self.assertEqual(witness["centered_involution_expectation"], "0")
        mechanism = self.packet["QJ1_mechanisms"]["centered_involution"]
        self.assertTrue(mechanism["sufficient"])
        self.assertFalse(mechanism["ordinary_h_to_minus_h_centers_nonzero_branch"])

    def test_qme_counterterm_orbit_is_not_selective(self) -> None:
        orbit = self.packet["QME_normalization_orbit"]
        point = frac(orbit["test_point_H"])
        target = frac(orbit["target_tadpole_shift"])
        for key in ("first_solution", "second_solution"):
            row = orbit[key]
            shift = 2 * frac(row["a"]) * point + 4 * frac(row["b"]) * point**3
            self.assertEqual(shift, target)
        self.assertTrue(orbit["QJ1_compatible_formal_QME_scheme_exists"])
        self.assertFalse(orbit["QME_uniquely_selects_QJ1"])

    def test_zero_source_legendre_anchor_proves_qj1_conditionally(self) -> None:
        mechanism = self.packet["QJ1_mechanisms"]["zero_source_state_anchor"]
        witness = mechanism["exact_witness"]
        self.assertEqual(witness["zero_source_Gamma_prime_at_H"], "0")
        self.assertTrue(witness["QJ1_follows_if_H_T34_equals_zero_source_expectation"])
        self.assertFalse(mechanism["same_source_equality_closed"])

    def test_actual_t35_bare_tadpole_is_nonzero(self) -> None:
        execution = self.packet["T35_tadpole_execution"]
        tadpole = Decimal(execution["bare_tadpole_over_kappa_Lambda3"])
        self.assertLess(tadpole, Decimal("-100"))
        self.assertFalse(execution["bare_tadpole_is_zero_at_mu_equals_Lambda"])
        self.assertTrue(execution["both_determinant_branches_have_nonzero_tadpole"])

    def test_tadpole_zero_scale_is_classified_not_promoted(self) -> None:
        execution = self.packet["T35_tadpole_execution"]
        self.assertGreater(Decimal(execution["mu_tad_over_H"]), Decimal(1))
        self.assertGreater(Decimal(execution["mu_tad_over_Lambda"]), Decimal(1))
        self.assertFalse(execution["mu_tad_selected_by_current_upper_action"])
        self.assertFalse(
            self.packet["parameter_ledger"][
                "bare_tadpole_zero_scale_is_counted_as_prediction"
            ]
        )

    def test_t35_pair_lies_on_qj1_affine_line(self) -> None:
        execution = self.packet["T35_tadpole_execution"]
        left = Decimal(execution["QJ1_line_reconstructed_from_T35_pair"])
        right = Decimal(
            execution["QJ1_counterterm_line_right_side_over_kappa_Lambda2"]
        )
        self.assertLess(abs(left - right), Decimal("1e-75"))
        self.assertEqual(
            self.packet["parameter_ledger"][
                "QJ1_nonconstant_counterterm_freedom_before_QJ2"
            ],
            1,
        )

    def test_no_fit_or_observed_value_was_added(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_physical_parameters"], 0)
        self.assertTrue(
            self.packet["state_anchor_reduction"][
                "QJ1_is_a_typed_state_or_Ward_certificate"
            ]
        )

    def test_formal_compatibility_closes_without_physical_promotion(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["formal_QME_compatible_QJ1_scheme_exists"])
        self.assertTrue(boundary["QJ1_reduced_to_same_source_state_anchor"])
        self.assertFalse(boundary["physical_QJ1_tadpole_protection_closed"])
        self.assertFalse(boundary["selected_interacting_q79_state_closed"])
        self.assertFalse(boundary["full_closure_jet_matching_selected"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
