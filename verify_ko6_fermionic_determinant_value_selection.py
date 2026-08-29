#!/usr/bin/env python3
"""Independent exact verification of the CBF.T30 finite value selector."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "ko6_fermionic_determinant_value_selection.packet.json"
SOURCE_LOCK_PATH = ROOT / "ko6_fermionic_determinant_value_selection_source_lock.json"
SCHEMA_PATH = ROOT / "ko6_fermionic_determinant_value_selection_contract.schema.json"
THEOREM_PATH = ROOT / "KO6PhysicalPolarizationFermionicDeterminantAndNeutralChamberValueSelectionTheorem_v1.md"
T20_PATH = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T25_PATH = ROOT / "direct_finite_source_continuum.packet.json"
T27_PATH = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T29_PATH = ROOT / "finite_dirac_cubic_variational_action.packet.json"

Alg = tuple[Fraction, Fraction]
ZERO_A: Alg = Fraction(0), Fraction(0)
ONE_A: Alg = Fraction(1), Fraction(0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


def encode_matrix(matrix: cp.Matrix) -> list[list[list[str]]]:
    return [[cp.encode(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    encoded = json.dumps(encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
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


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_shift(matrix: cp.Matrix, scalar: Fraction | int) -> cp.Matrix:
    return cp.madd(matrix, cp.mscale(q(scalar), cp.identity(len(matrix))))


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    rows = sum(len(block) for block in blocks)
    columns = sum(len(block[0]) for block in blocks)
    result = cp.zero(rows, columns)
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row, values in enumerate(block):
            for column, value in enumerate(values):
                result[row_offset + row][column_offset + column] = value
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def conjugate_entries(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def incidence(pairs: tuple[tuple[int, int], ...]) -> cp.Matrix:
    result = cp.zero(16, 16)
    for target, source in pairs:
        result[target][source] = cp.ONE
    return result


def family_map(projector: cp.Matrix, direction: cp.Matrix, t: Fraction) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), projector), cp.mscale(q(t), direction))


def transfer(
    projector: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    t: Fraction,
) -> cp.Matrix:
    phase_incidence = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    shift_incidence = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(projector, phase_direction, t), phase_incidence),
        cp.kron(family_map(projector, shift_direction, t), shift_incidence),
    )


def physical_dirac(transfer_matrix: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    return block_diag([particle, conjugate_entries(particle)])


def square(matrix: cp.Matrix) -> cp.Matrix:
    return sparse_matmul(matrix, matrix)


def jacobian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(sparse_matmul(basepoint, value), sparse_matmul(value, basepoint))


def grading_signs() -> list[int]:
    left_slots = {0, 1, 2, 3, 4, 5, 12, 13}
    gamma16 = [-1 if index in left_slots else 1 for index in range(16)]
    gamma48 = gamma16 * 3
    return gamma48 + [-value for value in gamma48]


def restrict_matrix(
    matrix: cp.Matrix, row_indices: list[int], column_indices: list[int]
) -> cp.Matrix:
    return [[matrix[row][column] for column in column_indices] for row in row_indices]


def determinant(matrix: cp.Matrix) -> cp.K:
    if not matrix or len(matrix) != len(matrix[0]):
        raise ValueError("determinant requires a nonempty square matrix")
    work = [row[:] for row in matrix]
    result = cp.ONE
    for column in range(len(work)):
        pivot_row = next(
            (row for row in range(column, len(work)) if work[row][column] != cp.ZERO),
            None,
        )
        if pivot_row is None:
            return cp.ZERO
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            result = cp.kmul(q(-1), result)
        pivot = work[column][column]
        result = cp.kmul(result, pivot)
        for row in range(column + 1, len(work)):
            if work[row][column] == cp.ZERO:
                continue
            factor = cp.kdiv(work[row][column], pivot)
            for inner in range(column, len(work)):
                work[row][inner] = cp.kadd(
                    work[row][inner],
                    cp.kmul(q(-1), cp.kmul(factor, work[column][inner])),
                )
    return result


def aadd(left: Alg, right: Alg) -> Alg:
    return left[0] + right[0], left[1] + right[1]


def asub(left: Alg, right: Alg) -> Alg:
    return left[0] - right[0], left[1] - right[1]


def amul(left: Alg, right: Alg) -> Alg:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def ascale(scale: Fraction | int, value: Alg) -> Alg:
    scalar = Fraction(scale)
    return scalar * value[0], scalar * value[1]


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
    return {"rational": fraction_text(value[0]), "sqrt13": fraction_text(value[1])}


def alg_decimal(value: Alg, digits: int = 18) -> str:
    getcontext().prec = max(80, digits + 20)
    numeric = Decimal(value[0].numerator) / Decimal(value[0].denominator)
    numeric += (
        Decimal(value[1].numerator)
        / Decimal(value[1].denominator)
        * Decimal(13).sqrt()
    )
    return f"{numeric:.{digits}f}"


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK_PATH.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="ascii"))
    t20 = json.loads(T20_PATH.read_text(encoding="ascii"))
    t23 = json.loads(T23_PATH.read_text(encoding="ascii"))
    t25 = json.loads(T25_PATH.read_text(encoding="ascii"))
    t27 = json.loads(T27_PATH.read_text(encoding="ascii"))
    t29 = json.loads(T29_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.ko6-fermionic-determinant-value-selection.v1", "packet schema", passed)
    require(packet["claim_id"] == "CBF.T30", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(source_lock["handoff_id"] == "54b63b63-c684-4fb5-a34d-6cfc556f5a6c", "handoff pin", passed)
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash: {source['path']}", passed)

    for upstream, claim in ((t20, "CBF.T20"), (t23, "CBF.T23"), (t25, "CBF.T25"), (t27, "CBF.T27"), (t29, "CBF.T29")):
        require(upstream["claim_id"] == claim and all(upstream["checks"].values()), f"{claim} exact", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = decode_matrix(primitive["P"])
    x = decode_matrix(primitive["X"])
    z = decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(0)))
    d_one = physical_dirac(transfer(projector, phase_direction, shift_direction, Fraction(1)))
    d1 = matrix_sub(d_one, d0)
    h_phys = jacobian(d0, d1)
    identity96 = cp.identity(96)
    zero96 = cp.zero(96, 96)

    signs = grading_signs()
    gamma = cp.diagonal([q(value) for value in signs])
    plus_indices = [index for index, value in enumerate(signs) if value == 1]
    minus_indices = [index for index, value in enumerate(signs) if value == -1]
    p_plus = cp.diagonal([q(value == 1) for value in signs])
    p_minus = cp.diagonal([q(value == -1) for value in signs])
    require(d0 == cp.adjoint(d0), "D0 self-adjoint", passed)
    require(square(d0) == identity96, "D0 involution", passed)
    require(d1 == cp.adjoint(d1), "D1 self-adjoint", passed)
    require(square(gamma) == identity96, "grading involution", passed)
    require(sparse_matmul(gamma, d0) == cp.mscale(q(-1), sparse_matmul(d0, gamma)), "grading odd D0", passed)
    require(sparse_matmul(gamma, d1) == cp.mscale(q(-1), sparse_matmul(d1, gamma)), "grading odd D1", passed)
    require(len(plus_indices) == cp.matrix_rank(p_plus) == 48, "plus chiral dimension", passed)
    require(len(minus_indices) == cp.matrix_rank(p_minus) == 48, "minus chiral dimension", passed)
    require(sparse_matmul(p_plus, p_minus) == zero96, "chiral orthogonality", passed)
    require(cp.madd(p_plus, p_minus) == identity96, "chiral resolution", passed)
    require(matrix_digest(h_phys) == t23["hessian_compression"]["KO6_response_sha256"], "T23 response digest", passed)

    spectral_projectors = {
        "-4": cp.mscale(q(Fraction(1, 12)), sparse_matmul(matrix_shift(h_phys, 2), matrix_shift(h_phys, -2))),
        "-2": cp.mscale(q(Fraction(-1, 8)), sparse_matmul(matrix_shift(h_phys, 4), matrix_shift(h_phys, -2))),
        "2": cp.mscale(q(Fraction(1, 24)), sparse_matmul(matrix_shift(h_phys, 4), matrix_shift(h_phys, 2))),
    }
    branch_eigenvalues = {"-4": -4, "-2": -2, "2": 2}
    projector_sum = cp.zero(96, 96)
    chiral_ranks: dict[str, int] = {}
    for label, spectral_projector in spectral_projectors.items():
        projector_sum = cp.madd(projector_sum, spectral_projector)
        restricted = restrict_matrix(spectral_projector, plus_indices, plus_indices)
        chiral_ranks[label] = cp.matrix_rank(restricted)
        require(spectral_projector == cp.adjoint(spectral_projector), f"{label} projector self-adjoint", passed)
        require(square(spectral_projector) == spectral_projector, f"{label} projector idempotent", passed)
        require(cp.matrix_rank(spectral_projector) == 32, f"{label} branch rank", passed)
        require(sparse_matmul(h_phys, spectral_projector) == cp.mscale(q(branch_eigenvalues[label]), spectral_projector), f"{label} eigenspace", passed)
        require(sparse_matmul(gamma, spectral_projector) == sparse_matmul(spectral_projector, gamma), f"{label} grading reduction", passed)
        require(chiral_ranks[label] == 16, f"{label} chiral rank", passed)
    require(projector_sum == identity96, "spectral resolution", passed)
    for left_label, left in spectral_projectors.items():
        for right_label, right in spectral_projectors.items():
            if left_label != right_label:
                require(sparse_matmul(left, right) == zero96, f"{left_label}/{right_label} orthogonality", passed)

    determinant_records: list[dict[str, str]] = []
    for sample in (Fraction(-1, 2), Fraction(0), Fraction(1, 4), Fraction(3, 4)):
        d_sample = cp.madd(d0, cp.mscale(q(sample), d1))
        b_sample = restrict_matrix(d_sample, minus_indices, plus_indices)
        b_star_b = sparse_matmul(cp.adjoint(b_sample), b_sample)
        d_squared_plus = restrict_matrix(square(d_sample), plus_indices, plus_indices)
        delta = (1 - 2 * sample) * (1 - sample) * (1 + sample)
        require(b_star_b == d_squared_plus, f"chiral square t={sample}", passed)
        require(determinant(b_star_b) == q(delta**32), f"determinant t={sample}", passed)
        determinant_records.append({"t": fraction_text(sample), "Delta": fraction_text(delta), "det_BstarB": fraction_text(delta**32)})

    t_star: Alg = Fraction(1, 6), Fraction(-1, 6)
    t_other: Alg = Fraction(1, 6), Fraction(1, 6)
    stationary = lambda value: asub(asub(ascale(3, apow(value, 2)), value), ONE_A)
    require(stationary(t_star) == ZERO_A, "selected stationary root", passed)
    require(stationary(t_other) == ZERO_A, "other stationary root", passed)
    delta_star = amul(asub(ONE_A, ascale(2, t_star)), amul(asub(ONE_A, t_star), aadd(ONE_A, t_star)))
    require(delta_star == (Fraction(35, 54), Fraction(13, 54)), "selected determinant factor", passed)
    sigma = {
        "-4": asub(ONE_A, ascale(2, t_star)),
        "-2": asub(ONE_A, t_star),
        "2": aadd(ONE_A, t_star),
    }
    expected_sigma = {
        "-4": (Fraction(2, 3), Fraction(1, 3)),
        "-2": (Fraction(5, 6), Fraction(1, 6)),
        "2": (Fraction(7, 6), Fraction(-1, 6)),
    }
    require(sigma == expected_sigma, "exact branch factors", passed)
    sigma_squares = {label: apow(value, 2) for label, value in sigma.items()}
    require(sigma_squares == {
        "-4": (Fraction(17, 9), Fraction(4, 9)),
        "-2": (Fraction(19, 18), Fraction(5, 18)),
        "2": (Fraction(31, 18), Fraction(-7, 18)),
    }, "exact branch squares", passed)
    ratios = {
        "sigma_-4_over_sigma_+2": adiv(sigma["-4"], sigma["2"]),
        "sigma_-2_over_sigma_+2": adiv(sigma["-2"], sigma["2"]),
        "sigma_-4_over_sigma_-2": adiv(sigma["-4"], sigma["-2"]),
    }
    require(ratios == {
        "sigma_-4_over_sigma_+2": (Fraction(3, 2), Fraction(1, 2)),
        "sigma_-2_over_sigma_+2": (Fraction(4, 3), Fraction(1, 3)),
        "sigma_-4_over_sigma_-2": (Fraction(-1, 2), Fraction(1, 2)),
    }, "exact branch ratios", passed)
    curvature = adiv((Fraction(0), Fraction(72)), (Fraction(35), Fraction(13)))
    require(curvature == (Fraction(338, 27), Fraction(-70, 27)), "exact curvature", passed)

    getcontext().prec = 80
    numeric = {label: Decimal(alg_decimal(value, 40)) for label, value in sigma.items()}
    numeric_t_star = Decimal(alg_decimal(t_star, 40))
    numeric_t_other = Decimal(alg_decimal(t_other, 40))
    require(Decimal(-1) < numeric_t_star < Decimal("-0.333333333333333333333333333333"), "selected chamber isolation", passed)
    require(Decimal("0.5") < numeric_t_other < Decimal(1), "other root separated by wall", passed)
    require(numeric["-4"] > numeric["-2"] > numeric["2"] > 0, "strict factor order", passed)
    require(Decimal(alg_decimal(curvature, 40)) > 0, "positive curvature", passed)

    # The full spacetime determinant cannot use the zero-mode coordinate uniformly.
    # Sum r_lambda(t)^2 = 3-4t+6t^2, so its large-x derivative vanishes at 1/3.
    large_mode_root = Fraction(1, 3)
    require(-2 + 6 * large_mode_root == 0, "large-mode root", passed)
    require(3 * large_mode_root**2 - large_mode_root - 1 != 0, "large-mode obstruction", passed)
    require(asub(ascale(6, t_star), (Fraction(2), Fraction(0))) != ZERO_A, "selected root not large-mode root", passed)

    require(packet["KO6_polarization"]["dimensions"] == {"plus": 48, "minus": 48}, "packet chiral dimensions", passed)
    require(not packet["KO6_polarization"]["KO_chirality_used_as_statistics"], "chirality/statistics separation", passed)
    require(packet["chiral_finite_operator"]["response_branch_multiplicities"] == chiral_ranks, "packet chiral ranks", passed)
    require(packet["chiral_finite_operator"]["determinant_identity"] == "det(B^*B)=Delta(t)^32", "packet determinant identity", passed)
    require(packet["chiral_finite_operator"]["exact_rational_samples"] == determinant_records, "packet determinant samples", passed)
    require(packet["finite_Grassmann_Gaussian"]["normalized_effective_profile"] == "W0(t)=-(1/48)log det(B^*B)=-(2/3)log|Delta(t)|", "packet Gaussian profile", passed)
    require(not packet["finite_Grassmann_Gaussian"]["full_4D_determinant_claimed"], "finite determinant boundary", passed)
    require(packet["neutral_invertible_chamber"]["connected_component"] == "(-1,1/2)", "packet neutral chamber", passed)
    require(packet["neutral_invertible_chamber"]["singular_walls"] == ["-1", "1/2", "1"], "packet singular walls", passed)
    require(packet["selected_coordinate"]["exact_coefficients"] == alg_payload(t_star), "packet coordinate", passed)
    require(packet["selected_coordinate"]["Delta_at_selected_coordinate"]["exact_coefficients"] == alg_payload(delta_star), "packet Delta value", passed)
    require(packet["selected_coordinate"]["curvature"]["exact_coefficients"] == alg_payload(curvature), "packet curvature", passed)
    for label, value in sigma.items():
        branch = packet["dimensionless_branch_values"]["ordered_by_response_eigenvalue"][label]
        require(branch["exact_coefficients"] == alg_payload(value), f"packet branch {label}", passed)
        require(branch["square_exact_coefficients"] == alg_payload(sigma_squares[label]), f"packet branch square {label}", passed)
    for label, value in ratios.items():
        require(packet["dimensionless_branch_values"]["ratios"][label]["exact_coefficients"] == alg_payload(value), f"packet ratio {label}", passed)
    require(not packet["dimensionless_branch_values"]["observed_values_used"], "no observed values", passed)
    require(not packet["dimensionless_branch_values"]["fitted_coefficients_used"], "no fit", passed)
    require(packet["conditional_one_scale_values"]["inherited_common_scale_count"] == 1, "one conditional scale", passed)
    require(not packet["conditional_one_scale_values"]["common_scale_h_selected_numerically"], "scale remains unselected", passed)
    require(not packet["external_mode_obstruction"]["common_stationary_coordinate_for_all_external_modes"], "packet external-mode obstruction", passed)
    require(not packet["external_mode_obstruction"]["finite_selected_coordinate_is_final_4D_vacuum"], "not final vacuum", passed)
    require(packet["parameter_ledger"] == {
        "new_observed_construction_inputs": 0,
        "new_fitted_coefficients": 0,
        "new_dimensionless_continuous_parameters": 0,
        "new_dimensionful_primitives": 0,
        "inherited_optional_common_scale_h": 1,
        "external_spectral_measure_parameters_selected": 0,
    }, "parameter ledger", passed)
    require(packet["physical_boundary"]["finite_KO6_chiral_determinant_profile_closed"], "finite determinant closed", passed)
    require(packet["physical_boundary"]["neutral_chamber_coordinate_closed"], "finite coordinate closed", passed)
    require(packet["physical_boundary"]["exact_dimensionless_branch_values_closed"], "finite values closed", passed)
    require(not packet["physical_boundary"]["full_four_dimensional_determinant_closed"], "4D determinant open", passed)
    require(not packet["physical_boundary"]["renormalized_QFT_vacuum_closed"], "QFT vacuum open", passed)
    require(not packet["physical_boundary"]["overall_SI_scale_closed"], "SI scale open", passed)
    require(not packet["physical_boundary"]["SM_mass_generation_map_closed"], "SM map open", passed)
    require(not packet["physical_boundary"]["held_out_physical_observable_emitted"], "observable open", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "physical packets", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "physical rows", passed)

    root_payload: dict[str, Any] = {
        "schema": "boe.mtt.ko6-fermionic-determinant-value-selection-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "D0_sha256": matrix_digest(d0),
        "D1_sha256": matrix_digest(d1),
        "H_phys_sha256": matrix_digest(h_phys),
        "Gamma96_sha256": matrix_digest(gamma),
        "chiral_dimensions": {"minus": 48, "plus": 48},
        "chiral_branch_multiplicities": {"-4": 16, "-2": 16, "2": 16},
        "determinant_identity": "det(B^*B)=((1-2t)(1-t)(1+t))^32",
        "finite_Gaussian_profile": "W0=-(2/3)log|Delta(t)|",
        "selected_coordinate": "(1-sqrt(13))/6",
        "isolating_interval": ["-1/2", "-1/3"],
        "full_four_dimensional_vacuum": None,
        "observed_targets": [],
        "theorem_sha256": sha256(THEOREM_PATH),
    }
    root_hash = hashlib.sha256(json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    require(root_payload == packet["source_provenance"]["source_root_payload"], "source-root payload", passed)
    require(root_hash == packet["source_provenance"]["source_root_sha256"], "source-root digest", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary", passed)

    print(f"CBF.T30 independent verification passed: {len(passed)}/{len(passed)} checks")


if __name__ == "__main__":
    main()
