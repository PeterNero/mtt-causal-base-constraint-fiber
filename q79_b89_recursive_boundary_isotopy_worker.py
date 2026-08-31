#!/usr/bin/env python3
"""Recursively certify difficult B89 signed-boundary isotopy cells.

The complete-cell certifier is mathematically preferable when it succeeds.
When its Taylor-Krawczyk enclosure is too wide, this wrapper bisects only the
failed parameter cell, retains every passing child certificate, and proves
that the labelled endpoint tubes glue uniquely across all child boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
CELL_CERTIFIER = HERE / "q79_b89_boundary_direct_homotopy_cell_worker.py"
CARRIER_SIZE = 36
PAIR_COUNT = CARRIER_SIZE * (CARRIER_SIZE - 1) // 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_box(value: dict) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    return (
        Decimal(value["real"][0]),
        Decimal(value["real"][1]),
        Decimal(value["imag"][0]),
        Decimal(value["imag"][1]),
    )


def overlaps(left, right) -> bool:
    return (
        max(left[0], right[0]) <= min(left[1], right[1])
        and max(left[2], right[2]) <= min(left[3], right[3])
    )


def endpoint_binding(previous_tubes: list[dict], current_tubes: list[dict]) -> dict:
    previous = {
        int(tube["branch"]): parse_box(tube["right_endpoint_x_box"])
        for tube in previous_tubes
    }
    current = {
        int(tube["branch"]): parse_box(tube["left_endpoint_x_box"])
        for tube in current_tubes
    }
    require(
        set(previous) == set(current) == set(range(CARRIER_SIZE)),
        "complete boundary endpoint label sets",
    )
    matches = 0
    for label, box in previous.items():
        hits = [
            candidate
            for candidate, candidate_box in current.items()
            if overlaps(box, candidate_box)
        ]
        require(hits == [label], f"unique endpoint overlap label={label} hits={hits}")
        matches += 1
    return {
        "bound_branches": len(previous),
        "unique_label_matches": matches,
        "identity_matching": True,
    }


def minimum_optional(values):
    present = [value for value in values if value is not None]
    return min(present) if present else None


def _fraction_tag(value: Fraction) -> str:
    return f"{value.numerator}of{value.denominator}"


def child_command(
    args,
    interval: int,
    start: Fraction,
    stop: Fraction,
    output: Path,
) -> list[str]:
    return [
        sys.executable,
        str(CELL_CERTIFIER),
        "--baseline-root",
        str(Path(args.baseline_root).resolve()),
        "--source",
        str(Path(args.source).resolve()),
        "--guides",
        str(Path(args.guides).resolve()),
        "--metadata",
        str(Path(args.metadata).resolve()),
        "--interval-start",
        str(interval),
        "--interval-stop",
        str(interval + 1),
        "--precision",
        str(args.precision),
        "--predictor-degree",
        str(args.predictor_degree),
        "--taylor-order",
        str(args.taylor_order),
        "--separation-max-depth",
        str(args.separation_max_depth),
        "--tube-factors",
        args.tube_factors,
        "--cell-fraction-start",
        str(start),
        "--cell-fraction-stop",
        str(stop),
        "--output",
        str(output),
    ]


def validate_child(
    packet: dict,
    args,
    interval: int,
    start: Fraction,
    stop: Fraction,
) -> dict:
    require(
        packet["schema"]
        == "mtt.preprojection.q79-eta9-b89-boundary-taylor-krawczyk.v1",
        "child schema",
    )
    require(packet["interval_range"] == [interval, interval + 1], "child interval")
    require(packet["cell_fraction"] == [str(start), str(stop)], "child fraction")
    require(all(packet["checks"].values()) and not packet["failures"], "child checks")
    require(len(packet["rows"]) == 1, "one child row")
    row = packet["rows"][0]
    require(row["cell_fraction"] == [str(start), str(stop)], "row fraction")
    require(
        row["certified_branches"] == CARRIER_SIZE
        and len(row["tubes"]) == CARRIER_SIZE,
        "child carrier",
    )
    certificate = packet.get("direct_homotopy_certificate") or {}
    require(certificate.get("certified_cell_calls") == 1, "direct homotopy child")
    row["direct_homotopy_certificate"] = certificate
    return row


def run_child(
    args,
    interval: int,
    start: Fraction,
    stop: Fraction,
    depth: int,
    directory: Path,
) -> tuple[dict | None, dict]:
    output = directory / (
        f"interval-{interval}-{_fraction_tag(start)}-{_fraction_tag(stop)}.json"
    )
    completed = subprocess.run(
        child_command(args, interval, start, stop, output),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    diagnostic = {
        "cell_fraction": [str(start), str(stop)],
        "depth": depth,
        "passed": False,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout.splitlines()[-4:],
        "stderr_tail": completed.stderr.splitlines()[-10:],
    }
    if completed.returncode != 0 or not output.is_file():
        return None, diagnostic
    packet = json.loads(output.read_text(encoding="ascii"))
    row = validate_child(packet, args, interval, start, stop)
    diagnostic["passed"] = True
    return row, diagnostic


def certify_interval(
    args,
    interval: int,
    directory: Path,
    runner=run_child,
) -> tuple[list[dict], list[dict], int]:
    diagnostics = []
    maximum_depth = 0

    def visit(start: Fraction, stop: Fraction, depth: int) -> list[dict]:
        nonlocal maximum_depth
        maximum_depth = max(maximum_depth, depth)
        row, diagnostic = runner(args, interval, start, stop, depth, directory)
        diagnostics.append(diagnostic)
        if row is not None:
            return [row]
        if depth >= args.max_dyadic_depth:
            tail = diagnostic.get("stderr_tail") or diagnostic.get("stdout_tail")
            raise RuntimeError(
                f"dyadic certification exhausted interval={interval} "
                f"cell={start}:{stop} depth={depth} diagnostic={tail}"
            )
        midpoint = (start + stop) / 2
        return visit(start, midpoint, depth + 1) + visit(
            midpoint, stop, depth + 1
        )

    subcells = visit(Fraction(0), Fraction(1), 0)
    for index, row in enumerate(subcells):
        row["binding_from_previous_subcell"] = (
            endpoint_binding(subcells[index - 1]["tubes"], row["tubes"])
            if index
            else None
        )
    return subcells, diagnostics, maximum_depth


def aggregate_logical_row(
    interval: int,
    subcells: list[dict],
    binding,
    maximum_dyadic_depth: int,
) -> dict:
    return {
        "interval": interval,
        "subdivision_count": len(subcells),
        "maximum_dyadic_depth": maximum_dyadic_depth,
        "certified_branches": subcells[0]["certified_branches"],
        "minimum_Krawczyk_margin": min(
            row["minimum_Krawczyk_margin"] for row in subcells
        ),
        "separation": {
            "certified_pairs": sum(
                row["separation"]["certified_pairs"] for row in subcells
            ),
            "coarse_pairs": sum(
                row["separation"]["coarse_pairs"] for row in subcells
            ),
            "refined_pair_count": sum(
                row["separation"]["refined_pair_count"] for row in subcells
            ),
            "leaf_intervals": sum(
                row["separation"]["leaf_intervals"] for row in subcells
            ),
            "maximum_refinement_depth": max(
                row["separation"]["maximum_refinement_depth"] for row in subcells
            ),
            "minimum_modulus_lower": minimum_optional(
                row["separation"]["minimum_modulus_lower"] for row in subcells
            ),
        },
        "guide_homotopy": {
            "certified_pairs": sum(
                row["guide_homotopy"]["certified_pairs"] for row in subcells
            ),
            "coarse_pairs": sum(
                row["guide_homotopy"]["coarse_pairs"] for row in subcells
            ),
            "direct_polynomial_pairs": sum(
                row["guide_homotopy"]["direct_polynomial_pairs"]
                for row in subcells
            ),
            "refined_pair_count": sum(
                row["guide_homotopy"]["refined_pair_count"] for row in subcells
            ),
            "leaf_intervals": sum(
                row["guide_homotopy"]["leaf_intervals"] for row in subcells
            ),
            "maximum_refinement_depth": max(
                row["guide_homotopy"]["maximum_refinement_depth"]
                for row in subcells
            ),
            "minimum_Rouche_margin": minimum_optional(
                row["guide_homotopy"]["minimum_Rouche_margin"]
                for row in subcells
            ),
        },
        "binding_from_previous_interval": binding,
        "subcells": subcells,
    }


def build_checkpoint_packet(
    args,
    metadata: dict,
    source_path: Path,
    guides_path: Path,
    metadata_path: Path,
    logical_rows: list[dict],
    attempts: list[dict],
    started: float,
) -> dict:
    selected_subcells = sum(len(row["subcells"]) for row in logical_rows)
    certified_stop = args.interval_start + len(logical_rows)
    return {
        "schema": "mtt.preprojection.q79-eta9-b89-adaptive-boundary-taylor-krawczyk.v1",
        "tier": "CERTIFIED_RECURSIVE_DYADIC_COMPLETE_BOUNDARY_TUBES_AND_GUIDE_ISOTOPY",
        "source_sha256": sha256(source_path),
        "guide_payload_sha256": sha256(guides_path),
        "guide_metadata_sha256": sha256(metadata_path),
        "edge": int(metadata["edge"]),
        "interval_range": [args.interval_start, certified_stop],
        "requested_interval_range": [args.interval_start, args.interval_stop],
        "checkpoint": {
            "complete_requested_range": certified_stop == args.interval_stop,
            "certified_interval_count": len(logical_rows),
            "next_interval": certified_stop,
            "atomic_replace": True,
        },
        "precision_bits": args.precision,
        "predictor_degree": args.predictor_degree,
        "taylor_order": args.taylor_order,
        "separation_max_depth": args.separation_max_depth,
        "subdivision_schedule": [
            2**depth for depth in range(args.max_dyadic_depth + 1)
        ],
        "recursive_dyadic_policy": {
            "maximum_depth": args.max_dyadic_depth,
            "only_failed_cells_are_bisected": True,
            "every_leaf_has_an_independent_boundary_cell_certificate": True,
            "worker_sha256": sha256(Path(__file__).resolve()),
            "cell_certifier_sha256": sha256(CELL_CERTIFIER),
        },
        "logical_rows": logical_rows,
        "attempts": attempts,
        "failures": [],
        "counts": {
            "logical_intervals": len(logical_rows),
            "certified_subcells": selected_subcells,
            "certified_boundary_tubes": selected_subcells * CARRIER_SIZE,
            "same_parameter_pair_certificates": selected_subcells * PAIR_COUNT,
            "guide_homotopy_pair_certificates": selected_subcells * PAIR_COUNT,
            "adaptively_subdivided_intervals": sum(
                len(row["subcells"]) > 1 for row in logical_rows
            ),
            "failed_parent_attempts": sum(
                not attempt["passed"]
                for interval in attempts
                for attempt in interval["attempts"]
            ),
        },
        "checks": {
            "every_declared_logical_interval_has_a_finite_dyadic_certificate": True,
            "every_selected_subcell_has_all_36_boundary_tubes": True,
            "every_same_parameter_pair_is_separated_on_every_selected_subcell": True,
            "every_source_to_linear_guide_pair_homotopy_excludes_zero": True,
            "all_subcells_and_logical_cells_have_unique_endpoint_label_bindings": True,
            "the_guide_payload_and_metadata_are_hash_bound": True,
            "only_failed_cells_are_recursively_bisected": True,
            "the_declared_interval_range_is_exactly_the_atomic_checkpoint_prefix": True,
        },
        "elapsed_seconds": time.monotonic() - started,
        "guardrails": {
            "a_failed_coarse_cell_is_not_called_a_singularity": True,
            "a_process_success_is_not_called_a_theorem": True,
            "a_partial_checkpoint_is_not_called_complete_coverage": True,
            "claims_the_complete_boundary_or_mixed_carrier_is_certified_here": False,
            "claims_Deligne_beta_C_U_eta9_or_HYM": False,
        },
    }


def write_checkpoint(path: Path, packet: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--guides", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--interval-start", type=int, required=True)
    parser.add_argument("--interval-stop", type=int, required=True)
    parser.add_argument("--precision", type=int, default=512)
    parser.add_argument("--predictor-degree", type=int, default=12)
    parser.add_argument("--taylor-order", type=int, default=14)
    parser.add_argument("--separation-max-depth", type=int, default=24)
    parser.add_argument(
        "--tube-factors",
        default="1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384",
    )
    parser.add_argument("--max-dyadic-depth", type=int, default=7)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    require(args.interval_start < args.interval_stop, "nonempty interval range")
    require(0 <= args.max_dyadic_depth <= 12, "bounded dyadic depth")
    source_path = Path(args.source).resolve()
    guides_path = Path(args.guides).resolve()
    metadata_path = Path(args.metadata).resolve()
    metadata = json.loads(metadata_path.read_text(encoding="ascii"))
    require(metadata["payload"]["sha256"] == sha256(guides_path), "guide hash")
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    logical_rows = []
    attempts = []
    previous_tubes = None
    require(CELL_CERTIFIER.is_file(), "boundary cell certifier")
    with tempfile.TemporaryDirectory(prefix="mtt-recursive-boundary-") as temporary:
        directory = Path(temporary)
        for interval in range(args.interval_start, args.interval_stop):
            subcells, diagnostics, maximum_depth = certify_interval(
                args, interval, directory
            )
            binding = (
                endpoint_binding(previous_tubes, subcells[0]["tubes"])
                if previous_tubes is not None
                else None
            )
            logical_rows.append(
                aggregate_logical_row(interval, subcells, binding, maximum_depth)
            )
            previous_tubes = subcells[-1]["tubes"]
            attempts.append({"interval": interval, "attempts": diagnostics})
            output = build_checkpoint_packet(
                args,
                metadata,
                source_path,
                guides_path,
                metadata_path,
                logical_rows,
                attempts,
                started,
            )
            write_checkpoint(output_path, output)
            print(
                f"interval={interval} leaves={len(subcells)} "
                f"maximum_dyadic_depth={maximum_depth}",
                flush=True,
            )

    selected_subcells = sum(len(row["subcells"]) for row in logical_rows)
    print(
        "recursive adaptive boundary-isotopy shard PASS "
        f"logical={len(logical_rows)} leaves={selected_subcells} "
        f"elapsed={output['elapsed_seconds']:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
