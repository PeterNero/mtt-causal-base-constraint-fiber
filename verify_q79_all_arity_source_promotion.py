"""Independently verify the q79 all-arity source-promotion packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_q79_higher_transfer_jet_filtration_and_m5_feasibility as high
import build_q79_symmetric_response_retraction_transferred_m3 as low
import build_q79_symmetric_weyl_calculus_isometric_retraction as sym


ROOT = Path(__file__).resolve().parent
PACKET_PATH = ROOT / "q79_all_arity_source_promotion.packet.json"
LOCK_PATH = ROOT / "q79_all_arity_source_promotion_source_lock.json"
THEOREM_PATH = ROOT / "AllArityContractionMorphismSourcePromotionTheorem_v1.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def act(name: str, source: low.SourceFrozen) -> low.SourceFrozen:
    thawed = low.thaw_source(source)
    if name == "translation":
        return low.freeze_source(sym.affine_action(thawed, 1, 1, 4))
    if name == "fourier":
        return low.freeze_source(sym.fourier_action(thawed, 4))
    raise ValueError(name)


def target_act(name: str, source: low.Target) -> low.Target:
    return low.target_projection(act(name, low.target_inclusion(source)))


def inverse(value: sym.E) -> sym.E:
    denominator = value.a * value.a - value.a * value.b + value.b * value.b
    return sym.E((value.a - value.b) / denominator, -value.b / denominator)


def target_signature(name: str, basis: tuple[low.Target, ...]) -> tuple[tuple[int, sym.E], ...]:
    index = {item: position for position, item in enumerate(basis)}
    records: list[tuple[int, sym.E]] = []
    for item in basis:
        image = target_act(name, item)
        assert len(image[0]) + len(image[1]) == 1
        coefficient = image[0][0][3] if image[0] else image[1][0][1]
        records.append((index[low.target_scale(inverse(coefficient), image)], coefficient))
    return tuple(records)


def compose(
    left: tuple[tuple[int, sym.E], ...], right: tuple[tuple[int, sym.E], ...]
) -> tuple[tuple[int, sym.E], ...]:
    return tuple(
        (left[middle][0], left[middle][1] * coefficient)
        for middle, coefficient in right
    )


def power(
    source: tuple[tuple[int, sym.E], ...], exponent: int
) -> tuple[tuple[int, sym.E], ...]:
    out = tuple((index, sym.wk.ONE) for index in range(len(source)))
    for _ in range(exponent):
        out = compose(source, out)
    return out


def closure(
    generators: tuple[tuple[tuple[int, sym.E], ...], ...]
) -> set[tuple[tuple[int, sym.E], ...]]:
    identity = tuple((index, sym.wk.ONE) for index in range(len(generators[0])))
    found = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            candidate = compose(generator, current)
            if candidate not in found:
                found.add(candidate)
                frontier.append(candidate)
    return found


def check() -> dict[str, bool]:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    sources = tuple(low.source_basis())
    target_records = tuple(low.old_basis() + low.ideal_basis())
    targets = tuple(record[2] for record in target_records)
    translation = target_signature("translation", targets)
    fourier = target_signature("fourier", targets)
    identity = tuple((index, sym.wk.ONE) for index in range(len(targets)))

    source_chain = all(
        act(name, low.source_differential(item))
        == low.source_differential(act(name, item))
        for name in ("translation", "fourier")
        for item in sources
    )
    source_product = all(
        act(name, low.source_product(left, right))
        == low.source_product(act(name, left), act(name, right))
        for name in ("translation", "fourier")
        for left in sources
        for right in sources
    )
    contraction = all(
        act(name, low.target_inclusion(item))
        == low.target_inclusion(target_act(name, item))
        for name in ("translation", "fourier")
        for item in targets
    ) and all(
        low.target_projection(act(name, item))
        == target_act(name, low.target_projection(item))
        and act(name, low.transfer_homotopy(item))
        == low.transfer_homotopy(act(name, item))
        for name in ("translation", "fourier")
        for item in sources
    )
    target_m2 = all(
        target_act(name, low.m2(left, right))
        == low.m2(target_act(name, left), target_act(name, right))
        for name in ("translation", "fourier")
        for left in targets
        for right in targets
    )

    labels = {label: index for index, (label, _, _) in enumerate(target_records)}
    selected_indices = (
        labels["C:0,0,1"],
        labels["C:0,0,1"],
        labels["C:0,0,1"],
        labels["C:1,0,1"],
        labels["C:1,0,0"],
    )
    m5_value = high.generic_mn(selected_indices)
    selected_m5_equivariance = True
    for name, signature in (("translation", translation), ("fourier", fourier)):
        mapped = tuple(signature[index][0] for index in selected_indices)
        coefficient = sym.wk.ONE
        for index in selected_indices:
            coefficient *= signature[index][1]
        selected_m5_equivariance &= target_act(name, m5_value) == low.target_scale(
            coefficient, high.generic_mn(mapped)
        )

    endpoint = packet["endpoint_contract"]
    expected_local_hashes = {item["path"]: item["sha256"] for item in lock["local_sources"]}
    checks = {
        "packet_schema": packet.get("schema")
        == "boe.mtt.q79-all-arity-source-promotion.packet.v1",
        "claim_id": packet.get("claim_id") == "CBF.T11",
        "source_lock_hash": packet.get("source_lock_sha256") == sha256(LOCK_PATH),
        "theorem_hash": packet.get("theorem_sha256") == sha256(THEOREM_PATH),
        "all_builder_checks_pass": all(packet.get("checks", {}).values()),
        "independent_source_chain_checks": source_chain,
        "independent_source_product_checks": source_product,
        "independent_contraction_square_checks": contraction,
        "independent_transferred_m2_checks": target_m2,
        "translation_order_three": power(translation, 3) == identity,
        "fourier_order_four": power(fourier, 4) == identity,
        "induced_target_group_order_36": len(closure((translation, fourier))) == 36,
        "selected_m5_is_nonzero": m5_value != low.ZERO_TARGET,
        "selected_m5_equivariance": selected_m5_equivariance,
        "physical_endpoint_rows_are_zero_of_seven": endpoint["physical_rows_accepted"] == 0
        and endpoint["physical_rows_total"] == 7,
        "physical_endpoint_rows_remain_open": all(
            row["state"] == "open" for row in endpoint["physical_source_rows"]
        ),
        "blocker_states_are_not_claimed_changed": not packet["frontier_delta"][
            "blocker_states_changed"
        ],
        "local_DGA_packet_hash": sha256(
            ROOT / "q79_symmetric_weyl_calculus_isometric_retraction.packet.json"
        )
        == expected_local_hashes["q79_symmetric_weyl_calculus_isometric_retraction.packet.json"],
        "local_contraction_packet_hash": sha256(
            ROOT / "q79_symmetric_response_retraction_transferred_m3.packet.json"
        )
        == expected_local_hashes["q79_symmetric_response_retraction_transferred_m3.packet.json"],
        "local_higher_packet_hash": sha256(
            ROOT / "q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json"
        )
        == expected_local_hashes["q79_higher_transfer_jet_filtration_and_m5_feasibility.packet.json"],
    }
    return checks


def main() -> None:
    checks = check()
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"independent all-arity source-promotion checks failed: {failed}")
    print(f"independent all-arity source-promotion verification passed: {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
