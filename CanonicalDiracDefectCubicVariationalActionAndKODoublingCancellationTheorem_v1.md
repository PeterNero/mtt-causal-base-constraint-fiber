# Canonical Dirac-Defect Cubic Variational Action and KO-Doubling Cancellation Theorem v1

**Claim:** CBF.T29

**Date:** 2026-08-29

**Status:** exact same-root signed finite variational action, signed Hessian and
normal-square bridge; exact KO6 odd-trace cancellation and canonical
two-anchor no-go; physical Lorentzian/BV action remains open.

## 1. Result

CBF.T26-T28 established the positive closure functional

```text
C(D)=1/2 tau96[(D^2-I96)^2]
```

and its operator-space Hessian

```text
A_rep=J0^*J0=J0^2=4P_comm.
```

The signed source behind that normal square is now exact. On the real vector
space of self-adjoint `96 x 96` matrices, define

```text
S_sig(D)=tau96(D^3/3-D).                    (1.1)
```

Then

```text
dS_sig(D)[X]=tau96[(D^2-I96)X],             (1.2)
grad S_sig(D)=D^2-I96.                      (1.3)
```

Thus `S_sig` is the direct H4-T9 variational anchor for the CBF closure
residual. It needs no multiplier field and no fitted coefficient. Its Hessian
at the closure basepoint is precisely

```text
H_sig=J0,             J0(X)=D0X+XD0,        (1.4)
H_sig^2=A_rep.                              (1.5)
```

The signed inertia is

```text
inertia(H_sig)=(2304 positive,2304 negative,4608 zero).   (1.6)
```

This closes the finite signed-action-to-repair-square bridge. It does not yet
give a physical action, because the KO6 grading forces

```text
S_sig(D_phys(t))=0 for every real t.         (1.7)
```

Indeed every odd scalar trace of the selected Dirac family vanishes. The
finite signed action exists, but the doubled odd spectrum cancels its scalar
pullback exactly.

## 2. Direct variational anchor

Let

```text
V_sa={D in M_96(C):D^*=D},
g(X,Y)=Re tau96(X^*Y),
tau96=Tr/96.
```

For a self-adjoint variation `X`, cyclicity gives

```text
d tau96(D^3)[X]
 =tau96(XD^2+DXD+D^2X)
 =3tau96(D^2X).
```

Subtracting `tau96(X)` proves (1.2). The residual one-form is therefore
globally exact, so its Helmholtz condition is automatic. Because `V_sa` is
connected, any differentiable scalar functional with gradient `D^2-I96`
differs from (1.1) by an additive constant. Requiring `S(D0)=0` fixes that
constant, since `D0^2=I96` and `tau96(D0)=0`.

The action is conjugation invariant:

```text
S_sig(UDU^*)=S_sig(D),       U in U(96).
```

It is signed and unbounded. It is not the positive repair functional and is
not being called a Lorentzian or BV action.

## 3. Exact critical locus

Nondegeneracy of the Hilbert-Schmidt pairing gives

```text
Crit(S_sig)={D in V_sa:D^2=I96}.             (3.1)
```

This is exactly the closure locus, not merely a set containing it. By
contrast, the full gradient of the positive repair cost is

```text
grad C(D)=2D(D^2-I96),
```

which also vanishes on operators having zero eigenvalues. For example,

```text
grad C(0)=0,
grad S_sig(0)=-I96.
```

The signed action therefore retains the first-order closure equation that the
normal square partially forgets.

## 4. Signed Hessian and exact inertia

At any `D`, differentiating (1.3) gives

```text
J_D(X)=DX+XD.
```

This operator is self-adjoint for `g`. At `D0`, set

```text
E_plus =(I96+D0)/2,
E_minus=(I96-D0)/2.
```

Both material projectors have rank `48`. Define three orthogonal
superprojectors:

```text
Pi_plus(X) =E_plus X E_plus,
Pi_minus(X)=E_minus X E_minus,
Pi_zero(X) =E_plus X E_minus+E_minus X E_plus.
```

They resolve the self-adjoint operator tangent and obey

```text
J0=2Pi_plus-2Pi_minus,
J0 Pi_zero=0.                               (4.1)
```

The real dimensions are

