# Relative Product-Supercharge Single-Operator Source Theorem

**Claim ID:** `CBF.T22`  
**Date:** 2026-08-29  
**Status:** exact canonical relative-source theorem; upper-MTT selection and
physical endpoint promotion remain open

## 1. Result

`CBF.T20` derives the finite response `H_derived=H_resp` from routed
Weyl-Gram families. `CBF.T21` inserts that response as a smooth order-zero
endomorphism of a normally hyperbolic q79 chart operator and gives a
nontrivial auxiliary Schur lift. The remaining algebraic source question is
whether the causal operator and finite response can be shadows of one
operator family rather than two separately supplied Hessians.

They can. Define one routed finite map `Y(t)`, its canonical odd
supercharge `D_F(t)`, and the graded product operator

```text
D_Lambda(t)=D_Y tensor I_96 + Gamma_Y tensor Lambda D_F(t).
```

After subtracting the neutral internal square, the target-chirality first
variation is exactly

```text
Lambda^2 H_derived.
```

Thus the coefficient called `mu^2` in `CBF.T21` is not an independent
response parameter:

```text
mu^2=Lambda^2.
```

All response shape data and the causal principal symbol now come from one
canonical relative product-supercharge family. The one remaining continuous
quantity is the universal dimensionful scale `Lambda`. Existing metrology
results prove that dimensionless source data cannot select its absolute SI
value. One declared universal length or energy primitive supplies it as
`Lambda=1/L0=E0`, with no sector-specific scale.

This is a single-operator and single-composite-root theorem. It is not yet a
selected physical-root theorem: the corpus does not derive the composite
product choice from a stricter upper-MTT selector, identify the response with
the physical Lorentz/Higgs/Yukawa second variation, or provide the continuum
HYM and quantum-BV endpoint data.

## 2. Locked carriers

Let

```text
K=C^3_family tensor H16,
dim_C K=48.
```

On `C^3_family`, retain the exact CBF.T20 primitives

```text
P=P*=P^-1,
X^3=Z^3=I,
F3* X F3=Z,
F3* P F3=P.
```

Let `R_phase` and `R_shift` be the orthogonal H16 projectors with supports

```text
R_phase: {6,7,8,14},
R_shift: {9,10,11,15}.
```

They have rank four each and disjoint support. Put

```text
C=P tensor I16,
M=(I+Z) tensor R_phase + (I+X) tensor R_shift.
```

Then `C=C*=C^-1`. No target response matrix occurs in these definitions.

The external input is the selected framed q79 globally hyperbolic spin base
at its declared free tier. The established continuum composition supplies the
typed rank-48 three-family carrier on that base. Its physical global vacuum,
strict action coefficients and interacting quantum theory remain open.

## 3. One routed Gram family

Define

```text
Y(t)=-C+tM : K_+ -> K_-.
```

Its target and source Gram operators are

```text
G_-(t)=Y(t)Y(t)*,
G_+(t)=Y(t)*Y(t).
```

At the neutral point,

```text
G_-(0)=G_+(0)=I48.
```

Their exact first variations are

```text
H_- = G_-'(0)=-(C M*+M C),
H_+ = G_+'(0)=-(C M+M* C).
```

By the CBF.T20 routing,

```text
H_-
 = B_phase tensor R_phase + A_shift tensor R_shift
 = H_derived
 = H_resp.
```

Moreover,

```text
H_+=C H_- C.
```

So the two chiral response blocks are unitarily conjugate. Each has rank 24
and squared Frobenius norm 192. The source block is not a second fitted
matrix.

## 4. Canonical odd supercharge

On the auxiliary graded carrier

```text
K_F=K_+ direct_sum K_-,
Gamma_F=diag(I48,-I48),
```

define

```text
D_F(t)=[[0,Y(t)*],
        [Y(t),0]].
```

Then

```text
D_F(t)*=D_F(t),
Gamma_F D_F(t)+D_F(t) Gamma_F=0,
D_F(t)^2=diag(G_+(t),G_-(t)).
```

In particular,

```text
D_F(0)^2=I96,
(d/dt)D_F(t)^2|_0=diag(H_+,H_-).
```

Within the declared minimal class, this lift is unique: an odd self-adjoint
operator with zero diagonal and prescribed map `Y:K_+->K_-` must have the
displayed two off-diagonal blocks. The 96-dimensional carrier is an
auxiliary graded lift. It is not a claim of 96 additional physical particle
states.

## 5. Graded causal product and neutral subtraction

Let `D_Y` be the external Dirac-type operator and `Gamma_Y` its grading, so

```text
D_Y Gamma_Y+Gamma_Y D_Y=0.
```

For a positive inverse-length scale `Lambda`, define

```text
D_Lambda(t)=D_Y tensor I96 + Gamma_Y tensor Lambda D_F(t).
```

The cross terms cancel exactly:

```text
D_Lambda(t)^2
 =D_Y^2 tensor I96 + Lambda^2 I tensor D_F(t)^2.
```

This is the same graded product identity used by the CBF.T13
product-Dirac compiler, applied here to the closure-repair supercharge rather
than relabelled as the physical matter Dirac operator.

Define the neutral-relative square

```text
L_rel,Lambda(t)
 =D_Lambda(t)^2-Lambda^2 I tensor D_F(0)^2
 =D_Y^2 tensor I96
  +Lambda^2 I tensor (D_F(t)^2-I96).
```

The subtraction is forced within the class of scalar neutral counterterms:
requiring the internal contribution to vanish at `t=0` fixes its coefficient
to `Lambda^2`, since `D_F(0)^2=I96`.

