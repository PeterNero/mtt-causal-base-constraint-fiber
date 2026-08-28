# Causal-Base Constraint-Fiber Compression-Leakage Theorem v1

## Status

```text
Mathematical identity:       EXACT_GENERAL
Finite witness:              EXACT_BENCHMARK
MTT source selection:        OPEN
Kernel authority promotion:  NOT YET REVIEWED
Continuous fit parameters:   0
Observed physical inputs:     0
```

The operator identity below is elementary and belongs to established
compression/Toeplitz/Hankel mathematics. The contribution of this packet is not
to claim a globally new identity. It is to give MTT a precise typed separation
between:

1. noncommutativity caused by crossing the retained/excluded constraint split;
2. preservation of locality on the projector-compatible local algebra; and
3. genuinely open selection of the physical projector and observables.

## 1. Setup

Let `H` be a complex Hilbert space. Let `P` be an orthogonal projector and set

```math
Q=I-P.
```

For a bounded operator `T` define its compression to `P H` by

```math
\Phi_P(T)=PTP\big|_{P\mathcal H}.
```

Boundedness is used so that every product below is defined everywhere. An
unbounded extension requires a common invariant core, closability and domain
control; that is a separate roadmap item.

## 2. Multiplicative defect

### Lemma 1

For bounded operators `S,T`,

```math
\Phi_P(S)\Phi_P(T)-\Phi_P(ST)
=-PSQTP\big|_{P\mathcal H}.
```

### Proof

Using `P=I-Q` between `S` and `T`,

```math
PSPTP
=PS(I-Q)TP
=PSTP-PSQTP.
```

Restriction to `P H` gives the result. QED.

Compression is therefore a unital completely positive map, but it is generally
not a homomorphism. Its failure of multiplicativity is exactly an excursion
through the excluded sector `Q H`.

## 3. Exact commutator decomposition

### Theorem 2

For bounded operators `A_tilde,B_tilde`,

```math
[\Phi_P(\widetilde A),\Phi_P(\widetilde B)]
=\Phi_P([\widetilde A,\widetilde B])
 +P(\widetilde BQ\widetilde A-\widetilde AQ\widetilde B)P
 \big|_{P\mathcal H}.
```

If the upper operators are self-adjoint, define leakage maps

```math
L_A=Q\widetilde A P:P\mathcal H\longrightarrow Q\mathcal H,
\qquad
L_B=Q\widetilde B P:P\mathcal H\longrightarrow Q\mathcal H.
```

If they also commute upstairs, then

```math
\boxed{
[\Phi_P(\widetilde A),\Phi_P(\widetilde B)]
=L_B^*L_A-L_A^*L_B.}
```

Consequently,

```math
\left\|[\Phi_P(\widetilde A),\Phi_P(\widetilde B)]\right\|
\le 2\|L_A\|\,\|L_B\|
\le 2\|[\widetilde A,P]\|\,\|[\widetilde B,P]\|.
```

For noncommuting upper operators the more general bound is

```math
\left\|[\Phi_P(\widetilde A),\Phi_P(\widetilde B)]\right\|
\le \|[\widetilde A,\widetilde B]\|
 +2\|L_A\|\,\|L_B\|.
```

### Proof

Antisymmetrizing Lemma 1 gives

```math
\begin{aligned}
[P\widetilde A P,P\widetilde B P]
&=P[\widetilde A,\widetilde B]P
  +P(\widetilde BQ\widetilde A-\widetilde AQ\widetilde B)P.
\end{aligned}
```

For self-adjoint upper operators,

```math
P\widetilde BQ\widetilde AP=L_B^*L_A,
\qquad
P\widetilde AQ\widetilde BP=L_A^*L_B.
```

If the upper commutator vanishes, only the leakage term remains. The norm bound
follows from submultiplicativity and the triangle inequality. Finally,

```math
[\widetilde A,P]P
=\widetilde AP-P\widetilde AP
=Q\widetilde AP=L_A,
```

and similarly for `B_tilde`. QED.

### Corollary 3: exact criterion

For commuting self-adjoint upper operators, their compressions commute if and
only if

```math
L_B^*L_A=L_A^*L_B.
```

Zero leakage for either operator is sufficient but not necessary: nonzero
leakage terms can cancel. In particular, if `P` reduces both upper operators,
then both leakage maps vanish and commutativity descends.

### Corollary 4: approximate compatibility

If the upper operators commute and

```math
\|[\widetilde A,P]\|\le\varepsilon_A,
\qquad
\|[\widetilde B,P]\|\le\varepsilon_B,
```

then

```math
\|[\Phi_P(\widetilde A),\Phi_P(\widetilde B)]\|
\le 2\varepsilon_A\varepsilon_B.
```

The lower noncommutativity is second order in the two compatibility defects.

## 4. Locality guardrail

Let `O -> A_U(O)` be an upper local net over a globally hyperbolic causal base.
Define the coherent-preserving subalgebra

```math
\mathcal A_U^P(O)
=\{A\in\mathcal A_U(O):[A,P]=0\}
```

and the compressed net

```math
\mathcal A_P(O)
=\{PAP|_{P\mathcal H}:A\in\mathcal A_U^P(O)\}.
```

### Theorem 5: compatible locality descent

If the upper net is isotonic and spacelike separated upper algebras commute,
then the compressed coherent-preserving net is isotonic and spacelike local.

### Proof

