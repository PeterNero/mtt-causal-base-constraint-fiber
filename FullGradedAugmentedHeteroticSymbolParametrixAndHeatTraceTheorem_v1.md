# Full Graded Augmented Heterotic Symbol Parametrix and Heat-Trace Theorem

**Identifier:** CBF.T58

**Date:** 2026-09-01

**Tier:** exact general theorem, exact source-locked non-diagonal witness and
conditional q79 rank-102 specialization

**Physical status:** the complete principal-symbol inverse and leading heat
coefficients are derived for a supplied augmented endpoint. No selected q79
connection, global Green operator or numerical continuum block is supplied.

## 1. Purpose

CBF.T57 calculates the degree-one principal symbol of the corrected augmented
heterotic complex and discovers its canonical rank-six projector. The
physical operator contract uses the whole graded complex, not degree one in
isolation. CBF.T58 derives the exact projector, spectrum, inverse,
determinant and leading heat trace for all five mapping-cone degrees.

The calculation also finds a necessary completion: the scalar degree-minus-one
lane cannot be discarded. Without it, degree zero has three symbol levels and
the uniform T57 projector formula fails.

## 2. Complete augmented complex

Let `X` have complex dimension three and let `Q` have complex rank `r>=3`.
The complete mapping-cone grading is

```text
Y_n=Q tensor Lambda^(0,n) direct-sum Lambda^(0,n+1),
n=-1,0,1,2,3,                                   (2.1)
```

where exterior powers outside degrees zero through three are zero. In
particular,

```text
Y_(-1)=Lambda^(0,0).                            (2.2)
```

At a nonzero real covector `xi`, write

```text
beta=xi^(0,1), alpha=xi^(1,0), q=|beta|^2,
c=a^2 rho>0.                                    (2.3)
```

The symbol differential is

```text
l_n=[[epsilon_beta, a(-1)^n A_alpha],
     [0,            epsilon_beta    ]],          (2.4)
```

with `A_alpha(z)=alpha tensor z` in the cotangent sublane of `Q`. At degree
minus one, (2.4) is the column from the scalar lane to `Q direct-sum
Lambda^(0,1)`.

## 3. Full graded projector theorem

Let `p_alpha` be the rank-one orthogonal projector onto the line spanned by
`alpha` in the cotangent sublane of `Q`. With absent exterior powers treated
as zero, define

```text
P_n=(p_alpha tensor I_Lambda^n) direct-sum I_Lambda^(n+1).  (3.1)
```

Then the Hodge symbol in every degree is

```text
sigma_2(Delta_Y,n)(xi)=q(xi)[I+cP_n].           (3.2)
```

The carrier dimension and correction rank are

```text
d_n=r C(3,n)+C(3,n+1),                          (3.3)
s_n=C(3,n)+C(3,n+1)=C(4,n+1).                  (3.4)
```

Thus

```text
rank sequence: 1,4,6,4,1.
```

```text
n:            -1     0      1       2       3
d_n:          1      r+3    3r+3    3r+1    r
s_n:          1      4      6       4       1.  (3.5)
```

### Proof

The diagonal wedge-contraction identities give `qI` in every complete
Dolbeault lane. The alternating sign in (2.4) cancels all mixed second-order
blocks exactly as in T57. At degree `n>=0`, the incoming partial lane adds

```text
cq(p_alpha tensor I_Lambda^n)
```

to the `Q` block. At degree `n<=2`, the outgoing partial lane adds

```text
cq I_Lambda^(n+1)
```

to the shifted-form block. At degree minus one only the outgoing scalar lane
exists and gives `q(1+c)`. The two blocks are orthogonal projectors, and
Pascal's identity gives (3.4). QED.

### Corollary 3.1 (scalar completion is necessary)

Delete `Y_(-1)` and `l_(-1)` while retaining `Y_0`. The degree-zero symbol
then has three levels:

```text
cq       on the beta line in Lambda^(0,1),
q        on Q,
q(1+c)   on beta-perpendicular in Lambda^(0,1). (3.6)
```

It cannot be written as `q[I+cP]` for an orthogonal projector. The scalar
degree-minus-one lane is therefore required by the uniform augmented
mapping-cone symbol.

## 4. Spectrum, inverse and determinant

Since `P_n^2=P_n=P_n^*`, equation (3.2) has two levels:

```text
lambda_low=q,       multiplicity d_n-s_n,
lambda_high=q(1+c), multiplicity s_n.            (4.1)
```

