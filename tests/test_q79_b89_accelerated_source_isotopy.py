import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from flint import acb, arb

from q79_b89_accelerated_source_isotopy_worker import (
    certify_interval_guide_homotopy_sweep,
    certify_interval_separation_sweep,
)


ROOT = Path(__file__).resolve().parents[1]


def _tube(branch, real, imag, error="0.01"):
    box = acb(arb(real, "0.02"), arb(imag, "0.02"))
    return {
        "branch": branch,
        "x_box": box,
        "predictor_x_box": box,
        "guide_error_upper": arb(error).upper(),
        "predictor_x": [acb(real, imag)],
        "guide_x": [acb(real, imag)],
        "x_residual_radius": 0.0,
    }


class Q79B89AcceleratedSourceIsotopyTests(unittest.TestCase):
    def test_source_sweep_partitions_every_pair_without_fallback(self):
        tubes = [
            _tube(0, "0", "0"),
            _tube(1, "1", "0"),
            _tube(2, "0", "1"),
        ]
        baseline = SimpleNamespace(
            certify_polynomial_difference=lambda *_args: (_ for _ in ()).throw(
                AssertionError("fallback should not run")
            )
        )
        result = certify_interval_separation_sweep(tubes, 0, 1, baseline)
        self.assertEqual(result["certified_pairs"], 3)
        self.assertEqual(result["coarse_pairs"], 3)
        self.assertEqual(result["refined_pair_count"], 0)
        self.assertTrue(result["sweep_certificate"]["pair_partition_complete"])

    def test_guide_sweep_uses_expanded_boxes_and_partitions_every_pair(self):
        tubes = [
            _tube(0, "0", "0"),
            _tube(1, "1", "0"),
            _tube(2, "0", "1"),
        ]
        baseline = SimpleNamespace(
            certify_predictor_guide_pair_homotopy=lambda *_args: (_ for _ in ()).throw(
                AssertionError("fallback should not run")
            )
        )
        result = certify_interval_guide_homotopy_sweep(tubes, 0, 1, baseline)
        self.assertEqual(result["certified_pairs"], 3)
        self.assertEqual(result["coarse_pairs"], 3)
        self.assertEqual(result["direct_polynomial_pairs"], 0)
        self.assertTrue(result["sweep_certificate"]["pair_partition_complete"])

    def test_hash_locked_two_edge_equivalence_packet_passes(self):
        packet = json.loads(
            (ROOT / "q79_b89_accelerated_source_isotopy_equivalence.packet.json").read_text(
                encoding="ascii"
            )
        )
        self.assertTrue(packet["check_summary"]["all_passed"])
        self.assertEqual(packet["check_summary"]["passed"], 5)
        self.assertEqual({row["edge"] for row in packet["benchmarks"]}, {0, 1})

    def test_independent_equivalence_verifier_passes(self):
        result = subprocess.run(
            [sys.executable, "verify_q79_b89_accelerated_source_isotopy.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"passed": 35', result.stdout)

    def test_campaign_covers_every_missing_branch_interval(self):
        campaign = json.loads(
            (ROOT / "q79_b89_accelerated_source_isotopy_campaign.json").read_text(
                encoding="ascii"
            )
        )
        self.assertEqual(len(campaign["jobs"]), 77)
        self.assertEqual(len(campaign["boundary_repair_jobs"]), 4)
        self.assertEqual(campaign["preexisting_certified_coverage"]["intervals"], 375)
        self.assertEqual(campaign["queued_coverage"]["intervals"], 1820)
        self.assertEqual(
            campaign["preexisting_certified_coverage"]["intervals"]
            + campaign["queued_coverage"]["intervals"],
            campaign["total_target"]["intervals"],
        )


if __name__ == "__main__":
    unittest.main()
