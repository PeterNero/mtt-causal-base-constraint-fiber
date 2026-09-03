# CBF.T69 q79 eta9 fixed-fiber/global-BHT scope correction theorem

## Status

`CORRECTED_RETRACTION_FIXED_FIBER_PICARD_POINT_DOES_NOT_EXCLUDE_GLOBAL_SPECTRAL_RANKS`

This theorem corrects the first T69 packet at commit `274730e`. That packet
applied the valid T68 twisted-rank determinant law to the wrong geometric
class. The correction preserves every calculation that H4-T132 actually
established and removes only the unsupported promotion to the global BHT
class.

## 1. What H4-T132 proved

For the exact algebraic framed member `C_fr`, H4-T132 studies the degree-zero
point

```text
P_e0=nu_alg(e_0) in Pic^0(C_e0)
```

on one selected genus-82 fiber. It proves, at every complex embedding,

```text
n P_e0 != 0 for every 1 <= n <= 1449.
```

The all-zero RREF framing remains deterministic rather than a coordinate-free
physical selection. Order 1450 remains merely the first multiplication not
resolved by those interval widths.

## 2. What H4-T133 corrected

Let

```text
V=H0(S,O_S(9H)),       dim V=83,
W=H0(E,O_E(3[0])),     dim W=3.
```

The primitive surface carrier and one fixed-fiber carrier are

```text
(V tensor W)/<F>,      rank 248,
V/<F_e>,               rank 82.
```

H4-T133 proves that evaluation at a smooth fiber induces a surjection

```text
r_e:(V tensor W)/<F> -> V/<F_e>
```

with kernel rank `166`. More importantly, the H4-T132 point is the initial
relative-Picard state for a moving chain. The normalized class required by the
BHT endpoint is instead the full handle sweep

```text
beta_C,j = integral_B sum_r R_rj(e) a_r(e) omega_E(e)
           modulo Pi_C(H2(C,Z)).
```

The nonzero initial point does not determine that closed-loop integral.
Transport can add, cancel or period-shift contributions along the loop.

## 3. Why the old exclusion does not follow

T68 proves the determinant condition

```text
rank-r twisted spectral object exists  =>  r beta_C=0.
```

H4-T132 proves

```text
r P_e0 != 0,  1 <= r <= 1449.
```

Since `P_e0` and `beta_C` are not the same object, these two statements cannot
be combined to infer `r beta_C != 0`. The earlier T69 implication therefore
fails at its middle identification, not in either input theorem.

## 4. Corrected theorem

**Fixed-Fiber/Global-BHT Scope Correction.** The H4-T132 non-torsion result
for `P_e0` excludes no spectral rank by itself. In particular, spectral ranks
`1` through `1449`, the intended spectral rank `1`/inverse-transform rank `3`
endpoint, and the global double-traversal or rank-`2` alternative all remain
undecided for `C_fr`.

**Proof.** H4-T133 gives the exact carrier distinction and explicitly
withdraws the implication from fixed-fiber nonidentity to nonzero global
`beta_C`. T68 requires multiplication of the latter class. No theorem in the
bound inputs identifies the two classes. Hence the premise needed for the old
rank exclusion is absent. QED.

This is a retraction of one derived claim, not a retraction of the H4-T132
period computation or the T68 determinant theorem.

## 5. Frontier

The next decisive computation is no longer a 122-direction family search.
First decide the already explicit member `C_fr` correctly:

1. propagate its rank-164 relative de Rham state around the selected B loop;
2. integrate all 248 quotient rows, or a separately proved characteristic-zero
   126-row normal projection;
3. reduce the result modulo the integral period lattice;
4. apply T68 only to that global class.

H4-T134 and its successors provide substantial pieces of the transport
backend. They do not turn the fixed-fiber point into the completed sweep.
Only after the global calculation is certified should the 122-dimensional
graph-family derivative be used to search for another member.

## 6. Reproduction

```powershell
python build_q79_eta9_framed_member_spectral_rank_exclusion.py
python verify_q79_eta9_framed_member_spectral_rank_exclusion.py
python -m unittest tests.test_q79_eta9_framed_member_spectral_rank_exclusion -q
```

No observed value, fitted parameter or physical selector is introduced.
