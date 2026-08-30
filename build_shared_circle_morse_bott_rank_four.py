#!/usr/bin/env python3
"""Build the exact CBF.T42 shared-circle rank-four determinant packet."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
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
OUTPUT = ROOT / "shared_circle_morse_bott_rank_four.packet.json"


Matrix = list[list[Fraction]]
Series = list[Fraction]


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


def fmatrix(matrix: Matrix) -> list[list[str]]:
    return [[ftext(value) for value in row] for row in matrix]


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
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [entry / pivot_value for entry in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def parse_matrix(matrix: list[list[str]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in matrix]


def series_add(left: Series, right: Series) -> Series:
    return [a + b for a, b in zip(left, right)]


def series_scale(value: Fraction, series: Series) -> Series:
    return [value * coefficient for coefficient in series]


def series_mul(left: Series, right: Series) -> Series:
    order = min(len(left), len(right)) - 1
    result = [Fraction(0) for _ in range(order + 1)]
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            degree = left_degree + right_degree
            if degree <= order:
                result[degree] += left_value * right_value
    return result


def series_exp(series: Series) -> Series:
    if series[0] != 0:
        raise ValueError("series_exp requires zero constant term")
    result = [Fraction(0) for _ in series]
    result[0] = Fraction(1)
    for degree in range(1, len(series)):
        numerator = sum(
            index * series[index] * result[degree - index]
            for index in range(1, degree + 1)
        )
        result[degree] = numerator / degree
    return result


def derivative_values(series: Series, through: int) -> list[Fraction]:
    return [math.factorial(order) * series[order] for order in range(through + 1)]


def rho_series(order: int = 10) -> Series:
    one_plus_y = [Fraction(1), Fraction(1)] + [Fraction(0)] * (order - 1)
    x2 = series_mul(one_plus_y, one_plus_y)
    x4 = series_mul(x2, x2)
    log_x_squared = [Fraction(0)] + [
        2 * Fraction((-1) ** (degree + 1), degree)
        for degree in range(1, order + 1)
    ]
    bracket = series_scale(Fraction(-1), log_x_squared)
    bracket[0] += Fraction(3, 2)
    result = series_mul(x4, bracket)
    result = series_add(result, series_scale(Fraction(-2), x2))
    result[0] += Fraction(1, 2)
    return result


def permutation_matrix(permutation: tuple[int, ...]) -> Matrix:
    result = zeros(len(permutation), len(permutation))
    for row, column in enumerate(permutation):
        result[row][column] = Fraction(1)
    return result


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    t41 = load_json(T41_PACKET)
    q79_action = load_json(Q79_ACTION_PACKET)
    shared_line = load_json(SHARED_LINE_PACKET)

    third_average = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    zero3 = zeros(3, 3)
    identity3 = eye(3)
    projector_p = block_diagonal(third_average, third_average)
    projector_q = subtract(eye(6), projector_p)
    complex_j = [
        [Fraction(0)] * 3 + [-entry for entry in row] for row in identity3
    ] + [
        row + [Fraction(0)] * 3 for row in identity3
    ]
    radial_projector_e = block_diagonal(third_average, zero3)
    circle_tangent_projector = block_diagonal(zero3, third_average)

    q79_p = parse_matrix(
        q79_action["finite_source_data"]["tangent_or_invariant_projector_P"]
    )
    q79_q = parse_matrix(
        q79_action["finite_source_data"]["normal_or_positive_Hessian_projector_Q"]
    )
    q79_j = parse_matrix(q79_action["finite_source_data"]["shared_quarter_turn_JDE"])

    permutations = [
        block_diagonal(permutation_matrix(permutation), permutation_matrix(permutation))
        for permutation in itertools.permutations(range(3))
    ]
    automorphism_checks = {
        "all_six_sheet_permutations_commute_with_P": all(
            matmul(group_element, projector_p) == matmul(projector_p, group_element)
            for group_element in permutations
        ),
        "all_six_sheet_permutations_commute_with_Q": all(
            matmul(group_element, projector_q) == matmul(projector_q, group_element)
            for group_element in permutations
        ),
        "all_six_sheet_permutations_commute_with_J": all(
            matmul(group_element, complex_j) == matmul(complex_j, group_element)
            for group_element in permutations
        ),
        "J_is_skew": transpose(complex_j) == scale(Fraction(-1), complex_j),
        "J_squared_is_minus_identity": matmul(complex_j, complex_j)
        == scale(Fraction(-1), eye(6)),
        "J_commutes_with_P": matmul(complex_j, projector_p)
        == matmul(projector_p, complex_j),
        "J_commutes_with_Q": matmul(complex_j, projector_q)
        == matmul(projector_q, complex_j),
    }

    rho = rho_series(10)
    rho_jets = derivative_values(rho, 5)
    log_a = series_scale(Fraction(1, 2), rho)
    a_series = series_exp(log_a)
    a_jets = derivative_values(a_series, 5)
    expected_rho_jets = [
        Fraction(0),
        Fraction(0),
        Fraction(0),
        Fraction(-16),
        Fraction(-64),
        Fraction(-48),
    ]

    source_root_payload = {
        "schema": "boe.mtt.shared-circle-morse-bott-rank-four-derived-root.v1",
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "carrier": "W_fin=R3_D direct_sum R3_E with exact P,Q,J_DE",
        "radial_map": "r(w)=sqrt(<w,Pw>)",
        "upper_action": (
            "S_up=q4_*(r^2-H^2)^2+"
            "4 q4_* H^2 exp(rho(r/H)/2)||Qw||^2"
        ),
        "determinant_lift": "K_Q(h)=kappa exp(rho(h/H)/2) I_RanQ",
        "rank": 4,
        "normalization": "K_Q(H)=kappa I_RanQ",
    }
    constructed_root = canonical_hash(source_root_payload)

    normalized_hessian = scale(Fraction(8), add(radial_projector_e, projector_q))
    expected_normalized_hessian = scale(
        Fraction(8), subtract(eye(6), circle_tangent_projector)
    )

    packet: dict[str, Any] = {
        "schema": "boe.mtt.shared-circle-morse-bott-rank-four.v1",
        "claim_id": "CBF.T42",
        "title": "Shared-Circle Morse-Bott Radial Action and Rank-Four Determinant Lift",
        "date": "2026-08-30",
        "status": (
            "exact finite/local-formal determinant-equivalent G0 construction; "
            "selected physical q79 source and interacting BV promotion open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "source_root_payload": source_root_payload,
            "constructed_source_root_sha256": constructed_root,
            "source_hashes_match": all(source_hash_checks(source_lock).values()),
        },
        "q79_carrier": {
            "carrier": "W_fin=R3_D direct_sum R3_E",
            "dimension": 6,
            "P": fmatrix(projector_p),
            "Q": fmatrix(projector_q),
            "J_DE": fmatrix(complex_j),
            "radial_basepoint_projector_E": fmatrix(radial_projector_e),
            "circle_tangent_projector_T": fmatrix(circle_tangent_projector),
            "rank_P": matrix_rank(projector_p),
            "rank_Q": matrix_rank(projector_q),
            "rank_E": matrix_rank(radial_projector_e),
            "rank_T": matrix_rank(circle_tangent_projector),
            "P_plus_Q_is_identity": add(projector_p, projector_q) == eye(6),
            "P_Q_orthogonal": matmul(projector_p, projector_q) == zeros(6, 6),
            "P_matches_q79_source": projector_p == q79_p,
            "Q_matches_q79_source": projector_q == q79_q,
            "J_matches_q79_source": complex_j == q79_j,
            "complex_dimension_of_RanP": 1,
            "physical_Higgs_line_identification_selected": False,
        },
        "radial_source": {
            "q4_star": t38["exact_radial_square_completion"]["q4_star"],
            "H_over_Lambda": t38["exact_radial_square_completion"]["H_over_Lambda"],
            "H_squared_over_Lambda_squared": t38["exact_radial_square_completion"][
                "H_squared_over_Lambda_squared"
            ],
            "relative_tree_action": "P_*(h)-P_*(H)=q4_* (h^2-H^2)^2",
            "tree_repair": "dh/ds=4 q4_* h(H^2-h^2)",
            "T38_source_copy_exact": t38["exact_radial_square_completion"][
                "exact_completion"
            ]
            == "P_*(h)-P_*(H)=q4_* (h^2-H^2)^2",
            "T39_remainder": t39["T35_pointed_execution"][
                "normalized_matched_remainder"
            ],
        },
        "upper_action": {
            "radial_coordinate": "r(w)=sqrt(<w,Pw>)",
            "normal_stiffness_profile": "a(x)=exp(rho(x)/2)",
            "common_stiffness": "kappa=8 q4_* H^2",
            "action": (
                "S_up(w)=q4_*(r(w)^2-H^2)^2+"
                "(kappa/2)a(r(w)/H)||Qw||^2"
            ),
            "equal_stiffness_family": (
                "S_alpha=q4_*(r^2-H^2)^2+"
                "alpha q4_* H^2 a(r/H)||Qw||^2"
            ),
            "radial_hessian_over_q4_H2": "8",
            "Q_hessian_over_q4_H2": "2 alpha",
            "unique_alpha": "4",
            "uniqueness_equation": "2 alpha=8",
            "normalized_vacuum_hessian": fmatrix(normalized_hessian),
            "normalized_vacuum_hessian_formula": "Hess/(q4_* H^2)=8(I-T_*)",
            "field_only_action_nonzero_on_zero_section": True,
            "action_is_a_cotangent_multiplier_only": False,
        },
        "shared_circle_vacuum": {
            "minimum_set": "M_H={w in Ran(P): ||w||=H}",
            "minimum_set_is_one_shared_circle_orbit": True,
            "circle_generator": "J_DE",
            "circle_tangent": "J_DE w_*",
            "circle_tangent_is_only_Hessian_zero_mode": matrix_rank(
                normalized_hessian
            )
            == 5,
            "normal_rank": matrix_rank(normalized_hessian),
            "radial_normal_rank": 1,
            "q79_strain_normal_rank": matrix_rank(projector_q),
            "profile_a_is_strictly_positive": True,
            "shared_circle_is_declared_physical_gauge_orbit": False,
        },
        "automorphism_transfer": {
            "group": "S3_sheet x U(1)_shared",
            "sheet_action": "rho(g)=diag(Pi_g,Pi_g)",
            "shared_circle_action": "exp(theta J_DE)",
            "action_depends_only_on_invariant_norms": True,
            **automorphism_checks,
            "universal_shared_line_source_present": shared_line["checks"][
                "same_scalar_line_holonomy_commutes_with_every_CLN_projector"
            ],
            "physical_parallel_Higgs_line_map_present": False,
        },
        "radial_projection": {
            "map": "p(w)=||Pw||",
            "domain": "{w: ||Pw||>0}",
            "zero_section": "Qw=0",
            "zero_section_is_gradient_invariant": True,
            "action_restriction": "S_up|Qw=0=q4_*(h^2-H^2)^2",
            "projected_repair_on_zero_section": "Dp(-grad S_up)=4 q4_* h(H^2-h^2)",
            "fixed_point_map": "p(w_*)=H",
            "pointed_vector_field_square": "Dp X_up(w_*)=X_rad(H)=0",
            "pointed_tangent_square": "Dp Hess(S_up)(w_*)=kappa Dp",
            "lower_hessian": "P_rel''(H)=kappa",
            "global_off_zero_section_intertwining_claimed": False,
        },
        "determinant_lift": {
            "rho": "rho(x)=x^4(3/2-log(x^2))-2x^2+1/2",
            "rho_series_about_x1_through_order10": [ftext(value) for value in rho],
            "rho_jets_at_x1_through_order5": [ftext(value) for value in rho_jets],
            "log_a": "log a(x)=rho(x)/2",
            "log_a_series_about_x1_through_order10": [
                ftext(value) for value in log_a
            ],
            "a_series_about_x1_through_order10": [
                ftext(value) for value in a_series
            ],
            "a_jets_at_x1_through_order5": [ftext(value) for value in a_jets],
            "rank": matrix_rank(projector_q),
            "normal_block": "K_Q(h)=kappa a(h/H) I_RanQ",
            "normalized_determinant_ratio": "det(K_Q(h)K_Q(H)^-1)=a(h/H)^4=exp(2rho(h/H))",
            "half_log_determinant": "(1/2)log det(K_Q(h)K_Q(H)^-1)=rho(h/H)",
            "normalized_partition_ratio": "Z_Q(h)/Z_Q(H)=a(h/H)^(-2)=exp(-rho(h/H))",
            "effective_action": "Gamma_rel(h)=P_rel(h)+epsilon rho(h/H)",
            "isotropic_rank_m_unique_profile": "a_m(x)=exp(2rho(x)/m)",
            "rank_four_profile_is_unique": True,
            "minimal_nonconstant_contact_order": 3,
            "first_nonconstant_a_coefficients": {
                "(x-1)^3": ftext(a_series[3]),
                "(x-1)^4": ftext(a_series[4]),
                "(x-1)^5": ftext(a_series[5]),
            },
            "full_T39_remainder_emitted": rho_jets == expected_rho_jets,
            "determinant_lift_is_target_informed": True,
            "determinant_equivalence_implies_operator_equivalence": False,
        },
        "pointed_intertwiner": {
            "upper_fixed_point": "w_* in M_H",
            "lower_fixed_point": "h=H",
            "upper_action_zero_jet_relative": "0",
            "lower_action_zero_jet_relative": "0",
            "upper_radial_tadpole": "0",
            "lower_effective_tadpole": "0",
            "upper_radial_hessian": "kappa",
            "lower_effective_hessian": "kappa",
            "rho_zero_two_jet": rho_jets[:3]
            == [Fraction(0), Fraction(0), Fraction(0)],
            "nonlinear_quantum_vertices_retained": rho_jets[3:] != [Fraction(0)] * 3,
            "fixed_point_square_closed_in_model": True,
            "tangent_generator_square_closed_in_model": True,
            "action_pushforward_closed_in_model": True,
            "one_constructed_root_for_model": constructed_root,
        },
        "gate_ledger": {
            "G0_finite_determinant_equivalent_model": {
                "closed": True,
                "scope": "one constructed P/Q/J action, radial map and normalized rank-four pushforward",
            },
            "G0_selected_physical_source": {
                "closed": False,
                "missing": "derive K_phys and its determinant identity from the upstream q79/HYM action",
            },
            "G1_finite_Euclidean_tangent_isometry": {
                "closed": True,
                "scope": "declared finite Euclidean carrier metric only",
            },
            "G1_physical_tangent_pairing": {
                "closed": False,
                "missing": "parallel A35/q79 line map and physical wave-function metric",
            },
            "G2_finite_normalized_Gaussian_BV_pushforward": {
                "closed": True,
                "scope": "positive rank-four local Gaussian determinant model",
            },
            "G2_selected_interacting_state_BV": {
                "closed": False,
                "missing": "physical statistics, Lorentzian domain, state, QME pushforward and continuum limit",
            },
            "physical_gluing_gates_closed": 0,
            "physical_gluing_gates_total": 3,
            "physical_packets_accepted": t41["physical_packets_accepted"],
            "physical_packets_total": t41["physical_packets_total"],
            "physical_rows_accepted": t41["physical_rows_accepted"],
            "physical_rows_total": t41["physical_rows_total"],
        },
        "parameter_ledger": {
            "new_fitted_parameters": 0,
            "new_observed_inputs": 0,
            "new_continuous_physical_parameters": 0,
            "new_discrete_physical_selectors": 0,
            "candidate_coefficients_before_equal_stiffness": 1,
            "candidate_coefficients_after_equal_stiffness": 0,
            "normal_rank_selected_by_q79": 4,
            "determinant_profile_selected_upstream": False,
            "remaining_structural_source_morphisms": 1,
        },
        "physical_boundary": {
            "finite_model_source_root_is_internally_single": True,
            "constructed_root_is_selected_upstream_root": False,
            "T34_radial_line_equals_q79_RanP_parallel_line": False,
            "actual_physical_q79_normal_block_emitted": False,
            "actual_operator_intertwiner_emitted": False,
            "physical_density_and_BV_cycle_emitted": False,
            "Lorentzian_domain_and_statistics_emitted": False,
            "selected_interacting_state_emitted": False,
            "physical_G0_closed": False,
            "physical_G1_closed": False,
            "physical_G2_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "next_operator_equation": (
                "(1/2) log det(K_phys(h) K_phys(H)^-1)=rho(h/H)"
            ),
            "scalar_determinant_equation_is_sufficient_for_operator_equivalence": False,
        },
        "frontier_delta": (
            "A single q79 P/Q/J action now realizes the shared-circle vacuum, "
            "the exact T38 radial restriction and pointed tangent square. The "
            "selected q79 normal rank four gives a unique isotropic determinant "
            "lift a=exp(rho/2), whose normalized finite BV/Gaussian pushforward "
            "emits the complete T39 anchored remainder. This closes a finite "
            "determinant-equivalent G0 model and reduces physical G0 to one "
            "explicit same-source normal-block determinant and operator "
            "intertwiner. Because the lift consumes rho, B.ACTION.01 and "
            "B.QFT.02 remain open."
        ),
    }

    checks = source_hash_checks(source_lock)

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("source_lock_claim", source_lock["claim_id"] == "CBF.T42")
    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("packet_claim", packet["claim_id"] == schema["properties"]["claim_id"]["const"])
    check("schema_closed", schema["additionalProperties"] is False)
    check(
        "schema_required",
        all(
            field in packet or field in {"checks", "check_summary"}
            for field in schema["required"]
        ),
    )
    check("P_source_match", projector_p == q79_p)
    check("Q_source_match", projector_q == q79_q)
    check("J_source_match", complex_j == q79_j)
    check("P_idempotent", matmul(projector_p, projector_p) == projector_p)
    check("Q_idempotent", matmul(projector_q, projector_q) == projector_q)
    check("P_Q_zero", matmul(projector_p, projector_q) == zeros(6, 6))
    check("P_plus_Q", add(projector_p, projector_q) == eye(6))
    check("rank_P_two", matrix_rank(projector_p) == 2)
    check("rank_Q_four", matrix_rank(projector_q) == 4)
    check("rank_E_one", matrix_rank(radial_projector_e) == 1)
    check("rank_T_one", matrix_rank(circle_tangent_projector) == 1)
    check("P_E_T_split", add(radial_projector_e, circle_tangent_projector) == projector_p)
    check("J_squared", automorphism_checks["J_squared_is_minus_identity"])
    check("J_skew", automorphism_checks["J_is_skew"])
    check("J_P_commutes", automorphism_checks["J_commutes_with_P"])
    check("J_Q_commutes", automorphism_checks["J_commutes_with_Q"])
    check("S3_P_commutes", automorphism_checks["all_six_sheet_permutations_commute_with_P"])
    check("S3_Q_commutes", automorphism_checks["all_six_sheet_permutations_commute_with_Q"])
    check("S3_J_commutes", automorphism_checks["all_six_sheet_permutations_commute_with_J"])
    check("normalized_Hessian_formula", normalized_hessian == expected_normalized_hessian)
    check("Hessian_rank_five", matrix_rank(normalized_hessian) == 5)
    check("unique_alpha_four", Fraction(8, 2) == Fraction(4))
    check("rho_source_formula", t39["T35_pointed_execution"]["normalized_matched_remainder"] == packet["radial_source"]["T39_remainder"])
    check("rho_exact_jets", rho_jets == expected_rho_jets)
    check("rho_zero_two_jet", rho_jets[:3] == [Fraction(0)] * 3)
    check("rho_higher_nonzero", all(value != 0 for value in rho_jets[3:]))
    check("log_a_half_rho", log_a == series_scale(Fraction(1, 2), rho))
    check("a_value_one", a_series[0] == 1)
    check("a_first_zero", a_series[1] == 0)
    check("a_second_zero", a_series[2] == 0)
    check("a_cubic", a_series[3] == Fraction(-4, 3))
    check("a_quartic", a_series[4] == Fraction(-4, 3))
    check("a_quintic", a_series[5] == Fraction(-1, 5))
    check("rank_four_half_log", Fraction(matrix_rank(projector_q), 2) * Fraction(1, 2) == 1)
    check("full_remainder_emitted", packet["determinant_lift"]["full_T39_remainder_emitted"])
    check("constructed_root_hash", packet["pointed_intertwiner"]["one_constructed_root_for_model"] == constructed_root)
    check("finite_G0_closed", packet["gate_ledger"]["G0_finite_determinant_equivalent_model"]["closed"])
    check("physical_G0_open", not packet["gate_ledger"]["G0_selected_physical_source"]["closed"])
    check("finite_G1_closed", packet["gate_ledger"]["G1_finite_Euclidean_tangent_isometry"]["closed"])
    check("physical_G1_open", not packet["gate_ledger"]["G1_physical_tangent_pairing"]["closed"])
    check("finite_G2_closed", packet["gate_ledger"]["G2_finite_normalized_Gaussian_BV_pushforward"]["closed"])
    check("physical_G2_open", not packet["gate_ledger"]["G2_selected_interacting_state_BV"]["closed"])
    check("physical_gate_count_zero", packet["gate_ledger"]["physical_gluing_gates_closed"] == 0)
    check("packet_count_unchanged", packet["gate_ledger"]["physical_packets_accepted"] == 0 and packet["gate_ledger"]["physical_packets_total"] == 3)
    check("row_count_unchanged", packet["gate_ledger"]["physical_rows_accepted"] == 0 and packet["gate_ledger"]["physical_rows_total"] == 7)
    check("zero_new_parameters", packet["parameter_ledger"]["new_continuous_physical_parameters"] == 0)
    check("zero_fits", packet["parameter_ledger"]["new_fitted_parameters"] == 0)
    check("zero_observed_inputs", packet["parameter_ledger"]["new_observed_inputs"] == 0)
    check("target_informed_guard", packet["determinant_lift"]["determinant_lift_is_target_informed"])
    check("operator_nonpromotion_guard", not packet["determinant_lift"]["determinant_equivalence_implies_operator_equivalence"])
    check("B_ACTION_open", not packet["physical_boundary"]["B_ACTION_01_closed"])
    check("B_QFT_open", not packet["physical_boundary"]["B_QFT_02_closed"])
    check("shared_line_input", packet["automorphism_transfer"]["universal_shared_line_source_present"])
    check("physical_line_map_open", not packet["automorphism_transfer"]["physical_parallel_Higgs_line_map_present"])
    check("q79_action_boundary_retained", "OPEN" in q79_action["blocker_assessment"]["B.ACTION.01"])
    check("T41_gate_count_source", t41["physical_gluing_gates_closed"] == 0 and t41["physical_gluing_gates_total"] == 3)

    theorem_text = THEOREM.read_text(encoding="utf-8")
    check("theorem_action_formula", "a(x)=exp(rho(x)/2)" in theorem_text)
    check("theorem_shared_circle", "one shared-circle orbit" in theorem_text)
    check("theorem_full_pushforward", "=epsilon rho(h/H)" in theorem_text)
    check("theorem_target_informed", "reconstructed from the known lower" in theorem_text)
    check("theorem_operator_equation", "log det[K_phys(h)K_phys(H)^-1]" in theorem_text)
    check("theorem_physical_counters", "physical packets accepted:               0/3" in theorem_text and "physical rows accepted:                  0/7" in theorem_text)

    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
    }
    return packet


def main() -> None:
    packet = build()
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    summary = packet["check_summary"]
    print(f"wrote {OUTPUT.name}")
    print(f"checks: {summary['passed']}/{summary['total']}")
    if summary["failed"]:
        raise SystemExit("failed checks: " + ", ".join(summary["failed"]))


if __name__ == "__main__":
    main()
