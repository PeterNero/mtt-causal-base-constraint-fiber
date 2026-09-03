#!/usr/bin/env python3
"""Independently replay the CBF.T72 characteristic-zero rank certificate."""

from __future__ import annotations

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

from flint import acb, acb_mat, arb, ctx


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_eta9_physical_midpoint_three_evaluation_frame.packet.json"


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


def bound_path(row: dict[str, Any]) -> Path:
    path = ROOT / row["path"]
    require(path.is_file(), f"bound input: {path}")
    require(path.stat().st_size == row["bytes"], f"bound bytes: {path}")
    require(sha256(path) == row["sha256"], f"bound hash: {path}")
    return path


def parse_acb(value: str) -> acb:
    if value.endswith("j") and " + " in value:
        real, imaginary = value.removesuffix("j").rsplit(" + ", 1)
        return acb(arb(real), arb(imaginary))
    return acb(arb(value))


def interval_matrix(rows: int, columns: int, entries: Sequence[str]) -> acb_mat:
    require(len(entries) == rows * columns, "matrix entry count")
    return acb_mat(rows, columns, [parse_acb(entry) for entry in entries])


def path_corners() -> list[acb]:
    scale = arb(432).root(3)
    margin = arb.pi() / 100
    left = -arb(1) / (2 * scale) - margin
    right = margin
    bottom = -arb(3).sqrt() / (2 * scale) - margin
    top = margin
    return [
        acb(left, bottom),
        acb(right, bottom),
        acb(right, top),
        acb(left, top),
        acb(left, bottom),
    ]


def path_point(edge: int, parameter: arb) -> tuple[tuple[acb, acb, acb], acb]:
    corners = path_corners()
    q = corners[edge] + parameter * (corners[edge + 1] - corners[edge])
    x = 1 / q
    radicand = x**3 - 432
    y = -radicand.sqrt()
    slope = (y - 36) / (x - 12)
    big_x = slope**2 - x - 12
    big_y = slope * (x - big_x) - y
    return ((1 + big_y / 36) / 2, (1 - big_y / 36) / 2, -big_x / 12), radicand


def det3(rows: Sequence[Sequence[acb]]) -> acb:
    a, b, c = rows
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def make_kernel(A: acb_mat, B: acb_mat, pivots: list[int], free: list[int]) -> acb_mat:
    solved = A.solve(-B)
    pivot_positions = {column: index for index, column in enumerate(pivots)}
    free_positions = {column: index for index, column in enumerate(free)}
    entries = []
    for ambient in range(249):
        for coordinate in range(123):
            if ambient in pivot_positions:
                entries.append(solved[pivot_positions[ambient], coordinate])
            else:
                entries.append(acb(1 if free_positions[ambient] == coordinate else 0))
    return acb_mat(249, 123, entries)


def restricted_map(
    point: Sequence[acb],
    member: Sequence[acb],
    kernel: acb_mat,
    pivot: int,
) -> acb_mat:
    relation = [
        sum((point[block] * member[83 * block + coordinate] for block in range(3)), acb(0))
        for coordinate in range(83)
    ]
    require(not relation[pivot].contains(0), "relation pivot")
    operator = []
    for coordinate in range(83):
        if coordinate == pivot:
            continue
        ratio = relation[coordinate] / relation[pivot]
        for ambient in range(249):
            block, fiber_coordinate = divmod(ambient, 83)
            entry = acb(0)
            if fiber_coordinate == coordinate:
                entry += point[block]
            if fiber_coordinate == pivot:
                entry -= point[block] * ratio
            operator.append(entry)
    return acb_mat(82, 249, operator) * kernel


def stacked(maps: Sequence[acb_mat]) -> acb_mat:
    return acb_mat(
        246,
        123,
        [maps[block][row, column] for block in range(3) for row in range(82) for column in range(123)],
    )


def square(value: acb_mat, rows: Sequence[int], columns: Sequence[int]) -> acb_mat:
    return acb_mat(122, 122, [value[row, column] for row in rows for column in columns])


def midpoint_inverse(value: acb_mat) -> acb_mat:
    midpoint = acb_mat(
        122,
        122,
        [
            acb(value[row, column].real.mid(), value[row, column].imag.mid())
            for row in range(122)
            for column in range(122)
        ],
    )
    return midpoint.inv()


def defect_upper(preconditioner: acb_mat, value: acb_mat) -> arb:
    identity = acb_mat(
        122,
        122,
        [acb(1 if row == column else 0) for row in range(122) for column in range(122)],
    )
    error = identity - preconditioner * value
    return max(
        sum((error[row, column].abs_upper() for column in range(122)), arb(0))
        for row in range(122)
    )


