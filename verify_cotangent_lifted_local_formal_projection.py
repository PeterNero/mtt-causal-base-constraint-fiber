#!/usr/bin/env python3
"""Independently verify the exact CBF.T41 projection assembly packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"
SOURCE_LOCK = ROOT / "cotangent_lifted_local_formal_projection_source_lock.json"
SCHEMA = ROOT / "cotangent_lifted_local_formal_projection_contract.schema.json"
THEOREM = ROOT / "CotangentLiftedLocalFormalProjectionAssemblyAndSameRootGluingGateTheorem_v1.md"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T40_PACKET = ROOT / "source_preserving_pointed_quantum_projection.packet.json"
H4_CERT = ROOT / "../mtt-preprojection-repair-calculus/certificates/h4_cotangent_reduction_q79_bv_gate.json"
FINITE_SHELL_CERT = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_finite_shell_bv_pushforward_regulator_comparison.certificate.json"
STATE_CERT = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_local_formal_physical_state.certificate.json"
A35_CERT = ROOT / "../mtt-sm-parity-closure/certificates/selected_neutralhiggsinsertionfunctorandradialcoordinatenormalization_certificate.json"


Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_matrix(matrix: list[list[str]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in matrix]


def zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def eye(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum(a * b for a, b in zip(row, column)) for column in transpose(right)]
        for row in left
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def determinant_2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant_3(matrix: Matrix) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    packet = load_json(PACKET)
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    t40 = load_json(T40_PACKET)
    h4 = load_json(H4_CERT)
    finite_shell = load_json(FINITE_SHELL_CERT)
    state = load_json(STATE_CERT)
    a35 = load_json(A35_CERT)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    for index, source in enumerate(source_lock["local_sources"], start=1):
        source_path = (ROOT / source["path"]).resolve()
        check(
            f"locked_source_{index:02d}",
            source_path.is_file() and sha256(source_path) == source["sha256"],
        )

    provenance = packet["source_provenance"]
    check("source_lock_hash", provenance["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("schema_hash", provenance["contract_schema_sha256"] == sha256(SCHEMA))
    check("theorem_hash", provenance["theorem_sha256"] == sha256(THEOREM))
    check("handoff_id", provenance["handoff_id"] == source_lock["handoff_id"])
    check("kernel_hash", provenance["kernel_model_sha256"] == source_lock["kernel_model_sha256"])

    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("packet_claim", packet["claim_id"] == schema["properties"]["claim_id"]["const"] == "CBF.T41")
    check("closed_schema", schema["additionalProperties"] is False)
    check("all_required_fields", all(field in packet for field in schema["required"]))
    check("component_counts", packet["component_packets_assembled"] == packet["component_packets_total"] == 4)
    check("gluing_counts", packet["physical_gluing_gates_closed"] == 0 and packet["physical_gluing_gates_total"] == 3)
    check("physical_packet_counts", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("physical_row_counts", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)

    components = packet["typed_components"]
    check("four_typed_components", set(components) == {"P_state", "P_jet", "P_line", "P_BV_free"})
    check("T38_map_copy", components["P_state"]["algebra_map"] == t38["formal_q79_state_extension"]["evaluation_map"])
    check("T38_state_copy", components["P_state"]["state_map"] == t38["formal_q79_state_extension"]["extended_state"])
    check("T38_positive", components["P_state"]["positive_normalized"])
    check("T38_preferred_open", not components["P_state"]["preferred_full_state_selected"])
    check("T39_map_copy", components["P_jet"]["map"] == t39["pointed_anchor_retraction"]["R_H"])
    check("T39_identity_copy", components["P_jet"]["identities"] == t39["pointed_anchor_retraction"]["identities"])
    check("T39_not_upper_derived", not components["P_jet"]["derived_from_selected_upper_action"])
    check("A35_carrier", components["P_line"]["carrier"] == a35["H_carrier"])
    check("A35_rank", components["P_line"]["rank"] == a35["H_projector_rank"] == 1)
    check("A35_magnitude", components["P_line"]["dimensionless_insertion_magnitude"] == a35["insertion_magnitude"] == 1.0)
    check("A35_physical_action_open", components["P_line"]["physical_action_weight_closed"] == a35["physical_action_weighted_Y_nu_closed"] is False)
    check("H4_abstract_cotangent", components["P_BV_free"]["abstract_cotangent_retract_closed"] == h4["selection_boundary"]["abstract_cotangent_compatibility_closed"] is True)
    check("H4_direct_BV_open", components["P_BV_free"]["direct_internal_to_4d_BV_identification_closed"] == h4["selection_boundary"]["direct_internal_to_4d_BV_identification_closed"] is False)
    check("free_shell_status", components["P_BV_free"]["free_finite_shell_pushforward"] == finite_shell["blocker_assessment"]["B.QFT.02_free_finite_shell_QME_pushforward"])
    check("interacting_limit_open", components["P_BV_free"]["fixed_coupling_interacting_endpoint"] == finite_shell["blocker_assessment"]["B.QFT.02_interacting_fixed_coupling_Cstar_limit"] == "open")
    check("source_state_certificate", state["all_checks_pass"])
    check("source_T40_certificate", t40["check_summary"]["failed"] == [])

    product = packet["component_product"]
    check("product_not_fiber", not product["component_product_is_physical_fiber_product"])
    check("domains_unidentified", not product["component_domains_identified_by_one_map"])
    check("evaluation_not_field_projection", not product["observable_evaluation_is_covariant_BV_field_projection"])
    check("all_components_pass", product["all_component_certificates_pass"])

    promotion = packet["promotion_criterion"]
    check("criterion_iff", promotion["necessary"] and promotion["sufficient"])
    check("criterion_G0", promotion["G0_implies_SP"] == ["SP0", "SP1", "SP2", "SP3"])
    check("criterion_G1", promotion["G1_implies_SP"] == ["SP4"])
    check("criterion_G2", promotion["G2_implies_SP"] == ["SP5"])
    check("criterion_not_existence", not promotion["existence_proved"])

    witness = packet["exact_finite_witness"]
    jet = witness["action_jet_retraction"]
    point = Fraction(jet["anchor_H"])
    jet_matrix = parse_matrix(jet["jet_matrix"])
    expected_jet = []
    for derivative in range(3):
        row: list[Fraction] = []
        for power in range(5):
            if derivative == 0:
                row.append(point**power)
            elif derivative == 1:
                row.append(Fraction(0) if power == 0 else power * point ** (power - 1))
            else:
                row.append(Fraction(0) if power < 2 else power * (power - 1) * point ** (power - 2))
        expected_jet.append(row)
    projection = parse_matrix(jet["counterterm_projection_C_H"])
    remainder = parse_matrix(jet["remainder_retraction_R_H"])
    restricted = [[row[column] for column in (0, 2, 4)] for row in expected_jet]
    check("jet_point", point == Fraction(3, 2))
    check("jet_matrix_recomputed", jet_matrix == expected_jet)
    check("jet_decomposition", add(projection, remainder) == eye(5))
    check("jet_projection_idempotent", matmul(projection, projection) == projection)
    check("jet_remainder_idempotent", matmul(remainder, remainder) == remainder)
    check("jet_projection_right_inverse", matmul(jet_matrix, projection) == jet_matrix)
    check("jet_remainder_kernel", matmul(jet_matrix, remainder) == zeros(3, 5))
    check("jet_restricted_copy", parse_matrix(jet["restricted_even_jet_matrix"]) == restricted)
    check("jet_determinant", determinant_3(restricted) == 16 * point**3 == 54 == Fraction(jet["restricted_even_determinant"]))

    cotangent = witness["cotangent_contraction"]
    differential = parse_matrix(cotangent["upper_differential"])
    p = parse_matrix(cotangent["projection"])
    inclusion = parse_matrix(cotangent["inclusion"])
    homotopy = parse_matrix(cotangent["homotopy"])
    differential_hat = parse_matrix(cotangent["cotangent_differential"])
    p_hat = parse_matrix(cotangent["cotangent_projection"])
    inclusion_hat = parse_matrix(cotangent["cotangent_inclusion"])
    homotopy_hat = parse_matrix(cotangent["cotangent_homotopy"])
    omega_upper = [
        [Fraction(0)] * 4 + row for row in eye(4)
    ] + [
        [-entry for entry in row] + [Fraction(0)] * 4 for row in eye(4)
    ]
    omega_lower = [
        [Fraction(0)] * 2 + row for row in eye(2)
    ] + [
        [-entry for entry in row] + [Fraction(0)] * 2 for row in eye(2)
    ]
    check("primal_pi_recomputed", matmul(p, inclusion) == eye(2))
    check("primal_homotopy_recomputed", add(matmul(differential, homotopy), matmul(homotopy, differential)) == subtract(eye(4), matmul(inclusion, p)))
    check("primal_h_square", matmul(homotopy, homotopy) == zeros(4, 4))
    check("primal_p_h", matmul(p, homotopy) == zeros(2, 4))
    check("primal_h_i", matmul(homotopy, inclusion) == zeros(4, 2))
    check("cotangent_pi_recomputed", matmul(p_hat, inclusion_hat) == eye(4))
    check("cotangent_homotopy_recomputed", add(matmul(differential_hat, homotopy_hat), matmul(homotopy_hat, differential_hat)) == subtract(eye(8), matmul(inclusion_hat, p_hat)))
    check("cotangent_pairing_recomputed", matmul(matmul(transpose(inclusion_hat), omega_upper), inclusion_hat) == omega_lower)
    check("cotangent_Q_symplectic_recomputed", add(matmul(transpose(differential_hat), omega_upper), matmul(omega_upper, differential_hat)) == zeros(8, 8))
    check("discarded_pairing", Fraction(cotangent["discarded_pairing_before_projection"]) == 1 and Fraction(cotangent["discarded_pairing_after_projection"]) == 0)

    shell = witness["free_shell_BV"]
    q = parse_matrix(shell["Q"])
    delta = parse_matrix(shell["Delta"])
    shell_h = parse_matrix(shell["h"])
    shell_omega = [
        [Fraction(0)] * 2 + row for row in eye(2)
    ] + [
        [-entry for entry in row] + [Fraction(0)] * 2 for row in eye(2)
    ]
    lagrangian = [
        [Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1)],
    ]
    quadratic = matmul(matmul(transpose(lagrangian), shell_omega), matmul(q, lagrangian))
    check("shell_Q2_recomputed", matmul(q, q) == zeros(4, 4))
    check("shell_symplectic_recomputed", add(matmul(transpose(q), shell_omega), matmul(shell_omega, q)) == zeros(4, 4))
    check("shell_delta_recomputed", delta == add(matmul(q, transpose(q)), matmul(transpose(q), q)) == eye(4))
    check("shell_h_recomputed", shell_h == transpose(q))
    check("shell_contraction_recomputed", add(matmul(q, shell_h), matmul(shell_h, q)) == eye(4))
    check("shell_lagrangian_recomputed", matmul(matmul(transpose(lagrangian), shell_omega), lagrangian) == zeros(2, 2))
    check("shell_quadratic_copy", parse_matrix(shell["restricted_quadratic_form"]) == quadratic)
    check("shell_quadratic_det", determinant_2(quadratic) == Fraction(shell["restricted_quadratic_determinant"]) == -1)

    state_witness = witness["radial_and_matter_states"]
    moments = [point**power for power in range(5)]
    check("state_moments", [Fraction(value) for value in state_witness["radial_moments_n_0_to_4"]] == moments)
    variance = moments[2] - 2 * point * moments[1] + point**2 * moments[0]
    check("state_zero_variance", variance == Fraction(state_witness["radial_variance"]) == 0)
    check("state_density_traces", state_witness["both_states_normalized"])
    check("state_positive", state_witness["both_states_positive"])
    check("state_same_radial", state_witness["both_radial_marginals"] == "delta_H")
    check("state_sigma_distinguishes", Fraction(state_witness["omega_0_sigma_z"]) == 1 and Fraction(state_witness["omega_1_sigma_z"]) == -1)
    check("state_nonselection", not state_witness["full_state_selected_by_radial_marginal"])

    gates = packet["independent_gluing_gates"]
    common_maps = {
        "anchor": "3/2",
        "projection": [[1, 0, 0, 0], [0, 1, 0, 0]],
        "jet_determinant": 54,
    }
    alpha = canonical_hash({"root": "alpha", "maps": common_maps})
    beta = canonical_hash({"root": "beta", "maps": common_maps})
    check("G0_alpha_hash", gates["G0_same_root"]["root_alpha_sha256"] == alpha)
    check("G0_beta_hash", gates["G0_same_root"]["root_beta_sha256"] == beta)
    check("G0_hash_separation", alpha != beta and gates["G0_same_root"]["root_hashes_distinct"])
    check("G0_nonentailment", not gates["G0_same_root"]["same_root_follows_from_numeric_component_equality"])
    metric_defect = Fraction(gates["G1_physical_tangent_pairing"]["g_lower"]) - Fraction(gates["G1_physical_tangent_pairing"]["g_up"])
    check("G1_metric_defect", metric_defect == Fraction(gates["G1_physical_tangent_pairing"]["isometry_defect"]) == 3)
    check("G1_nonentailment", not gates["G1_physical_tangent_pairing"]["physical_isometry_follows_from_internal_unit_line"])
    check("G2_expectations", gates["G2_selected_interacting_state_BV"]["distinguishing_expectations"] == ["1", "-1"])
    check("G2_nonentailment", not gates["G2_selected_interacting_state_BV"]["preferred_interacting_state_follows"])

    sp = packet["SP_clause_ledger"]
    check("SP_keys", list(sp) == ["SP0", "SP1", "SP2", "SP3", "SP4", "SP5"])
    check("SP_none_physical", not any(row["physical_satisfied"] for row in sp.values()))
    check("SP0_G0", sp["SP0"]["missing_gate"] == "G0")
    check("SP4_G1", sp["SP4"]["missing_gate"] == "G1")
    check("SP5_G2", sp["SP5"]["missing_gate"] == "G2")

    boundary = packet["physical_boundary"]
    check("three_gates_open", not any([boundary["same_root_source_action_gate_closed"], boundary["physical_tangent_pairing_gate_closed"], boundary["selected_interacting_state_BV_gate_closed"]]))
    check("projection_open", not boundary["selected_physical_projection_constructed"])
    check("QJ1_open", not boundary["physical_QJ1_selected"])
    check("QJ2_open", not boundary["physical_QJ2_selected"])
    check("QJ0_open", not boundary["gravitational_QJ0_selected"])
    check("compactification_open", not boundary["complete_q79_BV_compactification_closed"])
    check("endpoint_open", not boundary["fixed_coupling_interacting_endpoint_closed"])
    check("counters_unchanged", not boundary["acceptance_counters_change"])

    ledger = packet["parameter_ledger"]
    check("zero_parameters", ledger["new_physical_continuous_parameters"] == 0)
    check("zero_selectors", ledger["new_physical_discrete_selectors"] == 0)
    check("zero_fits", ledger["new_fits"] == 0)
    check("zero_observed", ledger["new_observed_inputs"] == 0)
    check("proof_coordinates_not_inputs", not ledger["proof_coordinates_are_physical_inputs"])

    check("theorem_claim", "**Claim:** CBF.T41" in theorem_text)
    check("theorem_four_components", "The four pieces form a consistent **component product**" in theorem_text)
    check("theorem_three_gates", all(name in theorem_text for name in ["G0: same-root source/action gate", "G1: physical tangent-pairing gate", "G2: selected interacting state/BV gate"]))
    check("theorem_iff", "if and only if `G0`, `G1` and `G2`" in theorem_text)
    check("theorem_plain_projection_no_go", "plain deletion fails exactly" in theorem_text)
    check("theorem_acceptance_boundary", "physical gluing gates discharged:  0/3" in theorem_text)
    check("theorem_next_target_G0", "build `G0`" in theorem_text)

    builder_checks = packet["checks"]
    check("builder_check_count", len(builder_checks) >= 100)
    check("builder_checks_true", all(builder_checks.values()))
    check("builder_summary", packet["check_summary"]["passed"] == packet["check_summary"]["total"] == len(builder_checks))
    check("builder_failures_empty", packet["check_summary"]["failed"] == [])

    failed = sorted(name for name, passed in checks.items() if not passed)
    print(f"independent checks: {len(checks) - len(failed)}/{len(checks)}")
    if failed:
        for name in failed:
            print(f"FAILED: {name}")
        raise SystemExit(1)
    print("cotangent-lifted local-formal projection verification passed")


if __name__ == "__main__":
    main()
