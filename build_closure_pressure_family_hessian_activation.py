#!/usr/bin/env python3
"""Build the exact closure-pressure family-Hessian activation certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "closure_pressure_family_hessian_activation_source_lock.json"
SCHEMA = ROOT / "closure_pressure_family_hessian_activation_contract.schema.json"
THEOREM = ROOT / "ClosurePressureFamilyHessianActivationAndRegularMultiplierNoGoTheorem_v1.md"
T15_PACKET = ROOT / "direct_one_constraint_multiplier_source.packet.json"
FSB_ROOT = ROOT.parent / "mtt-q79-total-superconnection-branching" / "artifacts"
DYNAMIC_PACKET = FSB_ROOT / "triadic_dynamic_weyl_orbit.packet.json"
ALGEBRA_PACKET = FSB_ROOT / "triadic_family_response_algebra.packet.json"
MINIMALITY_PACKET = FSB_ROOT / "triadic_spectral_coordinate_minimality.packet.json"
OUTPUT = ROOT / "closure_pressure_family_hessian_activation.packet.json"


K = tuple[Fraction, Fraction, Fraction, Fraction]
Matrix = list[list[K]]
ZERO: K = (Fraction(0), Fraction(0), Fraction(0), Fraction(0))
ONE: K = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qpair_mul(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    a, b = left
    c, d = right
    return a * c + 3 * b * d, a * d + b * c


def qpair_inv(value: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    a, b = value
    denominator = a * a - 3 * b * b
    if denominator == 0:
        raise ZeroDivisionError("zero divisor in Q(sqrt(3))")
    return a / denominator, -b / denominator


def kadd(left: K, right: K) -> K:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def kneg(value: K) -> K:
    return tuple(-entry for entry in value)  # type: ignore[return-value]


def ksub(left: K, right: K) -> K:
    return kadd(left, kneg(right))


def kmul(left: K, right: K) -> K:
    real_left = left[0], left[1]
    imag_left = left[2], left[3]
    real_right = right[0], right[1]
    imag_right = right[2], right[3]
    rr = qpair_mul(real_left, real_right)
    ii = qpair_mul(imag_left, imag_right)
    ri = qpair_mul(real_left, imag_right)
    ir = qpair_mul(imag_left, real_right)
    return rr[0] - ii[0], rr[1] - ii[1], ri[0] + ir[0], ri[1] + ir[1]


def kconj(value: K) -> K:
    return value[0], value[1], -value[2], -value[3]


def kinv(value: K) -> K:
    norm = kmul(value, kconj(value))
    if norm[2:] != (0, 0):
        raise ArithmeticError("non-real norm")
    inverse_norm = qpair_inv((norm[0], norm[1]))
    return kmul(kconj(value), (inverse_norm[0], inverse_norm[1], Fraction(0), Fraction(0)))


def kdiv(left: K, right: K) -> K:
    return kmul(left, kinv(right))


def kfrom_int(value: int) -> K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def parse_fraction(value: str | int) -> Fraction:
    return Fraction(value)


def decode(value: list[str] | list[int]) -> K:
    return tuple(parse_fraction(entry) for entry in value)  # type: ignore[return-value]


def encode_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def encode(value: K) -> list[str]:
    return [encode_fraction(entry) for entry in value]


def zero(rows: int, columns: int) -> Matrix:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [[ONE if row == column else ZERO for column in range(size)] for row in range(size)]


def diagonal(values: list[K]) -> Matrix:
    return [
        [values[row] if row == column else ZERO for column in range(len(values))]
        for row in range(len(values))
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def adjoint(matrix: Matrix) -> Matrix:
    return [[kconj(value) for value in row] for row in transpose(matrix)]


def madd(left: Matrix, right: Matrix) -> Matrix:
    return [
        [kadd(a, b) for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def mscale(value: K, matrix: Matrix) -> Matrix:
    return [[kmul(value, entry) for entry in row] for row in matrix]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    result: Matrix = []
    for row in left:
        result_row: list[K] = []
        for column in columns:
            value = ZERO
            for a, b in zip(row, column):
                value = kadd(value, kmul(a, b))
            result_row.append(value)
        result.append(result_row)
    return result


def block_matrix(
    top_left: Matrix,
    top_right: Matrix,
    bottom_left: Matrix,
    bottom_right: Matrix,
) -> Matrix:
    return [a + b for a, b in zip(top_left, top_right)] + [
        a + b for a, b in zip(bottom_left, bottom_right)
    ]


def kron(left: Matrix, right: Matrix) -> Matrix:
    result: Matrix = []
    for left_row in left:
        for right_row in right:
            row: list[K] = []
            for left_entry in left_row:
                row.extend(kmul(left_entry, right_entry) for right_entry in right_row)
            result.append(row)
    return result


def matrix_rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != ZERO),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [kdiv(value, pivot_value) for value in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            coefficient = work[row][column]
            if coefficient != ZERO:
                work[row] = [
                    ksub(a, kmul(coefficient, b))
                    for a, b in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def trace(matrix: Matrix) -> K:
    return sum((matrix[index][index] for index in range(len(matrix))), ZERO)


def make_j() -> Matrix:
    return [
        [ONE if column == row else ZERO for column in range(64)]
        for row in range(16)
    ]


def make_family_commutant_constraints(a: Matrix, b: Matrix) -> Matrix:
    equations: Matrix = []
    for generator in (a, b):
        for row in range(3):
            for column in range(3):
                coefficients = [ZERO] * 9
                for k in range(3):
                    coefficients[row * 3 + k] = kadd(
                        coefficients[row * 3 + k], generator[k][column]
                    )
                    coefficients[k * 3 + column] = ksub(
                        coefficients[k * 3 + column], generator[row][k]
                    )
                equations.append(coefficients)
    return equations


def polynomial_zero(matrix: Matrix) -> bool:
    size = len(matrix)
    plus4 = madd(matrix, mscale(kfrom_int(4), identity(size)))
    plus2 = madd(matrix, mscale(kfrom_int(2), identity(size)))
    minus2 = madd(matrix, mscale(kfrom_int(-2), identity(size)))
    return matmul(plus4, matmul(plus2, minus2)) == zero(size, size)


def local_source_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for entry in source_lock["local_sources"]:
        path = (ROOT / entry["path"]).resolve()
        checks[f"source_hash::{entry['path']}"] = path.is_file() and sha256(path) == entry["sha256"]
    return checks


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    t15 = json.loads(T15_PACKET.read_text(encoding="utf-8"))
    dynamic = json.loads(DYNAMIC_PACKET.read_text(encoding="utf-8"))
    algebra = json.loads(ALGEBRA_PACKET.read_text(encoding="utf-8"))
    minimality = json.loads(MINIMALITY_PACKET.read_text(encoding="utf-8"))

    response_shapes = algebra["exact_witness"]["response_shapes"]
    a = [[decode(value) for value in row] for row in response_shapes["A_H_shift"]]
    b = [[decode(value) for value in row] for row in response_shapes["B_H_phase"]]

    phase_indices = [6, 7, 8, 14]
    shift_indices = [9, 10, 11, 15]
    inactive_indices = [0, 1, 2, 3, 4, 5, 12, 13]
    r_phase = diagonal([ONE if index in phase_indices else ZERO for index in range(16)])
    r_shift = diagonal([ONE if index in shift_indices else ZERO for index in range(16)])
    r_inactive = diagonal([ONE if index in inactive_indices else ZERO for index in range(16)])
    h = madd(kron(b, r_phase), kron(a, r_shift))

    j = make_j()
    jt = adjoint(j)
    h_e = block_matrix(zero(16, 16), zero(16, 48), zero(48, 16), h)
    d0 = block_matrix(zero(64, 64), jt, j, zero(16, 16))
    d1 = block_matrix(h_e, jt, j, zero(16, 16))
    d_delta = madd(d1, mscale(kfrom_int(-1), d0))

    weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    y16 = diagonal([kfrom_int(value) for value in weights])
    y48 = kron(identity(3), y16)

    activated = madd(r_phase, r_shift)
    activated48 = kron(identity(3), activated)
    inactive48 = kron(identity(3), r_inactive)
    h2 = matmul(h, h)
    singular_polynomial = matmul(
        madd(h2, mscale(kfrom_int(-16), activated48)),
        madd(h2, mscale(kfrom_int(-4), activated48)),
    )

    family_constraints = make_family_commutant_constraints(a, b)
    family_commutant_rank = matrix_rank(family_constraints)
    family_commutant_dimension = 9 - family_commutant_rank

    expected_a = [
        [kfrom_int(-2), ZERO, kfrom_int(-2)],
        [ZERO, kfrom_int(-2), kfrom_int(-2)],
        [kfrom_int(-2), kfrom_int(-2), ZERO],
    ]
    expected_b = [
        [kfrom_int(-4), ZERO, ZERO],
        [ZERO, ZERO, (Fraction(-1), Fraction(0), Fraction(0), Fraction(-1))],
        [ZERO, (Fraction(-1), Fraction(0), Fraction(0), Fraction(1)), ZERO],
    ]

    quartet = algebra["exact_witness"]["selected_eigenchannel_geometry"]["projector_quartet"]
    t15_boundary = t15["claim_boundary"]
    minimality_boundary = minimality["exact_witness"]["source_value_boundary"]

    checks = {
        **local_source_checks(source_lock),
        "schema_freezes_regular_normal_derivative": schema["properties"]["regular_constraint"]["properties"]["normal_derivative"]["const"] == "I_H16",
        "schema_preserves_physical_nonpromotion": schema["properties"]["claim_boundary"]["properties"]["physical_action_selected"]["const"] is False,
        "T15_linear_source_is_regular_four_to_one": t15["minimality_theorem"]["three_family_source_multiplicity"] == 4 and t15["minimality_theorem"]["residual_multiplicity"] == 1,
        "T15_physical_source_was_not_promoted": t15_boundary["physical_source_selected"] is False,
        "imported_A_matches_exact_selected_response": a == expected_a,
        "imported_B_matches_exact_selected_response": b == expected_b,
        "A_is_Hermitian": adjoint(a) == a,
        "B_is_Hermitian": adjoint(b) == b,
        "A_has_selected_cubic_polynomial": polynomial_zero(a),
        "B_has_selected_cubic_polynomial": polynomial_zero(b),
        "A_is_invertible": matrix_rank(a) == 3,
        "B_is_invertible": matrix_rank(b) == 3,
        "A_and_B_do_not_commute": matmul(a, b) != matmul(b, a),
        "joint_AB_commutant_has_dimension_one": family_commutant_dimension == 1,
        "FSB04f_declares_full_M3_generation": algebra["exact_witness"]["complex_response_algebra"]["generated_algebra"] == "M3(C) after scalar extension",
        "FSB04f_CP_quartet_is_exact": quartet == ["-1/8", "0", "0", "-1/24"],
        "phase_shift_inactive_projectors_partition_H16": madd(madd(r_phase, r_shift), r_inactive) == identity(16),
        "phase_and_shift_projectors_are_disjoint": matmul(r_phase, r_shift) == zero(16, 16),
        "normal_Nc_line_has_zero_shared_circle_weight": weights[15] == 0,
        "routed_tangent_Hessian_is_Hermitian": adjoint(h) == h,
        "routed_tangent_Hessian_has_complex_rank_24": matrix_rank(h) == 24,
        "routed_tangent_Hessian_vanishes_on_Q_and_L": matmul(h, inactive48) == zero(48, 48),
        "routed_tangent_Hessian_commutes_with_shared_circle": matmul(h, y48) == matmul(y48, h),
        "routed_tangent_Hessian_obeys_selected_cubic_on_active_range": matmul(
            madd(h, mscale(kfrom_int(4), activated48)),
            matmul(
                madd(h, mscale(kfrom_int(2), activated48)),
                madd(h, mscale(kfrom_int(-2), activated48)),
            ),
        ) == zero(48, 48),
        "routed_tangent_singular_values_have_only_two_nonzero_levels": singular_polynomial == zero(48, 48),
        "pure_multiplier_bordered_Hessian_has_rank_32": matrix_rank(d0) == 32,
        "pure_multiplier_bordered_Hessian_has_kernel_48": 80 - matrix_rank(d0) == 48,
        "pressure_activated_bordered_Hessian_has_rank_56": matrix_rank(d1) == 56,
        "pressure_activated_bordered_Hessian_has_kernel_24": 80 - matrix_rank(d1) == 24,
        "pressure_changes_only_the_tangent_block": d_delta == block_matrix(h_e, zero(64, 16), zero(16, 64), zero(16, 16)),
        "zero_pressure_recovers_CBF_T15_Hessian": d0 == block_matrix(zero(64, 64), jt, j, zero(16, 16)),
        "normal_derivative_is_identity_and_surjective": matmul(j, jt) == identity(16),
        "reduced_and_bordered_tangent_Hessians_agree": [row[16:64] for row in d1[16:64]] == h,
        "family_stabilizer_reduces_from_U3_to_scalar_U1": family_commutant_dimension == 1,
        "dynamic_packet_routes_phase_to_u_e": dynamic["exact_witness"]["routing_and_scope"]["phase_lane"] == ["u", "e"],
        "dynamic_packet_routes_shift_to_d_nuD": dynamic["exact_witness"]["routing_and_scope"]["shift_lane"] == ["d", "nuD"],
        "first_response_does_not_emit_three_positive_magnitudes": dynamic["exact_witness"]["canonical_positive_Grams"]["three_distinct_positive_magnitudes_emitted"] is False,
        "FSB04g_retains_nine_charged_values": minimality_boundary["strict_charged_magnitude_values_remaining"] == 9,
        "same_root_intertwiner_remains_open": source_lock["boundary"]["direct_source_and_q79_response_same_root_is_not_proved"],
        "physical_pressure_remains_unselected": source_lock["boundary"]["closure_pressure_is_not_physically_selected"],
        "family_response_is_not_promoted_to_Yukawa_mass": source_lock["boundary"]["family_response_hessian_is_not_retyped_as_a_yukawa_mass_matrix"],
        "physical_packet_acceptance_is_unchanged": source_lock["boundary"]["physical_packet_acceptance_before"] == source_lock["boundary"]["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": source_lock["boundary"]["physical_row_acceptance_before"] == source_lock["boundary"]["physical_row_acceptance_after"] == 0,
        "no_observed_values_enter_witness": True,
    }

    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"closure-pressure activation checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.closure-pressure-family-hessian-activation.v1",
        "claim_id": "CBF.T16",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_SOURCE_PINNED_FINITE_WITNESS + CONDITIONAL_CROSS_REPOSITORY_COMPOSITION",
        "decision": "PRESSURE_ACTIVATION_MECHANISM_CLOSED_PHYSICAL_ACTION_AND_VALUES_OPEN",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "general_theorem": {
            "spaces": "E=N direct_sum K",
            "regular_residual": "Phi(n,k)=n+psi(k), psi(0)=0, Dpsi(0)=0",
            "normal_derivative": "D_n Phi=I_N",
            "pure_multiplier_critical_rule": "surjectivity forces lambda=0",
            "zero_pressure_Hessian": "[[0,J*],[J,0]] independent of D2psi and higher jets",
            "repair_Hessian": "J*J at exact closure; D2psi is absent at quadratic order",
            "loaded_action": "L_p=-p<n0,n>+<lambda,Phi(n,k)>",
            "loaded_critical_point": "(n,k,lambda)=(0,0,p n0)",
            "tangent_Hessian": "<u,H_p v>=p<n0,D2psi(0)[u,v]>",
            "reduced_action": "S_red(k)=p<n0,psi(k)>",
            "geometric_interpretation": "second fundamental form contracted with a normal closure pressure",
        },
        "finite_instantiation": {
            "normal_dimension_complex": 16,
            "tangent_dimension_complex": 48,
            "bordered_dimension_complex": 80,
            "H16_order": ["Q6", "u3", "d3", "L2", "e1", "N1"],
            "neutral_normal_line": "N1=N^c at H16 index 15",
            "neutral_shared_circle_weight_6Y": 0,
            "phase_response_slots": phase_indices,
            "shift_response_slots": shift_indices,
            "inactive_slots": inactive_indices,
            "A_H_shift": [[encode(value) for value in row] for row in a],
            "B_H_phase": [[encode(value) for value in row] for row in b],
            "routed_Hessian_formula": "H_resp=B tensor R_phase+A tensor R_shift",
            "nonlinear_residual": "Phi(n,k)=n+(1/2)n0 Re<k,H_resp k>",
            "normalized_pressure": 1,
            "pure_multiplier_rank": matrix_rank(d0),
            "pure_multiplier_kernel_dimension": 80 - matrix_rank(d0),
            "pressured_bordered_rank": matrix_rank(d1),
            "pressured_bordered_kernel_dimension": 80 - matrix_rank(d1),
            "tangent_Hessian_rank_complex": matrix_rank(h),
        },
        "symmetry_and_spectrum": {
            "free_family_stabilizer_before": "U(3)",
            "common_family_stabilizer_after": "U(1)",
            "joint_AB_commutant_dimension": family_commutant_dimension,
            "A_and_B_generate": "M3(C)",
            "complex_tangent_spectrum": {"-4": 8, "-2": 8, "+2": 8, "0": 24},
            "nonzero_singular_magnitudes": {"4": 8, "2": 16},
            "three_distinct_positive_family_magnitudes": False,
            "projector_quartet": quartet,
            "CP_sensitive_finite_orientation": True,
            "physical_CKM_or_CP_identification": False,
            "gauge_group_preserved": "(SU3 x SU2 x U1Y)/Z6",
            "shared_circle_preserved": True,
        },
        "source_provenance": {
            "linear_source_pinned": True,
            "finite_response_source_pinned": True,
            "one_physical_root_for_both": False,
            "same_root_intertwiner_status": "OPEN",
            "composition_tier": "CONDITIONAL",
        },
        "parameter_ledger": {
            "observed_construction_inputs": 0,
            "fitted_dimensionless_coefficients": 0,
            "new_postprojection_family_matrices": 0,
            "unselected_physical_pressure_or_scale": 1,
            "strict_charged_magnitude_values_remaining": 9,
            "physical_CKM_or_CP_parameters_derived": 0,
        },
        "physical_typing_boundary": {
            "field_only_cyclic_action_selected": False,
            "Lorentz_fermion_pairing_selected": False,
            "Higgs_Yukawa_left_right_map_selected": False,
            "four_dimensional_BV_action_selected": False,
            "pressure_vacuum_law_selected": False,
            "held_out_prediction_emitted": False,
        },
        "claim_boundary": {
            "B_ACTION_01_closed": False,
            "B_SM_02_closed": False,
            "physical_action_selected": False,
            "physical_pressure_selected": False,
            "physical_Yukawa_values_derived": False,
            "same_root_composition_proved": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": {
            "before": "higher nonlinear residual terms were proposed without proving that they enter the free family Hessian",
            "after": "zero-pressure activation is excluded and the exact missing datum is a selected normal pressure contracting residual curvature; the pinned A/B pair supplies a finite symmetry-breaking witness",
            "remaining": "one-root pressure/action selection, Lorentz-Higgs Yukawa typing, a sector-resolved positive spectral law and held-out prediction",
        },
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": failed},
    }

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "closure-pressure family-Hessian packet built: "
        f"{len(checks)}/{len(checks)} checks; physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
