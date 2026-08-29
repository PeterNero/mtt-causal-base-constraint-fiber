# Normal-Frame Quotient and Action-Intertwiner Minimal-Data Theorem

## Status

Claim ID: `CBF.T18`

Tier:

```text
EXACT_GENERAL
+ EXACT_SOURCE_PINNED_FINITE_QUOTIENT_WITNESS
+ CONDITIONAL_PHYSICAL_INTERTWINER_REDUCTION
```

Decision:

```text
A46_A47_A50_SELECT_ONE_INVARIANT_NORMAL_LINE_NOT_A_FRAME
SEPARATE_NONZERO_NORMAL_FACTORS_FORM_ONE_GL1_ORBIT
THE_CONTRACTED_HESSIAN_IS_THE_FRAME_INVARIANT_ACTION_DATUM
A74_FIXES_THE_FINITE_FAMILY_TRACE_NOT_THE_PHYSICAL_BV_DENSITY
THE_PHYSICAL_EXIT_IS_ONE_SAME_ROOT_HESSIAN_INTERTWINER_AND_SCALE
```

This theorem continues `CBF.T17`. It changes the next-source obligation, but it
does not close `B.ACTION.01`. Physical packet acceptance remains `0/3` and
physical row acceptance remains `0/7`.

## 1. Result in one paragraph

The A46/A47/A50 representation has exactly one vector slot invariant under the
faithful SM gauge group and shared hypercharge circle: the complex `N^c` line.
It does not select a unit vector in that line. That omission is not a missing
continuous physical parameter in the affine closure action. If the normal
curvature factor is `B` and the nonzero normal covector is `epsilon`, then

```text
H=epsilon o B
```

is invariant under every change of normal frame. In one complex dimension all
nonzero factorizations of the same `H` lie in one exact `GL(1,C)` orbit, and
the complete affine multiplier action is unchanged. The separately displayed
`epsilon` and `B` are therefore coordinates on a factorization, not two
physical source values. A74 independently fixes the normalized finite family
functional to `Tr/3`. Once these quotients are taken, the physical endpoint
must emit one same-root effective Hessian satisfying

```text
H_eff=c_action H_resp
```

and the BV/compactification data that interpret `c_action`. The coefficient is
unique and computable from the endpoint, but normalized finite data alone
cannot determine it.

## 2. The selected normal object is a line

Order the one-family A46 carrier as

```text
H16=Q6 direct_sum u3 direct_sum d3 direct_sum L2 direct_sum e1 direct_sum N1.
```

A50 gives the primitive shared-circle weights

```text
6Y=(1,-4,2,-3,6,0)
```

on these six sectors. Expanded over the sixteen states, the hypercharge
operator has fifteen nonzero diagonal entries and one zero entry. Hence

```text
ker(Y16)=N1=N^c,
dim_C ker(Y16)=1.
```

The color and weak actions are also trivial on this slot, so it is the unique
full gauge-invariant line in `H16`.

### Theorem 2.1

The A46/A47/A50 data canonically select the rank-one projector

```text
P_N=diag(0,...,0,1)
```

and its image `L_N`. They do not canonically select a nonzero vector `n0` in
`L_N`, a complex-linear trivialization `epsilon:L_N->C`, or a real ray in
`L_N`.

### Proof

The unique zero-weight eigenspace proves projector and line uniqueness. Every
nonzero vector in a one-dimensional complex line differs by multiplication by
an element of `C^x`. The projector is unchanged by this multiplication. None
of A46, A47 or A50 supplies a distinguished nonzero section or phase anchor,
so a frame does not follow from the selected line. QED.

This distinction corrects the informal phrase "selected normal covector" in
CBF.T17. Its finite coordinate vector is a convenient frame for an already
selected line.

## 3. Normal-frame covariance of the affine action

Let `L` be a one-dimensional complex vector space, `K` a complex carrier, and
let

```text
B:K->L
```

denote the quadratic normal curvature map. Let `epsilon in L^*` be nonzero and
write

```text
H=epsilon o B.
```

The corresponding complex affine multiplier polynomial is

```text
A_(B,epsilon)(n,k,lambda)
  =-epsilon(n)+lambda(n+B(k)),
```

and the real action is its real part. Here `lambda in L^*`.

For `T in GL(L)`, define

```text
B_T=T o B,
epsilon_T=epsilon o T^-1,
n_T=Tn,
lambda_T=lambda o T^-1.
```

In a chosen scalar frame, `T` is multiplication by `a in C^x`, so this is

```text
(B,epsilon,n,lambda)
  -> (aB,epsilon/a,an,lambda/a).
```

### Theorem 3.1

The contraction, closure graph and full affine multiplier action are exactly
normal-frame invariant:

```text
epsilon_T o B_T=epsilon o B,
A_(B_T,epsilon_T)(n_T,k,lambda_T)
  =A_(B,epsilon)(n,k,lambda).
```

### Proof

The first identity is

```text
epsilon T^-1 T B=epsilon B.
```

For the action,

