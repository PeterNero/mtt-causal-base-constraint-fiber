#!/usr/bin/env python3
"""Build the exact CBF.T24 upper-totalization selection packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_physical_yukawa_hessian_identification as phy
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "upper_totalization_supercharge_source_lock.json"
SCHEMA = ROOT / "upper_totalization_supercharge_contract.schema.json"
THEOREM = ROOT / "UpperTensorTotalizationSharedLineSuperchargeSelectionTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T22_PACKET = ROOT / "relative_product_supercharge.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
BV4_PACKET = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
FSB_ROOT = ROOT.parent / "mtt-q79-total-superconnection-branching"
ML_ROOT = ROOT.parent / "20 Mathematical Language Discovery Program"
QM_ROOT = ROOT.parent / "mtt-qm-source-proof"
SHARED_ROOT_PACKET = FSB_ROOT / "artifacts" / "almost_commutative_shared_root_spinc.packet.json"
BINARY_ROOT_PACKET = FSB_ROOT / "artifacts" / "binary_root_car_net_equivalence.packet.json"
UNIVERSAL_LINE_PACKET = ML_ROOT / "q79_universal_shared_line_intertwiner.packet.json"
FREE_DIRAC_CERT = QM_ROOT / "certificates" / "framed_q79_free_dirac_car_net.certificate.json"
OUTPUT = ROOT / "upper_totalization_supercharge.packet.json"

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    encoded = json.dumps(wg.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def sparse_matmul(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not compose")
    result = cp.zero(len(left), len(right[0]))
    for row, left_row in enumerate(left):
        for inner, left_value in enumerate(left_row):
            if left_value == cp.ZERO:
                continue
            for column, right_value in enumerate(right[inner]):
                if right_value == cp.ZERO:
                    continue
                result[row][column] = cp.kadd(
                    result[row][column], cp.kmul(left_value, right_value)
                )
    return result


def physical_transfer(
    p: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    parameter: Fraction,
) -> cp.Matrix:
    v_phase = phy.partial_isometry([(0, 6), (1, 7), (2, 8), (13, 14)])
    v_shift = phy.partial_isometry([(3, 9), (4, 10), (5, 11), (12, 15)])
    return phy.routed_incidence_map(
        p,
        phase_direction,
        shift_direction,
        v_phase,
        v_shift,
        parameter,
    )


def physical_differential(transfer: cp.Matrix) -> cp.Matrix:
    antiparticle = matrix_conjugate(cp.adjoint(transfer))
    return wg.block_diag([transfer, antiparticle])


def physical_dirac(transfer: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer, cp.adjoint(transfer))
    return wg.block_diag([particle, matrix_conjugate(particle)])


def total_differential(
    q_external: cp.Matrix,
    gamma_external: cp.Matrix,
    q_finite: cp.Matrix,
    scale: Fraction,
) -> cp.Matrix:
    return cp.madd(
        cp.kron(q_external, cp.identity(len(q_finite))),
        cp.kron(gamma_external, cp.mscale(q(scale), q_finite)),
    )


def total_charge(
    d_external: cp.Matrix,
    gamma_external: cp.Matrix,
    d_finite: cp.Matrix,
    scale: Fraction,
) -> cp.Matrix:
    return cp.madd(
        cp.kron(d_external, cp.identity(len(d_finite))),
        cp.kron(gamma_external, cp.mscale(q(scale), d_finite)),
    )


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def selection_root(
    source_lock: dict[str, Any],
    theorem_hash: str,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.upper-totalization-selection-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "factor_differentials": {
            "external": "q_Y=Pi_Y,- D_Y Pi_Y,+",
            "finite": "q_F=T direct_sum conjugate(T^*)",
        },
        "universal_rule": "q_tot=q_Y tensor I+Gamma_Y tensor h q_F",
        "closure_charge": "B_tot=q_tot+q_tot^*",
        "root_balance": "M_minus=M_plus tensor epsilon; epsilon^2=1; simultaneous twist",
        "theorem_sha256": theorem_hash,
        "observed_targets": [],
        "selected_binary_root": None,
        "continuum_HYM_endpoint": None,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t22 = json.loads(T22_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    bv4 = json.loads(BV4_PACKET.read_text(encoding="ascii"))
    shared_root = json.loads(SHARED_ROOT_PACKET.read_text(encoding="utf-8"))
    binary_root = json.loads(BINARY_ROOT_PACKET.read_text(encoding="utf-8"))
    universal_line = json.loads(UNIVERSAL_LINE_PACKET.read_text(encoding="utf-8"))
    free_dirac = json.loads(FREE_DIRAC_CERT.read_text(encoding="utf-8"))

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    phase_direction = cp.madd(cp.identity(3), z)
    shift_direction = cp.madd(cp.identity(3), x)

    q_external = [[cp.ZERO, cp.ZERO], [cp.ONE, cp.ZERO]]
    d_external = cp.madd(q_external, cp.adjoint(q_external))
    gamma_external = cp.diagonal([cp.ONE, q(-1)])
    identity2 = cp.identity(2)
    identity96 = cp.identity(96)
    identity192 = cp.identity(192)

    parameter = Fraction(1, 2)
    scale = Fraction(3, 2)
    transfer = physical_transfer(p, phase_direction, shift_direction, parameter)
    q_finite = physical_differential(transfer)
    d_finite = physical_dirac(transfer)
    q_total = total_differential(
        q_external, gamma_external, q_finite, scale
    )
    b_total_from_q = cp.madd(q_total, cp.adjoint(q_total))
    b_total_direct = total_charge(
        d_external, gamma_external, d_finite, scale
    )

    q_total_square = sparse_matmul(q_total, q_total)
    b_total_square = sparse_matmul(b_total_direct, b_total_direct)
    d_external_square = sparse_matmul(d_external, d_external)
    d_finite_square = sparse_matmul(d_finite, d_finite)
    expected_total_square = cp.madd(
        cp.kron(d_external_square, identity96),
        cp.kron(identity2, cp.mscale(q(scale * scale), d_finite_square)),
    )

    transfer_zero = physical_transfer(
        p, phase_direction, shift_direction, Fraction(0)
    )
    q_finite_zero = physical_differential(transfer_zero)
    d_finite_zero = physical_dirac(transfer_zero)
    b_total_zero = total_charge(
        d_external, gamma_external, d_finite_zero, scale
    )
    b_total_zero_square = sparse_matmul(b_total_zero, b_total_zero)
    relative_neutral = matrix_sub(
        b_total_zero_square,
        cp.mscale(q(scale * scale), identity192),
    )
    expected_relative_neutral = cp.kron(d_external_square, identity96)

    transfer_plus = physical_transfer(
        p, phase_direction, shift_direction, Fraction(1)
    )
    transfer_minus = physical_transfer(
        p, phase_direction, shift_direction, Fraction(-1)
    )
    d_finite_plus = physical_dirac(transfer_plus)
    d_finite_minus = physical_dirac(transfer_minus)
    h_physical = cp.mscale(
        q(Fraction(1, 2)),
        matrix_sub(
            sparse_matmul(d_finite_plus, d_finite_plus),
            sparse_matmul(d_finite_minus, d_finite_minus),
        ),
    )
    b_plus = total_charge(d_external, gamma_external, d_finite_plus, scale)
    b_minus = total_charge(d_external, gamma_external, d_finite_minus, scale)
    total_response = cp.mscale(
        q(Fraction(1, 2)),
        matrix_sub(sparse_matmul(b_plus, b_plus), sparse_matmul(b_minus, b_minus)),
    )
    expected_total_response = cp.kron(
        identity2, cp.mscale(q(scale * scale), h_physical)
    )

    # Exact uniqueness system for A=[[a,b],[c,d]]. Normalized equations are
    # b=0, c=0, a+d=0 and a=1.
    uniqueness_matrix = [
        [q(0), q(1), q(0), q(0)],
        [q(0), q(0), q(1), q(0)],
        [q(1), q(0), q(0), q(1)],
        [q(1), q(0), q(0), q(0)],
    ]
    uniqueness_rhs = [q(0), q(0), q(0), q(1)]
    uniqueness_solution = [q(1), q(0), q(0), q(-1)]
    uniqueness_residual: list[cp.K] = []
    for index, row in enumerate(uniqueness_matrix):
        value = cp.ZERO
        for column, coefficient in enumerate(row):
            value = cp.kadd(
                value, cp.kmul(coefficient, uniqueness_solution[column])
            )
        uniqueness_residual.append(
            cp.kadd(value, cp.kmul(q(-1), uniqueness_rhs[index]))
        )
    a_selected = [[cp.ONE, cp.ZERO], [cp.ZERO, q(-1)]]
    q_naive = cp.madd(
        cp.kron(q_external, identity96),
        cp.kron(identity2, cp.mscale(q(scale), q_finite)),
    )
    q_naive_square = sparse_matmul(q_naive, q_naive)

    epsilon_external = cp.mscale(q(-1), identity2)
    epsilon_residual = cp.mscale(q(-1), identity96)
    balanced_epsilon = cp.kron(epsilon_external, epsilon_residual)
    one_sided_epsilon = cp.kron(epsilon_external, identity96)
    balanced_intertwiner_left = sparse_matmul(balanced_epsilon, q_total)
    balanced_intertwiner_right = sparse_matmul(q_total, balanced_epsilon)

    source_checks = source_hash_checks(source_lock)
    universal_checks = universal_line["checks"]
    boundary = source_lock["boundary"]
    theorem_hash = sha256(THEOREM)
    selection_sha256, selection_payload = selection_root(source_lock, theorem_hash)
    selection_text = json.dumps(selection_payload, sort_keys=True)

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.upper-totalization-supercharge-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "f446c6a4-7804-484e-a7fc-7fce515744f0",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.upper-totalization-supercharge.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_factor_source_is_exact": t20["claim_id"] == "CBF.T20"
        and all(t20["checks"].values()),
        "T22_product_source_is_exact": t22["claim_id"] == "CBF.T22"
        and all(t22["checks"].values()),
        "T23_physical_factor_is_exact": t23["claim_id"] == "CBF.T23"
        and all(t23["checks"].values()),
        "BV4_product_compiler_is_exact": bv4["claim_id"] == "CBF.T13"
        and all(bv4["checks"].values()),
        "shared_root_factorization_is_exact": shared_root["all_checks_pass"]
        and all(shared_root["checks"].values()),
        "binary_root_observable_equivalence_is_exact": binary_root["all_checks_pass"]
        and all(binary_root["checks"].values()),
        "universal_shared_line_checks_are_exact": all(universal_checks.values()),
        "free_q79_Dirac_source_is_exact": free_dirac["all_checks_pass"]
        and all(free_dirac["checks"].values()),
        "external_chiral_differential_is_nilpotent": wg.is_zero(
            sparse_matmul(q_external, q_external)
        ),
        "external_Dirac_is_chiral_charge": d_external
        == cp.madd(q_external, cp.adjoint(q_external)),
        "external_grading_anticommutes_with_differential": wg.is_zero(
            cp.madd(
                sparse_matmul(gamma_external, q_external),
                sparse_matmul(q_external, gamma_external),
            )
        ),
        "finite_physical_differential_is_nilpotent": wg.is_zero(
            sparse_matmul(q_finite, q_finite)
        ),
        "finite_physical_Dirac_is_chiral_charge": d_finite
        == cp.madd(q_finite, cp.adjoint(q_finite)),
        "finite_physical_dimension_is_96": len(q_finite) == 96,
        "total_differential_dimension_is_192": len(q_total) == 192,
        "total_differential_is_nilpotent": wg.is_zero(q_total_square),
        "total_charge_from_differential_is_exact_product": b_total_from_q
        == b_total_direct,
        "total_charge_square_is_graded_factor_sum": b_total_square
        == expected_total_square,
        "neutral_finite_square_is_identity": sparse_matmul(
            d_finite_zero, d_finite_zero
        )
        == identity96,
        "neutral_relative_subtraction_is_forced": relative_neutral
        == expected_relative_neutral,
        "physical_response_digest_matches_T23": matrix_digest(h_physical)
        == t23["hessian_compression"]["KO6_response_sha256"],
        "total_response_is_h_squared_physical_response": total_response
        == expected_total_response,
        "uniqueness_system_has_full_rank": cp.matrix_rank(uniqueness_matrix) == 4,
        "uniqueness_solution_has_zero_residual": all(
            value == cp.ZERO for value in uniqueness_residual
        ),
        "unique_Koszul_coefficient_is_external_grading": a_selected
        == gamma_external,
        "ungraded_tensor_sum_is_not_nilpotent": not wg.is_zero(q_naive_square),
        "ungraded_failure_is_exact_cross_term": q_naive_square
        == cp.mscale(
            q(2 * scale), cp.kron(q_external, q_finite)
        ),
        "shared_line_classifying_map_is_exact": universal_checks[
            "S3_to_Z64_map_is_a_homomorphism"
        ]
        and universal_checks["S3_to_Z64_nontrivial_image_is_exactly_0_32"],
        "shared_line_connection_is_preserved": universal_checks[
            "connection_identification_follows_from_equal_flat_holonomy_characters"
        ],
        "finite_factor_is_scalar_line_neutral": universal_checks[
            "same_scalar_line_holonomy_commutes_with_every_CLN_projector"
        ]
        and t23["one_higgs_gauge_covariance"][
            "family_matrices_commute_with_gauge_action"
        ],
        "both_binary_roots_reconstruct_shared_line": shared_root["exact_witness"]["checks"][
            "both_root_pairs_reconstruct_the_shared_determinant"
        ],
        "order_two_root_difference_is_balanced": shared_root["exact_witness"]["checks"][
            "order_two_branch_ratio_cancels_across_the_two_factors"
        ],
        "balanced_epsilon_is_identity_on_complete_carrier": balanced_epsilon
        == identity192,
        "one_sided_epsilon_is_nontrivial": one_sided_epsilon != identity192,
        "balanced_root_change_intertwines_total_differential": (
            balanced_intertwiner_left == balanced_intertwiner_right
        ),
        "no_binary_root_selector_is_needed": binary_root["parameter_ledger"][
            "new_binary_root_selectors"
        ]
        == 0
        and boundary["binary_root_selector_required_for_this_endpoint"] is False,
        "selection_root_contains_no_observed_target": selection_payload[
            "observed_targets"
        ]
        == []
        and all(
            token not in selection_text
            for token in ("measured_mass", "CKM_target", "PMNS_target")
        ),
        "selection_root_does_not_choose_binary_branch": selection_payload[
            "selected_binary_root"
        ]
        is None,
        "selection_root_does_not_insert_HYM_endpoint": selection_payload[
            "continuum_HYM_endpoint"
        ]
        is None,
        "CBF_composite_product_truth_value_advances": boundary[
            "CBF_T22_composite_product_selected_before"
        ]
        is False
        and boundary["CBF_T22_composite_product_selected_after"] is True,
        "selection_is_conditional_on_factor_sources": boundary["selection_kind"]
        == "unique graded tensor totalization conditional on the selected factor sources",
        "primitive_background_selection_remains_open": boundary[
            "primitive_q79_background_selected_here"
        ]
        is False,
        "continuum_HYM_intertwiner_remains_open": boundary[
            "continuum_HYM_intertwiner"
        ]
        is False,
        "physical_BV_QME_remains_open": boundary["physical_BV_QME"] is False,
        "nonlinear_physical_action_remains_open": boundary[
            "nonlinear_physical_action_selected"
        ]
        is False,
        "no_observed_or_fitted_input": boundary["observed_values_used"] is False
        and boundary["fitted_coefficients_used"] is False,
        "physical_packet_acceptance_is_unchanged": boundary[
            "physical_packet_acceptance_before"
        ]
        == boundary["physical_packet_acceptance_after"]
        == 0,
        "physical_row_acceptance_is_unchanged": boundary[
            "physical_row_acceptance_before"
        ]
        == boundary["physical_row_acceptance_after"]
        == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T24 checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.upper-totalization-supercharge.v1",
        "claim_id": "CBF.T24",
        "date": "2026-08-29",
        "tier": "exact algebraic, framed-Cauchy and flat shared-line symbol selection by universal property",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": theorem_hash,
        "selection_root_sha256": selection_sha256,
        "source_provenance": {
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "selection_root_payload": selection_payload,
        },
        "factor_differentials": {
            "external": "q_Y=Pi_Y,- D_Y Pi_Y,+",
            "external_square": "q_Y^2=0",
            "external_charge": "D_Y=q_Y+q_Y^*",
            "finite": "q_F(t)=T(t) direct_sum conjugate(T(t)^*)",
            "finite_square": "q_F(t)^2=0",
            "finite_charge": "D_phys(t)=q_F(t)+q_F(t)^*",
            "finite_dimension": 96,
            "total_dimension": 192,
        },
        "totalization_uniqueness": {
            "rule": "q_tot=q_Y tensor I+Gamma_Y tensor h q_F",
            "class": "minimal factor-local degree-one tensor derivations extending both selected factors",
            "graded_Leibniz_rule": "q(x tensor y)=q_Y(x) tensor y+(-1)^degree(x) x tensor h q_F(y)",
            "coefficient_variables": ["a", "b", "c", "d"],
            "normalized_equations": ["b=0", "c=0", "a+d=0", "a=1"],
            "coefficient_rank": 4,
            "unique_solution": ["1", "0", "0", "-1"],
            "selected_coefficient": "A=Gamma_Y",
            "naive_ungraded_sum_nilpotent": False,
            "mixed_interaction_terms_selected": False,
        },
        "physical_closure_charge": {
            "charge": "B_tot=q_tot+q_tot^*=D_Y tensor I+Gamma_Y tensor h D_phys(t)",
            "square": "B_tot^2=D_Y^2 tensor I+h^2 I tensor D_phys(t)^2",
            "neutral_subtraction": "L_rel=B_tot^2-h^2 I",
            "response": "L_rel'(0)=h^2 I tensor H_phys",
            "target_compression": "h^2 H_derived",
            "one_primitive_identity": "h=Lambda=E0=1/L0 and mu^2=Lambda^2=h^2",
            "T23_response_sha256": matrix_digest(h_physical),
        },
        "shared_line_naturality": {
            "upper_object": universal_line["universal_preprojection_object"]["line"],
            "classifying_map": universal_line["universal_preprojection_object"]["q79_sheet_map"],
            "same_source_meaning": universal_line["universal_preprojection_object"]["same_source_meaning"],
            "external_factor": "covariant q79 framed Dirac differential",
            "finite_factor": "root-neutral order-zero A48/A51 Yukawa incidence",
            "totalization_is_parallel": True,
            "connection_and_holonomy_preserved": True,
            "flat_line_identified_with_nonzero_Chern_HYM": False,
        },
        "binary_root_balance": {
            "roots_mod64": [16, 48],
            "difference_mod64": 32,
            "difference_order": 2,
            "two_factor_difference_mod64": 0,
            "balanced_rule": "M_minus=M_plus tensor epsilon on both factors; epsilon^2=1",
            "finite_Yukawa_factor_root_charge": 0,
            "one_root_selected": False,
            "selector_required_for_this_endpoint": False,
            "future_odd_factorwise_interaction_could_reopen_question": True,
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_continuous_shape_parameters": 0,
            "new_binary_root_selectors": 0,
            "universal_dimensionful_primitives": 1,
            "sector_specific_scales": 0,
        },
        "physical_boundary": {
            "CBF_T22_composite_product_selected": True,
            "selection_is_conditional_on_factor_sources": True,
            "one_binary_root_selected": False,
            "binary_root_selector_required_for_this_endpoint": False,
            "primitive_q79_background_selected_here": False,
            "continuum_HYM_intertwiner": False,
            "physical_BV_QME": False,
            "nonlinear_physical_action_selected": False,
            "full_B_ACTION_01_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The CBF.T22 graded product is now the unique tensor totalization "
            "of the selected external chiral closure differential and the "
            "CBF.T23 physical finite Yukawa differential. Its self-adjoint "
            "closure charge and square recover the exact physical response, "
            "and the construction is natural over the selected flat shared "
            "line. Because the Yukawa incidence is root-neutral, the two "
            "balanced binary-root presentations are intertwined and no root "
            "selector is required for this endpoint. Continuum HYM, nonlinear "
            "physical action and BV/QME remain open, so acceptance stays 0/3 "
            "packets and 0/7 rows."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }
    if set(packet) != set(schema["properties"]):
        raise AssertionError("packet top-level keys do not match contract schema")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "upper-totalization supercharge packet built: "
        f"{len(checks)}/{len(checks)} checks; CBF composite product selected; "
        "physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
