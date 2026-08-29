# Minimal One-Constraint Multiplier Source and Three-Family Index Theorem

## Status

Claim ID: `CBF.T15`

Tier:

```text
EXACT_GENERAL
+ EXACT_BENCHMARK
+ CONDITIONAL_DIRECT_SOURCE_RECONSTRUCTION
```

Decision:

```text
MINIMAL_FREE_MATTER_DIRECT_SOURCE_CLASS_CLOSED
PHYSICAL_SOURCE_AND_NONLINEAR_VALUES_OPEN
```

This theorem closes a direct free-matter source class, not `B.ACTION.01` as a
whole. Physical packet acceptance remains `0/3` and physical row acceptance
remains `0/7`.

## 1. Result in one paragraph

The `80 x 80` operator used by `CBF.T13` is not merely a convenient Dirac
matrix. It is exactly the universal multiplier Hessian of `H4-T9` for one
family-blind closure constraint

```text
J : C^4 tensor H16 -> H16.
```

If `J` is surjective and coisometric, its kernel is

```text
ker J = C^3 tensor H16,
```

which is the established A46 48-state carrier. Conversely, among one-residual-
copy, family-blind constraints, three kernel copies force four source copies.
The coisometric constraint is unique up to a unitary change of source frame.
Its positive repair flow converges exactly to the 48-dimensional projector,
while its signed multiplier action has the CBF.T13 first-order Hessian. Gauge,
shared-circle and free four-dimensional externalization all commute.

This is the first exact non-q79 direct source for the complete free associated-
matter compiler. It does not select nonlinear flavor values, a physical mass
scale, a field-only cyclic action or the interacting BV theory.

## 2. Inputs and hypothesis

Let `H16` be the established one-family A46 complex representation, including

```text
Q, u^c, d^c, L, e^c, N^c
```

with the A47 faithful gauge group and A50 shared hypercharge circle. The
physical family carrier is

```text
H_chiral = C^3_family tensor H16.
```

For an integer `m>=1`, define

```text
E_m = C^m tensor H16,
F   = H16.
```

A **one-constraint family-blind source** is a linear residual

```text
Phi(a)=J a,
J=l tensor I_H16 : E_m -> F,
```

where `l:C^m -> C` is a nonzero covector. Family-blindness is an explicit
hypothesis. Gauge equivariance alone would not force it because `H16` is
reducible into Standard Model sectors.

The source is normalized when `J` is coisometric:

```text
J J^* = I_F.
```

Equivalently, `||l||=1`.

## 3. Minimal multiplicity theorem

### Theorem 3.1

For a surjective one-constraint family-blind source,

```text
ker J = ker(l) tensor H16,
dim_C ker J = (m-1) dim_C H16.
```

Consequently,

```text
ker J is C^3 tensor H16  if and only if  m=4.
```

### Proof

Because `J=l tensor I`, tensor exactness gives

```text
ker(l tensor I_H16)=ker(l) tensor H16.
```

Surjectivity of `l` gives `dim ker(l)=m-1`. Since `dim H16=16`,

```text
dim ker J=16(m-1).
```

This equals `48=3 x 16` exactly when `m-1=3`, hence `m=4`. QED.

### Interpretation boundary

This is a minimal reverse-source theorem. Given

1. the A46 three-family target;
2. one residual copy of the same typed `H16`; and
3. a family-blind surjective constraint,

the source multiplicity is forced to be four. It does not independently prove
that nature begins with four copies or that the three-family target should
have been assumed. The conditional direction must remain visible.

## 4. Unitary uniqueness theorem

### Theorem 4.1

Every normalized one-constraint source at `m=4` is unitarily equivalent to

```text
J_0=[I16  0  0  0].
```

Thus the normalized source class has no continuous dimensionless matrix knob
after quotienting by source-frame equivalence.

### Proof

The unitary group `U(4)` acts transitively on unit covectors. For every unit
`l`, there is `U in U(4)` such that

```text
l U^* = e_0^*.
```

Then

```text
J (U^* tensor I_H16)=e_0^* tensor I_H16=J_0.
```

The transformation is a provider-coordinate change of the type quotiented by
`CBF.T14`. QED.

The specific block placement in `CBF.T13` is therefore a coordinate choice,
while the one-normal-line equivalence class is invariant.

## 5. Universal multiplier action

`H4-T9` proves that every residual admits a variational multiplier lift. For

```text
a in E_4,
lambda in F,
Phi(a)=J_0 a,
```

define the real action

```text
S_mult(a,lambda)=Re <lambda,J_0 a>.
```

Its Euler-Lagrange equations are

```text
J_0 a=0,
J_0^* lambda=0.
```

Since `J_0` is surjective, `J_0^*` is injective. Therefore

```text
Crit(S_mult)=ker(J_0) x {0}
            =(C^3 tensor H16) x {0}.
```

At every point of this critical locus, the signed Hessian is

```text
          [ 0      J_0^* ]
D_J =     [                 ].
          [ J_0       0    ]
```

