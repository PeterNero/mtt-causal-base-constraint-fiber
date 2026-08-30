#!/usr/bin/env python3
"""Independently verify the CBF.T40 source-preserving projection packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "source_preserving_pointed_quantum_projection.packet.json"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def close(left: Decimal, right: Decimal, tolerance: str = "1e-70") -> bool:
    return abs(left - right) < Decimal(tolerance)


def main() -> None:
    packet = load_json(PACKET)
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
    theorem_text = THEOREM.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    for index, source in enumerate(source_lock["local_sources"], start=1):
        source_path = (ROOT / source["path"]).resolve()
        check(
            f"locked_source_{index:02d}",
            source_path.is_file() and sha256(source_path) == source["sha256"],
        )

    provenance = packet["source_provenance"]
    check("source_lock_hash", provenance["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("schema_hash", provenance["contract_schema_sha256"] == sha256(SCHEMA))
    check("provider_schema_hash", provenance["provider_contract_schema_sha256"] == sha256(PROVIDER_SCHEMA))
    check("theorem_hash", provenance["theorem_sha256"] == sha256(THEOREM))
    check("handoff_id", provenance["handoff_id"] == source_lock["handoff_id"])
    check("kernel_hash", provenance["kernel_model_sha256"] == source_lock["kernel_model_sha256"])

    check("schema_id", packet["schema"] == schema["properties"]["schema"]["const"])
    check("claim_id", packet["claim_id"] == schema["properties"]["claim_id"]["const"] == "CBF.T40")
    check("schema_closed", schema["additionalProperties"] is False)
    check("schema_required", all(key in packet for key in schema["required"]))
    check("packet_counters", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("row_counters", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)

    orbit = packet["finite_counterterm_orbit"]
    h = Fraction(orbit["rational_witness_H"])
    matrix = [
        [2 * h, 4 * h**3],
        [Fraction(2), 12 * h**2],
    ]
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    check("witness_H", h == Fraction(3, 2))
    check("matrix_rows", orbit["first_second_jet_matrix"] == [[str(v) for v in row] for row in matrix])
    check("determinant_exact", determinant == 16 * h**3 == 54)
    check("determinant_packet", Fraction(orbit["rational_witness_determinant"]) == determinant)

    kernel_a = -2 * h**2
    kernel_b = Fraction(1)
    kernel_first = 2 * kernel_a * h + 4 * kernel_b * h**3
    kernel_second = 2 * kernel_a + 12 * kernel_b * h**2
    check("kernel_vector", [Fraction(v) for v in orbit["QJ1_kernel_vector_a_b"]] == [kernel_a, kernel_b])
    check("kernel_first_zero", kernel_first == 0 == Fraction(orbit["QJ1_kernel_first_derivative"]))
    check("kernel_second_8H2", kernel_second == 8 * h**2 == Fraction(orbit["QJ1_kernel_second_derivative"]))
    check("QJ1_rank", orbit["QJ1_map_rank"] == 1)
    check("QJ1_kernel_dim", orbit["QJ1_kernel_dimension_mod_constants"] == 1)
    check("QJ1_QJ2_rank", orbit["QJ1_plus_QJ2_rank"] == 2)
    check("QJ1_QJ2_kernel", orbit["QJ1_plus_QJ2_kernel_mod_constants"] == 0)

    for value in (Fraction(-5, 3), Fraction(0), Fraction(7, 2)):
        a = -2 * h**2 * value
        b = value
        first = 2 * a * h + 4 * b * h**3
        second = 2 * a + 12 * b * h**2
        check(f"QJ1_line_first_{value}", first == 0)
        check(f"QJ1_line_second_{value}", second == 8 * h**2 * value)

    b1 = Fraction(7, 3)
    b2 = Fraction(-11, 5)
    solved_a = (3 * b1 - h * b2) / (4 * h)
    solved_b = (h * b2 - b1) / (8 * h**3)
    reconstructed_first = 2 * solved_a * h + 4 * solved_b * h**3
    reconstructed_second = 2 * solved_a + 12 * solved_b * h**2
    check("unique_formula_first", reconstructed_first == b1)
    check("unique_formula_second", reconstructed_second == b2)

    nonselection = packet["ward_qme_ppa_nonselection"]
    qme_checks = qme["QME_checks"]
    check("anomaly_vector", nonselection["local_QME_anomaly_class"] == qme["local_QME_anomaly"]["class_vector"] == [0, 0, 0, 0, 0])
    check("formal_QME", nonselection["formal_QME_scheme_exists"] == qme_checks["renormalized_QME_scheme_exists_as_formal_power_series"])
    check("SP_freedom", nonselection["SP_freedom_remains"] == qme_checks["renormalization_freedom_is_local_Stueckelberg_Petermann"])
    check("QME_nonselection", not nonselection["QME_selects_finite_coefficients"])
    check("gauge_Ward_nonselection", not nonselection["gauge_Ward_selects_finite_coefficients"])
    check("Action_Ward_nonselection", not nonselection["Action_Ward_selects_finite_coefficients"])
    check("field_independence_nonselection", not nonselection["field_independence_selects_finite_coefficients"])
    check("split_Ward_nonselection", not nonselection["split_Ward_selects_finite_coefficients"])
    check("PPA_nonselection", not nonselection["perturbative_agreement_selects_total_action"])
    check("classical_on_shell_source", nonselection["classical_on_shell_background_removes_linear_tree_term"] == costello["matter_extension_checks"]["on_shell_background_removes_the_linear_tadpole"])
    check("classical_on_shell_not_quantum_selector", not nonselection["classical_on_shell_clause_selects_quantum_tadpole_scheme"])

    projection = packet["source_preserving_projection_contract"]
    provider_required = provider_schema["properties"]["bindings"]["required"]
    check("provider_required_copy", projection["provider_schema_binding_requirements"] == provider_required)
    for field, packet_key in (
        ("fixed_point_hessian_identity", "provider_schema_requires_fixed_point_hessian_identity"),
        ("action_bv_pushforward", "provider_schema_requires_action_bv_pushforward"),
        ("normalization_and_interaction_source", "provider_schema_requires_normalization_source"),
        ("one_root_hash_for_all_packets", "provider_schema_requires_one_root_hash"),
    ):
        check(f"provider_{field}", field in provider_required and projection[packet_key])
    check("six_projection_clauses", set(projection["clauses"]) == {"SP0", "SP1", "SP2", "SP3", "SP4", "SP5"})
    check("pointed_scope", projection["pointed_not_global"] and not projection["full_nonlinear_flow_equality_required"])
    check("A35_coordinate", projection["A35_selected_dimensionless_radial_coordinate"] == a35["selected_radial_coordinate_normalization_closed"])
    check("A35_action_open", projection["A35_selects_physical_action_weight"] == a35["physical_action_weighted_Y_nu_closed"] is False)
    check("physical_metric_not_smuggled", not projection["physical_tangent_metric_is_part_of_A35"])
    check("provider_instance_open", not projection["accepted_physical_provider_instance_present"])
    check("projection_instance_open", not projection["selected_quantum_projection_present"])

    selection = packet["selection_theorem"]
    check("QJ1_implication", selection["QJ1_follows_from_one_morphism"])
    check("QJ2_implication", selection["action_jet_QJ2_follows_from_same_morphism"])
    check("not_two_numeric_knobs", not selection["QJ1_and_action_QJ2_are_independent_numeric_knobs"])
    check("unique_T39_representative", selection["nonconstant_SP_representative_is_unique_given_morphism"] and selection["unique_representative_is_T39_anchor"])
    check("classification", selection["classification"] == "IMPLICATION_CLOSED_EXISTENCE_OPEN")
    check("existence_open", not selection["selected_morphism_existence_proved"])
    check("q79_realization_open", not selection["primitive_q79_realization_proved"])
    check("metric_QJ2_open", not selection["physical_metric_normalized_QJ2_proved"])

    state_route = packet["radial_state_route"]
    radial = t38["invariant_radial_state"]
    formal = t38["formal_q79_state_extension"]
    check("radial_unique", state_route["unique_upper_radial_marginal"] == radial["radial_marginal_is_unique_without_selecting_matter_state"])
    check("radial_expectation", state_route["forced_radial_expectation"] == radial["forced_radial_expectation"] == "omega(h)=H")
    check("formal_state_exists", state_route["formal_local_state_extension_exists"] == formal["formal_local_radial_anchored_state_exists"])
    check("full_state_not_unique", state_route["full_interacting_state_unique"] == formal["full_interacting_state_is_unique"] is False)
    check("state_map_open", not state_route["selected_physical_state_pushforward_present"])

    execution = packet["T35_execution"]
    numeric = t35["numerical_execution"]
    msbar = numeric["MSbar_mu_equals_Lambda_per_unit_kappa"]
    with localcontext() as context:
        context.prec = 100
        h_dec = Decimal(numeric["H_over_Lambda"])
        h2_dec = Decimal(numeric["H_squared_over_Lambda_squared"])
        q4 = Decimal(numeric["q4_star"])
        l_h = Decimal(t37["T35_tadpole_execution"]["L_H"])
        delta_m2 = Decimal(msbar["delta_m2_over_Lambda2"])
        delta_lambda = Decimal(msbar["delta_lambda"])
        bare = Decimal(t37["T35_tadpole_execution"]["bare_tadpole_over_kappa_Lambda3"])
        expected_m2 = -Decimal(2) * q4 * h2_dec
        expected_lambda = l_h + Decimal("1.5") * q4
        counterterm_tadpole = Decimal(2) * delta_m2 * h_dec + Decimal(4) * delta_lambda * h_dec**3
        residual = bare + counterterm_tadpole
        direction_m2 = -Decimal(2) * h2_dec
        direction_tadpole = Decimal(2) * direction_m2 * h_dec + Decimal(4) * h_dec**3
        direction_hessian = Decimal(2) * direction_m2 + Decimal(12) * h2_dec
        h_square = h_dec**2
        eight_h2 = Decimal(8) * h2_dec

    check("H_copy", Decimal(execution["H_over_Lambda"]) == h_dec)
    check("H2_copy", Decimal(execution["H_squared_over_Lambda_squared"]) == h2_dec)
    check("H_squared_consistency", close(h_square, h2_dec, "1e-75"))
    check("delta_m2_formula", close(delta_m2, expected_m2))
    check("delta_lambda_formula", close(delta_lambda, expected_lambda))
    check("delta_m2_packet", Decimal(execution["unique_T39_delta_m2_over_kappa_Lambda2"]) == delta_m2)
    check("delta_lambda_packet", Decimal(execution["unique_T39_delta_lambda_over_kappa"]) == delta_lambda)
    check("tadpole_cancel", abs(residual) < Decimal("1e-70"))
    check("tadpole_packet", close(Decimal(execution["matched_tadpole_residual"]), residual, "1e-90"))
    check("direction_m2", Decimal(execution["QJ1_orbit_direction"]["delta_m2_over_kappa_Lambda2_per_t"]) == direction_m2)
    check("direction_tadpole", abs(direction_tadpole) < Decimal("1e-75"))
    check("direction_hessian", Decimal(execution["QJ1_orbit_direction"]["hessian_shift_over_kappa_Lambda2_per_t"]) == direction_hessian == eight_h2)
    check("direction_hessian_positive", execution["QJ1_orbit_hessian_is_nonzero"] and direction_hessian > 0)
    check("higher_jets", execution["T35_higher_jets_retained"] and t35["closure_jet_matching"]["jets_at_x_equal_one"]["third"] == -16)

    qj = packet["QJ_classification"]
    check("T39_QJ1_preserved", qj["QJ1_local_formal_anchor_scheme"] == t39["QJ_classification"]["QJ1_local_formal_anchor_scheme"])
    check("morphism_QJ1_closed", qj["QJ1_same_source_morphism_implication"] == "closed_exactly")
    check("physical_QJ1_open", qj["QJ1_selected_physical_q79_law"] == "open_morphism_existence")
    check("T39_QJ2_preserved", qj["QJ2_local_formal_action_Hessian"] == t39["QJ_classification"]["QJ2_local_formal_action_Hessian"])
    check("morphism_QJ2_closed", qj["QJ2_same_source_action_jet_implication"] == "closed_exactly")
    check("physical_QJ2_open", qj["QJ2_physical_normalized_Hessian"].startswith("open_"))
    check("gravity_QJ0_open", qj["QJ0_gravitational_absolute_vacuum"] == "open")

    ledger = packet["parameter_ledger"]
    check("no_continuous_parameters", ledger["new_physical_continuous_parameters"] == 0)
    check("no_discrete_selectors", ledger["new_physical_discrete_selectors"] == 0)
    check("no_fits", ledger["new_fits"] == 0)
    check("no_observed_inputs", ledger["new_observed_inputs"] == 0)
    check("one_structural_certificate", ledger["new_structural_existence_certificates_required"] == 1)
    check("no_QFT_constant", ledger["remaining_additive_constant_in_normalized_connected_QFT"] == 0)
    check("one_gravity_constant", ledger["remaining_additive_constant_if_gravity_included"] == 1)

    boundary = packet["physical_boundary"]
    check("contract_selector", boundary["provider_contract_level_selector_proved"])
    check("physical_provider_open", not boundary["selected_physical_provider_instance_present"])
    check("physical_projection_open", not boundary["selected_physical_quantum_projection_present"])
    check("physical_QJ1_not_promoted", not boundary["physical_QJ1_selected"])
    check("physical_QJ2_not_promoted", not boundary["physical_QJ2_selected"])
    check("gravity_QJ0_not_promoted", not boundary["gravitational_QJ0_selected"])
    check("endpoint_not_executed", not boundary["physical_interacting_q79_BV_endpoint_executed"])
    check("acceptance_unchanged", not boundary["acceptance_counters_change"])

    check("theorem_orbit", "C_t(h)=t(h^2-H^2)^2 mod constants" in theorem_text)
    check("theorem_hessian", "C_t''(H)=8H^2 t" in theorem_text)
    check("theorem_source_contract", "Source-preserving pointed quantum projection" in theorem_text)
    check("theorem_physical_boundary", "does not contain an accepted physical instance" in theorem_text)
    check("theorem_counters", "physical packets accepted: 0/3" in theorem_text and "physical rows accepted:    0/7" in theorem_text)

    builder_checks = packet["checks"]
    check("builder_checks_nonempty", len(builder_checks) >= 70)
    check("builder_checks_all_true", all(builder_checks.values()))
    check("builder_summary", packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(builder_checks))
    check("builder_failed_empty", packet["check_summary"]["failed"] == [])

    failed = sorted(name for name, passed in checks.items() if not passed)
    print(f"independent checks: {len(checks) - len(failed)}/{len(checks)}")
    if failed:
        for name in failed:
            print(f"FAILED: {name}")
        raise SystemExit(1)
    print("source-preserving pointed quantum projection verification passed")


if __name__ == "__main__":
    main()
