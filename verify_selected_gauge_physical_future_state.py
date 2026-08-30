#!/usr/bin/env python3
"""Independent verifier for the exact CBF.T47 packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "selected_gauge_physical_future_state.packet.json"
SOURCE_LOCK = ROOT / "selected_gauge_physical_future_state_source_lock.json"
SCHEMA = ROOT / "selected_gauge_physical_future_state_contract.schema.json"
THEOREM = ROOT / "SelectedGaugePhysicalFutureStateBRSTAndZeroModeTheorem_v1.md"

Matrix = list[list[Fraction]]
Vector = list[Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_matrix(payload: list[list[str]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in payload]


def parse_vector(payload: list[str]) -> Vector:
    return [Fraction(value) for value in payload]


def zero(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zero(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def diagonal(values: list[Fraction]) -> Matrix:
    result = zero(len(values), len(values))
    for index, value in enumerate(values):
        result[index][index] = value
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[a - b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def scale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum((entry * component for entry, component in zip(row, vector)), Fraction(0)) for row in matrix]


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column] != 0), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [value - factor * pivot_value for value, pivot_value in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def verify_brst(label: str, payload: dict[str, Any], expected_physical: int, checks: dict[str, bool]) -> None:
    charge = parse_matrix(payload["Q0"])
    homotopy = parse_matrix(payload["homotopy"])
    physical = parse_matrix(payload["physical_projector"])
    krein = parse_matrix(payload["Krein_form"])
    closed_gram = parse_matrix(payload["closed_ghost_zero_Gram"])
    size = expected_physical + 4
    checks[f"{label}_dimension"] = len(charge) == size and all(len(row) == size for row in charge)
    checks[f"{label}_nilpotent"] = multiply(charge, charge) == zero(size, size)
    checks[f"{label}_rank_two"] = rank(charge) == 2
    checks[f"{label}_Krein_hermitian"] = multiply(transpose(charge), krein) == multiply(krein, charge)
    checks[f"{label}_projector_idempotent"] = multiply(physical, physical) == physical
    checks[f"{label}_projector_rank"] = rank(physical) == expected_physical
    checks[f"{label}_contraction"] = add(multiply(charge, homotopy), multiply(homotopy, charge)) == subtract(identity(size), physical)
    expected_gram = diagonal([Fraction(1)] * expected_physical + [Fraction(0)])
    checks[f"{label}_closed_Gram"] = closed_gram == expected_gram
    checks[f"{label}_cohomology_dimension"] = payload["physical_cohomology_dimension"] == expected_physical


def main() -> None:
    packet = load(PACKET)
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    checks: dict[str, bool] = {}

    checks["packet_claim"] = packet["claim_id"] == "CBF.T47"
    checks["packet_schema"] = packet["schema"] == "boe.mtt.selected-gauge-physical-future-state.v1"
    checks["lock_claim"] = source_lock["claim_id"] == "CBF.T47"
    checks["schema_claim"] = schema["properties"]["claim_id"]["const"] == "CBF.T47"
    checks["date"] = packet["date"] == "2026-08-30"
    checks["theorem_exists"] = THEOREM.is_file()
    checks["source_lock_digest"] = packet["source_provenance"]["source_lock_sha256"] == digest(SOURCE_LOCK)
    checks["schema_digest"] = packet["source_provenance"]["contract_sha256"] == digest(SCHEMA)
    checks["handoff_id"] = packet["source_provenance"]["handoff_id"] == "f223a622-f094-44bb-8825-633f8c2cf51f"
    checks["kernel_hash"] = packet["source_provenance"]["kernel_model_sha256"] == "592ef16dc03ce2195113b53cc75f8bb638bd27c279590ed3f5575d11dee05db8"
    checks["contract_keys"] = set(schema["required"]).issubset(packet)

    for category in ("construction_sources", "comparison_sources"):
        for index, source in enumerate(source_lock[category], start=1):
            path = (ROOT / source["path"]).resolve()
            checks[f"{category}_{index:02d}_exists"] = path.is_file()
            checks[f"{category}_{index:02d}_digest"] = path.is_file() and digest(path) == source["sha256"]

    mass = packet["generalized_mass_witness"]
    kinetic = parse_matrix(mass["kinetic_trace_metric"])
    mass_form = parse_matrix(mass["mass_form_up_to_common_positive_H_squared_factor"])
    mass_operator = parse_matrix(mass["generalized_mass_operator"])
    broken = parse_matrix(mass["broken_projector"])
    unbroken = parse_matrix(mass["unbroken_projector"])
    photon = parse_vector(mass["photon_vector"])
    z_vector = parse_vector(mass["Z_vector"])
    kinetic_inverse = diagonal([Fraction(1, 6)] * 11 + [Fraction(1, 10)])

    checks["kinetic_exact_diagonal"] = kinetic == diagonal([Fraction(6)] * 11 + [Fraction(10)])
    checks["mass_form_rank"] = rank(mass_form) == 3
    checks["generalized_operator_recomputed"] = mass_operator == multiply(kinetic_inverse, mass_form)
    checks["generalized_operator_K_self_adjoint"] = multiply(transpose(mass_operator), kinetic) == multiply(kinetic, mass_operator)
    checks["broken_projector_idempotent"] = multiply(broken, broken) == broken
    checks["broken_projector_rank"] = rank(broken) == 3 and trace(broken) == 3
    checks["broken_projector_K_self_adjoint"] = multiply(transpose(broken), kinetic) == multiply(kinetic, broken)
    checks["unbroken_projector_idempotent"] = multiply(unbroken, unbroken) == unbroken
    checks["unbroken_projector_rank"] = rank(unbroken) == 9 and trace(unbroken) == 9
    checks["projectors_complementary"] = add(broken, unbroken) == identity(12) and multiply(broken, unbroken) == zero(12, 12)
    checks["photon_kernel"] = matvec(mass_operator, photon) == [Fraction(0)] * 12
    checks["Z_eigenvalue"] = matvec(mass_operator, z_vector) == [Fraction(4, 15) * value for value in z_vector]
    checks["photon_Z_metric_orthogonal"] = sum(
        (photon[i] * kinetic[i][j] * z_vector[j] for i in range(12) for j in range(12)),
        Fraction(0),
    ) == 0
    checks["spectrum_ledger"] = mass["generalized_spectrum"] == {"0": 9, "1/6": 2, "4/15": 1}
    checks["absolute_mass_not_claimed"] = mass["absolute_common_mass_factor_selected"] is False

    brst = packet["BRST_mode_reduction"]
    verify_brst("massless", brst["massless_complex"], 2, checks)
    verify_brst("massive", brst["massive_complex"], 3, checks)
    checks["unbroken_count"] = brst["unbroken_generators"] == 9
    checks["broken_count"] = brst["broken_generators"] == 3
    checks["massless_physical_count"] = brst["massless_physical_polarizations"] == 18
    checks["massive_physical_count"] = brst["massive_physical_polarizations"] == 9
    checks["total_gauge_count"] = brst["total_physical_gauge_polarizations"] == 27
    checks["positive_quotient"] = brst["positive_ghost_zero_quotient"] is True
    checks["Goldstones_not_double_counted"] = brst["Goldstone_directions_counted_as_independent_Higgs_particles"] is False

    mixing = brst["broken_longitudinal_Goldstone_mixing"]
    rotation = parse_matrix(mixing["mixing_matrix_rows_x_ell"])
    gauge_orbit = parse_vector(mixing["gauge_orbit_input"])
    physical_longitudinal = parse_vector(mixing["physical_longitudinal_input"])
    zero_rotation = parse_matrix(mixing["zero_momentum_m_positive_matrix"])
    checks["mixing_orthogonal"] = multiply(rotation, transpose(rotation)) == identity(2)
    checks["orbit_maps_to_x"] = matvec(rotation, gauge_orbit) == [Fraction(5), Fraction(0)]
    checks["longitudinal_maps_to_ell"] = matvec(rotation, physical_longitudinal) == [Fraction(0), Fraction(5)]
    checks["massive_p_zero_regular"] = multiply(zero_rotation, transpose(zero_rotation)) == identity(2)

    ir = packet["massless_IR_zero_mode"]
    checks["IR_dimension"] = ir["spatial_dimension"] == 3
    checks["IR_radial_power"] = ir["radial_covariance_integrand_power"] == 1
    checks["IR_zero_projection"] = ir["zero_spectral_projection_on_L2_R3"] == 0
    checks["IR_p_zero_value_irrelevant"] = ir["value_of_projector_at_p_zero_affects_distribution"] is False
    checks["compact_harmonic_scope_open"] = ir["compact_Cauchy_harmonic_modes_covered"] is False
    for index, sample in enumerate(ir["samples"], start=1):
        momentum = parse_vector(sample["momentum"])
        projector = parse_matrix(sample["projector"])
        norm_squared = sum((value * value for value in momentum), Fraction(0))
        expected = [
            [
                (Fraction(1) if i == j else Fraction(0)) - momentum[i] * momentum[j] / norm_squared
                for j in range(3)
            ]
            for i in range(3)
        ]
        checks[f"IR_sample_{index}_formula"] = projector == expected
        checks[f"IR_sample_{index}_symmetric"] = transpose(projector) == projector
        checks[f"IR_sample_{index}_idempotent"] = multiply(projector, projector) == projector
        checks[f"IR_sample_{index}_rank"] = rank(projector) == 2
        checks[f"IR_sample_{index}_transverse"] = matvec(projector, momentum) == [Fraction(0)] * 3

    oscillator = packet["oscillator_witness"]
    symplectic = parse_matrix(oscillator["symplectic_form"])
    future_j = parse_matrix(oscillator["future_complex_structure"])
    future_metric = parse_matrix(oscillator["positive_metric_SJ"])
    past_metric = parse_matrix(oscillator["past_metric_minus_SJ"])
    checks["oscillator_J_squared"] = multiply(future_j, future_j) == scale(Fraction(-1), identity(2))
    checks["oscillator_symplectic"] = multiply(multiply(transpose(future_j), symplectic), future_j) == symplectic
    checks["oscillator_future_positive"] = future_metric == diagonal([Fraction(5), Fraction(1, 5)])
    checks["oscillator_past_negative"] = past_metric == diagonal([Fraction(-5), Fraction(-1, 5)])

    state = packet["future_positive_CCR_state"]
    checks["state_positive"] = state["positive"] is True
    checks["state_normalized"] = state["normalized"] is True
    checks["state_pure"] = state["pure"] is True
    checks["state_Hadamard"] = state["Hadamard_on_static_flat_branch"] is True
    checks["state_BRST_descended"] = state["BRST_descended"] is True
    checks["state_no_new_selector"] = state["new_state_parameter_count"] == 0
    checks["state_scale_boundary"] = state["depends_on_inherited_absolute_action_scale"] is True

    factorization = packet["broken_phase_seed_factorization"]
    checks["Weyl_selected"] = factorization["Weyl_factor"]["selected"] is True
    checks["gauge_selected"] = factorization["gauge_physical_factor"]["selected"] is True
    checks["gauge_rank_27"] = factorization["gauge_physical_factor"]["physical_polarizations"] == 27
    checks["radial_Higgs_open"] = factorization["radial_Higgs_factor"]["selected"] is False
    checks["radial_Higgs_rank_1"] = factorization["radial_Higgs_factor"]["physical_polarizations"] == 1
    checks["one_factor_missing"] = factorization["missing_selected_factors"] == 1
    checks["full_seed_open"] = factorization["full_product_seed_selected"] is False

    ledger = packet["G2_clause_ledger"]
    checks["gauge_clause_closed"] = ledger["G2a_flat_branch_free_gauge_physical_state"] == "closed by T47"
    checks["radial_clause_open"] = ledger["G2a_flat_branch_free_radial_Higgs_state"] == "open"
    checks["complete_seed_open"] = ledger["G2b_selected_complete_free_product_seed"] == "open by one radial Higgs factor"
    checks["continuum_open"] = ledger["G2c_selected_regulator_independent_continuum"] == "open 0/9"
    checks["top_G2_open"] = ledger["top_level_physical_G2"] == "open"
    checks["physical_gate_count"] = ledger["physical_T41_gate_count"] == "0/3"

    parameters = packet["parameter_ledger"]
    checks["no_observed_inputs"] = parameters["new_observed_inputs"] == 0
    checks["no_fits"] = parameters["new_fitted_parameters"] == 0
    checks["no_state_selectors"] = parameters["new_continuous_state_selectors"] == 0 and parameters["new_discrete_state_selectors"] == 0
    checks["unresolved_H_recorded"] = parameters["inherited_unresolved_radial_scale"] == "H>0"
    checks["unresolved_gauge_scale_recorded"] = parameters["inherited_unresolved_common_gauge_action_scale"] == "c_G>0"

    boundary = packet["physical_boundary"]
    checks["physical_packets_unchanged"] = boundary["physical_packets_accepted"] == 0 and boundary["physical_packets_total"] == 3
    checks["physical_rows_unchanged"] = boundary["physical_rows_accepted"] == 0 and boundary["physical_rows_total"] == 7
    checks["radial_exit_named"] = any("radial Higgs" in item for item in boundary["open"])
    checks["absolute_normalization_exit_named"] = any("absolute gauge" in item for item in boundary["open"])
    checks["all_builder_checks_true"] = all(packet["checks"].values())
    checks["builder_summary_consistent"] = packet["check_summary"]["failed"] == [] and packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(packet["checks"])

    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise SystemExit("CBF.T47 independent verification failed: " + ", ".join(failed))
    print(f"CBF.T47 independent verification passed {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