```text
dim Pi_plus =48^2=2304,
dim Pi_minus=48^2=2304,
dim Pi_zero =2*48*48=4608.
```

Equation (1.6) follows. Squaring (4.1) gives

```text
J0^2=4(Pi_plus+Pi_minus)=4P_comm=A_rep,     (4.2)
```

which is the exact CBF.T28 Hessian, not merely an isospectral operator.

## 5. Morse-Bott zero modes and automorphisms

The basepoint component of (3.1) is the unitary orbit

```text
O_D0={UD0U^*:U in U(96)}
    =U(96)/(U(48) x U(48)).
```

For a skew-adjoint `K`, its tangent is `[K,D0]`, which anticommutes with
`D0`. Conversely, if `X` is self-adjoint and anticommutes with `D0`, then

```text
K=(1/2)XD0
```

is skew-adjoint and `[K,D0]=X`. Therefore

```text
T_D0 O_D0=Ran(Pi_zero)=ker J0.              (5.1)
```

The action is Morse-Bott at this orbit: its normal Hessian is nondegenerate
with equal positive and negative dimensions. Conjugation transports all
structures exactly:

```text
F(UDU^*)=U F(D) U^*,
J_(UDU^*) Ad_U=Ad_U J_D,
S_sig(UDU^*)=S_sig(D).
```

This closes automorphism and zero-mode compatibility at the finite
operator-space action tier. It is not the continuum q79 automorphism-transfer
certificate required by the full `B.ACTION.01` exit.

## 6. KO6 cancellation on the selected family

CBF.T23 supplies a self-adjoint grading `Gamma96` with

```text
Gamma96^2=I96,
Gamma96 D_phys(t) Gamma96=-D_phys(t)
```

for the complete affine family. Hence, for every nonnegative integer `m`,

```text
tau96[D_phys(t)^(2m+1)]
 =tau96[Gamma96 D_phys(t)^(2m+1) Gamma96]
 =-tau96[D_phys(t)^(2m+1)]
 =0.                                        (6.1)
```

Equation (1.7) follows immediately. The CBF.T27 joint spectrum gives the same
result explicitly: each `H_phys` branch `h=-4,-2,+2` occurs with both `D0`
signs at multiplicity `16`, so every odd branch contribution cancels pairwise.

For the selected tangent `D1`,

```text
||Pi_plus D1||^2=1,
||Pi_minus D1||^2=1.
```

Therefore

```text
g(D1,J0D1)=2-2=0,                           (6.2)
g(D1,J0^2D1)=4+4=8.                         (6.3)
```

The signed quadratic variation cancels while the positive repair stiffness
adds. This is the exact finite mechanism behind the action-versus-repair
difference on the physical family.

## 7. Canonical D0-weighted escape test

The basepoint suggests a seemingly natural way to avoid cancellation:

```text
S_0(D)=tau96[D0(D^3/3-D)]+2/3.              (7.1)
```

This action is normalized by `S_0(D0)=0`. Its gradient is

```text
G_0(D)
 =(D^2D0+DD0D+D0D^2)/3-D0,                 (7.2)
```

not `D0(D^2-I96)` away from the commutant of `D0`. Its Hessian at `D0` is

```text
K_0=(4I+2Ad_D0)/3
   =2(Pi_plus+Pi_minus)+(2/3)Pi_zero.        (7.3)
```

Thus it lifts the `4608` orbit zero modes and does not square to `A_rep`.
It is invariant only under the stabilizer of `D0`, not under full `U(96)`
conjugation.

On the commuting affine family it is nonzero:

```text
S_0(D_phys(t))=2t^2-(8/9)t^3.               (7.4)
```

But the additional constrained stationary point `t=3/2` is not a full
closure point. This weighted trace is therefore a useful diagnostic, not a
physical value selector.

## 8. Exact two-anchor classification

Consider the minimal same-root cubic class

```text
S_(a,b)=a S_sig+b S_0.
```

Its Hessian eigenvalues on `(Pi_plus,Pi_minus,Pi_zero)` are

```text
2(a+b), 2(-a+b), 2b/3.                      (8.1)
```

Requiring its Hessian square to equal `A_rep` gives

```text
(a+b)^2=1,
(-a+b)^2=1,
b=0.
```

