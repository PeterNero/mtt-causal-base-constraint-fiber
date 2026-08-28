from fractions import Fraction
import unittest

import build_constraint_compression_leakage as proof


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


if __name__ == "__main__":
    unittest.main()
