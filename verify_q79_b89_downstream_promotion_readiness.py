#!/usr/bin/env python3
"""Independent verifier for CBF.T54 downstream-promotion readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
PACKET = ROOT / "q79_b89_downstream_promotion_readiness.packet.json"
EXPECTED = {0: 231, 1: 857, 2: 678, 3: 429}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def expand(ranges: dict[str, list[list[int]]]) -> set[tuple[int, int]]:
    return {
        (int(edge), interval)
        for edge, rows in ranges.items()
        for start, stop in rows
        for interval in range(int(start), int(stop))
    }


def rank_mod_two(matrix: list[list[int]]) -> int:
    rows = [
        sum((int(value) & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if (rows[row] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(len(rows)):
            if row != rank and ((rows[row] >> column) & 1):
                rows[row] ^= rows[rank]
        rank += 1
    return rank


def main() -> int:
    packet = load(PACKET)
    require(packet["theorem_id"] == "CBF.T54", "identity")
    for name, row in packet["inputs"].items():
        path = COMMON / row["path"]
        require(path.is_file(), f"input {name}")
        require(path.stat().st_size == row["bytes"], f"bytes {name}")
        require(sha256(path) == row["sha256"], f"hash {name}")

    campaign = load(COMMON / packet["inputs"]["campaign"]["path"])
    status = load(COMMON / packet["inputs"]["campaign_status"]["path"])
    preflight = load(COMMON / packet["inputs"]["preflight_coverage"]["path"])
    jobs = {row["id"]: row for row in campaign["jobs"]}
    require(len(jobs) == 218, "campaign jobs")
    additions = {"branch": set(), "boundary": set()}
    for row in status["campaign_verified_jobs"]:
        source = jobs[row["id"]]
        require(row["carrier"] == source["carrier"], "carrier")
        require(row["edge"] == source["edge"], "edge")
        require(
            row["interval_range"]
            == [source["interval_start"], source["interval_stop"]],
            "range",
        )
        require(row["input_capsule_sha256"] == source["input_capsule_sha256"], "capsule")
        require(
            row.get("reported_process_state", "succeeded")
            in {"succeeded", "failed", "running"},
            "process state",
        )
        require(row.get("result_manifest_exit_code", 0) == 0, "result exit")
        for interval in range(*row["interval_range"]):
            key = (row["edge"], interval)
            require(key not in additions[row["carrier"]], "overlap")
            additions[row["carrier"]].add(key)

    for carrier in ("branch", "boundary"):
        original_missing = expand(preflight[carrier]["missing_ranges"])
        require(not (additions[carrier] - original_missing), f"{carrier} outside gap")
        missing = original_missing - additions[carrier]
        row = packet["coverage"][carrier]
        require(expand(row["missing_ranges"]) == missing, f"{carrier} missing")
        require(
            row["certified_intervals"] == sum(EXPECTED.values()) - len(missing),
            f"{carrier} count",
        )
        require(row["complete"] == (not missing), f"{carrier} completion")

    affine = load(COMMON / packet["inputs"]["conditional_affine_obstruction"]["path"])
    matrix = affine["action_mod2"]
    translation = [int(value) & 1 for value in affine["affine_translation_mod2"]]
    witness = [int(value) & 1 for value in affine["mod2_obstruction_witness"]]
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
    require(packet["coverage"]["boundary"]["complete"], "boundary complete")
    expected_decision = (
        "READY_FOR_JOINT_ASSEMBLY_AND_B89_PROMOTION"
        if packet["coverage"]["branch"]["complete"]
        else "STATIC_ENDPOINT_READY_BRANCH_ISOTOPY_PENDING"
    )
    require(packet["decision"] == expected_decision, "decision")
    require(all(packet["checks"].values()), "checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    print(
        "CBF.T54 independent replay: PASS "
        f"branch={packet['coverage']['branch']['certified_intervals']}/2195 "
        "boundary=2195/2195 rank(M-I)=42 pairing=1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
