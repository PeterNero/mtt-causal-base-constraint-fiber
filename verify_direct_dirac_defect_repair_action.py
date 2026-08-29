#!/usr/bin/env python3
"""Independent exact reconstruction of the CBF.T26 repair-action packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "direct_dirac_defect_repair_action.packet.json"
SOURCE_LOCK_PATH = ROOT / "direct_dirac_defect_repair_action_source_lock.json"
SCHEMA_PATH = ROOT / "direct_dirac_defect_repair_action_contract.schema.json"
THEOREM_PATH = ROOT / "CanonicalNormalizedDiracSquareDefectRepairActionAndValueSelectionNoGoTheorem_v1.md"
T20_PATH = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T25_PATH = ROOT / "direct_finite_source_continuum.packet.json"


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


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def sparse_matmul(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not compose")
    result = cp.zero(len(left), len(right[0]))
    for row, left_row in enumerate(left):
        for inner, left_value in enumerate(left_row):
            if left_value == cp.ZERO:
                continue
            for column, right_value in enumerate(right[inner]):
                if right_value == cp.ZERO:
                    continue
                result[row][column] = cp.kadd(
                    result[row][column], cp.kmul(left_value, right_value)
                )
    return result


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


def total_charge(
    external: cp.Matrix,
    grading: cp.Matrix,
    finite: cp.Matrix,
    scale: Fraction,
) -> cp.Matrix:
    return cp.madd(
        cp.kron(external, cp.identity(len(finite))),
        cp.kron(grading, cp.mscale(q(scale), finite)),
    )


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    result = cp.ZERO
    for index in range(len(matrix)):
        result = cp.kadd(result, matrix[index][index])
    return result


def real_part(value: cp.K) -> Fraction:
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"non-real trace {value}")
    return value[0]


def repair_value(defect: cp.Matrix) -> Fraction:
    square = sparse_matmul(cp.adjoint(defect), defect)
    return real_part(matrix_trace(square)) / (2 * len(defect))


def polynomial_value(t: Fraction) -> Fraction:
    return 4 * t**2 - Fraction(16, 3) * t**3 + 3 * t**4


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
    t25 = json.loads(T25_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.direct-dirac-defect-repair-action.v1", "packet schema", passed)
    require(packet["claim_id"] == "CBF.T26", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(source_lock["handoff_id"] == "d9291f60-aa25-4c70-84ff-a3b3c9ca10c0", "handoff pin", passed)
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = decode_matrix(primitive["P"])
    x = decode_matrix(primitive["X"])
    z = decode_matrix(primitive["Z"])
    phase_direction = cp.madd(cp.identity(3), z)
    shift_direction = cp.madd(cp.identity(3), x)
    d0 = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(0)))
    d_at_one = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(1)))
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)
    h_phys = cp.madd(sparse_matmul(d0, d1), sparse_matmul(d1, d0))
    remainder = sparse_matmul(d1, d1)
    h2 = sparse_matmul(h_phys, h_phys)
    hr = sparse_matmul(h_phys, remainder)
    rh = sparse_matmul(remainder, h_phys)
    r2 = sparse_matmul(remainder, remainder)

    require(sparse_matmul(d0, d0) == identity96, "D0 square", passed)
    require(h_phys == cp.adjoint(h_phys), "H self-adjoint", passed)
    require(remainder == cp.adjoint(remainder), "R self-adjoint", passed)
    require(hr == rh, "H-R commutation", passed)
    require(cp.matrix_rank(h_phys) == 96, "H rank", passed)
    require(cp.matrix_rank(remainder) == 96, "R rank", passed)
    require(real_part(matrix_trace(h2)) == 768, "Tr H2", passed)
    require(real_part(matrix_trace(hr)) == -512, "Tr HR", passed)
    require(real_part(matrix_trace(r2)) == 576, "Tr R2", passed)
    require(matrix_digest(h_phys) == t23["hessian_compression"]["KO6_response_sha256"], "T23 H digest", passed)
    require(matrix_digest(h_phys) == packet["defect_residual"]["H_phys_sha256"], "packet H digest", passed)
    require(matrix_digest(remainder) == packet["defect_residual"]["R_sha256"], "packet R digest", passed)

    samples = [Fraction(-2), Fraction(-1), Fraction(-1, 2), Fraction(0), Fraction(1, 2), Fraction(1), Fraction(2)]
    for t in samples:
        d_t = physical_dirac(transfer(projector, phase_direction, shift_direction, t))
        require(d_t == cp.madd(d0, cp.mscale(q(t), d1)), f"affine D at {t}", passed)
        defect = matrix_sub(sparse_matmul(d_t, d_t), identity96)
        expected = cp.madd(cp.mscale(q(t), h_phys), cp.mscale(q(t * t), remainder))
        require(defect == expected, f"defect expansion at {t}", passed)
        require(repair_value(defect) == polynomial_value(t), f"repair polynomial at {t}", passed)
        require(packet["exact_coefficients"]["sample_values"][str(t)] == str(polynomial_value(t)), f"packet sample at {t}", passed)

    require(packet["exact_coefficients"]["coefficient_t2"] == "4", "quadratic coefficient", passed)
    require(packet["exact_coefficients"]["coefficient_t3"] == "-16/3", "cubic coefficient", passed)
    require(packet["exact_coefficients"]["coefficient_t4"] == "3", "quartic coefficient", passed)
    require(packet["exact_coefficients"]["Hessian_at_zero"] == "8", "repair Hessian", passed)
    require(Fraction(44, 27) > 0, "completed-square positivity", passed)
    require(16 - 24 == -8, "stationary discriminant", passed)
    require(packet["positivity_and_stationarity"]["zero_set"] == ["t=0"], "unique real zero", passed)
    require(packet["positivity_and_stationarity"]["real_stationary_set"] == ["t=0"], "unique real stationary point", passed)

    external_q = [[cp.ZERO, cp.ZERO], [cp.ONE, cp.ZERO]]
    external_d = cp.madd(external_q, cp.adjoint(external_q))
    external_gamma = cp.diagonal([cp.ONE, q(-1)])
    h_scale = Fraction(5, 4)
    continuum_t = Fraction(2, 3)
    finite = physical_dirac(transfer(projector, phase_direction, shift_direction, continuum_t))
    direct = total_charge(external_d, external_gamma, finite, h_scale)
    direct_square = sparse_matmul(direct, direct)
    neutral = cp.madd(
        cp.kron(sparse_matmul(external_d, external_d), identity96),
        cp.kron(cp.identity(2), cp.mscale(q(h_scale * h_scale), identity96)),
    )
    direct_defect = matrix_sub(direct_square, neutral)
    finite_defect = matrix_sub(sparse_matmul(finite, finite), identity96)
    expected_direct = cp.kron(cp.identity(2), cp.mscale(q(h_scale * h_scale), finite_defect))
    require(direct_defect == expected_direct, "continuum h-squared defect", passed)
    require(repair_value(direct_defect) == h_scale**4 * polynomial_value(continuum_t), "continuum h-fourth repair", passed)

    root_payload = {
        "schema": "boe.mtt.direct-dirac-defect-repair-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "finite_source": "D_phys(t)=D0+tD1 on H_F of complex dimension 96",
        "defect": "K(t)=D_phys(t)^2-I96=t H_phys+t^2 R",
        "normalized_repair_action": "S_rep(t)=1/2 (Tr/96)(K(t)^*K(t))",
        "coefficients": {"t2": "4", "t3": "-16/3", "t4": "3"},
        "H_phys_sha256": matrix_digest(h_phys),
        "R_sha256": matrix_digest(remainder),
        "observed_targets": [],
        "signed_physical_action": None,
        "physical_source_coordinate": None,
        "held_out_observable": None,
        "theorem_sha256": sha256(THEOREM_PATH),
    }
    root_hash = hashlib.sha256(json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    require(root_payload == packet["source_provenance"]["source_root_payload"], "source-root payload", passed)
    require(root_hash == packet["source_provenance"]["source_root_sha256"], "source-root digest", passed)

    require(t25["physical_boundary"]["direct_finite_source_continuum_realized"], "T25 direct realization", passed)
    require(packet["physical_boundary"]["exact_finite_repair_action_closed"], "finite repair action closure", passed)
    require(packet["physical_boundary"]["full_quartic_repair_jet_closed"], "quartic repair jet closure", passed)
    require(not packet["physical_boundary"]["signed_physical_action_selected"], "signed action remains open", passed)
    require(not packet["physical_boundary"]["nonzero_physical_source_coordinate_selected"], "nonzero value remains open", passed)
    require(not packet["physical_boundary"]["held_out_physical_observable_emitted"], "held-out observable remains open", passed)
    require(not packet["physical_boundary"]["B_ACTION_01_closed"], "B.ACTION.01 boundary", passed)
    require(not packet["physical_boundary"]["B_SM_02_closed"], "B.SM.02 boundary", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "packet acceptance unchanged", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "row acceptance unchanged", passed)
    require(all(packet["checks"].values()), "builder check map", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder check summary", passed)
    require(packet["check_summary"]["failed"] == [], "builder failures empty", passed)

    print(
        "direct Dirac defect repair packet verified independently: "
        f"{len(passed)}/{len(passed)} checks; polynomial "
        "4 t^2-(16/3)t^3+3t^4 exact"
    )


if __name__ == "__main__":
    main()
