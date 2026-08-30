# Selected Radial-Higgs Future State and Complete Free-Seed Theorem v1

**Claim ID:** `CBF.T48`

**Date:** 2026-08-30

**Status:** exact selected radial-Higgs free state and complete homogeneous-flat
broken-phase free product seed at the T34 finite direct-source, selected
internal-checkpoint and positive-relative-action Gaussian tier; absolute
field normalization, nonlinear upper-action/BV selection, determinant
holonomy, fixed-coupling continuum, `G1`, q79 HYM universality and top-level
physical `G2` remain open

## 1. Result

CBF.T47 left exactly one free factor open:

```text
omega_0,H
  =omega_gauge,H,phys tensor omega_h,rad tensor omega_Weyl.
```

T45 selects the Weyl factor and T47 selects the rank-27 gauge-physical
factor. The missing object is not a probability law for the background value
`H`; it is the two-point covariance of the one remaining radial Higgs
fluctuation.

That factor is already determined on the narrower T34 stationary branch.
The source chain is literal:

```text
A51 one-Higgs incidence
  -> T23 physical h D_phys(t)
  -> T24 total closure charge
  -> T30/T34 frozen t=t_*
  -> T34 selected H=H_* and f2/f0
  -> T32 fixed-source radial quadratic action.
```

No equality of dimensions is used as an identification. T23 proves that `h`
is the neutral radial amplitude of the selected A51 one-Higgs doublet in the
physical finite Dirac-Yukawa operator. T34 uses that same totalized operator.

At the selected source coordinate

```text
t_*=(1-sqrt(13))/6,
```

put

```text
q2_*=(14+sqrt(13))/3,
q4_*=(356+25sqrt(13))/27,
c=(f2/f0)Lambda^2.
```

The fixed-source potential and kinetic form, after suppressing one inherited
common positive action coefficient `A_H`, are

```text
P_*(h)=q4_* h^4-4c q2_* h^2,
T_*(h)=q2_* (partial h)^2.                         (1.1)
```

T34 selects

```text
H_*^2=2c q2_*/q4_*,
c/Lambda^2=15/log(448).                            (1.2)
```

The potential then has the exact square completion

```text
P_*(h)-P_*(H_*)=q4_* (h^2-H_*^2)^2.               (1.3)
```

For `h=H_*+eta`, the canonically normalized fluctuation

```text
phi=sqrt(2 A_H q2_*) eta                            (1.4)
```

has quadratic mass

```text
m_h^2=8c,
m_h^2/Lambda^2=120/log(448)>0.                     (1.5)
```

Thus the Euclidean free covariance is the inverse of
`-Delta_E+m_h^2`. Its Fourier kernel factorizes into an exact
Osterwalder-Schrader square on positive Euclidean time. The selected T45
future orientation chooses its positive-frequency boundary value, giving

```text
Omega_h=sqrt(-Delta+m_h^2),
J_h^fut(q,p)=(-Omega_h^(-1)p,Omega_h q).            (1.6)
```

Equation (1.6) selects the unique regular spatially translation-invariant
pure quasifree ground state in the future spectrum class. Since
`Omega_h>=m_h>0`, there is no scalar zero-mode selector on `R^3`.

The complete corrected free seed is therefore

```text
omega_0,H_*
 =omega_gauge,H_*,phys^fut
   tensor omega_h,rad^fut
   tensor omega_Weyl,H_*^fut.                      (1.7)
```

The T46 canonical homotopy-gauge lift can now be instantiated from this full
seed. This closes the free-seed input and the lift ambiguity. It does not
select the interacting BV map, its normalization, or a fixed-coupling
positive continuum state.

## 2. Same physical radial line

The radial variable is not introduced in T48. CBF.T23 constructs

```text
D_phys(t)=D_part(t) direct_sum conjugate(D_part(t)),
D_AC(t,h)=D_Y tensor I96+Gamma_Y tensor h D_phys(t).
```

Its incidence maps are the exact A51 one-Higgs contractions

```text
Q Y_u H u^c,
Q Y_d conjugate(H) d^c,
L Y_e conjugate(H) e^c,
L Y_N H N^c.
```

