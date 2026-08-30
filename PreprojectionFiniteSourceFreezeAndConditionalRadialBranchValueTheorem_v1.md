# Preprojection Finite Source Freeze and Conditional Radial Branch Value Theorem v1

**Claim:** CBF.T33

**Date:** 2026-08-30

**Status:** exact source-versus-field variational typing and exact nonzero
fixed-source branch values under two declared normalization branches; the
preprojection interpretation, A53 measure and particle map remain conditional.

## 1. The apparent conflict after CBF.T32

CBF.T30 selects the nonzero finite internal coordinate

```text
t_*=(1-sqrt(13))/6.                                    (1.1)
```

CBF.T32 proves that if `t(x)` is instead promoted to a spacetime scalar and
varied jointly with the Higgs radius in the bare standard spectral action, the
unique tree vacuum is `t=0`.

These statements concern different variational problems. They conflict only
if one silently asks `t` to play both roles at once:

1. an upstream source coordinate already selected before projection; and
2. a downstream field varied again after projection.

CBF.T33 makes this typing distinction exact and evaluates the upstream-source
branch. It does not claim that MTT has already proved that CBF.T30 is the
physical preprojection selector.

## 2. Source freeze is not field variation

Let `S` be a source space, `F` a field space and

```text
L:S x F -> R                                             (2.1)
```

an action family. If an upstream law selects `s_* in S`, the lower action is
the pullback

```text
L_* = i_*^* L,     i_*:F -> S x F,     x |-> (s_*,x).   (2.2)
```

Its variational differential is

```text
d L_* = i_*^*(d_F L).                                   (2.3)
```

There is no equation `d_S L=0`, because `S` is not in the lower configuration
space. Requiring both `d_F L=0` and `d_S L=0` defines the different enlarged
theory in which the source has been promoted to a field.

The distinction is strict. For

```text
L(s,x)=(x-s)^2+s,                                       (2.4)
```

freezing `s=1` gives the critical point `x=1`, while
`partial_s L(1,1)=1`. Thus a valid frozen-source solution need not be a joint
critical point.

This is the no-double-variation rule: source selection and downstream field
variation compose, but they are not two copies of the same extremization.

## 3. Why the frozen-source lane is admissible but not selected

The current evidence supports the following conditional lane:

- CBF.T30 supplies an exact finite internal Grassmann-Gaussian selector and
  the coordinate (1.1);
- CBF.T25 supplies a causal continuum family `D_dir(t;A,H)` that accepts any
  fixed `t` as source data;
- A51 selects one Higgs doublet and does not make `t` another inner
  fluctuation; and
- CBF.T32 supplies the standard heat-kernel potential for the family.

Consequently it is type-consistent to freeze (1.1) and vary the actual Higgs
field. What remains unproved is the physical commuting square saying that the
T30 finite selector is the same upstream source used by the final continuum
action. A53 is also not yet source-locked to T30. The calculation below is
therefore an exact conditional composition, not an accepted endpoint packet.

## 4. Exact source data at `t_*`

Let

```text
q2(t)=3-4t+6t^2,
q4(t)=3-8t+36t^2-32t^3+18t^4.                          (4.1)
```

At (1.1), exact arithmetic in `Q(sqrt(13))` gives

```text
q2_*=(14+sqrt(13))/3,
q4_*=(356+25sqrt(13))/27,                              (4.2)

R_* := 2q2_*/q4_*
     =(3106+4sqrt(13))/4393.                           (4.3)
```

The three positive finite branch factors are

```text
sigma_-4=(2+sqrt(13))/3,
sigma_-2=(5+sqrt(13))/6,
sigma_+2=(7-sqrt(13))/6.                               (4.4)
```

Their exact ratios are

```text
sigma_-4/sigma_-2=(sqrt(13)-1)/2,
sigma_-2/sigma_+2=(4+sqrt(13))/3,
sigma_-4/sigma_+2=(3+sqrt(13))/2.                      (4.5)
```

Equations (4.4)-(4.5) reproduce CBF.T30; they are not refitted here.

## 5. The fixed-source radial action

Freeze `t=t_*` in the CBF.T32 tree potential:

```text
P_*(h)=q4_* h^4-4c q2_* h^2,
c=f2 Lambda^2/f0>0.                                    (5.1)
```

Only `h` is varied. The positive broken minimum is

```text
h_*^2=R_* c
     =R_* (f2/f0)Lambda^2.                             (5.2)
```

The finite Dirac branch values are then

```text
m_a/Lambda=(h_*/Lambda)sigma_a.                        (5.3)
```

The canonically generalized radial curvature obeys

```text
m_h^2=8c,
m_h^2/Lambda^2=8f2/f0.                                 (5.4)
```

