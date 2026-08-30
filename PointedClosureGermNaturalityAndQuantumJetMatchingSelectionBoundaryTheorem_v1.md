# Pointed Closure-Germ Naturality and Quantum Jet-Matching Selection-Boundary Theorem v1

**Claim:** CBF.T36

**Date:** 2026-08-30

**Status:** exact pointed-jet retraction and naturality theorem; exact finite
Gaussian no-go against automatic quantum jet preservation; exact reduction of
the T35 matching rule to three typed quantum certificates; no selected
physical BV pushforward, Ward protection, tangent normalization or vacuum
energy normalization.

## 1. Result

CBF.T35 proved that the complete gauge-even radial counterterm class

```text
C_even=span{1,h^2,h^4}
```

contains a unique counterterm that makes the one-loop correction vanish in
value, slope and Hessian at the selected point `h=H`. It left open whether the
three matching conditions are selected by upper MTT.

CBF.T36 answers that question in two parts.

First, once a pointed two-jet is declared part of the quantum projection
contract, T35's prescription is mathematically forced. The jet map

```text
j_H^2 f=(f(H),f'(H),f''(H))
```

restricts to an isomorphism from `C_even` to `R^3` for every `H>0`. Therefore
there is one and only one linear retraction

```text
R_H f=f-(j_H^2|C_even)^(-1)j_H^2 f                  (1.1)
```

onto functions whose zero-through-second jet vanishes at `H`. This retraction
is natural under every pointed field transformation that intertwines the jet
map and the allowed counterterm space.

Second, ordinary action descent, Gaussian/BV pushforward, fixed-source base
change and the quantum master equation do not by themselves supply the
pointed two-jet condition. Exact finite Gaussian examples shift the tadpole or
Hessian while obeying perfectly natural pushforward. A separate normalization
of the fiber measure shifts only the action value. Thus the three T35
conditions are independent quantum matching data unless protected by further
Ward, nonrenormalization, tangent-normalization and determinant-line results.

The existing MTT action corpus supplies a selected classical repair fixed
point and Hessian at its declared tier, a bare cyclic/spectral action lane and
finite source freezing. It does not yet prove that the physical renormalized
BV shadow preserves that fixed point and Hessian, and it does not select its
absolute vacuum-energy normalization. Consequently the full T35 rule is not
derived from the currently selected upper action.

The useful positive result is sharper than that no-go. If first- and
second-jet protection are later proved, the relative one-loop action is
already unique and equals T35's universal remainder. Only the constant
vacuum-energy row remains, and it is irrelevant to normalized
nongravitational correlators but not to gravitational closure.

## 2. Pointed jet exact sequence

Let `A_H` be a vector space of real action germs at a positive radial point
`H`. Define

```text
j_H^2:A_H -> J_H^2=R^3,
j_H^2(f)=(f(H),f'(H),f''(H)).                         (2.1)
```

The kernel is the third power of the maximal ideal at `H`:

```text
ker j_H^2=m_H^3.
```

On the ordered basis `(1,h^2,h^4)` of `C_even`, the restriction of (2.1) is

```text
M_H=[ 1   H^2   H^4  ]
    [ 0   2H    4H^3 ]
    [ 0   2     12H^2].                              (2.2)
```

Its determinant is

```text
det M_H=16H^3.                                       (2.3)
```

Hence `M_H` is invertible exactly when `H` is nonzero.

### Theorem 2.1: unique jet retraction

For `H>0`, define `c_H(f)` to be the unique element of `C_even` satisfying

```text
j_H^2 c_H(f)=j_H^2 f.
```

Then

```text
R_H=I-c_H
```

has the following properties:

```text
image R_H = ker j_H^2,
kernel R_H=C_even,
R_H^2=R_H,
j_H^2 R_H=0.                                         (2.4)
```

It is the unique linear projection with image `ker j_H^2` and kernel
`C_even`.

### Proof

Equation (2.3) gives a direct-sum splitting

```text
A_H=ker j_H^2 direct_sum C_even.
```

The two summand projections are therefore unique. Equations (2.4) follow
immediately from the splitting. QED.

This theorem does not choose a physical renormalization condition. It proves
that no coefficient freedom remains after the pointed jet and counterterm
class have been selected.

## 3. Naturality and field normalization

Consider two pointed action-germ objects

```text
(A_H,C_H,J_H,j_H),
(A_K,C_K,J_K,j_K).
```

Let `T:A_H->A_K`, `T_C:C_H->C_K` and `T_J:J_H->J_K` be isomorphisms such that

```text
T(C_H)=C_K,
j_K T=T_J j_H.                                       (3.1)
```

