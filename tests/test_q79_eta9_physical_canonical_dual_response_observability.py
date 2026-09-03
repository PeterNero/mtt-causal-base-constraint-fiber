from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_physical_canonical_dual_response_observability.packet.json"


class Q79Eta9PhysicalCanonicalDualResponseObservabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_physical_canonical_dual_response_observability.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_replay(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_physical_canonical_dual_response_observability.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T73 verification: PASS", result.stdout)

    def test_adjunction_dimensions(self) -> None:
        row = self.packet["adjunction"]
        self.assertEqual(
            (row["curve_square"], row["fiber_genus"], row["H0_O9H_rank"], row["quotient_rank"]),
            (162, 82, 83, 82),
        )

    def test_canonical_response_preserves_exact_rank(self) -> None:
        row = self.packet["canonical_response_operator"]
        self.assertEqual(row["canonical_postmap_rank"], 246)
        self.assertEqual(row["canonical_response_image_rank"], 122)
        self.assertEqual(row["projective_response_kernel_rank"], 0)

    def test_same_physical_rows_and_quotient_charts(self) -> None:
        row = self.packet["same_source_alignment"]
        self.assertEqual(row["segments"], ["edge-0", "edge-1", "edge-2"])
        self.assertEqual(row["fiber_relation_pivots_zero_based"], {"edge-0": 5, "edge-1": 5, "edge-2": 11})

    def test_global_claims_remain_open(self) -> None:
        self.assertFalse(any(self.packet["guardrails"].values()))
        self.assertIn(
            "the divisor-to-Picard or Abel-Jacobi derivative",
            self.packet["frontier_delta"]["not_closed"],
        )


if __name__ == "__main__":
    unittest.main()
