# Selected Gauge-Physical Future State, BRST, and Zero-Mode Theorem v1

**Claim ID:** `CBF.T47`
**Date:** 2026-08-30
**Status:** exact selected free gauge-physical state on the homogeneous flat
`H>0` branch, conditional on the inherited positive common gauge-action
normalization; radial Higgs state, upper-action selection, determinant
holonomy, fixed-coupling completion, `G1`, and top-level `G2` remain open

## 1. Result

CBF.T46 reduced the missing free q79 state to a gauge-physical factor and a
Higgs-fluctuation factor in addition to the selected T45 Weyl factor. Its
factor count inherited the older q79 existence theorem, which was formulated
on a symmetric local chart and used

```text
12 massless gauge generators x 2 polarizations + 4 Higgs components
  = 24 + 4
  = 28 bosonic physical modes per nonzero momentum.
```

That count is correct at `H=0`. It is not the correct physical decomposition
on T45's declared branch, where the same single-Higgs radial background obeys
`H>0`.

On that branch the A47 gauge algebra and A51 one-Higgs module give the exact
stabilizer

```text
su(3) + u(1)_em,
```

of dimension nine. Three electroweak directions are broken. The q79
gauge-Higgs BRST differential then moves the three Goldstone directions into
the massive gauge complexes. Consequently the physical count is

```text
9 unbroken generators x 2 massless polarizations = 18,
3 broken generators   x 3 massive polarizations  =  9,
1 radial Higgs fluctuation                        =  1,
                                                     --
                                                     28.       (1.1)
```

Thus the total is conserved, but the factorization changes. The correct free
physical seed on the `H>0` branch is

```text
omega_0,H
  = omega_gauge,H,phys tensor omega_h,rad tensor omega_Weyl.   (1.2)
```

The present theorem selects the first factor. T45 selects the last. Only the
radial Higgs fluctuation factor remains unselected.

The selection uses the same future orientation as T45. On physical gauge
Cauchy data, let

```text
Omega_G,H = sqrt(-Delta + M_G,H^2).
```

The future complex structure is

```text
J_fut(q,p)=(-Omega_G,H^(-1)p, Omega_G,H q).          (1.3)
```

It determines a pure quasifree CCR ground state
`omega_gauge,H,phys^fut`. No density matrix, temperature, measured mass, or
continuous state coordinate is supplied.

The nine massless channels do not introduce a hidden zero-mode choice on the
declared spatial `R^3` branch. The point `p=0` has zero spectral measure,
`-Delta` has no `L2(R^3)` zero eigenvector, and

```text
d^3p/(2|p|)
```

is locally integrable at the origin. A compact Cauchy surface with harmonic
one-forms is a different problem and is not claimed here.

## 2. Typed inherited source

The construction uses four already certified structures.

1. A47 supplies the faithful compact gauge group
   `(SU3 x SU2 x U1)/Z6`. Its Lie algebra has dimension `8+3+1=12`.
2. A51 supplies one complex Higgs doublet of hypercharge `+1/2` and the raw
   three-family gauge trace coefficients

   ```text
   k_Y:k_2:k_3=10:6:6.                              (2.1)
   ```

3. The q79 background Feynman-'t Hooft construction supplies the normally
   hyperbolic gauge, ghost, and Higgs Hessians and the free BRST rule

   ```text
   s_0 a=Dbar c,
   s_0 h=-rho(c) Hbar,
   s_0 c=0,
   s_0 cbar=b,
   s_0 b=0.                                         (2.2)
   ```

4. T45 supplies the homogeneous flat branch, constant radial amplitude
   `H>0`, and future time orientation.

Choose the gauge representative

```text
Hbar=(0,H/sqrt(2)).                                 (2.3)
```

This chooses coordinates on the gauge orbit, not another physical vacuum
parameter. The radial value is the same inherited `H` used by T45.

