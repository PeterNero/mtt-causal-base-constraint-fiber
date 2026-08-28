# All-Arity Contraction-Morphism Source-Promotion Theorem v1

**Date:** 2026-08-28  
**Identifier:** `CBF.T11`  
**Tier:** `EXACT_GENERAL + SELECTED_EXACT_FINITE; CONDITIONAL_CONTINUUM`

## 1. Result

The finite q79 response target carries nonzero transferred operations at every
arity. A physical continuum comparison must therefore not be defined as an
unending list of separately matched vertices. This theorem proves that such a
list is unnecessary.

If one source map preserves the differential, product, inclusion, projection
and transfer homotopy, then it preserves every transferred operation
automatically. On the exact q79 finite source, the translation generator and
Fourier quarter-turn satisfy all these identities. They therefore act on the
complete, nontruncating transferred hierarchy, not only on `m2`, `m3` or the
previously enumerated `m4` table.

This closes an all-arity compiler theorem. It does not supply the selected
visible-hidden HYM endpoint or a physical continuum source map.

## 2. Contractions and source maps

Let `(A,d,mu)` and `(A',d',mu')` be differential graded associative algebras.
Suppose

```text
(T,m1)  <--p--  (A,d)  --p'-->  (T',m1')
          --i-->          <--i'--
```

denotes two normalized contractions, written separately as

```text
p i = id_T,             d H + H d = id_A - i p,
p' i' = id_T',          d' H' + H' d' = id_A' - i' p',
```

with the usual side conditions

```text
H^2=pH=Hi=0,            H'^2=p'H'=H'i'=0.
```

Let `Phi:A -> A'` and `Psi:T -> T'` have degree zero. Assume

```text
Phi d = d' Phi,
Phi mu = mu' (Phi tensor Phi),
Phi i = i' Psi,
p' Phi = Psi p,
Phi H = H' Phi.                         (2.1)
```

These are source-bearing identities. They are stronger than agreement of a
few projected matrices or low-order vertices.

## 3. All-arity theorem

Choose one fixed homotopy-transfer sign convention. For example, let the
source kernels be the signed sums over planar binary trees whose internal
vertices carry `mu`, internal non-root edges carry `H`, leaves carry `i`, and
the root carries `p`. Denote the resulting target operations by `m_n` and
`m'_n`.

### Theorem 3.1

Under (2.1), for every `n>=1`,

```text
Psi m_n = m'_n Psi^(tensor n).          (3.1)
```

The conclusion includes a curved arity-zero row if both contractions use the
same curved-tree convention and `Phi` also transports the curvature.

### Proof

For `n=1`, equation (3.1) is the retained chain-map identity, obtained from
the two inclusion or projection squares.

For `n>=2`, take any decorated planar binary tree. Move `Phi` from its root
down toward the leaves. At a product vertex use

```text
Phi mu = mu'(Phi tensor Phi).
```

On every internal edge use `Phi H=H' Phi`. At every leaf use
`Phi i=i' Psi`, and at the root use `p' Phi=Psi p`. The transformed term is
the corresponding primed tree with `Psi` on every input. Degrees are
unchanged, so its Koszul sign is unchanged. Summing all trees proves (3.1).
QED.

The proof is genuinely all-arity. It does not infer an infinite statement
from a finite numerical census.

## 4. Hodge reduction of the hypotheses

The homotopy identity in (2.1) need not always be checked independently.
Suppose `Phi` is unitary onto a closed reducing image, maps the declared closed
domains of `d` and `d*` to those of `d'` and `d'*`, and

```text
Phi d = d' Phi.
```

Then, on those domains,

```text
Phi d* = d'* Phi,
Phi Delta = Delta' Phi.
```

Functional calculus therefore gives

```text
Phi P_harm = P'_harm Phi,
Phi G = G' Phi,
Phi(d*G) = (d'*G')Phi.                 (4.1)
```

Thus a domain-preserving unitary cochain intertwiner with the correct reducing image transports
the harmonic projector, reduced Green and Hodge homotopy automatically. This
agrees with the adjacent curved-projective HYM naturality theorem: Green
naturality is a consequence of operator naturality once the endpoint,
domains and metric have actually been supplied.

Equation (4.1) is not available for a merely approximate, nonunitary or
nonreducing map. Such a map must use the already established `FSB.03b`
defect majorants.

## 5. Equivariant corollary

Let a group `Gamma` act on `A` by DGA automorphisms preserving `i`, `p` and
`H`. Define its target action by

```text
rho_T(g)=p rho_A(g) i.
```

The contraction squares make `rho_T` a group representation, and Theorem 3.1
gives

```text
rho_T(g) m_n
  =m_n rho_T(g)^(tensor n)             (5.1)
```

