#!/usr/bin/env python3
"""Focused safety tests for durable B89 result ingestion."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "q79_b89_recursive_replacement_ingest.py"
SPEC = importlib.util.spec_from_file_location("recursive_replacement_ingest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RecursiveReplacementIngestTests(unittest.TestCase):
    def test_safe_member_accepts_nested_posix_path(self) -> None:
        self.assertEqual(
            MODULE.safe_member("outputs/packet.json").as_posix(),
            "outputs/packet.json",
        )

    def test_safe_member_rejects_absolute_and_parent_paths(self) -> None:
        for candidate in ("/packet.json", "../packet.json", "outputs/../../packet.json"):
            with self.subTest(candidate=candidate), self.assertRaises(AssertionError):
                MODULE.safe_member(candidate)

    def test_safe_member_rejects_windows_separator(self) -> None:
        with self.assertRaises(AssertionError):
            MODULE.safe_member(r"..\packet.json")

    def test_atomic_json_write_is_ascii_and_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            MODULE.write_json_atomic(path, {"value": 1})
            MODULE.write_json_atomic(path, {"value": 2})
            self.assertEqual(MODULE.load(path), {"value": 2})
            path.read_bytes().decode("ascii")


if __name__ == "__main__":
    unittest.main()
