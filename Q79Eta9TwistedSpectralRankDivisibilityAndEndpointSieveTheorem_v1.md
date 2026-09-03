# Q79 eta9 late-candidate twisted-spectral endpoint-sieve theorem

**Identifier:** CBF.T68

**Status:** exact general theorem with exact B89 and G3BI applications

**Physical status:** the zero-`beta_C` requirement is derived for the existing
rank-one spectral endpoint; no replacement member or HYM endpoint is selected

## 1. Why this theorem is needed

The q79 program has used `beta_C=0` as the admissibility gate for the
normalized rank-one spectral object. That can look like an imposed definition.
It is not. Once the endpoint is required to be a rank-one object twisted by the
inverse restricted gerbe, vanishing of the twisting class is forced by descent.

This distinction matters after the exact nonzero results for G3BI and B89.
One cannot rescue either member merely by saying that a nonzero gerbe may carry
twisted sheaves. Higher-rank twisted objects can exist only under a rank
divisibility condition, and changing the spectral rank changes the downstream
Fourier--Mukai transform, index, matter multiplicities and finite carrier.

## 2. Consumed determinant theorem

The determinant argument in this section is **not new in T68**. It was already
proved for the degree-three q79 cover in the QG
`q79PostM32GlobalGerbeTargetAndRankCutsetTheorem`. T68 consumes that theorem
and applies it to the later exact B89 and G3BI obstruction results.

Let `alpha_ijk` be a scalar Cech two-cocycle on a cover and let a locally free
`alpha`-twisted object of rank `r` have transition matrices `g_ij`. With one
choice of sign convention, the twisted cocycle law is

```text
g_ij g_jk g_ki = alpha_ijk I_r.                 (2.1)
```

Taking determinants gives

```text
det(g_ij) det(g_jk) det(g_ki) = alpha_ijk^r.    (2.2)
```

The left side is the Cech coboundary of the determinant one-cochain. Hence

```text
r [alpha] = 0.                                  (2.3)
```

This proves a necessary condition for every finite rank. For `r=1`, it says
`[alpha]=0`. Conversely, if `[alpha]=0`, a scalar one-cochain trivializes the
cocycle and yields a rank-one twisted object. Therefore

```text
rank-one alpha-twisted object exists
    if and only if
[alpha] = 0.                                    (2.4)
```

