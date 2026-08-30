from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "future_cone_spectral_polarization.packet.json"


class FutureConeSpectralPolarizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            [sys.executable, "build_future_cone_spectral_polarization.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_and_builder_checks(self) -> None:
        self.assertEqual(self.packet["claim_id"], "CBF.T45")
        self.assertEqual(self.packet["check_summary"]["failed"], [])
        self.assertEqual(self.packet["check_summary"]["passed"], self.packet["check_summary"]["total"])

    def test_independent_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_future_cone_spectral_polarization.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CBF.T45 independent verification passed", result.stdout)

    def test_t_star_is_exact(self) -> None:
        t_star = self.packet["flat_direct_branch"]["t_star"]
        self.assertEqual(Fraction(t_star["rational"]), Fraction(1, 6))
        self.assertEqual(Fraction(t_star["sqrt13_coefficient"]), Fraction(-1, 6))

    def test_mass_gap_is_exact_and_positive(self) -> None:
        gap = self.packet["exact_gap"]
        minimum = gap["minimum_internal_gap"]
        self.assertEqual(Fraction(minimum["rational"]), Fraction(7, 6))
        self.assertEqual(Fraction(minimum["sqrt13_coefficient"]), Fraction(-1, 6))
        self.assertEqual(gap["strict_order"], "1-2t_star > 1-t_star > 1+t_star > 0")

    def test_future_and_past_projectors_are_complementary(self) -> None:
        polarization = self.packet["future_spectral_polarization"]
        future = polarization["future_projector_diagonal"]
        past = polarization["past_projector_diagonal"]
        self.assertEqual(sum(future), 48)
        self.assertEqual(sum(past), 48)
        self.assertEqual([a + b for a, b in zip(future, past)], [1] * 96)
        self.assertEqual([a * b for a, b in zip(future, past)], [0] * 96)

    def test_96_typing_is_guarded(self) -> None:
        guard = self.packet["future_spectral_polarization"]["typing_guard"]
        self.assertIn("48 physical Weyl labels", guard)
        self.assertIn("not the separate KO6 96", guard)

    def test_charge_conjugation_exchanges_polarizations(self) -> None:
        polarization = self.packet["future_spectral_polarization"]
        future = polarization["future_projector_diagonal"]
        past = polarization["past_projector_diagonal"]
        permutation = polarization["charge_conjugation_permutation"]
        self.assertEqual([future[permutation[i]] for i in range(96)], past)

    def test_half_line_selects_future_projector(self) -> None:
        half_line = self.packet["half_line_calderon_equivalence"]
        self.assertEqual(half_line["calderon_projector"], "C_+=P_fut")
        self.assertEqual(half_line["decaying_mode_count_in_finite_normal_form"], 48)
        self.assertTrue(half_line["auxiliary_half_line_is_not_internal_circle_or_physical_time"])

    def test_positive_hessian_does_not_select_energy_sign(self) -> None:
        result = self.packet["positive_hessian_nonselection"]
        self.assertEqual(result["damped_mode_count_in_finite_normal_form"], 96)
        self.assertFalse(result["selects_future_polarization"])
        self.assertIn("oriented first-order charge", result["required_extra_structure"])

    def test_free_state_is_selected_only_on_flat_branch(self) -> None:
        state = self.packet["quasifree_initial_state"]
        self.assertTrue(state["selected_free_initial_state_on_declared_branch"])
        self.assertTrue(state["Hadamard_on_static_flat_branch"])
        self.assertFalse(state["preferred_state_on_all_globally_hyperbolic_backgrounds"])

    def test_T44_is_scalarized_without_nonperturbative_overclaim(self) -> None:
        scalar = self.packet["T44_scalarization"]
        self.assertEqual(scalar["equal_source_identity"], "Z_fut[V,V]=1")
        self.assertTrue(scalar["local_formal_initial_state_is_selected"])
        self.assertFalse(scalar["nonperturbative_scalar_determinant_computed"])
        self.assertFalse(scalar["relative_determinant_line_holonomy_fixed"])

    def test_time_reversal_is_complement_not_binary_root(self) -> None:
        result = self.packet["time_reversal_and_binary_root"]
        self.assertTrue(result["two_complementary_oriented_polarizations"])
        self.assertTrue(result["selected_time_orientation_chooses_future_member_on_this_branch"])
        self.assertFalse(result["binary_root_selects_arrow_or_vacuum"])

    def test_only_free_initial_G2_subclause_closes(self) -> None:
        subclauses = self.packet["gate_ledger"]["G2_subclauses"]
        self.assertEqual(subclauses["free_initial_state"], "closed on flat branch")
        self.assertEqual(subclauses["interacting_pushforward"], "open")
        self.assertEqual(subclauses["fixed_coupling_continuum"], "open")
        self.assertEqual(self.packet["gate_ledger"]["physical_T41_gate_count"], "0/3")

    def test_no_new_fit_or_continuous_state_parameter(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_inputs"], 0)
        self.assertEqual(ledger["new_fitted_parameters"], 0)
        self.assertEqual(ledger["new_continuous_state_selectors"], 0)
        self.assertEqual(ledger["new_thermal_parameters"], 0)
        self.assertEqual(ledger["inherited_unresolved_radial_scale"], "H")

    def test_physical_acceptance_counters_do_not_move(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertEqual((boundary["physical_packets_accepted"], boundary["physical_packets_total"]), (0, 3))
        self.assertEqual((boundary["physical_rows_accepted"], boundary["physical_rows_total"]), (0, 7))


if __name__ == "__main__":
    unittest.main()
