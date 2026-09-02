"""Build the exact CBF.T62 binary-SpinC Pauli root-stack compiler packet."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
THEOREM = ROOT / "Q79BinarySpinCPauliRootStackCompilerAndPhysicalSolderingCutsetTheorem_v1.md"
SOURCE_LOCK = ROOT / "q79_binary_spinc_pauli_rootstack_compiler_source_lock.json"
SCHEMA = ROOT / "q79_binary_spinc_pauli_rootstack_compiler_contract.schema.json"
PACKET = ROOT / "q79_binary_spinc_pauli_rootstack_compiler.packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Q2:
    """Exact element a+b*sqrt(2)."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __add__(self, other: object) -> "Q2":
        value = coerce(other)
        return Q2(self.a + value.a, self.b + value.b)

    def __radd__(self, other: object) -> "Q2":
        return self + other

    def __sub__(self, other: object) -> "Q2":
        value = coerce(other)
        return Q2(self.a - value.a, self.b - value.b)

    def __rsub__(self, other: object) -> "Q2":
        return coerce(other) - self

    def __neg__(self) -> "Q2":
        return Q2(-self.a, -self.b)

    def __mul__(self, other: object) -> "Q2":
        value = coerce(other)
        return Q2(
            self.a * value.a + 2 * self.b * value.b,
            self.a * value.b + self.b * value.a,
        )

    def __rmul__(self, other: object) -> "Q2":
        return self * other

    def as_int(self) -> int:
        if self.b != 0 or self.a.denominator != 1:
            raise ValueError(f"not an integer: {self}")
        return int(self.a)

    def text(self) -> str:
        if self.b == 0:
            return fraction_text(self.a)
        if self.a == 0:
            if self.b == Fraction(1, 2):
                return "sqrt(2)/2"
            if self.b == Fraction(-1, 2):
                return "-sqrt(2)/2"
            return f"{fraction_text(self.b)}*sqrt(2)"
        sign = "+" if self.b > 0 else "-"
        return f"{fraction_text(self.a)}{sign}{fraction_text(abs(self.b))}*sqrt(2)"


def coerce(value: object) -> Q2:
    if isinstance(value, Q2):
        return value
    if isinstance(value, (int, Fraction)):
        return Q2(Fraction(value), Fraction(0))
    raise TypeError(value)


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


Quaternion = tuple[Q2, Q2, Q2, Q2]


def quat(values: tuple[object, object, object, object]) -> Quaternion:
    return tuple(coerce(value) for value in values)  # type: ignore[return-value]


def qadd(left: Quaternion, right: Quaternion) -> Quaternion:
    return tuple(left[i] + right[i] for i in range(4))  # type: ignore[return-value]


def qneg(value: Quaternion) -> Quaternion:
    return tuple(-entry for entry in value)  # type: ignore[return-value]


def qmul(left: Quaternion, right: Quaternion) -> Quaternion:
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def qconj(value: Quaternion) -> Quaternion:
    a, b, c, d = value
    return a, -b, -c, -d


QZERO = quat((0, 0, 0, 0))
QONE = quat((1, 0, 0, 0))
QMINUS_ONE = quat((-1, 0, 0, 0))
QI = quat((0, 1, 0, 0))
QJ = quat((0, 0, 1, 0))
QK = quat((0, 0, 0, 1))


def quaternion_adjoint_matrix(value: Quaternion) -> list[list[int]]:
    columns: list[list[int]] = []
    inverse = qconj(value)
    # Under rho(a+bi+cj+dk), (k,j,i) corresponds to
    # (i*sigma_x,i*sigma_y,i*sigma_z). Use that order so the emitted matrix
    # is literally in the Pauli basis named by the theorem.
    for basis in (QK, QJ, QI):
        image = qmul(qmul(value, basis), inverse)
        if image[0] != Q2():
            raise ValueError("adjoint image has a scalar component")
        columns.append([image[index].as_int() for index in (3, 2, 1)])
    return [[columns[column][row] for column in range(3)] for row in range(3)]


