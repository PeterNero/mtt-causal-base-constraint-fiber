# Normalized Orientation, Coframe Density and One-Primitive BV Profile Bridge Theorem v1

**Claim:** CBF.T50

**Date:** 2026-08-31

**Status:** exact selected-branch external coframe-density composition, exact
normalized q79 unit/orientation Frobenius and BV-profile retract, unique
trace-compatible real involution on the retained internal sector, and exact
preservation of the T49 action quantum; the full q79 Hodge real slice,
physical upper field action, complement-mode disposition, associated chiral
operator, Lorentzian full BV domain and QME pushforward remain open

## 1. Result

Three previously separate results fit together without introducing another
normalization parameter.

1. H4-T16 identifies the exact q79 unit/orientation sector

   ```text
   A_or=span_C{1,nu},
   tau(1)=0, tau(nu)=1, nu^2=0.                    (1.1)
   ```

2. MTT-Q79-RCE-01 proves, after the declared `A_QG` and `A_causal`
   inputs, that the response density is the selected q79 coframe density:

   ```text
   mu_response=dV_g_e.                              (1.2)
   ```

3. CBF.T49 proves that the direct scalar, gauge and anchored local-formal
   radial/BV normalization has one shared positive primitive

   ```text
   alpha=f0/hbar.                                   (1.3)
   ```

Define the retained product density by

```text
mu_10=mu_response tensor nu.                        (1.4)
```

Normalized fiber integration gives

```text
Red(mu_10)=mu_response tau(nu)=mu_response.         (1.5)
```

Fields use the internal profile `1`; their BV-dual profiles use `nu`. The
internal pairing is therefore exactly one:

```text
<1,nu>_A=tau(1*nu)=1.                               (1.6)
```

Consequently the external pairing, an already-supplied antifield-linear BV
action and its coefficient reduce without rescaling. In particular,

```text
alpha_upper=alpha_lower.                            (1.7)
```

The normalized orientation sector has a unique unital, degree-preserving,
trace-compatible antilinear involution:

```text
J_A(1)=1, J_A(nu)=nu.                               (1.8)
```

Thus the retained internal profile does not carry an additional continuous
reality or density choice. It does not select the real structure on the other
86 q79 topology modes, the bundle-valued fields or the physical fermionic
carrier.

Before imposing `tau(nu)=1`, an orientation scale would appear as a second
column in the action-amplitude Jacobian. The normalization condition removes
that tangent exactly. After reduction the amplitude rank is still one, and
the number of new continuous normalization primitives is zero.

This is progress on the density, pairing and profile-reality subclauses of the
H4-T15 bridge. It is not an independently selected upper action. The global
H4-T15 decision remains

```text
AUXILIARY_COTANGENT_REDUCTION_ONLY.                 (1.9)
```

## 2. The normalized orientation Frobenius algebra

Let `A_or` have ordered basis `(1,nu)` and product

```text
1*1=1,
1*nu=nu*1=nu,
nu*nu=0.                                            (2.1)
```

The last identity follows by degree on a real six-dimensional compact
internal space. With the trace in (1.1), the cyclic Frobenius pairing is

```text
G_A=[[0,1],[1,0]],
det(G_A)=-1.                                        (2.2)
```

It is nondegenerate. Associativity of (2.1) makes

```text
tau((ab)c)=tau(a(bc))                               (2.3)
```

for every basis triple and hence for all elements.

On this sector the normalized Hodge operation is

```text
star_A(1)=nu,
star_A(nu)=1.                                       (2.4)
```

The positive profile metric is

```text
(a,b)_A=tau(a*star_A(b)),
M_A=I_2.                                            (2.5)
```

Equations (2.1)-(2.5) are the exact H4-T16 orientation subpacket. They do not
assert that the complete q79 Hodge star has been selected.

## 3. Unique retained real involution

Let `J` be a unital, degree-preserving antilinear algebra involution on
`A_or`. Degree preservation and unitality imply

```text
J(1)=1,
J(nu)=lambda nu                                    (3.1)
```

for some complex `lambda`. Trace compatibility requires

```text
tau(J(nu))=overline(tau(nu))=1.                    (3.2)
```

Since `tau(nu)=1`, equation (3.2) gives `lambda=1`. The involution condition
then holds automatically. This proves uniqueness and (1.8).

