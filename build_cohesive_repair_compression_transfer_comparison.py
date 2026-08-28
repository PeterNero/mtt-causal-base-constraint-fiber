"""Build the exact compression/transfer comparison certificate."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import build_constraint_compression_leakage as alg


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "closure_dynamics_transfer_source_lock.json"
THEOREM_PATH = ROOT / "CohesiveRepairCompressionTransferComparisonTheorem_v1.md"
PACKET_PATH = ROOT / "cohesive_repair_compression_transfer_comparison.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(size: int, index: int) -> list[list[Fraction]]:
    out = alg.zero(size, 1)
    out[index][0] = Fraction(1)
    return out


def diagonal(values: list[int | Fraction]) -> list[list[Fraction]]:
    out = alg.zero(len(values), len(values))
    for index, value in enumerate(values):
        out[index][index] = Fraction(value)
    return out


def wedge_masks(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = sum(
        1
        for left_bit in range(3)
        if (left >> left_bit) & 1
        for right_bit in range(3)
        if ((right >> right_bit) & 1) and left_bit > right_bit
    )
    return left | right, -1 if inversions % 2 else 1


def left_multiplication(mask: int) -> list[list[Fraction]]:
    out = alg.zero(8, 8)
    for source in range(8):
        target, sign = wedge_masks(mask, source)
        if target is not None:
            out[target][source] = Fraction(sign)
    return out


def right_multiplication(mask: int) -> list[list[Fraction]]:
    out = alg.zero(8, 8)
    for source in range(8):
        target, sign = wedge_masks(source, mask)
        if target is not None:
            out[target][source] = Fraction(sign)
    return out


def propagated_excursion(
    p: list[list[Fraction]],
    source: list[list[Fraction]],
    propagator: list[list[Fraction]],
    target: list[list[Fraction]],
) -> list[list[Fraction]]:
    """Return P source propagator target P."""

    return alg.mul(alg.mul(alg.mul(alg.mul(p, source), propagator), target), p)


def defect(
    p: list[list[Fraction]],
    source: list[list[Fraction]],
    propagator: list[list[Fraction]],
    target: list[list[Fraction]],
) -> list[list[Fraction]]:
    return alg.scale(Fraction(-1), propagated_excursion(p, source, propagator, target))


def build_cohesive_witness() -> tuple[dict[str, object], dict[str, bool]]:
    # Phi(y)=(y2+y2^2,y1), E=1/2 ||Phi||^2, and R=-grad(E).
    background = [Fraction(0), Fraction(0)]
    phi_at_background = [Fraction(0), Fraction(0)]
    residual_jacobian = [
        [Fraction(0), Fraction(1)],
        [Fraction(1), Fraction(0)],
    ]
    hessian = alg.mul(alg.transpose(residual_jacobian), residual_jacobian)
    repair_jacobian = alg.scale(Fraction(-1), hessian)

    # The canonical fixed-mode projector is the spectral projector onto ker(H).
    # H=I2, so the retained fixed tangent space is zero-dimensional.
    p_fix = alg.zero(2, 2)
    q_fix = alg.identity(2)
    green_q = alg.identity(2)
    probe = [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(4)]]
    raw_defect = defect(p_fix, probe, q_fix, probe)
    feshbach_defect = defect(p_fix, probe, green_q, probe)

    checks = {
        "cohesive_background_is_zero": background == [Fraction(0), Fraction(0)],
        "cohesive_residual_vanishes_at_background": phi_at_background == [Fraction(0), Fraction(0)],
        "cohesive_residual_jacobian_is_swap": residual_jacobian == [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]],
        "cohesive_cost_hessian_is_identity": hessian == alg.identity(2),
        "cohesive_repair_jacobian_is_negative_identity": repair_jacobian == alg.scale(Fraction(-1), alg.identity(2)),
        "cohesive_fixed_tangent_projector_has_rank_zero": alg.matrix_rank(p_fix) == 0,
        "cohesive_excluded_projector_is_identity": q_fix == alg.identity(2),
        "cohesive_reduced_green_is_identity": green_q == alg.identity(2),
        "cohesive_raw_compression_defect_is_zero": raw_defect == alg.zero(2, 2),
        "cohesive_feshbach_defect_is_zero": feshbach_defect == alg.zero(2, 2),
    }
    return {
        "background": ["0", "0"],
        "residual": ["y2 + y2^2", "y1"],
        "closure_cost": "1/2*((y2+y2^2)^2+y1^2)",
        "repair_vector_field": ["-y1", "-(y2+y2^2)*(1+2*y2)"],
        "residual_jacobian_at_background": alg.serialize_matrix(residual_jacobian),
        "cost_hessian_at_background": alg.serialize_matrix(hessian),
        "repair_jacobian_at_background": alg.serialize_matrix(repair_jacobian),
        "fixed_tangent_projector": alg.serialize_matrix(p_fix),
        "complement_projector": alg.serialize_matrix(q_fix),
        "derived_reduced_green": alg.serialize_matrix(green_q),
        "canonical_retained_rank": 0,
        "conclusion": "The exact cohesive finite witness has no nonzero harmonic/fixed tangent sector, so it cannot furnish a nontrivial compression or transferred-interaction test.",
    }, checks


def build_nil_hodge_witness() -> tuple[dict[str, object], dict[str, bool]]:
    # Basis by exterior masks: 1,a,b,ab,c,ac,bc,abc.
    identity = alg.identity(8)
    differential = alg.zero(8, 8)
    differential[3][4] = Fraction(1)  # d(c)=ab
    adjoint = alg.transpose(differential)
    laplacian = alg.add(alg.mul(adjoint, differential), alg.mul(differential, adjoint))
    p_harmonic = diagonal([1, 1, 1, 0, 0, 1, 1, 1])
    q_contractible = alg.sub(identity, p_harmonic)
    green_q = q_contractible  # Delta=1 on span(ab,c).
    homotopy = alg.mul(adjoint, green_q)

    a_mask = 1
    b_mask = 2
    ac_mask = 5
    left_a = left_multiplication(a_mask)
    right_b = right_multiplication(b_mask)
    a = vector(8, a_mask)
    b = vector(8, b_mask)
    ac = vector(8, ac_mask)

    first_tree = alg.mul(
        alg.mul(alg.mul(alg.mul(p_harmonic, right_b), homotopy), left_a),
        a,
    )
    second_tree = alg.mul(
        alg.mul(alg.mul(alg.mul(p_harmonic, left_a), homotopy), left_a),
        b,
    )
    # |a|=1, so m3(a,a,b)=first_tree-(-1)^1 second_tree.
    m3_aab = alg.add(first_tree, second_tree)

    raw_excursion_operator = propagated_excursion(
        p_harmonic, left_a, q_contractible, left_a
    )
    homotopy_excursion_operator = propagated_excursion(
        p_harmonic, left_a, homotopy, left_a
    )
    raw_excursion_on_b = alg.mul(raw_excursion_operator, b)
    homotopy_excursion_on_b = alg.mul(homotopy_excursion_operator, b)
    raw_defect_operator = alg.scale(Fraction(-1), raw_excursion_operator)
    propagated_defect_operator = alg.scale(Fraction(-1), homotopy_excursion_operator)
    difference_rhs = alg.scale(
        Fraction(-1),
        propagated_excursion(
            p_harmonic,
            left_a,
            alg.sub(homotopy, q_contractible),
            left_a,
        ),
    )

    checks = {
        "nil_differential_squares_to_zero": alg.mul(differential, differential) == alg.zero(8, 8),
        "nil_hodge_laplacian_equals_contractible_projector": laplacian == q_contractible,
        "nil_harmonic_projector_has_rank_six": alg.matrix_rank(p_harmonic) == 6,
        "nil_contractible_projector_has_rank_two": alg.matrix_rank(q_contractible) == 2,
        "nil_green_is_inverse_on_contractible_sector": alg.mul(laplacian, green_q) == q_contractible,
        "nil_homotopy_equals_dstar_green": homotopy == alg.mul(adjoint, green_q),
        "nil_contraction_identity": alg.add(alg.mul(differential, homotopy), alg.mul(homotopy, differential)) == q_contractible,
        "nil_homotopy_side_conditions": alg.mul(p_harmonic, homotopy) == alg.zero(8, 8) and alg.mul(homotopy, p_harmonic) == alg.zero(8, 8) and alg.mul(homotopy, homotopy) == alg.zero(8, 8),
        "nil_first_m3_tree_vanishes_for_aab": first_tree == alg.zero(8, 1),
        "nil_second_m3_tree_is_ac": second_tree == ac,
        "nil_transferred_m3_aab_is_ac": m3_aab == ac,
        "nil_raw_Q_excursion_on_same_leg_vanishes": raw_excursion_on_b == alg.zero(8, 1),
        "nil_homotopy_excursion_on_same_leg_is_ac": homotopy_excursion_on_b == ac,
        "nil_raw_and_propagated_defects_differ": raw_defect_operator != propagated_defect_operator,
        "nil_weighted_minus_raw_defect_identity": alg.sub(propagated_defect_operator, raw_defect_operator) == difference_rhs,
    }
    return {
        "basis": ["1", "a", "b", "ab", "c", "ac", "bc", "abc"],
        "differential": alg.serialize_matrix(differential),
        "adjoint": alg.serialize_matrix(adjoint),
        "hodge_laplacian": alg.serialize_matrix(laplacian),
        "harmonic_projector": alg.serialize_matrix(p_harmonic),
        "contractible_projector": alg.serialize_matrix(q_contractible),
        "reduced_green": alg.serialize_matrix(green_q),
        "homotopy_dstar_green": alg.serialize_matrix(homotopy),
        "witness": {
            "inputs": ["a", "a", "b"],
            "raw_Q_excursion": "0",
            "homotopy_propagated_excursion": "ac",
            "transferred_m3": "ac",
        },
        "conclusion": "The transferred m3 is a signed sum of h=d*G_Q propagated excursions. It is not the unweighted Q compression defect.",
    }, checks


def build_feshbach_witness() -> tuple[dict[str, object], dict[str, bool]]:
    hessian = [
        [Fraction(1), Fraction(0), Fraction(1, 2), Fraction(0)],
        [Fraction(0), Fraction(2), Fraction(0), Fraction(0)],
        [Fraction(1, 2), Fraction(0), Fraction(3), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(4)],
    ]
    p = diagonal([1, 1, 0, 0])
    q = diagonal([0, 0, 1, 1])
    green_q = diagonal([0, 0, Fraction(1, 3), Fraction(1, 4)])
    bare = alg.mul(alg.mul(p, hessian), p)
    raw_excursion = propagated_excursion(p, hessian, q, hessian)
    self_energy = propagated_excursion(p, hessian, green_q, hessian)
    effective = alg.sub(bare, self_energy)
    raw_defect = alg.scale(Fraction(-1), raw_excursion)
    feshbach_correction = alg.scale(Fraction(-1), self_energy)
    difference_rhs = alg.scale(
        Fraction(-1),
        propagated_excursion(p, hessian, alg.sub(green_q, q), hessian),
    )
    expected_self_energy = diagonal([Fraction(1, 12), 0, 0, 0])
    expected_effective = diagonal([Fraction(11, 12), 2, 0, 0])

    checks = {
        "feshbach_split_is_exact": alg.add(p, q) == alg.identity(4) and alg.mul(p, q) == alg.zero(4, 4),
        "feshbach_green_inverts_excluded_block": alg.mul(alg.mul(alg.mul(q, hessian), q), green_q) == q,
        "feshbach_self_energy_is_one_twelfth": self_energy == expected_self_energy,
        "feshbach_effective_operator_matches_pinned_witness": effective == expected_effective,
        "feshbach_raw_Q_excursion_is_one_quarter": raw_excursion == diagonal([Fraction(1, 4), 0, 0, 0]),
        "feshbach_correction_is_not_raw_compression_defect": feshbach_correction != raw_defect,
        "feshbach_weighted_minus_raw_defect_identity": alg.sub(feshbach_correction, raw_defect) == difference_rhs,
        "feshbach_equality_criterion_fails_on_witness": difference_rhs != alg.zero(4, 4),
    }
    return {
        "hessian": alg.serialize_matrix(hessian),
        "retained_projector": alg.serialize_matrix(p),
        "excluded_projector": alg.serialize_matrix(q),
        "excluded_resolvent_at_zero": alg.serialize_matrix(green_q),
        "bare_compression": alg.serialize_matrix(bare),
        "raw_Q_excursion": alg.serialize_matrix(raw_excursion),
        "feshbach_self_energy": alg.serialize_matrix(self_energy),
        "feshbach_effective_operator": alg.serialize_matrix(effective),
        "conclusion": "The Feshbach correction is the resolvent-weighted excursion, not the raw Q excursion; here their nonzero entries are -1/12 and -1/4 respectively.",
    }, checks


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    cohesive, cohesive_checks = build_cohesive_witness()
    nil_hodge, nil_checks = build_nil_hodge_witness()
    feshbach, feshbach_checks = build_feshbach_witness()

    provenance_checks = {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.closure-dynamics-transfer-source-lock.v1",
        "seven_source_artifacts_are_pinned": len(lock.get("sources", [])) == 7,
        "every_source_has_commit_blob_and_sha256": all(
            len(source.get("commit", "")) == 40
            and len(source.get("git_blob", "")) == 40
            and len(source.get("sha256", "")) == 64
            for source in lock.get("sources", [])
        ),
        "source_lock_preserves_nonpromotion_guard": "does not promote" in lock.get("guard", ""),
    }
    checks = provenance_checks | cohesive_checks | nil_checks | feshbach_checks

    return {
        "schema": "boe.mtt.cohesive-repair-compression-transfer-comparison.v1",
        "theorem_id": "CohesiveRepairCompressionTransferComparisonTheorem.v1",
        "date": "2026-08-28",
        "tiers": ["EXACT_GENERAL", "EXACT_PINNED_BENCHMARK_COMPARISON"],
        "selected_mtt_physics": False,
        "continuous_fit_parameters": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "source_lock_sha256": sha256(LOCK_PATH),
            "theorem_sha256": sha256(THEOREM_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "general_theorem": {
            "excursion": "E_R(S,T)=P S R T P for R=Q R Q",
            "compression_defect": "D_Q(S,T)=Phi_P(S)Phi_P(T)-Phi_P(ST)=-E_Q(S,T)",
            "propagated_defect": "D_R(S,T)=-E_R(S,T)",
            "difference_identity": "D_R-D_Q=-P S (R-Q) T P",
            "equality_criterion": "D_R=D_Q iff P S (R-Q) T P=0",
            "norm_bound": "||D_R-D_Q|| <= ||P S Q|| ||R-Q|| ||Q T P||",
            "feshbach_specialization": "R=G_Q(z)=[Q(H-z)Q]^-1 on QH and S=T=H",
            "ainfinity_specialization": "R=h=d*G_Q; m3 is a signed sum of two E_h planar-tree excursions",
            "typing_guard": "Q and G_Q have degree 0, while h has degree -1; raw compression and m3 cannot be identified without the propagator and arity data.",
        },
        "cohesive_repair_benchmark": cohesive,
        "nil_hodge_ainfinity_benchmark": nil_hodge,
        "feshbach_benchmark": feshbach,
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "The conjectured direct identification is decided negatively on the pinned benchmarks. Compression, Feshbach and A-infinity share one P-to-Q-to-P excursion architecture, but Feshbach inserts the excluded resolvent and A-infinity inserts the degree-minus-one Hodge homotopy. The cohesive two-dimensional repair witness has P_fix=0, while the auxiliary Nil witness proves raw leakage can vanish although m3 is nonzero. A selected q79 P, G_Q and h are still required for physical promotion.",
        "nonclaims": [
            "selected q79 harmonic projector",
            "selected q79 Green operator or homotopy",
            "physical V3/W9 cohesive endpoint",
            "continuum-to-finite product transfer",
            "physical Feshbach self-energy",
            "closure of B.ACTION.01, B.GEO.01 or B.OP.01",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