A51 does not fix the common four-dimensional gauge-action coefficient.
Accordingly, every mass below is stated up to one inherited positive common
factor. Rank, stabilizer, projectors, mode counts, and future-state uniqueness
are independent of that factor. Numerical SI masses and absolute field
normalization are not claimed.

## 3. Exact gauge kinetic and mass pencil

Order the gauge algebra as

```text
(G_1,...,G_8,W_1,W_2,W_3,B).
```

Use the exact A51 trace metric

```text
K_G=diag(6 I_8,6 I_3,10).                           (3.1)
```

After removing one irrelevant common positive multiple of `H^2`, the
single-Higgs orbit map gives the mass form

```text
M_H = 0_8 direct_sum
      [ 1  0  0  0 ]
      [ 0  1  0  0 ]
      [ 0  0  1 -1 ]
      [ 0  0 -1  1 ].                              (3.2)
```

The physically relevant endomorphism is the generalized mass operator

```text
A_H=K_G^(-1) M_H.                                  (3.3)
```

It is self-adjoint in the `K_G` metric, although its raw coordinate matrix is
not Euclidean symmetric.

### Theorem 3.1: exact broken and unbroken subspaces

The spectrum of (3.3) is

```text
0      with multiplicity 9,
1/6    with multiplicity 2,
4/15   with multiplicity 1.                        (3.4)
```

The zero space is `su(3)+u(1)_em`. In the raw neutral coordinates,

```text
gamma = W_3+B,
Z     = -5 W_3+3 B.                                (3.5)
```

They are orthogonal in the metric (3.1). The exact broken projector has
identity entries on `W_1,W_2` and neutral block

```text
P_Z = [ 5/8 -5/8 ]
      [-3/8  3/8 ].                                (3.6)
```

It obeys

```text
P_br^2=P_br,
rank(P_br)=3,
P_br^T K_G=K_G P_br.                               (3.7)
```

The unbroken projector is `P_un=I-P_br` and has rank nine.

### Proof

The color block of (3.2) vanishes. The `W_1,W_2` generalized eigenvalues are
`1/6`. The neutral block is

```text
[ 1/6  -1/6 ]
[-1/10  1/10].                                    (3.8)
```

Its determinant is zero and its trace is `1/6+1/10=4/15`. Direct
multiplication gives

```text
A_H gamma=0,
A_H Z=(4/15)Z,
A_H|neutral=(4/15)P_Z.
```

Equations (3.6)-(3.7) follow exactly. QED.

No measured weak-mixing angle entered this calculation. Equation (3.8) is
the generalized eigenproblem associated with the already executed raw trace
metric (2.1). Rewriting it in canonically normalized fields gives the A51
structural relation `g_2^2=(5/3)g_Y^2`; it does not supply the missing common
coupling or RG scale.

## 4. BRST reduction on the H>0 branch

### 4.1 Unbroken generator

For an unbroken generator and one nonzero massless momentum, the inherited
six-direction canonical complex is

```text
(epsilon_1,epsilon_2,x,y,c,cbar),

Q_0 x=c,
Q_0 cbar=y.                                        (4.1)
```

With `h c=x`, `h y=cbar`, and `P_2` the projector onto the two transverse
directions,

```text
Q_0 h+h Q_0=I-P_2.                                (4.2)
```

The ghost-number-zero quotient has positive Gram matrix `I_2`.

### 4.2 Broken generator

For a broken generator of mass `m>0`, the longitudinal gauge datum and its
Goldstone datum mix. At spatial momentum modulus `r`, put

```text
E=sqrt(r^2+m^2),
x   =(r a_parallel+m chi)/E,
ell =(m a_parallel-r chi)/E.                       (4.3)
```

The gauge-orbit direction maps to `x`; its orthogonal complement `ell` is the
physical longitudinal massive polarization. The canonical complex is

```text
(epsilon_1,epsilon_2,ell,x,y,c,cbar),

Q_m x=c,
Q_m cbar=y.                                        (4.4)
```

Let `P_3` project onto `(epsilon_1,epsilon_2,ell)`. The same contraction gives

