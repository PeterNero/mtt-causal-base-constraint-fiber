# Symmetric Weyl Transferred m4 and Arity-Four Stasheff Theorem v1

## 1. Purpose

The preceding theorem constructed an exact strong deformation retract from the
144-dimensional symmetric signed Weyl DGA to the 48-dimensional target

\[
 T=\Omega_{\rm old}\oplus J,
\]

where `J` is the twelve-class higher-jet harmonic ideal. It computed a nonzero
transferred `m3` and verified the arity-three Stasheff identity exactly.

That result left one immediate mathematical question:

> Does the transferred structure truncate after `m3`, or is a further
> operation required?

This theorem decides the question. The transferred `m4` is nonzero. Its full
basis support is computed, and the arity-four Stasheff identity is verified on
every degree-admissible homogeneous basis quadruple.

Thus the finite response target is not a ternary truncation. It carries a
genuine higher `A_infinity` hierarchy through at least arity four.

This is a finite algebraic result. It does not identify `m4` with a physical
four-point vertex.

## 2. Pinned source boundary

The construction consumes the source-locked objects from the preceding result:

1. the 144-dimensional associative symmetric Weyl DGA `A`;
2. the exact strong deformation retract `(i,p,H)` from `A` to `T`;
3. the already certified operations `m1`, `m2` and `m3`;
4. the exact identification of `J` as higher-jet harmonic data.

All local inputs are commit-, Git-blob- and SHA-256-pinned at commit
`6c6c8ae87683ad16d563bbda843faa2a10d91471`. The recursive sign convention is
the convention of Merkulov's explicit homotopy-transfer construction, calibrated
by exact equality with the previously verified local `m3` on all 110,592 basis
triples.

Reference: S. A. Merkulov, *Strongly homotopy algebras of a Kahler manifold*,
arXiv:`math/9809172`, DOI:`10.1155/S1073792899000070`.

## 3. Low-arity convention

Let `mu` denote the associative product on `A`. The contraction maps have
degrees

```text
|i|=|p|=0,
|H|=-1.
```

The transferred operations use the cohomological convention

\[
 |m_n|=2-n.
\]

Write

\[
 \lambda_2(a,b)=\mu(ia,ib).
\]

The source-valued ternary recursion is

\[
 \begin{split}
 \lambda_3(a,b,c)={}&
 \mu(H\mu(ia,ib),ic)\\
 &-(-1)^{|a|}\mu(ia,H\mu(ib,ic)),
 \end{split}
 \tag{1}
\]

and

\[
 m_3=p\lambda_3.
\]

Exact execution confirms that (1) reproduces the prior `m3` on all 110,592
homogeneous basis triples. This removes any freedom to alter the `m4` signs
after seeing the answer.

## 4. The transferred m4

Under the same convention, the source-valued quaternary recursion is

\[
 \begin{split}
 \lambda_4(a,b,c,d)={}&
 -\mu(H\lambda_3(a,b,c),id)\\
 &-(-1)^{|a|+|b|}
   \mu(H\mu(ia,ib),H\mu(ic,id))\\
 &-\mu(ia,H\lambda_3(b,c,d)).
 \end{split}
 \tag{2}
\]

Define

\[
 m_4=p\lambda_4.
 \tag{3}
\]

Equation (2) contains all five planar binary trees with four leaves: two trees
inside the left `lambda3`, the balanced tree, and two trees inside the right
`lambda3`. The Koszul sign in the balanced term comes from moving the
degree-minus-one map `H lambda2` past the first two inputs.

### Theorem 4.1

The operation `m4:T^{tensor 4}->T` defined by (2)-(3) has degree `-2` and is
nonzero.

### Proof

Each binary product has degree zero. The two internal homotopies in every tree
have total degree `-2`, while `i` and `p` have degree zero. Therefore `m4` has
degree `-2`.

For the basis quadruple

```text
C:0,0,1
C:0,0,1
C:1,0,1
C:1,0,0
```

exact arithmetic over `Q(omega)` gives

```text
m4 = -(omega/8) C:2,0,1.
```

Hence `m4` is nonzero. QED.

## 5. Arity-four coherence

With Koszul evaluation signs, the arity-four Stasheff identity is

\[
 \begin{split}
0={}&m_1m_4(a,b,c,d)\\
&-m_2(m_3(a,b,c),d)
 -(-1)^{|a|}m_2(a,m_3(b,c,d))\\
&+m_3(m_2(a,b),c,d)
 -m_3(a,m_2(b,c),d)
 +m_3(a,b,m_2(c,d))\\
&-m_4(m_1a,b,c,d)
 -(-1)^{|a|}m_4(a,m_1b,c,d)\\
&-(-1)^{|a|+|b|}m_4(a,b,m_1c,d)\\
&-(-1)^{|a|+|b|+|c|}m_4(a,b,c,m_1d).
 \end{split}
 \tag{4}
\]

