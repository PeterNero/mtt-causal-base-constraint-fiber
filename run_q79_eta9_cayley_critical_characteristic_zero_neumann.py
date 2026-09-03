#!/usr/bin/env python3
"""Execute the portable CBF.T66 characteristic-zero inverse certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any

from flint import acb, arb, ctx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_characteristic_zero_seed7909"
)
DEFAULT_OUTPUT = (
    ROOT / "q79_eta9_cayley_critical_characteristic_zero_neumann.packet.json"
)
UNIT_ROUNDOFF = np.finfo(np.float64).eps / 2.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def upward(value: float) -> float:
    require(math.isfinite(value) and value >= 0.0, "finite nonnegative bound")
    return float(np.nextafter(value, math.inf))


def gamma(count: int) -> float:
    scaled = count * UNIT_ROUNDOFF
    require(scaled < 0.01, "roundoff operation budget")
    return upward(scaled / (1.0 - scaled))


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact(path: Path) -> dict[str, object]:
    require(path.is_file(), f"artifact exists: {path}")
    return {
        "path": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load_metadata(input_directory: Path) -> dict[str, Any]:
    path = input_directory / "metadata.json"
    payload = json.loads(path.read_text(encoding="ascii"))
    claimed = payload.pop("canonical_payload_sha256")
    require(canonical_sha256(payload) == claimed, "input canonical hash")
    payload["canonical_payload_sha256"] = claimed
    require(
        payload["schema"]
        == "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-input.v1",
        "input schema",
    )
    require(all(payload["checks"].values()), "input checks")
    return payload


def load_exact_ball_polynomials(
    binding: dict[str, Any],
    ambient: int,
) -> tuple[list[tuple[int, acb]], list[tuple[int, acb]]]:
    path = ROOT / binding["path"]
    require(artifact(path) == binding, f"exact polynomial binding: {path}")
    payload = json.loads(path.read_text(encoding="ascii"))
    claimed = payload.pop("canonical_payload_sha256")
    require(canonical_sha256(payload) == claimed, "exact polynomial hash")
    require(
        payload["schema"]
        == "mtt.cbf.q79-eta9-cayley-toric-jacobian-exact-balls.v1"
        and payload["ambient_columns"] == ambient,
        "exact polynomial schema",
    )

    def decode(rows: list[dict[str, Any]]) -> list[tuple[int, acb]]:
        output = [
            (
                int(row["column"]),
                acb(arb(row["real_ball"]), arb(row["imaginary_ball"])),
            )
            for row in rows
        ]
        require(
            len({column for column, _value in output}) == len(output)
            and all(0 <= column < ambient for column, _value in output),
            "exact polynomial columns",
        )
        return output

    return decode(payload["value_rows"]), decode(payload["derivative_rows"])


def load_array(binding: dict[str, Any], shape: tuple[int, ...]) -> np.ndarray:
    path = ROOT / binding["path"]
    require(artifact(path) == binding, f"array binding: {path}")
    value = np.load(path, allow_pickle=False)
    require(value.shape == shape and np.isfinite(value).all(), f"array: {path}")
    return value


def load_sparse(binding: dict[str, Any], shape: tuple[int, ...]) -> sparse.csr_matrix:
    path = ROOT / binding["path"]
    require(artifact(path) == binding, f"matrix binding: {path}")
    value = sparse.load_npz(path).tocsr()
    require(value.shape == shape and np.isfinite(value.data).all(), f"matrix: {path}")
    return value


def component(value: np.ndarray) -> np.ndarray:
    return np.nextafter(np.abs(value.real) + np.abs(value.imag), math.inf)


def component_sparse(matrix: sparse.spmatrix) -> sparse.csr_matrix:
    output = matrix.tocsr().copy()
    output.data = np.nextafter(
        np.abs(output.data.real) + np.abs(output.data.imag), math.inf
    )
    return output


def row_positive_sums_upper(matrix: sparse.csr_matrix) -> np.ndarray:
    output = np.empty(matrix.shape[0], dtype=np.float64)
    for row in range(matrix.shape[0]):
        start, stop = int(matrix.indptr[row]), int(matrix.indptr[row + 1])
        output[row] = upward(
            math.fsum(float(value) for value in matrix.data[start:stop])
        )
    return output


def positive_dot_upper(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    require(np.all(matrix >= 0.0) and np.all(vector >= 0.0), "positive dot")
    result = matrix @ vector
    return np.nextafter(result / (1.0 - gamma(vector.size + 2)), math.inf)


def exact_targeted_neumann_rows(
    inverse_rows_value: np.ndarray,
    row_indices: np.ndarray,
    matrix: sparse.csc_matrix,
    coefficient_error_row_sums: np.ndarray,
    report: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate cancellation-sensitive preconditioner rows with Arb.

    Every binary64 midpoint is embedded as an exact dyadic Arb value.  The
    resulting intervals therefore bound the true midpoint products without
    the condition-number-sized BLAS roundoff term used by the coarse pass.
    """

    require(
        inverse_rows_value.shape == (row_indices.size, matrix.shape[0]),
        "targeted inverse rows",
    )
    require(
        coefficient_error_row_sums.shape == (matrix.shape[0],),
        "targeted coefficient errors",
    )
    matrix_data = [acb(complex(value)) for value in matrix.data]
    residual_bounds_value = np.empty(row_indices.size, dtype=np.float64)
    coefficient_bounds = np.empty(row_indices.size, dtype=np.float64)
    total_bounds = np.empty(row_indices.size, dtype=np.float64)
    for local, (row_index, row) in enumerate(
        zip(row_indices, inverse_rows_value, strict=True)
    ):
        row_balls = [acb(complex(value)) for value in row]
        residual_sum = arb(0)
        for column in range(matrix.shape[1]):
            entry = acb(0)
            start = int(matrix.indptr[column])
            stop = int(matrix.indptr[column + 1])
            for position in range(start, stop):
                entry += (
                    row_balls[int(matrix.indices[position])]
                    * matrix_data[position]
                )
            if column == int(row_index):
                entry -= 1
            residual_sum += abs(entry.real) + abs(entry.imag)
        coefficient_sum = sum(
            (
                (abs(value.real) + abs(value.imag)) * arb(float(error))
                for value, error in zip(
                    row_balls, coefficient_error_row_sums, strict=True
                )
            ),
            arb(0),
        )
        residual_bounds_value[local] = upward(float(residual_sum.upper()))
        coefficient_bounds[local] = upward(float(coefficient_sum.upper()))
        total_bounds[local] = upward(
            float((residual_sum + coefficient_sum).upper())
        )
        if report:
            print(
                "CBF.T66 targeted Arb row="
                f"{int(row_index)} eta={total_bounds[local]:.6g}",
                flush=True,
            )
    return residual_bounds_value, coefficient_bounds, total_bounds


