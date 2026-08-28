"""Certify the higher-J cutset and probe the exact transferred m5."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from math import prod
from pathlib import Path

import build_q79_symmetric_response_retraction_transferred_m3 as low
import build_q79_symmetric_response_transferred_m4 as arity4


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "q79_higher_transfer_jet_filtration_source_lock.json"
THEOREM_PATH = ROOT / "HigherJetFiltrationAndTransferredAritySupportTheorem_v1.md"
PACKET_PATH = ROOT / "q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json"

E = low.E
SourceFrozen = low.SourceFrozen
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
COUNT = len(BASIS)
UNIT_INDEX = 0
OLD_COUNT = len(low.old_basis())
J_INDICES = tuple(range(OLD_COUNT, COUNT))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def field_inverse(value: E) -> E:
    norm = value * value.conjugate()
    if norm.b != 0 or norm.a == 0:
        raise ZeroDivisionError("invalid Eisenstein-field pivot")
    return value.conjugate() / norm.a


def vector_add(left: dict[int, E], right: dict[int, E], scale: E = ONE) -> dict[int, E]:
    out = dict(left)
    for mask, value in right.items():
        out[mask] = out.get(mask, ZERO) + scale * value
        if out[mask] == ZERO:
            del out[mask]
    return out


def vector_scale(value: E, source: dict[int, E]) -> dict[int, E]:
    return {mask: value * coefficient for mask, coefficient in source.items() if value * coefficient != ZERO}


def source_mode_vector(source: SourceFrozen, mode: tuple[int, int]) -> dict[int, E]:
    out: dict[int, E] = {}
    for a, b, mask, value in source:
        if (a, b) != mode:
            raise ValueError("source is not supported on the requested single mode")
        out[mask] = out.get(mask, ZERO) + value
    return {mask: value for mask, value in out.items() if value != ZERO}


def vector_source(mode: tuple[int, int], source: dict[int, E]) -> SourceFrozen:
    a, b = mode
    return tuple((a, b, mask, value) for mask, value in sorted(source.items()) if value != ZERO)


def encode_source(source: SourceFrozen) -> list[list[object]]:
    return [
        [a, b, mask, [str(value.a), str(value.b)]]
        for a, b, mask, value in source
    ]


def source_family_digest(sources: tuple[SourceFrozen, ...]) -> str:
    payload = json.dumps([encode_source(source) for source in sources], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ExactSpan:
    """Reduced row-echelon span over Q(omega), keyed by exterior masks."""

    def __init__(self, mode: tuple[int, int]) -> None:
        self.mode = mode
        self.rows: dict[int, dict[int, E]] = {}

    def reduce(self, source: SourceFrozen) -> dict[int, E]:
        vector = source_mode_vector(source, self.mode)
        for pivot in sorted(self.rows):
            coefficient = vector.get(pivot, ZERO)
            if coefficient != ZERO:
                vector = vector_add(vector, self.rows[pivot], -coefficient)
        return vector

    def add(self, source: SourceFrozen) -> bool:
        vector = self.reduce(source)
        if not vector:
            return False
        pivot = min(vector)
        vector = vector_scale(field_inverse(vector[pivot]), vector)
        for old_pivot, row in list(self.rows.items()):
            coefficient = row.get(pivot, ZERO)
            if coefficient != ZERO:
                self.rows[old_pivot] = vector_add(row, vector, -coefficient)
        self.rows[pivot] = vector
        return True

    def basis(self) -> tuple[SourceFrozen, ...]:
        return tuple(vector_source(self.mode, self.rows[pivot]) for pivot in sorted(self.rows))

    def contains(self, source: SourceFrozen) -> bool:
        return not self.reduce(source)


def multiply(left: SourceFrozen, right: SourceFrozen) -> SourceFrozen:
    return arity4.raw_source_product(left, right)


def homotopy_after(left: SourceFrozen, right: SourceFrozen) -> SourceFrozen:
    return low.transfer_homotopy(multiply(left, right))


def j_inclusions() -> tuple[SourceFrozen, ...]:
    return tuple(INCLUSIONS[index] for index in J_INDICES)


def nonzero_old_inclusions(mode: tuple[int, int]) -> tuple[SourceFrozen, ...]:
    a, b = mode
    return tuple(
        INCLUSIONS[index]
        for index, (_, _, target) in enumerate(BASIS[:OLD_COUNT])
        if any((source_a, source_b) == (a, b) for source_a, source_b, _, _ in target[0])
    )


def invariant_subspace_certificate() -> tuple[dict[str, object], dict[str, bool]]:
    jets = j_inclusions()
    modes = tuple((a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0))
    mode_records: list[dict[str, object]] = []
    all_initial_contained = True
    all_closed = True
    all_terminal_zero = True
    all_equal_homotopy_image = True

    for mode in modes:
        span = ExactSpan(mode)
        initial: list[SourceFrozen] = []
        for old in nonzero_old_inclusions(mode):
            for jet in jets:
                initial.extend((homotopy_after(old, jet), homotopy_after(jet, old)))
        initial = [source for source in initial if source]
        for source in initial:
            span.add(source)

        changed = True
        rounds = 0
        generated_nonzero = 0
        while changed:
            changed = False
            rounds += 1
            current = span.basis()
            for source in current:
                for jet in jets:
                    for candidate in (homotopy_after(source, jet), homotopy_after(jet, source)):
                        if candidate:
                            generated_nonzero += 1
                            changed |= span.add(candidate)

        homotopy_image = ExactSpan(mode)
        for mask in range(16):
            homotopy_image.add(
                low.transfer_homotopy(
                    low.freeze_source(low.sym.basis_element(mode[0], mode[1], mask))
                )
            )
        equals_homotopy_image = (
            all(homotopy_image.contains(source) for source in span.basis())
            and all(span.contains(source) for source in homotopy_image.basis())
        )

        initial_contained = all(span.contains(source) for source in initial)
        closure_failures = 0
        terminal_failures = 0
        terminal_witness: dict[str, object] | None = None
        for source in span.basis():
            for jet_index, jet in zip(J_INDICES, jets):
                for side, candidate in (
                    ("right", homotopy_after(source, jet)),
                    ("left", homotopy_after(jet, source)),
                ):
                    if candidate and not span.contains(candidate):
                        closure_failures += 1
                for side, product_value in (
                    ("right", multiply(source, jet)),
                    ("left", multiply(jet, source)),
                ):
                    projected = low.target_projection(product_value)
                    if projected != ZERO_TARGET:
                        terminal_failures += 1
                        if terminal_witness is None:
                            terminal_witness = {
                                "span_basis": encode_source(source),
                                "jet": LABELS[jet_index],
                                "side": side,
                                "projection": low.encode_target(projected),
                            }

        all_initial_contained &= initial_contained
        all_closed &= closure_failures == 0
        all_terminal_zero &= terminal_failures == 0
        all_equal_homotopy_image &= equals_homotopy_image
        degree_dimensions = Counter()
        for source in span.basis():
            degrees = {mask.bit_count() for _, _, mask, _ in source}
            if len(degrees) != 1:
                raise ValueError("invariant-span row is not homogeneous")
            degree_dimensions[next(iter(degrees))] += 1
        mode_records.append(
            {
                "mode": list(mode),
                "initial_nonzero_generator_count": len(initial),
                "closure_rounds": rounds,
                "generated_nonzero_operator_images": generated_nonzero,
                "invariant_span_dimension": len(span.rows),
                "homotopy_image_dimension": len(homotopy_image.rows),
                "invariant_span_equals_homotopy_image": equals_homotopy_image,
                "degree_dimensions": {str(key): degree_dimensions[key] for key in sorted(degree_dimensions)},
                "canonical_span_basis_sha256": source_family_digest(span.basis()),
                "closure_operator_tests": len(span.rows) * len(jets) * 2,
                "closure_failures": closure_failures,
                "terminal_projection_tests": len(span.rows) * len(jets) * 2,
                "terminal_projection_failures": terminal_failures,
                "first_terminal_failure": terminal_witness,
            }
        )

    pure_jet_homotopy_failures = 0
    for left in jets:
        for right in jets:
            pure_jet_homotopy_failures += int(homotopy_after(left, right) != ZERO_SOURCE)

    claims = {
        "field": "Q(omega), omega^2+omega+1=0",
        "operator_family": "H mu(-,j) and H mu(j,-) for every one of the 12 J basis vectors",
        "nonzero_modes": mode_records,
        "pure_J_pair_homotopy_failures": pure_jet_homotopy_failures,
        "tree_argument": {
            "pure_J_subtree_rule": "Every non-root pure-J subtree is killed at its first H edge because J is zero-mode harmonic and H|mode(0,0)=0.",
            "one_old_input_rule": "Any surviving planar tree with exactly one old input is a comb along that input. Its first H edge lies in the certified invariant span; every intermediate J edge preserves the span; the root J multiplication has zero target projection.",
            "conclusion": "For every n>=3, m_n vanishes term by term when at least n-1 inputs lie in J.",
        },
    }
    checks = {
        "all_initial_one_old_one_J_homotopy_images_lie_in_the_certified_spans": all_initial_contained,
        "each_certified_span_equals_the_full_nonzero_mode_image_of_H": all_equal_homotopy_image,
        "certified_spans_are_invariant_under_all_left_and_right_J_homotopy_operators": all_closed,
        "all_terminal_left_and_right_J_products_project_to_zero": all_terminal_zero,
        "H_annihilates_every_pure_J_basis_pair_product": pure_jet_homotopy_failures == 0,
        "general_n_minus_1_J_tree_cutset_is_certified": all_initial_contained
        and all_equal_homotopy_image
        and all_closed
        and all_terminal_zero
        and pure_jet_homotopy_failures == 0,
    }
    return claims, checks


def attribute_counts() -> Counter[tuple[int, bool, bool, bool]]:
    counts: Counter[tuple[int, bool, bool, bool]] = Counter()
    for index, (label, degree, target) in enumerate(BASIS):
        is_jet = label.startswith("J:")
        is_harmonic = is_jet or any(a == 0 and b == 0 for a, b, _, _ in target[0])
        counts[(degree, index == UNIT_INDEX, is_harmonic, is_jet)] += 1
    return counts


def m5_combinatorial_feasibility() -> dict[str, object]:
    categories = tuple(attribute_counts().items())
    total = COUNT**5
    degree_admissible = 0
    after_unit = 0
    after_harmonic = 0
    after_jet_cutset = 0
    jet_cutset_removed = 0
    harmonic_removed = 0

    for chosen in itertools.product(categories, repeat=5):
        attributes = tuple(item[0] for item in chosen)
        multiplicity = prod(item[1] for item in chosen)
        degree_sum = sum(item[0] for item in attributes)
        if not 3 <= degree_sum <= 7:
            continue
        degree_admissible += multiplicity
        if any(item[1] for item in attributes):
            continue
        after_unit += multiplicity
        if all(item[2] for item in attributes):
            harmonic_removed += multiplicity
            continue
        after_harmonic += multiplicity
        if sum(item[3] for item in attributes) >= 4:
            jet_cutset_removed += multiplicity
            continue
        after_jet_cutset += multiplicity

    return {
        "total_basis_quintuples": total,
        "degree_admissible_basis_quintuples": degree_admissible,
        "degree_rule": "|m5|=-3, so 3<=sum(input degrees)<=7",
        "after_strict_unit_cutset": after_unit,
        "all_harmonic_cutset_removed_after_unit": harmonic_removed,
        "after_all_harmonic_cutset": after_harmonic,
        "n_minus_1_J_cutset_removed_after_prior_cutsets": jet_cutset_removed,
        "remaining_after_proved_cheap_cutsets": after_jet_cutset,
        "remaining_fraction_of_raw": [after_jet_cutset, total],
        "planar_binary_tree_count": 14,
        "verdict": "The structural cutsets are exact but do not by themselves make a full m5 table cheap; state compression or orbit decomposition is still required.",
    }


def source_sum(*terms: SourceFrozen) -> SourceFrozen:
    result = ZERO_SOURCE
    for term in terms:
        result = low.source_add(result, term)
    return result


@lru_cache(maxsize=300_000)
def lambda4_source_index(a: int, b: int, c: int, d: int) -> SourceFrozen:
    first = multiply(arity4.h3_index(a, b, c), INCLUSIONS[d])
    balanced = multiply(arity4.h2_index(a, b), arity4.h2_index(c, d))
    final = multiply(INCLUSIONS[a], arity4.h3_index(b, c, d))
    balanced_sign = -1 if (DEGREES[a] + DEGREES[b]) % 2 == 0 else 1
    return source_sum(
        low.source_scale(-1, first),
        low.source_scale(balanced_sign, balanced),
        low.source_scale(-1, final),
    )


@lru_cache(maxsize=300_000)
def h4_index(a: int, b: int, c: int, d: int) -> SourceFrozen:
    return low.transfer_homotopy(lambda4_source_index(a, b, c, d))


def m5_index(a: int, b: int, c: int, d: int, e: int) -> Target:
    """Merkulov's explicit lambda5, projected to the 48-dimensional target."""

    output_degree = DEGREES[a] + DEGREES[b] + DEGREES[c] + DEGREES[d] + DEGREES[e] - 3
    if output_degree < 0 or output_degree > 4:
        return ZERO_TARGET
    first = multiply(h4_index(a, b, c, d), INCLUSIONS[e])
    second = multiply(arity4.h3_index(a, b, c), arity4.h2_index(d, e))
    third = multiply(arity4.h2_index(a, b), arity4.h3_index(c, d, e))
    final = multiply(INCLUSIONS[a], h4_index(b, c, d, e))
    second_sign = -1 if (DEGREES[a] + DEGREES[b] + DEGREES[c]) % 2 else 1
    final_sign = 1 if DEGREES[a] % 2 else -1
    value = source_sum(
        first,
        low.source_scale(second_sign, second),
        low.source_scale(-1, third),
        low.source_scale(final_sign, final),
    )
    return low.target_projection(value)


