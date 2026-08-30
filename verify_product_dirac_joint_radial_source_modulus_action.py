#!/usr/bin/env python3
"""Independent reconstruction of the CBF.T32 joint heat-kernel action."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "product_dirac_joint_radial_source_modulus_action.packet.json"
SOURCE_LOCK_PATH = ROOT / "product_dirac_joint_radial_source_modulus_action_source_lock.json"
SCHEMA_PATH = ROOT / "product_dirac_joint_radial_source_modulus_action_contract.schema.json"
THEOREM_PATH = ROOT / "ProductDiracJointRadialSourceModulusHeatKernelActionAndNonzeroVacuumNoGoTheorem_v1.md"
T20_PATH = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T25_PATH = ROOT / "direct_finite_source_continuum.packet.json"
T26_PATH = ROOT / "direct_dirac_defect_repair_action.packet.json"
T27_PATH = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T31_PATH = ROOT / "four_dimensional_fermion_determinant_scheme_classification.packet.json"
LOG_TERMS = 72

Poly = list[Fraction]
Interval = tuple[Fraction, Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


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
    phase_incidence = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    shift_incidence = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(projector, phase_direction, t), phase_incidence),
        cp.kron(family_map(projector, shift_direction, t), shift_incidence),
    )


def physical_dirac(transfer_matrix: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    return block_diag([particle, conjugate(particle)])


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    result = cp.ZERO
    for index in range(len(matrix)):
        result = cp.kadd(result, matrix[index][index])
    return result


def real_trace(matrix: cp.Matrix) -> Fraction:
    value = matrix_trace(matrix)
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"non-real trace: {value}")
    return value[0]


def trim(poly: Poly) -> Poly:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def padd(left: Poly, right: Poly) -> Poly:
    result = [Fraction(0) for _ in range(max(len(left), len(right)))]
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    return trim(result)


def pscale(scale: Fraction | int, poly: Poly) -> Poly:
    return trim([Fraction(scale) * value for value in poly])


def pmul(left: Poly, right: Poly) -> Poly:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return trim(result)


def ppow(poly: Poly, exponent: int) -> Poly:
    result = [Fraction(1)]
    for _ in range(exponent):
        result = pmul(result, poly)
    return result


def pderivative(poly: Poly) -> Poly:
    if len(poly) == 1:
        return [Fraction(0)]
    return trim([Fraction(index) * poly[index] for index in range(1, len(poly))])


def peval(poly: Poly, value: Fraction | int) -> Fraction:
    result = Fraction(0)
    x = Fraction(value)
    for coefficient in reversed(poly):
        result = result * x + coefficient
    return result


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def interval_payload_exact(payload: dict[str, str]) -> Interval:
    return parse_fraction(payload["lower_exact"]), parse_fraction(payload["upper_exact"])


def iadd(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def iscale(scale: Fraction | int, value: Interval) -> Interval:
    products = (Fraction(scale) * value[0], Fraction(scale) * value[1])
    return min(products), max(products)


def idiv(left: Interval, right: Interval) -> Interval:
    if right[0] <= 0 <= right[1]:
        raise ZeroDivisionError("interval divisor contains zero")
    products = (
        left[0] / right[0],
        left[0] / right[1],
        left[1] / right[0],
        left[1] / right[1],
    )
    return min(products), max(products)


def atanh_bounds(z: Fraction) -> Interval:
    z2 = z * z
    power = z
    partial = Fraction(0)
    for index in range(LOG_TERMS):
        partial += power / (2 * index + 1)
        power *= z2
    return partial, partial + power / ((2 * LOG_TERMS + 1) * (1 - z2))


@lru_cache(maxsize=None)
def ln2_bounds() -> Interval:
    return iscale(2, atanh_bounds(Fraction(1, 3)))


def ln_bounds(value: Fraction) -> Interval:
    reduced = value
    exponent = 0
    while reduced >= 2:
        reduced /= 2
        exponent += 1
    while reduced < 1:
        reduced *= 2
        exponent -= 1
    local = iscale(2, atanh_bounds((reduced - 1) / (reduced + 1)))
    return iadd(local, iscale(exponent, ln2_bounds()))


def sqrt_fraction_bounds(value: Fraction, digits: int = 30) -> Interval:
    scale = 10**digits
    quotient = (value.numerator * scale * scale) // value.denominator
    lower_integer = isqrt(quotient)
    lower = Fraction(lower_integer, scale)
    upper = lower if lower * lower == value else Fraction(lower_integer + 1, scale)
    return lower, upper


def sqrt_interval(value: Interval) -> Interval:
    return sqrt_fraction_bounds(value[0])[0], sqrt_fraction_bounds(value[1])[1]


def source_root(
    lock: dict[str, Any], theorem_hash: str, q2: Poly, q4: Poly
) -> tuple[str, dict[str, Any]]:
    def text_fraction(value: Fraction) -> str:
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

    payload = {
        "schema": "boe.mtt.product-dirac-joint-radial-source-modulus-action-root.v1",
        "repository_heads": lock["repositories"],
        "source_hashes": [source["sha256"] for source in lock["local_sources"]],
        "finite_family": "Phi(x)=h(x)D_phys(t(x))",
        "q2_coefficients_ascending": [text_fraction(value) for value in q2],
        "q4_coefficients_ascending": [text_fraction(value) for value in q4],
        "conditional_scalar_action": "f0/(8pi^2) Tr[(partial Phi)^2+Phi^4-4(f2 Lambda^2/f0)Phi^2]",
        "selected_t_field_promotion": False,
        "observed_targets": [],
        "theorem_sha256": theorem_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="ascii"))
    lock = json.loads(SOURCE_LOCK_PATH.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="ascii"))
    t20 = json.loads(T20_PATH.read_text(encoding="ascii"))
    t23 = json.loads(T23_PATH.read_text(encoding="ascii"))
    t25 = json.loads(T25_PATH.read_text(encoding="ascii"))
    t26 = json.loads(T26_PATH.read_text(encoding="ascii"))
    t27 = json.loads(T27_PATH.read_text(encoding="ascii"))
    t31 = json.loads(T31_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.product-dirac-joint-radial-source-modulus-action.v1", "packet schema", passed)
    require(packet["claim_id"] == "CBF.T32", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(lock["handoff_id"] == "cfe21291-1890-4355-a0c7-297aa4d0947d", "handoff pin", passed)
    require(packet["source_provenance"]["kernel_model_sha256"] == lock["kernel_model_sha256"], "kernel model pin", passed)
    for source in lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)

    for lower_packet, claim in ((t20, "CBF.T20"), (t23, "CBF.T23"), (t25, "CBF.T25"), (t26, "CBF.T26"), (t27, "CBF.T27"), (t31, "CBF.T31")):
        require(lower_packet["claim_id"] == claim, f"{claim} identity", passed)
        require(all(lower_packet["checks"].values()), f"{claim} checks", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = decode_matrix(primitive["P"])
    x = decode_matrix(primitive["X"])
    z = decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase = cp.madd(identity3, z)
    shift = cp.madd(identity3, x)
    d0 = physical_dirac(transfer(projector, phase, shift, Fraction(0)))
    d_one = physical_dirac(transfer(projector, phase, shift, Fraction(1)))
    d1 = matrix_sub(d_one, d0)
    d0_2 = sparse_matmul(d0, d0)
    d0d1 = sparse_matmul(d0, d1)
    d1d0 = sparse_matmul(d1, d0)
    d1_2 = sparse_matmul(d1, d1)
    require(d0_2 == cp.identity(96), "D0 is an involution", passed)
    require(d0d1 == d1d0, "D0 and D1 commute", passed)
    require(real_trace(d0_2) == 96, "Tr D0 squared", passed)
    require(real_trace(d0d1) == -64, "Tr D0 D1", passed)
    require(real_trace(d1_2) == 192, "Tr D1 squared", passed)

    q2 = [Fraction(3), Fraction(-4), Fraction(6)]
    q4 = [Fraction(3), Fraction(-8), Fraction(36), Fraction(-32), Fraction(18)]
    q2p = pderivative(q2)
    q4p = pderivative(q4)
    for t in (Fraction(-1), Fraction(-1, 2), Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(2)):
        direct = physical_dirac(transfer(projector, phase, shift, t))
        direct2 = sparse_matmul(direct, direct)
        direct4 = sparse_matmul(direct2, direct2)
        require(real_trace(direct2) == 32 * peval(q2, t), f"q2 sample {t}", passed)
        require(real_trace(direct4) == 32 * peval(q4, t), f"q4 sample {t}", passed)
        require(real_trace(sparse_matmul(direct, d1)) == 16 * peval(q2p, t), f"DD1 sample {t}", passed)

    require(packet["exact_trace_data"]["q2_coefficients_ascending"] == ["3", "-4", "6"], "packet q2", passed)
    require(packet["exact_trace_data"]["q4_coefficients_ascending"] == ["3", "-8", "36", "-32", "18"], "packet q4", passed)

    metric_det = padd(pscale(6, q2), pscale(Fraction(-1, 4), ppow(q2p, 2)))
    require(metric_det == [Fraction(14)], "field metric determinant", passed)
    require(packet["field_space_geometry"]["determinant"] == "14h^2", "packet field determinant", passed)
    require(packet["field_space_geometry"]["positive_definite_domain"] == "h>0", "metric domain", passed)
    require(not packet["field_space_geometry"]["selected_t_dynamicality_closed"], "dynamicality boundary", passed)

    gap = padd(pscale(3, q4), pscale(-1, ppow(q2, 2)))
    expected_gap = [Fraction(0), Fraction(0), Fraction(56), Fraction(-48), Fraction(18)]
    require(gap == expected_gap, "Cauchy gap expansion", passed)
    require((-24) ** 2 - 4 * 9 * 28 == -432, "positive gap quadratic", passed)
    require(packet["vacuum_selection"]["equality_condition"] == "t=0 only", "packet equality condition", passed)
    require(packet["vacuum_selection"]["unique_radial_vacuum_for_h>=0"] == "h0^2=2c", "packet radial vacuum", passed)
    require(not packet["vacuum_selection"]["nonzero_family_hierarchy_at_tree_level"], "tree hierarchy no-go", passed)

    stationary = padd(pmul(q2, q4p), pscale(-2, pmul(q4, q2p)))
    cubic = [Fraction(14), Fraction(-18), Fraction(-11), Fraction(6)]
    require(stationary == pscale(8, pmul([Fraction(0), Fraction(1)], cubic)), "stationary factorization", passed)
    require(peval(cubic, -1) == 15, "cubic left endpoint", passed)
    require(peval(cubic, Fraction(1, 2)) == 3, "cubic right endpoint", passed)
    require(20**2 < 445 < 22**2, "critical-root rational bounds", passed)
    require(Fraction(-11, 18) > -1 and Fraction(-1, 2) < Fraction(1, 2), "interior maximum bounds", passed)

    repair = [Fraction(0), Fraction(0), Fraction(4), Fraction(-16, 3), Fraction(3)]
    u1 = padd(q4, pscale(-2, q2))
    relative_u1 = padd(u1, [-peval(u1, 0)])
    require(relative_u1 == pscale(6, repair), "T26 bridge", passed)
    require(packet["fixed_radial_bridge"]["rho_one_identity"] == "U_1(t)-U_1(0)=6S_rep(t)", "packet T26 bridge", passed)

    for h in (Fraction(1), Fraction(2), Fraction(7, 3)):
        g = [[Fraction(3), -2 * h], [-2 * h, 6 * h * h]]
        hessian = [[24 * h * h, -16 * h**3], [-16 * h**3, 48 * h**4]]
        for row in range(2):
            for column in range(2):
                require(hessian[row][column] == 8 * h * h * g[row][column], f"Hessian metric relation h={h} ({row},{column})", passed)
        determinant = g[0][0] * g[1][1] - g[0][1] * g[1][0]
        inverse = [[g[1][1] / determinant, -g[0][1] / determinant], [-g[1][0] / determinant, g[0][0] / determinant]]
        mass = [[sum(inverse[row][k] * hessian[k][column] for k in range(2)) / 2 for column in range(2)] for row in range(2)]
        require(mass == [[4 * h * h, Fraction(0)], [Fraction(0), 4 * h * h]], f"generalized mass matrix h={h}", passed)
    require(packet["scalar_spectrum"]["generalized_mass_squared_spectrum"] == {"4h0^2": 2}, "packet scalar spectrum", passed)

    tau = iscale(Fraction(1, 15), ln_bounds(Fraction(448)))
    rho = idiv((Fraction(2), Fraction(2)), tau)
    h_ratio = sqrt_interval(rho)
    mass_ratio = iscale(2, h_ratio)
    mass_squared_ratio = iscale(4, rho)
    compatibility = packet["A53_T23_compatibility"]
    require(interval_payload_exact(compatibility["tau_interval"]) == tau, "tau interval", passed)
    require(interval_payload_exact(compatibility["rho_interval"]) == rho, "rho interval", passed)
    require(interval_payload_exact(compatibility["A53_conditional_ratios"]["h0_over_Lambda_interval"]) == h_ratio, "h over Lambda interval", passed)
    require(interval_payload_exact(compatibility["A53_conditional_ratios"]["mass_over_Lambda_interval"]) == mass_ratio, "mass over Lambda interval", passed)
    require(interval_payload_exact(compatibility["A53_conditional_ratios"]["mass_squared_over_Lambda_squared_interval"]) == mass_squared_ratio, "mass squared interval", passed)
    require(tau[1] < 1 < 2, "tau excludes stationarity value two", passed)
    require(not compatibility["A53_one_atom_premise_selected_by_MTT"], "A53 conditional premise", passed)
    require(not compatibility["A53_and_T23_stationary_combination_compatible"], "A53 T23 cutset", passed)

    root_hash, root_payload = source_root(lock, sha256(THEOREM_PATH), q2, q4)
    require(packet["source_provenance"]["source_root_sha256"] == root_hash, "source root digest", passed)
    require(packet["source_provenance"]["source_root_payload"] == root_payload, "source root payload", passed)
    require(packet["parameter_ledger"]["new_observed_construction_inputs"] == 0, "no observed inputs", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fitted coefficients", passed)
    require(packet["parameter_ledger"]["new_accepted_physical_parameters"] == 0, "no accepted parameters", passed)
    require(packet["physical_packets_accepted"] == 0, "physical packet boundary", passed)
    require(packet["physical_rows_accepted"] == 0, "physical row boundary", passed)
    require(not packet["physical_boundary"]["B_ACTION_01_closed"], "B.ACTION.01 boundary", passed)
    require(not packet["physical_boundary"]["B_QFT_02_closed"], "B.QFT.02 boundary", passed)
    require(not packet["physical_boundary"]["B_SM_02_closed"], "B.SM.02 boundary", passed)
    require(all(packet["checks"].values()), "builder check ledger", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder check summary", passed)
    require(packet["check_summary"]["failed"] == [], "builder failed ledger", passed)

    print(f"verified {PACKET_PATH.name}: {len(passed)}/{len(passed)} independent checks passed")


if __name__ == "__main__":
    main()
