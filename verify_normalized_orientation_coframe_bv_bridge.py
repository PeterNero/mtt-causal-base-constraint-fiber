#!/usr/bin/env python3
"""Independently verify the CBF.T50 normalized orientation/coframe bridge."""

from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "normalized_orientation_coframe_bv_bridge_source_lock.json"
SCHEMA_PATH = ROOT / "normalized_orientation_coframe_bv_bridge_contract.schema.json"
THEOREM_PATH = ROOT / "NormalizedOrientationCoframeDensityAndOnePrimitiveBVProfileBridgeTheorem_v1.md"
PACKET_PATH = ROOT / "normalized_orientation_coframe_bv_bridge.packet.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    return pivot_row


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    size = len(work)
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


def multiply(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0] * b[0], a[0] * b[1] + a[1] * b[0]


def trace(a: tuple[Fraction, Fraction]) -> Fraction:
    return a[1]


def star(a: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[1], a[0]


def as_fraction_matrix(matrix: list[list[Any]]) -> list[list[Fraction]]:
    return [[Fraction(str(entry)) for entry in row] for row in matrix]


def main() -> None:
    lock = load_json(LOCK_PATH)
    schema = load_json(SCHEMA_PATH)
    packet = load_json(PACKET_PATH)
    theorem_text = THEOREM_PATH.read_text(encoding="utf-8")
    source_paths = {
        item["id"]: (ROOT / item["path"]).resolve() for item in lock["sources"]
    }
    source_hashes = {
        item["id"]: source_paths[item["id"]].is_file()
        and sha256(source_paths[item["id"]]) == item["sha256"]
        for item in lock["sources"]
    }

    h4_t15 = load_json(source_paths["H4_T15_CERT"])
    h4_t16 = load_json(source_paths["H4_T16_CERT"])
    h4_t17 = load_json(source_paths["H4_T17_CERT"])
    h4_t18 = load_json(source_paths["H4_T18_CERT"])
    rce = load_json(source_paths["Q79_RCE_PACKET"])
    t49 = load_json(source_paths["T49_PACKET"])

    checks: dict[str, bool] = {
        f"builder::{name}": passed for name, passed in packet["checks"].items()
    }

    payload_core = deepcopy(packet)
    payload_core.pop("checks")
    payload_core.pop("check_summary")
    stored_payload_hash = payload_core.pop("exact_payload_sha256")

    orientation = packet["normalized_orientation_frobenius"]
    real = packet["unique_profile_real_structure"]
    density = packet["coframe_product_density"]
    retract = packet["exact_bv_profile_retract"]
    normalization = packet["normalization_rank_reduction"]
    audit = packet["bridge_clause_audit"]
    parameters = packet["parameter_ledger"]
    boundary = packet["physical_boundary"]

    basis = [(Fraction(1), Fraction(0)), (Fraction(0), Fraction(1))]
    pairing = [
        [trace(multiply(left, right)) for right in basis] for left in basis
    ]
    metric = [
        [trace(multiply(left, star(right))) for right in basis] for left in basis
    ]
    cyclic = all(
        trace(multiply(multiply(basis[i], basis[j]), basis[k]))
        == trace(multiply(basis[i], multiply(basis[j], basis[k])))
        for i, j, k in itertools.product(range(2), repeat=3)
    )

    odd_symplectic = as_fraction_matrix(retract["lifted_odd_symplectic_matrix"])
    pre_jacobian = as_fraction_matrix(normalization["pre_normalization_jacobian"])
    post_jacobian = as_fraction_matrix(normalization["post_normalization_jacobian"])
    required = set(schema["required"])
    properties = set(schema["properties"])
    bridge_rows = [key for key in audit if key.startswith("C")]

    independent: dict[str, bool] = {
        "packet_schema_matches_contract": packet["schema"]
        == schema["properties"]["schema"]["const"],
        "packet_claim_matches_contract": packet["claim_id"]
        == schema["properties"]["claim_id"]["const"],
        "packet_has_all_required_keys": required <= set(packet),
        "packet_has_no_undeclared_keys": set(packet) <= properties,
        "source_lock_hash_matches_packet": packet["source_provenance"]["source_lock_sha256"]
        == sha256(LOCK_PATH),
        "schema_hash_matches_packet": packet["source_provenance"]["contract_schema_sha256"]
        == sha256(SCHEMA_PATH),
        "theorem_hash_matches_packet": packet["source_provenance"]["theorem_sha256"]
        == sha256(THEOREM_PATH),
        "all_locked_source_hashes_recompute": all(source_hashes.values()),
        "packet_source_hash_map_is_exact": packet["source_provenance"]["source_hashes_match"]
        == source_hashes,
        "canonical_payload_hash_recomputes": stored_payload_hash
        == canonical_hash(payload_core),
        "builder_summary_is_consistent": packet["check_summary"]["passed"]
        == packet["check_summary"]["total"]
        == len(packet["checks"]),
        "builder_has_75_checks": len(packet["checks"]) == 75,
        "orientation_basis_is_unit_and_top_class": orientation["basis"]
        == ["1", "nu=u*t*v"],
        "orientation_degrees_are_zero_and_six": orientation["degrees"] == [0, 6],
        "orientation_square_is_zero": orientation["multiplication_table"]["nu*nu"]
        == "0",
        "orientation_trace_is_normalized": orientation["trace"]
        == {"tau(1)": "0", "tau(nu)": "1"},
        "pairing_recomputes": as_fraction_matrix(orientation["cyclic_pairing_matrix"])
        == pairing,
        "pairing_determinant_recomputes": Fraction(orientation["pairing_determinant"])
        == determinant(pairing)
        == -1,
        "pairing_is_nondegenerate": rank(pairing) == 2,
        "all_eight_cyclicity_rows_are_present": len(orientation["all_basis_cyclicity_rows"])
        == 8,
        "all_basis_triples_are_cyclic": cyclic,
        "hodge_star_is_involutive": all(star(star(item)) == item for item in basis),
        "hodge_metric_recomputes": as_fraction_matrix(orientation["normalized_hodge_metric"])
        == metric,
        "hodge_metric_is_positive_identity": metric
        == [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]],
        "real_structure_general_form_is_typed": real["general_form"]
        == "J(1)=1, J(nu)=lambda nu",
        "trace_equation_selects_lambda_one": real["unique_solution"] == "lambda=1",
        "real_structure_matrix_is_identity": real["matrix_on_basis"]
        == [[1, 0], [0, 1]],
        "real_fixed_locus_is_two_dimensional": real["fixed_locus"]
        == "span_R{1,nu}",
        "real_structure_is_hodge_compatible": real["hodge_compatible"],
        "full_real_slice_is_not_claimed": real["full_physical_field_real_slice_selected"]
        is False,
        "RCE_declared_inputs_are_retained": density["declared_inputs"]
        == ["A_QG", "A_causal"],
        "response_volume_witness_is_120": density["exact_witness"]["response_volume_density"]
        == "120",
        "coframe_volume_witness_is_120": density["exact_witness"]["coframe_volume_density"]
        == "120",
        "internal_fiber_factor_is_one": density["exact_witness"]["internal_fiber_factor"]
        == "1",
        "product_volume_reduces_to_120": density["exact_witness"]["reduced_product_volume_density"]
        == "120",
        "time_reversal_preserves_density": density["time_orientation_reversal_preserves_density"],
        "A_QG_selection_is_not_claimed": density["primitive_A_QG_selection_proved"]
        is False,
        "A_causal_origin_is_not_claimed": density["binary_A_causal_origin_proved"]
        is False,
        "field_profile_is_unit": retract["field_profile"] == "1",
        "antifield_profile_is_orientation": retract["antifield_profile"] == "nu",
        "fiber_degree_shift_is_minus_six": retract["fiber_degree_shift"] == -6,
        "field_antifield_internal_pairing_is_one": retract["internal_field_antifield_pairing"]
        == "tau(1*nu)=1",
        "lifted_pairing_is_identity": as_fraction_matrix(retract["lifted_field_dual_pairing"])
        == [[Fraction(int(i == j)) for j in range(3)] for i in range(3)],
        "odd_symplectic_rank_recomputes": rank(odd_symplectic)
        == retract["odd_symplectic_rank"]
        == 6,
        "odd_symplectic_determinant_recomputes": determinant(odd_symplectic)
        == Fraction(retract["odd_symplectic_determinant"])
        == 1,
        "all_action_witness_residuals_vanish": all(
            row["residual"] == "0" and row["lower"] == row["reduced"]
            for row in retract["action_sample_rows"]
        ),
        "profile_reduction_is_identity": retract["reduction_after_lift"]
        == "IDENTITY",
        "upper_action_source_is_not_claimed": retract["independent_upper_action_source_proved"]
        is False,
        "pre_normalization_rank_recomputes": rank(pre_jacobian)
        == normalization["pre_normalization_rank"]
        == 2,
        "normalization_tangent_is_f0_only": normalization["normalized_tangent"]
        == [1, 0],
        "post_normalization_rank_recomputes": rank(post_jacobian)
        == normalization["post_normalization_rank"]
        == 1,
        "post_normalization_direction_is_common": post_jacobian
        == [[Fraction(1)]] * 5,
        "action_quantum_is_preserved": normalization["action_quantum_transport"]
        == "alpha_upper=alpha_lower=f0/hbar",
        "no_new_normalization_primitive": normalization["new_continuous_normalization_primitives"]
        == 0,
        "all_ten_bridge_clauses_are_audited": len(bridge_rows) == 11
        and set(bridge_rows)
        == {
            "C0_base_and_source",
            "C1_primal_contraction",
            "C2_cotangent_lift",
            "C3_representation_and_phase",
            "C4_density_and_normalization",
            "C5_field_only_action",
            "C6_BV_differential_and_action",
            "C7_reality_statistics_grading",
            "C8_gauge_fixing_and_domain",
            "C9_BV_pushforward",
            "C10_provenance_and_parameters",
        },
        "no_full_bridge_clause_is_claimed_closed": not any(
            audit[key]["closed"] for key in bridge_rows
        ),
        "density_clause_advances_only_at_profile_tier": audit["C4_density_and_normalization"]["state"]
        == "EXACT_ON_SELECTED_BRANCH_NORMALIZED_PROFILE",
        "reality_clause_advances_only_at_profile_tier": audit["C7_reality_statistics_grading"]["state"]
        == "EXACT_ON_INTERNAL_ORIENTATION_PROFILE",
        "field_action_clause_remains_right_inverse_only": audit["C5_field_only_action"]["state"]
        == "RIGHT_INVERSE_ONLY",
        "global_decision_remains_auxiliary": audit["global_decision"]
        == "AUXILIARY_COTANGENT_REDUCTION_ONLY"
        and audit["global_decision_changed"] is False,
        "one_action_primitive_is_preserved": parameters["shared_action_primitives_before_T50"]
        == parameters["shared_action_primitives_after_T50"]
        == 1,
        "zero_observed_inputs_are_added": parameters["observed_inputs_added"] == 0,
        "zero_continuous_parameters_are_added": parameters["continuous_action_parameters_added"]
        == parameters["continuous_density_parameters_added"]
        == 0,
        "alpha_source_value_remains_open": parameters["strict_source_value_for_alpha"]
        == "open",
        "binary_orientation_is_not_amplitude": parameters["binary_orientation_is_continuous_amplitude"]
        is False,
        "H4_T17_no_go_is_preserved": h4_t17["index_obstruction"]["minimum_complement_cohomology_dimension"]
        == 2
        and orientation["unresolved_complement_dimension"] == 86,
        "H4_T18_no_go_is_preserved": h4_t18["checks"]["positive_hessian_is_not_claimed_to_select_chirality_orientation"],
        "H4_T16_source_boundary_is_preserved": h4_t16["bv_right_inverse"]["source_selection"]
        == "NOT_PROVED",
        "H4_T15_global_boundary_is_preserved": h4_t15["selection_boundary"]["B_ACTION_01_closed"]
        is False,
        "RCE_branch_conditions_are_preserved": rce["status"]["primitive_MTT_selection_of_A_QG"]
        == "OPEN"
        and rce["status"]["origin_of_A_causal_time_orientation"]
        == "OPEN_ONE_BINARY_DATUM",
        "T49_alpha_boundary_is_preserved": t49["one_shared_primitive_ledger"]["strict_source_value_for_alpha"]
        == "open",
        "B_GEO_remains_open": boundary["B_GEO_01_closed"] is False,
        "B_ACTION_remains_open": boundary["B_ACTION_01_closed"] is False,
        "B_QFT_remains_open": boundary["B_QFT_02_closed"] is False,
        "physical_gates_remain_zero": boundary["physical_gates"]
        == {"accepted": 0, "total": 3},
        "physical_packets_remain_zero": boundary["physical_packets"]
        == {"accepted": 0, "total": 3},
        "physical_rows_remain_zero": boundary["physical_rows"]
        == {"accepted": 0, "total": 7},
        "theorem_declares_profile_not_full_real_slice": "is not the Majorana, charge-conjugation or Hermitian reality theorem"
        in theorem_text,
        "theorem_declares_right_inverse_not_source": "Equation (5.4) is a right inverse, not a source theorem."
        in theorem_text,
        "theorem_keeps_global_decision": "AUXILIARY_COTANGENT_REDUCTION_ONLY"
        in theorem_text,
    }
    checks.update({f"independent::{name}": passed for name, passed in independent.items()})

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T50 independent checks failed: {failed}")

    print(f"CBF.T50 verification passed {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
