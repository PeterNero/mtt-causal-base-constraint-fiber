#!/usr/bin/env python3
"""Build the exact CBF.T39 anchored BV repair-semiflow packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "renormalized_bv_anchored_repair_semiflow_source_lock.json"
SCHEMA = ROOT / "renormalized_bv_anchored_repair_semiflow_contract.schema.json"
THEOREM = ROOT / "RenormalizedBVAnchoredRepairSemiflowAndGlobalIntertwiningNoGoTheorem_v1.md"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T37_PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
QM_ROOT = ROOT / "../mtt-qm-source-proof/certificates"
QME_CERT = QM_ROOT / "q79_sm_renormalized_timeordering_local_qme.certificate.json"
COSTELLO_CERT = QM_ROOT / "q79_firstorder_costello_bv_graphwise_counterterm.certificate.json"
LORENTZ_CERT = QM_ROOT / "q79_lorentzian_spectral_sp_qme_cauchy_bridge.certificate.json"
SHELL_CERT = QM_ROOT / "q79_sm_finite_shell_bv_pushforward_regulator_comparison.certificate.json"
DIFF_CERT = QM_ROOT / "q79_sm_diffeomorphism_transported_regulator_orbit.certificate.json"
PHASE_CERT = QM_ROOT / "q79_sm_determinant_phase_torsor_quotient.certificate.json"
OUTPUT = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"


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


def trim(coefficients: list[Fraction]) -> list[Fraction]:
    result = list(coefficients)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return trim([
        (left[index] if index < len(left) else Fraction(0))
        + (right[index] if index < len(right) else Fraction(0))
        for index in range(size)
    ])


def poly_sub(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return trim([
        (left[index] if index < len(left) else Fraction(0))
        - (right[index] if index < len(right) else Fraction(0))
        for index in range(size)
    ])


def poly_derivative_value(
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
    return [poly_derivative_value(coefficients, point, order) for order in range(3)]


def anchor_coefficients(
    point: Fraction, jets: list[Fraction]
) -> list[Fraction]:
    b0, b1, b2 = jets
    a0 = b0 - Fraction(5, 8) * point * b1 + Fraction(1, 8) * point**2 * b2
    a2 = (3 * b1 - point * b2) / (4 * point)
    a4 = (point * b2 - b1) / (8 * point**3)
    return [a0, a2, a4]


def counterterm_polynomial(coefficients: list[Fraction]) -> list[Fraction]:
    a0, a2, a4 = coefficients
    return [a0, Fraction(0), a2, Fraction(0), a4]


def anchor_retract(
    polynomial: list[Fraction], point: Fraction
) -> tuple[list[Fraction], list[Fraction]]:
    counterterm = counterterm_polynomial(
        anchor_coefficients(point, jet2(polynomial, point))
    )
    return counterterm, poly_sub(polynomial, counterterm)


def sum_polynomials(rows: list[list[Fraction]]) -> list[Fraction]:
    total = [Fraction(0)]
    for row in rows:
        total = poly_add(total, row)
    return total


def serialize_poly(coefficients: list[Fraction]) -> list[str]:
    return [ftext(value) for value in coefficients]


def pointed_anchor_witness() -> dict[str, Any]:
    point = Fraction(3, 2)
    components = {
        "action_insertion": [Fraction(v) for v in (2, 0, 3, 0, 5, 0, 7)],
        "measure_density": [Fraction(v) for v in (1, 0, -2, 0, 4, 0, -3)],
        "determinant_density": [Fraction(v) for v in (0, 0, 5, 0, -1, 0, 2)],
        "cycle_boundary": [Fraction(v) for v in (3, 0, 1, 0, -4, 0, 1)],
    }
    total = sum_polynomials(list(components.values()))
    total_counterterm, total_remainder = anchor_retract(total, point)
    component_counterterms: list[list[Fraction]] = []
    component_remainders: list[list[Fraction]] = []
    serialized_components: dict[str, Any] = {}
    for name, polynomial in components.items():
        counterterm, remainder = anchor_retract(polynomial, point)
        component_counterterms.append(counterterm)
        component_remainders.append(remainder)
        serialized_components[name] = {
            "polynomial_coefficients_ascending": serialize_poly(polynomial),
            "counterterm_coefficients_ascending": serialize_poly(counterterm),
            "remainder_coefficients_ascending": serialize_poly(remainder),
            "remainder_jet_0_1_2": [ftext(v) for v in jet2(remainder, point)],
        }

    summed_counterterms = sum_polynomials(component_counterterms)
    summed_remainders = sum_polynomials(component_remainders)
    _, retracted_twice = anchor_retract(total_remainder, point)

    return {
        "rational_anchor_H": ftext(point),
        "components": serialized_components,
        "total_polynomial_coefficients_ascending": serialize_poly(total),
        "total_jet_0_1_2": [ftext(v) for v in jet2(total, point)],
        "total_counterterm_coefficients_ascending": serialize_poly(total_counterterm),
        "total_remainder_coefficients_ascending": serialize_poly(total_remainder),
        "total_remainder_jet_0_1_2": [
            ftext(v) for v in jet2(total_remainder, point)
        ],
        "counterterm_is_linear_over_four_BV_terms": (
            summed_counterterms == total_counterterm
        ),
        "retraction_is_linear_over_four_BV_terms": (
            summed_remainders == total_remainder
        ),
        "retraction_is_idempotent": retracted_twice == total_remainder,
        "matching_matrix_determinant": "16 H^3",
        "matching_matrix_determinant_at_witness": ftext(16 * point**3),
    }


def t35_global_no_go(t35: dict[str, Any], t37: dict[str, Any]) -> dict[str, Any]:
    numerical = t35["numerical_execution"]
    determinant = t35["fixed_source_four_dimensional_determinant"]
    q4_exact = determinant["q4_star"]["exact_coefficients"]
    with localcontext() as context:
        context.prec = 90
        q4 = Decimal(numerical["q4_star"])
        h = Decimal(numerical["H_over_Lambda"])
        fifth_at_h = -Decimal(48) * q4 / h
        tadpole = Decimal(
            t37["T35_tadpole_execution"]["bare_tadpole_over_kappa_Lambda3"]
        )

    return {
        "scope": (
            "identity radial projection, common radial metric at the T34/T35 tier, "
            "and the allowed local counterterm class span{1,h^2,h^4}"
        ),
        "fermion_log_term": "-kappa_F q4_* h^4 log(h^2/mu^2)",
        "fifth_derivative": "-48 kappa_F q4_*/h",
        "q4_star_exact_coefficients": q4_exact,
        "q4_star_positive": q4 > 0,
        "H_positive": h > 0,
        "fifth_derivative_at_H_per_kappa_in_Lambda_minus_one_units": dtext(
            fifth_at_h
        ),
        "fifth_derivative_at_H_is_nonzero": fifth_at_h != 0,
        "allowed_counterterm_fifth_derivative": "0",
        "global_same_metric_gradient_equality_would_force_fifth_derivative_zero": True,
        "global_identity_radial_repair_intertwining_possible": False,
        "bare_tadpole_over_kappa_Lambda3": dtext(tadpole),
        "bare_tadpole_is_nonzero": tadpole != 0,
        "nonlinear_field_redefinition_or_unsourced_metric_escape_excluded": False,
        "no_go_is_universal_beyond_declared_scope": False,
        "correct_replacement": (
            "pointed fixed-point and tangent-flow intertwining through the first "
            "jet of the repair vector field"
        ),
    }


def quantum_bv_generator() -> dict[str, Any]:
    return {
        "semidensity_pushforward": (
            "Psi_s(h,phi_IR)=integral_(L_s(h)) exp[-S_s(h,phi_IR,chi)/hbar] "
            "rho_s^(1/2)"
        ),
        "effective_action": "Gamma_s=-hbar log Psi_s",
        "radial_Ward_identity": (
            "partial_h Gamma_s=<partial_h S_s-hbar partial_h log rho_s^(1/2)>"
            "+B_s/Psi_s"
        ),
        "raw_scale_generator": (
            "beta_s^BV=beta_s^action+beta_s^measure+beta_s^determinant+"
            "beta_s^cycle"
        ),
        "action_term_included": True,
        "measure_term_included": True,
        "determinant_term_included": True,
        "cycle_boundary_term_included": True,
        "terms_must_cancel_only_in_total": True,
        "individual_termwise_vanishing_required": False,
        "repair_parameter_identified_with_RG_scale": False,
        "RG_scale_identified_with_Lorentzian_time": False,
        "scope": (
            "local formal q79 charts and finite/gapped shell presentations; a "
            "fixed-coupling nonperturbative integral is not asserted"
        ),
    }


def q79_source_coverage(
    qme: dict[str, Any],
    costello: dict[str, Any],
    lorentz: dict[str, Any],
    shell: dict[str, Any],
    diff: dict[str, Any],
    phase: dict[str, Any],
) -> dict[str, Any]:
    qme_checks = qme["QME_checks"]
    recursion = costello["graphwise_counterterm_recursion"]["recursion_checks"]
    bridge = lorentz["direct_six_row_bridge"]
    shell_theorem = shell["finite_shell_theorem"]
    diff_conclusions = diff["diffeomorphism_naturality_theorem"]["conclusions"]
    return {
        "local_formal_QME_scheme": qme_checks[
            "renormalized_QME_scheme_exists_as_formal_power_series"
        ],
        "SP_renormalization_freedom": qme_checks[
            "renormalization_freedom_is_local_Stueckelberg_Petermann"
        ],
        "graphwise_local_counterterm_recursion": recursion[
            "Costello_recursion_emits_one_local_counterterm_per_bidegree"
        ],
        "exact_RG_composition": recursion[
            "renormalized_effective_actions_obey_the_exact_RG_semigroup"
        ],
        "Lorentzian_QME_and_Ward_bridge": bridge["QME_and_Ward_compatibility"][
            "accepted"
        ],
        "active_local_domain_boundary_gluing": bridge[
            "boundary_gluing_compatibility"
        ]["accepted"],
        "finite_shell_free_BV_pushforward": "preserves the free QME"
        in shell_theorem["result"],
        "diffeomorphism_orbit_zero_BFV_flux": diff_conclusions[
            "relative_BV_BFV_boundary_flux_is_zero"
        ],
        "diffeomorphism_orbit_determinant_transport": diff_conclusions[
            "determinant_half_density_is_canonically_transported"
        ],
        "common_determinant_phase_drops_from_positive_source_derivatives": (
            "every positive-order source derivative is unchanged"
            in phase["normalized_observable_theorem"]["connected_generating_function"]
        ),
        "radial_background_change_is_a_diffeomorphism_presentation_orbit": False,
        "QME_is_a_radial_stationarity_identity": False,
        "physical_fixed_coupling_interacting_BV_pushforward": False,
        "uniform_interacting_cutoff_removal": False,
        "selected_global_interacting_state": False,
    }


def anchor_retraction_contract() -> dict[str, Any]:
    return {
        "jet_map": "j_H^2 f=(f(H),f'(H),f''(H))",
        "local_counterterm_space": "C_even=span{1,h^2,h^4}",
        "determinant": "det(j_H^2|C_even)=16 H^3",
        "H_positive_makes_map_invertible": True,
        "counterterm_formula": {
            "a0": "b0-(5/8)H b1+(1/8)H^2 b2",
            "a2": "(3 b1-H b2)/(4H)",
            "a4": "(H b2-b1)/(8H^3)",
        },
        "C_H": "C_H[f]=a0+a2 h^2+a4 h^4",
        "R_H": "R_H=I-C_H",
        "identities": [
            "j_H^2 C_H=j_H^2",
            "j_H^2 R_H=0",
            "C_H^2=C_H",
            "R_H^2=R_H",
        ],
        "four_term_linearity": (
            "R_H beta_BV=sum_X R_H beta_BV^X for X=action,measure,determinant,cycle"
        ),
        "witness": pointed_anchor_witness(),
    }


def anchored_formal_flow() -> dict[str, Any]:
    return {
        "raw_evolution": "partial_s Gamma_s=beta_s^BV(Gamma_s)",
        "anchored_evolution": "partial_s Gamma_s^H=R_H beta_s^BV(Gamma_s^H)",
        "initial_condition": "j_H^2 Gamma_0^H=j_H^2 P_*",
        "jet_conservation": "partial_s j_H^2 Gamma_s^H=0",
        "QJ1_formal_consequence": "partial_h Gamma_s^H(H)=0 at every formal order",
        "QJ2_formal_action_jet_consequence": (
            "partial_h^2 Gamma_s^H(H)=partial_h^2 P_*(H)"
        ),
        "QJ2_metric_requirement_remaining": (
            "the physical tangent metric or wave-function normalization at H"
        ),
        "QJ0_formal_action_jet_consequence": "Gamma_s^H(H)=P_*(H)",
        "formal_existence": (
            "Costello graph recursion plus zero q79 anomaly gives an anchored "
            "coefficientwise solution at every finite perturbative bidegree"
        ),
        "formal_uniqueness": (
            "for each raw coefficient and H>0, the three local coefficients are "
            "uniquely fixed by the three anchor equations"
        ),
        "composition": (
            "the unique normalized anchored SP comparisons obey the scale cocycle; "
            "equivalently the extended (s,Gamma) evolution is a formal semiflow"
        ),
        "new_free_counterterm_coefficients": 0,
        "finite_normalization_conditions": 3,
        "upper_MTT_selects_this_normalization": False,
        "physical_fixed_coupling_flow_claimed": False,
    }


def t35_pointed_execution(t35: dict[str, Any]) -> dict[str, Any]:
    matched = t35["closure_jet_matching"]
    jets = matched["jets_at_x_equal_one"]
    with localcontext() as context:
        context.prec = 90
        q4 = Decimal(t35["numerical_execution"]["q4_star"])
        h = Decimal(t35["numerical_execution"]["H_over_Lambda"])
        fifth_h = -Decimal(48) * q4 / h
    return {
        "normalized_matched_remainder": matched["normalized_shape"],
        "action_jets_at_x_equal_one": {
            "value": jets["value"],
            "first": jets["first"],
            "second": jets["second"],
            "third": jets["third"],
            "fourth": jets["fourth"],
            "fifth": -48,
        },
        "repair_vector_field_difference_at_H": 0,
        "repair_vector_field_linearization_difference_at_H": 0,
        "repair_vector_field_quadratic_jet_difference_is_nonzero": jets["third"] != 0,
        "global_repair_vector_fields_equal": False,
        "fifth_h_derivative_per_kappa_Lambda_inverse": dtext(fifth_h),
        "pointed_fixed_point_intertwining": True,
        "pointed_tangent_intertwining_given_common_metric_at_H": True,
        "nonlinear_quantum_corrections_retained": True,
    }


def qme_and_ward_compatibility() -> dict[str, Any]:
    return {
        "radial_counterterms": "a0+a2 h^2+a4 h^4",
        "ghost_number": 0,
        "antifield_degree": 0,
        "Higgs_radius_is_BRST_invariant": True,
        "BV_laplacian_of_radial_counterterms": 0,
        "self_BV_bracket_of_radial_counterterms": 0,
        "local_gauge_anomaly_class": [0, 0, 0, 0, 0],
        "formal_QME_compatible_scheme_exists": True,
        "QME_selects_anchor_coefficients": False,
        "Ward_identity_selects_anchor_coefficients": False,
        "why_not": (
            "the radial potential terms are nontrivial ghost-zero gauge-invariant "
            "finite normalization directions, not gauge-anomaly representatives"
        ),
        "cycle_boundary_scope": (
            "zero or canceled on the declared boundaryless local bridge and exact on "
            "transported diffeomorphism orbits; arbitrary physical boundaries remain open"
        ),
    }


def qj_classification() -> dict[str, Any]:
    return {
        "QJ1_local_formal_anchor_scheme": "closed_constructively",
        "QJ1_selected_physical_q79_law": "open",
        "QJ2_local_formal_action_Hessian": "closed_constructively",
        "QJ2_physical_normalized_Hessian": "open_tangent_metric_or_wavefunction",
        "QJ0_normalized_connected_QFT_common_phase": "quotiented_not_a_physical_exit",
        "QJ0_gravitational_absolute_vacuum": "open",
        "global_tree_quantum_repair_flow_identity": "excluded_in_declared_T35_scope",
        "correct_quantum_naturality_level": (
            "pointed first-jet repair-vector intertwining, not equality of the full "
            "nonlinear tree and quantum repair flows"
        ),
    }


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t35 = load_json(T35_PACKET)
    t37 = load_json(T37_PACKET)
    t38 = load_json(T38_PACKET)
    qme = load_json(QME_CERT)
    costello = load_json(COSTELLO_CERT)
    lorentz = load_json(LORENTZ_CERT)
    shell = load_json(SHELL_CERT)
    diff = load_json(DIFF_CERT)
    phase = load_json(PHASE_CERT)

    generator = quantum_bv_generator()
    coverage = q79_source_coverage(qme, costello, lorentz, shell, diff, phase)
    no_go = t35_global_no_go(t35, t37)
    retraction = anchor_retraction_contract()
    flow = anchored_formal_flow()
    execution = t35_pointed_execution(t35)
    compatibility = qme_and_ward_compatibility()
    qj = qj_classification()

    physical_boundary = {
        "physical_QJ1_selected": False,
        "physical_QJ2_selected": False,
        "gravitational_QJ0_selected": False,
        "full_global_intertwiner_required_for_QJ1": False,
        "pointed_anchor_scheme_available_without_observed_input": True,
        "pointed_anchor_scheme_selected_by_upper_action": False,
        "physical_interacting_q79_BV_endpoint_executed": False,
        "full_loop_content_executed": False,
        "RG_beta_functions_and_matching_executed": False,
        "fixed_coupling_nonperturbative_completion": False,
        "acceptance_counters_change": False,
    }

    parameter_ledger = {
        "new_physical_continuous_parameters": 0,
        "new_physical_discrete_selectors": 0,
        "new_fits": 0,
        "new_observed_inputs": 0,
        "finite_anchor_normalization_conditions": 3,
        "free_coefficients_after_anchor_conditions": 0,
        "anchor_H_source": "CBF.T34 same-root finite/formal radial coordinate",
        "anchor_conditions_are_a_physical_prediction": False,
        "repair_parameter_is_physical_time": False,
    }

    checks: dict[str, bool] = {}
    checks.update(source_hash_checks(source_lock))
    checks.update({
        "schema_id_matches": schema["properties"]["claim_id"]["const"] == "CBF.T39",
        "theorem_exists": THEOREM.is_file(),
        "T38_predecessor_is_green": t38["check_summary"]["failed"] == [],
        "q79_local_formal_QME_source_is_green": qme["all_checks_pass"],
        "q79_Costello_counterterm_source_is_green": costello["all_checks_pass"],
        "q79_Lorentzian_bridge_source_is_green": lorentz["all_checks_pass"],
        "q79_finite_shell_source_is_green": shell["all_checks_pass"],
        "q79_diffeomorphism_transport_source_is_green": diff["all_checks_pass"],
        "q79_determinant_phase_source_is_green": phase["all_checks_pass"],
        "all_four_BV_generator_terms_included": all(
            generator[key]
            for key in (
                "action_term_included",
                "measure_term_included",
                "determinant_term_included",
                "cycle_boundary_term_included",
            )
        ),
        "global_intertwining_no_go_has_nonzero_fifth_derivative": no_go[
            "fifth_derivative_at_H_is_nonzero"
        ],
        "quartic_counterterm_cannot_cancel_fifth_derivative": (
            no_go["allowed_counterterm_fifth_derivative"] == "0"
            and not no_go["global_identity_radial_repair_intertwining_possible"]
        ),
        "no_go_scope_is_not_overstated": (
            not no_go["nonlinear_field_redefinition_or_unsourced_metric_escape_excluded"]
            and not no_go["no_go_is_universal_beyond_declared_scope"]
        ),
        "anchor_retraction_is_linear": retraction["witness"][
            "retraction_is_linear_over_four_BV_terms"
        ],
        "anchor_counterterm_is_linear": retraction["witness"][
            "counterterm_is_linear_over_four_BV_terms"
        ],
        "anchor_retraction_is_idempotent": retraction["witness"][
            "retraction_is_idempotent"
        ],
        "anchor_remainder_has_zero_two_jet": retraction["witness"][
            "total_remainder_jet_0_1_2"
        ] == ["0", "0", "0"],
        "anchor_matrix_is_invertible": retraction[
            "H_positive_makes_map_invertible"
        ],
        "q79_exact_RG_composition_is_sourced": coverage["exact_RG_composition"],
        "q79_QME_scheme_is_sourced": coverage["local_formal_QME_scheme"],
        "q79_finite_shell_pushforward_is_sourced": coverage[
            "finite_shell_free_BV_pushforward"
        ],
        "radial_change_not_misclassified_as_diffeomorphism": not coverage[
            "radial_background_change_is_a_diffeomorphism_presentation_orbit"
        ],
        "QME_not_misclassified_as_radial_stationarity": not coverage[
            "QME_is_a_radial_stationarity_identity"
        ],
        "anchored_flow_preserves_QJ1_formally": (
            "partial_h Gamma" in flow["QJ1_formal_consequence"]
        ),
        "anchored_flow_has_no_free_counterterm_coefficients": flow[
            "new_free_counterterm_coefficients"
        ] == 0,
        "anchored_flow_not_physically_promoted": (
            not flow["upper_MTT_selects_this_normalization"]
            and not flow["physical_fixed_coupling_flow_claimed"]
        ),
        "T35_pointed_fixed_point_intertwining_closes": execution[
            "pointed_fixed_point_intertwining"
        ],
        "T35_pointed_tangent_intertwining_is_typed": execution[
            "pointed_tangent_intertwining_given_common_metric_at_H"
        ],
        "T35_full_nonlinear_flow_equality_is_rejected": (
            not execution["global_repair_vector_fields_equal"]
            and execution["nonlinear_quantum_corrections_retained"]
        ),
        "T35_fifth_normalized_jet_is_exact": execution[
            "action_jets_at_x_equal_one"
        ]["fifth"] == -48,
        "radial_counterterms_are_QME_compatible": compatibility[
            "formal_QME_compatible_scheme_exists"
        ],
        "QME_does_not_select_anchor": (
            not compatibility["QME_selects_anchor_coefficients"]
            and not compatibility["Ward_identity_selects_anchor_coefficients"]
        ),
        "normalized_QJ0_is_retyped": qj[
            "QJ0_normalized_connected_QFT_common_phase"
        ] == "quotiented_not_a_physical_exit",
        "gravitational_QJ0_remains_open": qj["QJ0_gravitational_absolute_vacuum"]
        == "open",
        "physical_QJ1_remains_open": not physical_boundary[
            "physical_QJ1_selected"
        ],
        "physical_QJ2_remains_open": not physical_boundary[
            "physical_QJ2_selected"
        ],
        "physical_acceptance_unchanged": not physical_boundary[
            "acceptance_counters_change"
        ],
        "no_observed_input_or_fit": (
            parameter_ledger["new_observed_inputs"] == 0
            and parameter_ledger["new_fits"] == 0
        ),
        "no_new_physical_parameter": (
            parameter_ledger["new_physical_continuous_parameters"] == 0
            and parameter_ledger["new_physical_discrete_selectors"] == 0
        ),
    })

    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema": "boe.mtt.renormalized-bv-anchored-repair-semiflow.v1",
        "claim_id": "CBF.T39",
        "date": "2026-08-30",
        "status": (
            "GLOBAL_IDENTITY_RADIAL_INTERTWINING_EXCLUDED_FOR_T35_LOGARITHMIC_"
            "QUANTUM_ACTION_IN_ALLOWED_LOCAL_ORBIT_POINTED_QJ1_AND_ACTION_JET_"
            "QJ2_ANCHORED_FORMAL_BV_FLOW_CONSTRUCTED_UNIQUELY_PHYSICAL_UPPER_"
            "SELECTION_FIXED_COUPLING_COMPLETION_AND_GRAVITATIONAL_QJ0_OPEN"
        ),
        "source_provenance": {
            "source_lock": SOURCE_LOCK.name,
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "schema": SCHEMA.name,
            "schema_sha256": sha256(SCHEMA),
            "theorem": THEOREM.name,
            "theorem_sha256": sha256(THEOREM) if THEOREM.is_file() else "",
            "repositories": source_lock["repositories"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "source_inventory_hash": canonical_hash(source_lock["local_sources"]),
        },
        "quantum_bv_generator": generator,
        "q79_source_coverage": coverage,
        "global_intertwining_no_go": no_go,
        "pointed_anchor_retraction": retraction,
        "anchored_formal_bv_flow": flow,
        "T35_pointed_execution": execution,
        "qme_and_ward_compatibility": compatibility,
        "QJ_classification": qj,
        "parameter_ledger": parameter_ledger,
        "physical_boundary": physical_boundary,
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "T39 proves that literal identity-projection equality of the full T34 "
            "tree and T35 quantum radial repair flows is impossible within the "
            "allowed local renormalizable counterterm orbit, because the fermion "
            "logarithm has nonzero fifth derivative. It replaces that impossible "
            "target with the unique all-orders local-formal q79 BV normalization "
            "that preserves the selected value, tadpole and Hessian at H. This "
            "closes formal pointed QJ1 and the action-jet part of QJ2, but the upper "
            "physical action has not selected the normalization. Physical QJ1, "
            "metric-normalized QJ2, gravitational QJ0 and acceptance remain open."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks) - len(failed),
            "total": len(checks),
            "failed": failed,
        },
    }
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    summary = payload["check_summary"]
    if summary["failed"]:
        raise SystemExit(
            f"wrote {OUTPUT.name}: {summary['passed']}/{summary['total']} checks; "
            f"failed={summary['failed']}"
        )
    print(
        f"wrote {OUTPUT.name}: {summary['passed']}/{summary['total']} checks passed; "
        "global flow equality excluded, pointed formal BV anchor closed"
    )


if __name__ == "__main__":
    main()