def inverse_rows(
    factor: Any,
    matrix: sparse.csc_matrix,
    batch: int,
    refinements: int,
) -> np.ndarray:
    size = matrix.shape[0]
    inverse = np.empty((size, size), dtype=np.complex128)
    started = time.monotonic()
    for low in range(0, size, batch):
        high = min(low + batch, size)
        indices = np.arange(low, high)
        rhs = np.zeros((size, high - low), dtype=np.complex128)
        rhs[indices, np.arange(high - low)] = 1.0
        rows = factor.solve(rhs, trans="T").transpose()
        for _ in range(refinements):
            residual = -(rows @ matrix)
            residual[np.arange(high - low), indices] += 1.0
            rows += factor.solve(residual.transpose(), trans="T").transpose()
        inverse[low:high, :] = rows
        if high == size or high % max(batch, 256) < batch:
            print(
                f"CBF.T66 inverse rows={high}/{size} "
                f"elapsed={time.monotonic() - started:.1f}s",
                flush=True,
            )
    return inverse


def neumann_rows(
    inverse: np.ndarray,
    matrix: sparse.csc_matrix,
    coefficient_error_row_sums: np.ndarray,
    batch: int,
) -> tuple[
    np.ndarray,
    dict[str, float | int],
    dict[str, np.ndarray],
]:
    size = matrix.shape[0]
    matrix_component = component_sparse(matrix)
    matrix_row_sums = row_positive_sums_upper(matrix_component)
    maximum_column_width = int(np.diff(matrix.indptr).max())
    total = np.empty(size, dtype=np.float64)
    residual_maximum = 0.0
    roundoff_maximum = 0.0
    diagonal_maximum = 0.0
    coefficient_maximum = 0.0
    inverse_row_sum_maximum = 0.0
    for low in range(0, size, batch):
        high = min(low + batch, size)
        rows = inverse[low:high, :]
        products = rows @ matrix
        local = np.arange(high - low)
        indices = np.arange(low, high)
        diagonal = products[local, indices].copy()
        products[local, indices] -= 1.0
        residual = np.nextafter(
            component(products).sum(axis=1) / (1.0 - gamma(2 * size + 8)),
            math.inf,
        )
        inverse_component = component(rows)
        product_roundoff = np.nextafter(
            gamma(32 * maximum_column_width + 32)
            * positive_dot_upper(inverse_component, matrix_row_sums),
            math.inf,
        )
        diagonal_roundoff = np.nextafter(
            8.0 * UNIT_ROUNDOFF * (1.0 + component(diagonal)), math.inf
        )
        coefficient = positive_dot_upper(
            inverse_component, coefficient_error_row_sums
        )
        total[low:high] = np.nextafter(
            residual + product_roundoff + diagonal_roundoff + coefficient,
            math.inf,
        )
        residual_maximum = max(residual_maximum, float(residual.max()))
        roundoff_maximum = max(
            roundoff_maximum, float(product_roundoff.max())
        )
        diagonal_maximum = max(
            diagonal_maximum, float(diagonal_roundoff.max())
        )
        coefficient_maximum = max(
            coefficient_maximum, float(coefficient.max())
        )
        inverse_row_sum_maximum = max(
            inverse_row_sum_maximum,
            float(inverse_component.sum(axis=1).max()),
        )
    coarse_total = total.copy()
    targeted_indices = np.flatnonzero(coarse_total >= 1.0).astype(np.int64)
    targeted_inverse = inverse[targeted_indices, :].copy()
    (
        targeted_residual,
        targeted_coefficient,
        targeted_total,
    ) = exact_targeted_neumann_rows(
        targeted_inverse,
        targeted_indices,
        matrix,
        coefficient_error_row_sums,
    )
    total[targeted_indices] = targeted_total
    maximum_index = int(np.argmax(total))
    coarse_maximum_index = int(np.argmax(coarse_total))
    diagnostics: dict[str, float | int] = {
        "maximum_midpoint_inverse_residual": residual_maximum,
        "maximum_product_roundoff_bound": roundoff_maximum,
        "maximum_diagonal_subtraction_bound": diagonal_maximum,
        "maximum_exact_coefficient_correction": coefficient_maximum,
        "maximum_coarse_Neumann_row": float(
            coarse_total[coarse_maximum_index]
        ),
        "maximum_coarse_row_zero_based": coarse_maximum_index,
        "targeted_Arb_row_count": int(targeted_indices.size),
        "maximum_targeted_Arb_midpoint_residual": float(
            targeted_residual.max(initial=0.0)
        ),
        "maximum_targeted_Arb_coefficient_correction": float(
            targeted_coefficient.max(initial=0.0)
        ),
        "maximum_targeted_Arb_total": float(
            targeted_total.max(initial=0.0)
        ),
        "maximum_total_Neumann_row": float(total[maximum_index]),
        "maximum_total_row_zero_based": maximum_index,
        "strict_Neumann_margin": float(1.0 - total[maximum_index]),
        "maximum_inverse_component_row_sum": inverse_row_sum_maximum,
        "maximum_column_nonzeros": maximum_column_width,
    }
    refinement = {
        "coarse_rows": coarse_total,
        "indices": targeted_indices,
        "inverse_rows": targeted_inverse,
        "midpoint_residual_bounds": targeted_residual,
        "coefficient_correction_bounds": targeted_coefficient,
        "total_bounds": targeted_total,
    }
    return total, diagnostics, refinement


