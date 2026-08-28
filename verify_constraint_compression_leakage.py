"""Independently verify the generated compression-leakage packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "constraint_compression_leakage.packet.json"


def z(rows: int, cols: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def eye(n: int) -> list[list[Fraction]]:
    out = z(n, n)
    for i in range(n):
        out[i][i] = Fraction(1)
    return out


def t(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def plus(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def minus(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def times(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    bt = t(b)
    return [[sum((x * y for x, y in zip(ar, bc)), Fraction(0)) for bc in bt] for ar in a]


def scalar(c: Fraction, a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[c * x for x in row] for row in a]


def bracket(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return minus(times(a, b), times(b, a))


def diagonal(*entries: int) -> list[list[Fraction]]:
    out = z(len(entries), len(entries))
    for i, value in enumerate(entries):
        out[i][i] = Fraction(value)
    return out


def rank(a: list[list[Fraction]]) -> int:
    m = [row[:] for row in a]
    row = 0
    for col in range(len(m[0])):
        pivot = next((i for i in range(row, len(m)) if m[i][col] != 0), None)
        if pivot is None:
            continue
        m[row], m[pivot] = m[pivot], m[row]
        pv = m[row][col]
        m[row] = [x / pv for x in m[row]]
        for i in range(len(m)):
            if i != row and m[i][col] != 0:
                factor = m[i][col]
                m[i] = [x - factor * y for x, y in zip(m[i], m[row])]
        row += 1
        if row == len(m):
            break
    return row


def tr(a: list[list[Fraction]]) -> Fraction:
    return sum((a[i][i] for i in range(len(a))), Fraction(0))


def frob2(a: list[list[Fraction]]) -> Fraction:
    return sum((x * x for row in a for x in row), Fraction(0))


def parse_matrix(rows: list[list[str]]) -> list[list[Fraction]]:
    return [[Fraction(value) for value in row] for row in rows]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected() -> tuple[dict[str, list[list[Fraction]]], dict[str, bool]]:
    i = eye(3)
    q = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    p = minus(i, q)
    x = diagonal(1, 0, 0)
    y = diagonal(0, 1, 0)
    xp = times(times(p, x), p)
    yp = times(times(p, y), p)
    c = bracket(xp, yp)
    lx = times(times(q, x), p)
    ly = times(times(q, y), p)
    leak = minus(times(t(ly), lx), times(t(lx), ly))
    upper = times(times(p, bracket(x, y)), p)
    defect = times(times(p, minus(times(times(y, q), x), times(times(x, q), y))), p)
    u = plus(scalar(Fraction(2), p), scalar(Fraction(3), q))
    v = plus(scalar(Fraction(5), p), scalar(Fraction(7), q))
    up = times(times(p, u), p)
    vp = times(times(p, v), p)
    lu = times(times(q, u), p)
    lv = times(times(q, v), p)
    dxy = minus(times(xp, yp), times(times(p, times(x, y)), p))
    exy = scalar(Fraction(-1), times(times(times(p, x), q), times(y, p)))
    dyx = minus(times(yp, xp), times(times(p, times(y, x)), p))
    eyx = scalar(Fraction(-1), times(times(times(p, y), q), times(x, p)))

    matrices = {
        "P": p,
        "Q": q,
        "X_tilde": x,
        "Y_tilde": y,
        "X_compressed": xp,
        "Y_compressed": yp,
        "commutator": c,
        "L_X": lx,
        "L_Y": ly,
        "leakage_antisymmetrization": leak,
        "compatible_U": u,
        "compatible_V": v,
    }
    checks = {
        "P_is_self_adjoint": t(p) == p,
        "P_is_idempotent": times(p, p) == p,
        "Q_is_self_adjoint": t(q) == q,
        "Q_is_idempotent": times(q, q) == q,
        "P_plus_Q_is_identity": plus(p, q) == i,
        "P_Q_are_orthogonal": times(p, q) == z(3, 3) and times(q, p) == z(3, 3),
        "rank_P_is_2": rank(p) == 2,
        "rank_Q_is_1": rank(q) == 1,
        "upper_X_Y_are_self_adjoint": t(x) == x and t(y) == y,
        "upper_X_Y_commute": bracket(x, y) == z(3, 3),
        "compressed_X_Y_are_self_adjoint": t(xp) == xp and t(yp) == yp,
        "XY_multiplicative_defect_identity": dxy == exy,
        "YX_multiplicative_defect_identity": dyx == eyx,
        "general_commutator_decomposition": c == plus(upper, defect),
        "commuting_upper_leakage_identity": c == leak,
        "compressed_commutator_is_nonzero": c != z(3, 3),
        "compressed_commutator_is_skew_adjoint": t(c) == scalar(Fraction(-1), c),
        "compressed_commutator_rank_is_2": rank(c) == 2,
        "compressed_commutator_trace_is_0": tr(c) == 0,
        "compressed_commutator_frobenius_squared_is_2_over_27": frob2(c) == Fraction(2, 27),
        "commutator_norm_certificate": times(t(c), c) == scalar(Fraction(1, 27), p),
        "both_witness_leakages_are_nonzero": lx != z(3, 3) and ly != z(3, 3),
        "compatible_control_leakage_vanishes": lu == z(3, 3) and lv == z(3, 3),
        "compatible_control_compressions_commute": bracket(up, vp) == z(3, 3),
        "exact_operator_norm_bound_holds": Fraction(1, 27) <= Fraction(16, 81),
    }
    return matrices, checks


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    assert packet["schema"] == "boe.mtt.constraint-compression-leakage.v1"
    assert packet["theorem_id"] == "CausalBaseConstraintFiberCompressionLeakageTheorem.v1"
    assert packet["selected_mtt_physics"] is False
    assert packet["continuous_fit_parameters"] == 0
    assert packet["observed_physical_inputs"] == []

    matrices, checks = expected()
    stored = packet["finite_witness"]["matrices"]
    assert set(stored) == set(matrices)
    for name, value in matrices.items():
        assert parse_matrix(stored[name]) == value, f"matrix mismatch: {name}"

    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}

    sources = packet["source_hashes"]
    assert sources["theorem_sha256"] == sha256(ROOT / "CausalBaseConstraintFiberCompressionLeakageTheorem_v1.md")
    assert sources["kernel_authority_lock_sha256"] == sha256(ROOT / "KERNEL_AUTHORITY_LOCK.json")
    assert sources["builder_sha256"] == sha256(ROOT / "build_constraint_compression_leakage.py")

    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} exact checks")


if __name__ == "__main__":
    main()
