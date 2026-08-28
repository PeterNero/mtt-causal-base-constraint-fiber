# Seven-Row Endpoint Factorization and Minimal-Source Theorem v1

**Date:** 2026-08-29
**Identifier:** `CBF.T12`
**Tier:** `EXACT_GENERAL + EXACT_DEPENDENCY_WITNESSES; PHYSICAL_Q79_OPEN`

## 1. Result

The physical continuum contract was previously written as seven flat rows,
`EP.01` through `EP.07`. That presentation is safe but mathematically
misleading: it makes deterministic outputs look like independent physical
inputs.

This theorem proves that, within the accepted MTT endpoint architecture, all
seven rows factor through three hash-bound source packets:

```text
GAS  geometry-action source
SYN  spectral-synthesis source
BV4  BV-compatible externalization/compactification source
```

The factorization is

```text
EP.01 <- GAS.endpoint
EP.02 <- SYN.map and domains
EP.03 <- SYN.source/contraction squares
EP.04 <- GAS.symmetry + SYN.equivariance
EP.05 <- Hess(GAS.action) + SYN.projector/complement
EP.06 <- GAS.action, pairing, real slice and normalization
EP.07 <- BV4
```

Thus `EP.04` and `EP.05` are deterministic consequences once their source
packets are present. The higher-operation part of `EP.03` is also automatic by
`CBF.T11` after its finite differential, product and contraction squares have
been proved.

The three packets are structured mathematical objects, not three numbers and
not a claim of a three-parameter physical theory. They may be serialized in
one file; "three" counts informationally distinct typed components, not storage
objects. Their current physical q79 acceptance remains `0/3` components and
`0/7` rows.

## 2. The three source packets

### 2.1 Geometry-action packet `GAS`

`GAS` contains one source-hashed endpoint and one action on that same endpoint:

```text
GAS=(
  X, V3, W9, metrics, HYM connections, common chamber,
  anomaly/Bianchi/Green-Schwarz data, shared-line descent,
  field and residual complexes, domains,
  omega, real slice, normalization,
  S, u_*, K=D^2 S(u_*),
  source symmetry Gamma, source hash
).
```

Here `K` is the signed gauge-fixed action Hessian on its declared domain. A
positive repair normal may also be recorded, but it is not substituted for
`K`. The cyclic Maurer-Cartan theorem supplies a formal candidate for one
integrability lane; it does not currently instantiate this physical packet.

### 2.2 Spectral-synthesis packet `SYN`

`SYN` contains the selected finite/continuum comparison:

```text
SYN=(
  F_fin, H_cont,
  U:F_fin -> H_cont, U*U=I,
  P=UU*, Q=I-P,
  Sobolev domains,
  differential/product/projector squares,
  intrinsic spectral and multiplicity selection,
  product/phase anchors and symmetry equivariance,
  complement inverse or exact Galerkin certificate,
  nonlinear and omitted-tail majorants,
  source hash
).
```

An arbitrary unitary between equal-dimensional spaces is not `SYN`. The map
must be emitted by the endpoint spectral and representation data, or by the
already-proved overlap-polar compiler with all physical source rows supplied.

### 2.3 Four-dimensional BV packet `BV4`

`BV4` is the physical compactification object frozen by H4-T15/H4-T16:

```text
BV4=(
  Y4, X, externalized or ten-dimensional field stack,
  four-dimensional field stack,
  p_KK, i_KK, h_KK and cotangent lifts,
  source and target BV pairings and actions,
  representation/shared-line maps,
  density and fiber integration,
  real structures, statistics and ghost degrees,
  gauge fixing, domains and principal symbols,
  BV pushforward and determinant orientation,
  source hash
).
```

The normalized orientation-profile theorem supplies an exact reduction
mechanism for an already-given lower action. It is not an upstream construction
of `BV4`.

All three packets must carry the same root source hash, and cross-packet
certificates must identify the action Hessian, endpoint, synthesis and
compactification action literally rather than up to an unnamed isomorphism.

## 3. Seven-row factorization theorem

### Theorem 3.1

Assume `GAS`, `SYN` and `BV4` satisfy their declared identities and share one
root source. Then every row `EP.01` through `EP.07` is decidable without any
fourth source packet.

More precisely:

1. `GAS` supplies `EP.01` and `EP.06`.
2. `SYN` supplies the typed map/domains of `EP.02` and the finite
   source/contraction identities of `EP.03`.
3. `GAS.symmetry` and `SYN.equivariance` imply `EP.04`.
4. `K=D^2S(u_*)` from `GAS` and `(U,P,Q)` from `SYN` determine every
   rank-102 matrix entry, Galerkin residual and Feshbach self-energy in
   `EP.05`. Complement and tail estimates remain proofs to execute, but they
   use the same operators and add no new physical source values.
5. `BV4` supplies `EP.07` and verifies that the action in `EP.06` reduces to
   the accepted four-dimensional field and BV actions.

### Proof

Rows `EP.01`, `EP.02`, `EP.03`, `EP.06` and `EP.07` follow directly from the
typed contents of the three packets. This is not circular: those rows identify
the irreducible source-bearing declarations and their required certificates.

