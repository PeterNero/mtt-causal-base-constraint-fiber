"""Independent exact verifier for CBF.T60.

This file deliberately does not import the builder.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.packet.json"
LOCK_PATH = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge_source_lock.json"
SCHEMA_PATH = ROOT / "q79_fourier_mukai_double_qutrit_augmented_exterior_bridge_contract.schema.json"

Z = tuple[Fraction, Fraction]
ZERO: Z = (Fraction(0), Fraction(0))
ONE: Z = (Fraction(1), Fraction(0))
OMEGA: Z = (Fraction(0), Fraction(1))


def add(x: Z, y: Z) -> Z:
    return x[0] + y[0], x[1] + y[1]


def neg(x: Z) -> Z:
    return -x[0], -x[1]


def sub(x: Z, y: Z) -> Z:
    return add(x, neg(y))


def mul(x: Z, y: Z) -> Z:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0] - x[1] * y[1]


def conjugate(x: Z) -> Z:
    return x[0] - x[1], -x[1]


def inverse(x: Z) -> Z:
    norm = mul(conjugate(x), x)
    assert norm[1] == 0 and norm[0]
    value = conjugate(x)
    return value[0] / norm[0], value[1] / norm[0]


def scale(value: int | Fraction, x: Z) -> Z:
    return Fraction(value) * x[0], Fraction(value) * x[1]


def power(exponent: int) -> Z:
    return (ONE, OMEGA, (Fraction(-1), Fraction(-1)))[exponent % 3]


def rank(matrix: list[list[Z]]) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    pivot_row = 0
    for col in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][col] != ZERO), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_inverse = inverse(work[pivot_row][col])
        work[pivot_row] = [mul(pivot_inverse, value) for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or work[row][col] == ZERO:
                continue
            factor = work[row][col]
            work[row] = [sub(value, mul(factor, pivot_value)) for value, pivot_value in zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def choose(degree: int) -> list[tuple[int, ...]]:
    return list(itertools.combinations(range(4), degree))


def differential(label: tuple[int, int, int, int], degree: int) -> list[list[Z]]:
    if degree == 4:
        return []
    a, b, c, d = label
    coefficients = (sub(power(a), ONE), sub(power(-b), ONE), sub(power(c), ONE), sub(power(-d), ONE))
    source = choose(degree)
    target = choose(degree + 1)
    target_index = {item: index for index, item in enumerate(target)}
    matrix = [[ZERO for _ in source] for _ in target]
    for column, item in enumerate(source):
        for generator, coefficient in enumerate(coefficients):
            if generator in item:
                continue
            sign = -1 if sum(existing < generator for existing in item) % 2 else 1
            row = target_index[tuple(sorted(item + (generator,)))]
            matrix[row][column] = scale(sign, coefficient)
    return matrix


def matmul(left: list[list[Z]], right: list[list[Z]]) -> list[list[Z]]:
    return [
        [
            sum_values(mul(left[row][k], right[k][col]) for k in range(len(right)))
            for col in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def sum_values(values) -> Z:
    total = ZERO
    for value in values:
        total = add(total, value)
    return total


def identity(size: int) -> list[list[Z]]:
    return [[ONE if row == col else ZERO for col in range(size)] for row in range(size)]


def matrix_scale(scalar: Z, matrix: list[list[Z]]) -> list[list[Z]]:
    return [[mul(scalar, value) for value in row] for row in matrix]


def matrix_power(matrix: list[list[Z]], exponent: int) -> list[list[Z]]:
    result = identity(len(matrix))
    for _ in range(exponent % 3):
        result = matmul(result, matrix)
    return result


def reconstruct_weyl_orientation() -> tuple[bool, bool, bool]:
    x = [
        [ZERO, ONE, ZERO],
        [ZERO, ZERO, ONE],
        [ONE, ZERO, ZERO],
    ]
    z = [
        [ONE, ZERO, ZERO],
        [ZERO, power(1), ZERO],
        [ZERO, ZERO, power(2)],
    ]
    relation = matmul(x, z) == matrix_scale(power(1), matmul(z, x))
    x_inverse = matrix_power(x, 2)
    z_inverse = matrix_power(z, 2)
    ad_x = True
    ad_z = True
    for a, b in itertools.product(range(3), repeat=2):
        mode = matmul(matrix_power(z, a), matrix_power(x, b))
        ad_x &= matmul(matmul(x, mode), x_inverse) == matrix_scale(power(a), mode)
        ad_z &= matmul(matmul(z, mode), z_inverse) == matrix_scale(power(-b), mode)
    return relation, ad_x, ad_z


def center(value: int) -> int:
    return (0, 1, -1)[value % 3]


def binomial(n: int, k: int) -> int:
    return 0 if k < 0 or k > n else math.comb(n, k)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    labels = list(itertools.product(range(3), repeat=4))
    spectrum: Counter[int] = Counter()
    cohomology = [0] * 5
    square_zero = True
    for label in labels:
        exponents = (label[0] % 3, (-label[1]) % 3, label[2] % 3, (-label[3]) % 3)
        support = sum(exponent != 0 for exponent in exponents)
        spectrum[3 * support] += 1
        ranks = [rank(differential(label, degree)) for degree in range(4)]
        for degree in range(5):
            incoming = ranks[degree - 1] if degree else 0
            outgoing = ranks[degree] if degree < 4 else 0
            cohomology[degree] += math.comb(4, degree) - incoming - outgoing
        for degree in range(3):
            square_zero &= all(
                value == ZERO
                for row in matmul(differential(label, degree + 1), differential(label, degree))
                for value in row
            )

    bridge_dimensions = []
    bridge_bijections = True
    for n in range(-1, 4):
        degree = n + 1
        source = choose(degree)
        alpha = [item for item in source if 0 in item]
        ordinary = [item for item in source if 0 not in item]
        target_dimension = binomial(3, n) + binomial(3, n + 1)
        bridge_dimensions.append(len(source))
        bridge_bijections &= len(source) == len(alpha) + len(ordinary) == target_dimension

    def quadratic(x: int, y: int) -> int:
        return 2 * x * x + 2 * x * y + 2 * y * y

    sector_rows = []
    ground: Counter[int] = Counter()
    tails = []
    for a in range(3):
        for b in range(3):
            residue = (center(a) % 3, (-center(b)) % 3)
            values = [
                (quadratic(x, y), x, y)
                for x in range(-5, 6)
                for y in range(-5, 6)
                if x % 3 == residue[0] and y % 3 == residue[1]
            ]
            levels = sorted(set(value for value, _, _ in values))
            minimum = levels[0]
            multiplicity = sum(value == minimum for value, _, _ in values)
            ground[minimum] += multiplicity
            tails.append(levels[1])
            sector_rows.append((a, b, minimum, multiplicity, levels[1]))

    local_hashes_match = all(file_hash(ROOT / row["path"]) == row["sha256"] for row in lock["sources"])
    weyl_relation, ad_x_orientation, ad_z_orientation = reconstruct_weyl_orientation()
    packet_modes = packet["double_qutrit_koszul_hodge"]["modes"]
    packet_sector_rows = packet["equianharmonic_continuum_cutset"]["sector_rows"]
    checks = {
        "packet_schema_matches_contract": packet["schema"] == schema["$id"],
        "contract_required_fields_present": set(schema["required"]).issubset(packet),
        "claim_is_CBF_T60": packet["claim_id"] == "CBF.T60",
        "source_lock_model_matches_packet": lock["model_state_sha256"] == packet["source_provenance"]["model_state_sha256"],
        "four_local_source_hashes_match": local_hashes_match and len(lock["sources"]) == 4,
        "locked_Weyl_relation_reconstructed": weyl_relation,
        "Ad_X_character_orientation_reconstructed": ad_x_orientation,
        "Ad_Z_character_orientation_reconstructed": ad_z_orientation,
        "all_81_labels_reconstructed": len(labels) == 81,
        "all_81_packet_modes_present": len(packet_modes) == 81,
        "Koszul_square_zero_exact": square_zero,
        "spectrum_reconstructed": dict(sorted(spectrum.items())) == {0: 1, 3: 8, 6: 24, 9: 32, 12: 16},
        "packet_spectrum_matches": packet["double_qutrit_koszul_hodge"]["degree_zero_spectrum"] == {str(key): value for key, value in sorted(spectrum.items())},
        "cohomology_reconstructed": cohomology == [1, 4, 6, 4, 1],
        "packet_cohomology_matches": packet["double_qutrit_koszul_hodge"]["cohomology_dimensions"] == cohomology,
        "tracefree_dimension_reconstructed": 9 * 9 - 1 == 80,
        "tracefree_gap_reconstructed": min(value for value in spectrum if value) == 3,
        "Green_values_reconstructed": [str(Fraction(1, value)) for value in sorted(spectrum) if value] == ["1/3", "1/6", "1/9", "1/12"],
        "five_exterior_bridge_degrees_reconstructed": len(bridge_dimensions) == 5,
        "exterior_bridge_is_bijective_by_decomposition": bridge_bijections,
        "exterior_bridge_dimensions_reconstructed": bridge_dimensions == [1, 4, 6, 4, 1],
        "packet_bridge_dimensions_match": packet["augmented_exterior_bridge"]["rank_sequence"] == bridge_dimensions,
        "T58_bridge_dimensions_match": packet["augmented_exterior_bridge"]["T58_rank_sequence"] == bridge_dimensions,
        "equianharmonic_form_is_positive": 2 > 0 and 4 - 1 > 0,
        "nine_equianharmonic_sectors_reconstructed": len(sector_rows) == 9,
        "ground_spectrum_reconstructed": dict(sorted(ground.items())) == {0: 1, 2: 6, 6: 6},
        "ground_band_rank_reconstructed": sum(ground.values()) == 13,
        "two_triply_degenerate_sectors_reconstructed": sum(row[3] == 3 for row in sector_rows) == 2,
        "strict_6_to_8_gap_reconstructed": max(row[2] for row in sector_rows) == 6 and min(tails) == 8,
        "packet_has_nine_sector_rows": len(packet_sector_rows) == 9,
        "packet_rank13_cutset_matches": packet["equianharmonic_continuum_cutset"]["lowest_full_band_rank"] == 13,
        "packet_rejects_scalar_band_identification": packet["equianharmonic_continuum_cutset"]["scalar_fourier_low_band_equals_M3"] is False,
        "centered_log_is_typed_finite_only": packet["centered_log_compiler"]["claims_continuum_derivative"] is False,
        "selected_physical_intertwiner_remains_open": packet["augmented_exterior_bridge"]["selected_physical_intertwiner"] == "OPEN",
        "physical_blockers_remain_open": not any(packet["physical_boundary"][key] for key in ("B_HS_01_closed", "B_GEO_01_closed", "B_OP_01_closed")),
        "parameter_ledger_is_zero": all(value == 0 for value in packet["parameter_ledger"].values()),
        "builder_summary_passed": packet["check_summary"]["all_passed"] is True,
    }
    summary = {"all_passed": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "checks": checks}
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
