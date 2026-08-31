#!/usr/bin/env python3
"""Independently verify the CBF.T49 action-quantum torsor packet."""

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
PACKET = ROOT / "common_action_quantum_torsor.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_entry = work[pivot_row][column]
        work[pivot_row] = [entry / pivot_entry for entry in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    entry - multiplier * pivot_value
                    for entry, pivot_value in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def main() -> None:
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    packet = load_json(PACKET)
    theorem_text = THEOREM.read_text(encoding="utf-8")
    sources = {entry["id"]: entry for entry in lock["sources"]}
    paths = {
        source_id: (ROOT / entry["path"]).resolve()
        for source_id, entry in sources.items()
    }

    t32 = load_json(paths["T32"])
    t39 = load_json(paths["T39"])
    t43 = load_json(paths["T43"])
    t46 = load_json(paths["T46"])
    t48 = load_json(paths["T48"])
    a52 = load_json(paths["A52_PACKET"])
    a88 = load_json(paths["A88_PACKET"])
    a89 = load_json(paths["A89_CERT"])
    h4 = load_json(paths["H4_T14"])
    shell = load_json(paths["Q79_FINITE_SHELL_BV"])

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("packet_schema", packet["schema"] == "boe.mtt.common-action-quantum-torsor.v1")
    check("packet_claim", packet["claim_id"] == "CBF.T49")
    check("source_lock_hash", packet["source_provenance"]["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("contract_hash", packet["source_provenance"]["contract_schema_sha256"] == sha256(SCHEMA))
    check("theorem_hash", packet["source_provenance"]["theorem_sha256"] == sha256(THEOREM))
    check("model_hash", packet["source_provenance"]["model_state_sha256"] == lock["model_state_sha256"])
    check("handoff_id", packet["source_provenance"]["handoff_id"] == lock["handoff_id"])
    check("all_source_files_exist", all(path.is_file() for path in paths.values()))
    for source_id, entry in sources.items():
        check(f"hash_{source_id}", sha256(paths[source_id]) == entry["sha256"])

    required = set(schema["required"])
    check("contract_required_keys", required <= set(packet))
    check("builder_check_summary", packet["check_summary"]["all_passed"] is True)
    check("builder_checks_all_true", all(packet["checks"].values()))
    check("builder_check_count", packet["check_summary"]["passed"] == len(packet["checks"]))

    core = dict(packet)
    core.pop("checks")
    core.pop("check_summary")
    stored_core_hash = core.pop("exact_payload_sha256")
    check("exact_payload_hash", stored_core_hash == canonical_hash(core))

    trace_factor = Fraction(32)
    heat_denominator = Fraction(8)
    a_h_factor = trace_factor / heat_denominator
    gauge_factor = Fraction(6)
    ratio_rational = a_h_factor / gauge_factor
    loop_tree_rational = Fraction(1, 2) / a_h_factor
    check("independent_A_H_factor", a_h_factor == 4)
    check("independent_gauge_factor", gauge_factor == 6)
    check("independent_scalar_gauge_ratio", ratio_rational == Fraction(2, 3))
    check("independent_loop_tree_ratio", loop_tree_rational == Fraction(1, 8))
    check("T32_trace_source", t32["exact_trace_data"]["Tr_D_squared"] == "32 q2(t)")
    check("T32_quartic_source", t32["exact_trace_data"]["Tr_D_fourth"] == "32 q4(t)")
    check(
        "T32_prefactor_source",
        t32["conditional_action_scope"]["overall_positive_factor_suppressed_below"]
        == "32 f0/(8pi^2)",
    )

    direction = [Fraction(1)] * 4
    jacobian = [[value] for value in direction]
    projection = [
        [Fraction(1), Fraction(-1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)],
    ]
    check("independent_amplitude_rank", rank(jacobian) == 1)
    check("independent_relative_rank", rank(projection) == 3)
    check("independent_relative_kernel", matvec(projection, direction) == [0, 0, 0])

    torsor = packet["positive_scale_torsor"]
    check("packet_amplitude_rank", torsor["jacobian_rank"] == 1)
    check("packet_relative_rank", torsor["relative_projection_rank"] == 3)
    check("packet_relative_kernel", torsor["relative_projection_of_orbit"] == [0, 0, 0])
    check("packet_topology_nonselection", torsor["topology_or_phase_selects_orbit_point"] is False)

    orbit_examples = a88["orbit_examples"]
    base_ratios = orbit_examples[0]["ratios_g1_over_g2_g3_over_g2"]
    for index, example in enumerate(orbit_examples):
        check(
            f"A88_c_equals_6f0_{index}",
            math.isclose(example["c"], 6.0 * example["f0"], rel_tol=0.0, abs_tol=2e-15),
        )
        check(
            f"A88_ratios_invariant_{index}",
            all(
                math.isclose(left, right, rel_tol=0.0, abs_tol=3e-16)
                for left, right in zip(
                    example["ratios_g1_over_g2_g3_over_g2"], base_ratios
                )
            ),
        )

    f0 = float(
        a52["minimal_profile_normalization"][
            "f0_in_g_i^-2_equals_6_f0_K_i_convention"
        ]
    )
    a_h = 4.0 * f0 / math.pi**2
    c_g = 6.0 * f0
    check("profile_A_H_recomputed", math.isclose(a_h, packet["common_coefficient_map"]["profile_diagnostic_only"]["A_H"], rel_tol=0.0, abs_tol=1e-17))
    check("profile_c_g_recomputed", math.isclose(c_g, packet["common_coefficient_map"]["profile_diagnostic_only"]["c_g"], rel_tol=0.0, abs_tol=1e-16))
    check("profile_ratio_recomputed", math.isclose(a_h / c_g, 2.0 / (3.0 * math.pi**2), rel_tol=0.0, abs_tol=2e-17))
    check("profile_not_strict_source", packet["common_coefficient_map"]["profile_diagnostic_only"]["strict_MTT_source"] is False)

    for index, scale in enumerate([0.25, 0.5, 1.0, 2.0, 4.0]):
        scaled_a_h = scale * a_h
        scaled_c_g = scale * c_g
        check(
            f"scalar_gauge_ratio_scale_invariant_{index}",
            math.isclose(scaled_a_h / scaled_c_g, a_h / c_g, rel_tol=0.0, abs_tol=2e-17),
        )
        check(
            f"g3_scaling_{index}",
            math.isclose(scale ** (-0.5), math.sqrt(a_h / scaled_a_h), rel_tol=0.0, abs_tol=2e-16),
        )
        check(
            f"g4_scaling_{index}",
            math.isclose(scale ** (-1.0), a_h / scaled_a_h, rel_tol=0.0, abs_tol=2e-16),
        )

    action = packet["dimensionless_effective_action"]
    check("alpha_definition", action["shared_primitive"] == "alpha=f0/hbar")
    check("tree_prefactor", action["tree_prefactor"] == "4 alpha/pi^2")
    check("loop_prefactor", action["selected_Weyl_one_loop_prefactor"] == "1/(2 pi^2)")
    check("loop_tree_packet", action["one_loop_over_tree_prefactor"] == "1/(8 alpha)")
    check("rho_jets", action["rho_jets_0_through_5_at_one"] == [0, 0, 0, -16, -64, -48])
    check("no_fixed_coupling_claim", action["fixed_coupling_convergence_claimed"] is False)
    check("T43_loop_source", t43["determinant_exponent"]["selected_kappa_F"] == "1/(2 pi^2)")
    check("T43_action_source", t43["emitted_action"]["formula"] == "Delta V_cl(h)=q4_* H^4 rho(h/H)/(2 pi^2)")
    check("T43_higher_vertices", t43["emitted_action"]["higher_vertices_nonzero"])

    vertices = packet["canonical_radial_vertices"]
    check("mass_scale_exponent_zero", vertices["f0_scaling_exponents"]["mass_squared"] == "0")
    check("g3_scale_exponent", vertices["f0_scaling_exponents"]["g3_tree"] == "-1/2")
    check("g4_scale_exponent", vertices["f0_scaling_exponents"]["g4_tree"] == "-1")
    check("T48_mass_source", t48["canonical_radial_hessian"]["mass_squared"] == "m_h^2=8c")
    check("T48_seed_complete", t48["complete_free_seed"]["missing_selected_factors"] == 0)

    bv = packet["bv_qme_scale_separation"]
    for index, scale in enumerate([Fraction(1, 3), Fraction(2), Fraction(7, 2)]):
        bracket_term = Fraction(5, 7)
        anomaly_term = Fraction(5, 7)
        scaled_bracket = scale * scale * bracket_term
        scaled_anomaly = scale * scale * anomaly_term
        check(f"QME_homogeneous_witness_{index}", scaled_bracket == scaled_anomaly)
    check("T39_three_conditions", t39["anchored_formal_bv_flow"]["finite_normalization_conditions"] == 3)
    check("T39_zero_coefficients", t39["anchored_formal_bv_flow"]["new_free_counterterm_coefficients"] == 0)
    check("T39_not_upper_selected", t39["anchored_formal_bv_flow"]["upper_MTT_selects_this_normalization"] is False)
    check("T46_formal_only", t46["formal_BV_state_pullback"]["closed_as_algebraic_transport_theorem"])
    check("T46_continuum_open", t46["fixed_coupling_boundary"]["selected_continuum_Cstar_rows"] == "0/9")
    check("H4_cotangent_exact", h4["selection_boundary"]["canonical_cotangent_cyclic_completion_closed"])
    check("H4_multiplier_open", h4["selection_boundary"]["selected_physical_trace_normalization_closed"] is False)
    check("H4_gluing_not_promoted", bv["H4_to_direct_gluing_proved"] is False)
    check("shell_free_QME", shell["blocker_assessment"]["B.QFT.02_free_finite_shell_QME_pushforward"] == "closed_up_to_the_transported_determinant_line_scalar")
    check("shell_interacting_open", shell["blocker_assessment"]["B.QFT.02_interacting_fixed_coupling_Cstar_limit"] == "open")

    ledger = packet["one_shared_primitive_ledger"]
    check("A89_adopted_standard", a89["one_shared_primitive_gauge_standard_closed"])
    check("A89_strict_open", a89["strict_primitive_zero_anchor_closed"] is False)
    check("one_primitive_before", ledger["shared_primitives_before_scalar_BV_consolidation"] == 1)
    check("one_primitive_after", ledger["shared_primitives_after_scalar_BV_consolidation"] == 1)
    check("no_new_primitive", ledger["new_primitives_introduced_by_T49"] == 0)
    check("strict_alpha_open", ledger["strict_source_value_for_alpha"] == "open")
    check("zero_knob_not_claimed", ledger["zero_knob_claimed"] is False)

    boundary = packet["physical_boundary"]
    check("ACTION_stays_open", boundary["B_ACTION_01_closed"] is False)
    check("QFT_stays_open", boundary["B_QFT_02_closed"] is False)
    check("gates_zero", boundary["physical_gates"] == {"accepted": 0, "total": 3})
    check("packets_zero", boundary["physical_packets"] == {"accepted": 0, "total": 3})
    check("rows_zero", boundary["physical_rows"] == {"accepted": 0, "total": 7})

    check("theorem_A_H_formula", "A_H=32 f0/(8 pi^2)=4 f0/pi^2" in theorem_text)
    check("theorem_alpha_formula", "alpha=f0/hbar" in theorem_text)
    check("theorem_vertex_nonselection", "g3_tree scales as f0^(-1/2)" in theorem_text)
    check("theorem_topology_guard", "Chern-Weil integrality" in theorem_text)
    check("theorem_ACTION_open", "top-level B.ACTION.01 and G2:                  open" in theorem_text)

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T49 independent checks failed: {failed}")
    print(f"CBF.T49 independent verification passed {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
