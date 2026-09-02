"""Independently verify the CBF.T62 binary-SpinC root-stack compiler packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "q79_binary_spinc_pauli_rootstack_compiler.packet.json"
THEOREM = ROOT / "Q79BinarySpinCPauliRootStackCompilerAndPhysicalSolderingCutsetTheorem_v1.md"
SOURCE_LOCK = ROOT / "q79_binary_spinc_pauli_rootstack_compiler_source_lock.json"
SCHEMA = ROOT / "q79_binary_spinc_pauli_rootstack_compiler_contract.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eye(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def trace(matrix: list[list[int]]) -> int:
    return sum(matrix[index][index] for index in range(len(matrix)))


def determinant3(matrix: list[list[int]]) -> int:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def key(matrix: list[list[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row) for row in matrix)


def require(condition: bool, name: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    passed.append(name)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    passed: list[str] = []

    require(packet["schema"] == "boe.mtt.q79-binary-spinc-pauli-rootstack-compiler.v1", "schema", passed)
    require(packet["claim_id"] == "CBF.T62", "claim", passed)
    require("FLAT_ROOTSTACK_1PLUS3" in packet["status"], "status", passed)
    require(packet["source_provenance"]["source_lock_sha256"] == sha256(SOURCE_LOCK), "source lock hash", passed)
    require(packet["source_provenance"]["theorem_sha256"] == sha256(THEOREM), "theorem hash", passed)
    require(packet["source_provenance"]["schema_sha256"] == sha256(SCHEMA), "schema hash", passed)
    require(all(row["matches"] for row in packet["source_provenance"]["locked_local_sources"]), "locked local sources", passed)
    require(len(source_lock["discovery_evidence"]) == 4, "discovery evidence", passed)
    require(not source_lock["portability"]["external_absolute_paths_required_at_runtime"], "portable source lock", passed)
    require(source_lock["portability"]["binary_and_representation_claims_are_recomputed_algebraically"], "representation replay scope", passed)
    require(source_lock["portability"]["hidden_HYM_claim_is_composed_not_reexecuted"], "HYM composition scope", passed)

    expected_a1 = [[-1, 0, 0], [0, 0, -1], [0, -1, 0]]
    expected_a2 = [[0, -1, 0], [-1, 0, 0], [0, 0, -1]]
    p23 = [[1, 0, 0], [0, 0, 1], [0, 1, 0]]
    p12 = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    pauli = packet["pauli_adjoint"]
    require(pauli["Ad_q1"] == expected_a1, "q1 adjoint", passed)
    require(pauli["Ad_q2"] == expected_a2, "q2 adjoint", passed)
    require(pauli["determinant_twisted_Ad_q1"] == p23, "literal P23", passed)
    require(pauli["determinant_twisted_Ad_q2"] == p12, "literal P12", passed)
    require(pauli["character_on_identity_transposition_three_cycle"] == [3, -1, 0], "adjoint character", passed)
    require(pauli["twisted_representation_type"] == "E_D", "E_D typing", passed)

    require(matmul(p23, p23) == eye(3), "P23 involution", passed)
    require(matmul(p12, p12) == eye(3), "P12 involution", passed)
    require(matmul(matmul(p23, p12), p23) == matmul(matmul(p12, p23), p12), "braid", passed)
    cycle = matmul(p23, p12)
    require(matmul(matmul(cycle, cycle), cycle) == eye(3), "cycle order", passed)

    compiler = packet["flat_rootstack_compiler"]
    rows = compiler["holonomy_rows"]
    require(len(rows) == 6, "six holonomies", passed)
    matrices = {key(row["sheet_matrix"]) for row in rows}
    require(len(matrices) == 6, "six distinct matrices", passed)
    require(all(key(matmul(left["sheet_matrix"], right["sheet_matrix"])) in matrices for left in rows for right in rows), "group closure", passed)
    require(sum(row["class"] == "identity" for row in rows) == 1, "identity count", passed)
    require(sum(row["class"] == "transposition" for row in rows) == 3, "transposition count", passed)
    require(sum(row["class"] == "three_cycle" for row in rows) == 2, "cycle count", passed)
    require({trace(row["sheet_matrix"]) for row in rows if determinant3(row["sheet_matrix"]) == -1} == {1}, "permutation transposition character", passed)
    require(compiler["character_on_identity_transposition_three_cycle"] == [4, 0, 1], "combined character", passed)
    require(compiler["scalar_lane"].startswith("D=det(S)=L_shared"), "shared scalar line", passed)
    require(compiler["rank_three_lane"] == "D tensor sl(S)=E_D^C", "rank-three lane", passed)
    require(compiler["new_parameter_or_selector"] is False, "no selector", passed)

    hidden = packet["hidden_HYM_compatibility"]
    require(hidden["curvature_HYM_constant_and_hidden_Hessian_unchanged"], "hidden HYM naturality", passed)
    require(hidden["selected_visible_V3"] is False, "visible endpoint guard", passed)
    require(hidden["physical_Hull_Strominger_endpoint"] is False, "HS guard", passed)
    require(packet["totalization_cutset"]["T24_supplies_T61_degree_shift"] is False, "T24 degree guard", passed)
    require(packet["source_cutset"]["open_qutrit_maps"] == ["b_v:U_v->S", "b_i:U_i->S"], "qutrit cutset", passed)
    require(packet["source_cutset"]["open_physical_soldering"] == "sigma_D:E_D^C->T^(0,1)*X", "physical soldering", passed)

    boundary = packet["physical_boundary"]
    require(boundary["B_HS_01"] == boundary["B_GEO_01"] == boundary["B_OP_01"] == "OPEN", "blocker guards", passed)
    require((boundary["physical_packets_accepted"], boundary["physical_packets_required"]) == (0, 3), "packet counter", passed)
    require((boundary["physical_rows_accepted"], boundary["physical_rows_required"]) == (0, 7), "row counter", passed)
    require(all(value == 0 for key_name, value in packet["parameter_ledger"].items() if key_name != "equivalent_unselected_root_presentations"), "parameter ledger", passed)
    require(packet["parameter_ledger"]["equivalent_unselected_root_presentations"] == 2, "root presentations", passed)
    require(all(packet["checks"].values()), "builder checks", passed)

    print(f"independent q79 binary-SpinC Pauli root-stack verification passed: {len(passed)}/{len(passed)}")


if __name__ == "__main__":
    main()
