# CBF.T72 q79 eta9 physical midpoint three-evaluation frame theorem

## Status

`CLOSED_CHARACTERISTIC_ZERO_PHYSICAL_THREE_EVALUATION_PROJECTIVE_RANK122_WITH_POSITIVE_WIDTH_OPERATOR_PANELS`

CBF.T71 found a rank-122 three-evaluation frame over the selected residue
field. Its rows were algebraic probes, not points on the characteristic-zero
physical path. T72 performs that missing promotion on the exact selected G3AJ
member.

## 1. Selected physical rows

Use the first three consecutive rectangle-edge midpoints on the declared
counterclockwise q79 path:

```text
edge-0 at s=1/2,
edge-1 at s=1/2,
edge-2 at s=1/2.
```

Their Fermat coordinates are reconstructed from the exact path formula and
overlap the three independently certified H4-T152 Arb packets. Each midpoint
packet has a degree-198 saturated ramification polynomial with 198 pairwise
disjoint roots. The determinant of the three Fermat weight rows has certified
absolute lower bound

```text
0.3289986911530479938470980167... > 0.
```

Thus these are three independent characteristic-zero evaluation rows from the
actual physical path. They are not fitted probes or newly selected knobs.

## 2. Characteristic-zero graph tangent

The H4 characteristic-zero compiler reconstructs the exact 168 by 249 graph
incidence operator of the selected member. Its imported algebraization theorem
gives

```text
incidence rank                 126,
affine graph-tangent rank      123,
radial member line rank          1,
projective graph-tangent rank  122.
```

T72 binds a 126 by 126 incidence pivot whose Arb determinant excludes zero,
then solves the pivot block to obtain a 249 by 123 graph-kernel frame. Applying
each physical evaluation and quotienting its 83-coordinate fiber value by the
evaluated member relation gives three 82-row maps. Their joined map is

```text
246 by 123.
```

The exact radial member line is killed by all three quotient maps. Hence the
joined image has rank at most 122. A fixed 122 by 122 minor on a complementary
gauge has certified determinant absolute lower bound

```text
1.859060527587799e15 > 0.
```

It therefore has rank at least 122. The characteristic-zero projective image
rank is exactly 122 and its projective kernel is zero.

## 3. Positive-width stability

The calculation is not confined to three isolated points. Independently vary
the three edge parameters in the Cartesian product

```text
|s_i-1/2| <= 2^-32,  i=0,1,2.
```

The same fiber-relation pivots remain nonzero, the three Fermat rows remain
independent, and the same 122 by 122 minor remains invertible. For the fixed
midpoint preconditioner `R`, exact interval arithmetic gives

```text
||I-R M(s_0,s_1,s_2)||_infinity <= 0.198228356616... < 1.
```

The Neumann lemma proves invertibility throughout the complete product panel.
The width is a conservative certificate radius chosen for interval stability;
it is neither an observed input nor a physical parameter.

## 4. Theorem

**Physical Three-Evaluation Observability Theorem.** For the exact selected
characteristic-zero G3AJ member, coefficient-evaluation quotients at the
physical `edge-0`, `edge-1` and `edge-2` midpoints jointly separate all 122
projective graph-preserving tangent directions. The same statement holds for
every triple in the declared positive-width product panel.

**Proof.** The rank-126 incidence pivot produces a rank-123 affine tangent
frame. The evaluated radial member is zero in every fiber quotient, giving the
upper bound 122. The certified nonzero center minor gives the matching lower
bound. On the interval product, the strict Neumann defect below one proves that
the same minor remains invertible. Therefore the image rank is exactly 122 at
the center and throughout the panel. QED.

## 5. What changed

The characteristic-zero promotion left open by T71 is now closed at the
coefficient-evaluation level:

```text
residue probes                         -> actual physical B-loop rows,
one isolated rank calculation          -> three positive-width operator panels,
finite-field projective observability  -> characteristic-zero rank 122.
```

This is not yet the global normal-function derivative. H4-T155 certifies the
complete 252-branch carrier on a much wider `edge-2` panel, so the T72
`edge-2` operator box lies inside a proved geometric branch panel. Equivalent
complete branch-panel certificates for `edge-0` and `edge-1` have not yet been
executed. H4-T158 supplies the adaptive marcher needed to construct them.

## 6. Boundary and next target

T72 does not claim:

```text
complete 252-branch panels on edge-0 or edge-1,
an overlapping cover of all six physical path segments,
Picard or Abel-Jacobi derivative rank 122,
rank-164 Gauss-Manin transport,
the 248-row BHT handle integral,
beta_C, U_eta9, HYM, SM or QG closure.
```

The next exact calculation is to certify complete selected-source branch
panels around the `edge-0` and `edge-1` rows. Once those rows live in the same
overlapping smooth transport atlas, their 82-row states can enter the rank-164
relative system and the 248-row BHT accumulation.

## 7. Reproduction

Ordinary machine-independent replay uses the committed compressed source:

```powershell
python build_q79_eta9_physical_midpoint_three_evaluation_frame.py
python verify_q79_eta9_physical_midpoint_three_evaluation_frame.py
python -m unittest tests.test_q79_eta9_physical_midpoint_three_evaluation_frame -q
```

The optional provenance compiler
`export_q79_eta9_physical_char0_graph_operator.py` regenerates that source from
the declared clean H4 and UST commits. No observed value or fitted continuous
or discrete parameter is used.
