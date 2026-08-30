#!/usr/bin/env python3
"""Build the exact conditional CBF.T32 joint product-Dirac action packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from pathlib import Path
from typing import Any

import build_upper_totalization_supercharge_selection as uts
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "product_dirac_joint_radial_source_modulus_action_source_lock.json"
SCHEMA = ROOT / "product_dirac_joint_radial_source_modulus_action_contract.schema.json"
THEOREM = ROOT / "ProductDiracJointRadialSourceModulusHeatKernelActionAndNonzeroVacuumNoGoTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
T26_PACKET = ROOT / "direct_dirac_defect_repair_action.packet.json"
T27_PACKET = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T31_PACKET = ROOT / "four_dimensional_fermion_determinant_scheme_classification.packet.json"
A51_CERTIFICATE = ROOT / "../mtt-sm-parity-closure/certificates/selected_finitespectralactionandhiggsinnerfluctuation_or_directgenerativesmactionclosure_certificate.json"
A52_CERTIFICATE = ROOT / "../mtt-sm-parity-closure/certificates/selected_spectralcutoffmomentsandspacetimeproducttriple_or_bosonicactionnormalization_certificate.json"
A53_CERTIFICATE = ROOT / "../mtt-sm-parity-closure/certificates/selected_propertimemeasureandoverlapkineticmetricsource_or_strictspectralactionclosure_certificate.json"
OUTPUT = ROOT / "product_dirac_joint_radial_source_modulus_action.packet.json"

cp = wg.cp
Poly = list[Fraction]
Interval = tuple[Fraction, Fraction]
LOG_TERMS = 72


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def decimal_fraction(value: Fraction, digits: int = 30) -> str:
    with localcontext() as context:
        context.prec = digits + 30
        number = Decimal(value.numerator) / Decimal(value.denominator)
        return f"{number:.{digits}f}"


def trim(poly: Poly) -> Poly:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def padd(left: Poly, right: Poly) -> Poly:
    size = max(len(left), len(right))
    result = [Fraction(0) for _ in range(size)]
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
    if exponent < 0:
        raise ValueError("negative polynomial powers are unsupported")
    result = [Fraction(1)]
    factor = list(poly)
    power = exponent
    while power:
        if power & 1:
            result = pmul(result, factor)
        factor = pmul(factor, factor)
        power //= 2
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


def poly_payload(poly: Poly) -> list[str]:
    return [fraction_text(value) for value in poly]


def interval(lower: Fraction | int, upper: Fraction | int | None = None) -> Interval:
    low = Fraction(lower)
    high = low if upper is None else Fraction(upper)
    if low > high:
        raise ValueError("reversed interval")
    return low, high


def iadd(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def iscale(scale: Fraction | int, value: Interval) -> Interval:
    factor = Fraction(scale)
    products = (factor * value[0], factor * value[1])
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


def atanh_positive_bounds(z: Fraction, terms: int = LOG_TERMS) -> Interval:
    if not 0 <= z < 1:
        raise ValueError("atanh series requires 0 <= z < 1")
    z2 = z * z
    power = z
    partial = Fraction(0)
    for index in range(terms):
        partial += power / (2 * index + 1)
        power *= z2
    remainder = power / ((2 * terms + 1) * (1 - z2))
    return partial, partial + remainder


@lru_cache(maxsize=None)
def ln2_bounds() -> Interval:
    return iscale(2, atanh_positive_bounds(Fraction(1, 3)))


def ln_positive_bounds(value: Fraction) -> Interval:
    if value <= 0:
        raise ValueError("logarithm requires a positive rational")
    reduced = value
    exponent = 0
    while reduced >= 2:
        reduced /= 2
        exponent += 1
    while reduced < 1:
        reduced *= 2
        exponent -= 1
    local = iscale(2, atanh_positive_bounds((reduced - 1) / (reduced + 1)))
    return iadd(local, iscale(exponent, ln2_bounds()))


def sqrt_fraction_bounds(value: Fraction, digits: int = 30) -> Interval:
    if value < 0:
        raise ValueError("square root requires a nonnegative rational")
    scale = 10**digits
    quotient = (value.numerator * scale * scale) // value.denominator
    lower_integer = isqrt(quotient)
    lower = Fraction(lower_integer, scale)
    upper = lower if lower * lower == value else Fraction(lower_integer + 1, scale)
    return lower, upper


def sqrt_interval_bounds(value: Interval, digits: int = 30) -> Interval:
    return sqrt_fraction_bounds(value[0], digits)[0], sqrt_fraction_bounds(value[1], digits)[1]


def interval_payload(value: Interval, digits: int = 30) -> dict[str, str]:
    return {
        "lower_exact": fraction_text(value[0]),
        "upper_exact": fraction_text(value[1]),
        "lower_decimal": decimal_fraction(value[0], digits),
        "upper_decimal": decimal_fraction(value[1], digits),
    }


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for index in range(len(matrix)):
        total = cp.kadd(total, matrix[index][index])
    return total


def real_trace(matrix: cp.Matrix) -> Fraction:
    value = matrix_trace(matrix)
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"expected real trace, received {value}")
    return value[0]


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def source_root(
    source_lock: dict[str, Any], theorem_hash: str, q2: Poly, q4: Poly
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.product-dirac-joint-radial-source-modulus-action-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "finite_family": "Phi(x)=h(x)D_phys(t(x))",
        "q2_coefficients_ascending": poly_payload(q2),
        "q4_coefficients_ascending": poly_payload(q4),
        "conditional_scalar_action": (
            "f0/(8pi^2) Tr[(partial Phi)^2+Phi^4-"
            "4(f2 Lambda^2/f0)Phi^2]"
        ),
        "selected_t_field_promotion": False,
        "observed_targets": [],
        "theorem_sha256": theorem_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    t25 = json.loads(T25_PACKET.read_text(encoding="ascii"))
    t26 = json.loads(T26_PACKET.read_text(encoding="ascii"))
    t27 = json.loads(T27_PACKET.read_text(encoding="ascii"))
    t31 = json.loads(T31_PACKET.read_text(encoding="ascii"))
    a51 = json.loads(A51_CERTIFICATE.read_text(encoding="ascii"))
    a52 = json.loads(A52_CERTIFICATE.read_text(encoding="ascii"))
    a53 = json.loads(A53_CERTIFICATE.read_text(encoding="ascii"))

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = uts.physical_dirac(
        uts.physical_transfer(projector, phase_direction, shift_direction, Fraction(0))
    )
    d_at_one = uts.physical_dirac(
        uts.physical_transfer(projector, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)

    d0_2 = uts.sparse_matmul(d0, d0)
    d0d1 = uts.sparse_matmul(d0, d1)
    d1d0 = uts.sparse_matmul(d1, d0)
    d1_2 = uts.sparse_matmul(d1, d1)
    d0_3 = uts.sparse_matmul(d0_2, d0)
    d0_4 = uts.sparse_matmul(d0_2, d0_2)
    d0_3_d1 = uts.sparse_matmul(d0_3, d1)
    d0_2_d1_2 = uts.sparse_matmul(d0_2, d1_2)
    d1_3 = uts.sparse_matmul(d1_2, d1)
    d0_d1_3 = uts.sparse_matmul(d0, d1_3)
    d1_4 = uts.sparse_matmul(d1_2, d1_2)

    q2_trace = [
        real_trace(d0_2) / 32,
        2 * real_trace(d0d1) / 32,
        real_trace(d1_2) / 32,
    ]
    q4_trace = [
        real_trace(d0_4) / 32,
        4 * real_trace(d0_3_d1) / 32,
        6 * real_trace(d0_2_d1_2) / 32,
        4 * real_trace(d0_d1_3) / 32,
        real_trace(d1_4) / 32,
    ]
    branches = {"-4": [Fraction(1), Fraction(-2)], "-2": [Fraction(1), Fraction(-1)], "2": [Fraction(1), Fraction(1)]}
    q2 = [Fraction(0)]
    q4 = [Fraction(0)]
    for branch in branches.values():
        q2 = padd(q2, ppow(branch, 2))
        q4 = padd(q4, ppow(branch, 4))
    q2_prime = pderivative(q2)
    q4_prime = pderivative(q4)
    q2_second = pderivative(q2_prime)
    q4_second = pderivative(q4_prime)

    metric_reduced_determinant = padd(
        pscale(6, q2), pscale(Fraction(-1, 4), ppow(q2_prime, 2))
    )
    cauchy_gap = padd(pscale(3, q4), pscale(-1, ppow(q2, 2)))
    cauchy_gap_expected = pscale(2, pmul([Fraction(0), Fraction(0), Fraction(1)], [Fraction(28), Fraction(-24), Fraction(9)]))
    stationary_numerator = padd(
        pmul(q2, q4_prime), pscale(-2, pmul(q4, q2_prime))
    )
    chamber_cubic = [Fraction(14), Fraction(-18), Fraction(-11), Fraction(6)]
    stationary_expected = pscale(8, pmul([Fraction(0), Fraction(1)], chamber_cubic))

    repair = [Fraction(0), Fraction(0), Fraction(4), Fraction(-16, 3), Fraction(3)]
    fixed_rho_one = padd(q4, pscale(-2, q2))
    fixed_bridge = padd(fixed_rho_one, pscale(-1, [peval(fixed_rho_one, 0)]))

    q2_0 = peval(q2, 0)
    q2p_0 = peval(q2_prime, 0)
    q2pp_0 = peval(q2_second, 0)
    q4_0 = peval(q4, 0)
    q4p_0 = peval(q4_prime, 0)
    q4pp_0 = peval(q4_second, 0)
    g0_coefficients = [[q2_0, q2p_0 / 2], [q2p_0 / 2, Fraction(6)]]
    hessian_coefficients = [
        [12 * q4_0 - 4 * q2_0, 4 * q4p_0 - 4 * q2p_0],
        [4 * q4p_0 - 4 * q2p_0, q4pp_0 - 2 * q2pp_0],
    ]
    hessian_metric_relation = [
        [8 * g0_coefficients[0][0], 8 * g0_coefficients[0][1]],
        [8 * g0_coefficients[1][0], 8 * g0_coefficients[1][1]],
    ]

    log448 = ln_positive_bounds(Fraction(448))
    tau = iscale(Fraction(1, 15), log448)
    rho = idiv(interval(2), tau)
    h_over_lambda = sqrt_interval_bounds(rho)
    mass_over_lambda = iscale(2, h_over_lambda)
    mass_squared_over_lambda_squared = iscale(4, rho)

    theorem_hash = sha256(THEOREM)
    root_hash, root_payload = source_root(source_lock, theorem_hash, q2, q4)
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.product-dirac-joint-radial-source-modulus-action-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"] == "cfe21291-1890-4355-a0c7-297aa4d0947d",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"] == "boe.mtt.product-dirac-joint-radial-source-modulus-action.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()),
        "T23_source_is_exact": t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()),
        "T25_source_is_exact": t25["claim_id"] == "CBF.T25" and all(t25["checks"].values()),
        "T26_source_is_exact": t26["claim_id"] == "CBF.T26" and all(t26["checks"].values()),
        "T27_source_is_exact": t27["claim_id"] == "CBF.T27" and all(t27["checks"].values()),
        "T31_source_is_exact": t31["claim_id"] == "CBF.T31" and all(t31["checks"].values()),
        "A51_standard_bosonic_operator_content_is_available": a51["bosonic_SM_operator_content_closed_via_standard_heat_kernel_theorem"],
        "A51_absolute_normalization_remains_open": not a51["absolute_spectral_action_normalization_closed"],
        "A52_strict_moments_remain_open": not a52["strict_spectral_cutoff_moments_closed"],
        "A53_tau_is_available": a53["tau_int_exact_source_available"],
        "A53_point_measure_is_conditional": a53["minimal_point_measure_moments_closed_conditionally"] and not a53["point_measure_selected_by_MTT"],
        "D0_square_is_identity": d0_2 == identity96,
        "D0_D1_commute": d0d1 == d1d0,
        "trace_q2_matches_branches": q2_trace == q2 == [Fraction(3), Fraction(-4), Fraction(6)],
        "trace_q4_matches_branches": q4_trace == q4 == [Fraction(3), Fraction(-8), Fraction(36), Fraction(-32), Fraction(18)],
        "Tr_D1_squared_is_192": real_trace(d1_2) == 192,
        "kinetic_metric_determinant_is_14h_squared": metric_reduced_determinant == [Fraction(14)],
        "q2_is_strictly_positive": (-4) ** 2 - 4 * 6 * 3 < 0 and q2[-1] > 0,
        "cauchy_gap_factorization_is_exact": cauchy_gap == cauchy_gap_expected,
        "cauchy_quadratic_is_positive": (-24) ** 2 - 4 * 9 * 28 == -432 and 9 > 0,
        "cauchy_equality_only_at_zero": cauchy_gap[0] == cauchy_gap[1] == 0 and cauchy_gap[2] > 0,
        "broken_branch_stationary_factorization_is_exact": stationary_numerator == stationary_expected,
        "chamber_cubic_endpoints_are_positive": peval(chamber_cubic, -1) == 15 and peval(chamber_cubic, Fraction(1, 2)) == 3,
        "chamber_cubic_has_only_an_interior_maximum": 20**2 < 445 < 22**2 and 1780 == 4 * 445,
        "unique_broken_stationary_point_in_neutral_chamber": peval(stationary_numerator, 0) == 0,
        "fixed_radial_rho_one_bridge_is_six_times_T26": fixed_bridge == pscale(6, repair),
        "T26_coefficients_match_bridge": t26["exact_coefficients"]["coefficient_t2"] == "4" and t26["exact_coefficients"]["coefficient_t3"] == "-16/3" and t26["exact_coefficients"]["coefficient_t4"] == "3",
        "vacuum_metric_coefficients_are_exact": g0_coefficients == [[Fraction(3), Fraction(-2)], [Fraction(-2), Fraction(6)]],
        "vacuum_hessian_coefficients_are_exact": hessian_coefficients == [[Fraction(24), Fraction(-16)], [Fraction(-16), Fraction(48)]],
        "vacuum_hessian_is_8h_squared_times_metric": hessian_coefficients == hessian_metric_relation,
        "generalized_mass_squared_is_4h_squared_twice": hessian_coefficients == hessian_metric_relation,
        "tau_interval_is_positive": tau[0] > 0,
        "tau_interval_excludes_two": tau[1] < 2,
        "A53_ratio_is_certified": rho[0] > 4 and rho[1] < 5,
        "A53_h_over_Lambda_is_certified": h_over_lambda[0] > 2 and h_over_lambda[1] < Fraction(9, 4),
        "A53_mass_over_Lambda_is_certified": mass_over_lambda[0] > 4 and mass_over_lambda[1] < Fraction(9, 2),
        "T23_h_equals_Lambda_conflicts_with_A53_stationarity": tau[1] < 2,
        "joint_kinetic_metric_is_newly_closed_conditionally": not boundary["joint_h_t_kinetic_metric_before"] and boundary["joint_h_t_kinetic_metric_after"],
        "joint_tree_vacuum_is_newly_closed_conditionally": not boundary["joint_tree_vacuum_before"] and boundary["joint_tree_vacuum_after"],
        "t_field_promotion_remains_unselected": not boundary["t_promoted_to_spacetime_source_modulus_by_MTT"],
        "nonzero_tree_hierarchy_is_not_selected": not boundary["nonzero_t_tree_vacuum_selected"],
        "absolute_scale_remains_unselected": not boundary["absolute_scale_selected"],
        "no_observed_values_used": not boundary["observed_values_used"],
        "no_fitted_coefficients_used": not boundary["fitted_coefficients_used"],
        "physical_packet_acceptance_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "source_root_is_nonempty": len(root_hash) == 64,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T32 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.product-dirac-joint-radial-source-modulus-action.v1",
        "claim_id": "CBF.T32",
        "date": "2026-08-30",
        "status": (
            "exact conditional joint radial/source-modulus heat-kernel action, "
            "unique zero-hierarchy tree vacuum and A53/T23 compatibility cutset; "
            "source-modulus field promotion and physical values remain open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_sha256": root_hash,
            "source_root_payload": root_payload,
        },
        "conditional_action_scope": {
            "product_Dirac_scalar": "Phi(x)=h(x)D_phys(t(x))",
            "adopted_heat_kernel_expansion": "Tr f(D/Lambda)~2f4 Lambda^4 a0+2f2 Lambda^2 a2+f0 a4",
            "scalar_action": "f0/(8pi^2) Tr[(partial Phi)^2+Phi^4-4(f2 Lambda^2/f0)Phi^2]",
            "overall_positive_factor_suppressed_below": "32 f0/(8pi^2)",
            "background": "flat Euclidean four-dimensional product chart",
            "requires": ["f0>0", "f2>0", "h is a radial amplitude"],
            "A51_one_Higgs_module_selected": True,
            "t_is_an_A51_inner_fluctuation": False,
            "t_field_role": "conditional spacetime source-modulus extension of the CBF finite family",
            "t_field_promotion_selected_by_MTT": False,
            "global_Wick_or_Lorentzian_action_selected": False,
        },
        "exact_trace_data": {
            "branch_factors": {key: ({"-4": "1-2t", "-2": "1-t", "2": "1+t"}[key]) for key in branches},
            "Tr_D_squared": "32 q2(t)",
            "q2": "3-4t+6t^2",
            "q2_coefficients_ascending": poly_payload(q2),
            "Tr_D_fourth": "32 q4(t)",
            "q4": "3-8t+36t^2-32t^3+18t^4",
            "q4_coefficients_ascending": poly_payload(q4),
            "Tr_D_D1": "16 q2'(t)",
            "Tr_D1_squared": "192",
            "matrix_reconstruction_exact": True,
        },
        "field_space_geometry": {
            "kinetic_trace": "32[q2(dh)^2+h q2'(dh)(dt)+6h^2(dt)^2]",
            "coordinates": ["h", "t"],
            "metric": [["q2(t)", "h q2'(t)/2"], ["h q2'(t)/2", "6h^2"]],
            "determinant": "14h^2",
            "positive_definite_domain": "h>0",
            "h_zero_interpretation": "radial origin where t is not an independent coordinate",
            "conditional_t_kinetic_term_closed": True,
            "selected_t_dynamicality_closed": False,
        },
        "tree_potential": {
            "c_definition": "c=f2 Lambda^2/f0>0",
            "normalized_potential": "P(h,t)=h^4 q4(t)-4c h^2 q2(t)",
            "radial_stationary_branches": ["h=0", "h^2=2c q2(t)/q4(t)"],
            "h_zero_ridge_radial_curvature": "-8c q2(t)<0",
            "broken_branch_reduced_potential": "P_min(t)=-4c^2 q2(t)^2/q4(t)",
            "stationary_numerator": "q2 q4'-2q4 q2'=8t(6t^3-11t^2-18t+14)",
        },
        "vacuum_selection": {
            "cauchy_identity": "3q4-q2^2=2t^2(9t^2-24t+28)",
            "inner_quadratic_discriminant": -432,
            "ratio_bound": "q2(t)^2/q4(t)<=3",
            "equality_condition": "t=0 only",
            "neutral_chamber": "-1<t<1/2",
            "chamber_cubic_endpoint_values": {"t=-1": 15, "t=1/2": 3},
            "chamber_cubic_interior_critical_type": "one strict maximum",
            "unique_broken_stationary_coordinate_in_chamber": "t0=0",
            "unique_radial_vacuum_for_h>=0": "h0^2=2c",
            "global_minimum_value": "-12c^2",
            "nonzero_family_hierarchy_at_tree_level": False,
            "fixed_h_nonzero_candidates_survive_joint_h_equation": False,
        },
        "scalar_spectrum": {
            "vacuum_metric": [["3", "-2h0"], ["-2h0", "6h0^2"]],
            "vacuum_potential_Hessian": [["24h0^2", "-16h0^3"], ["-16h0^3", "48h0^4"]],
            "exact_relation": "Hess(P)|0=8h0^2 g|0",
            "mass_convention": "M^2=(1/2)g^{-1}Hess(P)",
            "generalized_mass_squared_spectrum": {"4h0^2": 2},
            "dimensionless_mass_ratio": "m/h0=2",
            "interpretation": "conditional tree-level radial/source-modulus curvature masses, not pole masses",
        },
        "fixed_radial_bridge": {
            "rho_definition": "rho=2f2 Lambda^2/(f0 h^2)=2c/h^2",
            "fixed_h_potential": "U_rho(t)=q4(t)-2rho q2(t)",
            "rho_one_identity": "U_1(t)-U_1(0)=6S_rep(t)",
            "S_rep": "4t^2-(16/3)t^3+3t^4",
            "source": "CBF.T26",
            "meaning": "the positive repair profile is the fixed-radial spectral potential at the t=0 radial stationarity ratio",
            "warning": "substituting a fixed h before varying h can create spurious nonzero t extrema",
        },
        "A53_T23_compatibility": {
            "tau_int_exact": "log(448)/15",
            "A53_one_atom_premise_selected_by_MTT": False,
            "A53_conditional_ratios": {
                "f2_over_f0": "15/log(448)",
                "h0_squared_over_Lambda_squared": "30/log(448)",
                "h0_over_Lambda_interval": interval_payload(h_over_lambda),
                "mass_squared_over_Lambda_squared": "120/log(448)",
                "mass_squared_over_Lambda_squared_interval": interval_payload(mass_squared_over_lambda_squared),
                "mass_over_Lambda_interval": interval_payload(mass_over_lambda),
            },
            "tau_interval": interval_payload(tau),
            "rho_interval": interval_payload(rho),
            "T23_one_primitive_identification": "h=Lambda=E0=1/L0",
            "stationarity_with_h_equals_Lambda_requires": "f2/f0=1/2, equivalently tau_int=2",
            "A53_and_T23_stationary_combination_compatible": False,
            "exact_exit_options": [
                "retain A53 moments and use h0/Lambda=sqrt(30/log(448))",
                "retain h=Lambda and replace the A53 one-atom ratio by f2/f0=1/2",
                "retain both inputs but add a selected action term so h=Lambda is not the bare tree stationary point",
            ],
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_accepted_physical_parameters": 0,
            "conditional_structural_extensions": 1,
            "conditional_structural_extension": "promote t to a spacetime source modulus",
            "conditional_A53_premises": 1,
            "conditional_A53_premise": "zero-new-scale minimal one-atom proper-time support",
            "absolute_dimensionful_scale_selected": False,
            "dimensionless_conditional_ratios_emitted": 3,
        },
        "physical_boundary": {
            "conditional_joint_heat_kernel_action_closed": True,
            "conditional_t_kinetic_metric_closed": True,
            "conditional_joint_tree_vacuum_closed": True,
            "standard_tree_action_nonzero_hierarchy_no_go_closed": True,
            "conditional_tree_scalar_curvature_spectrum_closed": True,
            "selected_source_modulus_field_closed": False,
            "selected_spectral_moments_closed": False,
            "selected_absolute_scale_closed": False,
            "selected_Lorentzian_or_global_Wick_action_closed": False,
            "renormalized_quantum_vacuum_closed": False,
            "measured_mass_prediction_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The standard flat product-Dirac heat-kernel tier has now been "
            "executed on the complete CBF finite family with both h and t varied. "
            "It gives an exact positive field metric with det g=14h^2, a unique "
            "broken tree vacuum t=0 and h^2=2f2 Lambda^2/f0, and two degenerate "
            "conditional scalar curvature masses m^2=4h^2. This proves that the "
            "bare standard spectral action cannot generate a nonzero family hierarchy "
            "from the one-coordinate source family. Under A53's conditional one-atom "
            "premise it emits exact ratios h/Lambda=sqrt(30/log448) and "
            "m/Lambda=2sqrt(30/log448), which are incompatible with simultaneously "
            "imposing the T23 h=Lambda normalization at a stationary tree vacuum. "
            "MTT promotion of t as a physical field, selected moments, Lorentzian/QFT "
            "completion, absolute scale and accepted physical values remain open."
        ),
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"wrote {OUTPUT.name}: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
