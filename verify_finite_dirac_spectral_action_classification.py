#!/usr/bin/env python3
"""Independent exact reconstruction of the CBF.T27 spectral classification."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import build_closure_pressure_family_hessian_activation as cp


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "finite_dirac_spectral_action_classification.packet.json"
SOURCE_LOCK_PATH = ROOT / "finite_dirac_spectral_action_classification_source_lock.json"
SCHEMA_PATH = ROOT / "finite_dirac_spectral_action_classification_contract.schema.json"
THEOREM_PATH = ROOT / "CanonicalFiniteDiracSpectralActionClassificationAndProfileSelectionNoGoTheorem_v1.md"
T20_PATH = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PATH = ROOT / "physical_yukawa_hessian.packet.json"
T26_PATH = ROOT / "direct_dirac_defect_repair_action.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def decode_matrix(payload: list[list[list[str]]]) -> cp.Matrix:
    return [[cp.decode(value) for value in row] for row in payload]


def encode_matrix(matrix: cp.Matrix) -> list[list[list[str]]]:
    return [[cp.encode(value) for value in row] for row in matrix]


def matrix_digest(matrix: cp.Matrix) -> str:
    payload = json.dumps(encode_matrix(matrix), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def sparse_matmul(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not compose")
    result = cp.zero(len(left), len(right[0]))
    for row, left_row in enumerate(left):
        for inner, left_value in enumerate(left_row):
            if left_value == cp.ZERO:
                continue
            for column, right_value in enumerate(right[inner]):
                if right_value == cp.ZERO:
                    continue
                result[row][column] = cp.kadd(
                    result[row][column], cp.kmul(left_value, right_value)
                )
    return result


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def block_diag(blocks: list[cp.Matrix]) -> cp.Matrix:
    rows = sum(len(block) for block in blocks)
    columns = sum(len(block[0]) for block in blocks)
    result = cp.zero(rows, columns)
    row_offset = 0
    column_offset = 0
    for block in blocks:
        for row, values in enumerate(block):
            for column, value in enumerate(values):
                result[row_offset + row][column_offset + column] = value
        row_offset += len(block)
        column_offset += len(block[0])
    return result


def conjugate(matrix: cp.Matrix) -> cp.Matrix:
    return [[cp.kconj(value) for value in row] for row in matrix]


def incidence(pairs: tuple[tuple[int, int], ...]) -> cp.Matrix:
    result = cp.zero(16, 16)
    for target, source in pairs:
        result[target][source] = cp.ONE
    return result


def family_map(projector: cp.Matrix, direction: cp.Matrix, t: Fraction) -> cp.Matrix:
    return cp.madd(cp.mscale(q(-1), projector), cp.mscale(q(t), direction))


def transfer(
    projector: cp.Matrix,
    phase_direction: cp.Matrix,
    shift_direction: cp.Matrix,
    t: Fraction,
) -> cp.Matrix:
    v_phase = incidence(((0, 6), (1, 7), (2, 8), (13, 14)))
    v_shift = incidence(((3, 9), (4, 10), (5, 11), (12, 15)))
    return cp.madd(
        cp.kron(family_map(projector, phase_direction, t), v_phase),
        cp.kron(family_map(projector, shift_direction, t), v_shift),
    )


def physical_dirac(transfer_matrix: cp.Matrix) -> cp.Matrix:
    particle = cp.madd(transfer_matrix, cp.adjoint(transfer_matrix))
    return block_diag([particle, conjugate(particle)])


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for index in range(len(matrix)):
        total = cp.kadd(total, matrix[index][index])
    return total


def real_trace(matrix: cp.Matrix) -> Fraction:
    value = matrix_trace(matrix)
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"non-real trace {value}")
    return value[0]


def add_scalar(matrix: cp.Matrix, scalar: Fraction | int) -> cp.Matrix:
    return cp.madd(matrix, cp.mscale(q(scalar), cp.identity(len(matrix))))


def spectral_projector(hessian: cp.Matrix, eigenvalue: int) -> cp.Matrix:
    result = cp.identity(len(hessian))
    denominator = 1
    for other in (-4, -2, 2):
        if other == eigenvalue:
            continue
        result = sparse_matmul(result, add_scalar(hessian, -other))
        denominator *= eigenvalue - other
    return cp.mscale(q(Fraction(1, denominator)), result)


def moment_one(t: Fraction) -> Fraction:
    return 2 * t**2 - Fraction(4, 3) * t + 1


def moment_two(t: Fraction) -> Fraction:
    return (
        6 * t**4
        - Fraction(32, 3) * t**3
        + 12 * t**2
        - Fraction(8, 3) * t
        + 1
    )


def repair_action(t: Fraction) -> Fraction:
    return 4 * t**2 - Fraction(16, 3) * t**3 + 3 * t**4


def quartic_cubic(t: Fraction) -> Fraction:
    return 9 * t**3 - 12 * t**2 + 9 * t - 1


def require(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="ascii"))
    source_lock = json.loads(SOURCE_LOCK_PATH.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="ascii"))
    t20 = json.loads(T20_PATH.read_text(encoding="ascii"))
    t23 = json.loads(T23_PATH.read_text(encoding="ascii"))
    t26 = json.loads(T26_PATH.read_text(encoding="ascii"))
    passed: list[str] = []

    require(
        packet["schema"] == "boe.mtt.finite-dirac-spectral-action-classification.v1",
        "packet schema",
        passed,
    )
    require(packet["claim_id"] == "CBF.T27", "claim id", passed)
    require(set(packet) == set(schema["properties"]), "strict top-level schema", passed)
    require(
        source_lock["handoff_id"] == "b5346b8d-1373-42c2-bee8-e0ddab69ef62",
        "handoff pin",
        passed,
    )
    for source in source_lock["local_sources"]:
        path = (ROOT / source["path"]).resolve()
        require(path.is_file(), f"source exists: {source['path']}", passed)
        require(
            sha256(path) == source["sha256"],
            f"source hash: {source['path']}",
            passed,
        )

    primitive = t20["primitive_source"]["primitive_payload"]
    p = decode_matrix(primitive["P"])
    x = decode_matrix(primitive["X"])
    z = decode_matrix(primitive["Z"])
    fourier = decode_matrix(primitive["F3"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = physical_dirac(transfer(p, phase_direction, shift_direction, Fraction(0)))
    d_at_one = physical_dirac(
        transfer(p, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)
    d0d1 = sparse_matmul(d0, d1)
    d1d0 = sparse_matmul(d1, d0)
    hessian = cp.madd(d0d1, d1d0)
    hessian2 = sparse_matmul(hessian, hessian)
    remainder = sparse_matmul(d1, d1)

    require(sparse_matmul(d0, d0) == identity96, "D0 square", passed)
    require(d0d1 == d1d0, "D0-D1 commutation", passed)
    require(
        d1 == cp.mscale(q(Fraction(1, 2)), sparse_matmul(d0, hessian)),
        "D1 factorization",
        passed,
    )
    require(
        remainder == cp.mscale(q(Fraction(1, 4)), hessian2),
        "R equals H squared over four",
        passed,
    )
    require(hessian == cp.adjoint(hessian), "H self-adjoint", passed)
    require(
        matrix_digest(hessian) == t23["hessian_compression"]["KO6_response_sha256"],
        "T23 H digest",
        passed,
    )
    require(
        matrix_digest(hessian) == packet["finite_source"]["H_phys_sha256"],
        "packet H digest",
        passed,
    )

    minimal = sparse_matmul(
        add_scalar(hessian, 4),
        sparse_matmul(add_scalar(hessian, 2), add_scalar(hessian, -2)),
    )
    require(minimal == cp.zero(96, 96), "H minimal polynomial", passed)
    projectors = {
        eigenvalue: spectral_projector(hessian, eigenvalue)
        for eigenvalue in (-4, -2, 2)
    }
    projector_sum = cp.zero(96, 96)
    for eigenvalue, projector in projectors.items():
        projector_sum = cp.madd(projector_sum, projector)
        require(projector == cp.adjoint(projector), f"P{eigenvalue} self-adjoint", passed)
        require(
            sparse_matmul(projector, projector) == projector,
            f"P{eigenvalue} idempotent",
            passed,
        )
        require(cp.matrix_rank(projector) == 32, f"P{eigenvalue} rank", passed)
        require(real_trace(projector) == 32, f"P{eigenvalue} trace", passed)
    require(projector_sum == identity96, "spectral resolution", passed)
    for left in projectors:
        for right in projectors:
            if left < right:
                require(
                    sparse_matmul(projectors[left], projectors[right]) == cp.zero(96, 96),
                    f"P{left}-P{right} orthogonality",
                    passed,
                )

    d0_plus = cp.mscale(q(Fraction(1, 2)), cp.madd(identity96, d0))
    d0_minus = cp.mscale(q(Fraction(1, 2)), matrix_sub(identity96, d0))
    for eigenvalue, projector in projectors.items():
        for sign, sign_projector in ((1, d0_plus), (-1, d0_minus)):
            joint = sparse_matmul(projector, sign_projector)
            require(
                cp.matrix_rank(joint) == 16,
                f"joint H={eigenvalue},D0={sign} rank",
                passed,
            )
            require(
                real_trace(joint) == 16,
                f"joint H={eigenvalue},D0={sign} trace",
                passed,
            )

    phase_fourier = sparse_matmul(
        cp.adjoint(fourier), sparse_matmul(shift_direction, fourier)
    )
    baseline_fourier = sparse_matmul(cp.adjoint(fourier), sparse_matmul(p, fourier))
    require(phase_fourier == phase_direction, "Fourier direction covariance", passed)
    require(baseline_fourier == p, "Fourier baseline invariance", passed)

    samples = [
        Fraction(-2),
        Fraction(-1),
        Fraction(-1, 2),
        Fraction(0),
        Fraction(1, 3),
        Fraction(1, 2),
        Fraction(1),
        Fraction(2),
    ]
    for t in samples:
        direct = physical_dirac(transfer(p, phase_direction, shift_direction, t))
        expected = sparse_matmul(
            d0, cp.madd(identity96, cp.mscale(q(t / 2), hessian))
        )
        require(direct == expected, f"D factorization at {t}", passed)
        direct_square = sparse_matmul(direct, direct)
        expected_square = cp.zero(96, 96)
        branch = {-4: (2 * t - 1) ** 2, -2: (t - 1) ** 2, 2: (t + 1) ** 2}
        for eigenvalue, projector in projectors.items():
            expected_square = cp.madd(
                expected_square, cp.mscale(q(branch[eigenvalue]), projector)
            )
        require(direct_square == expected_square, f"square spectrum at {t}", passed)
        require(
            real_trace(direct_square) / 96 == moment_one(t),
            f"first moment at {t}",
            passed,
        )
        require(
            real_trace(sparse_matmul(direct_square, direct_square)) / 96
            == moment_two(t),
            f"second moment at {t}",
            passed,
        )

    profiles = packet["profile_examples"]
    require(
        profiles["dirac_norm"]["unique_global_minimizer"] == "t=1/3",
        "Dirac norm minimizer",
        passed,
    )
    require(moment_one(Fraction(1, 3)) / 2 == Fraction(7, 18), "Dirac norm minimum", passed)
    require(quartic_cubic(Fraction(132, 1000)) < 0, "quartic lower bracket", passed)
    require(quartic_cubic(Fraction(133, 1000)) > 0, "quartic upper bracket", passed)
    require(24**2 - 4 * 27 * 9 == -396, "quartic root uniqueness", passed)
    require(quartic_cubic(Fraction(1, 3)) == 1, "profile disagreement", passed)
    require(repair_action(Fraction(0)) == 0, "repair zero", passed)
    require(
        t26["positivity_and_stationarity"]["real_stationary_set"] == ["t=0"],
        "T26 repair stationary set",
        passed,
    )
    require(
        profiles["normalized_logdet"]["stationary_equation"] == "3t^2-t-1=0",
        "logdet stationary equation",
        passed,
    )
    require(
        packet["heat_profile_no_go"]["derivative_at_candidate_positive_for_all_tau"],
        "heat derivative sign",
        passed,
    )
    require(
        Fraction(-1, 9) > Fraction(-16, 9)
        and Fraction(-4, 9) > Fraction(-16, 9),
        "heat exponent ordering",
        passed,
    )
    require(
        not packet["heat_profile_no_go"]["common_stationary_coordinate_exists"],
        "heat common-stationary no-go",
        passed,
    )
    require(
        not packet["spectral_functional"]["profile_f_selected_by_trace_theorem"],
        "trace does not select profile",
        passed,
    )
    require(
        packet["profile_selection_no_go"]["profile_choice_changes_stationary_coordinate"],
        "profile-selection no-go",
        passed,
    )
    require(
        not packet["coordinate_interpretation"]["D_phys_at_closure_is_zero"],
        "closure operator nonzero",
        passed,
    )
    require(
        packet["full_spectrum"]["D_phys_at_zero_spectrum"] == {"-1": 48, "1": 48},
        "closure signed spectrum",
        passed,
    )

    boundary = source_lock["boundary"]
    require(boundary["exact_full_spectrum_after"], "full spectrum boundary", passed)
    require(boundary["exact_D0_H_factorization_after"], "factorization boundary", passed)
    require(
        not boundary["profile_independent_stationary_coordinate_exists"],
        "profile-independent coordinate boundary",
        passed,
    )
    require(
        not packet["physical_boundary"]["selected_physical_action_profile"],
        "physical profile open",
        passed,
    )
    require(
        not packet["physical_boundary"]["nonzero_physical_source_coordinate_selected"],
        "physical coordinate open",
        passed,
    )
    require(not packet["physical_boundary"]["B_ACTION_01_closed"], "B.ACTION.01 open", passed)
    require(not packet["physical_boundary"]["B_SM_02_closed"], "B.SM.02 open", passed)
    require(packet["physical_packets_accepted"] == 0, "packet acceptance unchanged", passed)
    require(packet["physical_rows_accepted"] == 0, "row acceptance unchanged", passed)
    require(packet["parameter_ledger"]["new_fitted_coefficients"] == 0, "no fit", passed)
    require(
        packet["parameter_ledger"]["new_observed_construction_inputs"] == 0,
        "no observed input",
        passed,
    )

    root_payload: dict[str, Any] = {
        "schema": "boe.mtt.finite-dirac-spectral-action-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "finite_source": "D_phys(t)=D0(I96+t H_phys/2)",
        "H_phys_sha256": matrix_digest(hessian),
        "H_phys_spectrum": {"-4": 32, "-2": 32, "2": 32},
        "D_phys_squared_spectrum": {
            "(2t-1)^2": 32,
            "(t-1)^2": 32,
            "(t+1)^2": 32,
        },
        "universal_spectral_functional": (
            "tau96 f(D_phys(t)^2)="
            "[f((t-1)^2)+f((t+1)^2)+f((2t-1)^2)]/3"
        ),
        "profile_independent_stationary_coordinate": None,
        "selected_physical_profile": None,
        "observed_targets": [],
        "theorem_sha256": sha256(THEOREM_PATH),
    }
    root_hash = hashlib.sha256(
        json.dumps(root_payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    require(
        root_payload == packet["source_provenance"]["source_root_payload"],
        "source-root payload",
        passed,
    )
    require(
        root_hash == packet["source_provenance"]["source_root_sha256"],
        "source-root digest",
        passed,
    )
    require(all(packet["checks"].values()), "builder checks", passed)
    require(
        packet["check_summary"]["passed"] == packet["check_summary"]["total"],
        "builder check summary",
        passed,
    )

    print(f"CBF.T27 independent verification passed: {len(passed)}/{len(passed)} checks")


if __name__ == "__main__":
    main()