for every `g` and every `n`. Consequently source covariance cannot be lost at
a later transferred arity. Conversely, target covariance at finitely many
arities does not prove source covariance.

## 6. Exact q79 execution

The source is the established 144-dimensional symmetric crossed-exterior
qutrit Weyl DGA over `Q(omega)`. The target is the established

```text
T = old q79 response complex direct-sum higher-jet harmonic ideal,
dim(T)=48.
```

Its normalized contraction is the previously verified triple `(i,p,H)`.
For both source generators

```text
t = affine translation,
F = Fourier quarter-turn,
```

the new packet checks exactly:

- commutation with `d` on all 144 source basis elements;
- preservation of `mu` on all 20,736 source basis pairs;
- preservation of `i` on all 48 target basis elements;
- preservation of `p` and `H` on all 144 source basis elements;
- preservation of `m1` and `m2` on all target basis elements and pairs;
- monomiality of the induced target actions;
- orders three and four for `t` and `F`;
- an order-six affine subgroup and faithful order-36 generated covariance
  group on the target; and
- exact regression probes on the nontruncating family through arity eight.

The low-arity target checks and selected higher probes are regression tests.
Equation (5.1), proved from the source and contraction identities, is what
establishes every arity.

The order-36 group is an exact finite covariance group. This theorem does not
identify it with physical q79 holonomy.

## 7. Continuum source-promotion contract

The theorem changes the eventual endpoint test. Once a selected source emits
an exact continuum map satisfying the source and contraction squares, these
rows become consequences:

```text
adjoint and Laplacian naturality,
harmonic projector and Green naturality,
transfer-homotopy naturality,
every A-infinity operation,
every source-preserved covariance identity.
```

They are not independent physical inputs.

The still-open endpoint rows are:

1. a source-hashed visible-hidden HYM endpoint and common chamber;
2. a typed unitary continuum-to-finite map on declared Sobolev domains;
3. differential, product and retained-projector intertwining, or certified
   defects with a convergent tail majorant;
4. the selected physical `C4`/monodromy lift;
5. rank-102 coefficient arrays, `QHP` or Feshbach decision, inverse and tail
   bounds;
6. a same-source cyclic/BV or Lorentzian action, real slice, pairing and
   normalization; and
7. BV-compatible externalization to the accepted four-dimensional fields.

The packet records these as `EP.01` through `EP.07`, presently `0/7` accepted.
This count is deliberately strict: the universal compilers do not fill
physical source rows.

## 8. Relation to the initial thesis

The result gives a precise version of the claim that complicated projected
rules can be controlled by simpler preprojection structure. The lower theory
has infinitely many coherent operations, yet their covariance can be proved
once at the upper differential, product and contraction level.

This does not prove that bundle directions are non-spatiotemporal, that the
finite model is nature's selected reduction, or that entanglement and gauge
are both generated by this one source. It proves the mathematical mechanism
that such a physical theorem would use.

## 9. Frontier decision

Closed here:

- all-arity functoriality of homotopy transfer under a contraction-preserving
  DGA morphism;
- exact all-arity covariance of the finite q79 transferred hierarchy;
- faithful descent of the order-36 finite covariance action to the response
  target; and
- replacement of infinitely many exact vertex-matching obligations by a
  finite source-level contract.

Still open:

- `B.HS.01`, because the physical endpoint is not selected;
- `B.GEO.01`, because no continuum source map or physical `C4` lift is
  instantiated;
- `B.OP.01`, because no selected rank-102 arrays or tail bounds are emitted;
- `B.ACTION.01`, because the physical action and compactification map are not
  supplied.

The next physical object is therefore not `m6`, another generic polar
compiler, or a renamed finite covariance packet. It is the selected endpoint
map filling `EP.01` through `EP.04`; after that, this theorem transports the
entire hierarchy in one step.

## 10. Verification

Run:

```powershell
python build_q79_all_arity_source_promotion.py
python verify_q79_all_arity_source_promotion.py
python verify.py
```

The generated packet is
`q79_all_arity_source_promotion.packet.json`.

## 11. Sources and version delta

The planar-tree proof uses the homotopy-transfer recursion of S. A. Merkulov,
*Strongly homotopy algebras of a Kahler manifold*, arXiv:math/9809172. The
continuum comparison consumes, without reopening, `FSB.03a-c`, the q79 curved
projective-module HYM naturality theorem, and the H4-T10/H4-T15 action and BV
boundaries locked in the source manifest.

Version 1 adds the missing all-arity morphism theorem and executes its finite
q79 hypotheses. Earlier packets proved individual operations, support cutsets
and nontruncation; this theorem proves their simultaneous covariance and
freezes the physical endpoint rows required for promotion.
