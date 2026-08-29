# KO6 Physical Polarization, Fermionic Determinant and Neutral-Chamber Value-Selection Theorem v1

**Claim:** CBF.T30

**Date:** 2026-08-30

**Status:** exact finite internal Grassmann-Gaussian profile and neutral-chamber
value selection; one nonzero algebraic coordinate and three dimensionless
branch factors closed at that tier; full four-dimensional determinant,
renormalized vacuum and Standard-Model mass identification remain open.

## 1. Result

CBF.T23 and CBF.T25 provide the selected KO6-real odd finite Dirac family and
its first-order physical fermion action. CBF.T27 computed two stationary roots
of a normalized log determinant but correctly left them unpromoted because a
scalar function of `D_phys(t)^2` was not selected by the operator and trace
alone. CBF.T29 then proved that the direct odd cubic trace cancels on the whole
KO6 family.

The missing finite datum is supplied by the already selected Grassmann
fermionic action, not by another scalar trace ansatz. Let

```text
P_chi^+=(I96+Gamma96)/2,
P_chi^-=(I96-Gamma96)/2,
B(t)=P_chi^- D_phys(t) P_chi^+ : H_chi^+ -> H_chi^-.
```

Then

```text
B(t)^*B(t)=P_chi^+ D_phys(t)^2 P_chi^+,                 (1.1)
det_(H_chi^+)(B(t)^*B(t))=Delta(t)^32,                 (1.2)
Delta(t)=(1-2t)(1-t)(1+t).                            (1.3)
```

The normalized finite Grassmann-Gaussian effective profile is therefore

```text
W_0(t)=-(1/48) log det(B(t)^*B(t))
      =-(2/3) log|Delta(t)|.                           (1.4)
```

An alternative Majorana/Pfaffian convention only multiplies (1.4) by a
positive constant, so it has the same stationary coordinate.

The invertible component containing the selected neutral closure point `t=0`
is

```text
C_0=(-1,1/2).                                          (1.5)
```

On `C_0`, (1.4) has one and only one stationary point,

```text
t_*=(1-sqrt(13))/6
   =-0.4342585459106649... .                           (1.6)
```

It is the strict global minimum of `W_0` in that component. This is the first
nonzero source-selected coordinate emitted by the CBF chain without an
observed target or fitted coefficient, at the explicitly declared finite
internal Grassmann-Gaussian tier.

At `t_*`, the three positive singular-value branch factors are

```text
sigma_-4=(2+sqrt(13))/3,
sigma_-2=(5+sqrt(13))/6,
sigma_+2=(7-sqrt(13))/6.                               (1.7)
```

They are exact dimensionless finite values. They are not yet Standard-Model
masses: the overall scale, sector assignment, external spectrum and
renormalized action are not selected here.

## 2. KO6 polarization is not statistics grading

The internal grading obeys

```text
Gamma96^2=I96,
Gamma96 D_phys(t) Gamma96=-D_phys(t),
dim H_chi^+=dim H_chi^-=48.
```

It therefore selects the two chiral blocks of the odd operator. It does not
provide the fermionic sign in an effective action. That sign comes from the
Grassmann integration of the CBF.T25 fermion fields. This distinction is
required by A56: KO chirality cannot be relabelled as boson/fermion statistics
or used as a threshold supertrace.

