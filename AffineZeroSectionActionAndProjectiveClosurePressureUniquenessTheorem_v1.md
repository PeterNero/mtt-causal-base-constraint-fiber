# Affine Zero-Section Action and Projective Closure-Pressure Uniqueness Theorem

## Status

Claim ID: `CBF.T17`

Tier:

```text
EXACT_GENERAL
+ EXACT_SOURCE_PINNED_FINITE_ACTION_WITNESS
+ CONDITIONAL_PHYSICAL_SOURCE_COMPOSITION
```

Decision:

```text
PURE_COTANGENT_COMPLETION_CANNOT_ACTIVATE_REGULAR_RESIDUAL_CURVATURE
ONE_AFFINE_NORMAL_TADPOLE_IS_NECESSARY_AND_SUFFICIENT_AT_MINIMAL_TWO_JET_TIER
NONZERO_PRESSURE_HAS_ONE_UNORIENTED_CLASSICAL_PROJECTIVE_CLASS
PHYSICAL_ACTION_DENSITY_YUKAWA_TYPING_AND_VALUES_REMAIN_OPEN
```

This theorem continues `CBF.T16`. It constructs one exact finite action object,
but it does not close `B.ACTION.01` or `B.SM.02`. Physical packet acceptance
remains `0/3` and physical row acceptance remains `0/7`.

## 1. Result in one paragraph

Let a regular closure locus be the graph

```text
Phi(n,k)=n+psi(k)=0.
```

The canonical cotangent action `<lambda,Phi>` vanishes on its zero section and
forces `lambda=0` at a regular critical point, so it cannot turn `D2psi` into a
tangent Hessian. The minimal missing datum is a field-only affine normal action

```text
U_ell(n,k)=-ell(n).
```

Its multiplier completion has critical multiplier `lambda=ell`, and its
restriction to the closure graph is

```text
U_ell(-psi(k),k)=ell(psi(k)).
```

Thus a linear upper rule becomes a nonlinear lower action solely because the
coherent locus is curved. For the CBF.T16 quadratic graph this pullback is
exactly the FSB.04e/04f family quadratic. Every nonzero scalar pressure is
equivalent to the normalized pressure under a multiplier-coordinate change
and an overall classical action rescaling. Pressure therefore adds no new
continuous dimensionless shape parameter at this tier, although the overall
physical action normalization remains unselected.

## 2. Regular closure graph

Let `N` and `K` be finite-dimensional real inner-product spaces. Let

```text
psi:K->N,
psi(0)=0,
Dpsi(0)=0,
```

and define

```text
Phi(n,k)=n+psi(k).
```

The normal derivative is `D_n Phi=I_N`, so the closure locus is the smooth
graph

```text
i(k)=(-psi(k),k).
```

Write

```text
B=D2psi(0):Sym2(K)->N.
```

## 3. Why canonical cotangent completion is insufficient

The unshifted multiplier or cotangent action is

```text
S_cot(n,k,lambda)=<lambda,Phi(n,k)>.
```

It has two relevant properties:

```text
S_cot(n,k,0)=0,
D_n Phi=I_N.
```

The first says that the action vanishes on the zero section of the dual lane.
The second forces `lambda=0` at every critical point. Consequently its tangent
Hessian at the origin is zero, independently of `B`.

This is the finite regular-graph form of the zero-section limitation recorded
by H4-T14 and H4-T15. Canonical evaluation fixes the coefficient of the
multiplier term; it does not manufacture a field-only base action.

## 4. General constrained second variation

Let `U:N direct_sum K -> R` be a smooth field-only action and set

```text
L_U(n,k,lambda)=U(n,k)+<lambda,Phi(n,k)>.
```

Assume `(0,0,lambda_*)` is critical. The normal and tangent first variations
give

```text
lambda_*=-D_n U(0,0),
D_k U(0,0)=0.
```

Define the pressure covector

```text
ell=-D_n U(0,0).
```

### Theorem 4.1

The Hessian of `L_U` on tangent directions `u,v in K` is

```text
D2_kk U(0,0)[u,v]+ell(B(u,v)).
```

The same expression is the Hessian of the graph-restricted action `i^*U`.

### Proof

The tangent-tangent block of the multiplier term is

```text
<lambda_*,D2psi(0)[u,v]>=ell(B(u,v)).
```

Adding the intrinsic tangent Hessian of `U` gives the first formula.

For the pullback, `Di(0)u=(0,u)` and

