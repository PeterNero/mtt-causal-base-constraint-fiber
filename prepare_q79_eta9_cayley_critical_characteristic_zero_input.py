#!/usr/bin/env python3
"""Prepare the portable characteristic-zero input for CBF.T66.

The exact geometry is evaluated with 512-bit Arb arithmetic.  Every sparse
coefficient is then represented portably by its binary64 midpoint together
with an outward component-norm error enclosing the Arb coefficient.  The
worker therefore needs no research checkout and cannot silently substitute a
different framed member, path, top trace, or row gauge.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from flint import acb, arb, ctx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu

import build_q79_eta9_directed_cayley_serre_scale as t65


ROOT = Path(__file__).resolve().parent
OUTPUT = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_characteristic_zero_seed7909"
)
SEGMENT = "edge-2"
PARAMETER = 0.5
LIFT_SIGN = -1
PRECISION = 512
SEED = 7909

Exponent = tuple[int, int, int, int, int, int]
BallPolynomial = dict[Exponent, acb]


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


def artifact(path: Path) -> dict[str, object]:
    require(path.is_file(), f"artifact exists: {path}")
    return {
        "path": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def external_artifact(path: Path) -> dict[str, object]:
    require(path.is_file(), f"external artifact exists: {path}")
    return {
        "repository": "mtt-preprojection-repair-calculus",
        "path": path.resolve().relative_to(t65.PRE.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def save_array(name: str, value: np.ndarray) -> dict[str, object]:
    path = OUTPUT / f"{name}.npy"
    np.save(path, value, allow_pickle=False)
    return artifact(path)


def save_sparse(name: str, value: sparse.spmatrix) -> dict[str, object]:
    path = OUTPUT / f"{name}.npz"
    sparse.save_npz(path, value, compressed=True)
    return artifact(path)


def poly_add(left: BallPolynomial, right: BallPolynomial) -> BallPolynomial:
    output = dict(left)
    for term, coefficient in right.items():
        output[term] = output.get(term, acb(0)) + coefficient
    return output


def poly_multiply(left: BallPolynomial, right: BallPolynomial) -> BallPolynomial:
    output: BallPolynomial = {}
    for left_term, left_value in left.items():
        for right_term, right_value in right.items():
            term = tuple(
                a + b for a, b in zip(left_term, right_term, strict=True)
            )
            output[term] = output.get(term, acb(0)) + left_value * right_value
    return output


def poly_shift(poly: BallPolynomial, shift: Exponent) -> BallPolynomial:
    return {
        tuple(a + b for a, b in zip(term, shift, strict=True)): coefficient
        for term, coefficient in poly.items()
    }


def poly_derivative(poly: BallPolynomial, variable: int) -> BallPolynomial:
    output: BallPolynomial = {}
    for term, coefficient in poly.items():
        power = term[variable]
        if power:
            reduced = list(term)
            reduced[variable] -= 1
            output[tuple(reduced)] = power * coefficient
    return output


def regularizing_cubic() -> BallPolynomial:
    return {
        (3, 0, 0, 0, 0, 0): acb(1),
        (0, 3, 0, 0, 0, 0): acb(1),
        (0, 0, 3, 0, 0, 0): acb(1),
        (0, 0, 0, 1, 0, 0): acb(1),
    }


def exact_framed_polynomials(
    h4: Any,
    k3_payload: dict[str, Any],
    rows: Any,
    geometry: dict[str, Any],
) -> tuple[BallPolynomial, BallPolynomial, BallPolynomial]:
    b_poly, c_poly = h4.combine_sections(rows, geometry["point"])
    db_poly, dc_poly = h4.combine_sections(rows, geometry["tangent"])
    f6: BallPolynomial = {(0, 0, 0, 2, 0, 0): acb(1)}
    for row in k3_payload["K3"]["F6_terms"]:
        term = (*tuple(int(value) for value in row["exponents"]), 0, 0, 0)
        f6[term] = f6.get(term, acb(0)) - int(row["coefficient"])
    f9 = {(*term, 0, 0, 0): coefficient for term, coefficient in b_poly.items()}
    f9.update(
        {(*term, 1, 0, 0): coefficient for term, coefficient in c_poly.items()}
    )
    dot_f9 = {
        (*term, 0, 0, 0): coefficient for term, coefficient in db_poly.items()
    }
    dot_f9.update(
        {(*term, 1, 0, 0): coefficient for term, coefficient in dc_poly.items()}
    )
    return f6, f9, dot_f9


def exact_cayley_sections(
    f6: BallPolynomial,
    f9: BallPolynomial,
    dot_f9: BallPolynomial,
) -> tuple[list[BallPolynomial], list[BallPolynomial]]:
    f9_regular = poly_add(f9, poly_multiply(regularizing_cubic(), f6))
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


def exact_relation_rows(
    sections: list[BallPolynomial],
    component_monomials: Any,
) -> Iterable[BallPolynomial]:
    multipliers = component_monomials(9, 2)
    for section in sections:
        for multiplier in multipliers:
            yield poly_shift(section, multiplier)


def relation_error_matrix(
    h4: Any,
    exact_sections: list[BallPolynomial],
    binary: sparse.csr_matrix,
    component_monomials: Any,
    basis_index: dict[Exponent, int],
) -> sparse.csr_matrix:
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    exact_rows = exact_relation_rows(exact_sections, component_monomials)
    for row_number, exact_row in enumerate(exact_rows):
        start = int(binary.indptr[row_number])
        stop = int(binary.indptr[row_number + 1])
        midpoint = {
            int(binary.indices[position]): complex(binary.data[position])
            for position in range(start, stop)
        }
        for term, coefficient in exact_row.items():
            column = basis_index[term]
            error = h4.acb_component_error(
                coefficient, midpoint.pop(column, 0.0j)
            )
            if error:
                row_indices.append(row_number)
                column_indices.append(column)
                values.append(error)
        for column, coefficient in midpoint.items():
            error = h4.upward(abs(coefficient.real) + abs(coefficient.imag))
            if error:
                row_indices.append(row_number)
                column_indices.append(column)
                values.append(error)
    require(row_number + 1 == binary.shape[0], "complete exact relation traversal")
    output = sparse.csr_matrix(
        (
            np.asarray(values, dtype=np.float64),
            (row_indices, column_indices),
        ),
        shape=binary.shape,
    )
    output.sum_duplicates()
    output.data = np.nextafter(output.data, math.inf)
    return output


def acb_array(
    center: np.ndarray,
    radius: np.ndarray,
) -> list[acb]:
    require(center.shape == radius.shape, "ball array shape")
    return [
        acb(
            arb(float(value.real), float(error)),
            arb(float(value.imag), float(error)),
        )
        for value, error in zip(center, radius, strict=True)
    ]


def ball_arrays(h4: Any, values: list[acb]) -> tuple[np.ndarray, np.ndarray]:
    center = np.asarray(
        [
            complex(float(value.real.mid()), float(value.imag.mid()))
            for value in values
        ],
        dtype=np.complex128,
    )
    radius = np.asarray(
        [
            h4.acb_component_error(value, midpoint)
            for value, midpoint in zip(values, center, strict=True)
        ],
        dtype=np.float64,
    )
    return center, radius


def pivot_balls(
    h4: Any,
    embedding: sparse.csr_matrix,
    pivots: np.ndarray,
    center: np.ndarray,
    radius: np.ndarray,
) -> tuple[list[acb], dict[str, Any]]:
    block = embedding[:, pivots].tocsr()
    identity = sparse.eye(block.shape[0], dtype=np.complex128, format="csr")
    nilpotent = block - identity
    nilpotent.eliminate_zeros()
    square = nilpotent @ nilpotent
    square.eliminate_zeros()
    require(square.nnz == 0, "square-zero Cayley embedding shear")
    top = acb_array(center, radius)
    output: list[acb] = []
    for row in range(block.shape[0]):
        value = top[row]
        start, stop = int(nilpotent.indptr[row]), int(nilpotent.indptr[row + 1])
        for position in range(start, stop):
            coefficient = nilpotent.data[position]
            require(coefficient.imag == 0 and coefficient.real.is_integer(), "integral embedding")
            value -= int(coefficient.real) * top[int(nilpotent.indices[position])]
        output.append(value)
    return output, {
        "shape": list(block.shape),
        "off_diagonal_nonzeros": int(nilpotent.nnz),
        "nilpotence_index": 2,
        "inverse_formula": "(I+N)^-1=I-N because N^2=0",
    }


def selected_exact_rows(
    sections: list[BallPolynomial],
    component_monomials: Any,
    selected: np.ndarray,
    *,
    require_nonempty: bool = True,
) -> list[BallPolynomial]:
    lookup = {int(source): local for local, source in enumerate(selected)}
    output: list[BallPolynomial] = [dict() for _ in range(selected.size)]
    assigned = np.zeros(selected.size, dtype=bool)
    for source, row in enumerate(exact_relation_rows(sections, component_monomials)):
        local = lookup.get(source)
        if local is not None:
            output[local] = row
            assigned[local] = True
    require(bool(assigned.all()), "complete selected exact relation rows")
    require(
        not require_nonempty or all(row for row in output),
        "nonempty selected exact relation rows",
    )
    return output


def scaled_rhs_balls(
    rows: list[BallPolynomial],
    basis_index: dict[Exponent, int],
    pivot_lookup: dict[int, int],
    pivot_values: list[acb],
    row_factor: np.ndarray,
) -> list[acb]:
    output: list[acb] = []
    for local, row in enumerate(rows):
        value = sum(
            (
                coefficient * pivot_values[pivot_lookup[basis_index[term]]]
                for term, coefficient in row.items()
                if basis_index[term] in pivot_lookup
            ),
            acb(0),
        )
        output.append(-acb(float(row_factor[local])) * value)
    return output


def scaled_derivative_constant_balls(
    rows: list[BallPolynomial],
    derivative_rows: list[BallPolynomial],
    basis_index: dict[Exponent, int],
    pivot_lookup: dict[int, int],
    pivot_values: list[acb],
    pivot_derivatives: list[acb],
    row_factor: np.ndarray,
) -> list[acb]:
    output: list[acb] = []
    for local, (row, derivative_row) in enumerate(
        zip(rows, derivative_rows, strict=True)
    ):
        value = sum(
            (
                coefficient * pivot_derivatives[pivot_lookup[basis_index[term]]]
                for term, coefficient in row.items()
                if basis_index[term] in pivot_lookup
            ),
            acb(0),
        )
        value += sum(
            (
                coefficient * pivot_values[pivot_lookup[basis_index[term]]]
                for term, coefficient in derivative_row.items()
                if basis_index[term] in pivot_lookup
            ),
            acb(0),
        )
        output.append(-acb(float(row_factor[local])) * value)
    return output


def scaled_error_matrix(
    h4: Any,
    center_unscaled: sparse.csr_matrix,
    error_unscaled: sparse.csr_matrix,
    selected: np.ndarray,
    free: np.ndarray,
    row_factor: np.ndarray,
    column_factor: np.ndarray,
) -> sparse.csr_matrix:
    center = center_unscaled[selected, :][:, free].tocsr()
    error = error_unscaled[selected, :][:, free].tocsr()
    scaled_error = (
        sparse.diags(np.abs(row_factor))
        @ error
        @ sparse.diags(np.abs(column_factor))
    ).tocsr()
    component = h4.component_sparse(center)
    rounding = (
        sparse.diags(np.abs(row_factor))
        @ (component + error)
        @ sparse.diags(np.abs(column_factor))
    ).tocsr()
    rounding.data *= h4.gamma(12)
    output = (scaled_error + rounding).tocsr()
    output.sum_duplicates()
    output.data = np.nextafter(output.data, math.inf)
    return output


@dataclass(frozen=True)
class BallJet:
    value: acb
    first: acb

    def __add__(self, other: "BallJet") -> "BallJet":
        return BallJet(self.value + other.value, self.first + other.first)

    def __neg__(self) -> "BallJet":
        return BallJet(-self.value, -self.first)

    def __mul__(self, other: "BallJet") -> "BallJet":
        return BallJet(
            self.value * other.value,
            self.first * other.value + self.value * other.first,
        )


JetPolynomial = dict[Exponent, BallJet]


def jet_add(left: JetPolynomial, right: JetPolynomial) -> JetPolynomial:
    output = dict(left)
    for term, coefficient in right.items():
        output[term] = output.get(term, BallJet(acb(0), acb(0))) + coefficient
    return output


def jet_multiply(left: JetPolynomial, right: JetPolynomial) -> JetPolynomial:
    output: JetPolynomial = {}
    for left_term, left_value in left.items():
        for right_term, right_value in right.items():
            term = tuple(
                a + b for a, b in zip(left_term, right_term, strict=True)
            )
            product = left_value * right_value
            output[term] = output.get(term, BallJet(acb(0), acb(0))) + product
    return output


def jet_derivative(poly: JetPolynomial, variable: int) -> JetPolynomial:
    output: JetPolynomial = {}
    for term, coefficient in poly.items():
        power = term[variable]
        if power:
            reduced = list(term)
            reduced[variable] -= 1
            output[tuple(reduced)] = BallJet(
                power * coefficient.value,
                power * coefficient.first,
            )
    return output


def jet_determinant(matrix: list[list[JetPolynomial]]) -> JetPolynomial:
    output: JetPolynomial = {}
    unit = {(0, 0, 0, 0, 0, 0): BallJet(acb(1), acb(0))}
    for permutation in itertools.permutations(range(len(matrix))):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(len(matrix))
            for right in range(left + 1, len(matrix))
        )
        term = unit
        for row, column in enumerate(permutation):
            term = jet_multiply(term, matrix[row][column])
        if inversions % 2:
            term = {key: -value for key, value in term.items()}
        output = jet_add(output, term)
    return output


def exact_toric_jacobian(
    sections: list[BallPolynomial],
    derivatives: list[BallPolynomial],
) -> tuple[BallPolynomial, BallPolynomial, dict[str, str]]:
    jets = [
        {
            term: BallJet(section.get(term, acb(0)), derivatives[index].get(term, acb(0)))
            for term in set(section) | set(derivatives[index])
        }
        for index, section in enumerate(sections)
    ]
    matrix = [jets]
    for variable in (1, 2, 3, 4):
        matrix.append([jet_derivative(poly, variable) for poly in jets])
    numerator = jet_determinant(matrix)
    divisor = (1, 0, 0, 0, 0, 1)
    value: BallPolynomial = {}
    derivative: BallPolynomial = {}
    discarded_value = arb(0)
    discarded_derivative = arb(0)
    for term, coefficient in numerator.items():
        if all(a >= b for a, b in zip(term, divisor, strict=True)):
            reduced = tuple(a - b for a, b in zip(term, divisor, strict=True))
            value[reduced] = value.get(reduced, acb(0)) + coefficient.value
            derivative[reduced] = (
                derivative.get(reduced, acb(0)) + coefficient.first
            )
        else:
            require(
                coefficient.value.contains(0) and coefficient.first.contains(0),
                f"exact toric-Jacobian divisibility: {term}",
            )
            discarded_value = max(discarded_value, coefficient.value.abs_upper())
            discarded_derivative = max(
                discarded_derivative, coefficient.first.abs_upper()
            )
    return value, derivative, {
        "discarded_nondivisible_value_absolute_upper": str(discarded_value),
        "discarded_nondivisible_derivative_absolute_upper": str(
            discarded_derivative
        ),
    }


def polynomial_vector_error(
    h4: Any,
    exact: BallPolynomial,
    binary: dict[Exponent, complex],
    basis: list[Exponent],
) -> tuple[np.ndarray, np.ndarray]:
    center = np.asarray([binary.get(term, 0.0j) for term in basis], dtype=np.complex128)
    error = np.asarray(
        [
            h4.acb_component_error(exact.get(term, acb(0)), midpoint)
            for term, midpoint in zip(basis, center, strict=True)
        ],
        dtype=np.float64,
    )
    return center, error


def save_exact_ball_polynomials(
    value: BallPolynomial,
    derivative: BallPolynomial,
    basis_index: dict[Exponent, int],
) -> dict[str, object]:
    path = OUTPUT / "toric_jacobian_exact_balls.json"

    def rows(poly: BallPolynomial) -> list[dict[str, object]]:
        return [
            {
                "column": basis_index[term],
                "real_ball": str(coefficient.real),
                "imaginary_ball": str(coefficient.imag),
            }
            for term, coefficient in sorted(
                poly.items(), key=lambda item: basis_index[item[0]]
            )
        ]

    payload: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-toric-jacobian-exact-balls.v1",
        "precision_bits": ctx.prec,
        "ambient_columns": len(basis_index),
        "value_rows": rows(value),
        "derivative_rows": rows(derivative),
    }
    payload["canonical_payload_sha256"] = canonical_sha256(payload)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    return artifact(path)


def main() -> int:
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--precision", type=int, default=PRECISION)
    parser.add_argument("--output-directory", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    require(arguments.precision >= 384, "characteristic-zero precision")
    OUTPUT = arguments.output_directory.resolve()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    ctx.prec = arguments.precision

    sys.path[:0] = [str(t65.H4_EXPERIMENT), str(t65.H4_GM), str(t65.H4_SERRE)]
    import charzero_serre_pairing_pilot as serre
    import probe_framed_member_charzero_gm_backend as framed
    import probe_framed_member_directed_top_trace as h4

    core, gm, _redundant = framed.import_sources()
    member_basis, coefficients, member_diagnostics = core.build_exact_member()
    binary_section_rows, normalization, _normalized = framed.section_rows(
        member_basis, coefficients
    )
    exact_section_rows_input = h4.exact_section_rows(
        member_basis, coefficients, normalization
    )
    binary_geometry_module = __import__(
        "probe_framed_member_direct_operator_derivative"
    )
    binary_geometry = binary_geometry_module.selected_path_jet(
        gm, SEGMENT, PARAMETER, LIFT_SIGN
    )
    exact_geometry = h4.exact_path_jet(SEGMENT, PARAMETER, LIFT_SIGN)
    k3_payload = json.loads(t65.H4_SOURCE.read_text(encoding="ascii"))
    binary_f6, binary_f9, binary_dot_f9 = framed.framed_polynomials(
        gm,
        k3_payload,
        binary_section_rows,
        binary_geometry["point"],
        binary_geometry["tangent"],
    )
    binary_sections, binary_derivatives = t65.cayley_sections(
        binary_f6, binary_f9, binary_dot_f9
    )
    exact_f6, exact_f9, exact_dot_f9 = exact_framed_polynomials(
        h4, k3_payload, exact_section_rows_input, exact_geometry
    )
    exact_sections, exact_derivatives = exact_cayley_sections(
        exact_f6, exact_f9, exact_dot_f9
    )

    basis = serre.component_monomials(9, 3)
    basis_index = {term: column for column, term in enumerate(basis)}
    relation = t65.relation_matrix(binary_sections, serre.component_monomials).tocsr()
    relation_prime = t65.relation_matrix(
        binary_derivatives, serre.component_monomials
    ).tocsr()
    relation_error = relation_error_matrix(
        h4, exact_sections, relation, serre.component_monomials, basis_index
    )
    relation_prime_error = relation_error_matrix(
        h4,
        exact_derivatives,
        relation_prime,
        serre.component_monomials,
        basis_index,
    )
    embedding, pivots, free = t65.top_embedding(serre, basis)

    h4_packet = t65.load_canonical(t65.H4_T141)
    h4_row = next(
        row
        for row in h4_packet["six_midpoint_audit"]["rows"]
        if row["segment"] == SEGMENT
    )
    top_center = t65.load_bound_array(h4_row["arrays"]["value_center"], (2584,))
    top_radius = t65.load_bound_array(h4_row["arrays"]["value_radius"], (2584,))
    top_prime_center = t65.load_bound_array(
        h4_row["arrays"]["derivative_center"], (2584,)
    )
    top_prime_radius = t65.load_bound_array(
        h4_row["arrays"]["derivative_radius"], (2584,)
    )
    pivot_value_balls, embedding_diagnostics = pivot_balls(
        h4, embedding, pivots, top_center, top_radius
    )
    pivot_derivative_balls, derivative_embedding_diagnostics = pivot_balls(
        h4, embedding, pivots, top_prime_center, top_prime_radius
    )
    require(
        embedding_diagnostics == derivative_embedding_diagnostics,
        "common exact top embedding",
    )
    pivot_center, pivot_radius = ball_arrays(h4, pivot_value_balls)
    pivot_prime_center, pivot_prime_radius = ball_arrays(
        h4, pivot_derivative_balls
    )
    binary_pivot = splu(embedding[:, pivots].tocsc()).solve(top_center)
    binary_pivot_prime = splu(embedding[:, pivots].tocsc()).solve(top_prime_center)
    require(
        np.linalg.norm(binary_pivot - pivot_center, np.inf) < 1.0e-10,
        "pivot center replay",
    )
    require(
        np.linalg.norm(binary_pivot_prime - pivot_prime_center, np.inf) < 1.0e-8,
        "pivot derivative center replay",
    )

    selected_path = (
        ROOT
        / "certificates"
        / "q79_eta9_cayley_critical_refinement_seed7909"
        / "selected_original_rows.npy"
    )
    selected = np.load(selected_path, allow_pickle=False).astype(np.int64)
    require(selected.shape == (6777,), "selected row shape")
    reduced = relation[:, free].tocsr()
    selected_center = reduced[selected, :].tocsr()
    row_norm = np.asarray(abs(selected_center).max(axis=1).toarray()).ravel()
    row_factor = 1.0 / row_norm
    row_balanced = sparse.diags(row_factor) @ selected_center
    column_norm = np.asarray(abs(row_balanced).max(axis=0).toarray()).ravel()
    column_factor = 1.0 / column_norm
    balanced = (
        sparse.diags(row_factor)
        @ selected_center
        @ sparse.diags(column_factor)
    ).tocsr()
    balanced_error = scaled_error_matrix(
        h4,
        relation,
        relation_error,
        selected,
        free,
        row_factor,
        column_factor,
    )
    derivative_coupling = -(
        sparse.diags(row_factor)
        @ relation_prime[selected, :][:, free]
        @ sparse.diags(column_factor)
    ).tocsr()
    derivative_coupling_error = scaled_error_matrix(
        h4,
        relation_prime,
        relation_prime_error,
        selected,
        free,
        row_factor,
        column_factor,
    )

    exact_selected = selected_exact_rows(
        exact_sections, serre.component_monomials, selected
    )
    exact_selected_prime = selected_exact_rows(
        exact_derivatives,
        serre.component_monomials,
        selected,
        require_nonempty=False,
    )
    pivot_lookup = {int(column): index for index, column in enumerate(pivots)}
    value_rhs_balls = scaled_rhs_balls(
        exact_selected,
        basis_index,
        pivot_lookup,
        pivot_value_balls,
        row_factor,
    )
    value_rhs_center = row_factor * (
        -(relation[selected, :][:, pivots] @ binary_pivot)
    )
    value_rhs_error = np.asarray(
        [
            h4.acb_component_error(value, midpoint)
            for value, midpoint in zip(
                value_rhs_balls, value_rhs_center, strict=True
            )
        ],
        dtype=np.float64,
    )
    derivative_constant_balls = scaled_derivative_constant_balls(
        exact_selected,
        exact_selected_prime,
        basis_index,
        pivot_lookup,
        pivot_value_balls,
        pivot_derivative_balls,
        row_factor,
    )
    derivative_constant_center = row_factor * -(
        relation[selected, :][:, pivots] @ binary_pivot_prime
        + relation_prime[selected, :][:, pivots] @ binary_pivot
    )
    derivative_constant_error = np.asarray(
        [
            h4.acb_component_error(value, midpoint)
            for value, midpoint in zip(
                derivative_constant_balls,
                derivative_constant_center,
                strict=True,
            )
        ],
        dtype=np.float64,
    )

    binary_jacobian, binary_jacobian_prime, binary_cancellation = (
        t65.toric_jacobian_jet(binary_sections, binary_derivatives)
    )
    exact_jacobian, exact_jacobian_prime, exact_cancellation = exact_toric_jacobian(
        exact_sections, exact_derivatives
    )
    jacobian_center, jacobian_error = polynomial_vector_error(
        h4, exact_jacobian, binary_jacobian, basis
    )
    jacobian_prime_center, jacobian_prime_error = polynomial_vector_error(
        h4, exact_jacobian_prime, binary_jacobian_prime, basis
    )
    exact_jacobian_binding = save_exact_ball_polynomials(
        exact_jacobian, exact_jacobian_prime, basis_index
    )

    arrays = {
        "selected_rows": save_array("selected_rows", selected),
        "embedding_pivots": save_array("embedding_pivots", pivots),
        "free_columns": save_array("free_columns", free),
        "row_factor": save_array("row_factor", row_factor),
        "column_factor": save_array("column_factor", column_factor),
        "pivot_value_center": save_array("pivot_value_center", pivot_center),
        "pivot_value_radius": save_array("pivot_value_radius", pivot_radius),
        "pivot_derivative_center": save_array(
            "pivot_derivative_center", pivot_prime_center
        ),
        "pivot_derivative_radius": save_array(
            "pivot_derivative_radius", pivot_prime_radius
        ),
        "value_rhs_center": save_array("value_rhs_center", value_rhs_center),
        "value_rhs_error": save_array("value_rhs_error", value_rhs_error),
        "derivative_constant_center": save_array(
            "derivative_constant_center", derivative_constant_center
        ),
        "derivative_constant_error": save_array(
            "derivative_constant_error", derivative_constant_error
        ),
        "jacobian_center": save_array("jacobian_center", jacobian_center),
        "jacobian_error": save_array("jacobian_error", jacobian_error),
        "jacobian_derivative_center": save_array(
            "jacobian_derivative_center", jacobian_prime_center
        ),
        "jacobian_derivative_error": save_array(
            "jacobian_derivative_error", jacobian_prime_error
        ),
    }
    matrices = {
        "balanced_matrix_center": save_sparse("balanced_matrix_center", balanced),
        "balanced_matrix_error": save_sparse(
            "balanced_matrix_error", balanced_error
        ),
        "balanced_derivative_coupling_center": save_sparse(
            "balanced_derivative_coupling_center", derivative_coupling
        ),
        "balanced_derivative_coupling_error": save_sparse(
            "balanced_derivative_coupling_error", derivative_coupling_error
        ),
        "full_relation_center": save_sparse("full_relation_center", relation),
        "full_relation_error": save_sparse("full_relation_error", relation_error),
        "full_relation_derivative_center": save_sparse(
            "full_relation_derivative_center", relation_prime
        ),
        "full_relation_derivative_error": save_sparse(
            "full_relation_derivative_error", relation_prime_error
        ),
    }
    checks = {
        "the_exact_top_embedding_is_square_zero_unipotent": embedding_diagnostics[
            "nilpotence_index"
        ]
        == 2,
        "the_selected_system_has_6777_rows_and_columns": balanced.shape
        == (6777, 6777),
        "all_characteristic_zero_coefficient_errors_are_finite": bool(
            np.isfinite(balanced_error.data).all()
            and np.isfinite(relation_error.data).all()
            and np.isfinite(relation_prime_error.data).all()
        ),
        "the_value_and_derivative_anchor_errors_are_finite": bool(
            np.isfinite(value_rhs_error).all()
            and np.isfinite(derivative_constant_error).all()
        ),
        "the_toric_Jacobian_and_derivative_are_enclosed": bool(
            np.isfinite(jacobian_error).all()
            and np.isfinite(jacobian_prime_error).all()
        ),
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"preparation checks: {checks}")
    metadata: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-input.v1",
        "theorem_id": "CBF.T66",
        "status": "PORTABLE_CHARACTERISTIC_ZERO_COMPONENT_BALL_INPUT",
        "geometry": {
            "segment": SEGMENT,
            "parameter": PARAMETER,
            "lift_sign": LIFT_SIGN,
            "precision_bits": arguments.precision,
            "selection_seed": SEED,
            "exact_q_ball": str(exact_geometry["q"]),
            "member_diagnostics": member_diagnostics,
        },
        "dimensions": {
            "critical_basis": len(basis),
            "top_anchor": int(pivots.size),
            "free_coordinates": int(free.size),
            "full_relation_rows": int(relation.shape[0]),
            "nonzero_reduced_rows": int(
                np.count_nonzero(np.asarray(abs(relation[:, free]).max(axis=1).toarray()).ravel())
            ),
            "selected_rows": int(selected.size),
        },
        "top_embedding": embedding_diagnostics,
        "coefficient_error_summary": {
            "balanced_matrix_maximum_entry": float(
                balanced_error.data.max(initial=0.0)
            ),
            "balanced_matrix_maximum_row_sum": float(
                h4.row_positive_sums_upper(balanced_error).max()
            ),
            "full_relation_maximum_entry": float(
                relation_error.data.max(initial=0.0)
            ),
            "full_derivative_relation_maximum_entry": float(
                relation_prime_error.data.max(initial=0.0)
            ),
            "value_rhs_maximum_error": float(value_rhs_error.max()),
            "derivative_constant_maximum_error": float(
                derivative_constant_error.max()
            ),
            "jacobian_maximum_error": float(jacobian_error.max()),
            "jacobian_derivative_maximum_error": float(
                jacobian_prime_error.max()
            ),
        },
        "binary_cancellation_audit": binary_cancellation,
        "exact_cancellation_audit": exact_cancellation,
        "arrays": arrays,
        "matrices": matrices,
        "exact_polynomials": {
            "toric_Jacobian": exact_jacobian_binding,
        },
        "source_bindings": {
            "T65_packet": artifact(t65.PACKET),
            "T65_selected_rows": artifact(selected_path),
            "H4_T141_contract": external_artifact(t65.H4_T141),
            "H4_T141_value_center": external_artifact(
                t65.PRE / h4_row["arrays"]["value_center"]["path"]
            ),
            "H4_T141_value_radius": external_artifact(
                t65.PRE / h4_row["arrays"]["value_radius"]["path"]
            ),
            "H4_T141_derivative_center": external_artifact(
                t65.PRE / h4_row["arrays"]["derivative_center"]["path"]
            ),
            "H4_T141_derivative_radius": external_artifact(
                t65.PRE / h4_row["arrays"]["derivative_radius"]["path"]
            ),
            "exact_ball_compiler": external_artifact(
                t65.H4_EXPERIMENT / "probe_framed_member_directed_top_trace.py"
            ),
            "preparer": artifact(Path(__file__)),
        },
        "representation": {
            "norm": "abs(real)+abs(imag)",
            "center": "binary64 coefficient used by the existing complex scout",
            "error": "outward float upper bound enclosing the 512-bit Arb coefficient around that center",
            "worker_contract": "replace each complex midpoint z and component error e by [Re(z)+/-e]+i[Im(z)+/-e]",
        },
        "checks": checks,
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    metadata["canonical_payload_sha256"] = canonical_sha256(metadata)
    output_path = OUTPUT / "metadata.json"
    output_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T66 characteristic-zero input: PASS "
        f"shape={balanced.shape} nnz={balanced.nnz} "
        f"error_row={metadata['coefficient_error_summary']['balanced_matrix_maximum_row_sum']:.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
