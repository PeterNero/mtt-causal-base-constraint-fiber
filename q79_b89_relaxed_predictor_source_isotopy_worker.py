#!/usr/bin/env python3
"""Versioned B89 cell worker with a binary64-aware Newton seed threshold.

The Newton iterate is only a seed for the subsequent interval Krawczyk proof.
This wrapper leaves the baseline certifier and every proof gate unchanged while
raising the seed stopping threshold from 2^-55 to 2^-52, above the observed
binary64 input floor on the hard edge-2 cells.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import q79_b89_accelerated_source_isotopy_worker as accelerated


PREDICTOR_REFINEMENT_BITS = 52
PREDICTOR_REFINEMENT_ITERATIONS = 30


def relaxed_high_precision_newton(baseline, geometry, kind, x_value, y_value):
    values = [baseline.acb_point(x_value), baseline.acb_point(y_value)]
    if kind == "ramification":
        values.append(
            baseline.acb_point(
                baseline.normalization_w_guide(geometry, x_value, y_value)
            )
        )
    target = baseline.arb(2) ** -PREDICTOR_REFINEMENT_BITS
    for _ in range(PREDICTOR_REFINEMENT_ITERATIONS):
        if kind == "node":
            residual, jacobian = baseline.evaluate_system(
                geometry, values[0], values[1], values[0], values[1]
            )
        else:
            residual, jacobian = baseline.evaluate_normalization_point(
                geometry,
                values[0],
                values[1],
                values[2],
                values[0],
                values[1],
            )
        matrix = baseline.acb_mat(jacobian)
        rhs = baseline.acb_mat([[-value] for value in residual])
        correction = matrix.solve(rhs)
        maximum = baseline.arb(0)
        for coordinate in range(len(values)):
            delta = correction[coordinate, 0]
            maximum = max(maximum, delta.abs_upper())
            values[coordinate] = baseline.midpoint_ball(values[coordinate] + delta)
        if maximum < target:
            return tuple(values)
    raise ValueError(
        "predictor Newton did not reach the binary64-aware seed threshold "
        f"correction={maximum}"
    )


def main() -> int:
    arguments = list(sys.argv[1:])
    output_path = Path(arguments[arguments.index("--output") + 1]).resolve()
    original_load = accelerated._load_baseline

    def load_relaxed(root: Path):
        baseline, path = original_load(root)
        baseline.high_precision_newton = lambda geometry, kind, x, y: (
            relaxed_high_precision_newton(baseline, geometry, kind, x, y)
        )
        return baseline, path

    accelerated._load_baseline = load_relaxed
    accelerated.__file__ = __file__
    exit_code = accelerated.main()
    if exit_code != 0:
        return exit_code

    packet = json.loads(output_path.read_text(encoding="ascii"))
    packet["accelerated_pair_certificate"]["predictor_seed_policy"] = {
        "refinement_threshold_bits": PREDICTOR_REFINEMENT_BITS,
        "maximum_iterations": PREDICTOR_REFINEMENT_ITERATIONS,
        "role": "nonproof_seed_for_interval_Krawczyk_validation",
        "rigorous_acceptance_unchanged": True,
    }
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    temporary.replace(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
