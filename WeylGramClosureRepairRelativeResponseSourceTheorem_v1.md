# Weyl-Gram Closure-Repair Relative-Response Source Theorem

**Claim ID:** `CBF.T20`  
**Date:** 2026-08-29  
**Status:** exact source-pinned finite theorem; provider-neutral physical promotion remains open

## 1. Purpose

`CBF.T19` proved that gauge-sector separation, Fourier pairing and universal
routing reduce the admissible Hermitian response module as

```text
36 -> 18 -> 9,
```

but do not select the line spanned by the finite routed response
`H_resp`.  It also proved that the last reduction is equivalent to a
relative-response intertwining condition.  This theorem constructs that last
finite source line without using an eta9/HYM endpoint, observed masses,
mixing data or a fitted response matrix.

The construction starts from the already source-pinned finite Weyl data

```text
P, X, Z, F3,
```

and one real source coordinate `t`.  The selected response blocks are the
first variations of two positive Gram families.  Consequently `H_resp` is
derived from primitive operators rather than inserted as an independent
matrix.

The theorem is deliberately finite and provider-neutral.  It does not prove
that the source coordinate is selected by a physical Lorentzian causal base,
that a continuum q79 endpoint emits it, or that its projective scale has the
physical action normalization.

## 2. Locked finite data

Work on `V=C^3` with the exact source-pinned operators

```text
P = [[1,0,0],
     [0,0,1],
     [0,1,0]],

X = [[0,1,0],
     [0,0,1],
     [1,0,0]],

Z = diag(1,omega,omega^2),
omega = exp(2 pi i/3),
```

and the unitary discrete Fourier transform `F3`, with the locked convention

```text
F3^* X F3 = Z.
```

The involution is Fourier invariant:

```text
P=P^*=P^-1,
F3^* P F3=P.
```

Define the two Weyl response directions

```text
M_s=I+X,
M_p=I+Z=F3^* M_s F3.
```

No matrix below is selected by reference to Standard Model measurements.

## 3. Closure-repair Gram families

For one real source coordinate `t`, define

```text
Y_s(t)=-P+t M_s,
Y_p(t)=-P+t M_p,
G_s(t)=Y_s(t)Y_s(t)^*,
G_p(t)=Y_p(t)Y_p(t)^*.
```

Every `G_alpha(t)` is positive semidefinite because it is a Gram operator.
At the neutral point,

```text
G_s(0)=G_p(0)=I.
```

The coordinate `t` is therefore a first-order deformation of the neutral
closure frame, not a fitted spectral coefficient.

### Lemma 3.1: exact first variation

For any matrix `M`,

```text
Y_M(t)=-P+tM
```

gives

```text
d/dt [Y_M(t)Y_M(t)^*] at t=0
  = -(P M^*+M P).
```

**Proof.** Expand the exact quadratic polynomial

```text
Y_M(t)Y_M(t)^*
 = PP^* - t(PM^*+MP^*) + t^2 MM^*.
```

Since `P=P^*`, differentiation at zero gives the claim.  Equivalently, the
centered exact difference

```text
[G_M(1)-G_M(-1)]/2
```

equals the same derivative because the even terms cancel.  No limiting or
floating-point argument is involved.  QED.

Apply the lemma to `M_s` and `M_p`.  The resulting blocks are

```text
A_shift = G_s'(0)
        = [[-2, 0,-2],
           [ 0,-2,-2],
           [-2,-2, 0]],

B_phase = G_p'(0)
        = [[-4,       0,       0],
           [ 0,       0,-1-i sqrt(3)],
           [ 0,-1+i sqrt(3),       0]].
```

These are exactly the source-pinned FSB.04e normalized first Hermitian
response blocks, but here they are outputs of the Gram variation.

### Lemma 3.2: Fourier covariance of the full family

For every real `t`,

```text
Y_p(t)=F3^* Y_s(t) F3,
G_p(t)=F3^* G_s(t) F3,
B_phase=F3^* A_shift F3.
```

**Proof.** Use Fourier invariance of `P` and
`M_p=F3^*M_sF3`; unitary conjugation commutes with Gram formation and
differentiation.  QED.

Thus phase and shift are one Weyl orbit, not two independently fitted source
matrices.

## 4. One shared coordinate and universal routing

Let the four finite sector slots be ordered

```text
(u,e,d,N).
```

The source-pinned routing assigns `B_phase` to `u,e` and `A_shift` to `d,N`:

```text
H_12(t)' at t=0
  = diag(B_phase,B_phase,A_shift,A_shift).
```

After tensoring with the corresponding rank-four internal projectors in
`H16`, this is

```text
H_derived
 = B_phase tensor R_phase + A_shift tensor R_shift
 = H_resp.
```

Here

