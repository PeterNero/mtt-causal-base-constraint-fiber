# Causal Relative Cauchy Evolution and State-Separated Global G0 Theorem v1

**Claim:** CBF.T44
**Date:** 2026-08-30
**Status:** exact state-free global causal evolution and unique minimal return
chain for the direct product-Dirac route; exact common-phase cancellation and
state-scalarization cutset; global scalar determinant, preferred state,
interacting cutoff removal, q79 HYM equivalence, G1 and full G2 remain open

## 1. Result

CBF.T43 derived the direct flat-background local one-loop action from the
actual T25 product-Dirac family. It left a global question:

```text
Which Lorentzian domain, integration cycle and determinant phase turn that
local expression into one physical global quantum action?
```

The question contains two different mathematical objects. They must not be
solved by pretending that they are one.

The first object is global causal evolution. T25 already supplies a
Green-hyperbolic Dirac-Yukawa family on the selected time-oriented globally
hyperbolic spacetime. Compactly supported changes of its order-zero Higgs or
Yukawa endomorphism therefore have advanced and retarded Moller maps. Their
relative Cauchy evolution acts on the solution space and, by the CAR universal
property, on the representation-independent observable algebra. It requires
no vacuum, determinant line, Wick rotation or path-integral cycle.

The local-formal interacting version is the relative S-matrix. At the T43
anchor H, define

```text
C_H[V_plus,V_minus]
  =S_H[V_minus]^{-1} star S_H[V_plus].               (1.1)
```

This is an algebra element before any state is chosen. It has exact return
normalization

```text
C_H[V,V]=1.                                          (1.2)
```

The minimal connected two-leg contour behind (1.1) is also forced once one
requires one normalized forward leg and an integral return chain. If e_plus
and e_minus are two copies of the same oriented interval, then

```text
partial(a e_plus+b e_minus)
  =(a+b)(t_f-t_i).
```

Closure and a=1 give b=-1 uniquely. Thus the minimal return chain is

```text
c_CTP=e_plus-e_minus.                                 (1.3)
```

No continuous contour coefficient has been introduced.

The second object is a scalar quantum functional. For a normalized state
omega,

```text
Z_omega[V_plus,V_minus]
  =omega(C_H[V_plus,V_minus]).                        (1.4)
```

Equation (1.2) implies Z_omega[V,V]=1 for every normalized state, but it does
not select omega. An exact two-state witness below gives different values for
the same unequal-source operator. Therefore a global scalar determinant or
in-in functional cannot be extracted from the return identity alone.

This changes the frontier. The direct route now has a state-free global
causal object with exact domain, composition and return. A common central
U(1) determinant phase cancels from (1.1), and no integration cycle is needed
to define the algebra element. What remains is not an unspecified global
domain/cycle/common-phase package. It is the selected scalarization of this
operator, including the relative phase, interacting state and renormalized
cutoff removal. That remaining problem is shared with G2.

## 2. Typed source data

The construction uses four established tiers.

### 2.1 Direct causal operator

T25 supplies

```text
D_h=D_dir(t;A,h)=D_A+Y_t(h)
```

on

```text
C_c^infinity(Y4,S_Y tensor E_F),
```

where Y4 is globally hyperbolic and time oriented. The principal symbol is

```text
sigma_Dh(x,xi)=i Clifford_g(xi) tensor I96.
```

Changing h changes only lower-order terms, so every D_h is Green hyperbolic.

### 2.2 Local-formal quantum algebra

The q79 renormalized time-ordering theorem and T39 supply local-formal
time-ordered products satisfying causal factorization, unitarity and the QME
at each finite perturbative order. They define

```text
S(V)=T_ren exp(iV/hbar),
```

and relative S-matrices in the microcausal algebra. This is a formal series.
No nonperturbative convergence or interacting cutoff removal is asserted.

### 2.3 Representation-independent free state space

The framed q79 free Dirac CAR certificate supplies the even observable net and
a nonempty convex space of positive normalized quasifree Hadamard states. It
explicitly does not select a preferred state. The binary-root theorem proves
that the two balanced-root presentations give naturally equivalent free CAR
nets and corresponding Hadamard/GNS state spaces.

### 2.4 Local one-loop shadow

T43 supplies

```text
kappa_F=1/(2 pi^2),
Delta V_cl(h)=q4_* H^4 rho(h/H)/(2 pi^2),
q4_*=(356+25sqrt(13))/27.                             (2.1)
```

This is a same-source local flat-background one-loop result. T44 retains it
as the anchored local reference. It does not infer that (2.1) is the complete
global expectation (1.4) in every Hadamard state.

## 3. Global Moller maps

Fix the anchor operator D_H and let

```text
D_h=D_H+V_h,
```

where V_h is a compactly supported smooth order-zero endomorphism. Let E_H^+
and E_H^- be the advanced and retarded Green maps of D_H, and similarly for
D_h. For either support choice, the resolvent identities are

```text
E_h=E_H-E_h V_h E_H
   =E_H-E_H V_h E_h.                                  (3.1)
```

Define

