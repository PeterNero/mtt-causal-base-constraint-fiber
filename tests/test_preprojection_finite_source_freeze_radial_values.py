from __future__ import annotations

import json
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "preprojection_finite_source_freeze_radial_values.packet.json"


class PreprojectionFiniteSourceFreezeRadialValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_source_freeze_and_joint_variation_are_typed_differently(self) -> None:
        typed = self.packet["typed_source_freeze"]
        self.assertEqual(typed["variational_identity"], "dL_*=i_*^*(d_F L)")
        self.assertFalse(typed["source_equation_in_lower_variation"])
        self.assertTrue(typed["joint_variation_is_a_different_enlarged_model"])
        self.assertTrue(typed["no_double_variation_rule_closed"])

    def test_T30_source_coordinate_and_exact_moments_are_preserved(self) -> None:
        source = self.packet["selected_finite_source"]
        self.assertEqual(
            source["coordinate"]["exact_coefficients"],
            {"rational": "1/6", "sqrt13": "-1/6"},
        )
        self.assertEqual(
            source["q2_star"]["exact_coefficients"],
            {"rational": "14/3", "sqrt13": "1/3"},
        )
        self.assertEqual(
            source["q4_star"]["exact_coefficients"],
            {"rational": "356/27", "sqrt13": "25/27"},
        )
        self.assertFalse(source["proved_physical_preprojection_source"])

    def test_radial_ratio_is_exact(self) -> None:
        ratio = self.packet["selected_finite_source"]["R_star"]
        self.assertEqual(
            ratio["exact_coefficients"],
            {"rational": "3106/4393", "sqrt13": "4/4393"},
        )
        self.assertGreater(Decimal(ratio["interval"]["lower_decimal"]), Decimal("0.7"))
        self.assertLess(Decimal(ratio["interval"]["upper_decimal"]), Decimal("0.8"))

    def test_T23_branch_reproduces_T30_values_without_claiming_stationarity(self) -> None:
        branch = self.packet["T23_metrology_branch"]
        self.assertEqual(branch["normalization"], "h=Lambda=E0=1/L0")
        self.assertFalse(branch["radial_stationarity_claimed"])
        values = branch["branch_values_over_Lambda"]
        self.assertEqual(values["-4"]["expression"], "(2+sqrt(13))/3")
        self.assertEqual(values["-2"]["expression"], "(5+sqrt(13))/6")
        self.assertEqual(values["2"]["expression"], "(7-sqrt(13))/6")

    def test_A53_branch_emits_three_nonzero_certified_values(self) -> None:
        branch = self.packet["A53_radial_stationary_branch"]
        self.assertFalse(branch["premise_selected_by_MTT"])
        h = branch["h_over_Lambda_interval"]
        self.assertLess(Decimal(h["lower_decimal"]), Decimal("1.3211016293754684937241140791005"))
        self.assertGreater(Decimal(h["upper_decimal"]), Decimal("1.3211016293754684937241140791005"))
        values = branch["branch_values_over_Lambda"]
        decimals = {
            key: Decimal(value["interval"]["lower_decimal"])
            for key, value in values.items()
        }
        self.assertGreater(decimals["-4"], decimals["-2"])
        self.assertGreater(decimals["-2"], decimals["2"])
        self.assertGreater(decimals["2"], 0)

    def test_A53_values_match_the_reported_numerical_scale(self) -> None:
        branch = self.packet["A53_radial_stationary_branch"]
        values = branch["branch_values_over_Lambda"]
        expected = {
            "-4": Decimal("2.4685009745210706266233707476685"),
            "-2": Decimal("1.8948013019482695601737424133845"),
            "2": Decimal("0.7474019568026674272744857448165"),
        }
        for key, target in expected.items():
            lower = Decimal(values[key]["interval"]["lower_decimal"])
            upper = Decimal(values[key]["interval"]["upper_decimal"])
            self.assertLess(lower, target)
            self.assertGreater(upper, target)

    def test_radial_curvature_ratio_is_certified_but_not_a_pole_mass(self) -> None:
        branch = self.packet["A53_radial_stationary_branch"]
        self.assertEqual(
            branch["radial_curvature_mass_over_Lambda"],
            "sqrt(120/log(448))",
        )
        interval = branch["radial_curvature_mass_interval"]
        self.assertLess(Decimal(interval["lower_decimal"]), Decimal("4.4335860654478022327846180090205"))
        self.assertGreater(Decimal(interval["upper_decimal"]), Decimal("4.4335860654478022327846180090205"))

    def test_normalization_branches_are_exactly_incompatible(self) -> None:
        comparison = self.packet["branch_comparison"]
        required = comparison["required_T23_stationary_moment_interval"]
        a53 = comparison["A53_moment_interval"]
        self.assertLess(Fraction(required["upper_exact"]), Fraction(a53["lower_exact"]))
        self.assertTrue(comparison["moment_intervals_disjoint"])
        self.assertFalse(comparison["branches_can_be_simultaneous_predictions"])
        self.assertFalse(comparison["common_normalization_creates_additional_family_hierarchy"])

    def test_no_hidden_fit_or_new_parameter_enters(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_continuous_parameters"], 0)
        self.assertEqual(ledger["new_accepted_physical_parameters"], 0)
        self.assertEqual(ledger["branches_selected_by_current_MTT_authority"], 0)

    def test_physical_value_gate_remains_open(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["no_double_variation_typing_closed"])
        self.assertTrue(boundary["fixed_source_exact_values_closed"])
        self.assertFalse(boundary["T30_physical_preprojection_promotion_closed"])
        self.assertFalse(boundary["T30_A53_same_root_closed"])
        self.assertFalse(boundary["normalization_branch_selected"])
        self.assertFalse(boundary["nine_charged_Yukawa_values_closed"])
        self.assertFalse(boundary["held_out_observable_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)

    def test_builder_check_ledger_is_green(self) -> None:
        summary = self.packet["check_summary"]
        self.assertEqual(summary["passed"], summary["total"])
        self.assertEqual(summary["failed"], [])
        self.assertTrue(all(self.packet["checks"].values()))


if __name__ == "__main__":
    unittest.main()