```text
Q_m h+h Q_m=I-P_3.                                (4.5)
```

The ghost-number-zero quotient has positive Gram matrix `I_3`.

Equation (4.3) remains regular at `r=0` because `m>0`. At `r=0`, the gauge
orbit is the Goldstone direction and `ell` is the third rest-frame vector
polarization. Thus a massive zero-momentum mode is physical and unambiguous;
it is not the massless zero-mode problem.

### Theorem 4.1: broken-phase gauge cohomology count

For every nonzero spatial momentum in a massless channel, and every spatial
momentum in a massive channel, the positive ghost-number-zero gauge
cohomology has dimension

```text
9 x 2 + 3 x 3=27.                                  (4.6)
```

All remaining gauge, Goldstone, ghost, antighost, and auxiliary directions
are contractible.

### Proof

Apply (4.2) to the rank-nine unbroken projector and (4.5) to the rank-three
broken projector of Theorem 3.1. A contraction identifies cohomology with the
image of its physical projector. The inherited Krein form restricts to
`I_2` and `I_3` respectively, while its null ghost-zero directions are exact.
The direct sum therefore has positive dimension (4.6). QED.

This theorem replaces, rather than duplicates, the older `12 x 2=24` count
on the `H>0` branch. That older count remains correct on the symmetric
`H=0` chart for which it was used.

## 5. Massless zero-mode and infrared theorem

Let the flat Cauchy surface be `Sigma=R^3`. For `p != 0`, the physical
massless projector can be written without choosing polarization vectors:

```text
Pi_T(p)=I_3-p p^T/|p|^2.                           (5.1)
```

It is bounded, self-adjoint, idempotent, has rank two, and annihilates `p`.
The value assigned to (5.1) at the single point `p=0` has no effect on the
state distribution.

### Theorem 5.1: no flat-branch zero-mode selector

On `L2(R^3)`, the massless spatial operator `-Delta` has no zero eigenvector.
The massless vacuum covariance is infrared finite on compact test data in
three spatial dimensions. Therefore the flat-branch gauge ground state needs
no additional `p=0` state coordinate.

### Proof

An `L2` function in the kernel of `-Delta` has Fourier transform supported at
the singleton `{0}`. A singleton has Lebesgue measure zero, so that Fourier
transform vanishes as an `L2` class. Hence the spectral projection
`E_{-Delta}({0})` is zero.

Near `p=0`, the scalar part of the positive-frequency covariance has measure

```text
d^3p/(2|p|).
```

In polar coordinates its radial behavior is `r dr`; explicitly,

```text
integral_(|p|<epsilon) d^3p/(2|p|)=pi epsilon^2.   (5.2)
```

The bounded projector (5.1) does not change integrability. Thus compact
smooth test data have finite covariance. QED.

Constant gauge potentials and compact-topology Wilson-line modes are not
silently discarded. They are not `L2(R^3)` particle modes. If the physical
Cauchy surface is compact or has nontrivial harmonic one-forms, a separate
finite-dimensional state and holonomy theorem is required. T47 does not
promote that global problem.

## 6. Future-positive physical CCR state

On the BRST cohomology of Section 4, define the nonnegative physical mass
operator by restoring the inherited common positive coefficient and `H^2`:

```text
M_G,H^2=c_G H^2 A_H,
c_G>0.                                             (6.1)
```

The A51 absolute-normalization theorem has not selected `c_G`; it is an
inherited action-scale coordinate, not a state coordinate introduced here.
Set

```text
Omega_G,H=sqrt(-Delta+M_G,H^2).                    (6.2)
```

On the massive sectors it is bounded below by a positive number. On the
massless sectors zero belongs to the continuous spectrum but has zero
spectral projection by Theorem 5.1. The natural energy phase space is

```text
Dom(Omega_G,H^(1/2)) direct_sum
Dom(Omega_G,H^(-1/2)).                             (6.3)
```

The compact test-function quotient is contained in the covariance form
domain by (5.2).

