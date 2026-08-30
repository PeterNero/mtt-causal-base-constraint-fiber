#!/usr/bin/env python3
"""Build the rigorous CBF.T31 four-dimensional determinant boundary packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, getcontext, localcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "four_dimensional_fermion_determinant_scheme_classification_source_lock.json"
SCHEMA = ROOT / "four_dimensional_fermion_determinant_scheme_classification_contract.schema.json"
THEOREM = ROOT / "FourDimensionalFermionDeterminantSchemeClassificationAndPhysicalValueBoundaryTheorem_v1.md"
T30_PACKET = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
OUTPUT = ROOT / "four_dimensional_fermion_determinant_scheme_classification.packet.json"

Interval = tuple[Fraction, Fraction]
BRANCHES: tuple[tuple[str, int], ...] = (("-4", -2), ("-2", -1), ("2", 1))
LOG_TERMS = 32


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def decimal_fraction(value: Fraction, digits: int = 24) -> str:
    with localcontext() as context:
        context.prec = digits + 20
        number = Decimal(value.numerator) / Decimal(value.denominator)
        return f"{number:.{digits}f}"


def decimal_text(value: Decimal, digits: int = 36) -> str:
    return f"{value:.{digits}f}"


def interval(lower: Fraction | int, upper: Fraction | int | None = None) -> Interval:
    low = Fraction(lower)
    high = low if upper is None else Fraction(upper)
    if low > high:
        raise ValueError("interval endpoints are reversed")
    return low, high


def iadd(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def ineg(value: Interval) -> Interval:
    return -value[1], -value[0]


def isub(left: Interval, right: Interval) -> Interval:
    return iadd(left, ineg(right))


def imul(left: Interval, right: Interval) -> Interval:
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def iscale(scale: Fraction | int, value: Interval) -> Interval:
    return imul(interval(Fraction(scale)), value)


def ipow(value: Interval, exponent: int) -> Interval:
    if exponent < 0:
        raise ValueError("negative interval powers are unsupported")
    result = interval(1)
    factor = value
    power = exponent
    while power:
        if power & 1:
            result = imul(result, factor)
        factor = imul(factor, factor)
        power //= 2
    return result


def idiv(left: Interval, right: Interval) -> Interval:
    if right[0] <= 0 <= right[1]:
        raise ZeroDivisionError("interval divisor contains zero")
    reciprocal = interval(Fraction(1, right[1]), Fraction(1, right[0]))
    return imul(left, reciprocal)


def interval_payload(value: Interval, digits: int = 24) -> dict[str, Any]:
    def integer_encoding(number: int) -> bytes:
        magnitude = abs(number)
        payload = magnitude.to_bytes(max(1, (magnitude.bit_length() + 7) // 8), "big")
        return (b"-" if number < 0 else b"+") + len(payload).to_bytes(8, "big") + payload

    exact_encoding = b"".join(
        integer_encoding(number)
        for number in (
            value[0].numerator,
            value[0].denominator,
            value[1].numerator,
            value[1].denominator,
        )
    )
    return {
        "lower_decimal": decimal_fraction(value[0], digits),
        "upper_decimal": decimal_fraction(value[1], digits),
        "exact_rational_bounds_sha256": hashlib.sha256(exact_encoding).hexdigest(),
    }


def atanh_positive_bounds(z: Fraction, terms: int = LOG_TERMS) -> Interval:
    if not 0 <= z < 1:
        raise ValueError("positive atanh series requires 0 <= z < 1")
    z2 = z * z
    power = z
    partial = Fraction(0)
    for index in range(terms):
        partial += power / (2 * index + 1)
        power *= z2
    remainder = power / ((2 * terms + 1) * (1 - z2))
    return partial, partial + remainder


@lru_cache(maxsize=None)
def ln2_bounds(terms: int = LOG_TERMS) -> Interval:
    return iscale(2, atanh_positive_bounds(Fraction(1, 3), terms))


@lru_cache(maxsize=None)
def ln_positive_bounds(value: Fraction, terms: int = LOG_TERMS) -> Interval:
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
    z = (reduced - 1) / (reduced + 1)
    local = iscale(2, atanh_positive_bounds(z, terms))
    binary = iscale(exponent, ln2_bounds(terms))
    return iadd(binary, local)


def ln_interval(value: Interval) -> Interval:
    if value[0] <= 0:
        raise ValueError("log interval must be strictly positive")
    return ln_positive_bounds(value[0])[0], ln_positive_bounds(value[1])[1]


def branch_interval(t_value: Interval, slope: int) -> Interval:
    return iadd(interval(1), iscale(slope, t_value))


def g_interval(t_value: Interval) -> Interval:
    result = interval(0)
    for _, slope in BRANCHES:
        branch = branch_interval(t_value, slope)
        logarithm = ln_interval(ipow(branch, 2))
        factor = isub(logarithm, interval(1))
        result = iadd(result, iscale(slope, imul(ipow(branch, 3), factor)))
    return result


def a_interval(t_value: Interval) -> Interval:
    result = interval(0)
    for _, slope in BRANCHES:
        branch = branch_interval(t_value, slope)
        logarithm = ln_interval(ipow(branch, 2))
        result = iadd(result, iscale(slope, imul(ipow(branch, 3), logarithm)))
    return result


def gprime_interval(t_value: Interval) -> Interval:
    result = interval(0)
    for _, slope in BRANCHES:
        branch = branch_interval(t_value, slope)
        logarithm = ln_interval(ipow(branch, 2))
        factor = isub(iscale(3, logarithm), interval(1))
        result = iadd(result, iscale(slope * slope, imul(ipow(branch, 2), factor)))
    return result


def f_interval(branch: Interval) -> Interval:
    logarithm = ln_interval(ipow(branch, 2))
    return imul(ipow(branch, 2), isub(iscale(3, logarithm), interval(1)))


def v_interval(t_value: Interval, ell: Fraction = Fraction(-3, 2)) -> Interval:
    result = interval(0)
    for _, slope in BRANCHES:
        branch = branch_interval(t_value, slope)
        logarithm = ln_interval(ipow(branch, 2))
        result = iadd(result, imul(ipow(branch, 4), iadd(logarithm, interval(ell))))
    return iscale(Fraction(-1, 3), result)


def zero_extended_v_point(t_value: Fraction) -> Interval:
    result = interval(0)
    for _, slope in BRANCHES:
        branch = 1 + slope * t_value
        if branch == 0:
            continue
        logarithm = ln_positive_bounds(branch * branch)
        term = iscale(branch**4, iadd(logarithm, interval(Fraction(-3, 2))))
        result = iadd(result, term)
    return iscale(Fraction(-1, 3), result)


def g_point_with_zero_extension(t_value: Fraction) -> Interval:
    result = interval(0)
    for _, slope in BRANCHES:
        branch = 1 + slope * t_value
        if branch == 0:
            continue
        logarithm = ln_positive_bounds(branch * branch)
        term = iscale(slope * branch**3, isub(logarithm, interval(1)))
        result = iadd(result, term)
    return result


def scan_no_zero(start: Fraction, end: Fraction, cells: int) -> dict[str, Any]:
    width = (end - start) / cells
    ambiguous = 0
    minimum_margin: Fraction | None = None
    negative_cells = 0
    positive_cells = 0
    for index in range(cells):
        cell = interval(start + index * width, start + (index + 1) * width)
        enclosure = g_interval(cell)
        if enclosure[1] < 0:
            margin = -enclosure[1]
            negative_cells += 1
        elif enclosure[0] > 0:
            margin = enclosure[0]
            positive_cells += 1
        else:
            ambiguous += 1
            continue
        minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
    return {
        "interval": [fraction_text(start), fraction_text(end)],
        "cells": cells,
        "negative_cells": negative_cells,
        "positive_cells": positive_cells,
        "ambiguous_cells": ambiguous,
        "minimum_absolute_margin": (
            interval_payload(interval(minimum_margin)) if minimum_margin is not None else None
        ),
    }


def poly_add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    result = [Fraction(0) for _ in range(size)]
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_scale(scale: Fraction | int, value: list[Fraction]) -> list[Fraction]:
    return [Fraction(scale) * coefficient for coefficient in value]


def poly_mul(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return result


def poly_pow(value: list[Fraction], exponent: int) -> list[Fraction]:
    result = [Fraction(1)]
    for _ in range(exponent):
        result = poly_mul(result, value)
    return result


def poly_eval(value: list[Fraction], coordinate: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(value):
        result = result * coordinate + coefficient
    return result


def decimal_g(t_value: Decimal) -> Decimal:
    result = Decimal(0)
    for _, slope in BRANCHES:
        slope_d = Decimal(slope)
        branch = Decimal(1) + slope_d * t_value
        result += slope_d * branch**3 * ((branch * branch).ln() - Decimal(1))
    return result


def decimal_a(t_value: Decimal) -> Decimal:
    result = Decimal(0)
    for _, slope in BRANCHES:
        slope_d = Decimal(slope)
        branch = Decimal(1) + slope_d * t_value
        result += slope_d * branch**3 * (branch * branch).ln()
    return result


def decimal_b(t_value: Decimal) -> Decimal:
    return Decimal(-2) + Decimal(18) * t_value - Decimal(24) * t_value**2 + Decimal(18) * t_value**3


def decimal_gprime(t_value: Decimal) -> Decimal:
    result = Decimal(0)
    for _, slope in BRANCHES:
        slope_d = Decimal(slope)
        branch = Decimal(1) + slope_d * t_value
        result += slope_d**2 * branch**2 * (Decimal(3) * (branch * branch).ln() - Decimal(1))
    return result


def decimal_v(t_value: Decimal, ell: Decimal = Decimal("-1.5")) -> Decimal:
    result = Decimal(0)
    for _, slope in BRANCHES:
        branch = Decimal(1) + Decimal(slope) * t_value
        if branch == 0:
            continue
        result += branch**4 * ((branch * branch).ln() + ell)
    return -result / Decimal(3)


def bisect_decimal_root(lower: Decimal, upper: Decimal, iterations: int = 260) -> Decimal:
    lower_value = decimal_g(lower)
    upper_value = decimal_g(upper)
    if lower_value == 0:
        return lower
    if upper_value == 0:
        return upper
    if lower_value * upper_value >= 0:
        raise ValueError("root interval does not bracket a sign change")
    for _ in range(iterations):
        middle = (lower + upper) / Decimal(2)
        middle_value = decimal_g(middle)
        if middle_value == 0:
            return middle
        if lower_value * middle_value < 0:
            upper = middle
            upper_value = middle_value
        else:
            lower = middle
            lower_value = middle_value
    return (lower + upper) / Decimal(2)


def decimal_enclosure(value: Decimal, places: int = 55) -> Interval:
    scale = Decimal(10) ** places
    lower_integer = int((value * scale).to_integral_value(rounding=ROUND_FLOOR))
    upper_integer = int((value * scale).to_integral_value(rounding=ROUND_CEILING))
    return Fraction(lower_integer, 10**places), Fraction(upper_integer, 10**places)


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def source_root(
    source_lock: dict[str, Any],
    theorem_hash: str,
    q4: list[Fraction],
    b_polynomial: list[Fraction],
    root_boxes: dict[str, list[str]],
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.four-dimensional-fermion-determinant-scheme-classification-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "branch_slopes": {label: slope for label, slope in BRANCHES},
        "chiral_multiplicity_each": 16,
        "normalized_shape": "V_ell=-(1/3)sum r_a^4(log(r_a^2)+ell)",
        "B_coefficients_ascending": [fraction_text(value) for value in b_polynomial],
        "Q4_coefficients_ascending": [fraction_text(value) for value in q4],
        "candidate_convention": {"scheme": "MSbar", "mu_over_h": "1", "ell": "-3/2"},
        "certified_root_boxes": root_boxes,
        "selected_physical_vacuum": None,
        "accepted_physical_rows": 0,
        "observed_targets": [],
        "theorem_sha256": theorem_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    getcontext().prec = 100
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t30 = json.loads(T30_PACKET.read_text(encoding="ascii"))

    q4 = [Fraction(0)]
    b_polynomial = [Fraction(0)]
    for _, slope in BRANCHES:
        branch_polynomial = [Fraction(1), Fraction(slope)]
        q4 = poly_add(q4, poly_pow(branch_polynomial, 4))
        b_polynomial = poly_add(
            b_polynomial, poly_scale(slope, poly_pow(branch_polynomial, 3))
        )
    expected_q4 = [Fraction(3), Fraction(-8), Fraction(36), Fraction(-32), Fraction(18)]
    expected_b = [Fraction(-2), Fraction(18), Fraction(-24), Fraction(18)]

    scan_records = [
        scan_no_zero(Fraction(-1023, 1024), Fraction(-7, 20), 512),
        scan_no_zero(Fraction(-17, 50), Fraction(27, 100), 1024),
        scan_no_zero(Fraction(29, 100), Fraction(511, 1024), 512),
    ]

    maximum_box = interval(Fraction(-344776761, 10**9), Fraction(-344776760, 10**9))
    minimum_box = interval(Fraction(281284282, 10**9), Fraction(281284283, 10**9))
    maximum_wide = interval(Fraction(-7, 20), Fraction(-17, 50))
    minimum_wide = interval(Fraction(27, 100), Fraction(29, 100))
    maximum_left = g_interval(interval(maximum_box[0]))
    maximum_right = g_interval(interval(maximum_box[1]))
    minimum_left = g_interval(interval(minimum_box[0]))
    minimum_right = g_interval(interval(minimum_box[1]))
    maximum_monotonicity = gprime_interval(maximum_wide)
    minimum_monotonicity = gprime_interval(minimum_wide)

    # On the left wall sliver every summand in g is negative. The first two
    # branches exceed sqrt(e), while the last branch lies strictly below one.
    left_wall_ln4 = ln_positive_bounds(Fraction(4))
    left_wall_ln_49_over_16 = ln_positive_bounds(Fraction(49, 16))
    left_wall_sign = left_wall_ln4[0] > 1 and left_wall_ln_49_over_16[0] > 1

    # On the right wall sliver, bound g' from below including the continuous
    # r^2 log(r^2) extension at r=0, and evaluate g at the limiting endpoint.
    tiny_branch = Fraction(1, 512)
    tiny_derivative_condition = 3 * ln_positive_bounds(tiny_branch**2)[1] + 2 < 0
    tiny_f_at_edge = f_interval(interval(tiny_branch))
    tiny_f = tiny_f_at_edge[0], Fraction(0)
    middle_f = f_interval(interval(Fraction(1, 2), Fraction(513, 1024)))
    plus_f = f_interval(interval(Fraction(1535, 1024), Fraction(3, 2)))
    right_wall_gprime = iadd(iadd(iscale(4, tiny_f), middle_f), plus_f)
    g_at_half = g_point_with_zero_extension(Fraction(1, 2))

    b_derivative_discriminant = (-48) ** 2 - 4 * 54 * 18
    b_root_box = interval(Fraction(132, 1000), Fraction(1321, 10000))
    b_at_left = poly_eval(b_polynomial, b_root_box[0])
    b_at_right = poly_eval(b_polynomial, b_root_box[1])
    a_at_b_root = a_interval(b_root_box)

    maximum_root = bisect_decimal_root(Decimal("-0.344776761"), Decimal("-0.344776760"))
    minimum_root = bisect_decimal_root(Decimal("0.281284282"), Decimal("0.281284283"))

    def root_record(root: Decimal, box: Interval, kind: str) -> dict[str, Any]:
        branch_values = {
            label: Decimal(1) + Decimal(slope) * root for label, slope in BRANCHES
        }
        ratios = {
            "r_+2_over_r_-2": branch_values["2"] / branch_values["-2"],
            "r_-2_over_r_-4": branch_values["-2"] / branch_values["-4"],
            "r_+2_over_r_-4": branch_values["2"] / branch_values["-4"],
        }
        return {
            "certified_interval": [fraction_text(box[0]), fraction_text(box[1])],
            "decimal": decimal_text(root, 48),
            "type": kind,
            "V": decimal_text(decimal_v(root), 36),
            "V_second_derivative": decimal_text(-Decimal(4) * decimal_gprime(root) / Decimal(3), 36),
            "branch_factors": {label: decimal_text(value, 36) for label, value in branch_values.items()},
            "branch_ratios": {label: decimal_text(value, 36) for label, value in ratios.items()},
        }

    maximum_record = root_record(maximum_root, maximum_box, "local maximum")
    minimum_record = root_record(minimum_root, minimum_box, "local minimum")

    left_wall_v = zero_extended_v_point(Fraction(-1))
    right_wall_v = zero_extended_v_point(Fraction(1, 2))
    minimum_v_box = v_interval(minimum_box)
    maximum_v_box = v_interval(maximum_box)

    sqrt13 = Decimal(13).sqrt()
    t30_coordinate = (Decimal(1) - sqrt13) / Decimal(6)
    ell_star = -Decimal("0.5") - decimal_a(t30_coordinate) / decimal_b(t30_coordinate)
    mu_over_h = (-(ell_star + Decimal("1.5")) / Decimal(2)).exp()
    t30_enclosure = decimal_enclosure(t30_coordinate)
    ell_star_interval = isub(
        interval(Fraction(-1, 2)), idiv(a_interval(t30_enclosure), interval(
            min(poly_eval(b_polynomial, t30_enclosure[0]), poly_eval(b_polynomial, t30_enclosure[1])),
            max(poly_eval(b_polynomial, t30_enclosure[0]), poly_eval(b_polynomial, t30_enclosure[1])),
        ))
    )

    root_boxes = {
        "local_maximum": [fraction_text(maximum_box[0]), fraction_text(maximum_box[1])],
        "local_minimum": [fraction_text(minimum_box[0]), fraction_text(minimum_box[1])],
    }
    theorem_hash = sha256(THEOREM)
    root_hash, root_payload = source_root(
        source_lock, theorem_hash, q4, b_polynomial, root_boxes
    )
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.four-dimensional-fermion-determinant-scheme-classification-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"] == "ec8fc7e0-33c8-4cf1-9ae0-6b941d4da986",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"] == "boe.mtt.four-dimensional-fermion-determinant-scheme-classification.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T30_packet_is_exact": t30["claim_id"] == "CBF.T30" and all(t30["checks"].values()),
        "branch_multiplicity_is_inherited": t30["chiral_finite_operator"]["response_branch_multiplicities"] == {"-4": 16, "-2": 16, "2": 16},
        "Q4_polynomial_is_derived_exactly": q4 == expected_q4,
        "B_polynomial_is_derived_exactly": b_polynomial == expected_b,
        "B_derivative_has_negative_discriminant": b_derivative_discriminant == -1584,
        "B_derivative_leading_coefficient_is_positive": 54 > 0,
        "B_has_one_real_root_in_certified_box": b_at_left < 0 < b_at_right,
        "A_is_nonzero_at_B_root_box": a_at_b_root[0] > 0,
        "all_outer_scan_cells_exclude_zero": all(record["ambiguous_cells"] == 0 for record in scan_records),
        "outer_scan_cell_count_is_2048": sum(record["cells"] for record in scan_records) == 2048,
        "maximum_box_has_negative_left_sign": maximum_left[1] < 0,
        "maximum_box_has_positive_right_sign": maximum_right[0] > 0,
        "maximum_wide_box_is_strictly_increasing": maximum_monotonicity[0] > 0,
        "minimum_box_has_positive_left_sign": minimum_left[0] > 0,
        "minimum_box_has_negative_right_sign": minimum_right[1] < 0,
        "minimum_wide_box_is_strictly_decreasing": minimum_monotonicity[1] < 0,
        "left_wall_summands_are_strictly_negative": left_wall_sign,
        "right_wall_tiny_branch_monotonic_bound": tiny_derivative_condition,
        "right_wall_gprime_is_positive": right_wall_gprime[0] > 0,
        "right_wall_limit_g_is_negative": g_at_half[1] < 0,
        "exactly_two_stationary_roots_certified": (
            all(record["ambiguous_cells"] == 0 for record in scan_records)
            and maximum_left[1] < 0 < maximum_right[0]
            and maximum_monotonicity[0] > 0
            and minimum_left[0] > 0 > minimum_right[1]
            and minimum_monotonicity[1] < 0
            and left_wall_sign
            and right_wall_gprime[0] > 0
            and g_at_half[1] < 0
        ),
        "maximum_decimal_is_inside_certified_box": Decimal(maximum_box[0].numerator) / Decimal(maximum_box[0].denominator) < maximum_root < Decimal(maximum_box[1].numerator) / Decimal(maximum_box[1].denominator),
        "minimum_decimal_is_inside_certified_box": Decimal(minimum_box[0].numerator) / Decimal(minimum_box[0].denominator) < minimum_root < Decimal(minimum_box[1].numerator) / Decimal(minimum_box[1].denominator),
        "maximum_curvature_is_negative": decimal_gprime(maximum_root) > 0,
        "minimum_curvature_is_positive": decimal_gprime(minimum_root) < 0,
        "four_dimensional_wall_is_finite": left_wall_v[0] > Fraction(-10**6) and right_wall_v[1] < Fraction(10**6),
        "left_wall_is_below_local_minimum": left_wall_v[1] < minimum_v_box[0],
        "left_wall_is_below_right_wall": left_wall_v[1] < right_wall_v[0],
        "candidate_has_no_global_open_chamber_minimum": left_wall_v[1] < minimum_v_box[0] and left_wall_v[1] < right_wall_v[0],
        "T30_coordinate_is_in_neutral_chamber": Decimal(-1) < t30_coordinate < Decimal("0.5"),
        "T30_coordinate_ell_is_enclosed": Decimal(ell_star_interval[0].numerator) / Decimal(ell_star_interval[0].denominator) <= ell_star <= Decimal(ell_star_interval[1].numerator) / Decimal(ell_star_interval[1].denominator),
        "T30_diagnostic_scale_is_positive": mu_over_h > 0,
        "T30_diagnostic_stationarity_residual_is_small": abs(decimal_a(t30_coordinate) + (ell_star + Decimal("0.5")) * decimal_b(t30_coordinate)) < Decimal("1e-80"),
        "conditional_shape_is_newly_closed": not boundary["flat_four_dimensional_one_loop_shape_before"] and boundary["flat_four_dimensional_one_loop_shape_after"],
        "scale_orbit_is_newly_classified": not boundary["renormalization_scale_orbit_classified_before"] and boundary["renormalization_scale_orbit_classified_after"],
        "counterterm_orbit_is_newly_classified": not boundary["finite_local_counterterm_nonuniqueness_classified_before"] and boundary["finite_local_counterterm_nonuniqueness_classified_after"],
        "candidate_is_newly_executed": not boundary["MSbar_same_scale_candidate_executed_before"] and boundary["MSbar_same_scale_candidate_executed_after"],
        "global_Wick_remains_open": not boundary["selected_Cauchy_normal_or_global_Wick_rotation"],
        "external_measure_remains_open": not boundary["selected_external_spectral_measure"],
        "scalar_counterterm_rule_remains_open": not boundary["selected_scalar_counterterm_rule"],
        "source_dynamicality_remains_open": not boundary["source_coordinate_proved_dynamical"],
        "bosonic_completion_remains_open": not boundary["selected_bosonic_completion"],
        "absolute_scale_remains_open": not boundary["selected_absolute_scale"],
        "candidate_is_not_promoted_to_vacuum": not boundary["candidate_called_final_physical_vacuum"],
        "candidate_is_not_promoted_to_mass": not boundary["candidate_called_SM_mass_prediction"],
        "no_observed_values_used": not boundary["observed_values_used"],
        "no_fitted_coefficients_used": not boundary["fitted_coefficients_used"],
        "physical_packet_acceptance_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "source_root_is_nonempty": len(root_hash) == 64,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T31 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.four-dimensional-fermion-determinant-scheme-classification.v1",
        "claim_id": "CBF.T31",
        "date": "2026-08-30",
        "status": "conditional flat four-dimensional one-loop shape and complete scheme-orbit classification; conventional MSbar same-scale candidate certified but no selected physical vacuum or mass",
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_sha256": root_hash,
            "source_root_payload": root_payload,
            "external_context": source_lock["external_context"],
        },
        "four_dimensional_shape": {
            "branch_factors": {"-4": "1-2t", "-2": "1-t", "2": "1+t"},
            "chiral_multiplicity_each": 16,
            "assumptions": ["flat Euclidean four-dimensional spectral chart", "constant common scale h", "dimensional regularization", "fermion-only one-loop truncation"],
            "normalized_formula": "V_ell(t)=-(1/3)sum_a r_a(t)^4[log(r_a(t)^2)+ell]",
            "ell_definition": "ell=log(h^2/mu^2)-c_scheme",
            "derivative": "V_ell'=-(4/3)[A+(ell+1/2)B]",
            "A_definition": "A=sum_a r_a^3 r_a' log(r_a^2)",
            "B_definition": "B=sum_a r_a^3 r_a'",
            "B_coefficients_ascending": [fraction_text(value) for value in b_polynomial],
            "Q4_coefficients_ascending": [fraction_text(value) for value in q4],
            "zero_branch_limit": "r^4 log(r^2)->0",
            "conditional_pushforward_closed": True,
            "selected_global_Lorentzian_determinant": False,
        },
        "renormalization_orbit": {
            "stationarity_scale_solution": "ell(t0)=-1/2-A(t0)/B(t0) for B(t0)!=0",
            "B_derivative": "18-48t+54t^2",
            "B_derivative_discriminant": b_derivative_discriminant,
            "B_unique_root_interval": [fraction_text(b_root_box[0]), fraction_text(b_root_box[1])],
            "A_on_B_root_interval": interval_payload(a_at_b_root),
            "scale_change": "Delta V=-(Delta ell/3)Q4(t)",
            "Q4": "3-8t+36t^2-32t^3+18t^4",
            "general_finite_local_source_potential": "c0+c1 t+c2 t^2+c3 t^3+c4 t^4",
            "c0_affects_stationarity": False,
            "c1_can_set_slope_at_any_regular_point": True,
            "c2_can_set_curvature_after_slope_fix": True,
            "scheme_independent_stationary_coordinate": False,
            "selected_scalar_counterterm_rule": False,
        },
        "MSbar_same_scale_candidate": {
            "scheme": "MSbar",
            "c_scheme": "3/2",
            "mu_over_h": "1",
            "ell": "-3/2",
            "stationary_equation": "g(t)=sum_a r_a^3 r_a'[log(r_a^2)-1]=0",
            "proof_method": "exact rational interval logarithms from the atanh series with geometric remainder",
            "log_series_terms": LOG_TERMS,
            "outer_scans": scan_records,
            "root_certificates": {
                "local_maximum": {
                    "box": root_boxes["local_maximum"],
                    "left_g": interval_payload(maximum_left),
                    "right_g": interval_payload(maximum_right),
                    "gprime_on_wide_box": interval_payload(maximum_monotonicity),
                },
                "local_minimum": {
                    "box": root_boxes["local_minimum"],
                    "left_g": interval_payload(minimum_left),
                    "right_g": interval_payload(minimum_right),
                    "gprime_on_wide_box": interval_payload(minimum_monotonicity),
                },
                "left_wall_sign": "g<0 term by term on (-1,-1023/1024]",
                "right_wall_gprime": interval_payload(right_wall_gprime),
                "right_wall_g_limit": interval_payload(g_at_half),
                "exact_root_count_in_neutral_chamber": 2,
            },
            "stationary_points": {
                "local_maximum": maximum_record,
                "local_minimum": minimum_record,
            },
            "wall_and_stationary_values": {
                "V_left_wall_limit": decimal_text(decimal_v(Decimal(-1)), 36),
                "V_local_maximum": maximum_record["V"],
                "V_local_minimum": minimum_record["V"],
                "V_right_wall_limit": decimal_text(decimal_v(Decimal("0.5")), 36),
                "left_wall_exact_interval": interval_payload(left_wall_v),
                "local_maximum_exact_interval": interval_payload(maximum_v_box),
                "local_minimum_exact_interval": interval_payload(minimum_v_box),
                "right_wall_exact_interval": interval_payload(right_wall_v),
            },
            "global_minimum_in_open_neutral_chamber": False,
            "infimum_location": "t approaches -1 from above; singular wall not attained",
            "local_minimum_is_metastable": True,
            "conventional_candidate_only": True,
            "MTT_selected_physical_vacuum": False,
            "observed_values_used": False,
            "fitted_coefficients_used": False,
        },
        "T30_coordinate_scheme_diagnostic": {
            "coordinate": "(1-sqrt(13))/6",
            "coordinate_decimal": decimal_text(t30_coordinate, 48),
            "stationary_ell_expression": "-1/2-A(t_*)/B(t_*)",
            "stationary_ell_decimal": decimal_text(ell_star, 48),
            "stationary_ell_rational_enclosure": interval_payload(ell_star_interval, 36),
            "MSbar_mu_over_h_expression": "exp[-(ell_*+3/2)/2]",
            "MSbar_mu_over_h_decimal": decimal_text(mu_over_h, 48),
            "independently_selected": False,
            "role": "diagnostic scale required to preserve the finite T30 coordinate, not a derivation",
        },
        "dynamicality_and_global_boundary": {
            "T25_role_of_t": "coordinate in a finite Dirac-Yukawa source family",
            "four_dimensional_kinetic_term_for_t_selected": False,
            "canonical_normalization_for_t_selected": False,
            "equation_of_motion_for_t_selected": False,
            "selected_Cauchy_normal_or_global_Wick_rotation": False,
            "selected_external_spectral_measure": False,
            "full_domain_chiral_measure": False,
            "selected_bosonic_gauge_Higgs_gravity_completion": False,
            "extremizing_profile_is_physical_equation_of_motion": False,
        },
        "authority_reconciliation": {
            "CBF_T30": "finite chiral determinant and neutral chamber remain exact; its zero-mode coordinate is not promoted to the 4D vacuum",
            "A18": "full Lorentzian and constructive four-dimensional QFT remains open",
            "A73": "same-action determinant identity is respected without importing physical routing or counterterm selection",
            "A84": "proper-time gauge tier supplies no proven intertwiner to this scalar source coordinate",
            "A85": "profile-tier scheme agreement supplies neither scalar subtraction, Wick class nor mu/h",
            "QM_orbitwise_measure": "7/7 finite orbitwise Berezin measure does not close its own 0/4 full-domain contract",
            "B_ACTION_01": "advanced by an exact conditional shape and obstruction classification, but remains open",
            "B_QFT_02": "global Wick, external measure and finite renormalization selection remain open",
            "B_SM_02": "no physical mass or held-out Standard Model row is accepted",
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "candidate_convention_choices": ["flat Euclidean chart", "MSbar c=3/2", "mu/h=1", "fermion-only one-loop truncation"],
            "candidate_convention_choice_count": 4,
            "candidate_choices_selected_by_MTT": 0,
            "unresolved_scale_orbit_dimension": 1,
            "unresolved_nonconstant_local_counterterm_coefficients": 4,
            "inherited_optional_common_scale_h": 1,
            "accepted_new_physical_parameters": 0,
        },
        "physical_boundary": {
            "conditional_flat_4D_one_loop_shape_closed": True,
            "renormalization_scale_orbit_classified": True,
            "finite_local_counterterm_nonuniqueness_classified": True,
            "MSbar_same_scale_candidate_certified": True,
            "candidate_global_neutral_chamber_vacuum_exists": False,
            "selected_four_dimensional_determinant_closed": False,
            "source_coordinate_dynamicality_closed": False,
            "renormalized_physical_vacuum_closed": False,
            "absolute_SI_scale_closed": False,
            "sector_generation_mass_map_closed": False,
            "held_out_physical_observable_emitted": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": "The T30 finite branch spectrum now has an exact conditional flat four-dimensional fermion one-loop pushforward. Its complete subtraction-scale and quartic local-counterterm orbit is classified, proving that no stationary source coordinate is selected by the current data. Under the explicit conventional MSbar mu=h choice, exactly two stationary points are interval-certified; the positive-curvature point is only metastable and the chamber infimum lies at a singular wall. The calculation therefore narrows B.ACTION.01 to a dynamical source-field action plus same-source Wick, external measure, bosonic completion and renormalization rule, without accepting a physical q79 row.",
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    if set(packet) != set(schema["properties"]):
        raise AssertionError("packet top-level keys do not match contract schema")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "Four-dimensional fermion determinant scheme-classification packet built: "
        f"{len(checks)}/{len(checks)} checks; two conventional stationary roots "
        "certified; selected physical vacuum remains open"
    )


if __name__ == "__main__":
    main()