@lru_cache(maxsize=500_000)
def q_lambda_indices(indices: tuple[int, ...]) -> SourceFrozen:
    """Return H lambda_n, with Merkulov's formal H lambda_1=-i convention."""

    if len(indices) == 1:
        return low.source_scale(-1, INCLUSIONS[indices[0]])
    return low.transfer_homotopy(lambda_indices(indices))


@lru_cache(maxsize=500_000)
def lambda_indices(indices: tuple[int, ...]) -> SourceFrozen:
    """Generic Merkulov recursion, independently calibrated through arity five."""

    n = len(indices)
    if n < 2:
        raise ValueError("lambda_n starts at arity two")
    terms: list[SourceFrozen] = []
    for left_arity in range(1, n):
        right_arity = n - left_arity
        prefix_degree = sum(DEGREES[index] for index in indices[:left_arity])
        exponent = left_arity + (right_arity - 1) * prefix_degree
        recursion_sign = -1 if exponent % 2 == 0 else 1
        terms.append(
            low.source_scale(
                recursion_sign,
                multiply(
                    q_lambda_indices(indices[:left_arity]),
                    q_lambda_indices(indices[left_arity:]),
                ),
            )
        )
    return source_sum(*terms)


def generic_mn(indices: tuple[int, ...]) -> Target:
    output_degree = sum(DEGREES[index] for index in indices) + 2 - len(indices)
    if output_degree < 0 or output_degree > 4:
        return ZERO_TARGET
    return low.target_projection(lambda_indices(indices))


