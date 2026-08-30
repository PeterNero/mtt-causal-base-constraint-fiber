# Four-Dimensional Fermion Determinant Scheme Classification and Physical-Value Boundary Theorem v1

**Claim:** CBF.T31

**Date:** 2026-08-30

**Status:** exact flat four-dimensional one-loop shape and renormalization-
orbit classification; one conventional MSbar same-scale candidate executed
with certified stationary intervals; no selected physical vacuum, mass or
accepted q79 endpoint row.

## 1. Result

CBF.T30 closed the finite chiral determinant and selected one source
coordinate in the neutral invertible component from the zero-external-mode
Grassmann Gaussian. It also proved that this coordinate is not stationary for
every external mode. CBF.T31 performs the next calculation instead of treating
that warning as a footnote.

Let

```text
r_-4(t)=1-2t,
r_-2(t)=1-t,
r_+2(t)=1+t.
```

Each branch has chiral multiplicity 16. On a flat Euclidean four-dimensional
background with constant `h`, dimensional regularization gives, up to one
common positive multiplicity and loop factor, the normalized fermionic shape

```text
V_ell(t)=-(1/3) sum_a r_a(t)^4 [log r_a(t)^2+ell],       (1.1)
ell=log(h^2/mu^2)-c_scheme.                              (1.2)
```

For MSbar fermions, `c_scheme=3/2`. Equation (1.1) is the exact shape induced
by the CBF.T30 branches once this external background and subtraction
convention are supplied. Neither is selected by the finite determinant alone.

The derivative is

```text
V_ell'(t)=-(4/3)[A(t)+(ell+1/2)B(t)],                    (1.3)
A(t)=sum_a r_a^3 r_a' log r_a^2,
B(t)=sum_a r_a^3 r_a'
    =-2+18t-24t^2+18t^3.                                (1.4)
```

Changing the subtraction scale changes `ell` and therefore changes the
stationary coordinate. More generally, an allowed finite local source
potential adds a polynomial through degree four. Without an upper action or
normalization conditions, its four nonconstant coefficients can set the
slope and curvature at an arbitrary regular point. Consequently there is no
scheme-independent four-dimensional stationary source coordinate in the
current data.

For a transparent candidate only, adopt

```text
MSbar, mu=h, hence ell=-3/2.                             (1.5)
```

There are exactly two stationary points in `(-1,1/2)`:

```text
t_MS,max in [-0.344776761,-0.344776760],
t_MS,min in [ 0.281284282, 0.281284283].                 (1.6)
```

The first is a local maximum and the second is a local minimum. The local
minimum emits the candidate factors

```text
r_-4=0.4374314344115137...,
r_-2=0.7187157172057568...,
r_+2=1.2812842827942432....                              (1.7)
```

This is a reproducible conventional-scheme candidate, not an MTT-selected
vacuum. In fact the profile has no global minimum in the open neutral chamber:
its lowest limiting value occurs at the singular wall `t -> -1`. Four-
dimensional momentum integration softens `r^4 log r^2` to zero at a massless
branch, so the T30 determinant wall no longer gives an infinite barrier.

## 2. Derivation of the four-dimensional shape

For a constant branch mass `m_a=h r_a(t)`, the Euclidean momentum integral of
the fermionic determinant has the standard renormalized form

```text
-m_a^4 [log(m_a^2/mu^2)-c_scheme]
```

