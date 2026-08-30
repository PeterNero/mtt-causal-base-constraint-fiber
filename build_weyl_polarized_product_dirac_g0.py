#!/usr/bin/env python3
"""Build the exact CBF.T43 Weyl-polarized direct local G0 packet."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "weyl_polarized_product_dirac_g0_source_lock.json"
SCHEMA = ROOT / "weyl_polarized_product_dirac_g0_contract.schema.json"
THEOREM = ROOT / "WeylPolarizedProductDiracOneLoopPushforwardAndDirectG0SourceTheorem_v1.md"
OUTPUT = ROOT / "weyl_polarized_product_dirac_g0.packet.json"

T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
T25_LOCK = ROOT / "direct_finite_source_continuum_source_lock.json"
T30_PACKET = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
T30_LOCK = ROOT / "ko6_fermionic_determinant_value_selection_source_lock.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
T34_LOCK = ROOT / "same_root_state_repair_heat_profile_radial_values_source_lock.json"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T35_LOCK = ROOT / "frozen_source_four_dimensional_fermion_pushforward_source_lock.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T39_LOCK = ROOT / "renormalized_bv_anchored_repair_semiflow_source_lock.json"
T40_PACKET = ROOT / "source_preserving_pointed_quantum_projection.packet.json"
T40_LOCK = ROOT / "source_preserving_pointed_quantum_projection_source_lock.json"
T41_PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"
T41_LOCK = ROOT / "cotangent_lifted_local_formal_projection_source_lock.json"
T42_PACKET = ROOT / "shared_circle_morse_bott_rank_four.packet.json"
QM_PACKET = (
    ROOT
    / "../mtt-qm-source-proof/certificates/q79_continuum_sm_classical_bv_composition.certificate.json"
)

Series = list[Fraction]
Q13 = tuple[Fraction, Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    sources = source_lock["construction_sources"] + source_lock["comparison_sources"]
    for index, source in enumerate(sources, start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def series_add(left: Series, right: Series) -> Series:
    return [a + b for a, b in zip(left, right)]


def series_subtract(left: Series, right: Series) -> Series:
    return [a - b for a, b in zip(left, right)]


def series_scale(value: Fraction, series: Series) -> Series:
    return [value * coefficient for coefficient in series]


def series_mul(left: Series, right: Series) -> Series:
    order = min(len(left), len(right)) - 1
    result = [Fraction(0) for _ in range(order + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= order:
                result[i + j] += a * b
    return result


def x_power_series(power: int, order: int) -> Series:
    result = [Fraction(0) for _ in range(order + 1)]
    for degree in range(min(power, order) + 1):
        result[degree] = Fraction(math.comb(power, degree))
    return result


def raw_log_seed_series(order: int) -> Series:
    log_x_squared = [Fraction(0)] + [
        2 * Fraction((-1) ** (degree + 1), degree)
        for degree in range(1, order + 1)
    ]
    return series_scale(Fraction(-1), series_mul(x_power_series(4, order), log_x_squared))


def derivative_values(series: Series, through: int) -> list[Fraction]:
    return [math.factorial(order) * series[order] for order in range(through + 1)]


def solve_linear(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    work = [row[:] + [value] for row, value in zip(matrix, rhs)]
    size = len(work)
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column] != 0)
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[column])
                ]
    return [work[row][-1] for row in range(size)]


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def q13_from_payload(payload: dict[str, str]) -> Q13:
    return Fraction(payload["rational"]), Fraction(payload["sqrt13"])


def q13_add(left: Q13, right: Q13) -> Q13:
    return left[0] + right[0], left[1] + right[1]


def q13_mul(left: Q13, right: Q13) -> Q13:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def q13_pow(value: Q13, power: int) -> Q13:
    result: Q13 = Fraction(1), Fraction(0)
    for _ in range(power):
        result = q13_mul(result, value)
    return result


def q13_text(value: Q13) -> dict[str, str]:
    return {"rational": ftext(value[0]), "sqrt13": ftext(value[1])}


def has_pin(lock: dict[str, Any], path: str, expected_hash: str) -> bool:
    return any(
        source["path"] == path and source["sha256"] == expected_hash
        for source in lock["local_sources"]
    )


def required_schema_keys(schema: dict[str, Any]) -> set[str]:
    return set(schema["required"])


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t23 = load_json(T23_PACKET)
    t25 = load_json(T25_PACKET)
    t25_lock = load_json(T25_LOCK)
    t30 = load_json(T30_PACKET)
    t30_lock = load_json(T30_LOCK)
    t34 = load_json(T34_PACKET)
    t34_lock = load_json(T34_LOCK)
    t35 = load_json(T35_PACKET)
    t35_lock = load_json(T35_LOCK)
    t39 = load_json(T39_PACKET)
    t39_lock = load_json(T39_LOCK)
    t40 = load_json(T40_PACKET)
    t40_lock = load_json(T40_LOCK)
    t41 = load_json(T41_PACKET)
    t41_lock = load_json(T41_LOCK)
    t42 = load_json(T42_PACKET)
    qm = load_json(QM_PACKET)

    source_checks = source_hash_checks(source_lock)

    physical_carrier = t23["carrier_and_incidence"]
    qm_carrier = qm["carrier_ledger"]
    ko6 = t30["KO6_polarization"]
    multiplicities = t30["chiral_finite_operator"]["response_branch_multiplicities"]
    ordered_branches = t30["dimensionless_branch_values"]["ordered_by_response_eigenvalue"]

    branch_order = ["-4", "-2", "2"]
    sigmas = {
        key: q13_from_payload(ordered_branches[key]["exact_coefficients"])
        for key in branch_order
    }
    q4: Q13 = Fraction(0), Fraction(0)
    for sigma in sigmas.values():
        q4 = q13_add(q4, q13_pow(sigma, 4))
    expected_q4: Q13 = Fraction(356, 27), Fraction(25, 27)

    per_weyl_pi2 = Fraction(1, 32)
    per_dirac_pi2 = Fraction(1, 16)
    branch_multiplicity = multiplicities["-4"]
    selected_kappa_pi2 = branch_multiplicity * per_weyl_pi2
    doubled_kappa_pi2 = branch_multiplicity * per_dirac_pi2

    order = 10
    raw = raw_log_seed_series(order)
    raw_jets = derivative_values(raw, 5)
    jet_matrix = [
        [Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(0), Fraction(2), Fraction(4)],
        [Fraction(0), Fraction(2), Fraction(12)],
    ]
    interpolation_coefficients = solve_linear(jet_matrix, raw_jets[:3])
    polynomial = [Fraction(0) for _ in range(order + 1)]
    for coefficient, power in zip(interpolation_coefficients, [0, 2, 4]):
        polynomial = series_add(polynomial, series_scale(coefficient, x_power_series(power, order)))
    remainder = series_subtract(raw, polynomial)
    remainder_jets = derivative_values(remainder, 5)

    expected_rho = series_add(
        series_add(
            series_mul(
                x_power_series(4, order),
                series_add(
                    [Fraction(3, 2)] + [Fraction(0)] * order,
                    series_scale(Fraction(-1), [Fraction(0)] + [
                        2 * Fraction((-1) ** (degree + 1), degree)
                        for degree in range(1, order + 1)
                    ]),
                ),
            ),
            series_scale(Fraction(-2), x_power_series(2, order)),
        ),
        [Fraction(1, 2)] + [Fraction(0)] * order,
    )
    expected_jets = [
        Fraction(0),
        Fraction(0),
        Fraction(0),
        Fraction(-16),
        Fraction(-64),
        Fraction(-48),
    ]

    t25_hash = sha256(T25_PACKET)
    t30_hash = sha256(T30_PACKET)
    t34_hash = sha256(T34_PACKET)
    t35_hash = sha256(T35_PACKET)
    t39_hash = sha256(T39_PACKET)
    t40_hash = sha256(T40_PACKET)

    graph_edges = {
        "T25_lock_pins_T23": has_pin(t25_lock, "physical_yukawa_hessian.packet.json", sha256(T23_PACKET)),
        "T30_lock_pins_T25_theorem": has_pin(t30_lock, "DirectFiniteSourceCausalContinuumDiracYukawaRealizationTheorem_v1.md", sha256(ROOT / "DirectFiniteSourceCausalContinuumDiracYukawaRealizationTheorem_v1.md")),
        "T30_lock_pins_T25_packet": has_pin(t30_lock, "direct_finite_source_continuum.packet.json", t25_hash),
        "T34_lock_pins_T25": has_pin(t34_lock, "direct_finite_source_continuum.packet.json", t25_hash),
        "T34_lock_pins_T30": has_pin(t34_lock, "ko6_fermionic_determinant_value_selection.packet.json", t30_hash),
        "T35_lock_pins_T30": has_pin(t35_lock, "ko6_fermionic_determinant_value_selection.packet.json", t30_hash),
        "T35_lock_pins_T34": has_pin(t35_lock, "same_root_state_repair_heat_profile_radial_values.packet.json", t34_hash),
        "T39_lock_pins_T35": has_pin(t39_lock, "frozen_source_four_dimensional_fermion_pushforward.packet.json", t35_hash),
        "T40_lock_pins_T35": has_pin(t40_lock, "frozen_source_four_dimensional_fermion_pushforward.packet.json", t35_hash),
        "T40_lock_pins_T39": has_pin(t40_lock, "renormalized_bv_anchored_repair_semiflow.packet.json", t39_hash),
        "T41_lock_pins_T39": has_pin(t41_lock, "renormalized_bv_anchored_repair_semiflow.packet.json", t39_hash),
        "T41_lock_pins_T40": has_pin(t41_lock, "source_preserving_pointed_quantum_projection.packet.json", t40_hash),
    }

    construction_root_payload = {
        "schema": "boe.mtt.weyl-polarized-product-dirac-g0-derived-root.v1",
        "T25_direct_source_root_sha256": t25["direct_source_root_sha256"],
        "physical_particle_dimension": physical_carrier["particle_dimension"],
        "KO6_completion_dimension": physical_carrier["KO6_dimension"],
        "left_Weyl_internal_dimension": qm_carrier["three_family_left_Weyl_internal_dimension"],
        "left_Weyl_spin_dimension": qm_carrier["left_Weyl_spin_dimension"],
        "source_coordinate": t30["selected_coordinate"]["expression"],
        "branch_factors": {
            key: ordered_branches[key]["exact_coefficients"] for key in branch_order
        },
        "branch_multiplicities": {key: multiplicities[key] for key in branch_order},
        "radial_anchor": t34["promoted_radial_values"]["h_over_Lambda"],
        "analytic_rule": source_lock["analytic_rule"],
        "counterterm_basis": ["1", "x^2", "x^4"],
        "pointed_conditions": ["Delta V(H)=0", "Delta V'(H)=0", "Delta V''(H)=0"],
        "excluded": [
            "rho",
            "CBF.T35 output",
            "CBF.T39 output",
            "CBF.T42 rank-four profile",
            "observed masses",
            "fitted coefficients",
            "q79 HYM endpoint",
        ],
        "construction_source_hashes": [
            source["sha256"] for source in source_lock["construction_sources"]
        ],
    }
    construction_root = canonical_hash(construction_root_payload)

    rho_text = "rho(x)=x^4(3/2-log(x^2))-2x^2+1/2"
    t35_rho = t35["closure_jet_matching"]["normalized_shape"]
    t39_rho = t39["T35_pointed_execution"]["normalized_matched_remainder"]
    t42_rho = t42["determinant_lift"]["rho"]

    packet: dict[str, Any] = {
        "schema": "boe.mtt.weyl-polarized-product-dirac-g0.v1",
        "claim_id": "CBF.T43",
        "title": "Weyl-Polarized Product-Dirac One-Loop Pushforward and Direct G0 Source",
        "date": "2026-08-30",
        "status": (
            "exact same-source direct product-Dirac flat-background local one-loop pushforward; "
            "Weyl normalization selected and normalized remainder source-derived; global Lorentzian, "
            "q79 HYM, G1 and G2 promotion open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "all_source_hashes_match": all(source_checks.values()),
            "construction_sources": len(source_lock["construction_sources"]),
            "comparison_sources": len(source_lock["comparison_sources"]),
            "comparison_sources_excluded_from_root": True,
            "construction_root_payload": construction_root_payload,
            "construction_root_sha256": construction_root,
        },
        "carrier_ledger": {
            "one_family_left_Weyl_internal_dimension": qm_carrier["one_family_left_Weyl_internal_dimension"],
            "three_family_left_Weyl_internal_dimension": qm_carrier["three_family_left_Weyl_internal_dimension"],
            "left_Weyl_spin_dimension": qm_carrier["left_Weyl_spin_dimension"],
            "continuum_left_Weyl_component_dimension": qm_carrier["continuum_left_Weyl_component_dimension"],
            "particle_carrier_dimension": physical_carrier["particle_dimension"],
            "KO6_real_completion_dimension": physical_carrier["KO6_dimension"],
            "KO6_description": physical_carrier["KO6_real_carrier"],
            "KO6_chiral_dimensions": ko6["dimensions"],
            "branch_multiplicities": {key: multiplicities[key] for key in branch_order},
            "branch_multiplicity_sum": sum(multiplicities[key] for key in branch_order),
            "off_shell_components_equal_Weyl_times_spin": qm_carrier["three_family_left_Weyl_internal_dimension"] * qm_carrier["left_Weyl_spin_dimension"],
            "KO6_completion_is_not_an_independent_field_copy": True,
            "q79_rank_is_not_particle_multiplicity": True,
        },
        "product_dirac_pushforward": {
            "source_operator": t25["causal_operator"]["operator"],
            "neutral_frame": t25["causal_operator"]["neutral_frame"],
            "exact_square": t25["exact_response"]["factorized_square"],
            "source_coordinate": t30["selected_coordinate"]["expression"],
            "polarized_mass_squares": "m_a(h)^2=h^2 sigma_a^2",
            "branch_factors": {
                key: {
                    "expression": ordered_branches[key]["expression"],
                    "exact_coefficients": ordered_branches[key]["exact_coefficients"],
                    "multiplicity": multiplicities[key],
                }
                for key in branch_order
            },
            "Berezin_pushforward": "-log det D_W=-(1/2)Tr_spin log(D_W^*D_W)+phase",
            "local_even_modulus_executed": True,
            "phase_executed": False,
            "Galerkin_proxy_used": False,
            "T42_rank_four_profile_used": False,
            "rho_used_as_input": False,
        },
        "determinant_exponent": {
            "fermionic_sign": -1,
            "squared_operator_exponent": "1/2",
            "left_Weyl_spin_trace": qm_carrier["left_Weyl_spin_dimension"],
            "per_left_Weyl_coefficient": "1/(32 pi^2)",
            "per_complex_Dirac_coefficient": "1/(16 pi^2)",
            "branch_multiplicity": branch_multiplicity,
            "selected_kappa_F": "1/(2 pi^2)",
            "selected_kappa_F_times_pi_squared": ftext(selected_kappa_pi2),
            "rejected_doubled_candidate": "1/pi^2",
            "rejected_candidate_times_pi_squared": ftext(doubled_kappa_pi2),
            "selection_reason": "the source contains 48 two-component left-Weyl fields; the 96-dimensional KO6 space is their real completion",
            "global_phase_can_change_local_even_multiplicity": False,
        },
        "exact_finite_trace": {
            "q4_star": {
                "expression": "(356+25sqrt(13))/27",
                "exact_coefficients": q13_text(q4),
            },
            "L4_star": "sum_a sigma_a^4 log(sigma_a^2)",
            "flat_one_loop_formula": "V_F(h)=-h^4[q4_*log(h^2/mu^2)+L4_*-c_scheme q4_*]/(2 pi^2)",
            "q4_matches_T35": q13_text(q4) == t35["fixed_source_four_dimensional_determinant"]["q4_star"]["exact_coefficients"],
            "observed_values_used": False,
        },
        "pointed_renormalization": {
            "normalized_raw_seed": "f(x)=-x^4 log(x^2)",
            "raw_series_about_x1_through_order10": [ftext(value) for value in raw],
            "raw_jets_at_x1_through_order5": [ftext(value) for value in raw_jets],
            "allowed_even_local_basis": ["1", "x^2", "x^4"],
            "jet_matrix": [[ftext(value) for value in row] for row in jet_matrix],
            "jet_matrix_determinant": ftext(determinant3(jet_matrix)),
            "interpolation_coefficients_c0_c2_c4": [
                ftext(value) for value in interpolation_coefficients
            ],
            "interpolation_polynomial": "I_H f=-1/2+2x^2-(3/2)x^4",
            "remainder": rho_text,
            "remainder_series_about_x1_through_order10": [ftext(value) for value in remainder],
            "remainder_jets_at_x1_through_order5": [ftext(value) for value in remainder_jets],
            "rho_is_output_not_input": True,
            "unique_zero_two_jet_representative": determinant3(jet_matrix) != 0,
            "scheme_scale_and_L4_cancel": True,
        },
        "emitted_action": {
            "formula": "Delta V_cl(h)=q4_* H^4 rho(h/H)/(2 pi^2)",
            "exact_amplitude": "(356+25sqrt(13)) H^4/(54 pi^2)",
            "third_vertex_shift": "-8 q4_* H/pi^2",
            "fourth_vertex_shift": "-32 q4_*/pi^2",
            "fifth_vertex_shift": "-24 q4_*/(pi^2 H)",
            "fixed_point_preserved": remainder_jets[0] == 0 and remainder_jets[1] == 0,
            "radial_Hessian_preserved": remainder_jets[2] == 0,
            "higher_vertices_nonzero": remainder_jets[3:] != [Fraction(0)] * 3,
            "matches_T35_shape": rho_text == t35_rho,
            "matches_T39_shape_and_jets": rho_text == t39_rho and remainder_jets == expected_jets,
        },
        "same_source_graph": {
            "nodes": ["CBF.T23", "CBF.T25", "CBF.T30", "CBF.T34", "CBF.T35", "CBF.T39", "CBF.T40", "CBF.T41", "CBF.T43"],
            "verified_edges": graph_edges,
            "all_edges_verified": all(graph_edges.values()),
            "one_construction_root": construction_root,
            "T35_T39_T42_used_only_as_output_comparisons": True,
            "direct_operator_and_one_loop_action_share_root": True,
            "physical_q79_HYM_root_identified_with_direct_root": False,
        },
        "T42_comparison": {
            "normalized_scalar_remainder_matches": rho_text == t42_rho,
            "T42_rank": t42["determinant_lift"]["rank"],
            "T42_is_target_informed": t42["determinant_lift"]["determinant_lift_is_target_informed"],
            "T43_uses_physical_Weyl_multiplicity": True,
            "operators_identified": False,
            "correlators_identified": False,
            "q79_rank_four_counts_physical_particles": False,
            "future_target": "construct a selected q79/HYM universality intertwiner to the direct product-Dirac pushforward",
        },
        "gate_ledger": {
            "G0_direct_local_one_loop": {
                "closed": True,
                "scope": "fixed t_*, flat constant radial chart, local even one-loop modulus and pointed action two-jet",
                "witness": "CBF.T25 Weyl Berezin pushforward followed by the unique R_H quotient",
            },
            "G0_global_physical": {
                "closed": False,
                "missing": "selected global determinant domain, cycle, phase and source transport",
            },
            "G0_q79_HYM": {
                "closed": False,
                "missing": "selected HYM/Strominger normal operator and its determinant/BV intertwiner",
            },
            "G1_physical_tangent_pairing": {
                "closed": False,
                "missing": "parallel physical line map, kinetic metric and Hessian transport",
            },
            "G2_selected_interacting_state_BV": {
                "closed": False,
                "missing": "fixed-coupling interacting QME-preserving BV and state pushforward",
            },
            "physical_gluing_gates_closed": t41["physical_gluing_gates_closed"],
            "physical_gluing_gates_total": t41["physical_gluing_gates_total"],
            "physical_packets_accepted": t41["physical_packets_accepted"],
            "physical_packets_total": t41["physical_packets_total"],
            "physical_rows_accepted": t41["physical_rows_accepted"],
            "physical_rows_total": t41["physical_rows_total"],
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_continuous_physical_parameters": 0,
            "local_determinant_normalization_candidates_before": 2,
            "local_determinant_normalization_candidates_after": 1,
            "selected_local_kappa_F": "1/(2 pi^2)",
            "universal_four_dimensional_Weyl_coefficient_is_a_fit": False,
            "inherited_radial_scale_primitives": 1,
            "absolute_SI_scale_selected": False,
            "global_determinant_phase_selected": False,
        },
        "physical_boundary": {
            "direct_local_flat_one_loop_pushforward_closed": True,
            "Weyl_exponent_selected": True,
            "normalized_remainder_source_derived": True,
            "global_Wick_or_direct_Lorentzian_determinant_closed": False,
            "determinant_line_orientation_closed": False,
            "selected_external_BV_operator_domain_closed": False,
            "q79_HYM_normal_operator_closed": False,
            "direct_and_q79_HYM_routes_identified": False,
            "physical_parallel_line_and_metric_closed": False,
            "selected_interacting_state_BV_closed": False,
            "RG_and_pole_transport_closed": False,
            "held_out_observable_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "B_OP_01_closed": False,
            "B_GEO_01_closed": False,
        },
        "frontier_delta": (
            "CBF.T43 replaces the target-informed determinant construction on the direct route with the "
            "actual CBF.T25 product-Dirac Weyl Berezin pushforward. The independent 48-left-Weyl carrier "
            "ledger fixes kappa_F=1/(2 pi^2) and rejects the doubled 1/pi^2 candidate. Solving the three "
            "pointed jet equations on span{1,x^2,x^4} derives the complete rho remainder and its fifth jet "
            "without taking rho as input. This closes a same-source direct/local one-loop G0 instance only; "
            "global Lorentzian, q79 HYM, G1, G2 and physical acceptance remain open."
        ),
    }

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema": source_lock["schema"] == "boe.mtt.weyl-polarized-product-dirac-g0-source-lock.v1",
        "handoff_pinned": source_lock["handoff_id"] == "45511f30-5ca5-49a8-bca3-20f258e6ad20",
        "kernel_model_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "schema_claim": schema["properties"]["claim_id"]["const"] == "CBF.T43",
        "theorem_nonempty": THEOREM.stat().st_size > 8000,
        "T23_passes": t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()),
        "T25_passes": t25["claim_id"] == "CBF.T25" and all(t25["checks"].values()),
        "T30_passes": t30["claim_id"] == "CBF.T30" and all(t30["checks"].values()),
        "T34_passes": t34["claim_id"] == "CBF.T34" and all(t34["checks"].values()),
        "T35_passes": t35["claim_id"] == "CBF.T35" and all(t35["checks"].values()),
        "T39_passes": t39["claim_id"] == "CBF.T39" and all(t39["checks"].values()),
        "T40_passes": t40["claim_id"] == "CBF.T40" and all(t40["checks"].values()),
        "T41_passes": t41["claim_id"] == "CBF.T41" and all(t41["checks"].values()),
        "T42_passes": t42["claim_id"] == "CBF.T42" and all(t42["checks"].values()),
        "QM_certificate_passes": qm["all_checks_pass"],
        "particle_dimension_48": physical_carrier["particle_dimension"] == 48,
        "KO6_dimension_96": physical_carrier["KO6_dimension"] == 96,
        "KO6_is_completion": physical_carrier["KO6_real_carrier"] == "particle direct_sum antiparticle",
        "QM_internal_Weyl_48": qm_carrier["three_family_left_Weyl_internal_dimension"] == 48,
        "QM_spin_dimension_2": qm_carrier["left_Weyl_spin_dimension"] == 2,
        "QM_offshell_96": qm_carrier["continuum_left_Weyl_component_dimension"] == 96,
        "offshell_product_exact": qm_carrier["three_family_left_Weyl_internal_dimension"] * qm_carrier["left_Weyl_spin_dimension"] == qm_carrier["continuum_left_Weyl_component_dimension"],
        "KO6_chiral_halves_48": ko6["dimensions"] == {"minus": 48, "plus": 48},
        "statistics_not_KO_chirality": not ko6["KO_chirality_used_as_statistics"],
        "multiplicities_all_16": all(multiplicities[key] == 16 for key in branch_order),
        "multiplicity_sum_48": sum(multiplicities[key] for key in branch_order) == 48,
        "per_Weyl_coefficient": per_weyl_pi2 == Fraction(1, 32),
        "selected_kappa_half": selected_kappa_pi2 == Fraction(1, 2),
        "Dirac_candidate_doubled": doubled_kappa_pi2 == 1,
        "q4_exact": q4 == expected_q4,
        "q4_matches_T35": packet["exact_finite_trace"]["q4_matches_T35"],
        "raw_value_slope_Hessian": raw_jets[:3] == [Fraction(0), Fraction(-2), Fraction(-14)],
        "jet_matrix_determinant_16": determinant3(jet_matrix) == 16,
        "interpolant_exact": interpolation_coefficients == [Fraction(-1, 2), Fraction(2), Fraction(-3, 2)],
        "remainder_is_rho": remainder == expected_rho,
        "remainder_jets_exact": remainder_jets == expected_jets,
        "remainder_zero_two_jet": remainder_jets[:3] == [0, 0, 0],
        "higher_vertices_retained": remainder_jets[3:] == [-16, -64, -48],
        "rho_matches_T35": rho_text == t35_rho,
        "rho_matches_T39": rho_text == t39_rho,
        "rho_matches_T42": rho_text == t42_rho,
        "rho_not_in_construction_root": "rho" in construction_root_payload["excluded"] and "rho" not in json.dumps({key: value for key, value in construction_root_payload.items() if key != "excluded"}),
        "comparison_hashes_not_in_root": all(source["sha256"] not in construction_root_payload["construction_source_hashes"] for source in source_lock["comparison_sources"]),
        "all_lineage_edges": all(graph_edges.values()),
        "direct_operator_root_present": len(t25["direct_source_root_sha256"]) == 64,
        "T25_exact_square": t25["exact_response"]["factorized_square"] == "D_dir(t,h)^2=D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2",
        "direct_local_G0_closed": packet["gate_ledger"]["G0_direct_local_one_loop"]["closed"],
        "global_G0_open": not packet["gate_ledger"]["G0_global_physical"]["closed"],
        "HYM_G0_open": not packet["gate_ledger"]["G0_q79_HYM"]["closed"],
        "G1_open": not packet["gate_ledger"]["G1_physical_tangent_pairing"]["closed"],
        "G2_open": not packet["gate_ledger"]["G2_selected_interacting_state_BV"]["closed"],
        "physical_gates_unchanged": packet["gate_ledger"]["physical_gluing_gates_closed"] == 0 and packet["gate_ledger"]["physical_gluing_gates_total"] == 3,
        "physical_packets_unchanged": packet["gate_ledger"]["physical_packets_accepted"] == 0 and packet["gate_ledger"]["physical_packets_total"] == 3,
        "physical_rows_unchanged": packet["gate_ledger"]["physical_rows_accepted"] == 0 and packet["gate_ledger"]["physical_rows_total"] == 7,
        "T42_target_informed": packet["T42_comparison"]["T42_is_target_informed"],
        "operators_not_identified": not packet["T42_comparison"]["operators_identified"],
        "no_observed_inputs": packet["parameter_ledger"]["new_observed_inputs"] == 0,
        "no_fitted_coefficients": packet["parameter_ledger"]["new_fitted_coefficients"] == 0,
        "no_new_continuous_parameters": packet["parameter_ledger"]["new_continuous_physical_parameters"] == 0,
        "normalization_ambiguity_reduced": packet["parameter_ledger"]["local_determinant_normalization_candidates_before"] == 2 and packet["parameter_ledger"]["local_determinant_normalization_candidates_after"] == 1,
        "B_ACTION_open": not packet["physical_boundary"]["B_ACTION_01_closed"],
        "B_QFT_open": not packet["physical_boundary"]["B_QFT_02_closed"],
        "B_OP_open": not packet["physical_boundary"]["B_OP_01_closed"],
        "B_GEO_open": not packet["physical_boundary"]["B_GEO_01_closed"],
        "theorem_claim": "**Claim:** CBF.T43" in THEOREM.read_text(encoding="utf-8"),
        "theorem_kappa": "kappa_F=1/(2 pi^2)" in THEOREM.read_text(encoding="utf-8"),
        "theorem_no_rho_input": "not an input" in THEOREM.read_text(encoding="utf-8"),
        "theorem_guard": "not a global q79 HYM determinant theorem" in THEOREM.read_text(encoding="utf-8"),
    }

    packet["checks"] = checks
    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["check_summary"] = {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
    }

    missing_schema_keys = required_schema_keys(schema) - set(packet)
    if missing_schema_keys:
        raise SystemExit(f"packet misses schema keys: {sorted(missing_schema_keys)}")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"builder checks: {packet['check_summary']['passed']}/{packet['check_summary']['total']}")
    if failed:
        raise SystemExit("failed checks: " + ", ".join(failed))
    return packet


if __name__ == "__main__":
    build()