In the neutral frame, `h` is their common radial amplitude. T24 totalizes the
same finite differential, and T34 freezes its finite source coordinate and
selects its radial stationary branch. Therefore

```text
h_T23=h_T24=h_T32=h_T34=H_*                         (2.1)
```

as one typed source coordinate, not merely as four isomorphic real lines.

The optional T23 metrology equation `h=Lambda` is not imposed here. T33 and
T34 already proved that it is incompatible with the selected moment ratio and
bare radial stationarity. T48 adopts the T34 stationary branch

```text
H_*/Lambda
 =sqrt[15(3106+4sqrt(13))/(4393 log(448))].         (2.2)
```

This leaves `Lambda` dimensionful and unresolved. It does not make (2.2) an
observed electroweak vacuum expectation value.

## 3. Exact radial expansion

At fixed `t=t_*`, only `h` is varied. The identities

```text
q2_*>0,
q4_*>0,
R_*=2q2_*/q4_*=(3106+4sqrt(13))/4393>0              (3.1)
```

give `H_*^2=R_* c`. Differentiation of (1.1) yields

```text
P_*'(H_*)=0,
P_*''(H_*)=16c q2_*,
P_*'''(H_*)=24q4_* H_*,
P_*''''(H_*)=24q4_*.                                (3.2)
```

Equivalently, (1.3) gives the complete local expansion

```text
P_*(H_*+eta)-P_*(H_*)
 =8c q2_* eta^2+4q4_* H_* eta^3+q4_* eta^4.        (3.3)
```

The quadratic coefficient is strictly positive. On the physical radial
half-line `h>=0`, (1.3) also proves that `H_*` is the unique positive global
minimum. The reflected algebraic minimum `-H_*` is the same doublet orbit
after the central phase action; it is not a second radial particle or vacuum
parameter in this gauge-fixed chart.

The source modulus `t` is not varied again. T30/T34 already selected and
froze it before the lower radial variation. Consequently T48 contains one
scalar fluctuation, not the conditional two-field extension rejected as a
physical claim in T32.

## 4. Canonical Hessian

Restore the unresolved common positive coefficient `A_H>0`. The Lorentzian
quadratic form obtained from the Gaussian continuation of (1.1) is

```text
S_rad^(2)
 =A_H integral [q2_* partial_mu eta partial^mu eta
                -8c q2_* eta^2].                   (4.1)
```

With (1.4),

```text
S_rad^(2)
 =1/2 integral [partial_mu phi partial^mu phi-m_h^2 phi^2],
m_h^2=P_*''(H_*)/(2q2_*)=8c.                       (4.2)
```

Both `A_H` and `q2_*` cancel from the generalized curvature mass. At the T34
checkpoint,

```text
m_h/Lambda=sqrt(120/log(448))
           =4.43358606544780223278... .             (4.3)
```

The exact checkpoint invariant is

```text
(m_h^2/Lambda^2) tau_int=8,
tau_int=log(448)/15.                                 (4.4)
```

The unresolved `A_H` fixes the conversion between the original coordinate
`eta` and the canonical observable `phi`. It is an inherited action
normalization, not a state selector added by T48. Absolute field amplitudes,
an SI value of `Lambda`, and the renormalized Higgs pole mass remain open.

## 5. Gaussian reflection positivity

The free Euclidean two-point function of `phi` is

```text
C_E(tau,x)
 =integral d^3p/((2pi)^3 2omega(p))
    exp(i p.x-omega(p)|tau|),
omega(p)=sqrt(|p|^2+m_h^2).                         (5.1)
```

Let `f` be a smooth compactly supported test function with support in
`tau>0`, and let `theta(tau,x)=(-tau,x)`. Direct Fourier substitution gives

```text
<theta f,C_E f>
 =integral d^3p/((2pi)^3 2omega(p))
    |integral_0^infinity d tau
       exp(-omega(p) tau) f_hat(tau,p)|^2
 >=0.                                               (5.2)
```

This is an explicit reflection-positivity proof for the selected Gaussian;
no nonlinear Euclidean measure is assumed. For positive Euclidean time,
`exp(-omega z)` is analytic on `Re z>0`. Its boundary value at
`z=epsilon+i(t-t')`, with `epsilon` decreasing to zero, is