```text
M_h=1-E_h V_h,
N_h=1+E_H V_h.                                       (3.2)
```

### Theorem 3.1: exact Moller inverse

On the natural compact-support and solution quotients,

```text
M_h N_h=N_h M_h=1.                                   (3.3)
```

Moreover M_h sends D_H-solutions to D_h-solutions with the selected advanced
or retarded support.

### Proof

Multiplying (3.1) on the right by V_h gives both

```text
E_h V_h=E_H V_h-E_h V_h E_H V_h,
E_h V_h=E_H V_h-E_H V_h E_h V_h.
```

Substitution into the two products in (3.3) cancels every nonidentity term.
For D_H phi=0,

```text
D_h M_h phi
 =D_h phi-D_h E_h V_h phi
 =V_h phi-V_h phi
 =0.
```

The Green-map support property gives the causal support statement. QED.

Using the advanced and retarded maps separately gives the relative Cauchy
evolution

```text
rce_h=(M_h^-)^{-1} M_h^+.                             (3.4)
```

For a formally self-adjoint Dirac family it preserves the causal Cauchy form,
so the CAR universal property emits a star-automorphism of the even observable
algebra. This is state free. A state may be pulled back along the
automorphism, but no state is selected by the automorphism.

## 4. Relative S-matrix completion

At the local-formal interacting tier, anchor the renormalized relative
S-matrix by

```text
S_H[0]=1,
S_H[V]^*=S_H[V]^{-1}.                                (4.1)
```

Causal factorization is inherited from the selected time-ordered products.
The doubled element (1.1) is therefore defined in the same microcausal algebra
as the direct interaction. It obeys:

```text
equal-source return: C_H[V,V]=1,
adjoint reversal:    C_H[V_plus,V_minus]^*
                     =C_H[V_minus,V_plus],
anchor:              C_H[0,0]=1.                     (4.2)
```

These are algebra identities. They do not require a trace-class density
matrix or a Fock-space implementer.

For actual unitary implementers U[V] in any chosen representation, (1.1)
becomes

```text
C_H[V_plus,V_minus]=U[V_minus]^* U[V_plus],           (4.3)
```

which is the usual closed-time-path operator. Equation (4.3) is a
representation of the algebraic object, not its definition.

## 5. Unique minimal return chain

Let the cellular boundary matrix of two copies of the oriented interval be

```text
             e_plus e_minus
partial = [   -1      -1
               1       1 ].                          (5.1)
```

Its integral kernel is generated by (1,-1). Requiring the coefficient of the
forward leg to be +1 fixes the primitive generator, not merely its ray.

### Theorem 5.1: return-chain uniqueness

Among integral two-leg chains with one normalized forward traversal, the
only closed chain is c_CTP=(1,-1). Its coefficient norm is minimal and no
third leg or continuous contour weight is required.

### Proof

Equation partial(a,b)=0 is a+b=0. The normalization a=1 gives b=-1. The
solution is primitive because gcd(1,-1)=1. Any integer multiple with larger
norm violates the forward normalization. QED.

The theorem is conditional on the demand for a return contour. It does not
derive the time orientation, which T25 inherits from the selected causal
source, and it does not prove that primitive MTT requires an in-in contour for
every observable.

## 6. Phase classification

Let z be a central unit complex number and replace both contour legs by

```text
S_H[V_plus]  -> z S_H[V_plus],
S_H[V_minus] -> z S_H[V_minus].
```

Then

```text
(z S_H[V_minus])^{-1}(z S_H[V_plus])
 =C_H[V_plus,V_minus].                               (6.1)
```

Thus the common determinant-line U(1) torsor does not obstruct the normalized
relative operator. This is the precise common-phase cancellation already
anticipated in T39.

A source-dependent relative phase does not cancel. If the plus leg alone is
multiplied by z(V_plus), then C_H is multiplied by that relative central
factor. Such a phase can encode a renormalization choice, spectral flow or
determinant-line holonomy. T44 neither discards it nor substitutes an internal
family holonomy for a Dai-Freed analytic determinant line.

Consequently:

```text
common phase:                 quotiented exactly,
relative phase/holonomy:      retained,
global anomaly trivialization: not proved.            (6.2)
```

## 7. Scalarization no-go

Let

```text
u=(3+4i)/5,
C=diag(u,conjugate(u)).                               (7.1)
```

C is unitary. On M_2(C), take the positive normalized states

```text
omega_0(A)=A_00,
omega_1(A)=A_11,
omega_mix(A)=Tr(A)/2.
```

Then

```text
omega_0(C)=(3+4i)/5,
omega_1(C)=(3-4i)/5,
omega_mix(C)=3/5.                                    (7.2)
```

All three states give 1 on the equal-source element I_2. Hence unitarity,
equal-source return, causal composition and normalization do not select a
scalar value for an unequal-source contour element.

### Theorem 7.1: state-separation cutset

There is no state-independent map from the operator identities (4.2) to one
global scalar functional (1.4). Any such scalarization must supply a state or
an equivalent boundary/initial-condition functional.

### Proof

