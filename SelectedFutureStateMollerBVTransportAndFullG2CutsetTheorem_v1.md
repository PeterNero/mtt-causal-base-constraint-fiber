# Selected Future-State Moller/BV Transport and Full G2 Cutset Theorem v1

**Claim:** `CBF.T46`

**Date:** 2026-08-30

**Status:** exact selected positive Hadamard in-state transport for compactly
supported direct Dirac-Yukawa background perturbations; exact local-formal
BV state-pullback and canonical BRST-lift criterion; full selected Standard
Model `G2`, determinant holonomy and the regulator-independent fixed-coupling
continuum remain open

## 1. Result

CBF.T44 and CBF.T45 leave a much smaller state problem than their separate
status lines suggest.

T44 already supplies, for a compactly supported smooth order-zero change of
the direct product-Dirac operator,

```text
D_h=D_H+V_h,
```

advanced and retarded Moller maps. They induce star-isomorphisms of the even
CAR observable algebras. T45 supplies the selected future-positive pure
quasifree state `omega_fut` on the homogeneous flat anchor branch. The
retarded map therefore determines an in-state on every member of that
background family:

```text
omega_h^in
  =omega_fut composed with (alpha_h^ret)^(-1).       (1.1)
```

Equation (1.1) is not another state choice. It is the unique transport of the
already selected initial state along the already specified causal map. It is
normalized, positive, pure, quasifree and Hadamard. It composes exactly along
successive background changes. No density matrix, temperature or continuous
state coordinate is appended.

This closes the exact state-transport subclause for the complete T44 direct
Dirac-Yukawa **background** family. That family is still linear in the
fermion field and must not be renamed the nonlinear interacting Standard Model.

At the local-formal BV tier the same algebraic mechanism is available. If

```text
I_V:A_phys,V -> A_phys,0                            (1.2)
```

is a unital star-isomorphism satisfying

```text
I_V s_hat_V=s_hat_0 I_V,                            (1.3)
```

then every free physical state `omega_0` gives

```text
omega_V=omega_0 composed with I_V.                  (1.4)
```

Normalization, formal square-cone positivity and BRST descent follow from
(1.2)-(1.3). The q79 deformation theorem already proves that every free
physical vector has a formal interacting lift. T46 adds a canonical choice
of that lift relative to the certified free contraction: at every positive
order impose zero physical projection and the homotopy gauge. The lift is
then unique recursively.

The remaining full-state obstruction is now exact. The certified free
physical seed factors as

```text
omega_0
 =omega_gauge,phys tensor omega_Higgs tensor omega_Weyl.  (1.5)
```

T45 selects `omega_Weyl`. T38 selects only the central radial marginal
`delta_H`; it explicitly does not select the local Higgs fluctuation state.
No current same-source theorem selects `omega_gauge,phys` either. Thus two
free factors remain unselected. In addition, T39's formal normalization has
not yet been selected by the upper physical action, and formal positivity is
not a fixed-coupling Cstar theorem.

Consequently T46 advances `G2` without falsely promoting it. The exact
quadratic-background state orbit, the formal pullback rule and the formal
lift ambiguity close. The selected full gauge-Higgs-Weyl seed, selected full
BV map, determinant holonomy and fixed-coupling continuum remain open. The
top-level physical counters stay `0/3` gates and `0/7` rows.

## 2. Typed domains

Three different uses of the word "interaction" must remain separate.

### 2.1 External-background Dirac interaction

Here `V_h` is a compactly supported c-number order-zero endomorphism in a
linear Dirac equation. The field algebra remains CAR. Its Moller map is exact,
not a perturbative series.

### 2.2 Local-formal nonlinear interaction

Here gauge, Higgs, Yukawa and scalar vertices belong to a formal interaction
functional `V`. Renormalized time ordering and the QME define the interacting
algebra and quantum BRST differential coefficientwise in the coupling and
`hbar`. Positivity takes values in the formal square cone.

### 2.3 Fixed-coupling physical interaction

Here the coupling has a nonzero numerical value and the observables belong to
a norm-complete Cstar algebra. The q79 corpus has this object at every finite
auxiliary regulator, but not yet as one selected regulator-independent
continuum theory.

Proofs at one tier do not silently promote another.

## 3. Exact retarded state transport

Let

```text
alpha_h^ret:A_H^even -> A_h^even                   (3.1)
```

be the CAR star-isomorphism induced by the retarded T44 Moller map. The
retarded support convention identifies the perturbed and anchor theories
before the compact interaction region. It is therefore the map appropriate
to the T45 initial state. Define (1.1).

### Theorem 3.1: state preservation

`omega_h^in` is a normalized positive state.

### Proof

