from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "selected_future_state_moller_bv_transport.packet.json"


class SelectedFutureStateMollerBVTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_selected_future_state_moller_bv_transport.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_checks_pass(self) -> None:
        self.assertTrue(all(self.packet["checks"].values()))
        self.assertEqual(self.packet["check_summary"]["failed"], [])

    def test_exact_state_transport_is_closed(self) -> None:
        result = self.packet["exact_direct_state_transport"]
        self.assertTrue(result["Hadamard_preserved"])
        self.assertTrue(result["purity_preserved"])
        self.assertEqual(result["new_state_parameter_count"], 0)
        self.assertFalse(result["nonlinear_full_SM_interaction"])

    def test_transported_projection_is_exact(self) -> None:
        projection = [
            [Fraction(value) for value in row]
            for row in self.packet["exact_transport_witness"]["transported_projection"]
        ]
        self.assertEqual(
            projection,
            [
                [Fraction(9, 25), Fraction(12, 25)],
                [Fraction(12, 25), Fraction(16, 25)],
            ],
        )

    def test_transport_composes(self) -> None:
        witness = self.packet["exact_transport_witness"]
        self.assertEqual(witness["sequential_transport_projection"], witness["direct_composite_projection"])

    def test_square_expectations_are_positive(self) -> None:
        values = [
            Fraction(row["positive_square_expectation"])
            for row in self.packet["exact_transport_witness"]["positive_square_rows"]
        ]
        self.assertTrue(all(value >= 0 for value in values))

    def test_formal_pullback_is_not_full_selection(self) -> None:
        result = self.packet["formal_BV_state_pullback"]
        self.assertTrue(result["closed_as_algebraic_transport_theorem"])
        self.assertFalse(result["instantiated_as_selected_full_SM_state"])

    def test_canonical_lift_is_closed(self) -> None:
        lift = self.packet["canonical_BRST_lift"]
        self.assertEqual(lift["recursive_lift"], "psi_n=-h r_n")
        self.assertTrue(lift["does_not_select_free_seed"])

    def test_lift_witness_has_exact_norm(self) -> None:
        witness = self.packet["canonical_lift_witness"]
        self.assertEqual(witness["formal_lift"], "psi(lambda)=epsilon_1+lambda x")
        self.assertEqual(witness["normalization_identity"], "<psi(lambda),psi(lambda)>_J=1")

    def test_seed_factorization_has_two_open_factors(self) -> None:
        factors = self.packet["full_seed_factorization"]
        self.assertEqual(factors["missing_selected_factors"], 2)
        self.assertFalse(factors["Higgs_fluctuation_factor"]["selected"])
        self.assertFalse(factors["gauge_physical_factor"]["selected"])
        self.assertFalse(factors["full_product_seed_selected"])

    def test_radial_marginal_is_not_higgs_state(self) -> None:
        marginal = self.packet["full_seed_factorization"]["radial_background_marginal"]
        self.assertFalse(marginal["is_Higgs_fluctuation_state"])

    def test_G2_ledger_is_typed(self) -> None:
        ledger = self.packet["G2_clause_ledger"]
        self.assertEqual(ledger["G2b_exact_quadratic_background_Dirac_state_transport"], "closed by T46")
        self.assertEqual(ledger["G2b_selected_full_gauge_Higgs_Weyl_seed"], "open")
        self.assertEqual(ledger["top_level_physical_G2"], "open")

    def test_fixed_coupling_boundary_is_preserved(self) -> None:
        boundary = self.packet["fixed_coupling_boundary"]
        self.assertEqual(boundary["finite_auxiliary_regulator_Cstar_rows"], "5/5")
        self.assertEqual(boundary["selected_continuum_Cstar_rows"], "0/9")
        self.assertFalse(boundary["T46_proves_regulator_removal"])

    def test_no_new_parameters(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_fitted_parameters"], 0)
        self.assertEqual(ledger["new_continuous_state_selectors"], 0)
        self.assertEqual(ledger["new_discrete_state_selectors"], 0)

    def test_physical_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual((boundary["physical_packets_accepted"], boundary["physical_packets_total"]), (0, 3))
        self.assertEqual((boundary["physical_rows_accepted"], boundary["physical_rows_total"]), (0, 7))

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_selected_future_state_moller_bv_transport.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
