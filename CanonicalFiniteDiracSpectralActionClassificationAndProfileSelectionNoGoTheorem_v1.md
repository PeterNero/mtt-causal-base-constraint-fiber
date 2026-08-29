# Canonical Finite Dirac Spectral-Action Classification and Profile-Selection No-Go Theorem

**Claim ID:** `CBF.T27`

**Date:** 2026-08-29

**Status:** exact full spectral classification of the selected finite
Dirac-Yukawa family and exact profile-independent value-selection no-go;
selection of the physical action, Higgs/Yukawa values and held-out observables
remains open

## 1. Result

CBF.T23 constructed the exact `96 x 96` physical finite Dirac-Yukawa family

```text
D_phys(t)=D0+tD1,                 D0^2=I96,
```

and CBF.T26 computed the complete positive Dirac-square defect action. The
full spectrum of this family had not been classified. That omission matters:
before searching for a new action, one must know whether the existing operator
and normalized trace already force a nonzero stationary coordinate for every
reasonable spectral functional.

They do not. The exact source satisfies the stronger identities

```text
[D0,D1]=0,
H_phys=D0D1+D1D0=2D0D1,
D1=(1/2)D0 H_phys,
R=D1^2=(1/4)H_phys^2,

D_phys(t)=D0(I96+t H_phys/2),
D_phys(t)^2=(I96+t H_phys/2)^2.              (1.1)
```

Moreover,

```text
spec(H_phys)={-4^32,-2^32,+2^32}.
```

Consequently the complete squared spectrum is

```text
spec(D_phys(t)^2)
 ={(2t-1)^2^32,(t-1)^2^32,(t+1)^2^32}.      (1.2)
```

For every scalar function `f` defined on these three nonnegative arguments,
the unique normalized unitary-invariant trace therefore gives

```text
S_f(t)=tau_96[f(D_phys(t)^2)]
      =[f((t-1)^2)+f((t+1)^2)+f((2t-1)^2)]/3.   (1.3)
```

Equation (1.3) is a complete finite spectral-action classifier. It reduces
every even scalar spectral functional of this family to three explicit scalar
branches. It also proves the decisive no-go: the operator and trace do not
select the profile `f`, and different admissible profiles have different
stationary coordinates. There is no real coordinate stationary for both
`f(s)=s` and `f(s)=s^2`, and there is no coordinate stationary for every heat
profile `f_tau(s)=exp(-tau s)`, `tau>0`.

Thus a nonzero physical value cannot be promoted from `D_phys(t)` and
`tau_96` alone. The missing datum is now exactly a same-root action profile,
nonlinear closure-repair law or equivalent physical variational principle.
This theorem does not close `B.ACTION.01` or `B.SM.02`.

## 2. Pinned source and Fourier lanes

The primitive CBF.T20 datum is

```text
(P,X,Z,F3),
Y_phase(t)=-P+t(I+Z),
Y_shift(t)=-P+t(I+X).
```

The exact Fourier identities are

```text
F3^* P F3=P,
F3^*(I+X)F3=I+Z,
F3^*Y_shift(t)F3=Y_phase(t).                 (2.1)
```

CBF.T23 inserts these maps into four phase incidences and four shift
incidences, adds their adjoints and performs the forced KO6 real completion.
Equation (2.1) shows before any numerical diagonalization that the phase and
shift lanes have identical singular spectra. Their eigenvectors and physical
incidence labels remain different; a scalar spectral trace forgets that
orientation data.

No observed mass, coupling, mixing angle, Higgs vacuum or q79 Galerkin row is
used below.

## 3. Exact factorization

Because `D_phys(t)` is affine, write its first square variation as

```text
H_phys=D0D1+D1D0.
```

Direct exact multiplication in `Q(sqrt(3),i)` gives

```text
D0D1=D1D0.                                  (3.1)
```

Since `D0^2=I96`, equation (3.1) implies

```text
H_phys=2D0D1,
D1=(1/2)D0H_phys.                           (3.2)
```

Squaring (3.2), using `[D0,H_phys]=0`, gives

```text
D1^2=H_phys^2/4.                            (3.3)
```