For the product geometry, the physical field restriction is stated at the
full spinor-times-finite level. Equation (1.1) concerns the exact finite factor
of that restriction. KO-dimension six and the associated resolution of the
finite fermion doubling problem are standard in the Lorentzian
almost-commutative construction; see
[Barrett](https://arxiv.org/abs/hep-th/0608221),
[Connes](https://arxiv.org/abs/hep-th/0608226), and the invariant-subspace
analysis of [Besnard](https://arxiv.org/abs/1903.04769). These references do
not select the MTT source coordinate or its value.

## 3. Exact chiral determinant

Because `D_phys(t)` is odd,

```text
D P_chi^+=P_chi^- D,
D P_chi^-=P_chi^+ D.
```

Consequently

```text
B^*B
 =P_chi^+ D P_chi^- D P_chi^+
 =P_chi^+ D^2 P_chi^+,
```

which proves (1.1).

CBF.T27 gives the response spectrum

```text
spec(H_phys)={-4^32,-2^32,+2^32}
```

and the factorization

```text
D_phys(t)^2=(I96+tH_phys/2)^2.
```

The three response projectors commute with `Gamma96`. Exact restriction gives
rank `16` in `H_chi^+` for each response eigenvalue. Therefore

```text
spec(B^*B)
 ={(1-2t)^2^16,(1-t)^2^16,(1+t)^2^16},
```

and (1.2) follows. This is a determinant on the selected 48-dimensional
chiral factor, not a full odd trace on all 96 states.

For a finite complex Grassmann Gaussian, the partition factor is a determinant
of its chiral kinetic block. Its squared modulus is (1.2). For a real or
Majorana convention, the corresponding Pfaffian changes the overall exponent
but not the extrema as long as its orientation is fixed within one invertible
component. Thus the coordinate result below is convention-independent at this
finite tier.

## 4. Neutral invertible chamber

The finite operator becomes singular only at

```text
t=-1, 1/2, 1.
```

Removing these walls splits the real source line into four invertible
components. The neutral closure basepoint `t=0` lies in exactly one of them,
namely (1.5). A continuous background path starting at `D0` and retaining an
invertible fermionic Gaussian cannot leave this component: at either boundary
the determinant vanishes and `W_0` diverges to positive infinity.

This chamber rule does not claim that all possible universes begin at `D0`.
It selects the branch continuously connected to the already selected neutral
CBF basepoint. The second stationary root belongs to a different component and
would require a zero-mode crossing.

## 5. Unique finite Gaussian coordinate

Inside `C_0`, `Delta(t)>0`, and

```text
Delta(t)=1-2t-t^2+2t^3,
Delta'(t)=2(3t^2-t-1).
```

Equation (1.4) gives

```text
W_0'(t)=-(2/3) Delta'(t)/Delta(t).
```

The stationary equation is

```text
3t^2-t-1=0,
```

with roots

```text
t_-=(1-sqrt(13))/6,
t_+=(1+sqrt(13))/6.
```

Since `3<sqrt(13)<4`,

```text
-1<t_-<0<1/2<t_+<1.
```

Thus only `t_-` lies in `C_0`. Moreover, `W_0` diverges at both boundaries
of `C_0`, and this is its only critical point there, so it is the strict global
minimum. Its exact curvature is

```text
W_0''(t_*)
 =72sqrt(13)/(35+13sqrt(13))
 =(338-70sqrt(13))/27
 >0.                                                       (5.1)
```

No empirical number or continuous fit enters (1.6).

## 6. Exact dimensionless values

Substitution of (1.6) in the three positive branches yields (1.7), numerically

```text
sigma_-4=1.8685170918213298...,
sigma_-2=1.4342585459106649...,
sigma_+2=0.5657414540893351... .
```

Their squares are

```text
sigma_-4^2=(17+4sqrt(13))/9,
sigma_-2^2=(19+5sqrt(13))/18,
sigma_+2^2=(31-7sqrt(13))/18.                (6.1)
```

Normalizing to the smallest branch gives the exact ratios

```text
sigma_-4/sigma_+2=(3+sqrt(13))/2,
sigma_-2/sigma_+2=(4+sqrt(13))/3,
sigma_-4/sigma_-2=(sqrt(13)-1)/2.             (6.2)
```

The branch product is

```text
Delta(t_*)=(35+13sqrt(13))/54.                (6.3)
```

If one later supplies the already declared common dimensionful primitive `h`,
the finite singular values are conditionally

```text
m_lambda=h sigma_lambda.
```

This is a one-scale conditional conversion, not a calculation of `h`. Nor has
the theorem proved that the three `H_phys` eigenspaces are the three observed
mass eigenstates in every charged sector. Equations (1.7), (6.1) and (6.2)
are finite operator values; their phenomenological assignment is a separate
intertwiner problem.

## 7. Decisive external-mode boundary

The full four-dimensional fermion determinant is not (1.4). After separating
an external squared mode `x=p^2/h^2`, one finite contribution has the form

```text
W_x(t)=-(1/3) sum_lambda log[x+r_lambda(t)^2],
```

where

```text
r_-4=1-2t,
r_-2=1-t,
r_+2=1+t.
```

Its derivative is

```text
W_x'(t)=-(2/3) sum_lambda
         r_lambda r_lambda'/(x+r_lambda^2).               (7.1)
```

At `x=0`, stationarity gives (1.6). For large `x`, the leading stationary
condition is instead

```text
sum_lambda r_lambda r_lambda'=-2+6t=0,
```

which gives `t=1/3`. Since `t_*` is not `1/3`, no source coordinate is
stationary for every external spectral mode. A spacetime spectral measure,
regularization, counterterms and the remaining bosonic action can shift the
finite value.

This is not a defect in the exact finite calculation. It identifies the next
physical object precisely: the selected external spectral measure and
renormalized BV/QFT pushforward on the same source. Until that object is
supplied, (1.6) is a finite internal Gaussian value, not a final vacuum or
held-out observable.

## 8. Reconciliation with previous results

**CBF.T27.** Its no-go remains correct for `D_phys(t)` plus the normalized
trace alone. CBF.T30 adds the selected Grassmann fermion action, physical
chiral restriction and neutral invertible component. These are exactly the
extra data T27 said were missing.

**CBF.T29.** There is no contradiction with odd-trace cancellation. The
determinant arises after integrating physical Grassmann fields and depends on
the even positive block `B^*B`; it is not an odd scalar trace of `D`.

**A56.** The fermionic sign comes from Grassmann statistics, not from KO
chirality. The A56 no-go is obeyed.

**A73.** The standard determinant response identity is instantiated on the
selected chiral finite block. A73's broader gauge and full physical-selection
questions are not promoted by this theorem.

**A84/A85 and B.ACTION.01.** The finite internal profile and one chamber value
advance the action/value frontier, but they do not provide the complete upper
action, external measure, normalization, continuum transfer or QME. The
blocker remains open.

## 9. Exact boundary

Closed exactly:

- the KO6 chiral block and its positive determinant operator;
- the finite Grassmann-Gaussian determinant profile;
- the neutral invertible component containing `D0`;
- its unique nonzero algebraic stationary coordinate;
- three exact dimensionless singular-value factors, squares and ratios;
- zero observed construction inputs and zero fitted coefficients; and
- the external-mode nonuniversality obstruction.

Still open:

- the full four-dimensional fermion determinant and external spectral measure;
- the renormalized BV/QME pushforward and counterterm scheme;
- all other bosonic, gauge, Higgs and gravitational contributions to the
  source-coordinate effective action;
- the overall dimensionful primitive `h`;
- identification of the three finite branches with measured generations;
- held-out masses, mixings, couplings or precision observables; and
- the complete upper action/automorphism transfer required by B.ACTION.01.

The q79 endpoint counters remain

```text
physical packets: 0/3,
physical rows:    0/7.
```

This theorem nevertheless changes one frontier truth value: the CBF chain now
emits a nonzero exact dimensionless coordinate and three associated finite
values at a source-selected physical-fermion Gaussian tier. Their promotion
to final physical observables requires the external QFT object identified in
Section 7.

## 10. Reproduction

```powershell
python build_ko6_fermionic_determinant_value_selection.py
python verify_ko6_fermionic_determinant_value_selection.py
python -m unittest tests.test_ko6_fermionic_determinant_value_selection -v
python verify.py
```

The generated packet is
`ko6_fermionic_determinant_value_selection.packet.json`.
