#!/usr/bin/env python3
"""Independently verify one shared-parameter mixed campaign slice."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import verify_q79_b89_joint_shared_parameter as child_verifier


HERE = Path(__file__).resolve().parent
WORKER = HERE / "q79_b89_joint_shared_parameter_worker.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_key(row: dict) -> tuple[int, int, Fraction, Fraction, int, int]:
    return (
        int(row["edge"]), int(row["interval"]),
        Fraction(row["fraction"][0]), Fraction(row["fraction"][1]),
        int(row["branch_label"]), int(row["boundary_label"]),
    )


def child_key(packet: dict, edge: int):
    return (
        edge, int(packet["interval"]),
        Fraction(packet["cell_fraction"][0]), Fraction(packet["cell_fraction"][1]),
        int(packet["branch_label"]), int(packet["boundary_label"]),
    )


def verify_component_checks(packet: dict) -> None:
    require(all(packet["checks"].values()), "child worker checks")
    require(not any(packet["guardrails"].values()), "child guardrails")
    components = packet["component_packets"]
    branch_checks = dict(components["branch"]["checks"])
    require(
        branch_checks.pop(
            "all_within_shard_adjacent_cells_have_unique_overlap_label_bindings"
        ) is False,
        "single-cell branch binding flag",
    )
    require(all(branch_checks.values()) and not components["branch"]["failures"], "branch component")
    require(all(components["boundary"]["checks"].values()) and not components["boundary"]["failures"], "boundary component")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--diagnostic", required=True, type=Path)
    parser.add_argument("--branch-source", required=True, type=Path)
    parser.add_argument("--branch-guides", required=True, type=Path)
    parser.add_argument("--branch-metadata", required=True, type=Path)
    parser.add_argument("--boundary-source", required=True, type=Path)
    parser.add_argument("--boundary-guides", required=True, type=Path)
    parser.add_argument("--boundary-metadata", required=True, type=Path)
    args = parser.parse_args()
    packet = json.loads(args.packet.resolve().read_text(encoding="ascii"))
    diagnostic = json.loads(args.diagnostic.resolve().read_text(encoding="ascii"))
    require(
        packet["schema"]
        == "mtt.cbf.q79-b89-joint-shared-parameter-campaign-slice.v1",
        "schema",
    )
    require(all(packet["checks"].values()), "campaign checks")
    require(not any(packet["guardrails"].values()), "campaign guardrails")
    require(packet["inputs"]["diagnostic_sha256"] == sha256(args.diagnostic.resolve()), "diagnostic hash")
    require(packet["inputs"]["worker_sha256"] == sha256(WORKER), "worker hash")
    for name in (
        "branch_source", "branch_guides", "branch_metadata",
        "boundary_source", "boundary_guides", "boundary_metadata",
    ):
        require(
            packet["inputs"][f"{name}_sha256"]
            == sha256(Path(getattr(args, name)).resolve()),
            f"input hash {name}",
        )
    edge = int(packet["edge"])
    interval_start, interval_stop = map(int, packet["interval_range"])
    targets = {
        target_key(row) for row in diagnostic["unresolved_mixed_pairs"]
        if int(row["edge"]) == edge
        and interval_start <= int(row["interval"]) < interval_stop
    }
    children = packet["target_packets"]
    require(len(children) == packet["target_count"], "declared child count")
    require({child_key(child, edge) for child in children} == targets, "exact target set")
    minimum = None
    leaves = 0
    for child in children:
        verify_component_checks(child)
        for name in (
            "branch_source", "branch_guides", "branch_metadata",
            "boundary_source", "boundary_guides", "boundary_metadata",
        ):
            require(
                child["inputs"][name] == packet["inputs"][f"{name}_sha256"],
                f"child input binding {name}",
            )
        replay = child_verifier.replay(child)
        leaves += replay["leaves"]
        margin = replay["minimum_strict_margin"]
        minimum = margin if minimum is None else min(minimum, margin)
    require(minimum is not None and minimum > 0, "positive global slice margin")
    print(json.dumps({
        "all_passed": True,
        "edge": edge,
        "interval_range": [interval_start, interval_stop],
        "targets": len(targets),
        "certified_parameter_leaves": leaves,
        "minimum_strict_margin": minimum,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
