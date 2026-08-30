# Product-Dirac Joint Radial/Source-Modulus Heat-Kernel Action and Nonzero-Vacuum No-Go Theorem v1

**Claim:** CBF.T32

**Date:** 2026-08-30

**Status:** exact conditional two-field heat-kernel action, field metric,
tree vacuum and generalized scalar spectrum; exact no-go for a nonzero family
hierarchy from the bare standard spectral action; no physical field promotion,
absolute scale or measured mass claim.

## 1. Why this calculation is necessary

CBF.T31 proved that the four-dimensional fermion determinant by itself cannot
select a scheme-independent value of the finite source coordinate `t`. It also
identified a more basic problem: in the established finite construction, `t`
labels a Dirac-Yukawa source family. A coupling coordinate is not automatically
a spacetime field and must not be extremized as though it were one.

There is nevertheless one precise calculation that can be made. Suppose the
CBF finite family is inserted into the standard flat Euclidean product-Dirac
heat-kernel construction and suppose, as an explicit extension, that both the
neutral Higgs radius `h(x)` and source coordinate `t(x)` are allowed to vary:

```text
Phi(x)=h(x) D_phys(t(x)).                               (1.1)
```

Then the heat-kernel action determines the kinetic metric and tree potential
of this two-coordinate ansatz. CBF.T32 performs that calculation exactly. It
does **not** assert that A51 or any other MTT authority has selected `t(x)` as
an additional Higgs field. A51 selects one complex Higgs doublet; `t(x)` is a
source-modulus extension beyond that selected inner-fluctuation module.

## 2. Adopted product-triple tier

In the conventional flat Euclidean product chart, the standard asymptotic
spectral action has the form

```text
Tr f(D/Lambda)
 ~ 2 f4 Lambda^4 a0 + 2 f2 Lambda^2 a2 + f0 a4.         (2.1)
```

For a matrix-valued scalar endomorphism `Phi`, its scalar terms can be written,
in the convention used here, as

```text
S_scalar = f0/(8 pi^2) integral Tr[
             (partial Phi)^2 + Phi^4
             -4(f2 Lambda^2/f0) Phi^2
           ].                                           (2.2)
```