The fixed locus is

```text
A_or,R=span_R{1,nu}.                                (3.3)
```

It is closed under the product and `star_A`, and (2.5) is positive on it.
This is a genuine real-structure theorem for the retained profile sector. It
is not the Majorana, charge-conjugation or Hermitian reality theorem required
for the complete physical field stack.

## 4. Selected-branch external density

MTT-Q79-RCE-01 uses the selected coframe

```text
e^0=N dt,
e^a=Q_WW^a_i(dx^i+N^i dt).                         (4.1)
```

After `A_QG` and `A_causal`, it proves

```text
det(e)=N det(Q_WW),
sqrt(-det(g_e))=|det(e)|,
mu_response=dV_g_e.                                (4.2)
```

Its exact rational witness has

```text
N=5,
det(Q_WW)=24,
mu_response=120.                                   (4.3)
```

Combining (4.3) with `tau(nu)=1` gives the exact product witness

```text
Red(120 nu)=120.                                    (4.4)
```

The equality is independent of the numerical Newton coefficient and of the
cosmological constant. The response theorem remains conditional on `A_QG`
and the binary `A_causal` choice. Reversing `A_causal` reverses chronology but
preserves the absolute density in (4.2); it introduces no positive action
scale.

## 5. Exact BV profile retract

Let `E` be any external graded field complex with pairing between fields and
duals. Define the retained lift

```text
i_or(phi)=phi tensor 1,
i_or(phi^!)=phi^! tensor nu.                        (5.1)
```

Let reduction apply `tau` to the internal product. For every external field
and dual,

```text
omega_product(i_or(phi),i_or(psi^!))
 =omega_E(phi,psi^!) tau(1*nu)
 =omega_E(phi,psi^!).                               (5.2)
```

The lift is therefore symplectic on the retained profile subspace. In a
three-pair finite witness its odd symplectic matrix has rank six and determinant
one.

If an external scalar density `L` is already supplied, its orientation lift is

```text
Lift(L)=L tensor nu.                                (5.3)
```

Equation (1.5) gives

```text
Red(Lift(L))=L.                                     (5.4)
```

The same identity holds coefficientwise for an antifield-linear BV action.
This recovers H4-T16's `Red o Lift=id` and composes it with the actual
selected-branch coframe density.

Equation (5.4) is a right inverse, not a source theorem. Starting with the
known lower action and multiplying it by `nu` does not prove that primitive
MTT independently emits that upper action.

## 6. No new density or action primitive

Introduce a temporary unnormalized orientation `nu_s=s nu`, `s>0`. Before
normalization, the five displayed amplitudes

```text
(A_H,g_1^-2,g_2^-2,g_3^-2,S_BV,product)             (6.1)
```

have logarithmic Jacobian with respect to `(log f0,log s)`

```text
J_pre=
[[1,0],
 [1,0],
 [1,0],
 [1,0],
 [1,1]],                                            (6.2)
```

of rank two. The last column is exactly the arbitrary orientation-density
scale. The H4-T16 normalization is

```text
tau(nu_s)=s=1.                                      (6.3)
```

Its tangent equation is `d log s=0`. Restricting (6.2) to that tangent gives

```text
J_normalized=(1,1,1,1,1)^T,                        (6.4)
```

of rank one. Hence normalized fiber integration neither multiplies nor
duplicates T49's action quantum:

```text
shared primitives before product reduction: 1,
shared primitives after product reduction:  1,
new continuous normalization primitives:    0.      (6.5)
```

An inverse simultaneous change of orientation basis and trace is merely a
coordinate change preserving `tau(nu)=1`; it also leaves (5.2)-(5.4)
unchanged.

## 7. H4-T15 bridge-clause audit

The exact composition changes only the following subclauses.