The cancellation of `q2_*` and `q4_*` in (5.4) is exact. It is a tree
curvature value, not yet a renormalized Higgs pole mass.

## 6. T23 metrology branch

CBF.T23 adopts, at its one-universal-metrology tier,

```text
h=Lambda=E0=1/L0.                                      (6.1)
```

On that branch, (5.3) reduces to the existing T30 values:

```text
m_-4/Lambda=1.868517091821329764...,
m_-2/Lambda=1.434258545910664882...,
m_+2/Lambda=0.565741454089335118....                   (6.2)
```

This branch does not by itself claim radial stationarity. If (6.1) is also
required to solve (5.2), the moments must obey

```text
f2/f0=q4_*/(2q2_*)
     =1553/1098-sqrt(13)/549
     =1.4078223109736539357....                         (6.3)
```

Equation (6.3) is a derived compatibility requirement, not a selected moment
value.

## 7. Conditional A53 radial-stationary branch

A53 gives

```text
tau_int=log(448)/15                                    (7.1)
```

and, only under its zero-new-scale/minimal one-atom premise,

```text
f2/f0=1/tau_int=15/log(448).                            (7.2)
```

Substitution into (5.2) yields

```text
h_*/Lambda
 =sqrt[15(3106+4sqrt(13))/(4393 log(448))]
 =1.32110162937546849372....                            (7.3)
```

The three exact conditional nonzero branch values are

```text
m_-4/Lambda=2.46850097452107062662...,
m_-2/Lambda=1.89480130194826956017...,
m_+2/Lambda=0.74740195680266742727....                  (7.4)
```

Their algebraic-logarithmic definition is (5.3), with (4.4) and (7.3). Their
relative ratios remain exactly (4.5); A53 supplies one common normalization,
not additional family shape.

The radial curvature ratio is

```text
m_h/Lambda=sqrt(120/log(448))
          =4.43358606544780223278....                   (7.5)
```

No observed target value or fitted coefficient enters (7.3)-(7.5).

## 8. Exact branch incompatibility

The A53 value (7.2) is approximately `2.45708567497`, whereas radial
stationarity with `h=Lambda` requires (6.3), approximately
`1.40782231097`. Their certified intervals are disjoint. Therefore the
following cannot all be adopted on the frozen T30 source:

1. literal T23 `h=Lambda`;
2. A53's one-atom moment ratio; and
3. bare radial tree stationarity.

This is the fixed-source analogue of the CBF.T32 compatibility cutset. The
two numerical rows (6.2) and (7.4) are alternative conditional branches, not
two simultaneous predictions.

## 9. What these values are, and are not

The new output is real: the A53 branch gives three exact, nonzero,
dimensionless eigenvalues of the fixed-source finite Dirac mass operator in
units of `Lambda`, plus one radial tree-curvature ratio. They are more than an
arbitrary fit because the only numbers are inherited exact source quantities.

They are not yet accepted Standard-Model masses because:

- the T30 selector has not been proved to be the physical preprojection source;
- the T30 and A53 source roots have not been identified by a commuting map;
- A53's point-support premise is conditional;
- `Lambda` has no selected SI value;
- no sector/generation assignment maps the three universal branches to the
  nine charged Yukawa values; and
- loop, RG, threshold and pole-mass transport are absent.

In particular, a common normalization does not create further hierarchy. The
three ratios (4.5) remain modest and cannot by themselves replace the full
sector-resolved flavor source required by `B.SM.02`.

## 10. Exact boundary

Closed here:

- the general no-double-variation theorem;
- exact evaluation of `q2_*`, `q4_*` and the radial ratio in `Q(sqrt(13))`;
- the fixed-source radial minimum formula;
- the T23 metrology values and its radial-stationarity moment requirement;
- the conditional A53 `h/Lambda`, three branch values and radial curvature;
- exact rational-interval certificates for every displayed decimal; and
- the incompatibility of the two normalization branches under bare radial
  stationarity.

Still open:

- physical promotion of T30 as the preprojection source selector;
- a same-root T30/A53 theorem;
- selection of one normalization/action branch;
- the absolute scale and particle-sector map;
- loop/RG/threshold/pole transport and a held-out observable;
- `B.ACTION.01`, `B.QFT.02` and `B.SM.02`; and
- all q79 physical endpoint acceptance.

The counters remain

```text
physical packets: 0/3,
physical rows:    0/7.
```

## 11. Reproduction

```powershell
python build_preprojection_finite_source_freeze_radial_values.py
python verify_preprojection_finite_source_freeze_radial_values.py
python -m unittest tests.test_preprojection_finite_source_freeze_radial_values -v
python verify.py
```

The generated packet is
`preprojection_finite_source_freeze_radial_values.packet.json`.
