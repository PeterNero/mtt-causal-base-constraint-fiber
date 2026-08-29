# Canonical Normalized Dirac-Square Defect Repair Action and Value-Selection No-Go Theorem

**Claim ID:** `CBF.T26`

**Date:** 2026-08-29

**Status:** exact normalized positive repair action for the direct finite source,
including its complete quartic jet and continuum scaling; the signed physical
action, absolute action normalization, nonzero physical source coordinate and
held-out observable remain open

## 1. Result

CBF.T23 constructed the exact physical finite Dirac-Yukawa family on the
`96`-dimensional real-even carrier. CBF.T25 realized it as an exact finite
associated-bundle fiber over the selected causal four-dimensional base. Those
theorems computed the first response

```text
d/dt D_phys(t)^2 at t=0=H_phys,
Tr(H_phys^2)=768,
rank(H_phys)=96,
```

but did not construct the complete nonlinear finite repair functional.

Write the affine family as

```text
D_phys(t)=D0+t D1,
D0^2=I96.
```

Its Dirac-square closure defect is exactly

```text
K(t)=D_phys(t)^2-I96=t H_phys+t^2 R,
H_phys=D0 D1+D1 D0,
R=D1^2.
```

The unique normalized unitary-invariant trace state on the full finite matrix
algebra is `tau_96=Tr/96`. In the declared minimal quadratic defect class, the
standard unit-gradient representative is therefore

```text
S_rep(t)=1/2 tau_96(K(t)^* K(t)).
```

Exact evaluation gives

```text
S_rep(t)=4 t^2-(16/3)t^3+3t^4
        =t^2[3(t-8/9)^2+44/27].
```

This is a genuine coefficient-bearing result: the quadratic, cubic and
quartic repair coefficients are all emitted by the same finite source, with no
observed value or fit. It is also a decisive no-go. The action is strictly
positive for every real `t != 0`, and

```text
S_rep'(t)=4t(3t^2-4t+2)
```

has only the real zero `t=0`. The minimal direct defect-square action therefore
stabilizes the closure point and cannot select a nonzero Yukawa or other
physical value coordinate. Such a value requires a distinct selected signed
action, affine/background source, density, or shifted target defect.

This theorem obeys the H4-T9 action-versus-repair separation. It does not call
`S_rep` the Lorentzian, BV or cyclic Maurer-Cartan action and does not close
`B.ACTION.01` or `B.SM.02`.

## 2. Pinned finite source

The primitive finite source is the CBF.T20 Weyl-Gram datum

```text
(P,X,Z),
Y_phase(t)=-P+t(I+Z),
Y_shift(t)=-P+t(I+X).
```

CBF.T23 routes these two family maps through the four gauge-singlet Yukawa
incidences, adds adjoints and applies the forced KO6 particle-antiparticle
completion. Every operation is linear in `t`, so the resulting self-adjoint
operator is affine:

```text
D_phys(t)=D0+tD1.
```

This is an identity of exact matrices, not a Taylor approximation. CBF.T23 and
CBF.T25 already establish

```text
dim_C H_F=96,
D0^2=I96,
H_phys=d/dt D_phys(t)^2 at t=0.
```

No q79 Galerkin endpoint, measured Yukawa magnitude, Higgs vacuum value or
continuum cutoff enters this finite calculation.

## 3. Exact defect expansion

Expanding the affine square gives

```text
D_phys(t)^2
 =D0^2+t(D0D1+D1D0)+t^2D1^2.
```

Since `D0^2=I96`, define

```text
H_phys=D0D1+D1D0,
R=D1^2.
```

Then

```text
K(t)=D_phys(t)^2-I96=tH_phys+t^2R.       (3.1)
```

Both `H_phys` and `R` are self-adjoint. The exact source additionally gives

```text
[H_phys,R]=0,
rank_C(H_phys)=96,
rank_C(R)=96.
```

Commutation is useful for simultaneous spectral interpretation, but the trace
calculation below only needs cyclicity.

## 4. Why the normalized trace is canonical here

Let `tau` be a positive normalized linear state on `M_96(C)`. It has the form

```text
tau(A)=Tr(rho A),
rho>=0,
Tr(rho)=1.
```

Suppose the scalar repair diagnostic is independent of every unitary change of
finite basis. Then

```text
tau(UAU^*)=tau(A)
```

for every `U in U(96)`. Hence `rho` commutes with every unitary matrix. The
commutant of the defining full matrix algebra consists only of scalars, so

```text
rho=I96/96,
tau=tau_96=Tr/96.                         (4.1)
```

This is the `96`-dimensional version of the normalized finite trace principle
used by A74 and CBF.T18. It selects the averaging functional, not a physical
spacetime density.

Now restrict attention to positive quadratic defect costs obtained by applying
that normalized invariant state to `K^*K`:

```text
S_c(K)=c tau_96(K^*K),
c>0.
```

They form one positive scale ray. Choosing the conventional gradient
normalization

```text
grad_K S=K
```

sets `c=1/2`. Equivalently, this fixes the unit of repair-flow time. Rescaling
`c` does not change the zero set, but it does rescale the repair Hessian and
must not be mistaken for a derived physical action normalization.

The uniqueness claim is deliberately limited to this normalized quadratic
defect class. It does not exclude higher invariants, an affine pressure term,
a signed cyclic functional or an independently selected Lorentzian action.

## 5. Exact coefficient calculation

Because `K(t)` is self-adjoint, equations (3.1) and trace cyclicity give

```text
S_rep(t)
 =1/(2*96) Tr[(tH_phys+t^2R)^2]
 =Tr(H_phys^2)/(2*96) t^2
  +Tr(H_phys R)/96 t^3
  +Tr(R^2)/(2*96) t^4.                    (5.1)
```

