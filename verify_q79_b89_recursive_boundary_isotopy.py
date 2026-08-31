#!/usr/bin/env python3
"""Independently verify a recursive B89 boundary-isotopy result shard."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKER = HERE / "q79_b89_recursive_boundary_isotopy_worker.py"
CELL_WORKER = HERE / "q79_b89_boundary_direct_homotopy_cell_worker.py"
BASELINE_CELL_RELATIVE = Path(
    "experiments/q79_eta9_b89_family_branch_braid_pilot/"
    "certify_right80_boundary_taylor_flint.py"
)
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


def independent_binding(previous_tubes: list[dict], current_tubes: list[dict]) -> dict:
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
        "boundary endpoint labels",
    )
    count = 0
    for label, box in previous.items():
        hits = [
            candidate
            for candidate, candidate_box in current.items()
            if overlaps(box, candidate_box)
        ]
        require(hits == [label], f"independent endpoint identity label={label}")
        count += 1
    return {
        "bound_branches": count,
        "unique_label_matches": count,
        "identity_matching": True,
    }


def minimum_optional(values):
    present = [value for value in values if value is not None]
    return min(present) if present else None


def verify_attempt_tree(
    logical_row: dict,
    attempt_entry: dict,
    maximum_allowed_depth: int,
) -> None:
    require(attempt_entry["interval"] == logical_row["interval"], "attempt interval")
    attempts = {}
    for attempt in attempt_entry["attempts"]:
        start, stop = map(Fraction, attempt["cell_fraction"])
        key = (start, stop)
        require(key not in attempts, "attempt cell uniqueness")
        require(0 <= start < stop <= 1, "attempt fraction range")
        depth = int(attempt["depth"])
        require(0 <= depth <= maximum_allowed_depth, "attempt depth")
        require(stop - start == Fraction(1, 2**depth), "dyadic attempt width")
        attempts[key] = attempt
    require((Fraction(0), Fraction(1)) in attempts, "root attempt")

    leaf_keys = {
        tuple(map(Fraction, subcell["cell_fraction"]))
        for subcell in logical_row["subcells"]
    }
    passed_keys = {key for key, attempt in attempts.items() if attempt["passed"]}
    require(leaf_keys == passed_keys, "successful attempts equal certified leaves")
    for (start, stop), attempt in attempts.items():
        midpoint = (start + stop) / 2
        children = ((start, midpoint), (midpoint, stop))
        if attempt["passed"]:
            require(not any(child in attempts for child in children), "passed cell not split")
        else:
            require(attempt["depth"] < maximum_allowed_depth, "failed terminal cell")
            require(all(child in attempts for child in children), "failed cell bisected")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--guides", required=True)
    parser.add_argument("--metadata", required=True)
    args = parser.parse_args()

    packet_path = Path(args.packet).resolve()
    baseline_cell_path = Path(args.baseline_root).resolve() / BASELINE_CELL_RELATIVE
    source_path = Path(args.source).resolve()
    guides_path = Path(args.guides).resolve()
    metadata_path = Path(args.metadata).resolve()
    packet = json.loads(packet_path.read_text(encoding="ascii"))
    metadata = json.loads(metadata_path.read_text(encoding="ascii"))
    checks = {}

    checks["schema_and_tier"] = (
        packet["schema"]
        == "mtt.preprojection.q79-eta9-b89-adaptive-boundary-taylor-krawczyk.v1"
        and packet["tier"]
        == "CERTIFIED_RECURSIVE_DYADIC_COMPLETE_BOUNDARY_TUBES_AND_GUIDE_ISOTOPY"
    )
    checks["all_builder_checks_true_and_no_failures"] = (
        all(packet["checks"].values()) and not packet["failures"]
    )
    checks["source_and_guides_are_hash_bound"] = (
        packet["source_sha256"] == sha256(source_path)
        and packet["guide_payload_sha256"] == sha256(guides_path)
        and packet["guide_metadata_sha256"] == sha256(metadata_path)
        and metadata["payload"]["sha256"] == sha256(guides_path)
        and packet["edge"] == int(metadata["edge"])
    )
    policy = packet["recursive_dyadic_policy"]
    checks["worker_implementations_are_hash_bound"] = (
        policy["worker_sha256"] == sha256(WORKER)
        and policy["cell_certifier_sha256"] == sha256(CELL_WORKER)
        and policy["only_failed_cells_are_bisected"] is True
        and policy["every_leaf_has_an_independent_boundary_cell_certificate"] is True
    )
    checks["numerical_policy_is_selected_policy"] = (
        packet["precision_bits"] == 512
        and packet["predictor_degree"] == 12
        and packet["taylor_order"] == 14
        and packet["separation_max_depth"] == 24
    )

    start_interval, stop_interval = packet["interval_range"]
    requested_start, requested_stop = packet["requested_interval_range"]
    rows = packet["logical_rows"]
    checkpoint = packet["checkpoint"]
    require(requested_start == start_interval, "checkpoint start")
    require(stop_interval <= requested_stop, "checkpoint stop bound")
    require(stop_interval == start_interval + len(rows), "checkpoint prefix length")
    require(checkpoint["certified_interval_count"] == len(rows), "checkpoint count")
    require(checkpoint["next_interval"] == stop_interval, "checkpoint next interval")
    require(
        checkpoint["complete_requested_range"] == (stop_interval == requested_stop),
        "checkpoint completion flag",
    )
    require(checkpoint["atomic_replace"] is True, "atomic checkpoint policy")
    require(len(rows) == stop_interval - start_interval, "logical row count")
    require(len(packet["attempts"]) == len(rows), "attempt row count")
    previous_tubes = None
    total_subcells = 0
    failed_attempts = 0
    for offset, (row, attempt_entry) in enumerate(
        zip(rows, packet["attempts"], strict=True)
    ):
        require(row["interval"] == start_interval + offset, "logical interval order")
        subcells = row["subcells"]
        require(subcells and row["subdivision_count"] == len(subcells), "subcell count")
        fractions = [tuple(map(Fraction, cell["cell_fraction"])) for cell in subcells]
        require(fractions[0][0] == 0 and fractions[-1][1] == 1, "subcell endpoints")
        require(
            all(left[1] == right[0] for left, right in zip(fractions, fractions[1:])),
            "gap-free subcell partition",
        )
        require(
            all(
                fraction.denominator & (fraction.denominator - 1) == 0
                for pair in fractions
                for fraction in pair
            ),
            "dyadic fractions",
        )
        for index, subcell in enumerate(subcells):
            require(
                subcell["certified_branches"] == CARRIER_SIZE,
                "complete boundary subcell carrier",
            )
            require(len(subcell["tubes"]) == CARRIER_SIZE, "complete boundary tube list")
            require(
                {int(tube["branch"]) for tube in subcell["tubes"]}
                == set(range(CARRIER_SIZE)),
                "complete boundary tube labels",
            )
            require(subcell["separation"]["certified_pairs"] == PAIR_COUNT, "source pairs")
            require(
                subcell["guide_homotopy"]["certified_pairs"] == PAIR_COUNT,
                "guide pairs",
            )
            direct = subcell["direct_homotopy_certificate"]
            require(direct["wrapper_sha256"] == sha256(CELL_WORKER), "cell wrapper hash")
            require(
                direct["baseline_cell_worker_sha256"] == sha256(baseline_cell_path),
                "baseline boundary worker hash",
            )
            require(direct["certified_cell_calls"] == 1, "one boundary cell call")
            require(direct["direct_max_parameter_depth"] == 8, "direct depth policy")
            require(
                direct["direct_affine_segment_pairs"] >= 0,
                "direct affine pair count",
            )
            require(
                direct["direct_parameter_intervals"] >= 0,
                "direct parameter interval count",
            )
            if direct["direct_affine_segment_pairs"]:
                require(
                    direct["minimum_direct_alignment_margin"] > 0,
                    "strict direct alignment margin",
                )
            expected_binding = (
                independent_binding(subcells[index - 1]["tubes"], subcell["tubes"])
                if index
                else None
            )
            require(
                subcell["binding_from_previous_subcell"] == expected_binding,
                "subcell endpoint binding",
            )
        expected_interval_binding = (
            independent_binding(previous_tubes, subcells[0]["tubes"])
            if previous_tubes is not None
            else None
        )
        require(
            row["binding_from_previous_interval"] == expected_interval_binding,
            "interval endpoint binding",
        )
        previous_tubes = subcells[-1]["tubes"]
        require(
            row["separation"]["certified_pairs"] == PAIR_COUNT * len(subcells),
            "aggregate source pairs",
        )
        require(
            row["guide_homotopy"]["certified_pairs"] == PAIR_COUNT * len(subcells),
            "aggregate guide pairs",
        )
        require(
            row["minimum_Krawczyk_margin"]
            == min(cell["minimum_Krawczyk_margin"] for cell in subcells),
            "aggregate Krawczyk margin",
        )
        require(
            row["separation"]["minimum_modulus_lower"]
            == minimum_optional(
                cell["separation"]["minimum_modulus_lower"] for cell in subcells
            ),
            "aggregate separation margin",
        )
        require(
            row["guide_homotopy"]["minimum_Rouche_margin"]
            == minimum_optional(
                cell["guide_homotopy"]["minimum_Rouche_margin"]
                for cell in subcells
            ),
            "aggregate guide margin",
        )
        verify_attempt_tree(row, attempt_entry, int(policy["maximum_depth"]))
        failed_attempts += sum(
            not attempt["passed"] for attempt in attempt_entry["attempts"]
        )
        total_subcells += len(subcells)

    counts = packet["counts"]
    checks["all_logical_rows_and_endpoint_bindings_replay"] = True
    checks["recursive_attempt_forest_is_complete"] = True
    checks["declared_range_is_exact_atomic_checkpoint_prefix"] = True
    checks["declared_counts_replay"] = (
        counts["logical_intervals"] == len(rows)
        and counts["certified_subcells"] == total_subcells
        and counts["certified_boundary_tubes"] == total_subcells * CARRIER_SIZE
        and counts["same_parameter_pair_certificates"] == total_subcells * PAIR_COUNT
        and counts["guide_homotopy_pair_certificates"] == total_subcells * PAIR_COUNT
        and counts["adaptively_subdivided_intervals"]
        == sum(len(row["subcells"]) > 1 for row in rows)
        and counts["failed_parent_attempts"] == failed_attempts
    )
    checks["nonpromotion_guardrails_are_explicit"] = (
        packet["guardrails"]["a_failed_coarse_cell_is_not_called_a_singularity"]
        and packet["guardrails"]["a_process_success_is_not_called_a_theorem"]
        and packet["guardrails"]["a_partial_checkpoint_is_not_called_complete_coverage"]
        and not packet["guardrails"][
            "claims_the_complete_boundary_or_mixed_carrier_is_certified_here"
        ]
        and not packet["guardrails"]["claims_Deligne_beta_C_U_eta9_or_HYM"]
    )
    require(all(checks.values()), "independent adaptive verification")
    result = {
        "packet": str(packet_path),
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_passed": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
