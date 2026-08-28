from __future__ import annotations

import unittest

import build_q79_seven_row_endpoint_factorization as factorization


class SevenRowEndpointFactorizationTests(unittest.TestCase):
    def test_three_packets_cover_all_seven_rows(self) -> None:
        rows = factorization.factorization_rows()
        self.assertEqual([row["row"] for row in rows], [f"EP.0{i}" for i in range(1, 8)])
        self.assertEqual(
            {source for row in rows for source in row["source_packets"]},
            {"GAS", "SYN", "BV4"},
        )

    def test_operator_and_symmetry_rows_are_derived(self) -> None:
        rows = {row["row"]: row for row in factorization.factorization_rows()}
        self.assertEqual(rows["EP.04"]["logical_role"], "deterministic_consequence")
        self.assertEqual(rows["EP.05"]["logical_role"], "deterministic_execution")

    def test_exact_feshbach_and_C4_witness(self) -> None:
        data, checks = factorization.feshbach_witness()
        self.assertTrue(all(checks.values()))
        self.assertEqual(data["effective_feshbach_operator"], [["9/5", 0], [0, "9/5"]])
        self.assertFalse(data["physical_q79_rank102_values_claimed"])

    def test_all_three_packet_types_are_independent(self) -> None:
        data, checks = factorization.independence_witnesses()
        self.assertTrue(all(checks.values()))
        self.assertIn("GAS_independence", data)
        self.assertIn("SYN_independence", data)
        self.assertIn("BV4_independence", data)

    def test_physical_acceptance_is_not_promoted(self) -> None:
        packet = factorization.build_packet()
        self.assertEqual(packet["physical_rows_accepted"], 0)
        self.assertEqual(packet["physical_rows_total"], 7)
        self.assertFalse(packet["frontier_delta"]["blocker_states_changed"])
        self.assertTrue(packet["frontier_delta"]["dependency_graph_changed"])


if __name__ == "__main__":
    unittest.main()
