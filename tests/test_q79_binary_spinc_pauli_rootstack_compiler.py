from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_binary_spinc_pauli_rootstack_compiler.packet.json"


class Q79BinarySpinCPauliRootStackCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_binary_spinc_pauli_rootstack_compiler.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_checks_pass(self) -> None:
        self.assertTrue(all(self.packet["checks"].values()))

    def test_binary_relations_are_exact(self) -> None:
        relations = self.packet["binary_spinor"]["relations"]
        self.assertEqual(relations, ["q1^2=q2^2=-1", "q1 q2 q1=q2 q1 q2", "(q1 q2)^3=-1"])

    def test_determinant_twist_is_literal_sheet_permutation(self) -> None:
        pauli = self.packet["pauli_adjoint"]
        self.assertEqual(pauli["determinant_twisted_Ad_q1"], pauli["P_23"])
        self.assertEqual(pauli["determinant_twisted_Ad_q2"], pauli["P_12"])

    def test_compiler_is_one_plus_three(self) -> None:
        compiler = self.packet["flat_rootstack_compiler"]
        self.assertEqual(compiler["character_on_identity_transposition_three_cycle"], [4, 0, 1])
        self.assertEqual(compiler["rank_three_lane"], "D tensor sl(S)=E_D^C")
        self.assertIn("L_shared", compiler["scalar_lane"])

    def test_full_s3_holonomy_is_present(self) -> None:
        rows = self.packet["flat_rootstack_compiler"]["holonomy_rows"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["class"] == "transposition" for row in rows), 3)
        self.assertEqual(sum(row["class"] == "three_cycle" for row in rows), 2)

    def test_conjugate_roots_need_no_selector(self) -> None:
        binary = self.packet["binary_spinor"]
        self.assertEqual(binary["SpinC_roots"], ["+i", "-i"])
        self.assertEqual(binary["unselected_conjugate_presentations"], 2)
        self.assertFalse(self.packet["flat_rootstack_compiler"]["new_parameter_or_selector"])

    def test_hidden_hym_naturality_is_scoped(self) -> None:
        hidden = self.packet["hidden_HYM_compatibility"]
        self.assertTrue(hidden["curvature_HYM_constant_and_hidden_Hessian_unchanged"])
        self.assertFalse(hidden["selected_visible_V3"])
        self.assertFalse(hidden["physical_Hull_Strominger_endpoint"])

    def test_T24_is_not_reused_as_the_missing_suspension(self) -> None:
        cutset = self.packet["totalization_cutset"]
        self.assertFalse(cutset["T24_supplies_T61_degree_shift"])
        self.assertIn("does not suspend or regrade", cutset["reason"])

    def test_qutrit_binding_is_explicitly_open(self) -> None:
        cutset = self.packet["source_cutset"]
        self.assertEqual(cutset["open_qutrit_maps"], ["b_v:U_v->S", "b_i:U_i->S"])
        self.assertEqual(cutset["derived_T61_matching_if_maps_exist"], "s=b_v^(-1) b_i")

    def test_physical_soldering_is_single_typed_exit(self) -> None:
        cutset = self.packet["source_cutset"]
        self.assertEqual(cutset["open_physical_soldering"], "sigma_D:E_D^C->T^(0,1)*X")
        self.assertIn("certified continuum-to-finite error", cutset["required_endpoint_properties"])

    def test_physical_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual((boundary["physical_packets_accepted"], boundary["physical_packets_required"]), (0, 3))
        self.assertEqual((boundary["physical_rows_accepted"], boundary["physical_rows_required"]), (0, 7))

    def test_parameter_ledger_adds_nothing(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["observed_inputs"], 0)
        self.assertEqual(ledger["fitted_values"], 0)
        self.assertEqual(ledger["continuous_physical_parameters"], 0)
        self.assertEqual(ledger["discrete_physical_selectors"], 0)

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_binary_spinc_pauli_rootstack_compiler.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