```text
D2i(0)[u,v]=(-B(u,v),0).
```

The second-order chain rule gives

```text
D2(i^*U)(0)[u,v]
 =D2_kk U(0,0)[u,v]
  +D_n U(0,0)(-B(u,v))
 =D2_kk U(0,0)[u,v]+ell(B(u,v)).
```

The two calculations agree. QED.

## 5. Minimal affine normal action

Fix a covector `ell in N^*` and define

```text
U_ell(n,k)=-ell(n),
L_ell=-ell(n)+<lambda,n+psi(k)>.
```

### Theorem 5.1

The point

```text
(n,k,lambda)=(0,0,ell)
```

is critical. Its tangent Hessian is

```text
H_ell(u,v)=ell(B(u,v)).
```

The exact lower action obtained by restricting to the closure graph is

```text
S_lower(k)=ell(psi(k)).
```

Among affine field-only actions that vanish at the origin, have a critical
tangent at the origin and use the selected normal covector `ell`, `U_ell` is
unique. At the two-jet level it is the unique minimal completion with zero
intrinsic tangent Hessian.

### Proof

The critical equations are

```text
Phi=0,
-ell+lambda=0,
Dpsi(0)^*lambda=0.
```

They hold at the displayed point. Theorem 4.1 applies with
`D2_kk U_ell=0`. The graph identity follows directly:

```text
U_ell(-psi(k),k)=ell(psi(k)).
```

An affine scalar function has only a constant and a linear covector. Vanishing
at the origin removes the constant; tangent criticality removes the `K`
covector; the declared normal gradient fixes the remaining term to `-ell`.
QED.

### Necessity boundary

This is a uniqueness theorem inside the affine normal class, not among all
possible physical actions. A different action can carry an independent
intrinsic tangent Hessian. Such a term is new source data and cannot be counted
as pressure-generated curvature.

## 6. Nonzero pressure is projectively unique

Choose a unit normal covector `ell_0` and write `ell=p ell_0`. Then

```text
L_p(n,k,lambda)
 =-p ell_0(n)+<lambda,Phi(n,k)>.
```

For `p!=0`, set `lambda=p mu`. Exactly,

```text
L_p(n,k,p mu)=p L_1(n,k,mu).
```

### Theorem 6.1

All nonzero pressure magnitudes belong to one unoriented classical projective
source class. The zero-pressure branch is separate because its family
curvature Hessian vanishes.

Multiplying an action by a nonzero scalar does not change its classical
Euler-Lagrange zero set. Therefore `|p|` is not an additional dimensionless
classical shape parameter. If only positive action rescalings are admitted,
the signs of `p` remain two oriented branches. In a quantum phase
`exp(iS/hbar)`, the overall action scale is physical relative to `hbar`; this
theorem does not select it.

## 7. Relation to curved and cotangent source language

The source data now split cleanly:

```text
Phi and its product/jet B:  closure graph and interactions,
ell:                        field-only normal tadpole,
<lambda,Phi>:               canonical cotangent enforcement.
```

The H4 common-curvature theorem shows why a normal curvature covector can have
a Jordan stability shadow while its Lie shadow controls orientation. H4-T14
supplies the canonical evaluation coefficient of the cotangent term. Neither
theorem alone supplies `U_ell`; the present theorem identifies that missing
zero-section datum exactly.

Calling `ell` a curved `m0`, vacuum load, order field, pressure or antifield
background requires the corresponding grading, pairing and source theorem.
The finite theorem only calls it a selected normal covector.

## 8. Exact finite family action

Use the CBF.T16 spaces

```text
N=H16,
K=C3_family tensor H16,
H16=Q6 direct_sum u3 direct_sum d3 direct_sum L2 direct_sum e1 direct_sum N1.
```

Let `n0` be the normalized neutral `N1=N^c` vector. It is a gauge singlet and
has shared-circle weight zero. Let

```text
H_resp=B_phase tensor R_phase+A_shift tensor R_shift
```

be the exact FSB.04e/04f routed family response of CBF.T16. Define

```text
q(k)=Re<k,H_resp k>,
psi(k)=1/2 n0 q(k),
ell(n)=Re<n0,n>.
```

The single finite action object is

```text
S_fin(n,k,lambda)
 =-Re<n0,n>
  +Re<lambda,n+1/2 n0 Re<k,H_resp k>>.
```

Its critical point is `(0,0,n0)`. Restriction to the closure graph gives

