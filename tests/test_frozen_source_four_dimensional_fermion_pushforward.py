from __future__ import annotations

import json
import subprocess
import sys
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

import build_frozen_source_four_dimensional_fermion_pushforward as t35


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"


class FrozenSourceFourDimensionalPushforwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "build_frozen_source_four_dimensional_fermion_pushforward.py"],
            cwd=ROOT,
            check=True,
        )
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_claim_and_checks(self) -> None:
        self.assertEqual(self.packet["claim_id"], "CBF.T35")
        self.assertTrue(all(self.packet["checks"].values()))

    def test_grassmann_base_change_witness(self) -> None:
        witness = self.packet["source_freeze_base_change"]["witness"]
        self.assertTrue(witness["grassmann_base_change_exact"])
        self.assertEqual(
            witness["grassmann_direct_at_t_star"],
            witness["grassmann_polynomial_at_t_star"],
        )

    def test_schur_base_change_witness(self) -> None:
        witness = self.packet["source_freeze_base_change"]["witness"]
        self.assertTrue(witness["high_block_invertible"])
        self.assertTrue(witness["schur_base_change_exact"])
        self.assertEqual(
            witness["schur_direct_at_t_star"],
            witness["schur_formula_at_t_star"],
        )

    def test_matching_matrix_is_invertible(self) -> None:
        determinant = Decimal(
            self.packet["numerical_execution"]["matching_matrix_determinant_over_Lambda3"]
        )
        self.assertGreater(determinant, 0)

    def test_scheme_cancellation(self) -> None:
        numeric = self.packet["numerical_execution"]
        self.assertLess(Decimal(numeric["maximum_scheme_residual"]), Decimal("1e-70"))
        self.assertLess(
            Decimal(numeric["maximum_universal_formula_residual"]), Decimal("1e-70")
        )

    def test_independent_corrected_loop(self) -> None:
        with localcontext() as context:
            context.prec = 70
            sqrt13 = Decimal(13).sqrt()
            sigmas = [
                (Decimal(2) + sqrt13) / Decimal(3),
                (Decimal(5) + sqrt13) / Decimal(6),
                (Decimal(7) - sqrt13) / Decimal(6),
            ]
            q4 = sum(value**4 for value in sigmas)
            l4 = sum(value**4 * (value * value).ln() for value in sigmas)
            tau = Decimal(448).ln() / Decimal(15)
            ratio = (Decimal(3106) + Decimal(4) * sqrt13) / Decimal(4393)
            h_ref = (ratio / tau).sqrt()
            h = Decimal("0.73") * h_ref
            mu = Decimal("1.91")
            c_scheme = Decimal("0.44")
            kappa = Decimal("0.081")
            corrected = t35.corrected_loop(
                h, h_ref, mu, c_scheme, kappa, q4, l4
            )
            universal = t35.universal_remainder(h, h_ref, kappa, q4)
            self.assertLess(abs(corrected - universal), Decimal("1e-60"))

    def test_zero_through_second_jet_and_higher_jets(self) -> None:
        jets = self.packet["closure_jet_matching"]["jets_at_x_equal_one"]
        self.assertEqual(jets, {"value": 0, "first": 0, "second": 0, "third": -16, "fourth": -64})

    def test_determinant_normalizations_are_discrete_pair(self) -> None:
        candidates = self.packet["numerical_execution"]["determinant_normalization_candidates"]
        with localcontext() as context:
            context.prec = 90
            complex_kappa = Decimal(candidates["complex_determinant"]["kappa_F"])
            pfaffian_kappa = Decimal(candidates["pfaffian_half"]["kappa_F"])
            self.assertLess(
                abs(complex_kappa - Decimal(2) * pfaffian_kappa),
                Decimal("1e-78"),
            )

    def test_rg_invariance_is_not_claimed(self) -> None:
        boundary = self.packet["regulator_and_RG_boundary"]
        self.assertTrue(boundary["t_star_preserved_at_one_matching_scale"])
        self.assertFalse(boundary["t_star_proved_RG_fixed"])

    def test_external_regulator_is_not_promoted(self) -> None:
        boundary = self.packet["regulator_and_RG_boundary"]
        self.assertFalse(boundary["selected_external_BV_Laplacian_and_domain"])
        self.assertFalse(boundary["internal_projector_used_as_spacetime_cutoff"])

    def test_no_physical_acceptance_inflation(self) -> None:
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)


if __name__ == "__main__":
    unittest.main()
