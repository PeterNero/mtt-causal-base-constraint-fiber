# Frozen-Source Four-Dimensional Fermion Pushforward and Closure-Jet Renormalization Theorem v1

**Claim:** CBF.T35

**Date:** 2026-08-30

**Status:** exact finite-regulator source-freeze/pushforward theorem and exact
flat four-dimensional fixed-source one-loop radial determinant; unique
zero-through-second-jet subtraction conditional on a closure-jet matching
rule; no selected external BV regulator, global Wick class, RG fixed point,
determinant orientation or physical pole mass.

## 1. Result

CBF.T31 proved that the four-dimensional fermion determinant cannot select a
scheme-independent value of `t` when `t` is varied as a field or coupling
coordinate. CBF.T33 then identified the typing error: the CBF.T30 coordinate

```text
t_*=(1-sqrt(13))/6
```

is upstream source data on the preprojection lane, so it is frozen before the
downstream fields are varied. CBF.T34 connected that source to the product
heat profile and selected the cutoff-unit radial point

```text
H/Lambda=1.32110162937546849372....
```

CBF.T35 proves what happens when the frozen source is carried through a
regulated fermionic pushforward.

First, evaluation at a fixed source commutes with every finite Grassmann
Gaussian integral and every finite Gaussian/BV Schur-complement pushforward.
The pushforward therefore cannot create an equation of motion for `t`. At one
matching scale, `t_*` survives exactly as a source label. This statement does
not prove that `t_*` is an RG fixed point.

Second, on the same conditional flat Euclidean chart used by CBF.T31, the full
constant-radial one-loop fermion determinant at fixed `t_*` is

```text
V_F(h)=-kappa_F h^4[
          q4_* log(h^2/mu^2)+L4_*-c_scheme q4_*
        ],                                               (1.1)
```

where

```text
q4_*=(356+25sqrt(13))/27,
L4_*=sum_a sigma_a^4 log(sigma_a^2).                    (1.2)
```

The positive coefficient `kappa_F` contains the physical determinant exponent
and the standard loop factor. The current source fixes the branch
multiplicity but not the determinant-line/Pfaffian normalization needed for a
physical four-dimensional effective action.

Third, in the gauge-even radial power-counting class, the complete local
counterterm is

```text
delta V=delta Omega+delta m2 h^2+delta lambda h^4.       (1.3)
```

If the renormalized lower action is required to preserve the selected closure
germ through order two at `h=H`, namely

```text
Delta V(H)=Delta V'(H)=Delta V''(H)=0,                  (1.4)
```

then (1.3) is fixed uniquely. The resulting one-loop remainder is independent
of `mu`, `c_scheme` and `L4_*`:

```text
Delta V_cl(h)=kappa_F q4_*[
  h^4(log(H^2/h^2)+3/2)-2H^2h^2+H^4/2
].                                                       (1.5)
```

Thus no continuous subtraction coefficient remains once the closure-jet
matching rule is imposed. The rule itself is not yet selected by the upper
MTT action, so (1.5) is a unique conditional matching scheme rather than an
accepted physical renormalized vacuum.

## 2. Source freeze and pushforward commute

Let `S` be a source space and let `E=L direct_sum H` be a finite regulated
field space. Write `i_s:L -> S x L` for inclusion at fixed source `s`. A
finite Grassmann quadratic form has the partition factor

```text
Z(s)=int dbar(psi)dpsi exp[-bar(psi) M(s) psi]=det M(s).
```

For any `s_*` where `M(s_*)` is invertible,

```text
i_s* Z=det M(s_*)
      =int dbar(psi)dpsi exp[-bar(psi) M(s_*) psi].      (2.1)
```

This follows because evaluation is an algebra homomorphism and the determinant
is a polynomial in the matrix entries. The same argument applies to a
Pfaffian after an orientation is fixed on one invertible component.

For an ordinary Gaussian block Hessian

```text
Q(s)=[A(s) B(s); B(s)^* C(s)],
```

integrating the high block gives

```text
Q_eff(s)=A(s)-B(s)C(s)^(-1)B(s)^*.                     (2.2)
```

