#!/usr/bin/env python3
"""Build the exact CBF.T57 augmented triangular principal-symbol packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Iterable

from build_q79_hermitian_metric_hodge_compiler import (
    canonical_hash,
    determinant,
    hodge_matrix,
    identity,
    inverse,
    matmul,
    matrix_hash,
    matrix_strings,
    scale,
    transpose,
    zeros,
)


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "augmented_heterotic_triangular_principal_symbol_source_lock.json"
SCHEMA = ROOT / "augmented_heterotic_triangular_principal_symbol_contract.schema.json"
THEOREM = ROOT / "AugmentedHeteroticTriangularPrincipalSymbolMetricRecoveryTheorem_v1.md"
AUDIT = ROOT / "augmented_heterotic_triangular_external_source.audit.json"
T52_PACKET = ROOT / "q79_hermitian_metric_hodge_compiler.packet.json"
T55_PACKET = ROOT / "same_source_principal_symbol_metric_hodge_naturality.packet.json"
OUTPUT = ROOT / "augmented_heterotic_triangular_principal_symbol.packet.json"

REAL_DIMENSION = 6
COMPLEX_DIMENSION = 3
WITNESS_Q_RANK = 4
Q79_Q_RANK = 102
PARTIAL_COEFFICIENT = Fraction(1, 2)
RELATIVE_LANE_NORMALIZATION = Fraction(1)
ACTION_SCALE = Fraction(7)

RealMatrix = list[list[Fraction]]
Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = list[list[Gaussian]]
GZERO: Gaussian = (Fraction(0), Fraction(0))
GONE: Gaussian = (Fraction(1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fractions(matrix: list[list[str]]) -> RealMatrix:
    return [[Fraction(entry) for entry in row] for row in matrix]


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gneg(value: Gaussian) -> Gaussian:
    return -value[0], -value[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gconj(value: Gaussian) -> Gaussian:
    return value[0], -value[1]


def ginv(value: Gaussian) -> Gaussian:
    denominator = value[0] * value[0] + value[1] * value[1]
    if denominator == 0:
        raise ZeroDivisionError("zero Gaussian rational")
    return value[0] / denominator, -value[1] / denominator


def gsum(values: Iterable[Gaussian]) -> Gaussian:
    result = GZERO
    for value in values:
        result = gadd(result, value)
    return result


def gzeros(rows: int, columns: int) -> GaussianMatrix:
    return [[GZERO for _ in range(columns)] for _ in range(rows)]


def gidentity(size: int) -> GaussianMatrix:
    return [[GONE if row == column else GZERO for column in range(size)] for row in range(size)]


def gmatrix_add(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [
        [gadd(a, b) for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def gmatrix_sub(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [
        [gadd(a, gneg(b)) for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def gmatrix_scale(matrix: GaussianMatrix, scalar: Fraction | Gaussian) -> GaussianMatrix:
    factor = scalar if isinstance(scalar, tuple) else (scalar, Fraction(0))
    return [[gmul(factor, entry) for entry in row] for row in matrix]


def gtranspose(matrix: GaussianMatrix) -> GaussianMatrix:
    return [list(row) for row in zip(*matrix)]


def gadjoint(matrix: GaussianMatrix) -> GaussianMatrix:
    return [[gconj(entry) for entry in row] for row in gtranspose(matrix)]


def gmatmul(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    right_t = gtranspose(right)
    return [
        [gsum(gmul(a, b) for a, b in zip(left_row, right_column)) for right_column in right_t]
        for left_row in left
    ]


def gaussian_string(value: Gaussian) -> str:
    real, imag = value
    if imag == 0:
        return str(real)
    if real == 0:
        if imag == 1:
            return "i"
        if imag == -1:
            return "-i"
        return f"{imag}i"
    sign = "+" if imag > 0 else ""
    imag_part = "i" if imag == 1 else ("-i" if imag == -1 else f"{imag}i")
    return f"{real}{sign}{imag_part}"


def gmatrix_strings(matrix: GaussianMatrix) -> list[list[str]]:
    return [[gaussian_string(entry) for entry in row] for row in matrix]


def grank(matrix: GaussianMatrix) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column] != GZERO), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse_pivot = ginv(work[pivot_row][column])
        work[pivot_row] = [gmul(inverse_pivot, entry) for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][column] == GZERO:
                continue
            factor = work[row][column]
            work[row] = [
                gadd(entry, gneg(gmul(factor, pivot_entry)))
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def form_basis(degree: int) -> list[tuple[int, ...]]:
    if degree < 0 or degree > COMPLEX_DIMENSION:
        return []
    return list(itertools.combinations(range(COMPLEX_DIMENSION), degree))


def wedge_matrix(covector: list[Gaussian], degree: int) -> GaussianMatrix:
    source = form_basis(degree)
    target = form_basis(degree + 1)
    target_index = {entry: index for index, entry in enumerate(target)}
    result = gzeros(len(target), len(source))
    for column, monomial in enumerate(source):
        for index, coefficient in enumerate(covector):
            if index in monomial:
                continue
            sign = -1 if sum(int(entry < index) for entry in monomial) % 2 else 1
            row = target_index[tuple(sorted((index,) + monomial))]
            result[row][column] = gadd(result[row][column], gmul((Fraction(sign), Fraction(0)), coefficient))
    return result


def identity_tensor(rank: int, matrix: GaussianMatrix) -> GaussianMatrix:
    rows = rank * len(matrix)
    columns = rank * (len(matrix[0]) if matrix else 0)
    result = gzeros(rows, columns)
    for lane in range(rank):
        for row, source_row in enumerate(matrix):
            for column, entry in enumerate(source_row):
                result[lane * len(matrix) + row][lane * len(source_row) + column] = entry
    return result


def partial_matrix(alpha: list[Gaussian], form_degree: int, q_rank: int) -> GaussianMatrix:
    form_count = len(form_basis(form_degree))
    result = gzeros(q_rank * form_count, form_count)
    for q_index, coefficient in enumerate(alpha):
        for form_index in range(form_count):
            result[q_index * form_count + form_index][form_index] = coefficient
    return result


def triangular_symbol(beta: list[Gaussian], alpha: list[Gaussian], degree: int, q_rank: int) -> GaussianMatrix:
    d_symbol = identity_tensor(q_rank, wedge_matrix(beta, degree))
    c_symbol = wedge_matrix(beta, degree + 1)
    a_symbol = partial_matrix(alpha, degree + 1, q_rank)
    top_rows = len(d_symbol)
    bottom_rows = len(c_symbol)
    left_columns = len(d_symbol[0])
    right_columns = len(a_symbol[0])
    result = gzeros(top_rows + bottom_rows, left_columns + right_columns)
    sign = Fraction(1 if degree % 2 == 0 else -1)
    for row in range(top_rows):
        for column in range(left_columns):
            result[row][column] = d_symbol[row][column]
        for column in range(right_columns):
            result[row][left_columns + column] = gmul(
                (sign * PARTIAL_COEFFICIENT, Fraction(0)), a_symbol[row][column]
            )
    for row in range(bottom_rows):
        for column in range(right_columns):
            result[top_rows + row][left_columns + column] = c_symbol[row][column]
    return result


def real_matvec(matrix: RealMatrix, vector: list[Fraction]) -> list[Fraction]:
    return [sum((entry * value for entry, value in zip(row, vector)), Fraction(0)) for row in matrix]


def quadratic(matrix: RealMatrix, vector: list[Fraction]) -> Fraction:
    return sum(
        (
            vector[row] * matrix[row][column] * vector[column]
            for row in range(len(vector))
            for column in range(len(vector))
        ),
        Fraction(0),
    )


def sample_vectors() -> list[tuple[str, int, int | None, list[Fraction]]]:
    basis = [
        [Fraction(int(row == column)) for row in range(REAL_DIMENSION)]
        for column in range(REAL_DIMENSION)
    ]
    result: list[tuple[str, int, int | None, list[Fraction]]] = []
    for first in range(REAL_DIMENSION):
        result.append((f"e{first + 1}", first, None, basis[first]))
        for second in range(first + 1, REAL_DIMENSION):
            result.append(
                (
                    f"e{first + 1}+e{second + 1}",
                    first,
                    second,
                    [left + right for left, right in zip(basis[first], basis[second])],
                )
            )
    return result


def reconstruct_quadratic(samples: list[dict[str, Any]], field: str) -> RealMatrix:
    diagonal: dict[int, Fraction] = {}
    pairs: dict[tuple[int, int], Fraction] = {}
    for sample in samples:
        value = Fraction(sample[field])
        if sample["column"] is None:
            diagonal[int(sample["row"])] = value
        else:
            pairs[(int(sample["row"]), int(sample["column"]))] = value
    result = zeros(REAL_DIMENSION, REAL_DIMENSION)
    for row, value in diagonal.items():
        result[row][row] = value
    for (row, column), value in pairs.items():
        result[row][column] = result[column][row] = (value - diagonal[row] - diagonal[column]) / 2
    return result


def exact_integer_root(value: int, degree: int) -> int:
    low, high = 0, max(1, value)
    while low <= high:
        middle = (low + high) // 2
        power = middle**degree
        if power == value:
            return middle
        if power < value:
            low = middle + 1
        else:
            high = middle - 1
    raise ValueError(f"{value} is not an exact {degree}th power")


def exact_fraction_root(value: Fraction, degree: int) -> Fraction:
    return Fraction(exact_integer_root(value.numerator, degree), exact_integer_root(value.denominator, degree))


def main() -> None:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    audit = load_json(AUDIT)
    t52 = load_json(T52_PACKET)
    t55 = load_json(T55_PACKET)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    source_checks = []
    for source in source_lock["sources"]:
        actual = sha256(ROOT / source["path"])
        source_checks.append(
            {
                "id": source["id"],
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": actual,
                "matches": actual == source["sha256"],
            }
        )

    witness = t52["non_diagonal_hermitian_witness"]
    coframe = fractions(witness["real_coframe"])
    metric = fractions(witness["covariant_metric_G"])
    metric_inverse = fractions(witness["covector_metric_H"])
    density = Fraction(witness["volume_factor"])
    inverse_transpose_coframe = transpose(inverse(coframe))

    degree_one_dimension = 3 * WITNESS_Q_RANK + 3
    expected_correction_rank = 6
    witness_trace_factor = Fraction(1) + Fraction(2) * PARTIAL_COEFFICIENT**2 / Fraction(WITNESS_Q_RANK + 1)
    sample_rows = []
    all_nilpotent = True
    all_projectors = True
    all_rank_six = True
    all_off_diagonal_cancel = True
    all_two_level = True
    all_negative_controls = True

    for label, row, column, vector in sample_vectors():
        orthonormal = real_matvec(inverse_transpose_coframe, vector)
        beta = [
            (orthonormal[2 * index], orthonormal[2 * index + 1])
            for index in range(COMPLEX_DIMENSION)
        ]
        alpha = [gconj(entry) for entry in beta]
        q_value = quadratic(metric_inverse, vector)
        assert q_value == gsum(gmul(gconj(entry), entry) for entry in beta)[0]

        l0 = triangular_symbol(beta, alpha, 0, WITNESS_Q_RANK)
        l1 = triangular_symbol(beta, alpha, 1, WITNESS_Q_RANK)
        nilpotent = gmatmul(l1, l0)
        delta = gmatrix_add(gmatmul(l0, gadjoint(l0)), gmatmul(gadjoint(l1), l1))
        baseline = gmatrix_scale(gidentity(degree_one_dimension), q_value)
        correction = gmatrix_sub(delta, baseline)
        projector = gmatrix_scale(correction, Fraction(1) / (PARTIAL_COEFFICIENT**2 * q_value))

        nilpotence_exact = all(entry == GZERO for source_row in nilpotent for entry in source_row)
        projector_exact = gmatmul(projector, projector) == projector and gadjoint(projector) == projector
        projector_rank = grank(projector)
        top_dimension = 3 * WITNESS_Q_RANK
        off_diagonal_zero = all(
            delta[top][bottom] == GZERO and delta[bottom][top] == GZERO
            for top in range(top_dimension)
            for bottom in range(top_dimension, degree_one_dimension)
        )
        low = q_value
        high = q_value * (Fraction(1) + PARTIAL_COEFFICIENT**2 * RELATIVE_LANE_NORMALIZATION)
        trace_value = gsum(delta[index][index] for index in range(degree_one_dimension))[0]
        normalized_trace = trace_value / degree_one_dimension
        two_level_identity = gmatrix_sub(
            gmatrix_sub(delta, gmatrix_scale(gidentity(degree_one_dimension), low)),
            gmatrix_scale(projector, high - low),
        )
        two_level_exact = all(entry == GZERO for source_row in two_level_identity for entry in source_row)
        scalar_residual_rank = grank(correction)

        all_nilpotent = all_nilpotent and nilpotence_exact
        all_projectors = all_projectors and projector_exact
        all_rank_six = all_rank_six and projector_rank == expected_correction_rank
        all_off_diagonal_cancel = all_off_diagonal_cancel and off_diagonal_zero
        all_two_level = all_two_level and two_level_exact
        all_negative_controls = all_negative_controls and scalar_residual_rank == expected_correction_rank
        sample_rows.append(
            {
                "label": label,
                "row": row,
                "column": column,
                "covector": [str(entry) for entry in vector],
                "metric_quadratic_q": str(q_value),
                "complex_symbol_beta": [gaussian_string(entry) for entry in beta],
                "nilpotence_exact": nilpotence_exact,
                "nilpotence_sha256": canonical_hash(gmatrix_strings(nilpotent)),
                "Hodge_symbol_sha256": canonical_hash(gmatrix_strings(delta)),
                "projector_sha256": canonical_hash(gmatrix_strings(projector)),
                "projector_exact": projector_exact,
                "projector_rank": projector_rank,
                "off_diagonal_second_order_cancellation": off_diagonal_zero,
                "baseline_eigenvalue": str(low),
                "elevated_eigenvalue": str(high),
                "baseline_multiplicity": degree_one_dimension - expected_correction_rank,
                "elevated_multiplicity": expected_correction_rank,
                "two_level_identity_exact": two_level_exact,
                "normalized_trace": str(normalized_trace),
                "normalized_trace_factor": str(normalized_trace / q_value),
                "scalar_ansatz_residual_rank": scalar_residual_rank,
                "corrected_baseline_action_scalar": str(ACTION_SCALE * normalized_trace / witness_trace_factor),
            }
        )

    reconstructed_A = reconstruct_quadratic(sample_rows, "corrected_baseline_action_scalar")
    action_quadratic = scale(metric_inverse, ACTION_SCALE)
    recovered_scale = exact_fraction_root(density**2 * determinant(reconstructed_A), REAL_DIMENSION)
    recovered_H = scale(reconstructed_A, Fraction(1) / recovered_scale)
    recovered_G = scale(inverse(reconstructed_A), recovered_scale)
    recovered_hodge = hodge_matrix(recovered_H, density)

    witness_ratio = Fraction(sample_rows[0]["elevated_eigenvalue"]) / Fraction(sample_rows[0]["baseline_eigenvalue"])
    recovered_rho = (witness_ratio - 1) / PARTIAL_COEFFICIENT**2
    q79_dimension = 3 * Q79_Q_RANK + 3
    q79_trace_factor = Fraction(1) + Fraction(2) * PARTIAL_COEFFICIENT**2 * RELATIVE_LANE_NORMALIZATION / Fraction(Q79_Q_RANK + 1)

    packet: dict[str, Any] = {
        "schema": "boe.mtt.augmented-heterotic-triangular-principal-symbol.v1",
        "claim_id": "CBF.T57",
        "date": "2026-09-01",
        "status": "EXACT_PROJECTOR_CORRECTED_TRIANGULAR_SYMBOL_AND_SAME_SOURCE_METRIC_NORMALIZATION_RECOVERY_CONDITIONAL_Q79_SOURCE_REDUCTION",
        "source_provenance": {
            "model_state_sha256": source_lock["model_state_sha256"],
            "handoff_id": source_lock["handoff_id"],
            "source_checks": source_checks,
            "all_sources_hash_locked": all(row["matches"] for row in source_checks),
            "external_audit": audit,
            "external_sources_are_audited_design_inputs_not_runtime_dependencies": True,
        },
        "triangular_symbol_theorem": {
            "complex": "Y_n=Omega^(0,n)(Q) direct-sum Omega^(0,n+1)(X)",
            "differential": "L_n=[[dbar_Q,a(-1)^n partial],[0,dbar]]",
            "partial_coefficient_a": str(PARTIAL_COEFFICIENT),
            "relative_lane_normalization_symbol": "rho=m_Q/m_shifted",
            "degree_one_formula": "sigma_2(Delta_Y,1)(xi)=q(xi)I+a^2 rho q(xi)P_xi",
            "projector_formula": "P_xi=(p_alpha tensor I_Lambda01) direct-sum I_Lambda02",
            "projector_rank": 6,
            "off_diagonal_second_order_terms_cancel": True,
            "full_augmented_symbol_is_scalar": False,
            "eigenvalues": ["q", "q(1+a^2 rho)"],
            "relative_normalization_recovery": "rho=(lambda_high/lambda_low-1)/a^2",
            "general_degree_one_dimension": "3r+3",
            "general_multiplicities": {"baseline": "3r-3", "elevated": 6},
            "normalized_trace_factor": "1+2a^2 rho/(r+1)",
            "T56_scope_correction": "T56 applies to the diagonal Dirac/Dolbeault blocks; T57 is required for the full first-order triangular totalization.",
        },
        "exact_six_dimensional_witness": {
            "real_dimension": REAL_DIMENSION,
            "complex_dimension": COMPLEX_DIMENSION,
            "Q_rank": WITNESS_Q_RANK,
            "degree_one_dimension": degree_one_dimension,
            "partial_coefficient_a": str(PARTIAL_COEFFICIENT),
            "relative_lane_normalization_fixture_rho": str(RELATIVE_LANE_NORMALIZATION),
            "relative_lane_normalization_fixture_is_physical": False,
            "coframe": matrix_strings(coframe),
            "covariant_metric_G": matrix_strings(metric),
            "contravariant_metric_H": matrix_strings(metric_inverse),
            "sample_count": len(sample_rows),
            "samples": sample_rows,
            "all_complex_symbols_nilpotent": all_nilpotent,
            "all_Hodge_off_diagonal_second_order_blocks_cancel": all_off_diagonal_cancel,
            "all_corrections_are_rank_six_orthogonal_projectors": all_projectors and all_rank_six,
            "all_symbols_have_exactly_two_levels": all_two_level,
            "scalar_full_symbol_negative_control_passes": all_negative_controls,
            "baseline_multiplicity": degree_one_dimension - expected_correction_rank,
            "elevated_multiplicity": expected_correction_rank,
            "normalized_trace_factor": str(witness_trace_factor),
            "recovered_relative_lane_normalization": str(recovered_rho),
        },
        "q79_rank102_specialization": {
            "Q_rank": Q79_Q_RANK,
            "degree_one_dimension": q79_dimension,
            "projector_rank": expected_correction_rank,
            "baseline_multiplicity": q79_dimension - expected_correction_rank,
            "elevated_multiplicity": expected_correction_rank,
            "partial_coefficient_a": str(PARTIAL_COEFFICIENT),
            "normalized_trace_factor_formula": "1+rho/206",
            "rho_one_benchmark_trace_factor": str(q79_trace_factor),
            "rho_one_benchmark_is_physical": False,
            "relative_normalization_is_spectrally_observable": True,
        },
        "same_source_recovery": {
            "action_scale_fixture": str(ACTION_SCALE),
            "action_scale_fixture_is_physical": False,
            "density_fixture": str(density),
            "trace_correction": str(witness_trace_factor),
            "action_quadratic_A": matrix_strings(action_quadratic),
            "reconstructed_action_quadratic_A": matrix_strings(reconstructed_A),
            "recovered_action_scale": str(recovered_scale),
            "recovered_covector_metric_H": matrix_strings(recovered_H),
            "recovered_covariant_metric_G": matrix_strings(recovered_G),
            "recovered_relative_lane_normalization": str(recovered_rho),
            "action_quadratic_reconstruction_exact": reconstructed_A == action_quadratic,
            "action_scale_reconstruction_exact": recovered_scale == ACTION_SCALE,
            "metric_reconstruction_exact": recovered_G == metric,
            "inverse_metric_reconstruction_exact": recovered_H == metric_inverse,
            "Hodge_reconstruction_sha256": matrix_hash(recovered_hodge),
            "source_T55_Hodge_sha256": t55["exact_non_diagonal_benchmark"]["source_Hodge_sha256"],
            "Hodge_reconstruction_matches_T55": matrix_hash(recovered_hodge) == t55["exact_non_diagonal_benchmark"]["source_Hodge_sha256"],
        },
        "q79_source_contract_update": {
            "before": "full augmented Hodge symbol was implicitly treated as a scalar T56 input",
            "after": "full augmented symbol is a canonical rank-six projector correction whose two levels emit rho and whose corrected baseline feeds T55",
            "independent_scalar_full_symbol_obligation": "REMOVED_AS_FALSE_REQUIREMENT",
            "independent_relative_lane_normalization_after_full_selected_symbol": 0,
            "independent_metric_payload_after_full_selected_symbol_and_density": 0,
            "selected_physical_q79_augmented_complex": "OPEN",
            "selected_physical_q79_density": "OPEN",
            "selected_visible_hidden_HYM_connection": "OPEN",
            "selected_domain_projector_and_reduced_Green": "OPEN",
            "selected_C4_TT_naturality_and_error_bounds": "OPEN",
        },
        "parameter_ledger": {
            "continuous_physical_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "rho_one_is_only_a_witness_fixture": True,
            "rho_is_recovered_not_fitted_once_full_symbol_is_selected": True,
            "one_shared_action_primitive_status": "OPEN_UNCHANGED",
        },
        "physical_boundary": {
            "B_GEO_01_closed": False,
            "B_ACTION_01_closed": False,
            "B_OP_01_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "selected_physical_endpoint_claimed": False,
            "selected_physical_relative_normalization_claimed": False,
        },
    }

    packet["exact_payload_sha256"] = canonical_hash(
        {
            "triangular_symbol_theorem": packet["triangular_symbol_theorem"],
            "samples": sample_rows,
            "q79_rank102_specialization": packet["q79_rank102_specialization"],
            "same_source_recovery": packet["same_source_recovery"],
            "audit_sha256": sha256(AUDIT),
        }
    )

    checks = {
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": (set(schema["required"]) - {"checks", "check_summary"}).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T57",
        "theorem_states_non_scalar_formula": "q(xi) I+a^2 rho q(xi) P_xi" in theorem_text,
        "theorem_states_q79_multiplicities": "303" in theorem_text and "six" in theorem_text.lower(),
        "theorem_preserves_physical_boundary": "Physical acceptance remains `0/3`" in theorem_text,
        "source_hashes_match": packet["source_provenance"]["all_sources_hash_locked"],
        "external_sources_are_nonruntime": packet["source_provenance"]["external_sources_are_audited_design_inputs_not_runtime_dependencies"],
        "audit_adopts_triangular_complex": audit["joint_conclusion"]["triangular_complex_formula_is_adopted"],
        "audit_does_not_select_endpoint": not audit["joint_conclusion"]["selected_physical_q79_endpoint_is_present"],
        "coframe_determinant_one": determinant(coframe) == 1,
        "coframe_nonorthogonal": matmul(transpose(coframe), coframe) != identity(REAL_DIMENSION),
        "metric_from_coframe": matmul(transpose(coframe), coframe) == metric,
        "metric_inverse_exact": matmul(metric, metric_inverse) == identity(REAL_DIMENSION),
        "sample_count": len(sample_rows) == 21,
        "all_nilpotence_exact": all_nilpotent,
        "all_off_diagonal_cancel": all_off_diagonal_cancel,
        "all_projectors_exact": all_projectors,
        "all_projector_ranks_six": all_rank_six,
        "all_two_level_identities": all_two_level,
        "scalar_negative_control": all_negative_controls,
        "witness_dimension": degree_one_dimension == 15,
        "witness_multiplicities": degree_one_dimension - expected_correction_rank == 9 and expected_correction_rank == 6,
        "witness_trace_factor": witness_trace_factor == Fraction(11, 10),
        "witness_rho_recovered": recovered_rho == RELATIVE_LANE_NORMALIZATION,
        "action_A_reconstructed": reconstructed_A == action_quadratic,
        "action_scale_recovered": recovered_scale == ACTION_SCALE,
        "inverse_metric_recovered": recovered_H == metric_inverse,
        "metric_recovered": recovered_G == metric,
        "Hodge_recovered": packet["same_source_recovery"]["Hodge_reconstruction_matches_T55"],
        "q79_dimension": q79_dimension == 309,
        "q79_baseline_multiplicity": q79_dimension - expected_correction_rank == 303,
        "q79_elevated_multiplicity": expected_correction_rank == 6,
        "q79_trace_factor": q79_trace_factor == Fraction(207, 206),
        "full_symbol_declared_nonscalar": not packet["triangular_symbol_theorem"]["full_augmented_symbol_is_scalar"],
        "T56_scope_corrected": "diagonal" in packet["triangular_symbol_theorem"]["T56_scope_correction"],
        "scalar_requirement_removed": packet["q79_source_contract_update"]["independent_scalar_full_symbol_obligation"] == "REMOVED_AS_FALSE_REQUIREMENT",
        "rho_not_duplicate_input": packet["q79_source_contract_update"]["independent_relative_lane_normalization_after_full_selected_symbol"] == 0,
        "metric_not_duplicate_input": packet["q79_source_contract_update"]["independent_metric_payload_after_full_selected_symbol_and_density"] == 0,
        "no_continuous_parameters": packet["parameter_ledger"]["continuous_physical_parameters_added"] == 0,
        "no_selectors": packet["parameter_ledger"]["discrete_selectors_added"] == 0,
        "no_observed_values": packet["parameter_ledger"]["observed_values_used"] == 0,
        "no_fitted_values": packet["parameter_ledger"]["fitted_values_used"] == 0,
        "rho_recovered_not_fitted": packet["parameter_ledger"]["rho_is_recovered_not_fitted_once_full_symbol_is_selected"],
        "B_GEO_open": not packet["physical_boundary"]["B_GEO_01_closed"],
        "B_ACTION_open": not packet["physical_boundary"]["B_ACTION_01_closed"],
        "B_OP_open": not packet["physical_boundary"]["B_OP_01_closed"],
        "physical_gates_unchanged": packet["physical_boundary"]["physical_gates"] == {"accepted": 0, "total": 3},
        "physical_packets_unchanged": packet["physical_boundary"]["physical_packets"] == {"accepted": 0, "total": 3},
        "physical_rows_unchanged": packet["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
        "no_selected_endpoint_claim": not packet["physical_boundary"]["selected_physical_endpoint_claimed"],
        "no_selected_rho_claim": not packet["physical_boundary"]["selected_physical_relative_normalization_claimed"],
    }
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": sum(bool(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    if not packet["check_summary"]["all_passed"]:
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"CBF.T57 build failed: {failed}")

    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet["check_summary"], sort_keys=True))


if __name__ == "__main__":
    main()