It is strongly elliptic for `q>0` and `rho>0`. Its condition number, exact
principal-symbol inverse and determinant are

```text
cond=1+c,                                           (4.2)
sigma_2(Delta_Y,n)(xi)^(-1)
  =q^(-1)[I-c/(1+c) P_n],                          (4.3)
det sigma_2(Delta_Y,n)(xi)=q^(d_n)(1+c)^(s_n).    (4.4)
```

This is the complete high-frequency parametrix. It is not a global Green
operator and says nothing about the finite-dimensional kernel.

## 5. Leading heat trace

In real dimension six, Gaussian integration of the two branches gives the
leading local fiber weight

```text
h_n(c)=(d_n-s_n)+s_n(1+c)^(-3).                 (5.1)
```

Suppressing the common metric-density factor and common action scale,

```text
tr K_n(t;x,x)~(4 pi t)^(-3)h_n(c).              (5.2)
```

The correction ranks and baseline multiplicities have alternating sums

```text
-1+4-6+4-1=0,                                   (5.3)
0+(r-1)-(3r-3)+(3r-3)-(r-1)=0.                 (5.4)
```

The first minus sign in (5.3) is the parity of degree minus one. Therefore

```text
sum_(n=-1)^3 (-1)^n h_n(c)=0.                  (5.5)
```

This is a leading-symbol heat-supertrace identity, not by itself a Fredholm
index theorem.

## 6. Exact non-diagonal witness

The executable certificate uses the T52/T57 nonorthogonal determinant-one
Hermitian coframe and rank-four `Q`. For every one of 21 polarization
covectors and all five degrees, it checks the projector, rank, two-level
identity, inverse and determinant. It also verifies the three-level defect of
Corollary 3.1 when the scalar lane is deleted.

With nonphysical fixtures `a=1/2`, `rho=1`, and `c=1/4`, the degree data are

```text
n              -1      0       1       2       3
d_n            1       7       15      13      4
s_n            1       4       6       4       1
d_n-s_n        0       3       9       9       3
tr/(d_n q)     5/4     8/7     11/10   14/13   17/16.  (6.1)
```

The leading heat weights are

```text
64/125, 631/125, 1509/125, 1381/125, 439/125,  (6.2)
```

whose degree-signed alternating sum is zero.

## 7. q79 rank-102 specialization

For `r=102` and `a=1/2`,

```text
n              -1      0       1       2       3
d_n            1       105     309     307     102
s_n            1       4       6       4       1
d_n-s_n        0       101     303     303     101.  (7.1)
```

The normalized trace factors are

```text
1+rho/4,
1+rho/105,
1+rho/206,
1+rho/307,
1+rho/408.                                     (7.2)
```

At the nonphysical witness value `rho=1`, the heat weights are

```text
64/125, 12881/125, 38259/125, 38131/125,
12689/125,                                      (7.3)
```

again with degree-signed alternating sum zero. These are conditional
rank-102 consequences, not selected physical q79 operator data.

## 8. Operator-execution frontier

Before T58, T57 supplied only the degree-one symbol correction. After T58,
every graded high-frequency block has an exact inverse, condition number,
determinant and leading heat coefficient. The theorem also proves that the
scalar completion lane is structurally necessary.

This does not close `B.OP.01`. The blocker still requires the selected
visible-hidden HYM endpoint, lower-order coefficient arrays, kernel
projection, global reduced inverse, tail bounds, physical intertwiner and
radii-inequality decision. The correct numerical chain is

```text
selected endpoint coefficients
  -> fixed principal preconditioner (4.3)
  -> invert the lower-order compact perturbation
  -> certify kernel, tail and radii bounds.
```

`B.GEO.01` and `B.OP.01` remain open. Physical acceptance remains `0/3`
gates, `0/3` packets and `0/7` endpoint rows.

## 9. Parameter accounting

The theorem adds zero observed values, fitted values, continuous physical
parameters and discrete selectors. `rho` remains an output of the selected
two-level symbol by T57. The values `rho=1` and `a=1/2` are exactness fixtures,
not accepted physical inputs.

## 10. Reproduction

```powershell
python build_full_graded_augmented_heterotic_symbol_parametrix.py
python verify_full_graded_augmented_heterotic_symbol_parametrix.py
python -m unittest tests.test_full_graded_augmented_heterotic_symbol_parametrix -v
```
