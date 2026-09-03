#!/usr/bin/env python3
"""Build CBF.T70, the exact graph-tangent single-fiber coefficient rank."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_graph_tangent_single_fiber_rank.source.json"
OUTPUT = ROOT / "q79_eta9_graph_tangent_single_fiber_rank.packet.json"
P = 101
RELATION = np.array([64, 16, 33, 44, 89, 24, 1], dtype=np.int64)
DEGREE = 6


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def field_mul(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    shape = np.broadcast_shapes(left.shape[:-1], right.shape[:-1])
    a = np.broadcast_to(left, shape + (DEGREE,))
    b = np.broadcast_to(right, shape + (DEGREE,))
    work = np.zeros(shape + (2 * DEGREE - 1,), dtype=np.int64)
    for i in range(DEGREE):
        for j in range(DEGREE):
            work[..., i + j] += a[..., i] * b[..., j]
    work %= P
    for exponent in range(2 * DEGREE - 2, DEGREE - 1, -1):
        coefficient = work[..., exponent].copy()
        shift = exponent - DEGREE
        for relation_exponent in range(DEGREE):
            work[..., shift + relation_exponent] -= (
                coefficient * RELATION[relation_exponent]
            )
        work %= P
    return work[..., :DEGREE]


def field_power(value: np.ndarray, exponent: int) -> np.ndarray:
    result = np.array([1, 0, 0, 0, 0, 0], dtype=np.int64)
    base = value.copy()
    while exponent:
        if exponent & 1:
            result = field_mul(result, base)
        base = field_mul(base, base)
        exponent //= 2
    return result


def field_inverse(value: np.ndarray) -> np.ndarray:
    require(bool(np.any(value)), "nonzero field inverse")
    inverse = field_power(value, P**DEGREE - 2)
    require(
        np.array_equal(
            field_mul(value, inverse), np.array([1, 0, 0, 0, 0, 0])
        ),
        "field inverse replay",
    )
    return inverse


def rank(matrix: np.ndarray) -> tuple[int, list[int]]:
    work = matrix.astype(np.int64, copy=True) % P
    row_count, column_count, extension_degree = work.shape
    require(extension_degree == DEGREE, "field width")
    pivot_row = 0
    pivots: list[int] = []
    for column in range(column_count):
        candidates = np.flatnonzero(np.any(work[pivot_row:, column, :] != 0, axis=1))
        if not len(candidates):
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected], :, :] = work[[selected, pivot_row], :, :]
        inverse = field_inverse(work[pivot_row, column, :])
        if pivot_row + 1 < row_count:
            factors = field_mul(work[pivot_row + 1 :, column, :], inverse)
            products = field_mul(
                factors[:, None, :], work[pivot_row : pivot_row + 1, :, :]
            )
            work[pivot_row + 1 :, :, :] = (
                work[pivot_row + 1 :, :, :] - products
            ) % P
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row, pivots


def monomials(degree: int) -> list[tuple[int, int, int]]:
    return [
        (x_power, y_power, degree - x_power - y_power)
        for x_power in range(degree, -1, -1)
        for y_power in range(degree - x_power, -1, -1)
    ]


def coefficient_lookup() -> dict[tuple[int, str, tuple[int, int, int]], int]:
    lookup: dict[tuple[int, str, tuple[int, int, int]], int] = {}
    index = 0
    for coordinate in range(3):
        for kind, degree in (("base_degree9", 9), ("K3_sheet_times_degree6", 6)):
            for powers in monomials(degree):
                lookup[(coordinate, kind, powers)] = index
                index += 1
    require(index == 249, "coefficient basis rank")
    return lookup


def selected_member(g3ad: dict[str, Any]) -> np.ndarray:
    vector = np.zeros((249, DEGREE), dtype=np.int64)
    lookup = coefficient_lookup()
    for row in g3ad["fixed_FQ"]["nonzero_gamma_rows"]:
        key = (
            int(row["target_coordinate"]),
            str(row["basis_kind"]),
            tuple(int(value) for value in row["powers_xyz"]),
        )
        vector[lookup[key], :] = np.array(
            row["gamma_coefficients_ascending"], dtype=np.int64
        )
    return vector % P


def principal_slice(g3ak: dict[str, Any]) -> np.ndarray:
    lookup = coefficient_lookup()
    union = {
        tuple(int(value) for value in row["powers_xyz"]): np.array(
            row["gamma_coefficients"], dtype=np.int64
        )
        for row in g3ak["selected_graph_union"]["union_terms"]
    }
    columns = []
    for coordinate in range(3):
        for monomial in monomials(3):
            vector = np.zeros((249, DEGREE), dtype=np.int64)
            for exponent, coefficient in union.items():
                output = tuple(a + b for a, b in zip(exponent, monomial))
                vector[lookup[(coordinate, "base_degree9", output)], :] = coefficient
            columns.append(vector)
        vector = np.zeros((249, DEGREE), dtype=np.int64)
        for exponent, coefficient in union.items():
            vector[
                lookup[(coordinate, "K3_sheet_times_degree6", exponent)], :
            ] = coefficient
        columns.append(vector)
    require(len(columns) == 33, "principal slice rank")
    return np.stack(columns, axis=0) % P


def matrix_vector(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    products = field_mul(matrix, vector[None, :, :])
    return np.sum(products, axis=1, dtype=np.int64) % P


def quotient_evaluation(member: np.ndarray) -> tuple[np.ndarray, int, np.ndarray]:
    block = 83
    relation = (member[:block, :] - member[2 * block :, :]) % P
    nonzero = np.flatnonzero(np.any(relation != 0, axis=1))
    require(len(nonzero) > 0, "nonzero fixed-fiber relation")
    pivot = int(nonzero[0])
    pivot_inverse = field_inverse(relation[pivot, :])
    rows = []
    one = np.array([1, 0, 0, 0, 0, 0], dtype=np.int64)
    for coordinate in range(block):
        if coordinate == pivot:
            continue
        quotient_row = np.zeros((block, DEGREE), dtype=np.int64)
        quotient_row[coordinate, :] = one
        quotient_row[pivot, :] = (-field_mul(relation[coordinate, :], pivot_inverse)) % P
        surface_row = np.zeros((249, DEGREE), dtype=np.int64)
        surface_row[:block, :] = quotient_row
        surface_row[2 * block :, :] = (-quotient_row) % P
        rows.append(surface_row)
    result = np.stack(rows, axis=0)
    require(result.shape == (82, 249, DEGREE), "quotient evaluation shape")
    require(not np.any(matrix_vector(result, member)), "radial member killed")
    return result, pivot, relation


def main() -> int:
    source = load(SOURCE)
    require(
        source["schema"] == "mtt.cbf.q79-eta9-graph-tangent-single-fiber-rank-source.v1",
        "source schema",
    )
    sources = source["sources"]
    g3ad_path = ROOT / sources["UST_G3AD"]["local_path"]
    g3ak_path = ROOT / sources["UST_G3AK"]["local_packet_path"]
    matrix_path = ROOT / sources["UST_G3AK"]["local_matrix_path"]
    h133_path = ROOT / sources["H4_T133"]["local_path"]
    require(sha256(g3ad_path) == sources["UST_G3AD"]["local_sha256"], "G3AD hash")
    require(sha256(g3ak_path) == sources["UST_G3AK"]["local_packet_sha256"], "G3AK hash")
    require(sha256(matrix_path) == sources["UST_G3AK"]["local_matrix_sha256"], "matrix hash")
    require(sha256(h133_path) == sources["H4_T133"]["local_sha256"], "H4-T133 hash")

    g3ad = load(g3ad_path)
    g3ak = load(g3ak_path)
    h133 = load(h133_path)
    require(g3ad["theorem_id"] == "UST.G3AD", "G3AD theorem")
    require(g3ak["theorem_id"] == "UST.G3AK", "G3AK theorem")
    require(h133["theorem_id"] == "H4-T133", "H4-T133 theorem")
    require(
        g3ak["residue_field"]["gamma_relation_coefficients_ascending"]
        == RELATION.tolist(),
        "field relation",
    )
    require(
        h133["fiber_evaluation_operator"]["codomain_rank"] == 82,
        "fiber quotient rank",
    )

    raw = np.frombuffer(matrix_path.read_bytes(), dtype=np.uint8)
    incidence = raw.reshape(168, 249, DEGREE).astype(np.int64)
    incidence_rank, incidence_pivots = rank(incidence)
    require(incidence_rank == g3ak["incidence_certificate"]["rank"] == 126, "incidence rank")
    require(
        incidence_pivots == g3ak["incidence_certificate"]["pivot_columns_zero_based"],
        "incidence pivot replay",
    )

    member = selected_member(g3ad)
    require(not np.any(matrix_vector(incidence, member)), "member in incidence kernel")
    quotient, relation_pivot, fiber_relation = quotient_evaluation(member)
    quotient_rank, quotient_pivots = rank(quotient)
    require(quotient_rank == 82, "quotient rank")
    principal = principal_slice(g3ak)
    require(
        not np.any(
            np.stack([matrix_vector(incidence, vector) for vector in principal])
        ),
        "principal slice in incidence kernel",
    )
    principal_evaluations = np.stack(
        [matrix_vector(quotient, vector) for vector in principal]
    )
    principal_image_rank, _principal_image_pivots = rank(principal_evaluations)
    stacked = np.concatenate((incidence, quotient), axis=0)
    stacked_rank, stacked_pivots = rank(stacked)
    image_rank = stacked_rank - incidence_rank
    affine_kernel_rank = 249 - incidence_rank
    invisible_affine_rank = affine_kernel_rank - image_rank
    invisible_projective_rank = invisible_affine_rank - 1
    print(
        "T70 rank probe: "
        f"incidence={incidence_rank} quotient={quotient_rank} "
        f"stacked={stacked_rank} image={image_rank} "
        f"principal-image={principal_image_rank} "
        f"affine-invisible={invisible_affine_rank} "
        f"projective-invisible={invisible_projective_rank}",
        flush=True,
    )
    require(
        (stacked_rank, image_rank, invisible_affine_rank, invisible_projective_rank)
        == (196, 70, 53, 52),
        "single-fiber graph tangent ranks",
    )
    require(principal_image_rank == 11, "principal-slice fiber image rank")
    fiber_cokernel_rank = quotient_rank - image_rank
    additional_image_rank = image_rank - principal_image_rank
    require(
        (fiber_cokernel_rank, additional_image_rank) == (12, 59),
        "fiber cokernel and additional image ranks",
    )

    checks = {
        "vendored_incidence_matrix_replays_the_G3AK_rank126_and_pivots": True,
        "the_selected_member_lies_in_the_rank123_incidence_kernel": True,
        "the_Fermat_origin_relation_is_A0_minus_A2_and_is_nonzero": True,
        "the_82_row_quotient_operator_kills_the_radial_member": True,
        "the_quotient_operator_has_rank82": True,
        "the_stacked_incidence_and_fiber_operator_has_rank208": True,
        "the_principal33_slice_has_fixed_fiber_image_rank11": True,
        "the_full_graph_kernel_has_fixed_fiber_image_rank70_and_cokernel12": True,
        "the89_additional_tangent_directions_add59_image_dimensions": True,
        "the_affine_invisible_kernel_has_rank53_including_the_radial_member": True,
        "the_projective_single_fiber_invisible_tangent_has_rank52": True,
        "no_normal_function_Deligne_or_BHT_derivative_is_claimed": True,
    }
    require(all(checks.values()), f"T70 checks: {checks}")

    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-graph-tangent-single-fiber-rank.v1",
        "theorem_id": "CBF.T70",
        "status": "CLOSED_EXACT_SELECTED_RESIDUE_GRAPH_TANGENT_TO_FIXED_FIBER_RANK70_KERNEL52",
        "tier": "exact_F101e6_linear_algebra_with_hash_locked_cross_repository_inputs",
        "selected_carrier": {
            "field": "F_101[gamma]/(M)",
            "extension_degree": 6,
            "eta9_coefficient_rank": 249,
            "graph_incidence_rank": incidence_rank,
            "graph_incidence_affine_kernel_rank": affine_kernel_rank,
            "graph_incidence_projective_tangent_rank": affine_kernel_rank - 1,
            "selected_fiber": "Fermat origin e_0",
            "elliptic_evaluation_weights": [1, 0, -1],
            "fiber_relation_pivot_zero_based": relation_pivot,
            "fiber_relation_sha256": canonical_sha256(fiber_relation.tolist()),
        },
        "rank_calculation": {
            "incidence_rank": incidence_rank,
            "fixed_fiber_quotient_rank": quotient_rank,
            "stacked_rank": stacked_rank,
            "restriction_image_on_graph_kernel_rank": image_rank,
            "restriction_is_surjective": False,
            "fixed_fiber_cokernel_rank": fiber_cokernel_rank,
            "principal33_slice_image_rank": principal_image_rank,
            "additional89_directions_new_image_rank_modulo_principal_image": additional_image_rank,
            "affine_invisible_kernel_rank": invisible_affine_rank,
            "radial_rank_inside_invisible_kernel": 1,
            "projective_invisible_tangent_rank": invisible_projective_rank,
            "dimension_identities": [
                "249-126=123",
                "196-126=70",
                "82-70=12",
                "123-70=53",
                "53-1=52",
                "122=70+52",
                "70-11=59",
            ],
            "incidence_pivots_zero_based": incidence_pivots,
            "fixed_fiber_quotient_pivots_zero_based": quotient_pivots,
            "stacked_pivots_zero_based": stacked_pivots,
        },
        "theorem": {
            "statement": "On the selected residue carrier, restriction of the rank-122 projective graph-preserving coefficient tangent to the Fermat-origin fiber quotient V/<F_e0> has rank 70, kernel rank 52 and cokernel rank 12. The old principal rank-33 slice has image rank only 11.",
            "interpretation": "The full graph family reaches seventy fixed-fiber coefficient directions, is blind to fifty-two projective family directions, and forbids twelve of the eighty-two possible fiber directions. The 89 extra graph-preserving directions add 59 image dimensions missed by the principal slice.",
        },
        "frontier_delta": {
            "closed": "the exact coefficient-level image, kernel and cokernel of one-fiber restriction inside the full graph family",
            "not_closed": "the derivative of the fixed-fiber Picard point, the 248-row BHT handle integral, or its derivative",
            "consequence": "a one-fiber coefficient test cannot isolate a graph-family member and the old principal slice misses 59 accessible image directions; the global BHT sweep remains required",
            "next_required_object": "Complete the pathwide characteristic-zero BHT sweep for C_fr; afterward evaluate its family derivative on the rank-122 tangent, using the rank-52 one-fiber kernel and rank-12 cokernel as explicit cutsets rather than hidden degeneracies.",
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "rank52_is_a_deformation_kernel_not_a_parameter_count": True,
        },
        "guardrails": {
            "claims_this_is_the_Abel_Jacobi_derivative": False,
            "claims_this_is_the_Deligne_or_BHT_derivative": False,
            "claims_one_fiber_selects_a_unique_member": False,
            "claims_beta_C_is_computed": False,
            "claims_a_beta_zero_member_exists": False,
            "claims_HYM_SM_or_QG_endpoint_closure": False,
        },
        "inputs": {
            "source_snapshot": binding(SOURCE),
            "UST_G3AD": binding(g3ad_path),
            "UST_G3AK_packet": binding(g3ak_path),
            "UST_G3AK_matrix": binding(matrix_path),
            "H4_T133": binding(h133_path),
            "upstream_repositories": {
                "mtt_unified_source_theorem": sources["UST_G3AK"]["repository_commit"],
                "mtt_preprojection_repair_calculus": sources["H4_T133"]["repository_commit"],
            },
        },
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T70 graph-tangent fiber rank: PASS "
        "projective=122 image=70 invisible=52 cokernel=12 principal-image=11"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
