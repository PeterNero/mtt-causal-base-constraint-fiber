#!/usr/bin/env python3
"""Accelerate the exact-source B89 family certificate without weakening it.

The upstream certifier proves pairwise strand separation by constructing an
Arb difference for every pair.  Most pairs are already separated by one
coordinate of their certified rectangular enclosures.  This wrapper proves
those pairs collectively by a sweep order and invokes the original Arb
polynomial argument only for the remaining candidates.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

from flint import arb


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rect(box):
    return (
        box.real.lower(),
        box.real.upper(),
        box.imag.lower(),
        box.imag.upper(),
    )


def _positive_float(value) -> float:
    if not value > 0:
        raise AssertionError("sweep gap must be strictly positive")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise AssertionError("sweep gap must have a positive finite float image")
    return result


def _minimum(current: float, candidate) -> float:
    return min(current, _positive_float(candidate))


def certify_interval_separation_sweep(
    tubes,
    predictor_degree: int,
    max_depth: int,
    baseline,
):
    """Prove every source-tube pair disjoint by exact rectangle ordering.

    Pairs whose real intervals are ordered are discharged collectively.  Of
    the active real-overlap pairs, an ordered imaginary interval discharges
    the pair.  Only a rectangle-overlap candidate reaches the original
    polynomial-difference subdivision proof.
    """

    rows = []
    for tube in tubes:
        real_lower, real_upper, imag_lower, imag_upper = _rect(tube["x_box"])
        rows.append(
            {
                "tube": tube,
                "branch": int(tube["branch"]),
                "real_lower": real_lower,
                "real_upper": real_upper,
                "imag_lower": imag_lower,
                "imag_upper": imag_upper,
            }
        )
    rows.sort(key=lambda row: (row["real_lower"], row["branch"]))

    active = []
    maximum_expired_upper = None
    pair_count = len(rows) * (len(rows) - 1) // 2
    real_order_pairs = 0
    imag_order_pairs = 0
    refined_pairs = []
    leaf_intervals = 0
    maximum_depth = 0
    minimum_lower = math.inf

    for position, current in enumerate(rows):
        retained = []
        for previous in active:
            if previous["real_upper"] < current["real_lower"]:
                if (
                    maximum_expired_upper is None
                    or previous["real_upper"] > maximum_expired_upper
                ):
                    maximum_expired_upper = previous["real_upper"]
            else:
                retained.append(previous)
        active = retained

        expired_pairs = position - len(active)
        if expired_pairs:
            real_order_pairs += expired_pairs
            leaf_intervals += expired_pairs
            minimum_lower = _minimum(
                minimum_lower,
                current["real_lower"] - maximum_expired_upper,
            )

        for previous in active:
            if previous["imag_upper"] < current["imag_lower"]:
                gap = current["imag_lower"] - previous["imag_upper"]
            elif current["imag_upper"] < previous["imag_lower"]:
                gap = previous["imag_lower"] - current["imag_upper"]
            else:
                gap = None
            if gap is not None:
                imag_order_pairs += 1
                leaf_intervals += 1
                minimum_lower = _minimum(minimum_lower, gap)
                continue

            left = previous["tube"]
            right = current["tube"]
            result = baseline.certify_polynomial_difference(
                left["predictor_x"][: predictor_degree + 1],
                right["predictor_x"][: predictor_degree + 1],
                left["x_residual_radius"] + right["x_residual_radius"],
                max_depth,
            )
            if result is None:
                raise ValueError(
                    "shared-parameter separation failed branches="
                    f"{left['branch']},{right['branch']} max_depth={max_depth}"
                )
            refined_pairs.append([left["branch"], right["branch"]])
            maximum_depth = max(maximum_depth, result["maximum_depth"])
            leaf_intervals += result["leaf_intervals"]
            minimum_lower = min(minimum_lower, result["minimum_modulus_lower"])
        active.append(current)

    coarse_pairs = real_order_pairs + imag_order_pairs
    if coarse_pairs + len(refined_pairs) != pair_count:
        raise AssertionError("source sweep pair partition")
    return {
        "certified_pairs": pair_count,
        "coarse_pairs": coarse_pairs,
        "refined_pairs": refined_pairs,
        "refined_pair_count": len(refined_pairs),
        "leaf_intervals": leaf_intervals,
        "maximum_refinement_depth": maximum_depth,
        "minimum_modulus_lower": minimum_lower if pair_count else None,
        "sweep_certificate": {
            "real_order_pairs": real_order_pairs,
            "imag_order_pairs": imag_order_pairs,
            "polynomial_candidate_pairs": len(refined_pairs),
            "pair_partition_complete": True,
        },
    }


def _expanded_rect(tube):
    real_lower, real_upper, imag_lower, imag_upper = _rect(
        tube["predictor_x_box"]
    )
    error = arb(tube["guide_error_upper"]).upper()
    return (
        real_lower - error,
        real_upper + error,
        imag_lower - error,
        imag_upper + error,
        error,
    )


def certify_interval_guide_homotopy_sweep(
    tubes,
    predictor_degree: int,
    max_depth: int,
    baseline,
):
    """Certify straight predictor-to-guide homotopy by expanded boxes.

    Disjoint expanded boxes imply the upstream Rouche inequality by one
    coordinate.  Pairs whose expanded boxes overlap are checked by the exact
    upstream coarse bound and, if necessary, its polynomial subdivision.
    """

    rows = []
    for tube in tubes:
        real_lower, real_upper, imag_lower, imag_upper, error = _expanded_rect(
            tube
        )
        rows.append(
            {
                "tube": tube,
                "branch": int(tube["branch"]),
                "real_lower": real_lower,
                "real_upper": real_upper,
                "imag_lower": imag_lower,
                "imag_upper": imag_upper,
                "error": error,
            }
        )
    rows.sort(key=lambda row: (row["real_lower"], row["branch"]))

    active = []
    maximum_expired_upper = None
    pair_count = len(rows) * (len(rows) - 1) // 2
    real_order_pairs = 0
    imag_order_pairs = 0
    exact_coarse_pairs = 0
    direct_polynomial_pairs = 0
    refined_pair_count = 0
    leaf_intervals = 0
    maximum_depth = 0
    minimum_margin = math.inf

    for position, current in enumerate(rows):
        retained = []
        for previous in active:
            if previous["real_upper"] < current["real_lower"]:
                if (
                    maximum_expired_upper is None
                    or previous["real_upper"] > maximum_expired_upper
                ):
                    maximum_expired_upper = previous["real_upper"]
            else:
                retained.append(previous)
        active = retained

        expired_pairs = position - len(active)
        if expired_pairs:
            real_order_pairs += expired_pairs
            leaf_intervals += expired_pairs
            minimum_margin = _minimum(
                minimum_margin,
                current["real_lower"] - maximum_expired_upper,
            )

        for previous in active:
            if previous["imag_upper"] < current["imag_lower"]:
                gap = current["imag_lower"] - previous["imag_upper"]
            elif current["imag_upper"] < previous["imag_lower"]:
                gap = previous["imag_lower"] - current["imag_upper"]
            else:
                gap = None
            if gap is not None:
                imag_order_pairs += 1
                leaf_intervals += 1
                minimum_margin = _minimum(minimum_margin, gap)
                continue

            left = previous["tube"]
            right = current["tube"]
            coarse_difference = left["predictor_x_box"] - right["predictor_x_box"]
            coarse_margin_ball = (
                coarse_difference.abs_lower()
                - previous["error"]
                - current["error"]
            )
            if coarse_margin_ball > 0:
                exact_coarse_pairs += 1
                leaf_intervals += 1
                minimum_margin = _minimum(minimum_margin, coarse_margin_ball)
                continue

            direct_polynomial_pairs += 1
            result = baseline.certify_predictor_guide_pair_homotopy(
                left["predictor_x"][: predictor_degree + 1],
                right["predictor_x"][: predictor_degree + 1],
                left["guide_x"],
                right["guide_x"],
                max_depth,
            )
            if result is None:
                raise ValueError(
                    "predictor-guide homotopy failed branches="
                    f"{left['branch']},{right['branch']} max_depth={max_depth}"
                )
            refined_pair_count += int(result["maximum_depth"] > 0)
            leaf_intervals += result["leaf_intervals"]
            maximum_depth = max(maximum_depth, result["maximum_depth"])
            minimum_margin = min(minimum_margin, result["minimum_Rouche_margin"])
        active.append(current)

    coarse_pair_count = real_order_pairs + imag_order_pairs + exact_coarse_pairs
    if coarse_pair_count + direct_polynomial_pairs != pair_count:
        raise AssertionError("guide sweep pair partition")
    return {
        "certified_pairs": pair_count,
        "coarse_pairs": coarse_pair_count,
        "direct_polynomial_pairs": direct_polynomial_pairs,
        "refined_pair_count": refined_pair_count,
        "leaf_intervals": leaf_intervals,
        "maximum_refinement_depth": maximum_depth,
        "minimum_Rouche_margin": minimum_margin if pair_count else None,
        "argument": (
            "Expanded predictor boxes are separated by an exact real or "
            "imaginary interval order; unresolved candidates use the original "
            "Arb Rouche polynomial proof."
        ),
        "sweep_certificate": {
            "real_order_pairs": real_order_pairs,
            "imag_order_pairs": imag_order_pairs,
            "exact_Arb_coarse_candidate_pairs": exact_coarse_pairs,
            "direct_polynomial_candidate_pairs": direct_polynomial_pairs,
            "pair_partition_complete": True,
        },
    }


def _load_baseline(root: Path):
    path = (
        root
        / "experiments"
        / "q79_eta9_b89_family_branch_braid_pilot"
        / "certify_rectangle_family_taylor_flint.py"
    )
    if not path.is_file():
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("mtt_b89_baseline_certifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load baseline certifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def _pop_option(arguments: list[str], name: str) -> str:
    try:
        index = arguments.index(name)
    except ValueError as error:
        raise SystemExit(f"missing required wrapper option {name}") from error
    if index + 1 >= len(arguments):
        raise SystemExit(f"missing value for wrapper option {name}")
    value = arguments[index + 1]
    del arguments[index : index + 2]
    return value


def main() -> int:
    arguments = list(sys.argv[1:])
    baseline_root = Path(_pop_option(arguments, "--baseline-root")).resolve()
    output_path = Path(arguments[arguments.index("--output") + 1]).resolve()
    baseline, baseline_path = _load_baseline(baseline_root)

    statistics = {"source_seconds": 0.0, "guide_seconds": 0.0, "calls": 0}

    def source_wrapper(tubes, predictor_degree, max_depth):
        started = time.monotonic()
        result = certify_interval_separation_sweep(
            tubes, predictor_degree, max_depth, baseline
        )
        statistics["source_seconds"] += time.monotonic() - started
        return result

    def guide_wrapper(tubes, predictor_degree, max_depth):
        started = time.monotonic()
        result = certify_interval_guide_homotopy_sweep(
            tubes, predictor_degree, max_depth, baseline
        )
        statistics["guide_seconds"] += time.monotonic() - started
        statistics["calls"] += 1
        return result

    baseline.certify_interval_separation = source_wrapper
    baseline.certify_interval_guide_homotopy = guide_wrapper
    original_argv = sys.argv
    try:
        sys.argv = [str(baseline_path), *arguments]
        exit_code = baseline.main()
    finally:
        sys.argv = original_argv
    if exit_code != 0:
        return exit_code

    packet = json.loads(output_path.read_text(encoding="ascii"))
    packet["accelerated_pair_certificate"] = {
        "schema": "mtt.cbf.q79-b89-accelerated-pair-sweep.v1",
        "wrapper_sha256": _sha256(Path(__file__).resolve()),
        "baseline_certifier_sha256": _sha256(baseline_path),
        "source_sweep_seconds": statistics["source_seconds"],
        "guide_sweep_seconds": statistics["guide_seconds"],
        "certified_cell_calls": statistics["calls"],
        "claim": (
            "The sweep partitions every strand pair and delegates every "
            "unresolved candidate to the original Arb polynomial certifier."
        ),
    }
    output_path.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