### Theorem 3.1: naturality of jet matching

The unique retractions satisfy

```text
R_K T=T R_H.                                         (3.2)
```

### Proof

Condition (3.1) sends `ker j_H` to `ker j_K` and sends the chosen complement
`C_H` to `C_K`. Both sides of (3.2) are therefore the same direct-sum
projection after transport by `T`. QED.

For the radial scaling `u=a h`, `a>0`, let

```text
(T_a f)(u)=f(u/a),
K=aH.
```

Then

```text
j_K^2(T_a f)=diag(1,a^-1,a^-2)j_H^2(f),             (3.3)
R_K T_a=T_a R_H.
```

Equation (3.3) exposes an important boundary. Hessian naturality is tensorial;
numeric equality of Hessian coefficients in two radial coordinates additionally
requires a selected tangent isometry or wave-function normalization. A field
rescaling is not a failure of naturality, but it changes the displayed Hessian
by `a^-2`.

## 4. Natural pushforward does not preserve the jet

Let `x` be a retained field and `y` an eliminated real Gaussian field. On a
neighborhood of `x=0`, take

```text
S_odd(x,y)=S_0(x)+(1/2)(1+2g x)y^2.                  (4.1)
```

The normalized finite Gaussian pushforward gives

```text
Gamma_odd(x)=S_0(x)+(1/2)log(1+2g x)+constant.       (4.2)
```

The loop jet at zero is

```text
j_0^2(Delta Gamma_odd)=(0,g,-2g^2).                  (4.3)
```

For `g!=0`, the pushforward shifts both the stationary equation and Hessian.
Nothing is non-natural: (4.2) is the exact fiber integral of (4.1).

Now impose the reflection symmetry `x -> -x` and use

```text
S_even(x,y)=S_0(x)+(1/2)(1+g x^2)y^2.                (4.4)
```

Then

```text
j_0^2(Delta Gamma_even)=(0,0,g).                     (4.5)
```

The symmetry protects the tadpole but not the Hessian. This is an exact
counterexample to deriving second-jet preservation from fixed-point symmetry
alone.

Finally, multiplying the fiber measure by `exp(-C)` shifts the effective
action by `C` and changes

```text
j_0^2 Gamma -> j_0^2 Gamma+(C,0,0).                  (4.6)
```

It changes no equation of motion, Hessian, normalized nongravitational
correlator or QME identity. The zero-jet normalization is therefore separate
from the first and second jets.

Equations (4.3)-(4.6) prove that generic projection/pushforward naturality
cannot select T35's matching conditions.

## 5. What the existing MTT action results provide

The current source lock separates the available statements.

H4-T8 proves that the full repair jet and graph tensors transport under a
declared residual/metric intertwiner. It explicitly does not perform
continuum renormalization or choose counterterms.

H4-T9 proves that the positive repair Hessian, signed action Hessian and BV
action are different typed objects. Equality of their kernels or normal
squares is insufficient.

H4-T10 supplies exact descent of a cyclic Maurer-Cartan bare action and its
signed Hessian. It leaves the physical compactification, QME and
renormalization open.

A84 identifies the selected closure Hessian as the repair semigroup generator
and derives the heat-shadow action clause at its declared action tier. A85
closes bare finite-source completeness while explicitly retaining finite local
renormalization freedom.

CBF.T33 and T35 freeze the upstream source coordinate `t_*` through the lower
pushforward. They do not freeze the lower radial field `h`, protect its
quantum tadpole, or select its physical kinetic normalization.

Therefore the existing results provide the classical pointed repair germ and
the allowed counterterm complement, but not a quantum morphism satisfying
(3.1) for the physical action germ.

## 6. Exact reduction of the T35 determinant

Write the T35 fixed-source fermion loop as

```text
V_F(h)=-kappa_F h^4[
 q4_* log(h^2/mu^2)+L4_*-c_scheme q4_*
].                                                     (6.1)
```

Let

```text
L_H=q4_* log(H^2/mu^2)+L4_*-c_scheme q4_*.
```

If only first- and second-jet preservation are imposed, the two nonconstant
counterterms are already unique:

```text
delta m2    =-2 kappa_F q4_* H^2,
delta lambda= kappa_F[L_H+(3/2)q4_*].                 (6.2)
```

The vacuum term `delta Omega` remains free. The corrected loop is

```text
Delta V_12(h)=kappa_F q4_*[
 h^4(log(H^2/h^2)+3/2)-2H^2h^2
]+delta Omega.                                        (6.3)
```

Subtracting its value at `H` removes the arbitrary constant and gives

