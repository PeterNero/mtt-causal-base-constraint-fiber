#!/usr/bin/env python3
"""Independent verifier for the provider-neutral q79-necessity packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "provider_neutral_projection_source_quotient.packet.json"
SOURCE_LOCK = ROOT / "provider_neutral_projection_source_lock.json"
SCHEMA = ROOT / "provider_neutral_physical_source_contract.schema.json"
THEOREM = ROOT / "ProviderNeutralProjectionSourceQuotientAndQ79NecessityTheorem_v1.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    columns = transpose(right)
    return [[sum(x * y for x, y in zip(row, col)) for col in columns] for row in left]


def identity(size: int) -> list[list[int]]:
    return [[int(row == col) for col in range(size)] for row in range(size)]


def diagonal(values: list[int]) -> list[list[int]]:
    return [[values[row] if row == col else 0 for col in range(len(values))] for row in range(len(values))]


def operator(scale: int) -> list[list[int]]:
    result = [[0 for _ in range(80)] for _ in range(80)]
    for index in range(16):
        result[index][64 + index] = scale
        result[64 + index][index] = scale
    return result


def family_permutation() -> list[int]:
    permutation = list(range(80))
    for family in range(3):
        for coordinate in range(16):
            permutation[16 + 16 * family + coordinate] = (
                16 + 16 * ((family + 1) % 3) + coordinate
            )
    return permutation


def permutation_matrix(permutation: list[int]) -> list[list[int]]:
    result = [[0 for _ in permutation] for _ in permutation]
    for source, target in enumerate(permutation):
        result[target][source] = 1
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_local_sources(source_lock: dict[str, Any]) -> int:
    checks = 0
    for entry in source_lock["local_sources"]:
        path = (ROOT / entry["path"]).resolve()
        require(path.is_file(), f"missing source: {entry['path']}")
        require(sha256(path) == entry["sha256"], f"source hash mismatch: {entry['path']}")
        checks += 1
    return checks


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    checks = verify_local_sources(source_lock)

    require(packet["schema"] == "boe.mtt.provider-neutral-projection-source-quotient.v1", "packet schema")
    checks += 1
    require(packet["claim_id"] == "CBF.T14", "claim id")
    checks += 1
    require(packet["decision"] == "Q79_NOT_LOGICALLY_REQUIRED_PHYSICAL_SOURCE_STILL_REQUIRED", "decision")
    checks += 1
    require(packet["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash")
    checks += 1
    require(packet["contract_schema_sha256"] == sha256(SCHEMA), "contract hash")
    checks += 1
    require(packet["theorem_sha256"] == sha256(THEOREM), "theorem hash")
    checks += 1

    provider_enum = schema["properties"]["root_source"]["properties"]["provider_kind"]["enum"]
    require("q79_hull_strominger" in provider_enum, "q79 provider missing")
    checks += 1
    require("direct_closure_repair" in provider_enum, "direct repair provider missing")
    checks += 1
    require("finite_spectral_action" in provider_enum, "finite spectral provider missing")
    checks += 1
    require(schema["properties"]["causal_base"]["properties"]["dimension"]["const"] == 4, "causal base dimension")
    checks += 1
    require(len(schema["properties"]["constraint_fiber"]["required"]) == 6, "constraint-fiber rows")
    checks += 1

    d1 = operator(1)
    d2 = operator(2)
    projector = diagonal([0] * 16 + [1] * 48 + [0] * 16)
    w = permutation_matrix(family_permutation())
    wt = transpose(w)
    one_family = [1] * 6 + [-4] * 3 + [2] * 3 + [-3] * 2 + [6] + [0]
    hypercharge = diagonal(one_family + one_family * 3 + one_family)
    zero = [[0 for _ in range(80)] for _ in range(80)]

    require(matmul(projector, projector) == projector, "projector idempotence")
    checks += 1
    require(sum(projector[index][index] for index in range(80)) == 48, "kernel rank")
    checks += 1
    require(matmul(w, wt) == identity(80), "unitarity")
    checks += 1
    require(matmul(w, matmul(w, w)) == identity(80), "order three")
    checks += 1
    require(matmul(w, matmul(d1, wt)) == d1, "operator intertwiner")
    checks += 1
    require(matmul(w, matmul(projector, wt)) == projector, "projector intertwiner")
    checks += 1
    require(matmul(w, matmul(hypercharge, wt)) == hypercharge, "hypercharge intertwiner")
    checks += 1
    require(matmul(projector, matmul(d1, projector)) == zero, "scale-one free projection")
    checks += 1
    require(matmul(projector, matmul(d2, projector)) == zero, "scale-two free projection")
    checks += 1
    require(matmul(d1, d1) != matmul(d2, d2), "complement spectrum countermodel")
    checks += 1

    witness = packet["exact_equivalence_witness"]
    require(witness["internal_dimension"] == 80, "witness dimension")
    checks += 1
    require(witness["kernel_dimension"] == 48, "witness kernel")
    checks += 1
    require(witness["family_cycle_permutation"] == family_permutation(), "permutation payload")
    checks += 1
    require(witness["source_a"]["benchmark_only"], "source A boundary")
    checks += 1
    require(witness["source_b"]["benchmark_only"], "source B boundary")
    checks += 1

    threshold = packet["no_source_no_values_countermodels"]["threshold"]
    require(threshold["source_1_complement_gap"] == 1, "gap one")
    checks += 1
    require(threshold["source_2_complement_gap"] == 2, "gap two")
    checks += 1
    require(threshold["shared_projected_internal_operator"], "shared free projection")
    checks += 1

    interaction = packet["no_source_no_values_countermodels"]["interaction"]
    require(interaction["source_1_tensor_norm_squared"] == 1, "tensor norm one")
    checks += 1
    require(interaction["source_2_tensor_norm_squared"] == 4, "tensor norm four")
    checks += 1
    require(interaction["unitary_invariant_norms_differ"], "interaction no-go")
    checks += 1

    classification = packet["q79_classification"]
    require(classification["A11_discrete_q79_branch_remains_established"], "A11 preservation")
    checks += 1
    require(not classification["q79_required_by_projection_formulas"], "q79 necessity verdict")
    checks += 1
    require(classification["q79_sufficiency_for_selected_physics"] == "OPEN", "q79 sufficiency boundary")
    checks += 1
    require(classification["q79_uniqueness_as_physical_provider"] == "NOT_ESTABLISHED", "q79 uniqueness boundary")
    checks += 1
    require(classification["physical_bypass_status"] == "FORMAL_BYPASS_EXACT_PHYSICAL_BYPASS_OPEN", "bypass boundary")
    checks += 1

    require(packet["physical_packets_accepted"] == 0, "packet acceptance")
    checks += 1
    require(packet["physical_rows_accepted"] == 0, "row acceptance")
    checks += 1
    require(packet["frontier_delta"]["route_specific_blockers_remain_open"] == ["B.HS.01", "B.GEO.01", "B.OP.01", "B.ACTION.01"], "blocker boundary")
    checks += 1

    require(all(packet["checks"].values()), "builder check failure recorded")
    checks += 1
    require(packet["check_summary"]["passed"] == packet["check_summary"]["total"], "builder summary")
    checks += 1
    require(packet["check_summary"]["failed"] == [], "builder failed list")
    checks += 1

    print(f"independent provider-neutral source quotient verification passed: {checks}/{checks}")


if __name__ == "__main__":
    main()