```text
Lambda_h^+(x,x')
 =integral d^3p/((2pi)^3 2omega(p))
    exp(-iomega(p)(t-t')+i p.(x-x')).               (5.3)
```

The opposite boundary value is the past-frequency conjugate. T45's selected
future orientation chooses (5.3). Thus the free Wick bridge is fixed by
reflection positivity plus the already selected orientation. T48 does not
claim a nonlinear Osterwalder-Schrader reconstruction of the interacting
spectral action.

## 6. Future-positive scalar state

On scalar Cauchy data, use the symplectic matrix

```text
S=[ 0  I]
  [-I  0].                                          (6.1)
```

Equation (1.6) obeys

```text
(J_h^fut)^2=-I,
(J_h^fut)^T S J_h^fut=S,
S J_h^fut=diag(Omega_h,Omega_h^(-1))>0.             (6.2)
```

### Theorem 6.1: selected radial ground state

Fix the T34 stationary `H_*` branch, its inherited positive scalar-action
normalization, the T45 flat spacetime and future orientation. Among regular,
spatially translation-invariant pure quasifree scalar states satisfying the
future ground-state spectrum condition, (1.6) is unique.

### Proof

The spatial Fourier transform decomposes the field into oscillators of
strictly positive frequency `omega(p)>=m_h`. CCR compatibility, purity and
the ground-state condition fix on every spectral fiber

```text
J_omega=[0,-omega^(-1);omega,0].                    (6.3)
```

Their direct integral is (1.6). No zero-frequency fiber exists, so no extra
covariance can be supported at `p=0`. Equation (5.3) is its two-point
function. It is the standard massive Minkowski ground-state kernel and is
Hadamard. QED.

Thermal, squeezed and mixed quasifree states exist, but they fail at least one
of the selected purity or future ground-state conditions. Their existence is
not an ambiguity in this theorem.

## 7. Correct broken-phase seed

T47 proves that the single A51 Higgs doublet decomposes on `H_*>0` as three
Goldstone directions in the broken BRST complexes plus one radial direction.
The Goldstones supply the three longitudinal massive gauge polarizations and
must not be counted again. Therefore

```text
gauge physical modes: 18 massless+9 massive=27,
radial Higgs modes:                             1,
total bosonic physical modes:                 28.    (7.1)
```

The radial tangent `eta` is orthogonal to the gauge orbit in the A51
one-Higgs kinetic form. The frozen family source `t_*` is not another scalar
mode. Hence the factor in Theorem 6.1 is exactly the one missing factor in
T47, rather than a duplicate of any gauge or source direction.

Tensor products of normalized positive states are normalized and positive;
tensor products of pure free factor states are pure. The componentwise
Hadamard wavefront condition gives a Hadamard state for the finite direct sum
of free fields. Thus (1.7) is the complete free physical product seed on this
homogeneous flat branch at the inherited relative-action tier.

## 8. Canonical formal lift

T46 proves that, once a full free physical vector is fixed, the existing q79
deformation theorem and certified contraction give the unique recursive lift

```text
psi_n=-h r_n,
p psi_n=0,
h psi_n=0.                                          (8.1)
```

Before T48, the premise was not met because the scalar state factor was
missing. Equation (1.7) now supplies the complete seed, so (8.1) applies to
its dense finite-particle domain and the formal state pullback is fixed
relative to the existing BV intertwiner.

This closes the free-seed input and formal-lift choice. It does not prove that
the T39 anchored normalization or the interacting BV intertwiner is selected
by one upper physical action. Coefficientwise formal positivity is not a
fixed-coupling Cstar state.

## 9. Type separations

### 9.1 T38 is not used as the fluctuation state

T38's `delta_H` evaluates the background radial coordinate. It has zero
background variance. T48 instead constructs the nonzero distributional
two-point function (5.3) for local fluctuations. The construction sources do
not include the T38 packet; it is hash-locked only as a comparison.

### 9.2 T39 remains an interacting boundary

