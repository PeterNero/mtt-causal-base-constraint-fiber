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


if __name__ == "__main__":
    unittest.main()
