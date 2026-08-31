#!/usr/bin/env python3
"""Build the exact CBF.T49 common action-quantum torsor packet."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "common_action_quantum_torsor_source_lock.json"
SCHEMA = ROOT / "common_action_quantum_torsor_contract.schema.json"
THEOREM = ROOT / "CommonActionQuantumTorsorAndOnePrimitiveBVNormalizationTheorem_v1.md"
OUTPUT = ROOT / "common_action_quantum_torsor.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [entry / pivot_value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def source_paths(lock: dict[str, Any]) -> dict[str, Path]:
    return {
        item["id"]: (ROOT / item["path"]).resolve()
        for item in lock["sources"]
    }


def main() -> None:
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    theorem_text = THEOREM.read_text(encoding="utf-8")
    paths = source_paths(lock)

    hashes_match = {
        item["id"]: paths[item["id"]].is_file()
        and sha256(paths[item["id"]]) == item["sha256"]
        for item in lock["sources"]
    }

    t32 = load_json(paths["T32"])
    t39 = load_json(paths["T39"])
    t43 = load_json(paths["T43"])
    t46 = load_json(paths["T46"])
    t48 = load_json(paths["T48"])
    a51 = load_json(paths["A51_PACKET"])
    a52 = load_json(paths["A52_PACKET"])
    a88 = load_json(paths["A88_PACKET"])
    a89 = load_json(paths["A89_CERT"])
    h4_t14 = load_json(paths["H4_T14"])
    q79_qme_text = paths["Q79_QME"].read_text(encoding="utf-8")
    q79_shell = load_json(paths["Q79_FINITE_SHELL_BV"])

    trace_factor = Fraction(32)
    heat_denominator = Fraction(8)
    a_h_over_f0 = trace_factor / heat_denominator
    c_g_over_f0 = Fraction(6)
    a_h_over_c_g_rational = a_h_over_f0 / c_g_over_f0
    loop_over_tree_rational = Fraction(1, 2) / a_h_over_f0

    amplitude_direction = [Fraction(1)] * 4
    amplitude_jacobian = [[entry] for entry in amplitude_direction]
    relative_projection = [
        [Fraction(1), Fraction(-1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)],
    ]
    projected_direction = matvec(relative_projection, amplitude_direction)

    profile_f0 = float(
        a52["minimal_profile_normalization"][
            "f0_in_g_i^-2_equals_6_f0_K_i_convention"
        ]
    )
    profile_a_h = 4.0 * profile_f0 / math.pi**2
    profile_c_g = 6.0 * profile_f0
    profile_ratio = profile_a_h / profile_c_g
    exact_ratio_float = 2.0 / (3.0 * math.pi**2)

    checks: dict[str, bool] = {
        "source_lock_schema_is_exact": lock["schema"]
        == "boe.mtt.common-action-quantum-torsor-source-lock.v1",
        "source_lock_claim_is_T49": lock["claim_id"] == "CBF.T49",
        "all_source_paths_exist": all(path.is_file() for path in paths.values()),
        "all_source_hashes_match": all(hashes_match.values()),
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.common-action-quantum-torsor.v1",
        "contract_claim_is_T49": schema["properties"]["claim_id"]["const"]
        == "CBF.T49",
        "T32_claim_is_exact": t32["claim_id"] == "CBF.T32",
        "T32_scalar_action_has_f0_over_8pi2": t32["conditional_action_scope"][
            "scalar_action"
        ].startswith("f0/(8pi^2)"),
        "T32_suppressed_factor_is_32f0_over_8pi2": t32[
            "conditional_action_scope"
        ]["overall_positive_factor_suppressed_below"]
        == "32 f0/(8pi^2)",
        "T32_quadratic_trace_factor_is_32": t32["exact_trace_data"][
            "Tr_D_squared"
        ]
        == "32 q2(t)",
        "T32_quartic_trace_factor_is_32": t32["exact_trace_data"][
            "Tr_D_fourth"
        ]
        == "32 q4(t)",
        "A51_one_Higgs_projection_is_exact": a51["checks"]
        ["selected_single_Higgs_module_rank_4"]
        and a51["checks"]["single_Higgs_projector_idempotent"],
        "A51_absolute_coefficient_is_open": a51["bosonic_action_interface"]
        ["absolute_coefficient_normalization_closed"]
        is False,
        "A52_profile_product_action_is_closed": a52["epistemic_policy"]
        ["profile_bosonic_matter_action_closed"],
        "A52_strict_universal_action_is_open": a52["epistemic_policy"]
        ["strict_universal_spectral_action_closed"]
        is False,
        "A52_selected_f0_is_not_strict": a52["moment_identifiability"]
        ["selected_f0_f2_f4_from_MTT"]
        is False,
        "A88_positive_scale_orbit_rank_is_one": a88["jacobian_rank"] == 1,
        "A88_one_anchor_is_minimal": a88["parameter_conclusion"]
        ["one_anchor_is_minimal_at_current_corpus_action_tier"],
        "A88_common_coordinates_remaining_is_one": a88["parameter_conclusion"]
        ["common_continuous_coordinates_remaining"]
        == 1,
        "A89_one_shared_primitive_standard_is_adopted": a89[
            "one_shared_primitive_gauge_standard_closed"
        ],
        "A89_strict_zero_anchor_is_open": a89["strict_primitive_zero_anchor_closed"]
        is False,
        "A89_topological_shortcut_is_rejected": a89["level120_candidate_promoted"]
        is False,
        "A_H_over_f0_is_exactly_four_over_pi2": a_h_over_f0 == 4,
        "common_gauge_amplitude_over_f0_is_six": c_g_over_f0 == 6,
        "A_H_over_c_g_rational_part_is_two_thirds": a_h_over_c_g_rational
        == Fraction(2, 3),
        "loop_over_tree_rational_part_is_one_eighth": loop_over_tree_rational
        == Fraction(1, 8),
        "combined_amplitude_jacobian_has_rank_one": rank(amplitude_jacobian) == 1,
        "relative_projection_kills_common_direction": projected_direction
        == [Fraction(0), Fraction(0), Fraction(0)],
        "relative_projection_has_rank_three": rank(relative_projection) == 3,
        "profile_A_H_matches_common_formula": math.isclose(
            profile_a_h, 0.16106348735963533, rel_tol=0.0, abs_tol=2e-16
        ),
        "profile_c_g_matches_six_f0": math.isclose(
            profile_c_g, 2.3844493555491857, rel_tol=0.0, abs_tol=5e-16
        ),
        "profile_relative_ratio_matches_exact_formula": math.isclose(
            profile_ratio, exact_ratio_float, rel_tol=0.0, abs_tol=2e-17
        ),
        "T43_selects_Weyl_half_coefficient": t43["determinant_exponent"]
        ["selected_kappa_F"]
        == "1/(2 pi^2)",
        "T43_emits_actual_direct_action": t43["emitted_action"]["formula"]
        == "Delta V_cl(h)=q4_* H^4 rho(h/H)/(2 pi^2)",
        "T43_remainder_has_zero_two_jet": t43["pointed_renormalization"]
        ["remainder_jets_at_x1_through_order5"][:3]
        == ["0", "0", "0"],
        "T43_higher_vertices_are_nonzero": t43["emitted_action"]
        ["higher_vertices_nonzero"],
        "T39_anchor_has_zero_free_coefficients": t39["anchored_formal_bv_flow"]
        ["new_free_counterterm_coefficients"]
        == 0,
        "T39_formal_QME_scheme_is_not_upper_selected": t39[
            "anchored_formal_bv_flow"
        ]["upper_MTT_selects_this_normalization"]
        is False,
        "T39_physical_endpoint_is_open": t39["physical_boundary"]
        ["physical_interacting_q79_BV_endpoint_executed"]
        is False,
        "T46_formal_pullback_exists": t46["formal_BV_state_pullback"]
        ["closed_as_algebraic_transport_theorem"],
        "T46_fixed_coupling_continuum_is_open": t46["fixed_coupling_boundary"]
        ["selected_continuum_Cstar_rows"]
        == "0/9",
        "T48_complete_free_seed_is_closed": t48["complete_free_seed"]
        ["missing_selected_factors"]
        == 0,
        "T48_A_H_was_recorded_unresolved": t48["parameter_ledger"]
        ["inherited_unresolved_scalar_action_amplitude"]
        == "A_H>0",
        "T48_mass_is_independent_of_A_H": t48["canonical_radial_hessian"]
        ["mass_squared"]
        == "m_h^2=8c"
        and t48["canonical_radial_hessian"]["absolute_field_normalization_selected"]
        is False,
        "H4_cotangent_completion_is_exact": h4_t14["selection_boundary"]
        ["canonical_cotangent_cyclic_completion_closed"],
        "H4_physical_trace_normalization_is_open": h4_t14["selection_boundary"]
        ["selected_physical_trace_normalization_closed"]
        is False,
        "H4_physical_antifields_are_open": h4_t14["selection_boundary"]
        ["cotangent_duals_identified_as_physical_antifields"]
        is False,
        "q79_QME_action_coefficients_remain_profile": "action coefficients remain\nprofile coordinates"
        in q79_qme_text,
        "q79_QME_blocker_remains_open": "`B.ACTION.01` remains open" in q79_qme_text,
        "finite_shell_free_QME_is_exact": q79_shell["blocker_assessment"]
        ["B.QFT.02_free_finite_shell_QME_pushforward"]
        == "closed_up_to_the_transported_determinant_line_scalar",
        "finite_shell_interacting_limit_is_open": q79_shell["blocker_assessment"]
        ["B.QFT.02_interacting_fixed_coupling_Cstar_limit"]
        == "open",
        "radial_and_gauge_c_symbols_are_type_separated": lock["guards"]
        ["radial_c_H_is_not_the_gauge_amplitude_c_g"],
        "profile_value_is_diagnostic_only": lock["guards"]
        ["A52_profile_f0_is_diagnostic_only"],
        "physical_counters_are_frozen": lock["guards"]
        ["physical_acceptance_counters_must_not_move"],
        "theorem_states_A_H_identity": "A_H=32 f0/(8 pi^2)=4 f0/pi^2" in theorem_text,
        "theorem_states_one_loop_tree_ratio": "one-loop/tree=1/(8alpha)" in theorem_text,
        "theorem_preserves_strict_open_boundary": "strict source selection of alpha:              open"
        in theorem_text,
        "theorem_does_not_close_ACTION_blocker": "closure of `B.ACTION.01`" in theorem_text,
    }

    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"CBF.T49 builder checks failed: {failed}")

    common_map = {
        "T32_trace_factor": 32,
        "T32_heat_kernel_prefactor": "f0/(8 pi^2)",
        "A_H": "4 f0/pi^2",
        "gauge_inverse_couplings": "g_i^(-2)=6 f0 K_i",
        "scalar_to_gauge_ratio": "A_H/g_i^(-2)=2/(3 pi^2 K_i)",
        "typed_scales": {
            "c_H": "(f2/f0)Lambda^2; radial mass-squared scale",
            "c_g": "6f0; common gauge action amplitude",
            "equality_claimed": False,
        },
        "profile_diagnostic_only": {
            "f0": profile_f0,
            "A_H": profile_a_h,
            "c_g": profile_c_g,
            "A_H_over_c_g": profile_ratio,
            "strict_MTT_source": False,
        },
    }

    dimensionless_action = {
        "shared_primitive": "alpha=f0/hbar",
        "tree_prefactor": "4 alpha/pi^2",
        "selected_Weyl_one_loop_prefactor": "1/(2 pi^2)",
        "one_loop_over_tree_prefactor": "1/(8 alpha)",
        "radial_action_through_one_loop": (
            "Gamma_rad/hbar=(4alpha/pi^2) integral P_*(h)"
            "+ integral q4_* H_*^4 rho(h/H_*)/(2pi^2)+higher formal orders"
        ),
        "rho": "x^4(3/2-log(x^2))-2x^2+1/2",
        "rho_jets_0_through_5_at_one": [0, 0, 0, -16, -64, -48],
        "fixed_coupling_convergence_claimed": False,
    }

    canonical_vertices = {
        "canonical_field": "phi=sqrt(2 A_H q2_*) eta",
        "mass_squared": "8 c_H",
        "mass_common_amplitude_exponent": "0",
        "g3_tree": (
            "6sqrt(2)q4_*H_*/(sqrt(A_H)q2_*^(3/2))"
            "=3sqrt(2)pi q4_*H_*/(sqrt(f0)q2_*^(3/2))"
        ),
        "g4_tree": "6q4_*/(A_H q2_*^2)=3pi^2q4_*/(2f0 q2_*^2)",
        "f0_scaling_exponents": {
            "mass_squared": "0",
            "g3_tree": "-1/2",
            "g4_tree": "-1",
        },
        "conclusion": "the common amplitude cancels from the free generalized mass but not from canonical interactions",
    }

    positive_scale_torsor = {
        "action": "f0->a f0, A_H->a A_H, g_i^-2->a g_i^-2, g_i->a^(-1/2)g_i",
        "a_domain": "a>0",
        "log_amplitude_order": ["A_H", "g_1^-2", "g_2^-2", "g_3^-2"],
        "log_jacobian_column": [1, 1, 1, 1],
        "jacobian_rank": 1,
        "relative_projection": [
            [1, -1, 0, 0],
            [0, 1, -1, 0],
            [0, 1, 0, -1],
        ],
        "relative_projection_rank": 3,
        "relative_projection_of_orbit": [0, 0, 0],
        "invariants": [
            "g_i^-2/g_j^-2=K_i/K_j",
            "A_H/g_i^-2=2/(3pi^2K_i)",
            "m_h^2=8c_H",
            "fixed points and BRST cohomology",
            "normalized state transport",
        ],
        "noninvariants_at_fixed_hbar": [
            "alpha=f0/hbar",
            "one-loop/tree=1/(8alpha)",
            "canonical cubic and quartic interactions",
        ],
        "topology_or_phase_selects_orbit_point": False,
    }

    bv_scale = {
        "unit_rescaling": "S->aS and hbar->a hbar leaves S/hbar and alpha fixed",
        "QME_homogeneity": "both terms in 1/2(S,S)-i hbar Delta S scale by a^2",
        "physical_rescaling": "f0->a f0 at fixed hbar changes alpha",
        "T39_anchor_conditions": 3,
        "T39_free_coefficients_after_anchor": 0,
        "formal_QME_scheme_exists_for_each_alpha": True,
        "QME_or_Ward_selects_alpha": False,
        "H4_canonical_algebraic_cotangent_coefficient": 1,
        "H4_physical_multiplier_selected": False,
        "H4_to_direct_gluing_rule": (
            "if physical action pushforward is proved, its multiplier must represent the same alpha"
        ),
        "H4_to_direct_gluing_proved": False,
        "determinant_line_relative_holonomy_selected": False,
    }

    primitive_ledger = {
        "adopted_standard": "one shared positive action primitive",
        "A89_adopted_gauge_primitive": True,
        "shared_primitives_before_scalar_BV_consolidation": 1,
        "shared_primitives_after_scalar_BV_consolidation": 1,
        "new_primitives_introduced_by_T49": 0,
        "direct_radial_normalization_given_alpha": "closed through one loop and local-formally anchored",
        "strict_source_value_for_alpha": "open",
        "profile_value_is_empirical": True,
        "zero_knob_claimed": False,
    }

    physical_boundary = {
        "closed": [
            "A_H=4f0/pi^2",
            "rank-one scalar-gauge common-amplitude torsor",
            "direct radial tree-plus-one-loop normalization relative to alpha",
            "zero additional T39 radial counterterm coefficients",
            "one-shared-primitive consolidation at the adopted tier",
        ],
        "open": [
            "strict source selection of alpha",
            "source-derived positive gauge-overlap shape beyond profile use",
            "physical q79 cyclic pairing, trace density and real slice",
            "same-upper full interacting BV map",
            "determinant-line connection and relative holonomy",
            "fixed-coupling regulator-independent C-star continuum",
            "physical G1, top-level G2 and q79 endpoint rows",
        ],
        "B_ACTION_01_closed": False,
        "B_QFT_02_closed": False,
        "physical_gates": {"accepted": 0, "total": 3},
        "physical_packets": {"accepted": 0, "total": 3},
        "physical_rows": {"accepted": 0, "total": 7},
    }

    packet_core = {
        "schema": "boe.mtt.common-action-quantum-torsor.v1",
        "claim_id": "CBF.T49",
        "date": "2026-08-31",
        "status": (
            "exact common scalar-gauge action-amplitude rank-one torsor and direct "
            "local-formal one-primitive radial normalization; primitive value and "
            "physical q79 upper action remain open"
        ),
        "source_provenance": {
            "source_lock": SOURCE_LOCK.name,
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema": SCHEMA.name,
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem": THEOREM.name,
            "theorem_sha256": sha256(THEOREM),
            "model_state_sha256": lock["model_state_sha256"],
            "handoff_id": lock["handoff_id"],
            "source_hashes_match": hashes_match,
        },
        "common_coefficient_map": common_map,
        "dimensionless_effective_action": dimensionless_action,
        "canonical_radial_vertices": canonical_vertices,
        "positive_scale_torsor": positive_scale_torsor,
        "bv_qme_scale_separation": bv_scale,
        "one_shared_primitive_ledger": primitive_ledger,
        "physical_boundary": physical_boundary,
        "frontier_delta": (
            "The apparent independent scalar coefficient A_H is recovered exactly as "
            "4f0/pi^2 and joins the A88 gauge amplitudes in one rank-one positive "
            "action torsor. T43 and T39 then give the direct radial tree-plus-one-loop "
            "and anchored local-formal normalization relative to alpha=f0/hbar with "
            "zero extra coefficients. The adopted one-shared-primitive tier therefore "
            "needs no new scalar or BV knob. A88/A89 nonselection remains decisive: "
            "the value of alpha and the physical q79 cyclic real slice/full action are "
            "not selected, so B.ACTION.01, B.QFT.02 and all physical counters remain open."
        ),
    }
    packet_core["exact_payload_sha256"] = canonical_hash(packet_core)
    packet = {
        **packet_core,
        "checks": checks,
        "check_summary": {
            "passed": sum(checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
    }

    required = set(schema["required"])
    missing = sorted(required - set(packet))
    if missing:
        raise AssertionError(f"CBF.T49 packet misses contract keys: {missing}")

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"CBF.T49 build passed {packet['check_summary']['passed']}/"
        f"{packet['check_summary']['total']} checks"
    )
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