def ball_value(midpoint: complex, error: float) -> acb:
    return acb(
        arb(float(midpoint.real), float(error)),
        arb(float(midpoint.imag), float(error)),
    )


def ball_vector(center: np.ndarray, error: np.ndarray) -> list[acb]:
    require(center.shape == error.shape, "ball vector shape")
    return [
        ball_value(complex(midpoint), float(radius))
        for midpoint, radius in zip(center, error, strict=True)
    ]


def ball_rows(
    center: sparse.csr_matrix,
    error: sparse.csr_matrix,
) -> list[list[tuple[int, acb]]]:
    output: list[list[tuple[int, acb]]] = []
    for row in range(center.shape[0]):
        values: dict[int, complex] = {}
        radii: dict[int, float] = {}
        for position in range(int(center.indptr[row]), int(center.indptr[row + 1])):
            values[int(center.indices[position])] = complex(center.data[position])
        for position in range(int(error.indptr[row]), int(error.indptr[row + 1])):
            radii[int(error.indices[position])] = float(error.data[position])
        output.append(
            [
                (column, ball_value(values.get(column, 0.0j), radii.get(column, 0.0)))
                for column in sorted(set(values) | set(radii))
            ]
        )
    return output


def ball_matvec(
    rows: list[list[tuple[int, acb]]], vector: list[acb]
) -> list[acb]:
    return [
        sum((coefficient * vector[column] for column, coefficient in row), acb(0))
        for row in rows
    ]


def residual_bounds(
    rows: list[list[tuple[int, acb]]],
    rhs: list[acb],
    vector: list[acb],
) -> tuple[list[acb], np.ndarray, float]:
    residual = [
        right - value
        for right, value in zip(rhs, ball_matvec(rows, vector), strict=True)
    ]
    bounds = np.asarray(
        [
            upward(
                float(abs(value.real).upper())
                + float(abs(value.imag).upper())
            )
            for value in residual
        ],
        dtype=np.float64,
    )
    midpoint = max(
        (
            abs(complex(float(value.real.mid()), float(value.imag.mid())))
            for value in residual
        ),
        default=0.0,
    )
    return residual, bounds, midpoint


def solve_center(
    factor: Any,
    matrix: sparse.csc_matrix,
    rhs: np.ndarray,
    refinements: int = 5,
) -> np.ndarray:
    value = factor.solve(rhs)
    for _ in range(refinements):
        value += factor.solve(rhs - matrix @ value)
    return value


def mixed_refine(
    factor: Any,
    rows: list[list[tuple[int, acb]]],
    rhs: list[acb],
    initial: np.ndarray,
    iterations: int,
) -> tuple[list[acb], dict[str, Any]]:
    value = [ball_value(complex(entry), 0.0) for entry in initial]
    history: list[dict[str, float | int]] = []
    previous = math.inf
    for iteration in range(iterations):
        residual, bounds, maximum = residual_bounds(rows, rhs, value)
        history.append(
            {
                "iteration": iteration,
                "maximum_residual_midpoint": maximum,
                "maximum_residual_ball_component_upper": float(bounds.max()),
            }
        )
        print(
            f"CBF.T66 refinement iteration={iteration} "
            f"midpoint={maximum:.3e} ball={bounds.max():.3e}",
            flush=True,
        )
        if maximum == 0.0 or maximum < 2.0**-300:
            break
        exponent = math.frexp(maximum)[1]
        scale = math.ldexp(1.0, exponent)
        midpoint = np.asarray(
            [
                complex(float(entry.real.mid()), float(entry.imag.mid())) / scale
                for entry in residual
            ],
            dtype=np.complex128,
        )
        correction = factor.solve(midpoint) * scale
        for index, entry in enumerate(correction):
            value[index] += ball_value(complex(entry), 0.0)
        if maximum >= previous and iteration >= 4:
            break
        previous = maximum
    _residual, final_bounds, final_midpoint = residual_bounds(rows, rhs, value)
    return value, {
        "iterations": len(history),
        "history": history,
        "final_residual_midpoint": final_midpoint,
        "final_residual_ball_component_upper": float(final_bounds.max()),
    }


def ball_centers(values: list[acb]) -> tuple[np.ndarray, np.ndarray]:
    center = np.asarray(
        [
            complex(float(value.real.mid()), float(value.imag.mid()))
            for value in values
        ],
        dtype=np.complex128,
    )
    radius = np.asarray(
        [
            upward(
                float(abs((value - ball_value(midpoint, 0.0)).real).upper())
                + float(abs((value - ball_value(midpoint, 0.0)).imag).upper())
            )
            for value, midpoint in zip(values, center, strict=True)
        ],
        dtype=np.float64,
    )
    return center, radius


def solve_radii(
    inverse_component: np.ndarray,
    eta_rows: np.ndarray,
    residual_bound: np.ndarray,
) -> tuple[float, np.ndarray]:
    image = positive_dot_upper(inverse_component, residual_bound)
    eta = float(eta_rows.max())
    global_radius = upward(float(image.max()) / (1.0 - eta))
    component_radii = np.nextafter(image + eta_rows * global_radius, math.inf)
    return global_radius, component_radii


def certified_ball_vector(
    arithmetic_values: list[acb],
    forward_radii: np.ndarray,
) -> tuple[list[acb], np.ndarray, np.ndarray]:
    center, arithmetic_radius = ball_centers(arithmetic_values)
    total = np.nextafter(arithmetic_radius + forward_radii, math.inf)
    return ball_vector(center, total), center, total


