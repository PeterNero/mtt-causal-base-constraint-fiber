from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import q79_b89_accelerated_source_isotopy_finalize as finalizer


class FlexibleFinalizerTests(unittest.TestCase):
    def test_packet_carrier_is_schema_derived(self):
        self.assertEqual(
            finalizer.packet_carrier(
                "mtt.preprojection.q79-eta9-b89-adaptive-family-taylor-krawczyk.v1"
            ),
            "branch",
        )
        self.assertEqual(
            finalizer.packet_carrier(
                "mtt.preprojection.q79-eta9-b89-adaptive-boundary-taylor-krawczyk.v1"
            ),
            "boundary",
        )

    def test_atomic_checkpoint_prefix_is_the_accepted_range(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packet_path = root / "pilot.json"
            packet = {
                "schema": "mtt.preprojection.q79-eta9-b89-adaptive-family-taylor-krawczyk.v1",
                "source_sha256": "source",
                "edge": 1,
                "interval_range": [336, 337],
                "requested_interval_range": [336, 360],
                "branch_range": [0, 252],
                "checkpoint": {
                    "complete_requested_range": False,
                    "certified_interval_count": 1,
                    "next_interval": 337,
                    "atomic_replace": True,
                },
                "logical_rows": [{"interval": 336}],
                "checks": {"certified": True},
                "failures": [],
            }
            packet_path.write_text(
                json.dumps(packet, sort_keys=True) + "\n", encoding="ascii"
            )
            digest = hashlib.sha256(packet_path.read_bytes()).hexdigest()
            carrier, job = finalizer.validated_result_job(
                {
                    "id": "pilot",
                    "packet_path": "pilot.json",
                    "packet_sha256": digest,
                    "independent_verification": {
                        "passed": True,
                        "packet_sha256": digest,
                        "verifier": "python verify_pilot.py",
                    },
                },
                root,
                {"branch": "source", "boundary": "unused"},
            )
            self.assertEqual(carrier, "branch")
            self.assertEqual(job["interval_range"], [336, 337])
            self.assertFalse(job["checkpoint_complete"])

    def test_coverage_reports_gap_ranges(self):
        jobs = [
            {"id": "a", "edge": 0, "interval_range": [0, 100]},
            {"id": "b", "edge": 0, "interval_range": [101, 231]},
        ]
        report = finalizer.coverage_report(jobs, "branch")
        self.assertFalse(report["complete"])
        self.assertEqual(report["missing_ranges"]["0"], [[100, 101]])
        self.assertEqual(report["missing_ranges"]["1"], [[0, 857]])

    def test_coverage_rejects_overlap(self):
        jobs = [
            {"id": "a", "edge": 2, "interval_range": [10, 20]},
            {"id": "b", "edge": 2, "interval_range": [19, 21]},
        ]
        with self.assertRaisesRegex(AssertionError, "overlap"):
            finalizer.coverage_report(jobs, "boundary")


if __name__ == "__main__":
    unittest.main()
