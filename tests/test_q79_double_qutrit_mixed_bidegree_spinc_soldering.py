from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_double_qutrit_mixed_bidegree_spinc_soldering.packet.json"


class Q79DoubleQutritMixedBidegreeSpinCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_double_qutrit_mixed_bidegree_spinc_soldering.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_passes(self) -> None:
        self.assertTrue(self.packet["check_summary"]["all_passed"])
        self.assertEqual(self.packet["check_summary"]["total"], 46)

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_double_qutrit_mixed_bidegree_spinc_soldering.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"all_passed": true', result.stdout)
        self.assertIn('"total": 41', result.stdout)

    def test_same_degree_polarized_route_is_exact_locally(self) -> None:
        row = self.packet["direct_holomorphic_polarization"]
        self.assertTrue(row["is_unitary"])
        self.assertTrue(row["uses_original_exterior_degree"])
        self.assertTrue(row["chartwise_map_selected_by_vertical_internal_labels_and_eta9_orientation"])
        self.assertFalse(row["global_connection_compatible_map_selected"])

    def test_direct_degree_one_route_is_rejected(self) -> None:
        row = self.packet["direct_degree_one_cutset"]
        self.assertFalse(row["invertible_intertwiner_exists"])
        self.assertIn("-I4", row["proof"])

    def test_mixed_bidegree_is_the_rank_four_replacement(self) -> None:
        row = self.packet["mixed_bidegree_endomorphism"]
        self.assertEqual(row["full_H2_ranks"], [1, 4, 1])
        self.assertTrue(row["endomorphism_map_is_unitary"])
        self.assertEqual(row["diagonal_double_return_spectrum"], {"+1": 2, "-1": 2})

    def test_trace_pauli_split_is_exact(self) -> None:
        row = self.packet["trace_pauli_transform"]
        self.assertTrue(row["is_unitary"])
        self.assertEqual(len(row["traceless_rows"]), 3)
        self.assertEqual(self.packet["result"]["finite_trace_decomposition_ranks"], [1, 3])

    def test_global_mixed_carrier_keeps_the_shared_determinant_line(self) -> None:
        bundle = self.packet["global_bundle_criterion"]
        soldering = self.packet["spinc_adjoint_soldering_criterion"]
        self.assertEqual(bundle["raw_mixed_bundle"], "M=U_v tensor U_i")
        self.assertIn("det(U_i)", bundle["globally_typed_mixed_bundle"])
        self.assertIn("D_i", bundle["scalar_line"])
        self.assertTrue(soldering["required_map"].startswith("kappa:D_i tensor End_0"))

    def test_double_return_cancels_the_central_sign(self) -> None:
        row = self.packet["mixed_bidegree_endomorphism"]
        self.assertIn("(-I) tensor (-I)=+I", row["central_sign_cancellation"])

    def test_C4_alone_does_not_select_the_map(self) -> None:
        row = self.packet["global_bundle_criterion"]
        self.assertEqual(row["C4_only_intertwiner_dimension_complex"], 8)
        self.assertFalse(row["C4_alone_selects_the_map"])

    def test_global_exit_is_two_typed_parallel_maps(self) -> None:
        matching = self.packet["global_bundle_criterion"]
        soldering = self.packet["spinc_adjoint_soldering_criterion"]
        self.assertFalse(matching["global_parallel_matching_selected"])
        self.assertFalse(soldering["selected_physical_kappa"])
        self.assertIn("s:U_i->U_v", matching["required_matching"])
        self.assertIn("kappa", soldering["required_map"])

    def test_corrected_bridge_has_normalized_formula(self) -> None:
        row = self.packet["corrected_augmented_bridge"]
        self.assertEqual(row["primary_same_degree_route"]["map"], "I_pol=s_alpha direct-sum kappa_3")
        self.assertIn("tr(B)/sqrt(2)", row["secondary_mixed_spinc_route"]["map"])
        self.assertEqual(row["secondary_mixed_spinc_route"]["determinant_line_map"], "d_alpha:D_i->L_alpha")
        self.assertIn("totalization", row["secondary_mixed_spinc_route"]["degree_issue"])

    def test_physical_frontier_does_not_move(self) -> None:
        row = self.packet["physical_boundary"]
        self.assertFalse(row["B_HS_01_closed"])
        self.assertFalse(row["B_GEO_01_closed"])
        self.assertFalse(row["B_OP_01_closed"])
        self.assertEqual(row["physical_rows"], {"accepted": 0, "total": 7})

    def test_no_new_parameter_or_fit(self) -> None:
        self.assertTrue(all(value == 0 for value in self.packet["parameter_ledger"].values()))

    def test_frontier_retires_generic_U4_search(self) -> None:
        delta = self.packet["frontier_delta"]["named_exit_clause_changed"]
        self.assertIn("local generic U(4) search is retired", delta)


if __name__ == "__main__":
    unittest.main()