def repeated_family_certificate() -> tuple[dict[str, object], dict[str, bool]]:
    x = LABELS.index("C:0,0,1")
    y = LABELS.index("C:1,0,1")
    z = LABELS.index("C:1,0,0")
    records: list[dict[str, object]] = []
    all_nonzero = True
    all_degree_correct = True
    for arity in range(3, 11):
        indices = (x,) * (arity - 2) + (y, z)
        value = generic_mn(indices)
        output_degree = low.target_degree(value)
        expected_degree = sum(DEGREES[index] for index in indices) + 2 - arity
        all_nonzero &= value != ZERO_TARGET
        all_degree_correct &= output_degree == expected_degree
        records.append(
            {
                "arity": arity,
                "inputs": [LABELS[index] for index in indices],
                "output": encode_target(value),
                "expected_output_degree": expected_degree,
            }
        )

    def a_state(k: int) -> SourceFrozen:
        return q_lambda_indices((x,) * k + (y, z))

    def b_state(k: int) -> SourceFrozen:
        return q_lambda_indices((x,) * k + (y,))

    one_twelfth = Fraction(1, 12)
    state_scaling = (
        a_state(3) == low.source_scale(one_twelfth, a_state(1))
        and b_state(3) == low.source_scale(one_twelfth, b_state(1))
        and a_state(4) == low.source_scale(one_twelfth, a_state(2))
        and b_state(4) == low.source_scale(one_twelfth, b_state(2))
    )
    expected_m3: Target = (
        low.freeze_source({(2, 0, 1): E(Fraction(1, 2), Fraction(1, 4))}),
        low.ZERO_IDEAL,
    )
    expected_m4: Target = (
        low.freeze_source({(2, 0, 1): E(Fraction(0), Fraction(-1, 8))}),
        low.ZERO_IDEAL,
    )
    generic_m3 = generic_mn((x, y, z))
    generic_m4 = generic_mn((x, x, y, z))
    explicit_m5 = m5_index(x, x, x, y, z)
    generic_m5 = generic_mn((x, x, x, y, z))
    generic_m6 = generic_mn((x, x, x, x, y, z))
    output_scaling_bases = (
        generic_m5 == low.target_scale(one_twelfth, generic_m3)
        and generic_m6 == low.target_scale(one_twelfth, generic_m4)
    )
    claims = {
        "family": "m_n((C:0,0,1)^(n-2), C:1,0,1, C:1,0,0)",
        "state_definitions": {
            "A_k": "H lambda_(k+2)(x^k,y,z)",
            "B_k": "H lambda_(k+1)(x^k,y)",
            "T": "H mu(i x,-)",
            "U": "H mu(-,i z)",
        },
        "state_recursion": [
            "B_k=(-1)^k T B_(k-1)",
            "A_k=(-1)^(k+1)(T A_(k-1)+U B_k)",
            "M_k=m_(k+2)(x^k,y,z)=(-1)^(k+1)p(mu(i x,A_(k-1))+mu(B_k,i z))",
        ],
        "period_two_state_certificate": [
            "(A_3,B_3)=(A_1,B_1)/12",
            "(A_4,B_4)=(A_2,B_2)/12",
            "the state update depends only on parity of k, hence (A_(k+2),B_(k+2))=(A_k,B_k)/12 for every k>=1",
            "M_3=M_1/12 and M_4=M_2/12 initialize the odd and even output subsequences",
        ],
        "closed_form": {
            "odd_arity": "m_(2r+3)(x^(2r+1),y,z)=((2+omega)/(4*12^r)) C:2,0,1 for r>=0",
            "even_arity": "m_(2r+4)(x^(2r+2),y,z)=(-omega/(8*12^r)) C:2,0,1 for r>=0",
            "conclusion": "m_n is nonzero for every n>=3",
        },
        "exact_records": records,
        "scope": "all-arity theorem for one selected ordered family; it does not compute complete operation tables or Stasheff residual tables at arity five and above",
    }
    checks = {
        "generic_Merkulov_recursion_matches_the_complete_m3_implementation": generic_m3
        == low.m3(TARGETS[x], TARGETS[y], TARGETS[z]),
        "generic_Merkulov_recursion_matches_the_complete_m4_implementation": generic_m4
        == arity4.m4_index(x, x, y, z),
        "generic_Merkulov_recursion_matches_the_explicit_m5_implementation": generic_m5
        == explicit_m5,
        "two_parity_base_states_certify_the_one_over_twelve_recurrence": state_scaling,
        "closed_form_base_values_m3_and_m4_are_exact": generic_m3 == expected_m3
        and generic_m4 == expected_m4,
        "odd_and_even_output_recurrence_bases_scale_by_one_over_twelve": output_scaling_bases,
        "selected_family_is_proved_nonzero_at_every_arity_n_ge_3": state_scaling
        and generic_m3 == expected_m3
        and generic_m4 == expected_m4
        and output_scaling_bases,
        "selected_repeated_family_is_nonzero_through_arity_ten": all_nonzero,
        "selected_repeated_family_has_the_expected_degree_through_arity_ten": all_degree_correct,
    }
    return claims, checks


