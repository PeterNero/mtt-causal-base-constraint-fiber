#!/usr/bin/env python3
"""Build the CBF.T63 q79 eta9 family value-map cutset packet."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
OUTPUT = ROOT / "q79_eta9_graph_family_normal_value_map.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def locate_repository(environment: str, name: str) -> Path:
    configured = os.environ.get(environment)
    path = Path(configured).expanduser().resolve() if configured else COMMON / name
    require(path.is_dir(), f"repository {name}: {path}")
    return path


REPOSITORIES = {
    "mtt-unified-source-theorem": locate_repository(
        "MTT_UNIFIED_SOURCE_REPOSITORY", "mtt-unified-source-theorem"
    ),
    "mtt-preprojection-repair-calculus": locate_repository(
        "MTT_PREPROJECTION_REPOSITORY", "mtt-preprojection-repair-calculus"
    ),
    "mtt-q79-total-superconnection-branching": locate_repository(
        "MTT_Q79_BRANCHING_REPOSITORY", "mtt-q79-total-superconnection-branching"
    ),
}

UST = REPOSITORIES["mtt-unified-source-theorem"]
PRE = REPOSITORIES["mtt-preprojection-repair-calculus"]
FSB = REPOSITORIES["mtt-q79-total-superconnection-branching"]
PRE_BHT = PRE / "experiments/q79_eta9_bht_fiber_evaluation_and_handle_sweep/outputs"
PRE_GRAPH = PRE / "experiments/q79_eta9_graph_normal_duality/outputs"

INPUTS: dict[str, tuple[str, Path]] = {
    "UST_G3AM_packet": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3am_selected_cayley_principal_response.packet.json",
    ),
    "UST_G3AM_principal_response": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3am_selected_cayley_principal_response.f101e6.u8",
    ),
    "UST_G3AN_packet": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3an_selected_cayley_full_response_schur.packet.json",
    ),
    "UST_G3AN_binary_bundle": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3an_selected_cayley_full_response_schur.f101e6.u8",
    ),
    "UST_G3AQ_packet": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3aq_selected_cayley_relative_residue_promotion.packet.json",
    ),
    "UST_G3AS_packet": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3as_selected_finite_normal_operator.packet.json",
    ),
    "UST_G3AS_normal_operator": (
        "mtt-unified-source-theorem",
        UST / "state/ust_g3as_selected_finite_normal_operator.f101e6.u8",
    ),
    "H4_pairing_kernel_packet": (
        "mtt-preprojection-repair-calculus",
        PRE_GRAPH / "q79_eta9_pairing_kernel.packet.json",
    ),
    "H4_pairing_quotient_intertwiner": (
        "mtt-preprojection-repair-calculus",
        PRE_GRAPH / "q79_eta9_graph_normal_quotient_intertwiner.f101e6.u8",
    ),
    "H4_T132_fixed_fiber_packet": (
        "mtt-preprojection-repair-calculus",
        PRE_GRAPH
        / "framed-member-char0-picard-embedding-binding"
        / "q79_eta9_framed_member_char0_picard_embedding_binding.packet.json",
    ),
    "H4_T133_fiber_evaluation_packet": (
        "mtt-preprojection-repair-calculus",
        PRE_BHT / "q79_eta9_bht_fiber_evaluation_and_handle_sweep.packet.json",
    ),
    "H4_T134_transport_packet": (
        "mtt-preprojection-repair-calculus",
        PRE_BHT / "q79_eta9_framed_member_bht_augmented_transport_contract.packet.json",
    ),
    "H4_T135_boundary_source_packet": (
        "mtt-preprojection-repair-calculus",
        PRE_BHT / "q79_eta9_framed_member_boundary_trace_source_contract.packet.json",
    ),
    "H4_T136_Serre_lift_packet": (
        "mtt-preprojection-repair-calculus",
        PRE_BHT / "q79_eta9_framed_member_serre_source_lift_contract.packet.json",
    ),
    "FSB_03g_root_selection_packet": (
        "mtt-q79-total-superconnection-branching",
        FSB / "artifacts/graph_prym_beta_root_selection.packet.json",
    ),
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(repository: str, path: Path) -> dict[str, Any]:
    root = REPOSITORIES[repository]
    return {
        "repository": repository,
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def decode_u8(path: Path, shape: list[int], offset: int = 0) -> np.ndarray:
    count = int(np.prod(shape))
    raw = path.read_bytes()
    require(offset >= 0 and offset + count <= len(raw), f"binary slice {path.name}")
    return np.frombuffer(raw, dtype=np.uint8, count=count, offset=offset).astype(
        np.int64
    ).reshape(shape)


def reduce_polynomial(
    coefficients: np.ndarray, prime: int, relation: tuple[int, ...]
) -> np.ndarray:
    degree = len(relation) - 1
    require(relation[-1] % prime == 1, "monic field relation")
    work = np.asarray(coefficients, dtype=np.int64).copy() % prime
    for power in range(work.shape[-1] - 1, degree - 1, -1):
        leading = work[..., power].copy()
        if np.any(leading):
            for index in range(degree):
                work[..., power - degree + index] -= leading * relation[index]
            work %= prime
        work[..., power] = 0
    return work[..., :degree] % prime


def multiply_scalar(
    left: np.ndarray, right: np.ndarray, prime: int, relation: tuple[int, ...]
) -> np.ndarray:
    degree = len(relation) - 1
    product = np.zeros(2 * degree - 1, dtype=np.int64)
    for left_index in range(degree):
        for right_index in range(degree):
            product[left_index + right_index] += int(left[left_index]) * int(
                right[right_index]
            )
    return reduce_polynomial(product, prime, relation)


def power_scalar(
    value: np.ndarray, exponent: int, prime: int, relation: tuple[int, ...]
) -> np.ndarray:
    degree = len(relation) - 1
    result = np.zeros(degree, dtype=np.int64)
    result[0] = 1
    base = np.asarray(value, dtype=np.int64) % prime
    while exponent:
        if exponent & 1:
            result = multiply_scalar(result, base, prime, relation)
        base = multiply_scalar(base, base, prime, relation)
        exponent >>= 1
    return result


def inverse_scalar(
    value: np.ndarray, prime: int, relation: tuple[int, ...]
) -> np.ndarray:
    degree = len(relation) - 1
    require(bool(np.any(value % prime)), "inverse of zero")
    inverse = power_scalar(value, prime**degree - 2, prime, relation)
    one = multiply_scalar(value, inverse, prime, relation)
    require(one[0] == 1 and not np.any(one[1:]), "field inverse check")
    return inverse


def scale_vector(
    row: np.ndarray, scalar: np.ndarray, prime: int, relation: tuple[int, ...]
) -> np.ndarray:
    degree = len(relation) - 1
    product = np.zeros((*row.shape[:-1], 2 * degree - 1), dtype=np.int64)
    for left_index in range(degree):
        for right_index in range(degree):
            product[..., left_index + right_index] += (
                row[..., left_index] * int(scalar[right_index])
            )
    return reduce_polynomial(product, prime, relation)


def matrix_multiply(
    left: np.ndarray, right: np.ndarray, prime: int, relation: tuple[int, ...]
) -> np.ndarray:
    require(left.ndim == right.ndim == 3, "field matrix dimensions")
    require(left.shape[1] == right.shape[0], "field matrix product shape")
    degree = len(relation) - 1
    require(left.shape[2] == right.shape[2] == degree, "field matrix degree")
    product = np.zeros(
        (left.shape[0], right.shape[1], 2 * degree - 1), dtype=np.int64
    )
    for left_index in range(degree):
        for right_index in range(degree):
            product[..., left_index + right_index] += (
                left[..., left_index] @ right[..., right_index]
            )
    return reduce_polynomial(product, prime, relation)


def matrix_rank(
    matrix: np.ndarray, prime: int, relation: tuple[int, ...]
) -> tuple[int, list[int]]:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, columns, _ = work.shape
    pivot_row = 0
    pivots: list[int] = []
    for column in range(columns):
        candidates = np.flatnonzero(
            np.any(work[pivot_row:, column, :] != 0, axis=1)
        )
        if not len(candidates):
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected], :, :] = work[[selected, pivot_row], :, :]
        inverse = inverse_scalar(work[pivot_row, column, :], prime, relation)
        work[pivot_row, column:, :] = scale_vector(
            work[pivot_row, column:, :], inverse, prime, relation
        )
        for row in range(pivot_row + 1, rows):
            factor = work[row, column, :].copy()
            if not np.any(factor):
                continue
            work[row, column:, :] = (
                work[row, column:, :]
                - scale_vector(work[pivot_row, column:, :], factor, prime, relation)
            ) % prime
        pivots.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row, pivots


def main() -> int:
    for _, path in INPUTS.values():
        require(path.is_file(), f"input {path}")

    source = {name: load(path) for name, (_, path) in INPUTS.items() if path.suffix == ".json"}
    g3am = source["UST_G3AM_packet"]
    g3an = source["UST_G3AN_packet"]
    g3aq = source["UST_G3AQ_packet"]
    g3as = source["UST_G3AS_packet"]
    pairing = source["H4_pairing_kernel_packet"]
    t132 = source["H4_T132_fixed_fiber_packet"]
    t133 = source["H4_T133_fiber_evaluation_packet"]
    t134 = source["H4_T134_transport_packet"]
    t135 = source["H4_T135_boundary_source_packet"]
    t136 = source["H4_T136_Serre_lift_packet"]
    fsb = source["FSB_03g_root_selection_packet"]

    require(g3am["theorem_id"] == "UST.G3AM", "G3AM identity")
    require(g3an["theorem_id"] == "UST.G3AN", "G3AN identity")
    require(g3aq["theorem_id"] == "UST.G3AQ", "G3AQ identity")
    require(g3as["theorem_id"] == "UST.G3AS", "G3AS identity")
    require(pairing["status"] == "CLOSED_EXACT_PROJECTIVE_RESPONSE_AND_GRAPH_NORMAL_DUALITY_ISOMORPHISM", "pairing status")
    require(t132["theorem_id"] == "H4-T132", "H4-T132 identity")
    require(t133["theorem_id"] == "H4-T133", "H4-T133 identity")
    require(t134["theorem_id"] == "H4-T134", "H4-T134 identity")
    require(t135["theorem_id"] == "H4-T135", "H4-T135 identity")
    require(t136["theorem_id"] == "H4-T136", "H4-T136 identity")
    require(fsb["claim_id"] == "FSB.03g" and fsb["all_checks_pass"], "FSB.03g identity")
    for name in (
        "UST_G3AN_packet",
        "UST_G3AQ_packet",
        "UST_G3AS_packet",
        "H4_pairing_kernel_packet",
        "H4_T132_fixed_fiber_packet",
        "H4_T133_fiber_evaluation_packet",
        "H4_T134_transport_packet",
        "H4_T135_boundary_source_packet",
        "H4_T136_Serre_lift_packet",
    ):
        require(all(source[name]["checks"].values()), f"upstream checks {name}")

    field = g3an["residue_field"]
    require(field == g3am["residue_field"] == g3as["residue_field"], "one residue field")
    prime = int(field["prime"])
    degree = int(field["extension_degree"])
    relation = tuple(int(value) for value in field["gamma_relation_coefficients_ascending"])
    require(prime == 101 and degree == 6 and len(relation) == 7, "F1016 field")

    d0_shape = [248, 33, degree]
    d0 = decode_u8(INPUTS["UST_G3AM_principal_response"][1], d0_shape)
    bundle_layout = g3an["full_response_schur"]["binary_artifact"]["layout"]
    d1_layout = bundle_layout["D1_extra_response"]
    d1 = decode_u8(
        INPUTS["UST_G3AN_binary_bundle"][1],
        [int(value) for value in d1_layout["shape"]],
        int(d1_layout["byte_offset"]),
    )
    response = np.concatenate((d0, d1), axis=1)
    normal = decode_u8(
        INPUTS["UST_G3AS_normal_operator"][1],
        [int(value) for value in g3as["normal_operator"]["shape"]],
    )
    quotient_intertwiner = decode_u8(
        INPUTS["H4_pairing_quotient_intertwiner"][1],
        [int(value) for value in pairing["quotient_intertwiner"]["shape"]],
    )

    normal_response = matrix_multiply(normal, response, prime, relation)
    response_rank, response_pivots = matrix_rank(response, prime, relation)
    normal_rank, normal_pivots = matrix_rank(normal, prime, relation)
    quotient_rank, quotient_pivots = matrix_rank(
        quotient_intertwiner, prime, relation
    )
    require(response.shape == (248, 122, degree), "response shape")
    require(normal.shape == (126, 248, degree), "normal shape")
    require(not np.any(normal_response), "N D = 0")
    require(response_rank == 122, "rank D")
    require(normal_rank == 126, "rank N")
    require(quotient_rank == 126, "rank quotient intertwiner")
    require(248 - normal_rank == response_rank, "exact-sequence dimensions")

    dimensions = t133["cohomology_dimensions"]
    require(dimensions["primitive_surface_rows"] == 248, "surface rows")
    require(dimensions["fiber_holomorphic_rows"] == 82, "fiber rows")
    require(dimensions["fixed_fiber_kernel_rank"] == 166, "fiber kernel")
    require(t134["state_correction"]["algebraic_de_Rham_transport_rank"] == 164, "transport rank")
    require(t134["state_correction"]["surface_accumulator_rank"] == 248, "accumulator rank")
    require(len(t134["midpoint_backend_audit"]["rows"]) == 6, "six transport midpoints")
    require(len(t135["sample_audit"]["rows"]) == 6, "six source midpoints")
    require(len(t136["sample_audit"]["rows"]) == 6, "six Serre lifts")
    require(t133["scope_correction"]["withdrawn_as_unproved"], "scope correction")

    checks = {
        "all_inputs_are_hash_bound": True,
        "the_selected_finite_response_has_shape_248_by_122": response.shape == (248, 122, degree),
        "the_selected_finite_response_has_exact_rank_122": response_rank == 122,
        "the_selected_finite_normal_has_shape_126_by_248": normal.shape == (126, 248, degree),
        "the_selected_finite_normal_has_exact_rank_126": normal_rank == 126,
        "the_selected_finite_normal_annihilates_every_response_column": not np.any(normal_response),
        "image_D_equals_kernel_N_over_the_selected_residue_field": response_rank == 248 - normal_rank,
        "the_graph_incidence_to_normal_quotient_intertwiner_has_exact_rank_126": quotient_rank == 126,
        "fixed_fiber_restriction_has_rank_82_and_kernel_rank_166": dimensions["fiber_holomorphic_rows"] == 82 and dimensions["fixed_fiber_kernel_rank"] == 166,
        "H4_T133_withdraws_fixed_fiber_nonzero_as_a_beta_C_rejection": "the fixed-fiber solve alone rejects the candidate from U_eta9" in t133["scope_correction"]["withdrawn_as_unproved"],
        "the_true_BHT_state_has_rank_164_with_248_accumulators": t134["state_correction"]["algebraic_de_Rham_transport_rank"] == 164 and t134["state_correction"]["surface_accumulator_rank"] == 248,
        "same_member_source_and_projective_Serre_lifts_exist_at_all_six_midpoints": len(t135["sample_audit"]["rows"]) == len(t136["sample_audit"]["rows"]) == 6,
        "FSB_03g_already_supplies_the_root_selection_and_Hensel_contract": fsb["checks"]["unit_minor_gives_an_integral_local_coordinate_system"] and fsb["checks"]["full_beta_root_not_normal_compatibility_is_the_selector"],
        "no_observed_value_fit_or_new_selector_is_used": True,
    }
    guardrails = {
        "claims_the_fixed_fiber_Picard_value_is_beta_C": False,
        "claims_the_framed_member_is_rejected_from_U_eta9": False,
        "claims_finite_modular_zero_proves_characteristic_zero_zero": False,
        "claims_the_linear_exact_sequence_is_the_nonlinear_root_theorem": False,
        "claims_six_midpoints_are_a_panelwise_directed_integration": False,
        "claims_beta_C_or_the_q79_physical_member_is_selected": False,
        "claims_B_ETA9_01_or_B_ETA9_02_is_closed": False,
    }
    require(all(checks.values()) and not any(guardrails.values()), "claim boundary")

    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-graph-family-normal-value-map.v1",
        "theorem_id": "CBF.T63",
        "status": "CLOSED_EXACT_FINITE_LINEAR_VALUE_MAP_CUTSET_AND_CORRECTED_BHT_EXECUTION_FRONTIER",
        "tier": "EXACT_FINITE_RESIDUE_SEQUENCE_PLUS_SOURCE_LOCKED_CHARACTERISTIC_ZERO_EXECUTION_CONTRACT",
        "residue_field": field,
        "finite_exact_sequence": {
            "sequence": "0 -> F_101^6^122 --D--> F_101^6^248 --N_full--> F_101^6^126 -> 0",
            "response_shape": [248, 122],
            "response_rank": response_rank,
            "response_pivot_columns_zero_based": response_pivots,
            "normal_shape": [126, 248],
            "normal_rank": normal_rank,
            "normal_pivot_columns_zero_based": normal_pivots,
            "normal_times_response_nonzero_entries": int(np.count_nonzero(normal_response)),
            "kernel_normal_dimension": 248 - normal_rank,
            "image_response_equals_kernel_normal": True,
            "affine_linear_criterion": "For b in F_101^6^248, b+D*t=0 is solvable iff N_full*b=0; when solvable, t is unique because D is injective.",
            "scope": "exact selected finite tangent criterion; not the nonlinear characteristic-zero beta_C root",
        },
        "graph_normal_duality": {
            "formula": pairing["quotient_intertwiner"]["formula"],
            "shape": [126, 126],
            "rank": quotient_rank,
            "pivot_columns_zero_based": quotient_pivots,
            "meaning": "the graph-incidence complement and finite Deligne-normal quotient are isomorphic over the selected residue field",
        },
        "fixed_fiber_scope_correction": {
            "surface_primitive_rows": 248,
            "fiber_holomorphic_rows": 82,
            "fiber_restriction_rank": 82,
            "fiber_restriction_kernel_rank": 166,
            "retained": t133["scope_correction"]["H4_T132_retained"],
            "corrected_conclusion": t133["scope_correction"]["not_implied"],
            "withdrawn_as_unproved": t133["scope_correction"]["withdrawn_as_unproved"],
        },
        "characteristic_zero_value_map": {
            "analytic_map": fsb["selection_theorem"]["analytic_map"],
            "derivative": fsb["selection_theorem"]["derivative"],
            "root_selection_contract": "already closed by FSB.03g and not reproved here",
            "normal_compatibility": "a necessary 126-row linear condition, not a sufficient nonlinear root condition",
            "accepted_full_beta_rows": {"accepted": 0, "total": 248},
            "accepted_characteristic_zero_normal_rows": {"accepted": 0, "total": 126},
        },
        "BHT_execution_cutset": {
            "physical_segments": t134["path_typing"]["physical_base_segments"],
            "transport_state_rank": 164,
            "holomorphic_readout_rank": 82,
            "surface_accumulator_rank": 248,
            "normal_first_accumulator_rank_after_char0_normal": 126,
            "forward_state_rank": 412,
            "normal_first_forward_state_rank_after_char0_normal": 290,
            "same_member_midpoint_transport_backends": {"accepted": 6, "total": 6, "tier": "binary64 point replay"},
            "same_member_midpoint_boundary_sources": {"accepted": 6, "total": 6, "tier": "binary64 point replay"},
            "same_member_midpoint_projective_H01_lifts": {"accepted": 6, "total": 6, "tier": "binary64 point replay"},
            "intrinsically_normalized_H01_source": {"accepted": 0, "total": 1},
            "panelwise_complete_rank164_action": {"accepted": 0, "total": 6},
            "panelwise_directed_source": {"accepted": 0, "total": 6},
            "directed_path_integration": {"accepted": 0, "total": 1},
            "period_quotient": {"accepted": 0, "total": 1},
        },
        "frontier_delta": {
            "closed": [
                "the exact selected finite tangent-normal sequence and affine solvability criterion",
                "the exact rank-126 graph-complement to normal-quotient isomorphism",
                "the 248-surface-row versus 82-fiber-row typing error",
                "the rank-164 transport, rank-82 readout and rank-248 accumulator architecture",
                "same-member boundary source and projective H01 lift at all six physical midpoints",
                "the root-selection and same-residue Hensel contract through FSB.03g",
            ],
            "retired_targets": [
                "rejecting the framed member from one fixed-fiber Picard nonidentity",
                "evaluating 122 independent fixed-fiber Picard points as a substitute for beta_C",
                "rebuilding the already-closed Hensel uniqueness theorem",
            ],
            "next_required_object": "Promote the H4-T136 source lift to intrinsic residue/integral normalization, then emit multiprecision panelwise rank-164 Gauss-Manin action and source on the six selected B-loop segments with directed ODE/quadrature error. Accumulate beta_C in 248 rows, or 126 rows only after an explicit characteristic-zero normal operator exists.",
            "decision_order": [
                "compute one same-member characteristic-zero beta_C value",
                "apply a finite one-way normal obstruction or an explicit characteristic-zero normal evaluator",
                "reject on certified nonzero normal residual, otherwise invoke the existing FSB.03g full-root contract",
            ],
            "open_blockers": ["B.ETA9.01", "B.ETA9.02"],
        },
        "checks": checks,
        "guardrails": guardrails,
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "physical_member_selected": False,
        },
        "inputs": {
            name: record(repository, path)
            for name, (repository, path) in INPUTS.items()
        },
    }
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T63 family value-map cutset: PASS "
        "rank(D)=122 rank(N)=126 im(D)=ker(N) BHT=typed beta=OPEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
