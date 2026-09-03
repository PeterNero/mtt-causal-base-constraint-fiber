# CBF.T70 q79 eta9 graph-tangent single-fiber rank theorem

## Status

`CLOSED_EXACT_SELECTED_RESIDUE_GRAPH_TANGENT_TO_FIXED_FIBER_RANK70_KERNEL52`

T70 computes how the complete graph-preserving eta9 coefficient family acts
on the selected Fermat-origin fiber. It uses the full UST.G3AK tangent space,
not only the earlier 33-direction principal slice.

## 1. Carriers

Over the selected residue field

```text
k=F_101[gamma]/(M),       [k:F_101]=6,
```

let `V=k^249` be the eta9 coefficient space and let

```text
I:V -> R
```

be the three-graph incidence map. UST.G3AK proves

```text
rank I=126,
rank ker I=123,
rank T_graph=rank(ker I/<F>)=122.
```

At the Fermat origin `e_0=[1:0:-1]`, evaluation sends the three elliptic
coefficient blocks to

```text
F_e0=A_0-A_2.
```

Quotienting the 83 K3 coefficient rows by `<F_e0>` gives the rank-82 fiber
coefficient carrier `V_9/<F_e0>` from H4-T133.

## 2. Exact computation

The builder reconstructs the hash-locked `168 x 249` G3AK incidence matrix
over `k` and independently replays its rank and pivot columns. It reconstructs
the selected member from UST.G3AD, verifies `I(F)=0`, and builds an explicit
82-row quotient map `Q_e0` that kills `F`.

Exact elimination gives

```text
rank I                  = 126,
rank Q_e0               =  82,
rank [I;Q_e0]           = 196.
```

Therefore the image of `Q_e0` on `ker I` has rank

```text
196-126=70.
```

Since the radial member lies in the kernel of this quotient, rank-nullity
gives

```text
affine invisible kernel       123-70=53,
projective invisible tangent   53-1=52,
fixed-fiber cokernel           82-70=12.
```

The independent verifier instead reconstructs the canonical 123-vector
kernel basis and evaluates those vectors directly. Its kernel hash agrees
with UST.G3AK and it obtains the same rank 70.

## 3. Principal-slice comparison

T70 also reconstructs the 33 directions `s_union H` from the exact selected
graph union. Their image on the same fiber has rank only 11. Hence the 89
additional graph-preserving directions found by UST.G3AK add

```text
70-11=59
```

new image dimensions modulo the principal image. This is an exact reason the
old 33-direction family could not represent the full local deformation
problem.

## 4. Theorem

**Graph-Tangent Single-Fiber Rank Theorem.** On the selected residue carrier,
restriction of the rank-122 projective graph-preserving coefficient tangent
to the Fermat-origin fiber quotient has rank 70, kernel rank 52 and cokernel
rank 12. The principal rank-33 slice has image rank 11, while its 89-direction
completion adds 59 new image dimensions.

**Proof.** The rank formula for a restriction to an incidence kernel is

```text
rank(Q_e0 | ker I)=rank([I;Q_e0])-rank(I).
```

The two exact elimination routes certify the displayed ranks. The member
itself is killed by both `I` and the fiber quotient, so removing its radial
line lowers the invisible affine kernel from 53 to 52. QED.

## 5. Interpretation and boundary

This is a coefficient-deformation theorem. It proves three useful facts:

1. the complete graph family controls 70 rather than 11 selected-fiber
   directions;
2. the graph constraints forbid 12 of the 82 possible first-order fiber
   coefficient directions;
3. one fixed fiber is blind to 52 projective graph-family directions.

It does **not** compute the derivative of the Picard point, the Abel-Jacobi
normal function, or the global 248-row BHT class. Those maps include moving
cycles, Gauss-Manin transport, period normalization and the B-handle sweep.
No rank statement here may be substituted for their derivative.

The immediate physical frontier remains the completed same-member BHT sweep
for `C_fr`. After it is decided, its 122-direction family derivative must
carry the rank-52 fiber-blind sector explicitly rather than silently dropping
it.

## 6. Reproduction

```powershell
python build_q79_eta9_graph_tangent_single_fiber_rank.py
python verify_q79_eta9_graph_tangent_single_fiber_rank.py
python -m unittest tests.test_q79_eta9_graph_tangent_single_fiber_rank -q
```

No observed value, fitted parameter or physical selector is introduced.
