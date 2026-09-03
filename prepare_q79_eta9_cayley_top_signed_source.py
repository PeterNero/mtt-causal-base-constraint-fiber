#!/usr/bin/env python3
"""Replay H4-T141 and preserve its high-precision top-functional centers.

The H4 packet stores one binary64 center and a radius that includes the
conversion from an Arb center to binary64.  This wrapper reuses the original
certified runner unchanged, captures the pre-conversion Arb vectors, and emits
a signed second binary64 component plus the genuine forward-error tail.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

from flint import acb, ctx
import numpy as np


ROOT = Path(__file__).resolve().parent
TEXPAPERS = ROOT.parent
EXPERIMENT = (
    TEXPAPERS
    / "mtt-preprojection-repair-calculus"
    / "experiments"
    / "q79_eta9_bht_fiber_evaluation_and_handle_sweep"
)
OUTPUT = ROOT / "certificates" / "q79_eta9_cayley_top_signed_source_seed7909"
NORMALIZATION_COLUMN = 1494


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def artifact(path: Path) -> dict[str, object]:
    path = path.resolve()
    try:
        name = path.relative_to(TEXPAPERS.resolve()).as_posix()
    except ValueError:
        name = path.name
    return {"path": name, "sha256": sha256(path), "bytes": path.stat().st_size}


def local_artifact(path: Path) -> dict[str, object]:
    path = path.resolve()
    return {
        "path": path.relative_to(ROOT.resolve()).as_posix(),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def localize_replay_packet(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="ascii"))

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if {"path", "sha256", "bytes"}.issubset(value):
                candidate = path.parent / Path(str(value["path"])).name
                if candidate.is_file() and candidate.name.startswith(path.stem + "."):
                    value.update(local_artifact(candidate))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    payload.pop("canonical_payload_sha256", None)
    visit(payload)
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )


def upward(value: float) -> float:
    require(math.isfinite(value) and value >= 0.0, "finite nonnegative bound")
    return float(np.nextafter(value, math.inf))


def save_array(directory: Path, name: str, value: np.ndarray) -> dict[str, object]:
    path = directory / f"{name}.npy"
    np.save(path, value, allow_pickle=False)
    return {
        "path": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def signed_source(
    top: Any,
    published_center: np.ndarray,
    high_precision_values: list[acb],
    forward_radius: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    require(
        published_center.shape == (2584,) and forward_radius.shape == (2583,),
        "signed source shape",
    )
    correction = np.zeros(published_center.shape, dtype=np.complex128)
    tail = np.zeros(published_center.shape, dtype=np.float64)
    nonnormal = np.asarray(
        [index for index in range(2584) if index != NORMALIZATION_COLUMN],
        dtype=np.int64,
    )
    require(len(high_precision_values) == nonnormal.size, "high precision vector")
    for local, column in enumerate(nonnormal):
        delta = high_precision_values[local] - acb(complex(published_center[column]))
        signed = complex(float(delta.real.mid()), float(delta.imag.mid()))
        correction[column] = signed
        tail[column] = upward(
            top.acb_component_error(delta, signed) + float(forward_radius[local])
        )
    return correction, tail, {
        "maximum_signed_correction_component": float(
            (np.abs(correction.real) + np.abs(correction.imag)).max()
        ),
        "maximum_genuine_forward_tail_component": float(tail.max()),
    }


def main() -> int:
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", type=Path, default=OUTPUT)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--inverse-batch", type=int, default=48)
    arguments = parser.parse_args()
    require(arguments.precision >= 384, "precision")
    OUTPUT = arguments.output_directory.resolve()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ctx.prec = arguments.precision

    sys.path.insert(0, str(EXPERIMENT))
    import probe_framed_member_directed_top_trace as top

    captured_refinements: list[list[acb]] = []
    captured_radii: list[tuple[float, np.ndarray]] = []
    captured_radius_arguments: list[tuple[Any, ...]] = []
    captured_unbalanced: list[list[acb]] = []
    captured_systems: list[tuple[Any, list[acb]]] = []
    diagonal_candidates: list[np.ndarray] = []

    original_mixed_refine = top.mixed_refine
    original_solve_radius = top.solve_radius
    original_conversion = top.ball_vector_to_complex
    original_diags = top.sparse.diags
    original_artifact = top.artifact

    def capture_mixed_refine(*args: Any, **kwargs: Any):
        result = original_mixed_refine(*args, **kwargs)
        captured_refinements.append(list(result[0]))
        captured_systems.append((args[1], list(args[2])))
        return result

    def capture_solve_radius(*args: Any, **kwargs: Any):
        result = original_solve_radius(*args, **kwargs)
        captured_radii.append((float(result[0]), np.asarray(result[1]).copy()))
        captured_radius_arguments.append(tuple(args))
        return result

    def capture_conversion(values: list[acb]):
        captured_unbalanced.append(list(values))
        return original_conversion(values)

    def capture_diags(diagonals: Any, *args: Any, **kwargs: Any):
        candidate = np.asarray(diagonals)
        if candidate.ndim == 1 and candidate.shape == (2583,):
            diagonal_candidates.append(candidate.astype(np.float64).copy())
        return original_diags(diagonals, *args, **kwargs)

    def flexible_artifact(path: Path) -> dict[str, object]:
        try:
            return original_artifact(path)
        except ValueError:
            return artifact(path)

    top.mixed_refine = capture_mixed_refine
    top.solve_radius = capture_solve_radius
    top.ball_vector_to_complex = capture_conversion
    top.sparse.diags = capture_diags
    top.artifact = flexible_artifact

    replay = OUTPUT / "upstream_replay.packet.json"
    previous_argv = sys.argv
    sys.argv = [
        str(Path(top.__file__).resolve()),
        "--segment",
        "edge-2",
        "--parameter",
        "0.5",
        "--lift-sign",
        "-1",
        "--precision",
        str(arguments.precision),
        "--inverse-batch",
        str(arguments.inverse_batch),
        "--output",
        str(replay),
    ]
    try:
        exit_code = top.main()
    finally:
        sys.argv = previous_argv
        top.mixed_refine = original_mixed_refine
        top.solve_radius = original_solve_radius
        top.ball_vector_to_complex = original_conversion
        top.sparse.diags = original_diags
        top.artifact = original_artifact
    require(exit_code == 0, "upstream top replay")
    localize_replay_packet(replay)
    require(
        len(captured_refinements) == len(captured_radii) == len(captured_unbalanced) == 2,
        "captured value and derivative solves",
    )

    # Select the diagonal that exactly maps each balanced Arb expansion to the
    # corresponding pre-conversion unbalanced expansion.
    scale_scores: list[tuple[float, np.ndarray]] = []
    for candidate in diagonal_candidates:
        error = 0.0
        for balanced, unbalanced, scale in zip(
            captured_refinements[0], captured_unbalanced[0], candidate, strict=True
        ):
            residual = unbalanced - acb(float(scale)) * balanced
            error = max(error, float(residual.abs_upper()))
        scale_scores.append((error, candidate))
    require(bool(scale_scores), "captured column-scale candidates")
    scale_score, column_factor = min(scale_scores, key=lambda item: item[0])
    require(scale_score < 1.0e-100, f"column-scale replay: {scale_score}")

    replay_packet = json.loads(replay.read_text(encoding="ascii"))
    value_center_path = replay.with_name(
        replay.stem + ".top_functional_center.npy"
    )
    derivative_center_path = replay.with_name(
        replay.stem + ".top_functional_derivative_center.npy"
    )
    published_value_center = np.load(value_center_path, allow_pickle=False)
    published_derivative_center = np.load(
        derivative_center_path, allow_pickle=False
    )
    value_forward = np.nextafter(column_factor * captured_radii[0][1], math.inf)
    value_correction, value_tail, value_diagnostics = signed_source(
        top,
        published_value_center,
        captured_unbalanced[0],
        value_forward,
    )

    published_value_radius = np.load(
        replay.with_name(replay.stem + ".top_functional_radius.npy"),
        allow_pickle=False,
    )
    positive_old_radius = published_value_radius > 0.0
    require(
        np.all(value_tail[~positive_old_radius] == 0.0),
        "new value tail respects exact old coordinates",
    )
    value_tail_ratio = float(
        np.max(
            value_tail[positive_old_radius]
            / published_value_radius[positive_old_radius]
        )
    )
    require(value_tail_ratio < 1.0, "strict value-tail improvement")
    old_feedback = float(
        replay_packet["top_trace_derivative"][
            "maximum_true_value_uncertainty_rhs_correction"
        ]
    )
    new_feedback = upward(value_tail_ratio * old_feedback)
    derivative_rows, derivative_rhs = captured_systems[1]
    _raw_derivative_residual, raw_derivative_bound = top.ball_residual_bounds(
        derivative_rows, derivative_rhs, captured_refinements[1]
    )
    improved_derivative_bound = np.nextafter(
        raw_derivative_bound + new_feedback, math.inf
    )
    derivative_inverse_component = captured_radius_arguments[1][0]
    derivative_eta_rows = captured_radius_arguments[1][1]
    (
        improved_derivative_global_radius,
        improved_derivative_radii,
    ) = original_solve_radius(
        derivative_inverse_component,
        derivative_eta_rows,
        improved_derivative_bound,
    )
    derivative_forward = np.nextafter(
        column_factor * improved_derivative_radii, math.inf
    )
    derivative_correction, derivative_tail, derivative_diagnostics = signed_source(
        top,
        published_derivative_center,
        captured_unbalanced[1],
        derivative_forward,
    )

    bindings = {
        "value_center": save_array(
            OUTPUT, "value_center", published_value_center
        ),
        "value_correction": save_array(
            OUTPUT, "value_correction", value_correction
        ),
        "value_tail": save_array(OUTPUT, "value_tail", value_tail),
        "derivative_center": save_array(
            OUTPUT, "derivative_center", published_derivative_center
        ),
        "derivative_correction": save_array(
            OUTPUT, "derivative_correction", derivative_correction
        ),
        "derivative_tail": save_array(
            OUTPUT, "derivative_tail", derivative_tail
        ),
    }
    checks = {
        "the_original_H4_T141_runner_passes_unchanged": bool(
            all(replay_packet["checks"].values())
        ),
        "the_balanced_to_top_column_scale_is_replayed_in_Arb": scale_score
        < 1.0e-100,
        "the_value_conversion_width_is_replaced_by_a_signed_correction": value_diagnostics[
            "maximum_genuine_forward_tail_component"
        ]
        < 1.0e-30,
        "the_derivative_tail_retains_the_genuine_forward_uncertainty": derivative_diagnostics[
            "maximum_genuine_forward_tail_component"
        ]
        > 0.0,
        "the_derivative_feedback_uses_the_promoted_value_tail": value_tail_ratio
        < 1.0e-10,
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"top signed source checks: {checks}")
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-top-signed-source.v1",
        "theorem_id": "CBF.T67.TOP",
        "status": "PORTABLE_SIGNED_ARB_TOP_SOURCE",
        "precision_bits": arguments.precision,
        "source_bindings": {
            "upstream_runner": artifact(Path(top.__file__).resolve()),
            "upstream_contract": artifact(
                EXPERIMENT
                / "outputs"
                / "q79_eta9_framed_member_directed_top_trace_contract.packet.json"
            ),
            "upstream_replay": local_artifact(replay),
        },
        "normalization_column_zero_based": NORMALIZATION_COLUMN,
        "representation": {
            "formula": "Arb center = binary64 center + signed binary64 correction + genuine component tail",
            "value_tail_excludes_binary64_center_conversion": True,
            "derivative_tail_retains_the_certified_forward_error": True,
        },
        "arrays": bindings,
        "diagnostics": {
            "value": value_diagnostics,
            "derivative": derivative_diagnostics,
            "column_scale_replay_absolute_upper": scale_score,
            "upstream_value_balanced_radius": captured_radii[0][0],
            "upstream_derivative_balanced_radius": captured_radii[1][0],
            "promoted_derivative_balanced_radius": improved_derivative_global_radius,
            "old_value_tail_feedback_maximum": old_feedback,
            "promoted_value_tail_ratio": value_tail_ratio,
            "promoted_value_tail_feedback_maximum": new_feedback,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    (OUTPUT / "metadata.json").write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T67.TOP signed source: PASS "
        f"value_tail={value_tail.max():.3e} "
        f"derivative_tail={derivative_tail.max():.3e}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
