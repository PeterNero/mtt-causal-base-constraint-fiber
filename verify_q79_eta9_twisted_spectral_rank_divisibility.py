#!/usr/bin/env python3
"""Independently verify the CBF.T68 rank-divisibility packet."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_twisted_spectral_rank_divisibility.source.json"
PACKET = ROOT / "q79_eta9_twisted_spectral_rank_divisibility.packet.json"


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


def verify_table(
    table: list[dict[str, Any]], value: int, modulus: int, order: int
) -> None:
    require([row["rank"] for row in table] == list(range(1, 11)), "rank table")
    for row in table:
        rank = row["rank"]
        multiple = (rank * value) % modulus
        require(row["multiple"] == multiple, "residue multiple")
        require(
            row["necessary_component_condition_passes"] == (multiple == 0),
            "component condition",
        )
        require(
            row["known_quotient_order_divides_rank"] == (rank % order == 0),
            "order divisibility",
        )


def main() -> int:
    packet = load(PACKET)
    require(
        packet["schema"]
        == "mtt.cbf.q79-eta9-twisted-spectral-rank-divisibility.v1",
        "packet schema",
    )
    require(packet["theorem_id"] == "CBF.T68", "theorem id")
    claimed_hash = packet["canonical_payload_sha256"]
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_sha256(unsigned) == claimed_hash, "canonical payload hash")

    source = verify_binding(packet["inputs"]["source_snapshot"])
    require(source == load(SOURCE), "source replay")
    b89 = verify_binding(packet["inputs"]["B89"])
    t67 = verify_binding(packet["inputs"]["T67"])
    require(b89["Deligne_conclusion"]["beta_C_B89"] == "NONZERO", "B89")
    require(b89["certified_replay"]["witness_pairing_mod2"] == 1, "B89 parity")
    require(
        not b89["guardrails"]["claims_the_new_replay_proves_exact_order_two_over_Z"],
        "B89 order guard",
    )
    require(t67["theorem_id"] == "CBF.T67", "T67 binding")
    require(not t67["guardrails"]["physical_endpoint_selected_here"], "T67 guard")

    theorem = packet["general_theorem"]
    require(
        theorem["source_status"]
        == "CONSUMED_FROM_POST_M32_QG_RANK_CUTSET_NOT_REDISCOVERED_HERE",
        "established source status",
    )
    require("alpha_ijk^r" in theorem["determinant_law"], "determinant law")
    require("r[alpha]=0" in theorem["cohomology_consequence"], "cohomology law")
    require("iff [alpha]=0" in theorem["rank_one_equivalence"], "rank-one iff")

    b89_result = packet["B89_application"]
    verify_table(b89_result["rank_table_1_through_10"], 1, 2, 2)
    require(b89_result["conclusion_rank_one"] == "REJECTED", "B89 rank one")
    require(
        b89_result["conclusion_spectral_rank_three"] == "REJECTED",
        "B89 spectral rank three",
    )
    require(
        b89_result["first_spectral_rank_not_rejected_by_known_shadow"] == 2
        and b89_result["corresponding_inverse_transform_rank"] == 6,
        "B89 transformed rank",
    )
    require(not b89_result["exact_integral_order_known"], "B89 exact order open")

    g3bi_result = packet["G3BI_application"]
    component = g3bi_result["local_component"]
    modulus = 20
    order = modulus // math.gcd(component, modulus)
    require(order == g3bi_result["local_component_order"] == 5, "G3BI order")
    verify_table(g3bi_result["rank_table_1_through_10"], component, modulus, order)
    pairing_four = g3bi_result["pairing_four_root_component"]
    pairing_order = modulus // math.gcd(pairing_four, modulus)
    require(pairing_four == 16 and pairing_order == 5, "pairing-four order")
    verify_table(
        g3bi_result["pairing_four_rank_table_1_through_10"],
        pairing_four,
        modulus,
        pairing_order,
    )
    require(g3bi_result["conclusion_rank_one"] == "REJECTED", "G3BI rank one")
    require(
        g3bi_result["conclusion_spectral_rank_three"] == "REJECTED",
        "G3BI spectral rank three",
    )
    require(
        g3bi_result["first_spectral_rank_passing_the_local_component_test"] == 5
        and g3bi_result["corresponding_inverse_transform_rank"] == 15,
        "G3BI transformed rank",
    )

    endpoint = packet["endpoint_decision"]
    require(endpoint["unchanged_MTT_BHT_spectral_rank"] == 1, "endpoint rank")
    require(endpoint["cover_degree"] == 3, "cover degree")
    require(endpoint["unchanged_inverse_transform_rank"] == 3, "inverse rank")
    require(endpoint["required_class"] == "beta_C=0", "endpoint class")
    require(not endpoint["is_an_optional_selection_convention"], "derived gate")
    require(
        packet["T67_interpretation"]["physical_promotion"]
        == "FORBIDDEN_BY_THE_B89_RANK_ONE_ENDPOINT_SIEVE",
        "T67 nonpromotion",
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
        "CBF.T68 verification: PASS "
        "rank1=B89:REJECTED,G3BI:REJECTED "
        "spectral-rank3=B89:REJECTED,G3BI:REJECTED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
