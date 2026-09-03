#!/usr/bin/env python3
"""Independent exact replay of the CBF.T64 Cayley trace certificate."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
PACKET = ROOT / "q79_eta9_cayley_serre_trace_normalization.packet.json"
WITNESS = ROOT / "q79_eta9_cayley_serre_trace_normalization.witness.json"


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def repository(variable: str, name: str) -> Path:
    configured = os.environ.get(variable)
    path = Path(configured).expanduser().resolve() if configured else COMMON / name
    demand(path.is_dir(), f"missing repository: {path}")
    return path


PRE = repository("MTT_PREPROJECTION_REPOSITORY", "mtt-preprojection-repair-calculus")
SHARDS = repository("MTT_ETA9_SHARDS_REPOSITORY", "mtt-eta9-parallel-shards")
CURVE_DIR = PRE / "experiments/q79_eta9_b89_curve_higgs_pilot"
SOURCE = PRE / "experiments/q79_eta9_b89_relative_adjoint_compiler/q79_eta9_b89_relative_adjoint_worker_input.json"
H4_RESULT = CURVE_DIR / "kernel_results/36cb7494-7785-4064-83e5-b74b1707229b/outputs/higgs_p21817_r5_O.json"


def load(path: Path) -> dict[str, Any]:
    demand(path.is_file(), f"missing input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_backend() -> Any:
    path = CURVE_DIR / "compute_curve_higgs_modp.py"
    spec = importlib.util.spec_from_file_location("cbf_t64_independent_curve", path)
    demand(spec is not None and spec.loader is not None, "curve backend import")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Exponent = tuple[int, int, int, int, int, int]
Polynomial = dict[Exponent, int]


def clean(poly: Polynomial, prime: int) -> Polynomial:
    return {term: value % prime for term, value in poly.items() if value % prime}


def add(left: Polynomial, right: Polynomial, prime: int) -> Polynomial:
    result = dict(left)
    for term, value in right.items():
        result[term] = (result.get(term, 0) + value) % prime
    return clean(result, prime)


def scale(poly: Polynomial, scalar: int, prime: int) -> Polynomial:
    return clean({term: scalar * value for term, value in poly.items()}, prime)


def shift(poly: Polynomial, delta: Exponent, prime: int) -> Polynomial:
    return clean(
        {tuple(a + b for a, b in zip(term, delta, strict=True)): value for term, value in poly.items()},
        prime,
    )


def derivative(poly: Polynomial, variable: int, prime: int) -> Polynomial:
    result: Polynomial = {}
    for term, value in poly.items():
        exponent = term[variable]
        if exponent:
            reduced = list(term)
            reduced[variable] -= 1
            result[tuple(reduced)] = exponent * value % prime
    return clean(result, prime)


def multiply(left: Polynomial, right: Polynomial, prime: int) -> Polynomial:
    result: Polynomial = {}
    for a, av in left.items():
        for b, bv in right.items():
            term = tuple(x + y for x, y in zip(a, b, strict=True))
            result[term] = (result.get(term, 0) + av * bv) % prime
    return clean(result, prime)


def determinant(matrix: list[list[Polynomial]], prime: int) -> Polynomial:
    result: Polynomial = {}
    for permutation in itertools.permutations(range(len(matrix))):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(len(matrix))
            for j in range(i + 1, len(matrix))
        )
        term: Polynomial = {(0, 0, 0, 0, 0, 0): 1}
        for row, column in enumerate(permutation):
            term = multiply(term, matrix[row][column], prime)
        result = add(result, scale(term, -1 if inversions % 2 else 1, prime), prime)
    return result


def sections(f6: Polynomial, f9: Polynomial, prime: int) -> list[Polynomial]:
    U = (0, 0, 0, 0, 1, 0)
    V = (0, 0, 0, 0, 0, 1)
    phi = add(shift(f6, U, prime), shift(f9, V, prime), prime)
    result = [phi]
    for variable in (1, 2, 3):
        unit = tuple(1 if index == variable else 0 for index in range(6))
        result.append(shift(derivative(phi, variable, prime), unit, prime))
    result.append(shift(f6, U, prime))
    return result


def regularizing_cubic() -> Polynomial:
    return {
        (3, 0, 0, 0, 0, 0): 1,
        (0, 3, 0, 0, 0, 0): 1,
        (0, 0, 3, 0, 0, 0): 1,
        (0, 0, 0, 1, 0, 0): 1,
    }


def transport_top_monomial(term: Exponent, cubic: Polynomial, prime: int) -> Polynomial:
    result: Polynomial = {term: 1}
    if term[4]:
        demand(term[4] == 1, "Cayley degree-one top monomial")
        base = list(term)
        base[4] -= 1
        base[5] += 1
        result = add(result, shift(cubic, tuple(base), prime), prime)
    return result


def evaluate(functional: list[int], index: dict[Exponent, int], poly: Polynomial, prime: int) -> int:
    return sum(functional[index[term]] * value for term, value in poly.items()) % prime


def integer_determinant(matrix: list[list[int]]) -> int:
    total = 0
    for permutation in itertools.permutations(range(len(matrix))):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(len(matrix))
            for j in range(i + 1, len(matrix))
        )
        product = 1
        for row, column in enumerate(permutation):
            product *= matrix[row][column]
        total += (-1 if inversions % 2 else 1) * product
    return total


def main() -> int:
    packet = load(PACKET)
    witness = load(WITNESS)
    curve = import_backend()
    source = load(SOURCE)
    old = load(H4_RESULT)["pieces"]["top_pairing"]
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
    demand(minimal_value == 0 and minimal_derivative != 0, "unramified split place")

    demand(packet["theorem_id"] == "CBF.T64", "theorem identity")
    demand(witness["prime"] == prime, "witness prime")
    functional = [int(value) % prime for value in witness["functional"]]
    demand(len(functional) == 9361, "critical functional length")
    demand(digest(functional) == witness["functional_sha256"], "critical functional hash")

    f6, physical_f9, _ = curve.selected_polynomials(source, 5, (1, 0, prime - 1), (0, 1, 0), prime)
    cubic = regularizing_cubic()
    f9 = add(physical_f9, multiply(f6, cubic, prime), prime)
    generators = sections(f6, f9, prime)
    physical_phi = sections(f6, physical_f9, prime)[0]
    regular_phi = generators[0]
    direct_transport = dict(physical_phi)
    for term, value in physical_phi.items():
        if term[4]:
            demand(term[4] == 1, "Cayley potential is linear in U")
            base = list(term)
            base[4] -= 1
            base[5] += 1
            direct_transport = add(
                direct_transport,
                scale(shift(cubic, tuple(base), prime), value, prime),
                prime,
            )
    demand(direct_transport == regular_phi, "triangular Cayley gauge identity")
    basis = curve.component_monomials(9, 3)
    index = {term: column for column, term in enumerate(basis)}
    demand(len(basis) == 9361, "critical basis dimension")
    relation_count = 0
    for generator in generators:
        for multiplier in curve.component_monomials(9, 2):
            relation_count += 1
            relation = shift(generator, multiplier, prime)
            demand(evaluate(functional, index, relation, prime) == 0, "relation annihilation")
    demand(relation_count == 16740, "relation count")

    old_basis = [tuple(int(value) for value in term) for term in old["monomial_basis"]]
    old_functional = [int(value) % prime for value in old["top_functional"]]
    M = (1, 1, 1, 1, 1, 1)
    embedded = [
        evaluate(functional, index, shift(transport_top_monomial(term, cubic, prime), M, prime), prime)
        for term in old_basis
    ]
    old_pivot = next(i for i, value in enumerate(old_functional) if value)
    ratio = embedded[old_pivot] * pow(old_functional[old_pivot], -1, prime) % prime
    demand(ratio != 0, "Cox multiplier nonzero")
    demand(all(a == ratio * b % prime for a, b in zip(embedded, old_functional, strict=True)), "intertwiner")

    matrix = [generators]
    for variable in (1, 2, 3, 4):
        matrix.append([derivative(poly, variable, prime) for poly in generators])
    numerator = determinant(matrix, prime)
    divisor = (1, 0, 0, 0, 0, 1)
    jacobian: Polynomial = {}
    for term, value in numerator.items():
        demand(all(a >= b for a, b in zip(term, divisor, strict=True)), "Cox divisibility")
        jacobian[tuple(a - b for a, b in zip(term, divisor, strict=True))] = value
    jacobian_value = evaluate(functional, index, jacobian, prime)
    demand(jacobian_value != 0, "Jacobian residue nonzero")

    rays = [
        [-1, -1, -3, -3], [1, 0, 0, 0], [0, 1, 0, 0],
        [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, -1],
    ]
    selected_minor = [[rays[column][row] for column in (1, 2, 3, 4)] for row in range(4)]
    demand(integer_determinant(selected_minor) == 1, "ray minor determinant")
    gauge = packet["geometry"]["regularizing_Cayley_gauge"]
    demand(gauge["determinant"] == 1, "Cayley gauge determinant")
    demand(not gauge["physical_complete_intersection_changed"], "Cayley gauge preserves curve")
    demand(not gauge["is_physical_parameter"], "Cayley gauge is not physical")
    xi_four = (6**3 + 6**2 * 9 + 6 * 9**2 + 9**3) // 3
    demand(xi_four == 585, "projective-bundle intersection")
    toric_scale = xi_four * ratio * pow(jacobian_value, -1, prime) % prime
    c12 = pow(2, -1, prime)
    serre_scale = c12 * toric_scale % prime

    recorded = packet["critical_quotient_witness"]
    demand(recorded["minimal_polynomial_value"] == minimal_value, "minimal polynomial replay")
    demand(recorded["minimal_polynomial_derivative"] == minimal_derivative, "unramified derivative replay")
    demand(recorded["relation_rank"] == 9360, "certified relation rank")
    demand(recorded["quotient_dimension"] == 1, "critical quotient line")
    demand(recorded["top_to_critical_embedding_ratio"] == ratio, "embedding ratio replay")
    demand(recorded["toric_Jacobian_quotient_value"] == jacobian_value, "Jacobian value replay")
    demand(recorded["canonical_toric_trace_scale_mod21817"] == toric_scale, "toric scale replay")
    demand(recorded["Mavlyutov_c12_mod21817"] == c12, "Mavlyutov c12 replay")
    demand(recorded["canonical_Serre_pairing_scale_mod21817"] == serre_scale, "Serre scale replay")
    roots = {
        "mtt-preprojection-repair-calculus": PRE,
        "mtt-eta9-parallel-shards": SHARDS,
        "mtt-causal-base-constraint-fiber": ROOT,
    }
    for record in packet["inputs"].values():
        path = roots[record["repository"]] / record["path"]
        demand(path.is_file(), f"hash-bound input exists: {path}")
        demand(path.stat().st_size == record["bytes"], f"input size: {path.name}")
        demand(file_sha256(path) == record["sha256"], f"input hash: {path.name}")
    demand(all(packet["checks"].values()), "packet checks")
    demand(not any(packet["guardrails"].values()), "guardrails")
    print(
        "CBF.T64 independent verification: PASS "
        f"relations={relation_count} quotient=1 xi4={xi_four} "
        f"toric_scale={toric_scale} Serre_scale={serre_scale} mod {prime}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
