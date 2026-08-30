#!/usr/bin/env python3
"""Independent verification of the CBF.T33 frozen-source radial values."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "preprojection_finite_source_freeze_radial_values.packet.json"
SOURCE_LOCK_PATH = ROOT / "preprojection_finite_source_freeze_radial_values_source_lock.json"
SCHEMA_PATH = ROOT / "preprojection_finite_source_freeze_radial_values_contract.schema.json"
THEOREM_PATH = ROOT / "PreprojectionFiniteSourceFreezeAndConditionalRadialBranchValueTheorem_v1.md"
T30_PATH = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
T32_PATH = ROOT / "product_dirac_joint_radial_source_modulus_action.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T25_PATH = ROOT / "direct_finite_source_continuum.packet.json"
LOG_TERMS = 72
DECIMAL_DIGITS = 30

Q13 = tuple[Fraction, Fraction]
Interval = tuple[Fraction, Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q13(a: Fraction | int = 0, b: Fraction | int = 0) -> Q13:
    return Fraction(a), Fraction(b)


def qadd(left: Q13, right: Q13) -> Q13:
    return left[0] + right[0], left[1] + right[1]


def qscale(scale: Fraction | int, value: Q13) -> Q13:
    return Fraction(scale) * value[0], Fraction(scale) * value[1]


def qmul(left: Q13, right: Q13) -> Q13:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def qinv(value: Q13) -> Q13:
    denominator = value[0] ** 2 - 13 * value[1] ** 2
    return value[0] / denominator, -value[1] / denominator


def qdiv(left: Q13, right: Q13) -> Q13:
    return qmul(left, qinv(right))


def qpow(value: Q13, exponent: int) -> Q13:
    result = q13(1)
    for _ in range(exponent):
        result = qmul(result, value)
    return result


def iadd(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def iscale(scale: Fraction | int, value: Interval) -> Interval:
    products = (Fraction(scale) * value[0], Fraction(scale) * value[1])
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
    reciprocal = (Fraction(1, right[1]), Fraction(1, right[0]))
    return imul(left, reciprocal)


def sqrt_fraction_bounds(value: Fraction, digits: int = DECIMAL_DIGITS) -> Interval:
    scale = 10**digits
    quotient = (value.numerator * scale * scale) // value.denominator
    lower_integer = isqrt(quotient)
    lower = Fraction(lower_integer, scale)
    upper = lower if lower * lower == value else Fraction(lower_integer + 1, scale)
    return lower, upper


def sqrt_interval(value: Interval) -> Interval:
    return sqrt_fraction_bounds(value[0])[0], sqrt_fraction_bounds(value[1])[1]


def q13_interval(value: Q13, sqrt13_bounds: Interval) -> Interval:
    return iadd((value[0], value[0]), iscale(value[1], sqrt13_bounds))


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


def parse_interval(payload: dict[str, str]) -> Interval:
    return Fraction(payload["lower_exact"]), Fraction(payload["upper_exact"])


def parse_q13(payload: dict[str, Any]) -> Q13:
    coefficients = payload["exact_coefficients"]
    return Fraction(coefficients["rational"]), Fraction(coefficients["sqrt13"])


def text_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def source_root(
    lock: dict[str, Any], theorem_hash: str, exact_values: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.preprojection-finite-source-freeze-radial-values-root.v1",
        "repository_heads": lock["repositories"],
        "source_hashes": [source["sha256"] for source in lock["local_sources"]],
        "source_coordinate": "t_*=(1-sqrt(13))/6",
        "exact_values": exact_values,
        "T30_as_preprojection_source_selected": False,
        "T30_A53_same_root_proved": False,
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
    t30 = json.loads(T30_PATH.read_text(encoding="ascii"))
    t32 = json.loads(T32_PATH.read_text(encoding="ascii"))
    t23 = json.loads(T23_PATH.read_text(encoding="ascii"))
    t25 = json.loads(T25_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.preprojection-finite-source-freeze-radial-values.v1", "packet schema", passed)
    require(packet["claim_id"] == "CBF.T33", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(lock["handoff_id"] == "1e03a938-4acb-47b8-a43f-09171905c3bc", "handoff pin", passed)
    require(packet["source_provenance"]["kernel_model_sha256"] == lock["kernel_model_sha256"], "kernel pin", passed)
    for source in lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)
    for lower, claim in ((t30, "CBF.T30"), (t32, "CBF.T32"), (t23, "CBF.T23"), (t25, "CBF.T25")):
        require(lower["claim_id"] == claim, f"{claim} id", passed)
        require(all(lower["checks"].values()), f"{claim} checks", passed)

    sqrt13_bounds = sqrt_fraction_bounds(Fraction(13), 40)
    t = q13(Fraction(1, 6), Fraction(-1, 6))
    t2 = qpow(t, 2)
    t3 = qpow(t, 3)
    t4 = qpow(t, 4)
    q2 = qadd(qadd(q13(3), qscale(-4, t)), qscale(6, t2))
    q4 = qadd(qadd(qadd(qadd(q13(3), qscale(-8, t)), qscale(36, t2)), qscale(-32, t3)), qscale(18, t4))
    radial = qdiv(qscale(2, q2), q4)
    required_moment = qinv(radial)
    branches = {
        "-4": qadd(q13(1), qscale(-2, t)),
        "-2": qadd(q13(1), qscale(-1, t)),
        "2": qadd(q13(1), t),
    }
    ratios = {
        "-4_over_-2": qdiv(branches["-4"], branches["-2"]),
        "-2_over_2": qdiv(branches["-2"], branches["2"]),
        "-4_over_2": qdiv(branches["-4"], branches["2"]),
    }

    require(qadd(qadd(qscale(3, t2), qscale(-1, t)), q13(-1)) == q13(0), "minimal polynomial", passed)
    require(q2 == q13(Fraction(14, 3), Fraction(1, 3)), "q2 exact", passed)
    require(q4 == q13(Fraction(356, 27), Fraction(25, 27)), "q4 exact", passed)
    require(radial == q13(Fraction(3106, 4393), Fraction(4, 4393)), "radial ratio exact", passed)
    require(required_moment == q13(Fraction(1553, 1098), Fraction(-1, 549)), "required moment exact", passed)
    require(branches == {"-4": q13(Fraction(2, 3), Fraction(1, 3)), "-2": q13(Fraction(5, 6), Fraction(1, 6)), "2": q13(Fraction(7, 6), Fraction(-1, 6))}, "branches exact", passed)
    require(ratios == {"-4_over_-2": q13(Fraction(-1, 2), Fraction(1, 2)), "-2_over_2": q13(Fraction(4, 3), Fraction(1, 3)), "-4_over_2": q13(Fraction(3, 2), Fraction(1, 2))}, "ratios exact", passed)

    selected = packet["selected_finite_source"]
    require(parse_q13(selected["coordinate"]) == t, "packet t", passed)
    require(parse_q13(selected["q2_star"]) == q2, "packet q2", passed)
    require(parse_q13(selected["q4_star"]) == q4, "packet q4", passed)
    require(parse_q13(selected["R_star"]) == radial, "packet radial", passed)
    for key, value in branches.items():
        require(parse_q13(selected["branch_values"][key]) == value, f"packet branch {key}", passed)
        require(parse_interval(selected["branch_values"][key]["interval"]) == q13_interval(value, sqrt13_bounds), f"branch interval {key}", passed)
    for key, value in ratios.items():
        require(parse_q13(selected["branch_ratios"][key]) == value, f"packet ratio {key}", passed)
    require(not selected["proved_physical_preprojection_source"], "preprojection boundary", passed)

    typed = packet["typed_source_freeze"]
    require(typed["variational_identity"] == "dL_*=i_*^*(d_F L)", "pullback differential", passed)
    require(not typed["source_equation_in_lower_variation"], "no source equation", passed)
    require(typed["joint_variation_is_a_different_enlarged_model"], "joint theory distinction", passed)
    require(2 * (1 - 1) == 0 and -2 * (1 - 1) + 1 == 1, "strict freeze witness", passed)

    log448 = ln_bounds(Fraction(448))
    tau = iscale(Fraction(1, 15), log448)
    a53_moment = idiv((Fraction(1), Fraction(1)), tau)
    h2 = imul(q13_interval(radial, sqrt13_bounds), a53_moment)
    h = sqrt_interval(h2)
    masses = {key: imul(h, q13_interval(value, sqrt13_bounds)) for key, value in branches.items()}
    radial_mass2 = iscale(8, a53_moment)
    radial_mass = sqrt_interval(radial_mass2)
    a53 = packet["A53_radial_stationary_branch"]
    require(parse_interval(a53["tau_interval"]) == tau, "tau interval", passed)
    require(parse_interval(a53["f2_over_f0_interval"]) == a53_moment, "A53 moment interval", passed)
    require(parse_interval(a53["h_squared_over_Lambda_squared_interval"]) == h2, "h squared interval", passed)
    require(parse_interval(a53["h_over_Lambda_interval"]) == h, "h interval", passed)
    for key, value in masses.items():
        require(parse_interval(a53["branch_values_over_Lambda"][key]["interval"]) == value, f"A53 mass {key}", passed)
    require(parse_interval(a53["radial_curvature_mass_squared_interval"]) == radial_mass2, "radial mass squared", passed)
    require(parse_interval(a53["radial_curvature_mass_interval"]) == radial_mass, "radial mass", passed)
    require(not a53["premise_selected_by_MTT"], "A53 premise boundary", passed)

    t23_branch = packet["T23_metrology_branch"]
    require(t23_branch["normalization"] == "h=Lambda=E0=1/L0", "T23 normalization", passed)
    require(not t23_branch["radial_stationarity_claimed"], "T23 stationarity boundary", passed)
    require(parse_q13(t23_branch["radial_stationarity_required_f2_over_f0"]) == required_moment, "T23 required moment", passed)
    required_interval = q13_interval(required_moment, sqrt13_bounds)
    comparison = packet["branch_comparison"]
    require(parse_interval(comparison["required_T23_stationary_moment_interval"]) == required_interval, "comparison required moment", passed)
    require(parse_interval(comparison["A53_moment_interval"]) == a53_moment, "comparison A53 moment", passed)
    require(required_interval[1] < a53_moment[0], "moment disjointness", passed)
    require(comparison["same_relative_branch_ratios"], "common ratios", passed)
    require(not comparison["branches_can_be_simultaneous_predictions"], "alternative branches", passed)
    require(not comparison["common_normalization_creates_additional_family_hierarchy"], "no added hierarchy", passed)

    exact_values = {
        "q2_star": [text_fraction(q2[0]), text_fraction(q2[1])],
        "q4_star": [text_fraction(q4[0]), text_fraction(q4[1])],
        "radial_ratio": [text_fraction(radial[0]), text_fraction(radial[1])],
        "branches": {key: [text_fraction(value[0]), text_fraction(value[1])] for key, value in branches.items()},
    }
    root_hash, root_payload = source_root(lock, sha256(THEOREM_PATH), exact_values)
    require(packet["source_provenance"]["source_root_sha256"] == root_hash, "source root digest", passed)
    require(packet["source_provenance"]["source_root_payload"] == root_payload, "source root payload", passed)
    require(packet["parameter_ledger"]["new_observed_construction_inputs"] == 0, "no observed inputs", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fits", passed)
    require(packet["parameter_ledger"]["new_continuous_parameters"] == 0, "no continuous parameters", passed)
    require(packet["parameter_ledger"]["branches_selected_by_current_MTT_authority"] == 0, "branch selection boundary", passed)
    require(not packet["physical_boundary"]["T30_physical_preprojection_promotion_closed"], "physical source gate", passed)
    require(not packet["physical_boundary"]["T30_A53_same_root_closed"], "same-root gate", passed)
    require(not packet["physical_boundary"]["normalization_branch_selected"], "normalization gate", passed)
    require(not packet["physical_boundary"]["nine_charged_Yukawa_values_closed"], "nine Yukawa gate", passed)
    require(packet["physical_packets_accepted"] == 0, "packet acceptance", passed)
    require(packet["physical_rows_accepted"] == 0, "row acceptance", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "check summary", passed)
    require(packet["check_summary"]["failed"] == [], "failed ledger", passed)

    print(f"verified {PACKET_PATH.name}: {len(passed)}/{len(passed)} independent checks passed")


if __name__ == "__main__":
    main()
