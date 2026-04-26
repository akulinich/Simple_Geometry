---
title: Segment and Circle in Topology
id: segment-and-circle-in-topology
tags:
  - Topology
date: 2026-04-25
references:
  - Computational Topology. Edelsbrunner
---

Topology loves studying continuous maps from the unit interval into the space under investigation. For example, we can map the interval $[0, 1]$ into the plane $\mathbb{R}^2$. The result is a path in the plane with a starting point and an endpoint.

![[topology_path.png]]
If the starting point coincides with the endpoint, we get a loop!
![[topology_closed_path.png]]

Two paths are said to be similar if one can be transformed into the other by a bijective continuous map whose inverse is also continuous.
![[homeomorphism.png]]

A loop can also be viewed from a different angle. Instead of thinking of it as a map from an interval into our space, we can think of it as a map from the circle $S^1$.

Now, a path whose endpoints do not coincide and a loop are not similar!

I recently found what seems to me a very intuitive proof.

Assume the opposite. Then we can continuously transform the circle into the interval. Now let us remove one of the interior points of the interval and its preimage on the circle. The circle with one point removed is connected, but the interval splits into two parts! It is problematic when a continuous map sends a connected set to a disconnected one. We arrive at a contradiction.

![[circle_and_segment_topology.png]]