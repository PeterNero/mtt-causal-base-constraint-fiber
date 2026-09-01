#!/usr/bin/env python3
"""Assemble complete local carriers and invoke the frozen H4-T123--126 promotion."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
READINESS = ROOT / "q79_b89_downstream_promotion_readiness.packet.json"
BRANCH = ROOT / "q79_b89_accelerated_source_isotopy_branch_aggregate.json"
BOUNDARY = ROOT / "q79_b89_accelerated_source_isotopy_boundary_aggregate.json"
JOINT = ROOT / "q79_b89_accelerated_source_isotopy_joint_aggregate.json"
OUTPUT = ROOT / "q79_b89_same_source_deligne_obstruction.packet.json"
CERTIFICATES = ROOT / "certificates"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None, f"module {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def promotion_ready(packet: dict) -> bool:
    coverage = packet.get("coverage", {})
    return (
        packet.get("theorem_id") == "CBF.T54"
        and packet.get("decision") == "READY_FOR_JOINT_ASSEMBLY_AND_B89_PROMOTION"
        and coverage.get("branch", {}).get("certified_intervals") == 2195
        and coverage.get("branch", {}).get("complete") is True
        and coverage.get("boundary", {}).get("certified_intervals") == 2195
        and coverage.get("boundary", {}).get("complete") is True
        and all(packet.get("checks", {}).values())
        and not any(packet.get("guardrails", {}).values())
    )


def configure_builder(module, upstream: Path) -> None:
    common = ROOT.parent
    pilot = upstream / "experiments/q79_eta9_b89_family_branch_braid_pilot"
    upstream_certificates = upstream / "certificates"
    module.ROOT = common
    module.OUTPUT = OUTPUT
    module.CERTIFICATES = CERTIFICATES
    module.INPUTS = {
        "H4_T122_exact_carrier": upstream_certificates / "h4_q79_eta9_b89_exact_integral_carrier.json",
        "H4_T113_signed_boundary": upstream_certificates / "h4_q79_eta9_b89_certified_signed_boundary_braid.json",
        "H4_T116_connector_free_parity": upstream_certificates / "h4_q79_eta9_b89_selected_rectangle_connector_free_parity.json",
        "H4_T118_integral_marking": upstream_certificates / "h4_q79_eta9_b89_certified_comb_h1_intertwiner.json",
        "H4_T119_boundary_spokes": upstream_certificates / "h4_q79_eta9_b89_certified_boundary_spoke_frame.json",
        "H4_T120_affine_Deligne_adapter_certificate": upstream_certificates / "h4_q79_eta9_b89_affine_deligne_adapter.json",
        "H4_T120_affine_Deligne_adapter_packet": upstream / "experiments/q79_eta9_b89_affine_deligne_adapter/q79_eta9_b89_affine_deligne_adapter.packet.json",
        "branch_isotopy": BRANCH,
        "boundary_isotopy": BOUNDARY,
        "joint_isotopy": JOINT,
        "joint_Artin": pilot / "outputs/certified-common-grid-right80-joint-artin.json",
        "segmented_adapter": pilot / "outputs/certified-common-grid-right80-segmented-adapter.json",
        "certified_affine_obstruction": pilot / "outputs/certified-common-grid-right80-mod2-affine-obstruction.json",
        "conditional_affine_obstruction": pilot / "outputs/family-global-right80-plus-rectangle-mod2-affine-obstruction.json",
        "independent_affine_replay_campaign": pilot / "kernel_certified_affine_replay_campaign.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream-root",
        default=str(ROOT.parent / "mtt-preprojection-repair-calculus"),
    )
    parser.add_argument("--skip-assembly", action="store_true")
    arguments = parser.parse_args()
    upstream = Path(arguments.upstream_root).resolve()

    require(READINESS.is_file(), "missing CBF.T54 readiness packet")
    require(
        promotion_ready(load(READINESS)),
        "promotion refused: exact branch and boundary coverage must both be 2195/2195",
    )
    if not arguments.skip_assembly:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "q79_b89_accelerated_source_isotopy_finalize.py"),
                "--upstream-root",
                str(upstream),
                "--result-index",
                str(ROOT / "q79_b89_accelerated_source_isotopy_result_index.json"),
            ],
            cwd=ROOT,
            check=True,
        )
    for path in (BRANCH, BOUNDARY, JOINT):
        require(path.is_file(), f"missing assembled carrier {path.name}")

    source = upstream / "experiments/q79_eta9_b89_certified_affine_deligne_obstruction/build.py"
    require(source.is_file(), f"missing frozen promotion builder {source}")
    CERTIFICATES.mkdir(parents=True, exist_ok=True)
    builder = load_module("cbf_b89_h4_t123_t126_builder", source)
    configure_builder(builder, upstream)
    require(builder.main() == 0, "H4-T123--126 builder")
    print(f"CBF B89 terminal promotion: PASS packet={OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
