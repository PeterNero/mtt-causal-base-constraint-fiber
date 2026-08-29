#!/usr/bin/env python3
"""Independent verifier for the CBF.T20 Weyl-Gram source packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import verify_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
SOURCE_LOCK = ROOT / "weyl_gram_closure_repair_source_lock.json"
SCHEMA = ROOT / "weyl_gram_closure_repair_contract.schema.json"
THEOREM = ROOT / "WeylGramClosureRepairRelativeResponseSourceTheorem_v1.md"
FSB_MANIFEST = ROOT.parent / "mtt-q79-total-superconnection-branching" / "state" / "source_manifest.v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.matrix_add(left, cp.matrix_scale(q(-1), right))


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


def commutator(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return sub(cp.matrix_mul(left, right), cp.matrix_mul(right, left))


def is_zero(matrix: cp.Matrix) -> bool:
    return matrix == cp.zero(len(matrix), len(matrix[0]))


def inverse(matrix: cp.Matrix) -> cp.Matrix:
    size = len(matrix)
    work = [row[:] + identity_row[:] for row, identity_row in zip(matrix, cp.identity(size))]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column] != cp.Z)
        work[column], work[pivot] = work[pivot], work[column]
        pivot_inverse = cp.inverse(work[column][column])
        work[column] = [cp.mul(pivot_inverse, value) for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor == cp.Z:
                continue
            work[row] = [
                cp.add(value, cp.neg(cp.mul(factor, pivot_value)))
                for value, pivot_value in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def frobenius(left: cp.Matrix, right: cp.Matrix) -> cp.K:
    total = cp.Z
    for row in range(len(left)):
        for column in range(len(left[0])):
            total = cp.add(total, cp.mul(cp.conj(left[row][column]), right[row][column]))
    return total


def flatten(matrix: cp.Matrix) -> list[cp.K]:
    return [value for row in matrix for value in row]


def span_rank(matrices: Iterable[cp.Matrix]) -> int:
    vectors = [flatten(matrix) for matrix in matrices]
    return cp.rank([list(column) for column in zip(*vectors)])


def gram(matrix: cp.Matrix) -> cp.Matrix:
    return cp.matrix_mul(matrix, cp.adjoint(matrix))


def source_family(p: cp.Matrix, response: cp.Matrix, parameter: Fraction) -> cp.Matrix:
    return cp.matrix_add(cp.matrix_scale(q(-1), p), cp.matrix_scale(q(parameter), response))


def derivative(p: cp.Matrix, response: cp.Matrix) -> cp.Matrix:
    plus = gram(source_family(p, response, Fraction(1)))
    minus = gram(source_family(p, response, Fraction(-1)))
    return cp.matrix_scale(q(Fraction(1, 2)), sub(plus, minus))


def derivative_formula(p: cp.Matrix, response: cp.Matrix) -> cp.Matrix:
    return cp.matrix_scale(
        q(-1),
        cp.matrix_add(
            cp.matrix_mul(p, cp.adjoint(response)),
            cp.matrix_mul(response, p),
        ),
    )


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


def hardcoded_responses() -> tuple[cp.Matrix, cp.Matrix]:
    a = [[q(-2), cp.Z, q(-2)], [cp.Z, q(-2), q(-2)], [q(-2), q(-2), cp.Z]]
    b = [
        [q(-4), cp.Z, cp.Z],
        [cp.Z, cp.Z, (Fraction(-1), Fraction(0), Fraction(0), Fraction(-1))],
        [cp.Z, (Fraction(-1), Fraction(0), Fraction(0), Fraction(1)), cp.Z],
    ]
    return a, b


def canonical_root(
    p: cp.Matrix,
    x: cp.Matrix,
    z: cp.Matrix,
    fourier: cp.Matrix,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "P": cp.encode_matrix(p),
        "X": cp.encode_matrix(x),
        "Z": cp.encode_matrix(z),
        "F3": cp.encode_matrix(fourier),
        "route": {
            "phase_sectors": ["u", "e"],
            "shift_sectors": ["d", "N"],
            "phase_H16_slots": [6, 7, 8, 14],
            "shift_H16_slots": [9, 10, 11, 15],
        },
        "source_line": ["t", "t", "t", "t"],
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest(), payload


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    checks = 0

    require(packet["schema"] == "boe.mtt.weyl-gram-closure-repair-source.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T20", "claim id")
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
    require(packet["finite_source_manifest_sha256"] == sha256(FSB_MANIFEST), "manifest hash")
    checks += 1
    require(source_lock["repository_head_before"] == "99aa5287e07ba269072e4dde543ed7dd67b2e562", "starting head")
    checks += 1
    require(source_lock["handoff_id"] == "6e3b0647-30a0-4529-af43-7c61b0004cca", "handoff id")
    checks += 1
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"missing {source['path']}")
        require(sha256(path) == source["sha256"], f"source hash {source['path']}")
        checks += 1

    require(schema["additionalProperties"] is False, "strict schema")
    checks += 1
    require(schema["properties"]["primitive_source"]["properties"]["observed_inputs"]["const"] == 0, "schema observations")
    checks += 1
    require(schema["properties"]["physical_boundary"]["properties"]["physically_selected"]["const"] is False, "schema boundary")
    checks += 1

    p, x, z, fourier = hardcoded_primitives()
    a_expected, b_expected = hardcoded_responses()
    identity3 = cp.identity(3)
    zero3 = cp.zero(3, 3)
    require(p == cp.adjoint(p) and cp.matrix_mul(p, p) == identity3, "P involution")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(fourier), fourier) == identity3, "F3 unitary")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(p, fourier)) == p, "P Fourier invariant")
    checks += 1

    m_shift = cp.matrix_add(identity3, x)
    m_phase = cp.matrix_add(identity3, z)
    require(cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(m_shift, fourier)) == m_phase, "Weyl response orbit")
    checks += 1
    a = derivative(p, m_shift)
    b = derivative(p, m_phase)
    require(a == derivative_formula(p, m_shift), "shift derivative formula")
    checks += 1
    require(b == derivative_formula(p, m_phase), "phase derivative formula")
    checks += 1
    require(a == a_expected and b == b_expected, "hardcoded response values")
    checks += 1
    require(a == cp.adjoint(a) and b == cp.adjoint(b), "Hermitian derivatives")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(a, fourier)) == b, "derivative Fourier orbit")
    checks += 1
    require(gram(source_family(p, m_shift, Fraction(0))) == identity3, "neutral shift Gram")
    checks += 1
    require(gram(source_family(p, m_phase, Fraction(0))) == identity3, "neutral phase Gram")
    checks += 1
    for parameter in (Fraction(-3, 2), Fraction(0), Fraction(7, 3)):
        ys = source_family(p, m_shift, parameter)
        yp = source_family(p, m_phase, parameter)
        require(yp == cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(ys, fourier)), "family covariance")
        checks += 1
        require(gram(yp) == cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(gram(ys), fourier)), "Gram covariance")
        checks += 1
        require(gram(ys) == cp.adjoint(gram(ys)), "Gram Hermitian")
        checks += 1

    require(cp.decode_matrix(packet["gram_derivation"]["shift_first_variation"]) == a, "packet shift derivative")
    checks += 1
    require(cp.decode_matrix(packet["gram_derivation"]["phase_first_variation"]) == b, "packet phase derivative")
    checks += 1

    sector = [
        block_diag([b, zero3, zero3, zero3]),
        block_diag([zero3, b, zero3, zero3]),
        block_diag([zero3, zero3, a, zero3]),
        block_diag([zero3, zero3, zero3, a]),
    ]
    paired = [block_diag([b, zero3, a, zero3]), block_diag([zero3, b, zero3, a])]
    shared = block_diag([b, b, a, a])
    anti = block_diag([b, cp.matrix_scale(q(-1), b), a, cp.matrix_scale(q(-1), a)])
    require(span_rank(sector) == 4, "sector coordinate dimension")
    checks += 1
    require(span_rank(paired) == 2, "paired coordinate dimension")
    checks += 1
    require(span_rank([shared]) == 1, "shared coordinate dimension")
    checks += 1
    require(span_rank([shared, anti]) == 2, "anti-coordinate independent")
    checks += 1
    require(packet["universal_routing"]["coordinate_dimension_ladder"] == [4, 2, 1], "packet coordinate ladder")
    checks += 1

    phase_slots = {6, 7, 8, 14}
    shift_slots = {9, 10, 11, 15}
    r_phase = cp.zero(16, 16)
    r_shift = cp.zero(16, 16)
    for index in phase_slots:
        r_phase[index][index] = cp.O
    for index in shift_slots:
        r_shift[index][index] = cp.O
    h48 = cp.matrix_add(cp.kron(b, r_phase), cp.kron(a, r_shift))
    require(h48 == cp.adjoint(h48), "H48 Hermitian")
    checks += 1
    require(cp.rank(h48) == 24, "H48 rank")
    checks += 1
    require(frobenius(h48, h48) == q(192), "H48 norm")
    checks += 1

    h6 = block_diag([b, a])
    identity6 = cp.identity(6)
    relative = cp.matrix_mul(inverse(h6), h6)
    require(relative == identity6, "relative identity")
    checks += 1
    a6 = block_diag([a, a])
    b6 = block_diag([b, b])
    parity = block_diag([identity3, cp.matrix_scale(q(-1), identity3)])
    exchange = [zero3[row] + cp.adjoint(fourier)[row] for row in range(3)] + [fourier[row] + zero3[row] for row in range(3)]
    for generator in (a6, b6, parity, exchange):
        require(is_zero(commutator(relative, generator)), "relative commutator")
        checks += 1
    require(cp.decode_matrix(packet["relative_intertwiner"]["T_rel"]) == identity6, "packet Trel")
    checks += 1
    require(packet["relative_intertwiner"]["comparison_commutant_dimension_from_CBF_T19"] == 1, "T19 scalar commutant")
    checks += 1

    root_sha, root_payload = canonical_root(p, x, z, fourier)
    require(root_sha == packet["primitive_root_sha256"], "primitive root hash")
    checks += 1
    require(root_payload == packet["primitive_source"]["primitive_payload"], "primitive root payload")
    checks += 1
    require(all(name not in root_payload for name in ("H_resp", "A_shift", "B_phase")), "target excluded")
    checks += 1

    require(packet["finite_action"]["finite_identity_synthesis"] is True, "finite identity synthesis")
    checks += 1
    require(packet["finite_action"]["physical_SYN_packet"] is False, "not physical synthesis")
    checks += 1
    require(packet["parameter_ledger"]["observed_construction_inputs"] == 0, "no observations")
    checks += 1
    require(packet["parameter_ledger"]["fitted_matrix_coefficients"] == 0, "no fits")
    checks += 1
    require(packet["parameter_ledger"]["new_continuous_response_shape_parameters"] == 0, "no response-shape knob")
    checks += 1
    require(packet["parameter_ledger"]["shared_finite_source_coordinates"] == 1, "one shared coordinate")
    checks += 1
    require(packet["parameter_ledger"]["unselected_overall_physical_action_scales"] == 1, "one open scale")
    checks += 1

    boundary = packet["physical_boundary"]
    require(boundary["physically_selected"] is False, "not physically selected")
    checks += 1
    require(boundary["eta9_or_HYM_endpoint_used"] is False, "eta9 independent")
    checks += 1
    require(boundary["physical_causal_base_supplied"] is False, "causal base open")
    checks += 1
    require(boundary["physical_SYN_supplied"] is False, "SYN open")
    checks += 1
    require(boundary["physical_BV4_supplied"] is False, "BV4 open")
    checks += 1
    require(boundary["physical_action_scale_selected"] is False, "scale open")
    checks += 1
    require(packet["physical_packets_accepted"] == 0 and packet["physical_rows_accepted"] == 0, "physical acceptance")
    checks += 1
    require(all(packet["checks"].values()), "builder checks")
    checks += 1
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary")
    checks += 1

    print(f"independent Weyl-Gram closure-repair verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()

