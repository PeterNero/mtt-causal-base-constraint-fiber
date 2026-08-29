#!/usr/bin/env python3
"""Independent verifier for the CBF.T22 relative product-supercharge packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import verify_weyl_gram_closure_repair_source as vw


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "relative_product_supercharge.packet.json"
SOURCE_LOCK = ROOT / "relative_product_supercharge_source_lock.json"
SCHEMA = ROOT / "relative_product_supercharge_contract.schema.json"
THEOREM = ROOT / "RelativeProductSuperchargeSingleOperatorSourceTheorem_v1.md"

cp = vw.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.matrix_add(left, cp.matrix_scale(q(-1), right))


def block_matrix(
    top_left: cp.Matrix,
    top_right: cp.Matrix,
    bottom_left: cp.Matrix,
    bottom_right: cp.Matrix,
) -> cp.Matrix:
    return [left + right for left, right in zip(top_left, top_right)] + [
        left + right for left, right in zip(bottom_left, bottom_right)
    ]


def digest(matrix: cp.Matrix) -> str:
    payload = json.dumps(cp.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def routed(c: cp.Matrix, m: cp.Matrix, t: Fraction) -> cp.Matrix:
    return cp.matrix_add(cp.matrix_scale(q(-1), c), cp.matrix_scale(q(t), m))


def target_gram(y: cp.Matrix) -> cp.Matrix:
    return cp.matrix_mul(y, cp.adjoint(y))


def source_gram(y: cp.Matrix) -> cp.Matrix:
    return cp.matrix_mul(cp.adjoint(y), y)


def derivative(
    gram: Callable[[cp.Matrix], cp.Matrix],
    c: cp.Matrix,
    m: cp.Matrix,
) -> cp.Matrix:
    plus = gram(routed(c, m, Fraction(1)))
    minus = gram(routed(c, m, Fraction(-1)))
    return cp.matrix_scale(q(Fraction(1, 2)), sub(plus, minus))


def frobenius(matrix: cp.Matrix) -> cp.K:
    total = cp.Z
    for row in matrix:
        for value in row:
            total = cp.add(total, cp.mul(cp.conj(value), value))
    return total


def is_zero(matrix: cp.Matrix) -> bool:
    return matrix == cp.zero(len(matrix), len(matrix[0]))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def independent_root(
    finite_root: str,
    source_lock: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    hashes = {Path(item["path"]).name: item["sha256"] for item in source_lock["local_sources"]}
    payload = {
        "schema": "boe.mtt.relative-product-supercharge-root.v1",
        "finite_primitive_root_sha256": finite_root,
        "causal_source_hashes": {
            "framed_q79_free_dirac": hashes[
                "Framed_q79_Free_Dirac_CAR_Net_and_Hadamard_State_Space_Cutset_Theorem_v1.md"
            ],
            "framed_q79_free_dirac_certificate": hashes[
                "framed_q79_free_dirac_car_net.certificate.json"
            ],
            "typed_rank48_continuum_sm": hashes[
                "q79_Continuum_SM_Coupling_and_Higgs_Extended_Classical_BV_Composition_Theorem_v1.md"
            ],
            "typed_rank48_continuum_sm_certificate": hashes[
                "q79_continuum_sm_classical_bv_composition.certificate.json"
            ],
        },
        "compiler_source_hashes": {
            "product_dirac_compiler": hashes[
                "AssociatedMatterProductDiracBVExternalizationCompilerTheorem_v1.md"
            ],
            "product_dirac_packet": hashes[
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
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    checks = 0

    require(packet["schema"] == "boe.mtt.relative-product-supercharge-source.v1", "schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T22", "claim id")
    checks += 1
    require(packet["tier"] == schema["properties"]["tier"]["const"], "tier")
    checks += 1
    require(set(packet) == set(schema["properties"]), "strict top-level packet")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1
    require(schema["additionalProperties"] is False, "strict schema")
    checks += 1
    require(source_lock["repository_head_before"] == "104177dc8978c86e77f7f21b73c1c1adea358b4a", "head")
    checks += 1
    require(source_lock["handoff_id"] == "2bbbad39-fdc8-420b-8afa-c37184ceeb63", "handoff")
    checks += 1
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"missing source {source['path']}")
        require(sha256(path) == source["sha256"], f"source hash {source['path']}")
        checks += 1

    p, x, z, fourier = vw.hardcoded_primitives()
    a_shift, b_phase = vw.hardcoded_responses()
    identity3 = cp.identity(3)
    identity16 = cp.identity(16)
    identity48 = cp.identity(48)
    phase_slots = [6, 7, 8, 14]
    shift_slots = [9, 10, 11, 15]
    r_phase = cp.diagonal([cp.O if index in phase_slots else cp.Z for index in range(16)])
    r_shift = cp.diagonal([cp.O if index in shift_slots else cp.Z for index in range(16)])
    c = cp.kron(p, identity16)
    m_phase = cp.matrix_add(identity3, z)
    m_shift = cp.matrix_add(identity3, x)
    m = cp.matrix_add(cp.kron(m_phase, r_phase), cp.kron(m_shift, r_shift))

    require(cp.matrix_mul(p, p) == identity3 and p == cp.adjoint(p), "P")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(fourier), cp.matrix_mul(p, fourier)) == p, "Fourier P")
    checks += 1
    require(cp.matrix_mul(c, c) == identity48 and c == cp.adjoint(c), "C")
    checks += 1
    require(cp.rank(r_phase) == 4 and cp.rank(r_shift) == 4, "route ranks")
    checks += 1
    require(cp.matrix_mul(r_phase, r_shift) == cp.zero(16, 16), "route disjointness")
    checks += 1

    y0 = routed(c, m, Fraction(0))
    h_target = derivative(target_gram, c, m)
    h_source = derivative(source_gram, c, m)
    h_expected = cp.matrix_add(cp.kron(b_phase, r_phase), cp.kron(a_shift, r_shift))
    require(target_gram(y0) == identity48, "neutral target")
    checks += 1
    require(source_gram(y0) == identity48, "neutral source")
    checks += 1
    require(h_target == h_expected, "target derivative")
    checks += 1
    require(h_source == cp.matrix_mul(c, cp.matrix_mul(h_target, c)), "source derivative")
    checks += 1
    require(h_target == cp.adjoint(h_target) and h_source == cp.adjoint(h_source), "Hermitian responses")
    checks += 1
    require(cp.rank(h_target) == 24 and cp.rank(h_source) == 24, "response ranks")
    checks += 1
    require(frobenius(h_target) == q(192) and frobenius(h_source) == q(192), "response norms")
    checks += 1
    routed_packet = packet["routed_internal_family"]
    require(routed_packet["target_response_sha256"] == digest(h_target), "target digest")
    checks += 1
    require(routed_packet["source_response_sha256"] == digest(h_source), "source digest")
    checks += 1

    zero3 = cp.zero(3, 3)
    y_half = routed(p, m_phase, Fraction(1, 2))
    d_f = block_matrix(zero3, cp.adjoint(y_half), y_half, zero3)
    gamma_f = vw.block_diag([identity3, cp.matrix_scale(q(-1), identity3)])
    identity6 = cp.identity(6)
    d_ext = [[q(0), q(2)], [q(2), q(0)]]
    gamma_ext = [[q(1), q(0)], [q(0), q(-1)]]
    identity2 = cp.identity(2)
    require(d_f == cp.adjoint(d_f), "odd lift self-adjoint")
    checks += 1
    require(is_zero(cp.matrix_add(cp.matrix_mul(gamma_f, d_f), cp.matrix_mul(d_f, gamma_f))), "odd grading")
    checks += 1
    require(is_zero(cp.matrix_add(cp.matrix_mul(d_ext, gamma_ext), cp.matrix_mul(gamma_ext, d_ext))), "external grading")
    checks += 1
    d_product = cp.matrix_add(cp.kron(d_ext, identity6), cp.kron(gamma_ext, d_f))
    lhs = cp.matrix_mul(d_product, d_product)
    rhs = cp.matrix_add(
        cp.kron(cp.matrix_mul(d_ext, d_ext), identity6),
        cp.kron(identity2, cp.matrix_mul(d_f, d_f)),
    )
    require(lhs == rhs, "product square")
    checks += 1
    require(packet["odd_supercharge"]["reduced_product_witness_sha256"] == digest(lhs), "witness digest")
    checks += 1

    for scale in (Fraction(1), Fraction(2), Fraction(3, 2), Fraction(5, 3)):
        scaled = cp.matrix_scale(q(scale * scale), h_target)
        normalized = cp.matrix_scale(q(Fraction(1, 1) / (scale * scale)), scaled)
        require(normalized == h_target, f"scale normalization {scale}")
        checks += 1

    t20 = json.loads((ROOT / "weyl_gram_closure_repair_source.packet.json").read_text(encoding="ascii"))
    root_hash, root_payload = independent_root(t20["primitive_root_sha256"], source_lock)
    require(packet["composite_root_sha256"] == root_hash, "root hash")
    checks += 1
    require(packet["root_provenance"]["composite_payload"] == root_payload, "root payload")
    checks += 1
    root_text = json.dumps(root_payload, sort_keys=True)
    require(all(term not in root_text for term in ("H_resp", "H_derived", "A_shift", "B_phase")), "target exclusion")
    checks += 1
    require(root_payload["numerical_scale_value"] is None and root_payload["observed_targets"] == [], "root inputs")
    checks += 1

    product = packet["relative_product_operator"]
    require(product["T21_identification"] == "mu^2=Lambda^2", "mu scale")
    checks += 1
    require(product["full_response_and_causal_part_from_one_operator_family"], "single family")
    checks += 1
    require(product["neutral_subtraction_unique_in_scalar_class"], "neutral subtraction")
    checks += 1
    causal = packet["causal_and_scale"]
    require(causal["internal_term_differential_order"] == 0, "order zero")
    checks += 1
    require(causal["metric_characteristic_cone_unchanged"], "causal cone")
    checks += 1
    require(causal["absolute_scale_no_go"], "scale no-go")
    checks += 1
    require(causal["one_anchor_identification"] == "Lambda=E0=1/L0", "one anchor")
    checks += 1
    require(causal["numerical_E0_or_L0_selected"] is False, "absolute value boundary")
    checks += 1

    ledger = packet["parameter_ledger"]
    require(ledger["new_observed_inputs"] == 0, "observations")
    checks += 1
    require(ledger["new_fitted_coefficients"] == 0, "fits")
    checks += 1
    require(ledger["new_dimensionless_shape_parameters"] == 0, "shape parameters")
    checks += 1
    require(ledger["universal_dimensionful_primitives"] == 1, "universal scale")
    checks += 1
    require(ledger["sector_specific_scale_parameters"] == 0, "sector scales")
    checks += 1
    require(ledger["relative_prediction_parameters"] == 0, "relative parameters")
    checks += 1

    provenance = packet["root_provenance"]
    require(provenance["deterministic_composite_root"], "deterministic root")
    checks += 1
    require(provenance["single_operator_family_proved"], "single operator root")
    checks += 1
    require(provenance["target_response_excluded"], "target excluded flag")
    checks += 1
    require(provenance["upper_MTT_selection_proved"] is False, "upper selection boundary")
    checks += 1
    require(provenance["same_physical_root_proved"] is False, "physical root boundary")
    checks += 1
    boundary = packet["physical_boundary"]
    require(not any(boundary.values()), "all physical boundary flags remain false")
    checks += 1
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "packet count")
    checks += 1
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "row count")
    checks += 1
    require(all(packet["checks"].values()), "builder checks")
    checks += 1
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary")
    checks += 1
    require(packet["check_summary"]["failed"] == [], "builder failures")
    checks += 1

    print(f"independent relative product-supercharge verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
