#!/usr/bin/env python3
"""Mixed-precision T65 scout with frozen binary coefficients.

This is deliberately a two-stage tool.  ``--prepare`` builds a small,
portable capsule from the full research checkout.  Normal execution needs
only NumPy, SciPy and python-flint and refines one selected critical solve
against exact-dyadic Arb copies of the frozen binary matrix and right side.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flint import acb, ctx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "certificates/q79_eta9_cayley_critical_refinement_seed7909"
DEFAULT_ROWS = ROOT / "q79_eta9_cayley_critical_rank_revealing_rows.npy"
DEFAULT_OUTPUT = (
    ROOT / "q79_eta9_cayley_critical_binary_mixed_refinement_seed7909.packet.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def artifact(path: Path) -> dict[str, object]:
    require(path.is_file(), f"artifact exists: {path}")
    return {
        "path": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def write_array(path: Path, value: np.ndarray) -> None:
    np.save(path, value, allow_pickle=False)


def prepare(input_directory: Path, rows_path: Path, seed: int) -> None:
    import build_q79_eta9_directed_cayley_serre_scale as t65

    serre, sections, derivatives, _normalization = t65.framed_input("edge-2")
    basis = serre.component_monomials(9, 3)
    index = {term: column for column, term in enumerate(basis)}
    relation = t65.relation_matrix(sections, serre.component_monomials)
    embedding, pivots, free = t65.top_embedding(serre, basis)
    h4 = t65.load_canonical(t65.H4_T141)
    h4_row = next(
        row for row in h4["six_midpoint_audit"]["rows"] if row["segment"] == "edge-2"
    )
    top_value = t65.load_bound_array(h4_row["arrays"]["value_center"], (2584,))
    pivot_value = splu(embedding[:, pivots].tocsc()).solve(top_value)
    selected_rows = np.load(rows_path, allow_pickle=False).astype(np.int64)
    require(
        selected_rows.shape == (6777,)
        and np.unique(selected_rows).size == 6777,
        "selected row shape",
    )

    reduced = relation[:, free].tocsr()
    selected = reduced[selected_rows, :].tocsr()
    row_norm = np.asarray(abs(selected).max(axis=1).toarray()).ravel()
    row_factor = 1.0 / row_norm
    row_balanced = sparse.diags(row_factor) @ selected
    column_norm = np.asarray(abs(row_balanced).max(axis=0).toarray()).ravel()
    column_factor = 1.0 / column_norm
    balanced = (row_balanced @ sparse.diags(column_factor)).tocsr()
    value_rhs = -(relation[:, pivots] @ pivot_value)
    balanced_rhs = row_factor * value_rhs[selected_rows]

    jacobian, _jacobian_prime, _cancellation = t65.toric_jacobian_jet(
        sections, derivatives
    )
    jacobian_vector = np.zeros(9361, dtype=np.complex128)
    for term, coefficient in jacobian.items():
        jacobian_vector[index[term]] += coefficient
    denominator_constant = np.asarray(
        [np.dot(jacobian_vector[pivots], pivot_value)], dtype=np.complex128
    )
    denominator_coefficients = jacobian_vector[free] * column_factor

    input_directory.mkdir(parents=True, exist_ok=True)
    matrix_path = input_directory / "balanced_matrix.npz"
    rhs_path = input_directory / "balanced_rhs.npy"
    denominator_path = input_directory / "denominator_coefficients.npy"
    constant_path = input_directory / "denominator_constant.npy"
    selected_rows_path = input_directory / "selected_original_rows.npy"
    sparse.save_npz(matrix_path, balanced, compressed=True)
    write_array(rhs_path, balanced_rhs)
    write_array(denominator_path, denominator_coefficients)
    write_array(constant_path, denominator_constant)
    write_array(selected_rows_path, selected_rows)
    metadata: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-binary-refinement-input.v1",
        "seed": seed,
        "segment": "edge-2",
        "parameter": 0.5,
        "lift_sign": -1,
        "matrix": artifact(matrix_path),
        "rhs": artifact(rhs_path),
        "denominator_coefficients": artifact(denominator_path),
        "denominator_constant": artifact(constant_path),
        "selected_rows": artifact(selected_rows_path),
        "matrix_shape": list(balanced.shape),
        "matrix_nonzeros": int(balanced.nnz),
        "unknowns_after_top_anchor": int(free.size),
        "top_anchor_coordinates": int(pivots.size),
    }
    metadata["canonical_payload_sha256"] = canonical_sha256(metadata)
    (input_directory / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T65 mixed-refinement input: PASS "
        f"seed={seed} shape={balanced.shape} nnz={balanced.nnz}"
    )


def load_metadata(input_directory: Path) -> dict[str, Any]:
    path = input_directory / "metadata.json"
    payload = json.loads(path.read_text(encoding="ascii"))
    claimed = payload.pop("canonical_payload_sha256")
    require(canonical_sha256(payload) == claimed, "metadata canonical hash")
    payload["canonical_payload_sha256"] = claimed
    return payload


def acb_from_complex(value: complex) -> acb:
    return acb(float(value.real), float(value.imag))


def ball_rows(matrix: sparse.csr_matrix) -> list[list[tuple[int, acb]]]:
    output: list[list[tuple[int, acb]]] = []
    for row in range(matrix.shape[0]):
        start, stop = int(matrix.indptr[row]), int(matrix.indptr[row + 1])
        output.append(
            [
                (int(matrix.indices[index]), acb_from_complex(matrix.data[index]))
                for index in range(start, stop)
            ]
        )
    return output


def ball_matvec(
    rows: list[list[tuple[int, acb]]], vector: list[acb]
) -> list[acb]:
    return [
        sum((coefficient * vector[column] for column, coefficient in row), acb(0))
        for row in rows
    ]


def component_upper(value: acb) -> float:
    return float(abs(value.real).upper()) + float(abs(value.imag).upper())


def residual(
    rows: list[list[tuple[int, acb]]], rhs: list[acb], vector: list[acb]
) -> tuple[list[acb], float, float]:
    values = ball_matvec(rows, vector)
    errors = [right - left for right, left in zip(rhs, values, strict=True)]
    midpoint = max(
        (
            abs(complex(float(value.real.mid()), float(value.imag.mid())))
            for value in errors
        ),
        default=0.0,
    )
    bound = max((component_upper(value) for value in errors), default=0.0)
    return errors, midpoint, bound


def mixed_refine(
    factor: Any,
    rows: list[list[tuple[int, acb]]],
    rhs: list[acb],
    initial: np.ndarray,
    iterations: int,
) -> tuple[list[acb], list[dict[str, float | int]]]:
    value = [acb_from_complex(entry) for entry in initial]
    history: list[dict[str, float | int]] = []
    previous = math.inf
    for iteration in range(iterations):
        errors, midpoint_maximum, component_bound = residual(rows, rhs, value)
        history.append(
            {
                "iteration": iteration,
                "maximum_residual_midpoint": midpoint_maximum,
                "maximum_residual_ball_component_upper": component_bound,
            }
        )
        print(
            f"CBF.T65 refinement iteration={iteration} "
            f"residual={midpoint_maximum:.3e} ball={component_bound:.3e}",
            flush=True,
        )
        if midpoint_maximum == 0.0 or midpoint_maximum < 2.0**-300:
            break
        exponent = math.frexp(midpoint_maximum)[1]
        scale = math.ldexp(1.0, exponent)
        midpoint = np.asarray(
            [
                complex(float(entry.real.mid()), float(entry.imag.mid())) / scale
                for entry in errors
            ],
            dtype=np.complex128,
        )
        correction = factor.solve(midpoint) * scale
        for position, entry in enumerate(correction):
            value[position] += acb_from_complex(entry)
        if midpoint_maximum >= previous and iteration >= 4:
            break
        previous = midpoint_maximum
    return value, history


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--seed", type=int, default=7909)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--input-directory", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--iterations", type=int, default=24)
    arguments = parser.parse_args()
    if arguments.prepare:
        prepare(arguments.input_directory, arguments.rows, arguments.seed)
    if arguments.prepare_only:
        return 0

    ctx.prec = arguments.precision
    metadata = load_metadata(arguments.input_directory)
    require(metadata["seed"] == arguments.seed, "seed binding")
    matrix_path = ROOT / metadata["matrix"]["path"]
    rhs_path = ROOT / metadata["rhs"]["path"]
    coefficients_path = ROOT / metadata["denominator_coefficients"]["path"]
    constant_path = ROOT / metadata["denominator_constant"]["path"]
    for binding, path in (
        (metadata["matrix"], matrix_path),
        (metadata["rhs"], rhs_path),
        (metadata["denominator_coefficients"], coefficients_path),
        (metadata["denominator_constant"], constant_path),
    ):
        require(artifact(path) == binding, f"input binding: {path}")
    matrix = sparse.load_npz(matrix_path).tocsr()
    rhs = np.load(rhs_path, allow_pickle=False)
    denominator_coefficients = np.load(coefficients_path, allow_pickle=False)
    denominator_constant = np.load(constant_path, allow_pickle=False)[0]
    require(matrix.shape == (6777, 6777), "matrix shape")
    require(rhs.shape == denominator_coefficients.shape == (6777,), "vector shapes")

    factor = splu(
        matrix.tocsc(),
        permc_spec="COLAMD",
        diag_pivot_thresh=1.0,
        options={"Equil": True, "IterRefine": "EXTRA"},
    )
    initial = factor.solve(rhs)
    for _ in range(5):
        initial += factor.solve(rhs - matrix @ initial)
    rows = ball_rows(matrix)
    rhs_ball = [acb_from_complex(value) for value in rhs]
    refined, history = mixed_refine(
        factor, rows, rhs_ball, initial, arguments.iterations
    )
    _errors, final_midpoint, final_component = residual(rows, rhs_ball, refined)
    denominator = acb_from_complex(denominator_constant) + sum(
        (
            acb_from_complex(coefficient) * value
            for coefficient, value in zip(
                denominator_coefficients, refined, strict=True
            )
        ),
        acb(0),
    )
    scale = acb(585) / (2 * denominator)
    denominator_midpoint = complex(
        float(denominator.real.mid()), float(denominator.imag.mid())
    )
    scale_midpoint = complex(float(scale.real.mid()), float(scale.imag.mid()))
    checks = {
        "the_selected_binary_matrix_has_a_complete_sparse_LU": bool(
            factor.L.shape == factor.U.shape == (6777, 6777)
        ),
        "Arb_residual_refinement_improves_the_initial_binary_solve": bool(
            final_midpoint < history[0]["maximum_residual_midpoint"]
        ),
        "the_refined_binary_denominator_excludes_zero_arithmetically": bool(
            not denominator.contains(0)
        ),
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"refinement checks: {checks}")
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-binary-mixed-refinement.v1",
        "theorem_id": "CBF.T65",
        "status": "EXACT_DYADIC_MATRIX_MIXED_REFINEMENT_SCOUT",
        "precision_bits": arguments.precision,
        "iterations_requested": arguments.iterations,
        "input": metadata,
        "factor": {
            "L_nonzeros": int(factor.L.nnz),
            "U_nonzeros": int(factor.U.nnz),
        },
        "refinement": {
            "history": history,
            "final_maximum_residual_midpoint": final_midpoint,
            "final_maximum_residual_ball_component_upper": final_component,
        },
        "toric_Jacobian_coordinate_midpoint": [
            denominator_midpoint.real,
            denominator_midpoint.imag,
        ],
        "toric_Jacobian_coordinate_Arb": str(denominator),
        "canonical_Serre_scale_midpoint": [
            scale_midpoint.real,
            scale_midpoint.imag,
        ],
        "canonical_Serre_scale_Arb": str(scale),
        "checks": checks,
        "guardrails": {
            "the_Arb_arithmetic_radius_is_called_a_forward_error_bound": False,
            "frozen_binary_coefficients_are_called_exact_geometry": False,
            "a_physical_eta9_selection_is_claimed": False,
        },
        "next": "Replace every frozen binary matrix, top-anchor and Jacobian coefficient by its selected 512-bit characteristic-zero ball and certify the inverse by a strict Neumann bound.",
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    arguments.output.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T65 binary mixed refinement: PASS "
        f"residual={final_midpoint:.3e} denominator={denominator_midpoint:.8g} "
        f"s_C={scale_midpoint:.8g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