```text
S_lower(k)=1/2 Re<k,H_resp k>.
```

Therefore its real tangent Hessian is the realification of `H_resp`. No new
postprojection matrix or coefficient has been added.

## 9. Exact ranks, inertia and symmetry

In complex notation,

```text
rank(H_resp)=24,
ker(H_resp)=24.
```

The pressured bordered operator has complex-formal dimension 80, rank 56 and
kernel dimension 24. On the actual real action carrier:

```text
tangent dimension:              96,
tangent Hessian rank:           48,
tangent Hessian kernel:         48,
bordered dimension:            160,
bordered Hessian rank:         112,
bordered Hessian kernel:        48.
```

For normalized positive pressure, the real bordered inertia is

```text
positive: 48,
negative: 64,
zero:     48.
```

This is a signed variational action, not a positive repair cost.

The action preserves A47 gauge and the A50 shared circle. Its common family
stabilizer is scalar `U(1)`, and it inherits the exact finite CP-sensitive
orientation. Its nonzero singular magnitudes remain only `4` and `2`; it does
not produce three positive family magnitudes.

## 10. What is genuinely unified

Before this theorem the linear source, nonlinear response curvature and normal
load were displayed as separate ingredients. The finite witness now packages
them into one executable action polynomial. In that precise algebraic sense,
one object emits:

```text
J,
D2psi,
n0,
normalized nonzero pressure,
H_resp,
U(3)->U(1) family orientation.
```

This proves existence of a common finite algebraic realization. It does not
prove that the selected physical q79 endpoint emits this polynomial. The
source is assembled from separately locked CBF, A46/A47/A50 and FSB inputs.

## 11. Parameter and physical boundary

The normalized finite construction uses

```text
observed construction inputs:                  0,
fitted dimensionless coefficients:             0,
new postprojection family matrices:            0,
nonzero unoriented pressure classes:            1,
new continuous pressure-shape parameters:       0,
unselected overall physical action scale:       1,
strict charged magnitude values still open:     9.
```

The pressure result is a parameter reduction, not a physical value prediction.
The finite unit norm uses the declared algebraic pairing. A physical HYM or
four-dimensional density could rescale it and remains part of `B.ACTION.01`.

## 12. Lorentz, Higgs and Yukawa boundary

`S_lower` is a Hermitian family quadratic on the retained internal carrier. It
is not yet:

- a Lorentzian fermion bilinear;
- a left-right map between the A46 chiral representations;
- a Higgs-dependent gauge singlet;
- a causal gauge-fixed BV action;
- a positive mass operator; or
- a prediction of masses, CKM, PMNS or observed CP.

Those statements require the physical external spinor pairing, Higgs/order
field, vacuum background, density, domains and same-root endpoint map.

## 13. Frontier delta

`CBF.T17` closes five exact finite questions:

1. the canonical cotangent term alone is proved insufficient;
2. the minimal missing zero-section action is the affine normal tadpole;
3. a simple upper linear rule pulls back to the exact lower family quadratic;
4. every nonzero pressure magnitude is one classical projective class; and
5. one exact finite action polynomial emits all CBF.T16 structural data.

It does not accept a physical row. The next theorem must select the normal
covector and physical density from the same endpoint that emits the response
product, then type the lower quadratic as a Lorentz-Higgs left-right map.

## 14. Claims and nonclaims

### Proved

- unshifted cotangent completion has no regular pressure activation;
- the general graph-restricted second-variation formula;
- affine normal tadpole necessity and sufficiency in the minimal class;
- exact graph pullback from a linear upper action to a nonlinear lower action;
- one nonzero unoriented classical projective pressure class;
- exact finite complex and realified ranks and inertia;
- gauge/shared-circle preservation and `U(3)->U(1)` symmetry reduction; and
- zero new continuous dimensionless pressure-shape parameters.

### Not proved

- selection of the finite action by one physical q79 endpoint;
- the physical density or overall action normalization;
- a cyclic/BV grading, causal domain or quantum master equation;
- Lorentz/Higgs/Yukawa typing;
- three family magnitudes or any of the nine charged scalar values; or
- closure of `B.ACTION.01` or `B.SM.02`.

## 15. Reproduction

```text
python build_affine_zero_section_action.py
python verify_affine_zero_section_action.py
python -m unittest tests.test_affine_zero_section_action -v
```

The generated packet is `affine_zero_section_action.packet.json`.
