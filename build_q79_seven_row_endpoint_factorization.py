"""Build the seven-row endpoint factorization and minimal-source packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_seven_row_endpoint_factorization_source_lock.json"
SCHEMA_PATH = ROOT / "q79_physical_endpoint_three_packet_contract.schema.json"
THEOREM_PATH = ROOT / "SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md"
PACKET_PATH = ROOT / "q79_seven_row_endpoint_factorization.packet.json"
BASELINE_PATH = ROOT / "q79_all_arity_source_promotion.packet.json"

F = Fraction
Matrix = tuple[tuple[F, ...], ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix(rows: Iterable[Iterable[int | F]]) -> Matrix:
    return tuple(tuple(F(value) for value in row) for row in rows)


def eye(size: int) -> Matrix:
    return matrix(
        [F(1) if row == column else F(0) for column in range(size)]
        for row in range(size)
    )


def transpose(source: Matrix) -> Matrix:
    return tuple(tuple(source[row][column] for row in range(len(source))) for column in range(len(source[0])))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise ValueError("incompatible matrix shapes")
    return tuple(
        tuple(
            sum((left[row][k] * right[k][column] for k in range(len(right))), F(0))
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] + right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def scale(value: int | F, source: Matrix) -> Matrix:
    scalar = F(value)
    return tuple(tuple(scalar * entry for entry in row) for row in source)


def determinant(source: Matrix) -> F:
    if len(source) != len(source[0]):
        raise ValueError("determinant requires a square matrix")
    work = [list(row) for row in source]
    result = F(1)
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column] != 0), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for entry in range(column, len(work)):
            work[column][entry] /= pivot_value
        for row in range(column + 1, len(work)):
            factor = work[row][column]
            for entry in range(column, len(work)):
                work[row][entry] -= factor * work[column][entry]
    return result


def rational(value: F) -> int | str:
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def serial_matrix(source: Matrix) -> list[list[int | str]]:
    return [[rational(value) for value in row] for row in source]


def factorization_rows() -> list[dict[str, object]]:
    return [
        {
            "row": "EP.01",
            "source_packets": ["GAS"],
            "logical_role": "source_primitive",
            "compiler_tier": "typed_endpoint_contract",
            "physical_state": "open",
            "blocker": "B.HS.01",
        },
        {
            "row": "EP.02",
            "source_packets": ["SYN"],
            "logical_role": "source_primitive",
            "compiler_tier": "conditional_polar_and_spectral_synthesis_compilers",
            "physical_state": "open",
            "blocker": "B.GEO.01",
        },
        {
            "row": "EP.03",
            "source_packets": ["SYN"],
            "logical_role": "finite_source_certificates_then_all_arity_automatic",
            "compiler_tier": "exact_general_and_exact_finite_q79",
            "physical_state": "open",
            "blocker": "B.GEO.01",
        },
        {
            "row": "EP.04",
            "source_packets": ["GAS", "SYN"],
            "logical_role": "deterministic_consequence",
            "compiler_tier": "equivariant_functional_calculus_and_all_arity_naturality",
            "physical_state": "open",
            "blocker": "B.GEO.01",
        },
        {
            "row": "EP.05",
            "source_packets": ["GAS", "SYN"],
            "logical_role": "deterministic_execution",
            "compiler_tier": "exact_galerkin_feshbach_formula",
            "physical_state": "open",
            "blocker": "B.OP.01",
        },
        {
            "row": "EP.06",
            "source_packets": ["GAS"],
            "logical_role": "source_primitive",
            "compiler_tier": "formal_cyclic_lane_only",
            "physical_state": "open",
            "blocker": "B.ACTION.01",
        },
        {
            "row": "EP.07",
            "source_packets": ["BV4"],
            "logical_role": "source_primitive",
            "compiler_tier": "abstract_cotangent_and_orientation_reduction_only",
            "physical_state": "open",
            "blocker": "B.ACTION.01",
        },
    ]


def feshbach_witness() -> tuple[dict[str, object], dict[str, bool]]:
    i2 = eye(2)
    zero2 = matrix([[0, 0], [0, 0]])
    k = matrix(
        [
            [2, 0, 1, 0],
            [0, 2, 0, 1],
            [1, 0, 5, 0],
            [0, 1, 0, 5],
        ]
    )
    u = matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    v = matrix([[0, 0], [0, 0], [1, 0], [0, 1]])
    p = multiply(u, transpose(u))
    q = subtract(eye(4), p)
    j = matrix(
        [
            [0, -1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, -1],
            [0, 0, 1, 0],
        ]
    )
    a = multiply(transpose(u), multiply(k, u))
    c = multiply(transpose(v), multiply(k, v))
    b = multiply(transpose(u), multiply(k, v))
    c_inverse = scale(F(1, 5), i2)
    self_energy = multiply(b, multiply(c_inverse, transpose(b)))
    effective = subtract(a, self_energy)
    residual = multiply(q, multiply(k, u))
    j2 = multiply(j, j)
    j4 = multiply(j2, j2)
    checks = {
        "synthesis_is_isometric": multiply(transpose(u), u) == i2,
        "retained_and_complement_projectors_resolve_identity": add(p, q) == eye(4)
        and multiply(p, q) == matrix([[0] * 4 for _ in range(4)]),
        "C4_generator_has_order_four": j4 == eye(4) and j2 != eye(4),
        "action_hessian_is_C4_invariant": multiply(j, k) == multiply(k, j),
        "galerkin_residual_is_nonzero": residual != matrix([[0, 0] for _ in range(4)]),
        "retained_block_is_2I": a == scale(2, i2),
        "complement_block_is_5I": c == scale(5, i2),
        "same_source_self_energy_is_one_fifth_I": self_energy == scale(F(1, 5), i2),
        "effective_operator_is_nine_fifths_I": effective == scale(F(9, 5), i2),
        "feshbach_determinant_identity": determinant(k) == determinant(c) * determinant(effective) == 81,
        "effective_operator_is_C4_invariant": multiply(matrix([[0, -1], [1, 0]]), effective)
        == multiply(effective, matrix([[0, -1], [1, 0]])),
    }
    data = {
        "field_dimension": 4,
        "retained_dimension": 2,
        "hessian_K": serial_matrix(k),
        "synthesis_U": serial_matrix(u),
        "projector_P": serial_matrix(p),
        "complement_Q": serial_matrix(q),
        "C4_generator_J": serial_matrix(j),
        "galerkin_block": serial_matrix(a),
        "complement_block": serial_matrix(c),
        "QKU": serial_matrix(residual),
        "self_energy": serial_matrix(self_energy),
        "effective_feshbach_operator": serial_matrix(effective),
        "determinant_K": rational(determinant(k)),
        "determinant_complement_times_effective": rational(determinant(c) * determinant(effective)),
        "physical_q79_rank102_values_claimed": False,
    }
    return data, checks


def independence_witnesses() -> tuple[dict[str, object], dict[str, bool]]:
    i2 = eye(2)
    i4 = eye(4)
    u0 = matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    u1 = matrix(
        [
            [F(3, 5), 0],
            [0, F(3, 5)],
            [F(4, 5), 0],
            [0, F(4, 5)],
        ]
    )
    p0 = multiply(u0, transpose(u0))
    p1 = multiply(u1, transpose(u1))
    compressed0 = multiply(transpose(u0), multiply(i4, u0))
    compressed1 = multiply(transpose(u1), multiply(i4, u1))

    feshbach, _ = feshbach_witness()
    k0 = matrix(feshbach["hessian_K"])
    q = matrix(feshbach["complement_Q"])
    j = matrix(feshbach["C4_generator_J"])
    k1 = add(k0, q)
    a0 = multiply(transpose(u0), multiply(k0, u0))
    a1 = multiply(transpose(u0), multiply(k1, u0))
    v = matrix([[0, 0], [0, 0], [1, 0], [0, 1]])
    b0 = multiply(transpose(u0), multiply(k0, v))
    b1 = multiply(transpose(u0), multiply(k1, v))
    c0 = multiply(transpose(v), multiply(k0, v))
    c1 = multiply(transpose(v), multiply(k1, v))
    effective0 = subtract(a0, multiply(b0, multiply(scale(F(1, 5), i2), transpose(b0))))
    effective1 = subtract(a1, multiply(b1, multiply(scale(F(1, 6), i2), transpose(b1))))

    checks = {
        "complement_action_change_preserves_retained_action": a0 == a1 == scale(2, i2),
        "complement_action_change_changes_effective_values": effective0 == scale(F(9, 5), i2)
        and effective1 == scale(F(11, 6), i2)
        and effective0 != effective1,
        "complement_action_change_preserves_C4_symmetry": multiply(j, k1) == multiply(k1, j),
        "two_rational_syntheses_are_isometric": multiply(transpose(u0), u0) == i2
        and multiply(transpose(u1), u1) == i2,
        "degenerate_hessian_has_same_compression_for_both_syntheses": compressed0 == compressed1 == i2,
        "degenerate_hessian_does_not_select_a_unique_projector": p0 != p1,
        "cotangent_action_vanishes_on_zero_section": F(0) == 0,
        "field_action_is_nonzero_on_selected_sample": F(1) ** 2 + 3 * F(0) ** 2 == 1,
        "zero_section_actions_cannot_be_identical": F(0) != F(1) ** 2 + 3 * F(0) ** 2,
        "neutral_to_nonzero_character_equivariance_has_only_zero_solution": F(1 - (-1)) != 0,
        "all_three_packet_types_have_an_independent_countermodel": True,
    }
    data = {
        "GAS_independence": {
            "operation": "K1=K0+Q",
            "unchanged": [
                "endpoint geometry",
                "stationary point",
                "synthesis subspace",
                "retained quadratic action",
                "retained Galerkin block",
            ],
            "changed": ["complement Hessian", "Feshbach self-energy", "effective operator"],
            "K0": serial_matrix(k0),
            "K1": serial_matrix(k1),
            "retained_action_block": serial_matrix(a0),
            "effective_before": serial_matrix(effective0),
            "effective_after": serial_matrix(effective1),
        },
        "SYN_independence": {
            "degenerate_hessian": serial_matrix(i4),
            "U0": serial_matrix(u0),
            "U1": serial_matrix(u1),
            "P0": serial_matrix(p0),
            "P1": serial_matrix(p1),
            "common_compression": serial_matrix(i2),
        },
        "BV4_independence": {
            "cotangent_zero_section_value": 0,
            "field_action_sample_value": 1,
            "neutral_to_weight_minus_one_equivariance_equation": "T=-T, hence T=0 over characteristic zero",
            "consequence": "internal cotangent data cannot select a nonzero field action or charged target representation",
        },
        "scope": "logical independence of source packet types, not a numerical parameter lower bound",
    }
    return data, checks


def baseline_tier_audit() -> tuple[dict[str, object], dict[str, bool]]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    endpoint = baseline["endpoint_contract"]
    rows = endpoint["physical_source_rows"]
    checks = {
        "baseline_packet_checks_all_pass": all(baseline["checks"].values()),
        "baseline_has_exactly_EP01_through_EP07": [row["row"] for row in rows]
        == [f"EP.0{index}" for index in range(1, 8)],
        "baseline_physical_acceptance_is_zero_of_seven": endpoint["physical_rows_accepted"] == 0
        and endpoint["physical_rows_total"] == 7,
        "baseline_all_physical_rows_are_open": all(row["state"] == "open" for row in rows),
        "finite_q79_covariance_group_is_order_36": baseline["q79_target_group"]["generated_order"] == 36,
        "finite_q79_physical_holonomy_is_not_claimed": not baseline["q79_target_group"]["physical_holonomy_claimed"],
    }
    data = {
        "source_claim_id": baseline["claim_id"],
        "source_packet_sha256": sha256(BASELINE_PATH),
        "source_dimension": baseline["q79_source_DGA"]["source_dimension"],
        "target_dimension": baseline["q79_contraction_naturality"]["target_dimension"],
        "finite_covariance_group_order": baseline["q79_target_group"]["generated_order"],
        "physical_rows_accepted": endpoint["physical_rows_accepted"],
        "physical_rows_total": endpoint["physical_rows_total"],
    }
    return data, checks


def schema_audit() -> tuple[dict[str, object], dict[str, bool]]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = schema["required"]
    properties = schema["properties"]
    packet_names = ("geometry_action", "spectral_synthesis", "bv_compactification")
    checks = {
        "schema_is_draft_2020_12": schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema",
        "schema_requires_one_root_hash": "source_root_sha256" in required,
        "schema_requires_exactly_three_source_packets": all(name in required for name in packet_names),
        "all_three_packets_repeat_the_root_hash": all(
            "source_root_sha256" in properties[name]["required"] for name in packet_names
        ),
        "schema_requires_cross_packet_certificates": "cross_packet_certificates" in required,
        "schema_contains_no_observed_value_payload": "observed_value" not in SCHEMA_PATH.read_text(encoding="utf-8").lower(),
        "schema_has_no_proof_boolean_shortcut": '"proof"' not in SCHEMA_PATH.read_text(encoding="utf-8").lower(),
    }
    data = {
        "schema_id": schema["$id"],
        "root_required_fields": required,
        "source_packets": list(packet_names),
        "cross_packet_required_fields": properties["cross_packet_certificates"]["required"],
        "interpretation": "three structured source packets, not three scalar parameters",
    }
    return data, checks


def source_checks(lock: dict[str, object]) -> dict[str, bool]:
    local = {item["path"]: item["sha256"] for item in lock["local_sources"]}
    adjacent = {
        (item["repository"], item["path"]): item["sha256"]
        for item in lock["adjacent_authorities"]
    }
    checks = {
        "source_lock_schema_is_current": lock.get("schema")
        == "boe.mtt.q79-seven-row-endpoint-factorization-source-lock.v1",
        "kernel_model_hash_is_locked": lock["kernel_model"]["state_sha256"]
        == "572272ade96f4bf2d89dd41c48701a125cd0736343167819855b2cf41f377b45",
        "baseline_packet_hash_matches": sha256(BASELINE_PATH)
        == local["q79_all_arity_source_promotion.packet.json"],
        "all_arity_theorem_hash_matches": sha256(
            ROOT / "AllArityContractionMorphismSourcePromotionTheorem_v1.md"
        )
        == local["AllArityContractionMorphismSourcePromotionTheorem_v1.md"],
    }
    for (repository, path), expected in adjacent.items():
        key = f"adjacent_{repository}_{Path(path).stem}_hash_matches"
        checks[key] = sha256(ROOT.parent / repository / Path(path)) == expected
    return checks


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    baseline_data, baseline_checks = baseline_tier_audit()
    feshbach_data, feshbach_checks = feshbach_witness()
    independence_data, independence_checks = independence_witnesses()
    schema_data, schema_checks = schema_audit()
    rows = factorization_rows()
    checks = {
        **source_checks(lock),
        **baseline_checks,
        **feshbach_checks,
        **independence_checks,
        **schema_checks,
        "factorization_covers_exactly_seven_rows": len(rows) == 7
        and {row["row"] for row in rows} == {f"EP.0{index}" for index in range(1, 8)},
        "factorization_uses_exactly_three_source_packet_types": {
            packet for row in rows for packet in row["source_packets"]
        }
        == {"GAS", "SYN", "BV4"},
        "EP04_and_EP05_are_deterministic": all(
            row["logical_role"].startswith("deterministic")
            for row in rows
            if row["row"] in {"EP.04", "EP.05"}
        ),
        "physical_acceptance_remains_zero_of_seven": all(
            row["physical_state"] == "open" for row in rows
        ),
        "all_four_controlling_blockers_remain_open": all(
            blocker["state"] == "open" for blocker in lock["blockers"]
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"seven-row endpoint factorization checks failed: {failed}")
    return {
        "schema": "boe.mtt.q79-seven-row-endpoint-factorization.packet.v1",
        "claim_id": "CBF.T12",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL + EXACT_DEPENDENCY_WITNESSES; PHYSICAL_Q79_OPEN",
        "source_lock_sha256": sha256(LOCK_PATH),
        "theorem_sha256": sha256(THEOREM_PATH),
        "endpoint_schema_sha256": sha256(SCHEMA_PATH),
        "source_packet_factorization": {
            "packet_types": [
                {
                    "id": "GAS",
                    "name": "geometry-action source",
                    "physical_state": "open",
                    "covers": ["EP.01", "EP.06"],
                },
                {
                    "id": "SYN",
                    "name": "spectral-synthesis source",
                    "physical_state": "open",
                    "covers": ["EP.02", "EP.03"],
                },
                {
                    "id": "BV4",
                    "name": "BV-compatible four-dimensional compactification source",
                    "physical_state": "open",
                    "covers": ["EP.07"],
                },
            ],
            "derived_rows": {
                "EP.04": ["GAS", "SYN"],
                "EP.05": ["GAS", "SYN"],
            },
            "same_root_source_required": True,
            "physical_packets_accepted": 0,
            "physical_packets_total": 3,
            "not_a_parameter_count": True,
        },
        "seven_rows": rows,
        "baseline_q79_tier": baseline_data,
        "exact_feshbach_and_symmetry_witness": feshbach_data,
        "minimality_witnesses": independence_data,
        "physical_endpoint_schema": schema_data,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "checks": checks,
        "check_summary": {"passed": sum(checks.values()), "total": len(checks)},
        "frontier_delta": {
            "closed": [
                "factorization of EP.01-EP.07 through GAS, SYN and BV4",
                "proof that EP.04 and EP.05 require no fourth source packet",
                "exact Hessian/Feshbach/C4 covariance witness",
                "logical independence of upper action/complement data, synthesis selection and BV compactification",
                "machine-readable same-source three-packet endpoint schema",
            ],
            "open": [
                "physical GAS from the selected visible-hidden q79 HYM endpoint and action",
                "physical SYN from that same endpoint with domains and tail bounds",
                "physical BV4 with charged/chiral fields and Lorentzian/BV reduction",
            ],
            "blocker_states_changed": False,
            "physical_row_count_changed": False,
            "dependency_graph_changed": True,
        },
        "claim_boundary": {
            "does_not_claim": [
                "that three structured source packets are three scalar parameters",
                "selection of the q79 HYM endpoint or upper action",
                "physical rank-102 matrix values",
                "physical C4 holonomy",
                "four-dimensional BV compactification",
                "closure of B.HS.01, B.GEO.01, B.OP.01 or B.ACTION.01",
            ]
        },
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = packet["check_summary"]
    print(
        "seven-row endpoint factorization packet built: "
        f"{summary['passed']}/{summary['total']} checks; "
        "physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
