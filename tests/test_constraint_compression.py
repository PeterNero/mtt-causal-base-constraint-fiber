from fractions import Fraction
import unittest

import build_constraint_compression_leakage as proof
import build_repair_fixedpoint_gauge_descent as repair


class CompressionLeakageTests(unittest.TestCase):
    def test_exact_witness_passes(self) -> None:
        objects = proof.build_exact_objects()
        self.assertTrue(all(objects["checks"].values()))

    def test_witness_is_nontrivial(self) -> None:
        objects = proof.build_exact_objects()
        self.assertNotEqual(objects["commutator"], proof.zero(3, 3))
        self.assertEqual(proof.matrix_rank(objects["commutator"]), 2)

    def test_exact_norm_certificate(self) -> None:
        objects = proof.build_exact_objects()
        lhs = proof.mul(proof.transpose(objects["commutator"]), objects["commutator"])
        rhs = proof.scale(Fraction(1, 27), objects["P"])
        self.assertEqual(lhs, rhs)

    def test_repair_gauge_witness_passes(self) -> None:
        objects = repair.build_exact_objects()
        self.assertTrue(all(objects["checks"].values()))

    def test_repair_gauge_kernel_is_central_pair(self) -> None:
        objects = repair.build_exact_objects()
        identity = proof.identity(3)
        expected = {
            repair.matrix_key(identity),
            repair.matrix_key(proof.scale(Fraction(-1), identity)),
        }
        actual = {repair.matrix_key(g) for g in objects["conjugation_kernel"]}
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