Unitality gives

```text
omega_h^in(1)
 =omega_fut((alpha_h^ret)^(-1)(1))
 =omega_fut(1)=1.                                   (3.2)
```

For `A in A_h^even`, put

```text
B=(alpha_h^ret)^(-1)(A).
```

The star property gives

```text
omega_h^in(A^*A)
 =omega_fut(B^*B)>=0.                               (3.3)
```

No representation or trace-class density operator is needed. QED.

### Theorem 3.2: quasifree purity and Hadamard class

On the transported one-particle solution space, write the T45 covariance as
`P_fut` and the retarded one-particle Moller map as `M_h^ret`. Then

```text
P_h^in=M_h^ret P_fut (M_h^ret)^(-1).                (3.4)
```

The Moller map preserves the causal Hermitian form between the two solution
spaces. Hence (3.4) is again a basis projection. It defines a pure quasifree
CAR state.

The perturbation changes only the lower-order part of a Dirac operator. The
Moller pullback preserves the Hadamard wavefront relation; therefore the
state in (3.4) is Hadamard. This is the standard Dirac Moller-Hadamard
transport theorem, not an MTT-specific replacement for microlocal analysis.

### Theorem 3.3: relative uniqueness and composition

Equation (1.1) is the unique state satisfying

```text
omega_h^in composed with alpha_h^ret=omega_fut.     (3.5)
```

If `alpha_(k<-h)^ret alpha_(h<-H)^ret=alpha_(k<-H)^ret`, then contravariant
pullback gives

```text
T_(k<-h)^* T_(h<-H)^* omega_fut
  =T_(k<-H)^* omega_fut.                            (3.6)
```

The word "unique" in this theorem means the unique transport of the selected anchor state
along the specified map. It does not mean that the perturbed CAR algebra has
only one Hadamard state.

Using the advanced map instead produces the corresponding out-state. Its
comparison with the in-state is the T44 relative Cauchy evolution. Future
time orientation plus the demand for an initial state chooses the retarded
member; it does not prove that in- and out-states coincide.

## 4. Relation to the T44 contour scalar

The T44 element

```text
C_H[V_plus,V_minus]
 =S_H[V_minus]^(-1) star S_H[V_plus]                (4.1)
```

was state free. T45 defined

```text
Z_fut[V_plus,V_minus]
 =omega_fut(C_H[V_plus,V_minus]).                   (4.2)
```

T46 now gives the full exact background-state orbit needed to compare (4.2)
at different compact source histories. Equal-source return remains

```text
Z_fut[V,V]=1.                                       (4.3)
```

The state transport does not trivialize a source-dependent determinant-line
phase. A common central phase still cancels as in T44; relative holonomy
remains a separate analytic object.

## 5. Local-formal BV state pullback

Let `A_phys,V=H^0(s_hat_V,A_int)` on one bounded `H^1=0` q79 chart. Assume
(1.2)-(1.3), with `I_V(1)=1` and

```text
I_V(A^* star_V B)=I_V(A)^* star_0 I_V(B).           (5.1)
```

Let `omega_0` be a normalized formally positive state on the free physical
algebra. Define (1.4).

### Theorem 5.1: formal physical state transport

`omega_V` is normalized, hermitian and formally positive on interacting
ghost-number-zero BRST cohomology.

### Proof

Unitality proves normalization. Equation (5.1) gives

```text
omega_V(A^* star_V A)
 =omega_0(I_V(A)^* star_0 I_V(A)),                  (5.2)
```

which lies in the certified formal square cone. Equation (1.3) sends closed
elements to closed elements and exact elements to exact elements, so (1.4)
depends only on the physical cohomology class. QED.

The q79 presentation-groupoid certificate additionally proves that changes
of Hadamard representative, admissible renormalization prescription and
gauge-fixing representative transport these state cones by specified formal
star-isomorphisms. Such a presentation change is not a new physical
parameter.

This theorem is algebraically complete but conditional on its seed and map.
The existing q79 state theorem proves a nonempty family of admissible seeds.
T46 does not turn that family into one full selected seed by notation.

## 6. Canonical formal BRST lift

The q79 free quartet supplies a contraction

```text
Q0 h+h Q0=I-i p,
h^2=0,
p h=0,
h i=0.                                               (6.1)
```

Let

```text
Q_I=Q0+sum_(n>=1) lambda^n delta_n                  (6.2)
```

be the certified hermitian nilpotent interacting charge. For a free physical
vector `psi_0=i v`, seek

```text
psi_I=sum_(n>=0)lambda^n psi_n,
Q_I psi_I=0.                                        (6.3)
```

At order `n>=1`, put

