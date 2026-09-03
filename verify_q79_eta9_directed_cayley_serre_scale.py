#!/usr/bin/env python3
"""Replay CBF.T65 and verify the frozen-binary non-promotion decision."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

import build_q79_eta9_directed_cayley_serre_scale as build


ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(left: float, right: float, tolerance: float = 2.0e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def complex_pair(value: list[float]) -> complex:
    require(len(value) == 2, "complex pair")
    return complex(float(value[0]), float(value[1]))


def load_array(binding: dict[str, Any]) -> np.ndarray:
    path = ROOT / binding["path"]
    require(build.artifact(path) == binding, f"array binding: {path}")
    value = np.load(path, allow_pickle=False)
    require(value.shape == (9361,), f"array shape: {path}")
    return value


def replay_row(
    packet_row: dict[str, Any],
    h4_t141: dict[str, Any],
) -> tuple[float, float, complex, complex]:
    segment = packet_row["segment"]
    serre, sections, derivatives, section_normalization = build.framed_input(segment)
    require(
        close(section_normalization, packet_row["section_normalization"]),
        f"section normalization: {segment}",
    )
    basis = serre.component_monomials(9, 3)
    index = {term: column for column, term in enumerate(basis)}
    relation = build.relation_matrix(sections, serre.component_monomials)
    relation_prime = build.relation_matrix(derivatives, serre.component_monomials)
    functional = load_array(packet_row["arrays"]["critical_functional"])
    functional_prime = load_array(
        packet_row["arrays"]["critical_functional_derivative"]
    )

    value_residual = relation @ functional
    derivative_residual = relation @ functional_prime + relation_prime @ functional
    value_relative = float(
        np.linalg.norm(value_residual, np.inf)
        / max(
            sparse.linalg.norm(relation, ord=np.inf)
            * np.linalg.norm(functional, np.inf),
            1.0e-300,
        )
    )
    derivative_relative = float(
        np.linalg.norm(derivative_residual, np.inf)
        / max(
            sparse.linalg.norm(relation, ord=np.inf)
            * np.linalg.norm(functional_prime, np.inf)
            + sparse.linalg.norm(relation_prime, ord=np.inf)
            * np.linalg.norm(functional, np.inf),
            1.0e-300,
        )
    )
    diagnostics = packet_row["diagnostics"]
    require(
        close(value_relative, diagnostics["all_row_value_relative_residual"]),
        f"stored value residual: {segment}",
    )
    require(
        close(
            derivative_relative,
            diagnostics["all_row_derivative_relative_residual"],
        ),
        f"stored derivative residual: {segment}",
    )
    require(value_relative < 1.0e-8, f"all-row value replay: {segment}")
    require(
        derivative_relative < 1.0e-8,
        f"all-row derivative replay: {segment}",
    )

    embedding, _pivots, _free = build.top_embedding(serre, basis)
    h4_row = next(
        row
        for row in h4_t141["six_midpoint_audit"]["rows"]
        if row["segment"] == segment
    )
    h4_top = build.load_bound_array(h4_row["arrays"]["value_center"], (2584,))
    h4_top_prime = build.load_bound_array(
        h4_row["arrays"]["derivative_center"], (2584,)
    )
    require(
        np.linalg.norm(embedding @ functional - h4_top, np.inf)
        / np.linalg.norm(h4_top, np.inf)
        < 1.0e-12,
        f"H4 top value anchor: {segment}",
    )
    require(
        np.linalg.norm(embedding @ functional_prime - h4_top_prime, np.inf)
        / np.linalg.norm(h4_top_prime, np.inf)
        < 1.0e-10,
        f"H4 top derivative anchor: {segment}",
    )

    jacobian, jacobian_prime, cancellation = build.toric_jacobian_jet(
        sections, derivatives
    )
    require(
        all(
            close(cancellation[key], packet_row["cancellation_audit"][key])
            for key in cancellation
        ),
        f"Jacobian cancellation audit: {segment}",
    )
    denominator = build.evaluate_polynomial(functional, index, jacobian)
    denominator_prime = build.evaluate_polynomial(
        functional_prime, index, jacobian
    ) + build.evaluate_polynomial(functional, index, jacobian_prime)
    top_basis = serre.component_monomials(18, 1)
    normalization_polynomial = build.poly_shift(
        build.transport_top_monomial(top_basis[1494]),
        (1, 1, 1, 1, 1, 1),
    )
    numerator = build.evaluate_polynomial(
        functional, index, normalization_polynomial
    )
    numerator_prime = build.evaluate_polynomial(
        functional_prime, index, normalization_polynomial
    )
    scale = 292.5 * numerator / denominator
    scale_prime = 292.5 * (
        numerator_prime * denominator - numerator * denominator_prime
    ) / (denominator * denominator)
    require(
        abs(scale - complex_pair(packet_row["canonical_Serre_scale"]))
        <= 2.0e-11 * max(1.0, abs(scale)),
        f"canonical scale replay: {segment}",
    )
    require(
        abs(
            scale_prime
            - complex_pair(packet_row["canonical_Serre_scale_derivative"])
        )
        <= 2.0e-11 * max(1.0, abs(scale_prime)),
        f"canonical scale derivative replay: {segment}",
    )
    return value_relative, derivative_relative, scale, scale_prime


def main() -> int:
    packet = build.load_canonical(build.PACKET)
    require(packet["theorem_id"] == "CBF.T65", "theorem identity")
    require(
        packet["status"]
        == "FROZEN_BINARY_CAYLEY_SERRE_SCALE_PROMOTION_REJECTED_BY_ROW_GAUGE_TEST",
        "theorem status",
    )
    require(all(packet["checks"].values()), "packet checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    require(packet["parameter_ledger"]["observed_values_used"] == 0, "observations")
    require(
        packet["parameter_ledger"]["new_continuous_fit_parameters"] == 0,
        "continuous parameters",
    )
    require(
        packet["source_bindings"]["T65_exact_good_reduction_minor"]
        == build.artifact(build.MINOR),
        "exact minor binding",
    )
    require(
        packet["source_bindings"]["T65_complex_minor_packet"]
        == build.artifact(build.COMPLEX_MINOR_PACKET),
        "complex minor packet binding",
    )
    require(
        packet["source_bindings"]["T65_complex_minor_rows"]
        == build.artifact(build.COMPLEX_MINOR_ROWS),
        "complex minor rows binding",
    )
    _selected, _minor_packet = build.load_complex_minor_rows()
    h4_t141 = build.load_canonical(build.H4_T141)
    require(
        packet["source_bindings"]["H4_T141_contract"]
        == build.external_artifact(build.H4_T141),
        "H4-T141 binding",
    )
    replays = [replay_row(row, h4_t141) for row in packet["rows"]]
    require(
        [row["segment"] for row in packet["rows"]] == ["edge-2", "edge-0"],
        "segment order",
    )
    gauge_audit = build.binary_gauge_audit(replays[0][2])
    require(
        build.canonical_sha256(gauge_audit)
        == build.canonical_sha256(packet["binary_row_gauge_audit"]),
        "binary row-gauge audit replay",
    )
    require(
        not gauge_audit["decision"]["binary_coefficient_scale_is_promoted"]
        and gauge_audit["minimum_pairwise_Serre_scale_relative_gap"] > 0.01,
        "binary scale non-promotion",
    )
    print(
        "CBF.T65 verification: PASS "
        f"max_value_residual={max(row[0] for row in replays):.3e} "
        f"max_derivative_residual={max(row[1] for row in replays):.3e} "
        f"min_gauge_gap={gauge_audit['minimum_pairwise_Serre_scale_relative_gap']:.3e} "
        "binary_promotion=REJECTED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
