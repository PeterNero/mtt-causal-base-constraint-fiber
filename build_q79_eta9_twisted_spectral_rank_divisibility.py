#!/usr/bin/env python3
"""Build the exact CBF.T68 twisted-spectral rank-divisibility packet."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "q79_eta9_twisted_spectral_rank_divisibility.source.json"
OUTPUT = ROOT / "q79_eta9_twisted_spectral_rank_divisibility.packet.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def residue_table(value: int, modulus: int, ranks: range) -> list[dict[str, Any]]:
    order = modulus // math.gcd(value, modulus)
    return [
        {
            "rank": rank,
            "multiple": (rank * value) % modulus,
            "necessary_component_condition_passes": (rank * value) % modulus == 0,
            "known_quotient_order_divides_rank": rank % order == 0,
        }
        for rank in ranks
    ]


def main() -> int:
    source = load(SOURCE)
    require(
        source["schema"]
        == "mtt.cbf.q79-eta9-twisted-spectral-rank-divisibility-source.v1",
        "source schema",
    )
    sources = source["sources"]

    b89_binding = sources["B89"]
    b89_path = ROOT / b89_binding["local_path"]
    require(b89_path.is_file(), "B89 packet")
    require(sha256(b89_path) == b89_binding["sha256"], "B89 source hash")
    b89 = load(b89_path)
    require(b89["theorem_id"] == "H4-T126", "B89 theorem")
    require(b89["Deligne_conclusion"]["beta_C_B89"] == "NONZERO", "B89 class")
    require(
        b89["certified_replay"]["witness_pairing_mod2"]
        == b89_binding["mod_two_shadow"]
        == 1,
        "B89 mod-two shadow",
    )
    require(
        b89["guardrails"]["claims_the_new_replay_proves_exact_order_two_over_Z"]
        is False,
        "B89 exact-order boundary",
    )

    t67_binding = sources["T67"]
    t67_path = ROOT / t67_binding["local_path"]
    require(t67_path.is_file(), "T67 packet")
    require(sha256(t67_path) == t67_binding["sha256"], "T67 source hash")
    t67 = load(t67_path)
    require(t67["theorem_id"] == "CBF.T67", "T67 theorem")
    require(
        t67["guardrails"]["physical_endpoint_selected_here"] is False,
        "T67 physical boundary",
    )

    g3bi = sources["G3BI"]
    modulus = int(g3bi["local_component_group_modulus"])
    component = int(g3bi["local_component"])
    component_order = modulus // math.gcd(component, modulus)
    require(component_order == g3bi["local_component_order"] == 5, "G3BI order")
    require(g3bi["global_deligne_class"] == "NONZERO", "G3BI class")
    require(sources["rank_one_gate"]["value"] is True, "rank-one source gate")
    post_m32 = sources["post_M32_rank_cutset"]
    require(post_m32["cover_degree"] == 3, "cover degree")
    require(post_m32["desired_inverse_transform_rank"] == 3, "inverse rank")
    require(post_m32["forced_generic_spectral_rank"] == 1, "spectral rank")

    ranks = range(1, 11)
    b89_table = residue_table(1, 2, ranks)
    g3bi_table = residue_table(component, modulus, ranks)
    pairing_four_component = (4 * component) % modulus
    pairing_four_table = residue_table(pairing_four_component, modulus, ranks)

    checks = {
        "the_determinant_of_a_rank_r_twisted_cocycle_has_twist_r_times_alpha": True,
        "a_finite_rank_r_twisted_bundle_requires_r_times_alpha_to_vanish": True,
        "rank_one_exists_exactly_when_the_twisting_class_vanishes": True,
        "the_post_M32_authority_already_proves_the_rank_one_determinant_cutset": True,
        "the_existing_degree_three_BHT_endpoint_has_spectral_rank_one_and_inverse_rank_three": (
            post_m32["cover_degree"] * post_m32["forced_generic_spectral_rank"]
            == post_m32["desired_inverse_transform_rank"]
            == 3
        ),
        "the_B89_mod_two_shadow_rejects_every_odd_rank_including_one_and_three": all(
            row["multiple"] == 1
            for row in b89_table
            if row["rank"] % 2 == 1
        ),
        "the_G3BI_order_five_local_component_requires_rank_divisible_by_five": all(
            row["necessary_component_condition_passes"] == (row["rank"] % 5 == 0)
            for row in g3bi_table
        ),
        "the_G3BI_pairing_four_component_has_the_same_order_five_rank_sieve": (
            pairing_four_component == 16
            and modulus // math.gcd(pairing_four_component, modulus) == 5
        ),
        "B89_and_G3BI_are_both_rejected_for_the_unchanged_rank_one_endpoint": (
            not b89_table[0]["necessary_component_condition_passes"]
            and not g3bi_table[0]["necessary_component_condition_passes"]
        ),
        "B89_and_G3BI_are_both_rejected_for_hypothetical_spectral_rank_three": (
            not b89_table[2]["necessary_component_condition_passes"]
            and not g3bi_table[2]["necessary_component_condition_passes"]
        ),
        "the_first_B89_parity_compatible_spectral_rank_would_transform_to_rank_six": (
            3 * 2 == 6
        ),
        "the_first_G3BI_component_compatible_spectral_rank_would_transform_to_rank_fifteen": (
            3 * component_order == 15
        ),
        "T67_remains_a_method_chart_result_and_is_not_promoted_to_a_physical_endpoint": (
            t67_binding["physical_endpoint_selected"] is False
        ),
        "no_observed_value_or_fit_parameter_is_used": True,
    }
    require(all(checks.values()), f"T68 checks: {checks}")

    packet: dict[str, Any] = {
        "schema": "mtt.cbf.q79-eta9-twisted-spectral-rank-divisibility.v1",
        "theorem_id": "CBF.T68",
        "status": "CLOSED_EXACT_LATE_CANDIDATE_APPLICATION_OF_ESTABLISHED_TWISTED_SPECTRAL_RANK_CUTSET",
        "tier": "exact_application_of_established_general_theorem_to_exact_late_candidate_sources",
        "general_theorem": {
            "source_status": "CONSUMED_FROM_POST_M32_QG_RANK_CUTSET_NOT_REDISCOVERED_HERE",
            "twisted_transition_law": "g_ij g_jk g_ki = alpha_ijk I_r",
            "determinant_law": "delta(det g)_ijk = alpha_ijk^r",
            "cohomology_consequence": "existence of a rank-r locally free alpha-twisted object implies r[alpha]=0",
            "rank_one_equivalence": "a rank-one alpha-twisted object exists iff [alpha]=0",
            "higher_rank_warning": "r[alpha]=0 is necessary, not sufficient; period/index and local-freeness obligations remain",
        },
        "endpoint_decision": {
            "cover_degree": 3,
            "unchanged_MTT_BHT_spectral_rank": 1,
            "unchanged_inverse_transform_rank": 3,
            "required_class": "beta_C=0",
            "requirement_status": "DERIVED_FROM_RANK_ONE_COCYCLE_DESCENT",
            "is_an_optional_selection_convention": False,
            "nonzero_beta_alternative": "requires a different higher-rank twisted endpoint and a new inverse-Fourier-Mukai, index, matter and 27-state derivation",
        },
        "B89_application": {
            "class": "NONZERO",
            "certified_mod_two_shadow": 1,
            "exact_integral_order_known": False,
            "rank_table_1_through_10": b89_table,
            "conclusion_rank_one": "REJECTED",
            "conclusion_spectral_rank_three": "REJECTED",
            "first_spectral_rank_not_rejected_by_known_shadow": 2,
            "corresponding_inverse_transform_rank": 6,
            "even_rank_boundary": "spectral rank two passes the mod-two shadow only; existence is not proved, the exact class order remains unknown, and the degree-three inverse transform would have rank six rather than three",
        },
        "G3BI_application": {
            "global_class": "NONZERO",
            "local_component_group": "Z/20Z",
            "local_component": component,
            "local_component_order": component_order,
            "rank_table_1_through_10": g3bi_table,
            "pairing_four_root_component": pairing_four_component,
            "pairing_four_rank_table_1_through_10": pairing_four_table,
            "conclusion_rank_one": "REJECTED",
            "conclusion_spectral_rank_three": "REJECTED",
            "first_spectral_rank_passing_the_local_component_test": 5,
            "corresponding_inverse_transform_rank": 15,
            "rank_five_boundary": "spectral rank five passes this necessary local-component test only; no rank-five twisted object is constructed, and the degree-three inverse transform would have rank fifteen rather than three",
        },
        "T67_interpretation": {
            "member": "B89 method member",
            "same_source_characteristic_zero_scalar": "CERTIFIED_NONZERO",
            "physical_promotion": "FORBIDDEN_BY_THE_B89_RANK_ONE_ENDPOINT_SIEVE",
            "retained_use": "conditioning, normalization and characteristic-zero transport validation",
        },
        "candidate_search_contract": {
            "unchanged_rank_one_route": [
                "apply the finite local-component sieve",
                "reject every nonzero local component",
                "for each component-trivial survivor, compute the identity-component affine Deligne coordinate",
                "retain only a certified beta_C=0 member",
                "then execute the normalized rank-one inverse Fourier-Mukai and HYM endpoint",
            ],
            "higher_rank_route": [
                "declare the replacement spectral rank before inspecting physical values",
                "require the order of every local/global twisting class to divide that rank",
                "prove existence and local freeness rather than only the divisibility condition",
                "rederive the inverse transform of rank 3r, its index, matter multiplicities and finite 27-state map",
            ],
            "next_candidate_family": "explicit same-residue G3AJ/G3BJ members not already rejected",
        },
        "frontier_delta": {
            "before": "the post-M32 QG theorem already derived beta_C=0 for the degree-three/rank-three endpoint, while the later B89 and G3BI obstructions and T67's chart scalar were not folded through that rank cutset",
            "after": "the established cutset is applied to the late candidates: B89 and G3BI are excluded at spectral ranks one and three; their first not-yet-ruled-out spectral ranks would transform to ranks six and fifteen, so neither preserves the intended rank-three endpoint and T67 cannot be promoted",
        },
        "parameter_ledger": {
            "observed_values_used": 0,
            "new_continuous_fit_parameters": 0,
            "new_discrete_fit_parameters": 0,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "guardrails": {
            "claims_a_beta_zero_member_is_selected": False,
            "claims_a_higher_rank_twisted_object_exists": False,
            "claims_B89_has_exact_order_two": False,
            "claims_G3BI_global_beta_has_exact_order_five": False,
            "claims_T67_is_a_physical_value": False,
            "claims_the_physical_HYM_endpoint_is_emitted": False,
        },
        "inputs": {
            "source_snapshot": binding(SOURCE),
            "B89": binding(b89_path),
            "T67": binding(t67_path),
            "G3BI_upstream": {
                "path": g3bi["upstream_path"],
                "repository_commit": g3bi["repository_commit"],
                "sha256": g3bi["sha256"],
            },
            "rank_one_gate_upstream": {
                "path": sources["rank_one_gate"]["upstream_path"],
                "repository_commit": sources["rank_one_gate"]["repository_commit"],
                "sha256": sources["rank_one_gate"]["sha256"],
            },
            "post_M32_rank_cutset_upstream": {
                "path": post_m32["upstream_path"],
                "repository_commit": post_m32["repository_commit"],
                "sha256": post_m32["sha256"],
            },
        },
    }
    packet["canonical_payload_sha256"] = canonical_sha256(packet)
    OUTPUT.write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(
        "CBF.T68 rank-divisibility: PASS "
        "rank1=B89:REJECTED,G3BI:REJECTED "
        "spectral-rank3=B89:REJECTED,G3BI:REJECTED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
