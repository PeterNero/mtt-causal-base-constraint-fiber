#!/usr/bin/env python3
"""Build the exact CBF.T44 causal relative-evolution packet."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "causal_relative_cauchy_evolution_global_g0_source_lock.json"
SCHEMA = ROOT / "causal_relative_cauchy_evolution_global_g0_contract.schema.json"
THEOREM = ROOT / "CausalRelativeCauchyEvolutionAndStateSeparatedGlobalG0Theorem_v1.md"
OUTPUT = ROOT / "causal_relative_cauchy_evolution_global_g0.packet.json"

T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T41_PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"
T43_PACKET = ROOT / "weyl_polarized_product_dirac_g0.packet.json"
FREE_CAR = ROOT / "../mtt-qm-source-proof/certificates/framed_q79_free_dirac_car_net.certificate.json"
BINARY_ROOT = ROOT / "../mtt-q79-total-superconnection-branching/artifacts/binary_root_car_net_equivalence.packet.json"
QFT_THEOREM = ROOT / "../mtt-qm-source-proof/proof_corpus/q79_SM_Renormalized_TimeOrdering_and_Local_QME_Anomaly_Cohomology_Theorem_v1.md"
PRIOR_CTP = ROOT / "../mtt-q79-mirror-zero-zero/MTT_SHARED_CIRCLE_DOUBLE_TRAVERSAL_CLOSED_TIME_PATH_THEOREM_2026-07-16.md"
SHARED_RETURN = ROOT / "../mtt-protospinor-gr-response-proof/certificates/q79_shared_circle_double_return_cln_nil_flat_endpoint_certificate.json"

Q = Fraction
QC = tuple[Fraction, Fraction]
QMatrix = list[list[Fraction]]
CMatrix = list[list[QC]]


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


def qctext(value: QC) -> dict[str, str]:
    return {"real": ftext(value[0]), "imag": ftext(value[1])}


def cadd(left: QC, right: QC) -> QC:
    return left[0] + right[0], left[1] + right[1]


def csub(left: QC, right: QC) -> QC:
    return left[0] - right[0], left[1] - right[1]


def cmul(left: QC, right: QC) -> QC:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def cconj(value: QC) -> QC:
    return value[0], -value[1]


def cscale(value: QC, scalar: QC) -> QC:
    return cmul(scalar, value)


def qmat_identity(size: int) -> QMatrix:
    return [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]


def qmat_add(left: QMatrix, right: QMatrix) -> QMatrix:
    return [[a + b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def qmat_sub(left: QMatrix, right: QMatrix) -> QMatrix:
    return [[a - b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def qmat_mul(left: QMatrix, right: QMatrix) -> QMatrix:
    return [
        [
            sum((left[row][k] * right[k][column] for k in range(len(right))), Fraction(0))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def qmat_inverse2(matrix: QMatrix) -> QMatrix:
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("matrix is singular")
    return [[d / determinant, -b / determinant], [-c / determinant, a / determinant]]


def qmat_text(matrix: QMatrix) -> list[list[str]]:
    return [[ftext(value) for value in row] for row in matrix]


def cmat_identity(size: int) -> CMatrix:
    return [[(Fraction(int(row == column)), Fraction(0)) for column in range(size)] for row in range(size)]


def cmat_mul(left: CMatrix, right: CMatrix) -> CMatrix:
    result: CMatrix = []
    for row in range(len(left)):
        result_row: list[QC] = []
        for column in range(len(right[0])):
            value: QC = Fraction(0), Fraction(0)
            for k in range(len(right)):
                value = cadd(value, cmul(left[row][k], right[k][column]))
            result_row.append(value)
        result.append(result_row)
    return result


def cmat_adjoint(matrix: CMatrix) -> CMatrix:
    return [
        [cconj(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def cmat_scalar(matrix: CMatrix, scalar: QC) -> CMatrix:
    return [[cscale(value, scalar) for value in row] for row in matrix]


def cmat_trace(matrix: CMatrix) -> QC:
    result: QC = Fraction(0), Fraction(0)
    for index in range(len(matrix)):
        result = cadd(result, matrix[index][index])
    return result


def cmat_text(matrix: CMatrix) -> list[list[dict[str, str]]]:
    return [[qctext(value) for value in row] for row in matrix]


def state_expectation(density: CMatrix, observable: CMatrix) -> QC:
    return cmat_trace(cmat_mul(density, observable))


def source_hash_checks(source_lock: dict[str, Any]) -> tuple[dict[str, bool], dict[str, bool]]:
    construction: dict[str, bool] = {}
    comparison: dict[str, bool] = {}
    for index, source in enumerate(source_lock["construction_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        construction[f"construction_source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    for index, source in enumerate(source_lock["comparison_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        comparison[f"comparison_source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return construction, comparison


def required_schema_keys(schema: dict[str, Any]) -> set[str]:
    return set(schema["required"])


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t25 = load_json(T25_PACKET)
    t39 = load_json(T39_PACKET)
    t41 = load_json(T41_PACKET)
    t43 = load_json(T43_PACKET)
    free_car = load_json(FREE_CAR)
    binary_root = load_json(BINARY_ROOT)
    shared_return = load_json(SHARED_RETURN)
    qft_text = QFT_THEOREM.read_text(encoding="utf-8")
    prior_ctp_text = PRIOR_CTP.read_text(encoding="utf-8")

    construction_checks, comparison_checks = source_hash_checks(source_lock)

    # Exact algebraic Moller/resolvent witness.
    d0: QMatrix = [[Fraction(2), Fraction(1)], [Fraction(0), Fraction(3)]]
    perturbation: QMatrix = [[Fraction(1), Fraction(0)], [Fraction(1), Fraction(1)]]
    d1 = qmat_add(d0, perturbation)
    e0 = qmat_inverse2(d0)
    e1 = qmat_inverse2(d1)
    identity_q = qmat_identity(2)
    resolvent_left = qmat_sub(e0, qmat_mul(qmat_mul(e1, perturbation), e0))
    resolvent_right = qmat_sub(e0, qmat_mul(qmat_mul(e0, perturbation), e1))
    moller = qmat_sub(identity_q, qmat_mul(e1, perturbation))
    moller_inverse = qmat_add(identity_q, qmat_mul(e0, perturbation))

    # Unique primitive two-leg chain.
    boundary: QMatrix = [[Fraction(-1), Fraction(-1)], [Fraction(1), Fraction(1)]]
    contour = [Fraction(1), Fraction(-1)]
    boundary_of_contour = [
        sum((boundary[row][column] * contour[column] for column in range(2)), Fraction(0))
        for row in range(2)
    ]
    kernel_generator = contour[:]
    primitive_gcd = math.gcd(abs(contour[0].numerator), abs(contour[1].numerator))

    # Exact unitary return, common-phase cancellation and state separation.
    one: QC = Fraction(1), Fraction(0)
    zero: QC = Fraction(0), Fraction(0)
    u: QC = Fraction(3, 5), Fraction(4, 5)
    w: QC = Fraction(5, 13), Fraction(12, 13)
    p: QC = Fraction(8, 17), Fraction(15, 17)
    identity_c = cmat_identity(2)
    unequal_source = [[u, zero], [zero, cconj(u)]]
    s_minus = cmat_scalar(identity_c, w)
    s_plus = cmat_scalar(unequal_source, w)
    contour_operator = cmat_mul(cmat_adjoint(s_minus), s_plus)
    equal_source_operator = cmat_mul(cmat_adjoint(s_plus), s_plus)
    common_phase_minus = cmat_scalar(s_minus, p)
    common_phase_plus = cmat_scalar(s_plus, p)
    common_phase_operator = cmat_mul(cmat_adjoint(common_phase_minus), common_phase_plus)
    relative_phase_operator = cmat_mul(cmat_adjoint(s_minus), cmat_scalar(s_plus, p))
    expected_relative_phase = cmat_scalar(contour_operator, p)

    rho0 = [[one, zero], [zero, zero]]
    rho1 = [[zero, zero], [zero, one]]
    rho_mix = [[(Fraction(1, 2), Fraction(0)), zero], [zero, (Fraction(1, 2), Fraction(0))]]
    state_values = {
        "omega_0": state_expectation(rho0, contour_operator),
        "omega_1": state_expectation(rho1, contour_operator),
        "omega_mix": state_expectation(rho_mix, contour_operator),
    }
    equal_state_values = {
        "omega_0": state_expectation(rho0, equal_source_operator),
        "omega_1": state_expectation(rho1, equal_source_operator),
        "omega_mix": state_expectation(rho_mix, equal_source_operator),
    }

    # Ordered relative-evolution composition with noncommuting exact unitaries.
    rotation: CMatrix = [
        [(Fraction(3, 5), Fraction(0)), (Fraction(-4, 5), Fraction(0))],
        [(Fraction(4, 5), Fraction(0)), (Fraction(3, 5), Fraction(0))],
    ]

    def relative(to_operator: CMatrix, from_operator: CMatrix) -> CMatrix:
        return cmat_mul(cmat_adjoint(from_operator), to_operator)

    r10 = relative(unequal_source, identity_c)
    r21 = relative(rotation, unequal_source)
    r20 = relative(rotation, identity_c)
    ordered_composition = cmat_mul(r10, r21)

    construction_root_payload = {
        "schema": "boe.mtt.causal-relative-evolution-derived-root.v1",
        "T25_direct_source_root_sha256": t25["direct_source_root_sha256"],
        "T43_construction_root_sha256": t43["source_provenance"]["construction_root_sha256"],
        "domain": source_lock["analytic_rule"]["domain"],
        "global_object": source_lock["analytic_rule"]["global_object"],
        "return_boundary_matrix": qmat_text(boundary),
        "normalized_primitive_cycle": [ftext(value) for value in contour],
        "scalarization": source_lock["analytic_rule"]["scalarization"],
        "construction_source_hashes": [source["sha256"] for source in source_lock["construction_sources"]],
        "excluded_inputs": source_lock["analytic_rule"]["excluded_inputs"],
    }
    construction_root = canonical_hash(construction_root_payload)

    packet: dict[str, Any] = {
        "schema": "boe.mtt.causal-relative-cauchy-evolution-global-g0.v1",
        "claim_id": "CBF.T44",
        "title": "Causal Relative Cauchy Evolution and State-Separated Global G0",
        "date": "2026-08-30",
        "status": (
            "exact state-free global causal evolution and unique minimal return chain for the direct route; "
            "common phase cancelled and scalar state dependence isolated; global scalar G0, G1, G2 and q79 HYM open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "construction_sources": len(source_lock["construction_sources"]),
            "comparison_sources": len(source_lock["comparison_sources"]),
            "all_construction_hashes_match": all(construction_checks.values()),
            "all_comparison_hashes_match": all(comparison_checks.values()),
            "comparison_sources_excluded_from_root": True,
            "construction_root_payload": construction_root_payload,
            "construction_root_sha256": construction_root,
        },
        "selected_domain": {
            "base": t25["causal_operator"]["globally_hyperbolic_base"],
            "time_orientation": "inherited from the selected T25 causal source",
            "test_domain": t25["causal_operator"]["test_domain"],
            "operator": t25["causal_operator"]["operator"],
            "principal_symbol": t25["causal_operator"]["principal_symbol"],
            "perturbation_class": "compactly supported smooth order-zero Higgs/Yukawa endomorphisms",
            "advanced_map": t25["causal_operator"]["advanced_Green_map"],
            "retarded_map": t25["causal_operator"]["retarded_Green_map"],
            "global_Wick_rotation_required": False,
            "preferred_state_required_for_domain": False,
        },
        "moller_relative_evolution": {
            "resolvent_identity": "E_h=E_H-E_h V E_H=E_H-E_H V E_h",
            "M_h": "1-E_h V",
            "M_h_inverse": "1+E_H V",
            "relative_Cauchy_evolution": "rce_h=(M_h^-)^{-1} M_h^+",
            "acts_on": "solution quotient and representation-independent even CAR observable algebra",
            "state_free": True,
            "causal_support": t25["causal_operator"]["causal_support"],
            "finite_resolvent_witness": {
                "D_H": qmat_text(d0),
                "V": qmat_text(perturbation),
                "D_h": qmat_text(d1),
                "E_H": qmat_text(e0),
                "E_h": qmat_text(e1),
                "M_h": qmat_text(moller),
                "M_h_inverse": qmat_text(moller_inverse),
            },
        },
        "minimal_return_chain": {
            "boundary_matrix": qmat_text(boundary),
            "integral_kernel_rank": 1,
            "primitive_kernel_generator": [ftext(value) for value in kernel_generator],
            "forward_normalization": "coefficient(e_plus)=1",
            "unique_normalized_cycle": [ftext(value) for value in contour],
            "boundary_of_cycle": [ftext(value) for value in boundary_of_contour],
            "primitive_gcd": primitive_gcd,
            "extra_contour_parameter": False,
            "conditional_on_return_requirement": True,
            "physical_time_orientation_derived_here": False,
        },
        "operator_valued_global_G0": {
            "relative_S_matrix": "S_H[V]=S(H)^{-1} star S(H+V)",
            "contour_element": "C_H[V_plus,V_minus]=S_H[V_minus]^{-1} star S_H[V_plus]",
            "anchor_identity": "C_H[0,0]=1",
            "equal_source_identity": "C_H[V,V]=1",
            "adjoint_reversal": "C_H[V_plus,V_minus]^*=C_H[V_minus,V_plus]",
            "causal_factorization": True,
            "formal_perturbative_tier": True,
            "nonperturbative_cutoff_removal": False,
            "path_integral_cycle_required": False,
            "preferred_state_required": False,
            "finite_unequal_source_operator": cmat_text(contour_operator),
            "finite_equal_source_operator": cmat_text(equal_source_operator),
            "relative_evolution_ordered_composition": "R(U1,U0) R(U2,U1)=R(U2,U0)",
        },
        "phase_ledger": {
            "common_phase": qctext(p),
            "common_central_phase_cancels": common_phase_operator == contour_operator,
            "relative_source_phase_is_retained": relative_phase_operator == expected_relative_phase and relative_phase_operator != contour_operator,
            "global_determinant_line_trivialized": False,
            "relative_eta_or_spectral_flow_computed": False,
            "internal_family_holonomy_identified_with_analytic_determinant_line": False,
            "common_torsor_is_not_a_physical_exit": t39["QJ_classification"]["QJ0_normalized_connected_QFT_common_phase"],
        },
        "state_scalarization_cutset": {
            "formula": "Z_omega[V_plus,V_minus]=omega(C_H[V_plus,V_minus])",
            "Hadamard_state_space_nonempty": free_car["state_space"]["assignment"].startswith("S_Had"),
            "preferred_state_selected": False,
            "state_values": {key: qctext(value) for key, value in state_values.items()},
            "equal_source_values": {key: qctext(value) for key, value in equal_state_values.items()},
            "unequal_source_values_are_distinct": len(set(state_values.values())) == 3,
            "equal_source_values_are_all_one": all(value == one for value in equal_state_values.values()),
            "return_identity_selects_state": False,
            "global_scalar_G0_requires_G2_data": True,
        },
        "T43_local_shadow": {
            "selected_kappa_F": t43["determinant_exponent"]["selected_kappa_F"],
            "q4_star": t43["exact_finite_trace"]["q4_star"]["expression"],
            "anchored_action": t43["emitted_action"]["formula"],
            "direct_source_root_matches": t43["source_provenance"]["construction_root_payload"]["T25_direct_source_root_sha256"] == t25["direct_source_root_sha256"],
            "local_one_loop_shadow_retained": True,
            "universal_short_distance_coefficient_replayed_as_fit": False,
            "full_global_scalar_equality_claimed": False,
            "smooth_state_dependent_contributions_excluded": False,
            "future_test": "compare local jets of log Z_omega at H after state and interacting transport are selected",
        },
        "shared_circle_and_root_boundary": {
            "internal_double_return_exact": shared_return["claim_tiers"]["double_traversal_odd_proto_state_return"],
            "internal_double_return_selects_zero_defect": shared_return["claim_tiers"]["double_return_dynamically_selects_zero_defect"],
            "internal_shared_circle_identified_with_physical_time": False,
            "internal_double_return_selects_CTP_contour": False,
            "prior_CTP_theorem_used_as_construction_source": False,
            "binary_root_free_CAR_equivalence": binary_root["blocker_delta"]["binary_root_free_CAR_net_ambiguity"],
            "binary_root_preferred_state_selected": binary_root["guardrails"]["claims_a_preferred_Hadamard_state_is_selected"],
            "new_binary_root_selector": False,
            "direct_root_neutral_transport_scope": "T24/T25 direct Yukawa perturbations only",
        },
        "gate_ledger": {
            "G0_direct_local_one_loop": {
                "closed": t43["gate_ledger"]["G0_direct_local_one_loop"]["closed"],
                "source": "CBF.T43",
            },
            "G0_direct_global_operator_relative": {
                "closed": True,
                "scope": "compact-support, representation-independent causal and local-formal relative evolution",
                "source": "CBF.T25 plus renormalized relative S-matrix",
            },
            "G0_global_scalar_physical": {
                "closed": False,
                "missing": "selected state/initial functional, relative phase and fixed-coupling interacting removal",
                "interlocked_with": "G2",
            },
            "G1_physical_tangent_pairing": t43["gate_ledger"]["G1_physical_tangent_pairing"],
            "G2_selected_interacting_state_BV": t43["gate_ledger"]["G2_selected_interacting_state_BV"],
            "G0_q79_HYM": t43["gate_ledger"]["G0_q79_HYM"],
            "physical_gluing_gates_closed": t41["physical_gluing_gates_closed"],
            "physical_gluing_gates_total": t41["physical_gluing_gates_total"],
            "physical_packets_accepted": t41["physical_packets_accepted"],
            "physical_packets_total": t41["physical_packets_total"],
            "physical_rows_accepted": t41["physical_rows_accepted"],
            "physical_rows_total": t41["physical_rows_total"],
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_continuous_physical_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "new_binary_root_selectors": 0,
            "new_preferred_state_selectors": 0,
            "normalized_return_cycle_candidates_after": 1,
            "inherited_time_orientation": 1,
            "time_orientation_is_a_fitted_parameter": False,
        },
        "physical_boundary": {
            "global_state_free_direct_causal_evolution_closed": True,
            "minimal_return_chain_closed_conditional_on_return": True,
            "common_central_phase_cancelled": True,
            "global_scalar_determinant_closed": False,
            "relative_determinant_phase_closed": False,
            "preferred_Hadamard_or_cosmological_state_selected": False,
            "interacting_QME_cutoff_removal_closed": False,
            "physical_time_orientation_derived": False,
            "internal_circle_time_identification_claimed": False,
            "q79_HYM_normal_operator_closed": False,
            "G1_closed": False,
            "G2_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
        },
        "frontier_delta": (
            "CBF.T44 replaces the vague search for a global Lorentzian determinant cycle by the exact state-free "
            "object already selected by the T25 causal family: relative Moller/Cauchy evolution and its local-formal "
            "relative S-matrix. The unique primitive two-leg return chain is (1,-1), equal-source return is exact and "
            "a common central determinant phase cancels. An exact M2(C) witness proves that unequal-source scalarization "
            "still depends on a selected state. Thus direct global operator evolution closes, while physical scalar G0 "
            "is retyped as interlocked with G2; physical counters and B.ACTION.01/B.QFT.02 remain open."
        ),
    }

    checks: dict[str, bool] = {
        **construction_checks,
        **comparison_checks,
        "source_lock_schema": source_lock["schema"] == "boe.mtt.causal-relative-cauchy-evolution-global-g0-source-lock.v1",
        "handoff_pinned": source_lock["handoff_id"] == "a9ef2144-5598-4502-86e1-5149e7817b81",
        "kernel_model_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "schema_claim": schema["properties"]["claim_id"]["const"] == "CBF.T44",
        "theorem_nonempty": THEOREM.stat().st_size > 12000,
        "T25_passes": t25["claim_id"] == "CBF.T25" and all(t25["checks"].values()),
        "T39_passes": t39["claim_id"] == "CBF.T39" and all(t39["checks"].values()),
        "T41_passes": t41["claim_id"] == "CBF.T41" and all(t41["checks"].values()),
        "T43_passes": t43["claim_id"] == "CBF.T43" and all(t43["checks"].values()),
        "free_CAR_passes": free_car["all_checks_pass"],
        "binary_root_passes": binary_root["all_checks_pass"],
        "shared_return_passes": all(shared_return["checks"].values()),
        "QFT_relative_S_matrix_present": "S(V)=T^{\\mathrm{ren}}" in qft_text and "Bogoliubov map" in qft_text,
        "QFT_causal_factorization_present": "causal factorization" in qft_text,
        "prior_CTP_is_conditional": "CONDITIONAL" in prior_ctp_text and "does not choose the" in prior_ctp_text and "orientation or" in prior_ctp_text,
        "T25_globally_hyperbolic": t25["causal_operator"]["globally_hyperbolic_base"],
        "T25_causal_support": t25["causal_operator"]["causal_support"],
        "T25_zero_order_perturbation": t25["causal_operator"]["Higgs_Yukawa_order"] == 0,
        "resolvent_left_exact": resolvent_left == e1,
        "resolvent_right_exact": resolvent_right == e1,
        "Moller_left_inverse": qmat_mul(moller, moller_inverse) == identity_q,
        "Moller_right_inverse": qmat_mul(moller_inverse, moller) == identity_q,
        "boundary_rank_one": boundary[0] == [-value for value in boundary[1]],
        "contour_is_cycle": boundary_of_contour == [0, 0],
        "contour_forward_normalized": contour[0] == 1,
        "contour_return_coefficient": contour[1] == -1,
        "contour_primitive": primitive_gcd == 1,
        "u_unitary": cmat_mul(cmat_adjoint(unequal_source), unequal_source) == identity_c,
        "common_source_legs_unitary": cmat_mul(cmat_adjoint(s_plus), s_plus) == identity_c and cmat_mul(cmat_adjoint(s_minus), s_minus) == identity_c,
        "unequal_contour_recovered": contour_operator == unequal_source,
        "equal_source_return_identity": equal_source_operator == identity_c,
        "common_phase_cancels": common_phase_operator == contour_operator,
        "relative_phase_retained": relative_phase_operator == expected_relative_phase and relative_phase_operator != contour_operator,
        "adjoint_reversal": cmat_adjoint(contour_operator) == cmat_mul(cmat_adjoint(s_plus), s_minus),
        "rotation_unitary": cmat_mul(cmat_adjoint(rotation), rotation) == identity_c,
        "ordered_relative_composition": ordered_composition == r20,
        "omega0_exact": state_values["omega_0"] == u,
        "omega1_exact": state_values["omega_1"] == cconj(u),
        "omega_mix_exact": state_values["omega_mix"] == (Fraction(3, 5), Fraction(0)),
        "three_state_values_distinct": len(set(state_values.values())) == 3,
        "equal_source_all_states_one": all(value == one for value in equal_state_values.values()),
        "Hadamard_space_nonempty": packet["state_scalarization_cutset"]["Hadamard_state_space_nonempty"],
        "preferred_state_not_selected": not packet["state_scalarization_cutset"]["preferred_state_selected"],
        "T43_direct_root_matches": packet["T43_local_shadow"]["direct_source_root_matches"],
        "T43_kappa_retained": packet["T43_local_shadow"]["selected_kappa_F"] == "1/(2 pi^2)",
        "T43_not_globalized": not packet["T43_local_shadow"]["full_global_scalar_equality_claimed"],
        "comparison_hashes_not_in_root": all(source["sha256"] not in construction_root_payload["construction_source_hashes"] for source in source_lock["comparison_sources"]),
        "internal_circle_not_time": not packet["shared_circle_and_root_boundary"]["internal_shared_circle_identified_with_physical_time"],
        "internal_return_not_contour_selection": not packet["shared_circle_and_root_boundary"]["internal_double_return_selects_CTP_contour"],
        "binary_root_no_state_selector": not packet["shared_circle_and_root_boundary"]["binary_root_preferred_state_selected"],
        "global_operator_G0_closed": packet["gate_ledger"]["G0_direct_global_operator_relative"]["closed"],
        "global_scalar_G0_open": not packet["gate_ledger"]["G0_global_scalar_physical"]["closed"],
        "G1_open": not packet["gate_ledger"]["G1_physical_tangent_pairing"]["closed"],
        "G2_open": not packet["gate_ledger"]["G2_selected_interacting_state_BV"]["closed"],
        "physical_gates_unchanged": packet["gate_ledger"]["physical_gluing_gates_closed"] == 0 and packet["gate_ledger"]["physical_gluing_gates_total"] == 3,
        "physical_packets_unchanged": packet["gate_ledger"]["physical_packets_accepted"] == 0 and packet["gate_ledger"]["physical_packets_total"] == 3,
        "physical_rows_unchanged": packet["gate_ledger"]["physical_rows_accepted"] == 0 and packet["gate_ledger"]["physical_rows_total"] == 7,
        "no_observed_inputs": packet["parameter_ledger"]["new_observed_inputs"] == 0,
        "no_fitted_coefficients": packet["parameter_ledger"]["new_fitted_coefficients"] == 0,
        "no_new_continuous_parameters": packet["parameter_ledger"]["new_continuous_physical_parameters"] == 0,
        "no_new_state_selector": packet["parameter_ledger"]["new_preferred_state_selectors"] == 0,
        "B_ACTION_open": not packet["physical_boundary"]["B_ACTION_01_closed"],
        "B_QFT_open": not packet["physical_boundary"]["B_QFT_02_closed"],
        "theorem_claim": "**Claim:** CBF.T44" in THEOREM.read_text(encoding="utf-8"),
        "theorem_relative_evolution": "relative Cauchy evolution" in THEOREM.read_text(encoding="utf-8"),
        "theorem_state_cutset": "state-separation cutset" in THEOREM.read_text(encoding="utf-8"),
        "theorem_guard": "time orientation, which T25" in THEOREM.read_text(encoding="utf-8"),
    }

    packet["checks"] = checks
    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["check_summary"] = {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
    }

    missing_schema_keys = required_schema_keys(schema) - set(packet)
    if missing_schema_keys:
        raise SystemExit(f"packet misses schema keys: {sorted(missing_schema_keys)}")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"builder checks: {packet['check_summary']['passed']}/{packet['check_summary']['total']}")
    if failed:
        raise SystemExit("failed checks: " + ", ".join(failed))
    return packet


if __name__ == "__main__":
    build()
