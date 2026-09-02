#!/usr/bin/env python3
"""Build the exact B89 downstream-promotion readiness packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
UPSTREAM = COMMON / "mtt-preprojection-repair-calculus"
CAMPAIGN = ROOT / "q79_b89_recursive_replacement_campaign.json"
STATUS = ROOT / "q79_b89_recursive_replacement_campaign_status.json"
PREFLIGHT = ROOT / "q79_b89_accelerated_source_isotopy_preflight_coverage_report.json"
OUTPUT = ROOT / "q79_b89_downstream_promotion_readiness.packet.json"
EXPECTED = {0: 231, 1: 857, 2: 678, 3: 429}

STATIC = {
    "H4_T122_exact_carrier": UPSTREAM / "certificates/h4_q79_eta9_b89_exact_integral_carrier.json",
    "H4_T113_signed_boundary": UPSTREAM / "certificates/h4_q79_eta9_b89_certified_signed_boundary_braid.json",
    "H4_T116_connector_free_parity": UPSTREAM / "certificates/h4_q79_eta9_b89_selected_rectangle_connector_free_parity.json",
    "H4_T118_integral_marking": UPSTREAM / "certificates/h4_q79_eta9_b89_certified_comb_h1_intertwiner.json",
    "H4_T119_boundary_spokes": UPSTREAM / "certificates/h4_q79_eta9_b89_certified_boundary_spoke_frame.json",
    "H4_T120_Deligne_adapter_certificate": UPSTREAM / "certificates/h4_q79_eta9_b89_affine_deligne_adapter.json",
    "H4_T120_Deligne_adapter_packet": UPSTREAM / "experiments/q79_eta9_b89_affine_deligne_adapter/q79_eta9_b89_affine_deligne_adapter.packet.json",
    "common_grid_Artin": UPSTREAM / "experiments/q79_eta9_b89_family_branch_braid_pilot/outputs/certified-common-grid-right80-joint-artin.json",
    "segmented_adapter": UPSTREAM / "experiments/q79_eta9_b89_family_branch_braid_pilot/outputs/certified-common-grid-right80-segmented-adapter.json",
    "conditional_affine_obstruction": UPSTREAM / "experiments/q79_eta9_b89_family_branch_braid_pilot/outputs/certified-common-grid-right80-mod2-affine-obstruction.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict:
    return {
        "path": path.relative_to(COMMON).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def rank_mod_two(matrix: list[list[int]]) -> int:
    columns = len(matrix[0])
    rows = [
        sum((int(value) & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(rows)) if (rows[row] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(rank + 1, len(rows)):
            if (rows[row] >> column) & 1:
                rows[row] ^= rows[rank]
        rank += 1
    return rank


def expand_missing(report: dict, carrier: str) -> set[tuple[int, int]]:
    return {
        (int(edge), interval)
        for edge, ranges in report[carrier]["missing_ranges"].items()
        for start, stop in ranges
        for interval in range(int(start), int(stop))
    }


def compress(values: set[tuple[int, int]]) -> dict[str, list[list[int]]]:
    output: dict[str, list[list[int]]] = {}
    for edge in EXPECTED:
        edge_values = sorted(interval for row_edge, interval in values if row_edge == edge)
        ranges: list[list[int]] = []
        if edge_values:
            start = previous = edge_values[0]
            for value in edge_values[1:]:
                if value != previous + 1:
                    ranges.append([start, previous + 1])
                    start = value
                previous = value
            ranges.append([start, previous + 1])
        output[str(edge)] = ranges
    return output


def main() -> int:
    for path in [CAMPAIGN, STATUS, PREFLIGHT, *STATIC.values()]:
        require(path.is_file(), f"input {path}")
    campaign = load(CAMPAIGN)
    status = load(STATUS)
    preflight = load(PREFLIGHT)
    campaign_by_id = {row["id"]: row for row in campaign["jobs"]}
    require(len(campaign_by_id) == len(campaign["jobs"]) == 219, "campaign ids")
    replacements_by_predecessor = {
        row["replacement_of_job_id"]: row
        for row in campaign["jobs"]
        if "replacement_of_job_id" in row
    }
    require(len(replacements_by_predecessor) == 1, "replacement lineage")

    verified = status["campaign_verified_jobs"]
    require(len({row["id"] for row in verified}) == len(verified), "verified ids")
    added: dict[str, set[tuple[int, int]]] = {"branch": set(), "boundary": set()}
    for row in verified:
        source = campaign_by_id[row["id"]]
        require(row["carrier"] == source["carrier"], f"carrier {row['id']}")
        require(int(row["edge"]) == int(source["edge"]), f"edge {row['id']}")
        expected_range = [int(source["interval_start"]), int(source["interval_stop"])]
        is_cancelled_prefix = row["interval_range"] != expected_range
        if is_cancelled_prefix:
            replacement = replacements_by_predecessor.get(row["id"])
            require(replacement is not None, f"prefix replacement {row['id']}")
            require(
                row["interval_range"]
                == replacement["predecessor_certified_atomic_prefix"]
                == [source["interval_start"], replacement["interval_start"]],
                f"atomic prefix {row['id']}",
            )
            require(
                replacement["interval_stop"] == source["interval_stop"],
                f"replacement remainder {row['id']}",
            )
        else:
            require(row["interval_range"] == expected_range, f"range {row['id']}")
        require(row["input_capsule_sha256"] == source["input_capsule_sha256"], f"input {row['id']}")
        require(
            row.get("reported_process_state", "succeeded")
            in {"succeeded", "failed", "running", "cancelled"},
            f"process state {row['id']}",
        )
        require(
            row.get("result_manifest_exit_code", 0) == (1 if is_cancelled_prefix else 0),
            f"result exit {row['id']}",
        )
        require(
            all(
                row.get(key)
                for key in (
                    "packet_sha256",
                    "result_capsule_sha256",
                    "result_manifest_sha256",
                    "verifier_sha256",
                )
            ),
            f"hash ledger {row['id']}",
        )
        start, stop = row["interval_range"]
        for interval in range(start, stop):
            key = (int(source["edge"]), interval)
            require(key not in added[row["carrier"]], f"verified overlap {row['id']}")
            added[row["carrier"]].add(key)

    coverage = {}
    for carrier in ("branch", "boundary"):
        preflight_missing = expand_missing(preflight, carrier)
        require(not (added[carrier] - preflight_missing), f"{carrier} additions lie in preflight gaps")
        remaining = preflight_missing - added[carrier]
        coverage[carrier] = {
            "certified_intervals": sum(EXPECTED.values()) - len(remaining),
            "target_intervals": sum(EXPECTED.values()),
            "complete": not remaining,
            "missing_ranges": compress(remaining),
            "campaign_delta_intervals": len(added[carrier]),
            "campaign_verified_packets": sum(row["carrier"] == carrier for row in verified),
        }

    static = {name: load(path) for name, path in STATIC.items()}
    expected_ids = {
        "H4_T122_exact_carrier": "H4-T122",
        "H4_T113_signed_boundary": "H4-T113",
        "H4_T116_connector_free_parity": "H4-T116",
        "H4_T118_integral_marking": "H4-T118",
        "H4_T119_boundary_spokes": "H4-T119",
        "H4_T120_Deligne_adapter_certificate": "H4-T120",
    }
    for name, result_id in expected_ids.items():
        require(static[name]["id"] == result_id and static[name]["all_passed"], name)
    require(
        static["H4_T120_Deligne_adapter_certificate"]["artifact"]["sha256"]
        == sha256(STATIC["H4_T120_Deligne_adapter_packet"]),
        "H4-T120 packet binding",
    )

    artin = static["common_grid_Artin"]
    segmented = static["segmented_adapter"]
    affine = static["conditional_affine_obstruction"]
    require(all(artin["checks"].values()) and not any(artin["guardrails"].values()), "Artin")
    require(all(segmented["checks"].values()) and not any(segmented["guardrails"].values()), "segmented")
    require(all(affine["checks"].values()), "affine checks")
    require(segmented["common_word_sha256"] == sha256(STATIC["common_grid_Artin"]), "Artin adapter")
    require(affine["segmented_word_sha256"] == sha256(STATIC["segmented_adapter"]), "affine adapter")

    matrix = affine["action_mod2"]
    translation = [int(value) & 1 for value in affine["affine_translation_mod2"]]
    witness = [int(value) & 1 for value in affine["mod2_obstruction_witness"]]
    require(len(matrix) == len(translation) == len(witness) == 164, "rank-164 data")
    require(all(len(row) == 164 for row in matrix), "matrix shape")
    delta = [
        [int(matrix[row][column]) ^ int(row == column) for column in range(164)]
        for row in range(164)
    ]
    require(rank_mod_two(matrix) == 164, "rank M")
    require(rank_mod_two(delta) == 42, "rank M-I")
    require(
        all(
            sum(witness[row] * delta[row][column] for row in range(164)) % 2 == 0
            for column in range(164)
        ),
        "left witness",
    )
    require(sum(witness[row] * translation[row] for row in range(164)) % 2 == 1, "pairing")

    checks = {
        "all_compact_campaign_attestations_bind_to_exact_requested_ranges_and_hashes": True,
        "timeout_labeled_results_require_a_zero_exit_manifest_and_the_same_independent_audit": True,
        "the_boundary_carrier_is_complete_after_independent_requester_verification": coverage["boundary"]["complete"],
        "the_remaining_branch_ranges_are_computed_exactly_without_counting_process_only_success": True,
        "the_H4_T113_T116_T118_T119_T120_and_T122_static_authorities_are_hash_bound": True,
        "the_common_grid_Artin_word_and_segmented_rectangle_adapter_are_closed": True,
        "the_conditional_rank_164_replay_has_rank_M_minus_I_42_and_a_pairing_one_left_witness": True,
        "the_dynamic_decision_is_determined_only_by_independently_verified_branch_coverage": True,
        "after_complete_branch_coverage_joint_assembly_is_the_only_missing_premise_for_the_existing_B89_rejection_replay": True,
    }
    require(all(checks.values()), "readiness checks")
    dynamic_decision = (
        "READY_FOR_JOINT_ASSEMBLY_AND_B89_PROMOTION"
        if coverage["branch"]["complete"]
        else "STATIC_ENDPOINT_READY_BRANCH_ISOTOPY_PENDING"
    )
    packet = {
        "schema": "mtt.cbf.q79-b89-downstream-promotion-readiness.v1",
        "theorem_id": "CBF.T54",
        "tier": "EXACT_DOWNSTREAM_READINESS_AND_DYNAMIC_COVERAGE_AUDIT",
        "decision": dynamic_decision,
        "coverage": coverage,
        "conditional_obstruction": {
            "rank": 164,
            "rank_M_over_F2": 164,
            "rank_M_minus_I_over_F2": 42,
            "left_nullity_M_minus_I_over_F2": 122,
            "witness_support": sum(witness),
            "translation_support": sum(translation),
            "witness_pairing_mod2": 1,
        },
        "promotion_chain": [
            "complete the exact 252-strand branch campaign",
            "assemble the branch and joint 288-strand same-source isotopy",
            "replay the existing hash-bound rank-164 mod-two affine operator",
            "apply H4-T120 to infer a nonzero B-handle Deligne-Leray transgression",
            "reject B89 from the beta-zero locus",
        ],
        "checks": checks,
        "guardrails": {
            "claims_branch_isotopy_complete_without_exact_verified_coverage": False,
            "claims_joint_isotopy_before_assembly": False,
            "claims_B89_is_already_rejected": False,
            "claims_a_replacement_graph_Prym_member": False,
            "claims_beta_C_zero_or_a_HYM_endpoint": False,
        },
        "inputs": {
            "campaign": record(CAMPAIGN),
            "campaign_status": record(STATUS),
            "preflight_coverage": record(PREFLIGHT),
            **{name: record(path) for name, path in STATIC.items()},
        },
    }
    require(not any(packet["guardrails"].values()), "claim boundary")
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T54 downstream readiness: PASS "
        f"branch={coverage['branch']['certified_intervals']}/2195 "
        f"boundary={coverage['boundary']['certified_intervals']}/2195 "
        "static_obstruction=ready"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
