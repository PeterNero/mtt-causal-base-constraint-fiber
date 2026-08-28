# Cohesive Repair, Compression and Transfer Comparison Theorem v1

## Status

```text
General propagated-excursion identity:       EXACT_GENERAL
Pinned cohesive benchmark extraction:        EXACT_BENCHMARK
Pinned Nil Hodge/A-infinity comparison:       EXACT_BENCHMARK
Pinned Feshbach comparison:                   EXACT_BENCHMARK
Direct equality with -PSQTP:                  DISPROVED IN GENERAL
Shared excursion architecture:                PROVED
Selected physical q79 realization:            OPEN
Continuous fit parameters:                    0
Observed physical inputs:                     0
```

The result decides a concrete question left by the compression-leakage and
closure-repair packets: is the raw compression defect

```math
-PSQTP
```

already the transferred `A_infinity` or Feshbach correction? The answer is no
in general and no on the available exact nontrivial witnesses. The three
constructions share a precise excursion skeleton, but the transferred theories
insert different propagation data in the excluded sector.

This distinction matters. It prevents an unweighted projector identity from
being promoted into a dynamical effective interaction without the Green,
homotopy or resolvent object that actually carries the virtual excursion.

## 1. Pinned source extraction

The source lock fixes six files from Closure Dynamics at commit
`aafecf2201ab5573b63968175592062d91d10a0a` and one Feshbach certificate from
the QM source repository at commit
`cd3c13b665d6712dd78655cf0d2007231f634065`. Each file is pinned by repository,
branch, commit, Git blob and SHA-256. The adjacent repositories are read-only
inputs; this repository contains the machine-independent reconstruction.

### Cohesive Maurer-Cartan repair witness

The finite cohesive witness has

```math
\Phi(y_1,y_2)=(y_2+y_2^2,y_1),
\qquad
E(y)=\frac12\|\Phi(y)\|^2,
\qquad
u_*=0.
```

Therefore

```math
D\Phi(0)=
\begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad
\operatorname{Hess}E(0)=I_2,
\qquad
D(-\nabla E)(0)=-I_2.
```

The canonical fixed-mode projector is the spectral projector onto the kernel of
the Hessian. Here

```math
P_{\rm fix}=0,
\qquad Q_{\rm fix}=I_2,
\qquad G_Q=(\operatorname{Hess}E|_{Q})^{-1}=I_2.
```

Thus this witness proves the nonlinear-repair-to-Hodge linearization, but it has
no nonzero retained tangent mode. Every `P_fix` compression, raw defect and
Feshbach correction vanishes. A nontrivial rank-one projector cannot be selected
from `I_2` by spectral calculus because its only eigenvalue is fully degenerate.

This is the first decisive boundary: the cohesive witness by itself cannot test
a nonzero compression/transfer identification.

## 2. Propagated excursion theorem

Let `P` be an orthogonal projector on a Hilbert space, let `Q=I-P`, and let
`R=QRQ` be any bounded excluded-sector propagator. For bounded `S,T`, define

```math
\mathcal E_R(S,T)=PSRTP|_{P\mathcal H}.
```

The raw compression defect is

```math
\mathcal D_Q(S,T)
=\Phi_P(S)\Phi_P(T)-\Phi_P(ST)
=-\mathcal E_Q(S,T).
```

Define the propagated defect by

```math
\mathcal D_R(S,T)=-\mathcal E_R(S,T).
```

Then exactly

```math
\boxed{
\mathcal D_R(S,T)-\mathcal D_Q(S,T)
=-PS(R-Q)TP.}
```

Consequently

```math
\mathcal D_R(S,T)=\mathcal D_Q(S,T)
\quad\Longleftrightarrow\quad
PS(R-Q)TP=0,
```

and

```math
\|\mathcal D_R-\mathcal D_Q\|
\le
\|PSQ\|\,\|R-Q\|\,\|QTP\|.
```

### Proof

Because `R=QRQ`, both excursion terms pass through the same excluded sector.
Subtracting their definitions gives

```math
-PSRTP+PSQTP=-PS(R-Q)TP.
```

The equality criterion is immediate. Submultiplicativity gives the norm bound.
QED.

This theorem supplies the exact common architecture:

```text
retained state -> leave through Q -> propagate in Q -> return to P.
```

The propagator is not optional data. Different propagators define different
effective theories even when they use the same `P/Q` split.

## 3. Feshbach specialization

For a self-adjoint `H` and spectral parameter `z`, assume the excluded block is
invertible and set

```math
G_Q(z)=Q[Q(H-z)Q]^{-1}Q.
```

The Feshbach operator is

```math
F_P(H-z)
=P(H-z)P-PHQG_Q(z)QHP.
```

Its correction is therefore exactly the propagated defect with

```text
R=G_Q(z), S=T=H,
```

not the raw defect with `R=Q`. Equality occurs precisely when

```math
PHQ(G_Q(z)-Q)QHP=0.
```

In the pinned four-dimensional rational witness,

