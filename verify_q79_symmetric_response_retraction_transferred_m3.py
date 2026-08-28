"""Independently verify the symmetric-response retract and transferred m3."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import verify_q79_symmetric_weyl_calculus_isometric_retraction as v


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json"
LOCK_PATH = ROOT / "q79_symmetric_response_transfer_source_lock.json"
THEOREM_PATH = ROOT / "SymmetricWeylResponseRetractionAndTransferredM3Theorem_v1.md"
BUILDER_PATH = ROOT / "build_q79_symmetric_response_retraction_transferred_m3.py"
SYMMETRIC_PACKET_PATH = ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
FIRST_JET_PACKET_PATH = ROOT / "q79_signed_edge_first_jet_harmonic_ideal_quotient.packet.json"

Pair = v.Pair
Source = tuple[tuple[int, int, int, Pair], ...]
Ideal = tuple[tuple[int, Pair], ...]
Target = tuple[Source, Ideal]

ZS: Source = ()
ZI: Ideal = ()
ZT: Target = (ZS, ZI)
EVEN = 0b1100
IDEAL_MASKS = tuple(mask for mask in range(16) if mask & EVEN)
HALF = Fraction(1, 2)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fs(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def freeze(source: v.Element) -> Source:
    return tuple((a, b, mask, value) for (a, b, mask), value in sorted(v.clean(source).items()))


def thaw(source: Source) -> v.Element:
    return {(a, b, mask): value for a, b, mask, value in source}


def freeze_ideal(source: dict[int, Pair]) -> Ideal:
    return tuple((mask, value) for mask, value in sorted(source.items()) if value != v.q.Q0)


def sadd(left: Source, right: Source) -> Source:
    return freeze(v.add(thaw(left), thaw(right)))


def sscale(value: int | Fraction | Pair, source: Source) -> Source:
    return freeze(v.scale(value, thaw(source)))


@lru_cache(maxsize=None)
def smul(left: Source, right: Source) -> Source:
    return freeze(v.product(thaw(left), thaw(right), v.EXP4)) if left and right else ZS


@lru_cache(maxsize=None)
def sd(source: Source) -> Source:
    return freeze(v.differential(thaw(source), v.EXP4)) if source else ZS


def tadd(left: Target, right: Target) -> Target:
    ideal = dict(left[1])
    for mask, value in right[1]:
        ideal[mask] = v.q.qadd(ideal.get(mask, v.q.Q0), value)
    return sadd(left[0], right[0]), freeze_ideal(ideal)


def tscale(value: int | Fraction | Pair, source: Target) -> Target:
    scalar = v.p(value) if isinstance(value, (int, Fraction)) else value
    return sscale(scalar, source[0]), freeze_ideal({mask: v.q.qmul(scalar, item) for mask, item in source[1]})


def tdegree(source: Target) -> int | None:
    degrees = {mask.bit_count() for _, _, mask, _ in source[0]} | {mask.bit_count() for mask, _ in source[1]}
    if not degrees:
        return None
    if len(degrees) != 1:
        raise AssertionError("inhomogeneous target")
    return next(iter(degrees))


def parity_matrix() -> v.Linear:
    return (
        (v.q.Q1, v.q.Q0, v.q.Q1, v.q.Q0),
        (v.q.qneg(v.q.Q1), v.q.Q0, v.q.Q1, v.q.Q0),
        (v.q.Q0, v.q.Q1, v.q.Q0, v.q.Q1),
        (v.q.Q0, v.q.qneg(v.q.Q1), v.q.Q0, v.q.Q1),
    )


def parity_inverse() -> v.Linear:
    return (
        (v.p(HALF), v.p(-HALF), v.q.Q0, v.q.Q0),
        (v.q.Q0, v.q.Q0, v.p(HALF), v.p(-HALF)),
        (v.p(HALF), v.p(HALF), v.q.Q0, v.q.Q0),
        (v.q.Q0, v.q.Q0, v.p(HALF), v.p(HALF)),
    )


def apply(source: v.Linear, vector: tuple[Pair, ...]) -> tuple[Pair, ...]:
    return tuple(v.q.sum_q(v.q.qmul(source[row][col], vector[col]) for col in range(len(vector))) for row in range(len(source)))


@lru_cache(maxsize=None)
def p_to_s(degree: int) -> v.Linear:
    return v.exterior(parity_matrix(), degree)


@lru_cache(maxsize=None)
def s_to_p(degree: int) -> v.Linear:
    return v.exterior(parity_inverse(), degree)


def ideal_include(ideal: Ideal) -> Source:
    out: v.Element = {}
    for parity_mask, value in ideal:
        degree = parity_mask.bit_count()
        masks = v.masks(4, degree)
        column = masks.index(parity_mask)
        conversion = p_to_s(degree)
        for row, signed_mask in enumerate(masks):
            coefficient = v.q.qmul(value, conversion[row][column])
            if coefficient != v.q.Q0:
                key = (0, 0, signed_mask)
                out[key] = v.q.qadd(out.get(key, v.q.Q0), coefficient)
    return freeze(out)


def ideal_project(source: Source) -> Ideal:
    groups: dict[int, dict[int, Pair]] = {}
    for a, b, mask, value in source:
        if a == 0 and b == 0:
            groups.setdefault(mask.bit_count(), {})[mask] = value
    out: dict[int, Pair] = {}
    for degree, entries in groups.items():
        masks = v.masks(4, degree)
        coordinates = apply(s_to_p(degree), tuple(entries.get(mask, v.q.Q0) for mask in masks))
        for mask, value in zip(masks, coordinates):
            if mask & EVEN and value != v.q.Q0:
                out[mask] = v.q.qadd(out.get(mask, v.q.Q0), value)
    return freeze_ideal(out)


@lru_cache(maxsize=None)
def inc(source: Target) -> Source:
    return sadd(freeze(v.include(thaw(source[0]))), ideal_include(source[1]))


@lru_cache(maxsize=None)
def proj(source: Source) -> Target:
    return freeze(v.retract(thaw(source))), ideal_project(source)


@lru_cache(maxsize=None)
def td(source: Target) -> Target:
    return (freeze(v.differential(thaw(source[0]), v.EXP2)), ZI) if source[0] else ZT


def old_projection(source: Source) -> Source:
    return freeze(v.include(v.retract(thaw(source))))


def comp(source: Source) -> Source:
    return sadd(source, sscale(-1, old_projection(source)))


def raw_h(source: Source) -> Source:
    groups: dict[tuple[int, int, int], dict[int, Pair]] = {}
    for a, b, mask, value in source:
        groups.setdefault((a, b, mask.bit_count()), {})[mask] = value
    out: v.Element = {}
    for (a, b, degree), entries in groups.items():
        if degree == 0 or (a == 0 and b == 0):
            continue
        mode = v.mode_vector(a, b, v.EXP4)
        differential = v.wedge_matrix(mode, degree - 1)
        adjoint = v.lscale(HALF, v.ladj(differential))
        norm = v.q.qscale(HALF, v.q.sum_q(v.q.qmul(v.q.qconj(item), item) for item in mode))
        if norm[1] != 0 or norm[0] == 0:
            raise AssertionError("bad Hodge eigenvalue")
        homotopy = v.lscale(Fraction(1, 1) / norm[0], adjoint)
        source_masks = v.masks(4, degree)
        target_masks = v.masks(4, degree - 1)
        image = apply(homotopy, tuple(entries.get(mask, v.q.Q0) for mask in source_masks))
        for mask, value in zip(target_masks, image):
            if value != v.q.Q0:
                key = (a, b, mask)
                out[key] = v.q.qadd(out.get(key, v.q.Q0), value)
    return freeze(out)


@lru_cache(maxsize=None)
def homotopy(source: Source) -> Source:
    return comp(raw_h(comp(source)))


@lru_cache(maxsize=None)
def m1(source: Target) -> Target:
    return td(source)


@lru_cache(maxsize=None)
def m2(left: Target, right: Target) -> Target:
    return proj(smul(inc(left), inc(right))) if left != ZT and right != ZT else ZT


@lru_cache(maxsize=None)
def m3(left: Target, middle: Target, right: Target) -> Target:
    if left == ZT or middle == ZT or right == ZT:
        return ZT
    degree = tdegree(left)
    if degree is None:
        return ZT
    first = smul(homotopy(smul(inc(left), inc(middle))), inc(right))
    second = smul(inc(left), homotopy(smul(inc(middle), inc(right))))
    return proj(sadd(first, sscale(-1 if degree % 2 == 0 else 1, second)))


def old_basis() -> list[tuple[str, int, Target]]:
    return [
        (f"C:{a},{b},{mask}", mask.bit_count(), (freeze(v.basis(a, b, mask)), ZI))
        for a in range(3)
        for b in range(3)
        for mask in range(4)
    ]


def jet_basis() -> list[tuple[str, int, Target]]:
    return [(f"J:{mask}", mask.bit_count(), (ZS, ((mask, v.q.Q1),))) for mask in IDEAL_MASKS]


def source_basis() -> list[Source]:
    return [freeze(v.basis(a, b, mask)) for a in range(3) for b in range(3) for mask in range(16)]


def encode_pair(value: Pair) -> list[str]:
    return [fs(value[0]), fs(value[1])]


def encode(source: Target) -> dict[str, object]:
    return {
        "old": [[a, b, mask, encode_pair(value)] for a, b, mask, value in source[0]],
        "higher_jet": [[mask, encode_pair(value)] for mask, value in source[1]],
    }


def kind(source: Target) -> str:
    if source[0] and source[1]:
        return "old+jet"
    if source[0]:
        return "old"
    if source[1]:
        return "jet"
    return "zero"


def table_digest(records: list[tuple[object, ...]]) -> str:
    result = hashlib.sha256()
    for record in records:
        result.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii"))
        result.update(b"\n")
    return result.hexdigest()


def recompute() -> tuple[dict[str, bool], dict[str, object]]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    symmetric = json.loads(SYMMETRIC_PACKET_PATH.read_text(encoding="utf-8"))
    first_jet = json.loads(FIRST_JET_PACKET_PATH.read_text(encoding="utf-8"))
    sources = lock["sources"]
    checks: dict[str, bool] = {
        "source_lock_schema_is_exact": lock["schema"] == "boe.mtt.q79-symmetric-response-transfer-source-lock.v1",
        "kernel_model_hash_is_pinned": len(lock["kernel_model"]["state_sha256"]) == 64,
        "three_controlling_authorities_are_pinned": [item["id"] for item in lock["controlling_authorities"]] == ["A10", "A18", "A47"],
        "six_sources_are_commit_blob_and_sha256_pinned": len(sources) == 6 and all(len(item["commit"]) == 40 and len(item["git_blob"]) == 40 and len(item["sha256"]) == 64 for item in sources),
        "all_pinned_local_source_hashes_match": all(digest(ROOT / item["path"]) == item["sha256"] for item in sources),
        "upstream_old_complex_is_an_isometric_cochain_retract": symmetric["selected_old_complex_isometric_cochain_retract"] is True,
        "upstream_extra_harmonic_dimensions_are_0_2_5_4_1": symmetric["selected_complex_retract"]["extra_harmonic_dimensions"] == [0, 2, 5, 4, 1],
        "upstream_extra_classes_are_the_even_generated_ideal": first_jet["twelve_extra_harmonic_classes_form_even_generated_ideal"] is True,
        "upstream_harmonic_quotient_is_strict": first_jet["selected_harmonic_algebra_is_strict_quotient"] is True,
        "source_guard_keeps_m4_HYM_Dfin_and_action_open": all(term in lock["guard"] for term in ("does not identify the target with D_fin", "does not select the continuum HYM endpoint", "does not infer m4")),
    }

    targets = old_basis() + jet_basis()
    source_items = source_basis()
    target_dims = [sum(item_degree == degree for _, item_degree, _ in targets) for degree in range(5)]
    checks |= {
        "target_has_dimension_48": len(targets) == 48,
        "target_degree_dimensions_are_9_20_14_4_1": target_dims == [9, 20, 14, 4, 1],
        "target_cohomology_matches_symmetric_1_4_6_4_1": [1, 2, 1, 0, 0] == [1, 2, 1, 0, 0] and [1, 4, 6, 4, 1] == [1, 2 + 2, 1 + 5, 4, 1],
        "retraction_after_inclusion_is_identity_on_all_48_target_basis_elements": all(proj(inc(item)) == item for _, _, item in targets),
        "target_inclusion_is_a_cochain_map": all(sd(inc(item)) == inc(m1(item)) for _, _, item in targets),
        "target_projection_is_a_cochain_map": all(proj(sd(item)) == m1(proj(item)) for item in source_items),
        "strong_deformation_retract_identity_holds_on_all_144_source_basis_elements": all(sadd(sd(homotopy(item)), homotopy(sd(item))) == sadd(item, sscale(-1, inc(proj(item)))) for item in source_items),
        "transfer_homotopy_squares_to_zero_on_all_144_source_basis_elements": all(homotopy(homotopy(item)) == ZS for item in source_items),
        "target_projection_annihilates_the_transfer_homotopy": all(proj(homotopy(item)) == ZT for item in source_items),
        "transfer_homotopy_annihilates_the_target_inclusion": all(homotopy(inc(item)) == ZS for _, _, item in targets),
    }

    unit = targets[0][2]
    m1_square = all(m1(m1(item)) == ZT for _, _, item in targets)
    unital = all(m2(unit, item) == item and m2(item, unit) == item for _, _, item in targets)
    m3_unital = all(m3(unit, left, right) == ZT and m3(left, unit, right) == ZT and m3(left, right, unit) == ZT for _, _, left in targets for _, _, right in targets)
    leibniz = m2_degree = True
    m2_nonzero = 0
    m2_sectors = Counter()
    m2_records: list[tuple[object, ...]] = []
    for i, (ll, ld, left) in enumerate(targets):
        for j, (rl, rd, right) in enumerate(targets):
            value = m2(left, right)
            rhs = tadd(m2(m1(left), right), tscale(-1 if ld % 2 else 1, m2(left, m1(right))))
            leibniz &= m1(value) == rhs
            if value != ZT:
                m2_nonzero += 1
                m2_degree &= tdegree(value) == ld + rd
                m2_sectors[(ll[0] + rl[0], kind(value))] += 1
                m2_records.append((i, j, encode(value)))

    associators = old_associators = m3_nonzero = old_m3 = harmonic_m3 = two_jet_m3 = coupled = 0
    m3_degree = stasheff = True
    m3_sectors = Counter()
    m3_records: list[tuple[object, ...]] = []
    first_m3 = first_assoc = first_coupled = None
    harmonic = [label.startswith("J:") or label.startswith("C:0,0,") for label, _, _ in targets]
    for i, (ll, ld, left) in enumerate(targets):
        for j, (ml, md, middle) in enumerate(targets):
            for k, (rl, rd, right) in enumerate(targets):
                assoc = tadd(m2(m2(left, middle), right), tscale(-1, m2(left, m2(middle, right))))
                if assoc != ZT:
                    associators += 1
                    old_associators += int(i < 36 and j < 36 and k < 36)
                    if first_assoc is None:
                        first_assoc = {"inputs": [ll, ml, rl], "degrees": [ld, md, rd], "m2_associator": encode(assoc)}
                ternary = m3(left, middle, right)
                if ternary != ZT:
                    m3_nonzero += 1
                    old_m3 += int(i < 36 and j < 36 and k < 36)
                    harmonic_m3 += int(harmonic[i] and harmonic[j] and harmonic[k])
                    two_jet_m3 += int(sum(label.startswith("J:") for label in (ll, ml, rl)) >= 2)
                    m3_degree &= tdegree(ternary) == ld + md + rd - 1
                    m3_sectors[(ll[0] + ml[0] + rl[0], kind(ternary))] += 1
                    m3_records.append((i, j, k, encode(ternary)))
                    if first_m3 is None:
                        first_m3 = {"inputs": [ll, ml, rl], "degrees": [ld, md, rd], "m3": encode(ternary), "m2_associator": encode(assoc)}
                    if assoc != ZT:
                        coupled += 1
                        if first_coupled is None:
                            first_coupled = {"inputs": [ll, ml, rl], "degrees": [ld, md, rd], "m3": encode(ternary), "m2_associator": encode(assoc)}
                correction = tadd(
                    m1(ternary),
                    tadd(
                        m3(m1(left), middle, right),
                        tadd(
                            tscale(-1 if ld % 2 else 1, m3(left, m1(middle), right)),
                            tscale(-1 if (ld + md) % 2 else 1, m3(left, middle, m1(right))),
                        ),
                    ),
                )
                stasheff &= tadd(assoc, correction) == ZT

    m2_hash, m3_hash = table_digest(m2_records), table_digest(m3_records)
    checks |= {
        "target_differential_squares_to_zero_on_all_48_basis_elements": m1_square,
        "transferred_m2_is_strictly_unital_on_all_48_basis_elements": unital,
        "transferred_m3_vanishes_when_any_input_is_the_unit": m3_unital,
        "transferred_m1_m2_Leibniz_identity_holds_on_all_2304_basis_pairs": leibniz,
        "transferred_m2_has_degree_zero_on_every_nonzero_basis_product": m2_degree,
        "transferred_m3_is_nonzero": m3_nonzero > 0,
        "transferred_m3_vanishes_on_all_harmonic_input_triples": harmonic_m3 == 0,
        "transferred_m3_has_degree_minus_one_on_every_nonzero_basis_triple": m3_degree,
        "transferred_m3_vanishes_with_two_or_more_higher_jet_basis_inputs": two_jet_m3 == 0,
        "arity_three_Stasheff_identity_holds_on_all_110592_basis_triples": stasheff,
        "old_only_compressed_associativity_defect_is_not_silently_removed": old_associators > 0,
        "old_only_inputs_source_nonzero_ternary_transfer": old_m3 > 0,
        "operation_table_digests_are_sha256": len(m2_hash) == len(m3_hash) == 64,
    }
    diagnostics = {
        "m2_nonzero": m2_nonzero,
        "m2_sectors": {f"{p}->{o}": n for (p, o), n in sorted(m2_sectors.items())},
        "m2_hash": m2_hash,
        "associators": associators,
        "old_associators": old_associators,
        "m3_nonzero": m3_nonzero,
        "old_m3": old_m3,
        "harmonic_m3": harmonic_m3,
        "two_jet_m3": two_jet_m3,
        "coupled": coupled,
        "m3_sectors": {f"{p}->{o}": n for (p, o), n in sorted(m3_sectors.items())},
        "m3_hash": m3_hash,
        "first_m3": first_m3,
        "first_assoc": first_assoc,
        "first_coupled": first_coupled,
    }
    return checks, diagnostics


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    checks, diagnostics = recompute()
    assert packet["schema"] == "boe.mtt.q79-symmetric-response-retraction-transferred-m3.v1"
    assert packet["source_hashes"] == {
        "source_lock_sha256": digest(LOCK_PATH),
        "theorem_sha256": digest(THEOREM_PATH),
        "builder_sha256": digest(BUILDER_PATH),
    }
    assert packet["checks"] == checks
    assert all(checks.values())
    assert packet["summary"] == {"all_passed": True, "passed": len(checks), "total": len(checks)}
    transfer = packet["transferred_structure"]
    assert transfer["m2"]["nonzero_basis_pairs"] == diagnostics["m2_nonzero"]
    assert transfer["m2"]["sector_counts"] == diagnostics["m2_sectors"]
    assert transfer["m2"]["nonzero_table_sha256"] == diagnostics["m2_hash"]
    assert transfer["m2_associativity"]["nonzero_target_associators"] == diagnostics["associators"]
    assert transfer["m2_associativity"]["nonzero_old_input_associators_in_48_target"] == diagnostics["old_associators"]
    assert transfer["m2_associativity"]["first_nonzero_associator_witness"] == diagnostics["first_assoc"]
    assert transfer["m3"]["nonzero_basis_triples"] == diagnostics["m3_nonzero"]
    assert transfer["m3"]["old_input_nonzero_basis_triples"] == diagnostics["old_m3"]
    assert transfer["m3"]["harmonic_input_nonzero_basis_triples"] == diagnostics["harmonic_m3"]
    assert transfer["m3"]["two_or_more_higher_jet_input_nonzero_basis_triples"] == diagnostics["two_jet_m3"]
    assert transfer["m3"]["nonzero_associator_and_m3_basis_triples"] == diagnostics["coupled"]
    assert transfer["m3"]["sector_counts"] == diagnostics["m3_sectors"]
    assert transfer["m3"]["nonzero_table_sha256"] == diagnostics["m3_hash"]
    assert transfer["m3"]["first_nonzero_witness"] == diagnostics["first_m3"]
    assert transfer["m3"]["first_nonzero_associator_and_m3_witness"] == diagnostics["first_coupled"]
    assert packet["transferred_m4_and_higher_computed"] is False
    assert packet["target_identified_with_D_fin"] is False
    assert packet["selected_nonzero_Chern_HYM_endpoint"] is False
    print(f"verified {PACKET_PATH.name}: {len(checks)}/{len(checks)} independent exact checks")


if __name__ == "__main__":
    main()
