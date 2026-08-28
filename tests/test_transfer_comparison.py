"""Regression tests for the compression/transfer comparison."""

from __future__ import annotations

import unittest

import build_cohesive_repair_compression_transfer_comparison as comparison


class TransferComparisonTests(unittest.TestCase):
    def test_cohesive_witness_has_no_retained_fixed_tangent_mode(self) -> None:
        witness, checks = comparison.build_cohesive_witness()
        self.assertTrue(all(checks.values()))
        self.assertEqual(witness["canonical_retained_rank"], 0)

    def test_nil_homotopy_recovers_data_raw_projection_misses(self) -> None:
        witness, checks = comparison.build_nil_hodge_witness()
        self.assertTrue(all(checks.values()))
        self.assertEqual(witness["witness"]["raw_Q_excursion"], "0")
        self.assertEqual(witness["witness"]["transferred_m3"], "ac")

    def test_feshbach_uses_resolvent_not_bare_complement(self) -> None:
        witness, checks = comparison.build_feshbach_witness()
        self.assertTrue(all(checks.values()))
        self.assertNotEqual(witness["raw_Q_excursion"], witness["feshbach_self_energy"])

    def test_complete_packet_has_no_physical_promotion(self) -> None:
        packet = comparison.build_packet()
        self.assertTrue(packet["summary"]["all_passed"])
        self.assertFalse(packet["selected_mtt_physics"])
        self.assertEqual(packet["continuous_fit_parameters"], 0)


if __name__ == "__main__":
    unittest.main()