```text
R_phase supports H16 slots {6,7,8,14},
R_shift supports H16 slots {9,10,11,15}.
```

### Lemma 4.1: source-coordinate reduction

Before identifications, four independent sector coordinates span four fixed
response directions.  Fourier pairing identifies `u` with `d` and `e` with
`N`, leaving two coordinates.  The lane-exchange-neutral diagonal identifies
the two pair coordinates, leaving the single vector

```text
(1,1,1,1).
```

The anti-diagonal pair coordinate transforms in the sign representation and
is not a neutral shared source.  Hence the invariant shared-coordinate source
space is one-dimensional.

This is a statement about source-coordinate symmetry.  It is stronger than
ordinary covariance of the resulting Hessian, which `CBF.T19` proved leaves a
nine-dimensional matrix module.

## 5. Relative-response intertwiner

Restrict to one active phase/shift pair.  Write

```text
H_resp,act=diag(B_phase,A_shift).
```

Both blocks have eigenvalues `(-4,-2,2)`, so this matrix is invertible.  The
Gram construction gives

```text
H_derived,act=H_resp,act.
```

Therefore

```text
T_rel=H_resp,act^-1 H_derived,act=I_6.
```

It commutes with

```text
diag(A_shift,A_shift),
diag(B_phase,B_phase),
lane parity,
Fourier lane exchange.
```

By `CBF.T19`, the commutant of this comparison algebra is scalar.  Hence the
Gram source satisfies the necessary-and-sufficient finite condition for the
last reduction

```text
9 -> span(H_resp).
```

At the normalized finite tier its coefficient is exactly one.

### Negative controls

Three failures distinguish the theorem from replay:

1. Replacing the shared coordinate by four independent sector coordinates
   restores a four-dimensional fixed-shape source space.
2. Imposing Fourier pairing but not shared neutrality leaves two dimensions.
3. Replacing `H_derived,act` by `I_6` preserves ordinary lane/Fourier
   covariance but fails the relative-response commutator test, as proved in
   `CBF.T19`.

Thus neither the matrix line nor the shared coefficient follows from ordinary
equivariance alone.

## 6. Affine closure action

Let `K=C^3 tensor H16`, let `N=H16`, and let `n0` be the already selected
neutral normal line.  Define

```text
psi(k)=1/2 n0 Re<k,H_derived k>
```

and the affine multiplier action

```text
A(n,k,lambda)
 = -epsilon(n)+Re<lambda,n+psi(k)>.
```

On the closure graph `n=-psi(k)`,

```text
A(-psi(k),k,lambda)
 = 1/2 Re<k,H_derived k>.
```

Since `H_derived=H_resp`, this reproduces the finite CBF.T17 quadratic from
the primitive Gram source.  In the finite identity-synthesis benchmark one
may take `U=I`, no complement, and obtain

```text
H_eff=H_derived,
T_rel=I.
```

This benchmark establishes algebraic compatibility.  It is not a physical
SYN packet: it has no selected continuum state space, domain, complement
resolvent or compactification map.

## 7. Parameter and provenance statement

The construction uses

```text
observed construction inputs:             0
fitted matrix coefficients:                0
new continuous response-shape parameters:  0
shared finite source coordinates:           1
normalized finite response coefficient:     1 (derived)
unselected physical action scales:          1
```

The source coordinate labels the one-dimensional tangent direction.  It is
not counted as a fitted Standard Model parameter.  Its absolute physical
normalization remains projective until a physical action density and quantum
normalization are supplied.

The primitive-root hash is formed from the exact encodings of `P,X,Z,F3`, the
sector route and the selected neutral source line.  The target response matrix
is excluded from that root.  The builder first constructs the Gram
derivatives and only then compares them with the earlier packet.

## 8. Exact conclusion

From the pinned finite Weyl primitives and one shared neutral source
coordinate, the positive Gram families above derive

```text
H_derived=H_resp
```

exactly.  They satisfy the `CBF.T19` relative-response intertwiner with
`T_rel=I`, close the finite normalized `9 -> 1` source-line construction, and
feed the CBF.T17 affine closure action with no observed input or fitted
coefficient.

This is an eta9-independent **finite direct-source theorem**.  It does not
close the physical endpoint.  In particular it supplies none of:

```text
a selected Lorentzian causal base,
a same-root continuum synthesis or nontrivial Feshbach complement,
a BV4 density and quantum master-equation certificate,
a physical action-scale normalization,
Lorentz/Higgs/Yukawa typing or measured value prediction.
```

Accordingly physical acceptance remains

```text
0/3 endpoint packets,
0/7 physical rows.
```

The next theorem no longer needs to invent the finite response source.  It
must select this primitive Gram deformation from a physical causal/continuum
root and transport its action and normalization through the provider-neutral
`GAS+SYN+BV4` contract.

