# Associated-Matter Product-Dirac/BV Externalization Compiler Theorem v1

**Date:** 2026-08-29
**Identifier:** `CBF.T13`
**Tier:** `EXACT_GENERAL_COMPILER + EXACT_FINITE_WITNESS; PHYSICAL_Q79_SOURCE_OPEN`

## 1. Result

`CBF.T12` proves that all seven physical endpoint rows factor through `GAS`,
`SYN` and `BV4`. It leaves `BV4` as one large source obligation. The existing
H4-T16, H4-T18 and H4-T21 results already establish three essential facts:

1. a normalized internal contraction can be externalized and cotangent-lifted;
2. charged chirality must be retained by a first-order graded associated-matter
   operator, not inferred from a positive Hessian; and
3. the normalized BHT transform identifies the derived matter complex and its
   q79 chirality orientation once the selected endpoint exists.

This theorem supplies the missing universal compiler between those facts. A
single source-hashed associated-matter operator, external causal Dirac operator
and normalized fiber pairing determine:

```text
internal harmonic modes
  -> four-dimensional charged/chiral fields
  -> inherited gauge and shared-circle action
  -> reduced free quadratic action and BV pairing
  -> modewise causal operators
  -> an explicit massive-complement gap certificate.
```

No additional field-by-field charge, chirality, massless-mode or free kinetic
coefficient may be chosen after these inputs are fixed.

The exact finite execution uses

```text
D_+ = [I_16  0  0  0] : Q^(4 x 16) -> Q^16.
```

Its kernel is three copies of the exact A46 one-family carrier, hence has
dimension `3 x 16 = 48`; its cokernel is zero; its characterwise index is
`3[H_16]`; and its self-adjoint completion has a unit spectral gap on the
32-dimensional complement. The inherited A50 hypercharge rows, anomaly
cancellations and diagonal `Z6` descent all pass exactly.

This is a compiler witness. It is not evidence that the q79 HYM endpoint has
already emitted this particular operator or its normalized zero modes. The
physical acceptance count remains `0/3` packets and `0/7` rows.

## 2. Source packet reduced by this theorem

Define an **associated-matter kernel packet**

```text
AMK=(
  H_X^+ direct_sum H_X^-, Gamma_X,
  D_+:H_X^+ -> H_X^-, D_-=D_+^dagger,
  G action and real structure,
  domains and Hermitian density,
  P_0, normalized harmonic basis, G_X,
  complement gap mu,
  characterwise index and chirality convention,
  source_root_sha256
).
```

Here

```text
D_X = [[0,D_-],[D_+,0]],
P_0 = projector onto ker(D_X),
Q_0 = I-P_0,
D_X G_X = G_X D_X = Q_0,
G_X P_0=P_0 G_X=0.
```

The external causal packet is

```text
EXT4=(Y4,g4,S4,D_Y,Gamma_Y,domains,support conditions,
      advanced/retarded Green certificates,source_root_sha256).
```

The density packet `DEN` identifies the product pairing and verifies that the
chosen internal harmonic modes are orthonormal. `AMK`, `EXT4` and `DEN` must
carry the same root source hash as `GAS` and `SYN`.

The compiler output is the free associated-matter subpacket of `BV4`. It does
not yet contain the full bosonic/gravitational field stack, nonlinear upper
action, physical overlap values or quantum BV pushforward.

## 3. Product-Dirac reduction

Let `Y4` be an even-dimensional globally hyperbolic spin spacetime with a
massless Dirac-type operator `D_Y` and grading `Gamma_Y` satisfying

```text
Gamma_Y^2=I,
D_Y Gamma_Y + Gamma_Y D_Y=0.
```

Let `D_X` be the odd self-adjoint operator from `AMK`. On the product carrier
define

```text
D_tot = D_Y tensor I + Gamma_Y tensor D_X.                (3.1)
```

### Theorem 3.1: exact square and zero-mode reduction

The product operator obeys

```text
D_tot^2 = D_Y^2 tensor I + I tensor D_X^2.                (3.2)
```

The projector `P=I tensor P_0` reduces `D_tot`, and

