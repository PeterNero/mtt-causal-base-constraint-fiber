#!/usr/bin/env python3
"""Independently verify the exact CBF.T57 packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "augmented_heterotic_triangular_principal_symbol.packet.json"
SOURCE_LOCK = ROOT / "augmented_heterotic_triangular_principal_symbol_source_lock.json"
SCHEMA = ROOT / "augmented_heterotic_triangular_principal_symbol_contract.schema.json"
AUDIT = ROOT / "augmented_heterotic_triangular_external_source.audit.json"
N = 6
M = 3
R = 4
A = Fraction(1, 2)
KAPPA = Fraction(7)

RealMatrix = list[list[Fraction]]
Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = list[list[Gaussian]]
ZERO: Gaussian = (Fraction(0), Fraction(0))
ONE: Gaussian = (Fraction(1), Fraction(0))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def fractions(matrix: list[list[str]]) -> RealMatrix:
    return [[Fraction(entry) for entry in row] for row in matrix]


def strings(matrix: RealMatrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


def zeros(rows: int, columns: int) -> RealMatrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> RealMatrix:
    return [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]


def transpose(matrix: list[list[Any]]) -> list[list[Any]]:
    return [list(row) for row in zip(*matrix)]


def matmul(left: RealMatrix, right: RealMatrix) -> RealMatrix:
    return [
        [sum((a * b for a, b in zip(left_row, right_column)), Fraction(0)) for right_column in transpose(right)]
        for left_row in left
    ]


def scale(matrix: RealMatrix, scalar: Fraction) -> RealMatrix:
    return [[scalar * entry for entry in row] for row in matrix]


def determinant(matrix: RealMatrix) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        value = work[column][column]
        result *= value
        for row in range(column + 1, len(work)):
            factor = work[row][column] / value
            for inner in range(column + 1, len(work)):
                work[row][inner] -= factor * work[column][inner]
    return result


def inverse(matrix: RealMatrix) -> RealMatrix:
    size = len(matrix)
    work = [row[:] + unit[:] for row, unit in zip(matrix, identity(size))]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [entry - factor * pivot_entry for entry, pivot_entry in zip(work[row], work[column])]
    return [row[size:] for row in work]


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gneg(value: Gaussian) -> Gaussian:
    return -value[0], -value[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def gconj(value: Gaussian) -> Gaussian:
    return value[0], -value[1]


def ginv(value: Gaussian) -> Gaussian:
    denominator = value[0] * value[0] + value[1] * value[1]
    return value[0] / denominator, -value[1] / denominator


def gsum(values: Iterable[Gaussian]) -> Gaussian:
    result = ZERO
    for value in values:
        result = gadd(result, value)
    return result


def gzeros(rows: int, columns: int) -> GaussianMatrix:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def gidentity(size: int) -> GaussianMatrix:
    return [[ONE if row == column else ZERO for column in range(size)] for row in range(size)]


def gadd_matrix(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [[gadd(a, b) for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def gsub_matrix(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [[gadd(a, gneg(b)) for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def gscale_matrix(matrix: GaussianMatrix, scalar: Fraction) -> GaussianMatrix:
    return [[gmul((scalar, Fraction(0)), entry) for entry in row] for row in matrix]


def gadjoint(matrix: GaussianMatrix) -> GaussianMatrix:
    return [[gconj(entry) for entry in row] for row in transpose(matrix)]


def gmatmul(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [
        [gsum(gmul(a, b) for a, b in zip(left_row, right_column)) for right_column in transpose(right)]
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


def gstrings(matrix: GaussianMatrix) -> list[list[str]]:
    return [[gaussian_string(entry) for entry in row] for row in matrix]


def grank(matrix: GaussianMatrix) -> int:
    work = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column] != ZERO), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse_pivot = ginv(work[pivot_row][column])
        work[pivot_row] = [gmul(inverse_pivot, entry) for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or work[row][column] == ZERO:
                continue
            factor = work[row][column]
            work[row] = [gadd(entry, gneg(gmul(factor, pivot_entry))) for entry, pivot_entry in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def basis(degree: int) -> list[tuple[int, ...]]:
    if degree < 0 or degree > M:
        return []
    return list(itertools.combinations(range(M), degree))


def wedge(covector: list[Gaussian], degree: int) -> GaussianMatrix:
    source = basis(degree)
    target = basis(degree + 1)
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


def diagonal_tensor(rank: int, matrix: GaussianMatrix) -> GaussianMatrix:
    result = gzeros(rank * len(matrix), rank * len(matrix[0]))
    for lane in range(rank):
        for row in range(len(matrix)):
            for column in range(len(matrix[0])):
                result[lane * len(matrix) + row][lane * len(matrix[0]) + column] = matrix[row][column]
    return result


def partial(alpha: list[Gaussian], degree: int, rank: int) -> GaussianMatrix:
    count = len(basis(degree))
    result = gzeros(rank * count, count)
    for lane, coefficient in enumerate(alpha):
        for index in range(count):
            result[lane * count + index][index] = coefficient
    return result


def symbol(beta: list[Gaussian], alpha: list[Gaussian], degree: int) -> GaussianMatrix:
    d = diagonal_tensor(R, wedge(beta, degree))
    c = wedge(beta, degree + 1)
    p = partial(alpha, degree + 1, R)
    left = len(d[0])
    right = len(p[0])
    result = gzeros(len(d) + len(c), left + right)
    sign = Fraction(1 if degree % 2 == 0 else -1)
    for row in range(len(d)):
        for column in range(left):
            result[row][column] = d[row][column]
        for column in range(right):
            result[row][left + column] = gmul((sign * A, Fraction(0)), p[row][column])
    for row in range(len(c)):
        for column in range(right):
            result[len(d) + row][left + column] = c[row][column]
    return result


def matvec(matrix: RealMatrix, vector: list[Fraction]) -> list[Fraction]:
    return [sum((entry * value for entry, value in zip(row, vector)), Fraction(0)) for row in matrix]


def quadratic(matrix: RealMatrix, vector: list[Fraction]) -> Fraction:
    return sum((vector[i] * matrix[i][j] * vector[j] for i in range(N) for j in range(N)), Fraction(0))


def reconstruct(samples: list[dict[str, Any]]) -> RealMatrix:
    diagonal: dict[int, Fraction] = {}
    pairs: dict[tuple[int, int], Fraction] = {}
    for sample in samples:
        value = Fraction(sample["corrected_baseline_action_scalar"])
        if sample["column"] is None:
            diagonal[int(sample["row"])] = value
        else:
            pairs[(int(sample["row"]), int(sample["column"]))] = value
    result = zeros(N, N)
    for row, value in diagonal.items():
        result[row][row] = value
    for (row, column), value in pairs.items():
        result[row][column] = result[column][row] = (value - diagonal[row] - diagonal[column]) / 2
    return result


def exact_root(value: Fraction, degree: int) -> Fraction:
    def integer_root(number: int) -> int:
        low, high = 0, max(1, number)
        while low <= high:
            middle = (low + high) // 2
            power = middle**degree
            if power == number:
                return middle
            if power < number:
                low = middle + 1
            else:
                high = middle - 1
        raise ValueError("not an exact root")
    return Fraction(integer_root(value.numerator), integer_root(value.denominator))


def exterior_basis() -> list[tuple[int, ...]]:
    return [tuple(indices) for degree in range(N + 1) for indices in itertools.combinations(range(1, N + 1), degree)]


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(int(sequence[left] > sequence[right]) for left in range(len(sequence)) for right in range(left + 1, len(sequence)))
    return -1 if inversions % 2 else 1


def minor(matrix: RealMatrix, rows: tuple[int, ...], columns: tuple[int, ...]) -> RealMatrix:
    return [[matrix[row - 1][column - 1] for column in columns] for row in rows]


def hodge(metric_inverse: RealMatrix, volume: Fraction) -> RealMatrix:
    all_basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(all_basis)}
    result = zeros(64, 64)
    for column, source in enumerate(all_basis):
        for test in (entry for entry in all_basis if len(entry) == len(source)):
            target = tuple(index for index in range(1, N + 1) if index not in test)
            result[lookup[target]][column] += permutation_sign(test + target) * volume * determinant(minor(metric_inverse, test, source))
    return result


def main() -> None:
    packet = load_json(PACKET)
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    audit = load_json(AUDIT)
    witness = packet["exact_six_dimensional_witness"]
    recovery = packet["same_source_recovery"]
    samples = witness["samples"]

    source_matches = [sha256(ROOT / source["path"]) == source["sha256"] for source in lock["sources"]]
    coframe = fractions(witness["coframe"])
    G = fractions(witness["covariant_metric_G"])
    H = fractions(witness["contravariant_metric_H"])
    inverse_transpose = transpose(inverse(coframe))
    dimension = int(witness["degree_one_dimension"])
    trace_factor = Fraction(witness["normalized_trace_factor"])
    replay_checks: list[bool] = []

    for sample in samples:
        vector = [Fraction(entry) for entry in sample["covector"]]
        eta = matvec(inverse_transpose, vector)
        beta = [(eta[2 * index], eta[2 * index + 1]) for index in range(M)]
        alpha = [gconj(entry) for entry in beta]
        q_value = quadratic(H, vector)
        l0 = symbol(beta, alpha, 0)
        l1 = symbol(beta, alpha, 1)
        nilpotent = gmatmul(l1, l0)
        delta = gadd_matrix(gmatmul(l0, gadjoint(l0)), gmatmul(gadjoint(l1), l1))
        baseline = gscale_matrix(gidentity(dimension), q_value)
        correction = gsub_matrix(delta, baseline)
        projector = gscale_matrix(correction, Fraction(1) / (A * A * q_value))
        high = q_value * (1 + A * A)
        two_level_residual = gsub_matrix(gsub_matrix(delta, baseline), gscale_matrix(projector, high - q_value))
        trace_value = gsum(delta[index][index] for index in range(dimension))[0] / dimension
        top = 3 * R
        replay_checks.extend(
            [
                all(entry == ZERO for row in nilpotent for entry in row),
                canonical_hash(gstrings(nilpotent)) == sample["nilpotence_sha256"],
                canonical_hash(gstrings(delta)) == sample["Hodge_symbol_sha256"],
                canonical_hash(gstrings(projector)) == sample["projector_sha256"],
                gmatmul(projector, projector) == projector,
                gadjoint(projector) == projector,
                grank(projector) == 6,
                all(delta[i][j] == ZERO and delta[j][i] == ZERO for i in range(top) for j in range(top, dimension)),
                all(entry == ZERO for row in two_level_residual for entry in row),
                Fraction(sample["metric_quadratic_q"]) == q_value,
                sample["complex_symbol_beta"] == [gaussian_string(entry) for entry in beta],
                Fraction(sample["baseline_eigenvalue"]) == q_value,
                Fraction(sample["elevated_eigenvalue"]) == high,
                sample["baseline_multiplicity"] == 9,
                sample["elevated_multiplicity"] == 6,
                Fraction(sample["normalized_trace"]) == trace_value,
                Fraction(sample["normalized_trace_factor"]) == Fraction(11, 10),
                grank(correction) == 6,
                Fraction(sample["corrected_baseline_action_scalar"]) == KAPPA * trace_value / trace_factor,
            ]
        )

    reconstructed_A = reconstruct(samples)
    density = Fraction(recovery["density_fixture"])
    recovered_scale = exact_root(density**2 * determinant(reconstructed_A), N)
    recovered_H = scale(reconstructed_A, Fraction(1) / recovered_scale)
    recovered_G = scale(inverse(reconstructed_A), recovered_scale)
    recovered_hodge = hodge(recovered_H, density)
    hodge_hash = canonical_hash(strings(recovered_hodge))

    expected_payload = canonical_hash(
        {
            "triangular_symbol_theorem": packet["triangular_symbol_theorem"],
            "samples": samples,
            "q79_rank102_specialization": packet["q79_rank102_specialization"],
            "same_source_recovery": recovery,
            "audit_sha256": sha256(AUDIT),
        }
    )
    theorem = packet["triangular_symbol_theorem"]
    q79 = packet["q79_rank102_specialization"]
    contract = packet["q79_source_contract_update"]
    ledger = packet["parameter_ledger"]
    boundary = packet["physical_boundary"]
    checks = {
        "packet_schema": packet["schema"] == "boe.mtt.augmented-heterotic-triangular-principal-symbol.v1",
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": set(schema["required"]).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T57",
        "source_hashes_match": all(source_matches),
        "source_count": len(source_matches) == 5,
        "builder_checks_pass": packet["check_summary"]["all_passed"],
        "builder_check_count": packet["check_summary"]["total"] == 52,
        "audit_exact": packet["source_provenance"]["external_audit"] == audit,
        "audit_role": audit["role"] == "source_locked_design_input_not_a_selected_physical_endpoint",
        "audit_source_count": len(audit["sources"]) == 2,
        "coframe_determinant": determinant(coframe) == 1,
        "coframe_nonorthogonal": matmul(transpose(coframe), coframe) != identity(N),
        "metric_from_coframe": matmul(transpose(coframe), coframe) == G,
        "metric_inverse": matmul(G, H) == identity(N),
        "sample_count": len(samples) == 21,
        "all_independent_sample_replays": all(replay_checks),
        "independent_replay_assertion_count": len(replay_checks) == 21 * 19,
        "full_symbol_nonscalar": not theorem["full_augmented_symbol_is_scalar"],
        "projector_rank_formula": theorem["projector_rank"] == 6,
        "off_diagonal_cancellation": theorem["off_diagonal_second_order_terms_cancel"],
        "rho_formula": theorem["relative_normalization_recovery"] == "rho=(lambda_high/lambda_low-1)/a^2",
        "witness_dimension": dimension == 15,
        "witness_multiplicities": witness["baseline_multiplicity"] == 9 and witness["elevated_multiplicity"] == 6,
        "witness_trace_factor": trace_factor == Fraction(11, 10),
        "witness_rho": Fraction(witness["recovered_relative_lane_normalization"]) == 1,
        "A_reconstruction": strings(reconstructed_A) == recovery["action_quadratic_A"],
        "scale_reconstruction": recovered_scale == KAPPA,
        "H_reconstruction": strings(recovered_H) == recovery["recovered_covector_metric_H"],
        "G_reconstruction": strings(recovered_G) == recovery["recovered_covariant_metric_G"],
        "Hodge_reconstruction": hodge_hash == recovery["source_T55_Hodge_sha256"],
        "Hodge_claim": recovery["Hodge_reconstruction_matches_T55"],
        "q79_rank": q79["Q_rank"] == 102,
        "q79_dimension": q79["degree_one_dimension"] == 309,
        "q79_projector_rank": q79["projector_rank"] == 6,
        "q79_multiplicities": q79["baseline_multiplicity"] == 303 and q79["elevated_multiplicity"] == 6,
        "q79_trace_formula": q79["normalized_trace_factor_formula"] == "1+rho/206",
        "q79_rho_one_factor": Fraction(q79["rho_one_benchmark_trace_factor"]) == Fraction(207, 206),
        "q79_benchmark_not_physical": not q79["rho_one_benchmark_is_physical"],
        "scalar_requirement_removed": contract["independent_scalar_full_symbol_obligation"] == "REMOVED_AS_FALSE_REQUIREMENT",
        "rho_source_not_duplicated": contract["independent_relative_lane_normalization_after_full_selected_symbol"] == 0,
        "metric_source_not_duplicated": contract["independent_metric_payload_after_full_selected_symbol_and_density"] == 0,
        "physical_complex_open": contract["selected_physical_q79_augmented_complex"] == "OPEN",
        "physical_density_open": contract["selected_physical_q79_density"] == "OPEN",
        "HYM_open": contract["selected_visible_hidden_HYM_connection"] == "OPEN",
        "no_parameters": ledger["continuous_physical_parameters_added"] == 0,
        "no_selectors": ledger["discrete_selectors_added"] == 0,
        "no_observed_values": ledger["observed_values_used"] == 0,
        "no_fits": ledger["fitted_values_used"] == 0,
        "rho_output_not_knob": ledger["rho_is_recovered_not_fitted_once_full_symbol_is_selected"],
        "B_GEO_open": not boundary["B_GEO_01_closed"],
        "B_ACTION_open": not boundary["B_ACTION_01_closed"],
        "B_OP_open": not boundary["B_OP_01_closed"],
        "physical_gates_unchanged": boundary["physical_gates"] == {"accepted": 0, "total": 3},
        "physical_packets_unchanged": boundary["physical_packets"] == {"accepted": 0, "total": 3},
        "physical_rows_unchanged": boundary["physical_rows"] == {"accepted": 0, "total": 7},
        "no_selected_endpoint_claim": not boundary["selected_physical_endpoint_claimed"],
        "payload_hash": packet["exact_payload_sha256"] == expected_payload,
    }
    summary = {
        "passed": sum(bool(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    if not summary["all_passed"]:
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"CBF.T57 independent verification failed: {failed}")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
