# Physical Yukawa-Incidence KO6 Hessian Compression Theorem

**Claim ID:** `CBF.T23`  
**Date:** 2026-08-29  
**Status:** exact finite physical Yukawa-Laplacian typing theorem; selected
continuum endpoint, Higgs vacuum value and quantum BV promotion remain open

## 1. Result

`CBF.T22` derived the routed family response from one graded operator family,
but correctly refused to call its auxiliary `96D` lift the physical Standard
Model finite Dirac operator. This theorem supplies the missing physical map.

The A46/A48 carrier has one-family left-Weyl ordering

```text
H16 = Q(6) + u^c(3) + d^c(3) + L(2) + e^c(1) + N^c(1).
```

The A48/A51 one-Higgs incidence defines two orthogonal partial isometries:

```text
V_phase : {u^c,e^c} -> {Q_up,L_down},
V_shift : {d^c,N^c} -> {Q_down,L_up}.
```

Insert the already selected CBF.T20 families

```text
Y_p(t)=-P+t(I+Z),
Y_s(t)=-P+t(I+X)
```

into those channels:

```text
T(t)=Y_p(t) tensor V_phase + Y_s(t) tensor V_shift,
D_part(t)=T(t)+T(t)^*.
```

The KO6-real completion is

```text
D_phys(t)=D_part(t) direct_sum conjugate(D_part(t)).
```

It is an exact `96 x 96` self-adjoint, grading-odd and `J_F`-real finite
Dirac-Yukawa family. It uses one selected Higgs doublet, all four Standard
Model Dirac-Yukawa channels and no observed Yukawa or mass value.

Let `H_-` and `H_+` be the CBF.T22 target and source Gram responses. Then

```text
d[D_part(t)^2]/dt at t=0
  = (I3 tensor V) H_- (I3 tensor V)^*
    + H_+,
V=V_phase+V_shift.
```

The first term acts on the left-doublet incidence range and the second on the
right-singlet source range. Thus the two CBF.T22 chiral responses are exactly
the two particle compressions of one physical finite Dirac square. The
antiparticle response is their forced `J_F` conjugate and introduces no
parameter.

For a covariantly constant neutral Higgs radial amplitude `h`, the internal
operator is `h D_phys(t)`, so its square has first variation

```text
h^2 H_phys.
```

At the one-universal-primitive tier of CBF.T22, `h=Lambda=E0=1/L0`; hence the
target compression is exactly `Lambda^2 H_derived`. This physically types the
previous coefficient identity `mu^2=Lambda^2` as a neutral-Higgs radial
Yukawa-Laplacian response. It does not select the numerical value of the Higgs
vacuum.

## 2. Why an incidence map is necessary

The CBF.T20 projectors label the four right-singlet source slots

```text
R_phase={6,7,8,14},
R_shift={9,10,11,15}.
```

These are not by themselves physical Yukawa edges. The A48 finite bimodule and
A51 one-Higgs projection provide their unique unit-incidence targets in the
declared basis:

```text
u:  6,7,8  -> 0,1,2,
e:  14     -> 13,
d:  9,10,11-> 3,4,5,
N:  15     -> 12.
```

Consequently

```text
V_phase^* V_phase=R_phase,
V_shift^* V_shift=R_shift,
V_phase V_phase^*=L_phase,
V_shift V_shift^*=L_shift,
V_phase^*V_shift=V_phase V_shift^*=0,
R_phase+R_shift=R,
L_phase+L_shift=L,
R+L=I16.
```

The map `V=V_phase+V_shift` is unitary from the rank-eight right source onto
the rank-eight left incidence range. This is the physical intertwiner that was
absent from CBF.T22.

## 3. One-Higgs gauge covariance

The four left-Weyl hypercharge sums in units of `6Y` are

```text
u:  1+3-4=0,
d:  1-3+2=0,
e: -3-3+6=0,
N: -3+3+0=0.
```

Color contracts `3` with `bar 3`; weak doublets contract with `H` or its
pseudoreal conjugate. Therefore the covariant incidence family is

```text
Q Y_u H u^c,
Q Y_d conjugate(H) d^c,
L Y_e conjugate(H) e^c,
L Y_N H N^c.
```

