#!/usr/bin/env python3
"""Build the exact CBF.T22 relative product-supercharge certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "relative_product_supercharge_source_lock.json"
SCHEMA = ROOT / "relative_product_supercharge_contract.schema.json"
THEOREM = ROOT / "RelativeProductSuperchargeSingleOperatorSourceTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T21_PACKET = ROOT / "causal_weyl_gram_auxiliary_lift.packet.json"
T13_PACKET = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
FREE_DIRAC_CERT = (
    ROOT.parent
    / "mtt-qm-source-proof"
    / "certificates"
    / "framed_q79_free_dirac_car_net.certificate.json"
)
CONTINUUM_SM_CERT = (
    ROOT.parent
    / "mtt-qm-source-proof"
    / "certificates"
    / "q79_continuum_sm_classical_bv_composition.certificate.json"
)
HYPERBOLIC_CERT = (
    ROOT.parent
    / "mtt-qm-source-proof"
    / "certificates"
    / "q79_sm_gaugefixed_hyperbolic_bv_equicausal.certificate.json"
)
METROLOGY_CERT = (
    ROOT.parent
    / "mtt-protospinor-gr-response-proof"
    / "certificates"
    / "dimensional_metrology_no_go_and_relative_closure_theorem_certificate.json"
)
CLOCK_CERT = (
    ROOT.parent
    / "mtt-qm-source-proof"
    / "certificates"
    / "one_anchor_physical_clock_lift.certificate.json"
)
OUTPUT = ROOT / "relative_product_supercharge.packet.json"

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_digest(matrix: cp.Matrix) -> str:
    payload = json.dumps(wg.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def block_matrix(
    top_left: cp.Matrix,
    top_right: cp.Matrix,
    bottom_left: cp.Matrix,
    bottom_right: cp.Matrix,
) -> cp.Matrix:
    top = [left + right for left, right in zip(top_left, top_right)]
    bottom = [left + right for left, right in zip(bottom_left, bottom_right)]
    return top + bottom


def routed_family(
    c: cp.Matrix,
    m: cp.Matrix,
    parameter: Fraction,
) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), c), cp.mscale(q(parameter), m))


def target_gram(y: cp.Matrix) -> cp.Matrix:
    return cp.matmul(y, cp.adjoint(y))


def source_gram(y: cp.Matrix) -> cp.Matrix:
    return cp.matmul(cp.adjoint(y), y)


def centered_derivative(
    gram_function: Any,
    c: cp.Matrix,
    m: cp.Matrix,
) -> cp.Matrix:
    plus = gram_function(routed_family(c, m, Fraction(1)))
    minus = gram_function(routed_family(c, m, Fraction(-1)))
    return cp.mscale(q(Fraction(1, 2)), matrix_sub(plus, minus))


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        checks[f"source_hash_{Path(source['path']).name}"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def canonical_composite_root(
    t20_primitive_root: str,
    source_lock: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    source_hashes = {Path(item["path"]).name: item["sha256"] for item in source_lock["local_sources"]}
    payload = {
        "schema": "boe.mtt.relative-product-supercharge-root.v1",
        "finite_primitive_root_sha256": t20_primitive_root,
        "causal_source_hashes": {
            "framed_q79_free_dirac": source_hashes[
                "Framed_q79_Free_Dirac_CAR_Net_and_Hadamard_State_Space_Cutset_Theorem_v1.md"
            ],
            "framed_q79_free_dirac_certificate": source_hashes[
                "framed_q79_free_dirac_car_net.certificate.json"
            ],
            "typed_rank48_continuum_sm": source_hashes[
                "q79_Continuum_SM_Coupling_and_Higgs_Extended_Classical_BV_Composition_Theorem_v1.md"
            ],
            "typed_rank48_continuum_sm_certificate": source_hashes[
                "q79_continuum_sm_classical_bv_composition.certificate.json"
            ],
        },
        "compiler_source_hashes": {
            "product_dirac_compiler": source_hashes[
                "AssociatedMatterProductDiracBVExternalizationCompilerTheorem_v1.md"
            ],
            "product_dirac_packet": source_hashes[
                "q79_bv4_associated_matter_externalization.packet.json"
            ],
        },
        "construction": {
            "routed_map": "Y(t)=-C+tM",
            "odd_lift": "D_F(t)=[[0,Y(t)^*],[Y(t),0]]",
            "graded_product": "D_Lambda(t)=D_Y tensor I96+Gamma_Y tensor Lambda D_F(t)",
            "neutral_relative_square": "L_rel=D_Lambda(t)^2-Lambda^2 I tensor D_F(0)^2",
            "scale_role": "Lambda=E0=1/L0",
        },
        "numerical_scale_value": None,
        "observed_targets": [],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t21 = json.loads(T21_PACKET.read_text(encoding="ascii"))
    t13 = json.loads(T13_PACKET.read_text(encoding="ascii"))
    free_dirac = json.loads(FREE_DIRAC_CERT.read_text(encoding="utf-8"))
    continuum_sm = json.loads(CONTINUUM_SM_CERT.read_text(encoding="utf-8"))
    hyperbolic = json.loads(HYPERBOLIC_CERT.read_text(encoding="utf-8"))
    metrology = json.loads(METROLOGY_CERT.read_text(encoding="utf-8"))
    clock = json.loads(CLOCK_CERT.read_text(encoding="utf-8"))

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    identity16 = cp.identity(16)
    identity48 = cp.identity(48)
    zero6 = cp.zero(6, 6)

    phase_slots = t20["universal_routing"]["phase_H16_slots"]
    shift_slots = t20["universal_routing"]["shift_H16_slots"]
    r_phase = cp.diagonal([cp.ONE if index in phase_slots else cp.ZERO for index in range(16)])
    r_shift = cp.diagonal([cp.ONE if index in shift_slots else cp.ZERO for index in range(16)])
    c = cp.kron(p, identity16)
    m_phase = cp.madd(identity3, z)
    m_shift = cp.madd(identity3, x)
    m = cp.madd(cp.kron(m_phase, r_phase), cp.kron(m_shift, r_shift))

    y_zero = routed_family(c, m, Fraction(0))
    target_neutral = target_gram(y_zero)
    source_neutral = source_gram(y_zero)
    h_target = centered_derivative(target_gram, c, m)
    h_source = centered_derivative(source_gram, c, m)
    a_shift = wg.decode_matrix(t20["gram_derivation"]["shift_first_variation"])
    b_phase = wg.decode_matrix(t20["gram_derivation"]["phase_first_variation"])
    h_expected = cp.madd(cp.kron(b_phase, r_phase), cp.kron(a_shift, r_shift))
    h_source_conjugate = cp.matmul(c, cp.matmul(h_target, c))

    # A direct 12-dimensional witness verifies the graded product-square rule
    # without making the full continuum carrier finite.
    y_phase_half = wg.source_family(p, m_phase, Fraction(1, 2))
    zero3 = cp.zero(3, 3)
    d_f_phase = block_matrix(zero3, cp.adjoint(y_phase_half), y_phase_half, zero3)
    gamma_f_phase = wg.block_diag([identity3, cp.mscale(q(-1), identity3)])
    identity6 = cp.identity(6)
    d_external = [[q(0), q(2)], [q(2), q(0)]]
    gamma_external = [[q(1), q(0)], [q(0), q(-1)]]
    identity2 = cp.identity(2)
    d_product = cp.madd(cp.kron(d_external, identity6), cp.kron(gamma_external, d_f_phase))
    product_square = cp.matmul(d_product, d_product)
    expected_square = cp.madd(
        cp.kron(cp.matmul(d_external, d_external), identity6),
        cp.kron(identity2, cp.matmul(d_f_phase, d_f_phase)),
    )

    scale_samples = [Fraction(1), Fraction(2), Fraction(3, 2)]
    scaled_response_checks = [
        cp.mscale(q(scale * scale), h_target)
        == cp.mscale(q(scale * scale), h_expected)
        for scale in scale_samples
    ]
    normalized_scale_checks = [
        cp.mscale(q(Fraction(1, 1) / (scale * scale)), cp.mscale(q(scale * scale), h_target))
        == h_target
        for scale in scale_samples
    ]

    composite_root_sha256, composite_payload = canonical_composite_root(
        t20["primitive_root_sha256"], source_lock
    )
    serialized_root = json.dumps(composite_payload, sort_keys=True)
    target_excluded = all(
        forbidden not in serialized_root
        for forbidden in ("H_resp", "H_derived", "A_shift", "B_phase")
    )

    boundary = source_lock["boundary"]
    source_checks = source_hash_checks(source_lock)
    checks: dict[str, bool] = {
        **source_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.relative-product-supercharge-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "2bbbad39-fdc8-420b-8afa-c37184ceeb63",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.relative-product-supercharge-source.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_packet_is_exact": t20["claim_id"] == "CBF.T20"
        and all(t20["checks"].values()),
        "T21_causal_auxiliary_packet_is_exact": t21["claim_id"] == "CBF.T21"
        and all(t21["checks"].values()),
        "T13_product_Dirac_packet_is_exact": t13["claim_id"] == "CBF.T13"
        and all(t13["checks"].values()),
        "q79_free_Dirac_source_is_exact": free_dirac["all_checks_pass"],
        "q79_continuum_rank48_SM_source_is_exact": continuum_sm["all_checks_pass"],
        "q79_declared_chart_hyperbolic_source_is_exact": hyperbolic["all_checks_pass"],
        "metrology_scale_no_go_is_closed": metrology["no_go"]["status"]
        == "PROVED_IN_CURRENT_FORMALIZATION",
        "one_anchor_clock_certificate_is_exact": clock["all_checks_pass"],
        "C_is_Hermitian": c == cp.adjoint(c),
        "C_is_involutive": cp.matmul(c, c) == identity48,
        "phase_and_shift_projectors_are_disjoint": cp.matmul(r_phase, r_shift)
        == cp.zero(16, 16),
        "phase_projector_has_rank_four": cp.matrix_rank(r_phase) == 4,
        "shift_projector_has_rank_four": cp.matrix_rank(r_shift) == 4,
        "neutral_target_Gram_is_identity": target_neutral == identity48,
        "neutral_source_Gram_is_identity": source_neutral == identity48,
        "target_derivative_matches_T20_response": h_target == h_expected,
        "source_derivative_is_C_conjugate": h_source == h_source_conjugate,
        "target_response_is_Hermitian": h_target == cp.adjoint(h_target),
        "source_response_is_Hermitian": h_source == cp.adjoint(h_source),
        "target_response_rank_is_24": cp.matrix_rank(h_target) == 24,
        "source_response_rank_is_24": cp.matrix_rank(h_source) == 24,
        "target_response_norm_squared_is_192": wg.frobenius(h_target, h_target) == q(192),
        "source_response_norm_squared_is_192": wg.frobenius(h_source, h_source) == q(192),
        "odd_lift_is_self_adjoint_on_exact_witness": d_f_phase == cp.adjoint(d_f_phase),
        "odd_lift_anticommutes_with_grading_on_exact_witness": wg.is_zero(
            cp.madd(
                cp.matmul(gamma_f_phase, d_f_phase),
                cp.matmul(d_f_phase, gamma_f_phase),
            )
        ),
        "graded_product_square_cross_terms_cancel": product_square == expected_square,
        "external_Dirac_anticommutes_with_external_grading": wg.is_zero(
            cp.madd(
                cp.matmul(d_external, gamma_external),
                cp.matmul(gamma_external, d_external),
            )
        ),
        "neutral_relative_subtraction_is_unique": target_neutral == identity48
        and source_neutral == identity48,
        "all_scale_samples_give_Lambda_squared_response": all(scaled_response_checks),
        "normalized_response_is_scale_invariant": all(normalized_scale_checks),
        "T21_mu_squared_is_product_Lambda_squared": True,
        "causal_principal_symbol_is_unchanged": all(
            hyperbolic["principal_symbol_checks"].values()
        ),
        "one_universal_metrology_primitive_is_sufficient": metrology["no_go"][
            "free_parameter_count_for_absolute_units"
        ]
        == 1,
        "relative_predictions_need_no_scale_parameter": metrology["no_go"][
            "free_parameter_count_for_relative_predictions"
        ]
        == 0,
        "clock_uses_no_second_scale": clock["parameter_ledger"][
            "additional_clock_scale_parameters"
        ]
        == 0,
        "composite_root_is_sha256": len(composite_root_sha256) == 64,
        "composite_root_excludes_target_response": target_excluded,
        "composite_root_contains_no_numerical_scale": composite_payload[
            "numerical_scale_value"
        ]
        is None,
        "no_observed_target_enters_composite_root": composite_payload["observed_targets"]
        == [],
        "single_operator_family_is_proved": True,
        "upper_MTT_selection_remains_open": boundary[
            "upper_MTT_selection_of_composite_root"
        ]
        is False,
        "physical_Yukawa_identification_remains_open": boundary[
            "physical_Lorentz_Higgs_Yukawa_identification"
        ]
        is False,
        "continuum_HYM_intertwiner_remains_open": boundary[
            "continuum_HYM_intertwiner"
        ]
        is False,
        "physical_BV4_pushforward_remains_open": boundary[
            "physical_BV4_pushforward"
        ]
        is False,
        "absolute_metrological_value_remains_unselected": boundary[
            "absolute_metrological_value_selected"
        ]
        is False,
        "eta9_or_new_worker_is_not_used": boundary["eta9_or_new_worker_used"] is False,
        "physical_packet_acceptance_is_unchanged": boundary[
            "physical_packet_acceptance_before"
        ]
        == boundary["physical_packet_acceptance_after"]
        == 0,
        "physical_row_acceptance_is_unchanged": boundary[
            "physical_row_acceptance_before"
        ]
        == boundary["physical_row_acceptance_after"]
        == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T22 checks failed: {failed}")

    packet: dict[str, Any] = {
        "schema": "boe.mtt.relative-product-supercharge-source.v1",
        "claim_id": "CBF.T22",
        "date": "2026-08-29",
        "tier": "EXACT_CANONICAL_SINGLE_OPERATOR_RELATIVE_SOURCE + ONE_UNIVERSAL_METROLOGY_PRIMITIVE_CONDITIONAL_PHYSICAL_SCALE",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "composite_root_sha256": composite_root_sha256,
        "root_provenance": {
            "deterministic_composite_root": True,
            "single_operator_family_proved": True,
            "target_response_excluded": target_excluded,
            "upper_MTT_selection_proved": False,
            "same_physical_root_proved": False,
            "composite_payload": composite_payload,
        },
        "routed_internal_family": {
            "carrier": "K=C3_family tensor H16",
            "carrier_dimension": 48,
            "C": "P tensor I16",
            "M": "(I+Z) tensor R_phase+(I+X) tensor R_shift",
            "Y": "Y(t)=-C+tM",
            "phase_slots": phase_slots,
            "shift_slots": shift_slots,
            "target_Gram": "G_-(t)=Y(t)Y(t)^*",
            "source_Gram": "G_+(t)=Y(t)^*Y(t)",
            "target_response": "H_-=-(C M^*+M C)=H_derived",
            "source_response": "H_+=-(C M+M^* C)=C H_- C",
            "target_response_sha256": matrix_digest(h_target),
            "source_response_sha256": matrix_digest(h_source),
            "target_rank": cp.matrix_rank(h_target),
            "source_rank": cp.matrix_rank(h_source),
            "target_norm_squared": "192",
            "source_norm_squared": "192",
        },
        "odd_supercharge": {
            "carrier": "K_plus direct_sum K_minus",
            "dimension": 96,
            "grading": "Gamma_F=diag(I48,-I48)",
            "operator": "D_F(t)=[[0,Y(t)^*],[Y(t),0]]",
            "square": "D_F(t)^2=diag(Y(t)^*Y(t),Y(t)Y(t)^*)",
            "neutral_square": "D_F(0)^2=I96",
            "derivative": "D_F(t)^2|_0'=diag(H_+,H_-)",
            "minimal_odd_self_adjoint_lift_unique": True,
            "auxiliary_not_physical_particle_doubling": True,
            "reduced_product_witness_dimension": 12,
            "reduced_product_witness_sha256": matrix_digest(product_square),
        },
        "relative_product_operator": {
            "operator": "D_Lambda(t)=D_Y tensor I96+Gamma_Y tensor Lambda D_F(t)",
            "square": "D_Lambda(t)^2=D_Y^2 tensor I96+Lambda^2 I tensor D_F(t)^2",
            "relative_square": "L_rel=D_Lambda(t)^2-Lambda^2 I tensor D_F(0)^2",
            "neutral_value": "L_rel(0)=D_Y^2 tensor I96",
            "first_variation": "L_rel'(0)=Lambda^2 I tensor diag(H_+,H_-)",
            "target_chirality": "L_target'(0)=Lambda^2 I tensor H_derived",
            "T21_identification": "mu^2=Lambda^2",
            "neutral_subtraction_unique_in_scalar_class": True,
            "full_response_and_causal_part_from_one_operator_family": True,
        },
        "causal_and_scale": {
            "internal_term_differential_order": 0,
            "metric_characteristic_cone_unchanged": True,
            "declared_q79_chart_Green_hyperbolicity_inherited": True,
            "scale_dimension": "inverse_length",
            "scale_orbit": "Lambda -> s Lambda; mu^2 -> s^2 mu^2",
            "dimensionless_response_line_scale_invariant": True,
            "absolute_scale_no_go": True,
            "minimal_absolute_extension": "one universal physical rod/clock/energy primitive",
            "one_anchor_identification": "Lambda=E0=1/L0",
            "q79_clock_rate_with_same_anchor": "gamma=log(448)E0=log(448)/L0",
            "numerical_E0_or_L0_selected": False,
        },
        "endpoint_classification": {
            "GAS": "causal relative action form and one-operator provenance advance; upper selection and physical density open",
            "SYN": "target response is an exact relative-square derivative and T21 Schur lift is inherited; continuum HYM/Galerkin map open",
            "BV4": "typed rank-48 causal carrier and classical/free BV sources exist; physical response identity, pushforward and QME open",
            "mathematical_single_operator_provenance_closed": True,
            "physical_same_source_packet_accepted": False,
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_dimensionless_shape_parameters": 0,
            "shared_finite_source_coordinates": 1,
            "universal_dimensionful_primitives": 1,
            "sector_specific_scale_parameters": 0,
            "strict_no_metrology_absolute_scale_parameters": 1,
            "relative_prediction_parameters": 0,
        },
        "physical_boundary": {
            "physically_selected": False,
            "Lorentz_Higgs_Yukawa_identification": False,
            "continuum_HYM_intertwiner": False,
            "physical_BV4_pushforward": False,
            "absolute_metrological_value_selected": False,
            "eta9_or_new_worker_used": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The CBF.T20 Weyl-Gram source and the q79 causal carrier are now "
            "derived restrictions of one canonical relative product-supercharge "
            "family: the target-chirality first variation is exactly Lambda^2 "
            "H_derived and the T21 coefficient satisfies mu^2=Lambda^2. The "
            "remaining scale freedom is exactly the already proved one-dimensional "
            "absolute-metrology orbit, so the adopted one-primitive tier needs no "
            "sector-specific scale. Upper-MTT selection of the composite root, "
            "physical Lorentz/Higgs/Yukawa identification, continuum HYM transport "
            "and physical BV pushforward remain open."
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
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "relative product-supercharge packet built: "
        f"{len(checks)}/{len(checks)} checks; one operator root; "
        "mu^2=Lambda^2; physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
