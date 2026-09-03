#!/usr/bin/env python3
"""Verify the complete shared-parameter submission manifest and runtime bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "q79_b89_joint_shared_parameter_campaign.json"
ENTRYPOINT = (
    "mtt-causal-base-constraint-fiber/"
    "q79_b89_joint_shared_parameter_campaign_worker.py"
)


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_key(row: dict):
    return (
        int(row["edge"]), int(row["interval"]),
        Fraction(row["fraction"][0]), Fraction(row["fraction"][1]),
        int(row["branch_label"]), int(row["boundary_label"]),
    )


def argument(arguments: list[str], name: str) -> str:
    return arguments[arguments.index(name) + 1]


def find_job(root: Path, job_id: str) -> Path:
    for path in (root / job_id / "job.json", root / "jobs" / job_id / "job.json"):
        if path.is_file():
            return path
    raise AssertionError(f"runtime job exists: {job_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--runtime-root", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.resolve().read_text(encoding="ascii"))
    checks = []
    require(
        manifest["schema"] == "mtt.cbf.q79-b89-joint-shared-parameter-campaign.v1",
        "schema", checks,
    )
    for label, lock in manifest["source_locks"].items():
        path = HERE / lock["path"]
        require(path.is_file(), f"source exists: {label}", checks)
        require(sha256(path) == lock["sha256"], f"source hash: {label}", checks)
    diagnostic = json.loads(
        (HERE / manifest["source_locks"]["diagnostic"]["path"]).read_text(
            encoding="ascii"
        )
    )
    targets = {target_key(row) for row in diagnostic["unresolved_mixed_pairs"]}
    require(len(diagnostic["unresolved_mixed_pairs"]) == 473, "473 diagnostic atoms", checks)
    require(len(targets) == 463, "463 unique targets", checks)
    jobs = manifest["jobs"]
    require(len(jobs) == 16, "16 jobs", checks)
    covered = set()
    states = {}
    for row in jobs:
        edge, start, stop = map(int, (row["edge"], row["interval_start"], row["interval_stop"]))
        selected = {
            target for target in targets
            if target[0] == edge and start <= target[1] < stop
        }
        require(len(selected) == row["targets"], f"target count: {row['id']}", checks)
        require(not covered.intersection(selected), f"disjoint slice: {row['id']}", checks)
        covered.update(selected)
        require(
            row["output"] == f"outputs/t53-shared-e{edge}-i{start}-{stop}.json",
            f"output: {row['id']}", checks,
        )
        if args.runtime_root is None:
            continue
        packet = json.loads(find_job(args.runtime_root.resolve(), row["id"]).read_text(encoding="utf-8"))
        require(packet["entrypoint"] == ENTRYPOINT, f"entrypoint: {row['id']}", checks)
        require(packet["input_capsule"]["sha256"] == row["input_capsule_sha256"], f"capsule: {row['id']}", checks)
        require(int(argument(packet["arguments"], "--edge")) == edge, f"edge: {row['id']}", checks)
        require(int(argument(packet["arguments"], "--interval-start")) == start, f"start: {row['id']}", checks)
        require(int(argument(packet["arguments"], "--interval-stop")) == stop, f"stop: {row['id']}", checks)
        require(argument(packet["arguments"], "--output") == row["output"], f"runtime output: {row['id']}", checks)
        state = packet["state"]
        require(state in {"queued", "running", "succeeded", "failed", "cancelled"}, f"state: {row['id']}", checks)
        states[state] = states.get(state, 0) + 1
    require(covered == targets, "jobs exactly partition all targets", checks)
    require(manifest["guardrails"]["process_success_is_not_proof"] is True, "process guardrail", checks)
    require(manifest["guardrails"]["independent_replay_required"] is True, "replay guardrail", checks)
    require(manifest["guardrails"]["claims_B89_or_beta_C"] is False, "no premature B89 claim", checks)
    print(json.dumps({
        "all_passed": True, "checks": len(checks), "jobs": len(jobs),
        "targets": len(targets), "runtime_states": states or None,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
