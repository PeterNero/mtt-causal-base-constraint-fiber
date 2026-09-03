#!/usr/bin/env python3
"""Independently verify the corrected CBF.T69 scope packet."""

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
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
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
        packet["schema"] == "mtt.cbf.q79-eta9-framed-member-spectral-rank-scope.v2",
        "packet schema",
    )
    require(packet["theorem_id"] == "CBF.T69", "theorem id")
    require(packet["status"].startswith("CORRECTED_RETRACTION_"), "status")
    claimed_hash = packet["canonical_payload_sha256"]
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_sha256(unsigned) == claimed_hash, "canonical payload hash")

    source = verify_binding(packet["inputs"]["source_snapshot"])
    require(source == load(SOURCE), "source replay")

    t68 = verify_binding(packet["inputs"]["T68"])
    require(t68["theorem_id"] == "CBF.T68", "T68 theorem")
    require(t68["endpoint_decision"]["required_class"] == "beta_C=0", "T68 gate")
    require(
        "r[alpha]=0" in t68["general_theorem"]["cohomology_consequence"],
        "T68 determinant law",
    )

    h132 = verify_binding(packet["inputs"]["H4_T132"])
    require(h132["theorem_id"] == "H4-T132", "H4-T132 theorem")
    require(
        h132["traversal_torsion_decision"]["certified_nonzero_orders_inclusive"]
        == [1, 1449],
        "H4-T132 retained result",
    )

    h133 = verify_binding(packet["inputs"]["H4_T133"])
    require(h133["theorem_id"] == "H4-T133", "H4-T133 theorem")
    restriction = h133["fiber_evaluation_operator"]
    require(
        (restriction["domain_rank"], restriction["codomain_rank"], restriction["kernel_rank"])
        == (248, 82, 166),
        "H4-T133 quotient dimensions",
    )
    require(h133["frontier"]["beta_C_decision"] == "OPEN", "global beta open")
    require(
        "the fixed-fiber solve alone rejects the candidate from U_eta9"
        in h133["scope_correction"]["withdrawn_as_unproved"],
        "scope withdrawal",
    )

    ledger = packet["carrier_ledger"]
    require(ledger["fixed_fiber_picard_point"]["holomorphic_row_rank"] == 82, "fiber rank")
    require(ledger["global_BHT_class"]["primitive_surface_row_rank"] == 248, "surface rank")
    require(ledger["evaluation_quotient"]["kernel_rank"] == 166, "kernel rank")

    decision = packet["spectral_rank_decision"]
    require(
        decision["ranks_1_through_1449"]
        == "UNDECIDED_BY_THE_FIXED_FIBER_CALCULATION",
        "rank range reopened",
    )
    require(decision["selected_spectral_rank_one"] == "OPEN", "rank one open")
    require(decision["selected_inverse_transform_rank_three"] == "OPEN", "rank three open")
    require(
        decision["double_traversal_or_rank_two"] == "OPEN_AT_THE_GLOBAL_BHT_LEVEL",
        "double traversal open",
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
        "fixed-fiber-rank=82 global-rank=248 kernel=166 spectral-decision=OPEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