Hence

```text
(a,b)=(+1,0) or (-1,0).                     (8.2)
```

But the affine-family pullback is

```text
S_(a,b)(D_phys(t))=b[2t^2-(8/9)t^3].        (8.3)
```

Every member that preserves the complete T28 normal square therefore
cancels identically on the selected family. Every noncancelling member has
`b != 0`, breaks the orbit zero-mode structure and changes the full residual.

This no-go is scoped to the canonical two-anchor class emitted by `I` and the
selected basepoint `D0`. It does not forbid a physical spinor bilinear, a
BV/cyclic density or a source-selected noncentral pairing. It proves that any
such escape is real additional structure, not hidden inside T26-T28.

## 9. Pairing and physical-action boundary

A linear functional `ell_W(X)=tau96(WX)` is invariant under every unitary
change of basis only when `W` is scalar. Normalization then recovers
`W=I96`, whose odd trace cancels by Section 6. A noncentral weight can avoid
that cancellation only after a smaller symmetry, polarization or density has
been selected.

The existing CBF.T25 fermionic action uses spinor fields,

```text
integral <bar(psi),D_dir psi> dvol,
```

not a scalar odd trace over `H_F`. Its classical fermion/Yukawa BV sublane is
therefore unaffected. Conversely, (1.1) cannot be relabeled as that action:
its field is the operator `D`, it has no Lorentzian principal symbol, and its
pullback to the selected finite family vanishes.

The minimal next datum is consequently one of:

1. a selected spinor/BV pairing and density whose finite reduction retains
   the required signed response without odd-trace cancellation;
2. a selected quotient or polarization that justifies discarding the
   cancelling partner while preserving gauge, real and anomaly structures;
3. a noncentral cyclic anchor with a proved source origin and reduced
   automorphism group; or
4. a different signed upper action whose compactification produces both the
   CBF finite response and the accepted four-dimensional action.

## 10. Relation to H4-T9, H4-T10 and H4-T15

**H4-T9.** The direct variational branch is now instantiated exactly for the
CBF residual. No universal multiplier is needed at this finite lane.

**H4-T10.** Equation (1.1) is a finite trace-cubic transgression, but it is not
the q79 holomorphic Maurer-Cartan action. Equality would require a typed
source map and cyclic pairing comparison.

**H4-T15.** A nonzero field-only finite action now exists before cotangent
completion. Nevertheless its relevant KO6 pullback is zero, and no theorem
reduces it to the accepted four-dimensional `S0`. The physical BV
compactification gate remains open.

**A84/A85.** The positive exponential repair profile remains the normal-square
shadow of this action. The even finite spectral action remains a separate
profile-tier object; it is not selected by the odd cubic primitive.

## 11. Exact boundary

Closed exactly:

- the unique normalized scalar action with gradient `D^2-I96`;
- its exact closure critical locus;
- the signed Hessian spectrum and Morse-Bott orbit zero modes;
- the identity `H_sig^2=A_rep`;
- full finite conjugation covariance;
- all-odd-trace cancellation on the KO6 finite family;
- the exact `0` versus `8` signed/repair pullback comparison; and
- the canonical two-anchor noncancellation-versus-normal-square no-go.

Still open:

- a selected physical Lorentzian, cyclic or BV action for the complete source;
- the physical pairing, density, real slice and compactification map;
- a nonzero physical value of `t` or `h`;
- absolute normalization relative to `hbar`;
- held-out masses, mixings, couplings or threshold predictions; and
- the continuum action/automorphism transfer required by `B.ACTION.01`.

Physical q79 acceptance remains

```text
packets: 0/3,
rows:    0/7.
```

The frontier has moved from "no signed source" to a sharper statement: the
canonical signed source exists and squares exactly to repair, but KO6 grading
makes its scalar finite-family shadow vanish. The next bridge must select the
physical pairing or polarization, not invent another scalar trace profile.

## 12. Reproduction

```powershell
python build_finite_dirac_cubic_variational_action.py
python verify_finite_dirac_cubic_variational_action.py
python -m unittest tests.test_finite_dirac_cubic_variational_action -v
python verify.py
```

The generated packet is `finite_dirac_cubic_variational_action.packet.json`.
