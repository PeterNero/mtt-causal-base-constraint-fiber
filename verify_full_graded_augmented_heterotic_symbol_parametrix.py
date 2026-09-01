#!/usr/bin/env python3
"""Independently verify the exact CBF.T58 packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

import verify_augmented_heterotic_triangular_principal_symbol as base


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "full_graded_augmented_heterotic_symbol_parametrix.packet.json"
SOURCE_LOCK = ROOT / "full_graded_augmented_heterotic_symbol_parametrix_source_lock.json"
SCHEMA = ROOT / "full_graded_augmented_heterotic_symbol_parametrix_contract.schema.json"
T57_PACKET = ROOT / "augmented_heterotic_triangular_principal_symbol.packet.json"
R = 4
A = Fraction(1, 2)
C = Fraction(1, 4)

Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = list[list[Gaussian]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def dimension(rank: int, degree: int) -> int:
    return rank * choose(3, degree) + choose(3, degree + 1)


def shifted_rank(degree: int) -> int:
    return choose(3, degree) + choose(3, degree + 1)


def minus_one_symbol(beta: list[Gaussian], alpha: list[Gaussian], rank: int) -> GaussianMatrix:
    result = base.gzeros(rank + 3, 1)
    for lane, coefficient in enumerate(alpha):
        result[lane][0] = base.gmul((-A, Fraction(0)), coefficient)
    for index, coefficient in enumerate(beta):
        result[rank + index][0] = coefficient
    return result


def graded_symbol(beta: list[Gaussian], alpha: list[Gaussian], degree: int) -> GaussianMatrix:
    if degree == -1:
        return minus_one_symbol(beta, alpha, R)
    return base.symbol(beta, alpha, degree)


def hodge_symbol(beta: list[Gaussian], alpha: list[Gaussian], degree: int) -> GaussianMatrix:
    size = dimension(R, degree)
    result = base.gscale_matrix(base.gidentity(size), Fraction(0))
    if degree > -1:
        incoming = graded_symbol(beta, alpha, degree - 1)
        result = base.gadd_matrix(result, base.gmatmul(incoming, base.gadjoint(incoming)))
    if degree < 3:
        outgoing = graded_symbol(beta, alpha, degree)
        result = base.gadd_matrix(result, base.gmatmul(base.gadjoint(outgoing), outgoing))
    return result


def gdeterminant(matrix: GaussianMatrix) -> Gaussian:
    work = [row[:] for row in matrix]
    result = base.ONE
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column] != base.ZERO), None)
        if pivot is None:
            return base.ZERO
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = base.gneg(result)
        pivot_value = work[column][column]
        result = base.gmul(result, pivot_value)
        inverse_pivot = base.ginv(pivot_value)
        for row in range(column + 1, len(work)):
            if work[row][column] == base.ZERO:
                continue
            factor = base.gmul(work[row][column], inverse_pivot)
            work[row] = [
                base.gadd(entry, base.gneg(base.gmul(factor, pivot_entry)))
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return result


def gaussian_string(value: Gaussian) -> str:
    if value[1] == 0:
        return str(value[0])
    return f"{value[0]}+{value[1]}i"


def expected_degree_row(rank: int, degree: int) -> dict[str, Any]:
    size = dimension(rank, degree)
    shifted = shifted_rank(degree)
    return {
        "degree": degree,
        "carrier_dimension": size,
        "correction_rank": shifted,
        "baseline_multiplicity": size - shifted,
        "elevated_multiplicity": shifted,
        "normalized_trace_factor_rho_one": str(Fraction(1) + C * Fraction(shifted, size)),
        "condition_number_rho_one": str(Fraction(5, 4)),
        "leading_heat_weight_rho_one": str(Fraction(size - shifted) + Fraction(shifted) / Fraction(5, 4) ** 3),
    }


def main() -> None:
    packet = base.load_json(PACKET)
    lock = base.load_json(SOURCE_LOCK)
    schema = base.load_json(SCHEMA)
    t57 = base.load_json(T57_PACKET)
    witness = packet["exact_non_diagonal_witness"]
    records = witness["records"]
    t57_witness = t57["exact_six_dimensional_witness"]

    source_matches = [sha256(ROOT / source["path"]) == source["sha256"] for source in lock["sources"]]
    coframe = base.fractions(t57_witness["coframe"])
    H = base.fractions(t57_witness["contravariant_metric_H"])
    inverse_transpose = base.transpose(base.inverse(coframe))
    t57_hashes = {sample["label"]: sample["Hodge_symbol_sha256"] for sample in t57_witness["samples"]}
    replay_checks: list[bool] = []
    truncated_failures: dict[str, bool] = {}

    for record in records:
        vector = [Fraction(entry) for entry in record["covector"]]
        eta = base.matvec(inverse_transpose, vector)
        beta = [(eta[2 * index], eta[2 * index + 1]) for index in range(3)]
        alpha = [base.gconj(entry) for entry in beta]
        q_value = base.quadratic(H, vector)
        degree = int(record["degree"])
        size = dimension(R, degree)
        shifted = shifted_rank(degree)
        delta = hodge_symbol(beta, alpha, degree)
        baseline = base.gscale_matrix(base.gidentity(size), q_value)
        correction = base.gsub_matrix(delta, baseline)
        projector = base.gscale_matrix(correction, Fraction(1) / (C * q_value))
        inverse_symbol = base.gscale_matrix(
            base.gsub_matrix(base.gidentity(size), base.gscale_matrix(projector, Fraction(1, 5))),
            Fraction(1) / q_value,
        )
        determinant = gdeterminant(delta)
        expected_determinant = q_value**size * Fraction(5, 4) ** shifted
        trace_value = base.gsum(delta[index][index] for index in range(size))[0]
        two_level_residual = base.gsub_matrix(
            base.gsub_matrix(delta, baseline),
            base.gscale_matrix(projector, q_value * C),
        )
        replay_checks.extend(
            [
                base.gmatmul(projector, projector) == projector,
                base.gadjoint(projector) == projector,
                base.grank(projector) == shifted,
                base.gmatmul(delta, inverse_symbol) == base.gidentity(size),
                base.gmatmul(inverse_symbol, delta) == base.gidentity(size),
                determinant == (expected_determinant, Fraction(0)),
                all(entry == base.ZERO for row in two_level_residual for entry in row),
                base.canonical_hash(base.gstrings(delta)) == record["Hodge_symbol_sha256"],
                base.canonical_hash(base.gstrings(projector)) == record["projector_sha256"],
                base.canonical_hash(base.gstrings(inverse_symbol)) == record["inverse_symbol_sha256"],
                gaussian_string(determinant) == record["determinant"],
                str(expected_determinant) == record["expected_determinant"],
                trace_value == q_value * (size + C * shifted),
                str(trace_value) == record["trace"],
                record["carrier_dimension"] == size,
                record["projector_rank"] == shifted,
                record["baseline_multiplicity"] == size - shifted,
                record["elevated_multiplicity"] == shifted,
                degree != 1 or base.canonical_hash(base.gstrings(delta)) == t57_hashes[record["label"]],
            ]
        )
        if record["label"] not in truncated_failures:
            l0 = graded_symbol(beta, alpha, 0)
            truncated = base.gmatmul(base.gadjoint(l0), l0)
            truncated_candidate = base.gscale_matrix(
                base.gsub_matrix(truncated, base.gscale_matrix(base.gidentity(dimension(R, 0)), q_value)),
                Fraction(1) / (C * q_value),
            )
            truncated_failures[record["label"]] = not (
                base.gmatmul(truncated_candidate, truncated_candidate) == truncated_candidate
                and base.gadjoint(truncated_candidate) == truncated_candidate
            )

    witness_rows = [expected_degree_row(R, degree) for degree in range(-1, 4)]
    q79_rows = [expected_degree_row(102, degree) for degree in range(-1, 4)]
    witness_supertrace = sum(
        (Fraction(row["leading_heat_weight_rho_one"]) * (-1 if row["degree"] % 2 else 1) for row in witness_rows),
        Fraction(0),
    )
    q79_supertrace = sum(
        (Fraction(row["leading_heat_weight_rho_one"]) * (-1 if row["degree"] % 2 else 1) for row in q79_rows),
        Fraction(0),
    )
    expected_payload = base.canonical_hash(
        {
            "full_graded_theorem": packet["full_graded_theorem"],
            "records": records,
            "q79": packet["q79_rank102_specialization"],
            "heat": packet["heat_supertrace_certificate"],
        }
    )

    theorem = packet["full_graded_theorem"]
    q79 = packet["q79_rank102_specialization"]
    heat = packet["heat_supertrace_certificate"]
    contract = packet["operator_execution_contract_update"]
    ledger = packet["parameter_ledger"]
    boundary = packet["physical_boundary"]
    checks = {
        "packet_schema": packet["schema"] == "boe.mtt.full-graded-augmented-heterotic-symbol-parametrix.v1",
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": set(schema["required"]).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T58",
        "source_hashes_match": all(source_matches),
        "source_count": len(source_matches) == 4,
        "builder_checks_pass": packet["check_summary"]["all_passed"],
        "builder_check_count": packet["check_summary"]["total"] == 45,
        "degree_list": theorem["degrees"] == [-1, 0, 1, 2, 3],
        "rank_sequence": theorem["correction_ranks"] == [1, 4, 6, 4, 1],
        "scalar_completion_required": theorem["degree_minus_one_scalar_completion_is_required"],
        "record_count": len(records) == 105,
        "all_independent_replays": all(replay_checks),
        "independent_replay_count": len(replay_checks) == 105 * 19,
        "all_truncated_controls_fail": len(truncated_failures) == 21 and all(truncated_failures.values()),
        "witness_rows": witness["degree_rows"] == witness_rows,
        "q79_rows": q79["degree_rows"] == q79_rows,
        "witness_dimensions": [row["carrier_dimension"] for row in witness_rows] == [1, 7, 15, 13, 4],
        "witness_ranks": [row["correction_rank"] for row in witness_rows] == [1, 4, 6, 4, 1],
        "q79_dimensions": [row["carrier_dimension"] for row in q79_rows] == [1, 105, 309, 307, 102],
        "q79_baselines": [row["baseline_multiplicity"] for row in q79_rows] == [0, 101, 303, 303, 101],
        "q79_trace_formulas": q79["normalized_trace_factor_formulas"] == ["1+rho/4", "1+rho/105", "1+rho/206", "1+rho/307", "1+rho/408"],
        "witness_supertrace": witness_supertrace == 0,
        "q79_supertrace": q79_supertrace == 0,
        "rank_supertrace": heat["correction_rank_alternating_sum"] == 0,
        "baseline_supertrace": heat["baseline_multiplicity_alternating_sum"] == 0,
        "heat_identity": heat["general_identity"] == "sum_n(-1)^n h_n(c)=0",
        "no_index_claim": not heat["index_claimed"],
        "preconditioner_complete": contract["principal_symbol_preconditioner_complete_all_degrees"],
        "principal_inverse_rows_zero": contract["independent_principal_symbol_inverse_rows_remaining"] == 0,
        "global_inverse_open": contract["selected_global_reduced_inverse"] == "OPEN",
        "tail_bounds_open": contract["selected_inverse_tail_bounds"] == "OPEN",
        "B_OP_open": not contract["B_OP_01_closed"],
        "no_parameters": ledger["continuous_physical_parameters_added"] == 0,
        "no_selectors": ledger["discrete_selectors_added"] == 0,
        "no_observed_values": ledger["observed_values_used"] == 0,
        "no_fits": ledger["fitted_values_used"] == 0,
        "B_GEO_open": not boundary["B_GEO_01_closed"],
        "physical_counters": boundary["physical_gates"] == {"accepted": 0, "total": 3} and boundary["physical_packets"] == {"accepted": 0, "total": 3} and boundary["physical_rows"] == {"accepted": 0, "total": 7},
        "no_endpoint_claim": not boundary["selected_physical_endpoint_claimed"],
        "no_Green_claim": not boundary["selected_global_Green_claimed"],
        "payload_hash": packet["exact_payload_sha256"] == expected_payload,
    }
    summary = {
        "passed": sum(bool(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    if not summary["all_passed"]:
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"CBF.T58 independent verification failed: {failed}")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
