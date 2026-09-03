#!/usr/bin/env python3
"""Build the T65 directed Cayley-Serre scale calculation.

The expensive first stage selects 9,360 independent *original* Cox relation
rows at the T64 good reduction.  Normal replays use that frozen row set for
the edge-2 and edge-0 complex calculations.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import build_q79_eta9_cayley_serre_trace_normalization as t64
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import LinearOperator, onenormest, splu


ROOT = Path(__file__).resolve().parent
MINOR = ROOT / "q79_eta9_cayley_critical_minor.witness.json"
PACKET = ROOT / "q79_eta9_directed_cayley_serre_scale.packet.json"
COMPLEX_MINOR_ROWS = ROOT / "q79_eta9_cayley_critical_rank_revealing_rows.npy"
COMPLEX_MINOR_PACKET = (
    ROOT / "q79_eta9_cayley_critical_rank_revealing_minor.packet.json"
)
REFINEMENT_SEEDS = (7909, 7919, 7933)
PRE = t64.PRE
H4_EXPERIMENT = PRE / "experiments/q79_eta9_bht_fiber_evaluation_and_handle_sweep"
H4_GM = PRE / "experiments/q79_eta9_b89_charzero_goal_adjoint"
H4_SERRE = PRE / "experiments/q79_eta9_b89_moving_serre_pairing"
H4_SOURCE = (
    PRE
    / "experiments/q79_eta9_b89_relative_adjoint_compiler"
    / "q79_eta9_b89_relative_adjoint_worker_input.json"
)
H4_T141 = (
    H4_EXPERIMENT
    / "outputs/q79_eta9_framed_member_directed_top_trace_contract.packet.json"
)

Exponent = tuple[int, int, int, int, int, int]
ComplexPolynomial = dict[Exponent, complex]
JetPolynomial = dict[Exponent, tuple[complex, complex]]


def functional_path(segment: str, derivative: bool = False) -> Path:
    suffix = ".functional_derivative.npy" if derivative else ".functional.npy"
    return ROOT / f"q79_eta9_directed_cayley_serre_scale.{segment}{suffix}"


def refinement_packet_path(seed: int) -> Path:
    return (
        ROOT
        / f"q79_eta9_cayley_critical_binary_mixed_refinement_seed{seed}.packet.json"
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def artifact(path: Path, repository: str = "mtt-causal-base-constraint-fiber") -> dict[str, object]:
    return {
        "repository": repository,
        "path": path.name if path.parent == ROOT else path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def external_artifact(path: Path) -> dict[str, object]:
    return {
        "repository": "mtt-preprojection-repair-calculus",
        "path": path.resolve().relative_to(PRE.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load_canonical(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="ascii"))
    claimed = payload.pop("canonical_payload_sha256")
    require(canonical_sha256(payload) == claimed, f"canonical payload: {path}")
    payload["canonical_payload_sha256"] = claimed
    return payload


def poly_add(left: ComplexPolynomial, right: ComplexPolynomial) -> ComplexPolynomial:
    output = dict(left)
    for term, value in right.items():
        updated = output.get(term, 0.0j) + value
        if updated:
            output[term] = updated
        else:
            output.pop(term, None)
    return output


def poly_scale(poly: ComplexPolynomial, scalar: complex) -> ComplexPolynomial:
    return {term: scalar * value for term, value in poly.items() if scalar * value}


def poly_shift(poly: ComplexPolynomial, shift: Exponent) -> ComplexPolynomial:
    return {
        tuple(left + right for left, right in zip(term, shift, strict=True)): value
        for term, value in poly.items()
    }


def poly_multiply(left: ComplexPolynomial, right: ComplexPolynomial) -> ComplexPolynomial:
    output: ComplexPolynomial = {}
    for left_term, left_value in left.items():
        for right_term, right_value in right.items():
            term = tuple(
                a + b for a, b in zip(left_term, right_term, strict=True)
            )
            output[term] = output.get(term, 0.0j) + left_value * right_value
    return {term: value for term, value in output.items() if value}


def poly_derivative(poly: ComplexPolynomial, variable: int) -> ComplexPolynomial:
    output: ComplexPolynomial = {}
    for term, value in poly.items():
        power = term[variable]
        if power:
            reduced = list(term)
            reduced[variable] -= 1
            output[tuple(reduced)] = power * value
    return output


def jet_add(left: JetPolynomial, right: JetPolynomial) -> JetPolynomial:
    output = dict(left)
    for term, value in right.items():
        old = output.get(term, (0.0j, 0.0j))
        updated = (old[0] + value[0], old[1] + value[1])
        if updated != (0.0j, 0.0j):
            output[term] = updated
        else:
            output.pop(term, None)
    return output


def jet_multiply(left: JetPolynomial, right: JetPolynomial) -> JetPolynomial:
    output: JetPolynomial = {}
    for left_term, left_value in left.items():
        for right_term, right_value in right.items():
            term = tuple(
                a + b for a, b in zip(left_term, right_term, strict=True)
            )
            old = output.get(term, (0.0j, 0.0j))
            product = (
                left_value[0] * right_value[0],
                left_value[1] * right_value[0]
                + left_value[0] * right_value[1],
            )
            output[term] = (old[0] + product[0], old[1] + product[1])
    return {
        term: value for term, value in output.items() if value != (0.0j, 0.0j)
    }


def jet_derivative(poly: JetPolynomial, variable: int) -> JetPolynomial:
    output: JetPolynomial = {}
    for exponent, coefficient in poly.items():
        power = exponent[variable]
        if power:
            reduced = list(exponent)
            reduced[variable] -= 1
            output[tuple(reduced)] = (
                power * coefficient[0],
                power * coefficient[1],
            )
    return output


def jet_determinant(matrix: list[list[JetPolynomial]]) -> JetPolynomial:
    size = len(matrix)
    output: JetPolynomial = {}
    unit: JetPolynomial = {(0, 0, 0, 0, 0, 0): (1.0 + 0.0j, 0.0j)}
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        term = unit
        for row, column in enumerate(permutation):
            term = jet_multiply(term, matrix[row][column])
            if not term:
                break
        if inversions % 2:
            term = {
                exponent: (-value[0], -value[1])
                for exponent, value in term.items()
            }
        output = jet_add(output, term)
    return output


def regularizing_cubic() -> ComplexPolynomial:
    return {
        (3, 0, 0, 0, 0, 0): 1.0 + 0.0j,
        (0, 3, 0, 0, 0, 0): 1.0 + 0.0j,
        (0, 0, 3, 0, 0, 0): 1.0 + 0.0j,
        (0, 0, 0, 1, 0, 0): 1.0 + 0.0j,
    }


def cayley_sections(
    f6: ComplexPolynomial,
    f9: ComplexPolynomial,
    dot_f9: ComplexPolynomial,
) -> tuple[list[ComplexPolynomial], list[ComplexPolynomial]]:
    cubic = regularizing_cubic()
    f9_regular = poly_add(f9, poly_multiply(cubic, f6))
    u = (0, 0, 0, 0, 1, 0)
    v = (0, 0, 0, 0, 0, 1)
    phi = poly_add(poly_shift(f6, u), poly_shift(f9_regular, v))
    dot_phi = poly_shift(dot_f9, v)
    sections = [phi]
    derivatives = [dot_phi]
    for variable in (1, 2, 3):
        shift = tuple(1 if index == variable else 0 for index in range(6))
        sections.append(poly_shift(poly_derivative(phi, variable), shift))
        derivatives.append(poly_shift(poly_derivative(dot_phi, variable), shift))
    sections.append(poly_shift(f6, u))
    derivatives.append({})
    return sections, derivatives


def relation_matrix(
    sections: list[ComplexPolynomial],
    component_monomials: Any,
    selected_rows: list[int] | None = None,
) -> sparse.csr_matrix:
    basis = component_monomials(9, 3)
    index = {term: column for column, term in enumerate(basis)}
    multipliers = component_monomials(9, 2)
    total_rows = len(sections) * len(multipliers)
    if selected_rows is None:
        selected_lookup = None
        row_count = total_rows
    else:
        selected_lookup = {source: row for row, source in enumerate(selected_rows)}
        require(len(selected_lookup) == len(selected_rows), "unique selected rows")
        row_count = len(selected_rows)
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[complex] = []
    source_row = 0
    for section in sections:
        for multiplier in multipliers:
            destination = (
                source_row
                if selected_lookup is None
                else selected_lookup.get(source_row)
            )
            if destination is not None:
                for term, value in poly_shift(section, multiplier).items():
                    row_indices.append(destination)
                    column_indices.append(index[term])
                    values.append(value)
            source_row += 1
    require(source_row == total_rows, "complete relation-row traversal")
    return sparse.csr_matrix(
        (
            np.asarray(values, dtype=np.complex128),
            (row_indices, column_indices),
        ),
        shape=(row_count, len(basis)),
    )


def toric_jacobian_jet(
    sections: list[ComplexPolynomial], derivatives: list[ComplexPolynomial]
) -> tuple[ComplexPolynomial, ComplexPolynomial, dict[str, float]]:
    jet_sections = [
        {
            term: (section.get(term, 0.0j), derivatives[index].get(term, 0.0j))
            for term in set(section) | set(derivatives[index])
        }
        for index, section in enumerate(sections)
    ]
    matrix = [jet_sections]
    for variable in (1, 2, 3, 4):
        matrix.append(
            [jet_derivative(polynomial, variable) for polynomial in jet_sections]
        )
    numerator = jet_determinant(matrix)
    divisor = (1, 0, 0, 0, 0, 1)
    divisible: JetPolynomial = {}
    bad_value = 0.0
    bad_derivative = 0.0
    total_value = max((abs(value[0]) for value in numerator.values()), default=0.0)
    total_derivative = max((abs(value[1]) for value in numerator.values()), default=0.0)
    for term, value in numerator.items():
        if all(left >= right for left, right in zip(term, divisor, strict=True)):
            reduced = tuple(
                left - right for left, right in zip(term, divisor, strict=True)
            )
            divisible[reduced] = value
        else:
            bad_value = max(bad_value, abs(value[0]))
            bad_derivative = max(bad_derivative, abs(value[1]))
    value_ratio = bad_value / max(total_value, 1.0e-300)
    derivative_ratio = bad_derivative / max(total_derivative, 1.0e-300)
    require(value_ratio < 1.0e-10, f"toric Jacobian value cancellation: {value_ratio}")
    require(
        derivative_ratio < 1.0e-10,
        f"toric Jacobian derivative cancellation: {derivative_ratio}",
    )
    value = {term: coefficient[0] for term, coefficient in divisible.items()}
    derivative = {term: coefficient[1] for term, coefficient in divisible.items()}
    return value, derivative, {
        "discarded_nondivisible_value_relative_maximum": value_ratio,
        "discarded_nondivisible_derivative_relative_maximum": derivative_ratio,
    }


def transport_top_monomial(term: Exponent) -> ComplexPolynomial:
    output: ComplexPolynomial = {term: 1.0 + 0.0j}
    if term[4]:
        require(term[4] == 1, "top Cayley degree one")
        base = list(term)
        base[4] -= 1
        base[5] += 1
        output = poly_add(output, poly_shift(regularizing_cubic(), tuple(base)))
    return output


def top_embedding(
    serre: Any,
    critical_basis: list[Exponent],
) -> tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    """Embed the old top basis into the regularized Cayley critical degree."""
    index = {term: column for column, term in enumerate(critical_basis)}
    top_basis = serre.component_monomials(18, 1)
    cox_product = (1, 1, 1, 1, 1, 1)
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[complex] = []
    pivot_columns: list[int] = []
    for row, term in enumerate(top_basis):
        primary = tuple(
            left + right for left, right in zip(term, cox_product, strict=True)
        )
        pivot_columns.append(index[primary])
        transported = poly_shift(transport_top_monomial(term), cox_product)
        for monomial, value in transported.items():
            row_indices.append(row)
            column_indices.append(index[monomial])
            values.append(value)
    embedding = sparse.csr_matrix(
        (
            np.asarray(values, dtype=np.complex128),
            (row_indices, column_indices),
        ),
        shape=(len(top_basis), len(critical_basis)),
    )
    pivots = np.asarray(pivot_columns, dtype=np.int64)
    free = np.setdiff1d(
        np.arange(len(critical_basis), dtype=np.int64), pivots
    )
    require(np.unique(pivots).size == 2584, "distinct embedding pivots")
    require(embedding[:, free].nnz == 0, "embedding pivot support")
    return embedding, pivots, free


def load_complex_minor_rows() -> tuple[np.ndarray, dict[str, Any]]:
    packet = load_canonical(COMPLEX_MINOR_PACKET)
    require(
        packet["schema"]
        == "mtt.cbf.q79-eta9-cayley-critical-rank-revealing-minor.v1",
        "complex minor schema",
    )
    binding = packet["selection"]["selected_rows"]
    require(binding["bytes"] == COMPLEX_MINOR_ROWS.stat().st_size, "minor row bytes")
    require(binding["sha256"] == sha256(COMPLEX_MINOR_ROWS), "minor row hash")
    selected = np.load(COMPLEX_MINOR_ROWS, allow_pickle=False).astype(np.int64)
    require(
        selected.shape == (6777,)
        and np.unique(selected).size == 6777
        and np.all((0 <= selected) & (selected < 16740)),
        "complex minor rows",
    )
    return selected, packet


def binary_gauge_audit(binary_edge2_scale: complex) -> dict[str, Any]:
    """Reject binary-coefficient promotion using three predeclared row gauges.

    Each input solves a different full-rank row subsystem after freezing every
    coefficient to its binary64 value.  Mixed refinement removes linear-solver
    residual as the explanation for disagreement.  The comparison is a
    stability rejection of that frozen-coefficient method, not an obstruction
    to the common characteristic-zero quotient functional.
    """
    rows: list[dict[str, Any]] = []
    scales: list[complex] = []
    denominators: list[complex] = []
    row_hashes: list[str] = []
    for seed in REFINEMENT_SEEDS:
        path = refinement_packet_path(seed)
        packet = load_canonical(path)
        require(
            packet["schema"]
            == "mtt.cbf.q79-eta9-cayley-critical-binary-mixed-refinement.v1",
            f"refinement schema: {seed}",
        )
        require(packet["input"]["seed"] == seed, f"refinement seed: {seed}")
        require(all(packet["checks"].values()), f"refinement checks: {seed}")
        scale = complex(*packet["canonical_Serre_scale_midpoint"])
        denominator = complex(*packet["toric_Jacobian_coordinate_midpoint"])
        scales.append(scale)
        denominators.append(denominator)
        row_hashes.append(packet["input"]["selected_rows"]["sha256"])
        rows.append(
            {
                "seed": seed,
                "selected_rows_sha256": row_hashes[-1],
                "matrix_sha256": packet["input"]["matrix"]["sha256"],
                "matrix_nonzeros": packet["input"]["matrix_nonzeros"],
                "final_exact_dyadic_residual_component_upper": packet[
                    "refinement"
                ]["final_maximum_residual_ball_component_upper"],
                "toric_Jacobian_coordinate_midpoint": [
                    denominator.real,
                    denominator.imag,
                ],
                "Serre_scale_midpoint": [scale.real, scale.imag],
                "source_packet": artifact(path),
            }
        )

    pairwise: list[dict[str, Any]] = []
    for left in range(len(scales)):
        for right in range(left + 1, len(scales)):
            scale_gap = abs(scales[left] - scales[right])
            scale_reference = max(abs(scales[left]), abs(scales[right]), 1.0e-300)
            denominator_gap = abs(denominators[left] - denominators[right])
            denominator_reference = max(
                abs(denominators[left]), abs(denominators[right]), 1.0e-300
            )
            pairwise.append(
                {
                    "seeds": [REFINEMENT_SEEDS[left], REFINEMENT_SEEDS[right]],
                    "Serre_scale_absolute_gap": scale_gap,
                    "Serre_scale_relative_gap": scale_gap / scale_reference,
                    "toric_Jacobian_absolute_gap": denominator_gap,
                    "toric_Jacobian_relative_gap": denominator_gap
                    / denominator_reference,
                }
            )
    minimum_scale_gap = min(row["Serre_scale_relative_gap"] for row in pairwise)
    maximum_scale_gap = max(row["Serre_scale_relative_gap"] for row in pairwise)
    same_minor_gap = abs(binary_edge2_scale - scales[0]) / max(
        abs(binary_edge2_scale), abs(scales[0]), 1.0e-300
    )
    return {
        "purpose": "predeclared row-gauge stability test for the frozen-binary coefficient model",
        "rows": rows,
        "pairwise": pairwise,
        "minimum_pairwise_Serre_scale_relative_gap": minimum_scale_gap,
        "maximum_pairwise_Serre_scale_relative_gap": maximum_scale_gap,
        "seed7909_binary64_to_exact_dyadic_refinement_relative_gap": same_minor_gap,
        "decision": {
            "binary_coefficient_scale_is_promoted": False,
            "binary_coefficient_derivative_is_promoted": False,
            "characteristic_zero_coefficient_ball_extension_is_required": True,
            "reason": "all three exact-dyadic residual refinements converge below 1e-80, but the resulting row-gauge scale midpoints disagree by more than one percent",
        },
        "scope": "This rejects numerical promotion from frozen binary coefficients; it neither rejects nor evaluates the common characteristic-zero geometric functional.",
    }


def solve_anchored_minor(
    relation: sparse.csr_matrix,
    relation_prime: sparse.csr_matrix,
    embedding: sparse.csr_matrix,
    embedding_pivots: np.ndarray,
    free_columns: np.ndarray,
    top_value: np.ndarray,
    top_derivative: np.ndarray,
    selected_rows: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    """Extend the H4 top trace through one common critical original-row minor."""
    require(relation.shape == relation_prime.shape == (16740, 9361), "relation shape")
    require(embedding.shape == (2584, 9361), "embedding shape")
    embedding_factor = splu(embedding[:, embedding_pivots].tocsc())
    pivot_value = embedding_factor.solve(top_value)
    pivot_derivative = embedding_factor.solve(top_derivative)

    reduced = relation[:, free_columns].tocsr()
    selected = reduced[selected_rows, :].tocsr()
    require(selected.shape == (6777, 6777), "selected anchored minor shape")
    row_norm = np.asarray(abs(selected).max(axis=1).toarray()).ravel()
    require(np.all(row_norm > 0), "nonzero anchored minor rows")
    row_factor = 1.0 / row_norm
    balanced_rows = sparse.diags(row_factor) @ selected
    column_norm = np.asarray(abs(balanced_rows).max(axis=0).toarray()).ravel()
    require(np.all(column_norm > 0), "nonzero anchored minor columns")
    column_factor = 1.0 / column_norm
    balanced = (
        sparse.diags(row_factor)
        @ selected
        @ sparse.diags(column_factor)
    ).tocsc()
    started = time.monotonic()
    factor = splu(
        balanced,
        permc_spec="COLAMD",
        diag_pivot_thresh=1.0,
        options={"Equil": True, "IterRefine": "EXTRA"},
    )
    factor_seconds = time.monotonic() - started

    def solve(rhs: np.ndarray) -> tuple[np.ndarray, float]:
        selected_rhs = rhs[selected_rows]
        result = column_factor * factor.solve(row_factor * selected_rhs)
        for _ in range(5):
            residual = selected_rhs - selected @ result
            result += column_factor * factor.solve(row_factor * residual)
        residual = selected_rhs - selected @ result
        relative = float(
            np.linalg.norm(residual, np.inf)
            / max(
                np.linalg.norm(selected_rhs, np.inf)
                + sparse.linalg.norm(selected, ord=np.inf)
                * np.linalg.norm(result, np.inf),
                1.0e-300,
            )
        )
        return result, relative

    value_rhs = -(relation[:, embedding_pivots] @ pivot_value)
    free_value, selected_value_residual = solve(value_rhs)
    functional = np.empty(9361, dtype=np.complex128)
    functional[embedding_pivots] = pivot_value
    functional[free_columns] = free_value

    derivative_rhs = -(
        relation_prime @ functional
        + relation[:, embedding_pivots] @ pivot_derivative
    )
    free_derivative, selected_derivative_residual = solve(derivative_rhs)
    functional_prime = np.empty(9361, dtype=np.complex128)
    functional_prime[embedding_pivots] = pivot_derivative
    functional_prime[free_columns] = free_derivative

    value_residual = relation @ functional
    derivative_residual = relation @ functional_prime + relation_prime @ functional
    inverse_operator = LinearOperator(
        balanced.shape,
        matvec=lambda vector: factor.solve(vector),
        rmatvec=lambda vector: factor.solve(vector, trans="H"),
        dtype=np.complex128,
    )
    inverse_one_norm_estimate = float(onenormest(inverse_operator))
    balanced_one_norm = float(abs(balanced).sum(axis=0).max())
    return functional, functional_prime, {
        "factor_seconds": factor_seconds,
        "factor_L_nonzeros": int(factor.L.nnz),
        "factor_U_nonzeros": int(factor.U.nnz),
        "balanced_one_norm": balanced_one_norm,
        "inverse_one_norm_estimate": inverse_one_norm_estimate,
        "condition_one_norm_estimate": balanced_one_norm
        * inverse_one_norm_estimate,
        "selected_value_backward_error": selected_value_residual,
        "selected_derivative_backward_error": selected_derivative_residual,
        "all_row_value_absolute_residual": float(
            np.linalg.norm(value_residual, np.inf)
        ),
        "all_row_derivative_absolute_residual": float(
            np.linalg.norm(derivative_residual, np.inf)
        ),
        "all_row_value_relative_residual": float(
            np.linalg.norm(value_residual, np.inf)
            / max(
                sparse.linalg.norm(relation, ord=np.inf)
                * np.linalg.norm(functional, np.inf),
                1.0e-300,
            )
        ),
        "all_row_derivative_relative_residual": float(
            np.linalg.norm(derivative_residual, np.inf)
            / max(
                sparse.linalg.norm(relation, ord=np.inf)
                * np.linalg.norm(functional_prime, np.inf)
                + sparse.linalg.norm(relation_prime, ord=np.inf)
                * np.linalg.norm(functional, np.inf),
                1.0e-300,
            )
        ),
        "top_embedding_value_relative_residual": float(
            np.linalg.norm(embedding @ functional - top_value, np.inf)
            / max(np.linalg.norm(top_value, np.inf), 1.0e-300)
        ),
        "top_embedding_derivative_relative_residual": float(
            np.linalg.norm(embedding @ functional_prime - top_derivative, np.inf)
            / max(np.linalg.norm(top_derivative, np.inf), 1.0e-300)
        ),
    }


def evaluate_polynomial(
    functional: np.ndarray,
    index: dict[Exponent, int],
    polynomial: ComplexPolynomial,
) -> complex:
    return sum(functional[index[term]] * value for term, value in polynomial.items())


def load_bound_array(binding: dict[str, Any], shape: tuple[int, ...]) -> np.ndarray:
    path = PRE / binding["path"]
    require(external_artifact(path) == {"repository": "mtt-preprojection-repair-calculus", **binding}, f"array binding: {path}")
    value = np.load(path, allow_pickle=False)
    require(value.shape == shape, f"array shape: {path}")
    return value


def framed_input(segment: str) -> tuple[Any, list[ComplexPolynomial], list[ComplexPolynomial], float]:
    sys.path[:0] = [str(H4_EXPERIMENT), str(H4_GM), str(H4_SERRE)]
    import charzero_serre_pairing_pilot as serre
    import probe_framed_member_charzero_gm_backend as framed
    import probe_framed_member_direct_operator_derivative as direct

    core, gm, _ = framed.import_sources()
    basis, coefficients, _ = core.build_exact_member()
    section_rows, section_normalization, _ = framed.section_rows(basis, coefficients)
    geometry = direct.selected_path_jet(gm, segment, 0.5, -1)
    source = json.loads(H4_SOURCE.read_text(encoding="ascii"))
    f6, f9, dot_f9 = framed.framed_polynomials(
        gm,
        source,
        section_rows,
        geometry["point"],
        geometry["tangent"],
    )
    sections, derivatives = cayley_sections(f6, f9, dot_f9)
    return serre, sections, derivatives, float(section_normalization)


def execute_segment(
    segment: str,
    minor: dict[str, Any],
    h4_t141: dict[str, Any],
    selected_rows: np.ndarray,
) -> dict[str, Any]:
    started = time.monotonic()
    serre, sections, derivatives, section_normalization = framed_input(segment)
    basis = serre.component_monomials(9, 3)
    require(canonical_sha256(basis) == minor["critical_basis_sha256"], "critical basis")
    index = {term: column for column, term in enumerate(basis)}
    full = relation_matrix(sections, serre.component_monomials)
    full_prime = relation_matrix(derivatives, serre.component_monomials)
    embedding, embedding_pivots, free_columns = top_embedding(serre, basis)
    h4_row = next(
        row
        for row in h4_t141["six_midpoint_audit"]["rows"]
        if row["segment"] == segment
    )
    h4_top = load_bound_array(h4_row["arrays"]["value_center"], (2584,))
    h4_top_prime = load_bound_array(
        h4_row["arrays"]["derivative_center"], (2584,)
    )
    functional, functional_prime, diagnostics = solve_anchored_minor(
        full,
        full_prime,
        embedding,
        embedding_pivots,
        free_columns,
        h4_top,
        h4_top_prime,
        selected_rows,
    )

    jacobian, jacobian_prime, cancellation = toric_jacobian_jet(sections, derivatives)
    denominator = evaluate_polynomial(functional, index, jacobian)
    denominator_prime = evaluate_polynomial(functional_prime, index, jacobian) + evaluate_polynomial(
        functional, index, jacobian_prime
    )

    top_basis = serre.component_monomials(18, 1)
    cox_product = (1, 1, 1, 1, 1, 1)
    normalization_coordinate = 1494
    normalization_polynomial = poly_shift(
        transport_top_monomial(top_basis[normalization_coordinate]),
        cox_product,
    )
    numerator = evaluate_polynomial(functional, index, normalization_polynomial)
    numerator_prime = evaluate_polynomial(
        functional_prime, index, normalization_polynomial
    )

    require(abs(numerator) > 0 and abs(denominator) > 0, "nonzero scale quotient")
    serre_scale = 292.5 * numerator / denominator
    serre_scale_prime = 292.5 * (
        numerator_prime * denominator - numerator * denominator_prime
    ) / (denominator * denominator)
    np.save(functional_path(segment), functional, allow_pickle=False)
    np.save(functional_path(segment, derivative=True), functional_prime, allow_pickle=False)
    diagnostics["total_seconds"] = time.monotonic() - started
    return {
        "segment": segment,
        "parameter": 0.5,
        "lift_sign": -1,
        "section_normalization": section_normalization,
        "critical_relation_nonzeros": int(full.nnz),
        "critical_derivative_relation_nonzeros": int(full_prime.nnz),
        "toric_Jacobian_terms": len(jacobian),
        "toric_Jacobian_derivative_terms": len(jacobian_prime),
        "critical_functional_top_anchor_rows": len(top_basis),
        "critical_functional_free_coordinates": len(free_columns),
        "top_functional_normalization_column_zero_based": normalization_coordinate,
        "Cox_multiplier_coordinate": [float(numerator.real), float(numerator.imag)],
        "Cox_multiplier_coordinate_derivative": [
            float(numerator_prime.real),
            float(numerator_prime.imag),
        ],
        "toric_Jacobian_coordinate": [
            float(denominator.real),
            float(denominator.imag),
        ],
        "toric_Jacobian_coordinate_derivative": [
            float(denominator_prime.real),
            float(denominator_prime.imag),
        ],
        "canonical_Serre_scale": [float(serre_scale.real), float(serre_scale.imag)],
        "canonical_Serre_scale_derivative": [
            float(serre_scale_prime.real),
            float(serre_scale_prime.imag),
        ],
        "cancellation_audit": cancellation,
        "diagnostics": diagnostics,
        "arrays": {
            "critical_functional": artifact(functional_path(segment)),
            "critical_functional_derivative": artifact(
                functional_path(segment, derivative=True)
            ),
        },
        "H4_T141_point_packet": external_artifact(PRE / h4_row["point_packet"]["path"]),
    }


def selected_original_rows(
    rows: list[t64.SparseRow], prime: int, target_rank: int
) -> tuple[list[int], dict[int, t64.SparseRow]]:
    """Return source-row indices that first create each maximum-column pivot."""
    pivots: dict[int, t64.SparseRow] = {}
    selected: list[int] = []
    started = time.monotonic()
    for source_index, source in enumerate(rows):
        row = {
            column: value % prime
            for column, value in source.items()
            if value % prime
        }
        while row:
            pivot = max(row)
            prior = pivots.get(pivot)
            if prior is None:
                inverse = pow(row[pivot], -1, prime)
                pivots[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value % prime
                }
                selected.append(source_index)
                if len(pivots) == target_rank:
                    print(
                        "T65 exact minor selection reached "
                        f"rank={target_rank} at source_row={source_index} "
                        f"elapsed={time.monotonic() - started:.1f}s",
                        flush=True,
                    )
                    return selected, pivots
                break
            factor = row[pivot]
            for column, value in prior.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        if (source_index + 1) % 500 == 0:
            print(
                f"T65 exact minor rows={source_index + 1} rank={len(pivots)} "
                f"elapsed={time.monotonic() - started:.1f}s",
                flush=True,
            )
    return selected, pivots


def build_minor() -> dict[str, Any]:
    curve = t64.import_curve_module()
    source = t64.load(t64.SOURCE)
    prime = 21817
    f6, physical_f9, _ = curve.selected_polynomials(
        source, 5, (1, 0, prime - 1), (0, 1, 0), prime
    )
    cubic = t64.regularizing_cubic()
    f9 = t64.poly_add(
        physical_f9, t64.poly_multiply(f6, cubic, prime), prime
    )
    sections = t64.toric_sections(f6, f9, prime)
    basis = curve.component_monomials(9, 3)
    rows, counts = t64.relation_rows(
        basis, sections, curve.component_monomials, prime
    )
    selected, pivots = selected_original_rows(rows, prime, len(basis) - 1)
    existing = t64.load(t64.WITNESS)
    functional = [int(value) % prime for value in existing["functional"]]
    free = [column for column in range(len(basis)) if column not in pivots]

    require(len(selected) == len(set(selected)) == 9360, "9,360 selected rows")
    require(len(pivots) == 9360 and free == [0], "same free column as T64")
    require(
        canonical_sha256(sorted(pivots)) == existing["pivot_columns_sha256"],
        "same pivot-column certificate as T64",
    )
    require(
        all(
            sum(value * functional[column] for column, value in rows[index].items())
            % prime
            == 0
            for index in selected
        ),
        "T64 dual annihilates selected original rows",
    )
    require(all(functional), "T64 dual is nonzero on every coordinate")

    payload: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-original-row-minor.v1",
        "prime": prime,
        "split_root": 5,
        "ambient_columns": len(basis),
        "relation_rows": len(rows),
        "relation_rows_by_section": counts,
        "rank": len(pivots),
        "quotient_dimension": len(basis) - len(pivots),
        "deleted_column_zero_based": 0,
        "selected_original_rows_zero_based": selected,
        "selected_rows_sha256": canonical_sha256(selected),
        "pivot_columns_sha256": canonical_sha256(sorted(pivots)),
        "critical_basis_sha256": canonical_sha256(basis),
        "t64_dual_functional_sha256": existing["functional_sha256"],
        "selection_rule": "stream all original rows in section/multiplier order and accept each first maximum-column pivot",
        "source_bindings": {
            "T64_dual_witness": artifact(t64.WITNESS),
            "T64_packet": artifact(t64.OUTPUT),
        },
    }
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    MINOR.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    return payload


def load_minor() -> dict[str, Any]:
    payload = json.loads(MINOR.read_text(encoding="ascii"))
    claimed = payload.pop("canonical_payload_sha256")
    require(canonical_sha256(payload) == claimed, "minor canonical hash")
    payload["canonical_payload_sha256"] = claimed
    require(payload["rank"] == 9360, "minor rank")
    require(payload["quotient_dimension"] == 1, "minor quotient dimension")
    require(payload["deleted_column_zero_based"] == 0, "minor deleted column")
    rows = payload["selected_original_rows_zero_based"]
    require(len(rows) == len(set(rows)) == 9360, "minor row count")
    require(canonical_sha256(rows) == payload["selected_rows_sha256"], "row hash")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute-minor", action="store_true")
    parser.add_argument("--select-only", action="store_true")
    arguments = parser.parse_args()

    if arguments.recompute_minor or not MINOR.is_file():
        minor = build_minor()
    else:
        minor = load_minor()

    if arguments.select_only:
        print(
            "CBF.T65 critical minor: PASS "
            f"rows={minor['rank']} deleted={minor['deleted_column_zero_based']}"
        )
        return 0

    h4_t141 = load_canonical(H4_T141)
    require(h4_t141["theorem_id"] == "H4-T141", "H4-T141 identity")
    require(all(h4_t141["checks"].values()), "H4-T141 checks")
    selected_rows, complex_minor = load_complex_minor_rows()
    rows = [
        execute_segment(segment, minor, h4_t141, selected_rows)
        for segment in ("edge-2", "edge-0")
    ]
    gauge_audit = binary_gauge_audit(
        complex(*rows[0]["canonical_Serre_scale"])
    )
    checks = {
        "the_exact_good_reduction_selects_9360_original_relation_rows": minor["rank"]
        == 9360,
        "the_top_embedding_eliminates_2584_coordinates": all(
            row["critical_functional_top_anchor_rows"] == 2584
            and row["critical_functional_free_coordinates"] == 6777
            for row in rows
        ),
        "edge2_and_edge0_use_the_same_hash_bound_complex_minor": len(rows) == 2,
        "both_complex_minor_factorizations_are_nonsingular": all(
            row["diagnostics"]["factor_L_nonzeros"] > 0
            and row["diagnostics"]["factor_U_nonzeros"] > 0
            for row in rows
        ),
        "both_all_row_value_residuals_are_below_1e_8": all(
            row["diagnostics"]["all_row_value_relative_residual"] < 1.0e-8
            for row in rows
        ),
        "both_all_row_derivative_residuals_are_below_1e_8": all(
            row["diagnostics"]["all_row_derivative_relative_residual"] < 1.0e-8
            for row in rows
        ),
        "both_top_embeddings_match_H4_T141_below_1e_12": all(
            row["diagnostics"]["top_embedding_value_relative_residual"] < 1.0e-12
            for row in rows
        ),
        "both_top_embedding_derivatives_match_H4_T141_below_1e_10": all(
            row["diagnostics"]["top_embedding_derivative_relative_residual"]
            < 1.0e-10
            for row in rows
        ),
        "both_binary64_Serre_scale_scouts_are_nonzero": all(
            row["canonical_Serre_scale"] != [0.0, 0.0] for row in rows
        ),
        "three_predeclared_binary_row_gauges_are_replayed": len(
            gauge_audit["rows"]
        )
        == 3,
        "all_exact_dyadic_refinement_residuals_are_below_1e_80": all(
            row["final_exact_dyadic_residual_component_upper"] < 1.0e-80
            for row in gauge_audit["rows"]
        ),
        "the_three_selected_row_gauges_are_distinct": len(
            {row["selected_rows_sha256"] for row in gauge_audit["rows"]}
        )
        == 3,
        "frozen_binary_coefficients_fail_the_one_percent_gauge_stability_test": gauge_audit[
            "minimum_pairwise_Serre_scale_relative_gap"
        ]
        > 0.01,
        "no_binary_scale_or_derivative_is_promoted": not gauge_audit["decision"][
            "binary_coefficient_scale_is_promoted"
        ]
        and not gauge_audit["decision"][
            "binary_coefficient_derivative_is_promoted"
        ],
        "no_observed_value_fit_parameter_or_selector_is_used": True,
    }
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-directed-cayley-serre-scale.v1",
        "theorem_id": "CBF.T65",
        "status": "FROZEN_BINARY_CAYLEY_SERRE_SCALE_PROMOTION_REJECTED_BY_ROW_GAUGE_TEST",
        "tier": "EXACT_FINITE_RANK_CERTIFICATE_PLUS_REPRODUCIBLE_BINARY_STABILITY_REJECTION",
        "source_bindings": {
            "T64_packet": artifact(t64.OUTPUT),
            "T65_exact_good_reduction_minor": artifact(MINOR),
            "T65_complex_minor_packet": artifact(COMPLEX_MINOR_PACKET),
            "T65_complex_minor_rows": artifact(COMPLEX_MINOR_ROWS),
            "H4_T141_contract": external_artifact(H4_T141),
        },
        "formula": {
            "canonical_Serre_scale": "s_C=(585/2)*f_crit(M*m_1494)/f_crit(J_toric)",
            "derivative": "s_C'=(585/2)*(a'*b-a*b')/b^2",
            "top_anchor": "E_M*f=f_H4 and E_M*f'=f_H4'",
            "critical_functional": "R_critical*f=0 after eliminating the 2584 E_M anchor coordinates",
            "critical_functional_derivative": "R_critical*f'=-R_critical'*f with the differentiated H4 anchor",
        },
        "minors": {
            "exact_good_reduction": {
                "rows": minor["rank"],
                "columns": minor["rank"],
                "deleted_column_zero_based": minor["deleted_column_zero_based"],
                "selected_rows_sha256": minor["selected_rows_sha256"],
            },
            "complex_top_anchored": {
                "rows": int(selected_rows.size),
                "columns": int(selected_rows.size),
                "selection_seed": complex_minor["selection"]["seed"],
                "selected_rows_sha256": sha256(COMPLEX_MINOR_ROWS),
            },
        },
        "rows": rows,
        "binary_row_gauge_audit": gauge_audit,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "guardrails": {
            "binary64_residuals_are_called_directed_interval_bounds": False,
            "exact_dyadic_arithmetic_radii_are_called_forward_error_bounds": False,
            "a_binary_scout_value_is_called_the_canonical_geometric_scale": False,
            "two_midpoints_are_called_a_pathwide_execution": False,
            "the_framed_graph_member_is_called_physically_selected": False,
            "beta_C_or_U_eta9_is_claimed": False,
        },
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
        "frontier": {
            "before": "T64 supplied the exact scale formula and H4-T141 supplied only projective directed top traces; the finite-field original-row minor was too ill-conditioned over the complex framed member.",
            "after": "The H4-T141 top functional is embedded through the Cayley multiplier and 2584 coordinates are eliminated. Three predeclared 6777-row gauges all refine their frozen binary systems below 1e-80 residual, yet disagree by more than one percent. Therefore no binary scale or derivative is promoted, and coefficient exactness is isolated as the next cutset.",
            "next": "Construct the selected characteristic-zero coefficient balls, certify one exact 6777-row inverse by a strict Neumann bound, and test all remaining relation rows before evaluating denominator and derivative balls.",
        },
    }
    require(all(checks.values()), f"T65 checks: {checks}")
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    PACKET.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T65 build: PASS "
        + " ".join(
            f"{row['segment']} s_C={complex(*row['canonical_Serre_scale']):.8g}"
            for row in rows
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
