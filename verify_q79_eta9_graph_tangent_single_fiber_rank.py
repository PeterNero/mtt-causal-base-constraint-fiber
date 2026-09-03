#!/usr/bin/env python3
"""Independently verify CBF.T70 through a kernel-first calculation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_eta9_graph_tangent_single_fiber_rank.packet.json"
P = 101
D = 6
REL = np.array([64, 16, 33, 44, 89, 24, 1], dtype=np.int64)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def verify_binding(binding: dict[str, Any]) -> Path:
    path = ROOT / binding["path"]
    require(path.is_file(), f"bound file: {path}")
    require(path.stat().st_size == binding["bytes"], f"bound bytes: {path}")
    require(sha256(path) == binding["sha256"], f"bound hash: {path}")
    return path


def mul(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    shape = np.broadcast_shapes(left.shape[:-1], right.shape[:-1])
    a = np.broadcast_to(left, shape + (D,))
    b = np.broadcast_to(right, shape + (D,))
    work = np.zeros(shape + (11,), dtype=np.int64)
    for total in range(11):
        for i in range(max(0, total - 5), min(5, total) + 1):
            work[..., total] += a[..., i] * b[..., total - i]
    work %= P
    for exponent in range(10, 5, -1):
        coefficient = work[..., exponent].copy()
        for j in range(6):
            work[..., exponent - 6 + j] -= coefficient * REL[j]
        work %= P
    return work[..., :6]


def power(value: np.ndarray, exponent: int) -> np.ndarray:
    result = np.array([1, 0, 0, 0, 0, 0], dtype=np.int64)
    factor = value.copy()
    while exponent:
        if exponent % 2:
            result = mul(result, factor)
        factor = mul(factor, factor)
        exponent //= 2
    return result


def inverse(value: np.ndarray) -> np.ndarray:
    require(bool(np.any(value)), "inverse of nonzero element")
    result = power(value, P**D - 2)
    require(np.array_equal(mul(value, result), [1, 0, 0, 0, 0, 0]), "inverse")
    return result


def rref(matrix: np.ndarray) -> tuple[np.ndarray, list[int]]:
    work = matrix.astype(np.int64, copy=True) % P
    rows, columns, width = work.shape
    require(width == D, "field width")
    pivot_row = 0
    pivots: list[int] = []
    for column in range(columns):
        candidates = np.flatnonzero(np.any(work[pivot_row:, column, :] != 0, axis=1))
        if not len(candidates):
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected]] = work[[selected, pivot_row]]
        work[pivot_row] = mul(work[pivot_row], inverse(work[pivot_row, column]))
        factors = work[:, column, :].copy()
        factors[pivot_row] = 0
        work = (work - mul(factors[:, None, :], work[pivot_row][None, :, :])) % P
        pivots.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    return work, pivots


def monomials(degree: int) -> list[tuple[int, int, int]]:
    return [
        (x, y, degree - x - y)
        for x in range(degree, -1, -1)
        for y in range(degree - x, -1, -1)
    ]


def lookup() -> dict[tuple[int, str, tuple[int, int, int]], int]:
    result = {}
    index = 0
    for coordinate in range(3):
        for kind, degree in (("base_degree9", 9), ("K3_sheet_times_degree6", 6)):
            for powers_xyz in monomials(degree):
                result[(coordinate, kind, powers_xyz)] = index
                index += 1
    require(index == 249, "basis size")
    return result


def member_from_packet(g3ad: dict[str, Any]) -> np.ndarray:
    result = np.zeros((249, D), dtype=np.int64)
    indices = lookup()
    for row in g3ad["fixed_FQ"]["nonzero_gamma_rows"]:
        key = (
            int(row["target_coordinate"]),
            str(row["basis_kind"]),
            tuple(int(value) for value in row["powers_xyz"]),
        )
        result[indices[key]] = row["gamma_coefficients_ascending"]
    return result % P


def quotient_values(vectors: np.ndarray, relation: np.ndarray, pivot: int) -> np.ndarray:
    evaluated = (vectors[:, :83, :] - vectors[:, 166:, :]) % P
    inv_pivot = inverse(relation[pivot])
    coordinates = []
    for index in range(83):
        if index == pivot:
            continue
        ratio = mul(relation[index], inv_pivot)
        coordinates.append((evaluated[:, index] - mul(evaluated[:, pivot], ratio)) % P)
    return np.stack(coordinates, axis=1)


def principal_vectors(g3ak: dict[str, Any]) -> np.ndarray:
    indices = lookup()
    union = {
        tuple(row["powers_xyz"]): np.array(row["gamma_coefficients"], dtype=np.int64)
        for row in g3ak["selected_graph_union"]["union_terms"]
    }
    result = []
    for coordinate in range(3):
        for cubic in monomials(3):
            vector = np.zeros((249, D), dtype=np.int64)
            for exponent, coefficient in union.items():
                out = tuple(a + b for a, b in zip(exponent, cubic))
                vector[indices[(coordinate, "base_degree9", out)]] = coefficient
            result.append(vector)
        vector = np.zeros((249, D), dtype=np.int64)
        for exponent, coefficient in union.items():
            vector[indices[(coordinate, "K3_sheet_times_degree6", exponent)]] = coefficient
        result.append(vector)
    return np.stack(result) % P


def main() -> int:
    packet = load(PACKET)
    require(packet["schema"] == "mtt.cbf.q79-eta9-graph-tangent-single-fiber-rank.v1", "schema")
    claimed = packet["canonical_payload_sha256"]
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_hash(unsigned) == claimed, "canonical packet hash")

    g3ad = load(verify_binding(packet["inputs"]["UST_G3AD"]))
    g3ak = load(verify_binding(packet["inputs"]["UST_G3AK_packet"]))
    matrix_path = verify_binding(packet["inputs"]["UST_G3AK_matrix"])
    h133 = load(verify_binding(packet["inputs"]["H4_T133"]))
    require(h133["fiber_evaluation_operator"]["kernel_rank"] == 166, "H4-T133")

    incidence = np.frombuffer(matrix_path.read_bytes(), dtype=np.uint8).reshape(168, 249, D)
    reduced, pivots = rref(incidence)
    require(len(pivots) == 126, "incidence rank")
    require(pivots == g3ak["incidence_certificate"]["pivot_columns_zero_based"], "pivots")
    free = [column for column in range(249) if column not in set(pivots)]
    kernel = np.zeros((len(free), 249, D), dtype=np.int64)
    one = np.array([1, 0, 0, 0, 0, 0], dtype=np.int64)
    for basis_index, free_column in enumerate(free):
        kernel[basis_index, free_column] = one
        for row, pivot_column in enumerate(pivots):
            kernel[basis_index, pivot_column] = (-reduced[row, free_column]) % P
    require(
        canonical_hash(kernel.tolist())
        == g3ak["incidence_certificate"]["canonical_kernel_basis_sha256"],
        "canonical kernel basis",
    )

    member = member_from_packet(g3ad)
    relation = (member[:83] - member[166:]) % P
    relation_pivot = int(np.flatnonzero(np.any(relation != 0, axis=1))[0])
    evaluated_kernel = quotient_values(kernel, relation, relation_pivot)
    _, image_pivots = rref(evaluated_kernel)
    principal = principal_vectors(g3ak)
    evaluated_principal = quotient_values(principal, relation, relation_pivot)
    _, principal_pivots = rref(evaluated_principal)

    ranks = packet["rank_calculation"]
    require(len(image_pivots) == ranks["restriction_image_on_graph_kernel_rank"] == 70, "image rank")
    require(len(principal_pivots) == ranks["principal33_slice_image_rank"] == 11, "principal rank")
    require(123 - len(image_pivots) == ranks["affine_invisible_kernel_rank"] == 53, "affine kernel")
    require(122 - len(image_pivots) == ranks["projective_invisible_tangent_rank"] == 52, "projective kernel")
    require(82 - len(image_pivots) == ranks["fixed_fiber_cokernel_rank"] == 12, "cokernel")
    require(packet["all_checks_pass"] and all(packet["checks"].values()), "checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    print(
        "CBF.T70 verification: PASS "
        "projective=122 image=70 invisible=52 cokernel=12 principal-image=11"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
