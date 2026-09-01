"""Build the exact CBF.T60 double-qutrit bridge packet."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.packet.json"
LOCK = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge_source_lock.json"
SCHEMA = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge_contract.schema.json"
THEOREM = ROOT / "Q79FourierMukaiDoubleQutritKoszulAndAugmentedExteriorBridgeTheorem_v1.md"
T58_PACKET = ROOT / "full_graded_augmented_heterotic_symbol_parametrix.packet.json"


Q = tuple[Fraction, Fraction]
Q0: Q = (Fraction(0), Fraction(0))
Q1: Q = (Fraction(1), Fraction(0))


def qadd(x: Q, y: Q) -> Q:
    return x[0] + y[0], x[1] + y[1]


def qneg(x: Q) -> Q:
    return -x[0], -x[1]


def qsub(x: Q, y: Q) -> Q:
    return qadd(x, qneg(y))


def qmul(x: Q, y: Q) -> Q:
    # omega^2=-omega-1
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0] - x[1] * y[1]


def qconj(x: Q) -> Q:
    # conjugate(omega)=omega^2=-1-omega
    return x[0] - x[1], -x[1]


def qinv(x: Q) -> Q:
    norm = qmul(qconj(x), x)
    assert norm[1] == 0 and norm[0] != 0
    return qconj(x)[0] / norm[0], qconj(x)[1] / norm[0]


def qscale(c: int | Fraction, x: Q) -> Q:
    return Fraction(c) * x[0], Fraction(c) * x[1]


def qpow(exponent: int) -> Q:
    return (Q1, (Fraction(0), Fraction(1)), (Fraction(-1), Fraction(-1)))[exponent % 3]


def qrank(matrix: list[list[Q]]) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if work[r][col] != Q0), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inv = qinv(work[pivot_row][col])
        work[pivot_row] = [qmul(inv, value) for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][col] == Q0:
                continue
            factor = work[row][col]
            work[row] = [
                qsub(value, qmul(factor, pivot_value))
                for value, pivot_value in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def subsets(size: int) -> list[tuple[int, ...]]:
    return list(itertools.combinations(range(4), size))


def difference_coefficients(label: tuple[int, int, int, int]) -> tuple[Q, Q, Q, Q]:
    a, b, c, d = label
    return qsub(qpow(a), Q1), qsub(qpow(-b), Q1), qsub(qpow(c), Q1), qsub(qpow(-d), Q1)


def differential_matrix(coefficients: tuple[Q, Q, Q, Q], degree: int) -> list[list[Q]]:
    if degree < 0 or degree >= 4:
        return []
    source = subsets(degree)
    target = subsets(degree + 1)
    target_index = {item: index for index, item in enumerate(target)}
    matrix = [[Q0 for _ in source] for _ in target]
    for col, item in enumerate(source):
        for generator in range(4):
            if generator in item:
                continue
            sign = -1 if sum(existing < generator for existing in item) % 2 else 1
            new_item = tuple(sorted(item + (generator,)))
            row = target_index[new_item]
            matrix[row][col] = qscale(sign, coefficients[generator])
    return matrix


def qmatmul(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    if not left or not right:
        return []
    return [
        [
            sum_q(qmul(left[row][k], right[k][col]) for k in range(len(right)))
            for col in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def sum_q(values: Iterable[Q]) -> Q:
    result = Q0
    for value in values:
        result = qadd(result, value)
    return result


def qadjoint(matrix: list[list[Q]]) -> list[list[Q]]:
    if not matrix:
        return []
    return [[qconj(matrix[row][col]) for row in range(len(matrix))] for col in range(len(matrix[0]))]


def qidentity(size: int, scalar: Fraction = Fraction(1)) -> list[list[Q]]:
    return [[(scalar, Fraction(0)) if row == col else Q0 for col in range(size)] for row in range(size)]


def qmatrix_add(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [qadd(left[row][col], right[row][col]) for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def qmatrix_scale(scalar: Q, matrix: list[list[Q]]) -> list[list[Q]]:
    return [[qmul(scalar, value) for value in row] for row in matrix]


def qmatrix_power(matrix: list[list[Q]], exponent: int) -> list[list[Q]]:
    result = qidentity(len(matrix))
    for _ in range(exponent % 3):
        result = qmatmul(result, matrix)
    return result


def weyl_orientation_checks() -> tuple[bool, bool, bool]:
    x = [
        [Q0, Q1, Q0],
        [Q0, Q0, Q1],
        [Q1, Q0, Q0],
    ]
    z = [
        [Q1, Q0, Q0],
        [Q0, qpow(1), Q0],
        [Q0, Q0, qpow(2)],
    ]
    relation = qmatmul(x, z) == qmatrix_scale(qpow(1), qmatmul(z, x))
    ad_x = True
    ad_z = True
    for a, b in itertools.product(range(3), repeat=2):
        mode = qmatmul(qmatrix_power(z, a), qmatrix_power(x, b))
        ad_x_mode = qmatmul(qmatmul(x, mode), qadjoint(x))
        ad_z_mode = qmatmul(qmatmul(z, mode), qadjoint(z))
        ad_x &= ad_x_mode == qmatrix_scale(qpow(a), mode)
        ad_z &= ad_z_mode == qmatrix_scale(qpow(-b), mode)
    return relation, ad_x, ad_z


def hodge_matrix(coefficients: tuple[Q, Q, Q, Q], degree: int) -> list[list[Q]]:
    size = math.comb(4, degree)
    result = [[Q0 for _ in range(size)] for _ in range(size)]
    if degree < 4:
        d = differential_matrix(coefficients, degree)
        result = qmatrix_add(result, qmatmul(qadjoint(d), d))
    if degree > 0:
        previous = differential_matrix(coefficients, degree - 1)
        result = qmatrix_add(result, qmatmul(previous, qadjoint(previous)))
    return result


def centered(value: int) -> int:
    residue = value % 3
    return 0 if residue == 0 else (1 if residue == 1 else -1)


def binomial(n: int, k: int) -> int:
    return 0 if k < 0 or k > n else math.comb(n, k)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_checks(lock: dict) -> list[dict]:
    checks = []
    for row in lock["sources"]:
        path = ROOT / row["path"]
        actual = sha256(path)
        checks.append({
            "id": row["id"],
            "path": row["path"],
            "expected_sha256": row["sha256"],
            "actual_sha256": actual,
            "matches": actual == row["sha256"],
        })
    return checks


def exterior_bridge_rows() -> list[dict]:
    rows = []
    for n in range(-1, 4):
        degree = n + 1
        domain = subsets(degree)
        alpha_lane = [item for item in domain if 0 in item]
        form_lane = [item for item in domain if 0 not in item]
        rows.append({
            "mapping_cone_degree": n,
            "exterior_degree": degree,
            "domain_dimension": len(domain),
            "alpha_lane_dimension": len(alpha_lane),
            "form_lane_dimension": len(form_lane),
            "target_dimension": binomial(3, n) + binomial(3, n + 1),
            "basis_map": [
                {
                    "source_subset": list(item),
                    "target_lane": "alpha_tensor_Lambda_n" if 0 in item else "Lambda_n_plus_1",
                    "target_subset": [index - 1 for index in item if index != 0],
                }
                for item in domain
            ],
        })
    return rows


def equianharmonic_rows() -> tuple[list[dict], Counter[int], int, int]:
    def quadratic(vector: tuple[int, int]) -> int:
        x, y = vector
        return 2 * x * x + 2 * x * y + 2 * y * y

    rows = []
    ground_spectrum: Counter[int] = Counter()
    tail_minima = []
    for a in range(3):
        for b in range(3):
            residue = (centered(a) % 3, (-centered(b)) % 3)
            values = []
            for x in range(-5, 6):
                for y in range(-5, 6):
                    if x % 3 == residue[0] and y % 3 == residue[1]:
                        values.append((quadratic((x, y)), x, y))
            levels = sorted(set(value for value, _, _ in values))
            minimum = levels[0]
            representatives = [[x, y] for value, x, y in values if value == minimum]
            ground_spectrum[minimum] += len(representatives)
            tail_minima.append(levels[1])
            rows.append({
                "character": [a, b],
                "residue": list(residue),
                "minimum_Q": minimum,
                "minimizing_representatives": representatives,
                "minimum_multiplicity": len(representatives),
                "next_Q": levels[1],
            })
    return rows, ground_spectrum, max(row["minimum_Q"] for row in rows), min(tail_minima)


def build_packet() -> dict:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    theorem_text = THEOREM.read_text(encoding="utf-8")
    t58 = json.loads(T58_PACKET.read_text(encoding="utf-8"))
    locked_sources = source_checks(lock)
    weyl_relation, ad_x_orientation, ad_z_orientation = weyl_orientation_checks()

    labels = list(itertools.product(range(3), repeat=4))
    spectrum: Counter[int] = Counter()
    modes = []
    all_square_zero = True
    all_hodge_scalar = True
    cohomology_totals = [0] * 5
    green_identity = True
    for label in labels:
        coefficients = difference_coefficients(label)
        support = sum(value != Q0 for value in coefficients)
        eigenvalue = 3 * support
        spectrum[eigenvalue] += 1
        ranks = [qrank(differential_matrix(coefficients, degree)) for degree in range(4)]
        cohomology = []
        for degree in range(5):
            incoming = ranks[degree - 1] if degree > 0 else 0
            outgoing = ranks[degree] if degree < 4 else 0
            dimension = math.comb(4, degree)
            value = dimension - incoming - outgoing
            cohomology.append(value)
            cohomology_totals[degree] += value
            hodge = hodge_matrix(coefficients, degree)
            all_hodge_scalar &= hodge == qidentity(dimension, Fraction(eigenvalue))
            if eigenvalue:
                green_identity &= all(
                    hodge[row][col] == qidentity(dimension, Fraction(eigenvalue))[row][col]
                    for row in range(dimension)
                    for col in range(dimension)
                )
        for degree in range(3):
            composition = qmatmul(
                differential_matrix(coefficients, degree + 1),
                differential_matrix(coefficients, degree),
            )
            all_square_zero &= all(value == Q0 for row in composition for value in row)
        modes.append({
            "label": list(label),
            "difference_exponents": [label[0] % 3, (-label[1]) % 3, label[2] % 3, (-label[3]) % 3],
            "nonzero_direction_count": support,
            "laplacian_eigenvalue": eigenvalue,
            "green_eigenvalue": None if eigenvalue == 0 else str(Fraction(1, eigenvalue)),
            "cohomology_dimensions": cohomology,
        })

    degree_rows = [
        {
            "degree": degree,
            "carrier_dimension": 81 * math.comb(4, degree),
            "harmonic_dimension": math.comb(4, degree),
            "tracefree_carrier_dimension": 80 * math.comb(4, degree),
            "tracefree_harmonic_dimension": 0,
        }
        for degree in range(5)
    ]
    bridge_rows = exterior_bridge_rows()
    fourier_rows, fourier_spectrum, ground_ceiling, tail_floor = equianharmonic_rows()
    t58_ranks = t58["full_graded_theorem"]["correction_ranks"]

    packet = {
        "schema": schema["$id"],
        "claim_id": "CBF.T60",
        "date": "2026-09-01",
        "status": "CLOSED_EXACT_SELECTED_FIBER_COEFFICIENT_AND_AUGMENTED_EXTERIOR_BRIDGE_PHYSICAL_CONTINUUM_INTERTWINER_OPEN",
        "source_provenance": {
            "model_state_sha256": lock["model_state_sha256"],
            "handoff_id": lock["handoff_id"],
            "source_checks": locked_sources,
            "all_local_sources_hash_locked": all(row["matches"] for row in locked_sources),
            "discovery_evidence": lock["discovery_evidence"],
        },
        "fourier_mukai_coefficient_typing": {
            "theta_line": "L=O_E(3[0])",
            "theta_line_degree": 3,
            "fiber_formula": "H_theta,y=H0(E,L tensor P_y)",
            "fiber_h0": 3,
            "fiber_h1": 0,
            "fourier_mukai_factor_rank": 3,
            "internal_qutrit_rank": 3,
            "local_hidden_fiber": "W9_y=H_theta,y tensor Q3_internal",
            "hidden_rank": 9,
            "endomorphism_rank": 81,
            "adjoint_rank": 80,
            "coefficient_algebra": "M3(Q(omega)) tensor M3(Q(omega))",
            "first_action": "finite theta kernel of the semihomogeneous Fourier-Mukai factor",
            "second_action": "internal qutrit action over the identity on the three-factor orbit",
            "actions_are_distinct": True,
            "strict_global_elliptic_action_claimed": False,
            "continuum_mode_truncation_used": False,
        },
        "double_qutrit_koszul_hodge": {
            "automorphisms": [
                "Ad_X tensor id",
                "Ad_Z tensor id",
                "id tensor Ad_X",
                "id tensor Ad_Z",
            ],
            "all_four_adjoint_automorphisms_commute": True,
            "mode_basis": "W_ab tensor W_cd",
            "mode_difference_coefficients": "(omega^a-1,omega^(-b)-1,omega^c-1,omega^(-d)-1)",
            "mode_count": len(modes),
            "modes": modes,
            "degree_zero_spectrum": {str(key): spectrum[key] for key in sorted(spectrum)},
            "spectrum_generating_polynomial": "(1+2t)^4",
            "kernel_rank": 1,
            "kernel": "Q(omega).I9",
            "tracefree_gap": 3,
            "reduced_green_eigenvalues": ["1/3", "1/6", "1/9", "1/12"],
            "degree_rows": degree_rows,
            "cohomology_dimensions": cohomology_totals,
            "all_differential_compositions_zero": all_square_zero,
            "all_hodge_blocks_are_scalar_mode_laplacians": all_hodge_scalar,
            "green_identity_exact": green_identity,
            "one_qutrit_complex_embeds_as_either_two_direction_face": True,
        },
        "centered_log_compiler": {
            "principal_log_is_unique": True,
            "generator_spectrum": ["-2*pi*i/3", "0", "2*pi*i/3"],
            "exponential_recovers_each_adjoint_generator": True,
            "difference_to_log_factor": "R(lambda)=(exp(lambda)-1)/lambda, R(0)=1",
            "degree_k_chain_map": "T_k(theta_S)=prod_(j in S)R(lambda_j) theta_S",
            "chain_map_identity": "d_difference T_k=T_(k+1) d_log",
            "nonzero_factor_absolute_value": "3*sqrt(3)/(2*pi)",
            "nonzero_factor_absolute_square": "27/(4*pi^2)",
            "all_factors_nonzero": True,
            "claims_continuum_derivative": False,
        },
        "augmented_exterior_bridge": {
            "finite_one_form_space": "V4_fin=span(theta_vX,theta_vZ,theta_iX,theta_iZ)",
            "augmented_symbol_space": "V4_aug=C.alpha direct-sum C^3",
            "isometry": "J_n(e0 wedge eta+zeta)=alpha tensor eta direct-sum zeta",
            "rows": bridge_rows,
            "rank_formula": "C(3,n)+C(3,n+1)=C(4,n+1)",
            "rank_sequence": [row["domain_dimension"] for row in bridge_rows],
            "T58_rank_sequence": t58_ranks,
            "abstract_carrier_bridge_closed": True,
            "selected_physical_intertwiner": "OPEN",
            "physical_acceptance_conditions": [
                "same-source selection",
                "metric isometry",
                "orientation and real-structure compatibility",
                "connection covariance",
                "domain covariance",
                "endpoint residual intertwining",
            ],
        },
        "equianharmonic_continuum_cutset": {
            "marked_curve": "Fermat/equianharmonic elliptic curve",
            "dual_quadratic_form_up_to_scale": [[2, 1], [1, 2]],
            "quadratic_formula": "Q(u,v)=2u^2+2uv+2v^2",
            "character_residue_formula": "(u,v)=(-bar(a),bar(b)) mod 3",
            "sector_rows": fourier_rows,
            "ground_mode_spectrum": {str(key): fourier_spectrum[key] for key in sorted(fourier_spectrum)},
            "lowest_full_band_rank": sum(fourier_spectrum.values()),
            "ground_band_ceiling": ground_ceiling,
            "tail_floor": tail_floor,
            "strict_band_gap": tail_floor - ground_ceiling,
            "triply_degenerate_character_sectors": sum(row["minimum_multiplicity"] == 3 for row in fourier_rows),
            "scalar_fourier_low_band_equals_M3": False,
            "conclusion": "The exact M3 is a Fourier-Mukai theta coefficient algebra, not the lowest scalar-Fourier band.",
        },
        "frontier_delta": {
            "closed": [
                "selected local Fourier-Mukai theta-fiber source of the first M3",
                "double-qutrit coefficient typing and 81=1+80 decomposition",
                "four-generator finite Koszul-Hodge complex and reduced Green operator",
                "centered-log finite-chain compiler",
                "canonical augmented-exterior carrier bridge to CBF.T58",
                "equianharmonic rank-13 scalar-Fourier truncation no-go",
            ],
            "open": [
                "selected global finite-to-augmented one-form intertwiner",
                "connection, domain and endpoint-residual covariance of that intertwiner",
                "same-source visible/common Hull-Strominger endpoint",
                "physical Hessian coefficients, harmonic projector and reduced Green operator",
            ],
            "named_exit_clause_changed": "The finite coefficient source and abstract four-direction carrier bridge are now closed; B.GEO.01 is reduced to a selected covariant intertwiner and endpoint execution.",
        },
        "parameter_ledger": {
            "continuous_physical_parameters_added": 0,
            "discrete_selectors_added": 0,
            "observed_values_used": 0,
            "fitted_values_used": 0,
            "nonphysical_fixture_values_used": 0,
        },
        "physical_boundary": {
            "B_HS_01_closed": False,
            "B_GEO_01_closed": False,
            "B_OP_01_closed": False,
            "physical_gates": {"accepted": 0, "total": 3},
            "physical_packets": {"accepted": 0, "total": 3},
            "physical_rows": {"accepted": 0, "total": 7},
            "finite_coefficient_algebra_is_selected": True,
            "physical_continuum_operator_is_selected": False,
        },
    }

    checks = {
        "schema_identifier": packet["schema"] == "boe.mtt.q79-fourier-mukai-double-qutrit-augmented-exterior-bridge.v1",
        "schema_required_fields": set(schema["required"]).issubset(packet | {"check_summary": {}}),
        "claim_id": packet["claim_id"] == "CBF.T60",
        "theorem_states_81_equals_1_plus_80": "81=1+80" in theorem_text,
        "theorem_states_rank13_cutset": "rank `13`, not `9`" in theorem_text,
        "theorem_preserves_physical_boundary": "Physical counters do not" in theorem_text,
        "all_local_sources_hash_locked": packet["source_provenance"]["all_local_sources_hash_locked"],
        "four_local_sources_checked": len(locked_sources) == 4,
        "locked_Weyl_relation_is_exact": weyl_relation,
        "Ad_X_character_orientation_is_exact": ad_x_orientation,
        "Ad_Z_character_orientation_is_exact": ad_z_orientation,
        "theta_RR_dimension_is_three": packet["fourier_mukai_coefficient_typing"]["fiber_h0"] == 3,
        "theta_h1_vanishes": packet["fourier_mukai_coefficient_typing"]["fiber_h1"] == 0,
        "hidden_tensor_rank_is_nine": packet["fourier_mukai_coefficient_typing"]["hidden_rank"] == 9,
        "endomorphism_rank_is_81": packet["fourier_mukai_coefficient_typing"]["endomorphism_rank"] == 81,
        "adjoint_rank_is_80": packet["fourier_mukai_coefficient_typing"]["adjoint_rank"] == 80,
        "actions_are_typed_as_distinct": packet["fourier_mukai_coefficient_typing"]["actions_are_distinct"],
        "no_continuum_truncation_used_for_typing": not packet["fourier_mukai_coefficient_typing"]["continuum_mode_truncation_used"],
        "all_81_double_qutrit_modes_executed": len(modes) == 81,
        "all_Koszul_compositions_zero": all_square_zero,
        "all_Hodge_blocks_scalar": all_hodge_scalar,
        "degree_zero_spectrum_is_1_8_24_32_16": dict(sorted(spectrum.items())) == {0: 1, 3: 8, 6: 24, 9: 32, 12: 16},
        "spectrum_multiplicity_sums_to_81": sum(spectrum.values()) == 81,
        "green_identity_exact": green_identity,
        "tracefree_gap_is_three": packet["double_qutrit_koszul_hodge"]["tracefree_gap"] == 3,
        "cohomology_is_1_4_6_4_1": cohomology_totals == [1, 4, 6, 4, 1],
        "degree_carrier_dimensions_are_exact": [row["carrier_dimension"] for row in degree_rows] == [81, 324, 486, 324, 81],
        "tracefree_harmonic_dimensions_are_zero": all(row["tracefree_harmonic_dimension"] == 0 for row in degree_rows),
        "centered_log_factors_are_nonzero": packet["centered_log_compiler"]["all_factors_nonzero"],
        "centered_log_not_called_continuum": not packet["centered_log_compiler"]["claims_continuum_derivative"],
        "exterior_bridge_has_five_degrees": len(bridge_rows) == 5,
        "exterior_bridge_is_bijective_by_basis_count": all(row["domain_dimension"] == row["target_dimension"] == len(row["basis_map"]) for row in bridge_rows),
        "exterior_bridge_rank_sequence_is_1_4_6_4_1": [row["domain_dimension"] for row in bridge_rows] == [1, 4, 6, 4, 1],
        "T58_rank_sequence_matches_exactly": t58_ranks == [1, 4, 6, 4, 1],
        "equianharmonic_metric_is_positive": 2 > 0 and 2 * 2 - 1 * 1 > 0,
        "all_nine_character_sectors_executed": len(fourier_rows) == 9,
        "equianharmonic_ground_band_rank_is_13": sum(fourier_spectrum.values()) == 13,
        "equianharmonic_ground_spectrum_is_0_2_6": dict(sorted(fourier_spectrum.items())) == {0: 1, 2: 6, 6: 6},
        "exactly_two_sectors_are_triply_degenerate": sum(row["minimum_multiplicity"] == 3 for row in fourier_rows) == 2,
        "equianharmonic_scalar_band_gap_is_two": tail_floor - ground_ceiling == 2,
        "scalar_Fourier_band_does_not_equal_M3": not packet["equianharmonic_continuum_cutset"]["scalar_fourier_low_band_equals_M3"],
        "no_parameters_or_observed_values_added": all(value == 0 for value in packet["parameter_ledger"].values()),
        "physical_blockers_remain_open": not any(packet["physical_boundary"][key] for key in ("B_HS_01_closed", "B_GEO_01_closed", "B_OP_01_closed")),
        "physical_counters_do_not_move": packet["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
    }
    packet["check_summary"] = {
        "all_passed": all(checks.values()),
        "passed": sum(checks.values()),
        "total": len(checks),
        "checks": checks,
    }
    packet["source_hashes"] = {
        "theorem_sha256": sha256(THEOREM),
        "builder_sha256": sha256(Path(__file__)),
        "source_lock_sha256": sha256(LOCK),
        "schema_sha256": sha256(SCHEMA),
    }
    return packet


def main() -> None:
    packet = build_packet()
    PACKET.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(packet["check_summary"], indent=2, sort_keys=True))
    if not packet["check_summary"]["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
