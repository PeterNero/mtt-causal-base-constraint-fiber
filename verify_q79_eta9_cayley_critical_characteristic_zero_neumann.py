#!/usr/bin/env python3
"""Independently verify the durable CBF.T66 output packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flint import acb, ctx
import numpy as np

import run_q79_eta9_cayley_critical_characteristic_zero_neumann as run


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_eta9_cayley_critical_characteristic_zero_neumann.packet.json"
INPUT = (
    ROOT
    / "certificates"
    / "q79_eta9_cayley_critical_characteristic_zero_seed7909"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(left: float, right: float, tolerance: float = 2.0e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def load_packet(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="ascii"))
    claimed = payload.pop("canonical_payload_sha256")
    require(run.canonical_sha256(payload) == claimed, "packet canonical hash")
    payload["canonical_payload_sha256"] = claimed
    return payload


def load_output_array(binding: dict[str, Any], shape: tuple[int, ...]) -> np.ndarray:
    path = ROOT / binding["path"]
    require(run.artifact(path) == binding, f"output binding: {path}")
    value = np.load(path, allow_pickle=False)
    require(value.shape == shape and np.isfinite(value).all(), f"output: {path}")
    return value


def compare_audit(
    calculated: dict[str, Any],
    stored: dict[str, Any],
    label: str,
) -> None:
    require(calculated.keys() == stored.keys(), f"{label} keys")
    for key, value in calculated.items():
        expected = stored[key]
        if isinstance(value, bool):
            require(value is expected, f"{label}: {key}")
        elif isinstance(value, int):
            require(value == expected, f"{label}: {key}")
        else:
            require(close(float(value), float(expected)), f"{label}: {key}")


def main() -> int:
    packet = load_packet(PACKET)
    require(packet["theorem_id"] == "CBF.T66", "theorem id")
    require(
        packet["schema"]
        == "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-neumann.v1",
        "packet schema",
    )
    require(packet["input"] == run.artifact(INPUT / "metadata.json"), "input binding")
    metadata = run.load_metadata(INPUT)
    ctx.prec = int(packet["precision_bits"])
    eta_rows = load_output_array(packet["Neumann_row_bounds"], (6777,))
    eta = float(eta_rows.max())
    diagnostics = packet["inverse_certificate"]
    require(
        close(eta, diagnostics["maximum_total_Neumann_row"]),
        "maximum Neumann row",
    )
    require(
        int(np.argmax(eta_rows)) == diagnostics["maximum_total_row_zero_based"],
        "maximum Neumann row index",
    )
    targeted = packet["targeted_high_precision_refinement"]
    targeted_count = int(diagnostics["targeted_Arb_row_count"])
    coarse_rows = load_output_array(
        targeted["coarse_Neumann_row_bounds"], (6777,)
    )
    targeted_indices = load_output_array(
        targeted["row_indices"], (targeted_count,)
    ).astype(np.int64)
    targeted_inverse = load_output_array(
        targeted["inverse_rows"], (targeted_count, 6777)
    )
    stored_targeted_residual = load_output_array(
        targeted["midpoint_residual_bounds"], (targeted_count,)
    )
    stored_targeted_coefficient = load_output_array(
        targeted["coefficient_correction_bounds"], (targeted_count,)
    )
    stored_targeted_total = load_output_array(
        targeted["total_bounds"], (targeted_count,)
    )
    require(
        np.array_equal(targeted_indices, np.flatnonzero(coarse_rows >= 1.0)),
        "targeted row selection",
    )
    source_matrices = metadata["matrices"]
    selected_matrix = run.load_sparse(
        source_matrices["balanced_matrix_center"], (6777, 6777)
    ).tocsc()
    selected_error = run.load_sparse(
        source_matrices["balanced_matrix_error"], (6777, 6777)
    )
    coefficient_error_row_sums = run.row_positive_sums_upper(selected_error)
    (
        calculated_targeted_residual,
        calculated_targeted_coefficient,
        calculated_targeted_total,
    ) = run.exact_targeted_neumann_rows(
        targeted_inverse,
        targeted_indices,
        selected_matrix,
        coefficient_error_row_sums,
        report=False,
    )
    require(
        np.allclose(
            calculated_targeted_residual,
            stored_targeted_residual,
            rtol=2.0e-14,
            atol=0.0,
        ),
        "targeted midpoint residual bounds",
    )
    require(
        np.allclose(
            calculated_targeted_coefficient,
            stored_targeted_coefficient,
            rtol=2.0e-14,
            atol=0.0,
        ),
        "targeted coefficient correction bounds",
    )
    require(
        np.allclose(
            calculated_targeted_total,
            stored_targeted_total,
            rtol=2.0e-14,
            atol=0.0,
        ),
        "targeted total bounds",
    )
    reconstructed_rows = coarse_rows.copy()
    reconstructed_rows[targeted_indices] = calculated_targeted_total
    require(
        np.allclose(reconstructed_rows, eta_rows, rtol=2.0e-14, atol=0.0),
        "hybrid Neumann rows",
    )

    if packet["status"] == "SEED7909_CHARACTERISTIC_ZERO_NEUMANN_INVERSE_REJECTED":
        require(eta >= 1.0, "honest Neumann rejection")
        require(all(packet["checks"].values()), "obstruction checks")
        require(not any(packet["guardrails"].values()), "obstruction guardrails")
        print(f"CBF.T66 verification: PASS certified_preconditioner_rejection eta={eta:.6g}")
        return 0

    require(eta < 1.0, "strict Neumann inverse")
    arrays = packet["arrays"]
    functional_center = load_output_array(
        arrays["critical_functional_center"], (9361,)
    )
    functional_radius = load_output_array(
        arrays["critical_functional_radius"], (9361,)
    )
    functional_prime_center = load_output_array(
        arrays["critical_functional_derivative_center"], (9361,)
    )
    functional_prime_radius = load_output_array(
        arrays["critical_functional_derivative_radius"], (9361,)
    )
    require(
        np.all(functional_radius >= 0.0)
        and np.all(functional_prime_radius >= 0.0),
        "nonnegative functional radii",
    )

    source_arrays = metadata["arrays"]
    full = run.load_sparse(source_matrices["full_relation_center"], (16740, 9361))
    full_error = run.load_sparse(
        source_matrices["full_relation_error"], (16740, 9361)
    )
    full_prime = run.load_sparse(
        source_matrices["full_relation_derivative_center"], (16740, 9361)
    )
    full_prime_error = run.load_sparse(
        source_matrices["full_relation_derivative_error"], (16740, 9361)
    )
    value_audit = run.all_row_value_audit(
        full, full_error, functional_center, functional_radius
    )
    derivative_audit = run.all_row_derivative_audit(
        full,
        full_error,
        full_prime,
        full_prime_error,
        functional_center,
        functional_radius,
        functional_prime_center,
        functional_prime_radius,
    )
    compare_audit(value_audit, packet["all_row_audit"]["value"], "value audit")
    compare_audit(
        derivative_audit,
        packet["all_row_audit"]["derivative"],
        "derivative audit",
    )

    del source_arrays
    exact_jacobian, exact_jacobian_prime = run.load_exact_ball_polynomials(
        metadata["exact_polynomials"]["toric_Jacobian"], 9361
    )
    functional_balls = run.ball_vector(functional_center, functional_radius)
    functional_prime_balls = run.ball_vector(
        functional_prime_center, functional_prime_radius
    )
    denominator = run.exact_sparse_functional(exact_jacobian, functional_balls)
    first = run.exact_sparse_functional(exact_jacobian, functional_prime_balls)
    second = run.exact_sparse_functional(exact_jacobian_prime, functional_balls)
    denominator_prime = first + second
    denominator_diagnostics = run.ball_diagnostics(denominator)
    first_diagnostics = run.ball_diagnostics(first)
    second_diagnostics = run.ball_diagnostics(second)
    stored_jacobian = packet["toric_Jacobian"]
    require(
        stored_jacobian["exact_ball_source"]
        == metadata["exact_polynomials"]["toric_Jacobian"],
        "exact Jacobian source",
    )
    require(
        stored_jacobian["value_term_count"] == len(exact_jacobian)
        and stored_jacobian["derivative_term_count"]
        == len(exact_jacobian_prime),
        "exact Jacobian term counts",
    )
    require(str(denominator) == stored_jacobian["denominator_ball"], "denominator ball")
    require(str(denominator_prime) == stored_jacobian["derivative_ball"], "derivative ball")
    require(
        denominator_diagnostics == stored_jacobian["denominator_diagnostics"],
        "denominator diagnostics",
    )
    require(
        first_diagnostics
        == stored_jacobian["derivative_terms"]["J_times_functional_derivative"],
        "first derivative term",
    )
    require(
        second_diagnostics
        == stored_jacobian["derivative_terms"]["J_derivative_times_functional"],
        "second derivative term",
    )
    excludes_zero = not denominator.contains(0)
    require(excludes_zero is stored_jacobian["excludes_zero"], "zero exclusion")
    if excludes_zero:
        scale = acb(585) / (2 * denominator)
        scale_prime = -acb(585) * denominator_prime / (2 * denominator**2)
        require(
            str(scale) == packet["canonical_Serre_scale"]["value_ball"],
            "scale ball",
        )
        require(
            str(scale_prime)
            == packet["canonical_Serre_scale"]["derivative_ball"],
            "scale derivative ball",
        )

    expected_checks = {
        "the_exact_characteristic_zero_matrix_has_a_strict_Neumann_inverse": eta
        < 1.0,
        "all_16740_value_relation_rows_enclose_zero": value_audit[
            "all_rows_enclose_zero"
        ],
        "all_16740_derivative_relation_rows_enclose_zero": derivative_audit[
            "all_rows_enclose_zero"
        ],
        "the_toric_Jacobian_denominator_ball_excludes_zero": excludes_zero,
        "the_scale_and_derivative_balls_are_emitted": excludes_zero,
    }
    for key, value in expected_checks.items():
        require(packet["checks"][key] is value, f"check decision: {key}")
    require(not any(packet["guardrails"].values()), "guardrails")
    promoted = all(packet["checks"].values())
    require(packet["all_checks_pass"] is promoted, "aggregate decision")
    require(
        packet["status"]
        == (
            "CLOSED_CHARACTERISTIC_ZERO_POINTWISE_CAYLEY_SERRE_SCALE_AND_DERIVATIVE"
            if promoted
            else "CHARACTERISTIC_ZERO_INVERSE_CERTIFIED_DOWNSTREAM_INTERVAL_EXIT_OPEN"
        ),
        "status decision",
    )
    print(
        "CBF.T66 verification: PASS "
        f"eta={eta:.6g} value_rows={value_audit['rows_enclosing_zero']}/16740 "
        f"derivative_rows={derivative_audit['rows_enclosing_zero']}/16740 "
        f"denominator_excludes_zero={excludes_zero} promoted={promoted}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
