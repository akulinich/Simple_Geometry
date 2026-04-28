---
title: On Knot Invariants in Topology
id: knot-invariants-in-topology
tags:
  - Topology
  - Knots
date: 2026-04-27
references:
  - Computational Topology. Edelsbrunner
---
A knot in topology is a mapping from the circle $S^1$ into three-dimensional space $\mathbb{R}^3$ without self-intersections. The simplest knot is an ordinary circle. In everyday life one would not call such an object a knot, but in knot theory the circle is called the trivial knot.
![[cirle.png]]

The next knot, called the trefoil, is a genuine knot. Moreover, it cannot be untangled — it cannot be continuously deformed into a circle.
![[trefoil 1.png]]

How can we tell that a knot cannot be untangled? For this purpose topological invariants are used. Topological invariants are certain measurements that yield different values for different knots.

The simplest invariant is the ability to color a knot with three colors.

A few words are needed on what "coloring" means. We color not the knot itself but its projection onto a plane. This projection has a special feature. Wherever the knot crosses itself in the projection, there is a strand passing "underneath" and a strand passing "over the top." The strand that goes underneath is, so to speak, broken into two arcs. As a result, near each self-crossing we see three arcs: the upper arc of the knot and two lower arcs, one on each side of the upper arc. For the trefoil, for example, there are exactly three arcs in total. When we say "color" a knot, we mean assigning a color to each of its arcs.

![[trefoil_prjection_colored.png]]

Now let us return to the invariant. If one knot can be colored with three colors so that at every crossing all three arcs are the same color or all three arcs are different colors, while a second knot cannot be colored this way, then the two knots are distinct.

The circle has no three-coloring, since it has only one arc, whereas the trefoil does admit a three-coloring: it suffices to color all three arcs in different colors, as shown in the picture above.

The proof that three-colorability is an invariant is non-trivial. It can be studied by examining Reidemeister's theorem and the theorem on three-colorability of knots.