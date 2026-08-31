# q79 B89 affine-Deligne logical audit

**Purpose:** fix the exact implication to be used after the same-source B89
isotopy campaign completes. This note audits H4-T90, H4-T120 and the drafted
H4-T126. It does not replace their theorem ownership and does not promote the
drafted branch decision.

## 1. Objects that must remain distinct

For the selected signed relative divisor

```text
D=(C intersect H0)-(C intersect Rminus),
```

let `nu_D=AJ(D)` be its normalized divisor normal function. The portable
A110-A121 authority defines `beta_C(B89)` as the oriented B-handle sweep of
this normal function modulo the integral period image. It is therefore a
member-level Deligne-Leray transgression, not the value of `nu_D` at every
point of the base.

On the selected B-loop, the relative homology extension is

```text
0 -> H1(C,Z)
  -> H1(C,|D|;Z)
  -> H0_tilde(|D|,Z)
  -> 0.
```

Choose a relative chain `lambda_0` with the fixed primitive boundary
`(1^18,-1^18)`. If continuation around the loop returns `lambda_1`, then

```text
n=lambda_1-lambda_0 in H1(C,Z).
```

Changing `lambda_0` by an absolute cycle `b` changes `n` by `(M-I)b`.
Consequently the intrinsic loop class is

```text
[n] in coker(M-I)=H1(S1,H1(C,Z)_M).
```

The connecting homomorphism for the displayed extension identifies `[n]`
with the restriction of the topological class of `nu_D` to this same loop.
This is the precise content needed from H4-T120.

## 2. The valid nonzero implication

Once the moving family, signed endpoints and integral marking are certified
to be the same source, the implication is

```text
[n] != 0
  => delta(nu_D)|B-loop != 0
  => beta_C(B89) != 0.
```

The second arrow uses the corpus definition of `beta_C(B89)` as this oriented
B-handle transgression. It does not infer that `nu_D(s)` is nonzero for every
base point `s`, nor does it inject a finite component group into a complex
period torus.

Thus a certified nonzero class rejects B89 from the beta-zero locus without a
248-coordinate period evaluation. This is a quotient obstruction, not a
numerical approximation.

## 3. The converse is deliberately unavailable

The vanishing of `[n]` only says that the topological affine torsor is
trivial on the loop. A normal function with trivial topological invariant can
still have a nonzero identity-component Abel-Jacobi value. Therefore

```text
[n]=0
```

does not prove `beta_C(B89)=0`. That branch would still require the normalized
period-image calculation and an explicit trivializing cochain.

This asymmetry is essential:

```text
nonzero affine class  -> exact rejection,
zero affine class     -> period calculation still required.
```

## 4. Finite witness implication

Suppose the exact same-source return data reduce modulo two to `M_bar` and
`n_bar`, and an emitted row `w` satisfies

```text
w(M_bar-I)=0,
w n_bar=1.
```

If `[n]` vanished integrally, then `n=(M-I)b` for some integral `b`. Reduction
modulo two would give `n_bar=(M_bar-I)b_bar`, contradicting the two witness
equalities. Hence the finite witness proves integral nonvanishing. It does not
by itself prove an exact order for `[n]`; nonvanishing is sufficient for the
rejection.

## 5. Remaining promotion gate

The existing finite obstruction matrix and witness are conditional inputs.
They promote only after all of the following are bound to one source:

1. the exact characteristic-zero moving branch family;
2. the complete 252-strand isotopy on the four selected edges;
3. the 36 signed boundary endpoints and their label continuation;
4. the common 288-strand joint isotopy;
5. the resulting rectangle word, integral action `M` and translation `n`.

The live T53 campaign addresses precisely these five rows. Until its result
packets, endpoint bindings and independent assemblers pass, B89 remains
undecided at the selected-source tier.

## 6. Mathematical context

The logical distinction between a normal function, its cohomological or
singularity invariant and its zero locus is standard in the primary
literature:

- Patrick Brosnan and Gregory Pearlstein, *Zero Loci of Admissible Normal
  Functions with Torsion Singularities*,
  https://arxiv.org/abs/0803.3365;
- Patrick Brosnan, Hao Fang, Zhaohu Nie and Gregory Pearlstein,
  *Singularities of Admissible Normal Functions*,
  https://arxiv.org/abs/0711.0964;
- Christian Schnell, *Complex-analytic Neron models for arbitrary families
  of intermediate Jacobians*, https://arxiv.org/abs/0910.0662.

These references support the general comparison. The identification of the
particular q79 signed divisor, loop and `beta_C` carrier remains an internal
same-source obligation and is not supplied by the external literature.