The dimensions are

```text
dim E_4=64,
dim F=16,
dim(E_4 direct_sum F)=80.
```

This is exactly the CBF.T13 internal operator `D_X`.

Its square is

```text
D_J^2=diag(J_0^* J_0, J_0 J_0^*)
     =diag(Q,I16),
```

where `Q` is the rank-16 projector onto the closure-normal copy in `E_4`.
Hence

```text
spectrum(D_J)={-1,0,+1},
mult(-1)=16,
mult(0)=48,
mult(+1)=16.
```

The characterwise index is

```text
[ker J_0]-[coker J_0]=3[H16].
```

## 6. Positive repair and exact projection flow

The corresponding positive repair cost is

```text
R(a)=1/2 ||J_0 a||^2.
```

Its Hessian is the normal operator

```text
H_rep=J_0^* J_0=Q.
```

Let

```text
P=I_E-Q.
```

Then `P` is the orthogonal projector onto `ker J_0`, with rank 48. The negative
repair gradient flow is

```text
d a/dt = -Q a.
```

It has the exact solution

```text
a(t)=P a(0)+exp(-t) Q a(0).
```

Therefore

```text
lim_(t->infinity) a(t)=P a(0).
```

This is a literal repair-to-projection theorem. The closure-normal component
decays, while the coherent three-family component survives unchanged.

For `r=exp(-t)`, the flow operators

```text
T_r=P+r Q
```

obey

```text
T_r T_s=T_(rs),
J_0 T_r=r J_0,
T_0=P,
T_1=I.
```

The machine packet verifies these identities exactly with rational formal
parameters; it does not approximate exponentials.

## 7. Signed action is not the repair square

The source carries two related but inequivalent functionals:

```text
signed multiplier action:  S_mult(a,lambda)=Re<lambda,J_0 a>,
positive repair cost:       R(a)=1/2||J_0 a||^2.
```

The first has Hessian `D_J` and both positive and negative directions. The
second has Hessian `Q` and is nonnegative. Squaring erases the sign and the
multiplier polarization. This instantiates the H4-T9 boundary rather than
reopening it.

The multiplier action is also not automatically the field-only cyclic
Maurer-Cartan action of H4-T10. It adds a typed response/multiplier copy of
`H16`. H4-T15 requires a separate BV-compatible externalization theorem before
such fields can be identified with the accepted physical BV stack.

## 8. Gauge and shared-circle descent

Let `rho_16(g)` be the A46 one-family representation. Act diagonally by

```text
rho_E(g)=I4 tensor rho_16(g),
rho_F(g)=rho_16(g).
```

Then

```text
J_0 rho_E(g)=rho_F(g) J_0.
```

The same identity holds for the A50 shared-circle generator because its action
is also identical on every source copy. Therefore

```text
[D_J,rho_E direct_sum rho_F]=0,
[P,rho_E]=0,
[Q,rho_E]=0.
```

The kernel inherits

```text
rho_kernel=I3 tensor rho_16.
```

Thus the A46 representation, A47 global gauge quotient and A50 hypercharge
rows descend without any postprojection charge choice. The already-certified
anomaly sums remain zero.

## 9. Source automorphisms and the flavor no-go

The subgroup of source-frame unitaries preserving `J_0` acts as

```text
U(3)
```

on `ker J_0`. This is the free-source family stabilizer.

### Theorem 9.1

Any linear family operator determined solely by this source and natural under
all source automorphisms is family scalar:

```text
M_family=c I3.
```

### Proof

Naturality requires `M_family U=U M_family` for every `U in U(3)`. The
commutant of the defining irreducible `U(3)` representation is the scalar
algebra. QED.

The independent verifier also solves the exact commutator equations against a
matrix-unit generating set and obtains commutant dimension one.

### Physical consequence

The minimal direct source produces

- three equivalent families;
- the correct family-blind gauge action;
- no family mass splitting;
- no CKM or PMNS orientation;
- no CP-sensitive family invariant; and
- no nine charged magnitude values.

This is not a defect in the proof. It identifies the next irreducible source
datum. The already-established finite family-response results provide
noncommuting structural operators generating `M3(C)`, but `B.SM.02` records
that nine charged scalar values remain unsourced. Those operators must enter a
nonlinear cyclic residual or field-only action from the same root source;
their mere existence cannot alter this theorem's `U(3)`-symmetric free action.

## 10. Parameter ledger

At the normalized finite source tier:

```text
continuous dimensionless matrix parameters after U(4) quotient: 0,
postprojection charge choices:                                  0,
observed values used:                                            0.
```

However, assigning physical units introduces an overall scale. Replacing

```text
J_0 -> Lambda J_0
```

changes

```text
spectrum(D_J):       +/-1 -> +/-Lambda,
repair gap:          1 -> Lambda^2,
repair time scale:   1 -> Lambda^(-2).
```

