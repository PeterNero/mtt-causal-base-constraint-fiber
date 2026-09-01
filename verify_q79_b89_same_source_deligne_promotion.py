#!/usr/bin/env python3
"""Independent H4-T123--126 replay for the local same-source B89 promotion."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_b89_same_source_deligne_obstruction.packet.json"
CERTIFICATE_DIR = ROOT / "certificates"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None, f"module {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream-root",
        default=str(ROOT.parent / "mtt-preprojection-repair-calculus"),
    )
    arguments = parser.parse_args()
    upstream = Path(arguments.upstream_root).resolve()
    source = upstream / "experiments/q79_eta9_b89_certified_affine_deligne_obstruction/verify.py"
    require(source.is_file(), f"missing frozen independent verifier {source}")
    verifier = load_module("cbf_b89_h4_t123_t126_verifier", source)
    verifier.ROOT = ROOT.parent
    verifier.PACKET = PACKET
    verifier.CERTIFICATES = {
        "H4-T123": CERTIFICATE_DIR / "h4_q79_eta9_b89_certified_exact_source_branch_isotopy.json",
        "H4-T124": CERTIFICATE_DIR / "h4_q79_eta9_b89_certified_signed_boundary_isotopy.json",
        "H4-T125": CERTIFICATE_DIR / "h4_q79_eta9_b89_certified_joint_288_strand_isotopy.json",
        "H4-T126": CERTIFICATE_DIR / "h4_q79_eta9_b89_certified_affine_deligne_obstruction.json",
    }
    return int(verifier.main())


if __name__ == "__main__":
    raise SystemExit(main())
