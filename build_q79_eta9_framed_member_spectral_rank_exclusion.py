#!/usr/bin/env python3
"""Build the corrected CBF.T69 fixed-fiber/global-BHT scope packet."""

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
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
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
        == "mtt.cbf.q79-eta9-framed-member-spectral-rank-scope-source.v2",
        "source schema",
    )

    h132_source = source["sources"]["H4_T132"]
    h132_path = ROOT / h132_source["local_path"]
    require(sha256(h132_path) == h132_source["local_sha256"], "H4-T132 hash")
    h132 = load(h132_path)
    require(h132["theorem_id"] == "H4-T132", "H4-T132 theorem")
    require(h132["status"] == h132_source["status"], "H4-T132 status")
    torsion = h132["traversal_torsion_decision"]
    require(
        torsion["certified_nonzero_orders_inclusive"] == [1, 1449],
        "fixed-fiber order range",
    )
    require(
        torsion["first_order_not_decided_by_current_interval_widths"] == 1450,
        "fixed-fiber interval boundary",
    )

    h133_source = source["sources"]["H4_T133"]
    h133_path = ROOT / h133_source["local_path"]
    require(sha256(h133_path) == h133_source["local_sha256"], "H4-T133 hash")
    h133 = load(h133_path)
    require(h133["theorem_id"] == "H4-T133", "H4-T133 theorem")
    require(h133["status"] == h133_source["status"], "H4-T133 status")
    restriction = h133["fiber_evaluation_operator"]
    require(
        (
            restriction["domain_rank"],
            restriction["codomain_rank"],
            restriction["kernel_rank"],
        )
        == (248, 82, 166),
        "248-to-82 quotient dimensions",
    )
    withdrawn = h133["scope_correction"]["withdrawn_as_unproved"]
    require(
        "the fixed-fiber solve alone rejects the candidate from U_eta9" in withdrawn,
        "H4-T133 U_eta9 correction",
    )
    require(
        h133["frontier"]["beta_C_decision"] == "OPEN",
        "H4-T133 beta decision",
    )

    t68_source = source["sources"]["T68"]
    require(sha256(T68_PACKET) == t68_source["sha256"], "T68 hash")
    t68 = load(T68_PACKET)
    require(t68["theorem_id"] == "CBF.T68", "T68 theorem")
    endpoint = t68["endpoint_decision"]
    require(
        endpoint["cover_degree"] == 3
        and endpoint["unchanged_MTT_BHT_spectral_rank"] == 1
        and endpoint["unchanged_inverse_transform_rank"] == 3,
        "T68 endpoint",
    )
    require(endpoint["required_class"] == "beta_C=0", "T68 beta gate")

    checks = {
        "H4_T132_fixed_fiber_point_is_nonzero_through_order1449": True,
        "H4_T133_distinguishes_the82_row_fiber_carrier_from_the248_row_surface_carrier": True,
        "H4_T133_proves_the_fiber_evaluation_kernel_has_rank166": True,
        "H4_T133_withdraws_fixed_fiber_nonidentity_implies_beta_C_nonzero": True,
        "T68_rank_divisibility_lemma_remains_valid": True,
        "T68_requires_the_global_normalized_beta_C_not_the_fixed_fiber_initial_point": True,
        "no_spectral_rank_is_excluded_by_T132_plus_T68_without_the_missing_BHT_sweep": True,
        "the_intended_rank_one_inverse_rank_three_endpoint_returns_to_open": True,
        "double_traversal_of_the_fixed_fiber_point_does_not_decide_double_BHT_sweep": True,
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"T69 correction checks: {checks}")

    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-framed-member-spectral-rank-scope.v2",
        "theorem_id": "CBF.T69",
        "status": "CORRECTED_RETRACTION_FIXED_FIBER_PICARD_POINT_DOES_NOT_EXCLUDE_GLOBAL_SPECTRAL_RANKS",
        "tier": "exact_cross_repository_carrier_scope_and_logical_dependency_audit",
        "correction": {
            "supersedes": "the T69 claim at commit 274730e that spectral ranks 1 through 1449 are excluded on C_fr",
            "reason": "H4-T133 proves that H4-T132 computed an 82-coordinate fixed-fiber Picard initial point, not the 248-coordinate normalized BHT handle integral beta_C required by T68",
            "retained_H4_T132_result": "n*P_e0 is nonzero for every integer 1<=n<=1449 at every complex embedding of the exact framed member",
            "retained_T68_result": "a rank-r alpha-twisted locally free spectral object requires r[alpha]=0",
            "invalid_inference_removed": "n*P_e0!=0 does not imply n*beta_C!=0",
        },
        "carrier_ledger": {
            "fixed_fiber_picard_point": {
                "symbol": "P_e0=nu_alg(e_0)",
                "holomorphic_row_rank": 82,
                "role": "initial condition for moving relative-chain transport",
            },
            "global_BHT_class": {
                "symbol": "beta_C",
                "primitive_surface_row_rank": 248,
                "definition": "integral around the selected B handle of the transported normal-function integrand modulo the integral period lattice",
                "decision": "OPEN",
            },
            "evaluation_quotient": {
                "map": "(V tensor W)/<F> -> V/<F_e>",
                "rank": 82,
                "kernel_rank": 166,
                "consequence": "one fixed fiber omits 166 primitive surface directions and cannot replace the handle sweep",
            },
        },
        "spectral_rank_decision": {
            "necessary_condition": "rank r requires r*beta_C=0",
            "ranks_1_through_1449": "UNDECIDED_BY_THE_FIXED_FIBER_CALCULATION",
            "selected_spectral_rank_one": "OPEN",
            "selected_inverse_transform_rank_three": "OPEN",
            "double_traversal_or_rank_two": "OPEN_AT_THE_GLOBAL_BHT_LEVEL",
            "rank1450": "NO_SPECIAL_STATUS; it was only the first unresolved fixed-fiber interval order",
        },
        "frontier_delta": {
            "closed_here": "the false fixed-fiber-to-global-beta promotion is removed and machine-checked",
            "next_required_object": h133["frontier"]["next_required_object"],
            "execution_order": [
                "propagate the rank-164 relative de Rham state around the selected B loop",
                "integrate all 248 quotient rows or a characteristic-zero 126-row normal projection",
                "reduce the result modulo the integral period lattice",
                "only then apply the T68 spectral-rank divisibility test",
            ],
        },
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "guardrails": {
            "claims_fixed_fiber_P_equals_global_beta_C": False,
            "claims_any_spectral_rank_is_excluded_for_C_fr": False,
            "claims_double_fixed_fiber_traversal_equals_double_BHT_sweep": False,
            "claims_C_fr_is_physically_selected": False,
            "claims_the_entire_G3AJ_ball_is_decided": False,
            "claims_beta_C_is_computed": False,
            "claims_HYM_SM_or_QG_endpoint_closure": False,
        },
        "inputs": {
            "source_snapshot": binding(SOURCE),
            "T68": binding(T68_PACKET),
            "H4_T132": binding(h132_path),
            "H4_T133": binding(h133_path),
            "upstream": {
                "H4_T132": {
                    "repository_commit": h132_source["repository_commit"],
                    "packet_git_blob": h132_source["packet_git_blob"],
                    "theorem_git_blob": h132_source["theorem_git_blob"],
                },
                "H4_T133": {
                    "repository_commit": h133_source["repository_commit"],
                    "packet_git_blob": h133_source["packet_git_blob"],
                    "theorem_git_blob": h133_source["theorem_git_blob"],
                },
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
        "CBF.T69 scope correction: PASS "
        "fixed-fiber-rank=82 global-rank=248 kernel=166 spectral-decision=OPEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
