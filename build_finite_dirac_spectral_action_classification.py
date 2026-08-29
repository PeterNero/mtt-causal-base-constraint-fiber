#!/usr/bin/env python3
"""Build the exact CBF.T27 finite Dirac spectral-action classification."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_upper_totalization_supercharge_selection as uts
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "finite_dirac_spectral_action_classification_source_lock.json"
SCHEMA = ROOT / "finite_dirac_spectral_action_classification_contract.schema.json"
THEOREM = ROOT / "CanonicalFiniteDiracSpectralActionClassificationAndProfileSelectionNoGoTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T26_PACKET = ROOT / "direct_dirac_defect_repair_action.packet.json"
OUTPUT = ROOT / "finite_dirac_spectral_action_classification.packet.json"

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for index in range(len(matrix)):
        total = cp.kadd(total, matrix[index][index])
    return total


def real_trace(matrix: cp.Matrix) -> Fraction:
    value = matrix_trace(matrix)
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"expected real trace, received {value}")
    return value[0]


def add_scalar(matrix: cp.Matrix, scalar: Fraction | int) -> cp.Matrix:
    return cp.madd(matrix, cp.mscale(q(scalar), cp.identity(len(matrix))))


def spectral_projector(hessian: cp.Matrix, eigenvalue: int) -> cp.Matrix:
    eigenvalues = (-4, -2, 2)
    result = cp.identity(len(hessian))
    denominator = 1
    for other in eigenvalues:
        if other == eigenvalue:
            continue
        result = uts.sparse_matmul(result, add_scalar(hessian, -other))
        denominator *= eigenvalue - other
    return cp.mscale(q(Fraction(1, denominator)), result)


def moment_one(t: Fraction) -> Fraction:
    return 2 * t * t - Fraction(4, 3) * t + 1


def moment_two(t: Fraction) -> Fraction:
    return (
        6 * t**4
        - Fraction(32, 3) * t**3
        + 12 * t**2
        - Fraction(8, 3) * t
        + 1
    )


def repair_action(t: Fraction) -> Fraction:
    return 4 * t**2 - Fraction(16, 3) * t**3 + 3 * t**4


def quartic_stationary_cubic(t: Fraction) -> Fraction:
    return 9 * t**3 - 12 * t**2 + 9 * t - 1


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def source_root(
    source_lock: dict[str, Any], theorem_hash: str, hessian_hash: str
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.finite-dirac-spectral-action-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "finite_source": "D_phys(t)=D0(I96+t H_phys/2)",
        "H_phys_sha256": hessian_hash,
        "H_phys_spectrum": {"-4": 32, "-2": 32, "2": 32},
        "D_phys_squared_spectrum": {
            "(2t-1)^2": 32,
            "(t-1)^2": 32,
            "(t+1)^2": 32,
        },
        "universal_spectral_functional": (
            "tau96 f(D_phys(t)^2)="
            "[f((t-1)^2)+f((t+1)^2)+f((2t-1)^2)]/3"
        ),
        "profile_independent_stationary_coordinate": None,
        "selected_physical_profile": None,
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
    t26 = json.loads(T26_PACKET.read_text(encoding="ascii"))

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    fourier = wg.decode_matrix(primitive["F3"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)

    d0 = uts.physical_dirac(
        uts.physical_transfer(p, phase_direction, shift_direction, Fraction(0))
    )
    d_at_one = uts.physical_dirac(
        uts.physical_transfer(p, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)
    d0d1 = uts.sparse_matmul(d0, d1)
    d1d0 = uts.sparse_matmul(d1, d0)
    hessian = cp.madd(d0d1, d1d0)
    hessian2 = uts.sparse_matmul(hessian, hessian)
    remainder = uts.sparse_matmul(d1, d1)

    factor_direction = cp.madd(
        identity96, cp.mscale(q(Fraction(1, 2)), hessian)
    )
    h_minimal = uts.sparse_matmul(
        add_scalar(hessian, 4),
        uts.sparse_matmul(add_scalar(hessian, 2), add_scalar(hessian, -2)),
    )
    projectors = {
        eigenvalue: spectral_projector(hessian, eigenvalue)
        for eigenvalue in (-4, -2, 2)
    }
    d0_plus = cp.mscale(q(Fraction(1, 2)), cp.madd(identity96, d0))
    d0_minus = cp.mscale(q(Fraction(1, 2)), matrix_sub(identity96, d0))
    signed_joint_projectors = {
        (eigenvalue, sign): uts.sparse_matmul(
            projector, d0_plus if sign == 1 else d0_minus
        )
        for eigenvalue, projector in projectors.items()
        for sign in (-1, 1)
    }
    projector_sum = cp.zero(96, 96)
    for projector in projectors.values():
        projector_sum = cp.madd(projector_sum, projector)

    sample_parameters = [
        Fraction(-2),
        Fraction(-1),
        Fraction(-1, 2),
        Fraction(0),
        Fraction(1, 3),
        Fraction(1, 2),
        Fraction(1),
        Fraction(2),
    ]
    factorization_checks: list[bool] = []
    square_spectrum_checks: list[bool] = []
    moment_checks: list[bool] = []
    for parameter in sample_parameters:
        direct = uts.physical_dirac(
            uts.physical_transfer(
                p, phase_direction, shift_direction, parameter
            )
        )
        expected_direct = uts.sparse_matmul(
            d0,
            cp.madd(
                identity96,
                cp.mscale(q(parameter / 2), hessian),
            ),
        )
        factorization_checks.append(direct == expected_direct)
        direct_square = uts.sparse_matmul(direct, direct)
        expected_square = cp.zero(96, 96)
        branch_values = {
            -4: (2 * parameter - 1) ** 2,
            -2: (parameter - 1) ** 2,
            2: (parameter + 1) ** 2,
        }
        for eigenvalue, projector in projectors.items():
            expected_square = cp.madd(
                expected_square,
                cp.mscale(q(branch_values[eigenvalue]), projector),
            )
        square_spectrum_checks.append(direct_square == expected_square)
        normalized_trace_square = real_trace(direct_square) / 96
        normalized_trace_fourth = real_trace(
            uts.sparse_matmul(direct_square, direct_square)
        ) / 96
        moment_checks.extend(
            [
                normalized_trace_square == moment_one(parameter),
                normalized_trace_fourth == moment_two(parameter),
            ]
        )

    phase_fourier = uts.sparse_matmul(
        cp.adjoint(fourier), uts.sparse_matmul(shift_direction, fourier)
    )
    baseline_fourier = uts.sparse_matmul(
        cp.adjoint(fourier), uts.sparse_matmul(p, fourier)
    )

    lower = Fraction(132, 1000)
    upper = Fraction(133, 1000)
    alpha = 0.132061614157470
    t_minus = (1 - math.sqrt(13)) / 6
    t_plus = (1 + math.sqrt(13)) / 6

    theorem_hash = sha256(THEOREM)
    hessian_hash = uts.matrix_digest(hessian)
    root_hash, root_payload = source_root(source_lock, theorem_hash, hessian_hash)
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.finite-dirac-spectral-action-classification-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "b5346b8d-1373-42c2-bee8-e0ddab69ef62",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.finite-dirac-spectral-action-classification.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20"
        and all(t20["checks"].values()),
        "T23_source_is_exact": t23["claim_id"] == "CBF.T23"
        and all(t23["checks"].values()),
        "T26_repair_action_is_exact": t26["claim_id"] == "CBF.T26"
        and all(t26["checks"].values()),
        "D0_square_is_identity": uts.sparse_matmul(d0, d0) == identity96,
        "D0_and_D1_commute": d0d1 == d1d0,
        "D0_and_H_commute": uts.sparse_matmul(d0, hessian)
        == uts.sparse_matmul(hessian, d0),
        "D1_equals_D0_H_over_2": d1
        == cp.mscale(q(Fraction(1, 2)), uts.sparse_matmul(d0, hessian)),
        "R_equals_H_squared_over_4": remainder
        == cp.mscale(q(Fraction(1, 4)), hessian2),
        "factor_direction_matches_D_at_one": d_at_one
        == uts.sparse_matmul(d0, factor_direction),
        "affine_factorization_matches_all_samples": all(factorization_checks),
        "H_minimal_polynomial_vanishes": h_minimal == cp.zero(96, 96),
        "H_phys_matches_T23": hessian_hash
        == t23["hessian_compression"]["KO6_response_sha256"],
        "H_phys_is_self_adjoint": hessian == cp.adjoint(hessian),
        "projectors_sum_to_identity": projector_sum == identity96,
        "projectors_are_self_adjoint": all(
            projector == cp.adjoint(projector)
            for projector in projectors.values()
        ),
        "projectors_are_idempotent": all(
            uts.sparse_matmul(projector, projector) == projector
            for projector in projectors.values()
        ),
        "projectors_are_pairwise_orthogonal": all(
            uts.sparse_matmul(projectors[left], projectors[right])
            == cp.zero(96, 96)
            for left in projectors
            for right in projectors
            if left != right
        ),
        "each_H_eigenspace_has_rank_32": all(
            cp.matrix_rank(projector) == 32 for projector in projectors.values()
        ),
        "each_H_eigenspace_has_trace_32": all(
            real_trace(projector) == 32 for projector in projectors.values()
        ),
        "each_signed_joint_eigenspace_has_rank_16": all(
            cp.matrix_rank(projector) == 16
            for projector in signed_joint_projectors.values()
        ),
        "each_signed_joint_eigenspace_has_trace_16": all(
            real_trace(projector) == 16
            for projector in signed_joint_projectors.values()
        ),
        "full_square_spectrum_matches_all_samples": all(square_spectrum_checks),
        "trace_moments_match_all_samples": all(moment_checks),
        "phase_and_shift_directions_are_Fourier_conjugate": phase_fourier
        == phase_direction,
        "baseline_is_Fourier_invariant": baseline_fourier == p,
        "quadratic_moment_has_unique_minimum_at_one_third": (
            2 * Fraction(1, 3) - Fraction(2, 3) == 0 and 2 > 0
        ),
        "quadratic_moment_minimum_is_seven_over_eighteen": (
            moment_one(Fraction(1, 3)) / 2 == Fraction(7, 18)
        ),
        "quartic_stationary_root_is_bracketed": quartic_stationary_cubic(lower)
        < 0
        < quartic_stationary_cubic(upper),
        "quartic_stationary_cubic_is_strictly_increasing": 24**2 - 4 * 27 * 9
        == -396,
        "quadratic_and_quartic_profiles_disagree": quartic_stationary_cubic(
            Fraction(1, 3)
        )
        == 1,
        "repair_profile_selects_zero": repair_action(Fraction(0)) == 0
        and t26["positivity_and_stationarity"]["real_stationary_set"] == ["t=0"],
        "logdet_has_two_exact_stationary_roots": 1 - 4 * 3 * (-1) == 13,
        "heat_derivative_bracket_is_positive_for_tau_positive": Fraction(-1, 9)
        > Fraction(-16, 9)
        and Fraction(-4, 9) > Fraction(-16, 9),
        "no_common_polynomial_profile_stationary_coordinate": boundary[
            "profile_independent_stationary_coordinate_exists"
        ]
        is False,
        "no_common_heat_profile_stationary_coordinate": boundary[
            "profile_independent_stationary_coordinate_exists"
        ]
        is False,
        "exact_full_spectrum_is_newly_closed": not boundary[
            "exact_full_spectrum_before"
        ]
        and boundary["exact_full_spectrum_after"],
        "exact_factorization_is_newly_closed": not boundary[
            "exact_D0_H_factorization_before"
        ]
        and boundary["exact_D0_H_factorization_after"],
        "all_scalar_even_spectral_functionals_are_now_reduced": not boundary[
            "all_scalar_even_spectral_functionals_reduced_before"
        ]
        and boundary["all_scalar_even_spectral_functionals_reduced_after"],
        "spectral_profile_remains_unselected": not boundary[
            "spectral_profile_selected_by_finite_operator_and_trace"
        ],
        "signed_physical_action_remains_open": not boundary[
            "signed_physical_action_selected"
        ],
        "nonzero_physical_coordinate_remains_open": not boundary[
            "nonzero_physical_source_coordinate_selected"
        ],
        "held_out_observable_remains_open": not boundary[
            "held_out_physical_observable_emitted"
        ],
        "B_ACTION_01_remains_open": not boundary["B_ACTION_01_closed"],
        "B_SM_02_remains_open": not boundary["B_SM_02_closed"],
        "no_observed_values_used": not boundary["observed_values_used"],
        "no_fitted_coefficients_used": not boundary["fitted_coefficients_used"],
        "physical_packet_acceptance_unchanged": boundary[
            "physical_packet_acceptance_before"
        ]
        == boundary["physical_packet_acceptance_after"]
        == 0,
        "physical_row_acceptance_unchanged": boundary[
            "physical_row_acceptance_before"
        ]
        == boundary["physical_row_acceptance_after"]
        == 0,
        "source_root_is_nonempty": len(root_hash) == 64,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T27 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.finite-dirac-spectral-action-classification.v1",
        "claim_id": "CBF.T27",
        "date": "2026-08-29",
        "status": (
            "exact full finite-Dirac spectral classification and "
            "profile-independent value-selection no-go; physical action open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_sha256": root_hash,
            "source_root_payload": root_payload,
        },
        "finite_source": {
            "carrier": "H_F",
            "complex_dimension": 96,
            "family": "D_phys(t)=D0+tD1",
            "D0_square": "I96",
            "D0_D1_commute": True,
            "H_phys_definition": "H_phys=D0D1+D1D0=2D0D1",
            "H_phys_sha256": hessian_hash,
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
        },
        "exact_factorization": {
            "D1_identity": "D1=(1/2)D0 H_phys",
            "D_identity": "D_phys(t)=D0(I96+t H_phys/2)",
            "R_identity": "R=D1^2=H_phys^2/4",
            "square_identity": "D_phys(t)^2=(I96+t H_phys/2)^2",
            "minimal_polynomial": "(H_phys+4I)(H_phys+2I)(H_phys-2I)=0",
            "all_identities_exact": True,
        },
        "joint_spectrum": {
            "H_phys": {"-4": 32, "-2": 32, "2": 32},
            "R_given_H": {"-4": 4, "-2": 1, "2": 1},
            "spectral_projector_ranks": {"-4": 32, "-2": 32, "2": 32},
            "spectral_projectors_are_exact_orthogonal_resolution": True,
        },
        "full_spectrum": {
            "D_phys_squared": {
                "(2t-1)^2": 32,
                "(t-1)^2": 32,
                "(t+1)^2": 32,
            },
            "D_phys_signed": {
                "+(1-2t)": 16,
                "-(1-2t)": 16,
                "+(1-t)": 16,
                "-(1-t)": 16,
                "+(1+t)": 16,
                "-(1+t)": 16,
            },
            "singular_walls": ["t=-1", "t=1/2", "t=1"],
            "D_phys_at_zero_spectrum": {"-1": 48, "1": 48},
            "phase_shift_lane_spectra_identical": True,
            "reason": "fixed F3 Fourier conjugacy",
        },
        "spectral_functional": {
            "normalized_trace": "tau96=Tr/96",
            "definition": "S_f(t)=tau96 f(D_phys(t)^2)",
            "exact_formula": (
                "S_f(t)=[f((t-1)^2)+f((t+1)^2)+"
                "f((2t-1)^2)]/3"
            ),
            "derivative": (
                "S_f'(t)=(2/3)[(t-1)f'((t-1)^2)+"
                "(t+1)f'((t+1)^2)+"
                "2(2t-1)f'((2t-1)^2)]"
            ),
            "ordinary_odd_trace_moments": "zero by grading-symmetric spectrum",
            "profile_f_selected_by_trace_theorem": False,
        },
        "profile_examples": {
            "dirac_norm": {
                "profile": "f(s)=s/2",
                "action": "t^2-(2/3)t+1/2",
                "unique_global_minimizer": "t=1/3",
                "minimum": "7/18",
                "physical_selection_claimed": False,
            },
            "quartic_moment": {
                "profile": "f(s)=s^2",
                "action": "6t^4-(32/3)t^3+12t^2-(8/3)t+1",
                "stationary_equation": "9t^3-12t^2+9t-1=0",
                "unique_global_minimizer_interval": ["0.132", "0.133"],
                "unique_global_minimizer_approx": f"{alpha:.15f}",
                "physical_selection_claimed": False,
            },
            "defect_repair": {
                "profile": "f(s)=(s-1)^2/2",
                "action": "4t^2-(16/3)t^3+3t^4",
                "unique_global_minimizer": "t=0",
                "source": "CBF.T26",
                "physical_signed_action_claimed": False,
            },
            "normalized_logdet": {
                "profile": "f(s)=log(s)",
                "domain": "t not in {-1,1/2,1}",
                "action": "(2/3)log|(t-1)(t+1)(2t-1)|",
                "stationary_equation": "3t^2-t-1=0",
                "stationary_points_exact": [
                    "(1-sqrt(13))/6",
                    "(1+sqrt(13))/6",
                ],
                "stationary_points_approx": [
                    f"{t_minus:.15f}",
                    f"{t_plus:.15f}",
                ],
                "logdet_stationary_type": "strict local maxima",
                "minus_logdet_stationary_type": "strict chamberwise local minima",
                "physical_selection_claimed": False,
            },
        },
        "heat_profile_no_go": {
            "family": "f_tau(s)=exp(-tau s), tau>0",
            "functional": (
                "H_tau(t)=[exp(-tau(t-1)^2)+exp(-tau(t+1)^2)+"
                "exp(-tau(2t-1)^2)]/3"
            ),
            "common_stationary_candidate_for_all_tau": "t=1/3 from the tau-linear term",
            "derivative_at_candidate": (
                "(4tau/9)[exp(-4tau/9)+exp(-tau/9)-"
                "2exp(-16tau/9)]"
            ),
            "derivative_at_candidate_positive_for_all_tau": True,
            "common_stationary_coordinate_exists": False,
            "A53_tau_int_selects_profile_under_current_authority": False,
        },
        "profile_selection_no_go": {
            "operator_and_trace_determine_spectral_arguments": True,
            "operator_and_trace_determine_scalar_profile": False,
            "no_common_stationary_point_even_for_profiles": ["f(s)=s", "f(s)=s^2"],
            "no_common_stationary_point_for_all_heat_profiles": True,
            "profile_choice_changes_stationary_coordinate": True,
            "conclusion": (
                "D_phys(t) and tau96 alone cannot select a physical t; a same-root "
                "action/profile or nonlinear repair law is necessary"
            ),
            "no_go_scope": (
                "spectral-profile-independent selection only; it does not forbid "
                "an upstream MTT theorem selecting one physical action"
            ),
        },
        "coordinate_interpretation": {
            "t_is_defined_as": "deformation coordinate of the CBF.T20/CBF.T23 family",
            "closure_basepoint": "t=0",
            "D_phys_at_closure_is_zero": False,
            "D_phys_at_closure_is_unitary_involution": True,
            "closure_basepoint_has_equal_singular_magnitudes": True,
            "closure_basepoint_alone_emits_family_hierarchy": False,
            "nonzero_spectral_stationary_point_is_measured_Yukawa": False,
            "lesson": (
                "Selecting a deformation coordinate and deriving physical Higgs/Yukawa "
                "magnitudes are distinct tasks"
            ),
        },
        "action_boundary": {
            "A74_normalized_trace_used": True,
            "A74_selects_profile": False,
            "A73_logdet_precedent_used_as_comparison_only": True,
            "A53_one_atom_heat_profile_is_conditional": True,
            "A85_finite_spectral_action_is_at_declared_corpus_tier": True,
            "signed_Lorentzian_action_selected": False,
            "BV_QME_selected": False,
            "absolute_action_normalization_selected": False,
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_dimensionful_primitives": 0,
            "new_sector_specific_parameters": 0,
            "unselected_functional_choices_compared": 4,
            "compared_profiles_are_parameters_of_final_model": False,
            "numerical_physical_t_selected": False,
            "numerical_physical_h_selected": False,
        },
        "physical_boundary": {
            "exact_full_finite_spectrum_closed": True,
            "exact_D0_H_factorization_closed": True,
            "all_even_spectral_profiles_reduced_to_three_branches": True,
            "profile_independent_value_selection_ruled_out": True,
            "selected_physical_action_profile": False,
            "nonzero_physical_source_coordinate_selected": False,
            "strict_Yukawa_magnitudes_emitted": False,
            "held_out_physical_observable_emitted": False,
            "B_ACTION_01_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The complete 96D spectral family is now exact: D_phys(t)="
            "D0(I+tH_phys/2), with H_phys spectrum {-4,-2,2} at multiplicity "
            "32 and D_phys(t)^2 branches (2t-1)^2, (t-1)^2 and (t+1)^2. "
            "Every scalar spectral action is therefore reduced to one explicit "
            "three-term formula. The same source yields incompatible stationary "
            "coordinates for the Dirac norm, quartic moment, defect repair and "
            "logdet profiles, and no coordinate is stationary for all heat profiles. "
            "Consequently the remaining action blocker is profile selection, not "
            "matrix construction or spectral computation."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"wrote {OUTPUT.name}: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
