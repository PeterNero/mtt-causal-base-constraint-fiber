# Finite Dirac Operator-Space Repair Hessian, Semigroup and Profile Boundary Theorem v1

**Claim:** CBF.T28

**Date:** 2026-08-29

**Status:** exact full operator-space Hessian and same-root repair semigroup;
the repair profile is selected, while the signed physical action and scalar
spectral-action profile remain open.

## 1. Result

CBF.T26 selected the normalized positive closure functional

```text
C(D)=1/2 tau_96[(D^2-I96)^*(D^2-I96)]
```

and evaluated its pullback to the finite family `D_phys(t)=D0+tD1`. CBF.T27
then proved that the finite operator and normalized trace do not select a
scalar spectral profile `f` in

```text
tau_96 f(D_phys(t)^2).
```

The missing intermediate calculation is now exact. On the real Hilbert space
of self-adjoint `96 x 96` matrices, with normalized Hilbert-Schmidt metric,
the Frechet derivative of the closure defect at `D0` is

```text
J0(X)=D0 X+X D0.
```

Its repair Hessian is the superoperator

```text
A_rep=J0^* J0=J0^2=2(I+Ad_D0)=4 P_com,       (1.1)
```

where

```text
Ad_D0(X)=D0 X D0,
P_com =(I+Ad_D0)/2,
P_anti=(I-Ad_D0)/2.
```

Because `D0` has `+1` and `-1` multiplicities `48,48`, both real sectors have
dimension `4608`. Thus

```text
spec(A_rep)={0^4608,4^4608}.                (1.2)
```

The exact linearized negative-gradient repair semigroup is

```text
T_s=exp(-s A_rep)=P_anti+exp(-4s)P_com.     (1.3)
```

This closes the same-root exponential **repair** profile and instantiates the
general closure-Hessian-to-semigroup mechanism used by A84. It does not choose
the physical scalar profile `f(D_phys^2)`, because (1.3) acts on operator
perturbations in `End(H_F)`, whereas `R`, `H_phys^2` and `D_phys^2` act on
`H_F` itself.

## 2. Configuration space and metric

Let

```text
V_sa={X in M_96(C): X^*=X}
```

with real inner product

```text
g(X,Y)=Re tau_96(XY),       tau_96=Tr/96.
```

The normalization is the same unitary-invariant normalized trace selected in
CBF.T26. The base operator satisfies

```text
D0^*=D0,
D0^2=I96,
spec(D0)={-1^48,+1^48}.
```

The map `theta=Ad_D0` is an orthogonal involution on `V_sa`. Its two
orthogonal projectors are `P_com` and `P_anti`. They have the concrete
interpretations

```text
Ran(P_com) ={X:[D0,X]=0},
Ran(P_anti)={X:{D0,X}=0}.
```

In a basis where `D0=diag(I48,-I48)`, a commuting self-adjoint perturbation is
block diagonal, while an anticommuting self-adjoint perturbation is block off
diagonal. Therefore

```text
dim_R Ran(P_com) =48^2+48^2     =4608,
dim_R Ran(P_anti)=2*48*48       =4608.       (2.1)
```

No `9216 x 9216` matrix needs to be materialized: (1.1), the material
`D0` projectors and (2.1) determine the superoperator exactly.

## 3. Frechet derivative and Hessian

Write the defect map as

```text
F(D)=D^2-I96.
```

At `D0`, where `F(D0)=0`, its derivative in direction `X` is

```text
DF_D0[X]=D0X+XD0=J0(X).                    (3.1)
```

Cyclicity of the trace gives

```text
g(J0X,Y)=g(X,J0Y),
```

so `J0^*=J0`. The second-variation term containing `F(D0)` vanishes, and

```text
Hess_D0 C=J0^*J0.
```

Using `D0^2=I96`,

```text
J0^2(X)
 =D0(D0X+XD0)+(D0X+XD0)D0
 =2X+2D0XD0
 =4P_com(X).                                (3.2)
```

Hence the Hessian vanishes exactly on anticommuting directions and is four
times the identity on commuting directions. The nearby minimum manifold is
the unitary orbit of self-adjoint involutions. Its tangent is
`Ran(P_anti)`, while `Ran(P_com)` is the positive normal space. This is an
exact finite Morse-Bott decomposition.

## 4. Repair semigroup

The linearized negative-gradient equation is

```text
d_s X=-A_rep X.
```

Since `P_com P_anti=0`, functional calculus immediately gives (1.3). It obeys

```text
T_0=I,
T_s T_u=T_(s+u),
||T_s||<=1 for s>=0,
T_s X_anti=X_anti,
T_s X_com=exp(-4s)X_com.
```

On the complexification of the operator tangent, the entire continuation is

```text
T_z=P_anti+exp(-4z)P_com.
```

Its imaginary boundary is unitary. For example,

```text
T_(i pi/8)=P_anti-i P_com.
```

This analytic boundary is not by itself a physical Hamiltonian evolution.
It acts on complexified operator perturbations, and no theorem here identifies
its parameter with Lorentzian time or supplies the cyclic/BV pairing required
by `B.ACTION.01`.

## 5. Pullback to the selected one-parameter family

CBF.T27 proves

```text
[D0,D1]=0,
H_phys=2D0D1,
R=D1^2=H_phys^2/4.
```

