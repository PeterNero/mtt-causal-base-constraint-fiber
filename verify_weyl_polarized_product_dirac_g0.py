#!/usr/bin/env python3
"""Independent verifier for CBF.T43; does not import the builder."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "weyl_polarized_product_dirac_g0.packet.json"
SOURCE_LOCK = ROOT / "weyl_polarized_product_dirac_g0_source_lock.json"
SCHEMA = ROOT / "weyl_polarized_product_dirac_g0_contract.schema.json"
THEOREM = ROOT / "WeylPolarizedProductDiracOneLoopPushforwardAndDirectG0SourceTheorem_v1.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [a + b for a, b in zip(left, right)]


def subtract(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [a - b for a, b in zip(left, right)]


def scale(value: Fraction, series: list[Fraction]) -> list[Fraction]:
    return [value * entry for entry in series]


def multiply(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    order = min(len(left), len(right)) - 1
    result = [Fraction(0) for _ in range(order + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= order:
                result[i + j] += a * b
    return result


def xpower(power: int, order: int) -> list[Fraction]:
    result = [Fraction(0) for _ in range(order + 1)]
    for degree in range(min(power, order) + 1):
        result[degree] = Fraction(math.comb(power, degree))
    return result


def raw_seed(order: int) -> list[Fraction]:
    log_x2 = [Fraction(0)] + [
        2 * Fraction((-1) ** (degree + 1), degree)
        for degree in range(1, order + 1)
    ]
    return scale(Fraction(-1), multiply(xpower(4, order), log_x2))


def derivatives(series: list[Fraction], through: int) -> list[Fraction]:
    return [math.factorial(index) * series[index] for index in range(through + 1)]


def solve(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    work = [row[:] + [value] for row, value in zip(matrix, rhs)]
    for column in range(len(work)):
        pivot = next(index for index in range(column, len(work)) if work[index][column])
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(len(work)):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return [row[-1] for row in work]


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def qadd(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return left[0] + right[0], left[1] + right[1]


def qmul(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def qpow(value: tuple[Fraction, Fraction], power: int) -> tuple[Fraction, Fraction]:
    result = Fraction(1), Fraction(0)
    for _ in range(power):
        result = qmul(result, value)
    return result


def parse_series(values: list[str]) -> list[Fraction]:
    return [Fraction(value) for value in values]


def parse_q(payload: dict[str, str]) -> tuple[Fraction, Fraction]:
    return Fraction(payload["rational"]), Fraction(payload["sqrt13"])


def main() -> None:
    packet = load(PACKET)
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    t23 = load(ROOT / "physical_yukawa_hessian.packet.json")
    t25 = load(ROOT / "direct_finite_source_continuum.packet.json")
    t30 = load(ROOT / "ko6_fermionic_determinant_value_selection.packet.json")
    t34 = load(ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json")
    t35 = load(ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json")
    t39 = load(ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json")
    t41 = load(ROOT / "cotangent_lifted_local_formal_projection.packet.json")
    t42 = load(ROOT / "shared_circle_morse_bott_rank_four.packet.json")
    qm = load(ROOT / "../mtt-qm-source-proof/certificates/q79_continuum_sm_classical_bv_composition.certificate.json")
    theorem_text = THEOREM.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        if name in checks:
            raise AssertionError(f"duplicate check: {name}")
        checks[name] = bool(condition)

    check("packet_schema", packet["schema"] == "boe.mtt.weyl-polarized-product-dirac-g0.v1")
    check("claim_id", packet["claim_id"] == "CBF.T43")
    check("source_lock_schema", source_lock["schema"] == "boe.mtt.weyl-polarized-product-dirac-g0-source-lock.v1")
    check("schema_const", schema["properties"]["claim_id"]["const"] == "CBF.T43")
    check("schema_keys", set(packet) == set(schema["required"]))
    check("builder_checks_all_pass", all(packet["checks"].values()))
    check("builder_summary", packet["check_summary"]["failed"] == [] and packet["check_summary"]["passed"] == packet["check_summary"]["total"])

    all_sources = source_lock["construction_sources"] + source_lock["comparison_sources"]
    for index, source in enumerate(all_sources, start=1):
        path = (ROOT / source["path"]).resolve()
        check(f"source_{index:02d}_exists", path.is_file())
        check(f"source_{index:02d}_hash", digest(path) == source["sha256"])

    provenance = packet["source_provenance"]
    check("source_lock_hash", provenance["source_lock_sha256"] == digest(SOURCE_LOCK))
    check("schema_hash", provenance["contract_schema_sha256"] == digest(SCHEMA))
    check("theorem_hash", provenance["theorem_sha256"] == digest(THEOREM))
    check("all_hashes", provenance["all_source_hashes_match"])
    check("construction_source_count", provenance["construction_sources"] == len(source_lock["construction_sources"]))
    check("comparison_source_count", provenance["comparison_sources"] == len(source_lock["comparison_sources"]))
    check("comparison_excluded", provenance["comparison_sources_excluded_from_root"])
    check("root_recomputed", provenance["construction_root_sha256"] == canonical_hash(provenance["construction_root_payload"]))
    root_payload_text = json.dumps(provenance["construction_root_payload"], sort_keys=True)
    check("root_excludes_T35_hash", digest(ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json") not in provenance["construction_root_payload"]["construction_source_hashes"])
    check("root_excludes_T39_hash", digest(ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json") not in provenance["construction_root_payload"]["construction_source_hashes"])
    check("root_excludes_T42_hash", digest(ROOT / "shared_circle_morse_bott_rank_four.packet.json") not in provenance["construction_root_payload"]["construction_source_hashes"])
    check("root_has_no_rho_formula", "rho(x)=" not in root_payload_text)

    carrier = packet["carrier_ledger"]
    qm_carrier = qm["carrier_ledger"]
    check("particle_48", carrier["particle_carrier_dimension"] == t23["carrier_and_incidence"]["particle_dimension"] == 48)
    check("KO6_96", carrier["KO6_real_completion_dimension"] == t23["carrier_and_incidence"]["KO6_dimension"] == 96)
    check("Weyl_48", carrier["three_family_left_Weyl_internal_dimension"] == qm_carrier["three_family_left_Weyl_internal_dimension"] == 48)
    check("spin_2", carrier["left_Weyl_spin_dimension"] == qm_carrier["left_Weyl_spin_dimension"] == 2)
    check("offshell_96", carrier["continuum_left_Weyl_component_dimension"] == 96)
    check("offshell_product", carrier["off_shell_components_equal_Weyl_times_spin"] == 96)
    check("KO6_not_copy", carrier["KO6_completion_is_not_an_independent_field_copy"])
    check("q79_rank_not_count", carrier["q79_rank_is_not_particle_multiplicity"])
    check("branch_sum", carrier["branch_multiplicity_sum"] == 48)
    check("branch_multiplicities", all(value == 16 for value in carrier["branch_multiplicities"].values()))

    exponent = packet["determinant_exponent"]
    per_weyl = Fraction(1, 32)
    per_dirac = Fraction(1, 16)
    check("Weyl_spin_trace", exponent["left_Weyl_spin_trace"] == 2)
    check("square_root_exponent", Fraction(exponent["squared_operator_exponent"]) == Fraction(1, 2))
    check("Weyl_branch_factor", 16 * per_weyl == Fraction(1, 2))
    check("Dirac_branch_factor", 16 * per_dirac == 1)
    check("selected_kappa", exponent["selected_kappa_F"] == "1/(2 pi^2)")
    check("selected_kappa_exact", Fraction(exponent["selected_kappa_F_times_pi_squared"]) == Fraction(1, 2))
    check("rejected_kappa", exponent["rejected_doubled_candidate"] == "1/pi^2")
    check("phase_no_doubling", not exponent["global_phase_can_change_local_even_multiplicity"])

    sigma_payloads = t30["dimensionless_branch_values"]["ordered_by_response_eigenvalue"]
    q4 = Fraction(0), Fraction(0)
    for key in ["-4", "-2", "2"]:
        value = parse_q(sigma_payloads[key]["exact_coefficients"])
        q4 = qadd(q4, qpow(value, 4))
    check("q4_exact", q4 == (Fraction(356, 27), Fraction(25, 27)))
    check("q4_packet", parse_q(packet["exact_finite_trace"]["q4_star"]["exact_coefficients"]) == q4)
    check("q4_T35", packet["exact_finite_trace"]["q4_matches_T35"])
    check("one_loop_formula", "1/(2 pi^2)" not in packet["exact_finite_trace"]["flat_one_loop_formula"] and "/(2 pi^2)" in packet["exact_finite_trace"]["flat_one_loop_formula"])
    check("no_observed_trace", not packet["exact_finite_trace"]["observed_values_used"])

    order = 10
    raw = raw_seed(order)
    raw_jets = derivatives(raw, 5)
    matrix = [
        [Fraction(1), Fraction(1), Fraction(1)],
        [Fraction(0), Fraction(2), Fraction(4)],
        [Fraction(0), Fraction(2), Fraction(12)],
    ]
    coefficients = solve(matrix, raw_jets[:3])
    polynomial = [Fraction(0) for _ in range(order + 1)]
    for coefficient, power in zip(coefficients, [0, 2, 4]):
        polynomial = add(polynomial, scale(coefficient, xpower(power, order)))
    remainder = subtract(raw, polynomial)
    remainder_jets = derivatives(remainder, 5)
    expected_jets = [Fraction(0), Fraction(0), Fraction(0), Fraction(-16), Fraction(-64), Fraction(-48)]
    renorm = packet["pointed_renormalization"]
    check("raw_series", parse_series(renorm["raw_series_about_x1_through_order10"]) == raw)
    check("raw_jets", parse_series(renorm["raw_jets_at_x1_through_order5"]) == raw_jets)
    check("raw_anchor_jets", raw_jets[:3] == [0, -2, -14])
    check("matrix_determinant", determinant3(matrix) == 16 == Fraction(renorm["jet_matrix_determinant"]))
    check("coefficients", coefficients == [Fraction(-1, 2), Fraction(2), Fraction(-3, 2)])
    check("packet_coefficients", parse_series(renorm["interpolation_coefficients_c0_c2_c4"]) == coefficients)
    check("remainder_series", parse_series(renorm["remainder_series_about_x1_through_order10"]) == remainder)
    check("remainder_jets", parse_series(renorm["remainder_jets_at_x1_through_order5"]) == expected_jets == remainder_jets)
    check("rho_output", renorm["rho_is_output_not_input"])
    check("unique_representative", renorm["unique_zero_two_jet_representative"])
    check("scheme_cancels", renorm["scheme_scale_and_L4_cancel"])

    emitted = packet["emitted_action"]
    check("emitted_amplitude", emitted["exact_amplitude"] == "(356+25sqrt(13)) H^4/(54 pi^2)")
    check("third_vertex", emitted["third_vertex_shift"] == "-8 q4_* H/pi^2")
    check("fourth_vertex", emitted["fourth_vertex_shift"] == "-32 q4_*/pi^2")
    check("fifth_vertex", emitted["fifth_vertex_shift"] == "-24 q4_*/(pi^2 H)")
    check("fixed_point", emitted["fixed_point_preserved"])
    check("Hessian", emitted["radial_Hessian_preserved"])
    check("higher_vertices", emitted["higher_vertices_nonzero"])
    check("T35_shape", emitted["matches_T35_shape"] and renorm["remainder"] == t35["closure_jet_matching"]["normalized_shape"])
    check("T39_shape", emitted["matches_T39_shape_and_jets"] and renorm["remainder"] == t39["T35_pointed_execution"]["normalized_matched_remainder"])

    graph = packet["same_source_graph"]
    check("lineage_edges", graph["all_edges_verified"] and all(graph["verified_edges"].values()))
    check("same_root", graph["direct_operator_and_one_loop_action_share_root"])
    check("comparison_only", graph["T35_T39_T42_used_only_as_output_comparisons"])
    check("HYM_root_open", not graph["physical_q79_HYM_root_identified_with_direct_root"])

    comparison = packet["T42_comparison"]
    check("T42_scalar_match", comparison["normalized_scalar_remainder_matches"])
    check("T42_rank_four", comparison["T42_rank"] == 4)
    check("T42_target_informed", comparison["T42_is_target_informed"] == t42["determinant_lift"]["determinant_lift_is_target_informed"])
    check("T42_operator_guard", not comparison["operators_identified"] and not comparison["correlators_identified"])
    check("T42_count_guard", not comparison["q79_rank_four_counts_physical_particles"])

    gates = packet["gate_ledger"]
    check("direct_local_G0", gates["G0_direct_local_one_loop"]["closed"])
    check("global_G0_open", not gates["G0_global_physical"]["closed"])
    check("HYM_G0_open", not gates["G0_q79_HYM"]["closed"])
    check("G1_open", not gates["G1_physical_tangent_pairing"]["closed"])
    check("G2_open", not gates["G2_selected_interacting_state_BV"]["closed"])
    check("physical_gate_counters", (gates["physical_gluing_gates_closed"], gates["physical_gluing_gates_total"]) == (t41["physical_gluing_gates_closed"], t41["physical_gluing_gates_total"]) == (0, 3))
    check("packet_counters", (gates["physical_packets_accepted"], gates["physical_packets_total"]) == (0, 3))
    check("row_counters", (gates["physical_rows_accepted"], gates["physical_rows_total"]) == (0, 7))

    parameters = packet["parameter_ledger"]
    check("no_observed", parameters["new_observed_inputs"] == 0)
    check("no_fits", parameters["new_fitted_coefficients"] == 0)
    check("no_continuous", parameters["new_continuous_physical_parameters"] == 0)
    check("candidate_reduction", (parameters["local_determinant_normalization_candidates_before"], parameters["local_determinant_normalization_candidates_after"]) == (2, 1))
    check("Weyl_not_fit", not parameters["universal_four_dimensional_Weyl_coefficient_is_a_fit"])
    check("scale_open", not parameters["absolute_SI_scale_selected"])
    check("phase_open", not parameters["global_determinant_phase_selected"])

    boundary = packet["physical_boundary"]
    check("direct_local_closed", boundary["direct_local_flat_one_loop_pushforward_closed"])
    check("Weyl_selected", boundary["Weyl_exponent_selected"])
    check("rho_derived", boundary["normalized_remainder_source_derived"])
    for name in [
        "global_Wick_or_direct_Lorentzian_determinant_closed",
        "determinant_line_orientation_closed",
        "selected_external_BV_operator_domain_closed",
        "q79_HYM_normal_operator_closed",
        "direct_and_q79_HYM_routes_identified",
        "physical_parallel_line_and_metric_closed",
        "selected_interacting_state_BV_closed",
        "RG_and_pole_transport_closed",
        "held_out_observable_closed",
        "B_ACTION_01_closed",
        "B_QFT_02_closed",
        "B_OP_01_closed",
        "B_GEO_01_closed",
    ]:
        check(f"boundary_{name}", not boundary[name])

    check("theorem_claim", "**Claim:** CBF.T43" in theorem_text)
    check("theorem_operator", "D_dir(h)" in theorem_text)
    check("theorem_kappa", "kappa_F=1/(2 pi^2)" in theorem_text)
    check("theorem_interpolant", "I_H f=-1/2+2x^2-(3/2)x^4" in theorem_text)
    check("theorem_rho_output", "not an input" in theorem_text)
    check("theorem_fifth", "rho'''''" in theorem_text)
    check("theorem_HYM_guard", "not a global q79 HYM determinant theorem" in theorem_text)

    failed = sorted(name for name, passed in checks.items() if not passed)
    print(f"independent checks: {len(checks) - len(failed)}/{len(checks)}")
    if failed:
        raise SystemExit("failed checks: " + ", ".join(failed))


if __name__ == "__main__":
    main()
