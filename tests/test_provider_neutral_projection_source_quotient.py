from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProviderNeutralSourceQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "provider_neutral_projection_source_quotient.packet.json").read_text(
                encoding="utf-8"
            )
        )
        cls.schema = json.loads(
            (ROOT / "provider_neutral_physical_source_contract.schema.json").read_text(
                encoding="utf-8"
            )
        )

    def test_q79_is_a_provider_not_a_projection_argument(self) -> None:
        classification = self.packet["q79_classification"]
        self.assertFalse(classification["q79_required_by_projection_formulas"])
        self.assertEqual(classification["q79_sufficiency_for_selected_physics"], "OPEN")
        self.assertEqual(
            classification["q79_uniqueness_as_physical_provider"],
            "NOT_ESTABLISHED",
        )

    def test_non_q79_equivalence_witness_is_exact_but_not_physical(self) -> None:
        witness = self.packet["exact_equivalence_witness"]
        self.assertEqual(witness["internal_dimension"], 80)
        self.assertEqual(witness["kernel_dimension"], 48)
        self.assertEqual(witness["intertwiner_order"], 3)
        self.assertTrue(all(witness["unitary_intertwining"].values()))
        self.assertTrue(witness["source_a"]["benchmark_only"])
        self.assertTrue(witness["source_b"]["benchmark_only"])

    def test_projection_cannot_reconstruct_discarded_values(self) -> None:
        countermodels = self.packet["no_source_no_values_countermodels"]
        self.assertTrue(countermodels["threshold"]["shared_projected_internal_operator"])
        self.assertNotEqual(
            countermodels["threshold"]["source_1_complement_gap"],
            countermodels["threshold"]["source_2_complement_gap"],
        )
        self.assertNotEqual(
            countermodels["interaction"]["source_1_tensor_norm_squared"],
            countermodels["interaction"]["source_2_tensor_norm_squared"],
        )

    def test_contract_accepts_multiple_provider_kinds_but_requires_provenance(self) -> None:
        provider_kinds = self.schema["properties"]["root_source"]["properties"]
        provider_kinds = provider_kinds["provider_kind"]["enum"]
        self.assertIn("q79_hull_strominger", provider_kinds)
        self.assertIn("direct_closure_repair", provider_kinds)
        self.assertIn("finite_spectral_action", provider_kinds)
        self.assertIn(
            "one_root_hash_for_all_packets",
            self.schema["properties"]["bindings"]["required"],
        )

    def test_physical_boundary_is_preserved(self) -> None:
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_packets_total"], 3)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_total"], 7)
        self.assertTrue(all(self.packet["checks"].values()))


if __name__ == "__main__":
    unittest.main()
