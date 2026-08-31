#!/usr/bin/env python3
"""Independently verify the CBF.T51 Hodge and real-carrier packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_oriented_hodge_real_carrier_source_lock.json"
SCHEMA_PATH = ROOT / "q79_oriented_hodge_real_carrier_contract.schema.json"
THEOREM_PATH = ROOT / "Q79OrientedHodgeStarAndConjugatePairedRealCarrierCompilerTheorem_v1.md"
PACKET_PATH = ROOT / "q79_oriented_hodge_real_carrier.packet.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def as_matrix(raw: list[list[Any]]) -> list[list[Fraction]]:
    return [[Fraction(str(entry)) for entry in row] for row in raw]


def zeros(rows: int, columns: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def eye(size: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def trans(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    right_columns = trans(right)
    return [
        [sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in right_columns]
        for row in left
    ]


def add(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [[a + b for a, b in zip(x, y)] for x, y in zip(left, right)]


def subtract(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [[a - b for a, b in zip(x, y)] for x, y in zip(left, right)]


def scalar(matrix: list[list[Fraction]], value: Fraction) -> list[list[Fraction]]:
    return [[value * entry for entry in row] for row in matrix]


def matrix_rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
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
            coefficient = work[row][column]
            if coefficient:
                work[row] = [
                    entry - coefficient * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
    return pivot_row


def determinant_diagonal(entries: list[Fraction]) -> Fraction:
    result = Fraction(1)
    for entry in entries:
        result *= entry
    return result


def parse_label(label: str) -> tuple[int, ...]:
    if label == "1":
        return ()
    if label == "nu":
        return (1, 2, 3, 4, 5, 6)
    if not label.startswith("e"):
        raise ValueError(f"unknown exterior label: {label}")
    return tuple(int(character) for character in label[1:])


def sign_of(sequence: tuple[int, ...]) -> int:
    count = 0
    for left in range(len(sequence)):
        for right in range(left + 1, len(sequence)):
            count += int(sequence[left] > sequence[right])
    return -1 if count % 2 else 1


def set_complement(indices: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(index for index in range(1, 7) if index not in indices)


def wedge_coefficient(
    left: tuple[int, ...], right: tuple[int, ...]
) -> int:
    if set(left).intersection(right):
        return 0
    return sign_of(left + right)


def expected_kappa(rank: int) -> list[list[Fraction]]:
    doubled = 2 * rank
    swap = zeros(doubled, doubled)
    for column in range(doubled):
        row = column + rank if column < rank else column - rank
        swap[row][column] = Fraction(1)
    result = zeros(2 * doubled, 2 * doubled)
    for row in range(doubled):
        for column in range(doubled):
            result[row][column] = swap[row][column]
            result[doubled + row][doubled + column] = -swap[row][column]
    return result


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

    payload_core = deepcopy(packet)
    payload_core.pop("checks")
    payload_core.pop("check_summary")
    stored_payload_hash = payload_core.pop("exact_payload_sha256")

    hodge = packet["oriented_exterior_hodge"]
    orientation = packet["normalized_orientation_composition"]
    shape = packet["same_volume_metric_shape_nogo"]
    real = packet["conjugate_paired_real_carrier"]
    covariance = packet["operator_covariance"]
    q79 = packet["q79_instantiation_boundary"]
    ledger = packet["parameter_ledger"]
    boundary = packet["physical_boundary"]

    basis = [parse_label(label) for label in hodge["basis_order"]]
    table = hodge["complete_signed_permutation_table"]
    table_by_input = {row["input"]: row for row in table}
    degree_counts = [sum(int(len(indices) == degree) for indices in basis) for degree in range(7)]

    independent_table = []
    for column, indices in enumerate(basis):
        target = set_complement(indices)
        target_label = hodge["basis_order"][basis.index(target)]
        independent_table.append(
            {
                "column": column,
                "input": hodge["basis_order"][column],
                "degree": len(indices),
                "row": basis.index(target),
                "output": target_label,
                "sign": sign_of(indices + target),
            }
        )

    star_square = True
    wedge_star = True
    wedge_count = 0
    for indices in basis:
        target = set_complement(indices)
        actual = sign_of(indices + target) * sign_of(target + indices)
        star_square &= actual == (-1) ** (len(indices) * (6 - len(indices)))
    for degree in range(7):
        degree_basis = [entry for entry in basis if len(entry) == degree]
        for left, right in itertools.product(degree_basis, repeat=2):
            right_complement = set_complement(right)
            actual = wedge_coefficient(left, right_complement) * sign_of(right + right_complement)
            wedge_star &= actual == int(left == right)
            wedge_count += 1

    metric_diagonal = [Fraction(entry) for entry in shape["metric_diagonal"]]
    coframe_lengths = [Fraction(entry) for entry in shape["coframe_lengths"]]
    volume = determinant_diagonal(coframe_lengths)
    deformed_by_input = {
        row["input"]: row for row in shape["full_deformed_star_table"]
    }
    deformed_table_matches = True
    changed_rows = 0
    for label, indices in zip(hodge["basis_order"], basis):
        denominator = determinant_diagonal([metric_diagonal[index - 1] for index in indices])
        expected = Fraction(sign_of(indices + set_complement(indices))) * volume / denominator
        actual = Fraction(deformed_by_input[label]["coefficient"])
        deformed_table_matches &= actual == expected
        changed_rows += int(actual != Fraction(sign_of(indices + set_complement(indices))))

    kappa = as_matrix(real["kappa_matrix"])
    connection = as_matrix(real["unitary_connection_witness"]["realified_matrix"])
    q = as_matrix(covariance["witness_Q"])
    q_adjoint = as_matrix(covariance["witness_Q_adjoint"])
    laplacian = as_matrix(covariance["witness_laplacian"])
    projector = as_matrix(covariance["witness_harmonic_projector"])
    green = as_matrix(covariance["witness_reduced_green"])
    homotopy = as_matrix(covariance["witness_homotopy"])
    size = len(kappa)
    zero = zeros(size, size)
    identity = eye(size)

    independent_laplacian = add(multiply(q_adjoint, q), multiply(q, q_adjoint))
    contraction = add(multiply(q, homotopy), multiply(homotopy, q))
    expected_contraction = subtract(identity, projector)
    source_t50 = load_json(source_paths["T50_PACKET"])
    source_h4_t17 = load_json(source_paths["H4_T17_CERT"])
    source_proto = load_json(source_paths["PROTOSPINOR_HODGE_TABLE"])
    source_fm = load_json(source_paths["Q79_FM_HYM_FRONTIER"])
    source_hodge_audit = load_json(source_paths["Q79_HODGE_ACTION_AUDIT"])

    checks: dict[str, bool] = {
        **{f"builder::{name}": passed for name, passed in packet["checks"].items()},
        **{f"source::{name}": passed for name, passed in source_hashes.items()},
        "payload_hash_recomputes": canonical_hash(payload_core) == stored_payload_hash,
        "schema_name_matches": packet["schema"] == schema["$id"],
        "claim_id_matches": packet["claim_id"] == schema["properties"]["claim_id"]["const"],
        "schema_required_fields_exactly_present": set(schema["required"]) == set(packet),
        "basis_dimension_recomputes": len(basis) == 64,
        "basis_has_no_duplicates": len(set(basis)) == 64,
        "degree_counts_recompute": degree_counts == [1, 6, 15, 20, 15, 6, 1],
        "complete_table_recomputes_independently": table == independent_table,
        "complete_table_is_bijective": len({row["row"] for row in table}) == 64,
        "star_square_recomputes": star_square,
        "wedge_star_recomputes": wedge_star,
        "wedge_pair_count_recomputes": wedge_count == 924,
        "unit_orientation_rows_recompute": table_by_input["1"]["output"] == "nu" and table_by_input["nu"]["output"] == "1" and table_by_input["1"]["sign"] == table_by_input["nu"]["sign"] == 1,
        "T50_block_matches": orientation["T50_hodge_block"] == [[0, 1], [1, 0]],
        "T50_action_primitive_is_inherited": source_t50["parameter_ledger"]["shared_action_primitives_after_T50"] == 1,
        "metric_determinant_recomputes": determinant_diagonal(metric_diagonal) == 1,
        "metric_volume_recomputes": volume == 1,
        "metric_is_Hermitian_in_declared_pairs": metric_diagonal[0] == metric_diagonal[1] and metric_diagonal[2] == metric_diagonal[3] and metric_diagonal[4] == metric_diagonal[5],
        "deformed_star_table_recomputes": deformed_table_matches,
        "deformed_star_changes_shape": changed_rows == shape["shape_rows_changed"] and changed_rows > 0,
        "orientation_survives_deformation": Fraction(deformed_by_input["1"]["coefficient"]) == 1 and Fraction(deformed_by_input["nu"]["coefficient"]) == 1,
        "e1_e3_witness_recomputes": Fraction(deformed_by_input["e1"]["coefficient"]) == Fraction(1, 4) and Fraction(deformed_by_input["e3"]["coefficient"]) == 4,
        "Hermitian_shape_dimension_is_eight": shape["fixed_complex_structure_volume_one_Hermitian_shape_dimension"] == 8,
        "kappa_matrix_recomputes": kappa == expected_kappa(real["witness_original_complex_rank"]),
        "kappa_is_involution": multiply(kappa, kappa) == identity,
        "kappa_fixed_rank_recomputes": size - matrix_rank(subtract(kappa, identity)) == real["fixed_real_rank"],
        "kappa_antifixed_rank_recomputes": size - matrix_rank(add(kappa, identity)) == real["anti_fixed_real_rank"],
        "connection_is_skew": trans(connection) == scalar(connection, Fraction(-1)),
        "connection_commutes_with_kappa": multiply(connection, kappa) == multiply(kappa, connection),
        "Q_is_nilpotent": multiply(q, q) == zero,
        "Q_adjoint_recomputes": q_adjoint == trans(q),
        "Q_commutes_with_kappa": multiply(q, kappa) == multiply(kappa, q),
        "Q_adjoint_commutes_with_kappa": multiply(q_adjoint, kappa) == multiply(kappa, q_adjoint),
        "laplacian_recomputes": laplacian == independent_laplacian,
        "laplacian_commutes_with_kappa": multiply(laplacian, kappa) == multiply(kappa, laplacian),
        "projector_is_idempotent": multiply(projector, projector) == projector,
        "projector_commutes_with_kappa": multiply(projector, kappa) == multiply(kappa, projector),
        "Green_is_reduced_inverse": multiply(laplacian, green) == subtract(identity, projector) and multiply(green, laplacian) == subtract(identity, projector),
        "Green_commutes_with_kappa": multiply(green, kappa) == multiply(kappa, green),
        "contraction_identity_recomputes": contraction == expected_contraction,
        "homotopy_side_conditions_recompute": multiply(homotopy, homotopy) == zero and multiply(projector, homotopy) == zero and multiply(homotopy, projector) == zero,
        "harmonic_rank_recomputes": matrix_rank(projector) == covariance["harmonic_rank"] == 4,
        "positive_rank_recomputes": matrix_rank(laplacian) == covariance["positive_rank"] == 8,
        "proto_wedge_row_was_open": source_proto["what_remains_open"]["oriented_full_Hodge_star_wedge_sign_table"],
        "compiler_closes_only_wedge_row": q79["oriented_full_Hodge_star_wedge_sign_table"].endswith("COMPILER_TIER") and q79["selected_metric_endomorphism_coefficients"] == "OPEN",
        "H4_T17_86_mode_boundary_is_preserved": source_h4_t17["index_obstruction"]["complement_dimension"] == 86 and q79["other_86_topology_mode_disposition"].startswith("OPEN"),
        "prior_shared_circle_no_go_is_preserved": source_hodge_audit["theorems"]["circle_no_go"]["name"] == "SharedCircleDoesNotSelectHodgeChannelRatioTheorem",
        "common_HYM_chamber_is_still_open": source_fm["compiler_checks"]["common_visible_hidden_chamber_remains_open"],
        "realification_is_not_majorana_claim": real["does_not_select_Majorana_condition"],
        "realification_is_not_chirality_claim": real["does_not_select_chiral_index"],
        "one_action_primitive_remains": ledger["shared_action_primitives_before_T51"] == ledger["shared_action_primitives_after_T51"] == 1,
        "no_new_parameter_or_selector": ledger["continuous_parameters_added"] == ledger["discrete_selectors_added"] == ledger["observed_values_used"] == ledger["fitted_values_used"] == 0,
        "metric_shape_is_source_field_not_parameter": not ledger["metric_shape_components_are_free_parameters"] and ledger["metric_shape_components_are_endpoint_fields_to_compute"],
        "physical_blockers_remain_open": not any(boundary[key] for key in ["B_HS_01_closed", "B_GEO_01_closed", "B_ACTION_01_closed", "B_QFT_02_closed"]),
        "physical_counters_remain_zero": boundary["physical_gates"] == {"accepted": 0, "total": 3} and boundary["physical_packets"] == {"accepted": 0, "total": 3} and boundary["physical_rows"] == {"accepted": 0, "total": 7},
        "global_H4_decision_is_unchanged": boundary["global_H4_T15_decision"] == "AUXILIARY_COTANGENT_REDUCTION_ONLY",
        "theorem_contains_exact_scope": "complete exact 64-state" in theorem_text and "does not select the physical q79 metric" in theorem_text,
        "frontier_names_actual_next_source": "source-hashed q79 metric" in packet["frontier_delta"],
    }

    summary = {
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    print(json.dumps(summary, indent=2))
    if not summary["all_passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit(f"failed checks: {failed}")


if __name__ == "__main__":
    main()
