from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "q79_oriented_hodge_real_carrier.packet.json"


def load_packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


class Q79OrientedHodgeRealCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_oriented_hodge_real_carrier.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = load_packet()

    def test_builder_packet_passes(self) -> None:
        summary = self.packet["check_summary"]
        self.assertTrue(summary["all_passed"])
        self.assertEqual(summary["passed"], 74)

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_oriented_hodge_real_carrier.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"passed": 143', result.stdout)

    def test_complete_hodge_table_has_64_rows(self) -> None:
        hodge = self.packet["oriented_exterior_hodge"]
        self.assertEqual(hodge["basis_dimension"], 64)
        self.assertEqual(len(hodge["complete_signed_permutation_table"]), 64)
        self.assertEqual(hodge["nonzero_entries"], 64)

    def test_exterior_degree_dimensions_are_exact(self) -> None:
        self.assertEqual(
            self.packet["oriented_exterior_hodge"]["degree_dimensions"],
            {"0": 1, "1": 6, "2": 15, "3": 20, "4": 15, "5": 6, "6": 1},
        )

    def test_star_square_holds_on_every_basis_state(self) -> None:
        rows = self.packet["oriented_exterior_hodge"]["star_square_rows"]
        self.assertEqual(len(rows), 64)
        self.assertTrue(all(row["actual"] == row["expected"] for row in rows))

    def test_all_equal_degree_wedge_star_pairs_are_checked(self) -> None:
        hodge = self.packet["oriented_exterior_hodge"]
        self.assertEqual(hodge["wedge_star_checks"], 924)
        self.assertEqual(
            hodge["wedge_sign_table_status"],
            "CLOSED_EXACT_ORIENTED_ORTHONORMAL_FRAME_COMPILER",
        )

    def test_T50_orientation_block_is_exactly_recovered(self) -> None:
        orientation = self.packet["normalized_orientation_composition"]
        self.assertEqual(orientation["star_1"], "1*nu")
        self.assertEqual(orientation["star_nu"], "1*1")
        self.assertEqual(orientation["T50_hodge_block"], [[0, 1], [1, 0]])
        self.assertTrue(orientation["restriction_equals_T50"])

    def test_same_volume_metric_changes_hodge_shape(self) -> None:
        shape = self.packet["same_volume_metric_shape_nogo"]
        self.assertEqual(shape["metric_determinant"], "1")
        self.assertEqual(shape["volume_factor"], "1")
        self.assertTrue(shape["is_Hermitian_for_fixed_standard_complex_structure"])
        self.assertGreater(shape["shape_rows_changed"], 0)

    def test_explicit_metric_counterfamily_rows_are_exact(self) -> None:
        rows = {
            row["input"]: row["coefficient"]
            for row in self.packet["same_volume_metric_shape_nogo"]["full_deformed_star_table"]
        }
        self.assertEqual(rows["1"], "1")
        self.assertEqual(rows["nu"], "1")
        self.assertEqual(rows["e1"], "1/4")
        self.assertEqual(rows["e3"], "4")

    def test_eight_metric_shapes_are_source_fields_not_parameters(self) -> None:
        shape = self.packet["same_volume_metric_shape_nogo"]
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(shape["fixed_complex_structure_volume_one_Hermitian_shape_dimension"], 8)
        self.assertEqual(ledger["metric_shape_source_components_for_general_fixed_complex_structure"], 8)
        self.assertFalse(ledger["metric_shape_components_are_free_parameters"])
        self.assertTrue(ledger["metric_shape_components_are_endpoint_fields_to_compute"])

    def test_conjugate_paired_realification_is_exact(self) -> None:
        real = self.packet["conjugate_paired_real_carrier"]
        self.assertTrue(real["kappa_squared_identity"])
        self.assertEqual(real["witness_original_complex_rank"], 3)
        self.assertEqual(real["fixed_real_rank"], 6)
        self.assertEqual(real["anti_fixed_real_rank"], 6)

    def test_unitary_connection_respects_realification(self) -> None:
        connection = self.packet["conjugate_paired_real_carrier"]["unitary_connection_witness"]
        self.assertTrue(connection["skew_symmetric"])
        self.assertTrue(connection["commutes_with_kappa"])

    def test_realified_hodge_contraction_is_exact(self) -> None:
        covariance = self.packet["operator_covariance"]
        self.assertTrue(all(covariance["checks"].values()))
        self.assertEqual(covariance["harmonic_rank"], 4)
        self.assertEqual(covariance["positive_rank"], 8)

    def test_realification_does_not_claim_majorana_or_chirality(self) -> None:
        real = self.packet["conjugate_paired_real_carrier"]
        self.assertTrue(real["does_not_select_Majorana_condition"])
        self.assertTrue(real["does_not_select_chiral_index"])

    def test_q79_physical_metric_and_operator_remain_open(self) -> None:
        boundary = self.packet["q79_instantiation_boundary"]
        self.assertEqual(boundary["selected_metric_endomorphism_coefficients"], "OPEN")
        self.assertEqual(boundary["selected_visible_hidden_HYM_metric_and_connection"], "OPEN")
        self.assertEqual(boundary["rank102_Dbar_Q_and_domains"], "OPEN")
        self.assertEqual(boundary["associated_chiral_operator_and_index"], "OPEN")

    def test_H4_T17_mode_boundary_is_not_reopened(self) -> None:
        boundary = self.packet["q79_instantiation_boundary"]
        self.assertTrue(boundary["other_86_topology_mode_disposition"].startswith("OPEN"))

    def test_one_primitive_and_physical_counters_do_not_move(self) -> None:
        ledger = self.packet["parameter_ledger"]
        physical = self.packet["physical_boundary"]
        self.assertEqual(ledger["shared_action_primitives_before_T51"], 1)
        self.assertEqual(ledger["shared_action_primitives_after_T51"], 1)
        self.assertEqual(ledger["continuous_parameters_added"], 0)
        self.assertEqual(physical["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(physical["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(physical["physical_rows"], {"accepted": 0, "total": 7})

    def test_all_controlling_blockers_remain_open(self) -> None:
        physical = self.packet["physical_boundary"]
        self.assertFalse(physical["B_HS_01_closed"])
        self.assertFalse(physical["B_GEO_01_closed"])
        self.assertFalse(physical["B_ACTION_01_closed"])
        self.assertFalse(physical["B_QFT_02_closed"])


if __name__ == "__main__":
    unittest.main()
