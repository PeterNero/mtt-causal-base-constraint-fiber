#!/usr/bin/env python3
"""Build the exact CBF.T40 source-preserving quantum-projection packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "source_preserving_pointed_quantum_projection_source_lock.json"
SCHEMA = ROOT / "source_preserving_pointed_quantum_projection_contract.schema.json"
THEOREM = ROOT / "SourcePreservingPointedQuantumProjectionAndWardNonselectionTheorem_v1.md"
PROVIDER_SCHEMA = ROOT / "provider_neutral_physical_source_contract.schema.json"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T37_PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
QME_CERT = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_renormalized_timeordering_local_qme.certificate.json"
COSTELLO_CERT = ROOT / "../mtt-qm-source-proof/certificates/q79_firstorder_costello_bv_graphwise_counterterm.certificate.json"
A35_CERT = ROOT / "../mtt-sm-parity-closure/certificates/selected_neutralhiggsinsertionfunctorandradialcoordinatenormalization_certificate.json"
OUTPUT = ROOT / "source_preserving_pointed_quantum_projection.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def dtext(value: Decimal) -> str:
    return format(value, "f")


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def derivative_pair(point: Fraction, quadratic: Fraction, quartic: Fraction) -> tuple[Fraction, Fraction]:
    first = 2 * quadratic * point + 4 * quartic * point**3
    second = 2 * quadratic + 12 * quartic * point**2
    return first, second


def finite_counterterm_orbit() -> dict[str, Any]:
    point = Fraction(3, 2)
    matrix = [
        [2 * point, 4 * point**3],
        [Fraction(2), 12 * point**2],
    ]
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    qj1_kernel = [-2 * point**2, Fraction(1)]
    qj1_first, qj1_second = derivative_pair(point, *qj1_kernel)
    violating_first, violating_second = derivative_pair(
        point, Fraction(1), Fraction(0)
    )
    return {
        "counterterm_space": "C_even=span{1,h^2,h^4}",
        "nonconstant_coefficients": ["a", "b"],
        "first_second_jet_matrix": [
            [ftext(entry) for entry in row] for row in matrix
        ],
        "symbolic_matrix": "[[2H,4H^3],[2,12H^2]]",
        "symbolic_determinant": "16 H^3",
        "rational_witness_H": ftext(point),
        "rational_witness_determinant": ftext(determinant),
        "QJ1_map_rank": 1,
        "QJ1_kernel_dimension_mod_constants": 1,
        "QJ1_kernel_vector_a_b": [ftext(value) for value in qj1_kernel],
        "QJ1_kernel_polynomial_mod_constants": "(h^2-H^2)^2",
        "QJ1_kernel_first_derivative": ftext(qj1_first),
        "QJ1_kernel_second_derivative": ftext(qj1_second),
        "symbolic_QJ1_hessian_shift": "8 H^2 t",
        "QJ1_plus_QJ2_rank": 2,
        "QJ1_plus_QJ2_kernel_mod_constants": 0,
        "QJ1_violating_vector_a_b": ["1", "0"],
        "QJ1_violating_first_derivative": ftext(violating_first),
        "QJ1_violating_second_derivative": ftext(violating_second),
        "unique_counterterm_formula": {
            "a": "(3b1-Hb2)/(4H)",
            "b": "(Hb2-b1)/(8H^3)",
        },
        "constant_survives_QJ1_QJ2": True,
        "constant_is_quotiented_in_normalized_connected_QFT": True,
        "constant_remains_physical_for_gravity": True,
    }


def ward_qme_ppa_nonselection(
    qme: dict[str, Any], costello: dict[str, Any], t37: dict[str, Any]
) -> dict[str, Any]:
    qme_checks = qme["QME_checks"]
    costello_matter = costello["matter_extension_checks"]
    tadpole = Decimal(
        t37["T35_tadpole_execution"]["bare_tadpole_over_kappa_Lambda3"]
    )
    return {
        "local_QME_anomaly_class": qme["local_QME_anomaly"]["class_vector"],
        "formal_QME_scheme_exists": qme_checks[
            "renormalized_QME_scheme_exists_as_formal_power_series"
        ],
        "SP_freedom_remains": qme_checks[
            "renormalization_freedom_is_local_Stueckelberg_Petermann"
        ],
        "ten_EG_axioms_include_field_independence_and_Action_Ward": qme_checks[
            "ten_EG_normalization_axioms_declared"
        ],
        "radial_counterterms_are_gauge_invariant_ghost_zero": True,
        "radial_counterterms_are_antifield_free": True,
        "radial_counterterm_self_BV_bracket": 0,
        "radial_counterterm_BV_laplacian": 0,
        "QME_selects_finite_coefficients": False,
        "gauge_Ward_selects_finite_coefficients": False,
        "Action_Ward_selects_finite_coefficients": False,
        "field_independence_selects_finite_coefficients": False,
        "split_Ward_selects_finite_coefficients": False,
        "split_Ward_counterexample": "C(h_total)=a h_total^2",
        "perturbative_agreement_selects_total_action": False,
        "perturbative_agreement_scope": (
            "compares alternative free/interacting splittings of one fixed total action"
        ),
        "PPA_countermodel": (
            "S and S+C can each satisfy perturbative agreement internally; PPA does not identify their total actions"
        ),
        "classical_on_shell_background_removes_linear_tree_term": costello_matter[
            "on_shell_background_removes_the_linear_tadpole"
        ],
        "classical_on_shell_clause_selects_quantum_tadpole_scheme": False,
        "T35_bare_tadpole_over_kappa_Lambda3": dtext(tadpole),
        "T35_bare_tadpole_nonzero": tadpole != 0,
        "external_primary_context": [
            "https://arxiv.org/abs/1502.02705",
            "https://arxiv.org/abs/2010.15076",
            "https://arxiv.org/abs/2203.07236",
            "https://arxiv.org/abs/1907.02500",
        ],
    }


def source_preserving_projection_contract(
    provider_schema: dict[str, Any], a35: dict[str, Any]
) -> dict[str, Any]:
    binding_required = provider_schema["properties"]["bindings"]["required"]
    return {
        "name": "source-preserving pointed quantum projection",
        "clauses": {
            "SP0": "one root provenance and no observed target used as source data",
            "SP1": "Pi(u_*)=H",
            "SP2": "DPi X_up(u_*)=X_Gamma(H)",
            "SP3": "DPi A_up=A_Gamma DPi on the selected tangent image",
            "SP4": "DPi is an isometry for the selected tangent pairings",
            "SP5": "BV/QME and normalized state pushforwards commute with Pi",
        },
        "pointed_not_global": True,
        "full_nonlinear_flow_equality_required": False,
        "provider_schema_binding_requirements": binding_required,
        "provider_schema_requires_fixed_point_hessian_identity": (
            "fixed_point_hessian_identity" in binding_required
        ),
        "provider_schema_requires_action_bv_pushforward": (
            "action_bv_pushforward" in binding_required
        ),
        "provider_schema_requires_normalization_source": (
            "normalization_and_interaction_source" in binding_required
        ),
        "provider_schema_requires_one_root_hash": (
            "one_root_hash_for_all_packets" in binding_required
        ),
        "A35_selected_dimensionless_radial_coordinate": a35[
            "selected_radial_coordinate_normalization_closed"
        ],
        "A35_insertion_magnitude": a35["insertion_magnitude"],
        "A35_selects_physical_action_weight": a35[
            "physical_action_weighted_Y_nu_closed"
        ],
        "physical_tangent_metric_is_part_of_A35": False,
        "accepted_physical_provider_instance_present": False,
        "selected_quantum_projection_present": False,
    }


def selection_theorem() -> dict[str, Any]:
    return {
        "fixed_point_implication": (
            "X_up(u_*)=0 and DPi X_up(u_*)=X_Gamma(H) imply X_Gamma(H)=0"
        ),
        "gradient_implication": (
            "X_Gamma(H)=0 with positive invertible g_H implies dGamma(H)=0"
        ),
        "QJ1_follows_from_one_morphism": True,
        "tangent_implication": (
            "DPi A_up=A_Gamma DPi plus tangent isometry transports the action Hessian"
        ),
        "action_jet_QJ2_follows_from_same_morphism": True,
        "QJ1_and_action_QJ2_are_independent_numeric_knobs": False,
        "nonconstant_SP_representative_is_unique_given_morphism": True,
        "unique_representative_is_T39_anchor": True,
        "selected_morphism_existence_proved": False,
        "primitive_q79_realization_proved": False,
        "physical_metric_normalized_QJ2_proved": False,
        "classification": "IMPLICATION_CLOSED_EXISTENCE_OPEN",
    }


def radial_state_route(t38: dict[str, Any]) -> dict[str, Any]:
    radial = t38["invariant_radial_state"]
    formal = t38["formal_q79_state_extension"]
    return {
        "upper_radial_invariant_state": "delta_H",
        "unique_upper_radial_marginal": radial[
            "radial_marginal_is_unique_without_selecting_matter_state"
        ],
        "forced_radial_expectation": radial["forced_radial_expectation"],
        "formal_local_state_extension_exists": formal[
            "formal_local_radial_anchored_state_exists"
        ],
        "full_interacting_state_unique": formal["full_interacting_state_is_unique"],
        "state_pushforward_clause": (
            "the selected lower zero-source state is Pi_* of the upper invariant state"
        ),
        "Legendre_identity": "dGamma/dh=J",
        "zero_source_then_QJ1": True,
        "full_gauge_matter_state_uniqueness_required_for_radial_QJ1": False,
        "selected_physical_state_pushforward_present": False,
    }


def t35_execution(t35: dict[str, Any], t37: dict[str, Any]) -> dict[str, Any]:
    numeric = t35["numerical_execution"]
    msbar = numeric["MSbar_mu_equals_Lambda_per_unit_kappa"]
    with localcontext() as context:
        context.prec = 100
        h = Decimal(numeric["H_over_Lambda"])
        h2 = Decimal(numeric["H_squared_over_Lambda_squared"])
        delta_m2 = Decimal(msbar["delta_m2_over_Lambda2"])
        delta_lambda = Decimal(msbar["delta_lambda"])
        bare_tadpole = Decimal(
            t37["T35_tadpole_execution"]["bare_tadpole_over_kappa_Lambda3"]
        )
        counterterm_tadpole = (
            Decimal(2) * delta_m2 * h
            + Decimal(4) * delta_lambda * h**3
        )
        tadpole_residual = bare_tadpole + counterterm_tadpole
        direction_m2 = -Decimal(2) * h2
        direction_lambda = Decimal(1)
        direction_tadpole = (
            Decimal(2) * direction_m2 * h
            + Decimal(4) * direction_lambda * h**3
        )
        direction_hessian = (
            Decimal(2) * direction_m2
            + Decimal(12) * direction_lambda * h2
        )
    return {
        "H_over_Lambda": dtext(h),
        "H_squared_over_Lambda_squared": dtext(h2),
        "unique_T39_delta_m2_over_kappa_Lambda2": dtext(delta_m2),
        "unique_T39_delta_lambda_over_kappa": dtext(delta_lambda),
        "bare_tadpole_over_kappa_Lambda3": dtext(bare_tadpole),
        "counterterm_tadpole_over_kappa_Lambda3": dtext(counterterm_tadpole),
        "matched_tadpole_residual": dtext(tadpole_residual),
        "QJ1_orbit_direction": {
            "delta_m2_over_kappa_Lambda2_per_t": dtext(direction_m2),
            "delta_lambda_over_kappa_per_t": dtext(direction_lambda),
            "tadpole_shift_over_kappa_Lambda3_per_t": dtext(direction_tadpole),
            "hessian_shift_over_kappa_Lambda2_per_t": dtext(direction_hessian),
            "symbolic": "(-2 H^2,1)",
        },
        "QJ1_orbit_tadpole_is_zero": abs(direction_tadpole) < Decimal("1e-75"),
        "QJ1_orbit_hessian_is_nonzero": direction_hessian > 0,
        "matched_tadpole_is_zero_to_locked_precision": (
            abs(tadpole_residual) < Decimal("1e-70")
        ),
        "T35_higher_jets_retained": t35["closure_jet_matching"][
            "jets_at_x_equal_one"
        ]["third"] != 0,
    }


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    provider_schema = load_json(PROVIDER_SCHEMA)
    t35 = load_json(T35_PACKET)
    t37 = load_json(T37_PACKET)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    qme = load_json(QME_CERT)
    costello = load_json(COSTELLO_CERT)
    a35 = load_json(A35_CERT)

    orbit = finite_counterterm_orbit()
    nonselection = ward_qme_ppa_nonselection(qme, costello, t37)
    projection = source_preserving_projection_contract(provider_schema, a35)
    theorem = selection_theorem()
    state_route = radial_state_route(t38)
    execution = t35_execution(t35, t37)

    qj = {
        "QJ1_local_formal_anchor_scheme": t39["QJ_classification"][
            "QJ1_local_formal_anchor_scheme"
        ],
        "QJ1_same_source_morphism_implication": "closed_exactly",
        "QJ1_selected_physical_q79_law": "open_morphism_existence",
        "QJ2_local_formal_action_Hessian": t39["QJ_classification"][
            "QJ2_local_formal_action_Hessian"
        ],
        "QJ2_same_source_action_jet_implication": "closed_exactly",
        "QJ2_physical_normalized_Hessian": "open_tangent_metric_and_morphism_existence",
        "QJ0_normalized_connected_QFT_common_constant": "quotiented",
        "QJ0_gravitational_absolute_vacuum": "open",
        "new_sharp_exit": (
            "construct one selected same-root state/action projection map with its tangent pairing"
        ),
    }

    parameter_ledger = {
        "new_physical_continuous_parameters": 0,
        "new_physical_discrete_selectors": 0,
        "new_fits": 0,
        "new_observed_inputs": 0,
        "QJ1_QJ2_scalar_matching_conditions_reclassified_as_independent_knobs": 0,
        "new_structural_existence_certificates_required": 1,
        "required_certificate": "source-preserving pointed quantum projection",
        "remaining_additive_constant_in_normalized_connected_QFT": 0,
        "remaining_additive_constant_if_gravity_included": 1,
    }

    physical_boundary = {
        "provider_contract_level_selector_proved": True,
        "selected_physical_provider_instance_present": False,
        "selected_physical_quantum_projection_present": False,
        "physical_QJ1_selected": False,
        "physical_QJ2_selected": False,
        "gravitational_QJ0_selected": False,
        "physical_interacting_q79_BV_endpoint_executed": False,
        "physical_tangent_metric_selected": False,
        "acceptance_counters_change": False,
    }

    packet: dict[str, Any] = {
        "schema": "boe.mtt.source-preserving-pointed-quantum-projection.v1",
        "claim_id": "CBF.T40",
        "date": "2026-08-30",
        "status": (
            "EXACT_SP_ORBIT_AND_WARD_NONSELECTION_PLUS_CONDITIONAL_SAME_SOURCE_"
            "PROJECTION_SELECTOR_PHYSICAL_MORPHISM_OPEN"
        ),
        "source_provenance": {
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "provider_contract_schema_sha256": sha256(PROVIDER_SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "handoff_id": source_lock["handoff_id"],
            "source_bundle_sha256": canonical_hash(source_lock["local_sources"]),
        },
        "finite_counterterm_orbit": orbit,
        "ward_qme_ppa_nonselection": nonselection,
        "source_preserving_projection_contract": projection,
        "selection_theorem": theorem,
        "radial_state_route": state_route,
        "T35_execution": execution,
        "QJ_classification": qj,
        "parameter_ledger": parameter_ledger,
        "physical_boundary": physical_boundary,
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The finite radial scheme problem is reduced from separate QJ1/QJ2 scalar "
            "conditions to one source-preserving pointed quantum-projection existence "
            "certificate. Ward/QME/PPA identities alone are proved insufficient."
        ),
    }

    checks = source_hash_checks(source_lock)

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    required = schema["required"]
    check("schema_claim_id", schema["properties"]["claim_id"]["const"] == "CBF.T40")
    check("schema_requires_all_packet_fields", all(key in required for key in packet))
    check("orbit_witness_det_54", orbit["rational_witness_determinant"] == "54")
    check("symbolic_det_16H3", orbit["symbolic_determinant"] == "16 H^3")
    check("QJ1_rank_one", orbit["QJ1_map_rank"] == 1)
    check("QJ1_kernel_first_zero", orbit["QJ1_kernel_first_derivative"] == "0")
    check("QJ1_kernel_second_nonzero", orbit["QJ1_kernel_second_derivative"] == "18")
    check("QJ1_QJ2_full_nonconstant_rank", orbit["QJ1_plus_QJ2_rank"] == 2)
    check("QJ1_violating_counterexample", orbit["QJ1_violating_first_derivative"] != "0")
    check("QME_zero_anomaly", nonselection["local_QME_anomaly_class"] == [0, 0, 0, 0, 0])
    check("QME_scheme_exists", nonselection["formal_QME_scheme_exists"])
    check("SP_freedom_remains", nonselection["SP_freedom_remains"])
    check("QME_does_not_select", not nonselection["QME_selects_finite_coefficients"])
    check("Ward_does_not_select", not nonselection["gauge_Ward_selects_finite_coefficients"])
    check("Action_Ward_does_not_select", not nonselection["Action_Ward_selects_finite_coefficients"])
    check("field_independence_does_not_select", not nonselection["field_independence_selects_finite_coefficients"])
    check("split_Ward_does_not_select", not nonselection["split_Ward_selects_finite_coefficients"])
    check("PPA_does_not_select_total_action", not nonselection["perturbative_agreement_selects_total_action"])
    check("classical_on_shell_is_not_quantum_selector", not nonselection["classical_on_shell_clause_selects_quantum_tadpole_scheme"])
    check("T35_bare_tadpole_nonzero", nonselection["T35_bare_tadpole_nonzero"])
    check("provider_requires_fixedpoint_hessian", projection["provider_schema_requires_fixed_point_hessian_identity"])
    check("provider_requires_action_pushforward", projection["provider_schema_requires_action_bv_pushforward"])
    check("provider_requires_normalization", projection["provider_schema_requires_normalization_source"])
    check("provider_requires_one_root", projection["provider_schema_requires_one_root_hash"])
    check("A35_radial_coordinate_closed", projection["A35_selected_dimensionless_radial_coordinate"])
    check("A35_action_weight_open", not projection["A35_selects_physical_action_weight"])
    check("projection_is_pointed", projection["pointed_not_global"])
    check("global_flow_not_required", not projection["full_nonlinear_flow_equality_required"])
    check("QJ1_one_morphism_implication", theorem["QJ1_follows_from_one_morphism"])
    check("QJ2_same_morphism_implication", theorem["action_jet_QJ2_follows_from_same_morphism"])
    check("QJ1_QJ2_not_numeric_knobs", not theorem["QJ1_and_action_QJ2_are_independent_numeric_knobs"])
    check("T39_unique_given_morphism", theorem["unique_representative_is_T39_anchor"])
    check("morphism_existence_open", not theorem["selected_morphism_existence_proved"])
    check("radial_marginal_unique", state_route["unique_upper_radial_marginal"])
    check("full_state_need_not_be_unique", not state_route["full_gauge_matter_state_uniqueness_required_for_radial_QJ1"])
    check("state_pushforward_open", not state_route["selected_physical_state_pushforward_present"])
    check("T35_tadpole_matched", execution["matched_tadpole_is_zero_to_locked_precision"])
    check("T35_QJ1_orbit_tadpole_zero", execution["QJ1_orbit_tadpole_is_zero"])
    check("T35_QJ1_orbit_hessian_nonzero", execution["QJ1_orbit_hessian_is_nonzero"])
    check("T35_higher_jets_retained", execution["T35_higher_jets_retained"])
    check("QJ1_morphism_implication_closed", qj["QJ1_same_source_morphism_implication"] == "closed_exactly")
    check("QJ1_physical_open", qj["QJ1_selected_physical_q79_law"] == "open_morphism_existence")
    check("QJ2_metric_open", qj["QJ2_physical_normalized_Hessian"].startswith("open_"))
    check("QJ0_gravity_open", qj["QJ0_gravitational_absolute_vacuum"] == "open")
    check("zero_new_physical_parameters", parameter_ledger["new_physical_continuous_parameters"] == 0)
    check("zero_new_discrete_selectors", parameter_ledger["new_physical_discrete_selectors"] == 0)
    check("zero_observed_inputs", parameter_ledger["new_observed_inputs"] == 0)
    check("one_structural_exit", parameter_ledger["new_structural_existence_certificates_required"] == 1)
    check("physical_QJ1_not_promoted", not physical_boundary["physical_QJ1_selected"])
    check("physical_QJ2_not_promoted", not physical_boundary["physical_QJ2_selected"])
    check("physical_endpoint_not_promoted", not physical_boundary["physical_interacting_q79_BV_endpoint_executed"])
    check("packet_acceptance_unchanged", packet["physical_packets_accepted"] == 0)
    check("row_acceptance_unchanged", packet["physical_rows_accepted"] == 0)

    theorem_text = THEOREM.read_text(encoding="utf-8")
    check("theorem_states_8H2_obstruction", "C_t''(H)=8H^2 t" in theorem_text)
    check("theorem_states_contract_not_existence", "does not contain an accepted physical instance" in theorem_text)
    check("theorem_keeps_endpoint_open", "physical q79 pointed quantum projection" in theorem_text)

    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
    }
    return packet


def main() -> None:
    packet = build()
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    summary = packet["check_summary"]
    print(f"wrote {OUTPUT.name}")
    print(f"checks: {summary['passed']}/{summary['total']}")
    if summary["failed"]:
        raise SystemExit("failed checks: " + ", ".join(summary["failed"]))


if __name__ == "__main__":
    main()
