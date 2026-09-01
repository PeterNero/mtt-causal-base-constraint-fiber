from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.packet.json"


class Q79FourierMukaiDoubleQutritBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_passes_all_checks(self) -> None:
        summary = self.packet["check_summary"]
        self.assertTrue(summary["all_passed"])
        self.assertEqual(summary["total"], 44)

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"all_passed": true', result.stdout)
        self.assertIn('"total": 37', result.stdout)

    def test_fourier_mukai_tensor_typing_is_exact(self) -> None:
        row = self.packet["fourier_mukai_coefficient_typing"]
        self.assertEqual((row["fiber_h0"], row["fiber_h1"]), (3, 0))
        self.assertEqual((row["hidden_rank"], row["endomorphism_rank"], row["adjoint_rank"]), (9, 81, 80))
        self.assertTrue(row["actions_are_distinct"])
        self.assertFalse(row["continuum_mode_truncation_used"])

    def test_weyl_orientation_matches_the_locked_eta9_source(self) -> None:
        checks = self.packet["check_summary"]["checks"]
        self.assertTrue(checks["locked_Weyl_relation_is_exact"])
        self.assertTrue(checks["Ad_X_character_orientation_is_exact"])
        self.assertTrue(checks["Ad_Z_character_orientation_is_exact"])

    def test_double_qutrit_spectrum_is_exact(self) -> None:
        row = self.packet["double_qutrit_koszul_hodge"]
        self.assertEqual(row["degree_zero_spectrum"], {"0": 1, "3": 8, "6": 24, "9": 32, "12": 16})
        self.assertEqual(sum(row["degree_zero_spectrum"].values()), 81)
        self.assertEqual(row["tracefree_gap"], 3)

    def test_all_four_generator_Koszul_compositions_vanish(self) -> None:
        row = self.packet["double_qutrit_koszul_hodge"]
        self.assertTrue(row["all_differential_compositions_zero"])
        self.assertTrue(row["all_hodge_blocks_are_scalar_mode_laplacians"])
        self.assertTrue(row["green_identity_exact"])

    def test_reduced_green_values_are_exact(self) -> None:
        values = self.packet["double_qutrit_koszul_hodge"]["reduced_green_eigenvalues"]
        self.assertEqual([Fraction(value) for value in values], [Fraction(1, 3), Fraction(1, 6), Fraction(1, 9), Fraction(1, 12)])

    def test_cohomology_matches_augmented_rank_pattern(self) -> None:
        row = self.packet["double_qutrit_koszul_hodge"]
        bridge = self.packet["augmented_exterior_bridge"]
        self.assertEqual(row["cohomology_dimensions"], [1, 4, 6, 4, 1])
        self.assertEqual(bridge["rank_sequence"], [1, 4, 6, 4, 1])
        self.assertEqual(bridge["T58_rank_sequence"], [1, 4, 6, 4, 1])

    def test_exterior_bridge_is_basiswise_bijective(self) -> None:
        rows = self.packet["augmented_exterior_bridge"]["rows"]
        self.assertEqual([row["mapping_cone_degree"] for row in rows], [-1, 0, 1, 2, 3])
        for row in rows:
            self.assertEqual(row["domain_dimension"], row["target_dimension"])
            self.assertEqual(row["domain_dimension"], len(row["basis_map"]))

    def test_centered_log_is_not_promoted_to_continuum(self) -> None:
        row = self.packet["centered_log_compiler"]
        self.assertTrue(row["principal_log_is_unique"])
        self.assertTrue(row["all_factors_nonzero"])
        self.assertFalse(row["claims_continuum_derivative"])

    def test_equianharmonic_low_band_has_rank_thirteen(self) -> None:
        row = self.packet["equianharmonic_continuum_cutset"]
        self.assertEqual(row["ground_mode_spectrum"], {"0": 1, "2": 6, "6": 6})
        self.assertEqual(row["lowest_full_band_rank"], 13)
        self.assertEqual(row["strict_band_gap"], 2)
        self.assertEqual(row["triply_degenerate_character_sectors"], 2)

    def test_scalar_fourier_shortcut_is_rejected(self) -> None:
        row = self.packet["equianharmonic_continuum_cutset"]
        self.assertFalse(row["scalar_fourier_low_band_equals_M3"])
        self.assertIn("coefficient algebra", row["conclusion"])

    def test_physical_intertwiner_remains_the_exact_exit(self) -> None:
        bridge = self.packet["augmented_exterior_bridge"]
        self.assertEqual(bridge["selected_physical_intertwiner"], "OPEN")
        self.assertEqual(len(bridge["physical_acceptance_conditions"]), 6)

    def test_physical_counters_do_not_move(self) -> None:
        row = self.packet["physical_boundary"]
        self.assertFalse(row["B_HS_01_closed"])
        self.assertFalse(row["B_GEO_01_closed"])
        self.assertFalse(row["B_OP_01_closed"])
        self.assertEqual(row["physical_rows"], {"accepted": 0, "total": 7})

    def test_no_parameters_or_observations_are_added(self) -> None:
        self.assertTrue(all(value == 0 for value in self.packet["parameter_ledger"].values()))


if __name__ == "__main__":
    unittest.main()
