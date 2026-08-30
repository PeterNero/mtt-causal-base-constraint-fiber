from __future__ import annotations

import json
import unittest
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

import build_selected_radial_higgs_future_state as builder


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "selected_radial_higgs_future_state.packet.json"
LOCK = ROOT / "selected_radial_higgs_future_state_source_lock.json"
THEOREM = ROOT / "SelectedRadialHiggsFutureStateAndCompleteFreeSeedTheorem_v1.md"


class SelectedRadialHiggsFutureStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        getcontext().prec = 80
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_01_builder_has_no_failed_checks(self) -> None:
        rebuilt = builder.build()
        self.assertEqual(rebuilt["check_summary"]["failed"], [])
        self.assertGreaterEqual(rebuilt["check_summary"]["passed"], 100)

    def test_02_all_locked_sources_match(self) -> None:
        for group in ("construction_sources", "comparison_sources"):
            for source in self.lock[group]:
                path = (ROOT / source["path"]).resolve()
                self.assertTrue(path.is_file())
                self.assertEqual(builder.sha256(path), source["sha256"])

    def test_03_exact_radial_algebra(self) -> None:
        witness, checks = builder.radial_algebra_witness()
        self.assertTrue(all(checks.values()))
        self.assertEqual(witness["q2_star"]["rational"], "14/3")
        self.assertEqual(witness["q2_star"]["sqrt13_coefficient"], "1/3")
        self.assertEqual(witness["q4_star"]["rational"], "356/27")
        self.assertEqual(witness["R_star_equals_2q2_over_q4"]["rational"], "3106/4393")

    def test_04_square_completion_and_derivatives(self) -> None:
        radial = self.packet["exact_radial_action"]
        self.assertEqual(radial["exact_square_completion"], "P_*(h)-P_*(H_*)=q4_*(h^2-H_*^2)^2")
        self.assertEqual(radial["derivatives_at_H_star"]["first"], "0")
        self.assertEqual(radial["derivatives_at_H_star"]["second"], "16c q2_*")
        self.assertIn("8c q2_* eta^2", radial["expansion"])

    def test_05_canonical_mass_is_positive_and_exact(self) -> None:
        hessian = self.packet["canonical_radial_hessian"]
        self.assertEqual(hessian["mass_squared"], "m_h^2=8c")
        self.assertEqual(hessian["mass_squared_over_Lambda_squared"], "120/log(448)")
        self.assertTrue(hessian["strictly_positive"])
        self.assertFalse(hessian["physical_pole_mass_claimed"])

    def test_06_checkpoint_identity(self) -> None:
        tau = Decimal(448).ln() / Decimal(15)
        mass2 = Decimal(120) / Decimal(448).ln()
        self.assertLess(abs(tau * mass2 - Decimal(8)), Decimal("1e-70"))
        mass = mass2.sqrt()
        self.assertGreaterEqual(mass, Decimal("4.433586065447802232784618009020"))
        self.assertLessEqual(mass, Decimal("4.433586065447802232784618009021"))

    def test_07_reflection_positivity_witness(self) -> None:
        witness, checks = builder.reflection_positivity_witness()
        self.assertTrue(all(checks.values()))
        self.assertEqual(witness["OS_gram_rank"], 1)
        self.assertEqual(witness["test_quadratic_form"], "1/10")
        self.assertEqual(witness["future_phase_sample"]["imaginary"], "-4/5")

    def test_08_oscillator_witness(self) -> None:
        witness, checks = builder.oscillator_witness()
        self.assertTrue(all(checks.values()))
        covariance = [[Fraction(entry) for entry in row] for row in witness["pure_covariance_one_half_SJ"]]
        self.assertEqual(4 * builder.determinant_2(covariance), 1)

    def test_09_same_physical_radial_line(self) -> None:
        source = self.packet["same_branch_source"]
        self.assertIn("A51 one-Higgs", source["finite_source"])
        self.assertIn("h D_phys(t)", source["radial_coordinate"])
        self.assertFalse(source["literal_T23_h_equals_Lambda_imposed"])
        self.assertFalse(source["same_symbol_used_without_source_map"])

    def test_10_future_state_is_selected_without_zero_mode(self) -> None:
        state = self.packet["future_positive_CCR_state"]
        self.assertTrue(state["positive"])
        self.assertTrue(state["normalized"])
        self.assertTrue(state["pure"])
        self.assertTrue(state["Hadamard_on_static_flat_branch"])
        self.assertEqual(state["new_state_parameter_count"], 0)
        self.assertFalse(state["p_zero_selector_required"])

    def test_11_background_marginal_and_fluctuation_are_separate(self) -> None:
        separation = self.packet["type_separation"]
        self.assertFalse(separation["T38_used_as_fluctuation_covariance"])
        self.assertFalse(separation["source_modulus_t_varied_as_particle"])
        self.assertFalse(separation["Goldstones_counted_as_radial_particles"])
        self.assertIn("remains open", separation["T40_G1_role"])

    def test_12_complete_free_seed(self) -> None:
        seed = self.packet["complete_free_seed"]
        self.assertTrue(seed["Weyl_factor"]["selected"])
        self.assertTrue(seed["gauge_physical_factor"]["selected"])
        self.assertTrue(seed["radial_Higgs_factor"]["selected"])
        self.assertEqual(seed["total_bosonic_physical_polarizations"], 28)
        self.assertEqual(seed["missing_selected_factors"], 0)
        self.assertTrue(seed["full_product_seed_selected_at_declared_tier"])

    def test_13_canonical_formal_lift_is_instantiated_but_bounded(self) -> None:
        lift = self.packet["canonical_formal_lift"]
        self.assertTrue(lift["complete_seed_premise_now_met"])
        self.assertTrue(lift["formal_lift_choice_removed"])
        self.assertEqual(lift["recursion"], "psi_n=-h r_n")
        self.assertFalse(lift["upper_action_selected_full_BV_map"])
        self.assertFalse(lift["fixed_coupling_positive_state"])

    def test_14_g2_ledger_advances_only_free_seed(self) -> None:
        ledger = self.packet["G2_clause_ledger"]
        self.assertEqual(ledger["G2a_flat_branch_free_radial_Higgs_state"], "closed by T48")
        self.assertIn("closed by T48", ledger["G2b_selected_complete_free_product_seed"])
        self.assertEqual(ledger["G2b_selected_upper_action_and_full_BV_map"], "open")
        self.assertEqual(ledger["top_level_physical_G2"], "open")

    def test_15_parameters_boundaries_and_theorem_text(self) -> None:
        parameters = self.packet["parameter_ledger"]
        boundary = self.packet["physical_boundary"]
        text = THEOREM.read_text(encoding="utf-8")
        self.assertEqual(parameters["new_observed_inputs"], 0)
        self.assertEqual(parameters["new_fitted_parameters"], 0)
        self.assertEqual(parameters["new_continuous_state_selectors"], 0)
        self.assertEqual(boundary["physical_gates_accepted"], 0)
        self.assertEqual(boundary["physical_packets_accepted"], 0)
        self.assertEqual(boundary["physical_rows_accepted"], 0)
        self.assertIn("The next obstruction is not another free vacuum", text)


if __name__ == "__main__":
    unittest.main()
