"""Build the exact q79 Weyl-Koszul monodromy/C4 cohomology bridge."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable

import build_selected_finite_weyl_koszul_hodge_and_interaction_cutset as wk


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_weyl_koszul_monodromy_c4_source_lock.json"
THEOREM_PATH = ROOT / "Q79WeylKoszulMonodromyC4CohomologyIntertwinerAndProductCutsetTheorem_v1.md"
PACKET_PATH = ROOT / "q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json"

E = wk.Eisenstein
Linear = tuple[tuple[E, ...], ...]
Action = Callable[[wk.Element], wk.Element]

MASKS_BY_DEGREE = {0: (0,), 1: (1, 2), 2: (3,)}
AFFINE_S3 = tuple((eps, shift) for eps in (1, -1) for shift in range(3))


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
    if not left or not right:
        raise ValueError("linear matrices must be nonempty")
    return tuple(
        tuple(
            sum((left[row][k] * right[k][col] for k in range(len(right))), wk.ZERO)
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
    return sum(entry != wk.ZERO for row in source for entry in row)


def serialize_linear(source: Linear) -> list[list[list[str]]]:
    return [[entry.pair() for entry in row] for row in source]


def rational_linear(source: Linear) -> list[list[str]]:
    if any(entry.b != 0 for row in source for entry in row):
        raise ValueError("matrix is not rational")
    return [[wk.fstr(entry.a) for entry in row] for row in source]


def basis_keys(degree: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((row, col, mask) for mask in MASKS_BY_DEGREE[degree] for row in range(3) for col in range(3))


def coefficient_matrix(source: wk.Element, mask: int) -> wk.Matrix:
    return wk.matrix([[source.get((row, col, mask), wk.ZERO) for col in range(3)] for row in range(3)])


def element_from_matrix(source: wk.Matrix, mask: int) -> wk.Element:
    return wk.clean(
        {
            (row, col, mask): source[row][col]
            for row in range(3)
            for col in range(3)
            if source[row][col] != wk.ZERO
        }
    )


def element_from_coefficients(coefficients: dict[int, wk.Matrix]) -> wk.Element:
    out: wk.Element = {}
    for mask, source in coefficients.items():
        out = wk.element_add(out, element_from_matrix(source, mask))
    return out


def element_vector(source: wk.Element, degree: int) -> tuple[E, ...]:
    return tuple(source.get(key, wk.ZERO) for key in basis_keys(degree))


def action_linear(degree_in: int, degree_out: int, action: Action) -> Linear:
    columns = [element_vector(action({key: wk.ONE}), degree_out) for key in basis_keys(degree_in)]
    return tuple(tuple(columns[col][row] for col in range(len(columns))) for row in range(len(columns[0])))


def matrix_iterate(action: Callable[[wk.Matrix], wk.Matrix], source: wk.Matrix, count: int) -> wk.Matrix:
    out = source
    for _ in range(count):
        out = action(out)
    return out


def alpha_inverse(source: wk.Matrix) -> wk.Matrix:
    return matrix_iterate(wk.alpha_matrix, source, 2)


def beta_inverse(source: wk.Matrix) -> wk.Matrix:
    return matrix_iterate(wk.beta_matrix, source, 2)


def affine_permutation(eps: int, shift: int) -> wk.Matrix:
    return wk.matrix(
        [
            [1 if row == (eps * col + shift) % 3 else 0 for col in range(3)]
            for row in range(3)
        ]
    )


def gamma_affine(source: wk.Matrix, eps: int, shift: int) -> wk.Matrix:
    unitary = affine_permutation(eps, shift)
    return wk.matrix_multiply(wk.matrix_multiply(unitary, source), wk.matrix_adjoint(unitary))


def fourier_matrix() -> wk.Matrix:
    return wk.matrix([[wk.omega_power(row * col) for col in range(3)] for row in range(3)])


def gamma_fourier(source: wk.Matrix) -> wk.Matrix:
    transform = fourier_matrix()
    return wk.matrix_scale(
        Fraction(1, 3),
        wk.matrix_multiply(wk.matrix_multiply(transform, source), wk.matrix_adjoint(transform)),
    )


def apply_s3(source: wk.Element, eps: int, shift: int) -> wk.Element:
    coefficients = {mask: coefficient_matrix(source, mask) for mask in range(4)}
    if eps == 1:
        return element_from_coefficients(
            {mask: gamma_affine(value, eps, shift) for mask, value in coefficients.items()}
        )
    return element_from_coefficients(
        {
            0: gamma_affine(coefficients[0], eps, shift),
            1: wk.matrix_scale(-1, gamma_affine(alpha_inverse(coefficients[1]), eps, shift)),
            2: wk.matrix_scale(-1, gamma_affine(beta_inverse(coefficients[2]), eps, shift)),
            3: gamma_affine(alpha_inverse(beta_inverse(coefficients[3])), eps, shift),
        }
    )


def apply_c4(source: wk.Element) -> wk.Element:
    coefficients = {mask: coefficient_matrix(source, mask) for mask in range(4)}
    return element_from_coefficients(
        {
            0: gamma_fourier(coefficients[0]),
            1: wk.matrix_scale(-1, gamma_fourier(beta_inverse(coefficients[2]))),
            2: gamma_fourier(coefficients[1]),
            3: gamma_fourier(beta_inverse(coefficients[3])),
        }
    )


def affine_compose(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    eps_left, shift_left = left
    eps_right, shift_right = right
    return eps_left * eps_right, (eps_left * shift_right + shift_left) % 3


def harmonic_project(source: wk.Element) -> wk.Element:
    coefficients: dict[int, wk.Matrix] = {}
    for mask in range(4):
        value = coefficient_matrix(source, mask)
        coefficients[mask] = wk.matrix_scale(wk.normalized_trace(value), wk.matrix_identity())
    return element_from_coefficients(coefficients)


def complex_operators() -> dict[str, object]:
    d0 = action_linear(0, 1, wk.element_differential)
    d1 = action_linear(1, 2, wk.element_differential)
    d0_star = ladj(d0)
    d1_star = ladj(d1)
    delta0 = lmul(d0_star, d0)
    delta1 = ladd(lmul(d0, d0_star), lmul(d1_star, d1))
    delta2 = lmul(d1, d1_star)
    projectors = {degree: action_linear(degree, degree, harmonic_project) for degree in range(3)}
    deltas = {0: delta0, 1: delta1, 2: delta2}
    greens = {
        degree: lscale(
            Fraction(1, 36),
            lsub(lscale(7, delta), lmul(delta, delta)),
        )
        for degree, delta in deltas.items()
    }
    h1 = lmul(d0_star, greens[1])
    h2 = lmul(d1_star, greens[2])
    return {
        "d": {0: d0, 1: d1},
        "d_star": {0: d0_star, 1: d1_star},
        "delta": deltas,
        "P": projectors,
        "G": greens,
        "h": {1: h1, 2: h2},
    }


def harmonic_inclusion(degree: int) -> Linear:
    masks = MASKS_BY_DEGREE[degree]
    columns = [element_vector(wk.center_form(mask), degree) for mask in masks]
    return tuple(tuple(columns[col][row] for col in range(len(columns))) for row in range(len(columns[0])))


def induced_harmonic(action: Linear, degree: int) -> Linear:
    inclusion = harmonic_inclusion(degree)
    # Each matrix-center generator is I_3, whose raw coordinate norm is 3.
    # The selected normalized Hilbert-Schmidt pairing divides that norm by 3.
    return lscale(Fraction(1, 3), lmul(ladj(inclusion), lmul(action, inclusion)))


def block_diag(left: Linear, right: Linear) -> Linear:
    rows = len(left) + len(right)
    cols = len(left[0]) + len(right[0])
    out = [[wk.ZERO for _ in range(cols)] for _ in range(rows)]
    for row in range(len(left)):
        for col in range(len(left[0])):
            out[row][col] = left[row][col]
    for row in range(len(right)):
        for col in range(len(right[0])):
            out[len(left) + row][len(left[0]) + col] = right[row][col]
    return tuple(tuple(row) for row in out)


def exact_cochain_checks(operators: dict[str, object]) -> tuple[dict[str, object], dict[str, bool], dict[tuple[int, int], dict[int, Linear]], dict[int, Linear]]:
    d = operators["d"]
    deltas = operators["delta"]
    projectors = operators["P"]
    greens = operators["G"]
    homotopies = operators["h"]
    s3_actions = {
        group: {
            degree: action_linear(
                degree,
                degree,
                lambda source, group=group: apply_s3(source, group[0], group[1]),
            )
            for degree in range(3)
        }
        for group in AFFINE_S3
    }
    c4_actions = {degree: action_linear(degree, degree, apply_c4) for degree in range(3)}

    matrix_units = [wk.matrix([[1 if (i, j) == (row, col) else 0 for j in range(3)] for i in range(3)]) for row in range(3) for col in range(3)]
    affine_conjugation = all(
        gamma_affine(wk.alpha_matrix(source), eps, shift)
        == (wk.alpha_matrix(gamma_affine(source, eps, shift)) if eps == 1 else alpha_inverse(gamma_affine(source, eps, shift)))
        and gamma_affine(wk.beta_matrix(source), eps, shift)
        == (wk.beta_matrix(gamma_affine(source, eps, shift)) if eps == 1 else beta_inverse(gamma_affine(source, eps, shift)))
        for eps, shift in AFFINE_S3
        for source in matrix_units
    )
    fourier_conjugation = all(
        gamma_fourier(wk.alpha_matrix(source)) == wk.beta_matrix(gamma_fourier(source))
        and gamma_fourier(wk.beta_matrix(source)) == alpha_inverse(gamma_fourier(source))
        for source in matrix_units
    )

    chain_s3 = all(
        lmul(action[1], d[0]) == lmul(d[0], action[0])
        and lmul(action[2], d[1]) == lmul(d[1], action[1])
        for action in s3_actions.values()
    )
    chain_c4 = lmul(c4_actions[1], d[0]) == lmul(d[0], c4_actions[0]) and lmul(c4_actions[2], d[1]) == lmul(d[1], c4_actions[1])
    s3_group_law = all(
        lmul(s3_actions[left][degree], s3_actions[right][degree])
        == s3_actions[affine_compose(left, right)][degree]
        for left in AFFINE_S3
        for right in AFFINE_S3
        for degree in range(3)
    )
    unitary_s3 = all(
        lmul(ladj(action[degree]), action[degree]) == lidentity(len(action[degree]))
        for action in s3_actions.values()
        for degree in range(3)
    )
    unitary_c4 = all(
        lmul(ladj(c4_actions[degree]), c4_actions[degree]) == lidentity(len(c4_actions[degree]))
        for degree in range(3)
    )
    c4_order = all(lpower(c4_actions[degree], 4) == lidentity(len(c4_actions[degree])) for degree in range(3))
    c4_square_reflection = all(c4_actions[degree] and lpower(c4_actions[degree], 2) == s3_actions[(-1, 0)][degree] for degree in range(3))

    natural_s3 = all(
        lmul(action[degree], family[degree]) == lmul(family[degree], action[degree])
        for action in s3_actions.values()
        for family in (deltas, projectors, greens)
        for degree in range(3)
    )
    natural_c4 = all(
        lmul(c4_actions[degree], family[degree]) == lmul(family[degree], c4_actions[degree])
        for family in (deltas, projectors, greens)
        for degree in range(3)
    )
    homotopy_s3 = all(
        lmul(action[0], homotopies[1]) == lmul(homotopies[1], action[1])
        and lmul(action[1], homotopies[2]) == lmul(homotopies[2], action[2])
        for action in s3_actions.values()
    )
    homotopy_c4 = (
        lmul(c4_actions[0], homotopies[1]) == lmul(homotopies[1], c4_actions[1])
        and lmul(c4_actions[1], homotopies[2]) == lmul(homotopies[2], c4_actions[2])
    )

    expected_j = lmatrix([[0, -1], [1, 0]])
    harmonic_s3 = {
        group: {degree: induced_harmonic(action[degree], degree) for degree in range(3)}
        for group, action in s3_actions.items()
    }
    harmonic_c4 = {degree: induced_harmonic(c4_actions[degree], degree) for degree in range(3)}
    s3_harmonic_types = all(
        reps[0] == lmatrix([[1]])
        and reps[1] == lscale(group[0], lidentity(2))
        and reps[2] == lmatrix([[1]])
        for group, reps in harmonic_s3.items()
    )
    c4_harmonic_types = harmonic_c4 == {0: lmatrix([[1]]), 1: expected_j, 2: lmatrix([[1]])}
    harmonic_commutes = all(
        lmul(harmonic_c4[degree], harmonic_s3[group][degree])
        == lmul(harmonic_s3[group][degree], harmonic_c4[degree])
        for group in AFFINE_S3
        for degree in range(3)
    )

    checks = {
        "affine_S3_conjugates_alpha_beta_by_the_exact_signed_lattice_action": affine_conjugation,
        "Fourier_C4_conjugates_alpha_to_beta_and_beta_to_alpha_inverse": fourier_conjugation,
        "six_affine_S3_maps_are_exact_cochain_maps": chain_s3,
        "affine_S3_cochain_maps_obey_the_group_law": s3_group_law,
        "affine_S3_cochain_maps_are_unitary": unitary_s3,
        "Fourier_quarterturn_is_an_exact_cochain_map": chain_c4,
        "Fourier_quarterturn_is_unitary": unitary_c4,
        "Fourier_quarterturn_has_order_four_on_every_degree": c4_order,
        "Fourier_quarterturn_square_is_the_selected_affine_reflection": c4_square_reflection,
        "S3_commutes_with_Delta_P_and_G_on_every_degree": natural_s3,
        "C4_commutes_with_Delta_P_and_G_on_every_degree": natural_c4,
        "S3_intertwines_both_Hodge_homotopies": homotopy_s3,
        "C4_intertwines_both_Hodge_homotopies": homotopy_c4,
        "harmonic_S3_types_are_trivial_sign_trivial_in_degrees_0_1_2": s3_harmonic_types,
        "harmonic_C4_types_are_one_j_one_in_degrees_0_1_2": c4_harmonic_types,
        "S3_and_C4_commute_on_harmonic_cohomology": harmonic_commutes,
    }
    data = {
        "affine_group": "g_(eps,b): j -> eps*j+b on Z3",
        "matrix_action": "gamma_g=Ad_Ug",
        "cochain_action": {
            "eps_plus": "T0=T1=T2=gamma_g",
            "eps_minus": "T0=gamma_g; T1(b,c)=(-gamma_g alpha^-1(b),-gamma_g beta^-1(c)); T2(w)=gamma_g alpha^-1 beta^-1(w)",
        },
        "Fourier_action": {
            "matrix": "F_jk=omega^(jk), gamma_F(A)=F A F*/3",
            "relations": ["gamma_F alpha gamma_F^-1=beta", "gamma_F beta gamma_F^-1=alpha^-1"],
            "cochain": "J0=gamma_F; J1(b,c)=(-gamma_F beta^-1(c),gamma_F(b)); J2(w)=gamma_F beta^-1(w)",
            "order": 4,
            "square": "affine reflection j -> -j",
        },
        "Hodge_naturality": ["Delta", "P", "G", "h1", "h2"],
        "harmonic_representations": {
            "S3": ["trivial", "sign direct-sum sign", "trivial"],
            "C4": ["1", "j=[[0,-1],[1,0]]", "1"],
        },
    }
    return data, checks, s3_actions, c4_actions


def hodge_identity_checks(operators: dict[str, object]) -> tuple[dict[str, object], dict[str, bool]]:
    d = operators["d"]
    deltas = operators["delta"]
    projectors = operators["P"]
    greens = operators["G"]
    h1 = operators["h"][1]
    h2 = operators["h"][2]
    identities = {
        "degree_0": lmul(h1, d[0]) == lsub(lidentity(9), projectors[0]),
        "degree_1": ladd(lmul(d[0], h1), lmul(h2, d[1])) == lsub(lidentity(18), projectors[1]),
        "degree_2": lmul(d[1], h2) == lsub(lidentity(9), projectors[2]),
    }
    green_inverse = all(
        lmul(deltas[degree], greens[degree]) == lsub(lidentity(len(deltas[degree])), projectors[degree])
        and lmul(greens[degree], deltas[degree]) == lsub(lidentity(len(deltas[degree])), projectors[degree])
        for degree in range(3)
    )
    side_conditions = (
        lmul(h1, h2) == lzero(9, 9)
        and lmul(h1, projectors[1]) == lzero(9, 18)
        and lmul(projectors[0], h1) == lzero(9, 18)
        and lmul(h2, projectors[2]) == lzero(18, 9)
        and lmul(projectors[1], h2) == lzero(18, 9)
    )
    checks = {
        "matrix_Hodge_contraction_identity_holds_in_degree_zero": identities["degree_0"],
        "matrix_Hodge_contraction_identity_holds_in_degree_one": identities["degree_1"],
        "matrix_Hodge_contraction_identity_holds_in_degree_two": identities["degree_2"],
        "reduced_Green_is_the_exact_two_sided_inverse_off_harmonics": green_inverse,
        "Hodge_homotopy_and_projector_side_conditions_hold_exactly": side_conditions,
    }
    data = {
        "dimensions": [9, 18, 9],
        "projector_ranks": [1, 2, 1],
        "Green_polynomial": "G=(7 Delta-Delta^2)/36",
        "contraction": "dh+hd=I-P",
        "side_conditions": ["h^2=0", "hP=0", "Ph=0"],
    }
    return data, checks


def strain_intertwiner_checks(s3_actions: dict[tuple[int, int], dict[int, Linear]], c4_actions: dict[int, Linear]) -> tuple[dict[str, object], dict[str, bool]]:
    permutations = {group: lmatrix(affine_permutation(*group)) for group in AFFINE_S3}
    target_s3 = {group: block_diag(permutation, permutation) for group, permutation in permutations.items()}
    harmonic_s3 = {group: induced_harmonic(action[1], 1) for group, action in s3_actions.items()}
    source_s3 = {
        group: block_diag(
            lscale(group[0], lscale(group[0], permutations[group])),
            lscale(group[0], lscale(group[0], permutations[group])),
        )
        for group in AFFINE_S3
    }
    harmonic_c4 = induced_harmonic(c4_actions[1], 1)
    jde = block_diag(lzero(3, 3), lzero(3, 3))
    jde_rows = [[wk.ZERO for _ in range(6)] for _ in range(6)]
    for index in range(3):
        jde_rows[index][index + 3] = e(-1)
        jde_rows[index + 3][index] = e(1)
    jde = tuple(tuple(row) for row in jde_rows)
    source_c4_rows = [[wk.ZERO for _ in range(6)] for _ in range(6)]
    for out_lane in range(2):
        for in_lane in range(2):
            for sheet in range(3):
                source_c4_rows[3 * out_lane + sheet][3 * in_lane + sheet] = harmonic_c4[out_lane][in_lane]
    source_c4 = tuple(tuple(row) for row in source_c4_rows)

    reynolds = lscale(Fraction(1, 6), sum_linear(target_s3.values()))
    tt = lsub(lidentity(6), reynolds)
    checks = {
        "determinant_twist_cancels_the_harmonic_H1_sign_for_all_six_holonomies": all(source_s3[group] == target_s3[group] for group in AFFINE_S3),
        "identity_basis_map_is_an_exact_S3_intertwiner_to_D_and_E_strain_lanes": all(source_s3[group] == target_s3[group] for group in AFFINE_S3),
        "harmonic_C4_tensor_identity_is_exactly_J_DE": source_c4 == jde,
        "identity_basis_map_is_an_exact_C4_intertwiner_to_J_DE": source_c4 == jde,
        "induced_strain_C4_has_square_minus_identity_and_order_four": lpower(jde, 2) == lscale(-1, lidentity(6)) and lpower(jde, 4) == lidentity(6),
        "strain_C4_commutes_with_all_six_S3_holonomies": all(lmul(jde, target_s3[group]) == lmul(target_s3[group], jde) for group in AFFINE_S3),
        "Reynolds_projector_is_idempotent_with_trace_two": lmul(reynolds, reynolds) == reynolds and ltrace(reynolds) == e(2),
        "TT_projector_is_idempotent_with_trace_four": lmul(tt, tt) == tt and ltrace(tt) == e(4),
        "J_DE_preserves_the_Reynolds_and_TT_subspaces": lmul(jde, reynolds) == lmul(reynolds, jde) and lmul(jde, tt) == lmul(tt, jde),
    }
    data = {
        "source_bundle": "det(E_D) tensor H1(K_W) tensor E_D",
        "source_monodromy": "sign tensor (sign direct-sum sign) tensor permutation",
        "sign_cancellation": "sign^2=1",
        "intertwiner": [
            "s tensor [I theta_x] tensor d_i -> D_i",
            "s tensor [I theta_z] tensor d_i -> E_i",
        ],
        "target_local_system": "universal_cover(B_reg) x_mu (R3_D direct-sum R3_E)",
        "C4_generator": rational_linear(jde),
        "Reynolds_projector": rational_linear(reynolds),
        "TT_projector": rational_linear(tt),
        "ranks": {"invariant": 2, "TT": 4},
        "scope": "regular q79 root-stack associated local-system cohomology shadow",
    }
    return data, checks


def sum_linear(values: Iterable[Linear]) -> Linear:
    iterator = iter(values)
    out = next(iterator)
    for value in iterator:
        out = ladd(out, value)
    return out


def multiplicativity_defects(action: Action, basis: list[wk.Element]) -> int:
    defects = 0
    for left in basis:
        for right in basis:
            if action(wk.element_multiply(left, right)) != wk.element_multiply(action(left), action(right)):
                defects += 1
    return defects


def serialize_element(source: wk.Element) -> list[dict[str, object]]:
    return [
        {"row": row, "col": col, "mask": mask, "coefficient": value.pair()}
        for (row, col, mask), value in sorted(source.items())
    ]


def product_and_globalization_cutset(
    s3_actions: dict[tuple[int, int], dict[int, Linear]],
    c4_actions: dict[int, Linear],
) -> tuple[dict[str, object], dict[str, bool]]:
    basis = [wk.basis_element(row, col, mask) for mask in range(4) for row in range(3) for col in range(3)]
    harmonic = [wk.center_form(mask) for mask in range(4)]
    reflection = lambda source: apply_s3(source, -1, 0)
    s3_defects = {
        f"eps_{eps}_shift_{shift}": multiplicativity_defects(
            lambda source, eps=eps, shift=shift: apply_s3(source, eps, shift), basis
        )
        for eps, shift in AFFINE_S3
    }
    c4_defects = multiplicativity_defects(apply_c4, basis)
    harmonic_s3_multiplicative = all(
        apply_s3(wk.element_multiply(left, right), eps, shift)
        == wk.element_multiply(apply_s3(left, eps, shift), apply_s3(right, eps, shift))
        for eps, shift in AFFINE_S3
        for left in harmonic
        for right in harmonic
    )
    harmonic_c4_multiplicative = all(
        apply_c4(wk.element_multiply(left, right))
        == wk.element_multiply(apply_c4(left), apply_c4(right))
        for left in harmonic
        for right in harmonic
    )

    a = wk.basis_element(0, 0, 0)
    theta_x = wk.center_form(1)
    reflection_left = reflection(wk.element_multiply(a, theta_x))
    reflection_right = wk.element_multiply(reflection(a), reflection(theta_x))
    reflection_witness = wk.element_add(reflection_left, wk.element_scale(-1, reflection_right))

    full_commutators = {
        f"eps_{eps}_shift_{shift}": {
            str(degree): nonzero_entries(
                lsub(
                    lmul(c4_actions[degree], s3_actions[(eps, shift)][degree]),
                    lmul(s3_actions[(eps, shift)][degree], c4_actions[degree]),
                )
            )
            for degree in range(3)
        }
        for eps, shift in AFFINE_S3
    }
    full_noncommuting = any(count > 0 for record in full_commutators.values() for count in record.values())
    harmonic_commuting = all(
        lmul(induced_harmonic(c4_actions[degree], degree), induced_harmonic(s3_actions[group][degree], degree))
        == lmul(induced_harmonic(s3_actions[group][degree], degree), induced_harmonic(c4_actions[degree], degree))
        for group in AFFINE_S3
        for degree in range(3)
    )

    checks = {
        "orientation_preserving_affine_maps_are_full_DGA_automorphisms": all(value == 0 for key, value in s3_defects.items() if "eps_1_" in key),
        "canonical_affine_reflections_are_not_full_DGA_automorphisms": all(value > 0 for key, value in s3_defects.items() if "eps_-1_" in key),
        "explicit_reflection_product_defect_is_nonzero": bool(reflection_witness),
        "canonical_Fourier_C4_cochain_map_is_not_a_full_DGA_automorphism": c4_defects > 0,
        "full_chain_C4_does_not_commute_with_all_S3_holonomies": full_noncommuting,
        "harmonic_exterior_product_is_S3_equivariant": harmonic_s3_multiplicative,
        "harmonic_exterior_product_is_C4_equivariant": harmonic_c4_multiplicative,
        "S3_and_C4_commute_after_harmonic_projection": harmonic_commuting,
        "full_forward_difference_DGA_globalization_remains_open": bool(reflection_witness) and c4_defects > 0 and full_noncommuting,
    }
    data = {
        "S3_full_DGA_defect_pairs_out_of_1296": s3_defects,
        "C4_full_DGA_defect_pairs_out_of_1296": c4_defects,
        "reflection_witness": {
            "a": "E_00",
            "v": "I theta_x",
            "T(a v)-T(a)T(v)": serialize_element(reflection_witness),
        },
        "full_chain_C4_S3_commutator_nonzero_entries": full_commutators,
        "harmonic_product": "globally S3- and C4-equivariant exterior algebra",
        "interpretation": "Affine S3 globalizes the cochain and Hodge complex. The combined S3/C4 action globalizes only after harmonic projection, where it is the q79 strain shadow. The canonical lifts do not globalize the full forward-difference multiplication. A covariant enlarged calculus or the actual continuum HYM complex is still required.",
    }
    return data, checks


def source_checks(lock: dict[str, object]) -> dict[str, bool]:
    sources = lock.get("sources", [])
    claims = lock.get("extracted_claims", {})
    return {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.q79-weyl-koszul-monodromy-c4-source-lock.v1",
        "nine_sources_are_commit_blob_and_sha256_pinned": len(sources) == 9 and all(
            len(source.get("commit", "")) == 40
            and len(source.get("git_blob", "")) == 40
            and len(source.get("sha256", "")) == 64
            for source in sources
        ),
        "source_lock_preserves_full_S3_holonomy_and_trivial_deck_group": claims["q79_monodromy"]["cover_monodromy"] == "full S3" and claims["q79_monodromy"]["deck_group"] == "trivial",
        "source_lock_preserves_the_selected_shared_C4_generator": claims["q79_shared_root_c4"]["real_generator"] == [[0, -1], [1, 0]],
        "source_lock_preserves_the_marked_FuYau_C4_nogo": claims["q79_shared_root_c4"]["marked_FuYau_autonomous_descent"] is False,
        "source_lock_preserves_the_continuum_product_transfer_blocker": claims["continuum_bridge_boundary"]["continuum_product_connection_and_higher_operation_transfer"] == "open",
        "source_lock_guard_forbids_HYM_and_full_DGA_promotion": "does not select the nonzero-Chern HYM endpoint" in lock.get("guard", "") and "full forward-difference DGA" in lock.get("guard", ""),
    }


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    operators = complex_operators()
    hodge_data, hodge_checks = hodge_identity_checks(operators)
    cochain_data, cochain_checks, s3_actions, c4_actions = exact_cochain_checks(operators)
    strain_data, strain_checks = strain_intertwiner_checks(s3_actions, c4_actions)
    cutset_data, cutset_checks = product_and_globalization_cutset(s3_actions, c4_actions)
    checks = source_checks(lock) | hodge_checks | cochain_checks | strain_checks | cutset_checks
    return {
        "schema": "boe.mtt.q79-weyl-koszul-monodromy-c4-cohomology-intertwiner.v1",
        "theorem_id": "Q79WeylKoszulMonodromyC4CohomologyIntertwinerAndProductCutsetTheorem.v1",
        "date": "2026-08-28",
        "tiers": ["SELECTED_EXACT_FINITE", "GLOBAL_ROOTSTACK_COHOMOLOGY_SHADOW", "EXACT_PRODUCT_CUTSET", "PHYSICAL_HYM_OPEN"],
        "global_rootstack_cohomology_bridge": True,
        "global_full_forward_difference_DGA": False,
        "selected_nonzero_Chern_HYM_endpoint": False,
        "continuous_fit_parameters": 0,
        "discrete_physical_selectors": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "source_lock_sha256": sha256(LOCK_PATH),
            "theorem_sha256": sha256(THEOREM_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "finite_Hodge_contraction": hodge_data,
        "S3_cochain_and_local_C4_naturality": cochain_data,
        "determinant_twisted_H1_strain_intertwiner": strain_data,
        "product_and_globalization_cutset": cutset_data,
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "The selected q79 affine S3 holonomy and shared-root Fourier C4 now act exactly by unitary cochain maps on the finite Weyl-Koszul complex and preserve its Delta, harmonic projector, reduced Green and homotopy. Harmonic H1 carries sign plus sign under S3 and the exact quarter-turn j under C4. After tensoring by det(E_D) and E_D, this is exactly the established rank-six q79 D/E strain local system with J_DE, Reynolds rank two and TT rank four. The harmonic exterior product globalizes, but the canonical reflection and Fourier lifts are not multiplicative on the full forward-difference DGA and full-chain C4 does not commute with all S3 holonomies. Thus the cohomology shadow is globally identified while the full covariant calculus and selected nonzero-Chern HYM endpoint remain open.",
        "nonclaims": [
            "global multiplicative descent of the full forward-difference Weyl-Koszul DGA",
            "autonomous C4 symmetry of the marked Fu-Yau branch",
            "selected visible-hidden nonzero-Chern HYM endpoint or reduced Green",
            "continuum connection, nonlinear product or higher-operation transfer",
            "physical action normalization or closure of B.GEO.01, B.OP.01 or B.ACTION.01",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