Substitution in the affine family proves both identities in (1.1). In
particular, the CBF.T26 quadratic remainder `R` is not another independent
source object: it is forced by the first response.

The response obeys the exact minimal-polynomial identity

```text
(H_phys+4I)(H_phys+2I)(H_phys-2I)=0.         (3.4)
```

The three Lagrange spectral projectors constructed from (3.4) are
self-adjoint, pairwise orthogonal, sum to `I96`, and each have exact rank and
trace `32`. Thus (3.4) has no missing eigenvalue or multiplicity.

## 4. Full signed and squared spectra

On the three response eigenspaces, equation (1.1) becomes

```text
H=-4:  D(t)^2=(1-2t)^2,
H=-2:  D(t)^2=(1-t)^2,
H=+2:  D(t)^2=(1+t)^2.                      (4.1)
```

Each subspace has dimension `32`, proving (1.2). The odd grading gives equal
positive and negative signed multiplicities. Equivalently,

```text
spec(D_phys(t))
 ={ +(1-2t)^16, -(1-2t)^16,
    +(1-t)^16,  -(1-t)^16,
    +(1+t)^16,  -(1+t)^16 }.                (4.2)
```

The family has three singular walls,

```text
t=-1,                 t=1/2,                 t=1.
```

At the closure basepoint,

```text
spec(D_phys(0))={-1^48,+1^48}.
```

Therefore `t=0` does not mean a zero operator. It is the undeformed normalized
involution selected by the positive repair target `D^2=I`.

## 5. Universal spectral functional

Let

```text
tau_96=Tr/96.
```

A74 and CBF.T18 prove that this is the unique positive normalized scalar trace
invariant under all unitary basis changes on the simple full matrix carrier.
Applying functional calculus to (1.2) gives equation (1.3) immediately.

For differentiable `f`, its derivative is

```text
S_f'(t)
 =(2/3)[
   (t-1)f'((t-1)^2)
  +(t+1)f'((t+1)^2)
  +2(2t-1)f'((2t-1)^2)
 ].                                          (5.1)
```

The normalized trace selects the average in (1.3). It does not select the
function `f`. This is the exact point at which operator data end and action
data begin.

Because the signed spectrum is grading symmetric, every ordinary odd trace
moment vanishes. A scalar trace action therefore also cannot recover the
fermionic sign, phase-lane orientation or CP-sensitive eigenvector data from
eigenvalues alone.

## 6. Four exact profile comparisons

### 6.1 Dirac-norm profile

For `f(s)=s/2`,

```text
S_D(t)=1/2 tau_96(D_phys(t)^2)
      =t^2-(2/3)t+1/2
      =(t-1/3)^2+7/18.                      (6.1)
```

It has the unique global minimum

```text
t=1/3,                 S_D=7/18.
```

This is an exact least-Hilbert-Schmidt-norm coordinate in the declared affine
family. It is not a selected physical vacuum because no upstream theorem yet
chooses `f(s)=s/2` as the physical MTT action.

### 6.2 Quartic-moment profile

For `f(s)=s^2`,

```text
S_2(t)=tau_96(D_phys(t)^4)
      =6t^4-(32/3)t^3+12t^2-(8/3)t+1,

S_2'(t)=(8/3)(9t^3-12t^2+9t-1).            (6.2)
```

The derivative of the cubic factor has negative discriminant,

```text
(-24)^2-4(27)(9)=-396<0,
```

so the cubic is strictly increasing and has one real root. Exact rational
signs bracket it by

```text
0.132 < alpha < 0.133,
alpha approximately 0.132061614157470.
```

At `t=1/3` the cubic factor equals `1`, so the Dirac-norm and quartic-moment
profiles cannot share a stationary coordinate.

### 6.3 Closure-defect profile

For

```text
f(s)=(s-1)^2/2,
```

CBF.T26 gives

```text
S_rep(t)=4t^2-(16/3)t^3+3t^4
        =t^2[3(t-8/9)^2+44/27].             (6.3)
```

Its unique real stationary point and global minimum is `t=0`. This does not
contradict (6.1) or (6.2): the three functionals answer three different
variational questions.