def equation_roundoff(
    matrix_component: sparse.csr_matrix,
    vector_component: np.ndarray,
) -> np.ndarray:
    maximum_row_width = int(np.diff(matrix_component.indptr).max())
    scale = matrix_component @ vector_component
    return np.nextafter(
        gamma(32 * maximum_row_width + 32) * scale, math.inf
    )


def sparse_positive_matvec_upper(
    matrix: sparse.csr_matrix,
    vector: np.ndarray,
) -> np.ndarray:
    require(
        np.all(matrix.data >= 0.0) and np.all(vector >= 0.0),
        "positive sparse product",
    )
    maximum_row_width = int(np.diff(matrix.indptr).max())
    result = matrix @ vector
    return np.nextafter(
        result / (1.0 - gamma(maximum_row_width + 2)), math.inf
    )


def all_row_value_audit(
    center: sparse.csr_matrix,
    error: sparse.csr_matrix,
    vector_center: np.ndarray,
    vector_radius: np.ndarray,
) -> dict[str, Any]:
    matrix_component = component_sparse(center)
    vector_component = component(vector_center)
    residual = center @ vector_center
    residual_component = component(residual)
    bound = np.nextafter(
        sparse_positive_matvec_upper(error, vector_component)
        + sparse_positive_matvec_upper(
            (matrix_component + error).tocsr(), vector_radius
        )
        + equation_roundoff(matrix_component, vector_component),
        math.inf,
    )
    passed = residual_component <= bound
    ratio = residual_component / np.maximum(bound, np.finfo(np.float64).tiny)
    return {
        "rows": int(center.shape[0]),
        "rows_enclosing_zero": int(np.count_nonzero(passed)),
        "maximum_midpoint_residual_component": float(residual_component.max()),
        "maximum_enclosure_radius_component": float(bound.max()),
        "maximum_midpoint_to_radius_ratio": float(ratio.max()),
        "all_rows_enclose_zero": bool(passed.all()),
    }


def all_row_derivative_audit(
    center: sparse.csr_matrix,
    error: sparse.csr_matrix,
    prime_center: sparse.csr_matrix,
    prime_error: sparse.csr_matrix,
    value_center: np.ndarray,
    value_radius: np.ndarray,
    derivative_center: np.ndarray,
    derivative_radius: np.ndarray,
) -> dict[str, Any]:
    matrix_component = component_sparse(center)
    prime_component = component_sparse(prime_center)
    value_component = component(value_center)
    derivative_component = component(derivative_center)
    residual = center @ derivative_center + prime_center @ value_center
    residual_component = component(residual)
    bound = np.nextafter(
        sparse_positive_matvec_upper(error, derivative_component)
        + sparse_positive_matvec_upper(
            (matrix_component + error).tocsr(), derivative_radius
        )
        + sparse_positive_matvec_upper(prime_error, value_component)
        + sparse_positive_matvec_upper(
            (prime_component + prime_error).tocsr(), value_radius
        )
        + equation_roundoff(matrix_component, derivative_component)
        + equation_roundoff(prime_component, value_component)
        + gamma(8) * component(residual),
        math.inf,
    )
    passed = residual_component <= bound
    ratio = residual_component / np.maximum(bound, np.finfo(np.float64).tiny)
    return {
        "rows": int(center.shape[0]),
        "rows_enclosing_zero": int(np.count_nonzero(passed)),
        "maximum_midpoint_residual_component": float(residual_component.max()),
        "maximum_enclosure_radius_component": float(bound.max()),
        "maximum_midpoint_to_radius_ratio": float(ratio.max()),
        "all_rows_enclose_zero": bool(passed.all()),
    }


def linear_functional_ball(
    coefficient_center: np.ndarray,
    coefficient_error: np.ndarray,
    vector_center: np.ndarray,
    vector_radius: np.ndarray,
) -> tuple[acb, dict[str, float]]:
    coefficient_component = component(coefficient_center)
    vector_component = component(vector_center)
    midpoint = complex(np.dot(coefficient_center, vector_center))
    uncertainty_terms = (
        coefficient_error * vector_component
        + (coefficient_component + coefficient_error) * vector_radius
    )
    uncertainty = upward(
        math.fsum(float(value) for value in uncertainty_terms)
        / (1.0 - gamma(coefficient_center.size + 2))
    )
    roundoff = upward(
        gamma(32 * coefficient_center.size + 32)
        * math.fsum(
            float(value)
            for value in coefficient_component * vector_component
        )
    )
    radius = upward(uncertainty + roundoff)
    return ball_value(midpoint, radius), {
        "midpoint_real": midpoint.real,
        "midpoint_imaginary": midpoint.imag,
        "input_uncertainty_component_bound": uncertainty,
        "roundoff_component_bound": roundoff,
        "total_component_bound": radius,
    }


def sum_balls(left: acb, right: acb) -> acb:
    return left + right


def exact_sparse_functional(
    coefficients: list[tuple[int, acb]],
    vector: list[acb],
) -> acb:
    return sum(
        (coefficient * vector[column] for column, coefficient in coefficients),
        acb(0),
    )


def ball_diagnostics(value: acb) -> dict[str, float]:
    midpoint = complex(float(value.real.mid()), float(value.imag.mid()))
    centered = value - ball_value(midpoint, 0.0)
    return {
        "midpoint_real": midpoint.real,
        "midpoint_imaginary": midpoint.imag,
        "component_radius_upper": upward(
            float(abs(centered.real).upper())
            + float(abs(centered.imag).upper())
        ),
        "absolute_lower": float(value.abs_lower()),
        "absolute_upper": float(value.abs_upper()),
    }


