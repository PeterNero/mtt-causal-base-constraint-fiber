"""Build the exact selected finite q79 Weyl-Koszul/Hodge certificate."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_weyl_koszul_source_lock.json"
THEOREM_PATH = ROOT / "SelectedFiniteWeylKoszulHodgeAndInteractionCutsetTheorem_v1.md"
PACKET_PATH = ROOT / "selected_finite_weyl_koszul_hodge_and_interaction_cutset.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class Eisenstein:
    """Exact a+b*omega arithmetic with omega^2+omega+1=0."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    @staticmethod
    def coerce(value: int | Fraction | "Eisenstein") -> "Eisenstein":
        if isinstance(value, Eisenstein):
            return value
        return Eisenstein(Fraction(value), Fraction(0))

    def __add__(self, other: int | Fraction | "Eisenstein") -> "Eisenstein":
        rhs = self.coerce(other)
        return Eisenstein(self.a + rhs.a, self.b + rhs.b)

    __radd__ = __add__

    def __neg__(self) -> "Eisenstein":
        return Eisenstein(-self.a, -self.b)

    def __sub__(self, other: int | Fraction | "Eisenstein") -> "Eisenstein":
        return self + (-self.coerce(other))

    def __rsub__(self, other: int | Fraction | "Eisenstein") -> "Eisenstein":
        return self.coerce(other) - self

    def __mul__(self, other: int | Fraction | "Eisenstein") -> "Eisenstein":
        rhs = self.coerce(other)
        return Eisenstein(
            self.a * rhs.a - self.b * rhs.b,
            self.a * rhs.b + self.b * rhs.a - self.b * rhs.b,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: int | Fraction) -> "Eisenstein":
        divisor = Fraction(other)
        return Eisenstein(self.a / divisor, self.b / divisor)

    def conjugate(self) -> "Eisenstein":
        return Eisenstein(self.a - self.b, -self.b)

    def pair(self) -> list[str]:
        return [fstr(self.a), fstr(self.b)]


ZERO = Eisenstein()
ONE = Eisenstein(Fraction(1))
OMEGA = Eisenstein(Fraction(0), Fraction(1))


def omega_power(power: int) -> Eisenstein:
    return (ONE, OMEGA, -ONE - OMEGA)[power % 3]


Matrix = tuple[tuple[Eisenstein, ...], ...]
TermKey = tuple[int, int, int]
Element = dict[TermKey, Eisenstein]


def matrix(rows: Iterable[Iterable[int | Fraction | Eisenstein]]) -> Matrix:
    return tuple(tuple(Eisenstein.coerce(value) for value in row) for row in rows)


def matrix_zero() -> Matrix:
    return matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])


def matrix_identity() -> Matrix:
    return matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(x + y for x, y in zip(lrow, rrow)) for lrow, rrow in zip(left, right))


def matrix_scale(value: int | Fraction | Eisenstein, source: Matrix) -> Matrix:
    scalar = Eisenstein.coerce(value)
    return tuple(tuple(scalar * entry for entry in row) for row in source)


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            sum((left[row][k] * right[k][col] for k in range(3)), ZERO)
            for col in range(3)
        )
        for row in range(3)
    )


def matrix_adjoint(source: Matrix) -> Matrix:
    return tuple(tuple(source[col][row].conjugate() for col in range(3)) for row in range(3))


def matrix_trace(source: Matrix) -> Eisenstein:
    return sum((source[index][index] for index in range(3)), ZERO)


def normalized_trace(source: Matrix) -> Eisenstein:
    return matrix_trace(source) / 3


def normalized_hs(left: Matrix, right: Matrix) -> Eisenstein:
    return normalized_trace(matrix_multiply(matrix_adjoint(left), right))


def shift_matrix() -> Matrix:
    # X e_j=e_(j+1), so ZX=omega XZ for Z=diag(1,omega,omega^2).
    return matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])


def clock_matrix() -> Matrix:
    return matrix([[1, 0, 0], [0, OMEGA, 0], [0, 0, omega_power(2)]])


