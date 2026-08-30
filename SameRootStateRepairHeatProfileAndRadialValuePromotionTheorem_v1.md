# Same-Root State-Repair Heat Profile and Radial-Value Promotion Theorem v1

**Claim:** CBF.T34

**Date:** 2026-08-30

**Status:** exact same-root and heat-profile theorem at the selected finite
direct-source, totalization and internal-checkpoint tier; the additive physical
clock lift, full four-dimensional determinant, absolute scale, particle map
and renormalized observables remain open.

## 1. Result

CBF.T33 obtained exact nonzero radial branch values after freezing the CBF.T30
source coordinate, but retained two explicit conditions:

1. the finite determinant selector had not been connected to the downstream
   product action by one source diagram; and
2. A53's one-atom proper-time measure was still an added minimal-support
   premise.

Both conditions can be removed at the already declared algebraic and selected
internal-checkpoint tier. The key is to use the physical state carrier, not
the operator-space repair carrier of CBF.T28.

CBF.T24 selects the total differential and its self-adjoint closure charge

```text
q_tot(t,h)=q_Y tensor I+Gamma_Y tensor h q_F(t),
B_tot(t,h)=q_tot(t,h)+q_tot(t,h)^*.
```

The finite factor `q_F(t)` supplies the CBF.T30 Grassmann determinant. The
same total differential supplies the positive state-space generator

```text
K(t,h)=B_tot(t,h)^2/Lambda^2.
```

The canonical quadratic closure functional has negative-gradient flow
`exp(-sK)`. Therefore the normalized scalar cutoff profile is forced to be

```text
chi_s(x)=exp(-s x).
```

Its positive Laplace-representing measure is uniquely `delta_s`; no
minimal-support axiom is needed. At the inherited selected internal checkpoint

```text
s=tau_int=log(448)/15,
```

the spectral moment ratio is exactly

```text
f2/f0=1/tau_int=15/log(448).
```

Consequently the CBF.T33 A53 radial row is promoted from "conditional on a
one-atom measure premise" to "derived from the same total closure charge and
selected internal checkpoint." This does not make the resulting cutoff-unit
eigenvalues measured particle pole masses.

## 2. One source diagram

The CBF.T24 source object is not merely the self-adjoint operator `B_tot`.
It is the factor data and their unique graded totalization:

```text
R_tot=(q_Y,q_F(t),Gamma_Y,h,totalize).
```

There are two functorial readouts.

The finite-factor readout gives

```text
R_tot -> q_F(t) -> D_phys(t)=q_F(t)+q_F(t)^*
      -> B_F(t)=P_- D_phys(t) P_+
      -> W0(t)=-(1/48)log det(B_F(t)^*B_F(t)).
```

CBF.T30 proves that the neutral invertible component has the unique minimum

```text
t_*=(1-sqrt(13))/6.                                    (2.1)
```

The total-charge readout gives

```text
R_tot -> B_tot(t,h) -> K(t,h)=B_tot(t,h)^2/Lambda^2
      -> exp(-sK(t,h)).                                (2.2)
```

The occurrence of `q_F(t)` in both paths is literal: it is the same finite
factor of the universal totalization. No comparison matrix or fitted map is
inserted. Applying the CBF.T33 source-freeze theorem means evaluating (2.2)
at (2.1) without varying `t` again in the lower Higgs problem.

This closes a same-composite-root diagram at the T24 direct-source tier. It
does not prove that the full q79/HYM background or this factor source is the
unique physical universe selected by upper MTT.

## 3. State-space quadratic repair theorem

Let `H` be the selected Hilbert realization and let `B=B^*` be a closed
self-adjoint closure charge. Set

```text
K=B^2/Lambda^2 >= 0                                    (3.1)
```

and define, on the form domain of `B`,

```text
J_B(Psi)=1/2 ||B Psi/Lambda||^2
         =1/2 <Psi,K Psi>.                             (3.2)
```

The form gradient is `K Psi`. Hence the linearized closure-repair equation is

```text
d_s Psi=-K Psi.                                        (3.3)
```

By the spectral theorem, `-K` generates the unique strongly continuous
contraction semigroup

