#!/usr/bin/env python3
"""Independent verifier for the CBF.T48 radial-Higgs packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "selected_radial_higgs_future_state.packet.json"
SOURCE_LOCK = ROOT / "selected_radial_higgs_future_state_source_lock.json"
SCHEMA = ROOT / "selected_radial_higgs_future_state_contract.schema.json"
THEOREM = ROOT / "SelectedRadialHiggsFutureStateAndCompleteFreeSeedTheorem_v1.md"

T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
T45_PACKET = ROOT / "future_cone_spectral_polarization.packet.json"
T46_PACKET = ROOT / "selected_future_state_moller_bv_transport.packet.json"
T47_PACKET = ROOT / "selected_gauge_physical_future_state.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T40_PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"

Q = tuple[Fraction, Fraction]
Matrix = list[list[Fraction]]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def parse_matrix(matrix: list[list[str]]) -> Matrix:
    return [[parse_fraction(entry) for entry in row] for row in matrix]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matscale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def determinant_2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [entry - factor * pivot_entry for entry, pivot_entry in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def q(value: int | Fraction, radical: int | Fraction = 0) -> Q:
    return Fraction(value), Fraction(radical)


def qadd(left: Q, right: Q) -> Q:
    return left[0] + right[0], left[1] + right[1]


def qneg(value: Q) -> Q:
    return -value[0], -value[1]


def qsub(left: Q, right: Q) -> Q:
    return qadd(left, qneg(right))


def qmul(left: Q, right: Q) -> Q:
    return left[0] * right[0] + 13 * left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def qscale(value: int | Fraction, item: Q) -> Q:
    return Fraction(value) * item[0], Fraction(value) * item[1]


def qinverse(value: Q) -> Q:
    norm = value[0] * value[0] - 13 * value[1] * value[1]
    return value[0] / norm, -value[1] / norm


def qdivide(left: Q, right: Q) -> Q:
    return qmul(left, qinverse(right))


def qpow(value: Q, exponent: int) -> Q:
    result = q(1)
    for _ in range(exponent):
        result = qmul(result, value)
    return result


def qdecimal(value: Q) -> Decimal:
    return Decimal(value[0].numerator) / Decimal(value[0].denominator) + (
        Decimal(value[1].numerator) / Decimal(value[1].denominator)
    ) * Decimal(13).sqrt()


def q_from_packet(item: dict[str, str]) -> Q:
    return Fraction(item["rational"]), Fraction(item["sqrt13_coefficient"])


def main() -> None:
    getcontext().prec = 80
    packet = load_json(PACKET)
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    theorem_text = THEOREM.read_text(encoding="utf-8")
    t23 = load_json(T23_PACKET)
    t34 = load_json(T34_PACKET)
    t45 = load_json(T45_PACKET)
    t46 = load_json(T46_PACKET)
    t47 = load_json(T47_PACKET)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    t40 = load_json(T40_PACKET)

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("packet_exists", PACKET.is_file())
    check("source_lock_exists", SOURCE_LOCK.is_file())
    check("schema_exists", SCHEMA.is_file())
    check("theorem_exists", THEOREM.is_file())
    check("packet_schema", packet["schema"] == "boe.mtt.selected-radial-higgs-future-state.v1")
    check("packet_claim", packet["claim_id"] == "CBF.T48")
    check("packet_date", packet["date"] == "2026-08-30")
    check("source_lock_schema", source_lock["schema"] == "boe.mtt.selected-radial-higgs-future-state-source-lock.v1")
    check("source_lock_claim", source_lock["claim_id"] == "CBF.T48")
    check("schema_claim", schema["properties"]["claim_id"]["const"] == "CBF.T48")
    check("schema_packet", schema["properties"]["schema"]["const"] == packet["schema"])
    check("source_lock_hash", packet["source_provenance"]["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("contract_hash", packet["source_provenance"]["contract_sha256"] == sha256(SCHEMA))
    check("handoff_id", packet["source_provenance"]["handoff_id"] == "c458f2b0-f8e3-4e61-8f94-c5e65d8c207f")
    check("kernel_hash", packet["source_provenance"]["kernel_model_sha256"] == "592ef16dc03ce2195113b53cc75f8bb638bd27c279590ed3f5575d11dee05db8")

    for index, source in enumerate(source_lock["construction_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        check(f"construction_{index:02d}_exists", path.is_file())
        check(f"construction_{index:02d}_hash", path.is_file() and sha256(path) == source["sha256"])
    for index, source in enumerate(source_lock["comparison_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        check(f"comparison_{index:02d}_exists", path.is_file())
        check(f"comparison_{index:02d}_hash", path.is_file() and sha256(path) == source["sha256"])

    required = set(schema["required"])
    check("all_required_keys", required.issubset(packet))
    for key in sorted(required):
        check(f"required_key_{key}", key in packet)

    t_star = q(Fraction(1, 6), Fraction(-1, 6))
    q2 = qadd(qsub(q(3), qscale(4, t_star)), qscale(6, qpow(t_star, 2)))
    q4 = qadd(
        qsub(qadd(qsub(q(3), qscale(8, t_star)), qscale(36, qpow(t_star, 2))), qscale(32, qpow(t_star, 3))),
        qscale(18, qpow(t_star, 4)),
    )
    radial_ratio = qdivide(qscale(2, q2), q4)
    expected_q2 = q(Fraction(14, 3), Fraction(1, 3))
    expected_q4 = q(Fraction(356, 27), Fraction(25, 27))
    expected_ratio = q(Fraction(3106, 4393), Fraction(4, 4393))

    check("exact_t_star", q_from_packet(packet["exact_radial_action"]["t_star"]) == t_star)
    check("exact_q2", q2 == expected_q2)
    check("exact_q4", q4 == expected_q4)
    check("exact_R", radial_ratio == expected_ratio)
    check("packet_q2", q_from_packet(packet["exact_radial_action"]["q2_star"]) == q2)
    check("packet_q4", q_from_packet(packet["exact_radial_action"]["q4_star"]) == q4)
    check("packet_R", q_from_packet(packet["exact_radial_action"]["R_star_equals_2q2_over_q4"]) == radial_ratio)
    check("positive_q2", qdecimal(q2) > 0)
    check("positive_q4", qdecimal(q4) > 0)
    check("positive_R", qdecimal(radial_ratio) > 0)

    stationarity = qscale(4, qsub(qmul(radial_ratio, q4), qscale(2, q2)))
    hessian_over_c = qsub(qscale(12, qmul(q4, radial_ratio)), qscale(8, q2))
    mass_over_c = qdivide(hessian_over_c, qscale(2, q2))
    square_h2 = qscale(-2, qmul(q4, radial_ratio))
    check("stationarity_exact", stationarity == q(0))
    check("hessian_exact", hessian_over_c == qscale(16, q2))
    check("quadratic_coefficient_exact", qscale(Fraction(1, 2), hessian_over_c) == qscale(8, q2))
    check("mass_eight_c", mass_over_c == q(8))
    check("square_completion_h2", square_h2 == qscale(-4, q2))
    check("positive_hessian", qdecimal(hessian_over_c) > 0)
    check("square_completion_recorded", packet["exact_radial_action"]["exact_square_completion"] == "P_*(h)-P_*(H_*)=q4_*(h^2-H_*^2)^2")
    check("first_derivative_zero", packet["exact_radial_action"]["derivatives_at_H_star"]["first"] == "0")
    check("second_derivative", packet["exact_radial_action"]["derivatives_at_H_star"]["second"] == "16c q2_*")
    check("third_derivative", packet["exact_radial_action"]["derivatives_at_H_star"]["third"] == "24q4_* H_*")
    check("fourth_derivative", packet["exact_radial_action"]["derivatives_at_H_star"]["fourth"] == "24q4_*")

    log448 = Decimal(448).ln()
    tau = log448 / Decimal(15)
    c_over_lambda2 = Decimal(15) / log448
    mass2_over_lambda2 = Decimal(120) / log448
    mass_over_lambda = mass2_over_lambda2.sqrt()
    check("positive_tau", tau > 0)
    check("positive_c", c_over_lambda2 > 0)
    check("positive_mass2", mass2_over_lambda2 > 0)
    check("positive_mass", mass_over_lambda > 0)
    check("checkpoint_identity", abs(tau * mass2_over_lambda2 - Decimal(8)) < Decimal("1e-70"))
    check("packet_mass_formula", packet["canonical_radial_hessian"]["mass_squared_over_Lambda_squared"] == "120/log(448)")
    check("packet_mass_decimal", abs(Decimal(packet["canonical_radial_hessian"]["mass_over_Lambda_decimal"]) - mass_over_lambda) < Decimal("1e-29"))
    check("mass_interval", Decimal("4.433586065447802232784618009020") <= mass_over_lambda <= Decimal("4.433586065447802232784618009021"))
    check("mass_not_pole_claim", packet["canonical_radial_hessian"]["physical_pole_mass_claimed"] is False)
    check("absolute_normalization_open", packet["canonical_radial_hessian"]["absolute_field_normalization_selected"] is False)

    oscillator = packet["oscillator_witness"]
    symplectic = parse_matrix(oscillator["symplectic_form"])
    complex_structure = parse_matrix(oscillator["future_complex_structure"])
    positive_metric = parse_matrix(oscillator["positive_metric_SJ"])
    covariance = parse_matrix(oscillator["pure_covariance_one_half_SJ"])
    evolution = parse_matrix(oscillator["rational_time_evolution_cos_3_5_sin_4_5"])
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    check("oscillator_frequency", oscillator["frequency"] == "5")
    check("J_squared", matmul(complex_structure, complex_structure) == matscale(Fraction(-1), identity))
    check("J_symplectic", matmul(matmul(transpose(complex_structure), symplectic), complex_structure) == symplectic)
    check("SJ_recomputed", matmul(symplectic, complex_structure) == positive_metric)
    check("SJ_positive", positive_metric == [[Fraction(5), Fraction(0)], [Fraction(0), Fraction(1, 5)]])
    check("covariance_half_SJ", covariance == matscale(Fraction(1, 2), positive_metric))
    check("covariance_pure", 4 * determinant_2(covariance) == 1)
    check("evolution_symplectic", matmul(matmul(transpose(evolution), symplectic), evolution) == symplectic)
    check("evolution_covariance", matmul(matmul(transpose(evolution), covariance), evolution) == covariance)
    check("evolution_J", matmul(evolution, complex_structure) == matmul(complex_structure, evolution))

    os_data = packet["gaussian_reflection_positivity"]
    os_witness = os_data["finite_exact_witness"]
    os_gram = parse_matrix(os_witness["OS_gram"])
    laplace = [parse_fraction(value) for value in os_witness["positive_laplace_factors"]]
    coefficients = [parse_fraction(value) for value in os_witness["test_coefficients"]]
    expected_gram = [[left * right / 10 for right in laplace] for left in laplace]
    pairing = sum((coefficient * factor for coefficient, factor in zip(coefficients, laplace)), Fraction(0))
    expected_quadratic = pairing * pairing / 10
    check("OS_gram_exact", os_gram == expected_gram)
    check("OS_gram_symmetric", os_gram == transpose(os_gram))
    check("OS_gram_rank_one", rank(os_gram) == 1)
    check("OS_first_minor_positive", os_gram[0][0] > 0)
    check("OS_second_minor_zero", determinant_2([row[:2] for row in os_gram[:2]]) == 0)
    check("OS_quadratic_exact", parse_fraction(os_witness["test_quadratic_form"]) == expected_quadratic == Fraction(1, 10))
    check("OS_proved_nonnegative", os_data["proved_nonnegative"] is True)
    check("OS_future_phase", os_witness["future_phase_sample"] == {"real": "3/5", "imaginary": "-4/5"})
    check("OS_past_phase", os_witness["past_phase_sample"] == {"real": "3/5", "imaginary": "4/5"})
    check("OS_non_linear_not_claimed", os_data["nonlinear_interacting_reconstruction_claimed"] is False)

    check("T23_one_Higgs", t23["one_higgs_gauge_covariance"]["selected_Higgs_representation"] == "(1,2,+1/2)")
    check("T23_operator", t23["lorentzian_product_and_scale"]["operator"] == packet["same_branch_source"]["radial_coordinate"].replace("h in ", ""))
    check("T34_same_root", t34["checks"]["same_root_diagram_is_newly_closed"] is True)
    check("T34_moment", t34["spectral_moments"]["at_tau_f2_over_f0"] == "15/log(448)")
    check("T34_mass", t34["promoted_radial_values"]["radial_curvature_mass_squared_over_Lambda_squared"] == "120/log(448)")
    check("T45_future", t45["quasifree_initial_state"]["selected_free_initial_state_on_declared_branch"] is True)
    check("T45_inherits_T34", "T34/T43" in t45["flat_direct_branch"]["radial_scale"])
    check("T46_lift", t46["canonical_BRST_lift"]["recursive_lift"] == packet["canonical_formal_lift"]["recursion"])
    check("T47_one_missing", t47["broken_phase_seed_factorization"]["missing_selected_factors"] == 1)
    check("T47_gauge_27", t47["BRST_mode_reduction"]["total_physical_gauge_polarizations"] == 27)
    check("T38_not_full_state", t38["physical_boundary"]["preferred_full_q79_state_selected"] is False)
    check("T39_upper_action_open", t39["physical_boundary"]["pointed_anchor_scheme_selected_by_upper_action"] is False)
    check("T40_G1_open", t40["physical_boundary"]["physical_tangent_pairing_gate_closed"] is False)

    state = packet["future_positive_CCR_state"]
    check("state_positive", state["positive"] is True)
    check("state_normalized", state["normalized"] is True)
    check("state_pure", state["pure"] is True)
    check("state_Hadamard", state["Hadamard_on_static_flat_branch"] is True)
    check("state_no_selector", state["new_state_parameter_count"] == 0)
    check("state_no_zero_mode", state["p_zero_selector_required"] is False)
    check("state_strict_gap", state["strict_gap"] == "Omega_h>=m_h>0")

    separation = packet["type_separation"]
    check("delta_not_covariance", separation["T38_used_as_fluctuation_covariance"] is False)
    check("t_not_particle", separation["source_modulus_t_varied_as_particle"] is False)
    check("Goldstones_not_radial", separation["Goldstones_counted_as_radial_particles"] is False)
    check("T40_preserved", "remains open" in separation["T40_G1_role"])

    seed = packet["complete_free_seed"]
    check("seed_Weyl", seed["Weyl_factor"]["selected"] is True)
    check("seed_gauge", seed["gauge_physical_factor"]["selected"] is True)
    check("seed_radial", seed["radial_Higgs_factor"]["selected"] is True)
    check("seed_gauge_modes", seed["gauge_physical_factor"]["physical_polarizations"] == 27)
    check("seed_radial_modes", seed["radial_Higgs_factor"]["physical_polarizations"] == 1)
    check("seed_bosonic_total", seed["total_bosonic_physical_polarizations"] == 28)
    check("seed_no_missing", seed["missing_selected_factors"] == 0)
    check("seed_selected", seed["full_product_seed_selected_at_declared_tier"] is True)
    check("seed_positive", seed["positive"] is True)
    check("seed_normalized", seed["normalized"] is True)
    check("seed_pure", seed["pure"] is True)
    check("seed_Hadamard", seed["componentwise_Hadamard"] is True)

    lift = packet["canonical_formal_lift"]
    check("lift_premise", lift["complete_seed_premise_now_met"] is True)
    check("lift_choice_removed", lift["formal_lift_choice_removed"] is True)
    check("lift_upper_action_open", lift["upper_action_selected_full_BV_map"] is False)
    check("lift_fixed_coupling_open", lift["fixed_coupling_positive_state"] is False)

    ledger = packet["G2_clause_ledger"]
    check("ledger_radial_closed", ledger["G2a_flat_branch_free_radial_Higgs_state"] == "closed by T48")
    check("ledger_seed_closed", "closed by T48" in ledger["G2b_selected_complete_free_product_seed"])
    check("ledger_upper_action_open", ledger["G2b_selected_upper_action_and_full_BV_map"] == "open")
    check("ledger_continuum_open", ledger["G2c_selected_regulator_independent_continuum"] == "open 0/9")
    check("ledger_top_G2_open", ledger["top_level_physical_G2"] == "open")
    check("ledger_gate_count", ledger["physical_T41_gate_count"] == "0/3")

    parameters = packet["parameter_ledger"]
    check("zero_observed", parameters["new_observed_inputs"] == 0)
    check("zero_fits", parameters["new_fitted_parameters"] == 0)
    check("zero_continuous_selectors", parameters["new_continuous_state_selectors"] == 0)
    check("zero_discrete_selectors", parameters["new_discrete_state_selectors"] == 0)
    check("Lambda_open", parameters["inherited_unresolved_absolute_scale"] == "Lambda")
    check("action_amplitude_open", parameters["inherited_unresolved_scalar_action_amplitude"] == "A_H>0")

    boundary = packet["physical_boundary"]
    check("physical_gates", boundary["physical_gates_accepted"] == 0 and boundary["physical_gates_total"] == 3)
    check("physical_packets", boundary["physical_packets_accepted"] == 0 and boundary["physical_packets_total"] == 3)
    check("physical_rows", boundary["physical_rows_accepted"] == 0 and boundary["physical_rows_total"] == 7)
    check("open_upper_action_listed", any("upper-action" in item for item in boundary["open"]))
    check("open_G1_listed", any("G1" in item for item in boundary["open"]))
    check("closed_seed_listed", any("complete corrected" in item for item in boundary["closed"]))

    check("theorem_claim", "**Claim ID:** `CBF.T48`" in theorem_text)
    check("theorem_square_completion", "P_*(h)-P_*(H_*)=q4_* (h^2-H_*^2)^2" in theorem_text)
    check("theorem_mass", "m_h^2/Lambda^2=120/log(448)>0" in theorem_text)
    check("theorem_OS_square", "<theta f,C_E f>" in theorem_text)
    check("theorem_seed", "omega_0,H_*" in theorem_text)
    check("theorem_T38_separation", "T38 is not used as the fluctuation state" in theorem_text)
    check("theorem_G1_open", "T40 `G1` is not silently closed" in theorem_text)
    check("theorem_counters", "physical gates:   0/3" in theorem_text)
    check("theorem_no_pole_claim", "observed Higgs mass, VEV, pole mass" in theorem_text)

    packet_checks = packet["checks"]
    check("builder_checks_nonempty", len(packet_checks) >= 90)
    check("builder_checks_all_true", all(packet_checks.values()))
    check("builder_summary_no_failures", packet["check_summary"]["failed"] == [])
    check("builder_summary_total", packet["check_summary"]["total"] == len(packet_checks))
    check("builder_summary_passed", packet["check_summary"]["passed"] == len(packet_checks))

    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        for name in failed:
            print(f"FAIL {name}")
        raise SystemExit(f"CBF.T48 independent verification failed {len(failed)}/{len(checks)} checks")
    print(f"CBF.T48 independent verification passed {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
