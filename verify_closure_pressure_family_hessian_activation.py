#!/usr/bin/env python3
"""Independent verifier for the closure-pressure activation packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "closure_pressure_family_hessian_activation.packet.json"
SOURCE_LOCK = ROOT / "closure_pressure_family_hessian_activation_source_lock.json"
SCHEMA = ROOT / "closure_pressure_family_hessian_activation_contract.schema.json"
THEOREM = ROOT / "ClosurePressureFamilyHessianActivationAndRegularMultiplierNoGoTheorem_v1.md"
T15_PACKET = ROOT / "direct_one_constraint_multiplier_source.packet.json"
FSB_ROOT = ROOT.parent / "mtt-q79-total-superconnection-branching" / "artifacts"
ALGEBRA_PACKET = FSB_ROOT / "triadic_family_response_algebra.packet.json"
MINIMALITY_PACKET = FSB_ROOT / "triadic_spectral_coordinate_minimality.packet.json"


K = tuple[Fraction, Fraction, Fraction, Fraction]
Matrix = list[list[K]]
Z: K = (Fraction(0), Fraction(0), Fraction(0), Fraction(0))
O: K = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(x: K, y: K) -> K:
    return tuple(a + b for a, b in zip(x, y))  # type: ignore[return-value]


def neg(x: K) -> K:
    return tuple(-a for a in x)  # type: ignore[return-value]


def sub(x: K, y: K) -> K:
    return add(x, neg(y))


def pair_mul(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return x[0] * y[0] + 3 * x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def mul(x: K, y: K) -> K:
    rr = pair_mul((x[0], x[1]), (y[0], y[1]))
    ii = pair_mul((x[2], x[3]), (y[2], y[3]))
    ri = pair_mul((x[0], x[1]), (y[2], y[3]))
    ir = pair_mul((x[2], x[3]), (y[0], y[1]))
    return rr[0] - ii[0], rr[1] - ii[1], ri[0] + ir[0], ri[1] + ir[1]


def conj(x: K) -> K:
    return x[0], x[1], -x[2], -x[3]


def inverse(x: K) -> K:
    norm = mul(x, conj(x))
    denominator = norm[0] * norm[0] - 3 * norm[1] * norm[1]
    if denominator == 0:
        raise ZeroDivisionError
    inverse_norm = (
        norm[0] / denominator,
        -norm[1] / denominator,
        Fraction(0),
        Fraction(0),
    )
    return mul(conj(x), inverse_norm)


def divide(x: K, y: K) -> K:
    return mul(x, inverse(y))


def scalar(value: int) -> K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def zero(rows: int, columns: int) -> Matrix:
    return [[Z for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [[O if row == column else Z for column in range(size)] for row in range(size)]


def diagonal(values: list[K]) -> Matrix:
    return [
        [values[row] if row == column else Z for column in range(len(values))]
        for row in range(len(values))
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def adjoint(matrix: Matrix) -> Matrix:
    return [[conj(value) for value in row] for row in transpose(matrix)]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [add(a, b) for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def matrix_scale(value: K, matrix: Matrix) -> Matrix:
    return [[mul(value, entry) for entry in row] for row in matrix]


def matrix_mul(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    result: Matrix = []
    for row in left:
        result_row: list[K] = []
        for column in columns:
            value = Z
            for a, b in zip(row, column):
                value = add(value, mul(a, b))
            result_row.append(value)
        result.append(result_row)
    return result


def blocks(tl: Matrix, tr: Matrix, bl: Matrix, br: Matrix) -> Matrix:
    return [a + b for a, b in zip(tl, tr)] + [a + b for a, b in zip(bl, br)]


def kron(left: Matrix, right: Matrix) -> Matrix:
    result: Matrix = []
    for left_row in left:
        for right_row in right:
            row: list[K] = []
            for left_value in left_row:
                row.extend(mul(left_value, right_value) for right_value in right_row)
            result.append(row)
    return result


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if row_count else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column] != Z),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [divide(value, pivot_value) for value in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            coefficient = work[row][column]
            if coefficient != Z:
                work[row] = [
                    sub(a, mul(coefficient, b))
                    for a, b in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def decode_matrix(payload: list[list[list[str]]]) -> Matrix:
    return [
        [tuple(Fraction(component) for component in value) for value in row]  # type: ignore[misc]
        for row in payload
    ]


def encode_matrix(matrix: Matrix) -> list[list[list[str]]]:
    return [[[str(component) for component in value] for value in row] for row in matrix]


def family_commutant_equations(a: Matrix, b: Matrix) -> Matrix:
    equations: Matrix = []
    for generator in (a, b):
        for row in range(3):
            for column in range(3):
                equation = [Z] * 9
                for k in range(3):
                    equation[row * 3 + k] = add(
                        equation[row * 3 + k], generator[k][column]
                    )
                    equation[k * 3 + column] = sub(
                        equation[k * 3 + column], generator[row][k]
                    )
                equations.append(equation)
    return equations


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    t15 = json.loads(T15_PACKET.read_text(encoding="utf-8"))
    algebra = json.loads(ALGEBRA_PACKET.read_text(encoding="utf-8"))
    minimality = json.loads(MINIMALITY_PACKET.read_text(encoding="utf-8"))
    checks = 0

    for entry in source_lock["local_sources"]:
        path = (ROOT / entry["path"]).resolve()
        require(path.is_file(), f"missing source: {entry['path']}")
        require(sha256(path) == entry["sha256"], f"source hash: {entry['path']}")
        checks += 1

    require(packet["schema"] == "boe.mtt.closure-pressure-family-hessian-activation.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T16", "claim id")
    checks += 1
    require(packet["decision"] == "PRESSURE_ACTIVATION_MECHANISM_CLOSED_PHYSICAL_ACTION_AND_VALUES_OPEN", "decision")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1

    require(schema["properties"]["regular_constraint"]["properties"]["normal_derivative"]["const"] == "I_H16", "regular contract")
    checks += 1
    require(schema["properties"]["pressure_load"]["properties"]["physical_scale_selected"]["const"] is False, "pressure boundary contract")
    checks += 1
    require(schema["properties"]["claim_boundary"]["properties"]["physical_Yukawa_values_derived"]["const"] is False, "Yukawa boundary contract")
    checks += 1

    a = [
        [scalar(-2), Z, scalar(-2)],
        [Z, scalar(-2), scalar(-2)],
        [scalar(-2), scalar(-2), Z],
    ]
    b = [
        [scalar(-4), Z, Z],
        [Z, Z, (Fraction(-1), Fraction(0), Fraction(0), Fraction(-1))],
        [Z, (Fraction(-1), Fraction(0), Fraction(0), Fraction(1)), Z],
    ]
    require(adjoint(a) == a and adjoint(b) == b, "Hermitian A/B")
    checks += 1
    require(rank(a) == 3 and rank(b) == 3, "simple response ranks")
    checks += 1
    require(matrix_mul(a, b) != matrix_mul(b, a), "response noncommutativity")
    checks += 1
    require(rank(family_commutant_equations(a, b)) == 8, "joint commutant rank")
    checks += 1
    require(packet["finite_instantiation"]["A_H_shift"] == encode_matrix(a), "A payload")
    checks += 1
    require(packet["finite_instantiation"]["B_H_phase"] == encode_matrix(b), "B payload")
    checks += 1

    phase = {6, 7, 8, 14}
    shift = {9, 10, 11, 15}
    inactive = set(range(16)) - phase - shift
    p_phase = diagonal([O if index in phase else Z for index in range(16)])
    p_shift = diagonal([O if index in shift else Z for index in range(16)])
    p_inactive = diagonal([O if index in inactive else Z for index in range(16)])
    h = matrix_add(kron(b, p_phase), kron(a, p_shift))
    require(adjoint(h) == h, "routed Hessian Hermitian")
    checks += 1
    require(rank(h) == 24, "routed Hessian rank")
    checks += 1
    require(matrix_mul(h, kron(identity(3), p_inactive)) == zero(48, 48), "inactive Q/L slots")
    checks += 1

    weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    y48 = kron(identity(3), diagonal([scalar(value) for value in weights]))
    require(matrix_mul(h, y48) == matrix_mul(y48, h), "shared-circle descent")
    checks += 1
    require(weights[15] == 0, "neutral normal line")
    checks += 1

    j = [[O if column == row else Z for column in range(64)] for row in range(16)]
    jt = adjoint(j)
    h_e = blocks(zero(16, 16), zero(16, 48), zero(48, 16), h)
    d0 = blocks(zero(64, 64), jt, j, zero(16, 16))
    d1 = blocks(h_e, jt, j, zero(16, 16))
    require(matrix_mul(j, jt) == identity(16), "regular coisometry")
    checks += 1
    require(rank(d0) == 32 and 80 - rank(d0) == 48, "zero-pressure bordered rank")
    checks += 1
    require(rank(d1) == 56 and 80 - rank(d1) == 24, "pressured bordered rank")
    checks += 1
    require([row[16:64] for row in d1[16:64]] == h, "tangent Hessian block")
    checks += 1
    require(
        matrix_add(d1, matrix_scale(scalar(-1), d0))
        == blocks(h_e, zero(64, 16), zero(16, 64), zero(16, 16)),
        "pressure-only Hessian delta",
    )
    checks += 1

    require(packet["general_theorem"]["pure_multiplier_critical_rule"] == "surjectivity forces lambda=0", "regular multiplier no-go payload")
    checks += 1
    require(packet["general_theorem"]["tangent_Hessian"] == "<u,H_p v>=p<n0,D2psi(0)[u,v]>", "pressure contraction payload")
    checks += 1
    require(packet["general_theorem"]["reduced_action"] == "S_red(k)=p<n0,psi(k)>", "reduced action payload")
    checks += 1

    symmetry = packet["symmetry_and_spectrum"]
    require(symmetry["joint_AB_commutant_dimension"] == 1, "family commutant payload")
    checks += 1
    require((symmetry["free_family_stabilizer_before"], symmetry["common_family_stabilizer_after"]) == ("U(3)", "U(1)"), "stabilizer reduction")
    checks += 1
    require(symmetry["complex_tangent_spectrum"] == {"+2": 8, "-2": 8, "-4": 8, "0": 24}, "tangent spectrum payload")
    checks += 1
    require(symmetry["nonzero_singular_magnitudes"] == {"2": 16, "4": 8}, "singular spectrum payload")
    checks += 1
    require(not symmetry["three_distinct_positive_family_magnitudes"], "magnitude no-go")
    checks += 1

    source_quartet = algebra["exact_witness"]["selected_eigenchannel_geometry"]["projector_quartet"]
    require(source_quartet == ["-1/8", "0", "0", "-1/24"], "source CP quartet")
    checks += 1
    require(symmetry["projector_quartet"] == source_quartet, "CP quartet transport")
    checks += 1
    require(not symmetry["physical_CKM_or_CP_identification"], "CP nonpromotion")
    checks += 1

    require(t15["externalization"]["free_associated_matter_source_subclause"] == "CLOSED_AT_CONDITIONAL_BENCHMARK_TIER", "T15 source tier")
    checks += 1
    require(minimality["exact_witness"]["source_value_boundary"]["strict_charged_magnitude_values_remaining"] == 9, "FSB04g value boundary")
    checks += 1
    require(packet["parameter_ledger"]["strict_charged_magnitude_values_remaining"] == 9, "packet value boundary")
    checks += 1
    require(packet["parameter_ledger"]["observed_construction_inputs"] == 0, "no observed source input")
    checks += 1
    require(packet["parameter_ledger"]["unselected_physical_pressure_or_scale"] == 1, "open pressure scale")
    checks += 1

    require(not packet["source_provenance"]["one_physical_root_for_both"], "same-root boundary")
    checks += 1
    require(packet["source_provenance"]["same_root_intertwiner_status"] == "OPEN", "intertwiner status")
    checks += 1
    require(not any(packet["claim_boundary"].values()), "all claim gates remain false")
    checks += 1
    require(not any(packet["physical_typing_boundary"].values()), "all physical typing gates remain false")
    checks += 1
    require((packet["physical_packets_accepted"], packet["physical_packets_total"]) == (0, 3), "packet acceptance")
    checks += 1
    require((packet["physical_rows_accepted"], packet["physical_rows_total"]) == (0, 7), "row acceptance")
    checks += 1
    require(all(packet["checks"].values()), "builder check record")
    checks += 1
    require(packet["check_summary"] == {"failed": [], "passed": 54, "total": 54}, "builder summary")
    checks += 1

    print(f"independent closure-pressure family-Hessian verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