```text
P D_tot P = D_Y tensor P_0.                               (3.3)
```

Consequently each normalized internal zero mode produces one massless
four-dimensional Dirac/Weyl lane, while an internal eigenmode with eigenvalue
`lambda` produces

```text
D_Y + lambda Gamma_Y,
(D_Y + lambda Gamma_Y)^2=D_Y^2+lambda^2.                  (3.4)
```

#### Proof

Expand (3.1). The mixed term is

```text
(D_Y Gamma_Y + Gamma_Y D_Y) tensor D_X=0,
```

which proves (3.2). Since a spectral projector of `D_X` commutes with `D_X`,
`P` commutes with `D_tot`. On `Ran(P)`, `D_X P_0=0`, proving (3.3). Restriction
to a `lambda` eigenspace gives (3.4). QED.

This conclusion is stronger than a dimension count. The fields are the
kernel of a declared first-order operator with a declared metric and domain.
The operation does not manufacture them from neutral topology.

## 4. Gauge, shared-circle and chirality transport

Assume a compact gauge group `G` acts unitarily on `H_X^+` and `H_X^-` and

```text
D_+ rho_+(g)=rho_-(g)D_+.
```

Then `P_0` and `G_X` are `G`-equivariant by spectral functional calculus.
Therefore `ker(D_X)` is a canonical `G`-subrepresentation. Its characterwise
chiral multiplicity is

```text
Ind_G(D_+)=[ker D_+]-[ker D_-].                            (4.1)
```

Neither (4.1) nor its sign is recoverable from the ungraded positive operator
`D_X^2`; this is exactly the H4-T18 boundary. Once `D_+`, its grading and its
complex orientation are supplied, however, no separate postprojection
chirality selector is required.

For the selected low-energy group in A47,

```text
G_SM=(SU(3) x SU(2) x U(1)_Y)/Z6,
```

the exact A46/A50 one-family carrier has rows

| lane | complex dimension | `SU3` triality | `SU2` parity | `6Y` |
|---|---:|---:|---:|---:|
| `Q` | 6 | 1 | 1 | 1 |
| `u^c` | 3 | -1 | 0 | -4 |
| `d^c` | 3 | -1 | 0 | 2 |
| `L` | 2 | 0 | 1 | -3 |
| `e^c` | 1 | 0 | 0 | 6 |
| `N^c` | 1 | 0 | 0 | 0 |

The diagonal center generator acts trivially exactly when

```text
2 triality + 3 weak_parity + 6Y = 0 mod 6.                (4.2)
```

Every row satisfies (4.2). The shared-circle theorem additionally proves that
the circle tangent complex has one abelian harmonic coordinate, that it acts
with these A50 weights, and that its six cover lifts have identical descended
matter action. This fixes the representation-level circle lane. It does not
construct a selected four-dimensional gauge connection.

## 5. Quadratic action and BV-pairing reduction

Let `(phi_a)` be the normalized basis of `ker(D_X)` supplied by `AMK`. Define

```text
I_0((psi_a)_a)=sum_a psi_a tensor phi_a,
P_0(Psi)_a=<phi_a,Psi>_X.
```

The density certificate gives `P_0 I_0=I`. For the product quadratic action

```text
S_tot^(2)(Psi)=1/2 <Psi,D_tot Psi>_(Y x X),
```

equations (3.3) and orthonormality imply

```text
S_tot^(2)(I_0 psi)=1/2 sum_a <psi_a,D_Y psi_a>_Y.         (5.1)
```

Thus the free kinetic normalization is fixed by the same fiber density that
normalizes the zero modes. A separate coefficient can appear only if it is
present in the upper action or density ledger; it cannot be silently inserted
after reduction.

The cotangent lift is

```text
I_BV=I_0 direct_sum P_0^!,
P_BV=P_0 direct_sum I_0^!.
```

It preserves the canonical BV pairing. This is the associated-matter instance
of H4-T16. Together with (5.1), it supplies a nonzero field-only quadratic
action, rather than relabeling the internal cotangent Hamiltonian whose zero
section vanishes.

