#!/usr/bin/env python3
"""Independent verifier for the CBF.T19 equivariant Feshbach packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import verify_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "equivariant_feshbach_response.packet.json"
SOURCE_LOCK = ROOT / "equivariant_feshbach_response_source_lock.json"
SCHEMA = ROOT / "equivariant_feshbach_response_contract.schema.json"
THEOREM = ROOT / "EquivariantFeshbachOneDimensionalResponseTheorem_v1.md"
FSB_MANIFEST = ROOT.parent / "mtt-q79-total-superconnection-branching" / "state" / "source_manifest.v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.matrix_add(left, cp.matrix_scale(q(-1), right))


def commutator(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return sub(cp.matrix_mul(left, right), cp.matrix_mul(right, left))


def is_zero(matrix: cp.Matrix) -> bool:
    return matrix == cp.zero(len(matrix), len(matrix[0]))


def block_matrix(blocks: list[list[cp.Matrix]]) -> cp.Matrix:
    result: cp.Matrix = []
    for block_row in blocks:
        height = len(block_row[0])
        for local_row in range(height):
            row: list[cp.K] = []
            for block in block_row:
                if len(block) != height:
                    raise ValueError("bad block height")
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


def inverse(matrix: cp.Matrix) -> cp.Matrix:
    size = len(matrix)
    rows = [left[:] + right[:] for left, right in zip(matrix, cp.identity(size))]
    for column in range(size):
        pivot = next(row for row in range(column, size) if rows[row][column] != cp.Z)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        pivot_inverse = cp.inverse(rows[column][column])
        rows[column] = [cp.mul(pivot_inverse, value) for value in rows[column]]
        for row in range(size):
            if row == column:
                continue
            factor = rows[row][column]
            rows[row] = [
                cp.add(value, cp.neg(cp.mul(factor, pivot_value)))
                for value, pivot_value in zip(rows[row], rows[column])
            ]
    return [row[size:] for row in rows]


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


def centralizer_constraints(generators: list[cp.Matrix]) -> cp.Matrix:
    size = len(generators[0])
    equations: cp.Matrix = []
    for generator in generators:
        for output_row in range(size):
            for output_column in range(size):
                equation: list[cp.K] = []
                for source_row in range(size):
                    for source_column in range(size):
                        left = generator[source_column][output_column] if output_row == source_row else cp.Z
                        right = generator[output_row][source_row] if source_column == output_column else cp.Z
                        equation.append(cp.add(left, cp.neg(right)))
                equations.append(equation)
    return equations


def hermitian_basis() -> list[cp.Matrix]:
    basis: list[cp.Matrix] = []
    i_unit: cp.K = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    for index in range(3):
        value = cp.zero(3, 3)
        value[index][index] = cp.O
        basis.append(value)
    for row in range(3):
        for column in range(row + 1, 3):
            real = cp.zero(3, 3)
            real[row][column] = real[column][row] = cp.O
            basis.append(real)
            imaginary = cp.zero(3, 3)
            imaginary[row][column] = i_unit
            imaginary[column][row] = cp.neg(i_unit)
            basis.append(imaginary)
    return basis


def hardcoded_data() -> tuple[cp.Matrix, cp.Matrix, cp.Matrix]:
    sqrt3_third: cp.K = (Fraction(0), Fraction(1, 3), Fraction(0), Fraction(0))
    minus_sqrt3_six_plus_i_half: cp.K = (
        Fraction(0), Fraction(-1, 6), Fraction(1, 2), Fraction(0)
    )
    minus_sqrt3_six_minus_i_half: cp.K = (
        Fraction(0), Fraction(-1, 6), Fraction(-1, 2), Fraction(0)
    )
    fourier = [
        [sqrt3_third, sqrt3_third, sqrt3_third],
        [sqrt3_third, minus_sqrt3_six_plus_i_half, minus_sqrt3_six_minus_i_half],
        [sqrt3_third, minus_sqrt3_six_minus_i_half, minus_sqrt3_six_plus_i_half],
    ]
    a = [
        [q(-2), cp.Z, q(-2)],
        [cp.Z, q(-2), q(-2)],
        [q(-2), q(-2), cp.Z],
    ]
    b = [
        [q(-4), cp.Z, cp.Z],
        [cp.Z, cp.Z, (Fraction(-1), Fraction(0), Fraction(0), Fraction(-1))],
        [cp.Z, (Fraction(-1), Fraction(0), Fraction(0), Fraction(1)), cp.Z],
    ]
    return fourier, a, b


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    checks = 0

    require(packet["schema"] == "boe.mtt.equivariant-feshbach-response.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T19", "claim id")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "contract hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1
    require(packet["finite_source_manifest_sha256"] == sha256(FSB_MANIFEST), "manifest hash")
    checks += 1
    require(source_lock["repository_head_before"] == "a62c6326f399ed9a3ee7b5a427ce3a08a4a8607a", "starting head")
    checks += 1
    require(source_lock["handoff_id"] == "54421bb0-aa9e-4c9f-a1a4-a89e7d2dea0d", "handoff")
    checks += 1
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"missing {source['path']}")
        require(sha256(path) == source["sha256"], f"hash {source['path']}")
        checks += 1

    properties = schema["properties"]
    require(properties["module_ladder"]["properties"]["gauge_sector_dimension"]["const"] == 36, "schema dimension 36")
    checks += 1
    require(properties["feshbach_covariance"]["properties"]["equivariance_alone_forces_response_line"]["const"] is False, "schema no-go")
    checks += 1
    require(properties["relative_intertwiner"]["properties"]["physically_supplied"]["const"] is False, "schema boundary")
    checks += 1

    fourier, a, b = hardcoded_data()
    identity3 = cp.identity(3)
    identity6 = cp.identity(6)
    zero3 = cp.zero(3, 3)
    zero6 = cp.zero(6, 6)
    require(cp.matrix_mul(cp.adjoint(fourier), fourier) == identity3, "Fourier unitary")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(a, fourier)) == b, "Fourier response")
    checks += 1

    parity = block_diag([identity3, cp.matrix_scale(q(-1), identity3)])
    exchange = block_matrix([[zero3, cp.adjoint(fourier)], [fourier, zero3]])
    h6 = block_diag([b, a])
    a6 = block_diag([a, a])
    b6 = block_diag([b, b])
    require(cp.matrix_mul(parity, parity) == identity6, "parity involution")
    checks += 1
    require(cp.matrix_mul(exchange, exchange) == identity6, "exchange involution")
    checks += 1
    require(is_zero(commutator(h6, parity)) and is_zero(commutator(h6, exchange)), "response equivariance")
    checks += 1
    require(36 - cp.rank(centralizer_constraints([parity, exchange])) == 9, "routed commutant dimension")
    checks += 1
    require(36 - cp.rank(centralizer_constraints([a6, b6, parity, exchange])) == 1, "comparison commutant dimension")
    checks += 1

    basis = hermitian_basis()
    z = cp.zero(3, 3)
    gauge: list[cp.Matrix] = []
    paired: list[cp.Matrix] = []
    universal: list[cp.Matrix] = []
    for sector in range(4):
        for value in basis:
            blocks = [z, z, z, z]
            blocks[sector] = value
            gauge.append(block_diag(blocks))
    for value in basis:
        phase = cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(value, fourier))
        paired.append(block_diag([phase, z, value, z]))
        paired.append(block_diag([z, phase, z, value]))
        universal.append(block_diag([phase, phase, value, value]))
    h12 = block_diag([b, b, a, a])
    require(span_rank(gauge) == 36, "gauge module")
    checks += 1
    require(span_rank(paired) == 18, "paired module")
    checks += 1
    require(span_rank(universal) == 9, "universal module")
    checks += 1
    require(span_rank([h12]) == 1, "response line")
    checks += 1
    require(packet["module_ladder"]["dimension_chain"] == [36, 18, 9, 1], "packet ladder")
    checks += 1

    h6_inverse = inverse(h6)
    require(cp.matrix_mul(h6_inverse, h6) == identity6, "H6 inverse")
    checks += 1
    norm2 = frobenius(h6, h6)
    require(norm2 == q(48), "H6 norm")
    checks += 1

    scale = Fraction(7, 3)
    target = cp.matrix_scale(q(scale), h6)
    coupling = cp.matrix_scale(q(2), identity6)
    complement = cp.matrix_scale(q(3), identity6)
    complement_inverse = cp.matrix_scale(q(Fraction(1, 3)), identity6)
    self_energy = cp.matrix_mul(coupling, cp.matrix_mul(complement_inverse, cp.adjoint(coupling)))
    retained = cp.matrix_add(target, self_energy)
    upper = block_matrix([[retained, coupling], [cp.adjoint(coupling), complement]])
    effective = sub(retained, self_energy)
    upper_parity = block_diag([parity, parity])
    upper_exchange = block_diag([exchange, exchange])
    inclusion = block_matrix([[identity6], [zero6]])
    require(is_zero(commutator(upper, upper_parity)), "upper parity")
    checks += 1
    require(is_zero(commutator(upper, upper_exchange)), "upper exchange")
    checks += 1
    require(cp.matrix_mul(upper_parity, inclusion) == cp.matrix_mul(inclusion, parity), "inclusion parity")
    checks += 1
    require(cp.matrix_mul(upper_exchange, inclusion) == cp.matrix_mul(inclusion, exchange), "inclusion exchange")
    checks += 1
    require(cp.matrix_mul(complement_inverse, complement) == identity6, "complement inverse")
    checks += 1
    require(effective == target, "Feshbach target")
    checks += 1
    recovered = cp.divide(frobenius(h6, effective), norm2)
    require(recovered == q(scale), "scale")
    checks += 1
    require(is_zero(sub(effective, cp.matrix_scale(recovered, h6))), "residual")
    checks += 1

    relative = cp.matrix_mul(h6_inverse, effective)
    require(relative == cp.matrix_scale(q(scale), identity6), "relative scalar")
    checks += 1
    for generator in [a6, b6, parity, exchange]:
        require(is_zero(commutator(relative, generator)), "relative commutator")
        checks += 1

    alternative_retained = cp.matrix_add(identity6, self_energy)
    alternative_upper = block_matrix([[alternative_retained, coupling], [cp.adjoint(coupling), complement]])
    alternative_effective = sub(alternative_retained, self_energy)
    require(is_zero(commutator(alternative_upper, upper_parity)), "alternative parity")
    checks += 1
    require(is_zero(commutator(alternative_upper, upper_exchange)), "alternative exchange")
    checks += 1
    require(alternative_effective == identity6, "alternative Feshbach")
    checks += 1
    alternative_scale = cp.divide(frobenius(h6, alternative_effective), norm2)
    require(not is_zero(sub(alternative_effective, cp.matrix_scale(alternative_scale, h6))), "alternative residual")
    checks += 1
    alternative_relative = cp.matrix_mul(h6_inverse, alternative_effective)
    require(any(not is_zero(commutator(alternative_relative, generator)) for generator in [a6, b6, parity, exchange]), "alternative relative failure")
    checks += 1

    require(packet["feshbach_covariance"]["negative_control"]["response_residual_zero"] is False, "packet negative control")
    checks += 1
    require(packet["relative_intertwiner"]["comparison_commutant_dimension"] == 1, "packet relative dimension")
    checks += 1
    require(packet["relative_intertwiner"]["physically_supplied"] is False, "packet physical boundary")
    checks += 1
    require(packet["physical_packets_accepted"] == 0 and packet["physical_rows_accepted"] == 0, "acceptance boundary")
    checks += 1
    require(packet["parameter_ledger"]["observed_construction_inputs"] == 0, "no observations")
    checks += 1
    require(packet["parameter_ledger"]["fitted_coefficients"] == 0, "no fits")
    checks += 1
    require(all(packet["checks"].values()), "builder checks")
    checks += 1
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary")
    checks += 1

    print(f"independent equivariant Feshbach response verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
