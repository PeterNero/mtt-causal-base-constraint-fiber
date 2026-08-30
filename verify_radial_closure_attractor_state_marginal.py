#!/usr/bin/env python3
"""Independently verify the CBF.T38 radial attractor packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
SOURCE_LOCK = ROOT / "radial_closure_attractor_state_marginal_source_lock.json"
SCHEMA = ROOT / "radial_closure_attractor_state_marginal_contract.schema.json"
T33_PACKET = ROOT / "preprojection_finite_source_freeze_radial_values.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
T37_PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"
STATE_CERT = (
    ROOT
    / "../mtt-qm-source-proof/certificates/q79_sm_local_formal_state_space_gluing.certificate.json"
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def q13_mul(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    a, b = left
    c, d = right
    return a * c + 13 * b * d, a * d + b * c


def q13_decimal(value: tuple[Fraction, Fraction], root: Decimal) -> Decimal:
    return (
        Decimal(value[0].numerator) / Decimal(value[0].denominator)
        + Decimal(value[1].numerator)
        / Decimal(value[1].denominator)
        * root
    )


def close(left: Decimal, right: Decimal, tolerance: str = "1e-70") -> bool:
    return abs(left - right) <= Decimal(tolerance)


def verify() -> tuple[int, int, list[str]]:
    packet = load(PACKET)
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    t33 = load(T33_PACKET)
    t34 = load(T34_PACKET)
    t37 = load(T37_PACKET)
    state_cert = load(STATE_CERT)

    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_exists"] = path.is_file()
        checks[f"source_{index:02d}_hash"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )

    checks["packet_schema"] = (
        packet["schema"] == "boe.mtt.radial-closure-attractor-state-marginal.v1"
    )
    checks["packet_claim"] = packet["claim_id"] == "CBF.T38"
    checks["source_lock_claim"] = source_lock["claim_id"] == "CBF.T38"
    checks["required_keys"] = set(schema["required"]).issubset(packet)
    checks["no_extra_top_level_keys"] = set(packet).issubset(
        set(schema["properties"])
    )
    checks["packet_builder_checks_green"] = all(packet["checks"].values())
    checks["packet_builder_summary_green"] = (
        packet["check_summary"]["passed"] == packet["check_summary"]["total"]
        and not packet["check_summary"]["failed"]
    )
    checks["T33_locked"] = t33["claim_id"] == "CBF.T33"
    checks["T34_locked"] = t34["claim_id"] == "CBF.T34"
    checks["T37_locked"] = t37["claim_id"] == "CBF.T37"

    q2 = (Fraction(14, 3), Fraction(1, 3))
    q4 = (Fraction(356, 27), Fraction(25, 27))
    ratio = (Fraction(3106, 4393), Fraction(4, 4393))
    checks["quadratic_field_ratio_identity"] = q13_mul(q4, ratio) == (
        2 * q2[0],
        2 * q2[1],
    )

    with localcontext() as context:
        context.prec = 100
        root = Decimal(13).sqrt()
        q2_d = q13_decimal(q2, root)
        q4_d = q13_decimal(q4, root)
        ratio_d = q13_decimal(ratio, root)
        c_d = Decimal(15) / Decimal(448).ln()
        h2 = ratio_d * c_d
        h = h2.sqrt()
        rate = Decimal(8) * q4_d * h2
        minimum = -q4_d * h2**2

        square = packet["exact_radial_square_completion"]
        checks["q2_decimal"] = close(Decimal(square["q2_star"]["decimal"]), q2_d)
        checks["q4_decimal"] = close(Decimal(square["q4_star"]["decimal"]), q4_d)
        checks["ratio_decimal"] = close(Decimal(square["R_star"]["decimal"]), ratio_d)
        checks["c_decimal"] = close(
            Decimal(square["c_over_Lambda_squared_decimal"]), c_d
        )
        checks["H2_decimal"] = close(
            Decimal(square["H_squared_over_Lambda_squared_decimal"]), h2
        )
        checks["H_decimal"] = close(
            Decimal(square["H_over_Lambda_decimal"]), h
        )
        checks["minimum_decimal"] = close(
            Decimal(square["minimum_over_Lambda4"]), minimum
        )
        checks["q4_positive"] = q4_d > 0
        checks["H_positive"] = h > 0
        checks["square_completion_string"] = (
            square["exact_completion"]
            == "P_*(h)-P_*(H)=q4_* (h^2-H^2)^2"
        )

        x_values = [Decimal("0"), Decimal("0.4"), Decimal("1"), Decimal("2.5")]
        completion_residuals = []
        for x in x_values:
            p_x = q4_d * x**4 - Decimal(4) * c_d * q2_d * x**2
            p_h = minimum
            square_x = q4_d * (x**2 - h2) ** 2
            completion_residuals.append(abs((p_x - p_h) - square_x))
        checks["square_completion_numeric_samples"] = max(completion_residuals) < Decimal(
            "1e-85"
        )

        def u_flow(u0: Decimal, s: Decimal) -> Decimal:
            if u0 == h2:
                return h2
            return h2 / (
                Decimal(1)
                + (h2 / u0 - Decimal(1)) * (-rate * s).exp()
            )

        flow = packet["nonlinear_repair_flow"]
        checks["rate_decimal"] = close(
            Decimal(flow["linear_convergence_rate_over_Lambda2"]), rate
        )
        checks["zero_linearization"] = close(
            Decimal(flow["zero_branch_linearization"]), rate / Decimal(2)
        )
        checks["H_linearization"] = close(
            Decimal(flow["positive_branch_linearization"]), -rate
        )
        checks["zero_unstable"] = flow["zero_branch_is_unstable"]
        checks["H_stable"] = flow["positive_branch_is_strictly_stable"]

        s_eval = Decimal(flow["sample_repair_parameter"])
        sample_residuals = []
        for sample in flow["flow_samples"]:
            ratio0 = Decimal(sample["h0_over_H"])
            predicted = (u_flow(h2 * ratio0**2, s_eval) / h2).sqrt()
            recorded = Decimal(sample["h_at_s_over_H"])
            sample_residuals.append(abs(predicted - recorded))
        checks["flow_samples_reconstructed"] = max(sample_residuals) < Decimal(
            "1e-75"
        )

        u0 = h2 * Decimal("2.25")
        direct = u_flow(u0, Decimal("0.18"))
        composed = u_flow(u_flow(u0, Decimal("0.07")), Decimal("0.11"))
        checks["flow_semigroup_reconstructed"] = abs(direct - composed) < Decimal(
            "1e-85"
        )
        checks["positive_basin_convergence"] = all(
            abs((u_flow(h2 * ratio0**2, Decimal("0.3")) / h2).sqrt() - 1)
            < abs(ratio0 - 1)
            for ratio0 in (
                Decimal("0.25"),
                Decimal("0.5"),
                Decimal("2"),
                Decimal("4"),
            )
        )

    invariant = packet["invariant_radial_state"]
    points = [Fraction(value) for value in invariant["finite_support_points_over_H"]]
    defects = [(value**2 - 1) ** 2 for value in points]
    checks["finite_defect_values"] = [
        str(value) if value.denominator != 1 else str(value.numerator)
        for value in defects
    ] == invariant["dimensionless_defect_values"]
    checks["zero_defect_weight_is_unique"] = (
        invariant["unique_zero_defect_probability_weights"] == ["0", "1", "0"]
    )
    checks["invariant_state_is_delta_H"] = "delta_H" in invariant[
        "invariant_state_theorem"
    ]
    checks["GNS_support_forces_H"] = (
        invariant["positive_radial_support_then_forces"] == "supp(nu_omega)={H}"
    )
    checks["radial_expectation_forced"] = (
        invariant["forced_radial_expectation"] == "omega(h)=H"
    )
    checks["sample_measure_contracts"] = invariant["sample_mean_moves_toward_H"]

    state = packet["formal_q79_state_extension"]
    rho_trace = Fraction(2, 3) + Fraction(1, 3)
    independent_square = Fraction(2, 3) * Fraction(10, 9) + Fraction(
        1, 3
    ) * Fraction(17, 4)
    checks["finite_density_normalized"] = rho_trace == 1
    checks["finite_square_expectation"] = (
        Fraction(state["finite_test_square_expectation"]) == independent_square
        == Fraction(233, 108)
    )
    checks["finite_square_positive"] = independent_square > 0
    checks["q79_state_certificate_green"] = state_cert["all_checks_pass"]
    checks["q79_nonempty_state_space"] = (
        "nonempty local formal physical state spaces"
        in state_cert["claim_boundary"]["closed"]
    )
    checks["q79_preferred_state_open"] = (
        "one preferred or natural q79 state"
        in state_cert["claim_boundary"]["open"]
    )
    checks["formal_extension_exists"] = state[
        "formal_local_radial_anchored_state_exists"
    ]
    checks["full_state_not_claimed_unique"] = not state[
        "full_interacting_state_is_unique"
    ]

    naturality = packet["repair_semiflow_projection_naturality"]
    checks["finite_projection_intertwines"] = naturality[
        "finite_witness_intertwines"
    ] and Decimal(naturality["maximum_projection_commutator_residual"]) == 0
    checks["QJ1_semiflow_corollary"] = naturality[
        "QJ1_follows_from_physical_semiflow_intertwiner"
    ]
    checks["generic_pushforward_not_promoted"] = naturality[
        "generic_action_pushforward_is_not_sufficient"
    ]
    checks["physical_intertwiner_open"] = not naturality[
        "physical_q79_BV_semiflow_intertwiner_present"
    ]

    defect = packet["T35_quantum_intertwining_defect"]
    t37_defect = t37["T35_tadpole_execution"]
    checks["T35_normalized_defect_matches"] = (
        defect["lower_bare_tadpole_over_kappa_Lambda3"]
        == t37_defect["bare_tadpole_over_kappa_Lambda3"]
    )
    checks["T35_complex_defect_matches"] = (
        defect["lower_complex_determinant_tadpole_over_Lambda3"]
        == t37_defect["bare_tadpole_complex_over_Lambda3"]
    )
    checks["T35_pfaffian_defect_matches"] = (
        defect["lower_pfaffian_tadpole_over_Lambda3"]
        == t37_defect["bare_tadpole_pfaffian_over_Lambda3"]
    )
    checks["T35_defect_nonzero"] = (
        Decimal(defect["lower_bare_tadpole_over_kappa_Lambda3"]) != 0
    )
    checks["T35_does_not_intertwine"] = not defect[
        "bare_truncated_projection_intertwines_T34_flow"
    ]
    checks["counterterm_not_selected"] = not defect[
        "QJ1_counterterm_line_selected_by_current_upper_action"
    ]

    boundary = packet["physical_boundary"]
    checks["radial_attractor_closed"] = boundary[
        "T34_positive_radial_attractor_closed"
    ]
    checks["radial_state_closed"] = boundary[
        "T34_unique_invariant_radial_state_closed"
    ]
    checks["formal_q79_extension_closed"] = boundary[
        "formal_local_q79_radial_state_extension_closed"
    ]
    checks["physical_QJ1_open"] = not boundary["physical_QJ1_selected"]
    checks["physical_QJ2_open"] = not boundary["physical_QJ2_selected"]
    checks["physical_QJ0_open"] = not boundary["physical_QJ0_selected"]
    checks["physical_endpoint_open"] = not boundary["physical_endpoint_promoted"]
    checks["repair_not_called_time"] = not boundary[
        "repair_parameter_identified_with_physical_time"
    ]

    ledger = packet["parameter_ledger"]
    checks["no_new_continuous_parameter"] = ledger["new_continuous_parameters"] == 0
    checks["no_new_discrete_choice"] = ledger["new_discrete_choices"] == 0
    checks["no_observed_values"] = not ledger["observed_values_used"]
    checks["no_fitted_values"] = not ledger["fitted_values_used"]
    checks["matter_state_nonunique"] = ledger[
        "matter_gauge_state_family_remains_nonunique"
    ]
    checks["renormalization_choice_remains"] = not ledger[
        "renormalization_choice_removed"
    ]

    checks["packet_counter_0_of_3"] = (
        packet["physical_packets_accepted"] == 0
        and packet["physical_packets_total"] == 3
    )
    checks["row_counter_0_of_7"] = (
        packet["physical_rows_accepted"] == 0
        and packet["physical_rows_total"] == 7
    )
    root_payload = packet["source_provenance"]["source_root_payload"]
    checks["source_root_hash"] = canonical_hash(root_payload) == packet[
        "source_provenance"
    ]["source_root_sha256"]
    checks["source_count"] = packet["source_provenance"]["source_count"] == len(
        source_lock["local_sources"]
    )
    checks["all_sources_green"] = packet["source_provenance"][
        "all_source_hashes_match"
    ]

    failed = [name for name, passed in checks.items() if not passed]
    return len(checks) - len(failed), len(checks), failed


def main() -> None:
    passed, total, failed = verify()
    if failed:
        raise SystemExit(f"independent verification failed: {failed}")
    print(
        f"verified {PACKET.name}: {passed}/{total} independent checks passed"
    )


if __name__ == "__main__":
    main()
