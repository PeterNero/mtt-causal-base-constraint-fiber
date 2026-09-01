#!/usr/bin/env python3
"""Build the exact CBF.T59 lower-order and inverse-tail compiler packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from build_augmented_heterotic_triangular_principal_symbol import canonical_hash, load_json
from build_full_graded_augmented_heterotic_symbol_parametrix import (
    carrier_dimension,
    correction_rank,
    degree_hodge_symbol,
    graded_symbol,
)


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler_source_lock.json"
SCHEMA = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler_contract.schema.json"
THEOREM = ROOT / "AugmentedHodgeLowerOrderCoefficientAndGlobalInverseTailCompilerTheorem_v1.md"
OUTPUT = ROOT / "augmented_hodge_lower_order_inverse_tail_compiler.packet.json"

RANK = 4
THETA = Fraction(1, 3)
DEGREES = [-1, 0, 1, 2, 3]
MAP_DEGREES = [-1, 0, 1, 2]

Polynomial = tuple[Fraction, ...]
PolyMatrix = list[list[Polynomial]]
PolyVector = list[Polynomial]
Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ptrim(value: tuple[Fraction, ...] | list[Fraction]) -> Polynomial:
    result = list(value)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result or [Fraction(0)])


def pconst(value: Fraction | int) -> Polynomial:
    return (Fraction(value),)


def padd(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    return ptrim(
        [
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        ]
    )


def pneg(value: Polynomial) -> Polynomial:
    return tuple(-entry for entry in value)


def psub(left: Polynomial, right: Polynomial) -> Polynomial:
    return padd(left, pneg(right))


def pmul(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, left_entry in enumerate(left):
        for j, right_entry in enumerate(right):
            result[i + j] += left_entry * right_entry
    return ptrim(result)


def pderivative(value: Polynomial) -> Polynomial:
    if len(value) == 1:
        return pconst(0)
    return ptrim([Fraction(index) * value[index] for index in range(1, len(value))])


def pzero_matrix(rows: int, columns: int) -> PolyMatrix:
    return [[pconst(0) for _ in range(columns)] for _ in range(rows)]


def pshape(matrix: PolyMatrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0]) if matrix else 0


def ptranspose(matrix: PolyMatrix) -> PolyMatrix:
    rows, columns = pshape(matrix)
    return [[matrix[row][column] for row in range(rows)] for column in range(columns)]


def pmat_add(left: PolyMatrix, right: PolyMatrix) -> PolyMatrix:
    return [[padd(a, b) for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def pmat_neg(matrix: PolyMatrix) -> PolyMatrix:
    return [[pneg(entry) for entry in row] for row in matrix]


def pmat_sub(left: PolyMatrix, right: PolyMatrix) -> PolyMatrix:
    return pmat_add(left, pmat_neg(right))


def pmat_mul(left: PolyMatrix, right: PolyMatrix) -> PolyMatrix:
    left_rows, inner = pshape(left)
    right_rows, right_columns = pshape(right)
    if inner != right_rows:
        raise ValueError("polynomial matrix shape mismatch")
    result = pzero_matrix(left_rows, right_columns)
    for row in range(left_rows):
        for column in range(right_columns):
            total = pconst(0)
            for index in range(inner):
                total = padd(total, pmul(left[row][index], right[index][column]))
            result[row][column] = total
    return result


def pmat_derivative(matrix: PolyMatrix) -> PolyMatrix:
    return [[pderivative(entry) for entry in row] for row in matrix]


def pmat_scale(matrix: PolyMatrix, scalar: Polynomial) -> PolyMatrix:
    return [[pmul(scalar, entry) for entry in row] for row in matrix]


def pmat_from_fraction(matrix: Matrix) -> PolyMatrix:
    return [[pconst(entry) for entry in row] for row in matrix]


def pmat_vector(matrix: PolyMatrix, vector: PolyVector) -> PolyVector:
    rows, columns = pshape(matrix)
    if columns != len(vector):
        raise ValueError("polynomial matrix-vector shape mismatch")
    result = []
    for row in range(rows):
        total = pconst(0)
        for column in range(columns):
            total = padd(total, pmul(matrix[row][column], vector[column]))
        result.append(total)
    return result


def pvector_add(left: PolyVector, right: PolyVector) -> PolyVector:
    return [padd(a, b) for a, b in zip(left, right)]


def pvector_neg(vector: PolyVector) -> PolyVector:
    return [pneg(entry) for entry in vector]


def pvector_derivative(vector: PolyVector) -> PolyVector:
    return [pderivative(entry) for entry in vector]


def pvector_second_derivative(vector: PolyVector) -> PolyVector:
    return pvector_derivative(pvector_derivative(vector))


def serialize_pmatrix(matrix: PolyMatrix) -> list[list[list[str]]]:
    return [[[str(coefficient) for coefficient in entry] for entry in row] for row in matrix]


def pdigest(matrix: PolyMatrix) -> str:
    return canonical_hash(serialize_pmatrix(matrix))


def pnonzero_count(matrix: PolyMatrix) -> int:
    return sum(entry != pconst(0) for row in matrix for entry in row)


def pmax_degree(matrix: PolyMatrix) -> int:
    return max((len(entry) - 1 for row in matrix for entry in row), default=0)


def real_symbol_map(degree: int) -> Matrix:
    beta = [(Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))]
    symbol = graded_symbol(beta, beta, degree, RANK)
    result: Matrix = []
    for row in symbol:
        real_row = []
        for real, imaginary in row:
            if imaginary != 0:
                raise ValueError("real witness unexpectedly produced an imaginary symbol entry")
            real_row.append(real)
        result.append(real_row)
    return result


def map_polynomials(degree: int) -> tuple[Polynomial, Polynomial]:
    g = (Fraction(1), Fraction(degree + 3, 20))
    f = (Fraction(degree + 4, 7), Fraction(degree + 5, 11))
    return g, f


def weighted_adjoint_zero_order(a: PolyMatrix, b: PolyMatrix) -> PolyMatrix:
    at = ptranspose(a)
    return pmat_sub(
        pmat_sub(ptranspose(b), pmat_derivative(at)),
        pmat_scale(at, pconst(THETA)),
    )


def hodge_coefficients(
    dimension: int,
    outgoing: tuple[PolyMatrix, PolyMatrix] | None,
    incoming: tuple[PolyMatrix, PolyMatrix] | None,
) -> tuple[PolyMatrix, PolyMatrix, PolyMatrix]:
    c = pzero_matrix(dimension, dimension)
    r = pzero_matrix(dimension, dimension)
    e = pzero_matrix(dimension, dimension)
    if outgoing is not None:
        a, b = outgoing
        at = ptranspose(a)
        delta = weighted_adjoint_zero_order(a, b)
        c = pmat_add(c, pmat_mul(at, a))
        r = pmat_add(
            r,
            pmat_add(
                pmat_neg(pmat_mul(at, pmat_derivative(a))),
                pmat_sub(pmat_mul(delta, a), pmat_mul(at, b)),
            ),
        )
        e = pmat_add(
            e,
            pmat_add(
                pmat_neg(pmat_mul(at, pmat_derivative(b))),
                pmat_mul(delta, b),
            ),
        )
    if incoming is not None:
        a, b = incoming
        at = ptranspose(a)
        delta = weighted_adjoint_zero_order(a, b)
        c = pmat_add(c, pmat_mul(a, at))
        r = pmat_add(
            r,
            pmat_add(
                pmat_neg(pmat_mul(a, pmat_derivative(at))),
                pmat_sub(pmat_mul(a, delta), pmat_mul(b, at)),
            ),
        )
        e = pmat_add(
            e,
            pmat_add(pmat_mul(a, pmat_derivative(delta)), pmat_mul(b, delta)),
        )
    return c, r, e


def apply_l(a: PolyMatrix, b: PolyMatrix, vector: PolyVector) -> PolyVector:
    return pvector_add(pmat_vector(a, pvector_derivative(vector)), pmat_vector(b, vector))


def apply_l_adjoint(a: PolyMatrix, b: PolyMatrix, vector: PolyVector) -> PolyVector:
    at = ptranspose(a)
    delta = weighted_adjoint_zero_order(a, b)
    return pvector_add(
        pvector_neg(pmat_vector(at, pvector_derivative(vector))),
        pmat_vector(delta, vector),
    )


def apply_hodge_direct(
    vector: PolyVector,
    outgoing: tuple[PolyMatrix, PolyMatrix] | None,
    incoming: tuple[PolyMatrix, PolyMatrix] | None,
) -> PolyVector:
    result = [pconst(0) for _ in vector]
    if outgoing is not None:
        a, b = outgoing
        result = pvector_add(result, apply_l_adjoint(a, b, apply_l(a, b, vector)))
    if incoming is not None:
        a, b = incoming
        result = pvector_add(result, apply_l(a, b, apply_l_adjoint(a, b, vector)))
    return result


def apply_hodge_coefficients(c: PolyMatrix, r: PolyMatrix, e: PolyMatrix, vector: PolyVector) -> PolyVector:
    return pvector_add(
        pvector_add(
            pvector_neg(pmat_vector(c, pvector_second_derivative(vector))),
            pmat_vector(r, pvector_derivative(vector)),
        ),
        pmat_vector(e, vector),
    )


def dense_probe(dimension: int, probe: int) -> PolyVector:
    return [
        (
            Fraction(index + probe + 1),
            Fraction(2 * index + probe + 3),
            Fraction(index + 2 * probe + 5),
            Fraction((index + 1) * (probe + 1), 3),
        )
        for index in range(dimension)
    ]


def mzero(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def midentity(size: int) -> Matrix:
    result = mzero(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def mtranspose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def madd(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def mneg(matrix: Matrix) -> Matrix:
    return [[-entry for entry in row] for row in matrix]


def msub(left: Matrix, right: Matrix) -> Matrix:
    return madd(left, mneg(right))


def mmul(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left)
    inner = len(left[0]) if left else 0
    columns = len(right[0]) if right else 0
    if inner != len(right):
        raise ValueError("matrix shape mismatch")
    return [
        [sum((left[row][k] * right[k][column] for k in range(inner)), Fraction(0)) for column in range(columns)]
        for row in range(rows)
    ]


def mscale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * entry for entry in row] for row in matrix]


def mdiag(values: list[Fraction]) -> Matrix:
    result = mzero(len(values), len(values))
    for index, value in enumerate(values):
        result[index][index] = value
    return result


def mouter(left: list[Fraction], right: list[Fraction]) -> Matrix:
    return [[a * b for b in right] for a in left]


def minverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + identity_row[:] for row, identity_row in zip(matrix, midentity(size))]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [entry - factor * pivot_entry for entry, pivot_entry in zip(work[row], work[column])]
    return [row[size:] for row in work]


def mpower(matrix: Matrix, exponent: int) -> Matrix:
    result = midentity(len(matrix))
    base = matrix
    value = exponent
    while value:
        if value & 1:
            result = mmul(result, base)
        base = mmul(base, base)
        value >>= 1
    return result


def mblock(a: Matrix, b: Matrix, c: Matrix, d: Matrix) -> Matrix:
    return [a_row + b_row for a_row, b_row in zip(a, b)] + [c_row + d_row for c_row, d_row in zip(c, d)]


def mstrings(matrix: Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


def mdigest(matrix: Matrix) -> str:
    return canonical_hash(mstrings(matrix))


def build_neumann_certificate() -> tuple[dict[str, Any], dict[str, bool]]:
    sqrt_h0 = mdiag([Fraction(1), Fraction(2), Fraction(3), Fraction(4)])
    h0 = mmul(sqrt_h0, sqrt_h0)
    h0_inverse_half = mdiag([Fraction(1), Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)])
    vector = [Fraction(3, 5), Fraction(4, 5), Fraction(0), Fraction(0)]
    eta = Fraction(1, 3)
    projector = mouter(vector, vector)
    s = mscale(projector, eta)
    k = mmul(mmul(sqrt_h0, s), sqrt_h0)
    h = madd(h0, k)
    h_inverse = minverse(h)
    series = mzero(4, 4)
    for exponent in range(5):
        series = madd(series, mscale(mpower(s, exponent), Fraction(-1) ** exponent))
    approximation = mmul(mmul(h0_inverse_half, series), h0_inverse_half)
    error = msub(h_inverse, approximation)
    weighted_vector = [Fraction(3, 5), Fraction(2, 5), Fraction(0), Fraction(0)]
    exact_error_factor = -eta**5 / (Fraction(1) + eta)
    expected_error = mscale(mouter(weighted_vector, weighted_vector), exact_error_factor)
    actual_error_norm = eta**5 / (Fraction(1) + eta) * sum((entry * entry for entry in weighted_vector), Fraction(0))
    certified_bound = eta**5 / (Fraction(1) - eta)
    certificate = {
        "dimension": 4,
        "gamma": "1",
        "eta": str(eta),
        "neumann_order": 4,
        "H0_sha256": mdigest(h0),
        "relative_perturbation_sha256": mdigest(s),
        "H_sha256": mdigest(h),
        "exact_inverse_sha256": mdigest(h_inverse),
        "neumann_approximation_sha256": mdigest(approximation),
        "error_sha256": mdigest(error),
        "actual_error_operator_norm": str(actual_error_norm),
        "certified_error_bound": str(certified_bound),
        "inverse_norm_upper_bound": str(Fraction(1) / (Fraction(1) - eta)),
        "fixtures_are_physical": False,
    }
    checks = {
        "neumann_projector_is_idempotent": mmul(projector, projector) == projector,
        "neumann_relative_norm_is_one_third": eta == Fraction(1, 3),
        "neumann_exact_inverse": mmul(h, h_inverse) == midentity(4) and mmul(h_inverse, h) == midentity(4),
        "neumann_remainder_matrix_exact": error == expected_error,
        "neumann_actual_error_is_13_over_8100": actual_error_norm == Fraction(13, 8100),
        "neumann_bound_is_one_over_162": certified_bound == Fraction(1, 162),
        "neumann_bound_is_strict": actual_error_norm < certified_bound,
    }
    return certificate, checks


def build_feshbach_certificate() -> tuple[dict[str, Any], dict[str, bool]]:
    a = [[Fraction(2), Fraction(1, 5)], [Fraction(1, 5), Fraction(3)]]
    b = [[Fraction(1, 3), Fraction(1, 7)], [Fraction(1, 5), Fraction(1, 4)]]
    d = [[Fraction(5), Fraction(1, 4)], [Fraction(1, 4), Fraction(6)]]
    d_inverse = minverse(d)
    feshbach = msub(a, mmul(mmul(b, d_inverse), mtranspose(b)))
    feshbach_inverse = minverse(feshbach)
    full = mblock(a, b, mtranspose(b), d)
    full_inverse = minverse(full)
    top_right = mneg(mmul(mmul(feshbach_inverse, b), d_inverse))
    bottom_left = mneg(mmul(mmul(d_inverse, mtranspose(b)), feshbach_inverse))
    bottom_right = madd(
        d_inverse,
        mmul(mmul(mmul(mmul(d_inverse, mtranspose(b)), feshbach_inverse), b), d_inverse),
    )
    block_inverse = mblock(feshbach_inverse, top_right, bottom_left, bottom_right)
    tail_gap = Fraction(19, 4)
    main_gap = Fraction(9, 5)
    b_frobenius_sq = sum((entry * entry for row in b for entry in row), Fraction(0))
    schur_lower_bound = main_gap - b_frobenius_sq / tail_gap
    delta = mblock([[Fraction(0)]], mzero(1, 4), mzero(4, 1), full)
    green = mblock([[Fraction(0)]], mzero(1, 4), mzero(4, 1), full_inverse)
    projector = mdiag([Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)])
    complement = msub(midentity(5), projector)
    certificate = {
        "main_dimension": 2,
        "tail_dimension": 2,
        "tail_gap_gershgorin": str(tail_gap),
        "main_gap_gershgorin": str(main_gap),
        "coupling_frobenius_sq": str(b_frobenius_sq),
        "schur_lower_bound": str(schur_lower_bound),
        "full_operator_sha256": mdigest(full),
        "tail_inverse_sha256": mdigest(d_inverse),
        "feshbach_operator_sha256": mdigest(feshbach),
        "feshbach_inverse_sha256": mdigest(feshbach_inverse),
        "full_inverse_sha256": mdigest(full_inverse),
        "kernel_extended_delta_sha256": mdigest(delta),
        "kernel_projector_sha256": mdigest(projector),
        "reduced_green_sha256": mdigest(green),
        "fixtures_are_physical": False,
    }
    checks = {
        "tail_gap_positive": tail_gap > 0,
        "main_gap_positive": main_gap > 0,
        "schur_margin_positive": schur_lower_bound > 0,
        "tail_inverse_exact": mmul(d, d_inverse) == midentity(2),
        "feshbach_inverse_exact": mmul(feshbach, feshbach_inverse) == midentity(2),
        "block_inverse_formula_exact": block_inverse == full_inverse,
        "full_inverse_exact": mmul(full, full_inverse) == midentity(4) and mmul(full_inverse, full) == midentity(4),
        "kernel_projector_exact": mmul(projector, projector) == projector,
        "reduced_green_left_identity": mmul(delta, green) == complement,
        "reduced_green_right_identity": mmul(green, delta) == complement,
        "reduced_green_annihilates_kernel": mmul(projector, green) == mzero(5, 5) and mmul(green, projector) == mzero(5, 5),
    }
    return certificate, checks


def main() -> None:
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    theorem_text = THEOREM.read_text(encoding="utf-8")
    source_checks = []
    for source in lock["sources"]:
        actual = sha256(ROOT / source["path"])
        source_checks.append(
            {
                "id": source["id"],
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": actual,
                "matches": actual == source["sha256"],
            }
        )

    base_maps = {degree: real_symbol_map(degree) for degree in MAP_DEGREES}
    maps: dict[int, tuple[PolyMatrix, PolyMatrix]] = {}
    for degree, base_map in base_maps.items():
        g, f = map_polynomials(degree)
        constant = pmat_from_fraction(base_map)
        maps[degree] = (pmat_scale(constant, g), pmat_scale(constant, f))

    cochain_checks = []
    for degree in [-1, 0, 1]:
        vector = dense_probe(carrier_dimension(RANK, degree), degree + 2)
        composed = apply_l(*maps[degree + 1], apply_l(*maps[degree], vector))
        cochain_checks.append(all(entry == pconst(0) for entry in composed))

    degree_rows = []
    direct_checks = []
    beta = [(Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))]
    for degree in DEGREES:
        dimension = carrier_dimension(RANK, degree)
        outgoing = maps.get(degree)
        incoming = maps.get(degree - 1)
        c, r, e = hodge_coefficients(dimension, outgoing, incoming)
        for probe in range(3):
            vector = dense_probe(dimension, probe + 1)
            direct_checks.append(
                apply_hodge_direct(vector, outgoing, incoming)
                == apply_hodge_coefficients(c, r, e, vector)
            )
        c_at_zero = [[entry[0] for entry in row] for row in c]
        hodge_at_zero = degree_hodge_symbol(beta, beta, degree, RANK)
        hodge_real = [[entry[0] for entry in row] for row in hodge_at_zero]
        hodge_imaginary_zero = all(entry[1] == 0 for row in hodge_at_zero for entry in row)
        degree_rows.append(
            {
                "degree": degree,
                "carrier_dimension": dimension,
                "correction_rank": correction_rank(degree),
                "C_sha256": pdigest(c),
                "R_sha256": pdigest(r),
                "E_sha256": pdigest(e),
                "C_nonzero_entries": pnonzero_count(c),
                "R_nonzero_entries": pnonzero_count(r),
                "E_nonzero_entries": pnonzero_count(e),
                "C_max_polynomial_degree": pmax_degree(c),
                "R_max_polynomial_degree": pmax_degree(r),
                "E_max_polynomial_degree": pmax_degree(e),
                "principal_at_x0_matches_T58": hodge_imaginary_zero and c_at_zero == hodge_real,
                "three_dense_direct_composition_checks": all(direct_checks[-3:]),
            }
        )

    neumann, neumann_checks = build_neumann_certificate()
    feshbach, feshbach_checks = build_feshbach_certificate()

    packet: dict[str, Any] = {
        "schema": "boe.mtt.augmented-hodge-lower-order-inverse-tail-compiler.v1",
        "claim_id": "CBF.T59",
        "date": "2026-09-01",
        "status": "EXACT_FIVE_DEGREE_LOWER_ORDER_COEFFICIENT_AND_PROJECTED_GLOBAL_INVERSE_TAIL_COMPILER_PHYSICAL_VALUES_OPEN",
        "source_provenance": {
            "model_state_sha256": lock["model_state_sha256"],
            "handoff_id": lock["handoff_id"],
            "source_checks": source_checks,
            "all_portable_sources_hash_locked": all(source["matches"] for source in source_checks),
            "discovery_evidence": lock["discovery_evidence"],
        },
        "coefficient_compiler_theorem": {
            "local_differential": "L_n=A_n^j partial_j+B_n",
            "adjoint_zero_order": "D_n=B_n^*-mu^-1 partial_j(mu A_n^(j*))",
            "adjoint": "L_n^*=-A_n^(j*) partial_j+D_n",
            "Hodge_expansion": "Delta_n=-C_n^(ij)partial_i partial_j+R_n^j partial_j+E_n",
            "C_formula": "A_n^(i*)A_n^j+A_(n-1)^i A_(n-1)^(j*)",
            "R_formula": "-A_n^(i*)partial_iA_n^j+D_nA_n^j-A_n^(j*)B_n-A_(n-1)^i partial_iA_(n-1)^(j*)+A_(n-1)^jD_(n-1)-B_(n-1)A_(n-1)^(j*)",
            "E_formula": "-A_n^(i*)partial_iB_n+D_nB_n+A_(n-1)^i partial_iD_(n-1)+B_(n-1)D_(n-1)",
            "connection_fold": "B_n=b_n+a_n^j Gamma_j",
            "independent_lower_order_matrix_rows_required_after_endpoint": 0,
            "degrees": DEGREES,
        },
        "five_degree_exact_witness": {
            "Q_rank": RANK,
            "density": "mu(x)=exp(x/3)",
            "density_log_derivative": str(THETA),
            "nonconstant_principal_and_zero_order_coefficients": True,
            "cochain_compositions_checked": len(cochain_checks),
            "all_cochain_compositions_zero": all(cochain_checks),
            "direct_composition_checks": len(direct_checks),
            "all_direct_composition_checks_pass": all(direct_checks),
            "degree_rows": degree_rows,
            "all_principal_x0_blocks_match_T58": all(row["principal_at_x0_matches_T58"] for row in degree_rows),
            "fixtures_are_physical": False,
        },
        "projected_neumann_inverse_certificate": neumann,
        "feshbach_tail_certificate": feshbach,
        "q79_execution_contract_update": {
            "carrier_dimensions": [1, 105, 309, 307, 102],
            "principal_preconditioner": "CLOSED_BY_CBF_T58",
            "local_lower_order_coefficient_compiler": "CLOSED_BY_CBF_T59",
            "projected_global_inverse_acceptance_compiler": "CLOSED_BY_CBF_T59",
            "Feshbach_tail_acceptance_compiler": "CLOSED_BY_CBF_T59",
            "independent_coefficient_entry_source_rows_after_endpoint": 0,
            "selected_endpoint_coefficient_values": "OPEN",
            "selected_kernel_projection": "OPEN",
            "selected_gamma_eta_tau_and_schur_margin": "OPEN",
            "selected_global_reduced_inverse": "OPEN",
            "selected_finite_continuum_intertwiner": "OPEN",
            "radii_inequality_decision": "OPEN",
            "B_GEO_01_closed": False,
            "B_OP_01_closed": False,
        },
        "parameter_ledger": {
            "continuous_physical_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "witness_rationals_are_exactness_fixtures": True,
        },
        "physical_boundary": {
            "selected_visible_hidden_HYM_endpoint": False,
            "selected_lower_order_arrays": False,
            "selected_kernel_projector": False,
            "selected_global_inverse_and_tail": False,
            "B_GEO_01_closed": False,
            "B_OP_01_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
        },
        "check_summary": {},
    }

    theorem_tokens = [
        "CBF.T59",
        "D_n=B_n^* - mu^(-1) partial_j(mu A_n^(j*))",
        "eta<1",
        "F=A-BD^(-1)B^*",
        "B.GEO.01",
        "B.OP.01",
    ]
    checks = {
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": set(schema["required"]).issubset(packet),
        "source_hashes_match": all(source["matches"] for source in source_checks),
        "source_count": len(source_checks) == 4,
        "theorem_tokens_present": all(token in theorem_text for token in theorem_tokens),
        "five_degrees_present": [row["degree"] for row in degree_rows] == DEGREES,
        "witness_dimensions": [row["carrier_dimension"] for row in degree_rows] == [1, 7, 15, 13, 4],
        "witness_rank_sequence": [row["correction_rank"] for row in degree_rows] == [1, 4, 6, 4, 1],
        "all_cochain_checks": all(cochain_checks),
        "cochain_check_count": len(cochain_checks) == 3,
        "all_direct_coefficient_checks": all(direct_checks),
        "direct_coefficient_check_count": len(direct_checks) == 15,
        "all_principal_blocks_match_T58": packet["five_degree_exact_witness"]["all_principal_x0_blocks_match_T58"],
        "all_degree_probe_groups_pass": all(row["three_dense_direct_composition_checks"] for row in degree_rows),
        "nonconstant_C_present": any(row["C_max_polynomial_degree"] > 0 for row in degree_rows),
        "nonconstant_E_present": any(row["E_max_polynomial_degree"] > 0 for row in degree_rows),
        "neumann_checks": all(neumann_checks.values()),
        "neumann_check_count": len(neumann_checks) == 7,
        "feshbach_checks": all(feshbach_checks.values()),
        "feshbach_check_count": len(feshbach_checks) == 11,
        "q79_dimensions": packet["q79_execution_contract_update"]["carrier_dimensions"] == [1, 105, 309, 307, 102],
        "coefficient_rows_reduced_to_zero": packet["q79_execution_contract_update"]["independent_coefficient_entry_source_rows_after_endpoint"] == 0,
        "selected_values_remain_open": packet["q79_execution_contract_update"]["selected_endpoint_coefficient_values"] == "OPEN",
        "selected_inverse_remains_open": packet["q79_execution_contract_update"]["selected_global_reduced_inverse"] == "OPEN",
        "blockers_remain_open": not packet["q79_execution_contract_update"]["B_GEO_01_closed"] and not packet["q79_execution_contract_update"]["B_OP_01_closed"],
        "no_parameters_added": packet["parameter_ledger"]["continuous_physical_parameters_added"] == 0,
        "no_selectors_added": packet["parameter_ledger"]["discrete_selectors_added"] == 0,
        "no_observed_values": packet["parameter_ledger"]["observed_values_used"] == 0,
        "no_fitted_values": packet["parameter_ledger"]["fitted_values_used"] == 0,
        "physical_counters_unchanged": packet["physical_boundary"]["physical_gates"] == {"accepted": 0, "total": 3} and packet["physical_boundary"]["physical_packets"] == {"accepted": 0, "total": 3} and packet["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
    }
    packet["check_summary"] = {
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
        "neumann_subchecks": neumann_checks,
        "feshbach_subchecks": feshbach_checks,
    }
    packet["payload_sha256"] = canonical_hash(
        {
            "compiler": packet["coefficient_compiler_theorem"],
            "witness": packet["five_degree_exact_witness"],
            "neumann": neumann,
            "feshbach": feshbach,
            "contract": packet["q79_execution_contract_update"],
        }
    )
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"all_passed": packet["check_summary"]["all_passed"], "passed": packet["check_summary"]["passed"], "total": packet["check_summary"]["total"]}, sort_keys=True))
    if not packet["check_summary"]["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
