"""Canonical machine-independent verifier for this repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    run(sys.executable, "build_constraint_compression_leakage.py")
    run(sys.executable, "verify_constraint_compression_leakage.py")
    run(sys.executable, "build_repair_fixedpoint_gauge_descent.py")
    run(sys.executable, "verify_repair_fixedpoint_gauge_descent.py")
    run(sys.executable, "build_cohesive_repair_compression_transfer_comparison.py")
    run(sys.executable, "verify_cohesive_repair_compression_transfer_comparison.py")
    run(sys.executable, "build_selected_finite_weyl_koszul_hodge_and_interaction_cutset.py")
    run(sys.executable, "verify_selected_finite_weyl_koszul_hodge_and_interaction_cutset.py")
    run(sys.executable, "build_q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.py")
    run(sys.executable, "verify_q79_weyl_koszul_monodromy_c4_cohomology_intertwiner.py")
    run(sys.executable, "build_q79_symmetric_weyl_calculus_isometric_retraction.py")
    run(sys.executable, "verify_q79_symmetric_weyl_calculus_isometric_retraction.py")
    run(sys.executable, "build_q79_signed_edge_first_jet_harmonic_ideal_quotient.py")
    run(sys.executable, "verify_q79_signed_edge_first_jet_harmonic_ideal_quotient.py")
    run(sys.executable, "build_q79_symmetric_response_retraction_transferred_m3.py")
    run(sys.executable, "verify_q79_symmetric_response_retraction_transferred_m3.py")
    run(sys.executable, "verify_q79_symmetric_response_transferred_m4.py")
    run(sys.executable, "build_q79_higher_transfer_jet_filtration_and_m5_feasibility.py")
    run(sys.executable, "verify_q79_higher_transfer_jet_filtration_and_m5_feasibility.py")
    run(sys.executable, "build_q79_all_arity_source_promotion.py")
    run(sys.executable, "verify_q79_all_arity_source_promotion.py")
    run(sys.executable, "build_q79_seven_row_endpoint_factorization.py")
    run(sys.executable, "verify_q79_seven_row_endpoint_factorization.py")
    run(sys.executable, "build_q79_bv4_associated_matter_externalization.py")
    run(sys.executable, "verify_q79_bv4_associated_matter_externalization.py")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    print("repository verification passed")


if __name__ == "__main__":
    main()
