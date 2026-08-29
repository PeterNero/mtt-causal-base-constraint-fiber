from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CausalWeylGramAuxiliaryLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "causal_weyl_gram_auxiliary_lift.packet.json").read_text(
                encoding="ascii"
            )
        )

    def test_two_exact_sources_are_not_relabelled_one_physical_root(self) -> None:
        source = self.packet["source_composition"]
        self.assertEqual(source["finite_source"], "CBF.T20")
        self.assertEqual(source["source_roots"], 2)
        self.assertNotEqual(source["finite_root_sha256"], source["causal_root_sha256"])
        self.assertFalse(source["same_physical_root_proved"])
        self.assertFalse(source["eta9_used"])

    def test_order_zero_response_preserves_the_causal_cone(self) -> None:
        causal = self.packet["causal_lift"]
        self.assertEqual(causal["response_order"], 0)
        self.assertTrue(causal["characteristic_cone_unchanged"])
        self.assertTrue(causal["conditionally_Green_hyperbolic"])
        self.assertEqual(len(causal["covector_witnesses"]), 5)
        self.assertTrue(
            all(not row["response_changes_principal_symbol"] for row in causal["covector_witnesses"])
        )

    def test_auxiliary_lift_is_nontrivial_and_exact(self) -> None:
        auxiliary = self.packet["auxiliary_feshbach"]
        self.assertTrue(auxiliary["nontrivial_complement"])
        self.assertEqual(auxiliary["coupling"], "C=P tensor I16")
        self.assertEqual(auxiliary["coupling_rank"], 48)
        self.assertEqual(auxiliary["Schur_complement"], "F_D(K_mu)=L_mu")
        self.assertEqual(auxiliary["normalized_relative_intertwiner"], "T_rel=I6 at mu^2=1")

    def test_upper_rank_and_kernel_follow_exact_square_factorization(self) -> None:
        auxiliary = self.packet["auxiliary_feshbach"]
        self.assertEqual(auxiliary["upper_dimension"], 96)
        self.assertEqual(auxiliary["upper_rank_at_normalized_internal_witness"], 72)
        self.assertEqual(auxiliary["upper_kernel_at_normalized_internal_witness"], 24)
        self.assertTrue(self.packet["checks"]["upper_block_has_exact_square_factorization"])

    def test_endpoint_subclauses_advance_without_packet_acceptance(self) -> None:
        classification = self.packet["contract_classification"]
        self.assertEqual(len(classification["newly_closed_subclauses"]), 4)
        self.assertIn("conditional chart action", classification["GAS"])
        self.assertIn("nontrivial exact algebraic Schur", classification["SYN"])
        self.assertIn("Green-hyperbolic equicausal carrier", classification["BV4"])
        self.assertEqual(classification["physical_packets_accepted"], 0)

    def test_one_dimensionful_scale_and_physical_typing_remain_open(self) -> None:
        ledger = self.packet["parameter_ledger"]
        boundary = self.packet["physical_boundary"]
        self.assertEqual(ledger["observed_inputs"], 0)
        self.assertEqual(ledger["fitted_coefficients"], 0)
        self.assertEqual(ledger["new_dimensionless_shape_parameters"], 0)
        self.assertEqual(ledger["unselected_dimensionful_response_scales"], 1)
        self.assertFalse(boundary["physical_scale_selected"])
        self.assertFalse(boundary["Lorentz_Higgs_Yukawa_typing"])
        self.assertFalse(boundary["physical_BV4_insertion"])
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()

