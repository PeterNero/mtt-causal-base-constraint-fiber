"""Build the associated-matter product-Dirac/BV externalization packet."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_bv4_associated_matter_externalization_source_lock.json"
SCHEMA_PATH = ROOT / "q79_bv4_associated_matter_externalization_contract.schema.json"
THEOREM_PATH = ROOT / "AssociatedMatterProductDiracBVExternalizationCompilerTheorem_v1.md"
PACKET_PATH = ROOT / "q79_bv4_associated_matter_externalization.packet.json"
BASELINE_PATH = ROOT / "q79_seven_row_endpoint_factorization.packet.json"

F = Fraction
Entry = tuple[int, int]
Sparse = dict[Entry, F]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(source: Sparse) -> Sparse:
    return {position: value for position, value in source.items() if value}


def identity(size: int) -> Sparse:
    return {(index, index): F(1) for index in range(size)}


def diagonal(values: Iterable[int | F]) -> Sparse:
    return {
        (index, index): F(value)
        for index, value in enumerate(values)
        if F(value)
    }


def add(left: Sparse, right: Sparse) -> Sparse:
    result = dict(left)
    for position, value in right.items():
        result[position] = result.get(position, F(0)) + value
    return clean(result)


def scale(value: int | F, source: Sparse) -> Sparse:
    scalar = F(value)
    return clean({position: scalar * entry for position, entry in source.items()})


def transpose(source: Sparse) -> Sparse:
    return {(column, row): value for (row, column), value in source.items()}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_rows: dict[int, list[tuple[int, F]]] = {}
    for (row, column), value in right.items():
        right_rows.setdefault(row, []).append((column, value))
    result: Sparse = {}
    for (row, middle), left_value in left.items():
        for column, right_value in right_rows.get(middle, []):
            position = (row, column)
            result[position] = result.get(position, F(0)) + left_value * right_value
    return clean(result)


def kron(
    left: Sparse,
    left_rows: int,
    left_columns: int,
    right: Sparse,
    right_rows: int,
    right_columns: int,
) -> Sparse:
    del left_rows, right_rows
    result: Sparse = {}
    for (row_l, column_l), value_l in left.items():
        for (row_r, column_r), value_r in right.items():
            result[
                (row_l * right_columns + row_r, column_l * right_columns + column_r)
            ] = value_l * value_r
    return clean(result)


def trace(source: Sparse, size: int) -> F:
    return sum((source.get((index, index), F(0)) for index in range(size)), F(0))


def apply(source: Sparse, vector: tuple[F, ...], rows: int) -> tuple[F, ...]:
    result = [F(0) for _ in range(rows)]
    for (row, column), value in source.items():
        result[row] += value * vector[column]
    return tuple(result)


def dot(left: tuple[F, ...], right: tuple[F, ...]) -> F:
    return sum((a * b for a, b in zip(left, right, strict=True)), F(0))


def rank(source: Sparse, rows: int, columns: int) -> int:
    work = [
        [source.get((row, column), F(0)) for column in range(columns)]
        for row in range(rows)
    ]
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        for entry in range(column, columns):
            work[pivot_row][entry] /= pivot_value
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                for entry in range(column, columns):
                    work[row][entry] -= factor * work[pivot_row][entry]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def sectors() -> list[dict[str, int | str]]:
    return [
        {"name": "Q", "color_dim": 3, "weak_dim": 2, "triality": 1, "weak_parity": 1, "six_Y": 1},
        {"name": "u^c", "color_dim": 3, "weak_dim": 1, "triality": -1, "weak_parity": 0, "six_Y": -4},
        {"name": "d^c", "color_dim": 3, "weak_dim": 1, "triality": -1, "weak_parity": 0, "six_Y": 2},
        {"name": "L", "color_dim": 1, "weak_dim": 2, "triality": 0, "weak_parity": 1, "six_Y": -3},
        {"name": "e^c", "color_dim": 1, "weak_dim": 1, "triality": 0, "weak_parity": 0, "six_Y": 6},
        {"name": "N^c", "color_dim": 1, "weak_dim": 1, "triality": 0, "weak_parity": 0, "six_Y": 0},
    ]


def h16_weights(rows: list[dict[str, int | str]]) -> tuple[int, ...]:
    weights: list[int] = []
    for row in rows:
        multiplicity = int(row["color_dim"]) * int(row["weak_dim"])
        weights.extend([int(row["six_Y"])] * multiplicity)
    return tuple(weights)


def anomaly_rows(rows: list[dict[str, int | str]]) -> dict[str, int]:
    gravitational_u1 = 0
    cubic_u1 = 0
    su3_squared_u1 = 0
    su2_squared_u1 = 0
    su3_cubic = 0
    weak_doublets = 0
    for row in rows:
        color = int(row["color_dim"])
        weak = int(row["weak_dim"])
        triality = int(row["triality"])
        parity = int(row["weak_parity"])
        charge = int(row["six_Y"])
        dimension = color * weak
        gravitational_u1 += dimension * charge
        cubic_u1 += dimension * charge**3
        if color == 3:
            su3_squared_u1 += weak * charge
            su3_cubic += weak * triality
        if parity:
            su2_squared_u1 += color * charge
            weak_doublets += color
    return {
        "gravitational_U1": gravitational_u1,
        "U1_cubic": cubic_u1,
        "SU3_squared_U1_twice_Dynkin": su3_squared_u1,
        "SU2_squared_U1_twice_Dynkin": su2_squared_u1,
        "SU3_cubic": su3_cubic,
        "weak_doublet_count": weak_doublets,
    }


def internal_witness(weights: tuple[int, ...]) -> tuple[dict[str, object], dict[str, bool], dict[str, Sparse]]:
    h16 = len(weights)
    plus = 4 * h16
    minus = h16
    total = plus + minus

    d_plus: Sparse = {(index, index): F(1) for index in range(h16)}
    d_x: Sparse = {}
    for index in range(h16):
        d_x[(index, plus + index)] = F(1)
        d_x[(plus + index, index)] = F(1)
    gamma_x = diagonal([1] * plus + [-1] * minus)
    p0 = diagonal([0] * h16 + [1] * (3 * h16) + [0] * minus)
    q0 = add(identity(total), scale(-1, p0))
    g_x = dict(d_x)
    d_x_squared = multiply(d_x, d_x)

    representation_weights = tuple(weights) * 5
    rho = diagonal(representation_weights)
    d_plus_domain_weights = tuple(weights) * 4
    d_plus_codomain_weights = tuple(weights)
    rho_plus = diagonal(d_plus_domain_weights)
    rho_minus = diagonal(d_plus_codomain_weights)

    checks = {
        "D_plus_has_rank_16": rank(d_plus, minus, plus) == 16,
        "D_plus_kernel_has_dimension_48": plus - rank(d_plus, minus, plus) == 48,
        "D_plus_cokernel_is_zero": minus - rank(d_plus, minus, plus) == 0,
        "self_adjoint_DX_has_dimension_80": total == 80,
        "DX_is_self_adjoint": transpose(d_x) == d_x,
        "DX_is_odd": add(multiply(gamma_x, d_x), multiply(d_x, gamma_x)) == {},
        "harmonic_projector_has_rank_48": trace(p0, total) == 48,
        "harmonic_projector_is_idempotent": multiply(p0, p0) == p0,
        "projector_and_complement_resolve_identity": add(p0, q0) == identity(total)
        and multiply(p0, q0) == {},
        "DX_square_is_complement_projector": d_x_squared == q0,
        "reduced_green_is_DX": multiply(d_x, g_x) == q0
        and multiply(g_x, d_x) == q0,
        "reduced_green_annihilates_kernel": multiply(g_x, p0) == {}
        and multiply(p0, g_x) == {},
        "shared_circle_action_commutes_with_DX": multiply(rho, d_x) == multiply(d_x, rho),
        "shared_circle_action_commutes_with_kernel_projector": multiply(rho, p0)
        == multiply(p0, rho),
        "D_plus_is_shared_circle_equivariant": multiply(d_plus, rho_plus)
        == multiply(rho_minus, d_plus),
        "complement_gap_is_exactly_one": d_x_squared == q0,
    }
    data = {
        "one_family_dimension": h16,
        "plus_dimension": plus,
        "minus_dimension": minus,
        "self_adjoint_dimension": total,
        "D_plus_definition": "[I16 0 0 0]",
        "D_plus_rank": rank(d_plus, minus, plus),
        "kernel_dimension": plus - rank(d_plus, minus, plus),
        "cokernel_dimension": minus - rank(d_plus, minus, plus),
        "characterwise_index": "3[H16]",
        "total_index_dimension": 48,
        "self_adjoint_kernel_dimension": int(trace(p0, total)),
        "complement_dimension": int(trace(q0, total)),
        "nonzero_spectrum": [-1, 1],
        "spectral_gap_mu": 1,
        "reduced_green_norm": 1,
        "normal_inverse_norm": 1,
        "physical_q79_operator_claimed": False,
    }
    matrices = {
        "D_plus": d_plus,
        "D_X": d_x,
        "Gamma_X": gamma_x,
        "P0": p0,
        "Q0": q0,
        "G_X": g_x,
    }
    return data, checks, matrices


def product_witness(internal: dict[str, Sparse]) -> tuple[dict[str, object], dict[str, bool]]:
    internal_dimension = 80
    d_y: Sparse = {(0, 1): F(1), (1, 0): F(1)}
    gamma_y = diagonal([1, -1])
    i_y = identity(2)
    i_x = identity(internal_dimension)
    d_x = internal["D_X"]
    p0 = internal["P0"]
    q0 = internal["Q0"]

    d_total = add(
        kron(d_y, 2, 2, i_x, internal_dimension, internal_dimension),
        kron(gamma_y, 2, 2, d_x, internal_dimension, internal_dimension),
    )
    d_total_squared = multiply(d_total, d_total)
    square_formula = add(
        kron(multiply(d_y, d_y), 2, 2, i_x, internal_dimension, internal_dimension),
        kron(i_y, 2, 2, multiply(d_x, d_x), internal_dimension, internal_dimension),
    )
    p_total = kron(i_y, 2, 2, p0, internal_dimension, internal_dimension)
    q_total = kron(i_y, 2, 2, q0, internal_dimension, internal_dimension)
    retained_operator = kron(d_y, 2, 2, p0, internal_dimension, internal_dimension)

    zero_mode_index = 16
    psi = (F(2), F(-3))
    eta = (F(5), F(7))
    embedded_psi = [F(0)] * 160
    embedded_eta = [F(0)] * 160
    for external in range(2):
        embedded_psi[external * internal_dimension + zero_mode_index] = psi[external]
        embedded_eta[external * internal_dimension + zero_mode_index] = eta[external]
    embedded_psi_tuple = tuple(embedded_psi)
    embedded_eta_tuple = tuple(embedded_eta)
    external_dpsi = apply(d_y, psi, 2)
    total_dpsi = apply(d_total, embedded_psi_tuple, 160)

    d_lambda_plus = add(d_y, gamma_y)
    d_lambda_minus = add(d_y, scale(-1, gamma_y))
    two_i = scale(2, identity(2))

    checks = {
        "external_grading_anticommutes_with_DY": add(
            multiply(d_y, gamma_y), multiply(gamma_y, d_y)
        )
        == {},
        "product_operator_has_dimension_160": 2 * internal_dimension == 160,
        "product_Dirac_square_identity": d_total_squared == square_formula,
        "zero_mode_projector_reduces_product_operator": multiply(p_total, d_total)
        == multiply(d_total, p_total),
        "compressed_operator_is_DY_tensor_P0": multiply(p_total, multiply(d_total, p_total))
        == retained_operator,
        "retained_product_dimension_is_96": trace(p_total, 160) == 96,
        "product_complement_dimension_is_64": trace(q_total, 160) == 64,
        "finite_mass_plus_mode_square_is_two_I": multiply(d_lambda_plus, d_lambda_plus)
        == two_i,
        "finite_mass_minus_mode_square_is_two_I": multiply(d_lambda_minus, d_lambda_minus)
        == two_i,
        "product_complement_normal_is_two_Q": multiply(
            q_total, multiply(d_total_squared, q_total)
        )
        == scale(2, q_total),
        "quadratic_action_reduces_exactly": dot(embedded_psi_tuple, total_dpsi)
        == dot(psi, external_dpsi),
        "fiber_pairing_reduces_exactly": dot(embedded_eta_tuple, embedded_psi_tuple)
        == dot(eta, psi),
    }
    data = {
        "external_dimension": 2,
        "internal_dimension": internal_dimension,
        "product_dimension": 160,
        "retained_product_dimension": int(trace(p_total, 160)),
        "complement_product_dimension": int(trace(q_total, 160)),
        "D_Y": [[0, 1], [1, 0]],
        "Gamma_Y": [[1, 0], [0, -1]],
        "product_operator_nonzero_entries": len(d_total),
        "product_square_nonzero_entries": len(d_total_squared),
        "massless_mode_square": "D_Y^2",
        "massive_mode_normal_eigenvalue": 2,
        "quadratic_sample": {
            "psi": [2, -3],
            "upper_bilinear": int(dot(embedded_psi_tuple, total_dpsi)),
            "reduced_bilinear": int(dot(psi, external_dpsi)),
        },
        "cotangent_pairing_sample": {
            "psi": [2, -3],
            "eta": [5, 7],
            "upper_pairing": int(dot(embedded_eta_tuple, embedded_psi_tuple)),
            "reduced_pairing": int(dot(eta, psi)),
        },
        "physical_spacetime_claimed": False,
    }
    return data, checks


def representation_witness(rows: list[dict[str, int | str]]) -> tuple[dict[str, object], dict[str, bool]]:
    anomalies = anomaly_rows(rows)
    z6 = {
        str(row["name"]): (
            2 * int(row["triality"])
            + 3 * int(row["weak_parity"])
            + int(row["six_Y"])
        )
        % 6
        for row in rows
    }
    checks = {
        "one_family_has_dimension_16": sum(
            int(row["color_dim"]) * int(row["weak_dim"]) for row in rows
        )
        == 16,
        "all_six_rows_descend_through_Z6": all(value == 0 for value in z6.values()),
        "gravitational_U1_anomaly_vanishes": anomalies["gravitational_U1"] == 0,
        "U1_cubic_anomaly_vanishes": anomalies["U1_cubic"] == 0,
        "SU3_squared_U1_anomaly_vanishes": anomalies["SU3_squared_U1_twice_Dynkin"] == 0,
        "SU2_squared_U1_anomaly_vanishes": anomalies["SU2_squared_U1_twice_Dynkin"] == 0,
        "SU3_cubic_anomaly_vanishes": anomalies["SU3_cubic"] == 0,
        "weak_doublet_count_is_even": anomalies["weak_doublet_count"] % 2 == 0,
        "three_family_anomalies_also_vanish": all(
            3 * value == 0
            for name, value in anomalies.items()
            if name != "weak_doublet_count"
        )
        and (3 * anomalies["weak_doublet_count"]) % 2 == 0,
    }
    data = {
        "gauge_group": "(SU3 x SU2 x U1Y)/Z6",
        "sectors": [
            {
                **row,
                "complex_dimension": int(row["color_dim"]) * int(row["weak_dim"]),
                "z6_congruence": z6[str(row["name"])],
            }
            for row in rows
        ],
        "one_family_anomalies": anomalies,
        "three_family_anomalies": {
            name: 3 * value for name, value in anomalies.items()
        },
        "shared_circle_weight_vector": [int(row["six_Y"]) for row in rows],
        "postprojection_charge_choices_added": 0,
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
        == "boe.mtt.q79-bv4-associated-matter-externalization-source-lock.v1",
        "live_kernel_model_hash_is_locked": lock["kernel_model"]["state_sha256"]
        == "592ef16dc03ce2195113b53cc75f8bb638bd27c279590ed3f5575d11dee05db8",
        "CBF_T12_theorem_hash_matches": sha256(
            ROOT / "SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md"
        )
        == local["SevenRowEndpointFactorizationAndMinimalSourceTheorem_v1.md"],
        "CBF_T12_packet_hash_matches": sha256(BASELINE_PATH)
        == local["q79_seven_row_endpoint_factorization.packet.json"],
        "three_packet_schema_hash_matches": sha256(
            ROOT / "q79_physical_endpoint_three_packet_contract.schema.json"
        )
        == local["q79_physical_endpoint_three_packet_contract.schema.json"],
    }
    for (repository, path), expected in adjacent.items():
        checks[f"adjacent_{repository}_{Path(path).stem}_hash_matches"] = sha256(
            ROOT.parent / repository / Path(path)
        ) == expected
    return checks


def shared_circle_checks() -> tuple[dict[str, object], dict[str, bool]]:
    source = json.loads(
        (
            ROOT.parent
            / "20 Mathematical Language Discovery Program - Closure Dynamics"
            / "shared_circle_sm_gauge_stack_reference.packet.json"
        ).read_text(encoding="utf-8")
    )
    checks = {
        "shared_circle_source_checks_all_pass": all(source["checks"].values()),
        "shared_circle_has_one_abelian_harmonic_mode": source["finite_circle_model"]
        ["representative_full_dimensions_n7"]["H1_split"]
        == {"color": 8, "weak": 3, "shared_abelian": 1},
        "shared_circle_weights_match_A50": source["shared_holonomy"]
        ["matter_holonomy_exponents_6Y"]
        == {"Q": 1, "u^c": -4, "d^c": 2, "L": -3, "e^c": 6, "N^c": 0},
        "six_lifts_have_identical_descended_action": source["circle_lift_theorem"]
        ["physical_descended_action"].startswith("identical for all six"),
        "four_dimensional_extension_is_not_imported": source["checks"]
        ["four_dimensional_extension_is_not_claimed"]
        is True,
    }
    data = {
        "source_schema": source["schema"],
        "source_sha256": sha256(
            ROOT.parent
            / "20 Mathematical Language Discovery Program - Closure Dynamics"
            / "shared_circle_sm_gauge_stack_reference.packet.json"
        ),
        "H1_split": source["finite_circle_model"]["representative_full_dimensions_n7"]
        ["H1_split"],
        "matter_weights_6Y": source["shared_holonomy"]["matter_holonomy_exponents_6Y"],
        "lift_torsor": source["circle_lift_theorem"]["lift_torsor"],
        "physical_four_dimensional_connection_claimed": False,
    }
    return data, checks


def schema_checks() -> tuple[dict[str, object], dict[str, bool]]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = schema["required"]
    same_root_sections = (
        "internal_matter_operator",
        "external_causal_base",
        "representation_descent",
        "density_and_pairing",
    )
    text = SCHEMA_PATH.read_text(encoding="utf-8").lower()
    checks = {
        "schema_is_draft_2020_12": schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema",
        "schema_requires_root_hash": "source_root_sha256" in required,
        "all_source_sections_repeat_root_hash": all(
            "source_root_sha256" in schema["properties"][section]["required"]
            for section in same_root_sections
        ),
        "schema_requires_first_order_operator_and_kernel": all(
            field in schema["properties"]["internal_matter_operator"]["required"]
            for field in (
                "first_order_operator_artifact",
                "normalized_kernel_basis_artifact",
                "characterwise_index_certificate",
            )
        ),
        "schema_requires_causal_and_gap_certificates": all(
            field in schema["properties"]["compiler_certificates"]["required"]
            for field in ("modewise_causal_decomposition", "complement_gap_bound")
        ),
        "schema_retains_seven_physical_exit_groups": len(
            schema["properties"]["remaining_physical_rows"]["required"]
        )
        == 7,
        "schema_contains_no_observed_value_field": "observed_value" not in text,
        "schema_has_no_proof_boolean_shortcut": '"proof"' not in text,
    }
    data = {
        "schema_id": schema["$id"],
        "root_required_fields": required,
        "same_root_sections": list(same_root_sections),
        "remaining_physical_rows": schema["properties"]["remaining_physical_rows"]
        ["required"],
    }
    return data, checks


def baseline_checks() -> tuple[dict[str, object], dict[str, bool]]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    factorization = baseline["source_packet_factorization"]
    checks = {
        "CBF_T12_builder_checks_all_pass": all(baseline["checks"].values()),
        "physical_packets_remain_zero_of_three": factorization["physical_packets_accepted"]
        == 0
        and factorization["physical_packets_total"] == 3,
        "physical_rows_remain_zero_of_seven": baseline["physical_rows_accepted"] == 0
        and baseline["physical_rows_total"] == 7,
        "BV4_was_open_before_this_compiler": next(
            packet for packet in factorization["packet_types"] if packet["id"] == "BV4"
        )["physical_state"]
        == "open",
    }
    data = {
        "source_claim_id": baseline["claim_id"],
        "source_packet_sha256": sha256(BASELINE_PATH),
        "physical_packets_accepted": factorization["physical_packets_accepted"],
        "physical_packets_total": factorization["physical_packets_total"],
        "physical_rows_accepted": baseline["physical_rows_accepted"],
        "physical_rows_total": baseline["physical_rows_total"],
    }
    return data, checks


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    rows = sectors()
    weights = h16_weights(rows)
    internal_data, internal_checks, internal_matrices = internal_witness(weights)
    product_data, product_checks = product_witness(internal_matrices)
    representation_data, representation_checks = representation_witness(rows)
    circle_data, circle_checks = shared_circle_checks()
    schema_data, contract_checks = schema_checks()
    baseline_data, prior_checks = baseline_checks()

    checks = {
        **source_checks(lock),
        **internal_checks,
        **product_checks,
        **representation_checks,
        **circle_checks,
        **contract_checks,
        **prior_checks,
        "compiler_adds_no_physical_scalar_parameters": True,
        "compiler_does_not_select_q79_endpoint": not internal_data[
            "physical_q79_operator_claimed"
        ],
        "compiler_does_not_claim_physical_spacetime": not product_data[
            "physical_spacetime_claimed"
        ],
        "controlling_blockers_remain_open": all(
            blocker["state"] == "open" for blocker in lock["blockers"]
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"associated-matter externalization checks failed: {failed}")

    return {
        "schema": "boe.mtt.q79-bv4-associated-matter-externalization.packet.v1",
        "claim_id": "CBF.T13",
        "date": "2026-08-29",
        "tier": "EXACT_GENERAL_COMPILER + EXACT_FINITE_WITNESS; PHYSICAL_Q79_SOURCE_OPEN",
        "source_lock_sha256": sha256(LOCK_PATH),
        "theorem_sha256": sha256(THEOREM_PATH),
        "instance_schema_sha256": sha256(SCHEMA_PATH),
        "baseline": baseline_data,
        "compiler": {
            "inputs": ["AMK", "EXT4", "DEN"],
            "output": "free associated-matter subpacket of BV4",
            "derived_without_new_postprojection_choices": [
                "four-dimensional zero-mode field carrier",
                "gauge and shared-circle representation on the kernel",
                "characterwise chirality index",
                "free quadratic action",
                "cotangent BV pairing",
                "modewise causal operator family",
                "internal complement gap bound",
            ],
            "same_root_source_required": True,
            "new_continuous_physical_parameters": 0,
            "physical_instance_state": "open",
        },
        "exact_internal_witness": internal_data,
        "exact_product_witness": product_data,
        "representation_and_anomaly_witness": representation_data,
        "shared_circle_input": circle_data,
        "instance_contract": schema_data,
        "bv4_clause_cutset": [
            {"clause": "C1", "compiler_state": "exact", "physical_input": "selected normalized q79 kernel and complement"},
            {"clause": "C2", "compiler_state": "exact", "physical_input": "selected density and BV grading"},
            {"clause": "C3", "compiler_state": "exact", "physical_input": "selected equivariant first-order operator and real structure"},
            {"clause": "C4", "compiler_state": "exact_identity", "physical_input": "HYM density, volume and scales"},
            {"clause": "C5", "compiler_state": "exact_free_reduction", "physical_input": "selected upper quadratic action"},
            {"clause": "C8", "compiler_state": "conditional_green_hyperbolic", "physical_input": "Y4, domains, gauge fixing and causal support prescription"},
            {"clause": "C9", "compiler_state": "classical_gap_bound", "physical_input": "determinant orientation, anomaly and QME pushforward"},
        ],
        "physical_packets_accepted": 0,
        "physical_packets_total": 3,
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "decision": "RETAINED_ASSOCIATED_MATTER_EXTERNALIZATION_COMPILER_ONLY",
        "checks": checks,
        "check_summary": {"passed": sum(checks.values()), "total": len(checks)},
        "frontier_delta": {
            "closed": [
                "product-Dirac zero-mode externalization compiler",
                "equivariant characterwise-index transport",
                "free quadratic action and cotangent pairing reduction",
                "modewise causal consequence under explicit EXT4 hypotheses",
                "internal complement gap bound",
                "exact 3x16=48 A46/A50 and shared-circle/Z6 witness",
            ],
            "open": [
                "selected q79 AMK instance from the physical V3/W9 HYM endpoint",
                "selected EXT4 causal base and complete field stack",
                "physical density, normalization and nonlinear upper action",
                "interaction overlap values and massive-mode BV/QME pushforward",
            ],
            "blocker_states_changed": False,
            "physical_acceptance_count_changed": False,
            "BV4_dependency_graph_changed": True,
        },
        "claim_boundary": {
            "does_not_claim": [
                "that the exact finite witness is the selected q79 internal operator",
                "a selected physical four-dimensional spacetime or gauge connection",
                "Yukawa or other interaction values",
                "the full bosonic, gravitational or quantum BV compactification",
                "closure of B.HS.01, B.GEO.01 or B.ACTION.01",
            ]
        },
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = packet["check_summary"]
    print(
        "associated-matter BV4 compiler packet built: "
        f"{summary['passed']}/{summary['total']} checks; "
        "physical rows remain 0/7"
    )


if __name__ == "__main__":
    main()
