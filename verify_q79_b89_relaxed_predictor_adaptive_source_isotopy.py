#!/usr/bin/env python3
"""Verify a B89 adaptive shard using the versioned relaxed-seed worker."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import verify_q79_b89_accelerated_adaptive_source_isotopy as verifier


HERE = Path(__file__).resolve().parent
WORKER = HERE / "q79_b89_relaxed_predictor_adaptive_source_isotopy_worker.py"
CELL_WORKER = HERE / "q79_b89_relaxed_predictor_source_isotopy_worker.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    arguments = list(sys.argv[1:])
    packet_path = Path(arguments[arguments.index("--packet") + 1]).resolve()
    packet = json.loads(packet_path.read_text(encoding="ascii"))
    policies = [
        subcell["accelerated_pair_certificate"].get("predictor_seed_policy")
        for row in packet["logical_rows"]
        for subcell in row["subcells"]
    ]
    require(bool(policies), "predictor seed policies")
    require(
        all(
            policy
            == {
                "maximum_iterations": 30,
                "refinement_threshold_bits": 52,
                "rigorous_acceptance_unchanged": True,
                "role": "nonproof_seed_for_interval_Krawczyk_validation",
            }
            for policy in policies
        ),
        "binary64-aware predictor seed policy",
    )
    verifier.WORKER = WORKER
    verifier.CELL_WORKER = CELL_WORKER
    verifier.main()


if __name__ == "__main__":
    main()
