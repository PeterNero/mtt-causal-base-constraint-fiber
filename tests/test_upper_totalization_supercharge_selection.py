from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "upper_totalization_supercharge.packet.json"


class UpperTotalizationSuperchargeSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_factor_differentials_are_nilpotent_chiral_halves(self) -> None:
        factors = self.packet["factor_differentials"]
        self.assertEqual(factors["external_square"], "q_Y^2=0")
        self.assertEqual(factors["finite_square"], "q_F(t)^2=0")
        self.assertEqual(factors["finite_dimension"], 96)
        self.assertEqual(factors["total_dimension"], 192)

    def test_koszul_totalization_is_unique_in_declared_class(self) -> None:
        totalization = self.packet["totalization_uniqueness"]
        self.assertEqual(totalization["coefficient_rank"], 4)
        self.assertEqual(totalization["unique_solution"], ["1", "0", "0", "-1"])
        self.assertEqual(totalization["selected_coefficient"], "A=Gamma_Y")
        self.assertFalse(totalization["naive_ungraded_sum_nilpotent"])
        self.assertFalse(totalization["mixed_interaction_terms_selected"])

    def test_total_charge_recovers_the_physical_response(self) -> None:
        charge = self.packet["physical_closure_charge"]
        self.assertEqual(
            charge["response"], "L_rel'(0)=h^2 I tensor H_phys"
        )
        self.assertEqual(charge["target_compression"], "h^2 H_derived")
        self.assertEqual(
            charge["one_primitive_identity"],
            "h=Lambda=E0=1/L0 and mu^2=Lambda^2=h^2",
        )

    def test_shared_line_is_parallel_but_not_the_HYM_connection(self) -> None:
        shared = self.packet["shared_line_naturality"]
        self.assertTrue(shared["totalization_is_parallel"])
        self.assertTrue(shared["connection_and_holonomy_preserved"])
        self.assertFalse(shared["flat_line_identified_with_nonzero_Chern_HYM"])

    def test_binary_roots_are_balanced_not_selected(self) -> None:
        roots = self.packet["binary_root_balance"]
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(roots["roots_mod64"], [16, 48])
        self.assertEqual(roots["two_factor_difference_mod64"], 0)
        self.assertEqual(roots["finite_Yukawa_factor_root_charge"], 0)
        self.assertFalse(roots["one_root_selected"])
        self.assertFalse(roots["selector_required_for_this_endpoint"])
        self.assertEqual(ledger["new_binary_root_selectors"], 0)

    def test_product_clause_closes_without_endpoint_overpromotion(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["CBF_T22_composite_product_selected"])
        self.assertTrue(boundary["selection_is_conditional_on_factor_sources"])
        self.assertFalse(boundary["primitive_q79_background_selected_here"])
        self.assertFalse(boundary["continuum_HYM_intertwiner"])
        self.assertFalse(boundary["physical_BV_QME"])
        self.assertFalse(boundary["nonlinear_physical_action_selected"])
        self.assertFalse(boundary["full_B_ACTION_01_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
