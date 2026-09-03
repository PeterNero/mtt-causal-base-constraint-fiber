# q79 eta9 graph-family normal-function value-map theorem

**Identifier:** CBF.T63
**Status:** closed exact finite linear value-map cutset; characteristic-zero
normal-function integration remains open
**Tier:** exact selected finite-residue sequence plus a source-locked
characteristic-zero execution contract

## 1. Purpose

This theorem joins three results that previously sat in different repositories:

1. the selected q79 graph-family tangent response and its finite normal
   quotient;
2. the corrected relation between a genus-82 fixed-fiber Picard value and the
   248-row surface normal function;
3. the actual rank-164 Gauss-Manin/BHT transport that must emit the
   characteristic-zero value.

The join removes a misleading target. A nonzero fixed-fiber Picard point is
not by itself a nonzero `beta_C`, because restriction from the surface
primitive space to one fiber has a 166-dimensional kernel. The earlier
fixed-fiber computation remains a valid initial-condition and non-torsion
result, but it does not reject the framed member from the beta-zero locus.

## 2. Selected finite objects

Let

```text
k = F_101[gamma]/(64 + 16 gamma + 33 gamma^2 + 44 gamma^3
                   + 89 gamma^4 + 24 gamma^5 + gamma^6).
```

The hash-bound UST.G3AM/G3AN response matrices define

```text
D : k^122 -> k^248.
```

The hash-bound UST.G3AS normal matrix defines

```text
N : k^248 -> k^126.
```

The builder and an independent verifier decode the original unsigned-byte
polynomial-basis matrices and perform arithmetic in `k`. They obtain

```text
rank(D) = 122,
rank(N) = 126,
N D = 0.
```

The graph-normal pairing packet independently supplies a square map

```text
B = N A_full C_incidence : k^126 -> k^126
```

with exact rank 126. Thus the graph-incidence complement and the finite
Deligne-normal quotient are isomorphic in the selected residue fiber.

## 3. Finite exact-sequence theorem

**Theorem CBF.T63A.** The selected finite sequence

```text
0 -> k^122 --D--> k^248 --N--> k^126 -> 0
```

is exact.

**Proof.** The exact row reduction gives `rank(D)=122`, so `D` is injective.
The exact product `N D=0` gives `im(D) subset ker(N)`. Since
`rank(N)=126`, rank-nullity gives

```text
dim ker(N) = 248 - 126 = 122 = dim im(D).
```

The inclusion is therefore equality. Finally `rank(N)=126`, equal to the
codomain dimension, makes `N` surjective. QED.

**Corollary CBF.T63B.** For a finite affine source `b in k^248`,

```text
b + D t = 0
```

has a solution exactly when `N b=0`. When it exists, the solution `t` is
unique.

**Proof.** If `b=-Dt`, then `Nb=0`. Conversely, `Nb=0` puts `b` in
`ker(N)=im(D)`. Injectivity of `D` gives uniqueness. QED.

This is the complete linearized criterion in the selected residue fiber. It
is not a proof that a modularly compatible source vanishes in characteristic
zero, and it is not the nonlinear beta-root theorem.

## 4. Why the fixed-fiber conclusion changes

H4-T133 distinguishes two spaces that H4-T131/H4-T132 had effectively treated
as though one determined the other:

```text
surface primitive rows:  (V tensor W)/<F>, dimension 248,
fiber holomorphic rows:   V/<F_e>,          dimension 82.
```

The evaluation map

```text
r_e : (V tensor W)/<F> -> V/<F_e>
```

is surjective of rank 82 and has kernel rank 166. Therefore a fixed-fiber
Picard value sees only one 82-row projection of the moving surface class. It
cannot determine the B-handle integral in 248 rows.

What remains valid from H4-T132 is substantial but narrower:

- the algebraic relative-Picard point is attached to the declared exact
  framed member and complex embedding;
- its fixed-fiber point is nonidentity at the declared isotopy tier;
- the stated low-order torsion exclusions remain valid;
- those facts provide initial data, not the integrated `beta_C` decision.

Consequently, neither one fixed-fiber nonidentity nor its double traversal is
the full BHT handle sweep.

## 5. Characteristic-zero value map

Let `p(t)` be the relative de Rham period state in the fixed rank-164 frame and
let `z(t)` be the 248-row surface accumulator. H4-T133/H4-T134 give the typed
system

```text
p' = C(t)^T p + s_D(t),
z' = ell(t) R(t)^T H p.
```

Here:

