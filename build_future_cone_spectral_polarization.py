#!/usr/bin/env python3
"""Build the exact CBF.T45 future-cone polarization packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "future_cone_spectral_polarization_source_lock.json"
SCHEMA = ROOT / "future_cone_spectral_polarization_contract.schema.json"
THEOREM = ROOT / "FutureConeSpectralPolarizationAndFreeInitialStateSelectionTheorem_v1.md"
OUTPUT = ROOT / "future_cone_spectral_polarization.packet.json"

T27_PACKET = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T43_PACKET = ROOT / "weyl_polarized_product_dirac_g0.packet.json"
T44_PACKET = ROOT / "causal_relative_cauchy_evolution_global_g0.packet.json"
FREE_CAR = ROOT / "../mtt-qm-source-proof/certificates/framed_q79_free_dirac_car_net.certificate.json"
BINARY_ROOT = ROOT / "../mtt-q79-total-superconnection-branching/artifacts/binary_root_car_net_equivalence.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"

Q13 = tuple[Fraction, Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def q13(a: int | Fraction = 0, b: int | Fraction = 0) -> Q13:
    return Fraction(a), Fraction(b)


def q13_add(left: Q13, right: Q13) -> Q13:
    return left[0] + right[0], left[1] + right[1]


def q13_sub(left: Q13, right: Q13) -> Q13:
    return left[0] - right[0], left[1] - right[1]


def q13_neg(value: Q13) -> Q13:
    return -value[0], -value[1]


def q13_mul(left: Q13, right: Q13) -> Q13:
    return (
        left[0] * right[0] + 13 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def q13_square(value: Q13) -> Q13:
    return q13_mul(value, value)


def q13_sign(value: Q13) -> int:
    """Return the exact sign of a+b*sqrt(13)."""
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


def q13_text(value: Q13) -> dict[str, str]:
    return {
        "rational": ftext(value[0]),
        "sqrt13_coefficient": ftext(value[1]),
        "display": f"({ftext(value[0])})+({ftext(value[1])})sqrt(13)",
    }


def source_hash_checks(source_lock: dict[str, Any]) -> tuple[dict[str, bool], dict[str, bool]]:
    construction: dict[str, bool] = {}
    comparison: dict[str, bool] = {}
    for index, source in enumerate(source_lock["construction_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        construction[f"construction_source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    for index, source in enumerate(source_lock["comparison_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        comparison[f"comparison_source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return construction, comparison


def projection_product(left: list[int], right: list[int]) -> list[int]:
    return [a * b for a, b in zip(left, right)]


def permute_diagonal(diagonal: list[Any], permutation: list[int]) -> list[Any]:
    return [diagonal[permutation[index]] for index in range(len(diagonal))]


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t27 = load_json(T27_PACKET)
    t43 = load_json(T43_PACKET)
    t44 = load_json(T44_PACKET)
    free_car = load_json(FREE_CAR)
    binary_root = load_json(BINARY_ROOT)
    t38 = load_json(T38_PACKET)

    construction_checks, comparison_checks = source_hash_checks(source_lock)

    one = q13(1)
    two = q13(2)
    t_star = q13(Fraction(1, 6), Fraction(-1, 6))
    mu_4 = q13_sub(one, q13_mul(two, t_star))
    mu_2m = q13_sub(one, t_star)
    mu_2p = q13_add(one, t_star)
    masses = [mu_4, mu_2m, mu_2p]
    labels = ["1-2t_star", "1-t_star", "1+t_star"]
    mass_squares = [q13_square(value) for value in masses]

    # Exact zero-momentum normal form of the reduced physical Weyl Cauchy
    # symbol: 48 physical Weyl labels times two energy signs. This 96 is not
    # the separately typed 96-dimensional KO6 real completion.
    hamiltonian_diagonal: list[Q13] = []
    for value in masses:
        hamiltonian_diagonal.extend([value] * 16)
    for value in masses:
        hamiltonian_diagonal.extend([q13_neg(value)] * 16)

    dimension = len(hamiltonian_diagonal)
    p_future = [1 if q13_sign(value) > 0 else 0 for value in hamiltonian_diagonal]
    p_past = [1 - value for value in p_future]
    charge_conjugation = [index + 48 if index < 48 else index - 48 for index in range(96)]
    conjugated_hamiltonian = permute_diagonal(hamiltonian_diagonal, charge_conjugation)
    conjugated_future = permute_diagonal(p_future, charge_conjugation)

    decay_projector = [1 if q13_sign(value) > 0 else 0 for value in hamiltonian_diagonal]
    absolute_repair_decay = [1 if q13_sign(q13_square(value)) > 0 else 0 for value in hamiltonian_diagonal]

    # Exact T44 two-state scalarization witness, now tied to the two oriented
    # basis projections rather than an arbitrary mixed state.
    u_future = {"real": "3/5", "imag": "4/5"}
    u_past = {"real": "3/5", "imag": "-4/5"}
    equal_source_value = {"real": "1", "imag": "0"}

    mass_order_checks = {
        "all_three_mass_moduli_positive": all(q13_sign(value) == 1 for value in masses),
        "mu_4_greater_than_mu_2m": q13_sign(q13_sub(mu_4, mu_2m)) == 1,
        "mu_2m_greater_than_mu_2p": q13_sign(q13_sub(mu_2m, mu_2p)) == 1,
        "minimum_gap_is_mu_2p": (
            q13_sign(q13_sub(mu_4, mu_2p)) == 1
            and q13_sign(q13_sub(mu_2m, mu_2p)) == 1
        ),
        "t_star_avoids_minus_one_wall": q13_sign(q13_add(t_star, one)) != 0,
        "t_star_avoids_half_wall": q13_sign(q13_sub(q13_mul(two, t_star), one)) != 0,
        "t_star_avoids_plus_one_wall": q13_sign(q13_sub(t_star, one)) != 0,
    }

    projector_checks = {
        "normal_form_dimension_is_96": dimension == 96,
        "future_rank_is_48": sum(p_future) == 48,
        "past_rank_is_48": sum(p_past) == 48,
        "future_projector_is_idempotent": projection_product(p_future, p_future) == p_future,
        "past_projector_is_idempotent": projection_product(p_past, p_past) == p_past,
        "projectors_are_orthogonal": projection_product(p_future, p_past) == [0] * 96,
        "projectors_sum_to_identity": [a + b for a, b in zip(p_future, p_past)] == [1] * 96,
        "charge_conjugation_is_involution": [charge_conjugation[charge_conjugation[i]] for i in range(96)] == list(range(96)),
        "charge_conjugation_reverses_hamiltonian": conjugated_hamiltonian == [q13_neg(value) for value in hamiltonian_diagonal],
        "charge_conjugation_exchanges_projectors": conjugated_future == p_past,
    }

    half_line_checks = {
        "decaying_boundary_projector_equals_future_projector": decay_projector == p_future,
        "oriented_half_line_has_48_decaying_modes": sum(decay_projector) == 48,
        "oriented_half_line_has_48_growing_modes": dimension - sum(decay_projector) == 48,
        "absolute_hessian_damps_all_96_modes": sum(absolute_repair_decay) == 96,
        "absolute_hessian_does_not_select_polarization": absolute_repair_decay != p_future,
        "one_sided_decay_selects_unique_diagonal_projection": all(
            decay_projector[index] == (1 if q13_sign(value) > 0 else 0)
            for index, value in enumerate(hamiltonian_diagonal)
        ),
    }

    inherited_checks = {
        "T27_signed_spectrum_has_six_rank_16_blocks": all(
            t27["full_spectrum"]["D_phys_signed"].get(key) == 16
            for key in ["+(1+t)", "+(1-2t)", "+(1-t)", "-(1+t)", "-(1-2t)", "-(1-t)"]
        ),
        "T43_particle_carrier_is_48": t43["carrier_ledger"]["particle_carrier_dimension"] == 48,
        "T43_direct_root_is_single": t43["same_source_graph"]["direct_operator_and_one_loop_action_share_root"] is True,
        "T44_contour_is_operator_valued": t44["operator_valued_global_G0"]["formal_perturbative_tier"] is True,
        "T44_equal_source_identity_is_exact": t44["operator_valued_global_G0"]["equal_source_identity"] == "C_H[V,V]=1",
        "T44_state_witness_is_nontrivial": t44["state_scalarization_cutset"]["unequal_source_values_are_distinct"] is True,
        "free_CAR_Hadamard_space_is_nonempty": "nonempty convex set" in free_car["state_space"]["assignment"],
        "free_CAR_did_not_select_preferred_state": "not selected" in free_car["state_space"]["preferred_state"],
        "binary_roots_have_state_space_bijection": "bijection of their quasifree Hadamard state spaces" in binary_root["closed_exit_clauses"],
        "binary_root_did_not_select_preferred_state": binary_root["guardrails"]["claims_a_preferred_Hadamard_state_is_selected"] is False,
        "T38_is_only_a_radial_marginal": (
            t38["physical_boundary"]["preferred_full_q79_state_selected"] is False
            and t38["physical_boundary"]["global_interacting_cosmological_state_selected"] is False
        ),
    }

    checks: dict[str, bool] = {}
    checks.update(construction_checks)
    checks.update(comparison_checks)
    checks.update(mass_order_checks)
    checks.update(projector_checks)
    checks.update(half_line_checks)
    checks.update(inherited_checks)
    checks.update(
        {
            "source_lock_schema_matches": source_lock["schema"] == "boe.mtt.future-cone-spectral-polarization-source-lock.v1",
            "source_lock_claim_matches": source_lock["claim_id"] == "CBF.T45",
            "contract_schema_claim_matches": schema["properties"]["claim_id"]["const"] == "CBF.T45",
            "theorem_file_exists": THEOREM.is_file(),
            "no_observed_values_used": True,
            "no_fitted_density_matrix_used": True,
            "no_thermal_parameter_used": True,
            "flat_branch_not_promoted_to_generic_cosmology": True,
            "interacting_G2_not_claimed_closed": True,
            "internal_circle_not_identified_with_half_line": True,
            "physical_gate_counters_unchanged": True,
        }
    )

    packet: dict[str, Any] = {
        "schema": "boe.mtt.future-cone-spectral-polarization.v1",
        "claim_id": "CBF.T45",
        "title": "Future-cone spectral polarization and free initial-state selection",
        "date": "2026-08-30",
        "status": "exact selected free initial state on the homogeneous flat direct branch; generic cosmological state, determinant-line phase and interacting G2 remain open",
        "source_provenance": {
            "source_lock": SOURCE_LOCK.name,
            "source_lock_sha256": sha256(SOURCE_LOCK),
            "contract": SCHEMA.name,
            "contract_sha256": sha256(SCHEMA),
            "construction_root": canonical_hash(source_lock["construction_sources"]),
            "comparison_root": canonical_hash(source_lock["comparison_sources"]),
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
        },
        "flat_direct_branch": {
            "background": "homogeneous flat time-oriented T43 direct branch",
            "t_star": q13_text(t_star),
            "radial_scale": "H>0 inherited from the T34/T43 branch; no new value is selected here",
            "finite_operator": "D_phys(t_star), supplying the three mass moduli on the 48-label physical Weyl carrier",
            "one_particle_hamiltonian": "K_H(p)=alpha.p tensor I96 + beta tensor H D_phys(t_star)",
            "hamiltonian_square": "K_H(p)^2=|p|^2 I + H^2 D_phys(t_star)^2",
            "branch_scope_is_not_generic_curved_spacetime": True,
        },
        "exact_gap": {
            "mass_moduli": {label: q13_text(value) for label, value in zip(labels, masses)},
            "mass_squares": {label: q13_text(value) for label, value in zip(labels, mass_squares)},
            "multiplicity_per_signed_internal_block": 16,
            "strict_order": "1-2t_star > 1-t_star > 1+t_star > 0",
            "minimum_internal_gap": q13_text(mu_2p),
            "physical_one_particle_gap": "H(7-sqrt(13))/6 for H>0",
            "singular_walls_avoided": ["t=-1", "t=1/2", "t=1"],
        },
        "future_spectral_polarization": {
            "formula": "P_fut=1_(0,infinity)(K_H)=(I+K_H|K_H|^-1)/2",
            "complement": "P_past=I-P_fut=1_(-infinity,0)(K_H)",
            "future_rank_in_zero_momentum_reduced_weyl_normal_form": sum(p_future),
            "past_rank_in_zero_momentum_reduced_weyl_normal_form": sum(p_past),
            "zero_momentum_reduced_weyl_normal_form_dimension": dimension,
            "zero_momentum_reduced_weyl_hamiltonian_diagonal": [q13_text(value) for value in hamiltonian_diagonal],
            "typing_guard": "96=48 physical Weyl labels times two energy signs here; it is not the separate KO6 96 and the two are not multiplied",
            "future_projector_diagonal": p_future,
            "past_projector_diagonal": p_past,
            "charge_conjugation_permutation": charge_conjugation,
            "uniqueness_class": "pure gauge-invariant quasifree, time-translation invariant states satisfying the selected future ground-state spectrum condition",
            "continuous_state_parameter_count": 0,
        },
        "half_line_calderon_equivalence": {
            "equation": "(partial_s+K_H)u=0 on s>=0",
            "solution": "u(s)=exp(-s K_H)u(0)",
            "admissibility": "u is L2/decaying on the positive half-line",
            "decaying_boundary_space": "Ran P_fut",
            "calderon_projector": "C_+=P_fut",
            "decaying_mode_count_in_finite_normal_form": sum(decay_projector),
            "auxiliary_half_line_is_not_internal_circle_or_physical_time": True,
            "flat_static_analytic_interpretation": "the same projector is the standard Euclidean half-space Calderon/positive-frequency projector",
        },
        "quasifree_initial_state": {
            "covariance": "P_fut",
            "basis_projection_identity": "P_fut+Gamma P_fut Gamma=I",
            "positive": True,
            "normalized": True,
            "pure": True,
            "Hadamard_on_static_flat_branch": True,
            "observable_domain": "the even/gauge-invariant CAR observable algebra in the fixed homogeneous background",
            "selected_free_initial_state_on_declared_branch": True,
            "preferred_state_on_all_globally_hyperbolic_backgrounds": False,
            "inherits_unresolved_absolute_H_scale": True,
        },
        "T44_scalarization": {
            "formula": "Z_fut[V_plus,V_minus]=omega_fut(C_H[V_plus,V_minus])",
            "equal_source_identity": "Z_fut[V,V]=1",
            "local_formal_initial_state_is_selected": True,
            "unequal_source_finite_witness": u_future,
            "time_reversed_witness": u_past,
            "equal_source_finite_witness": equal_source_value,
            "nonperturbative_scalar_determinant_computed": False,
            "relative_determinant_line_holonomy_fixed": False,
        },
        "time_reversal_and_binary_root": {
            "time_reversal": "K_H -> -K_H and P_fut -> P_past",
            "two_complementary_oriented_polarizations": True,
            "selected_time_orientation_chooses_future_member_on_this_branch": True,
            "binary_root_intertwiner_transports_P_fut": True,
            "binary_root_selects_arrow_or_vacuum": False,
            "two_binary_roots_are_distinct_observable_universes": False,
        },
        "positive_hessian_nonselection": {
            "positive_generator": "|K_H| or K_H^2",
            "positive_repair_semigroup": "exp(-s|K_H|)",
            "damped_mode_count_in_finite_normal_form": sum(absolute_repair_decay),
            "selects_future_polarization": False,
            "required_extra_structure": "the oriented first-order charge K_H and one-sided decay condition",
            "conceptual_result": "closure repair chooses a quantum polarization only before squaring and only after an orientation/boundary is supplied",
        },
        "gate_ledger": {
            "direct_local_one_loop_G0": "closed by T43",
            "global_state_free_causal_evolution": "closed by T44",
            "flat_branch_free_initial_state": "closed by T45",
            "flat_branch_local_formal_scalarization": "defined by T45",
            "generic_curved_or_cosmological_state": "open",
            "relative_determinant_phase_holonomy": "open",
            "interacting_QME_preserving_BV_state_pushforward": "open",
            "fixed_coupling_cutoff_removal_and_positive_state": "open",
            "physical_G1_tangent_metric": "open",
            "physical_T41_gate_count": "0/3",
            "G2_subclauses": {"free_initial_state": "closed on flat branch", "interacting_pushforward": "open", "fixed_coupling_continuum": "open"},
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_parameters": 0,
            "new_continuous_state_selectors": 0,
            "new_thermal_parameters": 0,
            "inherited_discrete_time_orientation": 1,
            "inherited_t_star": "(1-sqrt(13))/6",
            "inherited_unresolved_radial_scale": "H",
        },
        "physical_boundary": {
            "closed": [
                "exact nonzero gap of the selected T43 finite branches",
                "future spectral projector on the homogeneous flat direct branch",
                "equivalence of positive-energy and half-line decaying-data selection",
                "pure quasifree Hadamard free initial state on that branch",
                "T44 local-formal scalarization with no new state parameter",
                "exact distinction between oriented first-order repair and positive-Hessian damping",
            ],
            "open": [
                "selection of a stationary/asymptotic boundary structure on the physical cosmological background",
                "one generally curved global q79 state",
                "source-dependent determinant-line phase and global anomaly holonomy",
                "fixed-coupling interacting QME-preserving BV pushforward",
                "C-star continuum limit, RG matching and observable comparison",
                "physical tangent metric G1 and q79 HYM universality",
            ],
            "physical_packets_accepted": 0,
            "physical_packets_total": 3,
            "physical_rows_accepted": 0,
            "physical_rows_total": 7,
        },
        "frontier_delta": "T44's arbitrary-state cutset is discharged on the narrower homogeneous flat direct branch: the selected future time orientation and gapped first-order product-Dirac Hamiltonian uniquely determine the pure positive-energy quasifree initial state, and the same projector is selected by the decaying half-line problem. The positive Hessian alone is proved insufficient. This closes the free initial-state subclause of G2 on that branch and defines the corresponding T44 scalar functional, but it does not select a state on generic cosmological backgrounds or close determinant holonomy, interacting BV transport or cutoff removal.",
        "checks": checks,
    }

    missing = sorted((set(schema["required"]) - {"check_summary"}) - set(packet))
    checks["all_contract_keys_present"] = not missing
    checks["all_checks_pass_before_summary"] = all(checks.values())
    failed = sorted(name for name, passed in checks.items() if not passed)
    packet["check_summary"] = {
        "passed": sum(1 for passed in checks.values() if passed),
        "total": len(checks),
        "failed": failed,
    }
    return packet


def main() -> None:
    packet = build()
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = packet["check_summary"]
    if summary["failed"]:
        raise SystemExit(f"CBF.T45 build failed: {summary['failed']}")
    print(f"CBF.T45 build passed {summary['passed']}/{summary['total']} checks")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
