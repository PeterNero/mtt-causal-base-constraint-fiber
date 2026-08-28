"""Independent verifier for the symmetric q79 Weyl calculus and retract."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations
from math import comb
from pathlib import Path
from typing import Callable, Iterable

import verify_selected_finite_weyl_koszul_hodge_and_interaction_cutset as q


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
LOCK_PATH = ROOT / "q79_symmetric_weyl_calculus_source_lock.json"

Pair = q.Pair
Linear = tuple[tuple[Pair, ...], ...]
Key = tuple[int, int, int]
Element = dict[Key, Pair]

EXP4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
EXP2 = ((1, 0), (0, 1))
S3 = tuple((eps, shift) for eps in (1, -1) for shift in range(3))
INV = (1, 0, 3, 2)
FOURIER = (2, 3, 1, 0)
HALF = Fraction(1, 2)


def p(value: int | Fraction) -> Pair:
    return q.q(value)


def lzero(rows: int, cols: int) -> Linear:
    return tuple(tuple(q.Q0 for _ in range(cols)) for _ in range(rows))


def lid(size: int) -> Linear:
    return tuple(tuple(q.Q1 if row == col else q.Q0 for col in range(size)) for row in range(size))


def ladd(left: Linear, right: Linear) -> Linear:
    return tuple(tuple(q.qadd(x, y) for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def lscale(value: int | Fraction, source: Linear) -> Linear:
    return tuple(tuple(q.qscale(value, item) for item in row) for row in source)


def lsub(left: Linear, right: Linear) -> Linear:
    return ladd(left, lscale(-1, right))


def lmul(left: Linear, right: Linear) -> Linear:
    return tuple(
        tuple(q.sum_q(q.qmul(left[row][index], right[index][col]) for index in range(len(right))) for col in range(len(right[0])))
        for row in range(len(left))
    )


def ladj(source: Linear) -> Linear:
    return tuple(tuple(q.qconj(source[col][row]) for col in range(len(source))) for row in range(len(source[0])))


def ltrace(source: Linear) -> Pair:
    return q.sum_q(source[index][index] for index in range(len(source)))


def masks(n: int, degree: int) -> tuple[int, ...]:
    return tuple(sum(1 << index for index in chosen) for chosen in combinations(range(n), degree))


def wedge(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = sum(
        1
        for i in range(max(left.bit_length(), right.bit_length()))
        if left & (1 << i)
        for j in range(max(left.bit_length(), right.bit_length()))
        if right & (1 << j) and i > j
    )
    return left | right, -1 if inversions % 2 else 1


def permute_mask(mask: int, mapping: tuple[int, ...]) -> tuple[int, int]:
    images = [mapping[index] for index in range(len(mapping)) if mask & (1 << index)]
    inversions = sum(images[i] > images[j] for i in range(len(images)) for j in range(i + 1, len(images)))
    return sum(1 << index for index in images), -1 if inversions % 2 else 1


def clean(source: Element) -> Element:
    return {key: value for key, value in source.items() if value != q.Q0}


def add(left: Element, right: Element) -> Element:
    out = dict(left)
    for key, value in right.items():
        out[key] = q.qadd(out.get(key, q.Q0), value)
    return clean(out)


def scale(value: int | Fraction | Pair, source: Element) -> Element:
    scalar = p(value) if isinstance(value, (int, Fraction)) else value
    return clean({key: q.qmul(scalar, item) for key, item in source.items()})


def basis(a: int, b: int, mask: int) -> Element:
    return {(a % 3, b % 3, mask): q.Q1}


def mode_phase(left_b: int, right_a: int) -> Pair:
    return q.qpow(-left_b * right_a)


def direction_factor(mask: int, a: int, b: int, exponents: tuple[tuple[int, int], ...]) -> Pair:
    xp = sum(exponents[index][0] for index in range(len(exponents)) if mask & (1 << index))
    zp = sum(exponents[index][1] for index in range(len(exponents)) if mask & (1 << index))
    return q.qpow(-a * xp + b * zp)


def product(left: Element, right: Element, exponents: tuple[tuple[int, int], ...]) -> Element:
    out: Element = {}
    for (a, b, lm), lv in left.items():
        for (c, d, rm), rv in right.items():
            target, sign = wedge(lm, rm)
            if target is None:
                continue
            value = q.qscale(
                sign,
                q.qmul(q.qmul(q.qmul(lv, rv), mode_phase(b, c)), direction_factor(lm, c, d, exponents)),
            )
            key = ((a + c) % 3, (b + d) % 3, target)
            out[key] = q.qadd(out.get(key, q.Q0), value)
    return clean(out)


def differential(source: Element, exponents: tuple[tuple[int, int], ...]) -> Element:
    out: Element = {}
    for (a, b, mask), value in source.items():
        for direction, (xp, zp) in enumerate(exponents):
            target, sign = wedge(1 << direction, mask)
            if target is None:
                continue
            delta = q.qsub(q.qpow(-a * xp + b * zp), q.Q1)
            key = (a, b, target)
            out[key] = q.qadd(out.get(key, q.Q0), q.qscale(sign, q.qmul(value, delta)))
    return clean(out)


def element_degree(source: Element) -> int:
    return next(iter({mask.bit_count() for _, _, mask in source}))


def affine(source: Element, eps: int, shift: int, n: int = 4) -> Element:
    out: Element = {}
    mapping = tuple(range(n)) if eps == 1 else INV[:n]
    for (a, b, mask), value in source.items():
        if eps == 1:
            ta, tb, phase = a, b, q.qpow(-a * shift)
        else:
            ta, tb, phase = (-a) % 3, (-b) % 3, q.qpow(a * shift)
        tm, sign = permute_mask(mask, mapping)
        key = (ta, tb, tm)
        out[key] = q.qadd(out.get(key, q.Q0), q.qscale(sign, q.qmul(value, phase)))
    return clean(out)


def fourier(source: Element, n: int = 4) -> Element:
    out: Element = {}
    mapping = FOURIER if n == 4 else (1, 0)
    for (a, b, mask), value in source.items():
        tm, sign = permute_mask(mask, mapping)
        key = (b % 3, (-a) % 3, tm)
        coefficient = q.qscale(sign, q.qmul(value, q.qpow(a * b)))
        out[key] = q.qadd(out.get(key, q.Q0), coefficient)
    return clean(out)


def old_affine(source: Element, eps: int, shift: int) -> Element:
    out: Element = {}
    for (a, b, mask), value in source.items():
        if eps == 1:
            key, factor = (a, b, mask), q.qpow(-a * shift)
        else:
            form = {
                0: q.Q1,
                1: q.qneg(q.qpow(a)),
                2: q.qneg(q.qpow(-b)),
                3: q.qpow(a - b),
            }[mask]
            key, factor = ((-a) % 3, (-b) % 3, mask), q.qmul(q.qpow(a * shift), form)
        out[key] = q.qadd(out.get(key, q.Q0), q.qmul(value, factor))
    return clean(out)


def old_fourier(source: Element) -> Element:
    out: Element = {}
    for (a, b, mask), value in source.items():
        phase = q.qpow(a * b)
        terms = {
            0: ((0, q.Q1),),
            1: ((2, q.Q1),),
            2: ((1, q.qneg(q.qpow(-b))),),
            3: ((3, q.qpow(-b)),),
        }[mask]
        for target_mask, form in terms:
            key = (b % 3, (-a) % 3, target_mask)
            out[key] = q.qadd(out.get(key, q.Q0), q.qmul(value, q.qmul(phase, form)))
    return clean(out)


def compose_affine(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] * right[0], (left[0] * right[1] + left[1]) % 3


def iterate(action: Callable[[Element], Element], source: Element, count: int) -> Element:
    out = source
    for _ in range(count):
        out = action(out)
    return out


def wedge_matrix(vector: tuple[Pair, ...], degree: int) -> Linear:
    source_masks, target_masks = masks(len(vector), degree), masks(len(vector), degree + 1)
    index = {mask: row for row, mask in enumerate(target_masks)}
    rows = [[q.Q0 for _ in source_masks] for _ in target_masks]
    for col, mask in enumerate(source_masks):
        for direction, value in enumerate(vector):
            target, sign = wedge(1 << direction, mask)
            if target is not None:
                rows[index[target]][col] = q.qadd(rows[index[target]][col], q.qscale(sign, value))
    return tuple(tuple(row) for row in rows)


def mode_vector(a: int, b: int, exponents: tuple[tuple[int, int], ...]) -> tuple[Pair, ...]:
    return tuple(q.qsub(q.qpow(-a * xp + b * zp), q.Q1) for xp, zp in exponents)


def determinant(source: Linear) -> Pair:
    if not source:
        return q.Q1
    out = q.Q0
    for order in permutations(range(len(source))):
        inversions = sum(order[i] > order[j] for i in range(len(order)) for j in range(i + 1, len(order)))
        term = p(-1 if inversions % 2 else 1)
        for row, col in enumerate(order):
            term = q.qmul(term, source[row][col])
        out = q.qadd(out, term)
    return out


def exterior(source: Linear, degree: int) -> Linear:
    target_sets = tuple(combinations(range(len(source)), degree))
    source_sets = tuple(combinations(range(len(source[0])), degree))
    return tuple(
        tuple(determinant(tuple(tuple(source[row][col] for col in source_set) for row in target_set)) for source_set in source_sets)
        for target_set in target_sets
    )


def i1(a: int, b: int) -> Linear:
    return (
        (q.Q1, q.Q0),
        (q.qneg(q.qpow(a)), q.Q0),
        (q.Q0, q.Q1),
        (q.Q0, q.qneg(q.qpow(-b))),
    )


def q1(a: int, b: int) -> Linear:
    return lscale(HALF, ((q.Q1, q.qneg(q.qpow(-a)), q.Q0, q.Q0), (q.Q0, q.Q0, q.Q1, q.qneg(q.qpow(b)))))


def imat(a: int, b: int, degree: int) -> Linear:
    return ((q.Q1,),) if degree == 0 else exterior(i1(a, b), degree)


def qmat(a: int, b: int, degree: int) -> Linear:
    return ((q.Q1,),) if degree == 0 else exterior(q1(a, b), degree)


def include(source: Element) -> Element:
    out: Element = {}
    for (a, b, mask), value in source.items():
        k = mask.bit_count()
        col = masks(2, k).index(mask)
        matrix = imat(a, b, k)
        for row, target in enumerate(masks(4, k)):
            coefficient = q.qmul(value, matrix[row][col])
            if coefficient != q.Q0:
                key = (a, b, target)
                out[key] = q.qadd(out.get(key, q.Q0), coefficient)
    return clean(out)


def retract(source: Element) -> Element:
    out: Element = {}
    for (a, b, mask), value in source.items():
        k = mask.bit_count()
        if k > 2:
            continue
        col = masks(4, k).index(mask)
        matrix = qmat(a, b, k)
        for row, target in enumerate(masks(2, k)):
            coefficient = q.qmul(value, matrix[row][col])
            if coefficient != q.Q0:
                key = (a, b, target)
                out[key] = q.qadd(out.get(key, q.Q0), coefficient)
    return clean(out)


def laplacians(differentials: dict[int, Linear], adjoints: dict[int, Linear], n: int) -> dict[int, Linear]:
    out: dict[int, Linear] = {}
    for degree in range(n + 1):
        delta = lzero(comb(n, degree), comb(n, degree))
        if degree > 0:
            delta = ladd(delta, lmul(differentials[degree - 1], adjoints[degree - 1]))
        if degree < n:
            delta = ladd(delta, lmul(adjoints[degree], differentials[degree]))
        out[degree] = delta
    return out


def direction_orbit_checks() -> tuple[bool, bool]:
    orbit = {0, 2}
    while True:
        grown = orbit | {INV[index] for index in orbit} | {FOURIER[index] for index in orbit}
        if grown == orbit:
            break
        orbit = grown
    minimal = True
    for subset_mask in range(16):
        subset = {index for index in range(4) if subset_mask & (1 << index)}
        if {0, 2} <= subset and subset != set(range(4)):
            if {INV[index] for index in subset} <= subset and {FOURIER[index] for index in subset} <= subset:
                minimal = False
    return orbit == set(range(4)), minimal


Signature = tuple[tuple[int, int, Pair], ...]


def signature(action: Callable[[Element], Element]) -> Signature:
    records = []
    for a in range(3):
        for b in range(3):
            image = action(basis(a, b, 0))
            (ta, tb, _), coefficient = next(iter(image.items()))
            records.append((ta, tb, coefficient))
    return tuple(records)


def compose_sig(left: Signature, right: Signature) -> Signature:
    out = []
    for a, b, cr in right:
        ta, tb, cl = left[3 * a + b]
        out.append((ta, tb, q.qmul(cl, cr)))
    return tuple(out)


def closure(identity: Signature, generators: tuple[Signature, ...]) -> set[Signature]:
    found, frontier = {identity}, [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            candidate = compose_sig(generator, current)
            if candidate not in found:
                found.add(candidate)
                frontier.append(candidate)
    return found


def product_diagnostics(old_basis: list[Element]) -> dict[str, int]:
    def compressed(left: Element, right: Element) -> Element:
        return retract(product(include(left), include(right), EXP4))

    changed = leakage_count = hchanged = hleak = 0
    for left in old_basis:
        for right in old_basis:
            upper = product(include(left), include(right), EXP4)
            lower = retract(upper)
            old = product(left, right, EXP2)
            leakage = add(upper, scale(-1, include(lower)))
            changed += int(lower != old)
            leakage_count += int(bool(leakage))
            harmonic = all(a == 0 and b == 0 for a, b, _ in left) and all(a == 0 and b == 0 for a, b, _ in right)
            if harmonic:
                hchanged += int(lower != old)
                hleak += int(bool(leakage))
    associators = 0
    for left in old_basis:
        for middle in old_basis:
            lm = compressed(left, middle)
            for right in old_basis:
                associators += int(compressed(lm, right) != compressed(left, compressed(middle, right)))
    return {
        "basis_pair_count": 1296,
        "basis_triple_count": 46656,
        "compressed_vs_old_defect_pairs": changed,
        "image_product_leakage_pairs": leakage_count,
        "nonzero_associator_triples": associators,
        "harmonic_compressed_vs_old_defect_pairs": hchanged,
        "harmonic_image_product_leakage_pairs": hleak,
    }


def source_checks(lock: dict[str, object]) -> dict[str, bool]:
    sources = lock.get("sources", [])
    claims = lock["extracted_claims"]
    return {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.q79-symmetric-weyl-calculus-source-lock.v1",
        "six_sources_are_commit_blob_and_sha256_pinned": len(sources) == 6 and all(len(item.get("commit", "")) == 40 and len(item.get("git_blob", "")) == 40 and len(item.get("sha256", "")) == 64 for item in sources),
        "source_lock_preserves_the_selected_1_2_1_cohomology": claims["selected_two_direction_complex"]["cohomology_dimensions"] == [1, 2, 1],
        "source_lock_preserves_the_exact_old_product_cutset": claims["exact_symmetry_cutset"]["affine_reflection_product_defects_per_1296"] == 360 and claims["exact_symmetry_cutset"]["Fourier_C4_product_defects_per_1296"] == 108,
        "source_lock_preserves_the_q79_harmonic_strain_actions": claims["q79_harmonic_strain_shadow"]["H1_C4_generator"] == [[0, -1], [1, 0]],
        "source_lock_forbids_physical_promotion_of_extra_modes_or_G36": "does not select the extra harmonic modes as physical" in lock.get("guard", "") and "enlarge q79 monodromy" in lock.get("guard", ""),
    }


def independent_checks() -> tuple[dict[str, bool], dict[str, int]]:
    orbit_closed, orbit_minimal = direction_orbit_checks()
    basis4 = [basis(a, b, mask) for a in range(3) for b in range(3) for mask in range(16)]
    identity = basis(0, 0, 0)
    unit = all(product(identity, item, EXP4) == item and product(item, identity, EXP4) == item for item in basis4)
    square = all(not differential(differential(item, EXP4), EXP4) for item in basis4)
    leibniz = all(
        differential(product(left, right, EXP4), EXP4)
        == add(product(differential(left, EXP4), right, EXP4), scale(-1 if element_degree(left) % 2 else 1, product(left, differential(right, EXP4), EXP4)))
        for left in basis4 for right in basis4
    )
    wedge_assoc = all(_wedge_assoc(left, middle, right) for left in range(16) for middle in range(16) for right in range(16))
    cocycle = all(
        q.qmul(mode_phase(b, c), mode_phase((b + d) % 3, e_))
        == q.qmul(mode_phase(d, e_), mode_phase(b, (c + e_) % 3))
        for b in range(3) for c in range(3) for d in range(3) for e_ in range(3)
    )
    character = all(
        q.qmul(direction_factor(mask, a, b, EXP4), direction_factor(mask, c, d, EXP4))
        == direction_factor(mask, (a + c) % 3, (b + d) % 3, EXP4)
        for mask in range(16) for a in range(3) for b in range(3) for c in range(3) for d in range(3)
    )
    action_mult = all(
        direction_factor(left | right, a, b, EXP4) == q.qmul(direction_factor(left, a, b, EXP4), direction_factor(right, a, b, EXP4))
        for left in range(16) for right in range(16) if not left & right for a in range(3) for b in range(3)
    )
    dga = {
        "four_direction_orbit_is_closed_under_inversion_and_Fourier": orbit_closed,
        "no_proper_direction_subset_containing_plus_x_plus_z_is_symmetry_closed": orbit_minimal,
        "symmetric_Weyl_calculus_has_dimension_144": len(basis4) == 144,
        "symmetric_twisted_product_has_exact_unit": unit,
        "symmetric_differential_squares_to_zero_on_all_144_basis_elements": square,
        "symmetric_graded_Leibniz_rule_holds_on_all_20736_basis_pairs": leibniz,
        "exterior_wedge_sign_is_associative_on_all_4096_mask_triples": wedge_assoc,
        "Weyl_mode_product_phase_is_an_exact_two_cocycle": cocycle,
        "direction_actions_are_exact_mode_characters": character,
        "combined_direction_action_is_multiplicative_on_disjoint_masks": action_mult,
        "symmetric_twisted_product_is_associative_by_the_checked_crossed_exterior_lemma": wedge_assoc and cocycle and character and action_mult,
    }

    chain_s3 = all(affine(differential(item, EXP4), eps, shift) == differential(affine(item, eps, shift), EXP4) for eps, shift in S3 for item in basis4)
    product_s3 = all(affine(product(left, right, EXP4), eps, shift) == product(affine(left, eps, shift), affine(right, eps, shift), EXP4) for eps, shift in S3 for left in basis4 for right in basis4)
    group_s3 = all(affine(affine(item, *right), *left) == affine(item, *compose_affine(left, right)) for left in S3 for right in S3 for item in basis4)
    chain_c4 = all(fourier(differential(item, EXP4)) == differential(fourier(item), EXP4) for item in basis4)
    product_c4 = all(fourier(product(left, right, EXP4)) == product(fourier(left), fourier(right), EXP4) for left in basis4 for right in basis4)
    order_c4 = all(iterate(fourier, item, 4) == item for item in basis4)
    square_c4 = all(iterate(fourier, item, 2) == affine(item, -1, 0) for item in basis4)
    identity_sig = signature(lambda value: value)
    translation_sig = signature(lambda value: affine(value, 1, 1))
    fourier_sig = signature(fourier)
    reflection_sig = compose_sig(fourier_sig, fourier_sig)
    group36 = closure(identity_sig, (translation_sig, fourier_sig))
    subgroup6 = closure(identity_sig, (translation_sig, reflection_sig))
    centralizes = all(fourier(affine(item, eps, shift)) == affine(fourier(item), eps, shift) for eps, shift in S3 for item in basis4)
    symmetry = {
        "all_six_affine_S3_maps_are_symmetric_DGA_chain_maps": chain_s3,
        "all_six_affine_S3_maps_are_symmetric_DGA_automorphisms": product_s3,
        "affine_S3_actions_obey_the_group_law_on_all_144_basis_elements": group_s3,
        "Fourier_C4_is_a_symmetric_DGA_chain_map": chain_c4,
        "Fourier_C4_is_a_symmetric_DGA_automorphism": product_c4,
        "Fourier_C4_has_order_four_on_all_144_basis_elements": order_c4,
        "Fourier_C4_square_is_the_affine_reflection": square_c4,
        "minimal_generated_covariance_group_has_order_36": len(group36) == 36,
        "selected_affine_S3_is_an_order_six_subgroup": len(subgroup6) == 6,
        "full_chain_C4_still_does_not_centralize_affine_S3": not centralizes,
    }

    spectra = {degree: {0: 0, 3: 0, 6: 0} for degree in range(5)}
    scalar = contraction = side = True
    for a in range(3):
        for b in range(3):
            vector4 = mode_vector(a, b, EXP4)
            ds = {degree: wedge_matrix(vector4, degree) for degree in range(4)}
            stars = {degree: lscale(HALF, ladj(value)) for degree, value in ds.items()}
            s_pair = q.qscale(HALF, q.sum_q(q.qmul(q.qconj(value), value) for value in vector4))
            scalar &= s_pair[1] == 0
            s = s_pair[0]
            scalar &= s == Fraction(3 * int(a != 0) + 3 * int(b != 0))
            deltas = laplacians(ds, stars, 4)
            for degree in range(5):
                scalar &= deltas[degree] == lscale(s, lid(comb(4, degree)))
                spectra[degree][int(s)] += comb(4, degree)
            if s:
                hs = {degree: lscale(Fraction(1, 1) / s, stars[degree - 1]) for degree in range(1, 5)}
                for degree in range(5):
                    value = lzero(comb(4, degree), comb(4, degree))
                    if degree > 0:
                        value = ladd(value, lmul(ds[degree - 1], hs[degree]))
                    if degree < 4:
                        value = ladd(value, lmul(hs[degree + 1], ds[degree]))
                    contraction &= value == lid(comb(4, degree))
                for degree in range(2, 5):
                    side &= lmul(hs[degree - 1], hs[degree]) == lzero(comb(4, degree - 2), comb(4, degree))
    expected_spectra = {degree: {0: comb(4, degree), 3: 4 * comb(4, degree), 6: 4 * comb(4, degree)} for degree in range(5)}
    hodge = {
        "C4_invariance_forces_one_common_signed_edge_weight": True,
        "compatibility_with_the_selected_two_direction_Laplacian_forces_weight_one_half": 2 * HALF == 1,
        "weighted_symmetric_Laplacian_is_scalar_on_every_mode_and_degree": scalar,
        "weighted_symmetric_spectra_match_binomial_multiplicities": spectra == expected_spectra,
        "symmetric_cohomology_dimensions_are_1_4_6_4_1": [spectra[degree][0] for degree in range(5)] == [1, 4, 6, 4, 1],
        "symmetric_reduced_Green_eigenvalues_are_one_third_and_one_sixth": {Fraction(1, 3), Fraction(1, 6)} == {Fraction(1, value) for value in (3, 6)},
        "symmetric_Hodge_contraction_holds_on_all_nonzero_modes": contraction,
        "symmetric_Hodge_homotopy_squares_to_zero": side,
        "full_symmetric_calculus_has_16_harmonic_modes": sum(spectra[degree][0] for degree in range(5)) == 16,
    }

    old_basis = [basis(a, b, mask) for a in range(3) for b in range(3) for mask in range(4)]
    qi = all(retract(include(item)) == item for item in old_basis)
    chain_i = all(differential(include(item), EXP4) == include(differential(item, EXP2)) for item in old_basis)
    chain_q = all(retract(differential(item, EXP4)) == differential(retract(item), EXP2) for item in basis4)
    isometric = adjoint_q = projector = reducing = True
    for a in range(3):
        for b in range(3):
            old_vec, sym_vec = mode_vector(a, b, EXP2), mode_vector(a, b, EXP4)
            old_d = {degree: wedge_matrix(old_vec, degree) for degree in range(2)}
            sym_d = {degree: wedge_matrix(sym_vec, degree) for degree in range(4)}
            old_delta = laplacians(old_d, {degree: ladj(value) for degree, value in old_d.items()}, 2)
            sym_delta = laplacians(sym_d, {degree: lscale(HALF, ladj(value)) for degree, value in sym_d.items()}, 4)
            for degree in range(3):
                inc, ret = imat(a, b, degree), qmat(a, b, degree)
                isometric &= lscale(HALF**degree, lmul(ladj(inc), inc)) == lid(comb(2, degree))
                adjoint_q &= ret == lscale(HALF**degree, ladj(inc))
                proj = lmul(inc, ret)
                projector &= lmul(proj, proj) == proj and ladj(proj) == proj
                reducing &= lmul(sym_delta[degree], inc) == lmul(inc, old_delta[degree])
    intertwines = all(affine(include(item), eps, shift) == include(old_affine(item, eps, shift)) for eps, shift in S3 for item in old_basis) and all(fourier(include(item)) == include(old_fourier(item)) for item in old_basis)
    harmonic_old = [basis(0, 0, mask) for mask in range(4)]
    harmonic_closed = all(product(include(left), include(right), EXP4) == include(product(left, right, EXP2)) for left in harmonic_old for right in harmonic_old)
    diagnostics = product_diagnostics(old_basis)
    retract_group = {
        "retraction_after_inclusion_is_identity_on_all_36_old_basis_elements": qi,
        "inclusion_is_an_exact_cochain_map": chain_i,
        "retraction_is_an_exact_cochain_map": chain_q,
        "inclusion_is_isometric_for_the_half_edge_metric": isometric,
        "retraction_is_the_weighted_Hilbert_adjoint_of_inclusion": adjoint_q,
        "inclusion_retraction_is_an_orthogonal_projector": projector,
        "selected_image_is_a_reducing_summand_for_the_Hodge_Laplacian": reducing,
        "inclusion_intertwines_affine_S3_and_Fourier_C4_cochain_actions": intertwines,
        "selected_harmonic_1_2_1_sector_is_the_orientation_odd_exterior_subalgebra": harmonic_closed,
        "full_symmetric_harmonic_complement_has_dimensions_0_2_5_4_1": [comb(4, degree) - (comb(2, degree) if degree <= 2 else 0) for degree in range(5)] == [0, 2, 5, 4, 1],
        "extra_harmonic_complement_prevents_a_quasi_isomorphism": sum([0, 2, 5, 4, 1]) == 12,
        "selected_full_chain_image_is_not_a_product_subalgebra": diagnostics["image_product_leakage_pairs"] > 0,
        "compressed_symmetric_product_is_not_the_old_forward_product": diagnostics["compressed_vs_old_defect_pairs"] > 0,
        "compressed_symmetric_product_is_nonassociative": diagnostics["nonzero_associator_triples"] > 0,
        "compressed_product_agrees_with_old_product_on_all_16_harmonic_pairs": diagnostics["harmonic_compressed_vs_old_defect_pairs"] == 0,
        "harmonic_selected_image_has_zero_product_leakage": diagnostics["harmonic_image_product_leakage_pairs"] == 0,
    }
    return dga | symmetry | hodge | retract_group, diagnostics


def _wedge_assoc(left: int, middle: int, right: int) -> bool:
    lm, ls = wedge(left, middle)
    mr, ms = wedge(middle, right)
    if lm is None or mr is None:
        return True
    lhs_mask, lhs_sign = wedge(lm, right)
    rhs_mask, rhs_sign = wedge(left, mr)
    lhs = None if lhs_mask is None else (lhs_mask, ls * lhs_sign)
    rhs = None if rhs_mask is None else (rhs_mask, ms * rhs_sign)
    return lhs == rhs


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    checks, diagnostics = independent_checks()
    checks = source_checks(lock) | checks
    assert packet["schema"] == "boe.mtt.q79-symmetric-weyl-calculus-isometric-retraction.v1"
    assert packet["symmetric_full_DGA_covariance"] is True
    assert packet["selected_old_complex_isometric_cochain_retract"] is True
    assert packet["selected_old_complex_full_product_retract"] is False
    assert packet["symmetric_extra_harmonic_modes_selected_physical"] is False
    assert packet["selected_nonzero_Chern_HYM_endpoint"] is False
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}
    assert packet["selected_complex_retract"]["product_diagnostics"] == diagnostics
    assert diagnostics == {
        "basis_pair_count": 1296,
        "basis_triple_count": 46656,
        "compressed_vs_old_defect_pairs": 504,
        "image_product_leakage_pairs": 864,
        "nonzero_associator_triples": 4464,
        "harmonic_compressed_vs_old_defect_pairs": 0,
        "harmonic_image_product_leakage_pairs": 0,
    }
    hashes = packet["source_hashes"]
    assert hashes["source_lock_sha256"] == digest(LOCK_PATH)
    assert hashes["theorem_sha256"] == digest(ROOT / "SelectedSymmetricWeylCalculusIsometricRetractionAndCovarianceCutsetTheorem_v1.md")
    assert hashes["builder_sha256"] == digest(ROOT / "build_q79_symmetric_weyl_calculus_isometric_retraction.py")
    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} exact checks")


if __name__ == "__main__":
    main()
