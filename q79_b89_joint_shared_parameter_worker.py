#!/usr/bin/env python3
"""Certify one mixed B89 pair using its shared source and homotopy parameters."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from flint import acb, arb, ctx

import q79_b89_boundary_direct_homotopy_cell_worker as boundary_direct
import q79_b89_relaxed_predictor_source_isotopy_worker as relaxed


BRANCH_RELATIVE = Path(
    "experiments/q79_eta9_b89_family_branch_braid_pilot/"
    "certify_rectangle_family_taylor_flint.py"
)
BOUNDARY_RELATIVE = Path(
    "experiments/q79_eta9_b89_family_branch_braid_pilot/"
    "certify_right80_boundary_taylor_flint.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def serialize_acb(value: acb) -> dict[str, list[str]]:
    return {
        "real": [
            repr(math.nextafter(float(value.real.lower()), -math.inf)),
            repr(math.nextafter(float(value.real.upper()), math.inf)),
        ],
        "imag": [
            repr(math.nextafter(float(value.imag.lower()), -math.inf)),
            repr(math.nextafter(float(value.imag.upper()), math.inf)),
        ],
    }


def deserialize_arb(bounds: list[str]) -> arb:
    lower, upper = map(arb, bounds)
    return (lower + upper) / 2 + arb(0, (upper - lower) / 2)


def deserialize_acb(value: dict[str, list[str]]) -> acb:
    return acb(deserialize_arb(value["real"]), deserialize_arb(value["imag"]))


def serialize_polynomial(values) -> list[dict[str, list[str]]]:
    return [serialize_acb(value) for value in values]


def polynomial_difference(left, right):
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


def residual_box(radius: str) -> acb:
    value = arb(0, radius)
    return acb(value, value)


def certify_shared_homotopy(
    predictor_difference,
    guide_difference,
    residual_radius: str,
    max_depth: int,
) -> list[dict]:
    displacement = polynomial_difference(guide_difference, predictor_difference)
    error = residual_box(residual_radius)
    error_upper = error.abs_upper()
    pending = [(Fraction(-1), Fraction(1), 0)]
    leaves = []
    while pending:
        left, right, depth = pending.pop()
        parameter = parameter_ball(left, right)
        predictor = evaluate(predictor_difference, parameter)
        shift = evaluate(displacement, parameter)
        rouche_margin = predictor.abs_lower() - shift.abs_upper() - error_upper
        if rouche_margin > 0:
            leaves.append({
                "fraction": [str(left), str(right)],
                "depth": depth,
                "method": "residual_aware_Rouche",
                "strict_margin": repr(float(rouche_margin)),
            })
            continue
        source = predictor + error
        guide = evaluate(guide_difference, parameter)
        product = source.conjugate() * guide
        cross_margin = product.imag.abs_lower()
        dot_margin = product.real.lower()
        alignment_margin = max(float(cross_margin), float(dot_margin))
        if math.isfinite(alignment_margin) and alignment_margin > 0:
            leaves.append({
                "fraction": [str(left), str(right)],
                "depth": depth,
                "method": "residual_aware_alignment",
                "strict_margin": repr(alignment_margin),
            })
            continue
        require(depth < max_depth, f"shared-parameter proof exhausted depth={max_depth}")
        midpoint = (left + right) / 2
        pending.append((midpoint, right, depth + 1))
        pending.append((left, midpoint, depth + 1))
    return sorted(leaves, key=lambda row: Fraction(row["fraction"][0]))


def execute_components(args, directory: Path):
    baseline_root = Path(args.baseline_root).resolve()
    branch_path = baseline_root / BRANCH_RELATIVE
    boundary_path = baseline_root / BOUNDARY_RELATIVE
    branch = load_module("mtt_joint_shared_branch", branch_path)
    branch.high_precision_newton = lambda geometry, kind, x, y: (
        relaxed.relaxed_high_precision_newton(branch, geometry, kind, x, y)
    )
    branch_private = {}
    original_branch_homotopy = branch.certify_interval_guide_homotopy

    def capture_branch(tubes, predictor_degree, max_depth):
        matches = [tube for tube in tubes if int(tube["branch"]) == args.branch_label]
        require(len(matches) == 1, "one private branch predictor")
        branch_private.update(matches[0])
        return original_branch_homotopy(tubes, predictor_degree, max_depth)

    branch.certify_interval_guide_homotopy = capture_branch
    branch_output = directory / "branch.json"
    branch_arguments = [
        "--source", args.branch_source, "--guides", args.branch_guides,
        "--metadata", args.branch_metadata,
        "--interval-start", str(args.interval),
        "--interval-stop", str(args.interval + 1),
        "--branch-start", str(args.branch_label),
        "--branch-stop", str(args.branch_label + 1),
        "--precision", str(args.precision), "--predictor-degree", "12",
        "--taylor-order", "14", "--separation-max-depth", "24",
        "--cell-fraction-start", args.cell_fraction_start,
        "--cell-fraction-stop", args.cell_fraction_stop,
        "--output", str(branch_output),
    ]
    original_argv = sys.argv
    try:
        sys.argv = [str(branch_path), *branch_arguments]
        require(branch.main() == 0, "branch component execution")
    finally:
        sys.argv = original_argv

    boundary = load_module("mtt_joint_shared_boundary", boundary_path)
    boundary_private = {}

    def capture_boundary(tubes, predictor_degree, max_depth):
        matches = [tube for tube in tubes if int(tube["branch"]) == args.boundary_label]
        require(len(matches) == 1, "one private boundary predictor")
        boundary_private.update(matches[0])
        return boundary_direct.certified_guide_homotopy(
            boundary, tubes, predictor_degree, max_depth
        )

    boundary.certify_interval_guide_homotopy = capture_boundary
    boundary_output = directory / "boundary.json"
    boundary_arguments = [
        "--source", args.boundary_source, "--guides", args.boundary_guides,
        "--metadata", args.boundary_metadata,
        "--interval-start", str(args.interval),
        "--interval-stop", str(args.interval + 1),
        "--precision", str(args.precision), "--predictor-degree", "12",
        "--taylor-order", "14", "--separation-max-depth", "24",
        "--cell-fraction-start", args.cell_fraction_start,
        "--cell-fraction-stop", args.cell_fraction_stop,
        "--output", str(boundary_output),
    ]
    try:
        sys.argv = [str(boundary_path), *boundary_arguments]
        require(boundary.main() == 0, "boundary component execution")
    finally:
        sys.argv = original_argv
    return (
        branch_private,
        boundary_private,
        json.loads(branch_output.read_text(encoding="ascii")),
        json.loads(boundary_output.read_text(encoding="ascii")),
        branch_path,
        boundary_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--interval", type=int, required=True)
    parser.add_argument("--branch-label", type=int, required=True)
    parser.add_argument("--boundary-label", type=int, required=True)
    parser.add_argument("--branch-source", required=True)
    parser.add_argument("--branch-guides", required=True)
    parser.add_argument("--branch-metadata", required=True)
    parser.add_argument("--boundary-source", required=True)
    parser.add_argument("--boundary-guides", required=True)
    parser.add_argument("--boundary-metadata", required=True)
    parser.add_argument("--cell-fraction-start", default="0")
    parser.add_argument("--cell-fraction-stop", default="1")
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--max-depth", type=int, default=24)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    require(args.precision >= 256, "minimum precision")
    cell_start = Fraction(args.cell_fraction_start)
    cell_stop = Fraction(args.cell_fraction_stop)
    require(Fraction(0) <= cell_start < cell_stop <= Fraction(1), "cell fraction")
    ctx.prec = args.precision
    with tempfile.TemporaryDirectory(prefix="mtt-joint-shared-parameter-") as temporary:
        (
            branch, boundary, branch_packet, boundary_packet,
            branch_worker, boundary_worker,
        ) = execute_components(args, Path(temporary))
    predictor_payload = polynomial_difference(
        branch["predictor_x"], boundary["predictor_x"]
    )
    guide_payload = polynomial_difference(branch["guide_x"], boundary["guide_x"])
    residual_radius = repr(
        float(branch["x_residual_radius"] + boundary["x_residual_radius"])
    )
    serialized_predictor = serialize_polynomial(predictor_payload)
    serialized_guide = serialize_polynomial(guide_payload)
    predictor = [deserialize_acb(value) for value in serialized_predictor]
    guide = [deserialize_acb(value) for value in serialized_guide]
    leaves = certify_shared_homotopy(
        predictor, guide, residual_radius, args.max_depth
    )
    require(leaves[0]["fraction"][0] == "-1", "left endpoint")
    require(leaves[-1]["fraction"][1] == "1", "right endpoint")
    require(
        all(
            Fraction(left["fraction"][1]) == Fraction(right["fraction"][0])
            for left, right in zip(leaves, leaves[1:])
        ),
        "gap-free parameter cover",
    )
    inputs = {
        name: sha256(Path(getattr(args, name)).resolve())
        for name in (
            "branch_source", "branch_guides", "branch_metadata",
            "boundary_source", "boundary_guides", "boundary_metadata",
        )
    }
    inputs.update({
        "branch_baseline_sha256": sha256(branch_worker),
        "boundary_baseline_sha256": sha256(boundary_worker),
        "relaxed_branch_wrapper_sha256": sha256(Path(relaxed.__file__).resolve()),
        "boundary_direct_wrapper_sha256": sha256(Path(boundary_direct.__file__).resolve()),
    })
    output = {
        "schema": "mtt.cbf.q79-b89-joint-shared-parameter-homotopy.v1",
        "tier": "CERTIFIED_RESIDUAL_AWARE_SHARED_PARAMETER_MIXED_HOMOTOPY",
        "interval": args.interval,
        "branch_label": args.branch_label,
        "boundary_label": args.boundary_label,
        "cell_fraction": [str(cell_start), str(cell_stop)],
        "predictor_difference": serialized_predictor,
        "guide_difference": serialized_guide,
        "source_residual_radius": residual_radius,
        "proof_policy": {
            "precision_bits": args.precision,
            "maximum_parameter_depth": args.max_depth,
        },
        "certified_parameter_leaves": leaves,
        "component_packets": {"branch": branch_packet, "boundary": boundary_packet},
        "inputs": inputs,
        "checks": {
            "both_component_Krawczyk_certificates_pass": True,
            "shared_parameter_difference_preserves_source_correlation": True,
            "source_residual_radii_are_included": True,
            "every_parameter_leaf_excludes_zero_throughout_the_homotopy": True,
            "parameter_cover_is_finite_gap_free_and_endpoint_complete": True,
        },
        "guardrails": {
            "claims_other_mixed_pairs": False,
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
        f"shared-parameter mixed homotopy PASS interval={args.interval} "
        f"pair={args.branch_label},{args.boundary_label} leaves={len(leaves)} "
        f"depth={max(row['depth'] for row in leaves)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
