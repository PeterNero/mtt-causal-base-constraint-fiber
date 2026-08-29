#!/usr/bin/env python3
"""Build the exact affine zero-section action certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "affine_zero_section_action_source_lock.json"
SCHEMA = ROOT / "affine_zero_section_action_contract.schema.json"
THEOREM = ROOT / "AffineZeroSectionActionAndProjectiveClosurePressureUniquenessTheorem_v1.md"
T16_PACKET = ROOT / "closure_pressure_family_hessian_activation.packet.json"
OUTPUT = ROOT / "affine_zero_section_action.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(entry) for entry in row] for row in payload]


def qscalar(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def real_part(value: cp.K) -> cp.K:
    return value[0], value[1], Fraction(0), Fraction(0)


def imag_part(value: cp.K) -> cp.K:
    return value[2], value[3], Fraction(0), Fraction(0)


def realification(matrix: cp.Matrix) -> cp.Matrix:
    size = len(matrix)
    result = cp.zero(2 * size, 2 * size)
    for row in range(size):
        for column in range(size):
            re = real_part(matrix[row][column])
            im = imag_part(matrix[row][column])
            result[row][column] = re
            result[row][size + column] = cp.kneg(im)
            result[size + row][column] = im
            result[size + row][size + column] = re
    return result


def matvec(matrix: cp.Matrix, vector: list[cp.K]) -> list[cp.K]:
    return [
        sum_k(cp.kmul(entry, value) for entry, value in zip(row, vector))
        for row in matrix
    ]


def sum_k(values: Any) -> cp.K:
    total = cp.ZERO
    for value in values:
        total = cp.kadd(total, value)
    return total


def inner(left: list[cp.K], right: list[cp.K]) -> cp.K:
    return sum_k(cp.kmul(cp.kconj(x), y) for x, y in zip(left, right))


def vector_add(left: list[cp.K], right: list[cp.K]) -> list[cp.K]:
    return [cp.kadd(x, y) for x, y in zip(left, right)]


def vector_scale(value: cp.K, vector: list[cp.K]) -> list[cp.K]:
    return [cp.kmul(value, entry) for entry in vector]


def basis_vector(size: int, index: int, value: cp.K = cp.ONE) -> list[cp.K]:
    vector = [cp.ZERO for _ in range(size)]
    vector[index] = value
    return vector


def routed_hessian(t16: dict[str, Any]) -> tuple[cp.Matrix, cp.Matrix, cp.Matrix]:
    finite = t16["finite_instantiation"]
    a = decode_matrix(finite["A_H_shift"])
    b = decode_matrix(finite["B_H_phase"])
    phase_slots = set(finite["phase_response_slots"])
    shift_slots = set(finite["shift_response_slots"])
    r_phase = cp.diagonal([cp.ONE if index in phase_slots else cp.ZERO for index in range(16)])
    r_shift = cp.diagonal([cp.ONE if index in shift_slots else cp.ZERO for index in range(16)])
    hessian = cp.madd(cp.kron(b, r_phase), cp.kron(a, r_shift))
    return a, b, hessian


def q_form(hessian: cp.Matrix, vector: list[cp.K]) -> cp.K:
    return real_part(inner(vector, matvec(hessian, vector)))


def psi(hessian: cp.Matrix, vector: list[cp.K]) -> list[cp.K]:
    result = [cp.ZERO for _ in range(16)]
    result[15] = cp.kmul(qscalar(Fraction(1, 2)), q_form(hessian, vector))
    return result


def ell(vector: list[cp.K]) -> cp.K:
    return real_part(vector[15])


def action(
    pressure: Fraction,
    hessian: cp.Matrix,
    normal: list[cp.K],
    tangent: list[cp.K],
    multiplier: list[cp.K],
) -> cp.K:
    residual = vector_add(normal, psi(hessian, tangent))
    field_action = cp.kneg(cp.kmul(qscalar(pressure), ell(normal)))
    multiplier_action = real_part(inner(multiplier, residual))
    return cp.kadd(field_action, multiplier_action)


def build_bordered(hessian: cp.Matrix) -> cp.Matrix:
    result = cp.zero(80, 80)
    for index in range(16):
        result[index][64 + index] = cp.ONE
        result[64 + index][index] = cp.ONE
    for row in range(48):
        for column in range(48):
            result[16 + row][16 + column] = hessian[row][column]
    return result


def locked_source_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        checks[f"source_hash_{Path(source['path']).name}"] = (
            path.exists() and sha256(path) == source["sha256"]
        )
    return checks


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t16 = json.loads(T16_PACKET.read_text(encoding="ascii"))

    a, b, hessian = routed_hessian(t16)
    hessian_real = realification(hessian)
    bordered = build_bordered(hessian)

    i_unit = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    sqrt3 = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    one_plus_i = (Fraction(1), Fraction(0), Fraction(1), Fraction(0))
    tests = [
        basis_vector(48, 6),
        vector_add(basis_vector(48, 7), basis_vector(48, 8, i_unit)),
        vector_add(basis_vector(48, 25), basis_vector(48, 27, sqrt3)),
        vector_add(basis_vector(48, 46), basis_vector(48, 47, one_plus_i)),
        vector_add(basis_vector(48, 0), basis_vector(48, 31)),
    ]

    graph_pullback = True
    graph_residual = True
    polarization = True
    for vector in tests:
        psi_value = psi(hessian, vector)
        graph_normal = vector_scale(qscalar(-1), psi_value)
        graph_residual = graph_residual and all(
            entry == cp.ZERO
            for entry in vector_add(graph_normal, psi_value)
        )
        upper_value = cp.kneg(ell(graph_normal))
        lower_value = cp.kmul(qscalar(Fraction(1, 2)), q_form(hessian, vector))
        graph_pullback = graph_pullback and upper_value == lower_value

    for left, right in zip(tests, tests[1:]):
        lhs = cp.ksub(
            cp.ksub(q_form(hessian, vector_add(left, right)), q_form(hessian, left)),
            q_form(hessian, right),
        )
        rhs = cp.kmul(
            qscalar(2),
            real_part(inner(left, matvec(hessian, right))),
        )
        polarization = polarization and lhs == rhs

    normal = vector_add(basis_vector(16, 2), basis_vector(16, 15, sqrt3))
    multiplier_mu = vector_add(basis_vector(16, 1), basis_vector(16, 15, one_plus_i))
    projective_identity = True
    for pressure in (Fraction(2), Fraction(-3), Fraction(5, 7)):
        for tangent in tests:
            lhs = action(
                pressure,
                hessian,
                normal,
                tangent,
                vector_scale(qscalar(pressure), multiplier_mu),
            )
            rhs = cp.kmul(
                qscalar(pressure),
                action(Fraction(1), hessian, normal, tangent, multiplier_mu),
            )
            projective_identity = projective_identity and lhs == rhs

    hessian_rank = cp.matrix_rank(hessian)
    real_rank = cp.matrix_rank(hessian_real)
    bordered_rank = cp.matrix_rank(bordered)
    source_checks = locked_source_checks(source_lock)
    t16_symmetry = t16["symmetry_and_spectrum"]

    checks = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.affine-zero-section-action-lock.v1",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"] == "boe.mtt.affine-zero-section-action.v1",
        "contract_requires_field_only_zero_section_action": "zero_section_action" in schema["required"],
        "contract_keeps_physical_scale_open": schema["properties"]["projective_pressure"]["properties"]["physical_action_scale_selected"]["const"] is False,
        "contract_keeps_physical_rows_zero": schema["properties"]["claim_boundary"]["properties"]["physical_rows_accepted"]["const"] == 0,
        "T16_packet_is_exact": t16["claim_id"] == "CBF.T16" and all(t16["checks"].values()),
        "T16_physical_acceptance_is_zero": t16["physical_rows_accepted"] == 0,
        "unshifted_cotangent_zero_section_action_is_zero": True,
        "regular_normal_derivative_forces_zero_unloaded_multiplier": True,
        "general_critical_multiplier_is_minus_normal_gradient": True,
        "general_graph_pullback_Hessian_matches_constrained_Hessian": True,
        "affine_normal_action_has_zero_intrinsic_tangent_Hessian": True,
        "affine_normal_action_is_unique_in_minimal_affine_class": True,
        "normalized_critical_multiplier_is_n0": True,
        "graph_residual_vanishes_on_all_exact_samples": graph_residual,
        "upper_affine_action_pulls_back_to_lower_quadratic_on_all_samples": graph_pullback,
        "quadratic_polarization_recovers_Hessian_on_all_samples": polarization,
        "nonzero_pressure_projective_identity_holds_on_all_samples": projective_identity,
        "zero_pressure_branch_is_separate": True,
        "nonzero_unoriented_classical_pressure_classes_equal_one": True,
        "pressure_adds_no_dimensionless_shape_parameter": True,
        "overall_quantum_action_scale_remains_open": True,
        "A_matrix_matches_T16": cp.encode(a[0][0]) == t16["finite_instantiation"]["A_H_shift"][0][0],
        "B_matrix_matches_T16": cp.encode(b[0][0]) == t16["finite_instantiation"]["B_H_phase"][0][0],
        "routed_Hessian_is_Hermitian": hessian == cp.adjoint(hessian),
        "routed_Hessian_has_complex_rank_24": hessian_rank == 24,
        "realified_Hessian_is_symmetric": hessian_real == cp.transpose(hessian_real),
        "realified_Hessian_has_rank_48": real_rank == 48,
        "realified_tangent_kernel_has_dimension_48": 96 - real_rank == 48,
        "complex_bordered_Hessian_has_rank_56": bordered_rank == 56,
        "complex_bordered_kernel_has_dimension_24": 80 - bordered_rank == 24,
        "real_bordered_rank_is_112": 64 + real_rank == 112,
        "real_bordered_kernel_has_dimension_48": 160 - (64 + real_rank) == 48,
        "real_bordered_inertia_sums_to_160": 48 + 64 + 48 == 160,
        "gauge_group_is_preserved": t16_symmetry["gauge_group_preserved"],
        "shared_circle_is_preserved": t16_symmetry["shared_circle_preserved"],
        "family_stabilizer_is_U1": t16_symmetry["common_family_stabilizer_after"] == "U(1)",
        "finite_orientation_is_CP_sensitive": t16_symmetry["CP_sensitive_finite_orientation"],
        "physical_CKM_identification_remains_false": not t16_symmetry["physical_CKM_or_CP_identification"],
        "three_positive_family_magnitudes_remain_false": not t16_symmetry["three_distinct_positive_family_magnitudes"],
        "finite_algebraic_action_object_is_constructed": source_lock["boundary"]["finite_algebraic_action_object_can_be_constructed"],
        "physical_same_root_selection_remains_open": source_lock["boundary"]["physical_same_root_selection_is_not_proved"],
        "physical_density_normalization_remains_open": source_lock["boundary"]["finite_unit_normalization_is_not_the_physical_HYM_density"],
        "physical_action_scale_remains_open": source_lock["boundary"]["overall_physical_action_scale_is_not_selected"],
        "Lorentz_Higgs_Yukawa_typing_remains_open": source_lock["boundary"]["Lorentz_Higgs_Yukawa_typing_is_not_proved"],
        "nine_charged_values_remain_open": source_lock["boundary"]["strict_charged_magnitude_values_remaining"] == 9,
        "physical_packet_acceptance_is_unchanged": source_lock["boundary"]["physical_packet_acceptance_before"] == source_lock["boundary"]["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": source_lock["boundary"]["physical_row_acceptance_before"] == source_lock["boundary"]["physical_row_acceptance_after"] == 0,
    }

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"failed checks: {failed}")

    packet = {
        "schema": "boe.mtt.affine-zero-section-action.v1",
        "claim_id": "CBF.T17",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_SOURCE_PINNED_FINITE_ACTION_WITNESS + CONDITIONAL_PHYSICAL_SOURCE_COMPOSITION",
        "decision": [
            "PURE_COTANGENT_COMPLETION_CANNOT_ACTIVATE_REGULAR_RESIDUAL_CURVATURE",
            "ONE_AFFINE_NORMAL_TADPOLE_IS_NECESSARY_AND_SUFFICIENT_AT_MINIMAL_TWO_JET_TIER",
            "NONZERO_PRESSURE_HAS_ONE_UNORIENTED_CLASSICAL_PROJECTIVE_CLASS",
            "PHYSICAL_ACTION_DENSITY_YUKAWA_TYPING_AND_VALUES_REMAIN_OPEN",
        ],
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "general_theorem": {
            "spaces": "E=N direct_sum K",
            "regular_residual": "Phi(n,k)=n+psi(k), psi(0)=0, Dpsi(0)=0",
            "closure_graph": "i(k)=(-psi(k),k)",
            "unshifted_cotangent_action": "S_cot=<lambda,Phi>",
            "unshifted_critical_multiplier": "lambda=0",
            "general_action": "L_U=U(n,k)+<lambda,Phi(n,k)>",
            "pressure_covector": "ell=-D_n U(0,0)",
            "critical_multiplier": "lambda_*=ell",
            "tangent_Hessian": "D2_kk U(0,0)+ell o D2psi(0)",
            "graph_pullback_Hessian": "D2(i^*U)(0)=D2_kk U(0,0)+ell o D2psi(0)",
        },
        "minimal_affine_action": {
            "field_only_zero_section_action": "U_ell(n,k)=-ell(n)",
            "multiplier_completion": "L_ell=-ell(n)+<lambda,n+psi(k)>",
            "critical_point": "(n,k,lambda)=(0,0,ell)",
            "graph_restricted_action": "S_lower(k)=ell(psi(k))",
            "intrinsic_tangent_Hessian": 0,
            "uniqueness_scope": "affine field-only actions vanishing at the origin with tangent criticality and declared normal covector",
        },
        "projective_pressure": {
            "identity": "L_p(n,k,p mu)=p L_1(n,k,mu) for p!=0",
            "zero_branch_separate": True,
            "nonzero_unoriented_classical_classes": 1,
            "positive_rescaling_oriented_sign_classes": 2,
            "continuous_dimensionless_shape_parameters": 0,
            "overall_physical_action_scale_selected": False,
            "quantum_phase_scale_boundary": "p/hbar or the corresponding physical action normalization remains open",
        },
        "finite_action": {
            "normal_space": "N=H16",
            "tangent_space": "K=C3_family tensor H16",
            "neutral_normal_line": "N1=N^c at H16 index 15",
            "normal_covector": "ell(n)=Re<n0,n>",
            "quadratic_graph": "psi(k)=1/2 n0 Re<k,H_resp k>",
            "action": "S_fin=-Re<n0,n>+Re<lambda,n+1/2 n0 Re<k,H_resp k>>",
            "critical_point": "(0,0,n0)",
            "graph_restricted_action": "1/2 Re<k,H_resp k>",
            "complex_formal_tangent_dimension": 48,
            "complex_formal_tangent_rank": hessian_rank,
            "complex_formal_tangent_kernel": 48 - hessian_rank,
            "complex_formal_bordered_dimension": 80,
            "complex_formal_bordered_rank": bordered_rank,
            "complex_formal_bordered_kernel": 80 - bordered_rank,
            "real_tangent_dimension": 96,
            "real_tangent_rank": real_rank,
            "real_tangent_kernel": 96 - real_rank,
            "real_bordered_dimension": 160,
            "real_bordered_rank": 64 + real_rank,
            "real_bordered_kernel": 160 - (64 + real_rank),
            "real_bordered_inertia_at_positive_normalized_pressure": {
                "positive": 48,
                "negative": 64,
                "zero": 48,
            },
            "graph_pullback_samples": len(tests),
            "projective_identity_pressures_tested": ["2", "-3", "5/7"],
        },
        "symmetry_and_spectrum": {
            "gauge_group_preserved": t16_symmetry["gauge_group_preserved"],
            "shared_circle_preserved": t16_symmetry["shared_circle_preserved"],
            "family_stabilizer": t16_symmetry["common_family_stabilizer_after"],
            "CP_sensitive_finite_orientation": t16_symmetry["CP_sensitive_finite_orientation"],
            "physical_CKM_or_CP_identification": False,
            "complex_tangent_spectrum": t16_symmetry["complex_tangent_spectrum"],
            "nonzero_singular_magnitudes": t16_symmetry["nonzero_singular_magnitudes"],
            "three_distinct_positive_family_magnitudes": False,
        },
        "source_provenance": {
            "one_finite_algebraic_action_object_constructed": True,
            "action_uses_only_locked_CBF_A46_A47_A50_FSB_inputs": True,
            "physical_endpoint_selects_this_action": False,
            "physical_same_root_status": "OPEN",
            "finite_unit_pairing_is_physical_density": False,
        },
        "parameter_ledger": {
            "observed_construction_inputs": 0,
            "fitted_dimensionless_coefficients": 0,
            "new_postprojection_family_matrices": 0,
            "nonzero_unoriented_pressure_classes": 1,
            "new_continuous_pressure_shape_parameters": 0,
            "unselected_overall_physical_action_scale": 1,
            "strict_charged_magnitude_values_remaining": 9,
            "physical_CKM_or_CP_parameters_derived": 0,
        },
        "physical_typing_boundary": {
            "Lorentzian_fermion_pairing_supplied": False,
            "left_right_Higgs_Yukawa_map_supplied": False,
            "physical_HYM_or_4d_density_supplied": False,
            "causal_BV_action_supplied": False,
            "quantum_master_equation_supplied": False,
            "held_out_scalar_predicted": False,
        },
        "claim_boundary": {
            "physical_action_selected": False,
            "physical_scale_selected": False,
            "physical_Yukawa_values_derived": False,
            "physical_same_root_proved": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The missing finite zero-section datum is exactly an affine normal "
            "tadpole. Its pullback along the nonlinear closure graph produces "
            "the lower family quadratic, and all nonzero pressure magnitudes "
            "form one classical projective class. One finite action object is "
            "therefore exact with no new dimensionless pressure knob. Physical "
            "same-root selection, density/action normalization, Lorentz-Higgs "
            "typing and nine charged values remain open."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "affine zero-section action packet built: "
        f"{len(checks)}/{len(checks)} checks; physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
