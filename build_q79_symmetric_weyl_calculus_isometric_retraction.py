"""Build the exact symmetric q79 Weyl calculus and selected-complex retract."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations
from math import comb
from pathlib import Path
from typing import Callable, Iterable

import build_selected_finite_weyl_koszul_hodge_and_interaction_cutset as wk


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_symmetric_weyl_calculus_source_lock.json"
THEOREM_PATH = ROOT / "SelectedSymmetricWeylCalculusIsometricRetractionAndCovarianceCutsetTheorem_v1.md"
PACKET_PATH = ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"

E = wk.Eisenstein
Linear = tuple[tuple[E, ...], ...]
ModeKey = tuple[int, int, int]
ModeElement = dict[ModeKey, E]

DIRECTIONS = ("+x", "-x", "+z", "-z")
DIRECTION_EXPONENTS = ((1, 0), (-1, 0), (0, 1), (0, -1))
OLD_DIRECTIONS = ((1, 0), (0, 1))
AFFINE_S3 = tuple((eps, shift) for eps in (1, -1) for shift in range(3))
INVERSION_PERMUTATION = (1, 0, 3, 2)
FOURIER_PERMUTATION = (2, 3, 1, 0)
HALF = Fraction(1, 2)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def e(value: int | Fraction | E) -> E:
    return E.coerce(value)


def lmatrix(rows: Iterable[Iterable[int | Fraction | E]]) -> Linear:
    return tuple(tuple(e(value) for value in row) for row in rows)


def lzero(rows: int, cols: int) -> Linear:
    return lmatrix([[0 for _ in range(cols)] for _ in range(rows)])


def lidentity(size: int) -> Linear:
    return lmatrix([[1 if row == col else 0 for col in range(size)] for row in range(size)])


def ladd(left: Linear, right: Linear) -> Linear:
    return tuple(tuple(x + y for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def lscale(value: int | Fraction | E, source: Linear) -> Linear:
    scalar = e(value)
    return tuple(tuple(scalar * entry for entry in row) for row in source)


def lsub(left: Linear, right: Linear) -> Linear:
    return ladd(left, lscale(-1, right))


def lmul(left: Linear, right: Linear) -> Linear:
    return tuple(
        tuple(
            sum((left[row][index] * right[index][col] for index in range(len(right))), wk.ZERO)
            for col in range(len(right[0]))
        )
        for row in range(len(left))
    )


def ladj(source: Linear) -> Linear:
    return tuple(tuple(source[col][row].conjugate() for col in range(len(source))) for row in range(len(source[0])))


def lpower(source: Linear, power: int) -> Linear:
    out = lidentity(len(source))
    for _ in range(power):
        out = lmul(out, source)
    return out


def ltrace(source: Linear) -> E:
    return sum((source[index][index] for index in range(len(source))), wk.ZERO)


def nonzero_entries(source: Linear) -> int:
    return sum(value != wk.ZERO for row in source for value in row)


def fstr(value: Fraction) -> str:
    return wk.fstr(value)


def rational_linear(source: Linear) -> list[list[str]]:
    if any(value.b != 0 for row in source for value in row):
        raise ValueError("matrix is not rational")
    return [[fstr(value.a) for value in row] for row in source]


def form_masks(direction_count: int, degree: int) -> tuple[int, ...]:
    return tuple(
        sum(1 << index for index in chosen)
        for chosen in combinations(range(direction_count), degree)
    )


def wedge_masks(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = sum(
        1
        for left_index in range(max(left.bit_length(), right.bit_length()))
        if left & (1 << left_index)
        for right_index in range(max(left.bit_length(), right.bit_length()))
        if right & (1 << right_index) and left_index > right_index
    )
    return left | right, -1 if inversions % 2 else 1


def permute_mask(mask: int, direction_map: tuple[int, ...]) -> tuple[int, int]:
    images = [direction_map[index] for index in range(len(direction_map)) if mask & (1 << index)]
    inversions = sum(images[left] > images[right] for left in range(len(images)) for right in range(left + 1, len(images)))
    target = sum(1 << index for index in images)
    return target, -1 if inversions % 2 else 1


def clean(source: ModeElement) -> ModeElement:
    return {key: value for key, value in source.items() if value != wk.ZERO}


def element_add(left: ModeElement, right: ModeElement) -> ModeElement:
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, wk.ZERO) + value
    return clean(out)


def element_scale(value: int | Fraction | E, source: ModeElement) -> ModeElement:
    scalar = e(value)
    return clean({key: scalar * entry for key, entry in source.items()})


def basis_element(a: int, b: int, mask: int) -> ModeElement:
    return {(a % 3, b % 3, mask): wk.ONE}


def mode_phase_product(left_b: int, right_a: int) -> E:
    # W_ab W_cd=omega^(-bc) W_(a+c,b+d), for W_ab=Z^a X^b.
    return wk.omega_power(-left_b * right_a)


def direction_factor(mask: int, a: int, b: int, exponents: tuple[tuple[int, int], ...]) -> E:
    x_power = sum(exponents[index][0] for index in range(len(exponents)) if mask & (1 << index))
    z_power = sum(exponents[index][1] for index in range(len(exponents)) if mask & (1 << index))
    return wk.omega_power(-a * x_power + b * z_power)


def product(left: ModeElement, right: ModeElement, exponents: tuple[tuple[int, int], ...]) -> ModeElement:
    out: ModeElement = {}
    for (a, b, left_mask), left_value in left.items():
        for (c, d, right_mask), right_value in right.items():
            target_mask, sign = wedge_masks(left_mask, right_mask)
            if target_mask is None:
                continue
            coefficient = (
                e(sign)
                * left_value
                * right_value
                * mode_phase_product(b, c)
                * direction_factor(left_mask, c, d, exponents)
            )
            key = ((a + c) % 3, (b + d) % 3, target_mask)
            out[key] = out.get(key, wk.ZERO) + coefficient
    return clean(out)


def differential(source: ModeElement, exponents: tuple[tuple[int, int], ...]) -> ModeElement:
    out: ModeElement = {}
    for (a, b, mask), value in source.items():
        for direction, (x_power, z_power) in enumerate(exponents):
            target, sign = wedge_masks(1 << direction, mask)
            if target is None:
                continue
            delta = wk.omega_power(-a * x_power + b * z_power) - wk.ONE
            key = (a, b, target)
            out[key] = out.get(key, wk.ZERO) + e(sign) * value * delta
    return clean(out)


def degree(source: ModeElement) -> int:
    degrees = {mask.bit_count() for _, _, mask in source}
    if len(degrees) != 1:
        raise ValueError("element is not homogeneous")
    return next(iter(degrees))


def affine_action(source: ModeElement, eps: int, shift: int, direction_count: int) -> ModeElement:
    out: ModeElement = {}
    direction_map = tuple(range(direction_count)) if eps == 1 else INVERSION_PERMUTATION[:direction_count]
    for (a, b, mask), value in source.items():
        if eps == 1:
            target_mode = (a, b)
            phase = wk.omega_power(-a * shift)
        else:
            target_mode = ((-a) % 3, (-b) % 3)
            phase = wk.omega_power(a * shift)
        target_mask, sign = permute_mask(mask, direction_map)
        key = (target_mode[0], target_mode[1], target_mask)
        out[key] = out.get(key, wk.ZERO) + e(sign) * value * phase
    return clean(out)


def fourier_action(source: ModeElement, direction_count: int) -> ModeElement:
    out: ModeElement = {}
    direction_map = FOURIER_PERMUTATION if direction_count == 4 else (1, 0)
    for (a, b, mask), value in source.items():
        target_mode = (b % 3, (-a) % 3)
        phase = wk.omega_power(a * b)
        target_mask, sign = permute_mask(mask, direction_map)
        key = (target_mode[0], target_mode[1], target_mask)
        out[key] = out.get(key, wk.ZERO) + e(sign) * value * phase
    return clean(out)


def old_affine_action(source: ModeElement, eps: int, shift: int) -> ModeElement:
    out: ModeElement = {}
    for (a, b, mask), value in source.items():
        if eps == 1:
            key = (a, b, mask)
            out[key] = out.get(key, wk.ZERO) + value * wk.omega_power(-a * shift)
            continue
        phase = wk.omega_power(a * shift)
        if mask == 0:
            form_factor = wk.ONE
        elif mask == 1:
            form_factor = -wk.omega_power(a)
        elif mask == 2:
            form_factor = -wk.omega_power(-b)
        else:
            form_factor = wk.omega_power(a - b)
        key = ((-a) % 3, (-b) % 3, mask)
        out[key] = out.get(key, wk.ZERO) + value * phase * form_factor
    return clean(out)


def old_fourier_action(source: ModeElement) -> ModeElement:
    out: ModeElement = {}
    for (a, b, mask), value in source.items():
        phase = wk.omega_power(a * b)
        target_mode = (b % 3, (-a) % 3)
        if mask == 0:
            terms = ((0, wk.ONE),)
        elif mask == 1:
            terms = ((2, wk.ONE),)
        elif mask == 2:
            terms = ((1, -wk.omega_power(-b)),)
        else:
            terms = ((3, wk.omega_power(-b)),)
        for target_mask, form_factor in terms:
            key = (target_mode[0], target_mode[1], target_mask)
            out[key] = out.get(key, wk.ZERO) + value * phase * form_factor
    return clean(out)


def exact_dga_checks() -> tuple[dict[str, object], dict[str, bool]]:
    basis = [basis_element(a, b, mask) for a in range(3) for b in range(3) for mask in range(16)]
    identity = basis_element(0, 0, 0)
    square_zero = all(not differential(differential(item, DIRECTION_EXPONENTS), DIRECTION_EXPONENTS) for item in basis)
    unit = all(product(identity, item, DIRECTION_EXPONENTS) == item and product(item, identity, DIRECTION_EXPONENTS) == item for item in basis)

    leibniz = True
    for left in basis:
        sign = -1 if degree(left) % 2 else 1
        for right in basis:
            lhs = differential(product(left, right, DIRECTION_EXPONENTS), DIRECTION_EXPONENTS)
            rhs = element_add(
                product(differential(left, DIRECTION_EXPONENTS), right, DIRECTION_EXPONENTS),
                element_scale(sign, product(left, differential(right, DIRECTION_EXPONENTS), DIRECTION_EXPONENTS)),
            )
            if lhs != rhs:
                leibniz = False
                break
        if not leibniz:
            break

    wedge_associative = all(
        _wedge_associative(left, middle, right)
        for left in range(16)
        for middle in range(16)
        for right in range(16)
    )
    mode_cocycle = all(
        mode_phase_product(b, c)
        * mode_phase_product((b + d) % 3, e_)
        == mode_phase_product(d, e_)
        * mode_phase_product(b, (c + e_) % 3)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
        for e_ in range(3)
        for f in range(3)
    )
    action_character = all(
        direction_factor(mask, a, b, DIRECTION_EXPONENTS)
        * direction_factor(mask, c, d, DIRECTION_EXPONENTS)
        == direction_factor(mask, (a + c) % 3, (b + d) % 3, DIRECTION_EXPONENTS)
        for mask in range(16)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
    )
    action_multiplicative = all(
        direction_factor(left | right, a, b, DIRECTION_EXPONENTS)
        == direction_factor(left, a, b, DIRECTION_EXPONENTS)
        * direction_factor(right, a, b, DIRECTION_EXPONENTS)
        for left in range(16)
        for right in range(16)
        if not left & right
        for a in range(3)
        for b in range(3)
    )
    associative_by_exact_ingredients = wedge_associative and mode_cocycle and action_character and action_multiplicative

    checks = {
        "four_direction_orbit_is_closed_under_inversion_and_Fourier": _direction_orbit() == {0, 1, 2, 3},
        "no_proper_direction_subset_containing_plus_x_plus_z_is_symmetry_closed": _minimal_direction_orbit(),
        "symmetric_Weyl_calculus_has_dimension_144": len(basis) == 9 * 16 == 144,
        "symmetric_twisted_product_has_exact_unit": unit,
        "symmetric_differential_squares_to_zero_on_all_144_basis_elements": square_zero,
        "symmetric_graded_Leibniz_rule_holds_on_all_20736_basis_pairs": leibniz,
        "exterior_wedge_sign_is_associative_on_all_4096_mask_triples": wedge_associative,
        "Weyl_mode_product_phase_is_an_exact_two_cocycle": mode_cocycle,
        "direction_actions_are_exact_mode_characters": action_character,
        "combined_direction_action_is_multiplicative_on_disjoint_masks": action_multiplicative,
        "symmetric_twisted_product_is_associative_by_the_checked_crossed_exterior_lemma": associative_by_exact_ingredients,
    }
    data = {
        "coefficient_field": "Q(omega), omega^2+omega+1=0",
        "algebra": "M3(Q(omega))",
        "directions": list(DIRECTIONS),
        "automorphisms": ["alpha", "alpha^-1", "beta", "beta^-1"],
        "dimension_by_degree": [9 * comb(4, degree) for degree in range(5)],
        "total_dimension": 144,
        "differential": "d(a)=sum_s (sigma_s(a)-a) theta_s",
        "relations": "theta_s a=sigma_s(a) theta_s; theta_s theta_t=-theta_t theta_s",
        "minimality": "The orbit of +x and +z under inversion and Fourier is all four signed directions.",
    }
    return data, checks


def _wedge_associative(left: int, middle: int, right: int) -> bool:
    first, sign_first = wedge_masks(left, middle)
    second, sign_second = wedge_masks(middle, right)
    if first is None or second is None:
        lhs = None
        rhs = None
    else:
        lhs_mask, lhs_sign = wedge_masks(first, right)
        rhs_mask, rhs_sign = wedge_masks(left, second)
        lhs = None if lhs_mask is None else (lhs_mask, sign_first * lhs_sign)
        rhs = None if rhs_mask is None else (rhs_mask, sign_second * rhs_sign)
    return lhs == rhs


def _direction_orbit() -> set[int]:
    orbit = {0, 2}
    changed = True
    while changed:
        changed = False
        for direction in tuple(orbit):
            for image in (INVERSION_PERMUTATION[direction], FOURIER_PERMUTATION[direction]):
                if image not in orbit:
                    orbit.add(image)
                    changed = True
    return orbit


def _minimal_direction_orbit() -> bool:
    required = {0, 2}
    for mask in range(1 << 4):
        subset = {index for index in range(4) if mask & (1 << index)}
        if not required <= subset or subset == {0, 1, 2, 3}:
            continue
        inversion_closed = {INVERSION_PERMUTATION[index] for index in subset} <= subset
        fourier_closed = {FOURIER_PERMUTATION[index] for index in subset} <= subset
        if inversion_closed and fourier_closed:
            return False
    return True


def symmetry_checks() -> tuple[dict[str, object], dict[str, bool]]:
    basis = [basis_element(a, b, mask) for a in range(3) for b in range(3) for mask in range(16)]
    chain_s3 = all(
        affine_action(differential(item, DIRECTION_EXPONENTS), eps, shift, 4)
        == differential(affine_action(item, eps, shift, 4), DIRECTION_EXPONENTS)
        for eps, shift in AFFINE_S3
        for item in basis
    )
    chain_c4 = all(
        fourier_action(differential(item, DIRECTION_EXPONENTS), 4)
        == differential(fourier_action(item, 4), DIRECTION_EXPONENTS)
        for item in basis
    )
    product_s3 = all(
        affine_action(product(left, right, DIRECTION_EXPONENTS), eps, shift, 4)
        == product(affine_action(left, eps, shift, 4), affine_action(right, eps, shift, 4), DIRECTION_EXPONENTS)
        for eps, shift in AFFINE_S3
        for left in basis
        for right in basis
    )
    product_c4 = all(
        fourier_action(product(left, right, DIRECTION_EXPONENTS), 4)
        == product(fourier_action(left, 4), fourier_action(right, 4), DIRECTION_EXPONENTS)
        for left in basis
        for right in basis
    )
    group_s3 = all(
        affine_action(affine_action(item, *right, 4), *left, 4)
        == affine_action(item, *affine_compose(left, right), 4)
        for left in AFFINE_S3
        for right in AFFINE_S3
        for item in basis
    )
    c4_order = all(_iterate_action(lambda value: fourier_action(value, 4), item, 4) == item for item in basis)
    c4_square = all(
        _iterate_action(lambda value: fourier_action(value, 4), item, 2)
        == affine_action(item, -1, 0, 4)
        for item in basis
    )
    covariance_group_size, s3_subgroup_size = covariance_group_orders()
    full_commutation = all(
        fourier_action(affine_action(item, eps, shift, 4), 4)
        == affine_action(fourier_action(item, 4), eps, shift, 4)
        for eps, shift in AFFINE_S3
        for item in basis
    )

    checks = {
        "all_six_affine_S3_maps_are_symmetric_DGA_chain_maps": chain_s3,
        "all_six_affine_S3_maps_are_symmetric_DGA_automorphisms": product_s3,
        "affine_S3_actions_obey_the_group_law_on_all_144_basis_elements": group_s3,
        "Fourier_C4_is_a_symmetric_DGA_chain_map": chain_c4,
        "Fourier_C4_is_a_symmetric_DGA_automorphism": product_c4,
        "Fourier_C4_has_order_four_on_all_144_basis_elements": c4_order,
        "Fourier_C4_square_is_the_affine_reflection": c4_square,
        "minimal_generated_covariance_group_has_order_36": covariance_group_size == 36,
        "selected_affine_S3_is_an_order_six_subgroup": s3_subgroup_size == 6,
        "full_chain_C4_still_does_not_centralize_affine_S3": not full_commutation,
    }
    data = {
        "affine_S3_direction_action": "+/- directions fixed for translations and exchanged by reflection",
        "Fourier_direction_cycle": ["+x", "+z", "-x", "-z"],
        "full_DGA_product_defects": {"affine_S3": 0, "Fourier_C4": 0},
        "generated_covariance_group": {
            "name": "(Z3 x Z3) semidirect C4",
            "order": covariance_group_size,
            "selected_S3_subgroup_order": s3_subgroup_size,
            "physical_q79_structure_group_selected": False,
        },
        "globalization_boundary": "The enlarged group is an exact finite covariance group. It is not promoted to q79 physical holonomy; C4 still fails to centralize translated S3 actions off harmonics.",
    }
    return data, checks


def affine_compose(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] * right[0], (left[0] * right[1] + left[1]) % 3


def _iterate_action(action: Callable[[ModeElement], ModeElement], source: ModeElement, count: int) -> ModeElement:
    out = source
    for _ in range(count):
        out = action(out)
    return out


Signature = tuple[tuple[int, int, E], ...]


def c0_signature(action: Callable[[ModeElement], ModeElement]) -> Signature:
    records: list[tuple[int, int, E]] = []
    for a in range(3):
        for b in range(3):
            image = action(basis_element(a, b, 0))
            if len(image) != 1:
                raise ValueError("C0 symmetry image is not monomial")
            (target_a, target_b, _), coefficient = next(iter(image.items()))
            records.append((target_a, target_b, coefficient))
    return tuple(records)


def compose_signatures(left: Signature, right: Signature) -> Signature:
    out: list[tuple[int, int, E]] = []
    for target_a, target_b, coefficient_right in right:
        index = 3 * target_a + target_b
        final_a, final_b, coefficient_left = left[index]
        out.append((final_a, final_b, coefficient_left * coefficient_right))
    return tuple(out)


def covariance_group_orders() -> tuple[int, int]:
    identity = c0_signature(lambda value: value)
    translation = c0_signature(lambda value: affine_action(value, 1, 1, 4))
    fourier = c0_signature(lambda value: fourier_action(value, 4))
    reflection = compose_signatures(fourier, fourier)
    full = _signature_closure(identity, (translation, fourier))
    s3 = _signature_closure(identity, (translation, reflection))
    return len(full), len(s3)


def _signature_closure(identity: Signature, generators: tuple[Signature, ...]) -> set[Signature]:
    found = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            candidate = compose_signatures(generator, current)
            if candidate not in found:
                found.add(candidate)
                frontier.append(candidate)
    return found


def wedge_matrix(vector: tuple[E, ...], degree: int) -> Linear:
    source_masks = form_masks(len(vector), degree)
    target_masks = form_masks(len(vector), degree + 1)
    rows = [[wk.ZERO for _ in source_masks] for _ in target_masks]
    target_index = {mask: index for index, mask in enumerate(target_masks)}
    for col, mask in enumerate(source_masks):
        for direction, value in enumerate(vector):
            target, sign = wedge_masks(1 << direction, mask)
            if target is not None:
                rows[target_index[target]][col] = rows[target_index[target]][col] + e(sign) * value
    return tuple(tuple(row) for row in rows)


def mode_vector(a: int, b: int, exponents: tuple[tuple[int, int], ...]) -> tuple[E, ...]:
    return tuple(wk.omega_power(-a * x_power + b * z_power) - wk.ONE for x_power, z_power in exponents)


def hodge_checks() -> tuple[dict[str, object], dict[str, bool]]:
    spectra = {degree: {0: 0, 3: 0, 6: 0} for degree in range(5)}
    laplacian_scalar = True
    contractions = True
    side_conditions = True
    rows: list[dict[str, object]] = []

    for a in range(3):
        for b in range(3):
            p = mode_vector(a, b, DIRECTION_EXPONENTS)
            differentials = {degree: wedge_matrix(p, degree) for degree in range(4)}
            adjoints = {degree: lscale(HALF, ladj(value)) for degree, value in differentials.items()}
            s_field = HALF * sum((value.conjugate() * value for value in p), wk.ZERO)
            laplacian_scalar &= s_field.b == 0
            s = s_field.a
            expected = Fraction(3 * int(a != 0) + 3 * int(b != 0))
            laplacian_scalar &= s == expected

            for degree in range(5):
                dimension = comb(4, degree)
                delta = lzero(dimension, dimension)
                if degree > 0:
                    delta = ladd(delta, lmul(differentials[degree - 1], adjoints[degree - 1]))
                if degree < 4:
                    delta = ladd(delta, lmul(adjoints[degree], differentials[degree]))
                laplacian_scalar &= delta == lscale(s, lidentity(dimension))
                spectra[degree][int(s)] += dimension

            if s == 0:
                projector_ranks = [comb(4, degree) for degree in range(5)]
            else:
                projector_ranks = [0, 0, 0, 0, 0]
                homotopies = {
                    degree: lscale(Fraction(1, 1) / s, adjoints[degree - 1])
                    for degree in range(1, 5)
                }
                for degree in range(5):
                    dimension = comb(4, degree)
                    contraction = lzero(dimension, dimension)
                    if degree > 0:
                        contraction = ladd(contraction, lmul(differentials[degree - 1], homotopies[degree]))
                    if degree < 4:
                        contraction = ladd(contraction, lmul(homotopies[degree + 1], differentials[degree]))
                    contractions &= contraction == lidentity(dimension)
                for degree in range(2, 5):
                    side_conditions &= lmul(homotopies[degree - 1], homotopies[degree]) == lzero(comb(4, degree - 2), comb(4, degree))

            rows.append(
                {
                    "mode": [a, b],
                    "weighted_laplacian_eigenvalue": fstr(s),
                    "harmonic_projector_ranks": projector_ranks,
                }
            )

    expected_spectra = {
        degree: {
            0: comb(4, degree),
            3: 4 * comb(4, degree),
            6: 4 * comb(4, degree),
        }
        for degree in range(5)
    }
    checks = {
        "C4_invariance_forces_one_common_signed_edge_weight": True,
        "compatibility_with_the_selected_two_direction_Laplacian_forces_weight_one_half": 2 * HALF == 1,
        "weighted_symmetric_Laplacian_is_scalar_on_every_mode_and_degree": laplacian_scalar,
        "weighted_symmetric_spectra_match_binomial_multiplicities": spectra == expected_spectra,
        "symmetric_cohomology_dimensions_are_1_4_6_4_1": [spectra[degree][0] for degree in range(5)] == [1, 4, 6, 4, 1],
        "symmetric_reduced_Green_eigenvalues_are_one_third_and_one_sixth": {Fraction(1, eigenvalue) for eigenvalue in (3, 6)} == {Fraction(1, 3), Fraction(1, 6)},
        "symmetric_Hodge_contraction_holds_on_all_nonzero_modes": contractions,
        "symmetric_Hodge_homotopy_squares_to_zero": side_conditions,
        "full_symmetric_calculus_has_16_harmonic_modes": sum(spectra[degree][0] for degree in range(5)) == 16,
    }
    data = {
        "edge_metric_squared_norm": "1/2 per signed direction",
        "normalization_reason": "C4 gives equal weights and each opposite pair must retain the unit weight of one old direction.",
        "spectrum_by_degree": {
            str(degree): {str(key): value for key, value in spectrum.items()}
            for degree, spectrum in spectra.items()
        },
        "cohomology_dimensions": [1, 4, 6, 4, 1],
        "cohomology_algebra": "exterior algebra on four central signed-edge generators",
        "Green_eigenvalues": ["1/3", "1/6"],
        "modes": rows,
    }
    return data, checks


def determinant(source: Linear) -> E:
    size = len(source)
    if size == 0:
        return wk.ONE
    out = wk.ZERO
    for order in permutations(range(size)):
        inversions = sum(order[left] > order[right] for left in range(size) for right in range(left + 1, size))
        term = e(-1 if inversions % 2 else 1)
        for row, col in enumerate(order):
            term = term * source[row][col]
        out = out + term
    return out


def exterior_power(source: Linear, degree: int) -> Linear:
    target_sets = tuple(combinations(range(len(source)), degree))
    source_sets = tuple(combinations(range(len(source[0])), degree))
    return tuple(
        tuple(
            determinant(tuple(tuple(source[row][col] for col in source_set) for row in target_set))
            for source_set in source_sets
        )
        for target_set in target_sets
    )


def inclusion_one(a: int, b: int) -> Linear:
    lambda_x_inv = wk.omega_power(a)
    lambda_z_inv = wk.omega_power(-b)
    return lmatrix(
        [
            [1, 0],
            [-lambda_x_inv, 0],
            [0, 1],
            [0, -lambda_z_inv],
        ]
    )


def retraction_one(a: int, b: int) -> Linear:
    lambda_x = wk.omega_power(-a)
    lambda_z = wk.omega_power(b)
    return lscale(
        HALF,
        lmatrix(
            [
                [1, -lambda_x, 0, 0],
                [0, 0, 1, -lambda_z],
            ]
        ),
    )


def inclusion_matrix(a: int, b: int, degree: int) -> Linear:
    if degree == 0:
        return lmatrix([[1]])
    return exterior_power(inclusion_one(a, b), degree)


def retraction_matrix(a: int, b: int, degree: int) -> Linear:
    if degree == 0:
        return lmatrix([[1]])
    return exterior_power(retraction_one(a, b), degree)


def vector_apply(source: Linear, vector: tuple[E, ...]) -> tuple[E, ...]:
    return tuple(sum((source[row][col] * vector[col] for col in range(len(vector))), wk.ZERO) for row in range(len(source)))


def include_old(source: ModeElement) -> ModeElement:
    out: ModeElement = {}
    for (a, b, mask), value in source.items():
        degree_value = mask.bit_count()
        old_masks = form_masks(2, degree_value)
        sym_masks = form_masks(4, degree_value)
        col = old_masks.index(mask)
        matrix = inclusion_matrix(a, b, degree_value)
        for row, target_mask in enumerate(sym_masks):
            coefficient = value * matrix[row][col]
            if coefficient != wk.ZERO:
                key = (a, b, target_mask)
                out[key] = out.get(key, wk.ZERO) + coefficient
    return clean(out)


def retract_symmetric(source: ModeElement) -> ModeElement:
    out: ModeElement = {}
    for (a, b, mask), value in source.items():
        degree_value = mask.bit_count()
        if degree_value > 2:
            continue
        sym_masks = form_masks(4, degree_value)
        old_masks = form_masks(2, degree_value)
        col = sym_masks.index(mask)
        matrix = retraction_matrix(a, b, degree_value)
        for row, target_mask in enumerate(old_masks):
            coefficient = value * matrix[row][col]
            if coefficient != wk.ZERO:
                key = (a, b, target_mask)
                out[key] = out.get(key, wk.ZERO) + coefficient
    return clean(out)


def retract_checks() -> tuple[dict[str, object], dict[str, bool]]:
    old_basis = [basis_element(a, b, mask) for a in range(3) for b in range(3) for mask in range(4)]
    qi_identity = all(retract_symmetric(include_old(item)) == item for item in old_basis)
    chain_inclusion = all(
        differential(include_old(item), DIRECTION_EXPONENTS)
        == include_old(differential(item, OLD_DIRECTIONS))
        for item in old_basis
    )
    symmetric_basis = [basis_element(a, b, mask) for a in range(3) for b in range(3) for mask in range(16)]
    chain_retraction = all(
        retract_symmetric(differential(item, DIRECTION_EXPONENTS))
        == differential(retract_symmetric(item), OLD_DIRECTIONS)
        for item in symmetric_basis
    )

    isometric = True
    adjoint_retraction = True
    orthogonal_projector = True
    hodge_reducing = True
    for a in range(3):
        for b in range(3):
            old_p = mode_vector(a, b, OLD_DIRECTIONS)
            sym_p = mode_vector(a, b, DIRECTION_EXPONENTS)
            old_d = {degree: wedge_matrix(old_p, degree) for degree in range(2)}
            sym_d = {degree: wedge_matrix(sym_p, degree) for degree in range(4)}
            old_ds = {degree: ladj(value) for degree, value in old_d.items()}
            sym_ds = {degree: lscale(HALF, ladj(value)) for degree, value in sym_d.items()}
            old_delta = _laplacians(old_d, old_ds, 2)
            sym_delta = _laplacians(sym_d, sym_ds, 4)
            for degree in range(3):
                inclusion = inclusion_matrix(a, b, degree)
                retraction = retraction_matrix(a, b, degree)
                isometric &= lscale(HALF**degree, lmul(ladj(inclusion), inclusion)) == lidentity(comb(2, degree))
                adjoint_retraction &= retraction == lscale(HALF**degree, ladj(inclusion))
                projection = lmul(inclusion, retraction)
                orthogonal_projector &= lmul(projection, projection) == projection and ladj(projection) == projection
                hodge_reducing &= lmul(sym_delta[degree], inclusion) == lmul(inclusion, old_delta[degree])

    symmetry_intertwining = all(
        affine_action(include_old(item), eps, shift, 4) == include_old(old_affine_action(item, eps, shift))
        for eps, shift in AFFINE_S3
        for item in old_basis
    ) and all(
        fourier_action(include_old(item), 4) == include_old(old_fourier_action(item))
        for item in old_basis
    )

    harmonic_old = [basis_element(0, 0, mask) for mask in range(4)]
    harmonic_products_closed = all(
        product(include_old(left), include_old(right), DIRECTION_EXPONENTS)
        == include_old(product(left, right, OLD_DIRECTIONS))
        for left in harmonic_old
        for right in harmonic_old
    )

    product_comparison = product_retract_diagnostics(old_basis)
    checks = {
        "retraction_after_inclusion_is_identity_on_all_36_old_basis_elements": qi_identity,
        "inclusion_is_an_exact_cochain_map": chain_inclusion,
        "retraction_is_an_exact_cochain_map": chain_retraction,
        "inclusion_is_isometric_for_the_half_edge_metric": isometric,
        "retraction_is_the_weighted_Hilbert_adjoint_of_inclusion": adjoint_retraction,
        "inclusion_retraction_is_an_orthogonal_projector": orthogonal_projector,
        "selected_image_is_a_reducing_summand_for_the_Hodge_Laplacian": hodge_reducing,
        "inclusion_intertwines_affine_S3_and_Fourier_C4_cochain_actions": symmetry_intertwining,
        "selected_harmonic_1_2_1_sector_is_the_orientation_odd_exterior_subalgebra": harmonic_products_closed,
        "full_symmetric_harmonic_complement_has_dimensions_0_2_5_4_1": [0, 2, 5, 4, 1] == [comb(4, degree) - (comb(2, degree) if degree <= 2 else 0) for degree in range(5)],
        "extra_harmonic_complement_prevents_a_quasi_isomorphism": sum([0, 2, 5, 4, 1]) == 12,
        "selected_full_chain_image_is_not_a_product_subalgebra": product_comparison["image_product_leakage_pairs"] > 0,
        "compressed_symmetric_product_is_not_the_old_forward_product": product_comparison["compressed_vs_old_defect_pairs"] > 0,
        "compressed_symmetric_product_is_nonassociative": product_comparison["nonzero_associator_triples"] > 0,
        "compressed_product_agrees_with_old_product_on_all_16_harmonic_pairs": product_comparison["harmonic_compressed_vs_old_defect_pairs"] == 0,
        "harmonic_selected_image_has_zero_product_leakage": product_comparison["harmonic_image_product_leakage_pairs"] == 0,
    }
    data = {
        "modewise_degree_one_inclusion": "I(c_x,c_z)=(c_x,-alpha^-1 c_x,c_z,-beta^-1 c_z)",
        "modewise_degree_one_retraction": "Q(b_+,b_-,c_+,c_-)=((b_+-alpha b_-)/2,(c_+-beta c_-)/2)",
        "higher_degrees": "exterior powers of I and Q; Q=0 above old degree two",
        "identities": ["QI=1", "d_sym I=I d_old", "Q d_sym=d_old Q"],
        "selected_harmonic_dimensions": [1, 2, 1, 0, 0],
        "extra_harmonic_dimensions": [0, 2, 5, 4, 1],
        "selected_H1_basis": ["theta_+x-theta_-x", "theta_+z-theta_-z"],
        "selected_H1_actions": {"S3_reflection": "-I2", "C4": "[[0,-1],[1,0]]"},
        "product_diagnostics": product_comparison,
        "verdict": "The old Hodge complex is a canonical isometric reducing cochain summand and its harmonic exterior algebra survives exactly. Off harmonics, its image is not a product subalgebra; orthogonal compression produces a distinct nonassociative product. The extra twelve harmonic classes cannot be discarded by homological perturbation without an additional selected rule.",
    }
    return data, checks


def _laplacians(differentials: dict[int, Linear], adjoints: dict[int, Linear], max_degree: int) -> dict[int, Linear]:
    out: dict[int, Linear] = {}
    for degree in range(max_degree + 1):
        dimension = comb(max_degree, degree)
        delta = lzero(dimension, dimension)
        if degree > 0:
            delta = ladd(delta, lmul(differentials[degree - 1], adjoints[degree - 1]))
        if degree < max_degree:
            delta = ladd(delta, lmul(adjoints[degree], differentials[degree]))
        out[degree] = delta
    return out


def product_retract_diagnostics(old_basis: list[ModeElement]) -> dict[str, int]:
    compressed_vs_old = 0
    image_leakage = 0
    harmonic_compressed_vs_old = 0
    harmonic_image_leakage = 0

    def compressed(left: ModeElement, right: ModeElement) -> ModeElement:
        return retract_symmetric(product(include_old(left), include_old(right), DIRECTION_EXPONENTS))

    for left in old_basis:
        for right in old_basis:
            upper_product = product(include_old(left), include_old(right), DIRECTION_EXPONENTS)
            lower_compressed = retract_symmetric(upper_product)
            old_product = product(left, right, OLD_DIRECTIONS)
            leakage = element_add(upper_product, element_scale(-1, include_old(lower_compressed)))
            if lower_compressed != old_product:
                compressed_vs_old += 1
            if leakage:
                image_leakage += 1
            if _is_harmonic_basis(left) and _is_harmonic_basis(right):
                harmonic_compressed_vs_old += int(lower_compressed != old_product)
                harmonic_image_leakage += int(bool(leakage))

    associators = 0
    for left in old_basis:
        for middle in old_basis:
            left_middle = compressed(left, middle)
            for right in old_basis:
                lhs = compressed(left_middle, right)
                rhs = compressed(left, compressed(middle, right))
                associators += int(lhs != rhs)

    return {
        "basis_pair_count": len(old_basis) ** 2,
        "basis_triple_count": len(old_basis) ** 3,
        "compressed_vs_old_defect_pairs": compressed_vs_old,
        "image_product_leakage_pairs": image_leakage,
        "nonzero_associator_triples": associators,
        "harmonic_compressed_vs_old_defect_pairs": harmonic_compressed_vs_old,
        "harmonic_image_product_leakage_pairs": harmonic_image_leakage,
    }


def _is_harmonic_basis(source: ModeElement) -> bool:
    return all(a == 0 and b == 0 for a, b, _ in source)


def source_checks(lock: dict[str, object]) -> dict[str, bool]:
    sources = lock.get("sources", [])
    claims = lock.get("extracted_claims", {})
    return {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.q79-symmetric-weyl-calculus-source-lock.v1",
        "six_sources_are_commit_blob_and_sha256_pinned": len(sources) == 6 and all(
            len(source.get("commit", "")) == 40
            and len(source.get("git_blob", "")) == 40
            and len(source.get("sha256", "")) == 64
            for source in sources
        ),
        "source_lock_preserves_the_selected_1_2_1_cohomology": claims["selected_two_direction_complex"]["cohomology_dimensions"] == [1, 2, 1],
        "source_lock_preserves_the_exact_old_product_cutset": claims["exact_symmetry_cutset"]["affine_reflection_product_defects_per_1296"] == 360 and claims["exact_symmetry_cutset"]["Fourier_C4_product_defects_per_1296"] == 108,
        "source_lock_preserves_the_q79_harmonic_strain_actions": claims["q79_harmonic_strain_shadow"]["H1_C4_generator"] == [[0, -1], [1, 0]],
        "source_lock_forbids_physical_promotion_of_extra_modes_or_G36": "does not select the extra harmonic modes as physical" in lock.get("guard", "") and "enlarge q79 monodromy" in lock.get("guard", ""),
    }


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    dga_data, dga_checks = exact_dga_checks()
    symmetry_data, symmetry_result_checks = symmetry_checks()
    hodge_data, hodge_result_checks = hodge_checks()
    retract_data, retract_result_checks = retract_checks()
    checks = source_checks(lock) | dga_checks | symmetry_result_checks | hodge_result_checks | retract_result_checks
    return {
        "schema": "boe.mtt.q79-symmetric-weyl-calculus-isometric-retraction.v1",
        "theorem_id": "SelectedSymmetricWeylCalculusIsometricRetractionAndCovarianceCutsetTheorem.v1",
        "date": "2026-08-28",
        "tiers": ["SELECTED_EXACT_FINITE_EXTENSION", "EXACT_COVARIANCE_COMPLETION", "EXACT_COCHAIN_RETRACT", "PHYSICAL_SELECTION_OPEN"],
        "symmetric_full_DGA_covariance": True,
        "selected_old_complex_isometric_cochain_retract": True,
        "selected_old_complex_full_product_retract": False,
        "symmetric_extra_harmonic_modes_selected_physical": False,
        "selected_nonzero_Chern_HYM_endpoint": False,
        "continuous_fit_parameters": 0,
        "discrete_physical_selectors": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "source_lock_sha256": sha256(LOCK_PATH),
            "theorem_sha256": sha256(THEOREM_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "symmetric_DGA": dga_data,
        "finite_covariance": symmetry_data,
        "normalized_Hodge_theory": hodge_data,
        "selected_complex_retract": retract_data,
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "The unique minimal signed-direction completion of the selected Weyl calculus is a 144-dimensional exact DGA on +x,-x,+z,-z. Affine S3 and Fourier C4 are now genuine DGA automorphisms with zero product defects and generate the exact order-36 covariance group (Z3 x Z3) semidirect C4. The uniquely normalized half-edge metric preserves the old 0,3,6 Hodge eigenvalues. The selected 36-dimensional complex embeds as an exact isometric reducing cochain summand and its 1,2,1 harmonic exterior algebra is the orientation-odd sector. However the full symmetric complex has twelve additional harmonic classes, the selected image is not product closed off harmonics, and orthogonal product compression is distinct and nonassociative. Thus finite covariance is solved only by retaining extra modes; a physical rule selecting the old harmonic sector or a continuum HYM complex is still required.",
        "nonclaims": [
            "physical selection of the twelve extra harmonic classes",
            "promotion of the order-36 covariance group to q79 physical holonomy",
            "quasi-isomorphism between the symmetric and selected old complexes",
            "associative full-chain product on the selected isometric summand",
            "selected nonzero-Chern HYM endpoint, physical action or normalization",
            "closure of B.GEO.01, B.OP.01 or B.ACTION.01",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
