#!/usr/bin/env python3
"""Independent verifier for the affine zero-section action packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import verify_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "affine_zero_section_action.packet.json"
SOURCE_LOCK = ROOT / "affine_zero_section_action_source_lock.json"
SCHEMA = ROOT / "affine_zero_section_action_contract.schema.json"
THEOREM = ROOT / "AffineZeroSectionActionAndProjectiveClosurePressureUniquenessTheorem_v1.md"
T16_PACKET = ROOT / "closure_pressure_family_hessian_activation.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qscalar(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def real_part(value: cp.K) -> cp.K:
    return value[0], value[1], Fraction(0), Fraction(0)


def imag_part(value: cp.K) -> cp.K:
    return value[2], value[3], Fraction(0), Fraction(0)


def realification(matrix: cp.Matrix) -> cp.Matrix:
    size = len(matrix)
    result = cp.zero(2 * size, 2 * size)
    for row in range(size):
        for column in range(size):
            re = real_part(matrix[row][column])
            im = imag_part(matrix[row][column])
            result[row][column] = re
            result[row][size + column] = cp.neg(im)
            result[size + row][column] = im
            result[size + row][size + column] = re
    return result


def sum_k(values: Any) -> cp.K:
    result = cp.Z
    for value in values:
        result = cp.add(result, value)
    return result


def matvec(matrix: cp.Matrix, vector: list[cp.K]) -> list[cp.K]:
    return [sum_k(cp.mul(entry, value) for entry, value in zip(row, vector)) for row in matrix]


def inner(left: list[cp.K], right: list[cp.K]) -> cp.K:
    return sum_k(cp.mul(cp.conj(x), y) for x, y in zip(left, right))


def vector_add(left: list[cp.K], right: list[cp.K]) -> list[cp.K]:
    return [cp.add(x, y) for x, y in zip(left, right)]


def vector_scale(value: cp.K, vector: list[cp.K]) -> list[cp.K]:
    return [cp.mul(value, entry) for entry in vector]


def basis_vector(size: int, index: int, value: cp.K = cp.O) -> list[cp.K]:
    vector = [cp.Z for _ in range(size)]
    vector[index] = value
    return vector


def hardcoded_responses() -> tuple[cp.Matrix, cp.Matrix]:
    zero = cp.Z
    minus_one_minus_i_sqrt3: cp.K = (
        Fraction(-1), Fraction(0), Fraction(0), Fraction(-1)
    )
    minus_one_plus_i_sqrt3: cp.K = (
        Fraction(-1), Fraction(0), Fraction(0), Fraction(1)
    )
    a = [
        [cp.scalar(-2), zero, cp.scalar(-2)],
        [zero, cp.scalar(-2), cp.scalar(-2)],
        [cp.scalar(-2), cp.scalar(-2), zero],
    ]
    b = [
        [cp.scalar(-4), zero, zero],
        [zero, zero, minus_one_minus_i_sqrt3],
        [zero, minus_one_plus_i_sqrt3, zero],
    ]
    return a, b


def routed_hessian() -> tuple[cp.Matrix, cp.Matrix, cp.Matrix]:
    a, b = hardcoded_responses()
    phase_slots = {6, 7, 8, 14}
    shift_slots = {9, 10, 11, 15}
    r_phase = cp.diagonal([cp.O if index in phase_slots else cp.Z for index in range(16)])
    r_shift = cp.diagonal([cp.O if index in shift_slots else cp.Z for index in range(16)])
    hessian = cp.matrix_add(cp.kron(b, r_phase), cp.kron(a, r_shift))
    return a, b, hessian


def q_form(hessian: cp.Matrix, vector: list[cp.K]) -> cp.K:
    return real_part(inner(vector, matvec(hessian, vector)))


def psi(hessian: cp.Matrix, vector: list[cp.K]) -> list[cp.K]:
    result = [cp.Z for _ in range(16)]
    result[15] = cp.mul(qscalar(Fraction(1, 2)), q_form(hessian, vector))
    return result


def ell(vector: list[cp.K]) -> cp.K:
    return real_part(vector[15])


def action(
    pressure: Fraction,
    hessian: cp.Matrix,
    normal: list[cp.K],
    tangent: list[cp.K],
    multiplier: list[cp.K],
) -> cp.K:
    residual = vector_add(normal, psi(hessian, tangent))
    field_action = cp.neg(cp.mul(qscalar(pressure), ell(normal)))
    return cp.add(field_action, real_part(inner(multiplier, residual)))


def bordered(hessian: cp.Matrix) -> cp.Matrix:
    result = cp.zero(80, 80)
    for index in range(16):
        result[index][64 + index] = cp.O
        result[64 + index][index] = cp.O
    for row in range(48):
        for column in range(48):
            result[16 + row][16 + column] = hessian[row][column]
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t16 = json.loads(T16_PACKET.read_text(encoding="ascii"))
    checks = 0

    require(packet["schema"] == "boe.mtt.affine-zero-section-action.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T17", "claim id")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1

    require(source_lock["repository_head_before"] == "563778fdb161014b7497a84ff19fde6500906816", "starting head")
    checks += 1
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.exists() and sha256(path) == source["sha256"], f"locked source {source['path']}")
        checks += 1

    require(schema["properties"]["schema"]["const"] == packet["schema"], "contract packet schema")
    checks += 1
    require(schema["properties"]["projective_pressure"]["properties"]["nonzero_unoriented_classes"]["const"] == 1, "projective class contract")
    checks += 1
    require(schema["properties"]["projective_pressure"]["properties"]["physical_action_scale_selected"]["const"] is False, "scale boundary contract")
    checks += 1
    require(schema["properties"]["claim_boundary"]["properties"]["physical_rows_accepted"]["const"] == 0, "physical row contract")
    checks += 1

    a, b, hessian = routed_hessian()
    require(cp.encode_matrix(a) == t16["finite_instantiation"]["A_H_shift"], "independent A")
    checks += 1
    require(cp.encode_matrix(b) == t16["finite_instantiation"]["B_H_phase"], "independent B")
    checks += 1
    require(hessian == cp.adjoint(hessian), "Hermitian routed Hessian")
    checks += 1
    require(cp.rank(hessian) == 24, "complex Hessian rank")
    checks += 1

    hessian_real = realification(hessian)
    require(hessian_real == cp.transpose(hessian_real), "realified symmetry")
    checks += 1
    require(cp.rank(hessian_real) == 48, "realified rank")
    checks += 1
    require(96 - cp.rank(hessian_real) == 48, "real tangent kernel")
    checks += 1

    bordered_hessian = bordered(hessian)
    require(cp.rank(bordered_hessian) == 56, "complex bordered rank")
    checks += 1
    require(80 - cp.rank(bordered_hessian) == 24, "complex bordered kernel")
    checks += 1
    require(64 + cp.rank(hessian_real) == 112, "real bordered rank")
    checks += 1
    require(160 - (64 + cp.rank(hessian_real)) == 48, "real bordered kernel")
    checks += 1

    i_unit: cp.K = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    sqrt3: cp.K = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    one_plus_i: cp.K = (Fraction(1), Fraction(0), Fraction(1), Fraction(0))
    vectors = [
        basis_vector(48, 6),
        vector_add(basis_vector(48, 7), basis_vector(48, 8, i_unit)),
        vector_add(basis_vector(48, 25), basis_vector(48, 27, sqrt3)),
        vector_add(basis_vector(48, 46), basis_vector(48, 47, one_plus_i)),
        vector_add(basis_vector(48, 0), basis_vector(48, 31)),
    ]
    for vector in vectors:
        psi_value = psi(hessian, vector)
        graph_normal = vector_scale(qscalar(-1), psi_value)
        require(all(value == cp.Z for value in vector_add(graph_normal, psi_value)), "graph residual")
        require(cp.neg(ell(graph_normal)) == cp.mul(qscalar(Fraction(1, 2)), q_form(hessian, vector)), "graph pullback")
        checks += 2

    for left, right in zip(vectors, vectors[1:]):
        lhs = cp.sub(cp.sub(q_form(hessian, vector_add(left, right)), q_form(hessian, left)), q_form(hessian, right))
        rhs = cp.mul(qscalar(2), real_part(inner(left, matvec(hessian, right))))
        require(lhs == rhs, "polarization")
        checks += 1

    normal = vector_add(basis_vector(16, 2), basis_vector(16, 15, sqrt3))
    mu = vector_add(basis_vector(16, 1), basis_vector(16, 15, one_plus_i))
    for pressure in (Fraction(2), Fraction(-3), Fraction(5, 7)):
        for tangent in vectors:
            lhs = action(pressure, hessian, normal, tangent, vector_scale(qscalar(pressure), mu))
            rhs = cp.mul(qscalar(pressure), action(Fraction(1), hessian, normal, tangent, mu))
            require(lhs == rhs, "projective pressure identity")
            checks += 1

    general = packet["general_theorem"]
    require(general["unshifted_critical_multiplier"] == "lambda=0", "cotangent no-go")
    checks += 1
    require(general["critical_multiplier"] == "lambda_*=ell", "loaded multiplier")
    checks += 1
    require(
        general["tangent_Hessian"]
        == "D2_kk U(0,0)+ell o D2psi(0)"
        and general["graph_pullback_Hessian"]
        == "D2(i^*U)(0)=D2_kk U(0,0)+ell o D2psi(0)",
        "second variation",
    )
    checks += 1

    projective = packet["projective_pressure"]
    require(projective["zero_branch_separate"], "zero branch")
    checks += 1
    require(projective["nonzero_unoriented_classical_classes"] == 1, "one nonzero projective class")
    checks += 1
    require(projective["continuous_dimensionless_shape_parameters"] == 0, "no pressure shape knob")
    checks += 1
    require(not projective["overall_physical_action_scale_selected"], "scale not selected")
    checks += 1

    finite = packet["finite_action"]
    require(finite["graph_restricted_action"] == "1/2 Re<k,H_resp k>", "lower action")
    checks += 1
    require((finite["real_bordered_dimension"], finite["real_bordered_rank"], finite["real_bordered_kernel"]) == (160, 112, 48), "real bordered data")
    checks += 1
    require(finite["real_bordered_inertia_at_positive_normalized_pressure"] == {"positive": 48, "negative": 64, "zero": 48}, "real inertia")
    checks += 1

    symmetry = packet["symmetry_and_spectrum"]
    require(symmetry["gauge_group_preserved"] and symmetry["shared_circle_preserved"], "gauge and circle")
    checks += 1
    require(symmetry["family_stabilizer"] == "U(1)", "family stabilizer")
    checks += 1
    require(symmetry["CP_sensitive_finite_orientation"], "CP-sensitive finite orientation")
    checks += 1
    require(not symmetry["physical_CKM_or_CP_identification"], "CP nonpromotion")
    checks += 1
    require(not symmetry["three_distinct_positive_family_magnitudes"], "magnitude no-go")
    checks += 1

    provenance = packet["source_provenance"]
    require(provenance["one_finite_algebraic_action_object_constructed"], "finite action object")
    checks += 1
    require(not provenance["physical_endpoint_selects_this_action"], "physical selection boundary")
    checks += 1
    require(provenance["physical_same_root_status"] == "OPEN", "same-root status")
    checks += 1

    ledger = packet["parameter_ledger"]
    require(ledger["observed_construction_inputs"] == 0, "no observed inputs")
    checks += 1
    require(ledger["fitted_dimensionless_coefficients"] == 0, "no fitted coefficients")
    checks += 1
    require(ledger["new_continuous_pressure_shape_parameters"] == 0, "no continuous pressure knob")
    checks += 1
    require(ledger["unselected_overall_physical_action_scale"] == 1, "one overall scale open")
    checks += 1
    require(ledger["strict_charged_magnitude_values_remaining"] == 9, "nine charged values")
    checks += 1

    require(not any(packet["physical_typing_boundary"].values()), "physical typing gates")
    checks += 1
    require(not any(packet["claim_boundary"].values()), "claim gates")
    checks += 1
    require((packet["physical_packets_accepted"], packet["physical_packets_total"]) == (0, 3), "packet acceptance")
    checks += 1
    require((packet["physical_rows_accepted"], packet["physical_rows_total"]) == (0, 7), "row acceptance")
    checks += 1
    require(all(packet["checks"].values()), "builder checks")
    checks += 1
    require(packet["check_summary"] == {"failed": [], "passed": 60, "total": 60}, "builder summary")
    checks += 1

    print(f"independent affine zero-section action verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
