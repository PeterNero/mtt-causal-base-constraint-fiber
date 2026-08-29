# q79 eta9 Endpoint Unlock Decision Program

Date: 2026-08-29

Status: research strategy and execution contract, not a theorem.

Kernel lock: `572272ade96f4bf2d89dd41c48701a125cd0736343167819855b2cf41f377b45`

Primary blocker: `B.ETA9.01`, followed by `B.ETA9.02` and `B.HS.01`.

## Objective

Select or obstruct the physical eta9/Deligne/HYM endpoint without repeating a
large reconstruction that cannot change the frontier. The target is not merely
the value of `beta_C` on an arbitrarily fixed member. It is the joint selected
root contract

```text
C_* in U_graph-Prym^(smooth,ff,free) intersect Z(beta_C),
```

together with the chain-level integral lift, transported source metric and
same-source visible bundle required by the Hull-Strominger endpoint.

If the selected residue classes contain no root, the required output is a
rigorous obstruction. That is a valid and scientifically useful branch result.

## Locked Results

The following are inputs and must not be recomputed or weakened:

1. Gate 1 is complete at 30/30 groups and 225/225 support columns.
2. Gate 2 supplies 248 stage-one rows, a `1509 x 248` source block and a
   `1509 x 1509` GF(11) operator. GF(11) completion is not a
   characteristic-zero connection.
3. The graph-Prym affine kernel has dimension 123; radial gauge leaves 122
   projective tangent directions. The primitive response has size `248 x 122`,
   rank 122 and left-normal dimension 126.
4. Characteristic-zero response rank 122 is stable on same-residue lifts.
   Tangent insufficiency is therefore not the current blocker.
5. The selected three-cycle detector has Gram matrix `-2 I_3` and all three
   cross-pairings vanish. It is rigorously non-detecting and is retired.
6. The static frozen-Schur shortcut is invalid. Dynamic Gauss-Manin/Riccati
   transport cannot be replaced by a lower-coordinate backsolve.
7. Exact selected-source p-adic action through `p^2048` and the height cutset
   are closed. More blind p-adic depth or ordinary rational reconstruction is
   retired.
8. Once a selected integral branch, cochain metric and chain-level null
   homotopy are supplied, the normalized Deligne lift, twisted Prym line and
   visible rank-three bundle are deterministic downstream constructions.
9. The seven physical endpoint rows factor through three same-root typed
   packets: geometry plus action (`GAS`), spectral synthesis (`SYN`) and
   four-dimensional BV compactification (`BV4`). Physical `C4` and rank-102
   Galerkin/Feshbach execution are derived from `GAS+SYN`.

## Central Reframing

The old serial question was:

```text
choose member -> reconstruct full transport -> evaluate beta_C -> test member.
```

The correct selection question is:

```text
solve source constraints and beta_C together -> certify one root or exclude
each selected residue ball -> compile the endpoint from that same root.
```

This turns `beta_C` from a late diagnostic into part of the source-selection
equation. It also prevents an arbitrary member choice from becoming a hidden
physical knob.

## Constraint Object

Every candidate must carry one immutable `source_orbit_id`. Its unknowns and
constraints are:

```text
Discrete source data
  graph-Prym orbit and selected 101-adic residue ball
  integral branch/parity and first primitive Bezout prefix

Root coordinates
  122 projective graph-Prym coordinates u

Analytic source data
  dynamic Gauss-Manin transport
  transported cochain/HYM metric
  chain-level integral marking and null homotopy

Equations
  smoothness, finite-flatness and free-orbit conditions
  248 beta_C coordinates
  126 left-normal compatibility coordinates
  visible-hidden common-chamber, Bianchi and descent constraints

Derived outputs
  twisted Prym line and visible V3
  GAS, then SYN, then derived C4 and rank-102 execution
  BV4 from the same source root
```

No endpoint object may be imported from a different `source_orbit_id` merely
because it has the required type.

## Ordered Decision Gates

### Gate A: exact primitive detector

Compute the ordered integral residues `<h_Z,e_i>` already available from the
selected affine basis and stop at the first prefix whose gcd is one. Emit the
canonical Bezout dual. This decides whether a pairing-one detector is available
without constructing a full rank-1509 frame.

In parallel, construct the cheapest exact full-lattice annihilator or
dual-lattice character allowed by the existing quotient contract. A certified
nonintegral interval for one character proves `beta_C != 0`. Integer lattice
membership proves `beta_C = 0`.

Exit A:

```text
primitive Bezout detector + source hashes + exact replay,
```

or a proof that the selected affine subsystem cannot provide one.

### Gate B: one-vector quotient transport

Transport the selected pairing-four root tube `z4` along the exact
discriminant-avoiding arc. Do not transport the complete 1509-vector frame.
Compute only:

```text
the integral B89 marking of z4,
the 248 root period/residue readout,
and the period columns used by the chosen dual character.
```

If `4 beta_C` is nonzero, the current member is rejected. If it vanishes, no
zero claim is permitted: escalate to the first selected odd/pairing-one Bezout
dual and decide `beta_C` there.

Exit B is an exact or interval-certified `beta_C=0` witness, a nonzero
obstruction, or a precise proof that the quotient detector is insufficient.

