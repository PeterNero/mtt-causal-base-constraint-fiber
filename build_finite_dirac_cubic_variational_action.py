#!/usr/bin/env python3
"""Build the exact CBF.T29 cubic variational-action packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import build_upper_totalization_supercharge_selection as uts
import build_weyl_gram_closure_repair_source as wg


ROOT = Path(__file__).resolve().parent
SOURCE_LOCK = ROOT / "finite_dirac_cubic_variational_action_source_lock.json"
SCHEMA = ROOT / "finite_dirac_cubic_variational_action_contract.schema.json"
THEOREM = ROOT / "CanonicalDiracDefectCubicVariationalActionAndKODoublingCancellationTheorem_v1.md"
T20_PACKET = ROOT / "weyl_gram_closure_repair_source.packet.json"
T23_PACKET = ROOT / "physical_yukawa_hessian.packet.json"
T26_PACKET = ROOT / "direct_dirac_defect_repair_action.packet.json"
T27_PACKET = ROOT / "finite_dirac_spectral_action_classification.packet.json"
T28_PACKET = ROOT / "finite_dirac_operator_repair_semigroup.packet.json"
OUTPUT = ROOT / "finite_dirac_cubic_variational_action.packet.json"

cp = wg.cp
Action = Callable[[cp.Matrix], Fraction]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | int) -> cp.K:
    return Fraction(value), Fraction(0), Fraction(0), Fraction(0)


def matrix_sub(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return cp.madd(left, cp.mscale(q(-1), right))


def commutator(left: cp.Matrix, right: cp.Matrix) -> cp.Matrix:
    return matrix_sub(uts.sparse_matmul(left, right), uts.sparse_matmul(right, left))


def matrix_trace(matrix: cp.Matrix) -> cp.K:
    total = cp.ZERO
    for index in range(len(matrix)):
        total = cp.kadd(total, matrix[index][index])
    return total


def real_part(value: cp.K) -> Fraction:
    if value[1:] != (Fraction(0), Fraction(0), Fraction(0)):
        raise AssertionError(f"expected real scalar, received {value}")
    return value[0]


def normalized_trace(matrix: cp.Matrix) -> Fraction:
    return real_part(matrix_trace(matrix)) / len(matrix)


def inner(left: cp.Matrix, right: cp.Matrix) -> Fraction:
    return normalized_trace(uts.sparse_matmul(cp.adjoint(left), right))


def square(value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(value, value)


def cube(value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(square(value), value)


def residual(value: cp.Matrix) -> cp.Matrix:
    return matrix_sub(square(value), cp.identity(len(value)))


def signed_action(value: cp.Matrix) -> Fraction:
    primitive = matrix_sub(cp.mscale(q(Fraction(1, 3)), cube(value)), value)
    return normalized_trace(primitive)


def weighted_action(anchor: cp.Matrix, value: cp.Matrix) -> Fraction:
    primitive = matrix_sub(cp.mscale(q(Fraction(1, 3)), cube(value)), value)
    return normalized_trace(uts.sparse_matmul(anchor, primitive)) + Fraction(2, 3)


def jacobian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(
        uts.sparse_matmul(basepoint, value),
        uts.sparse_matmul(value, basepoint),
    )


def repair_hessian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return jacobian(basepoint, jacobian(basepoint, value))


def positive_repair_gradient(value: cp.Matrix) -> cp.Matrix:
    return cp.mscale(q(2), uts.sparse_matmul(value, residual(value)))


def weighted_gradient(anchor: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    value_squared = square(value)
    terms = cp.madd(
        uts.sparse_matmul(value_squared, anchor),
        cp.madd(
            uts.sparse_matmul(value, uts.sparse_matmul(anchor, value)),
            uts.sparse_matmul(anchor, value_squared),
        ),
    )
    return matrix_sub(cp.mscale(q(Fraction(1, 3)), terms), anchor)


def weighted_hessian(basepoint: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    theta_value = uts.sparse_matmul(
        basepoint, uts.sparse_matmul(value, basepoint)
    )
    return cp.mscale(
        q(Fraction(1, 3)), cp.madd(cp.mscale(q(4), value), cp.mscale(q(2), theta_value))
    )


def material_projectors(basepoint: cp.Matrix) -> tuple[cp.Matrix, cp.Matrix]:
    identity = cp.identity(len(basepoint))
    return (
        cp.mscale(q(Fraction(1, 2)), cp.madd(identity, basepoint)),
        cp.mscale(q(Fraction(1, 2)), matrix_sub(identity, basepoint)),
    )


def pi_plus(e_plus: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(e_plus, uts.sparse_matmul(value, e_plus))


def pi_minus(e_minus: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(e_minus, uts.sparse_matmul(value, e_minus))


def pi_zero(e_plus: cp.Matrix, e_minus: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return cp.madd(
        uts.sparse_matmul(e_plus, uts.sparse_matmul(value, e_minus)),
        uts.sparse_matmul(e_minus, uts.sparse_matmul(value, e_plus)),
    )


def outer(left: list[cp.K], right: list[cp.K]) -> cp.Matrix:
    result = cp.zero(len(left), len(right))
    for row, left_value in enumerate(left):
        for column, right_value in enumerate(right):
            result[row][column] = cp.kmul(left_value, cp.kconj(right_value))
    return result


def nonzero_column(matrix: cp.Matrix) -> list[cp.K]:
    for column in range(len(matrix[0])):
        vector = [matrix[row][column] for row in range(len(matrix))]
        if any(value != cp.ZERO for value in vector):
            return vector
    raise AssertionError("matrix has no nonzero column")


def gamma96() -> cp.Matrix:
    left_slots = {0, 1, 2, 3, 4, 5, 12, 13}
    gamma16 = [-1 if index in left_slots else 1 for index in range(16)]
    gamma48 = gamma16 * 3
    signs = gamma48 + [-value for value in gamma48]
    return cp.diagonal([q(value) for value in signs])


def conjugate_by(unitary: cp.Matrix, value: cp.Matrix) -> cp.Matrix:
    return uts.sparse_matmul(unitary, uts.sparse_matmul(value, cp.adjoint(unitary)))


def cyclic_permutation(size: int) -> cp.Matrix:
    result = cp.zero(size, size)
    for source in range(size):
        result[(source + 1) % size][source] = cp.ONE
    return result


def directional_derivative(action: Action, value: cp.Matrix, direction: cp.Matrix) -> Fraction:
    """Extract the linear coefficient of a cubic action exactly."""

    def evaluate(scale: int) -> Fraction:
        return action(cp.madd(value, cp.mscale(q(scale), direction)))

    return (
        8 * (evaluate(1) - evaluate(-1)) - (evaluate(2) - evaluate(-2))
    ) / 12


def odd_moment(value: cp.Matrix, power: int) -> Fraction:
    if power < 1 or power % 2 == 0:
        raise ValueError("odd positive power required")
    result = cp.identity(len(value))
    for _ in range(power):
        result = uts.sparse_matmul(result, value)
    return normalized_trace(result)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def source_hash_checks(source_lock: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    for index, source in enumerate(source_lock["local_sources"], start=1):
        path = (ROOT / source["path"]).resolve()
        checks[f"source_{index:02d}_hash_matches"] = (
            path.is_file() and sha256(path) == source["sha256"]
        )
    return checks


def source_root(
    source_lock: dict[str, Any],
    theorem_hash: str,
    d0_hash: str,
    d1_hash: str,
    h_hash: str,
    gamma_hash: str,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "schema": "boe.mtt.finite-dirac-cubic-variational-action-root.v1",
        "repository_heads": source_lock["repositories"],
        "source_hashes": [source["sha256"] for source in source_lock["local_sources"]],
        "configuration_space": "End_sa(H_F), dim_R=9216",
        "metric": "g(X,Y)=Re (Tr/96)(X^*Y)",
        "D0_sha256": d0_hash,
        "D1_sha256": d1_hash,
        "H_phys_sha256": h_hash,
        "Gamma96_sha256": gamma_hash,
        "signed_action": "S_sig(D)=tau96(D^3/3-D)",
        "signed_hessian": "H_sig=J0=2Pi_plus-2Pi_minus",
        "normal_square": "H_sig^2=A_rep=4(Pi_plus+Pi_minus)",
        "signed_hessian_inertia": {"negative": 2304, "positive": 2304, "zero": 4608},
        "KO6_pullback": "S_sig(D_phys(t))=0",
        "physical_Lorentzian_or_BV_action": None,
        "observed_targets": [],
        "theorem_sha256": theorem_hash,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest(), payload


def main() -> None:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="ascii"))
    schema = json.loads(SCHEMA.read_text(encoding="ascii"))
    t20 = json.loads(T20_PACKET.read_text(encoding="ascii"))
    t23 = json.loads(T23_PACKET.read_text(encoding="ascii"))
    t26 = json.loads(T26_PACKET.read_text(encoding="ascii"))
    t27 = json.loads(T27_PACKET.read_text(encoding="ascii"))
    t28 = json.loads(T28_PACKET.read_text(encoding="ascii"))

    primitive = t20["primitive_source"]["primitive_payload"]
    projector = wg.decode_matrix(primitive["P"])
    x = wg.decode_matrix(primitive["X"])
    z = wg.decode_matrix(primitive["Z"])
    identity3 = cp.identity(3)
    phase_direction = cp.madd(identity3, z)
    shift_direction = cp.madd(identity3, x)
    d0 = uts.physical_dirac(
        uts.physical_transfer(projector, phase_direction, shift_direction, Fraction(0))
    )
    d_at_one = uts.physical_dirac(
        uts.physical_transfer(projector, phase_direction, shift_direction, Fraction(1))
    )
    d1 = matrix_sub(d_at_one, d0)
    identity96 = cp.identity(96)
    h_phys = jacobian(d0, d1)
    grading = gamma96()
    e_plus, e_minus = material_projectors(d0)

    rank_plus = cp.matrix_rank(e_plus)
    rank_minus = cp.matrix_rank(e_minus)
    positive_dimension = rank_plus**2
    negative_dimension = rank_minus**2
    zero_dimension = 2 * rank_plus * rank_minus

    plus_vector = nonzero_column(e_plus)
    minus_vector = nonzero_column(e_minus)
    positive_sample = outer(plus_vector, plus_vector)
    negative_sample = outer(minus_vector, minus_vector)
    cross = outer(plus_vector, minus_vector)
    zero_sample = cp.madd(cross, cp.adjoint(cross))
    generic_sample = cp.madd(positive_sample, cp.madd(negative_sample, zero_sample))
    samples = {
        "positive": positive_sample,
        "negative": negative_sample,
        "zero": zero_sample,
        "generic": generic_sample,
        "D1": d1,
        "H_phys": h_phys,
    }

    decomposition_checks: dict[str, bool] = {}
    square_checks: dict[str, bool] = {}
    for name, sample in samples.items():
        plus = pi_plus(e_plus, sample)
        minus = pi_minus(e_minus, sample)
        zero = pi_zero(e_plus, e_minus, sample)
        decomposition_checks[f"{name}_three_projectors_resolve"] = cp.madd(
            plus, cp.madd(minus, zero)
        ) == sample
        decomposition_checks[f"{name}_three_projectors_are_pairwise_orthogonal"] = (
            inner(plus, minus) == inner(plus, zero) == inner(minus, zero) == 0
        )
        decomposition_checks[f"{name}_signed_Hessian_decomposes"] = jacobian(
            d0, sample
        ) == matrix_sub(cp.mscale(q(2), plus), cp.mscale(q(2), minus))
        square_checks[f"{name}_signed_Hessian_square_is_repair_Hessian"] = (
            repair_hessian(d0, sample)
            == cp.mscale(q(4), cp.madd(plus, minus))
        )

    t_samples = [Fraction(-1), Fraction(0), Fraction(1, 2), Fraction(1), Fraction(3, 2)]
    odd_powers = [1, 3, 5, 7]
    family_checks: dict[str, bool] = {}
    signed_values: dict[str, str] = {}
    weighted_values: dict[str, str] = {}
    odd_moments: dict[str, dict[str, str]] = {}
    for t in t_samples:
        label = fraction_text(t).replace("-", "minus_").replace("/", "_over_")
        d_t = cp.madd(d0, cp.mscale(q(t), d1))
        family_checks[f"family_{label}_is_KO6_odd"] = conjugate_by(grading, d_t) == cp.mscale(q(-1), d_t)
        signed_value = signed_action(d_t)
        weighted_value = weighted_action(d0, d_t)
        signed_values[fraction_text(t)] = fraction_text(signed_value)
        weighted_values[fraction_text(t)] = fraction_text(weighted_value)
        odd_moments[fraction_text(t)] = {}
        family_checks[f"family_{label}_signed_action_cancels"] = signed_value == 0
        family_checks[f"family_{label}_weighted_action_matches_polynomial"] = (
            weighted_value == 2 * t**2 - Fraction(8, 9) * t**3
        )
        for power in odd_powers:
            moment = odd_moment(d_t, power)
            odd_moments[fraction_text(t)][str(power)] = fraction_text(moment)
            family_checks[f"family_{label}_odd_moment_{power}_vanishes"] = moment == 0

    d1_plus = pi_plus(e_plus, d1)
    d1_minus = pi_minus(e_minus, d1)
    d1_zero = pi_zero(e_plus, e_minus, d1)
    d1_plus_norm = inner(d1_plus, d1_plus)
    d1_minus_norm = inner(d1_minus, d1_minus)
    signed_quadratic = inner(d1, jacobian(d0, d1))
    repair_quadratic = inner(d1, repair_hessian(d0, d1))

    zero_matrix = cp.zero(96, 96)
    orbit_generator = cp.mscale(q(Fraction(1, 2)), uts.sparse_matmul(zero_sample, d0))
    orbit_tangent = commutator(orbit_generator, d0)

    action_probe = cp.madd(d0, cp.mscale(q(Fraction(1, 3)), positive_sample))
    direction_probe = generic_sample
    permutation = cyclic_permutation(96)
    transformed_d0 = conjugate_by(permutation, d0)
    transformed_probe = conjugate_by(permutation, action_probe)
    transformed_direction = conjugate_by(permutation, direction_probe)

    signed_derivative = directional_derivative(signed_action, action_probe, direction_probe)
    signed_derivative_expected = inner(residual(action_probe), direction_probe)
    weighted = lambda value: weighted_action(d0, value)
    weighted_derivative = directional_derivative(weighted, action_probe, direction_probe)
    weighted_derivative_expected = inner(weighted_gradient(d0, action_probe), direction_probe)

    t_stationary = Fraction(3, 2)
    d_stationary = cp.madd(d0, cp.mscale(q(t_stationary), d1))
    weighted_stationary_derivative = inner(
        weighted_gradient(d0, d_stationary), d1
    )
    square_solutions: list[tuple[Fraction, Fraction]] = []
    for plus_sign in (Fraction(-1), Fraction(1)):
        for minus_sign in (Fraction(-1), Fraction(1)):
            candidate_a = (plus_sign - minus_sign) / 2
            candidate_b = (plus_sign + minus_sign) / 2
            if (
                (candidate_a + candidate_b) ** 2 == 1
                and (-candidate_a + candidate_b) ** 2 == 1
                and candidate_b**2 == 0
            ):
                square_solutions.append((candidate_a, candidate_b))

    theorem_hash = sha256(THEOREM)
    d0_hash = uts.matrix_digest(d0)
    d1_hash = uts.matrix_digest(d1)
    h_hash = uts.matrix_digest(h_phys)
    gamma_hash = uts.matrix_digest(grading)
    root_hash, root_payload = source_root(
        source_lock, theorem_hash, d0_hash, d1_hash, h_hash, gamma_hash
    )
    source_checks = source_hash_checks(source_lock)
    boundary = source_lock["boundary"]

    checks: dict[str, bool] = {
        **source_checks,
        **decomposition_checks,
        **square_checks,
        **family_checks,
        "source_lock_schema_is_exact": source_lock["schema"]
        == "boe.mtt.finite-dirac-cubic-variational-action-source-lock.v1",
        "handoff_is_pinned": source_lock["handoff_id"]
        == "2921d8c2-d14a-4f82-b8f0-25f0c5b28b96",
        "kernel_model_is_pinned": len(source_lock["kernel_model_sha256"]) == 64,
        "contract_schema_is_exact": schema["properties"]["schema"]["const"]
        == "boe.mtt.finite-dirac-cubic-variational-action.v1",
        "strict_top_level_contract": schema["additionalProperties"] is False,
        "T20_source_is_exact": t20["claim_id"] == "CBF.T20" and all(t20["checks"].values()),
        "T23_response_is_exact": t23["claim_id"] == "CBF.T23" and all(t23["checks"].values()),
        "T26_repair_action_is_exact": t26["claim_id"] == "CBF.T26" and all(t26["checks"].values()),
        "T27_spectral_classification_is_exact": t27["claim_id"] == "CBF.T27" and all(t27["checks"].values()),
        "T28_operator_repair_is_exact": t28["claim_id"] == "CBF.T28" and all(t28["checks"].values()),
        "D0_is_self_adjoint": d0 == cp.adjoint(d0),
        "D0_square_is_identity": square(d0) == identity96,
        "D0_trace_is_zero": normalized_trace(d0) == 0,
        "D0_plus_rank_is_48": rank_plus == 48,
        "D0_minus_rank_is_48": rank_minus == 48,
        "material_projectors_are_orthogonal": uts.sparse_matmul(e_plus, e_minus) == zero_matrix,
        "material_projectors_resolve_identity": cp.madd(e_plus, e_minus) == identity96,
        "signed_action_is_normalized_at_D0": signed_action(d0) == 0,
        "signed_gradient_vanishes_at_D0": residual(d0) == zero_matrix,
        "signed_action_directional_derivative_is_residual_pairing": signed_derivative == signed_derivative_expected,
        "signed_Hessian_is_self_adjoint_on_probe": inner(direction_probe, jacobian(d0, positive_sample))
        == inner(jacobian(d0, direction_probe), positive_sample),
        "positive_inertia_is_2304": positive_dimension == 2304,
        "negative_inertia_is_2304": negative_dimension == 2304,
        "zero_inertia_is_4608": zero_dimension == 4608,
        "full_operator_dimension_is_9216": positive_dimension + negative_dimension + zero_dimension == 9216,
        "positive_sample_has_eigenvalue_plus_two": jacobian(d0, positive_sample) == cp.mscale(q(2), positive_sample),
        "negative_sample_has_eigenvalue_minus_two": jacobian(d0, negative_sample) == cp.mscale(q(-2), negative_sample),
        "zero_sample_is_in_Hessian_kernel": jacobian(d0, zero_sample) == zero_matrix,
        "orbit_generator_is_skew_adjoint": cp.adjoint(orbit_generator) == cp.mscale(q(-1), orbit_generator),
        "orbit_commutator_equals_zero_mode": orbit_tangent == zero_sample,
        "zero_mode_is_nonzero": zero_sample != zero_matrix,
        "critical_locus_rejects_zero_operator": residual(zero_matrix) == cp.mscale(q(-1), identity96),
        "positive_repair_gradient_accepts_zero_operator": positive_repair_gradient(zero_matrix) == zero_matrix,
        "grading_is_self_adjoint": grading == cp.adjoint(grading),
        "grading_square_is_identity": square(grading) == identity96,
        "grading_anticommutes_with_D0": conjugate_by(grading, d0) == cp.mscale(q(-1), d0),
        "grading_anticommutes_with_D1": conjugate_by(grading, d1) == cp.mscale(q(-1), d1),
        "H_phys_matches_T23": h_hash == t23["hessian_compression"]["KO6_response_sha256"],
        "D1_plus_norm_is_one": d1_plus_norm == 1,
        "D1_minus_norm_is_one": d1_minus_norm == 1,
        "D1_has_no_zero_sector": d1_zero == zero_matrix,
        "signed_quadratic_pullback_cancels": signed_quadratic == 0,
        "repair_quadratic_pullback_is_eight": repair_quadratic == 8,
        "repair_quadratic_matches_T28": fraction_text(repair_quadratic)
        == t28["selected_family_pullback"]["scalar_Hessian"],
        "cyclic_permutation_is_unitary": uts.sparse_matmul(cp.adjoint(permutation), permutation) == identity96,
        "signed_action_is_conjugation_invariant": signed_action(transformed_probe) == signed_action(action_probe),
        "residual_is_conjugation_covariant": residual(transformed_probe) == conjugate_by(permutation, residual(action_probe)),
        "Hessian_is_conjugation_covariant": jacobian(transformed_d0, transformed_direction)
        == conjugate_by(permutation, jacobian(d0, direction_probe)),
        "weighted_action_is_normalized_at_D0": weighted_action(d0, d0) == 0,
        "weighted_directional_derivative_matches_gradient": weighted_derivative == weighted_derivative_expected,
        "weighted_Hessian_positive_sector_is_two": weighted_hessian(d0, positive_sample) == cp.mscale(q(2), positive_sample),
        "weighted_Hessian_negative_sector_is_two": weighted_hessian(d0, negative_sample) == cp.mscale(q(2), negative_sample),
        "weighted_Hessian_zero_sector_is_two_thirds": weighted_hessian(d0, zero_sample) == cp.mscale(q(Fraction(2, 3)), zero_sample),
        "weighted_Hessian_lifts_orbit_zero_mode": weighted_hessian(d0, zero_sample) != zero_matrix,
        "weighted_Hessian_square_differs_from_repair": weighted_hessian(d0, weighted_hessian(d0, zero_sample))
        != repair_hessian(d0, zero_sample),
        "weighted_pullback_has_extra_stationary_point": weighted_stationary_derivative == 0,
        "weighted_extra_stationary_point_is_not_closure": residual(d_stationary) != zero_matrix,
        "two_anchor_square_equations_force_b_zero": square_solutions
        and all(b == 0 for _, b in square_solutions),
        "two_anchor_exact_square_solutions_are_plus_minus_signed": set(square_solutions)
        == {(Fraction(1), Fraction(0)), (Fraction(-1), Fraction(0))},
        "exact_square_members_cancel_on_family": all(
            a * signed_action(cp.madd(d0, cp.mscale(q(Fraction(1, 2)), d1)))
            + b * weighted_action(d0, cp.madd(d0, cp.mscale(q(Fraction(1, 2)), d1)))
            == 0
            for a, b in [(1, 0), (-1, 0)]
        ),
        "noncancelling_weighted_member_changes_zero_sector_square": square_checks["zero_signed_Hessian_square_is_repair_Hessian"]
        and weighted_hessian(d0, weighted_hessian(d0, zero_sample)) != repair_hessian(d0, zero_sample),
        "direct_signed_action_is_newly_closed": not boundary["direct_signed_variational_action_before"]
        and boundary["direct_signed_variational_action_after"],
        "signed_Hessian_inertia_is_newly_closed": not boundary["signed_Hessian_inertia_before"]
        and boundary["signed_Hessian_inertia_after"],
        "signed_Hessian_square_bridge_is_newly_closed": not boundary["signed_Hessian_square_bridge_before"]
        and boundary["signed_Hessian_square_bridge_after"],
        "KO6_cancellation_is_newly_closed": not boundary["KO6_odd_trace_cancellation_before"]
        and boundary["KO6_odd_trace_cancellation_after"],
        "canonical_two_anchor_no_go_is_newly_closed": not boundary["canonical_two_anchor_no_go_before"]
        and boundary["canonical_two_anchor_no_go_after"],
        "full_B_ACTION_01_remains_open": not boundary["full_B_ACTION_01_closed"],
        "physical_Lorentzian_action_remains_open": not boundary["physical_Lorentzian_action_selected"],
        "physical_scalar_profile_remains_open": not boundary["physical_scalar_spectral_profile_selected"],
        "nonzero_physical_coordinate_remains_open": not boundary["nonzero_physical_source_coordinate_selected"],
        "held_out_observable_remains_open": not boundary["held_out_physical_observable_emitted"],
        "no_observed_values_used": not boundary["observed_values_used"],
        "no_fitted_coefficients_used": not boundary["fitted_coefficients_used"],
        "physical_packet_acceptance_unchanged": boundary["physical_packet_acceptance_before"]
        == boundary["physical_packet_acceptance_after"] == 0,
        "physical_row_acceptance_unchanged": boundary["physical_row_acceptance_before"]
        == boundary["physical_row_acceptance_after"] == 0,
        "source_root_is_nonempty": len(root_hash) == 64,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"CBF.T29 build checks failed: {failed}")

    packet = {
        "schema": "boe.mtt.finite-dirac-cubic-variational-action.v1",
        "claim_id": "CBF.T29",
        "date": "2026-08-29",
        "status": (
            "exact same-root signed finite variational action, signed Hessian and "
            "normal-square bridge; exact KO6 cancellation and canonical two-anchor "
            "no-go; physical Lorentzian/BV action remains open"
        ),
        "source_provenance": {
            "handoff_id": source_lock["handoff_id"],
            "kernel_model_sha256": source_lock["kernel_model_sha256"],
            "repository_heads": source_lock["repositories"],
            "source_count": len(source_lock["local_sources"]),
            "all_source_hashes_match": all(source_checks.values()),
            "source_root_sha256": root_hash,
            "source_root_payload": root_payload,
        },
        "configuration_space": {
            "carrier": "V_sa=End_sa(H_F)",
            "H_F_complex_dimension": 96,
            "V_sa_real_dimension": 9216,
            "metric": "g(X,Y)=Re tau96(X^*Y)",
            "normalized_trace": "tau96=Tr/96",
            "basepoint": "D0",
            "D0_spectrum": {"-1": 48, "1": 48},
            "D0_sha256": d0_hash,
            "D1_sha256": d1_hash,
            "Gamma96_sha256": gamma_hash,
        },
        "direct_variational_action": {
            "definition": "S_sig(D)=tau96(D^3/3-D)",
            "variation": "dS_sig(D)[X]=tau96((D^2-I96)X)",
            "gradient": "grad S_sig(D)=D^2-I96",
            "Helmholtz_exact": True,
            "normalized_at_D0": True,
            "unique_up_to_additive_constant": True,
            "bounded_below": False,
            "physical_action_claimed": False,
        },
        "critical_locus": {
            "exact_locus": "Crit(S_sig)={D=D^*:D^2=I96}",
            "equals_closure_locus": True,
            "zero_operator_signed_gradient": "-I96",
            "zero_operator_positive_repair_gradient": "0",
            "normal_square_has_extra_critical_points": True,
        },
        "signed_Hessian": {
            "definition": "H_sig=J0, J0(X)=D0X+XD0",
            "superprojector_form": "J0=2Pi_plus-2Pi_minus",
            "spectrum": {"-2": 2304, "0": 4608, "2": 2304},
            "inertia": {"negative": 2304, "positive": 2304, "zero": 4608},
            "self_adjoint": True,
            "materialized_9216_square_matrix": False,
        },
        "Morse_Bott_decomposition": {
            "orbit": "U(96)/(U(48) x U(48))",
            "tangent": "Ran(Pi_zero)=ker J0",
            "normal_positive": "Ran(Pi_plus)",
            "normal_negative": "Ran(Pi_minus)",
            "tangent_real_dimension": zero_dimension,
            "positive_normal_dimension": positive_dimension,
            "negative_normal_dimension": negative_dimension,
            "finite_Morse_Bott": True,
        },
        "normal_square_bridge": {
            "exact_identity": "H_sig^2=J0^2=4(Pi_plus+Pi_minus)=A_rep",
            "T28_spectrum": {"0": 4608, "4": 4608},
            "same_root": True,
            "signed_source_is_not_positive_repair": True,
        },
        "automorphism_transfer": {
            "group": "U(96)",
            "action_invariant": "S_sig(UDU^*)=S_sig(D)",
            "residual_covariant": "F(UDU^*)=UF(D)U^*",
            "Hessian_intertwiner": "J_(UDU^*) Ad_U=Ad_U J_D",
            "finite_operator_space_closed": True,
            "continuum_q79_transfer_closed": False,
        },
        "KO6_cancellation": {
            "grading_relation": "Gamma96 D_phys(t) Gamma96=-D_phys(t)",
            "all_odd_traces_vanish": True,
            "signed_action_pullback": "S_sig(D_phys(t))=0",
            "sampled_t_values": [fraction_text(value) for value in t_samples],
            "sampled_odd_moments": odd_moments,
            "D1_sector_norms": {"Pi_plus": fraction_text(d1_plus_norm), "Pi_minus": fraction_text(d1_minus_norm), "Pi_zero": "0"},
            "signed_quadratic_pullback": fraction_text(signed_quadratic),
            "repair_quadratic_pullback": fraction_text(repair_quadratic),
            "mechanism": "equal KO6 partner contributions cancel in J0 and add in J0^2",
        },
        "weighted_anchor_escape_test": {
            "definition": "S_0(D)=tau96(D0(D^3/3-D))+2/3",
            "gradient": "G_0(D)=(D^2D0+DD0D+D0D^2)/3-D0",
            "Hessian": "K_0=2(Pi_plus+Pi_minus)+(2/3)Pi_zero",
            "family_pullback": "S_0(D_phys(t))=2t^2-(8/9)t^3",
            "sampled_values": weighted_values,
            "constrained_stationary_points": ["0", "3/2"],
            "three_halves_is_full_closure": False,
            "preserves_full_U96": False,
            "squares_to_A_rep": False,
            "physical_value_selector": False,
        },
        "canonical_two_anchor_classification": {
            "class": "S_(a,b)=aS_sig+bS_0",
            "Hessian_eigenvalues": {"Pi_plus": "2(a+b)", "Pi_minus": "2(-a+b)", "Pi_zero": "2b/3"},
            "normal_square_equations": ["(a+b)^2=1", "(-a+b)^2=1", "b=0"],
            "exact_square_solutions": [{"a": -1, "b": 0}, {"a": 1, "b": 0}],
            "family_pullback": "b(2t^2-(8/9)t^3)",
            "all_exact_square_solutions_cancel": True,
            "all_noncancelling_members_change_residual_or_zero_modes": True,
            "scope": "canonical anchors emitted by I96 and D0 only",
        },
        "action_tier_reconciliation": {
            "H4_T9": "direct variational branch instantiated for F(D)=D^2-I96",
            "H4_T10": "finite trace-cubic transgression only; no q79 Maurer-Cartan identification",
            "H4_T15": "field-only finite action exists; physical BV compactification gate remains open",
            "CBF_T25": "fermion/Yukawa spinor action remains distinct and unaffected",
            "CBF_T28": "positive repair semigroup is the exact normal-square shadow",
            "physical_pairing_or_polarization_required": True,
        },
        "parameter_ledger": {
            "new_observed_construction_inputs": 0,
            "new_fitted_coefficients": 0,
            "new_sector_specific_parameters": 0,
            "new_dimensionful_primitives": 0,
            "canonical_cubic_coefficients": ["1/3", "-1"],
            "canonical_coefficients_are_fixed_by_gradient": True,
        },
        "physical_boundary": {
            "finite_signed_variational_action_closed": True,
            "signed_Hessian_and_inertia_closed": True,
            "signed_to_positive_normal_square_closed": True,
            "KO6_scalar_odd_trace_cancellation_closed": True,
            "canonical_two_anchor_no_go_closed": True,
            "physical_Lorentzian_or_BV_action_selected": False,
            "physical_pairing_density_and_real_slice_selected": False,
            "nonzero_physical_source_coordinate_selected": False,
            "held_out_physical_observable_emitted": False,
            "continuum_q79_action_transfer_closed": False,
            "B_ACTION_01_closed": False,
        },
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "frontier_delta": (
            "The finite closure residual now has its unique normalized direct cubic "
            "variational primitive. Its signed Hessian has inertia (2304,2304,4608) "
            "and squares exactly to the T28 positive repair Hessian. KO6 grading then "
            "proves that every odd trace, the action pullback and its signed quadratic "
            "physical-family response cancel exactly, while repair remains 8. The "
            "canonical D0-weighted escape is nonzero but changes the residual and orbit "
            "zero modes. The remaining action blocker is therefore a selected physical "
            "pairing/polarization and compactification map, not another scalar trace fit."
        ),
        "checks": checks,
        "check_summary": {"passed": len(checks), "total": len(checks), "failed": []},
    }
    if set(packet) != set(schema["properties"]):
        raise AssertionError("packet top-level keys do not match contract schema")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        "finite Dirac cubic variational-action packet built: "
        f"{len(checks)}/{len(checks)} checks; signed source and square bridge closed; "
        "physical Lorentzian/BV action remains open"
    )


if __name__ == "__main__":
    main()
