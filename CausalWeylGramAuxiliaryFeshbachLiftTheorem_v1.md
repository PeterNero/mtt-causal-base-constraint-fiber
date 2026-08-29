# Causal Weyl-Gram Auxiliary Feshbach Lift Theorem

**Claim ID:** `CBF.T21`  
**Date:** 2026-08-29  
**Status:** exact general theorem and exact source-pinned auxiliary witness;
conditional q79 chart composition; no physical endpoint promotion

## 1. Question

`CBF.T20` derives the normalized finite response

```text
H_derived=H_resp
```

from the primitive Weyl data `P,X,Z,F3` and one shared neutral source
coordinate.  It does not by itself give a causal spacetime operator or a
nontrivial synthesis/complement.

Independently, the q79 QM/QFT source proves that, on every declared on-shell
q79 background chart, the gauge-fixed free field complex is Green-hyperbolic
and its corrected functional domain is equicausal.  That result does not
contain the CBF.T20 response source.

This theorem composes the two existing exact objects without using eta9 or a
future endpoint calculation.  It answers three narrower questions:

1. Can the finite response be placed in a causal operator without changing
   its propagation cone?
2. Can it arise from a nontrivial upper auxiliary action and exact Feshbach
   reduction rather than the identity benchmark?
3. Which physical endpoint clauses remain after that construction?

## 2. Inputs and source separation

The finite source root is the CBF.T20 hash of

```text
(P,X,Z,F3, sector route, shared source line).
```

The causal root is the separately hashed q79 gauge-fixed Green-hyperbolic
free-BV/equicausal chart certificate.  Both are exact at their declared
tiers.  No theorem presently identifies them as outputs of one physical
upper source.  This theorem therefore records

```text
exact source roots used:       2
same physical root proved:     no.
```

That distinction is decisive for the `GAS+SYN+BV4` acceptance contract.

## 3. Causal lower-order lift

Let `(O,g)` be a globally hyperbolic Lorentzian chart and let `E->O` be a
finite-rank Hermitian vector bundle carrying the internal 48-dimensional
response representation.  Let

```text
L0: Gamma(E) -> Gamma(E)
```

be a formally self-adjoint normally hyperbolic operator.  Thus its principal
symbol is

```text
sigma_2(L0)(x,xi)=-g_x^{-1}(xi,xi) I_E
```

up to the fixed sign convention.

Let `H_derived` be the smooth Hermitian bundle endomorphism obtained by
transporting the CBF.T20 finite matrix through the A46/A47 typed carrier on
the chart.  For a real coefficient `mu^2`, define

```text
L_mu=L0+mu^2 H_derived.
```

Here `mu^2 H_derived` has differential order zero.

### Theorem 3.1: causal-cone invariance

`L_mu` is normally hyperbolic with exactly the same principal symbol and
characteristic cone as `L0`.

**Proof.** The principal symbol of order two ignores every order-zero term.
Therefore

```text
sigma_2(L_mu)=sigma_2(L0).
```

Normal hyperbolicity is defined by this metric principal symbol.  The
advanced and retarded Green operators consequently exist and are unique on a
globally hyperbolic base, with causal support governed by the metric cone.
QED.

This is standard Lorentzian operator theory; see:

