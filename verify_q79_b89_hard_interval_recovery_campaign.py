#!/usr/bin/env python3
"""Verify the exact T53 hard-interval recovery campaign and runtime jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "q79_b89_hard_interval_recovery_campaign.json"
EXPECTED_SCHEMA = "mtt.cbf.q79-b89-hard-interval-recovery-campaign.v1"
EXPECTED_ENTRYPOINT = (
    "mtt-causal-base-constraint-fiber/"
    "q79_b89_relaxed_predictor_adaptive_source_isotopy_worker.py"
)
EXPECTED_CAPSULES = {
    1: "47f31f53e553458191f210928fc6426829f2cbfb8707c8e47f103754c6c98c51",
    2: "906bfad85bae68abfe2060bcda546f11db186ef53f5c92661c17331a767f7033",
}


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(ranges: dict[str, list[list[int]]]) -> set[tuple[int, int]]:
    return {
        (int(edge), interval)
        for edge, edge_ranges in ranges.items()
        for start, stop in edge_ranges
        for interval in range(start, stop)
    }


def argument_value(arguments: list[str], name: str) -> str:
    index = arguments.index(name)
    return arguments[index + 1]


def find_job_path(runtime_root: Path, job_id: str) -> Path:
    candidates = (
        runtime_root / job_id / "job.json",
        runtime_root / "jobs" / job_id / "job.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise AssertionError(f"runtime job record exists: {job_id}")


def verify_runtime(
    runtime_root: Path, jobs: list[dict[str, object]], checks: list[str]
) -> dict[str, int]:
    states: dict[str, int] = {}
    for declared in jobs:
        job_id = str(declared["id"])
        packet = json.loads(find_job_path(runtime_root, job_id).read_text(encoding="utf-8"))
        require(packet["id"] == job_id, f"runtime id binding: {job_id}", checks)
        require(
            packet["execution_mode"] == "isolated-capsule",
            f"isolated execution: {job_id}",
            checks,
        )
        request = packet.get("request", packet)
        require(
            request.get("entrypoint", request.get("script")) == EXPECTED_ENTRYPOINT,
            f"entrypoint binding: {job_id}",
            checks,
        )
        arguments = request.get("arguments", packet.get("arguments", []))
        require(
            f"edge{declared['edge']}-guides.npz"
            in argument_value(arguments, "--guides"),
            f"runtime edge binding: {job_id}",
            checks,
        )
        require(
            int(argument_value(arguments, "--interval-start"))
            == declared["interval_start"],
            f"runtime interval start: {job_id}",
            checks,
        )
        require(
            int(argument_value(arguments, "--interval-stop"))
            == declared["interval_stop"],
            f"runtime interval stop: {job_id}",
            checks,
        )
        require(
            argument_value(arguments, "--output") == declared["output"],
            f"runtime output binding: {job_id}",
            checks,
        )
        capsule = packet.get("input_capsule", request.get("input_capsule", {}))
        capsule_hash = capsule.get(
            "sha256",
            packet.get("execution", {}).get(
                "input_capsule_sha256", request.get("input_capsule_sha256")
            ),
        )
        require(
            capsule_hash == declared["input_capsule_sha256"],
            f"runtime capsule binding: {job_id}",
            checks,
        )
        state = packet["state"]
        require(
            state in {"queued", "running", "succeeded", "failed", "cancelled"},
            f"recognized runtime state: {job_id}",
            checks,
        )
        states[state] = states.get(state, 0) + 1
    return states


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--runtime-root", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.resolve().read_text(encoding="ascii"))
    checks: list[str] = []
    require(manifest["schema"] == EXPECTED_SCHEMA, "campaign schema", checks)

    for label, lock in manifest["source_locks"].items():
        path = HERE / lock["path"]
        require(path.is_file(), f"source lock exists: {label}", checks)
        require(sha256(path) == lock["sha256"], f"source lock hash: {label}", checks)

    coverage_lock = manifest["source_locks"]["coverage_report"]
    coverage = json.loads((HERE / coverage_lock["path"]).read_text(encoding="ascii"))
    frontier = manifest["frontier_before"]
    require(
        coverage["branch"]["certified_intervals"]
        == frontier["branch_certified_intervals"]
        == 2003,
        "branch frontier is 2003",
        checks,
    )
    require(
        coverage["branch"]["target_intervals"]
        == frontier["target_intervals"]
        == 2195,
        "branch target is 2195",
        checks,
    )
    require(
        coverage["boundary"]["certified_intervals"]
        == frontier["boundary_certified_intervals"]
        == 2195,
        "boundary carrier is complete",
        checks,
    )

    requested = expand(manifest["exact_requested_coverage"]["ranges"])
    missing = expand(coverage["branch"]["missing_ranges"])
    require(requested == missing, "requested coverage equals exact branch gap", checks)
    require(
        len(requested) == manifest["exact_requested_coverage"]["intervals"] == 192,
        "requested coverage contains 192 intervals",
        checks,
    )

    jobs = manifest["jobs"]
    require(len(jobs) == 24, "campaign contains 24 jobs", checks)
    require(len({job["id"] for job in jobs}) == 24, "job ids are unique", checks)
    require(
        len({job["output"] for job in jobs}) == 24,
        "output paths are unique",
        checks,
    )
    job_intervals: set[tuple[int, int]] = set()
    for job in jobs:
        edge = int(job["edge"])
        start = int(job["interval_start"])
        stop = int(job["interval_stop"])
        width = stop - start
        require(edge in (1, 2), f"recognized edge: {job['id']}", checks)
        require(
            0 < width <= (4 if edge == 1 else 12),
            f"bounded job width: {job['id']}",
            checks,
        )
        require(
            job["input_capsule_sha256"] == EXPECTED_CAPSULES[edge],
            f"declared capsule binding: {job['id']}",
            checks,
        )
        require(
            job["verification_profile"] == "relaxed_predictor_v1",
            f"verification profile: {job['id']}",
            checks,
        )
        require(bool(job["recovery_of_job_id"]), f"predecessor link: {job['id']}", checks)
        require(
            job["output"]
            == f"outputs/t53-v3-recovery-branch-e{edge}-i{start}-{stop}.json",
            f"output range binding: {job['id']}",
            checks,
        )
        for interval in range(start, stop):
            cell = (edge, interval)
            require(cell not in job_intervals, f"non-overlap: {cell}", checks)
            job_intervals.add(cell)
    require(job_intervals == requested, "jobs exactly partition requested coverage", checks)

    policy = manifest["policy"]
    require(policy["predictor_refinement_threshold_bits"] == 52, "seed threshold is 2^-52", checks)
    require(
        policy["predictor_role"]
        == "nonproof_seed_for_interval_Krawczyk_validation",
        "predictor is declared non-proof",
        checks,
    )
    require(policy["rigorous_acceptance_unchanged"] is True, "proof gates are unchanged", checks)
    guardrails = manifest["guardrails"]
    require(all(guardrails.values()), "all recovery guardrails are active", checks)

    runtime_states = None
    if args.runtime_root is not None:
        runtime_states = verify_runtime(args.runtime_root.resolve(), jobs, checks)

    print(
        json.dumps(
            {
                "all_passed": True,
                "checks": len(checks),
                "jobs": len(jobs),
                "intervals": len(job_intervals),
                "runtime_states": runtime_states,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