```text
r_n=sum_(k=1)^n delta_k psi_(n-k).                  (6.4)
```

The coefficient equation is `Q0 psi_n=-r_n`. Impose

```text
p psi_n=0,
h psi_n=0.                                           (6.5)
```

Then define

```text
psi_n=-h r_n.                                        (6.6)
```

### Theorem 6.1: existence and uniqueness in homotopy gauge

For every free physical vector covered by the certified q79 deformation
theorem, (6.4)-(6.6) produce the unique formal interacting lift satisfying
(6.5).

### Proof

Nilpotence of `Q_I` and the lower-order equations make `r_n` `Q0`-closed.
Existence of some lift, already proved in the q79 deformation theorem,
implies the obstruction `p r_n` vanishes. Applying (6.1) gives

```text
Q0 h r_n=(I-i p-h Q0)r_n=r_n,
```

so (6.6) solves the coefficient equation and obeys (6.5).

If two such lifts first differ at order `n`, their difference `chi_n` obeys

```text
Q0 chi_n=0,
p chi_n=0,
h chi_n=0.
```

Equation (6.1) then gives `chi_n=0`, a contradiction. Induction proves
uniqueness. QED.

The interacting norm has positive leading coefficient. Its unique formal
square root with positive constant term normalizes `psi_I`; deformation
stability supplies square-cone positivity and null-equals-exactness.

This removes the phrase "choose a formal lift" once the free vector and one
certified contraction are fixed. It does not select the free vector. Under an
admissible gauge-fixing or renormalization change, the entire contraction and
lift transport through the certified presentation isomorphism.

## 7. Exact finite witnesses

The executable packet contains two independent finite witnesses.

### 7.1 Pure-state transport

Start with

```text
P=[[1,0],[0,0]],
U=[[3/5,-4/5],[4/5,3/5]].                           (7.1)
```

Then

```text
P'=U P U^T
  =[[9/25,12/25],[12/25,16/25]].                    (7.2)
```

Exact rational arithmetic verifies

```text
P'^2=P',
Tr(P')=1,
det(P')=0,
U^T P' U=P.                                         (7.3)
```

Expectations on every `2 x 2` matrix unit agree with algebra pullback, four
nontrivial square expectations are nonnegative, and a second `5-12-13`
rotation verifies exact composition.

### 7.2 Canonical BRST lift

Use the certified six-direction quartet basis

```text
(epsilon_1,epsilon_2,x,y,c,bar_c),
Q0 x=c,
Q0 bar_c=y,
h c=x,
h y=bar_c.                                          (7.4)
```

For the exact finite perturbation

```text
delta_1 epsilon_1=-c                                (7.5)
```

with all other images zero,

```text
Q(lambda)=Q0+lambda delta_1,
psi(lambda)=epsilon_1+lambda x.                     (7.6)
```

The verifier checks

```text
Q(lambda)^2=0,
Q(lambda)psi(lambda)=0,
p psi(lambda)=epsilon_1,
h(psi(lambda)-epsilon_1)=0.                         (7.7)
```

The inherited Krein form gives formal norm one. This is an exact
homological-lift witness, not a replacement proof of the full q79
interacting charge's hermiticity. That property is imported only from the
hash-locked q79 certificate.

## 8. The full free-seed cutset

The q79 local-formal theorem requires (1.5). Its three factors now have the
following status.

| Factor | Current selected status |
|---|---|
| `omega_Weyl` | selected by T45 on the homogeneous flat direct branch |
| radial background marginal | `delta_H` selected by T38 at its declared finite/formal repair tier |
| `omega_Higgs` for local fluctuations | nonempty Hadamard state space, but no same-source selected factor |
| `omega_gauge,phys` | positive BRST quotient and nonempty Hadamard state space, but no same-source selected factor |
| formal lift after a full seed | canonical in the T46 homotopy gauge |

The radial marginal and Higgs fluctuation state are different typed objects.
`delta_H` fixes the homogeneous background coordinate. It does not set local
Higgs fluctuations to zero and does not determine their two-point function.

Likewise, a fermionic covariance does not determine the gauge physical
covariance. Tensor-product existence is not tensor-product selection.

Therefore the selected full product seed is still open, with exactly two
missing factors in the current decomposition. A later theorem may select
them from the same stationary flat action, an asymptotic boundary, or a more
primitive closure condition. T46 proves neither that such a theorem is
impossible nor that ordinary Poincare vocabulary alone makes it an MTT source
theorem.

## 9. Fixed-coupling boundary

Formal positivity means

```text
b(lambda)=c(lambda)^*c(lambda)                      (9.1)
```

in the formal coefficient ring. It does not assign a convergent nonnegative
number at the physical coupling.

