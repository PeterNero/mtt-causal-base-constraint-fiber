#!/usr/bin/env python3
"""Versioned adaptive B89 worker using the certified relaxed-seed cell worker."""

from __future__ import annotations

from pathlib import Path

import q79_b89_accelerated_adaptive_source_isotopy_worker as adaptive


HERE = Path(__file__).resolve().parent


def main() -> int:
    adaptive.CELL_CERTIFIER = HERE / "q79_b89_relaxed_predictor_source_isotopy_worker.py"
    adaptive.__file__ = __file__
    return adaptive.main()


if __name__ == "__main__":
    raise SystemExit(main())
