# Source-Preserving Pointed Quantum Projection and Ward Nonselection Theorem v1

**Claim:** CBF.T40

**Date:** 2026-08-30

**Status:** exact classification of the finite radial Stueckelberg-Petermann
orbit; exact no-go showing that QME, gauge Ward, Action Ward, field
independence, split/background Ward and perturbative-agreement requirements do
not by themselves select the T39 anchor; exact theorem showing that one
source-preserving pointed quantum projection forces QJ1 and the action-jet
part of QJ2 and hence selects the unique nonconstant T39 representative;
existence of a selected physical projection, the physical tangent metric,
gravitational QJ0 and the physical q79 endpoint remain open.

## 1. Result

The T35-T39 sequence left a precise question. The local-formal renormalized
action admits the complete gauge-even radial counterterm class

```text
C(h)=c+a h^2+b h^4.                                  (1.1)
```

The T39 anchor chooses one representative by preserving value, slope and
Hessian at the selected point `H>0`. The missing issue was whether ordinary
quantum identities select that representative, or whether the rule follows
from the stronger statement that the quantum theory is the projection of the
same selected upper source.

This paper proves four statements.

1. QME and the usual Ward or perturbative-agreement requirements do not
   select `(c,a,b)`.
2. QJ1 alone leaves exactly one nonconstant scheme direction.
3. QJ1 together with source-preserving tangent-action data kills that last
   direction and reproduces the unique T39 pair.
4. The remaining task is one structural existence theorem for a selected
   source-preserving quantum projection, not another search for radial
   counterterm numbers.

This is a strict advance in the classification of the blocker. It is not a
claim that the required physical projection has already been constructed.

## 2. Exact finite counterterm orbit

Modulo the additive constant, write a finite scheme displacement as

```text
C_(a,b)(h)=a h^2+b h^4.                              (2.1)
```

Its first two derivatives at `H` are

```text
C_(a,b)'(H) =2aH+4bH^3,
C_(a,b)''(H)=2a+12bH^2.                              (2.2)
```

The corresponding matrix is

```text
M_H=[[2H,4H^3],[2,12H^2]],
det M_H=16H^3.                                       (2.3)
```

Since `H>0`, `M_H` is invertible.

### Theorem 2.1: QJ1 orbit

The QJ1 condition `C'(H)=0` has rank one and leaves the line

```text
(a,b)=(-2H^2 t,t),
C_t(h)=t(h^2-H^2)^2 mod constants.                   (2.4)
```

On this line,

```text
C_t''(H)=8H^2 t.                                     (2.5)
```

Therefore QJ1 does not imply QJ2. QJ1 plus equality of the action Hessian at
`H` forces `t=0`. The only surviving finite scheme displacement is a
constant. If normalized connected QFT quotients common constants, there is no
remaining physical radial scheme freedom. If gravity is included, QJ0 must
still select that constant.

### Corollary 2.2: unique correction of an arbitrary two-jet

If a raw loop has slope and Hessian differences `(b1,b2)` at `H`, the unique
nonconstant counterterm with that two-jet is

```text
a=(3b1-Hb2)/(4H),
b=(Hb2-b1)/(8H^3).                                   (2.6)
```

This is exactly the nonconstant part of the T39 retraction. No new choice has
been introduced.

## 3. Why the standard quantum identities do not select it

The q79 QME calculation proves that the nontrivial ghost-one anomaly class is
zero and that a compatible local formal prescription exists. The same result
retains local Stueckelberg-Petermann freedom. The counterterms (1.1) are
gauge-invariant, ghost-zero and antifield-free. In the declared radial sector
their self BV bracket and BV Laplacian vanish. Consequently QME compatibility
does not select their finite coefficients.

The same counterexample applies to the gauge Ward identity, field
independence and the Action Ward identity. These conditions are shared by two
renormalized prescriptions related by an allowed local finite map. For
example, `C(h)=a h^2` shifts the tadpole by `2aH` while remaining an invariant
local functional.

A split or background Ward identity also does not suffice. Any
`C(h_total)` depending only on the total field obeys the split identity but
can shift both derivatives in (2.2).

The principle of perturbative agreement compares two splittings of one fixed
total action. Both `S` and `S+C` may separately obey that comparison. It does
not identify the two total actions and therefore cannot force `C'(H)=0` or
`C''(H)=0` at a point selected by an upstream theory.

Costello's on-shell-background statement removes the linear term in the
classical expansion. It does not remove the quantum tadpole in every finite
renormalization scheme. T35 supplies an explicit witness: at `mu=Lambda` its
unmatched fermion determinant has

```text
V_F'(H)/(kappa_F Lambda^3)
=-100.1144836274302795882555068876968... !=0.        (3.1)
```

Thus none of these identities alone proves QJ1, and QJ1 alone still leaves
the direction (2.4).

## 4. Source-preserving pointed quantum projection

Let an upper selected source contain a fixed point `u_*`, repair vector field
`X_up`, tangent generator `A_up`, action and selected tangent pairing. Let the
lower renormalized effective action be `Gamma`, with positive radial tangent
metric `g_H` and repair field

```text
X_Gamma=-g_H^(-1)dGamma.                              (4.1)
```

A pointed quantum projection `Pi` is source-preserving at the two-jet tier
when it has the following properties.

```text
SP0  one root provenance and no observed target used as source data;
SP1  Pi(u_*)=H;
SP2  DPi X_up(u_*)=X_Gamma(H);
SP3  DPi A_up=A_Gamma DPi on the selected tangent image;
SP4  DPi is an isometry for the selected tangent pairings;
SP5  the BV/QME and normalized state pushforwards commute with Pi.
```                                                     (4.2)

