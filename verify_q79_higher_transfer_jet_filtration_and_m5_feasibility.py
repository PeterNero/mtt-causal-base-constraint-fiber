"""Independent verifier for the all-arity higher-J cutset and m5 witness."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from functools import lru_cache
from math import prod
from pathlib import Path

import build_q79_symmetric_response_retraction_transferred_m3 as low


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json"
LOCK_PATH = ROOT / "q79_higher_transfer_jet_filtration_source_lock.json"

E = low.E
Source = low.SourceFrozen
Target = low.Target
ZERO = low.sym.wk.ZERO
ONE = low.sym.wk.ONE
ZERO_SOURCE = low.ZERO_SOURCE
ZERO_TARGET = low.ZERO_TARGET

BASIS = low.old_basis() + low.ideal_basis()
LABELS = tuple(label for label, _, _ in BASIS)
DEGREES = tuple(degree for _, degree, _ in BASIS)
TARGETS = tuple(target for _, _, target in BASIS)
INCLUSIONS = tuple(low.target_inclusion(target) for target in TARGETS)
OLD_COUNT = len(low.old_basis())
J_INDICES = tuple(range(OLD_COUNT, len(BASIS)))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inverse(value: E) -> E:
    norm = value * value.conjugate()
    if norm.b != 0 or norm.a == 0:
        raise ZeroDivisionError("invalid Q(omega) pivot")
    return value.conjugate() / norm.a


def add_vectors(left: dict[int, E], right: dict[int, E], scale: E = ONE) -> dict[int, E]:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, ZERO) + scale * value
        if result[key] == ZERO:
            del result[key]
    return result


def scale_vector(value: E, vector: dict[int, E]) -> dict[int, E]:
    return {key: value * item for key, item in vector.items() if value * item != ZERO}


def thaw_mode(source: Source, mode: tuple[int, int]) -> dict[int, E]:
    result: dict[int, E] = {}
    for a, b, mask, value in source:
        if (a, b) != mode:
            raise ValueError("mixed-mode vector")
        result[mask] = result.get(mask, ZERO) + value
    return {mask: value for mask, value in result.items() if value != ZERO}


def freeze_mode(mode: tuple[int, int], vector: dict[int, E]) -> Source:
    return tuple((mode[0], mode[1], mask, value) for mask, value in sorted(vector.items()) if value != ZERO)


def encode_source(source: Source) -> list[list[object]]:
    return [[a, b, mask, [str(value.a), str(value.b)]] for a, b, mask, value in source]


def family_digest(sources: tuple[Source, ...]) -> str:
    value = json.dumps([encode_source(source) for source in sources], separators=(",", ":"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Span:
    def __init__(self, mode: tuple[int, int]) -> None:
        self.mode = mode
        self.rows: dict[int, dict[int, E]] = {}

    def remainder(self, source: Source) -> dict[int, E]:
        vector = thaw_mode(source, self.mode)
        for pivot in sorted(self.rows):
            coefficient = vector.get(pivot, ZERO)
            if coefficient != ZERO:
                vector = add_vectors(vector, self.rows[pivot], -coefficient)
        return vector

    def insert(self, source: Source) -> bool:
        vector = self.remainder(source)
        if not vector:
            return False
        pivot = min(vector)
        vector = scale_vector(inverse(vector[pivot]), vector)
        for old_pivot, old_row in list(self.rows.items()):
            coefficient = old_row.get(pivot, ZERO)
            if coefficient != ZERO:
                self.rows[old_pivot] = add_vectors(old_row, vector, -coefficient)
        self.rows[pivot] = vector
        return True

    def includes(self, source: Source) -> bool:
        return not self.remainder(source)

    def basis(self) -> tuple[Source, ...]:
        return tuple(freeze_mode(self.mode, self.rows[pivot]) for pivot in sorted(self.rows))


def multiply(left: Source, right: Source) -> Source:
    if not left or not right:
        return ZERO_SOURCE
    return low.freeze_source(
        low.sym.product(low.thaw_source(left), low.thaw_source(right), low.sym.DIRECTION_EXPONENTS)
    )


def source_sum(*terms: Source) -> Source:
    result = ZERO_SOURCE
    for term in terms:
        result = low.source_add(result, term)
    return result


def h_product(left: Source, right: Source) -> Source:
    return low.transfer_homotopy(multiply(left, right))


def independent_invariant_certificate(packet: dict[str, object]) -> dict[str, bool]:
    jets = tuple(INCLUSIONS[index] for index in J_INDICES)
    modes = tuple((a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0))
    records = packet["higher_jet_invariant_subspace_certificate"]["nonzero_modes"]
    record_by_mode = {tuple(record["mode"]): record for record in records}
    dimensions_match = True
    digests_match = True
    equals_h_image = True
    invariant = True
    terminal_zero = True

    for mode in modes:
        old = tuple(
            INCLUSIONS[index]
            for index, (_, _, target) in enumerate(BASIS[:OLD_COUNT])
            if any((a, b) == mode for a, b, _, _ in target[0])
        )
        span = Span(mode)
        for old_value in old:
            for jet in jets:
                span.insert(h_product(old_value, jet))
                span.insert(h_product(jet, old_value))

        changed = True
        while changed:
            changed = False
            for source in span.basis():
                for jet in jets:
                    changed |= span.insert(h_product(source, jet))
                    changed |= span.insert(h_product(jet, source))

        h_image = Span(mode)
        for mask in range(16):
            basis_value = low.freeze_source(low.sym.basis_element(mode[0], mode[1], mask))
            h_image.insert(low.transfer_homotopy(basis_value))

        equals_h_image &= all(h_image.includes(value) for value in span.basis())
        equals_h_image &= all(span.includes(value) for value in h_image.basis())
        for source in span.basis():
            for jet in jets:
                invariant &= span.includes(h_product(source, jet))
                invariant &= span.includes(h_product(jet, source))
                terminal_zero &= low.target_projection(multiply(source, jet)) == ZERO_TARGET
                terminal_zero &= low.target_projection(multiply(jet, source)) == ZERO_TARGET

        record = record_by_mode[mode]
        degree_dimensions = Counter(next(iter({mask.bit_count() for _, _, mask, _ in row})) for row in span.basis())
        dimensions_match &= len(span.rows) == record["invariant_span_dimension"] == 6
        dimensions_match &= {str(key): degree_dimensions[key] for key in sorted(degree_dimensions)} == record[
            "degree_dimensions"
        ]
        digests_match &= family_digest(span.basis()) == record["canonical_span_basis_sha256"]

    pure_jet_zero = all(h_product(left, right) == ZERO_SOURCE for left in jets for right in jets)
    return {
        "independent_eight_mode_span_dimensions_match": dimensions_match,
        "independent_canonical_span_digests_match": digests_match,
        "independent_reachable_spans_equal_im_H": equals_h_image,
        "independent_left_right_J_invariance_holds": invariant,
        "independent_terminal_J_products_project_to_zero": terminal_zero,
        "independent_pure_J_products_are_killed_by_H": pure_jet_zero,
    }


@lru_cache(maxsize=None)
def h2(a: int, b: int) -> Source:
    return low.transfer_homotopy(multiply(INCLUSIONS[a], INCLUSIONS[b]))


@lru_cache(maxsize=None)
def lambda3(a: int, b: int, c: int) -> Source:
    first = multiply(h2(a, b), INCLUSIONS[c])
    second = multiply(INCLUSIONS[a], h2(b, c))
    sign = -1 if DEGREES[a] % 2 == 0 else 1
    return source_sum(first, low.source_scale(sign, second))


@lru_cache(maxsize=None)
def h3(a: int, b: int, c: int) -> Source:
    return low.transfer_homotopy(lambda3(a, b, c))


@lru_cache(maxsize=None)
def lambda4(a: int, b: int, c: int, d: int) -> Source:
    first = multiply(h3(a, b, c), INCLUSIONS[d])
    middle = multiply(h2(a, b), h2(c, d))
    final = multiply(INCLUSIONS[a], h3(b, c, d))
    middle_sign = -1 if (DEGREES[a] + DEGREES[b]) % 2 == 0 else 1
    return source_sum(
        low.source_scale(-1, first),
        low.source_scale(middle_sign, middle),
        low.source_scale(-1, final),
    )


@lru_cache(maxsize=None)
def h4(a: int, b: int, c: int, d: int) -> Source:
    return low.transfer_homotopy(lambda4(a, b, c, d))


def independent_m5(indices: tuple[int, int, int, int, int]) -> Target:
    a, b, c, d, e = indices
    first = multiply(h4(a, b, c, d), INCLUSIONS[e])
    second = multiply(h3(a, b, c), h2(d, e))
    third = multiply(h2(a, b), h3(c, d, e))
    final = multiply(INCLUSIONS[a], h4(b, c, d, e))
    second_sign = -1 if (DEGREES[a] + DEGREES[b] + DEGREES[c]) % 2 else 1
    final_sign = 1 if DEGREES[a] % 2 else -1
    return low.target_projection(
        source_sum(
            first,
            low.source_scale(second_sign, second),
            low.source_scale(-1, third),
            low.source_scale(final_sign, final),
        )
    )


@lru_cache(maxsize=None)
def independent_q_lambda(indices: tuple[int, ...]) -> Source:
    if len(indices) == 1:
        return low.source_scale(-1, INCLUSIONS[indices[0]])
    return low.transfer_homotopy(independent_lambda(indices))


@lru_cache(maxsize=None)
def independent_lambda(indices: tuple[int, ...]) -> Source:
    n = len(indices)
    if n < 2:
        raise ValueError("lambda_n starts at arity two")
    terms: list[Source] = []
    for left_arity in range(1, n):
        right_arity = n - left_arity
        prefix_degree = sum(DEGREES[index] for index in indices[:left_arity])
        exponent = left_arity + (right_arity - 1) * prefix_degree
        coefficient = -1 if exponent % 2 == 0 else 1
        terms.append(
            low.source_scale(
                coefficient,
                multiply(
                    independent_q_lambda(indices[:left_arity]),
                    independent_q_lambda(indices[left_arity:]),
                ),
            )
        )
    return source_sum(*terms)


def independent_generic_mn(indices: tuple[int, ...]) -> Target:
    return low.target_projection(independent_lambda(indices))


def independent_all_arity_family(packet: dict[str, object]) -> dict[str, bool]:
    x = LABELS.index("C:0,0,1")
    y = LABELS.index("C:1,0,1")
    z = LABELS.index("C:1,0,0")
    scale = low.Fraction(1, 12)

    def a_state(k: int) -> Source:
        return independent_q_lambda((x,) * k + (y, z))

    def b_state(k: int) -> Source:
        return independent_q_lambda((x,) * k + (y,))

    parity_bases = (
        a_state(3) == low.source_scale(scale, a_state(1))
        and b_state(3) == low.source_scale(scale, b_state(1))
        and a_state(4) == low.source_scale(scale, a_state(2))
        and b_state(4) == low.source_scale(scale, b_state(2))
    )
    expected_m3: Target = (
        low.freeze_source({(2, 0, 1): E(low.Fraction(1, 2), low.Fraction(1, 4))}),
        low.ZERO_IDEAL,
    )
    expected_m4: Target = (
        low.freeze_source({(2, 0, 1): E(low.Fraction(0), low.Fraction(-1, 8))}),
        low.ZERO_IDEAL,
    )
    m3_value = independent_generic_mn((x, y, z))
    m4_value = independent_generic_mn((x, x, y, z))
    m5_value = independent_generic_mn((x, x, x, y, z))
    m6_value = independent_generic_mn((x, x, x, x, y, z))
    explicit_values_match = (
        m3_value == low.m3(TARGETS[x], TARGETS[y], TARGETS[z])
        and m4_value == low.target_projection(lambda4(x, x, y, z))
        and m5_value == independent_m5((x, x, x, y, z))
    )

    records = packet["selected_higher_arity_repeated_family_probe"]["exact_records"]
    records_match = True
    closed_forms_match = True
    for record in records:
        arity = record["arity"]
        indices = (x,) * (arity - 2) + (y, z)
        value = independent_generic_mn(indices)
        records_match &= low.encode_target(value) == record["output"]
        r = (arity - 3) // 2
        if arity % 2:
            coefficient = E(low.Fraction(2, 4 * 12**r), low.Fraction(1, 4 * 12**r))
        else:
            coefficient = E(low.Fraction(0), low.Fraction(-1, 8 * 12**r))
        expected: Target = (low.freeze_source({(2, 0, 1): coefficient}), low.ZERO_IDEAL)
        closed_forms_match &= value == expected

    return {
        "independent_generic_recursion_matches_explicit_arities_three_through_five": explicit_values_match,
        "independent_two_parity_state_bases_scale_by_one_over_twelve": parity_bases,
        "independent_closed_form_base_values_are_exact": m3_value == expected_m3
        and m4_value == expected_m4,
        "independent_odd_even_output_recurrence_bases_scale_by_one_over_twelve": m5_value
        == low.target_scale(scale, m3_value)
        and m6_value == low.target_scale(scale, m4_value),
        "independent_selected_records_through_arity_ten_match": records_match,
        "independent_odd_even_closed_forms_match_through_arity_ten": closed_forms_match,
    }


def independent_m5_witness(packet: dict[str, object]) -> dict[str, bool]:
    witness = packet["m5_selected_exact_probe"]["first_nonzero_m5_witness"]
    indices = tuple(LABELS.index(label) for label in witness["inputs"])
    value = independent_m5(indices)
    expected = (
        low.freeze_source(
            {
                (2, 0, 1): E(
                    low.Fraction(1, 24),
                    low.Fraction(1, 48),
                )
            }
        ),
        low.ZERO_IDEAL,
    )
    return {
        "independent_m5_witness_equals_declared_exact_value": value == expected,
        "independent_m5_witness_is_nonzero": value != ZERO_TARGET,
        "independent_m5_witness_has_degree_minus_three": low.target_degree(value)
        == sum(DEGREES[index] for index in indices) - 3,
    }


def independent_combinatorics(packet: dict[str, object]) -> dict[str, bool]:
    categories: Counter[tuple[int, bool, bool, bool]] = Counter()
    for index, (label, degree, target) in enumerate(BASIS):
        jet = label.startswith("J:")
        harmonic = jet or any(a == 0 and b == 0 for a, b, _, _ in target[0])
        categories[(degree, index == 0, harmonic, jet)] += 1

    totals = [0, 0, 0, 0]
    for selected in itertools.product(tuple(categories.items()), repeat=5):
        attrs = tuple(item[0] for item in selected)
        multiplicity = prod(item[1] for item in selected)
        if not 3 <= sum(item[0] for item in attrs) <= 7:
            continue
        totals[0] += multiplicity
        if any(item[1] for item in attrs):
            continue
        totals[1] += multiplicity
        if all(item[2] for item in attrs):
            continue
        totals[2] += multiplicity
        if sum(item[3] for item in attrs) >= 4:
            continue
        totals[3] += multiplicity

    declared = packet["m5_combinatorial_feasibility"]
    return {
        "independent_raw_m5_count_matches": declared["total_basis_quintuples"] == len(BASIS) ** 5,
        "independent_degree_and_support_counts_match": totals
        == [
            declared["degree_admissible_basis_quintuples"],
            declared["after_strict_unit_cutset"],
            declared["after_all_harmonic_cutset"],
            declared["remaining_after_proved_cheap_cutsets"],
        ],
    }


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    checks = {
        "packet_schema_is_exact": packet["schema"]
        == "boe.mtt.q79-higher-transfer-jet-filtration-and-m5-feasibility.v1",
        "packet_source_lock_hash_matches": packet["source_lock"]["sha256"] == sha256(LOCK_PATH),
        "all_locked_source_hashes_match": all(
            sha256(ROOT / source["path"]) == source["sha256"] for source in lock["sources"]
        ),
        "builder_checks_are_all_true": packet["all_checks_pass"] is True
        and all(packet["checks"].values()),
    }
    checks |= independent_invariant_certificate(packet)
    checks |= independent_m5_witness(packet)
    checks |= independent_all_arity_family(packet)
    checks |= independent_combinatorics(packet)
    checks["physical_nonpromotion_boundary_is_preserved"] = (
        packet["full_m5_table_computed"] is False
        and packet["arity_five_Stasheff_identity_fully_verified"] is False
        and packet["physical_D_fin_or_HYM_identification"] is False
    )
    failed = [name for name, value in checks.items() if not value]
    print(json.dumps({"checks": checks, "passed": len(checks) - len(failed), "total": len(checks)}, indent=2))
    if failed:
        raise SystemExit("failed checks: " + ", ".join(failed))


if __name__ == "__main__":
    main()
