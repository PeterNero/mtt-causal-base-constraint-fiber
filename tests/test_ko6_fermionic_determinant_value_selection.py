from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"


class KO6FermionicDeterminantValueSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_KO6_polarization_does_not_supply_statistics(self) -> None:
        polarization = self.packet["KO6_polarization"]
        self.assertEqual(polarization["dimensions"], {"minus": 48, "plus": 48})
        self.assertEqual(polarization["statistics_source"], "Grassmann fermion fields in CBF.T25")
        self.assertFalse(polarization["KO_chirality_used_as_statistics"])

    def test_chiral_determinant_is_exact(self) -> None:
        operator = self.packet["chiral_finite_operator"]
        self.assertEqual(operator["response_branch_multiplicities"], {"-4": 16, "-2": 16, "2": 16})
        self.assertEqual(operator["determinant_identity"], "det(B^*B)=Delta(t)^32")
        self.assertEqual(operator["Delta"], "(1-2t)(1-t)(1+t)")

    def test_neutral_component_selects_one_stationary_root(self) -> None:
        chamber = self.packet["neutral_invertible_chamber"]
        coordinate = self.packet["selected_coordinate"]
        self.assertEqual(chamber["singular_walls"], ["-1", "1/2", "1"])
        self.assertEqual(chamber["connected_component"], "(-1,1/2)")
        self.assertEqual(coordinate["expression"], "(1-sqrt(13))/6")
        self.assertEqual(coordinate["minimal_polynomial"], "3t^2-t-1")
        self.assertTrue(coordinate["unique_global_minimum_in_neutral_component"])

    def test_three_dimensionless_values_are_emitted(self) -> None:
        values = self.packet["dimensionless_branch_values"]
        branches = values["ordered_by_response_eigenvalue"]
        self.assertEqual(branches["-4"]["expression"], "(2+sqrt(13))/3")
        self.assertEqual(branches["-2"]["expression"], "(5+sqrt(13))/6")
        self.assertEqual(branches["2"]["expression"], "(7-sqrt(13))/6")
        self.assertEqual(values["strict_order"], "sigma_-4>sigma_-2>sigma_+2>0")
        self.assertFalse(values["observed_values_used"])
        self.assertFalse(values["fitted_coefficients_used"])

    def test_one_scale_values_are_conditional_not_masses(self) -> None:
        values = self.packet["conditional_one_scale_values"]
        self.assertEqual(values["formula"], "m_lambda=h sigma_lambda")
        self.assertEqual(values["new_dimensionless_shape_parameters"], 0)
        self.assertEqual(values["inherited_common_scale_count"], 1)
        self.assertFalse(values["common_scale_h_selected_numerically"])
        self.assertFalse(values["sector_assignment_selected"])
        self.assertFalse(values["SM_mass_claimed"])

    def test_external_modes_prevent_premature_vacuum_promotion(self) -> None:
        obstruction = self.packet["external_mode_obstruction"]
        self.assertEqual(obstruction["zero_external_mode_stationarity"], "3t^2-t-1=0")
        self.assertEqual(obstruction["large_external_mode_leading_stationarity"], "-2+6t=0, hence t=1/3")
        self.assertFalse(obstruction["common_stationary_coordinate_for_all_external_modes"])
        self.assertFalse(obstruction["finite_selected_coordinate_is_final_4D_vacuum"])

    def test_parameter_ledger_has_no_observed_or_fitted_inputs(self) -> None:
        ledger = self.packet["parameter_ledger"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_dimensionless_continuous_parameters"], 0)
        self.assertEqual(ledger["new_dimensionful_primitives"], 0)
        self.assertEqual(ledger["inherited_optional_common_scale_h"], 1)

    def test_physical_boundary_is_explicit(self) -> None:
        boundary = self.packet["physical_boundary"]
        self.assertTrue(boundary["finite_KO6_chiral_determinant_profile_closed"])
        self.assertTrue(boundary["neutral_chamber_coordinate_closed"])
        self.assertTrue(boundary["exact_dimensionless_branch_values_closed"])
        self.assertFalse(boundary["full_four_dimensional_determinant_closed"])
        self.assertFalse(boundary["renormalized_QFT_vacuum_closed"])
        self.assertFalse(boundary["overall_SI_scale_closed"])
        self.assertFalse(boundary["SM_mass_generation_map_closed"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
