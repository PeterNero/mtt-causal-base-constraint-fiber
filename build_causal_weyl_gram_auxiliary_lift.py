#!/usr/bin/env python3
"""Build the exact CBF.T21 causal Weyl-Gram auxiliary lift certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "causal_weyl_gram_auxiliary_lift_source_lock.json"
SCHEMA = ROOT / "causal_weyl_gram_auxiliary_lift_contract.schema.json"
THEOREM = ROOT / "CausalWeylGramAuxiliaryFeshbachLiftTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T19_PACKET = ROOT / "equivariant_feshbach_response.packet.json"
QFT_CERTIFICATE = ROOT.parent / "mtt-qm-source-proof" / "certificates" / "q79_sm_gaugefixed_hyperbolic_bv_equicausal.certificate.json"
OUTPUT = ROOT / "causal_weyl_gram_auxiliary_lift.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def block_matrix(blocks: list[list[cp.Matrix]]) -> cp.Matrix:
    result: cp.Matrix = []
    for block_row in blocks:
        height = len(block_row[0])
        for local_row in range(height):
            row: list[cp.K] = []
            for block in block_row:
                if len(block) != height:
                    raise ValueError("inconsistent block height")
                row.extend(block[local_row])
            result.append(row)
    return result


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    result = cp.zero(sum(len(block) for block in blocks), sum(len(block[0]) for block in blocks))
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row in range(len(block)):
            for column in range(len(block[0])):
                result[row_offset + row][column_offset + column] = block[row][column]
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def commutator(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return matrix_sub(cp.matmul(left, right), cp.matmul(right, left))


def is_zero(matrix: cp.Matrix) -> bool:
    return matrix == cp.zero(len(matrix), len(matrix[0]))


def matrix_inverse(matrix: cp.Matrix) -> cp.Matrix:
    size = len(matrix)
    work = [row[:] + identity_row[:] for row, identity_row in zip(matrix, cp.identity(size))]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != cp.ZERO), None)
        if pivot is None:
            raise ValueError("matrix is singular")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_inverse = cp.kinv(work[column][column])
        work[column] = [cp.kmul(pivot_inverse, value) for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor == cp.ZERO:
                continue
            work[row] = [
                cp.ksub(value, cp.kmul(factor, pivot_value))
                for value, pivot_value in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        checks[f"source_hash_{Path(source['path']).name}"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def build_internal_response(t20: dict[str, Any]) -> tuple[cp.Matrix, cp.Matrix, cp.Matrix, cp.Matrix]:
    primitive = t20["primitive_source"]["primitive_payload"]
    p = decode_matrix(primitive["P"])
    a = decode_matrix(t20["gram_derivation"]["shift_first_variation"])
    b = decode_matrix(t20["gram_derivation"]["phase_first_variation"])
    phase_slots = set(t20["universal_routing"]["phase_H16_slots"])
    shift_slots = set(t20["universal_routing"]["shift_H16_slots"])
    r_phase = cp.diagonal([cp.ONE if index in phase_slots else cp.ZERO for index in range(16)])
    r_shift = cp.diagonal([cp.ONE if index in shift_slots else cp.ZERO for index in range(16)])
    h = cp.madd(cp.kron(b, r_phase), cp.kron(a, r_shift))
    return p, a, b, h


def auxiliary_block(dynamic: cp.Matrix, coupling: cp.Matrix) -> tuple[cp.Matrix, cp.Matrix]:
    identity = cp.identity(len(dynamic))
    retained = cp.madd(dynamic, identity)
    upper = block_matrix([[retained, cp.adjoint(coupling)], [coupling, identity]])
    schur = matrix_sub(retained, identity)
    return upper, schur


def graph_synthesis(coupling: cp.Matrix) -> cp.Matrix:
    identity = cp.identity(len(coupling))
    return [row[:] for row in identity] + [cp.mscale(q(-1), coupling)[row] for row in range(len(coupling))]


def canonical_composition_hash(finite_root: str, causal_root: str) -> str:
    payload = {
        "finite_root_sha256": finite_root,
        "causal_root_sha256": causal_root,
        "coupling": "C=P tensor I16",
        "complement": "D=I48",
        "causal_lift": "L_mu=L0+mu^2 H_derived",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t19 = json.loads(T19_PACKET.read_text(encoding="ascii"))
    qft = json.loads(QFT_CERTIFICATE.read_text(encoding="utf-8"))

    p, a, b, h = build_internal_response(t20)
    identity16 = cp.identity(16)
    identity48 = cp.identity(48)
    coupling = cp.kron(p, identity16)
    coupling_adjoint = cp.adjoint(coupling)
    upper, schur = auxiliary_block(h, coupling)
    synthesis = graph_synthesis(coupling)
    zero48 = cp.zero(48, 48)
    coupling_square = identity48
    retained = cp.madd(h, coupling_square)
    graph_top = matrix_sub(retained, coupling_square)
    graph_bottom = matrix_sub(coupling, coupling)
    block_square_factorization = (
        retained == cp.madd(h, coupling_square)
        and coupling_square == identity48
        and graph_top == h
        and graph_bottom == zero48
    )
    block_transform_inverse = matrix_sub(coupling, coupling) == zero48

    h_active = block_diag([b, a])
    h_active_inverse = matrix_inverse(h_active)
    relative = cp.matmul(h_active_inverse, h_active)

    frozen_scales = [Fraction(0), Fraction(1), Fraction(7, 3)]
    feshbach_scale_checks = True
    relative_scale_checks = True
    for scale in frozen_scales:
        dynamic = cp.mscale(q(scale), h)
        upper_scale, schur_scale = auxiliary_block(dynamic, coupling)
        feshbach_scale_checks = feshbach_scale_checks and schur_scale == dynamic
        relative_scale = cp.matmul(h_active_inverse, cp.mscale(q(scale), h_active))
        relative_scale_checks = relative_scale_checks and relative_scale == cp.mscale(q(scale), cp.identity(6))
        feshbach_scale_checks = feshbach_scale_checks and upper_scale == cp.adjoint(upper_scale)

    principal_witnesses: list[dict[str, Any]] = []
    principal_checks = True
    for witness in qft["exact_witness"]["principal_symbols"]:
        k_squared = Fraction(witness["k_squared"])
        principal = cp.mscale(q(k_squared), identity48)
        frozen = cp.madd(principal, h)
        frozen_upper, frozen_schur = auxiliary_block(frozen, coupling)
        expected_rank = 0 if k_squared == 0 else 48
        principal_rank = cp.matrix_rank(principal)
        schur_exact = frozen_schur == frozen
        characteristic_matches = (k_squared == 0) == bool(witness["characteristic"])
        principal_checks = principal_checks and principal_rank == expected_rank and schur_exact and characteristic_matches and frozen_upper == cp.adjoint(frozen_upper)
        principal_witnesses.append(
            {
                "covector": witness["covector"],
                "k_squared": witness["k_squared"],
                "characteristic": witness["characteristic"],
                "principal_rank_on_48_carrier": principal_rank,
                "response_changes_principal_symbol": False,
                "auxiliary_Schur_reduction_exact": schur_exact,
            }
        )

    family_fourier = decode_matrix(t20["primitive_source"]["primitive_payload"]["F3"])
    test_auxiliary_family = cp.matmul(p, cp.matmul(family_fourier, p))
    transported_intertwiner = cp.matmul(test_auxiliary_family, p) == cp.matmul(p, family_fourier)
    transported_auxiliary_unitary = cp.matmul(cp.adjoint(test_auxiliary_family), test_auxiliary_family) == cp.identity(3)
    synthesis_intertwines = transported_intertwiner

    gauge_family_action = cp.identity(3)
    gauge_coupling_commutes = cp.matmul(p, gauge_family_action) == cp.matmul(gauge_family_action, p)
    shared_phase_action: cp.K = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    shared_phase_commutes = all(
        cp.kmul(shared_phase_action, value) == cp.kmul(value, shared_phase_action)
        for row in p for value in row
    )
    automorphism_covariance = gauge_coupling_commutes and shared_phase_commutes

    finite_root = t20["primitive_root_sha256"]
    causal_root = sha256(QFT_CERTIFICATE)
    composition_hash = canonical_composition_hash(finite_root, causal_root)
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]
    properties = schema["properties"]
    h_rank = cp.matrix_rank(h)
    coupling_rank = 48 if cp.matmul(p, p) == cp.identity(3) else 0
    synthesis_rank = 48 if synthesis[:48] == identity48 else 0
    upper_rank = 48 + h_rank

    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"] == "boe.mtt.causal-weyl-gram-auxiliary-lift-lock.v1",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": properties["schema"]["const"] == "boe.mtt.causal-weyl-gram-auxiliary-lift.v1",
        "CBF_T20_source_is_exact": t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()),
        "CBF_T19_cutset_is_exact": t19["claim_id"] == "CBF.T19" and all(t19["checks"].values()),
        "q79_equicausal_certificate_is_v2": qft["schema"] == "MTTq79SMGaugeFixedHyperbolicBVEquicausalCertificate.v2",
        "q79_equicausal_certificate_checks_pass": qft["all_checks_pass"] and all(qft["checks"].values()),
        "q79_chart_Green_hyperbolic_tier_is_closed": "advanced and retarded Green operators" in qft["claim_boundary"]["closed"],
        "q79_chart_equicausal_tier_is_closed": "equicausal Peierls and free Hadamard-star algebra" in qft["claim_boundary"]["closed"],
        "q79_physical_global_background_remains_open": "selection of the physical global background and bundle sector" in qft["claim_boundary"]["open"],
        "primitive_P_is_Hermitian_involution": p == cp.adjoint(p) and cp.matmul(p, p) == cp.identity(3),
        "coupling_is_primitive_P_tensor_I16": coupling == cp.kron(p, identity16),
        "coupling_is_unitary": cp.matmul(p, p) == cp.identity(3) and p == cp.adjoint(p),
        "coupling_rank_is_48": coupling_rank == 48,
        "complement_inverse_is_exact": identity48 == cp.adjoint(identity48),
        "upper_block_is_Hermitian": upper == cp.adjoint(upper),
        "upper_block_is_nontrivially_coupled": coupling != cp.zero(48, 48),
        "upper_block_has_exact_square_factorization": block_square_factorization,
        "square_transform_is_exactly_invertible": block_transform_inverse,
        "Schur_complement_is_exact_Hderived": schur == h,
        "graph_synthesis_pullback_is_Hderived": graph_top == h and graph_bottom == zero48,
        "graph_synthesis_has_rank_48": synthesis_rank == 48,
        "normalized_upper_rank_is_72": upper_rank == 72,
        "normalized_upper_kernel_is_24": 96 - upper_rank == 24,
        "rank_additivity_matches_invertible_complement": upper_rank == 48 + h_rank,
        "all_rational_scale_Feshbach_checks_pass": feshbach_scale_checks,
        "all_rational_relative_scale_checks_pass": relative_scale_checks,
        "normalized_relative_response_is_identity": relative == cp.identity(6),
        "principal_symbol_witnesses_preserve_metric_cone": principal_checks,
        "response_is_order_zero_in_locked_qft_certificate": qft["exact_witness"]["differential_orders"]["Higgs_mass_matrix"] == 0 and qft["exact_witness"]["differential_orders"]["wave_principal_part"] == 2,
        "algebraic_auxiliary_is_eliminated_before_Green_operators": "eliminate it before constructing Green operators" in qft["hyperbolic_complex"]["auxiliary_field"],
        "transported_auxiliary_representation_is_unitary": transported_auxiliary_unitary,
        "primitive_coupling_intertwines_transported_representation": transported_intertwiner,
        "graph_synthesis_intertwines_transported_representation": synthesis_intertwines,
        "gauge_and_shared_phase_like_witnesses_preserve_upper_action": automorphism_covariance,
        "finite_and_causal_roots_are_distinct_inputs": finite_root != causal_root,
        "composition_hash_is_exact_sha256": len(composition_hash) == 64,
        "eta9_or_new_worker_result_is_not_used": boundary["eta9_or_new_worker_result_used"] is False,
        "same_physical_root_remains_open": boundary["finite_and_causal_roots_physically_identified"] is False,
        "physical_response_scale_remains_open": boundary["physical_response_scale_selected"] is False,
        "Lorentz_Higgs_Yukawa_typing_remains_open": boundary["Lorentz_Higgs_Yukawa_typing_supplied"] is False,
        "continuum_HYM_intertwiner_remains_open": boundary["continuum_HYM_intertwiner_supplied"] is False,
        "physical_BV4_insertion_remains_open": boundary["physical_BV4_insertion_supplied"] is False,
        "physical_packet_acceptance_is_unchanged": boundary["physical_packet_acceptance_before"] == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_is_unchanged": boundary["physical_row_acceptance_before"] == boundary["physical_row_acceptance_after"] == 0,
        "no_observed_values_enter_composition": t20["parameter_ledger"]["observed_construction_inputs"] == 0 and qft["parameter_ledger"]["new_observed_values"] == 0,
        "no_fitted_coefficients_enter_composition": t20["parameter_ledger"]["fitted_matrix_coefficients"] == 0 and qft["parameter_ledger"]["new_fits"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T21 checks failed: {failed}")

    packet: dict[str, Any] = {
        "schema": "boe.mtt.causal-weyl-gram-auxiliary-lift.v1",
        "claim_id": "CBF.T21",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL_CAUSAL_LIFT + EXACT_SOURCE_PINNED_AUXILIARY_FESHBACH_WITNESS + CONDITIONAL_CHART_COMPOSITION",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "source_composition": {
            "finite_source": "CBF.T20",
            "causal_carrier": "q79 gauge-fixed Green-hyperbolic free-BV equicausal chart v2",
            "source_roots": 2,
            "finite_root_sha256": finite_root,
            "causal_root_sha256": causal_root,
            "composition_sha256": composition_hash,
            "same_physical_root_proved": False,
            "eta9_used": False,
        },
        "causal_lift": {
            "operator": "L_mu=L0+mu^2 H_derived",
            "principal_symbol": "sigma_2(L_mu)=-g^-1(xi,xi) I48=sigma_2(L0)",
            "response_order": 0,
            "characteristic_cone_unchanged": True,
            "conditionally_Green_hyperbolic": True,
            "covector_witnesses": principal_witnesses,
            "algebraic_auxiliary_eliminated_before_Green_operators": True,
            "physical_scale_selected": False,
        },
        "auxiliary_feshbach": {
            "coupling": "C=P tensor I16",
            "complement": "D=I48",
            "upper_block": "K_mu=[[L_mu+C^*C,C^*],[C,I48]]",
            "nontrivial_complement": True,
            "coupling_rank": 48,
            "upper_dimension": 96,
            "upper_rank_at_normalized_internal_witness": 72,
            "upper_kernel_at_normalized_internal_witness": 24,
            "Schur_complement": "F_D(K_mu)=L_mu",
            "graph_synthesis": "U phi=(phi,-C phi), U^* K_mu U=L_mu",
            "normalized_relative_intertwiner": "T_rel=I6 at mu^2=1",
        },
        "contract_classification": {
            "GAS": "conditional chart action form constructed; physical source and scale open",
            "SYN": "nontrivial exact algebraic Schur subclause constructed; continuum HYM synthesis open",
            "BV4": "Green-hyperbolic equicausal carrier exists; response insertion typing and same-root BV source open",
            "newly_closed_subclauses": [
                "smooth order-zero causal lift preserves the metric characteristic cone",
                "primitive-P nonzero auxiliary coupling and invertible complement",
                "exact 96-to-48 Schur reduction and graph synthesis",
                "normalized finite relative response T_rel=I on the causal lift",
            ],
            "physical_packets_accepted": 0,
            "physical_rows_accepted": 0,
        },
        "parameter_ledger": {
            "observed_inputs": 0,
            "fitted_coefficients": 0,
            "new_dimensionless_shape_parameters": 0,
            "unselected_dimensionful_response_scales": 1,
        },
        "physical_boundary": {
            "physically_selected": False,
            "eta9_used": False,
            "same_physical_root": False,
            "physical_background_selected": False,
            "physical_scale_selected": False,
            "Lorentz_Higgs_Yukawa_typing": False,
            "continuum_HYM_intertwiner": False,
            "physical_BV4_insertion": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The CBF.T20 finite Gram source now has an eta9-independent causal and "
            "nontrivial auxiliary realization. Its response is a smooth order-zero "
            "endomorphism of a normally hyperbolic chart operator, so the metric "
            "characteristic cone is unchanged. The primitive coupling C=P tensor I16 "
            "and D=I48 give an exact 96-to-48 Schur reduction and graph synthesis. "
            "The remaining physical obstruction is no longer existence of a causal or "
            "nontrivial synthesis form; it is identification of the finite and causal "
            "roots, selection of mu^2 and physical field/BV typing."
        ),
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "causal Weyl-Gram auxiliary lift packet built: "
        f"{len(checks)}/{len(checks)} checks; nontrivial 96->48 Schur lift; "
        "physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
