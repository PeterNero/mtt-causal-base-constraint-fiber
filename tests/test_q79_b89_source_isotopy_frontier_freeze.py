import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "verify_q79_b89_source_isotopy_frontier_freeze.py"
SPEC = importlib.util.spec_from_file_location("q79_b89_source_isotopy_frontier_freeze", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class NewlinePortableSourceLockTests(unittest.TestCase):
    def test_lf_and_crlf_are_the_same_frozen_text(self):
        lf = b'{"exact":true}\n{"count":2195}\n'
        crlf = lf.replace(b"\n", b"\r\n")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            path.write_bytes(lf)
            expected = hashlib.sha256(crlf).hexdigest()
            self.assertTrue(MODULE.newline_portable_sha256_matches(path, expected))

    def test_content_change_is_rejected(self):
        original = b'{"count":2195}\r\n'
        changed = b'{"count":2194}\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            path.write_bytes(changed)
            expected = hashlib.sha256(original).hexdigest()
            self.assertFalse(MODULE.newline_portable_sha256_matches(path, expected))

    def test_lone_carriage_return_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            path.write_bytes(b'{"count":2195}\r')
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertFalse(MODULE.newline_portable_sha256_matches(path, expected))


class CampaignIntervalTests(unittest.TestCase):
    def test_replacement_job_is_not_part_of_original_interval_union(self):
        campaign = MODULE.load("q79_b89_recursive_replacement_campaign.json")
        original = [
            row for row in campaign["jobs"] if "replacement_of_job_id" not in row
        ]
        branch, overlap = MODULE.interval_union(original, "branch")
        self.assertFalse(overlap)
        self.assertEqual(sum(map(len, branch.values())), 1817)

    def test_replacement_is_exact_uncertified_remainder(self):
        campaign = MODULE.load("q79_b89_recursive_replacement_campaign.json")
        jobs = {row["id"]: row for row in campaign["jobs"]}
        replacements = [
            row for row in campaign["jobs"] if "replacement_of_job_id" in row
        ]
        self.assertEqual(len(replacements), 1)
        replacement = replacements[0]
        predecessor = jobs[replacement["replacement_of_job_id"]]
        self.assertEqual(
            replacement["predecessor_certified_atomic_prefix"],
            [predecessor["interval_start"], replacement["interval_start"]],
        )
        self.assertEqual(replacement["interval_stop"], predecessor["interval_stop"])

if __name__ == "__main__":
    unittest.main()
