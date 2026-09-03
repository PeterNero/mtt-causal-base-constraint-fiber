#!/usr/bin/env python3
"""Recursively split component-hard cells before shared-parameter certification."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from q79_b89_joint_shared_parameter_campaign_worker import WORKER, key, require, sha256


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--diagnostic", required=True)
    parser.add_argument("--edge", type=int, required=True)
    parser.add_argument("--interval-start", type=int, required=True)
    parser.add_argument("--interval-stop", type=int, required=True)
    parser.add_argument("--branch-source", required=True)
    parser.add_argument("--branch-guides", required=True)
    parser.add_argument("--branch-metadata", required=True)
    parser.add_argument("--boundary-source", required=True)
    parser.add_argument("--boundary-guides", required=True)
    parser.add_argument("--boundary-metadata", required=True)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--max-depth", type=int, default=24)
    parser.add_argument("--component-max-depth", type=int, default=6)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    diagnostic_path = Path(args.diagnostic).resolve()
    diagnostic = json.loads(diagnostic_path.read_text(encoding="ascii"))
    targets = sorted({
        key(row) for row in diagnostic["unresolved_mixed_pairs"]
        if int(row["edge"]) == args.edge
        and args.interval_start <= int(row["interval"]) < args.interval_stop
    })
    require(bool(targets), "nonempty repair target slice")
    packets = []
    with tempfile.TemporaryDirectory(prefix="mtt-joint-shared-repair-") as temporary:
        temporary = Path(temporary)
        for target_index, target in enumerate(targets):
            edge, interval, parent_start, parent_stop, branch_label, boundary_label = target
            pending = [(parent_start, parent_stop, 0)]
            while pending:
                start, stop, depth = pending.pop()
                child = temporary / (
                    f"target-{target_index}-d{depth}-"
                    f"{start.numerator}of{start.denominator}-"
                    f"{stop.numerator}of{stop.denominator}.json"
                )
                command = [
                    sys.executable, str(WORKER),
                    "--baseline-root", args.baseline_root,
                    "--interval", str(interval),
                    "--branch-label", str(branch_label),
                    "--boundary-label", str(boundary_label),
                    "--cell-fraction-start", str(start),
                    "--cell-fraction-stop", str(stop),
                    "--branch-source", args.branch_source,
                    "--branch-guides", args.branch_guides,
                    "--branch-metadata", args.branch_metadata,
                    "--boundary-source", args.boundary_source,
                    "--boundary-guides", args.boundary_guides,
                    "--boundary-metadata", args.boundary_metadata,
                    "--precision", str(args.precision),
                    "--max-depth", str(args.max_depth),
                    "--output", str(child),
                ]
                completed = subprocess.run(
                    command, capture_output=True, text=True, check=False
                )
                if completed.returncode == 0:
                    packets.append(json.loads(child.read_text(encoding="ascii")))
                    continue
                require(
                    depth < args.component_max_depth,
                    completed.stdout + completed.stderr,
                )
                midpoint = (start + stop) / 2
                pending.append((midpoint, stop, depth + 1))
                pending.append((start, midpoint, depth + 1))
            print(
                f"target={target_index + 1}/{len(targets)} interval={interval} "
                f"pair={branch_label},{boundary_label}",
                flush=True,
            )
    names = (
        "branch_source", "branch_guides", "branch_metadata",
        "boundary_source", "boundary_guides", "boundary_metadata",
    )
    output = {
        "schema": "mtt.cbf.q79-b89-joint-shared-parameter-repair-slice.v1",
        "tier": "CERTIFIED_COMPONENT_ADAPTIVE_SHARED_PARAMETER_MIXED_HOMOTOPY",
        "edge": args.edge,
        "interval_range": [args.interval_start, args.interval_stop],
        "target_count": len(targets),
        "certificate_count": len(packets),
        "target_packets": packets,
        "inputs": {
            "diagnostic_sha256": sha256(diagnostic_path),
            "worker_sha256": sha256(WORKER),
            **{
                f"{name}_sha256": sha256(Path(getattr(args, name)).resolve())
                for name in names
            },
        },
        "policy": {"component_max_depth": args.component_max_depth},
        "checks": {
            "every_target_has_a_finite_gap_free_component_subdivision": True,
            "every_subcell_has_a_residual_aware_shared_parameter_certificate": True,
            "all_sources_and_workers_are_hash_bound": True,
        },
        "guardrails": {
            "claims_targets_outside_this_slice": False,
            "claims_complete_joint_isotopy": False,
            "claims_B89_or_beta_C": False,
        },
    }
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="ascii", newline="\n",
    )
    print(
        f"shared-parameter repair PASS targets={len(targets)} "
        f"certificates={len(packets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