Only the common positive coefficient is suppressed below. Formula (2.2) is
the standard heat-kernel result, not a new MTT axiom; see
[Chamseddine and Connes](https://arxiv.org/abs/hep-th/9606001),
[Vassilevich](https://arxiv.org/abs/hep-th/0306138) and
[Iochum, Levy and Vassilevich](https://arxiv.org/abs/1201.6637).

A51 establishes that the selected finite data can enter this standard
product-triple operator-content theorem. It does not select the absolute
moments, the Wick/causal completion or the source-modulus extension (1.1).
Accordingly every result below is conditional on (1.1)-(2.2), `f0>0` and
`f2>0`.

## 3. Exact finite traces

CBF.T27 gives the three squared branches, each with multiplicity 32,

```text
r_-4(t)=1-2t,
r_-2(t)=1-t,
r_+2(t)=1+t.                                            (3.1)
```

Define

```text
q2(t)=sum_a r_a(t)^2
     =3-4t+6t^2,                                        (3.2)

q4(t)=sum_a r_a(t)^4
     =3-8t+36t^2-32t^3+18t^4.                          (3.3)
```

Exact reconstruction of the 96-dimensional matrices gives

```text
Tr D(t)^2 =32 q2(t),
Tr D(t)^4 =32 q4(t),
Tr[D(t)D1]=16 q2'(t),
Tr D1^2   =192.                                         (3.4)
```

No observed mass, coupling or fitted coefficient enters (3.1)-(3.4).

## 4. The two-field kinetic geometry

Differentiating (1.1) gives

```text
partial Phi = D(t) partial h + h D1 partial t.           (4.1)
```

Using (3.4),

```text
Tr(partial Phi)^2
 =32 [q2 (partial h)^2
      +h q2' (partial h)(partial t)
      +6h^2 (partial t)^2].                             (4.2)
```

Thus, in coordinates `(h,t)`, the reduced field metric is

```text
g(h,t) = [ q2(t)         h q2'(t)/2 ]
         [ h q2'(t)/2       6h^2     ].                 (4.3)
```

Its determinant collapses exactly:

```text
det g
 =h^2[6q2-(q2')^2/4]
 =14h^2.                                                (4.4)
```

Since `q2` has discriminant `-56` and positive leading coefficient, `g` is
positive definite for `h>0`. At `h=0`, the metric degenerates because all
values of `t` describe the same zero endomorphism `Phi=0`; this is a radial
coordinate singularity, not a propagating negative-norm mode.

Equation (4.2) closes the **conditional** kinetic term that CBF.T31 lacked.
It does not prove that MTT selects `t(x)` as a physical scalar.

## 5. Joint tree potential

Set

```text
c=f2 Lambda^2/f0 >0.                                   (5.1)
```

After removing the common factor `32 f0/(8 pi^2)`, (2.2) gives

```text
P(h,t)=h^4 q4(t)-4c h^2 q2(t).                          (5.2)
```

The radial equation is

```text
partial_h P=4h[h^2 q4(t)-2c q2(t)]=0.                  (5.3)
```

The ridge `h=0` has radial curvature `-8c q2(t)<0`. On the broken branch,

```text
h^2=2c q2/q4,
P_min(t)=-4c^2 q2(t)^2/q4(t).                          (5.4)
```

The decisive identity is

```text
3q4(t)-q2(t)^2
 =2t^2(9t^2-24t+28).                                   (5.5)
```

The last quadratic has discriminant `-432` and is strictly positive.
Therefore

```text
q2(t)^2/q4(t) <= 3,                                    (5.6)
```

with equality only at `t=0`. Equations (5.4)-(5.6) prove the unique radial
minimum for `h>=0`:

```text
t0=0,
h0^2=2c=2f2 Lambda^2/f0,
P(h0,t0)=-12c^2.                                       (5.7)
```

This is also the only broken stationary point in the neutral chamber
`-1<t<1/2`. Indeed,

```text
q2 q4'-2q4 q2'
 =8t(6t^3-11t^2-18t+14).                               (5.8)
```

The cubic is `15` at `t=-1` and `3` at `t=1/2`; its sole critical point in
that interval is a strict maximum. It is therefore positive throughout the
chamber.

**No-go.** The bare standard product spectral action on this one-coordinate
CBF family cannot generate a nonzero tree-level family hierarchy. The exact
joint minimum is the undeformed equal-magnitude point `t=0`.

## 6. Exact generalized scalar spectrum

At (5.7), the metric and potential Hessian are

```text
g0 = [ 3       -2h0   ],
     [ -2h0   6h0^2  ]                                  (6.1)

Hess(P)|0 = [ 24h0^2    -16h0^3 ],
             [ -16h0^3   48h0^4 ]
           =8h0^2 g0.                                  (6.2)
```

Because (4.2) has no conventional factor `1/2`, the linearized mass matrix is

```text
M^2=(1/2)g0^-1 Hess(P)|0=4h0^2 I2.                     (6.3)
```

Both conditional scalar curvature modes therefore obey

```text
m^2=4h0^2,
m/h0=2.                                                (6.4)
```

These are tree-level generalized curvature masses of the conditional
two-field ansatz. They are not pole masses, and the second mode is not a
physical particle unless the source-modulus promotion is independently
proved.

## 7. Exact bridge to the CBF.T26 repair action

If `h` is artificially held fixed, define

```text
rho=2c/h^2,
U_rho(t)=q4(t)-2rho q2(t).                              (7.1)
```

At `rho=1`, which is precisely the radial stationarity ratio at `t=0`,

```text
U_1(t)-U_1(0)
 =6[4t^2-(16/3)t^3+3t^4]
 =6 S_rep(t).                                          (7.2)
```

Thus the positive CBF.T26 defect-repair profile is not unrelated to the
standard spectral potential: it is exactly its fixed-radial relative profile
at the closure-point radial ratio.

Equation (7.2) also explains why fixed-`h` experiments can mislead. A chosen
`rho` can produce nonzero extrema of `U_rho`, but such an extremum is a joint
vacuum only if it also satisfies (5.3). The previously tempting A53 fixed-
radius nonzero extremum fails this test and is rejected rather than promoted.

## 8. A53 moment candidate and the T23 scale cutset

A53 supplies the exact internal value

```text
tau_int=log(448)/15.                                    (8.1)
```

Under its explicitly conditional zero-new-scale/minimal one-atom premise,

```text
f2/f0=1/tau_int=15/log(448).                            (8.2)
```

Combining (5.7) and (8.2) emits the exact conditional ratios

```text
h0^2/Lambda^2=30/log(448),
h0/Lambda=sqrt(30/log(448))
         =2.21679303272390111639...,
m/h0=2,
m/Lambda=2sqrt(30/log(448))
        =4.43358606544780223278....                     (8.3)
```

These ratios use no observed target value and no fit. They are nevertheless
not accepted physical values because A53 has not proved that the point measure
is selected and no absolute `Lambda` has been emitted.

There is also an exact compatibility cutset. CBF.T23 records the one-primitive
identification

```text
h=Lambda=E0=1/L0.                                      (8.4)
```

For (8.4) to be the stationary value (5.7), one needs

```text
f2/f0=1/2,                                              (8.5)
```

whereas A53 gives (8.2). Equivalently, simultaneous adoption would require
`tau_int=2`, contradicted by (8.1). Hence these three statements cannot all be
imposed at once:

1. the A53 one-atom moment ratio;
2. the literal T23 normalization `h=Lambda`; and
3. stationarity of the bare tree spectral action.

The exact exits are to relax one of them: retain A53 and use the ratio (8.3),
retain `h=Lambda` and require (8.5), or add a selected action term that changes
the radial equation. No choice is made here.

## 9. Scientific boundary

Closed here:

- exact 96-dimensional trace reconstruction for the two-field ansatz;
- the conditional kinetic term for both `h(x)` and `t(x)`;
- the positive field metric and exact determinant `14h^2`;
- the complete joint tree potential and radial reduction;
- the unique `t=0` tree vacuum and nonzero-hierarchy no-go;
- the exact two-mode generalized scalar curvature spectrum;
- the exact bridge to the CBF.T26 repair action; and
- the A53 conditional dimensionless ratios and T23 compatibility cutset.

Still open:

- an MTT theorem promoting `t(x)` to an admissible physical field;
- selected spectral moments or a selected alternative upper action;
- the absolute metrological scale;
- a global Wick/direct Lorentzian and renormalized BV/QME construction;
- loop and RG transport of the joint vacuum and curvature masses;
- a nonzero family hierarchy, sector/generation map and measured prediction;
- `B.ACTION.01`, `B.QFT.02` and `B.SM.02`; and
- all q79 physical endpoint acceptance.

The counters therefore remain

```text
physical packets: 0/3,
physical rows:    0/7.
```

## 10. Reproduction

```powershell
python build_product_dirac_joint_radial_source_modulus_action.py
python verify_product_dirac_joint_radial_source_modulus_action.py
python -m unittest tests.test_product_dirac_joint_radial_source_modulus_action -v
python verify.py
```

The generated packet is
`product_dirac_joint_radial_source_modulus_action.packet.json`.
