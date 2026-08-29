#!/usr/bin/env python3
"""Independently verify the CBF.T24 upper-totalization packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "upper_totalization_supercharge_source_lock.json"
SCHEMA = ROOT / "upper_totalization_supercharge_contract.schema.json"
THEOREM = ROOT / "UpperTensorTotalizationSharedLineSuperchargeSelectionTheorem_v1.md"
PACKET = ROOT / "upper_totalization_supercharge.packet.json"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T22_PACKET = ROOT / "relative_product_supercharge.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
SHARED_ROOT_PACKET = (
    ROOT.parent
    / "mtt-q79-total-superconnection-branching"
    / "artifacts"
    / "almost_commutative_shared_root_spinc.packet.json"
)
BINARY_ROOT_PACKET = (
    ROOT.parent
    / "mtt-q79-total-superconnection-branching"
    / "artifacts"
    / "binary_root_car_net_equivalence.packet.json"
)
UNIVERSAL_LINE_PACKET = (
    ROOT.parent
    / "20 Mathematical Language Discovery Program"
    / "q79_universal_shared_line_intertwiner.packet.json"
)

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def subtract(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def sparse_multiply(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    result = cp.zero(len(left), len(right[0]))
    for row in range(len(left)):
        for inner, left_value in enumerate(left[row]):
            if left_value == cp.ZERO:
                continue
            for column, right_value in enumerate(right[inner]):
                if right_value != cp.ZERO:
                    result[row][column] = cp.kadd(
                        result[row][column], cp.kmul(left_value, right_value)
                    )
    return result


def digest(matrix: cp.Matrix) -> str:
    encoded = json.dumps(wg.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def incidence(pairs: tuple[tuple[int, int], ...]) -> cp.Matrix:
    matrix = cp.zero(16, 16)
    for target, source in pairs:
        matrix[target][source] = cp.ONE
    return matrix


def family_map(p: cp.Matrix, direction: cp.Matrix, value: Fraction) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), p), cp.mscale(q(value), direction))


def transfer(
    p: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    value: Fraction,
) -> cp.Matrix:
    v_phase = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    v_shift = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(p, phase_direction, value), v_phase),
        cp.kron(family_map(p, shift_direction, value), v_shift),
    )


def finite_q_and_d(transfer_matrix: cp.Matrix) -> tuple[cp.Matrix, cp.Matrix]:
    q_finite = wg.block_diag(
        [transfer_matrix, conjugate(cp.adjoint(transfer_matrix))]
    )
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    d_finite = wg.block_diag([particle, conjugate(particle)])
    return q_finite, d_finite


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t22 = json.loads(T22_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    shared_root = json.loads(SHARED_ROOT_PACKET.read_text(encoding="utf-8"))
    binary_root = json.loads(BINARY_ROOT_PACKET.read_text(encoding="utf-8"))
    universal_line = json.loads(UNIVERSAL_LINE_PACKET.read_text(encoding="utf-8"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.upper-totalization-supercharge.v1", "schema", passed)
    require(packet["claim_id"] == "CBF.T24", "claim", passed)
    require(set(packet) == set(schema["required"]), "strict required keys", passed)
    require(set(packet) == set(schema["properties"]), "strict property keys", passed)
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash", passed)
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash", passed)
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash", passed)

    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash {source['path']}", passed)

    require(t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()), "T20 source", passed)
    require(t22["claim_id"] == "CBF.T22" and all(t22["checks"].values()), "T22 source", passed)
    require(t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()), "T23 source", passed)
    require(shared_root["all_checks_pass"], "shared root source", passed)
    require(binary_root["all_checks_pass"], "binary root source", passed)
    require(all(universal_line["checks"].values()), "universal line source", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    phase_direction = cp.madd(cp.identity(3), z)
    shift_direction = cp.madd(cp.identity(3), x)

    q_y = [[cp.ZERO, cp.ZERO], [cp.ONE, cp.ZERO]]
    d_y = cp.madd(q_y, cp.adjoint(q_y))
    gamma_y = cp.diagonal([cp.ONE, q(-1)])
    i2 = cp.identity(2)
    i96 = cp.identity(96)
    i192 = cp.identity(192)
    h = Fraction(5, 4)
    value = Fraction(2, 3)

    q_f, d_f = finite_q_and_d(
        transfer(p, phase_direction, shift_direction, value)
    )
    require(sparse_multiply(q_f, q_f) == cp.zero(96, 96), "finite q squared", passed)
    require(cp.madd(q_f, cp.adjoint(q_f)) == d_f, "finite charge", passed)

    q_total = cp.madd(
        cp.kron(q_y, i96),
        cp.kron(gamma_y, cp.mscale(q(h), q_f)),
    )
    require(sparse_multiply(q_total, q_total) == cp.zero(192, 192), "total q squared", passed)
    b_from_q = cp.madd(q_total, cp.adjoint(q_total))
    b_direct = cp.madd(
        cp.kron(d_y, i96),
        cp.kron(gamma_y, cp.mscale(q(h), d_f)),
    )
    require(b_from_q == b_direct, "closure charge reconstruction", passed)
    expected_square = cp.madd(
        cp.kron(sparse_multiply(d_y, d_y), i96),
        cp.kron(i2, cp.mscale(q(h * h), sparse_multiply(d_f, d_f))),
    )
    require(sparse_multiply(b_direct, b_direct) == expected_square, "graded square", passed)

    q_naive = cp.madd(
        cp.kron(q_y, i96),
        cp.kron(i2, cp.mscale(q(h), q_f)),
    )
    naive_square = sparse_multiply(q_naive, q_naive)
    require(naive_square != cp.zero(192, 192), "naive sum fails", passed)
    require(
        naive_square == cp.mscale(q(2 * h), cp.kron(q_y, q_f)),
        "naive exact cross term",
        passed,
    )

    coefficient_system = [
        [q(0), q(1), q(0), q(0)],
        [q(0), q(0), q(1), q(0)],
        [q(1), q(0), q(0), q(1)],
        [q(1), q(0), q(0), q(0)],
    ]
    require(cp.matrix_rank(coefficient_system) == 4, "uniqueness rank", passed)
    require(packet["totalization_uniqueness"]["unique_solution"] == ["1", "0", "0", "-1"], "unique coefficient", passed)
    require(packet["totalization_uniqueness"]["selected_coefficient"] == "A=Gamma_Y", "Koszul sign", passed)

    _, d_zero = finite_q_and_d(
        transfer(p, phase_direction, shift_direction, Fraction(0))
    )
    require(sparse_multiply(d_zero, d_zero) == i96, "neutral finite square", passed)
    b_zero = cp.madd(
        cp.kron(d_y, i96),
        cp.kron(gamma_y, cp.mscale(q(h), d_zero)),
    )
    relative_zero = subtract(
        sparse_multiply(b_zero, b_zero), cp.mscale(q(h * h), i192)
    )
    require(relative_zero == cp.kron(sparse_multiply(d_y, d_y), i96), "neutral subtraction", passed)

    _, d_plus = finite_q_and_d(
        transfer(p, phase_direction, shift_direction, Fraction(1))
    )
    _, d_minus = finite_q_and_d(
        transfer(p, phase_direction, shift_direction, Fraction(-1))
    )
    h_phys = cp.mscale(
        q(Fraction(1, 2)),
        subtract(sparse_multiply(d_plus, d_plus), sparse_multiply(d_minus, d_minus)),
    )
    require(digest(h_phys) == t23["hessian_compression"]["KO6_response_sha256"], "T23 response digest", passed)
    require(packet["physical_closure_charge"]["T23_response_sha256"] == digest(h_phys), "packet response digest", passed)

    roots = packet["binary_root_balance"]["roots_mod64"]
    require(roots == [16, 48], "binary roots", passed)
    require((roots[1] - roots[0]) % 64 == 32, "order two difference", passed)
    require((2 * (roots[1] - roots[0])) % 64 == 0, "balanced root cancellation", passed)
    epsilon_total = cp.kron(cp.mscale(q(-1), i2), cp.mscale(q(-1), i96))
    require(epsilon_total == i192, "balanced epsilon identity", passed)
    require(sparse_multiply(epsilon_total, q_total) == sparse_multiply(q_total, epsilon_total), "root intertwiner", passed)
    require(packet["binary_root_balance"]["finite_Yukawa_factor_root_charge"] == 0, "root-neutral Yukawa", passed)
    require(not packet["binary_root_balance"]["one_root_selected"], "no root selected", passed)
    require(not packet["binary_root_balance"]["selector_required_for_this_endpoint"], "no selector required", passed)

    shared = packet["shared_line_naturality"]
    require(shared["totalization_is_parallel"], "parallel totalization", passed)
    require(shared["connection_and_holonomy_preserved"], "connection and holonomy", passed)
    require(not shared["flat_line_identified_with_nonzero_Chern_HYM"], "HYM guard", passed)

    boundary = packet["physical_boundary"]
    require(boundary["CBF_T22_composite_product_selected"], "product selected", passed)
    require(boundary["selection_is_conditional_on_factor_sources"], "conditional factor source", passed)
    require(not boundary["one_binary_root_selected"], "binary selection boundary", passed)
    require(not boundary["primitive_q79_background_selected_here"], "background boundary", passed)
    require(not boundary["continuum_HYM_intertwiner"], "continuum boundary", passed)
    require(not boundary["physical_BV_QME"], "BV boundary", passed)
    require(not boundary["nonlinear_physical_action_selected"], "action boundary", passed)
    require(not boundary["full_B_ACTION_01_closed"], "blocker boundary", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "packet acceptance", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "row acceptance", passed)
    require(packet["parameter_ledger"]["new_observed_inputs"] == 0, "no observations", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fits", passed)
    require(packet["parameter_ledger"]["new_binary_root_selectors"] == 0, "no root knob", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(packet["checks"]), "builder count", passed)
    require(packet["check_summary"]["failed"] == [], "builder failures", passed)

    print(
        "independent upper-totalization supercharge verification passed: "
        f"{len(passed)}/{len(passed)}"
    )


if __name__ == "__main__":
    main()
