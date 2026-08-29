"""Independently verify the associated-matter BV4 compiler packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
LOCK_PATH = ROOT / "q79_bv4_associated_matter_externalization_source_lock.json"
SCHEMA_PATH = ROOT / "q79_bv4_associated_matter_externalization_contract.schema.json"
THEOREM_PATH = ROOT / "AssociatedMatterProductDiracBVExternalizationCompilerTheorem_v1.md"
BASELINE_PATH = ROOT / "q79_seven_row_endpoint_factorization.packet.json"

F = Fraction
Sparse = dict[tuple[int, int], F]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(source: Sparse) -> Sparse:
    return {position: value for position, value in source.items() if value}


def identity(size: int) -> Sparse:
    return {(index, index): F(1) for index in range(size)}


def diagonal(values: list[int]) -> Sparse:
    return {
        (index, index): F(value)
        for index, value in enumerate(values)
        if value
    }


def add(left: Sparse, right: Sparse) -> Sparse:
    result = dict(left)
    for position, value in right.items():
        result[position] = result.get(position, F(0)) + value
    return clean(result)


def scale(value: int | F, source: Sparse) -> Sparse:
    return clean({position: F(value) * entry for position, entry in source.items()})


def transpose(source: Sparse) -> Sparse:
    return {(column, row): value for (row, column), value in source.items()}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, F]]] = {}
    for (row, column), value in right.items():
        by_row.setdefault(row, []).append((column, value))
    result: Sparse = {}
    for (row, middle), left_value in left.items():
        for column, right_value in by_row.get(middle, []):
            position = (row, column)
            result[position] = result.get(position, F(0)) + left_value * right_value
    return clean(result)


def kron(left: Sparse, right: Sparse, right_dimension: int) -> Sparse:
    result: Sparse = {}
    for (row_l, column_l), value_l in left.items():
        for (row_r, column_r), value_r in right.items():
            result[
                (row_l * right_dimension + row_r, column_l * right_dimension + column_r)
            ] = value_l * value_r
    return clean(result)


def trace(source: Sparse, size: int) -> F:
    return sum((source.get((index, index), F(0)) for index in range(size)), F(0))


def apply(source: Sparse, vector: tuple[F, ...], rows: int) -> tuple[F, ...]:
    result = [F(0)] * rows
    for (row, column), value in source.items():
        result[row] += value * vector[column]
    return tuple(result)


def dot(left: tuple[F, ...], right: tuple[F, ...]) -> F:
    return sum((a * b for a, b in zip(left, right, strict=True)), F(0))


def make_witness() -> dict[str, object]:
    weights = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    plus = 64
    minus = 16
    total = 80

    d_plus: Sparse = {(index, index): F(1) for index in range(16)}
    d_x: Sparse = {}
    for index in range(16):
        d_x[(index, plus + index)] = F(1)
        d_x[(plus + index, index)] = F(1)
    gamma_x = diagonal([1] * plus + [-1] * minus)
    p0 = diagonal([0] * 16 + [1] * 48 + [0] * 16)
    q0 = add(identity(total), scale(-1, p0))
    rho_x = diagonal(weights * 5)

    d_y: Sparse = {(0, 1): F(1), (1, 0): F(1)}
    gamma_y = diagonal([1, -1])
    d_total = add(kron(d_y, identity(total), total), kron(gamma_y, d_x, total))
    square_formula = add(
        kron(multiply(d_y, d_y), identity(total), total),
        kron(identity(2), multiply(d_x, d_x), total),
    )
    p_total = kron(identity(2), p0, total)
    q_total = kron(identity(2), q0, total)

    return {
        "weights": weights,
        "D_plus": d_plus,
        "D_X": d_x,
        "Gamma_X": gamma_x,
        "P0": p0,
        "Q0": q0,
        "rho_X": rho_x,
        "D_Y": d_y,
        "Gamma_Y": gamma_y,
        "D_total": d_total,
        "square_formula": square_formula,
        "P_total": p_total,
        "Q_total": q_total,
    }


def anomaly_check() -> dict[str, int]:
    rows = [
        (3, 2, 1, 1, 1),
        (3, 1, -1, 0, -4),
        (3, 1, -1, 0, 2),
        (1, 2, 0, 1, -3),
        (1, 1, 0, 0, 6),
        (1, 1, 0, 0, 0),
    ]
    return {
        "dimension": sum(color * weak for color, weak, _, _, _ in rows),
        "gravity_u1": sum(color * weak * charge for color, weak, _, _, charge in rows),
        "u1_cubic": sum(color * weak * charge**3 for color, weak, _, _, charge in rows),
        "su3_squared_u1": sum(weak * charge for color, weak, _, _, charge in rows if color == 3),
        "su2_squared_u1": sum(color * charge for color, _, _, parity, charge in rows if parity),
        "su3_cubic": sum(weak * triality for color, weak, triality, _, _ in rows if color == 3),
        "weak_doublets": sum(color for color, _, _, parity, _ in rows if parity),
        "z6_failures": sum(
            (2 * triality + 3 * parity + charge) % 6 != 0
            for _, _, triality, parity, charge in rows
        ),
    }


def check() -> dict[str, bool]:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    witness = make_witness()

    d_x = witness["D_X"]
    gamma_x = witness["Gamma_X"]
    p0 = witness["P0"]
    q0 = witness["Q0"]
    rho_x = witness["rho_X"]
    d_y = witness["D_Y"]
    gamma_y = witness["Gamma_Y"]
    d_total = witness["D_total"]
    p_total = witness["P_total"]
    q_total = witness["Q_total"]
    d_total_squared = multiply(d_total, d_total)

    psi = (F(2), F(-3))
    eta = (F(5), F(7))
    embedded_psi = [F(0)] * 160
    embedded_eta = [F(0)] * 160
    for external in range(2):
        embedded_psi[external * 80 + 16] = psi[external]
        embedded_eta[external * 80 + 16] = eta[external]
    embedded_psi_t = tuple(embedded_psi)
    embedded_eta_t = tuple(embedded_eta)

    anomaly = anomaly_check()
    local_hashes = {item["path"]: item["sha256"] for item in lock["local_sources"]}
    adjacent_hashes = {
        (item["repository"], item["path"]): item["sha256"]
        for item in lock["adjacent_authorities"]
    }
    internal = packet["exact_internal_witness"]
    product = packet["exact_product_witness"]

    checks = {
        "packet_schema": packet.get("schema")
        == "boe.mtt.q79-bv4-associated-matter-externalization.packet.v1",
        "claim_id": packet.get("claim_id") == "CBF.T13",
        "source_lock_hash": packet.get("source_lock_sha256") == sha256(LOCK_PATH),
        "theorem_hash": packet.get("theorem_sha256") == sha256(THEOREM_PATH),
        "instance_schema_hash": packet.get("instance_schema_sha256") == sha256(SCHEMA_PATH),
        "all_builder_checks_pass": all(packet.get("checks", {}).values()),
        "D_plus_pattern_has_16_entries": len(witness["D_plus"]) == 16,
        "internal_dimension_is_80": internal["self_adjoint_dimension"] == 80,
        "kernel_dimension_is_48": internal["kernel_dimension"] == 48
        and trace(p0, 80) == 48,
        "complement_dimension_is_32": internal["complement_dimension"] == 32
        and trace(q0, 80) == 32,
        "DX_is_self_adjoint": transpose(d_x) == d_x,
        "DX_is_odd": add(multiply(gamma_x, d_x), multiply(d_x, gamma_x)) == {},
        "DX_square_is_Q0": multiply(d_x, d_x) == q0,
        "DX_is_its_reduced_green": multiply(d_x, d_x) == q0
        and multiply(d_x, p0) == {},
        "kernel_projector_is_exact": multiply(p0, p0) == p0
        and add(p0, q0) == identity(80),
        "shared_circle_equivariance": multiply(rho_x, d_x) == multiply(d_x, rho_x)
        and multiply(rho_x, p0) == multiply(p0, rho_x),
        "external_grading_anticommutation": add(
            multiply(d_y, gamma_y), multiply(gamma_y, d_y)
        )
        == {},
        "product_square_identity": d_total_squared == witness["square_formula"],
        "product_projector_reduces_Dtotal": multiply(p_total, d_total)
        == multiply(d_total, p_total),
        "product_retained_dimension_is_96": trace(p_total, 160) == 96,
        "product_complement_dimension_is_64": trace(q_total, 160) == 64,
        "product_complement_normal_is_two_Q": multiply(
            q_total, multiply(d_total_squared, q_total)
        )
        == scale(2, q_total),
        "quadratic_reduction_sample": dot(
            embedded_psi_t, apply(d_total, embedded_psi_t, 160)
        )
        == dot(psi, apply(d_y, psi, 2))
        == product["quadratic_sample"]["reduced_bilinear"],
        "cotangent_pairing_sample": dot(embedded_eta_t, embedded_psi_t)
        == dot(eta, psi)
        == product["cotangent_pairing_sample"]["reduced_pairing"],
        "one_family_dimension_is_16": anomaly["dimension"] == 16,
        "all_local_anomalies_vanish": all(
            anomaly[name] == 0
            for name in (
                "gravity_u1",
                "u1_cubic",
                "su3_squared_u1",
                "su2_squared_u1",
                "su3_cubic",
                "z6_failures",
            )
        ),
        "weak_doublet_parity_is_even": anomaly["weak_doublets"] % 2 == 0,
        "shared_circle_input_hash": packet["shared_circle_input"]["source_sha256"]
        == adjacent_hashes[
            (
                "20 Mathematical Language Discovery Program - Closure Dynamics",
                "shared_circle_sm_gauge_stack_reference.packet.json",
            )
        ],
        "contract_requires_same_root": all(
            "source_root_sha256" in schema["properties"][section]["required"]
            for section in (
                "internal_matter_operator",
                "external_causal_base",
                "representation_descent",
                "density_and_pairing",
            )
        ),
        "contract_requires_first_order_chiral_source": all(
            field in schema["properties"]["internal_matter_operator"]["required"]
            for field in (
                "first_order_operator_artifact",
                "characterwise_index_certificate",
                "chirality_orientation_certificate",
            )
        ),
        "contract_preserves_open_physical_rows": len(
            schema["properties"]["remaining_physical_rows"]["required"]
        )
        == 7,
        "baseline_checks_pass": all(baseline["checks"].values()),
        "physical_acceptance_remains_zero_of_three": packet["physical_packets_accepted"]
        == baseline["source_packet_factorization"]["physical_packets_accepted"]
        == 0
        and packet["physical_packets_total"] == 3,
        "physical_acceptance_remains_zero_of_seven": packet["physical_rows_accepted"]
        == baseline["physical_rows_accepted"]
        == 0
        and packet["physical_rows_total"] == 7,
        "decision_is_compiler_only": packet["decision"]
        == "RETAINED_ASSOCIATED_MATTER_EXTERNALIZATION_COMPILER_ONLY",
        "no_blocker_state_promotion": not packet["frontier_delta"][
            "blocker_states_changed"
        ],
        "no_physical_count_promotion": not packet["frontier_delta"][
            "physical_acceptance_count_changed"
        ],
        "local_CBF_T12_theorem_hash": sha256(
            ROOT / "SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md"
        )
        == local_hashes["SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md"],
        "local_CBF_T12_packet_hash": sha256(BASELINE_PATH)
        == local_hashes["q79_seven_row_endpoint_factorization.packet.json"],
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
        raise AssertionError(
            f"independent associated-matter BV4 checks failed: {failed}"
        )
    print(
        "independent associated-matter BV4 verification passed: "
        f"{len(checks)}/{len(checks)}"
    )


if __name__ == "__main__":
    main()
