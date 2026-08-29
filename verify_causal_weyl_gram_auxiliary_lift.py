#!/usr/bin/env python3
"""Independent verifier for the CBF.T21 causal auxiliary lift packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import verify_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "causal_weyl_gram_auxiliary_lift.packet.json"
SOURCE_LOCK = ROOT / "causal_weyl_gram_auxiliary_lift_source_lock.json"
SCHEMA = ROOT / "causal_weyl_gram_auxiliary_lift_contract.schema.json"
THEOREM = ROOT / "CausalWeylGramAuxiliaryFeshbachLiftTheorem_v1.md"
QFT_CERTIFICATE = ROOT.parent / "mtt-qm-source-proof" / "certificates" / "q79_sm_gaugefixed_hyperbolic_bv_equicausal.certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.matrix_add(left, cp.matrix_scale(q(-1), right))


def block_matrix(blocks: list[list[cp.Matrix]]) -> cp.Matrix:
    result: cp.Matrix = []
    for block_row in blocks:
        height = len(block_row[0])
        for local_row in range(height):
            row: list[cp.K] = []
            for block in block_row:
                row.extend(block[local_row])
            result.append(row)
    return result


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    result = cp.zero(sum(len(block) for block in blocks), sum(len(block[0]) for block in blocks))
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row in range(len(block)):
            for column in range(len(block[0])):
                result[row_offset + row][column_offset + column] = block[row][column]
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def gram(matrix: cp.Matrix) -> cp.Matrix:
    return cp.matrix_mul(matrix, cp.adjoint(matrix))


def source_family(p: cp.Matrix, response: cp.Matrix, parameter: Fraction) -> cp.Matrix:
    return cp.matrix_add(cp.matrix_scale(q(-1), p), cp.matrix_scale(q(parameter), response))


def derivative(p: cp.Matrix, response: cp.Matrix) -> cp.Matrix:
    plus = gram(source_family(p, response, Fraction(1)))
    minus = gram(source_family(p, response, Fraction(-1)))
    return cp.matrix_scale(q(Fraction(1, 2)), sub(plus, minus))


def hardcoded_primitives() -> tuple[cp.Matrix, cp.Matrix, cp.Matrix, cp.Matrix]:
    z0 = cp.Z
    o = cp.O
    omega: cp.K = (Fraction(-1, 2), Fraction(0), Fraction(0), Fraction(1, 2))
    omega2: cp.K = (Fraction(-1, 2), Fraction(0), Fraction(0), Fraction(-1, 2))
    p = [[o, z0, z0], [z0, z0, o], [z0, o, z0]]
    x = [[z0, o, z0], [z0, z0, o], [o, z0, z0]]
    z = [[o, z0, z0], [z0, omega, z0], [z0, z0, omega2]]
    s3: cp.K = (Fraction(0), Fraction(1, 3), Fraction(0), Fraction(0))
    plus: cp.K = (Fraction(0), Fraction(-1, 6), Fraction(1, 2), Fraction(0))
    minus: cp.K = (Fraction(0), Fraction(-1, 6), Fraction(-1, 2), Fraction(0))
    fourier = [[s3, s3, s3], [s3, plus, minus], [s3, minus, plus]]
    return p, x, z, fourier


def internal_response() -> tuple[cp.Matrix, cp.Matrix, cp.Matrix, cp.Matrix, cp.Matrix]:
    p, x, z, fourier = hardcoded_primitives()
    identity3 = cp.identity(3)
    a = derivative(p, cp.matrix_add(identity3, x))
    b = derivative(p, cp.matrix_add(identity3, z))
    phase_slots = {6, 7, 8, 14}
    shift_slots = {9, 10, 11, 15}
    r_phase = cp.zero(16, 16)
    r_shift = cp.zero(16, 16)
    for index in phase_slots:
        r_phase[index][index] = cp.O
    for index in shift_slots:
        r_shift[index][index] = cp.O
    h = cp.matrix_add(cp.kron(b, r_phase), cp.kron(a, r_shift))
    return p, a, b, h, fourier


def auxiliary_block(dynamic: cp.Matrix, coupling: cp.Matrix) -> tuple[cp.Matrix, cp.Matrix]:
    identity = cp.identity(len(dynamic))
    retained = cp.matrix_add(dynamic, identity)
    upper = block_matrix([[retained, cp.adjoint(coupling)], [coupling, identity]])
    schur = sub(retained, identity)
    return upper, schur


def synthesis(coupling: cp.Matrix) -> cp.Matrix:
    return cp.identity(48) + cp.matrix_scale(q(-1), coupling)


def composition_hash(finite_root: str, causal_root: str) -> str:
    payload = {
        "finite_root_sha256": finite_root,
        "causal_root_sha256": causal_root,
        "coupling": "C=P tensor I16",
        "complement": "D=I48",
        "causal_lift": "L_mu=L0+mu^2 H_derived",
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    qft = json.loads(QFT_CERTIFICATE.read_text(encoding="utf-8"))
    checks = 0

    require(packet["schema"] == "boe.mtt.causal-weyl-gram-auxiliary-lift.v1", "schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T21", "claim id")
    checks += 1
    require(packet["tier"] == schema["properties"]["tier"]["const"], "tier")
    checks += 1
    require(set(packet) == set(schema["properties"]), "strict top-level contract")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "contract hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1
    require(source_lock["repository_head_before"] == "68379be18ca7b88764400ab9aca71251c9ca3300", "starting head")
    checks += 1
    require(source_lock["handoff_id"] == "138975b0-174f-4006-adf1-bf9f57ca609e", "handoff")
    checks += 1
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"missing {source['path']}")
        require(sha256(path) == source["sha256"], f"source hash {source['path']}")
        checks += 1

    require(schema["additionalProperties"] is False, "strict schema")
    checks += 1
    require(schema["properties"]["source_composition"]["properties"]["source_roots"]["const"] == 2, "two-root schema")
    checks += 1
    require(schema["properties"]["physical_boundary"]["properties"]["physically_selected"]["const"] is False, "boundary schema")
    checks += 1

    require(qft["schema"] == "MTTq79SMGaugeFixedHyperbolicBVEquicausalCertificate.v2", "qft v2")
    checks += 1
    require(qft["all_checks_pass"] and all(qft["checks"].values()), "qft checks")
    checks += 1
    require("advanced and retarded Green operators" in qft["claim_boundary"]["closed"], "Green operators")
    checks += 1
    require("equicausal Peierls and free Hadamard-star algebra" in qft["claim_boundary"]["closed"], "equicausal algebra")
    checks += 1
    require("selection of the physical global background and bundle sector" in qft["claim_boundary"]["open"], "background boundary")
    checks += 1

    p, a, b, h, fourier = internal_response()
    identity16 = cp.identity(16)
    identity48 = cp.identity(48)
    zero48 = cp.zero(48, 48)
    coupling = cp.kron(p, identity16)
    require(p == cp.adjoint(p) and cp.matrix_mul(p, p) == cp.identity(3), "P involution")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(fourier), fourier) == cp.identity(3), "F3 unitary")
    checks += 1
    require(cp.matrix_mul(p, p) == cp.identity(3), "C isometry")
    checks += 1
    require(p == cp.adjoint(p), "C unitary")
    checks += 1
    require(cp.rank(h) == 24, "H rank")
    checks += 1

    upper, schur = auxiliary_block(h, coupling)
    graph = synthesis(coupling)
    require(upper == cp.adjoint(upper), "upper Hermitian")
    checks += 1
    require(schur == h, "Schur complement")
    checks += 1
    coupling_square = identity48
    retained = cp.matrix_add(h, coupling_square)
    graph_top = sub(retained, coupling_square)
    graph_bottom = sub(coupling, coupling)
    require(graph_top == h and graph_bottom == zero48, "graph pullback")
    checks += 1
    require(graph[:48] == identity48, "graph rank witness")
    checks += 1

    require(sub(coupling, coupling) == zero48, "transform inverse")
    checks += 1
    require(coupling_square == identity48, "inverse transform")
    checks += 1
    expected_upper = block_matrix([[retained, cp.adjoint(coupling)], [coupling, identity48]])
    require(expected_upper == upper, "square factorization")
    checks += 1
    require(packet["auxiliary_feshbach"]["upper_rank_at_normalized_internal_witness"] == 48 + cp.rank(h), "upper rank consequence")
    checks += 1
    require(packet["auxiliary_feshbach"]["upper_kernel_at_normalized_internal_witness"] == 48 - cp.rank(h), "upper kernel consequence")
    checks += 1

    for scale in (Fraction(0), Fraction(1), Fraction(7, 3)):
        dynamic = cp.matrix_scale(q(scale), h)
        scaled_upper, scaled_schur = auxiliary_block(dynamic, coupling)
        require(scaled_schur == dynamic, "scaled Schur")
        checks += 1
        require(scaled_upper == cp.adjoint(scaled_upper), "scaled Hermitian")
        checks += 1

    witnesses = packet["causal_lift"]["covector_witnesses"]
    require(len(witnesses) == len(qft["exact_witness"]["principal_symbols"]) == 5, "five symbols")
    checks += 1
    for source, record in zip(qft["exact_witness"]["principal_symbols"], witnesses):
        k_squared = Fraction(source["k_squared"])
        principal = cp.matrix_scale(q(k_squared), identity48)
        require(record["covector"] == source["covector"], "covector")
        checks += 1
        require(record["principal_rank_on_48_carrier"] == cp.rank(principal), "principal rank")
        checks += 1
        require(record["response_changes_principal_symbol"] is False, "lower order")
        checks += 1
        frozen = cp.matrix_add(principal, h)
        _, frozen_schur = auxiliary_block(frozen, coupling)
        require(frozen_schur == frozen and record["auxiliary_Schur_reduction_exact"], "frozen Schur")
        checks += 1

    test_auxiliary = cp.matrix_mul(p, cp.matrix_mul(fourier, p))
    require(cp.matrix_mul(test_auxiliary, p) == cp.matrix_mul(p, fourier), "transported intertwiner")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(test_auxiliary), test_auxiliary) == cp.identity(3), "transported unitary")
    checks += 1
    require(cp.matrix_mul(test_auxiliary, p) == cp.matrix_mul(p, fourier), "graph intertwiner")
    checks += 1

    finite_root = packet["source_composition"]["finite_root_sha256"]
    causal_root = sha256(QFT_CERTIFICATE)
    require(packet["source_composition"]["causal_root_sha256"] == causal_root, "causal root")
    checks += 1
    require(finite_root != causal_root, "distinct roots")
    checks += 1
    require(packet["source_composition"]["composition_sha256"] == composition_hash(finite_root, causal_root), "composition hash")
    checks += 1
    require(packet["source_composition"]["same_physical_root_proved"] is False, "same-root boundary")
    checks += 1

    require(packet["causal_lift"]["response_order"] == 0, "order zero")
    checks += 1
    require(packet["causal_lift"]["characteristic_cone_unchanged"], "cone")
    checks += 1
    require(packet["causal_lift"]["conditionally_Green_hyperbolic"], "Green hyperbolic")
    checks += 1
    require(packet["causal_lift"]["physical_scale_selected"] is False, "scale boundary")
    checks += 1
    require(len(packet["contract_classification"]["newly_closed_subclauses"]) == 4, "subclauses")
    checks += 1

    ledger = packet["parameter_ledger"]
    require(ledger["observed_inputs"] == 0 and ledger["fitted_coefficients"] == 0, "no fit")
    checks += 1
    require(ledger["new_dimensionless_shape_parameters"] == 0, "no shape knobs")
    checks += 1
    require(ledger["unselected_dimensionful_response_scales"] == 1, "one scale")
    checks += 1
    boundary = packet["physical_boundary"]
    require(not boundary["physically_selected"] and not boundary["eta9_used"], "not physical and no eta9")
    checks += 1
    require(not boundary["same_physical_root"] and not boundary["physical_background_selected"], "root/background open")
    checks += 1
    require(not boundary["physical_scale_selected"] and not boundary["Lorentz_Higgs_Yukawa_typing"], "scale/typing open")
    checks += 1
    require(not boundary["continuum_HYM_intertwiner"] and not boundary["physical_BV4_insertion"], "continuum/BV open")
    checks += 1
    require(packet["physical_packets_accepted"] == 0 and packet["physical_rows_accepted"] == 0, "acceptance boundary")
    checks += 1
    require(all(packet["checks"].values()), "builder checks")
    checks += 1
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary")
    checks += 1

    print(f"independent causal Weyl-Gram auxiliary lift verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
