# Repair, Fixed-Point, and Gauge-Descent Theorem v1

## Status

```text
Abstract theorem:             EXACT_GENERAL
Finite equivariant witness:   EXACT_BENCHMARK
A47 gauge group:              CONSUMED AT ITS ESTABLISHED TIER
Physical q79 repair source:   OPEN
Continuous fit parameters:    0
Observed physical inputs:     0
```

This theorem connects three structures that must otherwise be kept separate:

1. a nonlinear repair or closure law;
2. its fixed point and tangent spectral projector;
3. the faithful symmetry acting after reduction.

It does not derive the MTT physical action or the Standard Model gauge group.
Authority `A47` remains the owner of the latter result.

## 1. Equivariant repair setup

Let `H` be a complex Hilbert space, let `U` be an open subset, and let

```math
\mathcal F:U\longrightarrow\mathcal H
```

be continuously Frechet differentiable. Let a group `G` act by bounded unitary
operators `U_g` and suppose the repair law is equivariant:

```math
\mathcal F(U_g u)=U_g\mathcal F(u).
```

Let `u_*` be a fixed point of the repair law,

```math
\mathcal F(u_*)=0,
```

and let `G_*` be the stabilizer of the background:

```math
G_*=\{g\in G:U_g u_*=u_*\}.
```

Write

```math
J_*=D\mathcal F(u_*).
```

## 2. Linearization and spectral projector

### Theorem 1: stabilizer-linearization intertwining

For every `g in G_*`,

```math
J_*U_g=U_gJ_*.
```

### Proof

For `v in H`, equivariance and stabilization of `u_*` give

```math
\mathcal F(u_*+tU_gv)
=\mathcal F(U_g(u_*+tv))
=U_g\mathcal F(u_*+tv).
```

Differentiate at `t=0`. QED.

If the background is not fixed but is moved along its orbit, the corresponding
statement is

```math
D\mathcal F(U_gu_*)
=U_gJ_*U_g^{-1}.
```

Thus tangent operators and their spectral data form an equivariant family over
the orbit.

### Theorem 2: Riesz-projector descent

Suppose an isolated spectral cluster of `J_*` is enclosed by a contour `Gamma`
in the resolvent set, and define

```math
P=\frac{1}{2\pi i}\int_\Gamma(zI-J_*)^{-1}\,dz,
\qquad Q=I-P.
```

Then every `U_g`, `g in G_*`, commutes with `P` and `Q`. If `J_*` is
self-adjoint and the cluster is real, `P` is an orthogonal projector.

### Proof

Theorem 1 implies

```math
U_g(zI-J_*)^{-1}=(zI-J_*)^{-1}U_g
```

throughout the resolvent set. Integrating around `Gamma` proves
`U_gP=PU_g`; the statement for `Q` follows. QED.

This is the exact abstract link to the Fixed Points I and IV spine. The fixed
point does not merely coexist with a projector: under a gap hypothesis, its
tangent operator determines the projector, and repair symmetries preserve it.

For the remaining compression, leakage and local-net statements, assume the
self-adjoint case so that `P` is orthogonal.

## 3. Covariance of compression and leakage

Let

```math
\Phi_P(A)=PAP|_{P\mathcal H},
\qquad
L_A=QAP:P\mathcal H\longrightarrow Q\mathcal H.
```

Let `alpha_g(A)=U_gAU_g^{-1}`. Since the `P/Q` split is invariant, write the
restricted representations as `U_{g,P}` and `U_{g,Q}`.

### Theorem 3: covariant shadows

For `g in G_*`,

```math
\Phi_P(\alpha_g(A))
=U_{g,P}\Phi_P(A)U_{g,P}^{-1},
```

and

```math
L_{\alpha_g(A)}
=U_{g,Q}L_AU_{g,P}^{-1}.
```

Consequently, the compression-leakage commutator form

```math
\Omega_P(A,B)=L_B^*L_A-L_A^*L_B
```

is equivariant:

```math
\Omega_P(\alpha_g(A),\alpha_g(B))
=U_{g,P}\Omega_P(A,B)U_{g,P}^{-1}.
```

### Proof

Insert `U_gP=PU_g` and `U_gQ=QU_g` into each definition. QED.

The symbol `Omega_P` is an antisymmetric leakage form. It is not called a
differential-geometric curvature until a selected connection theorem identifies
it as one.

## 4. Faithful quotient

Let `A_phys` be the accepted reduced observable algebra and assume it is
preserved by the reduced `G_*` action. Define

```math
K_{\rm phys}
=\{g\in G_*:
\operatorname{Ad}(U_{g,P})(A)=A
\text{ for every }A\in\mathcal A_{\rm phys}\}.
```

