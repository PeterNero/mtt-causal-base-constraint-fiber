import importlib.util
import json
import tempfile
import time
import unittest
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "q79_b89_recursive_boundary_isotopy_worker.py"
SPEC = importlib.util.spec_from_file_location("recursive_boundary_isotopy", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

CELL_PATH = ROOT / "q79_b89_boundary_direct_homotopy_cell_worker.py"
CELL_SPEC = importlib.util.spec_from_file_location("boundary_direct_cell", CELL_PATH)
CELL_MODULE = importlib.util.module_from_spec(CELL_SPEC)
assert CELL_SPEC.loader is not None
CELL_SPEC.loader.exec_module(CELL_MODULE)


def box(real_center):
    return {
        "real": [str(real_center - 0.1), str(real_center + 0.1)],
        "imag": ["-0.1", "0.1"],
    }


def tube(label, left, right):
    return {
        "branch": label,
        "left_endpoint_x_box": box(left),
        "right_endpoint_x_box": box(right),
    }


def row(start, stop):
    return {
        "cell_fraction": [str(start), str(stop)],
        "certified_branches": MODULE.CARRIER_SIZE,
        "minimum_Krawczyk_margin": 0.5,
        "separation": {
            "certified_pairs": MODULE.PAIR_COUNT,
            "coarse_pairs": MODULE.PAIR_COUNT,
            "refined_pair_count": 0,
            "leaf_intervals": MODULE.PAIR_COUNT,
            "maximum_refinement_depth": 0,
            "minimum_modulus_lower": 0.25,
        },
        "guide_homotopy": {
            "certified_pairs": MODULE.PAIR_COUNT,
            "coarse_pairs": MODULE.PAIR_COUNT,
            "direct_polynomial_pairs": 0,
            "refined_pair_count": 0,
            "leaf_intervals": MODULE.PAIR_COUNT,
            "maximum_refinement_depth": 0,
            "minimum_Rouche_margin": 0.2,
        },
        "tubes": [
            tube(label, float(start) + label, float(stop) + label)
            for label in range(MODULE.CARRIER_SIZE)
        ],
    }


class Q79B89RecursiveBoundaryIsotopyTests(unittest.TestCase):
    def test_endpoint_binding_is_identity_and_complete(self):
        previous = [
            tube(label, label - 1, label) for label in range(MODULE.CARRIER_SIZE)
        ]
        current = [
            tube(label, label, label + 1) for label in range(MODULE.CARRIER_SIZE)
        ]
        binding = MODULE.endpoint_binding(previous, current)
        self.assertEqual(
            binding,
            {
                "bound_branches": MODULE.CARRIER_SIZE,
                "unique_label_matches": MODULE.CARRIER_SIZE,
                "identity_matching": True,
            },
        )

    def test_recursive_policy_bisects_only_failed_parent(self):
        args = SimpleNamespace(max_dyadic_depth=3)
        calls = []

        def runner(_args, _interval, start, stop, depth, _directory):
            calls.append((start, stop, depth))
            passed = stop - start <= Fraction(1, 2)
            diagnostic = {
                "cell_fraction": [str(start), str(stop)],
                "depth": depth,
                "passed": passed,
                "returncode": 0 if passed else 1,
            }
            return (row(start, stop) if passed else None), diagnostic

        with tempfile.TemporaryDirectory() as temporary:
            leaves, diagnostics, maximum_depth = MODULE.certify_interval(
                args, 17, Path(temporary), runner=runner
            )
        self.assertEqual(
            [leaf["cell_fraction"] for leaf in leaves],
            [["0", "1/2"], ["1/2", "1"]],
        )
        self.assertEqual(
            calls,
            [
                (Fraction(0), Fraction(1), 0),
                (Fraction(0), Fraction(1, 2), 1),
                (Fraction(1, 2), Fraction(1), 1),
            ],
        )
        self.assertEqual(len(diagnostics), 3)
        self.assertEqual(maximum_depth, 1)
        self.assertIsNone(leaves[0]["binding_from_previous_subcell"])
        self.assertTrue(
            leaves[1]["binding_from_previous_subcell"]["identity_matching"]
        )

    def test_aggregate_counts_every_leaf_certificate(self):
        left = row(Fraction(0), Fraction(1, 2))
        right = row(Fraction(1, 2), Fraction(1))
        left["binding_from_previous_subcell"] = None
        right["binding_from_previous_subcell"] = MODULE.endpoint_binding(
            left["tubes"], right["tubes"]
        )
        aggregate = MODULE.aggregate_logical_row(5, [left, right], None, 1)
        self.assertEqual(aggregate["subdivision_count"], 2)
        self.assertEqual(
            aggregate["separation"]["certified_pairs"], 2 * MODULE.PAIR_COUNT
        )
        self.assertEqual(
            aggregate["guide_homotopy"]["certified_pairs"],
            2 * MODULE.PAIR_COUNT,
        )
        self.assertEqual(aggregate["maximum_dyadic_depth"], 1)

    def test_atomic_checkpoint_declares_only_certified_prefix(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.json"
            guides = directory / "guides.npz"
            metadata_path = directory / "guides.json"
            source.write_text("{}\n", encoding="ascii")
            guides.write_bytes(b"guide")
            metadata_path.write_text("{}\n", encoding="ascii")
            args = SimpleNamespace(
                baseline_root=str(directory),
                interval_start=10,
                interval_stop=12,
                precision=512,
                predictor_degree=12,
                taylor_order=14,
                separation_max_depth=24,
                max_dyadic_depth=7,
            )
            logical = row(Fraction(0), Fraction(1))
            logical["interval"] = 10
            logical["subdivision_count"] = 1
            logical["maximum_dyadic_depth"] = 0
            logical["binding_from_previous_interval"] = None
            logical["subcells"] = [row(Fraction(0), Fraction(1))]
            attempts = [
                {
                    "interval": 10,
                    "attempts": [
                        {
                            "cell_fraction": ["0", "1"],
                            "depth": 0,
                            "passed": True,
                            "returncode": 0,
                        }
                    ],
                }
            ]
            packet = MODULE.build_checkpoint_packet(
                args,
                {"edge": 2},
                source,
                guides,
                metadata_path,
                [logical],
                attempts,
                time.monotonic(),
            )
            self.assertEqual(packet["interval_range"], [10, 11])
            self.assertEqual(packet["requested_interval_range"], [10, 12])
            self.assertFalse(packet["checkpoint"]["complete_requested_range"])
            output = directory / "checkpoint.json"
            MODULE.write_checkpoint(output, packet)
            self.assertEqual(
                json.loads(output.read_text(encoding="ascii"))["checkpoint"]
                ["next_interval"],
                11,
            )

    def test_direct_homotopy_fallback_certifies_safe_segment(self):
        class PolynomialModule:
            @staticmethod
            def dyadic_parameter_ball(left, right):
                center = (left + right) / 2
                radius = (right - left) / 2
                return CELL_MODULE.arb(
                    f"{center.numerator}/{center.denominator}",
                    f"{radius.numerator}/{radius.denominator}",
                )

            @staticmethod
            def evaluate_univariate_polynomial(coefficients, parameter):
                result = 0
                for coefficient in reversed(coefficients):
                    result = result * parameter + coefficient
                return result

        result = CELL_MODULE.direct_homotopy_exclusion(
            PolynomialModule,
            [CELL_MODULE.acb(1)],
            [CELL_MODULE.acb(0, 1)],
            max_parameter_depth=6,
        )
        self.assertIsNotNone(result)
        self.assertGreater(result["minimum_alignment_margin"], 0)

    def test_direct_homotopy_fallback_rejects_crossing_segment(self):
        class PolynomialModule:
            @staticmethod
            def dyadic_parameter_ball(left, right):
                center = (left + right) / 2
                radius = (right - left) / 2
                return CELL_MODULE.arb(
                    f"{center.numerator}/{center.denominator}",
                    f"{radius.numerator}/{radius.denominator}",
                )

            @staticmethod
            def evaluate_univariate_polynomial(coefficients, parameter):
                result = 0
                for coefficient in reversed(coefficients):
                    result = result * parameter + coefficient
                return result

        result = CELL_MODULE.direct_homotopy_exclusion(
            PolynomialModule,
            [CELL_MODULE.acb(1)],
            [CELL_MODULE.acb(-1)],
            max_parameter_depth=4,
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
