#!/usr/bin/env python3
"""Independently verify the CBF.T35 frozen-source pushforward packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "frozen_source_four_dimensional_fermion_pushforward_source_lock.json"
SCHEMA = ROOT / "frozen_source_four_dimensional_fermion_pushforward_contract.schema.json"
THEOREM = ROOT / "FrozenSourceFourDimensionalFermionPushforwardAndClosureJetRenormalizationTheorem_v1.md"
PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T30_PACKET = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
T31_PACKET = ROOT / "four_dimensional_fermion_determinant_scheme_classification.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
QFT_REGULATOR = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_gauge_compatible_finite_bv_regulator_criterion.certificate.json"

Q13 = tuple[Fraction, Fraction]
PI = Decimal("3.141592653589793238462643383279502884197169399375105820974944")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def q13(a: Fraction | int = 0, b: Fraction | int = 0) -> Q13:
    return Fraction(a), Fraction(b)


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
    norm = value[0] * value[0] - 13 * value[1] * value[1]
    return value[0] / norm, -value[1] / norm


def qdiv(left: Q13, right: Q13) -> Q13:
    return qmul(left, qinv(right))


def qpow(value: Q13, exponent: int) -> Q13:
    result = q13(1)
    for _ in range(exponent):
        result = qmul(result, value)
    return result


def qsum(values: list[Q13]) -> Q13:
    result = q13()
    for value in values:
        result = qadd(result, value)
    return result


def qpayload(value: Q13) -> dict[str, str]:
    return {"rational": str(value[0]), "sqrt13_coefficient": str(value[1])}


def interval_contains(payload: dict[str, str], value: Decimal) -> bool:
    return Decimal(payload["lower_decimal"]) <= value <= Decimal(payload["upper_decimal"])


def reconstruct_root(
    source_lock: dict[str, Any],
    t30: dict[str, Any],
    t34: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "boe.mtt.frozen-source-four-dimensional-pushforward-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "selected_source_coordinate": t30["selected_coordinate"]["expression"],
        "source_role": "frozen upstream coordinate; excluded from lower variational tangent",
        "selected_radial_coordinate": t34["promoted_radial_values"]["h_over_Lambda"],
        "one_loop_branch_multiplicity": t30["chiral_finite_operator"][
            "response_branch_multiplicities"
        ]["-4"],
        "counterterm_class": "delta_Omega+delta_m2 h^2+delta_lambda h^4",
        "matching_rule": "preserve value, first derivative and Hessian at h=H",
        "excluded_from_root": [
            "observed masses",
            "fitted counterterms",
            "selected external BV regulator",
            "determinant-line orientation",
            "RG fixed-point assertion",
        ],
    }


def main() -> None:
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    packet = load(PACKET)
    t30 = load(T30_PACKET)
    t31 = load(T31_PACKET)
    t34 = load(T34_PACKET)
    qft_regulator = load(QFT_REGULATOR)
    theorem = THEOREM.read_text(encoding="ascii")

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("claim_id", packet["claim_id"] == "CBF.T35")
    check("date", packet["date"] == "2026-08-30")
    check("source_lock_hash", packet["source_provenance"]["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("schema_hash", packet["source_provenance"]["contract_schema_sha256"] == sha256(SCHEMA))
    check("theorem_hash", packet["source_provenance"]["theorem_sha256"] == sha256(THEOREM))
    check("handoff_id", packet["source_provenance"]["handoff_id"] == source_lock["handoff_id"])
    check("source_count", packet["source_provenance"]["source_count"] == len(source_lock["local_sources"]))
    for index, source in enumerate(source_lock["local_sources"], start=1):
        check(
            f"source_{index:02d}_hash",
            sha256((ROOT / source["path"]).resolve()) == source["sha256"],
        )

    root = reconstruct_root(source_lock, t30, t34)
    check("source_root_payload", packet["source_provenance"]["source_root_payload"] == root)
    check("source_root_hash", packet["source_provenance"]["source_root_sha256"] == canonical_hash(root))
    check("source_root_excludes_observations", "observed masses" in root["excluded_from_root"])
    check("source_root_excludes_regulator", "selected external BV regulator" in root["excluded_from_root"])

    check("all_required_fields", set(schema["required"]) <= set(packet))
    check("no_extra_top_level_fields", set(packet) <= set(schema["properties"]))
    check("builder_checks", all(packet["checks"].values()))
    check("builder_check_count", packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(packet["checks"]))
    check("builder_failed_empty", packet["check_summary"]["failed"] == [])

    t_star = q13(Fraction(1, 6), Fraction(-1, 6))
    sigmas = {
        "-4": q13(Fraction(2, 3), Fraction(1, 3)),
        "-2": q13(Fraction(5, 6), Fraction(1, 6)),
        "2": q13(Fraction(7, 6), Fraction(-1, 6)),
    }
    minimal_polynomial = qsum([qscale(3, qpow(t_star, 2)), qneg(t_star), q13(-1)])
    q4_exact = qsum([qpow(value, 4) for value in sigmas.values()])
    check("t_star_minimal_polynomial", minimal_polynomial == q13())
    check("q4_exact", q4_exact == q13(Fraction(356, 27), Fraction(25, 27)))

    one = q13(1)
    direct_det = qsub(qmul(qadd(one, t_star), qsub(q13(4), t_star)), q13(6))
    polynomial_det = qsum([q13(-2), qscale(3, t_star), qneg(qpow(t_star, 2))])
    witness = packet["source_freeze_base_change"]["witness"]
    check("grassmann_base_change", direct_det == polynomial_det)
    check("grassmann_packet_value", witness["grassmann_direct_at_t_star"] == qpayload(direct_det))

    c00 = qadd(q13(3), t_star)
    c11 = qsub(q13(4), t_star)
    det_c = qsub(qmul(c00, c11), one)
    bcb = qsum(
        [
            qdiv(c11, det_c),
            qscale(-2, qdiv(t_star, det_c)),
            qdiv(qmul(qpow(t_star, 2), c00), det_c),
        ]
    )
    schur_direct = qsub(qadd(q13(2), t_star), bcb)
    t2 = qpow(t_star, 2)
    t3 = qpow(t_star, 3)
    det_formula = qsum([q13(11), t_star, qneg(t2)])
    numerator = qsum([q13(4), qscale(-3, t_star), qscale(3, t2), t3])
    schur_formula = qsub(qadd(q13(2), t_star), qdiv(numerator, det_formula))
    check("schur_base_change", schur_direct == schur_formula)
    check("schur_packet_value", witness["schur_direct_at_t_star"] == qpayload(schur_direct))
    check("high_block_invertible", det_c != q13())

    with localcontext() as context:
        context.prec = 90
        sqrt13 = Decimal(13).sqrt()
        sigma_dec = {
            "-4": (Decimal(2) + sqrt13) / Decimal(3),
            "-2": (Decimal(5) + sqrt13) / Decimal(6),
            "2": (Decimal(7) - sqrt13) / Decimal(6),
        }
        q4 = sum(value**4 for value in sigma_dec.values())
        l4 = sum(value**4 * (value * value).ln() for value in sigma_dec.values())
        tau = Decimal(448).ln() / Decimal(15)
        radial_ratio = (Decimal(3106) + Decimal(4) * sqrt13) / Decimal(4393)
        h_ref = (radial_ratio / tau).sqrt()
        mu = Decimal("2.375")
        c_scheme = Decimal("0.625")
        kappa = Decimal("0.073")
        l_h = q4 * (h_ref * h_ref / (mu * mu)).ln() + l4 - c_scheme * q4
        delta_omega = kappa * q4 * h_ref**4 / Decimal(2)
        delta_m2 = -Decimal(2) * kappa * q4 * h_ref**2
        delta_lambda = kappa * (l_h + Decimal("1.5") * q4)

        def raw(h: Decimal) -> Decimal:
            return -kappa * h**4 * (
                q4 * (h * h / (mu * mu)).ln() + l4 - c_scheme * q4
            )

        def corrected(h: Decimal) -> Decimal:
            return raw(h) + delta_omega + delta_m2 * h * h + delta_lambda * h**4

        def universal(h: Decimal) -> Decimal:
            return kappa * q4 * (
                h**4 * ((h_ref * h_ref / (h * h)).ln() + Decimal("1.5"))
                - Decimal(2) * h_ref * h_ref * h * h
                + h_ref**4 / Decimal(2)
            )

        comparison_residual = max(
            abs(corrected(x * h_ref) - universal(x * h_ref))
            for x in (Decimal("0.2"), Decimal("0.67"), Decimal(1), Decimal("1.42"))
        )
        determinant = Decimal(16) * h_ref**3
        kappa_complex = Decimal(1) / (PI * PI)
        kappa_pfaffian = kappa_complex / Decimal(2)

    numeric = packet["numerical_execution"]
    check("q4_decimal", abs(Decimal(numeric["q4_star"]) - q4) < Decimal("1e-75"))
    check("L4_decimal", abs(Decimal(numeric["L4_star"]) - l4) < Decimal("1e-75"))
    check("H_decimal", abs(Decimal(numeric["H_over_Lambda"]) - h_ref) < Decimal("1e-75"))
    check("H_inside_T34_interval", interval_contains(t34["promoted_radial_values"]["h_over_Lambda_interval"], h_ref))
    check("matching_matrix_determinant", abs(Decimal(numeric["matching_matrix_determinant_over_Lambda3"]) - determinant) < Decimal("1e-74"))
    check("independent_scheme_cancellation", comparison_residual < Decimal("1e-80"))
    check("packet_scheme_residual", Decimal(numeric["maximum_scheme_residual"]) < Decimal("1e-70"))
    check("packet_formula_residual", Decimal(numeric["maximum_universal_formula_residual"]) < Decimal("1e-70"))
    check("complex_kappa", abs(Decimal(numeric["determinant_normalization_candidates"]["complex_determinant"]["kappa_F"]) - kappa_complex) < Decimal("1e-75"))
    check("pfaffian_kappa", abs(Decimal(numeric["determinant_normalization_candidates"]["pfaffian_half"]["kappa_F"]) - kappa_pfaffian) < Decimal("1e-75"))

    matching = packet["closure_jet_matching"]
    check("matching_conditions_three", len(matching["conditions"]) == 3)
    check("matching_unique_conditionally", matching["unique_given_conditions"])
    check("matching_not_physically_selected", not matching["selected_by_upper_MTT"])
    check("matching_removes_mu", "mu" in matching["independent_of"])
    check("matching_removes_scheme", "c_scheme" in matching["independent_of"])
    check("matching_removes_branch_log", "L4_*" in matching["independent_of"])
    check("jet_value", matching["jets_at_x_equal_one"]["value"] == 0)
    check("jet_first", matching["jets_at_x_equal_one"]["first"] == 0)
    check("jet_second", matching["jets_at_x_equal_one"]["second"] == 0)
    check("jet_third", matching["jets_at_x_equal_one"]["third"] == -16)
    check("jet_fourth", matching["jets_at_x_equal_one"]["fourth"] == -64)

    check("T31_reextremization_still_scheme_dependent", not t31["renormalization_orbit"]["scheme_independent_stationary_coordinate"])
    check("T30_branch_multiplicity", t30["chiral_finite_operator"]["response_branch_multiplicities"] == {"-2": 16, "-4": 16, "2": 16})
    check("qft_certificate_passes", qft_regulator["all_checks_pass"])
    check("no_internal_projector_promotion", qft_regulator["type_nogo_checks"]["no_existing_internal_object_is_promoted_to_spacetime_cutoff"])

    regulator = packet["regulator_and_RG_boundary"]
    check("finite_base_change_closed", regulator["finite_regulator_base_change_closed"])
    check("external_BV_open", not regulator["selected_external_BV_Laplacian_and_domain"])
    check("global_determinant_open", not regulator["global_Wick_or_direct_Lorentzian_determinant"])
    check("orientation_open", not regulator["determinant_line_orientation_selected"])
    check("matching_scale_survival", regulator["t_star_preserved_at_one_matching_scale"])
    check("RG_fixed_point_open", not regulator["t_star_proved_RG_fixed"])
    check("RG_exit_is_explicit", "beta_t" in regulator["required_RG_exit"])

    check("theorem_states_base_change", "Source freeze and pushforward commute" in theorem)
    check("theorem_states_no_t_equation", "there is no `d_t Gamma=0`" in theorem)
    check("theorem_states_RG_boundary", "beta_t(t_*)=0" in theorem)
    check("theorem_states_unique_matching", "determinant" in theorem and "16 H^3>0" in theorem)
    check("theorem_rejects_physical_promotion", "not promoted to accepted particle masses" in theorem)

    physical = packet["physical_boundary"]
    for key in (
        "closure_jet_matching_rule_selected_by_upper_MTT",
        "selected_external_BV_operator_domain_closed",
        "global_physical_4D_determinant_closed",
        "t_star_RG_invariance_closed",
        "full_renormalized_QFT_vacuum_closed",
        "absolute_scale_closed",
        "sector_generation_map_closed",
        "loop_RG_threshold_pole_transport_closed",
        "held_out_observable_closed",
        "B_ACTION_01_closed",
        "B_QFT_02_closed",
        "B_SM_02_closed",
    ):
        check(f"boundary_{key}_open", not physical[key])
    check("packet_acceptance", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("row_acceptance", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)
    check("no_observed_inputs", packet["parameter_ledger"]["new_observed_construction_inputs"] == 0)
    check("no_fits", packet["parameter_ledger"]["new_fitted_coefficients"] == 0)
    check("no_new_continuous_parameters", packet["parameter_ledger"]["new_continuous_physical_parameters"] == 0)

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T35 independent verification failed: {failed}")
    print(f"verified {PACKET.name}: {len(checks)}/{len(checks)} independent checks passed")


if __name__ == "__main__":
    main()
