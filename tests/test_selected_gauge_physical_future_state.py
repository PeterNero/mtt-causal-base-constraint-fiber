from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "selected_gauge_physical_future_state.packet.json"


def parse_matrix(payload: list[list[str]]) -> list[list[Fraction]]:
    return [[Fraction(value) for value in row] for row in payload]


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


class SelectedGaugePhysicalFutureStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_selected_gauge_physical_future_state.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_builder_checks_pass(self) -> None:
        self.assertTrue(all(self.packet["checks"].values()))
        self.assertEqual(self.packet["check_summary"]["failed"], [])

    def test_generalized_mass_spectrum_is_exact(self) -> None:
        spectrum = self.packet["generalized_mass_witness"]["generalized_spectrum"]
        self.assertEqual(spectrum, {"0": 9, "1/6": 2, "4/15": 1})

    def test_broken_and_unbroken_projectors_are_exact(self) -> None:
        witness = self.packet["generalized_mass_witness"]
        broken = parse_matrix(witness["broken_projector"])
        unbroken = parse_matrix(witness["unbroken_projector"])
        self.assertEqual(multiply(broken, broken), broken)
        self.assertEqual(multiply(unbroken, unbroken), unbroken)
        self.assertEqual(sum(broken[i][i] for i in range(12)), 3)
        self.assertEqual(sum(unbroken[i][i] for i in range(12)), 9)

    def test_photon_and_Z_are_source_derived(self) -> None:
        witness = self.packet["generalized_mass_witness"]
        self.assertEqual(witness["photon_Z_K_pairing"], "0")
        self.assertFalse(witness["absolute_common_mass_factor_selected"])
        reduction = self.packet["electroweak_mass_reduction"]
        self.assertFalse(reduction["measured_weak_angle_used"])
        self.assertFalse(reduction["absolute_mass_prediction"])

    def test_massless_BRST_quotient_has_rank_two(self) -> None:
        complex_ = self.packet["BRST_mode_reduction"]["massless_complex"]
        self.assertEqual(complex_["physical_cohomology_dimension"], 2)
        self.assertEqual(parse_matrix(complex_["closed_ghost_zero_Gram"]), [[1, 0, 0], [0, 1, 0], [0, 0, 0]])

    def test_massive_BRST_quotient_has_rank_three(self) -> None:
        complex_ = self.packet["BRST_mode_reduction"]["massive_complex"]
        self.assertEqual(complex_["physical_cohomology_dimension"], 3)
        self.assertEqual(parse_matrix(complex_["closed_ghost_zero_Gram"]), [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]])

    def test_broken_phase_gauge_count_is_twenty_seven(self) -> None:
        reduction = self.packet["BRST_mode_reduction"]
        self.assertEqual(reduction["massless_physical_polarizations"], 18)
        self.assertEqual(reduction["massive_physical_polarizations"], 9)
        self.assertEqual(reduction["total_physical_gauge_polarizations"], 27)
        self.assertFalse(reduction["Goldstone_directions_counted_as_independent_Higgs_particles"])

    def test_broken_longitudinal_mixing_is_regular(self) -> None:
        witness = self.packet["BRST_mode_reduction"]["broken_longitudinal_Goldstone_mixing"]
        self.assertEqual(witness["gauge_orbit_output"], ["5", "0"])
        self.assertEqual(witness["physical_longitudinal_output"], ["0", "5"])
        self.assertEqual(witness["zero_momentum_m_positive_matrix"], [["0", "1"], ["1", "0"]])

    def test_massless_zero_mode_adds_no_selector(self) -> None:
        ir = self.packet["massless_IR_zero_mode"]
        self.assertEqual(ir["zero_spectral_projection_on_L2_R3"], 0)
        self.assertEqual(ir["radial_covariance_integrand_power"], 1)
        self.assertFalse(ir["new_zero_mode_state_parameter"])
        self.assertFalse(ir["compact_Cauchy_harmonic_modes_covered"])

    def test_transverse_projector_samples_are_rank_two(self) -> None:
        samples = self.packet["massless_IR_zero_mode"]["samples"]
        self.assertEqual([sample["rank"] for sample in samples], [2, 2])
        self.assertEqual([sample["trace"] for sample in samples], ["2", "2"])

    def test_future_oscillator_complex_structure_is_positive(self) -> None:
        witness = self.packet["oscillator_witness"]
        self.assertEqual(witness["positive_metric_SJ"], [["5", "0"], ["0", "1/5"]])
        self.assertEqual(witness["past_metric_minus_SJ"], [["-5", "0"], ["0", "-1/5"]])

    def test_gauge_state_is_selected_at_declared_tier(self) -> None:
        state = self.packet["future_positive_CCR_state"]
        self.assertTrue(state["positive"])
        self.assertTrue(state["normalized"])
        self.assertTrue(state["pure"])
        self.assertTrue(state["Hadamard_on_static_flat_branch"])
        self.assertTrue(state["BRST_descended"])
        self.assertEqual(state["new_state_parameter_count"], 0)

    def test_only_radial_Higgs_factor_remains(self) -> None:
        factors = self.packet["broken_phase_seed_factorization"]
        self.assertTrue(factors["Weyl_factor"]["selected"])
        self.assertTrue(factors["gauge_physical_factor"]["selected"])
        self.assertFalse(factors["radial_Higgs_factor"]["selected"])
        self.assertEqual(factors["missing_selected_factors"], 1)
        self.assertFalse(factors["full_product_seed_selected"])

    def test_parameters_and_physical_counters_remain_honest(self) -> None:
        parameters = self.packet["parameter_ledger"]
        self.assertEqual(parameters["new_observed_inputs"], 0)
        self.assertEqual(parameters["new_fitted_parameters"], 0)
        self.assertEqual(parameters["new_continuous_state_selectors"], 0)
        boundary = self.packet["physical_boundary"]
        self.assertEqual((boundary["physical_packets_accepted"], boundary["physical_packets_total"]), (0, 3))
        self.assertEqual((boundary["physical_rows_accepted"], boundary["physical_rows_total"]), (0, 7))

    def test_independent_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "verify_selected_gauge_physical_future_state.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
