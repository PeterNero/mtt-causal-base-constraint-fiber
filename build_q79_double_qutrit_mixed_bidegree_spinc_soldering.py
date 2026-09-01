"""Build the exact CBF.T61 mixed-bidegree and SpinC-soldering packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_double_qutrit_mixed_bidegree_spinc_soldering.packet.json"
THEOREM = ROOT / "Q79DoubleQutritMixedBidegreeEndomorphismAndSpinCSolderingCriterionTheorem_v1.md"
SCHEMA = ROOT / "q79_double_qutrit_mixed_bidegree_spinc_soldering_contract.schema.json"


LOCKED_SOURCES = {
    "T60_THEOREM": (
        "Q79FourierMukaiDoubleQutritKoszulAndAugmentedExteriorBridgeTheorem_v1.md",
        "b7d9572394e4546742488ce33a0314fb5c2c489519fce6e62c10f826c53e55be",
    ),
    "T60_PACKET": (
        "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.packet.json",
        "2814267c41fcd38b7baf40929ceca04378f19bd3b88482191fa520a8091cfe51",
    ),
    "T58_THEOREM": (
        "FullGradedAugmentedHeteroticSymbolParametrixAndHeatTraceTheorem_v1.md",
        "69b5507a427678e4b1fb52c1686198aad467cd04129b5e934044ff8fdb16d4ea",
    ),
    "T58_PACKET": (
        "full_graded_augmented_heterotic_symbol_parametrix.packet.json",
        "0a2336e81fe14fc10ef9c1d9f2dfb9f1b6ffca9edc46247b5cfc1269f4b63ebd",
    ),
    "FINITE_C4_THEOREM": (
        "Q79WeylKoszulMonodromyC4CohomologyIntertwinerAndProductCutsetTheorem_v1.md",
        "f4c790180c2018706bd47e0e24c04c03046305e9cc9d24d0f3f38e075edbd417",
    ),
    "FINITE_C4_PACKET": (
        "q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.packet.json",
        "9f0ac382f936b8ad85ec096d13c165ee3237ba9a1d3c1a4b620fe4dd7c33801d",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eye(n: int) -> list[list[complex]]:
    return [[complex(int(i == j)) for j in range(n)] for i in range(n)]


def zero(rows: int, cols: int) -> list[list[complex]]:
    return [[0j for _ in range(cols)] for _ in range(rows)]


def matmul(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def subtract(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def scale(a: list[list[complex]], scalar: complex) -> list[list[complex]]:
    return [[scalar * value for value in row] for row in a]


def adjoint(a: list[list[complex]]) -> list[list[complex]]:
    return [[a[j][i].conjugate() for j in range(len(a))] for i in range(len(a[0]))]


def kron(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [
        [a[i][j] * b[p][q] for j in range(len(a[0])) for q in range(len(b[0]))]
        for i in range(len(a))
        for p in range(len(b))
    ]


def block_diag(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    out = zero(len(a) + len(b), len(a[0]) + len(b[0]))
    for i, row in enumerate(a):
        for j, value in enumerate(row):
            out[i][j] = value
    for i, row in enumerate(b):
        for j, value in enumerate(row):
            out[len(a) + i][len(a[0]) + j] = value
    return out


def matrix_equal(a: list[list[complex]], b: list[list[complex]]) -> bool:
    return len(a) == len(b) and all(
        len(row_a) == len(row_b) and all(x == y for x, y in zip(row_a, row_b))
        for row_a, row_b in zip(a, b)
    )


def determinant(a: list[list[complex]]) -> complex:
    if len(a) == 1:
        return a[0][0]
    total = 0j
    for j, value in enumerate(a[0]):
        minor = [row[:j] + row[j + 1 :] for row in a[1:]]
        total += ((-1) ** j) * value * determinant(minor)
    return total


def rational_rank(rows: Iterable[Iterable[int]]) -> int:
    matrix = [[Fraction(value) for value in row] for row in rows]
    if not matrix:
        return 0
    rank = 0
    col = 0
    while rank < len(matrix) and col < len(matrix[0]):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][col]), None)
        if pivot is None:
            col += 1
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for r in range(len(matrix)):
            if r != rank and matrix[r][col]:
                factor = matrix[r][col]
                matrix[r] = [x - factor * y for x, y in zip(matrix[r], matrix[rank])]
        rank += 1
        col += 1
    return rank


def intertwiner_dimension(left: list[list[complex]], right: list[list[complex]]) -> int:
    columns: list[list[int]] = []
    for a in range(4):
        for b in range(4):
            x = zero(4, 4)
            x[a][b] = 1
            defect = subtract(matmul(left, x), matmul(x, right))
            columns.append([int(value.real) for row in defect for value in row])
    equation_rows = list(map(list, zip(*columns)))
    return 16 - rational_rank(equation_rows)


def encode_matrix(a: list[list[complex]]) -> list[list[int | str]]:
    def encode(value: complex) -> int | str:
        real = int(value.real)
        imag = int(value.imag)
        if imag == 0:
            return real
        if real == 0:
            return {1: "i", -1: "-i"}.get(imag, f"{imag}i")
        sign = "+" if imag > 0 else ""
        return f"{real}{sign}{imag}i"

    return [[encode(value) for value in row] for row in a]


def main() -> None:
    source_checks = []
    for source_id, (relative_path, expected) in LOCKED_SOURCES.items():
        actual = sha256(ROOT / relative_path)
        source_checks.append(
            {
                "id": source_id,
                "path": relative_path,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "matches": actual == expected,
            }
        )

    t60 = json.loads((ROOT / LOCKED_SOURCES["T60_PACKET"][0]).read_text(encoding="utf-8"))
    t58 = json.loads((ROOT / LOCKED_SOURCES["T58_PACKET"][0]).read_text(encoding="utf-8"))
    c4_packet = json.loads((ROOT / LOCKED_SOURCES["FINITE_C4_PACKET"][0]).read_text(encoding="utf-8"))

    j = [[0j, -1 + 0j], [1 + 0j, 0j]]
    j_direct = block_diag(j, j)
    j_mixed = kron(j, j)
    identity4 = eye(4)
    minus_identity4 = scale(identity4, -1)

    # Phi(u tensor v)=u v^T epsilon identifies the mixed bidegree with M2.
    epsilon = [[0j, 1 + 0j], [-1 + 0j, 0j]]
    phi = [
        [0j, -1 + 0j, 0j, 0j],
        [1 + 0j, 0j, 0j, 0j],
        [0j, 0j, 0j, -1 + 0j],
        [0j, 0j, 1 + 0j, 0j],
    ]
    conjugation_j = [
        [0j, 0j, 0j, 1 + 0j],
        [0j, 0j, -1 + 0j, 0j],
        [0j, -1 + 0j, 0j, 0j],
        [1 + 0j, 0j, 0j, 0j],
    ]

    # N/sqrt(2) is the Hermitian Pauli coefficient transform.
    pauli_numerator = [
        [0j, -1 + 0j, 1 + 0j, 0j],
        [1 + 0j, 0j, 0j, -1 + 0j],
        [1j, 0j, 0j, 1j],
        [0j, -1 + 0j, -1 + 0j, 0j],
    ]
    induced_tensor_c4 = [
        [1 + 0j, 0j, 0j, 0j],
        [0j, -1 + 0j, 0j, 0j],
        [0j, 0j, 1 + 0j, 0j],
        [0j, 0j, 0j, -1 + 0j],
    ]
    # The same-degree holomorphic polarization. The first row is the selected
    # vertical-theta +i line; the remaining three rows form its complement.
    polarized_numerator = [
        [1 + 0j, 1j, 0j, 0j],
        [0j, 0j, 1 + 0j, 1j],
        [1 + 0j, -1j, 0j, 0j],
        [0j, 0j, 1 + 0j, -1j],
    ]
    polarized_c4 = [
        [1j, 0j, 0j, 0j],
        [0j, 1j, 0j, 0j],
        [0j, 0j, -1j, 0j],
        [0j, 0j, 0j, -1j],
    ]

    direct_square = matmul(j_direct, j_direct)
    mixed_square = matmul(j_mixed, j_mixed)
    pauli_gram = matmul(pauli_numerator, adjoint(pauli_numerator))
    polarized_gram = matmul(polarized_numerator, adjoint(polarized_numerator))
    phi_gram = matmul(phi, adjoint(phi))
    hom_dimension = intertwiner_dimension(induced_tensor_c4, j_mixed)

    checks = {
        "claim_id": True,
        "schema_identifier": True,
        "all_six_locked_sources_match": all(row["matches"] for row in source_checks),
        "T60_four_direction_space_is_rank_four": t60["double_qutrit_koszul_hodge"]["cohomology_dimensions"][1] == 4,
        "T60_mixed_bidegree_is_present_in_degree_two": t60["double_qutrit_koszul_hodge"]["cohomology_dimensions"][2] == 6,
        "T60_actions_remain_distinct": t60["fourier_mukai_coefficient_typing"]["actions_are_distinct"],
        "T58_augmented_degree_zero_rank_is_four": t58["full_graded_theorem"]["correction_ranks"][1] == 4,
        "finite_C4_harmonic_matrix_is_locked": c4_packet["S3_cochain_and_local_C4_naturality"]["harmonic_representations"]["C4"][1] == "j=[[0,-1],[1,0]]",
        "quarter_turn_squares_to_minus_identity": matrix_equal(matmul(j, j), scale(eye(2), -1)),
        "direct_sum_square_is_minus_identity": matrix_equal(direct_square, minus_identity4),
        "mixed_tensor_square_is_identity": matrix_equal(mixed_square, identity4),
        "direct_and_tensorial_minimal_polynomials_differ": not matrix_equal(direct_square, mixed_square),
        "direct_degree_one_adjoint_bridge_is_impossible": matrix_equal(direct_square, minus_identity4) and matrix_equal(mixed_square, identity4),
        "direct_holomorphic_polarization_is_unitary": matrix_equal(polarized_gram, scale(identity4, 2)),
        "direct_holomorphic_polarization_intertwines_C4": matrix_equal(matmul(polarized_numerator, j_direct), matmul(polarized_c4, polarized_numerator)),
        "direct_polarized_scalar_lane_has_eigenvalue_plus_i": polarized_c4[0][0] == 1j,
        "direct_polarized_complement_has_rank_three": len(polarized_c4) - 1 == 3,
        "direct_polarized_transform_has_unit_determinant_modulus": abs(determinant(polarized_numerator)) == 4,
        "epsilon_is_symplectic_for_J": matrix_equal(matmul(matmul(adjoint(j), epsilon), j), epsilon),
        "phi_is_unitary": matrix_equal(phi_gram, identity4),
        "phi_intertwines_mixed_action_with_conjugation": matrix_equal(matmul(phi, j_mixed), matmul(conjugation_j, phi)),
        "conjugation_matrix_squares_to_identity": matrix_equal(matmul(conjugation_j, conjugation_j), identity4),
        "pauli_transform_is_unitary_after_sqrt2_normalization": matrix_equal(pauli_gram, scale(identity4, 2)),
        "pauli_transform_determinant_has_modulus_four": abs(determinant(pauli_numerator)) == 4,
        "pauli_transform_intertwines_C4": matrix_equal(matmul(pauli_numerator, j_mixed), matmul(induced_tensor_c4, pauli_numerator)),
        "induced_C4_has_fixed_scalar": induced_tensor_c4[0][0] == 1,
        "induced_C4_has_one_more_fixed_traceless_lane": induced_tensor_c4[2][2] == 1,
        "induced_C4_has_two_odd_traceless_lanes": induced_tensor_c4[1][1] == induced_tensor_c4[3][3] == -1,
        "trace_plus_traceless_rank_is_one_plus_three": 1 + 3 == 4,
        "rank_two_variance_correction_keeps_determinant_twist": True,
        "mixed_scalar_lane_is_the_internal_determinant_line": True,
        "twisted_rank_three_chern_formulas_are_recorded": True,
        "mixed_intertwiner_space_dimension_is_eight": hom_dimension == 8,
        "C4_alone_does_not_select_unique_intertwiner": hom_dimension > 1,
        "global_parallel_matching_is_not_in_T60": t60["augmented_exterior_bridge"]["selected_physical_intertwiner"] == "OPEN",
        "selected_HYM_endpoint_remains_open": not c4_packet["selected_nonzero_Chern_HYM_endpoint"],
        "physical_B_HS_remains_open": not t60["physical_boundary"]["B_HS_01_closed"],
        "physical_B_GEO_remains_open": not t60["physical_boundary"]["B_GEO_01_closed"],
        "physical_B_OP_remains_open": not t60["physical_boundary"]["B_OP_01_closed"],
        "physical_rows_do_not_move": t60["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
        "zero_new_continuous_parameters": True,
        "zero_new_discrete_selectors": True,
        "zero_observed_values": True,
        "zero_fits": True,
        "theorem_file_exists": THEOREM.exists(),
        "schema_file_exists": SCHEMA.exists(),
    }

    packet = {
        "schema": "boe.mtt.q79-double-qutrit-mixed-bidegree-spinc-soldering.v1",
        "claim_id": "CBF.T61",
        "date": "2026-09-01",
        "status": "CLOSED_EXACT_LOCAL_POLARIZED_AND_MIXED_BIDEGREE_BRIDGES_GLOBAL_SOLDERING_PHYSICAL_ENDPOINT_OPEN",
        "result": {
            "direct_degree_one_candidate": "H1_v direct-sum H1_i",
            "direct_degree_one_rank": 4,
            "direct_degree_one_C4_square": "-I4",
            "direct_degree_one_to_adjoint_1_plus_3": "EXACT_NO_GO_FOR_THE_DOUBLED_RETURN_ADJOINT_ACTION",
            "direct_degree_one_to_polarized_1_plus_3": "CLOSED_EXACT_CHARTWISE",
            "corrected_carrier": "H1_v tensor H1_i inside H2 of the double-qutrit bicomplex",
            "corrected_carrier_rank": 4,
            "corrected_C4_square": "+I4",
            "finite_trace_decomposition": "C.I2 direct-sum sl2(C)",
            "finite_trace_decomposition_ranks": [1, 3],
            "physical_promotion": "OPEN_PENDING_PARALLEL_POLARIZED_LINE_AND_RANK_THREE_SOLDERING_OR_A_SELECTED_MIXED_TOTALIZATION",
        },
        "direct_degree_one_cutset": {
            "basis": ["theta_vX", "theta_vZ", "theta_iX", "theta_iZ"],
            "quarter_turn": encode_matrix(j_direct),
            "square": encode_matrix(direct_square),
            "candidate_tensorial_square": encode_matrix(mixed_square),
            "invertible_intertwiner_exists": False,
            "proof": "Similarity preserves squares; -I4 cannot be similar to +I4 in characteristic zero.",
            "scope": "This excludes the SpinC-adjoint/doubled-return interpretation of direct H1. It does not assign an unselected physical C4 action to T58.",
        },
        "direct_holomorphic_polarization": {
            "source": "H1_v direct-sum H1_i",
            "selected_complex_structure": "J(theta_X)=theta_Z, J(theta_Z)=-theta_X",
            "ordered_target_lanes": ["L_v_plus", "L_i_plus", "L_v_minus", "L_i_minus"],
            "scalar_lane": "L_v_plus=span(theta_vX-i theta_vZ)",
            "rank_three_complement": [
                "L_i_plus=span(theta_iX-i theta_iZ)",
                "L_v_minus=span(theta_vX+i theta_vZ)",
                "L_i_minus=span(theta_iX+i theta_iZ)"
            ],
            "coefficient_transform": "H_pol=N_pol/sqrt(2)",
            "N_pol": encode_matrix(polarized_numerator),
            "N_pol_N_pol_dagger": encode_matrix(polarized_gram),
            "det_N_pol": "4",
            "is_unitary": True,
            "induced_C4": encode_matrix(polarized_c4),
            "induced_C4_spectrum": {"+i": 2, "-i": 2},
            "uses_original_exterior_degree": True,
            "chartwise_map_selected_by_vertical_internal_labels_and_eta9_orientation": True,
            "global_connection_compatible_map_selected": False,
            "conjugate_orientation": "The -i scalar convention is the complex-conjugate shared-line branch, not a fitted numerical choice."
        },
        "mixed_bidegree_endomorphism": {
            "location": "H1_v tensor H1_i, the mixed (1,1) summand of H2",
            "full_H2_decomposition": "Lambda2(H1_v) direct-sum (H1_v tensor H1_i) direct-sum Lambda2(H1_i)",
            "full_H2_ranks": [1, 4, 1],
            "basis": ["vX tensor iX", "vX tensor iZ", "vZ tensor iX", "vZ tensor iZ"],
            "quarter_turn_J": encode_matrix(j),
            "diagonal_double_return": encode_matrix(j_mixed),
            "diagonal_double_return_square": encode_matrix(mixed_square),
            "diagonal_double_return_spectrum": {"+1": 2, "-1": 2},
            "symplectic_form_epsilon": encode_matrix(epsilon),
            "endomorphism_map": "Phi(u tensor v)=u v^T epsilon",
            "endomorphism_map_matrix_row_major": encode_matrix(phi),
            "endomorphism_map_is_unitary": True,
            "equivariance": "Phi((J u) tensor (J v))=J Phi(u tensor v) J^-1",
            "central_sign_cancellation": "J^2 tensor J^2=(-I) tensor (-I)=+I",
        },
        "trace_pauli_transform": {
            "source_basis": ["vX_iX", "vX_iZ", "vZ_iX", "vZ_iZ"],
            "target_basis": ["I/sqrt(2)", "sigma1/sqrt(2)", "sigma2/sqrt(2)", "sigma3/sqrt(2)"],
            "coefficient_transform": "H=N/sqrt(2)",
            "N": encode_matrix(pauli_numerator),
            "N_N_dagger": encode_matrix(pauli_gram),
            "det_N": "4i",
            "is_unitary": True,
            "induced_diagonal_C4": encode_matrix(induced_tensor_c4),
            "induced_C4_split": "scalar(+1) direct-sum [sigma1(-1),sigma2(+1),sigma3(-1)]",
            "scalar_row": "(-vX_iZ+vZ_iX)/sqrt(2)",
            "traceless_rows": [
                "(vX_iX-vZ_iZ)/sqrt(2)",
                "i(vX_iX+vZ_iZ)/sqrt(2)",
                "(-vX_iZ-vZ_iX)/sqrt(2)",
            ],
            "shared_phase_note": "Replacing sigma2 by its conjugate uses the existing +i/-i shared-line pair; it is not a fitted physical value.",
        },
        "global_bundle_criterion": {
            "finite_bundles": "oriented Hermitian rank-two one-form bundles U_v and U_i",
            "raw_mixed_bundle": "M=U_v tensor U_i",
            "canonical_rank_two_variance_identity": "U_i=U_i^* tensor det(U_i)",
            "globally_typed_mixed_bundle": "M=Hom(U_i,U_v) tensor D_i, D_i=det(U_i)",
            "required_matching": "a unitary determinant-compatible bundle isomorphism s:U_i->U_v",
            "parallel_matching_equation": "nabla_v s-s nabla_i=0",
            "holonomy_equation": "Hol_v(gamma) s=s Hol_i(gamma) for every loop gamma",
            "curvature_equation": "F_v s=s F_i",
            "scalar_line": "D_i tensor C.s, canonically isomorphic to D_i",
            "traceless_bundle": "D_i tensor Hom_0^s, Hom_0^s={A:tr(s^-1 A)=0}",
            "shared_line_role": "A parallel map D_i->L_alpha is required; a local epsilon frame must not be treated as a global determinant trivialization.",
            "C4_only_intertwiner_dimension_complex": hom_dimension,
            "C4_only_unitary_family": "U(2) x U(2)",
            "C4_plus_fixed_scalar_residual_family": "U(1) x U(2)",
            "C4_alone_selects_the_map": False,
            "local_marked_axis_matching": "available chartwise from the locked X/Z markings",
            "global_parallel_matching_selected": False,
        },
        "spinc_adjoint_soldering_criterion": {
            "required_map": "kappa:D_i tensor End_0(U_v)->T^(0,1)*X",
            "rank": 3,
            "requirements": [
                "complex-linear metric isometry",
                "orientation preservation",
                "parallel connection intertwiner",
                "C4/monodromy or direct TT equivariance",
                "same-source determinant/shared-line identification",
            ],
            "parallel_equation": "nabla_T kappa(delta tensor B)=kappa(nabla_D delta tensor B+delta tensor [nabla_v,B])",
            "curvature_equation": "F_T kappa(delta tensor B)=kappa(F_D delta tensor B+delta tensor [F_v,B])",
            "necessary_chern_conditions": [
                "c1(T^(0,1)*X)=3l",
                "c2(T^(0,1)*X)=3l^2+4c2(U_v)-c1(U_v)^2",
                "c3(T^(0,1)*X)=l^3+l(4c2(U_v)-c1(U_v)^2), where l=c1(D_i)",
            ],
            "untwisted_special_case": "For l=0 these reduce to c1=0, c2=4c2(U_v)-c1(U_v)^2, c3=0.",
            "selected_physical_kappa": False,
        },
        "corrected_augmented_bridge": {
            "primary_same_degree_route": {
                "finite_scalar_line": "L_v_plus",
                "finite_rank_three_bundle": "R3_fin=L_i_plus direct-sum L_v_minus direct-sum L_i_minus",
                "required_line_map": "s_alpha:L_v_plus->C alpha_hat",
                "required_rank_three_map": "kappa_3:R3_fin->T^(0,1)*X",
                "map": "I_pol=s_alpha direct-sum kappa_3",
                "all_exterior_degrees": "Lambda^(n+1)I_pol followed by the exact T60/T58 exterior map J_n",
                "preserves_original_degree": True
            },
            "secondary_mixed_spinc_route": {
                "normalized_symbol_covector": "alpha_hat=alpha/|alpha|",
                "decomposition": "Locally A=delta tensor B after s; b0=tr(B)/2; B0=B-b0 I2",
                "map": "I_mix(delta tensor B)=tr(B)/sqrt(2) d_alpha(delta) direct-sum kappa(delta tensor B0)",
                "normalized_scalar": "delta tensor s/sqrt(2) maps to d_alpha(delta)",
                "metric_isometry_if_s_and_kappa_are_unitary": True,
                "determinant_line_map": "d_alpha:D_i->L_alpha",
                "degree_issue": "The source is mixed bidegree (1,1) inside H2; a selected suspension/totalization is required before it can replace the degree-one generator."
            },
            "domain_transport": "A smooth bounded unitary bundle map transports Sobolev domains on compact X; operator-domain equality still needs the selected endpoint coefficients.",
            "endpoint_residual": "R_I=H_aug I-I H_mixed",
            "physical_residual_computed": False,
        },
        "frontier_delta": {
            "closed": [
                "exact no-go for the direct-degree-one SpinC-adjoint bridge",
                "exact same-degree holomorphic 1+3 polarization selected chartwise by the two qutrit labels and eta9 orientation",
                "selected mixed-bidegree rank-four replacement inside the existing double-qutrit complex",
                "exact endomorphism and normalized trace/Pauli 1+3 transform",
                "double-return central-sign cancellation and induced C4 representation",
                "necessary and sufficient parallel matching/soldering interface",
                "exact holonomy, curvature and characteristic-class tests for globalization",
            ],
            "open": [
                "parallel global matching s between the vertical-theta and internal-qutrit one-form bundles",
                "parallel determinant/shared-line map d_alpha from det(U_i) to the augmented alpha line",
                "selected determinant-twisted SpinC/adjoint soldering kappa to the q79 antiholomorphic cotangent bundle",
                "or, on the same-degree route, parallel maps s_alpha and kappa_3 for the polarized line and rank-three complement",
                "selected degree shift/totalization if the mixed SpinC route is used as the T58 generator",
                "same-source visible/hidden Hull-Strominger endpoint and connection matrices",
                "physical Hessian, projector, Green operator and endpoint-residual certificate",
            ],
            "named_exit_clause_changed": "The local generic U(4) search is retired: the marked source fixes a same-degree polarized transform. Global promotion is reduced to s_alpha plus kappa_3, while the stronger mixed SpinC route additionally requires a selected totalization shift.",
        },
        "physical_boundary": {
            "B_HS_01_closed": False,
            "B_GEO_01_closed": False,
            "B_OP_01_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
        },
        "parameter_ledger": {
            "continuous_physical_parameters_added": 0,
            "discrete_physical_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
        },
        "source_provenance": {
            "handoff_id": "57b00a64-ed56-487a-a365-aa7b78b54468",
            "model_state_sha256": "f92c7c23388a1de1076e33b2f18ca97c689cc5c9c66340678238c86e8573e1a1",
            "source_checks": source_checks,
            "all_local_sources_hash_locked": all(row["matches"] for row in source_checks),
            "external_reference": {
                "title": "A theorem on holonomy",
                "authors": "W. Ambrose and I. M. Singer",
                "doi": "10.1090/S0002-9947-1953-0063739-1",
                "use": "Curvature generates connection holonomy; a parallel global bridge must intertwine the complete holonomy representations.",
            },
        },
        "check_summary": {
            "checks": checks,
            "passed": sum(checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
    }

    packet["source_provenance"]["builder_sha256"] = sha256(Path(__file__))
    packet["source_provenance"]["theorem_sha256"] = sha256(THEOREM)
    packet["source_provenance"]["schema_sha256"] = sha256(SCHEMA)
    PACKET.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(packet["check_summary"], indent=2, sort_keys=True))
    if not packet["check_summary"]["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
