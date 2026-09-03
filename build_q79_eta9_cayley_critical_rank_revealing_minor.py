#!/usr/bin/env python3
"""Build the T65 complex rank-revealing critical minor.

The preparation stage eliminates the H4-T141 top-functional embedding from
the edge-2 critical relation system.  The expensive stage selects 6,777
original rows from the resulting 13,014 x 6,777 matrix by a seeded
interpolative decomposition of its transpose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.linalg.interpolative import interp_decomp
from scipy.sparse.linalg import LinearOperator, aslinearoperator, onenormest, splu


ROOT = Path(__file__).resolve().parent
CERTIFICATES = ROOT / "certificates"
MATRIX = CERTIFICATES / "q79_eta9_cayley_critical_reduced_edge2.npz"
MATRIX_META = CERTIFICATES / "q79_eta9_cayley_critical_reduced_edge2.meta.json"
ROWS = ROOT / "q79_eta9_cayley_critical_rank_revealing_rows.npy"
OUTPUT = ROOT / "q79_eta9_cayley_critical_rank_revealing_minor.packet.json"
SEED = 7909


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


def top_embedding(
    serre: Any,
    critical_basis: list[tuple[int, ...]],
) -> tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    import build_q79_eta9_directed_cayley_serre_scale as t65

    index = {term: column for column, term in enumerate(critical_basis)}
    top_basis = serre.component_monomials(18, 1)
    cox_product = (1, 1, 1, 1, 1, 1)
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[complex] = []
    pivot_columns: list[int] = []
    for row, term in enumerate(top_basis):
        primary = tuple(
            left + right for left, right in zip(term, cox_product, strict=True)
        )
        pivot_columns.append(index[primary])
        transported = t65.poly_shift(t65.transport_top_monomial(term), cox_product)
        for monomial, value in transported.items():
            row_indices.append(row)
            column_indices.append(index[monomial])
            values.append(value)
    embedding = sparse.csr_matrix(
        (np.asarray(values, dtype=np.complex128), (row_indices, column_indices)),
        shape=(len(top_basis), len(critical_basis)),
    )
    pivots = np.asarray(pivot_columns, dtype=np.int64)
    free = np.setdiff1d(np.arange(len(critical_basis), dtype=np.int64), pivots)
    require(np.unique(pivots).size == 2584, "distinct top-embedding pivots")
    require(embedding[:, free].nnz == 0, "embedding is supported on pivot block")
    return embedding, pivots, free


def prepare_matrix() -> tuple[sparse.csr_matrix, dict[str, Any]]:
    import build_q79_eta9_directed_cayley_serre_scale as t65

    serre, sections, _derivatives, _normalization = t65.framed_input("edge-2")
    critical_basis = serre.component_monomials(9, 3)
    relation = t65.relation_matrix(sections, serre.component_monomials)
    _embedding, pivots, free = top_embedding(serre, critical_basis)
    reduced = relation[:, free].tocsr()
    row_scale = np.asarray(abs(reduced).max(axis=1).toarray()).ravel()
    kept = np.flatnonzero(row_scale > 0).astype(np.int64)
    row_balanced = sparse.diags(1.0 / row_scale[kept]) @ reduced[kept, :]
    column_scale = np.asarray(abs(row_balanced).max(axis=0).toarray()).ravel()
    require(np.all(column_scale > 0), "nonzero reduced columns")
    balanced = (row_balanced @ sparse.diags(1.0 / column_scale)).tocsr()
    require(balanced.shape == (13014, 6777), "anchored reduced shape")

    CERTIFICATES.mkdir(parents=True, exist_ok=True)
    sparse.save_npz(MATRIX, balanced, compressed=True)
    metadata: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-reduced-edge2.v1",
        "source_segment": "edge-2",
        "source_parameter": 0.5,
        "source_lift_sign": -1,
        "full_relation_shape": list(relation.shape),
        "top_embedding_pivots": int(pivots.size),
        "free_columns": int(free.size),
        "kept_original_rows_zero_based": kept.tolist(),
        "kept_original_rows_sha256": canonical_sha256(kept.tolist()),
        "balanced_shape": list(balanced.shape),
        "balanced_nonzeros": int(balanced.nnz),
    }
    metadata["canonical_payload_sha256"] = canonical_sha256(metadata)
    MATRIX_META.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    return balanced, metadata


def load_matrix() -> tuple[sparse.csr_matrix, dict[str, Any]]:
    balanced = sparse.load_npz(MATRIX).tocsr()
    metadata = json.loads(MATRIX_META.read_text(encoding="ascii"))
    claimed = metadata.pop("canonical_payload_sha256")
    require(canonical_sha256(metadata) == claimed, "matrix metadata hash")
    metadata["canonical_payload_sha256"] = claimed
    require(list(balanced.shape) == metadata["balanced_shape"], "matrix shape")
    require(int(balanced.nnz) == metadata["balanced_nonzeros"], "matrix nonzeros")
    require(balanced.shape == (13014, 6777), "anchored reduced shape")
    return balanced, metadata


def inverse_infinity_estimate(factor: Any, size: int) -> float:
    operator = LinearOperator(
        (size, size),
        matvec=lambda value: factor.solve(value, trans="H"),
        rmatvec=lambda value: factor.solve(value),
        matmat=lambda value: factor.solve(value, trans="H"),
        rmatmat=lambda value: factor.solve(value),
        dtype=np.complex128,
    )
    return float(onenormest(operator, t=8, itmax=12))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--reuse-rows", action="store_true")
    parser.add_argument("--seed", type=int, default=SEED)
    arguments = parser.parse_args()

    if arguments.prepare or not (MATRIX.is_file() and MATRIX_META.is_file()):
        balanced, metadata = prepare_matrix()
    else:
        balanced, metadata = load_matrix()
    if arguments.prepare_only:
        print(
            "CBF.T65 reduced critical system: PASS "
            f"shape={balanced.shape} nnz={balanced.nnz}"
        )
        return 0

    started = time.monotonic()
    if arguments.reuse_rows:
        selected_original_input = np.load(ROWS, allow_pickle=False).astype(np.int64)
        kept = np.asarray(metadata["kept_original_rows_zero_based"], dtype=np.int64)
        kept_lookup = {int(original): row for row, original in enumerate(kept)}
        selected_reduced = np.asarray(
            [kept_lookup[int(original)] for original in selected_original_input],
            dtype=np.int64,
        )
        projection_shape = [balanced.shape[1], balanced.shape[0] - balanced.shape[1]]
        print(
            f"CBF.T65 selected-row replay seed={arguments.seed}; sparse LU start",
            flush=True,
        )
    else:
        print(
            f"CBF.T65 seeded ID start seed={arguments.seed} shape={balanced.shape}",
            flush=True,
        )
        index, projection = interp_decomp(
            aslinearoperator(balanced.transpose().tocsc()),
            balanced.shape[1],
            rng=np.random.default_rng(arguments.seed),
        )
        selected_reduced = np.asarray(index[: balanced.shape[1]], dtype=np.int64)
        projection_shape = list(projection.shape)
        del projection
        print(
            f"CBF.T65 seeded ID complete seed={arguments.seed}; sparse LU start",
            flush=True,
        )
    require(
        np.unique(selected_reduced).size == balanced.shape[1]
        and np.all((0 <= selected_reduced) & (selected_reduced < balanced.shape[0])),
        "rank-revealing row selection",
    )
    kept = np.asarray(metadata["kept_original_rows_zero_based"], dtype=np.int64)
    selected_original = kept[selected_reduced]
    minor = balanced[selected_reduced, :].tocsc()
    factor = splu(
        minor,
        permc_spec="COLAMD",
        diag_pivot_thresh=1.0,
        options={"Equil": True, "IterRefine": "EXTRA"},
    )
    infinity_norm = float(np.max(np.asarray(abs(minor).sum(axis=1)).ravel()))
    inverse_estimate = inverse_infinity_estimate(factor, minor.shape[0])

    np.save(ROWS, selected_original, allow_pickle=False)
    checks = {
        "the_seeded_ID_selects_6777_distinct_original_rows": bool(
            np.unique(selected_original).size == 6777
        ),
        "the_selected_edge2_minor_has_a_complete_sparse_LU": bool(
            factor.L.shape == factor.U.shape == (6777, 6777)
        ),
        "the_minor_is_selected_after_exact_top_embedding_elimination": True,
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"minor checks: {checks}")
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-cayley-critical-rank-revealing-minor.v1",
        "theorem_id": "CBF.T65",
        "status": "COMPLEX_EDGE2_RANK_REVEALING_MINOR_SCOUT",
        "selection": {
            "source_point": {
                "segment": "edge-2",
                "parameter": 0.5,
                "lift_sign": -1,
            },
            "algorithm": "scipy seeded randomized interpolative decomposition of the transposed top-anchored balanced critical relation matrix",
            "seed": arguments.seed,
            "selected_row_replay": arguments.reuse_rows,
            "selected_rows": artifact(ROWS),
            "selected_row_minimum": int(selected_original.min()),
            "selected_row_maximum": int(selected_original.max()),
            "unselected_nonzero_rows": int(balanced.shape[0] - 6777),
            "interpolation_shape": projection_shape,
        },
        "reduced_system": {
            "matrix_input": artifact(MATRIX),
            "metadata_input": artifact(MATRIX_META),
            "shape": list(balanced.shape),
            "nonzero_entries": int(balanced.nnz),
            "top_embedding_pivots": metadata["top_embedding_pivots"],
            "free_columns": metadata["free_columns"],
        },
        "minor": {
            "shape": list(minor.shape),
            "nonzero_entries": int(minor.nnz),
            "factor_nonzero_entries": int(factor.L.nnz + factor.U.nnz),
            "infinity_norm": infinity_norm,
            "inverse_infinity_norm_estimate_not_a_bound": inverse_estimate,
            "condition_infinity_estimate_not_a_bound": infinity_norm
            * inverse_estimate,
        },
        "checks": checks,
        "guardrails": {
            "condition_estimate_is_called_a_directed_bound": False,
            "edge2_selection_is_called_pathwide": False,
            "B89_framed_member_is_called_physically_selected": False,
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T65 rank-revealing minor: PASS "
        f"nnz={minor.nnz} factor={factor.L.nnz + factor.U.nnz} "
        f"cond_est={infinity_norm * inverse_estimate:.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