- `C(t)` is the rank-164 Gauss-Manin connection action;
- `s_D(t)` is the inhomogeneous relative-divisor source;
- `H` reads the rank-82 holomorphic block;
- `R(t)` restricts the 248 surface rows to the moving rank-82 fiber rows;
- `ell(t)` supplies the elliptic one-form and path tangent;
- `z(T)` represents `beta_C` before the integral-period quotient.

The rank-82 holomorphic block is not Gauss-Manin flat. Its complementary
rank-82 block is required, so an 82-state transport is not a valid shortcut.
The full forward state has rank `164+248=412`. A genuine
characteristic-zero normal-first evaluator would reduce this to
`164+126=290`, but the finite matrix `N` cannot be silently retyped as that
characteristic-zero operator.

## 6. What T133-T136 now supply

On each of the six physical path segments

```text
connector-out, edge-0, edge-1, edge-2, edge-3, connector-in,
```

the current chain supplies:

- a same-member midpoint Gauss-Manin backend and rank-82 moving-fiber frame;
- a boundary-trace formula descending to the fixed `H10` dual frame;
- an all-original-row top trace and Serre pairing;
- a projective `H01` lift of the inhomogeneous source;
- exact outward/return reversal at the sampled stem points.

These are six pointwise binary64 replays. They are not yet an intrinsic
normalization, a panelwise action/source, a directed ODE enclosure or a period
quotient. The largest reported Serre condition number is about `1.49e11`, so
small residuals cannot be promoted to coordinatewise accuracy without
multiprecision or interval certification.

## 7. Root selection is already solved conditionally

FSB.03g already proves the selected same-residue root contract. Its unit
minor gives local analytic coordinates, and multivariate Hensel uniqueness
applies after one same-source analytic `beta_C` is integrally normalized and
the complete 248-coordinate root is certified. CBF.T63 does not rebuild that
theorem.

The logical order is now:

```text
same-member panelwise source and rank-164 transport
    -> directed BHT integration and period quotient
    -> beta_C in 248 rows
    -> finite one-way or characteristic-zero normal test
    -> rejection, or the existing FSB.03g full-root theorem.
```

Normal compatibility alone is necessary but not sufficient for a nonlinear
root.

## 8. Closed and open rows

| Object | Current status |
|---|---|
| finite response `D` | 248 by 122, exact rank 122 |
| finite normal `N` | 126 by 248, exact rank 126 |
| finite exactness | `im(D)=ker(N)` |
| graph-normal quotient map | 126 by 126, exact rank 126 |
| fixed-fiber restriction | rank 82, kernel rank 166 |
| midpoint transport backends | 6/6, point replay |
| midpoint boundary sources | 6/6, point replay |
| midpoint projective `H01` lifts | 6/6, point replay |
| intrinsic source normalization | 0/1 |
| panelwise complete rank-164 action/source | 0/6 |
| directed BHT integration | 0/1 |
| accepted characteristic-zero `beta_C` rows | 0/248 |
| accepted characteristic-zero normal rows | 0/126 |
| selected physical beta root | open |

The active blockers remain `B.ETA9.01` and `B.ETA9.02`.

## 9. Next exact object

The next computation is not another fixed-fiber period campaign. It is a
panelwise characteristic-zero transport packet with all of the following in
one gauge:

1. intrinsic residue or integral normalization of the H4-T136 top trace and
   source lift;
2. multiprecision complete rank-164 Gauss-Manin action on each selected
   B-loop panel;
3. the same-member full de Rham source `s_D(t)` on those panels;
4. directed residual-to-ODE and quadrature bounds;
5. a period-lattice quotient for the accumulated 248 rows.

Edge 2 is the correct first panel because the current midpoint audits identify
it as the stiffest source/transport point. Edge 0 is the comparison panel.
Once those two panels pass under one normalization, the same construction can
be extended to the remaining four physical segments.

## 10. Claim boundary

CBF.T63 adds no observed input, fitted value, continuous parameter or discrete
selector. It does not claim that:

- the framed member is selected or rejected;
- a modular zero is a characteristic-zero zero;
- six midpoint samples constitute path integration;
- the finite exact sequence is the nonlinear beta-root theorem;
- q79, the Hull-Strominger endpoint, or Standard Model equivalence is closed.

## 11. Reproduction

```powershell
python build_q79_eta9_graph_family_normal_value_map.py
python verify_q79_eta9_graph_family_normal_value_map.py
```

The packet is
`q79_eta9_graph_family_normal_value_map.packet.json`. Every upstream packet
and binary matrix used by the proof is repository-relative and hash-bound.
