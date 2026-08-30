#!/usr/bin/env python3
"""Independently verify the CBF.T36 pointed quantum jet-matching packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "pointed_closure_germ_quantum_jet_matching.packet.json"
SOURCE_LOCK = ROOT / "pointed_closure_germ_quantum_jet_matching_source_lock.json"
SCHEMA = ROOT / "pointed_closure_germ_quantum_jet_matching_contract.schema.json"
THEOREM = ROOT / "PointedClosureGermNaturalityAndQuantumJetMatchingSelectionBoundaryTheorem_v1.md"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def parse_fraction(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", maxsplit=1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text))


def derivative_value(
    coefficients: list[Fraction], point: Fraction, order: int
) -> Fraction:
    total = Fraction(0)
    for power, coefficient in enumerate(coefficients):
        if power < order:
            continue
        multiplier = 1
        for index in range(order):
            multiplier *= power - index
        total += coefficient * multiplier * point ** (power - order)
    return total


def jet(coefficients: list[Fraction], point: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(derivative_value(coefficients, point, order) for order in range(3))


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    return sum(
        (
            matrix[0][0]
            * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]),
            -matrix[0][1]
            * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]),
            matrix[0][2]
            * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]),
        ),
        Fraction(0),
    )


def solve(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    work = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for col in range(3):
        candidates = [row for row in range(col, 3) if work[row][col]]
        if not candidates:
            raise ArithmeticError("singular jet matrix")
        row = candidates[0]
        work[col], work[row] = work[row], work[col]
        pivot = work[col][col]
        for j in range(col, 4):
            work[col][j] /= pivot
        for row in range(3):
            if row == col:
                continue
            factor = work[row][col]
            for j in range(col, 4):
                work[row][j] -= factor * work[col][j]
    return [work[row][3] for row in range(3)]


def subtract(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return [
        (left[index] if index < len(left) else Fraction(0))
        - (right[index] if index < len(right) else Fraction(0))
        for index in range(size)
    ]


def matrix_at(point: Fraction) -> list[list[Fraction]]:
    return [
        [Fraction(1), point**2, point**4],
        [Fraction(0), 2 * point, 4 * point**3],
        [Fraction(0), Fraction(2), 12 * point**2],
    ]


def raw_loop(
    h: Decimal,
    mu: Decimal,
    c_scheme: Decimal,
    kappa: Decimal,
    q4: Decimal,
    l4: Decimal,
) -> Decimal:
    return -kappa * h**4 * (
        q4 * (h * h / (mu * mu)).ln() + l4 - c_scheme * q4
    )


def relative_loop_from_record(
    record: dict[str, str], point: Decimal, q4: Decimal, l4: Decimal, kappa: Decimal
) -> tuple[Decimal, Decimal]:
    h = Decimal(record["h_over_H"]) * point
    mu = Decimal(record["mu_over_Lambda"])
    c_scheme = Decimal(record["c_scheme"])
    omega = Decimal(record["delta_Omega_over_Lambda4"])
    l_h = q4 * (point * point / (mu * mu)).ln() + l4 - c_scheme * q4
    mass = -Decimal(2) * kappa * q4 * point**2
    quartic = kappa * (l_h + Decimal("1.5") * q4)

    def corrected(value: Decimal) -> Decimal:
        return (
            raw_loop(value, mu, c_scheme, kappa, q4, l4)
            + omega
            + mass * value**2
            + quartic * value**4
        )

    relative = corrected(h) - corrected(point)
    universal = kappa * q4 * (
        h**4 * ((point * point / (h * h)).ln() + Decimal("1.5"))
        - Decimal(2) * point**2 * h**2
        + point**4 / Decimal(2)
    )
    return relative, universal


def main() -> None:
    packet = load_json(PACKET)
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t35 = load_json(T35_PACKET)
    theorem = THEOREM.read_text(encoding="utf-8")
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)

    check("packet_schema", packet["schema"] == schema["properties"]["schema"]["const"])
    check("packet_claim", packet["claim_id"] == "CBF.T36")
    check("source_lock_claim", source_lock["claim_id"] == "CBF.T36")
    check("builder_check_ledger", all(packet["checks"].values()))
    check(
        "builder_check_summary",
        packet["check_summary"]["passed"] == packet["check_summary"]["total"]
        and packet["check_summary"]["failed"] == [],
    )
    check("theorem_hash", packet["source_provenance"]["theorem_sha256"] == sha256(THEOREM))
    check("schema_hash", packet["source_provenance"]["contract_schema_sha256"] == sha256(SCHEMA))
    check("source_lock_hash", packet["source_provenance"]["source_lock_sha256"] == sha256(SOURCE_LOCK))

    all_sources_match = True
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        matched = path.is_file() and sha256(path) == source["sha256"]
        check(f"source_{index:02d}_hash", matched)
        all_sources_match &= matched
    check("all_source_hashes", all_sources_match)

    root_payload = packet["source_provenance"]["source_root_payload"]
    check(
        "source_root_hash",
        canonical_hash(root_payload) == packet["source_provenance"]["source_root_sha256"],
    )
    check("source_root_repositories", root_payload["repositories"] == source_lock["repositories"])

    retraction = packet["pointed_jet_retraction"]
    witness = retraction["exact_witness"]
    point = parse_fraction(witness["source_point"])
    matrix = matrix_at(point)
    check("jet_determinant_formula", determinant(matrix) == 16 * point**3)
    check("jet_determinant_packet", witness["source_jet_matrix_determinant"] == str(determinant(matrix)))

    polynomial = [
        parse_fraction(value)
        for value in witness["source_polynomial_coefficients_ascending"]
    ]
    independent_jet = list(jet(polynomial, point))
    declared_jet = [parse_fraction(value) for value in witness["source_jet"]]
    check("source_jet_recomputed", independent_jet == declared_jet)
    solved = solve(matrix, independent_jet)
    declared_solved = [
        parse_fraction(value)
        for value in witness["source_counterterm_coefficients_1_h2_h4"]
    ]
    check("counterterm_coefficients_recomputed", solved == declared_solved)
    counterterm = [solved[0], Fraction(0), solved[1], Fraction(0), solved[2]]
    remainder = subtract(polynomial, counterterm)
    check("remainder_zero_jet", jet(remainder, point) == (0, 0, 0))

    scale = parse_fraction(witness["radial_scale"])
    target_point = parse_fraction(witness["target_point"])
    scaled_polynomial = [value / scale**power for power, value in enumerate(polynomial)]
    target_matrix = matrix_at(target_point)
    target_solution = solve(target_matrix, list(jet(scaled_polynomial, target_point)))
    target_counterterm = [
        target_solution[0],
        Fraction(0),
        target_solution[1],
        Fraction(0),
        target_solution[2],
    ]
    target_remainder = subtract(scaled_polynomial, target_counterterm)
    scaled_remainder = [value / scale**power for power, value in enumerate(remainder)]
    check("naturality_under_scaling", target_remainder == scaled_remainder)
    check("target_zero_jet", jet(target_remainder, target_point) == (0, 0, 0))
    check(
        "jet_transport_diagonal",
        witness["jet_transport_diagonal"]
        == ["1", str(Fraction(1, scale)), str(Fraction(1, scale**2))],
    )
    check("hessian_numeric_not_invariant", scale != 1 and retraction["unique_for_positive_H"])

    no_go = packet["gaussian_pushforward_no_go"]
    g_odd = parse_fraction(no_go["odd_coupling"]["g"])
    odd_expected = [Fraction(0), g_odd, -2 * g_odd**2]
    odd_declared = [parse_fraction(value) for value in no_go["odd_coupling"]["jet_at_zero"]]
    check("odd_gaussian_jet", odd_declared == odd_expected)
    check("odd_tadpole_shift", odd_declared[1] != 0)
    check("odd_hessian_shift", odd_declared[2] != 0)

    g_even = parse_fraction(no_go["even_coupling"]["g"])
    even_expected = [Fraction(0), Fraction(0), g_even]
    even_declared = [parse_fraction(value) for value in no_go["even_coupling"]["jet_at_zero"]]
    check("even_gaussian_jet", even_declared == even_expected)
    check("even_tadpole_protected", even_declared[1] == 0)
    check("even_hessian_shift", even_declared[2] != 0)

    measure_shift = [
        parse_fraction(value)
        for value in no_go["measure_normalization"]["effective_action_jet_shift"]
    ]
    check("measure_changes_value", measure_shift[0] != 0)
    check("measure_leaves_derivatives", measure_shift[1:] == [0, 0])
    check(
        "nongravitational_normalized_correlators_ignore_measure_shift",
        no_go["measure_normalization"][
            "normalized_nongravitational_correlators_unchanged"
        ],
    )
    check(
        "gravity_keeps_vacuum_row",
        not no_go["measure_normalization"]["gravitational_vacuum_energy_unchanged"],
    )

    reduction = packet["t35_reduction"]
    numeric = reduction["numerical_execution"]
    with localcontext() as context:
        context.prec = 90
        h_reference = Decimal(numeric["H_over_Lambda"])
        q4 = Decimal(numeric["q4_star"])
        l4 = Decimal(t35["numerical_execution"]["L4_star"])
        kappa = Decimal(numeric["test_kappa_F"])
        maximum = Decimal(0)
        for index, record in enumerate(numeric["sample_records"], start=1):
            relative, universal = relative_loop_from_record(
                record, h_reference, q4, l4, kappa
            )
            residual = abs(relative - universal)
            maximum = max(maximum, residual)
            check(f"relative_sample_{index:02d}", residual < Decimal("1e-75"))
            check(
                f"relative_record_{index:02d}",
                abs(relative - Decimal(record["relative_correction"])) < Decimal("1e-75")
                and abs(universal - Decimal(record["universal_remainder"]))
                < Decimal("1e-75"),
            )
        check(
            "maximum_relative_residual",
            maximum == Decimal(numeric["maximum_relative_formula_residual"]),
        )
        omega = q4 * h_reference**4 / Decimal(2)
        check(
            "QJ0_omega_recomputed",
            abs(omega - Decimal(numeric["derived_QJ0_delta_Omega_per_unit_kappa"]))
            < Decimal("1e-75"),
        )
        check(
            "QJ0_matches_T35",
            abs(omega - Decimal(numeric["T35_delta_Omega_per_unit_kappa"]))
            < Decimal("1e-75"),
        )

    clauses = packet["matching_clause_classification"]
    check("three_typed_certificates", set(clauses).issuperset({"QJ0", "QJ1", "QJ2"}))
    check("QJ0_open", not clauses["QJ0"]["selected_by_existing_sources"])
    check("QJ1_open", not clauses["QJ1"]["selected_by_existing_sources"])
    check("QJ2_open", not clauses["QJ2"]["selected_by_existing_sources"])
    check("certificates_not_fit_parameters", not clauses["these_are_scalar_fit_parameters"])
    check("relative_requires_QJ1_QJ2", clauses["QJ1_QJ2_suffice_for_relative_nongravitational_action"])
    check("absolute_requires_QJ0", clauses["QJ0_required_for_absolute_gravitational_action"])
    check("full_rule_not_selected", not clauses["existing_upper_action_selects_full_rule"])

    ledger = packet["parameter_ledger"]
    check("no_observed_inputs", ledger["new_observed_construction_inputs"] == 0)
    check("no_fits", ledger["new_fitted_coefficients"] == 0)
    check("no_new_continuous_parameters", ledger["new_continuous_physical_parameters"] == 0)
    check("one_absolute_constant_after_QJ1_QJ2", ledger["counterterm_freedom_after_QJ1_QJ2"] == 1)
    check("zero_relative_freedom_after_QJ1_QJ2", ledger["counterterm_freedom_modulo_constants_after_QJ1_QJ2"] == 0)
    check("zero_freedom_after_all_certificates", ledger["counterterm_freedom_after_QJ0_QJ1_QJ2"] == 0)

    physical = packet["physical_boundary"]
    check("mathematical_retraction_closed", physical["pointed_jet_retraction_mathematics_closed"])
    check("generic_preservation_rejected", physical["generic_pushforward_jet_preservation_rejected"])
    for key in (
        "physical_QJ1_tadpole_protection_closed",
        "physical_QJ2_tangent_Hessian_intertwiner_closed",
        "physical_QJ0_vacuum_normalization_closed",
        "full_closure_jet_matching_selected",
        "selected_external_BV_operator_domain_closed",
        "QME_Ward_execution_closed",
        "full_renormalized_QFT_vacuum_closed",
        "B_ACTION_01_closed",
        "B_QFT_02_closed",
    ):
        check(f"boundary_{key}", not physical[key])
    check("packet_acceptance", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("row_acceptance", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)

    check("theorem_has_unique_retraction", "unique linear projection" in theorem)
    check("theorem_has_gaussian_no_go", "Natural pushforward does not preserve the jet" in theorem)
    check("theorem_has_relative_remainder", "Delta V_12(h)-Delta V_12(H)" in theorem)
    check("theorem_keeps_physical_boundary", "full closure-jet rule remains unselected" in theorem)

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T36 independent verification failed: {failed}")
    print(f"verified {PACKET.name}: {len(checks)}/{len(checks)} independent checks passed")


if __name__ == "__main__":
    main()
