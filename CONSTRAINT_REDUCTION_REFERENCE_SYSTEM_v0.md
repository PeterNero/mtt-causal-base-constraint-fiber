# Constraint-Reduction Reference System v0

## Purpose

MTT currently uses several successful but differently presented languages:
fixed points, coherent projectors, bundle automorphisms, spectral triples,
Hodge transfer, qutrit finite operators, AQFT nets, HYM geometry and effective
physical profiles. The proposed reference system asks whether these can be
organized as views of one preprojection object.

This document is a candidate specification. It is not a theorem.

## 1. Candidate object

Define a constraint-reduction object

```math
\mathfrak C=
(M,g,E,\nabla,\mathcal F,u_*,D\mathcal F_{u_*},P,Q,
\widetilde{\mathcal A},\mathcal R).
```

The fields are typed as follows:

| Field | Role |
|---|---|
| `(M,g)` | Lorentzian causal base and localization index. |
| `(E,nabla)` | upper bundle and connection carrying internal closure data. |
| `F` | nonlinear repair map, Maurer-Cartan residual or variational source. |
| `u_*` | selected fixed/coherent background. |
| `D F_(u_*)` | tangent generator or Hessian at the background. |
| `P,Q` | retained and excluded spectral/tangent projectors. |
| `A_tilde` | upper local and global operator structures. |
| `R` | evaluation/transfer data, including Green or homotopy operators. |

The current MTT kernel has exact instances of several fields on certified
benchmarks. It does not yet emit all of them from one selected physical q79
source.

## 2. Morphisms

A morphism `(f,U): C_1 -> C_2` should preserve, at the declared tier:

1. causal order on the base;
2. Hermitian bundle and connection data;
3. the repair equation and selected fixed point;
4. the retained projector, `U P_1 = P_2 U`;
5. localization of the upper operator net;
6. Green/homotopy data whenever transferred products are claimed.

This is stronger than saying that two encodings use isomorphic vector spaces.
It asks for commuting source-to-shadow diagrams.

## 3. Reduction readouts

One upper object can have several typed readouts:

```text
fixed/coherent states       H_P = Ran(P) or cohomology
operators                   Phi_P(A) = P A P
compatibility defect        L_A = Q A P
local net                   O -> P A_U^P(O) P
gauge                       Aut_M(E,F,nabla,P)
linear response             retained Hessian / Schur complement
topology                    index, holonomy, Fitting and spectral data
records                     selected effects and instruments
```

None of these readouts may be identified merely because their dimensions agree.

## 4. Why higher products enter

The exact first theorem gives

```math
\Phi_P(A)\Phi_P(B)-\Phi_P(AB)=-PAQBP.
```

Thus direct compression forgets a two-step excursion through `Q`. If the
excluded sector has a selected inverse or Green operator, homological
perturbation and Feshbach-Schur constructions can restore its effect through
transferred products. Schematically,

```text
upper product
  -> direct retained product
  + Q-sector Green corrections
  + higher transferred operations.
```

This fits the kernel's existing Hodge-transferred `A_infinity` and shorted
Hessian results, but an exact intertwiner is still needed. The leakage identity
is a diagnostic input to that theorem, not a replacement for it.

### Concrete next calculation

For the current cohesive repair benchmark, extract

```text
P, Q, G_Q, D F_(u_*), and the accepted upper product,
```

then compare:

```math
-PAQBP
```

with the first nontrivial transferred correction. Equality, a controlled
homotopy relation, or a counterexample would each move the frontier.

## 5. Encoding map

| Encoding | Candidate location in the reference object | Current boundary |
|---|---|---|
| Fixed points | `F(u_*)=0`, tangent generator and spectral gap | Abstract/benchmark results exist; physical source remains open. |
| Proto-spinor / Clifford | Clifford module structure on `E` and its retained sector | Needs selected Lorentzian and connection-preserving descent. |
| Dirac / Weyl | First-order upper operator and chiral retained modules | Finite/free constructions exist; physical HYM family remains open. |
| Twistor | Holomorphic incidence transform of selected causal/connection data | Vocabulary overlap is insufficient; typed containment is open. |
| Born recorder | Normal state, effects and instruments on a selected reduced algebra | Canonical q79 recorder is closed on its operational domain. |
| QM | `H_P`, self-adjoint operators, unitary dynamics and instruments | Canonical CCR and action normalization are not derived by this packet. |
| AQFT / QFT | Upper local net and compatible compressed net | Free/conditional results exist; interacting continuum completion is open. |
| Gauge / SM | Vertical stabilizer and finite/operator readouts | `A47` closes the faithful low-energy group structurally; values have separate tiers. |
| GR | Dynamics of `(M,g)` sourced by a selected reduced effective action | Physical normalization and UV completion remain open. |
| String / Fu-Yau | A selected internal geometric realization of `E,nabla,F` | May contain genuine physical internal modes; cannot be relabelled as pure constraint data without the charter tests. |

## 6. Falsification tests

The reference system should be rejected or narrowed if any of these occurs:

1. no one selected source emits compatible `F`, `P`, connection and operator
   data;
2. compression destroys microcausality for the proposed physical local algebra;
3. transferred products depend on unselected Green operators or gauges;
4. the established `A47` gauge group cannot arise as the source stabilizer;
5. the candidate conjugate observables require an independent lower
   noncommutative algebra rather than upper constraint leakage;
6. vertical modes have independent causal propagation, invalidating their
   classification as constraint coordinates;
7. the language only renames existing packets without shortening a dependency,
   predicting a held-out entry or exposing an obstruction.

## 7. What would count as a breakthrough

The decisive result would be a same-source theorem of the form

```text
selected closure repair
  -> fixed point and gapped tangent projector
  -> upper automorphisms and local net
  -> transferred operator algebra
  -> A47 gauge shadow + selected quantum pair + locality
```

with all arrows preserving connections, domains, normalizations and source
hashes. That would make several complicated postprojection rules consequences
of simpler upper rules. Until then, this is a disciplined search coordinate,
not a new fundamental ontology.
