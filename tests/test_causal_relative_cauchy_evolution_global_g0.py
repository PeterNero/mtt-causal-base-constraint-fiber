from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "causal_relative_cauchy_evolution_global_g0.packet.json"


class CausalRelativeCauchyEvolutionGlobalG0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "build_causal_relative_cauchy_evolution_global_g0.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_packet_passes(self) -> None:
        self.assertEqual(self.packet["claim_id"], "CBF.T44")
        self.assertEqual(self.packet["check_summary"]["failed"], [])
        self.assertEqual(
            self.packet["check_summary"]["passed"],
            self.packet["check_summary"]["total"],
        )

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_causal_relative_cauchy_evolution_global_g0.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("independent checks: 95/95", result.stdout)

    def test_direct_global_operator_evolution_closes(self) -> None:
        gate = self.packet["gate_ledger"]["G0_direct_global_operator_relative"]
        self.assertTrue(gate["closed"])
        self.assertIn("representation-independent", gate["scope"])

    def test_global_scalar_G0_stays_open_and_is_interlocked_with_G2(self) -> None:
        gate = self.packet["gate_ledger"]["G0_global_scalar_physical"]
        self.assertFalse(gate["closed"])
        self.assertEqual(gate["interlocked_with"], "G2")

    def test_moller_inverse_is_exact(self) -> None:
        checks = self.packet["checks"]
        self.assertTrue(checks["resolvent_left_exact"])
        self.assertTrue(checks["resolvent_right_exact"])
        self.assertTrue(checks["Moller_left_inverse"])
        self.assertTrue(checks["Moller_right_inverse"])

    def test_minimal_return_chain_is_unique_and_parameter_free(self) -> None:
        contour = self.packet["minimal_return_chain"]
        self.assertEqual(contour["unique_normalized_cycle"], ["1", "-1"])
        self.assertEqual(contour["boundary_of_cycle"], ["0", "0"])
        self.assertEqual(contour["primitive_gcd"], 1)
        self.assertFalse(contour["extra_contour_parameter"])

    def test_equal_source_return_is_exact(self) -> None:
        operator = self.packet["operator_valued_global_G0"]
        self.assertEqual(operator["equal_source_identity"], "C_H[V,V]=1")
        self.assertTrue(self.packet["checks"]["equal_source_return_identity"])

    def test_common_phase_cancels_but_relative_phase_survives(self) -> None:
        phase = self.packet["phase_ledger"]
        self.assertTrue(phase["common_central_phase_cancels"])
        self.assertTrue(phase["relative_source_phase_is_retained"])
        self.assertFalse(phase["global_determinant_line_trivialized"])

    def test_state_scalarization_is_not_selected_by_return(self) -> None:
        state = self.packet["state_scalarization_cutset"]
        self.assertTrue(state["unequal_source_values_are_distinct"])
        self.assertTrue(state["equal_source_values_are_all_one"])
        self.assertFalse(state["return_identity_selects_state"])
        self.assertFalse(state["preferred_state_selected"])

    def test_T43_local_shadow_is_retained_without_global_overclaim(self) -> None:
        shadow = self.packet["T43_local_shadow"]
        self.assertEqual(shadow["selected_kappa_F"], "1/(2 pi^2)")
        self.assertTrue(shadow["direct_source_root_matches"])
        self.assertTrue(shadow["local_one_loop_shadow_retained"])
        self.assertFalse(shadow["full_global_scalar_equality_claimed"])

    def test_internal_circle_is_not_relabelled_as_time(self) -> None:
        boundary = self.packet["shared_circle_and_root_boundary"]
        self.assertFalse(boundary["internal_shared_circle_identified_with_physical_time"])
        self.assertFalse(boundary["internal_double_return_selects_CTP_contour"])
        self.assertFalse(boundary["prior_CTP_theorem_used_as_construction_source"])

    def test_binary_root_neutrality_adds_no_selector(self) -> None:
        boundary = self.packet["shared_circle_and_root_boundary"]
        self.assertEqual(boundary["binary_root_free_CAR_equivalence"], "closed_exact")
        self.assertFalse(boundary["binary_root_preferred_state_selected"])
        self.assertFalse(boundary["new_binary_root_selector"])

    def test_physical_counters_do_not_move(self) -> None:
        gate = self.packet["gate_ledger"]
        self.assertEqual((gate["physical_gluing_gates_closed"], gate["physical_gluing_gates_total"]), (0, 3))
        self.assertEqual((gate["physical_packets_accepted"], gate["physical_packets_total"]), (0, 3))
        self.assertEqual((gate["physical_rows_accepted"], gate["physical_rows_total"]), (0, 7))

    def test_no_fit_or_new_physical_parameter(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_physical_parameters"], 0)
        self.assertEqual(ledger["new_preferred_state_selectors"], 0)

    def test_remaining_blockers_are_not_overclaimed(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["global_scalar_determinant_closed"])
        self.assertFalse(boundary["relative_determinant_phase_closed"])
        self.assertFalse(boundary["G1_closed"])
        self.assertFalse(boundary["G2_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])


if __name__ == "__main__":
    unittest.main()
