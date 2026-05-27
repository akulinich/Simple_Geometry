---
title: Euler's Formula for Planar Graphs
id: euler-formula-planar-graph
tags:
  - ComputationalGeometry
  - graphs
date: 2026-05-25
references:
  - Computational Topology. Edelsbrunner
---
A graph is planar if it can be drawn on a plane such that all vertices map to distinct points, and edges map to non-intersecting paths.

One also says that the graph has an embedding in the plane. An embedding is a mapping $h: (V, E) \to \mathbb{R}^2$ where $\forall\, v, u \in V \colon u \neq v \implies f(u) \neq f(v)$, and edges map to paths that do not intersect, i.e. $h(e_1) \cap h(e_2) = \varnothing$, where $e_1,e_2$ are edges, with the vertices themselves not included in the edges.

In the picture below, the left shows a planar graph, and the right shows a non-planar one, since two edges intersect.
![[Pasted image 20260526213414.png]]

When we have a planar graph embedded in the plane, it creates a partition of the plane. Each partition consists of three basic elements: vertices, edges, and faces (including the outer face). Let $v$ denote the number of vertices, $e$ the number of edges, and $f$ the number of faces. It turns out there is a rigid relation among these three quantities, known as Euler's Formula.

**Euler's Formula** — $v + f - e = 2$.

On the ordering of terms. I prefer to write vertices and faces first, then subtract edges, because vertices and faces are similar — both are connected by edges. Edges, on the other hand, are a distinct kind of object: they connect both vertices and faces. You can learn more about this by reading about dual graphs.

To show that the formula holds, take a spanning tree of our graph (a tree obtained by removing edges one at a time until removing the next edge would disconnect the graph into two parts). Note that for a tree the formula is obvious. There is always one face, the number of vertices is $v$, and the number of edges is $v - 1$. We get $v + 1 - (v - 1) = 2$. Then we add back edges one by one. Each time we add an edge, we gain one additional face (see the animation below). Thus, Euler's formula for a planar graph is proved by induction.

![[euler_big.gif]]