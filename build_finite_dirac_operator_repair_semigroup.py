#!/usr/bin/env python3
"""Build the exact CBF.T28 operator-space repair Hessian packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_upper_totalization_supercharge_selection as uts
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "finite_dirac_operator_repair_semigroup_source_lock.json"
SCHEMA = ROOT / "finite_dirac_operator_repair_semigroup_contract.schema.json"
THEOREM = ROOT / "FiniteDiracOperatorSpaceRepairHessianSemigroupAndProfileBoundaryTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T26_PACKET = ROOT / "direct_dirac_defect_repair_action.packet.json"
T27_PACKET = ROOT / "finite_dirac_spectral_action_classification.packet.json"
OUTPUT = ROOT / "finite_dirac_operator_repair_semigroup.packet.json"

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


def real_part(value: cp.K) -> Fraction:
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"expected a real scalar, received {value}")
    return value[0]


def normalized_trace(matrix: cp.Matrix) -> Fraction:
    return real_part(matrix_trace(matrix)) / len(matrix)


def inner(left: cp.Matrix, right: cp.Matrix) -> Fraction:
    product = uts.sparse_matmul(cp.adjoint(left), right)
    return normalized_trace(product)


def theta(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(d0, uts.sparse_matmul(value, d0))


def p_comm(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.mscale(q(Fraction(1, 2)), cp.madd(value, theta(d0, value)))


def p_anti(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.mscale(q(Fraction(1, 2)), matrix_sub(value, theta(d0, value)))


def defect_derivative(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(
        uts.sparse_matmul(d0, value), uts.sparse_matmul(value, d0)
    )


def repair_hessian(d0: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return defect_derivative(d0, defect_derivative(d0, value))


def full_gradient(value: cp.Matrix) -> cp.Matrix:
    square = uts.sparse_matmul(value, value)
    defect = matrix_sub(square, cp.identity(len(value)))
    return cp.mscale(q(2), uts.sparse_matmul(value, defect))


def outer(left: list[cp.K], right: list[cp.K]) -> cp.Matrix:
    result = cp.zero(len(left), len(right))
    for row, left_value in enumerate(left):
        for column, right_value in enumerate(right):
            result[row][column] = cp.kmul(left_value, cp.kconj(right_value))
    return result


def nonzero_column(matrix: cp.Matrix) -> list[cp.K]:
    for column in range(len(matrix[0])):
        vector = [matrix[row][column] for row in range(len(matrix))]
        if any(value != cp.ZERO for value in vector):
            return vector
    raise AssertionError("matrix has no nonzero column")


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
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.finite-dirac-operator-repair-semigroup-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "configuration_space": "End_sa(H_F), dim_R=9216",
        "metric": "g(X,Y)=Re (Tr/96)(X^*Y)",
        "D0_sha256": d0_hash,
        "D1_sha256": d1_hash,
        "H_phys_sha256": h_hash,
        "repair_hessian": "A_rep=J0^*J0=4P_comm",
        "repair_hessian_spectrum": {"0": 4608, "4": 4608},
        "repair_semigroup": "exp(-sA_rep)=P_anti+exp(-4s)P_comm",
        "physical_spectral_profile": None,
        "signed_physical_action": None,
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
    t27 = json.loads(T27_PACKET.read_text(encoding="ascii"))

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
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
    h_phys = defect_derivative(d0, d1)
    remainder = uts.sparse_matmul(d1, d1)
    h2 = uts.sparse_matmul(h_phys, h_phys)

    e_plus = cp.mscale(q(Fraction(1, 2)), cp.madd(identity96, d0))
    e_minus = cp.mscale(q(Fraction(1, 2)), matrix_sub(identity96, d0))
    rank_plus = cp.matrix_rank(e_plus)
    rank_minus = cp.matrix_rank(e_minus)
    comm_dimension = rank_plus**2 + rank_minus**2
    anti_dimension = 2 * rank_plus * rank_minus

    plus_vector = nonzero_column(e_plus)
    minus_vector = nonzero_column(e_minus)
    commuting_sample = outer(plus_vector, plus_vector)
    cross = outer(plus_vector, minus_vector)
    anticommuting_sample = cp.madd(cross, cp.adjoint(cross))
    generic_sample = cp.madd(commuting_sample, anticommuting_sample)

    samples = {
        "D1": d1,
        "H_phys": h_phys,
        "R": remainder,
        "commuting_rank_one": commuting_sample,
        "anticommuting_cross": anticommuting_sample,
        "generic_split": generic_sample,
    }
    algebra_checks: dict[str, bool] = {}
    for name, sample in samples.items():
        plus = p_comm(d0, sample)
        minus = p_anti(d0, sample)
        algebra_checks[f"{name}_projectors_resolve"] = cp.madd(plus, minus) == sample
        algebra_checks[f"{name}_Pcomm_idempotent"] = p_comm(d0, plus) == plus
        algebra_checks[f"{name}_Panti_idempotent"] = p_anti(d0, minus) == minus
        algebra_checks[f"{name}_projectors_orthogonal"] = inner(plus, minus) == 0
        algebra_checks[f"{name}_J_squared_equals_4Pcomm"] = (
            repair_hessian(d0, sample) == cp.mscale(q(4), plus)
        )

    d1_norm_squared = inner(d1, d1)
    pullback_hessian = inner(d1, repair_hessian(d0, d1))
    tr_r = real_part(matrix_trace(remainder))
    tr_h2 = real_part(matrix_trace(h2))
    a_d1 = repair_hessian(d0, d1)
    a_h = repair_hessian(d0, h_phys)
    a_r = repair_hessian(d0, remainder)

    t_sample = Fraction(1, 2)
    d_sample = cp.madd(d0, cp.mscale(q(t_sample), d1))
    gradient_sample = full_gradient(d_sample)
    projected_coefficient = inner(d1, gradient_sample) / d1_norm_squared
    expected_projected_coefficient = (
        2 * t_sample * (3 * t_sample**2 - 4 * t_sample + 2)
    )

    d0_hash = uts.matrix_digest(d0)
    d1_hash = uts.matrix_digest(d1)
    h_hash = uts.matrix_digest(h_phys)
    theorem_hash = sha256(THEOREM)
    root_hash, root_payload = source_root(
        source_lock, theorem_hash, d0_hash, d1_hash, h_hash
    )
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        **algebra_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.finite-dirac-operator-repair-semigroup-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "23aae2ca-0eff-4cb1-b39f-a4bbf78cabf9",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.finite-dirac-operator-repair-semigroup.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20"
        and all(t20["checks"].values()),
        "T23_response_is_exact": t23["claim_id"] == "CBF.T23"
        and all(t23["checks"].values()),
        "T26_repair_action_is_exact": t26["claim_id"] == "CBF.T26"
        and all(t26["checks"].values()),
        "T27_spectral_classification_is_exact": t27["claim_id"] == "CBF.T27"
        and all(t27["checks"].values()),
        "D0_is_self_adjoint": d0 == cp.adjoint(d0),
        "D0_square_is_identity": uts.sparse_matmul(d0, d0) == identity96,
        "D0_plus_rank_is_48": rank_plus == 48,
        "D0_minus_rank_is_48": rank_minus == 48,
        "material_projectors_are_orthogonal": uts.sparse_matmul(e_plus, e_minus)
        == cp.zero(96, 96),
        "material_projectors_resolve_identity": cp.madd(e_plus, e_minus) == identity96,
        "commuting_tangent_dimension_is_4608": comm_dimension == 4608,
        "anticommuting_tangent_dimension_is_4608": anti_dimension == 4608,
        "operator_tangent_dimension_is_9216": comm_dimension + anti_dimension == 9216,
        "commuting_sample_is_nonzero": commuting_sample != cp.zero(96, 96),
        "anticommuting_sample_is_nonzero": anticommuting_sample != cp.zero(96, 96),
        "commuting_sample_has_positive_parity": p_comm(d0, commuting_sample)
        == commuting_sample,
        "anticommuting_sample_has_negative_parity": p_anti(d0, anticommuting_sample)
        == anticommuting_sample,
        "defect_derivative_kills_tangent_sample": defect_derivative(
            d0, anticommuting_sample
        )
        == cp.zero(96, 96),
        "repair_hessian_is_positive_on_normal_sample": inner(
            commuting_sample, repair_hessian(d0, commuting_sample)
        )
        > 0,
        "H_phys_matches_T23": h_hash
        == t23["hessian_compression"]["KO6_response_sha256"],
        "D1_commutes_with_D0": uts.sparse_matmul(d0, d1)
        == uts.sparse_matmul(d1, d0),
        "J0_D1_equals_H_phys": defect_derivative(d0, d1) == h_phys,
        "R_equals_H_squared_over_four": remainder
        == cp.mscale(q(Fraction(1, 4)), h2),
        "D1_is_normal": p_comm(d0, d1) == d1,
        "H_phys_is_normal": p_comm(d0, h_phys) == h_phys,
        "R_is_normal": p_comm(d0, remainder) == remainder,
        "A_D1_equals_4D1": a_d1 == cp.mscale(q(4), d1),
        "A_H_equals_4H": a_h == cp.mscale(q(4), h_phys),
        "A_R_equals_4R": a_r == cp.mscale(q(4), remainder),
        "trace_R_is_192": tr_r == 192,
        "normalized_D1_norm_squared_is_2": d1_norm_squared == 2,
        "trace_H_squared_is_768": tr_h2 == 768,
        "pullback_Hessian_is_8": pullback_hessian == 8,
        "pullback_Hessian_equals_metric_times_eigenvalue": pullback_hessian
        == d1_norm_squared * 4,
        "induced_scalar_linear_rate_is_4": pullback_hessian / d1_norm_squared == 4,
        "projected_full_gradient_matches_scalar_pullback": projected_coefficient
        == expected_projected_coefficient,
        "nonlinear_branch_ratio_difference_nonzero_at_sample": -6 * t_sample**2
        != 0,
        "full_affine_family_not_nonlinearly_invariant": gradient_sample
        != cp.mscale(q(projected_coefficient), d1),
        "repair_supertrace_profile_has_equal_multiplicities": comm_dimension
        == anti_dimension,
        "full_operator_space_hessian_is_newly_closed": not boundary[
            "full_operator_space_hessian_before"
        ]
        and boundary["full_operator_space_hessian_after"],
        "same_root_repair_semigroup_is_newly_closed": not boundary[
            "same_root_repair_semigroup_before"
        ]
        and boundary["same_root_repair_semigroup_after"],
        "repair_semigroup_profile_is_selected": boundary[
            "repair_semigroup_profile_selected"
        ],
        "repair_generator_is_not_material_R_or_H2": not boundary[
            "repair_generator_equals_R_or_H_phys_squared"
        ],
        "physical_spectral_profile_remains_open": not boundary[
            "physical_spectral_action_profile_selected"
        ],
        "repair_time_to_tau_int_remains_open": not boundary[
            "repair_time_identified_with_tau_int"
        ],
        "signed_physical_action_remains_open": not boundary[
            "signed_physical_action_selected"
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
        raise AssertionError(f"CBF.T28 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.finite-dirac-operator-repair-semigroup.v1",
        "claim_id": "CBF.T28",
        "date": "2026-08-29",
        "status": (
            "exact full operator-space positive repair Hessian and semigroup; "
            "signed physical action and scalar spectral-action profile open"
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
        "configuration_space": {
            "carrier": "V_sa=End_sa(H_F)",
            "H_F_complex_dimension": 96,
            "V_sa_real_dimension": 9216,
            "metric": "g(X,Y)=Re tau96(X^*Y)",
            "normalized_trace": "tau96=Tr/96",
            "basepoint": "D0",
            "D0_spectrum": {"-1": 48, "1": 48},
            "D0_sha256": d0_hash,
        },
        "closure_functional": {
            "definition": "C(D)=1/2 tau96((D^2-I96)^*(D^2-I96))",
            "defect_map": "F(D)=D^2-I96",
            "basepoint_defect": "F(D0)=0",
            "full_gradient_on_self_adjoint_D": "grad C(D)=2D(D^2-I96)",
            "positive_repair_not_signed_action": True,
        },
        "frechet_linearization": {
            "definition": "J0(X)=DF_D0[X]=D0X+XD0",
            "metric_adjoint": "J0^*=J0",
            "theta": "Ad_D0(X)=D0XD0",
            "theta_is_orthogonal_involution": True,
        },
        "hessian_superoperator": {
            "definition": "A_rep=J0^*J0=J0^2",
            "exact_identity": "A_rep=2(I+Ad_D0)=4P_comm",
            "P_comm": "P_comm=(I+Ad_D0)/2",
            "P_anti": "P_anti=(I-Ad_D0)/2",
            "spectrum": {"0": 4608, "4": 4608},
            "rank": 4608,
            "nullity": 4608,
            "materialized_9216_square_matrix": False,
        },
        "tangent_normal_decomposition": {
            "tangent": "Ran(P_anti)={X:{D0,X}=0}",
            "normal": "Ran(P_comm)={X:[D0,X]=0}",
            "tangent_real_dimension": anti_dimension,
            "normal_real_dimension": comm_dimension,
            "nearby_minimum_manifold": "unitary orbit of self-adjoint involutions",
            "finite_Morse_Bott": True,
        },
        "repair_semigroup": {
            "linearized_equation": "d_s X=-A_rep X",
            "exact_solution": "T_s=P_anti+exp(-4s)P_comm",
            "contraction_for_nonnegative_s": True,
            "entire_complexification": "T_z=P_anti+exp(-4z)P_comm",
            "imaginary_boundary": "T_it=P_anti+exp(-4it)P_comm",
            "quarter_boundary": "T_(i*pi/8)=P_anti-iP_comm",
            "physical_Lorentzian_time_identified": False,
        },
        "selected_family_pullback": {
            "family": "D_phys(t)=D0+tD1",
            "D1_sha256": d1_hash,
            "H_phys_sha256": h_hash,
            "commuting_identities": [
                "A_rep(D1)=4D1",
                "A_rep(H_phys)=4H_phys",
                "A_rep(R)=4R",
            ],
            "induced_metric_g_tt": str(d1_norm_squared),
            "scalar_Hessian": str(pullback_hessian),
            "scalar_Hessian_interpretation": "g_tt times normal eigenvalue 4",
            "induced_metric_gradient": "d_s t=-2t(3t^2-4t+2)",
            "linearized_scalar_rate": "d_s t=-4t",
        },
        "nonlinear_flow_boundary": {
            "full_gradient": "grad C(D)=2D(D^2-I96)",
            "branch_ratio": "r_h(t)=2t+(3/2)t^2 h+(1/4)t^3 h^2",
            "decisive_difference": "r_-2(t)-r_+2(t)=-6t^2",
            "affine_family_invariant_only_at": ["t=0"],
            "scalar_flow_is_constrained_projection": True,
            "nonzero_physical_coordinate_selected": False,
        },
        "typed_operator_comparison": {
            "A_rep_type": "End_sa(H_F)->End_sa(H_F)",
            "R_type": "H_F->H_F",
            "H_phys_squared_type": "H_F->H_F",
            "A_rep_spectrum": {"0": 4608, "4": 4608},
            "R_spectrum": {"1": 64, "4": 32},
            "H_phys_squared_spectrum": {"4": 64, "16": 32},
            "R_is_A_rep_eigenvector_not_A_rep": True,
            "repair_semigroup_equals_exp_minus_sR": False,
            "normalized_supertrace_profile": "(1+exp(-4s))/2",
        },
        "action_profile_boundary": {
            "same_root_exponential_repair_profile_selected": True,
            "scalar_profile_f_of_D_phys_squared_selected": False,
            "repair_semigroup_is_physical_spectral_action": False,
            "signed_cyclic_or_BV_action_selected": False,
            "absolute_repair_scale_selected": False,
            "nonzero_Yukawa_or_mass_value_selected": False,
        },
        "authority_reconciliation": {
            "A84": (
                "general closure-Hessian-to-semigroup mechanism instantiated "
                "exactly with A_rep=4P_comm"
            ),
            "A53": (
                "tau_int=log(448)/15 is not imported because no selected "
                "comparison map identifies it with 4s"
            ),
            "A85": (
                "finite spectral action acts on H_F while the repair semigroup "
                "acts on End_sa(H_F); primitive scalar profile remains open"
            ),
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_sector_specific_parameters": 0,
            "new_dimensionful_primitives": 0,
            "normalized_repair_scale_convention": 1,
            "scale_is_physical_parameter": False,
        },
        "physical_boundary": {
            "full_operator_space_repair_Hessian_closed": True,
            "same_root_repair_semigroup_closed": True,
            "A84_general_mechanism_instantiated": True,
            "selected_physical_action_profile": False,
            "signed_physical_action_selected": False,
            "repair_time_to_tau_int_selected": False,
            "nonzero_physical_source_coordinate_selected": False,
            "held_out_physical_observable_emitted": False,
            "B_ACTION_01_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The T26 closure functional now emits its complete typed Hessian "
            "A_rep=4P_comm on the 9216-real-dimensional self-adjoint operator "
            "tangent, with exact spectrum 0^4608,4^4608 and semigroup "
            "P_anti+exp(-4s)P_comm. This closes the exponential repair-profile "
            "source and the same-root A84 mechanism. It also proves that the "
            "generator is not R or H_phys^2 and cannot select the scalar "
            "physical spectral-action profile; signed action promotion remains open."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }
    if set(packet) != set(schema["properties"]):
        raise AssertionError("packet top-level keys do not match contract schema")
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(
        "finite Dirac operator-space repair packet built: "
        f"{len(checks)}/{len(checks)} checks; Hessian and repair semigroup closed; "
        "signed action and scalar physical profile remain open"
    )


if __name__ == "__main__":
    main()