For `EP.04`, let `rho_cont(g)` preserve the endpoint complex, action, domains
and pairing, and let `rho_fin(g)` be the selected finite action. The synthesis
identity

```text
rho_cont(g) U = U rho_fin(g)
```

implies

```text
rho_cont(g) P=P rho_cont(g),
rho_cont(g) Q=Q rho_cont(g).
```

If `K` is action-natural, then it commutes with `rho_cont(g)`. Functional
calculus transports every selected Riesz projector, reduced Green and
complement inverse. `CBF.T11` transports every transferred operation once the
source and contraction squares of `EP.03` hold. Hence the physical
`C4`/monodromy row is a consequence of the declared source action and
equivariant synthesis, not an independent matrix choice.

For `EP.05`, choose a finite orthonormal basis `(e_a)` and write

```text
A(z)=U*(K-z)U,
R(z)=Q(K-z)U=QKU.
```

If `R=0`, the selected range reduces `K` and `A(z)` is the exact Galerkin
operator. Otherwise, whenever the complementary inverse exists,

```text
F_U(K-z)
 = U*(K-z)U
   - U*K Q [Q(K-z)Q]^-1 Q K U.        (3.1)
```

Every coefficient in (3.1) is a matrix element of `K`, `U` or the
same-source complementary Green. No new coefficient can be fitted at this
stage. Interval inverse bounds and omitted-tail majorants are analytic
certificates on the same objects. This proves the claimed factorization of
`EP.05`.

Finally, the `BV4` action and pairing identities compare the same upper action
with the accepted four-dimensional action. They cannot be replaced by the
internal cotangent notation alone. This proves the seven-row sufficiency
statement. QED.

## 4. Exact all-arity consequence

The finite part of `EP.03` is intentionally small. Suppose the continuum and
finite contractions obey

```text
Phi d=d' Phi,
Phi mu=mu'(Phi tensor Phi),
Phi i=i' Psi,
p'Phi=Psi p,
Phi H=H'Phi.
```

`CBF.T11` then gives

```text
Psi m_n=m'_n Psi^(tensor n)
```

for every arity. A domain-preserving unitary reducing cochain map also
transports the adjoint, Laplacian, harmonic projector, reduced Green and Hodge
homotopy. Therefore `SYN` does not need an infinite vertex table.

If any square has nonzero defect, the exact conclusion is unavailable. The
candidate must instead use the existing `FSB.03b` polar-distortion and
nonlinear-tail majorants.

## 5. Minimality and independence

Theorem 3.1 proves sufficiency. The following theorem prevents an unjustified
claim that one of the three packets follows from the other two.

### Theorem 5.1

In the class of endpoint systems used above, none of the `GAS`, `SYN` or `BV4`
obligations can be deleted from Theorem 3.1 using the currently proved
universal implications. Doing so requires an additional selection theorem.

### Proof by exact countermodels

**Upper action/complement data.** Keep the synthesis and its retained lower
action fixed. If `Q=I-UU*`, the two upper quadratic actions with Hessians

```text
K0=[[2I,I],[I,5I]],
K1=K0+Q=[[2I,I],[I,6I]]
```

agree exactly after restriction to `Ran(U)`, so they induce the same retained
field action and can share the same lower `BV4` data. Their Feshbach operators
are nevertheless `(9/5)I` and `(11/6)I`. Thus the upper action, its
complementary dynamics and normalization cannot be recovered from `SYN` and a
retained lower action alone.

**Spectral synthesis.** Let `K=I_4`. Both

```text
U0=(e1,e2),
U1=((3e1+4e3)/5,(3e2+4e4)/5)
```

are rational isometries and select distinct rank-two projectors while having
identical compressed Hessian `I_2`. Geometry and action alone therefore do not
select `SYN` in a multiplicity space. The FSB.03d spectral, representation,
product and phase anchors are essential.

**Four-dimensional compactification.** A cotangent Hamiltonian satisfies

```text
S_cot(x,0)=0,
```

whereas a physical field action can obey `S0(x) != 0`. No
zero-section-preserving identification follows without a field-only upper
action and reduction map. Independently, a neutral source representation has
no surjective equivariant map onto a nonzero character sector. Hence internal
geometry, action and synthesis do not determine the charged four-dimensional
field stack or `BV4`.

The three failures prove informational independence at the level of the
current source obligations. They do not prove an invariant minimum number of
files, a categorical uniqueness statement or a lower bound of three numerical
parameters.
QED.

## 6. Exact finite execution

The generated packet contains three independent exact checks.

### 6.1 q79 source/contraction and covariance rows

The source-locked `CBF.T11` packet verifies on the 144-to-48 q79 contraction
that translation and Fourier preserve the differential, product, inclusion,
projection and homotopy. Its order-36 target action therefore preserves all
transferred operations. This is an exact finite execution of the mechanism
behind `EP.03` and `EP.04`, not a physical continuum instantiation.

### 6.2 Signed Hessian and Feshbach row

Use

```text
K = [[2I2,I2],[I2,5I2]],
U = [[I2],[0]],
J = diag(J2,J2),
J2=[[0,-1],[1,0]].
```