The T35 fermion determinant has a nonzero one-loop tadpole at the T34 point.
T39 proves that an anchored local-formal counterterm scheme can preserve the
selected value, tadpole and Hessian, but upper-action selection of that scheme
is open. T48 is the free Gaussian state of the selected tree Hessian. It does
not claim that loop corrections leave (4.3) equal to the physical pole mass.

### 9.3 T40 `G1` is not silently closed

T23 and T32 provide a physical lower direct-branch radial coordinate and
kinetic form. They do not produce an upper q79/HYM tangent map `Dp` satisfying

```text
(Dp)^* g_H Dp=g_up.
```

Therefore the direct radial covariance is closed while the independent
upper-to-lower `G1` tangent-isometry gate remains open.

## 10. G2 and parameter ledger

```text
G2a flat-branch Weyl state:                    closed by T45,
G2a flat-branch gauge physical state:          closed by T47,
G2a flat-branch radial Higgs state:             closed by T48,
G2b complete free product seed:                 closed by T48,
G2b exact background Dirac state transport:    closed by T46,
G2b formal state pullback and canonical lift:  closed by T46/T48,
G2b selected upper action and full BV map:      open,
G2c selected fixed-coupling continuum:          open 0/9,
top-level physical G2:                          open. (10.1)
```

The parameter ledger is

```text
new observed inputs:                  0,
new fitted parameters:                0,
new continuous state selectors:       0,
new discrete state selectors:         0,
inherited future orientation:         1 discrete branch structure,
selected dimensionless H_*/Lambda:    T34 exact value,
selected dimensionless m_h/Lambda:    sqrt(120/log(448)),
inherited absolute Lambda:             unresolved,
inherited scalar-action amplitude A_H: unresolved positive normalization.
```

No top-level physical endpoint counter changes. Those counters require the
same upper action, selected interacting map, continuum endpoint and physical
row certificates. They remain

```text
physical gates:   0/3,
physical packets: 0/3,
physical rows:    0/7.                              (10.2)
```

## 11. Scientific boundary

T48 proves:

- the T23 one-Higgs radial line and T34 stationary line are one typed source;
- the exact fixed-source square completion and all radial derivatives;
- the positive canonical mass `m_h^2=8c` and selected cutoff ratio;
- Gaussian reflection positivity by an explicit Fourier square;
- the unique future-positive pure quasifree Hadamard radial state;
- absence of a scalar zero-mode selector on the massive flat branch;
- the corrected complete gauge-radial-Weyl free product seed;
- applicability of the T46 canonical formal lift to that complete seed.

T48 does not prove:

- an observed Higgs mass, VEV, pole mass or SI cutoff;
- absolute scalar or gauge action normalization;
- nonlinear Euclidean-to-Lorentzian reconstruction;
- upper-action selection of the T39 normalization or full BV map;
- determinant-line connection or relative holonomy;
- compact cosmological harmonic-mode states;
- a regulator-independent fixed-coupling interacting state;
- the physical `G1` upper tangent metric or q79 HYM/direct intertwiner;
- top-level `G2` or any q79 physical endpoint row.

The frontier therefore changes in one precise way: the complete free seed is
no longer missing a factor. The next obstruction is not another free vacuum;
it is same-upper-action selection of the interacting BV map and its
normalization.

## 12. Primary mathematical context

The Gaussian continuation used here is the free-field specialization of the
corrected [Osterwalder-Schrader reconstruction
theorem](https://doi.org/10.1007/BF01608978). Equation (5.2) proves the needed
reflection positivity directly rather than importing it as a label.

Static ground-state Hadamard results are discussed by
[Wrochna](https://arxiv.org/abs/1108.2982). General constructions of pure
regular Klein-Gordon Hadamard states are given by
[Gerard, Oulghazi and Wrochna](https://arxiv.org/abs/1602.00930).

These references establish the standard free-field context. The MTT-specific
content is the exact source chain selecting `t_*`, `H_*`, the relative radial
Hessian and the common future branch without an observed mass input.

## 13. Reproduction

```powershell
python build_selected_radial_higgs_future_state.py
python verify_selected_radial_higgs_future_state.py
python -m unittest tests.test_selected_radial_higgs_future_state -v
python verify.py
```

The generated machine certificate is
`selected_radial_higgs_future_state.packet.json`.
