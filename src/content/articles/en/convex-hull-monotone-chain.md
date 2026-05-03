---
title: Convex Hull. Monotone Chain Algorithm
id: convex-hull-monotone-chain
tags:
  - ComputationalGeometry
date: 2026-04-28
references:
  - Computational Geometry. Mark de Berg
---
In many problems, both in 3D and 2D, it is necessary to obtain a simplified representation of objects. Often, instead of the objects themselves — which can be quite complex — their convex hulls are used to compute object dimensions or detect collisions between objects.

In two-dimensional space, the convex hull of a finite set of points $S$ is the minimal convex polygon $P$ that contains $S$. Minimal in the sense that any other convex set containing $S$ also contains $P$.

![[ch_result.png]]

Computing the convex hull of a finite set of points is a classic problem in computational geometry, and many algorithms have been written for it. In this note, we will walk through the monotone chain algorithm.

The monotone chain algorithm operates on a finite set of points $S$. It is built using the sweep line method. We construct the convex hull by scanning all points of $S$ sorted by $x$-coordinate. We will denote the sorted set as $S_{\text{sorted}}$. In this note, we will not consider the cases where multiple points share the same $x$-coordinate, or where three points are collinear. We will discuss degenerate cases another time.

Before we begin, note that after sorting, the first and last points of our set are guaranteed to be part of the convex hull. This is proved by contradiction: if a point is not part of the convex hull, it is an interior point and lies inside the convex hull along with its neighborhood, which contradicts the fact that this point is extremal in the $x$-coordinate.

So by sorting the points, we have already found two vertices of the convex hull.

![[ch_min_max.png]]

Next, observe that to build the polygon, we need to construct its upper and lower parts independently. These are called the upper hull and the lower hull.

We are now ready to scan $S_{\text{sorted}}$. We will build the upper hull. To do this, in addition to the sorted points themselves, we need a stack, which we will call $\mathrm{CH}_{\text{top}}$. We start by pushing the first two points onto the stack. When considering the point at index $k$, we call the point itself $s_k$ and the two topmost points on the stack $p_k$ and $p_{k-1}$. There are two possible situations:

- The path $p_{k-1} \to p_{k} \to s_{k}$ makes a right turn
	- When building the upper hull, convexity is not violated by a right turn. We simply push $s_k$ onto the stack.
- The path $p_{k-1} \to p_{k} \to s_{k}$ makes a left turn
	- In this case, simply pushing $s_k$ onto the stack would make the upper hull non-convex. Moreover, if we look at the line passing through $p_{k-1}$ and $s_k$, the point $p_k$ lies below it, meaning it is interior to the upper hull. We pop $p_k$ from the stack and reconsider the point $s_k$. If after a series of pops only one point remains on the stack, we simply push $s_k$ onto the stack.

Right and left turns are determined by the sign of the cross product. The image below shows examples of left and right turns.
![[turns.png]]

The essence of the algorithm is that we scan the points and keep only those that produce a right turn when building the answer — and if, when traversing the polygon, we make only right turns, the polygon is convex.

After processing all of $S_{\text{sorted}}$, the upper hull is complete and stored in $\mathrm{CH}_{\text{top}}$. The lower hull $\mathrm{CH}_{\text{bottom}}$ is built analogously, but scanning from end to beginning in order to continue making right turns.

It remains to join the upper and lower hulls to obtain the result.

Nearly the entire algorithm is linear — each point enters and exits the stack at most once. So the overall complexity is dictated by the sort step: $O(n \, \log n)$.

A proof of correctness can be found, for example, in Mark de Berg's book "Computational Geometry".

Example of the algorithm in action:

![[ch_monotone_chain 2.gif]]