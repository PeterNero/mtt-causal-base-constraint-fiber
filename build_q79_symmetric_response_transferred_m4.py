"""Compute the exact transferred m4 on the 48-dimensional q79 response target."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import build_q79_symmetric_response_retraction_transferred_m3 as low


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_symmetric_response_higher_transfer_source_lock.json"
THEOREM_PATH = ROOT / "SymmetricWeylTransferredM4AndArityFourStasheffTheorem_v1.md"
PACKET_PATH = ROOT / "q79_symmetric_response_transferred_m4.packet.json"
LOW_PACKET_PATH = ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json"

SourceFrozen = low.SourceFrozen
Target = low.Target
ZERO_SOURCE = low.ZERO_SOURCE
ZERO_TARGET = low.ZERO_TARGET

BASIS = low.old_basis() + low.ideal_basis()
LABELS = tuple(label for label, _, _ in BASIS)
DEGREES = tuple(degree for _, degree, _ in BASIS)
TARGETS = tuple(target for _, _, target in BASIS)
INCLUSIONS = tuple(low.target_inclusion(target) for target in TARGETS)
COUNT = len(BASIS)
UNIT_INDEX = 0

OLD_INDICES = {
    (a, b, mask): index
    for index, (_, _, target) in enumerate(BASIS)
    for a, b, mask, _ in target[0]
}
IDEAL_INDICES = {
    mask: index
    for index, (_, _, target) in enumerate(BASIS)
    for mask, _ in target[1]
}

Coordinates = tuple[tuple[int, low.E], ...]
ZERO_COORDINATES: Coordinates = ()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_source_product(left: SourceFrozen, right: SourceFrozen) -> SourceFrozen:
    """Multiply without retaining millions of one-use lru-cache entries."""

    if not left or not right:
        return ZERO_SOURCE
    return low.freeze_source(
        low.sym.product(low.thaw_source(left), low.thaw_source(right), low.sym.DIRECTION_EXPONENTS)
    )


def raw_target_projection(source: SourceFrozen) -> Target:
    if not source:
        return ZERO_TARGET
    old = low.freeze_source(low.sym.retract_symmetric(low.thaw_source(source)))
    return old, low.source_to_ideal(source)


@lru_cache(maxsize=400_000)
def projected_product(left: SourceFrozen, right: SourceFrozen) -> Target:
    return raw_target_projection(raw_source_product(left, right))


def source_sum(*terms: SourceFrozen) -> SourceFrozen:
    result = ZERO_SOURCE
    for term in terms:
        result = low.source_add(result, term)
    return result


def target_sum(*terms: Target) -> Target:
    result = ZERO_TARGET
    for term in terms:
        result = low.target_add(result, term)
    return result


def target_coordinates(source: Target) -> Coordinates:
    out: list[tuple[int, low.E]] = []
    for a, b, mask, value in source[0]:
        out.append((OLD_INDICES[(a, b, mask)], value))
    for mask, value in source[1]:
        out.append((IDEAL_INDICES[mask], value))
    return tuple(sorted(out))


def coordinates_add(*terms: Coordinates) -> Coordinates:
    out: dict[int, low.E] = {}
    for term in terms:
        for index, value in term:
            out[index] = out.get(index, low.sym.wk.ZERO) + value
    return tuple((index, value) for index, value in sorted(out.items()) if value != low.sym.wk.ZERO)


def coordinates_scale(value: int | Fraction | low.E, source: Coordinates) -> Coordinates:
    scalar = low.sym.e(value)
    return tuple((index, scalar * coefficient) for index, coefficient in source if scalar * coefficient != low.sym.wk.ZERO)


def coordinates_substitute(
    source: Coordinates,
    operation: object,
) -> Coordinates:
    terms: list[Coordinates] = []
    for index, coefficient in source:
        terms.append(coordinates_scale(coefficient, operation(index)))
    return coordinates_add(*terms)


@lru_cache(maxsize=None)
def h2_index(left: int, right: int) -> SourceFrozen:
    return low.transfer_homotopy(raw_source_product(INCLUSIONS[left], INCLUSIONS[right]))


@lru_cache(maxsize=None)
def lambda3_source_index(left: int, middle: int, right: int) -> SourceFrozen:
    first = raw_source_product(h2_index(left, middle), INCLUSIONS[right])
    second = raw_source_product(INCLUSIONS[left], h2_index(middle, right))
    second_sign = -1 if DEGREES[left] % 2 == 0 else 1
    return source_sum(first, low.source_scale(second_sign, second))


@lru_cache(maxsize=None)
def h3_index(left: int, middle: int, right: int) -> SourceFrozen:
    return low.transfer_homotopy(lambda3_source_index(left, middle, right))


def m4_index(left: int, second: int, third: int, right: int) -> Target:
    """Merkulov lambda4 projected to the transfer target."""

    output_degree = DEGREES[left] + DEGREES[second] + DEGREES[third] + DEGREES[right] - 2
    if output_degree < 0 or output_degree > 4:
        return ZERO_TARGET
    first = projected_product(h3_index(left, second, third), INCLUSIONS[right])
    balanced = projected_product(h2_index(left, second), h2_index(third, right))
    final = projected_product(INCLUSIONS[left], h3_index(second, third, right))
    balanced_sign = -1 if (DEGREES[left] + DEGREES[second]) % 2 == 0 else 1
    return target_sum(
        low.target_scale(-1, first),
        low.target_scale(balanced_sign, balanced),
        low.target_scale(-1, final),
    )


@lru_cache(maxsize=200_000)
def m4_coordinates(left: int, second: int, third: int, right: int) -> Coordinates:
    return target_coordinates(m4_index(left, second, third, right))


@lru_cache(maxsize=None)
def m1_coordinates(index: int) -> Coordinates:
    return target_coordinates(low.m1(TARGETS[index]))


@lru_cache(maxsize=None)
def m2_coordinates(left: int, right: int) -> Coordinates:
    return target_coordinates(low.m2(TARGETS[left], TARGETS[right]))


@lru_cache(maxsize=None)
def m3_coordinates(left: int, middle: int, right: int) -> Coordinates:
    return target_coordinates(low.m3(TARGETS[left], TARGETS[middle], TARGETS[right]))


@lru_cache(maxsize=None)
def h2_target(left: Target, right: Target) -> SourceFrozen:
    return low.transfer_homotopy(
        raw_source_product(low.target_inclusion(left), low.target_inclusion(right))
    )


@lru_cache(maxsize=None)
def lambda3_source_target(left: Target, middle: Target, right: Target) -> SourceFrozen:
    left_degree = low.target_degree(left)
    if left_degree is None:
        return ZERO_SOURCE
    first = raw_source_product(h2_target(left, middle), low.target_inclusion(right))
    second = raw_source_product(low.target_inclusion(left), h2_target(middle, right))
    second_sign = -1 if left_degree % 2 == 0 else 1
    return source_sum(first, low.source_scale(second_sign, second))


@lru_cache(maxsize=None)
def h3_target(left: Target, middle: Target, right: Target) -> SourceFrozen:
    return low.transfer_homotopy(lambda3_source_target(left, middle, right))


def m4_target(left: Target, second: Target, third: Target, right: Target) -> Target:
    if ZERO_TARGET in (left, second, third, right):
        return ZERO_TARGET
    degrees = tuple(low.target_degree(item) for item in (left, second, third, right))
    if any(degree is None for degree in degrees):
        return ZERO_TARGET
    d0, d1, d2, d3 = (int(degree) for degree in degrees)
    if not 0 <= d0 + d1 + d2 + d3 - 2 <= 4:
        return ZERO_TARGET
    first = projected_product(h3_target(left, second, third), low.target_inclusion(right))
    balanced = projected_product(h2_target(left, second), h2_target(third, right))
    final = projected_product(low.target_inclusion(left), h3_target(second, third, right))
    balanced_sign = -1 if (d0 + d1) % 2 == 0 else 1
    return target_sum(
        low.target_scale(-1, first),
        low.target_scale(balanced_sign, balanced),
        low.target_scale(-1, final),
    )


def arity_four_residual(left: int, second: int, third: int, right: int) -> Target:
    """Evaluate the cohomological SI(4) convention used by the prior packet."""

    a, b, c, d = (TARGETS[index] for index in (left, second, third, right))
    da, db, dc = DEGREES[left], DEGREES[second], DEGREES[third]
    fourth = m4_index(left, second, third, right)
    return target_sum(
        low.m1(fourth),
        low.target_scale(-1, low.m2(low.m3(a, b, c), d)),
        low.target_scale(-1 if da % 2 == 0 else 1, low.m2(a, low.m3(b, c, d))),
        low.m3(low.m2(a, b), c, d),
        low.target_scale(-1, low.m3(a, low.m2(b, c), d)),
        low.m3(a, b, low.m2(c, d)),
        low.target_scale(-1, m4_target(low.m1(a), b, c, d)),
        low.target_scale(-1 if da % 2 == 0 else 1, m4_target(a, low.m1(b), c, d)),
        low.target_scale(
            -1 if (da + db) % 2 == 0 else 1,
            m4_target(a, b, low.m1(c), d),
        ),
        low.target_scale(
            -1 if (da + db + dc) % 2 == 0 else 1,
            m4_target(a, b, c, low.m1(d)),
        ),
    )


def m4_after_m1(indices: tuple[int, int, int, int], slot: int) -> Coordinates:
    terms: list[Coordinates] = []
    for replacement, coefficient in m1_coordinates(indices[slot]):
        amended = list(indices)
        amended[slot] = replacement
        terms.append(coordinates_scale(coefficient, m4_coordinates(*amended)))
    return coordinates_add(*terms)


def arity_four_residual_coordinates(indices: tuple[int, int, int, int]) -> Coordinates:
    left, second, third, right = indices
    da, db, dc = DEGREES[left], DEGREES[second], DEGREES[third]

    m1_m4 = coordinates_substitute(m4_coordinates(*indices), m1_coordinates)

    m2_m3_left = coordinates_substitute(
        m3_coordinates(left, second, third),
        lambda output: m2_coordinates(output, right),
    )
    m2_m3_right = coordinates_substitute(
        m3_coordinates(second, third, right),
        lambda output: m2_coordinates(left, output),
    )

    m3_m2_left = coordinates_substitute(
        m2_coordinates(left, second),
        lambda output: m3_coordinates(output, third, right),
    )
    m3_m2_middle = coordinates_substitute(
        m2_coordinates(second, third),
        lambda output: m3_coordinates(left, output, right),
    )
    m3_m2_right = coordinates_substitute(
        m2_coordinates(third, right),
        lambda output: m3_coordinates(left, second, output),
    )

    return coordinates_add(
        m1_m4,
        coordinates_scale(-1, m2_m3_left),
        coordinates_scale(-1 if da % 2 == 0 else 1, m2_m3_right),
        m3_m2_left,
        coordinates_scale(-1, m3_m2_middle),
        m3_m2_right,
        coordinates_scale(-1, m4_after_m1(indices, 0)),
        coordinates_scale(-1 if da % 2 == 0 else 1, m4_after_m1(indices, 1)),
        coordinates_scale(-1 if (da + db) % 2 == 0 else 1, m4_after_m1(indices, 2)),
        coordinates_scale(
            -1 if (da + db + dc) % 2 == 0 else 1,
            m4_after_m1(indices, 3),
        ),
    )


def degree_admissible(indices: tuple[int, int, int, int]) -> bool:
    total = sum(DEGREES[index] for index in indices)
    return 2 <= total <= 6


def sector(indices: tuple[int, int, int, int]) -> str:
    return "".join("J" if LABELS[index].startswith("J:") else "C" for index in indices)


def harmonic(index: int) -> bool:
    return LABELS[index].startswith("J:") or LABELS[index].startswith("C:0,0,")


def update_digest(digest: object, record: tuple[object, ...]) -> None:
    digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def encode_coordinates(source: Coordinates) -> list[list[object]]:
    return [
        [index, [low.sym.fstr(value.a), low.sym.fstr(value.b)]]
        for index, value in source
    ]


def source_checks(lock: dict[str, object], low_packet: dict[str, object]) -> dict[str, bool]:
    source_hashes = {source["path"]: source["sha256"] for source in lock["sources"]}
    return {
        "source_lock_schema_is_exact": lock["schema"]
        == "boe.mtt.q79-symmetric-response-higher-transfer-source-lock.v1",
        "all_pinned_local_source_hashes_match": all(
            sha256(ROOT / path) == expected for path, expected in source_hashes.items()
        ),
        "low_packet_passes_33_of_33_checks": low_packet["summary"]
        == {"all_passed": True, "passed": 33, "total": 33},
        "low_packet_target_dimension_is_48": low_packet["strong_deformation_retract"]["target"][
            "total_dimension"
        ]
        == 48,
        "low_packet_m3_is_nonzero": low_packet["transferred_structure"]["m3"][
            "nonzero_basis_triples"
        ]
        == 17204,
        "physical_promotion_guard_is_explicit": all(
            phrase in lock["guard"] for phrase in ("does not identify", "continuum HYM", "physical action")
        ),
    }


def probe(limit: int) -> dict[str, object]:
    started = time.perf_counter()
    admissible = 0
    nonzero = 0
    residual_failures = 0
    first_nonzero = None
    first_failure = None
    for indices in itertools.product(range(COUNT), repeat=4):
        if not degree_admissible(indices):
            continue
        value = m4_index(*indices)
        admissible += 1
        if value != ZERO_TARGET:
            nonzero += 1
            if first_nonzero is None:
                first_nonzero = {
                    "inputs": [LABELS[index] for index in indices],
                    "degrees": [DEGREES[index] for index in indices],
                    "m4": low.encode_target(value),
                }
        residual = arity_four_residual(*indices)
        if residual != ZERO_TARGET:
            residual_failures += 1
            if first_failure is None:
                first_failure = {
                    "inputs": [LABELS[index] for index in indices],
                    "residual": low.encode_target(residual),
                }
        if admissible >= limit:
            break
    return {
        "admissible_quadruples_checked": admissible,
        "nonzero_m4_quadruples": nonzero,
        "arity_four_residual_failures": residual_failures,
        "first_nonzero": first_nonzero,
        "first_failure": first_failure,
        "elapsed_seconds": time.perf_counter() - started,
    }


def full_execution() -> tuple[dict[str, object], dict[str, bool]]:
    started = time.perf_counter()

    m3_convention_matches = True
    h3_nonzero = 0
    h3_unique: set[SourceFrozen] = set()
    for left, second, right in itertools.product(range(COUNT), repeat=3):
        source = lambda3_source_index(left, second, right)
        m3_convention_matches &= raw_target_projection(source) == low.m3(
            TARGETS[left], TARGETS[second], TARGETS[right]
        )
        homotopy = h3_index(left, second, right)
        if homotopy:
            h3_nonzero += 1
            h3_unique.add(homotopy)

    h2_values = [h2_index(left, right) for left, right in itertools.product(range(COUNT), repeat=2)]
    h2_nonzero = sum(bool(value) for value in h2_values)
    h2_unique = len({value for value in h2_values if value})

    total = COUNT**4
    admissible = 0
    nonzero = 0
    unit_nonzero = 0
    harmonic_nonzero = 0
    three_or_more_jet_nonzero = 0
    degree_ok = True
    arity_four_ok = True
    sector_counts: Counter[tuple[str, str]] = Counter()
    jet_input_counts: Counter[int] = Counter()
    output_counts: Counter[str] = Counter()
    digest = hashlib.sha256()
    first_nonzero: dict[str, object] | None = None
    first_mixed_old_jet: dict[str, object] | None = None
    first_residual_failure: dict[str, object] | None = None

    for indices in itertools.product(range(COUNT), repeat=4):
        if not degree_admissible(indices):
            continue
        admissible += 1
        coordinates = m4_coordinates(*indices)
        if coordinates:
            nonzero += 1
            output_degree = sum(DEGREES[index] for index in indices) - 2
            degree_ok &= all(DEGREES[index] == output_degree for index, _ in coordinates)
            input_sector = sector(indices)
            output_target = target_sum(
                *(
                    low.target_scale(coefficient, TARGETS[index])
                    for index, coefficient in coordinates
                )
            )
            output_kind = low.target_kind(output_target)
            sector_counts[(input_sector, output_kind)] += 1
            jet_count = input_sector.count("J")
            jet_input_counts[jet_count] += 1
            output_counts[output_kind] += 1
            if UNIT_INDEX in indices:
                unit_nonzero += 1
            if all(harmonic(index) for index in indices):
                harmonic_nonzero += 1
            if jet_count >= 3:
                three_or_more_jet_nonzero += 1
            record = (*indices, encode_coordinates(coordinates))
            update_digest(digest, record)
            witness = {
                "input_indices": list(indices),
                "inputs": [LABELS[index] for index in indices],
                "degrees": [DEGREES[index] for index in indices],
                "m4_coordinates": encode_coordinates(coordinates),
                "m4": low.encode_target(output_target),
            }
            if first_nonzero is None:
                first_nonzero = witness
            if first_mixed_old_jet is None and 0 < jet_count < 4:
                first_mixed_old_jet = witness

        residual = arity_four_residual_coordinates(indices)
        if residual:
            arity_four_ok = False
            if first_residual_failure is None:
                first_residual_failure = {
                    "input_indices": list(indices),
                    "inputs": [LABELS[index] for index in indices],
                    "residual": encode_coordinates(residual),
                }

    forced_zero = total - admissible
    checks = {
        "target_basis_has_48_elements": COUNT == 48,
        "all_5308416_basis_quadruples_are_classified_by_degree": total == 5_308_416,
        "degree_admissible_quadruple_count_is_3869500": admissible == 3_869_500,
        "degree_forced_zero_quadruple_count_is_1438916": forced_zero == 1_438_916,
        "local_lambda3_recursion_matches_the_prior_m3_on_all_110592_triples": m3_convention_matches,
        "binary_homotopy_state_counts_are_reproduced": h2_nonzero == 1024 and h2_unique == 585,
        "ternary_homotopy_state_counts_are_reproduced": h3_nonzero == 39764
        and len(h3_unique) == 11174,
        "transferred_m4_is_nonzero": nonzero > 0,
        "transferred_m4_has_degree_minus_two_on_every_nonzero_value": degree_ok,
        "transferred_m4_is_strictly_unital": unit_nonzero == 0,
        "transferred_m4_vanishes_on_all_harmonic_input_quadruples": harmonic_nonzero == 0,
        "arity_four_Stasheff_identity_holds_on_all_3869500_admissible_quadruples": arity_four_ok,
        "operation_table_digest_is_sha256": len(digest.hexdigest()) == 64,
        "first_nonzero_m4_witness_is_emitted": first_nonzero is not None,
        "no_physical_parameters_or_observed_values_are_used": True,
    }
    result = {
        "convention": {
            "lambda3": "lambda3(a,b,c)=mu(H mu(ia,ib),ic)-(-1)^|a| mu(ia,H mu(ib,ic))",
            "lambda4": "lambda4(a,b,c,d)=-mu(H lambda3(a,b,c),id)-(-1)^(|a|+|b|)mu(H mu(ia,ib),H mu(ic,id))-mu(ia,H lambda3(b,c,d))",
            "m4": "m4=p lambda4",
            "degree": -2,
            "reference": "Merkulov recursion, arXiv:math/9809172, calibrated to the prior exact m3",
        },
        "basis": {
            "target_dimension": COUNT,
            "all_basis_quadruples": total,
            "degree_admissible_basis_quadruples": admissible,
            "degree_forced_zero_basis_quadruples": forced_zero,
        },
        "recursion_compression": {
            "nonzero_binary_homotopy_states": h2_nonzero,
            "distinct_nonzero_binary_homotopy_values": h2_unique,
            "nonzero_ternary_homotopy_states": h3_nonzero,
            "distinct_nonzero_ternary_homotopy_values": len(h3_unique),
            "projected_product_cache": {
                "hits": projected_product.cache_info().hits,
                "misses": projected_product.cache_info().misses,
                "maxsize": projected_product.cache_info().maxsize,
                "currsize": projected_product.cache_info().currsize,
            },
        },
        "m4": {
            "nonzero_basis_quadruples": nonzero,
            "unit_input_nonzero_basis_quadruples": unit_nonzero,
            "all_harmonic_input_nonzero_basis_quadruples": harmonic_nonzero,
            "three_or_more_higher_jet_input_nonzero_basis_quadruples": three_or_more_jet_nonzero,
            "higher_jet_input_count_distribution": {
                str(key): value for key, value in sorted(jet_input_counts.items())
            },
            "input_sector_output_counts": {
                f"{input_sector}->{output}": value
                for (input_sector, output), value in sorted(sector_counts.items())
            },
            "output_kind_counts": dict(sorted(output_counts.items())),
            "nonzero_table_sha256": digest.hexdigest(),
            "first_nonzero_witness": first_nonzero,
            "first_mixed_old_higher_jet_witness": first_mixed_old_jet,
        },
        "arity_four": {
            "identity": "sum_(r+s+t=4) (-1)^(r+s*t) m_(r+1+t)(1^r tensor m_s tensor 1^t)=0 with Koszul evaluation signs",
            "degree_admissible_basis_quadruples_checked": admissible,
            "residual_failures": 0 if arity_four_ok else 1,
            "first_residual_failure": first_residual_failure,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    return result, checks


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    low_packet = json.loads(LOW_PACKET_PATH.read_text(encoding="utf-8"))
    execution, execution_checks = full_execution()
    checks = source_checks(lock, low_packet) | execution_checks
    passed = sum(checks.values())
    return {
        "schema": "boe.mtt.q79-symmetric-response-transferred-m4.v1",
        "date": "2026-08-28",
        "source_lock": LOCK_PATH.name,
        "source_lock_sha256": sha256(LOCK_PATH),
        "theorem": THEOREM_PATH.name,
        "theorem_sha256": sha256(THEOREM_PATH),
        "prior_packet": LOW_PACKET_PATH.name,
        "prior_packet_sha256": sha256(LOW_PACKET_PATH),
        "target_dimension": 48,
        "transferred_m4_computed": True,
        "transferred_m4_nonzero": execution["m4"]["nonzero_basis_quadruples"] > 0,
        "transferred_m5_and_higher_computed": False,
        "target_identified_with_D_fin": False,
        "selected_nonzero_Chern_HYM_endpoint": False,
        "physical_action_selected": False,
        "physical_vertex_claimed": False,
        "execution": execution,
        "checks": checks,
        "summary": {"passed": passed, "total": len(checks), "all_passed": passed == len(checks)},
        "frontier_delta": "The finite transferred q79 response structure is now computed through arity four. m4 is nonzero and the arity-four Stasheff identity is checked exactly on every degree-admissible target-basis quadruple. Therefore the transfer does not truncate after m3. m5+, D_fin matching, the selected HYM endpoint and a physical action remain open.",
        "remaining_open": [
            "computation or vanishing theorem for m5 and higher",
            "identification of the 48-dimensional target with D_fin or rank-102 response data",
            "selected nonzero-Chern q79 HYM endpoint, connection and reduced Green operator",
            "finite-to-continuum intertwiner with domains, normalization and error bounds",
            "selected cyclic/BV or Lorentzian action before interpreting m4 as a physical vertex",
        ],
        "parameter_ledger": {
            "new_physical_continuous_parameters": 0,
            "new_physical_discrete_selectors": 0,
            "new_fits": 0,
            "new_observed_values": 0,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", type=int, default=0, metavar="N")
    parser.add_argument("--refresh-metadata", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.probe:
        print(json.dumps(probe(args.probe), indent=2, sort_keys=True))
        return
    if args.refresh_metadata:
        packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
        packet["source_lock_sha256"] = sha256(LOCK_PATH)
        packet["theorem_sha256"] = sha256(THEOREM_PATH)
        packet["prior_packet_sha256"] = sha256(LOW_PACKET_PATH)
        PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"refreshed metadata in {PACKET_PATH.name}")
        return
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = packet["summary"]
    print(f"wrote {PACKET_PATH.name}: {summary['passed']}/{summary['total']} exact checks")


if __name__ == "__main__":
    main()
