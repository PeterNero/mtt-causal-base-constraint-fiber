#!/usr/bin/env python3
"""Independently verify the exact CBF.T55 packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "same_source_principal_symbol_metric_hodge_naturality.packet.json"
SOURCE_LOCK = ROOT / "same_source_principal_symbol_metric_hodge_naturality_source_lock.json"
SCHEMA = ROOT / "same_source_principal_symbol_metric_hodge_naturality_contract.schema.json"
N = 6

Matrix = list[list[Fraction]]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def fractions(matrix: list[list[str]]) -> Matrix:
    return [[Fraction(entry) for entry in row] for row in matrix]


def strings(matrix: Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    right_t = transpose(right)
    return [
        [
            sum((a * b for a, b in zip(left_row, right_column)), Fraction(0))
            for right_column in right_t
        ]
        for left_row in left
    ]


def scale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * entry for entry in row] for row in matrix]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def determinant(matrix: Matrix) -> Fraction:
    if not matrix:
        return Fraction(1)
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]), None
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, len(work)):
            factor = work[row][column] / pivot_value
            for inner in range(column + 1, len(work)):
                work[row][inner] -= factor * work[column][inner]
    return result


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + unit[:] for row, unit in zip(matrix, identity(size))]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def rank(matrix: Matrix) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [entry / pivot_value for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
    return pivot_row


def exterior_basis() -> list[tuple[int, ...]]:
    return [
        tuple(indices)
        for degree in range(N + 1)
        for indices in itertools.combinations(range(1, N + 1), degree)
    ]


def sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        int(sequence[left] > sequence[right])
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def complement(indices: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(index for index in range(1, N + 1) if index not in indices)


def minor(matrix: Matrix, rows: tuple[int, ...], columns: tuple[int, ...]) -> Matrix:
    return [[matrix[row - 1][column - 1] for column in columns] for row in rows]


def hodge(metric_inverse: Matrix, volume: Fraction) -> Matrix:
    basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(basis)}
    result = zeros(64, 64)
    for column, source in enumerate(basis):
        for test in (entry for entry in basis if len(entry) == len(source)):
            target = complement(test)
            result[lookup[target]][column] += (
                sign(test + target)
                * volume
                * determinant(minor(metric_inverse, test, source))
            )
    return result


def exterior_pullback(coframe_map: Matrix) -> Matrix:
    basis = exterior_basis()
    result = zeros(64, 64)
    for row, target in enumerate(basis):
        for column, source in enumerate(basis):
            if len(target) == len(source):
                result[row][column] = determinant(minor(coframe_map, target, source))
    return result


def reconstruct_A(samples: list[dict[str, Any]]) -> Matrix:
    diagonal: dict[int, Fraction] = {}
    pairs: dict[tuple[int, int], Fraction] = {}
    for sample in samples:
        row = int(sample["row"])
        column = sample["column"]
        value = Fraction(sample["normalized_trace"])
        if column is None:
            diagonal[row] = value
        else:
            pairs[(row, int(column))] = value
    result = zeros(N, N)
    for row in range(N):
        result[row][row] = diagonal[row]
    for (row, column), value in pairs.items():
        result[row][column] = result[column][row] = (
            value - diagonal[row] - diagonal[column]
        ) / 2
    return result


def direct_hodge_derivative(metric: Matrix, delta_metric: Matrix) -> Matrix:
    inverse_metric = inverse(metric)
    delta_inverse = scale(
        matmul(matmul(inverse_metric, delta_metric), inverse_metric), -1
    )
    delta_volume = trace(matmul(inverse_metric, delta_metric)) / 2
    basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(basis)}
    result = zeros(64, 64)
    epsilon = Fraction(1, 10**6)
    # Determinants are polynomial, so a symmetric formal-epsilon extraction is
    # exact here after coefficient interpolation at enough rational points.
    # For this verifier the supplied directions are diagonal/off-diagonal at I;
    # use determinant multilinearity directly by replacing one row at a time.
    del epsilon
    for column, source in enumerate(basis):
        for test in (entry for entry in basis if len(entry) == len(source)):
            target = complement(test)
            base = minor(inverse_metric, test, source)
            delta = minor(delta_inverse, test, source)
            derivative = Fraction(0)
            size = len(base)
            for replaced in range(size):
                changed = [row[:] for row in base]
                changed[replaced] = delta[replaced][:]
                derivative += determinant(changed)
            result[lookup[target]][column] += sign(test + target) * (
                delta_volume * determinant(base) + derivative
            )
    return result


def main() -> None:
    packet = load_json(PACKET)
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    benchmark = packet["exact_non_diagonal_benchmark"]
    samples = benchmark["symbol_samples"]
    A = fractions(benchmark["action_quadratic_A"])
    recovered_A = reconstruct_A(samples)
    c = Fraction(benchmark["recovered_action_scale"])
    v = Fraction(benchmark["density_fixture"])
    H = scale(recovered_A, 1 / c)
    G = scale(inverse(recovered_A), c)
    star = hodge(H, v)

    source_results = []
    for source in lock["sources"]:
        actual = sha256((ROOT / source["path"]).resolve())
        source_results.append(actual == source["sha256"])

    symbol_scalar_checks = []
    for sample in samples:
        symbol = fractions(sample["symbol_matrix"])
        normalized = trace(symbol) / len(symbol)
        symbol_scalar_checks.append(symbol == scale(identity(len(symbol)), normalized))

    naturality = packet["naturality_certificate"]
    coframe = fractions(naturality["coframe_change"])
    H_target = matmul(matmul(transpose(coframe), H), coframe)
    star_target = hodge(H_target, v)
    pullback = exterior_pullback(coframe)

    variation_matrices = []
    variation_checks = []
    for row in packet["first_variation_certificate"]["shape_rows"]:
        delta_A = fractions(row["delta_symbol_quadratic"])
        delta_c_over_c = Fraction(row["delta_action_scale_over_scale"])
        delta_G = subtract(scale(identity(N), delta_c_over_c), scale(delta_A, 1 / c))
        delta_star = direct_hodge_derivative(identity(N), delta_G)
        variation_matrices.append(delta_star)
        variation_checks.append(
            canonical_hash(strings(delta_star))
            == row["T52_Hodge_derivative_sha256"]
        )
    variation_flat = [
        [matrix[row][column] for matrix in variation_matrices]
        for row in range(64)
        for column in range(64)
    ]

    nonscalar = fractions(
        packet["necessity_cutsets"]["without_scalarity"]["nonscalar_symbol"]
    )
    nonscalar_average = trace(nonscalar) / len(nonscalar)
    nonscalar_residual = subtract(
        nonscalar, scale(identity(len(nonscalar)), nonscalar_average)
    )

    checks = {
        "packet_schema": packet["schema"]
        == "boe.mtt.same-source-principal-symbol-metric-hodge-naturality.v1",
        "claim_id": packet["claim_id"] == "CBF.T55",
        "all_source_hashes_match": all(source_results),
        "schema_required_fields": set(schema["required"]).issubset(packet),
        "builder_checks_pass": packet["check_summary"]["all_passed"],
        "builder_check_count": packet["check_summary"]["total"] == 35,
        "sample_count": len(samples) == 21,
        "all_samples_scalar": all(symbol_scalar_checks),
        "polarization_reconstructs_A": recovered_A == A,
        "A_is_symmetric": transpose(A) == A,
        "A_is_invertible": determinant(A) != 0,
        "scale_determinant_equation": c**N == v**2 * determinant(A),
        "scale_is_positive": c > 0,
        "H_reconstruction": strings(H)
        == benchmark["recovered_covector_metric_H"],
        "G_reconstruction": strings(G)
        == benchmark["recovered_covariant_metric_G"],
        "G_H_inverse_identity": matmul(G, H) == identity(N),
        "density_equation": determinant(G) == v**2,
        "Hodge_digest_matches": canonical_hash(strings(star))
        == benchmark["source_Hodge_sha256"],
        "Hodge_square_on_zero_form": matmul(star, star)[0][0] == 1,
        "coframe_orientation": determinant(coframe) == 1,
        "coframe_nonorthogonal": matmul(transpose(coframe), coframe) != identity(N),
        "transformed_A_formula": fractions(naturality["transformed_action_quadratic"])
        == scale(H_target, c),
        "full_Hodge_naturality": matmul(pullback, star_target)
        == matmul(star, pullback),
        "all_variation_digests_match": all(variation_checks),
        "variation_count": len(variation_checks) == 8,
        "variation_rank": rank(variation_flat) == 8,
        "density_free_A_invariance": packet["necessity_cutsets"][
            "without_density"
        ]["same_action_quadratic"],
        "density_free_values_differ": packet["necessity_cutsets"][
            "without_density"
        ]["first_candidate_density"]
        != packet["necessity_cutsets"]["without_density"][
            "second_candidate_density"
        ],
        "nonscalar_control_keeps_trace": nonscalar_average
        == Fraction(samples[0]["normalized_trace"]),
        "nonscalar_control_has_residual": rank(nonscalar_residual) > 0,
        "shape_dimension_preserved": packet["q79_source_contract_update"][
            "intrinsic_Hermitian_shape_dimension_after_T55"
        ]
        == 8,
        "duplicate_payload_conditionally_removed": packet[
            "q79_source_contract_update"
        ]["independent_metric_payload_after_accepted_same_source_symbol_and_density"]
        == 0,
        "physical_GAS_still_open": packet["q79_source_contract_update"][
            "selected_physical_GAS_instance"
        ]
        == "OPEN",
        "no_parameters_added": packet["parameter_ledger"][
            "continuous_parameters_added"
        ]
        == 0,
        "benchmark_scale_not_physical": not packet["parameter_ledger"][
            "benchmark_action_scale_is_physical"
        ],
        "physical_gate_counter_unchanged": packet["physical_boundary"][
            "physical_gates"
        ]
        == {"accepted": 0, "total": 3},
        "physical_packet_counter_unchanged": packet["physical_boundary"][
            "physical_packets"
        ]
        == {"accepted": 0, "total": 3},
        "physical_row_counter_unchanged": packet["physical_boundary"][
            "physical_rows"
        ]
        == {"accepted": 0, "total": 7},
        "B_GEO_open": not packet["physical_boundary"]["B_GEO_01_closed"],
        "B_ACTION_open": not packet["physical_boundary"]["B_ACTION_01_closed"],
        "payload_hash_shape": len(packet["exact_payload_sha256"]) == 64,
    }
    summary = {
        "passed": sum(int(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
        "checks": checks,
    }
    print(json.dumps(summary, indent=2))
    if not summary["all_passed"]:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"failed checks: {failed}")


if __name__ == "__main__":
    main()

