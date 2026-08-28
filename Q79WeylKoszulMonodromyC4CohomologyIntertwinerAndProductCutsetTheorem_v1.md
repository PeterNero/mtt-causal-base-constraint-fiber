# q79 Weyl-Koszul Monodromy/C4 Cohomology Intertwiner and Product Cutset Theorem v1

## 1. Purpose

The selected finite q79 Weyl pair already supplies an exact 36-dimensional
Weyl-Koszul differential graded algebra, Hodge contraction and harmonic
exterior algebra.  Separately, the q79 spectral branch supplies a flat
rank-six strain local system with full `S3` holonomy and a parallel shared-root
quarter-turn `J_DE`.

This theorem proves that these are not merely similar finite constructions.
The q79 strain local system is exactly a determinant-twisted degree-one Hodge
cohomology shadow of the selected Weyl-Koszul complex.  It also determines the
limit of that statement: the canonical cochain lifts do not preserve the full
forward-difference multiplication, and they do not produce the selected
nonzero-Chern HYM endpoint.

No observed value, fitted coefficient or new branch selector is used.

## 2. Selected finite complex

Work over

\[
  k=\mathbb Q(\omega),\qquad \omega^2+\omega+1=0,
\]

with `A=M3(k)`, the shift and clock matrices `X,Z`, and

\[
 \alpha=\operatorname{Ad}_X,\qquad
 \beta=\operatorname{Ad}_Z.
\]

The selected complex is

\[
 K^0=A,\qquad K^1=A\theta_x\oplus A\theta_z,\qquad
 K^2=A\theta_x\theta_z,
\]

with

\[
 d_0a=((\alpha-1)a,(\beta-1)a),
\]

and

\[
 d_1(b,c)=(\alpha-1)c-(\beta-1)b.
\]

Its exact Hodge data are

\[
 \dim H^\bullet(K)=(1,2,1),
\]

with harmonic basis

\[
 1,\quad \theta_x,\quad \theta_z,\quad
 \theta_x\theta_z.
\]

The reduced Green is the exact polynomial

\[
 G=\frac{7\Delta-\Delta^2}{36},
\]

because the selected spectrum is `0,3,6`.  Thus

\[
 \Delta G=G\Delta=1-P,
 \qquad dh+hd=1-P.
\]

## 3. Exact affine S3 cochain action

Write the six affine permutations of `Z3` as

\[
 g_{\varepsilon,b}(j)=\varepsilon j+b,
 \qquad \varepsilon\in\{+1,-1\},\quad b\in\mathbb Z_3,
\]

and let

\[
 \gamma_g=\operatorname{Ad}_{U_g}.
\]

They obey

\[
 \gamma_g\alpha\gamma_g^{-1}=\alpha^\varepsilon,
 \qquad
 \gamma_g\beta\gamma_g^{-1}=\beta^\varepsilon.
\]

For `epsilon=+1`, set `T0=T1=T2=gamma_g`.  For
`epsilon=-1`, define

\[
 \begin{aligned}
 T_0(a)&=\gamma_g(a),\\
 T_1(b,c)&=(-\gamma_g\alpha^{-1}b,
             -\gamma_g\beta^{-1}c),\\
 T_2(w)&=\gamma_g\alpha^{-1}\beta^{-1}w.
 \end{aligned}
\]

Direct exact matrix calculation gives

\[
 T_1d_0=d_0T_0,
 \qquad
 T_2d_1=d_1T_1.
\]

All six maps are unitary and obey the affine `S3` group law.  Therefore they
define a flat associated cochain bundle over the regular q79 branch
complement.  Since they are unitary cochain maps, and as also checked entry by
entry, they commute with

\[
 \Delta,\qquad P,\qquad G
\]

and intertwine both Hodge homotopies.

On harmonic cohomology their representation type is

\[
 H^0: \mathbf 1,
 \qquad
 H^1: \operatorname{sign}\oplus\operatorname{sign},
 \qquad
 H^2: \mathbf 1.
\]

Thus full `S3` remains holonomy rather than a deck action; no global sheet
labelling has been introduced.

## 4. Exact Fourier C4 cochain action

Let

\[
 F_{jk}=\omega^{jk},
 \qquad
 \gamma_F(a)=\frac13FaF^*.
\]

The scalar normalization cancels in conjugation, and exact arithmetic gives

\[
 \gamma_F\alpha\gamma_F^{-1}=\beta,
 \qquad
 \gamma_F\beta\gamma_F^{-1}=\alpha^{-1}.
\]

Define

\[
 \begin{aligned}
 J_0(a)&=\gamma_F(a),\\
 J_1(b,c)&=(-\gamma_F\beta^{-1}c,\gamma_Fb),\\
 J_2(w)&=\gamma_F\beta^{-1}w.
 \end{aligned}
\]

Then `J` is a unitary cochain map, `J^4=1`, and `J^2` is exactly the affine
reflection `j -> -j`.  It commutes with `Delta,P,G` and the Hodge homotopy.

On harmonic one-forms,

\[
 [\theta_x]\longmapsto[\theta_z],
 \qquad
 [\theta_z]\longmapsto-[\theta_x].
\]

Hence

\[
 J\big|_{H^1}=
 j=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\]

This is exactly the realification of the unique order-four subgroup of the
selected shared `Z64` root.  On cohomology it commutes with the `S3` action.
It does not commute with every translated `S3` holonomy on the full cochain
space, so this paragraph constructs a local cochain symmetry and a global
harmonic symmetry, not a global parallel full-chain `C4` action.

