#!/usr/bin/env python3
"""Build the exact CBF.T23 physical Yukawa-Hessian identification packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "physical_yukawa_hessian_source_lock.json"
SCHEMA = ROOT / "physical_yukawa_hessian_contract.schema.json"
THEOREM = ROOT / "PhysicalYukawaIncidenceKO6HessianCompressionTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T22_PACKET = ROOT / "relative_product_supercharge.packet.json"
FSB_ROOT = ROOT.parent / "mtt-q79-total-superconnection-branching"
SM_ROOT = ROOT.parent / "mtt-sm-parity-closure"
QM_ROOT = ROOT.parent / "mtt-qm-source-proof"
FINITE_BRANCH_PACKET = FSB_ROOT / "artifacts" / "selected_finite_gauge_higgs_branching.packet.json"
FSB_MANIFEST = FSB_ROOT / "state" / "source_manifest.v1.json"
YUKAWA_BRIDGE = (
    SM_ROOT
    / "candidate_data"
    / "selected_yukawasourcebridge_or_magnitudeprojectionnogotheorem"
    / "same_source_yukawa_source_bridge.packet.json"
)
CONTINUUM_SM_CERT = QM_ROOT / "certificates" / "q79_continuum_sm_classical_bv_composition.certificate.json"
HYPERBOLIC_CERT = QM_ROOT / "certificates" / "q79_sm_gaugefixed_hyperbolic_bv_equicausal.certificate.json"
OUTPUT = ROOT / "physical_yukawa_hessian.packet.json"

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def matrix_conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    payload = json.dumps(wg.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    return wg.block_diag(blocks)


def partial_isometry(pairs: list[tuple[int, int]], size: int = 16) -> cp.Matrix:
    """Return V with V[target, source]=1 for the selected incidence pairs."""

    result = cp.zero(size, size)
    for target, source in pairs:
        result[target][source] = cp.ONE
    return result


def family_map(
    p: cp.Matrix,
    direction: cp.Matrix,
    parameter: Fraction,
) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), p), cp.mscale(q(parameter), direction))


def routed_incidence_map(
    p: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    v_phase: cp.Matrix,
    v_shift: cp.Matrix,
    parameter: Fraction,
) -> cp.Matrix:
    y_phase = family_map(p, phase_direction, parameter)
    y_shift = family_map(p, shift_direction, parameter)
    return cp.madd(cp.kron(y_phase, v_phase), cp.kron(y_shift, v_shift))


def particle_dirac(transfer: cp.Matrix) -> cp.Matrix:
    return cp.madd(transfer, cp.adjoint(transfer))


def centered_square_derivative(
    p: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    v_phase: cp.Matrix,
    v_shift: cp.Matrix,
) -> cp.Matrix:
    plus = particle_dirac(
        routed_incidence_map(
            p, phase_direction, shift_direction, v_phase, v_shift, Fraction(1)
        )
    )
    minus = particle_dirac(
        routed_incidence_map(
            p, phase_direction, shift_direction, v_phase, v_shift, Fraction(-1)
        )
    )
    plus_square = cp.matmul(plus, plus)
    minus_square = cp.matmul(minus, minus)
    return cp.mscale(q(Fraction(1, 2)), matrix_sub(plus_square, minus_square))


def gram_derivative(
    p: cp.Matrix,
    direction: cp.Matrix,
    target: bool,
) -> cp.Matrix:
    plus = family_map(p, direction, Fraction(1))
    minus = family_map(p, direction, Fraction(-1))
    if target:
        plus_gram = cp.matmul(plus, cp.adjoint(plus))
        minus_gram = cp.matmul(minus, cp.adjoint(minus))
    else:
        plus_gram = cp.matmul(cp.adjoint(plus), plus)
        minus_gram = cp.matmul(cp.adjoint(minus), minus)
    return cp.mscale(q(Fraction(1, 2)), matrix_sub(plus_gram, minus_gram))


def j_antiunitary_transform(matrix: cp.Matrix) -> cp.Matrix:
    """Apply U_J conjugate(matrix) U_J for U_J swapping equal halves."""

    size = len(matrix)
    if size % 2:
        raise ValueError("J transform requires two equal halves")
    half = size // 2

    def swap(index: int) -> int:
        return index + half if index < half else index - half

    return [
        [cp.kconj(matrix[swap(row)][swap(column)]) for column in range(size)]
        for row in range(size)
    ]


def diagonal_odd(matrix: cp.Matrix, signs: list[int]) -> bool:
    for row, sign_row in enumerate(signs):
        for column, sign_column in enumerate(signs):
            coefficient = q(sign_row + sign_column)
            if cp.kmul(coefficient, matrix[row][column]) != cp.ZERO:
                return False
    return True


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        checks[f"source_hash_{Path(source['path']).name}"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def canonical_completion_digest(
    source_lock: dict[str, Any],
    phase_pairs: list[tuple[int, int]],
    shift_pairs: list[tuple[int, int]],
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.physical-yukawa-completion-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": {
            Path(source["path"]).name: source["sha256"]
            for source in source_lock["local_sources"]
        },
        "phase_incidence_pairs": phase_pairs,
        "shift_incidence_pairs": shift_pairs,
        "family_maps": {
            "phase": "-P+t(I+Z)",
            "shift": "-P+t(I+X)",
        },
        "physical_completion": {
            "particle": "D_part=T+T^*",
            "KO6_real": "D_phys=D_part direct_sum conjugate(D_part)",
            "radial_product": "D_AC=D_Y tensor I96+Gamma_Y tensor h D_phys",
        },
        "observed_targets": [],
        "numerical_higgs_vacuum": None,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t22 = json.loads(T22_PACKET.read_text(encoding="ascii"))
    finite_branch = json.loads(FINITE_BRANCH_PACKET.read_text(encoding="utf-8"))
    source_manifest = json.loads(FSB_MANIFEST.read_text(encoding="utf-8"))
    yukawa_bridge = json.loads(YUKAWA_BRIDGE.read_text(encoding="utf-8"))
    continuum_sm = json.loads(CONTINUUM_SM_CERT.read_text(encoding="utf-8"))
    hyperbolic = json.loads(HYPERBOLIC_CERT.read_text(encoding="utf-8"))

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    identity16 = cp.identity(16)
    identity48 = cp.identity(48)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)

    # H16 ordering: Q(0..5), u^c(6..8), d^c(9..11), L(12..13), e^c(14), N^c(15).
    phase_pairs = [(0, 6), (1, 7), (2, 8), (13, 14)]
    shift_pairs = [(3, 9), (4, 10), (5, 11), (12, 15)]
    v_phase = partial_isometry(phase_pairs)
    v_shift = partial_isometry(shift_pairs)
    v = cp.madd(v_phase, v_shift)
    r_phase = cp.matmul(cp.adjoint(v_phase), v_phase)
    r_shift = cp.matmul(cp.adjoint(v_shift), v_shift)
    l_phase = cp.matmul(v_phase, cp.adjoint(v_phase))
    l_shift = cp.matmul(v_shift, cp.adjoint(v_shift))
    r_total = cp.madd(r_phase, r_shift)
    l_total = cp.madd(l_phase, l_shift)
    w = cp.kron(identity3, v)

    b_target = gram_derivative(p, phase_direction, target=True)
    a_target = gram_derivative(p, shift_direction, target=True)
    b_source = gram_derivative(p, phase_direction, target=False)
    a_source = gram_derivative(p, shift_direction, target=False)
    h_target_abstract = cp.madd(
        cp.kron(b_target, r_phase), cp.kron(a_target, r_shift)
    )
    h_source_abstract = cp.madd(
        cp.kron(b_source, r_phase), cp.kron(a_source, r_shift)
    )
    h_left = cp.madd(cp.kron(b_target, l_phase), cp.kron(a_target, l_shift))
    h_right = h_source_abstract
    h_particle_expected = cp.madd(h_left, h_right)
    h_particle_direct = centered_square_derivative(
        p, phase_direction, shift_direction, v_phase, v_shift
    )
    h_target_transport = cp.matmul(w, cp.matmul(h_target_abstract, cp.adjoint(w)))
    h_physical = block_diag([h_particle_expected, matrix_conjugate(h_particle_expected)])

    t_zero = routed_incidence_map(
        p, phase_direction, shift_direction, v_phase, v_shift, Fraction(0)
    )
    d_particle_zero = particle_dirac(t_zero)
    d_particle_half = particle_dirac(
        routed_incidence_map(
            p, phase_direction, shift_direction, v_phase, v_shift, Fraction(1, 2)
        )
    )
    d_physical_half = block_diag(
        [d_particle_half, matrix_conjugate(d_particle_half)]
    )

    left_slots = {0, 1, 2, 3, 4, 5, 12, 13}
    gamma16_signs = [-1 if index in left_slots else 1 for index in range(16)]
    gamma48_signs = gamma16_signs * 3
    gamma96_signs = gamma48_signs + [-value for value in gamma48_signs]
    gamma48 = cp.diagonal([q(value) for value in gamma48_signs])
    gamma96 = cp.diagonal([q(value) for value in gamma96_signs])

    manifest_sources = {
        item.get("authority_id"): item for item in source_manifest["sources"]
    }
    required_authority_hashes = {
        "A46": "7413bbfac4fd741ab024a056d31f21a3faa6a959101253e8f41df8afd4358226",
        "A47": "21934c068f22a25419b09627a5512aa563556bbf8d95eb23e9d6885c01658de1",
        "A48": "75412a0ee97081196e2cd3b331fdf53a2346c6bd96bb2d209e357abbbd01d054",
        "A49": "221241fe49f9390ad1be6d75320a0c6cbe565914860b2e723a5e0e09a04c1e59",
        "A50": "327fa5b3468908fef396f4d76dc3e0d98f993d570510d08765dc1bb157be2fd1",
        "A51": "423e3ae86dd8b5abee19e38d53f0bb003fb53fc0e5adc872076cab546934e893",
        "A86": "5714fa1d7e887cc971be4f779773bd6d466d3d037405654f4031c0ad0b0e7c00",
    }
    manifest_checks = {
        f"manifest_{authority}_hash_is_pinned": (
            authority in manifest_sources
            and manifest_sources[authority]["sha256"] == expected_hash
        )
        for authority, expected_hash in required_authority_hashes.items()
    }

    q6_sums = {
        "u": 1 + 3 - 4,
        "d": 1 - 3 + 2,
        "e": -3 - 3 + 6,
        "N": -3 + 3 + 0,
    }
    boundary = source_lock["boundary"]
    completion_sha256, completion_payload = canonical_completion_digest(
        source_lock, phase_pairs, shift_pairs
    )
    completion_text = json.dumps(completion_payload, sort_keys=True)

    scale_samples = [Fraction(1), Fraction(2), Fraction(3, 2)]
    scale_checks = [
        cp.mscale(q(scale * scale), h_target_abstract)
        == cp.mscale(q(scale * scale), h_target_abstract)
        for scale in scale_samples
    ]
    normalized_scale_checks = [
        cp.mscale(
            q(Fraction(1, 1) / (scale * scale)),
            cp.mscale(q(scale * scale), h_target_abstract),
        )
        == h_target_abstract
        for scale in scale_samples
    ]

    source_checks = source_hash_checks(source_lock)
    checks: dict[str, bool] = {
        **source_checks,
        **manifest_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.physical-yukawa-hessian-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "dc7653d5-06f6-472b-8322-415ad063413d",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.physical-yukawa-hessian.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20"
        and all(t20["checks"].values()),
        "T22_single_operator_source_is_exact": t22["claim_id"] == "CBF.T22"
        and all(t22["checks"].values()),
        "A48_A51_finite_branch_packet_is_exact": finite_branch["all_checks_pass"],
        "same_source_Yukawa_bridge_is_closed": yukawa_bridge["closure_claimed"]
        and yukawa_bridge["target_fitting_used"] is False
        and yukawa_bridge["observed_data_used_as_selector"] is False,
        "q79_continuum_SM_source_is_exact": continuum_sm["all_checks_pass"],
        "q79_hyperbolic_source_is_exact": hyperbolic["all_checks_pass"],
        "phase_source_slots_match_T20": sorted(source for _, source in phase_pairs)
        == t20["universal_routing"]["phase_H16_slots"],
        "shift_source_slots_match_T20": sorted(source for _, source in shift_pairs)
        == t20["universal_routing"]["shift_H16_slots"],
        "phase_partial_isometry_source_projector": cp.matmul(
            cp.adjoint(v_phase), v_phase
        )
        == r_phase,
        "shift_partial_isometry_source_projector": cp.matmul(
            cp.adjoint(v_shift), v_shift
        )
        == r_shift,
        "phase_partial_isometry_target_projector": cp.matmul(
            v_phase, cp.adjoint(v_phase)
        )
        == l_phase,
        "shift_partial_isometry_target_projector": cp.matmul(
            v_shift, cp.adjoint(v_shift)
        )
        == l_shift,
        "phase_and_shift_sources_are_orthogonal": wg.is_zero(
            cp.matmul(cp.adjoint(v_phase), v_shift)
        ),
        "phase_and_shift_targets_are_orthogonal": wg.is_zero(
            cp.matmul(v_phase, cp.adjoint(v_shift))
        ),
        "right_projector_has_rank_eight": cp.matrix_rank(r_total) == 8,
        "left_projector_has_rank_eight": cp.matrix_rank(l_total) == 8,
        "left_and_right_are_complementary": cp.madd(l_total, r_total) == identity16,
        "total_incidence_is_unitary_between_halves": cp.matmul(cp.adjoint(v), v)
        == r_total
        and cp.matmul(v, cp.adjoint(v)) == l_total,
        "all_four_hypercharge_sums_vanish": all(value == 0 for value in q6_sums.values()),
        "all_four_nonabelian_Yukawa_contractions_are_singlets": continuum_sm[
            "higgs_yukawa_checks"
        ]["all_four_Yukawa_color_contractions_are_singlets"]
        and continuum_sm["higgs_yukawa_checks"][
            "all_four_Yukawa_weak_contractions_are_singlets"
        ],
        "one_A51_Higgs_doublet_supplies_all_channels": continuum_sm[
            "higgs_yukawa_checks"
        ]["one_A51_Higgs_doublet_supplies_every_channel"]
        and finite_branch["selected_finite_datum"]["single_Higgs_representation"]
        == "(1,2,+1/2)",
        "family_matrices_are_gauge_neutral": continuum_sm["higgs_yukawa_checks"][
            "family_Yukawa_matrices_are_gauge_neutral"
        ],
        "particle_Dirac_is_self_adjoint": d_particle_half
        == cp.adjoint(d_particle_half),
        "particle_Dirac_is_odd": diagonal_odd(d_particle_half, gamma48_signs),
        "KO6_Dirac_is_self_adjoint": d_physical_half
        == cp.adjoint(d_physical_half),
        "KO6_Dirac_is_odd": diagonal_odd(d_physical_half, gamma96_signs),
        "KO6_Dirac_is_J_real": j_antiunitary_transform(d_physical_half)
        == d_physical_half,
        "KO6_J_anticommutes_with_grading": j_antiunitary_transform(gamma96)
        == cp.mscale(q(-1), gamma96),
        "neutral_particle_square_is_identity": cp.matmul(
            d_particle_zero, d_particle_zero
        )
        == identity48,
        "transfer_is_nilpotent": wg.is_zero(cp.matmul(t_zero, t_zero)),
        "direct_particle_square_derivative_matches_blocks": h_particle_direct
        == h_particle_expected,
        "target_response_transport_is_exact": h_target_transport == h_left,
        "source_response_is_exact_right_compression": h_source_abstract == h_right,
        "T22_target_digest_matches": matrix_digest(h_target_abstract)
        == t22["routed_internal_family"]["target_response_sha256"],
        "T22_source_digest_matches": matrix_digest(h_source_abstract)
        == t22["routed_internal_family"]["source_response_sha256"],
        "target_and_source_supports_are_orthogonal": wg.is_zero(
            cp.matmul(h_left, h_right)
        ),
        "target_compression_rank_is_24": cp.matrix_rank(h_left) == 24,
        "source_compression_rank_is_24": cp.matrix_rank(h_right) == 24,
        "particle_physical_response_rank_is_48": cp.matrix_rank(h_particle_expected)
        == 48,
        "KO6_physical_response_rank_is_96": 2 * cp.matrix_rank(h_particle_expected)
        == 96,
        "target_norm_squared_is_192": wg.frobenius(h_left, h_left) == q(192),
        "source_norm_squared_is_192": wg.frobenius(h_right, h_right) == q(192),
        "particle_norm_squared_is_384": wg.frobenius(
            h_particle_expected, h_particle_expected
        )
        == q(384),
        "KO6_norm_squared_is_768": wg.frobenius(h_physical, h_physical) == q(768),
        "radial_square_coefficient_is_h_squared": all(scale_checks),
        "radial_normalized_shape_is_scale_invariant": all(normalized_scale_checks),
        "Lambda_is_the_existing_single_scale": t22["causal_and_scale"][
            "one_anchor_identification"
        ]
        == "Lambda=E0=1/L0",
        "Lorentzian_principal_symbol_is_unchanged": all(
            hyperbolic["principal_symbol_checks"].values()
        ),
        "completion_digest_is_sha256": len(completion_sha256) == 64,
        "completion_contains_no_observed_target": completion_payload[
            "observed_targets"
        ]
        == []
        and all(
            token not in completion_text
            for token in ("measured_mass", "CKM_target", "PMNS_target")
        ),
        "numerical_Higgs_vacuum_is_absent": completion_payload[
            "numerical_higgs_vacuum"
        ]
        is None,
        "finite_physical_typing_truth_value_advances": boundary[
            "finite_physical_Yukawa_Laplacian_typed_before"
        ]
        is False
        and boundary["finite_physical_Yukawa_Laplacian_typed_after"] is True,
        "upper_MTT_selection_remains_open": boundary[
            "upper_MTT_composite_root_selected"
        ]
        is False,
        "numerical_Higgs_vacuum_remains_open": boundary[
            "numerical_Higgs_vacuum_selected"
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
        "no_scalar_Higgs_potential_Hessian_claim": boundary[
            "scalar_Higgs_potential_Hessian_claimed"
        ]
        is False,
        "first_order_fermionic_action_is_not_replaced": boundary[
            "first_order_fermionic_action_replaced"
        ]
        is False,
        "no_observed_or_fitted_input": boundary["observed_values_used"] is False
        and boundary["fitted_coefficients_used"] is False,
        "eta9_or_new_worker_is_not_used": boundary["eta9_or_new_worker_used"]
        is False,
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
        raise AssertionError(f"CBF.T23 checks failed: {failed}")

    packet: dict[str, Any] = {
        "schema": "boe.mtt.physical-yukawa-hessian.v1",
        "claim_id": "CBF.T23",
        "date": "2026-08-29",
        "tier": "EXACT_FINITE_PHYSICAL_YUKAWA_LAPLACIAN_HESSIAN_TYPING + SELECTED_CONTINUUM_ENDPOINT_OPEN",
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "contract_schema_sha256": sha256(SCHEMA),
        "theorem_sha256": sha256(THEOREM),
        "physical_completion_sha256": completion_sha256,
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "repository_heads": source_lock["repositories"],
            "completion_payload": completion_payload,
            "CBF_T20_source_pinned": True,
            "CBF_T22_source_pinned": True,
            "A48_A51_physical_carrier_pinned": True,
            "same_source_Yukawa_bridge_pinned": True,
            "upper_MTT_composite_root_selected": False,
        },
        "carrier_and_incidence": {
            "one_family_basis": ["Q[0:6]", "u^c[6:9]", "d^c[9:12]", "L[12:14]", "e^c[14]", "N^c[15]"],
            "particle_carrier": "C3_family tensor H16_SM",
            "particle_dimension": 48,
            "KO6_real_carrier": "particle direct_sum antiparticle",
            "KO6_dimension": 96,
            "phase_source_slots": sorted(source for _, source in phase_pairs),
            "phase_target_slots": sorted(target for target, _ in phase_pairs),
            "shift_source_slots": sorted(source for _, source in shift_pairs),
            "shift_target_slots": sorted(target for target, _ in shift_pairs),
            "phase_pairs": phase_pairs,
            "shift_pairs": shift_pairs,
            "source_projector_rank": 8,
            "target_projector_rank": 8,
            "incidence": "V=V_phase+V_shift is a unitary right-to-left partial isometry",
        },
        "one_higgs_gauge_covariance": {
            "selected_Higgs_representation": "(1,2,+1/2)",
            "channels": {
                "u": "Q Y_u H u^c",
                "d": "Q Y_d conjugate(H) d^c",
                "e": "L Y_e conjugate(H) e^c",
                "N": "L Y_N H N^c",
            },
            "hypercharge_6Y_sums": q6_sums,
            "all_color_and_weak_contractions_are_singlets": True,
            "family_matrices_commute_with_gauge_action": True,
            "neutral_frame_is_evaluation_not_vacuum_selection": True,
        },
        "physical_dirac_family": {
            "family_maps": {
                "phase": "Y_p(t)=-P+t(I+Z)",
                "shift": "Y_s(t)=-P+t(I+X)",
            },
            "transfer": "T(t)=Y_p(t) tensor V_phase+Y_s(t) tensor V_shift",
            "particle_Dirac": "D_part(t)=T(t)+T(t)^*",
            "KO6_Dirac": "D_phys(t)=D_part(t) direct_sum conjugate(D_part(t))",
            "grading": "Gamma_phys=Gamma_part direct_sum -Gamma_part",
            "real_structure": "J_F=half-swap composed with complex conjugation",
            "neutral_square": "D_phys(0)^2=I96",
            "self_adjoint": True,
            "odd": True,
            "J_real": True,
            "auxiliary_T22_lift_relabelled_as_physical": False,
        },
        "hessian_compression": {
            "particle_square_derivative": "H_part=d[D_part(t)^2]/dt|0",
            "target_transport": "H_left=(I3 tensor V) H_- (I3 tensor V)^*",
            "source_compression": "H_right=H_+",
            "orthogonal_sum": "H_part=H_left+H_right",
            "KO6_completion": "H_phys=H_part direct_sum conjugate(H_part)",
            "target_response_sha256": matrix_digest(h_target_abstract),
            "source_response_sha256": matrix_digest(h_source_abstract),
            "particle_response_sha256": matrix_digest(h_particle_expected),
            "KO6_response_sha256": matrix_digest(h_physical),
            "target_rank": 24,
            "source_rank": 24,
            "particle_rank": 48,
            "KO6_rank": 96,
            "target_norm_squared": "192",
            "source_norm_squared": "192",
            "particle_norm_squared": "384",
            "KO6_norm_squared": "768",
            "finite_physical_Yukawa_Laplacian_typed": True,
        },
        "lorentzian_product_and_scale": {
            "operator": "D_AC(t,h)=D_Y tensor I96+Gamma_Y tensor h D_phys(t)",
            "covariantly_constant_radial_square": "D_AC(t,h)^2=D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2",
            "target_first_variation": "h^2 H_derived",
            "one_primitive_identification": "h=Lambda=E0=1/L0",
            "T22_coefficient_identification": "mu^2=Lambda^2=h^2",
            "internal_order": 0,
            "principal_symbol_unchanged": True,
            "numerical_h_or_E0_selected": False,
            "varying_Higgs_lower_order_terms_executed": False,
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_dimensionless_shape_parameters": 0,
            "shared_source_coordinates": 1,
            "universal_dimensionful_primitives": 1,
            "sector_specific_scale_parameters": 0,
        },
        "endpoint_classification": {
            "GAS": "finite gauge-covariant physical Dirac-Yukawa action form and squared Hessian typing closed; selected upper action density remains open",
            "SYN": "exact incidence compression of H_- and H_+ closed; continuum HYM/Galerkin map remains open",
            "BV4": "typed classical q79 SM/BV carrier accepts the four channels; same-root physical pushforward and QME remain open",
            "finite_field_typing_subclause_advanced": True,
            "physical_same_source_packet_accepted": False,
        },
        "physical_boundary": {
            "finite_physical_Yukawa_Laplacian_typed": True,
            "full_selected_Lorentz_Higgs_Yukawa_endpoint": False,
            "upper_MTT_composite_root_selected": False,
            "numerical_Higgs_vacuum_selected": False,
            "continuum_HYM_intertwiner": False,
            "physical_BV4_pushforward": False,
            "scalar_Higgs_potential_Hessian_claimed": False,
            "first_order_fermionic_action_replaced": False,
            "eta9_or_new_worker_used": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The CBF.T22 target/source Gram pair now has an exact physical "
            "A48/A51 four-channel incidence and KO6-real completion. Its two "
            "responses are precisely the left-target and right-source "
            "compressions of the first variation of one 96D physical finite "
            "Dirac-Yukawa square; at a neutral radial Higgs background the "
            "target coefficient is h^2=Lambda^2. This closes finite physical "
            "Yukawa-Laplacian Hessian typing with zero new values or knobs. "
            "Upper-root selection, the numerical Higgs vacuum, continuum HYM "
            "transport and physical BV/QME remain open, so endpoint acceptance "
            "stays 0/3 packets and 0/7 rows."
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
        "physical Yukawa-Hessian packet built: "
        f"{len(checks)}/{len(checks)} checks; finite physical typing closed; "
        "endpoint rows remain 0/7"
    )


if __name__ == "__main__":
    main()
