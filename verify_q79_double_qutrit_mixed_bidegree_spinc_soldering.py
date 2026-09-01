"""Independently verify the CBF.T61 mixed-bidegree packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_double_qutrit_mixed_bidegree_spinc_soldering.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mm(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def dagger(a: list[list[complex]]) -> list[list[complex]]:
    return [[a[j][i].conjugate() for j in range(len(a))] for i in range(len(a[0]))]


def kron(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[a[i][j] * b[p][q] for j in range(len(a[0])) for q in range(len(b[0]))] for i in range(len(a)) for p in range(len(b))]


def same(a: list[list[complex]], b: list[list[complex]]) -> bool:
    return a == b


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    j = [[0j, -1 + 0j], [1 + 0j, 0j]]
    identity4 = [[complex(int(i == k)) for k in range(4)] for i in range(4)]
    mixed = kron(j, j)
    direct = [
        [0j, -1 + 0j, 0j, 0j],
        [1 + 0j, 0j, 0j, 0j],
        [0j, 0j, 0j, -1 + 0j],
        [0j, 0j, 1 + 0j, 0j],
    ]
    phi = [
        [0j, -1 + 0j, 0j, 0j],
        [1 + 0j, 0j, 0j, 0j],
        [0j, 0j, 0j, -1 + 0j],
        [0j, 0j, 1 + 0j, 0j],
    ]
    conjugation = [
        [0j, 0j, 0j, 1 + 0j],
        [0j, 0j, -1 + 0j, 0j],
        [0j, -1 + 0j, 0j, 0j],
        [1 + 0j, 0j, 0j, 0j],
    ]
    n = [
        [0j, -1 + 0j, 1 + 0j, 0j],
        [1 + 0j, 0j, 0j, -1 + 0j],
        [1j, 0j, 0j, 1j],
        [0j, -1 + 0j, -1 + 0j, 0j],
    ]
    d = [
        [1 + 0j, 0j, 0j, 0j],
        [0j, -1 + 0j, 0j, 0j],
        [0j, 0j, 1 + 0j, 0j],
        [0j, 0j, 0j, -1 + 0j],
    ]
    n_pol = [
        [1 + 0j, 1j, 0j, 0j],
        [0j, 0j, 1 + 0j, 1j],
        [1 + 0j, -1j, 0j, 0j],
        [0j, 0j, 1 + 0j, -1j],
    ]
    d_pol = [
        [1j, 0j, 0j, 0j],
        [0j, 1j, 0j, 0j],
        [0j, 0j, -1j, 0j],
        [0j, 0j, 0j, -1j],
    ]
    minus_i4 = [[-value for value in row] for row in identity4]
    two_i4 = [[2 * value for value in row] for row in identity4]

    source_rows = packet["source_provenance"]["source_checks"]
    checks = {
        "schema": packet["schema"] == "boe.mtt.q79-double-qutrit-mixed-bidegree-spinc-soldering.v1",
        "claim": packet["claim_id"] == "CBF.T61",
        "source_count": len(source_rows) == 6,
        "source_hashes": all(sha256(ROOT / row["path"]) == row["expected_sha256"] for row in source_rows),
        "direct_square": same(mm(direct, direct), minus_i4),
        "mixed_square": same(mm(mixed, mixed), identity4),
        "square_cutset": mm(direct, direct) != mm(mixed, mixed),
        "polarized_unitary": same(mm(n_pol, dagger(n_pol)), two_i4),
        "polarized_equivariance": same(mm(n_pol, direct), mm(d_pol, n_pol)),
        "polarized_same_degree": packet["direct_holomorphic_polarization"]["uses_original_exterior_degree"],
        "polarized_local_selected": packet["direct_holomorphic_polarization"]["chartwise_map_selected_by_vertical_internal_labels_and_eta9_orientation"],
        "polarized_global_open": not packet["direct_holomorphic_polarization"]["global_connection_compatible_map_selected"],
        "phi_unitary": same(mm(phi, dagger(phi)), identity4),
        "phi_equivariance": same(mm(phi, mixed), mm(conjugation, phi)),
        "conjugation_square": same(mm(conjugation, conjugation), identity4),
        "pauli_unitary": same(mm(n, dagger(n)), two_i4),
        "pauli_equivariance": same(mm(n, mixed), mm(d, n)),
        "one_plus_three": packet["result"]["finite_trace_decomposition_ranks"] == [1, 3],
        "determinant_twist": packet["global_bundle_criterion"]["globally_typed_mixed_bundle"] == "M=Hom(U_i,U_v) tensor D_i, D_i=det(U_i)",
        "determinant_scalar": "D_i" in packet["global_bundle_criterion"]["scalar_line"],
        "twisted_soldering": packet["spinc_adjoint_soldering_criterion"]["required_map"].startswith("kappa:D_i tensor End_0"),
        "h2_split": packet["mixed_bidegree_endomorphism"]["full_H2_ranks"] == [1, 4, 1],
        "central_sign_cancelled": packet["mixed_bidegree_endomorphism"]["central_sign_cancellation"] == "J^2 tensor J^2=(-I) tensor (-I)=+I",
        "direct_bridge_rejected": not packet["direct_degree_one_cutset"]["invertible_intertwiner_exists"],
        "C4_not_unique": not packet["global_bundle_criterion"]["C4_alone_selects_the_map"],
        "intertwiner_dimension": packet["global_bundle_criterion"]["C4_only_intertwiner_dimension_complex"] == 8,
        "parallel_s_open": not packet["global_bundle_criterion"]["global_parallel_matching_selected"],
        "physical_kappa_open": not packet["spinc_adjoint_soldering_criterion"]["selected_physical_kappa"],
        "chern_conditions": len(packet["spinc_adjoint_soldering_criterion"]["necessary_chern_conditions"]) == 3,
        "primary_route_preserves_degree": packet["corrected_augmented_bridge"]["primary_same_degree_route"]["preserves_original_degree"],
        "mixed_route_records_degree_issue": "totalization" in packet["corrected_augmented_bridge"]["secondary_mixed_spinc_route"]["degree_issue"],
        "mixed_route_records_line_map": packet["corrected_augmented_bridge"]["secondary_mixed_spinc_route"]["determinant_line_map"] == "d_alpha:D_i->L_alpha",
        "physical_residual_open": not packet["corrected_augmented_bridge"]["physical_residual_computed"],
        "B_HS_open": not packet["physical_boundary"]["B_HS_01_closed"],
        "B_GEO_open": not packet["physical_boundary"]["B_GEO_01_closed"],
        "B_OP_open": not packet["physical_boundary"]["B_OP_01_closed"],
        "rows_unchanged": packet["physical_boundary"]["physical_rows"] == {"accepted": 0, "total": 7},
        "zero_parameters": all(value == 0 for value in packet["parameter_ledger"].values()),
        "builder_checks": packet["check_summary"]["all_passed"],
        "theorem_hash": sha256(ROOT / "Q79DoubleQutritMixedBidegreeEndomorphismAndSpinCSolderingCriterionTheorem_v1.md") == packet["source_provenance"]["theorem_sha256"],
        "schema_hash": sha256(ROOT / "q79_double_qutrit_mixed_bidegree_spinc_soldering_contract.schema.json") == packet["source_provenance"]["schema_sha256"],
    }
    summary = {"checks": checks, "passed": sum(checks.values()), "total": len(checks), "all_passed": all(checks.values())}
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
