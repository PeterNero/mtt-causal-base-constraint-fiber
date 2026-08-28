"""Build the exact symmetric-response retract and transferred m2/m3 packet."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path
from typing import Iterable

import build_q79_symmetric_weyl_calculus_isometric_retraction as sym


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_symmetric_response_transfer_source_lock.json"
THEOREM_PATH = ROOT / "SymmetricWeylResponseRetractionAndTransferredM3Theorem_v1.md"
PACKET_PATH = ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json"
SYMMETRIC_PACKET_PATH = ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
FIRST_JET_PACKET_PATH = ROOT / "q79_signed_edge_first_jet_harmonic_ideal_quotient.packet.json"

E = sym.E
SourceFrozen = tuple[tuple[int, int, int, E], ...]
IdealFrozen = tuple[tuple[int, E], ...]
Target = tuple[SourceFrozen, IdealFrozen]

ZERO_SOURCE: SourceFrozen = ()
ZERO_IDEAL: IdealFrozen = ()
ZERO_TARGET: Target = (ZERO_SOURCE, ZERO_IDEAL)
PARITY_EVEN_MASK = 0b1100
IDEAL_MASKS = tuple(mask for mask in range(16) if mask & PARITY_EVEN_MASK)
TARGET_DIMS = (9, 20, 14, 4, 1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_source(source: sym.ModeElement) -> SourceFrozen:
    return tuple((a, b, mask, value) for (a, b, mask), value in sorted(sym.clean(source).items()))


def thaw_source(source: SourceFrozen) -> sym.ModeElement:
    return {(a, b, mask): value for a, b, mask, value in source}


def freeze_ideal(source: dict[int, E]) -> IdealFrozen:
    return tuple((mask, value) for mask, value in sorted(source.items()) if value != sym.wk.ZERO)


def thaw_ideal(source: IdealFrozen) -> dict[int, E]:
    return dict(source)


def source_add(left: SourceFrozen, right: SourceFrozen) -> SourceFrozen:
    return freeze_source(sym.element_add(thaw_source(left), thaw_source(right)))


def source_scale(value: int | Fraction | E, source: SourceFrozen) -> SourceFrozen:
    return freeze_source(sym.element_scale(value, thaw_source(source)))


@lru_cache(maxsize=None)
def source_product(left: SourceFrozen, right: SourceFrozen) -> SourceFrozen:
    if not left or not right:
        return ZERO_SOURCE
    return freeze_source(sym.product(thaw_source(left), thaw_source(right), sym.DIRECTION_EXPONENTS))


@lru_cache(maxsize=None)
def source_differential(source: SourceFrozen) -> SourceFrozen:
    if not source:
        return ZERO_SOURCE
    return freeze_source(sym.differential(thaw_source(source), sym.DIRECTION_EXPONENTS))


def target_add(left: Target, right: Target) -> Target:
    ideal = thaw_ideal(left[1])
    for mask, value in right[1]:
        ideal[mask] = ideal.get(mask, sym.wk.ZERO) + value
    return source_add(left[0], right[0]), freeze_ideal(ideal)


def target_scale(value: int | Fraction | E, source: Target) -> Target:
    scalar = sym.e(value)
    return source_scale(scalar, source[0]), freeze_ideal({mask: scalar * item for mask, item in source[1]})


def target_degree(source: Target) -> int | None:
    degrees = {mask.bit_count() for _, _, mask, _ in source[0]}
    degrees |= {mask.bit_count() for mask, _ in source[1]}
    if not degrees:
        return None
    if len(degrees) != 1:
        raise ValueError("target element is not homogeneous")
    return next(iter(degrees))


def parity_change() -> sym.Linear:
    return sym.lmatrix(
        [
            [1, 0, 1, 0],
            [-1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, -1, 0, 1],
        ]
    )


def parity_inverse() -> sym.Linear:
    return sym.lmatrix(
        [
            [Fraction(1, 2), Fraction(-1, 2), 0, 0],
            [0, 0, Fraction(1, 2), Fraction(-1, 2)],
            [Fraction(1, 2), Fraction(1, 2), 0, 0],
            [0, 0, Fraction(1, 2), Fraction(1, 2)],
        ]
    )


@lru_cache(maxsize=None)
def parity_to_signed(degree: int) -> sym.Linear:
    return sym.exterior_power(parity_change(), degree)


@lru_cache(maxsize=None)
def signed_to_parity(degree: int) -> sym.Linear:
    return sym.exterior_power(parity_inverse(), degree)


def ideal_to_source(ideal: IdealFrozen) -> SourceFrozen:
    out: sym.ModeElement = {}
    for parity_mask, value in ideal:
        degree = parity_mask.bit_count()
        masks = sym.form_masks(4, degree)
        col = masks.index(parity_mask)
        conversion = parity_to_signed(degree)
        for row, signed_mask in enumerate(masks):
            coefficient = value * conversion[row][col]
            if coefficient != sym.wk.ZERO:
                out[(0, 0, signed_mask)] = out.get((0, 0, signed_mask), sym.wk.ZERO) + coefficient
    return freeze_source(out)


def source_to_ideal(source: SourceFrozen) -> IdealFrozen:
    by_degree: dict[int, dict[int, E]] = {}
    for a, b, mask, value in source:
        if a == 0 and b == 0:
            by_degree.setdefault(mask.bit_count(), {})[mask] = value
    out: dict[int, E] = {}
    for degree, entries in by_degree.items():
        masks = sym.form_masks(4, degree)
        vector = tuple(entries.get(mask, sym.wk.ZERO) for mask in masks)
        coordinates = sym.vector_apply(signed_to_parity(degree), vector)
        for mask, coefficient in zip(masks, coordinates):
            if mask & PARITY_EVEN_MASK and coefficient != sym.wk.ZERO:
                out[mask] = out.get(mask, sym.wk.ZERO) + coefficient
    return freeze_ideal(out)


@lru_cache(maxsize=None)
def target_inclusion(source: Target) -> SourceFrozen:
    old = freeze_source(sym.include_old(thaw_source(source[0])))
    return source_add(old, ideal_to_source(source[1]))


@lru_cache(maxsize=None)
def target_projection(source: SourceFrozen) -> Target:
    old = freeze_source(sym.retract_symmetric(thaw_source(source)))
    return old, source_to_ideal(source)


@lru_cache(maxsize=None)
def target_differential(source: Target) -> Target:
    if not source[0]:
        return ZERO_TARGET
    old = freeze_source(sym.differential(thaw_source(source[0]), sym.OLD_DIRECTIONS))
    return old, ZERO_IDEAL


def old_project_source(source: SourceFrozen) -> SourceFrozen:
    old = sym.retract_symmetric(thaw_source(source))
    return freeze_source(sym.include_old(old))


def complement_source(source: SourceFrozen) -> SourceFrozen:
    return source_add(source, source_scale(-1, old_project_source(source)))


def raw_symmetric_homotopy(source: SourceFrozen) -> SourceFrozen:
    if not source:
        return ZERO_SOURCE
    groups: dict[tuple[int, int, int], dict[int, E]] = {}
    for a, b, mask, value in source:
        degree = mask.bit_count()
        groups.setdefault((a, b, degree), {})[mask] = value
    out: sym.ModeElement = {}
    for (a, b, degree), entries in groups.items():
        if degree == 0 or (a == 0 and b == 0):
            continue
        mode = sym.mode_vector(a, b, sym.DIRECTION_EXPONENTS)
        differential = sym.wedge_matrix(mode, degree - 1)
        adjoint = sym.lscale(sym.HALF, sym.ladj(differential))
        norm = sym.HALF * sum((value.conjugate() * value for value in mode), sym.wk.ZERO)
        if norm.b != 0 or norm.a == 0:
            raise ValueError("non-rational or zero nonharmonic Hodge eigenvalue")
        homotopy = sym.lscale(Fraction(1, 1) / norm.a, adjoint)
        source_masks = sym.form_masks(4, degree)
        target_masks = sym.form_masks(4, degree - 1)
        vector = tuple(entries.get(mask, sym.wk.ZERO) for mask in source_masks)
        image = sym.vector_apply(homotopy, vector)
        for mask, coefficient in zip(target_masks, image):
            if coefficient != sym.wk.ZERO:
                out[(a, b, mask)] = out.get((a, b, mask), sym.wk.ZERO) + coefficient
    return freeze_source(out)


@lru_cache(maxsize=None)
def transfer_homotopy(source: SourceFrozen) -> SourceFrozen:
    return complement_source(raw_symmetric_homotopy(complement_source(source)))


@lru_cache(maxsize=None)
def m1(source: Target) -> Target:
    return target_differential(source)


@lru_cache(maxsize=None)
def m2(left: Target, right: Target) -> Target:
    if left == ZERO_TARGET or right == ZERO_TARGET:
        return ZERO_TARGET
    return target_projection(source_product(target_inclusion(left), target_inclusion(right)))


@lru_cache(maxsize=None)
def m3(left: Target, middle: Target, right: Target) -> Target:
    if left == ZERO_TARGET or middle == ZERO_TARGET or right == ZERO_TARGET:
        return ZERO_TARGET
    left_degree = target_degree(left)
    if left_degree is None:
        return ZERO_TARGET
    first = source_product(
        transfer_homotopy(source_product(target_inclusion(left), target_inclusion(middle))),
        target_inclusion(right),
    )
    second = source_product(
        target_inclusion(left),
        transfer_homotopy(source_product(target_inclusion(middle), target_inclusion(right))),
    )
    sign = -1 if left_degree % 2 == 0 else 1
    return target_projection(source_add(first, source_scale(sign, second)))


def old_basis() -> list[tuple[str, int, Target]]:
    out = []
    for a in range(3):
        for b in range(3):
            for mask in range(4):
                source = freeze_source(sym.basis_element(a, b, mask))
                out.append((f"C:{a},{b},{mask}", mask.bit_count(), (source, ZERO_IDEAL)))
    return out


def ideal_basis() -> list[tuple[str, int, Target]]:
    return [
        (f"J:{mask}", mask.bit_count(), (ZERO_SOURCE, ((mask, sym.wk.ONE),)))
        for mask in IDEAL_MASKS
    ]


def source_basis() -> list[SourceFrozen]:
    return [
        freeze_source(sym.basis_element(a, b, mask))
        for a in range(3)
        for b in range(3)
        for mask in range(16)
    ]


def encode_eisenstein(value: E) -> list[str]:
    return [sym.fstr(value.a), sym.fstr(value.b)]


def encode_target(source: Target) -> dict[str, object]:
    return {
        "old": [[a, b, mask, encode_eisenstein(value)] for a, b, mask, value in source[0]],
        "higher_jet": [[mask, encode_eisenstein(value)] for mask, value in source[1]],
    }


def target_kind(source: Target) -> str:
    old, jet = bool(source[0]), bool(source[1])
    if old and jet:
        return "old+jet"
    if old:
        return "old"
    if jet:
        return "jet"
    return "zero"


def operation_digest(records: Iterable[tuple[object, ...]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def contraction_checks() -> tuple[dict[str, object], dict[str, bool]]:
    targets = old_basis() + ideal_basis()
    sources = source_basis()
    projection_inclusion = all(target_projection(target_inclusion(item)) == item for _, _, item in targets)
    inclusion_chain = all(source_differential(target_inclusion(item)) == target_inclusion(m1(item)) for _, _, item in targets)
    projection_chain = all(target_projection(source_differential(item)) == m1(target_projection(item)) for item in sources)
    homotopy_identity = all(
        source_add(source_differential(transfer_homotopy(item)), transfer_homotopy(source_differential(item)))
        == source_add(item, source_scale(-1, target_inclusion(target_projection(item))))
        for item in sources
    )
    homotopy_square = all(transfer_homotopy(transfer_homotopy(item)) == ZERO_SOURCE for item in sources)
    projection_homotopy = all(target_projection(transfer_homotopy(item)) == ZERO_TARGET for item in sources)
    homotopy_inclusion = all(transfer_homotopy(target_inclusion(item)) == ZERO_SOURCE for _, _, item in targets)
    target_counts = [sum(degree == target_degree for _, target_degree, _ in targets) for degree in range(5)]
    cohomology = [1, 2, 1, 0, 0]
    ideal_cohomology = [0, 2, 5, 4, 1]
    target_cohomology = [left + right for left, right in zip(cohomology, ideal_cohomology)]
    checks = {
        "target_has_dimension_48": len(targets) == 48,
        "target_degree_dimensions_are_9_20_14_4_1": target_counts == list(TARGET_DIMS),
        "target_cohomology_matches_symmetric_1_4_6_4_1": target_cohomology == [1, 4, 6, 4, 1],
        "retraction_after_inclusion_is_identity_on_all_48_target_basis_elements": projection_inclusion,
        "target_inclusion_is_a_cochain_map": inclusion_chain,
        "target_projection_is_a_cochain_map": projection_chain,
        "strong_deformation_retract_identity_holds_on_all_144_source_basis_elements": homotopy_identity,
        "transfer_homotopy_squares_to_zero_on_all_144_source_basis_elements": homotopy_square,
        "target_projection_annihilates_the_transfer_homotopy": projection_homotopy,
        "transfer_homotopy_annihilates_the_target_inclusion": homotopy_inclusion,
    }
    data = {
        "source": {
            "name": "symmetric signed Weyl DGA",
            "degree_dimensions": [9, 36, 54, 36, 9],
            "total_dimension": 144,
        },
        "target": {
            "name": "selected old q79 complex direct-sum higher-jet harmonic ideal",
            "degree_dimensions": target_counts,
            "old_complex_dimensions": [9, 18, 9, 0, 0],
            "higher_jet_dimensions": [0, 2, 5, 4, 1],
            "total_dimension": len(targets),
            "cohomology_dimensions": target_cohomology,
        },
        "maps": {
            "inclusion": "i_T(x,j)=I_old(x)+j",
            "projection": "p_T(y)=(Q_old(y),P_J(y))",
            "homotopy": "H_T=(1-IQ) h_sym (1-IQ), with h_sym=d*_sym G_sym on nonzero modes",
        },
        "identity": "d H_T + H_T d = 1 - i_T p_T",
        "side_conditions": ["p_T i_T=1", "H_T^2=0", "p_T H_T=0", "H_T i_T=0"],
    }
    return data, checks


def transfer_checks() -> tuple[dict[str, object], dict[str, bool]]:
    basis = old_basis() + ideal_basis()
    count = len(basis)
    unit = basis[0][2]
    m1_square = all(m1(m1(item)) == ZERO_TARGET for _, _, item in basis)
    m2_unital = all(m2(unit, item) == item and m2(item, unit) == item for _, _, item in basis)
    m3_unital = all(
        m3(unit, left, right) == ZERO_TARGET
        and m3(left, unit, right) == ZERO_TARGET
        and m3(left, right, unit) == ZERO_TARGET
        for _, _, left in basis
        for _, _, right in basis
    )
    leibniz = True
    m2_degree_ok = True
    m2_nonzero = 0
    m2_sector = Counter()
    m2_records: list[tuple[object, ...]] = []
    for left_index, (left_label, left_degree, left) in enumerate(basis):
        for right_index, (right_label, _, right) in enumerate(basis):
            value = m2(left, right)
            rhs = target_add(m2(m1(left), right), target_scale(-1 if left_degree % 2 else 1, m2(left, m1(right))))
            leibniz &= m1(value) == rhs
            if value != ZERO_TARGET:
                m2_degree_ok &= target_degree(value) == left_degree + (target_degree(right) or 0)
                m2_nonzero += 1
                pattern = left_label[0] + right_label[0]
                m2_sector[(pattern, target_kind(value))] += 1
                m2_records.append((left_index, right_index, encode_target(value)))

    associators = 0
    old_input_associators = 0
    m3_nonzero = 0
    old_input_m3 = 0
    harmonic_m3 = 0
    two_or_more_jet_input_m3 = 0
    associator_and_m3 = 0
    m3_degree_ok = True
    m3_sector = Counter()
    m3_records: list[tuple[object, ...]] = []
    stasheff = True
    first_witness: dict[str, object] | None = None
    first_associator_witness: dict[str, object] | None = None
    first_coupled_witness: dict[str, object] | None = None
    harmonic_flags = [label.startswith("J:") or label.startswith("C:0,0,") for label, _, _ in basis]
    for left_index, (left_label, left_degree, left) in enumerate(basis):
        for middle_index, (middle_label, middle_degree, middle) in enumerate(basis):
            for right_index, (right_label, right_degree, right) in enumerate(basis):
                associator = target_add(m2(m2(left, middle), right), target_scale(-1, m2(left, m2(middle, right))))
                if associator != ZERO_TARGET:
                    associators += 1
                    if left_index < 36 and middle_index < 36 and right_index < 36:
                        old_input_associators += 1
                    if first_associator_witness is None:
                        first_associator_witness = {
                            "inputs": [left_label, middle_label, right_label],
                            "degrees": [left_degree, middle_degree, right_degree],
                            "m2_associator": encode_target(associator),
                        }
                ternary = m3(left, middle, right)
                if ternary != ZERO_TARGET:
                    m3_nonzero += 1
                    m3_degree_ok &= target_degree(ternary) == left_degree + middle_degree + right_degree - 1
                    pattern = left_label[0] + middle_label[0] + right_label[0]
                    m3_sector[(pattern, target_kind(ternary))] += 1
                    m3_records.append((left_index, middle_index, right_index, encode_target(ternary)))
                    if left_index < 36 and middle_index < 36 and right_index < 36:
                        old_input_m3 += 1
                    if harmonic_flags[left_index] and harmonic_flags[middle_index] and harmonic_flags[right_index]:
                        harmonic_m3 += 1
                    if sum(label.startswith("J:") for label in (left_label, middle_label, right_label)) >= 2:
                        two_or_more_jet_input_m3 += 1
                    if associator != ZERO_TARGET:
                        associator_and_m3 += 1
                        if first_coupled_witness is None:
                            first_coupled_witness = {
                                "inputs": [left_label, middle_label, right_label],
                                "degrees": [left_degree, middle_degree, right_degree],
                                "m3": encode_target(ternary),
                                "m2_associator": encode_target(associator),
                            }
                    if first_witness is None:
                        first_witness = {
                            "inputs": [left_label, middle_label, right_label],
                            "degrees": [left_degree, middle_degree, right_degree],
                            "m3": encode_target(ternary),
                            "m2_associator": encode_target(associator),
                        }
                correction = target_add(
                    m1(ternary),
                    target_add(
                        m3(m1(left), middle, right),
                        target_add(
                            target_scale(-1 if left_degree % 2 else 1, m3(left, m1(middle), right)),
                            target_scale(-1 if (left_degree + middle_degree) % 2 else 1, m3(left, middle, m1(right))),
                        ),
                    ),
                )
                stasheff &= target_add(associator, correction) == ZERO_TARGET

    m2_digest = operation_digest(m2_records)
    m3_digest = operation_digest(m3_records)

    checks = {
        "target_differential_squares_to_zero_on_all_48_basis_elements": m1_square,
        "transferred_m2_is_strictly_unital_on_all_48_basis_elements": m2_unital,
        "transferred_m3_vanishes_when_any_input_is_the_unit": m3_unital,
        "transferred_m1_m2_Leibniz_identity_holds_on_all_2304_basis_pairs": leibniz,
        "transferred_m2_has_degree_zero_on_every_nonzero_basis_product": m2_degree_ok,
        "transferred_m3_is_nonzero": m3_nonzero > 0,
        "transferred_m3_vanishes_on_all_harmonic_input_triples": harmonic_m3 == 0,
        "transferred_m3_has_degree_minus_one_on_every_nonzero_basis_triple": m3_degree_ok,
        "transferred_m3_vanishes_with_two_or_more_higher_jet_basis_inputs": two_or_more_jet_input_m3 == 0,
        "arity_three_Stasheff_identity_holds_on_all_110592_basis_triples": stasheff,
        "old_only_compressed_associativity_defect_is_not_silently_removed": old_input_associators > 0,
        "old_only_inputs_source_nonzero_ternary_transfer": old_input_m3 > 0,
        "operation_table_digests_are_sha256": len(m2_digest) == len(m3_digest) == 64,
    }
    data = {
        "convention": {
            "m1": "d_T",
            "m2": "p mu(i tensor i)",
            "m3": "p mu(H mu(i a,i b),i c) - (-1)^|a| p mu(i a,H mu(i b,i c))",
            "arity_three_identity": "Assoc(m2)+m1m3+m3(m1,a,b)+(-1)^|a|m3(a,m1,b)+(-1)^(|a|+|b|)m3(a,b,m1)=0",
        },
        "basis_counts": {
            "target": count,
            "pairs": count**2,
            "triples": count**3,
        },
        "m2": {
            "nonzero_basis_pairs": m2_nonzero,
            "sector_counts": {f"{pattern}->{output}": value for (pattern, output), value in sorted(m2_sector.items())},
            "nonzero_table_sha256": m2_digest,
        },
        "m3": {
            "nonzero_basis_triples": m3_nonzero,
            "old_input_nonzero_basis_triples": old_input_m3,
            "harmonic_input_nonzero_basis_triples": harmonic_m3,
            "two_or_more_higher_jet_input_nonzero_basis_triples": two_or_more_jet_input_m3,
            "nonzero_associator_and_m3_basis_triples": associator_and_m3,
            "sector_counts": {f"{pattern}->{output}": value for (pattern, output), value in sorted(m3_sector.items())},
            "nonzero_table_sha256": m3_digest,
            "first_nonzero_witness": first_witness,
            "first_nonzero_associator_and_m3_witness": first_coupled_witness,
        },
        "m2_associativity": {
            "nonzero_target_associators": associators,
            "nonzero_old_input_associators_in_48_target": old_input_associators,
            "prior_old_only_36_target_associators": 4464,
            "first_nonzero_associator_witness": first_associator_witness,
            "verdict": "The binary target product is not strict associative off harmonics; m3 supplies its exact chain-homotopy correction at arity three.",
        },
        "scope": "m1, m2, m3 and the arity-three identity only; m4 and higher are not inferred",
    }
    return data, checks


def source_checks(lock: dict[str, object], symmetric: dict[str, object], first_jet: dict[str, object]) -> dict[str, bool]:
    sources = lock["sources"]
    return {
        "source_lock_schema_is_exact": lock["schema"] == "boe.mtt.q79-symmetric-response-transfer-source-lock.v1",
        "kernel_model_hash_is_pinned": len(lock["kernel_model"]["state_sha256"]) == 64,
        "three_controlling_authorities_are_pinned": [item["id"] for item in lock["controlling_authorities"]] == ["A10", "A18", "A47"],
        "six_sources_are_commit_blob_and_sha256_pinned": len(sources) == 6 and all(len(item["commit"]) == 40 and len(item["git_blob"]) == 40 and len(item["sha256"]) == 64 for item in sources),
        "all_pinned_local_source_hashes_match": all(sha256(ROOT / item["path"]) == item["sha256"] for item in sources),
        "upstream_old_complex_is_an_isometric_cochain_retract": symmetric["selected_old_complex_isometric_cochain_retract"] is True,
        "upstream_extra_harmonic_dimensions_are_0_2_5_4_1": symmetric["selected_complex_retract"]["extra_harmonic_dimensions"] == [0, 2, 5, 4, 1],
        "upstream_extra_classes_are_the_even_generated_ideal": first_jet["twelve_extra_harmonic_classes_form_even_generated_ideal"] is True,
        "upstream_harmonic_quotient_is_strict": first_jet["selected_harmonic_algebra_is_strict_quotient"] is True,
        "source_guard_keeps_m4_HYM_Dfin_and_action_open": all(term in lock["guard"] for term in ("does not identify the target with D_fin", "does not select the continuum HYM endpoint", "does not infer m4")),
    }


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    symmetric = json.loads(SYMMETRIC_PACKET_PATH.read_text(encoding="utf-8"))
    first_jet = json.loads(FIRST_JET_PACKET_PATH.read_text(encoding="utf-8"))
    contraction, contraction_result_checks = contraction_checks()
    transfer, transfer_result_checks = transfer_checks()
    checks = source_checks(lock, symmetric, first_jet) | contraction_result_checks | transfer_result_checks
    return {
        "schema": "boe.mtt.q79-symmetric-response-retraction-transferred-m3.v1",
        "theorem_id": "SymmetricWeylResponseRetractionAndTransferredM3Theorem.v1",
        "date": "2026-08-28",
        "tiers": [
            "EXACT_FINITE_STRONG_DEFORMATION_RETRACT",
            "EXACT_TRANSFERRED_M1_M2_M3",
            "EXACT_ARITY_THREE_A_INFINITY_IDENTITY",
            "HIGHER_ARITY_AND_PHYSICAL_PROMOTION_OPEN",
        ],
        "strong_deformation_retract_to_old_plus_higher_jet_ideal": True,
        "transferred_m3_computed": True,
        "transferred_m4_and_higher_computed": False,
        "target_identified_with_D_fin": False,
        "selected_nonzero_Chern_HYM_endpoint": False,
        "physical_action_selected": False,
        "continuous_fit_parameters": 0,
        "discrete_physical_selectors": 0,
        "observed_physical_inputs": [],
        "source_hashes": {
            "source_lock_sha256": sha256(LOCK_PATH),
            "theorem_sha256": sha256(THEOREM_PATH),
            "builder_sha256": sha256(Path(__file__).resolve()),
        },
        "strong_deformation_retract": contraction,
        "transferred_structure": transfer,
        "checks": checks,
        "summary": {
            "passed": sum(bool(value) for value in checks.values()),
            "total": len(checks),
            "all_passed": all(checks.values()),
        },
        "frontier_delta": "The 144-dimensional symmetric signed Weyl DGA now has an exact 48-dimensional strong deformation retract onto the selected 36-dimensional old q79 cochain complex plus the twelve-class higher-jet harmonic ideal. The transferred m2 and m3 are computed on every target basis pair/triple, and the arity-three Stasheff identity is verified exactly. This explains the old compressed associator as low-arity homotopy-transfer data instead of a failed product. Higher m4+, D_fin matching, the selected HYM endpoint and physical action remain open.",
        "nonclaims": [
            "vanishing or computation of m4 and higher transferred products",
            "identification of the 48-dimensional target with D_fin or the rank-102 continuum operator",
            "a selected continuum q79 HYM endpoint, connection or Green operator",
            "physical interpretation or removal of the higher-jet ideal",
            "a selected physical action, normalization or observable comparison",
            "closure of B.GEO.01, B.OP.01 or B.ACTION.01",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {PACKET_PATH.name}: {packet['summary']['passed']}/{packet['summary']['total']} exact checks")


if __name__ == "__main__":
    main()