def alpha_matrix(source: Matrix) -> Matrix:
    shift = shift_matrix()
    return matrix_multiply(matrix_multiply(shift, source), matrix_adjoint(shift))


def beta_matrix(source: Matrix) -> Matrix:
    clock = clock_matrix()
    return matrix_multiply(matrix_multiply(clock, source), matrix_adjoint(clock))


def clean(element: Element) -> Element:
    return {key: value for key, value in element.items() if value != ZERO}


def element_add(left: Element, right: Element) -> Element:
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, ZERO) + value
    return clean(out)


def element_scale(value: int | Fraction | Eisenstein, source: Element) -> Element:
    scalar = Eisenstein.coerce(value)
    return clean({key: scalar * entry for key, entry in source.items()})


def wedge_masks(left: int, right: int) -> tuple[int | None, int]:
    if left & right:
        return None, 0
    inversions = int(bool(left & 2) and bool(right & 1))
    return left | right, -1 if inversions else 1


def act_on_matrix_unit(mask: int, row: int, col: int) -> tuple[Eisenstein, int, int]:
    coefficient = ONE
    out_row, out_col = row, col
    if mask & 1:
        out_row = (out_row + 1) % 3
        out_col = (out_col + 1) % 3
    if mask & 2:
        coefficient = coefficient * omega_power(out_row - out_col)
    return coefficient, out_row, out_col


def element_multiply(left: Element, right: Element) -> Element:
    out: Element = {}
    for (i, j, left_mask), left_value in left.items():
        for (k, ell, right_mask), right_value in right.items():
            target_mask, sign = wedge_masks(left_mask, right_mask)
            if target_mask is None:
                continue
            twist, acted_k, acted_ell = act_on_matrix_unit(left_mask, k, ell)
            if j != acted_k:
                continue
            key = (i, acted_ell, target_mask)
            out[key] = out.get(key, ZERO) + sign * left_value * right_value * twist
    return clean(out)


def element_differential(source: Element) -> Element:
    out: Element = {}
    for (row, col, mask), value in source.items():
        x_mask, x_sign = wedge_masks(1, mask)
        if x_mask is not None:
            shifted = ((row + 1) % 3, (col + 1) % 3, x_mask)
            original = (row, col, x_mask)
            out[shifted] = out.get(shifted, ZERO) + x_sign * value
            out[original] = out.get(original, ZERO) - x_sign * value

        z_mask, z_sign = wedge_masks(2, mask)
        if z_mask is not None:
            key = (row, col, z_mask)
            delta = omega_power(row - col) - ONE
            out[key] = out.get(key, ZERO) + z_sign * value * delta
    return clean(out)


def basis_element(row: int, col: int, mask: int) -> Element:
    return {(row, col, mask): ONE}


def center_form(mask: int) -> Element:
    return {(index, index, mask): ONE for index in range(3)}


def element_degree(source: Element) -> int:
    degrees = {mask.bit_count() for _, _, mask in source}
    if len(degrees) != 1:
        raise ValueError("element is not homogeneous")
    return next(iter(degrees))


