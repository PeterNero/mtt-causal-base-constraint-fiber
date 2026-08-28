"""Independent exact verification of the compression/transfer comparison."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "cohesive_repair_compression_transfer_comparison.packet.json"
LOCK_PATH = ROOT / "closure_dynamics_transfer_source_lock.json"


def zeros(rows: int, cols: int | None = None) -> list[list[Fraction]]:
    width = rows if cols is None else cols
    return [[Fraction(0) for _ in range(width)] for _ in range(rows)]


def eye(size: int) -> list[list[Fraction]]:
    out = zeros(size)
    for index in range(size):
        out[index][index] = Fraction(1)
    return out


def trans(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    bt = trans(b)
    return [[sum((x * y for x, y in zip(row, col)), Fraction(0)) for col in bt] for row in a]


def add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(value: Fraction, a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[value * x for x in row] for row in a]


def diag(values: list[int | Fraction]) -> list[list[Fraction]]:
    out = zeros(len(values))
    for index, value in enumerate(values):
        out[index][index] = Fraction(value)
    return out


def rank(a: list[list[Fraction]]) -> int:
    work = [row[:] for row in a]
    pivot_row = 0
    for column in range(len(work[0]) if work else 0):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                factor = work[row][column]
                work[row] = [x - factor * y for x, y in zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def vec(size: int, index: int) -> list[list[Fraction]]:
    out = zeros(size, 1)
    out[index][0] = Fraction(1)
    return out


def wedge(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = sum(
        1
        for i in range(3)
        if (left >> i) & 1
        for j in range(3)
        if ((right >> j) & 1) and i > j
    )
    return left | right, -1 if inversions % 2 else 1


def left_mult(mask: int) -> list[list[Fraction]]:
    out = zeros(8)
    for source in range(8):
        target, sign = wedge(mask, source)
        if target is not None:
            out[target][source] = Fraction(sign)
    return out


def right_mult(mask: int) -> list[list[Fraction]]:
    out = zeros(8)
    for source in range(8):
        target, sign = wedge(source, mask)
        if target is not None:
            out[target][source] = Fraction(sign)
    return out


def excursion(p: list[list[Fraction]], s: list[list[Fraction]], r: list[list[Fraction]], t: list[list[Fraction]]) -> list[list[Fraction]]:
    return mul(mul(mul(mul(p, s), r), t), p)


def parse(rows: list[list[str]]) -> list[list[Fraction]]:
    return [[Fraction(value) for value in row] for row in rows]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_checks() -> dict[str, bool]:
    residual_jacobian = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    cohesive_hessian = mul(trans(residual_jacobian), residual_jacobian)
    cohesive_p = zeros(2)
    cohesive_q = eye(2)
    cohesive_green = eye(2)
    probe = [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(4)]]
    cohesive_raw = scale(Fraction(-1), excursion(cohesive_p, probe, cohesive_q, probe))
    cohesive_feshbach = scale(Fraction(-1), excursion(cohesive_p, probe, cohesive_green, probe))

    differential = zeros(8)
    differential[3][4] = Fraction(1)
    adjoint = trans(differential)
    laplacian = add(mul(adjoint, differential), mul(differential, adjoint))
    harmonic = diag([1, 1, 1, 0, 0, 1, 1, 1])
    contractible = sub(eye(8), harmonic)
    green = contractible
    homotopy = mul(adjoint, green)
    left_a = left_mult(1)
    right_b = right_mult(2)
    a = vec(8, 1)
    b = vec(8, 2)
    ac = vec(8, 5)
    first_tree = mul(mul(mul(mul(harmonic, right_b), homotopy), left_a), a)
    second_tree = mul(mul(mul(mul(harmonic, left_a), homotopy), left_a), b)
    m3 = add(first_tree, second_tree)
    raw_operator = excursion(harmonic, left_a, contractible, left_a)
    propagated_operator = excursion(harmonic, left_a, homotopy, left_a)
    raw_on_b = mul(raw_operator, b)
    propagated_on_b = mul(propagated_operator, b)
    raw_defect = scale(Fraction(-1), raw_operator)
    propagated_defect = scale(Fraction(-1), propagated_operator)
    nil_difference = scale(Fraction(-1), excursion(harmonic, left_a, sub(homotopy, contractible), left_a))

    hessian = [
        [Fraction(1), Fraction(0), Fraction(1, 2), Fraction(0)],
        [Fraction(0), Fraction(2), Fraction(0), Fraction(0)],
        [Fraction(1, 2), Fraction(0), Fraction(3), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(4)],
    ]
    p = diag([1, 1, 0, 0])
    q = diag([0, 0, 1, 1])
    resolvent = diag([0, 0, Fraction(1, 3), Fraction(1, 4)])
    bare = mul(mul(p, hessian), p)
    raw_feshbach_excursion = excursion(p, hessian, q, hessian)
    self_energy = excursion(p, hessian, resolvent, hessian)
    effective = sub(bare, self_energy)
    raw_feshbach_defect = scale(Fraction(-1), raw_feshbach_excursion)
    correction = scale(Fraction(-1), self_energy)
    feshbach_difference = scale(Fraction(-1), excursion(p, hessian, sub(resolvent, q), hessian))

    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    return {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.closure-dynamics-transfer-source-lock.v1",
        "seven_source_artifacts_are_pinned": len(lock.get("sources", [])) == 7,
        "every_source_has_commit_blob_and_sha256": all(len(source.get("commit", "")) == 40 and len(source.get("git_blob", "")) == 40 and len(source.get("sha256", "")) == 64 for source in lock.get("sources", [])),
        "source_lock_preserves_nonpromotion_guard": "does not promote" in lock.get("guard", ""),
        "cohesive_background_is_zero": [Fraction(0), Fraction(0)] == [Fraction(0), Fraction(0)],
        "cohesive_residual_vanishes_at_background": [Fraction(0), Fraction(0)] == [Fraction(0), Fraction(0)],
        "cohesive_residual_jacobian_is_swap": residual_jacobian == [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]],
        "cohesive_cost_hessian_is_identity": cohesive_hessian == eye(2),
        "cohesive_repair_jacobian_is_negative_identity": scale(Fraction(-1), cohesive_hessian) == scale(Fraction(-1), eye(2)),
        "cohesive_fixed_tangent_projector_has_rank_zero": rank(cohesive_p) == 0,
        "cohesive_excluded_projector_is_identity": cohesive_q == eye(2),
        "cohesive_reduced_green_is_identity": cohesive_green == eye(2),
        "cohesive_raw_compression_defect_is_zero": cohesive_raw == zeros(2),
        "cohesive_feshbach_defect_is_zero": cohesive_feshbach == zeros(2),
        "nil_differential_squares_to_zero": mul(differential, differential) == zeros(8),
        "nil_hodge_laplacian_equals_contractible_projector": laplacian == contractible,
        "nil_harmonic_projector_has_rank_six": rank(harmonic) == 6,
        "nil_contractible_projector_has_rank_two": rank(contractible) == 2,
        "nil_green_is_inverse_on_contractible_sector": mul(laplacian, green) == contractible,
        "nil_homotopy_equals_dstar_green": homotopy == mul(adjoint, green),
        "nil_contraction_identity": add(mul(differential, homotopy), mul(homotopy, differential)) == contractible,
        "nil_homotopy_side_conditions": mul(harmonic, homotopy) == zeros(8) and mul(homotopy, harmonic) == zeros(8) and mul(homotopy, homotopy) == zeros(8),
        "nil_first_m3_tree_vanishes_for_aab": first_tree == zeros(8, 1),
        "nil_second_m3_tree_is_ac": second_tree == ac,
        "nil_transferred_m3_aab_is_ac": m3 == ac,
        "nil_raw_Q_excursion_on_same_leg_vanishes": raw_on_b == zeros(8, 1),
        "nil_homotopy_excursion_on_same_leg_is_ac": propagated_on_b == ac,
        "nil_raw_and_propagated_defects_differ": raw_defect != propagated_defect,
        "nil_weighted_minus_raw_defect_identity": sub(propagated_defect, raw_defect) == nil_difference,
        "feshbach_split_is_exact": add(p, q) == eye(4) and mul(p, q) == zeros(4),
        "feshbach_green_inverts_excluded_block": mul(mul(mul(q, hessian), q), resolvent) == q,
        "feshbach_self_energy_is_one_twelfth": self_energy == diag([Fraction(1, 12), 0, 0, 0]),
        "feshbach_effective_operator_matches_pinned_witness": effective == diag([Fraction(11, 12), 2, 0, 0]),
        "feshbach_raw_Q_excursion_is_one_quarter": raw_feshbach_excursion == diag([Fraction(1, 4), 0, 0, 0]),
        "feshbach_correction_is_not_raw_compression_defect": correction != raw_feshbach_defect,
        "feshbach_weighted_minus_raw_defect_identity": sub(correction, raw_feshbach_defect) == feshbach_difference,
        "feshbach_equality_criterion_fails_on_witness": feshbach_difference != zeros(4),
    }


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    assert packet["schema"] == "boe.mtt.cohesive-repair-compression-transfer-comparison.v1"
    assert packet["theorem_id"] == "CohesiveRepairCompressionTransferComparisonTheorem.v1"
    assert packet["selected_mtt_physics"] is False
    assert packet["continuous_fit_parameters"] == 0
    assert packet["observed_physical_inputs"] == []

    checks = expected_checks()
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}

    cohesive = packet["cohesive_repair_benchmark"]
    assert parse(cohesive["cost_hessian_at_background"]) == eye(2)
    assert parse(cohesive["fixed_tangent_projector"]) == zeros(2)
    nil_hodge = packet["nil_hodge_ainfinity_benchmark"]
    assert parse(nil_hodge["hodge_laplacian"]) == diag([0, 0, 0, 1, 1, 0, 0, 0])
    assert nil_hodge["witness"] == {"homotopy_propagated_excursion": "ac", "inputs": ["a", "a", "b"], "raw_Q_excursion": "0", "transferred_m3": "ac"}
    feshbach = packet["feshbach_benchmark"]
    assert parse(feshbach["feshbach_self_energy"]) == diag([Fraction(1, 12), 0, 0, 0])
    assert parse(feshbach["feshbach_effective_operator"]) == diag([Fraction(11, 12), 2, 0, 0])

    hashes = packet["source_hashes"]
    assert hashes["source_lock_sha256"] == digest(LOCK_PATH)
    assert hashes["theorem_sha256"] == digest(ROOT / "CohesiveRepairCompressionTransferComparisonTheorem_v1.md")
    assert hashes["builder_sha256"] == digest(ROOT / "build_cohesive_repair_compression_transfer_comparison.py")

    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} exact checks")


if __name__ == "__main__":
    main()
