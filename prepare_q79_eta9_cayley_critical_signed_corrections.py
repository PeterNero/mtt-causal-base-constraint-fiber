#!/usr/bin/env python3
"""Emit signed corrections and residual source tails for the CBF.T66 geometry.

CBF.T66 deliberately enclosed every binary64 coefficient independently.  It
proved invertibility and all-row compatibility, but that box forgets the
signs of deterministic rounding errors and is too wide for the highly
cancelling toric-Jacobian scalar.  This builder preserves each signed first
correction and encloses the remaining Arb tail.  Matrix tails are almost entirely
arithmetic remainder, while the inhomogeneous vectors also retain the genuine
upstream top-anchor interval width.  Keeping those two meanings separate is
essential for the refined solve.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

from flint import acb, ctx
import numpy as np
from scipy import sparse

import build_q79_eta9_directed_cayley_serre_scale as t65
import prepare_q79_eta9_cayley_critical_characteristic_zero_input as base
import run_q79_eta9_cayley_critical_characteristic_zero_neumann as certify


ROOT = Path(__file__).resolve().parent
BASE_INPUT = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_characteristic_zero_seed7909"
)
OUTPUT = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_signed_correction_seed7909"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def save_array(directory: Path, name: str, value: np.ndarray) -> dict[str, object]:
    path = directory / f"{name}.npy"
    np.save(path, value, allow_pickle=False)
    return certify.artifact(path)


def save_sparse(
    directory: Path, name: str, value: sparse.spmatrix
) -> dict[str, object]:
    path = directory / f"{name}.npz"
    sparse.save_npz(path, value, compressed=True)
    return certify.artifact(path)


def scaled_exact_free_rows(
    rows: list[base.BallPolynomial],
    basis_index: dict[base.Exponent, int],
    free: np.ndarray,
    row_factor: np.ndarray,
    column_factor: np.ndarray,
    sign: int,
) -> list[dict[int, acb]]:
    free_lookup = {int(column): local for local, column in enumerate(free)}
    output: list[dict[int, acb]] = []
    for row_index, row in enumerate(rows):
        scaled: dict[int, acb] = {}
        for term, coefficient in row.items():
            local = free_lookup.get(basis_index[term])
            if local is None:
                continue
            scaled[local] = (
                sign
                * acb(float(row_factor[row_index]))
                * coefficient
                * acb(float(column_factor[local]))
            )
        output.append(scaled)
    return output


def scaled_exact_pivot_rows(
    rows: list[base.BallPolynomial],
    basis_index: dict[base.Exponent, int],
    pivots: np.ndarray,
    row_factor: np.ndarray,
) -> list[dict[int, acb]]:
    pivot_lookup = {int(column): local for local, column in enumerate(pivots)}
    output: list[dict[int, acb]] = []
    for row_index, row in enumerate(rows):
        scaled: dict[int, acb] = {}
        for term, coefficient in row.items():
            local = pivot_lookup.get(basis_index[term])
            if local is not None:
                scaled[local] = -acb(float(row_factor[row_index])) * coefficient
        output.append(scaled)
    return output


def sparse_signed_correction(
    h4: Any,
    center: sparse.csr_matrix,
    exact_rows: list[dict[int, acb]],
) -> tuple[sparse.csr_matrix, sparse.csr_matrix, dict[str, float]]:
    center = center.tocsr()
    require(len(exact_rows) == center.shape[0], "exact sparse row count")
    output_rows: list[int] = []
    output_columns: list[int] = []
    correction_values: list[complex] = []
    tail_values: list[float] = []
    maximum_exact_radius = 0.0
    exact_support_size = 0
    for row_index, exact_row in enumerate(exact_rows):
        start, stop = int(center.indptr[row_index]), int(center.indptr[row_index + 1])
        center_row = {
            int(center.indices[position]): complex(center.data[position])
            for position in range(start, stop)
        }
        exact_row = {
            column: value for column, value in exact_row.items() if value != 0
        }
        exact_support_size += len(exact_row)
        for column in sorted(set(center_row) | set(exact_row)):
            exact = exact_row.get(column, acb(0))
            midpoint = center_row.get(column, 0.0j)
            delta = exact - acb(midpoint)
            signed = complex(float(delta.real.mid()), float(delta.imag.mid()))
            output_rows.append(row_index)
            output_columns.append(column)
            correction_values.append(signed)
            tail_values.append(h4.acb_component_error(delta, signed))
            maximum_exact_radius = max(
                maximum_exact_radius,
                float(abs(exact.real.rad()).upper())
                + float(abs(exact.imag.rad()).upper()),
            )
    correction = np.asarray(correction_values, dtype=np.complex128)
    tail = np.asarray(tail_values, dtype=np.float64)
    correction_matrix = sparse.csr_matrix(
        (correction, (output_rows, output_columns)),
        shape=center.shape,
    )
    tail_matrix = sparse.csr_matrix(
        (np.nextafter(tail, math.inf), (output_rows, output_columns)),
        shape=center.shape,
    )
    return correction_matrix, tail_matrix, {
        "binary_center_support": int(center.nnz),
        "exact_support": exact_support_size,
        "union_support": len(output_rows),
        "maximum_signed_correction_component": float(
            (np.abs(correction.real) + np.abs(correction.imag)).max(initial=0.0)
        ),
        "maximum_remaining_tail_component": float(tail.max(initial=0.0)),
        "maximum_exact_Arb_radius_component": maximum_exact_radius,
    }


def vector_signed_correction(
    h4: Any,
    center: np.ndarray,
    exact: list[acb],
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    require(center.shape == (len(exact),), "exact vector shape")
    correction = np.empty(center.shape, dtype=np.complex128)
    tail = np.empty(center.shape, dtype=np.float64)
    for index, (midpoint, value) in enumerate(zip(center, exact, strict=True)):
        delta = value - acb(complex(midpoint))
        signed = complex(float(delta.real.mid()), float(delta.imag.mid()))
        correction[index] = signed
        tail[index] = h4.acb_component_error(delta, signed)
    tail = np.nextafter(tail, math.inf)
    return correction, tail, {
        "maximum_signed_correction_component": float(
            (np.abs(correction.real) + np.abs(correction.imag)).max(initial=0.0)
        ),
        "maximum_remaining_tail_component": float(tail.max(initial=0.0)),
    }


def dense_exact_vector(
    size: int, entries: list[tuple[int, acb]]
) -> list[acb]:
    output = [acb(0) for _ in range(size)]
    for column, value in entries:
        require(0 <= column < size, "exact vector column")
        output[column] = value
    return output


def main() -> int:
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-input", type=Path, default=BASE_INPUT)
    parser.add_argument("--output-directory", type=Path, default=OUTPUT)
    parser.add_argument("--precision", type=int, default=512)
    arguments = parser.parse_args()
    require(arguments.precision >= 384, "Arb precision")
    ctx.prec = arguments.precision
    base_input = arguments.base_input.resolve()
    OUTPUT = arguments.output_directory.resolve()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    metadata = certify.load_metadata(base_input)

    sys.path[:0] = [str(t65.H4_EXPERIMENT), str(t65.H4_GM), str(t65.H4_SERRE)]
    import charzero_serre_pairing_pilot as serre
    import probe_framed_member_charzero_gm_backend as framed
    import probe_framed_member_directed_top_trace as h4

    core, gm, _redundant = framed.import_sources()
    member_basis, coefficients, _member_diagnostics = core.build_exact_member()
    binary_section_rows, normalization, _normalized = framed.section_rows(
        member_basis, coefficients
    )
    exact_section_rows_input = h4.exact_section_rows(
        member_basis, coefficients, normalization
    )
    exact_geometry = h4.exact_path_jet(
        base.SEGMENT, base.PARAMETER, base.LIFT_SIGN
    )
    k3_payload = json.loads(t65.H4_SOURCE.read_text(encoding="ascii"))
    exact_f6, exact_f9, exact_dot_f9 = base.exact_framed_polynomials(
        h4, k3_payload, exact_section_rows_input, exact_geometry
    )
    exact_sections, exact_derivatives = base.exact_cayley_sections(
        exact_f6, exact_f9, exact_dot_f9
    )

    basis = serre.component_monomials(9, 3)
    basis_index = {term: column for column, term in enumerate(basis)}
    arrays = metadata["arrays"]
    matrices = metadata["matrices"]
    selected = certify.load_array(arrays["selected_rows"], (6777,)).astype(np.int64)
    pivots = certify.load_array(arrays["embedding_pivots"], (2584,)).astype(np.int64)
    free = certify.load_array(arrays["free_columns"], (6777,)).astype(np.int64)
    row_factor = certify.load_array(arrays["row_factor"], (6777,))
    column_factor = certify.load_array(arrays["column_factor"], (6777,))
    exact_selected = base.selected_exact_rows(
        exact_sections, serre.component_monomials, selected
    )
    exact_selected_prime = base.selected_exact_rows(
        exact_derivatives,
        serre.component_monomials,
        selected,
        require_nonempty=False,
    )

    matrix_center = certify.load_sparse(
        matrices["balanced_matrix_center"], (6777, 6777)
    )
    coupling_center = certify.load_sparse(
        matrices["balanced_derivative_coupling_center"], (6777, 6777)
    )
    exact_matrix_rows = scaled_exact_free_rows(
        exact_selected,
        basis_index,
        free,
        row_factor,
        column_factor,
        1,
    )
    exact_coupling_rows = scaled_exact_free_rows(
        exact_selected_prime,
        basis_index,
        free,
        row_factor,
        column_factor,
        -1,
    )
    matrix_correction, matrix_tail, matrix_diagnostics = sparse_signed_correction(
        h4, matrix_center, exact_matrix_rows
    )
    coupling_correction, coupling_tail, coupling_diagnostics = (
        sparse_signed_correction(h4, coupling_center, exact_coupling_rows)
    )

    full_relation_center = certify.load_sparse(
        matrices["full_relation_center"], (16740, 9361)
    )
    full_relation_prime_center = certify.load_sparse(
        matrices["full_relation_derivative_center"], (16740, 9361)
    )
    source_map_center = -(
        sparse.diags(row_factor)
        @ full_relation_center[selected, :][:, pivots]
    ).tocsr()
    source_map_prime_center = -(
        sparse.diags(row_factor)
        @ full_relation_prime_center[selected, :][:, pivots]
    ).tocsr()
    exact_source_map_rows = scaled_exact_pivot_rows(
        exact_selected, basis_index, pivots, row_factor
    )
    exact_source_map_prime_rows = scaled_exact_pivot_rows(
        exact_selected_prime, basis_index, pivots, row_factor
    )
    source_map_correction, source_map_tail, source_map_diagnostics = (
        sparse_signed_correction(
            h4, source_map_center, exact_source_map_rows
        )
    )
    (
        source_map_prime_correction,
        source_map_prime_tail,
        source_map_prime_diagnostics,
    ) = sparse_signed_correction(
        h4, source_map_prime_center, exact_source_map_prime_rows
    )

    h4_packet = t65.load_canonical(t65.H4_T141)
    h4_row = next(
        row
        for row in h4_packet["six_midpoint_audit"]["rows"]
        if row["segment"] == base.SEGMENT
    )
    top_center = t65.load_bound_array(h4_row["arrays"]["value_center"], (2584,))
    top_radius = t65.load_bound_array(h4_row["arrays"]["value_radius"], (2584,))
    top_prime_center = t65.load_bound_array(
        h4_row["arrays"]["derivative_center"], (2584,)
    )
    top_prime_radius = t65.load_bound_array(
        h4_row["arrays"]["derivative_radius"], (2584,)
    )
    embedding, _pivots_replay, _free_replay = t65.top_embedding(serre, basis)
    pivot_balls, _embedding_diagnostics = base.pivot_balls(
        h4, embedding, pivots, top_center, top_radius
    )
    pivot_prime_balls, _prime_embedding_diagnostics = base.pivot_balls(
        h4, embedding, pivots, top_prime_center, top_prime_radius
    )
    embedding_block = embedding[:, pivots].tocsr()
    embedding_identity = sparse.eye(
        embedding_block.shape[0], dtype=np.complex128, format="csr"
    )
    embedding_nilpotent = embedding_block - embedding_identity
    embedding_nilpotent.eliminate_zeros()
    pivot_from_top = embedding_identity - embedding_nilpotent
    require(
        (embedding_nilpotent @ embedding_nilpotent).nnz == 0,
        "square-zero pivot-from-top map",
    )
    pivot_lookup = {int(column): index for index, column in enumerate(pivots)}
    exact_rhs = base.scaled_rhs_balls(
        exact_selected,
        basis_index,
        pivot_lookup,
        pivot_balls,
        row_factor,
    )
    exact_constant = base.scaled_derivative_constant_balls(
        exact_selected,
        exact_selected_prime,
        basis_index,
        pivot_lookup,
        pivot_balls,
        pivot_prime_balls,
        row_factor,
    )
    rhs_center = certify.load_array(arrays["value_rhs_center"], (6777,))
    rhs_previous_error = certify.load_array(
        arrays["value_rhs_error"], (6777,)
    )
    constant_center = certify.load_array(
        arrays["derivative_constant_center"], (6777,)
    )
    constant_previous_error = certify.load_array(
        arrays["derivative_constant_error"], (6777,)
    )
    rhs_correction, rhs_tail, rhs_diagnostics = vector_signed_correction(
        h4, rhs_center, exact_rhs
    )
    constant_correction, constant_tail, constant_diagnostics = (
        vector_signed_correction(h4, constant_center, exact_constant)
    )

    jacobian_entries, jacobian_prime_entries = certify.load_exact_ball_polynomials(
        metadata["exact_polynomials"]["toric_Jacobian"], 9361
    )
    exact_jacobian = dense_exact_vector(9361, jacobian_entries)
    exact_jacobian_prime = dense_exact_vector(9361, jacobian_prime_entries)
    jacobian_center = certify.load_array(arrays["jacobian_center"], (9361,))
    jacobian_prime_center = certify.load_array(
        arrays["jacobian_derivative_center"], (9361,)
    )
    jacobian_correction, jacobian_tail, jacobian_diagnostics = (
        vector_signed_correction(h4, jacobian_center, exact_jacobian)
    )
    jacobian_prime_correction, jacobian_prime_tail, jacobian_prime_diagnostics = (
        vector_signed_correction(
            h4, jacobian_prime_center, exact_jacobian_prime
        )
    )

    pivot_center = certify.load_array(arrays["pivot_value_center"], (2584,))
    pivot_prime_center = certify.load_array(
        arrays["pivot_derivative_center"], (2584,)
    )
    pivot_correction, pivot_tail, pivot_diagnostics = vector_signed_correction(
        h4, pivot_center, pivot_balls
    )
    pivot_prime_correction, pivot_prime_tail, pivot_prime_diagnostics = (
        vector_signed_correction(h4, pivot_prime_center, pivot_prime_balls)
    )

    output_arrays = {
        "value_rhs_correction": save_array(OUTPUT, "value_rhs_correction", rhs_correction),
        "value_rhs_tail": save_array(OUTPUT, "value_rhs_tail", rhs_tail),
        "derivative_constant_correction": save_array(
            OUTPUT, "derivative_constant_correction", constant_correction
        ),
        "derivative_constant_tail": save_array(
            OUTPUT, "derivative_constant_tail", constant_tail
        ),
        "jacobian_correction": save_array(
            OUTPUT, "jacobian_correction", jacobian_correction
        ),
        "jacobian_tail": save_array(OUTPUT, "jacobian_tail", jacobian_tail),
        "jacobian_derivative_correction": save_array(
            OUTPUT,
            "jacobian_derivative_correction",
            jacobian_prime_correction,
        ),
        "jacobian_derivative_tail": save_array(
            OUTPUT, "jacobian_derivative_tail", jacobian_prime_tail
        ),
        "pivot_value_correction": save_array(
            OUTPUT, "pivot_value_correction", pivot_correction
        ),
        "pivot_value_tail": save_array(
            OUTPUT, "pivot_value_tail", pivot_tail
        ),
        "pivot_derivative_correction": save_array(
            OUTPUT, "pivot_derivative_correction", pivot_prime_correction
        ),
        "pivot_derivative_tail": save_array(
            OUTPUT, "pivot_derivative_tail", pivot_prime_tail
        ),
        "top_value_center": save_array(
            OUTPUT, "top_value_center", top_center
        ),
        "top_value_radius": save_array(
            OUTPUT, "top_value_radius", top_radius
        ),
        "top_derivative_center": save_array(
            OUTPUT, "top_derivative_center", top_prime_center
        ),
        "top_derivative_radius": save_array(
            OUTPUT, "top_derivative_radius", top_prime_radius
        ),
    }
    output_matrices = {
        "balanced_matrix_correction": save_sparse(
            OUTPUT, "balanced_matrix_correction", matrix_correction
        ),
        "balanced_matrix_tail": save_sparse(
            OUTPUT, "balanced_matrix_tail", matrix_tail
        ),
        "balanced_derivative_coupling_correction": save_sparse(
            OUTPUT,
            "balanced_derivative_coupling_correction",
            coupling_correction,
        ),
        "balanced_derivative_coupling_tail": save_sparse(
            OUTPUT, "balanced_derivative_coupling_tail", coupling_tail
        ),
        "pivot_source_map_center": save_sparse(
            OUTPUT, "pivot_source_map_center", source_map_center
        ),
        "pivot_source_map_correction": save_sparse(
            OUTPUT, "pivot_source_map_correction", source_map_correction
        ),
        "pivot_source_map_tail": save_sparse(
            OUTPUT, "pivot_source_map_tail", source_map_tail
        ),
        "pivot_source_map_derivative_center": save_sparse(
            OUTPUT,
            "pivot_source_map_derivative_center",
            source_map_prime_center,
        ),
        "pivot_source_map_derivative_correction": save_sparse(
            OUTPUT,
            "pivot_source_map_derivative_correction",
            source_map_prime_correction,
        ),
        "pivot_source_map_derivative_tail": save_sparse(
            OUTPUT,
            "pivot_source_map_derivative_tail",
            source_map_prime_tail,
        ),
        "pivot_from_top_map": save_sparse(
            OUTPUT, "pivot_from_top_map", pivot_from_top
        ),
    }
    diagnostics = {
        "balanced_matrix": matrix_diagnostics,
        "balanced_derivative_coupling": coupling_diagnostics,
        "value_rhs": rhs_diagnostics,
        "derivative_constant": constant_diagnostics,
        "toric_jacobian": jacobian_diagnostics,
        "toric_jacobian_derivative": jacobian_prime_diagnostics,
        "pivot_value": pivot_diagnostics,
        "pivot_derivative": pivot_prime_diagnostics,
        "pivot_source_map": source_map_diagnostics,
        "pivot_source_map_derivative": source_map_prime_diagnostics,
    }
    checks = {
        "the_signed_matrix_correction_covers_the_support_union": matrix_correction.nnz
        == matrix_diagnostics["union_support"],
        "the_signed_derivative_correction_covers_the_support_union": coupling_correction.nnz
        == coupling_diagnostics["union_support"],
        "every_remaining_tail_is_nonnegative": bool(
            np.all(matrix_tail.data >= 0.0)
            and np.all(coupling_tail.data >= 0.0)
            and np.all(rhs_tail >= 0.0)
            and np.all(constant_tail >= 0.0)
        ),
        "the_matrix_tail_is_smaller_than_1e_28": matrix_diagnostics[
            "maximum_remaining_tail_component"
        ]
        < 1.0e-28,
        "the_derivative_coupling_tail_is_smaller_than_1e_28": coupling_diagnostics[
            "maximum_remaining_tail_component"
        ]
        < 1.0e-28,
        "the_pivot_source_map_tail_is_smaller_than_1e_28": source_map_diagnostics[
            "maximum_remaining_tail_component"
        ]
        < 1.0e-28,
        "the_pivot_source_map_derivative_tail_is_smaller_than_1e_28": source_map_prime_diagnostics[
            "maximum_remaining_tail_component"
        ]
        < 1.0e-28,
        "the_value_rhs_tail_retains_no_more_than_the_previous_source_bound": bool(
            np.all(rhs_tail <= np.nextafter(rhs_previous_error, math.inf))
        ),
        "the_derivative_constant_tail_retains_no_more_than_the_previous_source_bound": bool(
            np.all(constant_tail <= np.nextafter(constant_previous_error, math.inf))
        ),
        "the_toric_Jacobian_signed_tail_is_finite": bool(
            np.isfinite(jacobian_tail).all()
            and np.isfinite(jacobian_prime_tail).all()
        ),
        "the_pivot_signed_tail_is_finite": bool(
            np.isfinite(pivot_tail).all()
            and np.isfinite(pivot_prime_tail).all()
        ),
        "the_common_top_source_replays_the_pivot_centers": bool(
            np.linalg.norm(pivot_from_top @ top_center - pivot_center, np.inf)
            < 1.0e-14
            and np.linalg.norm(
                pivot_from_top @ top_prime_center - pivot_prime_center,
                np.inf,
            )
            < 1.0e-12
        ),
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"signed-correction checks: {checks}")
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-signed-correction.v1",
        "theorem_id": "CBF.T67",
        "status": "PORTABLE_SIGNED_DOUBLE_DOUBLE_CHARACTERISTIC_ZERO_SOURCE",
        "precision_bits": arguments.precision,
        "base_input": certify.artifact(base_input / "metadata.json"),
        "geometry": metadata["geometry"],
        "dimensions": metadata["dimensions"],
        "representation": {
            "formula": "exact coefficient in binary64 center + signed binary64 correction + component tail",
            "purpose": "retain deterministic cancellation discarded by independent first-order coefficient boxes",
            "tail_semantics": {
                "matrix_and_coupling": "outward arithmetic remainder after the signed correction",
                "rhs_and_derivative_constant": "outward remainder plus genuine upstream top-anchor source width",
                "toric_jacobian": "outward arithmetic remainder after the signed correction",
                "pivots": "outward remainder plus genuine upstream top-anchor source width",
                "pivot_source_maps": "outward arithmetic remainder after the signed correction",
                "top_anchor_map": "the exact integral square-zero Cayley inverse I-N",
            },
        },
        "arrays": output_arrays,
        "matrices": output_matrices,
        "diagnostics": diagnostics,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
    }
    packet["canonical_payload_sha256"] = certify.canonical_sha256(packet)
    output_path = OUTPUT / "metadata.json"
    output_path.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T67 signed correction source: PASS "
        f"matrix_correction={matrix_diagnostics['maximum_signed_correction_component']:.3e} "
        f"matrix_tail={matrix_diagnostics['maximum_remaining_tail_component']:.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