times a common loop and multiplicity coefficient. The common coefficient does
not alter stationary coordinates, so division by three gives (1.1). In MSbar
the conventional fermion constant is `3/2`; see the general effective-
potential treatment of
[Martin](https://arxiv.org/abs/hep-ph/0111209).

This formula requires a positive Euclidean spectral chart. CBF.T25 supplies a
Lorentzian Green-hyperbolic Dirac-Yukawa operator, not a preferred global Wick
rotation. The QM source audit proves that a unit Cauchy normal determines a
positive auxiliary metric, but the normal/Euclideanization class itself is
not selected. Analytic Wick rotation similarly requires analytic Cauchy data;
see [Gerard and Wrochna](https://arxiv.org/abs/1706.08942). The almost-
commutative Wick and fermion-projection order also matters; see
[D'Andrea, Kurkov and Lizzi](https://arxiv.org/abs/1605.03231).

Thus (1.1) is an exact conditional flat-background pushforward, not a theorem
that every admitted Lorentzian CBF background has this determinant.

## 3. Scale and scheme orbit

Write `a=(-2,-1,1)` so `r_a'=a`. Differentiating (1.1) yields (1.3). At every
point with `B(t_0) != 0`, one can force stationarity by choosing

```text
ell(t_0)=-1/2-A(t_0)/B(t_0).                            (3.1)
```

The cubic `B` is strictly increasing after its derivative discriminant is
checked and has one real zero in the neutral chamber. At that exceptional
point, `A` is nonzero, so a scale change alone cannot make it stationary.
This exceptional point does not restore selection: a finite local linear
counterterm can still do so.

The scale orbit is visible directly because changing `ell` adds

```text
-(delta ell/3) Q4(t),
Q4(t)=sum_a r_a(t)^4
     =3-8t+36t^2-32t^3+18t^4.                          (3.2)
```

The general local potential ambiguity on this one-dimensional source chart is

```text
C4(t)=c0+c1 t+c2 t^2+c3 t^3+c4 t^4.                   (3.3)
```

The constant `c0` does not affect stationarity. Given any regular `t_0`, `c1`
can cancel the existing slope and `c2` can independently set the curvature.
Therefore neither a stationary point nor its stability is invariant under
the unresolved finite local counterterm orbit. This agrees with the general
renormalization-prescription freedom described by
[Hollands and Wald](https://arxiv.org/abs/gr-qc/0209029).

## 4. The MSbar same-scale candidate

Under (1.5), define

```text
g(t)=sum_a r_a^3 r_a' [log r_a^2-1].                   (4.1)
```

Then `V'(t)=-(4/3)g(t)`. Rational interval evaluation of logarithms, using
the positive atanh series with a certified geometric remainder, proves that
`g` has exactly two roots in the neutral chamber. The narrow intervals are
given in (1.6). Their second-derivative signs are certified by

```text
g'(t)=sum_a (r_a')^2 r_a^2[3 log r_a^2-1].             (4.2)
```

On the first root interval `g'>0`, so `V''<0`. On the second `g'<0`, so
`V''>0`.

At the local minimum,

```text
t_MS,min=0.2812842827942431677...,
V_-3/2(t_MS,min)=1.132876443911305657...,
V_-3/2''(t_MS,min)=7.070530392842679766....              (4.3)
```

The candidate branch ratios are

```text
r_+2/r_-2=1.7827414262980865...,
r_-2/r_-4=1.6430362810406189...,
r_+2/r_-4=2.9291088431218568....                         (4.4)
```

No observed mass or coupling entered these numbers. However, the convention
`mu=h`, the MSbar finite constant, flat Euclidean spectral density and
fermion-only truncation did enter. They are calculation choices, not hidden
fits, and they are not currently selected MTT source data.

## 5. No global chamber vacuum

The finite T30 profile behaves as `-log|r|` and diverges at a zero-mode wall.
The four-dimensional integrand instead behaves as

```text
r^4 log r^2 -> 0 as r -> 0.                            (5.1)
```

For the candidate (1.5), the continuous wall limits and stationary values are

```text
V(-1)              =-18.2186335140506733...,
V(t_MS,max)        =  2.3586634429695740...,
V(t_MS,min)        =  1.1328764439113057...,
V(1/2)             =  1.2229363926582763....            (5.2)
```

The derivative sign decomposition from the two certified roots proves that
the infimum on `(-1,1/2)` is the left wall limit and is not attained. The
fermion-only MSbar same-scale profile therefore supplies a metastable local
minimum, not a selected global vacuum. A bosonic completion or a source-domain
rule is indispensable.

## 6. Diagnostic for the T30 coordinate

The finite coordinate

```text
t_*=(1-sqrt(13))/6
```

can be made stationary in the one-parameter four-dimensional scale orbit by

```text
ell_*=-1.6789685371002474353... .                       (6.1)
```

In MSbar this corresponds to

```text
mu/h=1.0936101291040973565....                          (6.2)
```

This is close to the same-scale convention but is not equal to it. Equations
(6.1)-(6.2) are a diagnostic, not a derivation: choosing the renormalization
scale to retain a previously known stationary coordinate would be target
selection unless an independent source theorem emitted that ratio.

## 7. Source-coordinate dynamicality

There is a further gate before any stationary coordinate is a physical vacuum.
CBF.T25 treats `t` as a coordinate in the finite Dirac-Yukawa family. It does
not provide a four-dimensional kinetic term, canonical normalization or field
equation for `t(x)`. Ordinary couplings are not varied to find a vacuum.

An upper MTT action could promote this source coordinate to a modulus or
closure field, but then it must emit:

- its kinetic and measure terms;
- its bosonic potential and couplings to the remaining fields;
- its allowed counterterm class and normalization conditions; and
- the map from its finite branches to physical sectors.

Without this dynamicality theorem, extremizing (1.1) is a profile diagnostic,
not an equation of motion.

## 8. Reconciliation with current authorities

**A18.** The full four-dimensional, Lorentzian and constructive-QFT
obligations remain open. CBF.T31 supplies a conditional flat one-loop shape,
not that missing existence theorem.

**A73.** The determinant-response identity is respected. Physical selection,
routing and counterterm preservation are not inferred from mathematical
same-action existence.

**A84.** Its proper-time action tier does not identify the CBF source
coordinate with the selected gauge heat-shadow density. No bosonic completion
is imported from A84 without an intertwiner.

**A85.** Its common multi-loop scheme is closed at the gauge profile tier and
strict primitive no-knob selection remains open. It does not supply a scalar
CBF potential subtraction rule, a Wick class or `mu/h`. Consequently it cannot
select (1.6) or (6.1).

**QM orbitwise measure.** The `7/7` result constructs a finite chiral Berezin
measure on each certified connected presentation orbit. Its own full-domain
contract is `0/4`; it does not provide the external momentum measure, global
Wick rotation, cross-stratum phases or finite counterterm gluing needed here.

**B.ACTION.01 and B.QFT.02.** Both remain open. The exact calculation narrows
their relevant exit: one selected upper action must provide the dynamical
source field and bosonic terms, while the QFT package must provide one
external spectral/Wick and renormalization prescription on the same source.

## 9. Exact boundary

Closed here:

- the conditional flat four-dimensional fermion one-loop shape;
- its complete one-parameter subtraction-scale orbit;
- the quartic local counterterm nonuniqueness theorem;
- the loss of the finite determinant wall after four-dimensional integration;
- exactly two stationary points for the conventional MSbar `mu=h` candidate;
- their certified intervals, stability types and dimensionless branch values;
- the absence of a global neutral-chamber minimum for that candidate; and
- the exact diagnostic scale ratio needed to retain the T30 coordinate.

Still open:

- a selected Cauchy normal/global Wick or direct Lorentzian determinant rule;
- the physical external spectral measure and full-domain chiral measure;
- a selected scalar finite-counterterm and normalization prescription;
- proof that `t` is a dynamical field rather than a coupling coordinate;
- the bosonic, gauge, Higgs and gravitational effective action on the same
  source;
- the absolute scale `h` and the sector/generation map;
- a held-out observable; and
- all physical q79 endpoint acceptance.

The counters remain

```text
physical packets: 0/3,
physical rows:    0/7.
```

## 10. Reproduction

```powershell
python build_four_dimensional_fermion_determinant_scheme_classification.py
python verify_four_dimensional_fermion_determinant_scheme_classification.py
python -m unittest tests.test_four_dimensional_fermion_determinant_scheme_classification -v
python verify.py
```

The generated packet is
`four_dimensional_fermion_determinant_scheme_classification.packet.json`.
