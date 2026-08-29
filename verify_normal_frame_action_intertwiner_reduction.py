#!/usr/bin/env python3
"""Independent verifier for the CBF.T18 normal-frame quotient packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import verify_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "normal_frame_action_intertwiner_reduction.packet.json"
SOURCE_LOCK = ROOT / "normal_frame_action_intertwiner_source_lock.json"
SCHEMA = ROOT / "normal_frame_action_intertwiner_contract.schema.json"
THEOREM = ROOT / "NormalFrameQuotientAndActionIntertwinerMinimalDataTheorem_v1.md"
FSB_MANIFEST = ROOT.parent / "mtt-q79-total-superconnection-branching" / "state" / "source_manifest.v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qscalar(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def sum_k(values: Any) -> cp.K:
    result = cp.Z
    for value in values:
        result = cp.add(result, value)
    return result


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    return sum_k(matrix[index][index] for index in range(len(matrix)))


def frobenius_inner(left: cp.Matrix, right: cp.Matrix) -> cp.K:
    return sum_k(
        cp.mul(cp.conj(left[row][column]), right[row][column])
        for row in range(len(left))
        for column in range(len(left[0]))
    )


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.matrix_add(left, cp.matrix_scale(qscalar(-1), right))


def hardcoded_responses() -> tuple[cp.Matrix, cp.Matrix]:
    minus_one_minus_i_sqrt3: cp.K = (
        Fraction(-1), Fraction(0), Fraction(0), Fraction(-1)
    )
    minus_one_plus_i_sqrt3: cp.K = (
        Fraction(-1), Fraction(0), Fraction(0), Fraction(1)
    )
    a = [
        [qscalar(-2), cp.Z, qscalar(-2)],
        [cp.Z, qscalar(-2), qscalar(-2)],
        [qscalar(-2), qscalar(-2), cp.Z],
    ]
    b = [
        [qscalar(-4), cp.Z, cp.Z],
        [cp.Z, cp.Z, minus_one_minus_i_sqrt3],
        [cp.Z, minus_one_plus_i_sqrt3, cp.Z],
    ]
    return a, b


def routed_hessian() -> tuple[cp.Matrix, cp.Matrix, cp.Matrix]:
    a, b = hardcoded_responses()
    phase = {6, 7, 8, 14}
    shift = {9, 10, 11, 15}
    r_phase = cp.diagonal([cp.O if index in phase else cp.Z for index in range(16)])
    r_shift = cp.diagonal([cp.O if index in shift else cp.Z for index in range(16)])
    return a, b, cp.matrix_add(cp.kron(b, r_phase), cp.kron(a, r_shift))


def weyl_pair() -> tuple[cp.Matrix, cp.Matrix]:
    omega: cp.K = (Fraction(-1, 2), Fraction(0), Fraction(0), Fraction(1, 2))
    omega2 = cp.mul(omega, omega)
    shift = [
        [cp.Z, cp.O, cp.Z],
        [cp.Z, cp.Z, cp.O],
        [cp.O, cp.Z, cp.Z],
    ]
    return shift, cp.diagonal([cp.O, omega, omega2])


def complex_action(
    epsilon: cp.K,
    curvature: cp.K,
    normal: cp.K,
    multiplier: cp.K,
) -> cp.K:
    return cp.add(
        cp.neg(cp.mul(epsilon, normal)),
        cp.mul(multiplier, cp.add(normal, curvature)),
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    checks = 0

    require(packet["schema"] == "boe.mtt.normal-frame-action-intertwiner.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T18", "claim id")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "contract hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1
    require(packet["finite_source_manifest_sha256"] == sha256(FSB_MANIFEST), "finite source manifest hash")
    checks += 1

    require(source_lock["repository_head_before"] == "ddc206737d1992f351f489442f062ad1580b2fee", "starting head")
    checks += 1
    require(source_lock["kernel_model_sha256"] == "592ef16dc03ce2195113b53cc75f8bb638bd27c279590ed3f5575d11dee05db8", "kernel model")
    checks += 1
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"missing source {source['path']}")
        require(sha256(path) == source["sha256"], f"source hash {source['path']}")
        checks += 1

    properties = schema["properties"]
    require(properties["schema"]["const"] == packet["schema"], "contract schema")
    checks += 1
    require(properties["normal_line"]["properties"]["invariant_multiplicity"]["const"] == 1, "normal multiplicity contract")
    checks += 1
    require(properties["normal_line"]["properties"]["unit_frame_selected"]["const"] is False, "frame boundary contract")
    checks += 1
    require(properties["normal_frame_quotient"]["properties"]["factorization_orbits_for_nonzero_response"]["const"] == 1, "factor orbit contract")
    checks += 1
    require(properties["finite_trace"]["properties"]["functional"]["const"] == "tau3(A)=Tr(A)/3", "trace contract")
    checks += 1
    require(properties["finite_trace"]["properties"]["physical_density_identified"]["const"] is False, "physical density boundary")
    checks += 1
    require(properties["physical_intertwiner"]["properties"]["required_identity"]["const"] == "H_eff=c_action H_resp", "intertwiner contract")
    checks += 1
    require(properties["physical_intertwiner"]["properties"]["absolute_scale_selected"]["const"] is False, "scale boundary")
    checks += 1

    weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    y16 = cp.diagonal([qscalar(value) for value in weights])
    p_neutral = cp.diagonal([cp.O if index == 15 else cp.Z for index in range(16)])
    require(cp.rank(y16) == 15, "hypercharge rank")
    checks += 1
    require(16 - cp.rank(y16) == 1, "unique zero weight")
    checks += 1
    require(cp.rank(p_neutral) == 1, "neutral projector rank")
    checks += 1
    require(cp.matrix_mul(y16, p_neutral) == cp.zero(16, 16), "neutral projector kernel")
    checks += 1
    require(packet["normal_line"]["carrier"] == "N^c subset H16", "packet normal carrier")
    checks += 1
    require(packet["normal_line"]["unit_frame_selected"] is False, "packet frame boundary")
    checks += 1

    a, b, hessian = routed_hessian()
    require(hessian == cp.adjoint(hessian), "Hermitian response")
    checks += 1
    require(cp.rank(hessian) == 24, "response rank")
    checks += 1
    require(48 - cp.rank(hessian) == 24, "response kernel")
    checks += 1
    norm2 = frobenius_inner(hessian, hessian)
    require(norm2 == qscalar(192), "response norm squared")
    checks += 1
    require(matrix_trace(hessian) == qscalar(-32), "response trace")
    checks += 1
    require(cp.divide(norm2, qscalar(48)) == qscalar(4), "full normalized square")
    checks += 1
    require(cp.divide(norm2, qscalar(24)) == qscalar(8), "active normalized square")
    checks += 1
    require(packet["contracted_response"]["frobenius_norm_squared"] == "192", "packet norm")
    checks += 1
    require(packet["contracted_response"]["new_matrix_added"] is False, "no new matrix")
    checks += 1

    shift, clock = weyl_pair()
    require(cp.matrix_mul(cp.adjoint(shift), shift) == cp.identity(3), "shift unitary")
    checks += 1
    require(cp.matrix_mul(cp.adjoint(clock), clock) == cp.identity(3), "clock unitary")
    checks += 1
    require(9 - cp.rank(cp.family_commutant_equations(shift, clock)) == 1, "Weyl commutant")
    checks += 1
    require(9 - cp.rank(cp.family_commutant_equations(a, b)) == 1, "response commutant")
    checks += 1
    rho = cp.matrix_scale(qscalar(Fraction(1, 3)), cp.identity(3))
    require(matrix_trace(rho) == cp.O, "density trace")
    checks += 1
    require(cp.matrix_mul(shift, cp.matrix_mul(rho, cp.adjoint(shift))) == rho, "shift-invariant density")
    checks += 1
    require(cp.matrix_mul(clock, cp.matrix_mul(rho, cp.adjoint(clock))) == rho, "clock-invariant density")
    checks += 1
    require(packet["finite_trace"]["finite_family_measure_parameters"] == 0, "no trace parameter")
    checks += 1
    require(packet["finite_trace"]["physical_BV_density_identified"] is False, "trace not physical density")
    checks += 1

    i_unit: cp.K = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    sqrt3: cp.K = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    frames = [qscalar(Fraction(3, 2)), qscalar(-5), i_unit, cp.add(qscalar(2), i_unit), cp.add(sqrt3, qscalar(-1))]
    curvatures = [qscalar(Fraction(7, 4)), i_unit, cp.add(qscalar(-2), sqrt3)]
    normals = [cp.add(qscalar(1), i_unit), qscalar(Fraction(-3, 7)), sqrt3]
    multipliers = [qscalar(4), cp.add(qscalar(-1), i_unit), cp.add(qscalar(2), sqrt3)]
    for frame in frames:
        inverse_frame = cp.inverse(frame)
        require(cp.matrix_scale(inverse_frame, cp.matrix_scale(frame, hessian)) == hessian, "frame contraction")
        checks += 1
        for curvature, normal, multiplier in zip(curvatures, normals, multipliers):
            base = complex_action(cp.O, curvature, normal, multiplier)
            transformed = complex_action(
                inverse_frame,
                cp.mul(frame, curvature),
                cp.mul(frame, normal),
                cp.mul(inverse_frame, multiplier),
            )
            require(base == transformed, "frame action")
            checks += 1

    for first, second in zip(frames, frames[1:] + frames[:1]):
        transition = cp.divide(second, first)
        require(cp.matrix_scale(transition, cp.matrix_scale(first, hessian)) == cp.matrix_scale(second, hessian), "factor transition")
        checks += 1
        require(cp.mul(cp.inverse(first), cp.inverse(transition)) == cp.inverse(second), "dual transition")
        checks += 1

    independent_scales = [Fraction(2, 3), Fraction(11, 5), Fraction(13, 2)]
    for scale in independent_scales:
        effective = cp.matrix_scale(qscalar(scale), hessian)
        recovered = cp.divide(frobenius_inner(hessian, effective), norm2)
        require(recovered == qscalar(scale), "scale recovery")
        checks += 1
        residual = matrix_sub(effective, cp.matrix_scale(recovered, hessian))
        require(residual == cp.zero(48, 48), "scale residual")
        checks += 1

    two_h = cp.matrix_scale(qscalar(2), hessian)
    seven_h = cp.matrix_scale(qscalar(7), hessian)
    require(two_h != seven_h, "absolute scales differ")
    checks += 1
    require(cp.matrix_scale(qscalar(7), two_h) == cp.matrix_scale(qscalar(2), seven_h), "projective shapes agree")
    checks += 1
    require(cp.rank(two_h) == cp.rank(seven_h) == 24, "scaled ranks agree")
    checks += 1

    require(packet["physical_intertwiner_minimal_data"]["coefficient_formula"] == "c_action=<H_resp,H_eff>_F/192", "packet coefficient formula")
    checks += 1
    require(packet["physical_intertwiner_minimal_data"]["same_root_physical_intertwiner_supplied"] is False, "same-root boundary")
    checks += 1
    require(packet["scale_nonidentifiability"]["normalized_shape_determines_absolute_scale"] is False, "scale no-go")
    checks += 1
    require(packet["parameter_ledger"]["normal_frame_parameters_after_quotient"] == 0, "frame ledger")
    checks += 1
    require(packet["parameter_ledger"]["finite_family_measure_parameters"] == 0, "trace ledger")
    checks += 1
    require(packet["parameter_ledger"]["conditional_common_action_coefficients_per_endpoint"] == 1, "scale ledger")
    checks += 1
    require(packet["parameter_ledger"]["selected_physical_action_coefficients"] == 0, "unselected scale ledger")
    checks += 1
    require(packet["parameter_ledger"]["strict_charged_magnitude_values_remaining"] == 9, "nine-value boundary")
    checks += 1
    require(packet["physical_packets_accepted"] == 0 and packet["physical_packets_total"] == 3, "packet acceptance")
    checks += 1
    require(packet["physical_rows_accepted"] == 0 and packet["physical_rows_total"] == 7, "row acceptance")
    checks += 1
    require(packet["claim_boundary"]["physical_action_scale_selected"] is False, "physical scale open")
    checks += 1
    require(packet["claim_boundary"]["Lorentz_Higgs_Yukawa_typing"] is False, "physical typing open")
    checks += 1
    require(all(packet["checks"].values()), "builder checks")
    checks += 1
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary")
    checks += 1

    print(f"independent normal-frame action-intertwiner verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
