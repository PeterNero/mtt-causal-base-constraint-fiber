#!/usr/bin/env python3
"""Independently verify the CBF.T67 correlated scalar and first jet."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from flint import acb, arb, ctx
import numpy as np

import run_q79_eta9_cayley_critical_characteristic_zero_neumann as t66


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_eta9_cayley_critical_correlated_readout.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_packet(path: Path, schema: str) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="ascii"))
    require(payload.get("schema") == schema, f"schema: {path}")
    claimed = payload.get("canonical_payload_sha256")
    unsigned = dict(payload)
    unsigned.pop("canonical_payload_sha256", None)
    require(claimed == t66.canonical_sha256(unsigned), f"canonical hash: {path}")
    return payload


def load_array(binding: dict[str, Any], shape: tuple[int, ...]) -> np.ndarray:
    return t66.load_array(binding, shape)


def component(value: np.ndarray) -> np.ndarray:
    return np.nextafter(np.abs(value.real) + np.abs(value.imag), math.inf)


def positive_pair_sum(left: np.ndarray, right: np.ndarray) -> float:
    require(left.shape == right.shape, "positive pair shape")
    require(np.all(left >= 0.0) and np.all(right >= 0.0), "positive pair")
    total = sum(
        (arb(float(a)) * arb(float(b)) for a, b in zip(left, right, strict=True)),
        arb(0),
    )
    return float(total.upper())


def exact_dot(left: np.ndarray, right: np.ndarray) -> acb:
    require(left.shape == right.shape, "dot shape")
    return sum(
        (acb(complex(a)) * acb(complex(b)) for a, b in zip(left, right, strict=True)),
        acb(0),
    )


def midpoint(value: acb) -> complex:
    return complex(float(value.real.mid()), float(value.imag.mid()))


def close(left: float, right: float, tolerance: float = 2.0e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def main() -> int:
    ctx.prec = 512
    packet = load_packet(
        PACKET, "mtt.cbf.q79-eta9-cayley-critical-correlated-readout.v1"
    )
    require(packet["theorem_id"] == "CBF.T67", "theorem identity")
    require(
        packet["status"]
        == "CERTIFIED_SAME_SOURCE_CHARACTERISTIC_ZERO_SCALAR_READOUT",
        "theorem status",
    )
    require(packet["all_checks_pass"] and all(packet["checks"].values()), "checks")
    require(
        not packet["guardrails"]["physical_endpoint_selected_here"],
        "physical endpoint guardrail",
    )
    require(packet["parameter_ledger"]["observed_values_used"] == 0, "observations")
    require(
        packet["parameter_ledger"]["new_continuous_fit_parameters"] == 0,
        "continuous parameters",
    )
    require(
        packet["parameter_ledger"]["new_discrete_fit_parameters"] == 0,
        "discrete parameters",
    )

    input_schemas = {
        "base": "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-input.v1",
        "signed": "mtt.cbf.q79-eta9-cayley-critical-signed-correction.v1",
        "top_signed": "mtt.cbf.q79-eta9-cayley-top-signed-source.v1",
        "T66": "mtt.cbf.q79-eta9-cayley-critical-characteristic-zero-neumann.v1",
    }
    inputs: dict[str, dict[str, Any]] = {}
    for name, schema in input_schemas.items():
        binding = packet["inputs"][name]
        path = ROOT / binding["path"]
        require(t66.artifact(path) == binding, f"input binding: {name}")
        inputs[name] = load_packet(path, schema)
    require(inputs["signed"]["all_checks_pass"], "signed source")
    require(inputs["top_signed"]["all_checks_pass"], "top signed source")
    replay_binding = inputs["top_signed"]["source_bindings"]["upstream_replay"]
    replay_path = ROOT / replay_binding["path"]
    require(t66.artifact(replay_path) == replay_binding, "portable upstream replay")
    replay = load_packet(
        replay_path,
        "mtt.preprojection.q79-eta9-framed-member-directed-top-trace-probe.v1",
    )
    for binding in (
        replay["Neumann_row_bounds"],
        replay["top_trace_value"]["center"],
        replay["top_trace_value"]["radius"],
        replay["top_trace_derivative"]["center"],
        replay["top_trace_derivative"]["radius"],
    ):
        require(t66.artifact(ROOT / binding["path"]) == binding, "replay array")
    require(
        inputs["T66"]["checks"][
            "the_exact_characteristic_zero_matrix_has_a_strict_Neumann_inverse"
        ],
        "inherited inverse",
    )
    require(
        inputs["T66"]["checks"]["all_16740_value_relation_rows_enclose_zero"]
        and inputs["T66"]["checks"][
            "all_16740_derivative_relation_rows_enclose_zero"
        ],
        "inherited all-row execution",
    )

    arrays = packet["arrays"]
    x = load_array(arrays["balanced_value_center"], (6777,))
    x_radius = load_array(arrays["balanced_value_radius"], (6777,))
    v = load_array(arrays["balanced_derivative_center"], (6777,))
    v_radius = load_array(arrays["balanced_derivative_radius"], (6777,))
    K = load_array(arrays["common_top_readout_center"], (2584,))
    K_radius = load_array(arrays["common_top_readout_radius"], (2584,))
    Kprime = load_array(
        arrays["common_top_readout_derivative_center"], (2584,)
    )
    Kprime_radius = load_array(
        arrays["common_top_readout_derivative_radius"], (2584,)
    )
    rz = load_array(arrays["value_adjoint_residual_bound"], (6777,))
    ry = load_array(arrays["derivative_adjoint_residual_bound"], (6777,))
    require(
        all(
            np.all(value >= 0.0)
            for value in (x_radius, v_radius, K_radius, Kprime_radius, rz, ry)
        ),
        "nonnegative output bounds",
    )

    top_arrays = inputs["top_signed"]["arrays"]
    top = load_array(top_arrays["value_center"], (2584,)) + load_array(
        top_arrays["value_correction"], (2584,)
    )
    top_radius = load_array(top_arrays["value_tail"], (2584,))
    topprime = load_array(
        top_arrays["derivative_center"], (2584,)
    ) + load_array(top_arrays["derivative_correction"], (2584,))
    topprime_radius = load_array(top_arrays["derivative_tail"], (2584,))

    x_bound = np.nextafter(component(x) + x_radius, math.inf)
    v_bound = np.nextafter(component(v) + v_radius, math.inf)
    K_bound = np.nextafter(component(K) + K_radius, math.inf)
    Kprime_bound = np.nextafter(component(Kprime) + Kprime_radius, math.inf)
    denominator_center = exact_dot(K, top)
    denominator_error = sum(
        (
            positive_pair_sum(K_radius, component(top)),
            positive_pair_sum(K_bound, top_radius),
            positive_pair_sum(rz, x_bound),
        )
    )
    denominator_midpoint = midpoint(denominator_center)
    denominator_lower = abs(denominator_midpoint) - denominator_error
    require(denominator_lower > 0.0, "independent denominator exclusion")

    denominator_prime_center = exact_dot(K, topprime) + exact_dot(Kprime, top)
    denominator_prime_error = sum(
        (
            positive_pair_sum(K_radius, component(topprime)),
            positive_pair_sum(K_bound, topprime_radius),
            positive_pair_sum(Kprime_radius, component(top)),
            positive_pair_sum(Kprime_bound, top_radius),
            positive_pair_sum(rz, v_bound),
            positive_pair_sum(ry, x_bound),
        )
    )
    denominator_prime_midpoint = midpoint(denominator_prime_center)
    denominator_prime_lower = abs(denominator_prime_midpoint) - denominator_prime_error
    require(denominator_prime_lower > 0.0, "independent derivative exclusion")

    stored_denominator = packet["denominator"]
    stored_derivative = packet["denominator_derivative"]
    require(stored_denominator["excludes_zero"], "stored denominator exclusion")
    require(stored_derivative["excludes_zero"], "stored derivative exclusion")
    stored_D = complex(
        stored_denominator["midpoint_real"],
        stored_denominator["midpoint_imaginary"],
    )
    stored_Dprime = complex(
        stored_derivative["midpoint_real"],
        stored_derivative["midpoint_imaginary"],
    )
    require(
        abs(denominator_midpoint - stored_D)
        <= denominator_error + stored_denominator["total_absolute_error"],
        "denominator disk replay",
    )
    require(
        abs(denominator_prime_midpoint - stored_Dprime)
        <= denominator_prime_error + stored_derivative["total_absolute_error"],
        "derivative disk replay",
    )

    scale = packet["canonical_Serre_scale"]["value_disk"]
    scale_prime = packet["canonical_Serre_scale"]["derivative_disk"]
    require(scale is not None and scale_prime is not None, "scale disks")
    scale_replay = 585.0 / (2.0 * stored_D)
    scale_prime_replay = -585.0 * stored_Dprime / (2.0 * stored_D**2)
    require(
        close(scale_replay.real, scale["midpoint_real"])
        and close(scale_replay.imag, scale["midpoint_imaginary"]),
        "scale formula",
    )
    require(
        close(scale_prime_replay.real, scale_prime["midpoint_real"])
        and close(scale_prime_replay.imag, scale_prime["midpoint_imaginary"]),
        "scale derivative formula",
    )
    require(scale["relative_error_upper"] < 1.0e-6, "resolved scale disk")
    print(
        "CBF.T67 verification: PASS "
        f"independent_D_lower={denominator_lower:.6e} "
        f"independent_Dprime_lower={denominator_prime_lower:.6e} "
        f"scale_relative_error={scale['relative_error_upper']:.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
