---
title: Transformation Matrices
id: transformation-matrices
tags:
  - LinearAlgebra
  - Geometry
  - Matrices
date: 2026-05-27
references: []
---
If we have an object in Euclidean space $\mathbb{R}^n$, we often want to be able to transform it: translate, rotate, reflect, scale, and sometimes all at once!

All of these operations are available to us in Euclidean spaces $\mathbb{R}^n$. The only exception is that rotation is not available on a line — but that is a minor detail.

All of the transformations listed above belong to the group of so-called affine transformations. In general form, an affine transformation $f: \mathbb{R}^n \to \mathbb{R}^n$ is a transformation that preserves the relationships between any two lines. That is, if lines were parallel, they will remain so after we apply our transformation to them. The same holds for intersecting and skew lines.

In practice, it is convenient to work with affine transformations using algebraic notation. Let $x \in \mathbb{R}^n$; then any affine transformation has the form:
$$ f(x) = A x + b$$
where $A \in \mathrm{GL}(n, \mathbb{R})$ — this denotes the set of invertible matrices — and $b$ is an ordinary vector from $\mathbb{R}^n$.

Now let us look at how the simplest transformations can be represented in algebraic form. We begin with 2D space:

|                   $f$                   |                                      $A$                                       |  $b$  |                Example                |
| :-------------------------------------: | :----------------------------------------------------------------------------: | :---: | :----------------------------------: |
|       Translation by vector $b_0$       |               $\begin{pmatrix}  1 & 0 \\  0 & 1  \end{pmatrix}$                | $b_0$ | ![[Pasted image 20260527185502.png]] |
|         Rotation by angle $\phi$          | $\begin{pmatrix}  \cos\phi & -\sin\phi \\  \sin\phi & \cos\phi  \end{pmatrix}$ |  $0$  | ![[Pasted image 20260527185532.png]] |
|     Reflection about the $x$-axis      |               $\begin{pmatrix}  1 & 0 \\  0 & -1  \end{pmatrix}$               |  $0$  | ![[Pasted image 20260527185615.png]] |
| Scaling by $\lambda_x$ and $\lambda_y$ |       $\begin{pmatrix}  \lambda_x & 0 \\  0 & \lambda_y  \end{pmatrix}$        |  $0$  | ![[Pasted image 20260527185635.png]] |

When moving to higher-dimensional spaces, all transformations extend in a natural way — by adding new components. What about rotation? It is known that in Euclidean spaces of any dimension, rotations occur in a plane (a subspace of dimension 2), and the rotation matrix $A$ by angle $\phi$ in the plane $x_i, x_j$ is obtained from the identity matrix by replacing the four elements at the intersection of the rows and columns with indices $i$ and $j$ with the rotation matrix block from the two-dimensional case:
$$\begin{pmatrix}  a_{ii} & a_{ij} \\  a_{ji} & a_{jj}  \end{pmatrix} \to \begin{pmatrix}  \cos\phi & -\sin\phi \\  \sin\phi & \cos\phi  \end{pmatrix}$$

The resulting rotation matrix then takes the form:

$$  
A=  
\begin{pmatrix}  
1 & &  & &  & & 0 \\  
& \ddots & & & & & \\  
& & \cos\phi & \cdots & -\sin\phi & & \\  
& & \vdots & \ddots & \vdots & & \\  
& & \sin\phi & \cdots & \cos\phi & & \\  
& & & & & \ddots & \\  
0 & & & & & & 1  
\end{pmatrix}  
$$