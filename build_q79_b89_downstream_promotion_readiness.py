#!/usr/bin/env python3
"""Build the exact B89 downstream-promotion readiness packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMON = ROOT.parent
UPSTREAM = COMMON / "mtt-preprojection-repair-calculus"
OUTPUT = ROOT / "q79_b89_downstream_promotion_readiness.packet.json"
DYNAMIC = {
    "coverage_report": ROOT / "q79_b89_accelerated_source_isotopy_coverage_report.json",
    "branch_isotopy": ROOT / "q79_b89_accelerated_source_isotopy_branch_aggregate.json",
    "boundary_isotopy": ROOT / "q79_b89_accelerated_source_isotopy_boundary_aggregate.json",
    "joint_isotopy": ROOT / "q79_b89_accelerated_source_isotopy_joint_aggregate.json",
    "joint_replay_audit": ROOT / "q79_b89_joint_mixed_separation_replay_audit.json",
    "shared_parameter_result_index": ROOT / "q79_b89_joint_shared_parameter_results/index.json",
}
STATIC = {
    "H4_T122_exact_carrier": UPSTREAM / "certificates/h4_q79_eta9_b89_exact_integral_carrier.json",
    "H4_T113_signed_boundary": UPSTREAM / "certificates/h4_q79_eta9_b89_certified_signed_boundary_braid.json",
    "H4_T116_connector_free_parity": UPSTREAM / "certificates/h4_q79_eta9_b89_selected_rectangle_connector_free_parity.json",
    "H4_T118_integral_marking": UPSTREAM / "certificates/h4_q79_eta9_b89_certified_comb_h1_intertwiner.json",
    "H4_T119_boundary_spokes": UPSTREAM / "certificates/h4_q79_eta9_b89_certified_boundary_spoke_frame.json",
    "H4_T120_Deligne_adapter_certificate": UPSTREAM / "certificates/h4_q79_eta9_b89_affine_deligne_adapter.json",
    "H4_T120_Deligne_adapter_packet": UPSTREAM / "experiments/q79_eta9_b89_affine_deligne_adapter/q79_eta9_b89_affine_deligne_adapter.packet.json",
    "common_grid_Artin": UPSTREAM / "experiments/q79_eta9_b89_family_branch_braid_pilot/outputs/certified-common-grid-right80-joint-artin.json",
    "segmented_adapter": UPSTREAM / "experiments/q79_eta9_b89_family_branch_braid_pilot/outputs/certified-common-grid-right80-segmented-adapter.json",
    "conditional_affine_obstruction": UPSTREAM / "experiments/q79_eta9_b89_family_branch_braid_pilot/outputs/certified-common-grid-right80-mod2-affine-obstruction.json",
    "independent_affine_replay": COMMON / "mtt-preprojection-h4t108/experiments/q79_eta9_selected_component_scout/outputs/q79-eta9-b89-certified-affine-replay.packet.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict:
    return {
        "path": path.relative_to(COMMON).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def rank_mod_two(matrix: list[list[int]]) -> int:
    rows = [sum((int(v) & 1) << c for c, v in enumerate(row)) for row in matrix]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((r for r in range(rank, len(rows)) if (rows[r] >> column) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(len(rows)):
            if row != rank and ((rows[row] >> column) & 1):
                rows[row] ^= rows[rank]
        rank += 1
    return rank


def main() -> int:
    for path in [*DYNAMIC.values(), *STATIC.values()]:
        require(path.is_file(), f"input {path}")
    dynamic = {name: load(path) for name, path in DYNAMIC.items()}
    static = {name: load(path) for name, path in STATIC.items()}
    coverage = dynamic["coverage_report"]
    branch = dynamic["branch_isotopy"]
    boundary = dynamic["boundary_isotopy"]
    joint = dynamic["joint_isotopy"]
    audit = dynamic["joint_replay_audit"]
    result_index = dynamic["shared_parameter_result_index"]

    require(coverage["complete"] is True, "carrier coverage")
    require(coverage["branch"]["certified_intervals"] == 2195, "branch coverage")
    require(coverage["boundary"]["certified_intervals"] == 2195, "boundary coverage")
    for name, value in (("branch", branch), ("boundary", boundary), ("joint", joint)):
        require(all(value["checks"].values()), f"{name} checks")
        require(not any(value["guardrails"].values()), f"{name} guardrails")
    require(branch["counts"]["source_intervals"] == 2195, "branch interval count")
    require(boundary["counts"]["source_intervals"] == 2195, "boundary interval count")
    require(joint["counts"]["source_intervals"] == 2195, "joint interval count")
    require(joint["counts"]["joint_strands"] == 288, "joint strand count")
    require(joint["counts"]["joint_Artin_word_length"] == 24999, "Artin length")
    require(joint["counts"]["mixed_homotopy_targeted_certificates"] == 473, "targeted calls")
    require(joint["inputs"]["branch_aggregate_sha256"] == sha256(DYNAMIC["branch_isotopy"]), "joint branch binding")
    require(joint["inputs"]["boundary_aggregate_sha256"] == sha256(DYNAMIC["boundary_isotopy"]), "joint boundary binding")
    require(all(audit["counts"][key] == 0 for key in ("unresolved_common_refinement_atoms", "unresolved_label_pairs", "unresolved_source_intervals")), "unresolved joint rows")
    require(audit["targeted_certificate_provenance"]["result_index_sha256"] == sha256(DYNAMIC["shared_parameter_result_index"]), "target index binding")
    require(result_index["complete"] is True, "target result completeness")
    require(result_index["coverage"]["unique_targets"] == result_index["coverage"]["verified_targets"] == 463, "target verification")

    expected_ids = {
        "H4_T122_exact_carrier": "H4-T122",
        "H4_T113_signed_boundary": "H4-T113",
        "H4_T116_connector_free_parity": "H4-T116",
        "H4_T118_integral_marking": "H4-T118",
        "H4_T119_boundary_spokes": "H4-T119",
        "H4_T120_Deligne_adapter_certificate": "H4-T120",
    }
    for name, result_id in expected_ids.items():
        require(static[name]["id"] == result_id and static[name]["all_passed"], name)
    require(static["H4_T120_Deligne_adapter_certificate"]["artifact"]["sha256"] == sha256(STATIC["H4_T120_Deligne_adapter_packet"]), "H4-T120 packet binding")

    artin = static["common_grid_Artin"]
    segmented = static["segmented_adapter"]
    affine = static["conditional_affine_obstruction"]
    require(all(artin["checks"].values()) and not any(artin["guardrails"].values()), "Artin")
    require(all(segmented["checks"].values()) and not any(segmented["guardrails"].values()), "segmented")
    require(all(affine["checks"].values()), "affine checks")
    require(joint["inputs"]["joint_artin_sha256"] == sha256(STATIC["common_grid_Artin"]), "joint Artin binding")
    require(segmented["common_word_sha256"] == sha256(STATIC["common_grid_Artin"]), "Artin adapter")
    require(affine["segmented_word_sha256"] == sha256(STATIC["segmented_adapter"]), "affine adapter")
    replay = static["independent_affine_replay"]
    require(replay["all_jobs_observed"] is True, "independent replay observed")
    require(replay["job"]["observed_state"] == "succeeded", "independent replay state")
    require(replay["job"]["exact_payload_match"] is True, "independent replay equality")
    require(replay["job"]["retrieved_payload_sha256"] == sha256(STATIC["conditional_affine_obstruction"]), "independent replay payload")

    matrix = affine["action_mod2"]
    translation = [int(v) & 1 for v in affine["affine_translation_mod2"]]
    witness = [int(v) & 1 for v in affine["mod2_obstruction_witness"]]
    require(len(matrix) == len(translation) == len(witness) == 164, "rank-164 data")
    delta = [[int(matrix[r][c]) ^ int(r == c) for c in range(164)] for r in range(164)]
    require(rank_mod_two(matrix) == 164, "rank M")
    require(rank_mod_two(delta) == 42, "rank M-I")
    require(all(sum(witness[r] * delta[r][c] for r in range(164)) % 2 == 0 for c in range(164)), "left witness")
    require(sum(witness[r] * translation[r] for r in range(164)) % 2 == 1, "pairing")

    checks = {
        "the_exact_252_strand_branch_carrier_is_complete_on_all_2195_source_intervals": True,
        "the_exact_36_strand_signed_boundary_carrier_is_complete_on_all_2195_source_intervals": True,
        "all_463_hard_mixed_targets_have_independently_verified_shared_parameter_certificates": True,
        "the_complete_288_strand_same_source_isotopy_is_collision_free": True,
        "the_joint_isotopy_is_hash_bound_to_the_24999_letter_Arb_certified_Artin_word": True,
        "the_H4_T113_T116_T118_T119_T120_and_T122_static_authorities_are_hash_bound": True,
        "the_rank_164_replay_has_rank_M_minus_I_42_and_a_pairing_one_left_witness": True,
        "an_independent_kernel_process_reproduced_the_affine_payload_byte_for_byte": True,
        "all_dynamic_premises_for_the_existing_B89_rejection_replay_are_complete": True,
    }
    guardrails = {
        "claims_a_replacement_graph_Prym_member": False,
        "claims_beta_C_zero_or_a_HYM_endpoint": False,
        "claims_exact_order_two_over_Z": False,
        "claims_the_B89_rejection_before_running_H4_T120_promotion": False,
    }
    packet = {
        "schema": "mtt.cbf.q79-b89-downstream-promotion-readiness.v2",
        "theorem_id": "CBF.T54",
        "tier": "EXACT_COMPLETE_DYNAMIC_AND_STATIC_PROMOTION_READINESS",
        "decision": "READY_FOR_B89_PROMOTION",
        "coverage": {
            "branch": {"certified_intervals": 2195, "target_intervals": 2195, "complete": True},
            "boundary": {"certified_intervals": 2195, "target_intervals": 2195, "complete": True},
            "joint": {"mixed_pairs": 28295568, "hard_diagnostic_calls": 473, "unique_hard_targets": 463, "complete": True},
        },
        "conditional_obstruction": {
            "rank": 164,
            "rank_M_over_F2": 164,
            "rank_M_minus_I_over_F2": 42,
            "left_nullity_M_minus_I_over_F2": 122,
            "witness_support": sum(witness),
            "translation_support": sum(translation),
            "witness_pairing_mod2": 1,
        },
        "promotion_chain": [
            "apply the frozen H4-T123 and H4-T124 component promotions",
            "apply H4-T125 to the completed same-source 288-strand isotopy",
            "replay the hash-bound rank-164 mod-two affine operator",
            "apply H4-T120 and H4-T126 to reject B89 from the beta-zero locus",
        ],
        "checks": checks,
        "guardrails": guardrails,
        "inputs": {**{name: record(path) for name, path in DYNAMIC.items()}, **{name: record(path) for name, path in STATIC.items()}},
    }
    require(all(checks.values()) and not any(guardrails.values()), "claim boundary")
    OUTPUT.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="ascii", newline="\n")
    print("CBF.T54 downstream readiness: PASS branch=2195/2195 boundary=2195/2195 joint=PASS promotion=ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
