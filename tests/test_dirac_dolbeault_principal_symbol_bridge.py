from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "dirac_dolbeault_principal_symbol_bridge.packet.json"


class DiracDolbeaultPrincipalSymbolBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_dirac_dolbeault_principal_symbol_bridge.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))

    def test_builder_passes_all_checks(self) -> None:
        self.assertEqual(self.packet["check_summary"]["total"], 46)
        self.assertTrue(self.packet["check_summary"]["all_passed"])

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_dirac_dolbeault_principal_symbol_bridge.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"all_passed": true', result.stdout)

    def test_non_diagonal_six_dimensional_Clifford_relations_are_exact(self) -> None:
        witness = self.packet["exact_six_dimensional_clifford_witness"]
        self.assertEqual(witness["dimension"], 6)
        self.assertEqual(witness["complex_spinor_rank"], 8)
        self.assertEqual(witness["independent_Clifford_relation_count"], 21)
        self.assertTrue(witness["all_Clifford_relations_exact"])

    def test_metric_is_recovered_from_first_order_symbol(self) -> None:
        witness = self.packet["exact_six_dimensional_clifford_witness"]
        self.assertTrue(witness["metric_recovered_from_Clifford_anticommutators"])

    def test_all_polarization_samples_square_to_scalar_symbol(self) -> None:
        witness = self.packet["exact_six_dimensional_clifford_witness"]
        self.assertEqual(witness["principal_symbol_sample_count"], 21)
        self.assertTrue(witness["all_Dirac_squares_scalar"])

    def test_lower_order_terms_do_not_change_quadratic_symbol(self) -> None:
        stability = self.packet["lower_order_stability"]
        self.assertEqual(len(stability["rows"]), 3)
        self.assertTrue(stability["all_quadratic_coefficients_unchanged"])

    def test_T55_composition_recovers_scale_metric_and_Hodge(self) -> None:
        composition = self.packet["T55_composition"]
        self.assertEqual(composition["recovered_action_scale"], "7")
        self.assertTrue(composition["A_reconstruction_exact"])
        self.assertTrue(composition["metric_reconstruction_exact"])
        self.assertTrue(composition["inverse_metric_reconstruction_exact"])
        self.assertTrue(composition["Hodge_reconstruction_matches_T55"])

    def test_external_evidence_is_audited_without_overpromotion(self) -> None:
        audit = self.packet["q79_evidence_audit"]
        self.assertEqual(len(audit["sources"]), 3)
        self.assertFalse(audit["joint_conclusion"]["selected_physical_q79_operator_is_present"])
        self.assertFalse(audit["joint_conclusion"]["selected_physical_q79_density_is_present"])

    def test_scalar_symbol_and_metric_are_not_duplicate_source_rows(self) -> None:
        contract = self.packet["q79_source_contract_update"]
        self.assertEqual(contract["independent_scalar_symbol_proof_after_selected_Dirac_source"], 0)
        self.assertEqual(contract["independent_metric_payload_after_selected_Dirac_source_and_density"], 0)

    def test_actual_q79_operator_and_density_remain_open(self) -> None:
        contract = self.packet["q79_source_contract_update"]
        self.assertEqual(contract["selected_physical_q79_Dolbeault_operator"], "OPEN")
        self.assertEqual(contract["selected_physical_q79_density"], "OPEN")
        self.assertEqual(contract["selected_visible_hidden_HYM_connection"], "OPEN")

    def test_parameter_ledger_adds_nothing(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["continuous_physical_parameters_added"], 0)
        self.assertEqual(ledger["discrete_selectors_added"], 0)
        self.assertEqual(ledger["observed_values_used"], 0)
        self.assertEqual(ledger["fitted_values_used"], 0)
        self.assertFalse(ledger["benchmark_action_scale_is_physical"])

    def test_physical_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})

    def test_controlling_blockers_remain_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["B_GEO_01_closed"])
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_OP_01_closed"])


if __name__ == "__main__":
    unittest.main()
