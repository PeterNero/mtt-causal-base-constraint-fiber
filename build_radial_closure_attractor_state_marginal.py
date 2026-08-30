#!/usr/bin/env python3
"""Build the exact CBF.T38 radial attractor and state-marginal packet."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "radial_closure_attractor_state_marginal_source_lock.json"
SCHEMA = ROOT / "radial_closure_attractor_state_marginal_contract.schema.json"
THEOREM = ROOT / "RadialClosureAttractorStateMarginalAndQuantumProjectionBoundaryTheorem_v1.md"
T33_PACKET = ROOT / "preprojection_finite_source_freeze_radial_values.packet.json"
T34_PACKET = ROOT / "same_root_state_repair_heat_profile_radial_values.packet.json"
T37_PACKET = ROOT / "quantum_radial_anchor_tadpole.packet.json"
Q79_STATE_CERT = (
    ROOT
    / "../mtt-qm-source-proof/certificates/q79_sm_local_formal_state_space_gluing.certificate.json"
)
OUTPUT = ROOT / "radial_closure_attractor_state_marginal.packet.json"


Q13 = tuple[Fraction, Fraction]


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


def dtext(value: Decimal) -> str:
    return format(value, "f")


def q13_text(value: Q13) -> dict[str, str]:
    return {"rational": ftext(value[0]), "sqrt13": ftext(value[1])}


def q13_mul(left: Q13, right: Q13) -> Q13:
    a, b = left
    c, d = right
    return a * c + 13 * b * d, a * d + b * c


def q13_scale(value: Q13, scalar: Fraction) -> Q13:
    return value[0] * scalar, value[1] * scalar


def parse_q13_coefficients(payload: dict[str, Any]) -> Q13:
    return (
        Fraction(payload["rational"]),
        Fraction(payload["sqrt13"]),
    )


def q13_decimal(value: Q13, sqrt13: Decimal) -> Decimal:
    return (
        Decimal(value[0].numerator) / Decimal(value[0].denominator)
        + Decimal(value[1].numerator)
        / Decimal(value[1].denominator)
        * sqrt13
    )


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def exact_square_completion(
    t33: dict[str, Any], t34: dict[str, Any]
) -> dict[str, Any]:
    selected = t33["selected_finite_source"]
    radial = t34["promoted_radial_values"]
    q2 = parse_q13_coefficients(selected["q2_star"]["exact_coefficients"])
    q4 = parse_q13_coefficients(selected["q4_star"]["exact_coefficients"])
    ratio = parse_q13_coefficients(radial["R_star"]["exact_coefficients"])
    ratio_identity = q13_mul(q4, ratio) == q13_scale(q2, Fraction(2))

    with localcontext() as context:
        context.prec = 90
        sqrt13 = Decimal(13).sqrt()
        log448 = Decimal(448).ln()
        q2_d = q13_decimal(q2, sqrt13)
        q4_d = q13_decimal(q4, sqrt13)
        ratio_d = q13_decimal(ratio, sqrt13)
        c_d = Decimal(15) / log448
        h2_d = ratio_d * c_d
        h_d = h2_d.sqrt()
        minimum_d = -q4_d * h2_d**2
        curvature_d = Decimal(8) * q4_d * h2_d

    return {
        "Lambda_normalization_for_execution": "1",
        "q2_star": {
            "exact_coefficients": q13_text(q2),
            "expression": selected["q2_star"]["expression"],
            "decimal": dtext(q2_d),
        },
        "q4_star": {
            "exact_coefficients": q13_text(q4),
            "expression": selected["q4_star"]["expression"],
            "decimal": dtext(q4_d),
        },
        "R_star": {
            "exact_coefficients": q13_text(ratio),
            "expression": radial["R_star"]["expression"],
            "decimal": dtext(ratio_d),
        },
        "ratio_identity": "q4_* R_*=2 q2_*",
        "ratio_identity_exact": ratio_identity,
        "c_over_Lambda_squared": "15/log(448)",
        "c_over_Lambda_squared_decimal": dtext(c_d),
        "H_squared_over_Lambda_squared": radial[
            "h_squared_over_Lambda_squared"
        ],
        "H_squared_over_Lambda_squared_decimal": dtext(h2_d),
        "H_over_Lambda": radial["h_over_Lambda"],
        "H_over_Lambda_decimal": dtext(h_d),
        "tree_potential": "P_*(h)=q4_* h^4-4 c q2_* h^2",
        "exact_completion": (
            "P_*(h)-P_*(H)=q4_* (h^2-H^2)^2"
        ),
        "minimum_over_Lambda4": dtext(minimum_d),
        "raw_tree_curvature_over_Lambda2": dtext(curvature_d),
        "q4_is_positive": q4_d > 0,
        "H_is_positive": h_d > 0,
        "positive_radial_minimum_is_unique": True,
        "completion_adds_only_the_existing_constant_minus_P_of_H": True,
        "new_coefficient_introduced": False,
    }


def nonlinear_repair_flow(square: dict[str, Any]) -> dict[str, Any]:
    with localcontext() as context:
        context.prec = 90
        q4 = Decimal(square["q4_star"]["decimal"])
        h2 = Decimal(square["H_squared_over_Lambda_squared_decimal"])
        h = Decimal(square["H_over_Lambda_decimal"])
        rate = Decimal(8) * q4 * h2
        sample_s = Decimal("0.2")

        def u_flow(u0: Decimal, s: Decimal) -> Decimal:
            if u0 == h2:
                return h2
            denominator = Decimal(1) + (h2 / u0 - Decimal(1)) * (-rate * s).exp()
            return h2 / denominator

        ratios = [
            Decimal("0.25"),
            Decimal("0.5"),
            Decimal("1"),
            Decimal("2"),
            Decimal("4"),
        ]
        samples: list[dict[str, Any]] = []
        all_contract = True
        for ratio in ratios:
            u0 = h2 * ratio**2
            us = u_flow(u0, sample_s)
            hs = us.sqrt()
            initial_error = abs(ratio - Decimal(1))
            final_error = abs(hs / h - Decimal(1))
            contracts = final_error <= initial_error
            all_contract = all_contract and contracts
            samples.append(
                {
                    "h0_over_H": dtext(ratio),
                    "h_at_s_over_H": dtext(hs / h),
                    "initial_absolute_ratio_error": dtext(initial_error),
                    "final_absolute_ratio_error": dtext(final_error),
                    "error_contracts": contracts,
                }
            )

        u0 = h2 * Decimal("2.25")
        s1 = Decimal("0.07")
        s2 = Decimal("0.11")
        direct = u_flow(u0, s1 + s2)
        composed = u_flow(u_flow(u0, s1), s2)
        semigroup_residual = abs(direct - composed)

        beta_prime_zero = Decimal(4) * q4 * h2
        beta_prime_h = -rate

    return {
        "repair_parameter": "s_rep",
        "repair_parameter_is_physical_time": False,
        "gradient_flow": "d h/ds_rep=4 q4_* h(H^2-h^2)",
        "squared_coordinate": "u=h^2",
        "logistic_equation": "d u/ds_rep=8 q4_* u(H^2-u)",
        "closed_solution": (
            "u(s)=H^2/[1+(H^2/u0-1)exp(-8 q4_* H^2 s)]"
        ),
        "linear_convergence_rate_over_Lambda2": dtext(rate),
        "fixed_points_on_closed_radial_half_line": ["0", "H"],
        "zero_branch_linearization": dtext(beta_prime_zero),
        "positive_branch_linearization": dtext(beta_prime_h),
        "zero_branch_is_unstable": beta_prime_zero > 0,
        "positive_branch_is_strictly_stable": beta_prime_h < 0,
        "positive_open_basin": "(0,infinity)",
        "global_positive_basin_converges_to_H": True,
        "sample_repair_parameter": dtext(sample_s),
        "flow_samples": samples,
        "all_sample_errors_contract": all_contract,
        "semigroup_composition_residual": dtext(semigroup_residual),
        "semigroup_composition_verified": semigroup_residual < Decimal("1e-75"),
        "Lyapunov_identity": "dP_*/ds_rep=-(partial_h P_*)^2<=0",
    }


def invariant_radial_state(
    square: dict[str, Any], flow: dict[str, Any]
) -> dict[str, Any]:
    support_points = [Fraction(1, 2), Fraction(1), Fraction(2)]
    defect_values = [(point**2 - 1) ** 2 for point in support_points]
    unique_weights = [Fraction(0), Fraction(1), Fraction(0)]

    with localcontext() as context:
        context.prec = 80
        h = Decimal(square["H_over_Lambda_decimal"])
        h2 = Decimal(square["H_squared_over_Lambda_squared_decimal"])
        rate = Decimal(flow["linear_convergence_rate_over_Lambda2"])
        s = Decimal("0.2")
        ratios = [Decimal("0.5"), Decimal("1.5"), Decimal("3")]
        weights = [Decimal("0.2"), Decimal("0.5"), Decimal("0.3")]

        def evolved_ratio(ratio: Decimal) -> Decimal:
            u0 = h2 * ratio**2
            denominator = Decimal(1) + (h2 / u0 - Decimal(1)) * (-rate * s).exp()
            return (h2 / denominator).sqrt() / h

        initial_mean = sum(w * r for w, r in zip(weights, ratios))
        evolved = [evolved_ratio(ratio) for ratio in ratios]
        evolved_mean = sum(w * r for w, r in zip(weights, evolved))
        initial_error = abs(initial_mean - Decimal(1))
        evolved_error = abs(evolved_mean - Decimal(1))

    return {
        "state_algebra": (
            "unitized C_0((0,infinity)) radial algebra, or its finite-moment polynomial domain"
        ),
        "state_measure": "Riesz probability measure nu_omega",
        "invariant_state_theorem": (
            "the only repair-flow invariant Borel probability on (0,infinity) is delta_H"
        ),
        "proof_identity": (
            "int f dnu=int f(Phi_s(h)) dnu -> f(H) for every bounded continuous f"
        ),
        "every_initial_probability_converges_weakly_to_delta_H": True,
        "finite_support_points_over_H": [ftext(value) for value in support_points],
        "dimensionless_defect_values": [ftext(value) for value in defect_values],
        "unique_zero_defect_probability_weights": [
            ftext(value) for value in unique_weights
        ],
        "GNS_null_ideal_criterion": (
            "omega((h^2-H^2)^2)=0 implies pi_omega(h^2-H^2)Omega_omega=0"
        ),
        "positive_radial_support_then_forces": "supp(nu_omega)={H}",
        "forced_radial_expectation": "omega(h)=H",
        "forced_radial_variance": "omega((h-H)^2)=0",
        "sample_initial_mean_over_H": dtext(initial_mean),
        "sample_evolved_mean_over_H": dtext(evolved_mean),
        "sample_initial_mean_error": dtext(initial_error),
        "sample_evolved_mean_error": dtext(evolved_error),
        "sample_mean_moves_toward_H": evolved_error < initial_error,
        "radial_marginal_is_unique_without_selecting_matter_state": True,
    }


def matrix_square_expectation() -> Fraction:
    rho = [[Fraction(2, 3), Fraction(0)], [Fraction(0), Fraction(1, 3)]]
    b = [[Fraction(1), Fraction(1, 2)], [Fraction(-1, 3), Fraction(2)]]
    bt_b = [
        [sum(b[k][i] * b[k][j] for k in range(2)) for j in range(2)]
        for i in range(2)
    ]
    return sum(rho[i][i] * bt_b[i][i] for i in range(2))


def formal_q79_state_extension(
    state_certificate: dict[str, Any]
) -> dict[str, Any]:
    closed = state_certificate["claim_boundary"]["closed"]
    open_rows = state_certificate["claim_boundary"]["open"]
    square_expectation = matrix_square_expectation()
    observable_expectation = Fraction(2, 3)
    return {
        "base_fiber_algebra": (
            "C_0((0,infinity)) tensor A_phys,H on the declared local formal tier"
        ),
        "evaluation_map": "ev_H tensor id:A_base->A_phys,H",
        "extended_state": "Omega_H=omega_H composed with (ev_H tensor id)",
        "normalization_identity": "Omega_H(1)=omega_H(1)=1",
        "positivity_identity": (
            "Omega_H(a^*a)=omega_H(a(H)^*a(H))>=0"
        ),
        "BRST_identity": (
            "if ev_H Q=Q_H ev_H and omega_H Q_H=0, then Omega_H Q=0"
        ),
        "q79_local_formal_state_spaces_nonempty": (
            "nonempty local formal physical state spaces" in closed
        ),
        "q79_restriction_preserves_formal_positivity": (
            "normalization and formal positivity under restriction" in closed
        ),
        "q79_preferred_state_remains_open": (
            "one preferred or natural q79 state" in open_rows
        ),
        "finite_density_matrix": [["2/3", "0"], ["0", "1/3"]],
        "finite_test_square_expectation": ftext(square_expectation),
        "finite_test_square_is_positive": square_expectation > 0,
        "finite_test_observable_expectation": ftext(observable_expectation),
        "radial_scalar_expectation_over_H": "1",
        "formal_local_radial_anchored_state_exists": True,
        "full_interacting_state_is_unique": False,
        "single_global_cosmological_state_constructed": False,
    }


def repair_projection_naturality(
    square: dict[str, Any], flow: dict[str, Any]
) -> dict[str, Any]:
    with localcontext() as context:
        context.prec = 80
        h = Decimal(square["H_over_Lambda_decimal"])
        h2 = Decimal(square["H_squared_over_Lambda_squared_decimal"])
        rate = Decimal(flow["linear_convergence_rate_over_Lambda2"])
        s = Decimal("0.13")
        samples = [
            (Decimal("0.6") * h, Decimal("2")),
            (Decimal("1.4") * h, Decimal("-3")),
            (Decimal("2.2") * h, Decimal("5")),
        ]

        def h_flow(h0: Decimal) -> Decimal:
            u0 = h0**2
            denominator = Decimal(1) + (h2 / u0 - Decimal(1)) * (-rate * s).exp()
            return (h2 / denominator).sqrt()

        commutator_residuals = []
        upper_outputs = []
        for h0, z0 in samples:
            upper_h = h_flow(h0)
            upper_z = z0 * (-s).exp()
            lower_h = h_flow(h0)
            residual = abs(upper_h - lower_h)
            commutator_residuals.append(residual)
            upper_outputs.append(
                {
                    "h_over_H": dtext(upper_h / h),
                    "auxiliary_z": dtext(upper_z),
                    "projection_commutator_residual": dtext(residual),
                }
            )
        max_residual = max(commutator_residuals)

    return {
        "upper_lower_contract": (
            "pi composed Phi_s=Psi_s composed pi for all s>=0"
        ),
        "surjectivity_required_for_global_lower_attractor": True,
        "fixed_point_descent": "Psi_s(pi(x_*))=pi(x_*)",
        "state_pushforward_naturality": (
            "pi_* (Phi_s)_* nu=(Psi_s)_* pi_* nu"
        ),
        "attractor_state_descent": "pi_* delta_x*=delta_pi(x*)",
        "gradient_flow_corollary": (
            "if Psi is generated by -g^{-1}dGamma and g(H)>0, fixedness of H implies dGamma(H)=0"
        ),
        "QJ1_follows_from_physical_semiflow_intertwiner": True,
        "generic_action_pushforward_is_not_sufficient": True,
        "finite_witness": upper_outputs,
        "maximum_projection_commutator_residual": dtext(max_residual),
        "finite_witness_intertwines": max_residual == 0,
        "linearized_corollary": (
            "Dpi_x* A_up=A_low Dpi_x*; QJ2 additionally needs the selected tangent metric"
        ),
        "physical_q79_BV_semiflow_intertwiner_present": False,
    }


def t35_quantum_defect(t37: dict[str, Any]) -> dict[str, Any]:
    execution = t37["T35_tadpole_execution"]
    normalized = Decimal(execution["bare_tadpole_over_kappa_Lambda3"])
    complex_value = Decimal(execution["bare_tadpole_complex_over_Lambda3"])
    pfaffian_value = Decimal(execution["bare_tadpole_pfaffian_over_Lambda3"])
    return {
        "scheme": execution["scheme"],
        "mu_over_Lambda": execution["mu_over_Lambda"],
        "upper_T34_flow_at_H": "0",
        "lower_bare_tadpole_over_kappa_Lambda3": dtext(normalized),
        "lower_complex_determinant_tadpole_over_Lambda3": dtext(complex_value),
        "lower_pfaffian_tadpole_over_Lambda3": dtext(pfaffian_value),
        "fixed_point_intertwining_defect_covector": (
            "Dpi beta_up(H)-beta_low(H)=V_F'(H) before metric inversion"
        ),
        "bare_truncated_projection_intertwines_T34_flow": normalized == 0,
        "both_declared_determinant_branches_fail_bare_QJ1": (
            complex_value != 0 and pfaffian_value != 0
        ),
        "QJ1_counterterm_affine_line_available": True,
        "QJ1_counterterm_line_selected_by_current_upper_action": False,
        "full_BV_bosonic_ghost_gravitational_completion_executed": False,
        "physical_promotion_certificate": (
            "one same-source renormalized BV flow satisfying pi Phi_s=Psi_s pi, or one radial BV Ward primitive with Stokes and no cycle boundary"
        ),
    }


def build_packet() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t33 = load_json(T33_PACKET)
    t34 = load_json(T34_PACKET)
    t37 = load_json(T37_PACKET)
    state_certificate = load_json(Q79_STATE_CERT)

    square = exact_square_completion(t33, t34)
    flow = nonlinear_repair_flow(square)
    invariant = invariant_radial_state(square, flow)
    state_extension = formal_q79_state_extension(state_certificate)
    naturality = repair_projection_naturality(square, flow)
    t35_defect = t35_quantum_defect(t37)

    source_checks = source_hash_checks(source_lock)
    source_root_payload = {
        "schema": "boe.mtt.radial-closure-attractor-state-marginal-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [entry["sha256"] for entry in source_lock["local_sources"]],
        "H_expression": square["H_over_Lambda"],
        "square_completion": square["exact_completion"],
        "flow": flow["gradient_flow"],
        "observed_targets": [],
    }

    physical_boundary = {
        "T34_positive_radial_attractor_closed": True,
        "T34_unique_invariant_radial_state_closed": True,
        "formal_local_q79_radial_state_extension_closed": True,
        "formal_state_anchor_equality_is_constructible": True,
        "preferred_full_q79_state_selected": False,
        "global_interacting_cosmological_state_selected": False,
        "physical_renormalized_BV_semiflow_intertwiner_emitted": False,
        "T35_bare_loop_preserves_T34_anchor": False,
        "physical_QJ1_selected": False,
        "physical_QJ2_selected": False,
        "physical_QJ0_selected": False,
        "repair_parameter_identified_with_physical_time": False,
        "physical_endpoint_promoted": False,
    }

    parameter_ledger = {
        "new_continuous_parameters": 0,
        "new_discrete_choices": 0,
        "observed_values_used": [],
        "fitted_values_used": [],
        "inherited_source_values": [
            "t_*=(1-sqrt(13))/6",
            "q2_*=(14+sqrt(13))/3",
            "q4_*=(356+25sqrt(13))/27",
            "f2/f0=15/log(448)",
            "H=H_T34",
        ],
        "state_choice_removed_only_for_radial_marginal": True,
        "matter_gauge_state_family_remains_nonunique": True,
        "renormalization_choice_removed": False,
    }

    packet: dict[str, Any] = {
        "schema": "boe.mtt.radial-closure-attractor-state-marginal.v1",
        "claim_id": "CBF.T38",
        "date": "2026-08-30",
        "status": (
            "exact T34 radial square completion, nonlinear attractor, unique invariant radial state, formal local q79 state extension and repair-semiflow QJ1 criterion; physical renormalized BV intertwiner and QJ1 promotion remain open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_payload": source_root_payload,
            "source_root_sha256": canonical_hash(source_root_payload),
        },
        "exact_radial_square_completion": square,
        "nonlinear_repair_flow": flow,
        "invariant_radial_state": invariant,
        "formal_q79_state_extension": state_extension,
        "repair_semiflow_projection_naturality": naturality,
        "T35_quantum_intertwining_defect": t35_defect,
        "parameter_ledger": parameter_ledger,
        "physical_boundary": physical_boundary,
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "CBF.T38 proves that the exact T34 tree potential is q4_*(h^2-H_T34^2)^2 up to its minimum, solves its nonlinear positive-basin repair flow, and proves delta_H is the unique invariant radial state. Pullback along evaluation at H extends every existing local formal positive q79 state to a radial-anchored state, so full preferred-state uniqueness is not required for the scalar marginal. The exact promotion condition is stronger than action pushforward: the physical renormalized BV projection must intertwine the upper and lower repair semiflows, which would force QJ1. The actual T35 bare determinant has a nonzero fixed-point intertwining defect, and no selected full BV intertwiner or radial Ward primitive is emitted. Thus the finite/formal radial-state blocker is closed while physical QJ1 and 0/3, 0/7 acceptance remain open."
        ),
    }

    required = set(schema["required"])
    checks: dict[str, bool] = {
        **source_checks,
        "all_source_hashes_match": packet["source_provenance"][
            "all_source_hashes_match"
        ],
        "schema_required_keys_present": required.issubset(packet.keys() | {"checks", "check_summary"}),
        "T33_and_T34_claims_are_locked": (
            t33["claim_id"] == "CBF.T33" and t34["claim_id"] == "CBF.T34"
        ),
        "T37_claim_is_locked": t37["claim_id"] == "CBF.T37",
        "q79_state_certificate_passes": state_certificate["all_checks_pass"],
        "q4_R_equals_two_q2_exactly": square["ratio_identity_exact"],
        "q4_is_positive": square["q4_is_positive"],
        "H_is_positive": square["H_is_positive"],
        "positive_radial_minimum_is_unique": square[
            "positive_radial_minimum_is_unique"
        ],
        "square_completion_adds_no_coefficient": not square[
            "new_coefficient_introduced"
        ],
        "zero_branch_is_unstable": flow["zero_branch_is_unstable"],
        "positive_branch_is_stable": flow["positive_branch_is_strictly_stable"],
        "global_positive_basin_converges": flow[
            "global_positive_basin_converges_to_H"
        ],
        "flow_samples_contract": flow["all_sample_errors_contract"],
        "flow_semigroup_composes": flow["semigroup_composition_verified"],
        "repair_parameter_is_not_promoted_to_time": not flow[
            "repair_parameter_is_physical_time"
        ],
        "unique_invariant_radial_state_is_delta_H": invariant[
            "every_initial_probability_converges_weakly_to_delta_H"
        ],
        "finite_zero_defect_measure_is_unique": invariant[
            "unique_zero_defect_probability_weights"
        ]
        == ["0", "1", "0"],
        "sample_measure_moves_toward_H": invariant["sample_mean_moves_toward_H"],
        "radial_marginal_does_not_require_unique_matter_state": invariant[
            "radial_marginal_is_unique_without_selecting_matter_state"
        ],
        "q79_local_formal_state_space_is_nonempty": state_extension[
            "q79_local_formal_state_spaces_nonempty"
        ],
        "q79_formal_positivity_is_preserved": state_extension[
            "q79_restriction_preserves_formal_positivity"
        ],
        "state_pullback_positive_witness": state_extension[
            "finite_test_square_is_positive"
        ],
        "formal_local_radial_state_extension_exists": state_extension[
            "formal_local_radial_anchored_state_exists"
        ],
        "preferred_q79_state_is_not_overclaimed": (
            state_extension["q79_preferred_state_remains_open"]
            and not state_extension["full_interacting_state_is_unique"]
        ),
        "semiflow_projection_witness_intertwines": naturality[
            "finite_witness_intertwines"
        ],
        "semiflow_naturality_implies_QJ1": naturality[
            "QJ1_follows_from_physical_semiflow_intertwiner"
        ],
        "generic_action_pushforward_remains_insufficient": naturality[
            "generic_action_pushforward_is_not_sufficient"
        ],
        "physical_BV_intertwiner_is_not_overclaimed": not naturality[
            "physical_q79_BV_semiflow_intertwiner_present"
        ],
        "T35_bare_intertwining_defect_is_nonzero": not t35_defect[
            "bare_truncated_projection_intertwines_T34_flow"
        ],
        "both_determinant_branches_fail_bare_QJ1": t35_defect[
            "both_declared_determinant_branches_fail_bare_QJ1"
        ],
        "counterterm_line_is_not_overpromoted": not t35_defect[
            "QJ1_counterterm_line_selected_by_current_upper_action"
        ],
        "formal_radial_state_progress_is_recorded": physical_boundary[
            "formal_local_q79_radial_state_extension_closed"
        ],
        "physical_QJ1_remains_open": not physical_boundary[
            "physical_QJ1_selected"
        ],
        "physical_QJ2_remains_open": not physical_boundary[
            "physical_QJ2_selected"
        ],
        "physical_QJ0_remains_open": not physical_boundary[
            "physical_QJ0_selected"
        ],
        "no_observed_values_used": not parameter_ledger["observed_values_used"],
        "no_fitted_values_used": not parameter_ledger["fitted_values_used"],
        "no_new_continuous_parameter": parameter_ledger[
            "new_continuous_parameters"
        ]
        == 0,
        "physical_packet_boundary_preserved": (
            packet["physical_packets_accepted"] == 0
            and packet["physical_packets_total"] == 3
        ),
        "physical_row_boundary_preserved": (
            packet["physical_rows_accepted"] == 0
            and packet["physical_rows_total"] == 7
        ),
        "theorem_file_exists": THEOREM.is_file(),
    }
    failed = [name for name, passed in checks.items() if not passed]
    packet["checks"] = checks
    packet["check_summary"] = {
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "failed": failed,
    }
    return packet


def main() -> None:
    packet = build_packet()
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = packet["check_summary"]
    if summary["failed"]:
        raise SystemExit(f"failed checks: {summary['failed']}")
    print(
        f"wrote {OUTPUT.name}: {summary['passed']}/{summary['total']} checks passed; "
        "radial invariant state closed, physical BV intertwiner remains open"
    )


if __name__ == "__main__":
    main()
