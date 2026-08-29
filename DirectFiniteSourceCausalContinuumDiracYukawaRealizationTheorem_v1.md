# Direct Finite-Source Causal Continuum Dirac-Yukawa Realization Theorem

**Claim ID:** `CBF.T25`
**Date:** 2026-08-29
**Status:** exact provider-neutral direct finite-source realization at the
four-dimensional causal, classical fermion/Yukawa and classical BV tier;
q79 HYM provenance, strict values and quantum BV remain open

## 1. Result

CBF.T14 proved that the fixed-point compiler does not logically require a
six-dimensional q79 endpoint. CBF.T23 constructed the exact physical
`96`-dimensional finite Dirac-Yukawa family, and CBF.T24 proved that its
graded product with the selected external chiral differential is the unique
tensor totalization. The remaining question was whether this finite object
can be realized in a genuine continuum theory without first identifying it
with a low-mode Galerkin truncation of an unconstructed HYM operator.

It can, at a precise direct finite-source tier.

Declare the established finite real-even datum

```text
(A_F,H_F,D_phys(t),Gamma_F,J_F),   dim_C H_F=96,
```

to be the exact internal source object, not an approximation to an
unprojected internal continuum. On the already selected globally hyperbolic
four-dimensional carrier `Y4`, form the associated finite bundle

```text
E_F=P_SM times_G H_F
```

and the almost-commutative Dirac-Yukawa family

```text
D_dir(t;A,H)=D_A tensor I_HF + Y_t(H).
```

In a covariantly constant neutral Higgs frame with radial amplitude `h`, this
is exactly

```text
D_dir(t,h)=D_Y tensor I96+Gamma_Y tensor h D_phys(t).
```

The internal realization is fiberwise. In every gauge frame the analysis and
synthesis are inverse identity maps on `H_F`. Therefore

```text
P_int=I96,
Q_int=0,
internal Galerkin residual=0,
internal complement Green contribution=0,
internal omitted-mode tail=0.
```

This is not an approximation theorem. There is no larger internal Hilbert
space in this route from which the `96` states were truncated. The external
spacetime dependence remains an infinite-dimensional continuum and is not
being called a finite cutoff.

The smooth Yukawa-Higgs endomorphism is order zero. Hence `D_dir` retains the
Lorentzian Clifford principal symbol and is Green hyperbolic on the selected
globally hyperbolic base. In the constant neutral frame,

```text
D_dir(t,h)^2
 =D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2,

d/dt D_dir(t,h)^2 at t=0
 =h^2 I tensor H_phys.
```

Thus the CBF.T23 response has a direct causal continuum realization with zero
internal synthesis error. No eta9 result is used.

This closes a provider-neutral direct operator/synthesis clause. It does not
close the distinct q79 HYM-to-finite route, select `h` or a physical value of
`t`, derive the full nonlinear upper action, or prove a quantum master
equation.

## 2. Two continuum questions

The word `continuum` had been carrying two different obligations.

### Route HYM

```text
selected six-dimensional visible-hidden HYM endpoint
  -> continuum Hodge/Dirac operator
  -> selected spectral modes
  -> finite physical carrier.
```

This route needs a nontrivial synthesis map, complementary Green operator,
tail estimate and HYM connection comparison. It remains the exit specified by
`B.HS.01` and `B.GEO.01`.

### Route direct

```text
selected finite real-even source object
  -> associated finite bundle over Y4
  -> exact fiberwise Dirac-Yukawa endomorphism
  -> four-dimensional causal field theory.
```

This route has no internal Galerkin step. Its difficult source question is
why this finite source object and its coefficient values are selected, not
how to approximate it by continuum HYM modes. CBF.T20-CBF.T24 now select its
structural deformation, incidence and product rule, conditional on their
pinned factor sources. They do not select all numerical values.

The two routes can later be compared. If a completed HYM endpoint descends to
the same direct finite source class, that would be a universality theorem. It
is not a prerequisite for the direct realization proved here.

## 3. Exact associated-bundle realization

Let

```text
G_SM=(SU(3) x SU(2) x U(1)_Y)/Z6
```

and let `P_SM -> Y4` be a principal `G_SM` bundle. A46-A50 supply the exact
unitary representation `rho_F` on `H_F`, including three families,
particle-antiparticle completion, grading, real structure and the anomaly-free
shared physical circle. The associated vector bundle is