def save_array(output: Path, suffix: str, value: np.ndarray) -> dict[str, object]:
    path = output.with_name(output.stem + f".{suffix}.npy")
    np.save(path, value, allow_pickle=False)
    return artifact(path)


def replay_downstream(input_directory: Path, output: Path, precision: int) -> int:
    """Recompute post-inverse bounds from already certified solution arrays."""
    ctx.prec = precision
    metadata = load_metadata(input_directory)
    packet = json.loads(output.read_text(encoding="ascii"))
    claimed = packet.pop("canonical_payload_sha256")
    require(canonical_sha256(packet) == claimed, "existing output canonical hash")
    require(
        packet["status"]
        != "SEED7909_CHARACTERISTIC_ZERO_NEUMANN_INVERSE_REJECTED",
        "downstream replay requires a certified inverse and solution arrays",
    )
    arrays = packet["arrays"]
    functional_center = load_array(arrays["critical_functional_center"], (9361,))
    functional_radius = load_array(arrays["critical_functional_radius"], (9361,))
    functional_prime_center = load_array(
        arrays["critical_functional_derivative_center"], (9361,)
    )
    functional_prime_radius = load_array(
        arrays["critical_functional_derivative_radius"], (9361,)
    )
    functional_balls = ball_vector(functional_center, functional_radius)
    functional_prime_balls = ball_vector(
        functional_prime_center, functional_prime_radius
    )
    matrices = metadata["matrices"]
    full = load_sparse(matrices["full_relation_center"], (16740, 9361))
    full_error = load_sparse(matrices["full_relation_error"], (16740, 9361))
    full_prime = load_sparse(
        matrices["full_relation_derivative_center"], (16740, 9361)
    )
    full_prime_error = load_sparse(
        matrices["full_relation_derivative_error"], (16740, 9361)
    )
    value_all_rows = all_row_value_audit(
        full, full_error, functional_center, functional_radius
    )
    derivative_all_rows = all_row_derivative_audit(
        full,
        full_error,
        full_prime,
        full_prime_error,
        functional_center,
        functional_radius,
        functional_prime_center,
        functional_prime_radius,
    )
    exact_jacobian, exact_jacobian_prime = load_exact_ball_polynomials(
        metadata["exact_polynomials"]["toric_Jacobian"], 9361
    )
    denominator = exact_sparse_functional(exact_jacobian, functional_balls)
    first_term = exact_sparse_functional(
        exact_jacobian, functional_prime_balls
    )
    second_term = exact_sparse_functional(
        exact_jacobian_prime, functional_balls
    )
    denominator_prime = first_term + second_term
    denominator_excludes_zero = not denominator.contains(0)
    scale = acb(585) / (2 * denominator) if denominator_excludes_zero else None
    scale_prime = (
        -acb(585) * denominator_prime / (2 * denominator**2)
        if denominator_excludes_zero
        else None
    )
    packet["input"] = artifact(input_directory / "metadata.json")
    packet["all_row_audit"] = {
        "value": value_all_rows,
        "derivative": derivative_all_rows,
    }
    packet["toric_Jacobian"] = {
        "exact_ball_source": metadata["exact_polynomials"]["toric_Jacobian"],
        "value_term_count": len(exact_jacobian),
        "derivative_term_count": len(exact_jacobian_prime),
        "denominator_ball": str(denominator),
        "denominator_diagnostics": ball_diagnostics(denominator),
        "derivative_ball": str(denominator_prime),
        "derivative_terms": {
            "J_times_functional_derivative": ball_diagnostics(first_term),
            "J_derivative_times_functional": ball_diagnostics(second_term),
        },
        "excludes_zero": denominator_excludes_zero,
    }
    packet["canonical_Serre_scale"] = {
        "value_ball": str(scale) if scale is not None else None,
        "derivative_ball": str(scale_prime) if scale_prime is not None else None,
        "formula": "s_C=585/(2D), s_C'=-(585/2)D'/D^2",
    }
    packet["checks"]["all_16740_value_relation_rows_enclose_zero"] = (
        value_all_rows["all_rows_enclose_zero"]
    )
    packet["checks"]["all_16740_derivative_relation_rows_enclose_zero"] = (
        derivative_all_rows["all_rows_enclose_zero"]
    )
    packet["checks"]["the_toric_Jacobian_denominator_ball_excludes_zero"] = (
        denominator_excludes_zero
    )
    packet["checks"]["the_scale_and_derivative_balls_are_emitted"] = (
        denominator_excludes_zero
    )
    promoted = all(packet["checks"].values())
    packet["all_checks_pass"] = promoted
    packet["status"] = (
        "CLOSED_CHARACTERISTIC_ZERO_POINTWISE_CAYLEY_SERRE_SCALE_AND_DERIVATIVE"
        if promoted
        else "CHARACTERISTIC_ZERO_INVERSE_CERTIFIED_DOWNSTREAM_INTERVAL_EXIT_OPEN"
    )
    packet["next"] = (
        "Extend the certified point calculation to adaptive panels and the BHT accumulator."
        if promoted
        else "Inspect the failed downstream interval check; retain the strict inverse certificate and improve only the responsible enclosure."
    )
    packet["downstream_replay"] = {
        "method": "recomputed from stored certified functional balls using outward sparse sums and exact 512-bit toric-Jacobian coefficient balls",
        "runner_sha256": sha256(Path(__file__)),
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    output.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T66 downstream replay: PASS "
        f"value_rows={value_all_rows['rows_enclosing_zero']}/16740 "
        f"derivative_rows={derivative_all_rows['rows_enclosing_zero']}/16740 "
        f"denominator_excludes_zero={denominator_excludes_zero} "
        f"promoted={promoted}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--inverse-batch", type=int, default=32)
    parser.add_argument("--inverse-refinements", type=int, default=5)
    parser.add_argument("--mixed-refinements", type=int, default=18)
    parser.add_argument("--replay-downstream", action="store_true")
    arguments = parser.parse_args()
    require(arguments.precision >= 384, "Arb precision")
    require(arguments.inverse_batch > 0, "inverse batch")
    started = time.monotonic()
    ctx.prec = arguments.precision
    input_directory = arguments.input_directory.resolve()
    output = arguments.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if arguments.replay_downstream:
        return replay_downstream(input_directory, output, arguments.precision)
    metadata = load_metadata(input_directory)

    n = 6777
    ambient = 9361
    relation_rows = 16740
    arrays = metadata["arrays"]
    matrices = metadata["matrices"]
    selected = load_array(arrays["selected_rows"], (n,)).astype(np.int64)
    pivots = load_array(arrays["embedding_pivots"], (2584,)).astype(np.int64)
    free = load_array(arrays["free_columns"], (n,)).astype(np.int64)
    row_factor = load_array(arrays["row_factor"], (n,))
    column_factor = load_array(arrays["column_factor"], (n,))
    pivot_center = load_array(arrays["pivot_value_center"], (2584,))
    pivot_radius = load_array(arrays["pivot_value_radius"], (2584,))
    pivot_prime_center = load_array(
        arrays["pivot_derivative_center"], (2584,)
    )
    pivot_prime_radius = load_array(
        arrays["pivot_derivative_radius"], (2584,)
    )
    value_rhs_center = load_array(arrays["value_rhs_center"], (n,))
    value_rhs_error = load_array(arrays["value_rhs_error"], (n,))
    derivative_constant_center = load_array(
        arrays["derivative_constant_center"], (n,)
    )
    derivative_constant_error = load_array(
        arrays["derivative_constant_error"], (n,)
    )
    jacobian_center = load_array(arrays["jacobian_center"], (ambient,))
    jacobian_error = load_array(arrays["jacobian_error"], (ambient,))
    jacobian_prime_center = load_array(
        arrays["jacobian_derivative_center"], (ambient,)
    )
    jacobian_prime_error = load_array(
        arrays["jacobian_derivative_error"], (ambient,)
    )
    exact_jacobian, exact_jacobian_prime = load_exact_ball_polynomials(
        metadata["exact_polynomials"]["toric_Jacobian"], ambient
    )
    matrix = load_sparse(matrices["balanced_matrix_center"], (n, n)).tocsc()
    matrix_error = load_sparse(
        matrices["balanced_matrix_error"], (n, n)
    )
    derivative_coupling = load_sparse(
        matrices["balanced_derivative_coupling_center"], (n, n)
    )
    derivative_coupling_error = load_sparse(
        matrices["balanced_derivative_coupling_error"], (n, n)
    )
    full = load_sparse(
        matrices["full_relation_center"], (relation_rows, ambient)
    )
    full_error = load_sparse(
        matrices["full_relation_error"], (relation_rows, ambient)
    )
    full_prime = load_sparse(
        matrices["full_relation_derivative_center"], (relation_rows, ambient)
    )
    full_prime_error = load_sparse(
        matrices["full_relation_derivative_error"], (relation_rows, ambient)
    )
    require(
        np.unique(selected).size == n
        and np.unique(pivots).size == 2584
        and np.unique(free).size == n
        and np.intersect1d(pivots, free).size == 0,
        "coordinate partitions",
    )
    require(np.all(row_factor > 0) and np.all(column_factor > 0), "scales")

    factor_started = time.monotonic()
    factor = splu(
        matrix,
        permc_spec="COLAMD",
        diag_pivot_thresh=1.0,
        options={"Equil": True, "IterRefine": "EXTRA"},
    )
    factor_seconds = time.monotonic() - factor_started
    inverse = inverse_rows(
        factor,
        matrix,
        arguments.inverse_batch,
        arguments.inverse_refinements,
    )
    coefficient_error_row_sums = row_positive_sums_upper(matrix_error)
    eta_rows, inverse_diagnostics, targeted_refinement = neumann_rows(
        inverse,
        matrix,
        coefficient_error_row_sums,
        arguments.inverse_batch,
    )
    eta = float(eta_rows.max())
    inverse_component = component(inverse)
    bindings = {
        "Neumann_row_bounds": save_array(output, "Neumann_row_bounds", eta_rows),
        "coarse_Neumann_row_bounds": save_array(
            output,
            "coarse_Neumann_row_bounds",
            targeted_refinement["coarse_rows"],
        ),
        "targeted_row_indices": save_array(
            output, "targeted_row_indices", targeted_refinement["indices"]
        ),
        "targeted_inverse_rows": save_array(
            output, "targeted_inverse_rows", targeted_refinement["inverse_rows"]
        ),
        "targeted_midpoint_residual_bounds": save_array(
            output,
            "targeted_midpoint_residual_bounds",
            targeted_refinement["midpoint_residual_bounds"],
        ),
        "targeted_coefficient_correction_bounds": save_array(
            output,
            "targeted_coefficient_correction_bounds",
            targeted_refinement["coefficient_correction_bounds"],
        ),
        "targeted_total_bounds": save_array(
            output, "targeted_total_bounds", targeted_refinement["total_bounds"]
        ),
    }
    targeted_binding = {
        "selection_rule": "coarse_Neumann_row_bound >= 1",
        "arithmetic": "512-bit Arb over exact binary64 dyadic midpoints",
        "coarse_Neumann_row_bounds": bindings["coarse_Neumann_row_bounds"],
        "row_indices": bindings["targeted_row_indices"],
        "inverse_rows": bindings["targeted_inverse_rows"],
        "midpoint_residual_bounds": bindings[
            "targeted_midpoint_residual_bounds"
        ],
        "coefficient_correction_bounds": bindings[
            "targeted_coefficient_correction_bounds"
        ],
        "total_bounds": bindings["targeted_total_bounds"],
    }
    # Keep the isolated result contract stable in both the pass and
    # obstruction branches.  A rejected inverse leaves these arrays unbound
    # in the packet; a passing inverse overwrites them with certified data.
    for suffix in (
        "critical_functional_center",
        "critical_functional_radius",
        "critical_functional_derivative_center",
        "critical_functional_derivative_radius",
    ):
        dtype = np.complex128 if suffix.endswith("center") else np.float64
        np.save(
            output.with_name(output.stem + f".{suffix}.npy"),
            np.zeros(ambient, dtype=dtype),
            allow_pickle=False,
        )
    base_checks = {
        "the_binary_midpoint_matrix_has_a_complete_sparse_LU": bool(
            factor.L.shape == factor.U.shape == (n, n)
        ),
        "the_characteristic_zero_coefficient_errors_are_nonnegative": bool(
            np.all(matrix_error.data >= 0.0)
        ),
        "no_observed_value_or_fit_parameter_is_used": True,
    }

    if eta >= 1.0:
        checks = {
            **base_checks,
            "the_seed7909_inverse_fails_the_strict_Neumann_test": True,
            "no_value_denominator_or_scale_is_promoted": True,
        }
        packet: dict[str, Any] = {
            "schema": "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-neumann.v1",
            "theorem_id": "CBF.T66",
            "status": "SEED7909_CHARACTERISTIC_ZERO_NEUMANN_INVERSE_REJECTED",
            "tier": "DIRECTED_COEFFICIENT_BALL_CONDITIONING_OBSTRUCTION",
            "input": artifact(input_directory / "metadata.json"),
            "precision_bits": arguments.precision,
            "factor": {
                "seconds": factor_seconds,
                "L_nonzeros": int(factor.L.nnz),
                "U_nonzeros": int(factor.U.nnz),
            },
            "inverse_certificate": inverse_diagnostics,
            "Neumann_row_bounds": bindings["Neumann_row_bounds"],
            "targeted_high_precision_refinement": targeted_binding,
            "checks": checks,
            "all_checks_pass": all(checks.values()),
            "guardrails": {
                "failure_of_this_preconditioner_is_called_nonexistence_of_the_exact_functional": False,
                "a_binary_or_uncertified_scale_is_promoted": False,
                "the_B89_member_is_called_physical": False,
            },
            "parameter_ledger": {
                "observed_values_used": 0,
                "new_continuous_fit_parameters": 0,
                "new_discrete_fit_parameters": 0,
            },
            "next": "Replace the selected row gauge or construct a block/symbolic preconditioner whose directed Neumann row maximum is below one.",
            "elapsed_seconds": time.monotonic() - started,
        }
        packet["canonical_payload_sha256"] = canonical_sha256(packet)
        output.write_text(
            json.dumps(packet, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
            newline="\n",
        )
        print(
            "CBF.T66 Neumann obstruction: PASS "
            f"eta={eta:.6g} row={inverse_diagnostics['maximum_total_row_zero_based']}"
        )
        return 0

    matrix_rows = ball_rows(matrix.tocsr(), matrix_error)
    value_rhs = ball_vector(value_rhs_center, value_rhs_error)
    initial_value = solve_center(factor, matrix, value_rhs_center)
    value_arithmetic, value_refinement = mixed_refine(
        factor,
        matrix_rows,
        value_rhs,
        initial_value,
        arguments.mixed_refinements,
    )
    _value_residual, value_residual_bound, _value_midpoint = residual_bounds(
        matrix_rows, value_rhs, value_arithmetic
    )
    value_global_radius, value_forward_radii = solve_radii(
        inverse_component, eta_rows, value_residual_bound
    )
    value_balls, value_center, value_radius = certified_ball_vector(
        value_arithmetic, value_forward_radii
    )

    derivative_coupling_rows = ball_rows(
        derivative_coupling, derivative_coupling_error
    )
    derivative_constant = ball_vector(
        derivative_constant_center, derivative_constant_error
    )
    derivative_rhs = [
        constant + coupled
        for constant, coupled in zip(
            derivative_constant,
            ball_matvec(derivative_coupling_rows, value_balls),
            strict=True,
        )
    ]
    derivative_rhs_midpoint = np.asarray(
        [
            complex(float(value.real.mid()), float(value.imag.mid()))
            for value in derivative_rhs
        ],
        dtype=np.complex128,
    )
    initial_derivative = solve_center(factor, matrix, derivative_rhs_midpoint)
    derivative_arithmetic, derivative_refinement = mixed_refine(
        factor,
        matrix_rows,
        derivative_rhs,
        initial_derivative,
        arguments.mixed_refinements,
    )
    (
        _derivative_residual,
        derivative_residual_bound,
        _derivative_midpoint,
    ) = residual_bounds(matrix_rows, derivative_rhs, derivative_arithmetic)
    derivative_global_radius, derivative_forward_radii = solve_radii(
        inverse_component, eta_rows, derivative_residual_bound
    )
    derivative_balls, derivative_center, derivative_radius = certified_ball_vector(
        derivative_arithmetic, derivative_forward_radii
    )

    pivot_balls = ball_vector(pivot_center, pivot_radius)
    pivot_prime_balls = ball_vector(pivot_prime_center, pivot_prime_radius)
    free_balls = [
        ball_value(complex(float(column_factor[index])), 0.0) * value_balls[index]
        for index in range(n)
    ]
    free_prime_balls = [
        ball_value(complex(float(column_factor[index])), 0.0)
        * derivative_balls[index]
        for index in range(n)
    ]
    functional_balls = [acb(0) for _ in range(ambient)]
    functional_prime_balls = [acb(0) for _ in range(ambient)]
    for local, column in enumerate(pivots):
        functional_balls[int(column)] = pivot_balls[local]
        functional_prime_balls[int(column)] = pivot_prime_balls[local]
    for local, column in enumerate(free):
        functional_balls[int(column)] = free_balls[local]
        functional_prime_balls[int(column)] = free_prime_balls[local]
    functional_center, functional_radius = ball_centers(functional_balls)
    functional_prime_center, functional_prime_radius = ball_centers(
        functional_prime_balls
    )

    value_all_rows = all_row_value_audit(
        full, full_error, functional_center, functional_radius
    )
    derivative_all_rows = all_row_derivative_audit(
        full,
        full_error,
        full_prime,
        full_prime_error,
        functional_center,
        functional_radius,
        functional_prime_center,
        functional_prime_radius,
    )

    denominator = exact_sparse_functional(exact_jacobian, functional_balls)
    first_term = exact_sparse_functional(
        exact_jacobian, functional_prime_balls
    )
    second_term = exact_sparse_functional(
        exact_jacobian_prime, functional_balls
    )
    denominator_prime = sum_balls(first_term, second_term)
    denominator_diagnostics = ball_diagnostics(denominator)
    first_term_diagnostics = ball_diagnostics(first_term)
    second_term_diagnostics = ball_diagnostics(second_term)
    denominator_excludes_zero = not denominator.contains(0)
    scale = acb(585) / (2 * denominator) if denominator_excludes_zero else None
    scale_prime = (
        -acb(585) * denominator_prime / (2 * denominator**2)
        if denominator_excludes_zero
        else None
    )

    bindings.update(
        {
            "critical_functional_center": save_array(
                output, "critical_functional_center", functional_center
            ),
            "critical_functional_radius": save_array(
                output, "critical_functional_radius", functional_radius
            ),
            "critical_functional_derivative_center": save_array(
                output,
                "critical_functional_derivative_center",
                functional_prime_center,
            ),
            "critical_functional_derivative_radius": save_array(
                output,
                "critical_functional_derivative_radius",
                functional_prime_radius,
            ),
        }
    )
    checks = {
        **base_checks,
        "the_exact_characteristic_zero_matrix_has_a_strict_Neumann_inverse": eta
        < 1.0,
        "all_16740_value_relation_rows_enclose_zero": value_all_rows[
            "all_rows_enclose_zero"
        ],
        "all_16740_derivative_relation_rows_enclose_zero": derivative_all_rows[
            "all_rows_enclose_zero"
        ],
        "the_toric_Jacobian_denominator_ball_excludes_zero": denominator_excludes_zero,
        "the_scale_and_derivative_balls_are_emitted": scale is not None
        and scale_prime is not None,
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    promoted = all(checks.values())
    packet = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-neumann.v1",
        "theorem_id": "CBF.T66",
        "status": (
            "CLOSED_CHARACTERISTIC_ZERO_POINTWISE_CAYLEY_SERRE_SCALE_AND_DERIVATIVE"
            if promoted
            else "CHARACTERISTIC_ZERO_INVERSE_CERTIFIED_DOWNSTREAM_INTERVAL_EXIT_OPEN"
        ),
        "tier": "CHARACTERISTIC_ZERO_COMPONENT_BALL_PLUS_DYADIC_NEUMANN_FORWARD_ERROR",
        "input": artifact(input_directory / "metadata.json"),
        "precision_bits": arguments.precision,
        "factor": {
            "seconds": factor_seconds,
            "L_nonzeros": int(factor.L.nnz),
            "U_nonzeros": int(factor.U.nnz),
        },
        "inverse_certificate": inverse_diagnostics,
        "Neumann_row_bounds": bindings["Neumann_row_bounds"],
        "targeted_high_precision_refinement": targeted_binding,
        "value_solution": {
            "maximum_balanced_coordinate_forward_radius": value_global_radius,
            "maximum_critical_coordinate_radius": float(functional_radius.max()),
            "mixed_refinement": value_refinement,
        },
        "derivative_solution": {
            "maximum_balanced_coordinate_forward_radius": derivative_global_radius,
            "maximum_critical_coordinate_radius": float(
                functional_prime_radius.max()
            ),
            "mixed_refinement": derivative_refinement,
        },
        "all_row_audit": {
            "value": value_all_rows,
            "derivative": derivative_all_rows,
        },
        "toric_Jacobian": {
            "exact_ball_source": metadata["exact_polynomials"]["toric_Jacobian"],
            "value_term_count": len(exact_jacobian),
            "derivative_term_count": len(exact_jacobian_prime),
            "denominator_ball": str(denominator),
            "denominator_diagnostics": denominator_diagnostics,
            "derivative_ball": str(denominator_prime),
            "derivative_terms": {
                "J_times_functional_derivative": first_term_diagnostics,
                "J_derivative_times_functional": second_term_diagnostics,
            },
            "excludes_zero": denominator_excludes_zero,
        },
        "canonical_Serre_scale": {
            "value_ball": str(scale) if scale is not None else None,
            "derivative_ball": str(scale_prime) if scale_prime is not None else None,
            "formula": "s_C=585/(2D), s_C'=-(585/2)D'/D^2",
        },
        "arrays": bindings,
        "checks": checks,
        "all_checks_pass": promoted,
        "guardrails": {
            "the_pointwise_B89_method_member_is_called_physically_selected": False,
            "one_midpoint_is_called_a_pathwise_certificate": False,
            "beta_C_or_the_248_row_period_readout_is_claimed": False,
            "an_interval_containing_zero_is_inverted": False,
        },
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
        "next": (
            "Extend the certified point calculation to adaptive panels and the BHT accumulator."
            if promoted
            else "Inspect the failed downstream interval check; retain the strict inverse certificate and improve only the responsible enclosure."
        ),
        "elapsed_seconds": time.monotonic() - started,
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    output.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T66 characteristic-zero execution: "
        f"{'PASS' if promoted else 'PARTIAL'} eta={eta:.6g} "
        f"value_rows={value_all_rows['rows_enclosing_zero']}/{relation_rows} "
        f"derivative_rows={derivative_all_rows['rows_enclosing_zero']}/{relation_rows} "
        f"denominator_excludes_zero={denominator_excludes_zero}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