Isotony follows by set inclusion. If `O_1` and `O_2` are spacelike and
`A in A_U^P(O_1)`, `B in A_U^P(O_2)`, then `[A,B]=0` by upper locality and
`L_A=L_B=0` by projector compatibility. Theorem 2 gives

```math
[PAP,PBP]|_{P\mathcal H}=0.
```

QED.

This theorem transports locality; it does not manufacture locality from an
arbitrary nonlocal projector. If two spacelike upper operators fail to preserve
the retained sector, their compressed commutator can contain a leakage term.
Such operators cannot both be admitted into the physical local algebra without
an additional localization theorem.

This is the key conceptual separation:

```text
upper spacetime commutator       -> interaction locality or its failure
off-diagonal P/Q leakage         -> constraint-reduction incompatibility
nonfactorizing state             -> entanglement
```

These are different mathematical objects.

## 5. Exact finite witness

Work on `C^3` and let

```math
P=I-\frac13\mathbf 1\mathbf 1^{\mathsf T}
=\frac13
\begin{pmatrix}
2&-1&-1\\
-1&2&-1\\
-1&-1&2
\end{pmatrix},
\qquad
Q=\frac13\mathbf 1\mathbf 1^{\mathsf T}.
```

Then `P` has rank two and projects onto the sum-zero plane. Choose two commuting
self-adjoint upper observables

```math
\widetilde X=\operatorname{diag}(1,0,0),
\qquad
\widetilde Y=\operatorname{diag}(0,1,0).
```

Their compressions are

```math
X_P=\frac19
\begin{pmatrix}
4&-2&-2\\
-2&1&1\\
-2&1&1
\end{pmatrix},
\qquad
Y_P=\frac19
\begin{pmatrix}
1&-2&1\\
-2&4&-2\\
1&-2&1
\end{pmatrix}.
```

Although `[X_tilde,Y_tilde]=0`,

```math
[X_P,Y_P]
=\frac19
\begin{pmatrix}
0&-1&1\\
1&0&-1\\
-1&1&0
\end{pmatrix}
\ne0.
```

The verifier establishes exactly that

```math
[X_P,Y_P]=L_Y^*L_X-L_X^*L_Y,
\qquad
[X_P,Y_P]^*[X_P,Y_P]=\frac1{27}P.
```

Hence the commutator has rank two and operator norm `1/sqrt(27)`. Both leakage
maps have squared operator norm `2/9`, so the theorem's bound reads

```math
\frac1{\sqrt{27}}\le\frac49.
```

The witness uses no fitted number or measured physical input. It proves
possibility, not physical selection.

## 6. Uncertainty consequence and boundary

For normalized `psi in P H`, bounded self-adjoint compressed observables obey
the standard Robertson inequality

```math
\Delta_\psi A\,\Delta_\psi B
\ge \frac12
\left|\langle\psi,
(L_B^*L_A-L_A^*L_B)\psi\rangle\right|
```

when the upper pair commutes. This rewrites an existing uncertainty bound in
terms of constraint leakage. It does not determine a universal lower constant.

In finite dimension `Tr([A,B])=0`, so no nonzero exact relation
`[A,B]=i c I` can hold. The finite witness therefore cannot be promoted to the
canonical commutation relation. A selected infinite-dimensional or controlled
limit construction and an action/symplectic normalization are still required.

## 7. MTT interpretation at the allowed tier

If a future selected closure-repair dynamics emits `P`, then `L_A` measures how
an upper operation tries to leave the retained fixed/coherent tangent sector.
The lower commutator records the oriented mismatch between two such excursions.
This supports a precise candidate reading:

> Some lower incompatibility may be the shadow of jointly imposing an upper
> constraint, while physical spacetime locality is retained on the compatible
> local algebra.

The word "may" is essential. The current packet does not identify the selected
q79 `P`, physical position and momentum, a universal apparatus, or the missing
upper action. Those remain governed by `B.ACTION.01`, `B.GEO.01`, `B.OP.01` and
`B.QM.03` in the kernel snapshot.

## 8. Relation to established mathematics

Compression of multiplication operators to Hardy, Bergman or coherent-state
subspaces is the setting of Toeplitz quantization, and products of the excluded
parts are Hankel terms. The present leakage formula is the abstract projector
version of that familiar mechanism. Relevant primary sources include:

1. M. Schlichenmaier, [Berezin-Toeplitz quantization and Berezin transform](https://arxiv.org/abs/math/0009219).
2. A. Karabegov, [A formal model of Berezin-Toeplitz quantization](https://arxiv.org/abs/math/0607365).
3. I. Chalendar and D. Timotin, [Commutation relations for truncated Toeplitz operators](https://arxiv.org/abs/1305.6739).
4. N. P. Landsman, [Rieffel induction as generalized quantum Marsden-Weinstein reduction](https://arxiv.org/abs/dg-ga/9601009).
5. H. Casini, M. Huerta and J. A. Rosabal, [Remarks on entanglement entropy for gauge fields](https://arxiv.org/abs/1312.1183).
6. W. Donnelly and L. Freidel, [Local subsystems in gauge theory and gravity](https://arxiv.org/abs/1601.04744).

These precedents increase credibility by showing that projection, constraint
reduction, nonmultiplicativity and gauge nonfactorization are established
mathematics. They also prevent an inflated novelty claim. The open scientific
question is whether one selected MTT closure source realizes the required
objects and normalization.
