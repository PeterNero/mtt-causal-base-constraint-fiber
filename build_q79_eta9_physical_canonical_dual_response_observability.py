#!/usr/bin/env python3
"""Build CBF.T73, the physical canonical-dual response composition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from flint import arb


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_physical_canonical_dual_response_observability.source.json"
OUTPUT = ROOT / "q79_eta9_physical_canonical_dual_response_observability.packet.json"
INPUTS = {
    "CBF_T72": ROOT / "q79_eta9_physical_midpoint_three_evaluation_frame.packet.json",
    "CBF_characteristic_zero_member": ROOT / "q79_eta9_framed_member_char0_algebraization.input.json",
    "H4_T133_fiber_evaluation_geometry": ROOT / "q79_eta9_bht_fiber_evaluation_and_handle_sweep.input.json",
    "H4_T134_basis_audit": ROOT / "q79_eta9_h4_bht_augmented_transport_contract.input.json",
    "H4_T145_canonical_dual": ROOT / "q79_eta9_h4_canonical_dual_compensator_contract.input.json",
    "H4_T146_intrinsic_Rauch": ROOT / "q79_eta9_h4_intrinsic_rauch_bilinear_contract.input.json",
    "H4_T147_finite_trace": ROOT / "q79_eta9_h4_normalized_ramification_trace_contract.input.json",
    "H4_T159_three_branch_panels": ROOT / "q79_eta9_h4_physical_three_evaluation_complete_branch_panels.input.json",
    "H4_T155_edge2_branch_panel": ROOT / "q79_eta9_selected_member_edge2_complete_branch_panel.input.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify_canonical(packet: dict[str, Any], label: str) -> None:
    claimed = packet.get("canonical_payload_sha256")
    require(isinstance(claimed, str), f"{label} canonical digest")
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_sha256(unsigned) == claimed, f"{label} canonical payload")


def require_checks(packet: dict[str, Any], label: str) -> None:
    checks = packet.get("checks")
    require(isinstance(checks, dict) and checks, f"{label} checks")
    require(all(checks.values()), f"{label} checks pass")


def rows_by_segment(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["segment"]): row for row in rows}


def positive_ball(value: str) -> bool:
    ball = arb(value)
    return not ball.contains(0) and ball.lower() > 0


def main() -> int:
    source = load(SOURCE)
    require(
        source["schema"]
        == "mtt.cbf.q79-eta9-physical-canonical-dual-response-observability-source.v1",
        "source schema",
    )
    packets = {name: load(path) for name, path in INPUTS.items()}
    for name, packet in packets.items():
        if "canonical_payload_sha256" in packet:
            verify_canonical(packet, name)

    t72 = packets["CBF_T72"]
    char0 = packets["CBF_characteristic_zero_member"]
    fiber_geometry = packets["H4_T133_fiber_evaluation_geometry"]
    t134 = packets["H4_T134_basis_audit"]
    t145 = packets["H4_T145_canonical_dual"]
    t146 = packets["H4_T146_intrinsic_Rauch"]
    t147 = packets["H4_T147_finite_trace"]
    t159 = packets["H4_T159_three_branch_panels"]
    t155 = packets["H4_T155_edge2_branch_panel"]

    require(t72["theorem_id"] == "CBF.T72" and t72["all_checks_pass"], "CBF.T72")
    for packet, theorem_id, label in (
        (t134, "H4-T134", "H4-T134"),
        (t145, "H4-T145", "H4-T145"),
        (t146, "H4-T146", "H4-T146"),
        (t147, "H4-T147", "H4-T147"),
        (t159, "H4-T159", "H4-T159"),
    ):
        require(packet["theorem_id"] == theorem_id, f"{label} theorem id")
        require_checks(packet, label)
    require(t155["id"] == "H4-T155" and t155["all_passed"], "H4-T155")
    require_checks(char0, "characteristic-zero member")
    require_checks(fiber_geometry, "fiber evaluation geometry")

    segments = source["physical_rows"]["segments"]
    require(segments == ["edge-0", "edge-1", "edge-2"], "selected segment order")
    require(t72["physical_frame"]["segments"] == segments, "T72 segment alignment")
    require(t72["physical_frame"]["midpoint_parameter"] == "1/2", "T72 midpoint")
    require(
        t159["physical_evaluation_rows"] == [f"{segment}@1/2" for segment in segments],
        "T159 physical row alignment",
    )

    t134_rows = rows_by_segment(t134["midpoint_backend_audit"]["rows"])
    t145_rows = rows_by_segment(t145["construction"]["rows"])
    t72_pivots = t72["physical_frame"]["fiber_relation_pivots_zero_based"]
    pivot_rows: dict[str, int] = {}
    determinants: dict[str, str] = {}
    for segment in segments:
        require(segment in t134_rows and segment in t145_rows, f"{segment} H4 row")
        require(t134_rows[segment]["segment_parameter"] == 0.5, f"{segment} T134 midpoint")
        pivot = int(t134_rows[segment]["fiber_relation_pivot_zero_based"])
        require(pivot == int(t72_pivots[segment]), f"{segment} relation-pivot alignment")
        pivot_rows[segment] = pivot
        bilinear = t145_rows[segment]
        require(
            bilinear["arrays"]["canonical_bilinear"]["shape"] == [82, 82],
            f"{segment} canonical bilinear shape",
        )
        require(positive_ball(bilinear["determinant_abs_lower"]), f"{segment} B_e invertible")
        determinants[segment] = bilinear["determinant_abs_lower"]

    expected_halfwidth = source["physical_rows"]["operator_panel_halfwidth"]
    for segment in ("edge-0", "edge-1"):
        row = t159["newly_certified_segments"][segment]
        require(row["panel"]["segment_parameter_halfwidth"] == expected_halfwidth, f"{segment} panel width")
        require(row["certificate"]["total_branches"] == 252, f"{segment} branch count")
        require(row["certificate"]["certified_pairwise_disjointness_relations"] == 31626, f"{segment} branch separation")
    require(t159["imported_edge_2_predecessor"]["theorem_id"] == "H4-T155", "edge-2 predecessor")
    require(t72["checks"]["the_edge2_rank_panel_lies_inside_the_H4_T155_complete_branch_panel"], "edge-2 panel containment")

    geometry = source["surface_geometry"]
    cohomology = fiber_geometry["cohomology_dimensions"]
    derivation = cohomology["derivation"]
    require(char0["geometry"]["smooth"] and char0["geometry"]["finite_flat"], "smooth characteristic-zero member")
    require("K3 x E" in char0["global_construction"]["member"], "K3 family binding")
    require(int(geometry["eta"]) == int(derivation["eta"]) == 9, "eta=9")
    require(int(geometry["H_square"]) == int(derivation["H_square"]) == 2, "H square")
    curve_square = int(geometry["eta"]) ** 2 * int(geometry["H_square"])
    genus = 1 + curve_square // 2
    riemann_roch_sections = 2 + curve_square // 2
    require(curve_square == int(derivation["etaH_square"]) == 162, "curve square")
    require(genus == cohomology["fiber_genus"] == 82, "adjunction genus")
    require(riemann_roch_sections == cohomology["K3_eta9_sections"] == 83, "K3 Riemann-Roch")

    hypotheses = source["adjunction_hypotheses"]
    require(hypotheses["canonical_bundle_is_trivial"], "K3 canonical bundle")
    require(hypotheses["h0_structure_sheaf"] == 1, "connected K3")
    require(hypotheses["h1_structure_sheaf"] == 0, "K3 irregularity")
    require(hypotheses["divisors_are_smooth_at_the_selected_midpoints"], "smooth midpoint divisors")
    quotient_rank = riemann_roch_sections - hypotheses["h0_structure_sheaf"]
    require(quotient_rank == cohomology["fiber_holomorphic_rows"] == 82, "adjunction quotient rank")

    coefficient_rank = int(t72["characteristic_zero_rank"]["joined_evaluation_image_rank"])
    affine_rank = int(t72["characteristic_zero_rank"]["affine_graph_tangent_rank"])
    radial_kernel = int(t72["characteristic_zero_rank"]["radial_kernel_rank"])
    projective_kernel = int(t72["characteristic_zero_rank"]["projective_kernel_rank"])
    response_codomain_rank = len(segments) * quotient_rank
    canonical_postmap_rank = response_codomain_rank
    response_rank = coefficient_rank
    require((affine_rank, radial_kernel, coefficient_rank, projective_kernel) == (123, 1, 122, 0), "T72 rank ledger")
    require(canonical_postmap_rank == 246 and response_rank == 122, "composed rank ledger")

    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-physical-canonical-dual-response-observability.v1",
        "theorem_id": "CBF.T73",
        "status": "CLOSED_EXACT_PHYSICAL_MIDPOINT_CANONICAL_DUAL_RESPONSE_PROJECTIVE_RANK122",
        "tier": "EXACT_K3_ADJUNCTION_COMPOSITION_WITH_CHARACTERISTIC_ZERO_ARB_NONDEGENERACY",
        "inputs": {name: binding(path) for name, path in INPUTS.items()} | {"source_snapshot": binding(SOURCE)},
        "same_source_alignment": {
            "segments": segments,
            "midpoint_parameter": "1/2",
            "fiber_relation_pivots_zero_based": pivot_rows,
            "canonical_bilinear_determinant_absolute_lowers": determinants,
            "complete_branch_carriers": {
                "edge-0": "H4-T159 on |s-1/2|<=2^-32",
                "edge-1": "H4-T159 on |s-1/2|<=2^-32",
                "edge-2": "H4-T155 on |s-1/2|<=2^-8, containing the T72 box",
            },
            "T134_role": "coordinate-chart identity audit only; its binary64 basis residual is not an exact premise",
        },
        "adjunction": {
            "exact_sequence": "0 -> O_S --F_e--> O_S(9H) -> K_Ce -> 0",
            "surjectivity_reason": "K_S=O_S and H1(S,O_S)=0",
            "kernel": "H0(S,O_S) F_e=<F_e>",
            "H_square": int(geometry["H_square"]),
            "curve_square": curve_square,
            "fiber_genus": genus,
            "H0_O9H_rank": riemann_roch_sections,
            "quotient_rank": quotient_rank,
            "conclusion": "A_e: H0(S,O_S(9H))/<F_e> is isomorphic to H0(C_e,K_Ce)",
        },
        "canonical_response_operator": {
            "formula": "D=(direct_sum_e B_e^flat A_e) R",
            "coefficient_evaluation_codomain_rank": response_codomain_rank,
            "canonical_postmap_rank": canonical_postmap_rank,
            "affine_graph_tangent_rank": affine_rank,
            "radial_kernel_rank": radial_kernel,
            "coefficient_evaluation_image_rank": coefficient_rank,
            "canonical_response_image_rank": response_rank,
            "projective_response_kernel_rank": projective_kernel,
            "rank_identity": "ker(D)=ker(R) and rank(D)=rank(R) because direct_sum_e(B_e^flat A_e) is an isomorphism",
        },
        "intrinsic_provenance": {
            "H4_T146": "B has an intrinsic Cech/Serre ramification-residue formula, certified at the selected origin",
            "H4_T147": "the same formula has a root-label-independent finite-etale trace and directed derivative rule at the selected origin",
            "proof_role_here": "provenance and next-step guidance; midpoint rank uses H4-T145 nondegeneracy, not an unproved pathwide intrinsic-trace identification",
        },
        "checks": {
            "all_three_T72_rows_are_the_same_H4_midpoint_rows": True,
            "all_three_82_coordinate_quotient_charts_have_matching_relation_pivots": True,
            "all_three_selected_midpoint_canonical_bilinears_are_certifiably_invertible": True,
            "all_three_rows_have_complete_positive_width_selected_source_branch_carriers": True,
            "K3_adjunction_identifies_each_83_mod_1_coefficient_quotient_with_H0_KC": True,
            "the_direct_sum_canonical_postmap_is_an_isomorphism_of_rank246": True,
            "the_composed_midpoint_response_has_exact_projective_rank122_and_kernel0": True,
            "no_binary64_basis_residual_is_used_as_an_exact_rank_premise": True,
            "no_observed_value_or_fit_parameter_is_used": True,
        },
        "frontier_delta": {
            "closed": [
                "exact K3-adjunction promotion of the three T72 quotient rows to holomorphic differential spaces",
                "exact canonical-dual response image rank122 at the three physical midpoints",
                "same-row branch-carrier support for all three midpoint evaluations",
            ],
            "not_closed": [
                "an explicit canonical-bilinear nondegeneracy certificate over the full T72 product panel",
                "the divisor-to-Picard or Abel-Jacobi derivative",
                "six-segment Gauss-Manin transport and the 248-row BHT accumulation",
                "integral period reduction, beta_C, U_eta9 or a HYM endpoint",
            ],
            "next_required_object": "Promote the H4-T145 canonical bilinear from midpoint balls to the three T159/T155 parameter panels using the H4-T147 finite-trace derivative rule; then compose that panel map with T72 before global transport.",
        },
        "guardrails": {
            "claims_the_canonical_response_is_the_global_Abel_Jacobi_derivative": False,
            "claims_the_canonical_bilinear_is_certified_on_the_full_2^-32_panels": False,
            "claims_rank164_Gauss_Manin_or_248_row_BHT_execution": False,
            "claims_beta_C_U_eta9_HYM_SM_or_QG_closure": False,
        },
        "parameter_ledger": {
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "observed_values_used": 0,
        },
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    with OUTPUT.open("w", encoding="ascii", newline="\n") as stream:
        stream.write(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    print(
        "CBF.T73 canonical-dual response: PASS "
        f"quotient={quotient_rank} postmap={canonical_postmap_rank} response_rank={response_rank}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