def encode_target(source: Target) -> dict[str, object]:
    return low.encode_target(source)


def selected_m5_probe() -> tuple[dict[str, object], dict[str, bool]]:
    preferred_labels = (
        "C:0,0,1",
        "C:1,0,1",
        "C:1,0,0",
        "C:2,0,1",
        "C:2,0,0",
        "C:0,1,2",
        "C:0,1,0",
        "J:4",
        "J:8",
        "J:5",
    )
    preferred = tuple(LABELS.index(label) for label in preferred_labels)
    witness: dict[str, object] | None = None
    checked = 0
    cutset_failures = 0

    for indices in itertools.product(preferred, repeat=5):
        if UNIT_INDEX in indices:
            continue
        degree_sum = sum(DEGREES[index] for index in indices)
        if not 3 <= degree_sum <= 7:
            continue
        value = m5_index(*indices)
        checked += 1
        jet_count = sum(index in J_INDICES for index in indices)
        if jet_count >= 4 and value != ZERO_TARGET:
            cutset_failures += 1
        if witness is None and value != ZERO_TARGET:
            witness = {
                "inputs": [LABELS[index] for index in indices],
                "input_degrees": [DEGREES[index] for index in indices],
                "output": encode_target(value),
                "higher_jet_input_count": jet_count,
            }

    claims = {
        "probe_basis_labels": list(preferred_labels),
        "degree_admissible_quintuples_checked": checked,
        "first_nonzero_m5_witness": witness,
        "cutset_failures_in_probe": cutset_failures,
        "scope": "deterministic selected exact probe, not the full 48^5 operation table or SI(5) verification",
    }
    checks = {
        "selected_exact_m5_probe_executed": checked > 0,
        "selected_probe_respects_the_general_higher_J_cutset": cutset_failures == 0,
        "transferred_m5_is_proved_nonzero_by_an_exact_witness": witness is not None,
    }
    return claims, checks