- [Baer, Green-hyperbolic operators](https://arxiv.org/abs/1310.0738);
- [Baer-Ginoux-Pfaeffle, Wave equations on Lorentzian manifolds](https://arxiv.org/abs/0806.1036).

The theorem is about a normally hyperbolic response bundle.  It does not
identify `H_derived` with a chiral fermion mass.  A physical fermion mass or
Yukawa insertion requires a Lorentz/Higgs left-right map that CBF.T20 does
not supply.

### Corollary 3.2: q79 chart realization

On every chart covered by the locked q79 gauge-fixed free-BV theorem, the
normally hyperbolic gauge, ghost or Higgs-type principal carrier can be
tensored with the finite response carrier and deformed by `mu^2 H_derived`
without changing its null cone.  The pre-existing equicausal Peierls,
Hadamard-star and time-slice theorems then apply to the resulting linear
normally hyperbolic operator at the same conditional chart tier.  The active
functional domain is equicausal, not the superseded unrestricted microcausal
class; see [Hawkins-Rejzner-Visser](https://arxiv.org/abs/2312.15203).

This corollary does not select the chart as the physical global background.

## 4. Primitive auxiliary carrier

Let `K=C^3 tensor H16` be the 48-dimensional retained internal carrier.  The
CBF.T20 primitive involution `P` defines

```text
C=P tensor I16: K -> E_aux,
```

where `E_aux` is a second copy of `K`.  Since `P=P^*=P^-1`,

```text
C^*C=CC^*=I48.
```

Thus the coupling is source-derived and unitary.  It introduces no matrix
coefficient.

For any unitary retained automorphism `g`, equip the auxiliary copy with the
transported action

```text
g_aux=C g C^*.
```

Then

```text
g_aux C=C g.
```

So `C` is an exact intertwiner.  In particular, the A47 gauge action is
identity on the family factor and hence commutes directly with `C`; the A50
shared-circle action is preserved as well.

## 5. Nontrivial upper action

For a dynamical response field `phi` and an algebraic auxiliary field `e`,
define

```text
S_up(phi,e)
 = 1/2 integral_O [
       <phi,L_mu phi>
       + <C phi+e,C phi+e>
   ] dvol_g.
```

The block Hessian is

```text
K_mu = [[L_mu+C^*C, C^*],
        [C,           I48]].
```

The complement block is invertible and the coupling is nonzero of rank 48.
This is therefore not the CBF.T20 identity-synthesis benchmark.

### Theorem 5.1: exact algebraic elimination

The auxiliary Euler-Lagrange equation is

```text
e=-C phi.
```

Substitution gives

```text
S_eff(phi)=1/2 integral_O <phi,L_mu phi> dvol_g.
```

Equivalently, the Feshbach/Schur complement of the auxiliary block is

```text
F_I(K_mu)
 = L_mu+C^*C-C^* I48^-1 C
 = L_mu.
```

**Proof.** Complete the square or perform the displayed block subtraction.
The identity `C^*C=I48` makes cancellation exact.  QED.

The graph synthesis

```text
U phi=(phi,-C phi)
```

satisfies

```text
U^* K_mu U=L_mu.
```

Moreover,

```text
ker(K_mu)={ (phi,-C phi) : phi in ker(L_mu) }.
```

Hence `U` gives an exact kernel isomorphism.  At the normalized finite
internal witness `L0=0`, `mu^2=1`, the Schur complement is `H_derived`, the
upper `96 x 96` block has rank 72, and its kernel has dimension 24.

The full mixed block is not itself a normally hyperbolic operator because
`e` is algebraic.  It must be eliminated before Green operators are formed.
This is the same ordering already enforced for the Nakanishi-Lautrup
auxiliary in the locked q79 free-BV certificate.

## 6. Relative response and scale

On one active phase/shift pair,

```text
H_derived,act=H_resp,act.
```

At the normalized finite witness,

```text
T_rel=H_resp,act^-1 H_derived,act=I6.
```

For the causal deformation, the response coefficient is `mu^2`, so the
zeroth-order relative response is

```text
T_rel(mu)=mu^2 I6.
```

This commutes with the CBF.T19 comparison algebra.  Thus the shape and
relative-intertwiner clauses are exact for every `mu`; only the physical
dimensionful value of `mu` is missing.

One cannot set that physical value by declaring the normalized finite
coordinate to be one.  The base operator carries dimensions, and the ratio
between its kinetic normalization and the response endomorphism is a genuine
physical action-scale question.

## 7. Endpoint-contract classification

The exact progress is:

```text
GAS:
  conditional quadratic chart action form constructed;
  physical background, one-root provenance and response scale open.

SYN:
  nontrivial 96 -> 48 algebraic auxiliary Schur/Feshbach subclause closed;
  continuum HYM synthesis, projection and error bounds open.

BV4:
  a Green-hyperbolic equicausal free-BV chart carrier already exists;
  the response is a causal zeroth-order endomorphism on a response bundle;
  physical SM field insertion, BRST interaction typing and same-root BV
  provenance remain open.
```

The composition does not satisfy the physical same-source rule because its
finite and causal inputs have distinct hashes and no root-identification
theorem.  Therefore no GAS, SYN or BV4 packet is physically accepted here.

## 8. Parameter ledger

```text
observed construction inputs:              0
fitted coefficients:                       0
new dimensionless response-shape knobs:    0
normalized auxiliary-frame coefficients:   0
unselected dimensionful response scales:   1  (mu^2)
unselected physical global backgrounds:    1  (source-selection class)
```

The auxiliary normalization is not a physical knob.  Replacing
`e` by `s e` and transporting the auxiliary metric/coupling accordingly is a
frame change.  The dimensionful coefficient `mu^2` relative to `L0` is not a
frame change and remains open.

## 9. Conclusion

The finite Weyl-Gram response now has an eta9-independent causal and
nontrivial auxiliary realization:

```text
primitive Gram source
  -> H_derived
  -> smooth order-zero causal deformation L_mu
  -> primitive-P upper auxiliary action
  -> exact Schur reduction back to L_mu.
```

The construction proves that a q79 HYM endpoint is not logically required
for the **operator-theoretic existence** of a causal response lift or a
nontrivial synthesis.  Q79 may still be the physical geometric provider, but
that is a source-selection question rather than a prerequisite for the
general mathematics.

What remains is sharply smaller but still physical: identify the finite and
causal roots as one selected upper source, derive `mu^2` from that source,
type the response into the Lorentz/Higgs/Yukawa or other physical field
sector, and provide the matching BV4 interaction/density and continuum error
certificate.  Physical acceptance remains

```text
0/3 packets,
0/7 rows.
```