def main() -> int:
    packet = load(PACKET)
    require(
        packet["schema"] == "mtt.cbf.q79-eta9-physical-midpoint-three-evaluation-frame.v1",
        "packet schema",
    )
    claimed_hash = packet["canonical_payload_sha256"]
    unsigned = dict(packet)
    unsigned.pop("canonical_payload_sha256")
    require(canonical_sha256(unsigned) == claimed_hash, "canonical packet hash")
    paths = {name: bound_path(row) for name, row in packet["inputs"].items()}
    source = load(paths["source_snapshot"])
    compiled = json.loads(
        gzip.decompress(paths["compiled_characteristic_zero_operator"].read_bytes()).decode("ascii")
    )
    require(
        source["schema"] == "mtt.cbf.q79-eta9-physical-midpoint-three-evaluation-frame-source.v1",
        "source schema",
    )
    require(
        compiled["schema"] == "mtt.cbf.q79-eta9-physical-char0-graph-operator-input.v1",
        "compiled schema",
    )
    ctx.prec = int(compiled["precision_bits"])

    char0 = load(paths["H4_char0_algebraization"])
    atlas = load(paths["H4_physical_midpoint_atlas"])
    edge2 = load(paths["H4_edge2_complete_branch_panel"])
    require(
        char0["geometry"]["incidence_rank"] == 126
        and char0["geometry"]["projective_deformation_rank"] == 122,
        "upstream characteristic-zero dimensions",
    )
    require(atlas["theorem_id"] == "H4-T152" and all(atlas["checks"].values()), "midpoint atlas")
    require(edge2["id"] == "H4-T155" and edge2["all_passed"], "edge2 panel")

    incidence = compiled["incidence"]
    pivots = [int(value) for value in incidence["pivot_columns_zero_based"]]
    free = [int(value) for value in incidence["free_columns_zero_based"]]
    A = interval_matrix(126, 126, incidence["selected_pivot_block_entries_row_major"])
    B = interval_matrix(126, 123, incidence["selected_free_block_entries_row_major"])
    require(not A.det().contains(0), "incidence pivot determinant")
    kernel = make_kernel(A, B, pivots, free)
    member = [parse_acb(value) for value in compiled["selected_member_coefficients"]]
    member_free = acb_mat(123, 1, [member[column] for column in free])
    reconstructed = kernel * member_free
    require(all((reconstructed[row, 0] - member[row]).contains(0) for row in range(249)), "radial reconstruction")

    selection = source["physical_row_selection"]
    segments = selection["segments_in_order"]
    require(segments == ["edge-0", "edge-1", "edge-2"], "physical row order")
    piv = [int(value) for value in selection["relation_pivots_zero_based"]]
    center_data = [path_point(edge, arb(1) / 2) for edge in range(3)]
    center_points = [point for point, _radicand in center_data]
    require(all(not radicand.contains(0) for _point, radicand in center_data), "center lift branch")
    for edge, segment in enumerate(segments):
        midpoint_packet = load(paths[f"H4_edge{edge}_midpoint"])
        stored = [parse_acb(value) for value in midpoint_packet["geometry"]["Fermat_point"]]
        exported = [parse_acb(value) for value in compiled["physical_midpoint_rows"][segment]]
        require(all(point.overlaps(a) and point.overlaps(b) for point, a, b in zip(center_points[edge], stored, exported, strict=True)), f"midpoint binding {edge}")
        require(midpoint_packet["roots"]["count"] == 198 and all(midpoint_packet["checks"].values()), f"midpoint certificate {edge}")
    require(not det3(center_points).contains(0), "physical midpoint weight determinant")
    center_maps = [restricted_map(point, member, kernel, pivot) for point, pivot in zip(center_points, piv, strict=True)]
    center_stack = stacked(center_maps)

    rank_certificate = source["rank_certificate"]
    drop = int(rank_certificate["gauge_drop_free_coordinate_zero_based"])
    require(free[drop] == rank_certificate["gauge_drop_ambient_coordinate_zero_based"], "gauge binding")
    columns = [column for column in range(123) if column != drop]
    rows = [int(value) for value in rank_certificate["selected_output_rows_zero_based"]]
    require(len(rows) == len(set(rows)) == 122, "certificate rows")
    center_square = square(center_stack, rows, columns)
    require(not center_square.det().contains(0), "center rank-122 minor")
    radial = center_stack * member_free
    require(all(radial[row, 0].contains(0) for row in range(246)), "exact radial kernel")

    radius = Fraction(selection["segment_parameter_halfwidth"])
    parameter = arb(1) / 2 + arb(0, 1) * arb(radius.numerator) / radius.denominator
    panel_data = [path_point(edge, parameter) for edge in range(3)]
    panel_points = [point for point, _radicand in panel_data]
    require(all(not radicand.contains(0) for _point, radicand in panel_data), "panel lift branch")
    require(not det3(panel_points).contains(0), "panel weight determinant")
    panel_maps = [restricted_map(point, member, kernel, pivot) for point, pivot in zip(panel_points, piv, strict=True)]
    panel_square = square(stacked(panel_maps), rows, columns)
    defect = defect_upper(midpoint_inverse(center_square), panel_square)
    require(defect < 1, "Neumann panel certificate")
    stored_defect = arb(packet["positive_width_operator_panel"]["Neumann_infinity_norm_defect_upper"])
    require(defect.overlaps(stored_defect), "stored defect overlap")

    rank = packet["characteristic_zero_rank"]
    require(
        rank["incidence_rank"] == 126
        and rank["affine_graph_tangent_rank"] == 123
        and rank["radial_kernel_rank"] == 1
        and rank["joined_evaluation_image_rank"] == 122
        and rank["projective_kernel_rank"] == 0,
        "stored rank decision",
    )
    require(packet["all_checks_pass"] and all(packet["checks"].values()), "stored checks")
    require(not any(packet["guardrails"].values()), "guardrails")
    require(packet["parameter_ledger"]["observed_values_used"] == 0, "observed values")
    print(
        "CBF.T72 verification: PASS "
        f"char0_projective_rank=122 panel_defect={float(defect):.6e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
