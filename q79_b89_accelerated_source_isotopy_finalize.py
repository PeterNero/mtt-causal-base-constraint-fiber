#!/usr/bin/env python3
"""Reconcile verified T53 result capsules and run the exact assemblers."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CAMPAIGN_PATH = ROOT / "q79_b89_accelerated_source_isotopy_campaign.json"
MIXED_BRANCH_PATH = ROOT / "q79_b89_accelerated_source_isotopy_mixed_campaign.json"
MIXED_BOUNDARY_PATH = ROOT / "q79_b89_accelerated_source_isotopy_boundary_campaign.json"
MIXED_REPAIR_PATH = ROOT / "q79_b89_accelerated_source_isotopy_boundary_repair_campaign.json"
ADAPTED_SIGNED_PATH = ROOT / "q79_b89_accelerated_source_isotopy_signed_boundary_adapter.json"
BRANCH_AGGREGATE_PATH = ROOT / "q79_b89_accelerated_source_isotopy_branch_aggregate.json"
BOUNDARY_AGGREGATE_PATH = ROOT / "q79_b89_accelerated_source_isotopy_boundary_aggregate.json"
JOINT_AGGREGATE_PATH = ROOT / "q79_b89_accelerated_source_isotopy_joint_aggregate.json"
COVERAGE_REPORT_PATH = ROOT / "q79_b89_accelerated_source_isotopy_coverage_report.json"
EXPECTED_INTERVALS = {0: 231, 1: 857, 2: 678, 3: 429}
BRANCH_SCHEMAS = {
    "mtt.preprojection.q79-eta9-b89-family-taylor-krawczyk.v1",
    "mtt.preprojection.q79-eta9-b89-adaptive-family-taylor-krawczyk.v1",
}
BOUNDARY_SCHEMAS = {
    "mtt.preprojection.q79-eta9-b89-boundary-taylor-krawczyk.v1",
    "mtt.preprojection.q79-eta9-b89-adaptive-boundary-taylor-krawczyk.v1",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="ascii"))


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="ascii")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def prefixed_upstream_path(path: str, upstream_name: str) -> str:
    return f"{upstream_name}/{path.replace('\\', '/')}"


def packet_carrier(schema: str) -> str:
    if schema in BRANCH_SCHEMAS:
        return "branch"
    if schema in BOUNDARY_SCHEMAS:
        return "boundary"
    raise AssertionError(f"unsupported result packet schema {schema}")


def result_path(common_root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    require(not candidate.is_absolute(), "portable relative result packet path")
    resolved = (common_root / candidate).resolve()
    try:
        resolved.relative_to(common_root.resolve())
    except ValueError as error:
        raise AssertionError("result packet remains under the common repository root") from error
    return resolved


def validated_result_job(
    result: dict,
    common_root: Path,
    expected_source_sha256: dict[str, str],
) -> tuple[str, dict]:
    path = result_path(common_root, result["packet_path"])
    require(path.is_file(), f"result packet {result['id']}")
    payload_sha256 = sha256(path)
    require(payload_sha256 == result["packet_sha256"], f"result hash {result['id']}")

    verification = result.get("independent_verification") or {}
    require(verification.get("passed") is True, f"independent verification {result['id']}")
    require(
        verification.get("packet_sha256") == payload_sha256,
        f"verification hash {result['id']}",
    )
    require(bool(verification.get("verifier")), f"verification command {result['id']}")

    packet = load(path)
    carrier = packet_carrier(packet["schema"])
    require(all(packet["checks"].values()) and not packet["failures"], f"packet checks {result['id']}")
    require(
        packet["source_sha256"] == expected_source_sha256[carrier],
        f"same-source hash {result['id']}",
    )
    edge = int(packet["edge"])
    require(edge in EXPECTED_INTERVALS, f"edge {result['id']}")
    interval_range = [int(value) for value in packet["interval_range"]]
    start, stop = interval_range
    require(0 <= start < stop <= EXPECTED_INTERVALS[edge], f"interval range {result['id']}")
    rows = packet.get("logical_rows") or packet.get("rows") or []
    require(len(rows) == stop - start, f"packet row count {result['id']}")
    require(
        all(int(row["interval"]) == start + offset for offset, row in enumerate(rows)),
        f"packet row order {result['id']}",
    )

    if carrier == "branch":
        require(packet["branch_range"] == [0, 252], f"branch carrier {result['id']}")
    if "requested_interval_range" in packet:
        requested_start, requested_stop = packet["requested_interval_range"]
        require(requested_start == start and stop <= requested_stop, f"checkpoint prefix {result['id']}")
        checkpoint = packet["checkpoint"]
        require(checkpoint["certified_interval_count"] == len(rows), f"checkpoint count {result['id']}")
        require(checkpoint["next_interval"] == stop, f"checkpoint next interval {result['id']}")
        require(checkpoint["atomic_replace"] is True, f"atomic checkpoint {result['id']}")
        require(
            checkpoint["complete_requested_range"] == (stop == requested_stop),
            f"checkpoint completion {result['id']}",
        )

    if "carrier" in result:
        require(result["carrier"] == carrier, f"index carrier {result['id']}")
    if "edge" in result:
        require(int(result["edge"]) == edge, f"index edge {result['id']}")
    if "interval_range" in result:
        require(result["interval_range"] == interval_range, f"index range {result['id']}")

    return carrier, {
        "id": result["id"],
        "edge": edge,
        "interval_range": interval_range,
        "observed_state": "succeeded",
        "assigned_agent": result.get("assigned_agent") or "",
        "retrieved_path": result["packet_path"].replace("\\", "/"),
        "retrieved_payload_sha256": payload_sha256,
        "packet_schema": packet["schema"],
        "independent_verification": verification,
        "checkpoint_complete": packet.get("checkpoint", {}).get(
            "complete_requested_range", True
        ),
    }


def compress_missing(values: list[int]) -> list[list[int]]:
    if not values:
        return []
    ranges = []
    start = previous = values[0]
    for value in values[1:]:
        if value != previous + 1:
            ranges.append([start, previous + 1])
            start = value
        previous = value
    ranges.append([start, previous + 1])
    return ranges


def coverage_report(jobs: list[dict], carrier: str) -> dict:
    occupied: dict[tuple[int, int], str] = {}
    for job in jobs:
        start, stop = job["interval_range"]
        edge = int(job["edge"])
        require(edge in EXPECTED_INTERVALS, f"{carrier} edge")
        require(0 <= start < stop <= EXPECTED_INTERVALS[edge], f"{carrier} range")
        for interval in range(start, stop):
            key = (edge, interval)
            require(key not in occupied, f"{carrier} overlap at edge {edge} interval {interval}")
            occupied[key] = job["id"]
    missing = {
        str(edge): compress_missing(
            [interval for interval in range(count) if (edge, interval) not in occupied]
        )
        for edge, count in EXPECTED_INTERVALS.items()
    }
    complete = all(not ranges for ranges in missing.values())
    return {
        "carrier": carrier,
        "complete": complete,
        "certified_intervals": len(occupied),
        "target_intervals": sum(EXPECTED_INTERVALS.values()),
        "shards": len(jobs),
        "missing_ranges": missing,
    }


def adapt_paths(value, upstream_name: str):
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            if key == "path" and isinstance(item, str) and not Path(item).is_absolute():
                output[key] = prefixed_upstream_path(item, upstream_name)
            else:
                output[key] = adapt_paths(item, upstream_name)
        return output
    if isinstance(value, list):
        return [adapt_paths(item, upstream_name) for item in value]
    return value


def build_campaigns(
    upstream_root: Path,
    result_index_path: Path,
    allow_incomplete: bool = False,
) -> dict:
    common_root = upstream_root.parent
    upstream_name = upstream_root.name
    index_packet = load(result_index_path)
    result_rows = index_packet["jobs"]
    require(len({row["id"] for row in result_rows}) == len(result_rows), "unique result ids")
    campaign = load(CAMPAIGN_PATH)

    upstream_branch_path = (
        upstream_root
        / "experiments/q79_eta9_b89_family_branch_braid_pilot/"
        "kernel_adaptive_taylor_family_campaign.json"
    )
    upstream_branch = load(upstream_branch_path)
    boundary_source_path = (
        upstream_root
        / "experiments/q79_eta9_b89_branch_forms/"
        "q79_eta9_b89_branch_form_worker_input.json"
    )
    expected_source_sha256 = {
        "branch": campaign["source_sha256"],
        "boundary": sha256(boundary_source_path),
    }
    new_jobs = {"branch": [], "boundary": []}
    for row in result_rows:
        carrier, job = validated_result_job(row, common_root, expected_source_sha256)
        new_jobs[carrier].append(job)

    existing_branch_jobs = []
    for row in upstream_branch["jobs"]:
        if row.get("observed_state") != "succeeded":
            continue
        copied = dict(row)
        copied["retrieved_path"] = prefixed_upstream_path(
            row["retrieved_path"], upstream_name
        )
        existing_branch_jobs.append(copied)
    branch_jobs = [*existing_branch_jobs, *new_jobs["branch"]]
    branch_coverage = coverage_report(branch_jobs, "branch")
    mixed_branch = {
        "schema": "mtt.cbf.q79-b89-mixed-exact-source-campaign.v1",
        "campaign_set": "adaptive",
        "all_jobs_observed": branch_coverage["complete"],
        "source_campaign_sha256": sha256(CAMPAIGN_PATH),
        "upstream_campaign_sha256": sha256(upstream_branch_path),
        "coverage": branch_coverage,
        "jobs": sorted(
            branch_jobs, key=lambda row: (row["edge"], row["interval_range"][0])
        ),
    }
    write(MIXED_BRANCH_PATH, mixed_branch)

    upstream_boundary_path = (
        upstream_root
        / "experiments/q79_eta9_b89_family_branch_braid_pilot/"
        "kernel_boundary_taylor_campaign.json"
    )
    upstream_boundary = load(upstream_boundary_path)
    boundary_jobs = []
    excluded_boundary_jobs = []
    for row in upstream_boundary["jobs"]:
        if row.get("observed_state") == "succeeded":
            copied = dict(row)
            copied["retrieved_path"] = prefixed_upstream_path(
                row["retrieved_path"], upstream_name
            )
            boundary_jobs.append(copied)
        else:
            excluded_boundary_jobs.append(row["id"])
    boundary_jobs.extend(new_jobs["boundary"])
    boundary_coverage = coverage_report(boundary_jobs, "boundary")
    mixed_boundary = dict(upstream_boundary)
    mixed_boundary["jobs"] = sorted(
        boundary_jobs, key=lambda row: (row["edge"], row["interval_range"][0])
    )
    mixed_boundary["all_jobs_observed"] = boundary_coverage["complete"]
    mixed_boundary["source_campaign_sha256"] = sha256(upstream_boundary_path)
    mixed_boundary["coverage"] = boundary_coverage
    mixed_boundary["excluded_unsuccessful_original_job_ids"] = sorted(excluded_boundary_jobs)
    write(MIXED_BOUNDARY_PATH, mixed_boundary)

    mixed_repair = {
        "schema": "mtt.cbf.q79-b89-boundary-repair-campaign.v1",
        "all_jobs_observed": True,
        "source_campaign_sha256": sha256(upstream_boundary_path),
        "replacement_packets_are_in_mixed_boundary_campaign": True,
        "jobs": [],
    }
    write(MIXED_REPAIR_PATH, mixed_repair)

    signed_path = upstream_root / "certificates/h4_q79_eta9_b89_certified_signed_boundary_braid.json"
    signed = adapt_paths(load(signed_path), upstream_name)
    signed["common_root_adapter"] = {
        "original_path": prefixed_upstream_path(
            "certificates/h4_q79_eta9_b89_certified_signed_boundary_braid.json",
            upstream_name,
        ),
        "original_sha256": sha256(signed_path),
        "semantic_change": False,
        "path_prefix_only": True,
    }
    write(ADAPTED_SIGNED_PATH, signed)

    report = {
        "schema": "mtt.cbf.q79-b89-flexible-result-coverage.v1",
        "result_index_path": str(result_index_path),
        "result_index_sha256": sha256(result_index_path),
        "branch": branch_coverage,
        "boundary": boundary_coverage,
        "complete": branch_coverage["complete"] and boundary_coverage["complete"],
        "guardrails": {
            "packet_interval_ranges_are_authoritative": True,
            "partial_atomic_checkpoints_count_only_their_certified_prefix": True,
            "overlap_is_rejected": True,
            "complete_coverage_is_required_before_assembly": True,
            "claims_affine_Deligne_rejection": False,
        },
    }
    write(COVERAGE_REPORT_PATH, report)
    require(report["complete"] or allow_incomplete, "branch and boundary coverage complete")
    return report


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_main(module, arguments: list[str]) -> None:
    original = sys.argv
    try:
        sys.argv = [str(Path(module.__file__).resolve()), *arguments]
        code = module.main()
    finally:
        sys.argv = original
    require(code == 0, f"assembler {module.__name__}")


def assemble(upstream_root: Path) -> None:
    common_root = upstream_root.parent
    pilot = upstream_root / "experiments/q79_eta9_b89_family_branch_braid_pilot"
    sys.path.insert(0, str(pilot))

    branch = load_module("t53_branch_assembler", pilot / "assemble_taylor_family_campaign.py")
    branch.ROOT = common_root
    run_main(
        branch,
        [
            "--campaign",
            str(MIXED_BRANCH_PATH),
            "--artin",
            str(pilot / "outputs/family-global-right80-plus-artin.json"),
            "--exact-carrier",
            str(
                upstream_root
                / "experiments/q79_eta9_b89_moving_branch_polynomial/"
                "exact_integral_carrier.aggregate.json"
            ),
            "--exact-carrier-certificate",
            str(upstream_root / "certificates/h4_q79_eta9_b89_exact_integral_carrier.json"),
            "--output",
            str(BRANCH_AGGREGATE_PATH),
        ],
    )

    boundary = load_module(
        "t53_boundary_assembler", pilot / "assemble_boundary_taylor_campaign.py"
    )
    boundary.ROOT = common_root
    run_main(
        boundary,
        [
            "--campaign",
            str(MIXED_BOUNDARY_PATH),
            "--repair-campaign",
            str(MIXED_REPAIR_PATH),
            "--joint-artin",
            str(pilot / "outputs/family-global-right80-plus-joint-artin.json"),
            "--boundary-source",
            str(
                upstream_root
                / "experiments/q79_eta9_b89_branch_forms/"
                "q79_eta9_b89_branch_form_worker_input.json"
            ),
            "--signed-boundary-certificate",
            str(ADAPTED_SIGNED_PATH),
            "--output",
            str(BOUNDARY_AGGREGATE_PATH),
        ],
    )

    joint = load_module(
        "t53_joint_assembler", pilot / "assemble_joint_taylor_isotopy.py"
    )
    joint.ROOT = common_root
    run_main(
        joint,
        [
            "--branch-campaign",
            str(MIXED_BRANCH_PATH),
            "--boundary-campaign",
            str(MIXED_BOUNDARY_PATH),
            "--boundary-repair-campaign",
            str(MIXED_REPAIR_PATH),
            "--branch-aggregate",
            str(BRANCH_AGGREGATE_PATH),
            "--boundary-aggregate",
            str(BOUNDARY_AGGREGATE_PATH),
            "--joint-artin",
            str(pilot / "outputs/certified-common-grid-right80-joint-artin.json"),
            "--output",
            str(JOINT_AGGREGATE_PATH),
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", required=True)
    parser.add_argument("--result-index", required=True)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    require(
        not args.allow_incomplete or args.prepare_only,
        "incomplete coverage may only be prepared, never assembled",
    )
    upstream_root = Path(args.upstream_root).resolve()
    report = build_campaigns(
        upstream_root,
        Path(args.result_index).resolve(),
        allow_incomplete=args.allow_incomplete,
    )
    if not args.prepare_only:
        assemble(upstream_root)
    print(
        json.dumps(
            {
                "mixed_branch_campaign": str(MIXED_BRANCH_PATH),
                "mixed_boundary_campaign": str(MIXED_BOUNDARY_PATH),
                "mixed_boundary_repair_campaign": str(MIXED_REPAIR_PATH),
                "coverage_report": str(COVERAGE_REPORT_PATH),
                "coverage_complete": report["complete"],
                "assembled": not args.prepare_only,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
