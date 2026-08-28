from __future__ import annotations

import unittest

import build_q79_all_arity_source_promotion as promotion
import build_q79_symmetric_response_retraction_transferred_m3 as low


class AllAritySourcePromotionTests(unittest.TestCase):
    def test_generators_preserve_the_contraction(self) -> None:
        _, checks = promotion.contraction_naturality_checks()
        self.assertTrue(all(checks.values()))

    def test_induced_target_group_is_order_36(self) -> None:
        data, checks = promotion.target_group_checks()
        self.assertEqual(data["generated_order"], 36)
        self.assertTrue(all(checks.values()))

    def test_endpoint_contract_does_not_promote_physics(self) -> None:
        contract = promotion.endpoint_contract()
        self.assertEqual(contract["physical_rows_accepted"], 0)
        self.assertEqual(contract["physical_rows_total"], 7)
        self.assertTrue(all(row["state"] == "open" for row in contract["physical_source_rows"]))

    def test_selected_family_probe_remains_nonzero_and_equivariant(self) -> None:
        data, checks = promotion.selected_all_arity_probes()
        self.assertTrue(all(checks.values()))
        self.assertTrue(all(row["source_nonzero"] for row in data["probes"]))
        self.assertNotEqual(len(low.old_basis() + low.ideal_basis()), 0)


if __name__ == "__main__":
    unittest.main()
