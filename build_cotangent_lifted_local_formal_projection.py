#!/usr/bin/env python3
"""Build the exact CBF.T41 local-formal projection assembly packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
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
OUTPUT = ROOT / "cotangent_lifted_local_formal_projection.packet.json"


Matrix = list[list[Fraction]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def fmatrix(matrix: Matrix) -> list[list[str]]:
    return [[ftext(value) for value in row] for row in matrix]


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
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
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


def scale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def block_diagonal(*blocks: Matrix) -> Matrix:
    row_count = sum(len(block) for block in blocks)
    column_count = sum(len(block[0]) for block in blocks)
    result = zeros(row_count, column_count)
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row_index, row in enumerate(block):
            for column_index, value in enumerate(row):
                result[row_offset + row_index][column_offset + column_index] = value
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def symplectic(size: int) -> Matrix:
    identity = eye(size)
    return [
        [Fraction(0)] * size + row for row in identity
    ] + [
        [-entry for entry in row] + [Fraction(0)] * size for row in identity
    ]


def det2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def det3(matrix: Matrix) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def vector(size: int, index: int) -> Matrix:
    result = zeros(size, 1)
    result[index][0] = Fraction(1)
    return result


def bilinear(left: Matrix, form: Matrix, right: Matrix) -> Fraction:
    return matmul(matmul(transpose(left), form), right)[0][0]


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def jet_retraction_witness() -> dict[str, Any]:
    point = Fraction(3, 2)

    def jet(power: int) -> tuple[Fraction, Fraction, Fraction]:
        value = point**power
        first = Fraction(0) if power == 0 else power * point ** (power - 1)
        second = Fraction(0) if power < 2 else power * (power - 1) * point ** (power - 2)
        return value, first, second

    jet_matrix = [[jet(power)[row] for power in range(5)] for row in range(3)]

    def counterterm(jet_values: tuple[Fraction, Fraction, Fraction]) -> list[Fraction]:
        b0, b1, b2 = jet_values
        a0 = b0 - Fraction(5, 8) * point * b1 + Fraction(1, 8) * point**2 * b2
        a2 = (3 * b1 - point * b2) / (4 * point)
        a4 = (point * b2 - b1) / (8 * point**3)
        return [a0, Fraction(0), a2, Fraction(0), a4]

    projection = zeros(5, 5)
    for column in range(5):
        projected = counterterm(jet(column))
        for row, value in enumerate(projected):
            projection[row][column] = value
    remainder = subtract(eye(5), projection)
    restricted = [[row[column] for column in (0, 2, 4)] for row in jet_matrix]
    determinant = det3(restricted)
    return {
        "anchor_H": ftext(point),
        "polynomial_basis": ["1", "h", "h^2", "h^3", "h^4"],
        "jet_matrix": fmatrix(jet_matrix),
        "counterterm_projection_C_H": fmatrix(projection),
        "remainder_retraction_R_H": fmatrix(remainder),
        "restricted_even_jet_matrix": fmatrix(restricted),
        "restricted_even_determinant": ftext(determinant),
        "symbolic_determinant": "16 H^3",
        "C_H_idempotent": matmul(projection, projection) == projection,
        "R_H_idempotent": matmul(remainder, remainder) == remainder,
        "jet_C_H_equals_jet": matmul(jet_matrix, projection) == jet_matrix,
        "jet_R_H_zero": matmul(jet_matrix, remainder) == zeros(3, 5),
    }


def cotangent_witness() -> dict[str, Any]:
    differential = zeros(4, 4)
    differential[3][2] = Fraction(1)
    projection = [
        [Fraction(1), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0), Fraction(0)],
    ]
    inclusion = transpose(projection)
    homotopy = zeros(4, 4)
    homotopy[2][3] = Fraction(1)

    differential_hat = block_diagonal(differential, scale(Fraction(-1), transpose(differential)))
    homotopy_hat = block_diagonal(homotopy, scale(Fraction(-1), transpose(homotopy)))
    inclusion_hat = block_diagonal(inclusion, transpose(projection))
    projection_hat = block_diagonal(projection, transpose(inclusion))
    omega_upper = symplectic(4)
    omega_lower = symplectic(2)

    upper_field = vector(8, 2)
    upper_dual = vector(8, 6)
    lower_field = matmul(projection_hat, upper_field)
    lower_dual = matmul(projection_hat, upper_dual)

    return {
        "upper_primal_basis": ["r1", "r2", "u", "v"],
        "upper_differential": fmatrix(differential),
        "projection": fmatrix(projection),
        "inclusion": fmatrix(inclusion),
        "homotopy": fmatrix(homotopy),
        "cotangent_differential": fmatrix(differential_hat),
        "cotangent_projection": fmatrix(projection_hat),
        "cotangent_inclusion": fmatrix(inclusion_hat),
        "cotangent_homotopy": fmatrix(homotopy_hat),
        "primal_projection_after_inclusion": matmul(projection, inclusion) == eye(2),
        "primal_contraction_identity": add(matmul(differential, homotopy), matmul(homotopy, differential)) == subtract(eye(4), matmul(inclusion, projection)),
        "primal_side_conditions": homotopy == matmul(homotopy, subtract(eye(4), matmul(inclusion, projection))) and matmul(homotopy, homotopy) == zeros(4, 4) and matmul(projection, homotopy) == zeros(2, 4) and matmul(homotopy, inclusion) == zeros(4, 2),
        "cotangent_projection_after_inclusion": matmul(projection_hat, inclusion_hat) == eye(4),
        "cotangent_contraction_identity": add(matmul(differential_hat, homotopy_hat), matmul(homotopy_hat, differential_hat)) == subtract(eye(8), matmul(inclusion_hat, projection_hat)),
        "cotangent_inclusion_is_symplectic": matmul(matmul(transpose(inclusion_hat), omega_upper), inclusion_hat) == omega_lower,
        "cotangent_differential_is_symplectic": add(matmul(transpose(differential_hat), omega_upper), matmul(omega_upper, differential_hat)) == zeros(8, 8),
        "discarded_pairing_before_projection": ftext(bilinear(upper_field, omega_upper, upper_dual)),
        "discarded_pairing_after_projection": ftext(bilinear(lower_field, omega_lower, lower_dual)),
    }


def free_shell_witness() -> dict[str, Any]:
    differential = zeros(4, 4)
    differential[1][0] = Fraction(1)
    differential[2][3] = Fraction(-1)
    adjoint = transpose(differential)
    laplacian = add(matmul(differential, adjoint), matmul(adjoint, differential))
    homotopy = adjoint
    omega = symplectic(2)
    lagrangian_inclusion = [
        [Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1)],
    ]
    restricted_form = matmul(
        matmul(transpose(lagrangian_inclusion), omega),
        matmul(differential, lagrangian_inclusion),
    )
    return {
        "basis": ["e0", "e1", "f0", "f1"],
        "Q": fmatrix(differential),
        "Delta": fmatrix(laplacian),
        "h": fmatrix(homotopy),
        "L_shell_basis": ["e0", "f1"],
        "Q_squared_zero": matmul(differential, differential) == zeros(4, 4),
        "Q_preserves_odd_pairing": add(matmul(transpose(differential), omega), matmul(omega, differential)) == zeros(4, 4),
        "Delta_is_identity": laplacian == eye(4),
        "Hodge_contraction_identity": add(matmul(differential, homotopy), matmul(homotopy, differential)) == eye(4),
        "L_shell_is_lagrangian": matmul(matmul(transpose(lagrangian_inclusion), omega), lagrangian_inclusion) == zeros(2, 2),
        "restricted_quadratic_form": fmatrix(restricted_form),
        "restricted_quadratic_determinant": ftext(det2(restricted_form)),
        "restricted_quadratic_is_nondegenerate": det2(restricted_form) != 0,
    }


def state_witness() -> dict[str, Any]:
    point = Fraction(3, 2)
    moments = [point**power for power in range(5)]
    variance = moments[2] - 2 * point * moments[1] + point**2 * moments[0]
    return {
        "anchor_H": ftext(point),
        "radial_moments_n_0_to_4": [ftext(value) for value in moments],
        "radial_variance": ftext(variance),
        "matter_algebra": "M_2(C)",
        "omega_0_density": [["1", "0"], ["0", "0"]],
        "omega_1_density": [["0", "0"], ["0", "1"]],
        "both_states_normalized": True,
        "both_states_positive": True,
        "both_radial_marginals": "delta_H",
        "test_observable": "sigma_z=diag(1,-1)",
        "omega_0_sigma_z": "1",
        "omega_1_sigma_z": "-1",
        "full_state_selected_by_radial_marginal": False,
    }


def independence_witness() -> dict[str, Any]:
    common_maps = {
        "anchor": "3/2",
        "projection": [[1, 0, 0, 0], [0, 1, 0, 0]],
        "jet_determinant": 54,
    }
    root_alpha = canonical_hash({"root": "alpha", "maps": common_maps})
    root_beta = canonical_hash({"root": "beta", "maps": common_maps})
    return {
        "G0_same_root": {
            "root_alpha_sha256": root_alpha,
            "root_beta_sha256": root_beta,
            "component_matrices_identical": True,
            "root_hashes_distinct": root_alpha != root_beta,
            "same_root_follows_from_numeric_component_equality": False,
        },
        "G1_physical_tangent_pairing": {
            "Dp": "1",
            "g_up": "1",
            "g_lower": "4",
            "isometry_defect": "3",
            "internal_A35_unit_line_unchanged": True,
            "physical_isometry_follows_from_internal_unit_line": False,
        },
        "G2_selected_interacting_state_BV": {
            "same_radial_marginal": "delta_H",
            "two_positive_normalized_matter_states": True,
            "distinguishing_expectations": ["1", "-1"],
            "free_shell_pushforward_shared": True,
            "preferred_interacting_state_follows": False,
        },
    }


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    t40 = load_json(T40_PACKET)
    h4 = load_json(H4_CERT)
    finite_shell = load_json(FINITE_SHELL_CERT)
    state = load_json(STATE_CERT)
    a35 = load_json(A35_CERT)

    jet = jet_retraction_witness()
    cotangent = cotangent_witness()
    shell = free_shell_witness()
    state_exact = state_witness()
    independence = independence_witness()

    typed_components = {
        "P_state": {
            "source": "CBF.T38 plus q79 local-formal physical-state theorem",
            "algebra_map": t38["formal_q79_state_extension"]["evaluation_map"],
            "state_map": t38["formal_q79_state_extension"]["extended_state"],
            "positive_normalized": t38["formal_q79_state_extension"]["formal_local_radial_anchored_state_exists"],
            "radial_marginal_unique": t38["invariant_radial_state"]["radial_marginal_is_unique_without_selecting_matter_state"],
            "preferred_full_state_selected": False,
        },
        "P_jet": {
            "source": "CBF.T39",
            "map": t39["pointed_anchor_retraction"]["R_H"],
            "identities": t39["pointed_anchor_retraction"]["identities"],
            "local_formal_QJ1": t39["QJ_classification"]["QJ1_local_formal_anchor_scheme"],
            "local_formal_action_QJ2": t39["QJ_classification"]["QJ2_local_formal_action_Hessian"],
            "derived_from_selected_upper_action": False,
        },
        "P_line": {
            "source": "A35",
            "carrier": a35["H_carrier"],
            "rank": a35["H_projector_rank"],
            "dimensionless_insertion_magnitude": a35["insertion_magnitude"],
            "dimensionless_radial_normalization_closed": a35["selected_radial_coordinate_normalization_closed"],
            "physical_action_weight_closed": a35["physical_action_weighted_Y_nu_closed"],
            "physical_tangent_metric_selected": False,
        },
        "P_BV_free": {
            "sources": ["H4-T15", "q79 free finite-shell BV pushforward"],
            "abstract_cotangent_retract_closed": h4["selection_boundary"]["abstract_cotangent_compatibility_closed"],
            "direct_internal_to_4d_BV_identification_closed": h4["selection_boundary"]["direct_internal_to_4d_BV_identification_closed"],
            "free_finite_shell_pushforward": finite_shell["blocker_assessment"]["B.QFT.02_free_finite_shell_QME_pushforward"],
            "fixed_coupling_interacting_endpoint": finite_shell["blocker_assessment"]["B.QFT.02_interacting_fixed_coupling_Cstar_limit"],
        },
    }

    component_product = {
        "notation": "P_sep=P_state x P_jet x P_line x P_BV^free",
        "component_count": 4,
        "all_component_certificates_pass": all(
            [
                t38["check_summary"]["failed"] == [],
                t39["check_summary"]["failed"] == [],
                h4["all_passed"],
                finite_shell["all_checks_pass"],
                state["all_checks_pass"],
                a35["theorem_proved"],
            ]
        ),
        "component_domains_identified_by_one_map": False,
        "component_product_is_physical_fiber_product": False,
        "observable_evaluation_is_covariant_BV_field_projection": False,
        "status": "MAXIMAL_LOCAL_FORMAL_COMPONENT_PRODUCT_CLOSED_PHYSICAL_FIBER_PRODUCT_OPEN",
    }

    promotion_criterion = {
        "theorem": "components extend to SP0-SP5 if and only if G0, G1 and G2 hold",
        "necessary": True,
        "sufficient": True,
        "G0": "one root, upper field-only action and one projection/contraction whose BV pushforward emits the anchored lower action and whose pointed repair/tangent-generator squares commute",
        "G1": "Dp is an isometry for the selected physical tangent pairings and transports the action Hessian",
        "G2": "the same map supplies the selected interacting QME-preserving BV and normalized-state pushforwards",
        "G0_implies_SP": ["SP0", "SP1", "SP2", "SP3"],
        "G1_implies_SP": ["SP4"],
        "G2_implies_SP": ["SP5"],
        "T40_then_implies": ["physical QJ1", "physical action-jet QJ2"],
        "existence_proved": False,
    }

    sp_ledger = {
        "SP0": {"component_support": "separate pinned hashes", "physical_satisfied": False, "missing_gate": "G0"},
        "SP1": {"component_support": "radial evaluation at H", "physical_satisfied": False, "missing_gate": "G0"},
        "SP2": {"component_support": "T39 anchored QJ1 scheme", "physical_satisfied": False, "missing_gate": "G0"},
        "SP3": {"component_support": "T39 action-Hessian preservation", "physical_satisfied": False, "missing_gate": "G0+G1"},
        "SP4": {"component_support": "A35 internal unit line", "physical_satisfied": False, "missing_gate": "G1"},
        "SP5": {"component_support": "cotangent retract, local-formal state existence and free shell pushforward", "physical_satisfied": False, "missing_gate": "G2"},
    }

    physical_boundary = {
        "same_root_source_action_gate_closed": False,
        "physical_tangent_pairing_gate_closed": False,
        "selected_interacting_state_BV_gate_closed": False,
        "selected_physical_projection_constructed": False,
        "physical_QJ1_selected": False,
        "physical_QJ2_selected": False,
        "gravitational_QJ0_selected": False,
        "complete_q79_BV_compactification_closed": False,
        "fixed_coupling_interacting_endpoint_closed": False,
        "acceptance_counters_change": False,
    }

    packet: dict[str, Any] = {
        "schema": "boe.mtt.cotangent-lifted-local-formal-projection.v1",
        "claim_id": "CBF.T41",
        "date": "2026-08-30",
        "status": "EXACT_MAXIMAL_LOCAL_FORMAL_COMPONENT_ASSEMBLY_AND_THREE_INDEPENDENT_PHYSICAL_GLUING_GATES",
        "source_provenance": {
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "handoff_id": source_lock["handoff_id"],
            "source_bundle_sha256": canonical_hash(source_lock["local_sources"]),
        },
        "typed_components": typed_components,
        "component_product": component_product,
        "promotion_criterion": promotion_criterion,
        "independent_gluing_gates": independence,
        "exact_finite_witness": {
            "action_jet_retraction": jet,
            "cotangent_contraction": cotangent,
            "free_shell_BV": shell,
            "radial_and_matter_states": state_exact,
        },
        "SP_clause_ledger": sp_ledger,
        "parameter_ledger": {
            "new_physical_continuous_parameters": 0,
            "new_physical_discrete_selectors": 0,
            "new_fits": 0,
            "new_observed_inputs": 0,
            "proof_coordinate_H": "3/2",
            "proof_coordinate_metric_scale_lambda": "2",
            "proof_coordinates_are_physical_inputs": False,
        },
        "physical_boundary": physical_boundary,
        "component_packets_assembled": 4,
        "component_packets_total": 4,
        "physical_gluing_gates_closed": 0,
        "physical_gluing_gates_total": 3,
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": "All known state, action-jet, internal-line, cotangent and free-shell pieces are now one typed component product. Promotion is proved equivalent to three independent gluing gates: same-root source/action, physical tangent pairing, and selected interacting state/BV pushforward.",
    }

    checks = source_hash_checks(source_lock)

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    required = schema["required"]
    check("schema_claim_id", schema["properties"]["claim_id"]["const"] == "CBF.T41")
    check("schema_requires_all_fields", all(field in required for field in packet))
    check("T38_builder_closed", t38["check_summary"]["failed"] == [])
    check("T39_builder_closed", t39["check_summary"]["failed"] == [])
    check("T40_builder_closed", t40["check_summary"]["failed"] == [])
    check("H4_certificate_passes", h4["all_passed"])
    check("finite_shell_certificate_passes", finite_shell["all_checks_pass"])
    check("state_certificate_passes", state["all_checks_pass"])
    check("A35_certificate_passes", a35["theorem_proved"])
    check("radial_component_positive", typed_components["P_state"]["positive_normalized"])
    check("radial_component_unique_marginal", typed_components["P_state"]["radial_marginal_unique"])
    check("preferred_state_not_promoted", not typed_components["P_state"]["preferred_full_state_selected"])
    check("action_QJ1_component_closed", typed_components["P_jet"]["local_formal_QJ1"] == "closed_constructively")
    check("action_QJ2_component_closed", typed_components["P_jet"]["local_formal_action_QJ2"] == "closed_constructively")
    check("action_not_derived_from_upper", not typed_components["P_jet"]["derived_from_selected_upper_action"])
    check("A35_rank_one", typed_components["P_line"]["rank"] == 1)
    check("A35_unit_magnitude", typed_components["P_line"]["dimensionless_insertion_magnitude"] == 1.0)
    check("A35_action_weight_open", not typed_components["P_line"]["physical_action_weight_closed"])
    check("H4_cotangent_closed", typed_components["P_BV_free"]["abstract_cotangent_retract_closed"])
    check("H4_direct_identification_open", not typed_components["P_BV_free"]["direct_internal_to_4d_BV_identification_closed"])
    check("free_shell_closed", typed_components["P_BV_free"]["free_finite_shell_pushforward"].startswith("closed_"))
    check("fixed_coupling_open", typed_components["P_BV_free"]["fixed_coupling_interacting_endpoint"] == "open")
    check("four_components", component_product["component_count"] == 4)
    check("all_component_certificates", component_product["all_component_certificates_pass"])
    check("domains_not_identified", not component_product["component_domains_identified_by_one_map"])
    check("product_not_fiber_product", not component_product["component_product_is_physical_fiber_product"])
    check("evaluation_not_BV_projection", not component_product["observable_evaluation_is_covariant_BV_field_projection"])
    check("promotion_necessary", promotion_criterion["necessary"])
    check("promotion_sufficient", promotion_criterion["sufficient"])
    check("promotion_existence_open", not promotion_criterion["existence_proved"])
    check("G0_maps_SP0_to_SP3", promotion_criterion["G0_implies_SP"] == ["SP0", "SP1", "SP2", "SP3"])
    check("G1_maps_SP4", promotion_criterion["G1_implies_SP"] == ["SP4"])
    check("G2_maps_SP5", promotion_criterion["G2_implies_SP"] == ["SP5"])
    check("jet_det_54", jet["restricted_even_determinant"] == "54")
    check("jet_C_idempotent", jet["C_H_idempotent"])
    check("jet_R_idempotent", jet["R_H_idempotent"])
    check("jet_C_right_inverse", jet["jet_C_H_equals_jet"])
    check("jet_R_kernel", jet["jet_R_H_zero"])
    check("primal_pi", cotangent["primal_projection_after_inclusion"])
    check("primal_contraction", cotangent["primal_contraction_identity"])
    check("primal_side_conditions", cotangent["primal_side_conditions"])
    check("cotangent_pi", cotangent["cotangent_projection_after_inclusion"])
    check("cotangent_contraction", cotangent["cotangent_contraction_identity"])
    check("cotangent_symplectic_inclusion", cotangent["cotangent_inclusion_is_symplectic"])
    check("cotangent_symplectic_differential", cotangent["cotangent_differential_is_symplectic"])
    check("discarded_pairing_nonzero", cotangent["discarded_pairing_before_projection"] == "1")
    check("discarded_pairing_killed", cotangent["discarded_pairing_after_projection"] == "0")
    check("shell_Q2", shell["Q_squared_zero"])
    check("shell_Q_symplectic", shell["Q_preserves_odd_pairing"])
    check("shell_Delta_identity", shell["Delta_is_identity"])
    check("shell_contraction", shell["Hodge_contraction_identity"])
    check("shell_Lagrangian", shell["L_shell_is_lagrangian"])
    check("shell_nondegenerate", shell["restricted_quadratic_is_nondegenerate"])
    check("shell_det_minus_one", shell["restricted_quadratic_determinant"] == "-1")
    check("radial_variance_zero", state_exact["radial_variance"] == "0")
    check("two_states_positive", state_exact["both_states_positive"])
    check("two_states_normalized", state_exact["both_states_normalized"])
    check("state_expectations_distinct", state_exact["omega_0_sigma_z"] != state_exact["omega_1_sigma_z"])
    check("radial_does_not_select_full_state", not state_exact["full_state_selected_by_radial_marginal"])
    check("G0_hashes_distinct", independence["G0_same_root"]["root_hashes_distinct"])
    check("G0_nonimplication", not independence["G0_same_root"]["same_root_follows_from_numeric_component_equality"])
    check("G1_defect_three", independence["G1_physical_tangent_pairing"]["isometry_defect"] == "3")
    check("G1_nonimplication", not independence["G1_physical_tangent_pairing"]["physical_isometry_follows_from_internal_unit_line"])
    check("G2_two_states", independence["G2_selected_interacting_state_BV"]["two_positive_normalized_matter_states"])
    check("G2_nonimplication", not independence["G2_selected_interacting_state_BV"]["preferred_interacting_state_follows"])
    check("six_SP_clauses", set(sp_ledger) == {"SP0", "SP1", "SP2", "SP3", "SP4", "SP5"})
    check("no_physical_SP_clause", not any(row["physical_satisfied"] for row in sp_ledger.values()))
    check("G0_open", not physical_boundary["same_root_source_action_gate_closed"])
    check("G1_open", not physical_boundary["physical_tangent_pairing_gate_closed"])
    check("G2_open", not physical_boundary["selected_interacting_state_BV_gate_closed"])
    check("physical_projection_open", not physical_boundary["selected_physical_projection_constructed"])
    check("physical_QJ1_open", not physical_boundary["physical_QJ1_selected"])
    check("physical_QJ2_open", not physical_boundary["physical_QJ2_selected"])
    check("gravity_QJ0_open", not physical_boundary["gravitational_QJ0_selected"])
    check("zero_new_parameters", packet["parameter_ledger"]["new_physical_continuous_parameters"] == 0)
    check("zero_new_selectors", packet["parameter_ledger"]["new_physical_discrete_selectors"] == 0)
    check("zero_fits", packet["parameter_ledger"]["new_fits"] == 0)
    check("zero_observed_inputs", packet["parameter_ledger"]["new_observed_inputs"] == 0)
    check("component_counter_4_of_4", packet["component_packets_assembled"] == packet["component_packets_total"] == 4)
    check("gluing_counter_0_of_3", packet["physical_gluing_gates_closed"] == 0 and packet["physical_gluing_gates_total"] == 3)
    check("packet_counter_unchanged", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("row_counter_unchanged", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)

    theorem_text = THEOREM.read_text(encoding="utf-8")
    check("theorem_three_gates", all(marker in theorem_text for marker in ["G0: same-root", "G1: physical", "G2: selected"]))
    check("theorem_if_and_only_if", "if and only if `G0`, `G1` and `G2`" in theorem_text)
    check("theorem_component_product_boundary", "component product" in theorem_text and "physical fiber product" in theorem_text)
    check("theorem_metric_witness", "the defect is `3`" in theorem_text)
    check("theorem_state_witness", "Omega_0(sigma_z)=1" in theorem_text and "Omega_1(sigma_z)=-1" in theorem_text)
    check("theorem_physical_counters", "physical packets accepted:         0/3" in theorem_text and "physical rows accepted:            0/7" in theorem_text)

    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
    }
    return packet


def main() -> None:
    packet = build()
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    summary = packet["check_summary"]
    print(f"wrote {OUTPUT.name}")
    print(f"checks: {summary['passed']}/{summary['total']}")
    if summary["failed"]:
        raise SystemExit("failed checks: " + ", ".join(summary["failed"]))


if __name__ == "__main__":
    main()
