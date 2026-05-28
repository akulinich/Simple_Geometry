---
title: Transformation Matrices in Homogeneous Coordinates
id: transformation-matrices-homogeneous-coordinates
tags:
  - LinearAlgebra
  - Matrices
date: 2026-05-27
references: []
---
In the article [[transformation-matrices|transformation matrices]] we discussed the basic plane transformations, such as rotations, reflections, scalings, and translations. All of them are affine transformations, i.e., they have the form:
$$ f(x) = A x + b$$
where $A \in \mathrm{GL}(n, \mathbb{R})$ is an invertible matrix, and $x$ and $b$ are ordinary vectors in $\mathbb{R}^n$.

It turns out that for rotations, reflections, and scalings the term $b$ is always zero, whereas for translations, conversely, the matrix $A$ is the identity matrix. As a result, the term $b$ somewhat breaks the pattern. This is inconvenient.

There is a trick to write translation as a matrix. Note that when we multiply a matrix by a column vector, we get a vector in which each component is a sum of products of the coordinates:
$$
A x=
\begin{pmatrix}  
a_{11} & a_{12} \\  
a_{21} & a_{22}  
\end{pmatrix}
\begin{pmatrix}  
x_{1}  \\  
x_{2} 
\end{pmatrix}
=
\begin{pmatrix}  
a_{11}x_{1} + a_{12}x_2  \\  
a_{21}x_{1} + a_{22}x_2 
\end{pmatrix}
$$
What do we want? We want to add the vector $b$ to the result:
$$
\begin{pmatrix}  
a_{11}x_{1} + a_{12}x_2  \\  
a_{21}x_{1} + a_{22}x_2 
\end{pmatrix}
+ b
= 
\begin{pmatrix}  
a_{11}x_{1} + a_{12}x_2 + b_1  \\  
a_{21}x_{1} + a_{22}x_2 + b_2 
\end{pmatrix}
$$
This expression resembles matrix multiplication if we imagine that matrix $A$ has three columns and vector $x$ has three components, where $x_3 = 1$:

$$
A x + b =
\begin{pmatrix}  
a_{11} & a_{12} & b_1 \\  
a_{21} & a_{22} & b_2 
\end{pmatrix}
\begin{pmatrix}  
x_{1}  \\  
x_{2}  \\
1
\end{pmatrix}
$$

We have written translation as a matrix! But is everything fine? Unfortunately, the resulting matrix maps vectors from $\mathbb{R}^3$ to $\mathbb{R}^2$. This is inconvenient, because if we want to apply several transformations in sequence, we would constantly have to append the third component of vector $x$ as a separate step. Fortunately, this is easily fixed by adding to matrix $A$ not just a third column, but also a third row:
$$
\hat A = \begin{pmatrix}  
a_{11} & a_{12} & b_1 \\  
a_{21} & a_{22} & b_2 \\
0 & 0 & 1
\end{pmatrix}, \,
\hat x =
\begin{pmatrix}  
x_{1}  \\  
x_{2}  \\
1
\end{pmatrix}
$$

Thus, we have expressed affine transformations in a form where all computations reduce to a single matrix-vector multiplication:
$$ f(\hat x) = \hat A \hat x$$
Let us note once more: in order to work with affine transformations in this form, we need to move to a coordinate system with one additional dimension. Such a system is called a homogeneous coordinate system.

A note on the name. When speaking of homogeneous coordinates, one usually means a space where points of the form $(x, y, w)$ are identified with $(\tfrac{x}{w}, \tfrac{y}{w}, 1)$. In our case, such 'homogeneity' is not used, and this notation takes its name from its resemblance to genuine homogeneous coordinates.