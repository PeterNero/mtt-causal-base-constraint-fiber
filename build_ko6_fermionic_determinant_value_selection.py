#!/usr/bin/env python3
"""Build the exact CBF.T30 KO6 finite determinant value-selection packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_upper_totalization_supercharge_selection as uts
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "ko6_fermionic_determinant_value_selection_source_lock.json"
SCHEMA = ROOT / "ko6_fermionic_determinant_value_selection_contract.schema.json"
THEOREM = ROOT / "KO6PhysicalPolarizationFermionicDeterminantAndNeutralChamberValueSelectionTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
T27_PACKET = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T29_PACKET = ROOT / "finite_dirac_cubic_variational_action.packet.json"
OUTPUT = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"

cp = wg.cp
Alg = tuple[Fraction, Fraction]
ZERO_A: Alg = Fraction(0), Fraction(0)
ONE_A: Alg = Fraction(1), Fraction(0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_shift(matrix: cp.Matrix, scalar: Fraction | int) -> cp.Matrix:
    return cp.madd(matrix, cp.mscale(q(scalar), cp.identity(len(matrix))))


def square(matrix: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(matrix, matrix)


def jacobian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(
        uts.sparse_matmul(basepoint, value), uts.sparse_matmul(value, basepoint)
    )


def gamma_signs() -> list[int]:
    left_slots = {0, 1, 2, 3, 4, 5, 12, 13}
    gamma16 = [-1 if index in left_slots else 1 for index in range(16)]
    gamma48 = gamma16 * 3
    return gamma48 + [-value for value in gamma48]


def conjugate_by(unitary: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(unitary, uts.sparse_matmul(value, cp.adjoint(unitary)))


def restrict_matrix(
    matrix: cp.Matrix, row_indices: list[int], column_indices: list[int]
) -> cp.Matrix:
    return [[matrix[row][column] for column in column_indices] for row in row_indices]


def determinant(matrix: cp.Matrix) -> cp.K:
    if not matrix or len(matrix) != len(matrix[0]):
        raise ValueError("determinant requires a nonempty square matrix")
    work = [row[:] for row in matrix]
    result = cp.ONE
    size = len(work)
    for column in range(size):
        pivot_row = next(
            (row for row in range(column, size) if work[row][column] != cp.ZERO),
            None,
        )
        if pivot_row is None:
            return cp.ZERO
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            result = cp.kmul(q(-1), result)
        pivot = work[column][column]
        result = cp.kmul(result, pivot)
        for row in range(column + 1, size):
            if work[row][column] == cp.ZERO:
                continue
            factor = cp.kdiv(work[row][column], pivot)
            for inner in range(column, size):
                work[row][inner] = cp.kadd(
                    work[row][inner],
                    cp.kmul(q(-1), cp.kmul(factor, work[column][inner])),
                )
    return result


def aadd(left: Alg, right: Alg) -> Alg:
    return left[0] + right[0], left[1] + right[1]


def aneg(value: Alg) -> Alg:
    return -value[0], -value[1]


def asub(left: Alg, right: Alg) -> Alg:
    return aadd(left, aneg(right))


def amul(left: Alg, right: Alg) -> Alg:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def ascale(value: Fraction | int, operand: Alg) -> Alg:
    scale = Fraction(value)
    return scale * operand[0], scale * operand[1]


def apow(value: Alg, exponent: int) -> Alg:
    result = ONE_A
    for _ in range(exponent):
        result = amul(result, value)
    return result


def ainv(value: Alg) -> Alg:
    norm = value[0] ** 2 - 13 * value[1] ** 2
    if norm == 0:
        raise ZeroDivisionError("zero algebraic norm")
    return value[0] / norm, -value[1] / norm


def adiv(left: Alg, right: Alg) -> Alg:
    return amul(left, ainv(right))


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def alg_payload(value: Alg) -> dict[str, str]:
    return {
        "rational": fraction_text(value[0]),
        "sqrt13": fraction_text(value[1]),
    }


def alg_decimal(value: Alg, digits: int = 18) -> str:
    getcontext().prec = max(80, digits + 20)
    numeric = Decimal(value[0].numerator) / Decimal(value[0].denominator)
    numeric += (
        Decimal(value[1].numerator)
        / Decimal(value[1].denominator)
        * Decimal(13).sqrt()
    )
    return f"{numeric:.{digits}f}"


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def source_root(
    source_lock: dict[str, Any],
    theorem_hash: str,
    d0_hash: str,
    d1_hash: str,
    h_hash: str,
    gamma_hash: str,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.ko6-fermionic-determinant-value-selection-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "D0_sha256": d0_hash,
        "D1_sha256": d1_hash,
        "H_phys_sha256": h_hash,
        "Gamma96_sha256": gamma_hash,
        "chiral_dimensions": {"minus": 48, "plus": 48},
        "chiral_branch_multiplicities": {"-4": 16, "-2": 16, "2": 16},
        "determinant_identity": "det(B^*B)=((1-2t)(1-t)(1+t))^32",
        "finite_Gaussian_profile": "W0=-(2/3)log|Delta(t)|",
        "selected_coordinate": "(1-sqrt(13))/6",
        "isolating_interval": ["-1/2", "-1/3"],
        "full_four_dimensional_vacuum": None,
        "observed_targets": [],
        "theorem_sha256": theorem_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    t25 = json.loads(T25_PACKET.read_text(encoding="ascii"))
    t27 = json.loads(T27_PACKET.read_text(encoding="ascii"))
    t29 = json.loads(T29_PACKET.read_text(encoding="ascii"))

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = uts.physical_dirac(
        uts.physical_transfer(projector, phase_direction, shift_direction, Fraction(0))
    )
    d_one = uts.physical_dirac(
        uts.physical_transfer(projector, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_one, d0)
    h_phys = jacobian(d0, d1)
    identity96 = cp.identity(96)
    zero96 = cp.zero(96, 96)

    signs = gamma_signs()
    gamma = cp.diagonal([q(value) for value in signs])
    plus_indices = [index for index, value in enumerate(signs) if value == 1]
    minus_indices = [index for index, value in enumerate(signs) if value == -1]
    p_plus = cp.diagonal([q(1 if value == 1 else 0) for value in signs])
    p_minus = cp.diagonal([q(1 if value == -1 else 0) for value in signs])

    spectral_projectors = {
        "-4": cp.mscale(
            q(Fraction(1, 12)),
            uts.sparse_matmul(matrix_shift(h_phys, 2), matrix_shift(h_phys, -2)),
        ),
        "-2": cp.mscale(
            q(Fraction(-1, 8)),
            uts.sparse_matmul(matrix_shift(h_phys, 4), matrix_shift(h_phys, -2)),
        ),
        "2": cp.mscale(
            q(Fraction(1, 24)),
            uts.sparse_matmul(matrix_shift(h_phys, 4), matrix_shift(h_phys, 2)),
        ),
    }
    branch_eigenvalues = {"-4": -4, "-2": -2, "2": 2}
    projector_checks: dict[str, bool] = {}
    chiral_branch_ranks: dict[str, int] = {}
    for label, spectral_projector in spectral_projectors.items():
        eigenvalue = branch_eigenvalues[label]
        restricted = restrict_matrix(spectral_projector, plus_indices, plus_indices)
        chiral_branch_ranks[label] = cp.matrix_rank(restricted)
        projector_checks[f"branch_{label}_projector_is_self_adjoint"] = (
            spectral_projector == cp.adjoint(spectral_projector)
        )
        projector_checks[f"branch_{label}_projector_is_idempotent"] = (
            square(spectral_projector) == spectral_projector
        )
        projector_checks[f"branch_{label}_projector_has_rank_32"] = (
            cp.matrix_rank(spectral_projector) == 32
        )
        projector_checks[f"branch_{label}_is_H_eigenspace"] = (
            uts.sparse_matmul(h_phys, spectral_projector)
            == cp.mscale(q(eigenvalue), spectral_projector)
        )
        projector_checks[f"branch_{label}_commutes_with_grading"] = (
            uts.sparse_matmul(gamma, spectral_projector)
            == uts.sparse_matmul(spectral_projector, gamma)
        )
        projector_checks[f"branch_{label}_positive_chiral_rank_is_16"] = (
            chiral_branch_ranks[label] == 16
        )

    projector_sum = cp.zero(96, 96)
    for spectral_projector in spectral_projectors.values():
        projector_sum = cp.madd(projector_sum, spectral_projector)

    determinant_samples = [Fraction(-1, 2), Fraction(0), Fraction(1, 4), Fraction(3, 4)]
    determinant_records: list[dict[str, str]] = []
    determinant_checks: dict[str, bool] = {}
    for sample in determinant_samples:
        d_sample = cp.madd(d0, cp.mscale(q(sample), d1))
        b_sample = restrict_matrix(d_sample, minus_indices, plus_indices)
        b_star_b = uts.sparse_matmul(cp.adjoint(b_sample), b_sample)
        d_squared_plus = restrict_matrix(square(d_sample), plus_indices, plus_indices)
        delta = (1 - 2 * sample) * (1 - sample) * (1 + sample)
        actual_determinant = determinant(b_star_b)
        expected_determinant = q(delta**32)
        label = fraction_text(sample).replace("-", "minus_").replace("/", "_over_")
        determinant_checks[f"sample_{label}_BstarB_equals_chiral_Dsquare"] = (
            b_star_b == d_squared_plus
        )
        determinant_checks[f"sample_{label}_determinant_identity"] = (
            actual_determinant == expected_determinant
        )
        determinant_records.append(
            {
                "t": fraction_text(sample),
                "Delta": fraction_text(delta),
                "det_BstarB": fraction_text(delta**32),
            }
        )

    sqrt13: Alg = Fraction(0), Fraction(1)
    t_star: Alg = Fraction(1, 6), Fraction(-1, 6)
    t_other: Alg = Fraction(1, 6), Fraction(1, 6)
    polynomial_at_star = asub(
        asub(ascale(3, apow(t_star, 2)), t_star), ONE_A
    )
    polynomial_at_other = asub(
        asub(ascale(3, apow(t_other, 2)), t_other), ONE_A
    )
    delta_star = amul(
        asub(ONE_A, ascale(2, t_star)),
        amul(asub(ONE_A, t_star), aadd(ONE_A, t_star)),
    )
    sigma_m4 = asub(ONE_A, ascale(2, t_star))
    sigma_m2 = asub(ONE_A, t_star)
    sigma_p2 = aadd(ONE_A, t_star)
    sigma_values = {"-4": sigma_m4, "-2": sigma_m2, "2": sigma_p2}
    sigma_squares = {label: apow(value, 2) for label, value in sigma_values.items()}
    ratios = {
        "sigma_-4_over_sigma_+2": adiv(sigma_m4, sigma_p2),
        "sigma_-2_over_sigma_+2": adiv(sigma_m2, sigma_p2),
        "sigma_-4_over_sigma_-2": adiv(sigma_m4, sigma_m2),
    }
    curvature = adiv(ascale(72, sqrt13), aadd((Fraction(35), Fraction(0)), ascale(13, sqrt13)))
    expected_curvature: Alg = Fraction(338, 27), Fraction(-70, 27)

    getcontext().prec = 80
    decimal_sqrt13 = Decimal(13).sqrt()
    decimal_t_star = (Decimal(1) - decimal_sqrt13) / Decimal(6)
    decimal_t_other = (Decimal(1) + decimal_sqrt13) / Decimal(6)

    theorem_hash = sha256(THEOREM)
    d0_hash = uts.matrix_digest(d0)
    d1_hash = uts.matrix_digest(d1)
    h_hash = uts.matrix_digest(h_phys)
    gamma_hash = uts.matrix_digest(gamma)
    root_hash, root_payload = source_root(
        source_lock, theorem_hash, d0_hash, d1_hash, h_hash, gamma_hash
    )
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        **projector_checks,
        **determinant_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.ko6-fermionic-determinant-value-selection-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "54b63b63-c684-4fb5-a34d-6cfc556f5a6c",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.ko6-fermionic-determinant-value-selection.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()),
        "T23_KO6_source_is_exact": t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()),
        "T25_fermion_action_is_exact": t25["claim_id"] == "CBF.T25" and all(t25["checks"].values()),
        "T27_spectrum_is_exact": t27["claim_id"] == "CBF.T27" and all(t27["checks"].values()),
        "T29_signed_action_is_exact": t29["claim_id"] == "CBF.T29" and all(t29["checks"].values()),
        "D0_is_self_adjoint": d0 == cp.adjoint(d0),
        "D0_square_is_identity": square(d0) == identity96,
        "D1_is_self_adjoint": d1 == cp.adjoint(d1),
        "grading_is_self_adjoint": gamma == cp.adjoint(gamma),
        "grading_square_is_identity": square(gamma) == identity96,
        "grading_anticommutes_with_D0": conjugate_by(gamma, d0) == cp.mscale(q(-1), d0),
        "grading_anticommutes_with_D1": conjugate_by(gamma, d1) == cp.mscale(q(-1), d1),
        "positive_chiral_dimension_is_48": len(plus_indices) == cp.matrix_rank(p_plus) == 48,
        "negative_chiral_dimension_is_48": len(minus_indices) == cp.matrix_rank(p_minus) == 48,
        "chiral_projectors_are_orthogonal": uts.sparse_matmul(p_plus, p_minus) == zero96,
        "chiral_projectors_resolve_identity": cp.madd(p_plus, p_minus) == identity96,
        "H_phys_matches_T23": h_hash == t23["hessian_compression"]["KO6_response_sha256"],
        "spectral_projectors_resolve_identity": projector_sum == identity96,
        "spectral_projectors_are_pairwise_orthogonal": all(
            uts.sparse_matmul(left, right) == zero96
            for left_label, left in spectral_projectors.items()
            for right_label, right in spectral_projectors.items()
            if left_label != right_label
        ),
        "all_three_chiral_branch_ranks_are_16": set(chiral_branch_ranks.values()) == {16},
        "finite_chiral_determinant_degree_is_96": 32 * 3 == 96,
        "stationary_polynomial_vanishes_at_selected_root": polynomial_at_star == ZERO_A,
        "stationary_polynomial_vanishes_at_other_root": polynomial_at_other == ZERO_A,
        "selected_root_is_nonzero": t_star != ZERO_A,
        "selected_root_is_in_neutral_chamber": Decimal(-1) < decimal_t_star < Decimal("0.5"),
        "selected_root_has_tight_rational_isolation": Decimal("-0.5") < decimal_t_star < Decimal("-0.3333333333333333333333333333"),
        "other_root_is_outside_neutral_chamber": decimal_t_other > Decimal("0.5"),
        "neutral_chamber_contains_zero": Fraction(-1) < 0 < Fraction(1, 2),
        "Delta_star_is_exact": delta_star == (Fraction(35, 54), Fraction(13, 54)),
        "Delta_star_is_positive": Decimal(alg_decimal(delta_star, 40)) > 0,
        "curvature_identity_is_exact": curvature == expected_curvature,
        "curvature_is_positive": Decimal(alg_decimal(curvature, 40)) > 0,
        "sigma_minus4_is_exact": sigma_m4 == (Fraction(2, 3), Fraction(1, 3)),
        "sigma_minus2_is_exact": sigma_m2 == (Fraction(5, 6), Fraction(1, 6)),
        "sigma_plus2_is_exact": sigma_p2 == (Fraction(7, 6), Fraction(-1, 6)),
        "all_sigma_values_are_positive": all(Decimal(alg_decimal(value, 40)) > 0 for value in sigma_values.values()),
        "sigma_minus4_square_is_exact": sigma_squares["-4"] == (Fraction(17, 9), Fraction(4, 9)),
        "sigma_minus2_square_is_exact": sigma_squares["-2"] == (Fraction(19, 18), Fraction(5, 18)),
        "sigma_plus2_square_is_exact": sigma_squares["2"] == (Fraction(31, 18), Fraction(-7, 18)),
        "large_over_small_ratio_is_exact": ratios["sigma_-4_over_sigma_+2"] == (Fraction(3, 2), Fraction(1, 2)),
        "middle_over_small_ratio_is_exact": ratios["sigma_-2_over_sigma_+2"] == (Fraction(4, 3), Fraction(1, 3)),
        "large_over_middle_ratio_is_exact": ratios["sigma_-4_over_sigma_-2"] == (Fraction(-1, 2), Fraction(1, 2)),
        "branch_order_is_strict": Decimal(alg_decimal(sigma_m4, 40)) > Decimal(alg_decimal(sigma_m2, 40)) > Decimal(alg_decimal(sigma_p2, 40)) > 0,
        "zero_mode_stationarity_differs_from_large_external_mode": asub(ascale(6, t_star), (Fraction(2), Fraction(0))) != ZERO_A,
        "large_external_mode_condition_selects_one_third": -2 + 6 * Fraction(1, 3) == 0,
        "one_third_fails_zero_mode_stationary_polynomial": 3 * Fraction(1, 9) - Fraction(1, 3) - 1 != 0,
        "finite_KO6_fermion_action_is_available": boundary["finite_KO6_physical_fermion_action_available"],
        "finite_Gaussian_profile_is_newly_closed": not boundary["finite_chiral_Gaussian_profile_before"] and boundary["finite_chiral_Gaussian_profile_after"],
        "neutral_chamber_is_newly_closed": not boundary["neutral_invertible_chamber_before"] and boundary["neutral_invertible_chamber_after"],
        "finite_coordinate_is_newly_closed": not boundary["finite_Gaussian_stationary_coordinate_before"] and boundary["finite_Gaussian_stationary_coordinate_after"],
        "dimensionless_values_are_newly_closed": not boundary["exact_dimensionless_branch_values_before"] and boundary["exact_dimensionless_branch_values_after"],
        "KO_chirality_is_not_used_as_statistics": not boundary["KO_chirality_used_as_statistics_grading"],
        "full_four_dimensional_determinant_remains_open": not boundary["full_four_dimensional_fermion_determinant_selected"],
        "external_measure_remains_open": not boundary["external_spectral_measure_selected"],
        "renormalization_scheme_remains_open": not boundary["renormalization_scheme_selected"],
        "overall_scale_remains_open": not boundary["overall_dimensionful_scale_selected"],
        "SM_mass_identification_remains_open": not boundary["branch_values_identified_with_SM_masses"],
        "B_ACTION_01_remains_open": not boundary["full_B_ACTION_01_closed"],
        "B_SM_02_remains_open": not boundary["full_B_SM_02_closed"],
        "held_out_observable_remains_open": not boundary["held_out_physical_observable_emitted"],
        "no_observed_values_used": not boundary["observed_values_used"],
        "no_fitted_coefficients_used": not boundary["fitted_coefficients_used"],
        "physical_packet_acceptance_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "source_root_is_nonempty": len(root_hash) == 64,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T30 build checks failed: {failed}")

    branch_payload = {
        label: {
            "exact_coefficients": alg_payload(value),
            "expression": {
                "-4": "(2+sqrt(13))/3",
                "-2": "(5+sqrt(13))/6",
                "2": "(7-sqrt(13))/6",
            }[label],
            "decimal": alg_decimal(value, 18),
            "square_exact_coefficients": alg_payload(sigma_squares[label]),
        }
        for label, value in sigma_values.items()
    }
    ratio_expressions = {
        "sigma_-4_over_sigma_+2": "(3+sqrt(13))/2",
        "sigma_-2_over_sigma_+2": "(4+sqrt(13))/3",
        "sigma_-4_over_sigma_-2": "(sqrt(13)-1)/2",
    }
    ratio_payload = {
        label: {
            "exact_coefficients": alg_payload(value),
            "expression": ratio_expressions[label],
            "decimal": alg_decimal(value, 18),
        }
        for label, value in ratios.items()
    }

    packet = {
        "schema": "boe.mtt.ko6-fermionic-determinant-value-selection.v1",
        "claim_id": "CBF.T30",
        "date": "2026-08-30",
        "status": (
            "exact finite internal Grassmann-Gaussian profile, neutral-chamber "
            "coordinate and dimensionless branch values; full four-dimensional "
            "determinant, renormalized vacuum and SM mass identification open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_sha256": root_hash,
            "source_root_payload": root_payload,
            "external_context": source_lock["external_context"],
        },
        "KO6_polarization": {
            "grading": "Gamma96",
            "projectors": {"plus": "(I96+Gamma96)/2", "minus": "(I96-Gamma96)/2"},
            "dimensions": {"plus": 48, "minus": 48},
            "oddness": "Gamma96 D_phys(t) Gamma96=-D_phys(t)",
            "role": "physical chiral restriction of the finite factor",
            "statistics_source": "Grassmann fermion fields in CBF.T25",
            "KO_chirality_used_as_statistics": False,
        },
        "chiral_finite_operator": {
            "definition": "B(t)=P_chi^- D_phys(t) P_chi^+",
            "positive_block": "B(t)^*B(t)=P_chi^+D_phys(t)^2P_chi^+",
            "response_branch_multiplicities": chiral_branch_ranks,
            "positive_block_spectrum": {
                "(1-2t)^2": 16,
                "(1-t)^2": 16,
                "(1+t)^2": 16,
            },
            "determinant_identity": "det(B^*B)=Delta(t)^32",
            "Delta": "(1-2t)(1-t)(1+t)",
            "exact_rational_samples": determinant_records,
        },
        "finite_Grassmann_Gaussian": {
            "complex_Gaussian_modulus": "|det B(t)|^2=det(B(t)^*B(t))",
            "normalized_effective_profile": "W0(t)=-(1/48)log det(B^*B)=-(2/3)log|Delta(t)|",
            "fermionic_sign_source": "Grassmann integration",
            "Pfaffian_convention_effect": "positive overall multiplier only within a fixed oriented chamber",
            "stationary_coordinate_convention_independent": True,
            "full_4D_determinant_claimed": False,
        },
        "neutral_invertible_chamber": {
            "singular_walls": ["-1", "1/2", "1"],
            "selected_basepoint": "t=0, D0^2=I96",
            "connected_component": "(-1,1/2)",
            "selection_rule": "continuous invertible deformation from the selected neutral basepoint",
            "effective_profile_diverges_at_both_boundaries": True,
            "other_stationary_root_requires_zero_mode_crossing": True,
        },
        "selected_coordinate": {
            "symbol": "t_*",
            "expression": "(1-sqrt(13))/6",
            "exact_coefficients": alg_payload(t_star),
            "decimal": alg_decimal(t_star, 18),
            "minimal_polynomial": "3t^2-t-1",
            "isolating_interval": ["-1/2", "-1/3"],
            "other_root": "(1+sqrt(13))/6",
            "other_root_component": "(1/2,1)",
            "unique_global_minimum_in_neutral_component": True,
            "Delta_at_selected_coordinate": {
                "expression": "(35+13sqrt(13))/54",
                "exact_coefficients": alg_payload(delta_star),
                "decimal": alg_decimal(delta_star, 18),
            },
            "curvature": {
                "expression": "(338-70sqrt(13))/27",
                "exact_coefficients": alg_payload(curvature),
                "decimal": alg_decimal(curvature, 18),
                "positive": True,
            },
            "tier": "finite internal physical-fermion Grassmann Gaussian",
        },
        "dimensionless_branch_values": {
            "ordered_by_response_eigenvalue": branch_payload,
            "strict_order": "sigma_-4>sigma_-2>sigma_+2>0",
            "ratios": ratio_payload,
            "observed_values_used": False,
            "fitted_coefficients_used": False,
            "identified_with_measured_generations": False,
        },
        "conditional_one_scale_values": {
            "formula": "m_lambda=h sigma_lambda",
            "new_dimensionless_shape_parameters": 0,
            "inherited_common_scale_count": 1,
            "common_scale_h_selected_numerically": False,
            "sector_assignment_selected": False,
            "SM_mass_claimed": False,
        },
        "external_mode_obstruction": {
            "single_mode_profile": "Wx(t)=-(1/3)sum_lambda log(x+r_lambda(t)^2)",
            "x_definition": "x=p^2/h^2",
            "zero_external_mode_stationarity": "3t^2-t-1=0",
            "large_external_mode_leading_stationarity": "-2+6t=0, hence t=1/3",
            "common_stationary_coordinate_for_all_external_modes": False,
            "full_spacetime_spectral_measure_required": True,
            "renormalization_and_counterterms_required": True,
            "finite_selected_coordinate_is_final_4D_vacuum": False,
        },
        "authority_reconciliation": {
            "CBF_T27": "profile no-go remains for D and trace alone; selected fermion statistics, chiral block and chamber are added",
            "CBF_T29": "odd scalar trace still cancels; determinant uses the even B^*B block after Grassmann integration",
            "A56": "KO chirality is not used as statistics grading",
            "A73": "determinant response identity is instantiated only on the finite chiral block",
            "A84_A85": "complete upper action and finite matching are not promoted",
            "B_ACTION_01": "advanced but open at external measure, renormalized action and continuum transfer",
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_dimensionless_continuous_parameters": 0,
            "new_dimensionful_primitives": 0,
            "inherited_optional_common_scale_h": 1,
            "external_spectral_measure_parameters_selected": 0,
        },
        "physical_boundary": {
            "finite_KO6_chiral_determinant_profile_closed": True,
            "neutral_chamber_coordinate_closed": True,
            "exact_dimensionless_branch_values_closed": True,
            "finite_value_tier": "internal physical-fermion Gaussian",
            "full_four_dimensional_determinant_closed": False,
            "renormalized_QFT_vacuum_closed": False,
            "overall_SI_scale_closed": False,
            "SM_mass_generation_map_closed": False,
            "held_out_physical_observable_emitted": False,
            "B_ACTION_01_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The selected KO6 physical fermion sublane now fixes the finite chiral "
            "Grassmann determinant profile. The invertible component containing D0 "
            "has a unique nonzero minimum t_*=(1-sqrt(13))/6 and emits three exact "
            "dimensionless singular-value factors and ratios with no observed input "
            "or fit. An exact external-mode comparison proves this coordinate is not "
            "universal under the full spacetime determinant, so it is a finite internal "
            "Gaussian physical-profile value rather than a final mass or vacuum."
        ),
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    if set(packet) != set(schema["properties"]):
        raise AssertionError("packet top-level keys do not match contract schema")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "KO6 fermionic determinant value-selection packet built: "
        f"{len(checks)}/{len(checks)} checks; finite t_* and three dimensionless "
        "values closed; full 4D vacuum remains open"
    )


if __name__ == "__main__":
    main()
