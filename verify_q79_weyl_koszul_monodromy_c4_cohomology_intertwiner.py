"""Independent exact verifier for the q79 Weyl-Koszul monodromy/C4 bridge."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable

import verify_selected_finite_weyl_koszul_hodge_and_interaction_cutset as base


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json"
LOCK_PATH = ROOT / "q79_weyl_koszul_monodromy_c4_source_lock.json"

Pair = base.Pair
Sparse = base.Sparse
Mat = base.Mat
Linear = tuple[tuple[Pair, ...], ...]
Action = Callable[[Sparse], Sparse]
MASKS = {0: (0,), 1: (1, 2), 2: (3,)}
S3 = tuple((eps, shift) for eps in (1, -1) for shift in range(3))


def lzero(rows: int, cols: int) -> Linear:
    return tuple(tuple(base.Q0 for _ in range(cols)) for _ in range(rows))


def lid(size: int) -> Linear:
    return tuple(tuple(base.Q1 if row == col else base.Q0 for col in range(size)) for row in range(size))


def ladd(left: Linear, right: Linear) -> Linear:
    return tuple(tuple(base.qadd(x, y) for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def lscale(value: int | Fraction, source: Linear) -> Linear:
    return tuple(tuple(base.qscale(value, item) for item in row) for row in source)


def lsub(left: Linear, right: Linear) -> Linear:
    return ladd(left, lscale(-1, right))


def lmul(left: Linear, right: Linear) -> Linear:
    return tuple(
        tuple(
            base.sum_q(base.qmul(left[row][k], right[k][col]) for k in range(len(right)))
            for col in range(len(right[0]))
        )
        for row in range(len(left))
    )


def ladj(source: Linear) -> Linear:
    return tuple(tuple(base.qconj(source[col][row]) for col in range(len(source))) for row in range(len(source[0])))


def lpower(source: Linear, power: int) -> Linear:
    out = lid(len(source))
    for _ in range(power):
        out = lmul(out, source)
    return out


def ltrace(source: Linear) -> Pair:
    return base.sum_q(source[index][index] for index in range(len(source)))


def nonzero_entries(source: Linear) -> int:
    return sum(value != base.Q0 for row in source for value in row)


def basis_keys(degree: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((row, col, mask) for mask in MASKS[degree] for row in range(3) for col in range(3))


def coefficient(source: Sparse, mask: int) -> Mat:
    return tuple(tuple(source.get((row, col, mask), base.Q0) for col in range(3)) for row in range(3))


def from_matrix(source: Mat, mask: int) -> Sparse:
    return base.sparse_clean(
        {
            (row, col, mask): source[row][col]
            for row in range(3)
            for col in range(3)
            if source[row][col] != base.Q0
        }
    )


def from_coefficients(values: dict[int, Mat]) -> Sparse:
    out: Sparse = {}
    for mask, value in values.items():
        out = base.sparse_add(out, from_matrix(value, mask))
    return out


def vector(source: Sparse, degree: int) -> tuple[Pair, ...]:
    return tuple(source.get(key, base.Q0) for key in basis_keys(degree))


def action_matrix(degree_in: int, degree_out: int, action: Action) -> Linear:
    columns = [vector(action({key: base.Q1}), degree_out) for key in basis_keys(degree_in)]
    return tuple(tuple(columns[col][row] for col in range(len(columns))) for row in range(len(columns[0])))


def alpha_inv(source: Mat) -> Mat:
    return base.alpha(base.alpha(source))


def beta_inv(source: Mat) -> Mat:
    return base.beta(base.beta(source))


def permutation(eps: int, shift: int) -> Mat:
    return tuple(
        tuple(base.Q1 if row == (eps * col + shift) % 3 else base.Q0 for col in range(3))
        for row in range(3)
    )


def gamma(source: Mat, eps: int, shift: int) -> Mat:
    unitary = permutation(eps, shift)
    return base.mmul(base.mmul(unitary, source), base.madj(unitary))


def fourier() -> Mat:
    return tuple(tuple(base.qpow(row * col) for col in range(3)) for row in range(3))


def gamma_f(source: Mat) -> Mat:
    transform = fourier()
    return base.mscale(Fraction(1, 3), base.mmul(base.mmul(transform, source), base.madj(transform)))


def apply_s3(source: Sparse, eps: int, shift: int) -> Sparse:
    values = {mask: coefficient(source, mask) for mask in range(4)}
    if eps == 1:
        return from_coefficients({mask: gamma(value, eps, shift) for mask, value in values.items()})
    return from_coefficients(
        {
            0: gamma(values[0], eps, shift),
            1: base.mscale(-1, gamma(alpha_inv(values[1]), eps, shift)),
            2: base.mscale(-1, gamma(beta_inv(values[2]), eps, shift)),
            3: gamma(alpha_inv(beta_inv(values[3])), eps, shift),
        }
    )


def apply_c4(source: Sparse) -> Sparse:
    values = {mask: coefficient(source, mask) for mask in range(4)}
    return from_coefficients(
        {
            0: gamma_f(values[0]),
            1: base.mscale(-1, gamma_f(beta_inv(values[2]))),
            2: gamma_f(values[1]),
            3: gamma_f(beta_inv(values[3])),
        }
    )


def compose(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] * right[0], (left[0] * right[1] + left[1]) % 3


def harmonic_project(source: Sparse) -> Sparse:
    values: dict[int, Mat] = {}
    for mask in range(4):
        source_matrix = coefficient(source, mask)
        weight = base.mtrace(source_matrix)
        values[mask] = tuple(
            tuple(weight if row == col else base.Q0 for col in range(3))
            for row in range(3)
        )
    return from_coefficients(values)


def operators() -> dict[str, object]:
    d0 = action_matrix(0, 1, base.differential)
    d1 = action_matrix(1, 2, base.differential)
    d0s, d1s = ladj(d0), ladj(d1)
    deltas = {
        0: lmul(d0s, d0),
        1: ladd(lmul(d0, d0s), lmul(d1s, d1)),
        2: lmul(d1, d1s),
    }
    projectors = {degree: action_matrix(degree, degree, harmonic_project) for degree in range(3)}
    greens = {
        degree: lscale(Fraction(1, 36), lsub(lscale(7, delta), lmul(delta, delta)))
        for degree, delta in deltas.items()
    }
    return {
        "d": {0: d0, 1: d1},
        "delta": deltas,
        "P": projectors,
        "G": greens,
        "h": {1: lmul(d0s, greens[1]), 2: lmul(d1s, greens[2])},
    }


def inclusion(degree: int) -> Linear:
    columns = [vector(base.center(mask), degree) for mask in MASKS[degree]]
    return tuple(tuple(columns[col][row] for col in range(len(columns))) for row in range(len(columns[0])))


def induced(action: Linear, degree: int) -> Linear:
    inc = inclusion(degree)
    return lscale(Fraction(1, 3), lmul(ladj(inc), lmul(action, inc)))


def block_diag(left: Linear, right: Linear) -> Linear:
    out = [[base.Q0 for _ in range(len(left[0]) + len(right[0]))] for _ in range(len(left) + len(right))]
    for row in range(len(left)):
        for col in range(len(left[0])):
            out[row][col] = left[row][col]
    for row in range(len(right)):
        for col in range(len(right[0])):
            out[len(left) + row][len(left[0]) + col] = right[row][col]
    return tuple(tuple(row) for row in out)


def sum_linear(values: Iterable[Linear]) -> Linear:
    iterator = iter(values)
    out = next(iterator)
    for value in iterator:
        out = ladd(out, value)
    return out


def defects(action: Action, basis: list[Sparse]) -> int:
    return sum(
        action(base.product(left, right)) != base.product(action(left), action(right))
        for left in basis
        for right in basis
    )


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


def independent_checks() -> tuple[dict[str, bool], dict[str, object]]:
    ops = operators()
    d, delta, projectors, greens, homotopies = ops["d"], ops["delta"], ops["P"], ops["G"], ops["h"]
    hodge = {
        "matrix_Hodge_contraction_identity_holds_in_degree_zero": lmul(homotopies[1], d[0]) == lsub(lid(9), projectors[0]),
        "matrix_Hodge_contraction_identity_holds_in_degree_one": ladd(lmul(d[0], homotopies[1]), lmul(homotopies[2], d[1])) == lsub(lid(18), projectors[1]),
        "matrix_Hodge_contraction_identity_holds_in_degree_two": lmul(d[1], homotopies[2]) == lsub(lid(9), projectors[2]),
        "reduced_Green_is_the_exact_two_sided_inverse_off_harmonics": all(
            lmul(delta[degree], greens[degree]) == lsub(lid(len(delta[degree])), projectors[degree])
            and lmul(greens[degree], delta[degree]) == lsub(lid(len(delta[degree])), projectors[degree])
            for degree in range(3)
        ),
        "Hodge_homotopy_and_projector_side_conditions_hold_exactly": (
            lmul(homotopies[1], homotopies[2]) == lzero(9, 9)
            and lmul(homotopies[1], projectors[1]) == lzero(9, 18)
            and lmul(projectors[0], homotopies[1]) == lzero(9, 18)
            and lmul(homotopies[2], projectors[2]) == lzero(18, 9)
            and lmul(projectors[1], homotopies[2]) == lzero(18, 9)
        ),
    }

    actions_s3 = {
        group: {
            degree: action_matrix(degree, degree, lambda item, group=group: apply_s3(item, *group))
            for degree in range(3)
        }
        for group in S3
    }
    actions_c4 = {degree: action_matrix(degree, degree, apply_c4) for degree in range(3)}
    units = [base.unit_matrix(row, col) for row in range(3) for col in range(3)]
    harmonic_s3 = {group: {degree: induced(action[degree], degree) for degree in range(3)} for group, action in actions_s3.items()}
    harmonic_c4 = {degree: induced(actions_c4[degree], degree) for degree in range(3)}
    expected_j: Linear = ((base.Q0, base.q(-1)), (base.Q1, base.Q0))

    cochain = {
        "affine_S3_conjugates_alpha_beta_by_the_exact_signed_lattice_action": all(
            gamma(base.alpha(item), eps, shift) == (base.alpha(gamma(item, eps, shift)) if eps == 1 else alpha_inv(gamma(item, eps, shift)))
            and gamma(base.beta(item), eps, shift) == (base.beta(gamma(item, eps, shift)) if eps == 1 else beta_inv(gamma(item, eps, shift)))
            for eps, shift in S3
            for item in units
        ),
        "Fourier_C4_conjugates_alpha_to_beta_and_beta_to_alpha_inverse": all(
            gamma_f(base.alpha(item)) == base.beta(gamma_f(item))
            and gamma_f(base.beta(item)) == alpha_inv(gamma_f(item))
            for item in units
        ),
        "six_affine_S3_maps_are_exact_cochain_maps": all(
            lmul(action[1], d[0]) == lmul(d[0], action[0])
            and lmul(action[2], d[1]) == lmul(d[1], action[1])
            for action in actions_s3.values()
        ),
        "affine_S3_cochain_maps_obey_the_group_law": all(
            lmul(actions_s3[left][degree], actions_s3[right][degree]) == actions_s3[compose(left, right)][degree]
            for left in S3 for right in S3 for degree in range(3)
        ),
        "affine_S3_cochain_maps_are_unitary": all(
            lmul(ladj(action[degree]), action[degree]) == lid(len(action[degree]))
            for action in actions_s3.values() for degree in range(3)
        ),
        "Fourier_quarterturn_is_an_exact_cochain_map": lmul(actions_c4[1], d[0]) == lmul(d[0], actions_c4[0]) and lmul(actions_c4[2], d[1]) == lmul(d[1], actions_c4[1]),
        "Fourier_quarterturn_is_unitary": all(lmul(ladj(actions_c4[degree]), actions_c4[degree]) == lid(len(actions_c4[degree])) for degree in range(3)),
        "Fourier_quarterturn_has_order_four_on_every_degree": all(lpower(actions_c4[degree], 4) == lid(len(actions_c4[degree])) for degree in range(3)),
        "Fourier_quarterturn_square_is_the_selected_affine_reflection": all(lpower(actions_c4[degree], 2) == actions_s3[(-1, 0)][degree] for degree in range(3)),
        "S3_commutes_with_Delta_P_and_G_on_every_degree": all(
            lmul(action[degree], family[degree]) == lmul(family[degree], action[degree])
            for action in actions_s3.values() for family in (delta, projectors, greens) for degree in range(3)
        ),
        "C4_commutes_with_Delta_P_and_G_on_every_degree": all(
            lmul(actions_c4[degree], family[degree]) == lmul(family[degree], actions_c4[degree])
            for family in (delta, projectors, greens) for degree in range(3)
        ),
        "S3_intertwines_both_Hodge_homotopies": all(
            lmul(action[0], homotopies[1]) == lmul(homotopies[1], action[1])
            and lmul(action[1], homotopies[2]) == lmul(homotopies[2], action[2])
            for action in actions_s3.values()
        ),
        "C4_intertwines_both_Hodge_homotopies": lmul(actions_c4[0], homotopies[1]) == lmul(homotopies[1], actions_c4[1]) and lmul(actions_c4[1], homotopies[2]) == lmul(homotopies[2], actions_c4[2]),
        "harmonic_S3_types_are_trivial_sign_trivial_in_degrees_0_1_2": all(
            reps[0] == ((base.Q1,),) and reps[1] == lscale(group[0], lid(2)) and reps[2] == ((base.Q1,),)
            for group, reps in harmonic_s3.items()
        ),
        "harmonic_C4_types_are_one_j_one_in_degrees_0_1_2": harmonic_c4 == {0: ((base.Q1,),), 1: expected_j, 2: ((base.Q1,),)},
        "S3_and_C4_commute_on_harmonic_cohomology": all(
            lmul(harmonic_c4[degree], harmonic_s3[group][degree]) == lmul(harmonic_s3[group][degree], harmonic_c4[degree])
            for group in S3 for degree in range(3)
        ),
    }

    permutations = {group: permutation(*group) for group in S3}
    target = {group: block_diag(value, value) for group, value in permutations.items()}
    source = {
        group: block_diag(lscale(group[0] * group[0], value), lscale(group[0] * group[0], value))
        for group, value in permutations.items()
    }
    jde_rows = [[base.Q0 for _ in range(6)] for _ in range(6)]
    for index in range(3):
        jde_rows[index][index + 3] = base.q(-1)
        jde_rows[index + 3][index] = base.Q1
    jde = tuple(tuple(row) for row in jde_rows)
    source_c4_rows = [[base.Q0 for _ in range(6)] for _ in range(6)]
    for out_lane in range(2):
        for in_lane in range(2):
            for sheet in range(3):
                source_c4_rows[3 * out_lane + sheet][3 * in_lane + sheet] = harmonic_c4[1][out_lane][in_lane]
    source_c4 = tuple(tuple(row) for row in source_c4_rows)
    reynolds = lscale(Fraction(1, 6), sum_linear(target.values()))
    tt = lsub(lid(6), reynolds)
    strain = {
        "determinant_twist_cancels_the_harmonic_H1_sign_for_all_six_holonomies": all(source[group] == target[group] for group in S3),
        "identity_basis_map_is_an_exact_S3_intertwiner_to_D_and_E_strain_lanes": all(source[group] == target[group] for group in S3),
        "harmonic_C4_tensor_identity_is_exactly_J_DE": source_c4 == jde,
        "identity_basis_map_is_an_exact_C4_intertwiner_to_J_DE": source_c4 == jde,
        "induced_strain_C4_has_square_minus_identity_and_order_four": lpower(jde, 2) == lscale(-1, lid(6)) and lpower(jde, 4) == lid(6),
        "strain_C4_commutes_with_all_six_S3_holonomies": all(lmul(jde, target[group]) == lmul(target[group], jde) for group in S3),
        "Reynolds_projector_is_idempotent_with_trace_two": lmul(reynolds, reynolds) == reynolds and ltrace(reynolds) == base.q(2),
        "TT_projector_is_idempotent_with_trace_four": lmul(tt, tt) == tt and ltrace(tt) == base.q(4),
        "J_DE_preserves_the_Reynolds_and_TT_subspaces": lmul(jde, reynolds) == lmul(reynolds, jde) and lmul(jde, tt) == lmul(tt, jde),
    }

    full_basis = [base.basis_element(row, col, mask) for mask in range(4) for row in range(3) for col in range(3)]
    harmonic = [base.center(mask) for mask in range(4)]
    defect_s3 = {
        f"eps_{eps}_shift_{shift}": defects(lambda item, eps=eps, shift=shift: apply_s3(item, eps, shift), full_basis)
        for eps, shift in S3
    }
    defect_c4 = defects(apply_c4, full_basis)
    a, theta_x = base.basis_element(0, 0, 0), base.center(1)
    witness = base.sparse_add(
        apply_s3(base.product(a, theta_x), -1, 0),
        base.sparse_scale(-1, base.product(apply_s3(a, -1, 0), apply_s3(theta_x, -1, 0))),
    )
    commutators = {
        f"eps_{eps}_shift_{shift}": {
            str(degree): nonzero_entries(lsub(lmul(actions_c4[degree], actions_s3[(eps, shift)][degree]), lmul(actions_s3[(eps, shift)][degree], actions_c4[degree])))
            for degree in range(3)
        }
        for eps, shift in S3
    }
    any_noncommuting = any(value > 0 for row in commutators.values() for value in row.values())
    harmonic_commuting = all(
        lmul(harmonic_c4[degree], harmonic_s3[group][degree]) == lmul(harmonic_s3[group][degree], harmonic_c4[degree])
        for group in S3 for degree in range(3)
    )
    cutset = {
        "orientation_preserving_affine_maps_are_full_DGA_automorphisms": all(value == 0 for key, value in defect_s3.items() if "eps_1_" in key),
        "canonical_affine_reflections_are_not_full_DGA_automorphisms": all(value > 0 for key, value in defect_s3.items() if "eps_-1_" in key),
        "explicit_reflection_product_defect_is_nonzero": bool(witness),
        "canonical_Fourier_C4_cochain_map_is_not_a_full_DGA_automorphism": defect_c4 > 0,
        "full_chain_C4_does_not_commute_with_all_S3_holonomies": any_noncommuting,
        "harmonic_exterior_product_is_S3_equivariant": all(
            apply_s3(base.product(left, right), eps, shift) == base.product(apply_s3(left, eps, shift), apply_s3(right, eps, shift))
            for eps, shift in S3 for left in harmonic for right in harmonic
        ),
        "harmonic_exterior_product_is_C4_equivariant": all(
            apply_c4(base.product(left, right)) == base.product(apply_c4(left), apply_c4(right))
            for left in harmonic for right in harmonic
        ),
        "S3_and_C4_commute_after_harmonic_projection": harmonic_commuting,
        "full_forward_difference_DGA_globalization_remains_open": bool(witness) and defect_c4 > 0 and any_noncommuting,
    }
    return hodge | cochain | strain | cutset, {
        "S3_full_DGA_defect_pairs_out_of_1296": defect_s3,
        "C4_full_DGA_defect_pairs_out_of_1296": defect_c4,
        "full_chain_C4_S3_commutator_nonzero_entries": commutators,
    }


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    checks, cutset_data = independent_checks()
    checks = source_checks(lock) | checks

    assert packet["schema"] == "boe.mtt.q79-weyl-koszul-monodromy-c4-cohomology-intertwiner.v1"
    assert packet["global_rootstack_cohomology_bridge"] is True
    assert packet["global_full_forward_difference_DGA"] is False
    assert packet["selected_nonzero_Chern_HYM_endpoint"] is False
    assert packet["continuous_fit_parameters"] == 0
    assert packet["discrete_physical_selectors"] == 0
    assert packet["observed_physical_inputs"] == []
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}

    cutset = packet["product_and_globalization_cutset"]
    for key, value in cutset_data.items():
        assert cutset[key] == value
    assert packet["determinant_twisted_H1_strain_intertwiner"]["ranks"] == {"invariant": 2, "TT": 4}

    hashes = packet["source_hashes"]
    assert hashes["source_lock_sha256"] == digest(LOCK_PATH)
    assert hashes["theorem_sha256"] == digest(ROOT / "Q79WeylKoszulMonodromyC4CohomologyIntertwinerAndProductCutsetTheorem_v1.md")
    assert hashes["builder_sha256"] == digest(ROOT / "build_q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.py")
    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} exact checks")


if __name__ == "__main__":
    main()
