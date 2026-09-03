#!/usr/bin/env python3
"""Independently replay a residual-aware shared-parameter mixed certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deserialize_arb(bounds: list[str]) -> arb:
    lower, upper = map(arb, bounds)
    return (lower + upper) / 2 + arb(0, (upper - lower) / 2)


def deserialize_acb(value: dict[str, list[str]]) -> acb:
    return acb(deserialize_arb(value["real"]), deserialize_arb(value["imag"]))


def difference(left, right):
    return [
        a - b
        for a, b in itertools.zip_longest(left, right, fillvalue=acb(0))
    ]


def evaluate(values, parameter):
    result = acb(0)
    for coefficient in reversed(values):
        result = result * parameter + coefficient
    return result


def parameter_ball(left: Fraction, right: Fraction) -> arb:
    midpoint = (left + right) / 2
    radius = (right - left) / 2
    return arb(
        f"{midpoint.numerator}/{midpoint.denominator}",
        f"{radius.numerator}/{radius.denominator}",
    )


def replay(packet: dict) -> dict:
    ctx.prec = int(packet["proof_policy"]["precision_bits"])
    predictor = [deserialize_acb(value) for value in packet["predictor_difference"]]
    guide = [deserialize_acb(value) for value in packet["guide_difference"]]
    displacement = difference(guide, predictor)
    radius = packet["source_residual_radius"]
    error = acb(arb(0, radius), arb(0, radius))
    error_upper = error.abs_upper()
    leaves = packet["certified_parameter_leaves"]
    require(bool(leaves), "nonempty finite leaf cover")
    ordered = sorted(leaves, key=lambda row: Fraction(row["fraction"][0]))
    require(Fraction(ordered[0]["fraction"][0]) == -1, "left endpoint")
    require(Fraction(ordered[-1]["fraction"][1]) == 1, "right endpoint")
    require(
        all(
            Fraction(left["fraction"][1]) == Fraction(right["fraction"][0])
            for left, right in zip(ordered, ordered[1:])
        ),
        "gap-free leaf cover",
    )
    minimum = math.inf
    for leaf in ordered:
        left, right = map(Fraction, leaf["fraction"])
        require(left < right, "positive leaf width")
        require(
            int(leaf["depth"])
            <= int(packet["proof_policy"]["maximum_parameter_depth"]),
            "bounded leaf depth",
        )
        parameter = parameter_ball(left, right)
        source_predictor = evaluate(predictor, parameter)
        if leaf["method"] == "residual_aware_Rouche":
            margin = float(
                source_predictor.abs_lower()
                - evaluate(displacement, parameter).abs_upper()
                - error_upper
            )
        elif leaf["method"] == "residual_aware_alignment":
            product = (source_predictor + error).conjugate() * evaluate(
                guide, parameter
            )
            margin = max(float(product.imag.abs_lower()), float(product.real.lower()))
        else:
            raise AssertionError(f"recognized proof method {leaf['method']}")
        require(math.isfinite(margin) and margin > 0, "strict replayed margin")
        require(float(leaf["strict_margin"]) == margin, "exact serialized margin replay")
        minimum = min(minimum, margin)
    return {"leaves": len(ordered), "minimum_strict_margin": minimum}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--baseline-root", required=True, type=Path)
    parser.add_argument("--branch-source", required=True, type=Path)
    parser.add_argument("--branch-guides", required=True, type=Path)
    parser.add_argument("--branch-metadata", required=True, type=Path)
    parser.add_argument("--boundary-source", required=True, type=Path)
    parser.add_argument("--boundary-guides", required=True, type=Path)
    parser.add_argument("--boundary-metadata", required=True, type=Path)
    args = parser.parse_args()
    packet = json.loads(args.packet.resolve().read_text(encoding="ascii"))
    require(
        packet["schema"] == "mtt.cbf.q79-b89-joint-shared-parameter-homotopy.v1",
        "schema",
    )
    require(all(packet["checks"].values()), "worker checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    paths = {
        name: Path(getattr(args, name)).resolve()
        for name in (
            "branch_source", "branch_guides", "branch_metadata",
            "boundary_source", "boundary_guides", "boundary_metadata",
        )
    }
    for name, path in paths.items():
        require(packet["inputs"][name] == sha256(path), f"input hash {name}")
    baseline = args.baseline_root.resolve()
    require(
        packet["inputs"]["branch_baseline_sha256"]
        == sha256(baseline / "experiments/q79_eta9_b89_family_branch_braid_pilot/certify_rectangle_family_taylor_flint.py"),
        "branch baseline hash",
    )
    require(
        packet["inputs"]["boundary_baseline_sha256"]
        == sha256(baseline / "experiments/q79_eta9_b89_family_branch_braid_pilot/certify_right80_boundary_taylor_flint.py"),
        "boundary baseline hash",
    )
    require(
        packet["inputs"]["relaxed_branch_wrapper_sha256"]
        == sha256(HERE / "q79_b89_relaxed_predictor_source_isotopy_worker.py"),
        "relaxed wrapper hash",
    )
    require(
        packet["inputs"]["boundary_direct_wrapper_sha256"]
        == sha256(HERE / "q79_b89_boundary_direct_homotopy_cell_worker.py"),
        "boundary wrapper hash",
    )
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
    result = replay(packet)
    print(json.dumps({
        "all_passed": True,
        "interval": packet["interval"],
        "pair": [packet["branch_label"], packet["boundary_label"]],
        **result,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
