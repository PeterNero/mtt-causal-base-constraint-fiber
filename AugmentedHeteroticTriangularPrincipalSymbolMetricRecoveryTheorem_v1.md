# Augmented Heterotic Triangular Principal-Symbol and Metric-Recovery Theorem

**Identifier:** CBF.T57

**Date:** 2026-09-01

**Tier:** exact general theorem, exact source-locked non-diagonal
six-dimensional witness and conditional q79 rank-102 specialization

**Physical status:** the full triangular symbol and its recovery law are
derived. The selected physical q79 endpoint, density and visible-hidden HYM
connection are not supplied here.

## 1. Purpose

CBF.T56 proves that a genuine Dirac/Dolbeault square has scalar Laplace
principal symbol. The corrected q79 upper complex is richer. It is the
triangular totalization

```text
Y_n=Omega^(0,n)(Q) direct-sum Omega^(0,n+1)(X),

L_n=[[dbar_Q, a(-1)^n partial],
     [0,      dbar            ]].                 (1.1)
```

The `partial` lane is first order. It therefore cannot be classified as a
lower-order perturbation of the diagonal Dolbeault blocks. CBF.T57 computes
its contribution instead of assuming that T56 applies unchanged to the full
totalization.

The result is unexpectedly rigid. The full degree-one Hodge symbol is not
scalar, but its failure of scalarity is one canonical rank-six orthogonal
projector. It has exactly two spectral levels. Those levels recover the
relative Hilbert normalization between the two lanes, while their corrected
baseline recovers the same metric and action scale as CBF.T55.

## 2. Triangular symbol complex

Let `X` have complex dimension three. At a nonzero real covector `xi`, put

```text
beta=xi^(0,1),
alpha=xi^(1,0),
q(xi)=|beta|^2=|alpha|^2.
```

Let `Q` be a Hermitian bundle of complex rank `r` containing the holomorphic
cotangent lane used by `partial`. On symbols, write

```text
D_n=epsilon_beta on Q tensor Lambda^(0,n),
C_n=epsilon_beta on Lambda^(0,n+1),
A_n(z)=alpha tensor z.
```

Then

```text
l_n(xi)=[[D_n, a(-1)^n A_n],
         [0,   C_n          ]].                  (2.1)
```

Because `D_(n+1) A_n=A_(n+1) C_n` and the sign alternates,

```text
l_(n+1)(xi) l_n(xi)=0.                           (2.2)
```

Thus (2.1) is itself a symbol complex. The alternating sign is not cosmetic:
it is the mechanism that cancels the mixed second-order Hodge blocks.

## 3. Relative Hilbert normalization

Let the Hermitian weights of the `Q` and shifted-form lanes have positive
ratio

```text
rho=m_Q/m_shifted.                               (3.1)
```

This ratio changes the adjoint of `A_n` by `rho`; it does not change the
nilpotent differential. Let

```text
Delta_Y,n=l_(n-1) l_(n-1)^*+l_n^* l_n.          (3.2)
```

At degree one, direct block multiplication gives

```text
sigma_2(Delta_Y,1)(xi)=q(xi) I+a^2 rho q(xi) P_xi,  (3.3)
```

or, in the ASCII formula used by the executable contract,

```text
q(xi) I+a^2 rho q(xi) P_xi.
```

Here

```text
P_xi=(p_alpha tensor I_Lambda01) direct-sum I_Lambda02,  (3.4)
```

where `p_alpha` is the rank-one orthogonal projector onto the holomorphic
covector line spanned by `alpha` inside `Q`.

### Proof

The diagonal Dolbeault identities give

```text
D_0 D_0^*+D_1^*D_1=q I,
C_0 C_0^*+C_1^*C_1=q I.                         (3.5)
```

The upper-right block of (3.2) is proportional to

```text
-D_1^* A_1+A_0 C_0^*,                           (3.6)
```

and the lower-left block is its adjoint. Wedge-contraction compatibility
makes (3.6) zero. The remaining `A` terms are

```text
a^2 rho A_0 A_0^*=a^2 rho q(p_alpha tensor I_Lambda01),
a^2 rho A_1^*A_1=a^2 rho q I_Lambda02.          (3.7)
```

Equations (3.5)-(3.7) prove (3.3)-(3.4). Both summands in (3.4) are orthogonal
projectors on orthogonal lanes. Their ranks are three and three, hence

```text
P_xi^2=P_xi=P_xi^*,
rank(P_xi)=six.                                  (3.8)
```

QED.

## 4. Two-level spectrum and recovery

The degree-one carrier has dimension

```text
d=3r+3.                                         (4.1)
```

Equation (3.3) has exactly the two eigenvalues

```text
lambda_low=q,
lambda_high=q(1+a^2 rho),                       (4.2)
```

with multiplicities

```text
mult(lambda_low)=3r-3,
mult(lambda_high)=6.                            (4.3)
```

Consequently the full symbol itself recovers the lane normalization:

```text
rho=(lambda_high/lambda_low-1)/a^2.             (4.4)
```

The normalized trace is

```text
tr(sigma_2 Delta_Y,1)/d
  =q [1+2a^2 rho/(r+1)].                        (4.5)
```

