"""Independently verify the signed-edge first-jet harmonic quotient packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import factorial
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_signed_edge_first_jet_harmonic_ideal_quotient.packet.json"
LOCK_PATH = ROOT / "q79_signed_edge_first_jet_source_lock.json"
THEOREM_PATH = ROOT / "SignedEdgeFirstJetSelectionAndHarmonicIdealQuotientTheorem_v1.md"
BUILDER_PATH = ROOT / "build_q79_signed_edge_first_jet_harmonic_ideal_quotient.py"
SYMMETRIC_PACKET_PATH = ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
C4_PACKET_PATH = ROOT / "q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json"

Q = Fraction
Matrix = tuple[tuple[Q, ...], ...]
EVEN_MASK = 0b1100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mat(rows: list[list[int | Q]]) -> Matrix:
    return tuple(tuple(Q(value) for value in row) for row in rows)


def eye(size: int) -> Matrix:
    return mat([[1 if row == col else 0 for col in range(size)] for row in range(size)])


def zmat(rows: int, cols: int) -> Matrix:
    return mat([[0 for _ in range(cols)] for _ in range(rows)])


def madd(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(x + y for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def mscale(value: int | Q, source: Matrix) -> Matrix:
    return tuple(tuple(Q(value) * entry for entry in row) for row in source)


def msub(left: Matrix, right: Matrix) -> Matrix:
    return madd(left, mscale(-1, right))


def mmul(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(sum((left[row][index] * right[index][col] for index in range(len(right))), Q(0)) for col in range(len(right[0])))
        for row in range(len(left))
    )


def mt(source: Matrix) -> Matrix:
    return tuple(tuple(source[col][row] for col in range(len(source))) for row in range(len(source[0])))


def mpow(source: Matrix, exponent: int) -> Matrix:
    out = eye(len(source))
    for _ in range(exponent):
        out = mmul(out, source)
    return out


def matrix_rank(source: Matrix) -> int:
    rows = [list(row) for row in source]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        chosen = next((row for row in range(pivot, len(rows)) if rows[row][col] != 0), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        base = rows[pivot][col]
        rows[pivot] = [entry / base for entry in rows[pivot]]
        for row in range(len(rows)):
            if row != pivot and rows[row][col]:
                factor = rows[row][col]
                rows[row] = [entry - factor * base_entry for entry, base_entry in zip(rows[row], rows[pivot])]
        pivot += 1
    return pivot


def pmat(mapping: tuple[int, ...]) -> Matrix:
    rows = [[0 for _ in mapping] for _ in mapping]
    for source, target in enumerate(mapping):
        rows[target][source] = 1
    return mat(rows)


def wedge(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = 0
    for left_index in range(4):
        if left & (1 << left_index):
            for right_index in range(left_index):
                if right & (1 << right_index):
                    inversions += 1
    return left | right, -1 if inversions % 2 else 1


def monomial_action(
    mask: int,
    mapping: tuple[int, ...],
    generator_signs: tuple[int, ...],
) -> tuple[int, int]:
    images = []
    coefficient = 1
    for generator in range(4):
        if mask & (1 << generator):
            images.append(mapping[generator])
            coefficient *= generator_signs[generator]
    coefficient *= -1 if sum(images[i] > images[j] for i in range(len(images)) for j in range(i + 1, len(images))) % 2 else 1
    return sum(1 << image for image in images), coefficient


def independent_checks() -> dict[str, bool]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    symmetric = json.loads(SYMMETRIC_PACKET_PATH.read_text(encoding="utf-8"))
    c4_packet = json.loads(C4_PACKET_PATH.read_text(encoding="utf-8"))
    sources = lock["sources"]
    symmetric_retract = symmetric["selected_complex_retract"]
    harmonic_representations = c4_packet["S3_cochain_and_local_C4_naturality"]["harmonic_representations"]

    checks: dict[str, bool] = {
        "source_lock_schema_is_exact": lock["schema"] == "boe.mtt.q79-signed-edge-first-jet-source-lock.v1",
        "kernel_model_hash_is_pinned": len(lock["kernel_model"]["state_sha256"]) == 64,
        "three_controlling_authorities_are_pinned": [item["id"] for item in lock["controlling_authorities"]] == ["A10", "A18", "A47"],
        "six_sources_are_commit_blob_and_sha256_pinned": len(sources) == 6 and all(len(item["commit"]) == 40 and len(item["git_blob"]) == 40 and len(item["sha256"]) == 64 for item in sources),
        "all_repo_local_source_hashes_match": all(sha256(ROOT / item["path"]) == item["sha256"] for item in sources if item["repository"] == "mtt-causal-base-constraint-fiber"),
        "upstream_symmetric_cohomology_is_1_4_6_4_1": symmetric["normalized_Hodge_theory"]["cohomology_dimensions"] == [1, 4, 6, 4, 1],
        "upstream_selected_H1_is_the_odd_signed_edge_plane": symmetric_retract["selected_H1_basis"] == ["theta_+x-theta_-x", "theta_+z-theta_-z"],
        "upstream_extra_harmonic_dimensions_are_0_2_5_4_1": symmetric_retract["extra_harmonic_dimensions"] == [0, 2, 5, 4, 1],
        "upstream_q79_harmonic_C4_is_the_quarter_turn": harmonic_representations["C4"][1] == "j=[[0,-1],[1,0]]",
        "adjacent_strain_evidence_is_explicitly_non_authoritative_for_this_proof": lock["extracted_claims"]["adjacent_strain_jet_evidence"]["zero_edge_first_jets_vanish"] is True and "not a derivation" in sources[4]["role"],
        "source_guard_keeps_HYM_endpoint_and_continuum_intertwiner_open": "does not select the nonzero-Chern" in lock["guard"] and "does not assert that the finite qutrit translations" in lock["guard"],
    }

    change = mat([[1, 0, 1, 0], [-1, 0, 1, 0], [0, 1, 0, 1], [0, -1, 0, 1]])
    inverse = mat([[Q(1, 2), Q(-1, 2), 0, 0], [0, 0, Q(1, 2), Q(-1, 2)], [Q(1, 2), Q(1, 2), 0, 0], [0, 0, Q(1, 2), Q(1, 2)]])
    signed_metric = mscale(Q(1, 2), eye(4))
    reflection = mmul(mmul(inverse, pmat((1, 0, 3, 2))), change)
    fourier = mmul(mmul(inverse, pmat((2, 3, 1, 0))), change)
    fourier_square = mpow(fourier, 2)
    expected_reflection = mat([[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    expected_fourier = mat([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    odd = mscale(Q(1, 2), msub(eye(4), fourier_square))
    even = mscale(Q(1, 2), madd(eye(4), fourier_square))
    expected_odd = mat([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    expected_even = msub(eye(4), expected_odd)
    principal = mat([[1, 0], [0, 1], [0, 0], [0, 0]])
    axial = mat([[0, 0], [0, 0], [Q(1, 2), 0], [0, Q(1, 2)]])
    checks |= {
        "odd_even_change_of_basis_is_exact": mmul(inverse, change) == eye(4) and mmul(change, inverse) == eye(4),
        "half_edge_metric_makes_odd_even_basis_orthonormal": mmul(mmul(mt(change), signed_metric), change) == eye(4),
        "reflection_is_minus_on_odd_and_plus_on_even": reflection == expected_reflection,
        "Fourier_is_quarter_turn_on_odd_and_swap_on_even": fourier == expected_fourier,
        "Fourier_square_is_the_signed_parity_involution": fourier_square == expected_reflection,
        "odd_projector_is_one_minus_Fourier_square_over_two": odd == expected_odd,
        "even_projector_is_one_plus_Fourier_square_over_two": even == expected_even,
        "odd_even_projectors_are_complementary_orthogonal_idempotents": mpow(odd, 2) == odd and mpow(even, 2) == even and mmul(odd, even) == zmat(4, 4) and madd(odd, even) == eye(4),
        "odd_and_even_projectors_both_have_rank_two": matrix_rank(odd) == matrix_rank(even) == 2,
        "first_order_principal_symbol_has_rank_two_and_lands_exactly_in_odd_plane": matrix_rank(principal) == 2 and mmul(odd, principal) == principal and mmul(even, principal) == zmat(4, 2),
        "axial_second_symbol_lands_exactly_in_even_plane": matrix_rank(axial) == 2 and mmul(even, axial) == axial and mmul(odd, axial) == zmat(4, 2),
        "reflection_odd_eigenspace_has_dimension_two": 4 - matrix_rank(madd(reflection, eye(4))) == 2,
        "the_q79_harmonic_C4_generator_is_recovered_on_the_odd_plane": tuple(tuple(fourier[row][col] for col in range(2)) for row in range(2)) == ((Q(0), Q(-1)), (Q(1), Q(0))),
    }

    terms = []
    exact_split = True
    for derivative_order in range(1, 13):
        plus = Q(1, factorial(derivative_order))
        minus = Q((-1) ** derivative_order, factorial(derivative_order))
        odd_coefficient = (plus - minus) / 2
        even_coefficient = (plus + minus) / 2
        exact_split &= odd_coefficient == (plus if derivative_order % 2 else 0)
        exact_split &= even_coefficient == (plus if derivative_order % 2 == 0 else 0)
        terms.append((derivative_order, derivative_order - 1, odd_coefficient, even_coefficient))
    checks |= {
        "signed_exponential_series_splits_exactly_by_derivative_parity": exact_split,
        "odd_channel_starts_with_nabla_at_h_power_zero": terms[0][1:] == (0, Q(1), Q(0)),
        "even_channel_has_no_principal_first_jet": terms[0][3] == 0,
        "even_channel_starts_with_h_nabla_squared_over_two": terms[1][1:] == (1, Q(0), Q(1, 2)),
        "odd_first_correction_is_h_squared_nabla_cubed_over_six": terms[2][1:] == (2, Q(1, 6), Q(0)),
        "all_odd_derivatives_land_only_in_odd_plane_through_order_twelve": all(even_coefficient == 0 for order, _, _, even_coefficient in terms if order % 2),
        "all_even_derivatives_land_only_in_even_plane_through_order_twelve": all(odd_coefficient == 0 for order, _, odd_coefficient, _ in terms if order % 2 == 0),
    }

    masks = tuple(range(16))
    ideal = tuple(mask for mask in masks if mask & EVEN_MASK)
    quotient = tuple(mask for mask in masks if not mask & EVEN_MASK)
    full_dims = [sum(mask.bit_count() == degree for mask in masks) for degree in range(5)]
    ideal_dims = [sum(mask.bit_count() == degree for mask in ideal) for degree in range(5)]
    quotient_dims = [sum(mask.bit_count() == degree for mask in quotient) for degree in range(5)]
    ideal_generated = all(any(mask & (1 << generator) and wedge(1 << generator, mask ^ (1 << generator))[0] == mask for generator in (2, 3)) for mask in ideal)
    ideal_closed = quotient_map = valuation_additive = True
    for left in masks:
        for right in masks:
            target, _ = wedge(left, right)
            if left in ideal and target is not None:
                ideal_closed &= target in ideal
            quotient_product = None
            if left not in ideal and right not in ideal:
                quotient_product, _ = wedge(left, right)
            projected = None if target is None or target in ideal else target
            quotient_map &= quotient_product == projected
            if target is not None:
                valuation_additive &= (target & EVEN_MASK).bit_count() == (left & EVEN_MASK).bit_count() + (right & EVEN_MASK).bit_count()
    associative = True
    for left in quotient:
        for middle in quotient:
            for right in quotient:
                lm, s1 = wedge(left, middle)
                mr, s2 = wedge(middle, right)
                lt, s3 = (None, 0) if lm is None else wedge(lm, right)
                rt, s4 = (None, 0) if mr is None else wedge(left, mr)
                associative &= lt == rt and s1 * s3 == s2 * s4
    symmetry_stable = valuation_stable = True
    actions = (((1, 0, 3, 2), (1, -1, 1, 1)), ((0, 1, 2, 3), (-1, -1, 1, 1)))
    for mask in masks:
        for mapping, signs in actions:
            target, _ = monomial_action(mask, mapping, signs)
            symmetry_stable &= (mask in ideal) == (target in ideal)
            valuation_stable &= (mask & EVEN_MASK).bit_count() == (target & EVEN_MASK).bit_count()
    even_fourier = mat([[0, 1], [1, 0]])
    scalar = mat([[1], [1]])
    traceless = mat([[1], [-1]])
    checks |= {
        "symmetric_harmonic_exterior_algebra_has_sixteen_basis_classes": len(masks) == 16,
        "even_generated_ideal_has_exactly_twelve_basis_classes": len(ideal) == 12,
        "ideal_dimensions_are_0_2_5_4_1": ideal_dims == [0, 2, 5, 4, 1],
        "quotient_dimensions_are_1_2_1_0_0": quotient_dims == [1, 2, 1, 0, 0],
        "full_dimensions_are_1_4_6_4_1": full_dims == [1, 4, 6, 4, 1],
        "all_extra_classes_are_generated_by_the_even_plane": ideal_generated,
        "even_generated_subspace_is_a_two_sided_graded_ideal": ideal_closed,
        "harmonic_quotient_map_is_multiplicative_on_all_256_basis_pairs": quotient_map,
        "four_class_odd_quotient_product_is_associative_on_all_64_basis_triples": associative,
        "ideal_and_quotient_are_reflection_and_C4_stable": symmetry_stable,
        "Rees_even_count_is_additive_under_every_nonzero_wedge_product": valuation_additive,
        "Rees_even_count_is_preserved_by_reflection_and_C4": valuation_stable,
        "Rees_special_fiber_kernel_is_exactly_the_twelve_class_ideal": set(ideal) == {mask for mask in masks if (mask & EVEN_MASK).bit_count() > 0},
        "even_scalar_and_axial_channels_have_Fourier_eigenvalues_plus_and_minus_one": mmul(even_fourier, scalar) == scalar and mmul(even_fourier, traceless) == mscale(-1, traceless),
    }
    return checks


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    checks = independent_checks()
    assert packet["schema"] == "boe.mtt.q79-signed-edge-first-jet-harmonic-ideal-quotient.v1"
    assert packet["source_hashes"] == {
        "source_lock_sha256": sha256(LOCK_PATH),
        "theorem_sha256": sha256(THEOREM_PATH),
        "builder_sha256": sha256(BUILDER_PATH),
    }
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"passed": len(checks), "total": len(checks), "all_passed": True}
    assert packet["orientation_odd_plane_is_unique_principal_first_jet"] is True
    assert packet["twelve_extra_harmonic_classes_form_even_generated_ideal"] is True
    assert packet["selected_harmonic_algebra_is_strict_quotient"] is True
    assert packet["selected_finite_to_continuum_intertwiner"] is False
    assert packet["selected_nonzero_Chern_HYM_endpoint"] is False
    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} independent exact checks")


if __name__ == "__main__":
    main()
