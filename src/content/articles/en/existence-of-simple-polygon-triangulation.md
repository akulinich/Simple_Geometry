---
title: Existence of Simple Polygon Triangulation
id: existence-of-simple-polygon-triangulation
tags:
  - ComputationalGeometry
date: 2026-04-25
references:
  - Computational Geometry. Mark de Berg
---
One of the fundamental operations in computational geometry performed on polygons is triangulation. We will consider simple polygons. The boundary of such polygons is a closed polyline.

But does a triangulation always exist? Always. The proof of this fact is constructive. We will add diagonals to the polygon one by one.

Take a simple polygon $P$ with $n$ vertices. Fix some direction in the plane $\vec{v}$. Choose the extreme vertex $A$ of the polygon in this direction. Denote the neighbors of this vertex as $B$ and $C$. Try to draw a diagonal between $B$ and $C$. There are two cases: either the new diagonal does not intersect the boundary of the polygon (points $B$ and $C$ are not counted), or it does.

In the first case, the diagonal splits the polygon into a triangle and a polygon with $n-1$ vertices, for which we can repeat the algorithm iteration.

In the second case, at least one vertex of polygon $P$ other than $A$, $B$, and $C$ lies inside $\triangle ABC$. There may be more than one. Among them, take the farthest vertex along direction $\vec{v}$, call it $D$, and instead of diagonal $BC$ add diagonal $AD$. This diagonal cannot intersect other parts of polygon $P$, as that would contradict how we chose $D$. Once diagonal $AD$ is constructed, it splits polygon $P$ into two smaller polygons, since any diagonal splits a polygon into two parts. Repeating the algorithm for each of them, after a finite number of iterations we will have split $P$ into triangles.

![[Pasted image 20260425171834.png]]