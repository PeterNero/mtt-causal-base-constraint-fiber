#!/usr/bin/env python3
"""Add a direct interval fallback to one B89 boundary cell certificate.

The upstream Rouché test remains the first choice. If its sufficient inequality
cannot decide a pair, this wrapper eliminates the affine homotopy parameter from
H(s,a)=(1-a)P(s)+aG(s). A segment can contain zero only when P and G are
collinear and oppositely directed, so each parameter interval is certified by
nonzero Im(conj(P)G) or positive Re(conj(P)G).
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

from flint import acb, arb


CELL_RELATIVE = Path(
    "experiments/q79_eta9_b89_family_branch_braid_pilot/"
    "certify_right80_boundary_taylor_flint.py"
)
DIRECT_MAX_PARAMETER_DEPTH = 8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pop_option(arguments: list[str], name: str) -> str:
    try:
        index = arguments.index(name)
    except ValueError as error:
        raise SystemExit(f"missing required wrapper option {name}") from error
    require(index + 1 < len(arguments), f"value for {name}")
    value = arguments[index + 1]
    del arguments[index : index + 2]
    return value


def direct_homotopy_exclusion(
    module,
    predictor_difference,
    guide_difference,
    max_parameter_depth: int,
) -> dict | None:
    pending = [(Fraction(-1), Fraction(1), 0)]
    leaves = 0
    deepest_parameter = 0
    minimum_margin = math.inf
    while pending:
        s_left, s_right, s_depth = pending.pop()
        parameter = module.dyadic_parameter_ball(s_left, s_right)
        predictor = module.evaluate_univariate_polynomial(
            predictor_difference, parameter
        )
        guide = module.evaluate_univariate_polynomial(guide_difference, parameter)
        product = predictor.conjugate() * guide
        cross_margin = float(product.imag.abs_lower())
        dot_margin = float(product.real.lower())
        margin = max(cross_margin, dot_margin)
        if math.isfinite(margin) and margin > 0:
            leaves += 1
            deepest_parameter = max(deepest_parameter, s_depth)
            minimum_margin = min(minimum_margin, margin)
            continue
        if s_depth >= max_parameter_depth:
            return None
        midpoint = (s_left + s_right) / 2
        pending.append((midpoint, s_right, s_depth + 1))
        pending.append((s_left, midpoint, s_depth + 1))
    return {
        "leaf_intervals": leaves,
        "maximum_parameter_depth": deepest_parameter,
        "minimum_alignment_margin": minimum_margin,
    }


def certified_guide_homotopy(module, tubes, predictor_degree: int, max_depth: int):
    pair_count = 0
    coarse_pair_count = 0
    direct_polynomial_pair_count = 0
    direct_affine_pair_count = 0
    leaf_intervals = 0
    maximum_depth = 0
    minimum_margin = math.inf
    refined_pair_count = 0
    direct_parameter_intervals = 0
    maximum_parameter_depth = 0
    minimum_alignment_margin = math.inf

    for left, right in itertools.combinations(tubes, 2):
        pair_count += 1
        coarse_difference = left["predictor_x_box"] - right["predictor_x_box"]
        coarse_margin = float(
            coarse_difference.abs_lower()
            - left["guide_error_upper"]
            - right["guide_error_upper"]
        )
        if math.isfinite(coarse_margin) and coarse_margin > 0:
            coarse_pair_count += 1
            leaf_intervals += 1
            minimum_margin = min(minimum_margin, coarse_margin)
            continue

        predictor_difference = [
            a - b
            for a, b in itertools.zip_longest(
                left["predictor_x"][: predictor_degree + 1],
                right["predictor_x"][: predictor_degree + 1],
                fillvalue=acb(0),
            )
        ]
        guide_difference = [
            a - b
            for a, b in itertools.zip_longest(
                left["guide_x"], right["guide_x"], fillvalue=acb(0)
            )
        ]
        direct_polynomial_pair_count += 1
        result = module.certify_predictor_guide_pair_homotopy(
            left["predictor_x"][: predictor_degree + 1],
            right["predictor_x"][: predictor_degree + 1],
            left["guide_x"],
            right["guide_x"],
            max_depth,
        )
        if result is not None:
            refined_pair_count += int(result["maximum_depth"] > 0)
            leaf_intervals += result["leaf_intervals"]
            maximum_depth = max(maximum_depth, result["maximum_depth"])
            minimum_margin = min(minimum_margin, result["minimum_Rouche_margin"])
            continue

        direct = direct_homotopy_exclusion(
            module,
            predictor_difference,
            guide_difference,
            max_parameter_depth=DIRECT_MAX_PARAMETER_DEPTH,
        )
        if direct is None:
            raise ValueError(
                "direct predictor-guide homotopy failed branches="
                f"{left['branch']},{right['branch']}"
            )
        direct_affine_pair_count += 1
        refined_pair_count += 1
        direct_parameter_intervals += direct["leaf_intervals"]
        leaf_intervals += direct["leaf_intervals"]
        maximum_parameter_depth = max(
            maximum_parameter_depth, direct["maximum_parameter_depth"]
        )
        minimum_alignment_margin = min(
            minimum_alignment_margin, direct["minimum_alignment_margin"]
        )
        minimum_margin = min(minimum_margin, direct["minimum_alignment_margin"])

    return {
        "certified_pairs": pair_count,
        "coarse_pairs": coarse_pair_count,
        "direct_polynomial_pairs": direct_polynomial_pair_count,
        "refined_pair_count": refined_pair_count,
        "leaf_intervals": leaf_intervals,
        "maximum_refinement_depth": max(
            maximum_depth, maximum_parameter_depth
        ),
        "minimum_Rouche_margin": minimum_margin,
        "direct_affine_segment_pairs": direct_affine_pair_count,
        "direct_parameter_intervals": direct_parameter_intervals,
        "maximum_direct_parameter_depth": maximum_parameter_depth,
        "minimum_direct_alignment_margin": (
            minimum_alignment_margin if direct_affine_pair_count else None
        ),
    }


def main() -> int:
    arguments = list(sys.argv[1:])
    baseline_root = Path(pop_option(arguments, "--baseline-root")).resolve()
    cell_path = baseline_root / CELL_RELATIVE
    require(cell_path.is_file(), "baseline boundary cell worker")
    output_path = Path(arguments[arguments.index("--output") + 1]).resolve()

    spec = importlib.util.spec_from_file_location("boundary_direct_cell", cell_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {cell_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rectangle_globals = module.certify_interval_guide_homotopy.__globals__
    module.certify_predictor_guide_pair_homotopy = rectangle_globals[
        "certify_predictor_guide_pair_homotopy"
    ]
    module.dyadic_parameter_ball = rectangle_globals["dyadic_parameter_ball"]
    statistics = {
        "certified_cell_calls": 0,
        "direct_affine_segment_pairs": 0,
        "direct_parameter_intervals": 0,
        "maximum_direct_parameter_depth": 0,
        "minimum_direct_alignment_margin": math.inf,
    }

    def wrapper(tubes, predictor_degree, max_depth):
        result = certified_guide_homotopy(
            module, tubes, predictor_degree, max_depth
        )
        statistics["certified_cell_calls"] += 1
        statistics["direct_affine_segment_pairs"] += result[
            "direct_affine_segment_pairs"
        ]
        statistics["direct_parameter_intervals"] += result[
            "direct_parameter_intervals"
        ]
        statistics["maximum_direct_parameter_depth"] = max(
            statistics["maximum_direct_parameter_depth"],
            result["maximum_direct_parameter_depth"],
        )
        if result["minimum_direct_alignment_margin"] is not None:
            statistics["minimum_direct_alignment_margin"] = min(
                statistics["minimum_direct_alignment_margin"],
                result["minimum_direct_alignment_margin"],
            )
        return result

    module.certify_interval_guide_homotopy = wrapper
    original_argv = sys.argv
    try:
        sys.argv = [str(cell_path), *arguments]
        exit_code = module.main()
    finally:
        sys.argv = original_argv
    if exit_code != 0:
        return exit_code

    packet = json.loads(output_path.read_text(encoding="ascii"))
    packet["direct_homotopy_certificate"] = {
        "schema": "mtt.cbf.q79-b89-boundary-direct-homotopy-cell.v1",
        "wrapper_sha256": sha256(Path(__file__).resolve()),
        "baseline_cell_worker_sha256": sha256(cell_path),
        "direct_max_parameter_depth": DIRECT_MAX_PARAMETER_DEPTH,
        **statistics,
        "minimum_direct_alignment_margin": (
            statistics["minimum_direct_alignment_margin"]
            if statistics["direct_affine_segment_pairs"]
            else None
        ),
        "claim": (
            "Every fallback parameter interval proves the predictor and guide "
            "differences noncollinear or positively aligned; the affine segment "
            "therefore excludes zero."
        ),
    }
    output_path.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
