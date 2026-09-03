#!/usr/bin/env python3
"""Independently replay a component-adaptive shared-parameter repair slice."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from verify_q79_b89_joint_shared_parameter_campaign import (
    child_key,
    require,
    sha256,
    target_key,
    verify_component_checks,
)
import verify_q79_b89_joint_shared_parameter as child_verifier


HERE = Path(__file__).resolve().parent
WORKER = HERE / "q79_b89_joint_shared_parameter_worker.py"


def parent_key(child: dict, edge: int, targets: set[tuple]):
    interval = int(child["interval"])
    start, stop = map(Fraction, child["cell_fraction"])
    branch = int(child["branch_label"])
    boundary = int(child["boundary_label"])
    matches = [
        target for target in targets
        if target[0] == edge and target[1] == interval
        and target[2] <= start < stop <= target[3]
        and target[4:] == (branch, boundary)
    ]
    require(len(matches) == 1, "child belongs to one target parent")
    return matches[0]


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
        == "mtt.cbf.q79-b89-joint-shared-parameter-repair-slice.v1",
        "schema",
    )
    require(all(packet["checks"].values()), "worker checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    require(packet["inputs"]["diagnostic_sha256"] == sha256(args.diagnostic.resolve()), "diagnostic hash")
    require(packet["inputs"]["worker_sha256"] == sha256(WORKER), "worker hash")
    for name in (
        "branch_source", "branch_guides", "branch_metadata",
        "boundary_source", "boundary_guides", "boundary_metadata",
    ):
        require(packet["inputs"][f"{name}_sha256"] == sha256(Path(getattr(args, name)).resolve()), f"input hash {name}")
    edge = int(packet["edge"])
    interval_start, interval_stop = map(int, packet["interval_range"])
    targets = {
        target_key(row) for row in diagnostic["unresolved_mixed_pairs"]
        if int(row["edge"]) == edge
        and interval_start <= int(row["interval"]) < interval_stop
    }
    grouped = {target: [] for target in targets}
    minimum = None
    leaves = 0
    for child in packet["target_packets"]:
        parent = parent_key(child, edge, targets)
        grouped[parent].append(child)
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
    require(len(packet["target_packets"]) == packet["certificate_count"], "certificate count")
    require(len(targets) == packet["target_count"], "target count")
    for target, children in grouped.items():
        cells = sorted(
            [tuple(map(Fraction, child["cell_fraction"])) for child in children]
        )
        require(bool(cells), "target has children")
        require(cells[0][0] == target[2] and cells[-1][1] == target[3], "target endpoints")
        require(all(left[1] == right[0] for left, right in zip(cells, cells[1:])), "target gap-free cover")
    require(minimum is not None and minimum > 0, "positive repair margin")
    print(json.dumps({
        "all_passed": True,
        "edge": edge,
        "interval_range": [interval_start, interval_stop],
        "targets": len(targets),
        "certificates": len(packet["target_packets"]),
        "parameter_leaves": leaves,
        "minimum_strict_margin": minimum,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
