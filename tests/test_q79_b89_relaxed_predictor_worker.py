import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "q79_b89_relaxed_predictor_source_isotopy_worker.py"
SPEC = importlib.util.spec_from_file_location("q79_b89_relaxed_predictor_worker", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RelaxedPredictorPolicyTests(unittest.TestCase):
    def test_threshold_matches_binary64_input_floor(self):
        self.assertEqual(MODULE.PREDICTOR_REFINEMENT_BITS, 52)
        self.assertEqual(MODULE.PREDICTOR_REFINEMENT_ITERATIONS, 30)

    def test_new_worker_is_versioned_without_mutating_old_worker(self):
        self.assertNotEqual(
            MODULE_PATH.name,
            "q79_b89_accelerated_source_isotopy_worker.py",
        )
        self.assertTrue(
            (ROOT / "q79_b89_accelerated_source_isotopy_worker.py").is_file()
        )


if __name__ == "__main__":
    unittest.main()
