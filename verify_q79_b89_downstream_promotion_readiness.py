#!/usr/bin/env python3
"""Independent verifier for current CBF.T54 downstream readiness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
PACKET = ROOT / "q79_b89_downstream_promotion_readiness.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_mod_two(matrix: list[list[int]]) -> int:
    rows = [sum((int(v) & 1) << c for c, v in enumerate(row)) for row in matrix]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((r for r in range(rank, len(rows)) if (rows[r] >> column) & 1), None)
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
    require(packet["schema"].endswith(".v2"), "schema")
    require(packet["theorem_id"] == "CBF.T54", "identity")
    inputs = {}
    for name, row in packet["inputs"].items():
        path = COMMON / row["path"]
        require(path.is_file(), f"input {name}")
        require(path.stat().st_size == row["bytes"], f"bytes {name}")
        require(sha256(path) == row["sha256"], f"hash {name}")
        inputs[name] = load(path)

    coverage = inputs["coverage_report"]
    branch = inputs["branch_isotopy"]
    boundary = inputs["boundary_isotopy"]
    joint = inputs["joint_isotopy"]
    audit = inputs["joint_replay_audit"]
    index = inputs["shared_parameter_result_index"]
    require(coverage["complete"] is True, "coverage complete")
    require(coverage["branch"]["certified_intervals"] == 2195, "branch coverage")
    require(coverage["boundary"]["certified_intervals"] == 2195, "boundary coverage")
    require(branch["counts"]["source_intervals"] == boundary["counts"]["source_intervals"] == 2195, "component intervals")
    require(all(branch["checks"].values()) and not any(branch["guardrails"].values()), "branch")
    require(all(boundary["checks"].values()) and not any(boundary["guardrails"].values()), "boundary")
    require(all(joint["checks"].values()) and not any(joint["guardrails"].values()), "joint")
    require(joint["inputs"]["branch_aggregate_sha256"] == packet["inputs"]["branch_isotopy"]["sha256"], "joint branch")
    require(joint["inputs"]["boundary_aggregate_sha256"] == packet["inputs"]["boundary_isotopy"]["sha256"], "joint boundary")
    mixed_total = sum(joint["counts"][key] for key in ("mixed_homotopy_rectangle_certificates", "mixed_homotopy_convex_region_certificates", "mixed_homotopy_targeted_certificates"))
    require(mixed_total == 28295568, "mixed total")
    require(index["complete"] is True, "result index")
    require(index["coverage"]["unique_targets"] == index["coverage"]["verified_targets"] == 463, "verified targets")
    require(audit["targeted_certificate_provenance"]["result_index_sha256"] == packet["inputs"]["shared_parameter_result_index"]["sha256"], "audit index")
    require(all(audit["counts"][key] == 0 for key in ("unresolved_common_refinement_atoms", "unresolved_label_pairs", "unresolved_source_intervals")), "audit unresolved")

    affine = inputs["conditional_affine_obstruction"]
    matrix = affine["action_mod2"]
    translation = [int(v) & 1 for v in affine["affine_translation_mod2"]]
    witness = [int(v) & 1 for v in affine["mod2_obstruction_witness"]]
    delta = [[int(matrix[r][c]) ^ int(r == c) for c in range(164)] for r in range(164)]
    require(rank_mod_two(matrix) == 164, "rank M")
    require(rank_mod_two(delta) == 42, "rank M-I")
    require(all(sum(witness[r] * delta[r][c] for r in range(164)) % 2 == 0 for c in range(164)), "left witness")
    require(sum(witness[r] * translation[r] for r in range(164)) % 2 == 1, "pairing")
    replay = inputs["independent_affine_replay"]
    require(replay["all_jobs_observed"] is True, "replay observed")
    require(replay["job"]["observed_state"] == "succeeded", "replay state")
    require(replay["job"]["exact_payload_match"] is True, "replay equality")
    require(replay["job"]["retrieved_payload_sha256"] == packet["inputs"]["conditional_affine_obstruction"]["sha256"], "replay payload")
    require(packet["decision"] == "READY_FOR_B89_PROMOTION", "decision")
    require(all(packet["checks"].values()) and not any(packet["guardrails"].values()), "claim boundary")
    print("CBF.T54 independent replay: PASS branch=2195/2195 boundary=2195/2195 mixed=28295568 promotion=ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