def source_checks(lock: dict[str, object]) -> dict[str, bool]:
    return {
        "source_lock_schema_is_exact": lock["schema"]
        == "boe.mtt.q79-higher-transfer-jet-filtration-source-lock.v1",
        "all_source_lock_hashes_match": all(
            source["sha256"] == sha256(ROOT / source["path"])
            for source in lock["sources"]
        ),
        "source_lock_preserves_the_physical_nonpromotion_boundary": "does not" in lock["guard"].lower(),
    }


def build_packet() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    invariant, invariant_checks = invariant_subspace_certificate()
    probe, probe_checks = selected_m5_probe()
    repeated_family, repeated_checks = repeated_family_certificate()
    feasibility = m5_combinatorial_feasibility()
    checks = source_checks(lock) | invariant_checks | probe_checks | repeated_checks
    return {
        "schema": "boe.mtt.q79-higher-transfer-jet-filtration-and-m5-feasibility.v1",
        "date": "2026-08-28",
        "source_lock": {"path": LOCK_PATH.name, "sha256": sha256(LOCK_PATH)},
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "higher_jet_invariant_subspace_certificate": invariant,
        "m5_combinatorial_feasibility": feasibility,
        "m5_selected_exact_probe": probe,
        "selected_higher_arity_repeated_family_probe": repeated_family,
        "general_n_minus_1_J_cutset_proved": invariant_checks[
            "general_n_minus_1_J_tree_cutset_is_certified"
        ],
        "transferred_m5_nonzero": probe_checks[
            "transferred_m5_is_proved_nonzero_by_an_exact_witness"
        ],
        "transferred_mn_nonzero_for_every_n_ge_3_on_selected_family": repeated_checks[
            "selected_family_is_proved_nonzero_at_every_arity_n_ge_3"
        ],
        "full_m5_table_computed": False,
        "arity_five_Stasheff_identity_fully_verified": False,
        "physical_D_fin_or_HYM_identification": False,
        "frontier_delta": "A finite invariant-subspace certificate proves for every n>=3 that m_n vanishes whenever at least n-1 inputs lie in the higher-jet ideal J. A separate exact two-state parity recurrence gives closed nonzero values for m_n(x^(n-2),y,z) at every n>=3, so the transferred hierarchy never truncates at finite arity. Complete operation tables and Stasheff residual tables from arity five onward remain open and require state compression or orbit decomposition.",
        "open_obligations": [
            "full m5 operation digest and arity-five Stasheff verification",
            "state-compressed or covariance-orbit execution of the remaining m5 candidates",
            "complete operation and Stasheff tables at arity six and above despite proved selected-family nonvanishing",
            "identification with D_fin, a continuum HYM vertex or a selected physical action",
            "continuum endpoint, domains, normalization and certified finite-to-continuum error",
        ],
    }


def main() -> None:
    packet = build_packet()
    PACKET_PATH.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet, indent=2))


if __name__ == "__main__":
    main()