```text
Delta V_12(h)-Delta V_12(H)
=kappa_F q4_*[
 h^4(log(H^2/h^2)+3/2)-2H^2h^2+H^4/2
].                                                     (6.4)
```

Equation (6.4) is exactly the T35 universal remainder. Thus its third- and
fourth-jet predictions do not depend on vacuum-energy normalization. The
zero-jet condition fixes the last coefficient to

```text
delta Omega=(1/2)kappa_F q4_* H^4.                    (6.5)
```

For a nongravitational relative effective action, (6.4) is the strongest
meaningful result. For a theory including gravity, (6.5) is a physical
cosmological/vacuum-energy row and cannot be selected by declaring additive
constants irrelevant.

## 7. Minimal quantum closure-germ packet

The T35 prescription is selected, rather than merely available, exactly when
one same-source physical packet supplies the following certificates.

```text
QJ1  fixed-point/tadpole protection:
     d Gamma(H)=0,

QJ2  normalized Hessian intertwining:
     I_H^* Hess Gamma(H) I_H=H_cl
     with a selected kinetic metric/tangent isometry,

QJ0  pointed determinant normalization:
     Gamma(H)=S_base(H)
     or an equivalent normalized determinant-line/gravitational rule.
```

These are certificates, not three adjustable scalar parameters. Once they
hold, Theorem 2.1 fixes every coefficient uniquely. QJ1 and QJ2 suffice for
the relative nongravitational action. QJ0 is additionally required for an
absolute action coupled to gravity.

The QME or gauge Ward identities may help prove QJ1/QJ2, but gauge invariance
alone permits gauge-invariant local counterterms and therefore does not imply
them. A supersymmetric or other nonrenormalization theorem could also supply
the protection, but no such selected q79 theorem is currently present.

## 8. Exact scientific boundary

Closed here:

- the exact pointed two-jet sequence for the radial counterterm class;
- the unique natural jet-matching retraction;
- covariance under radial field rescaling and the tangent-normalization
  boundary;
- exact finite Gaussian counterexamples to automatic tadpole and Hessian
  preservation;
- independence of zero-jet normalization from dynamics and the QME;
- reduction of full selection to QJ0, QJ1 and QJ2; and
- uniqueness of the T35 relative remainder once QJ1/QJ2 hold.

Still open:

- a selected physical quantum action and external BV pushforward on q79;
- QJ1 tadpole protection at the T34 radial point;
- QJ2 physical kinetic normalization and Hessian intertwining;
- QJ0 determinant-line or gravitational vacuum normalization;
- source RG transport, bosonic/gauge/gravitational loops and Ward/QME
  execution;
- absolute scale, particle-sector map, pole transport and held-out data.

Accordingly, the full closure-jet rule remains unselected and physical
acceptance remains

```text
packets: 0/3,
rows:    0/7.
```

This is not a failure of the constraint-first program. It identifies the
precise categorical object that the quantum projection must preserve and
proves that the remaining issue cannot be repaired by another finite
counterterm calculation.

## 9. Primary external context

Finite BV integration and homological pushforward supply natural effective
actions and master-equation transport, but not preservation of an arbitrarily
chosen local action jet. See the finite-dimensional BV treatment and the
BV-BFV pushforward framework:

- C. Albert, B. Bleile and J. Froehlich,
  [Batalin-Vilkovisky Integrals in Finite Dimensions](https://arxiv.org/abs/0812.0464).
- A. Cattaneo, P. Mnev and N. Reshetikhin,
  [Perturbative Quantum Gauge Theories on Manifolds with Boundary](https://arxiv.org/abs/1507.01221).

Costello's BV renormalization framework and the Hollands-Wald uniqueness
theorem likewise retain controlled local renormalization freedom rather than
selecting MTT's pointed jet:

- K. Costello,
  [Renormalisation and the Batalin-Vilkovisky Formalism](https://arxiv.org/abs/0706.1533).
- S. Hollands and R. Wald,
  [Local Wick Polynomials and Time Ordered Products of Quantum Fields in Curved Spacetime](https://arxiv.org/abs/gr-qc/0103074).

These sources support the general boundary only. They do not prove the
q79-specific jet selector or any physical MTT value.

## 10. Reproduction

```powershell
python build_pointed_closure_germ_quantum_jet_matching.py
python verify_pointed_closure_germ_quantum_jet_matching.py
python -m unittest tests.test_pointed_closure_germ_quantum_jet_matching -v
python verify.py
```

The generated packet is
`pointed_closure_germ_quantum_jet_matching.packet.json`.
