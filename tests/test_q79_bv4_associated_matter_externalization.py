"""Regression tests for the associated-matter BV4 compiler."""

from __future__ import annotations

import unittest

import build_q79_bv4_associated_matter_externalization as compiler


class AssociatedMatterBV4CompilerTests(unittest.TestCase):
    def test_exact_internal_index_witness(self) -> None:
        rows = compiler.sectors()
        data, checks, _ = compiler.internal_witness(compiler.h16_weights(rows))
        self.assertTrue(all(checks.values()))
        self.assertEqual(data["kernel_dimension"], 48)
        self.assertEqual(data["cokernel_dimension"], 0)
        self.assertEqual(data["characterwise_index"], "3[H16]")
        self.assertEqual(data["spectral_gap_mu"], 1)

    def test_product_dirac_and_pairing_reduction(self) -> None:
        rows = compiler.sectors()
        _, internal_checks, matrices = compiler.internal_witness(
            compiler.h16_weights(rows)
        )
        data, checks = compiler.product_witness(matrices)
        self.assertTrue(all(internal_checks.values()))
        self.assertTrue(all(checks.values()))
        self.assertEqual(data["product_dimension"], 160)
        self.assertEqual(data["retained_product_dimension"], 96)
        self.assertEqual(
            data["quadratic_sample"]["upper_bilinear"],
            data["quadratic_sample"]["reduced_bilinear"],
        )

    def test_representation_anomaly_and_z6_rows(self) -> None:
        data, checks = compiler.representation_witness(compiler.sectors())
        self.assertTrue(all(checks.values()))
        self.assertEqual(data["gauge_group"], "(SU3 x SU2 x U1Y)/Z6")
        self.assertTrue(
            all(row["z6_congruence"] == 0 for row in data["sectors"])
        )

    def test_packet_preserves_physical_boundary(self) -> None:
        packet = compiler.build_packet()
        self.assertTrue(all(packet["checks"].values()))
        self.assertEqual(packet["physical_packets_accepted"], 0)
        self.assertEqual(packet["physical_rows_accepted"], 0)
        self.assertFalse(packet["frontier_delta"]["blocker_states_changed"])
        self.assertTrue(packet["frontier_delta"]["BV4_dependency_graph_changed"])


if __name__ == "__main__":
    unittest.main()