### 6.4 Normalized log determinant

Away from the three singular walls,

```text
Gamma(t)=tau_96 log(D_phys(t)^2)
        =(2/3)log|(t-1)(t+1)(2t-1)|.        (6.4)
```

Its stationary equation is

```text
3t^2-t-1=0,
```

with exact roots

```text
t_-=(1-sqrt(13))/6,
t_+=(1+sqrt(13))/6.                         (6.5)
```

Since

```text
Gamma''(t)=-(2/3)[1/(t-1)^2+1/(t+1)^2+4/(2t-1)^2]<0,
```

both are strict local maxima of `Gamma` and strict chamberwise local minima
of `-Gamma`. A73 explains why a normalized log determinant follows from an
already selected positive Gaussian Hessian and statistics. It does not select
this CBF family as that physical Hessian, choose a chamber or promote either
root to a measured value.

## 7. Heat-profile no-go

The A53/A85 route motivates the heat family

```text
f_tau(s)=exp(-tau s),                 tau>0.
```

Equation (1.3) becomes

```text
H_tau(t)=1/3[
 exp(-tau(t-1)^2)
+exp(-tau(t+1)^2)
+exp(-tau(2t-1)^2)
].                                           (7.1)
```

Suppose one coordinate were stationary for every `tau>0`. Expanding (7.1)
at `tau=0`, the coefficient linear in `tau` is the negative first moment.
Therefore the common coordinate would have to satisfy

```text
d/dt tau_96(D_phys(t)^2)=0,
```

which forces `t=1/3` by (6.1). But direct differentiation gives

```text
H_tau'(1/3)
 =(4tau/9)[
   exp(-4tau/9)+exp(-tau/9)-2exp(-16tau/9)
 ].                                           (7.2)
```

For every `tau>0`, each of the first two exponentials is strictly larger than
`exp(-16tau/9)`. Hence the bracket and (7.2) are strictly positive. No real
coordinate is stationary for every heat profile.

In particular, the selected numerical expression
`tau_int=log(448)/15` from A53 cannot solve profile selection by itself. A53
correctly records its one-atom proper-time rule as conditional rather than a
primitive MTT theorem.

## 8. Profile-selection no-go

The preceding calculations prove two nested statements.

### Polynomial statement

There is no real `t_*` such that

```text
S_f'(t_*)=0
```

for every polynomial profile `f`, because the profiles `s` and `s^2` already
have different unique stationary points.

### Heat statement

There is no real `t_*` stationary for all completely monotone one-atom heat
profiles `exp(-tau s)`, by Section 7.

Therefore neither the exact operator family nor its uniquely normalized trace
contains a profile-independent stationary coordinate. This is a no-go only
for profile-free selection. It does not forbid a deeper MTT closure-dynamics
theorem from selecting one action and thereby one coordinate.

## 9. What `t` does and does not mean

The parameter `t` entered CBF.T20 as a deformation coordinate used to extract
the first Gram response. It was not introduced as a measured Yukawa coupling.
CBF.T23 then identified

```text
H_phys=d[D_phys(t)^2]/dt at t=0
```

with the exact physical left-target/right-source Yukawa-Laplacian response.
CBF.T26 proves that `t=0` is the unique closure point for the normalized
Dirac-square defect repair law.

This theorem shows why one must keep three assertions separate:

```text
closure basepoint:                  t=0, exact at repair tier;
stationary point of another f:      profile dependent;
measured Higgs/Yukawa magnitude:    not derived here.
```

Although `D_phys(0)` is nonzero and invertible, all its singular magnitudes
are equal to one. Thus the basepoint alone does not generate the observed
family hierarchy. A profile-selected nonzero `t` would still require a theorem
mapping its three branch magnitudes to typed physical sectors and a selected
dimensionful Higgs scale.

## 10. Closure-repair interpretation

The nonlinear closure-repair program asks for a process before its
linearized operator. CBF.T26 and this theorem now distinguish two logically
different constructions:

```text
repair target D^2=I
  -> positive defect norm
  -> selected closure basepoint t=0;

physical action profile f
  -> scalar spectral functional S_f
  -> profile-dependent stationary structure.
```