```text
T_s=exp(-sK),  s>=0.                                   (3.4)
```

It obeys

```text
T_0=I,
T_s T_r=T_(s+r),
||T_s||<=1,
ker K=Fix(T_s) for every s>0.                          (3.5)
```

The coefficient in (3.2) is not a physical fit. `B_tot` and the Hilbert
metric are already normalized by the T24 factor complexes. Multiplying the
whole functional by a new positive constant would introduce a new clock
normalization; it is excluded at this no-new-clock tier. An overall spectral
trace amplitude remains irrelevant to the moment ratio below.

For CBF.T24,

```text
B_tot(t,h)^2
 =D_Y^2 tensor I+h^2 I tensor D_phys(t)^2.             (3.6)
```

Thus (3.4) is a scalar functional calculus of the same product square used by
the CBF.T32 heat-kernel action. It is not a semigroup on a different carrier.

The passage from repair propagation to an action profile is not automatic in
an arbitrary spectral triple. It is supplied here by A84's declared
closure-shadow action theorem: at its fixed-point-gradient-flow and
regime-local action tier, the selected repair kernel enters the coherently
reduced action through its finite overlap/trace. Applying that rule to (3.4),
the uninserted scalar trace is

```text
Tr exp(-sK)=Tr chi_s(K).                               (3.7)
```

Thus the semigroup determines the scalar profile used in the CBF.T32 action
at this tier. Without the A84 action-shadow rule, (3.4) would select a repair
propagator but not, by itself, a bosonic spectral-action profile. A84's
remaining matching-completeness clause and the full nonlinear physical action
remain open.

## 4. Unique scalar profile

Let `x>=0` denote the spectral coordinate of `K`. Equation (3.4) acts on each
spectral fiber by

```text
chi_s(x)=exp(-s x).                                    (4.1)
```

This profile is unique in either of two equivalent senses.

First, the spectral theorem uniquely determines (4.1) from the generator
`K`. Second, suppose a continuous positive family satisfies

```text
chi_0(x)=1,
chi_(s+r)(x)=chi_s(x)chi_r(x),
d_s chi_s(x)|_(s=0)=-x.
```

For fixed `x`, the continuous multiplicative Cauchy equation gives
`chi_s(x)=exp(-sx)`. Therefore there is no remaining scalar-profile shape
parameter.

This is a linearized state-space repair statement. It does not assert that
the full nonlinear Lorentzian/BV action is a heat equation.

## 5. The one-atom measure is a theorem

Let `mu` be a finite positive Borel measure on `[0,infinity)` satisfying

```text
int exp(-u x) dmu(u)=A exp(-s x)                       (5.1)
```

for every `x>=0`, with `A>0`. Then

```text
mu=A delta_s.                                          (5.2)
```

To prove uniqueness without assuming moments at the origin, fix `x0>0` and
tilt the measure:

```text
dnu_x0(u)=exp(-x0 u)dmu(u)/(A exp(-s x0)).             (5.3)
```

This is a probability measure. Differentiating (5.1) at `x0` is legitimate
because `u^n exp(-x0u)` is bounded for `n=1,2`. It gives

```text
E_nu[u]=s,
Var_nu(u)=0.                                           (5.4)
```

Hence `nu_x0=delta_s`, and the strictly positive tilt implies (5.2).

Thus A53's one-atom measure is not selected because it has the smallest
support. It is selected because it is the only positive measure representing
the already selected exponential semigroup profile.

## 6. Spectral moments

Use the A53/CBF.T32 heat-kernel convention for

```text
chi_s(x)=A exp(-s x).
```

Then

```text
f0=chi_s(0)=A,
f2=int_0^infinity chi_s(x) dx=A/s,
f4=int_0^infinity x chi_s(x) dx=A/s^2.                 (6.1)
```

Therefore

```text
f2/f0=1/s,
f4/f0=1/s^2,
f0 f4-f2^2=0.                                         (6.2)
```

The last identity is the rank-one Hankel certificate. The amplitude `A`
cancels from every ratio used below, so no normalization knob is hidden in
the promotion.

At

