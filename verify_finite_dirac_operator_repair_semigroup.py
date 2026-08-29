#!/usr/bin/env python3
"""Independent exact reconstruction of the CBF.T28 repair semigroup."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "finite_dirac_operator_repair_semigroup.packet.json"
SOURCE_LOCK_PATH = ROOT / "finite_dirac_operator_repair_semigroup_source_lock.json"
SCHEMA_PATH = ROOT / "finite_dirac_operator_repair_semigroup_contract.schema.json"
THEOREM_PATH = ROOT / "FiniteDiracOperatorSpaceRepairHessianSemigroupAndProfileBoundaryTheorem_v1.md"
T20_PATH = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T26_PATH = ROOT / "direct_dirac_defect_repair_action.packet.json"
T27_PATH = ROOT / "finite_dirac_spectral_action_classification.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


def encode_matrix(matrix: cp.Matrix) -> list[list[list[str]]]:
    return [[cp.encode(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    payload = json.dumps(encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def sparse_matmul(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not compose")
    result = cp.zero(len(left), len(right[0]))
    for row, left_row in enumerate(left):
        for inner_index, left_value in enumerate(left_row):
            if left_value == cp.ZERO:
                continue
            for column, right_value in enumerate(right[inner_index]):
                if right_value == cp.ZERO:
                    continue
                result[row][column] = cp.kadd(
                    result[row][column], cp.kmul(left_value, right_value)
                )
    return result


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    rows = sum(len(block) for block in blocks)
    columns = sum(len(block[0]) for block in blocks)
    result = cp.zero(rows, columns)
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row, values in enumerate(block):
            for column, value in enumerate(values):
                result[row_offset + row][column_offset + column] = value
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def incidence(pairs: tuple[tuple[int, int], ...]) -> cp.Matrix:
    result = cp.zero(16, 16)
    for target, source in pairs:
        result[target][source] = cp.ONE
    return result


def family_map(projector: cp.Matrix, direction: cp.Matrix, t: Fraction) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), projector), cp.mscale(q(t), direction))


def transfer(
    projector: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    t: Fraction,
) -> cp.Matrix:
    v_phase = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    v_shift = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(projector, phase_direction, t), v_phase),
        cp.kron(family_map(projector, shift_direction, t), v_shift),
    )


def physical_dirac(transfer_matrix: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    return block_diag([particle, conjugate(particle)])


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for index in range(len(matrix)):
        total = cp.kadd(total, matrix[index][index])
    return total


def real_trace(matrix: cp.Matrix) -> Fraction:
    value = matrix_trace(matrix)
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"non-real trace {value}")
    return value[0]


def inner(left: cp.Matrix, right: cp.Matrix) -> Fraction:
    return real_trace(sparse_matmul(cp.adjoint(left), right)) / len(left)


def theta(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(d0, sparse_matmul(value, d0))


def p_plus(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.mscale(q(Fraction(1, 2)), cp.madd(value, theta(d0, value)))


def p_minus(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.mscale(q(Fraction(1, 2)), matrix_sub(value, theta(d0, value)))


def jacobian(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(sparse_matmul(d0, value), sparse_matmul(value, d0))


def hessian(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return jacobian(d0, jacobian(d0, value))


def gradient(value: cp.Matrix) -> cp.Matrix:
    square = sparse_matmul(value, value)
    return cp.mscale(q(2), sparse_matmul(value, matrix_sub(square, cp.identity(len(value)))))


def outer(left: list[cp.K], right: list[cp.K]) -> cp.Matrix:
    result = cp.zero(len(left), len(right))
    for row, left_value in enumerate(left):
        for column, right_value in enumerate(right):
            result[row][column] = cp.kmul(left_value, cp.kconj(right_value))
    return result


def first_column(matrix: cp.Matrix) -> list[cp.K]:
    for column in range(len(matrix[0])):
        candidate = [matrix[row][column] for row in range(len(matrix))]
        if any(value != cp.ZERO for value in candidate):
            return candidate
    raise AssertionError("no nonzero column")


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK_PATH.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="ascii"))
    t20 = json.loads(T20_PATH.read_text(encoding="ascii"))
    t23 = json.loads(T23_PATH.read_text(encoding="ascii"))
    t26 = json.loads(T26_PATH.read_text(encoding="ascii"))
    t27 = json.loads(T27_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(
        packet["schema"] == "boe.mtt.finite-dirac-operator-repair-semigroup.v1",
        "packet schema",
        passed,
    )
    require(packet["claim_id"] == "CBF.T28", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(
        source_lock["handoff_id"] == "23aae2ca-0eff-4cb1-b39f-a4bbf78cabf9",
        "handoff pin",
        passed,
    )
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = decode_matrix(primitive["P"])
    x = decode_matrix(primitive["X"])
    z = decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(0)))
    d_at_one = physical_dirac(
        transfer(projector, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)
    h_phys = jacobian(d0, d1)
    remainder = sparse_matmul(d1, d1)
    h2 = sparse_matmul(h_phys, h_phys)

    require(d0 == cp.adjoint(d0), "D0 self-adjoint", passed)
    require(sparse_matmul(d0, d0) == identity96, "D0 involution", passed)
    require(sparse_matmul(d0, d1) == sparse_matmul(d1, d0), "D0-D1 commute", passed)
    require(jacobian(d0, d1) == h_phys, "J0(D1)=H", passed)
    require(remainder == cp.mscale(q(Fraction(1, 4)), h2), "R=H2/4", passed)
    require(
        matrix_digest(h_phys) == t23["hessian_compression"]["KO6_response_sha256"],
        "T23 H digest",
        passed,
    )
    require(
        matrix_digest(h_phys) == packet["selected_family_pullback"]["H_phys_sha256"],
        "packet H digest",
        passed,
    )

    e_plus = cp.mscale(q(Fraction(1, 2)), cp.madd(identity96, d0))
    e_minus = cp.mscale(q(Fraction(1, 2)), matrix_sub(identity96, d0))
    rank_plus = cp.matrix_rank(e_plus)
    rank_minus = cp.matrix_rank(e_minus)
    require(rank_plus == 48, "D0 plus rank", passed)
    require(rank_minus == 48, "D0 minus rank", passed)
    require(sparse_matmul(e_plus, e_minus) == cp.zero(96, 96), "D0 projector orthogonality", passed)
    require(cp.madd(e_plus, e_minus) == identity96, "D0 projector resolution", passed)
    comm_dimension = rank_plus**2 + rank_minus**2
    anti_dimension = 2 * rank_plus * rank_minus
    require(comm_dimension == 4608, "commuting dimension", passed)
    require(anti_dimension == 4608, "anticommuting dimension", passed)
    require(comm_dimension + anti_dimension == 9216, "operator dimension", passed)

    plus_vector = first_column(e_plus)
    minus_vector = first_column(e_minus)
    normal = outer(plus_vector, plus_vector)
    cross = outer(plus_vector, minus_vector)
    tangent = cp.madd(cross, cp.adjoint(cross))
    generic = cp.madd(normal, tangent)
    require(normal != cp.zero(96, 96), "normal sample nonzero", passed)
    require(tangent != cp.zero(96, 96), "tangent sample nonzero", passed)
    require(p_plus(d0, normal) == normal, "normal parity", passed)
    require(p_minus(d0, normal) == cp.zero(96, 96), "normal negative part", passed)
    require(p_minus(d0, tangent) == tangent, "tangent parity", passed)
    require(p_plus(d0, tangent) == cp.zero(96, 96), "tangent positive part", passed)
    require(jacobian(d0, tangent) == cp.zero(96, 96), "Jacobian tangent kernel", passed)
    require(hessian(d0, tangent) == cp.zero(96, 96), "Hessian tangent kernel", passed)
    require(hessian(d0, normal) == cp.mscale(q(4), normal), "Hessian normal eigenvalue", passed)
    require(inner(normal, tangent) == 0, "tangent-normal orthogonality", passed)

    for name, sample in {
        "generic": generic,
        "D1": d1,
        "H": h_phys,
        "R": remainder,
    }.items():
        positive = p_plus(d0, sample)
        negative = p_minus(d0, sample)
        require(cp.madd(positive, negative) == sample, f"{name} split", passed)
        require(p_plus(d0, positive) == positive, f"{name} plus idempotence", passed)
        require(p_minus(d0, negative) == negative, f"{name} minus idempotence", passed)
        require(inner(positive, negative) == 0, f"{name} orthogonality", passed)
        require(
            hessian(d0, sample) == cp.mscale(q(4), positive),
            f"{name} A=4Pplus",
            passed,
        )

    require(p_plus(d0, d1) == d1, "D1 normal", passed)
    require(p_plus(d0, h_phys) == h_phys, "H normal", passed)
    require(p_plus(d0, remainder) == remainder, "R normal", passed)
    require(hessian(d0, d1) == cp.mscale(q(4), d1), "A(D1)=4D1", passed)
    require(hessian(d0, h_phys) == cp.mscale(q(4), h_phys), "A(H)=4H", passed)
    require(hessian(d0, remainder) == cp.mscale(q(4), remainder), "A(R)=4R", passed)

    d1_norm = inner(d1, d1)
    scalar_hessian = inner(d1, hessian(d0, d1))
    require(real_trace(remainder) == 192, "trace R", passed)
    require(d1_norm == 2, "D1 norm", passed)
    require(real_trace(h2) == 768, "trace H2", passed)
    require(scalar_hessian == 8, "scalar Hessian", passed)
    require(scalar_hessian == 4 * d1_norm, "metric-eigenvalue reconciliation", passed)
    require(scalar_hessian / d1_norm == 4, "induced linear rate", passed)

    t = Fraction(1, 2)
    d_sample = cp.madd(d0, cp.mscale(q(t), d1))
    grad = gradient(d_sample)
    projection = inner(d1, grad) / d1_norm
    expected = 2 * t * (3 * t**2 - 4 * t + 2)
    require(projection == expected, "projected nonlinear gradient", passed)
    require(-6 * t**2 != 0, "branch-ratio obstruction", passed)
    require(grad != cp.mscale(q(projection), d1), "affine family non-invariance", passed)

    hessian_packet = packet["hessian_superoperator"]
    require(hessian_packet["exact_identity"] == "A_rep=2(I+Ad_D0)=4P_comm", "packet Hessian identity", passed)
    require(hessian_packet["spectrum"] == {"0": 4608, "4": 4608}, "packet Hessian spectrum", passed)
    require(hessian_packet["rank"] == 4608, "packet Hessian rank", passed)
    require(hessian_packet["nullity"] == 4608, "packet Hessian nullity", passed)
    require(not hessian_packet["materialized_9216_square_matrix"], "symbolic superoperator", passed)
    require(
        packet["repair_semigroup"]["exact_solution"]
        == "T_s=P_anti+exp(-4s)P_comm",
        "packet semigroup",
        passed,
    )
    require(packet["repair_semigroup"]["contraction_for_nonnegative_s"], "semigroup contraction", passed)
    require(not packet["repair_semigroup"]["physical_Lorentzian_time_identified"], "time boundary", passed)
    require(
        packet["typed_operator_comparison"]["R_is_A_rep_eigenvector_not_A_rep"],
        "typed R distinction",
        passed,
    )
    require(
        not packet["typed_operator_comparison"]["repair_semigroup_equals_exp_minus_sR"],
        "semigroup not exp R",
        passed,
    )
    require(
        packet["typed_operator_comparison"]["normalized_supertrace_profile"]
        == "(1+exp(-4s))/2",
        "supertrace profile",
        passed,
    )
    require(packet["action_profile_boundary"]["same_root_exponential_repair_profile_selected"], "repair profile selected", passed)
    require(not packet["action_profile_boundary"]["scalar_profile_f_of_D_phys_squared_selected"], "scalar profile open", passed)
    require(not packet["action_profile_boundary"]["signed_cyclic_or_BV_action_selected"], "signed action open", passed)
    require(packet["physical_boundary"]["A84_general_mechanism_instantiated"], "A84 instantiated", passed)
    require(not packet["physical_boundary"]["repair_time_to_tau_int_selected"], "A53 scale not imported", passed)
    require(not packet["physical_boundary"]["B_ACTION_01_closed"], "B.ACTION.01 open", passed)
    require(not packet["physical_boundary"]["B_SM_02_closed"], "B.SM.02 open", passed)
    require(packet["physical_packets_accepted"] == 0, "packet acceptance unchanged", passed)
    require(packet["physical_rows_accepted"] == 0, "row acceptance unchanged", passed)
    require(packet["parameter_ledger"]["new_observed_construction_inputs"] == 0, "no observed inputs", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fits", passed)

    boundary = source_lock["boundary"]
    require(boundary["full_operator_space_hessian_after"], "Hessian boundary closed", passed)
    require(boundary["same_root_repair_semigroup_after"], "semigroup boundary closed", passed)
    require(boundary["repair_semigroup_profile_selected"], "repair profile boundary", passed)
    require(not boundary["repair_generator_equals_R_or_H_phys_squared"], "typed generator boundary", passed)
    require(not boundary["physical_spectral_action_profile_selected"], "physical profile boundary", passed)
    require(not boundary["signed_physical_action_selected"], "signed action boundary", passed)

    root_payload: dict[str, Any] = {
        "schema": "boe.mtt.finite-dirac-operator-repair-semigroup-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "configuration_space": "End_sa(H_F), dim_R=9216",
        "metric": "g(X,Y)=Re (Tr/96)(X^*Y)",
        "D0_sha256": matrix_digest(d0),
        "D1_sha256": matrix_digest(d1),
        "H_phys_sha256": matrix_digest(h_phys),
        "repair_hessian": "A_rep=J0^*J0=4P_comm",
        "repair_hessian_spectrum": {"0": 4608, "4": 4608},
        "repair_semigroup": "exp(-sA_rep)=P_anti+exp(-4s)P_comm",
        "physical_spectral_profile": None,
        "signed_physical_action": None,
        "observed_targets": [],
        "theorem_sha256": sha256(THEOREM_PATH),
    }
    root_hash = hashlib.sha256(
        json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    require(root_payload == packet["source_provenance"]["source_root_payload"], "source-root payload", passed)
    require(root_hash == packet["source_provenance"]["source_root_sha256"], "source-root digest", passed)
    require(t26["exact_coefficients"]["Hessian_at_zero"] == "8", "T26 scalar Hessian", passed)
    require(t27["exact_factorization"]["R_identity"] == "R=D1^2=H_phys^2/4", "T27 R identity", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary", passed)

    print(f"CBF.T28 independent verification passed: {len(passed)}/{len(passed)} checks")


if __name__ == "__main__":
    main()
