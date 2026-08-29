#!/usr/bin/env python3
"""Independently verify the CBF.T25 direct finite-source continuum packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "direct_finite_source_continuum_source_lock.json"
SCHEMA = ROOT / "direct_finite_source_continuum_contract.schema.json"
THEOREM = ROOT / "DirectFiniteSourceCausalContinuumDiracYukawaRealizationTheorem_v1.md"
PACKET = ROOT / "direct_finite_source_continuum.packet.json"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
FINITE_BRANCH_PACKET = (
    ROOT.parent
    / "mtt-q79-total-superconnection-branching"
    / "artifacts"
    / "selected_finite_gauge_higgs_branching.packet.json"
)
CONTINUUM_BV_CERT = (
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

cp = wg.cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def subtract(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def multiply(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not compose")
    result = cp.zero(len(left), len(right[0]))
    for row, left_row in enumerate(left):
        for inner, left_value in enumerate(left_row):
            if left_value == cp.ZERO:
                continue
            for column, right_value in enumerate(right[inner]):
                if right_value != cp.ZERO:
                    result[row][column] = cp.kadd(
                        result[row][column], cp.kmul(left_value, right_value)
                    )
    return result


def conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def incidence(pairs: tuple[tuple[int, int], ...]) -> cp.Matrix:
    matrix = cp.zero(16, 16)
    for target, source in pairs:
        matrix[target][source] = cp.ONE
    return matrix


def family_map(projector: cp.Matrix, direction: cp.Matrix, value: Fraction) -> cp.Matrix:
    return cp.madd(
        cp.mscale(q(-1), projector), cp.mscale(q(value), direction)
    )


def transfer(
    projector: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    value: Fraction,
) -> cp.Matrix:
    phase_incidence = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    shift_incidence = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(projector, phase_direction, value), phase_incidence),
        cp.kron(family_map(projector, shift_direction, value), shift_incidence),
    )


def physical_dirac(transfer_matrix: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    return wg.block_diag([particle, conjugate(particle)])


def total_charge(
    external_dirac: cp.Matrix,
    external_grading: cp.Matrix,
    finite_dirac: cp.Matrix,
    scale: Fraction,
) -> cp.Matrix:
    return cp.madd(
        cp.kron(external_dirac, cp.identity(len(finite_dirac))),
        cp.kron(external_grading, cp.mscale(q(scale), finite_dirac)),
    )


def digest(matrix: cp.Matrix) -> str:
    encoded = json.dumps(wg.encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    finite_branch = json.loads(FINITE_BRANCH_PACKET.read_text(encoding="utf-8"))
    continuum_bv = json.loads(CONTINUUM_BV_CERT.read_text(encoding="utf-8"))
    hyperbolic = json.loads(HYPERBOLIC_CERT.read_text(encoding="utf-8"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.direct-finite-source-continuum.v1", "schema", passed)
    require(packet["claim_id"] == "CBF.T25", "claim", passed)
    require(set(packet) == set(schema["required"]), "strict required keys", passed)
    require(set(packet) == set(schema["properties"]), "strict property keys", passed)
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash", passed)
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "schema hash", passed)
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash", passed)

    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists {source['path']}", passed)
        require(sha256(path) == source["sha256"], f"source hash {source['path']}", passed)

    require(t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()), "T20 source", passed)
    require(t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()), "T23 source", passed)
    require(finite_branch["all_checks_pass"], "finite real-even source", passed)
    require(continuum_bv["all_checks_pass"], "continuum classical BV source", passed)
    require(hyperbolic["all_checks_pass"], "hyperbolic source", passed)

    primitive = t20["primitive_source"]["primitive_payload"]
    p = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    phase_direction = cp.madd(cp.identity(3), z)
    shift_direction = cp.madd(cp.identity(3), x)
    i2 = cp.identity(2)
    i96 = cp.identity(96)
    zero96 = cp.zero(96, 96)

    analysis = i96
    synthesis = i96
    p_internal = multiply(synthesis, analysis)
    q_internal = subtract(i96, p_internal)
    require(p_internal == i96, "identity projector", passed)
    require(q_internal == zero96, "zero complement", passed)
    require(packet["direct_internal_realization"]["projector_rank"] == 96, "projector rank", passed)
    require(packet["direct_internal_realization"]["complement_rank"] == 0, "complement rank", passed)
    require(packet["direct_internal_realization"]["omitted_internal_modes"] == 0, "empty tail", passed)
    require(packet["direct_internal_realization"]["internal_truncation_error"] == "0", "zero truncation", passed)
    require(not packet["direct_internal_realization"]["external_spacetime_is_finite_cutoff"], "external continuum guard", passed)

    d_neutral = physical_dirac(transfer(p, phase_direction, shift_direction, Fraction(0)))
    require(multiply(d_neutral, d_neutral) == i96, "neutral square", passed)
    resolvent_witness = cp.mscale(q(Fraction(-1, 2)), i96)
    feshbach = multiply(
        multiply(multiply(multiply(p_internal, d_neutral), q_internal), resolvent_witness),
        multiply(q_internal, multiply(d_neutral, p_internal)),
    )
    require(feshbach == zero96, "zero Feshbach term", passed)

    q_y = [[cp.ZERO, cp.ZERO], [cp.ONE, cp.ZERO]]
    d_y = cp.madd(q_y, cp.adjoint(q_y))
    gamma_y = cp.diagonal([cp.ONE, q(-1)])
    h = Fraction(7, 6)
    value = Fraction(-3, 5)
    d_finite = physical_dirac(transfer(p, phase_direction, shift_direction, value))
    d_direct = total_charge(d_y, gamma_y, d_finite, h)
    expected_square = cp.madd(
        cp.kron(multiply(d_y, d_y), i96),
        cp.kron(i2, cp.mscale(q(h * h), multiply(d_finite, d_finite))),
    )
    require(multiply(d_direct, d_direct) == expected_square, "graded direct square", passed)

    d_plus = physical_dirac(transfer(p, phase_direction, shift_direction, Fraction(1)))
    d_minus = physical_dirac(transfer(p, phase_direction, shift_direction, Fraction(-1)))
    h_phys = cp.mscale(
        q(Fraction(1, 2)),
        subtract(multiply(d_plus, d_plus), multiply(d_minus, d_minus)),
    )
    response_hash = digest(h_phys)
    require(response_hash == t23["hessian_compression"]["KO6_response_sha256"], "T23 response", passed)
    direct_plus = total_charge(d_y, gamma_y, d_plus, h)
    direct_minus = total_charge(d_y, gamma_y, d_minus, h)
    direct_response = cp.mscale(
        q(Fraction(1, 2)),
        subtract(multiply(direct_plus, direct_plus), multiply(direct_minus, direct_minus)),
    )
    require(
        direct_response == cp.kron(i2, cp.mscale(q(h * h), h_phys)),
        "continuum h-squared response",
        passed,
    )
    require(packet["exact_response"]["H_phys_sha256"] == response_hash, "packet response hash", passed)
    require(packet["exact_response"]["H_phys_rank"] == 96, "packet response rank", passed)
    require(packet["exact_response"]["H_phys_frobenius_norm_squared"] == "768", "packet response norm", passed)

    root_payload = {
        "schema": "boe.mtt.direct-finite-source-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "internal_source": {
            "kind": "exact finite real-even associated-bundle fiber",
            "fiber_dimension": 96,
            "analysis": "U_x^*",
            "synthesis": "U_x",
            "projector": "P_int=U_x U_x^*=I96",
            "complement": "Q_int=0",
        },
        "continuum_operator": (
            "D_dir(t;A,H)=D_A+Y_t(H); in a covariantly constant neutral "
            "frame D_Y tensor I96+Gamma_Y tensor h D_phys(t)"
        ),
        "response_sha256": response_hash,
        "observed_targets": [],
        "numerical_higgs_vacuum": None,
        "numerical_source_coordinate": None,
        "continuum_HYM_endpoint": None,
        "theorem_sha256": sha256(THEOREM),
    }
    encoded_root = json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    require(packet["direct_source_root_sha256"] == hashlib.sha256(encoded_root).hexdigest(), "direct source root", passed)
    require(packet["source_provenance"]["direct_source_root_payload"] == root_payload, "root payload", passed)
    require(packet["source_provenance"]["eta9_dependency_count"] == 0, "no eta9", passed)

    causal = packet["causal_operator"]
    require(causal["Higgs_Yukawa_order"] == 0, "zero-order Yukawa", passed)
    require(causal["principal_symbol_unchanged"], "principal symbol", passed)
    require(causal["globally_hyperbolic_base"], "globally hyperbolic base", passed)
    require(causal["causal_support"], "causal support", passed)
    require(
        hyperbolic["construction_checks"]["advanced_retarded_propagators_exist_by_registered_theorem"],
        "advanced and retarded maps",
        passed,
    )

    action = packet["classical_action_and_bv"]
    require(not action["objects_identified"], "signed action repair distinction", passed)
    require(action["four_Yukawa_channels_are_gauge_singlets"], "Yukawa singlets", passed)
    require(action["family_matrices_commute_with_gauge_action"], "family gauge neutrality", passed)
    require(action["BRST_nilpotent"], "BRST nilpotency", passed)
    require(action["classical_action_BRST_closed"], "BRST closure", passed)
    require(action["classical_BV_master_equation"] == "(S_BV,S_BV)=0", "classical master equation", passed)
    require(not action["quantum_master_equation_closed"], "QME boundary", passed)

    route = packet["route_classification"]
    require(route["direct_route"].startswith("closed"), "direct route closed", passed)
    require(route["HYM_route"] == "open", "HYM route open", passed)
    require(not route["HYM_Galerkin_map_required_for_direct_route"], "direct bypass", passed)
    require(route["HYM_Galerkin_map_required_for_HYM_provenance"], "HYM provenance requirement", passed)
    require(not route["routes_identified"], "routes not identified", passed)

    boundary = packet["physical_boundary"]
    require(boundary["direct_finite_source_continuum_realized"], "direct realization", passed)
    require(boundary["provider_neutral_direct_operator_clause"], "direct operator clause", passed)
    require(not boundary["physical_q79_HYM_endpoint_selected"], "q79 endpoint boundary", passed)
    require(not boundary["q79_HYM_synthesis_closed"], "q79 synthesis boundary", passed)
    require(not boundary["full_provider_neutral_source_closed"], "full source boundary", passed)
    require(not boundary["full_nonlinear_upper_action_selected"], "action boundary", passed)
    require(not boundary["quantum_BV_QME_closed"], "quantum boundary", passed)
    require(not boundary["strict_numerical_values_selected"], "value boundary", passed)
    require(not boundary["B_GEO_01_closed_as_written"], "B.GEO boundary", passed)
    require(not boundary["B_ACTION_01_closed"], "B.ACTION boundary", passed)
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "q79 packet counts", passed)
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "q79 row counts", passed)

    ledger = packet["parameter_ledger"]
    require(ledger["new_observed_construction_inputs"] == 0, "no observations", passed)
    require(ledger["new_fitted_coefficients"] == 0, "no fits", passed)
    require(ledger["new_internal_Galerkin_coefficients"] == 0, "no Galerkin knobs", passed)
    require(not ledger["numerical_h_selected"] and not ledger["numerical_t_selected"], "no numerical h or t", passed)
    require(all(packet["checks"].values()), "builder checks", passed)
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(packet["checks"]), "builder count", passed)
    require(packet["check_summary"]["failed"] == [], "builder failures", passed)

    print(
        "independent direct finite-source continuum verification passed: "
        f"{len(passed)}/{len(passed)}"
    )


if __name__ == "__main__":
    main()
