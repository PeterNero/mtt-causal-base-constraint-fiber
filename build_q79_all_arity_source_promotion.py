"""Build the all-arity contraction-morphism source-promotion packet."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
import build_q79_higher_transfer_jet_filtration_and_m5_feasibility as high
import build_q79_symmetric_response_retraction_transferred_m3 as low
import build_q79_symmetric_weyl_calculus_isometric_retraction as sym


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_all_arity_source_promotion_source_lock.json"
THEOREM_PATH = ROOT / "AllArityContractionMorphismSourcePromotionTheorem_v1.md"
PACKET_PATH = ROOT / "q79_all_arity_source_promotion.packet.json"

E = sym.E
SourceFrozen = low.SourceFrozen
Target = low.Target
TargetSignature = tuple[tuple[int, E], ...]

ACTION_TRANSLATION = "translation"
ACTION_FOURIER = "fourier"
ACTIONS = (ACTION_TRANSLATION, ACTION_FOURIER)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_basis() -> tuple[SourceFrozen, ...]:
    return tuple(low.source_basis())


def target_records() -> tuple[tuple[str, int, Target], ...]:
    return tuple(low.old_basis() + low.ideal_basis())


def target_basis() -> tuple[Target, ...]:
    return tuple(record[2] for record in target_records())


@lru_cache(maxsize=None)
def source_action(name: str, source: SourceFrozen) -> SourceFrozen:
    value = low.thaw_source(source)
    if name == ACTION_TRANSLATION:
        image = sym.affine_action(value, 1, 1, 4)
    elif name == ACTION_FOURIER:
        image = sym.fourier_action(value, 4)
    else:
        raise ValueError(f"unknown action: {name}")
    return low.freeze_source(image)


@lru_cache(maxsize=None)
def target_action(name: str, source: Target) -> Target:
    return low.target_projection(source_action(name, low.target_inclusion(source)))


def source_dga_checks() -> tuple[dict[str, object], dict[str, bool]]:
    basis = source_basis()
    checks: dict[str, bool] = {}
    for name in ACTIONS:
        checks[f"{name}_commutes_with_source_differential_on_144_basis_elements"] = all(
            source_action(name, low.source_differential(item))
            == low.source_differential(source_action(name, item))
            for item in basis
        )
        checks[f"{name}_preserves_source_product_on_20736_basis_pairs"] = all(
            source_action(name, low.source_product(left, right))
            == low.source_product(source_action(name, left), source_action(name, right))
            for left in basis
            for right in basis
        )
    data = {
        "source_dimension": len(basis),
        "source_type": "symmetric crossed-exterior qutrit Weyl DGA over Q(omega)",
        "checked_generators": list(ACTIONS),
        "source_pairs_per_generator": len(basis) ** 2,
    }
    return data, checks


def contraction_naturality_checks() -> tuple[dict[str, object], dict[str, bool]]:
    sources = source_basis()
    targets = target_basis()
    checks: dict[str, bool] = {}
    for name in ACTIONS:
        checks[f"{name}_preserves_target_inclusion_on_48_basis_elements"] = all(
            source_action(name, low.target_inclusion(item))
            == low.target_inclusion(target_action(name, item))
            for item in targets
        )
        checks[f"{name}_preserves_target_projection_on_144_basis_elements"] = all(
            low.target_projection(source_action(name, item))
            == target_action(name, low.target_projection(item))
            for item in sources
        )
        checks[f"{name}_preserves_transfer_homotopy_on_144_basis_elements"] = all(
            source_action(name, low.transfer_homotopy(item))
            == low.transfer_homotopy(source_action(name, item))
            for item in sources
        )
        checks[f"{name}_commutes_with_target_differential_on_48_basis_elements"] = all(
            target_action(name, low.m1(item)) == low.m1(target_action(name, item))
            for item in targets
        )
        checks[f"{name}_preserves_transferred_m2_on_2304_basis_pairs"] = all(
            target_action(name, low.m2(left, right))
            == low.m2(target_action(name, left), target_action(name, right))
            for left in targets
            for right in targets
        )
    data = {
        "source_dimension": len(sources),
        "target_dimension": len(targets),
        "contraction_maps": ["i", "p", "H"],
        "automatic_consequence": (
            "Every Merkulov planar-tree operation m_n is equivariant for every n; "
            "no separate higher-arity covariance census is required."
        ),
    }
    return data, checks


def field_inverse(value: E) -> E:
    denominator = value.a * value.a - value.a * value.b + value.b * value.b
    if denominator == 0:
        raise ZeroDivisionError("zero Eisenstein coefficient")
    return E((value.a - value.b) / denominator, -value.b / denominator)


def monomial_target_coordinates(source: Target, index: dict[Target, int]) -> tuple[int, E]:
    terms = len(source[0]) + len(source[1])
    if terms != 1:
        raise ValueError("target action is not monomial on the selected basis")
    coefficient = source[0][0][3] if source[0] else source[1][0][1]
    normalized = low.target_scale(field_inverse(coefficient), source)
    return index[normalized], coefficient


def target_signature(name: str) -> TargetSignature:
    basis = target_basis()
    index = {item: position for position, item in enumerate(basis)}
    return tuple(monomial_target_coordinates(target_action(name, item), index) for item in basis)


def compose_signature(left: TargetSignature, right: TargetSignature) -> TargetSignature:
    out: list[tuple[int, E]] = []
    for middle, right_coefficient in right:
        target, left_coefficient = left[middle]
        out.append((target, left_coefficient * right_coefficient))
    return tuple(out)


def signature_power(source: TargetSignature, exponent: int) -> TargetSignature:
    identity = tuple((index, sym.wk.ONE) for index in range(len(source)))
    out = identity
    for _ in range(exponent):
        out = compose_signature(source, out)
    return out


def generated_group(signatures: tuple[TargetSignature, ...]) -> set[TargetSignature]:
    identity = tuple((index, sym.wk.ONE) for index in range(len(signatures[0])))
    found = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in signatures:
            candidate = compose_signature(generator, current)
            if candidate not in found:
                found.add(candidate)
                frontier.append(candidate)
    return found


def target_group_checks() -> tuple[dict[str, object], dict[str, bool]]:
    translation = target_signature(ACTION_TRANSLATION)
    fourier = target_signature(ACTION_FOURIER)
    identity = tuple((index, sym.wk.ONE) for index in range(len(translation)))
    full_group = generated_group((translation, fourier))
    reflection = signature_power(fourier, 2)
    affine_group = generated_group((translation, reflection))
    checks = {
        "translation_has_order_three_on_the_48_dimensional_target": (
            signature_power(translation, 3) == identity
            and signature_power(translation, 1) != identity
        ),
        "Fourier_has_order_four_on_the_48_dimensional_target": (
            signature_power(fourier, 4) == identity
            and signature_power(fourier, 2) != identity
        ),
        "induced_affine_subgroup_has_order_six": len(affine_group) == 6,
        "induced_covariance_group_has_order_36": len(full_group) == 36,
        "both_generator_actions_are_monomial_on_all_48_target_basis_elements": all(
            len(target_action(name, item)[0]) + len(target_action(name, item)[1]) == 1
            for name in ACTIONS
            for item in target_basis()
        ),
    }
    data = {
        "target_covariance_group": "(Z3 x Z3) semidirect C4",
        "generated_order": len(full_group),
        "affine_subgroup_order": len(affine_group),
        "representation_is_faithful_at_finite_target_tier": len(full_group) == 36,
        "physical_holonomy_claimed": False,
    }
    return data, checks


def multiply_coefficients(values: tuple[E, ...]) -> E:
    out = sym.wk.ONE
    for value in values:
        out *= value
    return out


def selected_all_arity_probes() -> tuple[dict[str, object], dict[str, bool]]:
    records = target_records()
    labels = {label: index for index, (label, _, _) in enumerate(records)}
    x = labels["C:0,0,1"]
    y = labels["C:1,0,1"]
    z = labels["C:1,0,0"]
    signatures = {name: target_signature(name) for name in ACTIONS}
    checks: dict[str, bool] = {}
    results: list[dict[str, object]] = []
    for arity in range(3, 9):
        indices = (x,) * (arity - 2) + (y, z)
        value = high.generic_mn(indices)
        for name in ACTIONS:
            signature = signatures[name]
            mapped = tuple(signature[index][0] for index in indices)
            coefficient = multiply_coefficients(tuple(signature[index][1] for index in indices))
            lhs = target_action(name, value)
            rhs = low.target_scale(coefficient, high.generic_mn(mapped))
            checks[f"{name}_selected_nontruncating_family_is_equivariant_at_arity_{arity}"] = lhs == rhs
        results.append(
            {
                "arity": arity,
                "source_nonzero": value != low.ZERO_TARGET,
                "translation_equivariant": checks[
                    f"{ACTION_TRANSLATION}_selected_nontruncating_family_is_equivariant_at_arity_{arity}"
                ],
                "fourier_equivariant": checks[
                    f"{ACTION_FOURIER}_selected_nontruncating_family_is_equivariant_at_arity_{arity}"
                ],
            }
        )
    checks["selected_family_is_nonzero_at_every_probed_arity_3_through_8"] = all(
        result["source_nonzero"] for result in results
    )
    data = {
        "family": "x^(n-2), y, z",
        "x": "C:0,0,1",
        "y": "C:1,0,1",
        "z": "C:1,0,0",
        "probes": results,
        "logical_scope": (
            "The finite probes are regression witnesses. All-arity equivariance follows from "
            "the contraction-morphism theorem, not extrapolation from these six arities."
        ),
    }
    return data, checks


def endpoint_contract() -> dict[str, object]:
    return {
        "schema": "boe.mtt.q79-all-arity-continuum-endpoint-contract.v1",
        "automatic_compiler_rows": [
            {
                "row": "AC.01",
                "state": "closed_exact_general",
                "requirement": "DGA morphism plus contraction-square identities imply all transferred m_n squares",
            },
            {
                "row": "AC.02",
                "state": "closed_exact_general",
                "requirement": "unitary reducing cochain map implies adjoint, Laplacian, projector, Green and H naturality",
            },
            {
                "row": "AC.03",
                "state": "closed_exact_finite_q79",
                "requirement": "translation and Fourier generators preserve the complete 144-to-48 contraction",
            },
        ],
        "physical_source_rows": [
            {
                "row": "EP.01",
                "state": "open",
                "blocker": "B.HS.01",
                "requirement": "selected source-hashed visible-hidden HYM endpoint and common chamber",
            },
            {
                "row": "EP.02",
                "state": "open",
                "blocker": "B.GEO.01",
                "requirement": "typed unitary continuum-to-finite source map on declared Sobolev domains",
            },
            {
                "row": "EP.03",
                "state": "open",
                "blocker": "B.GEO.01",
                "requirement": "same map intertwines differential, product and retained projector or supplies certified defects",
            },
            {
                "row": "EP.04",
                "state": "open",
                "blocker": "B.GEO.01",
                "requirement": "selected physical C4/monodromy lift preserves the endpoint source data",
            },
            {
                "row": "EP.05",
                "state": "open",
                "blocker": "B.OP.01",
                "requirement": "rank-102 coefficient arrays, QHP/Feshbach decision, inverse and tail bounds",
            },
            {
                "row": "EP.06",
                "state": "open",
                "blocker": "B.ACTION.01",
                "requirement": "same-source cyclic/BV or Lorentzian action, pairing, real slice and normalization",
            },
            {
                "row": "EP.07",
                "state": "open",
                "blocker": "B.ACTION.01",
                "requirement": "BV-compatible externalization/compactification to the accepted four-dimensional fields",
            },
        ],
        "physical_rows_accepted": 0,
        "physical_rows_total": 7,
        "key_reduction": (
            "Once EP.01-EP.04 provide an exact contraction-preserving source map, Green/homotopy "
            "naturality and every higher transferred operation are consequences, not independent rows."
        ),
        "approximate_case": (
            "If endpoint squares have nonzero defects, use the already closed FSB.03b arity majorants; "
            "this theorem does not silently promote approximate maps to exact ones."
        ),
    }


def source_checks(lock: dict[str, object]) -> dict[str, bool]:
    expected = {item["path"]: item["sha256"] for item in lock["local_sources"]}
    return {
        "source_lock_schema_is_current": lock.get("schema")
        == "boe.mtt.q79-all-arity-source-promotion-source-lock.v1",
        "kernel_model_hash_is_locked": lock["kernel_model"]["state_sha256"]
        == "572272ade96f4bf2d89dd41c48701a125cd0736343167819855b2cf41f377b45",
        "symmetric_DGA_packet_hash_matches": sha256(
            ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
        )
        == expected["q79_symmetric_weyl_calculus_isometric_retraction.packet.json"],
        "response_contraction_packet_hash_matches": sha256(
            ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json"
        )
        == expected["q79_symmetric_response_retraction_transferred_m3.packet.json"],
        "higher_transfer_packet_hash_matches": sha256(
            ROOT / "q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json"
        )
        == expected["q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json"],
        "contraction_implementation_hash_matches": sha256(
            ROOT / "build_q79_symmetric_response_retraction_transferred_m3.py"
        )
        == expected["build_q79_symmetric_response_retraction_transferred_m3.py"],
        "all_four_controlling_blockers_remain_explicitly_open": {
            item["id"] for item in lock["blockers"] if item["state"] == "open"
        }
        == {"B.HS.01", "B.GEO.01", "B.OP.01", "B.ACTION.01"},
    }


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    source_data, source_result = source_dga_checks()
    contraction_data, contraction_result = contraction_naturality_checks()
    group_data, group_result = target_group_checks()
    probe_data, probe_result = selected_all_arity_probes()
    checks = {
        **source_checks(lock),
        **source_result,
        **contraction_result,
        **group_result,
        **probe_result,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"all-arity source-promotion checks failed: {failed}")
    return {
        "schema": "boe.mtt.q79-all-arity-source-promotion.packet.v1",
        "claim_id": "CBF.T11",
        "date": "2026-08-28",
        "status": (
            "EXACT_GENERAL_ALL_ARITY_CONTRACTION_MORPHISM_THEOREM_AND_"
            "EXACT_FINITE_Q79_COVARIANCE_EXECUTION_PHYSICAL_ENDPOINT_OPEN"
        ),
        "tier": "EXACT_GENERAL + SELECTED_EXACT_FINITE; CONDITIONAL_CONTINUUM",
        "source_lock_sha256": sha256(LOCK_PATH),
        "theorem_sha256": sha256(THEOREM_PATH),
        "theorem": {
            "hypotheses": [
                "Phi is a degree-zero DGA morphism",
                "Psi is the retained chain map",
                "Phi i=i' Psi",
                "p' Phi=Psi p",
                "Phi H=H' Phi",
            ],
            "conclusion": "Psi m_n=m'_n Psi^(tensor n) for every n>=1",
            "proof_method": "induction on decorated planar binary trees in the Merkulov recursion",
            "hodge_corollary": (
                "a unitary reducing cochain intertwiner preserving the declared closed operator "
                "domains automatically transports adjoints, Laplacians, spectral projectors, "
                "reduced Greens and H=d*G"
            ),
        },
        "q79_source_DGA": source_data,
        "q79_contraction_naturality": contraction_data,
        "q79_target_group": group_data,
        "selected_all_arity_regression": probe_data,
        "endpoint_contract": endpoint_contract(),
        "checks": checks,
        "check_summary": {
            "passed": sum(checks.values()),
            "total": len(checks),
        },
        "frontier_delta": {
            "closed": [
                "all-arity functoriality of homotopy transfer under a contraction-preserving DGA morphism",
                "exact preservation of the q79 144-to-48 contraction by translation and Fourier generators",
                "faithful order-36 induced covariance action on the 48-dimensional target",
                "reduction of infinitely many exact higher-operation transport checks to finite source identities",
            ],
            "open": [
                "selected visible-hidden HYM endpoint and common chamber",
                "continuum source morphism and physical C4 lift",
                "rank-102 coefficient arrays and finite residual/tail execution",
                "physical cyclic/BV or Lorentzian action and compactification map",
            ],
            "blocker_states_changed": False,
        },
        "claim_boundary": {
            "does_not_claim": [
                "that the finite covariance group is physical q79 holonomy",
                "that a continuum HYM endpoint has been selected",
                "that D_fin is the transferred HYM operator",
                "that the physical action or four-dimensional BV compactification is closed",
                "that approximate endpoint maps satisfy exact all-arity naturality",
            ]
        },
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = packet["check_summary"]
    print(f"wrote {PACKET_PATH.name}: {summary['passed']}/{summary['total']} checks passed")


if __name__ == "__main__":
    main()