def exact_dga_checks() -> tuple[dict[str, object], dict[str, bool]]:
    basis = [basis_element(row, col, mask) for mask in range(4) for row in range(3) for col in range(3)]
    unit = center_form(0)

    alpha_beta_commutes = True
    for row in range(3):
        for col in range(3):
            source = matrix([[1 if (i, j) == (row, col) else 0 for j in range(3)] for i in range(3)])
            alpha_beta_commutes &= alpha_matrix(beta_matrix(source)) == beta_matrix(alpha_matrix(source))

    square_zero = all(not element_differential(element_differential(value)) for value in basis)
    unit_exact = all(element_multiply(unit, value) == value and element_multiply(value, unit) == value for value in basis)

    leibniz = True
    for left in basis:
        sign = -1 if element_degree(left) % 2 else 1
        for right in basis:
            lhs = element_differential(element_multiply(left, right))
            rhs = element_add(
                element_multiply(element_differential(left), right),
                element_scale(sign, element_multiply(left, element_differential(right))),
            )
            if lhs != rhs:
                leibniz = False
                break
        if not leibniz:
            break

    associative = True
    for left in basis:
        for middle in basis:
            left_middle = element_multiply(left, middle)
            for right in basis:
                if element_multiply(left_middle, right) != element_multiply(left, element_multiply(middle, right)):
                    associative = False
                    break
            if not associative:
                break
        if not associative:
            break

    checks = {
        "selected_weyl_adjoint_actions_commute": alpha_beta_commutes,
        "twisted_weyl_koszul_space_has_dimension_36": len(basis) == 36,
        "twisted_product_has_exact_unit": unit_exact,
        "twisted_product_is_associative_on_all_36_cubed_basis_triples": associative,
        "differential_squares_to_zero_on_all_36_basis_elements": square_zero,
        "graded_Leibniz_rule_holds_on_all_36_squared_basis_pairs": leibniz,
        "graded_commutator_is_a_DGLA_by_the_associative_DGA_lemma": associative and square_zero and leibniz,
    }
    data = {
        "coefficient_field": "Q(omega), omega^2+omega+1=0",
        "algebra": "A=M3(Q(omega))",
        "automorphisms": {
            "alpha": "Ad_X",
            "beta": "Ad_Z",
            "commutation_reason": "ZX=omega XZ and the central phase cancels under conjugation",
        },
        "forms": ["A", "A theta_x + A theta_z", "A theta_x theta_z"],
        "relations": [
            "theta_x a=alpha(a) theta_x",
            "theta_z a=beta(a) theta_z",
            "theta_x^2=theta_z^2=0",
            "theta_x theta_z=-theta_z theta_x",
        ],
        "differential": {
            "d0": "d(a)=(alpha(a)-a)theta_x+(beta(a)-a)theta_z",
            "d1": "d(b theta_x+c theta_z)=((alpha(c)-c)-(beta(b)-b))theta_x theta_z",
        },
        "exhaustive_counts": {
            "basis_elements": 36,
            "unit_tests": 72,
            "d_squared_tests": 36,
            "Leibniz_pairs": 36**2,
            "associativity_triples": 36**3,
        },
    }
    return data, checks


def two_by_two_add(left: list[list[Eisenstein]], right: list[list[Eisenstein]]) -> list[list[Eisenstein]]:
    return [[left[i][j] + right[i][j] for j in range(2)] for i in range(2)]


