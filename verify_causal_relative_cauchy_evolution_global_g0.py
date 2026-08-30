#!/usr/bin/env python3
"""Independently verify the CBF.T44 causal relative-evolution packet."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "causal_relative_cauchy_evolution_global_g0.packet.json"
SOURCE_LOCK = ROOT / "causal_relative_cauchy_evolution_global_g0_source_lock.json"
SCHEMA = ROOT / "causal_relative_cauchy_evolution_global_g0_contract.schema.json"
THEOREM = ROOT / "CausalRelativeCauchyEvolutionAndStateSeparatedGlobalG0Theorem_v1.md"
T25_PACKET = ROOT / "direct_finite_source_continuum.packet.json"
T39_PACKET = ROOT / "renormalized_bv_anchored_repair_semiflow.packet.json"
T41_PACKET = ROOT / "cotangent_lifted_local_formal_projection.packet.json"
T43_PACKET = ROOT / "weyl_polarized_product_dirac_g0.packet.json"
FREE_CAR = ROOT / "../mtt-qm-source-proof/certificates/framed_q79_free_dirac_car_net.certificate.json"
BINARY_ROOT = ROOT / "../mtt-q79-total-superconnection-branching/artifacts/binary_root_car_net_equivalence.packet.json"
SHARED_RETURN = ROOT / "../mtt-protospinor-gr-response-proof/certificates/q79_shared_circle_double_return_cln_nil_flat_endpoint_certificate.json"

QC = tuple[Fraction, Fraction]
QMatrix = list[list[Fraction]]
CMatrix = list[list[QC]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fparse(value: str) -> Fraction:
    return Fraction(value)


def qcparse(value: dict[str, str]) -> QC:
    return Fraction(value["real"]), Fraction(value["imag"])


def cadd(left: QC, right: QC) -> QC:
    return left[0] + right[0], left[1] + right[1]


def cmul(left: QC, right: QC) -> QC:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def cconj(value: QC) -> QC:
    return value[0], -value[1]


def qidentity(size: int) -> QMatrix:
    return [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]


def qadd(left: QMatrix, right: QMatrix) -> QMatrix:
    return [[a + b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def qsub(left: QMatrix, right: QMatrix) -> QMatrix:
    return [[a - b for a, b in zip(lrow, rrow)] for lrow, rrow in zip(left, right)]


def qmul(left: QMatrix, right: QMatrix) -> QMatrix:
    return [
        [
            sum((left[row][k] * right[k][column] for k in range(len(right))), Fraction(0))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def qinv2(matrix: QMatrix) -> QMatrix:
    a, b = matrix[0]
    c, d = matrix[1]
    determinant = a * d - b * c
    return [[d / determinant, -b / determinant], [-c / determinant, a / determinant]]


def qmatrix_from_packet(matrix: list[list[str]]) -> QMatrix:
    return [[fparse(value) for value in row] for row in matrix]


def cidentity(size: int) -> CMatrix:
    return [[(Fraction(int(row == column)), Fraction(0)) for column in range(size)] for row in range(size)]


def cmul_matrix(left: CMatrix, right: CMatrix) -> CMatrix:
    result: CMatrix = []
    for row in range(len(left)):
        result_row: list[QC] = []
        for column in range(len(right[0])):
            value: QC = Fraction(0), Fraction(0)
            for k in range(len(right)):
                value = cadd(value, cmul(left[row][k], right[k][column]))
            result_row.append(value)
        result.append(result_row)
    return result


def cadjoint(matrix: CMatrix) -> CMatrix:
    return [
        [cconj(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def cscalar(matrix: CMatrix, scalar: QC) -> CMatrix:
    return [[cmul(scalar, value) for value in row] for row in matrix]


def ctrace(matrix: CMatrix) -> QC:
    result: QC = Fraction(0), Fraction(0)
    for index in range(len(matrix)):
        result = cadd(result, matrix[index][index])
    return result


def cpacket_matrix(matrix: list[list[dict[str, str]]]) -> CMatrix:
    return [[qcparse(value) for value in row] for row in matrix]


def expectation(density: CMatrix, observable: CMatrix) -> QC:
    return ctrace(cmul_matrix(density, observable))


def verify() -> dict[str, bool]:
    packet = load_json(PACKET)
    source_lock = load_json(SOURCE_LOCK)
    schema = load_json(SCHEMA)
    t25 = load_json(T25_PACKET)
    t39 = load_json(T39_PACKET)
    t41 = load_json(T41_PACKET)
    t43 = load_json(T43_PACKET)
    free_car = load_json(FREE_CAR)
    binary_root = load_json(BINARY_ROOT)
    shared_return = load_json(SHARED_RETURN)
    theorem_text = THEOREM.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    all_sources = source_lock["construction_sources"] + source_lock["comparison_sources"]
    for index, source in enumerate(all_sources, start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash"] = path.is_file() and sha256(path) == source["sha256"]

    checks.update(
        {
            "packet_schema": packet["schema"] == "boe.mtt.causal-relative-cauchy-evolution-global-g0.v1",
            "claim_id": packet["claim_id"] == "CBF.T44",
            "contract_claim": schema["properties"]["claim_id"]["const"] == "CBF.T44",
            "source_lock_hash": packet["source_provenance"]["source_lock_sha256"] == sha256(SOURCE_LOCK),
            "schema_hash": packet["source_provenance"]["contract_schema_sha256"] == sha256(SCHEMA),
            "theorem_hash": packet["source_provenance"]["theorem_sha256"] == sha256(THEOREM),
            "construction_hashes_all": packet["source_provenance"]["all_construction_hashes_match"],
            "comparison_hashes_all": packet["source_provenance"]["all_comparison_hashes_match"],
            "comparison_excluded": packet["source_provenance"]["comparison_sources_excluded_from_root"],
            "builder_checks_all": all(packet["checks"].values()),
            "builder_summary": packet["check_summary"]["passed"] == packet["check_summary"]["total"] and packet["check_summary"]["failed"] == [],
            "required_keys": set(schema["required"]).issubset(packet),
            "T25_passes": t25["claim_id"] == "CBF.T25" and all(t25["checks"].values()),
            "T39_passes": t39["claim_id"] == "CBF.T39" and all(t39["checks"].values()),
            "T41_passes": t41["claim_id"] == "CBF.T41" and all(t41["checks"].values()),
            "T43_passes": t43["claim_id"] == "CBF.T43" and all(t43["checks"].values()),
            "free_CAR_passes": free_car["all_checks_pass"],
            "binary_root_passes": binary_root["all_checks_pass"],
            "shared_return_passes": all(shared_return["checks"].values()),
        }
    )

    # Recompute the Moller algebra from independent literals.
    d0: QMatrix = [[Fraction(2), Fraction(1)], [Fraction(0), Fraction(3)]]
    perturbation: QMatrix = [[Fraction(1), Fraction(0)], [Fraction(1), Fraction(1)]]
    d1 = qadd(d0, perturbation)
    e0 = qinv2(d0)
    e1 = qinv2(d1)
    iq = qidentity(2)
    moller = qsub(iq, qmul(e1, perturbation))
    inverse = qadd(iq, qmul(e0, perturbation))
    witness = packet["moller_relative_evolution"]["finite_resolvent_witness"]
    checks.update(
        {
            "D_H_recomputed": qmatrix_from_packet(witness["D_H"]) == d0,
            "V_recomputed": qmatrix_from_packet(witness["V"]) == perturbation,
            "D_h_recomputed": qmatrix_from_packet(witness["D_h"]) == d1,
            "E_H_recomputed": qmatrix_from_packet(witness["E_H"]) == e0,
            "E_h_recomputed": qmatrix_from_packet(witness["E_h"]) == e1,
            "resolvent_left": qsub(e0, qmul(qmul(e1, perturbation), e0)) == e1,
            "resolvent_right": qsub(e0, qmul(qmul(e0, perturbation), e1)) == e1,
            "Moller_left": qmul(moller, inverse) == iq,
            "Moller_right": qmul(inverse, moller) == iq,
            "Moller_packet": qmatrix_from_packet(witness["M_h"]) == moller,
            "Moller_inverse_packet": qmatrix_from_packet(witness["M_h_inverse"]) == inverse,
            "state_free_rce": packet["moller_relative_evolution"]["state_free"],
            "causal_support": packet["moller_relative_evolution"]["causal_support"],
        }
    )

    # Recompute the unique primitive contour.
    boundary = qmatrix_from_packet(packet["minimal_return_chain"]["boundary_matrix"])
    cycle = [fparse(value) for value in packet["minimal_return_chain"]["unique_normalized_cycle"]]
    boundary_value = [
        sum((boundary[row][column] * cycle[column] for column in range(2)), Fraction(0))
        for row in range(2)
    ]
    checks.update(
        {
            "boundary_exact": boundary == [[-1, -1], [1, 1]],
            "cycle_exact": cycle == [1, -1],
            "cycle_closed": boundary_value == [0, 0],
            "cycle_primitive": math.gcd(abs(cycle[0].numerator), abs(cycle[1].numerator)) == 1,
            "cycle_unique_after_forward_normalization": cycle[0] == 1 and cycle[1] == -cycle[0],
            "no_contour_parameter": not packet["minimal_return_chain"]["extra_contour_parameter"],
            "return_is_conditional": packet["minimal_return_chain"]["conditional_on_return_requirement"],
            "orientation_not_derived": not packet["minimal_return_chain"]["physical_time_orientation_derived_here"],
        }
    )

    # Recompute the exact CTP and state-separation witness.
    one: QC = Fraction(1), Fraction(0)
    zero: QC = Fraction(0), Fraction(0)
    u: QC = Fraction(3, 5), Fraction(4, 5)
    w: QC = Fraction(5, 13), Fraction(12, 13)
    p: QC = Fraction(8, 17), Fraction(15, 17)
    ic = cidentity(2)
    operator = [[u, zero], [zero, cconj(u)]]
    sminus = cscalar(ic, w)
    splus = cscalar(operator, w)
    contour_operator = cmul_matrix(cadjoint(sminus), splus)
    equal_operator = cmul_matrix(cadjoint(splus), splus)
    common_operator = cmul_matrix(cadjoint(cscalar(sminus, p)), cscalar(splus, p))
    relative_operator = cmul_matrix(cadjoint(sminus), cscalar(splus, p))
    rho0 = [[one, zero], [zero, zero]]
    rho1 = [[zero, zero], [zero, one]]
    rhom = [[(Fraction(1, 2), Fraction(0)), zero], [zero, (Fraction(1, 2), Fraction(0))]]
    values = [expectation(rho, contour_operator) for rho in [rho0, rho1, rhom]]
    equal_values = [expectation(rho, equal_operator) for rho in [rho0, rho1, rhom]]
    packet_values = packet["state_scalarization_cutset"]["state_values"]
    checks.update(
        {
            "operator_unitary": cmul_matrix(cadjoint(operator), operator) == ic,
            "packet_operator": cpacket_matrix(packet["operator_valued_global_G0"]["finite_unequal_source_operator"]) == operator,
            "equal_return": equal_operator == ic,
            "packet_equal_operator": cpacket_matrix(packet["operator_valued_global_G0"]["finite_equal_source_operator"]) == ic,
            "common_phase_cancel": common_operator == contour_operator,
            "relative_phase_survives": relative_operator == cscalar(contour_operator, p) and relative_operator != contour_operator,
            "phase_ledger_common": packet["phase_ledger"]["common_central_phase_cancels"],
            "phase_ledger_relative": packet["phase_ledger"]["relative_source_phase_is_retained"],
            "state_values_exact": values == [u, cconj(u), (Fraction(3, 5), Fraction(0))],
            "state_values_packet": [qcparse(packet_values[key]) for key in ["omega_0", "omega_1", "omega_mix"]] == values,
            "state_values_distinct": len(set(values)) == 3,
            "equal_values_one": all(value == one for value in equal_values),
            "state_not_selected": not packet["state_scalarization_cutset"]["preferred_state_selected"],
            "scalar_G0_requires_G2": packet["state_scalarization_cutset"]["global_scalar_G0_requires_G2_data"],
        }
    )

    # Recompute ordered relative evolution with a noncommuting second unitary.
    rotation: CMatrix = [
        [(Fraction(3, 5), Fraction(0)), (Fraction(-4, 5), Fraction(0))],
        [(Fraction(4, 5), Fraction(0)), (Fraction(3, 5), Fraction(0))],
    ]

    def relative(to_operator: CMatrix, from_operator: CMatrix) -> CMatrix:
        return cmul_matrix(cadjoint(from_operator), to_operator)

    checks["relative_composition"] = cmul_matrix(
        relative(operator, ic), relative(rotation, operator)
    ) == relative(rotation, ic)
    checks["rotation_noncommutes_with_first"] = cmul_matrix(operator, rotation) != cmul_matrix(rotation, operator)

    gate = packet["gate_ledger"]
    checks.update(
        {
            "local_G0_inherited": gate["G0_direct_local_one_loop"]["closed"],
            "global_operator_G0_closed": gate["G0_direct_global_operator_relative"]["closed"],
            "global_scalar_G0_open": not gate["G0_global_scalar_physical"]["closed"],
            "global_scalar_interlocked_G2": gate["G0_global_scalar_physical"]["interlocked_with"] == "G2",
            "G1_open": not gate["G1_physical_tangent_pairing"]["closed"],
            "G2_open": not gate["G2_selected_interacting_state_BV"]["closed"],
            "HYM_open": not gate["G0_q79_HYM"]["closed"],
            "physical_gates_0_3": gate["physical_gluing_gates_closed"] == 0 and gate["physical_gluing_gates_total"] == 3,
            "physical_packets_0_3": gate["physical_packets_accepted"] == 0 and gate["physical_packets_total"] == 3,
            "physical_rows_0_7": gate["physical_rows_accepted"] == 0 and gate["physical_rows_total"] == 7,
            "T43_root_match": packet["T43_local_shadow"]["direct_source_root_matches"],
            "T43_kappa": packet["T43_local_shadow"]["selected_kappa_F"] == "1/(2 pi^2)",
            "T43_not_globalized": not packet["T43_local_shadow"]["full_global_scalar_equality_claimed"],
            "internal_circle_not_time": not packet["shared_circle_and_root_boundary"]["internal_shared_circle_identified_with_physical_time"],
            "internal_return_not_CTP_selection": not packet["shared_circle_and_root_boundary"]["internal_double_return_selects_CTP_contour"],
            "no_observed_inputs": packet["parameter_ledger"]["new_observed_inputs"] == 0,
            "no_fits": packet["parameter_ledger"]["new_fitted_coefficients"] == 0,
            "no_continuous_parameters": packet["parameter_ledger"]["new_continuous_physical_parameters"] == 0,
            "no_state_selector": packet["parameter_ledger"]["new_preferred_state_selectors"] == 0,
            "B_ACTION_open": not packet["physical_boundary"]["B_ACTION_01_closed"],
            "B_QFT_open": not packet["physical_boundary"]["B_QFT_02_closed"],
            "theorem_claim": "**Claim:** CBF.T44" in theorem_text,
            "theorem_Moller": "Theorem 3.1: exact Moller inverse" in theorem_text,
            "theorem_return": "Theorem 5.1: return-chain uniqueness" in theorem_text,
            "theorem_state": "Theorem 7.1: state-separation cutset" in theorem_text,
            "theorem_circle_guard": "S1_shared = physical time" in theorem_text,
        }
    )

    failed = sorted(name for name, passed in checks.items() if not passed)
    print(f"independent checks: {len(checks) - len(failed)}/{len(checks)}")
    if failed:
        raise SystemExit("failed checks: " + ", ".join(failed))
    return checks


if __name__ == "__main__":
    verify()