The exact matrix calculation yields

```text
Tr(H_phys^2)= 768,
Tr(H_phys R) =-512,
Tr(R^2)      = 576.
```

Substitution into (5.1) gives

```text
S_rep(t)=4t^2-(16/3)t^3+3t^4.            (5.2)
```

In particular,

```text
S_rep''(0)=8.                             (5.3)
```

The number `8` is the normalized direct-source repair stiffness in the unit
repair-time convention. The new nonlinear data are the exact cubic coefficient
`-16/3` and quartic coefficient `3`. These are internal invariants of the
pinned source family. No theorem here maps them to a measured mass, coupling or
threshold.

## 6. Positivity and the nonzero-value no-go

Complete the square in (5.2):

```text
S_rep(t)=t^2[3(t-8/9)^2+44/27].           (6.1)
```

The bracket is strictly positive for every real `t`. Therefore

```text
S_rep(t)>=0,
S_rep(t)=0 iff t=0.                       (6.2)
```

Differentiation gives

```text
S_rep'(t)=4t(3t^2-4t+2).
```

The discriminant of the quadratic factor is

```text
(-4)^2-4*3*2=-8<0.
```

Since its leading coefficient is positive, it has no real zero. Thus

```text
Crit_R(S_rep)={0},
argmin_R S_rep={0}.                       (6.3)
```

### Corollary 6.1

If a proposed physical interpretation requires a nonzero real `t_*` to arise
as a stationary point of this minimal repair action, it is impossible.

### Corollary 6.2

A shifted defect

```text
K(t)-K_*
```

could place its zero at a nonzero coordinate, but `K_*` would be additional
source data unless independently emitted by the same upper geometry. Writing
down that shift is not a derivation of a value.

This is the useful frontier change: another search over positive polynomials of
the same unshifted defect cannot solve value selection. The next source must
change the action lane or provide a selected background target.

## 7. Direct continuum lift

CBF.T25 gives, in a covariantly constant neutral Higgs frame,

```text
D_dir(t,h)^2
 =D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2.
```

Subtract the external square and the neutral internal identity contribution.
The relative direct defect is

```text
K_dir,rel(t,h)=h^2 I tensor K(t).         (7.1)
```

With the normalized trace on the duplicated external witness and the internal
fiber, equation (7.1) gives

```text
S_dir,rep(t,h)=h^4 S_rep(t).              (7.2)
```

This is an exact local finite-fiber repair density. It introduces no internal
Galerkin error and does not change the Lorentzian principal symbol. It is not a
spacetime-integrated physical action because the physical value of `h`, the
spacetime density, gauge and gravitational bosonic terms, and overall action
normalization have not been selected here.

## 8. Separation from signed action

H4-T9 proves that

```text
1/2 <Phi,W Phi>
```

is a positive repair cost with Hessian `J^*WJ`; it does not in general recover
the sign, phase, Morse index or causal inverse of a signed variational action.
CBF.T25 already keeps the first-order fermionic action

```text
S_ferm=integral <bar(psi),D_dir psi> dvol
```

separate from its positive squared diagnostic.

H4-T10 provides a signed cyclic action for a Maurer-Cartan integrability lane,
but it does not identify that action with the complete physical q79 or direct
finite-source bosonic action. CBF.T26 therefore makes none of the following
identifications:

```text
S_rep = S_ferm,
S_rep = S_MC,
S_rep = S_BV,
S_rep = a Lorentzian Standard-Model action.
```

The quartic in (5.2) is the exact nonlinear **repair** action attached to the
Dirac-square closure defect. Its role is stability, response and diagnostics.

## 9. Parameter and proof ledger

This construction uses

```text
new observed construction inputs:    0,
new fitted coefficients:             0,
new sector-specific parameters:      0,
new dimensionful primitives:         0.
```

The factor `1/2` fixes the standard unit-gradient representative of one
positive scale ray. It is a repair-time convention, not a claimed new physical
constant.

CBF.T26 closes:

- the exact normalized direct finite-source positive repair action;
- the complete quadratic, cubic and quartic coefficient row;
- its exact `h^4` continuum relative-defect scaling;
- strict positivity and uniqueness of the real closure minimum; and
- the no-go against selecting a nonzero physical coordinate from this minimal
  unshifted defect square.

It does not close:

- a selected signed upper physical action or Lorentzian density;
- absolute action normalization relative to `hbar`;
- a nonzero physical value of `t` or `h`;
- a measured mass, mixing, coupling or threshold prediction;
- the q79 HYM provenance route;
- the interacting renormalized QME; or
- `B.ACTION.01` or `B.SM.02`.

Physical q79 acceptance therefore remains

```text
packets: 0/3,
rows:    0/7.
```

## 10. Next decisive construction

The finite response and its nonlinear repair completion no longer need to be
recomputed. A route to a nonzero physical value must now provide one of:

1. a same-root signed variational action whose stationary equation contains the
   finite family and its physical density;
2. a selected affine/background term that shifts the stationary point, with
   its coefficient derived before empirical comparison; or
3. a selected physical endpoint that emits a target defect `K_*`, its units and
   a held-out observable map.

Any candidate must reproduce the already fixed `H_phys` linear response and
must be compared against the exact nonlinear coefficients in (5.2). Merely
postulating another positive unshifted norm cannot change the conclusion of
Section 6.

## 11. Reproduction

Build the packet:

```powershell
python build_direct_dirac_defect_repair_action.py
```

Run the independent reconstruction:

```powershell
python verify_direct_dirac_defect_repair_action.py
```

Run the complete repository verification:

```powershell
python verify.py
```

The machine-readable result is
`direct_dirac_defect_repair_action.packet.json`. The source lock pins every
controlling theorem, packet, repository head and the active kernel model.