Let the Cauchy symplectic form have matrix

```text
S=[ 0  I]
  [-I  0].                                         (6.4)
```

The selected future orientation defines (1.3). It obeys

```text
J_fut^2=-I,
J_fut^T S J_fut=S,
S J_fut=diag(Omega_G,H,Omega_G,H^(-1))>0.          (6.5)
```

### Theorem 6.1: selected gauge-physical ground state

Fix the T45 homogeneous flat `H>0` branch, its future orientation, the A47
gauge carrier, the A51 relative kinetic metric, and any inherited positive
common coefficient `c_G`. Among regular, spatially translation-invariant,
stabilizer-invariant pure quasifree CCR states satisfying the future
ground-state spectrum condition, the physical gauge covariance is uniquely
the one determined by (1.3).

### Proof

The spectral theorem decomposes (6.2) into independent positive-frequency
oscillators on the rank-27 physical cohomology. For an oscillator of
frequency `omega>0`, CCR compatibility, purity, and the ground-state
condition fix

```text
J_omega=[0,-omega^(-1);omega,0].                   (6.6)
```

The direct integral of (6.6) is (1.3). The massless `p=0` singleton carries
no spectral subspace by Theorem 5.1, so it cannot support an additional
covariance. Internal degeneracies do not create another stabilizer-invariant
ground-state covariance because the construction is the identity on each
complete positive-energy eigenspace. QED.

The corresponding two-point kernel is the direct sum of

```text
Lambda_a^+(x,x')
 = integral d^3p/((2 pi)^3 2 omega_a(p))
     exp(-i omega_a(p)(t-t')+i p.(x-x')) Pi_a(p),  (6.7)
```

where `Pi_a` is the transverse projector for a massless channel and the
physical Proca projector for a massive channel. Positivity follows from
(6.5), normalization from the Weyl-algebra construction, and purity from
`J_fut^2=-I`. The standard flat massive and massless positive-frequency
kernels are Hadamard. Wrochna and Zahn's BRST-state equivalence then places
the descended state on the physical gauge algebra.

Gauge fixing does not become a parameter. The calculation uses the inherited
background Feynman-'t Hooft representative to expose the contraction, while
the state is defined on ghost-number-zero cohomology. BRST-equivalent gauge
presentations transport the same physical state.

## 7. Exact finite witnesses

The executable packet contains four independent finite checks.

1. The full rational `12 x 12` pencil `(K_G,M_H)` has generalized spectrum
   and projectors (3.4)-(3.7).
2. The six-direction massless and seven-direction massive BRST complexes
   satisfy the contraction identities exactly and have positive quotient
   Grams `I_2` and `I_3`.
3. At `r=3,m=4,E=5`, the rational mixing matrix

   ```text
   [3/5  4/5]
   [4/5 -3/5]                                      (7.1)
   ```

   sends the gauge-orbit vector `(3,4)` to `(5,0)` and the physical vector
   `(4,-3)` to `(0,5)`.
4. For sample rational momenta, (5.1) is checked exactly. A frequency-five
   oscillator verifies all identities in (6.5) over `Q`.

These witnesses execute the finite algebra in the proof. They do not replace
the Fourier/spectral arguments of Sections 5-6 with a finite momentum grid.

## 8. Corrected full-seed cutset

On the T45 `H>0` branch the physical factors are now

| Factor | Status after T47 |
|---|---|
| `omega_Weyl` | selected by T45 and transported by T46 |
| `omega_gauge,H,phys` | selected by T47 from the future physical gauge Hamiltonian |
| `omega_h,rad` | nonempty Hadamard state space, but no same-source selected radial Hessian covariance yet |
| formal interacting lift after a full seed | canonical by T46 |

The three Goldstone coordinates are not counted again in `omega_h,rad`.
They are part of the three broken BRST complexes and supply the physical
longitudinal gauge modes after quotient. Thus

```text
missing selected free factors after T47: 1.         (8.1)
```

