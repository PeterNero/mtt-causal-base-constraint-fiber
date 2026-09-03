# CBF.T69 q79 eta9 framed-member spectral-rank exclusion theorem

## Status

`CLOSED_EXACT_FRAMED_GRAPH_PRYM_SPECTRAL_RANKS_1_THROUGH_1449_EXCLUDED`

This theorem consumes, without re-proving, two established results:

1. H4-T132 binds a directed period calculation to one exact algebraic member
   `C_fr` of the G3AJ rank-123 fixed-residue graph-Prym ball and proves
   `n beta_C(C_fr) != 0` for every integer `1 <= n <= 1449`.
2. CBF.T68 imports the post-M32 twisted-spectral determinant theorem: a
   rank-`r` locally free `alpha`-twisted spectral object can exist only if
   `r[alpha]=0`.

T69 applies the second statement to the first. It does not relabel either
input theorem as new.

## 1. Same-member input

The H4-T132 member is not B89 or G3BI. It is the exact algebraization of the
deterministic framed point obtained by setting all 123 free correction digits
to zero in the frozen coefficient basis and RREF order. It lies in the G3AJ
graph-Prym ball. The associated algebraic relative-Picard point is

```text
P=nu_alg(e_0)=[pi^*O_K3(H-Rminus)|C_fr].
```

The same-source comparison identifies `P` with the restricted primitive
BHT/Deligne class `beta_C` on this carrier. H4-T132 proves that the directed
complex calculation is a base change of this exact algebraic point, not a
floating surrogate. It then certifies

```text
nP != 0 for every 1 <= n <= 1449.
```

In particular, a double shared-circle traversal does not annul the class.
Order 1450 is merely the first order not resolved by the current interval
widths; it is not a torsion candidate.

## 2. Rank-divisibility lemma

Let an `alpha`-twisted spectral object of rank `r` have transition matrices
obeying

```text
g_ij g_jk g_ki = alpha_ijk I_r.
```

Taking determinants gives

```text
delta(det g)_ijk = alpha_ijk^r,
```

so existence requires `r[alpha]=0`. Restricting to `C_fr` gives the necessary
condition

```text
r beta_C(C_fr)=0.
```

This is the already established T68/post-M32 theorem.

## 3. Theorem

**Framed-Member Spectral-Rank Exclusion.** No locally free twisted spectral
object of rank `r` with `1 <= r <= 1449` exists on `C_fr` for the selected
normalized BHT gerbe.

**Proof.** Such an object would force `r beta_C(C_fr)=0` by the determinant
law. H4-T132 proves the opposite for every integer in the stated range. This
contradiction excludes the object. QED.

The selected cover has degree three. A spectral rank `r` would therefore have
inverse-transform rank `3r`. The exact consequences include:

```text
spectral rank 1 -> inverse rank 3 -> rejected
spectral rank 2 -> inverse rank 6 -> rejected
spectral rank 3 -> inverse rank 9 -> rejected
...
spectral rank 1449 -> inverse rank 4347 -> rejected.
```

Thus the framed member cannot be rescued by double traversal, by the intended
rank-one construction, or by any low-rank higher-twist replacement in the
certified range. The first unresolved order would correspond to inverse rank
4350 and has no positive existence evidence.

## 4. What changed

T68 requested explicit same-residue graph-Prym candidates after excluding B89
and G3BI. H4-T132 has now supplied and decided the first such exact candidate.
T69 folds that decision into the endpoint rank theorem:

```text
B89                         rejected for intended rank
G3BI                        rejected for intended rank
C_fr in the G3AJ graph ball rejected for every spectral rank 1..1449
```

This is a genuine candidate elimination, not another normalization or method
packet. It also shows that moving to spectral rank two does not save this
member.

## 5. Boundary and next target

The result is scoped to `C_fr`. Its all-zero RREF framing is deterministic and
reproducible but has not been derived as a coordinate-free physical MTT
selector. T69 does not reject the other points of the G3AJ rank-123 ball and
does not prove that a beta-zero member exists.

The next nonduplicative object is the graph-family normal-function map

```text
Beta: B_graph -> Pic^0(C/B_graph)
```

together with its derivative on the 122 projective tangent directions. The
correct execution order is:

1. derive `dBeta` from the already selected family source and common marking;
2. apply the exact normal quotient as a cheap compatibility test;
3. if compatible, solve for and certify a different member with `Beta=0`;
4. if incompatible throughout the selected branch, prove the beta-zero locus
   empty and retire the rank-one q79 endpoint.

Repeating `C_fr`, changing its complex embedding, doubling its traversal, or
testing another low spectral rank cannot advance the proof.

## 6. Reproduction

```powershell
python build_q79_eta9_framed_member_spectral_rank_exclusion.py
python verify_q79_eta9_framed_member_spectral_rank_exclusion.py
python -m unittest tests.test_q79_eta9_framed_member_spectral_rank_exclusion -q
```

No observed value, fitted parameter or physical selector is used.
