# Weyl-Polarized Product-Dirac One-Loop Pushforward and Direct G0 Source Theorem

**Claim:** CBF.T43
**Date:** 2026-08-30
**Tier:** exact same-source, flat-background, local one-loop theorem for the direct product-Dirac route; not a global q79 HYM determinant theorem

## 1. Purpose

CBF.T35 computed the fixed-source radial one-loop shape but retained two
normalizations,

```text
pfaffian_half       kappa_F=1/(2 pi^2),
complex_determinant kappa_F=1/pi^2.
```

CBF.T42 then gave the complete normalized remainder an exact rank-four q79
normal form, but it did so by reconstructing a normal block from the already
known remainder.  It was therefore a right inverse, not the required source
calculation.

This theorem closes both gaps at the direct local one-loop tier.  It starts
from the actual CBF.T25 product Dirac family, applies the physical Weyl
polarization already fixed in CBF.T23/CBF.T30, performs the standard local
four-dimensional Grassmann pushforward, and derives the anchored remainder.
The normalized function `rho` is not an input.

## 2. Typed carrier ledger

Let

```text
H_part = C^3_family tensor H16_SM,       dim_C H_part = 48,
H_KO6  = H_part direct_sum conjugate(H_part), dim_C H_KO6 = 96.
```

The second summand is the KO6 real completion.  It is not a second set of 48
independent physical Weyl fields.  The selected continuum matter bundle has
48 left-Weyl internal states and the left-Weyl spin representation has complex
dimension two.  Thus

```text
48 internal Weyl labels x 2 spin components = 96 off-shell components.
```

This `96` must not be multiplied by the KO6 completion `96`, and the q79
projector ranks must not be interpreted as particle multiplicities.

At the selected finite coordinate

```text
t_*=(1-sqrt(13))/6,
```

the positive chiral block has three response factors

```text
sigma_-4=(2+sqrt(13))/3,
sigma_-2=(5+sqrt(13))/6,
sigma_+2=(7-sqrt(13))/6,
```

each with Weyl multiplicity 16.  Consequently

```text
16+16+16=48.
```

This is the physical multiplicity ledger used below.

## 3. Direct product-Dirac source

On the CBF.T25 covariantly constant neutral chart, freeze `t=t_*` and write

```text
D_dir(h)=D_Y tensor I_96 + Gamma_Y tensor h D_phys(t_*).
```

The grading anticommutation gives the exact square

```text
D_dir(h)^2=D_Y^2 tensor I_96
             +h^2 I tensor D_phys(t_*)^2.
```

After physical Weyl polarization, the mass-square eigenvalues are

```text
m_a(h)^2=h^2 sigma_a^2,
```

with multiplicity 16 for each of the three branches.  No Galerkin proxy,
rank-four determinant lift, observed mass, or fitted coefficient enters this
operator.

## 4. Weyl determinant exponent

For one complex two-component Weyl Grassmann field, the even local part of the
Euclidean one-loop functional is obtained from

```text
-log det D_W = -(1/2) Tr_spin log(D_W^* D_W) + phase.
```

The spin trace contributes `2`; the square-root exponent contributes `1/2`.
The renormalized scalar logarithmic integral in four dimensions therefore
gives

```text
V_W(m)=-m^4/(32 pi^2) [log(m^2/mu^2)-c_scheme].
```

The phase belongs to the global determinant-line problem and does not double
the even local modulus.  A four-component complex Dirac count would instead
give `-m^4/(16 pi^2)` and would count every selected left-Weyl state twice.

Since each response branch has multiplicity 16, the common coefficient is

```text
kappa_F=16/(32 pi^2)=1/(2 pi^2).
```

Hence the `complex_determinant` candidate `1/pi^2` is rejected at this typed
carrier tier.  This conclusion uses statistics from the Grassmann fields, not
KO chirality, in agreement with authority A56.

## 5. Exact finite trace

Set

```text
q4_* = sum_a sigma_a^4,
L4_* = sum_a sigma_a^4 log(sigma_a^2).
```

Arithmetic in `Q(sqrt(13))` gives

```text
q4_*=(356+25 sqrt(13))/27.
```

The direct local one-loop pushforward is therefore

```text
V_F(h)=-h^4/(2 pi^2)
       [q4_* log(h^2/mu^2)+L4_*-c_scheme q4_*].
```

This fixes the unresolved CBF.T35 normalization without using a measured
fermion mass or an observed vacuum value.

## 6. Pointed local renormalization is derived

Let `H>0` be the CBF.T34 radial anchor and put `x=h/H`.  Modulo the allowed
even local orbit

```text
P_4^even=span{1,x^2,x^4},
```

all scale, scheme, and branch-log terms are polynomial.  The only nonlocal
normalized seed is

```text
f(x)=-x^4 log(x^2).
```

Define `I_H f` to be the unique element of `P_4^even` having the same value,
first derivative, and second derivative as `f` at `x=1`.  In the ordered basis
`(1,x^2,x^4)`, the jet matrix is

```text
J = [[1,1,1],
     [0,2,4],
     [0,2,12]],       det J=16.
```

Thus the interpolation problem is uniquely solvable.  Since

```text
(f(1),f'(1),f''(1))=(0,-2,-14),
```

direct solution gives

```text
I_H f=-1/2+2x^2-(3/2)x^4.
```

