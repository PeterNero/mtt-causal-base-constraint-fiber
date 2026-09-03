# q79 B89 same-source promotion and rejection theorem

**Identifier:** `CBF.T54 / H4-T123--126`

## Statement

For the frozen B89 source, the exact 252-strand moving carrier and 36-strand
signed-boundary carrier each cover all 2,195 source intervals. Their complete
288-strand common-source isotopy is collision free and has the hash-bound
24,999-letter Arb-certified Artin word. The induced rank-164 affine return
operator has a nonzero integral cokernel class. Under the already-certified
H4-T120 same-source affine-Deligne adapter,

```text
beta_C(B89) != 0.
```

Therefore B89 is excluded from the beta-zero locus.

## Dynamic certificate

The component campaigns certify 3,044 branch subcells and 2,282 boundary
subcells. Most of the 28,295,568 mixed homotopy pairs are separated by outward
rectangles. Nine use stronger convex-region certificates. The remaining 473
diagnostic calls, representing 463 unique target tuples, are certified by a
residual-aware shared-parameter argument.

That argument is important. Branch and boundary are not independent motions:
they use the same source parameter `s` and homotopy parameter `a`. After
subtracting their Taylor predictors, the mixed displacement is

```text
(1-a)(Delta P(s) + E(s)) + a Delta G(s),
```

where `E` is bounded by the two certified Krawczyk residual boxes. A strict
Rouche separation inequality, with finite component subdivision only where
needed, certifies noncollision without replacing the correlated motion by an
artificial Cartesian product. All 463 unique targets pass independent replay;
the minimum certified mixed margin is
`3.7412459608088255e-7`.

## Affine-Deligne conclusion

The certified Artin word feeds the frozen segmented adapter and rank-164
mod-two affine replay. Independently recomputed linear algebra gives

```text
rank(M)       = 164,
rank(M-I)     = 42,
left nullity  = 122,
w(M-I)        = 0,
w n           = 1 mod 2.
```

If the affine translation `n` had an integral `(M-I)` preimage, reduction
modulo two would contradict the final two equations. Its integral cokernel
class is therefore nonzero. H4-T120 identifies that same-source class with the
B-handle Deligne-Leray connecting class, proving the stated rejection. An
independent Kernel process reproduced the affine payload byte for byte.

## Claim boundary

This theorem rejects B89. It does not prove the exact order of the integral
class, select a replacement member of `U_eta9`, compute the 248 period rows,
construct a visible HYM connection, or close the Hull-Strominger endpoint.
The next candidate should first pass the same finite affine/component sieve;
only a certified zero topological class should advance to periods and HYM.

## Reproduction

```powershell
python build_q79_b89_downstream_promotion_readiness.py
python verify_q79_b89_downstream_promotion_readiness.py
python q79_b89_same_source_deligne_promote.py --skip-assembly
python verify_q79_b89_same_source_deligne_promotion.py
```

Remove `--skip-assembly` to deterministically rebuild the three aggregate
carriers from the complete component and shared-parameter result indexes before
promotion.
