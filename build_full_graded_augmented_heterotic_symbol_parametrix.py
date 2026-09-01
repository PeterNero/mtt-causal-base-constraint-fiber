#!/usr/bin/env python3
"""Build the exact CBF.T58 full graded augmented-symbol packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

from build_augmented_heterotic_triangular_principal_symbol import (
    GONE,
    GZERO,
    canonical_hash,
    fractions,
    gadjoint,
    gadd,
    gidentity,
    ginv,
    gmul,
    gmatmul,
    gmatrix_add,
    gmatrix_scale,
    gmatrix_strings,
    gmatrix_sub,
    grank,
    gsum,
    gzeros,
    load_json,
    quadratic,
    real_matvec,
    sample_vectors,
    transpose,
    inverse,
    triangular_symbol,
    gconj,
)


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "full_graded_augmented_heterotic_symbol_parametrix_source_lock.json"
SCHEMA = ROOT / "full_graded_augmented_heterotic_symbol_parametrix_contract.schema.json"
THEOREM = ROOT / "FullGradedAugmentedHeteroticSymbolParametrixAndHeatTraceTheorem_v1.md"
T57_PACKET = ROOT / "augmented_heterotic_triangular_principal_symbol.packet.json"
OUTPUT = ROOT / "full_graded_augmented_heterotic_symbol_parametrix.packet.json"

COMPLEX_DIMENSION = 3
WITNESS_RANK = 4
Q79_RANK = 102
A = Fraction(1, 2)
RHO = Fraction(1)
C = A * A * RHO

Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = list[list[Gaussian]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def carrier_dimension(rank: int, degree: int) -> int:
    return rank * choose(3, degree) + choose(3, degree + 1)


def correction_rank(degree: int) -> int:
    return choose(3, degree) + choose(3, degree + 1)


def minus_one_symbol(beta: list[Gaussian], alpha: list[Gaussian], rank: int) -> GaussianMatrix:
    result = gzeros(rank + 3, 1)
    for lane, coefficient in enumerate(alpha):
        result[lane][0] = gmul((-A, Fraction(0)), coefficient)
    for index, coefficient in enumerate(beta):
        result[rank + index][0] = coefficient
    return result


def graded_symbol(beta: list[Gaussian], alpha: list[Gaussian], degree: int, rank: int) -> GaussianMatrix:
    if degree == -1:
        return minus_one_symbol(beta, alpha, rank)
    return triangular_symbol(beta, alpha, degree, rank)


def degree_hodge_symbol(beta: list[Gaussian], alpha: list[Gaussian], degree: int, rank: int) -> GaussianMatrix:
    dimension = carrier_dimension(rank, degree)
    result = gmatrix_scale(gidentity(dimension), Fraction(0))
    if degree > -1:
        incoming = graded_symbol(beta, alpha, degree - 1, rank)
        result = gmatrix_add(result, gmatmul(incoming, gadjoint(incoming)))
    if degree < 3:
        outgoing = graded_symbol(beta, alpha, degree, rank)
        result = gmatrix_add(result, gmatmul(gadjoint(outgoing), outgoing))
    return result


def gdeterminant(matrix: GaussianMatrix) -> Gaussian:
    work = [row[:] for row in matrix]
    result = GONE
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column] != GZERO), None)
        if pivot is None:
            return GZERO
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = (-result[0], -result[1])
        pivot_value = work[column][column]
        result = (
            result[0] * pivot_value[0] - result[1] * pivot_value[1],
            result[0] * pivot_value[1] + result[1] * pivot_value[0],
        )
        inverse_pivot = ginv(pivot_value)
        for row in range(column + 1, len(work)):
            if work[row][column] == GZERO:
                continue
            factor = (
                work[row][column][0] * inverse_pivot[0] - work[row][column][1] * inverse_pivot[1],
                work[row][column][0] * inverse_pivot[1] + work[row][column][1] * inverse_pivot[0],
            )
            work[row] = [
                gadd(entry, (-product[0], -product[1]))
                for entry, product in zip(
                    work[row],
                    [
                        (
                            factor[0] * pivot_entry[0] - factor[1] * pivot_entry[1],
                            factor[0] * pivot_entry[1] + factor[1] * pivot_entry[0],
                        )
                        for pivot_entry in work[column]
                    ],
                )
            ]
    return result


def gaussian_string(value: Gaussian) -> str:
    if value[1] == 0:
        return str(value[0])
    return f"{value[0]}+{value[1]}i"


def degree_summary(rank: int, degree: int) -> dict[str, Any]:
    dimension = carrier_dimension(rank, degree)
    shifted = correction_rank(degree)
    trace_factor = Fraction(1) + C * Fraction(shifted, dimension)
    heat_weight = Fraction(dimension - shifted) + Fraction(shifted) / (Fraction(1) + C) ** 3
    return {
        "degree": degree,
        "carrier_dimension": dimension,
        "correction_rank": shifted,
        "baseline_multiplicity": dimension - shifted,
        "elevated_multiplicity": shifted,
        "normalized_trace_factor_rho_one": str(trace_factor),
        "condition_number_rho_one": str(Fraction(1) + C),
        "leading_heat_weight_rho_one": str(heat_weight),
    }


def main() -> None:
    lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t57 = load_json(T57_PACKET)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    source_checks = []
    for source in lock["sources"]:
        actual = sha256(ROOT / source["path"])
        source_checks.append(
            {
                "id": source["id"],
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": actual,
                "matches": actual == source["sha256"],
            }
        )

    t57_witness = t57["exact_six_dimensional_witness"]
    coframe = fractions(t57_witness["coframe"])
    metric_inverse = fractions(t57_witness["contravariant_metric_H"])
    inverse_transpose = transpose(inverse(coframe))
    t57_degree_one_hashes = {
        sample["label"]: sample["Hodge_symbol_sha256"] for sample in t57_witness["samples"]
    }

    records = []
    all_projectors = True
    all_ranks = True
    all_inverses = True
    all_determinants = True
    all_two_level = True
    degree_one_hashes_match = True
    all_truncated_degree_zero_controls_fail = True
    for label, row, column, vector in sample_vectors():
        eta = real_matvec(inverse_transpose, vector)
        beta = [(eta[2 * index], eta[2 * index + 1]) for index in range(COMPLEX_DIMENSION)]
        alpha = [gconj(entry) for entry in beta]
        q_value = quadratic(metric_inverse, vector)
        l0_without_scalar_completion = graded_symbol(beta, alpha, 0, WITNESS_RANK)
        truncated_degree_zero = gmatmul(gadjoint(l0_without_scalar_completion), l0_without_scalar_completion)
        truncated_dimension = carrier_dimension(WITNESS_RANK, 0)
        truncated_candidate = gmatrix_scale(
            gmatrix_sub(truncated_degree_zero, gmatrix_scale(gidentity(truncated_dimension), q_value)),
            Fraction(1) / (C * q_value),
        )
        truncated_candidate_is_projector = (
            gmatmul(truncated_candidate, truncated_candidate) == truncated_candidate
            and gadjoint(truncated_candidate) == truncated_candidate
        )
        all_truncated_degree_zero_controls_fail = (
            all_truncated_degree_zero_controls_fail and not truncated_candidate_is_projector
        )
        for degree in range(-1, 4):
            dimension = carrier_dimension(WITNESS_RANK, degree)
            shifted = correction_rank(degree)
            delta = degree_hodge_symbol(beta, alpha, degree, WITNESS_RANK)
            baseline = gmatrix_scale(gidentity(dimension), q_value)
            correction = gmatrix_sub(delta, baseline)
            projector = gmatrix_scale(correction, Fraction(1) / (C * q_value))
            projector_exact = gmatmul(projector, projector) == projector and gadjoint(projector) == projector
            projector_rank = grank(projector)
            inverse_symbol = gmatrix_scale(
                gmatrix_sub(gidentity(dimension), gmatrix_scale(projector, C / (Fraction(1) + C))),
                Fraction(1) / q_value,
            )
            inverse_exact = (
                gmatmul(delta, inverse_symbol) == gidentity(dimension)
                and gmatmul(inverse_symbol, delta) == gidentity(dimension)
            )
            expected_determinant = q_value**dimension * (Fraction(1) + C) ** shifted
            actual_determinant = gdeterminant(delta)
            determinant_exact = actual_determinant == (expected_determinant, Fraction(0))
            high = q_value * (Fraction(1) + C)
            two_level_residual = gmatrix_sub(
                gmatrix_sub(delta, baseline),
                gmatrix_scale(projector, high - q_value),
            )
            two_level_exact = all(entry == GZERO for source_row in two_level_residual for entry in source_row)
            trace_value = gsum(delta[index][index] for index in range(dimension))[0]
            expected_trace = q_value * (dimension + C * shifted)
            hodge_hash = canonical_hash(gmatrix_strings(delta))
            if degree == 1:
                degree_one_hashes_match = degree_one_hashes_match and hodge_hash == t57_degree_one_hashes[label]
            all_projectors = all_projectors and projector_exact
            all_ranks = all_ranks and projector_rank == shifted
            all_inverses = all_inverses and inverse_exact
            all_determinants = all_determinants and determinant_exact
            all_two_level = all_two_level and two_level_exact
            records.append(
                {
                    "label": label,
                    "row": row,
                    "column": column,
                    "degree": degree,
                    "covector": [str(entry) for entry in vector],
                    "q": str(q_value),
                    "carrier_dimension": dimension,
                    "projector_rank": projector_rank,
                    "baseline_multiplicity": dimension - shifted,
                    "elevated_multiplicity": shifted,
                    "Hodge_symbol_sha256": hodge_hash,
                    "projector_sha256": canonical_hash(gmatrix_strings(projector)),
                    "inverse_symbol_sha256": canonical_hash(gmatrix_strings(inverse_symbol)),
                    "projector_exact": projector_exact,
                    "inverse_exact": inverse_exact,
                    "two_level_exact": two_level_exact,
                    "determinant": gaussian_string(actual_determinant),
                    "expected_determinant": str(expected_determinant),
                    "determinant_exact": determinant_exact,
                    "trace": str(trace_value),
                    "expected_trace": str(expected_trace),
                    "trace_exact": trace_value == expected_trace,
                }
            )

    witness_rows = [degree_summary(WITNESS_RANK, degree) for degree in range(-1, 4)]
    q79_rows = [degree_summary(Q79_RANK, degree) for degree in range(-1, 4)]
    witness_supertrace = sum(
        (Fraction(row["leading_heat_weight_rho_one"]) * (-1 if row["degree"] % 2 else 1) for row in witness_rows),
        Fraction(0),
    )
    q79_supertrace = sum(
        (Fraction(row["leading_heat_weight_rho_one"]) * (-1 if row["degree"] % 2 else 1) for row in q79_rows),
        Fraction(0),
    )
    rank_supertrace = sum((correction_rank(degree) * (-1 if degree % 2 else 1) for degree in range(-1, 4)))
    baseline_supertrace = sum(
        ((carrier_dimension(Q79_RANK, degree) - correction_rank(degree)) * (-1 if degree % 2 else 1) for degree in range(-1, 4))
    )

    packet: dict[str, Any] = {
        "schema": "boe.mtt.full-graded-augmented-heterotic-symbol-parametrix.v1",
        "claim_id": "CBF.T58",
        "date": "2026-09-01",
        "status": "EXACT_FULL_GRADED_PROJECTOR_SYMBOL_PARAMETRIX_DETERMINANT_AND_LEADING_HEAT_TRACE_CONDITIONAL_Q79_SOURCE_REDUCTION",
        "source_provenance": {
            "model_state_sha256": lock["model_state_sha256"],
            "handoff_id": lock["handoff_id"],
            "source_checks": source_checks,
            "all_sources_hash_locked": all(source["matches"] for source in source_checks),
        },
        "full_graded_theorem": {
            "degrees": [-1, 0, 1, 2, 3],
            "carrier_dimension_formula": "d_n=r*C(3,n)+C(3,n+1)",
            "correction_rank_formula": "s_n=C(3,n)+C(3,n+1)=C(4,n+1)",
            "correction_ranks": [1, 4, 6, 4, 1],
            "symbol_formula": "sigma_2(Delta_Y,n)(xi)=q(xi)[I+cP_n], c=a^2 rho",
            "inverse_formula": "q^(-1)[I-c/(1+c)P_n]",
            "condition_number": "1+c",
            "determinant_formula": "q^(d_n)(1+c)^(s_n)",
            "leading_heat_weight": "h_n(c)=(d_n-s_n)+s_n(1+c)^(-3)",
            "strong_ellipticity_for_positive_q_and_rho": True,
            "principal_inverse_is_not_global_reduced_Green": True,
            "degree_minus_one_scalar_completion_is_required": True,
        },
        "exact_non_diagonal_witness": {
            "Q_rank": WITNESS_RANK,
            "a_fixture": str(A),
            "rho_fixture": str(RHO),
            "c_fixture": str(C),
            "fixtures_are_physical": False,
            "degree_rows": witness_rows,
            "record_count": len(records),
            "records": records,
            "all_projectors_exact": all_projectors,
            "all_projector_ranks_exact": all_ranks,
            "all_symbol_inverses_exact": all_inverses,
            "all_determinants_exact": all_determinants,
            "all_two_level_identities_exact": all_two_level,
            "degree_one_hashes_match_T57": degree_one_hashes_match,
            "all_truncated_degree_zero_simple_projector_controls_fail": all_truncated_degree_zero_controls_fail,
        },
        "q79_rank102_specialization": {
            "Q_rank": Q79_RANK,
            "a": str(A),
            "degree_rows": q79_rows,
            "normalized_trace_factor_formulas": [
                "1+rho/4",
                "1+rho/105",
                "1+rho/206",
                "1+rho/307",
                "1+rho/408"
            ],
            "determinant_formulas": [
                "q(1+rho/4)",
                "q^105(1+rho/4)^4",
                "q^309(1+rho/4)^6",
                "q^307(1+rho/4)^4",
                "q^102(1+rho/4)"
            ],
            "rho_one_rows_are_physical": False,
        },
        "heat_supertrace_certificate": {
            "correction_rank_alternating_sum": rank_supertrace,
            "baseline_multiplicity_alternating_sum": baseline_supertrace,
            "witness_rho_one_heat_weight_alternating_sum": str(witness_supertrace),
            "q79_rho_one_heat_weight_alternating_sum": str(q79_supertrace),
            "general_identity": "sum_n(-1)^n h_n(c)=0",
            "complete_complex_value": 0,
            "degree_minus_one_scalar_lane_included": True,
            "index_claimed": False,
        },
        "operator_execution_contract_update": {
            "principal_symbol_preconditioner_complete_all_degrees": True,
            "independent_principal_symbol_inverse_rows_remaining": 0,
            "selected_lower_order_coefficient_arrays": "OPEN",
            "selected_kernel_projection": "OPEN",
            "selected_global_reduced_inverse": "OPEN",
            "selected_inverse_tail_bounds": "OPEN",
            "selected_radii_inequality_decision": "OPEN",
            "B_OP_01_closed": False,
        },
        "parameter_ledger": {
            "continuous_physical_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "rho_one_and_a_half_are_nonphysical_fixtures": True,
        },
        "physical_boundary": {
            "B_GEO_01_closed": False,
            "B_OP_01_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "selected_physical_endpoint_claimed": False,
            "selected_global_Green_claimed": False,
        },
    }

    packet["exact_payload_sha256"] = canonical_hash(
        {
            "full_graded_theorem": packet["full_graded_theorem"],
            "records": records,
            "q79": packet["q79_rank102_specialization"],
            "heat": packet["heat_supertrace_certificate"],
        }
    )

    q79_dimensions = [row["carrier_dimension"] for row in q79_rows]
    q79_ranks = [row["correction_rank"] for row in q79_rows]
    q79_baseline = [row["baseline_multiplicity"] for row in q79_rows]
    checks = {
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": (set(schema["required"]) - {"checks", "check_summary"}).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T58",
        "theorem_states_inverse": "q^(-1)[I-c/(1+c) P_n]" in theorem_text,
        "theorem_states_rank_sequence": "1,4,6,4,1" in theorem_text.replace(" ", ""),
        "theorem_preserves_boundary": "Physical acceptance remains `0/3`" in theorem_text,
        "source_hashes_match": packet["source_provenance"]["all_sources_hash_locked"],
        "source_count": len(source_checks) == 4,
        "record_count": len(records) == 105,
        "all_projectors": all_projectors,
        "all_ranks": all_ranks,
        "all_inverses": all_inverses,
        "all_determinants": all_determinants,
        "all_two_level": all_two_level,
        "degree_one_replays_T57": degree_one_hashes_match,
        "witness_dimensions": [row["carrier_dimension"] for row in witness_rows] == [1, 7, 15, 13, 4],
        "witness_ranks": [row["correction_rank"] for row in witness_rows] == [1, 4, 6, 4, 1],
        "witness_baselines": [row["baseline_multiplicity"] for row in witness_rows] == [0, 3, 9, 9, 3],
        "witness_trace_factors": [Fraction(row["normalized_trace_factor_rho_one"]) for row in witness_rows] == [Fraction(5, 4), Fraction(8, 7), Fraction(11, 10), Fraction(14, 13), Fraction(17, 16)],
        "witness_heat_weights": [Fraction(row["leading_heat_weight_rho_one"]) for row in witness_rows] == [Fraction(64, 125), Fraction(631, 125), Fraction(1509, 125), Fraction(1381, 125), Fraction(439, 125)],
        "witness_supertrace": witness_supertrace == 0,
        "truncated_degree_zero_controls_fail": all_truncated_degree_zero_controls_fail,
        "q79_dimensions": q79_dimensions == [1, 105, 309, 307, 102],
        "q79_ranks": q79_ranks == [1, 4, 6, 4, 1],
        "q79_baselines": q79_baseline == [0, 101, 303, 303, 101],
        "q79_trace_factors": [Fraction(row["normalized_trace_factor_rho_one"]) for row in q79_rows] == [Fraction(5, 4), Fraction(106, 105), Fraction(207, 206), Fraction(308, 307), Fraction(409, 408)],
        "q79_heat_weights": [Fraction(row["leading_heat_weight_rho_one"]) for row in q79_rows] == [Fraction(64, 125), Fraction(12881, 125), Fraction(38259, 125), Fraction(38131, 125), Fraction(12689, 125)],
        "q79_supertrace": q79_supertrace == 0,
        "rank_supertrace_zero": rank_supertrace == 0,
        "baseline_supertrace_zero": baseline_supertrace == 0,
        "principal_preconditioner_complete": packet["operator_execution_contract_update"]["principal_symbol_preconditioner_complete_all_degrees"],
        "no_principal_inverse_rows_left": packet["operator_execution_contract_update"]["independent_principal_symbol_inverse_rows_remaining"] == 0,
        "global_inverse_open": packet["operator_execution_contract_update"]["selected_global_reduced_inverse"] == "OPEN",
        "tail_bounds_open": packet["operator_execution_contract_update"]["selected_inverse_tail_bounds"] == "OPEN",
        "B_OP_open": not packet["operator_execution_contract_update"]["B_OP_01_closed"],
        "no_parameters": packet["parameter_ledger"]["continuous_physical_parameters_added"] == 0,
        "no_selectors": packet["parameter_ledger"]["discrete_selectors_added"] == 0,
        "no_observed_values": packet["parameter_ledger"]["observed_values_used"] == 0,
        "no_fits": packet["parameter_ledger"]["fitted_values_used"] == 0,
        "B_GEO_open": not packet["physical_boundary"]["B_GEO_01_closed"],
        "physical_gates": packet["physical_boundary"]["physical_gates"] == {"accepted": 0, "total": 3},
        "physical_packets": packet["physical_boundary"]["physical_packets"] == {"accepted": 0, "total": 3},
        "physical_rows": packet["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
        "no_endpoint_claim": not packet["physical_boundary"]["selected_physical_endpoint_claimed"],
        "no_global_Green_claim": not packet["physical_boundary"]["selected_global_Green_claimed"],
    }
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": sum(bool(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    if not packet["check_summary"]["all_passed"]:
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"CBF.T58 build failed: {failed}")

    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet["check_summary"], sort_keys=True))


if __name__ == "__main__":
    main()