```math
H=
\begin{pmatrix}
1&0&1/2&0\\
0&2&0&0\\
1/2&0&3&0\\
0&0&0&4
\end{pmatrix},
\qquad
P=\operatorname{diag}(1,1,0,0).
```

At `z=0`, the raw `Q` excursion is `diag(1/4,0)` on the retained block, whereas
the resolvent-weighted self-energy is `diag(1/12,0)`. Hence

```math
P H P-P H QG_QQ H P
=\operatorname{diag}(11/12,2).
```

The exact witness disproves a direct Feshbach identification with `-PHQHP`.

## 4. A-infinity specialization

For a Hodge contraction

```math
d h+h d=Q,
\qquad
h=d^*G_Q,
```

homological transfer gives, in the convention used by the pinned packet,

```math
m_3(x,y,z)=
P\mu(h\mu(x,y),z)
-(-1)^{|x|}P\mu(x,h\mu(y,z)).
```

If `L_x(w)=mu(x,w)` and `R_z(w)=mu(w,z)`, this is

```math
m_3(x,y,z)
=\mathcal E_h(R_z,L_x)y
-(-1)^{|x|}\mathcal E_h(L_x,L_y)z.
```

Thus `m3` is a signed sum of two homotopy-propagated excursions. It is not one
binary compression defect. The typing already proves the distinction:

```text
Q and G_Q: degree 0,
h=d*G_Q:   degree -1,
m3:        ternary and degree -1.
```

A direct equality to an unweighted binary `-PSQTP` is ill-typed unless the
homotopy and arity have first been absorbed into explicitly declared operators.

## 5. Exact Nil discriminator

The pinned auxiliary Hodge benchmark is the exterior DGA

```text
A=Lambda(a,b,c),
da=db=0,
dc=a wedge b.
```

With its orthonormal monomial basis,

```text
P projects onto (1,a,b,ac,bc,abc),
Q projects onto (ab,c),
Delta=Q,
G_Q=Q,
h=d*G_Q,
h(ab)=c.
```

For the exact transferred witness `m3(a,a,b)`, the relevant raw excursion is

```math
P L_a Q L_a P(b)=0,
```

but the homotopy-propagated excursion is

```math
P L_a h L_a P(b)=ac.
```

The first planar tree vanishes, the second equals `ac`, and because `|a|=1`,

```math
m_3(a,a,b)=ac.
```

This is an exact same-input discriminator:

```text
raw Q excursion:          0
transferred h excursion: ac
m3:                      ac.
```

Even though `G_Q=Q` in this normalized benchmark, `h=d*G_Q` is not `Q`. The
degree-lowering adjoint is exactly what turns the excluded `ab` direction into
the excluded `c` direction before the final multiplication returns it to the
harmonic `ac` state.

## 6. What is now settled

Closed exactly:

- the extraction of `Phi`, `u_*`, `D Phi(u_*)`, the repair Jacobian and Hessian
  from the cohesive finite benchmark;
- the fact that its canonical fixed tangent projector has rank zero;
- the universal propagated-excursion identity and equality criterion;
- the exact Feshbach specialization with the excluded resolvent;
- the exact `A_infinity` specialization with `h=d*G_Q` and two planar trees;
- a rational witness where the raw compression excursion vanishes but `m3` is
  nonzero;
- zero fitted parameters and zero measured-value inputs.

The correct statement is therefore:

> Compression leakage is the unpropagated excursion skeleton. Feshbach and
> homological transfer are dynamical refinements obtained by inserting the
> appropriate excluded-sector propagator and, for `A_infinity`, summing the
> typed tree channels.

That statement is stronger and more useful than a false equality. It tells the
MTT program exactly which upstream objects must be emitted before lower
interactions can be claimed as consequences of closure repair.

## 7. Physical boundary and next theorem

None of the witnesses is the selected physical q79 operator:

- the cohesive `S_HS` object remains a structural benchmark rather than the
  selected physical `V3/W9` endpoint;
- the Nil DGA is an auxiliary exact transfer benchmark;
- the four-dimensional Feshbach matrix is an exact QM cutset witness;
- no selected q79 harmonic projector, reduced Green operator, homotopy or
  continuum-to-finite product intertwiner has been executed here.

Accordingly `B.ACTION.01`, `B.GEO.01` and `B.OP.01` remain open. Their shared
next object is no longer ambiguous:

```text
selected q79 differential and pairing
  -> Delta_Q and harmonic P_Q
  -> reduced Green G_Q
  -> h_Q=Dbar_Q* G_Q
  -> transferred m2,m3,...
  -> comparison with finite compression and Feshbach data.
```

Only that same-source computation can decide whether the physical finite
operators are invariant restrictions, resolvent-corrected reductions or
homotopy-transferred interactions.

## 8. Reproduction

```powershell
python .\build_cohesive_repair_compression_transfer_comparison.py
python .\verify_cohesive_repair_compression_transfer_comparison.py
python .\verify.py
```

All arithmetic in the executable witnesses is exact rational arithmetic.
