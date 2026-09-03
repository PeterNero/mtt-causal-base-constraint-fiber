#!/usr/bin/env python3
"""Build CBF.T72, the physical characteristic-zero three-evaluation frame."""

from __future__ import annotations

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

from flint import acb, acb_mat, arb, ctx


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_physical_midpoint_three_evaluation_frame.source.json"
OUTPUT = ROOT / "q79_eta9_physical_midpoint_three_evaluation_frame.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def load_gzip(path: Path) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()).decode("ascii"))


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


def verify_declared_binding(row: dict[str, Any]) -> Path:
    path = ROOT / row["path"]
    require(path.is_file(), f"bound file: {path}")
    require(path.stat().st_size == row["bytes"], f"bound bytes: {path}")
    require(sha256(path) == row["sha256"], f"bound hash: {path}")
    return path


def parse_acb(value: str) -> acb:
    if value.endswith("j") and " + " in value:
        real, imaginary = value.removesuffix("j").rsplit(" + ", 1)
        return acb(arb(real), arb(imaginary))
    return acb(arb(value))


def matrix(rows: int, columns: int, entries: Sequence[str]) -> acb_mat:
    require(len(entries) == rows * columns, f"{rows}x{columns} entry count")
    return acb_mat(rows, columns, [parse_acb(value) for value in entries])


def rectangle() -> list[acb]:
    a = arb(432).root(3)
    margin = arb.pi() / 100
    left = -arb(1) / (2 * a) - margin
    right = margin
    bottom = -arb(3).sqrt() / (2 * a) - margin
    top = margin
    return [
        acb(left, bottom),
        acb(right, bottom),
        acb(right, top),
        acb(left, top),
        acb(left, bottom),
    ]


def lifted_point(q: acb) -> tuple[tuple[acb, acb, acb], acb]:
    x = 1 / q
    radicand = x**3 - 432
    y = -radicand.sqrt()
    slope = (y - 36) / (x - 12)
    big_x = slope * slope - x - 12
    big_y = slope * (x - big_x) - y
    return ((1 + big_y / 36) / 2, (1 - big_y / 36) / 2, -big_x / 12), radicand


def physical_edge_point(segment: str, parameter: arb) -> tuple[tuple[acb, acb, acb], acb]:
    require(segment.startswith("edge-"), f"edge segment: {segment}")
    edge = int(segment.removeprefix("edge-"))
    corners = rectangle()
    return lifted_point(corners[edge] + parameter * (corners[edge + 1] - corners[edge]))


def determinant3(rows: Sequence[Sequence[acb]]) -> acb:
    a, b, c = rows
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def graph_kernel(
    pivot_block: acb_mat,
    free_block: acb_mat,
    pivots: list[int],
    free: list[int],
) -> acb_mat:
    pivot_solution = pivot_block.solve(-free_block)
    pivot_map = {column: index for index, column in enumerate(pivots)}
    free_map = {column: index for index, column in enumerate(free)}
    return acb_mat(
        249,
        123,
        [
            pivot_solution[pivot_map[row], column]
            if row in pivot_map
            else acb(1 if free_map[row] == column else 0)
            for row in range(249)
            for column in range(123)
        ],
    )


def quotient_restriction(
    point: Sequence[acb],
    member: Sequence[acb],
    kernel: acb_mat,
    relation_pivot: int,
) -> tuple[acb_mat, arb]:
    relation = [
        sum((point[block] * member[83 * block + coordinate] for block in range(3)), acb(0))
        for coordinate in range(83)
    ]
    require(not relation[relation_pivot].contains(0), "fiber relation pivot")
    rows = []
    for coordinate in range(83):
        if coordinate == relation_pivot:
            continue
        ratio = relation[coordinate] / relation[relation_pivot]
        for ambient in range(249):
            block, fiber_coordinate = divmod(ambient, 83)
            value = acb(0)
            if fiber_coordinate == coordinate:
                value += point[block]
            if fiber_coordinate == relation_pivot:
                value -= point[block] * ratio
            rows.append(value)
    return acb_mat(82, 249, rows) * kernel, relation[relation_pivot].abs_lower()


def stack_restrictions(rows: Sequence[acb_mat]) -> acb_mat:
    return acb_mat(
        82 * len(rows),
        123,
        [value[row, column] for value in rows for row in range(82) for column in range(123)],
    )


def selected_square(
    stacked: acb_mat,
    output_rows: Sequence[int],
    gauge_columns: Sequence[int],
) -> acb_mat:
    return acb_mat(
        len(output_rows),
        len(gauge_columns),
        [stacked[row, column] for row in output_rows for column in gauge_columns],
    )


