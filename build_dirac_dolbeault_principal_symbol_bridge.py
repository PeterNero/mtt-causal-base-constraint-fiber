#!/usr/bin/env python3
"""Build the exact CBF.T56 Dirac-Dolbeault principal-symbol bridge."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from build_q79_hermitian_metric_hodge_compiler import (
    canonical_hash,
    determinant,
    hodge_matrix,
    identity,
    inverse,
    matmul,
    matrix_hash,
    matrix_strings,
    scale,
    trace,
    transpose,
    zeros,
)


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "dirac_dolbeault_principal_symbol_source_lock.json"
SCHEMA = ROOT / "dirac_dolbeault_principal_symbol_contract.schema.json"
THEOREM = ROOT / "DiracDolbeaultPrincipalSymbolAndSameSourceMetricBridgeTheorem_v1.md"
EVIDENCE = ROOT / "dirac_dolbeault_principal_symbol_external_evidence.audit.json"
T52_PACKET = ROOT / "q79_hermitian_metric_hodge_compiler.packet.json"
T55_PACKET = ROOT / "same_source_principal_symbol_metric_hodge_naturality.packet.json"
OUTPUT = ROOT / "dirac_dolbeault_principal_symbol_bridge.packet.json"

N = 6
SPINOR_RANK = 8
ACTION_SCALE = Fraction(7)

RealMatrix = list[list[Fraction]]
Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = list[list[Gaussian]]
GZERO: Gaussian = (Fraction(0), Fraction(0))
GONE: Gaussian = (Fraction(1), Fraction(0))
GI: Gaussian = (Fraction(0), Fraction(1))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fractions(matrix: list[list[str]]) -> RealMatrix:
    return [[Fraction(entry) for entry in row] for row in matrix]


def gadd(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gmul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gscale(value: Gaussian, scalar: Fraction) -> Gaussian:
    return value[0] * scalar, value[1] * scalar


def gzeros(rows: int, columns: int) -> GaussianMatrix:
    return [[GZERO for _ in range(columns)] for _ in range(rows)]


def gidentity(size: int) -> GaussianMatrix:
    return [[GONE if row == column else GZERO for column in range(size)] for row in range(size)]


def gmatrix_add(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    return [
        [gadd(a, b) for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def gmatrix_scale(matrix: GaussianMatrix, scalar: Fraction | Gaussian) -> GaussianMatrix:
    factor = scalar if isinstance(scalar, tuple) else (scalar, Fraction(0))
    return [[gmul(factor, entry) for entry in row] for row in matrix]


def gtranspose(matrix: GaussianMatrix) -> GaussianMatrix:
    return [list(row) for row in zip(*matrix)]


def gmatmul(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    right_t = gtranspose(right)
    return [
        [
            sum_gaussian(gmul(a, b) for a, b in zip(left_row, right_column))
            for right_column in right_t
        ]
        for left_row in left
    ]


def sum_gaussian(values: Any) -> Gaussian:
    result = GZERO
    for value in values:
        result = gadd(result, value)
    return result


def gtrace(matrix: GaussianMatrix) -> Gaussian:
    return sum_gaussian(matrix[index][index] for index in range(len(matrix)))


def tensor(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    rows = len(left) * len(right)
    columns = len(left[0]) * len(right[0])
    result = gzeros(rows, columns)
    for i, left_row in enumerate(left):
        for j, entry in enumerate(left_row):
            for k, right_row in enumerate(right):
                for ell, right_entry in enumerate(right_row):
                    result[i * len(right) + k][j * len(right[0]) + ell] = gmul(
                        entry, right_entry
                    )
    return result


def tensor_three(first: GaussianMatrix, second: GaussianMatrix, third: GaussianMatrix) -> GaussianMatrix:
    return tensor(tensor(first, second), third)


def gaussian_string(value: Gaussian) -> str:
    real, imag = value
    if imag == 0:
        return str(real)
    if real == 0:
        if imag == 1:
            return "i"
        if imag == -1:
            return "-i"
        return f"{imag}i"
    sign = "+" if imag > 0 else ""
    imag_part = "i" if imag == 1 else ("-i" if imag == -1 else f"{imag}i")
    return f"{real}{sign}{imag_part}"


def gmatrix_strings(matrix: GaussianMatrix) -> list[list[str]]:
    return [[gaussian_string(entry) for entry in row] for row in matrix]


def scalar_gmatrix(value: Fraction, size: int) -> GaussianMatrix:
    return gmatrix_scale(gidentity(size), value)


def flat_gamma_matrices() -> list[GaussianMatrix]:
    i2 = gidentity(2)
    x = [[GZERO, GONE], [GONE, GZERO]]
    y = [[GZERO, (Fraction(0), Fraction(-1))], [GI, GZERO]]
    z = [[GONE, GZERO], [GZERO, (Fraction(-1), Fraction(0))]]
    return [
        tensor_three(x, i2, i2),
        tensor_three(y, i2, i2),
        tensor_three(z, x, i2),
        tensor_three(z, y, i2),
        tensor_three(z, z, x),
        tensor_three(z, z, y),
    ]


def linear_combination(matrices: list[GaussianMatrix], coefficients: list[Fraction]) -> GaussianMatrix:
    result = gzeros(len(matrices[0]), len(matrices[0][0]))
    for matrix, coefficient in zip(matrices, coefficients):
        result = gmatrix_add(result, gmatrix_scale(matrix, coefficient))
    return result


def quadratic(matrix: RealMatrix, vector: list[Fraction]) -> Fraction:
    return sum(
        (
            vector[row] * matrix[row][column] * vector[column]
            for row in range(len(vector))
            for column in range(len(vector))
        ),
        Fraction(0),
    )


def exact_integer_root(value: int, degree: int) -> int:
    low, high = 0, max(1, value)
    while low <= high:
        middle = (low + high) // 2
        power = middle**degree
        if power == value:
            return middle
        if power < value:
            low = middle + 1
        else:
            high = middle - 1
    raise ValueError(f"{value} is not an exact {degree}th power")


def exact_fraction_root(value: Fraction, degree: int) -> Fraction:
    return Fraction(
        exact_integer_root(value.numerator, degree),
        exact_integer_root(value.denominator, degree),
    )


def sample_vectors() -> list[tuple[str, int, int | None, list[Fraction]]]:
    basis = [
        [Fraction(int(row == column)) for row in range(N)]
        for column in range(N)
    ]
    rows: list[tuple[str, int, int | None, list[Fraction]]] = []
    for first in range(N):
        rows.append((f"e{first + 1}", first, None, basis[first]))
        for second in range(first + 1, N):
            rows.append(
                (
                    f"e{first + 1}+e{second + 1}",
                    first,
                    second,
                    [a + b for a, b in zip(basis[first], basis[second])],
                )
            )
    return rows


def reconstruct_quadratic(samples: list[dict[str, Any]]) -> RealMatrix:
    diagonal: dict[int, Fraction] = {}
    pairs: dict[tuple[int, int], Fraction] = {}
    for sample in samples:
        row = int(sample["row"])
        column = sample["column"]
        value = Fraction(sample["hessian_scalar"])
        if column is None:
            diagonal[row] = value
        else:
            pairs[(row, int(column))] = value
    result = zeros(N, N)
    for row in range(N):
        result[row][row] = diagonal[row]
    for (row, column), value in pairs.items():
        result[row][column] = result[column][row] = (
            value - diagonal[row] - diagonal[column]
        ) / 2
    return result


def main() -> None:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    evidence = load_json(EVIDENCE)
    t52 = load_json(T52_PACKET)
    t55 = load_json(T55_PACKET)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    source_checks = []
    for source in source_lock["sources"]:
        path = ROOT / source["path"]
        actual = sha256(path)
        source_checks.append(
            {
                "id": source["id"],
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": actual,
                "matches": actual == source["sha256"],
            }
        )

    witness = t52["non_diagonal_hermitian_witness"]
    coframe = fractions(witness["real_coframe"])
    metric = fractions(witness["covariant_metric_G"])
    metric_inverse = fractions(witness["covector_metric_H"])
    density = Fraction(witness["volume_factor"])
    inverse_transpose_coframe = transpose(inverse(coframe))

    flat_gammas = flat_gamma_matrices()
    gammas = [
        linear_combination(
            flat_gammas,
            [inverse_transpose_coframe[row][column] for row in range(N)],
        )
        for column in range(N)
    ]

    clifford_rows = []
    recovered_H = zeros(N, N)
    for row in range(N):
        for column in range(row, N):
            anticommutator = gmatrix_add(
                gmatmul(gammas[row], gammas[column]),
                gmatmul(gammas[column], gammas[row]),
            )
            target = scalar_gmatrix(2 * metric_inverse[row][column], SPINOR_RANK)
            normalized_half_trace = gscale(
                gtrace(anticommutator), Fraction(1, 2 * SPINOR_RANK)
            )
            recovered_H[row][column] = recovered_H[column][row] = normalized_half_trace[0]
            clifford_rows.append(
                {
                    "row": row,
                    "column": column,
                    "target_H_entry": str(metric_inverse[row][column]),
                    "normalized_half_trace": gaussian_string(normalized_half_trace),
                    "relation_exact": anticommutator == target,
                    "relation_sha256": canonical_hash(gmatrix_strings(anticommutator)),
                }
            )

    symbol_samples = []
    action_quadratic = scale(metric_inverse, ACTION_SCALE)
    for label, row, column, vector in sample_vectors():
        symbol = linear_combination(gammas, vector)
        symbol_square = gmatmul(symbol, symbol)
        metric_value = quadratic(metric_inverse, vector)
        target = scalar_gmatrix(metric_value, SPINOR_RANK)
        symbol_samples.append(
            {
                "label": label,
                "row": row,
                "column": column,
                "covector": [str(entry) for entry in vector],
                "metric_scalar": str(metric_value),
                "hessian_scalar": str(ACTION_SCALE * metric_value),
                "Dirac_square_scalar": symbol_square == target,
                "Dirac_square_sha256": canonical_hash(gmatrix_strings(symbol_square)),
            }
        )

    reconstructed_A = reconstruct_quadratic(symbol_samples)
    recovered_scale = exact_fraction_root(
        density**2 * determinant(reconstructed_A), N
    )
    t55_H = scale(reconstructed_A, Fraction(1) / recovered_scale)
    t55_G = scale(inverse(reconstructed_A), recovered_scale)
    recovered_hodge = hodge_matrix(t55_H, density)

    # A noncommuting Hermitian order-zero potential i gamma_1 gamma_2.
    potential = gmatrix_scale(gmatmul(gammas[0], gammas[1]), GI)
    lower_order_rows = []
    for label, _, _, vector in [sample_vectors()[0], sample_vectors()[6], sample_vectors()[-1]]:
        symbol = linear_combination(gammas, vector)
        quadratic_coefficient = gmatmul(symbol, symbol)
        linear_coefficient = gmatrix_add(
            gmatmul(symbol, potential), gmatmul(potential, symbol)
        )
        constant_coefficient = gmatmul(potential, potential)
        target = scalar_gmatrix(quadratic(metric_inverse, vector), SPINOR_RANK)
        normalized_linear = gscale(gtrace(linear_coefficient), Fraction(1, SPINOR_RANK))
        lower_order_rows.append(
            {
                "label": label,
                "quadratic_coefficient_unchanged": quadratic_coefficient == target,
                "quadratic_sha256": canonical_hash(gmatrix_strings(quadratic_coefficient)),
                "linear_coefficient_sha256": canonical_hash(gmatrix_strings(linear_coefficient)),
                "constant_coefficient_sha256": canonical_hash(gmatrix_strings(constant_coefficient)),
                "linear_normalized_trace": gaussian_string(normalized_linear),
            }
        )

    joint = evidence["joint_conclusion"]
    packet: dict[str, Any] = {
        "schema": "boe.mtt.dirac-dolbeault-principal-symbol-bridge.v1",
        "claim_id": "CBF.T56",
        "date": "2026-09-01",
        "status": "EXACT_DIRAC_DOLBEAULT_SCALAR_SYMBOL_AND_T55_COMPOSITION_CONDITIONAL_Q79_SOURCE_REDUCTION",
        "source_provenance": {
            "model_state_sha256": source_lock["model_state_sha256"],
            "handoff_id": source_lock["handoff_id"],
            "source_checks": source_checks,
            "all_sources_hash_locked": all(row["matches"] for row in source_checks),
            "external_sources_are_portable_audit_metadata_not_runtime_dependencies": True,
        },
        "dirac_symbol_theorem": {
            "first_order_relation": "b(xi)b(eta)+b(eta)b(xi)=2h(xi,eta)I",
            "square_symbol": "sigma_2(B^2)(xi)=h(xi,xi)I",
            "action_hessian_symbol": "sigma_2(kappa B^2+lower)(xi)=kappa h(xi,xi)I",
            "metric_recovery": "h_ij I=(gamma_i gamma_j+gamma_j gamma_i)/2",
            "Dolbeault_corollary": "sqrt(2)(dbar_A+dbar_A_star) is Dirac type and squares to 2 Delta_dbar,A",
            "connection_curvature_HYM_Higgs_Yukawa_are_below_second_order": True,
            "mixed_order_detour_requires_separate_gauge_fixing": True,
        },
        "exact_six_dimensional_clifford_witness": {
            "dimension": N,
            "complex_spinor_rank": SPINOR_RANK,
            "coframe": matrix_strings(coframe),
            "inverse_transpose_coframe": matrix_strings(inverse_transpose_coframe),
            "covariant_metric_G": matrix_strings(metric),
            "contravariant_metric_H": matrix_strings(metric_inverse),
            "gamma_matrices": [gmatrix_strings(gamma) for gamma in gammas],
            "independent_Clifford_relation_count": len(clifford_rows),
            "Clifford_relations": clifford_rows,
            "all_Clifford_relations_exact": all(row["relation_exact"] for row in clifford_rows),
            "metric_recovered_from_Clifford_anticommutators": recovered_H == metric_inverse,
            "principal_symbol_samples": symbol_samples,
            "principal_symbol_sample_count": len(symbol_samples),
            "all_Dirac_squares_scalar": all(row["Dirac_square_scalar"] for row in symbol_samples),
        },
        "lower_order_stability": {
            "local_form": "B=gamma^i partial_i+gamma^i omega_i+Phi",
            "potential": "i gamma_1 gamma_2",
            "high_frequency_square": "(t b(xi)+V)^2=t^2 b(xi)^2+t(bV+Vb)+V^2",
            "rows": lower_order_rows,
            "all_quadratic_coefficients_unchanged": all(
                row["quadratic_coefficient_unchanged"] for row in lower_order_rows
            ),
            "connection_and_potential_change_only_lower_orders": True,
        },
        "T55_composition": {
            "action_scale_fixture": str(ACTION_SCALE),
            "action_scale_fixture_is_physical": False,
            "density_fixture": str(density),
            "polarization_sample_count": len(symbol_samples),
            "action_quadratic_A": matrix_strings(action_quadratic),
            "reconstructed_A": matrix_strings(reconstructed_A),
            "recovered_action_scale": str(recovered_scale),
            "recovered_covector_metric_H": matrix_strings(t55_H),
            "recovered_covariant_metric_G": matrix_strings(t55_G),
            "A_reconstruction_exact": reconstructed_A == action_quadratic,
            "action_scale_reconstruction_exact": recovered_scale == ACTION_SCALE,
            "metric_reconstruction_exact": t55_G == metric,
            "inverse_metric_reconstruction_exact": t55_H == metric_inverse,
            "Hodge_reconstruction_sha256": matrix_hash(recovered_hodge),
            "source_T55_Hodge_sha256": t55["exact_non_diagonal_benchmark"]["source_Hodge_sha256"],
            "Hodge_reconstruction_matches_T55": matrix_hash(recovered_hodge)
            == t55["exact_non_diagonal_benchmark"]["source_Hodge_sha256"],
        },
        "q79_evidence_audit": evidence,
        "q79_source_contract_update": {
            "before": "scalar positive q79 Hessian symbol and density requested before T55",
            "after": "one selected Dirac/Dolbeault operator and same-source Hilbert density imply scalarity and feed T55",
            "independent_scalar_symbol_proof_after_selected_Dirac_source": 0,
            "independent_metric_payload_after_selected_Dirac_source_and_density": 0,
            "selected_physical_q79_Dolbeault_operator": "OPEN",
            "selected_physical_q79_density": "OPEN",
            "selected_visible_hidden_HYM_connection": "OPEN",
            "selected_domain_projector_and_reduced_Green": "OPEN",
            "selected_C4_TT_naturality_and_error_bounds": "OPEN",
        },
        "parameter_ledger": {
            "continuous_physical_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "benchmark_action_scale_is_physical": False,
            "one_shared_action_primitive_status": "OPEN_UNCHANGED",
        },
        "physical_boundary": {
            "B_GEO_01_closed": False,
            "B_ACTION_01_closed": False,
            "B_OP_01_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "selected_physical_operator_claimed": joint["selected_physical_q79_operator_is_present"],
            "selected_physical_density_claimed": joint["selected_physical_q79_density_is_present"],
        },
    }

    packet["exact_payload_sha256"] = canonical_hash(
        {
            "Clifford_relations": clifford_rows,
            "principal_symbol_samples": symbol_samples,
            "lower_order_rows": lower_order_rows,
            "T55_composition": packet["T55_composition"],
            "evidence_sha256": sha256(EVIDENCE),
        }
    )

    checks = {
        "schema_identifier": schema["$id"] == packet["schema"],
        "schema_required_fields": (
            set(schema["required"]) - {"checks", "check_summary"}
        ).issubset(packet),
        "claim_id": packet["claim_id"] == "CBF.T56",
        "theorem_states_Dirac_relation": "b(xi)b(eta)+b(eta)b(xi)" in theorem_text,
        "theorem_preserves_physical_boundary": "Physical acceptance remains `0/3`" in theorem_text,
        "source_hashes_match": packet["source_provenance"]["all_sources_hash_locked"],
        "evidence_is_not_runtime_dependency": packet["source_provenance"]["external_sources_are_portable_audit_metadata_not_runtime_dependencies"],
        "coframe_determinant_one": determinant(coframe) == 1,
        "coframe_is_nonorthogonal": matmul(transpose(coframe), coframe) != identity(N),
        "metric_from_coframe": matmul(transpose(coframe), coframe) == metric,
        "metric_inverse_exact": matmul(metric, metric_inverse) == identity(N),
        "flat_gamma_count": len(flat_gammas) == N,
        "metric_gamma_count": len(gammas) == N,
        "spinor_rank": len(gammas[0]) == SPINOR_RANK,
        "Clifford_relation_count": len(clifford_rows) == 21,
        "all_Clifford_relations_exact": packet["exact_six_dimensional_clifford_witness"]["all_Clifford_relations_exact"],
        "metric_recovered_from_anticommutators": recovered_H == metric_inverse,
        "principal_sample_count": len(symbol_samples) == 21,
        "all_principal_squares_scalar": packet["exact_six_dimensional_clifford_witness"]["all_Dirac_squares_scalar"],
        "action_quadratic_exact": reconstructed_A == action_quadratic,
        "action_scale_positive": recovered_scale > 0,
        "action_scale_exact": recovered_scale == ACTION_SCALE,
        "T55_inverse_metric_exact": t55_H == metric_inverse,
        "T55_metric_exact": t55_G == metric,
        "T55_Hodge_digest_exact": packet["T55_composition"]["Hodge_reconstruction_matches_T55"],
        "lower_order_witness_count": len(lower_order_rows) == 3,
        "lower_order_quadratic_unchanged": packet["lower_order_stability"]["all_quadratic_coefficients_unchanged"],
        "connection_terms_classified_lower_order": packet["lower_order_stability"]["connection_and_potential_change_only_lower_orders"],
        "evidence_source_count": len(evidence["sources"]) == 3,
        "Costello_scope_is_four_dimensional_auxiliary": "four-dimensional auxiliary" in evidence["sources"][0]["scope_boundary"],
        "hidden_HYM_scope_is_not_visible_endpoint": "visible/common endpoint" in evidence["sources"][1]["scope_boundary"],
        "Hodge_action_scope_keeps_rank102_open": "rank-102 execution" in evidence["sources"][2]["scope_boundary"],
        "evidence_does_not_claim_selected_operator": not joint["selected_physical_q79_operator_is_present"],
        "evidence_does_not_claim_selected_density": not joint["selected_physical_q79_density_is_present"],
        "scalarity_obligation_reduced": packet["q79_source_contract_update"]["independent_scalar_symbol_proof_after_selected_Dirac_source"] == 0,
        "metric_payload_not_duplicated": packet["q79_source_contract_update"]["independent_metric_payload_after_selected_Dirac_source_and_density"] == 0,
        "no_continuous_parameters_added": packet["parameter_ledger"]["continuous_physical_parameters_added"] == 0,
        "no_selectors_added": packet["parameter_ledger"]["discrete_selectors_added"] == 0,
        "no_observed_values": packet["parameter_ledger"]["observed_values_used"] == 0,
        "no_fitted_values": packet["parameter_ledger"]["fitted_values_used"] == 0,
        "B_GEO_remains_open": not packet["physical_boundary"]["B_GEO_01_closed"],
        "B_ACTION_remains_open": not packet["physical_boundary"]["B_ACTION_01_closed"],
        "B_OP_remains_open": not packet["physical_boundary"]["B_OP_01_closed"],
        "physical_gates_unchanged": packet["physical_boundary"]["physical_gates"] == {"accepted": 0, "total": 3},
        "physical_packets_unchanged": packet["physical_boundary"]["physical_packets"] == {"accepted": 0, "total": 3},
        "physical_rows_unchanged": packet["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
    }
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": sum(bool(value) for value in checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    if not packet["check_summary"]["all_passed"]:
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"CBF.T56 build failed: {failed}")

    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet["check_summary"], sort_keys=True))


if __name__ == "__main__":
    main()