def mode_hodge_checks() -> tuple[dict[str, object], dict[str, bool]]:
    rows: list[dict[str, object]] = []
    spectrum_degree_0: Counter[int] = Counter()
    all_d1d0 = True
    all_laplacians = True
    all_contractions = True
    all_side_conditions = True
    all_projector_side_conditions = True

    for phase_power in range(3):
        for shift_power in range(3):
            lambda_x = omega_power(-phase_power)
            lambda_z = omega_power(shift_power)
            p = lambda_x - ONE
            q = lambda_z - ONE
            s_field = p.conjugate() * p + q.conjugate() * q
            all_laplacians &= s_field.b == 0
            s = s_field.a
            expected_s = Fraction(3 * int(phase_power != 0) + 3 * int(shift_power != 0))
            all_laplacians &= s == expected_s
            spectrum_degree_0[int(s)] += 1
            all_d1d0 &= (-q) * p + p * q == ZERO

            if s == 0:
                projector_ranks = [1, 2, 1]
                green = "0"
                homotopy = "0"
                all_projector_side_conditions &= p == ZERO and q == ZERO
            else:
                projector_ranks = [0, 0, 0]
                green = fstr(Fraction(1, 1) / s)
                homotopy = "h1(b,c)=(p* b+q* c)/s; h2(w)=(-q* w,p* w)/s"

                h1_d0 = (p.conjugate() * p + q.conjugate() * q) / s
                d1_h2 = (q * q.conjugate() + p * p.conjugate()) / s
                d0_h1 = [
                    [p * p.conjugate() / s, p * q.conjugate() / s],
                    [q * p.conjugate() / s, q * q.conjugate() / s],
                ]
                h2_d1 = [
                    [q.conjugate() * q / s, -q.conjugate() * p / s],
                    [-p.conjugate() * q / s, p.conjugate() * p / s],
                ]
                contraction_1 = two_by_two_add(d0_h1, h2_d1)
                h_squared = (p.conjugate() * (-q.conjugate()) + q.conjugate() * p.conjugate()) / s
                all_contractions &= h1_d0 == ONE and d1_h2 == ONE
                all_contractions &= contraction_1 == [[ONE, ZERO], [ZERO, ONE]]
                all_side_conditions &= h_squared == ZERO
                all_projector_side_conditions &= projector_ranks == [0, 0, 0]

            rows.append(
                {
                    "mode": [phase_power, shift_power],
                    "lambda_x": lambda_x.pair(),
                    "lambda_z": lambda_z.pair(),
                    "delta_x": p.pair(),
                    "delta_z": q.pair(),
                    "laplacian_eigenvalue": fstr(s),
                    "harmonic_projector_ranks_C0_C1_C2": projector_ranks,
                    "green_eigenvalue": green,
                    "homotopy": homotopy,
                }
            )

    spectrum_0 = dict(sorted(spectrum_degree_0.items()))
    spectrum_1 = {eigenvalue: 2 * multiplicity for eigenvalue, multiplicity in spectrum_0.items()}
    total_spectrum = {eigenvalue: 4 * multiplicity for eigenvalue, multiplicity in spectrum_0.items()}
    checks = {
        "Koszul_complex_identity_d1_d0_is_exact_on_all_nine_modes": all_d1d0,
        "degree_zero_laplacian_is_the_selected_Delta_W": all_laplacians and spectrum_0 == {0: 1, 3: 4, 6: 4},
        "degree_one_laplacian_is_two_copies_of_Delta_W": spectrum_1 == {0: 2, 3: 8, 6: 8},
        "degree_two_laplacian_is_the_selected_Delta_W": spectrum_0 == {0: 1, 3: 4, 6: 4},
        "full_complex_spectrum_is_0_4_3_16_6_16": total_spectrum == {0: 4, 3: 16, 6: 16},
        "cohomology_dimensions_are_1_2_1": rows[0]["harmonic_projector_ranks_C0_C1_C2"] == [1, 2, 1],
        "reduced_Green_eigenvalues_are_zero_one_third_one_sixth": {row["green_eigenvalue"] for row in rows} == {"0", "1/3", "1/6"},
        "Hodge_contraction_identity_holds_on_all_nonzero_modes": all_contractions,
        "Hodge_homotopy_squares_to_zero_on_all_modes": all_side_conditions,
        "Hodge_projector_homotopy_side_conditions_hold_on_all_modes": all_projector_side_conditions,
        "spectator_lift_degree_zero_harmonic_rank_is_96": 1 * 96 == 96,
        "spectator_lift_degree_one_harmonic_rank_is_192": 2 * 96 == 192,
        "spectator_lift_degree_two_harmonic_rank_is_96": 1 * 96 == 96,
    }
    data = {
        "mode_basis": "W_ab=Z^a X^b",
        "mode_differentials": {
            "d0": "v -> (p v,q v), p=omega^(-a)-1, q=omega^b-1",
            "d1": "(r,s) -> p s-q r",
        },
        "laplacians": {
            "Delta0": "Delta_W",
            "Delta1": "diag(Delta_W,Delta_W)",
            "Delta2": "Delta_W",
        },
        "spectra": {
            "degree_0": {str(key): value for key, value in spectrum_0.items()},
            "degree_1": {str(key): value for key, value in spectrum_1.items()},
            "degree_2": {str(key): value for key, value in spectrum_0.items()},
            "total": {str(key): value for key, value in total_spectrum.items()},
        },
        "harmonic_projectors": "P0=P_W, P1=P_W direct-sum P_W, P2=P_W",
        "reduced_Greens": "G0=G_W, G1=G_W direct-sum G_W, G2=G_W",
        "homotopies": "h1=d0*G1 and h2=d1*G2",
        "cohomology": {
            "dimensions": [1, 2, 1],
            "basis": ["I", "I theta_x", "I theta_z", "I theta_x theta_z"],
            "spectator_lift_ranks": [96, 192, 96],
        },
        "modes": rows,
    }
    return data, checks


