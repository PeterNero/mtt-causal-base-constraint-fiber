#!/usr/bin/env python3
"""Run shared-parameter mixed certificates for one diagnostic target slice."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKER = HERE / "q79_b89_joint_shared_parameter_worker.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(row: dict) -> tuple[int, int, Fraction, Fraction, int, int]:
    return (
        int(row["edge"]), int(row["interval"]),
        Fraction(row["fraction"][0]), Fraction(row["fraction"][1]),
        int(row["branch_label"]), int(row["boundary_label"]),
    )


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
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    diagnostic_path = Path(args.diagnostic).resolve()
    diagnostic = json.loads(diagnostic_path.read_text(encoding="ascii"))
    targets = sorted({
        key(row) for row in diagnostic["unresolved_mixed_pairs"]
        if int(row["edge"]) == args.edge
        and args.interval_start <= int(row["interval"]) < args.interval_stop
    })
    require(bool(targets), "nonempty shared-parameter target slice")
    packets = []
    with tempfile.TemporaryDirectory(prefix="mtt-joint-shared-campaign-") as temporary:
        temporary = Path(temporary)
        for index, target in enumerate(targets):
            edge, interval, start, stop, branch_label, boundary_label = target
            child = temporary / f"target-{index}.json"
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
            require(completed.returncode == 0, completed.stdout + completed.stderr)
            packet = json.loads(child.read_text(encoding="ascii"))
            require(
                (
                    edge, packet["interval"], [str(start), str(stop)],
                    branch_label, boundary_label,
                )
                == (
                    args.edge, interval, packet["cell_fraction"],
                    packet["branch_label"], packet["boundary_label"],
                ),
                "child target binding",
            )
            packets.append(packet)
            print(
                f"target={index + 1}/{len(targets)} interval={interval} "
                f"pair={branch_label},{boundary_label}",
                flush=True,
            )
    path_names = (
        "branch_source", "branch_guides", "branch_metadata",
        "boundary_source", "boundary_guides", "boundary_metadata",
    )
    output = {
        "schema": "mtt.cbf.q79-b89-joint-shared-parameter-campaign-slice.v1",
        "tier": "CERTIFIED_SHARED_PARAMETER_MIXED_HOMOTOPY_SLICE",
        "edge": args.edge,
        "interval_range": [args.interval_start, args.interval_stop],
        "target_count": len(targets),
        "target_packets": packets,
        "inputs": {
            "diagnostic_sha256": sha256(diagnostic_path),
            "worker_sha256": sha256(WORKER),
            **{
                f"{name}_sha256": sha256(Path(getattr(args, name)).resolve())
                for name in path_names
            },
        },
        "checks": {
            "every_selected_target_has_one_certificate": True,
            "every_child_component_certificate_passes": True,
            "every_child_shared_parameter_homotopy_excludes_zero": True,
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
        f"shared-parameter campaign PASS edge={args.edge} targets={len(targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