### Gate C: goal-oriented characteristic-zero solve

If Gate B requires the large action solve, compute the requested readout as a
functional, not the entire source vector. For a linearized source equation

```text
A x = b,       desired output = ell(x),
```

solve the adjoint problem

```text
A^* y = ell,   ell(x) = <y,b>.
```

Start with one dual character. Add rows only when the preceding row cannot
decide the quotient. Use the existing Woodbury decomposition, symmetry blocks
and a directed residual-to-functional error bound. A sparse directed `LDL*`
factorization of the 7746 core is a fallback only after this adjoint reduction
is proved inadequate.

Exit C is a certified scalar or sparse-row readout with an independently
checked error enclosure. A full source reconstruction is not an exit by itself.

### Gate D: certified joint graph-Prym root

Evaluate the nonlinear map `beta_C(u)` on the full 122-dimensional projective
tangent, not the obsolete 33-direction slice. Use modular evaluation only as a
filter:

1. Reject a residue ball when one of the 126 normal coordinates is provably
   nonzero.
2. When the residual vanishes modulo 101 and a `122 x 122` Jacobian minor is a
   unit, apply multivariate Hensel lifting.
3. Convert the lifted candidate to characteristic zero and certify it with
   interval Newton or a Krawczyk operator, using adjoint/Jacobian-vector products
   rather than a dense reconstructed Jacobian where possible.
4. Prove smoothness, finite-flatness and free-orbit conditions on the same box.

A successful Gate D emits one unique root in its selected residue ball. Failed
normal compatibility or disjoint interval images give a rigorous no-root
certificate for that ball. Exhaust the finite selected residue set before
declaring the q79 branch obstructed.

### Gate E: same-source endpoint compilation

During Gate D, transport and retain the integral branch, chain-level period
lift and source-derived cochain metric. Do not reconstruct them after selecting
the root. Compile in this order:

```text
root + integral lift + metric
  -> normalized null homotopy
  -> twisted Prym line
  -> visible V3
  -> visible-hidden common HYM chamber and Bianchi/descent data
  -> GAS
  -> SYN
  -> derived C4 and rank-102 Galerkin/Feshbach execution
  -> BV4 from the same root
```

This is the first point at which downstream Closure Dynamics, physical SM
values, GR normalization, interacting QFT and physical QG receive the physical
source they require. It unlocks their execution; it does not automatically
prove those theories.

## Computation Budget and Stop Rules

Every calculation must name the gate and a truth value it can change.

1. No new full-frame or all-period calculation before Gate A is complete.
2. No 7746-core factorization before a goal-oriented adjoint prototype is
   tested on one exact character and one characteristic-zero enclosure.
3. No additional p-adic depth, generic rational reconstruction, old
   33-direction search, static Schur solve or three-cycle expansion.
4. Checkpoint by certified residue ball, quotient character or endpoint row,
   never only by elapsed compute time.
5. A failure certificate is promoted immediately; it removes a residue class
   or branch and is genuine progress.
6. A long run is stopped when its current output cannot satisfy a named exit
   clause even if allowed to finish.

## Preferred Route Ranking

1. Primitive Bezout/dual-character decision plus one-vector `z4` transport.
2. Full 122-variable joint root solve with modular filtering and certified
   characteristic-zero interval validation.
3. Goal-oriented adjoint solves for only the required quotient and Jacobian
   functionals.
4. Symmetry-reduced directed sparse `LDL*` on the 7746 core if and only if the
   preceding functional route cannot certify its error.
5. Full rank-1509 frame and dense 248-period matrix only as a documented last
   resort.

## First Concrete Work Package

The next implementation should be a small, independently replayable packet,
not a month-long campaign:

```text
ETA9.QD1
  freeze the selected affine basis and source hashes;
  emit ordered residues and first gcd-one Bezout prefix;
  bind z4 and the pairing-one escalation rule;
  choose one exact dual-lattice character;
  compile its primal and adjoint readout contracts;
  run a finite-field consistency replay;
  state exactly which characteristic-zero interval solve remains.
```

Only after `ETA9.QD1` passes should the characteristic-zero one-vector/adjoint
calculation be launched. Its output has a binary interpretation: selected
class zero, selected class nonzero, or an explicit enclosure gap to close.

## Success and Falsification Criteria

Success requires all of the following on one source root:

```text
beta_C = 0,
unique certified graph-Prym root in a selected residue ball,
integral path lift and normalized chain-level Deligne trivialization,
twisted line and visible V3,
common visible-hidden HYM chamber with Bianchi/descent compatibility,
hash-bound GAS source packet.
```

The q79 physical branch is obstructed if every selected residue ball has a
certified nonzero normal residual, a nonzero Deligne character, or failure of
the required smooth/free/common-chamber conditions. Such an obstruction should
be reported plainly rather than hidden behind another reconstruction layer.

## Frontier Delta Intended by This Program

This document does not close `B.ETA9.01`. It narrows the next admissible work to
a finite decision tree, makes the Deligne equation part of source selection,
and postpones the expensive 7746 and rank-1509 reconstructions until a targeted
functional certificate proves they are necessary.
