#!/usr/bin/env python3
"""Independently verify the CBF.T39 anchored BV repair-semiflow packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
SOURCE_LOCK = ROOT / "renormalized_bv_anchored_repair_semiflow_source_lock.json"
SCHEMA = ROOT / "renormalized_bv_anchored_repair_semiflow_contract.schema.json"
THEOREM = ROOT / "RenormalizedBVAnchoredRepairSemiflowAndGlobalIntertwiningNoGoTheorem_v1.md"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T37_PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
CERT_ROOT = ROOT / "../mtt-qm-source-proof/certificates"
QME_CERT = CERT_ROOT / "q79_sm_renormalized_timeordering_local_qme.certificate.json"
COSTELLO_CERT = CERT_ROOT / "q79_firstorder_costello_bv_graphwise_counterterm.certificate.json"
LORENTZ_CERT = CERT_ROOT / "q79_lorentzian_spectral_sp_qme_cauchy_bridge.certificate.json"
SHELL_CERT = CERT_ROOT / "q79_sm_finite_shell_bv_pushforward_regulator_comparison.certificate.json"
DIFF_CERT = CERT_ROOT / "q79_sm_diffeomorphism_transported_regulator_orbit.certificate.json"
PHASE_CERT = CERT_ROOT / "q79_sm_determinant_phase_torsor_quotient.certificate.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def fraction(value: str | int) -> Fraction:
    return Fraction(value)


def trim(coefficients: list[Fraction]) -> list[Fraction]:
    result = list(coefficients)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return trim(
        [
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        ]
    )


def poly_sub(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return trim(
        [
            (left[index] if index < len(left) else Fraction(0))
            - (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        ]
    )


def derivative_value(
    coefficients: list[Fraction], point: Fraction, order: int
) -> Fraction:
    total = Fraction(0)
    for degree, coefficient in enumerate(coefficients):
        if degree < order:
            continue
        falling = 1
        for offset in range(order):
            falling *= degree - offset
        total += coefficient * falling * point ** (degree - order)
    return total


def jet2(coefficients: list[Fraction], point: Fraction) -> list[Fraction]:
    return [derivative_value(coefficients, point, order) for order in range(3)]


def anchor_coefficients(point: Fraction, jets: list[Fraction]) -> list[Fraction]:
    b0, b1, b2 = jets
    return [
        b0 - Fraction(5, 8) * point * b1 + Fraction(1, 8) * point**2 * b2,
        (3 * b1 - point * b2) / (4 * point),
        (point * b2 - b1) / (8 * point**3),
    ]


def counterterm_polynomial(coefficients: list[Fraction]) -> list[Fraction]:
    a0, a2, a4 = coefficients
    return [a0, Fraction(0), a2, Fraction(0), a4]


def retract(
    polynomial: list[Fraction], point: Fraction
) -> tuple[list[Fraction], list[Fraction]]:
    counterterm = counterterm_polynomial(
        anchor_coefficients(point, jet2(polynomial, point))
    )
    return counterterm, poly_sub(polynomial, counterterm)


def sum_polynomials(rows: list[list[Fraction]]) -> list[Fraction]:
    result = [Fraction(0)]
    for row in rows:
        result = poly_add(result, row)
    return result


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def multiply_series(
    left: list[Fraction], right: list[Fraction], degree: int
) -> list[Fraction]:
    result = [Fraction(0) for _ in range(degree + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= degree:
                result[i + j] += a * b
    return result


def normalized_t35_jets() -> list[Fraction]:
    """Expand rho(1+y) exactly through order five, independently of T35."""

    degree = 5
    x4 = [Fraction(comb(4, k)) if k <= 4 else Fraction(0) for k in range(6)]
    x2 = [Fraction(comb(2, k)) if k <= 2 else Fraction(0) for k in range(6)]
    log_x2 = [Fraction(0)] + [
        Fraction(2 * ((-1) ** (k + 1)), k) for k in range(1, degree + 1)
    ]
    x4_log_x2 = multiply_series(x4, log_x2, degree)
    rho = [
        Fraction(3, 2) * x4[k] - x4_log_x2[k] - 2 * x2[k]
        for k in range(degree + 1)
    ]
    rho[0] += Fraction(1, 2)
    return [rho[order] * factorial(order) for order in range(degree + 1)]


def close(left: Decimal, right: Decimal, tolerance: str = "1e-70") -> bool:
    return abs(left - right) <= Decimal(tolerance)


def verify() -> tuple[int, int, list[str]]:
    packet = load(PACKET)
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    t35 = load(T35_PACKET)
    t37 = load(T37_PACKET)
    t38 = load(T38_PACKET)
    qme = load(QME_CERT)
    costello = load(COSTELLO_CERT)
    lorentz = load(LORENTZ_CERT)
    shell = load(SHELL_CERT)
    diff = load(DIFF_CERT)
    phase = load(PHASE_CERT)
    theorem = THEOREM.read_text(encoding="utf-8")
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        check(f"source_{index:02d}_exists", path.is_file())
        check(
            f"source_{index:02d}_hash",
            path.is_file() and sha256(path) == source["sha256"],
        )

    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("packet_claim", packet["claim_id"] == "CBF.T39")
    check("source_lock_claim", source_lock["claim_id"] == "CBF.T39")
    check("source_lock_handoff", source_lock["handoff_id"] == "2446113d-ed17-4ea3-8a3e-30ce17582254")
    check("required_keys", set(schema["required"]).issubset(packet))
    check("no_extra_top_level_keys", set(packet).issubset(schema["properties"]))
    check("builder_checks_green", all(packet["checks"].values()))
    check(
        "builder_summary_green",
        packet["check_summary"]["passed"] == packet["check_summary"]["total"]
        and packet["check_summary"]["failed"] == [],
    )
    provenance = packet["source_provenance"]
    check("source_lock_hash", provenance["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("schema_hash", provenance["schema_sha256"] == sha256(SCHEMA))
    check("theorem_hash", provenance["theorem_sha256"] == sha256(THEOREM))
    check("source_inventory_hash", provenance["source_inventory_hash"] == canonical_hash(source_lock["local_sources"]))
    check("repository_heads_locked", provenance["repositories"] == source_lock["repositories"])
    check("kernel_model_locked", provenance["kernel_model_sha256"] == source_lock["kernel_model_sha256"])
    check("T35_locked", t35["claim_id"] == "CBF.T35")
    check("T37_locked", t37["claim_id"] == "CBF.T37")
    check("T38_locked", t38["claim_id"] == "CBF.T38")

    generator = packet["quantum_bv_generator"]
    check("generator_has_action", generator["action_term_included"])
    check("generator_has_measure", generator["measure_term_included"])
    check("generator_has_determinant", generator["determinant_term_included"])
    check("generator_has_cycle", generator["cycle_boundary_term_included"])
    check("generator_uses_total_cancellation", generator["terms_must_cancel_only_in_total"])
    check("generator_does_not_require_termwise_zero", not generator["individual_termwise_vanishing_required"])
    check("RG_not_repair_parameter", not generator["repair_parameter_identified_with_RG_scale"])
    check("RG_not_Lorentzian_time", not generator["RG_scale_identified_with_Lorentzian_time"])

    coverage = packet["q79_source_coverage"]
    qme_checks = qme["QME_checks"]
    recursion = costello["graphwise_counterterm_recursion"]["recursion_checks"]
    bridge = lorentz["direct_six_row_bridge"]
    shell_result = shell["finite_shell_theorem"]["result"]
    conclusions = diff["diffeomorphism_naturality_theorem"]["conclusions"]
    connected = phase["normalized_observable_theorem"]["connected_generating_function"]
    check("source_QME_scheme", coverage["local_formal_QME_scheme"] == qme_checks["renormalized_QME_scheme_exists_as_formal_power_series"])
    check("source_SP_freedom", coverage["SP_renormalization_freedom"] == qme_checks["renormalization_freedom_is_local_Stueckelberg_Petermann"])
    check("source_graph_recursion", coverage["graphwise_local_counterterm_recursion"] == recursion["Costello_recursion_emits_one_local_counterterm_per_bidegree"])
    check("source_RG_composition", coverage["exact_RG_composition"] == recursion["renormalized_effective_actions_obey_the_exact_RG_semigroup"])
    check("source_Lorentzian_QME", coverage["Lorentzian_QME_and_Ward_bridge"] == bridge["QME_and_Ward_compatibility"]["accepted"])
    check("source_boundary_gluing", coverage["active_local_domain_boundary_gluing"] == bridge["boundary_gluing_compatibility"]["accepted"])
    check("source_free_shell_pushforward", coverage["finite_shell_free_BV_pushforward"] == ("preserves the free QME" in shell_result))
    check("source_zero_BFV_flux", coverage["diffeomorphism_orbit_zero_BFV_flux"] == conclusions["relative_BV_BFV_boundary_flux_is_zero"])
    check("source_determinant_transport", coverage["diffeomorphism_orbit_determinant_transport"] == conclusions["determinant_half_density_is_canonically_transported"])
    check("source_phase_quotient", coverage["common_determinant_phase_drops_from_positive_source_derivatives"] == ("every positive-order source derivative is unchanged" in connected))
    check("radial_change_not_diffeomorphism", not coverage["radial_background_change_is_a_diffeomorphism_presentation_orbit"])
    check("QME_not_radial_stationarity", not coverage["QME_is_a_radial_stationarity_identity"])
    check("fixed_coupling_endpoint_not_claimed", not coverage["physical_fixed_coupling_interacting_BV_pushforward"])
    check("uniform_interacting_limit_not_claimed", not coverage["uniform_interacting_cutoff_removal"])
    check("selected_global_state_not_claimed", not coverage["selected_global_interacting_state"])

    point = Fraction(3, 2)
    matrix = [
        [Fraction(1), point**2, point**4],
        [Fraction(0), 2 * point, 4 * point**3],
        [Fraction(0), Fraction(2), 12 * point**2],
    ]
    determinant = determinant3(matrix)
    anchor = packet["pointed_anchor_retraction"]
    witness = anchor["witness"]
    check("anchor_matrix_determinant", determinant == 16 * point**3 == 54)
    check("anchor_packet_determinant", fraction(witness["matching_matrix_determinant_at_witness"]) == determinant)
    check("anchor_positive_invertible", anchor["H_positive_makes_map_invertible"] and determinant > 0)

    components = {
        "action_insertion": [Fraction(v) for v in (2, 0, 3, 0, 5, 0, 7)],
        "measure_density": [Fraction(v) for v in (1, 0, -2, 0, 4, 0, -3)],
        "determinant_density": [Fraction(v) for v in (0, 0, 5, 0, -1, 0, 2)],
        "cycle_boundary": [Fraction(v) for v in (3, 0, 1, 0, -4, 0, 1)],
    }
    counterterms: list[list[Fraction]] = []
    remainders: list[list[Fraction]] = []
    for name, polynomial in components.items():
        counterterm, remainder = retract(polynomial, point)
        record = witness["components"][name]
        counterterms.append(counterterm)
        remainders.append(remainder)
        check(f"{name}_polynomial", [fraction(v) for v in record["polynomial_coefficients_ascending"]] == polynomial)
        check(f"{name}_counterterm", [fraction(v) for v in record["counterterm_coefficients_ascending"]] == counterterm)
        check(f"{name}_remainder", [fraction(v) for v in record["remainder_coefficients_ascending"]] == remainder)
        check(f"{name}_zero_two_jet", jet2(remainder, point) == [Fraction(0)] * 3)

    total = sum_polynomials(list(components.values()))
    total_counterterm, total_remainder = retract(total, point)
    summed_counterterms = sum_polynomials(counterterms)
    summed_remainders = sum_polynomials(remainders)
    second_counterterm, second_remainder = retract(total_remainder, point)
    check("total_polynomial", [fraction(v) for v in witness["total_polynomial_coefficients_ascending"]] == total)
    check("total_counterterm", [fraction(v) for v in witness["total_counterterm_coefficients_ascending"]] == total_counterterm)
    check("total_remainder", [fraction(v) for v in witness["total_remainder_coefficients_ascending"]] == total_remainder)
    check("counterterm_linearity", summed_counterterms == total_counterterm)
    check("retraction_linearity", summed_remainders == total_remainder)
    check("remainder_zero_two_jet", jet2(total_remainder, point) == [Fraction(0)] * 3)
    check(
        "retraction_idempotent",
        all(value == 0 for value in second_counterterm)
        and second_remainder == total_remainder,
    )
    check("counterterm_projection_idempotent", retract(total_counterterm, point)[0] == total_counterterm)

    exact_jets = normalized_t35_jets()
    check("T35_exact_six_jets", exact_jets == [Fraction(0), Fraction(0), Fraction(0), Fraction(-16), Fraction(-64), Fraction(-48)])
    execution = packet["T35_pointed_execution"]
    execution_jets = execution["action_jets_at_x_equal_one"]
    check("T35_packet_value_jet", fraction(execution_jets["value"]) == exact_jets[0])
    check("T35_packet_first_jet", fraction(execution_jets["first"]) == exact_jets[1])
    check("T35_packet_second_jet", fraction(execution_jets["second"]) == exact_jets[2])
    check("T35_packet_third_jet", fraction(execution_jets["third"]) == exact_jets[3])
    check("T35_packet_fourth_jet", fraction(execution_jets["fourth"]) == exact_jets[4])
    check("T35_packet_fifth_jet", fraction(execution_jets["fifth"]) == exact_jets[5])
    check("T35_source_first_four_jets", [fraction(t35["closure_jet_matching"]["jets_at_x_equal_one"][key]) for key in ("value", "first", "second", "third", "fourth")] == exact_jets[:5])

    q4_exact = t35["fixed_source_four_dimensional_determinant"]["q4_star"]["exact_coefficients"]
    q4_pair = (fraction(q4_exact["rational"]), fraction(q4_exact["sqrt13"]))
    check("q4_exact_pair", q4_pair == (Fraction(356, 27), Fraction(25, 27)))
    with localcontext() as context:
        context.prec = 100
        q4 = Decimal(q4_pair[0].numerator) / Decimal(q4_pair[0].denominator)
        q4 += Decimal(q4_pair[1].numerator) / Decimal(q4_pair[1].denominator) * Decimal(13).sqrt()
        h = Decimal(t35["numerical_execution"]["H_over_Lambda"])
        fifth = -Decimal(48) * q4 / h
        no_go = packet["global_intertwining_no_go"]
        check("q4_positive", q4 > 0)
        check("H_positive", h > 0)
        check("fifth_derivative_reconstructed", close(Decimal(no_go["fifth_derivative_at_H_per_kappa_in_Lambda_minus_one_units"]), fifth))
        check("fifth_derivative_nonzero", fifth != 0 and no_go["fifth_derivative_at_H_is_nonzero"])
    check("quartic_counterterm_fifth_zero", derivative_value([Fraction(4), Fraction(0), Fraction(-3), Fraction(0), Fraction(9)], point, 5) == 0)
    check("global_identity_flow_excluded", not no_go["global_identity_radial_repair_intertwining_possible"])
    check("no_go_bounded", not no_go["no_go_is_universal_beyond_declared_scope"] and not no_go["nonlinear_field_redefinition_or_unsourced_metric_escape_excluded"])
    check("bare_tadpole_matches_T37", no_go["bare_tadpole_over_kappa_Lambda3"] == t37["T35_tadpole_execution"]["bare_tadpole_over_kappa_Lambda3"])
    check("bare_tadpole_nonzero", Decimal(no_go["bare_tadpole_over_kappa_Lambda3"]) != 0)

    flow = packet["anchored_formal_bv_flow"]
    check("formal_QJ1_preserved", "partial_h Gamma_s^H(H)=0" in flow["QJ1_formal_consequence"])
    check("formal_action_Hessian_preserved", "partial_h^2 Gamma_s^H(H)" in flow["QJ2_formal_action_jet_consequence"])
    check("formal_value_preserved", flow["QJ0_formal_action_jet_consequence"] == "Gamma_s^H(H)=P_*(H)")
    check("three_anchor_conditions", flow["finite_normalization_conditions"] == 3)
    check("zero_free_anchor_coefficients", flow["new_free_counterterm_coefficients"] == 0)
    check("upper_selection_not_claimed", not flow["upper_MTT_selects_this_normalization"])
    check("physical_flow_not_claimed", not flow["physical_fixed_coupling_flow_claimed"])
    check("pointed_fixed_intertwining", execution["pointed_fixed_point_intertwining"])
    check("pointed_tangent_intertwining_conditional", execution["pointed_tangent_intertwining_given_common_metric_at_H"])
    check("higher_nonlinearity_retained", execution["repair_vector_field_quadratic_jet_difference_is_nonzero"] and execution["nonlinear_quantum_corrections_retained"])
    check("global_vector_fields_not_equal", not execution["global_repair_vector_fields_equal"])

    compatibility = packet["qme_and_ward_compatibility"]
    check("zero_q79_anomaly_vector", qme["local_QME_anomaly"]["class_vector"] == compatibility["local_gauge_anomaly_class"] == [0, 0, 0, 0, 0])
    check("counterterm_ghost_zero", compatibility["ghost_number"] == 0)
    check("counterterm_antifield_free", compatibility["antifield_degree"] == 0)
    check("counterterm_BV_self_bracket_zero", compatibility["self_BV_bracket_of_radial_counterterms"] == 0)
    check("counterterm_BV_laplacian_zero", compatibility["BV_laplacian_of_radial_counterterms"] == 0)
    check("formal_QME_scheme_compatible", compatibility["formal_QME_compatible_scheme_exists"])
    check("QME_does_not_select_anchor", not compatibility["QME_selects_anchor_coefficients"])
    check("Ward_does_not_select_anchor", not compatibility["Ward_identity_selects_anchor_coefficients"])

    qj = packet["QJ_classification"]
    check("QJ1_formal_closed", qj["QJ1_local_formal_anchor_scheme"] == "closed_constructively")
    check("QJ1_physical_open", qj["QJ1_selected_physical_q79_law"] == "open")
    check("QJ2_action_jet_closed", qj["QJ2_local_formal_action_Hessian"] == "closed_constructively")
    check("QJ2_metric_open", qj["QJ2_physical_normalized_Hessian"] == "open_tangent_metric_or_wavefunction")
    check("QJ0_normalized_quotient", qj["QJ0_normalized_connected_QFT_common_phase"] == "quotiented_not_a_physical_exit")
    check("QJ0_gravity_open", qj["QJ0_gravitational_absolute_vacuum"] == "open")

    boundary = packet["physical_boundary"]
    ledger = packet["parameter_ledger"]
    check("physical_QJ1_not_promoted", not boundary["physical_QJ1_selected"])
    check("physical_QJ2_not_promoted", not boundary["physical_QJ2_selected"])
    check("gravitational_QJ0_not_promoted", not boundary["gravitational_QJ0_selected"])
    check("physical_endpoint_not_executed", not boundary["physical_interacting_q79_BV_endpoint_executed"])
    check("full_loops_not_executed", not boundary["full_loop_content_executed"])
    check("acceptance_unchanged", not boundary["acceptance_counters_change"])
    check("zero_new_physical_parameters", ledger["new_physical_continuous_parameters"] == 0 and ledger["new_physical_discrete_selectors"] == 0)
    check("zero_fit_or_observed_input", ledger["new_fits"] == 0 and ledger["new_observed_inputs"] == 0)
    check("anchor_not_prediction", not ledger["anchor_conditions_are_a_physical_prediction"])
    check("repair_not_physical_time", not ledger["repair_parameter_is_physical_time"])
    check("packet_counter_0_of_3", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("row_counter_0_of_7", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)

    check("theorem_states_bounded_no_go", "This no-go is deliberately bounded" in theorem)
    check("theorem_keeps_physical_QJ1_open", "Physical QJ1 and the endpoint acceptance counters therefore\nremain open" in theorem)
    check("theorem_does_not_call_repair_time", "T39 identifies none of them with another" in theorem)

    failed = [name for name, passed in checks.items() if not passed]
    return len(checks) - len(failed), len(checks), failed


def main() -> None:
    passed, total, failed = verify()
    if failed:
        raise SystemExit(f"independent verification failed: {failed}")
    print(f"verified {PACKET.name}: {passed}/{total} independent checks passed")


if __name__ == "__main__":
    main()
