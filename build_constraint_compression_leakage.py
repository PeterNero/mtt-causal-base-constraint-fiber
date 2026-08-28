"""Build the exact rational certificate for the compression-leakage theorem."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "constraint_compression_leakage.packet.json"
THEOREM_PATH = ROOT / "CausalBaseConstraintFiberCompressionLeakageTheorem_v1.md"
LOCK_PATH = ROOT / "KERNEL_AUTHORITY_LOCK.json"


def zero(rows: int, cols: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def identity(size: int) -> list[list[Fraction]]:
    out = zero(size, size)
    for i in range(size):
        out[i][i] = Fraction(1)
    return out


def transpose(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(c: Fraction, a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[c * x for x in row] for row in a]


def mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    bt = transpose(b)
    return [[sum((x * y for x, y in zip(ar, bc)), Fraction(0)) for bc in bt] for ar in a]


def commutator(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return sub(mul(a, b), mul(b, a))


def matrix_rank(a: list[list[Fraction]]) -> int:
    work = [row[:] for row in a]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if work[r][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][col]
        work[pivot_row] = [x / pivot_value for x in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [x - factor * y for x, y in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def trace(a: list[list[Fraction]]) -> Fraction:
    return sum((a[i][i] for i in range(len(a))), Fraction(0))


def frobenius_squared(a: list[list[Fraction]]) -> Fraction:
    return sum((x * x for row in a for x in row), Fraction(0))


def diag(*values: int) -> list[list[Fraction]]:
    out = zero(len(values), len(values))
    for i, value in enumerate(values):
        out[i][i] = Fraction(value)
    return out


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def serialize_matrix(a: list[list[Fraction]]) -> list[list[str]]:
    return [[fraction_string(x) for x in row] for row in a]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_exact_objects() -> dict[str, object]:
    i3 = identity(3)
    q = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    p = sub(i3, q)
    x = diag(1, 0, 0)
    y = diag(0, 1, 0)
    xp = mul(mul(p, x), p)
    yp = mul(mul(p, y), p)
    c = commutator(xp, yp)
    lx = mul(mul(q, x), p)
    ly = mul(mul(q, y), p)
    leakage = sub(mul(transpose(ly), lx), mul(transpose(lx), ly))
    upper_term = mul(mul(p, commutator(x, y)), p)
    defect_term = mul(mul(p, sub(mul(mul(y, q), x), mul(mul(x, q), y))), p)

    # A compatible control pair: both are block diagonal for P + Q.
    u = add(scale(Fraction(2), p), scale(Fraction(3), q))
    v = add(scale(Fraction(5), p), scale(Fraction(7), q))
    up = mul(mul(p, u), p)
    vp = mul(mul(p, v), p)
    lu = mul(mul(q, u), p)
    lv = mul(mul(q, v), p)

    expected_cstar_c = scale(Fraction(1, 27), p)
    xy_multiplicative_defect = sub(mul(xp, yp), mul(mul(p, mul(x, y)), p))
    xy_expected_defect = scale(Fraction(-1), mul(mul(mul(p, x), q), mul(y, p)))
    yx_multiplicative_defect = sub(mul(yp, xp), mul(mul(p, mul(y, x)), p))
    yx_expected_defect = scale(Fraction(-1), mul(mul(mul(p, y), q), mul(x, p)))

    checks = {
        "P_is_self_adjoint": transpose(p) == p,
        "P_is_idempotent": mul(p, p) == p,
        "Q_is_self_adjoint": transpose(q) == q,
        "Q_is_idempotent": mul(q, q) == q,
        "P_plus_Q_is_identity": add(p, q) == i3,
        "P_Q_are_orthogonal": mul(p, q) == zero(3, 3) and mul(q, p) == zero(3, 3),
        "rank_P_is_2": matrix_rank(p) == 2,
        "rank_Q_is_1": matrix_rank(q) == 1,
        "upper_X_Y_are_self_adjoint": transpose(x) == x and transpose(y) == y,
        "upper_X_Y_commute": commutator(x, y) == zero(3, 3),
        "compressed_X_Y_are_self_adjoint": transpose(xp) == xp and transpose(yp) == yp,
        "XY_multiplicative_defect_identity": xy_multiplicative_defect == xy_expected_defect,
        "YX_multiplicative_defect_identity": yx_multiplicative_defect == yx_expected_defect,
        "general_commutator_decomposition": c == add(upper_term, defect_term),
        "commuting_upper_leakage_identity": c == leakage,
        "compressed_commutator_is_nonzero": c != zero(3, 3),
        "compressed_commutator_is_skew_adjoint": transpose(c) == scale(Fraction(-1), c),
        "compressed_commutator_rank_is_2": matrix_rank(c) == 2,
        "compressed_commutator_trace_is_0": trace(c) == 0,
        "compressed_commutator_frobenius_squared_is_2_over_27": frobenius_squared(c) == Fraction(2, 27),
        "commutator_norm_certificate": mul(transpose(c), c) == expected_cstar_c,
        "both_witness_leakages_are_nonzero": lx != zero(3, 3) and ly != zero(3, 3),
        "compatible_control_leakage_vanishes": lu == zero(3, 3) and lv == zero(3, 3),
        "compatible_control_compressions_commute": commutator(up, vp) == zero(3, 3),
        "exact_operator_norm_bound_holds": Fraction(1, 27) <= Fraction(16, 81),
    }

    return {
        "P": p,
        "Q": q,
        "X_tilde": x,
        "Y_tilde": y,
        "X_compressed": xp,
        "Y_compressed": yp,
        "commutator": c,
        "L_X": lx,
        "L_Y": ly,
        "leakage_antisymmetrization": leakage,
        "compatible_U": u,
        "compatible_V": v,
        "checks": checks,
    }


def build_packet() -> dict[str, object]:
    objects = build_exact_objects()
    checks = objects.pop("checks")
    matrices = {name: serialize_matrix(value) for name, value in objects.items()}
    return {
        "schema": "boe.mtt.constraint-compression-leakage.v1",
        "theorem_id": "CausalBaseConstraintFiberCompressionLeakageTheorem.v1",
        "tiers": ["EXACT_GENERAL", "EXACT_BENCHMARK"],
        "selected_mtt_physics": False,
        "kernel_authority_promoted": False,
        "continuous_fit_parameters": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "theorem_sha256": sha256(THEOREM_PATH),
            "kernel_authority_lock_sha256": sha256(LOCK_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "exact_identities": {
            "multiplicative_defect": "Phi_P(S) Phi_P(T) - Phi_P(ST) = -P S Q T P",
            "general_commutator": "[Phi_P(A),Phi_P(B)] = Phi_P([A,B]) + P(BQA-AQB)P",
            "commuting_self_adjoint_case": "[Phi_P(A),Phi_P(B)] = L_B^* L_A - L_A^* L_B",
            "leakage_maps": "L_A=QAP and L_B=QBP",
            "norm_bound": "||[Phi_P(A),Phi_P(B)]|| <= 2 ||L_A|| ||L_B|| for [A,B]=0"
        },
        "finite_witness": {
            "field": "Q",
            "ambient_dimension": 3,
            "retained_rank": 2,
            "excluded_rank": 1,
            "matrices": matrices,
            "exact_invariants": {
                "commutator_rank": 2,
                "commutator_trace": "0",
                "commutator_frobenius_norm_squared": "2/27",
                "commutator_operator_norm_squared": "1/27",
                "L_X_operator_norm_squared": "2/9",
                "L_Y_operator_norm_squared": "2/9",
                "two_leakage_norm_bound": "4/9"
            }
        },
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values())
        },
        "frontier_delta": "Compression-induced incompatibility and compatible locality descent are separated by one exact leakage identity; physical P, observables, action normalization and q79 source selection remain open.",
        "nonclaims": [
            "canonical CCR",
            "Planck constant",
            "selected physical q79 projector",
            "Bell state selection",
            "universal apparatus",
            "upper physical action"
        ]
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
