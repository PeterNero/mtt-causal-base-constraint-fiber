"""Independently verify the transferred m4 packet, with optional full replay."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import verify_q79_symmetric_response_retraction_transferred_m3 as low


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_symmetric_response_higher_transfer_source_lock.json"
THEOREM_PATH = ROOT / "SymmetricWeylTransferredM4AndArityFourStasheffTheorem_v1.md"
PACKET_PATH = ROOT / "q79_symmetric_response_transferred_m4.packet.json"
LOW_PACKET_PATH = ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json"

Source = low.Source
Target = low.Target
Pair = low.Pair
ZS = low.ZS
ZT = low.ZT

BASIS = low.old_basis() + low.jet_basis()
LABELS = tuple(label for label, _, _ in BASIS)
DEGREES = tuple(degree for _, degree, _ in BASIS)
TARGETS = tuple(target for _, _, target in BASIS)
INCLUSIONS = tuple(low.inc(target) for target in TARGETS)
COUNT = len(BASIS)
UNIT = 0

OLD_INDICES = {
    (a, b, mask): index
    for index, (_, _, target) in enumerate(BASIS)
    for a, b, mask, _ in target[0]
}
JET_INDICES = {
    mask: index
    for index, (_, _, target) in enumerate(BASIS)
    for mask, _ in target[1]
}

Coordinates = tuple[tuple[int, Pair], ...]
ZC: Coordinates = ()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_mul(left: Source, right: Source) -> Source:
    if not left or not right:
        return ZS
    return low.freeze(low.v.product(low.thaw(left), low.thaw(right), low.v.EXP4))


def raw_proj(source: Source) -> Target:
    if not source:
        return ZT
    return low.freeze(low.v.retract(low.thaw(source))), low.ideal_project(source)


@lru_cache(maxsize=400_000)
def projected_product(left: Source, right: Source) -> Target:
    return raw_proj(raw_mul(left, right))


def source_sum(*terms: Source) -> Source:
    result = ZS
    for term in terms:
        result = low.sadd(result, term)
    return result


def target_sum(*terms: Target) -> Target:
    result = ZT
    for term in terms:
        result = low.tadd(result, term)
    return result


def target_coordinates(source: Target) -> Coordinates:
    out: list[tuple[int, Pair]] = []
    for a, b, mask, value in source[0]:
        out.append((OLD_INDICES[(a, b, mask)], value))
    for mask, value in source[1]:
        out.append((JET_INDICES[mask], value))
    return tuple(sorted(out))


def cadd(*terms: Coordinates) -> Coordinates:
    out: dict[int, Pair] = {}
    for term in terms:
        for index, value in term:
            out[index] = low.v.q.qadd(out.get(index, low.v.q.Q0), value)
    return tuple((index, value) for index, value in sorted(out.items()) if value != low.v.q.Q0)


def cscale(value: int | Fraction | Pair, source: Coordinates) -> Coordinates:
    scalar = low.v.p(value) if isinstance(value, (int, Fraction)) else value
    return tuple(
        (index, low.v.q.qmul(scalar, coefficient))
        for index, coefficient in source
        if low.v.q.qmul(scalar, coefficient) != low.v.q.Q0
    )


def csubstitute(source: Coordinates, operation: object) -> Coordinates:
    return cadd(*(cscale(coefficient, operation(index)) for index, coefficient in source))


@lru_cache(maxsize=None)
def h2(left: int, right: int) -> Source:
    return low.homotopy(raw_mul(INCLUSIONS[left], INCLUSIONS[right]))


@lru_cache(maxsize=None)
def lambda3(left: int, middle: int, right: int) -> Source:
    first = raw_mul(h2(left, middle), INCLUSIONS[right])
    second = raw_mul(INCLUSIONS[left], h2(middle, right))
    sign = -1 if DEGREES[left] % 2 == 0 else 1
    return source_sum(first, low.sscale(sign, second))


@lru_cache(maxsize=None)
def h3(left: int, middle: int, right: int) -> Source:
    return low.homotopy(lambda3(left, middle, right))


def m4(left: int, second: int, third: int, right: int) -> Target:
    degree = DEGREES[left] + DEGREES[second] + DEGREES[third] + DEGREES[right] - 2
    if degree < 0 or degree > 4:
        return ZT
    first = projected_product(h3(left, second, third), INCLUSIONS[right])
    balanced = projected_product(h2(left, second), h2(third, right))
    final = projected_product(INCLUSIONS[left], h3(second, third, right))
    middle_sign = -1 if (DEGREES[left] + DEGREES[second]) % 2 == 0 else 1
    return target_sum(
        low.tscale(-1, first),
        low.tscale(middle_sign, balanced),
        low.tscale(-1, final),
    )


@lru_cache(maxsize=200_000)
def m4c(left: int, second: int, third: int, right: int) -> Coordinates:
    return target_coordinates(m4(left, second, third, right))


@lru_cache(maxsize=None)
def m1c(index: int) -> Coordinates:
    return target_coordinates(low.m1(TARGETS[index]))


@lru_cache(maxsize=None)
def m2c(left: int, right: int) -> Coordinates:
    return target_coordinates(low.m2(TARGETS[left], TARGETS[right]))


@lru_cache(maxsize=None)
def m3c(left: int, middle: int, right: int) -> Coordinates:
    return target_coordinates(low.m3(TARGETS[left], TARGETS[middle], TARGETS[right]))


def m4_m1(indices: tuple[int, int, int, int], slot: int) -> Coordinates:
    terms: list[Coordinates] = []
    for replacement, coefficient in m1c(indices[slot]):
        amended = list(indices)
        amended[slot] = replacement
        terms.append(cscale(coefficient, m4c(*amended)))
    return cadd(*terms)


def si4(indices: tuple[int, int, int, int]) -> Coordinates:
    a, b, c, d = indices
    da, db, dc = DEGREES[a], DEGREES[b], DEGREES[c]
    return cadd(
        csubstitute(m4c(*indices), m1c),
        cscale(-1, csubstitute(m3c(a, b, c), lambda output: m2c(output, d))),
        cscale(-1 if da % 2 == 0 else 1, csubstitute(m3c(b, c, d), lambda output: m2c(a, output))),
        csubstitute(m2c(a, b), lambda output: m3c(output, c, d)),
        cscale(-1, csubstitute(m2c(b, c), lambda output: m3c(a, output, d))),
        csubstitute(m2c(c, d), lambda output: m3c(a, b, output)),
        cscale(-1, m4_m1(indices, 0)),
        cscale(-1 if da % 2 == 0 else 1, m4_m1(indices, 1)),
        cscale(-1 if (da + db) % 2 == 0 else 1, m4_m1(indices, 2)),
        cscale(-1 if (da + db + dc) % 2 == 0 else 1, m4_m1(indices, 3)),
    )


def admissible(indices: tuple[int, int, int, int]) -> bool:
    return 2 <= sum(DEGREES[index] for index in indices) <= 6


def harmonic(index: int) -> bool:
    return LABELS[index].startswith("J:") or LABELS[index].startswith("C:0,0,")


def sector(indices: tuple[int, int, int, int]) -> str:
    return "".join("J" if LABELS[index].startswith("J:") else "C" for index in indices)


def encode_pair(value: Pair) -> list[str]:
    return [low.fs(value[0]), low.fs(value[1])]


def encode_coordinates(source: Coordinates) -> list[list[object]]:
    return [[index, encode_pair(value)] for index, value in source]


def target_from_coordinates(source: Coordinates) -> Target:
    return target_sum(*(low.tscale(value, TARGETS[index]) for index, value in source))


def digest_record(digest: object, record: tuple[object, ...]) -> None:
    digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def source_hashes_match(lock: dict[str, object]) -> bool:
    return all(sha256(ROOT / source["path"]) == source["sha256"] for source in lock["sources"])


def deterministic_sample(size: int) -> list[tuple[int, int, int, int]]:
    rng = random.Random(44879)
    out: list[tuple[int, int, int, int]] = []
    seen: set[tuple[int, int, int, int]] = set()
    while len(out) < size:
        indices = tuple(rng.randrange(COUNT) for _ in range(4))
        if indices not in seen and admissible(indices):
            seen.add(indices)
            out.append(indices)
    return out


def quick_verify(packet: dict[str, object], lock: dict[str, object]) -> dict[str, bool]:
    execution = packet["execution"]
    m4_packet = execution["m4"]
    witness = tuple(m4_packet["first_nonzero_witness"]["input_indices"])
    mixed = tuple(m4_packet["first_mixed_old_higher_jet_witness"]["input_indices"])

    m3_match = all(
        raw_proj(lambda3(a, b, c)) == low.m3(TARGETS[a], TARGETS[b], TARGETS[c])
        for a, b, c in itertools.product(range(COUNT), repeat=3)
    )
    sample = deterministic_sample(4096)
    si4_sample = all(not si4(indices) for indices in sample)

    harmonics = [index for index in range(COUNT) if harmonic(index)]
    all_harmonic_zero = all(
        not m4c(*indices) for indices in itertools.product(harmonics, repeat=4)
    )

    jet = list(range(36, 48))
    old = list(range(36))
    three_jet_zero = True
    for old_slot in range(4):
        for old_index in old:
            for jet_inputs in itertools.product(jet, repeat=3):
                indices = list(jet_inputs)
                indices.insert(old_slot, old_index)
                if m4c(*indices):
                    three_jet_zero = False
                    break
            if not three_jet_zero:
                break
        if not three_jet_zero:
            break
    four_jet_zero = all(not m4c(*indices) for indices in itertools.product(jet, repeat=4))

    return {
        "packet_schema_is_exact": packet["schema"] == "boe.mtt.q79-symmetric-response-transferred-m4.v1",
        "packet_passes_21_of_21_checks": packet["summary"]
        == {"all_passed": True, "passed": 21, "total": 21},
        "all_packet_checks_are_true": all(packet["checks"].values()),
        "source_lock_hash_matches": packet["source_lock_sha256"] == sha256(LOCK_PATH),
        "theorem_hash_matches": packet["theorem_sha256"] == sha256(THEOREM_PATH),
        "prior_packet_hash_matches": packet["prior_packet_sha256"] == sha256(LOW_PACKET_PATH),
        "all_pinned_source_hashes_match": source_hashes_match(lock),
        "independent_lambda3_calibration_matches_all_110592_prior_values": m3_match,
        "first_nonzero_witness_recomputes_exactly": encode_coordinates(m4c(*witness))
        == m4_packet["first_nonzero_witness"]["m4_coordinates"],
        "first_mixed_witness_recomputes_exactly": encode_coordinates(m4c(*mixed))
        == m4_packet["first_mixed_old_higher_jet_witness"]["m4_coordinates"],
        "independent_4096_quadruple_SI4_sample_has_zero_residual": si4_sample,
        "independent_all_harmonic_cutset_is_zero": all_harmonic_zero,
        "independent_three_higher_jet_cutset_is_zero": three_jet_zero,
        "independent_four_higher_jet_cutset_is_zero": four_jet_zero,
        "packet_nonzero_count_is_693208": m4_packet["nonzero_basis_quadruples"] == 693208,
        "packet_digest_is_sha256": len(m4_packet["nonzero_table_sha256"]) == 64,
        "physical_promotion_remains_false": not any(
            packet[key]
            for key in (
                "target_identified_with_D_fin",
                "selected_nonzero_Chern_HYM_endpoint",
                "physical_action_selected",
                "physical_vertex_claimed",
            )
        ),
    }


def full_recompute(packet: dict[str, object]) -> dict[str, object]:
    nonzero = unit_nonzero = harmonic_nonzero = three_jet_nonzero = failures = admissible_count = 0
    jet_counts: Counter[int] = Counter()
    sector_counts: Counter[tuple[str, str]] = Counter()
    output_counts: Counter[str] = Counter()
    table_hash = hashlib.sha256()

    for indices in itertools.product(range(COUNT), repeat=4):
        if not admissible(indices):
            continue
        admissible_count += 1
        coordinates = m4c(*indices)
        if coordinates:
            nonzero += 1
            value = target_from_coordinates(coordinates)
            pattern = sector(indices)
            output = low.kind(value)
            jet_count = pattern.count("J")
            jet_counts[jet_count] += 1
            sector_counts[(pattern, output)] += 1
            output_counts[output] += 1
            unit_nonzero += int(UNIT in indices)
            harmonic_nonzero += int(all(harmonic(index) for index in indices))
            three_jet_nonzero += int(jet_count >= 3)
            digest_record(table_hash, (*indices, encode_coordinates(coordinates)))
        failures += int(bool(si4(indices)))

    result = {
        "degree_admissible_basis_quadruples": admissible_count,
        "nonzero_basis_quadruples": nonzero,
        "unit_input_nonzero_basis_quadruples": unit_nonzero,
        "all_harmonic_input_nonzero_basis_quadruples": harmonic_nonzero,
        "three_or_more_higher_jet_input_nonzero_basis_quadruples": three_jet_nonzero,
        "higher_jet_input_count_distribution": {
            str(key): value for key, value in sorted(jet_counts.items())
        },
        "input_sector_output_counts": {
            f"{pattern}->{output}": value
            for (pattern, output), value in sorted(sector_counts.items())
        },
        "output_kind_counts": dict(sorted(output_counts.items())),
        "nonzero_table_sha256": table_hash.hexdigest(),
        "arity_four_residual_failures": failures,
    }

    expected = packet["execution"]["m4"]
    assert result["degree_admissible_basis_quadruples"] == packet["execution"]["basis"][
        "degree_admissible_basis_quadruples"
    ]
    for key in (
        "nonzero_basis_quadruples",
        "unit_input_nonzero_basis_quadruples",
        "all_harmonic_input_nonzero_basis_quadruples",
        "three_or_more_higher_jet_input_nonzero_basis_quadruples",
        "higher_jet_input_count_distribution",
        "input_sector_output_counts",
        "output_kind_counts",
        "nonzero_table_sha256",
    ):
        assert result[key] == expected[key]
    assert failures == packet["execution"]["arity_four"]["residual_failures"] == 0
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    checks = quick_verify(packet, lock)
    assert all(checks.values()), [name for name, passed in checks.items() if not passed]
    if args.recompute:
        result = full_recompute(packet)
        print(
            f"fully recomputed {PACKET_PATH.name}: "
            f"{result['nonzero_basis_quadruples']} nonzero m4 values, 0 SI(4) failures"
        )
    else:
        print(f"verified {PACKET_PATH.name}: {sum(checks.values())}/{len(checks)} independent checks")


if __name__ == "__main__":
    main()
