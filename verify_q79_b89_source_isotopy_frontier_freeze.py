#!/usr/bin/env python3
"""Verify the portable freeze of the live B89 source-isotopy frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def newline_portable_sha256_matches(path: Path, expected: str) -> bool:
    """Accept the frozen text payload with either LF or CRLF transport bytes."""
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        return False
    variants = (raw, normalized, normalized.replace(b"\n", b"\r\n"))
    return any(hashlib.sha256(value).hexdigest() == expected for value in variants)


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="ascii"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def local_hash(entry: dict) -> bool:
    path = ROOT / entry["path"]
    return path.is_file() and sha256(path) == entry["sha256"]


def interval_union(rows: list[dict], carrier: str) -> tuple[dict[int, set[int]], bool]:
    covered: dict[int, set[int]] = {}
    overlap = False
    for row in rows:
        if row["carrier"] != carrier:
            continue
        edge = int(row["edge"])
        target = covered.setdefault(edge, set())
        for interval in range(int(row["interval_start"]), int(row["interval_stop"])):
            overlap = overlap or interval in target
            target.add(interval)
    return covered, overlap


def missing_union(coverage: dict, carrier: str) -> dict[int, set[int]]:
    output = {
        int(edge): {
            interval
            for start, stop in ranges
            for interval in range(int(start), int(stop))
        }
        for edge, ranges in coverage[carrier]["missing_ranges"].items()
    }
    return {edge: intervals for edge, intervals in output.items() if intervals}


def main() -> None:
    checks = {}
    branch_lock = load("q79_b89_accelerated_adaptive_source_isotopy_source_lock.json")
    boundary_lock = load("q79_b89_recursive_boundary_isotopy_source_lock.json")
    branch_verification = load(
        "q79_b89_accelerated_adaptive_source_isotopy_pilot_verification.packet.json"
    )
    cross_verification = load(
        "q79_b89_accelerated_adaptive_source_isotopy_cross_edge_verification.packet.json"
    )
    boundary_verification = load(
        "q79_b89_recursive_boundary_isotopy_pilot_verification.packet.json"
    )
    result_index = load("q79_b89_accelerated_source_isotopy_result_index.json")
    campaign = load("q79_b89_recursive_replacement_campaign.json")
    coverage = load(campaign["source_locks"]["preflight_coverage"]["path"])

    checks["branch_worker_and_verifier_hashes"] = all(
        local_hash(branch_lock[key])
        for key in ("adaptive_worker", "accelerated_cell_worker", "independent_verifier")
    )
    checks["boundary_worker_and_verifier_hashes"] = all(
        local_hash(boundary_lock[key])
        for key in (
            "recursive_worker",
            "direct_affine_cell_worker",
            "independent_verifier",
        )
    )

    branch_packets = [branch_lock["pilot"], *branch_lock["cross_edge_pilots"]]
    checks["all_branch_pilot_packet_hashes"] = all(
        sha256(ROOT / row["packet_path"]) == row["packet_sha256"]
        for row in branch_packets
    )
    checks["boundary_pilot_packet_hash"] = (
        sha256(ROOT / boundary_lock["pilot"]["packet_path"])
        == boundary_lock["pilot"]["packet_sha256"]
    )
    checks["boundary_cell_witness_hash"] = (
        sha256(ROOT / boundary_verification["cell_witness"]["path"])
        == boundary_verification["cell_witness"]["sha256"]
    )

    checks["requester_verification_packets_are_closed"] = (
        branch_verification["all_passed"]
        and all(branch_verification["checks"].values())
        and cross_verification["all_passed"]
        and all(cross_verification["checks"].values())
        and boundary_verification["all_passed"]
        and all(boundary_verification["checks"].values())
    )

    for row in result_index["jobs"]:
        packet_path = ROOT.parent / row["packet_path"]
        require(packet_path.is_file(), f"indexed packet {row['id']}")
        require(sha256(packet_path) == row["packet_sha256"], f"indexed hash {row['id']}")
        verification = row["independent_verification"]
        require(verification["passed"] is True, f"indexed verification {row['id']}")
        require(
            verification["packet_sha256"] == row["packet_sha256"],
            f"indexed verification hash {row['id']}",
        )
        packet = json.loads(packet_path.read_text(encoding="ascii"))
        require(all(packet["checks"].values()) and not packet["failures"], f"packet checks {row['id']}")
        require(packet["interval_range"] == row["interval_range"], f"packet range {row['id']}")
        require(packet["edge"] == row["edge"], f"packet edge {row['id']}")
    checks["result_index_is_hash_verified"] = True

    boundary_packet = load("q79_b89_recursive_boundary_isotopy_pilot.packet.json")
    direct_certificates = [
        cell["direct_homotopy_certificate"]
        for cell in boundary_packet["logical_rows"][0]["subcells"]
        if cell["direct_homotopy_certificate"]["direct_affine_segment_pairs"]
    ]
    checks["direct_affine_segment_margins_are_strict"] = (
        len(direct_certificates) == boundary_lock["pilot"]["direct_affine_segment_pairs"]
        and all(
            row["minimum_direct_alignment_margin"] > 0
            for row in direct_certificates
        )
    )
    checks["nonpromotion_scope_is_frozen"] = (
        not branch_lock["guardrails"][
            "claims_affine_Deligne_rejection_or_graph_Prym_selection"
        ]
        and not boundary_lock["guardrails"]["claims_complete_boundary_or_joint_isotopy"]
        and not boundary_lock["guardrails"][
            "claims_affine_Deligne_rejection_or_graph_Prym_selection"
        ]
    )

    campaign_jobs = campaign["jobs"]
    checks["replacement_campaign_source_locks_and_job_counts"] = (
        campaign["schema"] == "mtt.cbf.q79-b89-recursive-replacement-campaign.v1"
        and campaign["dispatch"]["active_job_count"] == len(campaign_jobs) == 218
        and campaign["dispatch"]["branch_job_count"]
        == sum(row["carrier"] == "branch" for row in campaign_jobs)
        == 153
        and campaign["dispatch"]["boundary_job_count"]
        == sum(row["carrier"] == "boundary" for row in campaign_jobs)
        == 65
        and newline_portable_sha256_matches(
            ROOT / campaign["source_locks"]["branch"]["path"],
            campaign["source_locks"]["branch"]["sha256"],
        )
        and newline_portable_sha256_matches(
            ROOT / campaign["source_locks"]["boundary"]["path"],
            campaign["source_locks"]["boundary"]["sha256"],
        )
        and newline_portable_sha256_matches(
            ROOT / campaign["source_locks"]["result_index"]["path"],
            campaign["source_locks"]["result_index"]["sha256"],
        )
        and newline_portable_sha256_matches(
            ROOT / campaign["source_locks"]["preflight_coverage"]["path"],
            campaign["source_locks"]["preflight_coverage"]["sha256"],
        )
    )

    branch_requested, branch_overlap = interval_union(campaign_jobs, "branch")
    boundary_requested, boundary_overlap = interval_union(campaign_jobs, "boundary")
    checks["replacement_campaign_exact_missing_interval_union"] = (
        not branch_overlap
        and not boundary_overlap
        and branch_requested == missing_union(coverage, "branch")
        and boundary_requested == missing_union(coverage, "boundary")
        and sum(map(len, branch_requested.values())) == 1817
        and sum(map(len, boundary_requested.values())) == 255
    )
    checks["replacement_campaign_nonpromotion_guardrail"] = (
        campaign["guardrails"]["process_success_is_not_theorem_promotion"]
        and campaign["guardrails"][
            "no_job_counts_as_coverage_before_result_download_and_independent_verification"
        ]
        and campaign["guardrails"][
            "complete_branch_and_boundary_coverage_are_required_before_joint_assembly"
        ]
        and campaign["guardrails"][
            "this_manifest_does_not_claim_B89_rejection_or_beta_C"
        ]
    )

    failed = [name for name, passed in checks.items() if not passed]
    require(not failed, f"B89 source-isotopy frontier freeze failed: {failed}")
    print(
        json.dumps(
            {
                "checks": checks,
                "passed": sum(checks.values()),
                "total": len(checks),
                "all_passed": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
