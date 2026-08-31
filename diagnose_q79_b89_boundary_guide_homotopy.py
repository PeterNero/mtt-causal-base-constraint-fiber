#!/usr/bin/env python3
"""Diagnose a boundary predictor-to-guide homotopy without accepting it."""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np


CELL_RELATIVE = Path(
    "experiments/q79_eta9_b89_family_branch_braid_pilot/"
    "certify_right80_boundary_taylor_flint.py"
)


def midpoint(value) -> complex:
    return complex(float(value.real.mid()), float(value.imag.mid()))


def evaluate(coefficients: np.ndarray, parameter: np.ndarray) -> np.ndarray:
    return np.polynomial.polynomial.polyval(parameter, coefficients)


def pair_diagnostic(left: dict, right: dict) -> dict:
    predictor = np.array(
        [
            midpoint(a) - midpoint(b)
            for a, b in itertools.zip_longest(
                left["predictor_x"], right["predictor_x"], fillvalue=0
            )
        ],
        dtype=np.complex128,
    )
    guide = np.array(
        [
            midpoint(a) - midpoint(b)
            for a, b in itertools.zip_longest(
                left["guide_x"], right["guide_x"], fillvalue=0
            )
        ],
        dtype=np.complex128,
    )
    center = 0.0
    halfwidth = 1.0
    best = None
    for _ in range(10):
        parameters = np.linspace(center - halfwidth, center + halfwidth, 2001)
        parameters = np.clip(parameters, -1.0, 1.0)
        source = evaluate(predictor, parameters)
        target = evaluate(guide, parameters)
        displacement = target - source
        denominator = np.abs(displacement) ** 2
        alpha = np.zeros_like(parameters)
        nonzero = denominator > 0
        alpha[nonzero] = np.clip(
            -np.real(source[nonzero] * np.conj(displacement[nonzero]))
            / denominator[nonzero],
            0.0,
            1.0,
        )
        values = source + alpha * displacement
        index = int(np.argmin(np.abs(values)))
        candidate = (
            float(abs(values[index])),
            float(parameters[index]),
            float(alpha[index]),
            complex(source[index]),
            complex(target[index]),
            complex(values[index]),
        )
        if best is None or candidate[0] < best[0]:
            best = candidate
        center = candidate[1]
        halfwidth /= 100.0
    assert best is not None
    minimum, parameter, alpha_value, source_value, guide_value, value = best
    return {
        "branches": [int(left["branch"]), int(right["branch"])],
        "sampled_minimum_modulus": minimum,
        "local_parameter": parameter,
        "homotopy_parameter": alpha_value,
        "source_difference": [source_value.real, source_value.imag],
        "guide_difference": [guide_value.real, guide_value.imag],
        "homotopy_difference": [value.real, value.imag],
        "source_modulus": abs(source_value),
        "guide_modulus": abs(guide_value),
        "displacement_modulus": abs(guide_value - source_value),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--guides", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--interval", type=int, required=True)
    parser.add_argument("--cell-fraction-start", required=True)
    parser.add_argument("--cell-fraction-stop", required=True)
    parser.add_argument("--left-branch", type=int, default=1)
    parser.add_argument("--right-branch", type=int, default=2)
    args = parser.parse_args()

    cell_path = Path(args.baseline_root).resolve() / CELL_RELATIVE
    spec = importlib.util.spec_from_file_location("boundary_cell_diagnostic", cell_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {cell_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = module.certify_interval_guide_homotopy

    def diagnostic(tubes, predictor_degree, max_depth):
        by_label = {int(tube["branch"]): tube for tube in tubes}
        result = pair_diagnostic(
            by_label[args.left_branch], by_label[args.right_branch]
        )
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        return original(tubes, predictor_degree, max_depth)

    module.certify_interval_guide_homotopy = diagnostic
    original_argv = sys.argv
    try:
        sys.argv = [
            str(cell_path),
            "--source",
            str(Path(args.source).resolve()),
            "--guides",
            str(Path(args.guides).resolve()),
            "--metadata",
            str(Path(args.metadata).resolve()),
            "--interval-start",
            str(args.interval),
            "--interval-stop",
            str(args.interval + 1),
            "--precision",
            "512",
            "--predictor-degree",
            "12",
            "--taylor-order",
            "14",
            "--separation-max-depth",
            "24",
            "--cell-fraction-start",
            args.cell_fraction_start,
            "--cell-fraction-stop",
            args.cell_fraction_stop,
            "--output",
            "boundary-guide-diagnostic-do-not-use.json",
        ]
        return module.main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
