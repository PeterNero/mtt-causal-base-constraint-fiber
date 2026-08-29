from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DirectOneConstraintMultiplierSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "direct_one_constraint_multiplier_source.packet.json").read_text(
                encoding="utf-8"
            )
        )

    def test_three_family_kernel_occurs_exactly_at_four_source_copies(self) -> None:
        table = self.packet["minimality_theorem"]["multiplicity_table"]
        selected = [
            row for row in table if row["family_copies_in_kernel"] == 3
        ]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["source_multiplicity"], 4)
        self.assertEqual(selected[0]["kernel_dimension"], 48)
        self.assertFalse(
            self.packet["minimality_theorem"]["independent_prediction_of_four_copies"]
        )

    def test_signed_hessian_and_positive_repair_are_kept_distinct(self) -> None:
        actions = self.packet["actions"]
        self.assertEqual(actions["signed_spectrum"], {"+1": 16, "-1": 16, "0": 48})
        self.assertEqual(actions["signed_hessian"], "D_J=[[0,J*],[J,0]]")
        self.assertEqual(actions["repair_hessian"], "Q=J*J")
        self.assertEqual(actions["critical_locus"], "ker(J) x {0} = C3 tensor H16")

    def test_repair_flow_projects_and_source_class_has_no_matrix_knob(self) -> None:
        flow = self.packet["repair_flow"]
        source_class = self.packet["unitary_source_class"]
        self.assertEqual(flow["composition"], "T_r T_s=T_(rs)")
        self.assertEqual(flow["limit"], "T_0=P")
        self.assertEqual(
            source_class["continuous_dimensionless_parameters_after_equivalence"],
            0,
        )
        self.assertEqual(source_class["all_unit_covectors_equivalent_under"], "U(4)")

    def test_gauge_circle_descend_but_flavor_values_do_not(self) -> None:
        descent = self.packet["descent"]
        self.assertEqual(descent["gauge_group"], "(SU3 x SU2 x U1Y)/Z6")
        self.assertEqual(descent["shared_circle_weights_6Y"], [1, -4, 2, -3, 6, 0])
        self.assertEqual(descent["free_family_stabilizer"], "U(3)")
        self.assertEqual(descent["family_commutant_dimension"], 1)
        self.assertEqual(
            self.packet["parameter_ledger"]["unselected_nonlinear_family_or_sector_values"],
            9,
        )

    def test_physical_promotion_and_scale_remain_open(self) -> None:
        self.assertTrue(all(value is False for value in self.packet["claim_boundary"].values()))
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)
        self.assertEqual(
            self.packet["parameter_ledger"]["unselected_dimensionful_scales"],
            1,
        )
        self.assertEqual(
            self.packet["externalization"]["free_associated_matter_source_subclause"],
            "CLOSED_AT_CONDITIONAL_BENCHMARK_TIER",
        )


if __name__ == "__main__":
    unittest.main()