The first lane is closed for this finite source. The second is not. Calling a
convenient `f` canonical after seeing its stationary value would simply move a
fit into functional form. The required advance is an upstream repair law,
cyclic/BV action, selected Gaussian fluctuation complex or other same-root
principle that emits `f` before physical values are inspected.

## 11. Spectral data cannot carry all orientation data

The Fourier equivalence (2.1) makes the phase and shift Gram spectra equal.
Thus every action of the form

```text
tau_96 f(D_phys(t)^2)
```

is blind to exchanging the two Fourier-paired lanes. This does not erase their
physical distinction: CBF.T23 routes them to different Yukawa incidences, and
the noncommuting eigenvectors carry information absent from the eigenvalue
multiset.

Consequently strict mixing, CP phase and gauge-incidence orientation cannot be
derived from the scalar spectral profile alone. They require matrix elements,
mixed noncommutative invariants, the fermionic action or another typed
orientation-sensitive readout.

## 12. Compatibility with the action authorities

The result aligns with, rather than reopens, the current action ledger:

- A74 selects normalized trace inside a simple finite block, not `f`.
- A73 derives `log det` once a positive physical Gaussian Hessian and its
  statistics are already selected.
- A85 supplies a finite projected spectral-action form at its declared corpus
  action tier, while primitive proper-time selection remains open.
- A53 records the one-atom heat profile as conditional.
- H4-T9 keeps positive repair distinct from a signed variational action.
- H4-T10 supplies a formal cyclic action class but not its selected physical
  instantiation on this finite source.

No authority currently promotes one of Sections 6-7 to the unique physical
action of `D_phys(t)`.

## 13. Frontier delta

Closed here:

```text
exact D0-H factorization:                         closed;
independence of CBF.T26 remainder R:              removed;
joint spectrum of H_phys and R:                   closed;
full signed and squared 96D spectra:              closed;
all scalar even spectral functionals:             reduced to (1.3);
profile-independent polynomial selection:         ruled out;
profile-independent heat selection:               ruled out;
new fitted or observed inputs:                    zero.
```

Still open:

```text
same-root selection of physical profile/action:   open;
signed Lorentzian/cyclic/BV physical action:       open;
dimensionful Higgs vacuum h:                       open;
strict family magnitudes and mixing:               open;
held-out scalar prediction:                        open;
B.ACTION.01 and B.SM.02:                           open.
```

The next theorem should no longer search the same finite spectrum for a
profile-free magic coordinate. It must derive one of the following upstream:

```text
nonlinear closure-repair generator
  -> selected linearized/cyclic action profile;

selected positive fluctuation Hessian plus statistics
  -> normalized log-determinant action and chamber;

selected proper-time measure
  -> one exact heat profile;

typed fermionic/BV action
  -> orientation-sensitive value equations.
```

Only after that selection is made independently may a stationary coordinate
be tested as a physical value.

## 14. Claims and nonclaims

### Proved

- the exact factorization (1.1);
- `R=H_phys^2/4`, so the T26 remainder is not independent;
- the exact joint response spectrum and all multiplicities;
- the complete signed and squared spectra of `D_phys(t)`;
- the universal scalar spectral formula (1.3);
- exact stationary equations for four named profiles;
- absence of a profile-independent polynomial stationary coordinate;
- absence of a coordinate stationary for every heat profile; and
- the distinction between the closure basepoint and a physical magnitude.

### Not proved

- that any compared profile is the selected physical MTT action;
- a nonzero physical value of `t` or `h`;
- a measured Yukawa magnitude, mass, mixing angle or CP phase;
- a physical determinant chamber or proper-time atom;
- a signed Lorentzian action, complete BV/QME or quantum effective action;
- a held-out prediction; or
- closure of `B.ACTION.01` or `B.SM.02`.

## 15. Reproduction

```text
python build_finite_dirac_spectral_action_classification.py
python verify_finite_dirac_spectral_action_classification.py
python -m unittest tests.test_finite_dirac_spectral_action_classification -v
python verify.py
```

The generated packet is
`finite_dirac_spectral_action_classification.packet.json`.