The statement is classical and free. A QME-preserving elimination of the
massive complement still requires the determinant-line, anomaly and
renormalized pushforward rows in the physical `BV4` packet.

## 6. Causal modes and the complement gap

For a compact internal elliptic problem, `D_X` has discrete spectrum. Assume
the nonzero spectrum satisfies

```text
abs(lambda)>=mu>0.                                        (6.1)
```

Then

```text
norm(G_X)<=1/mu,
norm((D_X^2|_Q)^-1)<=1/mu^2.                              (6.2)
```

The bounds follow directly from the spectral theorem. They are internal or
Euclidean-normal bounds, not Lorentzian resolvent estimates.

On a globally hyperbolic `Y4`, each operator in (3.4) is Dirac type with a
normally hyperbolic square differing only by the lower-order scalar
`lambda^2`. Under the declared domain and support hypotheses it therefore has
advanced and retarded Green maps. Direct sums of these mode operators are
Green-hyperbolic. This uses the standard Green-hyperbolic operator theorem,
not an MTT-specific causal postulate.

The compiler consequence is precise:

```text
causal prescription = supplied by EXT4,
mode masses          = internal eigenvalues,
massless fields      = internal kernel,
charges/chirality    = equivariant graded kernel.
```

The internal positive Hessian does not choose retarded versus advanced
support. It supplies the spectrum and gap; `EXT4` supplies causal orientation.

## 7. Interaction rows

Suppose the selected upper action contains a multilinear vertex `B_n`. On
normalized internal modes the corresponding four-dimensional coefficient is

```text
c_(a1...an)=<phi_a0,B_n(phi_a1,...,phi_an)>_X             (7.1)
```

with the appropriate density, grading and contractions. Therefore the
interaction coefficients are deterministic once the upper action and modes
are known. Equation (7.1) is a compiler, not a value source. In particular,
it does not derive Yukawa magnitudes from the A46 representation table alone.

This identifies the hard physical row sharply: q79 must emit the selected HYM
metric, normalized bundle-valued modes and upper vertex. The overlap values
must then be calculated from (7.1) with interval/error certificates. They may
not be imported from observed masses.

## 8. Exact `3 x 16 = 48` witness

Let `H_16` be the one-family carrier in Section 4. Set

```text
H_X^+ = Q^4 tensor H_16,
H_X^- = Q tensor H_16,
D_+   = [I_16 0 0 0].
```

Then

```text
rank(D_+)=16,
dim ker(D_+)=48,
dim ker(D_-)=0,
Ind_G(D_+)=3[H_16].                                      (8.1)
```

The self-adjoint completion acts on an 80-dimensional carrier. Its square is
the identity on the 32-dimensional paired complement and zero on the
48-dimensional chiral kernel. Hence

```text
mu=1,
G_X=D_X,
D_X G_X=G_X D_X=Q_0.
```

Use the two-dimensional external witness

```text
D_Y=[[0,1],[1,0]],
Gamma_Y=diag(1,-1).
```

The resulting 160-dimensional product operator verifies (3.2) exactly. Its
96-dimensional retained subspace is exactly `D_Y tensor I_48`; the complement
normal has eigenvalue two in this finite witness.

The executable also verifies:

- all six A46/A50 `Z6` congruences;
- one-family and three-family `U(1)`, mixed and nonabelian anomaly sums;
- even weak-doublet parity;
- equivariance of `D_+`, `P_0` and `G_X` for the shared-circle weights;
- exact projector, Green and grading identities; and
- exact reduced quadratic and cotangent pairings on independent samples.

The witness is deliberately universal. Its zeros in the last three family
blocks encode the theorem's index model; they are not claimed to be the
selected differential of the physical q79 bundle.

## 9. What changes in `BV4`

The associated-matter lane no longer needs independent postprojection rows
for its free fields, charges, chirality, kinetic form and causal mode labels.
They factor through `AMK+EXT4+DEN`:

