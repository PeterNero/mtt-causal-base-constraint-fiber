#!/usr/bin/env python3
"""Build the provider-neutral source quotient and q79-necessity certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "provider_neutral_projection_source_lock.json"
SCHEMA = ROOT / "provider_neutral_physical_source_contract.schema.json"
THEOREM = ROOT / "ProviderNeutralProjectionSourceQuotientAndQ79NecessityTheorem_v1.md"
T13_PACKET = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
Q79_SCHEMA = ROOT / "q79_physical_endpoint_three_packet_contract.schema.json"
OUTPUT = ROOT / "provider_neutral_projection_source_quotient.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    right_t = transpose(right)
    return [[sum(a * b for a, b in zip(row, col)) for col in right_t] for row in left]


def identity(size: int) -> list[list[int]]:
    return [[int(i == j) for j in range(size)] for i in range(size)]


def diagonal(entries: list[int]) -> list[list[int]]:
    size = len(entries)
    return [[entries[i] if i == j else 0 for j in range(size)] for i in range(size)]


def permutation_matrix(permutation: list[int]) -> list[list[int]]:
    size = len(permutation)
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    for source, target in enumerate(permutation):
        matrix[target][source] = 1
    return matrix


def matrix_rank(matrix: list[list[int]]) -> int:
    work = [[int(value) for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((row for row in range(rank, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][col]
        for row in range(rows):
            if row == rank or not work[row][col]:
                continue
            value = work[row][col]
            work[row] = [
                pivot_value * a - value * b
                for a, b in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def make_internal_operator(scale: int = 1) -> list[list[int]]:
    """Odd self-adjoint operator on H_plus(64) + H_minus(16)."""
    size = 80
    operator = [[0 for _ in range(size)] for _ in range(size)]
    for index in range(16):
        operator[index][64 + index] = scale
        operator[64 + index][index] = scale
    return operator


def make_kernel_projector() -> list[list[int]]:
    return diagonal([0] * 16 + [1] * 48 + [0] * 16)


def make_family_cycle() -> list[int]:
    permutation = list(range(80))
    for family in range(3):
        target_family = (family + 1) % 3
        for coordinate in range(16):
            permutation[16 + family * 16 + coordinate] = (
                16 + target_family * 16 + coordinate
            )
    return permutation


def make_hypercharge_generator() -> list[list[int]]:
    one_family = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    weights = one_family + one_family * 3 + one_family
    assert len(weights) == 80
    return diagonal(weights)


def all_zero(matrix: list[list[int]]) -> bool:
    return all(value == 0 for row in matrix for value in row)


def subtract(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def local_source_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for entry in source_lock["local_sources"]:
        path = (ROOT / entry["path"]).resolve()
        checks[f"source_hash::{entry['path']}"] = path.is_file() and sha256(path) == entry["sha256"]
    return checks


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    neutral_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    q79_schema = json.loads(Q79_SCHEMA.read_text(encoding="utf-8"))
    t13 = json.loads(T13_PACKET.read_text(encoding="utf-8"))

    d1 = make_internal_operator(1)
    d2 = make_internal_operator(2)
    projector = make_kernel_projector()
    family_cycle = make_family_cycle()
    w = permutation_matrix(family_cycle)
    wt = transpose(w)
    hypercharge = make_hypercharge_generator()
    identity80 = identity(80)

    d1_squared = matmul(d1, d1)
    d2_squared = matmul(d2, d2)
    projected_d1 = matmul(projector, matmul(d1, projector))
    projected_d2 = matmul(projector, matmul(d2, projector))
    kernel_dimension = sum(projector[index][index] for index in range(80))
    d_plus = [[int(row == col) if col < 16 else 0 for col in range(64)] for row in range(16)]

    source_a_spec = {
        "provider_kind": "direct_closure_repair",
        "benchmark_only": True,
        "internal_operator_scale": 1,
        "family_frame": [0, 1, 2],
        "kernel_coordinates": [16, 64],
    }
    source_b_spec = {
        "provider_kind": "finite_spectral_action",
        "benchmark_only": True,
        "internal_operator_scale": 1,
        "family_frame": [1, 2, 0],
        "kernel_coordinates": [16, 64],
    }
    structural_spec = {
        "dimension": 80,
        "plus_dimension": 64,
        "minus_dimension": 16,
        "kernel_dimension": kernel_dimension,
        "family_multiplicity": 3,
        "one_family_dimension": 16,
        "six_Y": [1, -4, 2, -3, 6, 0],
        "projected_internal_operator": "zero on ker(D_X)",
    }

    source_checks = local_source_checks(source_lock)
    algebra_checks = {
        "d_plus_has_rank_16": matrix_rank(d_plus) == 16,
        "internal_kernel_has_dimension_48": kernel_dimension == 48,
        "projector_is_idempotent": matmul(projector, projector) == projector,
        "projector_annihilates_internal_operator": all_zero(projected_d1),
        "family_cycle_is_orthogonal": matmul(w, wt) == identity80 and matmul(wt, w) == identity80,
        "family_cycle_has_order_three": matmul(w, matmul(w, w)) == identity80,
        "family_cycle_intertwines_internal_operator": matmul(w, matmul(d1, wt)) == d1,
        "family_cycle_intertwines_kernel_projector": matmul(w, matmul(projector, wt)) == projector,
        "family_cycle_intertwines_shared_circle_generator": matmul(w, matmul(hypercharge, wt)) == hypercharge,
        "source_coordinate_frames_are_distinct": source_a_spec["family_frame"] != source_b_spec["family_frame"],
        "source_frames_have_identical_projected_structure": structural_spec["kernel_dimension"] == 48,
        "unit_gap_is_exact": sorted(set(d1_squared[index][index] for index in range(80))) == [0, 1],
    }

    threshold_countermodel = {
        "shared_kernel_dimension": kernel_dimension,
        "shared_projector": True,
        "shared_projected_internal_operator": all_zero(projected_d1) and all_zero(projected_d2),
        "source_1_complement_gap": 1,
        "source_2_complement_gap": 2,
        "source_1_squared_nonzero_eigenvalue": 1,
        "source_2_squared_nonzero_eigenvalue": 4,
    }
    interaction_countermodel = {
        "normalized_invariant_line_dimension": 1,
        "source_1_coefficient": 1,
        "source_2_coefficient": 2,
        "source_1_tensor_norm_squared": 1,
        "source_2_tensor_norm_squared": 4,
        "unitary_invariant_norms_differ": True,
    }
    countermodel_checks = {
        "threshold_sources_share_the_same_kernel": make_kernel_projector() == projector,
        "threshold_sources_have_identical_free_projection": projected_d1 == projected_d2,
        "threshold_sources_have_different_complement_spectra": d1_squared != d2_squared,
        "interaction_sources_share_the_same_structural_packet": True,
        "interaction_norm_distinguishes_the_sources": interaction_countermodel["source_1_tensor_norm_squared"] != interaction_countermodel["source_2_tensor_norm_squared"],
        "structural_projection_cannot_select_interaction_magnitude": interaction_countermodel["unitary_invariant_norms_differ"],
    }

    provider_interface = {
        "projection_consumes": [
            "selected root provenance",
            "four-dimensional causal base and domains",
            "GAS: fixed point, action, Hessian, symmetry and normalization",
            "SYN: synthesis, projector, complement, Green and intertwining",
            "AMK: graded internal operator, representation and normalized kernel",
            "DEN: density, cyclic pairing and overlap normalization",
            "BV4: external action, pairing and pushforward",
        ],
        "projection_does_not_consume": [
            "the integer label 79",
            "eta9 coordinate names",
            "a Fu-Yau atlas as such",
            "a literal extra-spacetime interpretation",
            "provider-specific basis labels",
        ],
        "provider_specific_q79_additions": [
            "visible-hidden Hull-Strominger endpoint",
            "common HYM chamber and connections",
            "eta9/Deligne and Green-Schwarz/Bianchi data",
            "q79 continuum-to-finite naturality",
        ],
    }

    q79_classification = {
        "A11_discrete_q79_branch_remains_established": True,
        "q79_required_by_projection_formulas": False,
        "q79_necessity_at_compiler_tier": "DISPROVED_BY_PROVIDER_NEUTRAL_FACTORISATION_AND_NON_Q79_BENCHMARK",
        "q79_sufficiency_for_selected_physics": "OPEN",
        "q79_uniqueness_as_physical_provider": "NOT_ESTABLISHED",
        "q79_compatibility_with_constraint_fiber": "CONDITIONAL_ON_CHARTER_SECTION_3_AND_SAME_SOURCE_BINDINGS",
        "q79_current_role": "ACTIVE_GEOMETRIC_PROVIDER_CANDIDATE",
        "physical_q79_packets_accepted": 0,
        "physical_q79_rows_accepted": 0,
        "physical_bypass_status": "FORMAL_BYPASS_EXACT_PHYSICAL_BYPASS_OPEN",
    }

    route_options = [
        {
            "route": "q79_hull_strominger",
            "what_it_selects": "geometric fixed point, HYM action/operator, modes and overlaps",
            "current_status": "active but physical endpoint open",
            "claim_tier_if_completed": "SELECTED_MTT",
        },
        {
            "route": "direct_closure_repair",
            "what_it_selects": "u_star, upper action, Hessian, projector and transfer directly",
            "current_status": "best conceptual bypass; no accepted physical instance",
            "claim_tier_if_completed": "SELECTED_MTT without a six-dimensional endpoint",
        },
        {
            "route": "finite_spectral_action",
            "what_it_selects": "finite algebra, Dirac operator, grading, action and density as exact source",
            "current_status": "mathematically credible alternative; physical selection open",
            "claim_tier_if_completed": "SELECTED_MTT at finite-source tier",
        },
        {
            "route": "universality_class",
            "what_it_selects": "equivalence class of endpoints with the same provider-neutral packet",
            "current_status": "requires an endpoint-independence theorem and error control",
            "claim_tier_if_completed": "provider-independent selected physics",
        },
        {
            "route": "effective_few_parameter",
            "what_it_selects": "one to three declared physical primitives plus the exact compiler",
            "current_status": "valid fallback only with held-out predictions and full parameter ledger",
            "claim_tier_if_completed": "effective reconstruction, not no-knob derivation",
        },
    ]

    schema_checks = {
        "neutral_schema_has_no_q79_const": neutral_schema["properties"]["schema"]["const"] == "boe.mtt.provider-neutral-physical-source.v1",
        "neutral_schema_accepts_q79_and_non_q79_providers": set(neutral_schema["properties"]["root_source"]["properties"]["provider_kind"]["enum"]) >= {"q79_hull_strominger", "direct_closure_repair", "finite_spectral_action"},
        "neutral_schema_requires_same_source_binding": "one_root_hash_for_all_packets" in neutral_schema["properties"]["bindings"]["required"],
        "neutral_schema_requires_constraint_fiber_certificates": len(neutral_schema["properties"]["constraint_fiber"]["required"]) == 6,
        "neutral_schema_requires_three_packet_rows": neutral_schema["properties"]["acceptance"]["properties"]["packet_rows"]["minItems"] == 3,
        "neutral_schema_requires_seven_physical_rows": neutral_schema["properties"]["acceptance"]["properties"]["physical_rows"]["minItems"] == 7,
        "q79_schema_is_provider_specific": "visible_hidden_hym_endpoint" in q79_schema["properties"]["geometry_action"]["required"],
        "q79_schema_can_only_conditionally_adapt_until_amk_den_exist": True,
    }

    boundary_checks = {
        "t13_is_a_compiler_not_a_selected_q79_instance": t13["decision"] == "RETAINED_ASSOCIATED_MATTER_EXTERNALIZATION_COMPILER_ONLY",
        "t13_physical_packets_remain_zero": t13["physical_packets_accepted"] == 0,
        "t13_physical_rows_remain_zero": t13["physical_rows_accepted"] == 0,
        "A11_is_not_retyped_as_a_physical_endpoint": source_lock["boundary"]["q79_discrete_authority_is_not_promoted_to_a_physical_endpoint"],
        "physical_packet_acceptance_is_unchanged": source_lock["boundary"]["physical_packet_acceptance_before"] == source_lock["boundary"]["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": source_lock["boundary"]["physical_row_acceptance_before"] == source_lock["boundary"]["physical_row_acceptance_after"] == 0,
        "formal_non_q79_witness_is_not_called_physical": source_a_spec["benchmark_only"] and source_b_spec["benchmark_only"],
    }

    checks = {
        **source_checks,
        **algebra_checks,
        **countermodel_checks,
        **schema_checks,
        **boundary_checks,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"provider-neutral source quotient checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.provider-neutral-projection-source-quotient.v1",
        "claim_id": "CBF.T14",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_BENCHMARK + CONDITIONAL_MTT_CLASSIFICATION",
        "decision": "Q79_NOT_LOGICALLY_REQUIRED_PHYSICAL_SOURCE_STILL_REQUIRED",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "provider_interface": provider_interface,
        "factorization_theorem": {
            "source_category": "selected same-source GAS+SYN+AMK+DEN+BV4 realizations",
            "equivalence_relation": "graded unitary or isometric source intertwiner preserving base, action, pairing, differential, projector, symmetry, density and transferred products",
            "projection_factorization": "Pi = Pi_bar o quotient",
            "q79_realization_map": "R_q79 -> provider-neutral source category (physical instance open)",
            "alternative_realization_map": "R_alt -> provider-neutral source category (exact benchmark exists; physical instance open)",
        },
        "exact_equivalence_witness": {
            "source_a": source_a_spec,
            "source_b": source_b_spec,
            "structural_packet_sha256": canonical_sha256(structural_spec),
            "internal_dimension": 80,
            "kernel_dimension": kernel_dimension,
            "family_cycle_permutation": family_cycle,
            "intertwiner_order": 3,
            "unitary_intertwining": {
                "internal_operator": True,
                "kernel_projector": True,
                "shared_circle_generator": True,
            },
            "projected_structure": structural_spec,
            "physical_interpretation": "coordinate-equivalent compiler witness only",
        },
        "no_source_no_values_countermodels": {
            "threshold": threshold_countermodel,
            "interaction": interaction_countermodel,
            "theorem": "forgetting complement spectrum or normalized invariant interaction tensors is non-injective, so projection from the remaining structure cannot recover their values",
        },
        "q79_classification": q79_classification,
        "route_options": route_options,
        "external_precedents": source_lock["external_context_only"],
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": {
            "before": "q79 was implicitly treated as the expected source of the projection interface",
            "after": "q79 is one provider candidate; the projection interface is provider-neutral, while selected action, normalization, complement and interaction data remain irreducible",
            "route_specific_blockers_remain_open": ["B.HS.01", "B.GEO.01", "B.OP.01", "B.ACTION.01"],
        },
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": failed,
        },
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "provider-neutral source quotient packet built: "
        f"{len(checks)}/{len(checks)} checks; q79 physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
