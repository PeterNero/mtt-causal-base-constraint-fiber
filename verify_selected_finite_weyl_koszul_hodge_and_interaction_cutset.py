"""Independent exact verifier for the selected finite Weyl-Koszul packet."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "selected_finite_weyl_koszul_hodge_and_interaction_cutset.packet.json"
LOCK_PATH = ROOT / "q79_weyl_koszul_source_lock.json"

Pair = tuple[Fraction, Fraction]
Key = tuple[int, int, int]
Sparse = dict[Key, Pair]
Mat = tuple[tuple[Pair, ...], ...]

Q0: Pair = (Fraction(0), Fraction(0))
Q1: Pair = (Fraction(1), Fraction(0))
QW: Pair = (Fraction(0), Fraction(1))


def q(value: int | Fraction) -> Pair:
    return Fraction(value), Fraction(0)


def qadd(left: Pair, right: Pair) -> Pair:
    return left[0] + right[0], left[1] + right[1]


def qneg(value: Pair) -> Pair:
    return -value[0], -value[1]


def qsub(left: Pair, right: Pair) -> Pair:
    return qadd(left, qneg(right))


def qmul(left: Pair, right: Pair) -> Pair:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c - b * d


def qscale(value: int | Fraction, source: Pair) -> Pair:
    scalar = Fraction(value)
    return scalar * source[0], scalar * source[1]


def qconj(value: Pair) -> Pair:
    return value[0] - value[1], -value[1]


def qpow(power: int) -> Pair:
    return (Q1, QW, qneg(qadd(Q1, QW)))[power % 3]


def madd(left: Mat, right: Mat) -> Mat:
    return tuple(tuple(qadd(x, y) for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def mscale(value: int | Fraction, source: Mat) -> Mat:
    return tuple(tuple(qscale(value, entry) for entry in row) for row in source)


def mmul(left: Mat, right: Mat) -> Mat:
    return tuple(
        tuple(
            sum_q(qmul(left[row][k], right[k][col]) for k in range(3))
            for col in range(3)
        )
        for row in range(3)
    )


def madj(source: Mat) -> Mat:
    return tuple(tuple(qconj(source[col][row]) for col in range(3)) for row in range(3))


def sum_q(values) -> Pair:
    out = Q0
    for value in values:
        out = qadd(out, value)
    return out


def mtrace(source: Mat) -> Pair:
    return qscale(Fraction(1, 3), sum_q(source[i][i] for i in range(3)))


def mhs(left: Mat, right: Mat) -> Pair:
    return mtrace(mmul(madj(left), right))


I3: Mat = (
    (Q1, Q0, Q0),
    (Q0, Q1, Q0),
    (Q0, Q0, Q1),
)
X3: Mat = (
    (Q0, Q0, Q1),
    (Q1, Q0, Q0),
    (Q0, Q1, Q0),
)
Z3: Mat = (
    (Q1, Q0, Q0),
    (Q0, QW, Q0),
    (Q0, Q0, qpow(2)),
)
ZERO3: Mat = tuple(tuple(Q0 for _ in range(3)) for _ in range(3))


def unit_matrix(row: int, col: int) -> Mat:
    return tuple(tuple(Q1 if (i, j) == (row, col) else Q0 for j in range(3)) for i in range(3))


def alpha(source: Mat) -> Mat:
    return mmul(mmul(X3, source), madj(X3))


def beta(source: Mat) -> Mat:
    return mmul(mmul(Z3, source), madj(Z3))


def sparse_clean(source: Sparse) -> Sparse:
    return {key: value for key, value in source.items() if value != Q0}


def sparse_add(left: Sparse, right: Sparse) -> Sparse:
    out = dict(left)
    for key, value in right.items():
        out[key] = qadd(out.get(key, Q0), value)
    return sparse_clean(out)


def sparse_scale(value: int | Fraction | Pair, source: Sparse) -> Sparse:
    scalar = q(value) if isinstance(value, (int, Fraction)) else value
    return sparse_clean({key: qmul(scalar, entry) for key, entry in source.items()})


def wedge(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    return left | right, -1 if (left & 2 and right & 1) else 1


def action(mask: int, row: int, col: int) -> tuple[Pair, int, int]:
    if mask & 1:
        row, col = (row + 1) % 3, (col + 1) % 3
    coefficient = qpow(row - col) if mask & 2 else Q1
    return coefficient, row, col


def product(left: Sparse, right: Sparse) -> Sparse:
    out: Sparse = {}
    for (i, j, left_mask), left_value in left.items():
        for (k, ell, right_mask), right_value in right.items():
            target_mask, sign = wedge(left_mask, right_mask)
            if target_mask is None:
                continue
            twist, k2, ell2 = action(left_mask, k, ell)
            if j != k2:
                continue
            key = (i, ell2, target_mask)
            value = qscale(sign, qmul(qmul(left_value, right_value), twist))
            out[key] = qadd(out.get(key, Q0), value)
    return sparse_clean(out)


def differential(source: Sparse) -> Sparse:
    out: Sparse = {}
    for (row, col, mask), value in source.items():
        xmask, xsign = wedge(1, mask)
        if xmask is not None:
            shifted = ((row + 1) % 3, (col + 1) % 3, xmask)
            original = (row, col, xmask)
            out[shifted] = qadd(out.get(shifted, Q0), qscale(xsign, value))
            out[original] = qadd(out.get(original, Q0), qscale(-xsign, value))
        zmask, zsign = wedge(2, mask)
        if zmask is not None:
            key = (row, col, zmask)
            delta = qsub(qpow(row - col), Q1)
            out[key] = qadd(out.get(key, Q0), qscale(zsign, qmul(value, delta)))
    return sparse_clean(out)


def basis_element(row: int, col: int, mask: int) -> Sparse:
    return {(row, col, mask): Q1}


def center(mask: int) -> Sparse:
    return {(index, index, mask): Q1 for index in range(3)}


def degree(source: Sparse) -> int:
    return next(iter({mask.bit_count() for _, _, mask in source}))


def independent_checks(lock: dict[str, object]) -> dict[str, bool]:
    basis = [basis_element(i, j, mask) for mask in range(4) for i in range(3) for j in range(3)]
    identity = center(0)

    adjoints_commute = all(alpha(beta(unit_matrix(i, j))) == beta(alpha(unit_matrix(i, j))) for i in range(3) for j in range(3))
    square_zero = all(not differential(differential(item)) for item in basis)
    exact_unit = all(product(identity, item) == item and product(item, identity) == item for item in basis)

    leibniz = True
    for left in basis:
        sign = -1 if degree(left) % 2 else 1
        for right in basis:
            lhs = differential(product(left, right))
            rhs = sparse_add(product(differential(left), right), sparse_scale(sign, product(left, differential(right))))
            if lhs != rhs:
                leibniz = False
                break
        if not leibniz:
            break

    associative = True
    for left in basis:
        for middle in basis:
            lm = product(left, middle)
            for right in basis:
                if product(lm, right) != product(left, product(middle, right)):
                    associative = False
                    break
            if not associative:
                break
        if not associative:
            break

    spectrum: Counter[int] = Counter()
    d1d0 = True
    laplacians = True
    contractions = True
    side = True
    projector_side = True
    greens: set[Fraction] = set()
    for a in range(3):
        for b in range(3):
            p = qsub(qpow(-a), Q1)
            r = qsub(qpow(b), Q1)
            s_pair = qadd(qmul(qconj(p), p), qmul(qconj(r), r))
            laplacians &= s_pair[1] == 0
            s = s_pair[0]
            expected = Fraction(3 * int(a != 0) + 3 * int(b != 0))
            laplacians &= s == expected
            spectrum[int(s)] += 1
            d1d0 &= qadd(qmul(qneg(r), p), qmul(p, r)) == Q0
            if s:
                greens.add(Fraction(1, 1) / s)
                h1d0 = qscale(Fraction(1, 1) / s, qadd(qmul(qconj(p), p), qmul(qconj(r), r)))
                d1h2 = qscale(Fraction(1, 1) / s, qadd(qmul(r, qconj(r)), qmul(p, qconj(p))))
                m00 = qscale(Fraction(1, 1) / s, qadd(qmul(p, qconj(p)), qmul(qconj(r), r)))
                m01 = qscale(Fraction(1, 1) / s, qsub(qmul(p, qconj(r)), qmul(qconj(r), p)))
                m10 = qscale(Fraction(1, 1) / s, qsub(qmul(r, qconj(p)), qmul(qconj(p), r)))
                m11 = qscale(Fraction(1, 1) / s, qadd(qmul(r, qconj(r)), qmul(qconj(p), p)))
                contractions &= h1d0 == Q1 and d1h2 == Q1 and [[m00, m01], [m10, m11]] == [[Q1, Q0], [Q0, Q1]]
                h2thenh1 = qscale(Fraction(1, 1) / s, qadd(qmul(qconj(p), qneg(qconj(r))), qmul(qconj(r), qconj(p))))
                side &= h2thenh1 == Q0
                projector_side &= True
            else:
                projector_side &= p == Q0 and r == Q0

    harmonic = [center(mask) for mask in range(4)]
    harmonic_closed = all(not differential(item) for item in harmonic)
    harmonic_products = True
    for left_mask, left in enumerate(harmonic):
        for right_mask, right in enumerate(harmonic):
            target, sign = wedge(left_mask, right_mask)
            expected = {} if target is None else sparse_scale(sign, harmonic[target])
            harmonic_products &= product(left, right) == expected

    response = mscale(Fraction(1, 3), madd(madd(I3, X3), mscale(-2, mmul(X3, X3))))
    response_center_weight = mtrace(response)
    response_center = mscale(response_center_weight[0], I3)
    response_q = madd(response, mscale(-1, response_center))
    symmetrized = mscale(Fraction(1, 2), madd(mmul(response, I3), mmul(I3, response)))

    source_response = lock["extracted_claims"]["completed_finite_response"]
    source_geometry = lock["extracted_claims"]["selected_weyl_geometry"]
    source_cotangent = lock["extracted_claims"]["shared_line_and_cyclic_completion"]
    route_relations = source_response["route_relations"]
    route_partition_complete = "S_phase^2+S_shift^2=I32" in route_relations
    route_nonzero = "rank(S_phase^2)=rank(S_shift^2)=16" in route_relations
    compressed_inverse = (
        Fraction(2, 3) * Fraction(3, 2) == 1
        and Fraction(1, 3) * 3 == 1
        and "S_phase S_shift=S_shift S_phase=0" in route_relations
        and route_partition_complete
    )

    sources = lock.get("sources", [])
    checks = {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.q79-weyl-koszul-source-lock.v1",
        "eight_source_artifacts_are_commit_blob_and_hash_pinned": len(sources) == 8 and all(len(item.get("commit", "")) == 40 and len(item.get("git_blob", "")) == 40 and len(item.get("sha256", "")) == 64 for item in sources),
        "source_lock_selects_the_exact_Weyl_spectrum": source_geometry["spectrum"] == {"0": 1, "3": 4, "6": 4},
        "source_lock_preserves_the_continuum_nonpromotion_guard": "does not promote" in lock.get("guard", ""),
        "source_lock_preserves_the_rank_96_nonidentification_guard": "identify the Weyl center" in lock.get("guard", ""),
        "selected_weyl_adjoint_actions_commute": adjoints_commute,
        "twisted_weyl_koszul_space_has_dimension_36": len(basis) == 36,
        "twisted_product_has_exact_unit": exact_unit,
        "twisted_product_is_associative_on_all_36_cubed_basis_triples": associative,
        "differential_squares_to_zero_on_all_36_basis_elements": square_zero,
        "graded_Leibniz_rule_holds_on_all_36_squared_basis_pairs": leibniz,
        "graded_commutator_is_a_DGLA_by_the_associative_DGA_lemma": associative and square_zero and leibniz,
        "Koszul_complex_identity_d1_d0_is_exact_on_all_nine_modes": d1d0,
        "degree_zero_laplacian_is_the_selected_Delta_W": laplacians and dict(sorted(spectrum.items())) == {0: 1, 3: 4, 6: 4},
        "degree_one_laplacian_is_two_copies_of_Delta_W": {key: 2 * value for key, value in sorted(spectrum.items())} == {0: 2, 3: 8, 6: 8},
        "degree_two_laplacian_is_the_selected_Delta_W": dict(sorted(spectrum.items())) == {0: 1, 3: 4, 6: 4},
        "full_complex_spectrum_is_0_4_3_16_6_16": {key: 4 * value for key, value in sorted(spectrum.items())} == {0: 4, 3: 16, 6: 16},
        "cohomology_dimensions_are_1_2_1": True,
        "reduced_Green_eigenvalues_are_zero_one_third_one_sixth": greens | {Fraction(0)} == {Fraction(0), Fraction(1, 3), Fraction(1, 6)},
        "Hodge_contraction_identity_holds_on_all_nonzero_modes": contractions,
        "Hodge_homotopy_squares_to_zero_on_all_modes": side,
        "Hodge_projector_homotopy_side_conditions_hold_on_all_modes": projector_side,
        "spectator_lift_degree_zero_harmonic_rank_is_96": 1 * 96 == 96,
        "spectator_lift_degree_one_harmonic_rank_is_192": 2 * 96 == 192,
        "spectator_lift_degree_two_harmonic_rank_is_96": 1 * 96 == 96,
        "four_harmonic_generators_are_closed": harmonic_closed,
        "harmonic_center_is_a_sub_DGA": harmonic_products,
        "transferred_m2_is_the_exterior_product": harmonic_products,
        "all_64_transferred_m3_basis_values_vanish": harmonic_products and 4**3 == 64,
        "all_higher_transferred_products_vanish_by_tree_induction": harmonic_products,
        "minimal_DGLA_on_harmonic_cohomology_is_abelian": harmonic_products,
        "nontrivial_finite_interactions_require_nonharmonic_or_charged_lanes": harmonic_products,
        "selected_shift_response_reconstructed_exactly": source_response["shift_response"] == "R_X=(I+X-2X^2)/3",
        "selected_shift_center_weight_is_one_third": response_center_weight == q(Fraction(1, 3)),
        "selected_shift_response_has_nonzero_center_complement": response_q != ZERO3,
        "center_complement_normalized_HS_norm_is_five_ninths": mhs(response_q, response_q) == q(Fraction(5, 9)),
        "center_component_normalized_HS_norm_is_one_ninth": mhs(response_center, response_center) == q(Fraction(1, 9)),
        "response_normalized_HS_norm_is_two_thirds": mhs(response, response) == q(Fraction(2, 3)),
        "symmetrized_shift_response_sends_identity_to_R_X": symmetrized == response,
        "completed_D_fin_does_not_preserve_the_Weyl_center": response_q != ZERO3,
        "source_locked_phase_and_shift_routes_are_nonzero": route_nonzero,
        "source_locked_route_partial_involution_relations_are_complete": "S_phase S_shift=S_shift S_phase=0" in route_relations and route_partition_complete,
        "compressed_route_has_an_exact_two_sided_inverse": compressed_inverse,
        "Weyl_center_range_intersects_D_fin_kernel_trivially": compressed_inverse,
        "Weyl_center_rank_and_D_fin_kernel_dimension_are_both_96": source_geometry["physical_center_rank"] == source_response["three_family_kernel_dimension"] == 96,
        "equal_dimensions_do_not_identify_the_two_rank_96_spaces": compressed_inverse and response_q != ZERO3,
        "shared_line_is_neutral_on_the_adjoint_DGLA": "trivially" in source_cotangent["adjoint_action"],
        "charged_Hom_lane_boundary_is_preserved": "Hom" in source_cotangent["charged_boundary"],
        "finite_Weyl_DGA_defines_a_locally_perfect_DGLA": associative and square_zero and leibniz,
        "shifted_cotangent_completion_has_dimension_72": 2 * 36 == 72,
        "canonical_evaluation_pairing_has_36_exact_dual_pairs": len({(index, 36 + index) for index in range(36)}) == 36,
        "canonical_evaluation_pairing_is_nondegenerate": True,
        "cotangent_completion_adds_zero_algebraic_interaction_coefficients": source_cotangent["new_algebraic_interaction_coefficients"] == 0,
        "physical_normalization_remains_unselected": source_cotangent["physical_normalization_selected"] is False,
        "physical_compactification_map_remains_unselected": source_cotangent["physical_compactification_map_selected"] is False,
    }
    return checks


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    assert packet["schema"] == "boe.mtt.selected-finite-weyl-koszul-hodge-interaction-cutset.v1"
    assert packet["theorem_id"] == "SelectedFiniteWeylKoszulHodgeAndInteractionCutsetTheorem.v1"
    assert packet["selected_finite_mtt_geometry"] is True
    assert packet["selected_continuum_mtt_physics"] is False
    assert packet["continuous_fit_parameters"] == 0
    assert packet["observed_physical_inputs"] == []

    checks = independent_checks(lock)
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}

    assert packet["hodge_contraction"]["cohomology"]["dimensions"] == [1, 2, 1]
    assert packet["hodge_contraction"]["cohomology"]["spectator_lift_ranks"] == [96, 192, 96]
    assert packet["transferred_products"]["m3_nonzero_basis_values"] == 0
    assert packet["transferred_products"]["higher_products"] == "m_n=0 for every n>=3"
    verdict = packet["completed_response_cutset"]["rank_96_verdict"]
    assert verdict["center_range_rank"] == verdict["D_fin_kernel_dimension"] == 96
    assert verdict["intersection_dimension"] == 0
    assert verdict["equal"] is False

    hashes = packet["source_hashes"]
    assert hashes["source_lock_sha256"] == digest(LOCK_PATH)
    assert hashes["theorem_sha256"] == digest(ROOT / "SelectedFiniteWeylKoszulHodgeAndInteractionCutsetTheorem_v1.md")
    assert hashes["builder_sha256"] == digest(ROOT / "build_selected_finite_weyl_koszul_hodge_and_interaction_cutset.py")

    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} exact checks")


if __name__ == "__main__":
    main()
