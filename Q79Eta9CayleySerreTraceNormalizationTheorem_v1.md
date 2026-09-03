# q79 eta9 Cayley-Serre trace-normalization theorem

**Identifier:** CBF.T64
**Status:** closed canonical normalization formula with an exact good-reduction witness; selected complex panel evaluation and path transport remain open
**Tier:** characteristic-zero toric-residue theorem plus exact `GF(21817)` quotient certificate

## 1. Purpose

H4-T136 constructed the six same-member Serre pairings and source lifts needed
by the q79 eta9 BHT calculation, but normalized each one by the coordinate
condition `TopTrace[1494]=1`. That condition selected a convenient chart on a
one-dimensional trace line. It did not fix the intrinsic Serre trace and could
not be propagated as physical normalization.

CBF.T64 replaces that chart choice by one geometric formula. The formula uses
the weighted Cayley ambient space of the selected degree `(6,9)` curve and the
absolute toric residue of its Jacobian. No measured constant, fitted value or
new continuous/discrete parameter enters.

The exact calculation below uses the fixed B89 member as a test member because
all of its algebraic frames are already available. CBF.T54 has independently
rejected B89 from the beta-zero locus. T64 does not reverse that result or call
B89 physical: its normalization formula is uniform over every smooth member of
the same degree `(6,9)` family and is meant to transfer to the next surviving
candidate.

## 2. Cayley ambient and critical degree

Let `P=P(1,1,1,3)` with hyperplane class `H`, and let

```text
Y = P(O_P(6H) + O_P(9H)).
```

Write the Cox variables as `(x,y,z,w,U,V)`, with bidegrees

```text
x,y,z : (1,0),    w : (3,0),
U : (-6,1),       V : (-9,1).
```

For the degree-six and degree-nine equations `f6,f9`, the Cayley polynomial

```text
Phi = U f6 + V f9
```

has class `xi=(0,1)`. The sum of the six Cox-variable degrees is
`beta0=(-9,2)`, so the Cox critical degree for five sections of class `xi` is

```text
5 xi - beta0 = (9,3).
```

The ordinary curve socle used by H4-T96 and H4-T136 has degree `(18,1)`. The
Cox product

```text
M = x y z w U V,      deg(M)=(-9,2),
```

therefore gives a graded map from `(18,1)` to `(9,3)`.

The physical representative does not yield the required rank-one critical
quotient in its initial Cox coordinates. Treating that unsaturated quotient as
the residue line is therefore invalid. Following the determinant-one
ambient-gauge method already established in the eta9 B71/B72 program, set

```text
B3 = x^3+y^3+z^3+w,
f9_regular = f9_physical+B3 f6,
U_old = U_new+B3 V.
```

The last identity gives

```text
U_old f6+V f9_physical = U_new f6+V f9_regular.
```

It is a triangular graded bundle automorphism of determinant one. It changes
neither the curve `f6=f9=0` nor any physical class. The exact quotient test
below proves that this simple symmetric gauge is torically regular at the good
reduction. It is a computational coordinate choice, not a parameter.

## 3. Toric residue normalization

Use the five degree-`xi` sections

```text
Phi, y Phi_y, z Phi_z, w Phi_w, U Phi_U.
```

The weighted Euler relations recover the omitted logarithmic derivatives, so
these sections generate the relevant logarithmic Jacobian ideal. For the ray
minor `(rho_y,rho_z,rho_w,rho_U)`, the determinant is `+1`; Cox's Jacobian
formula therefore gives

```text
J_toric = det(F_i, partial_y F_i, partial_z F_i,
              partial_w F_i, partial_U F_i)/(x V).
```

It lies in degree `(9,3)`. Cox's trace theorem fixes its residue by the top
self-intersection of `xi`:

```text
Res_Y(J_toric) = integral_Y xi^4.
```

The rational Chow ring has

```text
H^3=1/3,              (xi-6H)(xi-9H)=0.
```

Consequently

```text
integral_Y xi^4
 = (6^3 + 6^2*9 + 6*9^2 + 9^3)/3
 = 585.
```

The Cayley residue comparison first defines the top toric functional by

```text
lambda_C([P]) = Res_Y([M P]).
```

For the two complementary pieces used here, Mavlyutov's proven cup-product
formula has ambient dimension `d=4`, `a=1`, `b=2`, and therefore

```text
c_12 = (-1)^(1+3+1+3)/(1!*2!) = 1/2.
```

In the algebraic de Rham convention already used by the eta9 residue program,
the Serre/Hodge trace is consequently