## 5. Determinant-twisted strain intertwiner

Let `E_D` be the q79 rank-three sheet-permutation local system.  The selected
determinant line has monodromy `sign`.  Form

\[
 \mathcal V
 =\det(E_D)\otimes H^1(K)\otimes E_D.
\]

Both `det(E_D)` and `H1(K)` carry `sign`, so their product is trivial:

\[
 \operatorname{sign}\otimes
 (\operatorname{sign}\oplus\operatorname{sign})
 =\mathbf1\oplus\mathbf1.
\]

Consequently `V` has precisely the two-copy permutation monodromy

\[
 P_\sigma\oplus P_\sigma.
\]

In the selected basis, define

\[
 \begin{aligned}
 \Psi(s\otimes[\theta_x]\otimes d_i)&=D_i,\\
 \Psi(s\otimes[\theta_z]\otimes d_i)&=E_i.
 \end{aligned}
\]

The verifier checks all six holonomies and proves

\[
 \Psi\rho_{\mathcal V}(\sigma)
 =\rho_{\rm strain}(\sigma)\Psi.
\]

The harmonic quarter-turn tensored with `I3` becomes

\[
 \Psi(J\otimes I_3)\Psi^{-1}
 =J_{DE}
 =\begin{pmatrix}0&-I_3\\I_3&0\end{pmatrix}.
\]

It commutes with every q79 holonomy matrix and preserves the exact Reynolds
and TT projectors of ranks two and four.  Therefore the previously established
q79 strain local system is an exact determinant-twisted Hodge-`H1` shadow of
the selected finite Weyl-Koszul complex.

## 6. Harmonic product globalization

The harmonic center is the exterior algebra on `theta_x,theta_z`.  Under a
reflection, both degree-one generators acquire `sign`, while their degree-two
product is invariant.  The Fourier quarter-turn has determinant one on the
two harmonic generators.  Hence the exact product

\[
 m_2=\wedge
\]

is globally `S3`- and `C4`-equivariant.  The previously proved higher products
remain

\[
 m_n=0\qquad(n\ge3).
\]

This closes product transport on the harmonic cohomology shadow.

## 7. Full-chain product cutset

The stronger full-DGA statement is false for these canonical lifts.  The
forward-difference calculus selects positive `X` and `Z` directions.  A
reflection converts a positive difference into a shifted negative
difference.  Its cochain correction therefore depends on the coefficient and
is not multiplicative.

For example, with `a=E_00`, `v=I theta_x`, and the reflection `j -> -j`, the
exact verifier finds

\[
 T(av)-T(a)T(v)\ne0.
\]

The canonical Fourier cochain lift likewise has nonzero full-DGA product
defects.  Moreover, its full-chain action does not commute with every affine
`S3` holonomy, even though the induced harmonic actions do commute.

The exhaustive exact counts are:

```text
each affine reflection: 360 defective products out of 1296
Fourier C4 lift:         108 defective products out of 1296
orientation-preserving affine maps: 0 defective products
```

Therefore the theorem does not globalize the full forward-difference DGA.
A symmetric forward/backward covariant calculus, or the actual continuum HYM
deformation complex, would be a new construction rather than an automatic
promotion of this result.

## 8. Geometric meaning

The exact chain is now

```text
selected q79 Weyl pair
    -> finite Weyl-Koszul cochain/Hodge complex
    -> harmonic H1 with sign x C4 quarter-turn
    -> determinant twist by the q79 sheet orientation line
    -> two-copy q79 D/E strain local system with J_DE
    -> Reynolds invariant and TT subbundles.
```

This gives a concrete instance of the preprojection principle: a simple
finite cohomological object in the upper description becomes the q79 strain
constraint after descent.  It is stronger than matching dimensions or
writing isomorphic matrices because it preserves holonomy, Hodge operators,
the shared-root quarter-turn and the harmonic product.

It remains weaker than a physical compactification theorem.  The flat
root-stack/cohomology shadow is not the selected nonzero-Chern HYM deformation
complex.

## 9. Claim boundary

Closed exactly:

- the affine `S3` unitary cochain representation on the selected finite
  Weyl-Koszul complex;
- the Fourier order-four unitary cochain map;
- naturality of `Delta,P,G,h` under both actions;
- harmonic representation types `1,(sign+sign),1` and `1,j,1`;
- the determinant-twisted `H1` intertwiner to the q79 rank-six strain local
  system;
- exact recovery of `J_DE`, the rank-two Reynolds bundle and rank-four TT
  bundle;
- `S3/C4` globalization of the harmonic exterior product;
- the explicit failure of full forward-difference DGA multiplicativity and
  full-chain `S3/C4` commutation.

Still open:

- a globally covariant full cochain algebra carrying the required products,
  connections and nonlinear operations;
- the selected visible/hidden nonzero-Chern HYM endpoint and domains;
- its reduced Green and physical TT response block;
- autonomous `C4` descent on the marked Fu-Yau branch, already excluded for
  the current marking;
- the continuum action, normalization and physical comparison.

## 10. Parameter ledger

```text
new physical continuous parameters: 0
new physical discrete selectors:     0
new fits:                            0
new observed values:                 0
```

The affine group, determinant twist and order-four Fourier action are fixed
by the hash-pinned selected sources.
