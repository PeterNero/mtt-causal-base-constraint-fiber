#!/usr/bin/env python3
"""Freeze two baseline-equivalence witnesses for the T53 sweep worker."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CAMPAIGN_RELATIVE = Path(
    "experiments/q79_eta9_b89_family_branch_braid_pilot/"
    "kernel_adaptive_taylor_family_campaign.json"
)
LOCK_PATH = ROOT / "q79_b89_accelerated_source_isotopy_source_lock.json"
PACKET_PATH = ROOT / "q79_b89_accelerated_source_isotopy_equivalence.packet.json"
BENCHMARKS = (
    {
        "name": "edge0_interval0",
        "edge": 0,
        "interval": 0,
        "job_start": 0,
        "job_stop": 24,
        "path": ROOT / "q79_b89_accelerated_source_isotopy_benchmark.packet.json",
    },
    {
        "name": "edge1_interval143",
        "edge": 1,
        "interval": 143,
        "job_start": 120,
        "job_stop": 144,
        "path": ROOT
        / "q79_b89_accelerated_source_isotopy_benchmark_edge1.packet.json",
    },
)


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_json(value) -> str:
    return digest_bytes(canonical(value))


def load(path: Path):
    return json.loads(path.read_text(encoding="ascii"))


def exact_root_projection(row: dict) -> dict:
    return {
        "interval": row["interval"],
        "cell_fraction": row["cell_fraction"],
        "certified_branches": row["certified_branches"],
        "minimum_Krawczyk_margin": row["minimum_Krawczyk_margin"],
        "binding_from_previous_interval": row["binding_from_previous_interval"],
        "tubes": row["tubes"],
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", required=True)
    args = parser.parse_args()
    upstream_root = Path(args.upstream_root).resolve()
    campaign_path = upstream_root / CAMPAIGN_RELATIVE
    campaign = load(campaign_path)

    rows = []
    for case in BENCHMARKS:
        job = next(
            row
            for row in campaign["jobs"]
            if row["edge"] == case["edge"]
            and row["interval_range"] == [case["job_start"], case["job_stop"]]
        )
        require(job.get("observed_state") == "succeeded", f"{case['name']} job")
        original_path = upstream_root / job["retrieved_path"]
        original = load(original_path)
        logical = next(
            row for row in original["logical_rows"] if row["interval"] == case["interval"]
        )
        require(logical["subdivision_count"] == 1, f"{case['name']} subdivision")
        original_row = logical["subcells"][0]
        accelerated = load(case["path"])
        accelerated_row = accelerated["rows"][0]

        exact_equal = exact_root_projection(original_row) == exact_root_projection(
            accelerated_row
        )
        pair_count = 252 * 251 // 2
        source_sweep = accelerated_row["separation"]["sweep_certificate"]
        guide_sweep = accelerated_row["guide_homotopy"]["sweep_certificate"]
        source_partition = (
            source_sweep["real_order_pairs"]
            + source_sweep["imag_order_pairs"]
            + source_sweep["polynomial_candidate_pairs"]
            == pair_count
        )
        guide_partition = (
            guide_sweep["real_order_pairs"]
            + guide_sweep["imag_order_pairs"]
            + guide_sweep["exact_Arb_coarse_candidate_pairs"]
            + guide_sweep["direct_polynomial_candidate_pairs"]
            == pair_count
        )
        original_seconds_per_interval = original["elapsed_seconds"] / (
            case["job_stop"] - case["job_start"]
        )
        accelerated_seconds = accelerated["elapsed_seconds"]
        checks = {
            "source_hash_matches": original["source_sha256"]
            == accelerated["source_sha256"],
            "guide_payload_hash_matches": original["guide_payload_sha256"]
            == accelerated["guide_payload_sha256"],
            "guide_metadata_hash_matches": original["guide_metadata_sha256"]
            == accelerated["guide_metadata_sha256"],
            "numerical_policy_matches": all(
                original[key] == accelerated[key]
                for key in (
                    "branch_range",
                    "precision_bits",
                    "predictor_degree",
                    "taylor_order",
                    "separation_max_depth",
                )
            ),
            "exact_root_projection_matches": exact_equal,
            "all_accelerated_scientific_checks_pass": all(
                accelerated["checks"].values()
            )
            and not accelerated["failures"],
            "source_sweep_is_a_complete_pair_partition": source_partition,
            "guide_sweep_is_a_complete_pair_partition": guide_partition,
            "both_sweep_lower_bounds_are_strictly_positive": accelerated_row[
                "separation"
            ]["minimum_modulus_lower"]
            > 0
            and accelerated_row["guide_homotopy"]["minimum_Rouche_margin"] > 0,
            "benchmark_is_faster_than_original_shard_mean": accelerated_seconds
            < original_seconds_per_interval,
        }
        require(all(checks.values()), f"{case['name']} equivalence")
        rows.append(
            {
                "name": case["name"],
                "edge": case["edge"],
                "interval": case["interval"],
                "accelerated_packet": case["path"].name,
                "accelerated_packet_sha256": digest_file(case["path"]),
                "upstream_packet": str(original_path.relative_to(upstream_root)).replace(
                    "\\", "/"
                ),
                "upstream_packet_sha256": digest_file(original_path),
                "upstream_exact_root_projection_sha256": digest_json(
                    exact_root_projection(original_row)
                ),
                "accelerated_exact_root_projection_sha256": digest_json(
                    exact_root_projection(accelerated_row)
                ),
                "original_seconds_per_interval": original_seconds_per_interval,
                "accelerated_seconds": accelerated_seconds,
                "speedup": original_seconds_per_interval / accelerated_seconds,
                "checks": checks,
            }
        )

    lock = {
        "schema": "mtt.cbf.q79-b89-accelerated-source-isotopy-source-lock.v1",
        "upstream_repository": "mtt-preprojection-repair-calculus",
        "upstream_campaign": str(CAMPAIGN_RELATIVE).replace("\\", "/"),
        "upstream_campaign_sha256": digest_file(campaign_path),
        "worker": "q79_b89_accelerated_source_isotopy_worker.py",
        "worker_sha256": digest_file(
            ROOT / "q79_b89_accelerated_source_isotopy_worker.py"
        ),
        "baseline_certifier_sha256": rows[0]["checks"][
            "numerical_policy_matches"
        ]
        and load(BENCHMARKS[0]["path"])["accelerated_pair_certificate"][
            "baseline_certifier_sha256"
        ],
        "benchmarks": rows,
    }
    packet_checks = {
        "two_distinct_edge_witnesses_are_frozen": len(rows) == 2
        and {row["edge"] for row in rows} == {0, 1},
        "both_witnesses_preserve_the_exact_root_tubes": all(
            row["checks"]["exact_root_projection_matches"] for row in rows
        ),
        "both_witnesses_partition_every_source_and_guide_pair": all(
            row["checks"]["source_sweep_is_a_complete_pair_partition"]
            and row["checks"]["guide_sweep_is_a_complete_pair_partition"]
            for row in rows
        ),
        "both_witnesses_have_strict_separation_margins": all(
            row["checks"]["both_sweep_lower_bounds_are_strictly_positive"]
            for row in rows
        ),
        "both_witnesses_reduce_wall_time": all(
            row["checks"]["benchmark_is_faster_than_original_shard_mean"]
            for row in rows
        ),
    }
    require(all(packet_checks.values()), "packet checks")
    packet = {
        "schema": "mtt.cbf.q79-b89-accelerated-source-isotopy-equivalence.v1",
        "theorem_id": "CBF.T53A",
        "tier": "ALGORITHM_EQUIVALENCE_ON_TWO_HASH_LOCKED_EXACT_SOURCE_CELLS",
        "source_lock_sha256": digest_json(lock),
        "benchmarks": rows,
        "checks": packet_checks,
        "check_summary": {
            "passed": sum(packet_checks.values()),
            "total": len(packet_checks),
            "all_passed": all(packet_checks.values()),
        },
        "boundary": {
            "claims_full_2195_interval_campaign": False,
            "claims_joint_source_isotopy": False,
            "claims_B89_Deligne_decision": False,
        },
    }
    LOCK_PATH.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="ascii")
    packet["source_lock_file_sha256"] = digest_file(LOCK_PATH)
    PACKET_PATH.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(packet["check_summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