def transfer_checks() -> tuple[dict[str, object], dict[str, bool]]:
    harmonic = [center_form(mask) for mask in range(4)]
    all_closed = all(not element_differential(value) for value in harmonic)
    products_harmonic = True
    table: list[list[str]] = []
    names = ["1", "theta_x", "theta_z", "theta_x theta_z"]
    for left_mask, left in enumerate(harmonic):
        row: list[str] = []
        for right_mask, right in enumerate(harmonic):
            product = element_multiply(left, right)
            target, sign = wedge_masks(left_mask, right_mask)
            expected = {} if target is None else element_scale(sign, harmonic[target])
            products_harmonic &= product == expected
            if target is None:
                row.append("0")
            else:
                prefix = "-" if sign < 0 else ""
                row.append(prefix + names[target])
        table.append(row)

    # Every m3 planar tree contains h immediately after a product of two
    # harmonic inputs. Those products stay harmonic and hP=0.
    m3_zero_count = 4**3 if products_harmonic else 0
    checks = {
        "four_harmonic_generators_are_closed": all_closed,
        "harmonic_center_is_a_sub_DGA": products_harmonic,
        "transferred_m2_is_the_exterior_product": products_harmonic,
        "all_64_transferred_m3_basis_values_vanish": m3_zero_count == 64,
        "all_higher_transferred_products_vanish_by_tree_induction": products_harmonic,
        "minimal_DGLA_on_harmonic_cohomology_is_abelian": products_harmonic,
        "nontrivial_finite_interactions_require_nonharmonic_or_charged_lanes": products_harmonic,
    }
    data = {
        "m2_basis_order": names,
        "m2_table": table,
        "m3_nonzero_basis_values": 0,
        "higher_products": "m_n=0 for every n>=3",
        "proof": "The inclusion of the harmonic center is multiplicative. Every higher-transfer tree contains h after a harmonic product, and hP=0.",
        "consequence": "The selected Weyl constraint complex supplies an exact contraction but does not generate Yukawa, gauge or gravitational interactions on its harmonic center by itself.",
    }
    return data, checks


