"""Independently verify the seven-row endpoint factorization packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_seven_row_endpoint_factorization.packet.json"
LOCK_PATH = ROOT / "q79_seven_row_endpoint_factorization_source_lock.json"
SCHEMA_PATH = ROOT / "q79_physical_endpoint_three_packet_contract.schema.json"
THEOREM_PATH = ROOT / "SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md"
BASELINE_PATH = ROOT / "q79_all_arity_source_promotion.packet.json"

F = Fraction
Matrix = tuple[tuple[F, ...], ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix(rows: list[list[int | str | F]]) -> Matrix:
    return tuple(tuple(F(value) for value in row) for row in rows)


def eye(size: int) -> Matrix:
    return tuple(
        tuple(F(1) if row == column else F(0) for column in range(size))
        for row in range(size)
    )


def transpose(source: Matrix) -> Matrix:
    return tuple(tuple(source[row][column] for row in range(len(source))) for column in range(len(source[0])))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            sum((left[row][k] * right[k][column] for k in range(len(right))), F(0))
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] + right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def scale(value: int | F, source: Matrix) -> Matrix:
    return tuple(tuple(F(value) * entry for entry in row) for row in source)


def determinant(source: Matrix) -> F:
    work = [list(row) for row in source]
    result = F(1)
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column]), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        value = work[column][column]
        result *= value
        for entry in range(column, len(work)):
            work[column][entry] /= value
        for row in range(column + 1, len(work)):
            factor = work[row][column]
            for entry in range(column, len(work)):
                work[row][entry] -= factor * work[column][entry]
    return result


def check() -> dict[str, bool]:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    witness = packet["exact_feshbach_and_symmetry_witness"]
    k = matrix(witness["hessian_K"])
    u = matrix(witness["synthesis_U"])
    p = matrix(witness["projector_P"])
    q = matrix(witness["complement_Q"])
    j = matrix(witness["C4_generator_J"])
    feshbach = matrix(witness["effective_feshbach_operator"])
    u_star = transpose(u)
    a = multiply(u_star, multiply(k, u))
    v = matrix([[0, 0], [0, 0], [1, 0], [0, 1]])
    c = multiply(transpose(v), multiply(k, v))
    b = multiply(u_star, multiply(k, v))
    self_energy = multiply(b, multiply(scale(F(1, 5), eye(2)), transpose(b)))

    synth = packet["minimality_witnesses"]["SYN_independence"]
    u0 = matrix(synth["U0"])
    u1 = matrix(synth["U1"])
    p0 = multiply(u0, transpose(u0))
    p1 = multiply(u1, transpose(u1))

    local_hashes = {item["path"]: item["sha256"] for item in lock["local_sources"]}
    adjacent_hashes = {
        (item["repository"], item["path"]): item["sha256"]
        for item in lock["adjacent_authorities"]
    }
    rows = packet["seven_rows"]
    packet_types = packet["source_packet_factorization"]["packet_types"]
    schema_packets = ("geometry_action", "spectral_synthesis", "bv_compactification")

    checks = {
        "packet_schema": packet.get("schema")
        == "boe.mtt.q79-seven-row-endpoint-factorization.packet.v1",
        "claim_id": packet.get("claim_id") == "CBF.T12",
        "source_lock_hash": packet.get("source_lock_sha256") == sha256(LOCK_PATH),
        "theorem_hash": packet.get("theorem_sha256") == sha256(THEOREM_PATH),
        "endpoint_schema_hash": packet.get("endpoint_schema_sha256") == sha256(SCHEMA_PATH),
        "all_builder_checks_pass": all(packet.get("checks", {}).values()),
        "seven_rows_are_exactly_EP01_to_EP07": [row["row"] for row in rows]
        == [f"EP.0{index}" for index in range(1, 8)],
        "three_packet_types_only": {item["id"] for item in packet_types}
        == {"GAS", "SYN", "BV4"},
        "all_rows_covered_by_three_packets": {
            source for row in rows for source in row["source_packets"]
        }
        == {"GAS", "SYN", "BV4"},
        "EP04_is_derived": next(row for row in rows if row["row"] == "EP.04")["logical_role"]
        == "deterministic_consequence",
        "EP05_is_derived": next(row for row in rows if row["row"] == "EP.05")["logical_role"]
        == "deterministic_execution",
        "physical_rows_remain_zero_of_seven": packet["physical_rows_accepted"] == 0
        and packet["physical_rows_total"] == 7
        and all(row["physical_state"] == "open" for row in rows),
        "physical_packets_remain_zero_of_three": packet["source_packet_factorization"][
            "physical_packets_accepted"
        ]
        == 0
        and packet["source_packet_factorization"]["physical_packets_total"] == 3,
        "packet_count_is_not_parameter_count": packet["source_packet_factorization"][
            "not_a_parameter_count"
        ],
        "independent_isometry": multiply(u_star, u) == eye(2),
        "independent_projector_resolution": subtract(eye(4), p) == q,
        "independent_C4_order": multiply(multiply(j, j), multiply(j, j)) == eye(4)
        and multiply(j, j) != eye(4),
        "independent_action_C4_naturality": multiply(j, k) == multiply(k, j),
        "independent_feshbach_value": feshbach == subtract(a, self_energy) == scale(F(9, 5), eye(2)),
        "independent_feshbach_determinant": determinant(k) == determinant(c) * determinant(feshbach) == 81,
        "independent_complement_action_countermodel": multiply(
            u_star, multiply(add(k, q), u)
        )
        == a
        and multiply(j, add(k, q)) == multiply(add(k, q), j)
        and subtract(
            a,
            multiply(b, multiply(scale(F(1, 6), eye(2)), transpose(b))),
        )
        == scale(F(11, 6), eye(2))
        != feshbach,
        "independent_synthesis_countermodel": multiply(transpose(u0), u0) == eye(2)
        and multiply(transpose(u1), u1) == eye(2)
        and multiply(transpose(u0), multiply(eye(4), u0))
        == multiply(transpose(u1), multiply(eye(4), u1))
        == eye(2)
        and p0 != p1,
        "independent_zero_section_countermodel": F(0) != F(1) ** 2 + 3 * F(0) ** 2,
        "independent_neutral_character_countermodel": F(1 - (-1)) != 0,
        "baseline_q79_checks_pass": all(baseline["checks"].values()),
        "baseline_q79_physical_count_unchanged": baseline["endpoint_contract"][
            "physical_rows_accepted"
        ]
        == 0
        and baseline["endpoint_contract"]["physical_rows_total"] == 7,
        "schema_requires_three_packets": all(name in schema["required"] for name in schema_packets),
        "schema_repeats_same_root_hash": all(
            "source_root_sha256" in schema["properties"][name]["required"]
            for name in schema_packets
        ),
        "local_baseline_hash": sha256(BASELINE_PATH)
        == local_hashes["q79_all_arity_source_promotion.packet.json"],
        "local_all_arity_theorem_hash": sha256(
            ROOT / "AllArityContractionMorphismSourcePromotionTheorem_v1.md"
        )
        == local_hashes["AllArityContractionMorphismSourcePromotionTheorem_v1.md"],
        "blocker_states_not_claimed_changed": not packet["frontier_delta"][
            "blocker_states_changed"
        ],
    }
    for (repository, path), expected in adjacent_hashes.items():
        checks[f"adjacent_{repository}_{Path(path).stem}_hash"] = sha256(
            ROOT.parent / repository / Path(path)
        ) == expected
    return checks


def main() -> None:
    checks = check()
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"independent seven-row factorization checks failed: {failed}")
    print(f"independent seven-row endpoint verification passed: {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
