from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_eta9_twisted_spectral_rank_divisibility.packet.json"


class Q79Eta9TwistedSpectralRankDivisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_eta9_twisted_spectral_rank_divisibility.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_eta9_twisted_spectral_rank_divisibility.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CBF.T68 verification: PASS", result.stdout)

    def test_rank_one_gate_is_derived(self) -> None:
        endpoint = self.packet["endpoint_decision"]
        self.assertEqual(endpoint["unchanged_MTT_BHT_spectral_rank"], 1)
        self.assertEqual(endpoint["cover_degree"], 3)
        self.assertEqual(endpoint["unchanged_inverse_transform_rank"], 3)
        self.assertEqual(endpoint["required_class"], "beta_C=0")
        self.assertFalse(endpoint["is_an_optional_selection_convention"])

    def test_b89_odd_rank_sieve(self) -> None:
        rows = self.packet["B89_application"]["rank_table_1_through_10"]
        for row in rows:
            self.assertEqual(
                row["necessary_component_condition_passes"],
                row["rank"] % 2 == 0,
            )
        self.assertFalse(self.packet["B89_application"]["exact_integral_order_known"])
        self.assertEqual(
            self.packet["B89_application"]["corresponding_inverse_transform_rank"],
            6,
        )

    def test_g3bi_rank_five_sieve(self) -> None:
        rows = self.packet["G3BI_application"]["rank_table_1_through_10"]
        for row in rows:
            self.assertEqual(
                row["necessary_component_condition_passes"],
                row["rank"] % 5 == 0,
            )
        self.assertIn(
            "necessary local-component test only",
            self.packet["G3BI_application"]["rank_five_boundary"],
        )
        self.assertEqual(
            self.packet["G3BI_application"]["corresponding_inverse_transform_rank"],
            15,
        )

    def test_t67_is_not_promoted(self) -> None:
        self.assertEqual(
            self.packet["T67_interpretation"]["physical_promotion"],
            "FORBIDDEN_BY_THE_B89_RANK_ONE_ENDPOINT_SIEVE",
        )

    def test_no_parameters_or_observations(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["new_continuous_fit_parameters"], 0)
        self.assertEqual(ledger["new_discrete_fit_parameters"], 0)
        self.assertFalse(any(self.packet["guardrails"].values()))


if __name__ == "__main__":
    unittest.main()
