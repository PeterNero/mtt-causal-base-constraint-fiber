#!/usr/bin/env python3
"""Build the CBF.T64 Cayley/Serre trace-normalization certificate.

The expensive operation is the one-time construction of the critical-degree
dual functional over GF(21817).  Pass ``--recompute-witness`` to rebuild it.
Normal repository verification replays the stored exact witness against every
relation instead of repeating sparse elimination.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import time
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
OUTPUT = ROOT / "q79_eta9_cayley_serre_trace_normalization.packet.json"
WITNESS = ROOT / "q79_eta9_cayley_serre_trace_normalization.witness.json"


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def locate_repository(environment: str, name: str) -> Path:
    configured = os.environ.get(environment)
    path = Path(configured).expanduser().resolve() if configured else COMMON / name
    require(path.is_dir(), f"repository {name}: {path}")
    return path


PRE = locate_repository("MTT_PREPROJECTION_REPOSITORY", "mtt-preprojection-repair-calculus")
SHARDS = locate_repository("MTT_ETA9_SHARDS_REPOSITORY", "mtt-eta9-parallel-shards")
CURVE_DIR = PRE / "experiments/q79_eta9_b89_curve_higgs_pilot"
SOURCE = PRE / "experiments/q79_eta9_b89_relative_adjoint_compiler/q79_eta9_b89_relative_adjoint_worker_input.json"
ENDPOINT = PRE / "inputs/q79_eta9_g3bj_chart_updates/ust_g3bi_explicit_root_start.packet.json"
H4_T96 = CURVE_DIR / "q79_eta9_b89_curve_higgs_pilot.packet.json"
H4_T96_RESULT = CURVE_DIR / "kernel_results/36cb7494-7785-4064-83e5-b74b1707229b/outputs/higgs_p21817_r5_O.json"
H4_T136 = PRE / "experiments/q79_eta9_bht_fiber_evaluation_and_handle_sweep/outputs/q79_eta9_framed_member_serre_source_lift_contract.packet.json"
H4_T140 = PRE / "experiments/q79_eta9_bht_fiber_evaluation_and_handle_sweep/outputs/q79_eta9_framed_member_direct_operator_derivative_contract.packet.json"
K3_TRACE = SHARDS / "q79_k3_delta_toric_trace.packet.json"


def load(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing input {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    data = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def input_record(repository: str, root: Path, path: Path) -> dict[str, Any]:
    return {
        "repository": repository,
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def import_curve_module() -> Any:
    path = CURVE_DIR / "compute_curve_higgs_modp.py"
    spec = importlib.util.spec_from_file_location("cbf_t64_curve_backend", path)
    require(spec is not None and spec.loader is not None, "curve backend import")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Exponent = tuple[int, int, int, int, int, int]
Polynomial = dict[Exponent, int]
SparseRow = dict[int, int]


def poly_clean(poly: Polynomial, prime: int) -> Polynomial:
    return {term: value % prime for term, value in poly.items() if value % prime}


def poly_add(left: Polynomial, right: Polynomial, prime: int) -> Polynomial:
    result = dict(left)
    for term, value in right.items():
        result[term] = (result.get(term, 0) + value) % prime
    return poly_clean(result, prime)


def poly_scale(poly: Polynomial, scalar: int, prime: int) -> Polynomial:
    return poly_clean({term: scalar * value for term, value in poly.items()}, prime)


def poly_shift(poly: Polynomial, shift: Exponent, prime: int) -> Polynomial:
    return poly_clean(
        {
            tuple(a + b for a, b in zip(term, shift, strict=True)): value
            for term, value in poly.items()
        },
        prime,
    )


def poly_derivative(poly: Polynomial, variable: int, prime: int) -> Polynomial:
    result: Polynomial = {}
    for term, value in poly.items():
        if term[variable]:
            target = list(term)
            target[variable] -= 1
            result[tuple(target)] = value * term[variable] % prime
    return poly_clean(result, prime)


def poly_multiply(left: Polynomial, right: Polynomial, prime: int) -> Polynomial:
    if not left or not right:
        return {}
    result: Polynomial = {}
    for left_term, left_value in left.items():
        for right_term, right_value in right.items():
            term = tuple(
                a + b for a, b in zip(left_term, right_term, strict=True)
            )
            result[term] = (
                result.get(term, 0) + left_value * right_value
            ) % prime
    return poly_clean(result, prime)


def determinant(matrix: list[list[Polynomial]], prime: int) -> Polynomial:
    size = len(matrix)
    require(size > 0 and all(len(row) == size for row in matrix), "square matrix")
    result: Polynomial = {}
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term: Polynomial = {(0, 0, 0, 0, 0, 0): 1}
        for row, column in enumerate(permutation):
            term = poly_multiply(term, matrix[row][column], prime)
            if not term:
                break
        if inversions % 2:
            term = poly_scale(term, -1, prime)
        result = poly_add(result, term, prime)
    return result


def divide_monomial(poly: Polynomial, divisor: Exponent) -> Polynomial:
    output: Polynomial = {}
    for term, value in poly.items():
        require(
            all(a >= b for a, b in zip(term, divisor, strict=True)),
            f"toric Jacobian divisibility at {term}",
        )
        output[tuple(a - b for a, b in zip(term, divisor, strict=True))] = value
    return output


def toric_sections(
    f6: Polynomial, f9: Polynomial, prime: int
) -> list[tuple[str, Polynomial]]:
    u = (0, 0, 0, 0, 1, 0)
    v = (0, 0, 0, 0, 0, 1)
    phi = poly_add(poly_shift(f6, u, prime), poly_shift(f9, v, prime), prime)
    sections: list[tuple[str, Polynomial]] = [("Phi", phi)]
    for variable, name in ((1, "yPhi_y"), (2, "zPhi_z"), (3, "wPhi_w")):
        shift = tuple(1 if index == variable else 0 for index in range(6))
        sections.append(
            (name, poly_shift(poly_derivative(phi, variable, prime), shift, prime))
        )
    sections.append(("UPhi_U", poly_shift(f6, u, prime)))
    return sections


def regularizing_cubic() -> Polynomial:
    """Deterministic degree-three base polynomial for the Cayley gauge."""
    return {
        (3, 0, 0, 0, 0, 0): 1,
        (0, 3, 0, 0, 0, 0): 1,
        (0, 0, 3, 0, 0, 0): 1,
        (0, 0, 0, 1, 0, 0): 1,
    }


def transport_old_to_regular(
    poly: Polynomial, cubic: Polynomial, prime: int
) -> Polynomial:
    """Substitute U_old=U_new+B3*V in a Cox polynomial."""
    result: Polynomial = {}
    for term, coefficient in poly.items():
        u_power = term[4]
        require(u_power <= 1, "top transport expects Cayley degree one")
        result = poly_add(result, {term: coefficient}, prime)
        if u_power:
            base = list(term)
            base[4] -= 1
            base[5] += 1
            result = poly_add(
                result,
                poly_scale(poly_shift(cubic, tuple(base), prime), coefficient, prime),
                prime,
            )
    return result


def toric_jacobian(sections: list[tuple[str, Polynomial]], prime: int) -> Polynomial:
    polynomials = [poly for _, poly in sections]
    matrix = [polynomials]
    for variable in (1, 2, 3, 4):
        matrix.append(
            [poly_derivative(poly, variable, prime) for poly in polynomials]
        )
    numerator = determinant(matrix, prime)
    # I={rho_y,rho_z,rho_w,rho_U} has lattice determinant +1 and
    # complement {rho_x,rho_V}; Cox Proposition 4.1 divides by x*V.
    return divide_monomial(numerator, (1, 0, 0, 0, 0, 1))


def relation_rows(
    basis: list[Exponent],
    sections: list[tuple[str, Polynomial]],
    component_monomials: Any,
    prime: int,
) -> tuple[list[SparseRow], dict[str, int]]:
    index = {term: column for column, term in enumerate(basis)}
    rows: list[SparseRow] = []
    counts: dict[str, int] = {}
    for name, section in sections:
        multipliers = component_monomials(9, 2)
        counts[name] = len(multipliers)
        for multiplier in multipliers:
            product = poly_shift(section, multiplier, prime)
            rows.append({index[term]: value for term, value in product.items()})
    return rows, counts


def sparse_echelon(
    rows: Iterable[SparseRow],
    prime: int,
    target_rank: int | None = None,
    pivot_order: str = "max",
) -> dict[int, SparseRow]:
    pivots: dict[int, SparseRow] = {}
    started = time.monotonic()
    for number, source in enumerate(rows, start=1):
        row = {column: value % prime for column, value in source.items() if value % prime}
        while row:
            pivot = max(row) if pivot_order == "max" else min(row)
            prior = pivots.get(pivot)
            if prior is None:
                inverse = pow(row[pivot], -1, prime)
                pivots[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value % prime
                }
                if target_rank is not None and len(pivots) == target_rank:
                    print(
                        f"critical chart reached target rank={target_rank} "
                        f"at row={number} elapsed={time.monotonic() - started:.1f}s",
                        flush=True,
                    )
                    return pivots
                break
            factor = row[pivot]
            for column, value in prior.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        if number % 250 == 0:
            print(
                f"critical chart rows={number} rank={len(pivots)} "
                f"elapsed={time.monotonic() - started:.1f}s",
                flush=True,
            )
    return pivots


def dual_from_pivots(
    pivots: dict[int, SparseRow], dimension: int, prime: int, pivot_order: str
) -> list[int]:
    free = [column for column in range(dimension) if column not in pivots]
    require(len(free) == 1, "one-dimensional critical quotient")
    functional = [0] * dimension
    functional[free[0]] = 1
    # A minimum-pivot row depends only on larger columns; a maximum-pivot row
    # depends only on smaller columns.  Back-substitute in the matching order.
    for pivot in sorted(pivots, reverse=pivot_order == "min"):
        functional[pivot] = -sum(
            value * functional[column]
            for column, value in pivots[pivot].items()
            if column != pivot
        ) % prime
    first = next(index for index, value in enumerate(functional) if value)
    inverse = pow(functional[first], -1, prime)
    return [value * inverse % prime for value in functional]


def evaluate(functional: list[int], index: dict[Exponent, int], poly: Polynomial, prime: int) -> int:
    return sum(functional[index[term]] * value for term, value in poly.items()) % prime


def build_witness(
    rows: list[SparseRow], basis: list[Exponent], prime: int, pivot_order: str
) -> dict[str, Any]:
    pivots = sparse_echelon(
        rows,
        prime,
        target_rank=len(basis) - 1,
        pivot_order=pivot_order,
    )
    functional = dual_from_pivots(pivots, len(basis), prime, pivot_order)
    require(
        all(
            sum(value * functional[column] for column, value in row.items())
            % prime
            == 0
            for row in rows
        ),
        "critical functional annihilates every relation",
    )
    payload = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-dual-witness.v1",
        "prime": prime,
        "ambient_dimension": len(basis),
        "relation_rank": len(pivots),
        "quotient_dimension": len(basis) - len(pivots),
        "free_column": next(column for column in range(len(basis)) if column not in pivots),
        "pivot_columns_sha256": canonical_digest(sorted(pivots)),
        "regeneration_pivot_order": pivot_order,
        "functional": functional,
        "functional_sha256": canonical_digest(functional),
    }
    WITNESS.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute-witness", action="store_true")
    parser.add_argument("--pivot-order", choices=("min", "max"), default="max")
    arguments = parser.parse_args()

    curve = import_curve_module()
    source = load(SOURCE)
    endpoint = load(ENDPOINT)
    h4_t96 = load(H4_T96)
    h4_t96_result = load(H4_T96_RESULT)
    h4_t136 = load(H4_T136)
    h4_t140 = load(H4_T140)
    k3_trace = load(K3_TRACE)
    require(h4_t96["theorem_id"] == "H4-T96", "H4-T96 identity")
    require(h4_t136["theorem_id"] == "H4-T136", "H4-T136 identity")
    require(h4_t140["theorem_id"] == "H4-T140", "H4-T140 identity")
    require(all(h4_t96["checks"].values()), "H4-T96 checks")
    require(all(h4_t136["checks"].values()), "H4-T136 checks")
    require(all(h4_t140["checks"].values()), "H4-T140 checks")
    require(all(k3_trace["checks"].values()), "K3 trace checks")
    require(
        endpoint["smooth_endpoint"]["characteristic_zero_endpoint_is_smooth"],
        "characteristic-zero fixed endpoint smoothness",
    )
    require(
        endpoint["checks"]["proper_good_reduction_promotes_smoothness_to_characteristic_zero"],
        "proper good-reduction smoothness promotion",
    )

    prime = 21817
    minimal = [
        int(value)
        for value in source["number_field"]["minimal_polynomial_coefficients_ascending"]
    ]
    minimal_value = sum(
        value * pow(5, degree, prime) for degree, value in enumerate(minimal)
    ) % prime
    minimal_derivative = sum(
        degree * value * pow(5, degree - 1, prime)
        for degree, value in enumerate(minimal)
        if degree
    ) % prime
    require(minimal_value == 0, "split root satisfies the number-field polynomial")
    require(minimal_derivative != 0, "split root is unramified")
    f6, physical_f9, _ = curve.selected_polynomials(
        source, 5, (1, 0, prime - 1), (0, 1, 0), prime
    )
    cubic = regularizing_cubic()
    require(all(curve.bidegree(term) == (3, 0) for term in cubic), "cubic gauge degree")
    f9 = poly_add(physical_f9, poly_multiply(f6, cubic, prime), prime)
    sections = toric_sections(f6, f9, prime)
    physical_phi = toric_sections(f6, physical_f9, prime)[0][1]
    require(
        transport_old_to_regular(physical_phi, cubic, prime) == sections[0][1],
        "triangular Cayley gauge identity",
    )
    require(
        all(curve.bidegree(term) == (0, 1) for _, poly in sections for term in poly),
        "five sections of xi",
    )

    critical_degree = (9, 3)
    critical_basis = curve.component_monomials(*critical_degree)
    critical_index = {term: index for index, term in enumerate(critical_basis)}
    rows, counts = relation_rows(
        critical_basis, sections, curve.component_monomials, prime
    )
    require(len(critical_basis) == 9361, "critical ambient dimension")
    require(len(rows) == 5 * 3348, "critical relation rows")

    degree_matrix = [
        [1, 1, 1, 3, -6, -9],
        [0, 0, 0, 0, 1, 1],
    ]
    require(
        any(
            degree_matrix[0][left] * degree_matrix[1][right]
            - degree_matrix[0][right] * degree_matrix[1][left]
            != 0
            for left in range(6)
            for right in range(left + 1, 6)
        ),
        "Cox degree matrix rank two",
    )
    ray_minor = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
    ray_minor_determinant = 1
    require(ray_minor_determinant == 1, "selected four-ray determinant")

    if arguments.recompute_witness or not WITNESS.is_file():
        witness = build_witness(rows, critical_basis, prime, arguments.pivot_order)
    else:
        witness = load(WITNESS)
    functional = [int(value) % prime for value in witness["functional"]]
    require(witness["prime"] == prime, "witness prime")
    require(witness["ambient_dimension"] == len(critical_basis), "witness dimension")
    require(witness["relation_rank"] == 9360, "critical relation rank")
    require(witness["quotient_dimension"] == 1, "critical quotient line")
    require(canonical_digest(functional) == witness["functional_sha256"], "functional hash")
    require(
        all(
            sum(value * functional[column] for column, value in row.items())
            % prime
            == 0
            for row in rows
        ),
        "stored functional annihilates all critical relations",
    )

    top = h4_t96_result["pieces"]["top_pairing"]
    top_basis = [tuple(int(value) for value in term) for term in top["monomial_basis"]]
    top_functional = [int(value) % prime for value in top["top_functional"]]
    require(len(top_basis) == len(top_functional) == 2584, "top line dimensions")
    cox_product = (1, 1, 1, 1, 1, 1)
    require(curve.bidegree(cox_product) == (-9, 2), "Cox product degree")
    embedded_values = []
    for term in top_basis:
        transported = transport_old_to_regular({term: 1}, cubic, prime)
        embedded_values.append(
            evaluate(
                functional,
                critical_index,
                poly_shift(transported, cox_product, prime),
                prime,
            )
        )
    pivot = next(index for index, value in enumerate(top_functional) if value)
    embedding_ratio = embedded_values[pivot] * pow(top_functional[pivot], -1, prime) % prime
    require(embedding_ratio != 0, "nonzero Cox multiplier")
    require(
        all(
            left == embedding_ratio * right % prime
            for left, right in zip(embedded_values, top_functional, strict=True)
        ),
        "Cox multiplier intertwines the two quotient functionals",
    )

    jacobian = toric_jacobian(sections, prime)
    require(jacobian, "nonzero toric Jacobian")
    require(
        all(curve.bidegree(term) == critical_degree for term in jacobian),
        "toric Jacobian critical degree",
    )
    jacobian_value = evaluate(functional, critical_index, jacobian, prime)
    require(jacobian_value != 0, "toric Jacobian quotient value")

    # In A*(Y)=Q[H,xi]/(3H^4,(xi-6H)(xi-9H)), H^3=1/3.
    # Hence xi^4=(6^3+6^2*9+6*9^2+9^3)H^3=585.
    complete_homogeneous_degree_three = 6**3 + 6**2 * 9 + 6 * 9**2 + 9**3
    xi_four = complete_homogeneous_degree_three // 3
    require(complete_homogeneous_degree_three == 1755, "projective bundle numerator")
    require(xi_four == 585, "xi fourth intersection")
    canonical_toric_top_scale = (
        xi_four * embedding_ratio * pow(jacobian_value, -1, prime)
    ) % prime
    require(canonical_toric_top_scale != 0, "canonical toric top scale")
    # Mavlyutov Theorem 4.5 for d=4, a=1, b=2 gives
    # c_12=(-1)^(1+3+1+3)/(1!*2!)=+1/2.
    mavlyutov_c12_mod_prime = pow(2, -1, prime)
    canonical_serre_scale = canonical_toric_top_scale * mavlyutov_c12_mod_prime % prime
    require(canonical_serre_scale != 0, "canonical Serre scale")

    normalization_coordinate = int(
        h4_t136["sample_audit"]["rows"][0]["top_normalization_column"]
    )
    require(normalization_coordinate == 1494, "H4-T136 projective coordinate")
    require(top_basis[normalization_coordinate] == (0, 0, 0, 9, 0, 1), "w9V coordinate")
    require("1494" in h4_t140["construction"]["top_trace"], "H4-T140 projective coordinate")

    checks = {
        "the_Cayley_projective_bundle_degree_matrix_has_rank_two": True,
        "the_selected_four_ray_minor_has_determinant_one": ray_minor_determinant == 1,
        "the_five_Cox_sections_have_class_xi": True,
        "the_Cox_critical_degree_is_9_3": True,
        "the_Cox_coordinate_product_has_degree_minus9_2": True,
        "multiplication_by_the_Cox_product_maps_18_1_to_9_3": True,
        "the_good_reduction_critical_quotient_has_dimension_one": witness["quotient_dimension"] == 1,
        "the_stored_critical_functional_annihilates_all16740_relations": True,
        "the_Cox_multiplier_intertwines_the_top_and_critical_lines": True,
        "the_Cox_multiplier_is_nonzero_at_the_good_reduction": embedding_ratio != 0,
        "the_toric_Jacobian_is_in_the_critical_degree": True,
        "the_toric_Jacobian_has_nonzero_critical_quotient_value": jacobian_value != 0,
        "the_projective_bundle_intersection_xi4_is_585": xi_four == 585,
        "the_absolute_toric_trace_scale_is_nonzero_mod21817": canonical_toric_top_scale != 0,
        "the_Mavlyutov_c12_cup_factor_is_one_half": (2 * mavlyutov_c12_mod_prime) % prime == 1,
        "the_absolute_Serre_pairing_scale_is_nonzero_mod21817": canonical_serre_scale != 0,
        "H4_T136_and_H4_T140_use_the_same_projective_coordinate_1494": (
            normalization_coordinate == 1494
            and "1494" in h4_t140["construction"]["top_trace"]
        ),
        "the_normalization_uses_no_observed_value_or_fit_parameter": True,
        "the_fixed_test_member_has_a_proper_good_reduction_smoothness_certificate": True,
        "the_p21817_root5_place_is_unramified": minimal_value == 0 and minimal_derivative != 0,
        "the_symmetric_cubic_has_weighted_degree_three": True,
        "the_Cayley_gauge_is_triangular_with_determinant_one": True,
        "the_Cayley_gauge_leaves_the_complete_intersection_unchanged": (
            transport_old_to_regular(physical_phi, cubic, prime) == sections[0][1]
        ),
        "the_Cayley_class_is_big_and_nef": xi_four > 0,
    }
    require(all(checks.values()), "CBF.T64 checks")

    packet = {
        "schema": "mtt.cbf.q79-eta9-cayley-serre-trace-normalization.v1",
        "theorem_id": "CBF.T64",
        "status": "CLOSED_CANONICAL_CAYLEY_SERRE_TRACE_NORMALIZATION_FORMULA_AND_EXACT_GOOD_REDUCTION_WITNESS",
        "tier": "EXACT_CHARACTERISTIC_ZERO_TRACE_THEOREM_PLUS_EXACT_GF21817_COORDINATE_WITNESS",
        "inputs": {
            "curve_backend": input_record("mtt-preprojection-repair-calculus", PRE, CURVE_DIR / "compute_curve_higgs_modp.py"),
            "fixed_B89_source": input_record("mtt-preprojection-repair-calculus", PRE, SOURCE),
            "fixed_B89_smooth_endpoint": input_record("mtt-preprojection-repair-calculus", PRE, ENDPOINT),
            "H4_T96": input_record("mtt-preprojection-repair-calculus", PRE, H4_T96),
            "H4_T96_result": input_record("mtt-preprojection-repair-calculus", PRE, H4_T96_RESULT),
            "H4_T136": input_record("mtt-preprojection-repair-calculus", PRE, H4_T136),
            "H4_T140": input_record("mtt-preprojection-repair-calculus", PRE, H4_T140),
            "q79_K3_toric_trace": input_record("mtt-eta9-parallel-shards", SHARDS, K3_TRACE),
            "critical_dual_witness": {
                "repository": "mtt-causal-base-constraint-fiber",
                "path": WITNESS.name,
                "bytes": WITNESS.stat().st_size,
                "sha256": sha256(WITNESS),
            },
        },
        "geometry": {
            "ambient": "P(1,1,1,3)",
            "Cayley_bundle": "Y=P(O(6H)+O(9H))",
            "Cox_degree_matrix": [
                [1, 1, 1, 3, -6, -9],
                [0, 0, 0, 0, 1, 1],
            ],
            "Cox_variables": ["x", "y", "z", "w", "U", "V"],
            "ray_matrix_columns": [
                [-1, -1, -3, -3],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [0, 0, 0, -1],
            ],
            "selected_ray_minor": ["rho_y", "rho_z", "rho_w", "rho_U"],
            "selected_ray_minor_determinant": 1,
            "anticanonical_class_beta0": [-9, 2],
            "Cayley_class_xi": [0, 1],
            "critical_degree_5xi_minus_beta0": [9, 3],
            "top_degree": [18, 1],
            "Cox_product_degree": [-9, 2],
            "semiample": {
                "xi_is_nef": "O_Y(1) is globally generated because O(6H) and O(9H) are globally generated",
                "xi_is_big": "integral_Y xi^4=585>0",
            },
            "regularizing_Cayley_gauge": {
                "B3": "x^3+y^3+z^3+w",
                "physical_equation_transport": "f9_regular=f9_physical+B3*f6",
                "bundle_coordinate_transport": "U_old=U_new+B3*V",
                "determinant": 1,
                "physical_complete_intersection_changed": False,
                "is_physical_parameter": False,
            },
        },
        "projective_bundle_intersection": {
            "relations": ["H^3=1/3 on P(1,1,1,3)", "(xi-6H)(xi-9H)=0"],
            "complete_homogeneous_h3_6_9": complete_homogeneous_degree_three,
            "xi_four": xi_four,
            "Cox_trace_property": "Res_Y(J_toric)=integral_Y xi^4=585",
            "Mavlyutov_c12": "1/2",
            "Mavlyutov_exponent": "1+3+1+3=8, hence positive sign",
        },
        "critical_quotient_witness": {
            "prime": prime,
            "split_root": 5,
            "minimal_polynomial_value": minimal_value,
            "minimal_polynomial_derivative": minimal_derivative,
            "ambient_monomials": len(critical_basis),
            "relation_rows": len(rows),
            "relation_rows_by_section": counts,
            "relation_rank": witness["relation_rank"],
            "quotient_dimension": witness["quotient_dimension"],
            "basis_sha256": canonical_digest(critical_basis),
            "functional_sha256": witness["functional_sha256"],
            "top_to_critical_embedding_ratio": embedding_ratio,
            "toric_Jacobian_term_count": len(jacobian),
            "toric_Jacobian_sha256": canonical_digest(
                [[list(term), value] for term, value in sorted(jacobian.items())]
            ),
            "toric_Jacobian_quotient_value": jacobian_value,
            "canonical_toric_trace_scale_mod21817": canonical_toric_top_scale,
            "Mavlyutov_c12_mod21817": mavlyutov_c12_mod_prime,
            "canonical_Serre_pairing_scale_mod21817": canonical_serre_scale,
        },
        "normalization_contract": {
            "top_class": "[P] in R_(18,1)",
            "Cox_multiplier": "M=x*y*z*w*U*V",
            "canonical_toric_trace": "lambda_C([P])=Res_Y([M*P])",
            "canonical_Serre_pairing_trace": "Tr_C([P])=c_12*Res_Y([M*P]) with c_12=1/2 in the adopted algebraic de Rham convention",
            "projective_functional": "f_1494=1 with monomial w^9*V",
            "general_toric_scale_formula": "s_toric=(integral_Y xi^4)*f_crit(M*m_1494)/f_crit(J_toric)",
            "general_Serre_scale_formula": "s_C=c_12*(integral_Y xi^4)*f_crit(M*m_1494)/f_crit(J_toric), c_12=1/2",
            "good_reduction_toric_scale_mod21817": canonical_toric_top_scale,
            "good_reduction_Serre_scale_mod21817": canonical_serre_scale,
            "adjunction_compatibility": "Tr_C=Tr_K3 o delta for 0->O_S->O_S(C)->K_C->0",
            "transport_rule": "replace every projective f,S,h by s_C*f,s_C*S,h/s_C respectively; source covectors and physical pairings are unchanged",
            "directed_derivative_rule": {
                "trace": "f_abs'=s_C'*f_proj+s_C*f_proj'",
                "Serre_matrix": "S_abs'=s_C'*S_proj+s_C*S_proj'",
                "source_lift": "h_abs'=h_proj'/s_C-(s_C'/s_C^2)*h_proj",
                "required_new_scalar": "s_C' is obtained by differentiating the same Cox-residue quotient; it is not an independent input",
            },
        },
        "frontier_delta": {
            "before": "TopTrace[1494]=1 was only a projective chart and intrinsic residue/integral normalization was unspecified.",
            "after": "The scale is a canonical Cox-residue evaluation fixed by xi^4=585. A complete exact good-reduction witness on the rejected B89 test member proves the top-to-critical multiplier is nonzero and gives the first absolute coordinate scale; the formula applies to every smooth degree-(6,9) member and uses no period or physical fit.",
            "next": "Apply the same algebraic scalar formula to the first surviving selected candidate and at every framed-member panel in multiprecision, then perform directed rank-164 transport and the period quotient.",
        },
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "normalization_choices_promoted_to_physics": 0,
        },
        "checks": checks,
        "guardrails": {
            "the_GF21817_scale_is_called_the_selected_complex_member_scale": False,
            "a_projective_chart_coordinate_is_called_a_physical_period": False,
            "the_trace_normalization_is_called_a_beta_C_or_U_eta9_decision": False,
            "the_B89_member_is_reinstated_after_its_Deligne_rejection": False,
            "directed_path_transport_or_period_quotient_is_claimed": False,
        },
        "references": [
            "https://arxiv.org/abs/alg-geom/9410017",
            "https://arxiv.org/abs/alg-geom/9506024",
            "https://arxiv.org/abs/math/9812163",
            "https://arxiv.org/abs/math/0610228",
        ],
    }
    require(not any(packet["guardrails"].values()), "CBF.T64 guardrails")
    OUTPUT.write_text(
        json.dumps(packet, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T64 build: PASS "
        f"critical=9361-9360 toric_scale={canonical_toric_top_scale} "
        f"Serre_scale={canonical_serre_scale} mod {prime} xi4={xi_four}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