For `r>1`, equation (2.3) is only necessary. It does not prove that an
appropriate twisted vector bundle exists. The Brauer period divides every
admissible rank, while the index and local-freeness conditions may be stronger.
This is standard twisted-sheaf/period-index mathematics; see Lieblich,
[Twisted sheaves and the period-index problem](https://arxiv.org/abs/math/0511244),
and Antieau,
[Cohomological obstruction theory for Brauer classes and the period-index problem](https://arxiv.org/abs/0909.2352).

The same determinant calculation applies to the flat/Deligne cocycle used by
the q79 endpoint. If that class is non-torsion, no finite rank can kill it.
If it is torsion, its order must divide the proposed rank.

## 3. Consequence for the existing q79 endpoint

The existing normalized BHT/Fourier--Mukai contract uses a degree-three cover,
asks for an inverse-gerbe-twisted **rank-one spectral object**, and is intended
to reconstruct a rank-three bundle. Applying (2.4) gives

```text
existing rank-one q79 spectral endpoint
    exists
if and only if
beta_C = 0.                                     (3.1)
```

Thus the zero-`beta_C` gate is not an optional preference and is not an
empirical selector. It is the descent condition for the endpoint already used
by the SM-parity and HYM compiler chain.

## 4. Exact B89 application

H4-T126 gives a nonzero B89 class and a mod-two cokernel character `w` with

```text
w(M-I) = 0,
w n     = 1 mod 2.                              (4.1)
```

For an odd rank `r`, multiplication by `r` preserves this mod-two shadow:

```text
w(r n) = r w(n) = 1 mod 2.                      (4.2)
```

Consequently no odd spectral rank can exist on this same class. In particular,
B89 is excluded at spectral ranks one and three.

The calculation does **not** prove that the integral B89 class has exact order
two. Spectral rank two merely passes this parity test; existence does not
follow. On a degree-three cover it would reconstruct rank six, not the intended
rank three.

## 5. Exact G3BI application

H4-T87 maps the selected G3BI normal-function class to

```text
4 mod 20 in Z/20Z.                              (5.1)
```

This local component has exact order five. If `r beta_C=0` globally, every
functorial local image must also vanish, so

```text
r (4 mod 20) = 0
    only if
5 divides r.                                    (5.2)
```

Spectral ranks one and three are therefore impossible. Spectral rank five is
the first rank that passes this local necessary condition, but no rank-five
twisted object is constructed. On the degree-three cover its inverse transform
would have rank fifteen. The pairing-four detector has component `16 mod 20`,
also of order five, and gives the same rank sieve.

H4-T87 proves the order of the **local component**, not that the full global
Deligne class has exact order five.

## 6. What this says about T67

CBF.T67 rigorously certifies a nonzero characteristic-zero Cayley/Serre scalar
and first derivative on the B89 method member. T68 now proves why that scalar
cannot be promoted to the existing physical rank-one endpoint: B89 fails the
rank-one descent gate before any normalization value is considered.

The T67 result remains valuable as a conditioning, normalization and
characteristic-zero transport theorem. It is not a measured or predicted
physical value.

## 7. The legitimate routes forward

### 7.1 Preserve the current rank-one endpoint

The candidate search must proceed in this order:

1. Apply the finite local-component sieve.
2. Reject every candidate with a nonzero component.
3. For each component-trivial survivor, compute the identity-component affine
   Deligne coordinate.
4. Retain only a member with certified `beta_C=0`.
5. Execute the normalized rank-one inverse Fourier--Mukai transform and HYM
   endpoint on that member.

The next search family is the explicit same-residue G3AJ/G3BJ inventory, after
removing G3BI and B89 and without reusing either rejected chart as a physical
endpoint.

### 7.2 Deliberately change the endpoint rank

A nonzero-`beta_C` theory is mathematically possible only as a different
construction. It must declare the rank before inspecting physical values,
prove that the class period and index permit that rank, construct a locally
free twisted object, and redo the inverse transform, family index, matter
multiplicities and `27`-state comparison.

For a spectral-rank-three alternative, both known candidates still fail: B89
has a nonzero mod-two shadow and G3BI has an order-five local component. Such
an alternative would in any case reconstruct rank nine, as the earlier
post-M32 theorem already observed for order-three twisting. The first
not-yet-ruled-out ranks from the current partial information are spectral rank
two for B89 (inverse rank six) and spectral rank five for G3BI (inverse rank
fifteen). Neither is a shortcut to the current rank-three MTT/SM chain.

## 8. Parameter and claim boundary

```text
observed values used:               0
new continuous fit parameters:      0
new discrete fit parameters:        0
selected beta-zero member:          no
selected physical HYM endpoint:     no
```

T68 does not re-prove the post-M32 rank cutset. Its new result is to apply that
cutset to the later exact candidate data and exclude four candidate/spectral-
rank combinations. It does not select a surviving member, prove a higher-rank
twisted object, determine the exact order of the B89 class, or promote T67 to
a physical result.

## 9. Reproducibility

The portable source snapshot is
`q79_eta9_twisted_spectral_rank_divisibility.source.json`. The exact packet is
`q79_eta9_twisted_spectral_rank_divisibility.packet.json`. Rebuild and verify
with

```powershell
python build_q79_eta9_twisted_spectral_rank_divisibility.py
python verify_q79_eta9_twisted_spectral_rank_divisibility.py
```

The verifier reconstructs the rank tables, checks the B89 and T67 local
hashes, verifies the G3BI component arithmetic, and enforces every scope
guardrail.
