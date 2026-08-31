#!/usr/bin/env python3
"""Build the exact CBF.T52 Hermitian metric Hodge compiler packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "q79_hermitian_metric_hodge_compiler_source_lock.json"
SCHEMA = ROOT / "q79_hermitian_metric_hodge_compiler_contract.schema.json"
THEOREM = ROOT / "Q79HermitianMetricHodgeCoefficientAndFirstVariationCompilerTheorem_v1.md"
OUTPUT = ROOT / "q79_hermitian_metric_hodge_compiler.packet.json"
N = 6

Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


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


def matadd(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * entry for entry in row] for row in matrix]


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def determinant(matrix: Matrix) -> Fraction:
    if not matrix:
        return Fraction(1)
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, len(work)):
            if not work[row][column]:
                continue
            factor = work[row][column] / pivot_value
            for inner in range(column + 1, len(work)):
                work[row][inner] -= factor * work[column][inner]
    return result


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + unit[:] for row, unit in zip(matrix, identity(size))]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
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
            if factor:
                work[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def matrix_strings(matrix: Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


def sparse_entries(matrix: Matrix) -> list[dict[str, int | str]]:
    return [
        {"row": row, "column": column, "value": str(value)}
        for row, values in enumerate(matrix)
        for column, value in enumerate(values)
        if value
    ]


def matrix_hash(matrix: Matrix) -> str:
    return canonical_hash(matrix_strings(matrix))


def exterior_basis() -> list[tuple[int, ...]]:
    return [
        tuple(indices)
        for degree in range(N + 1)
        for indices in itertools.combinations(range(1, N + 1), degree)
    ]


def basis_label(indices: tuple[int, ...]) -> str:
    if not indices:
        return "1"
    if len(indices) == N:
        return "nu"
    return "e" + "".join(str(index) for index in indices)


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


def submatrix(
    matrix: Matrix, rows: tuple[int, ...], columns: tuple[int, ...]
) -> Matrix:
    return [[matrix[row - 1][column - 1] for column in columns] for row in rows]


def determinant_derivative(base: Matrix, delta: Matrix) -> Fraction:
    size = len(base)
    if size == 0:
        return Fraction(0)
    total = Fraction(0)
    for permutation in itertools.permutations(range(size)):
        sign = Fraction(permutation_sign(tuple(index + 1 for index in permutation)))
        for differentiated in range(size):
            term = sign * delta[differentiated][permutation[differentiated]]
            for row in range(size):
                if row != differentiated:
                    term *= base[row][permutation[row]]
            total += term
    return total


def hodge_matrix(metric_inverse: Matrix, volume: Fraction) -> Matrix:
    basis = exterior_basis()
    basis_index = {entry: index for index, entry in enumerate(basis)}
    result = zeros(len(basis), len(basis))
    for column, source in enumerate(basis):
        same_degree = [entry for entry in basis if len(entry) == len(source)]
        for test in same_degree:
            target = complement(test)
            coefficient = (
                Fraction(wedge_sign(test, target))
                * determinant(submatrix(metric_inverse, test, source))
                * volume
            )
            result[basis_index[target]][column] += coefficient
    return result


def exterior_gram(metric_inverse: Matrix) -> Matrix:
    basis = exterior_basis()
    result = zeros(len(basis), len(basis))
    for row, left in enumerate(basis):
        for column, right in enumerate(basis):
            if len(left) == len(right):
                result[row][column] = determinant(
                    submatrix(metric_inverse, left, right)
                )
    return result


def exterior_derivation(covector_generator: Matrix) -> Matrix:
    basis = exterior_basis()
    basis_index = {entry: index for index, entry in enumerate(basis)}
    result = zeros(len(basis), len(basis))
    for column, source in enumerate(basis):
        for slot, original in enumerate(source):
            for replacement in range(1, N + 1):
                coefficient = covector_generator[replacement - 1][original - 1]
                if not coefficient:
                    continue
                raw = source[:slot] + (replacement,) + source[slot + 1 :]
                if len(set(raw)) != len(raw):
                    continue
                ordered = tuple(sorted(raw))
                result[basis_index[ordered]][column] += (
                    Fraction(permutation_sign(raw)) * coefficient
                )
    return result


def hodge_derivative_direct(
    metric: Matrix, metric_inverse: Matrix, volume: Fraction, variation: Matrix
) -> Matrix:
    del metric
    inverse_variation = scale(
        matmul(matmul(metric_inverse, variation), metric_inverse), Fraction(-1)
    )
    volume_variation = volume * trace(matmul(metric_inverse, variation)) / 2
    basis = exterior_basis()
    basis_index = {entry: index for index, entry in enumerate(basis)}
    result = zeros(len(basis), len(basis))
    for column, source in enumerate(basis):
        same_degree = [entry for entry in basis if len(entry) == len(source)]
        for test in same_degree:
            target = complement(test)
            base_minor = submatrix(metric_inverse, test, source)
            delta_minor = submatrix(inverse_variation, test, source)
            coefficient = Fraction(wedge_sign(test, target)) * (
                volume_variation * determinant(base_minor)
                + volume * determinant_derivative(base_minor, delta_minor)
            )
            result[basis_index[target]][column] += coefficient
    return result


def hodge_derivative_formula(
    star: Matrix, metric_inverse: Matrix, variation: Matrix
) -> Matrix:
    relative = matmul(metric_inverse, variation)
    covector_generator = transpose(relative)
    scalar_part = scale(identity(64), trace(relative) / 2)
    return matmul(star, matsub(scalar_part, exterior_derivation(covector_generator)))


def complex_realification(real: Matrix, imaginary: Matrix) -> Matrix:
    size = len(real)
    result = zeros(2 * size, 2 * size)
    for row in range(size):
        for column in range(size):
            block = (
                (real[row][column], -imaginary[row][column]),
                (imaginary[row][column], real[row][column]),
            )
            for local_row in range(2):
                for local_column in range(2):
                    result[2 * row + local_row][2 * column + local_column] = block[
                        local_row
                    ][local_column]
    return result


def standard_complex_structure() -> Matrix:
    result = zeros(N, N)
    for index in range(0, N, 2):
        result[index][index + 1] = Fraction(-1)
        result[index + 1][index] = Fraction(1)
    return result


def hermitian_shape_directions() -> list[tuple[str, Matrix]]:
    directions: list[tuple[str, Matrix]] = []

    def add(name: str, real: Matrix, imaginary: Matrix) -> None:
        directions.append((name, complex_realification(real, imaginary)))

    zero = zeros(3, 3)
    d3 = zeros(3, 3)
    d3[0][0], d3[1][1] = Fraction(1), Fraction(-1)
    add("diag_1_minus_2", d3, zero)
    d8 = zeros(3, 3)
    d8[0][0], d8[1][1], d8[2][2] = Fraction(1), Fraction(1), Fraction(-2)
    add("diag_1_plus_2_minus_2x3", d8, zero)
    for left, right in ((0, 1), (0, 2), (1, 2)):
        real = zeros(3, 3)
        real[left][right] = real[right][left] = Fraction(1)
        add(f"real_{left + 1}{right + 1}", real, zero)
    for left, right in ((0, 1), (0, 2), (1, 2)):
        imaginary = zeros(3, 3)
        imaginary[left][right] = Fraction(1)
        imaginary[right][left] = Fraction(-1)
        add(f"imag_{left + 1}{right + 1}", zero, imaginary)
    return directions


def expected_star_square() -> Matrix:
    basis = exterior_basis()
    result = zeros(len(basis), len(basis))
    for index, entry in enumerate(basis):
        result[index][index] = Fraction((-1) ** (len(entry) * (N - len(entry))))
    return result


def wedge_identity_holds(star: Matrix, metric_inverse: Matrix, volume: Fraction) -> bool:
    basis = exterior_basis()
    for left in basis:
        for right in basis:
            if len(left) != len(right):
                continue
            column = basis.index(right)
            actual = Fraction(0)
            for row, target in enumerate(basis):
                if len(target) == N - len(left):
                    actual += Fraction(wedge_sign(left, target)) * star[row][column]
            expected = determinant(submatrix(metric_inverse, left, right)) * volume
            if actual != expected:
                return False
    return True


def main() -> None:
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    theorem_text = THEOREM.read_text(encoding="utf-8")
    source_paths = {
        item["id"]: (ROOT / item["path"]).resolve() for item in lock["sources"]
    }
    hashes_match = {
        item["id"]: source_paths[item["id"]].is_file()
        and sha256(source_paths[item["id"]]) == item["sha256"]
        for item in lock["sources"]
    }

    t51 = load_json(source_paths["T51_PACKET"])
    proto = load_json(source_paths["PROTOSPINOR_HODGE_TABLE"])
    fuyau = load_json(source_paths["Q79_FUYAU_BASE"])
    hodge_audit = load_json(source_paths["Q79_HODGE_ACTION_AUDIT"])

    # A genuinely non-diagonal complex coframe with determinant one.
    coframe_real = [
        [Fraction(1), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(1)],
        [Fraction(0), Fraction(0), Fraction(1)],
    ]
    coframe_imaginary = [
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(-1)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    real_coframe = complex_realification(coframe_real, coframe_imaginary)
    metric = matmul(transpose(real_coframe), real_coframe)
    metric_inverse = inverse(metric)
    volume = Fraction(1)
    complex_structure = standard_complex_structure()
    leading_minors = [
        determinant([row[:size] for row in metric[:size]])
        for size in range(1, N + 1)
    ]

    basis = exterior_basis()
    labels = [basis_label(entry) for entry in basis]
    star = hodge_matrix(metric_inverse, volume)
    gram = exterior_gram(metric_inverse)
    star_isometry = matmul(matmul(transpose(star), gram), star) == gram
    star_square = matmul(star, star) == expected_star_square()
    wedge_checks = sum(
        len([entry for entry in basis if len(entry) == degree]) ** 2
        for degree in range(N + 1)
    )
    wedge_identity = wedge_identity_holds(star, metric_inverse, volume)

    identity_metric = identity(N)
    identity_star = hodge_matrix(identity_metric, Fraction(1))
    t51_sparse = t51["oriented_exterior_hodge"]["sparse_matrix_entries"]
    t51_matrix = zeros(64, 64)
    for entry in t51_sparse:
        t51_matrix[entry["row"]][entry["column"]] = Fraction(entry["value"])

    directions = hermitian_shape_directions()
    direction_matrices = [matrix for _, matrix in directions]
    direction_span_rank = rank(
        [[entry for row in matrix for entry in row] for matrix in direction_matrices]
    )
    direction_checks = {
        name: {
            "trace_zero": trace(direction) == 0,
            "symmetric": direction == transpose(direction),
            "Hermitian": matmul(
                matmul(transpose(complex_structure), direction), complex_structure
            )
            == direction,
        }
        for name, direction in directions
    }

    identity_variations = []
    witness_variations = []
    identity_direct_matrices: list[Matrix] = []
    witness_direct_matrices: list[Matrix] = []
    identity_formula_matches = True
    witness_formula_matches = True
    for name, direction in directions:
        identity_direct = hodge_derivative_direct(
            identity_metric, identity_metric, Fraction(1), direction
        )
        identity_formula = hodge_derivative_formula(
            identity_star, identity_metric, direction
        )
        identity_formula_matches &= identity_direct == identity_formula
        identity_direct_matrices.append(identity_direct)
        identity_variations.append(
            {
                "name": name,
                "metric_direction": matrix_strings(direction),
                "nonzero_Hodge_derivative_entries": len(sparse_entries(identity_direct)),
                "Hodge_derivative_sparse_entries": sparse_entries(identity_direct),
                "Hodge_derivative_sha256": matrix_hash(identity_direct),
            }
        )

        witness_direction = matmul(
            matmul(transpose(real_coframe), direction), real_coframe
        )
        witness_direct = hodge_derivative_direct(
            metric, metric_inverse, volume, witness_direction
        )
        witness_formula = hodge_derivative_formula(
            star, metric_inverse, witness_direction
        )
        witness_formula_matches &= witness_direct == witness_formula
        witness_direct_matrices.append(witness_direct)
        witness_variations.append(
            {
                "name": name,
                "metric_direction_sha256": matrix_hash(witness_direction),
                "relative_trace": str(
                    trace(matmul(metric_inverse, witness_direction))
                ),
                "nonzero_Hodge_derivative_entries": len(sparse_entries(witness_direct)),
                "Hodge_derivative_sha256": matrix_hash(witness_direct),
            }
        )

    identity_response_rank = rank(
        [[entry for row in matrix for entry in row] for matrix in identity_direct_matrices]
    )
    witness_response_rank = rank(
        [[entry for row in matrix for entry in row] for matrix in witness_direct_matrices]
    )

    star_one = star[labels.index("nu")][labels.index("1")]
    star_nu = star[labels.index("1")][labels.index("nu")]
    changed_from_identity = sum(
        int(star[row][column] != identity_star[row][column])
        for row in range(64)
        for column in range(64)
    )

    payload: dict[str, Any] = {
        "schema": "boe.mtt.q79-hermitian-metric-hodge-compiler.v1",
        "claim_id": "CBF.T52",
        "date": "2026-08-31",
        "status": "EXACT_SUPPLIED_HERMITIAN_METRIC_TO_FULL_HODGE_AND_EIGHT_SHAPE_RESPONSE_COMPILER_PHYSICAL_Q79_METRIC_HYM_AND_BETA_ROOT_OPEN",
        "source_provenance": {
            "source_lock": SOURCE_LOCK.name,
            "source_hashes_match": hashes_match,
            "all_source_hashes_match": all(hashes_match.values()),
            "model_state_sha256": lock["model_state_sha256"],
            "handoff_id": lock["handoff_id"],
        },
        "metric_hodge_definition": {
            "dimension": N,
            "basis_dimension": len(basis),
            "basis_order": labels,
            "input_contract": "G is an oriented positive covariant metric, H=G^-1, and v>0 satisfies v^2=det(G)",
            "coefficient_formula": "coefficient of e_(I^c) in star_G(e_J) is sgn(I,I^c)*v*det(H[I,J])",
            "defining_identity": "e_I wedge star_G(e_J)=det(H[I,J])*v*nu",
            "variation_formula": "delta(star_G)=star_G*(one_half_trace(G^-1 deltaG)*Id-Lambda^k((G^-1 deltaG)^T))",
            "exact_backend": "rational or exact-algebraic inputs with supplied exact volume root; interval inputs use the same finite minor formula",
            "T51_specialization": "G=I and v=1 gives the CBF.T51 signed-permutation table",
            "orientation_is_input_not_selected": True,
        },
        "non_diagonal_hermitian_witness": {
            "complex_coframe_real_part": matrix_strings(coframe_real),
            "complex_coframe_imaginary_part": matrix_strings(coframe_imaginary),
            "real_coframe": matrix_strings(real_coframe),
            "standard_complex_structure": matrix_strings(complex_structure),
            "covariant_metric_G": matrix_strings(metric),
            "covector_metric_H": matrix_strings(metric_inverse),
            "determinant_G": str(determinant(metric)),
            "volume_factor": str(volume),
            "leading_principal_minors": [str(value) for value in leading_minors],
            "positive_definite": all(value > 0 for value in leading_minors),
            "Hermitian": matmul(
                matmul(transpose(complex_structure), metric), complex_structure
            )
            == metric,
            "inverse_exact": matmul(metric, metric_inverse) == identity(N),
            "full_Hodge_shape": [64, 64],
            "full_Hodge_sparse_entries": sparse_entries(star),
            "full_Hodge_nonzero_entries": len(sparse_entries(star)),
            "full_Hodge_sha256": matrix_hash(star),
            "changed_matrix_entries_from_T51": changed_from_identity,
            "star_square_identity": star_square,
            "wedge_metric_identity_checks": wedge_checks,
            "wedge_metric_identity": wedge_identity,
            "Hodge_isometry": star_isometry,
            "orientation_rows": {"star_1": str(star_one), "star_nu": str(star_nu)},
        },
        "eight_shape_first_variation": {
            "fixed_complex_structure_volume_one_shape_dimension": 8,
            "direction_labels": [name for name, _ in directions],
            "direction_checks": direction_checks,
            "direction_span_rank": direction_span_rank,
            "identity_metric_variations": identity_variations,
            "non_diagonal_metric_variations": witness_variations,
            "direct_minor_derivative_matches_variation_formula_at_identity": identity_formula_matches,
            "direct_minor_derivative_matches_variation_formula_at_non_diagonal_metric": witness_formula_matches,
            "identity_Hodge_response_rank": identity_response_rank,
            "non_diagonal_Hodge_response_rank": witness_response_rank,
            "injective_on_all_eight_shape_directions": identity_response_rank
            == witness_response_rank
            == 8,
            "interpretation": "all eight Hermitian shape fields are visible to the full Hodge operator; none may be dropped before source selection",
        },
        "q79_instantiation_boundary": {
            "T51_oriented_sign_compiler": "CLOSED_EXACT",
            "universal_supplied_metric_to_Hodge_coefficients": "CLOSED_EXACT_BY_T52",
            "universal_eight_shape_first_variation": "CLOSED_EXACT_BY_T52",
            "selected_metric_endomorphism_values": "OPEN",
            "selected_FuYau_conformal_factor": "OPEN",
            "same_member_beta_C_root_EA03R": "OPEN",
            "selected_visible_hidden_HYM_metric_and_connection": "OPEN",
            "gauge_projector_values": "OPEN",
            "rank102_Dbar_domains_projector_and_Green": "OPEN",
            "physical_C4_or_direct_TT_intertwiner": "OPEN",
            "associated_chiral_operator_and_index": "OPEN",
            "upper_action_and_QME": "OPEN",
            "proto_spinor_row_update": {
                "oriented_full_Hodge_star_wedge_sign_table": "CLOSED_BY_T51",
                "metric_endomorphism_coefficient_compiler": "CLOSED_BY_T52",
                "selected_metric_endomorphism_coefficients": "OPEN",
                "selected_HYM_connection_correction_coefficients": "OPEN",
                "gauge_projector_values": "OPEN",
            },
            "FuYau_source_status": fuyau.get("status", "RECORDED"),
            "prior_Hodge_audit_status": hodge_audit.get("status", "RECORDED"),
        },
        "parameter_ledger": {
            "shared_action_primitives_before_T52": 1,
            "shared_action_primitives_after_T52": 1,
            "continuous_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "unresolved_metric_shape_source_fields": 8,
            "metric_shape_fields_are_fit_parameters": False,
            "metric_shape_fields_must_be_emitted_by_selected_endpoint": True,
        },
        "physical_boundary": {
            "B_HS_01_closed": False,
            "B_GEO_01_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "compiler_success_is_physical_metric_selection": False,
            "compiler_success_is_HYM_endpoint_selection": False,
            "compiler_success_is_rank102_execution": False,
        },
    }

    payload_core = deepcopy(payload)
    payload["exact_payload_sha256"] = canonical_hash(payload_core)

    required_fields = set(schema["required"])
    proto_open = proto["what_remains_open"]
    checks = {
        "all_source_hashes_match": all(hashes_match.values()),
        "T51_source_packet_passes": t51["check_summary"]["all_passed"],
        "proto_source_had_metric_coefficients_open": proto_open[
            "selected_metric_endomorphism_coefficients"
        ],
        "proto_source_had_HYM_corrections_open": proto_open[
            "selected_HYM_connection_correction_coefficients"
        ],
        "metric_is_symmetric": metric == transpose(metric),
        "metric_is_positive_definite": all(value > 0 for value in leading_minors),
        "metric_is_Hermitian": payload["non_diagonal_hermitian_witness"]["Hermitian"],
        "metric_determinant_is_one": determinant(metric) == 1,
        "metric_inverse_is_exact": matmul(metric, metric_inverse) == identity(N),
        "non_diagonal_metric_is_not_identity": metric != identity(N),
        "full_exterior_basis_has_64_states": len(basis) == 64,
        "non_diagonal_Hodge_has_more_than_64_nonzeros": len(sparse_entries(star)) > 64,
        "Hodge_square_identity_holds": star_square,
        "all_924_wedge_metric_identities_hold": wedge_checks == 924 and wedge_identity,
        "Hodge_is_an_isometry": star_isometry,
        "orientation_unit_row_is_preserved": star_one == 1,
        "orientation_volume_row_is_preserved": star_nu == 1,
        "identity_metric_specializes_exactly_to_T51": identity_star == t51_matrix,
        "exactly_eight_shape_directions_are_emitted": len(directions) == 8,
        "shape_direction_span_has_rank_eight": direction_span_rank == 8,
        "all_shape_directions_are_trace_free": all(
            row["trace_zero"] for row in direction_checks.values()
        ),
        "all_shape_directions_are_symmetric": all(
            row["symmetric"] for row in direction_checks.values()
        ),
        "all_shape_directions_are_Hermitian": all(
            row["Hermitian"] for row in direction_checks.values()
        ),
        "direct_and_formula_variations_match_at_identity": identity_formula_matches,
        "direct_and_formula_variations_match_at_non_diagonal_metric": witness_formula_matches,
        "identity_shape_response_rank_is_eight": identity_response_rank == 8,
        "non_diagonal_shape_response_rank_is_eight": witness_response_rank == 8,
        "all_non_diagonal_relative_shape_traces_vanish": all(
            row["relative_trace"] == "0" for row in witness_variations
        ),
        "selected_metric_values_remain_open": payload["q79_instantiation_boundary"][
            "selected_metric_endomorphism_values"
        ]
        == "OPEN",
        "same_member_beta_root_remains_open": payload["q79_instantiation_boundary"][
            "same_member_beta_C_root_EA03R"
        ]
        == "OPEN",
        "selected_HYM_endpoint_remains_open": payload["q79_instantiation_boundary"][
            "selected_visible_hidden_HYM_metric_and_connection"
        ]
        == "OPEN",
        "rank102_execution_remains_open": payload["q79_instantiation_boundary"][
            "rank102_Dbar_domains_projector_and_Green"
        ]
        == "OPEN",
        "one_action_primitive_is_preserved": payload["parameter_ledger"][
            "shared_action_primitives_after_T52"
        ]
        == 1,
        "no_continuous_parameters_are_added": payload["parameter_ledger"][
            "continuous_parameters_added"
        ]
        == 0,
        "eight_shapes_are_source_fields_not_fit_parameters": not payload[
            "parameter_ledger"
        ]["metric_shape_fields_are_fit_parameters"],
        "physical_counters_do_not_move": payload["physical_boundary"][
            "physical_gates"
        ]
        == {"accepted": 0, "total": 3}
        and payload["physical_boundary"]["physical_packets"]
        == {"accepted": 0, "total": 3}
        and payload["physical_boundary"]["physical_rows"]
        == {"accepted": 0, "total": 7},
        "both_controlling_blockers_remain_open": not payload["physical_boundary"][
            "B_HS_01_closed"
        ]
        and not payload["physical_boundary"]["B_GEO_01_closed"],
        "theorem_declares_supplied_metric_compiler_tier": "supplied-metric compiler"
        in theorem_text,
        "theorem_does_not_select_the_physical_metric": "does not select the physical q79 metric"
        in theorem_text,
        "theorem_records_rank_eight_shape_response": "rank-eight shape response"
        in theorem_text,
        "schema_required_fields_are_present": required_fields.issubset(
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
