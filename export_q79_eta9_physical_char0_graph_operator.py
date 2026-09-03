#!/usr/bin/env python3
"""Export the committed H4 characteristic-zero graph operator for CBF.T72.

This is a provenance compiler, not part of the ordinary T72 replay.  It reads
only the declared clean files in the adjacent H4 and UST repositories and
emits a deterministic gzip-compressed interval source snapshot.  The normal
builder and verifier consume that local snapshot and are machine-independent.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from flint import acb, acb_mat, arb, ctx


ROOT = Path(__file__).resolve().parent
DEFAULT_H4 = ROOT.parent / "mtt-preprojection-repair-calculus"
OUTPUT = ROOT / "q79_eta9_physical_char0_graph_operator.input.json.gz"
SEGMENTS = ("edge-0", "edge-1", "edge-2")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def binding(repository: Path, path: Path) -> dict[str, Any]:
    relative = path.resolve().relative_to(repository.resolve()).as_posix()
    require(path.is_file(), f"bound source exists: {path}")
    require(not git(repository, "status", "--short", "--", relative), f"dirty source: {path}")
    return {
        "repository": repository.name,
        "repository_commit": git(repository, "rev-parse", "HEAD"),
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def parse_acb(value: str) -> acb:
    if value.endswith("j") and " + " in value:
        real, imaginary = value.removesuffix("j").rsplit(" + ", 1)
        return acb(arb(real), arb(imaginary))
    return acb(arb(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--h4-repository", type=Path, default=DEFAULT_H4)
    parser.add_argument("--precision", type=int, default=768)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    h4 = arguments.h4_repository.resolve()
    ust = h4.parent / "mtt-unified-source-theorem"
    require(h4.is_dir() and ust.is_dir(), "adjacent H4 and UST repositories")
    require(arguments.precision >= 512, "source precision")
    ctx.prec = arguments.precision

    graph = h4 / "experiments/q79_eta9_graph_normal_duality"
    ramification = h4 / "experiments/q79_eta9_ramification_coefficient_transport"
    sys.path[:0] = [str(graph), str(ramification)]
    import q79_framed_member_exact_complex_core as core
    import build_physical_midpoint_coefficient_jet_scout as physical

    modules = core.import_ust_modules()
    g3ae, g3af, g3ag = (modules[name] for name in ("g3ae", "g3af", "g3ag"))
    core.install_acb_cayley_reduction(g3ag)
    gamma, rho, mu = core.isolate_frame_roots()
    ring = core.AcbRing(gamma)
    expression = core.load(core.CHART)["inputs"]["embedded_fixed_K3_sextic"]
    first = core.representative_box("first_H", expression)
    second = core.representative_box("second_H", expression)
    basis = g3ae.coefficient_basis()
    targets = core.four_h_targets(g3ag, ring, rho, mu)
    rows = (
        g3af.matrix_for_graph(basis, first, ring)
        + g3af.matrix_for_graph(basis, second, ring)
        + g3ag.four_h_matrix(basis, targets, ring)
    )
    rebuilt_basis, member, diagnostics = core.build_exact_member()
    require(basis == rebuilt_basis, "coefficient basis agreement")
    require(len(rows) == 168 and all(len(row) == 249 for row in rows), "168x249 incidence")
    require(len(member) == 249, "249 member coefficients")
    require(
        [sum(1 for row in basis if int(row["target_coordinate"]) == block) for block in range(3)]
        == [83, 83, 83],
        "three 83-coordinate blocks",
    )

    incidence = core.load(core.G3AK)["incidence_certificate"]
    pivots = [int(value) for value in incidence["pivot_columns_zero_based"]]
    free = [int(value) for value in incidence["free_columns_zero_based"]]
    selected_rows = [int(value) for value in diagnostics["selected_minor_rows_zero_based"]]
    require((len(pivots), len(free), len(selected_rows)) == (126, 123, 126), "126+123 split")
    pivot_block = acb_mat(
        126,
        126,
        [rows[row][column] for row in selected_rows for column in pivots],
    )
    require(not pivot_block.det().contains(0), "characteristic-zero pivot minor")

    midpoint_dir = ramification / "outputs/physical_midpoint_jets"
    midpoint_packets = {}
    physical_rows = {}
    for segment in SEGMENTS:
        packet_path = midpoint_dir / f"{segment}.packet.json"
        packet = json.loads(packet_path.read_text(encoding="ascii"))
        require(packet["geometry"]["segment"] == segment, f"segment {segment}")
        require(all(packet["checks"].values()), f"midpoint checks {segment}")
        _q, _q_tangent, point, _tangent, _lift = physical.physical_midpoint(segment)
        stored = [parse_acb(value) for value in packet["geometry"]["Fermat_point"]]
        require(all(left.overlaps(right) for left, right in zip(point, stored, strict=True)), f"point overlap {segment}")
        require(sum((value**3 for value in point), acb(0)).contains(0), f"Fermat equation {segment}")
        midpoint_packets[segment] = binding(h4, packet_path)
        physical_rows[segment] = [str(value) for value in point]

    h4_paths = [
        Path(core.__file__),
        Path(physical.__file__),
        core.REPRESENTATIVE,
        core.SURPLUS,
        core.CHART,
        core.CHAR0,
        core.K3_SOURCE,
        ramification / "outputs/q79_eta9_physical_midpoint_ramification_atlas_contract.packet.json",
    ]
    ust_paths = [Path(module.__file__) for module in modules.values()] + [core.G3AD, core.G3AG, core.G3AK]
    payload = {
        "schema": "mtt.cbf.q79-eta9-physical-char0-graph-operator-input.v1",
        "precision_bits": arguments.precision,
        "source_repositories": {
            "H4": {"path_name": h4.name, "commit": git(h4, "rev-parse", "HEAD")},
            "UST": {"path_name": ust.name, "commit": git(ust, "rev-parse", "HEAD")},
        },
        "source_bindings": {
            "H4": [binding(h4, path) for path in h4_paths],
            "UST": [binding(ust, path) for path in ust_paths],
            "physical_midpoints": midpoint_packets,
        },
        "coefficient_basis": basis,
        "incidence": {
            "ambient_rows": 168,
            "ambient_columns": 249,
            "rank": 126,
            "pivot_columns_zero_based": pivots,
            "free_columns_zero_based": free,
            "selected_rows_zero_based": selected_rows,
            "selected_pivot_block_entries_row_major": [
                str(rows[row][column]) for row in selected_rows for column in pivots
            ],
            "selected_free_block_entries_row_major": [
                str(rows[row][column]) for row in selected_rows for column in free
            ],
        },
        "selected_member_coefficients": [str(value) for value in member],
        "selected_member_diagnostics": diagnostics,
        "physical_midpoint_rows": physical_rows,
        "upstream_claims": {
            "affine_graph_tangent_rank": 123,
            "projective_graph_tangent_rank": 122,
            "radial_line_is_the_projective_quotient": True,
            "three_midpoint_rows_are_selected_path_values_not_probe_knobs": True,
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_bytes(compressed)
    print(
        "q79 eta9 physical char0 source export: PASS "
        f"raw={len(raw)} gzip={len(compressed)} sha256={sha256(arguments.output)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
