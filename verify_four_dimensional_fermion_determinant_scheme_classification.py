#!/usr/bin/env python3
"""Independent exact verification of the CBF.T31 scheme classification."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "four_dimensional_fermion_determinant_scheme_classification.packet.json"
SOURCE_LOCK_PATH = ROOT / "four_dimensional_fermion_determinant_scheme_classification_source_lock.json"
SCHEMA_PATH = ROOT / "four_dimensional_fermion_determinant_scheme_classification_contract.schema.json"
THEOREM_PATH = ROOT / "FourDimensionalFermionDeterminantSchemeClassificationAndPhysicalValueBoundaryTheorem_v1.md"
T30_PATH = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"

Bounds = tuple[Fraction, Fraction]
BRANCHES = (("-4", -2), ("-2", -1), ("2", 1))
TERMS = 36


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def add(left: Bounds, right: Bounds) -> Bounds:
    return left[0] + right[0], left[1] + right[1]


def multiply(left: Bounds, right: Bounds) -> Bounds:
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def scale(number: Fraction | int, value: Bounds) -> Bounds:
    scalar = Fraction(number)
    return multiply((scalar, scalar), value)


def subtract(left: Bounds, right: Bounds) -> Bounds:
    return add(left, (-right[1], -right[0]))


def power(value: Bounds, exponent: int) -> Bounds:
    result = (Fraction(1), Fraction(1))
    for _ in range(exponent):
        result = multiply(result, value)
    return result


def atanh_bounds(z: Fraction) -> Bounds:
    z_squared = z * z
    term = z
    partial = Fraction(0)
    for index in range(TERMS):
        partial += term / (2 * index + 1)
        term *= z_squared
    tail = term / ((2 * TERMS + 1) * (1 - z_squared))
    return partial, partial + tail


@lru_cache(maxsize=None)
def log_two() -> Bounds:
    return scale(2, atanh_bounds(Fraction(1, 3)))


@lru_cache(maxsize=None)
def log_point(value: Fraction) -> Bounds:
    if value <= 0:
        raise ValueError("positive logarithm required")
    mantissa = value
    exponent = 0
    while mantissa >= 2:
        mantissa /= 2
        exponent += 1
    while mantissa < 1:
        mantissa *= 2
        exponent -= 1
    local = scale(2, atanh_bounds((mantissa - 1) / (mantissa + 1)))
    return add(scale(exponent, log_two()), local)


def log_bounds(value: Bounds) -> Bounds:
    if value[0] <= 0:
        raise ValueError("positive log interval required")
    return log_point(value[0])[0], log_point(value[1])[1]


def branch_bounds(t_bounds: Bounds, slope: int) -> Bounds:
    return add((Fraction(1), Fraction(1)), scale(slope, t_bounds))


def g_bounds(t_bounds: Bounds) -> Bounds:
    result = (Fraction(0), Fraction(0))
    for _, slope in BRANCHES:
        branch = branch_bounds(t_bounds, slope)
        log_square = log_bounds(power(branch, 2))
        summand = scale(slope, multiply(power(branch, 3), subtract(log_square, (Fraction(1), Fraction(1)))))
        result = add(result, summand)
    return result


def gprime_bounds(t_bounds: Bounds) -> Bounds:
    result = (Fraction(0), Fraction(0))
    for _, slope in BRANCHES:
        branch = branch_bounds(t_bounds, slope)
        log_square = log_bounds(power(branch, 2))
        factor = subtract(scale(3, log_square), (Fraction(1), Fraction(1)))
        result = add(result, scale(slope * slope, multiply(power(branch, 2), factor)))
    return result


def no_zero_scan(start: Fraction, end: Fraction, cells: int) -> bool:
    width = (end - start) / cells
    for index in range(cells):
        cell = (start + index * width, start + (index + 1) * width)
        enclosure = g_bounds(cell)
        if enclosure[0] <= 0 <= enclosure[1]:
            return False
    return True


def zero_extended_g(t_value: Fraction) -> Bounds:
    result = (Fraction(0), Fraction(0))
    for _, slope in BRANCHES:
        branch = 1 + slope * t_value
        if branch == 0:
            continue
        factor = subtract(log_point(branch * branch), (Fraction(1), Fraction(1)))
        result = add(result, scale(slope * branch**3, factor))
    return result


def zero_extended_v(t_value: Fraction) -> Bounds:
    result = (Fraction(0), Fraction(0))
    for _, slope in BRANCHES:
        branch = 1 + slope * t_value
        if branch == 0:
            continue
        factor = add(log_point(branch * branch), (Fraction(-3, 2), Fraction(-3, 2)))
        result = add(result, scale(branch**4, factor))
    return scale(Fraction(-1, 3), result)


def v_bounds(t_bounds: Bounds) -> Bounds:
    result = (Fraction(0), Fraction(0))
    for _, slope in BRANCHES:
        branch = branch_bounds(t_bounds, slope)
        factor = add(log_bounds(power(branch, 2)), (Fraction(-3, 2), Fraction(-3, 2)))
        result = add(result, multiply(power(branch, 4), factor))
    return scale(Fraction(-1, 3), result)


def decimal_g(value: Decimal) -> Decimal:
    total = Decimal(0)
    for _, slope in BRANCHES:
        slope_d = Decimal(slope)
        branch = Decimal(1) + slope_d * value
        total += slope_d * branch**3 * ((branch * branch).ln() - Decimal(1))
    return total


def decimal_gprime(value: Decimal) -> Decimal:
    total = Decimal(0)
    for _, slope in BRANCHES:
        slope_d = Decimal(slope)
        branch = Decimal(1) + slope_d * value
        total += slope_d**2 * branch**2 * (Decimal(3) * (branch * branch).ln() - Decimal(1))
    return total


def decimal_a(value: Decimal) -> Decimal:
    total = Decimal(0)
    for _, slope in BRANCHES:
        slope_d = Decimal(slope)
        branch = Decimal(1) + slope_d * value
        total += slope_d * branch**3 * (branch * branch).ln()
    return total


def decimal_b(value: Decimal) -> Decimal:
    return Decimal(-2) + Decimal(18) * value - Decimal(24) * value**2 + Decimal(18) * value**3


def decimal_v(value: Decimal) -> Decimal:
    total = Decimal(0)
    for _, slope in BRANCHES:
        branch = Decimal(1) + Decimal(slope) * value
        if branch:
            total += branch**4 * ((branch * branch).ln() - Decimal("1.5"))
    return -total / Decimal(3)


def root(lower: Decimal, upper: Decimal) -> Decimal:
    lower_value = decimal_g(lower)
    upper_value = decimal_g(upper)
    if lower_value * upper_value >= 0:
        raise ValueError("not a bracket")
    for _ in range(280):
        middle = (lower + upper) / 2
        middle_value = decimal_g(middle)
        if lower_value * middle_value < 0:
            upper = middle
            upper_value = middle_value
        else:
            lower = middle
            lower_value = middle_value
    return (lower + upper) / 2


def source_root_payload(source_lock: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "boe.mtt.four-dimensional-fermion-determinant-scheme-classification-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "branch_slopes": {label: slope for label, slope in BRANCHES},
        "chiral_multiplicity_each": 16,
        "normalized_shape": "V_ell=-(1/3)sum r_a^4(log(r_a^2)+ell)",
        "B_coefficients_ascending": ["-2", "18", "-24", "18"],
        "Q4_coefficients_ascending": ["3", "-8", "36", "-32", "18"],
        "candidate_convention": {"scheme": "MSbar", "mu_over_h": "1", "ell": "-3/2"},
        "certified_root_boxes": {
            "local_maximum": ["-344776761/1000000000", "-8619419/25000000"],
            "local_minimum": ["140642141/500000000", "281284283/1000000000"],
        },
        "selected_physical_vacuum": None,
        "accepted_physical_rows": 0,
        "observed_targets": [],
        "theorem_sha256": sha256(THEOREM_PATH),
    }


def main() -> None:
    getcontext().prec = 110
    packet = json.loads(PACKET_PATH.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK_PATH.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="ascii"))
    t30 = json.loads(T30_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.four-dimensional-fermion-determinant-scheme-classification.v1", "packet schema", passed)
    require(packet["claim_id"] == "CBF.T31", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(source_lock["handoff_id"] == "ec8fc7e0-33c8-4cf1-9ae0-6b941d4da986", "handoff pin", passed)
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)
    require(t30["claim_id"] == "CBF.T30" and all(t30["checks"].values()), "T30 exact upstream", passed)
    require(t30["chiral_finite_operator"]["response_branch_multiplicities"] == {"-4": 16, "-2": 16, "2": 16}, "T30 multiplicities", passed)

    # Independent binomial expansion of sum r^4 and sum r^3 r'.
    q4 = [Fraction(0)] * 5
    b_poly = [Fraction(0)] * 4
    binomial4 = (1, 4, 6, 4, 1)
    binomial3 = (1, 3, 3, 1)
    for _, slope in BRANCHES:
        for degree, coefficient in enumerate(binomial4):
            q4[degree] += coefficient * slope**degree
        for degree, coefficient in enumerate(binomial3):
            b_poly[degree] += slope * coefficient * slope**degree
    require(q4 == [3, -8, 36, -32, 18], "Q4 exact expansion", passed)
    require(b_poly == [-2, 18, -24, 18], "B exact expansion", passed)
    require(packet["four_dimensional_shape"]["Q4_coefficients_ascending"] == [ftext(value) for value in q4], "packet Q4", passed)
    require(packet["four_dimensional_shape"]["B_coefficients_ascending"] == [ftext(value) for value in b_poly], "packet B", passed)

    independent_scans = (
        no_zero_scan(Fraction(-1023, 1024), Fraction(-7, 20), 640),
        no_zero_scan(Fraction(-17, 50), Fraction(27, 100), 1280),
        no_zero_scan(Fraction(29, 100), Fraction(511, 1024), 640),
    )
    require(all(independent_scans), "independent 2560-cell outer scan", passed)

    maximum_box = (Fraction(-344776761, 10**9), Fraction(-344776760, 10**9))
    minimum_box = (Fraction(281284282, 10**9), Fraction(281284283, 10**9))
    max_left = g_bounds((maximum_box[0], maximum_box[0]))
    max_right = g_bounds((maximum_box[1], maximum_box[1]))
    min_left = g_bounds((minimum_box[0], minimum_box[0]))
    min_right = g_bounds((minimum_box[1], minimum_box[1]))
    require(max_left[1] < 0 < max_right[0], "maximum sign bracket", passed)
    require(min_left[0] > 0 > min_right[1], "minimum sign bracket", passed)
    require(gprime_bounds((Fraction(-7, 20), Fraction(-17, 50)))[0] > 0, "maximum uniqueness", passed)
    require(gprime_bounds((Fraction(27, 100), Fraction(29, 100)))[1] < 0, "minimum uniqueness", passed)
    require(log_point(Fraction(4))[0] > 1, "left wall first branch sign", passed)
    require(log_point(Fraction(49, 16))[0] > 1, "left wall second branch sign", passed)

    tiny = Fraction(1, 512)
    tiny_log = log_point(tiny * tiny)
    require(3 * tiny_log[1] + 2 < 0, "tiny branch monotonicity", passed)
    tiny_f_edge = multiply((tiny * tiny, tiny * tiny), subtract(scale(3, tiny_log), (Fraction(1), Fraction(1))))
    tiny_f = (tiny_f_edge[0], Fraction(0))
    middle = (Fraction(1, 2), Fraction(513, 1024))
    plus = (Fraction(1535, 1024), Fraction(3, 2))
    middle_f = multiply(power(middle, 2), subtract(scale(3, log_bounds(power(middle, 2))), (Fraction(1), Fraction(1))))
    plus_f = multiply(power(plus, 2), subtract(scale(3, log_bounds(power(plus, 2))), (Fraction(1), Fraction(1))))
    right_gprime = add(add(scale(4, tiny_f), middle_f), plus_f)
    require(right_gprime[0] > 0, "right wall increasing g", passed)
    require(zero_extended_g(Fraction(1, 2))[1] < 0, "right wall negative g", passed)

    maximum = root(Decimal("-0.344776761"), Decimal("-0.344776760"))
    minimum = root(Decimal("0.281284282"), Decimal("0.281284283"))
    stored_max = packet["MSbar_same_scale_candidate"]["stationary_points"]["local_maximum"]
    stored_min = packet["MSbar_same_scale_candidate"]["stationary_points"]["local_minimum"]
    require(abs(maximum - Decimal(stored_max["decimal"])) < Decimal("1e-47"), "maximum decimal", passed)
    require(abs(minimum - Decimal(stored_min["decimal"])) < Decimal("1e-47"), "minimum decimal", passed)
    require(decimal_gprime(maximum) > 0, "maximum curvature sign", passed)
    require(decimal_gprime(minimum) < 0, "minimum curvature sign", passed)
    require(abs(decimal_v(maximum) - Decimal(stored_max["V"])) < Decimal("1e-35"), "maximum value", passed)
    require(abs(decimal_v(minimum) - Decimal(stored_min["V"])) < Decimal("1e-35"), "minimum value", passed)
    require(abs(-Decimal(4) * decimal_gprime(minimum) / Decimal(3) - Decimal(stored_min["V_second_derivative"])) < Decimal("1e-35"), "minimum curvature value", passed)

    for label, slope in BRANCHES:
        expected = Decimal(1) + Decimal(slope) * minimum
        require(abs(expected - Decimal(stored_min["branch_factors"][label])) < Decimal("1e-35"), f"minimum branch {label}", passed)
    expected_ratios = {
        "r_+2_over_r_-2": (Decimal(1) + minimum) / (Decimal(1) - minimum),
        "r_-2_over_r_-4": (Decimal(1) - minimum) / (Decimal(1) - Decimal(2) * minimum),
        "r_+2_over_r_-4": (Decimal(1) + minimum) / (Decimal(1) - Decimal(2) * minimum),
    }
    for label, expected in expected_ratios.items():
        require(abs(expected - Decimal(stored_min["branch_ratios"][label])) < Decimal("1e-35"), f"minimum ratio {label}", passed)

    left_wall = zero_extended_v(Fraction(-1))
    right_wall = zero_extended_v(Fraction(1, 2))
    minimum_enclosure = v_bounds(minimum_box)
    require(left_wall[1] < minimum_enclosure[0], "left wall below local minimum", passed)
    require(left_wall[1] < right_wall[0], "left wall below right wall", passed)
    require(not packet["MSbar_same_scale_candidate"]["global_minimum_in_open_neutral_chamber"], "no global chamber minimum", passed)
    require(packet["MSbar_same_scale_candidate"]["local_minimum_is_metastable"], "metastable classification", passed)
    require(not packet["MSbar_same_scale_candidate"]["MTT_selected_physical_vacuum"], "candidate not promoted", passed)

    t_star = (Decimal(1) - Decimal(13).sqrt()) / Decimal(6)
    ell_star = -Decimal("0.5") - decimal_a(t_star) / decimal_b(t_star)
    scale_ratio = (-(ell_star + Decimal("1.5")) / Decimal(2)).exp()
    diagnostic = packet["T30_coordinate_scheme_diagnostic"]
    require(abs(t_star - Decimal(diagnostic["coordinate_decimal"])) < Decimal("1e-47"), "T30 coordinate decimal", passed)
    require(abs(ell_star - Decimal(diagnostic["stationary_ell_decimal"])) < Decimal("1e-47"), "T30 ell diagnostic", passed)
    require(abs(scale_ratio - Decimal(diagnostic["MSbar_mu_over_h_decimal"])) < Decimal("1e-47"), "T30 scale diagnostic", passed)
    require(not diagnostic["independently_selected"], "diagnostic not selected", passed)

    orbit = packet["renormalization_orbit"]
    require(orbit["B_derivative_discriminant"] == -1584, "B monotonicity discriminant", passed)
    require(not orbit["scheme_independent_stationary_coordinate"], "no scheme-independent coordinate", passed)
    require(not orbit["selected_scalar_counterterm_rule"], "counterterm rule open", passed)
    require(orbit["c1_can_set_slope_at_any_regular_point"], "linear counterterm slope freedom", passed)
    require(orbit["c2_can_set_curvature_after_slope_fix"], "quadratic counterterm curvature freedom", passed)

    dynamicality = packet["dynamicality_and_global_boundary"]
    require(not dynamicality["four_dimensional_kinetic_term_for_t_selected"], "t kinetic term open", passed)
    require(not dynamicality["equation_of_motion_for_t_selected"], "t equation open", passed)
    require(not dynamicality["selected_Cauchy_normal_or_global_Wick_rotation"], "Wick selection open", passed)
    require(not dynamicality["selected_external_spectral_measure"], "external measure open", passed)
    require(not dynamicality["selected_bosonic_gauge_Higgs_gravity_completion"], "bosonic completion open", passed)

    ledger = packet["parameter_ledger"]
    require(ledger["new_observed_construction_inputs"] == 0, "no observed inputs", passed)
    require(ledger["new_fitted_coefficients"] == 0, "no fitted coefficients", passed)
    require(ledger["candidate_convention_choice_count"] == 4, "four explicit candidate choices", passed)
    require(ledger["candidate_choices_selected_by_MTT"] == 0, "candidate choices unselected", passed)
    require(ledger["accepted_new_physical_parameters"] == 0, "no accepted parameters", passed)

    boundary = packet["physical_boundary"]
    require(boundary["conditional_flat_4D_one_loop_shape_closed"], "conditional shape closed", passed)
    require(boundary["renormalization_scale_orbit_classified"], "scale orbit classified", passed)
    require(boundary["finite_local_counterterm_nonuniqueness_classified"], "counterterm orbit classified", passed)
    require(boundary["MSbar_same_scale_candidate_certified"], "conventional candidate certified", passed)
    for key in (
        "selected_four_dimensional_determinant_closed",
        "source_coordinate_dynamicality_closed",
        "renormalized_physical_vacuum_closed",
        "absolute_SI_scale_closed",
        "sector_generation_mass_map_closed",
        "held_out_physical_observable_emitted",
        "B_ACTION_01_closed",
        "B_QFT_02_closed",
        "B_SM_02_closed",
    ):
        require(not boundary[key], f"open boundary: {key}", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "physical packet counters", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "physical row counters", passed)

    root_payload = source_root_payload(source_lock)
    root_hash = hashlib.sha256(json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    require(root_payload == packet["source_provenance"]["source_root_payload"], "source-root payload", passed)
    require(root_hash == packet["source_provenance"]["source_root_sha256"], "source-root digest", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary", passed)

    print(f"CBF.T31 independent verification passed: {len(passed)}/{len(passed)} checks")


if __name__ == "__main__":
    main()
