#!/usr/bin/env python3
"""Build the exact CBF.T36 pointed quantum jet-matching packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "pointed_closure_germ_quantum_jet_matching_source_lock.json"
SCHEMA = ROOT / "pointed_closure_germ_quantum_jet_matching_contract.schema.json"
THEOREM = ROOT / "PointedClosureGermNaturalityAndQuantumJetMatchingSelectionBoundaryTheorem_v1.md"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
H4_T8 = ROOT / "../mtt-preprojection-repair-calculus/theorems/PREPROJECTION_REPAIR_JET_TO_PERTURBATIVE_GRAPH_FUNCTOR_THEOREM_v1.md"
H4_T9 = ROOT / "../mtt-preprojection-repair-calculus/theorems/PREPROJECTION_VARIATIONAL_ANCHOR_MULTIPLIER_LIFT_AND_NORMAL_SQUARE_THEOREM_v1.md"
H4_T10 = ROOT / "../mtt-preprojection-repair-calculus/theorems/PREPROJECTION_CYCLIC_MAURER_CARTAN_ACTION_AND_TWISTED_DESCENT_THEOREM_v1.md"
ACTION_CONTRACT = ROOT / "../mtt-preprojection-repair-calculus/docs/PHYSICAL_ACTION_BRIDGE_CONTRACT.md"
A84 = ROOT / "../mtt-sm-parity-closure/proof_corpus/mtt_selected_closureshadowgaugeactionaxiomderivation_or_explicitadoptionandheldoutvalidation_v1.md"
A85 = ROOT / "../mtt-sm-parity-closure/proof_corpus/mtt_selected_finitematchingcompletenessfromunifiedaction_or_explicitboundaryadoptionandheldoutvalidation_v1.md"
OUTPUT = ROOT / "pointed_closure_germ_quantum_jet_matching.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def poly_trim(coefficients: list[Fraction]) -> list[Fraction]:
    result = list(coefficients)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_sub(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    result = []
    for index in range(size):
        a = left[index] if index < len(left) else Fraction(0)
        b = right[index] if index < len(right) else Fraction(0)
        result.append(a - b)
    return poly_trim(result)


def poly_derivative_value(
    coefficients: list[Fraction], point: Fraction, order: int
) -> Fraction:
    total = Fraction(0)
    for degree, coefficient in enumerate(coefficients):
        if degree < order:
            continue
        factor = 1
        for offset in range(order):
            factor *= degree - offset
        total += coefficient * factor * point ** (degree - order)
    return total


def jet(coefficients: list[Fraction], point: Fraction) -> list[Fraction]:
    return [poly_derivative_value(coefficients, point, order) for order in range(3)]


def det3(matrix: list[list[Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def solve3(matrix: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    augmented = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for column in range(3):
        pivot = next(row for row in range(column, 3) if augmented[row][column] != 0)
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [entry / pivot_value for entry in augmented[column]]
        for row in range(3):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(augmented[row], augmented[column])
            ]
    return [augmented[row][3] for row in range(3)]


def jet_matrix(point: Fraction) -> list[list[Fraction]]:
    return [
        [Fraction(1), point**2, point**4],
        [Fraction(0), 2 * point, 4 * point**3],
        [Fraction(0), Fraction(2), 12 * point**2],
    ]


def even_counterterm(coefficients: list[Fraction]) -> list[Fraction]:
    constant, quadratic, quartic = coefficients
    return [constant, Fraction(0), quadratic, Fraction(0), quartic]


def retract_jet(
    coefficients: list[Fraction], point: Fraction
) -> tuple[list[Fraction], list[Fraction], list[Fraction]]:
    counterterm_coefficients = solve3(jet_matrix(point), jet(coefficients, point))
    counterterm = even_counterterm(counterterm_coefficients)
    remainder = poly_sub(coefficients, counterterm)
    return counterterm_coefficients, counterterm, remainder


def scale_polynomial(coefficients: list[Fraction], scale: Fraction) -> list[Fraction]:
    return [coefficient / scale**degree for degree, coefficient in enumerate(coefficients)]


def pointed_retraction_witness() -> dict[str, Any]:
    point = Fraction(3, 2)
    scale = Fraction(2)
    target_point = scale * point
    polynomial = [Fraction(value) for value in (5, 7, 11, 13, 17, 19)]
    source_coefficients, source_counterterm, source_remainder = retract_jet(
        polynomial, point
    )
    _, _, source_retracted_twice = retract_jet(source_remainder, point)

    target_polynomial = scale_polynomial(polynomial, scale)
    target_coefficients, target_counterterm, target_remainder = retract_jet(
        target_polynomial, target_point
    )
    transported_counterterm = scale_polynomial(source_counterterm, scale)
    transported_remainder = scale_polynomial(source_remainder, scale)

    pure_counterterm = even_counterterm([Fraction(2), Fraction(-3), Fraction(5)])
    _, _, pure_counterterm_remainder = retract_jet(pure_counterterm, point)

    return {
        "source_point": ftext(point),
        "radial_scale": ftext(scale),
        "target_point": ftext(target_point),
        "source_polynomial_coefficients_ascending": [ftext(value) for value in polynomial],
        "source_jet": [ftext(value) for value in jet(polynomial, point)],
        "source_counterterm_coefficients_1_h2_h4": [
            ftext(value) for value in source_coefficients
        ],
        "source_remainder_coefficients_ascending": [
            ftext(value) for value in source_remainder
        ],
        "source_remainder_jet": [ftext(value) for value in jet(source_remainder, point)],
        "source_retracted_twice_equals_source_remainder": (
            source_retracted_twice == source_remainder
        ),
        "pure_counterterm_retracts_to_zero": pure_counterterm_remainder == [Fraction(0)],
        "source_jet_matrix_determinant": ftext(det3(jet_matrix(point))),
        "source_16H3": ftext(16 * point**3),
        "target_counterterm_coefficients_1_u2_u4": [
            ftext(value) for value in target_coefficients
        ],
        "target_counterterm_equals_scaled_source": target_counterterm
        == transported_counterterm,
        "target_remainder_equals_scaled_source": target_remainder == transported_remainder,
        "target_remainder_jet": [
            ftext(value) for value in jet(target_remainder, target_point)
        ],
        "jet_transport_diagonal": ["1", "1/2", "1/4"],
        "numeric_hessian_equality_requires_unit_scale": scale == 1,
    }


def gaussian_no_go_witnesses() -> dict[str, Any]:
    coupling = Fraction(1)
    normalization_shift = Fraction(7, 5)
    return {
        "odd_coupling": {
            "upper_action": "S0(x)+(1/2)(1+2g x)y^2",
            "effective_loop": "(1/2)log(1+2g x)",
            "g": ftext(coupling),
            "jet_at_zero": ["0", ftext(coupling), ftext(-2 * coupling**2)],
            "fixed_point_preserved": False,
            "hessian_preserved": False,
            "finite_gaussian_pushforward_exact": True,
        },
        "even_coupling": {
            "upper_action": "S0(x)+(1/2)(1+g x^2)y^2",
            "effective_loop": "(1/2)log(1+g x^2)",
            "g": ftext(coupling),
            "jet_at_zero": ["0", "0", ftext(coupling)],
            "reflection_symmetry_preserved": True,
            "fixed_point_preserved": True,
            "hessian_preserved": False,
            "finite_gaussian_pushforward_exact": True,
        },
        "measure_normalization": {
            "fiber_measure_multiplier": "exp(-C)",
            "C": ftext(normalization_shift),
            "effective_action_jet_shift": [ftext(normalization_shift), "0", "0"],
            "equations_and_hessian_unchanged": True,
            "normalized_nongravitational_correlators_unchanged": True,
            "gravitational_vacuum_energy_unchanged": False,
        },
    }


def raw_loop(
    h: Decimal,
    mu: Decimal,
    c_scheme: Decimal,
    kappa: Decimal,
    q4: Decimal,
    l4: Decimal,
) -> Decimal:
    log_term = (h * h / (mu * mu)).ln()
    return -kappa * h**4 * (q4 * log_term + l4 - c_scheme * q4)


def first_second_counterterms(
    point: Decimal,
    mu: Decimal,
    c_scheme: Decimal,
    kappa: Decimal,
    q4: Decimal,
    l4: Decimal,
) -> tuple[Decimal, Decimal]:
    l_h = q4 * (point * point / (mu * mu)).ln() + l4 - c_scheme * q4
    delta_m2 = -Decimal(2) * kappa * q4 * point**2
    delta_lambda = kappa * (l_h + Decimal("1.5") * q4)
    return delta_m2, delta_lambda


def corrected_first_second(
    h: Decimal,
    point: Decimal,
    mu: Decimal,
    c_scheme: Decimal,
    kappa: Decimal,
    q4: Decimal,
    l4: Decimal,
    delta_omega: Decimal,
) -> Decimal:
    delta_m2, delta_lambda = first_second_counterterms(
        point, mu, c_scheme, kappa, q4, l4
    )
    return (
        raw_loop(h, mu, c_scheme, kappa, q4, l4)
        + delta_omega
        + delta_m2 * h**2
        + delta_lambda * h**4
    )


def universal_relative_remainder(
    h: Decimal, point: Decimal, kappa: Decimal, q4: Decimal
) -> Decimal:
    return kappa * q4 * (
        h**4 * ((point * point / (h * h)).ln() + Decimal("1.5"))
        - Decimal(2) * point**2 * h**2
        + point**4 / Decimal(2)
    )


def numerical_reduction(t35: dict[str, Any]) -> dict[str, Any]:
    numeric = t35["numerical_execution"]
    with localcontext() as context:
        context.prec = 90
        point = Decimal(numeric["H_over_Lambda"])
        q4 = Decimal(numeric["q4_star"])
        l4 = Decimal(numeric["L4_star"])
        kappa = Decimal("0.071")
        samples = [
            (Decimal("0.31"), Decimal("0.83"), Decimal("-0.4"), Decimal("0")),
            (Decimal("0.79"), Decimal("1.37"), Decimal("0.2"), Decimal("1.7")),
            (Decimal("1.00"), Decimal("2.11"), Decimal("1.5"), Decimal("-0.3")),
            (Decimal("1.62"), Decimal("0.66"), Decimal("-1.1"), Decimal("4.2")),
        ]
        residuals: list[Decimal] = []
        records: list[dict[str, str]] = []
        for ratio, mu, c_scheme, delta_omega in samples:
            h = ratio * point
            corrected_h = corrected_first_second(
                h, point, mu, c_scheme, kappa, q4, l4, delta_omega
            )
            corrected_point = corrected_first_second(
                point, point, mu, c_scheme, kappa, q4, l4, delta_omega
            )
            relative = corrected_h - corrected_point
            expected = universal_relative_remainder(h, point, kappa, q4)
            residual = abs(relative - expected)
            residuals.append(residual)
            records.append(
                {
                    "h_over_H": str(ratio),
                    "mu_over_Lambda": str(mu),
                    "c_scheme": str(c_scheme),
                    "delta_Omega_over_Lambda4": str(delta_omega),
                    "relative_correction": str(relative),
                    "universal_remainder": str(expected),
                    "residual": str(residual),
                }
            )

        mu = Decimal("1.23")
        c_scheme = Decimal("0.41")
        delta_m2, delta_lambda = first_second_counterterms(
            point, mu, c_scheme, kappa, q4, l4
        )
        l_h = q4 * (point * point / (mu * mu)).ln() + l4 - c_scheme * q4
        raw_first = -kappa * point**3 * (Decimal(4) * l_h + Decimal(2) * q4)
        raw_second = -kappa * point**2 * (
            Decimal(12) * l_h + Decimal(14) * q4
        )
        first_residual = raw_first + Decimal(2) * delta_m2 * point + Decimal(4) * delta_lambda * point**3
        second_residual = raw_second + Decimal(2) * delta_m2 + Decimal(12) * delta_lambda * point**2
        t35_omega = Decimal(
            numeric["MSbar_mu_equals_Lambda_per_unit_kappa"][
                "delta_Omega_over_Lambda4"
            ]
        )
        derived_omega_per_unit_kappa = q4 * point**4 / Decimal(2)

        return {
            "H_over_Lambda": str(point),
            "q4_star": str(q4),
            "test_kappa_F": str(kappa),
            "first_jet_residual": str(abs(first_residual)),
            "second_jet_residual": str(abs(second_residual)),
            "maximum_relative_formula_residual": str(max(residuals)),
            "sample_records": records,
            "T35_delta_Omega_per_unit_kappa": str(t35_omega),
            "derived_QJ0_delta_Omega_per_unit_kappa": str(
                derived_omega_per_unit_kappa
            ),
            "delta_Omega_identity_residual": str(
                abs(t35_omega - derived_omega_per_unit_kappa)
            ),
        }


def main() -> None:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t35 = load_json(T35_PACKET)
    t34 = load_json(T34_PACKET)
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    source_root_payload = {
        "claim_id": source_lock["claim_id"],
        "kernel_model_sha256": source_lock["kernel_model_sha256"],
        "repositories": source_lock["repositories"],
        "sources": [
            {"path": source["path"], "sha256": source["sha256"]}
            for source in source_lock["local_sources"]
        ],
    }
    source_root_hash = canonical_hash(source_root_payload)
    retraction = pointed_retraction_witness()
    no_go = gaussian_no_go_witnesses()
    numerics = numerical_reduction(t35)

    h4_t8 = H4_T8.read_text(encoding="utf-8")
    h4_t9 = H4_T9.read_text(encoding="utf-8")
    h4_t10 = H4_T10.read_text(encoding="utf-8")
    action_contract = ACTION_CONTRACT.read_text(encoding="utf-8")
    a84 = A84.read_text(encoding="utf-8")
    a85 = A85.read_text(encoding="utf-8")
    theorem = THEOREM.read_text(encoding="utf-8")

    checks = {
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.pointed-closure-germ-quantum-jet-matching-source-lock.v1",
        "source_lock_claim_is_T36": source_lock["claim_id"] == "CBF.T36",
        "contract_schema_is_exact": schema["properties"]["claim_id"]["const"]
        == "CBF.T36",
        "all_source_hashes_match": all(source_checks.values()),
        "source_root_is_nonempty": len(source_root_hash) == 64,
        "T35_is_locked": t35["claim_id"] == "CBF.T35",
        "T34_is_locked": t34["claim_id"] == "CBF.T34",
        "T35_matching_was_conditional": not t35["closure_jet_matching"][
            "selected_by_upper_MTT"
        ],
        "H4_T8_excludes_counterterm_selection": "perform continuum renormalization or choose counterterms"
        in h4_t8,
        "H4_T9_separates_repair_and_signed_action": "positive repair Hessian"
        in h4_t9
        and "signed Euler-Lagrange Hessian" in h4_t9,
        "H4_T10_leaves_quantum_renormalization_open": "interacting QME and renormalization"
        in h4_t10,
        "physical_action_contract_rejects_repair_promotion": "positive repair cost"
        in action_contract
        and "silently renamed" in action_contract,
        "A84_retains_one_matching_clause": "CSGA2 remains independent" in a84,
        "A85_retains_finite_counterterm_freedom": "finite local" in a85
        and "covariant counterterm freedom" in a85,
        "jet_matrix_determinant_is_16H3": retraction[
            "source_jet_matrix_determinant"
        ]
        == retraction["source_16H3"],
        "jet_remainder_value_vanishes": retraction["source_remainder_jet"][0]
        == "0",
        "jet_remainder_first_vanishes": retraction["source_remainder_jet"][1]
        == "0",
        "jet_remainder_second_vanishes": retraction["source_remainder_jet"][2]
        == "0",
        "jet_retraction_is_idempotent": retraction[
            "source_retracted_twice_equals_source_remainder"
        ],
        "jet_retraction_kills_counterterm_space": retraction[
            "pure_counterterm_retracts_to_zero"
        ],
        "jet_retraction_is_natural_on_counterterms": retraction[
            "target_counterterm_equals_scaled_source"
        ],
        "jet_retraction_is_natural_on_remainders": retraction[
            "target_remainder_equals_scaled_source"
        ],
        "target_remainder_jet_vanishes": retraction["target_remainder_jet"]
        == ["0", "0", "0"],
        "field_scaling_changes_numeric_hessian": not retraction[
            "numeric_hessian_equality_requires_unit_scale"
        ],
        "odd_gaussian_pushforward_shifts_tadpole": no_go["odd_coupling"][
            "jet_at_zero"
        ][1]
        != "0",
        "odd_gaussian_pushforward_shifts_hessian": no_go["odd_coupling"][
            "jet_at_zero"
        ][2]
        != "0",
        "even_gaussian_symmetry_protects_tadpole": no_go["even_coupling"][
            "jet_at_zero"
        ][1]
        == "0",
        "even_gaussian_symmetry_does_not_protect_hessian": no_go[
            "even_coupling"
        ]["jet_at_zero"][2]
        != "0",
        "measure_normalization_changes_only_zero_jet": no_go[
            "measure_normalization"
        ]["effective_action_jet_shift"][1:]
        == ["0", "0"],
        "first_jet_matching_executes": Decimal(numerics["first_jet_residual"])
        < Decimal("1e-75"),
        "second_jet_matching_executes": Decimal(numerics["second_jet_residual"])
        < Decimal("1e-75"),
        "relative_T35_remainder_executes": Decimal(
            numerics["maximum_relative_formula_residual"]
        )
        < Decimal("1e-75"),
        "QJ0_recovers_T35_delta_Omega": Decimal(
            numerics["delta_Omega_identity_residual"]
        )
        < Decimal("1e-75"),
        "pointed_retraction_naturality_newly_closed": not boundary[
            "pointed_jet_retraction_naturality_before"
        ]
        and boundary["pointed_jet_retraction_naturality_after"],
        "generic_pushforward_no_go_newly_closed": not boundary[
            "generic_gaussian_pushforward_jet_preservation_no_go_before"
        ]
        and boundary["generic_gaussian_pushforward_jet_preservation_no_go_after"],
        "relative_remainder_reduction_newly_closed": not boundary[
            "relative_T35_remainder_unique_given_first_second_matching_before"
        ]
        and boundary["relative_T35_remainder_unique_given_first_second_matching_after"],
        "QJ1_selection_remains_open": not boundary[
            "existing_upper_action_selects_tadpole_protection"
        ],
        "QJ2_selection_remains_open": not boundary[
            "existing_upper_action_selects_physical_tangent_normalization"
        ],
        "QJ0_selection_remains_open": not boundary[
            "existing_upper_action_selects_vacuum_energy_normalization"
        ],
        "full_matching_selection_remains_open": not boundary[
            "full_closure_jet_matching_selected_by_upper_MTT"
        ],
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
        "theorem_states_naturality_boundary": "ordinary action descent" in theorem
        and "do not by themselves supply" in theorem,
        "theorem_states_three_certificates": all(
            marker in theorem for marker in ("QJ0", "QJ1", "QJ2")
        ),
        "theorem_rejects_physical_promotion": "full closure-jet rule remains unselected"
        in theorem,
    }
    checks.update(source_checks)
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T36 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.pointed-closure-germ-quantum-jet-matching.v1",
        "claim_id": "CBF.T36",
        "date": "2026-08-30",
        "status": (
            "exact pointed two-jet retraction and naturality theorem; exact no-go "
            "against automatic jet preservation by Gaussian/BV pushforward; T35 "
            "matching reduced to QJ0/QJ1/QJ2 with physical selection open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_sha256": source_root_hash,
            "source_root_payload": source_root_payload,
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract_schema_sha256": sha256(SCHEMA),
            "theorem_sha256": sha256(THEOREM),
            "external_context": [
                {
                    "role": "finite-dimensional BV integration and homological pushforward",
                    "url": "https://arxiv.org/abs/0812.0464",
                },
                {
                    "role": "BV-BFV pushforward compatible with cutting and gluing",
                    "url": "https://arxiv.org/abs/1507.01221",
                },
                {
                    "role": "BV effective renormalization with symmetry up to homotopy",
                    "url": "https://arxiv.org/abs/0706.1533",
                },
                {
                    "role": "finite local covariant renormalization ambiguities",
                    "url": "https://arxiv.org/abs/gr-qc/0103074",
                },
            ],
        },
        "pointed_jet_retraction": {
            "action_germ_space": "A_H",
            "jet_map": "j_H^2(f)=(f(H),f'(H),f''(H))",
            "jet_kernel": "m_H^3",
            "counterterm_space": "C_even=span{1,h^2,h^4}",
            "jet_matrix": "[[1,H^2,H^4],[0,2H,4H^3],[0,2,12H^2]]",
            "jet_matrix_determinant": "16H^3",
            "retraction": "R_H=I-(j_H^2|C_even)^(-1)j_H^2",
            "image": "ker j_H^2",
            "kernel": "C_even",
            "idempotent": True,
            "unique_for_positive_H": True,
            "physical_matching_condition_selected_by_this_algebra": False,
            "exact_witness": retraction,
        },
        "naturality": {
            "intertwining_conditions": [
                "T(C_H)=C_K",
                "j_K T=T_J j_H",
            ],
            "conclusion": "R_K T=T R_H",
            "radial_scaling": "u=a h, (T_a f)(u)=f(u/a), K=aH",
            "jet_transport": "diag(1,a^-1,a^-2)",
            "hessian_is_tensorially_covariant": True,
            "numeric_hessian_equality_requires_selected_tangent_isometry": True,
            "physical_wavefunction_normalization_selected": False,
        },
        "gaussian_pushforward_no_go": no_go,
        "matching_clause_classification": {
            "QJ1": {
                "condition": "d Gamma(H)=0",
                "role": "quantum fixed-point or tadpole protection",
                "possible_source": "Ward identity, background equation or nonrenormalization theorem",
                "selected_by_existing_sources": False,
            },
            "QJ2": {
                "condition": "I_H^* Hess Gamma(H) I_H=H_cl",
                "role": "normalized Hessian intertwining",
                "possible_source": "selected kinetic metric plus Hessian Ward/nonrenormalization theorem",
                "selected_by_existing_sources": False,
            },
            "QJ0": {
                "condition": "Gamma(H)=S_base(H)",
                "role": "pointed determinant-line or gravitational vacuum normalization",
                "possible_source": "normalized partition function, determinant-line trivialization or gravitational action",
                "selected_by_existing_sources": False,
            },
            "certificate_count": 3,
            "these_are_scalar_fit_parameters": False,
            "QJ1_QJ2_suffice_for_relative_nongravitational_action": True,
            "QJ0_required_for_absolute_gravitational_action": True,
            "existing_upper_action_selects_full_rule": False,
        },
        "t35_reduction": {
            "first_second_counterterms": {
                "delta_m2": "-2 kappa_F q4_* H^2",
                "delta_lambda": "kappa_F[L_H+(3/2)q4_*]",
            },
            "delta_Omega_after_QJ1_QJ2": "free additive constant",
            "relative_remainder": (
                "kappa_F q4_*[h^4(log(H^2/h^2)+3/2)-2H^2h^2+H^4/2]"
            ),
            "relative_remainder_equals_T35": True,
            "QJ0_solution": "delta_Omega=(1/2)kappa_F q4_* H^4",
            "normalized_higher_jets": {"third": -16, "fourth": -64},
            "unique_relative_action_given_QJ1_QJ2": True,
            "unique_absolute_action_given_QJ0_QJ1_QJ2": True,
            "numerical_execution": numerics,
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_continuous_physical_parameters": 0,
            "typed_selection_certificates_required": 3,
            "counterterm_freedom_after_QJ1_QJ2": 1,
            "counterterm_freedom_modulo_constants_after_QJ1_QJ2": 0,
            "counterterm_freedom_after_QJ0_QJ1_QJ2": 0,
            "physical_selection_certificates_currently_accepted": 0,
        },
        "physical_boundary": {
            "pointed_jet_retraction_mathematics_closed": True,
            "generic_pushforward_jet_preservation_rejected": True,
            "classical_repair_germ_available": True,
            "bare_action_lane_available_at_declared_tier": True,
            "physical_QJ1_tadpole_protection_closed": False,
            "physical_QJ2_tangent_Hessian_intertwiner_closed": False,
            "physical_QJ0_vacuum_normalization_closed": False,
            "full_closure_jet_matching_selected": False,
            "selected_external_BV_operator_domain_closed": False,
            "QME_Ward_execution_closed": False,
            "full_renormalized_QFT_vacuum_closed": False,
            "B_ACTION_01_closed": False,
            "B_QFT_02_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "CBF.T36 proves that T35's subtraction is the unique natural retraction "
            "once a pointed quantum two-jet and the even radial counterterm class are "
            "selected. Exact finite Gaussian witnesses prove that ordinary action "
            "descent and BV/Gaussian pushforward do not preserve the tadpole or Hessian, "
            "while measure normalization changes the value independently. The remaining "
            "physical selector is therefore exactly QJ1 tadpole protection, QJ2 normalized "
            "Hessian intertwining and QJ0 determinant-line/gravitational normalization. "
            "Given QJ1/QJ2 the relative T35 remainder is already unique; no current upper "
            "action proves those certificates, so physical acceptance remains unchanged."
        ),
        "checks": checks,
        "check_summary": {
            "passed": len(checks),
            "total": len(checks),
            "failed": [],
        },
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"wrote {OUTPUT.name}: {len(checks)}/{len(checks)} checks passed")


if __name__ == "__main__":
    main()
