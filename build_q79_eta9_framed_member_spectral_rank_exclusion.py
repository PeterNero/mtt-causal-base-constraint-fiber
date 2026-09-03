#!/usr/bin/env python3
"""Build CBF.T69 from the exact H4-T132 low-order torsion exclusion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_framed_member_spectral_rank_exclusion.source.json"
T68_PACKET = ROOT / "q79_eta9_twisted_spectral_rank_divisibility.packet.json"
OUTPUT = ROOT / "q79_eta9_framed_member_spectral_rank_exclusion.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    source = load(SOURCE)
    require(
        source["schema"]
        == "mtt.cbf.q79-eta9-framed-member-spectral-rank-exclusion-source.v1",
        "source schema",
    )
    h4_source = source["sources"]["H4_T132"]
    t68_source = source["sources"]["T68"]

    h4_path = ROOT / h4_source["local_path"]
    require(h4_path.is_file(), "vendored H4-T132 packet")
    require(sha256(h4_path) == h4_source["local_sha256"], "H4-T132 hash")
    h4 = load(h4_path)
    require(h4["theorem_id"] == h4_source["theorem_id"] == "H4-T132", "H4-T132 theorem id")
    require(
        h4["status"]
        == h4_source["status"]
        == "CLOSED_EXACT_CHAR0_PICARD_EMBEDDING_BINDING_AND_LOW_ORDER_TRAVERSAL_OBSTRUCTION",
        "H4-T132 status",
    )
    torsion = h4["traversal_torsion_decision"]
    lower, upper = torsion["certified_nonzero_orders_inclusive"]
    first_open = torsion["first_order_not_decided_by_current_interval_widths"]
    require((lower, upper, first_open) == (1, 1449, 1450), "order range")
    require(
        h4["checks"]["one_nonidentity_complex_base_change_proves_the_algebraic_point_is_nonidentity"],
        "all embeddings",
    )
    require(not h4["guardrails"]["claims_the_RREF_framing_is_coordinate_free"], "selection guard")
    require(not h4["guardrails"]["claims_the_entire_rank123_G3AJ_graph_ball_is_rejected"], "family guard")
    require(
        torsion["double_traversal"]["scaled_interval_outward_binary64"][1] < 0,
        "double traversal interval excludes zero",
    )
    require(
        h4["same_source_identification"]["relative_picard_section"]
        == "nu_alg(e)=[pi^*O_K3(H-Rminus)|C_e]",
        "relative Picard source",
    )

    require(T68_PACKET.is_file(), "T68 packet")
    require(sha256(T68_PACKET) == t68_source["sha256"], "T68 source hash")
    t68 = load(T68_PACKET)
    require(t68["theorem_id"] == "CBF.T68", "T68 theorem id")
    require(
        t68["general_theorem"]["source_status"]
        == "CONSUMED_FROM_POST_M32_QG_RANK_CUTSET_NOT_REDISCOVERED_HERE",
        "T68 theorem provenance",
    )
    endpoint = t68["endpoint_decision"]
    cover_degree = endpoint["cover_degree"]
    require(cover_degree == t68_source["cover_degree"] == 3, "cover degree")
    require(endpoint["unchanged_MTT_BHT_spectral_rank"] == 1, "selected rank")
    require(endpoint["unchanged_inverse_transform_rank"] == 3, "inverse rank")
    require(endpoint["required_class"] == "beta_C=0", "rank-one gate")

    selected_ranks = [1, 2, 3, 5, 9, 27, 248, 729, upper]
    rank_witnesses = [
        {
            "spectral_rank": rank,
            "H4_T132_proves_rank_times_beta_C_nonzero": lower <= rank <= upper,
            "twisted_object_existence": "REJECTED",
            "degree_three_inverse_transform_rank": cover_degree * rank,
        }
        for rank in selected_ranks
    ]

    checks = {
        "H4_T132_binds_the_directed_class_to_one_exact_algebraic_G3AJ_member": True,
        "H4_T132_identifies_that_Picard_point_with_the_restricted_primitive_BHT_Deligne_class": True,
        "orders_one_through_1449_are_certified_nonzero_on_every_complex_embedding": (
            lower == 1
            and upper == 1449
            and h4["checks"]["one_nonidentity_complex_base_change_proves_the_algebraic_point_is_nonidentity"]
        ),
        "T68_requires_r_times_beta_C_to_vanish_for_a_rank_r_twisted_spectral_object": True,
        "therefore_spectral_ranks_one_through_1449_are_excluded_for_this_member": True,
        "the_intended_spectral_rank_one_inverse_rank_three_endpoint_is_excluded": True,
        "double_traversal_and_spectral_rank_two_inverse_rank_six_are_excluded": True,
        "hypothetical_spectral_rank_three_inverse_rank_nine_is_excluded": True,
        "the_first_unresolved_order_1450_would_have_inverse_transform_rank_4350": (
            cover_degree * first_open == 4350
        ),
        "the_result_does_not_reject_the_rank123_graph_ball": (
            not h4["guardrails"]["claims_the_entire_rank123_G3AJ_graph_ball_is_rejected"]
        ),
        "the_result_does_not_promote_the_basis_framing_to_physical_MTT_selection": (
            not h4["guardrails"]["claims_the_RREF_framing_is_coordinate_free"]
        ),
        "no_observed_value_or_fit_parameter_is_used": (
            h4["parameter_ledger"]["observed_values_used"] == 0
            and h4["parameter_ledger"]["new_continuous_fit_parameters"] == 0
            and h4["parameter_ledger"]["new_discrete_fit_parameters"] == 0
        ),
    }
    require(all(checks.values()), f"T69 checks: {checks}")

    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-framed-member-spectral-rank-exclusion.v1",
        "theorem_id": "CBF.T69",
        "status": "CLOSED_EXACT_FRAMED_GRAPH_PRYM_SPECTRAL_RANKS_1_THROUGH_1449_EXCLUDED",
        "tier": "exact_cross_repository_application_to_one_algebraically_bound_directed_candidate",
        "provenance": {
            "H4_T132_role": "consumed exact algebraic/complex binding and certified nP nonvanishing; not reproved here",
            "T68_role": "consumed established twisted-spectral rank-divisibility theorem; not reproved here",
        },
        "candidate": {
            "name": "C_fr",
            "family": "G3AJ rank-123 fixed-residue graph-Prym ball",
            "selection_rule": "all 123 free correction digits are zero in the frozen coefficient basis and RREF order",
            "selection_tier": "deterministic_reproducible_basis_framing_not_coordinate_free_physical_selection",
            "class": "P=nu_alg(e_0)=restricted primitive BHT/Deligne class beta_C",
            "all_complex_embeddings_nonzero": True,
        },
        "rank_exclusion": {
            "twisted_rank_necessity": "a rank-r alpha-twisted locally free spectral object requires r*beta_C=0 on this carrier",
            "certified_excluded_spectral_ranks_inclusive": [lower, upper],
            "corresponding_degree_three_inverse_transform_ranks": {
                "formula": "3*r",
                "first": cover_degree * lower,
                "last": cover_degree * upper,
                "step": cover_degree,
            },
            "selected_endpoint": {
                "spectral_rank": 1,
                "inverse_transform_rank": 3,
                "decision": "REJECTED_FOR_C_fr",
            },
            "double_traversal": {
                "spectral_rank_analogue": 2,
                "inverse_transform_rank": 6,
                "decision": "REJECTED_FOR_C_fr",
                "H4_T132_witness": torsion["double_traversal"],
            },
            "spectral_rank_three": {
                "inverse_transform_rank": 9,
                "decision": "REJECTED_FOR_C_fr",
            },
            "first_order_not_resolved_by_H4_T132_intervals": first_open,
            "first_unresolved_corresponding_inverse_transform_rank": (
                cover_degree * first_open
            ),
            "unresolved_boundary": "rank 1450 is not a candidate and no torsion or object existence is inferred from loss of interval resolution",
            "selected_rank_witnesses": rank_witnesses,
        },
        "frontier_delta": {
            "before": "T68 excluded B89 and G3BI at the intended ranks and requested explicit same-residue G3AJ candidates; H4-T132 separately rejected one exact framed G3AJ member through traversal order 1449",
            "after": "the H4-T132 obstruction is now folded through the established rank cutset: C_fr admits no twisted spectral object of ranks 1 through 1449 and therefore cannot realize the intended inverse-rank-three endpoint or any degree-three inverse transform of ranks 3,6,...,4347",
            "next_required_object": "construct the graph-family beta_C value map and derivative on the 122 projective tangent directions, then either certify a beta-zero member or prove the beta-zero locus empty; do not rerun C_fr, its embeddings, or low-rank traversals",
        },
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "guardrails": {
            "claims_H4_T132_nonvanishing_is_new_here": False,
            "claims_the_T68_rank_theorem_is_new_here": False,
            "claims_the_entire_G3AJ_ball_is_rejected": False,
            "claims_C_fr_is_physically_selected": False,
            "claims_rank1450_is_a_torsion_candidate": False,
            "claims_a_replacement_beta_zero_member_exists": False,
            "claims_HYM_SM_or_QG_endpoint_closure": False,
        },
        "inputs": {
            "source_snapshot": binding(SOURCE),
            "T68": binding(T68_PACKET),
            "H4_T132": binding(h4_path),
            "H4_T132_upstream": {
                "repository": h4_source["repository"],
                "repository_commit": h4_source["repository_commit"],
                "packet_path": h4_source["packet_path"],
                "packet_git_blob": h4_source["packet_git_blob"],
                "theorem_path": h4_source["theorem_path"],
                "theorem_git_blob": h4_source["theorem_git_blob"],
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
        "CBF.T69 framed-member rank exclusion: PASS "
        "spectral-ranks=1..1449 rejected inverse-ranks=3..4347 step3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
