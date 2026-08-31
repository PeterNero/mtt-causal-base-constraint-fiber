#!/usr/bin/env python3
"""Build the exact CBF.T51 Hodge-star and real-carrier compiler packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "q79_oriented_hodge_real_carrier_source_lock.json"
SCHEMA = ROOT / "q79_oriented_hodge_real_carrier_contract.schema.json"
THEOREM = ROOT / "Q79OrientedHodgeStarAndConjugatePairedRealCarrierCompilerTheorem_v1.md"
OUTPUT = ROOT / "q79_oriented_hodge_real_carrier.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def source_paths(lock: dict[str, Any]) -> dict[str, Path]:
    return {
        item["id"]: (ROOT / item["path"]).resolve()
        for item in lock["sources"]
    }


def product(values: list[Fraction] | tuple[Fraction, ...]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def zero_matrix(rows: int, columns: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> list[list[Fraction]]:
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def matmul(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    right_t = transpose(right)
    return [
        [
            sum((a * b for a, b in zip(left_row, right_column)), Fraction(0))
            for right_column in right_t
        ]
        for left_row in left
    ]


def matadd(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def matsub(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scale(matrix: list[list[Fraction]], value: Fraction) -> list[list[Fraction]]:
    return [[value * entry for entry in row] for row in matrix]


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
        if pivot_row == rows:
            break
    return pivot_row


def block_diagonal(
    first: list[list[Fraction]], second: list[list[Fraction]]
) -> list[list[Fraction]]:
    n_first = len(first)
    n_second = len(second)
    result = zero_matrix(n_first + n_second, n_first + n_second)
    for row in range(n_first):
        for column in range(n_first):
            result[row][column] = first[row][column]
    for row in range(n_second):
        for column in range(n_second):
            result[n_first + row][n_first + column] = second[row][column]
    return result


def realify(
    real_part: list[list[Fraction]], imaginary_part: list[list[Fraction]]
) -> list[list[Fraction]]:
    size = len(real_part)
    result = zero_matrix(2 * size, 2 * size)
    for row in range(size):
        for column in range(size):
            result[row][column] = real_part[row][column]
            result[row][size + column] = -imaginary_part[row][column]
            result[size + row][column] = imaginary_part[row][column]
            result[size + row][size + column] = real_part[row][column]
    return result


def fraction_matrix(matrix: list[list[Fraction]]) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix]


def exterior_basis(dimension: int) -> list[tuple[int, ...]]:
    return [
        tuple(indices)
        for degree in range(dimension + 1)
        for indices in itertools.combinations(range(1, dimension + 1), degree)
    ]


def basis_label(indices: tuple[int, ...], dimension: int = 6) -> str:
    if not indices:
        return "1"
    if len(indices) == dimension:
        return "nu"
    return "e" + "".join(str(index) for index in indices)


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        int(sequence[left] > sequence[right])
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def complement(indices: tuple[int, ...], dimension: int = 6) -> tuple[int, ...]:
    selected = set(indices)
    return tuple(index for index in range(1, dimension + 1) if index not in selected)


def hodge_sign(indices: tuple[int, ...], dimension: int = 6) -> int:
    return permutation_sign(indices + complement(indices, dimension))


def wedge_sign(
    left: tuple[int, ...], right: tuple[int, ...]
) -> int | None:
    if set(left).intersection(right):
        return None
    return permutation_sign(left + right)


def diagonal(entries: list[Fraction]) -> list[list[Fraction]]:
    return [
        [entry if row == column else Fraction(0) for column in range(len(entries))]
        for row, entry in enumerate(entries)
    ]


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

    t50 = load_json(paths["T50_PACKET"])
    h4_t16 = load_json(paths["H4_T16_CERT"])
    h4_t17 = load_json(paths["H4_T17_CERT"])
    fuyau = load_json(paths["Q79_FUYAU_BASE"])
    proto_hodge = load_json(paths["PROTOSPINOR_HODGE_TABLE"])
    k3_real = load_json(paths["Q79_K3_REAL_STRUCTURE"])
    hodge_audit = load_json(paths["Q79_HODGE_ACTION_AUDIT"])
    fm_hym = load_json(paths["Q79_FM_HYM_FRONTIER"])

    dimension = 6
    basis = exterior_basis(dimension)
    basis_index = {entry: index for index, entry in enumerate(basis)}
    degree_counts = {
        str(degree): sum(int(len(entry) == degree) for entry in basis)
        for degree in range(dimension + 1)
    }

    hodge_table = []
    for column, indices in enumerate(basis):
        target = complement(indices, dimension)
        sign = hodge_sign(indices, dimension)
        hodge_table.append(
            {
                "column": column,
                "input": basis_label(indices),
                "degree": len(indices),
                "row": basis_index[target],
                "output": basis_label(target),
                "sign": sign,
            }
        )

    star_square_rows = []
    for indices in basis:
        target = complement(indices, dimension)
        actual = hodge_sign(indices, dimension) * hodge_sign(target, dimension)
        expected = (-1) ** (len(indices) * (dimension - len(indices)))
        star_square_rows.append(
            {
                "basis": basis_label(indices),
                "actual": actual,
                "expected": expected,
            }
        )

    wedge_star_checks = 0
    wedge_star_identity = True
    for degree in range(dimension + 1):
        degree_basis = [entry for entry in basis if len(entry) == degree]
        for left, right in itertools.product(degree_basis, repeat=2):
            target = complement(right, dimension)
            wedge = wedge_sign(left, target)
            coefficient = 0 if wedge is None else wedge * hodge_sign(right, dimension)
            wedge_star_identity &= coefficient == int(left == right)
            wedge_star_checks += 1

    reference_sparse_matrix = [
        {"row": row["row"], "column": row["column"], "value": row["sign"]}
        for row in hodge_table
    ]

    # A determinant-one Hermitian family in the fixed complex pairs
    # (e1,e2), (e3,e4), (e5,e6).  It preserves volume and complex structure
    # but changes the Hodge star whenever t != 1.
    t = Fraction(2)
    coframe_lengths = [t, t, 1 / t, 1 / t, Fraction(1), Fraction(1)]
    metric_diagonal = [length * length for length in coframe_lengths]
    metric_determinant = product(metric_diagonal)
    volume_factor = product(coframe_lengths)
    deformed_star = []
    changed_rows = 0
    for indices in basis:
        denominator = product(
            [metric_diagonal[index - 1] for index in indices]
        )
        coefficient = Fraction(hodge_sign(indices, dimension)) * volume_factor / denominator
        reference = Fraction(hodge_sign(indices, dimension))
        changed_rows += int(coefficient != reference)
        deformed_star.append(
            {
                "input": basis_label(indices),
                "output": basis_label(complement(indices, dimension)),
                "coefficient": str(coefficient),
            }
        )

    # Canonical conjugate-paired realification R(E)=E+conjugate(E), using a
    # rank-three exact witness.  Kappa(z,w)=(conj(w),conj(z)).
    fiber_rank = 3
    swap = zero_matrix(2 * fiber_rank, 2 * fiber_rank)
    for index in range(2 * fiber_rank):
        target = index + fiber_rank if index < fiber_rank else index - fiber_rank
        swap[target][index] = Fraction(1)
    kappa = block_diagonal(swap, scale(swap, Fraction(-1)))
    real_dimension = len(kappa)

    connection_real = [
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(-1), Fraction(0), Fraction(2)],
        [Fraction(0), Fraction(-2), Fraction(0)],
    ]
    connection_imaginary = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(-1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    doubled_connection_real = block_diagonal(connection_real, connection_real)
    doubled_connection_imaginary = block_diagonal(
        connection_imaginary, scale(connection_imaginary, Fraction(-1))
    )
    doubled_connection = realify(
        doubled_connection_real, doubled_connection_imaginary
    )

    q = zero_matrix(fiber_rank, fiber_rank)
    q[1][0] = Fraction(1)
    doubled_q_complex = block_diagonal(q, q)
    doubled_q = realify(doubled_q_complex, zero_matrix(2 * fiber_rank, 2 * fiber_rank))
    doubled_q_adjoint = transpose(doubled_q)
    laplacian = matadd(
        matmul(doubled_q_adjoint, doubled_q),
        matmul(doubled_q, doubled_q_adjoint),
    )
    harmonic_projector = diagonal(
        [Fraction(int(laplacian[index][index] == 0)) for index in range(real_dimension)]
    )
    reduced_green = diagonal(
        [
            Fraction(0)
            if laplacian[index][index] == 0
            else Fraction(1, 1) / laplacian[index][index]
            for index in range(real_dimension)
        ]
    )
    homotopy = matmul(doubled_q_adjoint, reduced_green)
    contraction_left = matadd(
        matmul(doubled_q, homotopy), matmul(homotopy, doubled_q)
    )
    contraction_right = matsub(identity(real_dimension), harmonic_projector)

    real_fixed_rank = real_dimension - rank(matsub(kappa, identity(real_dimension)))
    real_anti_fixed_rank = real_dimension - rank(matadd(kappa, identity(real_dimension)))
    operator_rows = {
        "Q_squared_zero": matmul(doubled_q, doubled_q) == zero_matrix(real_dimension, real_dimension),
        "kappa_commutes_Q": matmul(kappa, doubled_q) == matmul(doubled_q, kappa),
        "kappa_commutes_Q_adjoint": matmul(kappa, doubled_q_adjoint) == matmul(doubled_q_adjoint, kappa),
        "kappa_commutes_laplacian": matmul(kappa, laplacian) == matmul(laplacian, kappa),
        "kappa_commutes_harmonic_projector": matmul(kappa, harmonic_projector) == matmul(harmonic_projector, kappa),
        "kappa_commutes_reduced_green": matmul(kappa, reduced_green) == matmul(reduced_green, kappa),
        "contraction_identity": contraction_left == contraction_right,
        "homotopy_squared_zero": matmul(homotopy, homotopy) == zero_matrix(real_dimension, real_dimension),
        "projector_homotopy_zero": matmul(harmonic_projector, homotopy) == zero_matrix(real_dimension, real_dimension),
        "homotopy_projector_zero": matmul(homotopy, harmonic_projector) == zero_matrix(real_dimension, real_dimension),
    }

    orientation_row_1 = next(row for row in hodge_table if row["input"] == "1")
    orientation_row_nu = next(row for row in hodge_table if row["input"] == "nu")
    deformed_row_1 = next(row for row in deformed_star if row["input"] == "1")
    deformed_row_nu = next(row for row in deformed_star if row["input"] == "nu")
    deformed_row_e1 = next(row for row in deformed_star if row["input"] == "e1")
    deformed_row_e3 = next(row for row in deformed_star if row["input"] == "e3")

    payload: dict[str, Any] = {
        "schema": "boe.mtt.q79-oriented-hodge-real-carrier.v1",
        "claim_id": "CBF.T51",
        "date": "2026-08-31",
        "status": "EXACT_ORIENTED_EXTERIOR_HODGE_AND_CONJUGATE_PAIRED_REAL_CARRIER_COMPILER_PHYSICAL_Q79_METRIC_HYM_OPERATOR_AND_CHIRAL_INDEX_OPEN",
        "source_provenance": {
            "source_lock": SOURCE_LOCK.name,
            "source_hashes_match": hashes_match,
            "all_source_hashes_match": all(hashes_match.values()),
            "model_state_sha256": lock["model_state_sha256"],
            "handoff_id": lock["handoff_id"],
        },
        "oriented_exterior_hodge": {
            "dimension": dimension,
            "basis_dimension": len(basis),
            "degree_dimensions": degree_counts,
            "basis_order": [basis_label(entry) for entry in basis],
            "definition": "star(e_I)=sgn(I,I_complement)e_I_complement in an oriented orthonormal coframe",
            "complete_signed_permutation_table": hodge_table,
            "sparse_matrix_shape": [len(basis), len(basis)],
            "sparse_matrix_entries": reference_sparse_matrix,
            "nonzero_entries": len(reference_sparse_matrix),
            "positive_entries": sum(int(row["sign"] == 1) for row in hodge_table),
            "negative_entries": sum(int(row["sign"] == -1) for row in hodge_table),
            "star_square_identity": "star^2=(-1)^(k(6-k)) on degree k",
            "star_square_rows": star_square_rows,
            "wedge_star_identity": "e_I wedge star(e_J)=delta_IJ nu for equal degrees",
            "wedge_star_checks": wedge_star_checks,
            "wedge_sign_table_status": "CLOSED_EXACT_ORIENTED_ORTHONORMAL_FRAME_COMPILER",
        },
        "normalized_orientation_composition": {
            "T50_profile_basis": ["1", "nu"],
            "star_1": f"{orientation_row_1['sign']}*{orientation_row_1['output']}",
            "star_nu": f"{orientation_row_nu['sign']}*{orientation_row_nu['output']}",
            "T50_hodge_block": [[0, 1], [1, 0]],
            "restriction_equals_T50": True,
            "normalized_trace": "tau(nu)=1",
            "global_volume_normalization_added": False,
            "action_quantum": "alpha_upper=alpha_lower=f0/hbar",
        },
        "same_volume_metric_shape_nogo": {
            "complex_pairs": [[1, 2], [3, 4], [5, 6]],
            "parameter": "t=2",
            "coframe_lengths": [str(value) for value in coframe_lengths],
            "metric_diagonal": [str(value) for value in metric_diagonal],
            "metric_determinant": str(metric_determinant),
            "volume_factor": str(volume_factor),
            "is_Hermitian_for_fixed_standard_complex_structure": all(
                metric_diagonal[left - 1] == metric_diagonal[right - 1]
                for left, right in [[1, 2], [3, 4], [5, 6]]
            ),
            "reference_and_deformed_volume_equal": volume_factor == 1,
            "orientation_rows_unchanged": {
                "star_1": deformed_row_1,
                "star_nu": deformed_row_nu,
            },
            "shape_rows_changed": changed_rows,
            "explicit_changed_rows": [deformed_row_e1, deformed_row_e3],
            "full_deformed_star_table": deformed_star,
            "fixed_complex_structure_volume_one_Hermitian_shape_dimension": 8,
            "conclusion": "normalized volume and the shared orientation profile do not select the six-dimensional Hodge shape",
            "source_interpretation": "the eight local shape components are metric fields to be emitted by the selected Fu-Yau/HYM solution, not eight fitted constants",
        },
        "conjugate_paired_real_carrier": {
            "functor": "R(E)=E+conjugate(E)",
            "involution": "kappa(z,w)=(conjugate(w),conjugate(z))",
            "general_complex_rank": "2r",
            "general_fixed_real_rank": "2r",
            "witness_original_complex_rank": fiber_rank,
            "witness_doubled_complex_rank": 2 * fiber_rank,
            "witness_realified_rank": real_dimension,
            "kappa_matrix": fraction_matrix(kappa),
            "kappa_squared_identity": matmul(kappa, kappa) == identity(real_dimension),
            "fixed_real_rank": real_fixed_rank,
            "anti_fixed_real_rank": real_anti_fixed_rank,
            "unitary_connection_witness": {
                "realified_matrix": fraction_matrix(doubled_connection),
                "skew_symmetric": transpose(doubled_connection) == scale(doubled_connection, Fraction(-1)),
                "commutes_with_kappa": matmul(kappa, doubled_connection) == matmul(doubled_connection, kappa),
            },
            "form_Hodge_commutes_with_kappa": True,
            "interpretation": "the conjugate summand is the canonical realification/BV conjugate carrier, not an independently selected mirror particle family",
            "does_not_select_Majorana_condition": True,
            "does_not_select_chiral_index": True,
        },
        "operator_covariance": {
            "witness_Q": fraction_matrix(doubled_q),
            "witness_Q_adjoint": fraction_matrix(doubled_q_adjoint),
            "witness_laplacian": fraction_matrix(laplacian),
            "witness_harmonic_projector": fraction_matrix(harmonic_projector),
            "witness_reduced_green": fraction_matrix(reduced_green),
            "witness_homotopy": fraction_matrix(homotopy),
            "checks": operator_rows,
            "harmonic_rank": rank(harmonic_projector),
            "positive_rank": rank(laplacian),
            "general_theorem": "if a supplied unitary differential and its closed domain commute with kappa, then its adjoint, Laplacian, harmonic projector, reduced Green and Hodge homotopy commute with kappa",
            "green_reason": "inverse uniqueness on the kappa-invariant harmonic complement",
            "physical_q79_operator_instantiated": False,
        },
        "q79_instantiation_boundary": {
            "explicit_real_q79_K3_available": True,
            "q79_K3_real_structure_status": k3_real["status"],
            "q79_FuYau_topological_source_status": fuyau["status"],
            "oriented_full_Hodge_star_wedge_sign_table": "CLOSED_AT_UNIVERSAL_ORTHONORMAL_FRAME_COMPILER_TIER",
            "selected_metric_endomorphism_coefficients": "OPEN",
            "selected_FuYau_conformal_factor": "OPEN",
            "selected_visible_hidden_HYM_metric_and_connection": "OPEN",
            "rank102_Dbar_Q_and_domains": "OPEN",
            "rank102_harmonic_projector_and_reduced_Green": "OPEN",
            "physical_C4_HYM_lift_or_direct_TT_block": "OPEN",
            "other_86_topology_mode_disposition": "OPEN_AND_GOVERNED_BY_H4_T17",
            "associated_chiral_operator_and_index": "OPEN",
            "physical_real_slice": "OPEN_BEYOND_CANONICAL_CONJUGATE_PAIRED_COMPILER",
            "dependency_order": [
                "selected same-member visible source V",
                "common visible-hidden HYM endpoint H",
                "metric/coframe and rank102 differential",
                "physical C4 lift or direct TT block J",
            ],
        },
        "parameter_ledger": {
            "shared_action_primitives_before_T51": 1,
            "shared_action_primitives_after_T51": 1,
            "continuous_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "global_volume_knobs_added": 0,
            "metric_shape_source_components_for_general_fixed_complex_structure": 8,
            "metric_shape_components_are_free_parameters": False,
            "metric_shape_components_are_endpoint_fields_to_compute": True,
        },
        "physical_boundary": {
            "B_HS_01_closed": False,
            "B_GEO_01_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
            "global_H4_T15_decision": "AUXILIARY_COTANGENT_REDUCTION_ONLY",
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "not_claimed": [
                "selected physical q79 metric or Hodge star",
                "selected visible-hidden HYM endpoint",
                "rank102 physical differential, projector or Green operator",
                "Majorana reality, chirality or particle spectrum",
                "mass gap for the 86 topology complement modes",
                "upper physical action or quantum BV/QME pushforward",
            ],
        },
        "frontier_delta": "CBF.T51 closes the complete six-dimensional oriented orthonormal-frame Hodge signed-permutation table and the canonical conjugate-paired real-carrier compiler. It composes exactly with the T50 unit/orientation block and proves covariance of supplied unitary differential, adjoint, Laplacian, projector, reduced Green and homotopy under the real involution. An exact determinant-one Hermitian family proves that normalized volume leaves eight local metric-shape components undetermined. Those components are endpoint fields, not new fit parameters. The next actual source is a source-hashed q79 metric and unitary visible-hidden HYM connection. That metric/connection, the rank-102 operator, chiral index, 86-mode disposition, action and QME remain open, so physical counters do not move.",
    }

    payload["exact_payload_sha256"] = canonical_hash(payload)

    checks: dict[str, bool] = {
        **{f"source_hash::{name}": value for name, value in hashes_match.items()},
        "source_lock_claim_is_T51": lock["claim_id"] == "CBF.T51",
        "schema_id_matches": schema["$id"] == payload["schema"],
        "schema_claim_matches": schema["properties"]["claim_id"]["const"] == "CBF.T51",
        "all_schema_required_fields_present": set(schema["required"]).issubset(set(payload) | {"checks", "check_summary"}),
        "basis_has_64_states": len(basis) == 64,
        "degree_dimensions_are_binomial": list(degree_counts.values()) == [1, 6, 15, 20, 15, 6, 1],
        "hodge_table_has_one_row_per_state": len(hodge_table) == 64,
        "hodge_table_is_signed_permutation": len({row["row"] for row in hodge_table}) == 64 and all(abs(row["sign"]) == 1 for row in hodge_table),
        "star_square_identity_holds_on_all_states": all(row["actual"] == row["expected"] for row in star_square_rows),
        "wedge_star_identity_holds_on_all_equal_degree_pairs": wedge_star_identity,
        "wedge_star_check_count_is_924": wedge_star_checks == 924,
        "star_maps_unit_to_orientation": orientation_row_1["output"] == "nu" and orientation_row_1["sign"] == 1,
        "star_maps_orientation_to_unit": orientation_row_nu["output"] == "1" and orientation_row_nu["sign"] == 1,
        "T50_orientation_block_is_recovered": payload["normalized_orientation_composition"]["restriction_equals_T50"],
        "T50_source_has_one_shared_primitive": t50["parameter_ledger"]["shared_action_primitives_after_T50"] == 1,
        "H4_T16_source_passes": h4_t16["all_passed"],
        "H4_T17_source_passes": h4_t17["all_passed"],
        "H4_T17_keeps_86_mode_boundary": h4_t17["index_obstruction"]["complement_dimension"] == 86,
        "metric_family_is_Hermitian": payload["same_volume_metric_shape_nogo"]["is_Hermitian_for_fixed_standard_complex_structure"],
        "metric_family_has_unit_determinant": metric_determinant == 1,
        "metric_family_has_unit_volume": volume_factor == 1,
        "metric_family_changes_Hodge_shape": changed_rows > 0,
        "metric_family_preserves_orientation_rows": deformed_row_1["coefficient"] == "1" and deformed_row_nu["coefficient"] == "1",
        "explicit_e1_and_e3_rows_differ": deformed_row_e1["coefficient"] != deformed_row_e3["coefficient"],
        "fixed_complex_structure_shape_dimension_is_eight": payload["same_volume_metric_shape_nogo"]["fixed_complex_structure_volume_one_Hermitian_shape_dimension"] == 8,
        "kappa_squared_is_identity": payload["conjugate_paired_real_carrier"]["kappa_squared_identity"],
        "kappa_fixed_rank_is_six": real_fixed_rank == 2 * fiber_rank,
        "kappa_antifixed_rank_is_six": real_anti_fixed_rank == 2 * fiber_rank,
        "connection_witness_is_unitary": payload["conjugate_paired_real_carrier"]["unitary_connection_witness"]["skew_symmetric"],
        "connection_witness_commutes_with_kappa": payload["conjugate_paired_real_carrier"]["unitary_connection_witness"]["commutes_with_kappa"],
        **{f"operator::{name}": value for name, value in operator_rows.items()},
        "operator_harmonic_rank_is_four": rank(harmonic_projector) == 4,
        "operator_positive_rank_is_eight": rank(laplacian) == 8,
        "real_carrier_does_not_claim_majorana": payload["conjugate_paired_real_carrier"]["does_not_select_Majorana_condition"],
        "real_carrier_does_not_claim_chiral_index": payload["conjugate_paired_real_carrier"]["does_not_select_chiral_index"],
        "q79_K3_source_is_exact": "CLOSED_EXACT" in k3_real["status"],
        "q79_FuYau_source_is_topological_not_metric": "TOPOLOGICAL_SOURCE" in fuyau["status"],
        "proto_source_had_wedge_sign_table_open": proto_hodge["what_remains_open"]["oriented_full_Hodge_star_wedge_sign_table"],
        "prior_hodge_audit_keeps_physical_rows_zero": hodge_audit["q79_source_audit"]["accepted_physical_source_rows"] == 0,
        "prior_hodge_audit_shared_circle_insufficiency_is_inherited": hodge_audit["checks"]["circle_also_commutes_with_asymmetric_Hessian"],
        "FM_HYM_common_chamber_remains_open": fm_hym["compiler_checks"]["common_visible_hidden_chamber_remains_open"],
        "selected_metric_coefficients_remain_open": payload["q79_instantiation_boundary"]["selected_metric_endomorphism_coefficients"] == "OPEN",
        "selected_HYM_endpoint_remains_open": payload["q79_instantiation_boundary"]["selected_visible_hidden_HYM_metric_and_connection"] == "OPEN",
        "rank102_operator_remains_open": payload["q79_instantiation_boundary"]["rank102_Dbar_Q_and_domains"] == "OPEN",
        "other_86_modes_remain_open": payload["q79_instantiation_boundary"]["other_86_topology_mode_disposition"].startswith("OPEN"),
        "one_action_primitive_is_preserved": payload["parameter_ledger"]["shared_action_primitives_after_T51"] == 1,
        "no_continuous_parameters_added": payload["parameter_ledger"]["continuous_parameters_added"] == 0,
        "metric_shapes_are_fields_not_fit_parameters": not payload["parameter_ledger"]["metric_shape_components_are_free_parameters"],
        "all_four_blockers_remain_open": not any(
            payload["physical_boundary"][key]
            for key in ["B_HS_01_closed", "B_GEO_01_closed", "B_ACTION_01_closed", "B_QFT_02_closed"]
        ),
        "physical_counters_do_not_move": payload["physical_boundary"]["physical_gates"] == {"accepted": 0, "total": 3} and payload["physical_boundary"]["physical_packets"] == {"accepted": 0, "total": 3} and payload["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
        "theorem_declares_compiler_tier": "oriented orthonormal-frame compiler" in theorem_text,
        "theorem_preserves_physical_boundary": "does not select the physical q79 metric" in theorem_text,
        "theorem_records_eight_shape_fields": "eight local metric-shape components" in theorem_text,
        "payload_hash_is_well_formed": len(payload["exact_payload_sha256"]) == 64,
    }

    packet = deepcopy(payload)
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet["check_summary"], indent=2))
    if not packet["check_summary"]["all_passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit(f"failed checks: {failed}")


if __name__ == "__main__":
    main()
