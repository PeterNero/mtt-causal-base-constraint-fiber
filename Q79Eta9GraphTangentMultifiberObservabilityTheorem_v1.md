# CBF.T71 q79 eta9 graph-tangent multifiber observability theorem

## Status

`CLOSED_EXACT_SELECTED_RESIDUE_THREE_EVALUATION_PROJECTIVE_OBSERVABILITY_RANK122`

T70 proved that one selected coefficient-evaluation quotient sees rank 70 of
the 122 projective graph-family directions. T71 asks the next exact question:
how many independent elliptic evaluation rows are needed to remove that
coefficient-level blind sector?

## 1. Deterministic evaluation panel

Work over the same selected field `F_101[gamma]/(M)`. The four test rows are
points of the Fermat cubic modulo 101:

```text
e0=(1, 0,-1),
e1=(0, 1,-1),
e2=(1,-1, 0),
e3=(1, 1,75).
```

The first three satisfy `e2=e0-e1`, so their elliptic weight span has rank 2.
The fourth point is selected without a fit: it is the lexicographically first
`(1,a,b)`, with `1<=a,b<=100`, satisfying the Fermat equation and lying
outside `span(e0,e1)`. The determinant of `(e0,e1,e3)` is `77 mod 101`, hence
their weight span has rank 3.

These are residue coefficient probes. T71 does not assert that `e1` or `e3`
is a certified smooth fiber on the selected characteristic-zero physical
loop.

## 2. Exact ranks

For each `e_i`, quotient the evaluated 83-coordinate K3 section by its radial
fiber relation. Restrict the resulting 82-row operator to the canonical
rank-123 affine graph-incidence kernel. Exact elimination gives the one-row
image ranks

```text
e0: 70,
e1: 70,
e2: 68,
e3: 70.
```

Every pair among the four rows has

```text
image rank               111,
projective kernel rank    11.
```

The dependent triple `(e0,e1,e2)` remains rank 111. The independent triple
`(e0,e1,e3)` gives

```text
image rank                 122,
affine common kernel rank    1,
projective kernel rank       0.
```

The one-dimensional affine kernel is exactly the radial selected-member line
`<F>` removed on projectivization.

## 3. Theorem

**Three-Evaluation Coefficient Observability Theorem.** For the selected
residue graph-incidence family, the evaluation quotients at `e0`, `e1` and
`e3` jointly separate all 122 projective graph-preserving coefficient
directions. No tested pair does so: every pair leaves an 11-dimensional
projective kernel. A third row dependent in the elliptic weight carrier adds
no rank, while a third independent row closes the coefficient kernel.

**Proof.** The builder reconstructs the canonical G3AK rank-123 kernel and
computes the joined quotient maps on that basis. The independent verifier
uses the identity

```text
rank(Q_panel | ker I)=rank([I;Q_panel])-rank(I)
```

on the original incidence matrix instead. Both routes give rank 111 for the
pair/dependent triple and rank 122 for the independent triple. QED.

## 4. What this changes

T71 gives the first exact finite panel that removes the hidden coefficient
blind sector exposed by T70. It also identifies a structural role for the
three-dimensional elliptic carrier: three independent evaluation rows are
needed here, while repeated or linearly dependent rows cannot replace them.

This does not make the number three a physical selector or prove a general
minimality theorem over every member. It is a selected-carrier rank theorem.
It does show that any later family derivative computed from only one or two
fiber readouts is incomplete on this carrier.

## 5. Boundary and frontier

Coefficient observability is upstream of physical normal-function
observability. The following remain open:

```text
smooth characteristic-zero realization of three independent path panels,
Picard/Abel-Jacobi derivative on those panels,
rank-164 Gauss-Manin transport between them,
248-row BHT handle accumulation and integral-period reduction,
beta_C and U_eta9.
```

The next constructive target is therefore to replace the residue probes by
three independent **smooth characteristic-zero panels on the selected
B-loop**, with certified overlap and transport. Their joined coefficient
rank is a prerequisite, not a substitute, for the global BHT calculation.

## 6. Reproduction

```powershell
python build_q79_eta9_graph_tangent_multifiber_observability.py
python verify_q79_eta9_graph_tangent_multifiber_observability.py
python -m unittest tests.test_q79_eta9_graph_tangent_multifiber_observability -q
```

No observed value, fitted parameter or physical selector is introduced.
