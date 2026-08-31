from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "normalized_orientation_coframe_bv_bridge.packet.json"


def load_packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


class NormalizedOrientationCoframeBVBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_normalized_orientation_coframe_bv_bridge.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = load_packet()

    def test_builder_packet_passes(self) -> None:
        self.assertTrue(self.packet["check_summary"]["all_passed"])
        self.assertEqual(self.packet["check_summary"]["passed"], 75)

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_normalized_orientation_coframe_bv_bridge.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("checks", result.stdout)

    def test_orientation_pairing_is_exact(self) -> None:
        orientation = self.packet["normalized_orientation_frobenius"]
        self.assertEqual(orientation["cyclic_pairing_matrix"], [["0", "1"], ["1", "0"]])
        self.assertEqual(orientation["pairing_determinant"], "-1")

    def test_hodge_metric_is_normalized_identity(self) -> None:
        orientation = self.packet["normalized_orientation_frobenius"]
        self.assertEqual(orientation["normalized_hodge_metric"], [["1", "0"], ["0", "1"]])

    def test_profile_real_involution_is_unique(self) -> None:
        real = self.packet["unique_profile_real_structure"]
        self.assertEqual(real["unique_solution"], "lambda=1")
        self.assertEqual(real["matrix_on_basis"], [[1, 0], [0, 1]])
        self.assertFalse(real["full_physical_field_real_slice_selected"])

    def test_coframe_and_product_density_agree(self) -> None:
        witness = self.packet["coframe_product_density"]["exact_witness"]
        self.assertEqual(witness["response_volume_density"], "120")
        self.assertEqual(witness["coframe_volume_density"], "120")
        self.assertEqual(witness["internal_fiber_factor"], "1")
        self.assertEqual(witness["reduced_product_volume_density"], "120")

    def test_bv_profile_pairing_is_preserved(self) -> None:
        retract = self.packet["exact_bv_profile_retract"]
        self.assertEqual(retract["internal_field_antifield_pairing"], "tau(1*nu)=1")
        self.assertEqual(retract["reduction_after_lift"], "IDENTITY")
        self.assertEqual(retract["odd_symplectic_rank"], 6)

    def test_action_samples_reduce_exactly(self) -> None:
        rows = self.packet["exact_bv_profile_retract"]["action_sample_rows"]
        self.assertTrue(all(row["residual"] == "0" for row in rows))

    def test_orientation_normalization_removes_second_direction(self) -> None:
        normalization = self.packet["normalization_rank_reduction"]
        self.assertEqual(normalization["pre_normalization_rank"], 2)
        self.assertEqual(normalization["post_normalization_rank"], 1)
        self.assertEqual(normalization["new_continuous_normalization_primitives"], 0)

    def test_alpha_is_transported_not_refit(self) -> None:
        normalization = self.packet["normalization_rank_reduction"]
        self.assertEqual(normalization["action_quantum_transport"], "alpha_upper=alpha_lower=f0/hbar")

    def test_bridge_audit_has_all_clauses(self) -> None:
        audit = self.packet["bridge_clause_audit"]
        rows = [key for key in audit if key.startswith("C")]
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(not audit[key]["closed"] for key in rows))

    def test_global_bridge_decision_is_not_promoted(self) -> None:
        audit = self.packet["bridge_clause_audit"]
        self.assertEqual(audit["global_decision"], "AUXILIARY_COTANGENT_REDUCTION_ONLY")
        self.assertFalse(audit["global_decision_changed"])

    def test_one_shared_primitive_is_preserved(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["shared_action_primitives_before_T50"], 1)
        self.assertEqual(ledger["shared_action_primitives_after_T50"], 1)
        self.assertEqual(ledger["continuous_action_parameters_added"], 0)
        self.assertEqual(ledger["continuous_density_parameters_added"], 0)

    def test_binary_orientation_is_not_continuous_amplitude(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["inherited_binary_causal_orientation"], 1)
        self.assertFalse(ledger["binary_orientation_is_continuous_amplitude"])

    def test_physical_counters_and_blockers_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["B_GEO_01_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})


if __name__ == "__main__":
    unittest.main()
