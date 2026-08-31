from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "q79_hermitian_metric_hodge_compiler.packet.json"


def load_packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


class Q79HermitianMetricHodgeCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_hermitian_metric_hodge_compiler.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = load_packet()

    def test_builder_packet_passes(self) -> None:
        summary = self.packet["check_summary"]
        self.assertTrue(summary["all_passed"])
        self.assertEqual(summary["passed"], 42)

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_hermitian_metric_hodge_compiler.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"passed": 96', result.stdout)

    def test_metric_is_exact_positive_Hermitian_witness(self) -> None:
        witness = self.packet["non_diagonal_hermitian_witness"]
        self.assertEqual(witness["determinant_G"], "1")
        self.assertTrue(witness["positive_definite"])
        self.assertTrue(witness["Hermitian"])
        self.assertTrue(witness["inverse_exact"])

    def test_witness_is_genuinely_non_diagonal(self) -> None:
        metric = self.packet["non_diagonal_hermitian_witness"]["covariant_metric_G"]
        self.assertTrue(
            any(metric[row][column] != "0" for row in range(6) for column in range(6) if row != column)
        )

    def test_full_Hodge_matrix_is_emitted(self) -> None:
        witness = self.packet["non_diagonal_hermitian_witness"]
        self.assertEqual(witness["full_Hodge_shape"], [64, 64])
        self.assertEqual(
            len(witness["full_Hodge_sparse_entries"]),
            witness["full_Hodge_nonzero_entries"],
        )
        self.assertGreater(witness["full_Hodge_nonzero_entries"], 64)

    def test_all_metric_Hodge_identities_are_exact(self) -> None:
        witness = self.packet["non_diagonal_hermitian_witness"]
        self.assertTrue(witness["star_square_identity"])
        self.assertTrue(witness["wedge_metric_identity"])
        self.assertEqual(witness["wedge_metric_identity_checks"], 924)
        self.assertTrue(witness["Hodge_isometry"])

    def test_identity_metric_recovers_T51(self) -> None:
        definition = self.packet["metric_hodge_definition"]
        self.assertIn("CBF.T51", definition["T51_specialization"])
        self.assertTrue(self.packet["checks"]["identity_metric_specializes_exactly_to_T51"])

    def test_eight_shape_directions_are_exactly_emitted(self) -> None:
        response = self.packet["eight_shape_first_variation"]
        self.assertEqual(response["fixed_complex_structure_volume_one_shape_dimension"], 8)
        self.assertEqual(len(response["direction_labels"]), 8)
        self.assertEqual(response["direction_span_rank"], 8)

    def test_shape_basis_has_correct_decomposition(self) -> None:
        labels = self.packet["eight_shape_first_variation"]["direction_labels"]
        self.assertEqual(sum(label.startswith("diag_") for label in labels), 2)
        self.assertEqual(sum(label.startswith("real_") for label in labels), 3)
        self.assertEqual(sum(label.startswith("imag_") for label in labels), 3)

    def test_all_shape_directions_are_tracefree_Hermitian(self) -> None:
        checks = self.packet["eight_shape_first_variation"]["direction_checks"]
        self.assertTrue(all(row["trace_zero"] for row in checks.values()))
        self.assertTrue(all(row["symmetric"] for row in checks.values()))
        self.assertTrue(all(row["Hermitian"] for row in checks.values()))

    def test_direct_minor_derivative_matches_variation_formula(self) -> None:
        response = self.packet["eight_shape_first_variation"]
        self.assertTrue(
            response["direct_minor_derivative_matches_variation_formula_at_identity"]
        )
        self.assertTrue(
            response[
                "direct_minor_derivative_matches_variation_formula_at_non_diagonal_metric"
            ]
        )

    def test_Hodge_response_has_rank_eight_at_both_metrics(self) -> None:
        response = self.packet["eight_shape_first_variation"]
        self.assertEqual(response["identity_Hodge_response_rank"], 8)
        self.assertEqual(response["non_diagonal_Hodge_response_rank"], 8)
        self.assertTrue(response["injective_on_all_eight_shape_directions"])

    def test_proto_spinor_compiler_row_advances_only_one_tier(self) -> None:
        rows = self.packet["q79_instantiation_boundary"]["proto_spinor_row_update"]
        self.assertEqual(rows["metric_endomorphism_coefficient_compiler"], "CLOSED_BY_T52")
        self.assertEqual(rows["selected_metric_endomorphism_coefficients"], "OPEN")
        self.assertEqual(rows["selected_HYM_connection_correction_coefficients"], "OPEN")
        self.assertEqual(rows["gauge_projector_values"], "OPEN")

    def test_physical_metric_and_beta_root_remain_open(self) -> None:
        boundary = self.packet["q79_instantiation_boundary"]
        self.assertEqual(boundary["selected_metric_endomorphism_values"], "OPEN")
        self.assertEqual(boundary["selected_FuYau_conformal_factor"], "OPEN")
        self.assertEqual(boundary["same_member_beta_C_root_EA03R"], "OPEN")

    def test_HYM_and_rank102_execution_remain_open(self) -> None:
        boundary = self.packet["q79_instantiation_boundary"]
        self.assertEqual(boundary["selected_visible_hidden_HYM_metric_and_connection"], "OPEN")
        self.assertEqual(boundary["rank102_Dbar_domains_projector_and_Green"], "OPEN")
        self.assertEqual(boundary["associated_chiral_operator_and_index"], "OPEN")

    def test_eight_shapes_are_source_fields_not_fit_parameters(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["unresolved_metric_shape_source_fields"], 8)
        self.assertFalse(ledger["metric_shape_fields_are_fit_parameters"])
        self.assertTrue(ledger["metric_shape_fields_must_be_emitted_by_selected_endpoint"])

    def test_no_parameter_or_selector_is_added(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["continuous_parameters_added"], 0)
        self.assertEqual(ledger["discrete_selectors_added"], 0)
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["fitted_values_used"], 0)
        self.assertEqual(ledger["shared_action_primitives_after_T52"], 1)

    def test_physical_counters_and_blockers_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})
        self.assertFalse(boundary["B_HS_01_closed"])
        self.assertFalse(boundary["B_GEO_01_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])


if __name__ == "__main__":
    unittest.main()

