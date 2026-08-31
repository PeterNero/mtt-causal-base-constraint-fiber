from __future__ import annotations

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "common_action_quantum_torsor.packet.json"


def load_packet() -> dict:
    return json.loads(PACKET_PATH.read_text(encoding="utf-8"))


class CommonActionQuantumTorsorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_common_action_quantum_torsor.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = load_packet()

    def test_builder_packet_passes(self) -> None:
        self.assertTrue(self.packet["check_summary"]["all_passed"])
        self.assertEqual(self.packet["check_summary"]["passed"], 58)

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_common_action_quantum_torsor.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("116/116", result.stdout)

    def test_scalar_amplitude_is_recovered_from_f0(self) -> None:
        coefficient = self.packet["common_coefficient_map"]
        self.assertEqual(coefficient["A_H"], "4 f0/pi^2")
        self.assertEqual(coefficient["T32_trace_factor"], 32)

    def test_radial_and_gauge_scales_are_not_conflated(self) -> None:
        typed = self.packet["common_coefficient_map"]["typed_scales"]
        self.assertFalse(typed["equality_claimed"])
        self.assertIn("radial", typed["c_H"])
        self.assertIn("gauge", typed["c_g"])

    def test_scalar_gauge_ratio_is_common_scale_invariant(self) -> None:
        self.assertEqual(
            self.packet["common_coefficient_map"]["scalar_to_gauge_ratio"],
            "A_H/g_i^(-2)=2/(3 pi^2 K_i)",
        )
        diagnostic = self.packet["common_coefficient_map"]["profile_diagnostic_only"]
        self.assertTrue(
            math.isclose(
                diagnostic["A_H_over_c_g"],
                2.0 / (3.0 * math.pi**2),
                rel_tol=0.0,
                abs_tol=2e-17,
            )
        )

    def test_common_amplitude_torsor_has_rank_one(self) -> None:
        torsor = self.packet["positive_scale_torsor"]
        self.assertEqual(torsor["jacobian_rank"], 1)
        self.assertEqual(torsor["relative_projection_rank"], 3)
        self.assertEqual(torsor["relative_projection_of_orbit"], [0, 0, 0])

    def test_action_quantum_is_alpha(self) -> None:
        action = self.packet["dimensionless_effective_action"]
        self.assertEqual(action["shared_primitive"], "alpha=f0/hbar")
        self.assertEqual(action["one_loop_over_tree_prefactor"], "1/(8 alpha)")

    def test_pointed_loop_preserves_the_free_two_jet(self) -> None:
        action = self.packet["dimensionless_effective_action"]
        self.assertEqual(action["rho_jets_0_through_5_at_one"][:3], [0, 0, 0])
        self.assertNotEqual(action["rho_jets_0_through_5_at_one"][3:], [0, 0, 0])

    def test_free_mass_is_amplitude_blind(self) -> None:
        vertices = self.packet["canonical_radial_vertices"]
        self.assertEqual(vertices["mass_squared"], "8 c_H")
        self.assertEqual(vertices["f0_scaling_exponents"]["mass_squared"], "0")

    def test_interactions_detect_the_remaining_primitive(self) -> None:
        exponents = self.packet["canonical_radial_vertices"]["f0_scaling_exponents"]
        self.assertEqual(exponents["g3_tree"], "-1/2")
        self.assertEqual(exponents["g4_tree"], "-1")

    def test_T39_adds_no_counterterm_parameter(self) -> None:
        bv = self.packet["bv_qme_scale_separation"]
        self.assertEqual(bv["T39_anchor_conditions"], 3)
        self.assertEqual(bv["T39_free_coefficients_after_anchor"], 0)

    def test_H4_gluing_is_not_overpromoted(self) -> None:
        bv = self.packet["bv_qme_scale_separation"]
        self.assertFalse(bv["H4_physical_multiplier_selected"])
        self.assertFalse(bv["H4_to_direct_gluing_proved"])

    def test_one_shared_primitive_adds_no_new_knob(self) -> None:
        ledger = self.packet["one_shared_primitive_ledger"]
        self.assertEqual(ledger["shared_primitives_before_scalar_BV_consolidation"], 1)
        self.assertEqual(ledger["shared_primitives_after_scalar_BV_consolidation"], 1)
        self.assertEqual(ledger["new_primitives_introduced_by_T49"], 0)

    def test_strict_source_value_remains_open(self) -> None:
        ledger = self.packet["one_shared_primitive_ledger"]
        self.assertEqual(ledger["strict_source_value_for_alpha"], "open")
        self.assertFalse(ledger["zero_knob_claimed"])

    def test_physical_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertFalse(boundary["B_ACTION_01_closed"])
        self.assertFalse(boundary["B_QFT_02_closed"])
        self.assertEqual(boundary["physical_gates"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_packets"], {"accepted": 0, "total": 3})
        self.assertEqual(boundary["physical_rows"], {"accepted": 0, "total": 7})


if __name__ == "__main__":
    unittest.main()
