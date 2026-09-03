#!/usr/bin/env python3
"""Independently verify CBF.T71 by stacked-map rank identities."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import build_q79_eta9_graph_tangent_single_fiber_rank as t70


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_eta9_graph_tangent_multifiber_observability.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def verify_binding(binding: dict[str, Any]) -> Path:
    path = ROOT / binding["path"]
    require(path.is_file(), f"bound file: {path}")
    require(path.stat().st_size == binding["bytes"], f"bound bytes: {path}")
    require(sha256(path) == binding["sha256"], f"bound hash: {path}")
    return path


def quotient_operator(member: np.ndarray, weights: tuple[int, int, int]) -> np.ndarray:
    relation = sum(
        weights[block] * member[83 * block : 83 * (block + 1)]
        for block in range(3)
    ) % t70.P
    pivot = int(np.flatnonzero(np.any(relation != 0, axis=1))[0])
    inverse = t70.field_inverse(relation[pivot])
    one = np.array([1, 0, 0, 0, 0, 0], dtype=np.int64)
    rows = []
    for coordinate in range(83):
        if coordinate == pivot:
            continue
        fiber_row = np.zeros((83, t70.DEGREE), dtype=np.int64)
        fiber_row[coordinate] = one
        fiber_row[pivot] = (-t70.field_mul(relation[coordinate], inverse)) % t70.P
        surface_row = np.zeros((249, t70.DEGREE), dtype=np.int64)
        for block, weight in enumerate(weights):
            surface_row[83 * block : 83 * (block + 1)] = weight * fiber_row % t70.P
        rows.append(surface_row)
    return np.stack(rows)


def determinant3(matrix: list[tuple[int, int, int]]) -> int:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    ) % t70.P


def main() -> int:
    packet = load(PACKET)
    require(
        packet["schema"] == "mtt.cbf.q79-eta9-graph-tangent-multifiber-observability.v1",
        "schema",
    )
    claimed = packet["canonical_payload_sha256"]
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_sha256(unsigned) == claimed, "canonical packet hash")
    source = load(verify_binding(packet["inputs"]["source_snapshot"]))
    t70_packet = load(verify_binding(packet["inputs"]["CBF_T70"]))
    g3ad = load(verify_binding(packet["inputs"]["UST_G3AD"]))
    verify_binding(packet["inputs"]["UST_G3AK_packet"])
    matrix_path = verify_binding(packet["inputs"]["UST_G3AK_matrix"])
    verify_binding(packet["inputs"]["T70_builder_backend"])
    require(t70_packet["theorem_id"] == "CBF.T70", "T70 theorem")

    points = {
        name: tuple(int(value) for value in values)
        for name, values in source["evaluation_points_mod101"].items()
    }
    require(determinant3([points["e0"], points["e1"], points["e3"]]) == 77, "independent determinant")
    require(determinant3([points["e0"], points["e1"], points["e2"]]) == 0, "dependent determinant")
    incidence = np.frombuffer(matrix_path.read_bytes(), dtype=np.uint8).reshape(
        168, 249, t70.DEGREE
    )
    member = t70.selected_member(g3ad)
    operators = {name: quotient_operator(member, point) for name, point in points.items()}
    incidence_rank, _ = t70.rank(incidence)
    require(incidence_rank == 126, "incidence rank")

    def restricted_rank(*names: str) -> int:
        stacked = np.concatenate([incidence] + [operators[name] for name in names])
        return t70.rank(stacked)[0] - incidence_rank

    require(restricted_rank("e0") == 70, "e0 rank")
    require(restricted_rank("e2") == 68, "e2 rank")
    require(restricted_rank("e0", "e1") == 111, "representative pair rank")
    require(restricted_rank("e0", "e1", "e2") == 111, "dependent triple rank")
    require(restricted_rank("e0", "e1", "e3") == 122, "independent triple rank")

    panel = packet["rank_panel"]
    require(set(panel["all_pair_image_ranks"].values()) == {111}, "stored pair ranks")
    require(
        set(panel["all_pair_image_ranks"])
        == {"+".join(names) for names in itertools.combinations(points, 2)},
        "stored pair set",
    )
    independent = panel["independent_triple"]
    require(
        independent["image_rank"] == 122
        and independent["affine_common_kernel_rank"] == 1
        and independent["projective_kernel_rank"] == 0
        and independent["projectively_injective"],
        "independent triple decision",
    )
    require(packet["all_checks_pass"] and all(packet["checks"].values()), "checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    print(
        "CBF.T71 verification: PASS "
        "single=70/68 pair=111 dependent-triple=111 independent-triple=122"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
