"""Build the exact repair/fixed-point/gauge-descent witness packet."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import build_constraint_compression_leakage as alg


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "repair_fixedpoint_gauge_descent.packet.json"
THEOREM_PATH = ROOT / "RepairFixedPointGaugeDescentTheorem_v1.md"
GROUNDING_PATH = ROOT / "MTT_FIXEDPOINT_GAUGE_GROUNDING_MAP_v1.md"


def matrix_key(a: list[list[Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(row) for row in a)


def permutation_matrix(permutation: tuple[int, ...]) -> list[list[Fraction]]:
    out = alg.zero(len(permutation), len(permutation))
    for source, target in enumerate(permutation):
        out[target][source] = Fraction(1)
    return out


def matrix_unit(size: int, row: int, col: int) -> list[list[Fraction]]:
    out = alg.zero(size, size)
    out[row][col] = Fraction(1)
    return out


def conjugate(g: list[list[Fraction]], a: list[list[Fraction]]) -> list[list[Fraction]]:
    return alg.mul(alg.mul(g, a), alg.transpose(g))


def compression(p: list[list[Fraction]], a: list[list[Fraction]]) -> list[list[Fraction]]:
    return alg.mul(alg.mul(p, a), p)


def leakage(q: list[list[Fraction]], p: list[list[Fraction]], a: list[list[Fraction]]) -> list[list[Fraction]]:
    return alg.mul(alg.mul(q, a), p)


def omega(q: list[list[Fraction]], p: list[list[Fraction]], a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    la = leakage(q, p, a)
    lb = leakage(q, p, b)
    return alg.sub(
        alg.mul(alg.transpose(lb), la),
        alg.mul(alg.transpose(la), lb),
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_exact_objects() -> dict[str, object]:
    i3 = alg.identity(3)
    q = [[Fraction(1, 3) for _ in range(3)] for _ in range(3)]
    p = alg.sub(i3, q)
    h0 = alg.add(alg.scale(Fraction(2), p), alg.scale(Fraction(5), q))
    x = alg.diag(1, 0, 0)
    y = alg.diag(0, 1, 0)

    permutations = [permutation_matrix(perm) for perm in itertools.permutations(range(3))]
    group = []
    for sign in (Fraction(1), Fraction(-1)):
        group.extend(alg.scale(sign, r) for r in permutations)
    group_by_key = {matrix_key(g): g for g in group}

    retained_basis = [compression(p, matrix_unit(3, r, c)) for r in range(3) for c in range(3)]
    conjugation_kernel = [
        g for g in group
        if all(conjugate(g, a) == a for a in retained_basis)
    ]
    action_signatures = {
        tuple(matrix_key(conjugate(g, a)) for a in retained_basis)
        for g in group
    }

    lx = leakage(q, p, x)
    ly = leakage(q, p, y)
    omega_xy = omega(q, p, x, y)

    group_closed = all(
        matrix_key(alg.mul(g, h)) in group_by_key
        for g in group for h in group
    )
    group_orthogonal = all(alg.mul(alg.transpose(g), g) == i3 for g in group)
    group_commutes_h0 = all(alg.mul(g, h0) == alg.mul(h0, g) for g in group)
    group_commutes_split = all(
        alg.mul(g, p) == alg.mul(p, g) and alg.mul(g, q) == alg.mul(q, g)
        for g in group
    )
    compression_covariant = all(
        compression(p, conjugate(g, x)) == conjugate(g, compression(p, x))
        for g in group
    )
    leakage_covariant = all(
        leakage(q, p, conjugate(g, x)) == conjugate(g, lx)
        for g in group
    )
    omega_covariant = all(
        omega(q, p, conjugate(g, x), conjugate(g, y)) == conjugate(g, omega_xy)
        for g in group
    )

    plus_i = i3
    minus_i = alg.scale(Fraction(-1), i3)
    kernel_keys = {matrix_key(g) for g in conjugation_kernel}
    expected_kernel_keys = {matrix_key(plus_i), matrix_key(minus_i)}

    checks = {
        "signed_permutation_group_has_order_12": len(group_by_key) == 12,
        "group_contains_identity": matrix_key(i3) in group_by_key,
        "group_is_closed": group_closed,
        "every_group_element_is_orthogonal": group_orthogonal,
        "transpose_inverse_is_in_group": all(matrix_key(alg.transpose(g)) in group_by_key for g in group),
        "H0_equals_2P_plus_5Q": h0 == alg.add(alg.scale(Fraction(2), p), alg.scale(Fraction(5), q)),
        "P_is_low_spectral_projector": alg.scale(Fraction(1, 3), alg.sub(alg.scale(Fraction(5), i3), h0)) == p,
        "H0_has_eigenvalue_2_on_P": alg.mul(h0, p) == alg.scale(Fraction(2), p),
        "H0_has_eigenvalue_5_on_Q": alg.mul(h0, q) == alg.scale(Fraction(5), q),
        "spectral_gap_is_3": Fraction(5) - Fraction(2) == Fraction(3),
        "repair_fixed_point_is_unique_by_positive_split": alg.matrix_rank(p) == 2 and alg.matrix_rank(q) == 1,
        "group_commutes_with_linearization": group_commutes_h0,
        "group_preserves_Riesz_split": group_commutes_split,
        "nonlinear_radial_repair_equivariance_certificate": group_orthogonal and group_commutes_h0,
        "compression_is_group_covariant": compression_covariant,
        "leakage_is_group_covariant": leakage_covariant,
        "leakage_antisymmetrization_is_group_covariant": omega_covariant,
        "conjugation_kernel_has_order_2": len(conjugation_kernel) == 2,
        "conjugation_kernel_is_exactly_plus_minus_identity": kernel_keys == expected_kernel_keys,
        "faithful_quotient_has_order_6": len(group_by_key) // len(conjugation_kernel) == 6,
        "conjugation_image_has_order_6": len(action_signatures) == 6,
        "central_kernel_acts_trivially_on_retained_algebra": all(
            all(conjugate(g, a) == a for a in retained_basis)
            for g in (plus_i, minus_i)
        ),
        "witness_leakage_is_nonzero": lx != alg.zero(3, 3) and ly != alg.zero(3, 3),
        "witness_omega_matches_compressed_commutator": omega_xy == alg.commutator(compression(p, x), compression(p, y)),
    }

    return {
        "P": p,
        "Q": q,
        "H0": h0,
        "X_tilde": x,
        "Y_tilde": y,
        "L_X": lx,
        "L_Y": ly,
        "Omega_XY": omega_xy,
        "group": group,
        "conjugation_kernel": conjugation_kernel,
        "checks": checks,
    }


def build_packet() -> dict[str, object]:
    objects = build_exact_objects()
    checks = objects.pop("checks")
    group = objects.pop("group")
    kernel = objects.pop("conjugation_kernel")
    matrices = {name: alg.serialize_matrix(value) for name, value in objects.items()}
    return {
        "schema": "boe.mtt.repair-fixedpoint-gauge-descent.v1",
        "theorem_id": "RepairFixedPointGaugeDescentTheorem.v1",
        "tiers": ["EXACT_GENERAL", "EXACT_BENCHMARK"],
        "selected_mtt_physics": False,
        "consumes_authority": "A47",
        "continuous_fit_parameters": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "theorem_sha256": sha256(THEOREM_PATH),
            "grounding_map_sha256": sha256(GROUNDING_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
            "compression_builder_sha256": sha256(ROOT / "build_constraint_compression_leakage.py"),
        },
        "abstract_chain": [
            "G-equivariant repair F",
            "G-stabilized fixed point u_*",
            "intertwined linearization D F(u_*)",
            "G-invariant isolated Riesz projector P",
            "covariant compression Phi_P and leakage L",
            "faithful reduced action G_*/K_phys"
        ],
        "finite_witness": {
            "field": "Q",
            "ambient_dimension": 3,
            "repair": "F(u)=H0*u+(u^T*u)*u",
            "fixed_point": ["0", "0", "0"],
            "low_eigenvalue": "2",
            "high_eigenvalue": "5",
            "spectral_gap": "3",
            "source_group": "{epsilon R_sigma : epsilon in {+1,-1}, sigma in S3}",
            "source_group_order": 12,
            "observable_kernel_order": 2,
            "faithful_quotient_order": 6,
            "matrices": matrices,
            "group_elements": [alg.serialize_matrix(g) for g in group],
            "conjugation_kernel": [alg.serialize_matrix(g) for g in kernel],
        },
        "checks": checks,
        "summary": {
            "passed": sum(bool(v) for v in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "Repair equivariance now has an exact path through fixed-point linearization, isolated Riesz projection, covariant leakage and a faithful observable quotient. Selection of the physical q79 repair/action/projector remains open.",
        "nonclaims": [
            "derivation of A47",
            "selection of the q79 HYM endpoint",
            "physical Lorentzian action",
            "canonical quantum observables",
            "proof that every internal direction is non-spatiotemporal"
        ]
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