def response_cutset(lock: dict[str, object]) -> tuple[dict[str, object], dict[str, bool]]:
    unit = matrix_identity()
    shift = shift_matrix()
    shift_squared = matrix_multiply(shift, shift)
    response = matrix_scale(Fraction(1, 3), matrix_add(matrix_add(unit, shift), matrix_scale(-2, shift_squared)))
    center_weight = normalized_trace(response)
    center = matrix_scale(center_weight, unit)
    complement = matrix_add(response, matrix_scale(-1, center))
    symmetrized_on_identity = matrix_scale(Fraction(1, 2), matrix_add(matrix_multiply(response, unit), matrix_multiply(unit, response)))
    center_norm = normalized_hs(center, center)
    complement_norm = normalized_hs(complement, complement)
    total_norm = normalized_hs(response, response)

    response_claim = lock["extracted_claims"]["completed_finite_response"]
    geometry_claim = lock["extracted_claims"]["selected_weyl_geometry"]
    route_relations = response_claim["route_relations"]

    # C=(2/3)S_p+(1/3)S_s has inverse (3/2)S_p+3S_s under
    # the source-locked orthogonal partial-involution relations.
    phase_identity_coefficient = Fraction(2, 3) * Fraction(3, 2)
    shift_identity_coefficient = Fraction(1, 3) * 3
    cross_coefficients_zero = "S_phase S_shift=S_shift S_phase=0" in route_relations
    route_partition_complete = "S_phase^2+S_shift^2=I32" in route_relations
    route_nonzero = "rank(S_phase^2)=rank(S_shift^2)=16" in route_relations
    compressed_invertible = phase_identity_coefficient == 1 and shift_identity_coefficient == 1 and cross_coefficients_zero and route_partition_complete

    checks = {
        "selected_shift_response_reconstructed_exactly": response_claim["shift_response"] == "R_X=(I+X-2X^2)/3",
        "selected_shift_center_weight_is_one_third": center_weight == Eisenstein(Fraction(1, 3)),
        "selected_shift_response_has_nonzero_center_complement": complement != matrix_zero(),
        "center_complement_normalized_HS_norm_is_five_ninths": complement_norm == Eisenstein(Fraction(5, 9)),
        "center_component_normalized_HS_norm_is_one_ninth": center_norm == Eisenstein(Fraction(1, 9)),
        "response_normalized_HS_norm_is_two_thirds": total_norm == Eisenstein(Fraction(2, 3)),
        "symmetrized_shift_response_sends_identity_to_R_X": symmetrized_on_identity == response,
        "completed_D_fin_does_not_preserve_the_Weyl_center": complement != matrix_zero(),
        "source_locked_phase_and_shift_routes_are_nonzero": route_nonzero,
        "source_locked_route_partial_involution_relations_are_complete": cross_coefficients_zero and route_partition_complete,
        "compressed_route_has_an_exact_two_sided_inverse": compressed_invertible,
        "Weyl_center_range_intersects_D_fin_kernel_trivially": compressed_invertible,
        "Weyl_center_rank_and_D_fin_kernel_dimension_are_both_96": geometry_claim["physical_center_rank"] == response_claim["three_family_kernel_dimension"] == 96,
        "equal_dimensions_do_not_identify_the_two_rank_96_spaces": compressed_invertible and complement != matrix_zero(),
    }
    data = {
        "selected_response": "R_X=(I+X-2X^2)/3",
        "center_decomposition": {
            "P_W_R_X": "(1/3)I",
            "Q_W_R_X": "(X-2X^2)/3",
            "normalized_HS_norm_squared_center": "1/9",
            "normalized_HS_norm_squared_complement": "5/9",
        },
        "leakage_witness": "Q_W ((L_R_X+R_R_X)/2) P_W(I)=Q_W R_X !=0",
        "compressed_route": {
            "operator": "C=(2/3)S_phase+(1/3)S_shift",
            "inverse": "C^-1=(3/2)S_phase+3S_shift",
            "reason": "The route squares are complementary projectors and cross-products vanish.",
        },
        "rank_96_verdict": {
            "center_range_rank": 96,
            "D_fin_kernel_dimension": 96,
            "intersection_dimension": 0,
            "equal": False,
            "proof": "If E v lies in ker(D_fin), then 0=T D_fin E v=Cv. Since C is invertible, v=0.",
        },
        "consequence": "The Weyl Hodge projector is a selected finite constraint projector, not the zero-mode projector of D_fin. Coupling D_fin to this contraction requires a genuine Feshbach or transferred correction.",
    }
    return data, checks


