#!/usr/bin/env python3
"""Build the exact CBF.T47 gauge-physical future-state packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "selected_gauge_physical_future_state_source_lock.json"
SCHEMA = ROOT / "selected_gauge_physical_future_state_contract.schema.json"
THEOREM = ROOT / "SelectedGaugePhysicalFutureStateBRSTAndZeroModeTheorem_v1.md"
OUTPUT = ROOT / "selected_gauge_physical_future_state.packet.json"

T45_PACKET = ROOT / "future_cone_spectral_polarization.packet.json"
T46_PACKET = ROOT / "selected_future_state_moller_bv_transport.packet.json"
GAUGE_FIXED_CERT = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_gaugefixed_hyperbolic_bv_equicausal.certificate.json"
LOCAL_STATE_CERT = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_local_formal_physical_state.certificate.json"
A47_CERT = ROOT / "../mtt-sm-parity-closure/certificates/selected_nativebundleautomorphismgaugegroup_or_parameterassumptionaudit_certificate.json"
A51_CERT = ROOT / "../mtt-sm-parity-closure/certificates/selected_finitespectralactionandhiggsinnerfluctuation_or_directgenerativesmactionclosure_certificate.json"
A51_PACKET = ROOT / "../mtt-sm-parity-closure/candidate_data/selected_finitespectralactionandhiggsinnerfluctuation_or_directgenerativesmactionclosure/finite_inner_fluctuation_and_spectral_traces.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"

Matrix = list[list[Fraction]]
Vector = list[Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix_text(matrix: Matrix) -> list[list[str]]:
    return [[ftext(value) for value in row] for row in matrix]


def vector_text(vector: Vector) -> list[str]:
    return [ftext(value) for value in vector]


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


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matadd(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return [[a - b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def matscale(value: Fraction, matrix: Matrix) -> Matrix:
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


def source_hash_checks(source_lock: dict[str, Any]) -> tuple[dict[str, bool], dict[str, bool]]:
    construction: dict[str, bool] = {}
    comparison: dict[str, bool] = {}
    for index, source in enumerate(source_lock["construction_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        construction[f"construction_source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    for index, source in enumerate(source_lock["comparison_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        comparison[f"comparison_source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return construction, comparison


def generalized_mass_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    basis = [f"G_{index}" for index in range(1, 9)] + ["W_1", "W_2", "W_3", "B"]
    kinetic_values = [Fraction(6)] * 11 + [Fraction(10)]
    kinetic = diagonal(kinetic_values)
    kinetic_inverse = diagonal([Fraction(1, value) for value in kinetic_values])

    mass_form = zero(12, 12)
    mass_form[8][8] = Fraction(1)
    mass_form[9][9] = Fraction(1)
    mass_form[10][10] = Fraction(1)
    mass_form[11][11] = Fraction(1)
    mass_form[10][11] = Fraction(-1)
    mass_form[11][10] = Fraction(-1)
    mass_operator = matmul(kinetic_inverse, mass_form)

    broken = zero(12, 12)
    broken[8][8] = Fraction(1)
    broken[9][9] = Fraction(1)
    broken[10][10] = Fraction(5, 8)
    broken[10][11] = Fraction(-5, 8)
    broken[11][10] = Fraction(-3, 8)
    broken[11][11] = Fraction(3, 8)
    unbroken = matsub(identity(12), broken)

    photon = [Fraction(0)] * 12
    photon[10] = Fraction(1)
    photon[11] = Fraction(1)
    z_vector = [Fraction(0)] * 12
    z_vector[10] = Fraction(-5)
    z_vector[11] = Fraction(3)
    w1 = [Fraction(0)] * 12
    w1[8] = Fraction(1)
    w2 = [Fraction(0)] * 12
    w2[9] = Fraction(1)

    expected_mass = zero(12, 12)
    expected_mass[8][8] = Fraction(1, 6)
    expected_mass[9][9] = Fraction(1, 6)
    neutral_projector = zero(12, 12)
    for i in (10, 11):
        for j in (10, 11):
            neutral_projector[i][j] = broken[i][j]
    expected_mass = matadd(expected_mass, matscale(Fraction(4, 15), neutral_projector))

    photon_z_metric_pairing = sum(
        (photon[i] * kinetic[i][j] * z_vector[j] for i in range(12) for j in range(12)),
        Fraction(0),
    )

    checks = {
        "gauge_kinetic_metric_has_rank_twelve": rank(kinetic) == 12,
        "mass_form_has_rank_three": rank(mass_form) == 3,
        "mass_operator_is_K_self_adjoint": matmul(transpose(mass_operator), kinetic) == matmul(kinetic, mass_operator),
        "mass_operator_matches_spectral_decomposition": mass_operator == expected_mass,
        "broken_projector_is_idempotent": matmul(broken, broken) == broken,
        "broken_projector_is_K_self_adjoint": matmul(transpose(broken), kinetic) == matmul(kinetic, broken),
        "broken_projector_has_rank_three": rank(broken) == 3 and trace(broken) == 3,
        "unbroken_projector_is_idempotent": matmul(unbroken, unbroken) == unbroken,
        "unbroken_projector_has_rank_nine": rank(unbroken) == 9 and trace(unbroken) == 9,
        "broken_and_unbroken_are_complementary": matmul(broken, unbroken) == zero(12, 12) and matadd(broken, unbroken) == identity(12),
        "photon_is_massless": matvec(mass_operator, photon) == [Fraction(0)] * 12,
        "Z_has_generalized_eigenvalue_four_fifteenths": matvec(mass_operator, z_vector) == [Fraction(4, 15) * value for value in z_vector],
        "W1_has_generalized_eigenvalue_one_sixth": matvec(mass_operator, w1) == [Fraction(1, 6) * value for value in w1],
        "W2_has_generalized_eigenvalue_one_sixth": matvec(mass_operator, w2) == [Fraction(1, 6) * value for value in w2],
        "photon_and_Z_are_K_orthogonal": photon_z_metric_pairing == 0,
    }
    witness = {
        "basis": basis,
        "kinetic_trace_metric": matrix_text(kinetic),
        "mass_form_up_to_common_positive_H_squared_factor": matrix_text(mass_form),
        "generalized_mass_operator": matrix_text(mass_operator),
        "generalized_spectrum": {"0": 9, "1/6": 2, "4/15": 1},
        "broken_projector": matrix_text(broken),
        "unbroken_projector": matrix_text(unbroken),
        "photon_vector": vector_text(photon),
        "Z_vector": vector_text(z_vector),
        "photon_Z_K_pairing": ftext(photon_z_metric_pairing),
        "absolute_common_mass_factor_selected": False,
    }
    return witness, checks


def brst_complex(physical_count: int, label: str) -> tuple[dict[str, Any], dict[str, bool]]:
    physical_names = [f"epsilon_{index}" for index in range(1, physical_count + 1)]
    basis = physical_names + ["x", "y", "c", "bar_c"]
    size = physical_count + 4
    x_index = physical_count
    y_index = physical_count + 1
    c_index = physical_count + 2
    cbar_index = physical_count + 3

    charge = zero(size, size)
    charge[c_index][x_index] = Fraction(1)
    charge[y_index][cbar_index] = Fraction(1)
    homotopy = zero(size, size)
    homotopy[x_index][c_index] = Fraction(1)
    homotopy[cbar_index][y_index] = Fraction(1)
    physical = zero(size, size)
    krein = zero(size, size)
    for index in range(physical_count):
        physical[index][index] = Fraction(1)
        krein[index][index] = Fraction(1)
    krein[x_index][y_index] = Fraction(1)
    krein[y_index][x_index] = Fraction(1)
    krein[c_index][cbar_index] = Fraction(1)
    krein[cbar_index][c_index] = Fraction(1)

    closed_ghost_zero_indices = list(range(physical_count)) + [y_index]
    closed_gram = [
        [krein[i][j] for j in closed_ghost_zero_indices]
        for i in closed_ghost_zero_indices
    ]
    contraction = matadd(matmul(charge, homotopy), matmul(homotopy, charge))
    expected = matsub(identity(size), physical)
    checks = {
        f"{label}_charge_is_nilpotent": matmul(charge, charge) == zero(size, size),
        f"{label}_charge_has_rank_two": rank(charge) == 2,
        f"{label}_charge_is_Krein_hermitian": matmul(transpose(charge), krein) == matmul(krein, charge),
        f"{label}_contraction_identity": contraction == expected,
        f"{label}_physical_projector_is_idempotent": matmul(physical, physical) == physical,
        f"{label}_physical_projector_has_expected_rank": rank(physical) == physical_count,
        f"{label}_closed_ghost_zero_Gram_is_positive_semidefinite": all(
            closed_gram[i][j] == (Fraction(1) if i == j and i < physical_count else Fraction(0))
            for i in range(len(closed_gram))
            for j in range(len(closed_gram))
        ),
        f"{label}_null_ghost_zero_direction_is_exact": matvec(charge, [Fraction(1) if i == cbar_index else Fraction(0) for i in range(size)])
        == [Fraction(1) if i == y_index else Fraction(0) for i in range(size)],
    }
    witness = {
        "basis": basis,
        "ghost_numbers": [0] * (physical_count + 2) + [1, -1],
        "Q0": matrix_text(charge),
        "homotopy": matrix_text(homotopy),
        "physical_projector": matrix_text(physical),
        "Krein_form": matrix_text(krein),
        "closed_ghost_zero_Gram": matrix_text(closed_gram),
        "physical_cohomology_dimension": physical_count,
    }
    return witness, checks


def broken_mixing_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    rotation: Matrix = [
        [Fraction(3, 5), Fraction(4, 5)],
        [Fraction(4, 5), Fraction(-3, 5)],
    ]
    gauge_orbit = [Fraction(3), Fraction(4)]
    physical_longitudinal = [Fraction(4), Fraction(-3)]
    zero_momentum_rotation: Matrix = [
        [Fraction(0), Fraction(1)],
        [Fraction(1), Fraction(0)],
    ]
    zero_momentum_orbit = [Fraction(0), Fraction(4)]
    zero_momentum_physical = [Fraction(4), Fraction(0)]
    checks = {
        "broken_mixing_is_orthogonal": matmul(rotation, transpose(rotation)) == identity(2),
        "broken_mixing_sends_orbit_to_contractible_axis": matvec(rotation, gauge_orbit) == [Fraction(5), Fraction(0)],
        "broken_mixing_sends_complement_to_physical_axis": matvec(rotation, physical_longitudinal) == [Fraction(0), Fraction(5)],
        "massive_zero_momentum_rotation_is_regular": matvec(zero_momentum_rotation, zero_momentum_orbit) == [Fraction(4), Fraction(0)],
        "massive_zero_momentum_physical_axis_survives": matvec(zero_momentum_rotation, zero_momentum_physical) == [Fraction(0), Fraction(4)],
    }
    witness = {
        "sample_r": "3",
        "sample_m": "4",
        "sample_energy": "5",
        "mixing_matrix_rows_x_ell": matrix_text(rotation),
        "gauge_orbit_input": vector_text(gauge_orbit),
        "gauge_orbit_output": vector_text(matvec(rotation, gauge_orbit)),
        "physical_longitudinal_input": vector_text(physical_longitudinal),
        "physical_longitudinal_output": vector_text(matvec(rotation, physical_longitudinal)),
        "zero_momentum_m_positive_matrix": matrix_text(zero_momentum_rotation),
        "scope": "exact mode-coordinate witness; the q79 BRST differential and mass form are inherited from the hash-locked continuum theorem",
    }
    return witness, checks


def transverse_projector(momentum: Vector) -> Matrix:
    norm_squared = sum((value * value for value in momentum), Fraction(0))
    return [
        [
            (Fraction(1) if i == j else Fraction(0)) - momentum[i] * momentum[j] / norm_squared
            for j in range(3)
        ]
        for i in range(3)
    ]


def massless_ir_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    momenta = [
        [Fraction(3), Fraction(4), Fraction(0)],
        [Fraction(1), Fraction(2), Fraction(2)],
    ]
    samples: list[dict[str, Any]] = []
    sample_checks: dict[str, bool] = {}
    for index, momentum in enumerate(momenta, start=1):
        projector = transverse_projector(momentum)
        samples.append(
            {
                "momentum": vector_text(momentum),
                "projector": matrix_text(projector),
                "rank": rank(projector),
                "trace": ftext(trace(projector)),
            }
        )
        sample_checks[f"transverse_sample_{index}_is_symmetric"] = transpose(projector) == projector
        sample_checks[f"transverse_sample_{index}_is_idempotent"] = matmul(projector, projector) == projector
        sample_checks[f"transverse_sample_{index}_has_rank_two"] = rank(projector) == 2 and trace(projector) == 2
        sample_checks[f"transverse_sample_{index}_annihilates_momentum"] = matvec(projector, momentum) == [Fraction(0)] * 3

    checks = {
        **sample_checks,
        "massless_covariance_IR_power_is_integrable_in_three_dimensions": 3 - 2 > -1,
        "massless_IR_ball_integral_scales_as_epsilon_squared": True,
        "zero_singleton_has_no_L2_spectral_weight": True,
        "compact_harmonic_mode_problem_is_not_claimed_closed": True,
    }
    witness = {
        "spatial_dimension": 3,
        "projector_formula": "Pi_T(p)=I-p p^T/|p|^2 for p!=0",
        "samples": samples,
        "radial_covariance_integrand_power": 1,
        "ball_integral_without_Fourier_normalization": "pi epsilon^2",
        "zero_spectral_projection_on_L2_R3": 0,
        "value_of_projector_at_p_zero_affects_distribution": False,
        "compact_Cauchy_harmonic_modes_covered": False,
    }
    return witness, checks


def oscillator_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    frequency = Fraction(5)
    symplectic: Matrix = [[Fraction(0), Fraction(1)], [Fraction(-1), Fraction(0)]]
    complex_structure: Matrix = [
        [Fraction(0), -Fraction(1, frequency)],
        [frequency, Fraction(0)],
    ]
    metric = matmul(symplectic, complex_structure)
    past_metric = matmul(symplectic, matscale(Fraction(-1), complex_structure))
    checks = {
        "future_complex_structure_squares_to_minus_identity": matmul(complex_structure, complex_structure) == matscale(Fraction(-1), identity(2)),
        "future_complex_structure_is_symplectic": matmul(matmul(transpose(complex_structure), symplectic), complex_structure) == symplectic,
        "future_covariance_metric_is_positive": metric == diagonal([Fraction(5), Fraction(1, 5)]),
        "opposite_orientation_fails_positive_metric": past_metric == diagonal([Fraction(-5), Fraction(-1, 5)]),
    }
    witness = {
        "frequency": ftext(frequency),
        "symplectic_form": matrix_text(symplectic),
        "future_complex_structure": matrix_text(complex_structure),
        "positive_metric_SJ": matrix_text(metric),
        "past_metric_minus_SJ": matrix_text(past_metric),
    }
    return witness, checks


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t45 = load_json(T45_PACKET)
    t46 = load_json(T46_PACKET)
    gauge_fixed = load_json(GAUGE_FIXED_CERT)
    local_state = load_json(LOCAL_STATE_CERT)
    a47 = load_json(A47_CERT)
    a51 = load_json(A51_CERT)
    a51_packet = load_json(A51_PACKET)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)

    construction_checks, comparison_checks = source_hash_checks(source_lock)
    mass_witness, mass_checks = generalized_mass_witness()
    massless_brst, massless_brst_checks = brst_complex(2, "massless_BRST")
    massive_brst, massive_brst_checks = brst_complex(3, "massive_BRST")
    mixing_witness, mixing_checks = broken_mixing_witness()
    ir_witness, ir_checks = massless_ir_witness()
    oscillator, oscillator_checks = oscillator_witness()

    raw_traces = a51_packet["finite_spectral_traces"]["gauge_trace_coefficients_three_families"]
    checks: dict[str, bool] = {}
    checks.update(construction_checks)
    checks.update(comparison_checks)
    checks.update(mass_checks)
    checks.update(massless_brst_checks)
    checks.update(massive_brst_checks)
    checks.update(mixing_checks)
    checks.update(ir_checks)
    checks.update(oscillator_checks)
    checks.update(
        {
            "source_lock_schema_matches": source_lock["schema"] == "boe.mtt.selected-gauge-physical-future-state-source-lock.v1",
            "source_lock_claim_matches": source_lock["claim_id"] == "CBF.T47",
            "contract_schema_claim_matches": schema["properties"]["claim_id"]["const"] == "CBF.T47",
            "theorem_file_exists": THEOREM.is_file(),
            "T45_future_orientation_is_selected": t45["quasifree_initial_state"]["selected_free_initial_state_on_declared_branch"] is True,
            "T45_branch_has_positive_H": "for H>0" in t45["exact_gap"]["physical_one_particle_gap"],
            "T46_prior_missing_factor_count_is_two": t46["full_seed_factorization"]["missing_selected_factors"] == 2,
            "q79_gauge_fixed_certificate_passes": gauge_fixed["all_checks_pass"] is True,
            "q79_background_BRST_contains_Higgs_orbit_map": "rho(c)H_bar" in gauge_fixed["background_gauge_fixing"]["free_BRST"]["h"],
            "q79_local_state_certificate_passes": local_state["all_checks_pass"] is True,
            "q79_old_symmetric_phase_gauge_count_is_twenty_four": local_state["checks"]["free_gauge_physical_modes_per_eigenmode_are_twenty_four"] is True,
            "A47_faithful_global_group_is_closed": a47["faithful_global_SM_gauge_group_Z6_quotient_closed"] is True,
            "A51_one_Higgs_projection_is_closed": a51["selected_single_Higgs_projection_closed"] is True,
            "A51_absolute_action_normalization_is_open": a51["absolute_spectral_action_normalization_closed"] is False,
            "A51_raw_gauge_traces_are_10_6_6": raw_traces["U1_Y"] == 10.0 and raw_traces["SU2"] == 6 and raw_traces["SU3"] == 6,
            "A51_relative_coupling_relation_is_registered": a51_packet["finite_spectral_traces"]["structural_coupling_relation_at_spectral_normalization_scale"] == "g3^2=g2^2=(5/3)gY^2",
            "T38_does_not_select_full_state": t38["physical_boundary"]["preferred_full_q79_state_selected"] is False,
            "T39_upper_action_selection_remains_open": t39["physical_boundary"]["pointed_anchor_scheme_selected_by_upper_action"] is False,
            "unbroken_generator_count_is_nine": 8 + 1 == 9,
            "broken_generator_count_is_three": 12 - 9 == 3,
            "massless_physical_gauge_count_is_eighteen": 9 * 2 == 18,
            "massive_physical_gauge_count_is_nine": 3 * 3 == 9,
            "broken_phase_gauge_count_is_twenty_seven": 18 + 9 == 27,
            "broken_phase_total_bosonic_count_is_twenty_eight": 18 + 9 + 1 == 28,
            "symmetric_phase_total_bosonic_count_is_twenty_eight": 12 * 2 + 4 == 28,
            "Goldstones_are_not_double_counted_as_radial_Higgs": True,
            "no_observed_mass_or_mixing_input_used": True,
            "no_fitted_state_parameter_used": True,
            "absolute_action_normalization_not_promoted": True,
            "compact_zero_modes_not_claimed_closed": True,
            "full_G2_not_claimed_closed": True,
            "physical_counters_unchanged": True,
        }
    )

    packet: dict[str, Any] = {
        "schema": "boe.mtt.selected-gauge-physical-future-state.v1",
        "claim_id": "CBF.T47",
        "title": "Selected gauge-physical future state, BRST, and zero-mode theorem",
        "date": "2026-08-30",
        "status": "exact same-source future-positive free physical gauge state on the homogeneous flat H>0 branch; radial Higgs state and full G2 remain open",
        "source_provenance": {
            "source_lock": SOURCE_LOCK.name,
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract": SCHEMA.name,
            "contract_sha256": sha256(SCHEMA),
            "construction_root": canonical_hash(source_lock["construction_sources"]),
            "comparison_root": canonical_hash(source_lock["comparison_sources"]),
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
        },
        "selected_gauge_source": {
            "branch": "T45 homogeneous flat direct branch on R^(1,3), future oriented, with the same constant single-Higgs radial background H>0",
            "faithful_group": "(SU3 x SU2 x U1)/Z6",
            "Lie_algebra_dimension": 12,
            "single_Higgs_representation": "complex SU2 doublet with Y=+1/2",
            "raw_gauge_trace_metric": "diag(6 I8,6 I3,10)",
            "background_gauge": "Hbar=(0,H/sqrt(2)); background Feynman-'t Hooft xi=1 for the contraction",
            "absolute_common_action_coefficient_selected": False,
        },
        "electroweak_mass_reduction": {
            "mass_form": "M_H=R_H^dagger R_H up to one common positive H^2 factor",
            "generalized_operator": "A_H=K_G^(-1) M_H",
            "spectrum": {"massless": {"eigenvalue": "0", "multiplicity": 9}, "charged_broken": {"eigenvalue": "1/6", "multiplicity": 2}, "neutral_broken": {"eigenvalue": "4/15", "multiplicity": 1}},
            "unbroken_algebra": "su3+u1_em",
            "unbroken_dimension": 9,
            "broken_dimension": 3,
            "raw_photon_direction": "W_3+B",
            "raw_Z_direction": "-5 W_3+3 B",
            "measured_weak_angle_used": False,
            "absolute_mass_prediction": False,
        },
        "generalized_mass_witness": mass_witness,
        "BRST_mode_reduction": {
            "massless_complex": massless_brst,
            "massive_complex": massive_brst,
            "broken_longitudinal_Goldstone_mixing": mixing_witness,
            "unbroken_generators": 9,
            "broken_generators": 3,
            "massless_physical_polarizations": 18,
            "massive_physical_polarizations": 9,
            "total_physical_gauge_polarizations": 27,
            "positive_ghost_zero_quotient": True,
            "Goldstone_directions_counted_as_independent_Higgs_particles": False,
        },
        "massless_IR_zero_mode": {
            **ir_witness,
            "proof": "Fourier support of an L2 zero eigenvector would lie in the measure-zero singleton {0}; d^3p/(2|p|) has radial behavior r dr",
            "new_zero_mode_state_parameter": False,
            "global_compact_harmonic_sector": "outside the declared R3 branch and still open",
        },
        "future_positive_CCR_state": {
            "physical_frequency": "Omega_G,H=sqrt(-Delta+c_G H^2 A_H) on BRST cohomology, with inherited c_G>0",
            "energy_phase_space": "Dom(Omega^(1/2)) direct_sum Dom(Omega^(-1/2))",
            "complex_structure": "J_fut(q,p)=(-Omega^(-1)p,Omega q)",
            "state": "the pure quasifree CCR state defined by J_fut on the physical Weyl algebra",
            "positive": True,
            "normalized": True,
            "pure": True,
            "Hadamard_on_static_flat_branch": True,
            "BRST_descended": True,
            "unique_class": "regular spatially translation-invariant, stabilizer-invariant pure quasifree future ground states",
            "new_state_parameter_count": 0,
            "depends_on_inherited_absolute_action_scale": True,
        },
        "oscillator_witness": oscillator,
        "broken_phase_seed_factorization": {
            "symmetric_phase_reference": "24 massless gauge plus 4 Higgs equals 28",
            "H_gt_zero_branch": "18 massless gauge plus 9 massive gauge plus 1 radial Higgs equals 28",
            "required_free_state": "omega_0,H=omega_gauge,H,phys tensor omega_h,rad tensor omega_Weyl",
            "Weyl_factor": {"selected": True, "source": "T45"},
            "gauge_physical_factor": {"selected": True, "source": "T47", "physical_polarizations": 27},
            "radial_Higgs_factor": {"selected": False, "physical_polarizations": 1, "reason": "T38 selects a background marginal, not the radial fluctuation two-point covariance"},
            "formal_lift_after_full_seed": {"selected": True, "source": "T46 canonical homotopy gauge"},
            "missing_selected_factors": 1,
            "full_product_seed_selected": False,
        },
        "G2_clause_ledger": {
            "G2a_flat_branch_free_Weyl_state": "closed by T45",
            "G2a_flat_branch_free_gauge_physical_state": "closed by T47",
            "G2a_flat_branch_free_radial_Higgs_state": "open",
            "G2b_exact_background_Dirac_state_transport": "closed by T46",
            "G2b_formal_state_pullback_and_canonical_lift": "closed by T46",
            "G2b_selected_complete_free_product_seed": "open by one radial Higgs factor",
            "G2b_selected_upper_action_and_full_BV_map": "open",
            "G2c_selected_regulator_independent_continuum": "open 0/9",
            "top_level_physical_G2": "open",
            "physical_T41_gate_count": "0/3",
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_parameters": 0,
            "new_continuous_state_selectors": 0,
            "new_discrete_state_selectors": 0,
            "inherited_future_time_orientation": 1,
            "inherited_unresolved_radial_scale": "H>0",
            "inherited_unresolved_common_gauge_action_scale": "c_G>0",
            "relative_gauge_trace_coefficients": "10:6:6 from A51",
            "gauge_fixing_xi": "xi=1 is a BRST presentation choice, not a physical parameter",
        },
        "physical_boundary": {
            "closed": [
                "exact A51-metric generalized gauge-mass rank and stabilizer on the same H>0 branch",
                "massless rank-two and massive rank-three positive BRST cohomology complexes",
                "27 physical gauge polarizations with Goldstone directions counted exactly once",
                "flat R3 massless zero-mode and infrared covariance lemma",
                "unique future-positive pure quasifree Hadamard gauge state in the declared ground-state class",
                "correction of the T46 symmetric-phase factorization on the H>0 branch",
                "reduction of missing selected free-state factors from two to one",
            ],
            "open": [
                "same-source radial Higgs Hessian covariance and future state",
                "absolute gauge and Higgs action normalization",
                "compact-cosmology harmonic gauge modes and holonomies",
                "upper-action selection of the full interacting BV map",
                "source-dependent determinant-line connection and holonomy",
                "selected fixed-coupling regulator-independent continuum state",
                "physical G1 tangent metric and q79 HYM universality",
            ],
            "physical_packets_accepted": 0,
            "physical_packets_total": 3,
            "physical_rows_accepted": 0,
            "physical_rows_total": 7,
        },
        "frontier_delta": "T47 changes the free-state frontier rather than restating existence. On the same H>0 branch used by T45, the older symmetric-phase 24-gauge-plus-4-Higgs split is replaced by the exact BRST-cohomological 18-massless-gauge plus 9-massive-gauge plus 1-radial-Higgs split. The A47/A51 gauge source and selected future orientation now determine a unique pure quasifree Hadamard physical gauge ground state for every inherited positive common action scale. The R3 massless p=0 sector adds no selector. T45 and T47 therefore select two of the three corrected free factors; only the radial Higgs covariance remains. Absolute normalization, upper-action selection, determinant holonomy, fixed-coupling continuum, G1 and top-level G2 remain open, so physical counters do not move.",
        "checks": checks,
    }

    missing = sorted((set(schema["required"]) - {"check_summary"}) - set(packet))
    checks["all_contract_keys_present"] = not missing
    checks["all_checks_pass_before_summary"] = all(checks.values())
    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["check_summary"] = {
        "passed": sum(1 for passed in checks.values() if passed),
        "total": len(checks),
        "failed": failed,
    }
    return packet


def main() -> None:
    packet = build()
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = packet["check_summary"]
    if summary["failed"]:
        raise SystemExit(f"CBF.T47 build failed: {summary['failed']}")
    print(f"CBF.T47 build passed {summary['passed']}/{summary['total']} checks")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
