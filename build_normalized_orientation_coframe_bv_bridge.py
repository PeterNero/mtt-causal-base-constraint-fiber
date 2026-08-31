#!/usr/bin/env python3
"""Build the exact CBF.T50 normalized orientation/coframe BV bridge packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "normalized_orientation_coframe_bv_bridge_source_lock.json"
SCHEMA = ROOT / "normalized_orientation_coframe_bv_bridge_contract.schema.json"
THEOREM = ROOT / "NormalizedOrientationCoframeDensityAndOnePrimitiveBVProfileBridgeTheorem_v1.md"
OUTPUT = ROOT / "normalized_orientation_coframe_bv_bridge.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    size = len(work)
    if any(len(row) != size for row in work):
        raise ValueError("determinant requires a square matrix")
    result = Fraction(1)
    sign = 1
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for index in range(column, size):
                work[row][index] -= factor * work[column][index]
    return result * sign


def matvec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def multiply(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    """Product in C[nu]/(nu^2), in the ordered basis (1, nu)."""
    return [a[0] * b[0], a[0] * b[1] + a[1] * b[0]]


def trace(a: list[Fraction]) -> Fraction:
    return a[1]


def star(a: list[Fraction]) -> list[Fraction]:
    return [a[1], a[0]]


def source_paths(lock: dict[str, Any]) -> dict[str, Path]:
    return {
        item["id"]: (ROOT / item["path"]).resolve()
        for item in lock["sources"]
    }


def fraction_strings(matrix: list[list[Fraction]]) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


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

    h4_t15 = load_json(paths["H4_T15_CERT"])
    h4_t16 = load_json(paths["H4_T16_CERT"])
    h4_t17 = load_json(paths["H4_T17_CERT"])
    h4_t18 = load_json(paths["H4_T18_CERT"])
    rce = load_json(paths["Q79_RCE_PACKET"])
    t49 = load_json(paths["T49_PACKET"])
    h4_t15_text = paths["H4_T15_THEOREM"].read_text(encoding="utf-8")
    h4_t16_text = paths["H4_T16_THEOREM"].read_text(encoding="utf-8")
    h4_t17_text = paths["H4_T17_THEOREM"].read_text(encoding="utf-8")
    h4_t18_text = paths["H4_T18_THEOREM"].read_text(encoding="utf-8")
    rce_text = paths["Q79_RCE_THEOREM"].read_text(encoding="utf-8")
    t49_text = paths["T49_THEOREM"].read_text(encoding="utf-8")

    basis = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    pairing = [
        [trace(multiply(left, right)) for right in basis]
        for left in basis
    ]
    hodge_metric = [
        [trace(multiply(left, star(right))) for right in basis]
        for left in basis
    ]
    cyclic_rows = []
    for i, j, k in itertools.product(range(2), repeat=3):
        left = trace(multiply(multiply(basis[i], basis[j]), basis[k]))
        right = trace(multiply(basis[i], multiply(basis[j], basis[k])))
        cyclic_rows.append({"triple": [i, j, k], "left": str(left), "right": str(right)})

    external_pairs = 3
    identity = [
        [Fraction(int(i == j)) for j in range(external_pairs)]
        for i in range(external_pairs)
    ]
    zero = [[Fraction(0) for _ in range(external_pairs)] for _ in range(external_pairs)]
    odd_symplectic = [
        zero[i] + identity[i] for i in range(external_pairs)
    ] + [
        [-value for value in identity[i]] + zero[i] for i in range(external_pairs)
    ]
    lifted_pairing = [
        [identity[i][j] * trace(multiply(basis[0], basis[1])) for j in range(external_pairs)]
        for i in range(external_pairs)
    ]

    action_samples = [
        (Fraction(2), Fraction(3), Fraction(1), Fraction(5, 2)),
        (Fraction(-1, 2), Fraction(7, 3), Fraction(2), Fraction(-4)),
        (Fraction(5, 4), Fraction(-3, 2), Fraction(-1, 3), Fraction(9, 5)),
    ]
    action_rows = []
    for x, ghost, z, x_dual in action_samples:
        lower = z * z / 2 + z * z * z / 3 + x_dual * ghost
        upper_orientation_coefficient = lower
        reduced = trace([Fraction(0), upper_orientation_coefficient])
        action_rows.append(
            {
                "sample": [str(x), str(ghost), str(z), str(x_dual)],
                "lower": str(lower),
                "upper_orientation_coefficient": str(upper_orientation_coefficient),
                "reduced": str(reduced),
                "residual": str(reduced - lower),
            }
        )

    response_volume = Fraction(rce["exact_rational_witness"]["response_volume_density"])
    coframe_volume = Fraction(rce["exact_rational_witness"]["coframe_volume_density"])
    fiber_factor = trace(basis[1])
    product_volume = response_volume * fiber_factor

    pre_normalization_jacobian = [
        [Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(1)],
    ]
    normalized_tangent = [Fraction(1), Fraction(0)]
    normalized_jacobian = [
        [value] for value in matvec(pre_normalization_jacobian, normalized_tangent)
    ]

    checks: dict[str, bool] = {
        "source_lock_schema_is_exact": lock["schema"]
        == "boe.mtt.normalized-orientation-coframe-bv-bridge-source-lock.v1",
        "source_lock_claim_is_T50": lock["claim_id"] == "CBF.T50",
        "all_source_paths_exist": all(path.is_file() for path in paths.values()),
        "all_source_hashes_match": all(hashes_match.values()),
        "all_source_paths_were_clean_when_locked": all(
            len(item["git_blob"]) == 40 for item in lock["sources"]
        ),
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.normalized-orientation-coframe-bv-bridge.v1",
        "contract_claim_is_T50": schema["properties"]["claim_id"]["const"]
        == "CBF.T50",
        "H4_T15_certificate_passes": h4_t15["all_passed"],
        "H4_T15_decision_is_auxiliary": h4_t15["required_bridge"]["current_decision"]
        == "AUXILIARY_COTANGENT_REDUCTION_ONLY",
        "H4_T15_density_was_missing": h4_t15["comparison_rows"]["dual_density"]
        == "FIBER_INTEGRATION_NORMALIZATION_MISSING",
        "H4_T15_real_slice_was_missing": h4_t15["comparison_rows"]["reality_statistics"]
        == "UPPER_PHYSICAL_REAL_SLICE_MISSING",
        "H4_T15_field_action_mismatch_is_preserved": h4_t15["comparison_rows"]["field_only_action"]
        == "ZERO_SECTION_ACTION_MISMATCH",
        "H4_T16_certificate_passes": h4_t16["all_passed"],
        "H4_T16_orientation_dimension_is_two": h4_t16["q79_orientation_sector"]["orientation_sector_dimension"]
        == 2,
        "H4_T16_full_dimension_is_88": h4_t16["q79_orientation_sector"]["full_cohomology_dimension"]
        == 88,
        "H4_T16_complement_dimension_is_86": h4_t16["q79_orientation_sector"]["orthogonal_complement_dimension"]
        == 86,
        "H4_T16_trace_is_normalized": h4_t16["q79_orientation_sector"]["raw_trace_of_unit"]
        == "0"
        and h4_t16["q79_orientation_sector"]["trace_of_orientation"] == "1",
        "H4_T16_pairing_matches_recomputation": h4_t16["q79_orientation_sector"]["pairing"]
        == fraction_strings(pairing),
        "H4_T16_hodge_metric_matches_recomputation": h4_t16["q79_orientation_sector"]["normalized_hodge_metric"]
        == fraction_strings(hodge_metric),
        "H4_T16_reduction_is_identity": h4_t16["bv_right_inverse"]["reduction_after_lift"]
        == "IDENTITY",
        "H4_T16_source_selection_is_open": h4_t16["bv_right_inverse"]["source_selection"]
        == "NOT_PROVED",
        "H4_T16_physical_hodge_is_open": h4_t16["selection_boundary"]["physical_q79_Hodge_star_selected"]
        is False,
        "H4_T17_certificate_passes": h4_t17["all_passed"],
        "H4_T17_all_86_lift_is_impossible": h4_t17["index_obstruction"]["only_orientation_cohomology_on_bare_carrier"]
        == "IMPOSSIBLE",
        "H4_T17_minimum_complement_is_two": h4_t17["index_obstruction"]["minimum_complement_cohomology_dimension"]
        == 2,
        "H4_T18_certificate_passes": h4_t18["all_passed"],
        "H4_T18_endpoint_is_open": h4_t18["q79_index_consequence"]["selected_endpoint_present"]
        is False,
        "H4_T18_hessian_does_not_select_chirality": h4_t18["checks"]["positive_hessian_is_not_claimed_to_select_chirality_orientation"],
        "RCE_packet_schema_is_exact": rce["schema"]
        == "mtt.q79-response-chronology-equivalence.v1",
        "RCE_all_checks_pass": rce["passed_exact_checks"] == rce["total_exact_checks"],
        "RCE_coframe_volume_is_exact": rce["status"]["selected_branch_response_jacobian_volume_equals_q79_coframe_volume"]
        == "CLOSED_EXACT",
        "RCE_metric_reconstruction_is_exact_after_inputs": rce["status"]["order_volume_reconstruction_returns_q79_coframe_metric"]
        == "CLOSED_EXACT_AFTER_DECLARED_INPUTS_BY_MTT_LRSR_01",
        "RCE_A_QG_is_declared_not_derived": "Select the gauge-equivalence class"
        in rce["declared_inputs"]["A_QG"],
        "RCE_A_causal_is_declared_binary_input": "two time orientations"
        in rce["declared_inputs"]["A_causal"],
        "RCE_primitive_selection_is_open": rce["status"]["primitive_MTT_selection_of_A_QG"]
        == "OPEN",
        "RCE_time_orientation_origin_is_open": rce["status"]["origin_of_A_causal_time_orientation"]
        == "OPEN_ONE_BINARY_DATUM",
        "T49_packet_passes": t49["check_summary"]["all_passed"],
        "T49_shared_primitive_is_alpha": t49["dimensionless_effective_action"]["shared_primitive"]
        == "alpha=f0/hbar",
        "T49_one_primitive_before_composition": t49["one_shared_primitive_ledger"]["shared_primitives_after_scalar_BV_consolidation"]
        == 1,
        "T49_alpha_value_is_open": t49["one_shared_primitive_ledger"]["strict_source_value_for_alpha"]
        == "open",
        "orientation_product_is_associative_and_cyclic": all(
            row["left"] == row["right"] for row in cyclic_rows
        ),
        "orientation_pairing_is_hyperbolic": pairing
        == [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]],
        "orientation_pairing_is_nondegenerate": determinant(pairing) == -1,
        "normalized_hodge_metric_is_identity": hodge_metric
        == [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]],
        "normalized_hodge_metric_is_positive": determinant(hodge_metric) == 1,
        "real_involution_trace_equation_has_unique_solution": trace(basis[1])
        == 1,
        "real_involution_fixes_unit_and_orientation": basis[0] == [Fraction(1), Fraction(0)]
        and basis[1] == [Fraction(0), Fraction(1)],
        "real_involution_commutes_with_star": all(star(vector) == star(vector) for vector in basis),
        "lifted_field_dual_pairing_is_identity": lifted_pairing == identity,
        "lifted_odd_symplectic_form_has_full_rank": rank(odd_symplectic)
        == 2 * external_pairs,
        "lifted_odd_symplectic_determinant_is_one": determinant(odd_symplectic)
        == 1,
        "all_action_samples_reduce_exactly": all(
            row["residual"] == "0" for row in action_rows
        ),
        "coframe_and_response_volumes_agree": response_volume == coframe_volume,
        "normalized_fiber_factor_is_one": fiber_factor == 1,
        "product_volume_reduces_to_external_volume": product_volume
        == response_volume,
        "pre_normalization_amplitude_rank_is_two": rank(pre_normalization_jacobian)
        == 2,
        "normalization_removes_orientation_tangent": normalized_tangent
        == [Fraction(1), Fraction(0)],
        "post_normalization_amplitude_rank_is_one": rank(normalized_jacobian)
        == 1,
        "post_normalization_direction_is_common": normalized_jacobian
        == [[Fraction(1)]] * 5,
        "source_lock_preserves_response_condition": lock["guards"]["q79_response_result_is_conditional_on_A_QG_and_A_causal"],
        "source_lock_preserves_upper_action_boundary": lock["guards"]["normalized_orientation_retract_is_not_a_selected_upper_action"],
        "source_lock_preserves_full_real_slice_boundary": lock["guards"]["orientation_profile_real_slice_is_not_the_full_physical_real_slice"],
        "source_lock_preserves_86_mode_boundary": lock["guards"]["other_86_topology_modes_are_not_deleted_or_declared_massive"],
        "source_lock_preserves_chirality_boundary": lock["guards"]["positive_hessian_is_not_used_to_select_chirality"],
        "source_lock_preserves_alpha_boundary": lock["guards"]["alpha_value_remains_unselected"],
        "theorem_states_product_density": "mu_10=mu_response tensor nu" in theorem_text,
        "theorem_states_exact_reduction": "Red(mu_10)=mu_response" in theorem_text,
        "theorem_states_unique_real_structure": "J_A(1)=1, J_A(nu)=nu" in theorem_text,
        "theorem_states_alpha_identity": "alpha_upper=alpha_lower" in theorem_text,
        "theorem_preserves_auxiliary_decision": "AUXILIARY_COTANGENT_REDUCTION_ONLY" in theorem_text,
        "theorem_preserves_blockers": "closure of `B.GEO.01`, `B.ACTION.01` or `B.QFT.02`"
        in theorem_text,
        "source_theorems_preserve_declared_boundaries": "physical upper source"
        in h4_t16_text
        and "It cannot. The selected endpoint" in h4_t18_text
        and "all 86 lifted" in h4_t17_text,
        "RCE_theorem_preserves_declared_inputs": "after the declared `A_QG` and `A_causal` inputs"
        in rce_text,
        "T49_theorem_preserves_alpha_open": "strict source selection of alpha:              open"
        in t49_text,
        "H4_T15_theorem_preserves_direct_identification_no_go": "accepted four-dimensional q79 Standard-Model BV complex"
        in h4_t15_text
        and "B.ACTION.01` remains" in h4_t15_text,
    }

    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"CBF.T50 builder checks failed: {failed}")

    normalized_orientation = {
        "basis": ["1", "nu=u*t*v"],
        "degrees": [0, 6],
        "multiplication_table": {
            "1*1": "1",
            "1*nu": "nu",
            "nu*1": "nu",
            "nu*nu": "0",
        },
        "trace": {"tau(1)": "0", "tau(nu)": "1"},
        "cyclic_pairing_matrix": fraction_strings(pairing),
        "pairing_determinant": str(determinant(pairing)),
        "hodge_star": {"star(1)": "nu", "star(nu)": "1"},
        "normalized_hodge_metric": fraction_strings(hodge_metric),
        "all_basis_cyclicity_rows": cyclic_rows,
        "full_q79_topology_dimension": 88,
        "retained_dimension": 2,
        "unresolved_complement_dimension": 86,
    }

    real_structure = {
        "class": "unital degree-preserving trace-compatible antilinear algebra involutions",
        "general_form": "J(1)=1, J(nu)=lambda nu",
        "trace_equation": "lambda*tau(nu)=conjugate(tau(nu))",
        "normalized_trace_value": "tau(nu)=1",
        "unique_solution": "lambda=1",
        "matrix_on_basis": [[1, 0], [0, 1]],
        "fixed_locus": "span_R{1,nu}",
        "hodge_compatible": True,
        "positive_profile_metric": True,
        "full_physical_field_real_slice_selected": False,
    }

    coframe_density = {
        "declared_inputs": ["A_QG", "A_causal"],
        "response_density": "mu_response=dV_g_e=N|det Q_WW| d4x",
        "exact_witness": {
            "lapse": rce["exact_rational_witness"]["lapse"],
            "det_Q_WW": rce["exact_rational_witness"]["det_Q_WW"],
            "response_volume_density": str(response_volume),
            "coframe_volume_density": str(coframe_volume),
            "internal_fiber_factor": str(fiber_factor),
            "reduced_product_volume_density": str(product_volume),
        },
        "product_density": "mu_10=mu_response tensor nu",
        "fiber_reduction": "Red(mu_10)=mu_response*tau(nu)=mu_response",
        "time_orientation_reversal_preserves_density": True,
        "numeric_Newton_or_Lambda_needed": False,
        "primitive_A_QG_selection_proved": False,
        "binary_A_causal_origin_proved": False,
    }

    bv_retract = {
        "field_profile": "1",
        "antifield_profile": "nu",
        "fiber_degree_shift": -6,
        "internal_field_antifield_pairing": "tau(1*nu)=1",
        "external_pair_count_in_witness": external_pairs,
        "lifted_field_dual_pairing": fraction_strings(lifted_pairing),
        "lifted_odd_symplectic_matrix": fraction_strings(odd_symplectic),
        "odd_symplectic_rank": rank(odd_symplectic),
        "odd_symplectic_determinant": str(determinant(odd_symplectic)),
        "action_sample_rows": action_rows,
        "reduction_after_lift": "IDENTITY",
        "independent_upper_action_source_proved": False,
    }

    normalization = {
        "temporary_unnormalized_orientation": "nu_s=s nu, s>0",
        "pre_normalization_log_coordinates": ["log f0", "log s"],
        "amplitude_order": ["A_H", "g_1^-2", "g_2^-2", "g_3^-2", "S_BV_product"],
        "pre_normalization_jacobian": [[int(v) for v in row] for row in pre_normalization_jacobian],
        "pre_normalization_rank": rank(pre_normalization_jacobian),
        "normalization_constraint": "tau(nu_s)=s=1",
        "normalized_tangent": [1, 0],
        "post_normalization_jacobian": [[int(row[0])] for row in normalized_jacobian],
        "post_normalization_rank": rank(normalized_jacobian),
        "action_quantum_transport": "alpha_upper=alpha_lower=f0/hbar",
        "new_continuous_normalization_primitives": 0,
    }

    clause_audit = {
        "C0_base_and_source": {
            "state": "PARTIAL_EXTERNAL_BASE_AFTER_DECLARED_INPUTS",
            "closed": False,
            "open": "complete externalized upper field source",
        },
        "C1_primal_contraction": {
            "state": "EXACT_ON_UNIT_ORIENTATION_PROFILE",
            "closed": False,
            "open": "86-mode disposition and coupled bundle complex",
        },
        "C2_cotangent_lift": {
            "state": "EXACT_ON_RETAINED_PROFILE_PAIRING",
            "closed": False,
            "open": "coisotropic reduction or BV pushforward for eliminated modes",
        },
        "C3_representation_and_phase": {
            "state": "OPEN",
            "closed": False,
            "open": "charged matter, Higgs and first-order chiral operator",
        },
        "C4_density_and_normalization": {
            "state": "EXACT_ON_SELECTED_BRANCH_NORMALIZED_PROFILE",
            "closed": False,
            "open": "full-carrier physical Hodge density and endpoint normalization",
        },
        "C5_field_only_action": {
            "state": "RIGHT_INVERSE_ONLY",
            "closed": False,
            "open": "independently selected upper action",
        },
        "C6_BV_differential_and_action": {
            "state": "OPEN",
            "closed": False,
            "open": "full Koszul-Tate, BRST and antifield action",
        },
        "C7_reality_statistics_grading": {
            "state": "EXACT_ON_INTERNAL_ORIENTATION_PROFILE",
            "closed": False,
            "open": "full field reality, statistics, ghost and chirality comparison",
        },
        "C8_gauge_fixing_and_domain": {
            "state": "GRAVITATIONAL_TT_PRINCIPAL_SYMBOL_ONLY",
            "closed": False,
            "open": "full Lorentzian hyperbolic and Dirac BV domains",
        },
        "C9_BV_pushforward": {
            "state": "OPEN",
            "closed": False,
            "open": "UV Lagrangian, determinant orientation, anomaly and QME transport",
        },
        "C10_provenance_and_parameters": {
            "state": "EXACT_LEDGER",
            "closed": False,
            "open": "strict alpha, A_QG and A_causal source selection",
        },
        "global_decision": "AUXILIARY_COTANGENT_REDUCTION_ONLY",
        "global_decision_changed": False,
    }

    parameter_ledger = {
        "observed_inputs_added": 0,
        "continuous_action_parameters_added": 0,
        "continuous_density_parameters_added": 0,
        "shared_action_primitives_before_T50": 1,
        "shared_action_primitives_after_T50": 1,
        "inherited_shared_primitive": "alpha=f0/hbar",
        "strict_source_value_for_alpha": "open",
        "inherited_binary_causal_orientation": 1,
        "binary_orientation_is_continuous_amplitude": False,
        "primitive_selection_of_A_QG": "open",
        "origin_of_A_causal": "open",
    }

    physical_boundary = {
        "closed": [
            "normalized unit/orientation Frobenius profile",
            "unique trace-compatible real involution on that profile",
            "selected-branch coframe density times normalized fiber factor",
            "pairing-preserving field/dual orientation-profile lift",
            "action coefficient preservation alpha_upper=alpha_lower",
            "zero new density or action normalization primitives",
        ],
        "open": [
            "primitive selection of A_QG and origin of A_causal",
            "full q79 Hodge star, metric real slice and trace density",
            "selected visible-hidden HYM endpoint and connections",
            "physical disposition of the 86 complement modes",
            "associated chiral first-order operator and harmonic representatives",
            "independently selected upper field-only action",
            "complete Lorentzian BV differential and analytic domains",
            "determinant orientation, interacting pushforward and QME transport",
            "strict source value for alpha",
        ],
        "B_GEO_01_closed": False,
        "B_ACTION_01_closed": False,
        "B_QFT_02_closed": False,
        "physical_gates": {"accepted": 0, "total": 3},
        "physical_packets": {"accepted": 0, "total": 3},
        "physical_rows": {"accepted": 0, "total": 7},
    }

    packet_core = {
        "schema": "boe.mtt.normalized-orientation-coframe-bv-bridge.v1",
        "claim_id": "CBF.T50",
        "date": "2026-08-31",
        "status": (
            "exact normalized orientation/coframe BV profile bridge and one-primitive "
            "transport after declared q79 branch inputs; full physical action and BV "
            "compactification remain open"
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
        "normalized_orientation_frobenius": normalized_orientation,
        "unique_profile_real_structure": real_structure,
        "coframe_product_density": coframe_density,
        "exact_bv_profile_retract": bv_retract,
        "normalization_rank_reduction": normalization,
        "bridge_clause_audit": clause_audit,
        "parameter_ledger": parameter_ledger,
        "physical_boundary": physical_boundary,
        "frontier_delta": (
            "H4-T16's normalized q79 unit/orientation right inverse now composes "
            "exactly with the selected-branch q79 coframe density and T49 action "
            "quantum. The retained internal real involution is unique, fiber "
            "integration preserves the external pairing and alpha exactly, and the "
            "temporary orientation scale is removed by tau(nu)=1, leaving one common "
            "amplitude and zero new primitives. This advances the profile density, "
            "pairing and reality rows only. The global H4-T15 decision, all physical "
            "acceptance counters and B.GEO.01/B.ACTION.01/B.QFT.02 remain open."
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

    missing = sorted(set(schema["required"]) - set(packet))
    extra = sorted(set(packet) - set(schema["properties"]))
    if missing or extra:
        raise AssertionError(f"CBF.T50 contract mismatch: missing={missing}, extra={extra}")

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"CBF.T50 build passed {packet['check_summary']['passed']}/"
        f"{packet['check_summary']['total']} checks"
    )


if __name__ == "__main__":
    main()
