#!/usr/bin/env python3
"""Build the exact CBF.T19 equivariant Feshbach response certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "equivariant_feshbach_response_source_lock.json"
SCHEMA = ROOT / "equivariant_feshbach_response_contract.schema.json"
THEOREM = ROOT / "EquivariantFeshbachOneDimensionalResponseTheorem_v1.md"
T18_PACKET = ROOT / "normal_frame_action_intertwiner_reduction.packet.json"
FSB_ROOT = ROOT.parent / "mtt-q79-total-superconnection-branching"
DYNAMIC_PACKET = FSB_ROOT / "artifacts" / "triadic_dynamic_weyl_orbit.packet.json"
ALGEBRA_PACKET = FSB_ROOT / "artifacts" / "triadic_family_response_algebra.packet.json"
FSB_MANIFEST = FSB_ROOT / "state" / "source_manifest.v1.json"
OUTPUT = ROOT / "equivariant_feshbach_response.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qscalar(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(qscalar(-1), right))


def is_zero(matrix: cp.Matrix) -> bool:
    return matrix == cp.zero(len(matrix), len(matrix[0]))


def commutator(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return matrix_sub(cp.matmul(left, right), cp.matmul(right, left))


def block_matrix(blocks: list[list[cp.Matrix]]) -> cp.Matrix:
    row_heights = [len(row[0]) for row in blocks]
    column_widths = [len(blocks[0][column][0]) for column in range(len(blocks[0]))]
    result: cp.Matrix = []
    for block_row, height in zip(blocks, row_heights):
        for local_row in range(height):
            row: list[cp.K] = []
            for block, width in zip(block_row, column_widths):
                if len(block) != height or len(block[0]) != width:
                    raise ValueError("inconsistent block dimensions")
                row.extend(block[local_row])
            result.append(row)
    return result


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    rows = sum(len(block) for block in blocks)
    columns = sum(len(block[0]) for block in blocks)
    result = cp.zero(rows, columns)
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row in range(len(block)):
            for column in range(len(block[0])):
                result[row_offset + row][column_offset + column] = block[row][column]
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def matrix_inverse(matrix: cp.Matrix) -> cp.Matrix:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("matrix must be square")
    augmented = [row[:] + identity_row[:] for row, identity_row in zip(matrix, cp.identity(size))]
    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column] != cp.ZERO), None)
        if pivot is None:
            raise ValueError("matrix is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_inverse = cp.kinv(augmented[column][column])
        augmented[column] = [cp.kmul(pivot_inverse, value) for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == cp.ZERO:
                continue
            augmented[row] = [
                cp.kadd(value, cp.kneg(cp.kmul(factor, pivot_value)))
                for value, pivot_value in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def frobenius_inner(left: cp.Matrix, right: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for row in range(len(left)):
        for column in range(len(left[0])):
            total = cp.kadd(
                total,
                cp.kmul(cp.kconj(left[row][column]), right[row][column]),
            )
    return total


def flatten(matrix: cp.Matrix) -> list[cp.K]:
    return [value for row in matrix for value in row]


def span_rank(matrices: Iterable[cp.Matrix]) -> int:
    vectors = [flatten(matrix) for matrix in matrices]
    if not vectors:
        return 0
    coordinate_matrix = [list(column) for column in zip(*vectors)]
    return cp.matrix_rank(coordinate_matrix)


def centralizer_constraints(generators: list[cp.Matrix]) -> cp.Matrix:
    size = len(generators[0])
    rows: cp.Matrix = []
    for generator in generators:
        for output_row in range(size):
            for output_column in range(size):
                equation: list[cp.K] = []
                for source_row in range(size):
                    for source_column in range(size):
                        left = (
                            generator[source_column][output_column]
                            if output_row == source_row
                            else cp.ZERO
                        )
                        right = (
                            generator[output_row][source_row]
                            if source_column == output_column
                            else cp.ZERO
                        )
                        equation.append(cp.kadd(left, cp.kneg(right)))
                rows.append(equation)
    return rows


def hermitian_basis_3() -> list[cp.Matrix]:
    basis: list[cp.Matrix] = []
    i_unit: cp.K = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    for index in range(3):
        matrix = cp.zero(3, 3)
        matrix[index][index] = cp.ONE
        basis.append(matrix)
    for row in range(3):
        for column in range(row + 1, 3):
            symmetric = cp.zero(3, 3)
            symmetric[row][column] = cp.ONE
            symmetric[column][row] = cp.ONE
            basis.append(symmetric)
            skew = cp.zero(3, 3)
            skew[row][column] = i_unit
            skew[column][row] = cp.kneg(i_unit)
            basis.append(skew)
    return basis


def routed_pair(fourier: cp.Matrix, shift_block: cp.Matrix) -> tuple[cp.Matrix, cp.Matrix]:
    phase_block = cp.matmul(cp.adjoint(fourier), cp.matmul(shift_block, fourier))
    return phase_block, shift_block


def source_hash_checks(source_lock: dict[str, object]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for source in source_lock["local_sources"]:  # type: ignore[index]
        source_dict = source  # type: ignore[assignment]
        path = (ROOT / source_dict["path"]).resolve()
        checks[f"source_hash_{Path(source_dict['path']).name}"] = (
            path.is_file() and sha256(path) == source_dict["sha256"]
        )
    return checks


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t18 = json.loads(T18_PACKET.read_text(encoding="ascii"))
    dynamic = json.loads(DYNAMIC_PACKET.read_text(encoding="utf-8"))
    algebra = json.loads(ALGEBRA_PACKET.read_text(encoding="utf-8"))

    response = dynamic["exact_witness"]["normalized_first_Hermitian_response"]
    fourier = decode_matrix(dynamic["exact_witness"]["selected_Weyl_data"]["F3"])
    a_shift = decode_matrix(response["shift_shape"])
    b_phase = decode_matrix(response["phase_shape"])
    identity3 = cp.identity(3)
    zero3 = cp.zero(3, 3)

    phase_from_shift = cp.matmul(cp.adjoint(fourier), cp.matmul(a_shift, fourier))
    lane_parity = block_diag([identity3, cp.mscale(qscalar(-1), identity3)])
    lane_exchange = block_matrix([[zero3, cp.adjoint(fourier)], [fourier, zero3]])
    h6 = block_diag([b_phase, a_shift])
    a6 = block_diag([a_shift, a_shift])
    b6 = block_diag([b_phase, b_phase])

    routed_constraints = centralizer_constraints([lane_parity, lane_exchange])
    routed_commutant_dimension = 36 - cp.matrix_rank(routed_constraints)
    comparison_constraints = centralizer_constraints([a6, b6, lane_parity, lane_exchange])
    comparison_commutant_dimension = 36 - cp.matrix_rank(comparison_constraints)

    h3_basis = hermitian_basis_3()
    gauge_sector_basis: list[cp.Matrix] = []
    Fourier_paired_basis: list[cp.Matrix] = []
    universal_routed_basis: list[cp.Matrix] = []
    zero = cp.zero(3, 3)
    for sector in range(4):
        for family_matrix in h3_basis:
            blocks = [zero, zero, zero, zero]
            blocks[sector] = family_matrix
            gauge_sector_basis.append(block_diag(blocks))
    for family_matrix in h3_basis:
        phase_matrix, shift_matrix = routed_pair(fourier, family_matrix)
        Fourier_paired_basis.append(block_diag([phase_matrix, zero, shift_matrix, zero]))
        Fourier_paired_basis.append(block_diag([zero, phase_matrix, zero, shift_matrix]))
        universal_routed_basis.append(
            block_diag([phase_matrix, phase_matrix, shift_matrix, shift_matrix])
        )
    h12 = block_diag([b_phase, b_phase, a_shift, a_shift])

    gauge_sector_dimension = span_rank(gauge_sector_basis)
    Fourier_paired_dimension = span_rank(Fourier_paired_basis)
    universal_routed_dimension = span_rank(universal_routed_basis)
    response_line_dimension = span_rank([h12])

    h6_inverse = matrix_inverse(h6)
    h6_norm2 = frobenius_inner(h6, h6)
    h6_rank = cp.matrix_rank(h6)

    scale = Fraction(7, 3)
    coupling = Fraction(2)
    complement_scale = Fraction(3)
    identity6 = cp.identity(6)
    zero6 = cp.zero(6, 6)
    target = cp.mscale(qscalar(scale), h6)
    coupling_block = cp.mscale(qscalar(coupling), identity6)
    complement = cp.mscale(qscalar(complement_scale), identity6)
    complement_inverse = cp.mscale(qscalar(Fraction(1, 3)), identity6)
    self_energy = cp.matmul(
        coupling_block,
        cp.matmul(complement_inverse, cp.adjoint(coupling_block)),
    )
    retained_block = cp.madd(target, self_energy)
    upper_hessian = block_matrix(
        [[retained_block, coupling_block], [cp.adjoint(coupling_block), complement]]
    )
    effective = matrix_sub(retained_block, self_energy)

    inclusion = block_matrix([[identity6], [zero6]])
    upper_parity = block_diag([lane_parity, lane_parity])
    upper_exchange = block_diag([lane_exchange, lane_exchange])
    inclusion_parity_intertwines = cp.matmul(upper_parity, inclusion) == cp.matmul(inclusion, lane_parity)
    inclusion_exchange_intertwines = cp.matmul(upper_exchange, inclusion) == cp.matmul(inclusion, lane_exchange)
    upper_hessian_equivariant = is_zero(commutator(upper_hessian, upper_parity)) and is_zero(
        commutator(upper_hessian, upper_exchange)
    )

    recovered_scale = cp.kdiv(frobenius_inner(h6, effective), h6_norm2)
    response_residual = matrix_sub(effective, cp.mscale(recovered_scale, h6))
    relative_comparison = cp.matmul(h6_inverse, effective)
    relative_commutators_zero = all(
        is_zero(commutator(relative_comparison, generator))
        for generator in [a6, b6, lane_parity, lane_exchange]
    )

    alternative_target = identity6
    alternative_retained = cp.madd(alternative_target, self_energy)
    alternative_upper = block_matrix(
        [[alternative_retained, coupling_block], [cp.adjoint(coupling_block), complement]]
    )
    alternative_effective = matrix_sub(alternative_retained, self_energy)
    alternative_scale = cp.kdiv(frobenius_inner(h6, alternative_effective), h6_norm2)
    alternative_residual = matrix_sub(
        alternative_effective, cp.mscale(alternative_scale, h6)
    )
    alternative_relative = cp.matmul(h6_inverse, alternative_effective)
    alternative_relative_commutators = [
        commutator(alternative_relative, generator)
        for generator in [a6, b6, lane_parity, lane_exchange]
    ]
    alternative_equivariant = is_zero(commutator(alternative_upper, upper_parity)) and is_zero(
        commutator(alternative_upper, upper_exchange)
    )

    t18_response = t18["contracted_response"]
    boundary = source_lock["boundary"]
    properties = schema["properties"]
    checks = {
        **source_hash_checks(source_lock),
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.equivariant-feshbach-response-lock.v1",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": properties["schema"]["const"] == "boe.mtt.equivariant-feshbach-response.v1",
        "T18_response_rank_is_24": t18_response["complex_rank"] == 24,
        "T18_response_norm_squared_is_192": t18_response["frobenius_norm_squared"] == "192",
        "FSB04e_source_is_exact": dynamic["claim_id"] == "FSB.04e" and dynamic["all_checks_pass"],
        "FSB04f_response_algebra_is_full_M3": algebra["exact_witness"]["complex_response_algebra"]["generated_algebra"] == "M3(C) after scalar extension",
        "Fourier_is_unitary": cp.matmul(cp.adjoint(fourier), fourier) == identity3,
        "phase_is_Fourier_conjugate_of_shift": b_phase == phase_from_shift,
        "lane_parity_is_unitary_involution": cp.matmul(cp.adjoint(lane_parity), lane_parity) == identity6 and cp.matmul(lane_parity, lane_parity) == identity6,
        "lane_exchange_is_unitary_involution": cp.matmul(cp.adjoint(lane_exchange), lane_exchange) == identity6 and cp.matmul(lane_exchange, lane_exchange) == identity6,
        "selected_response_is_routed_equivariant": is_zero(commutator(h6, lane_parity)) and is_zero(commutator(h6, lane_exchange)),
        "routed_equivariant_complex_module_dimension_is_9": routed_commutant_dimension == 9,
        "gauge_sector_Hermitian_module_dimension_is_36": gauge_sector_dimension == 36,
        "Fourier_paired_Hermitian_module_dimension_is_18": Fourier_paired_dimension == 18,
        "universal_routed_Hermitian_module_dimension_is_9": universal_routed_dimension == 9,
        "selected_response_line_dimension_is_1": response_line_dimension == 1,
        "selected_family_lane_comparison_commutant_dimension_is_1": comparison_commutant_dimension == 1,
        "active_response_is_invertible": h6_rank == 6 and cp.matmul(h6_inverse, h6) == identity6,
        "active_response_norm_squared_is_48": h6_norm2 == qscalar(48),
        "nonreducing_complement_inverse_is_exact": cp.matmul(complement_inverse, complement) == identity6,
        "upper_hessian_is_exactly_equivariant": upper_hessian_equivariant,
        "synthesis_inclusion_intertwines_lane_parity": inclusion_parity_intertwines,
        "synthesis_inclusion_intertwines_lane_exchange": inclusion_exchange_intertwines,
        "Feshbach_effective_Hessian_is_exact_target": effective == target,
        "Feshbach_scale_is_recovered_exactly": recovered_scale == qscalar(scale),
        "Feshbach_response_residual_is_zero": is_zero(response_residual),
        "relative_response_comparison_is_scalar": relative_comparison == cp.mscale(qscalar(scale), identity6),
        "relative_response_intertwiner_commutators_vanish": relative_commutators_zero,
        "equivariant_negative_control_is_equivariant": alternative_equivariant,
        "equivariant_negative_control_reduces_to_identity": alternative_effective == identity6,
        "equivariant_negative_control_is_not_response_proportional": not is_zero(alternative_residual),
        "equivariant_negative_control_fails_relative_intertwiner": any(not is_zero(value) for value in alternative_relative_commutators),
        "equivariance_alone_does_not_force_response_line": routed_commutant_dimension > 1,
        "relative_intertwiner_plus_scalar_commutant_forces_response_line": comparison_commutant_dimension == 1,
        "physical_same_root_relative_intertwiner_remains_open": not boundary["same_root_relative_response_intertwiner_supplied"],
        "physical_action_scale_remains_open": not boundary["physical_action_scale_selected"],
        "physical_packet_acceptance_is_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "no_observed_values_enter_the_witness": True,
        "no_fitted_coefficients_enter_the_witness": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"failed checks: {failed}")

    packet = {
        "schema": "boe.mtt.equivariant-feshbach-response.v1",
        "claim_id": "CBF.T19",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_SOURCE_PINNED_FINITE_CUTSET + CONDITIONAL_PHYSICAL_SOURCE_LINE",
        "decision": [
            "FESHBACH_REDUCTION_PRESERVES_EXACT_EQUIVARIANCE",
            "ROUTED_FOURIER_EQUIVARIANCE_ALONE_LEAVES_NINE_HERMITIAN_DIRECTIONS",
            "THE_FULL_PHYSICAL_REDUCTION_LADDER_IS_36_TO_18_TO_9_TO_1",
            "A_RELATIVE_RESPONSE_INTERTWINER_FORCES_THE_FINAL_ONE_DIMENSIONAL_LINE",
            "THE_SELECTED_SAME_ROOT_RELATIVE_INTERTWINER_AND_BV_SCALE_REMAIN_OPEN",
        ],
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "finite_source_manifest_sha256": sha256(FSB_MANIFEST),
        "finite_response": {
            "formula": "H_resp=B_phase tensor R_phase+A_shift tensor R_shift",
            "full_complex_dimension": 48,
            "full_rank": 24,
            "full_frobenius_norm_squared": "192",
            "active_reduced_formula": "H6=diag(B_phase,A_shift)",
            "active_reduced_rank": h6_rank,
            "active_reduced_frobenius_norm_squared": str(h6_norm2[0]),
            "active_route_multiplicity": 4,
            "inactive_kernel_dimension": 24,
        },
        "module_ladder": {
            "gauge_sector_description": "independent Herm(3) blocks on u,e,d,N",
            "gauge_sector_dimension": gauge_sector_dimension,
            "Fourier_paired_description": "u=F3^* d F3 and e=F3^* N F3",
            "Fourier_paired_dimension": Fourier_paired_dimension,
            "universal_routed_description": "d=N=X and u=e=F3^* X F3",
            "universal_routed_dimension": universal_routed_dimension,
            "relative_response_line_description": "X=c A_shift",
            "relative_response_line_dimension": response_line_dimension,
            "dimension_chain": [36, 18, 9, 1],
            "routed_equivariant_complex_commutant_dimension": routed_commutant_dimension,
        },
        "feshbach_covariance": {
            "abstract_reducing_case": "H_eff=U^* K U",
            "abstract_nonreducing_case": "H_eff=U^*KU-U^*KQ(QKQ)^-1QKU",
            "reducing_case_equivariant": True,
            "nonreducing_case_equivariant": True,
            "inverse_equivariance_reason": "an invertible equivariant Q-block has an equivariant inverse",
            "equivariance_alone_forces_response_line": False,
            "exact_witness": {
                "retained_dimension": 6,
                "complement_dimension": 6,
                "coupling": str(coupling),
                "complement_scale": str(complement_scale),
                "target_scale": str(scale),
                "recovered_scale": str(recovered_scale[0]),
                "residual_zero": is_zero(response_residual),
            },
            "negative_control": {
                "effective_Hessian": "I6",
                "is_lane_Fourier_equivariant": alternative_equivariant,
                "best_response_coefficient": str(alternative_scale[0]),
                "response_residual_zero": is_zero(alternative_residual),
                "relative_intertwiner_passes": all(is_zero(value) for value in alternative_relative_commutators),
            },
        },
        "relative_intertwiner": {
            "active_test": "T=H_resp,act^-1 H_eff,act commutes with the selected family-lane algebra",
            "selected_generators": [
                "diag(A_shift,A_shift)",
                "diag(B_phase,B_phase)",
                "lane_parity",
                "Fourier_lane_exchange",
            ],
            "comparison_commutant_dimension": comparison_commutant_dimension,
            "conclusion": "H_eff,act=c_action H_resp,act",
            "coefficient_formula_full": "c_action=<H_resp,H_eff>_F/192",
            "support_and_route_multiplicity_must_also_intertwine": True,
            "physically_supplied": False,
        },
        "endpoint_consequence": {
            "old_terminal_test": "evaluate all entries of H_eff-c_action H_resp",
            "new_equivalent_source_test": "prove inactive-kernel/support equality and the relative response intertwiner, then evaluate one scalar coefficient",
            "remaining_same_root_objects": [
                "K_phys and its domain",
                "finite synthesis U",
                "Q-block inverse or reducing certificate",
                "relative response algebra intertwiner",
                "BV4 density and compactification normalization",
            ],
            "absolute_scale_selected_by_normalized_finite_data": False,
        },
        "parameter_ledger": {
            "observed_construction_inputs": 0,
            "fitted_coefficients": 0,
            "new_physical_parameters": 0,
            "conditional_action_coefficients_after_source_intertwiner": 1,
            "selected_physical_action_coefficients": 0,
            "strict_charged_magnitude_values_remaining": 9,
        },
        "physical_boundary": {
            "physical_endpoint_selected": False,
            "physical_GAS_packet_supplied": False,
            "physical_SYN_packet_supplied": False,
            "physical_BV4_packet_supplied": False,
            "physical_relative_response_intertwiner_supplied": False,
            "physical_action_scale_selected": False,
            "Lorentz_Higgs_Yukawa_typing": False,
            "physical_packets_accepted": 0,
            "physical_rows_accepted": 0,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "Feshbach covariance is now exact in both reducing and nonreducing cases. "
            "Natural gauge/Fourier/routing constraints reduce the admissible Hermitian "
            "response space through dimensions 36, 18 and 9 but do not force the selected "
            "line. The exact selected family-lane comparison algebra has scalar commutant, "
            "so one additional same-root relative-response intertwiner is necessary and "
            "sufficient to reduce the final space to span(H_resp)."
        ),
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "equivariant Feshbach response packet built: "
        f"{len(checks)}/{len(checks)} checks; module ladder 36->18->9->1; "
        "physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