The inherited q79 theorem has a genuine fixed-nonzero-coupling Cstar algebra,
Gauss-neutral reduction and positive state at every finite auxiliary
regulator. Its acceptance counts are

```text
finite regulated landing: 5/5,
selected continuum promotion: 0/9.                  (9.2)
```

T46 neither weakens nor upgrades (9.2). A continuum promotion still needs a
selected regulator family and uniform locality, energy, Ward, state and
convergence estimates, or an independently proved common positive
Borel/Cstar completion.

## 10. G2 ledger after T46

```text
G2a flat future Weyl initial state:             closed by T45,
exact quadratic-background Dirac state orbit:  closed by T46,
local-formal positive state existence:         closed in q79 corpus,
formal state-pullback rule:                     closed by T46,
formal BRST lift given a full seed:             closed by T46,
selected full gauge-Higgs-Weyl seed:            open,
upper-selected full BV map/normalization:       open,
finite-regulator fixed-coupling Cstar state:    closed 5/5,
selected regulator-independent continuum:      open 0/9,
top-level physical G2:                          open. (10.1)
```

The top-level gate does not move because its equation asks for one same-root
selected full interacting physical state and BV pushforward, not only a
fermionic background orbit or an implication theorem.

## 11. Parameter ledger

T46 introduces

```text
observed values:                     0,
fitted coefficients:                 0,
continuous state selectors:          0,
new discrete state selectors:        0.
```

The retarded role is fixed by the inherited future time orientation and the
request for an initial state. The unresolved positive radial scale `H`
remains inherited. Hadamard, gauge-fixing and renormalization representatives
are transported presentation data at the local-formal tier; they are not
counted as new physical knobs.

## 12. Exact scientific boundary

Closed here:

- exact selected in-state transport through every compact T44 direct
  Dirac-Yukawa background perturbation;
- positivity, normalization, purity, quasifree character and Hadamard
  preservation of that orbit;
- exact state-transport composition and relative uniqueness;
- formal BV pullback of normalized square-cone-positive physical states;
- BRST-cohomology descent under a QME-intertwining star-isomorphism;
- a canonical recursive interacting BRST lift given a free physical seed;
- exact finite state-transport and homological-lift witnesses; and
- reduction of the full free-state selection problem to the gauge-physical
  and Higgs-fluctuation factors.

Still open:

- same-source selection of those two free factors;
- upper-action selection of the full BV map and anchored normalization;
- one selected global cosmological interacting state;
- source-dependent determinant-line connection and holonomy;
- the fixed-coupling regulator-independent q79 continuum;
- physical `G1`, q79 HYM universality, RG matching, uncertainties and
  observable comparison.

Physical acceptance remains

```text
0/3 gates,
0/3 packets,
0/7 rows.                                            (12.1)
```

## 13. Primary mathematical context

Dirac Moller star-isomorphisms and preservation of the Hadamard singular
structure under state pullback are proved in:

- N. Drago, N. Ginoux and S. Murro, *Moller Operators and Hadamard States for
  Dirac Fields with MIT Boundary Conditions*,
  <https://arxiv.org/abs/2109.01375>.

Formal BRST positivity and lift stability are supplied by:

- M. Duetsch and K. Fredenhagen, *Deformation Stability of
  BRST-Quantization*, <https://arxiv.org/abs/hep-th/9807215>.

The local causal interacting algebra and renormalized BV/QME setting are:

- R. Brunetti and K. Fredenhagen, *Microlocal Analysis and Interacting
  Quantum Field Theories*, <https://arxiv.org/abs/math-ph/9903028>;
- K. Fredenhagen and K. Rejzner, *Batalin-Vilkovisky Formalism in
  Perturbative Algebraic Quantum Field Theory*,
  <https://arxiv.org/abs/1110.5232>.

The fixed-coupling Cstar construction including Fermi fields is an external
benchmark, not an automatic q79 continuum theorem:

- R. Brunetti, M. Duetsch, K. Fredenhagen and K. Rejzner,
  *Cstar-Algebraic Approach to Interacting Quantum Field Theory: Inclusion
  of Fermi Fields*, <https://arxiv.org/abs/2103.05740>.

## 14. Reproduction

Run:

```powershell
python build_selected_future_state_moller_bv_transport.py
python verify_selected_future_state_moller_bv_transport.py
python -m unittest tests.test_selected_future_state_moller_bv_transport -v
python verify.py
```

The builder hash-checks every source, recomputes the exact pure-state
transport and composition witness, verifies the quartet contraction and
canonical lift, audits the three-factor free seed and preserves the declared
fixed-coupling and physical-counter boundaries. The independent verifier
recomputes the finite mathematics without importing the builder.
