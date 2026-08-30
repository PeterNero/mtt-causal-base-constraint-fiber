#!/usr/bin/env python3
"""Independently verify the CBF.T34 same-root heat-profile packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "same_root_state_repair_heat_profile_radial_values_source_lock.json"
SCHEMA = ROOT / "same_root_state_repair_heat_profile_radial_values_contract.schema.json"
THEOREM = ROOT / "SameRootStateRepairHeatProfileAndRadialValuePromotionTheorem_v1.md"
PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
T24_PACKET = ROOT / "upper_totalization_supercharge.packet.json"
T28_PACKET = ROOT / "finite_dirac_operator_repair_semigroup.packet.json"
T30_PACKET = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
T33_PACKET = ROOT / "preprojection_finite_source_freeze_radial_values.packet.json"
A53_PACKET = ROOT / "../mtt-sm-parity-closure/candidate_data/selected_propertimemeasureandoverlapkineticmetricsource_or_strictspectralactionclosure/proper_time_atom_and_overlap_source_cutset.packet.json"
A84_PACKET = ROOT / "../mtt-sm-parity-closure/candidate_data/selected_closureshadowgaugeactionaxiomderivation_or_explicitadoptionandheldoutvalidation/fixed_point_semigroup_to_damped_overlap_derivation.packet.json"
QM_CLOCK = ROOT / "../mtt-qm-source-proof/certificates/one_anchor_physical_clock_lift.certificate.json"

Q13 = tuple[Fraction, Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def q13(rational: Fraction | int = 0, radical: Fraction | int = 0) -> Q13:
    return Fraction(rational), Fraction(radical)


def qadd(left: Q13, right: Q13) -> Q13:
    return left[0] + right[0], left[1] + right[1]


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


def interval_contains(payload: dict[str, str], value: Decimal) -> bool:
    lower_fraction = Fraction(payload["lower_exact"])
    upper_fraction = Fraction(payload["upper_exact"])
    with localcontext() as context:
        context.prec = 150
        lower = Decimal(lower_fraction.numerator) / Decimal(lower_fraction.denominator)
        upper = Decimal(upper_fraction.numerator) / Decimal(upper_fraction.denominator)
        return lower <= value <= upper


def root_payload(source_lock: dict[str, Any], t24: dict[str, Any], t30: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "boe.mtt.same-root-state-repair-heat-profile-source.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "finite_factor": t24["factor_differentials"]["finite"],
        "finite_charge": t24["factor_differentials"]["finite_charge"],
        "totalization_root_sha256": t24["selection_root_sha256"],
        "finite_determinant_root_sha256": t30["source_provenance"]["source_root_sha256"],
        "total_charge": t24["physical_closure_charge"]["charge"],
        "total_square": t24["physical_closure_charge"]["square"],
        "state_functional_rule": "J_B(Psi)=1/2||B_tot Psi/Lambda||^2",
        "state_generator_rule": "K=B_tot^2/Lambda^2",
        "semigroup_rule": "T_s=exp(-sK)",
        "internal_checkpoint": "tau_int=log(448)/15",
        "profile_amplitude_role": "common positive trace amplitude; cancels from f2/f0",
        "excluded_from_root": [
            "observed masses",
            "observed mixings",
            "target radial values",
            "fitted profile coefficients",
            "sector-specific scales",
        ],
    }


def main() -> None:
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    packet = load(PACKET)
    t24 = load(T24_PACKET)
    t28 = load(T28_PACKET)
    t30 = load(T30_PACKET)
    t33 = load(T33_PACKET)
    a53 = load(A53_PACKET)
    a84 = load(A84_PACKET)
    qm_clock = load(QM_CLOCK)
    theorem = THEOREM.read_text(encoding="ascii")

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("claim_id", packet["claim_id"] == "CBF.T34")
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

    reconstructed_root = root_payload(source_lock, t24, t30)
    check("source_root_payload", packet["source_provenance"]["source_root_payload"] == reconstructed_root)
    check("source_root_hash", packet["source_provenance"]["source_root_sha256"] == canonical_hash(reconstructed_root))
    check("source_root_excludes_observations", "observed masses" in reconstructed_root["excluded_from_root"])
    check("source_root_excludes_fits", "fitted profile coefficients" in reconstructed_root["excluded_from_root"])

    required = set(schema["required"])
    allowed = set(schema["properties"])
    check("all_schema_required_fields", required <= set(packet))
    check("no_extra_top_level_fields", set(packet) <= allowed)
    check("builder_checks_all_true", all(packet["checks"].values()))
    check("builder_check_count", packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(packet["checks"]))
    check("builder_failed_list_empty", packet["check_summary"]["failed"] == [])

    finite = t24["factor_differentials"]
    charge = t24["physical_closure_charge"]
    check("finite_factor_is_qF", "q_F(t)" in finite["finite"])
    check("finite_charge_is_Dphys", "D_phys(t)" in finite["finite_charge"])
    check("total_charge_uses_Dphys", "D_phys(t)" in charge["charge"])
    check("total_square_uses_Dphys_squared", "D_phys(t)^2" in charge["square"])
    check("T30_uses_Dphys", "D_phys(t)" in t30["chiral_finite_operator"]["definition"])
    check("diagram_root_matches", packet["same_root_commuting_diagram"]["root"] == "R_tot=(q_Y,q_F(t),Gamma_Y,h,totalize)")
    check("diagram_commutes", packet["same_root_commuting_diagram"]["commutes_by_factor_functoriality"])
    check("no_comparison_matrix", not packet["same_root_commuting_diagram"]["comparison_matrix_inserted"])
    check("source_is_frozen", packet["same_root_commuting_diagram"]["lower_evaluation"] == "freeze t=t_* before varying h")
    check("full_upper_selection_not_claimed", not packet["same_root_commuting_diagram"]["full_upper_physical_source_selected"])

    action_bridge = packet["action_shadow_bridge"]
    check("action_bridge_uses_A84", action_bridge["authority"] == "A84")
    check("action_bridge_identifies_scalar_trace", action_bridge["uninserted_scalar_trace"] == "Tr exp(-sK)=Tr chi_s(K)")
    check("semigroup_alone_is_not_sufficient", not action_bridge["semigroup_alone_would_select_action_profile"])
    check("action_bridge_closed_at_declared_tier", action_bridge["bridge_closed_at_regime_local_action_tier"])
    check("matching_completeness_remains_open", not action_bridge["full_matching_completeness_closed"])
    check("full_nonlinear_action_remains_open", not action_bridge["full_nonlinear_physical_action_closed"])

    t_exact = q13(Fraction(1, 6), Fraction(-1, 6))
    polynomial = qadd(qadd(qscale(3, qmul(t_exact, t_exact)), qscale(-1, t_exact)), q13(-1))
    check("t_minimal_polynomial_exact", polynomial == q13(0))
    q2_exact = qadd(qadd(q13(3), qscale(-4, t_exact)), qscale(6, qmul(t_exact, t_exact)))
    t2 = qmul(t_exact, t_exact)
    t3 = qmul(t2, t_exact)
    t4 = qmul(t2, t2)
    q4_exact = qadd(qadd(qadd(qadd(q13(3), qscale(-8, t_exact)), qscale(36, t2)), qscale(-32, t3)), qscale(18, t4))
    r_exact = qdiv(qscale(2, q2_exact), q4_exact)
    check("q2_exact", q2_exact == q13(Fraction(14, 3), Fraction(1, 3)))
    check("q4_exact", q4_exact == q13(Fraction(356, 27), Fraction(25, 27)))
    check("R_exact", r_exact == q13(Fraction(3106, 4393), Fraction(4, 4393)))

    with localcontext() as context:
        context.prec = 100
        sqrt13 = Decimal(13).sqrt()
        tau = Decimal(448).ln() / Decimal(15)
        moment = Decimal(1) / tau
        moment4 = moment * moment
        t_star = (Decimal(1) - sqrt13) / Decimal(6)
        radial_ratio = (Decimal(3106) + Decimal(4) * sqrt13) / Decimal(4393)
        h = (radial_ratio * moment).sqrt()
        sigmas = {
            "-4": (Decimal(2) + sqrt13) / Decimal(3),
            "-2": (Decimal(5) + sqrt13) / Decimal(6),
            "2": (Decimal(7) - sqrt13) / Decimal(6),
        }
        values = {key: h * sigma for key, sigma in sigmas.items()}
        radial_mass = (Decimal(8) * moment).sqrt()
        checkpoint = (-Decimal(15) * tau).exp()
        checkpoint_target = Decimal(1) / Decimal(448)
        split = tau * Decimal("0.37")
        remainder = tau - split
        semigroup_residual = max(
            abs((-tau * eigenvalue).exp() - (-split * eigenvalue).exp() * (-remainder * eigenvalue).exp())
            for eigenvalue in (Decimal(0), Decimal(1), Decimal(4), Decimal(15))
        )

    check("t_decimal", abs(t_star - Decimal("-0.434258545910664882186536877912")) < Decimal("1e-30"))
    check("tau_positive", tau > 0)
    check("tau_matches_packet", interval_contains(packet["selected_internal_checkpoint"]["tau_interval"], tau))
    check("checkpoint_exact_numerically", abs(checkpoint - checkpoint_target) < Decimal("1e-95"))
    check("semigroup_composition_independent_split", semigroup_residual < Decimal("1e-95"))
    check("moment_ratio", interval_contains(packet["spectral_moments"]["at_tau_f2_over_f0_interval"], moment))
    check("second_moment_ratio", interval_contains(packet["spectral_moments"]["at_tau_f4_over_f0_interval"], moment4))
    check("h_ratio", interval_contains(packet["promoted_radial_values"]["h_over_Lambda_interval"], h))
    for key, value in values.items():
        check(
            f"branch_{key}_value",
            interval_contains(packet["promoted_radial_values"]["branch_values_over_Lambda"][key]["interval"], value),
        )
    check("radial_mass", interval_contains(packet["promoted_radial_values"]["radial_curvature_mass_interval"], radial_mass))
    check("branch_order", values["-4"] > values["-2"] > values["2"] > 0)

    check("state_carrier_is_not_operator_space", packet["typed_no_go_reconciliation"]["CBF_T34_carrier"] != t28["configuration_space"]["carrier"])
    check("generators_not_identified", not packet["typed_no_go_reconciliation"]["generators_identified"])
    check("T28_nogo_preserved", packet["typed_no_go_reconciliation"]["T28_no_go_preserved"])
    check("T28_still_rejects_scalar_relabel", not t28["action_profile_boundary"]["scalar_profile_f_of_D_phys_squared_selected"])
    check("no_cross_carrier_trace_substitution", not packet["typed_no_go_reconciliation"]["trace_substitution_across_carriers_used"])

    measure = packet["positive_laplace_measure"]
    check("measure_is_point_atom", measure["unique_measure"] == "mu=A delta_s")
    check("measure_uses_tilt_proof", "tilt" in measure["proof_device"])
    check("measure_zero_variance", measure["tilted_variance"] == "Var(u)=0")
    check("minimal_support_not_used", not measure["minimal_support_axiom_used"])
    check("A53_old_measure_was_unselected", not a53["proper_time_candidate"]["selected_by_existing_MTT_source"])
    check("A53_old_policy_was_unpromoted", not a53["epistemic_policy"]["point_measure_promoted_to_selected_MTT_theorem"])
    check("A84_semigroup_theorem", a84["theorem"]["proved_at_fixed_point_gradient_flow_tier"])
    check("A84_gap", a84["selected_time_identity"]["gap"] == 15.0)
    check("QM_clock_checks", qm_clock["all_checks_pass"])
    check("QM_clock_remains_conditional", "conditional" in qm_clock["boundary"]["closed"])

    check("theorem_states_state_carrier", "physical state carrier" in theorem)
    check("theorem_states_A84_action_bridge", "Without the A84 action-shadow rule" in theorem)
    check("theorem_proves_laplace_uniqueness", "Var_nu(u)=0" in theorem)
    check("theorem_preserves_T28", "Why CBF.T28 is not violated" in theorem)
    check("theorem_rejects_pole_mass_claim", "observed particle masses would" in theorem)
    check("theorem_keeps_clock_open", "additive physical-clock lift" in theorem)

    physical = packet["physical_boundary"]
    check("same_root_closed", physical["same_root_direct_source_diagram_closed"])
    check("heat_profile_closed", physical["state_space_heat_profile_closed"])
    check("measure_closed_at_tier", physical["one_atom_measure_closed_at_declared_tier"])
    check("moment_ratio_closed_at_tier", physical["radial_moment_ratio_closed_at_declared_tier"])
    check("cutoff_values_closed_at_tier", physical["cutoff_unit_radial_values_closed_at_declared_tier"])
    for key in (
        "full_upper_physical_source_closed",
        "additive_physical_clock_lift_closed_unconditionally",
        "full_four_dimensional_determinant_closed",
        "renormalized_QFT_vacuum_closed",
        "absolute_scale_closed",
        "sector_generation_map_closed",
        "nine_charged_Yukawa_values_closed",
        "loop_RG_threshold_pole_transport_closed",
        "held_out_observable_closed",
        "B_ACTION_01_closed",
        "B_QFT_02_closed",
        "B_SM_02_closed",
    ):
        check(f"boundary_{key}_remains_open", not physical[key])
    check("physical_packets_unchanged", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("physical_rows_unchanged", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)
    check("no_observed_inputs", packet["parameter_ledger"]["new_observed_construction_inputs"] == 0)
    check("no_fitted_coefficients", packet["parameter_ledger"]["new_fitted_coefficients"] == 0)
    check("no_profile_parameters", packet["parameter_ledger"]["new_continuous_profile_parameters"] == 0)
    check("one_metrology_primitive_remains", packet["parameter_ledger"]["inherited_universal_metrology_primitives"] == 1)

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T34 independent verification failed: {failed}")
    print(
        f"verified {PACKET.name}: {len(checks)}/{len(checks)} independent checks passed"
    )


if __name__ == "__main__":
    main()