The same admissible unitary C in (7.1) has the three distinct normalized
positive values (7.2). A rule using only C and the identities (4.2) cannot
distinguish the three states because all satisfy those identities. Therefore
the state is additional typed data. QED.

This is not a claim that measurement creates the state. A state is the
functional used to evaluate the already defined observable evolution. The
physical process represented by a detector belongs inside the interaction;
it does not convert the abstract algebra identity into a preferred cosmic
state.

## 8. Relation to T43

T43's coefficient kappa_F and exact rho remainder remain proved. T44 changes
their interpretation at the global boundary:

```text
T43: local anchored one-loop determinant shadow,
T44: global state-free causal relative evolution,
G2:  selected scalar state/BV pushforward.            (8.1)
```

The Hadamard condition fixes the universal short-distance singular class, so
the local UV coefficient is not an arbitrary vacuum fit. Different Hadamard
states can nevertheless differ by smooth contributions and therefore change
finite global expectation values. T44 consequently preserves T43 as the
selected local reference but does not declare its complete rho potential to
be the full global in-in action for every state.

The correct future comparison is

```text
local expansion of log Z_omega around H
  versus
T43 local jets,                                      (8.2)
```

after omega and the interacting renormalized transport are selected. It is
not equality of a Euclidean determinant and a Lorentzian evolution operator
by notation alone.

## 9. Shared circle and binary root

The internal shared circle and the physical return contour remain different
objects.

The q79 shared-circle certificate proves that an odd proto-state acquires -1
on one internal halfturn and returns to +1 after two. It also proves that this
double return alone does not select a metric, zero strain or a physical
vacuum. The contour chain (1.3) instead duplicates a noncompact Lorentzian
time interval with opposite orientation. T44 uses the internal result only as
a compatibility comparison.

Therefore T44 does not assert

```text
S1_shared = physical time,
internal double return = primitive selection of the CTP contour.
```

The binary-root CAR theorem identifies the two balanced-root free observable
nets by a natural unitary. T24 additionally proves that the direct Yukawa
family is root neutral. Naturality transports the relative evolution under
that unitary. Thus T44 introduces no new +i/-i root selector at this direct
root-neutral tier. This does not prove root neutrality for an unconstructed
odd root-charged interaction.

## 10. Gate ledger

After T44:

```text
direct local one-loop G0:                 closed by T43,
direct global state-free causal evolution: closed by T44,
minimal return chain:                     closed conditional on return,
common central determinant phase:         cancelled exactly,
global scalar physical G0:                open,
relative determinant phase/holonomy:      open,
selected interacting state/BV G2:         open,
physical tangent metric G1:               open,
q79 HYM universality:                     open.       (10.1)
```

The physical T41 gate count remains 0/3 because its G0 equation asks for a
scalar BV pushforward from the selected source, not only an algebra-valued
relative evolution. The conceptual ordering has changed, however. The global
scalar part of G0 and the selected-state part of G2 must now be solved
together. Repeating a search for an independent common phase or arbitrary
integration cycle would move backward.

## 11. Parameter ledger

T44 introduces:

```text
observed values:                     0,
fitted coefficients:                 0,
new continuous physical parameters: 0,
new binary-root selectors:           0,
new preferred-state selectors:       0,
contour coefficient candidates:      unique primitive (1,-1).
```

The forward time orientation is inherited source data, not a newly derived
number. A future physical state may contain genuine boundary information; T44
does not prejudge whether MTT selects it uniquely or leaves a small discrete
or continuous state family.

## 12. External mathematical context

Brunetti, Fredenhagen and Verch formulate relative Cauchy evolution as the
state-free automorphic response of a locally covariant QFT satisfying the
time-slice axiom (`arXiv:math-ph/0112041`). Sanders constructs the free Dirac
field representation independently and proves that its relative Cauchy
evolution has the expected stress-energy response (`arXiv:0911.1304`).

Brunetti and Fredenhagen construct local perturbative interacting QFT on
globally hyperbolic spacetimes by causal microlocal renormalization
(`arXiv:math-ph/9903028`). Haehl, Loganayagam and Rangamani describe the
closed-time-path unitarity identities and their BRST organization
(`arXiv:1610.01940`). Dai and Freed show why global determinant phase is a
determinant-line/eta-invariant problem rather than a scalar sign convention
(`hep-th/9405012`). Capoferri and Murro construct global Lorentzian Dirac
propagators and Hadamard covariances (`arXiv:2201.12104`).

These sources support the mathematical object types used here. They do not
prove that MTT selects a particular interacting state or q79 HYM endpoint.

## 13. Reproduction

Run

```text
python build_causal_relative_cauchy_evolution_global_g0.py
python verify_causal_relative_cauchy_evolution_global_g0.py
python -m unittest tests.test_causal_relative_cauchy_evolution_global_g0 -v
```

The builder hash-checks every construction and comparison source, verifies
the Moller resolvent identities, solves the integral return chain, executes
common-phase cancellation, evaluates the three exact states, preserves the
T41 gate counters and emits the machine-readable T44 packet. The independent
verifier recomputes those results without importing the builder.
