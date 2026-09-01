#!/usr/bin/env python3
"""Hash-verify and independently ingest completed B89 replacement capsules."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent
RESULT_MANIFEST = "mtt-calculation-result.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    temporary.replace(path)


def jobs_directory(runtime_root: Path) -> Path:
    runtime_root = runtime_root.resolve()
    if (runtime_root / "jobs").is_dir():
        return runtime_root / "jobs"
    require(runtime_root.is_dir(), f"runtime root {runtime_root}")
    return runtime_root


def safe_member(name: str) -> PurePosixPath:
    require("\\" not in name, f"non-POSIX capsule member {name}")
    path = PurePosixPath(name)
    require(not path.is_absolute(), f"absolute capsule member {name}")
    require(".." not in path.parts, f"escaping capsule member {name}")
    require(bool(path.parts) and all(part not in {"", "."} for part in path.parts), f"empty capsule member {name}")
    return path


def verifier_command(
    carrier: str,
    edge: int,
    packet_path: Path,
    upstream_root: Path,
) -> tuple[list[str], Path]:
    pilot = upstream_root / "experiments/q79_eta9_b89_family_branch_braid_pilot"
    if carrier == "branch":
        verifier = ROOT / "verify_q79_b89_accelerated_adaptive_source_isotopy.py"
        source = (
            upstream_root
            / "experiments/q79_eta9_b89_relative_adjoint_compiler/"
            "q79_eta9_b89_relative_adjoint_worker_input.json"
        )
        guide_stem = pilot / f"kernel_inputs/right80-edge{edge}-guides"
    elif carrier == "boundary":
        verifier = ROOT / "verify_q79_b89_recursive_boundary_isotopy.py"
        source = (
            upstream_root
            / "experiments/q79_eta9_b89_branch_forms/"
            "q79_eta9_b89_branch_form_worker_input.json"
        )
        guide_stem = pilot / f"kernel_inputs/right80-boundary-edge{edge}-guides"
    else:
        raise AssertionError(f"unknown carrier {carrier}")
    command = [
        sys.executable,
        str(verifier),
        "--packet",
        str(packet_path),
        "--baseline-root",
        str(upstream_root),
        "--source",
        str(source),
        "--guides",
        str(guide_stem.with_suffix(".npz")),
        "--metadata",
        str(guide_stem.with_suffix(".json")),
    ]
    return command, verifier


def parse_verifier_output(output: str) -> dict:
    output = output.strip()
    require(bool(output), "independent verifier emitted output")
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        start = output.rfind("\n{")
        require(start >= 0, "independent verifier JSON output")
        payload = json.loads(output[start + 1 :])
    require(payload.get("all_passed") is True, "independent verifier all_passed")
    require(payload.get("passed") == payload.get("total"), "independent verifier count")
    return payload


def process_result_allowed(job: dict, allow_recoverable_failed: bool = False) -> bool:
    state = str(job.get("state", "unknown"))
    result_exit = job.get("result", {}).get("manifest", {}).get("exit_code")
    return (
        state == "succeeded" and job.get("exit_code") == 0
    ) or (
        allow_recoverable_failed and state == "failed" and result_exit == 0
    )


def verify_capsule(
    campaign_row: dict,
    job: dict,
    capsule_path: Path,
    result_root: Path,
    upstream_root: Path,
    allow_recoverable_failed: bool = False,
) -> tuple[dict, dict]:
    require(job["id"] == campaign_row["id"], "job id")
    process_state = str(job.get("state", "unknown"))
    require(
        process_result_allowed(job, allow_recoverable_failed),
        "job emitted a zero-exit result in an allowed process state",
    )
    require(job["input_capsule"]["sha256"] == campaign_row["input_capsule_sha256"], "input capsule hash")
    require(
        sha256(capsule_path.parent / "input-capsule.zip")
        == campaign_row["input_capsule_sha256"],
        "stored input capsule hash",
    )
    require(job["result"]["available"] is True, "result available")
    require(sha256(capsule_path) == job["result"]["sha256"], "result capsule hash")

    with zipfile.ZipFile(capsule_path) as archive:
        members = archive.namelist()
        for member in members:
            safe_member(member)
        require(RESULT_MANIFEST in members, "result manifest member")
        manifest_bytes = archive.read(RESULT_MANIFEST)
        require(
            sha256_bytes(manifest_bytes) == job["result"]["manifest_sha256"],
            "result manifest hash",
        )
        result_manifest = json.loads(manifest_bytes.decode("ascii"))
        require(result_manifest["job_id"] == job["id"], "result manifest job id")
        require(result_manifest["exit_code"] == 0, "result manifest exit")
        require(
            result_manifest["input_capsule_sha256"]
            == campaign_row["input_capsule_sha256"],
            "result manifest input hash",
        )
        require(result_manifest["file_count"] == 1, "one result packet")
        file_row = result_manifest["files"][0]
        require(file_row["path"] == campaign_row["output"], "declared output path")
        require(file_row["path"] in members, "result packet member")
        packet_bytes = archive.read(file_row["path"])
        require(len(packet_bytes) == file_row["bytes"], "result packet size")
        require(sha256_bytes(packet_bytes) == file_row["sha256"], "result packet hash")

    destination = result_root / job["id"] / PurePosixPath(campaign_row["output"]).name
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(packet_bytes)
    temporary.replace(destination)
    packet = json.loads(packet_bytes.decode("ascii"))
    require(all(packet["checks"].values()) and not packet["failures"], "packet checks")
    require(int(packet["edge"]) == int(campaign_row["edge"]), "packet edge")
    require(
        [int(value) for value in packet["interval_range"]]
        == [campaign_row["interval_start"], campaign_row["interval_stop"]],
        "packet requested range",
    )

    command, verifier = verifier_command(
        campaign_row["carrier"], int(campaign_row["edge"]), destination, upstream_root
    )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    require(
        completed.returncode == 0,
        f"independent verifier exit: {completed.stderr[-2000:]}",
    )
    verification = parse_verifier_output(completed.stdout)
    relative_packet = f"{ROOT.name}/{destination.relative_to(ROOT).as_posix()}"
    index_row = {
        "id": job["id"],
        "carrier": campaign_row["carrier"],
        "edge": int(campaign_row["edge"]),
        "interval_range": [
            int(campaign_row["interval_start"]),
            int(campaign_row["interval_stop"]),
        ],
        "assigned_agent": job.get("assigned_agent"),
        "reported_process_state": process_state,
        "process_exit_code": job.get("exit_code"),
        "result_manifest_exit_code": int(result_manifest["exit_code"]),
        "packet_path": relative_packet,
        "packet_sha256": sha256_bytes(packet_bytes),
        "input_capsule_sha256": campaign_row["input_capsule_sha256"],
        "result_capsule_sha256": job["result"]["sha256"],
        "result_manifest_sha256": job["result"]["manifest_sha256"],
        "independent_verification": {
            "passed": True,
            "packet_sha256": sha256_bytes(packet_bytes),
            "verifier": " ".join(command),
            "verifier_sha256": sha256(verifier),
            "passed_checks": int(verification["passed"]),
            "total_checks": int(verification["total"]),
        },
    }
    return index_row, verification


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--upstream-root", required=True)
    parser.add_argument(
        "--campaign", default=str(ROOT / "q79_b89_recursive_replacement_campaign.json")
    )
    parser.add_argument(
        "--result-index",
        default=str(ROOT / "q79_b89_accelerated_source_isotopy_result_index.json"),
    )
    parser.add_argument(
        "--result-root",
        default=str(ROOT / "q79_b89_accelerated_source_isotopy_results/v2"),
    )
    parser.add_argument(
        "--status-report",
        default=str(ROOT / "q79_b89_recursive_replacement_campaign_status.json"),
    )
    parser.add_argument("--ingest-succeeded", action="store_true")
    parser.add_argument("--ingest-recoverable-results", action="store_true")
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--max-ingest", type=int)
    args = parser.parse_args()

    campaign = load(Path(args.campaign).resolve())
    index_path = Path(args.result_index).resolve()
    result_root = Path(args.result_root).resolve()
    status_path = Path(args.status_report).resolve()
    upstream_root = Path(args.upstream_root).resolve()
    root = jobs_directory(Path(args.runtime_root))
    selected_ids = set(args.job_id)
    index = load(index_path)
    indexed = {row["id"]: row for row in index["jobs"]}
    statuses = Counter()
    ingested = []
    verification_failures = []
    succeeded_available = []
    recoverable_failed_available = []

    for campaign_row in campaign["jobs"]:
        job_id = campaign_row["id"]
        job_path = root / job_id / "job.json"
        if not job_path.is_file():
            statuses["missing_job_record"] += 1
            continue
        job = load(job_path)
        state = str(job.get("state", "unknown"))
        statuses[state] += 1
        result_available = job.get("result", {}).get("available") is True
        is_succeeded_result = state == "succeeded" and result_available
        is_recoverable_failed_result = (
            state == "failed"
            and job.get("result", {}).get("manifest", {}).get("exit_code") == 0
            and result_available
        )
        if is_succeeded_result:
            succeeded_available.append(job_id)
        if is_recoverable_failed_result:
            recoverable_failed_available.append(job_id)
        if not (is_succeeded_result or is_recoverable_failed_result):
            continue
        requested = (
            (is_succeeded_result and args.ingest_succeeded)
            or (
                is_recoverable_failed_result
                and args.ingest_recoverable_results
            )
        )
        if not requested or (selected_ids and job_id not in selected_ids):
            continue
        if job_id in indexed:
            continue
        if args.max_ingest is not None and len(ingested) >= args.max_ingest:
            continue
        try:
            row, verification = verify_capsule(
                campaign_row,
                job,
                root / job_id / "result-capsule.zip",
                result_root,
                upstream_root,
                allow_recoverable_failed=is_recoverable_failed_result,
            )
            indexed[job_id] = row
            ingested.append(
                {
                    "id": job_id,
                    "carrier": row["carrier"],
                    "edge": row["edge"],
                    "interval_range": row["interval_range"],
                    "packet_sha256": row["packet_sha256"],
                    "checks": verification["total"],
                }
            )
        except Exception as error:  # preserve every failed scientific audit
            verification_failures.append({"id": job_id, "error": str(error)})

    index["jobs"] = sorted(
        indexed.values(),
        key=lambda row: (
            row.get("carrier", ""),
            int(row.get("edge", -1)),
            int(row.get("interval_range", [-1])[0]),
            row["id"],
        ),
    )
    if ingested:
        write_json_atomic(index_path, index)

    campaign_ids = {row["id"] for row in campaign["jobs"]}
    verified_campaign_rows = [
        row
        for row in index["jobs"]
        if row["id"] in campaign_ids
        and row.get("independent_verification", {}).get("passed") is True
    ]
    verified_by_carrier = Counter(row["carrier"] for row in verified_campaign_rows)
    intervals_by_carrier = Counter()
    for row in verified_campaign_rows:
        start, stop = row["interval_range"]
        intervals_by_carrier[row["carrier"]] += int(stop) - int(start)

    report = {
        "schema": "mtt.cbf.q79-b89-recursive-replacement-campaign-status.v1",
        "campaign": os.path.relpath(Path(args.campaign).resolve(), ROOT),
        "campaign_job_count": len(campaign["jobs"]),
        "runtime": {
            "kind": "external durable job store supplied by CLI",
            "absolute_path_recorded": False,
        },
        "states": dict(sorted(statuses.items())),
        "succeeded_result_capsules_available": len(succeeded_available),
        "recoverable_failed_result_capsules_available": len(
            recoverable_failed_available
        ),
        "active_result_index_rows": len(index["jobs"]),
        "campaign_packets_independently_verified": len(verified_campaign_rows),
        "campaign_packets_independently_verified_by_carrier": dict(
            sorted(verified_by_carrier.items())
        ),
        "campaign_verified_jobs": [
            {
                "id": row["id"],
                "carrier": row["carrier"],
                "edge": int(row["edge"]),
                "interval_range": [int(value) for value in row["interval_range"]],
                "packet_sha256": row["packet_sha256"],
                "input_capsule_sha256": row.get("input_capsule_sha256"),
                "result_capsule_sha256": row.get("result_capsule_sha256"),
                "result_manifest_sha256": row.get("result_manifest_sha256"),
                "verifier_sha256": row["independent_verification"]["verifier_sha256"],
                "reported_process_state": row.get(
                    "reported_process_state", "succeeded"
                ),
                "result_manifest_exit_code": int(
                    row.get("result_manifest_exit_code", 0)
                ),
            }
            for row in sorted(
                verified_campaign_rows,
                key=lambda value: (
                    value["carrier"],
                    int(value["edge"]),
                    int(value["interval_range"][0]),
                ),
            )
        ],
        "campaign_intervals_independently_verified_by_carrier": dict(
            sorted(intervals_by_carrier.items())
        ),
        "succeeded_capsules_awaiting_independent_verification": len(
            set(succeeded_available) - {row["id"] for row in verified_campaign_rows}
        ),
        "recoverable_failed_capsules_awaiting_independent_verification": len(
            set(recoverable_failed_available)
            - {row["id"] for row in verified_campaign_rows}
        ),
        "newly_ingested": ingested,
        "verification_failures": verification_failures,
        "guardrails": {
            "succeeded_processes_are_not_counted_without_independent_verification": True,
            "recoverable_failed_process_labels_are_counted_only_after_zero_exit_capsule_and_independent_verification": True,
            "failed_verifications_are_absent_from_the_result_index": True,
        },
    }
    write_json_atomic(status_path, report)
    console_report = dict(report)
    console_report.pop("campaign_verified_jobs", None)
    console_report["campaign_verified_job_rows_in_status_report"] = len(
        verified_campaign_rows
    )
    print(json.dumps(console_report, indent=2, sort_keys=True))
    return 1 if verification_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