### Theorem 4: physical action factors through a quotient

`K_phys` is a normal subgroup of `G_*`, and the action on `A_phys` factors
faithfully through

```math
G_{\rm faithful}=G_*/K_{\rm phys}.
```

### Proof

`K_phys` is the kernel of the homomorphism

```math
G_*\longrightarrow\operatorname{Aut}(\mathcal A_{\rm phys}),
\qquad
g\longmapsto\operatorname{Ad}(U_{g,P}).
```

Every group-action kernel is normal, and quotienting by the kernel gives a
faithful image. QED.

This theorem distinguishes three notions:

- a symmetry of the repair source;
- a redundancy acting trivially on accepted physical observables;
- a faithful physical symmetry after quotienting.

Calling the whole source group "gauge" requires a locality and redundancy
interpretation; algebra alone does not make that decision.

## 5. Local-net version

Suppose `G_*` acts by vertical bundle automorphisms preserving base regions and
an upper local net `O -> A_U(O)`. On the coherent-preserving subalgebra

```math
\mathcal A_U^P(O)=\{A\in\mathcal A_U(O):[A,P]=0\},
```

Theorems 2 and 3 imply a covariant compressed net. Combined with the compatible
locality theorem in the first packet, spacelike commutativity is preserved.
The quotient in Theorem 4 then acts on this local physical net.

This is the precise form of the statement that upper bundle symmetry can govern
four-dimensional gauge structure without acting as a superluminal channel.

## 6. Corollary for the established A47 result

Authority `A47` establishes, from selected native bundle tensors, the faithful
low-energy group

```math
G_{\rm A47}
=\frac{SU(3)\times SU(2)\times U(1)}{\mathbb Z_6}.
```

The present theorem gives a conditional upstream interpretation:

> If one selected MTT repair source is equivariant under the native-tensor
> automorphism group, its selected fixed background and Riesz projector obey the
> hypotheses above, and its reduced observable kernel is exactly the diagonal
> `Z6` already certified by `A47`, then its faithful reduced symmetry is
> `G_A47` and all compression/leakage data transform covariantly.

The antecedent is not yet established. In particular, the physical repair law,
HYM endpoint, projector, connection and continuum transfer remain governed by
`B.ACTION.01`, `B.HS.01`, `B.GEO.01` and `B.OP.01`.

## 7. Exact finite witness

Let `H=R^3`,

```math
P=I-\frac13\mathbf1\mathbf1^{\mathsf T},
\qquad
Q=\frac13\mathbf1\mathbf1^{\mathsf T},
```

and define

```math
H_0=2P+5Q
=\begin{pmatrix}
3&1&1\\
1&3&1\\
1&1&3
\end{pmatrix}.
```

Consider the nonlinear repair map

```math
\mathcal F(u)=H_0u+(u^{\mathsf T}u)u.
```

Its unique fixed point is zero because

```math
u^{\mathsf T}\mathcal F(u)
=2\|Pu\|^2+5\|Qu\|^2+\|u\|^4,
```

which is positive for `u != 0`. The tangent operator at zero is `H_0`; its low
eigenvalue is two on `P H`, its high eigenvalue is five on `Q H`, and its gap is
three.

Let

```text
G_12 = {epsilon R_sigma : epsilon in {+1,-1}, sigma in S3},
```

where `R_sigma` is a coordinate-permutation matrix. Every group element is
orthogonal, preserves the Euclidean norm, commutes with `H_0`, and therefore
preserves the nonlinear repair law and its spectral projector.

On the full retained operator algebra `P M_3(R) P`, the conjugation kernel is
exactly `{+I,-I}`. Thus the faithful quotient has order six. The example is not
the Standard Model gauge group; it is a zero-fit exact witness of Theorems 1-4,
including a nontrivial central kernel.

The generated certificate verifies the group law, fixed-point source,
eigensplitting, kernel quotient, compression covariance and leakage covariance
with exact rational arithmetic.

## 8. Fixed Points interpretation

The theorem fits the existing series without moving theorem ownership:

- **FP I:** supplies the analytic fixed-point and spectral-bundle setting.
- **FP II:** places the projector in the declared `4+6` model, conditionally.
- **FP III:** controls decay and disturbance in `Q` modes.
- **FP IV:** replaces an obsolete projector by the curved Riesz projector when
  curvature moves the low cluster; `Q R P` is the corresponding linear leakage
  when the old projector is retained.
- **FP V:** keeps admissibility margins distinct from forces or energies.
- **FP VI:** preserves the boundary between the formal spine and physical
  interpretation.

The new contribution is the equivariant connective tissue: a symmetry of one
repair law automatically descends through its fixed-point linearization and
Riesz projector, with a precise faithful quotient on physical observables.
