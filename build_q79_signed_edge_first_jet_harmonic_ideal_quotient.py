"""Build the exact signed-edge first-jet and harmonic-ideal quotient packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_signed_edge_first_jet_source_lock.json"
THEOREM_PATH = ROOT / "SignedEdgeFirstJetSelectionAndHarmonicIdealQuotientTheorem_v1.md"
PACKET_PATH = ROOT / "q79_signed_edge_first_jet_harmonic_ideal_quotient.packet.json"
SYMMETRIC_PACKET_PATH = ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
C4_PACKET_PATH = ROOT / "q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json"

Q = Fraction
Matrix = tuple[tuple[Q, ...], ...]

SIGNED_BASIS = ("theta_+x", "theta_-x", "theta_+z", "theta_-z")
PARITY_BASIS = ("o_x", "o_z", "e_x", "e_z")
INVERSION = (1, 0, 3, 2)
FOURIER = (2, 3, 1, 0)
FOURIER_PARITY_MAP = (1, 0, 3, 2)
FOURIER_PARITY_SIGNS = (1, -1, 1, 1)
REFLECTION_PARITY_MAP = (0, 1, 2, 3)
REFLECTION_PARITY_SIGNS = (-1, -1, 1, 1)
EVEN_MASK = 0b1100
SERIES_ORDER = 12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix(rows: Iterable[Iterable[int | Q]]) -> Matrix:
    return tuple(tuple(Q(value) for value in row) for row in rows)


def identity(size: int) -> Matrix:
    return matrix([[1 if row == col else 0 for col in range(size)] for row in range(size)])


def zero(rows: int, cols: int) -> Matrix:
    return matrix([[0 for _ in range(cols)] for _ in range(rows)])


def add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(x + y for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def scale(value: int | Q, source: Matrix) -> Matrix:
    scalar = Q(value)
    return tuple(tuple(scalar * entry for entry in row) for row in source)


def sub(left: Matrix, right: Matrix) -> Matrix:
    return add(left, scale(-1, right))


def mul(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(sum((left[row][index] * right[index][col] for index in range(len(right))), Q(0)) for col in range(len(right[0])))
        for row in range(len(left))
    )


def transpose(source: Matrix) -> Matrix:
    return tuple(tuple(source[col][row] for col in range(len(source))) for row in range(len(source[0])))


def power(source: Matrix, exponent: int) -> Matrix:
    out = identity(len(source))
    for _ in range(exponent):
        out = mul(out, source)
    return out


def rank(source: Matrix) -> int:
    work = [list(row) for row in source]
    rows, cols = len(work), len(work[0]) if work else 0
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][col]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row != pivot_row and work[row][col]:
                factor = work[row][col]
                work[row] = [entry - factor * base for entry, base in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def permutation_matrix(mapping: tuple[int, ...]) -> Matrix:
    rows = [[0 for _ in mapping] for _ in mapping]
    for source, target in enumerate(mapping):
        rows[target][source] = 1
    return matrix(rows)


def serial_matrix(source: Matrix) -> list[list[str]]:
    return [[fstr(value) for value in row] for row in source]


def wedge_masks(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = sum(
        1
        for left_index in range(4)
        if left & (1 << left_index)
        for right_index in range(4)
        if right & (1 << right_index) and left_index > right_index
    )
    return left | right, -1 if inversions % 2 else 1


def exterior_signed_action(
    mask: int,
    mapping: tuple[int, ...],
    generator_signs: tuple[int, ...],
) -> tuple[int, int]:
    images = [mapping[index] for index in range(4) if mask & (1 << index)]
    coefficient = 1
    for index in range(4):
        if mask & (1 << index):
            coefficient *= generator_signs[index]
    inversions = sum(images[left] > images[right] for left in range(len(images)) for right in range(left + 1, len(images)))
    if inversions % 2:
        coefficient *= -1
    return sum(1 << index for index in images), coefficient


def parity_data() -> tuple[dict[str, object], dict[str, bool]]:
    change = matrix(
        [
            [1, 0, 1, 0],
            [-1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, -1, 0, 1],
        ]
    )
    inverse = matrix(
        [
            [Q(1, 2), Q(-1, 2), 0, 0],
            [0, 0, Q(1, 2), Q(-1, 2)],
            [Q(1, 2), Q(1, 2), 0, 0],
            [0, 0, Q(1, 2), Q(1, 2)],
        ]
    )
    metric_signed = scale(Q(1, 2), identity(4))
    reflection_signed = permutation_matrix(INVERSION)
    fourier_signed = permutation_matrix(FOURIER)
    reflection_parity = mul(mul(inverse, reflection_signed), change)
    fourier_parity = mul(mul(inverse, fourier_signed), change)
    fourier_square = power(fourier_parity, 2)
    odd_projector = scale(Q(1, 2), sub(identity(4), fourier_square))
    even_projector = scale(Q(1, 2), add(identity(4), fourier_square))
    principal_symbol = matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    second_axial = matrix([[0, 0], [0, 0], [Q(1, 2), 0], [0, Q(1, 2)]])
    expected_reflection = matrix(
        [
            [-1, 0, 0, 0],
            [0, -1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    expected_fourier = matrix(
        [
            [0, -1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ]
    )
    expected_square = expected_reflection
    expected_odd = matrix(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    )
    expected_even = sub(identity(4), expected_odd)
    checks = {
        "odd_even_change_of_basis_is_exact": mul(inverse, change) == identity(4) and mul(change, inverse) == identity(4),
        "half_edge_metric_makes_odd_even_basis_orthonormal": mul(mul(transpose(change), metric_signed), change) == identity(4),
        "reflection_is_minus_on_odd_and_plus_on_even": reflection_parity == expected_reflection,
        "Fourier_is_quarter_turn_on_odd_and_swap_on_even": fourier_parity == expected_fourier,
        "Fourier_square_is_the_signed_parity_involution": fourier_square == expected_square,
        "odd_projector_is_one_minus_Fourier_square_over_two": odd_projector == expected_odd,
        "even_projector_is_one_plus_Fourier_square_over_two": even_projector == expected_even,
        "odd_even_projectors_are_complementary_orthogonal_idempotents": (
            power(odd_projector, 2) == odd_projector
            and power(even_projector, 2) == even_projector
            and mul(odd_projector, even_projector) == zero(4, 4)
            and add(odd_projector, even_projector) == identity(4)
        ),
        "odd_and_even_projectors_both_have_rank_two": rank(odd_projector) == rank(even_projector) == 2,
        "first_order_principal_symbol_has_rank_two_and_lands_exactly_in_odd_plane": (
            rank(principal_symbol) == 2
            and mul(odd_projector, principal_symbol) == principal_symbol
            and mul(even_projector, principal_symbol) == zero(4, 2)
        ),
        "axial_second_symbol_lands_exactly_in_even_plane": (
            rank(second_axial) == 2
            and mul(even_projector, second_axial) == second_axial
            and mul(odd_projector, second_axial) == zero(4, 2)
        ),
        "reflection_odd_eigenspace_has_dimension_two": 4 - rank(add(reflection_parity, identity(4))) == 2,
        "the_q79_harmonic_C4_generator_is_recovered_on_the_odd_plane": tuple(tuple(row[col] for col in range(2)) for row in fourier_parity[:2]) == ((Q(0), Q(-1)), (Q(1), Q(0))),
    }
    return {
        "signed_basis": list(SIGNED_BASIS),
        "parity_basis": list(PARITY_BASIS),
        "change_of_basis_columns": serial_matrix(change),
        "signed_metric": serial_matrix(metric_signed),
        "reflection_in_parity_basis": serial_matrix(reflection_parity),
        "Fourier_in_parity_basis": serial_matrix(fourier_parity),
        "Fourier_square": serial_matrix(fourier_square),
        "odd_projector": serial_matrix(odd_projector),
        "even_projector": serial_matrix(even_projector),
        "principal_first_symbol": serial_matrix(principal_symbol),
        "axial_second_symbol_coefficient": serial_matrix(second_axial),
        "uniqueness": "The reversal-odd eigenspace is exactly the two-dimensional odd plane, so every rank-two first-order reflection-covariant symbol projector is P_O=(1-F^2)/2.",
    }, checks


def formal_series_data() -> tuple[dict[str, object], dict[str, bool]]:
    terms = []
    all_split = True
    for derivative_order in range(1, SERIES_ORDER + 1):
        plus = Q(1, factorial(derivative_order))
        minus = Q((-1) ** derivative_order, factorial(derivative_order))
        odd = (plus - minus) / 2
        even = (plus + minus) / 2
        expected_odd = plus if derivative_order % 2 else Q(0)
        expected_even = plus if derivative_order % 2 == 0 else Q(0)
        all_split &= odd == expected_odd and even == expected_even
        terms.append(
            {
                "derivative_order": derivative_order,
                "h_power_after_normalization": derivative_order - 1,
                "odd_coefficient": fstr(odd),
                "even_coefficient": fstr(even),
                "channel": "odd_first-jet" if derivative_order % 2 else "even_axial-higher-jet",
            }
        )
    checks = {
        "signed_exponential_series_splits_exactly_by_derivative_parity": all_split,
        "odd_channel_starts_with_nabla_at_h_power_zero": terms[0]["odd_coefficient"] == "1" and terms[0]["h_power_after_normalization"] == 0,
        "even_channel_has_no_principal_first_jet": terms[0]["even_coefficient"] == "0",
        "even_channel_starts_with_h_nabla_squared_over_two": terms[1]["even_coefficient"] == "1/2" and terms[1]["h_power_after_normalization"] == 1,
        "odd_first_correction_is_h_squared_nabla_cubed_over_six": terms[2]["odd_coefficient"] == "1/6" and terms[2]["h_power_after_normalization"] == 2,
        "all_odd_derivatives_land_only_in_odd_plane_through_order_twelve": all(term["even_coefficient"] == "0" for term in terms if term["derivative_order"] % 2),
        "all_even_derivatives_land_only_in_even_plane_through_order_twelve": all(term["odd_coefficient"] == "0" for term in terms if term["derivative_order"] % 2 == 0),
    }
    return {
        "exact_identity": "d_h=sinh(h*nabla)/h tensor o + (cosh(h*nabla)-1)/h tensor e",
        "truncation_used_for_executable_coefficient_audit": SERIES_ORDER,
        "terms": terms,
        "principal_first_jet": "nabla_x tensor o_x + nabla_z tensor o_z",
        "first_even_term": "h/2 (nabla_x^2 tensor e_x + nabla_z^2 tensor e_z)",
        "formal_parameter_status": "jet-order bookkeeper, not a physical length or fitted parameter",
    }, checks


def harmonic_ideal_data() -> tuple[dict[str, object], dict[str, bool]]:
    all_masks = tuple(range(16))
    ideal = tuple(mask for mask in all_masks if mask & EVEN_MASK)
    quotient = tuple(mask for mask in all_masks if not mask & EVEN_MASK)
    full_dims = [sum(mask.bit_count() == degree for mask in all_masks) for degree in range(5)]
    ideal_dims = [sum(mask.bit_count() == degree for mask in ideal) for degree in range(5)]
    quotient_dims = [sum(mask.bit_count() == degree for mask in quotient) for degree in range(5)]

    ideal_closed = True
    quotient_homomorphism = True
    valuation_additive = True
    for left in all_masks:
        for right in all_masks:
            target, _ = wedge_masks(left, right)
            if left in ideal and target is not None:
                ideal_closed &= target in ideal
            left_q = None if left in ideal else left
            right_q = None if right in ideal else right
            quotient_product = None
            if left_q is not None and right_q is not None:
                quotient_product, _ = wedge_masks(left_q, right_q)
            projected_product = None if target is None or target in ideal else target
            quotient_homomorphism &= quotient_product == projected_product
            if target is not None:
                valuation_additive &= ((target & EVEN_MASK).bit_count() == (left & EVEN_MASK).bit_count() + (right & EVEN_MASK).bit_count())

    quotient_associative = True
    for left in quotient:
        for middle in quotient:
            for right in quotient:
                lm, lm_sign = wedge_masks(left, middle)
                mr, mr_sign = wedge_masks(middle, right)
                left_target, left_sign = (None, 0) if lm is None else wedge_masks(lm, right)
                right_target, right_sign = (None, 0) if mr is None else wedge_masks(left, mr)
                quotient_associative &= left_target == right_target and lm_sign * left_sign == mr_sign * right_sign

    ideal_generated = all(
        any(
            mask & (1 << generator)
            and wedge_masks(1 << generator, mask ^ (1 << generator))[0] == mask
            for generator in (2, 3)
        )
        for mask in ideal
    )

    symmetry_stable = True
    valuation_stable = True
    for mask in all_masks:
        for mapping, signs in (
            (FOURIER_PARITY_MAP, FOURIER_PARITY_SIGNS),
            (REFLECTION_PARITY_MAP, REFLECTION_PARITY_SIGNS),
        ):
            target, _ = exterior_signed_action(mask, mapping, signs)
            symmetry_stable &= (mask in ideal) == (target in ideal)
            valuation_stable &= (mask & EVEN_MASK).bit_count() == (target & EVEN_MASK).bit_count()

    scalar = (Q(1), Q(1))
    axial = (Q(1), Q(-1))
    even_fourier = matrix([[0, 1], [1, 0]])
    checks = {
        "symmetric_harmonic_exterior_algebra_has_sixteen_basis_classes": len(all_masks) == 16,
        "even_generated_ideal_has_exactly_twelve_basis_classes": len(ideal) == 12,
        "ideal_dimensions_are_0_2_5_4_1": ideal_dims == [0, 2, 5, 4, 1],
        "quotient_dimensions_are_1_2_1_0_0": quotient_dims == [1, 2, 1, 0, 0],
        "full_dimensions_are_1_4_6_4_1": full_dims == [1, 4, 6, 4, 1],
        "all_extra_classes_are_generated_by_the_even_plane": ideal_generated,
        "even_generated_subspace_is_a_two_sided_graded_ideal": ideal_closed,
        "harmonic_quotient_map_is_multiplicative_on_all_256_basis_pairs": quotient_homomorphism,
        "four_class_odd_quotient_product_is_associative_on_all_64_basis_triples": quotient_associative,
        "ideal_and_quotient_are_reflection_and_C4_stable": symmetry_stable,
        "Rees_even_count_is_additive_under_every_nonzero_wedge_product": valuation_additive,
        "Rees_even_count_is_preserved_by_reflection_and_C4": valuation_stable,
        "Rees_special_fiber_kernel_is_exactly_the_twelve_class_ideal": set(ideal) == {mask for mask in all_masks if (mask & EVEN_MASK).bit_count() > 0},
        "even_scalar_and_axial_channels_have_Fourier_eigenvalues_plus_and_minus_one": (
            tuple(sum(even_fourier[row][col] * scalar[col] for col in range(2)) for row in range(2)) == scalar
            and tuple(sum(even_fourier[row][col] * axial[col] for col in range(2)) for row in range(2)) == tuple(-value for value in axial)
        ),
    }
    return {
        "harmonic_algebra": "Lambda(O direct_sum E)",
        "full_dimensions": full_dims,
        "even_generated_ideal": {
            "definition": "J=<e_x,e_z>",
            "basis_masks": list(ideal),
            "dimensions": ideal_dims,
            "total_dimension": len(ideal),
        },
        "first_jet_quotient": {
            "definition": "Lambda(O direct_sum E)/<E> = Lambda(O)",
            "basis_masks": list(quotient),
            "dimensions": quotient_dims,
            "total_dimension": len(quotient),
            "product": "strict exterior product; associative and C4-equivariant",
        },
        "Rees_degeneration": {
            "map": "rho_h(o_i)=o_i, rho_h(e_i)=h e_i",
            "valuation": "number of even generators in a harmonic monomial",
            "generic_fiber": "isomorphic to the sixteen-class symmetric harmonic algebra when h is invertible",
            "special_fiber": "the four-class odd exterior algebra with kernel J",
        },
        "even_second_jet_channels": {
            "scalar": "e_x+e_z, Fourier eigenvalue +1",
            "axial_traceless": "e_x-e_z, Fourier eigenvalue -1",
            "guard": "These are axial second-difference channels, not a claim of a complete continuum Hessian.",
        },
    }, checks


def source_checks(lock: dict[str, object], symmetric: dict[str, object], c4: dict[str, object]) -> dict[str, bool]:
    sources = lock.get("sources", [])
    claims = lock["extracted_claims"]
    local_hashes_match = all(
        sha256(ROOT / item["path"]) == item["sha256"]
        for item in sources
        if item["repository"] == "mtt-causal-base-constraint-fiber"
    )
    symmetric_retract = symmetric["selected_complex_retract"]
    harmonic_representations = c4["S3_cochain_and_local_C4_naturality"]["harmonic_representations"]
    return {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.q79-signed-edge-first-jet-source-lock.v1",
        "kernel_model_hash_is_pinned": len(lock["kernel_model"]["state_sha256"]) == 64,
        "three_controlling_authorities_are_pinned": [item["id"] for item in lock["controlling_authorities"]] == ["A10", "A18", "A47"],
        "six_sources_are_commit_blob_and_sha256_pinned": len(sources) == 6 and all(len(item["commit"]) == 40 and len(item["git_blob"]) == 40 and len(item["sha256"]) == 64 for item in sources),
        "all_repo_local_source_hashes_match": local_hashes_match,
        "upstream_symmetric_cohomology_is_1_4_6_4_1": symmetric["normalized_Hodge_theory"]["cohomology_dimensions"] == [1, 4, 6, 4, 1],
        "upstream_selected_H1_is_the_odd_signed_edge_plane": symmetric_retract["selected_H1_basis"] == ["theta_+x-theta_-x", "theta_+z-theta_-z"],
        "upstream_extra_harmonic_dimensions_are_0_2_5_4_1": symmetric_retract["extra_harmonic_dimensions"] == [0, 2, 5, 4, 1],
        "upstream_q79_harmonic_C4_is_the_quarter_turn": harmonic_representations["C4"][1] == "j=[[0,-1],[1,0]]",
        "adjacent_strain_evidence_is_explicitly_non_authoritative_for_this_proof": claims["adjacent_strain_jet_evidence"]["zero_edge_first_jets_vanish"] is True and "not a derivation" in sources[4]["role"],
        "source_guard_keeps_HYM_endpoint_and_continuum_intertwiner_open": "does not select the nonzero-Chern" in lock["guard"] and "does not assert that the finite qutrit translations" in lock["guard"],
    }


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    symmetric = json.loads(SYMMETRIC_PACKET_PATH.read_text(encoding="utf-8"))
    c4 = json.loads(C4_PACKET_PATH.read_text(encoding="utf-8"))
    parity, parity_checks = parity_data()
    series, series_checks = formal_series_data()
    harmonic, harmonic_checks = harmonic_ideal_data()
    checks = source_checks(lock, symmetric, c4) | parity_checks | series_checks | harmonic_checks
    return {
        "schema": "boe.mtt.q79-signed-edge-first-jet-harmonic-ideal-quotient.v1",
        "theorem_id": "SignedEdgeFirstJetSelectionAndHarmonicIdealQuotientTheorem.v1",
        "date": "2026-08-28",
        "tiers": [
            "EXACT_SIGNED_EDGE_REPRESENTATION",
            "EXACT_UNIVERSAL_FORMAL_FIRST_JET",
            "EXACT_HARMONIC_ALGEBRA_QUOTIENT",
            "CONDITIONAL_HYM_PRINCIPAL_SYMBOL_COROLLARY",
            "PHYSICAL_ENDPOINT_OPEN",
        ],
        "orientation_odd_plane_is_unique_principal_first_jet": True,
        "twelve_extra_harmonic_classes_form_even_generated_ideal": True,
        "selected_harmonic_algebra_is_strict_quotient": True,
        "selected_finite_to_continuum_intertwiner": False,
        "selected_nonzero_Chern_HYM_endpoint": False,
        "full_chain_associative_response_transfer": False,
        "continuous_fit_parameters": 0,
        "discrete_physical_selectors": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "source_lock_sha256": sha256(LOCK_PATH),
            "theorem_sha256": sha256(THEOREM_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "signed_edge_parity": parity,
        "formal_first_second_jet_split": series,
        "harmonic_ideal_quotient": harmonic,
        "conditional_HYM_corollary": {
            "statement": "Any connection-consistent signed-edge realization of a first-order Dolbeault or gauge deformation operator factors at principal-symbol order through the odd projector P_O.",
            "antecedent_selected_in_q79": False,
            "missing": [
                "source-hashed visible-hidden HYM endpoint and common chamber",
                "selected connection and reduced Green operator",
                "physical C4 naturality",
                "finite qutrit to continuum transport family",
                "domains, normalization and certified error bounds",
            ],
        },
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "The orientation-odd q79 harmonic plane is now proved to be the unique principal first-jet landing space of every reflection-covariant connection-generated signed-edge transport family. The twelve extra harmonic classes are exactly the C4-stable ideal generated by the orientation-even plane, and the selected 1,2,1 algebra is the strict associative quotient. The even plane begins at axial second-jet order, so it is retyped rather than arbitrarily discarded. Physical promotion remains conditional because no selected q79 HYM endpoint, finite-to-continuum intertwiner or certified error bound has been supplied.",
        "nonclaims": [
            "a selected small-spacing family for the finite qutrit Weyl translations",
            "convergence of the finite signed calculus to a continuum HYM complex",
            "physical absence of all orientation-even higher-jet modes",
            "a complete continuum Hessian carried by the even plane",
            "the selected nonzero-Chern visible-hidden HYM endpoint or reduced Green operator",
            "a full-chain associative or A-infinity response transfer",
            "closure of B.GEO.01, B.OP.01 or B.ACTION.01",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