| `BV4` clause | Status after `CBF.T13` | Physical q79 input still required |
|---|---|---|
| `C1` primal matter contraction | exact compiler | selected normalized q79 kernel and complement |
| `C2` cotangent lift | exact compiler | same selected density and physical BV grading |
| `C3` representation/chirality | exact compiler | selected equivariant first-order operator and real structure |
| `C4` matter density | exact reduction identity | physical HYM density, volume and scales |
| `C5` free matter action | exact reduction identity | selected upper quadratic action |
| `C8` matter causal modes | exact conditional compiler | selected `Y4`, domains, gauge fixing and support prescription |
| `C9` complement control | exact classical gap bound | determinant orientation, anomaly and QME pushforward |

Still outside this theorem are:

1. the physical q79 `V3/W9` endpoint, common HYM chamber and metric;
2. the complete coframe, gauge, Higgs, dilaton, `B`-field, ghost and antifield
   stack;
3. the selected nonlinear field-only upper action and its overlap values;
4. a selected four-dimensional gauge background, not merely its group;
5. full reality/statistics/domain matching across every field lane;
6. the quantum BV pushforward, QME and renormalization; and
7. physical normalization and dimensional parameter values.

Accordingly the current q79 decision remains

```text
RETAINED_ASSOCIATED_MATTER_EXTERNALIZATION_COMPILER_ONLY.
```

It is not `FULL_BV_COMPACTIFICATION_CLOSED`.

## 10. Best parallel attack on the physical rows

The q79 endpoint worker should continue `ETA9.QD1` and the joint root/HYM
selection. This repository can proceed independently in the following order:

1. **Freeze the AMK instance contract.** The q79 worker must export `D_+`, its
   grading, normalized kernel basis, characterwise index, `P_0`, `G_X` and
   gap from one root hash.
2. **Build the bosonic companion compiler.** Repeat the exact externalization
   analysis for gauge/coframe/Higgs zero modes, keeping first-order and
   positive-Hessian roles separate.
3. **Prove the action-density reduction.** Express all retained couplings as
   same-source fiber overlaps and isolate every physical normalization.
4. **Bind to the accepted causal BV complex.** Verify principal symbols,
   domains, retarded/advanced maps and real structures field by field.
5. **Execute the massive-mode pushforward.** Only after the physical gap and
   action exist, prove the determinant/anomaly/QME rows.

Steps 2 through 4 can be developed as source-independent compilers now. Their
physical instantiations remain blocked by `B.HS.01` and `B.ACTION.01`.

## 11. Frontier decision

Closed here:

- exact product-Dirac square and zero-mode externalization;
- exact transport of charged representations and characterwise chirality;
- exact free quadratic-action and cotangent-pairing reduction;
- modewise Green-hyperbolic consequence under explicit causal hypotheses;
- exact internal complement-gap bounds;
- exact `3 x 16 = 48` A46/A50 witness with shared-circle and `Z6` descent; and
- a machine contract reducing the associated-matter part of `BV4` to named
  same-source inputs.

Not closed here:

- any selected q79 physical `AMK`, `EXT4` or density instance;
- the complete physical `BV4` packet;
- interaction/Yukawa values;
- the rank-102 continuum operator;
- quantum BV/QME completion; or
- `B.HS.01`, `B.GEO.01` or `B.ACTION.01`.

The physical acceptance counts remain unchanged. The dependency graph does
change: once q79 emits the named first-order kernel packet, its free
associated-matter `BV4` rows are calculations, not additional physical source
choices.

## 12. Verification and sources

Run:

```powershell
python build_q79_bv4_associated_matter_externalization.py
python verify_q79_bv4_associated_matter_externalization.py
python verify.py
```

The generated packet is
`q79_bv4_associated_matter_externalization.packet.json` and the instance schema
is `q79_bv4_associated_matter_externalization_contract.schema.json`.

The Green-hyperbolic consequence uses Christian Baer,
*Green-hyperbolic operators on globally hyperbolic spacetimes*,
<https://arxiv.org/abs/1310.0738>. The product square, kernel reduction,
equivariant-index transport and exact finite witness are proved and replayed
directly here.

Version 1 introduces the associated-matter externalization compiler and
separates its exact universal consequences from the still-open selected q79
source and full BV compactification.
