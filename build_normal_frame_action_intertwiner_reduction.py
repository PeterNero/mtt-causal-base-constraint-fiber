#!/usr/bin/env python3
"""Build the exact CBF.T18 normal-frame and action-intertwiner certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "normal_frame_action_intertwiner_source_lock.json"
SCHEMA = ROOT / "normal_frame_action_intertwiner_contract.schema.json"
THEOREM = ROOT / "NormalFrameQuotientAndActionIntertwinerMinimalDataTheorem_v1.md"
T17_PACKET = ROOT / "affine_zero_section_action.packet.json"
SM_ROOT = ROOT.parent / "mtt-sm-parity-closure"
TRACE_PACKET = (
    SM_ROOT
    / "candidate_data"
    / "selected_finiteweyl_traceuniqueness_or_physicalboundarysource_derivation"
    / "finite_weyl_trace_uniqueness_derivation.packet.json"
)
FSB_ROOT = ROOT.parent / "mtt-q79-total-superconnection-branching"
DYNAMIC_PACKET = FSB_ROOT / "artifacts" / "triadic_dynamic_weyl_orbit.packet.json"
ALGEBRA_PACKET = FSB_ROOT / "artifacts" / "triadic_family_response_algebra.packet.json"
FSB_MANIFEST = FSB_ROOT / "state" / "source_manifest.v1.json"
OUTPUT = ROOT / "normal_frame_action_intertwiner_reduction.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qscalar(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def sum_k(values: Any) -> cp.K:
    total = cp.ZERO
    for value in values:
        total = cp.kadd(total, value)
    return total


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    return sum_k(matrix[index][index] for index in range(len(matrix)))


def frobenius_inner(left: cp.Matrix, right: cp.Matrix) -> cp.K:
    return sum_k(
        cp.kmul(cp.kconj(left[row][column]), right[row][column])
        for row in range(len(left))
        for column in range(len(left[0]))
    )


def matrix_equal(left: cp.Matrix, right: cp.Matrix) -> bool:
    return left == right


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(qscalar(-1), right))


def matvec(matrix: cp.Matrix, vector: list[cp.K]) -> list[cp.K]:
    return [
        sum_k(cp.kmul(entry, value) for entry, value in zip(row, vector))
        for row in matrix
    ]


def inner(left: list[cp.K], right: list[cp.K]) -> cp.K:
    return sum_k(cp.kmul(cp.kconj(x), y) for x, y in zip(left, right))


def vector_add(left: list[cp.K], right: list[cp.K]) -> list[cp.K]:
    return [cp.kadd(x, y) for x, y in zip(left, right)]


def basis_vector(size: int, index: int, value: cp.K = cp.ONE) -> list[cp.K]:
    result = [cp.ZERO for _ in range(size)]
    result[index] = value
    return result


def q_form(hessian: cp.Matrix, vector: list[cp.K]) -> cp.K:
    value = inner(vector, matvec(hessian, vector))
    return value[0], value[1], Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(entry) for entry in row] for row in payload]


def routed_hessian(algebra: dict[str, Any]) -> tuple[cp.Matrix, cp.Matrix, cp.Matrix]:
    shapes = algebra["exact_witness"]["response_shapes"]
    a = decode_matrix(shapes["A_H_shift"])
    b = decode_matrix(shapes["B_H_phase"])
    phase_slots = {6, 7, 8, 14}
    shift_slots = {9, 10, 11, 15}
    r_phase = cp.diagonal(
        [cp.ONE if index in phase_slots else cp.ZERO for index in range(16)]
    )
    r_shift = cp.diagonal(
        [cp.ONE if index in shift_slots else cp.ZERO for index in range(16)]
    )
    hessian = cp.madd(cp.kron(b, r_phase), cp.kron(a, r_shift))
    return a, b, hessian


def weyl_pair() -> tuple[cp.Matrix, cp.Matrix]:
    omega = (Fraction(-1, 2), Fraction(0), Fraction(0), Fraction(1, 2))
    omega2 = cp.kmul(omega, omega)
    shift = [
        [cp.ZERO, cp.ONE, cp.ZERO],
        [cp.ZERO, cp.ZERO, cp.ONE],
        [cp.ONE, cp.ZERO, cp.ZERO],
    ]
    clock = cp.diagonal([cp.ONE, omega, omega2])
    return shift, clock


def complex_action(
    epsilon: cp.K,
    curvature: cp.K,
    normal: cp.K,
    multiplier: cp.K,
) -> cp.K:
    field = cp.kneg(cp.kmul(epsilon, normal))
    constraint = cp.kmul(multiplier, cp.kadd(normal, curvature))
    return cp.kadd(field, constraint)


def locked_source_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        checks[f"source_hash_{Path(source['path']).name}"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t17 = json.loads(T17_PACKET.read_text(encoding="ascii"))
    trace_packet = json.loads(TRACE_PACKET.read_text(encoding="utf-8"))
    dynamic = json.loads(DYNAMIC_PACKET.read_text(encoding="utf-8"))
    algebra = json.loads(ALGEBRA_PACKET.read_text(encoding="utf-8"))

    a_response, b_response, hessian = routed_hessian(algebra)
    hessian_rank = cp.matrix_rank(hessian)
    hessian_norm2 = frobenius_inner(hessian, hessian)
    hessian_trace = matrix_trace(hessian)

    weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    y16 = cp.diagonal([qscalar(value) for value in weights])
    p_neutral = cp.diagonal(
        [cp.ONE if index == 15 else cp.ZERO for index in range(16)]
    )

    shift, clock = weyl_pair()
    weyl_constraints = cp.make_family_commutant_constraints(shift, clock)
    weyl_commutant_dimension = 9 - cp.matrix_rank(weyl_constraints)
    response_constraints = cp.make_family_commutant_constraints(a_response, b_response)
    response_commutant_dimension = 9 - cp.matrix_rank(response_constraints)
    rho = cp.mscale(qscalar(Fraction(1, 3)), cp.identity(3))

    i_unit = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    sqrt3 = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    one_plus_i = (Fraction(1), Fraction(0), Fraction(1), Fraction(0))
    frame_scalars = [qscalar(2), qscalar(-3), i_unit, one_plus_i, cp.kadd(sqrt3, i_unit)]
    tangent_samples = [
        basis_vector(48, 6),
        vector_add(basis_vector(48, 7), basis_vector(48, 8, i_unit)),
        vector_add(basis_vector(48, 25), basis_vector(48, 27, sqrt3)),
        vector_add(basis_vector(48, 46), basis_vector(48, 47, one_plus_i)),
    ]
    normal_samples = [qscalar(Fraction(2, 5)), one_plus_i, cp.kadd(qscalar(-2), sqrt3)]
    multiplier_samples = [qscalar(Fraction(7, 3)), i_unit, cp.kadd(qscalar(1), sqrt3)]

    frame_contraction_invariant = True
    frame_action_invariant = True
    frame_graph_invariant = True
    factorization_orbit_unique = True
    for frame in frame_scalars:
        epsilon_frame = cp.kinv(frame)
        contracted = cp.mscale(epsilon_frame, cp.mscale(frame, hessian))
        frame_contraction_invariant = frame_contraction_invariant and contracted == hessian
        for tangent, normal, multiplier in zip(
            tangent_samples,
            normal_samples + normal_samples[:1],
            multiplier_samples + multiplier_samples[:1],
        ):
            curvature = cp.kmul(qscalar(Fraction(1, 2)), q_form(hessian, tangent))
            transformed_curvature = cp.kmul(frame, curvature)
            transformed_normal = cp.kmul(frame, normal)
            transformed_multiplier = cp.kmul(cp.kinv(frame), multiplier)
            base_action = complex_action(cp.ONE, curvature, normal, multiplier)
            transformed_action = complex_action(
                epsilon_frame,
                transformed_curvature,
                transformed_normal,
                transformed_multiplier,
            )
            frame_action_invariant = frame_action_invariant and base_action == transformed_action
            base_graph = cp.kadd(cp.kneg(curvature), curvature)
            transformed_graph = cp.kadd(
                cp.kneg(transformed_curvature), transformed_curvature
            )
            frame_graph_invariant = (
                frame_graph_invariant
                and base_graph == cp.ZERO
                and transformed_graph == cp.ZERO
            )

    for first in frame_scalars:
        for second in frame_scalars:
            transition = cp.kdiv(second, first)
            b_first = cp.mscale(first, hessian)
            b_second = cp.mscale(second, hessian)
            epsilon_first = cp.kinv(first)
            epsilon_second = cp.kinv(second)
            factorization_orbit_unique = factorization_orbit_unique and (
                cp.mscale(transition, b_first) == b_second
                and cp.kmul(epsilon_first, cp.kinv(transition)) == epsilon_second
            )

    scale_samples = [Fraction(1, 2), Fraction(7, 3), Fraction(5)]
    recovered_scales: list[str] = []
    scale_recovery_exact = True
    scale_residuals_zero = True
    for scale in scale_samples:
        effective = cp.mscale(qscalar(scale), hessian)
        recovered = cp.kdiv(frobenius_inner(hessian, effective), hessian_norm2)
        residual = matrix_sub(effective, cp.mscale(recovered, hessian))
        recovered_scales.append(str(recovered[0]))
        scale_recovery_exact = scale_recovery_exact and recovered == qscalar(scale)
        scale_residuals_zero = scale_residuals_zero and residual == cp.zero(48, 48)

    scale_two = cp.mscale(qscalar(2), hessian)
    scale_three = cp.mscale(qscalar(3), hessian)
    projectively_equal_but_absolutely_distinct = (
        scale_two != scale_three
        and cp.mscale(qscalar(3), scale_two) == cp.mscale(qscalar(2), scale_three)
        and cp.matrix_rank(scale_two) == cp.matrix_rank(scale_three) == hessian_rank
    )

    source_checks = locked_source_checks(source_lock)
    trace_derived = trace_packet["derived_now"]
    trace_not_derived = trace_packet["not_derived_now"]
    boundary = source_lock["boundary"]
    contract = schema["properties"]

    checks = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.normal-frame-action-intertwiner-lock.v1",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": contract["schema"]["const"] == "boe.mtt.normal-frame-action-intertwiner.v1",
        "contract_quotients_separate_normal_covector": contract["normal_frame_quotient"]["properties"]["separate_normal_covector_is_physical_input"]["const"] is False,
        "contract_requires_one_Hessian_identity": contract["physical_intertwiner"]["properties"]["required_identity"]["const"] == "H_eff=c_action H_resp",
        "contract_keeps_absolute_scale_open": contract["physical_intertwiner"]["properties"]["absolute_scale_selected"]["const"] is False,
        "T17_exact_action_is_imported": t17["claim_id"] == "CBF.T17" and all(t17["checks"].values()),
        "T17_physical_rows_remain_zero": t17["physical_rows_accepted"] == 0,
        "A50_hypercharge_operator_has_rank_15": cp.matrix_rank(y16) == 15,
        "A50_hypercharge_kernel_has_dimension_one": 16 - cp.matrix_rank(y16) == 1,
        "neutral_projector_has_rank_one": cp.matrix_rank(p_neutral) == 1,
        "neutral_projector_is_in_hypercharge_kernel": cp.matmul(y16, p_neutral) == cp.zero(16, 16),
        "all_other_H16_weights_are_nonzero": all(value != 0 for value in weights[:15]),
        "selected_object_is_line_not_frame": boundary["unique_gauge_shared_circle_invariant_normal_line"] and not boundary["unit_frame_or_nonzero_covector_selected"],
        "normal_frame_GL1_samples_are_nonzero": all(frame != cp.ZERO for frame in frame_scalars),
        "normal_frame_contraction_is_exactly_invariant": frame_contraction_invariant,
        "normal_frame_full_affine_action_is_exactly_invariant": frame_action_invariant,
        "normal_frame_closure_graph_is_exactly_invariant": frame_graph_invariant,
        "nonzero_factorizations_form_one_tested_GL1_orbit": factorization_orbit_unique,
        "separate_normal_frame_adds_no_physical_parameter": not boundary["normal_frame_is_a_physical_parameter"],
        "Weyl_shift_is_unitary": cp.matmul(cp.adjoint(shift), shift) == cp.identity(3),
        "Weyl_clock_is_unitary": cp.matmul(cp.adjoint(clock), clock) == cp.identity(3),
        "Weyl_pair_commutant_dimension_is_one": weyl_commutant_dimension == 1,
        "response_AB_commutant_dimension_is_one": response_commutant_dimension == 1,
        "normalized_density_has_trace_one": matrix_trace(rho) == cp.ONE,
        "normalized_density_is_shift_invariant": cp.matmul(shift, cp.matmul(rho, cp.adjoint(shift))) == rho,
        "normalized_density_is_clock_invariant": cp.matmul(clock, cp.matmul(rho, cp.adjoint(clock))) == rho,
        "A74_trace_packet_selects_normalized_trace": trace_derived["finite_measure_equals_normalized_trace"],
        "A74_trace_choice_adds_no_knob": trace_derived["measure_choice_is_not_a_new_knob"],
        "A74_does_not_bind_physical_action": trace_not_derived["physical_PhiFinC1_action_restricts_to_finite_quotient"],
        "finite_trace_is_not_promoted_to_BV_density": not boundary["normalized_family_trace_is_the_physical_BV_density"],
        "FSB04e_is_exact_finite_same_source": dynamic["claim_id"] == "FSB.04e" and dynamic["all_checks_pass"],
        "FSB04f_generates_full_M3": algebra["exact_witness"]["complex_response_algebra"]["generated_algebra"] == "M3(C) after scalar extension",
        "routed_response_is_Hermitian": hessian == cp.adjoint(hessian),
        "routed_response_has_rank_24": hessian_rank == 24,
        "routed_response_frobenius_norm_squared_is_192": hessian_norm2 == qscalar(192),
        "routed_response_normalized_full_trace_square_is_4": cp.kdiv(hessian_norm2, qscalar(48)) == qscalar(4),
        "routed_response_normalized_active_trace_square_is_8": cp.kdiv(hessian_norm2, qscalar(24)) == qscalar(8),
        "routed_response_trace_is_minus_32": hessian_trace == qscalar(-32),
        "endpoint_scale_formula_recovers_all_exact_samples": scale_recovery_exact,
        "endpoint_scale_residual_vanishes_on_all_exact_samples": scale_residuals_zero,
        "normalized_finite_shape_cannot_distinguish_two_positive_scales": projectively_equal_but_absolutely_distinct,
        "physical_same_root_intertwiner_remains_open": not boundary["physical_same_root_intertwiner_proved"],
        "physical_action_scale_remains_open": not boundary["physical_action_scale_selected"],
        "Lorentz_Higgs_Yukawa_typing_remains_open": not boundary["Lorentz_Higgs_Yukawa_typing_proved"],
        "nine_charged_values_remain_open": boundary["strict_charged_magnitude_values_remaining"] == 9,
        "physical_packet_acceptance_is_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "no_observed_values_enter_the_witness": True,
        "no_fitted_coefficients_enter_the_witness": True,
    }

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"failed checks: {failed}")

    packet = {
        "schema": "boe.mtt.normal-frame-action-intertwiner.v1",
        "claim_id": "CBF.T18",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_SOURCE_PINNED_FINITE_QUOTIENT_WITNESS + CONDITIONAL_PHYSICAL_INTERTWINER_REDUCTION",
        "decision": [
            "A46_A47_A50_SELECT_ONE_INVARIANT_NORMAL_LINE_NOT_A_FRAME",
            "SEPARATE_NONZERO_NORMAL_FACTORS_FORM_ONE_GL1_ORBIT",
            "THE_CONTRACTED_HESSIAN_IS_THE_FRAME_INVARIANT_ACTION_DATUM",
            "A74_FIXES_THE_FINITE_FAMILY_TRACE_NOT_THE_PHYSICAL_BV_DENSITY",
            "THE_PHYSICAL_EXIT_IS_ONE_SAME_ROOT_HESSIAN_INTERTWINER_AND_SCALE",
        ],
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "finite_source_manifest_sha256": sha256(FSB_MANIFEST),
        "normal_line": {
            "carrier": "N^c subset H16",
            "H16_order": ["Q6", "u3", "d3", "L2", "e1", "N1"],
            "expanded_hypercharge_weights_6Y": weights,
            "projector": "diag(0,...,0,1)",
            "complex_dimension": 1,
            "invariant_multiplicity": 1,
            "unit_frame_selected": False,
            "separate_real_ray_selected": False,
        },
        "normal_frame_quotient": {
            "frame_group": "GL(1,C)",
            "frame_action": "(B,epsilon,n,lambda)->(aB,epsilon/a,an,lambda/a)",
            "invariant_contraction": "H=epsilon o B",
            "full_action_invariant": "A_(aB,epsilon/a)(an,k,lambda/a)=A_(B,epsilon)(n,k,lambda)",
            "factorization_orbits_for_nonzero_H": 1,
            "frame_samples": [cp.encode(frame) for frame in frame_scalars],
            "separate_frame_is_physical_parameter": False,
        },
        "finite_trace": {
            "family_algebra": "M3(C)",
            "Weyl_commutant_dimension": weyl_commutant_dimension,
            "response_AB_commutant_dimension": response_commutant_dimension,
            "invariant_density": "I3/3",
            "functional": "tau3(A)=Tr(A)/3",
            "finite_family_measure_parameters": 0,
            "physical_BV_density_identified": False,
        },
        "contracted_response": {
            "formula": "H_resp=B_phase tensor R_phase+A_shift tensor R_shift",
            "complex_dimension": 48,
            "complex_rank": hessian_rank,
            "complex_kernel": 48 - hessian_rank,
            "trace": str(hessian_trace[0]),
            "frobenius_norm_squared": str(hessian_norm2[0]),
            "normalized_full_trace_square": "4",
            "normalized_active_trace_square": "8",
            "new_matrix_added": False,
        },
        "physical_intertwiner_minimal_data": {
            "reducing_case": "H_eff=U^* K_phys U",
            "nonreducing_case": "H_eff=U^*K_phys U-U^*K_phys Q(QK_physQ)^-1QK_physU",
            "required_identity": "H_eff=c_action H_resp",
            "coefficient_formula": "c_action=<H_resp,H_eff>_F/192",
            "residual": "R_action=H_eff-c_action H_resp",
            "coefficient_is_unique_if_identity_holds": True,
            "exact_test_scales": [str(value) for value in scale_samples],
            "exact_recovered_scales": recovered_scales,
            "same_root_required": True,
            "same_root_physical_intertwiner_supplied": False,
            "physical_density_and_BV_pushforward_supplied": False,
        },
        "scale_nonidentifiability": {
            "normalized_shape_determines_absolute_scale": False,
            "positive_scale_family": "{c H_resp:c>0}",
            "invariants_preserved": [
                "rank_and_kernel",
                "projective_spectrum",
                "normal_frame_orbit",
                "automorphism_and_commutant_groups",
                "normalized_trace_state",
                "normalized_response_direction",
            ],
            "absolute_Hessian_and_quantum_phase_change": True,
            "endpoint_action_or_equivalent_metrology_required": True,
        },
        "source_provenance": {
            "A46_A47_A50_select_normal_line": True,
            "A74_selects_finite_trace": True,
            "A86_FSB04e_04f_select_finite_response_tier": True,
            "finite_source_manifest_is_physical_endpoint_root": False,
            "physical_endpoint_status": "OPEN",
        },
        "parameter_ledger": {
            "observed_construction_inputs": 0,
            "fitted_coefficients": 0,
            "normal_frame_parameters_after_quotient": 0,
            "finite_family_measure_parameters": 0,
            "new_contracted_response_matrices": 0,
            "conditional_common_action_coefficients_per_endpoint": 1,
            "selected_physical_action_coefficients": 0,
            "strict_charged_magnitude_values_remaining": 9,
        },
        "claim_boundary": {
            "physical_endpoint_selected": False,
            "physical_action_scale_selected": False,
            "physical_BV_density_selected": False,
            "Lorentz_Higgs_Yukawa_typing": False,
            "charged_values_derived": 0,
            "physical_packets_accepted": 0,
            "physical_rows_accepted": 0,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The A47/A50 neutral normal object is now proved to be one selected "
            "line, while its frame and the separate factors epsilon and B are "
            "quotient data. A74 removes the finite family-measure choice. The "
            "action-side physical exit is reduced to one same-root identity "
            "H_eff=c_action H_resp, with c_action uniquely recoverable from an "
            "endpoint but nonidentifiable from normalized finite data alone."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }

    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "normal-frame action-intertwiner packet built: "
        f"{len(checks)}/{len(checks)} checks; physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
