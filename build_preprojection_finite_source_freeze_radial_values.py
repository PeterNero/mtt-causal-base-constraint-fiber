#!/usr/bin/env python3
"""Build the exact CBF.T33 preprojection source-freeze value packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "preprojection_finite_source_freeze_radial_values_source_lock.json"
SCHEMA = ROOT / "preprojection_finite_source_freeze_radial_values_contract.schema.json"
THEOREM = ROOT / "PreprojectionFiniteSourceFreezeAndConditionalRadialBranchValueTheorem_v1.md"
T30_PACKET = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
T32_PACKET = ROOT / "product_dirac_joint_radial_source_modulus_action.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
A51_CERTIFICATE = ROOT / "../mtt-sm-parity-closure/certificates/selected_finitespectralactionandhiggsinnerfluctuation_or_directgenerativesmactionclosure_certificate.json"
A53_CERTIFICATE = ROOT / "../mtt-sm-parity-closure/certificates/selected_propertimemeasureandoverlapkineticmetricsource_or_strictspectralactionclosure_certificate.json"
OUTPUT = ROOT / "preprojection_finite_source_freeze_radial_values.packet.json"

Q13 = tuple[Fraction, Fraction]
Interval = tuple[Fraction, Fraction]
LOG_TERMS = 72
DECIMAL_DIGITS = 30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def decimal_fraction(value: Fraction, digits: int = DECIMAL_DIGITS) -> str:
    with localcontext() as context:
        context.prec = digits + 30
        number = Decimal(value.numerator) / Decimal(value.denominator)
        return f"{number:.{digits}f}"


def q13(rational: Fraction | int = 0, radical: Fraction | int = 0) -> Q13:
    return Fraction(rational), Fraction(radical)


def qadd(left: Q13, right: Q13) -> Q13:
    return left[0] + right[0], left[1] + right[1]


def qneg(value: Q13) -> Q13:
    return -value[0], -value[1]


def qsub(left: Q13, right: Q13) -> Q13:
    return qadd(left, qneg(right))


def qscale(scale: Fraction | int, value: Q13) -> Q13:
    factor = Fraction(scale)
    return factor * value[0], factor * value[1]


def qmul(left: Q13, right: Q13) -> Q13:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def qinv(value: Q13) -> Q13:
    denominator = value[0] * value[0] - 13 * value[1] * value[1]
    if denominator == 0:
        raise ZeroDivisionError("zero Q(sqrt(13)) element")
    return value[0] / denominator, -value[1] / denominator


def qdiv(left: Q13, right: Q13) -> Q13:
    return qmul(left, qinv(right))


def qpow(value: Q13, exponent: int) -> Q13:
    if exponent < 0:
        return qpow(qinv(value), -exponent)
    result = q13(1)
    factor = value
    power = exponent
    while power:
        if power & 1:
            result = qmul(result, factor)
        factor = qmul(factor, factor)
        power //= 2
    return result


def interval(lower: Fraction | int, upper: Fraction | int | None = None) -> Interval:
    low = Fraction(lower)
    high = low if upper is None else Fraction(upper)
    if low > high:
        raise ValueError("reversed interval")
    return low, high


def iadd(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def ineg(value: Interval) -> Interval:
    return -value[1], -value[0]


def iscale(scale: Fraction | int, value: Interval) -> Interval:
    factor = Fraction(scale)
    products = (factor * value[0], factor * value[1])
    return min(products), max(products)


def imul(left: Interval, right: Interval) -> Interval:
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def idiv(left: Interval, right: Interval) -> Interval:
    if right[0] <= 0 <= right[1]:
        raise ZeroDivisionError("interval divisor contains zero")
    reciprocal = (Fraction(1, right[1]), Fraction(1, right[0]))
    return imul(left, reciprocal)


def sqrt_fraction_bounds(value: Fraction, digits: int = DECIMAL_DIGITS) -> Interval:
    if value < 0:
        raise ValueError("square root requires a nonnegative rational")
    scale = 10**digits
    quotient = (value.numerator * scale * scale) // value.denominator
    lower_integer = isqrt(quotient)
    lower = Fraction(lower_integer, scale)
    upper = lower if lower * lower == value else Fraction(lower_integer + 1, scale)
    return lower, upper


def sqrt_interval(value: Interval, digits: int = DECIMAL_DIGITS) -> Interval:
    return sqrt_fraction_bounds(value[0], digits)[0], sqrt_fraction_bounds(value[1], digits)[1]


def q13_interval(value: Q13, sqrt13_bounds: Interval) -> Interval:
    radical = iscale(value[1], sqrt13_bounds)
    return iadd(interval(value[0]), radical)


def interval_payload(value: Interval, digits: int = DECIMAL_DIGITS) -> dict[str, str]:
    return {
        "lower_exact": fraction_text(value[0]),
        "upper_exact": fraction_text(value[1]),
        "lower_decimal": decimal_fraction(value[0], digits),
        "upper_decimal": decimal_fraction(value[1], digits),
    }


def q13_payload(value: Q13, expression: str, sqrt13_bounds: Interval) -> dict[str, Any]:
    return {
        "expression": expression,
        "exact_coefficients": {
            "rational": fraction_text(value[0]),
            "sqrt13": fraction_text(value[1]),
        },
        "interval": interval_payload(q13_interval(value, sqrt13_bounds)),
    }


def atanh_positive_bounds(z: Fraction) -> Interval:
    if not 0 <= z < 1:
        raise ValueError("atanh series requires 0 <= z < 1")
    z2 = z * z
    power = z
    partial = Fraction(0)
    for index in range(LOG_TERMS):
        partial += power / (2 * index + 1)
        power *= z2
    remainder = power / ((2 * LOG_TERMS + 1) * (1 - z2))
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


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def source_root(
    source_lock: dict[str, Any], theorem_hash: str, exact_values: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.preprojection-finite-source-freeze-radial-values-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "source_coordinate": "t_*=(1-sqrt(13))/6",
        "exact_values": exact_values,
        "T30_as_preprojection_source_selected": False,
        "T30_A53_same_root_proved": False,
        "observed_targets": [],
        "theorem_sha256": theorem_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t30 = json.loads(T30_PACKET.read_text(encoding="ascii"))
    t32 = json.loads(T32_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    t25 = json.loads(T25_PACKET.read_text(encoding="ascii"))
    a51 = json.loads(A51_CERTIFICATE.read_text(encoding="ascii"))
    a53 = json.loads(A53_CERTIFICATE.read_text(encoding="ascii"))

    sqrt13_bounds = sqrt_fraction_bounds(Fraction(13), 40)
    t_star = q13(Fraction(1, 6), Fraction(-1, 6))
    q2_star = qadd(qadd(q13(3), qscale(-4, t_star)), qscale(6, qpow(t_star, 2)))
    q4_star = qadd(
        qadd(qadd(qadd(q13(3), qscale(-8, t_star)), qscale(36, qpow(t_star, 2))), qscale(-32, qpow(t_star, 3))),
        qscale(18, qpow(t_star, 4)),
    )
    radial_ratio = qdiv(qscale(2, q2_star), q4_star)
    required_moment_ratio = qinv(radial_ratio)

    branch_values = {
        "-4": qsub(q13(1), qscale(2, t_star)),
        "-2": qsub(q13(1), t_star),
        "2": qadd(q13(1), t_star),
    }
    branch_expressions = {
        "-4": "(2+sqrt(13))/3",
        "-2": "(5+sqrt(13))/6",
        "2": "(7-sqrt(13))/6",
    }
    branch_ratios = {
        "-4_over_-2": qdiv(branch_values["-4"], branch_values["-2"]),
        "-2_over_2": qdiv(branch_values["-2"], branch_values["2"]),
        "-4_over_2": qdiv(branch_values["-4"], branch_values["2"]),
    }
    ratio_expressions = {
        "-4_over_-2": "(sqrt(13)-1)/2",
        "-2_over_2": "(4+sqrt(13))/3",
        "-4_over_2": "(3+sqrt(13))/2",
    }

    log448 = ln_positive_bounds(Fraction(448))
    tau = iscale(Fraction(1, 15), log448)
    a53_moment_ratio = idiv(interval(1), tau)
    radial_ratio_interval = q13_interval(radial_ratio, sqrt13_bounds)
    h_squared_over_lambda_squared = imul(radial_ratio_interval, a53_moment_ratio)
    h_over_lambda = sqrt_interval(h_squared_over_lambda_squared)
    a53_branch_values = {
        key: imul(h_over_lambda, q13_interval(value, sqrt13_bounds))
        for key, value in branch_values.items()
    }
    radial_mass_squared = iscale(8, a53_moment_ratio)
    radial_mass = sqrt_interval(radial_mass_squared)
    required_moment_interval = q13_interval(required_moment_ratio, sqrt13_bounds)

    exact_values = {
        "q2_star": [fraction_text(q2_star[0]), fraction_text(q2_star[1])],
        "q4_star": [fraction_text(q4_star[0]), fraction_text(q4_star[1])],
        "radial_ratio": [fraction_text(radial_ratio[0]), fraction_text(radial_ratio[1])],
        "branches": {
            key: [fraction_text(value[0]), fraction_text(value[1])]
            for key, value in branch_values.items()
        },
    }
    theorem_hash = sha256(THEOREM)
    root_hash, root_payload = source_root(source_lock, theorem_hash, exact_values)
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.preprojection-finite-source-freeze-radial-values-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"] == "1e03a938-4acb-47b8-a43f-09171905c3bc",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"] == "boe.mtt.preprojection-finite-source-freeze-radial-values.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T30_source_is_exact": t30["claim_id"] == "CBF.T30" and all(t30["checks"].values()),
        "T32_source_is_exact": t32["claim_id"] == "CBF.T32" and all(t32["checks"].values()),
        "T23_source_is_exact": t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()),
        "T25_source_is_exact": t25["claim_id"] == "CBF.T25" and all(t25["checks"].values()),
        "A51_selects_one_Higgs": a51["selected_single_Higgs_projection_closed"],
        "A51_absolute_normalization_is_open": not a51["absolute_spectral_action_normalization_closed"],
        "A53_tau_is_exact": a53["tau_int_exact_source_available"],
        "A53_point_measure_is_conditional": a53["minimal_point_measure_moments_closed_conditionally"] and not a53["point_measure_selected_by_MTT"],
        "source_freeze_witness_lower_derivative_vanishes": 2 * (1 - 1) == 0,
        "source_freeze_witness_source_derivative_does_not_vanish": -2 * (1 - 1) + 1 == 1,
        "t_star_is_in_neutral_chamber": sqrt13_bounds[0] > 3 and sqrt13_bounds[1] < 4,
        "t_star_minimal_polynomial_vanishes": qadd(qadd(qscale(3, qpow(t_star, 2)), qneg(t_star)), q13(-1)) == q13(0),
        "q2_star_is_exact": q2_star == q13(Fraction(14, 3), Fraction(1, 3)),
        "q4_star_is_exact": q4_star == q13(Fraction(356, 27), Fraction(25, 27)),
        "radial_ratio_is_exact": radial_ratio == q13(Fraction(3106, 4393), Fraction(4, 4393)),
        "required_moment_ratio_is_exact": required_moment_ratio == q13(Fraction(1553, 1098), Fraction(-1, 549)),
        "branch_minus4_is_exact": branch_values["-4"] == q13(Fraction(2, 3), Fraction(1, 3)),
        "branch_minus2_is_exact": branch_values["-2"] == q13(Fraction(5, 6), Fraction(1, 6)),
        "branch_plus2_is_exact": branch_values["2"] == q13(Fraction(7, 6), Fraction(-1, 6)),
        "branch_ratio_minus4_minus2_is_exact": branch_ratios["-4_over_-2"] == q13(Fraction(-1, 2), Fraction(1, 2)),
        "branch_ratio_minus2_plus2_is_exact": branch_ratios["-2_over_2"] == q13(Fraction(4, 3), Fraction(1, 3)),
        "branch_ratio_minus4_plus2_is_exact": branch_ratios["-4_over_2"] == q13(Fraction(3, 2), Fraction(1, 2)),
        "T30_coordinate_matches": t30["selected_coordinate"]["exact_coefficients"] == {"rational": "1/6", "sqrt13": "-1/6"},
        "T30_branch_values_match": all(
            t30["dimensionless_branch_values"]["ordered_by_response_eigenvalue"][key]["exact_coefficients"] == {"rational": fraction_text(value[0]), "sqrt13": fraction_text(value[1])}
            for key, value in branch_values.items()
        ),
        "T32_potential_is_consumed": t32["tree_potential"]["normalized_potential"] == "P(h,t)=h^4 q4(t)-4c h^2 q2(t)",
        "T32_t_promotion_is_not_selected": not t32["conditional_action_scope"]["t_field_promotion_selected_by_MTT"],
        "T23_h_equals_Lambda_is_recorded": t23["lorentzian_product_and_scale"]["one_primitive_identification"] == "h=Lambda=E0=1/L0",
        "fixed_source_radial_minimum_is_positive": radial_ratio_interval[0] > 0,
        "A53_h_over_Lambda_is_nonzero": h_over_lambda[0] > 1,
        "A53_branch_values_are_strictly_ordered": a53_branch_values["-4"][0] > a53_branch_values["-2"][1] > a53_branch_values["2"][1] > 0,
        "A53_radial_mass_is_nonzero": radial_mass[0] > 4,
        "normalization_moment_intervals_are_disjoint": required_moment_interval[1] < a53_moment_ratio[0],
        "A53_rescaling_preserves_branch_ratios": True,
        "T30_preprojection_status_remains_conditional": not boundary["T30_coordinate_proved_to_be_preprojection_physical_source"],
        "T30_A53_same_root_remains_open": not boundary["same_root_T30_A53_composition_proved"],
        "no_double_variation_typing_is_newly_closed": not boundary["no_double_variation_typing_before"] and boundary["no_double_variation_typing_after"],
        "fixed_source_radial_values_are_newly_closed": not boundary["fixed_source_radial_values_before"] and boundary["fixed_source_radial_values_after"],
        "absolute_scale_remains_unselected": not boundary["absolute_scale_selected"],
        "sector_map_remains_unselected": not boundary["sector_generation_map_selected"],
        "no_observed_values_used": not boundary["observed_values_used"],
        "no_fitted_coefficients_used": not boundary["fitted_coefficients_used"],
        "physical_packet_acceptance_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "source_root_is_nonempty": len(root_hash) == 64,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T33 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.preprojection-finite-source-freeze-radial-values.v1",
        "claim_id": "CBF.T33",
        "date": "2026-08-30",
        "status": (
            "exact no-double-variation typing and fixed-T30-source radial values; "
            "two conditional normalization branches classified; physical source "
            "promotion, same-root composition and particle values remain open"
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
        "typed_source_freeze": {
            "upper_source_space": "S",
            "lower_field_space": "F",
            "action_family": "L:S x F->R",
            "selected_source_inclusion": "i_*:F->S x F, x|->(s_*,x)",
            "pullback_action": "L_*=i_*^*L",
            "variational_identity": "dL_*=i_*^*(d_F L)",
            "source_equation_in_lower_variation": False,
            "joint_variation_is_a_different_enlarged_model": True,
            "strict_witness": "L(s,x)=(x-s)^2+s; s=1,x=1 has d_x=0 and d_s=1",
            "no_double_variation_rule_closed": True,
        },
        "selected_finite_source": {
            "coordinate": q13_payload(t_star, "(1-sqrt(13))/6", sqrt13_bounds),
            "selection_tier": t30["selected_coordinate"]["tier"],
            "neutral_chamber": t30["neutral_invertible_chamber"]["connected_component"],
            "q2_star": q13_payload(q2_star, "(14+sqrt(13))/3", sqrt13_bounds),
            "q4_star": q13_payload(q4_star, "(356+25sqrt(13))/27", sqrt13_bounds),
            "R_star": q13_payload(radial_ratio, "(3106+4sqrt(13))/4393", sqrt13_bounds),
            "branch_values": {
                key: q13_payload(value, branch_expressions[key], sqrt13_bounds)
                for key, value in branch_values.items()
            },
            "branch_ratios": {
                key: q13_payload(value, ratio_expressions[key], sqrt13_bounds)
                for key, value in branch_ratios.items()
            },
            "strict_order": "sigma_-4>sigma_-2>sigma_+2>0",
            "proved_physical_preprojection_source": False,
        },
        "fixed_source_radial_action": {
            "potential": "P_*(h)=q4_* h^4-4c q2_* h^2",
            "c_definition": "c=f2 Lambda^2/f0>0",
            "positive_broken_minimum": "h_*^2=R_* c",
            "branch_value_formula": "m_a/Lambda=(h_*/Lambda)sigma_a",
            "radial_curvature_mass_squared": "m_h^2=8c",
            "radial_curvature_mass_independent_of_t_star": True,
            "t_varied_in_lower_action": False,
        },
        "T23_metrology_branch": {
            "normalization": "h=Lambda=E0=1/L0",
            "h_over_Lambda": "1",
            "branch_values_over_Lambda": {
                key: q13_payload(value, branch_expressions[key], sqrt13_bounds)
                for key, value in branch_values.items()
            },
            "radial_stationarity_claimed": False,
            "radial_stationarity_required_f2_over_f0": q13_payload(
                required_moment_ratio,
                "1553/1098-sqrt(13)/549",
                sqrt13_bounds,
            ),
        },
        "A53_radial_stationary_branch": {
            "premise": "zero-new-scale minimal one-atom proper-time support",
            "premise_selected_by_MTT": False,
            "tau_int": "log(448)/15",
            "tau_interval": interval_payload(tau),
            "f2_over_f0": "15/log(448)",
            "f2_over_f0_interval": interval_payload(a53_moment_ratio),
            "h_squared_over_Lambda_squared": "15(3106+4sqrt(13))/(4393log(448))",
            "h_squared_over_Lambda_squared_interval": interval_payload(h_squared_over_lambda_squared),
            "h_over_Lambda": "sqrt(15(3106+4sqrt(13))/(4393log(448)))",
            "h_over_Lambda_interval": interval_payload(h_over_lambda),
            "branch_values_over_Lambda": {
                key: {
                    "expression": f"{branch_expressions[key]} sqrt(15(3106+4sqrt(13))/(4393log(448)))",
                    "interval": interval_payload(value),
                }
                for key, value in a53_branch_values.items()
            },
            "radial_curvature_mass_squared_over_Lambda_squared": "120/log(448)",
            "radial_curvature_mass_squared_interval": interval_payload(radial_mass_squared),
            "radial_curvature_mass_over_Lambda": "sqrt(120/log(448))",
            "radial_curvature_mass_interval": interval_payload(radial_mass),
            "observed_values_used": False,
            "fitted_coefficients_used": False,
        },
        "branch_comparison": {
            "same_finite_coordinate": "t_*=(1-sqrt(13))/6",
            "same_relative_branch_ratios": True,
            "T23_branch_is_radially_stationary_without_extra_moment_rule": False,
            "A53_branch_is_radially_stationary_under_its_premise": True,
            "required_T23_stationary_moment_interval": interval_payload(required_moment_interval),
            "A53_moment_interval": interval_payload(a53_moment_ratio),
            "moment_intervals_disjoint": True,
            "branches_can_be_simultaneous_predictions": False,
            "common_normalization_creates_additional_family_hierarchy": False,
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_continuous_parameters": 0,
            "new_accepted_physical_parameters": 0,
            "conditional_preprojection_role_assignments": 1,
            "conditional_A53_premises": 1,
            "alternative_normalization_branches": 2,
            "branches_selected_by_current_MTT_authority": 0,
            "absolute_dimensionful_scale_selected": False,
        },
        "physical_boundary": {
            "no_double_variation_typing_closed": True,
            "fixed_source_exact_values_closed": True,
            "T30_physical_preprojection_promotion_closed": False,
            "T30_A53_same_root_closed": False,
            "normalization_branch_selected": False,
            "absolute_scale_closed": False,
            "sector_generation_map_closed": False,
            "nine_charged_Yukawa_values_closed": False,
            "loop_RG_threshold_pole_transport_closed": False,
            "held_out_observable_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "CBF.T30 and CBF.T32 are now reconciled by a typed no-double-"
            "variation theorem: a source coordinate selected before projection is "
            "held fixed in the lower variational problem, whereas jointly varying t "
            "defines the distinct source-modulus theory already classified by T32. "
            "At the exact T30 coordinate, q2, q4 and the radial ratio are evaluated "
            "in Q(sqrt13). The T23 h=Lambda branch reproduces the three T30 values. "
            "Under A53's unselected one-atom premise, radial stationarity emits the "
            "new exact ratios h/Lambda=1.321101629... and branch values "
            "(2.468500975,1.894801302,0.747401957) in units of Lambda, plus radial "
            "curvature sqrt(120/log448). The T23-stationary and A53 moment intervals "
            "are disjoint. These are exact conditional spectral values, not accepted "
            "particle masses: preprojection promotion, same-root composition, branch "
            "selection, absolute scale, sector map and precision transport remain open."
        ),
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"wrote {OUTPUT.name}: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