```text
E_F=P_SM times_(rho_F) H_F.
```

For a local gauge frame `s`, write

```text
U_s(x):H_F -> (E_F)_x,
[p,v] = U_s(x)v.
```

On an overlap with transition `g_st(x)`,

```text
U_t(x)=U_s(x) rho_F(g_st(x)).
```

Hence the local identities

```text
U_s^*U_s=I96,
U_s U_s^*=I_(E_F,x)
```

glue covariantly. The resulting construction is the associated-bundle
functor itself, not a choice of `96` continuum eigenmodes. Its projector and
complement are therefore

```text
P_int=I_(E_F),
Q_int=0.
```

Every finite algebra operation, adjoint, functional calculus and normalized
finite trace is exact on the declared finite source. This is the same
finite-projected exactness principle already certified for the selected
finite qutrit source, applied here only to the exact finite real-even datum
that A48-A51 and CBF.T23 actually provide. It does not identify the two
finite carriers or promote either one to an unprojected HYM integral.

Because `Q_int=0`, the Feshbach term is identically absent:

```text
P_int K Q_int (Q_int K Q_int-z)^-1 Q_int K P_int=0.
```

There are likewise no omitted internal modes. These zeroes are structural,
not numerical estimates.

## 4. Causal operator and domains

Let `S_Y` be the selected framed spinor bundle and let `D_A` be the
gauge-covariant Dirac operator on

```text
S_Y tensor E_F.
```

The one-Higgs incidence of A51 and CBF.T23 defines a smooth gauge-covariant
bundle endomorphism `Y_t(H)`. Set

```text
D_dir(t;A,H)=D_A+Y_t(H).
```

Its natural test domain is

```text
C_c^infinity(Y4,S_Y tensor E_F).
```

The principal symbol is independent of `t`, `H` and the finite matrices:

```text
sigma_Ddir(x,xi)=i Clifford_g(xi) tensor I96.
```

The selected q79 causal theorem already establishes the globally hyperbolic,
time-oriented framed base and the Clifford principal symbol. A smooth
zero-order endomorphism preserves Dirac type. Standard Green-hyperbolic
operator theory therefore gives unique advanced and retarded maps

```text
E_t^+ and E_t^-
```

with the usual causal support. This proves pointwise and interaction locality
on the four-dimensional base at the background-coupled fermion tier. The
finite fiber constrains the allowed charges and interactions but supplies no
additional causal cone or clock.

For a varying Higgs or gauge background, the square contains the expected
connection and derivative terms. They are lower order and do not change the
principal symbol. The clean factorized square below is asserted only in the
covariantly constant neutral frame used to evaluate the CBF response.

## 5. Exact response in the continuum carrier

In the constant neutral frame,

```text
D_dir(t,h)=D_Y tensor I96+Gamma_Y tensor h D_phys(t).
```

The external grading anticommutes with `D_Y`, while `D_phys(t)` is a finite
zero-order operator. Therefore

```text
D_dir(t,h)^2
 =D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2.
```

At the neutral source point, CBF.T23 gives

```text
D_phys(0)^2=I96.
```

Its first variation is the exact physical left-target plus right-source
response, including the forced antiparticle copy:

```text
d/dt D_phys(t)^2 at t=0=H_phys.
```

Consequently

```text
d/dt D_dir(t,h)^2 at t=0=h^2 I tensor H_phys.
```

The computation is pointwise in the finite associated bundle. It has no
internal quadrature, interpolation or Galerkin error. The identity does not
claim that `H_phys` is the scalar Higgs-potential Hessian. It is the
Dirac-Yukawa Laplacian response already typed in CBF.T23.

## 6. Signed action, positive response and classical BV

The first-order fermionic action is

```text
S_ferm(t)=integral_Y4 <bar(psi),D_dir(t;A,H) psi> dvol_g.
```

It is distinct from the positive quadratic repair diagnostic

```text
E_rep(t)=1/2 ||D_dir(t;A,H) psi||^2.
```

The former retains chirality, phase and causal first-order information. The
latter contains the square whose finite response is `h^2 H_phys`. This
separation obeys the existing action-versus-repair no-go and does not rename a
positive closure cost as a Lorentzian Lagrangian.

