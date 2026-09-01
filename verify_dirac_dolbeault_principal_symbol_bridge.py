#!/usr/bin/env python3
"""Independently verify the exact CBF.T56 packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "dirac_dolbeault_principal_symbol_bridge.packet.json"
SOURCE_LOCK = ROOT / "dirac_dolbeault_principal_symbol_source_lock.json"
SCHEMA = ROOT / "dirac_dolbeault_principal_symbol_contract.schema.json"
EVIDENCE = ROOT / "dirac_dolbeault_principal_symbol_external_evidence.audit.json"
N = 6
RANK = 8

RealMatrix = list[list[Fraction]]
Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = list[list[Gaussian]]
ZERO: Gaussian = (Fraction(0), Fraction(0))
ONE: Gaussian = (Fraction(1), Fraction(0))
I: Gaussian = (Fraction(0), Fraction(1))


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


def parse_gaussian(value: str) -> Gaussian:
    if not value.endswith("i"):
        return Fraction(value), Fraction(0)
    body = value[:-1]
    split = max(body.rfind("+", 1), body.rfind("-", 1))
    if split >= 0:
        real = Fraction(body[:split])
        imag_text = body[split:]
    else:
        real = Fraction(0)
        imag_text = body
    if imag_text in ("", "+"):
        imag = Fraction(1)
    elif imag_text == "-":
        imag = Fraction(-1)
    else:
        imag = Fraction(imag_text)
    return real, imag


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


def gaussian_matrix(matrix: list[list[str]]) -> GaussianMatrix:
    return [[parse_gaussian(entry) for entry in row] for row in matrix]


def gaussian_strings(matrix: GaussianMatrix) -> list[list[str]]:
    return [[gaussian_string(entry) for entry in row] for row in matrix]


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def gsum(values: Iterable[Gaussian]) -> Gaussian:
    result = ZERO
    for value in values:
        result = gadd(result, value)
    return result


def gzeros(rows: int, columns: int) -> GaussianMatrix:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def gidentity(size: int) -> GaussianMatrix:
    return [[ONE if row == column else ZERO for column in range(size)] for row in range(size)]


def gmatrix_add(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [[gadd(a, b) for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def gmatrix_scale(matrix: GaussianMatrix, scalar: Fraction | Gaussian) -> GaussianMatrix:
    factor = scalar if isinstance(scalar, tuple) else (scalar, Fraction(0))
    return [[gmul(factor, entry) for entry in row] for row in matrix]


def gmatmul(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [
        [gsum(gmul(a, b) for a, b in zip(left_row, right_column)) for right_column in transpose(right)]
        for left_row in left
    ]


def tensor(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    result = gzeros(len(left) * len(right), len(left[0]) * len(right[0]))
    for i, left_row in enumerate(left):
        for j, entry in enumerate(left_row):
            for k, right_row in enumerate(right):
                for ell, right_entry in enumerate(right_row):
                    result[i * len(right) + k][j * len(right[0]) + ell] = gmul(entry, right_entry)
    return result


def flat_gammas() -> list[GaussianMatrix]:
    i2 = gidentity(2)
    x = [[ZERO, ONE], [ONE, ZERO]]
    y = [[ZERO, (Fraction(0), Fraction(-1))], [I, ZERO]]
    z = [[ONE, ZERO], [ZERO, (Fraction(-1), Fraction(0))]]
    return [
        tensor(tensor(x, i2), i2),
        tensor(tensor(y, i2), i2),
        tensor(tensor(z, x), i2),
        tensor(tensor(z, y), i2),
        tensor(tensor(z, z), x),
        tensor(tensor(z, z), y),
    ]


def linear_combination(matrices: list[GaussianMatrix], coefficients: list[Fraction]) -> GaussianMatrix:
    result = gzeros(len(matrices[0]), len(matrices[0]))
    for matrix, coefficient in zip(matrices, coefficients):
        result = gmatrix_add(result, gmatrix_scale(matrix, coefficient))
    return result


def scalar_matrix(value: Fraction) -> GaussianMatrix:
    return gmatrix_scale(gidentity(RANK), value)


def quadratic(matrix: RealMatrix, vector: list[Fraction]) -> Fraction:
    return sum(
        (vector[row] * matrix[row][column] * vector[column] for row in range(N) for column in range(N)),
        Fraction(0),
    )


def exact_root(value: Fraction, degree: int) -> Fraction:
    def integer_root(number: int) -> int:
        for candidate in range(number + 1):
            if candidate**degree == number:
                return candidate
        raise ValueError("not an exact root")
    return Fraction(integer_root(value.numerator), integer_root(value.denominator))


def reconstruct_A(samples: list[dict[str, Any]]) -> RealMatrix:
    diagonal: dict[int, Fraction] = {}
    pairs: dict[tuple[int, int], Fraction] = {}
    for row in samples:
        value = Fraction(row["hessian_scalar"])
        if row["column"] is None:
            diagonal[int(row["row"])] = value
        else:
            pairs[(int(row["row"]), int(row["column"]))] = value
    result = zeros(N, N)
    for row, value in diagonal.items():
        result[row][row] = value
    for (row, column), value in pairs.items():
        result[row][column] = result[column][row] = (value - diagonal[row] - diagonal[column]) / 2
    return result


def exterior_basis() -> list[tuple[int, ...]]:
    return [tuple(indices) for degree in range(N + 1) for indices in itertools.combinations(range(1, N + 1), degree)]


def sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(int(sequence[left] > sequence[right]) for left in range(len(sequence)) for right in range(left + 1, len(sequence)))
    return -1 if inversions % 2 else 1


def minor(matrix: RealMatrix, rows: tuple[int, ...], columns: tuple[int, ...]) -> RealMatrix:
    return [[matrix[row - 1][column - 1] for column in columns] for row in rows]


def hodge(metric_inverse: RealMatrix, volume: Fraction) -> RealMatrix:
    basis = exterior_basis()
    lookup = {entry: index for index, entry in enumerate(basis)}
    result = zeros(64, 64)
    for column, source in enumerate(basis):
        for test in (entry for entry in basis if len(entry) == len(source)):
            target = tuple(index for index in range(1, N + 1) if index not in test)
            result[lookup[target]][column] += sign(test + target) * volume * determinant(minor(metric_inverse, test, source))
    return result


def main() -> None:
    packet = load_json(PACKET)
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    evidence = load_json(EVIDENCE)
    witness = packet["exact_six_dimensional_clifford_witness"]
    composition = packet["T55_composition"]

    source_matches = [sha256(ROOT / row["path"]) == row["sha256"] for row in lock["sources"]]
    coframe = fractions(witness["coframe"])
    H = fractions(witness["contravariant_metric_H"])
    G = fractions(witness["covariant_metric_G"])
    coframe_inverse_transpose = transpose(inverse(coframe))
    flat = flat_gammas()
    computed_gammas = [
        linear_combination(flat, [coframe_inverse_transpose[row][column] for row in range(N)])
        for column in range(N)
    ]
    packet_gammas = [gaussian_matrix(matrix) for matrix in witness["gamma_matrices"]]

    clifford_checks = []
    recovered_H = zeros(N, N)
    relation_rows = {(row["row"], row["column"]): row for row in witness["Clifford_relations"]}
    for row in range(N):
        for column in range(row, N):
            anticommutator = gmatrix_add(gmatmul(packet_gammas[row], packet_gammas[column]), gmatmul(packet_gammas[column], packet_gammas[row]))
            target = scalar_matrix(2 * H[row][column])
            clifford_checks.append(anticommutator == target)
            trace_value = gsum(anticommutator[index][index] for index in range(RANK))
            recovered_H[row][column] = recovered_H[column][row] = trace_value[0] / (2 * RANK)
            recorded = relation_rows[(row, column)]
            clifford_checks.append(canonical_hash(gaussian_strings(anticommutator)) == recorded["relation_sha256"])

    sample_checks = []
    for row in witness["principal_symbol_samples"]:
        vector = [Fraction(entry) for entry in row["covector"]]
        symbol = linear_combination(packet_gammas, vector)
        square = gmatmul(symbol, symbol)
        target = scalar_matrix(quadratic(H, vector))
        sample_checks.extend(
            [
                square == target,
                canonical_hash(gaussian_strings(square)) == row["Dirac_square_sha256"],
                Fraction(row["hessian_scalar"]) == Fraction(7) * quadratic(H, vector),
            ]
        )

    samples = witness["principal_symbol_samples"]
    A = reconstruct_A(samples)
    density = Fraction(composition["density_fixture"])
    action_scale = exact_root(density**2 * determinant(A), N)
    recovered_metric_inverse = scale(A, Fraction(1) / action_scale)
    recovered_metric = scale(inverse(A), action_scale)
    recovered_hodge = hodge(recovered_metric_inverse, density)

    potential = gmatrix_scale(gmatmul(packet_gammas[0], packet_gammas[1]), I)
    lower_rows = packet["lower_order_stability"]["rows"]
    lower_checks = []
    sample_by_label = {row["label"]: row for row in samples}
    for row in lower_rows:
        vector = [Fraction(entry) for entry in sample_by_label[row["label"]]["covector"]]
        symbol = linear_combination(packet_gammas, vector)
        t2 = gmatmul(symbol, symbol)
        t1 = gmatrix_add(gmatmul(symbol, potential), gmatmul(potential, symbol))
        t0 = gmatmul(potential, potential)
        lower_checks.extend(
            [
                t2 == scalar_matrix(quadratic(H, vector)),
                canonical_hash(gaussian_strings(t2)) == row["quadratic_sha256"],
                canonical_hash(gaussian_strings(t1)) == row["linear_coefficient_sha256"],
                canonical_hash(gaussian_strings(t0)) == row["constant_coefficient_sha256"],
            ]
        )

    expected_payload_hash = canonical_hash(
        {
            "Clifford_relations": witness["Clifford_relations"],
            "principal_symbol_samples": samples,
            "lower_order_rows": lower_rows,
            "T55_composition": composition,
            "evidence_sha256": sha256(EVIDENCE),
        }
    )
    boundary = packet["physical_boundary"]
    contract = packet["q79_source_contract_update"]
    ledger = packet["parameter_ledger"]
    checks = {
        "packet_schema": packet["schema"] == "boe.mtt.dirac-dolbeault-principal-symbol-bridge.v1",
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": set(schema["required"]).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T56",
        "source_hashes_match": all(source_matches),
        "source_check_count": len(source_matches) == 3,
        "builder_checks_pass": packet["check_summary"]["all_passed"],
        "builder_check_count": packet["check_summary"]["total"] == 46,
        "external_evidence_exact": packet["q79_evidence_audit"] == evidence,
        "external_evidence_is_nonpremise": evidence["role"] == "corroborating_evidence_not_a_premise_of_CBF_T56",
        "external_source_count": len(evidence["sources"]) == 3,
        "coframe_determinant": determinant(coframe) == 1,
        "coframe_nonorthogonal": matmul(transpose(coframe), coframe) != identity(N),
        "metric_from_coframe": matmul(transpose(coframe), coframe) == G,
        "metric_inverse": matmul(G, H) == identity(N),
        "inverse_transpose_coframe": strings(coframe_inverse_transpose) == witness["inverse_transpose_coframe"],
        "flat_gamma_count": len(flat) == N,
        "packet_gamma_count": len(packet_gammas) == N,
        "gamma_reconstruction": computed_gammas == packet_gammas,
        "Clifford_row_count": len(witness["Clifford_relations"]) == 21,
        "all_Clifford_checks": all(clifford_checks),
        "metric_from_anticommutators": recovered_H == H,
        "sample_count": len(samples) == 21,
        "all_sample_checks": all(sample_checks),
        "A_reconstruction": strings(A) == composition["action_quadratic_A"],
        "action_scale_reconstruction": action_scale == Fraction(7),
        "inverse_metric_reconstruction": recovered_metric_inverse == H,
        "metric_reconstruction": recovered_metric == G,
        "density_equation": determinant(G) == density**2,
        "Hodge_digest": canonical_hash(strings(recovered_hodge)) == composition["source_T55_Hodge_sha256"],
        "Hodge_composition_claim": composition["Hodge_reconstruction_matches_T55"],
        "lower_row_count": len(lower_rows) == 3,
        "all_lower_order_checks": all(lower_checks),
        "lower_order_claim": packet["lower_order_stability"]["all_quadratic_coefficients_unchanged"],
        "mixed_order_guard": packet["dirac_symbol_theorem"]["mixed_order_detour_requires_separate_gauge_fixing"],
        "scalarity_reduced": contract["independent_scalar_symbol_proof_after_selected_Dirac_source"] == 0,
        "metric_payload_reduced": contract["independent_metric_payload_after_selected_Dirac_source_and_density"] == 0,
        "physical_Dolbeault_source_open": contract["selected_physical_q79_Dolbeault_operator"] == "OPEN",
        "physical_density_open": contract["selected_physical_q79_density"] == "OPEN",
        "HYM_source_open": contract["selected_visible_hidden_HYM_connection"] == "OPEN",
        "no_parameters": ledger["continuous_physical_parameters_added"] == 0,
        "no_selectors": ledger["discrete_selectors_added"] == 0,
        "no_observed_values": ledger["observed_values_used"] == 0,
        "no_fits": ledger["fitted_values_used"] == 0,
        "B_GEO_open": not boundary["B_GEO_01_closed"],
        "B_ACTION_open": not boundary["B_ACTION_01_closed"],
        "B_OP_open": not boundary["B_OP_01_closed"],
        "physical_gates_unchanged": boundary["physical_gates"] == {"accepted": 0, "total": 3},
        "physical_packets_unchanged": boundary["physical_packets"] == {"accepted": 0, "total": 3},
        "physical_rows_unchanged": boundary["physical_rows"] == {"accepted": 0, "total": 7},
        "selected_operator_not_claimed": not boundary["selected_physical_operator_claimed"],
        "selected_density_not_claimed": not boundary["selected_physical_density_claimed"],
        "payload_hash": packet["exact_payload_sha256"] == expected_payload_hash,
    }
    summary = {
        "passed": sum(bool(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    if not summary["all_passed"]:
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"CBF.T56 independent verification failed: {failed}")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