### Theorem 5.1

The operations `(m1,m2,m3,m4)` satisfy (4) on `T`.

### Proof

The exact maps `(i,p,H)` satisfy

\[
 pi=1,
 \qquad
 dH+Hd=1-ip,
 \qquad
 H^2=pH=Hi=0.
\]

The source product is associative and its differential is a derivation. The
standard homotopy-transfer recursion therefore cancels the boundary faces of
the five four-leaf trees in pairs. The remaining outer edges are precisely the
ten terms in (4).

For a machine-level check independent of this formal cancellation, the target
has degree dimensions

\[
 (9,20,14,4,1).
\]

There are `48^4=5,308,416` basis quadruples. Since `|m4|=-2`, a nonzero output
requires total input degree between two and six. This leaves exactly
`3,869,500` degree-admissible quadruples; the other `1,438,916` vanish by degree.
Exact `Q(omega)` evaluation of (4) has zero residual on every one of the
`3,869,500` admissible quadruples. QED.

## 6. Complete exact execution

The exhaustive operation table gives

```text
all basis quadruples:                              5,308,416
degree-admissible basis quadruples:                3,869,500
degree-forced-zero basis quadruples:               1,438,916
nonzero m4 basis quadruples:                         693,208
arity-four residual failures:                             0
nonzero m4 values containing the unit:                     0
nonzero all-harmonic m4 values:                            0
nonzero m4 values with three or four J inputs:             0
```

The complete nonzero operation table has canonical digest

```text
a534a7f2921037aeea145f865502fc9e78928d030363bb6e5f57c88f4b59231e
```

The recursion itself has substantial exact repetition:

```text
nonzero binary homotopy states:                     1,024
distinct nonzero binary homotopy values:              585
nonzero ternary homotopy states:                   39,764
distinct nonzero ternary homotopy values:          11,174
```

These repetitions are used only to accelerate exact evaluation. They do not
replace any quadruple by a numerical approximation.

## 7. Higher-jet support

Classifying nonzero values by the number of higher-jet inputs gives

```text
zero J inputs: 363,928
one J input:   293,208
two J inputs:   36,072
three J inputs:      0
four J inputs:       0
```

Thus the higher-jet ideal participates more deeply at arity four than it did at
arity three: two `J` inputs can contribute. But three or more cannot contribute
to `m4`.

Classifying outputs gives

```text
old only:     481,920
J only:       142,640
old plus J:    68,648
```

The operation therefore cannot be represented solely on the old 36-dimensional
response lanes. Retaining `J` was necessary not only for cohomology but also for
the complete chain-level higher transfer.

## 8. A mixed witness

The first lexicographic witness involving both sectors is

```text
a = C:0,0,1,
b = C:1,0,0,
c = J:5,
d = C:1,0,0.
```

Exact arithmetic gives

```text
m4(a,b,c,d) = (-1/12 + omega/12) C:2,0,1.
```

This is direct evidence that a higher-jet harmonic input can alter an old-lane
chain response. It is not evidence that `J` is an independently propagating
physical field.

## 9. Meaning of the result

The finite preprojection hierarchy now has the form

```text
associative symmetric DGA upstairs
    -> exact 48-dimensional retract
    -> nonassociative transferred m2
    -> nonzero m3 repairing SI(3)
    -> nonzero m4 repairing SI(4).
```

This establishes that the old compressed associator was only the first visible
part of a genuine higher transfer. The finite object does not truncate at
`m3`.

The result also sharpens the next question. It is no longer sensible to assume
that `m5` and higher vanish. They must be computed or eliminated by a separate
structural theorem.

## 10. Claim boundary

Closed exactly:

- the Merkulov-recursive `lambda4` with signs calibrated to the prior `m3`;
- the complete transferred `m4` on the 48-dimensional target;
- nonvanishing and exact degree `-2` of `m4`;
- strict-unit vanishing;
- all-harmonic vanishing;
- vanishing with three or four higher-jet inputs;
- the complete one- and two-higher-jet support counts;
- the complete output-sector counts;
- the arity-four Stasheff identity on all degree-admissible basis quadruples;
- the conclusion that the finite transfer does not truncate after `m3`.

Still open:

- computation or a vanishing theorem for `m5` and higher;
- identification of `T`, `m3` or `m4` with `D_fin` or rank-102 response data;
- the selected nonzero-Chern q79 HYM endpoint, connection and reduced Green;
- physical `C4` naturality and finite-to-continuum error bounds;
- a cyclic, BV or Lorentzian action compatible with the transferred operations;
- any interpretation of finite `m4` as a physical four-point vertex;
- closure of `B.GEO.01`, `B.OP.01` or `B.ACTION.01`.

## 11. Parameter ledger

```text
new physical continuous parameters: 0
new physical discrete selectors:     0
new fits:                            0
new observed values:                 0
```