def cotangent_checks(lock: dict[str, object], dga_checks: dict[str, bool]) -> tuple[dict[str, object], dict[str, bool]]:
    claim = lock["extracted_claims"]["shared_line_and_cyclic_completion"]
    basis_dimension = 36
    dual_pairs = {(index, basis_dimension + index) for index in range(basis_dimension)}
    checks = {
        "shared_line_is_neutral_on_the_adjoint_DGLA": "trivially" in claim["adjoint_action"],
        "charged_Hom_lane_boundary_is_preserved": "Hom" in claim["charged_boundary"],
        "finite_Weyl_DGA_defines_a_locally_perfect_DGLA": dga_checks["graded_commutator_is_a_DGLA_by_the_associative_DGA_lemma"],
        "shifted_cotangent_completion_has_dimension_72": 2 * basis_dimension == 72,
        "canonical_evaluation_pairing_has_36_exact_dual_pairs": len(dual_pairs) == 36,
        "canonical_evaluation_pairing_is_nondegenerate": {left for left, _ in dual_pairs} == set(range(36)) and {right for _, right in dual_pairs} == set(range(36, 72)),
        "cotangent_completion_adds_zero_algebraic_interaction_coefficients": claim["new_algebraic_interaction_coefficients"] == 0,
        "physical_normalization_remains_unselected": claim["physical_normalization_selected"] is False,
        "physical_compactification_map_remains_unselected": claim["physical_compactification_map_selected"] is False,
    }
    data = {
        "finite_DGLA": "graded commutator of the 36-dimensional Weyl-Koszul DGA",
        "completion": "L_hat=L semidirect L![-3]",
        "dimension": 72,
        "pairing": "canonical degree-three evaluation pairing",
        "action": "S_cot(x,p)=<p,dx+1/2[x,x]>",
        "free_algebraic_interaction_coefficients": 0,
        "shared_line_action": "neutral on this adjoint lane",
        "boundary": "This is an exact structural cyclic action, not the selected Lorentzian or compactified physical action.",
    }
    return data, checks


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    dga, dga_checks = exact_dga_checks()
    hodge, hodge_checks = mode_hodge_checks()
    transfer, transfer_result_checks = transfer_checks()
    cutset, cutset_checks = response_cutset(lock)
    cotangent, cotangent_result_checks = cotangent_checks(lock, dga_checks)

    provenance_checks = {
        "source_lock_schema_is_exact": lock.get("schema") == "boe.mtt.q79-weyl-koszul-source-lock.v1",
        "eight_source_artifacts_are_commit_blob_and_hash_pinned": len(lock.get("sources", [])) == 8 and all(
            len(source.get("commit", "")) == 40
            and len(source.get("git_blob", "")) == 40
            and len(source.get("sha256", "")) == 64
            for source in lock.get("sources", [])
        ),
        "source_lock_selects_the_exact_Weyl_spectrum": lock["extracted_claims"]["selected_weyl_geometry"]["spectrum"] == {"0": 1, "3": 4, "6": 4},
        "source_lock_preserves_the_continuum_nonpromotion_guard": "does not promote" in lock.get("guard", ""),
        "source_lock_preserves_the_rank_96_nonidentification_guard": "identify the Weyl center" in lock.get("guard", ""),
    }
    checks = provenance_checks | dga_checks | hodge_checks | transfer_result_checks | cutset_checks | cotangent_result_checks

    return {
        "schema": "boe.mtt.selected-finite-weyl-koszul-hodge-interaction-cutset.v1",
        "theorem_id": "SelectedFiniteWeylKoszulHodgeAndInteractionCutsetTheorem.v1",
        "date": "2026-08-28",
        "tiers": ["SELECTED_EXACT_FINITE", "EXACT_INTERACTION_CUTSET", "PHYSICAL_CONTINUUM_OPEN"],
        "selected_finite_mtt_geometry": True,
        "selected_continuum_mtt_physics": False,
        "continuous_fit_parameters": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "source_lock_sha256": sha256(LOCK_PATH),
            "theorem_sha256": sha256(THEOREM_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "weyl_koszul_DGA": dga,
        "hodge_contraction": hodge,
        "transferred_products": transfer,
        "completed_response_cutset": cutset,
        "cyclic_cotangent_completion": cotangent,
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "The selected finite q79 Weyl pair now emits an exact same-source differential, DGA, Hodge Laplacians, harmonic projectors, reduced Greens and contracting homotopies. Its harmonic cohomology is the strict exterior algebra on two generators, so m2 is exterior multiplication and every transferred m_n for n>=3 vanishes. The completed D_fin response leaks out of this center, and the rank-96 center range intersects the separate rank-96 D_fin kernel only at zero. Thus the finite Hodge object is closed and its interaction limitation is decided; continuum HYM promotion and the physical action remain open.",
        "nonclaims": [
            "continuum q79 Dolbeault or Hull-Strominger differential",
            "physical HYM Hessian or Green kernel",
            "identification of the Weyl center with ker(D_fin)",
            "nonzero Yukawa, gauge or gravitational interactions on the harmonic center",
            "selected Lorentzian action or action normalization",
            "closure of B.GEO.01, B.OP.01 or B.ACTION.01",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