Therefore `D1`, `H_phys` and `R` are all in `Ran(P_com)`, and

```text
A_rep(D1)=4D1,
A_rep(H_phys)=4H_phys,
A_rep(R)=4R.                                (5.1)
```

The induced metric on `D(t)=D0+tD1` is

```text
g_tt=g(D1,D1)=tau_96(D1^2)=tau_96(R)=2.
```

Consequently the scalar second variation is

```text
S_rep''(0)=g(D1,A_rep D1)=2*4=8,           (5.2)
```

exactly the number found in CBF.T26. The value `8` is a quadratic-form value
on the non-unit vector `D1`; it is not a conflicting superoperator
eigenvalue. With the induced metric, the constrained scalar gradient is

```text
d_s t=-(1/2)S_rep'(t)
     =-2t(3t^2-4t+2),
```

whose linear rate is `-4t`. Choosing the coordinate metric `dt^2` instead
gives the scalar rate `-8t`; that is a repair-time reparametrization.

## 6. The nonlinear affine family is not invariant

For a self-adjoint `D`, direct differentiation gives the full operator
gradient

```text
grad C(D)=2D(D^2-I96).                     (6.1)
```

On the three `H_phys` branches `h=-4,-2,+2`, write

```text
D(t)=D0(1+t h/2).
```

After dividing the branch gradient coefficient by `h`, the three ratios are

```text
r_h(t)=2t+(3/2)t^2 h+(1/4)t^3 h^2.
```

In particular,

```text
r_-2(t)-r_+2(t)=-6t^2.
```

All three branches have nonzero rank, so the full gradient can be parallel to
`D1` only when `t=0`. Thus the scalar T26 gradient is the constrained
projection of the full repair field onto the affine family. The affine family
is tangent to the full flow at closure, but it is not an invariant nonlinear
flow line away from closure.

This prevents a subtle overclaim: the full operator repair law does not
generate a nonzero scalar trajectory within the one-parameter Yukawa family.

## 7. Why the Hessian is not R or H_phys squared

The three objects have different types:

```text
A_rep:      End_sa(H_F) -> End_sa(H_F),
R:          H_F -> H_F,
H_phys^2:   H_F -> H_F.
```

Their exact spectra are

```text
spec(A_rep)={0^4608,4^4608},
spec(R)    ={1^64,4^32},
spec(H_phys^2)={4^64,16^32}.
```

Equation (5.1) says that `R` is an eigenvector of the superoperator
`A_rep`; it does not identify the two operators. Accordingly,

```text
exp(-s A_rep)=P_anti+exp(-4s)P_com
```

is not `exp(-sR)` and is not a scalar heat profile of `D_phys(t)^2`.
The normalized supertrace profile is simply

```text
Tr_End[exp(-sA_rep)]/9216=(1+exp(-4s))/2,
```

which contains no `t` and cannot select a Yukawa magnitude.

## 8. Reconciliation with A53, A84 and A85

**A84.** Its general fixed-point damping mechanism now has an exact same-root
CBF instance: the selected T26 functional and normalized Hilbert-Schmidt
metric emit `A_rep`, and `A_rep` emits (1.3). This closes the existence of the
exponential repair propagator for the CBF source.

**A53.** The value `tau_int=log(448)/15` belongs to a conditional one-atom
proper-time construction. No selected comparison map identifies that
parameter with `4s`, so neither `1/448` nor an absolute repair time is imported
here.

**A85.** Its finite spectral action has the form `Tr f(D_A^2)` on the finite
carrier. The present semigroup acts on the operator tangent. A trace over one
space cannot be silently substituted for a trace over the other. The primitive
physical profile remains open even though the repair semigroup is now derived.

## 9. Exact closure and remaining boundary

Closed exactly, with no observed inputs or fitted coefficients:

- the full Frechet defect derivative at `D0`;
- the full positive repair Hessian as a typed superoperator;
- its `4608+4608` tangent-normal spectral decomposition;
- its exact contraction semigroup and entire continuation;
- the reconciliation of the scalar Hessian `8` with normal eigenvalue `4`;
- the same-root application of the A84 semigroup mechanism; and
- the no-go against identifying this generator with `R`, `H_phys^2` or a
  scalar physical spectral-action profile.

Still open:

- a selected signed cyclic, BV or Lorentzian physical action;
- a physical action profile `f` on `D_phys^2`;
- an absolute map from repair time to `tau_int`, physical time or `hbar`;
- a selected nonzero value of `t` or `h`;
- a held-out mass, mixing, coupling or threshold prediction; and
- the commuting upper-to-lower action maps required by `B.ACTION.01`.

Physical q79 acceptance is unchanged:

```text
packets: 0/3,
rows:    0/7.
```

The frontier has nevertheless moved. The phrase "derive the heat profile from
repair" is no longer an open slogan for this finite source. It is theorem
(1.3). The remaining action blocker is now strictly the promotion from this
positive operator-space repair dynamics to a signed physical action and to a
typed scalar spectral profile on `H_F`.

## 10. Reproduction

```powershell
python build_finite_dirac_operator_repair_semigroup.py
python verify_finite_dirac_operator_repair_semigroup.py
python -m unittest tests.test_finite_dirac_operator_repair_semigroup -v
python verify.py
```

The generated packet is
`finite_dirac_operator_repair_semigroup.packet.json`.