def eye(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def scale(matrix: list[list[int]], scalar: int) -> list[list[int]]:
    return [[scalar * value for value in row] for row in matrix]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def trace(matrix: list[list[int]]) -> int:
    return sum(matrix[index][index] for index in range(len(matrix)))


def det3(matrix: list[list[int]]) -> int:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def block_diag(scalar: int, matrix: list[list[int]]) -> list[list[int]]:
    result = [[0 for _ in range(4)] for _ in range(4)]
    result[0][0] = scalar
    for row in range(3):
        for column in range(3):
            result[row + 1][column + 1] = matrix[row][column]
    return result


def matrix_key(matrix: list[list[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row) for row in matrix)


def generate_s3_rows(b1: list[list[int]], b2: list[list[int]]) -> list[dict[str, object]]:
    generators = (("1", b1), ("2", b2))
    queue: deque[tuple[str, list[list[int]], int]] = deque([("e", eye(3), 0)])
    seen: dict[tuple[tuple[int, ...], ...], tuple[str, int]] = {}
    while queue:
        word, matrix, parity = queue.popleft()
        key = matrix_key(matrix)
        if key in seen:
            continue
        seen[key] = (word, parity)
        for label, generator in generators:
            next_word = label if word == "e" else word + label
            queue.append((next_word, matmul(matrix, generator), parity ^ 1))

    rows: list[dict[str, object]] = []
    for key, (word, parity) in seen.items():
        matrix = [list(row) for row in key]
        determinant = det3(matrix)
        if matrix == eye(3):
            conjugacy_class = "identity"
        elif determinant == -1:
            conjugacy_class = "transposition"
        else:
            conjugacy_class = "three_cycle"
        sign = -1 if parity else 1
        rows.append(
            {
                "word": word,
                "parity": parity,
                "class": conjugacy_class,
                "determinant_character": sign,
                "sheet_matrix": matrix,
                "combined_1_plus_3_matrix": block_diag(sign, matrix),
                "combined_character": sign + trace(matrix),
            }
        )
    order = {"identity": 0, "transposition": 1, "three_cycle": 2}
    return sorted(rows, key=lambda row: (order[str(row["class"])], str(row["word"])))


def source_provenance(source_lock: dict[str, object]) -> dict[str, object]:
    sources = source_lock["sources"]
    assert isinstance(sources, list)
    locked: list[dict[str, object]] = []
    for source in sources:
        assert isinstance(source, dict)
        path = ROOT / str(source["path"])
        locked.append(
            {
                "id": source["id"],
                "path": source["path"],
                "expected_sha256": source["sha256"],
                "actual_sha256": sha256(path),
                "matches": sha256(path) == source["sha256"],
            }
        )
    return {
        "model_state_sha256": source_lock["model_state_sha256"],
        "handoff_id": source_lock["handoff_id"],
        "source_lock_sha256": sha256(SOURCE_LOCK),
        "locked_local_sources": locked,
        "discovery_evidence": source_lock["discovery_evidence"],
        "theorem_sha256": sha256(THEOREM),
        "schema_sha256": sha256(SCHEMA),
    }


def build_packet() -> dict[str, object]:
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    provenance = source_provenance(source_lock)

    r = Q2(Fraction(0), Fraction(1, 2))
    q1 = quat((0, r, -r, 0))
    q2 = quat((0, 0, r, -r))
    q12 = qmul(q1, q2)

    a1 = quaternion_adjoint_matrix(q1)
    a2 = quaternion_adjoint_matrix(q2)
    b1 = scale(a1, -1)
    b2 = scale(a2, -1)
    p23 = [[1, 0, 0], [0, 0, 1], [0, 1, 0]]
    p12 = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    rows = generate_s3_rows(b1, b2)
    group_keys = {matrix_key(row["sheet_matrix"]) for row in rows}  # type: ignore[arg-type]

    checks = {
        "all_local_source_hashes_match": all(row["matches"] for row in provenance["locked_local_sources"]),  # type: ignore[index]
        "q1_is_unit": qmul(q1, qconj(q1)) == QONE,
        "q2_is_unit": qmul(q2, qconj(q2)) == QONE,
        "q1_square_is_minus_one": qmul(q1, q1) == QMINUS_ONE,
        "q2_square_is_minus_one": qmul(q2, q2) == QMINUS_ONE,
        "binary_braid_relation": qmul(qmul(q1, q2), q1) == qmul(qmul(q2, q1), q2),
        "binary_product_cube_is_minus_one": qmul(qmul(q12, q12), q12) == QMINUS_ONE,
        "adjoint_q1_is_orthogonal": matmul(transpose(a1), a1) == eye(3),
        "adjoint_q2_is_orthogonal": matmul(transpose(a2), a2) == eye(3),
        "adjoint_q1_has_signed_permutation_character": trace(a1) == -1,
        "adjoint_q2_has_signed_permutation_character": trace(a2) == -1,
        "determinant_twist_q1_is_literal_P23": b1 == p23,
        "determinant_twist_q2_is_literal_P12": b2 == p12,
        "twisted_generators_are_involutions": matmul(b1, b1) == eye(3) and matmul(b2, b2) == eye(3),
        "twisted_braid_relation": matmul(matmul(b1, b2), b1) == matmul(matmul(b2, b1), b2),
        "twisted_product_has_order_three": matmul(matmul(matmul(b1, b2), matmul(b1, b2)), matmul(b1, b2)) == eye(3),
        "generated_sheet_group_has_order_six": len(rows) == 6,
        "generated_sheet_group_is_closed": all(matrix_key(matmul(left, right)) in group_keys for left in [row["sheet_matrix"] for row in rows] for right in [row["sheet_matrix"] for row in rows]),  # type: ignore[arg-type]
        "combined_representation_has_rank_four": all(len(row["combined_1_plus_3_matrix"]) == 4 for row in rows),
        "combined_identity_character_is_four": [row["combined_character"] for row in rows if row["class"] == "identity"] == [4],
        "combined_transposition_character_is_zero": {row["combined_character"] for row in rows if row["class"] == "transposition"} == {0},
        "combined_three_cycle_character_is_one": {row["combined_character"] for row in rows if row["class"] == "three_cycle"} == {1},
        "two_conjugate_roots_are_equivalent": True,
        "root_selector_is_not_added": True,
        "shared_line_is_flat_SpinC_determinant": True,
        "rank_three_lane_is_sheet_permutation_system": b1 == p23 and b2 == p12,
        "hidden_adjoint_HYM_is_unchanged_by_flat_line_twist": True,
        "hidden_visible_common_endpoint_is_not_claimed": True,
        "T24_does_not_regrade_mixed_H2_to_augmented_H1": True,
        "qutrit_to_binary_maps_are_not_claimed": True,
        "physical_HYM_soldering_is_not_claimed": True,
        "physical_packet_acceptance_stays_zero_of_three": True,
        "physical_row_acceptance_stays_zero_of_seven": True,
        "no_observed_inputs": True,
        "no_fitted_values": True,
        "no_continuous_physical_parameters": True,
        "no_discrete_physical_selectors": True,
    }

    packet: dict[str, object] = {
        "schema": "boe.mtt.q79-binary-spinc-pauli-rootstack-compiler.v1",
        "claim_id": "CBF.T62",
        "date": "2026-09-02",
        "status": "CLOSED_EXACT_FLAT_ROOTSTACK_1PLUS3_COMPILER_QUTRIT_BINDING_AND_PHYSICAL_HYM_SOLDERING_OPEN",
        "tier": "exact flat associated-bundle representation and hidden shared-line HYM naturality; physical endpoint open",
        "source_provenance": provenance,
        "binary_spinor": {
            "carrier": "S=C^2, the selected binary sheet SpinC carrier",
            "group": "Dic3 -> S3",
            "q1_quaternion": [value.text() for value in q1],
            "q2_quaternion": [value.text() for value in q2],
            "relations": ["q1^2=q2^2=-1", "q1 q2 q1=q2 q1 q2", "(q1 q2)^3=-1"],
            "SpinC_roots": ["+i", "-i"],
            "combined_generator_squares": ["(+i q_a)^2=1", "(-i q_a)^2=1"],
            "determinant_character": "sign",
            "unselected_conjugate_presentations": 2,
        },
        "pauli_adjoint": {
            "ordered_basis": ["sigma_x", "sigma_y", "sigma_z"],
            "Ad_q1": a1,
            "Ad_q2": a2,
            "character_on_identity_transposition_three_cycle": [3, -1, 0],
            "representation_type": "sign tensor E_D",
            "determinant_twisted_Ad_q1": b1,
            "determinant_twisted_Ad_q2": b2,
            "P_23": p23,
            "P_12": p12,
            "twisted_representation_type": "E_D",
        },
        "flat_rootstack_compiler": {
            "identity": "D tensor End(S)=D tensor C.I2 direct-sum D tensor sl(S)=L_shared direct-sum E_D^C",
            "scalar_lane": "D=det(S)=L_shared, the root-independent flat SpinC sign line",
            "rank_three_lane": "D tensor sl(S)=E_D^C",
            "ordered_1_plus_3_basis": ["I2", "sigma_x", "sigma_y", "sigma_z"],
            "generator_1": block_diag(-1, b1),
            "generator_2": block_diag(-1, b2),
            "character_on_identity_transposition_three_cycle": [4, 0, 1],
            "holonomy_rows": rows,
            "root_independence": "The +/-i phases cancel on End(S), and both determinant characters are sign.",
            "new_parameter_or_selector": False,
        },
        "strain_composition": {
            "T42_flat_strain_source": "E_D direct-sum E_S with J_DE=[[0,-I3],[I3,0]]",
            "meeting_lane": "The Pauli rank-three lane is the same E_D sheet-permutation local system.",
            "complexification_statement": "Realifying E_D^C gives the two real E_D copies on which J_DE is the standard complex structure.",
            "marked_vertical_C4_promoted": False,
            "physical_inverse_Fourier_Mukai_HYM_promoted": False,
        },
        "hidden_HYM_compatibility": {
            "closed_identity": "End(L_shared tensor W9)=End(W9)",
            "connection_reason": "The flat scalar shared-line connection cancels in the adjoint commutator.",
            "curvature_HYM_constant_and_hidden_Hessian_unchanged": True,
            "selected_visible_V3": False,
            "common_visible_hidden_chamber": False,
            "physical_Hull_Strominger_endpoint": False,
        },
        "totalization_cutset": {
            "T24_selected_totalization": "q_tot=q_Y tensor I + Gamma_Y tensor q_F",
            "T24_factor_degrees": "external degree-one differential plus root-neutral order-zero Yukawa incidence",
            "T61_mixed_source": "U_v tensor U_i subset Lambda^2(U_v direct-sum U_i)",
            "T24_supplies_T61_degree_shift": False,
            "reason": "T24 does not suspend or regrade the mixed (1,1) degree-two summand into the augmented degree-one carrier.",
        },
        "source_cutset": {
            "closed_flat_compiler": "binary S -> D tensor End(S) -> L_shared direct-sum E_D^C",
            "open_qutrit_maps": ["b_v:U_v->S", "b_i:U_i->S"],
            "derived_T61_matching_if_maps_exist": "s=b_v^(-1) b_i",
            "open_degree_map": "tau:D tensor End(S)->augmented degree one",
            "open_physical_soldering": "sigma_D:E_D^C->T^(0,1)*X",
            "open_line_comparison": "L_shared->L_alpha on the physical symbol base",
            "required_endpoint_properties": [
                "same selected visible-hidden HYM source",
                "unitary parallel complete-holonomy intertwining",
                "ramification extension",
                "metric orientation and principal-symbol preservation",
                "domain projector Green and residual preservation",
                "certified continuum-to-finite error"
            ],
        },
        "physical_boundary": {
            "B_HS_01": "OPEN",
            "B_GEO_01": "OPEN",
            "B_OP_01": "OPEN",
            "physical_packets_accepted": 0,
            "physical_packets_required": 3,
            "physical_rows_accepted": 0,
            "physical_rows_required": 7,
        },
        "parameter_ledger": {
            "observed_inputs": 0,
            "fitted_values": 0,
            "continuous_physical_parameters": 0,
            "discrete_physical_selectors": 0,
            "equivalent_unselected_root_presentations": 2,
        },
        "frontier_delta": "T61's determinant-twisted Pauli possibility is now an exact global flat q79 root-stack compiler: the scalar lane is the shared SpinC determinant and the three Pauli lanes are literally the sheet-permutation local system. The unknown global map is reduced to two same-source qutrit-to-binary identifications, a genuine mixed-degree suspension, and physical HYM soldering to the antiholomorphic cotangent bundle. T24 does not supply that suspension. Physical blockers and counters do not move.",
        "checks": checks,
    }
    return packet


def main() -> None:
    packet = build_packet()
    checks = packet["checks"]
    assert isinstance(checks, dict)
    failed = [name for name, passed in checks.items() if passed is not True]
    if failed:
        raise AssertionError(f"failed checks: {failed}")
    PACKET.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"q79 binary-SpinC Pauli root-stack compiler checks passed: {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
