#!/usr/bin/env python3
"""Independently verify the exact CBF.T42 packet."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "shared_circle_morse_bott_rank_four.packet.json"
SOURCE_LOCK = ROOT / "shared_circle_morse_bott_rank_four_source_lock.json"
SCHEMA = ROOT / "shared_circle_morse_bott_rank_four_contract.schema.json"
THEOREM = ROOT / "SharedCircleMorseBottRadialActionAndRankFourDeterminantLiftTheorem_v1.md"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T41_PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"
Q79_ACTION_PACKET = (
    ROOT
    / "../20 Mathematical Language Discovery Program - Closure Dynamics"
    / "q79_shared_circle_closure_dynamics_source.packet.json"
)
SHARED_LINE_PACKET = (
    ROOT
    / "../20 Mathematical Language Discovery Program"
    / "q79_universal_shared_line_intertwiner.packet.json"
)


Matrix = list[list[Fraction]]
Series = list[Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def eye(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def block_diagonal(*blocks: Matrix) -> Matrix:
    rows = sum(len(block) for block in blocks)
    columns = sum(len(block[0]) for block in blocks)
    result = zeros(rows, columns)
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row_index, row in enumerate(block):
            for column_index, value in enumerate(row):
                result[row_offset + row_index][column_offset + column_index] = value
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def matrix_rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [entry / pivot_value for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
    return pivot_row


def parse_matrix(matrix: list[list[str]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in matrix]


def parse_series(series: list[str]) -> Series:
    return [Fraction(value) for value in series]


def series_mul(left: Series, right: Series) -> Series:
    order = len(left) - 1
    result = [Fraction(0) for _ in left]
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            degree = left_degree + right_degree
            if degree <= order:
                result[degree] += left_value * right_value
    return result


def series_exp(series: Series) -> Series:
    assert series[0] == 0
    result = [Fraction(0) for _ in series]
    result[0] = Fraction(1)
    for degree in range(1, len(series)):
        result[degree] = sum(
            index * series[index] * result[degree - index]
            for index in range(1, degree + 1)
        ) / degree
    return result


def independent_rho_series(order: int) -> Series:
    x = [Fraction(1), Fraction(1)] + [Fraction(0)] * (order - 1)
    x2 = series_mul(x, x)
    x4 = series_mul(x2, x2)
    log_x2 = [Fraction(0)] + [
        Fraction(2 * ((-1) ** (degree + 1)), degree)
        for degree in range(1, order + 1)
    ]
    bracket = [-value for value in log_x2]
    bracket[0] += Fraction(3, 2)
    main = series_mul(x4, bracket)
    return [
        main[index]
        - 2 * x2[index]
        + (Fraction(1, 2) if index == 0 else Fraction(0))
        for index in range(order + 1)
    ]


def derivative_values(series: Series, through: int) -> list[Fraction]:
    return [math.factorial(order) * series[order] for order in range(through + 1)]


def permutation_matrix(permutation: tuple[int, ...]) -> Matrix:
    matrix = zeros(len(permutation), len(permutation))
    for row, column in enumerate(permutation):
        matrix[row][column] = Fraction(1)
    return matrix


def main() -> None:
    packet = load_json(PACKET)
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    t41 = load_json(T41_PACKET)
    q79_action = load_json(Q79_ACTION_PACKET)
    shared_line = load_json(SHARED_LINE_PACKET)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        check(
            f"locked_source_{index:02d}",
            path.is_file() and sha256(path) == source["sha256"],
        )

    provenance = packet["source_provenance"]
    check("source_lock_hash", provenance["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("schema_hash", provenance["contract_schema_sha256"] == sha256(SCHEMA))
    check("theorem_hash", provenance["theorem_sha256"] == sha256(THEOREM))
    check("handoff_id", provenance["handoff_id"] == source_lock["handoff_id"])
    check("kernel_hash", provenance["kernel_model_sha256"] == source_lock["kernel_model_sha256"])
    check("source_root_hash", provenance["constructed_source_root_sha256"] == canonical_hash(provenance["source_root_payload"]))
    check("all_source_hashes", provenance["source_hashes_match"])

    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("packet_claim", packet["claim_id"] == schema["properties"]["claim_id"]["const"])
    check("schema_closed", schema["additionalProperties"] is False)
    check("all_required_fields", all(field in packet for field in schema["required"]))
    check("builder_passed", packet["check_summary"]["failed"] == [])
    check("builder_count", packet["check_summary"]["passed"] == packet["check_summary"]["total"])

    average = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    zero3 = zeros(3, 3)
    identity3 = eye(3)
    expected_p = block_diagonal(average, average)
    expected_q = subtract(eye(6), expected_p)
    expected_j = [
        [Fraction(0)] * 3 + [-entry for entry in row] for row in identity3
    ] + [
        row + [Fraction(0)] * 3 for row in identity3
    ]
    expected_e = block_diagonal(average, zero3)
    expected_t = block_diagonal(zero3, average)

    carrier = packet["q79_carrier"]
    p_matrix = parse_matrix(carrier["P"])
    q_matrix = parse_matrix(carrier["Q"])
    j_matrix = parse_matrix(carrier["J_DE"])
    e_matrix = parse_matrix(carrier["radial_basepoint_projector_E"])
    t_matrix = parse_matrix(carrier["circle_tangent_projector_T"])

    check("P_exact", p_matrix == expected_p)
    check("Q_exact", q_matrix == expected_q)
    check("J_exact", j_matrix == expected_j)
    check("E_exact", e_matrix == expected_e)
    check("T_exact", t_matrix == expected_t)
    check("P_idempotent", matmul(p_matrix, p_matrix) == p_matrix)
    check("Q_idempotent", matmul(q_matrix, q_matrix) == q_matrix)
    check("P_Q_zero", matmul(p_matrix, q_matrix) == zeros(6, 6))
    check("P_plus_Q", add(p_matrix, q_matrix) == eye(6))
    check("E_plus_T", add(e_matrix, t_matrix) == p_matrix)
    check("rank_P", matrix_rank(p_matrix) == carrier["rank_P"] == 2)
    check("rank_Q", matrix_rank(q_matrix) == carrier["rank_Q"] == 4)
    check("rank_E", matrix_rank(e_matrix) == carrier["rank_E"] == 1)
    check("rank_T", matrix_rank(t_matrix) == carrier["rank_T"] == 1)
    check("J_skew", transpose(j_matrix) == scale(Fraction(-1), j_matrix))
    check("J_square", matmul(j_matrix, j_matrix) == scale(Fraction(-1), eye(6)))
    check("J_P", matmul(j_matrix, p_matrix) == matmul(p_matrix, j_matrix))
    check("J_Q", matmul(j_matrix, q_matrix) == matmul(q_matrix, j_matrix))
    check("source_P", p_matrix == parse_matrix(q79_action["finite_source_data"]["tangent_or_invariant_projector_P"]))
    check("source_Q", q_matrix == parse_matrix(q79_action["finite_source_data"]["normal_or_positive_Hessian_projector_Q"]))
    check("source_J", j_matrix == parse_matrix(q79_action["finite_source_data"]["shared_quarter_turn_JDE"]))

    for index, permutation in enumerate(itertools.permutations(range(3)), start=1):
        action = block_diagonal(
            permutation_matrix(permutation), permutation_matrix(permutation)
        )
        check(f"S3_{index}_P", matmul(action, p_matrix) == matmul(p_matrix, action))
        check(f"S3_{index}_Q", matmul(action, q_matrix) == matmul(q_matrix, action))
        check(f"S3_{index}_J", matmul(action, j_matrix) == matmul(j_matrix, action))

    normalized_hessian = parse_matrix(packet["upper_action"]["normalized_vacuum_hessian"])
    check("Hessian_formula", normalized_hessian == scale(Fraction(8), subtract(eye(6), t_matrix)))
    check("Hessian_split", normalized_hessian == scale(Fraction(8), add(e_matrix, q_matrix)))
    check("Hessian_rank", matrix_rank(normalized_hessian) == 5)
    check("one_zero_mode", packet["shared_circle_vacuum"]["circle_tangent_is_only_Hessian_zero_mode"])
    check("alpha_equation", packet["upper_action"]["uniqueness_equation"] == "2 alpha=8")
    check("alpha_four", Fraction(packet["upper_action"]["unique_alpha"]) == 4)
    check("normal_rank_four", packet["shared_circle_vacuum"]["q79_strain_normal_rank"] == 4)
    check("vacuum_circle", packet["shared_circle_vacuum"]["minimum_set_is_one_shared_circle_orbit"])
    check("circle_not_physical_gauge", not packet["shared_circle_vacuum"]["shared_circle_is_declared_physical_gauge_orbit"])

    rho = independent_rho_series(10)
    log_a = [coefficient / 2 for coefficient in rho]
    a_series = series_exp(log_a)
    determinant = packet["determinant_lift"]
    check("rho_series", parse_series(determinant["rho_series_about_x1_through_order10"]) == rho)
    check("rho_jets", parse_series(determinant["rho_jets_at_x1_through_order5"]) == derivative_values(rho, 5))
    check("rho_expected", derivative_values(rho, 5) == [Fraction(0), Fraction(0), Fraction(0), Fraction(-16), Fraction(-64), Fraction(-48)])
    check("log_a_series", parse_series(determinant["log_a_series_about_x1_through_order10"]) == log_a)
    check("a_series", parse_series(determinant["a_series_about_x1_through_order10"]) == a_series)
    check("a_jets", parse_series(determinant["a_jets_at_x1_through_order5"]) == derivative_values(a_series, 5))
    check("a_value", a_series[0] == 1)
    check("a_slope", a_series[1] == 0)
    check("a_hessian", a_series[2] == 0)
    check("a_cubic", a_series[3] == Fraction(-4, 3))
    check("a_quartic", a_series[4] == Fraction(-4, 3))
    check("a_quintic", a_series[5] == Fraction(-1, 5))
    check("rank_four", determinant["rank"] == 4)
    check("rank_four_factor", Fraction(determinant["rank"], 2) * Fraction(1, 2) == 1)
    check("full_rho", determinant["full_T39_remainder_emitted"])
    check("target_informed", determinant["determinant_lift_is_target_informed"])
    check("not_operator_equivalence", not determinant["determinant_equivalence_implies_operator_equivalence"])
    check("source_rho", packet["radial_source"]["T39_remainder"] == t39["T35_pointed_execution"]["normalized_matched_remainder"])
    check("source_tree", packet["radial_source"]["T38_source_copy_exact"])

    projection = packet["radial_projection"]
    check("zero_section_invariant", projection["zero_section_is_gradient_invariant"])
    check("tree_restriction", projection["action_restriction"] == "S_up|Qw=0=q4_*(h^2-H^2)^2")
    check("repair_restriction", projection["projected_repair_on_zero_section"] == "Dp(-grad S_up)=4 q4_* h(H^2-h^2)")
    check("fixed_map", projection["fixed_point_map"] == "p(w_*)=H")
    check("pointed_square", projection["pointed_vector_field_square"] == "Dp X_up(w_*)=X_rad(H)=0")
    check("tangent_square", projection["pointed_tangent_square"] == "Dp Hess(S_up)(w_*)=kappa Dp")
    check("no_global_claim", not projection["global_off_zero_section_intertwining_claimed"])

    pointed = packet["pointed_intertwiner"]
    check("pointed_rho_zero_two", pointed["rho_zero_two_jet"])
    check("pointed_higher", pointed["nonlinear_quantum_vertices_retained"])
    check("model_fixed", pointed["fixed_point_square_closed_in_model"])
    check("model_tangent", pointed["tangent_generator_square_closed_in_model"])
    check("model_pushforward", pointed["action_pushforward_closed_in_model"])
    check("model_root", pointed["one_constructed_root_for_model"] == provenance["constructed_source_root_sha256"])

    gates = packet["gate_ledger"]
    check("finite_G0", gates["G0_finite_determinant_equivalent_model"]["closed"])
    check("physical_G0", not gates["G0_selected_physical_source"]["closed"])
    check("finite_G1", gates["G1_finite_Euclidean_tangent_isometry"]["closed"])
    check("physical_G1", not gates["G1_physical_tangent_pairing"]["closed"])
    check("finite_G2", gates["G2_finite_normalized_Gaussian_BV_pushforward"]["closed"])
    check("physical_G2", not gates["G2_selected_interacting_state_BV"]["closed"])
    check("physical_gates", gates["physical_gluing_gates_closed"] == 0 and gates["physical_gluing_gates_total"] == 3)
    check("packets", gates["physical_packets_accepted"] == 0 and gates["physical_packets_total"] == 3)
    check("rows", gates["physical_rows_accepted"] == 0 and gates["physical_rows_total"] == 7)
    check("T41_counters", gates["physical_packets_accepted"] == t41["physical_packets_accepted"] and gates["physical_rows_accepted"] == t41["physical_rows_accepted"])

    parameters = packet["parameter_ledger"]
    check("no_fits", parameters["new_fitted_parameters"] == 0)
    check("no_observed", parameters["new_observed_inputs"] == 0)
    check("no_continuous", parameters["new_continuous_physical_parameters"] == 0)
    check("coefficient_removed", parameters["candidate_coefficients_before_equal_stiffness"] == 1 and parameters["candidate_coefficients_after_equal_stiffness"] == 0)
    check("source_profile_open", not parameters["determinant_profile_selected_upstream"])

    boundary = packet["physical_boundary"]
    check("internal_root", boundary["finite_model_source_root_is_internally_single"])
    check("upstream_root_open", not boundary["constructed_root_is_selected_upstream_root"])
    check("line_map_open", not boundary["T34_radial_line_equals_q79_RanP_parallel_line"])
    check("normal_block_open", not boundary["actual_physical_q79_normal_block_emitted"])
    check("operator_map_open", not boundary["actual_operator_intertwiner_emitted"])
    check("density_open", not boundary["physical_density_and_BV_cycle_emitted"])
    check("Lorentz_open", not boundary["Lorentzian_domain_and_statistics_emitted"])
    check("state_open", not boundary["selected_interacting_state_emitted"])
    check("B_ACTION_open", not boundary["B_ACTION_01_closed"])
    check("B_QFT_open", not boundary["B_QFT_02_closed"])
    check("operator_equation", boundary["next_operator_equation"] == "(1/2) log det(K_phys(h) K_phys(H)^-1)=rho(h/H)")
    check("equation_not_sufficient", not boundary["scalar_determinant_equation_is_sufficient_for_operator_equivalence"])

    automorphisms = packet["automorphism_transfer"]
    check("shared_line_source", automorphisms["universal_shared_line_source_present"] == shared_line["checks"]["same_scalar_line_holonomy_commutes_with_every_CLN_projector"])
    check("physical_line_open", not automorphisms["physical_parallel_Higgs_line_map_present"])

    check("theorem_claim", "**Claim:** CBF.T42" in theorem_text)
    check("theorem_action", "S_up(w)" in theorem_text and "a(x)=exp(rho(x)/2)" in theorem_text)
    check("theorem_rank_four", "rank(Q)=4" in theorem_text)
    check("theorem_pushforward", "=epsilon rho(h/H)" in theorem_text)
    check(
        "theorem_right_inverse",
        "constructive" in theorem_text and "right inverse" in theorem_text,
    )
    check("theorem_guard", "not a physical source theorem" in theorem_text)
    check("theorem_equation", "K_phys(h)K_phys(H)^-1" in theorem_text)

    failed = sorted(name for name, passed in checks.items() if not passed)
    print(f"independent checks: {len(checks) - len(failed)}/{len(checks)}")
    if failed:
        raise SystemExit("failed checks: " + ", ".join(failed))


if __name__ == "__main__":
    main()