Therefore either the lower spectral level or the trace corrected by (4.5)
recovers `q(xi)`. Polarization recovers the complete contravariant quadratic
form. For a Hessian with common positive scale `kappa`, this emits

```text
A=kappa H.                                      (4.6)
```

Together with the same-source oriented density `v`, CBF.T55 gives

```text
kappa=(v^2 det A)^(1/6),
H=A/kappa,
G=kappa A^-1,                                   (4.7)
```

and CBF.T52 emits the complete Hodge response. No independent metric table or
relative-lane parameter is required after the full symbol and density have
been selected.

## 5. Correction to the T56 application

There is no contradiction between T56 and T57.

```text
T56: each diagonal Dirac/Dolbeault square has scalar symbol.
T57: the full triangular totalization also contains a first-order partial lane.
```

The first statement remains exact. The second produces the projector in
(3.3). Treating the full augmented symbol as scalar would erase a rank-six
piece and would also erase the observable `rho`. Scalarity of the complete
totalization is therefore not a missing theorem to prove; it is a false exit
requirement to remove.

This distinguishes T57 from a generic mixed-order detour complex. All entries
in (2.1) are first order, their signs satisfy the symbol-complex identity, and
the residual is a controlled projector rather than an uncontrolled quartic
symbol.

## 6. Exact non-diagonal six-dimensional witness

The executable certificate uses the determinant-one nonorthogonal Hermitian
coframe from CBF.T52. It takes a witness bundle of rank `r=4`: three
holomorphic cotangent lanes plus one spectator lane. At degree one,

```text
d=15,
mult(lambda_low)=9,
mult(lambda_high)=6.                            (6.1)
```

For every one of the 21 polarization covectors `e_i` and `e_i+e_j`, the
builder constructs the exact Gaussian-rational exterior matrices `l_0` and
`l_1` and verifies:

1. `l_1 l_0=0` exactly;
2. both mixed Hodge blocks vanish exactly;
3. the correction divided by `a^2 q` is a Hermitian idempotent;
4. its exact Gaussian rank is six;
5. the complete symbol has the two levels in (4.2); and
6. the scalar full-symbol ansatz leaves a residual of rank six.

The deliberately nonphysical fixtures `a=1/2`, `rho=1` give

```text
lambda_high/lambda_low=5/4,
tr(Delta)/(15q)=11/10.                          (6.2)
```

Equation (4.4) recovers `rho=1`. After dividing the trace by `11/10`, the
nonphysical action fixture `kappa=7` reconstructs `A=7H`. Equations (4.7)
recover the exact CBF.T52 metric and its 64-dimensional Hodge digest. The
fixtures test the theorem; they are not physical inputs.

## 7. q79 rank-102 specialization

For the supplied augmented q79 design, `rank_C(Q)=102` and `a=1/2`. Hence the
degree-one carrier has dimension

```text
d=3(102)+3=309.                                 (7.1)
```

The two multiplicities are

```text
303 and six,                                    (7.2)
```

and the normalized trace factor is

```text
1+rho/206.                                      (7.3)
```

At the witness value `rho=1`, this is `207/206`. That number is not promoted
as the q79 physical value. The theorem says that the actual selected full
symbol would determine `rho` by its two levels and would then determine the
correct trace correction automatically.

The rank-six correction is independent of the other 99 `Q` lanes because
`partial` enters through the rank-three holomorphic cotangent subbundle. This
is why the non-scalar part stays finite while the baseline multiplicity grows
from nine in the witness to 303 in the rank-102 specialization.

## 8. Frontier change

Before CBF.T57, the existing augmented endpoint compiler established a
conditional Hilbert complex but did not compute its full cotangent Hodge
symbol. T56 could therefore be misapplied by treating the entire triangular
operator as one scalar Dirac square.

After CBF.T57, the source contract is exact:

```text
selected full augmented symbol and same-source density
  -> identify its rank-six projector
  -> recover rho from the two spectral levels
  -> recover the baseline quadratic form
  -> recover action scale and metric by T55
  -> recover Hodge response by T52.
```

This removes two duplicate source requests once the physical operator exists:
an independently supplied relative normalization and an independently
supplied metric payload. It also removes scalarity of the full triangular
symbol as a false requirement.

The remaining physical object is still substantial: one hash-addressed
selected q79 visible-hidden endpoint carrying the augmented differential,
Hilbert density, HYM connection, domains, projector, reduced Green operator,
`C4`/TT naturality and certified finite/continuum errors.

`B.GEO.01`, `B.ACTION.01` and `B.OP.01` remain open. Physical acceptance remains `0/3`
gates, `0/3` packets and `0/7` endpoint rows.

## 9. Parameter accounting

CBF.T57 adds zero observed values, fitted values, continuous physical
parameters and discrete selectors. The symbol ratio makes `rho` an output,
not a knob, once the full operator is selected. The witness values `rho=1`
and `kappa=7` are nonphysical exactness fixtures. The one shared physical
action primitive remains open and unchanged.

## 10. Reproduction

```powershell
python build_augmented_heterotic_triangular_principal_symbol.py
python verify_augmented_heterotic_triangular_principal_symbol.py
python -m unittest tests.test_augmented_heterotic_triangular_principal_symbol -v
```
