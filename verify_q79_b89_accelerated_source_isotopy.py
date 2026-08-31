#!/usr/bin/env python3
"""Independently verify the committed T53 acceleration evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_b89_accelerated_source_isotopy_source_lock.json"
PACKET_PATH = ROOT / "q79_b89_accelerated_source_isotopy_equivalence.packet.json"


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


def main() -> int:
    lock = load(LOCK_PATH)
    packet = load(PACKET_PATH)
    checks = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            raise AssertionError(message)
        checks.append(message)

    check(
        lock["schema"]
        == "mtt.cbf.q79-b89-accelerated-source-isotopy-source-lock.v1",
        "source lock schema",
    )
    check(
        packet["schema"]
        == "mtt.cbf.q79-b89-accelerated-source-isotopy-equivalence.v1",
        "packet schema",
    )
    check(packet["theorem_id"] == "CBF.T53A", "theorem id")
    check(packet["source_lock_file_sha256"] == digest_file(LOCK_PATH), "lock file hash")
    check(packet["source_lock_sha256"] == digest_json(lock), "canonical lock hash")
    check(lock["worker_sha256"] == digest_file(ROOT / lock["worker"]), "worker hash")
    check(len(lock["benchmarks"]) == 2, "two benchmarks")
    check({row["edge"] for row in lock["benchmarks"]} == {0, 1}, "distinct edges")

    pair_count = 252 * 251 // 2
    for frozen in lock["benchmarks"]:
        path = ROOT / frozen["accelerated_packet"]
        benchmark = load(path)
        row = benchmark["rows"][0]
        source = row["separation"]["sweep_certificate"]
        guide = row["guide_homotopy"]["sweep_certificate"]
        check(digest_file(path) == frozen["accelerated_packet_sha256"], f"{frozen['name']} packet hash")
        check(
            digest_json(exact_root_projection(row))
            == frozen["upstream_exact_root_projection_sha256"]
            == frozen["accelerated_exact_root_projection_sha256"],
            f"{frozen['name']} exact root projection",
        )
        check(all(benchmark["checks"].values()) and not benchmark["failures"], f"{frozen['name']} scientific checks")
        check(row["certified_branches"] == 252, f"{frozen['name']} branches")
        check(row["separation"]["certified_pairs"] == pair_count, f"{frozen['name']} source pair count")
        check(row["guide_homotopy"]["certified_pairs"] == pair_count, f"{frozen['name']} guide pair count")
        check(
            source["real_order_pairs"]
            + source["imag_order_pairs"]
            + source["polynomial_candidate_pairs"]
            == pair_count,
            f"{frozen['name']} source partition",
        )
        check(
            guide["real_order_pairs"]
            + guide["imag_order_pairs"]
            + guide["exact_Arb_coarse_candidate_pairs"]
            + guide["direct_polynomial_candidate_pairs"]
            == pair_count,
            f"{frozen['name']} guide partition",
        )
        check(row["separation"]["minimum_modulus_lower"] > 0, f"{frozen['name']} source lower bound")
        check(row["guide_homotopy"]["minimum_Rouche_margin"] > 0, f"{frozen['name']} guide lower bound")
        check(
            benchmark["accelerated_pair_certificate"]["wrapper_sha256"]
            == lock["worker_sha256"],
            f"{frozen['name']} wrapper binding",
        )
        check(
            benchmark["accelerated_pair_certificate"]["baseline_certifier_sha256"]
            == lock["baseline_certifier_sha256"],
            f"{frozen['name']} baseline binding",
        )

    check(all(packet["checks"].values()), "packet checks")
    check(packet["check_summary"]["all_passed"], "packet summary")
    check(not any(packet["boundary"].values()), "claim boundary")
    print(json.dumps({"passed": len(checks), "all_passed": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