Evaluation at `s_*` commutes with addition, multiplication and inversion on
the open set where `C` is invertible, hence

```text
i_s* Q_eff
=A(s_*)-B(s_*)C(s_*)^(-1)B(s_*)^*.                    (2.3)
```

Finite-dimensional BV pushforward is fiber integration over a fixed
Lagrangian. Pullback by a parameter point commutes with that finite integral
under the same fixed-domain and convergence hypotheses. The q79 regulator
criterion already proves the finite Schur-complement and determinant
identities, while explicitly refusing to call its internal finite witness a
physical spacetime regulator.

Equations (2.1)-(2.3) close the finite-regulator base-change law. They do not
select the missing external compact-resolvent BV operator, its domain,
integration cycle or determinant orientation.

## 3. What survival of `t_*` means

The lower effective action at one matching scale is

```text
Gamma_*(phi)=Gamma(t_*,phi).
```

Its variational differential is `d_phi Gamma_*`; there is no `d_t Gamma=0`
equation. A loop correction may change coefficients in `Gamma_*`, but it does
not convert the excluded source direction into a lower field direction.

This settles the CBF.T30 external-mode warning in the correctly typed lane.
Different external modes do prefer different `t` values only in the enlarged
theory that varies `t`. They do not dislodge an upstream frozen source.

There is a separate RG question. A renormalization transport can act on the
source space by

```text
R_(mu2,mu1):S -> S.
```

Then the source at another scale is `R_(mu2,mu1)(t_*)`. Proving literal
scale-independence requires

```text
beta_t(t_*)=0,                                         (3.1)
```

or an equivalent naturality theorem. Neither base change nor source freeze
proves (3.1). No RG-invariance claim is made here.

## 4. Fixed-source four-dimensional determinant

At `t_*`, the three positive finite singular-value factors are

```text
sigma_-4=(2+sqrt(13))/3,
sigma_-2=(5+sqrt(13))/6,
sigma_+2=(7-sqrt(13))/6.                               (4.1)
```

For a constant radial field, `m_a=h sigma_a`. The flat Euclidean
dimensionally regulated fermion determinant therefore has the form (1.1).
All branch dependence is contained in the two fixed quantities

```text
q4_*=sum_a sigma_a^4=(356+25sqrt(13))/27,
L4_*=sum_a sigma_a^4 log(sigma_a^2).                   (4.2)
```

Numerically,

```text
q4_*=16.52365858839258267881...,
L4_*=18.17606601754406236109....                       (4.3)
```

No observed mass or fitted coefficient enters (4.1)-(4.3). The assumptions
of flat Euclidean external spectrum, constant `h` and a local one-loop
renormalization prescription remain exactly the assumptions already declared
by CBF.T31.

## 5. Complete radial counterterm orbit

At fixed source, gauge invariance and four-dimensional power counting permit
the even radial counterterm (1.3). An additive constant affects only the
vacuum-energy convention. The `h^2` and `h^4` terms control the radial first
and second jets.

Set

```text
L_H=q4_* log(H^2/mu^2)+L4_*-c_scheme q4_*.
```

Solving (1.4) gives

```text
delta Omega = (1/2) kappa_F q4_* H^4,
delta m2    = -2 kappa_F q4_* H^2,
delta lambda= kappa_F[L_H+(3/2)q4_*].                  (5.1)
```

The coefficient matrix for `(delta Omega,delta m2,delta lambda)` has
determinant

```text
16 H^3>0.                                              (5.2)
```

Thus the subtraction is unique for `H>0`. Substitution of (5.1) into (1.1)
cancels `mu`, `c_scheme` and `L4_*` exactly and gives (1.5).

Condition (1.4) is stronger than choosing MSbar. It is a closure-germ
matching prescription: the projected quantum action is required to represent
the same selected value, stationary equation and repair Hessian at the
matching point. MTT has strong structural motivation for such compatible
projection, but the current upper action does not yet prove that physical
renormalization must obey this exact three-condition rule. Therefore the
uniqueness theorem is conditional on (1.4).

