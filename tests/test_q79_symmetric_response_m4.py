"""Regression tests for the transferred m4 theorem."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = json.loads(
    (ROOT / "q79_symmetric_response_transferred_m4.packet.json").read_text(encoding="utf-8")
)


class SymmetricResponseM4Tests(unittest.TestCase):
    def test_exact_packet_passes(self) -> None:
        self.assertEqual(PACKET["summary"], {"all_passed": True, "passed": 21, "total": 21})

    def test_complete_m4_table_is_nonzero_and_exact(self) -> None:
        execution = PACKET["execution"]
        self.assertEqual(execution["basis"]["all_basis_quadruples"], 5_308_416)
        self.assertEqual(execution["basis"]["degree_admissible_basis_quadruples"], 3_869_500)
        self.assertEqual(execution["m4"]["nonzero_basis_quadruples"], 693_208)
        self.assertEqual(
            execution["m4"]["nonzero_table_sha256"],
            "a534a7f2921037aeea145f865502fc9e78928d030363bb6e5f57c88f4b59231e",
        )

    def test_arity_four_identity_is_exhaustive(self) -> None:
        arity = PACKET["execution"]["arity_four"]
        self.assertEqual(arity["degree_admissible_basis_quadruples_checked"], 3_869_500)
        self.assertEqual(arity["residual_failures"], 0)
        self.assertIsNone(arity["first_residual_failure"])

    def test_unit_harmonic_and_higher_jet_cutsets(self) -> None:
        operation = PACKET["execution"]["m4"]
        self.assertEqual(operation["unit_input_nonzero_basis_quadruples"], 0)
        self.assertEqual(operation["all_harmonic_input_nonzero_basis_quadruples"], 0)
        self.assertEqual(operation["three_or_more_higher_jet_input_nonzero_basis_quadruples"], 0)
        self.assertEqual(
            operation["higher_jet_input_count_distribution"],
            {"0": 363_928, "1": 293_208, "2": 36_072},
        )

    def test_higher_and_physical_promotions_remain_open(self) -> None:
        self.assertTrue(PACKET["transferred_m4_computed"])
        self.assertTrue(PACKET["transferred_m4_nonzero"])
        self.assertFalse(PACKET["transferred_m5_and_higher_computed"])
        self.assertFalse(PACKET["target_identified_with_D_fin"])
        self.assertFalse(PACKET["selected_nonzero_Chern_HYM_endpoint"])
        self.assertFalse(PACKET["physical_action_selected"])
        self.assertFalse(PACKET["physical_vertex_claimed"])


if __name__ == "__main__":
    unittest.main()