```text
Tr_C([P]) = (1/2) Res_Y([M P]).
```

The later Betti period quotient remains responsible for the usual analytic
comparison conventions; no `2*pi*i` factor is promoted to a free parameter.

## 4. Exact finite certificate

At the already selected good reduction `p=21817`, split root `5`, the builder
constructs all `9361` monomials of critical degree `(9,3)` and all `16740`
Macaulay relation rows. Exact modular elimination proves

```text
rank(J_critical)=9360,
dim R_(9,3)=1.
```

The stored dual functional is replayed against every relation. Each old top
monomial is first transported through `U_old=U_new+B3 V`; multiplication by
`M` then intertwines the result with the independently stored H4-T96 top
functional on all `2584` old top monomials, with nonzero ratio. The toric Jacobian also has
nonzero quotient value. These checks prove that the Cayley multiplier is an
isomorphism between the two one-dimensional quotient lines at this good
reduction.

The fixed test member also has the existing proper-good-reduction certificate
that promotes its smoothness to characteristic zero. This supplies the
regularity hypothesis needed by the toric-residue theorem.

This modular witness establishes nonvanishing and catches all coordinate,
grading and sign errors in the finite model. It is not called the selected
complex numerical scale.

## 5. Absolute scale formula

Let `f_crit` denote any nonzero functional on the critical quotient, and let
`m_1494=w^9 V` be the H4-T136 normalization monomial. The intrinsic toric and
Serre scales of the projective trace are

```text
s_toric = 585 f_crit(M m_1494)/f_crit(J_toric),
s_C     = (585/2) f_crit(M m_1494)/f_crit(J_toric).
```

The numerator and denominator scale together if `f_crit` is rescaled, so both
quantities are independent of every auxiliary quotient basis or pivot choice.
The second scale is applied to the H4 Serre matrix. This is the missing
normalization theorem: the former free-looking scalar is one algebraic residue
evaluation fixed by the selected curve.

## 6. Transport and derivatives

If `(f_proj,S_proj,h_proj)` are the projectively normalized trace, Serre matrix
and H01 source lift, then the absolute objects are

```text
f_abs = s_C f_proj,
S_abs = s_C S_proj,
h_abs = h_proj/s_C.
```

Thus the source covector `S h` and all physical Serre pairings are unchanged.
For directed transport one must also differentiate the same scalar:

```text
f_abs' = s_C' f_proj + s_C f_proj',
S_abs' = s_C' S_proj + s_C S_proj',
h_abs' = h_proj'/s_C - (s_C'/s_C^2) h_proj.
```

Here `s_C'` is obtained by differentiating the same residue quotient. It is
not an additional input or knob. This term must be included when H4-T140's
projective midpoint derivatives are converted to the intrinsic gauge.

## 7. What closes and what remains

CBF.T64 closes the *source of normalization*: `TopTrace[1494]=1` no longer
stands between the six H4-T136 source lifts and a canonical trace. It also
provides a complete exact finite witness for the Cayley critical quotient.

It does not yet emit the six complex values `s_C(t)` and `s_C'(t)` on directed
panels. It does not execute the rank-164 Gauss-Manin ODE, integrate the 248-row
BHT accumulator, quotient by periods, evaluate `beta_C`, or decide `U_eta9`.
Those remain the next execution layer.

It also does not reinstate B89. The next physical use must begin with a
surviving same-residue candidate and reconstruct that member's framed source;
the B89 calculation remains a reproducible algebraic witness and regression
fixture.

The next nonduplicative object is therefore a multiprecision panel evaluator
for the scalar quotient and its derivative, first on edge 2 and edge 0, bound
to H4-T140's direct operator derivatives. Once those panels are certified, the
same evaluator extends to all six segments before directed ODE integration.

## 8. Reproduction

Normal verification replays the stored exact witness:

```powershell
python build_q79_eta9_cayley_serre_trace_normalization.py
python verify_q79_eta9_cayley_serre_trace_normalization.py
```

The expensive one-time rank certificate can be regenerated with:

```powershell
python build_q79_eta9_cayley_serre_trace_normalization.py --recompute-witness
```

Primary mathematical inputs are Cox's toric-residue Jacobian and trace theorem
([arXiv:alg-geom/9410017](https://arxiv.org/abs/alg-geom/9410017)),
Mavlyutov's regular-semiample residue and cup-product theorems
([arXiv:math/9812163](https://arxiv.org/abs/math/9812163)), the toric
complete-intersection residue comparison, and the existing q79
weighted-projective/K3 trace packet. The general mixed-Hessian conjecture is
not used.