```text
s=tau_int=log(448)/15,                                 (6.3)
```

equations (6.2) give

```text
f2/f0=15/log(448),
f4/f0=225/log(448)^2.                                  (6.4)
```

The exact checkpoint identity is

```text
exp(-15 tau_int)=1/448.                                (6.5)
```

A84 establishes (6.5) at the fixed-point-gradient-flow and selected internal
checkpoint tier. The separate physical-time statement remains conditional:
the QM clock theorem has not derived its additive clock hypotheses from upper
MTT. CBF.T34 uses the internal semigroup parameter, not an unproved equation
identifying compact phase with Lorentzian time.

## 7. Promoted radial values

At (2.1), CBF.T33 gives

```text
R_*=(3106+4sqrt(13))/4393.                             (7.1)
```

The frozen-source radial equation is

```text
h_*^2/Lambda^2=R_* f2/f0.                             (7.2)
```

Using (6.4),

```text
h_*/Lambda
 =sqrt[15(3106+4sqrt(13))/(4393 log(448))]
 =1.32110162937546849372....                           (7.3)
```

The three finite branch eigenvalues are

```text
m_-4/Lambda=2.46850097452107062662...,
m_-2/Lambda=1.89480130194826956017...,
m_+2/Lambda=0.74740195680266742727....                 (7.4)
```

The radial tree-curvature ratio is

```text
m_h/Lambda=sqrt(120/log(448))
           =4.43358606544780223278....                 (7.5)
```

Equations (7.3)-(7.5) are no longer conditional on A53's minimal-support
premise. They are selected outputs at the finite direct-source, T24
totalization, quadratic state-repair and internal-checkpoint tier.

They remain dimensionless cutoff-unit spectral values. A common heat
normalization does not generate the missing sector hierarchy: their relative
ratios are still the three CBF.T30 ratios.

## 8. Why CBF.T28 is not violated

CBF.T28 acts on

```text
V_sa=End_sa(H_F)
```

with a superoperator

```text
A_rep:V_sa -> V_sa.
```

It correctly proves that `exp(-sA_rep)` is not `exp(-sR)` and is not a scalar
profile of `D_phys^2`.

CBF.T34 instead acts on the physical state carrier `H` with

```text
K=B_tot^2/Lambda^2:H -> H.
```

The two generators have different domains, spectra and meanings. No trace or
operator is substituted across carriers. T28 remains closed exactly as
stated.

## 9. What has and has not become physical

Promoted here:

- the finite determinant and product heat profile now have one composite-root
  diagram;
- the no-double-variation role of `t_*` is implemented in that diagram;
- the scalar heat profile is derived from state-space closure repair;
- A84's action-shadow bridge identifies that profile with the regime-local
  spectral-action trace rather than merely a propagator;
- the positive one-atom measure is unique rather than postulated;
- `f2/f0=15/log(448)` is selected at the internal-checkpoint tier; and
- the four cutoff-unit radial/eigenvalue rows (7.3)-(7.5) are selected at that
  same declared tier.

Still open:

- unconditional upper-MTT selection of all factor sources and the physical
  q79/HYM background;
- derivation of the additive physical-clock lift;
- the full four-dimensional fermion determinant and renormalized vacuum;
- selection of an SI value for `Lambda`;
- a sector/generation map producing nine charged Yukawa magnitudes;
- neutral values, mixing, CP, loop/RG/threshold/pole transport and a held-out
  observable; and
- the full exits of `B.ACTION.01`, `B.QFT.02` and `B.SM.02`.

Accordingly the q79 physical endpoint counters remain

```text
physical packets: 0/3,
physical rows:    0/7.
```

The new values are physically typed finite mass-operator and radial-curvature
coordinates in cutoff units. Calling them observed particle masses would
still be an overclaim.

## 10. Reproduction

```powershell
python build_same_root_state_repair_heat_profile_radial_values.py
python verify_same_root_state_repair_heat_profile_radial_values.py
python -m unittest tests.test_same_root_state_repair_heat_profile_radial_values -v
python verify.py
```

The generated packet is
`same_root_state_repair_heat_profile_radial_values.packet.json`.
