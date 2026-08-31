#!/usr/bin/env python3
"""Independently recompute the exact CBF.T52 metric/Hodge compiler packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_hermitian_metric_hodge_compiler_source_lock.json"
SCHEMA_PATH = ROOT / "q79_hermitian_metric_hodge_compiler_contract.schema.json"
THEOREM_PATH = ROOT / "Q79HermitianMetricHodgeCoefficientAndFirstVariationCompilerTheorem_v1.md"
PACKET_PATH = ROOT / "q79_hermitian_metric_hodge_compiler.packet.json"
N = 6
Matrix = list[list[Fraction]]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def as_matrix(raw: list[list[Any]]) -> Matrix:
    return [[Fraction(str(value)) for value in row] for row in raw]


def matrix_strings(matrix: Matrix) -> list[list[str]]:
    return [[str(value) for value in row] for row in matrix]


def matrix_hash(matrix: Matrix) -> str:
    return canonical_hash(matrix_strings(matrix))


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def eye(size: int) -> Matrix:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in columns]
        for row in left
    ]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


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
            for index in range(column, len(work)):
                work[row][index] -= factor * work[column][index]
    return result


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + unit[:] for row, unit in zip(matrix, eye(size))]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(work[row], work[column])
                ]
    return [row[size:] for row in work]


def matrix_rank(matrix: Matrix) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
    return pivot_row


def exterior_basis() -> list[tuple[int, ...]]:
    return [
        tuple(indices)
        for degree in range(N + 1)
        for indices in itertools.combinations(range(1, N + 1), degree)
    ]


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        int(sequence[left] > sequence[right])
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def complement(indices: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(index for index in range(1, N + 1) if index not in indices)


def wedge_sign(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    if set(left).intersection(right):
        return 0
    return permutation_sign(left + right)


def submatrix(matrix: Matrix, rows: tuple[int, ...], columns: tuple[int, ...]) -> Matrix:
    return [[matrix[row - 1][column - 1] for column in columns] for row in rows]


def hodge(metric_inverse: Matrix, volume: Fraction) -> Matrix:
    basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(basis)}
    result = zeros(64, 64)
    for column, source in enumerate(basis):
        for test in (entry for entry in basis if len(entry) == len(source)):
            target = complement(test)
            result[lookup[target]][column] += (
                Fraction(wedge_sign(test, target))
                * volume
                * determinant(submatrix(metric_inverse, test, source))
            )
    return result


def exterior_gram(metric_inverse: Matrix) -> Matrix:
    basis = exterior_basis()
    result = zeros(64, 64)
    for row, left in enumerate(basis):
        for column, right in enumerate(basis):
            if len(left) == len(right):
                result[row][column] = determinant(
                    submatrix(metric_inverse, left, right)
                )
    return result


def determinant_derivative(base: Matrix, variation: Matrix) -> Fraction:
    size = len(base)
    total = Fraction(0)
    for permutation in itertools.permutations(range(size)):
        sign = Fraction(permutation_sign(tuple(index + 1 for index in permutation)))
        for varied_row in range(size):
            term = sign * variation[varied_row][permutation[varied_row]]
            for row in range(size):
                if row != varied_row:
                    term *= base[row][permutation[row]]
            total += term
    return total


def hodge_derivative_by_minors(
    metric_inverse: Matrix, volume: Fraction, metric_variation: Matrix
) -> Matrix:
    inverse_variation = scale(
        multiply(multiply(metric_inverse, metric_variation), metric_inverse),
        Fraction(-1),
    )
    volume_variation = volume * trace(multiply(metric_inverse, metric_variation)) / 2
    basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(basis)}
    result = zeros(64, 64)
    for column, source in enumerate(basis):
        for test in (entry for entry in basis if len(entry) == len(source)):
            target = complement(test)
            base_minor = submatrix(metric_inverse, test, source)
            varied_minor = submatrix(inverse_variation, test, source)
            result[lookup[target]][column] += Fraction(wedge_sign(test, target)) * (
                volume_variation * determinant(base_minor)
                + volume * determinant_derivative(base_minor, varied_minor)
            )
    return result


def exterior_derivation(generator: Matrix) -> Matrix:
    basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(basis)}
    result = zeros(64, 64)
    for column, source in enumerate(basis):
        for slot, original in enumerate(source):
            for replacement in range(1, N + 1):
                coefficient = generator[replacement - 1][original - 1]
                raw = source[:slot] + (replacement,) + source[slot + 1 :]
                if not coefficient or len(set(raw)) != len(raw):
                    continue
                result[lookup[tuple(sorted(raw))]][column] += (
                    Fraction(permutation_sign(raw)) * coefficient
                )
    return result


def hodge_derivative_formula(
    star: Matrix, metric_inverse: Matrix, metric_variation: Matrix
) -> Matrix:
    relative = multiply(metric_inverse, metric_variation)
    scalar = scale(eye(64), trace(relative) / 2)
    return multiply(
        star,
        subtract(scalar, exterior_derivation(transpose(relative))),
    )


def sparse_to_matrix(entries: list[dict[str, Any]]) -> Matrix:
    result = zeros(64, 64)
    for entry in entries:
        result[entry["row"]][entry["column"]] = Fraction(entry["value"])
    return result


def wedge_identities_hold(star: Matrix, metric_inverse: Matrix, volume: Fraction) -> bool:
    basis = exterior_basis()
    for left in basis:
        for right in basis:
            if len(left) != len(right):
                continue
            actual = sum(
                (
                    Fraction(wedge_sign(left, target)) * star[row][basis.index(right)]
                    for row, target in enumerate(basis)
                    if len(target) == N - len(left)
                ),
                Fraction(0),
            )
            expected = determinant(submatrix(metric_inverse, left, right)) * volume
            if actual != expected:
                return False
    return True


def expected_star_square() -> Matrix:
    result = zeros(64, 64)
    for index, entry in enumerate(exterior_basis()):
        result[index][index] = Fraction((-1) ** (len(entry) * (N - len(entry))))
    return result


def main() -> None:
    lock = load_json(LOCK_PATH)
    schema = load_json(SCHEMA_PATH)
    packet = load_json(PACKET_PATH)
    theorem = THEOREM_PATH.read_text(encoding="utf-8")

    source_paths = {
        source["id"]: (ROOT / source["path"]).resolve() for source in lock["sources"]
    }
    source_checks = {
        source["id"]: source_paths[source["id"]].is_file()
        and sha256(source_paths[source["id"]]) == source["sha256"]
        for source in lock["sources"]
    }

    core = deepcopy(packet)
    core.pop("checks")
    core.pop("check_summary")
    stored_hash = core.pop("exact_payload_sha256")

    witness = packet["non_diagonal_hermitian_witness"]
    response = packet["eight_shape_first_variation"]
    q79 = packet["q79_instantiation_boundary"]
    ledger = packet["parameter_ledger"]
    boundary = packet["physical_boundary"]

    real_coframe = as_matrix(witness["real_coframe"])
    complex_structure = as_matrix(witness["standard_complex_structure"])
    metric = as_matrix(witness["covariant_metric_G"])
    metric_inverse = inverse(metric)
    volume = Fraction(witness["volume_factor"])
    recomputed_metric = multiply(transpose(real_coframe), real_coframe)
    recomputed_star = hodge(metric_inverse, volume)
    packet_star = sparse_to_matrix(witness["full_Hodge_sparse_entries"])
    gram = exterior_gram(metric_inverse)

    identity_star = hodge(eye(N), Fraction(1))
    t51_packet = load_json(source_paths["T51_PACKET"])
    t51_star = sparse_to_matrix(
        t51_packet["oriented_exterior_hodge"]["sparse_matrix_entries"]
    )

    direction_rows = response["identity_metric_variations"]
    directions = [as_matrix(row["metric_direction"]) for row in direction_rows]
    identity_derivatives = [
        hodge_derivative_by_minors(eye(N), Fraction(1), direction)
        for direction in directions
    ]
    identity_formula_derivatives = [
        hodge_derivative_formula(identity_star, eye(N), direction)
        for direction in directions
    ]
    packet_identity_derivatives = [
        sparse_to_matrix(row["Hodge_derivative_sparse_entries"])
        for row in direction_rows
    ]

    witness_directions = [
        multiply(multiply(transpose(real_coframe), direction), real_coframe)
        for direction in directions
    ]
    witness_derivatives = [
        hodge_derivative_by_minors(metric_inverse, volume, direction)
        for direction in witness_directions
    ]
    witness_formula_derivatives = [
        hodge_derivative_formula(recomputed_star, metric_inverse, direction)
        for direction in witness_directions
    ]

    identity_rank = matrix_rank(
        [[entry for row in matrix for entry in row] for matrix in identity_derivatives]
    )
    witness_rank = matrix_rank(
        [[entry for row in matrix for entry in row] for matrix in witness_derivatives]
    )
    direction_rank = matrix_rank(
        [[entry for row in matrix for entry in row] for matrix in directions]
    )
    hermitian_checks = [
        multiply(multiply(transpose(complex_structure), direction), complex_structure)
        == direction
        for direction in directions
    ]

    witness_hashes = [
        row["Hodge_derivative_sha256"]
        for row in response["non_diagonal_metric_variations"]
    ]
    witness_direction_hashes = [
        row["metric_direction_sha256"]
        for row in response["non_diagonal_metric_variations"]
    ]

    checks: dict[str, bool] = {
        **{f"builder::{name}": value for name, value in packet["checks"].items()},
        **{f"source::{name}": value for name, value in source_checks.items()},
        "schema_identifier_is_exact": schema["$id"]
        == "boe.mtt.q79-hermitian-metric-hodge-compiler.v1",
        "schema_required_fields_are_present": set(schema["required"]).issubset(packet),
        "packet_hash_recomputes_exactly": canonical_hash(core) == stored_hash,
        "packet_claim_is_T52": packet["claim_id"] == "CBF.T52",
        "real_coframe_recomputes_metric": recomputed_metric == metric,
        "metric_is_symmetric": metric == transpose(metric),
        "metric_is_positive_by_leading_minors": all(
            determinant([row[:size] for row in metric[:size]]) > 0
            for size in range(1, N + 1)
        ),
        "metric_determinant_is_one": determinant(metric) == 1,
        "metric_inverse_recomputes_exactly": matrix_strings(metric_inverse)
        == witness["covector_metric_H"],
        "metric_is_Hermitian": multiply(
            multiply(transpose(complex_structure), metric), complex_structure
        )
        == metric,
        "full_Hodge_matrix_recomputes_exactly": recomputed_star == packet_star,
        "full_Hodge_hash_recomputes_exactly": matrix_hash(recomputed_star)
        == witness["full_Hodge_sha256"],
        "full_Hodge_has_recorded_nonzero_count": sum(
            int(value != 0) for row in recomputed_star for value in row
        )
        == witness["full_Hodge_nonzero_entries"],
        "Hodge_square_recomputes_exactly": multiply(recomputed_star, recomputed_star)
        == expected_star_square(),
        "all_wedge_metric_identities_recompute": wedge_identities_hold(
            recomputed_star, metric_inverse, volume
        ),
        "Hodge_isometry_recomputes_exactly": multiply(
            multiply(transpose(recomputed_star), gram), recomputed_star
        )
        == gram,
        "identity_specialization_equals_T51": identity_star == t51_star,
        "eight_direction_labels_are_distinct": len(set(response["direction_labels"])) == 8,
        "eight_direction_matrices_are_emitted": len(directions) == 8,
        "all_directions_are_symmetric": all(
            direction == transpose(direction) for direction in directions
        ),
        "all_identity_directions_are_trace_free": all(
            trace(direction) == 0 for direction in directions
        ),
        "all_directions_are_Hermitian": all(hermitian_checks),
        "direction_span_rank_recomputes_as_eight": direction_rank == 8,
        "identity_minor_and_formula_derivatives_match": identity_derivatives
        == identity_formula_derivatives,
        "identity_derivatives_match_packet_entries": identity_derivatives
        == packet_identity_derivatives,
        "identity_derivative_hashes_match": all(
            matrix_hash(matrix) == row["Hodge_derivative_sha256"]
            for matrix, row in zip(identity_derivatives, direction_rows)
        ),
        "witness_directions_have_zero_relative_trace": all(
            trace(multiply(metric_inverse, direction)) == 0
            for direction in witness_directions
        ),
        "witness_direction_hashes_match": [
            matrix_hash(direction) for direction in witness_directions
        ]
        == witness_direction_hashes,
        "witness_minor_and_formula_derivatives_match": witness_derivatives
        == witness_formula_derivatives,
        "witness_derivative_hashes_match": [
            matrix_hash(matrix) for matrix in witness_derivatives
        ]
        == witness_hashes,
        "identity_response_rank_is_eight": identity_rank == 8,
        "witness_response_rank_is_eight": witness_rank == 8,
        "packet_records_injective_eight_shape_response": response[
            "injective_on_all_eight_shape_directions"
        ],
        "selected_metric_values_remain_open": q79[
            "selected_metric_endomorphism_values"
        ]
        == "OPEN",
        "same_member_beta_root_remains_open": q79[
            "same_member_beta_C_root_EA03R"
        ]
        == "OPEN",
        "selected_HYM_endpoint_remains_open": q79[
            "selected_visible_hidden_HYM_metric_and_connection"
        ]
        == "OPEN",
        "rank102_execution_remains_open": q79[
            "rank102_Dbar_domains_projector_and_Green"
        ]
        == "OPEN",
        "one_shared_action_primitive_is_preserved": ledger[
            "shared_action_primitives_before_T52"
        ]
        == ledger["shared_action_primitives_after_T52"]
        == 1,
        "no_parameters_or_selectors_are_added": ledger["continuous_parameters_added"]
        == ledger["discrete_selectors_added"]
        == 0,
        "no_observed_or_fitted_values_are_used": ledger["observed_values_used"]
        == ledger["fitted_values_used"]
        == 0,
        "eight_shapes_remain_selected_source_fields": ledger[
            "unresolved_metric_shape_source_fields"
        ]
        == 8
        and not ledger["metric_shape_fields_are_fit_parameters"],
        "physical_counters_remain_zero": boundary["physical_gates"]
        == {"accepted": 0, "total": 3}
        and boundary["physical_packets"] == {"accepted": 0, "total": 3}
        and boundary["physical_rows"] == {"accepted": 0, "total": 7},
        "all_controlling_blockers_remain_open": not boundary["B_HS_01_closed"]
        and not boundary["B_GEO_01_closed"]
        and not boundary["B_ACTION_01_closed"]
        and not boundary["B_QFT_02_closed"],
        "theorem_declares_compiler_tier": "exact supplied-metric compiler" in theorem,
        "theorem_forbids_physical_metric_promotion": "does not select the physical q79 metric"
        in theorem,
        "theorem_proves_rank_eight_response": "rank-eight shape response" in theorem,
        "theorem_preserves_graph_Prym_boundary": "does not bypass the graph-Prym endpoint"
        in theorem,
    }

    summary = {
        "passed": sum(int(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    print(json.dumps(summary, indent=2))
    if not summary["all_passed"]:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"independent verification failed: {failed}")


if __name__ == "__main__":
    main()