Then `J^4=I`, `JK=KJ`, `U*U=I`, and

```text
Q K U != 0,
U*K U=2I2,
U*K Q (QKQ)^-1 Q K U=(1/5)I2,
F_U(K)=(9/5)I2.
```

The determinant identity is exact:

```text
det(K)=det(5I2) det((9/5)I2)=81.
```

This executes the derived calculation in `EP.05` and verifies that action
symmetry passes to the exact effective operator. It supplies no physical q79
rank-102 values.

### 6.3 Independence witnesses

The verifier checks the complementary-action ambiguity, rational
synthesis-degeneracy, zero-section and neutral-character examples in Theorem
5.1 over exact rationals. These witnesses establish logical independence and
guard against a false source reduction.

## 7. Current seven-row decision

| Row | Source packet | Mathematical status after this theorem | Physical q79 status |
|---|---|---|---|
| `EP.01` | `GAS` | typed primitive | open (`B.HS.01`) |
| `EP.02` | `SYN` | typed primitive with existing compilers | open (`B.GEO.01`) |
| `EP.03` | `SYN` | finite identities primitive; all-arity consequences automatic | open (`B.GEO.01`) |
| `EP.04` | `GAS+SYN` | derived by equivariance and functional calculus | open (`B.GEO.01`) |
| `EP.05` | `GAS+SYN` | derived Galerkin/Feshbach execution | open (`B.OP.01`) |
| `EP.06` | `GAS` | typed primitive; formal cyclic lane exists | open (`B.ACTION.01`) |
| `EP.07` | `BV4` | typed primitive; abstract cotangent/product reduction exists | open (`B.ACTION.01`) |

The strict count remains

```text
physical packets accepted: 0/3
physical rows accepted:    0/7
```

What changes is the dependency graph. `B.OP.01` is an execution blocker, not a
fourth independent physical source. Once the selected `GAS` and `SYN` packets
exist, its arrays and decision are compelled by equation (3.1).

## 8. Machine-readable endpoint contract

`q79_physical_endpoint_three_packet_contract.schema.json` freezes the required
input structure. It requires:

- one root source hash repeated in all three packets;
- endpoint/action and action/Hessian identity certificates;
- endpoint/synthesis and symmetry compatibility certificates;
- action/compactification identity and a full parameter/input ledger; and
- all typed data already demanded by the current HYM, Feshbach and BV bridge
  contracts.

The schema deliberately contains no boolean such as `proof=true`. Each row
points to a hash-addressed artifact. A future eta9/Hull-Strominger result can
fill `GAS` first; the compiler can then identify exactly which `SYN` and `BV4`
artifacts remain without changing the contract.

## 9. Relation to the preprojection thesis

The factorization is a concrete example of simpler upper-world rules producing
many lower checks. The action Hessian, symmetry and selected synthesis jointly
emit the finite operator, its self-energy correction, its covariance and its
entire transferred interaction hierarchy. Those are not seven unrelated
postprojection choices.

The theorem also marks the limit of that simplification. A source action, a
selection of the retained sector and a physical four-dimensional
externalization are logically distinct kinds of information. Calling all of
them "closure" would hide rather than solve the remaining problem.

## 10. Frontier decision

Closed here:

- exact factorization of `EP.01-EP.07` through `GAS`, `SYN` and `BV4`;
- proof that `EP.04` and `EP.05` introduce no fourth source packet;
- exact action-Hessian/Feshbach/covariance witness;
- exact independence of upper action/complement data, synthesis selection and
  physical compactification; and
- one machine-readable same-source endpoint schema.

Still open:

- construction of physical `GAS` from the selected visible-hidden q79 HYM
  endpoint and upper action;
- construction of physical `SYN` from that same endpoint, including domains,
  multiplicity resolution, complement inverse and tail bounds;
- construction of physical `BV4`, including charged/chiral zero modes,
  field-only action reduction and Lorentzian/BV domains; and
- all four controlling blockers `B.HS.01`, `B.GEO.01`, `B.OP.01` and
  `B.ACTION.01`.

The next integration step is no longer "fill seven unrelated rows." It is:

```text
1. bind the selected eta9/HYM endpoint and upper action into GAS;
2. execute SYN on the Hessian emitted by that exact GAS;
3. compute EP.04 and EP.05 automatically;
4. construct BV4 from the same root source.
```

## 11. Verification

Run:

```powershell
python build_q79_seven_row_endpoint_factorization.py
python verify_q79_seven_row_endpoint_factorization.py
python verify.py
```

The generated packet is
`q79_seven_row_endpoint_factorization.packet.json`.

## 12. Sources and version delta

This theorem composes, without reopening, `CBF.T11`, `FSB.03a-d`, the q79 HYM
naturality/Feshbach theorem, H4-T10, H4-T15 and H4-T16. The exact source paths,
commits and SHA-256 values are frozen in
`q79_seven_row_endpoint_factorization_source_lock.json`.

Version 1 replaces the flat seven-row frontier by a proved source-dependency
factorization, supplies exact independence countermodels and emits the
three-packet physical endpoint schema. It changes no physical acceptance
state.
