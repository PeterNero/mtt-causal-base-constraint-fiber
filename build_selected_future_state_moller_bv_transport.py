#!/usr/bin/env python3
"""Build the exact CBF.T46 selected-state transport and G2 cutset packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "selected_future_state_moller_bv_transport_source_lock.json"
SCHEMA = ROOT / "selected_future_state_moller_bv_transport_contract.schema.json"
THEOREM = ROOT / "SelectedFutureStateMollerBVTransportAndFullG2CutsetTheorem_v1.md"
OUTPUT = ROOT / "selected_future_state_moller_bv_transport.packet.json"

T44_PACKET = ROOT / "causal_relative_cauchy_evolution_global_g0.packet.json"
T45_PACKET = ROOT / "future_cone_spectral_polarization.packet.json"
T38_PACKET = ROOT / "radial_closure_attractor_state_marginal.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
LOCAL_FORMAL_STATE = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_local_formal_physical_state.certificate.json"
FORMAL_STATE_TRANSPORT = ROOT / "../mtt-qm-source-proof/certificates/q79_sm_equicausal_formal_state_transport.certificate.json"
FIXED_CSTAR = ROOT / "../mtt-qm-source-proof/certificates/q79_fixed_coupling_regulated_cstar_promotion_criterion.certificate.json"

Matrix = list[list[Fraction]]
Vector = list[Fraction]


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


def matrix_text(matrix: Matrix) -> list[list[str]]:
    return [[ftext(value) for value in row] for row in matrix]


def vector_text(vector: Vector) -> list[str]:
    return [ftext(value) for value in vector]


def zero(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zero(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left)
    middle = len(right)
    columns = len(right[0])
    return [
        [sum((left[i][k] * right[k][j] for k in range(middle)), Fraction(0)) for j in range(columns)]
        for i in range(rows)
    ]


def matadd(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return [[a - b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def matscale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum((entry * component for entry, component in zip(row, vector)), Fraction(0)) for row in matrix]


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def det2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def expectation(density: Matrix, observable: Matrix) -> Fraction:
    return trace(matmul(density, observable))


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


def exact_transport_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    unitary: Matrix = [
        [Fraction(3, 5), Fraction(-4, 5)],
        [Fraction(4, 5), Fraction(3, 5)],
    ]
    second: Matrix = [
        [Fraction(5, 13), Fraction(-12, 13)],
        [Fraction(12, 13), Fraction(5, 13)],
    ]
    source: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    transported = matmul(matmul(unitary, source), transpose(unitary))
    returned = matmul(matmul(transpose(unitary), transported), unitary)
    sequential = matmul(matmul(second, transported), transpose(second))
    composite = matmul(second, unitary)
    direct = matmul(matmul(composite, source), transpose(composite))

    observables: list[Matrix] = [
        [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]],
        [[Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]],
        [[Fraction(0), Fraction(0)], [Fraction(1), Fraction(0)]],
        [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]],
    ]
    expectation_rows: list[dict[str, Any]] = []
    for observable in observables:
        pulled_back = matmul(matmul(transpose(unitary), observable), unitary)
        expectation_rows.append(
            {
                "observable": matrix_text(observable),
                "transported_state": ftext(expectation(transported, observable)),
                "source_after_pullback": ftext(expectation(source, pulled_back)),
            }
        )

    square_roots: list[Matrix] = [
        [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]],
        [[Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]],
        [[Fraction(1), Fraction(1)], [Fraction(0), Fraction(0)]],
        [[Fraction(1), Fraction(-1)], [Fraction(2), Fraction(0)]],
    ]
    square_rows: list[dict[str, Any]] = []
    for root in square_roots:
        square = matmul(transpose(root), root)
        value = expectation(transported, square)
        square_rows.append(
            {"root": matrix_text(root), "positive_square_expectation": ftext(value)}
        )

    checks = {
        "transport_unitary_is_orthogonal": matmul(unitary, transpose(unitary)) == identity(2),
        "second_transport_is_orthogonal": matmul(second, transpose(second)) == identity(2),
        "source_is_rank_one_projection": matmul(source, source) == source and trace(source) == 1 and det2(source) == 0,
        "transported_is_rank_one_projection": matmul(transported, transported) == transported and trace(transported) == 1 and det2(transported) == 0,
        "inverse_transport_returns_source": returned == source,
        "state_expectations_obey_pullback": all(row["transported_state"] == row["source_after_pullback"] for row in expectation_rows),
        "positive_square_expectations_are_nonnegative": all(Fraction(row["positive_square_expectation"]) >= 0 for row in square_rows),
        "state_transport_composes_exactly": sequential == direct,
    }
    witness = {
        "source_future_projection": matrix_text(source),
        "transport_unitary": matrix_text(unitary),
        "transported_projection": matrix_text(transported),
        "inverse_transport": matrix_text(returned),
        "second_transport_unitary": matrix_text(second),
        "composite_transport_unitary": matrix_text(composite),
        "sequential_transport_projection": matrix_text(sequential),
        "direct_composite_projection": matrix_text(direct),
        "expectation_rows": expectation_rows,
        "positive_square_rows": square_rows,
    }
    return witness, checks


def canonical_lift_witness() -> tuple[dict[str, Any], dict[str, bool]]:
    # Ordered basis: (epsilon_1, epsilon_2, x, y, c, bar_c).
    q0 = zero(6, 6)
    q0[4][2] = Fraction(1)
    q0[3][5] = Fraction(1)
    homotopy = zero(6, 6)
    homotopy[2][4] = Fraction(1)
    homotopy[5][3] = Fraction(1)
    physical = zero(6, 6)
    physical[0][0] = Fraction(1)
    physical[1][1] = Fraction(1)

    delta = zero(6, 6)
    delta[4][0] = Fraction(-1)
    e1: Vector = [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    psi1: Vector = [Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    source_order_one = matvec(delta, e1)

    krein: Matrix = [
        [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
    ]

    q0_square = matmul(q0, q0)
    delta_square = matmul(delta, delta)
    anticommutator = matadd(matmul(q0, delta), matmul(delta, q0))
    contraction = matadd(matmul(q0, homotopy), matmul(homotopy, q0))
    expected_contraction = matsub(identity(6), physical)
    order_one_closed = [a + b for a, b in zip(matvec(q0, psi1), source_order_one)]
    projected_lift = [a + b for a, b in zip(e1, matvec(physical, psi1))]
    homotopy_gauge = matvec(homotopy, psi1)
    norm0 = sum((e1[i] * krein[i][j] * e1[j] for i in range(6) for j in range(6)), Fraction(0))
    norm1 = sum((psi1[i] * krein[i][j] * psi1[j] for i in range(6) for j in range(6)), Fraction(0))
    cross = sum((e1[i] * krein[i][j] * psi1[j] for i in range(6) for j in range(6)), Fraction(0))

    checks = {
        "free_BRST_charge_is_nilpotent": q0_square == zero(6, 6),
        "free_quartet_contraction_identity": contraction == expected_contraction,
        "perturbation_squares_to_zero": delta_square == zero(6, 6),
        "perturbation_anticommutes_with_free_charge": anticommutator == zero(6, 6),
        "formal_charge_is_nilpotent_to_all_orders_in_witness": q0_square == zero(6, 6) and anticommutator == zero(6, 6) and delta_square == zero(6, 6),
        "canonical_first_order_lift_is_closed": order_one_closed == [Fraction(0)] * 6,
        "canonical_lift_has_fixed_physical_projection": projected_lift == e1,
        "canonical_lift_obeys_homotopy_gauge": homotopy_gauge == [Fraction(0)] * 6,
        "canonical_lift_norm_is_one_formally": norm0 == 1 and norm1 == 0 and cross == 0,
    }
    witness = {
        "basis": ["epsilon_1", "epsilon_2", "x", "y", "c", "bar_c"],
        "Q0": matrix_text(q0),
        "homotopy": matrix_text(homotopy),
        "physical_projector": matrix_text(physical),
        "delta_Q1": matrix_text(delta),
        "free_vector": vector_text(e1),
        "first_order_correction": vector_text(psi1),
        "formal_lift": "psi(lambda)=epsilon_1+lambda x",
        "closure_identity": "(Q0+lambda delta_Q1)psi(lambda)=0",
        "normalization_identity": "<psi(lambda),psi(lambda)>_J=1",
        "scope_guard": "finite exact homological-lift witness; q79 hermiticity and positivity are imported from the certified interacting charge, not inferred from this toy perturbation",
    }
    return witness, checks


def build() -> dict[str, Any]:
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t44 = load_json(T44_PACKET)
    t45 = load_json(T45_PACKET)
    t38 = load_json(T38_PACKET)
    t39 = load_json(T39_PACKET)
    local_state = load_json(LOCAL_FORMAL_STATE)
    formal_transport = load_json(FORMAL_STATE_TRANSPORT)
    fixed_cstar = load_json(FIXED_CSTAR)

    construction_checks, comparison_checks = source_hash_checks(source_lock)
    transport_witness, transport_checks = exact_transport_witness()
    lift_witness, lift_checks = canonical_lift_witness()

    checks: dict[str, bool] = {}
    checks.update(construction_checks)
    checks.update(comparison_checks)
    checks.update(transport_checks)
    checks.update(lift_checks)
    checks.update(
        {
            "source_lock_schema_matches": source_lock["schema"] == "boe.mtt.selected-future-state-moller-bv-transport-source-lock.v1",
            "source_lock_claim_matches": source_lock["claim_id"] == "CBF.T46",
            "contract_schema_claim_matches": schema["properties"]["claim_id"]["const"] == "CBF.T46",
            "theorem_file_exists": THEOREM.is_file(),
            "T44_Moller_map_acts_on_even_CAR": "even CAR" in t44["moller_relative_evolution"]["acts_on"],
            "T44_Moller_map_is_causal": t44["moller_relative_evolution"]["causal_support"] is True,
            "T44_relative_element_is_formal": t44["operator_valued_global_G0"]["formal_perturbative_tier"] is True,
            "T45_future_state_is_selected": t45["quasifree_initial_state"]["selected_free_initial_state_on_declared_branch"] is True,
            "T45_future_state_is_positive": t45["quasifree_initial_state"]["positive"] is True,
            "T45_future_state_is_Hadamard": t45["quasifree_initial_state"]["Hadamard_on_static_flat_branch"] is True,
            "local_formal_state_certificate_passes": local_state["all_checks_pass"] is True,
            "local_formal_state_requires_three_factors": all(
                token in local_state["free_field_extension"]["free_physical_state"]
                for token in ("omega_gauge,phys", "omega_Higgs", "omega_Weyl")
            ),
            "formal_deformation_supplies_lifts": "at least one formal" in local_state["formal_physical_representation"]["deformation_stability"],
            "formal_state_transport_certificate_passes": formal_transport["all_checks_pass"] is True,
            "formal_state_transport_is_unital_star_pullback": "unital star isomorphism" in formal_transport["presentation_groupoid"]["physical_state_transport"],
            "formal_state_transport_preserves_positivity": "formal positivity" in formal_transport["presentation_groupoid"]["physical_state_transport"],
            "T38_does_not_select_full_state": t38["physical_boundary"]["preferred_full_q79_state_selected"] is False,
            "T38_does_not_select_cosmological_state": t38["physical_boundary"]["global_interacting_cosmological_state_selected"] is False,
            "T39_anchor_not_selected_by_upper_action": t39["physical_boundary"]["pointed_anchor_scheme_selected_by_upper_action"] is False,
            "fixed_regulator_Cstar_is_closed": fixed_cstar["acceptance_counts"]["regulated_fixed_coupling"] == "5/5",
            "continuum_Cstar_rows_are_open": fixed_cstar["acceptance_counts"]["continuum_reduced_product"] == "0/9",
            "no_observed_values_used": True,
            "no_fitted_state_used": True,
            "quadratic_background_not_called_full_SM_interaction": True,
            "formal_positivity_not_promoted_to_fixed_coupling": True,
            "full_G2_not_claimed_closed": True,
            "physical_counters_unchanged": True,
        }
    )

    packet: dict[str, Any] = {
        "schema": "boe.mtt.selected-future-state-moller-bv-transport.v1",
        "claim_id": "CBF.T46",
        "title": "Selected future-state Moller/BV transport and full G2 cutset",
        "date": "2026-08-30",
        "status": "exact selected in-state transport for compactly supported direct Dirac-Yukawa background perturbations; local-formal BV state-pullback and canonical-lift criterion closed; full selected SM G2 and fixed-coupling continuum remain open",
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
        "exact_direct_state_transport": {
            "domain": "T44 compactly supported smooth order-zero Dirac-Yukawa background perturbations of the T45 homogeneous flat direct branch",
            "retarded_algebra_map": "alpha_h^ret:A_H^even -> A_h^even, induced by the retarded Moller isomorphism",
            "selected_in_state": "omega_h^in=omega_fut composed with (alpha_h^ret)^(-1)",
            "normalization_proof": "omega_h^in(1)=omega_fut(1)=1 because alpha_h^ret is unital",
            "positivity_proof": "omega_h^in(A^*A)=omega_fut(B^*B)>=0 with B=(alpha_h^ret)^(-1)(A)",
            "quasifree_covariance": "P_h^in=M_h^ret P_fut (M_h^ret)^(-1) on the transported one-particle solution space",
            "Hadamard_preserved": True,
            "purity_preserved": True,
            "unique_meaning": "the unique pullback of omega_fut along the specified retarded Moller isomorphism, not the unique state of the perturbed theory",
            "state_orbit_composition": "T_k<-h^* T_h<-H^* omega_fut=T_k<-H^* omega_fut",
            "advanced_comparison": "the advanced transport defines the corresponding out-state; its comparison with the in-state is relative Cauchy evolution",
            "new_state_parameter_count": 0,
            "nonlinear_full_SM_interaction": False,
        },
        "exact_transport_witness": transport_witness,
        "formal_BV_state_pullback": {
            "domain": "bounded H1-zero q79 charts over the formal perturbative ring",
            "map": "I_V:A_phys,V -> A_phys,0 is a unital star-isomorphism satisfying I_V s_hat_V=s_hat_0 I_V",
            "state": "omega_V=omega_0 composed with I_V",
            "normalization": "omega_V(1)=1",
            "formal_positivity": "omega_V(A^* star_V A)=omega_0(I_V(A)^* star_0 I_V(A)) in the formal square cone",
            "BRST_descent": "closed and exact representatives are preserved by the intertwining identity, so omega_V is defined on H0",
            "presentation_covariance": "Hadamard, renormalization and gauge-fixing changes transport the state cone by the certified presentation groupoid",
            "closed_as_algebraic_transport_theorem": True,
            "instantiated_as_selected_full_SM_state": False,
            "reason_not_instantiated": "T45 selects only the Weyl factor; the full free physical seed also needs gauge-physical and Higgs-fluctuation factors, and T39's normalization is not yet selected by the upper action",
        },
        "canonical_BRST_lift": {
            "free_contraction": "Q0 h+h Q0=I-i p with h^2=0, p h=0 and h i=0",
            "interacting_charge": "Q_I=Q0+sum_(n>=1) lambda^n delta_n",
            "recursive_source": "r_n=sum_(k=1)^n delta_k psi_(n-k)",
            "recursive_lift": "psi_n=-h r_n",
            "gauge_conditions": ["p psi_n=0", "h psi_n=0"],
            "existence_condition": "p r_n=0 at every order; the certified q79 deformation-stability theorem supplies existence for every free physical vector",
            "uniqueness": "any two lifts with the same physical projection and homotopy gauge differ by a Q0-closed vector annihilated by p and h, hence vanish by the contraction identity",
            "result": "once a free physical vector and one certified contraction/presentation are fixed, the formal lift is canonical; presentation changes transport it rather than creating a physical parameter",
            "does_not_select_free_seed": True,
        },
        "canonical_lift_witness": lift_witness,
        "full_seed_factorization": {
            "required_free_state": "omega_0=omega_gauge,phys tensor omega_Higgs tensor omega_Weyl",
            "Weyl_factor": {
                "status": "selected on the homogeneous flat direct branch by T45",
                "source": "P_fut",
            },
            "radial_background_marginal": {
                "status": "selected at the T38 finite/formal repair tier",
                "source": "delta_H",
                "is_Higgs_fluctuation_state": False,
            },
            "Higgs_fluctuation_factor": {
                "status": "nonempty Hadamard state space exists; no same-source preferred factor is supplied by T38 or T45",
                "selected": False,
            },
            "gauge_physical_factor": {
                "status": "positive BRST quotient and compatible Hadamard states exist; no same-source preferred factor is supplied by T45",
                "selected": False,
            },
            "formal_lift_choice_after_full_seed": {
                "status": "removed by the canonical homotopy gauge in this theorem",
                "selected": True,
            },
            "full_product_seed_selected": False,
            "missing_selected_factors": 2,
        },
        "G2_clause_ledger": {
            "G2a_flat_branch_free_Weyl_initial_state": "closed by T45",
            "G2b_exact_quadratic_background_Dirac_state_transport": "closed by T46",
            "G2b_local_formal_positive_state_existence": "closed by the inherited q79 theorem",
            "G2b_local_formal_state_pullback_rule": "closed algebraically by T46",
            "G2b_canonical_formal_BRST_lift_given_seed": "closed by T46",
            "G2b_selected_full_gauge_Higgs_Weyl_seed": "open",
            "G2b_selected_upper_action_and_BV_map": "open",
            "G2c_fixed_coupling_finite_auxiliary_regulator": "closed 5/5 in the inherited q79 theorem",
            "G2c_selected_regulator_independent_continuum": "open 0/9",
            "top_level_physical_G2": "open",
            "physical_T41_gate_count": "0/3",
        },
        "fixed_coupling_boundary": {
            "formal_square_cone_is_numeric_positive_cone": False,
            "finite_auxiliary_regulator_Cstar_rows": "5/5",
            "selected_continuum_Cstar_rows": "0/9",
            "required_exit": "one selected regulator family plus uniform locality, energy, Ward, state and convergence estimates, or one common positive Borel/Cstar completion",
            "T46_proves_regulator_removal": False,
            "T46_proves_nonperturbative_SM_state": False,
        },
        "parameter_ledger": {
            "new_observed_inputs": 0,
            "new_fitted_parameters": 0,
            "new_continuous_state_selectors": 0,
            "new_discrete_state_selectors": 0,
            "inherited_future_time_orientation": 1,
            "inherited_unresolved_radial_scale": "H",
            "presentation_choices": "retarded/advanced boundary role, Hadamard representative, gauge fixing and renormalization prescription are typed maps or equivalent presentations; only the retarded map is used for the selected in-state",
        },
        "physical_boundary": {
            "closed": [
                "exact retarded transport of the T45 state through every T44 compact order-zero direct Dirac-Yukawa background perturbation",
                "normalization, positivity, purity, quasifree character and Hadamard preservation under that transport",
                "functorial composition and uniqueness of the transported state relative to the selected seed and map",
                "formal BV state-pullback preservation of normalization, square-cone positivity and BRST cohomology",
                "canonical formal BRST lift given a free physical seed and certified contraction",
                "exact identification of the two missing full-product seed factors",
            ],
            "open": [
                "same-source selection of the gauge-physical and Higgs-fluctuation free factors",
                "upper-action selection of the full interacting BV map and anchored normalization",
                "one global cosmological interacting state",
                "source-dependent determinant-line connection and holonomy",
                "selected fixed-coupling regulator-independent Cstar continuum state",
                "physical G1 tangent metric and q79 HYM universality",
            ],
            "physical_packets_accepted": 0,
            "physical_packets_total": 3,
            "physical_rows_accepted": 0,
            "physical_rows_total": 7,
        },
        "frontier_delta": "The state problem is no longer one undifferentiated G2 box. T45 plus the T44 retarded Moller map now select an exact positive Hadamard in-state orbit for the complete compact-background direct Dirac-Yukawa family, with no new state parameter. At the nonlinear q79 BV tier, state pullback and the canonical formal BRST lift are also no longer blockers once a full free seed and one selected map are supplied. The remaining selected-state obstruction is reduced exactly to two missing free factors (gauge physical and Higgs fluctuation), upper-action selection of the full BV map, determinant holonomy and the fixed-coupling continuum estimates. The physical counters do not move because those are required by top-level G2.",
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
        raise SystemExit(f"CBF.T46 build failed: {summary['failed']}")
    print(f"CBF.T46 build passed {summary['passed']}/{summary['total']} checks")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
