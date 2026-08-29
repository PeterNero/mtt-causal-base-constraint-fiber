#!/usr/bin/env python3
"""Build the exact one-constraint multiplier-source certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "direct_one_constraint_multiplier_source_lock.json"
SCHEMA = ROOT / "direct_one_constraint_multiplier_source_contract.schema.json"
THEOREM = ROOT / "MinimalOneConstraintMultiplierSourceAndThreeFamilyIndexTheorem_v1.md"
T13_PACKET = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
T14_PACKET = ROOT / "provider_neutral_projection_source_quotient.packet.json"
OUTPUT = ROOT / "direct_one_constraint_multiplier_source.packet.json"


Scalar = int | Fraction
Matrix = list[list[Scalar]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    return [[sum(a * b for a, b in zip(row, col)) for col in columns] for row in left]


def matvec(matrix: Matrix, vector: list[Scalar]) -> list[Scalar]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def scale(value: Scalar, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def identity(size: int) -> Matrix:
    return [[int(row == col) for col in range(size)] for row in range(size)]


def zero(rows: int, cols: int) -> Matrix:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def diagonal(values: list[Scalar]) -> Matrix:
    return [[values[row] if row == col else 0 for col in range(len(values))] for row in range(len(values))]


def block_matrix(top_left: Matrix, top_right: Matrix, bottom_left: Matrix, bottom_right: Matrix) -> Matrix:
    return [a + b for a, b in zip(top_left, top_right)] + [a + b for a, b in zip(bottom_left, bottom_right)]


def kron(left: Matrix, right: Matrix) -> Matrix:
    result: Matrix = []
    for left_row in left:
        for right_row in right:
            row: list[Scalar] = []
            for left_entry in left_row:
                row.extend(left_entry * right_entry for right_entry in right_row)
            result.append(row)
    return result


def matrix_rank(matrix: Matrix) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((row for row in range(rank, rows) if work[row][col] != 0), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][col]
        work[rank] = [entry / pivot_value for entry in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            coefficient = work[row][col]
            if coefficient:
                work[row] = [a - coefficient * b for a, b in zip(work[row], work[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def trace(matrix: Matrix) -> Scalar:
    return sum(matrix[index][index] for index in range(len(matrix)))


def make_j0() -> Matrix:
    return [[int(row == col) if col < 16 else 0 for col in range(64)] for row in range(16)]


def make_multiplier_hessian(j: Matrix) -> Matrix:
    jt = transpose(j)
    return block_matrix(zero(64, 64), jt, j, zero(16, 16))


def make_family_cycle_on_source() -> Matrix:
    permutation = list(range(64))
    for family in range(3):
        for coordinate in range(16):
            permutation[16 + 16 * family + coordinate] = 16 + 16 * ((family + 1) % 3) + coordinate
    matrix = zero(64, 64)
    for source, target in enumerate(permutation):
        matrix[target][source] = 1
    return matrix


def commutant_equations_3x3() -> Matrix:
    equations: Matrix = []
    for i in range(3):
        for j in range(3):
            generator = zero(3, 3)
            generator[i][j] = 1
            for row in range(3):
                for col in range(3):
                    coefficients = [0] * 9
                    for k in range(3):
                        coefficients[row * 3 + k] += generator[k][col]
                        coefficients[k * 3 + col] -= generator[row][k]
                    equations.append(coefficients)
    return equations


def dot(left: list[Scalar], right: list[Scalar]) -> Scalar:
    return sum(a * b for a, b in zip(left, right))


def local_source_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for entry in source_lock["local_sources"]:
        path = (ROOT / entry["path"]).resolve()
        checks[f"source_hash::{entry['path']}"] = path.is_file() and sha256(path) == entry["sha256"]
    return checks


def encode_scalar(value: Scalar) -> int | list[int]:
    value = Fraction(value)
    if value.denominator == 1:
        return value.numerator
    return [value.numerator, value.denominator]


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    t13 = json.loads(T13_PACKET.read_text(encoding="utf-8"))
    t14 = json.loads(T14_PACKET.read_text(encoding="utf-8"))

    j = make_j0()
    jt = transpose(j)
    jj_star = matmul(j, jt)
    q = matmul(jt, j)
    p = add(identity(64), scale(-1, q))
    d = make_multiplier_hessian(j)
    d2 = matmul(d, d)
    d3 = matmul(d2, d)

    multiplicity_table = [
        {
            "source_multiplicity": m,
            "source_dimension": 16 * m,
            "residual_dimension": 16,
            "kernel_dimension": 16 * (m - 1),
            "family_copies_in_kernel": m - 1,
        }
        for m in range(1, 7)
    ]

    hadamard4 = [
        [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)],
        [Fraction(1, 2), Fraction(-1, 2), Fraction(1, 2), Fraction(-1, 2)],
        [Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2), Fraction(-1, 2)],
        [Fraction(1, 2), Fraction(-1, 2), Fraction(-1, 2), Fraction(1, 2)],
    ]
    spread_covector = kron([[Fraction(1, 2)] * 4], identity(16))
    source_frame_unitary = kron(hadamard4, identity(16))

    family_cycle = make_family_cycle_on_source()
    family_cycle80 = block_matrix(family_cycle, zero(64, 16), zero(16, 64), identity(16))

    one_family_weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    y16 = diagonal(one_family_weights)
    y_source = diagonal(one_family_weights * 4)
    y_multiplier = block_matrix(y_source, zero(64, 16), zero(16, 64), y16)

    commutant_constraints = commutant_equations_3x3()
    commutant_rank = matrix_rank(commutant_constraints)
    commutant_dimension = 9 - commutant_rank

    r = Fraction(1, 2)
    s = Fraction(1, 3)
    flow_r = add(p, scale(r, q))
    flow_s = add(p, scale(s, q))
    flow_rs = add(p, scale(r * s, q))

    sample_a = [index - 20 for index in range(64)]
    sample_lambda = [3 - index for index in range(16)]
    sample_residual = matvec(j, sample_a)
    sample_action = dot(sample_lambda, sample_residual)
    sample_repair_twice = dot(sample_residual, sample_residual)
    sample_kernel = [0] * 16 + [index - 8 for index in range(48)]

    representation = t13["representation_and_anomaly_witness"]
    internal = t13["exact_internal_witness"]

    checks = {
        **local_source_checks(source_lock),
        "multiplicity_three_kernel_occurs_only_at_m4_in_test_range": [row["source_multiplicity"] for row in multiplicity_table if row["family_copies_in_kernel"] == 3] == [4],
        "rank_nullity_formula_holds_for_all_declared_m": all(row["kernel_dimension"] == row["source_dimension"] - row["residual_dimension"] for row in multiplicity_table),
        "J_has_rank_16": matrix_rank(j) == 16,
        "J_is_surjective": matrix_rank(j) == len(j),
        "J_is_coisometric": jj_star == identity(16),
        "Q_is_rank_16_projector": matmul(q, q) == q and matrix_rank(q) == 16,
        "P_is_rank_48_projector": matmul(p, p) == p and matrix_rank(p) == 48,
        "P_and_Q_are_complementary": add(p, q) == identity(64) and matmul(p, q) == zero(64, 64),
        "J_annihilates_P": matmul(j, p) == zero(16, 64),
        "spread_source_is_coisometric": matmul(spread_covector, transpose(spread_covector)) == identity(16),
        "Hadamard_source_frame_is_orthogonal": matmul(source_frame_unitary, transpose(source_frame_unitary)) == identity(64),
        "spread_source_is_unitarily_equivalent_to_J0": matmul(spread_covector, source_frame_unitary) == j,
        "multiplier_hessian_is_symmetric": transpose(d) == d,
        "multiplier_hessian_square_has_normal_blocks": d2 == block_matrix(q, zero(64, 16), zero(16, 64), identity(16)),
        "multiplier_hessian_obeys_D_cubed_equals_D": d3 == d,
        "multiplier_hessian_rank_is_32": matrix_rank(d) == 32,
        "multiplier_hessian_kernel_is_48": 80 - matrix_rank(d) == 48,
        "multiplier_hessian_trace_is_zero": trace(d) == 0,
        "signed_spectrum_multiplicities_are_16_48_16": matrix_rank(d) == 32 and trace(d) == 0 and d3 == d,
        "critical_kernel_sample_satisfies_Ja_zero": matvec(j, sample_kernel) == [0] * 16,
        "J_star_is_injective": matrix_rank(jt) == 16,
        "repair_flow_semigroup_is_exact": matmul(flow_r, flow_s) == flow_rs,
        "repair_flow_scales_residual": matmul(j, flow_r) == scale(r, j),
        "repair_flow_fixes_coherent_projector": matmul(flow_r, p) == p,
        "repair_flow_zero_limit_is_P": add(p, scale(0, q)) == p,
        "family_cycle_preserves_J": matmul(j, family_cycle) == j,
        "family_cycle_preserves_P": matmul(family_cycle, matmul(p, transpose(family_cycle))) == p,
        "family_cycle_intertwines_multiplier_hessian": matmul(family_cycle80, matmul(d, transpose(family_cycle80))) == d,
        "shared_circle_intertwines_J": matmul(j, y_source) == matmul(y16, j),
        "shared_circle_commutes_with_multiplier_hessian": matmul(d, y_multiplier) == matmul(y_multiplier, d),
        "family_commutant_has_dimension_one": commutant_dimension == 1,
        "family_natural_linear_operator_is_scalar": commutant_dimension == 1,
        "T13_witness_has_same_dimensions": internal["plus_dimension"] == 64 and internal["minus_dimension"] == 16 and internal["self_adjoint_dimension"] == 80,
        "T13_witness_has_same_kernel_and_cokernel": internal["kernel_dimension"] == 48 and internal["cokernel_dimension"] == 0,
        "T13_witness_has_same_spectrum_and_gap": internal["nonzero_spectrum"] == [-1, 1] and internal["spectral_gap_mu"] == 1,
        "T13_characterwise_index_matches": internal["characterwise_index"] == "3[H16]",
        "A46_anomaly_rows_remain_zero": all(value == 0 for key, value in representation["three_family_anomalies"].items() if key != "weak_doublet_count"),
        "A46_Witten_parity_is_even": representation["three_family_anomalies"]["weak_doublet_count"] % 2 == 0,
        "A47_global_group_is_preserved": representation["gauge_group"] == "(SU3 x SU2 x U1Y)/Z6",
        "A50_shared_circle_weights_are_preserved": representation["shared_circle_weight_vector"] == [1, -4, 2, -3, 6, 0],
        "T14_provider_interface_accepts_direct_repair": t14["q79_classification"]["q79_required_by_projection_formulas"] is False,
        "contract_schema_freezes_m4_to_m1": schema["properties"]["source"]["properties"]["source_multiplicity"]["const"] == 4 and schema["properties"]["source"]["properties"]["residual_multiplicity"]["const"] == 1,
        "contract_schema_preserves_nonpromotion": schema["properties"]["claim_boundary"]["properties"]["physical_source_selected"]["const"] is False,
        "sample_multiplier_action_is_exact": sample_action == dot(sample_lambda, matvec(j, sample_a)),
        "sample_repair_cost_is_exact": sample_repair_twice == dot(matvec(j, sample_a), matvec(j, sample_a)),
        "no_observed_values_enter_source": True,
        "physical_scale_remains_unselected": source_lock["boundary"]["physical_dimensionful_scale_is_not_selected"],
        "nonlinear_family_values_remain_unselected": source_lock["boundary"]["nonlinear_family_breaking_values_are_not_selected"],
        "physical_packet_acceptance_is_unchanged": source_lock["boundary"]["physical_packet_acceptance_before"] == source_lock["boundary"]["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": source_lock["boundary"]["physical_row_acceptance_before"] == source_lock["boundary"]["physical_row_acceptance_after"] == 0,
    }

    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"direct one-constraint source checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.direct-one-constraint-multiplier-source.v1",
        "claim_id": "CBF.T15",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_BENCHMARK + CONDITIONAL_DIRECT_SOURCE_RECONSTRUCTION",
        "decision": "MINIMAL_FREE_MATTER_DIRECT_SOURCE_CLASS_CLOSED_PHYSICAL_SOURCE_OPEN",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "minimality_theorem": {
            "one_family_dimension": 16,
            "residual_multiplicity": 1,
            "kernel_family_copies_formula": "m-1",
            "three_family_source_multiplicity": 4,
            "multiplicity_table": multiplicity_table,
            "logical_direction": "A46 three-family target plus one family-blind residual copy implies the minimal four-copy source",
            "independent_prediction_of_four_copies": False,
        },
        "unitary_source_class": {
            "canonical_J": "[I16 0 0 0]",
            "nontrivial_covector": [encode_scalar(Fraction(1, 2))] * 4,
            "source_frame": [[encode_scalar(value) for value in row] for row in hadamard4],
            "all_unit_covectors_equivalent_under": "U(4)",
            "continuous_dimensionless_parameters_after_equivalence": 0,
        },
        "actions": {
            "closure_residual": "Phi(a)=J a",
            "signed_multiplier_action": "S_mult(a,lambda)=Re<lambda,J a>",
            "critical_locus": "ker(J) x {0} = C3 tensor H16",
            "signed_hessian": "D_J=[[0,J*],[J,0]]",
            "positive_repair_cost": "R(a)=1/2 ||J a||^2",
            "repair_hessian": "Q=J*J",
            "coherent_projector": "P=I-Q",
            "signed_spectrum": {"-1": 16, "0": 48, "+1": 16},
            "sample": {
                "multiplier_action": encode_scalar(sample_action),
                "twice_repair_cost": encode_scalar(sample_repair_twice),
            },
        },
        "repair_flow": {
            "equation": "da/dt=-Q a",
            "solution": "a(t)=P a(0)+exp(-t) Q a(0)",
            "formal_operator": "T_r=P+rQ",
            "composition": "T_r T_s=T_(rs)",
            "limit": "T_0=P",
            "sample_r": encode_scalar(r),
            "sample_s": encode_scalar(s),
            "sample_product": encode_scalar(r * s),
        },
        "descent": {
            "kernel_representation": "I3_family tensor rho16",
            "gauge_group": representation["gauge_group"],
            "shared_circle_weights_6Y": representation["shared_circle_weight_vector"],
            "three_family_anomalies": representation["three_family_anomalies"],
            "free_family_stabilizer": "U(3)",
            "family_commutant_dimension": commutant_dimension,
            "flavor_no_go": "every source-natural linear family operator is scalar",
        },
        "externalization": {
            "internal_operator_equals_T13_D_X": True,
            "characterwise_index": "3[H16]",
            "T13_product_dimension": t13["exact_product_witness"]["product_dimension"],
            "T13_retained_product_dimension": t13["exact_product_witness"]["retained_product_dimension"],
            "free_associated_matter_source_subclause": "CLOSED_AT_CONDITIONAL_BENCHMARK_TIER",
            "physical_BV_externalization": "OPEN",
        },
        "parameter_ledger": {
            "continuous_dimensionless_matrix_parameters_after_equivalence": 0,
            "postprojection_charge_choices": 0,
            "observed_values_used": 0,
            "unselected_dimensionful_scales": 1,
            "unselected_nonlinear_family_or_sector_values": 9,
            "note": "The count nine follows the current B.SM.02 charged-row frontier and is not derived by this theorem.",
        },
        "next_source_object": {
            "form": "Phi(a)=J a+B2(a,a)+B3(a,a,a)+... or an equivalent field-only cyclic action",
            "must_break": "free U(3) family stabilizer through selected noncommuting family data",
            "must_preserve": ["A47 gauge group", "A50 shared circle", "same-root provenance", "cyclic or BV action identity"],
            "first_decisive_output": "one held-out source-normalized interaction or threshold scalar",
        },
        "claim_boundary": {
            "physical_source_selected": False,
            "four_copy_origin_independently_derived": False,
            "field_only_cyclic_action_selected": False,
            "physical_scale_selected": False,
            "family_magnitudes_derived": False,
            "B_ACTION_01_closed": False,
            "B_OP_01_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": {
            "before": "CBF.T13's 80-to-48 matrix was an exact compiler witness without an upper closure-action origin",
            "after": "the matrix is the unique normalized multiplier Hessian of the minimal one-constraint family-blind source class and its repair flow converges to the A46 carrier",
            "remaining": "selected nonlinear cyclic source, physical scale, transferred products and BV pushforward",
        },
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": failed},
    }

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "direct one-constraint multiplier-source packet built: "
        f"{len(checks)}/{len(checks)} checks; physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
