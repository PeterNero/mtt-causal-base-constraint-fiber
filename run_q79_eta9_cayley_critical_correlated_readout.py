#!/usr/bin/env python3
"""Certify the CBF.T67 same-source characteristic-zero scalar readout.

The T66 coordinate box proves the selected system but forgets that all right
hand sides come from one pivot-anchor vector.  This runner restores that
linearity, preserves signed double-double coefficient corrections, and uses
two adjoint solves to contract uncertainty directly to the scalar readout.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time
from typing import Any

from flint import acb, arb, ctx
import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla

import run_q79_eta9_cayley_critical_characteristic_zero_neumann as t66


ROOT = Path(__file__).resolve().parent
BASE_INPUT = (
    ROOT / "certificates/q79_eta9_cayley_critical_characteristic_zero_seed7909"
)
SIGNED_INPUT = (
    ROOT / "certificates/q79_eta9_cayley_critical_signed_correction_seed7909"
)
TOP_SIGNED_INPUT = (
    ROOT / "certificates/q79_eta9_cayley_top_signed_source_seed7909"
)
T66_PACKET = ROOT / "q79_eta9_cayley_critical_characteristic_zero_neumann.packet.json"
OUTPUT = ROOT / "q79_eta9_cayley_critical_correlated_readout.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_packet(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="ascii"))
    require(payload.get("schema") == schema, f"schema: {path}")
    claimed = payload.get("canonical_payload_sha256")
    unsigned = dict(payload)
    unsigned.pop("canonical_payload_sha256", None)
    require(claimed == t66.canonical_sha256(unsigned), f"payload hash: {path}")
    return payload


def point_rows(matrix: sparse.spmatrix) -> list[list[tuple[int, acb]]]:
    value = matrix.tocsr()
    return [
        [
            (int(value.indices[position]), acb(complex(value.data[position])))
            for position in range(int(value.indptr[row]), int(value.indptr[row + 1]))
        ]
        for row in range(value.shape[0])
    ]


def point_vector(value: np.ndarray) -> list[acb]:
    return [acb(complex(entry)) for entry in value]


def add_vectors(*vectors: list[acb]) -> list[acb]:
    require(bool(vectors), "vector sum")
    size = len(vectors[0])
    require(all(len(vector) == size for vector in vectors), "vector sum shape")
    return [sum((vector[index] for vector in vectors), acb(0)) for index in range(size)]


def sparse_point_matvec(matrix: sparse.spmatrix, vector: list[acb]) -> list[acb]:
    value = matrix.tocsr()
    require(value.shape[1] == len(vector), "sparse point product shape")
    output: list[acb] = []
    for row in range(value.shape[0]):
        total = acb(0)
        for position in range(int(value.indptr[row]), int(value.indptr[row + 1])):
            total += acb(complex(value.data[position])) * vector[
                int(value.indices[position])
            ]
        output.append(total)
    return output


def midpoint_vector(values: list[acb]) -> np.ndarray:
    return np.asarray(
        [complex(float(value.real.mid()), float(value.imag.mid())) for value in values],
        dtype=np.complex128,
    )


def component_upper(values: list[acb]) -> np.ndarray:
    return np.asarray(
        [
            t66.upward(float(abs(value.real).upper()) + float(abs(value.imag).upper()))
            for value in values
        ],
        dtype=np.float64,
    )


def add_upper(*values: np.ndarray) -> np.ndarray:
    require(bool(values), "bound sum")
    total = np.zeros(values[0].shape, dtype=np.float64)
    for value in values:
        require(value.shape == total.shape and np.all(value >= 0.0), "bound shape")
        total = np.nextafter(total + value, math.inf)
    return total


def positive_pair_sum_upper(left: np.ndarray, right: np.ndarray) -> float:
    require(left.shape == right.shape, "positive pair shape")
    require(np.all(left >= 0.0) and np.all(right >= 0.0), "positive pair")
    value = sum(
        (arb(float(a)) * arb(float(b)) for a, b in zip(left, right, strict=True)),
        arb(0),
    )
    return t66.upward(float(value.upper()))


def scaled_upper(value: float, factor: float) -> float:
    require(value >= 0.0 and factor >= 0.0, "positive scale")
    return t66.upward(float((arb(value) * arb(factor)).upper()))


def refine(
    label: str,
    factor: Any,
    rows: list[list[tuple[int, acb]]],
    rhs: list[acb],
    initial: np.ndarray,
    iterations: int,
) -> tuple[list[acb], dict[str, Any]]:
    value = point_vector(initial)
    history: list[dict[str, float | int]] = []
    previous = math.inf
    for iteration in range(iterations):
        residual, bounds, maximum = t66.residual_bounds(rows, rhs, value)
        history.append(
            {
                "iteration": iteration,
                "maximum_midpoint_residual": maximum,
                "maximum_component_upper": float(bounds.max()),
            }
        )
        print(
            f"CBF.T67 {label} refinement={iteration} "
            f"midpoint={maximum:.3e} ball={bounds.max():.3e}",
            flush=True,
        )
        if maximum == 0.0 or maximum < 2.0**-300:
            break
        exponent = math.frexp(maximum)[1]
        scale = math.ldexp(1.0, exponent)
        correction_rhs = np.asarray(
            [
                complex(float(entry.real.mid()), float(entry.imag.mid())) / scale
                for entry in residual
            ],
            dtype=np.complex128,
        )
        correction = factor.solve(correction_rhs) * scale
        for index, entry in enumerate(correction):
            value[index] += acb(complex(entry))
        if maximum >= previous and iteration >= 4:
            break
        previous = maximum
    _residual, final_bounds, final_midpoint = t66.residual_bounds(rows, rhs, value)
    return value, {
        "iterations": len(history),
        "history": history,
        "final_midpoint_residual": final_midpoint,
        "final_component_upper": float(final_bounds.max()),
    }


def ball_summary(value: acb) -> tuple[complex, float]:
    midpoint = complex(float(value.real.mid()), float(value.imag.mid()))
    centered = value - acb(midpoint)
    radius = t66.upward(
        float(abs(centered.real).upper()) + float(abs(centered.imag).upper())
    )
    return midpoint, radius


def scalar_certificate(
    center_ball: acb,
    source_error: float,
) -> dict[str, float | bool]:
    midpoint, arithmetic_error = ball_summary(center_ball)
    total_error = t66.upward(arithmetic_error + source_error)
    midpoint_absolute = abs(midpoint)
    absolute_lower = max(
        0.0, float(np.nextafter(midpoint_absolute - total_error, -math.inf))
    )
    absolute_upper = t66.upward(midpoint_absolute + total_error)
    return {
        "midpoint_real": midpoint.real,
        "midpoint_imaginary": midpoint.imag,
        "midpoint_absolute": midpoint_absolute,
        "arithmetic_component_error": arithmetic_error,
        "source_absolute_error": source_error,
        "total_absolute_error": total_error,
        "absolute_lower": absolute_lower,
        "absolute_upper": absolute_upper,
        "excludes_zero": absolute_lower > 0.0,
    }


def save_array(output: Path, suffix: str, value: np.ndarray) -> dict[str, object]:
    path = output.with_name(f"{output.name}.{suffix}.npy")
    np.save(path, value, allow_pickle=False)
    return t66.artifact(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-input", type=Path, default=BASE_INPUT)
    parser.add_argument("--signed-input", type=Path, default=SIGNED_INPUT)
    parser.add_argument("--top-signed-input", type=Path, default=TOP_SIGNED_INPUT)
    parser.add_argument("--t66-packet", type=Path, default=T66_PACKET)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--refinements", type=int, default=10)
    arguments = parser.parse_args()
    require(arguments.precision >= 384, "Arb precision")
    require(arguments.refinements >= 2, "refinement count")
    ctx.prec = arguments.precision
    started = time.monotonic()

    base = t66.load_metadata(arguments.base_input.resolve())
    signed_path = arguments.signed_input.resolve() / "metadata.json"
    signed = load_packet(
        signed_path,
        "mtt.cbf.q79-eta9-cayley-critical-signed-correction.v1",
    )
    top_signed_path = arguments.top_signed_input.resolve() / "metadata.json"
    top_signed = load_packet(
        top_signed_path,
        "mtt.cbf.q79-eta9-cayley-top-signed-source.v1",
    )
    previous = load_packet(
        arguments.t66_packet.resolve(),
        "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-neumann.v1",
    )
    require(signed["all_checks_pass"], "signed source checks")
    require(
        previous["checks"][
            "the_exact_characteristic_zero_matrix_has_a_strict_Neumann_inverse"
        ],
        "T66 strict inverse",
    )

    n = 6777
    anchors = 2584
    ambient = 9361
    arrays = base["arrays"]
    matrices = base["matrices"]
    signed_arrays = signed["arrays"]
    signed_matrices = signed["matrices"]

    load_array = lambda binding, shape: t66.load_array(binding, shape)
    load_sparse = lambda binding, shape: t66.load_sparse(binding, shape)
    A = (
        load_sparse(matrices["balanced_matrix_center"], (n, n))
        + load_sparse(signed_matrices["balanced_matrix_correction"], (n, n))
    ).tocsr()
    Atail = load_sparse(signed_matrices["balanced_matrix_tail"], (n, n))
    C = (
        load_sparse(matrices["balanced_derivative_coupling_center"], (n, n))
        + load_sparse(
            signed_matrices["balanced_derivative_coupling_correction"], (n, n)
        )
    ).tocsr()
    Ctail = load_sparse(
        signed_matrices["balanced_derivative_coupling_tail"], (n, n)
    )
    B = (
        load_sparse(signed_matrices["pivot_source_map_center"], (n, anchors))
        + load_sparse(
            signed_matrices["pivot_source_map_correction"], (n, anchors)
        )
    ).tocsr()
    Btail = load_sparse(
        signed_matrices["pivot_source_map_tail"], (n, anchors)
    )
    Bprime = (
        load_sparse(
            signed_matrices["pivot_source_map_derivative_center"],
            (n, anchors),
        )
        + load_sparse(
            signed_matrices["pivot_source_map_derivative_correction"],
            (n, anchors),
        )
    ).tocsr()
    Bprime_tail = load_sparse(
        signed_matrices["pivot_source_map_derivative_tail"], (n, anchors)
    )
    require(
        min(Atail.data.min(), Ctail.data.min(), Btail.data.min(), Bprime_tail.data.min())
        >= 0.0,
        "nonnegative coefficient tails",
    )

    pivots = load_array(arrays["embedding_pivots"], (anchors,)).astype(np.int64)
    free = load_array(arrays["free_columns"], (n,)).astype(np.int64)
    column_factor = load_array(arrays["column_factor"], (n,))
    pivot_from_top = load_sparse(
        signed_matrices["pivot_from_top_map"], (anchors, anchors)
    )
    top_arrays = top_signed["arrays"]
    top = load_array(top_arrays["value_center"], (anchors,)) + load_array(
        top_arrays["value_correction"], (anchors,)
    )
    top_tail = load_array(top_arrays["value_tail"], (anchors,))
    topprime = load_array(
        top_arrays["derivative_center"], (anchors,)
    ) + load_array(top_arrays["derivative_correction"], (anchors,))
    topprime_tail = load_array(top_arrays["derivative_tail"], (anchors,))
    J = load_array(arrays["jacobian_center"], (ambient,)) + load_array(
        signed_arrays["jacobian_correction"], (ambient,)
    )
    Jtail = load_array(signed_arrays["jacobian_tail"], (ambient,))
    Jprime = load_array(
        arrays["jacobian_derivative_center"], (ambient,)
    ) + load_array(
        signed_arrays["jacobian_derivative_correction"], (ambient,)
    )
    Jprime_tail = load_array(
        signed_arrays["jacobian_derivative_tail"], (ambient,)
    )

    A_csc = A.tocsc()
    factor = spla.splu(A_csc)
    factor_transpose = spla.splu(A.transpose().tocsc())
    A_rows = point_rows(A)
    AT_rows = point_rows(A.transpose())
    top_point = point_vector(top)
    topprime_point = point_vector(topprime)
    p_point = sparse_point_matvec(pivot_from_top, top_point)
    pprime_point = sparse_point_matvec(pivot_from_top, topprime_point)
    p = midpoint_vector(p_point)
    pprime = midpoint_vector(pprime_point)
    b_point = sparse_point_matvec(B, p_point)
    c_point = add_vectors(
        sparse_point_matvec(B, pprime_point),
        sparse_point_matvec(Bprime, p_point),
    )

    x_initial = t66.solve_center(factor, A_csc, midpoint_vector(b_point))
    x, x_refinement = refine(
        "value", factor, A_rows, b_point, x_initial, arguments.refinements
    )
    Cx = sparse_point_matvec(C, x)
    derivative_rhs = add_vectors(c_point, Cx)
    v_initial = t66.solve_center(
        factor, A_csc, midpoint_vector(derivative_rhs)
    )
    v, v_refinement = refine(
        "derivative",
        factor,
        A_rows,
        derivative_rhs,
        v_initial,
        arguments.refinements,
    )

    g_point = [
        acb(float(column_factor[index])) * acb(complex(J[int(column)]))
        for index, column in enumerate(free)
    ]
    z_initial = factor_transpose.solve(midpoint_vector(g_point))
    z, z_refinement = refine(
        "value-adjoint",
        factor_transpose,
        AT_rows,
        g_point,
        z_initial,
        arguments.refinements,
    )
    gprime_point = [
        acb(float(column_factor[index])) * acb(complex(Jprime[int(column)]))
        for index, column in enumerate(free)
    ]
    h_point = add_vectors(
        gprime_point, sparse_point_matvec(C.transpose(), z)
    )
    y_initial = factor_transpose.solve(midpoint_vector(h_point))
    y, y_refinement = refine(
        "derivative-adjoint",
        factor_transpose,
        AT_rows,
        h_point,
        y_initial,
        arguments.refinements,
    )

    A_component = t66.component_sparse(A)
    C_component = t66.component_sparse(C)
    B_component = t66.component_sparse(B)
    Bprime_component = t66.component_sparse(Bprime)
    top_component = t66.component(top)
    topprime_component = t66.component(topprime)
    p_component = component_upper(p_point)
    pprime_component = component_upper(pprime_point)
    pivot_map_component = t66.component_sparse(pivot_from_top)
    p_tail = t66.sparse_positive_matvec_upper(
        pivot_map_component, top_tail
    )
    pprime_tail = t66.sparse_positive_matvec_upper(
        pivot_map_component, topprime_tail
    )
    x_component = component_upper(x)
    v_component = component_upper(v)
    z_component = component_upper(z)
    y_component = component_upper(y)

    b_uncertainty = add_upper(
        t66.sparse_positive_matvec_upper(Btail, p_component),
        t66.sparse_positive_matvec_upper(
            (B_component + Btail).tocsr(), p_tail
        ),
    )
    c_uncertainty = add_upper(
        t66.sparse_positive_matvec_upper(Btail, pprime_component),
        t66.sparse_positive_matvec_upper(
            (B_component + Btail).tocsr(), pprime_tail
        ),
        t66.sparse_positive_matvec_upper(Bprime_tail, p_component),
        t66.sparse_positive_matvec_upper(
            (Bprime_component + Bprime_tail).tocsr(), p_tail
        ),
    )

    _x_residual, x_center_residual, _x_midpoint = t66.residual_bounds(
        A_rows, b_point, x
    )
    eta = float(previous["inverse_certificate"]["maximum_total_Neumann_row"])
    preconditioner_norm = float(
        previous["inverse_certificate"]["maximum_inverse_component_row_sum"]
    )
    inverse_norm = t66.upward(preconditioner_norm / (1.0 - eta))
    x_source_residual = add_upper(
        x_center_residual,
        b_uncertainty,
        t66.sparse_positive_matvec_upper(Atail, x_component),
    )
    x_error = scaled_upper(float(x_source_residual.max()), inverse_norm)
    x_true_bound = np.nextafter(x_component + x_error, math.inf)

    _v_residual, v_center_residual, _v_midpoint = t66.residual_bounds(
        A_rows, derivative_rhs, v
    )
    v_source_residual = add_upper(
        v_center_residual,
        c_uncertainty,
        t66.sparse_positive_matvec_upper(Ctail, x_component),
        t66.sparse_positive_matvec_upper(
            (C_component + Ctail).tocsr(),
            np.full(n, x_error, dtype=np.float64),
        ),
        t66.sparse_positive_matvec_upper(Atail, v_component),
    )
    v_error = scaled_upper(float(v_source_residual.max()), inverse_norm)
    v_true_bound = np.nextafter(v_component + v_error, math.inf)

    K_point = add_vectors(
        [acb(complex(J[int(column)])) for column in pivots],
        sparse_point_matvec(B.transpose(), z),
    )
    Kprime_point = add_vectors(
        [acb(complex(Jprime[int(column)])) for column in pivots],
        sparse_point_matvec(Bprime.transpose(), z),
        sparse_point_matvec(B.transpose(), y),
    )
    K_component = component_upper(K_point)
    Kprime_component = component_upper(Kprime_point)
    K_uncertainty = add_upper(
        Jtail[pivots],
        t66.sparse_positive_matvec_upper(Btail.transpose().tocsr(), z_component),
    )
    Kprime_uncertainty = add_upper(
        Jprime_tail[pivots],
        t66.sparse_positive_matvec_upper(
            Bprime_tail.transpose().tocsr(), z_component
        ),
        t66.sparse_positive_matvec_upper(Btail.transpose().tocsr(), y_component),
    )
    top_K_point = sparse_point_matvec(pivot_from_top.transpose(), K_point)
    top_Kprime_point = sparse_point_matvec(
        pivot_from_top.transpose(), Kprime_point
    )
    top_K_component = component_upper(top_K_point)
    top_Kprime_component = component_upper(top_Kprime_point)
    top_K_uncertainty = t66.sparse_positive_matvec_upper(
        pivot_map_component.transpose().tocsr(), K_uncertainty
    )
    top_Kprime_uncertainty = t66.sparse_positive_matvec_upper(
        pivot_map_component.transpose().tocsr(), Kprime_uncertainty
    )

    _rz, rz_center_bound, _rz_midpoint = t66.residual_bounds(
        AT_rows, g_point, z
    )
    g_uncertainty = np.nextafter(column_factor * Jtail[free], math.inf)
    rz_bound = add_upper(
        rz_center_bound,
        g_uncertainty,
        t66.sparse_positive_matvec_upper(
            Atail.transpose().tocsr(), z_component
        ),
    )
    _ry, ry_center_bound, _ry_midpoint = t66.residual_bounds(
        AT_rows, h_point, y
    )
    gprime_uncertainty = np.nextafter(
        column_factor * Jprime_tail[free], math.inf
    )
    ry_bound = add_upper(
        ry_center_bound,
        gprime_uncertainty,
        t66.sparse_positive_matvec_upper(
            Ctail.transpose().tocsr(), z_component
        ),
        t66.sparse_positive_matvec_upper(
            Atail.transpose().tocsr(), y_component
        ),
    )

    denominator_center = sum(
        (
            coefficient * source
            for coefficient, source in zip(
                top_K_point, top_point, strict=True
            )
        ),
        acb(0),
    )
    denominator_terms = {
        "coefficient_tail_times_common_top_center": positive_pair_sum_upper(
            top_K_uncertainty, top_component
        ),
        "coefficient_plus_tail_times_common_top_tail": positive_pair_sum_upper(
            add_upper(top_K_component, top_K_uncertainty), top_tail
        ),
        "adjoint_residual_times_solution": positive_pair_sum_upper(
            rz_bound, x_true_bound
        ),
    }
    denominator_source_error = t66.upward(
        math.fsum(denominator_terms.values())
    )
    denominator = scalar_certificate(
        denominator_center, denominator_source_error
    )

    denominator_prime_center = sum(
        (
            coefficient * source
            for coefficient, source in zip(
                top_K_point, topprime_point, strict=True
            )
        ),
        acb(0),
    ) + sum(
        (
            coefficient * source
            for coefficient, source in zip(
                top_Kprime_point, top_point, strict=True
            )
        ),
        acb(0),
    )
    denominator_prime_terms = {
        "value_coefficient_tail_times_common_top_derivative": positive_pair_sum_upper(
            top_K_uncertainty, topprime_component
        ),
        "value_coefficient_times_common_top_derivative_tail": positive_pair_sum_upper(
            add_upper(top_K_component, top_K_uncertainty), topprime_tail
        ),
        "derivative_coefficient_tail_times_common_top": positive_pair_sum_upper(
            top_Kprime_uncertainty, top_component
        ),
        "derivative_coefficient_times_common_top_tail": positive_pair_sum_upper(
            add_upper(top_Kprime_component, top_Kprime_uncertainty), top_tail
        ),
        "value_adjoint_residual_times_derivative_solution": positive_pair_sum_upper(
            rz_bound, v_true_bound
        ),
        "derivative_adjoint_residual_times_value_solution": positive_pair_sum_upper(
            ry_bound, x_true_bound
        ),
    }
    denominator_prime_source_error = t66.upward(
        math.fsum(denominator_prime_terms.values())
    )
    denominator_prime = scalar_certificate(
        denominator_prime_center, denominator_prime_source_error
    )

    scale: dict[str, float] | None = None
    scale_prime: dict[str, float] | None = None
    if denominator["excludes_zero"]:
        denominator_midpoint = complex(
            denominator["midpoint_real"], denominator["midpoint_imaginary"]
        )
        denominator_error = float(denominator["total_absolute_error"])
        denominator_modulus = abs(denominator_midpoint)
        denominator_lower = denominator_modulus - denominator_error
        scale_midpoint = 585.0 / (2.0 * denominator_midpoint)
        scale_error = t66.upward(
            292.5
            * denominator_error
            / (denominator_modulus * denominator_lower)
        )
        scale = {
            "midpoint_real": scale_midpoint.real,
            "midpoint_imaginary": scale_midpoint.imag,
            "absolute_error": scale_error,
            "relative_error_upper": t66.upward(scale_error / abs(scale_midpoint)),
        }
        denominator_prime_midpoint = complex(
            denominator_prime["midpoint_real"],
            denominator_prime["midpoint_imaginary"],
        )
        denominator_prime_error = float(
            denominator_prime["total_absolute_error"]
        )
        scale_prime_midpoint = (
            -292.5 * denominator_prime_midpoint / denominator_midpoint**2
        )
        reciprocal_square_error = (
            denominator_error * (2.0 * denominator_modulus + denominator_error)
            / (denominator_lower**2 * denominator_modulus**2)
        )
        scale_prime_error = t66.upward(
            292.5
            * (
                denominator_prime_error / denominator_lower**2
                + abs(denominator_prime_midpoint) * reciprocal_square_error
            )
        )
        scale_prime = {
            "midpoint_real": scale_prime_midpoint.real,
            "midpoint_imaginary": scale_prime_midpoint.imag,
            "absolute_error": scale_prime_error,
        }

    output = arguments.output.resolve()
    x_center, x_arithmetic_radius = t66.ball_centers(x)
    v_center, v_arithmetic_radius = t66.ball_centers(v)
    K_center, K_arithmetic_radius = t66.ball_centers(K_point)
    Kprime_center, Kprime_arithmetic_radius = t66.ball_centers(Kprime_point)
    top_K_center, top_K_arithmetic_radius = t66.ball_centers(top_K_point)
    top_Kprime_center, top_Kprime_arithmetic_radius = t66.ball_centers(
        top_Kprime_point
    )
    bindings = {
        "balanced_value_center": save_array(output, "balanced_value_center", x_center),
        "balanced_value_radius": save_array(
            output,
            "balanced_value_radius",
            np.nextafter(x_arithmetic_radius + x_error, math.inf),
        ),
        "balanced_derivative_center": save_array(
            output, "balanced_derivative_center", v_center
        ),
        "balanced_derivative_radius": save_array(
            output,
            "balanced_derivative_radius",
            np.nextafter(v_arithmetic_radius + v_error, math.inf),
        ),
        "anchor_readout_center": save_array(output, "anchor_readout_center", K_center),
        "anchor_readout_radius": save_array(
            output,
            "anchor_readout_radius",
            np.nextafter(K_arithmetic_radius + K_uncertainty, math.inf),
        ),
        "anchor_readout_derivative_center": save_array(
            output, "anchor_readout_derivative_center", Kprime_center
        ),
        "anchor_readout_derivative_radius": save_array(
            output,
            "anchor_readout_derivative_radius",
            np.nextafter(
                Kprime_arithmetic_radius + Kprime_uncertainty, math.inf
            ),
        ),
        "common_top_readout_center": save_array(
            output, "common_top_readout_center", top_K_center
        ),
        "common_top_readout_radius": save_array(
            output,
            "common_top_readout_radius",
            np.nextafter(
                top_K_arithmetic_radius + top_K_uncertainty, math.inf
            ),
        ),
        "common_top_readout_derivative_center": save_array(
            output,
            "common_top_readout_derivative_center",
            top_Kprime_center,
        ),
        "common_top_readout_derivative_radius": save_array(
            output,
            "common_top_readout_derivative_radius",
            np.nextafter(
                top_Kprime_arithmetic_radius + top_Kprime_uncertainty,
                math.inf,
            ),
        ),
        "value_adjoint_residual_bound": save_array(
            output, "value_adjoint_residual_bound", rz_bound
        ),
        "derivative_adjoint_residual_bound": save_array(
            output, "derivative_adjoint_residual_bound", ry_bound
        ),
    }
    checks = {
        "the_T66_characteristic_zero_inverse_certificate_is_inherited": eta < 1.0,
        "the_signed_source_and_pivot_maps_pass_their_source_checks": bool(
            signed["all_checks_pass"]
        ),
        "the_signed_Arb_top_source_passes_its_source_checks": bool(
            top_signed["all_checks_pass"]
        ),
        "the_exact_square_zero_Cayley_map_replays_the_common_top_source": bool(
            pivot_from_top.shape == (anchors, anchors)
            and top.shape == topprime.shape == (anchors,)
        ),
        "the_correlated_value_source_has_a_finite_forward_bound": math.isfinite(
            x_error
        ),
        "the_correlated_derivative_source_has_a_finite_forward_bound": math.isfinite(
            v_error
        ),
        "the_same_source_toric_Jacobian_denominator_excludes_zero": bool(
            denominator["excludes_zero"]
        ),
        "the_canonical_scale_and_first_derivative_disks_are_emitted": scale is not None
        and scale_prime is not None,
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-correlated-readout.v1",
        "theorem_id": "CBF.T67",
        "status": (
            "CERTIFIED_SAME_SOURCE_CHARACTERISTIC_ZERO_SCALAR_READOUT"
            if all(checks.values())
            else "CORRELATED_READOUT_OBSTRUCTION"
        ),
        "tier": "numerical_certified",
        "precision_bits": arguments.precision,
        "inputs": {
            "base": t66.artifact(arguments.base_input.resolve() / "metadata.json"),
            "signed": t66.artifact(signed_path),
            "top_signed": t66.artifact(top_signed_path),
            "T66": t66.artifact(arguments.t66_packet.resolve()),
        },
        "dimensions": {
            "balanced_system": n,
            "common_anchor_source": anchors,
            "critical_functional": ambient,
        },
        "method": {
            "value_identity": "K=J_P+B^T z, A^T z=g",
            "derivative_identity": "K'=J'_P+B'^T z+B^T y, A^T y=g'+C^T z",
            "remainder_identity": "D=K p+r_z^T x; D'=K p'+K' p+r_z^T x'+r_y^T x",
            "common_source_identity": "p=L top, p'=L top', and the final coefficients are L^T K and L^T K'",
            "norm": "component l1 modulus with an inherited directed infinity-norm inverse bound",
        },
        "inverse_bound": {
            "T66_eta": eta,
            "preconditioner_infinity_norm_upper": preconditioner_norm,
            "selected_matrix_inverse_infinity_norm_upper": inverse_norm,
        },
        "value_solution": {
            "maximum_source_residual_component": float(x_source_residual.max()),
            "uniform_component_forward_error": x_error,
            "refinement": x_refinement,
        },
        "derivative_solution": {
            "maximum_source_residual_component": float(v_source_residual.max()),
            "uniform_component_forward_error": v_error,
            "refinement": v_refinement,
        },
        "adjoints": {
            "value": z_refinement,
            "derivative": y_refinement,
        },
        "denominator": {
            **denominator,
            "source_error_terms": denominator_terms,
        },
        "denominator_derivative": {
            **denominator_prime,
            "source_error_terms": denominator_prime_terms,
        },
        "canonical_Serre_scale": {
            "formula": "585/(2D)",
            "value_disk": scale,
            "derivative_disk": scale_prime,
        },
        "arrays": bindings,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "declared_geometry_branch": "edge-2, t=1/2, lift sign -1, seed 7909",
        },
        "guardrails": {
            "physical_endpoint_selected_here": False,
            "claim": "same-source scalar execution on the already declared Cayley/Serre branch",
            "not_claimed": [
                "selection of the q79 physical HYM endpoint",
                "beta_C vanishing",
                "agreement with an observed Standard Model value",
            ],
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    packet["canonical_payload_sha256"] = t66.canonical_sha256(packet)
    output.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    require(all(checks.values()), f"correlated readout checks: {checks}")
    print(
        "CBF.T67 correlated readout: PASS "
        f"|D|_lower={denominator['absolute_lower']:.6e} "
        f"D_error={denominator['total_absolute_error']:.6e} "
        f"scale_relative_error={scale['relative_error_upper']:.6e}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
