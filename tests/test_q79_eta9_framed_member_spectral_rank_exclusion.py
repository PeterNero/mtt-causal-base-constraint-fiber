from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_framed_member_spectral_rank_exclusion.packet.json"


class Q79Eta9FramedMemberSpectralRankExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_framed_member_spectral_rank_exclusion.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_framed_member_spectral_rank_exclusion.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T69 verification: PASS", result.stdout)

    def test_complete_certified_rank_range_is_excluded(self) -> None:
        rank = self.packet["rank_exclusion"]
        self.assertEqual(
            rank["certified_excluded_spectral_ranks_inclusive"], [1, 1449]
        )
        self.assertEqual(
            rank["corresponding_degree_three_inverse_transform_ranks"],
            {"first": 3, "formula": "3*r", "last": 4347, "step": 3},
        )

    def test_intended_endpoint_and_double_traversal_are_rejected(self) -> None:
        rank = self.packet["rank_exclusion"]
        self.assertEqual(rank["selected_endpoint"]["decision"], "REJECTED_FOR_C_fr")
        self.assertEqual(
            rank["double_traversal"]["decision"], "REJECTED_FOR_C_fr"
        )
        self.assertEqual(rank["spectral_rank_three"]["decision"], "REJECTED_FOR_C_fr")

    def test_resolution_loss_is_not_torsion_evidence(self) -> None:
        rank = self.packet["rank_exclusion"]
        self.assertEqual(rank["first_order_not_resolved_by_H4_T132_intervals"], 1450)
        self.assertEqual(rank["first_unresolved_corresponding_inverse_transform_rank"], 4350)
        self.assertIn("not a candidate", rank["unresolved_boundary"])

    def test_candidate_scope_is_preserved(self) -> None:
        candidate = self.packet["candidate"]
        self.assertEqual(candidate["name"], "C_fr")
        self.assertIn("not_coordinate_free", candidate["selection_tier"])
        self.assertFalse(self.packet["guardrails"]["claims_the_entire_G3AJ_ball_is_rejected"])

    def test_no_parameters_or_observations(self) -> None:
        self.assertEqual(
            self.packet["parameter_ledger"],
            {
                "new_continuous_fit_parameters": 0,
                "new_discrete_fit_parameters": 0,
                "observed_values_used": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()
