from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "finite_dirac_cubic_variational_action.packet.json"


class FiniteDiracCubicVariationalActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_direct_action_is_exact_but_not_promoted_to_physical(self) -> None:
        action = self.packet["direct_variational_action"]
        self.assertEqual(action["gradient"], "grad S_sig(D)=D^2-I96")
        self.assertTrue(action["Helmholtz_exact"])
        self.assertTrue(action["unique_up_to_additive_constant"])
        self.assertFalse(action["physical_action_claimed"])

    def test_critical_locus_retains_first_order_closure_equation(self) -> None:
        locus = self.packet["critical_locus"]
        self.assertTrue(locus["equals_closure_locus"])
        self.assertEqual(locus["zero_operator_signed_gradient"], "-I96")
        self.assertEqual(locus["zero_operator_positive_repair_gradient"], "0")
        self.assertTrue(locus["normal_square_has_extra_critical_points"])

    def test_signed_hessian_has_balanced_morse_bott_inertia(self) -> None:
        hessian = self.packet["signed_Hessian"]
        self.assertEqual(hessian["spectrum"], {"-2": 2304, "0": 4608, "2": 2304})
        self.assertEqual(
            hessian["inertia"],
            {"negative": 2304, "positive": 2304, "zero": 4608},
        )
        self.assertTrue(self.packet["Morse_Bott_decomposition"]["finite_Morse_Bott"])

    def test_signed_hessian_squares_to_repair_hessian(self) -> None:
        bridge = self.packet["normal_square_bridge"]
        self.assertEqual(
            bridge["exact_identity"],
            "H_sig^2=J0^2=4(Pi_plus+Pi_minus)=A_rep",
        )
        self.assertEqual(bridge["T28_spectrum"], {"0": 4608, "4": 4608})
        self.assertTrue(bridge["same_root"])

    def test_KO6_cancels_signed_response_but_not_repair(self) -> None:
        cancellation = self.packet["KO6_cancellation"]
        self.assertTrue(cancellation["all_odd_traces_vanish"])
        self.assertEqual(cancellation["signed_action_pullback"], "S_sig(D_phys(t))=0")
        self.assertEqual(cancellation["D1_sector_norms"], {"Pi_minus": "1", "Pi_plus": "1", "Pi_zero": "0"})
        self.assertEqual(cancellation["signed_quadratic_pullback"], "0")
        self.assertEqual(cancellation["repair_quadratic_pullback"], "8")

    def test_weighted_anchor_is_nonzero_but_changes_the_geometry(self) -> None:
        weighted = self.packet["weighted_anchor_escape_test"]
        self.assertEqual(weighted["family_pullback"], "S_0(D_phys(t))=2t^2-(8/9)t^3")
        self.assertEqual(weighted["constrained_stationary_points"], ["0", "3/2"])
        self.assertFalse(weighted["three_halves_is_full_closure"])
        self.assertFalse(weighted["squares_to_A_rep"])
        self.assertFalse(weighted["physical_value_selector"])

    def test_two_anchor_classification_is_exact_and_scoped(self) -> None:
        classification = self.packet["canonical_two_anchor_classification"]
        self.assertEqual(
            classification["exact_square_solutions"],
            [{"a": -1, "b": 0}, {"a": 1, "b": 0}],
        )
        self.assertTrue(classification["all_exact_square_solutions_cancel"])
        self.assertTrue(classification["all_noncancelling_members_change_residual_or_zero_modes"])
        self.assertEqual(classification["scope"], "canonical anchors emitted by I96 and D0 only")

    def test_no_new_physical_parameters_or_fit_enter(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_sector_specific_parameters"], 0)
        self.assertTrue(ledger["canonical_coefficients_are_fixed_by_gradient"])

    def test_physical_action_gate_remains_explicitly_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["finite_signed_variational_action_closed"])
        self.assertTrue(boundary["signed_to_positive_normal_square_closed"])
        self.assertFalse(boundary["physical_Lorentzian_or_BV_action_selected"])
        self.assertFalse(boundary["continuum_q79_action_transfer_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