def midpoint_matrix(value: acb_mat) -> acb_mat:
    return acb_mat(
        value.nrows(),
        value.ncols(),
        [
            acb(value[row, column].real.mid(), value[row, column].imag.mid())
            for row in range(value.nrows())
            for column in range(value.ncols())
        ],
    )


def neumann_defect(preconditioner: acb_mat, value: acb_mat) -> arb:
    size = value.nrows()
    identity = acb_mat(
        size,
        size,
        [acb(1 if row == column else 0) for row in range(size) for column in range(size)],
    )
    defect = identity - preconditioner * value
    row_sums = [
        sum((defect[row, column].abs_upper() for column in range(size)), arb(0))
        for row in range(size)
    ]
    return max(row_sums)


def main() -> int:
    source = load(SOURCE)
    require(
        source["schema"] == "mtt.cbf.q79-eta9-physical-midpoint-three-evaluation-frame-source.v1",
        "source schema",
    )
    compiled_path = verify_declared_binding(source["compiled_characteristic_zero_operator"])
    upstream_paths = {
        name: verify_declared_binding(row) for name, row in source["upstream_packets"].items()
    }
    compiled = load_gzip(compiled_path)
    require(
        compiled["schema"] == "mtt.cbf.q79-eta9-physical-char0-graph-operator-input.v1",
        "compiled schema",
    )
    require(
        compiled["source_repositories"]["H4"]["commit"]
        == source["compiled_characteristic_zero_operator"]["H4_repository_commit"],
        "H4 commit",
    )
    require(
        compiled["source_repositories"]["UST"]["commit"]
        == source["compiled_characteristic_zero_operator"]["UST_repository_commit"],
        "UST commit",
    )
    ctx.prec = int(compiled["precision_bits"])

    char0 = load(upstream_paths["H4_char0_algebraization"])
    atlas = load(upstream_paths["H4_physical_midpoint_atlas"])
    edge2_panel = load(upstream_paths["H4_edge2_complete_branch_panel"])
    t71 = load(upstream_paths["CBF_T71"])
    require(char0["geometry"]["incidence_rank"] == 126, "upstream incidence rank")
    require(char0["geometry"]["projective_deformation_rank"] == 122, "upstream projective rank")
    require(char0["geometry"]["smooth"] and char0["geometry"]["finite_flat"], "char0 member geometry")
    require(atlas["theorem_id"] == "H4-T152" and all(atlas["checks"].values()), "H4-T152")
    require(edge2_panel["id"] == "H4-T155" and edge2_panel["all_passed"], "H4-T155")
    require(t71["theorem_id"] == "CBF.T71" and t71["all_checks_pass"], "CBF.T71")

    incidence = compiled["incidence"]
    require((incidence["rank"], incidence["ambient_columns"]) == (126, 249), "incidence dimensions")
    pivots = [int(value) for value in incidence["pivot_columns_zero_based"]]
    free = [int(value) for value in incidence["free_columns_zero_based"]]
    pivot_block = matrix(126, 126, incidence["selected_pivot_block_entries_row_major"])
    free_block = matrix(126, 123, incidence["selected_free_block_entries_row_major"])
    pivot_determinant = pivot_block.det()
    require(not pivot_determinant.contains(0), "rank-126 characteristic-zero incidence minor")
    kernel = graph_kernel(pivot_block, free_block, pivots, free)
    member = [parse_acb(value) for value in compiled["selected_member_coefficients"]]
    member_free = acb_mat(123, 1, [member[column] for column in free])
    member_reconstruction = kernel * member_free
    require(
        all((member_reconstruction[row, 0] - member[row]).contains(0) for row in range(249)),
        "radial member belongs to graph kernel",
    )

    selection = source["physical_row_selection"]
    segments = list(selection["segments_in_order"])
    require(segments == ["edge-0", "edge-1", "edge-2"], "deterministic physical triple")
    relation_pivots = [int(value) for value in selection["relation_pivots_zero_based"]]
    center_parameter = arb(1) / 2
    center_points = []
    midpoint_root_counts = {}
    midpoint_minimum_separations = {}
    for segment in segments:
        point, radicand = physical_edge_point(segment, center_parameter)
        require(not radicand.contains(0), f"center Weierstrass radicand {segment}")
        stored_packet = load(upstream_paths[f"H4_{segment.replace('-', '')}_midpoint"])
        stored_point = [parse_acb(value) for value in stored_packet["geometry"]["Fermat_point"]]
        compiled_point = [parse_acb(value) for value in compiled["physical_midpoint_rows"][segment]]
        require(
            all(value.overlaps(stored) and value.overlaps(exported) for value, stored, exported in zip(point, stored_point, compiled_point, strict=True)),
            f"physical point binding {segment}",
        )
        require(sum((value**3 for value in point), acb(0)).contains(0), f"Fermat equation {segment}")
        require(stored_packet["roots"]["count"] == 198 and all(stored_packet["checks"].values()), f"midpoint roots {segment}")
        center_points.append(point)
        midpoint_root_counts[segment] = stored_packet["roots"]["count"]
        midpoint_minimum_separations[segment] = stored_packet["roots"]["minimum_pair_separation_lower"]
    weight_determinant = determinant3(center_points)
    require(not weight_determinant.contains(0), "three physical weight rows are independent")

    center_restrictions = []
    center_relation_lowers = {}
    for segment, point, relation_pivot in zip(segments, center_points, relation_pivots, strict=True):
        restricted, lower = quotient_restriction(point, member, kernel, relation_pivot)
        center_restrictions.append(restricted)
        center_relation_lowers[segment] = str(lower)
    center_stacked = stack_restrictions(center_restrictions)
    certificate = source["rank_certificate"]
    drop = int(certificate["gauge_drop_free_coordinate_zero_based"])
    require(free[drop] == certificate["gauge_drop_ambient_coordinate_zero_based"], "gauge coordinate")
    gauge_columns = [column for column in range(123) if column != drop]
    output_rows = [int(value) for value in certificate["selected_output_rows_zero_based"]]
    require(len(output_rows) == len(set(output_rows)) == 122, "122 distinct output rows")
    center_square = selected_square(center_stacked, output_rows, gauge_columns)
    center_determinant = center_square.det()
    require(not center_determinant.contains(0), "physical rank-122 center minor")

    halfwidth = Fraction(selection["segment_parameter_halfwidth"])
    require(halfwidth > 0, "positive panel halfwidth")
    panel_parameter = arb(1) / 2 + arb(0, 1) * arb(halfwidth.numerator) / halfwidth.denominator
    panel_data = [physical_edge_point(segment, panel_parameter) for segment in segments]
    panel_points = [point for point, _radicand in panel_data]
    panel_radicand_lowers = {
        segment: str(radicand.abs_lower())
        for segment, (_point, radicand) in zip(segments, panel_data, strict=True)
    }
    require(
        all(not radicand.contains(0) for _point, radicand in panel_data),
        "selected Weierstrass lift remains analytic on every panel",
    )
    panel_weight_determinant = determinant3(panel_points)
    require(not panel_weight_determinant.contains(0), "panel weight independence")
    panel_restrictions = []
    panel_relation_lowers = {}
    for segment, point, relation_pivot in zip(segments, panel_points, relation_pivots, strict=True):
        restricted, lower = quotient_restriction(point, member, kernel, relation_pivot)
        panel_restrictions.append(restricted)
        panel_relation_lowers[segment] = str(lower)
    panel_square = selected_square(
        stack_restrictions(panel_restrictions), output_rows, gauge_columns
    )
    preconditioner = midpoint_matrix(center_square).inv()
    defect = neumann_defect(preconditioner, panel_square)
    require(defect < 1, "strict panel Neumann defect")

    radial_center_residual = center_stacked * member_free
    require(
        all(radial_center_residual[row, 0].contains(0) for row in range(radial_center_residual.nrows())),
        "radial line is killed by the center quotient",
    )
    checks = {
        "the_compiled_operator_is_bound_to_committed_H4_and_UST_sources": True,
        "the_characteristic_zero_incidence_pivot_has_rank126": True,
        "the_affine_graph_kernel_has_rank123_and_contains_the_radial_member": True,
        "the_three_rows_are_actual_edge0_edge1_edge2_physical_midpoints": True,
        "all_three_midpoint_ramification_algebras_are_degree198_and_squarefree": True,
        "the_three_physical_weight_rows_have_nonzero_characteristic_zero_determinant": True,
        "a_122_by_122_restricted_center_minor_excludes_zero": True,
        "the_only_possible_affine_blind_direction_is_the_exact_radial_member_line": True,
        "the_projective_characteristic_zero_image_rank_is_exactly122": True,
        "the_same_fixed_minor_is_invertible_on_three_positive_width_parameter_panels": True,
        "the_selected_negative_Weierstrass_lift_remains_analytic_on_all_three_panels": True,
        "the_edge2_rank_panel_lies_inside_the_H4_T155_complete_branch_panel": halfwidth <= Fraction(1, 256),
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"T72 checks: {checks}")
    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-physical-midpoint-three-evaluation-frame.v1",
        "theorem_id": "CBF.T72",
        "status": "CLOSED_CHARACTERISTIC_ZERO_PHYSICAL_THREE_EVALUATION_PROJECTIVE_RANK122_WITH_POSITIVE_WIDTH_OPERATOR_PANELS",
        "tier": "characteristic_zero_Arb_coefficient_evaluation_theorem_not_a_Picard_or_BHT_transport_result",
        "physical_frame": {
            "segments": segments,
            "selection_rule": selection["selection_rule"],
            "midpoint_parameter": selection["segment_parameter_center"],
            "midpoint_weight_determinant_absolute_lower": str(weight_determinant.abs_lower()),
            "midpoint_root_counts": midpoint_root_counts,
            "midpoint_minimum_pair_separations": midpoint_minimum_separations,
            "fiber_relation_pivots_zero_based": dict(zip(segments, relation_pivots, strict=True)),
            "fiber_relation_pivot_absolute_lowers": center_relation_lowers,
        },
        "characteristic_zero_rank": {
            "ambient_coefficient_rank": 249,
            "incidence_rank": 126,
            "affine_graph_tangent_rank": 123,
            "radial_kernel_rank": 1,
            "projective_graph_tangent_rank": 122,
            "joined_evaluation_image_rank": 122,
            "projective_kernel_rank": 0,
            "incidence_pivot_determinant_absolute_lower": str(pivot_determinant.abs_lower()),
            "restricted_minor_determinant_absolute_lower": str(center_determinant.abs_lower()),
            "gauge_drop_free_coordinate_zero_based": drop,
            "gauge_drop_ambient_coordinate_zero_based": free[drop],
            "selected_output_rows_zero_based": output_rows,
        },
        "positive_width_operator_panel": {
            "parameter_box_each_segment": f"|s-1/2| <= {selection['segment_parameter_halfwidth']}",
            "cartesian_product_of_three_independent_parameter_boxes": True,
            "weight_determinant_absolute_lower": str(panel_weight_determinant.abs_lower()),
            "fiber_relation_pivot_absolute_lowers": panel_relation_lowers,
            "Weierstrass_radicand_absolute_lowers": panel_radicand_lowers,
            "Neumann_infinity_norm_defect_upper": str(defect),
            "strictly_below_one": bool(defect < 1),
            "conclusion": "the fixed 122x122 restricted evaluation minor is invertible for every triple in the declared product panel",
        },
        "theorem": {
            "statement": "For the exact selected characteristic-zero G3AJ member, the coefficient-evaluation quotients at the physical edge-0, edge-1 and edge-2 midpoints jointly separate all 122 projective graph-preserving tangent directions. The same rank holds throughout the declared positive-width product of edge panels.",
            "proof_logic": "The imported exact incidence theorem gives affine tangent rank123. The radial member line is killed by every fiber quotient, so the image rank is at most122. A characteristic-zero Arb 122x122 minor excludes zero at the center, and a fixed midpoint preconditioner has interval infinity-norm defect below one on the product panel, proving rank at least122 there.",
        },
        "frontier_delta": {
            "closed": [
                "actual characteristic-zero physical realization of three independent evaluation rows",
                "exact projective graph-tangent image rank122 at the three selected B-loop midpoints",
                "positive-width rank stability of the same 122-row operator minor",
            ],
            "not_closed": [
                "complete 252-branch positive-width carriers on edge-0 and edge-1",
                "overlapping coverage of all six physical path segments",
                "rank-164 Gauss-Manin transport and 248-row BHT handle accumulation",
                "integral-period reduction, beta_C and U_eta9",
            ],
            "next_required_object": "Certify complete selected-source 252-branch panels around the edge-0 and edge-1 midpoint rows, then use overlapping path panels to transport the three 82-row evaluations through the rank-164 relative system.",
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
            "panel_width_is_a_conservative_proof_radius_not_a_physical_parameter": True,
        },
        "guardrails": {
            "claims_complete_edge0_or_edge1_branch_carrier": False,
            "claims_complete_six_segment_isotopy": False,
            "claims_Picard_Abel_Jacobi_or_normal_function_rank122": False,
            "claims_rank164_Gauss_Manin_transport_is_executed": False,
            "claims_248_row_BHT_handle_sweep_is_executed": False,
            "claims_beta_C_or_U_eta9_is_computed": False,
            "claims_HYM_SM_or_QG_endpoint_closure": False,
        },
        "inputs": {
            "source_snapshot": binding(SOURCE),
            "compiled_characteristic_zero_operator": binding(compiled_path),
            **{name: binding(path) for name, path in upstream_paths.items()},
        },
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T72 physical characteristic-zero evaluation frame: PASS "
        f"rank=122 panel_defect={float(defect):.6e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
