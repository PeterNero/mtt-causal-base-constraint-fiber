#!/usr/bin/env python3
"""Reconcile verified T53 result capsules and run the exact assemblers."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from decimal import Decimal
from fractions import Fraction
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
JOINT_DIAGNOSTIC_PATH = ROOT / "q79_b89_joint_mixed_separation_diagnostic.json"
JOINT_REPLAY_AUDIT_PATH = ROOT / "q79_b89_joint_mixed_separation_replay_audit.json"
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
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )


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
    excluded_boundary_rows = []
    for row in upstream_boundary["jobs"]:
        if row.get("observed_state") == "succeeded":
            copied = dict(row)
            copied["retrieved_path"] = prefixed_upstream_path(
                row["retrieved_path"], upstream_name
            )
            boundary_jobs.append(copied)
        else:
            excluded_boundary_jobs.append(row["id"])
            excluded_boundary_rows.append(row)
    boundary_repairs = [
        dict(row)
        for row in new_jobs["boundary"]
        if row["packet_schema"]
        == "mtt.preprojection.q79-eta9-b89-adaptive-boundary-taylor-krawczyk.v1"
    ]
    for repair in boundary_repairs:
        candidates = [
            original
            for original in excluded_boundary_rows
            if int(original["edge"]) == int(repair["edge"])
            and int(original["interval_range"][0])
            <= int(repair["interval_range"][0])
            < int(repair["interval_range"][1])
            <= int(original["interval_range"][1])
        ]
        require(
            len(candidates) == 1,
            f"unique failed boundary predecessor for {repair['id']}",
        )
        repair["replaces_job_id"] = candidates[0]["id"]
    boundary_jobs.extend(
        row
        for row in new_jobs["boundary"]
        if row["packet_schema"]
        == "mtt.preprojection.q79-eta9-b89-boundary-taylor-krawczyk.v1"
    )
    boundary_coverage = coverage_report(
        [*boundary_jobs, *boundary_repairs], "boundary"
    )
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
        "replacement_packets_are_in_mixed_boundary_campaign": False,
        "jobs": sorted(
            boundary_repairs,
            key=lambda row: (row["edge"], row["interval_range"][0]),
        ),
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


def exact_endpoint_binding(previous_tubes: list[dict], current_tubes: list[dict]) -> dict:
    def box(tube: dict, endpoint: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        value = tube[f"{endpoint}_endpoint_x_box"]
        return (
            Decimal(value["real"][0]),
            Decimal(value["real"][1]),
            Decimal(value["imag"][0]),
            Decimal(value["imag"][1]),
        )

    def overlaps(left, right) -> bool:
        return (
            max(left[0], right[0]) <= min(left[1], right[1])
            and max(left[2], right[2]) <= min(left[3], right[3])
        )

    previous = {int(tube["branch"]): box(tube, "right") for tube in previous_tubes}
    current = {int(tube["branch"]): box(tube, "left") for tube in current_tubes}
    require(set(previous) == set(current), "endpoint label sets")
    for label, previous_box in previous.items():
        hits = [
            candidate
            for candidate, current_box in current.items()
            if overlaps(previous_box, current_box)
        ]
        require(hits == [label], f"exact endpoint identity label={label} hits={hits}")
    return {
        "bound_branches": len(previous),
        "unique_label_matches": len(previous),
        "identity_matching": True,
    }


def branch_loader_with_exact_binding_reconstruction(module, campaign, expected_source_sha256):
    """Replay every branch binding and reconstruct only historical null summaries."""

    shards = {edge: [] for edge in range(4)}
    payload_hashes = []
    agents = set()
    audit = {
        "schema": "mtt.cbf.q79-b89-exact-endpoint-binding-reconstruction.v1",
        "method": "closed Decimal rectangle overlap with unique identity label",
        "historical_null_row_bindings_reconstructed": 0,
        "recorded_row_bindings_independently_replayed": 0,
        "recorded_subcell_bindings_independently_replayed": 0,
        "cross_shard_bindings_independently_replayed": 0,
        "all_replayed_bindings_are_identity": True,
        "source_packets_are_not_modified": True,
    }
    for job in campaign["jobs"]:
        module.require(job.get("observed_state") == "succeeded", "observed job")
        path = module.ROOT / job["retrieved_path"]
        module.require(module.sha256(path) == job["retrieved_payload_sha256"], "retrieved payload hash")
        packet = json.loads(path.read_text(encoding="ascii"))
        module.require(all(packet["checks"].values()), "shard scientific checks")
        module.require(not packet["failures"], "shard failures")
        adaptive = packet["schema"] == "mtt.preprojection.q79-eta9-b89-adaptive-family-taylor-krawczyk.v1"
        module.require(
            adaptive
            or packet["schema"]
            == "mtt.preprojection.q79-eta9-b89-family-taylor-krawczyk.v1",
            "family packet schema",
        )
        module.require(packet["branch_range"] == [0, 252], "complete branch carrier")
        module.require(packet["precision_bits"] == 512, "precision")
        module.require(packet["predictor_degree"] == 12, "predictor degree")
        module.require(packet["taylor_order"] == 14, "Taylor order")
        module.require(packet["source_sha256"] == expected_source_sha256, "H4-T122 source binding")
        module.require(packet["edge"] == job["edge"], "job edge")
        module.require(packet["interval_range"] == job["interval_range"], "job interval range")
        packet_rows = packet["logical_rows"] if adaptive else packet["rows"]
        module.require(
            len(packet_rows) == job["interval_range"][1] - job["interval_range"][0],
            "row count",
        )
        previous_tubes = None
        for offset, row in enumerate(packet_rows):
            module.require(row["interval"] == job["interval_range"][0] + offset, "row interval")
            module.require(row["certified_branches"] == 252, "row branch count")
            subcells = module.row_subcells(row)
            module.require(
                row["separation"]["certified_pairs"] == module.PAIR_COUNT * len(subcells),
                "row pair separation",
            )
            module.require(
                row["guide_homotopy"]["certified_pairs"] == module.PAIR_COUNT * len(subcells),
                "row guide homotopy",
            )
            for subcell_index, subcell in enumerate(subcells):
                module.require(len(subcell["tubes"]) == 252, "subcell tubes")
                module.require(subcell["certified_branches"] == 252, "subcell branch count")
                if subcell_index:
                    expected = exact_endpoint_binding(
                        subcells[subcell_index - 1]["tubes"], subcell["tubes"]
                    )
                    module.require(
                        subcell["binding_from_previous_subcell"] == expected,
                        "within-row exact subcell binding",
                    )
                    audit["recorded_subcell_bindings_independently_replayed"] += 1
            if previous_tubes is not None:
                expected = exact_endpoint_binding(previous_tubes, subcells[0]["tubes"])
                recorded = row.get("binding_from_previous_interval")
                if recorded is None:
                    row["binding_from_previous_interval"] = expected
                    audit["historical_null_row_bindings_reconstructed"] += 1
                else:
                    module.require(recorded == expected, "within-shard exact row binding")
                    audit["recorded_row_bindings_independently_replayed"] += 1
            previous_tubes = subcells[-1]["tubes"]
        packet["_logical_rows"] = packet_rows
        shards[job["edge"]].append((job, packet))
        payload_hashes.append(job["retrieved_payload_sha256"])
        agents.add(job.get("assigned_agent") or "")

    for edge in range(4):
        shards[edge].sort(key=lambda item: item[0]["interval_range"][0])
        previous_packet = None
        for _job, packet in shards[edge]:
            if previous_packet is not None:
                exact_endpoint_binding(
                    module.last_tubes(previous_packet["_logical_rows"][-1]),
                    module.first_tubes(packet["_logical_rows"][0]),
                )
                audit["cross_shard_bindings_independently_replayed"] += 1
            previous_packet = packet
    audit["source_packet_count"] = len(payload_hashes)
    audit["source_packet_hash_set_sha256"] = hashlib.sha256(
        ("\n".join(sorted(payload_hashes)) + "\n").encode("ascii")
    ).hexdigest()
    module.EXACT_BINDING_RECONSTRUCTION_AUDIT = audit
    return shards, sorted(payload_hashes), sorted(agents)


def load_joint_mixed_refinements(index_path: Path | None) -> tuple[dict, dict]:
    """Load only a complete, hash-bound, independently replayed result index."""

    if index_path is None:
        return {}, {}
    index_path = index_path.resolve()
    index = load(index_path)
    if index["schema"] == "mtt.cbf.q79-b89-joint-shared-parameter-result-index.v1":
        require(index["complete"] is True, "shared-parameter result index is complete")
        require(
            index["diagnostic_sha256"] == sha256(JOINT_DIAGNOSTIC_PATH),
            "shared-parameter diagnostic hash",
        )
        diagnostic = load(JOINT_DIAGNOSTIC_PATH)
        targets = {
            (
                int(row["edge"]), int(row["interval"]),
                str(Fraction(row["fraction"][0])),
                str(Fraction(row["fraction"][1])),
                int(row["branch_label"]), int(row["boundary_label"]),
            )
            for row in diagnostic["unresolved_mixed_pairs"]
        }
        valid_packet_hashes = set()
        for record in index["results"]:
            packet_path = result_path(ROOT, record["packet_path"])
            require(
                sha256(packet_path) == record["packet_sha256"],
                "shared-parameter packet hash",
            )
            require(
                record["verifier_result"]["all_passed"] is True,
                "shared-parameter independent replay",
            )
            valid_packet_hashes.add(record["packet_sha256"])
        refinements = {}
        for row in index["target_certificates"]:
            target = (
                int(row["edge"]), int(row["interval"]),
                str(Fraction(row["fraction"][0])),
                str(Fraction(row["fraction"][1])),
                int(row["branch_label"]), int(row["boundary_label"]),
            )
            margin = Decimal(str(row["minimum_strict_margin"]))
            require(target in targets, "recognized shared-parameter target")
            require(target not in refinements, "unique shared-parameter target")
            require(margin > 0, "strict shared-parameter target margin")
            require(
                row["packet_sha256"] in valid_packet_hashes,
                "shared-parameter target packet binding",
            )
            refinements[target] = {
                "strict_separation_margin": margin,
                "certified_leaves": int(row["component_subcells"]),
                "packet_sha256": row["packet_sha256"],
                "method": "residual_aware_shared_parameter",
            }
        require(set(refinements) == targets, "all shared-parameter targets loaded")
        return refinements, {
            "method": "residual_aware_shared_parameter",
            "result_index_path": str(index_path.relative_to(ROOT)).replace("\\", "/"),
            "result_index_sha256": sha256(index_path),
            "diagnostic_sha256": sha256(JOINT_DIAGNOSTIC_PATH),
            "unique_targets": len(targets),
            "diagnostic_atoms": len(diagnostic["unresolved_mixed_pairs"]),
        }
    require(
        index["schema"]
        == "mtt.cbf.q79-b89-joint-mixed-refinement-result-index.v1",
        "joint mixed refinement index schema",
    )
    require(index["complete"] is True, "joint mixed refinement index is complete")
    require(
        index["diagnostic_sha256"] == sha256(JOINT_DIAGNOSTIC_PATH),
        "joint mixed refinement diagnostic hash",
    )
    diagnostic = load(JOINT_DIAGNOSTIC_PATH)
    targets = {
        (
            int(row["edge"]), int(row["interval"]),
            str(Fraction(row["fraction"][0])), str(Fraction(row["fraction"][1])),
            int(row["branch_label"]), int(row["boundary_label"]),
        )
        for row in diagnostic["unresolved_mixed_pairs"]
    }
    refinements = {}
    for record in index["results"]:
        packet_path = result_path(ROOT, record["packet_path"])
        require(sha256(packet_path) == record["packet_sha256"], "refinement packet hash")
        require(record["independently_verified"] is True, "refinement independent replay")
        packet = load(packet_path)
        edge = int(packet["edge"])
        interval_start, interval_stop = map(int, packet["interval_range"])
        packet_targets = {
            target for target in targets
            if target[0] == edge and interval_start <= target[1] < interval_stop
        }
        for target in packet_targets:
            parent_start = Fraction(target[2])
            parent_stop = Fraction(target[3])
            cells = []
            margins = []
            for leaf in packet["certified_leaves"]:
                if int(leaf["interval"]) != target[1]:
                    continue
                leaf_start, leaf_stop = map(Fraction, leaf["cell_fraction"])
                if not (parent_start <= leaf_start < leaf_stop <= parent_stop):
                    continue
                matches = [
                    certificate
                    for certificate in leaf["mixed_pair_certificates"]
                    if int(certificate["branch_label"]) == target[4]
                    and int(certificate["boundary_label"]) == target[5]
                ]
                require(len(matches) == 1, "one mixed refinement leaf certificate")
                margin = Decimal(matches[0]["strict_separation_margin"])
                require(margin > 0, "strict mixed refinement leaf margin")
                cells.append((leaf_start, leaf_stop))
                margins.append(margin)
            cells.sort()
            require(bool(cells), "mixed refinement target has leaves")
            require(
                cells[0][0] == parent_start and cells[-1][1] == parent_stop,
                "mixed refinement target endpoints",
            )
            require(
                all(left[1] == right[0] for left, right in zip(cells, cells[1:])),
                "mixed refinement target is gap free",
            )
            require(target not in refinements, "unique mixed refinement target")
            refinements[target] = {
                "strict_separation_margin": min(margins),
                "certified_leaves": len(cells),
                "packet_sha256": record["packet_sha256"],
            }
    require(set(refinements) == targets, "all mixed refinement targets loaded")
    return refinements, {
        "result_index_path": str(index_path.relative_to(ROOT)).replace("\\", "/"),
        "result_index_sha256": sha256(index_path),
        "diagnostic_sha256": sha256(JOINT_DIAGNOSTIC_PATH),
        "unique_targets": len(targets),
        "diagnostic_atoms": len(diagnostic["unresolved_mixed_pairs"]),
    }


def install_joint_convex_region_fallback(module, refinements=None, provenance=None) -> dict:
    """Certify rare rectangle overlaps by a stronger convex capsule separator."""

    original_build = module.build_subcell_rectangles
    original_load_guides = module.load_guides
    guide_edges: dict[int, int] = {}
    audit = {
        "schema": "mtt.cbf.q79-b89-mixed-convex-region-fallback.v1",
        "method": "Decimal separating-axis certificate for convex hull(center, guide endpoints) plus source-disc radius",
        "fallback_pair_certificates": [],
        "targeted_pair_certificates": [],
        "unresolved_mixed_pairs": [],
        "rectangle_pair_certificates": 0,
        "all_fallback_margins_strictly_positive": True,
    }

    class RegionSet:
        def __init__(self, rectangles, capsules):
            self.rectangles = rectangles
            self.capsules = capsules

    def exact_float(value: float) -> Decimal:
        return Decimal.from_float(float(value))

    def wrapped_load_guides(edge: int, joint_artin: dict):
        branch_guides, boundary_guides = original_load_guides(edge, joint_artin)
        guide_edges[id(branch_guides)] = edge
        guide_edges[id(boundary_guides)] = edge
        return branch_guides, boundary_guides

    def wrapped_build(subcell, guides, interval, carrier_size):
        rectangles, endpoints, padding = original_build(
            subcell, guides, interval, carrier_size
        )
        capsules = []
        for tube in subcell["tubes"]:
            label = int(tube["branch"])
            guide_start, guide_stop = module.guide_segment(
                guides, interval, subcell, label
            )
            center = tuple(Decimal(value) for value in tube["x_center"])
            capsules.append(
                {
                    "edge": guide_edges[id(guides)],
                    "interval": interval,
                    "fraction": list(subcell.get("cell_fraction") or ["0", "1"]),
                    "label": label,
                    "triangle": [
                        center,
                        (exact_float(guide_start.real), exact_float(guide_start.imag)),
                        (exact_float(guide_stop.real), exact_float(guide_stop.imag)),
                    ],
                    "radius": Decimal(tube["x_radius"]),
                }
            )
        return RegionSet(rectangles, capsules), endpoints, padding

    def projection_gap(left, right, axis):
        left_projection = [point[0] * axis[0] + point[1] * axis[1] for point in left]
        right_projection = [point[0] * axis[0] + point[1] * axis[1] for point in right]
        return max(
            min(right_projection) - max(left_projection),
            min(left_projection) - max(right_projection),
        )

    def capsule_margin(left: dict, right: dict) -> float | None:
        radius = left["radius"] + right["radius"]
        candidates = []
        for triangle in (left["triangle"], right["triangle"]):
            for index in range(3):
                start = triangle[index]
                stop = triangle[(index + 1) % 3]
                edge = (stop[0] - start[0], stop[1] - start[1])
                norm_squared = edge[0] * edge[0] + edge[1] * edge[1]
                if norm_squared == 0:
                    continue
                axis = (-edge[1], edge[0])
                gap = projection_gap(left["triangle"], right["triangle"], axis)
                if gap > 0 and gap * gap > radius * radius * norm_squared:
                    candidates.append(float(gap / norm_squared.sqrt() - radius))
        return max(candidates) if candidates else None

    def wrapped_mixed_clearance(branch: RegionSet, boundary: RegionSet):
        minimum = float("inf")
        for boundary_index, boundary_rectangle in enumerate(boundary.rectangles):
            real_clearance = module.np.maximum(
                boundary_rectangle[0] - branch.rectangles[:, 1],
                branch.rectangles[:, 0] - boundary_rectangle[1],
            )
            imag_clearance = module.np.maximum(
                boundary_rectangle[2] - branch.rectangles[:, 3],
                branch.rectangles[:, 2] - boundary_rectangle[3],
            )
            clearances = module.np.maximum(real_clearance, imag_clearance)
            for branch_index, rectangle_clearance in enumerate(clearances):
                if rectangle_clearance > 0.0:
                    audit["rectangle_pair_certificates"] += 1
                    minimum = min(minimum, float(rectangle_clearance))
                    continue
                left = branch.capsules[branch_index]
                right = boundary.capsules[boundary_index]
                margin = capsule_margin(left, right)
                require(left["edge"] == right["edge"], "fallback common edge")
                require(left["interval"] == right["interval"], "fallback common interval")
                if margin is None:
                    key = (
                        left["edge"], left["interval"],
                        str(Fraction(left["fraction"][0])),
                        str(Fraction(left["fraction"][1])),
                        left["label"], right["label"],
                    )
                    refinement = (refinements or {}).get(key)
                    if refinement is not None:
                        adaptive_margin = refinement["strict_separation_margin"]
                        audit["targeted_pair_certificates"].append(
                            {
                                "edge": left["edge"],
                                "interval": left["interval"],
                                "fraction": left["fraction"],
                                "branch_label": left["label"],
                                "boundary_label": right["label"],
                                "strict_separation_margin": str(adaptive_margin),
                                "certified_leaves": refinement["certified_leaves"],
                                "packet_sha256": refinement["packet_sha256"],
                                "method": refinement.get(
                                    "method", "adaptive_dyadic_convex_region"
                                ),
                            }
                        )
                        minimum = min(minimum, float(adaptive_margin))
                        continue
                    audit["unresolved_mixed_pairs"].append(
                        {
                            "edge": left["edge"],
                            "interval": left["interval"],
                            "fraction": left["fraction"],
                            "branch_label": left["label"],
                            "boundary_label": right["label"],
                        }
                    )
                    continue
                audit["fallback_pair_certificates"].append(
                    {
                        "edge": left["edge"],
                        "interval": left["interval"],
                        "fraction": left["fraction"],
                        "branch_label": left["label"],
                        "boundary_label": right["label"],
                        "strict_separation_margin": margin,
                    }
                )
                minimum = min(minimum, margin)
        return minimum if minimum < float("inf") else 1.0

    module.load_guides = wrapped_load_guides
    module.build_subcell_rectangles = wrapped_build
    module.mixed_clearance = wrapped_mixed_clearance
    if provenance:
        audit["targeted_certificate_provenance"] = provenance
    return audit


def run_main(module, arguments: list[str]) -> None:
    original = sys.argv
    try:
        sys.argv = [str(Path(module.__file__).resolve()), *arguments]
        code = module.main()
    finally:
        sys.argv = original
    require(code == 0, f"assembler {module.__name__}")


def assemble(upstream_root: Path, joint_refinement_index: Path | None = None) -> None:
    common_root = upstream_root.parent
    pilot = upstream_root / "experiments/q79_eta9_b89_family_branch_braid_pilot"
    sys.path.insert(0, str(pilot))

    branch = load_module("t53_branch_assembler", pilot / "assemble_taylor_family_campaign.py")
    branch.ROOT = common_root
    branch.load_shards = lambda campaign, expected: branch_loader_with_exact_binding_reconstruction(
        branch, campaign, expected
    )
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
    branch_aggregate = load(BRANCH_AGGREGATE_PATH)
    branch_aggregate["exact_endpoint_binding_reconstruction"] = (
        branch.EXACT_BINDING_RECONSTRUCTION_AUDIT
    )
    write(BRANCH_AGGREGATE_PATH, branch_aggregate)

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
    refinements, refinement_provenance = load_joint_mixed_refinements(
        joint_refinement_index
    )
    convex_region_audit = install_joint_convex_region_fallback(
        joint, refinements, refinement_provenance
    )
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
    unresolved = convex_region_audit["unresolved_mixed_pairs"]
    convex_region_audit["inputs"] = {
        "branch_campaign_sha256": sha256(MIXED_BRANCH_PATH),
        "boundary_campaign_sha256": sha256(MIXED_BOUNDARY_PATH),
        "boundary_repair_campaign_sha256": sha256(MIXED_REPAIR_PATH),
        "branch_aggregate_sha256": sha256(BRANCH_AGGREGATE_PATH),
        "boundary_aggregate_sha256": sha256(BOUNDARY_AGGREGATE_PATH),
        "joint_Artin_sha256": sha256(
            pilot / "outputs/certified-common-grid-right80-joint-artin.json"
        ),
    }
    convex_region_audit["counts"] = {
        "fallback_pair_certificates": len(
            convex_region_audit["fallback_pair_certificates"]
        ),
        "targeted_pair_certificates": len(
            convex_region_audit["targeted_pair_certificates"]
        ),
        "unresolved_common_refinement_atoms": len(unresolved),
        "unresolved_source_intervals": len(
            {(row["edge"], row["interval"]) for row in unresolved}
        ),
        "unresolved_label_pairs": len(
            {
                (row["edge"], row["branch_label"], row["boundary_label"])
                for row in unresolved
            }
        ),
    }
    audit_path = (
        JOINT_REPLAY_AUDIT_PATH
        if joint_refinement_index is not None
        else JOINT_DIAGNOSTIC_PATH
    )
    write(audit_path, convex_region_audit)
    if unresolved:
        JOINT_AGGREGATE_PATH.unlink(missing_ok=True)
        raise AssertionError(
            "joint mixed refinement remains: "
            f"atoms={len(unresolved)} "
            f"intervals={convex_region_audit['counts']['unresolved_source_intervals']} "
            f"label_pairs={convex_region_audit['counts']['unresolved_label_pairs']}"
        )
    joint_aggregate = load(JOINT_AGGREGATE_PATH)
    fallback_count = len(convex_region_audit["fallback_pair_certificates"])
    targeted_count = len(
        convex_region_audit["targeted_pair_certificates"]
    )
    joint_aggregate["schema"] = (
        "mtt.cbf.q79-b89-certified-common-grid-joint-isotopy.v2"
    )
    joint_aggregate["counts"]["mixed_homotopy_rectangle_certificates"] -= (
        fallback_count + targeted_count
    )
    joint_aggregate["counts"]["mixed_homotopy_convex_region_certificates"] = fallback_count
    joint_aggregate["counts"][
        "mixed_homotopy_targeted_certificates"
    ] = targeted_count
    joint_aggregate["bounds"]["minimum_mixed_certified_separation_margin"] = (
        joint_aggregate["bounds"].pop("minimum_mixed_outward_rectangle_clearance")
    )
    for edge in joint_aggregate["per_edge"]:
        edge["minimum_certified_mixed_separation_margin"] = edge.pop(
            "minimum_outward_rectangle_clearance"
        )
    joint_aggregate["argument"]["homotopy_containment"] = (
        "Each path lies in its outward rectangle and also in the convex hull of the "
        "source-disc center and guide endpoints, Minkowski-summed with the certified "
        "source-disc radius."
    )
    joint_aggregate["argument"]["joint_noncollision"] = (
        "Every mixed pair is separated either by disjoint outward rectangles, by "
        "an exact Decimal separating-axis certificate for the stronger convex-region "
        "fallback, or by a targeted certificate preserving the common source and "
        "homotopy parameters, with any component subdivision finite and gap free."
    )
    joint_aggregate["checks"].pop(
        "all_source_and_guide_paths_lie_in_the_audited_convex_rectangles"
    )
    joint_aggregate["checks"][
        "all_source_and_guide_paths_lie_in_the_audited_convex_regions"
    ] = True
    joint_aggregate["mixed_convex_region_fallback"] = convex_region_audit
    write(JOINT_AGGREGATE_PATH, joint_aggregate)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", required=True)
    parser.add_argument("--result-index", required=True)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--joint-refinement-index", type=Path)
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
        assemble(upstream_root, args.joint_refinement_index)
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
