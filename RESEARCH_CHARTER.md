# Research Charter: Causal Base and Constraint Fiber

## 1. Hypothesis under test

Let `M` be a selected globally hyperbolic four-dimensional Lorentzian base. Let
`pi: E -> M` carry internal closure data. The working hypothesis is that:

1. causal propagation is indexed by regions of `M`;
2. vertical data in `E` encode admissibility, holonomy, gauge and repair;
3. physical configurations are selected fixed points, cohomology classes or
   coherent sections of the upper system;
4. physical observables are obtained through a typed reduction, not by treating
   every vertical coordinate as another spacetime direction.

The four-dimensional base is an input to this program until MTT derives it from
an upstream theorem. The charter does not count `3 x 3` comparison data as nine
manifold dimensions and does not identify the shared phase circle with time.

## 2. Minimal typed structure

A candidate realization must supply

```text
(M, g, causal order)
    Lorentzian causal base;

(H_U -> M, <.,.>)
    upper Hermitian Hilbert bundle or controlled field of Hilbert spaces;

F or C
    nonlinear closure-repair map or closure functional;

P = integral^oplus P_x
    decomposable orthogonal projector onto the retained tangent/coherent sector;

A_U(O)
    upper local operator net over base regions O;

Aut_M(H_U, F, P)
    vertical automorphisms preserving the source data and physical projector;

Ev
    typed evaluation or transfer map to physical observables.
```

For a fixed point `u_*`, the preferred route is

```text
closure repair F
  -> selected fixed point u_*
  -> linearization D F(u_*) or Hessian
  -> gapped spectral/tangent projector P
  -> compressed operators and transferred products
  -> physical records.
```

The current kernel contains a cohesive Maurer-Cartan repair benchmark and
tangent semigroup, but not yet the selected physical q79 action and endpoint.

## 3. What "constraint fiber" must mean

An internal direction may be classified as a constraint coordinate only after
all of the following are established on the declared domain:

1. it supplies no independent causal cone or clock;
2. it has no freely specifiable propagating initial data independent of the
   base evolution;
3. vertical relabelings preserving closure data are gauge or representational;
4. physical effects descend through fixed-point, spectrum, holonomy, index or
   transfer data;
5. the reduced local net remains microcausal on the base.

If vertical modes propagate independently, carry measurable energy, or produce
physical Kaluza-Klein towers, they are physical internal degrees of freedom and
must not be dismissed as mere coordinates.

## 4. Locality and global constraint

The intended distinction is:

- **interaction locality:** spacelike separated physical local algebras commute;
- **state nonfactorization:** a joint state need not factor across those algebras;
- **constraint dependence:** globally admissible sections can correlate local
  data without transmitting a controllable superluminal signal.

Entanglement is therefore not identified with nonlocal interaction. It remains
a property of a state on a joint algebra. A Bell-violating state and its local
instruments must still be selected or supplied.

## 5. Gauge interpretation

The candidate gauge group is the group of vertical automorphisms that preserves
the selected closure source, connection and physical reduction. MTT authority
`A47` separately establishes the low-energy group

```text
(SU(3) x SU(2) x U(1)) / Z6
```

from selected native bundle tensors at its structural tier. This repo may seek
an upstream stabilizer theorem for that result, but it may not rederive or
weaken `A47` by analogy alone.

## 6. Quantum interpretation

Compression can be nonmultiplicative. The first theorem in this repo measures
that defect exactly. This is enough to explain how commuting upper operators
*can* have noncommuting shadows, but it is not enough to derive quantum theory.

A physical quantization claim additionally requires:

- a selected `P` and selected observable pair from one MTT source;
- domains and self-adjointness for unbounded operators;
- a symplectic/action normalization fixing the scale called `hbar`;
- canonical commutation or a controlled limiting theorem;
- states, effects and instruments;
- the already separated probability and actualization obligations.

## 7. Promotion standard

Each proposed result must be labelled as one of:

- `EXACT_GENERAL`: proved under explicit mathematical assumptions;
- `EXACT_BENCHMARK`: exactly executed on a stated finite or analytic model;
- `CONDITIONAL_MTT`: applies if a selected MTT source supplies named inputs;
- `SELECTED_MTT`: all required source data are emitted from one accepted branch;
- `PHYSICAL_COMPARISON`: conventions, errors and held-out observables are given.

No result advances merely because a verifier passes. It must also change a
named kernel frontier truth value or discharge an exit clause.
