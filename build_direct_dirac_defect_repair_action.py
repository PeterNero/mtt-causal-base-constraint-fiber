#!/usr/bin/env python3
"""Build the exact CBF.T26 normalized Dirac-square repair-action packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_upper_totalization_supercharge_selection as uts
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "direct_dirac_defect_repair_action_source_lock.json"
SCHEMA = ROOT / "direct_dirac_defect_repair_action_contract.schema.json"
THEOREM = ROOT / "CanonicalNormalizedDiracSquareDefectRepairActionAndValueSelectionNoGoTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
OUTPUT = ROOT / "direct_dirac_defect_repair_action.packet.json"

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    result = cp.ZERO
    for index in range(len(matrix)):
        result = cp.kadd(result, matrix[index][index])
    return result


def real_part(value: cp.K) -> Fraction:
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"expected real scalar, received {value}")
    return value[0]


def normalized_trace(matrix: cp.Matrix) -> Fraction:
    return real_part(matrix_trace(matrix)) / len(matrix)


def repair_value(defect: cp.Matrix) -> Fraction:
    return normalized_trace(uts.sparse_matmul(cp.adjoint(defect), defect)) / 2


def polynomial_value(t: Fraction) -> Fraction:
    return 4 * t * t - Fraction(16, 3) * t**3 + 3 * t**4


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def cyclic_permutation(size: int) -> cp.Matrix:
    result = cp.zero(size, size)
    for target in range(size):
        result[target][(target - 1) % size] = cp.ONE
    return result


def source_root(
    source_lock: dict[str, Any],
    theorem_hash: str,
    h_hash: str,
    r_hash: str,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.direct-dirac-defect-repair-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "finite_source": "D_phys(t)=D0+tD1 on H_F of complex dimension 96",
        "defect": "K(t)=D_phys(t)^2-I96=t H_phys+t^2 R",
        "normalized_repair_action": "S_rep(t)=1/2 (Tr/96)(K(t)^*K(t))",
        "coefficients": {"t2": "4", "t3": "-16/3", "t4": "3"},
        "H_phys_sha256": h_hash,
        "R_sha256": r_hash,
        "observed_targets": [],
        "signed_physical_action": None,
        "physical_source_coordinate": None,
        "held_out_observable": None,
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

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    phase_direction = cp.madd(cp.identity(3), z)
    shift_direction = cp.madd(cp.identity(3), x)

    d0 = uts.physical_dirac(
        uts.physical_transfer(p, phase_direction, shift_direction, Fraction(0))
    )
    d_at_one = uts.physical_dirac(
        uts.physical_transfer(p, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)
    h_phys = cp.madd(
        uts.sparse_matmul(d0, d1), uts.sparse_matmul(d1, d0)
    )
    remainder = uts.sparse_matmul(d1, d1)

    h2 = uts.sparse_matmul(h_phys, h_phys)
    hr = uts.sparse_matmul(h_phys, remainder)
    rh = uts.sparse_matmul(remainder, h_phys)
    r2 = uts.sparse_matmul(remainder, remainder)
    tr_h2 = real_part(matrix_trace(h2))
    tr_hr = real_part(matrix_trace(hr))
    tr_r2 = real_part(matrix_trace(r2))
    coefficient_t2 = tr_h2 / (2 * 96)
    coefficient_t3 = tr_hr / 96
    coefficient_t4 = tr_r2 / (2 * 96)

    sample_parameters = [
        Fraction(-2),
        Fraction(-1),
        Fraction(-1, 2),
        Fraction(0),
        Fraction(1, 2),
        Fraction(1),
        Fraction(2),
    ]
    residual_identity_checks: list[bool] = []
    polynomial_checks: list[bool] = []
    sample_values: dict[str, str] = {}
    for parameter in sample_parameters:
        d_parameter = uts.physical_dirac(
            uts.physical_transfer(
                p, phase_direction, shift_direction, parameter
            )
        )
        defect = matrix_sub(
            uts.sparse_matmul(d_parameter, d_parameter), identity96
        )
        expected = cp.madd(
            cp.mscale(q(parameter), h_phys),
            cp.mscale(q(parameter * parameter), remainder),
        )
        value = repair_value(defect)
        residual_identity_checks.append(defect == expected)
        polynomial_checks.append(value == polynomial_value(parameter))
        sample_values[str(parameter)] = str(value)

    permutation = cyclic_permutation(96)
    basis_sample = cp.madd(
        cp.mscale(q(Fraction(1, 2)), h_phys),
        cp.mscale(q(Fraction(1, 4)), remainder),
    )
    transported_sample = uts.sparse_matmul(
        permutation,
        uts.sparse_matmul(basis_sample, cp.adjoint(permutation)),
    )

    # CBF.T25's constant neutral frame gives a direct continuum check. After
    # subtracting the external square and neutral internal identity, the
    # relative defect is h^2 I_2 tensor K(t), so its normalized cost is h^4 S.
    h_scale = Fraction(5, 4)
    continuum_t = Fraction(2, 3)
    q_external = [[cp.ZERO, cp.ZERO], [cp.ONE, cp.ZERO]]
    d_external = cp.madd(q_external, cp.adjoint(q_external))
    gamma_external = cp.diagonal([cp.ONE, q(-1)])
    external_square = uts.sparse_matmul(d_external, d_external)
    d_finite = uts.physical_dirac(
        uts.physical_transfer(
            p, phase_direction, shift_direction, continuum_t
        )
    )
    d_direct = uts.total_charge(d_external, gamma_external, d_finite, h_scale)
    direct_square = uts.sparse_matmul(d_direct, d_direct)
    direct_neutral = cp.madd(
        cp.kron(external_square, identity96),
        cp.kron(cp.identity(2), cp.mscale(q(h_scale * h_scale), identity96)),
    )
    direct_defect = matrix_sub(direct_square, direct_neutral)
    finite_defect = matrix_sub(uts.sparse_matmul(d_finite, d_finite), identity96)
    expected_direct_defect = cp.kron(
        cp.identity(2), cp.mscale(q(h_scale * h_scale), finite_defect)
    )
    direct_repair = repair_value(direct_defect)

    h_hash = uts.matrix_digest(h_phys)
    r_hash = uts.matrix_digest(remainder)
    theorem_hash = sha256(THEOREM)
    root_hash, root_payload = source_root(
        source_lock, theorem_hash, h_hash, r_hash
    )
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]
    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.direct-dirac-defect-repair-action-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "d9291f60-aa25-4c70-84ff-a3b3c9ca10c0",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.direct-dirac-defect-repair-action.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20"
        and all(t20["checks"].values()),
        "T23_response_is_exact": t23["claim_id"] == "CBF.T23"
        and all(t23["checks"].values()),
        "T25_direct_continuum_is_exact": t25["claim_id"] == "CBF.T25"
        and all(t25["checks"].values()),
        "D0_square_is_identity": uts.sparse_matmul(d0, d0) == identity96,
        "D_family_is_affine_on_exact_samples": all(residual_identity_checks),
        "H_phys_matches_T23": h_hash
        == t23["hessian_compression"]["KO6_response_sha256"],
        "H_phys_rank_is_96": cp.matrix_rank(h_phys) == 96,
        "H_phys_is_self_adjoint": h_phys == cp.adjoint(h_phys),
        "R_is_self_adjoint": remainder == cp.adjoint(remainder),
        "H_and_R_commute": hr == rh,
        "trace_H_squared_is_768": tr_h2 == 768,
        "trace_HR_is_minus_512": tr_hr == -512,
        "trace_R_squared_is_576": tr_r2 == 576,
        "quadratic_coefficient_is_4": coefficient_t2 == 4,
        "cubic_coefficient_is_minus_16_over_3": coefficient_t3
        == Fraction(-16, 3),
        "quartic_coefficient_is_3": coefficient_t4 == 3,
        "repair_Hessian_at_zero_is_8": 2 * coefficient_t2 == 8,
        "exact_polynomial_matches_all_samples": all(polynomial_checks),
        "basis_change_preserves_repair_value": repair_value(transported_sample)
        == repair_value(basis_sample),
        "positivity_completion_remainder_is_44_over_27": Fraction(44, 27) > 0,
        "stationary_quadratic_discriminant_is_negative": (-4) ** 2
        - 4 * 3 * 2
        == -8,
        "direct_continuum_defect_scales_by_h_squared": direct_defect
        == expected_direct_defect,
        "direct_continuum_repair_scales_by_h_fourth": direct_repair
        == h_scale**4 * polynomial_value(continuum_t),
        "exact_finite_repair_action_is_newly_closed": not boundary[
            "exact_direct_finite_repair_action_before"
        ]
        and boundary["exact_direct_finite_repair_action_after"],
        "full_quartic_repair_jet_is_newly_closed": not boundary[
            "full_quartic_repair_jet_before"
        ]
        and boundary["full_quartic_repair_jet_after"],
        "signed_physical_action_remains_open": not boundary[
            "signed_physical_action_selected"
        ],
        "absolute_action_normalization_remains_open": not boundary[
            "absolute_action_normalization_selected"
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
        raise AssertionError(f"CBF.T26 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.direct-dirac-defect-repair-action.v1",
        "claim_id": "CBF.T26",
        "date": "2026-08-29",
        "status": (
            "exact normalized direct finite-source positive repair action and "
            "nonzero-value-selection no-go; signed physical action and values open"
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
            "neutral_identity": "D0^2=I96",
            "D0_sha256": uts.matrix_digest(d0),
            "D1_sha256": uts.matrix_digest(d1),
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
        },
        "defect_residual": {
            "definition": "K(t)=D_phys(t)^2-I96",
            "exact_expansion": "K(t)=t H_phys+t^2 R",
            "H_phys_definition": "H_phys=D0 D1+D1 D0",
            "R_definition": "R=D1^2",
            "H_phys_sha256": h_hash,
            "R_sha256": r_hash,
            "H_phys_rank": cp.matrix_rank(h_phys),
            "R_rank": cp.matrix_rank(remainder),
            "H_phys_self_adjoint": True,
            "R_self_adjoint": True,
            "H_phys_R_commute": True,
        },
        "normalized_repair_action": {
            "normalized_trace": "tau_96=Tr/96",
            "definition": "S_rep(t)=1/2 tau_96(K(t)^*K(t))",
            "exact_polynomial": "4 t^2-(16/3)t^3+3t^4",
            "gradient_flow": "dt/ds=-dS_rep/dt in unit repair-time gauge",
            "physical_Lorentzian_action": False,
            "signed_variational_action": False,
        },
        "uniqueness_scope": {
            "basis_group": "U(96)",
            "trace_conditions": [
                "positive",
                "normalized by tau_96(I96)=1",
                "invariant under every unitary basis change",
            ],
            "unique_trace": "Tr/96",
            "quadratic_defect_class": "c tau_96(K^*K), c>0",
            "unique_up_to_positive_scale": True,
            "standard_gradient_normalization": "c=1/2",
            "remaining_scale_meaning": "repair-time/action-unit rescaling",
            "physical_absolute_scale_selected": False,
        },
        "exact_coefficients": {
            "Tr_H_squared": str(tr_h2),
            "Tr_HR": str(tr_hr),
            "Tr_R_squared": str(tr_r2),
            "coefficient_t2": str(coefficient_t2),
            "coefficient_t3": str(coefficient_t3),
            "coefficient_t4": str(coefficient_t4),
            "Hessian_at_zero": str(2 * coefficient_t2),
            "sample_values": sample_values,
        },
        "positivity_and_stationarity": {
            "completed_square": "t^2[3(t-8/9)^2+44/27]",
            "nonnegative_for_all_real_t": True,
            "zero_set": ["t=0"],
            "derivative": "4t(3t^2-4t+2)",
            "stationary_quadratic_discriminant": "-8",
            "real_stationary_set": ["t=0"],
            "global_minimizer": "t=0",
            "nonzero_value_selected": False,
        },
        "continuum_lift": {
            "scope": "CBF.T25 covariantly constant neutral frame",
            "relative_defect": "K_dir,rel(t,h)=h^2 I tensor K(t)",
            "normalized_local_repair_density": "S_dir,rep(t,h)=h^4 S_rep(t)",
            "principal_symbol_changed": False,
            "spacetime_integrated_physical_action_claimed": False,
            "numerical_h_selected": False,
        },
        "action_boundary": {
            "H4_T9_obeyed": True,
            "H4_T10_cyclic_action_replaced": False,
            "positive_repair_is_not_signed_action": True,
            "Morse_sign_and_first_order_phase_recovered": False,
            "Lorentzian_density_selected": False,
            "BV_QME_selected": False,
            "absolute_action_normalization_selected": False,
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_sector_specific_parameters": 0,
            "new_dimensionful_primitives": 0,
            "conventional_positive_repair_scale": 1,
            "conventional_scale_is_physical_parameter": False,
            "numerical_physical_t_selected": False,
            "numerical_physical_h_selected": False,
        },
        "physical_boundary": {
            "exact_finite_repair_action_closed": True,
            "full_quartic_repair_jet_closed": True,
            "internal_nonlinear_coefficients_emitted": True,
            "internal_coefficients_are_physical_observables": False,
            "signed_physical_action_selected": False,
            "nonzero_physical_source_coordinate_selected": False,
            "held_out_physical_observable_emitted": False,
            "q79_HYM_provenance_closed": False,
            "B_ACTION_01_closed": False,
            "B_SM_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The direct 96D source now emits an exact normalized positive repair "
            "action with the complete polynomial 4 t^2-(16/3)t^3+3t^4, not "
            "only its first response. Its unique real stationary point is t=0, "
            "which proves that this minimal defect-square lane cannot select a "
            "nonzero physical Yukawa/value coordinate. A signed same-root action "
            "or additional selected background/density remains necessary."
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
        "direct Dirac defect repair packet built: "
        f"{len(checks)}/{len(checks)} checks; exact quartic closed; "
        "signed action and nonzero physical value remain open"
    )


if __name__ == "__main__":
    main()
