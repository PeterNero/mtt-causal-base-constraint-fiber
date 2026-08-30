#!/usr/bin/env python3
"""Independent verifier for the CBF.T45 packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "future_cone_spectral_polarization.packet.json"
SOURCE_LOCK = ROOT / "future_cone_spectral_polarization_source_lock.json"
SCHEMA = ROOT / "future_cone_spectral_polarization_contract.schema.json"
THEOREM = ROOT / "FutureConeSpectralPolarizationAndFreeInitialStateSelectionTheorem_v1.md"

Q13 = tuple[Fraction, Fraction]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q13(a: int | Fraction = 0, b: int | Fraction = 0) -> Q13:
    return Fraction(a), Fraction(b)


def add(left: Q13, right: Q13) -> Q13:
    return left[0] + right[0], left[1] + right[1]


def sub(left: Q13, right: Q13) -> Q13:
    return left[0] - right[0], left[1] - right[1]


def neg(value: Q13) -> Q13:
    return -value[0], -value[1]


def mul(left: Q13, right: Q13) -> Q13:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def sign(value: Q13) -> int:
    a, b = value
    if a == 0 and b == 0:
        return 0
    if a >= 0 and b >= 0:
        return 1
    if a <= 0 and b <= 0:
        return -1
    comparison = a * a - 13 * b * b
    if comparison == 0:
        return 0
    if a > 0:
        return 1 if comparison > 0 else -1
    return -1 if comparison > 0 else 1


def parse_q13(payload: dict[str, str]) -> Q13:
    return Fraction(payload["rational"]), Fraction(payload["sqrt13_coefficient"])


def main() -> None:
    packet = load(PACKET)
    source_lock = load(SOURCE_LOCK)
    schema = load(SCHEMA)
    theorem = THEOREM.read_text(encoding="utf-8")
    checks: dict[str, bool] = {}

    checks["packet_schema"] = packet["schema"] == "boe.mtt.future-cone-spectral-polarization.v1"
    checks["packet_claim"] = packet["claim_id"] == "CBF.T45"
    checks["packet_date"] = packet["date"] == "2026-08-30"
    checks["lock_schema"] = source_lock["schema"] == "boe.mtt.future-cone-spectral-polarization-source-lock.v1"
    checks["lock_claim"] = source_lock["claim_id"] == "CBF.T45"
    checks["schema_claim"] = schema["properties"]["claim_id"]["const"] == "CBF.T45"
    checks["all_contract_keys"] = set(schema["required"]).issubset(packet)
    checks["source_lock_hash"] = packet["source_provenance"]["source_lock_sha256"] == digest(SOURCE_LOCK)
    checks["contract_hash"] = packet["source_provenance"]["contract_sha256"] == digest(SCHEMA)

    for group in ("construction_sources", "comparison_sources"):
        for index, source in enumerate(source_lock[group], start=1):
            path = (ROOT / source["path"]).resolve()
            checks[f"{group}_{index:02d}"] = path.is_file() and digest(path) == source["sha256"]

    t_star = parse_q13(packet["flat_direct_branch"]["t_star"])
    one = q13(1)
    two = q13(2)
    expected = {
        "1-2t_star": sub(one, mul(two, t_star)),
        "1-t_star": sub(one, t_star),
        "1+t_star": add(one, t_star),
    }
    checks["t_star_exact"] = t_star == q13(Fraction(1, 6), Fraction(-1, 6))
    masses = {name: parse_q13(value) for name, value in packet["exact_gap"]["mass_moduli"].items()}
    squares = {name: parse_q13(value) for name, value in packet["exact_gap"]["mass_squares"].items()}
    for name in expected:
        checks[f"mass_{name}_exact"] = masses[name] == expected[name]
        checks[f"square_{name}_exact"] = squares[name] == mul(expected[name], expected[name])
        checks[f"mass_{name}_positive"] = sign(masses[name]) == 1
    checks["strict_first_order"] = sign(sub(masses["1-2t_star"], masses["1-t_star"])) == 1
    checks["strict_second_order"] = sign(sub(masses["1-t_star"], masses["1+t_star"])) == 1
    checks["minimum_gap_exact"] = parse_q13(packet["exact_gap"]["minimum_internal_gap"]) == masses["1+t_star"]
    checks["all_walls_avoided"] = all(
        sign(value) != 0
        for value in (add(t_star, one), sub(mul(two, t_star), one), sub(t_star, one))
    )

    polarization = packet["future_spectral_polarization"]
    diagonal = [parse_q13(value) for value in polarization["zero_momentum_reduced_weyl_hamiltonian_diagonal"]]
    future = polarization["future_projector_diagonal"]
    past = polarization["past_projector_diagonal"]
    permutation = polarization["charge_conjugation_permutation"]
    checks["normal_form_dimension"] = len(diagonal) == len(future) == len(past) == len(permutation) == 96
    checks["future_rank"] = sum(future) == 48
    checks["past_rank"] = sum(past) == 48
    checks["future_binary"] = all(value in (0, 1) for value in future)
    checks["past_binary"] = all(value in (0, 1) for value in past)
    checks["future_matches_sign"] = future == [int(sign(value) > 0) for value in diagonal]
    checks["past_matches_sign"] = past == [int(sign(value) < 0) for value in diagonal]
    checks["projector_sum"] = [a + b for a, b in zip(future, past)] == [1] * 96
    checks["projector_product_zero"] = [a * b for a, b in zip(future, past)] == [0] * 96
    checks["future_idempotent"] = [a * a for a in future] == future
    checks["past_idempotent"] = [a * a for a in past] == past
    checks["charge_involution"] = [permutation[permutation[i]] for i in range(96)] == list(range(96))
    checks["charge_reverses_energy"] = [diagonal[permutation[i]] for i in range(96)] == [neg(value) for value in diagonal]
    checks["charge_exchanges_projection"] = [future[permutation[i]] for i in range(96)] == past
    checks["typing_guard_present"] = "not the separate KO6 96" in polarization["typing_guard"]

    half_line = packet["half_line_calderon_equivalence"]
    checks["calderon_equals_future"] = half_line["calderon_projector"] == "C_+=P_fut"
    checks["half_line_decay_count"] = half_line["decaying_mode_count_in_finite_normal_form"] == 48
    checks["half_line_type_guard"] = half_line["auxiliary_half_line_is_not_internal_circle_or_physical_time"] is True
    positive = packet["positive_hessian_nonselection"]
    checks["positive_hessian_damps_all"] = positive["damped_mode_count_in_finite_normal_form"] == 96
    checks["positive_hessian_does_not_select"] = positive["selects_future_polarization"] is False
    checks["oriented_charge_required"] = "oriented first-order charge" in positive["required_extra_structure"]

    state = packet["quasifree_initial_state"]
    checks["state_positive"] = state["positive"] is True
    checks["state_normalized"] = state["normalized"] is True
    checks["state_pure"] = state["pure"] is True
    checks["state_hadamard_flat"] = state["Hadamard_on_static_flat_branch"] is True
    checks["state_selected_flat"] = state["selected_free_initial_state_on_declared_branch"] is True
    checks["state_not_generic"] = state["preferred_state_on_all_globally_hyperbolic_backgrounds"] is False
    checks["scale_boundary_retained"] = state["inherits_unresolved_absolute_H_scale"] is True

    scalar = packet["T44_scalarization"]
    checks["scalar_formula"] = scalar["formula"] == "Z_fut[V_plus,V_minus]=omega_fut(C_H[V_plus,V_minus])"
    checks["scalar_equal_source"] = scalar["equal_source_identity"] == "Z_fut[V,V]=1"
    checks["scalar_state_selected"] = scalar["local_formal_initial_state_is_selected"] is True
    checks["future_and_past_witness_differ"] = scalar["unequal_source_finite_witness"] != scalar["time_reversed_witness"]
    checks["nonperturbative_not_claimed"] = scalar["nonperturbative_scalar_determinant_computed"] is False
    checks["phase_not_claimed"] = scalar["relative_determinant_line_holonomy_fixed"] is False

    root = packet["time_reversal_and_binary_root"]
    checks["complementary_orientations"] = root["two_complementary_oriented_polarizations"] is True
    checks["future_selected_on_branch"] = root["selected_time_orientation_chooses_future_member_on_this_branch"] is True
    checks["root_transports_state"] = root["binary_root_intertwiner_transports_P_fut"] is True
    checks["root_not_arrow_selector"] = root["binary_root_selects_arrow_or_vacuum"] is False
    checks["root_not_two_universes"] = root["two_binary_roots_are_distinct_observable_universes"] is False

    ledger = packet["gate_ledger"]
    checks["free_initial_subclause_closed"] = ledger["G2_subclauses"]["free_initial_state"] == "closed on flat branch"
    checks["interacting_subclause_open"] = ledger["G2_subclauses"]["interacting_pushforward"] == "open"
    checks["continuum_subclause_open"] = ledger["G2_subclauses"]["fixed_coupling_continuum"] == "open"
    checks["top_gate_unchanged"] = ledger["physical_T41_gate_count"] == "0/3"
    parameters = packet["parameter_ledger"]
    checks["no_observed_inputs"] = parameters["new_observed_inputs"] == 0
    checks["no_fits"] = parameters["new_fitted_parameters"] == 0
    checks["no_continuous_state_selector"] = parameters["new_continuous_state_selectors"] == 0
    checks["no_temperature"] = parameters["new_thermal_parameters"] == 0
    checks["H_remains_inherited"] = parameters["inherited_unresolved_radial_scale"] == "H"

    boundary = packet["physical_boundary"]
    checks["packets_unchanged"] = boundary["physical_packets_accepted"] == 0 and boundary["physical_packets_total"] == 3
    checks["rows_unchanged"] = boundary["physical_rows_accepted"] == 0 and boundary["physical_rows_total"] == 7
    checks["interacting_open_text"] = any("interacting" in item for item in boundary["open"])
    checks["cosmological_open_text"] = any("cosmological" in item for item in boundary["open"])

    required_phrases = [
        "positive Hessian semigroup",
        "cannot choose the quantum vacuum",
        "not identify it with Lorentzian time",
        "top-level physical `G2` gate",
        "The final two occurrences of `96` are not multiplied",
        "generic globally hyperbolic cosmological background",
        "binary root does not select",
    ]
    for index, phrase in enumerate(required_phrases, start=1):
        checks[f"theorem_guard_{index:02d}"] = phrase in theorem

    checks["builder_checks_all_true"] = all(packet["checks"].values())
    checks["builder_summary_failed_empty"] = packet["check_summary"]["failed"] == []
    checks["builder_summary_count_consistent"] = packet["check_summary"]["passed"] == packet["check_summary"]["total"]

    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise SystemExit("CBF.T45 independent verification failed: " + ", ".join(failed))
    print(f"CBF.T45 independent verification passed {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
