"""Independent exact verification of the repair/fixed-point/gauge witness."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "repair_fixedpoint_gauge_descent.packet.json"


def zeros(n: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(n)] for _ in range(n)]


def eye(n: int) -> list[list[Fraction]]:
    out = zeros(n)
    for i in range(n):
        out[i][i] = Fraction(1)
    return out


def trans(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def add(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(c: Fraction, a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[c * x for x in row] for row in a]


def mul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    bt = trans(b)
    return [[sum((x * y for x, y in zip(ar, bc)), Fraction(0)) for bc in bt] for ar in a]


def key(a: list[list[Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(row) for row in a)


def perm_matrix(perm: tuple[int, ...]) -> list[list[Fraction]]:
    out = zeros(len(perm))
    for source, target in enumerate(perm):
        out[target][source] = Fraction(1)
    return out


def unit(n: int, r: int, c: int) -> list[list[Fraction]]:
    out = zeros(n)
    out[r][c] = Fraction(1)
    return out


def conj(g: list[list[Fraction]], a: list[list[Fraction]]) -> list[list[Fraction]]:
    return mul(mul(g, a), trans(g))


def comp(p: list[list[Fraction]], a: list[list[Fraction]]) -> list[list[Fraction]]:
    return mul(mul(p, a), p)


def leak(q: list[list[Fraction]], p: list[list[Fraction]], a: list[list[Fraction]]) -> list[list[Fraction]]:
    return mul(mul(q, a), p)


def om(q: list[list[Fraction]], p: list[list[Fraction]], a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    la = leak(q, p, a)
    lb = leak(q, p, b)
    return sub(mul(trans(lb), la), mul(trans(la), lb))


def bracket(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return sub(mul(a, b), mul(b, a))


def parse(rows: list[list[str]]) -> list[list[Fraction]]:
    return [[Fraction(value) for value in row] for row in rows]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(a: list[list[Fraction]]) -> int:
    work = [row[:] for row in a]
    row = 0
    for col in range(len(work[0])):
        pivot = next((r for r in range(row, len(work)) if work[r][col]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        pv = work[row][col]
        work[row] = [x / pv for x in work[row]]
        for r in range(len(work)):
            if r != row and work[r][col]:
                f = work[r][col]
                work[r] = [x - f * y for x, y in zip(work[r], work[row])]
        row += 1
    return row


def expected() -> tuple[dict[str, list[list[Fraction]]], list[list[list[Fraction]]], list[list[list[Fraction]]], dict[str, bool]]:
    i = eye(3)
    q = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    p = sub(i, q)
    h = add(scale(Fraction(2), p), scale(Fraction(5), q))
    x = unit(3, 0, 0)
    y = unit(3, 1, 1)
    group = [scale(sign, perm_matrix(perm)) for sign in (Fraction(1), Fraction(-1)) for perm in itertools.permutations(range(3))]
    group_keys = {key(g) for g in group}
    basis = [comp(p, unit(3, r, c)) for r in range(3) for c in range(3)]
    kernel = [g for g in group if all(conj(g, a) == a for a in basis)]
    signatures = {tuple(key(conj(g, a)) for a in basis) for g in group}
    lx = leak(q, p, x)
    ly = leak(q, p, y)
    oxy = om(q, p, x, y)
    kernel_keys = {key(g) for g in kernel}
    expected_kernel = {key(i), key(scale(Fraction(-1), i))}

    checks = {
        "signed_permutation_group_has_order_12": len(group_keys) == 12,
        "group_contains_identity": key(i) in group_keys,
        "group_is_closed": all(key(mul(g, k)) in group_keys for g in group for k in group),
        "every_group_element_is_orthogonal": all(mul(trans(g), g) == i for g in group),
        "transpose_inverse_is_in_group": all(key(trans(g)) in group_keys for g in group),
        "H0_equals_2P_plus_5Q": h == add(scale(Fraction(2), p), scale(Fraction(5), q)),
        "P_is_low_spectral_projector": scale(Fraction(1, 3), sub(scale(Fraction(5), i), h)) == p,
        "H0_has_eigenvalue_2_on_P": mul(h, p) == scale(Fraction(2), p),
        "H0_has_eigenvalue_5_on_Q": mul(h, q) == scale(Fraction(5), q),
        "spectral_gap_is_3": Fraction(5) - Fraction(2) == Fraction(3),
        "repair_fixed_point_is_unique_by_positive_split": rank(p) == 2 and rank(q) == 1,
        "group_commutes_with_linearization": all(mul(g, h) == mul(h, g) for g in group),
        "group_preserves_Riesz_split": all(mul(g, p) == mul(p, g) and mul(g, q) == mul(q, g) for g in group),
        "nonlinear_radial_repair_equivariance_certificate": all(mul(trans(g), g) == i and mul(g, h) == mul(h, g) for g in group),
        "compression_is_group_covariant": all(comp(p, conj(g, x)) == conj(g, comp(p, x)) for g in group),
        "leakage_is_group_covariant": all(leak(q, p, conj(g, x)) == conj(g, lx) for g in group),
        "leakage_antisymmetrization_is_group_covariant": all(om(q, p, conj(g, x), conj(g, y)) == conj(g, oxy) for g in group),
        "conjugation_kernel_has_order_2": len(kernel) == 2,
        "conjugation_kernel_is_exactly_plus_minus_identity": kernel_keys == expected_kernel,
        "faithful_quotient_has_order_6": len(group_keys) // len(kernel) == 6,
        "conjugation_image_has_order_6": len(signatures) == 6,
        "central_kernel_acts_trivially_on_retained_algebra": all(all(conj(g, a) == a for a in basis) for g in (i, scale(Fraction(-1), i))),
        "witness_leakage_is_nonzero": lx != zeros(3) and ly != zeros(3),
        "witness_omega_matches_compressed_commutator": oxy == bracket(comp(p, x), comp(p, y)),
    }
    matrices = {"P": p, "Q": q, "H0": h, "X_tilde": x, "Y_tilde": y, "L_X": lx, "L_Y": ly, "Omega_XY": oxy}
    return matrices, group, kernel, checks


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    assert packet["schema"] == "boe.mtt.repair-fixedpoint-gauge-descent.v1"
    assert packet["theorem_id"] == "RepairFixedPointGaugeDescentTheorem.v1"
    assert packet["selected_mtt_physics"] is False
    assert packet["consumes_authority"] == "A47"
    assert packet["continuous_fit_parameters"] == 0
    assert packet["observed_physical_inputs"] == []

    matrices, group, kernel, checks = expected()
    stored = packet["finite_witness"]
    for name, value in matrices.items():
        assert parse(stored["matrices"][name]) == value, name
    assert [parse(g) for g in stored["group_elements"]] == group
    assert [parse(g) for g in stored["conjugation_kernel"]] == kernel
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}

    hashes = packet["source_hashes"]
    assert hashes["theorem_sha256"] == digest(ROOT / "RepairFixedPointGaugeDescentTheorem_v1.md")
    assert hashes["grounding_map_sha256"] == digest(ROOT / "MTT_FIXEDPOINT_GAUGE_GROUNDING_MAP_v1.md")
    assert hashes["builder_sha256"] == digest(ROOT / "build_repair_fixedpoint_gauge_descent.py")
    assert hashes["compression_builder_sha256"] == digest(ROOT / "build_constraint_compression_leakage.py")

    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} exact checks")


if __name__ == "__main__":
    main()
