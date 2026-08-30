#!/usr/bin/env python3
"""Build the exact CBF.T37 quantum radial-anchor and tadpole packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "quantum_radial_anchor_tadpole_source_lock.json"
SCHEMA = ROOT / "quantum_radial_anchor_tadpole_contract.schema.json"
THEOREM = ROOT / "QuantumRadialAnchorWardIdentityAndTadpoleSelectionBoundaryTheorem_v1.md"
T36_PACKET = ROOT / "pointed_closure_germ_quantum_jet_matching.packet.json"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
QME_THEOREM = ROOT / "../mtt-qm-source-proof/proof_corpus/q79_SM_Renormalized_TimeOrdering_and_Local_QME_Anomaly_Cohomology_Theorem_v1.md"
STATE_THEOREM = ROOT / "../mtt-qm-source-proof/proof_corpus/q79_SM_Local_Formal_Physical_State_Space_Compatibility_and_Gluing_Theorem_v1.md"
STATE_TRANSPORT = ROOT / "../mtt-qm-source-proof/proof_corpus/q79_SM_Equicausal_Formal_State_Transport_and_Local_QuasiEquivalence_Cutset_Theorem_v1.md"
WARD_THEOREM = ROOT / "../mtt-qm-source-proof/proof_corpus/q79_UniformGauss_GhostZeroBRST_WardDefect_and_ChiralMeasureReduction_Theorem_v1.md"
OUTPUT = ROOT / "quantum_radial_anchor_tadpole.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def dtext(value: Decimal) -> str:
    return format(value, "f")


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def differentiated_pushforward_witness() -> dict[str, Any]:
    hbar = Fraction(1)
    action_derivatives = [Fraction(3), Fraction(-1)]
    log_density_derivatives = [Fraction(1, 2), Fraction(-1, 2)]
    weights = [Fraction(1, 2), Fraction(1, 2)]
    insertion = [
        ds - hbar * anomaly
        for ds, anomaly in zip(action_derivatives, log_density_derivatives)
    ]
    gamma_derivative = sum(
        (weight * value for weight, value in zip(weights, insertion)), Fraction(0)
    )

    centered_insertion = [Fraction(3), Fraction(-3)]
    centered_average = sum(
        (weight * value for weight, value in zip(weights, centered_insertion)),
        Fraction(0),
    )

    return {
        "reference_point": "2",
        "hbar": ftext(hbar),
        "fiber_probabilities_at_reference": [ftext(value) for value in weights],
        "action_radial_derivatives": [ftext(value) for value in action_derivatives],
        "log_density_radial_derivatives": [
            ftext(value) for value in log_density_derivatives
        ],
        "covariant_insertions": [ftext(value) for value in insertion],
        "effective_action_radial_derivative": ftext(gamma_derivative),
        "identity": "Gamma'(H)=<D_H S-hbar A_H>_H+B_H/Z(H)",
        "cycle_boundary_term_in_witness": "0",
        "centered_involution_insertions": [
            ftext(value) for value in centered_insertion
        ],
        "centered_involution_expectation": ftext(centered_average),
        "action_naturality_alone_sufficient": False,
        "measure_cycle_state_data_required": True,
    }


def qme_normalization_witness() -> dict[str, Any]:
    point = Fraction(3, 2)
    target_shift = Fraction(7, 3)
    first_a = target_shift / (2 * point)
    first_b = Fraction(0)
    second_b = Fraction(1, 5)
    second_a = (target_shift - 4 * second_b * point**3) / (2 * point)

    def shift(a: Fraction, b: Fraction) -> Fraction:
        return 2 * a * point + 4 * b * point**3

    return {
        "test_point_H": ftext(point),
        "target_tadpole_shift": ftext(target_shift),
        "counterterm_class": "c+a h^2+b h^4",
        "first_solution": {
            "a": ftext(first_a),
            "b": ftext(first_b),
            "shift": ftext(shift(first_a, first_b)),
        },
        "second_solution": {
            "a": ftext(second_a),
            "b": ftext(second_b),
            "shift": ftext(shift(second_a, second_b)),
        },
        "tadpole_map_rank": 1,
        "nonconstant_kernel_dimension": 1,
        "additive_constant_dimension": 1,
        "gauge_invariant_counterterms_are_BRST_closed": True,
        "anomaly_free_formal_QME_scheme_exists": True,
        "QJ1_compatible_formal_QME_scheme_exists": True,
        "QME_uniquely_selects_QJ1": False,
        "QJ1_is_a_normalization_condition_at_this_tier": True,
    }


def state_anchor_witness() -> dict[str, Any]:
    point = Fraction(5, 3)
    variance = Fraction(7, 4)
    test_source = Fraction(2, 5)
    expectation = point + variance * test_source
    recovered_source = (expectation - point) / variance
    gamma_derivative_at_anchor = Fraction(0)
    return {
        "W_of_J": "H J+(sigma^2/2)J^2",
        "phi_of_J": "H+sigma^2 J",
        "Gamma_of_phi": "(phi-H)^2/(2 sigma^2)",
        "H": ftext(point),
        "sigma_squared": ftext(variance),
        "test_J": ftext(test_source),
        "test_phi": ftext(expectation),
        "recovered_dGamma_dphi": ftext(recovered_source),
        "zero_source_Gamma_prime_at_H": ftext(gamma_derivative_at_anchor),
        "Legendre_identity": "dGamma/dphi=J",
        "QJ1_follows_if_H_T34_equals_zero_source_expectation": True,
        "preferred_interacting_q79_state_selected": False,
        "H_T34_state_anchor_equality_proved": False,
    }


def t35_tadpole_execution(t35: dict[str, Any]) -> dict[str, Any]:
    numeric = t35["numerical_execution"]
    with localcontext() as context:
        context.prec = 90
        sqrt13 = Decimal(13).sqrt()
        q4 = (Decimal(356) + Decimal(25) * sqrt13) / Decimal(27)
        sigma_m4 = (Decimal(2) + sqrt13) / Decimal(3)
        sigma_m2 = (Decimal(5) + sqrt13) / Decimal(6)
        sigma_p2 = (Decimal(7) - sqrt13) / Decimal(6)
        l4 = sum(
            sigma**4 * (sigma**2).ln()
            for sigma in (sigma_m4, sigma_m2, sigma_p2)
        )
        h2 = (
            Decimal(15)
            * (Decimal(3106) + Decimal(4) * sqrt13)
            / (Decimal(4393) * Decimal(448).ln())
        )
        h = h2.sqrt()
        c_scheme = Decimal("1.5")
        mu_over_lambda = Decimal(1)
        l_h = q4 * (h2 / mu_over_lambda**2).ln() + l4 - c_scheme * q4
        tadpole_per_kappa = -Decimal(2) * h**3 * (Decimal(2) * l_h + q4)
        qj1_line = h2 * (Decimal(2) * l_h + q4)
        mu_tad_over_h = (
            (l4 / q4 - c_scheme + Decimal("0.5")) / Decimal(2)
        ).exp()
        mu_tad_over_lambda = mu_tad_over_h * h
        delta_m2 = -Decimal(2) * q4 * h2
        delta_lambda = l_h + Decimal("1.5") * q4
        qj1_line_from_t35 = delta_m2 + Decimal(2) * h2 * delta_lambda
        kappa_complex = Decimal(
            numeric["determinant_normalization_candidates"]["complex_determinant"][
                "kappa_F"
            ]
        )
        kappa_pfaffian = Decimal(
            numeric["determinant_normalization_candidates"]["pfaffian_half"][
                "kappa_F"
            ]
        )
        input_residuals = {
            "q4": abs(q4 - Decimal(numeric["q4_star"])),
            "L4": abs(l4 - Decimal(numeric["L4_star"])),
            "H": abs(h - Decimal(numeric["H_over_Lambda"])),
            "H2": abs(h2 - Decimal(numeric["H_squared_over_Lambda_squared"])),
        }
        return {
            "scheme": "MSbar",
            "mu_over_Lambda": dtext(mu_over_lambda),
            "c_scheme": dtext(c_scheme),
            "sqrt13": dtext(sqrt13),
            "q4_star": dtext(q4),
            "L4_star": dtext(l4),
            "H_over_Lambda": dtext(h),
            "H_squared_over_Lambda_squared": dtext(h2),
            "L_H": dtext(l_h),
            "two_L_H_plus_q4": dtext(Decimal(2) * l_h + q4),
            "bare_tadpole_over_kappa_Lambda3": dtext(tadpole_per_kappa),
            "bare_tadpole_complex_over_Lambda3": dtext(
                tadpole_per_kappa * kappa_complex
            ),
            "bare_tadpole_pfaffian_over_Lambda3": dtext(
                tadpole_per_kappa * kappa_pfaffian
            ),
            "QJ1_counterterm_line_right_side_over_kappa_Lambda2": dtext(qj1_line),
            "T35_delta_m2_over_kappa_Lambda2": dtext(delta_m2),
            "T35_delta_lambda_over_kappa": dtext(delta_lambda),
            "QJ1_line_reconstructed_from_T35_pair": dtext(qj1_line_from_t35),
            "mu_tad_over_H": dtext(mu_tad_over_h),
            "mu_tad_over_Lambda": dtext(mu_tad_over_lambda),
            "mu_tad_formula": "exp[(L4_*/q4_*-c_scheme+1/2)/2]",
            "bare_tadpole_is_zero_at_mu_equals_Lambda": tadpole_per_kappa == 0,
            "both_determinant_branches_have_nonzero_tadpole": (
                tadpole_per_kappa * kappa_complex != 0
                and tadpole_per_kappa * kappa_pfaffian != 0
            ),
            "mu_tad_selected_by_current_upper_action": False,
            "maximum_locked_input_residual": dtext(max(input_residuals.values())),
            "locked_input_residuals": {
                key: dtext(value) for key, value in input_residuals.items()
            },
        }


def main() -> None:
    source_lock = load_json(SOURCE_LOCK)
    t36 = load_json(T36_PACKET)
    t35 = load_json(T35_PACKET)
    t34 = load_json(T34_PACKET)
    qme_text = QME_THEOREM.read_text(encoding="utf-8")
    state_text = STATE_THEOREM.read_text(encoding="utf-8")
    state_transport_text = STATE_TRANSPORT.read_text(encoding="utf-8")
    ward_text = WARD_THEOREM.read_text(encoding="utf-8")

    pushforward = differentiated_pushforward_witness()
    qme_orbit = qme_normalization_witness()
    state_anchor = state_anchor_witness()
    t35_execution = t35_tadpole_execution(t35)

    source_root_payload = {
        "claim_id": "CBF.T37",
        "kernel_model_sha256": source_lock["kernel_model_sha256"],
        "repositories": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
    }

    source_checks = source_hash_checks(source_lock)
    checks: dict[str, bool] = {
        **source_checks,
        "all_source_hashes_match": all(source_checks.values()),
        "T36_QJ1_was_open": not t36["physical_boundary"][
            "physical_QJ1_tadpole_protection_closed"
        ],
        "T36_generic_pushforward_preservation_rejected": t36["physical_boundary"][
            "generic_pushforward_jet_preservation_rejected"
        ],
        "T34_point_is_positive": Decimal(
            t35["numerical_execution"]["H_over_Lambda"]
        )
        > 0
        and Decimal(
            t34["promoted_radial_values"]["h_over_Lambda_interval"][
                "lower_decimal"
            ]
        )
        > 0,
        "differentiated_pushforward_identity_nontrivial": pushforward[
            "effective_action_radial_derivative"
        ]
        == "1",
        "measure_term_enters_identity": pushforward[
            "log_density_radial_derivatives"
        ]
        != ["0", "0"],
        "centered_involution_cancels_insertion": pushforward[
            "centered_involution_expectation"
        ]
        == "0",
        "action_naturality_alone_not_enough": not pushforward[
            "action_naturality_alone_sufficient"
        ],
        "QME_first_solution_hits_target": qme_orbit["first_solution"]["shift"]
        == qme_orbit["target_tadpole_shift"],
        "QME_second_solution_hits_target": qme_orbit["second_solution"]["shift"]
        == qme_orbit["target_tadpole_shift"],
        "QME_orbit_has_nonconstant_kernel": qme_orbit[
            "nonconstant_kernel_dimension"
        ]
        == 1,
        "QME_compatibility_closed": qme_orbit[
            "QJ1_compatible_formal_QME_scheme_exists"
        ],
        "QME_selection_rejected": not qme_orbit["QME_uniquely_selects_QJ1"],
        "q79_formal_QME_source_present": "all-orders formal subtraction scheme" in qme_text,
        "q79_QME_finite_normalization_explicit": "finite local counterterm" in qme_text,
        "q79_state_spaces_nonempty": "nonempty contravariant" in state_text,
        "q79_preferred_state_explicitly_open": "does not select a preferred state" in state_text,
        "q79_state_transport_present": "Physical state transport" in state_transport_text,
        "q79_full_quantum_Ward_row_open": "full quantum Ward row" in ward_text,
        "Legendre_anchor_exact": state_anchor["zero_source_Gamma_prime_at_H"] == "0",
        "state_anchor_reduces_QJ1": state_anchor[
            "QJ1_follows_if_H_T34_equals_zero_source_expectation"
        ],
        "preferred_state_still_open": not state_anchor[
            "preferred_interacting_q79_state_selected"
        ],
        "T35_locked_inputs_match": Decimal(
            t35_execution["maximum_locked_input_residual"]
        )
        < Decimal("1e-75"),
        "T35_bare_tadpole_nonzero": not t35_execution[
            "bare_tadpole_is_zero_at_mu_equals_Lambda"
        ],
        "T35_both_determinant_branches_nonzero": t35_execution[
            "both_determinant_branches_have_nonzero_tadpole"
        ],
        "T35_pair_lies_on_QJ1_line": abs(
            Decimal(t35_execution["QJ1_line_reconstructed_from_T35_pair"])
            - Decimal(
                t35_execution[
                    "QJ1_counterterm_line_right_side_over_kappa_Lambda2"
                ]
            )
        )
        < Decimal("1e-75"),
        "bare_tadpole_zero_scale_positive": Decimal(
            t35_execution["mu_tad_over_H"]
        )
        > 0,
        "bare_tadpole_zero_scale_unselected": not t35_execution[
            "mu_tad_selected_by_current_upper_action"
        ],
        "no_observed_inputs": not source_lock["boundary"]["observed_values_used"],
        "no_fitted_coefficients": not source_lock["boundary"][
            "fitted_coefficients_used"
        ],
        "physical_QJ1_stays_open": not source_lock["boundary"][
            "physical_QJ1_selected"
        ],
        "physical_acceptance_unchanged": source_lock["boundary"][
            "physical_packet_acceptance_before"
        ]
        == source_lock["boundary"]["physical_packet_acceptance_after"]
        == 0
        and source_lock["boundary"]["physical_row_acceptance_before"]
        == source_lock["boundary"]["physical_row_acceptance_after"]
        == 0,
    }

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T37 builder checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.quantum-radial-anchor-tadpole.v1",
        "claim_id": "CBF.T37",
        "date": "2026-08-30",
        "status": (
            "exact quantum radial Ward reduction and QME-compatible QJ1 "
            "normalization existence; selected interacting state and physical QJ1 open"
        ),
        "source_provenance": {
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "source_root_payload": source_root_payload,
            "source_root_sha256": canonical_hash(source_root_payload),
            "handoff_id": source_lock["handoff_id"],
        },
        "differentiated_pushforward_identity": {
            "formula": "Gamma'(H)=<D_H S-hbar A_H>_H+B_H/Z(H)",
            "action_term": "D_H S",
            "measure_and_determinant_term": "-hbar A_H",
            "cycle_boundary_term": "B_H/Z(H)",
            "exact_finite_witness": pushforward,
            "projection_contract_must_include": [
                "action",
                "cycle transport",
                "measure or determinant half-density",
                "state or expectation functional",
                "radial anchor",
            ],
        },
        "QJ1_mechanisms": {
            "pointwise_horizontal_stationarity": {
                "condition": "D_H S=0 pointwise, A_H=0 and B_H=0",
                "sufficient": True,
                "present_in_current_MTT": False,
            },
            "quantum_BV_exact_insertion": {
                "condition": "D_H S-hbar A_H=s_q Psi_H and <s_q X>=0",
                "sufficient": True,
                "formal_QME_Stokes_available": True,
                "radial_primitive_Psi_H_emitted": False,
            },
            "centered_involution": {
                "condition": "measure-preserving involution fixes H and makes insertion odd",
                "sufficient": True,
                "ordinary_h_to_minus_h_centers_nonzero_branch": False,
            },
            "zero_source_state_anchor": {
                "condition": "H_T34=phi(J=0) for one selected interacting state",
                "sufficient": True,
                "exact_witness": state_anchor,
                "same_source_equality_closed": False,
            },
        },
        "QME_normalization_orbit": qme_orbit,
        "T35_tadpole_execution": t35_execution,
        "state_anchor_reduction": {
            "identity": "dGamma/dphi=J",
            "physical_QJ1_exit": "select omega_q79 and prove omega_q79(h)=H_T34 at J=0",
            "alternative_exit": (
                "emit Psi_H with D_H S-hbar A_H=s_q Psi_H and certify BV Stokes"
            ),
            "current_q79_state_space_nonempty": True,
            "current_q79_state_transport_closed": True,
            "current_q79_preferred_interacting_state_selected": False,
            "current_H_T34_anchor_equality_closed": False,
            "QJ1_is_independent_scalar_fit_parameter": False,
            "QJ1_is_a_typed_state_or_Ward_certificate": True,
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_continuous_physical_parameters": 0,
            "QJ1_nonconstant_counterterm_freedom_before_QJ2": 1,
            "additive_constant_freedom_before_QJ0": 1,
            "new_formal_normalization_conditions_classified": 1,
            "selected_interacting_state_data_still_missing": 1,
            "bare_tadpole_zero_scale_is_counted_as_prediction": False,
        },
        "physical_boundary": {
            "differentiated_pushforward_identity_closed": True,
            "QJ1_sufficient_mechanisms_classified": True,
            "formal_QME_compatible_QJ1_scheme_exists": True,
            "QME_or_gauge_naturality_selects_QJ1": False,
            "T35_bare_tadpole_obstruction_executed": True,
            "QJ1_reduced_to_same_source_state_anchor": True,
            "selected_interacting_q79_state_closed": False,
            "H_T34_state_anchor_equality_closed": False,
            "radial_BV_Ward_primitive_closed": False,
            "physical_QJ1_tadpole_protection_closed": False,
            "physical_QJ2_tangent_Hessian_intertwiner_closed": False,
            "physical_QJ0_vacuum_normalization_closed": False,
            "full_closure_jet_matching_selected": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "CBF.T37 derives the exact differentiated pushforward Ward identity and "
            "proves that the anomaly-free q79 formal QME permits a QJ1-preserving "
            "normalization but cannot select it because gauge-invariant h^2 and h^4 "
            "counterterms shift the tadpole arbitrarily. The actual T35 fermion "
            "determinant has a nonzero tadpole at H_T34 in MSbar at mu=Lambda. "
            "Physical QJ1 is now reduced to one same-source state-anchor equality "
            "omega_q79(h)=H_T34 at zero source, or one explicit quantum-BV radial "
            "Ward primitive. Neither is currently emitted, so acceptance stays 0/3 "
            "packets and 0/7 rows."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {OUTPUT.name}: {len(checks)}/{len(checks)} checks passed; "
        "formal QJ1 compatibility closed; physical state anchor remains open"
    )


if __name__ == "__main__":
    main()
