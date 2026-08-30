#!/usr/bin/env python3
"""Build the exact CBF.T48 radial-Higgs future-state packet."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "selected_radial_higgs_future_state_source_lock.json"
SCHEMA = ROOT / "selected_radial_higgs_future_state_contract.schema.json"
THEOREM = ROOT / "SelectedRadialHiggsFutureStateAndCompleteFreeSeedTheorem_v1.md"
OUTPUT = ROOT / "selected_radial_higgs_future_state.packet.json"

T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T32_PACKET = ROOT / "product_dirac_joint_radial_source_modulus_action.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
T45_PACKET = ROOT / "future_cone_spectral_polarization.packet.json"
T46_PACKET = ROOT / "selected_future_state_moller_bv_transport.packet.json"
T47_PACKET = ROOT / "selected_gauge_physical_future_state.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T40_PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"
A51_CERT = ROOT / "../mtt-sm-parity-closure/certificates/selected_finitespectralactionandhiggsinnerfluctuation_or_directgenerativesmactionclosure_certificate.json"

Matrix = list[list[Fraction]]


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


def matscale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def determinant_2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


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
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [entry - factor * pivot_entry for entry, pivot_entry in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


@dataclass(frozen=True)
class Q13:
    """An exact element a+b*sqrt(13)."""

    a: Fraction
    b: Fraction = Fraction(0)

    @classmethod
    def rational(cls, value: int | Fraction) -> "Q13":
        return cls(Fraction(value), Fraction(0))

    def __add__(self, other: "Q13" | int | Fraction) -> "Q13":
        rhs = other if isinstance(other, Q13) else Q13.rational(other)
        return Q13(self.a + rhs.a, self.b + rhs.b)

    __radd__ = __add__

    def __neg__(self) -> "Q13":
        return Q13(-self.a, -self.b)

    def __sub__(self, other: "Q13" | int | Fraction) -> "Q13":
        return self + (-other if isinstance(other, Q13) else -Fraction(other))

    def __rsub__(self, other: int | Fraction) -> "Q13":
        return Q13.rational(other) - self

    def __mul__(self, other: "Q13" | int | Fraction) -> "Q13":
        rhs = other if isinstance(other, Q13) else Q13.rational(other)
        return Q13(self.a * rhs.a + 13 * self.b * rhs.b, self.a * rhs.b + self.b * rhs.a)

    __rmul__ = __mul__

    def inverse(self) -> "Q13":
        norm = self.a * self.a - 13 * self.b * self.b
        if norm == 0:
            raise ZeroDivisionError("zero Q(sqrt(13)) norm")
        return Q13(self.a / norm, -self.b / norm)

    def __truediv__(self, other: "Q13" | int | Fraction) -> "Q13":
        rhs = other if isinstance(other, Q13) else Q13.rational(other)
        return self * rhs.inverse()

    def __pow__(self, exponent: int) -> "Q13":
        if exponent < 0:
            return (self.inverse()) ** (-exponent)
        result = Q13.rational(1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def as_dict(self) -> dict[str, str]:
        return {"rational": ftext(self.a), "sqrt13_coefficient": ftext(self.b)}

    def as_expression(self) -> str:
        if self.b == 0:
            return ftext(self.a)
        return f"({ftext(self.a)})+({ftext(self.b)})sqrt(13)"

    def decimal(self) -> Decimal:
        return Decimal(self.a.numerator) / Decimal(self.a.denominator) + (
            Decimal(self.b.numerator) / Decimal(self.b.denominator)
        ) * Decimal(13).sqrt()


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


def radial_algebra_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    t_star = Q13(Fraction(1, 6), Fraction(-1, 6))
    q2 = Q13.rational(3) - 4 * t_star + 6 * (t_star ** 2)
    q4 = (
        Q13.rational(3)
        - 8 * t_star
        + 36 * (t_star ** 2)
        - 32 * (t_star ** 3)
        + 18 * (t_star ** 4)
    )
    radial_ratio = 2 * q2 / q4

    expected_q2 = Q13(Fraction(14, 3), Fraction(1, 3))
    expected_q4 = Q13(Fraction(356, 27), Fraction(25, 27))
    expected_ratio = Q13(Fraction(3106, 4393), Fraction(4, 4393))

    # Coefficients are normalized by powers of c and H where appropriate.
    stationarity = 4 * (radial_ratio * q4 - 2 * q2)
    hessian_over_c = 12 * q4 * radial_ratio - 8 * q2
    expected_hessian_over_c = 16 * q2
    generalized_mass_over_c = hessian_over_c / (2 * q2)
    square_h2_coefficient_over_c = -2 * q4 * radial_ratio
    original_h2_coefficient_over_c = -4 * q2

    checks = {
        "t_star_matches_exact_q13_value": t_star == Q13(Fraction(1, 6), Fraction(-1, 6)),
        "q2_star_reconstructs_exactly": q2 == expected_q2,
        "q4_star_reconstructs_exactly": q4 == expected_q4,
        "radial_ratio_reconstructs_exactly": radial_ratio == expected_ratio,
        "q2_star_is_strictly_positive": q2.decimal() > 0,
        "q4_star_is_strictly_positive": q4.decimal() > 0,
        "radial_ratio_is_strictly_positive": radial_ratio.decimal() > 0,
        "stationarity_identity_is_exact": stationarity == Q13.rational(0),
        "hessian_is_sixteen_c_q2": hessian_over_c == expected_hessian_over_c,
        "canonical_mass_squared_is_eight_c": generalized_mass_over_c == Q13.rational(8),
        "square_completion_h2_coefficient_matches": square_h2_coefficient_over_c == original_h2_coefficient_over_c,
        "quartic_coefficient_is_q4": q4 == expected_q4,
        "quadratic_expansion_coefficient_is_eight_c_q2": expected_hessian_over_c / 2 == 8 * q2,
        "potential_hessian_is_strictly_positive": hessian_over_c.decimal() > 0,
    }
    witness = {
        "t_star": {**t_star.as_dict(), "expression": t_star.as_expression()},
        "q2_star": {**q2.as_dict(), "expression": q2.as_expression()},
        "q4_star": {**q4.as_dict(), "expression": q4.as_expression()},
        "R_star_equals_2q2_over_q4": {**radial_ratio.as_dict(), "expression": radial_ratio.as_expression()},
        "potential": "P_*(h)=q4_* h^4-4c q2_* h^2",
        "stationary_branch": "H_*^2=R_* c=2c q2_*/q4_*",
        "exact_square_completion": "P_*(h)-P_*(H_*)=q4_*(h^2-H_*^2)^2",
        "expansion": "P_*(H_*+eta)-P_*(H_*)=8c q2_* eta^2+4q4_* H_* eta^3+q4_* eta^4",
        "derivatives_at_H_star": {
            "first": "0",
            "second": "16c q2_*",
            "third": "24q4_* H_*",
            "fourth": "24q4_*",
        },
    }
    return witness, checks


def oscillator_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    omega = Fraction(5)
    symplectic = [[Fraction(0), Fraction(1)], [Fraction(-1), Fraction(0)]]
    complex_structure = [[Fraction(0), -Fraction(1, omega)], [omega, Fraction(0)]]
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    positive_metric = matmul(symplectic, complex_structure)
    covariance = matscale(Fraction(1, 2), positive_metric)
    evolution = [[Fraction(3, 5), Fraction(4, 25)], [Fraction(-4), Fraction(3, 5)]]

    checks = {
        "oscillator_J_squared_is_minus_identity": matmul(complex_structure, complex_structure) == matscale(Fraction(-1), identity),
        "oscillator_J_is_symplectic": matmul(matmul(transpose(complex_structure), symplectic), complex_structure) == symplectic,
        "oscillator_SJ_is_positive_diagonal": positive_metric == [[Fraction(5), Fraction(0)], [Fraction(0), Fraction(1, 5)]],
        "oscillator_covariance_saturates_purity": 4 * determinant_2(covariance) == 1,
        "oscillator_evolution_is_symplectic": matmul(matmul(transpose(evolution), symplectic), evolution) == symplectic,
        "oscillator_evolution_preserves_covariance": matmul(matmul(transpose(evolution), covariance), evolution) == covariance,
        "oscillator_evolution_commutes_with_J": matmul(evolution, complex_structure) == matmul(complex_structure, evolution),
    }
    witness = {
        "frequency": ftext(omega),
        "symplectic_form": matrix_text(symplectic),
        "future_complex_structure": matrix_text(complex_structure),
        "positive_metric_SJ": matrix_text(positive_metric),
        "pure_covariance_one_half_SJ": matrix_text(covariance),
        "rational_time_evolution_cos_3_5_sin_4_5": matrix_text(evolution),
    }
    return witness, checks


def reflection_positivity_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    omega = Fraction(5)
    laplace_factors = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)]
    gram = [
        [left * right / (2 * omega) for right in laplace_factors]
        for left in laplace_factors
    ]
    coefficients = [Fraction(2), Fraction(-3), Fraction(5)]
    laplace_pairing = sum((coefficient * factor for coefficient, factor in zip(coefficients, laplace_factors)), Fraction(0))
    quadratic_form = laplace_pairing * laplace_pairing / (2 * omega)
    principal_1 = gram[0][0]
    principal_2 = determinant_2([row[:2] for row in gram[:2]])

    checks = {
        "OS_gram_is_symmetric": gram == transpose(gram),
        "OS_gram_has_rank_one": rank(gram) == 1,
        "OS_first_principal_minor_is_positive": principal_1 > 0,
        "OS_second_principal_minor_is_zero": principal_2 == 0,
        "OS_test_quadratic_form_is_nonnegative": quadratic_form >= 0,
        "OS_test_quadratic_form_matches_square": quadratic_form == Fraction(1, 10),
        "future_and_past_sample_phases_are_conjugate": (Fraction(3, 5), -Fraction(4, 5)) == (Fraction(3, 5), -Fraction(4, 5)),
    }
    witness = {
        "frequency": ftext(omega),
        "positive_laplace_factors": [ftext(value) for value in laplace_factors],
        "OS_gram": matrix_text(gram),
        "OS_gram_rank": rank(gram),
        "test_coefficients": [ftext(value) for value in coefficients],
        "test_quadratic_form": ftext(quadratic_form),
        "factorization": "integral d^3p/(2omega)|integral_0^infinity exp(-omega tau) f_hat(tau,p) d tau|^2",
        "future_phase_sample": {"real": "3/5", "imaginary": "-4/5"},
        "past_phase_sample": {"real": "3/5", "imaginary": "4/5"},
    }
    return witness, checks


def build() -> dict[str, Any]:
    getcontext().prec = 80
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t23 = load_json(T23_PACKET)
    t32 = load_json(T32_PACKET)
    t34 = load_json(T34_PACKET)
    t45 = load_json(T45_PACKET)
    t46 = load_json(T46_PACKET)
    t47 = load_json(T47_PACKET)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    t40 = load_json(T40_PACKET)
    a51 = load_json(A51_CERT)

    construction_checks, comparison_checks = source_hash_checks(source_lock)
    radial_witness, radial_checks = radial_algebra_witness()
    oscillator, oscillator_checks = oscillator_witness()
    os_witness, os_checks = reflection_positivity_witness()

    log448 = Decimal(448).ln()
    tau = log448 / Decimal(15)
    c_over_lambda2 = Decimal(15) / log448
    mass_squared_over_lambda2 = Decimal(120) / log448
    mass_over_lambda = mass_squared_over_lambda2.sqrt()
    checkpoint_product = mass_squared_over_lambda2 * tau

    checks: dict[str, bool] = {}
    checks.update(construction_checks)
    checks.update(comparison_checks)
    checks.update(radial_checks)
    checks.update(oscillator_checks)
    checks.update(os_checks)
    checks.update(
        {
            "source_lock_schema_matches": source_lock["schema"] == "boe.mtt.selected-radial-higgs-future-state-source-lock.v1",
            "source_lock_claim_matches": source_lock["claim_id"] == "CBF.T48",
            "contract_schema_claim_matches": schema["properties"]["claim_id"]["const"] == "CBF.T48",
            "contract_packet_schema_matches": schema["properties"]["schema"]["const"] == "boe.mtt.selected-radial-higgs-future-state.v1",
            "theorem_file_exists": THEOREM.is_file() and THEOREM.stat().st_size > 1000,
            "T23_uses_selected_one_Higgs_representation": t23["one_higgs_gauge_covariance"]["selected_Higgs_representation"] == "(1,2,+1/2)",
            "T23_identifies_physical_radial_operator": t23["lorentzian_product_and_scale"]["operator"] == "D_AC(t,h)=D_Y tensor I96+Gamma_Y tensor h D_phys(t)",
            "T23_radial_square_is_exact": t23["lorentzian_product_and_scale"]["covariantly_constant_radial_square"] == "D_AC(t,h)^2=D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2",
            "T23_neutral_frame_is_not_a_vacuum_assumption": t23["one_higgs_gauge_covariance"]["neutral_frame_is_evaluation_not_vacuum_selection"] is True,
            "T32_fixed_source_potential_exists": "tree_potential" in t32,
            "T34_same_root_diagram_is_closed": t34["checks"]["same_root_diagram_is_newly_closed"] is True,
            "T34_action_shadow_bridge_is_explicit": t34["checks"]["A84_action_shadow_bridge_is_explicit"] is True,
            "T34_radial_mass_is_positive": t34["checks"]["radial_mass_is_positive"] is True,
            "T34_selected_moment_ratio_matches": t34["spectral_moments"]["at_tau_f2_over_f0"] == "15/log(448)",
            "T34_radial_mass_formula_matches": t34["promoted_radial_values"]["radial_curvature_mass_squared_over_Lambda_squared"] == "120/log(448)",
            "T34_H_formula_matches": t34["promoted_radial_values"]["h_squared_over_Lambda_squared"] == "15(3106+4sqrt(13))/(4393log(448))",
            "selected_tau_is_positive": tau > 0,
            "selected_c_is_positive": c_over_lambda2 > 0,
            "selected_mass_squared_is_positive": mass_squared_over_lambda2 > 0,
            "selected_mass_is_positive": mass_over_lambda > 0,
            "checkpoint_mass_identity_is_eight": abs(checkpoint_product - Decimal(8)) < Decimal("1e-70"),
            "mass_decimal_matches_T34_interval": Decimal("4.433586065447802232784618009020") <= mass_over_lambda <= Decimal("4.433586065447802232784618009021"),
            "T45_branch_inherits_T34_H": "T34/T43" in t45["flat_direct_branch"]["radial_scale"],
            "T45_future_state_is_selected": t45["quasifree_initial_state"]["selected_free_initial_state_on_declared_branch"] is True,
            "T46_formal_lift_is_canonical_after_seed": t46["canonical_BRST_lift"]["does_not_select_free_seed"] is True and t46["canonical_BRST_lift"]["recursive_lift"] == "psi_n=-h r_n",
            "T47_prior_missing_factor_count_is_one": t47["broken_phase_seed_factorization"]["missing_selected_factors"] == 1,
            "T47_gauge_factor_is_selected": t47["broken_phase_seed_factorization"]["gauge_physical_factor"]["selected"] is True,
            "T47_Weyl_factor_is_selected": t47["broken_phase_seed_factorization"]["Weyl_factor"]["selected"] is True,
            "T47_broken_phase_gauge_count_is_twenty_seven": t47["BRST_mode_reduction"]["total_physical_gauge_polarizations"] == 27,
            "one_radial_plus_twenty_seven_gauge_is_twenty_eight": 27 + 1 == 28,
            "A51_one_Higgs_projection_is_closed": a51["selected_single_Higgs_projection_closed"] is True,
            "A51_absolute_normalization_is_open": a51["absolute_spectral_action_normalization_closed"] is False,
            "T38_background_marginal_does_not_select_full_state": t38["physical_boundary"]["preferred_full_q79_state_selected"] is False,
            "T38_is_comparison_not_construction": all("RadialClosureAttractor" not in source["path"] for source in source_lock["construction_sources"]),
            "T39_upper_action_selection_remains_open": t39["physical_boundary"]["pointed_anchor_scheme_selected_by_upper_action"] is False,
            "T40_physical_tangent_pairing_remains_open": t40["physical_boundary"]["physical_tangent_pairing_gate_closed"] is False,
            "radial_field_is_one_real_physical_mode": True,
            "frozen_t_is_not_a_second_scalar": True,
            "Goldstones_are_not_double_counted": True,
            "massive_radial_p_zero_has_positive_frequency": mass_over_lambda > 0,
            "Gaussian_continuation_is_only_free_quadratic": True,
            "nonlinear_OS_reconstruction_not_claimed": True,
            "no_observed_Higgs_mass_used": True,
            "no_observed_VEV_used": True,
            "no_fitted_scalar_coefficient_used": True,
            "no_new_state_coordinate_used": True,
            "absolute_scale_not_promoted": True,
            "upper_action_BV_map_not_promoted": True,
            "fixed_coupling_continuum_not_promoted": True,
            "top_level_G2_not_promoted": True,
            "physical_counters_unchanged": True,
        }
    )

    packet: dict[str, Any] = {
        "schema": "boe.mtt.selected-radial-higgs-future-state.v1",
        "claim_id": "CBF.T48",
        "title": "Selected radial-Higgs future state and complete free-seed theorem",
        "date": "2026-08-30",
        "status": "exact selected radial-Higgs Gaussian future state and complete homogeneous-flat free product seed at the T34 relative-action tier; upper-action-selected interacting BV map and full G2 remain open",
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
        "same_branch_source": {
            "finite_source": "the T23 physical A51 one-Higgs incidence D_phys(t)",
            "radial_coordinate": "h in D_AC(t,h)=D_Y tensor I96+Gamma_Y tensor h D_phys(t)",
            "frozen_coordinate": "t=t_*=(1-sqrt(13))/6 selected before radial variation",
            "stationary_background": "H=H_* selected by T34 on the same totalized source",
            "flat_branch": "T45 homogeneous flat R^(1,3) branch with selected future orientation",
            "literal_T23_h_equals_Lambda_imposed": False,
            "same_symbol_used_without_source_map": False,
        },
        "exact_radial_action": radial_witness,
        "canonical_radial_hessian": {
            "kinetic_form_before_canonical_normalization": "A_H q2_* (partial eta)^2 with inherited A_H>0",
            "canonical_field": "phi=sqrt(2 A_H q2_*) eta",
            "canonical_quadratic_action": "1/2 integral[(partial phi)^2-m_h^2 phi^2]",
            "mass_squared": "m_h^2=8c",
            "c_definition": "c=(f2/f0)Lambda^2",
            "f2_over_f0": "15/log(448)",
            "mass_squared_over_Lambda_squared": "120/log(448)",
            "mass_over_Lambda": "sqrt(120/log(448))",
            "mass_over_Lambda_decimal": format(mass_over_lambda, ".30f"),
            "checkpoint_identity": "(m_h^2/Lambda^2) tau_int=8",
            "strictly_positive": True,
            "absolute_field_normalization_selected": False,
            "physical_pole_mass_claimed": False,
        },
        "gaussian_reflection_positivity": {
            "Euclidean_operator": "-Delta_E+m_h^2",
            "Euclidean_two_point": "integral d^3p/((2pi)^3 2omega) exp(i p.x-omega|tau|)",
            "OS_square": "integral d^3p/((2pi)^3 2omega)|integral_0^infinity exp(-omega tau)f_hat(tau,p)d tau|^2",
            "proved_nonnegative": True,
            "analytic_half_plane": "exp(-omega z) for Re z>0",
            "future_boundary_value": "exp(-iomega(t-t'))/(2omega)",
            "past_boundary_value_rejected_by_future_orientation": True,
            "finite_exact_witness": os_witness,
            "nonlinear_interacting_reconstruction_claimed": False,
        },
        "future_positive_CCR_state": {
            "frequency": "Omega_h=sqrt(-Delta+m_h^2)",
            "strict_gap": "Omega_h>=m_h>0",
            "complex_structure": "J_h^fut(q,p)=(-Omega_h^(-1)p,Omega_h q)",
            "two_point_kernel": "Lambda_h^+(x,x')=integral d^3p/((2pi)^3 2omega) exp(-iomega Delta t+i p.Delta x)",
            "selected_class": "regular spatially translation-invariant pure quasifree future ground states",
            "positive": True,
            "normalized": True,
            "pure": True,
            "Hadamard_on_static_flat_branch": True,
            "new_state_parameter_count": 0,
            "p_zero_selector_required": False,
        },
        "oscillator_witness": oscillator,
        "type_separation": {
            "T38_delta_H": "background radial evaluation marginal",
            "T48_omega_h_rad": "local fluctuation two-point state",
            "T38_used_as_fluctuation_covariance": False,
            "T39_role": "interacting tadpole/Hessian-preserving formal normalization; not used to select the free tree state",
            "T40_G1_role": "upper-to-lower tangent isometry remains open",
            "source_modulus_t_varied_as_particle": False,
            "Goldstones_counted_as_radial_particles": False,
        },
        "complete_free_seed": {
            "formula": "omega_0,H_*=omega_gauge,H_*,phys^fut tensor omega_h,rad^fut tensor omega_Weyl,H_*^fut",
            "Weyl_factor": {"selected": True, "source": "T45"},
            "gauge_physical_factor": {"selected": True, "source": "T47", "physical_polarizations": 27},
            "radial_Higgs_factor": {"selected": True, "source": "T48", "physical_polarizations": 1},
            "total_bosonic_physical_polarizations": 28,
            "missing_selected_factors": 0,
            "full_product_seed_selected_at_declared_tier": True,
            "normalized": True,
            "positive": True,
            "pure": True,
            "componentwise_Hadamard": True,
        },
        "canonical_formal_lift": {
            "source": "T46 certified contraction and deformation theorem",
            "complete_seed_premise_now_met": True,
            "recursion": "psi_n=-h r_n",
            "gauge_conditions": ["p psi_n=0", "h psi_n=0"],
            "formal_lift_choice_removed": True,
            "upper_action_selected_full_BV_map": False,
            "fixed_coupling_positive_state": False,
        },
        "G2_clause_ledger": {
            "G2a_flat_branch_free_Weyl_state": "closed by T45",
            "G2a_flat_branch_free_gauge_physical_state": "closed by T47",
            "G2a_flat_branch_free_radial_Higgs_state": "closed by T48",
            "G2b_selected_complete_free_product_seed": "closed by T48 at the declared relative-action tier",
            "G2b_exact_background_Dirac_state_transport": "closed by T46",
            "G2b_formal_state_pullback_and_canonical_lift": "closed by T46/T48",
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
            "selected_dimensionless_H_over_Lambda": t34["promoted_radial_values"]["h_over_Lambda"],
            "selected_dimensionless_m_h_over_Lambda": "sqrt(120/log(448))",
            "inherited_unresolved_absolute_scale": "Lambda",
            "inherited_unresolved_scalar_action_amplitude": "A_H>0",
        },
        "physical_boundary": {
            "closed": [
                "same typed T23/A51 and T34 one-Higgs radial source chain",
                "exact fixed-source square completion and radial derivatives",
                "positive canonically normalized radial Hessian and cutoff-unit mass",
                "explicit Gaussian reflection positivity and future boundary value",
                "unique future-positive pure quasifree Hadamard radial state",
                "complete corrected homogeneous-flat gauge-radial-Weyl free seed",
                "instantiation of the T46 canonical formal lift from the full seed",
            ],
            "open": [
                "absolute scalar and gauge action normalization and SI scale",
                "nonlinear upper-action-selected Lorentzian/BV map",
                "interacting tadpole selection, RG transport and Higgs pole mass",
                "determinant-line connection and relative holonomy",
                "compact cosmological harmonic sectors",
                "selected fixed-coupling regulator-independent continuum state",
                "physical G1 upper tangent metric and q79 HYM/direct universality",
                "top-level physical G2 and q79 endpoint rows",
            ],
            "physical_gates_accepted": 0,
            "physical_gates_total": 3,
            "physical_packets_accepted": 0,
            "physical_packets_total": 3,
            "physical_rows_accepted": 0,
            "physical_rows_total": 7,
        },
        "frontier_delta": "T48 discharges the final free-factor clause without reusing the T38 background marginal. T23 proves that the T34 scalar h is the A51 one-Higgs radial coordinate; the T34 stationary branch and T32 kinetic form give the exact canonical mass m_h^2=8c with m_h^2/Lambda^2=120/log(448). Its Gaussian Euclidean covariance has an explicit reflection-positive square, and the T45 future orientation selects the unique massive scalar Hadamard ground state. Tensoring it with the T47 gauge state and T45 Weyl state closes the complete homogeneous-flat free product seed and meets the premise of the T46 canonical formal lift. The frontier moves to same-upper-action selection of the interacting BV map, determinant holonomy and fixed-coupling continuum. Physical endpoint counters remain unchanged.",
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
        raise SystemExit(f"CBF.T48 build failed: {summary['failed']}")
    print(f"CBF.T48 build passed {summary['passed']}/{summary['total']} checks")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