| Clause | Status after T50 | Reason |
|---|---|---|
| C0 base and source | partial | The selected-branch external coframe and density exist after `A_QG/A_causal`; the complete externalized upper field source is open. |
| C1 primal contraction | profile exact | The unit/orientation right inverse is exact; disposition of the other 86 modes and the coupled bundle complex is open. |
| C2 cotangent lift | profile exact | Pairing preservation is exact on field/profile and dual/orientation pairs; eliminated-mode BV pushforward is open. |
| C3 representation and phase | open | Neutral topology does not emit charged matter, Higgs or the chiral operator. |
| C4 density and normalization | profile exact | Coframe density and normalized fiber factor compose exactly; the full-carrier physical Hodge density is open. |
| C5 field-only action | right inverse only | Reduction of a supplied action is exact; independent upper action selection is open. |
| C6 BV differential and action | open | Full Koszul-Tate, BRST and antifield action matching is not supplied. |
| C7 reality, statistics and grading | profile exact | The retained internal involution is unique; full field reality, parity and ghost comparison are open. |
| C8 gauge fixing and domain | gravitational principal symbol only | The selected TT chronology is exact; full hyperbolic/Dirac BV domains are open. |
| C9 BV pushforward | open | UV Lagrangian, determinant orientation, anomaly and QME transport are open. |
| C10 provenance and parameters | exact ledger | Inputs are hash-locked; one `alpha` and one inherited binary causal orientation remain. |

The profile rows are not enough to change the global decision (1.9).

## 8. Mandatory no-go boundaries

H4-T17 proves that the 88-dimensional bare q79 topology carrier has Euler
characteristic zero while the unit/orientation sector has Euler characteristic
two. Its 86-dimensional complement has index `-2`; no degree-one differential
on that unchanged carrier can lift all 86 modes while retaining only the
orientation sector. T50 therefore makes no low-energy completeness claim.

H4-T18 proves that an ungraded positive Hessian cannot select chiral
orientation. The physical endpoint must separately export the first-order
graded associated-matter operator and the positive rank-102 background
Hessian. T50 uses neither one as a substitute for the other.

These no-go results are part of the construction, not footnotes. They prevent
the exact two-profile pairing from being misread as a complete particle
spectrum or as a chirality theorem.

## 9. Parameter and selection ledger

At the declared selected-branch profile tier:

```text
new observed inputs:                         0,
new continuous action parameters:           0,
new continuous density parameters:          0,
inherited shared action primitive alpha:     1,
inherited binary A_causal orientation:       1,
strict source value of alpha:                open,
primitive selection of A_QG:                 open,
origin of A_causal:                          open.   (9.1)
```

The binary time orientation is not an action-amplitude parameter. It reverses
the causal order and exchanges retarded with advanced propagation while
preserving the metric, absolute volume and normalized internal real profile.

## 10. Exact boundary

T50 proves:

- the exact normalized q79 unit/orientation Frobenius algebra;
- the unique trace-compatible real involution on that retained sector;
- exact composition of the selected-branch q79 coframe density with normalized
  internal fiber integration;
- exact preservation of the external BV field-dual pairing on retained
  profiles;
- exact reduction of an already-supplied antifield-linear action;
- `alpha_upper=alpha_lower` and zero new density/action primitives;
- a clause-by-clause refinement of the H4-T15 compactification gate; and
- preservation of the H4-T17 and H4-T18 no-go boundaries.

T50 does not prove:

- primitive selection of `A_QG` or `A_causal`;
- the full q79 Hodge star, metric real slice or trace density on all modes;
- a selected visible/hidden HYM endpoint and its connection;
- physical removal or gapping of the 86 complement modes;
- charged/chiral bundle zero modes or their first-order operator;
- an independently selected upper field-only action;
- the complete Lorentzian BV differential, domains or causal inverse;
- determinant-line orientation, interacting BV pushforward or QME transport;
- a source-derived numerical value of `alpha`; or
- closure of `B.GEO.01`, `B.ACTION.01` or `B.QFT.02`.

Physical acceptance remains

```text
physical gates:   0/3,
physical packets: 0/3,
physical rows:    0/7.                              (10.1)
```

The next honest action target is now smaller: construct the full selected
q79 Hodge/real field carrier and an independently emitted upper action, then
prove its compactification lands on this normalized one-primitive profile
retract.

## 11. Reproduction

```text
python build_normalized_orientation_coframe_bv_bridge.py
python verify_normalized_orientation_coframe_bv_bridge.py
python -m unittest tests.test_normalized_orientation_coframe_bv_bridge -v
```

The machine-readable result is
`normalized_orientation_coframe_bv_bridge.packet.json`.
