#!/usr/bin/env python3
"""Ingest and independently verify the complete shared-parameter T53 campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from fractions import Fraction
from pathlib import Path, PurePosixPath

import verify_q79_b89_joint_shared_parameter as child_verifier


HERE = Path(__file__).resolve().parent
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


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="ascii", newline="\n",
    )
    temporary.replace(path)


def jobs_root(path: Path) -> Path:
    path = path.resolve()
    return path / "jobs" if (path / "jobs").is_dir() else path


def safe_member(name: str) -> None:
    path = PurePosixPath(name)
    require("\\" not in name and not path.is_absolute() and ".." not in path.parts, f"safe member {name}")


def target_key(row: dict):
    return (
        int(row["edge"]), int(row["interval"]),
        Fraction(row["fraction"][0]), Fraction(row["fraction"][1]),
        int(row["branch_label"]), int(row["boundary_label"]),
    )


def child_key(child: dict, edge: int):
    return (
        edge, int(child["interval"]),
        Fraction(child["cell_fraction"][0]), Fraction(child["cell_fraction"][1]),
        int(child["branch_label"]), int(child["boundary_label"]),
    )


def extract(row: dict, runtime: Path, result_root: Path) -> tuple[dict, Path, dict]:
    directory = runtime / row["id"]
    job = json.loads((directory / "job.json").read_text(encoding="utf-8"))
    require(job["state"] == "succeeded" and job["exit_code"] == 0, f"successful job {row['id']}")
    require(job["input_capsule"]["sha256"] == row["input_capsule_sha256"], "input capsule binding")
    require(sha256(directory / "input-capsule.zip") == row["input_capsule_sha256"], "stored input capsule")
    capsule = directory / "result-capsule.zip"
    require(job["result"]["available"] is True and sha256(capsule) == job["result"]["sha256"], "result capsule")
    with zipfile.ZipFile(capsule) as archive:
        for name in archive.namelist():
            safe_member(name)
        manifest_bytes = archive.read(RESULT_MANIFEST)
        require(sha256_bytes(manifest_bytes) == job["result"]["manifest_sha256"], "result manifest hash")
        manifest = json.loads(manifest_bytes.decode("ascii"))
        require(manifest["job_id"] == row["id"] and manifest["exit_code"] == 0, "result process binding")
        require(manifest["input_capsule_sha256"] == row["input_capsule_sha256"], "result input binding")
        require(manifest["file_count"] == 1, "one output")
        file_row = manifest["files"][0]
        require(file_row["path"] == row["output"], "output path binding")
        payload = archive.read(file_row["path"])
        require(len(payload) == file_row["bytes"] and sha256_bytes(payload) == file_row["sha256"], "output payload binding")
    destination = result_root / row["id"] / PurePosixPath(row["output"]).name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return json.loads(payload.decode("ascii")), destination, job


def verification_command(packet: Path, edge: int, repair: bool, diagnostic: Path, upstream: Path) -> list[str]:
    pilot = upstream / "experiments/q79_eta9_b89_family_branch_braid_pilot/kernel_inputs"
    verifier = (
        "verify_q79_b89_joint_shared_parameter_repair.py"
        if repair else "verify_q79_b89_joint_shared_parameter_campaign.py"
    )
    return [
        sys.executable, str(HERE / verifier), "--packet", str(packet),
        "--diagnostic", str(diagnostic),
        "--branch-source", str(upstream / "experiments/q79_eta9_b89_relative_adjoint_compiler/q79_eta9_b89_relative_adjoint_worker_input.json"),
        "--branch-guides", str(pilot / f"right80-edge{edge}-guides.npz"),
        "--branch-metadata", str(pilot / f"right80-edge{edge}-guides.json"),
        "--boundary-source", str(upstream / "experiments/q79_eta9_b89_branch_forms/q79_eta9_b89_branch_form_worker_input.json"),
        "--boundary-guides", str(pilot / f"right80-boundary-edge{edge}-guides.npz"),
        "--boundary-metadata", str(pilot / f"right80-boundary-edge{edge}-guides.json"),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--upstream-root", required=True, type=Path)
    parser.add_argument("--campaign", type=Path, default=HERE / "q79_b89_joint_shared_parameter_campaign.json")
    parser.add_argument("--repair-campaign", type=Path, default=HERE / "q79_b89_joint_shared_parameter_repair_campaign.json")
    parser.add_argument("--result-root", type=Path, default=HERE / "q79_b89_joint_shared_parameter_results")
    args = parser.parse_args()
    campaign = load(args.campaign.resolve())
    repair_campaign = load(args.repair_campaign.resolve())
    diagnostic = (HERE / campaign["source_locks"]["diagnostic"]["path"]).resolve()
    diagnostic_packet = load(diagnostic)
    all_targets = {target_key(row) for row in diagnostic_packet["unresolved_mixed_pairs"]}
    runtime = jobs_root(args.runtime_root)
    upstream = args.upstream_root.resolve()
    result_root = args.result_root.resolve()
    replaced = repair_campaign["replaces_job_id"]
    rows = [(row, False) for row in campaign["jobs"] if row["id"] != replaced]
    rows.append((repair_campaign["job"], True))
    covered = set()
    records = []
    target_certificates = []
    for row, repair in rows:
        packet, destination, job = extract(row, runtime, result_root)
        completed = subprocess.run(
            verification_command(destination, int(row["edge"]), repair, diagnostic, upstream),
            cwd=HERE, capture_output=True, text=True, check=False,
        )
        require(completed.returncode == 0, completed.stdout + completed.stderr)
        replay = json.loads(completed.stdout)
        require(replay["all_passed"] is True, "independent campaign replay")
        selected = {
            target for target in all_targets
            if target[0] == int(row["edge"])
            and int(row["interval_start"]) <= target[1] < int(row["interval_stop"])
        }
        grouped = {target: [] for target in selected}
        for child in packet["target_packets"]:
            key = child_key(child, int(row["edge"]))
            parents = [
                target for target in selected
                if target[0] == key[0] and target[1] == key[1]
                and target[2] <= key[2] < key[3] <= target[3]
                and target[4:] == key[4:]
            ]
            require(len(parents) == 1, "child has one diagnostic parent")
            child_replay = child_verifier.replay(child)
            grouped[parents[0]].append((key[2], key[3], child_replay["minimum_strict_margin"]))
        for target, cells in grouped.items():
            cells.sort()
            require(bool(cells), "target is certified")
            require(cells[0][0] == target[2] and cells[-1][1] == target[3], "target endpoints")
            require(all(left[1] == right[0] for left, right in zip(cells, cells[1:])), "target gap-free")
            require(target not in covered, "target unique across jobs")
            covered.add(target)
            target_certificates.append({
                "edge": target[0], "interval": target[1],
                "fraction": [str(target[2]), str(target[3])],
                "branch_label": target[4], "boundary_label": target[5],
                "component_subcells": len(cells),
                "minimum_strict_margin": min(cell[2] for cell in cells),
                "packet_sha256": sha256(destination),
            })
        records.append({
            "job_id": row["id"], "repair": repair,
            "edge": int(row["edge"]),
            "interval_range": [int(row["interval_start"]), int(row["interval_stop"])],
            "packet_path": str(destination.relative_to(HERE)).replace("\\", "/"),
            "packet_sha256": sha256(destination),
            "result_capsule_sha256": job["result"]["sha256"],
            "independent_verifier": Path(verification_command(destination, int(row["edge"]), repair, diagnostic, upstream)[1]).name,
            "verifier_result": replay,
        })
    require(covered == all_targets, "all 463 unique targets independently certified")
    index = {
        "schema": "mtt.cbf.q79-b89-joint-shared-parameter-result-index.v1",
        "complete": True,
        "campaign_sha256": sha256(args.campaign.resolve()),
        "repair_campaign_sha256": sha256(args.repair_campaign.resolve()),
        "diagnostic_sha256": sha256(diagnostic),
        "coverage": {
            "diagnostic_atoms": len(diagnostic_packet["unresolved_mixed_pairs"]),
            "unique_targets": len(all_targets),
            "verified_targets": len(covered),
            "result_packets": len(records),
        },
        "results": records,
        "target_certificates": sorted(
            target_certificates,
            key=lambda row: (
                row["edge"], row["interval"], Fraction(row["fraction"][0]),
                row["branch_label"], row["boundary_label"],
            ),
        ),
    }
    write_json(result_root / "index.json", index)
    print(json.dumps({"all_passed": True, **index["coverage"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