The four CBF.T23 Yukawa channels are exact `G_SM` singlets. Their family
matrices commute with the family-diagonal gauge action. The established
continuum SM theorem then supplies

```text
s S_ferm=0,
s^2=0,
(S_BV,S_BV)=0
```

for the classical shifted-cotangent BV composition with the same background
family. Substituting the CBF source family does not introduce a new BRST or BV
coefficient. This closes only the fermion/Yukawa classical sublane. Gauge
kinetic normalization, the Higgs potential, the full bosonic upper action,
the quantum measure and renormalized QME remain separate.

## 7. What is now bypassed

For this direct route, the following former synthesis questions are absent:

```text
which 96 internal continuum eigenmodes are retained:  not applicable,
internal polar normalization of their overlap map:    identity,
internal complement inverse:                          zero complement,
internal spectral tail:                               empty,
internal finite-to-continuum error:                    zero.
```

This is stronger than a conditional compiler but narrower than a HYM
derivation. It proves existence of a causal continuum realization of the
selected finite operator. It does not explain the finite operator as a shadow
of a six-dimensional compactification.

Accordingly `B.GEO.01` remains open as written, because that blocker asks for
the physical q79 HYM endpoint and its nontrivial symbol map. The direct route
has a different exit and now passes its operator/synthesis clause. Future
status reports must not say that an HYM Galerkin map is logically required for
all continuum realization; it is required only for HYM provenance.

## 8. Parameter and value boundary

This composition introduces

```text
new observed construction inputs:       0,
new fitted coefficients:                 0,
new internal Galerkin coefficients:      0,
new internal cutoff scales:              0,
new sector-specific physical scales:     0.
```

It inherits the existing single dimensionful primitive notation

```text
h=Lambda=E0=1/L0
```

only at the declared one-primitive tier. The theorem does not compute its SI
value. It also does not choose a numerical Higgs vacuum, a physical value of
the source coordinate `t`, strict masses, mixing angles, threshold values or
precision observables.

The q79 HYM endpoint counts remain

```text
0/3 physical packets,
0/7 physical rows.
```

Those counts describe the q79/HYM three-packet contract. They do not erase
the new provider-neutral direct realization, and the new realization does not
silently increment them.

## 9. Exact scope

Closed here:

```text
direct finite-source internal associated-bundle realization: closed,
fiberwise identity analysis/synthesis:                       closed,
zero internal complement and tail:                           closed,
four-dimensional Dirac-Yukawa principal symbol:              closed,
advanced/retarded Green-hyperbolic consequence:              closed,
continuum h^2 H_phys response identity:                      closed,
gauge/BRST/classical-BV fermion-Yukawa sublane:              closed,
eta9 dependence:                                             none.
```

Still open:

```text
physical q79 visible-hidden HYM endpoint and comparison:     open,
strict numerical h and t selection:                          open,
full nonlinear upper physical action and normalization:     open,
bosonic/gravitational direct-source completion:              open,
quantum BV/QME and renormalized interacting net:             open,
held-out masses, mixings and precision predictions:          open.
```

Thus the direct route has moved from `possible in principle` to an exact
structural causal realization. Its next decisive target is no longer an
internal continuum projector. It is the selected coefficient-bearing action
and background object, followed by a held-out scalar prediction.

## 10. External mathematical context

The Green-hyperbolic implication uses the standard theorem that Dirac-type
operators on globally hyperbolic spacetimes possess advanced and retarded
Green operators. See Christian Baer, *Green-hyperbolic operators on globally
hyperbolic spacetimes*, <https://arxiv.org/abs/1310.0738>.

The Lorentzian finite-real-geometry and fermionic-action typing is standard
almost-commutative geometry. See John W. Barrett, *A Lorentzian version of the
non-commutative geometry of the standard model of particle physics*,
<https://arxiv.org/abs/hep-th/0608221>.

These sources support the analytic and geometric framework. They do not
select the MTT finite source, its deformation or any numerical value.

## 11. Reproduction

```text
python build_direct_finite_source_continuum_realization.py
python verify_direct_finite_source_continuum_realization.py
python -m unittest tests.test_direct_finite_source_continuum_realization -v
```

The generated certificate is
`direct_finite_source_continuum.packet.json`.
