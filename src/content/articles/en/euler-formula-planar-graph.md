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
A graph is planar if it can be drawn on the plane such that different vertices of the graph are different points of the plane, and edges are curves that do not intersect. In this case, we say that an embedding of the graph in the plane $\mathbb{R}^2$ exists.

The picture below shows two embeddings of the same graph in the plane. On the left, no pair of edges intersects, while on the right the diagonals cross. But a single valid embedding is enough to declare a graph planar. So the complete graph on 4 vertices is planar.
![[Pasted image 20260526213414.png]]

When we have a planar graph embedded in the plane, it creates a subdivision of the plane. This subdivision consists of three basic elements: vertices, edges, and faces (including the outer face). Let $v$ denote the number of vertices, $e$ the number of edges, and $f$ the number of faces. It turns out there is a rigid relationship between these three quantities, called Euler's formula.
$$v + f - e = 2$$
In the general case, the relationship also depends on the number of connected components of the graph, but we will only consider connected graphs going forward.

A note on the order of terms. I prefer to write vertices and faces first, then subtract edges. Vertices and faces are similar: they connect to their neighbors via edges. Edges themselves are the connecting objects. You can learn more about this by reading about dual graphs.

To show that the formula holds, take a spanning tree of our graph (this is a tree obtained by removing edges one by one until the next removal would disconnect the graph). Note that for a tree the formula is obvious. There is always one face, the number of vertices is $v$, and the number of edges is $v - 1$. We get $v + 1 - (v - 1) = 2$. Then we add the edges back one by one. Each time we add an edge, we gain an additional face (see the animation below). Thus, Euler's formula for a planar graph is proved by induction.

![[euler_big.gif]]