```text
-epsilon T^-1(Tn)
 +(lambda T^-1)(Tn+TB(k))
=-epsilon(n)+lambda(n+B(k)).
```

Taking real parts preserves equality. QED.

The critical multiplier transforms covariantly with `epsilon`; no observable
coefficient changes.

## 4. Uniqueness of the nonzero factorization orbit

### Theorem 4.1

Let `H` be nonzero. Suppose

```text
H=epsilon_1 o B_1=epsilon_2 o B_2
```

with `epsilon_1` and `epsilon_2` nonzero covectors on one-dimensional complex
normal lines. Then there is a unique line isomorphism `T` such that

```text
B_2=T o B_1,
epsilon_2=epsilon_1 o T^-1.
```

Thus the set of nonzero factorizations of `H` has one `GL(1,C)` orbit.

### Proof

Every nonzero covector on a complex line is an isomorphism to `C`. Define

```text
T=epsilon_2^-1 o epsilon_1.
```

Then

```text
B_2=epsilon_2^-1 H
   =epsilon_2^-1 epsilon_1 B_1
   =T B_1,
```

and `epsilon_2 T=epsilon_1`. If another isomorphism has both properties, its
composition with the nonzero image of `B_1` agrees with `T`; one-dimensionality
then gives equality. QED.

### Consequence

Requiring a physical endpoint to select `epsilon` and `B` separately is too
strong. It must select their common source and the contracted Hessian `H`, plus
enough line/duality data to state the action covariantly. A frame may be chosen
for calculation and then quotiented.

The zero response `H=0` is separate. If invisible components of `B` are
allowed in `ker(epsilon)`, the theorem would fail; this cannot occur for a
nonzero complex covector on a complex line because its kernel is zero.

## 5. Relation to the pressure theorem

CBF.T17 held the curvature factor fixed and varied its normal covector. In
that presentation nonzero pressure magnitudes formed one classical projective
class after an overall action rescaling. CBF.T18 makes the stronger
factorization statement:

```text
(B,epsilon) and (aB,epsilon/a)
```

give literally the same action after a normal-coordinate change. No overall
action rescaling is needed.

Therefore:

- a scale assigned only to `epsilon` is normal-frame gauge;
- a common scale multiplying the contracted `H` is not removed by this gauge;
- the latter is the physical action-normalization question.

This separates normal factorization from physical action scale.

## 6. Unique finite family measure

Let `X` and `Z` be the qutrit Weyl shift and clock. A positive functional on
`M3(C)` can be written

```text
tau(A)=Tr(rho A),
rho>=0.
```

If `tau` is invariant under conjugation by `X` and `Z`, then `rho` commutes
with both generators. Their commutant is the scalar algebra. Normalization
`tau(I)=1` therefore gives

```text
rho=I3/3,
tau_3(A)=Tr(A)/3.
```

This is the exact A74 finite Weyl trace theorem. FSB.04f independently proves
that the selected response pair generates `M3(C)`, so the same scalar
commutant applies to the A/B family response algebra.

### Theorem 6.1

The selected finite family response has no free invariant measure parameter.
Its normalized family functional is `Tr/3`.

This theorem does not identify `Tr/3` with the physical HYM, ten-dimensional,
four-dimensional or BV density. That identification is a same-root
compactification statement and remains open.

## 7. Exact finite response invariants

Use the CBF.T16/T17 response

```text
H_resp=B_phase tensor R_phase+A_shift tensor R_shift.
```

The two internal projectors are disjoint and each has rank four. Both qutrit
response matrices have squared Frobenius norm `24`. Consequently

```text
rank_C(H_resp)=24,
Tr(H_resp^* H_resp)=4*24+4*24=192,
(Tr/48)(H_resp^* H_resp)=4.
```

On the active rank-24 carrier the normalized square is `8`. These are exact
finite algebraic normalizations. They use no observed mass, coupling, mixing
or threshold value.

Choosing a frame `n0` recovers the CBF.T17 display

```text
B(k)=1/2 n0 Re<k,H_resp k>,
epsilon(z n0)=z.
```

Every other nonzero frame gives the same graph-restricted action

```text
1/2 Re<k,H_resp k>.
```

## 8. Minimal physical intertwiner

Let `K_phys` be the Hessian of one selected upper action, and let `U` be the
same-source finite synthesis. If the selected range reduces `K_phys`, set

```text
H_eff=U^* K_phys U.
```

If it does not reduce the Hessian, use the same-source Feshbach operator
required by CBF.T12:

```text
H_eff=U^* K_phys U
      -U^* K_phys Q (Q K_phys Q)^-1 Q K_phys U.
```

The normal-frame quotient reduces the action match to one tensor identity:

```text
H_eff=c_action H_resp.                         (8.1)
```

No separate equality for a chosen `epsilon` or `B` is needed.

### Theorem 8.1

Because `H_resp` is nonzero, the coefficient in (8.1), if it exists, is
unique. With the Frobenius pairing,

