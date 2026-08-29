from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "direct_finite_source_continuum.packet.json"


class DirectFiniteSourceContinuumRealizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="ascii"))

    def test_finite_associated_bundle_has_identity_synthesis(self) -> None:
        realization = self.packet["direct_internal_realization"]
        self.assertEqual(realization["fiber_dimension"], 96)
        self.assertEqual(realization["projector"], "P_int=I_(E_F)")
        self.assertEqual(realization["projector_rank"], 96)
        self.assertEqual(realization["complement"], "Q_int=0")
        self.assertEqual(realization["complement_rank"], 0)

    def test_internal_complement_tail_and_error_vanish(self) -> None:
        realization = self.packet["direct_internal_realization"]
        response = self.packet["exact_response"]
        self.assertEqual(realization["feshbach_complement_term"], "0")
        self.assertEqual(realization["omitted_internal_modes"], 0)
        self.assertEqual(realization["internal_truncation_error"], "0")
        self.assertEqual(response["internal_quadrature_error"], "0")
        self.assertEqual(response["internal_interpolation_error"], "0")
        self.assertEqual(response["internal_Galerkin_error"], "0")
        self.assertFalse(realization["external_spacetime_is_finite_cutoff"])

    def test_causal_operator_keeps_the_lorentzian_symbol(self) -> None:
        causal = self.packet["causal_operator"]
        self.assertEqual(causal["Higgs_Yukawa_order"], 0)
        self.assertTrue(causal["principal_symbol_unchanged"])
        self.assertTrue(causal["globally_hyperbolic_base"])
        self.assertTrue(causal["causal_support"])
        self.assertEqual(causal["advanced_Green_map"], "E_t^+")
        self.assertEqual(causal["retarded_Green_map"], "E_t^-")

    def test_exact_product_square_recovers_the_physical_response(self) -> None:
        response = self.packet["exact_response"]
        self.assertEqual(response["operator_dimension_witness"], 192)
        self.assertEqual(response["finite_neutral_square"], "D_phys(0)^2=I96")
        self.assertEqual(
            response["first_variation"],
            "d_t D_dir(t,h)^2|0=h^2 I tensor H_phys",
        )
        self.assertEqual(response["H_phys_rank"], 96)
        self.assertEqual(response["H_phys_frobenius_norm_squared"], "768")
        self.assertFalse(response["scalar_Higgs_potential_Hessian_claimed"])

    def test_signed_action_remains_distinct_from_positive_repair(self) -> None:
        action = self.packet["classical_action_and_bv"]
        self.assertFalse(action["objects_identified"])
        self.assertTrue(action["BRST_nilpotent"])
        self.assertTrue(action["classical_action_BRST_closed"])
        self.assertEqual(action["classical_BV_master_equation"], "(S_BV,S_BV)=0")
        self.assertTrue(action["fermion_Yukawa_classical_sublane_closed"])
        self.assertFalse(action["quantum_master_equation_closed"])

    def test_direct_route_closes_without_relabeling_the_HYM_route(self) -> None:
        route = self.packet["route_classification"]
        boundary = self.packet["physical_boundary"]
        self.assertTrue(route["direct_route"].startswith("closed"))
        self.assertEqual(route["HYM_route"], "open")
        self.assertFalse(route["HYM_Galerkin_map_required_for_direct_route"])
        self.assertTrue(route["HYM_Galerkin_map_required_for_HYM_provenance"])
        self.assertFalse(route["routes_identified"])
        self.assertTrue(boundary["direct_finite_source_continuum_realized"])
        self.assertFalse(boundary["physical_q79_HYM_endpoint_selected"])
        self.assertFalse(boundary["B_GEO_01_closed_as_written"])

    def test_values_parameters_and_q79_acceptance_do_not_move(self) -> None:
        ledger = self.packet["parameter_ledger"]
        boundary = self.packet["physical_boundary"]
        self.assertEqual(ledger["new_observed_construction_inputs"], 0)
        self.assertEqual(ledger["new_fitted_coefficients"], 0)
        self.assertEqual(ledger["new_internal_Galerkin_coefficients"], 0)
        self.assertFalse(ledger["numerical_h_selected"])
        self.assertFalse(ledger["numerical_t_selected"])
        self.assertFalse(boundary["strict_numerical_values_selected"])
        self.assertFalse(boundary["held_out_scalar_prediction"])
        self.assertEqual(self.packet["physical_packets_accepted"], 0)
        self.assertEqual(self.packet["physical_packets_total"], 3)
        self.assertEqual(self.packet["physical_rows_accepted"], 0)
        self.assertEqual(self.packet["physical_rows_total"], 7)


if __name__ == "__main__":
    unittest.main()
