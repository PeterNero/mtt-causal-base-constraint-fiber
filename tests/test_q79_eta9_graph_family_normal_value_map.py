from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "q79_eta9_graph_family_normal_value_map.packet.json"


class Q79Eta9GraphFamilyNormalValueMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_graph_family_normal_value_map.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="ascii"))

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_graph_family_normal_value_map.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("im(D)=ker(N)", result.stdout)

    def test_finite_sequence_is_exact(self) -> None:
        sequence = self.packet["finite_exact_sequence"]
        self.assertEqual(sequence["response_rank"], 122)
        self.assertEqual(sequence["normal_rank"], 126)
        self.assertEqual(sequence["normal_times_response_nonzero_entries"], 0)
        self.assertEqual(sequence["kernel_normal_dimension"], 122)
        self.assertTrue(sequence["image_response_equals_kernel_normal"])

    def test_graph_normal_intertwiner_is_an_isomorphism(self) -> None:
        quotient = self.packet["graph_normal_duality"]
        self.assertEqual(quotient["shape"], [126, 126])
        self.assertEqual(quotient["rank"], 126)

    def test_fixed_fiber_does_not_determine_beta(self) -> None:
        correction = self.packet["fixed_fiber_scope_correction"]
        self.assertEqual(correction["surface_primitive_rows"], 248)
        self.assertEqual(correction["fiber_holomorphic_rows"], 82)
        self.assertEqual(correction["fiber_restriction_kernel_rank"], 166)
        self.assertIn(
            "the fixed-fiber solve alone rejects the candidate from U_eta9",
            correction["withdrawn_as_unproved"],
        )

    def test_true_transport_dimensions_are_preserved(self) -> None:
        cutset = self.packet["BHT_execution_cutset"]
        self.assertEqual(cutset["transport_state_rank"], 164)
        self.assertEqual(cutset["holomorphic_readout_rank"], 82)
        self.assertEqual(cutset["surface_accumulator_rank"], 248)
        self.assertEqual(cutset["forward_state_rank"], 412)
        self.assertEqual(cutset["normal_first_forward_state_rank_after_char0_normal"], 290)

    def test_six_midpoints_do_not_promote_to_pathwise_execution(self) -> None:
        cutset = self.packet["BHT_execution_cutset"]
        self.assertEqual(cutset["same_member_midpoint_transport_backends"]["accepted"], 6)
        self.assertEqual(cutset["same_member_midpoint_boundary_sources"]["accepted"], 6)
        self.assertEqual(cutset["same_member_midpoint_projective_H01_lifts"]["accepted"], 6)
        self.assertEqual(cutset["panelwise_complete_rank164_action"]["accepted"], 0)
        self.assertEqual(cutset["directed_path_integration"]["accepted"], 0)

    def test_beta_rows_and_blockers_remain_open(self) -> None:
        value_map = self.packet["characteristic_zero_value_map"]
        self.assertEqual(value_map["accepted_full_beta_rows"], {"accepted": 0, "total": 248})
        self.assertEqual(value_map["accepted_characteristic_zero_normal_rows"], {"accepted": 0, "total": 126})
        self.assertEqual(
            self.packet["frontier_delta"]["open_blockers"],
            ["B.ETA9.01", "B.ETA9.02"],
        )

    def test_no_parameter_or_selector_is_added(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["new_continuous_fit_parameters"], 0)
        self.assertEqual(ledger["new_discrete_fit_parameters"], 0)
        self.assertFalse(ledger["physical_member_selected"])


if __name__ == "__main__":
    unittest.main()
