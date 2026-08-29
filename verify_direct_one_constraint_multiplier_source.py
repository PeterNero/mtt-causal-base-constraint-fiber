#!/usr/bin/env python3
"""Independent verifier for the one-constraint multiplier-source packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "direct_one_constraint_multiplier_source.packet.json"
SOURCE_LOCK = ROOT / "direct_one_constraint_multiplier_source_lock.json"
SCHEMA = ROOT / "direct_one_constraint_multiplier_source_contract.schema.json"
THEOREM = ROOT / "MinimalOneConstraintMultiplierSourceAndThreeFamilyIndexTheorem_v1.md"
T13_PACKET = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
T14_PACKET = ROOT / "provider_neutral_projection_source_quotient.packet.json"


Scalar = int | Fraction
Matrix = list[list[Scalar]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in columns]
        for row in left
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scale(value: Scalar, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def identity(size: int) -> Matrix:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def zero(rows: int, columns: int) -> Matrix:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def diagonal(values: list[Scalar]) -> Matrix:
    return [
        [values[row] if row == column else 0 for column in range(len(values))]
        for row in range(len(values))
    ]


def blocks(
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
            row: list[Scalar] = []
            for left_entry in left_row:
                row.extend(left_entry * right_entry for right_entry in right_row)
            result.append(row)
    return result


def matrix_rank(matrix: Matrix) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [entry / pivot_value for entry in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            coefficient = work[row][column]
            if coefficient:
                work[row] = [
                    a - coefficient * b for a, b in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def decode(value: int | list[int]) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value[0], value[1])


def make_j() -> Matrix:
    return [
        [int(row == column) if column < 16 else 0 for column in range(64)]
        for row in range(16)
    ]


def make_family_cycle() -> Matrix:
    permutation = list(range(64))
    for family in range(3):
        for coordinate in range(16):
            source = 16 + 16 * family + coordinate
            permutation[source] = 16 + 16 * ((family + 1) % 3) + coordinate
    result = zero(64, 64)
    for source, target in enumerate(permutation):
        result[target][source] = 1
    return result


def commutant_constraints() -> Matrix:
    equations: Matrix = []
    for i in range(3):
        for j in range(3):
            generator = zero(3, 3)
            generator[i][j] = 1
            for row in range(3):
                for column in range(3):
                    coefficients = [0] * 9
                    for k in range(3):
                        coefficients[row * 3 + k] += generator[k][column]
                        coefficients[k * 3 + column] -= generator[row][k]
                    equations.append(coefficients)
    return equations


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    t13 = json.loads(T13_PACKET.read_text(encoding="utf-8"))
    t14 = json.loads(T14_PACKET.read_text(encoding="utf-8"))
    checks = 0

    for entry in source_lock["local_sources"]:
        path = (ROOT / entry["path"]).resolve()
        require(path.is_file(), f"missing source: {entry['path']}")
        require(sha256(path) == entry["sha256"], f"source hash: {entry['path']}")
        checks += 1

    require(packet["schema"] == "boe.mtt.direct-one-constraint-multiplier-source.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T15", "claim id")
    checks += 1
    require(packet["decision"] == "MINIMAL_FREE_MATTER_DIRECT_SOURCE_CLASS_CLOSED_PHYSICAL_SOURCE_OPEN", "decision")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1

    source_properties = schema["properties"]["source"]["properties"]
    require(source_properties["source_multiplicity"]["const"] == 4, "source multiplicity contract")
    checks += 1
    require(source_properties["residual_multiplicity"]["const"] == 1, "residual multiplicity contract")
    checks += 1
    require(source_properties["one_family_dimension"]["const"] == 16, "one-family dimension contract")
    checks += 1
    require(schema["properties"]["claim_boundary"]["properties"]["physical_source_selected"]["const"] is False, "source nonpromotion contract")
    checks += 1

    multiplicities = packet["minimality_theorem"]["multiplicity_table"]
    require([row["source_multiplicity"] for row in multiplicities] == list(range(1, 7)), "multiplicity range")
    checks += 1
    for row in multiplicities:
        m = row["source_multiplicity"]
        require(row["source_dimension"] == 16 * m, f"source dimension m={m}")
        require(row["residual_dimension"] == 16, f"residual dimension m={m}")
        require(row["kernel_dimension"] == 16 * (m - 1), f"kernel dimension m={m}")
        require(row["family_copies_in_kernel"] == m - 1, f"family index m={m}")
        checks += 1
    require([row["source_multiplicity"] for row in multiplicities if row["family_copies_in_kernel"] == 3] == [4], "three-family iff m=4")
    checks += 1
    require(not packet["minimality_theorem"]["independent_prediction_of_four_copies"], "conditional direction")
    checks += 1

    j = make_j()
    jt = transpose(j)
    q = matmul(jt, j)
    p = add(identity(64), scale(-1, q))
    d = blocks(zero(64, 64), jt, j, zero(16, 16))
    d2 = matmul(d, d)

    require(matrix_rank(j) == 16, "J rank")
    checks += 1
    require(matmul(j, jt) == identity(16), "J coisometry")
    checks += 1
    require(matmul(q, q) == q and matrix_rank(q) == 16, "normal projector")
    checks += 1
    require(matmul(p, p) == p and matrix_rank(p) == 48, "coherent projector")
    checks += 1
    require(add(p, q) == identity(64) and matmul(p, q) == zero(64, 64), "projector splitting")
    checks += 1
    require(matmul(j, p) == zero(16, 64), "kernel projection")
    checks += 1
    require(transpose(d) == d, "signed Hessian symmetry")
    checks += 1
    require(d2 == blocks(q, zero(64, 16), zero(16, 64), identity(16)), "normal-square blocks")
    checks += 1
    require(matmul(d2, d) == d, "D cubed")
    checks += 1
    require(matrix_rank(d) == 32 and 80 - matrix_rank(d) == 48, "D rank/nullity")
    checks += 1
    require(sum(d[index][index] for index in range(80)) == 0, "D trace")
    checks += 1
    require(packet["actions"]["signed_spectrum"] == {"+1": 16, "-1": 16, "0": 48}, "signed spectrum payload")
    checks += 1

    frame = [[decode(value) for value in row] for row in packet["unitary_source_class"]["source_frame"]]
    spread_row = [[decode(value) for value in packet["unitary_source_class"]["nontrivial_covector"]]]
    source_frame = kron(frame, identity(16))
    spread = kron(spread_row, identity(16))
    require(matmul(source_frame, transpose(source_frame)) == identity(64), "source-frame unitarity")
    checks += 1
    require(matmul(spread, transpose(spread)) == identity(16), "spread coisometry")
    checks += 1
    require(matmul(spread, source_frame) == j, "unitary source equivalence")
    checks += 1
    require(packet["unitary_source_class"]["continuous_dimensionless_parameters_after_equivalence"] == 0, "unitary quotient parameter count")
    checks += 1

    r = Fraction(1, 2)
    s = Fraction(1, 3)
    t_r = add(p, scale(r, q))
    t_s = add(p, scale(s, q))
    t_rs = add(p, scale(r * s, q))
    require(matmul(t_r, t_s) == t_rs, "repair semigroup")
    checks += 1
    require(matmul(j, t_r) == scale(r, j), "residual contraction")
    checks += 1
    require(matmul(t_r, p) == p, "fixed coherent sector")
    checks += 1
    require(packet["repair_flow"]["sample_product"] == [1, 6], "formal flow payload")
    checks += 1

    cycle = make_family_cycle()
    cycle80 = blocks(cycle, zero(64, 16), zero(16, 64), identity(16))
    require(matmul(j, cycle) == j, "family cycle preserves J")
    checks += 1
    require(matmul(cycle, matmul(p, transpose(cycle))) == p, "family cycle preserves P")
    checks += 1
    require(matmul(cycle80, matmul(d, transpose(cycle80))) == d, "family cycle intertwines D")
    checks += 1

    weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    y16 = diagonal(weights)
    y64 = diagonal(weights * 4)
    y80 = blocks(y64, zero(64, 16), zero(16, 64), y16)
    require(matmul(j, y64) == matmul(y16, j), "shared-circle intertwiner")
    checks += 1
    require(matmul(d, y80) == matmul(y80, d), "shared-circle Hessian commutant")
    checks += 1
    require(packet["descent"]["shared_circle_weights_6Y"] == [1, -4, 2, -3, 6, 0], "shared-circle payload")
    checks += 1
    require(matrix_rank(commutant_constraints()) == 8, "U3 commutant codimension")
    checks += 1
    require(packet["descent"]["family_commutant_dimension"] == 1, "U3 no-go payload")
    checks += 1

    internal = t13["exact_internal_witness"]
    require((internal["plus_dimension"], internal["minus_dimension"], internal["self_adjoint_dimension"]) == (64, 16, 80), "T13 dimensions")
    checks += 1
    require((internal["kernel_dimension"], internal["cokernel_dimension"]) == (48, 0), "T13 index dimensions")
    checks += 1
    require(internal["nonzero_spectrum"] == [-1, 1] and internal["spectral_gap_mu"] == 1, "T13 spectrum")
    checks += 1
    require(internal["characterwise_index"] == "3[H16]", "T13 character index")
    checks += 1
    require(not t14["q79_classification"]["q79_required_by_projection_formulas"], "provider-neutral compatibility")
    checks += 1

    ledger = packet["parameter_ledger"]
    require(ledger["continuous_dimensionless_matrix_parameters_after_equivalence"] == 0, "dimensionless source knobs")
    checks += 1
    require(ledger["observed_values_used"] == 0 and ledger["postprojection_charge_choices"] == 0, "no replay inputs")
    checks += 1
    require(ledger["unselected_dimensionful_scales"] == 1, "open scale")
    checks += 1
    require(ledger["unselected_nonlinear_family_or_sector_values"] == 9, "open nonlinear values")
    checks += 1

    boundary = packet["claim_boundary"]
    require(not any(boundary.values()), "all promotion gates remain false")
    checks += 1
    require((packet["physical_packets_accepted"], packet["physical_packets_total"]) == (0, 3), "physical packet boundary")
    checks += 1
    require((packet["physical_rows_accepted"], packet["physical_rows_total"]) == (0, 7), "physical row boundary")
    checks += 1
    require(all(packet["checks"].values()), "builder check record")
    checks += 1
    require(packet["check_summary"] == {"failed": [], "passed": 57, "total": 57}, "builder summary")
    checks += 1

    print(f"independent one-constraint multiplier-source verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