The selected A51 projection identifies the up/neutrino doublet and the
down/charged-lepton conjugate doublet. It removes the two extra scalar
doublets of the unrestricted finite one-form space. Family matrices commute
with the gauge representation because the latter is family diagonal.

At a neutral Higgs frame the four covariant contractions reduce exactly to
the unit-incidence maps displayed above. This is a gauge choice for evaluating
the Hessian, not a claim that the compact phase circle is physical time or
that a numerical vacuum has been selected.

## 4. Exact square and compression

The two incidence ranges are orthogonal, so all cross terms vanish:

```text
T(t)T(t)^*
 =G_p,-(t) tensor L_phase + G_s,-(t) tensor L_shift,
T(t)^*T(t)
 =G_p,+(t) tensor R_phase + G_s,+(t) tensor R_shift.
```

Since `D_part=T+T^*` and `T^2=(T^*)^2=0`,

```text
D_part(t)^2=T(t)T(t)^*+T(t)^*T(t).
```

At `t=0`, `P` is unitary and `V` identifies complementary rank-eight
subspaces, giving

```text
D_part(0)^2=I48,
D_phys(0)^2=I96.
```

Differentiating gives the claimed physical particle response

```text
H_part
 =B_phase tensor L_phase+A_shift tensor L_shift
  +B_phase,+ tensor R_phase+A_shift,+ tensor R_shift.
```

The first line is the partial-isometry image of `H_-=H_derived`; the second
is `H_+`. Their supports are disjoint. Each has rank 24 and squared Frobenius
norm 192, so

```text
rank(H_part)=48,       ||H_part||_F^2=384,
rank(H_phys)=96,       ||H_phys||_F^2=768.
```

This also explains why the old auxiliary lift must not be relabelled as the
physical carrier: its inactive derivative complement is removed by the
incidence compression, then the actual antiparticle half is supplied by
`J_F` reality.

## 5. Lorentzian interpretation

On the typed q79 four-dimensional carrier, write the almost-commutative
Dirac-Yukawa family in a covariantly constant radial Higgs frame as

```text
D_AC(t,h)=D_Y tensor I96 + Gamma_Y tensor h D_phys(t).
```

The external grading anticommutes with `D_Y`, so

```text
D_AC(t,h)^2
 =D_Y^2 tensor I96+h^2 I tensor D_phys(t)^2.
```

The internal contribution is order zero and does not change the Lorentzian
principal symbol or characteristic cone. For a varying Higgs field there are
the standard lower-order covariant derivative terms; those do not alter the
principal symbol, but their selected q79 HYM coefficients are not supplied by
this finite theorem.

This operator-square statement is standard almost-commutative geometry, not
an MTT-specific identity. See the [spectral action
principle](https://arxiv.org/abs/hep-th/9606001), the review of [particle
physics from almost-commutative
spacetimes](https://arxiv.org/abs/1204.0328), the Lorentzian [Krein spectral
triple fermionic action](https://arxiv.org/abs/1505.01939), and the KO6
Lorentzian Standard-Model construction in
[Barrett](https://arxiv.org/abs/hep-th/0608221). What is new inside this
program is the exact source-pinned incidence and compression of the MTT
Weyl-Gram response into that standard physical form.

## 6. Exact scope

Closed here:

```text
four-channel physical incidence:                 closed,
one-Higgs gauge-covariant channel typing:         closed,
KO6 self-adjoint/odd/J-real completion:           closed,
H_- and H_+ physical square compressions:         closed,
radial h^2 coefficient and h=Lambda typing:       closed,
new observed or fitted inputs:                    zero.
```

Still open:

```text
upper-MTT selection of the composite root:        open,
numerical Higgs vacuum or E0 value:                open,
selected continuum HYM/Galerkin intertwiner:      open,
physical BV pushforward and quantum QME:           open,
strict masses, mixing angles and threshold data:  open.
```

The theorem does not identify `H_phys` with the scalar Higgs-potential
Hessian. It also does not replace the first-order Grassmann fermionic action
by a squared bosonic action. It identifies the CBF response with the
Laplace-type Dirac-Yukawa square used in propagation, heat-kernel and
second-order fluctuation analysis.

The finite physical typing subclause advances from false to true. The three
same-source physical endpoint packets and all seven endpoint rows still need
the selected continuum source, so acceptance remains `0/3` and `0/7`.
