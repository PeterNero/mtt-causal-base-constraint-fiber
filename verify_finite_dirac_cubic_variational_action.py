#!/usr/bin/env python3
"""Independent exact reconstruction of the CBF.T29 variational action."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "finite_dirac_cubic_variational_action.packet.json"
SOURCE_LOCK_PATH = ROOT / "finite_dirac_cubic_variational_action_source_lock.json"
SCHEMA_PATH = ROOT / "finite_dirac_cubic_variational_action_contract.schema.json"
THEOREM_PATH = ROOT / "CanonicalDiracDefectCubicVariationalActionAndKODoublingCancellationTheorem_v1.md"
T20_PATH = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T26_PATH = ROOT / "direct_dirac_defect_repair_action.packet.json"
T27_PATH = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T28_PATH = ROOT / "finite_dirac_operator_repair_semigroup.packet.json"

Action = Callable[[cp.Matrix], Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


def encode_matrix(matrix: cp.Matrix) -> list[list[list[str]]]:
    return [[cp.encode(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    encoded = json.dumps(encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


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


def conjugate_entries(matrix: cp.Matrix) -> cp.Matrix:
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
    phase_incidence = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    shift_incidence = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(projector, phase_direction, t), phase_incidence),
        cp.kron(family_map(projector, shift_direction, t), shift_incidence),
    )


def physical_dirac(transfer_matrix: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    return block_diag([particle, conjugate_entries(particle)])


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for index in range(len(matrix)):
        total = cp.kadd(total, matrix[index][index])
    return total


def normalized_trace(matrix: cp.Matrix) -> Fraction:
    value = matrix_trace(matrix)
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"non-real trace {value}")
    return value[0] / len(matrix)


def inner(left: cp.Matrix, right: cp.Matrix) -> Fraction:
    return normalized_trace(sparse_matmul(cp.adjoint(left), right))


def square(value: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(value, value)


def cube(value: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(square(value), value)


def residual(value: cp.Matrix) -> cp.Matrix:
    return matrix_sub(square(value), cp.identity(len(value)))


def signed_action(value: cp.Matrix) -> Fraction:
    return normalized_trace(
        matrix_sub(cp.mscale(q(Fraction(1, 3)), cube(value)), value)
    )


def weighted_action(anchor: cp.Matrix, value: cp.Matrix) -> Fraction:
    primitive = matrix_sub(cp.mscale(q(Fraction(1, 3)), cube(value)), value)
    return normalized_trace(sparse_matmul(anchor, primitive)) + Fraction(2, 3)


def jacobian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(sparse_matmul(basepoint, value), sparse_matmul(value, basepoint))


def repair_hessian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return jacobian(basepoint, jacobian(basepoint, value))


def positive_repair_gradient(value: cp.Matrix) -> cp.Matrix:
    return cp.mscale(q(2), sparse_matmul(value, residual(value)))


def weighted_gradient(anchor: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    value_squared = square(value)
    terms = cp.madd(
        sparse_matmul(value_squared, anchor),
        cp.madd(
            sparse_matmul(value, sparse_matmul(anchor, value)),
            sparse_matmul(anchor, value_squared),
        ),
    )
    return matrix_sub(cp.mscale(q(Fraction(1, 3)), terms), anchor)


def weighted_hessian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    theta = sparse_matmul(basepoint, sparse_matmul(value, basepoint))
    return cp.mscale(
        q(Fraction(1, 3)), cp.madd(cp.mscale(q(4), value), cp.mscale(q(2), theta))
    )


def material_projectors(basepoint: cp.Matrix) -> tuple[cp.Matrix, cp.Matrix]:
    identity = cp.identity(len(basepoint))
    return (
        cp.mscale(q(Fraction(1, 2)), cp.madd(identity, basepoint)),
        cp.mscale(q(Fraction(1, 2)), matrix_sub(identity, basepoint)),
    )


def pi_plus(e_plus: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(e_plus, sparse_matmul(value, e_plus))


def pi_minus(e_minus: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(e_minus, sparse_matmul(value, e_minus))


def pi_zero(e_plus: cp.Matrix, e_minus: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(
        sparse_matmul(e_plus, sparse_matmul(value, e_minus)),
        sparse_matmul(e_minus, sparse_matmul(value, e_plus)),
    )


def outer(left: list[cp.K], right: list[cp.K]) -> cp.Matrix:
    result = cp.zero(len(left), len(right))
    for row, left_value in enumerate(left):
        for column, right_value in enumerate(right):
            result[row][column] = cp.kmul(left_value, cp.kconj(right_value))
    return result


def first_nonzero_column(matrix: cp.Matrix) -> list[cp.K]:
    for column in range(len(matrix[0])):
        candidate = [matrix[row][column] for row in range(len(matrix))]
        if any(value != cp.ZERO for value in candidate):
            return candidate
    raise AssertionError("no nonzero column")


def grading() -> cp.Matrix:
    left = {0, 1, 2, 3, 4, 5, 12, 13}
    gamma16 = [-1 if index in left else 1 for index in range(16)]
    gamma48 = gamma16 * 3
    gamma96 = gamma48 + [-value for value in gamma48]
    return cp.diagonal([q(value) for value in gamma96])


def conjugate_by(unitary: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(unitary, sparse_matmul(value, cp.adjoint(unitary)))


def directional_derivative(action: Action, value: cp.Matrix, direction: cp.Matrix) -> Fraction:
    def evaluate(scale: int) -> Fraction:
        return action(cp.madd(value, cp.mscale(q(scale), direction)))

    return (
        8 * (evaluate(1) - evaluate(-1)) - (evaluate(2) - evaluate(-2))
    ) / 12


def odd_moment(value: cp.Matrix, power: int) -> Fraction:
    result = cp.identity(len(value))
    for _ in range(power):
        result = sparse_matmul(result, value)
    return normalized_trace(result)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


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
    t28 = json.loads(T28_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.finite-dirac-cubic-variational-action.v1", "packet schema", passed)
    require(packet["claim_id"] == "CBF.T29", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(source_lock["handoff_id"] == "2921d8c2-d14a-4f82-b8f0-25f0c5b28b96", "handoff pin", passed)
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)

    require(t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()), "T20 exact", passed)
    require(t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()), "T23 exact", passed)
    require(t26["claim_id"] == "CBF.T26" and all(t26["checks"].values()), "T26 exact", passed)
    require(t27["claim_id"] == "CBF.T27" and all(t27["checks"].values()), "T27 exact", passed)
    require(t28["claim_id"] == "CBF.T28" and all(t28["checks"].values()), "T28 exact", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = decode_matrix(primitive["P"])
    x = decode_matrix(primitive["X"])
    z = decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(0)))
    d_one = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(1)))
    d1 = matrix_sub(d_one, d0)
    identity96 = cp.identity(96)
    zero96 = cp.zero(96, 96)
    h_phys = jacobian(d0, d1)
    gamma = grading()

    require(d0 == cp.adjoint(d0), "D0 self-adjoint", passed)
    require(square(d0) == identity96, "D0 involution", passed)
    require(normalized_trace(d0) == 0, "D0 traceless", passed)
    require(signed_action(d0) == 0, "signed action normalized", passed)
    require(residual(d0) == zero96, "signed gradient vanishes at D0", passed)
    require(residual(zero96) == cp.mscale(q(-1), identity96), "signed gradient rejects zero", passed)
    require(positive_repair_gradient(zero96) == zero96, "normal-square gradient accepts zero", passed)

    e_plus, e_minus = material_projectors(d0)
    rank_plus = cp.matrix_rank(e_plus)
    rank_minus = cp.matrix_rank(e_minus)
    require(rank_plus == 48, "plus material rank", passed)
    require(rank_minus == 48, "minus material rank", passed)
    require(sparse_matmul(e_plus, e_minus) == zero96, "material projector orthogonality", passed)
    require(cp.madd(e_plus, e_minus) == identity96, "material projector resolution", passed)
    require(rank_plus**2 == 2304, "positive inertia", passed)
    require(rank_minus**2 == 2304, "negative inertia", passed)
    require(2 * rank_plus * rank_minus == 4608, "zero inertia", passed)

    plus_vector = first_nonzero_column(e_plus)
    minus_vector = first_nonzero_column(e_minus)
    positive = outer(plus_vector, plus_vector)
    negative = outer(minus_vector, minus_vector)
    cross = outer(plus_vector, minus_vector)
    tangent = cp.madd(cross, cp.adjoint(cross))
    generic = cp.madd(positive, cp.madd(negative, tangent))
    require(positive != zero96 and negative != zero96 and tangent != zero96, "sector witnesses nonzero", passed)
    require(pi_plus(e_plus, positive) == positive, "positive witness sector", passed)
    require(pi_minus(e_minus, negative) == negative, "negative witness sector", passed)
    require(pi_zero(e_plus, e_minus, tangent) == tangent, "zero witness sector", passed)
    require(jacobian(d0, positive) == cp.mscale(q(2), positive), "positive Hessian eigenvalue", passed)
    require(jacobian(d0, negative) == cp.mscale(q(-2), negative), "negative Hessian eigenvalue", passed)
    require(jacobian(d0, tangent) == zero96, "zero Hessian eigenvalue", passed)

    for name, sample in {"positive": positive, "negative": negative, "tangent": tangent, "generic": generic, "D1": d1, "H": h_phys}.items():
        plus = pi_plus(e_plus, sample)
        minus = pi_minus(e_minus, sample)
        zero = pi_zero(e_plus, e_minus, sample)
        require(cp.madd(plus, cp.madd(minus, zero)) == sample, f"{name} split", passed)
        require(inner(plus, minus) == 0, f"{name} plus-minus orthogonal", passed)
        require(inner(plus, zero) == 0, f"{name} plus-zero orthogonal", passed)
        require(inner(minus, zero) == 0, f"{name} minus-zero orthogonal", passed)
        require(jacobian(d0, sample) == matrix_sub(cp.mscale(q(2), plus), cp.mscale(q(2), minus)), f"{name} signed decomposition", passed)
        require(repair_hessian(d0, sample) == cp.mscale(q(4), cp.madd(plus, minus)), f"{name} square bridge", passed)

    generator = cp.mscale(q(Fraction(1, 2)), sparse_matmul(tangent, d0))
    require(cp.adjoint(generator) == cp.mscale(q(-1), generator), "orbit generator skew", passed)
    require(matrix_sub(sparse_matmul(generator, d0), sparse_matmul(d0, generator)) == tangent, "orbit tangent equality", passed)

    probe = cp.madd(d0, cp.mscale(q(Fraction(1, 3)), positive))
    signed_derivative = directional_derivative(signed_action, probe, generic)
    require(signed_derivative == inner(residual(probe), generic), "signed variation", passed)
    require(inner(generic, jacobian(d0, positive)) == inner(jacobian(d0, generic), positive), "signed Hessian self-adjoint", passed)

    require(gamma == cp.adjoint(gamma), "grading self-adjoint", passed)
    require(square(gamma) == identity96, "grading involution", passed)
    require(conjugate_by(gamma, d0) == cp.mscale(q(-1), d0), "grading odd D0", passed)
    require(conjugate_by(gamma, d1) == cp.mscale(q(-1), d1), "grading odd D1", passed)
    require(matrix_digest(h_phys) == t23["hessian_compression"]["KO6_response_sha256"], "T23 H digest", passed)

    signed_samples: dict[str, str] = {}
    weighted_samples: dict[str, str] = {}
    moment_samples: dict[str, dict[str, str]] = {}
    for t in [Fraction(-1), Fraction(0), Fraction(1, 2), Fraction(1), Fraction(3, 2)]:
        d_t = cp.madd(d0, cp.mscale(q(t), d1))
        key = fraction_text(t)
        require(conjugate_by(gamma, d_t) == cp.mscale(q(-1), d_t), f"family odd t={key}", passed)
        signed_samples[key] = fraction_text(signed_action(d_t))
        weighted_samples[key] = fraction_text(weighted_action(d0, d_t))
        moment_samples[key] = {}
        require(signed_action(d_t) == 0, f"signed cancellation t={key}", passed)
        require(weighted_action(d0, d_t) == 2 * t**2 - Fraction(8, 9) * t**3, f"weighted polynomial t={key}", passed)
        for power in [1, 3, 5, 7]:
            moment = odd_moment(d_t, power)
            moment_samples[key][str(power)] = fraction_text(moment)
            require(moment == 0, f"odd moment {power}, t={key}", passed)

    d1_plus = pi_plus(e_plus, d1)
    d1_minus = pi_minus(e_minus, d1)
    d1_zero = pi_zero(e_plus, e_minus, d1)
    require(inner(d1_plus, d1_plus) == 1, "D1 plus norm", passed)
    require(inner(d1_minus, d1_minus) == 1, "D1 minus norm", passed)
    require(d1_zero == zero96, "D1 zero component", passed)
    require(inner(d1, jacobian(d0, d1)) == 0, "signed pullback cancellation", passed)
    require(inner(d1, repair_hessian(d0, d1)) == 8, "repair pullback addition", passed)

    weighted = lambda value: weighted_action(d0, value)
    require(weighted_action(d0, d0) == 0, "weighted normalization", passed)
    require(directional_derivative(weighted, probe, generic) == inner(weighted_gradient(d0, probe), generic), "weighted variation", passed)
    require(weighted_hessian(d0, positive) == cp.mscale(q(2), positive), "weighted positive eigenvalue", passed)
    require(weighted_hessian(d0, negative) == cp.mscale(q(2), negative), "weighted negative eigenvalue", passed)
    require(weighted_hessian(d0, tangent) == cp.mscale(q(Fraction(2, 3)), tangent), "weighted tangent eigenvalue", passed)
    require(weighted_hessian(d0, weighted_hessian(d0, tangent)) != repair_hessian(d0, tangent), "weighted square mismatch", passed)
    d_three_halves = cp.madd(d0, cp.mscale(q(Fraction(3, 2)), d1))
    require(inner(weighted_gradient(d0, d_three_halves), d1) == 0, "weighted extra stationary point", passed)
    require(residual(d_three_halves) != zero96, "extra stationary point not closure", passed)

    square_solutions: list[tuple[Fraction, Fraction]] = []
    for plus_sign in (Fraction(-1), Fraction(1)):
        for minus_sign in (Fraction(-1), Fraction(1)):
            a = (plus_sign - minus_sign) / 2
            b = (plus_sign + minus_sign) / 2
            if (a + b) ** 2 == 1 and (-a + b) ** 2 == 1 and b**2 == 0:
                square_solutions.append((a, b))
    require(set(square_solutions) == {(Fraction(-1), Fraction(0)), (Fraction(1), Fraction(0))}, "two-anchor solutions", passed)
    require(all(a * signed_action(cp.madd(d0, cp.mscale(q(Fraction(1, 2)), d1))) + b * weighted_action(d0, cp.madd(d0, cp.mscale(q(Fraction(1, 2)), d1))) == 0 for a, b in square_solutions), "exact-square solutions cancel", passed)

    action_packet = packet["direct_variational_action"]
    require(action_packet["gradient"] == "grad S_sig(D)=D^2-I96", "packet signed gradient", passed)
    require(action_packet["Helmholtz_exact"], "packet Helmholtz", passed)
    require(not action_packet["physical_action_claimed"], "packet action boundary", passed)
    require(packet["critical_locus"]["equals_closure_locus"], "packet critical locus", passed)
    require(packet["critical_locus"]["normal_square_has_extra_critical_points"], "packet normal-square warning", passed)
    require(packet["signed_Hessian"]["spectrum"] == {"-2": 2304, "0": 4608, "2": 2304}, "packet signed spectrum", passed)
    require(packet["normal_square_bridge"]["exact_identity"] == "H_sig^2=J0^2=4(Pi_plus+Pi_minus)=A_rep", "packet square bridge", passed)
    require(packet["Morse_Bott_decomposition"]["tangent_real_dimension"] == 4608, "packet Morse-Bott tangent", passed)
    require(packet["automorphism_transfer"]["finite_operator_space_closed"], "packet finite automorphism", passed)
    require(not packet["automorphism_transfer"]["continuum_q79_transfer_closed"], "packet continuum boundary", passed)
    require(packet["KO6_cancellation"]["sampled_odd_moments"] == moment_samples, "packet odd moments", passed)
    require(packet["KO6_cancellation"]["signed_quadratic_pullback"] == "0", "packet signed pullback", passed)
    require(packet["KO6_cancellation"]["repair_quadratic_pullback"] == "8", "packet repair pullback", passed)
    require(packet["weighted_anchor_escape_test"]["sampled_values"] == weighted_samples, "packet weighted samples", passed)
    require(not packet["weighted_anchor_escape_test"]["squares_to_A_rep"], "packet weighted no-go", passed)
    require(packet["canonical_two_anchor_classification"]["all_exact_square_solutions_cancel"], "packet two-anchor cancellation", passed)
    require(packet["canonical_two_anchor_classification"]["scope"] == "canonical anchors emitted by I96 and D0 only", "packet no-go scope", passed)
    require(packet["parameter_ledger"]["new_observed_construction_inputs"] == 0, "no observed inputs", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fitted coefficients", passed)
    require(not packet["physical_boundary"]["physical_Lorentzian_or_BV_action_selected"], "physical action open", passed)
    require(not packet["physical_boundary"]["continuum_q79_action_transfer_closed"], "q79 transfer open", passed)
    require(not packet["physical_boundary"]["B_ACTION_01_closed"], "B.ACTION.01 open", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "packet acceptance", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "row acceptance", passed)

    root_payload: dict[str, Any] = {
        "schema": "boe.mtt.finite-dirac-cubic-variational-action-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "configuration_space": "End_sa(H_F), dim_R=9216",
        "metric": "g(X,Y)=Re (Tr/96)(X^*Y)",
        "D0_sha256": matrix_digest(d0),
        "D1_sha256": matrix_digest(d1),
        "H_phys_sha256": matrix_digest(h_phys),
        "Gamma96_sha256": matrix_digest(gamma),
        "signed_action": "S_sig(D)=tau96(D^3/3-D)",
        "signed_hessian": "H_sig=J0=2Pi_plus-2Pi_minus",
        "normal_square": "H_sig^2=A_rep=4(Pi_plus+Pi_minus)",
        "signed_hessian_inertia": {"negative": 2304, "positive": 2304, "zero": 4608},
        "KO6_pullback": "S_sig(D_phys(t))=0",
        "physical_Lorentzian_or_BV_action": None,
        "observed_targets": [],
        "theorem_sha256": sha256(THEOREM_PATH),
    }
    root_hash = hashlib.sha256(
        json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    require(root_payload == packet["source_provenance"]["source_root_payload"], "source-root payload", passed)
    require(root_hash == packet["source_provenance"]["source_root_sha256"], "source-root digest", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary", passed)

    print(f"CBF.T29 independent verification passed: {len(passed)}/{len(passed)} checks")


if __name__ == "__main__":
    main()
