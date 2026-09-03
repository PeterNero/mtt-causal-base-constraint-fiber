#!/usr/bin/env python3
"""Independent replay of the CBF.T63 finite sequence and source cutset."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
PACKET = ROOT / "q79_eta9_graph_family_normal_value_map.packet.json"


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def repository_roots() -> dict[str, Path]:
    settings = {
        "mtt-unified-source-theorem": "MTT_UNIFIED_SOURCE_REPOSITORY",
        "mtt-preprojection-repair-calculus": "MTT_PREPROJECTION_REPOSITORY",
        "mtt-q79-total-superconnection-branching": "MTT_Q79_BRANCHING_REPOSITORY",
    }
    roots = {}
    for repository, environment in settings.items():
        configured = os.environ.get(environment)
        roots[repository] = (
            Path(configured).expanduser().resolve()
            if configured
            else COMMON / repository
        )
        require(roots[repository].is_dir(), f"repository {repository}")
    return roots


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_matrix(path: Path, shape: list[int], offset: int = 0) -> np.ndarray:
    count = 1
    for value in shape:
        count *= int(value)
    payload = path.read_bytes()
    require(offset + count <= len(payload), f"binary extent {path.name}")
    return np.frombuffer(
        payload, dtype=np.uint8, count=count, offset=offset
    ).astype(np.int64).reshape(tuple(int(value) for value in shape))


class ExtensionField:
    def __init__(self, prime: int, relation: list[int]) -> None:
        self.prime = int(prime)
        self.relation = tuple(int(value) % self.prime for value in relation)
        self.degree = len(self.relation) - 1
        require(self.relation[-1] == 1, "monic relation")

    def reduce(self, polynomial: np.ndarray) -> np.ndarray:
        work = np.asarray(polynomial, dtype=np.int64).copy() % self.prime
        for power in reversed(range(self.degree, work.shape[-1])):
            coefficient = work[..., power].copy()
            for target, relation_coefficient in enumerate(self.relation[:-1]):
                work[..., power - self.degree + target] = (
                    work[..., power - self.degree + target]
                    - coefficient * relation_coefficient
                ) % self.prime
            work[..., power] = 0
        return work[..., : self.degree]

    def multiply(self, left: np.ndarray, right: np.ndarray) -> np.ndarray:
        convolution = np.zeros(2 * self.degree - 1, dtype=np.int64)
        for total_degree in range(2 * self.degree - 1):
            convolution[total_degree] = sum(
                int(left[index]) * int(right[total_degree - index])
                for index in range(self.degree)
                if 0 <= total_degree - index < self.degree
            )
        return self.reduce(convolution)

    def exponentiate(self, value: np.ndarray, exponent: int) -> np.ndarray:
        answer = np.zeros(self.degree, dtype=np.int64)
        answer[0] = 1
        factor = np.asarray(value, dtype=np.int64) % self.prime
        while exponent > 0:
            if exponent % 2:
                answer = self.multiply(answer, factor)
            factor = self.multiply(factor, factor)
            exponent //= 2
        return answer

    def inverse(self, value: np.ndarray) -> np.ndarray:
        require(bool(np.any(value)), "nonzero pivot")
        inverse = self.exponentiate(value, self.prime**self.degree - 2)
        check = self.multiply(value, inverse)
        require(check[0] == 1 and not np.any(check[1:]), "inverse replay")
        return inverse

    def multiply_row(self, row: np.ndarray, scalar: np.ndarray) -> np.ndarray:
        convolution = np.zeros(
            (*row.shape[:-1], 2 * self.degree - 1), dtype=np.int64
        )
        for total_degree in range(2 * self.degree - 1):
            for index in range(self.degree):
                other = total_degree - index
                if 0 <= other < self.degree:
                    convolution[..., total_degree] += (
                        row[..., index] * int(scalar[other])
                    )
        return self.reduce(convolution)

    def product(self, left: np.ndarray, right: np.ndarray) -> np.ndarray:
        require(left.shape[1] == right.shape[0], "matrix product")
        convolution = np.zeros(
            (left.shape[0], right.shape[1], 2 * self.degree - 1),
            dtype=np.int64,
        )
        for total_degree in range(2 * self.degree - 1):
            for index in range(self.degree):
                other = total_degree - index
                if 0 <= other < self.degree:
                    convolution[..., total_degree] += (
                        left[..., index] @ right[..., other]
                    )
        return self.reduce(convolution)

    def rank(self, matrix: np.ndarray) -> tuple[int, list[int]]:
        work = np.asarray(matrix, dtype=np.int64).copy() % self.prime
        pivot_row = 0
        pivots: list[int] = []
        for column in range(work.shape[1]):
            selected = next(
                (
                    row
                    for row in range(pivot_row, work.shape[0])
                    if np.any(work[row, column, :])
                ),
                None,
            )
            if selected is None:
                continue
            if selected != pivot_row:
                temporary = work[pivot_row, :, :].copy()
                work[pivot_row, :, :] = work[selected, :, :]
                work[selected, :, :] = temporary
            reciprocal = self.inverse(work[pivot_row, column, :])
            work[pivot_row, column:, :] = self.multiply_row(
                work[pivot_row, column:, :], reciprocal
            )
            for row in range(pivot_row + 1, work.shape[0]):
                multiplier = work[row, column, :].copy()
                if np.any(multiplier):
                    work[row, column:, :] = (
                        work[row, column:, :]
                        - self.multiply_row(
                            work[pivot_row, column:, :], multiplier
                        )
                    ) % self.prime
            pivots.append(column)
            pivot_row += 1
            if pivot_row == work.shape[0]:
                break
        return pivot_row, pivots


def main() -> int:
    packet = load(PACKET)
    require(packet["schema"] == "mtt.cbf.q79-eta9-graph-family-normal-value-map.v1", "schema")
    require(packet["theorem_id"] == "CBF.T63", "theorem id")
    require(all(packet["checks"].values()), "packet checks")
    require(not any(packet["guardrails"].values()), "packet guardrails")

    roots = repository_roots()
    paths: dict[str, Path] = {}
    for name, row in packet["inputs"].items():
        require(row["repository"] in roots, f"input repository {name}")
        path = roots[row["repository"]] / row["path"]
        require(path.is_file(), f"input path {name}")
        require(path.stat().st_size == row["bytes"], f"input bytes {name}")
        require(digest(path) == row["sha256"], f"input hash {name}")
        paths[name] = path

    g3am = load(paths["UST_G3AM_packet"])
    g3an = load(paths["UST_G3AN_packet"])
    g3as = load(paths["UST_G3AS_packet"])
    pairing = load(paths["H4_pairing_kernel_packet"])
    t133 = load(paths["H4_T133_fiber_evaluation_packet"])
    t134 = load(paths["H4_T134_transport_packet"])
    t135 = load(paths["H4_T135_boundary_source_packet"])
    t136 = load(paths["H4_T136_Serre_lift_packet"])
    fsb = load(paths["FSB_03g_root_selection_packet"])

    field_data = packet["residue_field"]
    require(field_data == g3am["residue_field"] == g3an["residue_field"] == g3as["residue_field"], "field identity")
    field = ExtensionField(
        int(field_data["prime"]),
        [int(value) for value in field_data["gamma_relation_coefficients_ascending"]],
    )
    require(field.prime == 101 and field.degree == 6, "selected field")

    d0 = binary_matrix(paths["UST_G3AM_principal_response"], [248, 33, 6])
    d1_layout = g3an["full_response_schur"]["binary_artifact"]["layout"]["D1_extra_response"]
    d1 = binary_matrix(
        paths["UST_G3AN_binary_bundle"],
        d1_layout["shape"],
        int(d1_layout["byte_offset"]),
    )
    response = np.concatenate([d0, d1], axis=1)
    normal = binary_matrix(
        paths["UST_G3AS_normal_operator"], g3as["normal_operator"]["shape"]
    )
    intertwiner = binary_matrix(
        paths["H4_pairing_quotient_intertwiner"],
        pairing["quotient_intertwiner"]["shape"],
    )

    annihilator = field.product(normal, response)
    response_rank, response_pivots = field.rank(response)
    normal_rank, normal_pivots = field.rank(normal)
    intertwiner_rank, intertwiner_pivots = field.rank(intertwiner)
    finite = packet["finite_exact_sequence"]
    quotient = packet["graph_normal_duality"]
    require(not np.any(annihilator), "N D exact zero")
    require(response_rank == finite["response_rank"] == 122, "rank D")
    require(normal_rank == finite["normal_rank"] == 126, "rank N")
    require(intertwiner_rank == quotient["rank"] == 126, "rank B")
    require(response_pivots == finite["response_pivot_columns_zero_based"], "D pivots")
    require(normal_pivots == finite["normal_pivot_columns_zero_based"], "N pivots")
    require(intertwiner_pivots == quotient["pivot_columns_zero_based"], "B pivots")
    require(response_rank + normal_rank == 248, "exact middle dimension")
    require(finite["image_response_equals_kernel_normal"], "exact sequence claim")

    dimensions = t133["cohomology_dimensions"]
    require(dimensions["primitive_surface_rows"] == 248, "surface dimension")
    require(dimensions["fiber_holomorphic_rows"] == 82, "fiber dimension")
    require(dimensions["fixed_fiber_kernel_rank"] == 166, "restriction kernel")
    require(
        "the fixed-fiber solve alone rejects the candidate from U_eta9"
        in t133["scope_correction"]["withdrawn_as_unproved"],
        "fixed-fiber correction",
    )
    require(t134["state_correction"]["algebraic_de_Rham_transport_rank"] == 164, "de Rham rank")
    require(t134["state_correction"]["surface_accumulator_rank"] == 248, "BHT accumulator")
    require(len(t134["midpoint_backend_audit"]["rows"]) == 6, "transport samples")
    require(len(t135["sample_audit"]["rows"]) == 6, "source samples")
    require(len(t136["sample_audit"]["rows"]) == 6, "Serre samples")
    require(fsb["first_missing_leaf"]["id"] == "EA.03R", "root frontier")
    require(fsb["guardrails"]["claims_a_physical_root_is_emitted"] is False, "root remains open")

    cutset = packet["BHT_execution_cutset"]
    require(cutset["same_member_midpoint_transport_backends"]["accepted"] == 6, "transport count")
    require(cutset["same_member_midpoint_boundary_sources"]["accepted"] == 6, "source count")
    require(cutset["same_member_midpoint_projective_H01_lifts"]["accepted"] == 6, "lift count")
    require(cutset["panelwise_complete_rank164_action"]["accepted"] == 0, "panel frontier")
    require(packet["characteristic_zero_value_map"]["accepted_full_beta_rows"] == {"accepted": 0, "total": 248}, "beta rows")
    require(packet["frontier_delta"]["open_blockers"] == ["B.ETA9.01", "B.ETA9.02"], "blockers")
    print(
        "CBF.T63 independent replay: PASS "
        "rank(D)=122 rank(N)=126 im(D)=ker(N) fiber=82/248 beta=OPEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