T38's radial background marginal `delta_H` does not close (8.1). A probability
or repair marginal for the background amplitude is not the two-point
covariance of the radial fluctuation. The required next theorem must derive
the radial quadratic operator and its future-positive covariance from the
same selected action branch.

## 9. G2 and parameter ledger

```text
G2a flat-branch Weyl state:                    closed by T45,
G2a flat-branch gauge physical state:          closed by T47,
G2a flat-branch radial Higgs state:             open,
G2b exact background Dirac state transport:    closed by T46,
G2b formal state pullback and canonical lift:  closed by T46,
G2b selected complete free product seed:        open by one factor,
G2b upper-action-selected full BV map:          open,
G2c selected fixed-coupling continuum:          open 0/9,
top-level physical G2:                          open. (9.1)
```

No top-level physical acceptance counter changes. The physical gates remain
`0/3`, packets `0/3`, and endpoint rows `0/7` because those counters require
the complete same-source action and continuum endpoint, not only a selected
flat-branch gauge vacuum.

The parameter ledger is

```text
new observed inputs:                 0,
new fitted parameters:               0,
new continuous state selectors:      0,
new discrete state selectors:        0,
inherited future orientation:        1 discrete branch structure,
inherited radial amplitude:          H>0, unresolved absolute scale,
inherited gauge-action coefficient:  c_G>0, unresolved absolute scale,
gauge-fixing xi=1:                   presentation, not physical input.
```

The exact A51 trace metric fixes the relative generalized mass pencil. T47
does not claim a measured weak mixing angle, `W/Z` masses, RG matching, or
zero-primitive electroweak normalization.

## 10. Scientific boundary

T47 proves:

- the exact rank-nine stabilizer and rank-three broken gauge subspace on the
  same constant one-Higgs branch used by T45;
- the exact generalized electroweak mass spectrum at the A51 relative-trace
  tier;
- positive BRST cohomology with 18 massless and 9 massive physical gauge
  polarizations;
- absence of an additional massless `p=0` state coordinate on spatial `R^3`;
- the unique future-positive pure quasifree Hadamard gauge state in the
  declared regular stationary ground-state class;
- correction of the symmetric-phase seed factorization on the `H>0` branch;
- reduction of the missing free seed from two factors to one.

T47 does not prove:

- selection of the radial Higgs fluctuation covariance;
- absolute gauge or Higgs normalization;
- a vacuum on a compact cosmological Cauchy surface with harmonic modes;
- a nonlinear or fixed-coupling interacting Standard-Model state;
- upper-action selection of the T39/T46 BV map;
- determinant-line trivialization, RG flow, scattering, or observables;
- the q79 HYM endpoint, `G1`, or top-level `G2`.

## 11. Primary mathematical context

The BRST physical phase space and Hadamard-state descent are aligned with:

- M. Wrochna and J. Zahn, *Classical phase space and Hadamard states in the
  BRST formalism for gauge field theories on curved spacetime*,
  <https://arxiv.org/abs/1407.8079>.
- C. Gerard and M. Wrochna, *Hadamard states for the linearized Yang-Mills
  equation on curved spacetime*, <https://arxiv.org/abs/1403.7153>.
- T.-P. Hack and A. Schenkel, *Linear bosonic and fermionic quantum gauge
  theories on curved spacetimes*, <https://arxiv.org/abs/1205.3484>.

Those works provide the gauge-theory state framework. They do not select the
MTT gauge group, one-Higgs module, A51 trace metric, T45 branch, or its future
orientation. Those are the source-specific inputs executed here.

## 12. Reproduction

```powershell
python build_selected_gauge_physical_future_state.py
python verify_selected_gauge_physical_future_state.py
python -m unittest tests.test_selected_gauge_physical_future_state -v
python verify.py
```

The builder verifies every hash in the source lock, executes the rational
mass pencil, both BRST contractions, the broken-mode mixing, transverse
projectors, oscillator complex structure, mode ledger, and claim boundary.
The independent verifier reconstructs these objects from the emitted packet.
