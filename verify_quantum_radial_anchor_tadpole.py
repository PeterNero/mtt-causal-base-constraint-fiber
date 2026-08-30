#!/usr/bin/env python3
"""Independently verify the CBF.T37 quantum radial-anchor packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"
SOURCE_LOCK = ROOT / "quantum_radial_anchor_tadpole_source_lock.json"
SCHEMA = ROOT / "quantum_radial_anchor_tadpole_contract.schema.json"
THEOREM = ROOT / "QuantumRadialAnchorWardIdentityAndTadpoleSelectionBoundaryTheorem_v1.md"
T35_PACKET = ROOT / "frozen_source_four_dimensional_fermion_pushforward.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def fraction(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", maxsplit=1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text))


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
    check("packet_claim", packet["claim_id"] == "CBF.T37")
    check("source_lock_claim", source_lock["claim_id"] == "CBF.T37")
    check("builder_checks", all(packet["checks"].values()))
    check(
        "builder_summary",
        packet["check_summary"]["passed"] == packet["check_summary"]["total"]
        and packet["check_summary"]["failed"] == [],
    )
    provenance = packet["source_provenance"]
    check("theorem_hash", provenance["theorem_sha256"] == sha256(THEOREM))
    check("schema_hash", provenance["contract_schema_sha256"] == sha256(SCHEMA))
    check("source_lock_hash", provenance["source_lock_sha256"] == sha256(SOURCE_LOCK))
    check("handoff_id", provenance["handoff_id"] == source_lock["handoff_id"])

    source_matches = True
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        matched = path.is_file() and sha256(path) == source["sha256"]
        check(f"source_{index:02d}_hash", matched)
        source_matches &= matched
    check("all_source_hashes", source_matches)
    root_payload = provenance["source_root_payload"]
    check("source_root_hash", canonical_hash(root_payload) == provenance["source_root_sha256"])
    check("source_root_repositories", root_payload["repositories"] == source_lock["repositories"])

    identity = packet["differentiated_pushforward_identity"]
    witness = identity["exact_finite_witness"]
    hbar = fraction(witness["hbar"])
    weights = [fraction(value) for value in witness["fiber_probabilities_at_reference"]]
    action = [fraction(value) for value in witness["action_radial_derivatives"]]
    anomaly = [fraction(value) for value in witness["log_density_radial_derivatives"]]
    insertion = [ds - hbar * da for ds, da in zip(action, anomaly)]
    derivative = sum(
        (weight * value for weight, value in zip(weights, insertion)), Fraction(0)
    )
    check("probabilities_normalized", sum(weights, Fraction(0)) == 1)
    check(
        "pushforward_insertions",
        insertion == [fraction(value) for value in witness["covariant_insertions"]],
    )
    check(
        "pushforward_derivative",
        derivative == fraction(witness["effective_action_radial_derivative"]),
    )
    check("pushforward_derivative_nonzero", derivative != 0)
    check("cycle_boundary_zero_in_witness", fraction(witness["cycle_boundary_term_in_witness"]) == 0)
    centered = [fraction(value) for value in witness["centered_involution_insertions"]]
    check("centered_pair_is_odd", centered[0] == -centered[1])
    check(
        "centered_expectation_zero",
        sum((weight * value for weight, value in zip(weights, centered)), Fraction(0))
        == fraction(witness["centered_involution_expectation"])
        == 0,
    )
    check("projection_contract_has_state", "state or expectation functional" in identity["projection_contract_must_include"])
    check("projection_contract_has_measure", "measure or determinant half-density" in identity["projection_contract_must_include"])

    mechanisms = packet["QJ1_mechanisms"]
    for name in (
        "pointwise_horizontal_stationarity",
        "quantum_BV_exact_insertion",
        "centered_involution",
        "zero_source_state_anchor",
    ):
        check(f"mechanism_{name}_sufficient", mechanisms[name]["sufficient"])
    check(
        "pointwise_mechanism_open",
        not mechanisms["pointwise_horizontal_stationarity"]["present_in_current_MTT"],
    )
    check(
        "radial_primitive_open",
        not mechanisms["quantum_BV_exact_insertion"]["radial_primitive_Psi_H_emitted"],
    )
    check(
        "ordinary_broken_branch_not_centered",
        not mechanisms["centered_involution"]["ordinary_h_to_minus_h_centers_nonzero_branch"],
    )

    orbit = packet["QME_normalization_orbit"]
    point = fraction(orbit["test_point_H"])
    target = fraction(orbit["target_tadpole_shift"])
    solutions: list[tuple[Fraction, Fraction]] = []
    for name in ("first_solution", "second_solution"):
        record = orbit[name]
        a = fraction(record["a"])
        b = fraction(record["b"])
        shift = 2 * a * point + 4 * b * point**3
        solutions.append((a, b))
        check(f"{name}_shift", shift == target == fraction(record["shift"]))
    check("solutions_distinct", solutions[0] != solutions[1])
    kernel_vector = (Fraction(-2) * point**2, Fraction(1))
    check(
        "QJ1_kernel_vector",
        2 * kernel_vector[0] * point + 4 * kernel_vector[1] * point**3 == 0,
    )
    check("tadpole_map_rank_one", orbit["tadpole_map_rank"] == 1)
    check("nonconstant_kernel_one", orbit["nonconstant_kernel_dimension"] == 1)
    check("QME_compatible", orbit["QJ1_compatible_formal_QME_scheme_exists"])
    check("QME_not_selective", not orbit["QME_uniquely_selects_QJ1"])

    state = packet["state_anchor_reduction"]
    state_witness = mechanisms["zero_source_state_anchor"]["exact_witness"]
    h_anchor = fraction(state_witness["H"])
    variance = fraction(state_witness["sigma_squared"])
    source = fraction(state_witness["test_J"])
    phi = h_anchor + variance * source
    recovered = (phi - h_anchor) / variance
    check("state_test_phi", phi == fraction(state_witness["test_phi"]))
    check("Legendre_source_recovered", recovered == source == fraction(state_witness["recovered_dGamma_dphi"]))
    check("zero_source_anchor", fraction(state_witness["zero_source_Gamma_prime_at_H"]) == 0)
    check("state_space_nonempty", state["current_q79_state_space_nonempty"])
    check("state_transport_closed", state["current_q79_state_transport_closed"])
    check("preferred_state_open", not state["current_q79_preferred_interacting_state_selected"])
    check("anchor_equality_open", not state["current_H_T34_anchor_equality_closed"])
    check("certificate_not_scalar_fit", not state["QJ1_is_independent_scalar_fit_parameter"])

    execution = packet["T35_tadpole_execution"]
    numeric = t35["numerical_execution"]
    with localcontext() as context:
        context.prec = 90
        sqrt13 = Decimal(13).sqrt()
        q4 = (Decimal(356) + Decimal(25) * sqrt13) / Decimal(27)
        sigmas = (
            (Decimal(2) + sqrt13) / Decimal(3),
            (Decimal(5) + sqrt13) / Decimal(6),
            (Decimal(7) - sqrt13) / Decimal(6),
        )
        l4 = sum(sigma**4 * (sigma**2).ln() for sigma in sigmas)
        h2 = (
            Decimal(15)
            * (Decimal(3106) + Decimal(4) * sqrt13)
            / (Decimal(4393) * Decimal(448).ln())
        )
        h = h2.sqrt()
        c_scheme = Decimal(execution["c_scheme"])
        l_h = q4 * h2.ln() + l4 - c_scheme * q4
        obstruction = Decimal(2) * l_h + q4
        tadpole = -Decimal(2) * h**3 * obstruction
        qj1_line = h2 * obstruction
        delta_m2 = -Decimal(2) * q4 * h2
        delta_lambda = l_h + Decimal("1.5") * q4
        reconstructed_line = delta_m2 + Decimal(2) * h2 * delta_lambda
        mu_tad_over_h = ((l4 / q4 - c_scheme + Decimal("0.5")) / Decimal(2)).exp()
        mu_tad_over_lambda = mu_tad_over_h * h
        tolerance = Decimal("1e-75")
        check("sqrt13_recomputed", abs(sqrt13 - Decimal(execution["sqrt13"])) < tolerance)
        check("q4_recomputed", abs(q4 - Decimal(execution["q4_star"])) < tolerance)
        check("l4_recomputed", abs(l4 - Decimal(execution["L4_star"])) < tolerance)
        check("h_recomputed", abs(h - Decimal(execution["H_over_Lambda"])) < tolerance)
        check("h2_recomputed", abs(h2 - Decimal(execution["H_squared_over_Lambda_squared"])) < tolerance)
        check("l_h_recomputed", abs(l_h - Decimal(execution["L_H"])) < tolerance)
        check("obstruction_recomputed", abs(obstruction - Decimal(execution["two_L_H_plus_q4"])) < tolerance)
        check("tadpole_recomputed", abs(tadpole - Decimal(execution["bare_tadpole_over_kappa_Lambda3"])) < tolerance)
        check("tadpole_nonzero", abs(tadpole) > Decimal(1))
        check("qj1_line_recomputed", abs(qj1_line - Decimal(execution["QJ1_counterterm_line_right_side_over_kappa_Lambda2"])) < tolerance)
        check("T35_pair_reconstructs_line", abs(reconstructed_line - qj1_line) < tolerance)
        check("T35_delta_m2", abs(delta_m2 - Decimal(execution["T35_delta_m2_over_kappa_Lambda2"])) < tolerance)
        check("T35_delta_lambda", abs(delta_lambda - Decimal(execution["T35_delta_lambda_over_kappa"])) < tolerance)
        check("mu_tad_over_h", abs(mu_tad_over_h - Decimal(execution["mu_tad_over_H"])) < tolerance)
        check("mu_tad_over_lambda", abs(mu_tad_over_lambda - Decimal(execution["mu_tad_over_Lambda"])) < tolerance)
        l_at_mu_tad = q4 * (h2 / mu_tad_over_lambda**2).ln() + l4 - c_scheme * q4
        check("mu_tad_zeros_bare_tadpole", abs(Decimal(2) * l_at_mu_tad + q4) < tolerance)
        complex_kappa = Decimal(numeric["determinant_normalization_candidates"]["complex_determinant"]["kappa_F"])
        pfaffian_kappa = Decimal(numeric["determinant_normalization_candidates"]["pfaffian_half"]["kappa_F"])
        check("complex_tadpole", abs(tadpole * complex_kappa - Decimal(execution["bare_tadpole_complex_over_Lambda3"])) < tolerance)
        check("pfaffian_tadpole", abs(tadpole * pfaffian_kappa - Decimal(execution["bare_tadpole_pfaffian_over_Lambda3"])) < tolerance)
        check("both_branches_nonzero", tadpole * complex_kappa != 0 and tadpole * pfaffian_kappa != 0)

    ledger = packet["parameter_ledger"]
    check("no_observed_inputs", ledger["new_observed_construction_inputs"] == 0)
    check("no_fits", ledger["new_fitted_coefficients"] == 0)
    check("no_new_physical_parameters", ledger["new_continuous_physical_parameters"] == 0)
    check("QJ1_leaves_one_nonconstant_direction", ledger["QJ1_nonconstant_counterterm_freedom_before_QJ2"] == 1)
    check("QJ0_constant_still_open", ledger["additive_constant_freedom_before_QJ0"] == 1)
    check("state_datum_missing", ledger["selected_interacting_state_data_still_missing"] == 1)

    physical = packet["physical_boundary"]
    for key in (
        "differentiated_pushforward_identity_closed",
        "QJ1_sufficient_mechanisms_classified",
        "formal_QME_compatible_QJ1_scheme_exists",
        "T35_bare_tadpole_obstruction_executed",
        "QJ1_reduced_to_same_source_state_anchor",
    ):
        check(f"closed_{key}", physical[key])
    for key in (
        "QME_or_gauge_naturality_selects_QJ1",
        "selected_interacting_q79_state_closed",
        "H_T34_state_anchor_equality_closed",
        "radial_BV_Ward_primitive_closed",
        "physical_QJ1_tadpole_protection_closed",
        "physical_QJ2_tangent_Hessian_intertwiner_closed",
        "physical_QJ0_vacuum_normalization_closed",
        "full_closure_jet_matching_selected",
        "B_ACTION_01_closed",
        "B_QFT_02_closed",
    ):
        check(f"open_{key}", not physical[key])
    check("packet_acceptance", packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3)
    check("row_acceptance", packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7)

    check(
        "theorem_pushforward_formula",
        "Gamma'(H)" in theorem
        and "<D_H S-hbar A_H>_H+B_H/Z(H)" in theorem,
    )
    check("theorem_QME_boundary", "QME uniquely selects QJ1:             no" in theorem)
    check("theorem_state_anchor", "H_state=H_T34" in theorem)
    check("theorem_tadpole_number", "-100.1144836274302795882555068876969" in theorem)
    check("theorem_acceptance_boundary", "formal QJ1 compatibility is closed but physical QJ1 selection is" in theorem)

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T37 independent verification failed: {failed}")
    print(f"verified {PACKET.name}: {len(checks)}/{len(checks)} independent checks passed")


if __name__ == "__main__":
    main()
