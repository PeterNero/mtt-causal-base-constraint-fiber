#!/usr/bin/env python3
"""Independently verify the exact CBF.T59 compiler packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import verify_full_graded_augmented_heterotic_symbol_parametrix as prior


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler.packet.json"
SOURCE_LOCK = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler_source_lock.json"
SCHEMA = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler_contract.schema.json"
THETA = Fraction(1, 3)
DEGREES = [-1, 0, 1, 2, 3]
Polynomial = tuple[Fraction, ...]
PolyMatrix = list[list[Polynomial]]
PolyVector = list[Polynomial]
Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def trim(entries: list[Fraction] | tuple[Fraction, ...]) -> Polynomial:
    result = list(entries)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result or [Fraction(0)])


def pc(value: Fraction | int) -> Polynomial:
    return (Fraction(value),)


def pa(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    return trim([
        (left[index] if index < len(left) else 0) + (right[index] if index < len(right) else 0)
        for index in range(size)
    ])


def pn(value: Polynomial) -> Polynomial:
    return tuple(-entry for entry in value)


def ps(left: Polynomial, right: Polynomial) -> Polynomial:
    return pa(left, pn(right))


def pm(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return trim(result)


def pd(value: Polynomial) -> Polynomial:
    return pc(0) if len(value) == 1 else trim([index * value[index] for index in range(1, len(value))])


def pzero(rows: int, columns: int) -> PolyMatrix:
    return [[pc(0) for _ in range(columns)] for _ in range(rows)]


def pt(matrix: PolyMatrix) -> PolyMatrix:
    return [list(row) for row in zip(*matrix)]


def pma(left: PolyMatrix, right: PolyMatrix) -> PolyMatrix:
    return [[pa(a, b) for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def pmn(matrix: PolyMatrix) -> PolyMatrix:
    return [[pn(entry) for entry in row] for row in matrix]


def pmm(left: PolyMatrix, right: PolyMatrix) -> PolyMatrix:
    rows = len(left)
    inner = len(left[0]) if left else 0
    columns = len(right[0]) if right else 0
    if inner != len(right):
        raise ValueError("polynomial matrix shape mismatch")
    result = pzero(rows, columns)
    for row in range(rows):
        for column in range(columns):
            for index in range(inner):
                result[row][column] = pa(result[row][column], pm(left[row][index], right[index][column]))
    return result


def pmd(matrix: PolyMatrix) -> PolyMatrix:
    return [[pd(entry) for entry in row] for row in matrix]


def pmsc(matrix: PolyMatrix, scalar: Polynomial) -> PolyMatrix:
    return [[pm(scalar, entry) for entry in row] for row in matrix]


def pmv(matrix: PolyMatrix, vector: PolyVector) -> PolyVector:
    result = []
    for row in matrix:
        total = pc(0)
        for entry, value in zip(row, vector):
            total = pa(total, pm(entry, value))
        result.append(total)
    return result


def pva(left: PolyVector, right: PolyVector) -> PolyVector:
    return [pa(a, b) for a, b in zip(left, right)]


def pvn(vector: PolyVector) -> PolyVector:
    return [pn(entry) for entry in vector]


def pvd(vector: PolyVector) -> PolyVector:
    return [pd(entry) for entry in vector]


def pvscale(vector: PolyVector, scalar: Polynomial) -> PolyVector:
    return [pm(scalar, entry) for entry in vector]


def serialized(matrix: PolyMatrix) -> list[list[list[str]]]:
    return [[[str(coefficient) for coefficient in entry] for entry in row] for row in matrix]


def phash(matrix: PolyMatrix) -> str:
    return canonical_hash(serialized(matrix))


def base_map(degree: int) -> Matrix:
    beta = [(Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))]
    symbol = prior.graded_symbol(beta, beta, degree)
    if any(imaginary != 0 for row in symbol for _, imaginary in row):
        raise ValueError("independent real symbol has an imaginary entry")
    return [[real for real, _ in row] for row in symbol]


def polynomial_map(degree: int) -> tuple[PolyMatrix, PolyMatrix]:
    raw = [[pc(entry) for entry in row] for row in base_map(degree)]
    g = (Fraction(1), Fraction(degree + 3, 20))
    f = (Fraction(degree + 4, 7), Fraction(degree + 5, 11))
    return pmsc(raw, g), pmsc(raw, f)


def adjoint_zero(a: PolyMatrix, b: PolyMatrix) -> PolyMatrix:
    at = pt(a)
    return pma(pma(pt(b), pmn(pmd(at))), pmn(pmsc(at, pc(THETA))))


def apply_l(a: PolyMatrix, b: PolyMatrix, vector: PolyVector) -> PolyVector:
    return pva(pmv(a, pvd(vector)), pmv(b, vector))


def apply_lstar(a: PolyMatrix, b: PolyMatrix, vector: PolyVector) -> PolyVector:
    return pva(pvn(pmv(pt(a), pvd(vector))), pmv(adjoint_zero(a, b), vector))


def direct_hodge(
    vector: PolyVector,
    outgoing: tuple[PolyMatrix, PolyMatrix] | None,
    incoming: tuple[PolyMatrix, PolyMatrix] | None,
) -> PolyVector:
    result = [pc(0) for _ in vector]
    if outgoing is not None:
        result = pva(result, apply_lstar(*outgoing, apply_l(*outgoing, vector)))
    if incoming is not None:
        result = pva(result, apply_l(*incoming, apply_lstar(*incoming, vector)))
    return result


def basis_vector(dimension: int, column: int, polynomial: Polynomial) -> PolyVector:
    result = [pc(0) for _ in range(dimension)]
    result[column] = polynomial
    return result


def matrices_from_direct_action(
    dimension: int,
    outgoing: tuple[PolyMatrix, PolyMatrix] | None,
    incoming: tuple[PolyMatrix, PolyMatrix] | None,
) -> tuple[PolyMatrix, PolyMatrix, PolyMatrix]:
    c = pzero(dimension, dimension)
    r = pzero(dimension, dimension)
    e = pzero(dimension, dimension)
    x = (Fraction(0), Fraction(1))
    half_x2 = (Fraction(0), Fraction(0), Fraction(1, 2))
    for column in range(dimension):
        e_column = direct_hodge(basis_vector(dimension, column, pc(1)), outgoing, incoming)
        x_result = direct_hodge(basis_vector(dimension, column, x), outgoing, incoming)
        r_column = [ps(value, pm(x, e_value)) for value, e_value in zip(x_result, e_column)]
        x2_result = direct_hodge(basis_vector(dimension, column, half_x2), outgoing, incoming)
        c_column = [
            pn(ps(ps(value, pm(x, r_value)), pm(half_x2, e_value)))
            for value, r_value, e_value in zip(x2_result, r_column, e_column)
        ]
        for row in range(dimension):
            e[row][column] = e_column[row]
            r[row][column] = r_column[row]
            c[row][column] = c_column[row]
    return c, r, e


def mz(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def mi(size: int) -> Matrix:
    result = mz(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def mt(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def ma(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def mn(matrix: Matrix) -> Matrix:
    return [[-entry for entry in row] for row in matrix]


def ms(left: Matrix, right: Matrix) -> Matrix:
    return ma(left, mn(right))


def mm(left: Matrix, right: Matrix) -> Matrix:
    return [[sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in zip(*right)] for row in left]


def msc(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * entry for entry in row] for row in matrix]


def diag(values: list[Fraction]) -> Matrix:
    result = mz(len(values), len(values))
    for index, value in enumerate(values):
        result[index][index] = value
    return result


def outer(left: list[Fraction], right: list[Fraction]) -> Matrix:
    return [[a * b for b in right] for a in left]


def inv(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + identity[:] for row, identity in zip(matrix, mi(size))]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column] != 0)
        work[column], work[pivot] = work[pivot], work[column]
        value = work[column][column]
        work[column] = [entry / value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [entry - factor * pivot_entry for entry, pivot_entry in zip(work[row], work[column])]
    return [row[size:] for row in work]


def power(matrix: Matrix, exponent: int) -> Matrix:
    result = mi(len(matrix))
    for _ in range(exponent):
        result = mm(result, matrix)
    return result


def block(a: Matrix, b: Matrix, c: Matrix, d: Matrix) -> Matrix:
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def mh(matrix: Matrix) -> str:
    return canonical_hash([[str(entry) for entry in row] for row in matrix])


def independent_neumann(packet: dict[str, Any]) -> list[bool]:
    h0_half = diag([Fraction(1), Fraction(2), Fraction(3), Fraction(4)])
    h0 = mm(h0_half, h0_half)
    h0_inv_half = diag([Fraction(1), Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)])
    v = [Fraction(3, 5), Fraction(4, 5), 0, 0]
    p = outer(v, v)
    eta = Fraction(1, 3)
    s = msc(p, eta)
    h = ma(h0, mm(mm(h0_half, s), h0_half))
    h_inv = inv(h)
    series = mz(4, 4)
    for exponent in range(5):
        series = ma(series, msc(power(s, exponent), Fraction(-1) ** exponent))
    approximation = mm(mm(h0_inv_half, series), h0_inv_half)
    error = ms(h_inv, approximation)
    row = packet["projected_neumann_inverse_certificate"]
    return [
        mh(h0) == row["H0_sha256"],
        mh(s) == row["relative_perturbation_sha256"],
        mh(h) == row["H_sha256"],
        mh(h_inv) == row["exact_inverse_sha256"],
        mh(approximation) == row["neumann_approximation_sha256"],
        mh(error) == row["error_sha256"],
        Fraction(row["actual_error_operator_norm"]) == Fraction(13, 8100),
        Fraction(row["certified_error_bound"]) == Fraction(1, 162),
        Fraction(row["actual_error_operator_norm"]) < Fraction(row["certified_error_bound"]),
        mm(h, h_inv) == mi(4),
    ]


def independent_feshbach(packet: dict[str, Any]) -> list[bool]:
    a = [[Fraction(2), Fraction(1, 5)], [Fraction(1, 5), Fraction(3)]]
    b = [[Fraction(1, 3), Fraction(1, 7)], [Fraction(1, 5), Fraction(1, 4)]]
    d = [[Fraction(5), Fraction(1, 4)], [Fraction(1, 4), Fraction(6)]]
    di = inv(d)
    f = ms(a, mm(mm(b, di), mt(b)))
    fi = inv(f)
    full = block(a, b, mt(b), d)
    full_inv = inv(full)
    delta = block([[Fraction(0)]], mz(1, 4), mz(4, 1), full)
    green = block([[Fraction(0)]], mz(1, 4), mz(4, 1), full_inv)
    projector = diag([Fraction(1), 0, 0, 0, 0])
    complement = ms(mi(5), projector)
    row = packet["feshbach_tail_certificate"]
    bf2 = sum((entry * entry for source_row in b for entry in source_row), Fraction(0))
    lower = Fraction(9, 5) - bf2 / Fraction(19, 4)
    return [
        Fraction(row["tail_gap_gershgorin"]) == Fraction(19, 4),
        Fraction(row["main_gap_gershgorin"]) == Fraction(9, 5),
        Fraction(row["coupling_frobenius_sq"]) == bf2,
        Fraction(row["schur_lower_bound"]) == lower and lower > 0,
        mh(full) == row["full_operator_sha256"],
        mh(di) == row["tail_inverse_sha256"],
        mh(f) == row["feshbach_operator_sha256"],
        mh(fi) == row["feshbach_inverse_sha256"],
        mh(full_inv) == row["full_inverse_sha256"],
        mh(delta) == row["kernel_extended_delta_sha256"],
        mh(projector) == row["kernel_projector_sha256"],
        mh(green) == row["reduced_green_sha256"],
        mm(delta, green) == complement,
        mm(green, delta) == complement,
        mm(projector, green) == mz(5, 5),
        mm(green, projector) == mz(5, 5),
    ]


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    source_matches = [sha256(ROOT / source["path"]) == source["sha256"] for source in lock["sources"]]
    maps = {degree: polynomial_map(degree) for degree in [-1, 0, 1, 2]}
    independent_rows = []
    cochain_checks = []
    for degree in [-1, 0, 1]:
        dimension = prior.dimension(4, degree)
        vector = [
            (Fraction(index + 1), Fraction(index + 2), Fraction(index + 3))
            for index in range(dimension)
        ]
        composed = apply_l(*maps[degree + 1], apply_l(*maps[degree], vector))
        cochain_checks.append(all(entry == pc(0) for entry in composed))
    for degree in DEGREES:
        dimension = prior.dimension(4, degree)
        c, r, e = matrices_from_direct_action(dimension, maps.get(degree), maps.get(degree - 1))
        declared = packet["five_degree_exact_witness"]["degree_rows"][degree + 1]
        independent_rows.append(
            {
                "degree": degree,
                "carrier_dimension": dimension,
                "correction_rank": prior.shifted_rank(degree),
                "C_sha256": phash(c),
                "R_sha256": phash(r),
                "E_sha256": phash(e),
                "matches": phash(c) == declared["C_sha256"] and phash(r) == declared["R_sha256"] and phash(e) == declared["E_sha256"],
            }
        )
    neumann_checks = independent_neumann(packet)
    feshbach_checks = independent_feshbach(packet)
    contract = packet["q79_execution_contract_update"]
    boundary = packet["physical_boundary"]
    ledger = packet["parameter_ledger"]
    expected_payload = canonical_hash(
        {
            "compiler": packet["coefficient_compiler_theorem"],
            "witness": packet["five_degree_exact_witness"],
            "neumann": packet["projected_neumann_inverse_certificate"],
            "feshbach": packet["feshbach_tail_certificate"],
            "contract": contract,
        }
    )
    checks = {
        "packet_schema": packet["schema"] == "boe.mtt.augmented-hodge-lower-order-inverse-tail-compiler.v1",
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": set(schema["required"]).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T59",
        "source_hashes_match": all(source_matches),
        "source_count": len(source_matches) == 4,
        "builder_passes": packet["check_summary"]["all_passed"],
        "builder_check_count": packet["check_summary"]["total"] == 30,
        "independent_cochain_checks": len(cochain_checks) == 3 and all(cochain_checks),
        "five_independent_degree_rows": len(independent_rows) == 5,
        "independent_degree_hashes_match": all(row["matches"] for row in independent_rows),
        "independent_dimensions": [row["carrier_dimension"] for row in independent_rows] == [1, 7, 15, 13, 4],
        "independent_ranks": [row["correction_rank"] for row in independent_rows] == [1, 4, 6, 4, 1],
        "neumann_replay": all(neumann_checks),
        "neumann_replay_count": len(neumann_checks) == 10,
        "feshbach_replay": all(feshbach_checks),
        "feshbach_replay_count": len(feshbach_checks) == 16,
        "payload_hash": expected_payload == packet["payload_sha256"],
        "coefficient_rows_zero": contract["independent_coefficient_entry_source_rows_after_endpoint"] == 0,
        "compiler_rows_closed": contract["local_lower_order_coefficient_compiler"] == "CLOSED_BY_CBF_T59" and contract["projected_global_inverse_acceptance_compiler"] == "CLOSED_BY_CBF_T59" and contract["Feshbach_tail_acceptance_compiler"] == "CLOSED_BY_CBF_T59",
        "selected_values_open": contract["selected_endpoint_coefficient_values"] == "OPEN",
        "selected_inverse_open": contract["selected_global_reduced_inverse"] == "OPEN",
        "selected_intertwiner_open": contract["selected_finite_continuum_intertwiner"] == "OPEN",
        "blockers_open": not contract["B_GEO_01_closed"] and not contract["B_OP_01_closed"],
        "no_parameters": ledger["continuous_physical_parameters_added"] == 0 and ledger["discrete_selectors_added"] == 0,
        "no_empirical_inputs": ledger["observed_values_used"] == 0 and ledger["fitted_values_used"] == 0,
        "physical_counters": boundary["physical_gates"] == {"accepted": 0, "total": 3} and boundary["physical_packets"] == {"accepted": 0, "total": 3} and boundary["physical_rows"] == {"accepted": 0, "total": 7},
    }
    result = {
        "all_passed": all(checks.values()),
        "passed": sum(checks.values()),
        "total": len(checks),
        "checks": checks,
        "independent_degree_rows": independent_rows,
    }
    print(json.dumps(result, sort_keys=True))
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