```text
c_action
 =<H_resp,H_eff>_F/<H_resp,H_resp>_F
 =<H_resp,H_eff>_F/192.                        (8.2)
```

Equation (8.1) holds exactly if and only if

```text
R_action=H_eff-c_action H_resp
```

vanishes. For interval data, the corresponding norm ball must contain zero
with a certified upper radius.

### Proof

Taking the Frobenius inner product of (8.1) with `H_resp` gives (8.2).
Substitution gives the residual criterion. Nonzero norm `192` proves
uniqueness. QED.

The endpoint packet must put `K_phys`, `U`, its complement inverse or reducing
certificate, the physical density, and `c_action` on one root source. A
numerical proportionality found across unrelated packets is not acceptance.

## 9. Exact scale nonidentifiability

### Theorem 9.1

Normalized finite algebraic data cannot determine `c_action`.

### Proof

For every `c>0`, replace a candidate physical Hessian by

```text
H_eff,c=c H_resp.
```

All of the following are independent of `c`:

```text
rank and kernel,
projective spectrum,
normal-frame orbit,
automorphism and commutant groups,
normalized trace state,
normalized response direction H/||H||_F,
classical stationary zero set after common action rescaling.
```

But absolute Hessian eigenvalues and the quantum phase relative to `hbar`
scale with `c`. Hence no invariant of the normalized finite packet can choose
one member of this positive family. A physical action/density normalization or
equivalent metrology input is necessary. QED.

This is a nonidentifiability theorem, not permission to fit `c` to a measured
target. Equation (8.2) computes it prospectively once the selected endpoint is
available.

## 10. Source status

The source chain now separates into three levels.

### Exact established finite data

- A46/A47/A50 select `H16`, the faithful gauge action and `L_N=N^c`.
- A74 selects the normalized finite Weyl trace.
- A86 and FSB.04e/04f source and fix the finite A/B response orbit.
- CBF.T17 supplies the affine graph action.

### Exact quotient proved here

- a normal frame is not an additional source value;
- the contracted `H_resp` is the complete finite action datum;
- its family measure and Frobenius norm are fixed;
- a physical match has one uniquely recoverable common coefficient.

### Still absent

- a selected physical q79/Hull-Strominger endpoint root;
- the continuum `K_phys`, synthesis and inverse/tail certificate;
- the BV density and fiber integration;
- the equality (8.1) on that same root;
- Lorentzian, Higgs and left-right Yukawa typing;
- the nine charged scalar values and held-out prediction.

The FSB source manifest is a valid finite provenance root. It is not the
missing physical endpoint root required by `B.HS.01`, `B.OP.01` and
`B.ACTION.01`.

## 11. Parameter ledger

At the declared finite quotient tier:

```text
observed construction inputs:                         0,
fitted coefficients:                                  0,
normal-frame parameters after quotient:               0,
finite family-measure parameters:                     0,
finite contracted response matrices added here:       0,
conditional common action coefficient per endpoint:   1,
selected physical value for that coefficient:         0,
strict charged magnitude values still open:           9.
```

The one conditional coefficient is not a newly fitted MTT knob. It is a
required output of the missing physical action/compactification source.

## 12. What changed in the frontier

Before CBF.T18 the roadmap asked a future endpoint to select separately:

```text
normal covector,
normal curvature factor,
finite density,
action normalization,
same-root intertwiner.
```

The corrected minimal list is:

```text
selected invariant normal line: already closed by A46/A47/A50,
normal frame: quotient convention, not physical data,
finite family measure: already closed by A74,
contracted finite Hessian: already exact at the FSB finite tier,
physical exit: same-root H_eff=c_action H_resp plus BV density.
```

Thus two apparent source choices are removed and the action-side physical exit
is reduced to one tensor equality and one coefficient. The coefficient cannot
be emitted before the physical endpoint exists.

## 13. Claims and nonclaims

### Proved

- uniqueness of the A47/A50 invariant normal line in `H16`;
- nonselection and irrelevance of a separate normal frame;
- exact `GL(1,C)` covariance of the affine closure action;
- uniqueness of the nonzero normal-factorization orbit;
- uniqueness of the normalized finite family trace;
- exact finite response norm `192` and normalized square `4`;
- the unique endpoint coefficient formula and residual test; and
- nonidentifiability of the absolute action scale from normalized finite data.

### Not proved

- a physical q79 endpoint or common visible-hidden HYM chamber;
- continuum coefficient arrays, inverse/tail bounds or radii decision;
- a selected physical BV density or action coefficient;
- equality of a physical effective Hessian with `c_action H_resp`;
- Lorentz/Higgs/Yukawa typing, masses, CKM, PMNS or CP; or
- closure of `B.ACTION.01` or `B.SM.02`.

## 14. Reproduction

```text
python build_normal_frame_action_intertwiner_reduction.py
python verify_normal_frame_action_intertwiner_reduction.py
python -m unittest tests.test_normal_frame_action_intertwiner_reduction -v
```

The generated packet is
`normal_frame_action_intertwiner_reduction.packet.json`.