Coisometric normalization sets the dimensionless representative to one but
does not derive a physical value for `Lambda`. Thus the direct free source has
one unselected dimensionful scale before connection to a selected base/action
normalization.

The nonlinear family/sector coefficients are additional missing source data,
not hidden in this one scale.

## 11. Four-dimensional externalization

`CBF.T13` applies directly because its `D_X` is now identified with `D_J`.
On the product carrier,

```text
D_tot=D_Y tensor I80 + Gamma_Y tensor D_J,
D_tot^2=D_Y^2 tensor I80 + I tensor D_J^2.
```

Projection by `I tensor P` retains

```text
dim=2 x 48=96
```

in the exact two-dimensional external witness and gives one massless external
Dirac field for each internal zero mode in the general compiler. Gauge,
hypercharge, free quadratic action and cotangent pairing descend exactly as in
`CBF.T13`.

This closes the source origin of the **free associated-matter** operator used
there. It does not supply a selected four-dimensional spacetime, gauge
background, nonlinear vertex, QME or renormalized interacting state.

## 12. Fixed-point and constraint-fiber interpretation

The construction implements the intended upper-world logic directly:

```text
upper source coordinate a
  -> closure residual J_0 a
  -> repair flow exp(-t Q)
  -> coherent fixed subspace ker J_0
  -> 48-state projected matter carrier.
```

No extra manifold is introduced. The eliminated normal copy carries no
independent retained initial datum under repair flow, and the surviving family
carrier is a fixed/coherent sector. At this finite benchmark tier, this is a
cleaner fit to the constraint-fiber thesis than a literal compactification.

Physical constraint-fiber status still requires coupling to the declared
four-dimensional causal net and proving that the multiplier/normal sector does
not reappear as an independently propagating physical field.

## 13. What this changes about q79

The free matter source no longer needs q79 even as an expected provider. q79
may still provide:

- a geometric derivation of the same one-normal-line source class;
- the nonlinear action and density;
- the physical dimensionful scale;
- family/sector interaction coefficients;
- anomaly/Bianchi and UV consistency.

If q79 emits those data and its free operator lies in this unitary source
class, the two routes agree. If a direct repair source emits them first, the
q79 geometric endpoint has been bypassed for that sector.

## 14. Exact frontier delta

Before `CBF.T15`, the matrix

```text
D_+=[I16 0 0 0]
```

was only an exact compiler witness. After `CBF.T15` it is also:

- the unique normalized one-constraint source class under the declared
  family-blind hypotheses;
- the Jacobian of a closure residual;
- the H4-T9 multiplier-action Hessian;
- an odd self-adjoint dilation whose source block of `D_J^2` is the positive
  repair normal;
- the signed operator determining, through that normal square, an exact repair
  flow converging to the A46 carrier; and
- an equivariant source for the CBF.T13 free product-Dirac compiler.

This discharges the free associated-matter subclause of the direct-source
program. It does not satisfy the full `B.ACTION.01` exit because no selected
nonlinear cyclic action, physical scale, complete transferred product or BV
pushforward has been supplied.

## 15. Next target

The next object should not be another linear matrix. It is a same-source
nonlinear extension

```text
Phi(a)=J_0 a+B_2(a,a)+B_3(a,a,a)+...
```

or a field-only cyclic action whose Hessian is the present free source and
whose higher tensors:

1. break the free `U(3)` stabilizer through the already-selected noncommuting
   family orientation;
2. preserve A47/A50 gauge and shared-circle symmetry;
3. descend through the CBF.T13/T14 source contract;
4. select at least one invariant magnitude without observed input; and
5. carry one declared physical scale or derive it from the causal/action
   normalization.

The first decisive test is one held-out source-normalized scalar. If no such
scalar is emitted, the construction remains an exact structural compiler.

## 16. Claims and nonclaims

### Proved

- `m=4` is necessary and sufficient for a three-copy kernel under the stated
  one-constraint family-blind assumptions;
- the normalized source is unique up to source-unitary equivalence;
- the multiplier Hessian equals the CBF.T13 internal operator;
- the positive repair Hessian is its normal square;
- the repair flow converges exactly to the 48-dimensional projector;
- A46/A47/A50 data descend equivariantly;
- the free-source family stabilizer is `U(3)` and forces family universality;
- the normalized source has zero continuous dimensionless matrix knobs.

### Not proved

- an independent MTT derivation of the four-copy source multiplicity;
- selection of this source class by the physical universe;
- a physical value for the overall scale;
- nonlinear Yukawa, mass, threshold or CP values;
- equality with a selected field-only cyclic/BV action;
- a complete interacting four-dimensional theory;
- closure of `B.ACTION.01`, `B.OP.01` or `B.SM.02`.

## 17. Reproduction

```text
python build_direct_one_constraint_multiplier_source.py
python verify_direct_one_constraint_multiplier_source.py
python -m unittest tests.test_direct_one_constraint_multiplier_source -v
```

The generated packet is
`direct_one_constraint_multiplier_source.packet.json`.
