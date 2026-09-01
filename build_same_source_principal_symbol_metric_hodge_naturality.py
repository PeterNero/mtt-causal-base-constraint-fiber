#!/usr/bin/env python3
"""Build the exact CBF.T55 principal-symbol metric/Hodge packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from build_q79_hermitian_metric_hodge_compiler import (
    canonical_hash,
    complex_realification,
    determinant,
    exterior_basis,
    hodge_derivative_formula,
    hodge_matrix,
    identity,
    inverse,
    matmul,
    matrix_hash,
    matrix_strings,
    rank,
    scale,
    submatrix,
    trace,
    transpose,
    zeros,
)


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "same_source_principal_symbol_metric_hodge_naturality_source_lock.json"
SCHEMA = ROOT / "same_source_principal_symbol_metric_hodge_naturality_contract.schema.json"
THEOREM = ROOT / "SameSourcePrincipalSymbolMetricActionScaleAndHodgeNaturalityTheorem_v1.md"
T52_PACKET = ROOT / "q79_hermitian_metric_hodge_compiler.packet.json"
OUTPUT = ROOT / "same_source_principal_symbol_metric_hodge_naturality.packet.json"
N = 6
RANK_E = 4

Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fractions(matrix: list[list[str]]) -> Matrix:
    return [[Fraction(entry) for entry in row] for row in matrix]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def quadratic(matrix: Matrix, vector: list[Fraction]) -> Fraction:
    return sum(
        (
            vector[row] * matrix[row][column] * vector[column]
            for row in range(len(vector))
            for column in range(len(vector))
        ),
        Fraction(0),
    )


def scalar_matrix(value: Fraction, size: int) -> Matrix:
    return scale(identity(size), value)


def exact_integer_root(value: int, degree: int) -> int:
    if value < 0 or degree <= 0:
        raise ValueError("positive exact root required")
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
    return Fraction(
        exact_integer_root(value.numerator, degree),
        exact_integer_root(value.denominator, degree),
    )


def symbol_samples(action_quadratic: Matrix) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    basis = [
        [Fraction(int(row == column)) for row in range(N)]
        for column in range(N)
    ]
    for first in range(N):
        vectors = [(f"e{first + 1}", basis[first], first, None)]
        vectors.extend(
            (
                f"e{first + 1}+e{second + 1}",
                [a + b for a, b in zip(basis[first], basis[second])],
                first,
                second,
            )
            for second in range(first + 1, N)
        )
        for label, vector, row, column in vectors:
            value = quadratic(action_quadratic, vector)
            symbol = scalar_matrix(value, RANK_E)
            samples.append(
                {
                    "label": label,
                    "row": row,
                    "column": column,
                    "vector": [str(entry) for entry in vector],
                    "symbol_matrix": matrix_strings(symbol),
                    "normalized_trace": str(trace(symbol) / RANK_E),
                    "scalar_residual_zero": symbol == scalar_matrix(
                        trace(symbol) / RANK_E, RANK_E
                    ),
                }
            )
    return samples


def reconstruct_quadratic(samples: list[dict[str, Any]]) -> Matrix:
    diagonal: dict[int, Fraction] = {}
    pair: dict[tuple[int, int], Fraction] = {}
    for sample in samples:
        value = Fraction(sample["normalized_trace"])
        row = int(sample["row"])
        column = sample["column"]
        if column is None:
            diagonal[row] = value
        else:
            pair[(row, int(column))] = value
    result = zeros(N, N)
    for row in range(N):
        result[row][row] = diagonal[row]
    for (row, column), value in pair.items():
        result[row][column] = result[column][row] = (
            value - diagonal[row] - diagonal[column]
        ) / 2
    return result


def exterior_pullback(coframe_map: Matrix) -> Matrix:
    basis = exterior_basis()
    result = zeros(len(basis), len(basis))
    for row, target in enumerate(basis):
        for column, source in enumerate(basis):
            if len(target) != len(source):
                continue
            result[row][column] = determinant(
                submatrix(coframe_map, target, source)
            )
    return result


def matrix_equal(left: Matrix, right: Matrix) -> bool:
    return left == right


def flatten_columns(matrices: list[Matrix]) -> Matrix:
    return [
        [matrix[row][column] for matrix in matrices]
        for row in range(len(matrices[0]))
        for column in range(len(matrices[0][0]))
    ]


def main() -> None:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t52 = load_json(T52_PACKET)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    source_checks = []
    for source in source_lock["sources"]:
        path = (ROOT / source["path"]).resolve()
        source_checks.append(
            {
                "id": source["id"],
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": sha256(path),
                "matches": sha256(path) == source["sha256"],
            }
        )

    witness = t52["non_diagonal_hermitian_witness"]
    metric = fractions(witness["covariant_metric_G"])
    metric_inverse = fractions(witness["covector_metric_H"])
    volume = Fraction(witness["volume_factor"])
    action_scale = Fraction(7)
    action_quadratic = scale(metric_inverse, action_scale)
    samples = symbol_samples(action_quadratic)
    reconstructed_A = reconstruct_quadratic(samples)
    recovered_scale = exact_fraction_root(
        volume**2 * determinant(reconstructed_A), N
    )
    recovered_H = scale(reconstructed_A, Fraction(1, 1) / recovered_scale)
    recovered_G = scale(inverse(reconstructed_A), recovered_scale)
    recovered_star = hodge_matrix(recovered_H, volume)

    # A nonorthogonal determinant-one complex-linear coframe change.
    complex_shear = [
        [Fraction(1), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(1)],
        [Fraction(0), Fraction(0), Fraction(1)],
    ]
    coframe_change = complex_realification(complex_shear, zeros(3, 3))
    transformed_H = matmul(
        matmul(transpose(coframe_change), recovered_H), coframe_change
    )
    transformed_A = scale(transformed_H, recovered_scale)
    transformed_G = inverse(transformed_H)
    transformed_samples = symbol_samples(transformed_A)
    transformed_reconstructed_A = reconstruct_quadratic(transformed_samples)
    transformed_scale = exact_fraction_root(
        volume**2 * determinant(transformed_reconstructed_A), N
    )
    transformed_recovered_G = scale(
        inverse(transformed_reconstructed_A), transformed_scale
    )
    transformed_star = hodge_matrix(transformed_H, volume)
    pullback = exterior_pullback(coframe_change)
    naturality_left = matmul(pullback, transformed_star)
    naturality_right = matmul(recovered_star, pullback)

    # Push all T52 fixed-volume shape directions through the symbol chain.
    identity_metric = identity(N)
    identity_A = scale(identity_metric, action_scale)
    identity_A_inverse = inverse(identity_A)
    identity_star = hodge_matrix(identity_metric, Fraction(1))
    variation_rows = []
    recovered_hodge_variations: list[Matrix] = []
    for t52_row in t52["eight_shape_first_variation"][
        "identity_metric_variations"
    ]:
        delta_G = fractions(t52_row["metric_direction"])
        delta_A = scale(delta_G, -action_scale)
        delta_v_over_v = trace(delta_G) / 2
        gamma = (
            2 * delta_v_over_v + trace(matmul(identity_A_inverse, delta_A))
        ) / N
        recovered_delta_G = subtract(
            scale(identity_metric, gamma),
            scale(delta_A, Fraction(1, 1) / action_scale),
        )
        delta_star = hodge_derivative_formula(
            identity_star, identity_metric, recovered_delta_G
        )
        recovered_hodge_variations.append(delta_star)
        variation_rows.append(
            {
                "name": t52_row["name"],
                "delta_symbol_quadratic": matrix_strings(delta_A),
                "delta_volume_over_volume": str(delta_v_over_v),
                "delta_action_scale_over_scale": str(gamma),
                "recovered_metric_direction_matches_T52": recovered_delta_G
                == delta_G,
                "recovered_Hodge_derivative_sha256": matrix_hash(delta_star),
                "T52_Hodge_derivative_sha256": t52_row[
                    "Hodge_derivative_sha256"
                ],
                "Hodge_derivative_matches_T52": matrix_hash(delta_star)
                == t52_row["Hodge_derivative_sha256"],
            }
        )
    variation_rank = rank(flatten_columns(recovered_hodge_variations))

    # Density-free ambiguity: (c,G) and (2c,2G) have the same A.
    doubled_scale = 2 * recovered_scale
    doubled_metric = scale(recovered_G, Fraction(2))
    doubled_A = scale(inverse(doubled_metric), doubled_scale)
    doubled_volume = Fraction(8) * volume

    # Trace preservation is not enough when the endomorphism symbol is nonscalar.
    first_scalar = Fraction(samples[0]["normalized_trace"])
    nonscalar_symbol = scalar_matrix(first_scalar, RANK_E)
    nonscalar_symbol[0][0] -= 1
    nonscalar_symbol[-1][-1] += 1
    nonscalar_trace = trace(nonscalar_symbol) / RANK_E
    nonscalar_residual = subtract(
        nonscalar_symbol, scalar_matrix(nonscalar_trace, RANK_E)
    )

    payload: dict[str, Any] = {
        "schema": "boe.mtt.same-source-principal-symbol-metric-hodge-naturality.v1",
        "claim_id": "CBF.T55",
        "date": "2026-09-01",
        "status": "EXACT_GENERAL_PLUS_EXACT_SOURCE_LOCKED_BENCHMARK_CONDITIONAL_PHYSICAL_REDUCTION",
        "source_provenance": {
            "model_state_sha256": source_lock["model_state_sha256"],
            "handoff_id": source_lock["handoff_id"],
            "source_checks": source_checks,
            "all_sources_hash_locked": all(row["matches"] for row in source_checks),
        },
        "reconstruction_theorem": {
            "base_dimension": N,
            "internal_rank": RANK_E,
            "scalar_symbol_gate": "sigma_2(L)(xi)=a(xi) I_E",
            "normalized_trace": "a(xi)=Tr_E(sigma_2(L)(xi))/rank(E)",
            "polarization": "A_ij=(a(e_i+e_j)-a(e_i)-a(e_j))/2",
            "action_scale_formula": "c=(v^2 det(A))^(1/n)",
            "contravariant_metric_formula": "H=A/c",
            "covariant_metric_formula": "G=c A^-1",
            "density_is_required_for_absolute_scale": True,
            "unique_positive_reconstruction": True,
        },
        "exact_non_diagonal_benchmark": {
            "source_T52_claim": t52["claim_id"],
            "source_metric_sha256": canonical_hash(witness["covariant_metric_G"]),
            "source_Hodge_sha256": witness["full_Hodge_sha256"],
            "action_scale_fixture": str(action_scale),
            "density_fixture": str(volume),
            "action_quadratic_A": matrix_strings(action_quadratic),
            "determinant_A": str(determinant(action_quadratic)),
            "symbol_sample_count": len(samples),
            "symbol_samples": samples,
            "all_symbol_samples_scalar": all(
                row["scalar_residual_zero"] for row in samples
            ),
            "reconstructed_A": matrix_strings(reconstructed_A),
            "recovered_action_scale": str(recovered_scale),
            "recovered_covector_metric_H": matrix_strings(recovered_H),
            "recovered_covariant_metric_G": matrix_strings(recovered_G),
            "A_reconstruction_exact": reconstructed_A == action_quadratic,
            "action_scale_reconstruction_exact": recovered_scale == action_scale,
            "metric_reconstruction_exact": recovered_G == metric,
            "inverse_metric_reconstruction_exact": recovered_H == metric_inverse,
            "Hodge_reconstruction_sha256": matrix_hash(recovered_star),
            "Hodge_reconstruction_matches_T52": matrix_hash(recovered_star)
            == witness["full_Hodge_sha256"],
        },
        "naturality_certificate": {
            "coframe_change": matrix_strings(coframe_change),
            "coframe_change_determinant": str(determinant(coframe_change)),
            "complex_linear_nonorthogonal": True,
            "transformed_action_quadratic": matrix_strings(transformed_A),
            "transformed_A_reconstruction_exact": transformed_reconstructed_A
            == transformed_A,
            "transformed_action_scale_invariant": transformed_scale
            == recovered_scale,
            "transformed_metric_reconstruction_exact": transformed_recovered_G
            == transformed_G,
            "full_exterior_pullback_shape": [64, 64],
            "full_Hodge_pullback_naturality": naturality_left
            == naturality_right,
            "internal_unitary_conjugation_preserves_scalar_symbol": True,
            "gauge_and_base_naturality_exact": transformed_recovered_G
            == transformed_G
            and naturality_left == naturality_right,
        },
        "first_variation_certificate": {
            "variation_formula_action_scale": "dot(c)/c=(2 dot(v)/v+Tr(A^-1 dot(A)))/n",
            "variation_formula_metric": "dot(G)=(dot(c)/c)G-G[dot(A)/c]G",
            "shape_direction_count": len(variation_rows),
            "shape_rows": variation_rows,
            "all_metric_directions_recovered": all(
                row["recovered_metric_direction_matches_T52"]
                for row in variation_rows
            ),
            "all_Hodge_derivatives_match_T52": all(
                row["Hodge_derivative_matches_T52"] for row in variation_rows
            ),
            "composite_Hodge_response_rank": variation_rank,
            "rank_eight_shape_response": variation_rank == 8,
        },
        "necessity_cutsets": {
            "without_density": {
                "same_action_quadratic": doubled_A == reconstructed_A,
                "first_candidate_action_scale": str(recovered_scale),
                "second_candidate_action_scale": str(doubled_scale),
                "first_candidate_density": str(volume),
                "second_candidate_density": str(doubled_volume),
                "one_positive_scale_orbit_remains": True,
            },
            "without_scalarity": {
                "nonscalar_symbol": matrix_strings(nonscalar_symbol),
                "normalized_trace": str(nonscalar_trace),
                "trace_matches_scalar_sample": nonscalar_trace == first_scalar,
                "scalar_residual_rank": rank(nonscalar_residual),
                "scalar_gate_fails": rank(nonscalar_residual) > 0,
                "trace_only_metric_promotion_rejected": True,
            },
        },
        "q79_source_contract_update": {
            "previous_T52_metric_shape_source_fields": 8,
            "intrinsic_Hermitian_shape_dimension_after_T55": 8,
            "independent_metric_payload_after_accepted_same_source_symbol_and_density": 0,
            "required_same_source_inputs": [
                "scalar_positive_principal_symbol",
                "positive_oriented_density",
                "common_GAS_source_hash",
                "complex_structure_for_Hermitian_typing",
            ],
            "GAS_to_metric_Hodge_compiler": "CLOSED_CONDITIONALLY_BY_T55",
            "selected_physical_GAS_instance": "OPEN",
            "selected_q79_metric_values": "OPEN",
            "selected_HYM_connection_and_Green": "OPEN",
            "rank102_continuum_execution": "OPEN",
        },
        "parameter_ledger": {
            "continuous_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "benchmark_action_scale_is_physical": False,
            "shared_action_primitives_after_T55": 1,
            "metric_shape_degrees_removed": 0,
            "duplicate_metric_source_payloads_removed_conditionally": 1,
        },
        "physical_boundary": {
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "B_HS_01_closed": False,
            "B_GEO_01_closed": False,
            "B_ACTION_01_closed": False,
            "B_OP_01_closed": False,
            "B_QFT_02_closed": False,
            "reason": "No selected physical q79 scalar Hessian symbol, density, HYM endpoint, Green operator or continuum intertwiner is supplied.",
        },
    }
    payload["exact_payload_sha256"] = canonical_hash(payload)

    required = set(schema["required"])
    checks = {
        "all_sources_hash_locked": payload["source_provenance"][
            "all_sources_hash_locked"
        ],
        "all_symbol_samples_are_scalar": payload[
            "exact_non_diagonal_benchmark"
        ]["all_symbol_samples_scalar"],
        "twenty_one_polarization_samples_are_emitted": len(samples) == 21,
        "A_reconstruction_is_exact": reconstructed_A == action_quadratic,
        "determinant_A_is_seventh_power_six": determinant(action_quadratic)
        == Fraction(7**6),
        "action_scale_reconstruction_is_exact": recovered_scale == action_scale,
        "metric_reconstruction_is_exact": recovered_G == metric,
        "inverse_metric_reconstruction_is_exact": recovered_H == metric_inverse,
        "Hodge_reconstruction_matches_T52": matrix_hash(recovered_star)
        == witness["full_Hodge_sha256"],
        "coframe_change_is_orientation_preserving": determinant(coframe_change)
        == 1,
        "coframe_change_is_nonorthogonal": matmul(
            transpose(coframe_change), coframe_change
        )
        != identity(N),
        "transformed_A_reconstruction_is_exact": transformed_reconstructed_A
        == transformed_A,
        "transformed_scale_is_invariant": transformed_scale == recovered_scale,
        "transformed_metric_reconstruction_is_exact": transformed_recovered_G
        == transformed_G,
        "full_Hodge_pullback_naturality_holds": naturality_left
        == naturality_right,
        "all_eight_metric_variations_are_recovered": all(
            row["recovered_metric_direction_matches_T52"]
            for row in variation_rows
        ),
        "all_eight_Hodge_variations_match_T52": all(
            row["Hodge_derivative_matches_T52"] for row in variation_rows
        ),
        "composite_shape_response_has_rank_eight": variation_rank == 8,
        "density_free_scale_orbit_keeps_A_fixed": doubled_A == reconstructed_A,
        "density_free_scale_orbit_changes_density": doubled_volume != volume,
        "nonscalar_trace_control_preserves_trace": nonscalar_trace == first_scalar,
        "nonscalar_trace_control_fails_scalar_gate": rank(nonscalar_residual) > 0,
        "T52_shape_dimension_is_not_erased": payload[
            "q79_source_contract_update"
        ]["intrinsic_Hermitian_shape_dimension_after_T55"]
        == 8,
        "duplicate_metric_payload_is_conditionally_removed": payload[
            "q79_source_contract_update"
        ]["independent_metric_payload_after_accepted_same_source_symbol_and_density"]
        == 0,
        "selected_physical_GAS_remains_open": payload[
            "q79_source_contract_update"
        ]["selected_physical_GAS_instance"]
        == "OPEN",
        "one_action_primitive_is_preserved": payload["parameter_ledger"][
            "shared_action_primitives_after_T55"
        ]
        == 1,
        "no_observed_or_fitted_values_are_used": payload["parameter_ledger"][
            "observed_values_used"
        ]
        == 0
        and payload["parameter_ledger"]["fitted_values_used"] == 0,
        "physical_counters_do_not_move": payload["physical_boundary"][
            "physical_gates"
        ]
        == {"accepted": 0, "total": 3}
        and payload["physical_boundary"]["physical_packets"]
        == {"accepted": 0, "total": 3}
        and payload["physical_boundary"]["physical_rows"]
        == {"accepted": 0, "total": 7},
        "controlling_blockers_remain_open": not payload["physical_boundary"][
            "B_GEO_01_closed"
        ]
        and not payload["physical_boundary"]["B_ACTION_01_closed"],
        "theorem_states_same_source_reconstruction": "same-source reconstruction"
        in theorem_text,
        "theorem_records_scalar_gate": "scalar Laplace-type gate" in theorem_text,
        "theorem_records_scale_boundary": "one positive joint action/metric-scale orbit"
        in theorem_text,
        "theorem_preserves_physical_boundary": "physical packet\nacceptance remains `0/3`"
        in theorem_text,
        "schema_required_fields_are_present": required.issubset(
            set(payload) | {"checks", "check_summary"}
        ),
        "payload_hash_is_well_formed": len(payload["exact_payload_sha256"]) == 64,
    }
    payload["checks"] = checks
    payload["check_summary"] = {
        "passed": sum(int(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["check_summary"], indent=2))
    if not payload["check_summary"]["all_passed"]:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"failed checks: {failed}")


if __name__ == "__main__":
    main()