`SP2` and `SP3` are pointed statements. T39 proves that equality of the full
nonlinear radial flows is too strong and is not required here.

### Theorem 4.1: pointed projection selection

If (4.2) holds, then QJ1 and the action-jet part of QJ2 hold.

### Proof

Because `u_*` is fixed, `X_up(u_*)=0`. Equations `SP1-SP2` give

```text
X_Gamma(H)=DPi X_up(u_*)=0.                           (4.3)
```

The radial metric is positive and invertible, so (4.1) implies

```text
dGamma(H)=0.                                         (4.4)
```

This is QJ1. Differentiating the pointed vector-field relation and using
`SP3-SP4` transports the tangent generator and the action Hessian. Hence

```text
I_H^* Hess Gamma(H) I_H=Hess S_up(u_*)                (4.5)
```

in the selected normalized tangent coordinate. This is the action-jet part
of QJ2. Theorem 2.1 then forces `t=0` in (2.4), so the nonconstant finite
Stueckelberg-Petermann representative is unique. Equation (2.6) gives its
coefficients. QED.

## 5. Relation to the provider-neutral contract

The provider-neutral source schema already requires:

```text
fixed_point_hessian_identity,
action_bv_pushforward,
normalization_and_interaction_source,
one_root_hash_for_all_packets.                        (5.1)
```

Its source-preserving equivalence relation transports `u_*`, `K`, the action,
the density and the cyclic pairing. Theorem 4.1 is the local quantum
specialization of those data types. It proves:

> A lower effective action cannot be called the projection of the same
> selected source while choosing an arbitrary point or Hessian from the
> finite orbit (1.1).

Consequently QJ1 and action-jet QJ2 are not two independent numerical knobs
inside a completed same-source projection. They are two consequences of one
structural morphism certificate.

The current repository does not contain an accepted physical instance of the
provider-neutral source schema. Thus (5.1) is a contract-level selector, not
an existence proof for nature's q79 realization.

## 6. Equivalent radial-state route

T38 proves that the selected upper radial repair law has the unique invariant
radial probability `delta_H`. A full gauge/matter state need not be unique for
the following scalar implication.

If the physical quantum projection pushes the upper invariant radial state to
the lower zero-source state, then the lower radial expectation is `H`. The
Legendre identity

```text
dGamma/dh=J                                           (6.1)
```

at `J=0` gives `Gamma'(H)=0`. This is again QJ1. The missing datum is the
selected state pushforward itself, not another radial expectation value.

## 7. Exact T35 execution

For the T35 one-loop determinant, the unique source-preserving nonconstant
counterterm is

```text
delta m2    =-2 kappa_F q4_* H^2,
delta lambda=kappa_F[L_H+(3/2)q4_*].                  (7.1)
```

Every QJ1-compatible alternative is

```text
delta m2(t)    =delta m2-2 kappa_F H^2 t,
delta lambda(t)=delta lambda+kappa_F t.               (7.2)
```

It changes the Hessian by

```text
Delta Gamma''(H)=8 kappa_F H^2 t.                    (7.3)
```

At the current finite source point,

```text
H^2/Lambda^2 =1.7453095151385177185351833627423...,
-2H^2/Lambda^2=-3.4906190302770354370703667254847...,
 8H^2/Lambda^2=13.9624761211081417482814669019386....
```

Therefore the last QJ1 direction is decisively non-flat in the action
Hessian and is removed by one same-source tangent certificate. The exact
T35 remainder and all higher nonlinear quantum vertices remain unchanged.

## 8. Parameter and acceptance ledger

This theorem introduces:

```text
new continuous physical parameters: 0,
new discrete physical selectors:    0,
observed inputs or fits:             0,
new structural existence obligation: 1 source-preserving pointed projection.
```

It replaces two apparently separate scalar matching requirements by one
typed morphism obligation. It does not construct that morphism, select the
physical tangent metric, or promote the endpoint counters. Therefore

```text
physical packets accepted: 0/3,
physical rows accepted:    0/7.                       (8.1)
```

For normalized nongravitational QFT, a common additive constant is quotiented.
For gravity, QJ0 remains an independent determinant-line or vacuum-energy
problem.

## 9. External context

The generalized principle of perturbative agreement is explicitly a
renormalization condition comparing equivalent free/interacting splittings
of one total theory; it is not a vacuum-selection theorem:

- https://arxiv.org/abs/1502.02705

The existence of distinct consistent tadpole and VEV schemes in Standard
Model perturbation theory is external evidence for the same nonselection
boundary:

- https://arxiv.org/abs/2010.15076
- https://arxiv.org/abs/2203.07236
- https://arxiv.org/abs/1907.02500

These references support the classification of scheme freedom. They do not
prove the MTT source-preserving projection theorem, which is the exact
argument in Sections 2 and 4.

## 10. Frontier after T40

Closed here:

- the exact QJ1-preserving finite counterterm orbit;
- the exact `8H^2 t` Hessian obstruction on that orbit;
- nonselection by QME, ordinary Ward identities, split Ward and perturbative
  agreement alone;
- derivation of QJ1 and action-jet QJ2 from one source-preserving pointed
  quantum projection;
- uniqueness of the T39 nonconstant representative under that contract; and
- reduction from separate scalar matching clauses to one structural morphism
  certificate.

Still open:

- construction and selection of the physical q79 pointed quantum projection;
- a selected physical tangent metric or wave-function normalization;
- a preferred interacting state or equivalent radial Ward primitive;
- the fixed-coupling interacting BV pushforward and continuum transfer;
- gravitational QJ0, RG/matching, pole transport and held-out observables.

The next sharp target is therefore not another finite counterterm search. It
is an existence theorem for the same-root state/action projection map in
(4.2), with a selected tangent pairing.
