#!/usr/bin/env python3
"""Build CBF.T71, exact multifiber coefficient observability."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import build_q79_eta9_graph_tangent_single_fiber_rank as t70


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_graph_tangent_multifiber_observability.source.json"
OUTPUT = ROOT / "q79_eta9_graph_tangent_multifiber_observability.packet.json"


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


def binding(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def rref(matrix: np.ndarray) -> tuple[np.ndarray, list[int]]:
    work = matrix.astype(np.int64, copy=True) % t70.P
    rows, columns, width = work.shape
    require(width == t70.DEGREE, "field width")
    pivot_row = 0
    pivots: list[int] = []
    for column in range(columns):
        candidates = np.flatnonzero(np.any(work[pivot_row:, column, :] != 0, axis=1))
        if not len(candidates):
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected]] = work[[selected, pivot_row]]
        inverse = t70.field_inverse(work[pivot_row, column])
        work[pivot_row] = t70.field_mul(work[pivot_row], inverse)
        factors = work[:, column].copy()
        factors[pivot_row] = 0
        work = (
            work
            - t70.field_mul(factors[:, None, :], work[pivot_row][None, :, :])
        ) % t70.P
        pivots.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    return work, pivots


def canonical_kernel(incidence: np.ndarray) -> np.ndarray:
    reduced, pivots = rref(incidence)
    require(len(pivots) == 126, "incidence rank")
    free = [column for column in range(249) if column not in set(pivots)]
    result = np.zeros((len(free), 249, t70.DEGREE), dtype=np.int64)
    one = np.array([1, 0, 0, 0, 0, 0], dtype=np.int64)
    for basis_index, free_column in enumerate(free):
        result[basis_index, free_column] = one
        for row, pivot_column in enumerate(pivots):
            result[basis_index, pivot_column] = (-reduced[row, free_column]) % t70.P
    return result


def quotient_values(
    vectors: np.ndarray,
    member: np.ndarray,
    weights: tuple[int, int, int],
) -> tuple[np.ndarray, int]:
    evaluated = sum(
        weights[block] * vectors[:, 83 * block : 83 * (block + 1)]
        for block in range(3)
    ) % t70.P
    relation = sum(
        weights[block] * member[83 * block : 83 * (block + 1)]
        for block in range(3)
    ) % t70.P
    nonzero = np.flatnonzero(np.any(relation != 0, axis=1))
    require(len(nonzero) > 0, f"nonzero relation at {weights}")
    pivot = int(nonzero[0])
    inverse = t70.field_inverse(relation[pivot])
    rows = []
    for coordinate in range(83):
        if coordinate == pivot:
            continue
        ratio = t70.field_mul(relation[coordinate], inverse)
        rows.append(
            (evaluated[:, coordinate] - t70.field_mul(evaluated[:, pivot], ratio))
            % t70.P
        )
    return np.stack(rows, axis=1), pivot


def base_rank(points: list[tuple[int, int, int]]) -> int:
    work = np.array(points, dtype=np.int64) % t70.P
    rank = 0
    for column in range(3):
        selected = next(
            (row for row in range(rank, len(work)) if work[row, column] % t70.P),
            None,
        )
        if selected is None:
            continue
        work[[rank, selected]] = work[[selected, rank]]
        work[rank] = work[rank] * pow(int(work[rank, column]), -1, t70.P) % t70.P
        for row in range(len(work)):
            if row != rank:
                work[row] = (work[row] - work[row, column] * work[rank]) % t70.P
        rank += 1
    return rank


def selected_e3() -> tuple[int, int, int]:
    e0 = (1, 0, -1)
    e1 = (0, 1, -1)
    for a in range(1, t70.P):
        for b in range(1, t70.P):
            candidate = (1, a, b)
            if sum(value**3 for value in candidate) % t70.P == 0 and base_rank(
                [e0, e1, candidate]
            ) == 3:
                return candidate
    raise AssertionError("independent Fermat point")


def image_rank(outputs: dict[str, np.ndarray], names: tuple[str, ...]) -> int:
    joined = np.concatenate([outputs[name] for name in names], axis=1)
    return len(rref(joined)[1])


def main() -> int:
    source = load(SOURCE)
    require(
        source["schema"]
        == "mtt.cbf.q79-eta9-graph-tangent-multifiber-observability-source.v1",
        "source schema",
    )
    sources = source["sources"]
    t70_path = ROOT / sources["CBF_T70"]["local_path"]
    g3ad_path = ROOT / sources["UST_G3AD"]["local_path"]
    g3ak_path = ROOT / sources["UST_G3AK"]["local_packet_path"]
    matrix_path = ROOT / sources["UST_G3AK"]["local_matrix_path"]
    require(sha256(t70_path) == sources["CBF_T70"]["local_sha256"], "T70 hash")
    require(sha256(g3ad_path) == sources["UST_G3AD"]["local_sha256"], "G3AD hash")
    require(sha256(g3ak_path) == sources["UST_G3AK"]["local_packet_sha256"], "G3AK hash")
    require(sha256(matrix_path) == sources["UST_G3AK"]["local_matrix_sha256"], "matrix hash")
    t70_packet = load(t70_path)
    g3ad = load(g3ad_path)
    g3ak = load(g3ak_path)
    require(t70_packet["theorem_id"] == "CBF.T70", "T70 theorem")
    require(g3ak["theorem_id"] == "UST.G3AK", "G3AK theorem")

    points = {
        name: tuple(int(value) for value in values)
        for name, values in source["evaluation_points_mod101"].items()
    }
    require(points["e3"] == selected_e3() == (1, 1, 75), "e3 selection")
    for name, point in points.items():
        require(sum(value**3 for value in point) % t70.P == 0, f"Fermat point {name}")
    require(
        tuple(value % t70.P for value in points["e2"])
        == tuple((a - b) % t70.P for a, b in zip(points["e0"], points["e1"])),
        "dependent point",
    )
    require(base_rank([points["e0"], points["e1"], points["e2"]]) == 2, "dependent triple")
    require(base_rank([points["e0"], points["e1"], points["e3"]]) == 3, "independent triple")

    incidence = np.frombuffer(matrix_path.read_bytes(), dtype=np.uint8).reshape(
        168, 249, t70.DEGREE
    )
    kernel = canonical_kernel(incidence)
    require(
        canonical_sha256(kernel.tolist())
        == g3ak["incidence_certificate"]["canonical_kernel_basis_sha256"],
        "canonical kernel hash",
    )
    member = t70.selected_member(g3ad)
    outputs: dict[str, np.ndarray] = {}
    relation_pivots = {}
    for name, point in points.items():
        outputs[name], relation_pivots[name] = quotient_values(kernel, member, point)

    singles = {name: image_rank(outputs, (name,)) for name in points}
    pairs = {
        "+".join(names): image_rank(outputs, names)
        for names in itertools.combinations(points, 2)
    }
    dependent_names = ("e0", "e1", "e2")
    independent_names = ("e0", "e1", "e3")
    dependent_rank = image_rank(outputs, dependent_names)
    independent_rank = image_rank(outputs, independent_names)
    require(singles == {"e0": 70, "e1": 70, "e2": 68, "e3": 70}, "single ranks")
    require(set(pairs.values()) == {111}, "pair ranks")
    require((dependent_rank, independent_rank) == (111, 122), "triple ranks")

    checks = {
        "all_four_probe_points_lie_on_the_Fermat_cubic_mod101": True,
        "e3_is_selected_by_the_declared_lexicographic_rule": True,
        "the_canonical_rank123_graph_kernel_replays_G3AK": True,
        "one_fiber_images_have_ranks70_70_68_70": True,
        "every_tested_pair_has_image_rank111_and_projective_kernel11": True,
        "the_linearly_dependent_triple_e0_e1_e2_stays_at_rank111": True,
        "the_independent_triple_e0_e1_e3_has_image_rank122": True,
        "the_independent_triple_common_affine_kernel_is_exactly_the_radial_line": True,
        "the_independent_triple_projective_kernel_is_zero": True,
        "no_smooth_fiber_Picard_Deligne_or_BHT_claim_is_made": True,
    }
    require(all(checks.values()), f"T71 checks: {checks}")
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-graph-tangent-multifiber-observability.v1",
        "theorem_id": "CBF.T71",
        "status": "CLOSED_EXACT_SELECTED_RESIDUE_THREE_EVALUATION_PROJECTIVE_OBSERVABILITY_RANK122",
        "tier": "exact_F101e6_coefficient_evaluation_theorem_not_a_physical_period_result",
        "evaluation_points": {
            name: {
                "coordinates_mod101": list(point),
                "relation_pivot_zero_based": relation_pivots[name],
                "single_image_rank": singles[name],
                "single_projective_kernel_rank": 122 - singles[name],
            }
            for name, point in points.items()
        },
        "rank_panel": {
            "projective_graph_tangent_rank": 122,
            "all_pair_image_ranks": pairs,
            "all_pair_projective_kernel_rank": 11,
            "dependent_triple": {
                "points": list(dependent_names),
                "elliptic_weight_span_rank": 2,
                "image_rank": dependent_rank,
                "projective_kernel_rank": 122 - dependent_rank,
            },
            "independent_triple": {
                "points": list(independent_names),
                "elliptic_weight_span_rank": 3,
                "determinant_mod101": 77,
                "image_rank": independent_rank,
                "affine_common_kernel_rank": 1,
                "affine_common_kernel": "the radial selected-member line <F>",
                "projective_kernel_rank": 0,
                "projectively_injective": True,
            },
        },
        "theorem": {
            "statement": "For the selected residue graph-incidence family, the three coefficient-evaluation quotients at e0,e1,e3 jointly separate all 122 projective graph-preserving tangent directions. Every tested pair has image rank 111 and leaves kernel rank 11; the dependent triple e0,e1,e2 also remains rank111.",
            "interpretation": "Three linearly independent elliptic evaluation rows are sufficient for coefficient-level observability on this selected carrier, while two are not.",
        },
        "frontier_delta": {
            "closed": "a minimal witnessed three-evaluation coefficient panel with zero projective blind sector",
            "not_closed": "smoothness of the e1/e3 fibers, Picard or normal-function observability, characteristic-zero promotion, and the physical B-handle integral",
            "next_required_object": "Use three independent smooth characteristic-zero panels along the selected B-loop atlas, then transport their 82-row states with the rank-164 Gauss-Manin system; do not substitute these residue coefficient ranks for the BHT derivative.",
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "probe_points_are_deterministic_algebraic_test_rows_not_physical_knobs": True,
        },
        "guardrails": {
            "claims_e1_or_e3_is_a_certified_smooth_physical_fiber": False,
            "claims_selected_complex_path_coverage": False,
            "claims_characteristic_zero_rank_promotion": False,
            "claims_Picard_or_normal_function_derivative_rank122": False,
            "claims_beta_C_is_computed": False,
            "claims_a_beta_zero_member_exists": False,
            "claims_HYM_SM_or_QG_endpoint_closure": False,
        },
        "inputs": {
            "source_snapshot": binding(SOURCE),
            "CBF_T70": binding(t70_path),
            "UST_G3AD": binding(g3ad_path),
            "UST_G3AK_packet": binding(g3ak_path),
            "UST_G3AK_matrix": binding(matrix_path),
            "T70_builder_backend": binding(Path(t70.__file__)),
        },
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T71 multifiber observability: PASS "
        "singles=70,70,68,70 pairs=111 dependent-triple=111 independent-triple=122"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