At the neutral point and to first order,

```text
L_rel,Lambda(0)=D_Y^2 tensor I96,
L_rel,Lambda'(0)=Lambda^2 I tensor diag(H_+,H_-).
```

Restricting to `K_-` gives

```text
L_target(t)
 =D_Y^2 tensor I48
  +t Lambda^2 I tensor H_derived+O(t^2).
```

Therefore the CBF.T21 tangent operator

```text
L_mu=L0+mu^2 H_derived
```

is the target-chirality derivative of this one family with
`mu^2=Lambda^2`.

## 6. Causality

The entire internal relative square is differential order zero on the
four-dimensional base. Hence the principal symbol of the target block is

```text
sigma_2(L_target)(x,xi)
 =g^{-1}(xi,xi) I48,
```

independently of `t` and `Lambda`. On every declared q79 on-shell chart, the
existing Green-hyperbolic theorem therefore applies. The response changes
the lower-order dynamics but neither introduces a second causal cone nor
turns the constraint fiber into extra spacetime.

This is consistent with standard product-operator and Green-hyperbolic
machinery; the exact identities above are proved directly. Useful external
comparisons include product spectral triples and indefinite Kasparov
products:

- [Uuye, products of regular spectral triples](https://arxiv.org/abs/0911.0816);
- [van den Dungen and Rennie, indefinite Kasparov modules](https://arxiv.org/abs/1503.06916);
- [Baer, Green-hyperbolic operators](https://arxiv.org/abs/1310.0738).

## 7. Scale theorem

The finite source fixes a dimensionless direction. The external Dirac
operator has inverse-length dimension. Therefore the product requires one
quantity `Lambda` of inverse-length dimension.

For every positive `s`, the replacement

```text
Lambda -> s Lambda
```

leaves invariant:

```text
the primitive Weyl root,
the normalized response line,
the rank and kernel dimensions,
the relative intertwiner T_rel=I,
the causal cone,
all dimensionless source ratios.
```

It changes only the overall response coefficient by

```text
mu^2 -> s^2 mu^2.
```

Consequently no dimensionless finite theorem can select the absolute value
of `Lambda`. This is the same one-dimensional scale orbit proved by the
existing dimensional-metrology no-go.

At the explicitly adopted one-universal-metrology-primitive tier, choose a
physical length or energy standard not fitted to the target observable:

```text
Lambda=1/L0=E0,
mu^2=1/L0^2=E0^2.
```

The conditional q79 clock theorem then uses the same primitive and gives

```text
gamma=log(448) E0=log(448)/L0.
```

Thus no second clock or response scale is introduced. The number `448` fixes
the dimensionless coefficient, not the absolute unit. Strict no-metrology
absolute prediction remains impossible in the current formalization.

## 8. What is and is not one-root closure

Hash the following source-only payload:

```text
CBF.T20 primitive root,
q79 framed causal source hashes,
typed rank-48 continuum-carrier source hashes,
the graded tensor-sum rule,
the canonical odd lift,
the neutral-relative subtraction rule,
the symbolic universal scale role Lambda=E0=1/L0.
```

The payload excludes `H_resp`, `A_shift`, `B_phase`, observed masses and any
numerical value of `E0` or `L0`. Both the causal operator and finite response
are then derived from the resulting single composite-root operator family.

This closes the **mathematical single-operator provenance** obstruction. It
does not prove that upper MTT uniquely selects this composite root as the
physical universe. A deterministic product of two pinned inputs is stronger
than juxtaposition, but weaker than an upstream selection theorem.

## 9. Endpoint classification

The exact advance is:

```text
single causal/finite operator family:       closed,
target response from relative square:       closed,
nontrivial auxiliary Schur lift:             inherited closed,
mu^2 reduced to Lambda^2:                    closed,
number of sector-specific scale knobs:       zero,
universal metrology primitives required:     one,
upper-MTT composite-root selection:          open,
physical Lorentz/Higgs/Yukawa identity:      open,
continuum HYM/Galerkin intertwiner:           open,
physical BV pushforward and QME:              open.
```

The theorem advances the provenance and synthesis subclauses of `GAS` and
`SYN`, and it supplies a causal quadratic operator compatible with the free
`BV4` compiler. It does not satisfy the full physical packet contracts.
Physical acceptance therefore remains

```text
0/3 packets,
0/7 rows.
```

## 10. Relation to A52

This theorem does not reuse A52's profile spectral-action normalization.
A52 studies cutoff moments and gauge normalization and proves that universal
gauge unification does not follow from that profile construction. Here no
spectral cutoff function or measured gauge coordinate is used. The object is
the neutral-relative square of a source-pinned operator family. Accordingly
the new theorem neither evades nor contradicts A52's normalization no-go.

## 11. Conclusion

The finite response and causal propagation no longer need to be represented
by unrelated operators. The exact chain is now

```text
P,X,Z,F3 and fixed routing
  -> Y(t)
  -> odd closure-repair supercharge D_F(t)
  -> one graded product D_Lambda(t)
  -> neutral-relative square
  -> causal target block with response Lambda^2 H_derived.
```

The next hard theorem is narrower than before: select this composite root by
an upper-MTT rule and prove that its target block is the actual
Lorentz/Higgs/Yukawa or other physical second variation. If the adopted
one-primitive tier is retained, absolute scale itself is no longer a
sector-by-sector research target; it is one declared universal metrological
input shared with the q79 clock and GR normalization programs.
