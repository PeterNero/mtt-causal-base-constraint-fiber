from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AffineZeroSectionActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(
            (ROOT / "affine_zero_section_action.packet.json").read_text(
                encoding="ascii"
            )
        )

    def test_pure_cotangent_action_needs_a_zero_section_term(self) -> None:
        theorem = self.packet["general_theorem"]
        self.assertEqual(theorem["unshifted_cotangent_action"], "S_cot=<lambda,Phi>")
        self.assertEqual(theorem["unshifted_critical_multiplier"], "lambda=0")
        self.assertEqual(
            self.packet["minimal_affine_action"]["field_only_zero_section_action"],
            "U_ell(n,k)=-ell(n)",
        )

    def test_upper_linear_action_pulls_back_to_lower_quadratic(self) -> None:
        minimal = self.packet["minimal_affine_action"]
        finite = self.packet["finite_action"]
        self.assertEqual(minimal["graph_restricted_action"], "S_lower(k)=ell(psi(k))")
        self.assertEqual(finite["graph_restricted_action"], "1/2 Re<k,H_resp k>")
        self.assertEqual(finite["graph_pullback_samples"], 5)

    def test_nonzero_pressure_is_one_classical_projective_class(self) -> None:
        projective = self.packet["projective_pressure"]
        ledger = self.packet["parameter_ledger"]
        self.assertTrue(projective["zero_branch_separate"])
        self.assertEqual(projective["nonzero_unoriented_classical_classes"], 1)
        self.assertEqual(projective["continuous_dimensionless_shape_parameters"], 0)
        self.assertEqual(ledger["new_continuous_pressure_shape_parameters"], 0)
        self.assertEqual(ledger["unselected_overall_physical_action_scale"], 1)

    def test_real_action_rank_and_inertia_are_exact(self) -> None:
        finite = self.packet["finite_action"]
        self.assertEqual(
            (finite["real_bordered_dimension"], finite["real_bordered_rank"], finite["real_bordered_kernel"]),
            (160, 112, 48),
        )
        self.assertEqual(
            finite["real_bordered_inertia_at_positive_normalized_pressure"],
            {"positive": 48, "negative": 64, "zero": 48},
        )

    def test_finite_action_does_not_promote_physical_values(self) -> None:
        provenance = self.packet["source_provenance"]
        self.assertTrue(provenance["one_finite_algebraic_action_object_constructed"])
        self.assertFalse(provenance["physical_endpoint_selects_this_action"])
        self.assertEqual(provenance["physical_same_root_status"], "OPEN")
        self.assertEqual(self.packet["parameter_ledger"]["strict_charged_magnitude_values_remaining"], 9)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
