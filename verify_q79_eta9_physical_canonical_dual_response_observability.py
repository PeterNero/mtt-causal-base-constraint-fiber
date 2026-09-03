#!/usr/bin/env python3
"""Independently verify CBF.T73 and its exact rank-transfer premises."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from flint import arb


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_eta9_physical_canonical_dual_response_observability.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def verify_packet_digest(packet: dict[str, Any], label: str) -> None:
    claimed = packet.get("canonical_payload_sha256")
    require(isinstance(claimed, str), f"{label} canonical digest exists")
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_digest(unsigned) == claimed, f"{label} canonical digest")


def resolve(record: dict[str, Any]) -> Path:
    path = ROOT / record["path"]
    require(path.is_file(), f"bound file exists: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"bound byte count: {path}")
    require(digest(path) == record["sha256"], f"bound digest: {path}")
    return path


def checked(packet: dict[str, Any], label: str) -> None:
    checks = packet.get("checks")
    require(isinstance(checks, dict) and checks and all(checks.values()), f"{label} checks")


def main() -> int:
    packet = load(PACKET)
    require(
        packet["schema"]
        == "mtt.cbf.q79-eta9-physical-canonical-dual-response-observability.v1",
        "packet schema",
    )
    require(packet["theorem_id"] == "CBF.T73", "theorem id")
    verify_packet_digest(packet, "CBF.T73")
    inputs = {name: load(resolve(record)) for name, record in packet["inputs"].items()}
    source = inputs.pop("source_snapshot")
    require(
        source["schema"]
        == "mtt.cbf.q79-eta9-physical-canonical-dual-response-observability-source.v1",
        "source schema",
    )
    require(
        source["source_repositories"]["CBF_predecessor_commit"]
        == "e79cdcbd9c74dbbf3994a424e2d8a5b93fa4ae8c",
        "CBF predecessor commit",
    )
    require(
        source["source_repositories"]["H4_dependency_commit"]
        == "db711e73328a2e80b3d9054fdd756aefd53febbc",
        "H4 dependency commit",
    )
    for name, upstream in inputs.items():
        if "canonical_payload_sha256" in upstream:
            verify_packet_digest(upstream, name)

    t72 = inputs["CBF_T72"]
    char0 = inputs["CBF_characteristic_zero_member"]
    fiber = inputs["H4_T133_fiber_evaluation_geometry"]
    t134 = inputs["H4_T134_basis_audit"]
    t145 = inputs["H4_T145_canonical_dual"]
    t146 = inputs["H4_T146_intrinsic_Rauch"]
    t147 = inputs["H4_T147_finite_trace"]
    t159 = inputs["H4_T159_three_branch_panels"]
    t155 = inputs["H4_T155_edge2_branch_panel"]
    require(t72["theorem_id"] == "CBF.T72" and t72["all_checks_pass"], "CBF.T72")
    for upstream, theorem_id in (
        (t134, "H4-T134"),
        (t145, "H4-T145"),
        (t146, "H4-T146"),
        (t147, "H4-T147"),
        (t159, "H4-T159"),
    ):
        require(upstream["theorem_id"] == theorem_id, f"{theorem_id} id")
        checked(upstream, theorem_id)
    require(t155["id"] == "H4-T155" and t155["all_passed"], "H4-T155")
    checked(char0, "characteristic-zero member")
    checked(fiber, "fiber geometry")

    segments = ["edge-0", "edge-1", "edge-2"]
    require(source["physical_rows"]["segments"] == segments, "source rows")
    require(t72["physical_frame"]["segments"] == segments, "T72 rows")
    require(t159["physical_evaluation_rows"] == [f"{segment}@1/2" for segment in segments], "T159 rows")
    t134_rows = {row["segment"]: row for row in t134["midpoint_backend_audit"]["rows"]}
    t145_rows = {row["segment"]: row for row in t145["construction"]["rows"]}
    t72_pivots = t72["physical_frame"]["fiber_relation_pivots_zero_based"]
    replayed_pivots: dict[str, int] = {}
    for segment in segments:
        require(t134_rows[segment]["segment_parameter"] == 0.5, f"{segment} midpoint")
        pivot = int(t134_rows[segment]["fiber_relation_pivot_zero_based"])
        require(pivot == int(t72_pivots[segment]), f"{segment} quotient chart")
        replayed_pivots[segment] = pivot
        row = t145_rows[segment]
        require(row["arrays"]["canonical_bilinear"]["shape"] == [82, 82], f"{segment} B shape")
        determinant = arb(row["determinant_abs_lower"])
        require(not determinant.contains(0) and determinant.lower() > 0, f"{segment} B invertible")
    require(
        replayed_pivots == packet["same_source_alignment"]["fiber_relation_pivots_zero_based"],
        "recorded quotient pivots",
    )

    halfwidth = source["physical_rows"]["operator_panel_halfwidth"]
    for segment in ("edge-0", "edge-1"):
        panel = t159["newly_certified_segments"][segment]
        require(panel["panel"]["segment_parameter_halfwidth"] == halfwidth, f"{segment} width")
        require(panel["certificate"]["total_branches"] == 252, f"{segment} complete carrier")
        require(panel["certificate"]["certified_pairwise_disjointness_relations"] == 31626, f"{segment} disjointness")
    require(t159["imported_edge_2_predecessor"]["theorem_id"] == "H4-T155", "T159 edge-2 link")
    require(t72["checks"]["the_edge2_rank_panel_lies_inside_the_H4_T155_complete_branch_panel"], "edge-2 containment")

    geometry = source["surface_geometry"]
    cohomology = fiber["cohomology_dimensions"]
    hypotheses = source["adjunction_hypotheses"]
    require(char0["geometry"]["smooth"] and char0["geometry"]["finite_flat"], "smooth family")
    require(hypotheses["canonical_bundle_is_trivial"] and hypotheses["h1_structure_sheaf"] == 0, "K3 adjunction hypotheses")
    curve_square = int(geometry["eta"]) ** 2 * int(geometry["H_square"])
    genus = 1 + curve_square // 2
    section_rank = 2 + curve_square // 2
    quotient_rank = section_rank - int(hypotheses["h0_structure_sheaf"])
    require((curve_square, genus, section_rank, quotient_rank) == (162, 82, 83, 82), "adjunction arithmetic")
    require(
        (cohomology["K3_eta9_sections"], cohomology["fiber_genus"], cohomology["fiber_holomorphic_rows"])
        == (83, 82, 82),
        "upstream cohomology dimensions",
    )
    adjunction = packet["adjunction"]
    require(
        (adjunction["curve_square"], adjunction["fiber_genus"], adjunction["H0_O9H_rank"], adjunction["quotient_rank"])
        == (162, 82, 83, 82),
        "packet adjunction dimensions",
    )

    rank = t72["characteristic_zero_rank"]
    require(
        (
            rank["affine_graph_tangent_rank"],
            rank["radial_kernel_rank"],
            rank["joined_evaluation_image_rank"],
            rank["projective_kernel_rank"],
        )
        == (123, 1, 122, 0),
        "T72 exact rank ledger",
    )
    response = packet["canonical_response_operator"]
    require(response["coefficient_evaluation_codomain_rank"] == 3 * quotient_rank == 246, "response codomain")
    require(response["canonical_postmap_rank"] == 246, "block isomorphism rank")
    require(response["canonical_response_image_rank"] == rank["joined_evaluation_image_rank"] == 122, "response image rank")
    require(response["projective_response_kernel_rank"] == rank["projective_kernel_rank"] == 0, "response kernel")

    require(t146["construction"]["ramification_points"] == 198, "intrinsic residue count")
    require(t147["checks"]["the_trace_definition_is_invariant_under_idempotent_permutation"], "root-free trace provenance")
    require(not any(packet["guardrails"].values()), "claim boundary")
    require(all(packet["checks"].values()), "declared checks")
    require(packet["parameter_ledger"] == {
        "new_continuous_fit_parameters": 0,
        "new_discrete_fit_parameters": 0,
        "observed_values_used": 0,
    }, "parameter ledger")
    print("CBF.T73 verification: PASS adjunction=82x3 postmap=246 response_rank=122")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