The pointed quotient is therefore

```text
R_H f := f-I_H f
       =x^4(3/2-log(x^2))-2x^2+1/2
       =rho(x).
```

This is a derivation of `rho`, not a reconstruction from `rho`.  It is also
the unique representative in the local orbit whose zero-, first-, and
second-order jets vanish at the selected anchor.

## 7. Exact emitted action and vertices

The renormalized direct pushforward emits

```text
Delta V_cl(h)
  =q4_* H^4/(2 pi^2) rho(h/H)
  =(356+25 sqrt(13))H^4/(54 pi^2) rho(h/H).
```

The exact normalized jets are

```text
(rho,rho',rho'',rho''',rho'''',rho''''')(1)
  =(0,0,0,-16,-64,-48).
```

Consequently the loop vertex shifts are

```text
Delta V_cl'''(H)  =-8 q4_* H/pi^2,
Delta V_cl''''(H) =-32 q4_*/pi^2,
Delta V_cl'''''(H)=-24 q4_*/(pi^2 H).
```

The first three equalities show that the lower fixed point, tangent repair
generator, and radial Hessian are preserved.  The higher vertices are not
erased.

## 8. Same-source composition

The source-lock graph is

```text
CBF.T23 physical 48+48 KO6 finite family
  -> CBF.T25 direct causal product Dirac action
  -> CBF.T30 physical Weyl polarization, t_* and 16+16+16 spectrum
  -> CBF.T34 same-root radial anchor H
  -> direct Weyl Berezin pushforward
  -> unique pointed local quotient R_H
  -> CBF.T35/CBF.T39 remainder.
```

The T30 source lock pins T25, the T34 source lock pins T25 and T30, the T35
source lock pins T30 and T34, and the T39-T41 locks pin the subsequent pointed
projection and gate definitions.  The executable verifies every edge and
constructs a new canonical root from construction sources only.  T35, T39,
and T42 are used only for output comparison, so they cannot inject `rho` or
the determinant coefficient into the construction.

At this declared tier the Berezin contraction is an actual action
pushforward, not a scalar determinant right inverse.  Together with the
unique pointed quotient it supplies a direct/local one-loop instance of the
T41 `G0` pattern: one operator source, one field/action pushforward, and the
pointed fixed-point/tangent square.

## 9. Relation to the rank-four q79 normal form

CBF.T42 remains useful.  Its rank-four normal block and the present Weyl
pushforward emit the same normalized scalar function `rho`.  They are not the
same operator:

```text
CBF.T42: finite rank-four determinant-equivalent normal form,
CBF.T43: 48-state Weyl-polarized product-Dirac one-loop pushforward.
```

In particular, `rank(Q)=4` is not a particle count.  Equality of the two
normalized scalar outputs is a compatibility statement and a target for a
future q79/HYM universality intertwiner, not proof of operator equivalence.

## 10. Precisely closed and open statements

Closed here:

1. the T35 twofold local normalization ambiguity;
2. `kappa_F=1/(2 pi^2)` from the selected 48-state Weyl carrier;
3. the actual direct product-Dirac flat-background one-loop pushforward;
4. derivation of `rho` from the raw logarithm plus the pointed three-jet
   equations, without using `rho` as source data;
5. a same-source direct/local one-loop `G0` instance and all displayed exact
   higher radial vertices;
6. compatibility, but not identity, with the T42 rank-four normal form.

Still open:

1. a selected global Lorentzian determinant domain, Wick prescription,
   integration cycle, and determinant-line orientation;
2. a q79 HYM/Strominger Hessian or normal operator whose pushforward gives the
   same result;
3. the physical parallel line map and wave-function metric (`G1`);
4. a selected interacting QME-preserving BV/state pushforward (`G2`);
5. RG transport, pole matching, absolute scale selection, and held-out
   observable prediction;
6. the full bosonic and gravitational upper action.

Therefore `B.ACTION.01`, `B.QFT.02`, `B.OP.01`, and `B.GEO.01` remain open.
The physical packet and row counters do not move.

## 11. External mathematical context

The square-root/Pfaffian treatment of the KO6-completed fermion space and the
need to distinguish physical polarization from formal doubling are standard
issues in noncommutative-geometric Standard Model constructions; see Barrett,
`hep-th/0608221`, Connes, `hep-th/0608226`, and D'Andrea-Kurkov-Lizzi,
`arXiv:1605.03231`.  Martin, `hep-ph/0111209`, writes the general one-loop
effective potential directly in a two-component Weyl basis: after restoring
the paper's factored `1/(16 pi^2)`, one fermion eigenstate contributes exactly
`-m^4[log(m^2/Q^2)-k]/(32 pi^2)`.  These external results justify the analytic
determinant rule; they do not select the MTT source coordinate, anchor, or
global q79 geometry.

## 12. Machine certificate

The construction is emitted by

```text
python build_weyl_polarized_product_dirac_g0.py
python verify_weyl_polarized_product_dirac_g0.py
python -m unittest tests.test_weyl_polarized_product_dirac_g0 -v
```

The builder starts from the raw series `-x^4 log(x^2)`, independently solves
the jet interpolation system, verifies the `Q(sqrt(13))` trace, checks the
48-versus-96 carrier ledger and all provenance edges, and emits a
schema-checked packet.  The independent verifier recomputes these facts
without importing the builder.
