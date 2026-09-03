#!/usr/bin/env python3
"""Independently verify the CBF.T69 spectral-rank exclusion packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_framed_member_spectral_rank_exclusion.source.json"
PACKET = ROOT / "q79_eta9_framed_member_spectral_rank_exclusion.packet.json"


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


def verify_binding(binding: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / binding["path"]
    require(path.is_file(), f"bound file: {path}")
    require(path.stat().st_size == binding["bytes"], f"bound bytes: {path}")
    require(sha256(path) == binding["sha256"], f"bound hash: {path}")
    return load(path)


def main() -> int:
    packet = load(PACKET)
    require(
        packet["schema"]
        == "mtt.cbf.q79-eta9-framed-member-spectral-rank-exclusion.v1",
        "packet schema",
    )
    require(packet["theorem_id"] == "CBF.T69", "theorem id")
    claimed_hash = packet["canonical_payload_sha256"]
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_sha256(unsigned) == claimed_hash, "canonical payload hash")

    source = verify_binding(packet["inputs"]["source_snapshot"])
    require(source == load(SOURCE), "source replay")
    t68 = verify_binding(packet["inputs"]["T68"])
    require(t68["theorem_id"] == "CBF.T68", "T68 theorem")
    require(
        t68["endpoint_decision"]["cover_degree"] == 3
        and t68["endpoint_decision"]["unchanged_MTT_BHT_spectral_rank"] == 1
        and t68["endpoint_decision"]["unchanged_inverse_transform_rank"] == 3,
        "T68 endpoint",
    )
    require(
        "r[alpha]=0" in t68["general_theorem"]["cohomology_consequence"],
        "rank-divisibility law",
    )

    h4_source = source["sources"]["H4_T132"]
    h4 = verify_binding(packet["inputs"]["H4_T132"])
    require(h4["theorem_id"] == "H4-T132", "H4 theorem")
    require(
        h4["traversal_torsion_decision"]["certified_nonzero_orders_inclusive"]
        == [1, 1449],
        "H4 order range",
    )
    require(
        h4["traversal_torsion_decision"]
        ["first_order_not_decided_by_current_interval_widths"]
        == 1450,
        "H4 first open order",
    )
    require(
        h4["checks"]["one_nonidentity_complex_base_change_proves_the_algebraic_point_is_nonidentity"],
        "H4 embeddings",
    )
    require(not h4["guardrails"]["claims_the_RREF_framing_is_coordinate_free"], "H4 selection")
    require(not h4["guardrails"]["claims_the_entire_rank123_G3AJ_graph_ball_is_rejected"], "H4 family guard")
    require(
        sha256(ROOT / h4_source["local_path"]) == h4_source["local_sha256"],
        "source H4 binding",
    )

    rank = packet["rank_exclusion"]
    require(
        rank["certified_excluded_spectral_ranks_inclusive"] == [1, 1449],
        "excluded ranks",
    )
    inverse = rank["corresponding_degree_three_inverse_transform_ranks"]
    require(
        inverse == {"first": 3, "formula": "3*r", "last": 4347, "step": 3},
        "inverse ranks",
    )
    require(
        rank["selected_endpoint"]
        == {
            "decision": "REJECTED_FOR_C_fr",
            "inverse_transform_rank": 3,
            "spectral_rank": 1,
        },
        "selected endpoint",
    )
    require(
        rank["double_traversal"]["spectral_rank_analogue"] == 2
        and rank["double_traversal"]["inverse_transform_rank"] == 6
        and rank["double_traversal"]["decision"] == "REJECTED_FOR_C_fr",
        "double traversal",
    )
    require(
        rank["spectral_rank_three"]["inverse_transform_rank"] == 9
        and rank["spectral_rank_three"]["decision"] == "REJECTED_FOR_C_fr",
        "rank three",
    )
    require(
        rank["first_order_not_resolved_by_H4_T132_intervals"] == 1450
        and rank["first_unresolved_corresponding_inverse_transform_rank"] == 4350,
        "resolution boundary",
    )
    for witness in rank["selected_rank_witnesses"]:
        spectral_rank = witness["spectral_rank"]
        require(1 <= spectral_rank <= 1449, "witness range")
        require(
            witness["H4_T132_proves_rank_times_beta_C_nonzero"],
            "witness nonzero",
        )
        require(witness["twisted_object_existence"] == "REJECTED", "witness")
        require(
            witness["degree_three_inverse_transform_rank"] == 3 * spectral_rank,
            "witness inverse rank",
        )

    require(packet["all_checks_pass"] and all(packet["checks"].values()), "checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    require(
        packet["parameter_ledger"]
        == {
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "observed_values_used": 0,
        },
        "parameter ledger",
    )

    print(
        "CBF.T69 verification: PASS "
        "spectral-ranks=1..1449 rejected inverse-ranks=3..4347 step3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
