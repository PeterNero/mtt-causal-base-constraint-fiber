#!/usr/bin/env python3
"""Independently verify the CBF.T23 physical Yukawa-Hessian packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "physical_yukawa_hessian_source_lock.json"
SCHEMA = ROOT / "physical_yukawa_hessian_contract.schema.json"
THEOREM = ROOT / "PhysicalYukawaIncidenceKO6HessianCompressionTheorem_v1.md"
PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T22_PACKET = ROOT / "relative_product_supercharge.packet.json"
FINITE_BRANCH_PACKET = (
    ROOT.parent
    / "mtt-q79-total-superconnection-branching"
    / "artifacts"
    / "selected_finite_gauge_higgs_branching.packet.json"
)
YUKAWA_BRIDGE = (
    ROOT.parent
    / "mtt-sm-parity-closure"
    / "candidate_data"
    / "selected_yukawasourcebridge_or_magnitudeprojectionnogotheorem"
    / "same_source_yukawa_source_bridge.packet.json"
)
CONTINUUM_SM_CERT = (
    ROOT.parent
    / "mtt-qm-source-proof"
    / "certificates"
    / "q79_continuum_sm_classical_bv_composition.certificate.json"
)
HYPERBOLIC_CERT = (
    ROOT.parent
    / "mtt-qm-source-proof"
    / "certificates"
    / "q79_sm_gaugefixed_hyperbolic_bv_equicausal.certificate.json"
)

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    payload = json.dumps(wg.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def partial_isometry(pairs: tuple[tuple[int, int], ...]) -> cp.Matrix:
    result = cp.zero(16, 16)
    for target, source in pairs:
        result[target][source] = cp.ONE
    return result


def y_family(p: cp.Matrix, direction: cp.Matrix, t: Fraction) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), p), cp.mscale(q(t), direction))


def target_response(p: cp.Matrix, direction: cp.Matrix) -> cp.Matrix:
    return cp.mscale(
        q(-1),
        cp.madd(cp.matmul(p, cp.adjoint(direction)), cp.matmul(direction, p)),
    )


def source_response(p: cp.Matrix, direction: cp.Matrix) -> cp.Matrix:
    return cp.mscale(
        q(-1),
        cp.madd(cp.matmul(p, direction), cp.matmul(cp.adjoint(direction), p)),
    )


def routed_transfer(
    p: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    v_phase: cp.Matrix,
    v_shift: cp.Matrix,
    t: Fraction,
) -> cp.Matrix:
    return cp.madd(
        cp.kron(y_family(p, phase_direction, t), v_phase),
        cp.kron(y_family(p, shift_direction, t), v_shift),
    )


def d_particle(transfer: cp.Matrix) -> cp.Matrix:
    return cp.madd(transfer, cp.adjoint(transfer))


def block_diag(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return wg.block_diag([left, right])


def j_transform(matrix: cp.Matrix) -> cp.Matrix:
    half = len(matrix) // 2

    def swap(index: int) -> int:
        return index + half if index < half else index - half

    return [
        [cp.kconj(matrix[swap(row)][swap(column)]) for column in range(len(matrix))]
        for row in range(len(matrix))
    ]


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
    finite_branch = json.loads(FINITE_BRANCH_PACKET.read_text(encoding="utf-8"))
    yukawa_bridge = json.loads(YUKAWA_BRIDGE.read_text(encoding="utf-8"))
    continuum_sm = json.loads(CONTINUUM_SM_CERT.read_text(encoding="utf-8"))
    hyperbolic = json.loads(HYPERBOLIC_CERT.read_text(encoding="utf-8"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.physical-yukawa-hessian.v1", "schema", passed)
    require(packet["claim_id"] == "CBF.T23", "claim", passed)
    require(set(packet) == set(schema["required"]), "strict top-level keys", passed)
    require(set(packet) == set(schema["properties"]), "schema property keys", passed)
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source-lock hash", passed)
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash", passed)
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash", passed)

    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash {source['path']}", passed)

    require(t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()), "T20", passed)
    require(t22["claim_id"] == "CBF.T22" and all(t22["checks"].values()), "T22", passed)
    require(finite_branch["all_checks_pass"], "finite branch", passed)
    require(yukawa_bridge["closure_claimed"], "same-source bridge", passed)
    require(not yukawa_bridge["target_fitting_used"], "bridge no fit", passed)
    require(continuum_sm["all_checks_pass"], "continuum SM", passed)
    require(hyperbolic["all_checks_pass"], "hyperbolic source", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    identity16 = cp.identity(16)
    identity48 = cp.identity(48)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)

    phase_pairs = ((0, 6), (1, 7), (2, 8), (13, 14))
    shift_pairs = ((3, 9), (4, 10), (5, 11), (12, 15))
    v_phase = partial_isometry(phase_pairs)
    v_shift = partial_isometry(shift_pairs)
    v = cp.madd(v_phase, v_shift)
    r_phase = cp.matmul(cp.adjoint(v_phase), v_phase)
    r_shift = cp.matmul(cp.adjoint(v_shift), v_shift)
    l_phase = cp.matmul(v_phase, cp.adjoint(v_phase))
    l_shift = cp.matmul(v_shift, cp.adjoint(v_shift))
    right = cp.madd(r_phase, r_shift)
    left = cp.madd(l_phase, l_shift)
    require(cp.madd(left, right) == identity16, "complementary incidence halves", passed)
    require(wg.is_zero(cp.matmul(cp.adjoint(v_phase), v_shift)), "source orthogonality", passed)
    require(wg.is_zero(cp.matmul(v_phase, cp.adjoint(v_shift))), "target orthogonality", passed)
    require(cp.matrix_rank(left) == cp.matrix_rank(right) == 8, "incidence ranks", passed)

    b_minus = target_response(p, phase_direction)
    a_minus = target_response(p, shift_direction)
    b_plus = source_response(p, phase_direction)
    a_plus = source_response(p, shift_direction)
    h_minus = cp.madd(cp.kron(b_minus, r_phase), cp.kron(a_minus, r_shift))
    h_plus = cp.madd(cp.kron(b_plus, r_phase), cp.kron(a_plus, r_shift))
    w = cp.kron(identity3, v)
    h_left = cp.matmul(w, cp.matmul(h_minus, cp.adjoint(w)))
    h_right = h_plus
    h_particle = cp.madd(h_left, h_right)
    h_phys = block_diag(h_particle, matrix_conjugate(h_particle))

    plus = d_particle(
        routed_transfer(
            p, phase_direction, shift_direction, v_phase, v_shift, Fraction(1)
        )
    )
    minus = d_particle(
        routed_transfer(
            p, phase_direction, shift_direction, v_phase, v_shift, Fraction(-1)
        )
    )
    direct_derivative = cp.mscale(
        q(Fraction(1, 2)),
        matrix_sub(cp.matmul(plus, plus), cp.matmul(minus, minus)),
    )
    require(direct_derivative == h_particle, "direct Hessian reconstruction", passed)
    require(matrix_digest(h_minus) == t22["routed_internal_family"]["target_response_sha256"], "target T22 digest", passed)
    require(matrix_digest(h_plus) == t22["routed_internal_family"]["source_response_sha256"], "source T22 digest", passed)
    require(packet["hessian_compression"]["target_response_sha256"] == matrix_digest(h_minus), "packet target digest", passed)
    require(packet["hessian_compression"]["source_response_sha256"] == matrix_digest(h_plus), "packet source digest", passed)
    require(packet["hessian_compression"]["particle_response_sha256"] == matrix_digest(h_particle), "packet particle digest", passed)
    require(packet["hessian_compression"]["KO6_response_sha256"] == matrix_digest(h_phys), "packet KO6 digest", passed)
    require(wg.is_zero(cp.matmul(h_left, h_right)), "Hessian support orthogonality", passed)
    require(cp.matrix_rank(h_left) == 24, "target rank", passed)
    require(cp.matrix_rank(h_right) == 24, "source rank", passed)
    require(cp.matrix_rank(h_particle) == 48, "particle rank", passed)
    require(wg.frobenius(h_particle, h_particle) == q(384), "particle norm", passed)
    require(wg.frobenius(h_phys, h_phys) == q(768), "KO6 norm", passed)

    transfer_zero = routed_transfer(
        p, phase_direction, shift_direction, v_phase, v_shift, Fraction(0)
    )
    d_zero = d_particle(transfer_zero)
    require(wg.is_zero(cp.matmul(transfer_zero, transfer_zero)), "nilpotent transfer", passed)
    require(cp.matmul(d_zero, d_zero) == identity48, "neutral square", passed)

    sample = d_particle(
        routed_transfer(
            p, phase_direction, shift_direction, v_phase, v_shift, Fraction(2, 3)
        )
    )
    physical_sample = block_diag(sample, matrix_conjugate(sample))
    left_slots = {0, 1, 2, 3, 4, 5, 12, 13}
    gamma16 = [-1 if index in left_slots else 1 for index in range(16)]
    gamma48 = gamma16 * 3
    gamma96 = gamma48 + [-value for value in gamma48]
    require(sample == cp.adjoint(sample), "particle self-adjoint", passed)
    require(physical_sample == cp.adjoint(physical_sample), "KO6 self-adjoint", passed)
    require(j_transform(physical_sample) == physical_sample, "KO6 J reality", passed)
    require(
        all(
            cp.kmul(q(gamma96[row] + gamma96[column]), physical_sample[row][column])
            == cp.ZERO
            for row in range(96)
            for column in range(96)
        ),
        "KO6 oddness",
        passed,
    )

    q6_sums = {"u": 1 + 3 - 4, "d": 1 - 3 + 2, "e": -3 - 3 + 6, "N": -3 + 3}
    require(all(value == 0 for value in q6_sums.values()), "hypercharge sums", passed)
    require(
        continuum_sm["higgs_yukawa_checks"]["all_four_Yukawa_color_contractions_are_singlets"],
        "color singlets",
        passed,
    )
    require(
        continuum_sm["higgs_yukawa_checks"]["all_four_Yukawa_weak_contractions_are_singlets"],
        "weak singlets",
        passed,
    )
    require(
        continuum_sm["higgs_yukawa_checks"]["one_A51_Higgs_doublet_supplies_every_channel"],
        "one Higgs",
        passed,
    )
    require(all(hyperbolic["principal_symbol_checks"].values()), "principal symbol", passed)

    boundary = packet["physical_boundary"]
    require(boundary["finite_physical_Yukawa_Laplacian_typed"], "finite physical typing", passed)
    require(not boundary["full_selected_Lorentz_Higgs_Yukawa_endpoint"], "full endpoint boundary", passed)
    require(not boundary["upper_MTT_composite_root_selected"], "root selection boundary", passed)
    require(not boundary["numerical_Higgs_vacuum_selected"], "Higgs value boundary", passed)
    require(not boundary["continuum_HYM_intertwiner"], "HYM boundary", passed)
    require(not boundary["physical_BV4_pushforward"], "BV boundary", passed)
    require(not boundary["scalar_Higgs_potential_Hessian_claimed"], "scalar-Hessian boundary", passed)
    require(not boundary["first_order_fermionic_action_replaced"], "fermionic-action boundary", passed)
    require(not boundary["eta9_or_new_worker_used"], "independent route", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "packet count", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "row count", passed)
    require(packet["parameter_ledger"]["new_observed_inputs"] == 0, "no observations", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fits", passed)
    require(packet["parameter_ledger"]["sector_specific_scale_parameters"] == 0, "no sector scales", passed)
    require(all(packet["checks"].values()), "builder checks all true", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(packet["checks"]), "builder count", passed)
    require(packet["check_summary"]["failed"] == [], "builder failures empty", passed)

    print(
        "independent physical Yukawa-Hessian verification passed: "
        f"{len(passed)}/{len(passed)}"
    )


if __name__ == "__main__":
    main()
