#!/usr/bin/env python3
"""Independent verifier for the CBF.T46 packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "selected_future_state_moller_bv_transport.packet.json"
SOURCE_LOCK = ROOT / "selected_future_state_moller_bv_transport_source_lock.json"
SCHEMA = ROOT / "selected_future_state_moller_bv_transport_contract.schema.json"
THEOREM = ROOT / "SelectedFutureStateMollerBVTransportAndFullG2CutsetTheorem_v1.md"

Matrix = list[list[Fraction]]
Vector = list[Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_matrix(payload: list[list[str]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in payload]


def parse_vector(payload: list[str]) -> Vector:
    return [Fraction(value) for value in payload]


def zero(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zero(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[a - b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum((a * b for a, b in zip(row, vector)), Fraction(0)) for row in matrix]


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def determinant_2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def expectation(density: Matrix, observable: Matrix) -> Fraction:
    return trace(multiply(density, observable))


def main() -> None:
    packet = load(PACKET)
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    theorem = THEOREM.read_text(encoding="utf-8")
    checks: dict[str, bool] = {}

    checks["packet_schema"] = packet["schema"] == "boe.mtt.selected-future-state-moller-bv-transport.v1"
    checks["packet_claim"] = packet["claim_id"] == "CBF.T46"
    checks["packet_date"] = packet["date"] == "2026-08-30"
    checks["lock_schema"] = source_lock["schema"] == "boe.mtt.selected-future-state-moller-bv-transport-source-lock.v1"
    checks["lock_claim"] = source_lock["claim_id"] == "CBF.T46"
    checks["schema_claim"] = schema["properties"]["claim_id"]["const"] == "CBF.T46"
    checks["all_contract_keys"] = set(schema["required"]).issubset(packet)
    checks["source_lock_hash"] = packet["source_provenance"]["source_lock_sha256"] == digest(SOURCE_LOCK)
    checks["contract_hash"] = packet["source_provenance"]["contract_sha256"] == digest(SCHEMA)

    for group in ("construction_sources", "comparison_sources"):
        for index, source in enumerate(source_lock[group], start=1):
            path = (ROOT / source["path"]).resolve()
            checks[f"{group}_{index:02d}"] = path.is_file() and digest(path) == source["sha256"]

    transport = packet["exact_transport_witness"]
    source = parse_matrix(transport["source_future_projection"])
    unitary = parse_matrix(transport["transport_unitary"])
    transported = parse_matrix(transport["transported_projection"])
    returned = parse_matrix(transport["inverse_transport"])
    second = parse_matrix(transport["second_transport_unitary"])
    composite = parse_matrix(transport["composite_transport_unitary"])
    sequential = parse_matrix(transport["sequential_transport_projection"])
    direct = parse_matrix(transport["direct_composite_projection"])

    checks["unitary_exact"] = multiply(unitary, transpose(unitary)) == identity(2)
    checks["second_unitary_exact"] = multiply(second, transpose(second)) == identity(2)
    checks["source_projector"] = multiply(source, source) == source
    checks["source_rank_one"] = trace(source) == 1 and determinant_2(source) == 0
    recomputed_transport = multiply(multiply(unitary, source), transpose(unitary))
    checks["transport_recomputed"] = transported == recomputed_transport
    checks["transport_projector"] = multiply(transported, transported) == transported
    checks["transport_rank_one"] = trace(transported) == 1 and determinant_2(transported) == 0
    checks["transport_entries_exact"] = transported == [
        [Fraction(9, 25), Fraction(12, 25)],
        [Fraction(12, 25), Fraction(16, 25)],
    ]
    checks["inverse_returns_source"] = returned == multiply(multiply(transpose(unitary), transported), unitary) == source
    checks["composite_unitary"] = composite == multiply(second, unitary)
    checks["sequential_transport"] = sequential == multiply(multiply(second, transported), transpose(second))
    checks["direct_transport"] = direct == multiply(multiply(composite, source), transpose(composite))
    checks["transport_composition"] = sequential == direct

    for index, row in enumerate(transport["expectation_rows"], start=1):
        observable = parse_matrix(row["observable"])
        pulled_back = multiply(multiply(transpose(unitary), observable), unitary)
        checks[f"expectation_{index:02d}"] = (
            Fraction(row["transported_state"]) == expectation(transported, observable)
            and Fraction(row["source_after_pullback"]) == expectation(source, pulled_back)
            and Fraction(row["transported_state"]) == Fraction(row["source_after_pullback"])
        )

    for index, row in enumerate(transport["positive_square_rows"], start=1):
        root = parse_matrix(row["root"])
        square = multiply(transpose(root), root)
        value = expectation(transported, square)
        checks[f"positive_square_{index:02d}"] = value == Fraction(row["positive_square_expectation"]) and value >= 0

    lift = packet["canonical_lift_witness"]
    q0 = parse_matrix(lift["Q0"])
    homotopy = parse_matrix(lift["homotopy"])
    physical = parse_matrix(lift["physical_projector"])
    delta = parse_matrix(lift["delta_Q1"])
    free = parse_vector(lift["free_vector"])
    correction = parse_vector(lift["first_order_correction"])
    checks["Q0_nilpotent"] = multiply(q0, q0) == zero(6, 6)
    checks["contraction_identity"] = add(multiply(q0, homotopy), multiply(homotopy, q0)) == subtract(identity(6), physical)
    checks["delta_nilpotent"] = multiply(delta, delta) == zero(6, 6)
    checks["Q0_delta_anticommute"] = add(multiply(q0, delta), multiply(delta, q0)) == zero(6, 6)
    checks["formal_Q_nilpotent"] = all(
        value == zero(6, 6)
        for value in (multiply(q0, q0), add(multiply(q0, delta), multiply(delta, q0)), multiply(delta, delta))
    )
    first_order_closure = [a + b for a, b in zip(matvec(q0, correction), matvec(delta, free))]
    checks["lift_first_order_closed"] = first_order_closure == [Fraction(0)] * 6
    checks["lift_physical_projection"] = matvec(physical, correction) == [Fraction(0)] * 6
    checks["lift_homotopy_gauge"] = matvec(homotopy, correction) == [Fraction(0)] * 6
    checks["lift_formula_text"] = lift["formal_lift"] == "psi(lambda)=epsilon_1+lambda x"
    checks["lift_scope_guard"] = "not inferred from this toy perturbation" in lift["scope_guard"]

    exact = packet["exact_direct_state_transport"]
    checks["exact_state_formula"] = exact["selected_in_state"] == "omega_h^in=omega_fut composed with (alpha_h^ret)^(-1)"
    checks["exact_state_hadamard"] = exact["Hadamard_preserved"] is True
    checks["exact_state_pure"] = exact["purity_preserved"] is True
    checks["exact_state_no_parameter"] = exact["new_state_parameter_count"] == 0
    checks["exact_state_not_full_SM"] = exact["nonlinear_full_SM_interaction"] is False
    checks["relative_uniqueness_guard"] = "not the unique state" in exact["unique_meaning"]

    formal = packet["formal_BV_state_pullback"]
    checks["formal_map_unital_star"] = "unital star-isomorphism" in formal["map"]
    checks["formal_state_formula"] = formal["state"] == "omega_V=omega_0 composed with I_V"
    checks["formal_positive_square_cone"] = "formal square cone" in formal["formal_positivity"]
    checks["formal_BRST_descent"] = "closed and exact" in formal["BRST_descent"]
    checks["formal_transport_closed"] = formal["closed_as_algebraic_transport_theorem"] is True
    checks["full_SM_not_instantiated"] = formal["instantiated_as_selected_full_SM_state"] is False

    canonical = packet["canonical_BRST_lift"]
    checks["canonical_recursion"] = canonical["recursive_lift"] == "psi_n=-h r_n"
    checks["canonical_two_gauges"] = canonical["gauge_conditions"] == ["p psi_n=0", "h psi_n=0"]
    checks["canonical_unique"] = "hence vanish" in canonical["uniqueness"]
    checks["canonical_does_not_select_seed"] = canonical["does_not_select_free_seed"] is True

    factors = packet["full_seed_factorization"]
    checks["three_factor_formula"] = all(token in factors["required_free_state"] for token in ("omega_gauge,phys", "omega_Higgs", "omega_Weyl"))
    checks["Weyl_selected"] = "selected" in factors["Weyl_factor"]["status"]
    checks["radial_not_fluctuation"] = factors["radial_background_marginal"]["is_Higgs_fluctuation_state"] is False
    checks["Higgs_seed_open"] = factors["Higgs_fluctuation_factor"]["selected"] is False
    checks["gauge_seed_open"] = factors["gauge_physical_factor"]["selected"] is False
    checks["formal_lift_choice_closed"] = factors["formal_lift_choice_after_full_seed"]["selected"] is True
    checks["full_seed_open"] = factors["full_product_seed_selected"] is False
    checks["exactly_two_missing_factors"] = factors["missing_selected_factors"] == 2

    ledger = packet["G2_clause_ledger"]
    checks["G2a_closed"] = ledger["G2a_flat_branch_free_Weyl_initial_state"] == "closed by T45"
    checks["quadratic_transport_closed"] = ledger["G2b_exact_quadratic_background_Dirac_state_transport"] == "closed by T46"
    checks["formal_existence_inherited"] = "inherited" in ledger["G2b_local_formal_positive_state_existence"]
    checks["full_seed_ledger_open"] = ledger["G2b_selected_full_gauge_Higgs_Weyl_seed"] == "open"
    checks["upper_map_open"] = ledger["G2b_selected_upper_action_and_BV_map"] == "open"
    checks["continuum_open"] = ledger["G2c_selected_regulator_independent_continuum"] == "open 0/9"
    checks["top_G2_open"] = ledger["top_level_physical_G2"] == "open"
    checks["top_gate_unchanged"] = ledger["physical_T41_gate_count"] == "0/3"

    fixed = packet["fixed_coupling_boundary"]
    checks["formal_not_numeric"] = fixed["formal_square_cone_is_numeric_positive_cone"] is False
    checks["finite_Cstar_5_of_5"] = fixed["finite_auxiliary_regulator_Cstar_rows"] == "5/5"
    checks["continuum_Cstar_0_of_9"] = fixed["selected_continuum_Cstar_rows"] == "0/9"
    checks["no_regulator_removal_claim"] = fixed["T46_proves_regulator_removal"] is False
    checks["no_nonperturbative_claim"] = fixed["T46_proves_nonperturbative_SM_state"] is False

    parameters = packet["parameter_ledger"]
    checks["no_observed_inputs"] = parameters["new_observed_inputs"] == 0
    checks["no_fits"] = parameters["new_fitted_parameters"] == 0
    checks["no_continuous_selector"] = parameters["new_continuous_state_selectors"] == 0
    checks["no_discrete_selector"] = parameters["new_discrete_state_selectors"] == 0
    checks["H_inherited"] = parameters["inherited_unresolved_radial_scale"] == "H"

    boundary = packet["physical_boundary"]
    checks["packets_unchanged"] = boundary["physical_packets_accepted"] == 0 and boundary["physical_packets_total"] == 3
    checks["rows_unchanged"] = boundary["physical_rows_accepted"] == 0 and boundary["physical_rows_total"] == 7
    checks["determinant_open"] = any("determinant" in item for item in boundary["open"])
    checks["fixed_coupling_open"] = any("fixed-coupling" in item for item in boundary["open"])

    required_phrases = [
        "not another state choice",
        "must not be renamed the nonlinear interacting Standard Model",
        "unique transport of the selected anchor state",
        "It does not select the free vector",
        "radial marginal and Higgs fluctuation state are different typed objects",
        "Formal positivity means",
        "top-level physical G2",
        "0/7 rows",
    ]
    for index, phrase in enumerate(required_phrases, start=1):
        checks[f"theorem_guard_{index:02d}"] = phrase in theorem

    checks["builder_checks_all_true"] = all(packet["checks"].values())
    checks["builder_summary_failed_empty"] = packet["check_summary"]["failed"] == []
    checks["builder_summary_count_consistent"] = packet["check_summary"]["passed"] == packet["check_summary"]["total"]

    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise SystemExit("CBF.T46 independent verification failed: " + ", ".join(failed))
    print(f"CBF.T46 independent verification passed {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