## 6. Higher radial vertices

Write `x=h/H`. Then

```text
Delta V_cl/(kappa_F q4_* H^4)
=rho(x)
=x^4(3/2-log x^2)-2x^2+1/2.                           (6.1)
```

Exact differentiation gives

```text
rho(1)=rho'(1)=rho''(1)=0,
rho'''(1)=-16,
rho''''(1)=-64.                                       (6.2)
```

Consequently closure-jet matching preserves the T34 radial point and
curvature at one loop but predicts nonzero higher-vertex shifts:

```text
Delta V_cl'''(H) =-16 kappa_F q4_* H,
Delta V_cl''''(H)=-64 kappa_F q4_*.                    (6.3)
```

These are exact at the conditional flat one-loop tier. They are not yet
observable Higgs self-couplings because wave-function normalization, gauge
and bosonic loops, determinant orientation, RG transport and pole matching
are absent.

## 7. Numerical execution

Using the T34 value

```text
H^2/Lambda^2=1.74530951513851771854...,
```

the counterterms per unit `kappa_F` in MSbar at `mu=Lambda` are

```text
delta Omega/(kappa_F Lambda^4) = 25.16640203076220311...,
delta m2/(kappa_F Lambda^2)    =-57.67779711844372519...,
delta lambda/kappa_F           = 27.37861879664075521.... (7.1)
```

The higher-vertex shifts are

```text
Delta V'''/(kappa_F Lambda)=-349.2709165499103147...,
Delta V''''/kappa_F        =-1057.5141496571252914....    (7.2)
```

The branch multiplicity in CBF.T30 gives two currently unselected determinant
normalizations:

```text
complex determinant: kappa_F=1/pi^2,
Pfaffian half power:  kappa_F=1/(2pi^2).                (7.3)
```

Equation (7.3) is a determinant-line convention boundary, not two physical
predictions. Selecting the physical integration cycle and orientation is part
of the open external BV package.

## 8. Exact scientific boundary

Closed here:

- source evaluation commutes with every finite regulated Grassmann Gaussian;
- source evaluation commutes with finite Gaussian/BV Schur-complement
  pushforward;
- no lower `t` equation of motion is generated at one matching scale;
- the complete fixed-`t_*` flat four-dimensional one-loop radial determinant;
- the exact even radial counterterm orbit;
- uniqueness of the value/slope/Hessian-preserving subtraction;
- the scheme-independent universal remainder after that subtraction; and
- exact one-loop third- and fourth-radial-vertex shifts per determinant
  normalization.

Still open:

- upper-MTT selection of the closure-jet matching rule itself;
- a selected external q79 BV Laplacian, compact-resolvent domain, integration
  cycle and determinant-line orientation;
- global Wick rotation or a direct Lorentzian determinant;
- proof that `beta_t(t_*)=0` or any complete source RG transport;
- bosonic, gauge and gravitational loops and QME/Ward identities;
- absolute `Lambda`, sector/generation assignment, pole transport and a
  held-out observable; and
- the full exits of `B.ACTION.01`, `B.QFT.02` and `B.SM.02`.

The T34 cutoff-unit values survive this conditional one-loop matching scheme,
but they are not promoted to accepted particle masses. Physical acceptance
therefore remains

```text
packets: 0/3,
rows:    0/7.
```

## 9. External mathematical context

The flat one-loop determinant uses the standard effective-potential formula
already cited by CBF.T31. The distinction between finite spectral witnesses
and a physical external regulator follows the q79 finite-BV regulator
criterion. One-loop counterterms remaining in the spectral-action class are
consistent with the perturbative spectral-action analysis of van Nuland and
van Suijlekom, but that result does not select the MTT matching conditions or
the q79 physical domain.

## 10. Reproduction

```powershell
python build_frozen_source_four_dimensional_fermion_pushforward.py
python verify_frozen_source_four_dimensional_fermion_pushforward.py
python -m unittest tests.test_frozen_source_four_dimensional_fermion_pushforward -v
python verify.py
```

The generated packet is
`frozen_source_four_dimensional_fermion_pushforward.packet.json`.
