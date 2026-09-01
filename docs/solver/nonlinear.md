
# Xpress Nonlinear
## Reference manual


#### Release 47.01


#### __Last update 20 August, 2026__



(C) 1983-2026 Fair Isaac Corporation. All rights reserved. 
This documentation is the property of Fair Isaac Corporation ("FICO"). Receipt or possession of this documentation does not convey rights to disclose, reproduce, make derivative works, use, or allow others to use it except solely for internal evaluation purposes to determine whether to purchase a license to the software described in this documentation, or as otherwise set forth in a written software license agreement between you and FICO (or a FICO affiliate).  Use of this documentation and the software described in it must conform strictly to the foregoing permitted uses, and no other use is permitted.

The information in this documentation is subject to change without notice. If you find any problems in this documentation, please report them to us in writing. Neither FICO nor its affiliates warrant that this documentation is error-free, nor are there any other warranties with respect to the documentation except as may be provided in the license agreement. FICO and its affiliates specifically disclaim any warranties, express or implied, including, but not limited to, non-infringement, merchantability and fitness for a particular purpose. Portions of this documentation and the software described in it may contain copyright of various authors and may be licensed under certain third-party licenses identified in the software, documentation, or both.

In no event shall FICO or its affiliates be liable to any person for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this documentation or the software described in it, even if FICO or its affiliates have been advised of the possibility of such damage. FICO and its affiliates have no obligation to provide maintenance, support, updates, enhancements, or modifications except as required to licensed users under a license agreement.

FICO is a registered trademark of Fair Isaac Corporation in the United States and may be a registered trademark of Fair Isaac Corporation in other countries. Other product and company names herein may be trademarks of their respective owners.

Patent(s): [www.fico.com/en/patents](https://www.fico.com/en/patents})

Xpress Nonlinear 47.01 (FICO® Xpress 9.9)

Deliverable Version: A

Last Revised: 20 August, 2026


## Part A Overview


### Chapter 1 Introduction


This part of the manual is intended to provide a general description of the facilities available for modeling with Xpress NonLinear. It is not an exhaustive list of possibilities, and it does not go into very great depth on some of the more advanced topics. All the functions and formats are given in more detail in the second part of this manual and the Xpress-Mosel Reference Manual \(Module mmxnlp section\).

Xpress Nonlinear consists of:

 * the Xpress Optimizer to solve linear, mixed integer linear, and convex quadratic problems,
 * Xpress-SLP which uses Successive Linear Programming to solve non-linear models, and
 * Artelys Knitro, which is used as a plugin to solve highly nonlinear models.

Note that FICO Xpress Nonlinear is different from FICO Xpress Global, whose documentation can be found in the [Global Solver User Guide](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/). FICO Xpress Nonlinear targets finding locally optimal solutions for nonconvex problems. FICO Xpress Global finds globally optimal solutions for nonconvex problems \(which might be orders of magnitude harder\). For convex problems, both will find globally optimal solutions. It cannot be easily determined a priori which of the two solvers will be superior in performance, since both tackle the same problem with rather different approaches. Note that if both solvers are licensed, Xpress will by default call the global solver, unless user functions are present. For a particular convex problem, it is worth checking both independently.

The functionalities of Xpress Nonlinear extend those of the Xpress Optimizer. Almost any problem that fits into the problem types supported by the Xpress Optimizer are automatically detected and converted into the appropriate format to take advantage of the power of the optimizer's purpose written algorithms.

Xpress-SLP is in essence, a technique which involves making a linear approximation of the original problem at a chosen point, solving the linear approximation and seeing how "far away" the solution point is from the original chosen point. If it is "sufficiently close" then the solution is said to have converged and the process stops. Otherwise, a new point is chosen, based on the solution, and a new linear approximation is made. This process repeats \(iterates\) until the solution converges. Although this process will find a solution which is the optimum for the linear approximation, there is no guarantee that the solution will be the optimum for the original non-linear problem \(that is to say: it may not be the best possible solution to the original problem\). Such a solution is called a "local optimum", because it is a better solution than any others in the immediate neighborhood, but may not be better than one a long way away.

The problem of local optima can be thought of as being like trying to find the deepest valley in a range of mountains. You can find a valley relatively easily \(just keep going downhill\). However, when you reach it, you have no idea whether there is a deeper valley somewhere else, because the mountains block your view. You have found a local optimum, but you do not know whether it is a global optimum. Indeed, in general, finding a global optimum requires a rigorous search.

While Xpress-SLP is most powerful for large or integer nonlinear problems, Knitro which can take advantage of using second order partial derivative information can be more beneficial for highly nonlinear models.

#### Section 1.1 Mathematical programs


There are many specialised forms of models in mathematical programming, and if such a form can be identified, there are usually much more efficient solution techniques available. This section describes some of the major types of problem that Xpress Nonlinear can identify automatically.

##### Linear programs


Linear programming \(LP\) involves solving problems of the form

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _c<sup>T</sup>x_ | 
subject to | _Ax≤b_ | 
_

and in practice this encompasses, via transformations, any problem whose objective and constraints are linear functions.

Such problems were traditionally solved with the simplex method, although recently interior point methods have come to be favoured for larger instances. Linear programs can be solved quickly, and solution techniques scale to enormous sizes of the matrix _A_ . However, few applications are genuinely linear. It was common in the past, however, to approximate general functions by linear counterparts when LPs were the only class of problem with efficient solution techniques.

##### Convex quadratic programs


Convex quadratic programming \(QP\) involves solving problems of the form

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _c<sup>T</sup>x + x<sup>T</sup>Q x_ | 
subject to | _Ax≤b_ | 
_

for which the matrix _Q_  is symmetric and positive semi-definite \(that is, _x<sup>T</sup>Q x≥0_  for all _x_ \). This encompasses, via transformations, all problems with a positive semi-definite _Q_  and linear constraints. Such problems can be solved efficiently by interior point methods, and also by quadratic variants of the simplex method.

##### Convex quadratically constrained quadratic programs


Convex quadratically constrained quadratic programming \(QCQP\) involves solving problems of the form

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _c<sup>T</sup>x + x<sup>T</sup>Q x_ | 
subject to | _Ax≤b_ | 
|  | _q<sub>j</sub><sup>T</sup>x + x<sup>T</sup>P<sub>j</sub>x≤d<sub>j</sub>_ , _∀j_ | 
_

for which the matrix _Q_  and all matrices _P<sub>j</sub>_  are positive semi-definite. The most efficient solution techniques are based on interior point methods.

##### Second order conic problems


Second order conic problems is a special form of a convex quadratically constrained quadratic program, where although the quadratic matrix is not positive semi-definite, the feasible range of the problem is convex, and there are specialized algorithm to solve them.

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _c<sup>T</sup>x + x<sup>T</sup>Q x_ | 
subject to | _Ax≤b_ | 
|  | _x_ is in _C<sub>j</sub>_ , _∀j_ | 
_

for which the matrix _C<sub>j</sub>_  is a convex second order cone and _Q_  is positive semi-definite. The standard form of a second order cone is _x<sup>T</sup>I x≤y\*y_  where _y_  is non-negative, or \(a rotated second order cone\) _x<sup>T</sup>I x≤y\*z_  where _y_  and _z_  are non-negative. Many quadratic problems can be formulated as a second order convex conic problem, including any convex quadratically constrained quadratic programs. Transformation happens automatically for most convertible problems.

##### General nonlinear optimization problems


Nonlinear programming \(NLP\) involves solving problems of the form

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _f(x)_ | 
subject to | _g<sub>j</sub>\(x\)≤b_ , _∀j_ | 
_

where _f(x)_  is an arbitrary function, and _g(x)_  are a set of arbitrary functions. This is the most general type of problem, and any constrained model can be realised in this form via simple transformations.

Until recently, few practical techniques existed for tackling such problems, but it is now possible to solve even large instances using Successive Linear Programming solvers \(SLP\) or second-order methods.

##### Mixed integer programs


Mixed-integer programming \(MIP\), in the most general case, involves solving problems of the form

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _f(x)_ | 
subject to | _g<sub>j</sub>\(x\)≤b_ , _∀j_ | 
|  | _x<sub>k</sub>_ integral | 
_

It can be combined with any of the previous problem types, giving Mixed-Integer Linear Programming \(MILP\), Mixed-Integer Quadratic Programming \(MIQP\), Mixed-Integer Quadratically Constrained Quadratic Programming \(MIQCQP\), Mixed-Integer Second Order Conic Problems \(MISOCP\) and Mixed-Integer Nonlinear Programming \(MINLP\). Efficient solution techniques now exist for all of these classes of problem.

#### Section 1.2 Technology Overview


In real-world applications, it is vital to match the right optimization technology to your problem. The FICO Xpress libraries provide dedicated, high performance implementations of optimization technologies for the many model classes commonly appearing in practical applications. This includes solvers for linear programming \(LP\), mixed integer programming \(MIP\), convex quadratic programming \(QP\), and convex quadratically constrained programming \(QCQP\), general nonlinear programming \(NLP\), and general mixed-integer nonlinear programming \(MINLP\).

##### The Simplex Method


The simplex method is one of the most well-developed and highly studied mathematical programming tools. The solvers in the FICO Xpress Optimizer are the product of over 30 years of research, and include high quality, competitive implementations of the primal and dual simplex methods for both linear and quadratic programs. A key advantage of the simplex method is that it can very quickly reoptimize a problem after it has been modified, which is an important step in solving mixed integer programs.

##### The Logarithmic Barrier Method


The interior point method of the FICO Xpress Optimizer is a state of the art implementation, with leading performance across a variety of large models. It is capable of solving not only the largest and most difficult linear and convex quadratic programs, but also convex quadratically constrained quadratic and second order conic programs. It includes optimized versions of both infeasible logarithmic barrier methods, and also homogeneous self-dual methods.

##### Outer approximation schemes


A drawback of the barrier methods is that they are not efficiently warm-started. This makes these methods unattractive for solving several related problems, like the ones arising from a branch and bound search. While for linear and convex quadratic problems the simplex methods can be used, there is no immediate such alternative for convex quadratic constrained and second order methods. To bridge the gap, outer approximation cutting schemes are used, which themselves may be warm started by a barrier solution.

##### Successive Linear Programming


For general nonlinear programs which are very large, highly structured, or contain a significant linear part, the FICO Xpress Sequential Linear Programming solver \(XSLP\) offers exceptional performance. Successive linear programming is a first order, iterative approach for solving nonlinear models. At each iteration, a linear approximation to the original problem is solved at the current point, and the distance of the result from the selected point is examined. When the two points are sufficiently close, the solution is said to have converged and the result is returned. This technique is thus based upon solving a sequence of linear programming problems and benefits from the advanced algorithmic and presolving techniques available for linear problems. This makes XSLP scalable, as well as efficient for large problems. In addition, the relatively simple core concepts make understanding the solution process and subsequent tuning comparatively straightforward.

##### Second Order Methods


Also integrated into the Xpress suite is Knitro from Artelys, a second-order method which is particularly suited to large-scale continuous problems containing high levels of nonlinearity. Second order methods approximate a problem by examining quadratic programs fitted to a local region. This can provide information about the curvature of the solution space to the solver, which first-order methods do not have. Advanced implementations of such methods, like Knitro, may as a result be able to produce more resilient solutions. This can be especially noticeable when the initial point is close to a local optimum.

##### Mixed Integer Solvers


The FICO Xpress MIP solver is a highly scalable parallel branch and bound framework for all classes of mixed integer programs. It is based on a branch and bound search utilizing continuous solvers, advanced cutting planes, in-tree presolving and multiple heuristics, for discovering primal solutions and tightening best bounds. The search is guided by advanced methods for selecting branching variables and estimating sub-tree sizes/efforts.

Mixed integer programming forms the basis of many important applications, and the implementation in the FICO Xpress Suite has proven itself in operation for some of the world's largest organizations. For mixed integer nonlinear problems \(MINLPs\), we offer [FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/) to solve convex and non-convex, continuous and mixed-integer, problems to proven global optimality. Furthermore, [FICO Xpress Nonlinear](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/nonlinear/HTML/) offers black-box optimization and some enhanced nonlinear features in a local solver context.

#### Section 1.3 API naming convention


Xpress Nonlinear has been developed as an extension to the XPRS library building on the SLP solver technology, which is reflected in the naming convention. All XPRS API functions are used the same way as normal to build the linear part of the problem, while the API functions prefixed with XSLP are used for all nonlinear aspects, independently of how the problem is solved afterwards \(convex quadratic problems by a dedicated solver or Knitro instead of SLP\). Some controls have both an XPRS and an XSLP counterpart, for example "XPRS\_PRESOLVE" and "XSLP\_PRESOLVE". In such cases, "XSLP\_PRESOLVE" refers to the nonlinear presolver \(even if another solver than SLP is used to solve the problem afterwards\) and "XPRS\_PRESOLVE" refers to problems that are not deemed as general nonlinear \(LP, MIP or convex quadratic\); in such cases, if SLP solves one of such problems as part of its iterative process, the XPRS control is respected for such sub-solves.

### Chapter 2 An example problem


#### Section 2.1 Problem Definition


The diameter of a two-dimensional shape is the greatest distance between any two of its points. For a circle, this definition corresponds to the normal meaning of "diameter". For a polygon \(with straight sides\), it is equivalent to the greatest distance between any two vertices.

What is the greatest area of a polygon with N sides and a diameter of 1?

#### Section 2.2 Problem Formulation


This formulation is one of two described by Prieto \[1\]. It is easy to visualize, and has advantages in later examples. The pentagon is about the smallest model which can reasonably be used– it is non-trivial but is still just about small enough to be written out in full.

![Polygon Example images/PolygonDiagram1.png](Graphic/images/PolygonDiagram1.png)

    
  **Figure 2.1:** Polygon Example 


One vertex \(the highest-numbered, _V<sub>N</sub>_ \) is chosen as the "base" point, and all the other vertices are measured from it, using _\(r,θ\)_  coordinates– that is, the distance \(" _r_  "\) is measured from the vertex, and the angle or bearing of the vertex \("θ "\) is measured from the X-axis.

We shall use _r<sub>i</sub>_  and _θ<sub>i</sub>_  as the coordinates of vertex _V<sub>i</sub>_ . Then simple geometry and trigonometry gives:

 * The area of the triangle _V<sub>N</sub>V<sub>i</sub>V<sub>j</sub>_ : _area\(V<sub>N</sub>V<sub>i</sub>V<sub>j</sub>\) =\(1\) / \(2\)·r<sub>i</sub>·r<sub>j</sub>· sin\(θ<sub>j</sub>-θ<sub>i</sub>\)_ 
 * The side _V<sub>i</sub>V<sub>j</sub>_  is given by: _\(V<sub>i</sub>V<sub>j</sub>\)<sup>2</sup>= r<sub>i</sub><sup>2</sup>+ r<sub>j</sub><sup>2</sup>- 2·r<sub>i</sub>·r<sub>j</sub>· cos\(θ<sub>j</sub>-θ<sub>i</sub>\)_ 
 * The total area of the polygon is: _∑<sub>i=2</sub><sup>N-1</sup> area\(V<sub>N</sub>V<sub>i</sub>V<sub>i-1</sub>\)_ 
 * The maximum diameter of 1 requires that all the sides of all the triangles are≤ 1– that is:
   *   _r<sub>i</sub>≤1 fori=1,...,N-1_ 
   *  and
   *   _V<sub>i</sub>V<sub>j</sub>≤1 fori=1,...,N-2, j=i+1,...,N-1_ 

We have assumed in the diagram  _Polygon Example_ and in the formulation thatθ<sub>i</sub>≤θ<sub>i+1</sub>– in other words, the vertices are in order anti-clockwise. In fact, this is not just an assumption, and we need to include these constraints as well.

In the diagram, we have assumed that the first angleθ<sub>1</sub> is≥ 0. This is not an additional restriction if we use the normal modeling convention that all variables are non-negative. We also assumed that the last vertex is still "above" the X-axis– that is,θ<sub>N-1</sub> is≤ 180° \(orπ radians\).

The requirement is therefore:



| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
**maximize** | _∑<sub>i=2</sub><sup>N-1</sup>\(r<sub>i</sub>·r<sub>i-1</sub>· sin\(θ<sub>i</sub>-θ<sub>i-1</sub>\)\)\*0.5_ | _(area of the polygon)_ | 
|  | 
**subject to:** | _r<sub>i</sub>≤1 fori=1,...,N-1_ | _\(distances betweem V<sub>N</sub> and other vertices\)_ | 
|  | _r<sub>i</sub><sup>2</sup>+ r<sub>j</sub><sup>2</sup>- 2·r<sub>i</sub>·r<sub>j</sub>· cos\(θ<sub>j</sub>-θ<sub>i</sub>\)≤1 fori=1,...,N-2, j=i+1,...,N-1_ | | 
|  |  | _(distances between other pairs of vertices)_ | 
|  | _θ<sub>1</sub>≥0_ | _(first bearing is non-negative)_ | 
|  | _θ<sub>i+1</sub>-θ<sub>i</sub>≥0 fori=1,...,N-2_ | _(bearings are in order)_ | 
|  | _θ<sub>N-1</sub>≤π_ | _(last vertex is above X-axis)_ | 


**Reference:** 

\(1\)F.J. Prieto. _Maximum area for unit-diameter polygon of N sides, first model and second model_\(Netlib AMPL programs _in_ftp://netlib.bell-labs.com/netlib/ampl/models\).

### Chapter 3 Modeling in Mosel


#### Section 3.1 Basic formulation


Nonlinear capabilities in Mosel are provided by the `mmxnlp`  module. Please refer to the module documentation for more details. This chapter provides a short introduction only. Note that Mosel modeling for FICO Xpress Nonlinear and [FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/) work exactly the same, s.t. you can easily switch between both solvers.

The model uses the Mosel module `mmxnlp`  which contains the extensions required for modeling general non-linear expressions. This automatically loads the _mmxprs_ module, so there is no need to include this explicitly as well.

```
model "Polygon"
uses "mmxnlp"
```


We can design the model to work for any number of sides, so one way to do this is to set the number of sides of the polygon as a parameter.

```
parameters
  N=5
end-parameters
```


The meanings of most of these declarations will become apparent as the modeling progresses.

```
declarations
  area: nlctr
  rho: array(1..N) of mpvar
  theta: array(1..N) of mpvar
  objdef: mpvar
  D: array(1..N,1..N) of nlctr
end-declarations
```


 * The distances are described as " `rho` ", to distinguish them from the default names for the rows in the generated matrix \(which are R1, R2, etc\).
 * The types `nlctr`  \(nonlinear constraint\) are defined by the `mmxnlp` module.

```
area := sum(i in 2..N-1) (rho(i) * rho(i-1) * sin(theta(i)-theta(i-1)))*0.5
```


This uses the normal Mosel sum function to calculate the area. Notice that the formula is written in essentially the same way as normal, including the use of the `sin` function. Because the argument to the function is not a constant, Mosel will not try to evaluate the function yet; instead, it will be evaluated as part of the optimization process.

`area` is a Mosel object of type `nlctr`.

```
objdef = area
objdef is_free
```


What we really want to do is to maximize `area`. However, although Xpress NonLinear is happy in principle with a non-linear objective function, the Xpress Optimizer is not, unless it is handled in a special way. Xpress NonLinear therefore imposes the requirement that the objective function itself must be linear. This is not really a restriction, because– as in this case– it is easy to reformulate a non-linear objective function as an apparently linear one. Simply replace the function by a new `mpvar` and then maximize the value of the `mpvar`. In general, because the objective could have a positive or negative value, we make the variable free, so that it can take any value. In this example, we say:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`objdef = area` | defining the variable `objdef`to be equal to the non-linear expression `area` | 
`objdef is_free` | defining `objdef`to be a free variable | 
`maximize(objdef)` | maximizing the linear objective | 

This is firstly setting the standard bounds on the variables `rho` and `theta`. To reduce problems with sides of zero length, we impose a minimum of 0.1 on `rho(i)` instead of the default minimum of zero.

```
forall (i in 1..N-1) do
  rho(i) >= 0.1
  rho(i) <= 1  
  setinitval(rho(i), 4*i*(N+1-i)/((N+1)^2))
  setinitval(theta(i), M_PI*i/N)
end-do
```


We also give Xpress NonLinear initial values by using the `setinitval`  procedure. The first argument is the name of the variable, and the second is the initial value to be used. The initial values for `theta` are divided equally between 0 andπ. The initial values for `rho` are designed to go from 0 \(when _i=0_  or _N_ \) to 1 \(when _i_  is about half way\) and back.

```
forall (i in 1..N-2, j in i+1..N-1) do
  D(i,j) := rho(i)^2 + rho(j)^2 - rho(i)*rho(j)*2*cos(theta(j)-theta(i)) <= 1
end-do
```


This is creating the constraints `D(i,j)` which constrain the other sides of the triangles to be≤ 1.

These constraints could be made anonymous– that is, the assignment to an object of type `nlctr` could be omitted– but then it would not be possible to report the values.

```
forall (i in 2..N-1) do
  theta(i) >= theta(i-1) + 0.01
end-do
```


These anonymous constraints put the values of the `theta` variables in non-decreasing order. To avoid problems with triangles which have zero angles, we make each bearing at least 0.01 greater than its predecessor.

This is the boundary condition on the bearing of the final vertex.

```
theta(N-1) <= M_PI
```


#### Section 3.2 Setting up and solving the problem



`loadprob(objdef)` 

This procedure loads the currently-defined non-linear problem into the Xpress NonLinear optimization framework. This includes any purely linear part. Where a constraint has a linear expression as its left or right hand side, that linear expression will be retained as linear relationships \(constant coefficients\) in the matrix. Thus, for example, in the anonymous constraint defining `objdef`, the `objdef` coefficient will be identified as a linear term and will appear as a separate item in the problem.


`maximise` 

Optimization is carried out with the `maximise`  or `minimise`  procedures. They can take a string parameter– for example `maxmimise("b")`– as described in the Xpress NonLinear and Xpress Optimizer reference manuals.

With the default settings of the parameters, you will see usually nothing from the optimizer. The following parameters affect what is produced:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`xnlp_verbose` | Normally set to false. If set to true, it produces standard Xpress NonLinear iteration logging. | 
`xprs_verbose` | Normally set to false. If set to true, then information from the optimizer will also be output. | 
`xslp_log` | Normally set to -1. If set to 0, limited information is output from the SLP iterations. Settings of 1 or greater produce progressively more information for each SLP iteration. | 
`xslp_slplog` | If xslp\_log is set to 0, this determines the frequency with which SLP progress is reported. The default is 10, which means that it prints every 10 SLP iterations. | 

#### Section 3.3 Looking at the results


Within Mosel, the values of the variables and named constraints can be obtained using the `getsol` , `getslack`  and similar functions. A simple report lists just the area and the positions of the vertices:

```
writeln("Area = ", getobjval)
forall (i in 1..N-1) do
  writeln("V", i, ": r=", getsol(rho(i)), " theta=", getsol(theta(i)))
end-do
```


This produces the following result for the case N=5:

```
Area = 0.657166
V1: r=0.616416 theta=0.703301
V2: r=1 theta=1.33111
V3: r=1 theta=1.96079
V4: r=0.620439 theta=2.58648
```


#### Section 3.4 User functions


If an analytic description of the model is not available, it is possible to use black box functions implemented either directly in Mosel or by any external application.

The area calculation of the example could be implemented in Mosel as

```
public function MoselArea(I: array(Indices: range, Types: set of string) of real): real
  returned := (sum (i in 2..N-1) (I(i,"rho")*I(i-1,"rho")*sin(I(i,"theta")-I(i-1,"theta")))) * 0.5
 end-function
```


The user function is linked to the model using a user function object

```
declarations
  AreaFunction : userfunc
 end-declarations
 AreaFunction := userfuncMosel("MoselArea")
```


The arguments, which can be any expression, are passed down using an array of expressions

```
declarations
  FunctionArg: array(RN,{"rho","theta"}) of nlctr
 end-declarations
 forall (i in 1..N) do
  FunctionArg(i, "rho")   := rho(i)
  FunctionArg(i, "theta") := theta(i)
 end-do
```


Once the user function is declared and the arguments built, the user function is added to the model using F:

```
Area := F(AreaFunction,FunctionArg)
```


The function arguments are copied at the point when the F function is used, any later changes to the arrays holding the arguments are ignored.

#### Section 3.5 Parallel evaluation of Mosel user functions


It is possible to use parallel evaluations of simple Mosel functions that return a single real value. These functions may take an arbitrary array of nlctr expressions as input. It is the modeler's responsibility to ensure that the user functions to be called in parallel are thread-safe \(i.e., they do not depend upon shared resources\). Assuming the name of the user function is `MyFunc`, the user function before enabling the parallel version is expected to be declared as `usefuncMosel('MyFunc')`.

In order for mmxnlp to be able to utilize parallel user function evaluations, the user function must be implemented as a public function in a Mosel package. Any initialization necessary to enable the evaluation of the user function should be performed as part of the package initialization \(which is the code in in the main body of the package\).

To enable parallel evaluations, a parallel enabled version of the user function needs to be generated using the mmxnlp procedure `generateUFparallel`, which takes two arguments: the compiled package .bim name implementing the user function and the name of the user function within the package. It is good practice to use a separate Mosel model to perform this generation, keeping it separate from the main model. Multiple generated parallel user functions may be used within a single model.

The generator will produce a single Mosel file, the Mosel package `MyFunc_master`. This package also includes the worker model which will be responsible for the user function evaluations and will be resident in memory during the execution. The package also implements the parallel version of the user function, called `MyFunc_parallel`.

After compiling and including the main package into your model, it is this function that should be used in the actual model as `userfuncMosel('MyFunc_parallel',XSLP_DELTAS)`. In most cases, no other modifications are necessary, as the parallel function will detect the number of threads in the system and will start that many worker threads automatically. These will be shut down when your model finishes. Each worker's initialization code is performed only once, at the time of its first execution.

It may be necessary to explicitly start the worker threads, either to control the number of threads used, or to pass specific parameter settings to the user function package. This can be done by the procedure `MyFunc_StartWorkers( ThreadCount : integer, UfPackageParameters : string )`. In case it is necessary to stop the workers, the procedure `MyFunc_StopWorkers` may be used.

In case the user functions are computationally very expensive, by modifying the connection string in the generated module it is possible to utilize distributed/cloud-based computation of the user functions.

The worker model will only be compiled into memory during execution, but may be modified as necessary within the main model. For debugging purposes, it may be practical to redirect the worker to a file.

### Chapter 4 The Xpress NonLinear API Functions


Instead of writing an extended MPS file and reading in the model from the file, it is possible to embed Xpress NonLinear directly into your application, and to create the problem, solve it and analyze the solution entirely by using the Xpress NonLinear API functions. This example uses the C header files and API calls. We shall assume you have some familiarity with the Xpress Optimizer API functions.

The structure of the model and the naming system will follow that used in the previous section, so you should read  first.

#### Section 4.1 Header files


The header file containing the Xpress NonLinear definitions is `xslp.h`. This must be included together with the Xpress Optimizer header `xprs.h`, where `xprs.h` must come first.

```
#include "xprs.h"
#include "xslp.h"
```


#### Section 4.2 Initialization


Xpress NonLinear and Xpress Optimizer both need to be initialized, and an empty problem created. All Xpress NonLinear functions return a code indicating whether the function completed successfully. A non-zero value indicates an error. For ease of reading, we have for the most part omitted the tests on the return codes, but a well-written program should always test the values.

```
XPRSprob mprob;
XSLPprob sprob;

if (ReturnValue=XPRSinit(NULL)) goto ErrorReturn;
if (ReturnValue=XSLPinit()) goto ErrorReturn;
if (ReturnValue=XPRScreateprob(&mprob)) goto ErrorReturn;
if (ReturnValue=XSLPcreateprob(&sprob, &mprob)) goto ErrorReturn;
```


#### Section 4.3 Callbacks


It is good practice to set up at least a message callback, so that any messages produced by the system appear on the screen or in a file. The `XSLPsetcbmessage`  function sets both the Xpress NonLinear and Xpress Optimizer callbacks, so that all messages appear in the same place.


`XSLPsetcbmessage(sprob, XSLPMessage, NULL);` 

```
void XPRS_CC XSLPMessage(XSLPprob my_prob, void *my_object, char *msg, int len,
       int msg_type)
{
  switch (msg_type) {
  case 4: /* error */
  case 3: /* warning */
  case 2: /* dialogue */
  case 1: /* information */
    printf("%s\n", msg);
    break;
  default: /* exiting */
    fflush(stdout);
    break;
  }
}
```


This is a simple callback routine, which prints any message to standard output.

#### Section 4.4 Creating the linear part of the problem


The linear part of the problem, and the definitions of the rows and columns of the problem are carried out using the normal Xpress Optimizer functions.

```
#define MAXROW 20
#define MAXCOL 20
#define MAXELT 50
  int nRow, nCol, nSide, nRowName, nColName;
  int Sin, Cos;
  char RowType[MAXROW];
  double RHS[MAXROW], OBJ[MAXCOL], Element[MAXELT];
  double Lower[MAXCOL], Upper[MAXCOL];
  int ColStart[MAXCOL+1], RowIndex[MAXELT];
  char RowNames[500], ColNames[500];
```


In this example, we have set the dimensions by using `#  define` statements, rather than working out the actual sizes required from the number of sides and then allocating the space dynamically.

```
  nSide = 5;
  nRowName = 0;
  nColName = 0;
```


By making the number of sides a variable \( `nSide`\) we can create other polygons by changing its value.

It is useful– at least while building a model– to be able to see what has been created. We will therefore create meaningful names for the rows and columns. `nRowName` and `nColName` count along the character buffers `RowNames` and `ColNames`.

```
  nRow = nSide-2 + (nSide-1)*(nSide-2)/2 + 1;
  nCol = (nSide-1)*2 + 2;
  for (i=0; i<nRow; i++) RHS[i] = 0;
```


The number of constraints is:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`nSide-2` | for the relationships between adjacent thetas. | 
`(nSide-1)*(nSide-2)/2` | for the distances between pairs of vertices. | 
`1` | for the `OBJEQ`non-linear "objective function". | 

The number of columns is:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`nSide-1` | for the thetas. | 
`nSide-1` | for the rhos. | 
`1` | for the `OBJX`objective function column. | 

We are using "C"-style numbering for rows and columns, so the counting starts from zero.

```
  nRow = 0;
  RowType[nRow++] = 'E'; /* OBJEQ */
  nRowName = nRowName + 1 + sprintf(&RowNames[nRowName], "OBJEQ");
  for (i=1; i<nSide-1; i++) {
    RowType[nRow++] = 'G'; /* T2T1 .. T4T3 */
    RHS[i] = 0.001;
    nRowName = nRowName + 1 + sprintf(&RowNames[nRowName], "T%dT%d", i+1, i);
  }
```


This sets the row type indicator for `OBJEQ` and the theta relationships, with a right hand side of 0.001. We also create row names in the `RowNames` buffer. Each name is terminated by a `NULL` character \(automatically placed there by the `sprintf` function\). `sprintf` returns the length of the string written, excluding the terminating `NULL` character.

```
  for (i=1; i<nSide-1; i++) {
    for (j=i+1; j<nSide; j++) {
      RowType[nRow] = 'L';
      RHS[nRow++] = 1.0;
      nRowName = nRowName + 1 + sprintf(&RowNames[nRowName], "V%dV%d", i, j);
    }
  }
```


This defines the L-type rows which constrain the distances between pairs of vertices. The right hand side is 1.0 \(the maximum value\) and the names are of the form `ViVj`.

```
  for (i=0; i<nCol; i++) {
    OBJ[i] = 0;        /* objective function */
    Lower[i] = 0;      /* lower bound normally zero */
    Upper[i] = XPRS_PLUSINFINITY; /* upper bound = infinity */
  }
```


This sets up the standard column data, with objective function entries of zero, and default bounds of zero to plus infinity. We shall change these for the individual items as required.

```
  nCol = 0;
  nElement = 0;
  ColStart[nCol] = nElement;
  OBJ[nCol] = 1.0;
  Lower[nCol++] = XPRS_MINUSINFINITY; /* free column */
  Element[nElement] = -1.0;
  RowIndex[nElement++] = 0;
  nColName = nColName + 1 + sprintf(&ColNames[nColName], "OBJX");
```


This starts the construction of the matrix elements. `nElement` counts through the `Element` and `RowIndex` arrays, `nCol` counts through the `ColStart`, `OBJ`, `Lower` and `Upper` arrays. The first column, `OBJX`, has the objective function value of +1 and a value of -1 in the `OBJEQ` row. It is also defined to be "free", by making its lower bound equal to minus infinity.

```
  iRow = 0
  for (i=1; i<nSide; i++) {
    nColName = nColName + 1 + sprintf(&ColNames[nColName], "THETA%d", i);
    ColStart[nCol++] = nElement;
    if (i < nSide-1) {
      Element[nElement] = -1;
      RowIndex[nElement++] = iRow+1;
    }
    if (i > 1) {
      Element[nElement] = 1;
      RowIndex[nElement++] = iRow;
    }
    iRow++;
  }
```


This creates the relationships between adjacent thetas. The tests on `i` are to deal with the first and last thetas which do not have relationships with both their predecessor and successor.

```
  Upper[nCol-1] = 3.1415926;
```


This sets the bound on the final theta to beπ. The column index is `nCol-1` because `nCol` has already been incremented.

```
  for (i=1; i<nSide; i++) {
    Lower[nCol] = 0.01;         /* lower bound */
    Upper[nCol] = 1;
    ColStart[nCol++] = nElement;
    nColName = nColName + 1 + sprintf(&ColNames[nColName], "RHO%d", i);
  }
  ColStart[nCol] = nElement;
```


The remaining columns– the rho variables– have only non-linear formulas and so they do not appear in the linear section except as empty columns. They are bounded between 0.01 and 1.0 but have no entries. The final entry in `ColStart` is one after the end of the last column.

```
  XPRSsetintcontrol(mprob, XPRS_MPSNAMELENGTH, 16);
```


If you are creating your own names– as we are here– then you need to make sure that Xpress Optimizer can handle both the names you have created and the names that will be created by Xpress NonLinear. Typically, Xpress NonLinear will create names which are three characters longer than the names you have used. If the longest name would be more than 8 characters, you should set the Xpress Optimizer name length to be larger– it comes in multiples of 8, so we have used 16 here. If you do not make the name length sufficiently large, then the `XPRSaddnames` function will return an error either here or during the Xpress NonLinear "construct" phase.

```
  XPRSloadlp(mprob, "Polygon", nCol, nRow, RowType, RHS, NULL,
    OBJ, ColStart, NULL, RowIndex, Element, Lower, Upper);
```


This actually loads the model into Xpress Optimizer. We are not using ranges or column element counts, which is why the two arguments are `NULL`.

```
  XPRSaddnames(mprob, 1, RowNames, 0, nRow-1);
  XPRSaddnames(mprob, 2, ColNames, 0, nCol-1);
```


The row and column names can now be added.

#### Section 4.5 Adding the non-linear part of the problem


Be warned– this section is complicated, but it is the most efficient way– from SLP's point of view– to input formulae. See the next section for a much easier \(but less efficient\) way of inputting the formulae directly.

```
#define MAXTOKEN 200
#define MAXFORM 20
...
  int Sin, Cos;
  FormulaStart[MAXFORM];
  Type[MAXTOKEN];
  double Value[MAXTOKEN];
```


The arrays for the non-linear part can often be re-used from the linear part. The new arrays are `FormulaStart` for the nonlinear formulas and `Type` and `Value` to hold the internal forms of the formulae.

```
  XSLPgetindex(sprob, XSLP_INTERNALFUNCNAMES, "SIN", &Sin);
  XSLPgetindex(sprob, XSLP_INTERNALFUNCNAMES, "COS", &Cos);
```


We will be using the Xpress NonLinear internal functions `SIN` and `COS`. The `XSLPgetindex` function finds the index of an Xpress NonLinear entity \(character variable, internal or user function\).

```
  nToken = 0;
  nForm = 0;
  RowIndex[nForm] = 0;
  FormulaStart[nForm++] = nToken;
```


For each nonlinear formula, the following information is required:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`RowIndex` | the index of the row. | 
`FormulaStart` | the beginning of the internal formula array for the nonlinear formula. | 

```
  for (i=1; i<nSide-1; i++) {
    Type[nToken] = XSLP_COL;
    Value[nToken++] = nSide+i+1;
    Type[nToken] = XSLP_COL;
    Value[nToken++] = nSide+i;
    Type[nToken] = XSLP_OP;
    Value[nToken++] = XSLP_MULTIPLY;
    Type[nToken] = XSLP_RB;
    Value[nToken++] = 0;
    Type[nToken] = XSLP_COL;
    Value[nToken++] = i+1;
    Type[nToken] = XSLP_COL;
    Value[nToken++] = i;
    Type[nToken] = XSLP_OP;
    Value[nToken++] = XSLP_MINUS;
    Type[nToken] = XSLP_IFUN;
    Value[nToken++] = Sin;
    Type[nToken] = XSLP_OP
    Value[nToken++] = XSLP_MULTIPLY;
    if (i>1) {
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_PLUS;
    }
  }
```


This looks very complicated, but it is really just rather large. We are using the "reverse Polish" or "parsed" form of the formula for area. The original formula, written in the normal way, would look like this:

 `RHO2 * RHO1 * SIN ( THETA2 - THETA1 ) + .......`

In reverse Polish notation, tokens are pushed onto the stack or popped from it. Typically, this means that a binary operation A x B is written as A B x \(push A, push B, pop A and B and push the result\). The first term of our area formula then becomes:

 `RHO2 RHO1 * ) THETA2 THETA1 - SIN *`

Notice that the right hand bracket appears as an explicit token. This allows the `SIN`function to identify where its argument list starts–and incidentally allows functions to have varying numbers of arguments.

Each token of the formula is written as two items– `Type` and `Value`.

 `Type`is an integer and is one of the defined types of token, as given in the `xslp.h`header file. `XSLP_CON` , for example, is a constant; `XSLP_COL` is a column.

 `Value`is a double precision value, and its meaning depends on the corresponding `Type`. For a `Type`of `XSLP_CON`, `Value`is the constant value; for `XSLP_COL`, `Value`is the column number; for `XSLP_OP` \(arithmetic operation\), `Value`is the operand number as defined in `xslp.h`; for a function \(type `XSLP_IFUN` for internal functions, `XSLP_FUN` for user functions\), `Value`is the function number.

A list of tokens for a formula is always terminated by a token of type `XSLP_EOF` .

The loop writes each term in order, and adds terms \(using the `XSLP_PLUS` operator\) after the first pass through the loop.

```
  for (i=1; i<nSide-1; i++) {
    for (j=i+1; j<nSide; j++) {
      RowIndex[nForm] = iRow++;
      FormulaStart[nForm++] = nToken;

      Type[nToken] = XSLP_COL;
      Value[nToken++] = nSide+i;
      Type[nToken] = XSLP_CON;
      Value[nToken++] = 2;
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_EXPONENT;
      Type[nToken] = XSLP_COL;
      Value[nToken++] = nSide+j;
      Type[nToken] = XSLP_CON;
      Value[nToken++] = 2;
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_PLUS;
      Type[nToken] = XSLP_CON;
      Value[nToken++] = 2;
      Type[nToken] = XSLP_COL;
      Value[nToken++] = nSide+i;
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_MULTIPLY;
      Type[nToken] = XSLP_COL;
      Value[nToken++] = nSide+j;
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_MULTIPLY;
      Type[nToken] = XSLP_RB;
      Value[nToken++] = 0;
      Type[nToken] = XSLP_COL;
      Value[nToken++] = j;
      Type[nToken] = XSLP_COL;
      Value[nToken++] = i;
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_MINUS;
      Type[nToken] = XSLP_IFUN;
      Value[nToken++] = Cos;
      Type[nToken] = XSLP_OP
      Value[nToken++] = XSLP_MULTIPLY;
      Type[nToken] = XSLP_OP;
      Value[nToken++] = XSLP_MINUS;
      Type[nToken] = XSLP_EOF;
      Value[nToken++] = 0;
    }
  }
```


This writes the formula for the distances between pairs of vertices. It follows the same principle as the previous formula, writing the formula in parsed form as:

 `RHOi 2 ^  RHOj 2 ^  + 2 RHOi * RHOj * ) THETAj THETAi - COS * -`


`XSLPloadformulass(sprob, nForm, RowIndex, FormulaStart, 1, Type, Value);` 

The `XSLPloadformulas`  is the most efficient way of loading non-linear formulas into a problem. There is an `XSLPaddformulas` function which is identical except that it does not delete any existing nonlinear formulas first. There is also an `XSLPchgformula`  function, which can be used to change individual nonlinear formulas one at a time. Because we are using internal parsed format, the "Parsed" flag in the argument list is set to 1.

#### Section 4.6 Adding the non-linear part of the problem using character formulae


Provided that all entities– in particular columns and user functions– have explicit and unique names, the non-linear part can be input by writing the formulae as character strings. This is not as efficient as using the `XSLPloadformulas()` function but is generally easier to understand.

```
/* Build up nonlinear formulas */
/* Allow space for largest formula - approx 50 characters per side for area */
  FormBuffer = (char *) malloc(50*nSide);
```


We shall be using large formulae, so we need a character buffer large enough to hold the largest formula we are using. The estimate here is 50 characters per side of the polygon for the area formula, which is the largest we are using.

```
/* Area */

  BufferPos = 0;
  for (i=1; i<nSide-1; i++) {
    if (i > 1) {
      BufferPos = BufferPos + sprintf(&FormBuffer[BufferPos], " + ");
    }
    BufferPos = BufferPos + sprintf(&FormBuffer[BufferPos], "RHO%d * RHO%d * 
                SIN ( THETA%d - THETA%d )", i+1, i, i+1, i);
  }
  XSLPchgformulatext(sprob, 0, nSide, FormBuffer);
```


The area formula is of the form:

 `(RHO2*RHO1*SIN(THETA2-THETA1) + RHO3*RHO2*SIN(THETA3-THETA2) + ... ) / 2`

The loop writes the product for each consecutive pair of vertices and also puts in the "+" sign after the first one.

The `XSLPchgformulatext` function is a variation of `XSLPchgformula` but uses a character string for the formula instead of passing it as arrays of tokens. The arguments to the function are:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`RowIndex` | the index of the row. | 
`FormBuffer` | the formula, written in character form. | 

In this case, `RowIndex` is zero.

```
/* Distances */ 
  for (i=1; i<nSide-1; i++) {
    for (j=i+1; j<nSide; j++) {
      sprintf(FormBuffer, "RHO%d ^ 2 + RHO%d ^ 2 - 2 * RHO%d * RHO%d * 
              COS ( THETA%d - THETA%d )", j, i, j, i, j, i);
      XSLPchgformulatext(sprob, iRow, FormBuffer);
      iRow++;
    }
```


This creates the formula for the distance between pairs of vertices and writes each into a new row.

Provided you have given names to any user functions in your program, you can use them in a formula in exactly the same way as `SIN` and `COS` have been used above.

#### Section 4.7 Checking the data


Xpress NonLinear includes the function `XSLPwriteprob` which writes out a non-linear problem in text form which can then be checked manually. Indeed, the problem can then be run using the XSLP console program, provided there are no user functions which refer back into your compiled program. In particular, this facility does allow small versions of a problem to be checked before moving on to the full size ones.


`XSLPwriteprob(sprob, "testmat", "");` 

The first argument is the Xpress NonLinear problem pointer; the second is the name of the matrix to be produced \(the suffix ".mat" will be added automatically\). The last argument allows various different types of output including "scrambled" names– that is, internally-generated names will be used rather than those you have provided. For checking purposes, this is obviously not a good idea.

#### Section 4.8 Solving and printing the solution



`XSLPmaxim(sprob, "");` 

The `XSLPmaxim`  and `XSLPminim`  functions perform a non-linear maximization or minimization on the current problem. The second argument can be used to pass flags as defined in the Xpress NonLinear Reference Manual.


`XPRSwriteprtsol(mprob);` 

The standard Xpress Optimizer solution print can be obtained by using the `XPRSwriteprtsol`  function. The row and column activities and dual values can be obtained using the `XPRSgetlpsol` function.

In addition, you can use the `XSLPgetvar`  function to obtain the values of SLP variables– that is, of variables which are in nonlinear formulas, or which have nonlinear formulas. If you are using cascading \(see the Xpress NonLinear reference manual for more details\) so that Xpress NonLinear recalculates the values of the dependent SLP variables at each SLP iteration, then the value from `XSLPgetvar` will be the recalculated value, whereas the value from `XPRSgetlpsol`  will be the value from the LP solution \(before recalculation\).

#### Section 4.9 Closing the program


The `XSLPdestroyprob`  function frees any system resources allocated by Xpress NonLinear for the specific problem. The problem pointer is then no longer valid. `XPRSdestroyprob`  performs a similar function for the underlying linear problem `mprob`. The `XSLPfree`  function frees any system resources allocated by Xpress NonLinear. You must then call `XPRSfree`  to perform a similar operation for the optimizer.

```
  XSLPdestroyprob(sprob);
  XPRSdestroyprob(mprob);
  XSLPfree();
  XPRSfree();
```


If these functions are not called, the program may appear to have worked and terminated correctly. However, in such a case there may be areas of memory which are not returned to the system when the program terminates and so repeated executions of the program will result in progressive loss of available memory to the system, which will manifest iself in poorer performance and could ultimately produce a system crash.

#### Section 4.10 Adding initial values


So far, Xpress NonLinear has started by using values which it estimates for itself. Because most of the variables are bounded, these initial values are fairly reasonable, and the model will solve. However, in general, you will need to provide initial values for at least some of the variables. Initial values are provided using the `XSLPsetinitval` function.

### Chapter 5 The Nonlinear Console Program


#### Section 5.1 The Console Nonlinear


The nonlinear `optimizer` is an extension to the FICO Xpress Optimizer interactive console.

The console for nonlinear is started from the command line using the following syntax:

```


C:\> optimizer [problem_name] [@filename]


```


##### The nonlinear console extensions


The nonlinear console is an extension of the Xpress optimizer console. The optimizer automatically switches to nonlinear mode if a nonlinear license is detected. All the optimizer console commands work the same way as in the normal optimizer console. The active working problem for those commands is the actual linearization after augmentation, and the linear part of the problem before augmentation.

Optimizer console commands with an extended effect:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`readprob` | Read in an MPS/MAT or LP file | 
`minim` | Minimize an LP, a MIP or an SLP problem | 
`maxim` | Maximize an LP, a MIP or an SLP problem | 
`lpoptimize` | Minimize or maximize a problem | 
`mipoptimize` | Solve the problem to MIP optimality | 
`writeprob` | Export the problem into file | 
`dumpcontrols` | Display controls which are at a non default value | 


The MPS file can be an extended MPS file containing a nonlinear model. The `lpoptimize`, `nlpoptimize`, `mipoptimize`, and `optimize` commands will call the right algorithm depending on the presence of nonlinearities. Note that if a license for Xpress Global is present, the global solver will be called by default. You need to pass the "-s" flag to `nlpoptimize`, or `optimize` to enforce a local solve. In general, all commands accept the same flags as the corresponding library function.

New commands:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`cascade` | Perform cascading | 
`cascadeorder` | Recalculate the cascading order | 
`construct` | Construct the augmented problem | 
`dumpattributes` | Display problem attributes | 
`reinitialize` | Reinitialize an augmented problem | 
`setcurrentiv` | Copy the current solution as initial value | 
`slp_save` | XSLPsave | 
`slp_scaling` | Display scaling statistics | 
`unconstruct` | Remove the augmentation | 
`validate` | Validate the current solution | 
`validatekkt` | Validate the kkt conditions for the current solution | 


In order to separate XSLP controls and attributes for the XPRS ones, all XSLP controls and attributes are pretagged as `XSLP_` or `SLP_`, for example `XSLP_ALGORITHM`.

##### Common features of the Xpress Optimizer and the Xpress Nonlinear Optimizer console


All features of the Xpress optimizer console program is supported. For a full description, please refer to the Xpress optimizer reference manual.

From the command line an initial problem name can be optionally specified together with an optional second argument specifying a text "script" file from which the console input will be read as if it had been typed interactively.

Note that the syntax example above shows the command as if it were input from the Windows Command Prompt\( i.e., it is prefixed with the command prompt string `C:\>`\). For Windows users Console XSLP can also be started by typing `xslp` into the "Run ..." dialog box in the Start menu.

The Console XSLP provides a quick and convenient interface for operating on a single problem loaded into XSLP. The Console XSLP problem contains the problem data as well as\( i\) control variables for handling and solving the problem and\( ii\) attributes of the problem and its solution information.

The Console SLP auto– completion feature is a useful way of reducing key strokes when issuing commands. To use the auto– completion feature, type the first part of an optimizer command name followed by the Tab key. For example, by typing " `CONST` " followed by the Tab key Console Xpress will complete to the " `CONSTRUCT` ". Note that once you have finished inputting the command name portion of your command line, Console Xpress can also auto– complete on file names. Note that the auto– completion of file names is case– sensitive.

Console XSLP also features integration with the operating system's shell commands. For example, by typing " `dir` "\( or " `ls` " under Unix\) you will directly run the operating system's directory listing command. Using the " `cd` " command will change the working directory, which will be indicated in the prompt string:

```


[xpress bin] cd \
[xpress C:\]


```


Finally, note that when the Console XSLP is first started it will attempt to read in an initialization file named `optimizer.ini` from the current working directory. This is an ASCII "script" file that may contain commands to be run at start up, which are intended to setup a customized default Console Xpress environment for the user\( e.g., defining custom controls settings on the Console Xpress problem\).

The Console XSLP interactive command line hosts a TCL script parser\( [http://www.tcl.tk](http://www.tcl.tk/)\). With TCL scripting the user can program flow control into their optimizer scripts. Also TCL scripting provides the user with programmatic access to a powerful suite of functionality in the TCL library. With scripting support the Console Xpress provides a high level of control and flexibility well beyond that which can be achieved by combining operating system batch files with simple piped script files. Indeed, with scripting support the Console XSLP is ideal for\( i\) early application development,\( ii\) tuning of model formulations and solving performance and\( iii\) analyzing difficulties and bugs in models.

Note that the TCL parser has been customized and simplified to handle intuitive access to the controls and attributes of the Optimizer and XSLP. The following example shows how to proceed with write and read access to the XSLP\_ALGROITHM control:

```


[xpress C:\] xslp_algorithm=166
[xpress C:\] xslp_algorithm
166


```


The following shows how this would usually be achieved using TCL syntax:

```


[xpress C:\] set xslp_algorithm 166
166
[xpress C:\] $miplog
166


```


For examples on how TCL can be used for scripting, tuning and testing models, please refer to the Xpress Optimizer reference manual.

Console XSLP users may interrupt the running of the commands\( e.g., `minim`\) by typing Ctrl– C. Once interrupted Console Xpress will return to its command prompt. If an optimization algorithm has been interrupted in this way, any solution process will stop at the first 'safe' place before returning to the prompt.

When Console XSLP is being run with script input then Ctrl– C will not return to the command prompt and the Console Xpress process will simply stop.

Lastly, note that "typing ahead" while the console is writing output to screen can cause Ctrl– C input to fail on some operating systems.

The XSLP console program can be used as a direct substitute for the Xpress Optimizer console program. The one exception is the fixed format MPS files, which is not supported by XSLP and thus neither by the XSLP console.

## Part B Advanced


### Chapter 6 Nonlinear Problems


Xpress NonLinear will solve nonlinear problems. In this context, a nonlinear problem is one in which there are nonlinear relationships between variables or where there are nonlinear terms in the objective function. There is no such thing as a nonlinear variable— all variables are effectively the same— but there are nonlinear constraints and formulae. A nonlinear _constraint_ contains terms which are not linear. A nonlinear _term_ is one which is not a constant and is not a variable with a constant coefficient. A nonlinear constraint can contain any number of nonlinear terms.

Xpress NonLinear will also solve linear problems— that is, if the problem presented to Xpress NonLinear does not contain any nonlinear terms, then Xpress NonLinear will still solve it, using the normal optimizer library.

The solution mechanism used by Xpress-SLP is _Successive_ \(or _Sequential_\) _Linear Programming_. This involves building a linear approximation to the original nonlinear problem, solving this approximation \(to an optimal solution\) and attempting to validate the result against the original problem. If the linear optimal solution is sufficiently close to a solution to the original problem, then the SLP is said to have _converged_, and the procedure stops. Otherwise, a new approximation is created and the process is repeated. Xpress-SLP has a number of features which help to create good approximations to the original problem and therefore help to produce a rapid solution.

When licensed, Xpress NonLinear may also utilize Knitro to solve nonlinear problems.

Note that although the solution is the result of an optimization of the linear approximation, there is no guarantee that it will be an optimal solution to the original nonlinear problem. It may be a local optimum— that is, it is a better solution than any points in its immediate neighborhood, but there is a better solution rather further away. However, a converged SLP solution will always be \(to within defined tolerances\) a self-consistent— and therefore practical— solution to the original problem.

#### Section 6.1 Coefficients and formulas


Later in this manual, it will be helpful to distinguish between nonlinear expressions written as coefficients and those written as formulas.

If _X_  is a variable, then in the nonlinear expression _X*f(Y)_ , _f(Y)_  is the _coefficient_ of _X_ .

If _f(X)_  appears in a nonlinear constraint, then _f(X)_  is a _nonlinear formula_ in the nonlinear constraint.

If _X*f(Y)_  appears in a nonlinear constraint, then the entity _X*f(Y)_  is a _term_ in the nonlinear constraint.

As this implies, a formula written as a variable multiplied by a coefficient can always be viewed as a term, but there are terms which cannot be viewed as variables multiplied by coefficients. For example, in the constraint

 _X - SIN(Y) = 0_ ,

 _SIN(Y)_ is a _formula_and cannot be written as a coefficient.

#### Section 6.2 SLP variables


A variable which appears in a nonlinear coefficient or formula is described as an _SLP variable_.

Normally, any variable which has a nonlinear coefficient will also be treated as an SLP variable. However, it is possible to set options so that variables which do not appear in nonlinear coefficients or formulas are not treated as SLP variables.

Any variable, whether it is related to a nonlinear formula or not, can be defined by the user as an SLP variable. This is most easily achieved by setting an initial value for the variable.

#### Section 6.3 Local and global optimality


A globally optimal solution is a feasible solution with the best objective value among all feasible solutions for an optimization problem. In contrast, a locally optimal solution only has the best objective value within a limited neighborhood surrounding it. It's important to note that better solutions may exist in different regions of the problem space. While for convex problems every local optimum is a global optimum, this is not the case for general nonlinear problems.

The FICO Xpress library offers solvers that provide global optima for both convex and nonconvex problems. The base offering includes solving linear, quadratic, and quadratically constrained problems, as well as their mixed-integer counterparts. To handle more general nonlinear problems, a license for [FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/) is required.

For black-box optimization or obtaining local optima with duals for continuous nonlinear problems, a license for [FICO Xpress Nonlinear](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/nonlinear/HTML/) is necessary. FICO Xpress Nonlinear can also be used as a heuristic for mixed-integer nonlinear problems. It's important to note that finding a local optimum is usually much faster than finding a global optimum, but using a local solver doesn't provide guarantees on the global quality of the solution and may encounter issues such as local infeasibilities.

Lastly, neither local nor global optima are typically unique. The solution returned by a solver depends on the control settings and, especially for non-convex problems, the initial values provided. A connected set of initial points that yield the same locally optimal solutions is referred to as a region of attraction. These regions are algorithm and setting dependent.

#### Section 6.4 Convexity


Convex problems have many desirable characteristics from the perspective of mathematical optimization. Perhaps the most significant of these is that should both the objective and the feasible region be convex, any local optimally solutions found are also known immediately to be globally optimal.

A constraint _f\(x\)≤0_  is convex if the matrix of second derivatives of _f_ , that is to say its Hessian, is positive semi-definite at every point at which it exists. This requirement can be understood geometrically as requiring every point on every line segment which connects two points satisfying the constraint to also satisfy the constraint. It follows trivially that linear functions always lead to convex constraints, and that a nonlinear equality constraint is never convex.


![Two convex functions on the left, and two non-convex functions on the right. images/convexnonconvexfunctions.png](Graphic/images/convexnonconvexfunctions.png)

    
  **Figure 6.1:** Two convex functions on the left, and two non-convex functions on the right. 



For regions, a similar property must hold. If any two points of the region can be connected by a line segment which lies fully in the region itself, the region is convex. This extension is straightforward when the the properties of convex functions are considered.


![A convex region on the left and a non-convex region on the right. images/convexnonconvexregion.png](Graphic/images/convexnonconvexregion.png)

    
  **Figure 6.2:** A convex region on the left and a non-convex region on the right. 



It is important to note that convexity is necessary for some solution techniques and not for others. In particular, some solvers require convexity of the constraints and objective function to hold only in the feasible region, whilst others may require convexity to hold across the entire space, including infeasible points. In the special case of quadratic and quadratically constrained programs, Xpress NonLinear seamlessly migrates problems to solvers whose convexity requirements match the convexity of the problem.

#### Section 6.5 Converged and practical solutions


In a strict mathematical sense, an algorithm is said to have converged if repeated iterations do not alter the coordinates of its solution significantly. A more practical view of convergence, as used in the nonlinear solvers of the Xpress suite, is to also consider the algorithm to have converged if repeated iterations have no significant effect on either the objective value or upon feasibility. This will be called extended convergence to distinguish it from the strict sense.

For some problems, a solver may visit points at which the local neighborhood is very complex, or even malformed due to numerical issues. In this situation, the best results may be obtained when convergence of some of the variables is forced. This leads to practical solutions, which are feasible and converged in most variables, but the remaining variables have had their convergence forced by the solver, for example by means of a trust region. Although these solutions are not locally optimal in a strict sense, they provide meaningful, useful results for difficult problems in practice.

#### Section 6.6 The duals of general, nonlinear program


The dual of a mathematical program plays a fundamental role in the theory of continuous optimization. Each variable in a problem has a corresponding partner in that problem's dual, and the values of those variables are called the reduced costs and dual multipliers \(shadow prices\). Xpress NonLinear makes estimates of these values available. These are normally defined in a similar way to the usual linear programming case, so that each value represents the rate of change of the objective when either increasing the corresponding primal variable or relaxing the corresponding primal constraint.

From an algorithmic perspective, one of the most important roles of the dual variables is to characterize local optimality. In this context, the dual multipliers and reduced costs are called Lagrange multipliers, and a solution with both primal and dual feasible variables satisfies the Karush-Kuhn-Tucker conditions. However, it is important to note that for general nonlinear problems, there exist situations in which there are no such multipliers. Geometrically, this means that the slope of the objective function is orthogonal to the linearization of the active constraints, but that their curvature still prevents any movement in the improving direction.

_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _y_ | 
subject to | _x<sup>2</sup>+ y<sup>2</sup>≤1_ | 
|  | _\(x-2\)<sup>2</sup>+ y<sup>2</sup>≤1_ | 
_
 _A problem admitting no dual values_

![A problem admitting no dual values images/dual.png](Graphic/images/dual.png)

    
  **Figure 6.3:** A problem admitting no dual values 



This problem has a single feasible solution at \(1,0\). Reduced costs and dual multipliers could never be meaningful indicators of optimality, and indeed are not well-defined for this problem. Intuitively, this arises because the feasible region lacks an interior, and the existence of an interior \(also referred to as the Slater condition\) is one of several alternative conditions which can be enforced to ensure that such situations do not occur. The other common condition for well-defined duals is that the gradients of the active constraints are linearly independent.

Problems without valid duals do not often arise in practice, but it is important to be aware of the possibility. Analytic detection of such issues is difficult, and they manifest instead in the form of unexpectedly large or otherwise implausible dual values.

### Chapter 7 Extended MPS file format


One method of inputting a problem to Xpress NonLinear is from a text file which is similar to the normal MPS format matrix file. The Xpress NonLinear file uses _free format_ MPS-style data. All the features of normal free-format MPS are supported. There are no changes to the sections except as indicated below.

Note: the use of free-format requires that no name in the matrix contains any leading or embedded spaces and that no name could be interpreted as a number. Therefore, the following names are invalid:
 * `B 02`: because it contains an embedded space;
 * `1E02`: because it could be interpreted as 100 \(the scientific or floating-point format number, 1.0E02\).


It is possible to use column and row names including mathematical operators. A variable name **a+b**  is valid. However, as an expression **a + b**  would be interpreted as the addition of variables **a**  and **b**  - note the spaces between the variable names - it is best practice to avoid such names when possible. SLP will produce a warning if such names are encountered in the MPS file.

#### Section 7.1 Formulae


One new feature of the Extended MPS format is the _formula_. A formula is written in much the same way as it would be in any programming language or spreadsheet. It is made up of \(for example\) constants, functions, the names of variables, and mathematical operators. The formula always starts with an equals sign, and each item \(or _token_\) is separated from its neighbors by one or more spaces.

Tokens may be one of the following:

 * A constant;
 * The name of a variable;
 * An arithmetic operator "+", "-", "\*", "/";
 * The exponentiation operator "\*\*" or "^ ";
 * An opening or closing bracket "\(" or "\)";
 * A comma "," separating a list of function arguments;
 * The name of a supported internal function such as LOG, SIN, EXP;
 * The name of a user-supplied function;
 * A colon ":" preceding the return argument indicator of a multi-valued function;
 * The name of a return argument from a multi-valued function.

The following are valid formulae:
 * `_= SIN ( A / B )_ `: `SIN` is a recognized internal function which takes one argument and returns one result \(the sin of its argument\).
 * `_= A ^ B_ `: `^` is the exponentiation symbol. Note that the _formula_ may have valid syntax but it still may not be possible to evaluate it \(for example if _A = -1_  and _B = 0.5_ \).
 * `_= MyFunc1 ( C1 , - C2 , C3 : 1 )_ `: `MyFunc1` must be a function which can take three arguments and which returns an array of results. This formula is asking for the first item in the array.


The following are not valid formulae:
 * `_SIN ( A )_ `: Missing the equals sign at the start
 * `_=SIN(A)_ `: No spaces between adjacent tokens
 * `_= A * * B_ `: "\*\*" is exponentiation, "\*  \*" \(with an embedded space\) is not a recognized operation.
 * `_= MyFunc1 ( C1 , - C2 , C3 , 1 )_ `: If `MyFunc1` is as shown in the previous set of examples, it returns an array of results. The last argument to the function must be delimited by a colon, not a comma, and is the name or number of the item to be returned as the value of the function.
 * `__ `: 

There is no limit to the length of a formula. However, parsing very long records can be slow, and consideration should be given to pre-parsing them and passing the parsed formula to Xpress NonLinear rather than asking it to parse the formula itself.

#### Section 7.2 COLUMNS


Normal MPS-style records of the form

_column_   _row1_   _value1_   \[  _row2_   _value2_  \]

are supported. Non-linear relationships are modeled by using a formula instead of a constant in the _value1_ field. If a formula is used, then only one coefficient can be described in the record \(that is, there can be no _row2_ _value2_\). The formula begins with an equals sign \("="\) and is as described in the previous section.

A formula must be contained entirely on one record.

Variables used in formulae may be included in the `COLUMNS` section as variables, or may exist only as items within formulae. A variable which exists only within formulae is called an _implicit variable_.

Sometimes the non-linearity cannot be written as a coefficient. For example, in the constraint

 _Y - LOG(X) = 0_ ,

 `LOG(X)`cannot be written in the form of a coefficient. In such a case, the reserved column name "=" may be used in the first field of the record as shown:

| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
_Y_ | _MyRow_ | _1_ | 
_=_ | _MyRow_ | _= - LOG \( X \)_ | 
Effectively, "="is a column with a fixed activity of 1.0 .

When a file is read by `XSLPreadprob`, more than one coefficient can be defined for the same column/row intersection. As long as there is at most one constant coefficient \(one not written as a formula\), the coefficients will be added together. If there are two or more constant coefficients for the same intersection, they will be handled by the Optimizer according to its own rules \(normally additive, but the objective function retains only the last coefficient\).

#### Section 7.3 BOUNDS


Bounds can be included for variables which are not defined explicitly in the `COLUMNS` section of the matrix. If they are not in the `COLUMNS` section, they must appear as variables within formulae \( _implicit variables_\). A `BOUNDS` entry for an item which is not a column or a variable will produce a warning message and will be ignored.

MIP entities \(such as integer variables and members of Special Ordered Sets\) must be defined explicitly in the `COLUMNS` section of the matrix. If a variable would otherwise appear only in formulae in coefficients, then it should be included in the `COLUMNS` section with a zero entry in a row \(for example, the objective function\) which will not affect the result.

#### Section 7.4 SLPDATA


`SLPDATA` is a new section which holds additional information for solving the non-linear problem using SLP.

Many of the data items have a _setname_. This works in the same way as the `BOUND`, `RANGE` or `RHS` name, in that a number of different values can be given, each with a different set name, and the one which is actually used is then selected by specifying the appropriate setname before reading the problem.

Record type `IV` and the tolerance records `Tx`, `Rx` can have "=" as the variable name. This provides a default value for the record type, which will be used if no specific information is given for a particular variable.

Note that only linear `BOUND` types can be included in the `SLPDATA` section. Bound types for MIP entities \(discrete variables and special ordered sets\) must be provided in the normal `BOUNDS` section and the variables must also appear explicitly in the `COLUMNS` section.

All of the items in the SLPDATA section can be loaded into a model using Xpress NonLinear function calls.

##### DR \(Determining row\)


_DR variable rowname \[weighting\] \[limit\]_ 

The `DR` record defines the _determining row_ for a variable.

In most non-linear problems, there are some variables which are effectively defined by means of an equation in terms of other variables. Such an equation is called a _determining row_. If Xpress NonLinear knows the determining rows for the variables which appear in coefficients, then it can provide better linear approximations for the problem and can then solve it more quickly. Optionally, a non-zero integer value can be included in the _weighting_ field. Variables which have weights will generally be evaluated in order of increasing weight. Variables without weights will generally be evaluated after those which do have weights. However, if a variable _A_  \(with or without a weight\) is dependent through its determining row on another variable _B_ , then _B_  will always be evaluated first. The optional _limit_ field provides a variable specific value for `XSLP_CASCADENLIMIT`.

_Example:_

`DR  X  Row1`

This defines `Row1`as the determining row for the variable `X`. If `Row1`is

 _X - Y * Z = 6_ 

then _Y_ and _Z_ will be recalculated first before _X_ is recalculated as _Y*Z+6_ .

##### EC \(Enforced constraint\)


_EC rowname_ 

The `EC` record defines an _enforced constraint_. Penalty error vectors are never added to enforced constraints, so the effect of such constraints is maintained at all times.

Note that this means the _linearized_ version of the enforced constraint will be active, so it is important to appreciate that enforcing too many constraints can easily lead to infeasible linearizations which will make it hard to solve the original nonlinear problem.

_Example:_

`EC  Row1`

This defines `Row1`as an enforced constraint. When the SLP is augmented, no penalty error vectors will be added to the constraint, so the linearized version of `Row1`will constrain the linearized problem in the same sense \(L, G or E\) as the nonlinear version of `Row1`constrains the original nonlinear problem.

##### FR \(Free variable\)


_FR boundname variable_ 

An `FR` record performs the same function in the `SLPDATA` section as it does in the `BOUNDS` section. It can be used for bounding variables which do not appear as explicit columns in the matrix.

##### FX \(Fixed variable\)


_FX boundname variable value_ 

An `FX` record performs the same function in the `SLPDATA` section as it does in the `BOUNDS` section. It can be used for bounding variables which do not appear as explicit columns in the matrix.

##### IV \(Initial value\)


_IV setname variable \[value &#124; = formula\]_ 

An `IV` record specifies the initial value for a variable. All variables which appear in coefficients or terms, or which have non-linear coefficients, should have an `IV` record.

A formula provided as the initial value for a variable can contain references to other variables. It will be evaluated based on the initial values of those variables \(which may themselves be calculated by formula\). It is the user's responsibility to ensure that there are no circular references within the formulae. Formulae are typically used to calculate consistent initial values for dependent variables based on the values of independent variables.

If an `IV` record is provided for the _equals column_ \(the column whose name is "=" and which has a fixed value of 1.0\), the value provided will be used for all SLP variables which do not have an explicit initial value of their own.

If there is no explicit or implied initial value for an SLP variable, the value of control parameter `XSLP_DEFAULTIV` will be used.

If the initial value is greater than the upper bound of the variable, the upper bound will be used; if the initial value is less than the lower bound of the variable, the lower bound will be used.

If both a formula and a value are provided, then the explicit value will be used.

_Example:_

`IV  IVSET1  Col99  1.4971`

 `IV  IVSET2  Col99  2.5793`

This sets the initial value of column `Col99`. The initial value to be used is selected using control parameter `XSLP_IVNAME`. If no selection is made, the first initial value set found will be used.

If `Col99` is bounded in the range `1≤ Col99≤ 2` then in the second case \(when `IVSET2` is selected\), an initial value of 2 will be used because the value given is greater than the upper bound.

`IV  IVSET2  Col98  = Col99 * 2`

This sets the value of `Col98`to twice the initial value of `Col99`when `IVSET2`is the selected initial value set.

##### LO \(Lower bounded variable\)


_LO boundname variable value_ 

A `LO` record performs the same function in the `SLPDATA` section as it does in the `BOUNDS` section. It can be used for bounding variables which do not appear as explicit columns in the matrix.

##### Rx, Tx \(Relative and absolute convergence tolerances\)


_Rx setname variable value_ 

_Tx setname variable value_ 

The `Tx` and `Rx` records \(where "x" is one of the defined tolerance types\) define specific tolerances for convergence of the variable. See the section "convergence criteria" for a list of convergence tolerances. The same tolerance set name \( _setname_\) is used for all the tolerance records.

_Example:_

`RA  TOLSET1  Col99  0.005`

 `TA  TOLSET1  Col99  0.05`

 `RI  TOLSET1  Col99  0.015`

 `RA  TOLSET1  Col01  0.01`

 `RA  TOLSET2  Col01  0.015`

These records set convergence tolerances for variables `Col99`and `Col01`. Tolerances `RA`\(relative convergence tolerance\), `TA`\(absolute convergence tolerance\) and `RI`\(relative impact tolerance\) are set for `Col99`using the tolerance set named `TOLSET1`.

Tolerance `RA`is set for variable `Col01`using tolerance sets named `TOLSET1`and `TOLSET2`.

If control parameter `XSLP_TOLNAME`is set to the name of a tolerance set before the problem is read using `XSLPreadprob`, then only the tolerances on records with that tolerance set will be used. If `XSLP_TOLNAME`is blank or not set, then the name of the set on the first tolerance record will be used.

##### SB \(Initial step bound\)


_SB setname variable value_ 

An `SB` record defines the initial step bounds for a variable. Step bounds are symmetric \(i.e. the bounds on the delta are _-SB≤delta≤+SB_ \). If a value of 1.0E+20 is used \(equivalent to `XPRS_PLUSINFINITY` in programming\), the delta will never have step bounds applied, and will almost always be regarded as converged.

If there is no explicit initial step bound for an SLP variable, a value will be estimated either from the size of the coefficients in the initial linearization, or from the values of the variable during the early SLP iterations. The value of control parameter `XSLP_DEFAULTSTEPBOUND` provides a lower limit for the step bounds in such cases.

If there is no explicit initial step bound, then the closure convergence tolerance cannot be applied to the variable.

_Example:_

`SB  SBSET1  Col99  1.5`

 `SB  SBSET2  Col99  7.5`

This sets the initial step bound of column `Col99`. The value to be used is selected using control parameter `XSLP_SBNAME`. If no selection is made, the first step bound set found will be used.

##### UF \(User function\)


_UF funcname = libraryname \( functiontype \) linkage = library_ 

A `UF` record defines a user function.

The definition includes the function's type which matches the parameter supplied to the adduserfunction call.

_Example:_

`UF  MyFunc  (  VECMAPDELTA )  DLL  =  UserLib`

This defines a user function called `MyFunc`that takes multiple input arguments and supplies its own derivatives. The linkage is `DLL`\(free-standing user library or DLL\) and the function is in file `UserLib`.

##### UP \(Free variable\)


_UP boundname variable value_ 

An `UP` record performs the same function in the `SLPDATA` section as it does in the `BOUNDS` section. It can be used for bounding variables which do not appear as explicit columns in the matrix.

##### WT \(Explicit row weight\)


_WT rowname value_ 

The `WT` record is a way of setting the initial penalty weighting for a row. If `value` is positive, then the default initial weight is multiplied by the value given. If `value` is negative, then the absolute value will be used instead of the default weight.

Increasing the penalty weighting of a row makes it less attractive to violate the constraint during the SLP iterations.

_Examples:_

`WT  Row1  3`

This changes the initial weighting on `Row1`by multiplying by 3 the default weight calculated by Xpress-SLP during problem augmentation.

`WT  Row1  -3`

This sets the initial weighting on `Row1`to 3.

##### DL \(variable specific Determining row cascade iteration Limit\)


_DL columnname limit_ 

A `DL` record specififies a variable specific iteration limit to be emposed on the number of iterations when cascading the variable. This can be used to overwrite the setting of `XSLP_CASCADENLIMIT` for a specific variable.

### Chapter 8 Xpress-SLP Solution Process


This section gives a brief overview of the sequence of operations within Xpress-SLP once the data has been set up. The positions of the possible user callbacks are also shown.


Check if problem is an SLP problem or not. Call the appropriate XPRS library function if not, and DONE.

\[Call out to user callback if set by `XSLPsetcbslpstart`\]

Augment the matrix \(create the linearized structure\) if not already done

If determining row data supplied, calculate cascading order and detect determining columns

 _DO_ 

 \[Call out to user callback if set by `XSLPsetcbiterstart`\]

 If previous solution available, pre-process solution

  Execute line search

  \[Call out to user callback if set by `XSLPsetcbcascadestart`\]

  Sequentially update values of SLP variables \(cascading\) and re-calculate coefficients

  For each variable \(in a suitable evaluation order\):

   Update solution value \(cascading\) and re-calculate coefficients

   \[Call out to user callback if set by `XSLPsetcbcascadevar`\]

  \[Call out to user callback if set by `XSLPsetcbcascadeend`\]

 Update penalties

 Update coefficients, bounds and RHS in linearized matrix

 Solve linearized problem using the Xpress Optimizer

 Recover SLP variable and delta solution values

 Test convergence against specified tolerances and other criteria

 For each variable:

  Test convergence against specified tolerances

  \[Call out to user callback if set by `XSLPsetcbitervar`\]

 For each variable with a determining column:

  Check value of determining column and fix variable when necessary, or

  \[Call out to user callback if set by `XSLPsetcbdrcol`\]

  Reset variable convergence status if a change is made to a variable

 If not all variables have converged, check for other extended convergence criteria

 If the solution has converged, then _BREAK_ 

 For each SLP variable:

  Update history

  Reset step bounds

 \[Call out to user callback if set by `XSLPsetcbiterend`\]

 Change row types for DC rows as required

 If SLP iteration limit is reached, then _BREAK_ 

 _END DO_ 

\[Call out to user callback if set by `XSLPsetcbslpend`\]



For MISLP \(mixed-integer SLP\) problems, the above solution process is normally repeated at each node. The standard procedure for each node is as follows:


Initialize node

\[Call out to user callback if set by `XSLPsetcbprenode`\]

Solve node using SLP procedure

If an optimal solution is obtained for the node then

 \[Call out to user callback if set by `XSLPsetcboptnode`\]

If an integer optimal solution is obtained for the node then

 \[Call out to user callback if set by `XSLPsetcbintsol`\]

When node is completed

 \[Call out to user callback if set by `XSLPsetcbslpnode`\]



When a problem is destroyed, there is a call out to the user callback set by `XSLPsetcbdestroy`.

#### Section 8.1 Analyzing the solution process


Xpress-SLP provides a comprehensive set of callbacks to interact with, and to analyze the solution process. However, there are a set of purpose build options that are intended to assist and make the analysis more efficient.

For infeasible problems, it often helps to identify the source of conflict by running XPRESS' Irreducible Infeasibiliy Set \(IIS\) finder tool. The set found by IIS often helps to either point to a problem in the original model formulation, or if the infeasibility is a result of conflicting step bounds or linearization updates; please see control `XSLP_ANALYZE`.

It is often advantageous to trace a certain variable, constraint or a certain property through the solution process. `XSLP_TRACEMASK` and `XSLP_TRACEMASKOPS` allows for collecting detailed information during the solution process, without the need to stop XSLP between iterations.

For in depth debugging purposes or support requests, it is possible to create XSLP save files and linearizations at verious iterations, controlled by `XSLP_AUTOSAVE` and `XSLP_ANALYZE`.

#### Section 8.2 The initial point


The solution process is sensitive to the initial values which are selected for variables in the problem, and particularly so for non-convex problems. It is not uncommon for a general nonlinear problem to have a feasible region which is not connected, and in this case the starting point may largely determine which region, connected set, or basin of attraction the final solution belongs to.

Note that it may not always be beneficial to completely specify an initial point, as the solvers themselves may be able to detect suitable starting values for some or all of the variables.

#### Section 8.3 Derivatives


Both XSLP and Knitro require the availability of derivative information for the constraints and objective function in order to solve a problem. In the Xpress NonLinear framework, several advanced approaches to the production of both first and second order derivatives \(the Jacobian and Hessian matrices\) are available, and which approach is used can be controlled by the user.

##### Finite Differences


The simplest such method is the use of finite differences, sometimes called numerical derivatives. This is a relatively coarse approximation, in which the function is evaluated in a small neighborhood of the point in question. The standard argument from calculus indicates that an increasingly accurate approximation to the derivative of the function will be found as the size of the neighborhood decreases. This argument ignores the effects of floating point arithmetic, however, which can make it difficult to select values sufficiently small to give a good approximation to the function, and yet sufficiently large to avoid substantial numerical error.

The high performance implementation in XSLP makes use of subexpression caching to improve performance, but finite differences are inherently inefficient. They may however be necessary when the function itself is not known in closed form. When analytic approaches cannot be used, due to the use of expensive black box functions which do not provide derivatives \(note that XSLP does allow user functions to provide their own derivatives\), the cost of function evaluations may become a dominant factor in solve time. It is important to note that each second order numerical derivative costs twice as much as a first order numerical derivative, and this can make XSLP more attractive than Knitro for such problems.

##### Symbolic Differentiation


##### Automatic Differentiation


An automatic differentiation engine in contrast can simultaneously compute multiple derivatives by repeated application of the chain rule. This is a very efficient means of calculating large numbers of Hessian entries, and is the default approach to providing derivative information to Knitro. It is also the default choice for SLP in case of large scale models.

#### Section 8.4 Points of inflection


A point of inflection in a given variable occurs when the first and second order partial derivatives with respect to that variable become zero, but there exist nonzero derivatives of higher order. At such points, the approximations the iterative nonlinear methods create do not encapsulate enough information about the behavior of the function, and both first and second order methods may experience difficulties. For example, consider the following problem
_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _x<sup>3</sup>_ | 
subject to | _-1≤x≤1_ | 
_
 for which the optimal solution is -1.

When the initial value of _x_  is varied, XSLP and Knitro produce the solutions presented in Table  _Effect of an inflection point on solution values._ for this problem:


![Effect of an inflection point on solution values. images/inflection1.png](Graphic/images/inflection1.png)

    
  **Figure 8.1:** Effect of an inflection point on solution values. 



As a second order method, Knitro examines a local quadratic approximation to the function. Starting at both 0 and 1, this approximation will closely resemble the _x^2_  function, and so the solution will be attracted to zero. For XSLP, which is a first order method, the approximation at 0 will have a zero gradient. However, XSLP can detect this situation and will perform the analysis required to substitute an appropriate small nonzero \(placeholder\) value for the derivative during the first iterations. As can be seen, this allows XSLP find an optimal solution in all three cases.

This is only one example of the behaviour of these solvers without further tuning. The long steps which XSLP often takes can be both beneficial and harmful in different contexts. For example, if the function to be optimized includes many local minima, it is possible to see the opposite pattern for XSLP and Knitro. Consider
_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _x sin\(100 x<sup>2</sup>\)_ | 
subject to | _-1≤x≤1_ | 
_
 which has many local minima. For this problem, the results obtained are presented in Table  _Local solutions for a function with several local optima_:


![Local solutions for a function with several local optima images/inflection2.png](Graphic/images/inflection2.png)

    
  **Figure 8.2:** Local solutions for a function with several local optima 



In this case the same long steps made by XSLP lead to it finding the an identical, but unfortunate, local optimum no matter which initial point it begins from.

#### Section 8.5 Trust regions


In a second order method like Knitro, there is a well-defined merit function which can be used to compare solutions, and which provides a measure of the progress being made by the algorithm. This is a significant advantage over first order methods, in which there is generally no such function.

Despite their speed and resilience to points of inflection, first order methods can also experience difficulties at points in which the current approximation is not well posed. Consider
_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _x<sup>2</sup>_ | 
subject to | _x_ free | 
_
 at _x=1_ . A naive linearization is simply
_

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
minimize | _2x_ | 
subject to | _x_ free | 
_
 which is unbounded. To address such situations, XSLP will introduce trust regions to model the neighborhood in which the current approximation is believed to be applicable. When coupled with the use of derivative placeholders described in the previous section, this can lead XSLP to initially make large moves from its starting position.

### Chapter 9 Handling Infeasibilities


By default, Xpress-SLP will include _penalty error vectors_ in the augmented SLP structure. This feature adds explicit positive and negative slack vectors to all constraints \(or, optionally, just to equality constraints\) which include nonlinear coefficients. In many cases, this is itself enough to retain feasibility. There is also an opportunity to add penalty error vectors to all constraints, but this is not normally required.

During cascading \(see next section\), Xpress-SLP will ensure that the value of a cascaded variable is never set outside its lower and upper bounds \(if these have been specified\).

#### Section 9.1 Infeasibility Analysis in the Xpress Optimizer

`iis` `repairinfeas` `iis` `repairinfeas`
#### Section 9.2 Managing Infeasibility with Xpress Knitro


 * ``XKTR_PARAM_FEASTOL``: This is the relative feasibility tolerance applied to a problem.
 * ``XKTR_PARAM_FEASTOLABS``: This is the corresponding absolute feasibility tolerance.
 * ``XKTR_PARAM_INFEASTOL``: This is the tolerance for declaring a problem infeasible.
`XKTR_PARAM_BAR_FEASIBLE` `get` `get_stay``XKTR_PARAM_ALGORITHM``XKTR_PARAM_BAR_SWITCHRULE``XKTR_PARAM_BAR_PENCONS`
#### Section 9.3 Managing Infeasibility with Xpress-SLP


 1. Infeasibility introduced by the error of the approximation, most noticeable when significant steps are made in the linearization.
 2. Infeasibility introduced by the activation of penalty breakers, where it was not otherwise possible to make a meaningful step in the linearization.

 * ``XSLP_ECFTOL_A``: The absolute linearization feasibility tolerance is compared for each constraint in the original, nonlinear problem to its violation by the current solution.
 * ``XSLP_ECFTOL_R``: The relative linearization feasibility tolerance is compared for each constraint in the original, nonlinear problem to its violation by the current solution, relative to the maximum absolute value of the positive and negative contributions to the constraint.

#### Section 9.4 Penalty Infeasibility Breakers in XSLP

`XSLP_CURRENTERRORCOST``XSLP_ERRORCOST``XSLP_ERRORCOSTFACTOR``XSLP_ERRORMAXCOST``XSLP_ALGORITHM``XSLP_ERRORCOST``XSLP_OBJTOPENALTYCOST``XSLP_ERRORCOST``XSLP_ALGORITHM``XSLP_LOG`
### Chapter 10 Cascading


_Cascading_ is the process of recalculating the values of SLP variables to be more consistent with each other. The procedure involves sequencing the designated variables in order of dependence and then, starting from the current solution values, successively recalculating values for the variables, and modifying the stored solution values as required. Normal cascading is only possible if a _determining row_ can be identified for each variable to be recalculated. A determining row is an equality constraint which uniquely determines the value of a variable in terms of other variables whose values are already known. Any variable for which there is no determining row will retain its original solution value. Defining a determining row for a column automatically makes the column into an SLP variable.

In extended MPS format, the SLPDATA record type "DR" is used to provide information about determining rows.

In the Xpress NonLinear function library, function `XSLPsetdetrow` allows the definition of a determining row for a column.

The cascading procedure is as follows:


 * Produce an order of evaluation to ensure that variables are cascaded after any variables on which they are dependent.
 * After each SLP iteration, evaluate the columns in order, updating coefficients only as required. If a determining row cannot calculate a new value for the SLP variable \(for example, because the coefficient of the variable evaluates to zero\), then the current value may be left unchanged, or \(optionally\) the previous value can be used instead.
 * If a feedback loop is detected \(that is, a determining row for a variable is dependent indirectly on the value of the variable\), the evaluation sequence is carried out in the order in which the variables are weighted, or the order in which they are encountered if there is no explicit weighting.
 * Check the step bounds, individual bounds and cascaded values for consistency. Adjust the cascaded result to ensure it remains within any explicit or implied bounds.


Normally, the solution value of a variable is exactly equal to its assumed value plus the solution value of its delta. Occasionally, this calculation is not exact \(it may vary by up to the LP feasibility tolerance\) and the difference may cause problems with the SLP solution path. This is most likely to occur in a quadratic problem when the quadratic part of the objective function contains SLP variables. Xpress NonLinear can re-calculate the value of an SLP variable to be equal to its assumed value plus its delta, rather than using the solution value itself.

`XSLP_CASCADE` is a bitmap which determines whether cascading takes place and whether the recalculation of solution values is extended from the use of determining rows to recalculation of the solution values for all SLP variables, based on the assumed value and the solution value of the delta.

In the following table, in the definitions under **Category** , _error_ means the difference between the solution value and the assumed value plus the delta value. Bit settings in `XSLP_CASCADE` are used to determine which category of variable will have its value recalculated as follows:


__Bit__ | __Constant name__ | __Category__ | 
---------- |  ---------- | ---------- | 
0 | `XSLP_CASCADE_ALL` | SLP variables with determining rows | 
1 | `XSLP_CASCADE_COEF_VAR` | Variables appearing in coefficients where the error is greater than the feasibility tolerance | 
2 | `XSLP_CASCADE_ALL_COEF_VAR` | Variables appearing in coefficients where the error is greater than 1.0E-14 | 
3 | `XSLP_CASCADE_STRUCT_VAR` | Variables not appearing in coefficients where the error is greater than the feasibility tolerance | 
4 | `XSLP_CASCADE_ALL_STRUCT_VAR` | Variables not appearing in coefficients where the error is greater than 1.0E-14 | 

In the presence of determining rows that include instantiated functions, SLP can attempt to group the corresponding variables together in the cascading order. This can be achieved by setting

__Bit__ | __Constant name__ | __Effect__ | 
---------- |  ---------- | ---------- | 
0 | `XSLP_CASCADE_SECONDARY_GROUPS` | Create secondary order groupping DR rows with instantiated user functions together in the order | 


#### Section 10.1 Determining rows and determining columns


Normally, Xpress-SLP automatically identifies if the constraint selected as determining row for a variable defines the value of the SLP variable which it determines or not. However, in certain situations, the value of a single other column determines if the determing row defines the variable or not; such a column is called the determining column for the variable.

This situation is typical when the determined and determining column form a bilinear term: x \* y + F\( Z \) = 0 where y is the determined variable, Z is a set of other variables not including x or y, and F is an arbitrary function; in this case x is the determining column. These variable pairs are detected automatically. In case the absolute value of x is smaller than `XSLP_DRCOLTOL`, then variable y will not be cascaded, instead its value will be fixed and kept at its current value until the value of x becomes larger than the threshold.

Alternatively, the handling of variables for which a determining column has been identified can be customized by using a callback, see `XSLPsetcbdrcol`.

### Chapter 11 Convergence criteria


#### Section 11.1 Convergence criteria


In Xpress-SLP there are two levels of convergence criteria. On the higher level, convergence is driven by the target relative feasibility / validation control `XSLP_VALIDATIONTARGET_R`, and the target first order validation tolerance `XSLP_VALIDATIONTARGET_K`. These high level targets drive the traditional SLP convergence measures, of which there are three types for testing convergence:
 * Strict convergence tests on variables
 * Extended convergence tests on variables
 * Convergence tests on the solution overall


#### Section 11.2 Convergence overview


##### Strict Convergence


 * ``XSLP_CTOL``: The closure tolerance is compared against the movement of a variable relative to its initial step bound.
 * ``XSLP_ATOL_A``: The absolute delta tolerance is compared against the absolute movement of a variable.
 * ``XSLP_ATOL_R``: The relative delta tolerance is compared against the movement of a variable relative to its initial value.

##### Extended Convergence


 * ``XSLP_MTOL_A``: The absolute matrix tolerance is compared against the approximation error relative only to the absolute value of the variable.
 * ``XSLP_MTOL_R``: The relative matrix tolerance is compared against the approximation error relative to the size of the nonlinear term before any step is taken.
 * ``XSLP_ITOL_A``: The absolute impact tolerance is compared against the approximation error of the nonlinear term.
 * ``XSLP_ITOL_R``: The relative impact tolerance is compared against the approximation error relative to the positive and negative contributions to each constraint.
 * ``XSLP_STOL_A``: The absolute slack impact tolerance is compared against the approximation error, but only for non-binding constraints, which is to say those for which the marginal value is small \(as defined by `XSLP_MVTOL`\).
 * ``XSLP_STOL_R``: The relative slack impact tolerance is compared against the approximation error relative to the term's contribution to its constraints, but only for non-binding constraints, which is to say those for which the marginal value is small \(as defined by `XSLP_MVTOL`\).

##### Stopping Criterion

`XSLP_STATUS``XSLP_CONVERGENCEOPS`
 * `VTOL`: This is the baseline static objective function tolerance, which is compared against the change in the objective over a given number of iterations, relative to the average objective value. Satisfaction of VTOL does not imply convergence of the variables.

 * ``XSLP_VCOUNT``: This is the number of iterations over which to apply this measure of static objective convergence.
 * ``XSLP_VLIMIT``: The static objective function test is applied only after at least `XSLP_VLIMIT` + `XSLP_SBSTART` XSLP iterations have taken place.
 * ``XSLP_VTOL_A``: This is the absolute tolerance which is compared to the range of the objective over the last `XSLP_VLIMIT` iterations.
 * ``XSLP_VTOL_R``: This is the tolerance used for a scaled version of the absolute test which considers the average size of the absolute value of the objective over the previous `XSLP_VLIMIT` iterations.
 * `OTOL`: This static objective function tolerance is applied when there are no unconverged variables in active constraints, although some variables with active step bounds might remain. It is compared to the change in the objective over a given number of iterations, relative to the average objective value.

 * ``XSLP_OCOUNT``: This is the number of iterations over which to apply this measure of static objective convergence.
 * ``XSLP_OTOL_A``: This is the absolute tolerance which is compared to the range of the objective over the last `XSLP_OCOUNT` iterations.
 * ``XSLP_OTOL_R``: This is used for a scaled version of the absolute test which considers the average size of the absolute value of the objective over the previous `XSLP_OCOUNT` iterations.
 * `XTOL`: This static objective function tolerance is applied when a practical solution has been found. It is compared against the change in the objective over a given number of iterations, relative to the average objective value.

 * ``XSLP_XCOUNT``: This is the number of iterations over which to apply this measure of static objective convergence.
 * ``XSLP_XLIMIT``: This is the maximum number of iterations which can have occurred for this static objective function test to be applied. Once this number is exceeded, the solution is deemed to have converged if all the variables have converged by the strict or extended criteria.
 * ``XSLP_XTOL_A``: This is the absolute tolerance which is compared to the range of the objective function over the last `XSLP_XLIMIT` iterations.
 * ``XSLP_XTOL_R``: This is used for a scaled version of the absolute test which considers the average size of the absolute value of the objective over the last `XSLP_XLIMIT` iterations.
 * `WTOL`: The extended convergence continuation tolerance is applied when a practical solution has been found. It is compared to the change in the objective during the previous iteration.

 * ``XSLP_WCOUNT``: This is number of iterations over which to calculate this measure of static objective convergence in the relative version of the test.
 * ``XSLP_WTOL_A``: This is the absolute tolerance which is compared to the change in the objective in the previous iteration.
 * ``XSLP_WTOL_R``: This is used for a scaled version of the test which considers the average size of the absolute value of the objective over the last `XSLP_WCOUNT` iterations.

##### Step Bounding

`XSLP_SBSTART``XSLP_ALGORITHM`
 * ``XSLP_SBSTART``: This defines the number of iterations which must occur before XSLP may apply non-essential step bounding. When a linearization is unbounded, XSLP will introduce step bounding regardless of the value of this control.
 * ``XSLP_DEFAULTSTEPBOUND``: This is the initial size of the step bounds introduced. Depending upon the value of `XSLP_ALGORITHM`, XSLP may use the iterations before `XSLP_SBSTART` to refine this initial value on a per variable basis.

#### Section 11.3 Convergence: technical details


In the following sections we shall use the subscript _0_ to refer to values used to build the linear approximation \(the _assumed_ value\) and the subscript _1_ to refer to values in the solution to the linear approximation \(the _actual_ value\). We shall also useδ to indicate the change between the assumed and the actual values, so that for example:

 _δX = X<sub>1</sub>- X<sub>0</sub>_ .

The tests are described in detail later in this section. Tests are first carried out on each variable in turn, according to the following sequence:

Strict convergence criteria:
 1. **Closure tolerance**  \( [CTOL](#ssecCTOL)\).
   *  This tests _δX_ against the initial step bound of _X_ .

 2. **Delta tolerance**  \( [ATOL](#ssecATOL)\)
   *  This tests _δX_ against _X<sub>0</sub>_ .


If the strict convergence tests fail for a variable, it is tested against the extended convergence criteria:
 4. **Matrix tolerance**  \( [MTOL](#ssecMTOL)\)
   *  This tests whether the effect of a matrix coefficient is adequately approximated by the linearization. It tests the error against the magnitude of the effect.

 5. **Impact tolerance**  \( [ITOL](#ssecITOL)\)
   *  This tests whether the effect of a matrix coefficient is adequately approximated by the linearization. It tests the error against the magnitude of the contributions to the constraint.

 6. **Slack impact tolerance**  \( [STOL](#ssecSTOL)\)
   *  This tests whether the effect of a matrix coefficient is adequately approximated by the linearization and is applied only if the constraint has a negligible marginal value \(that is, it is regarded as "not constraining"\). The test is the same as for the impact tolerance, but the tolerance values may be different.
 The three extended convergence tests are applied simultaneously to all coefficients involving the variable, and each coefficient must pass at least one of the tests if the variable is to be regarded as converged. If any coefficient fails the test, the variable has not converged.

Regardless of whether the variable has passed the system convergence tests or not, if a convergence callback function has been set using `XSLPsetcbitervar` then it is called to allow the user to determine the convergence status of the variable.
 7. **User convergence test** 
   *  This test is entirely in the hands of the user and can return one of three conditions: the variable has converged on user criteria; the variable has not converged; or the convergence status of the variable is unchanged from that determined by the system.


Once the tests have been completed for all the variables, there are several possibilities for the convergence status of the solution:
 1. All variables have converged on strict criteria or user criteria.
 2. All variables have converged, some on extended criteria, and there are no active step bounds \(that is, there is no delta vector which is at its bound and has a significant reduced cost\).
 3. All variables have converged, some on extended criteria, and there are active step bounds \(that is, there is at least one delta vector which is at its bound and has a significant reduced cost\).
 4. Some variables have not converged, but these have non-constant coefficients only in constraints which are not active \(that is, the constraints do not have a significant marginal value\);
 5. Some variables have not converged, and at least one has a non-constant coefficient in an active constraint \(that is, the constraint has a significant marginal value\);


If \(a\) is true, then the solution has converged on _strict convergence criteria_.

If \(b\) is true, then the solution has converged on _extended convergence criteria_.

If \(c\) is true, then the solution is a _practical_ solution. That is, the solution is an optimal solution to the linearization and, within the defined tolerances, it is a solution to the original nonlinear problem. It is possible to accept this as the solution to the nonlinear problem, or to continue optimizing to see if a better solution can be obtained.

If \(d\) or \(e\) is true, then the solution has not converged. Nevertheless, there are tests which can be applied to establish whether the solution can be regarded as converged, or at least whether there is benefit in continuing with more iterations.

The first convergence test on the solution simply tests the variation in the value of the objective function over a number of SLP iterations:
 8. **Objective function convergence test 1**  \( [VTOL](#ssecVTOL)\)
   *  This test measures the range of the objective function \(the difference between the maximum and minimum values\) over a number of SLP iterations, and compares this against the magnitude of the average objective function value. If the range is small, then the solution is deemed to have converged.
 Notice that this test says nothing about the convergence of the variables. Indeed, it is almost certain that the solution is not in any sense a practical solution to the original nonlinear problem. However, experience with a particular type of problem may show that the objective function does settle into a narrow range quickly, and is a good indicator of the ultimate _value_ obtained. This test can therefore be used in circumstances where only an estimate of the solution value is required, not how it is made up. One example of this is where a set of schedules is being evaluated. If a quick estimate of the value of each schedule can be obtained, then only the most profitable or economical ones need be examined further.

If the convergence status of the variables is as in \(d\) above, then it may be that the solution is practical and can be regarded as converged:
 9. **Objective function convergence test 2**  \( [XTOL](#ssecXTOL)\)
   *  If there are no unconverged values in active constraints, then the inaccuracies in the linearization \(at least for small errors\) are not important. If a constraint is not active, then deleting the constraint does not change the feasibility or optimality of the solution. The convergence test measures the range of the objective function \(the difference between the maximum and minimum values\) over a number of SLP iterations, and compares this against the magnitude of the average objective function value. If the range is small, then the solution is deemed to have converged.
 The difference between this test and the previous one is the requirement for the convergence status of the variables to be \(d\).

Unless test 7 \(VTOL\) is being applied, if the convergence status of the variables is \(e\) then the solution has not converged and another SLP iteration will be carried out.

If the convergence status is \(c\), then the solution is practical. Because there are active step bounds in the solution, a "better" solution would be obtained to the linearization if the step bounds were relaxed. However, the linearization becomes less accurate the larger the step bounds become, so it might not be the case that a better solution would also be achieved for the nonlinear problem. There are two convergence tests which can be applied to decide whether it is worth continuing with more SLP iterations in the hope of improving the solution:
 10. **Objective function convergence test 3**  \( [OTOL](#ssecOTOL)\)
   *  If all variables have converged \(even if some are converged on extended criteria only, and some of those have active step bounds\), the solution is a practical one. If the objective function has not changed significantly over the last few iterations, then it is reasonable to suppose that the solution will not be significantly improved by continuing with more SLP iterations. The convergence test measures the range of the objective function \(the difference between the maximum and minimum values\) over a number of SLP iterations, and compares this against the magnitude of the average objective function value. If the range is small, then the solution is deemed to have converged.

 11. **Extended convergence continuation test**  \( [WTOL](#ssecWTOL)\)
   *  Once a solution satisfying \(c\) has been found, we have a practical solution against which to compare solution values from later SLP iterations. As long as there has been a significant improvement in the objective function, then it is worth continuing. If the objective function over the last few iterations has failed to improve over the practical solution, then the practical solution is restored and the solution is deemed to have converged.
 The difference between tests 9 and 10 is that 9 \(OTOL\) tests for the objective function being stable, whereas 10 \(WTOL\) tests whether it is actually improving. In either case, if the solution is deemed to have converged, then it has converged to a practical solution.

##### Closure tolerance \(CTOL\)


If an initial step bound is provided for a variable, then the closure test measures the significance of the magnitude of the delta compared to the magnitude of the initial step bound. More precisely:

Closure test:
_ABS\(δX\)≤B \* XSLP\_CTOL_
 where _B_  is the initial step bound for _X_ . If no initial step bound is given for a particular variable, the closure test is not applied to that variable, even if automatic step bounds are applied to it during the solution process.

If a variable passes the closure test, then it is deemed to have converged.

##### Delta tolerance \(ATOL\)


The simplest tests for convergence measure whether the actual value of a variable in the solution is significantly different from the assumed value used to build the linear approximation.

The absolute test measures the significance of the magnitude of the delta; the relative test measures the significance of the magnitude of the delta compared to the magnitude of the assumed value. More precisely:

Absolute delta test:

_ABS\(δX\)≤XSLP\_ATOL\_A_

Relative delta test:

_ABS\(δX\)≤X<sub>0</sub>\* XSLP\_ATOL\_R_

If a variable passes the absolute or relative delta tests, then it is deemed to have converged.

##### Matrix tolerance \(MTOL\)


The matrix tests for convergence measure the linearization error in the effect of a coefficient. The _effect_ of a coefficient is its value multiplied by the activity of the column in which it appears.

_E=V \* C_

where _V_  is the activity of the matrix column in which the coefficient appears, and _C_  is the value of the coefficient. The linearization approximates the effect of the coefficient as

_E=V \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>_

where _V_  is as before, _C<sub>0</sub>_  is the value of the coefficient _C_  calculated using the assumed values for the variables and _C'<sub>0</sub>_  is the value of _\(∂C\) / \(∂X\)_  calculated using the assumed values for the variables.

The error in the effect of the coefficient is given by

_δE = V<sub>1</sub>\* C<sub>1</sub>- \(V<sub>1</sub>\* C<sub>0</sub>  +  δX \* C'<sub>0</sub>\)_

Absolute matrix test:

_ABS\(δE\)≤XSLP\_MTOL\_A_

Relative matrix test:

_ABS\(δE\)≤V<sub>0</sub>\*X<sub>0</sub>\* XSLP\_MTOL\_R_

If all the coefficients which involve a given variable pass the absolute or relative matrix tests, then the variable is deemed to have converged.

##### Impact tolerance \(ITOL\)


The impact tests for convergence also measure the linearization error in the effect of a coefficient. The effect of a coefficient was described in the previous section. Whereas the matrix test compares the error against the magnitude of the coefficient itself, the impact test compares the error against a measure of the magnitude of the constraint in which it appears. All the elements of the constraint are examined: for each, the contribution to the constraint is evaluated as the element multiplied by the activity of the vector in which it appears; it is then included in a _total positive contribution_ or _total negative contribution_ depending on the sign of the contribution. If the predicted effect of the coefficient is positive, it is tested against the total positive contribution; if the effect of the coefficient is negative, it is tested against the total negative contribution.

As in the matrix tests, the predicted effect of the coefficient is

_V \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>_

and the error is

_δE = V<sub>1</sub>\* C<sub>1</sub>- \(V<sub>1</sub>\* C<sub>0</sub>  +  δX \* C'<sub>0</sub>\)_

Absolute impact test:

_ABS\(δE\)≤XSLP\_ITOL\_A_

Relative impact test:

_ABS\(δE\)≤T<sub>0</sub>\* XSLP\_ITOL\_R_

where

_T<sub>0</sub>  = ABS\( ∑<sub>v∈V</sub>v<sub>0</sub>\* c<sub>0</sub>\)_

_c_  is the value of the constraint coefficient in the vector _v_ ; _V_  is the set of vectors such that _v<sub>0</sub>\*c<sub>0</sub>>0_  if _E_  is positive, or the set of vectors such that _v<sub>0</sub>\*c<sub>0</sub><0_  if _E_  is negative.

If a coefficient passes the matrix test, then it is deemed to have passed the impact test as well. If all the coefficients which involve a given variable pass the absolute or relative impact tests, then the variable is deemed to have converged.

##### Slack impact tolerance \(STOL\)


This test is identical in form to the impact test described in the previous section, but is applied only to constraints whose marginal value is less than `XSLP_ MVTOL`. This allows a weaker test to be applied where the constraint is not, or is almost not, binding.

Absolute slack impact test:

_ABS\(δE\)≤XSLP\_STOL\_A_

Relative slack impact test:

_ABS\(δE\)≤T<sub>0</sub>\* XSLP\_STOL\_R_

where the items in the expressions are as described in the previous section, and the tests are applied only when

_ABS\(π<sub>i</sub>\)<XSLP\_MVTOL_

where _π<sub>i</sub>_  is the marginal value of the constraint.

If all the coefficients which involve a given variable pass the absolute or relative matrix, impact or slack impact tests, then the variable is deemed to have converged.

##### Fixed variables due to determining columns smaller than threshold \(FX\)


Variables having a determining column, that are temporarily fixed due to the absolute value of the determining column being smaller than the threshold `XSLP_DRCOLTOL` are regarded as converged.

##### User-defined convergence


Regardless of what the Xpress-SLP convergence tests have said about the status of an individual variable, it is possible for the user to set the convergence status for a variable by using a function defined through the `XSLPsetcbitervar` callback registration procedure. The callback function returns an integer result _S_  which is interpreted as follows:

 * ___S<0_ __: mark variable as unconverged
 * ___S=0_ __: leave convergence status of variable unchanged
 * ___S≥11_ __: mark variable as converged with status S

Values of _S_  in the range 1 to 10 are interpreted as meaning convergence on the standard system-defined criteria.

If a variable is marked by the user as converged, it is treated as if it has converged on strict criteria.

##### Static objective function \(1\) tolerance \(VTOL\)


This test does not measure convergence of individual variables, and in fact does not in any way imply that the solution has converged. However, it is sometimes useful to be able to terminate an optimization once the objective function appears to have stabilized. One example is where a set of possible schedules are being evaluated and initially only a good estimate of the likely objective function value is required, to eliminate the worst candidates.

The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_

where _Iter_  is the `XSLP_ VCOUNT` most recent SLP iterations and _Obj_  is the corresponding objective function value.

Absolute static objective function \(3\) test:

_ABS\(δObj\)≤XSLP\_VTOL\_A_

Relative static objective function \(3\) test:

_ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_VTOL\_R_

The static objective function \(3\) test is applied only after at least `XSLP_ VLIMIT
+ XSLP_ SBSTART` SLP iterations have taken place. Where step bounding is being applied, this ensures that the test is not applied until after step bounding has been introduced.

If the objective function passes the relative or absolute static objective function \(3\) test then the solution will be deemed to have converged.

##### Static objective function \(2\) tolerance \(OTOL\)


This test does not measure convergence of individual variables. Instead, it measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables interacting with active constraints \(those that have a marginal value of at least `XSLP_ MVTOL`\) have converged. The rationale is that if the remaining unconverged variables are not involved in active constraints and if the objective function is not changing significantly between iterations, then the solution is more-or-less practical.

The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_

where _Iter_  is the `XSLP_ OCOUNT` most recent SLP iterations and _Obj_  is the corresponding objective function value.

Absolute static objective function \(2\) test:

_ABS\(δObj\)≤XSLP\_OTOL\_A_

Relative static objective function \(2\) test:

_ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_OTOL\_R_

If the objective function passes the relative or absolute static objective function \(2\) test then the solution is deemed to have converged.

##### Static objective function \(3\) tolerance \(XTOL\)


It may happen that all the variables have converged, but some have converged on extended criteria \(MTOL, ITOL or STOL\) and at least one of these is at its step bound. It is therefore possible that an improved result could be obtained by taking another SLP iteration. However, if the objective function has already been stable for several SLP iterations, then there is less likelihood of an improved result, and the converged solution can be accepted.

The static objective function \(1\) test measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables have converged, but some have converged on extended criteria \(MTOL, ITOL or STOL\) and at least one of these is at its step bound. Because all the variables have converged, the solution is already converged but the fact that some variables are at their step bound limit suggests that the objective function could be improved by going further.

The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_

where _Iter_  is the `XSLP_ XCOUNT` most recent SLP iterations and _Obj_  is the corresponding objective function value.

Absolute static objective function \(1\) test:

_ABS\(δObj\)≤XSLP\_XTOL\_A_

Relative static objective function \(1\) test:

_ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_XTOL\_R_

The static objective function \(1\) test is applied only until `XSLP_ XLIMIT` SLP iterations have taken place. After that, if all the variables have converged on strict or extended criteria, the solution is deemed to have converged.

If the objective function passes the relative or absolute static objective function \(1\) test then the solution is deemed to have converged.

##### Extended convergence continuation tolerance \(WTOL\)


This test is applied after a converged solution has been found where at least one variable has converged on extended criteria and is at its step bound limit. As described under XTOL above, it is possible that by continuing with additional SLP iterations, the objective function might improve. The extended convergence continuation test measures whether any improvement is being achieved. If not, then the last converged solution will be restored and the optimization will stop.

For a maximization problem, the improvement in the objective function at the current iteration compared to the objective function at the last converged solution is given by:

_δObj = Obj - ConvergedObj_

\(for a minimization problem, the sign is reversed\).

Absolute extended convergence continuation test:

_δObj>XSLP\_WTOL\_A_

Relative extended convergence continuation test:

_δObj>ABS\(ConvergedObj\) \* XSLP\_WTOL\_R_

A solution is deemed to have a significantly better objective function value than the converged solution if _δObj_  passes the relative _and_ absolute extended convergence continuation tests.

When a solution is found which converges on extended criteria and with active step bounds, the solution is saved and SLP optimization continues until one of the following:

 * a new solution is found which converges on some other criterion, in which case the SLP optimization stops with this new solution
 * a new solution is found which converges on extended criteria and with active step bounds, and which has a significantly better objective function, in which case this is taken as the new saved solution
 * none of the `XSLP_ WCOUNT` most recent SLP iterations has a significantly better objective function than the saved solution, in which case the saved solution is restored and the SLP optimization stops

### Chapter 12 Xpress-SLP Structures


#### Section 12.1 SLP Matrix Structures


Xpress-SLP augments the original matrix to include additional rows and columns to model some or all of the variables involved in nonlinear relationships, together with first-order derivatives.

The amount and type of augmentation is determined by the bit map control variable `XSLP_AUGMENTATION`:

 * `Bit 0`: Minimal augmentation. All SLP variables appearing in coefficients or matrix entries are provided with a corresponding update row and delta vector.
 * `Bit 1`: Even-handed augmentation. All nonlinear expressions are converted into terms. All SLP variables are provided with a corresponding update row and delta vector.
 * `Bit 2`: Create penalty error vectors \(+ and -\) for each equality row of the original problem containing a nonlinear coefficient or term. This can also be implied by the setting of bit 3.
 * `Bit 3`: Create penalty error vectors \(+ and/or - as required\) for each row of the original problem containing a nonlinear coefficient or term. Setting bit 3 to 1 implies the setting of bit 2 to 1 even if it is not explicitly carried out.
 * `Bit 4`: Create additional penalty delta vectors to allow the solution to exceed the step bounds at a suitable penalty.
 * `Bit 8`: Implement step bounds as constraint rows.
 * `Bit 9`: Create error vectors \(+ and/or - as required\) for each constraining row of the original problem.

If Bits 0-1 are not set, then Xpress-SLP will use standard augmentation: all SLP variables \(appearing in coefficients or matrix entries, or variables with non constant coefficients\) are provided with a corresponding update row and delta vector.

To avoid too many levels of super- and sub- scripting, we shall use _X_ , _Y_  and _Z_  as variables, _F()_  as a function, and _R_  as the row name. In the matrix structure, column and row names are shown _in italics_.
 _X<sub>0</sub>_  _X_  _F'<sub>x</sub>\(...\)_  _F_  _X_ 
##### Augmentation of a nonlinear coefficient


**Original matrix structure** 



|  | ___X___ | 
---------- |  ---------- | 
___R___ | _F(Y,Z)_ | 


  

**Matrix structure: minimal augmentation (XSLP_AUGMENTATION=1)** 



|  | ___X___ | ___Y___ | ___Z___ | ___dY___ | ___dZ___ | 
---------- |  ---------- | ---------- | ---------- | ---------- | ---------- | 
___R___ | _F\(Y<sub>0</sub>,Z<sub>0</sub>\)_ |  |  | _X<sub>0</sub>\*F'<sub>y</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | _X<sub>0</sub>\*F'<sub>z</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | 
___uY___ |  | _1_ |  | _-1_ |  | _=_ | _Y<sub>0</sub>_ | 
___uZ___ |  |  | _1_ |  | _-1_ | _=_ | _Z<sub>0</sub>_ | 


The original nonlinear coefficient \(X,R\) is replaced by its evaluation using the assumed values of the independent variables.

Two vectors and one equality constraint for each independent variable in the coefficient are created if they do not already exist.

The new vectors are:
 * The SLP variable \(e.g. _Y_ \)
 * The SLP delta variable \(e.g. _dY_ \)


The new constraint is the SLP update row \(e.g. _uY_ \) and is always an equality. The only entries in the update row are the +1 and -1 for the SLP variable and delta variable respectively. The right hand side is the assumed value for the SLP variable.

The entry in the original nonlinear constraint row for each independent variable is the first-order partial derivative of the implied term _X*F(Y,Z)_ , evaluated at the assumed values.

The delta variables are bounded by the current values of the corresponding step bounds.

  

**Matrix structure: standard augmentation (XSLP_AUGMENTATION=0)** 



|  | ___X___ | ___Y___ | ___Z___ | ___dX___ | ___dY___ | ___dZ___ | 
---------- |  ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | 
___R___ | _F\(Y<sub>0</sub>,Z<sub>0</sub>\)_ |  |  |  | _X<sub>0</sub>\*F'<sub>y</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | _X<sub>0</sub>\*F'<sub>z</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | 
___uX___ | _1_ |  |  | _-1_ |  |  | _=_ | _X<sub>0</sub>_ | 
___uY___ |  | _1_ |  |  | _-1_ |  | _=_ | _Y<sub>0</sub>_ | 
___uZ___ |  |  | _1_ |  |  | _-1_ | _=_ | _Z<sub>0</sub>_ | 


The original nonlinear coefficient \(X,R\) is replaced by its evaluation using the assumed values of the independent variables.

Two vectors and one equality constraint for each independent variable in the coefficient are created if they do not already exist.

The new vectors are:
 * The SLP variable \(e.g. _Y_ \)
 * The SLP delta variable \(e.g. _dY_ \)


The new constraint is the SLP update row \(e.g. _uY_ \) and is always an equality. The only entries in the update row are the +1 and -1 for the SLP variable and delta variable respectively. The right hand side is the assumed value for the SLP variable.

The entry in the original nonlinear constraint row for each independent variable is the first-order partial derivative of the implied term _X*F(Y,Z)_ , evaluated at the assumed values.

The delta variables are bounded by the current values of the corresponding step bounds.

One new vector and one new equality constraint are created for the variable containing the nonlinear coefficient.

The new vector is:
 * The SLP delta variable \(e.g. _dX_ \)


The new constraint is the SLP update row \(e.g. _uX_ \) and is always an equality. The only entries in the update row are the +1 and -1 for the original variable and delta variable respectively. The right hand side is the assumed value for the original variable.

The delta variable is bounded by the current values of the corresponding step bounds.

  

**Matrix structure: even-handed augmentation (XSLP_AUGMENTATION=2)** 



|  | ___=___ | ___X___ | ___Y___ | ___Z___ | ___dX___ | ___dY___ | ___dZ___ | 
---------- |  ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | 
___R___ | _X<sub>0</sub>\*F\(Y<sub>0</sub>,Z<sub>0</sub>\)_ |  |  |  | _F\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | _X<sub>0</sub>\*F'<sub>y</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | _X<sub>0</sub>\*F'<sub>z</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | 
___uX___ |  | _1_ |  |  | _-1_ |  |  | _=_ | _X<sub>0</sub>_ | 
___uY___ |  |  | _1_ |  |  | _-1_ |  | _=_ | _Y<sub>0</sub>_ | 
___uZ___ |  |  |  | _1_ |  |  | _-1_ | _=_ | _Z<sub>0</sub>_ | 


The coefficient is treated as if it was the term _X*F(Y,Z)_  and is expanded in the same way as a _nonlinear term_.

##### Augmentation of a nonlinear term


**Original matrix structure** 



|  | ___=___ | 
---------- |  ---------- | 
___R___ | _F(X,Y,Z)_ | 


The column name _=_  is a reserved name for a column which has a fixed activity of 1.0 and can conveniently be used to hold nonlinear terms, particularly those which cannot be expressed as coefficients of variables.

  

**Matrix structure: all augmentations** 



|  | ___=___ | ___X___ | ___Y___ | ___Z___ | ___dX___ | ___dY___ | ___dZ___ | 
---------- |  ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | 
___R___ | _F\(X<sub>0</sub>,Y<sub>0</sub>,Z<sub>0</sub>\)_ |  |  |  | _F'<sub>x</sub>\(X<sub>0</sub>,Y<sub>0</sub>,Z<sub>0</sub>\)_ | _F'<sub>y</sub>\(X<sub>0</sub>,Y<sub>0</sub>,Z<sub>0</sub>\)_ | _F'<sub>z</sub>\(X<sub>0</sub>,Y<sub>0</sub>,Z<sub>0</sub>\)_ | 
___uX___ |  | _1_ |  |  | _-1_ |  |  | _=_ | _X<sub>0</sub>_ | 
___uY___ |  |  | _1_ |  |  | _-1_ |  | _=_ | _Y<sub>0</sub>_ | 
___uZ___ |  |  |  | _1_ |  |  | _-1_ | _=_ | _Z<sub>0</sub>_ | 


The original nonlinear coefficient \(=,R\) is replaced by its evaluation using the assumed values of the independent variables.

Two vectors and one equality constraint for each independent variable in the coefficient are created if they do not already exist.

The new vectors are:
 * The SLP variable \(e.g. _Y_ \)
 * The SLP delta variable \(e.g. _dY_ \)


The new constraint is the SLP update row \(e.g. _uY_ \) and is always an equality. The only entries in the update row are the +1 and -1 for the SLP variable and delta variable respectively. The right hand side is the assumed value for the SLP variable.

The entry in the original nonlinear constraint row for each independent variable is the first-order partial derivative of the term _F(X,Y,Z)_ , evaluated at the assumed values.

The delta variables are bounded by the current values of the corresponding step bounds.

One new vector and one new equality constraint are created for the variable containing the nonlinear coefficient.

The new vector is:
 * The SLP delta variable \(e.g. _dX_ \)


The new constraint is the SLP update row \(e.g. _uX_ \) and is always an equality. The only entries in the update row are the +1 and -1 for the original variable and delta variable respectively. The right hand side is the assumed value for the original variable.

The delta variable is bounded by the current values of the corresponding step bounds.

Note that if F\(X,Y,Z\) = X\*F\(Y,Z\) then this translation is exactly equivalent to that for the nonlinear coefficient described earlier.

##### Augmentation of a user-defined SLP variable


Typically, this will arise when a variable represents the result of a nonlinear function, and is required to converge, or to be constrained by step-bounding to force convergence. In essence, it would arise from a relationship of the form

 _X = F(Y,Z)_ 

  

**Original matrix structure** 



|  | ___=___ | ___X___ | 
---------- |  ---------- | ---------- | 
___R___ | _F(Y,Z)_ | _-1_ | 


  

**Matrix structure: all augmentations** 



|  | ___=___ | ___X___ | ___Y___ | ___Z___ | ___dX___ | ___dY___ | ___dZ___ | 
---------- |  ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | 
___R___ | _F\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | _-1_ |  |  |  | _F'<sub>y</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | _F'<sub>z</sub>\(Y<sub>0</sub>,Z<sub>0</sub>\)_ | 
___uX___ |  | _1_ |  |  | _-1_ |  |  | _=_ | _X<sub>0</sub>_ | 
___uY___ |  |  | _1_ |  |  | _-1_ |  | _=_ | _Y<sub>0</sub>_ | 
___uZ___ |  |  |  | _1_ |  |  | _-1_ | _=_ | _Z<sub>0</sub>_ | 


The Y,Z structures are identical to those which would result from a nonlinear term or coefficient. The X, dX and uX structures effectively define dX as the deviation of X from X0 which can be controlled with step bounds.

The augmented and even-handed structures include more delta vectors, and so allow for more measurement and control of convergence.

  



__Type of structure__ | __Minimal__ | __Standard__ | __Even-handed__ | 
---------- |  ---------- | ---------- | ---------- | 
__Type of variable__ | 
__Variables in nonlinear coefficients__ | Y | Y | Y | 
__Variables with nonlinear coefficients__ | N | Y | Y | 
__User-defined SLP variable__ | Y | Y | Y | 
__Nonlinear term__ | Y | Y | Y | 


 * `Y`: SLP variable has a delta vector which can be measured and/or controlled for convergence.
 * `N`: SLP variable does not have a delta and cannot be measured and/or controlled for convergence.

There is no mathematical difference between the augmented and even-handed structures.

The even-handed structure is more elegant because it treats all variables in an identical way. However, the original coefficients are lost, because their effect is transferred to the "=" column as a term and so it is not possible to look up the coefficient value in the matrix after the SLP solution process has finished \(whether because it has converged or because it has terminated for some other reason\). The values of the SLP variables are still accessible in the usual way.

Some of the extended convergence criteria will be less effective because the effects of the individual coefficients may be amalgamated into one term \(so, for example, the total positive and negative contributions to a constraint are no longer available\).

##### SLP penalty error vectors


Bits 2, 3 and 9 of control variable `XSLP_AUGMENTATION` determine whether SLP penalty error vectors are added to constraints. Bit 9 applies penalty error vectors to all constraints; bits 2 and 3 apply them only to constraints containing nonlinear terms. When bit 2 or bit 3 is set, two penalty error vectors are added to each such equality constraint; when bit 3 is set, one penalty error vector is also added to each such inequality constraint. The general form is as follows:

  

**Original matrix structure** 



|  | ___=___ | 
---------- |  ---------- | 
___R___ | _F(Y,Z)_ | 


  

**Matrix structure with error vectors** 



|  | ___X___ | ___R+___ | ___R-___ | 
---------- |  ---------- | ---------- | ---------- | 
___R___ | _F(Y,Z)_ | _+1_ | _-1_ | 
___P_ERROR___ |  | _+Weight_ | _+Weight_ | 


For equality rows, two penalty error vectors are added. These have penalty weights in the penalty error row _P_ERROR_ , whose total is transferred to the objective with a cost of `XSLP_CURRENTERRORCOST`. For inequality rows, only one penalty error vector is added— the one corresponding to the slack is omitted. If any error vectors are used in a solution, the transfer cost from the cost penalty error row will be increased by a factor of `XSLP_ERRORCOSTFACTOR` up to a maximum of `XSLP_ERRORMAXCOST`.

Error vectors are ignored when calculating cascaded values.

The presence of error vectors at a non-zero level in an SLP solution normally indicates that the solution is not self-consistent and is therefore not a solution to the nonlinear problem.

Control variable `XSLP_ERRORTOL_A` is a tolerance on error vectors. Any error vector with a value less than `XSLP_ERRORTOL_A` will be regarded as having a value of zero.

Bit 9 controls whether error vectors are added to all constraints. If bit 9 is set, then error vectors are added in the same way as for the setting of bit 3, but to all constraints regardless of whether or not they have nonlinear coefficients.

#### Section 12.2 Xpress-SLP Matrix Name Generation


Xpress-SLP adds rows and columns to the nonlinear problem in order to create a linear approximation. The new rows and columns are given names derived from the row or column to which they are related as follows:



__Row or column type__ | __Control parameter containing format__ | __Default format__ | 
---------- |  ---------- | ---------- | 
__Update row__ | `XSLP_UPDATEFORMAT` | pU\_r | 
__Delta vector__ | `XSLP_DELTAFORMAT` | pD\_c | 
__Penalty delta \(below step bound\)__ | `XSLP_MINUSDELTAFORMAT` | pD-c | 
__Penalty delta \(above step bound\)__ | `XSLP_PLUSDELTAFORMAT` | pD+c | 
__Penalty error \(below RHS\)__ | `XSLP_MINUSERRORFORMAT` | pE-r | 
__Penalty error \(above RHS\)__ | `XSLP_PLUSERRORFORMAT` | pE+r | 
__Row for total of all penalty vectors \(error or delta\)__ | `XSLP_PENALTYROWFORMAT` | pPR\_x | 
__Column for standard penalty cost \(error or delta\)__ | `XSLP_PENALTYCOLFORMAT` | pPC\_x | 
__LO step bound formulated as a row__ | `XSLP_SBLOROWFORMAT` | pSB-c | 
__UP step bound formulated as a row__ | `XSLP_SBUPROWFORMAT` | pSB+c | 


In the default formats:


 * `p`: a unique prefix \(one or more characters not used as the beginning of any name in the problem\).
 * `r`: the original row name.
 * `c`: the original column name.
 * `x`: The penalty row and column vectors are suffixed with "ERR" or "DELT" \(for error and delta respectively\).
Other characters appear "as is".

The format of one of these generated names can be changed by setting the corresponding control parameter to a formatting string using standard "C"-style conventions. In these cases, the unique prefix is not available and the only obvious choices, apart from constant names, use "% s" to include the original name— for example:

  _U\_% s_ would create names like `U_abcdefghi`

  _U\_% -8s_would create names like `U_abcdefgh`\(always truncated to 8 characters\).

You can use a part of the name by using the `XSLP_*OFFSET` control parameters \(such as `XSLP_UPDATEOFFSET`\) which will offset the start of the original name by the number of characters indicated \(so, setting `XSLP_UPDATEOFFSET` to 1 would produce the name `U_bcdefghi`\).

#### Section 12.3 Xpress-SLP Statistics


When a matrix is read in using `XSLPreadprob`, statistics on the model are produced. They should be interpreted as described in the numbered footnotes:

```

Reading Problem xxx                                               (1)
Problem Statistics
        1920 (      0 spare) rows                                 (2)
         899 (      0 spare) structural columns                   (3)
        6683 (   3000 spare) non-zero elements                    (4)
MIP Entity Statistics
      0 entities   0 sets    0 set members                        (5)
Xpress-SLP Statistics:
        3632 coefficients                                         (6)
          14 extended variable arrays                             (7)
           1 user functions                                       (8)
        1011 SLP variables                                        (9)

```


Notes:

 1. Standard output from `XPRSreadprob` reading the linear part of the problem
 2. Number of rows declared in the ROWS section
 3. Number of columns with at least one constant coefficient
 4. Number of constant elements
 5. Integer and SOS statistics if appropriate
 6. Number of non-constant coefficients
 7. Number of XVs defined
 8. Number of user functions defined
 9. Number of variables identified as SLP variables \(interacting with a non-linear coefficient\)

When the original problem is augmented prior to optimization, the following statistics are produced:

```

Xpress-SLP Augmentation Statistics:	
  Columns:	
         754 implicit SLP variables                              (10)
        1010 delta vectors                                       (11)
        2138 penalty error vectors (1177 positive, 961 negative) (12)
  Rows:	
        1370 nonlinear constraints                               (13)
        1010 update rows                                         (14)
           1 penalty error rows                                  (15)
  Coefficients:	
       11862 non-constant coefficients                           (16)

```


Notes:

 11. SLP variables appearing only in coefficients and having no constant elements
 12. Number of delta vectors created
 13. Numbers of penalty error vectors
 14. Number of constraints containing nonlinear terms
 15. Number of update rows \(equals number of delta vectors\)
 16. Number of rows totaling penalty vectors \(error or delta\)
 17. Number of non-constant coefficients in the linear augmented matrix

If the matrix is read in using the `XPRSloadxxx` and `XSLPloadxxx` functions then these statistics may not be produced. However, most of the values are accessible through Xpress NonLinear integer attributes using the `XSLPgetintattrib` function.

#### Section 12.4 SLP Variable History


Xpress-SLP maintains a history value for each SLP variable. This value indicates the direction in which the variable last moved and the number of consecutive times it moved in the same direction. All variables start with a history value of zero.


__Current History__ | __Change in activity of variable__ | __New History__ | 
---------- |  ---------- | ---------- | 
0 | >0 | 1 | 
0 | <0 | -1 | 
>0 | >0 | No change unless delta vector is at its bound. If it is, then new value is Current History + 1 | 
>0 | <0 | -1 | 
<0 | <0 | No change unless delta vector is at its bound. If it is, then new value is Current History - 1 | 
<0 | >0 | 1 | 
anything | 0 | No change | 

Tests of variable movement are based on comparison with absolute and relative \(and, if set, closure\) tolerances. Any movement within tolerance is regarded as zero.

If the new absolute value of History exceeds the setting of `XSLP_SAMECOUNT`, then the step bound is reset to a larger value \(determined by `XSLP_EXPAND`\) and History is reset as if it had been zero.

If History and the change in activity are of opposite signs, then the step bound is reset to a smaller value \(determined by `XSLP_SHRINK`\) and History is reset as if it had been zero.

With the default settings, History will normally be in the range -1 to -3 or +1 to +3.

### Chapter 13 Xpress NonLinear Formulae


Xpress NonLinear can handle formulae described in three different ways:

 * `Character strings`: The formula is written exactly as it would appear in, for example, the Extended MPS format used for text file input.
 * Internal unparsed format: The tokens within the formula are replaced by a
   *   _\{token type, token value\}_ pair. The list of types and values is in the table below.
 * Internal parsed format: The tokens are converted as in the unparsed format, but the order is changed so that the resulting array forms a reverse-Polish execution stack for direct evaluation by the system.

#### Section 13.1 Parsed and unparsed formulae


All formulae input into Xpress NonLinear are parsed into a reverse-Polish execution stack. Tokens are identified by their type and a value. The table below shows the values used in interface functions.

All formulae are provided in the interface functions as two parallel arrays:

 an integer array of token types;

 a double array of token values.

The last token type in the array should be an end-of-formula token \( `XSLP_EOF`, which evaluates to zero\).

If the value required is an integer, it should still be provided in the array of token values as a double precision value.

Even if a token type requires no token value, it is best practice to initialize such values as zeros. In particular, any other provided values will generally not be preserved when queried later.


__Type__ | __Description__ | __Value__ | 
---------- |  ---------- | ---------- | 
`XSLP_COL` | column | index of matrix column. | 
`XSLP_CON` | constant | \(double\) value. | 
`XSLP_DEL` | delimiter | `XSLP_COMMA`\(1\) = comma \(","\) | 
| `` |  | `XSLP_COLON`\(2\) = colon \(":"\) | 
`XSLP_EOF` | end of formula | not required: use zero | 
`XSLP_FUN` | user function | index of function | 
`XSLP_IFUN` | internal function | index of function | 
`XSLP_LB` | left bracket | not required: use zero | 
`XSLP_OP` | operator | `XSLP_UMINUS`\(1\) = unary minus \("-"\) | 
| `` |  | `XSLP_EXPONENT`\(2\) = exponent \("\*\*" or "^"\) | 
| `` |  | `XSLP_MULTIPLY`\(3\) = multiplication \("\*"\) | 
| `` |  | `XSLP_DIVIDE`\(4\) = division \("/"\) | 
| `` |  | `XSLP_PLUS`\(5\) = addition \("+"\) | 
| `` |  | `XSLP_MINUS`\(6\) = subtraction \("-"\) | 
`XSLP_RB` | right bracket | not required: use zero | 

When a formula is passed to Xpress NonLinear in "internal unparsed format"— that is, with the formula already converted into tokens— the full range of token types is permitted.

When a formula is passed to Xpress NonLinear in "parsed format"— that is, in reverse Polish— the following rules apply:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XSLP_DEL` | comma is optional. | 
`XSLP_FUN` | implies a following left-bracket, which is not included explicitly. | 
`XSLP_IFUN` | implies a following left-bracket, which is not included explicitly. | 
`XSLP_LB` | never used. | 
`XSLP_RB` | only used to terminate the list of arguments to a function. | 


Brackets are not used in the reverse Polish representation of the formula: the order of evaluation is determined by the order of the items on the stack. Functions which need the brackets—for example `XPRSslpgetcoefstr`—fill in brackets as required to achieve the correct evaluation order. The result may not match the formula as originally provided.

#### Section 13.2 Example of an arithmetic formula


_x<sup>2</sup>+4y\(z-3\)_ 

Written as an unparsed formula, each token is directly transcribed as follows:



__Type__ | __Value__ | 
---------- |  ---------- | 
`XSLP_COL` | index of `x` | 
`XSLP_OP` | `XSLP_EXPONENT` | 
`XSLP_CON` | 2 | 
`XSLP_OP` | `XSLP_PLUS` | 
`XSLP_CON` | 4 | 
`XSLP_OP` | `XSLP_MULTIPLY` | 
`XSLP_COL` | index of `y` | 
`XSLP_OP` | `XSLP_MULTIPLY` | 
`XSLP_LB` | 0 | 
`XSLP_COL` | index of `z` | 
`XSLP_OP` | `XSLP_MINUS` | 
`XSLP_CON` | 3 | 
`XSLP_RB` | 0 | 
`XSLP_EOF` | 0 | 


Written as a parsed formula \(in reverse Polish\), an evaluation order is established first, for example:

_x 2 ^ 4 y \* z 3 - \* +_ 

and this is then transcribed as follows:



__Type__ | __Value__ | 
---------- |  ---------- | 
`XSLP_COL` | index of `x` | 
`XSLP_CON` | 2 | 
`XSLP_OP` | `XSLP_EXPONENT` | 
`XSLP_CON` | 4 | 
`XSLP_COL` | index of `y` | 
`XSLP_OP` | `XSLP_MULTIPLY` | 
`XSLP_COL` | index of `z` | 
`XSLP_CON` | 3 | 
`XSLP_OP` | `XSLP_MINUS` | 
`XSLP_OP` | `XSLP_MULTIPLY` | 
`XSLP_OP` | `XSLP_PLUS` | 
`XSLP_EOF` | 0 | 


Notice that the brackets used to establish the order of evaluation in the unparsed formula are not required in the parsed form.

#### Section 13.3 Example of a formula involving a simple function


_y*MyFunc(z,3)_ 

Written as an unparsed formula, each token is directly transcribed as follows:



__Type__ | __Value__ | 
---------- |  ---------- | 
`XSLP_COL` | index of `y` | 
`XSLP_OP` | `XSLP_MULTIPLY` | 
`XSLP_FUN` | index of `MyFunc` | 
`XSLP_LB` | 0 | 
`XSLP_COL` | index of `z` | 
`XSLP_DEL` | `XSLP_COMMA` | 
`XSLP_CON` | 3 | 
`XSLP_RB` | 0 | 
`XSLP_EOF` | 0 | 


Written as a parsed formula \(in reverse Polish\), an evaluation order is established first, for example:

_y \) 3 , z MyFunc\( \*_ 

and this is then transcribed as follows:



__Type__ | __Value__ | 
---------- |  ---------- | 
`XSLP_COL` | index of `y` | 
`XSLP_RB` | 0 | 
`XSLP_CON` | 3 | 
`XSLP_DEL` | `XSLP_COMMA` | 
`XSLP_COL` | index of `z` | 
`XSLP_FUN` | index of `MyFunc` | 
`XSLP_OP` | `XSLP_MULTIPLY` | 
`XSLP_EOF` | 0 | 


Notice that the function arguments are in reverse order, and that a right bracket is used as a delimiter to indicate the end of the argument list. The left bracket indicating the start of the argument list is implied by the `XSLP_FUN` token.

### Chapter 14 User Functions


#### Section 14.1 Callbacks and user functions


Callbacks and user functions both provide mechanisms for connecting user-written functions to Xpress NonLinear. However, they have different capabilities and are not interchangeable.

A _callback_ is called at a specific point in the SLP optimization process \(for example, at the start of each SLP iteration\). It has full access to all the problem data and can, in principle, change the values of any items— although not all such changes will necessarily be acted upon immediately or at all.

A _user function_ is essentially the same as any other mathematical function, used in a formula to calculate the current value of a coefficient. The function is called when a new value is needed; for efficiency, user functions are usually not called if the value is already known \(for example, when all function arguments stay the same between two SLP iterations\). Therefore, there is no guarantee that a user function will be called at any specific point in the optimization procedure or at all.

Although a user function is normally free-standing and needs no access to problem or other data apart from that which it receives through its argument list, there are facilities to allow it to access the problem and its data if required. The following limitations should be observed:
 1. The function should not make use of any variable data which is not in its list of arguments;
 2. The function should not change any of the problem data.


The reasons for these restrictions are as follows:
 1. Xpress NonLinear determines which variables are linked to a formula by examining the list of variables and arguments to functions in the formula. In particular it may store previous arguments and results for user function calls to avoid unnecessary recomputations as explained above, and if a user function depended on additional variables, then a recalculation might not be requested even though a different result could be obtained.
 2. Xpress NonLinear generally allows problem data to be changed between function calls, and also by callbacks called from within an Xpress NonLinear function. However, user functions are called at various points during the optimization and no checks are generally made to see if any problem data has changed. The effects of any such changes will therefore at best be unpredictable.


For a description of how to access the problem data from within a user function, see the section on "More complicated user functions" later in this chapter.

#### Section 14.2 User function interface


In its simplest form, a user function is exactly the same as any other mathematical function: it takes a set of arguments \(constants or values of variables\) and returns a value as its result. In this form, which is the usual implementation, the function needs no information apart from the values of its arguments. It is possible to create more complicated functions which do use external data in some form.

Xpress NonLinear distinguishes six different types of user functions.

 * A user function is called a `map`, if it takes and returns a single value.
 * A user function is called a `mapvec`, if it takes an array of inputs, and returns a single evaluation value.
 * A user function is called a `multimap`, if it takes an array of inputs, and also returns an array of evaluation values.
 * A `mapdelta` user function is an extended version of a `map` that also returns its own partial derivatives when requested
 * A `mapvecdelta` user function is an extended version of a `mapvec` that also returns its own partial derivatives when requested
 * A `multimapdelta` user function is an extended version of a `multimap` that also returns its own partial derivatives when requested

#### Section 14.3 User Function declaration in native languages


This section describes how to declare a user function in C. The general shape of the declaration is shown. Not all the possible arguments will necessarily be used by any particular function, and the actual arguments required will depend on the way the function is declared to Xpress NonLinear.

##### User function declaration in C


If the function is placed in a library, `XSLPimportlibfunc` may be used to retrieve a pointer to be passed to `XSLPadduserfunction`.

A user function can be included in the executable program which calls Xpress NonLinear.

A multimapdelta function's `Deltas` is an array with the same number of items as `Value`. It is used as an indication of which derivatives \(if any\) are required on a particular function call. If `Deltas[i]` is zero then a derivative for input variable `i` is not required and does not need to be computed. If `Deltas[i]` is nonzero then a derivative for input variable `i` is required and must be returned.

The return values array contains the values and the derivatives \(if requested, otherwise these entries will be stepped over\) as follows \( `DVi` is the i<sup>th</sup> input variable of the user function\):

  `Result1`

 Derivative of `Result1`w.r.t. `DV1`

 Derivative of `Result1`w.r.t. `DV2`

  `...`

 Derivative of `Result1`w.r.t. `DVn`

  `Result2`

 Derivative of `Result2`w.r.t. `DV1`

 Derivative of `Result2`w.r.t. `DV2`

  `...`

 Derivative of `Result2`w.r.t. `DVn`

  `...`

 Derivative of `Resultm`w.r.t. `DVn`

The return value of the user functions that return an int \(as opposed to the evaluation value\) is a status code indicating whether the function has completed normally. Possible values are:
 * `0`: No errors: the function has completed normally.
 * `1`: The function has encountered an error. This will terminate the optimization.
 * `-1`: The calling function must estimate the function value from the last set of values calculated. This will cause an error if no values are available.


#### Section 14.4 Programming Techniques for User Functions


This section is principally concerned with the programming of large or complicated user functions, perhaps taking a potentially large number of input values and calculating a large number of results. However, some of the issues raised are also applicable to simpler functions.

The first part describes in more detail some of the possible arguments to the function. The remainder of the section looks at function instances, function objects and direct calls to user functions.

##### Deltas


The `Deltas` array has the same dimension as `Value` and is used to indicate which of the input variables should be used to calculate derivatives. If `Deltas[i]` is zero, then `Partials[i]` does not need to be populated. If `Deltas[i]` is nonzero, then a derivative is required for input variable `i`. The value of `Deltas[i]` can be used as a suggested perturbation for numerical differentiation \(a negative sign indicates that if a one-sided derivative is calculated, then a backward one is preferred\). If derivatives are calculated analytically, or without requiring a specific perturbation, then `Deltas` can be interpreted simply as an array of flags indicating which derivatives are required.

##### Returning Derivatives


A multi-valued function which does not calculate its own derivatives will return its results as a one-dimensional array.

As already described, when derivatives are calculated as well, the order is changed, so that the required derivatives follow the value for each result. That is, the order becomes:

 _A,\(∂A\) / \(∂X<sub>1</sub>\),\(∂A\) / \(∂X<sub>2</sub>\), ...\(∂A\) / \(∂X<sub>n</sub>\)_ , _B,\(∂B\) / \(∂X<sub>1</sub>\),\(∂B\) / \(∂X<sub>2</sub>\), ...\(∂B\) / \(∂X<sub>n</sub>\), ...\(∂Z\) / \(∂X<sub>n</sub>\)_ 

where _A_ , _B_ , _Z_ are the return values, and _X<sub>1</sub>_ , _X<sub>2</sub>_ , _X<sub>n</sub>_ , are the input \(independent\) variables \(in order\). Only the entries for variables for which derivatives have been requested need to be filled.

Not all calls to a user function necessarily require derivatives to be calculated. If `Deltas` is NULL, no derivatives are required, otherwise the nonzero elements of `Deltas` determine which derivatives are requested as explained above.

##### Function Instances


Xpress NonLinear defines an _instance_ of a user function to be a unique combination of function and arguments. For functions which return an array of values, the specific return argument is ignored when determining instances. Thus, given the following formulae:

  _f(x) + f(y) + g(x,y : 1)_ 

  _f(y)*f(x)*g(x,y : 2)_ 

  _f(z)_ 

the following instances are created:

 _f(x)_ 

 _f(y)_ 

 _f(z)_ 

 _g(x,y)_ 

\(A function reference of the form _g(x,y:n)_ means that _g_ is a multi-valued function of _x_ and _y_ , and we want the n<sup>th</sup>return value.\)

Xpress NonLinear regards as _complicated_ any user function which returns more than one value, which uses input or return names, or which calculates its own derivatives. All complicated functions give rise to function instances, so that each function is called only once for each distinct combination of arguments.

Functions which are not regarded as complicated are normally called each time a value is required.

Note that conditional re-evaluation of the function is only possible if it generates function instances.

Using function instances can improve the performance of a problem, because the function is called only once for each combination of arguments, and is not re-evaluated if the values have not changed significantly. If the function is computationally intensive, the improvement can be significant.

Xpress NonLinear normally expects to obtain a set of partial derivatives from a user function at a particular base-point and then to use them as required, depending on the evaluation settings for the various functions. If for any reason this is not appropriate, then the integer control parameter `XSLP_EVALUATE` can be set to 1, which will force re-evaluation every time.

A function instance is not re-evaluated if all of its arguments are unchanged.

A simple function which does not have a function instance is evaluated every time.

If `XSLP_EVALUATE` is not set, then it is still possible to by-pass the re-evaluation of a function if the values have not changed significantly since the last evaluation. If the input values to a function have all converged to within their strict convergence tolerance \( `CTOL`, `ATOL_A`, `ATOL_R`\), and bit 4 of `XSLP_FUNCEVAL` is set to 1, then the existing values and derivatives will continue to be used. At the option of the user, an individual function, or all functions, can be re-evaluated in this way or at each SLP iteration. If a function is not re-evaluated, then all the required values will be calculated from the base point and the partial derivatives; the input and return values used in making the original function calculation are unchanged.

Bits 3-5 of integer control parameter `XSLP_FUNCEVAL` determine the nature of function evaluations. The meaning of each bit is as follows:
 * __Bit 3__: evaluate functions whenever independent variables change.
 * __Bit 4__: evaluate functions when independent variables change outside tolerances.
 * __Bit 5__: apply evaluation mode to all functions.
 If bits 3-4 are zero, then the settings for the individual functions are used.

If bit 5 is zero, then the settings in bits 3-4 apply only to functions which do not have their own specific evaluation modes set.

**Examples:** 


 * _Bits 3-5 = 1 \(set bit 3\)_: Evaluate functions whenever their input arguments \(independent variables\) change, unless the functions already have their own evaluation options set.
 * _Bits 3-5 = 5 \(set bits 3 and 5\)_: Evaluate all functions whenever their input arguments \(independent variables\) change.
 * _Bits 3-5 = 6 \(set bits 4 and 5\)_: Evaluate functions whenever input arguments \(independent variables\) change outside tolerance. Use existing calculation to estimate values otherwise.


Bits 6-8 of integer control parameter `XSLP_FUNCEVAL` determine the nature of derivative calculations. The meaning of each bit is as follows:
 * __Bit 6__: tangential derivatives.
 * __Bit 7__: forward derivatives.
 * __Bit 8__: apply evaluation mode to all functions.
 If bits 6-7 are zero, then the settings for the individual functions are used.

If bit 8 is zero, then the settings in bits 6-7 apply only to functions which do not have their own specific derivative calculation modes set.

**Examples:** 


 * _Bits 6-8 = 1 \(set bit 6\)_: Use tangential derivatives for all functions which do not already have their own derivative options set.
 * _Bits 6-8 = 5 \(set bits 6 and 8\)_: Use tangential derivatives for all functions.
 * _Bits 6-8 = 6 \(set bits 7 and 8\)_: Use forward derivatives for all functions.


The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 3 | `XSLP_RECALC` | 
Setting bit 4 | `XSLP_TOLCALC` | 
Setting bit 5 | `XSLP_ALLCALCS` | 
Setting bit 6 | `XSLP_2DERIVATIVE` | 
Setting bit 7 | `XSLP_1DERIVATIVE` | 
Setting bit 8 | `XSLP_ALLDERIVATIVES` | 


When analytical derivatives are used, for user functions not returning their own derivatives, SLP will calculate approximated derivatives using finite differences for instantiated functions and use these values when deriving analytical derivatives.

### Chapter 15 Management of zero placeholder entries


#### Section 15.1 The augmented matrix structure


During the augmentation process, Xpress-SLP builds additional matrix structure to represent the linear approximation of the nonlinear constraints within the problem \(see [Xpress-SLP Structures](#chapStructures)\). In effect, it adds a generic structure which approximates the effect of changes to variables in nonlinear expressions, over and above that which would apply if the variables were simply replaced by their current values.

As a very simple example, consider the nonlinear constraint \( _R1_ , say\)

 _X \* Y≤10_ 

The variables _X_  and _Y_  are replaced by _X<sub>0</sub>+δX_  and _Y<sub>0</sub>+δY_  respectively, where _X<sub>0</sub>_  and _Y<sub>0</sub>_  are the values of _X_  and _Y_  at which the approximation will be made.

The original constraint is therefore

 _\(X<sub>0</sub>+δX\)\*\(Y<sub>0</sub>+δY\)≤10_ 

Expanding this into individual terms, we have

 _X<sub>0</sub>\*Y<sub>0</sub>+ X<sub>0</sub>\*δY + Y<sub>0</sub>\*δX +δX\*δY≤10_ 

The first term is constant, the next two terms are linear in _δY_  and _δX_  respectively, and the last term is nonlinear.

The augmented structure deletes the nonlinear term, so that the remaining structure is a linear approximation to the original constraint. The justification for doing this is that if _δX_  or _δY_  \(or both\) are small, then the error involved in ignoring the term is also small.

The resulting matrix structure has entries of _Y<sub>0</sub>_  in the delta variable _δX_  and _X<sub>0</sub>_  in the delta variable _δY_ . The constant entry _X<sub>0</sub>\*Y<sub>0</sub>_  is placed in the special "equals" column which has a fixed activity of 1. All these entries are updated at each SLP iteration as the solution process proceeds and the problem is linearized at a new point. The positions of these entries– _\(R1,δX\)_ , _\(R1,δY\)_  and _(R1,=)_ – are known as _placeholders_.

#### Section 15.2 Derivatives and zero derivatives


At each SLP iteration, the values of the placeholders are re-calculated. In the example in the previous section, the values _X<sub>0</sub>_  in the delta variable _δY_  and _Y<sub>0</sub>_  in the delta variable _δX_  were effectively determined by analytic methods– that is, we differentiated the original formula to determine what values would be required in the placeholders.

In general, analytic differentiation may not be possible: the formula may contain functions which cannot be differentiated \(because, for example, they are not smooth or not continuous\), or for which the analytic derivatives are not known \(because, for example, they are functions providing values from "black boxes" such as databases or simulators\). In such cases, Xpress-SLP approximates the differentiation process by numerical methods. The example in the previous section would have approximate derivatives calculated as follows:

The current value of _X_  \( _X<sub>0</sub>_ \) is perturbed by a small amount \( _dX_ \), and the value of the formula is recalculated in each case.

_f<sub>d</sub>= \(X<sub>0</sub>- dX\) \* Y<sub>0</sub>_ 

 _f<sub>u</sub>= \(X<sub>0</sub>+ dX\) \* Y<sub>0</sub>_ 

_derivative = \(f<sub>u</sub>- f<sub>d</sub>\) / \( 2 \* dX\)_ 

In this particular example, the value obtained by numerical methods is the same as the analytic derivative. For more complex functions, there may be a slight difference, depending on the magnitude of _dX_ .

This derivative represents the effect on the constraint of a change in the value of _X_ . Obviously, if _Y_  changes as well, then the combined effect will not be fully represented although, in general, it will be directionally correct.

The problem comes when _Y<sub>0</sub>_  is zero. In such a case, the derivative is calculated as zero, meaning that changing _X_  has no effect on the value of the formula. This can impact in one of two ways: either the value of _X_  never changes because there is no incentive to do so, or it changes by unreasonably large amounts because there is no effect from doing so. If _X_  and _Y_  are linked in some other way, so that _Y_  becomes nonzero when _X_  changes, the approximation using zero as the derivative can cause the optimization process to behave badly.

Xpress-SLP tries to avoid the problem of zero derivatives by using small nonzero values for variables which are in fact zero. In most cases this gives a small nonzero value for the derivative, and hence for the placeholder entry. The model then contains some effect for the change in a variable, even if instantaneously the effect is zero.

The same principle is applied to analytic derivatives, so that the values obtained by either method are broadly similar.

#### Section 15.3 Placeholder management


The default action of Xpress-SLP is to retain all the calculated values for all the placeholder entries. This includes values which would be zero without the special handling described in the previous section. We will call such values "zero placeholders".

Although retaining all the values gives the best chance of finding a good optimum, the presence of a large dense area of small values often gives rise to considerable numerical instability which adversely affects the optimization process. Xpress-SLP therefore offers a way of deleting small values which is less likely to affect the final outcome whilst improving numerical stability.

Most of the candidate placeholders are in the delta variables \(represented by the _δX_  and _δY_  variables above\). Various criteria can be selected for deletion of zero placeholder entries without affecting the validity of the basis \(and so making the next SLP iteration more costly in time and stability\). The criteria are selected using the control parameter `XSLP_ZEROCRITERION` as follows:

 * **Bit 0 (=1)**  Remove placeholders in nonbasic SLP variables
   *  This criterion applies to placeholders which are in the SLP variable \(not the delta\). Any value can be deleted from a nonbasic variable without upsetting the basis, so all eligible zero placeholders can be deleted.

 * **Bit 1 (=2)**  Remove placeholders in nonbasic delta variables
   *  Any value can be deleted from a nonbasic variable without upsetting the basis, so all eligible zero placeholders can be deleted.

 * **Bit 2 (=4)**  Remove placeholders in a basic SLP variable if its update row is nonbasic
   *  If the update row is nonbasic, then generally the basic SLP variable can be pivoted in the update row, so the basis is still valid if other entries are deleted. The entry in the update row is always 1.0 and will never be deleted.

 * **Bit 3 (=8)**  Remove placeholders in a basic delta variable if its update row is nonbasic and the corresponding SLP variable is nonbasic
   *  If the delta is basic and the corresponding SLP variable is nonbasic, then the delta will pivot in the update row \(the delta and the SLP variable are the only two variables in the update row\), so the basis is still valid if other entries are deleted. The entry in the update row is always -1.0 and will never be deleted.

 * **Bit 4 (=16)**  Remove placeholders in a basic delta variable if the determining row for the corresponding SLP variable is nonbasic
   *  If the delta variable is basic and the determining row for the corresponding SLP variable is nonbasic then it is generally possible \(although not 100%guaranteed\) to pivot the delta variable in the determining row. so the basis is still valid if other entries are deleted. The entry in the determining row is never deleted even if it is otherwise eligible.

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_ZEROCRTIERION_NBSLPVAR` | 
Setting bit 1 | `XSLP_ZEROCRTIERION_NBDELTA` | 
Setting bit 2 | `XSLP_ZEROCRTIERION_SLPVARNBUPDATEROW` | 
Setting bit 3 | `XSLP_ZEROCRTIERION_DELTANBUPSATEROW` | 
Setting bit 4 | `XSLP_ZEROCRTIERION_DELTANBDRROW` | 


There are two additional control parameters used in this procedure:

 * `XSLP_ZEROCRITERIONSTART`
   *  This is the first SLP iteration at which zero placeholders will be examined for eligibility. Use of this parameter allows a balance to be made between optimality and numerical stability.

 * `XSLP_ZEROCRITERIONCOUNT`
   *  This is the number of consecutive SLP iterations that a placeholder is a zero placeholder before it is deleted. So, if in the earlier example `XSLP_ZEROCRITERIONCOUNT`is 2, the entry in the delta variable _dX_ will be deleted only if _Y_ was also zero on the previous SLP iteration.

Regardless of the basis status of a variable, its delta, update row and determining row, if a zero placeholder was deleted on the previous SLP iteration, it will always be deleted in the current SLP iteration \(keeping a zero matrix entry at zero does not upset the basis\).

If the optimization method is barrier, or the basis is not being used, then the bit settings of `XSLP_ZEROCRITERION` are not used as such: if `XSLP_ZEROCRITERION` is nonzero, all zero placeholders will be deleted subject to `XSLP_ZEROCRITERIONCOUNT` and `XSLP_ZEROCRITERIONSTART`.

### Chapter 16 Special Types of Problem


#### Section 16.1 Nonlinear objectives


Xpress NonLinear works with nonlinear constraints. If a nonlinear objective is required \(except for the special case of a quadratic objective— see below\) then the objective should be provided using a constraint in the problem. For example, to optimize `f(x)` where `f` is a nonlinear function and `x` is a set of one or more variables, create the constraint

_f\(x\) - X = 0_

where `X` is a new variable, and then optimize `X`.

In general, `X` should be made a free variable, so that the problem does not converge prematurely on the basis of an unchanging objective function. It is generally important that the objective is not artificially constrained \(for example, by bounding `X`\) because this can distort the solution process. Also, as such an objective transfer row is not a real constraint, no error vectors should be added \(row can be enforced\); feasibility should be provided by the transfer variable `X` being free.

#### Section 16.2 Convex Quadratic Programming


Convex quadratic programming \(QP\) is a special case of nonlinear programming where the constraints are linear but the objective is quadratic \(that is, it contains only terms which are constant, variables multiplied by a constant, or products of two variables multiplied by a constant\) and convex \(convexity is checked by the Xpress Optimizer\). It is possible to solve convex quadratic problems using SLP, but it is not usually the best way. The reason is that the solution to a convex QP problem is typically not at a vertex. In SLP a non-vertex solution is achieved by applying step bounds to create additional constraints which surround the solution point, so that ultimately the solution has been obtained within suitable tolerances. Because of the nature of the problem, successive solutions will often swing from one step bound to the other; in such circumstances, the step bounds are reduced on each SLP iteration but it will still take a long time before convergence. In addition, unless the linear approximation is adequately constrained, it will be unbounded because the linear approximation will not recognize the change in direction of the relationship with the derivative as the variable passes through a stationary point. The easiest way to ensure that the linear problem is constrained is to provide realistic upper and lower bounds on all variables.

In Xpress NonLinear, convex quadratic problems can be solved using the quadratic optimizer within the Xpress optimizer package. For pure QP \(or MIQP\) problems, therefore, SLP is not required. However, the SLP algorithm can be used together with QP to solve problems with a quadratic objective and also nonlinear constraints. The constraints are handled using the normal SLP techniques; the objective is handled by the QP optimizer. If the objective is not convex \(not semi-definite\), the QP optimizer may not give a solution \(with default settings, it will produce an error message\); SLP will find a solution but— as always— it may be a local optimum.

If a QP problem is to be solved, then the quadratic component should be input in the normal way \(using `QMATRIX` or `QUADOBJ` in MPS file format, or the library functions `XPRSloadqp` or `XPRSloadmiqp`\). Xpress NonLinear will then automatically use the QP optimizer. If the problem is to be solved using the SLP routines throughout, then the objective should be provided via a constraint as described in the previous section.

This applies to quadratically constrained \(QCQP and MIQCQP\) problems as well.

For a description on when it's more beneficial to use the XPRS library to solve QP or QCQP problems, please see  _Selecting the right algorithm for a nonlinear problem - when to use the XPRS library instead of XSLP_.

#### Section 16.3 Mixed Integer Nonlinear Programming


Mixed Integer Non-Linear Programming \(MINLP\) is the application of mixed integer techniques to the solution of problems including non-linear relationships. Xpress NonLinear offers a set of components to implement MINLP using Mixed Integer Successive Linear Programming \(MISLP\).

##### Mixed Integer SLP


The mixed integer successive linear programming \(MISLP\) solver is a generalization of the traditional branch and bound procedure to nonlinear programming. The MIP engine is used to control the branch-and-bound algorithm, with each node being evaluated using SLP. MIP then compares the SLP solutions at each node to decide which node to explore next, and to decide when an integer feasible and ultimately optimal solution have been obtained.

MISLP, also known as SLP within MIP, offers nonlinear specific root heuristics controlled by control `XSLP_HEURSTRATEGY`.

Other generic heuristics are controlled by the respective XPRS heuristics controls.

The branch and bound tree exploration is executed in parallel. Use the XPRS control MIPTHREADS to limit the number of threads used.

Normally, the relaxed problem is solved first, using `XSLPnlpoptimize` with the `-l` flag to ignore the integer elements of the problem. It is also possible to call the `XSLPnlpoptimize` routine with the `-g` flag and allow it to do the initial SLP optimization as well. In either case, ensure that the control parameter `XSLP_OBJSENSE` is set to +1 \(minimization\) or -1 \(maximization\) before calling `XSLPnlpoptimize`.

The actual algorithm employed is controlled by a number of control parameters, as well as offering the possibility of direct user interaction through call-backs at key points in the solution process.

##### Heuristics for Mixed Integer SLP


For hard MINLP problems, or where a solution must quickly be generated, the root heuristics of MISLP can be executed as stand alone methods. These approaches can be used by changing the value of the control parameter `XSLP_MIPALGORITHM`.

there are two MISLP heuristics:
 1. MIP within SLP. In this, each SLP iteration is optimized using MIP to obtain an integer optimal solution to the linear approximation of the original problem. SLP then compares this MIP solution to the MIP solution of the previous SLP iteration and determines convergence based on the differences between the successive MIP solutions.
 2. SLP then MIP. In this, SLP is used to find a converged solution to the relaxed problem. The resulting linearization is then fixed \(i.e. the base point and the partial derivatives do not change\) and MIP is run to find an integer optimum. SLP is then run again to find a converged solution to the original problem with these integer settings.


The approach described in \(1\) seems potentially dangerous, in that changes in the integer variables could have disproportionate effects on the solution and on the values of the SLP variables. There are also question-marks over the use of step-bounding to control convergence, particularly if any of the integer variables are also SLP variables.

The approach described in \(2\) has the big advantage that MIP is working on a linear problem and so can take advantage of all of the special attributes of such a problem. This means that the solution time is likely to be much faster than the alternatives. However, if the real problem is significantly non-linear, the integer solution to the initial SLP solution may not be a good integer solution to the original problem and so a false optimum may occur.

##### Fixing or relaxing the values of the SLP variables


The solution process may involve step-bounding to obtain the converged solution. Some MIP solution strategies may want to fix the values of some of the SLP variables before moving on to the MIP part of the process, or they may want to allow the child nodes more freedom than would be allowed by the final settings of the step bounds. Control parameters `XSLP_MIPALGORITHM`, `XSLP_MIPFIXSTEPBOUNDS` and `XSLP_MIPRELAXSTEPBOUNDS` can be used to free, or fix to zero, various categories of step bounds, thus effectively freeing the SLP variables or fixing them to their values in the initial solution.

At each node, step bounds may again be fixed to zero or relaxed or left in the same state as in the solution to the parent node.

`XSLP_MIPALGORITHM` uses bits 2-3 \(for the root node\) and 4-5 \(for other nodes\) to determine which step bounds are fixed to zero \(thus fixing the values of the corresponding variables\) or freed \(thus allowing the variables to change, possibly beyond the point they were restricted to in the parent node\).

Set bit 2 \(4\) of `XSLP_MIPALGORITHM`to implement relaxation of defined categories of step bounds as determined by `XSLP_MIPRELAXSTEPBOUNDS`at the root node \(at each node\).

Set bit 3 \(5\) of `XSLP_MIPALGORITHM`to implement fixing of defined categories of step bounds as determined by `XSLP_MIPFIXSTEPBOUNDS`at the root node \(at each node\).

Alternatively, specific actions on setting bounds can be carried out by the user callback defined by `XSLPsetcbprenode`.

The default setting of `XSLP_MIPALGORITHM` is 17 which relaxes step bounds at all nodes except the root node. The step bounds from the initial SLP optimization are retained for the root node.

`XSLP_MIPRELAXSTEPBOUNDS` and `XSLP_MIPFIXSTEPBOUNDS` are bitmaps which determine which categories of SLP variables are processed.

 * `Bit 1`: Process SLP variables which do not appear in coefficients but which do have coefficients \(constant or variable\) in the original problem.
 * `Bit 2`: Process SLP variables which have coefficients \(constant or variable\) in the original problem.
 * `Bit 3`: Process SLP variables which appear in coefficients but which do not have coefficients \(constant or variable\) in the original problem.
 * `Bit 4`: Process SLP variables which appear in coefficients.

In most cases, the default settings \( `XSLP_MIPFIXSTEPBOUNDS` = `0`, `XSLP_MIPRELAXSTEPBOUNDS` = `15`\) are appropriate.

##### Iterating at each node


Any number of SLP iterations can be carried out at each node. The maximum number is set by control parameter `XSLP_MIPITERLIMIT` and is activated by `XSLP_MIPALGORITHM`. The significant values for `XSLP_MIPITERLIMIT` are:

 * `0`: Perform an LP optimization with the current linearization. This means that, subject to the step bounds, the SLP variables can take on other values, but the coefficients are not updated.
 * `1`: As for `0`, but the model is updated after each iteration, so that each node starts with a new linearization based on the solution of its parent.
 * `n>1`: Perform up to `n` SLP iterations, but stop when a termination criterion is satisfied. If no other criteria are set, the SLP will terminate on `XSLP_ITERLIMIT` or `XSLP_MIPITERLIMIT` iterations, or when the SLP converges.

After the last MIP node has been evaluated and the MIP procedure has terminated, the final solution can be re-optimized using SLP to obtain a converged solution. This is only necessary if the individual nodes are being terminated on a criterion other than SLP convergence.

##### Termination criteria at each node


Because the intention at each node is to get a reasonably good estimate for the SLP objective function rather than to obtain a fully converged solution \(which is only required at the optimum\), it may be possible to set looser but practical termination criteria. The following are provided:

**Testing for movement of the objective function** 

This functions in a similar way to the extended convergence criteria for ordinary SLP convergence, but does not require the SLP variables to have converged in any way. The test is applied once step bounding has been applied \(or `XSLP_SBSTART`SLP iterations have taken place if step bounding is not being used\). The node will be terminated at the current iteration if the range of the objective function values over the last _XSLP\_MIPOCOUNT_ SLP iterations is within _XSLP\_MIPOTOL\_A_ or within _XSLP\_MIPOTOL\_R \* OBJ_ where _OBJ_ is the average value of the objective function over those iterations.

**Related control parameters:** 



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XSLP_MIPOTOL_A` | Absolute tolerance | 
`XSLP_MIPOTOL_R` | Relative tolerance | 
`XSLP_MIPOCOUNT` | Number of SLP iterations over which the movement is measured | 


**Testing the objective function against a cutoff** 

If the objective function is worse by a defined amount than the best integer solution obtained so far, then the SLP will be terminated \(and the node will be cut off\). The node will be cut off at the current SLP iteration if the objective function for the last _XSLP\_MIPCUTOFFCOUNT_ SLP iterations are all worse than the best obtained so far, and the difference is greater than _XSLP\_MIPCUTOFF\_A_ and _XSLP\_MIPCUTOFF\_R \* OBJ_ where _OBJ_ is the best integer solution obtained so far.

**Related control parameters:** 



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XSLP_MIPCUTOFF_A` | Absolute amount by which the objective function is worse | 
`XSLP_MIPCUTOFF_R` | Relative amount by which the objective function is worse | 
`XSLP_MIPCUTOFFCOUNT` | Number of SLP iterations checked | 
`XSLP_MIPCUTOFFLIMIT` | Number of SLP iterations before which the cutoff takes effect | 


##### Callbacks


User callbacks are provided as follows:

```
XSLPsetcbintsol(XSLPprob Prob,
                int (*UserFunc)(XSLPprob myProb, void *myObject),
                void *Object);
```


`UserFunc` is called when an integer solution has been obtained. The return value is ignored.

```
XSLPsetcboptnode(XSLPprob Prob,
                 int (*UserFunc)(XSLPprob myProb, void *myObject, int *feas),
                 void *Object);
```


`UserFunc` is called when an optimal solution is obtained at a node.

If the feasibility flag `*feas`is set nonzero or if the function returns a nonzero value, then further processing of the node will be terminated \(it is declared infeasible\).

```
XSLPsetcbprenode(XSLPprob Prob,
                 int (*UserFunc)(XSLPprob myProb, void *myObject, int *feas),
                 void *Object);
```


`UserFunc` is called at the beginning of each node after the SLP problem has been set up but before any SLP iterations have taken place.

If the feasibility flag `*feas`is set nonzero or if the function returns a nonzero value, then the node will be declared infeasible and cut off. In particular, the SLP optimization at the node will not be performed.

```
XSLPsetcbslpnode(XSLPprob Prob,
                 int (*UserFunc)(XSLPprob myProb, void *myObject, int *feas),
                 void *Object);
```


`UserFunc` is called after each SLP iteration at each node, after the SLP iteration, and after the convergence and termination criteria have been tested.

If the feasibility flag `*feas`is set nonzero or if the function returns a nonzero value, then the node will be declared infeasible and cut off.

#### Section 16.4 Integer and semi-continuous delta variables


Functions implementing piecewise linear expressions often lead to local stalling due to the partial derivatives not capturing the true nature of the behaviour of the function. Such functions are often implemented as user functions or expressions using the abs function. To provide Xpress with a better way of evaluating such expressions, it is possible to mark variables \(typically the key dependencies of the expression\) as having a semi-continuous delta variable with a minimum perturbation size associated, which means the value of any expression that involves this variable is expected to meaningfully change if the variable's value in the current solution is changed by at least the semi-continuous bound of the delta. If a minimum meaningful perturbation is not known, the variable's delta may be set up to being of type explore, when SLP will trial several values up to the provided maximum in case zero partials are detected. Using exploration deltas may significantly increase the number of times the formulas the variable is used in are evaluated.

It is important to note that the value with a semi-continuous delta will still be allowed to take any value and make arbitrary steps between iterations, the extra information of the delta variable is solely used as a means of better evaluating the effect of change per variable.

User functions that can only be evaluated at given values \(e.g. lookup tables or simulations over integer input\) may be modelled with variables with an integer delta variable. If a variable's delta variable is flagged as being integer, with a step value of 'delta', then assuming the variable has an initial value of 'x0', the possible values of the variable are 'x0 + i \* delta' where 'i' is an integer number. If no initial value is provided, the lower bound \(or zero if no lower bound\) is used to start the possible values from.

Variables with a semi-continuous delta are not expected to make the problem harder, in fact, the extra information usually aids the solve noticeably.

A model with variables with integer deltas is considered to be hard. An integer delta is expected to be used to model the domain of user functions, and should not be used to otherwise model integrality of the original variable. Variables with an integer delta used in constraints tend to make the problem difficult to solve unless their use is balanced by the presence of infeasibility breaker variables \(penalty slacks\).

To change the type of a delta variable, use 'XSLPchgdeltatype' in the API and the 'setdeltatype' method in Mosel.

If variables with integer deltas are present in the problem, then SLP will run a number of heuristics as part of the solve, please refer to XSLP\_GRIDHEURSELECT.

### Chapter 17 Xpress NonLinear multistart


The feature is an additive feature that minimizes the development overhead and effort of implementing parallel multistart searches. The purpose of multistart is two-fold. Traditionally, multistart is a so called "globalization" feature. It is important to correctly understand what this technology offers, and what it does not. It offers a convenient and efficient way of exploring a larger feasible space building on top of existing local solver algorithms by the means of perturbing initial points and/or parameters or even the problem statement itself. Multistarts increase the chance that one of the found local optima is indeed the global one. However, multistarts do not guarantee that a global optimum is found and never provide a proof of global optimality. For solving MINLPs to proven global optimality, consider using [FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/).

Multistart can also be viewed as a left-alone feature. In a typical situation, versions of a model react favourably to a set of control settings, dependent on data. Multistart allows for a simple way of combining different control setting scenarios, increasing the robustness of the model.

The initial problem is defined as the baseline: as the model is normally loaded it without any multistart information, including problem description, callbacks and controls. A run or a job is defined as a problem instance that needs to be solved as part of multistart.

On completion, the initial problem is set up to match that of the winner, allowing examination of the winning strategy and solution using the normal means.

The initial prob object is not reused, all runs are made on a copy of the problem, allowing full customization from the callbacks, including changes to structure.

Callbacks are inherited by the multistart jobs from the initial problem and can be customized from the multistart callbacks. XSLPinterrupt has a global scope, and calling it terminates the multistart search.

Although not intended as the primary use, multistart allows the execution of all supported problem classes, so for example alternate MIP strategies can be used in parallel.

The multistart job pool is maintained and can be extended until the first call to optimize / nlpoptimize with `XSLP_MULTISTART` on. This allows for doing optimizations runs aimed at generating multistart jobs. The multistart pool is dynamic and new jobs can be added on the fly from the jobstart and jobend callbacks.

## Part C Reference


### Chapter 18 Reference Documentation by Topic/Functionality


This section lists all functions, controls, and attributes of FICO XPress Nonlinear by topics. The topics comprise problem creation, modification, and the solution process itself as well as querying the solution status and values to quickly get started with the nonlinear solver.

Every function, control or attribute in this section is displayed with all their related topic areas.

#### Section 18.1 Bit-vector


Reference section for all bit-vector controls.

##### Bit-vector library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPchgrowstatus, XPRSslpchgrowstatus` | Change the status setting of a constraint | Bit-vector, Data Input, SLP
`XSLPgetrowstatus, XPRSslpgetrowstatus` | Retrieve the status setting of a constraint | Bit-vector, SLP, Solution

##### Bit-vector controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_ALGORITHM`, `SLPALGORITHM` | Bit map describing the SLP algorithm\(s\) to be used | Bit-vector, SLP
`XSLP_ANALYZE`, `SLPANALYZE` | Bit map activating additional options supporting model / solution path analysis | Bit-vector, Logging, SLP
`XSLP_AUGMENTATION`, `SLPAUGMENTATION` | Bit map describing the SLP augmentation method\(s\) to be used | Bit-vector, SLP
`XSLP_CONTROL` | Bit map describing which Xpress NonLinear functions also activate the corresponding Optimizer Library function | Bit-vector, Misc
`XSLP_CONVERGENCEOPS`, `SLPCONVERGENCEOPS` | Bit map describing which convergence tests should be carried out | Bit-vector, SLP, SLP-convergence
`XSLP_FILTER`, `SLPFILTER` | Bit map for controlling solution updates | Bit-vector, SLP, Solution
`XSLP_MIPALGORITHM`, `SLPMIPALGORITHM` | Bitmap describing the MISLP algorithms to be used | Bit-vector, MISLP
`XSLP_PRESOLVEOPS`, `NLPPRESOLVEOPS` | Bitmap indicating the SLP presolve actions to be taken | Bit-vector, Presolve
`XSLP_TRACEMASKOPS`, `SLPTRACEMASKOPS` | Controls the information printed for `XSLP_TRACEMASK`. | Bit-vector, Logging, SLP
`XSLP_ZEROCRITERION`, `SLPZEROCRITERION` | Bitmap determining the behavior of the placeholder deletion procedure | Bit-vector, SLP

#### Section 18.2 Branching


Reference section for functions, controls, and attributes related to Branching. All of them affect how problems are subdivided to resolve infeasibilities during the Branch and Bound search.

##### Branching controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_MIP_BRANCHRULE`, `KNITRO_PARAM_MIP_BRANCHRULE` | Specifies which branching rule to use for MIP branch and bound procedure. | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_GUB_BRANCH`, `KNITRO_PARAM_MIP_GUB_BRANCH` | Specifies whether or not to branch on generalized upper bounds \(GUBs\). | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_PSEUDOINIT`, `KNITRO_PARAM_MIP_PSEUDOINIT` | Specifies the method used to initialize pseudo-costs corresponding to variables that have not yet been branched on in the MIP method. | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_STRONG_CANDLIM`, `KNITRO_PARAM_MIP_STRONG_CANDLIM` | Specifies the maximum number of candidates to explore for MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_LEVEL`, `KNITRO_PARAM_MIP_STRONG_LEVEL` | Specifies the maximum number of tree levels on which to perform MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_MAXIT`, `KNITRO_PARAM_MIP_STRONG_MAXIT` | Specifies the maximum number of iterations to allow for MIP strong branching solves. | Branching, Knitro-MINLP, Limits

#### Section 18.3 Callback


Reference section for functions, controls, and attributes related to the use of callback functions. Callbacks enable the user to interact with the solver at all stages of the solution process. For example, use callbacks to interrupt the search when a special condition is satisfied, to query or reject certain solutions while the solution process is still running, or to make custom problem modifications.

##### Callback library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbmsjobend` | Add a user callback to be called every time a new multistart job finishes. | Callback, Multistart
`XPRSaddcbmsjobstart` | Add a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied | Callback, Multistart
`XPRSaddcbmswinner` | Add a user callback to be called every time a multistart winner has been declared | Callback, Multistart
`XPRSaddcbnlpcoefevalerror` | Add a user callback to be called when an evaluation of a coefficient fails during the solve | Callback, Numerics
`XPRSaddcbslpcascadeend` | Add a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadestart` | Add a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevar` | Add a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevarfail` | Add a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XPRSaddcbslpconstruct` | Add a user callback to be called during the Xpress-SLP augmentation process | Callback, SLP
`XPRSaddcbslpdrcol` | Add a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XPRSaddcbslpintsol` | Add a user callback to be called during MISLP when an integer solution is obtained | Callback, MISLP
`XPRSaddcbslpiterend` | Add a user callback to be called at the end of each SLP iteration | Callback, SLP
`XPRSaddcbslpiterstart` | Add a user callback to be called at the start of each SLP iteration | Callback, SLP
`XPRSaddcbslpitervar` | Add a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XPRSaddcbslppreupdatelinearization` | Add a user callback to be called before the linearization is updated | Callback, SLP
`XPRSremovecbmsjobend` | Removes a callback function previously added by `XPRSaddcbmsjobend`. | Callback, Multistart
`XPRSremovecbmsjobstart` | Removes a callback function previously added by `XPRSaddcbmsjobstart`. | Callback, Multistart
`XPRSremovecbmswinner` | Removes a callback function previously added by `XPRSaddcbmswinner`. | Callback, Multistart
`XPRSremovecbnlpcoefevalerror` | Removes a callback function previously added by `XPRSaddcbnlpcoefevalerror`. | Callback, Numerics
`XPRSremovecbslpcascadeend` | Removes a callback function previously added by `XPRSaddcbslpcascadeend`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadestart` | Removes a callback function previously added by `XPRSaddcbslpcascadestart`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevar` | Removes a callback function previously added by `XPRSaddcbslpcascadevar`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevarfail` | Removes a callback function previously added by `XPRSaddcbslpcascadevarfail`. | Callback, Cascading, SLP
`XPRSremovecbslpconstruct` | Removes a callback function previously added by `XPRSaddcbslpconstruct`. | Callback, SLP
`XPRSremovecbslpdrcol` | Removes a callback function previously added by `XPRSaddcbslpdrcol`. | Callback, Cascading, SLP
`XPRSremovecbslpintsol` | Removes a callback function previously added by `XPRSaddcbslpintsol`. | Callback, MISLP
`XPRSremovecbslpiterend` | Removes a callback function previously added by `XPRSaddcbslpiterend`. | Callback, SLP
`XPRSremovecbslpiterstart` | Removes a callback function previously added by `XPRSaddcbslpiterstart`. | Callback, SLP
`XPRSremovecbslpitervar` | Removes a callback function previously added by `XPRSaddcbslpitervar`. | Callback, SLP, SLP-convergence
`XPRSremovecbslppreupdatelinearization` | Removes a callback function previously added by `XPRSaddcbslppreupdatelinearization`. | Callback, SLP
`XSLPcopycallbacks` | Copy the user-defined callbacks from one SLP problem to another | Callback
`XSLPsetcbcascadeend, XPRSsetcbslpcascadeend` | Set a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadestart, XPRSsetcbslpcascadestart` | Set a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevar, XPRSsetcbslpcascadevar` | Set a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevarfail, XPRSsetcbslpcascadevarfail` | Set a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XSLPsetcbcoefevalerror, XPRSsetcbnlpcoefevalerror` | Set a user callback to be called when an evaluation of a coefficient fails during the solve | Callback, Numerics
`XSLPsetcbconstruct, XPRSsetcbslpconstruct` | Set a user callback to be called during the Xpress-SLP augmentation process | Callback, SLP
`XSLPsetcbdestroy` | Set a user callback to be called when an SLP problem is about to be destroyed | Callback
`XSLPsetcbdrcol, XPRSsetcbslpdrcol` | Set a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XSLPsetcbintsol, XPRSsetcbslpintsol` | Set a user callback to be called during MISLP when an integer solution is obtained | Callback, MISLP
`XSLPsetcbiterend, XPRSsetcbslpiterend` | Set a user callback to be called at the end of each SLP iteration | Callback, SLP
`XSLPsetcbiterstart, XPRSsetcbslpiterstart` | Set a user callback to be called at the start of each SLP iteration | Callback, SLP
`XSLPsetcbitervar, XPRSsetcbslpitervar` | Set a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XSLPsetcbmessage` | Set a user callback to be called whenever Xpress NonLinear outputs a line of text according to `XSLP_ECHOXPRSMESSAGES`. | Callback, Logging
`XSLPsetcbmsjobend, XPRSsetcbmsjobend` | Set a user callback to be called every time a new multistart job finishes. | Callback, Multistart
`XSLPsetcbmsjobstart, XPRSsetcbmsjobstart` | Set a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied | Callback, Multistart
`XSLPsetcbmswinner, XPRSsetcbmswinner` | Set a user callback to be called every time a multistart winner has been declared | Callback, Multistart
`XSLPsetcboptnode` | Set a user callback to be called during MISLP when an optimal SLP solution is obtained at a node | Callback, MISLP
`XSLPsetcbprenode` | Set a user callback to be called during MISLP after the set-up of the SLP problem to be solved at a node, but before SLP optimization | Callback, MISLP
`XSLPsetcbpresolved` | Set a user callback to be called after the nonlinear presolver has been applied. | Callback, SLP
`XSLPsetcbpreupdatelinearization, XPRSsetcbslppreupdatelinearization` | Set a user callback to be called before the linearization is updated | Callback, SLP
`XSLPsetcbslpend` | Set a user callback to be called at the end of the SLP optimization | Callback, SLP
`XSLPsetcbslpnode` | Set a user callback to be called during MISLP after the SLP optimization at each node. | Callback, MISLP
`XSLPsetcbslpstart` | Set a user callback to be called at the start of the SLP optimization | Callback, SLP

#### Section 18.4 Cascading


Reference section for functions, controls, and attributes for using cascading in SLP on problems with pooling structure to recompute implied values after the iteration.

##### Cascading library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbslpcascadeend` | Add a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadestart` | Add a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevar` | Add a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevarfail` | Add a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XPRSaddcbslpdrcol` | Add a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XPRSremovecbslpcascadeend` | Removes a callback function previously added by `XPRSaddcbslpcascadeend`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadestart` | Removes a callback function previously added by `XPRSaddcbslpcascadestart`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevar` | Removes a callback function previously added by `XPRSaddcbslpcascadevar`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevarfail` | Removes a callback function previously added by `XPRSaddcbslpcascadevarfail`. | Callback, Cascading, SLP
`XPRSremovecbslpdrcol` | Removes a callback function previously added by `XPRSaddcbslpdrcol`. | Callback, Cascading, SLP
`XSLPcascade, XPRSslpcascade` | Re-calculate consistent values for SLP variables based on the current values of the remaining variables. | Cascading, SLP, Solution Process
`XSLPsetcbcascadeend, XPRSsetcbslpcascadeend` | Set a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadestart, XPRSsetcbslpcascadestart` | Set a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevar, XPRSsetcbslpcascadevar` | Set a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevarfail, XPRSsetcbslpcascadevarfail` | Set a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XSLPsetcbdrcol, XPRSsetcbslpdrcol` | Set a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XSLPsetdetrow, XPRSslpsetdetrow` | Set the determining row of a variable | Cascading, Data Input, SLP

##### Cascading controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_CASCADE`, `SLPCASCADE` | Bit map describing the cascading to be used | Cascading, SLP
`XSLP_CASCADENLIMIT`, `SLPCASCADENLIMIT` | Maximum number of iterations for cascading with non-linear determining rows | Cascading, Limits, SLP
`XSLP_CASCADETOL_PA`, `SLPCASCADETOL_PA` | Absolute cascading print tolerance | Cascading, Logging, SLP
`XSLP_CASCADETOL_PR`, `SLPCASCADETOL_PR` | Relative cascading print tolerance | Cascading, Logging, SLP
`XSLP_DRCOLDJTOL`, `SLPDRCOLDJTOL` | Reduced cost tolerance on the delta variable when fixing due to the determining column being below `XSLP_DRCOLTOL`. | Cascading, SLP, Tolerances
`XSLP_DRCOLTOL`, `SLPDRCOLTOL` | The minimum absolute magnitude of a determining column, for which the determined variable is still regarded as well defined | Cascading, SLP, Tolerances
`XSLP_DRFIXRANGE`, `SLPDRFIXRANGE` | The range around the previous value where variables are fixed in cascading if the determining column is below `XSLP_DRCOLTOL`. | Cascading, SLP

#### Section 18.5 Controls and Attributes


Reference section for functions related to setting and querying Controls and Attributes. There are various problem and solution statistics in the form of user attributes. User controls govern the execution of the solution algorithms.

##### Controls and Attributes library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPcopycontrols` | Copy the values of the control variables from one SLP problem to another | Controls and Attributes
`XSLPgetdblattrib` | Retrieve the value of a double precision problem attribute | Controls and Attributes
`XSLPgetdblcontrol` | Retrieve the value of a double precision problem control | Controls and Attributes
`XSLPgetintattrib` | Retrieve the value of an integer problem attribute | Controls and Attributes
`XSLPgetintcontrol` | Retrieve the value of an integer problem control | Controls and Attributes
`XSLPgetptrattrib` | Retrieve the value of a problem pointer attribute | Controls and Attributes
`XSLPgetstrattrib` | Retrieve the value of a string problem attribute | Controls and Attributes
`XSLPgetstrcontrol` | Retrieve the value of a string problem control | Controls and Attributes
`XSLPsetdblcontrol` | Set the value of a double precision problem control | Controls and Attributes
`XSLPsetdefaultcontrol` | Set the values of one SLP control to its default value | Controls and Attributes
`XSLPsetdefaults` | Set the values of all SLP controls to their default values | Controls and Attributes
`XSLPsetintcontrol` | Set the value of an integer problem control | Controls and Attributes
`XSLPsetparam` | Set the value of a control parameter by name | Controls and Attributes
`XSLPsetstrcontrol` | Set the value of a string problem control | Controls and Attributes

#### Section 18.6 Cuts


Reference section for functions, controls, and attributes related to cutting plane separation. Separation denotes the process of deriving new valid inequalities to strengthen the linear \(LP\) relaxation during the Branch and Bound Search.

##### Cuts controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_MIP_KNAPSACK`, `KNITRO_PARAM_MIP_KNAPSACK` | Specifies rules for adding MIP knapsack cuts. | Cuts, Knitro-MINLP
`XSLP_CUTSTRATEGY`, `SLPCUTSTRATEGY` | Determines whihc cuts to apply in the MISLP search when the default SLP-in-MIP strategy is used. | Cuts, MISLP

#### Section 18.7 Data Input


Reference section for functions, controls, and attributes related to the input of auxiliary data. While not strictly necessary, auxiliary data can be used to customize the solution process.

##### Data Input library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPcascadeorder, XPRSslpcascadeorder` | Establish a re-calculation sequence for SLP variables with determining rows. | Data Input, SLP
`XSLPchgcascadenlimit, XPRSslpchgcascadenlimit` | Set a variable specific cascade iteration limit | Data Input, SLP
`XSLPchgrowstatus, XPRSslpchgrowstatus` | Change the status setting of a constraint | Bit-vector, Data Input, SLP
`XSLPchgrowwt, XPRSslpchgrowwt` | Set or change the initial penalty error weight for a row | Data Input, SLP
`XSLPmsaddcustompreset, XPRSmsaddcustompreset` | A combined version of XSLPmsaddjob and XSLPmsaddpreset. | Data Input, Multistart
`XSLPmsaddjob, XPRSmsaddjob` | Adds a multistart job to the multistart pool | Data Input, Multistart
`XSLPmsaddpreset, XPRSmsaddpreset` | Loads a preset of jobs into the multistart job pool. | Data Input, Multistart
`XSLPsetcurrentiv, XPRSnlpsetcurrentiv` | Transfer the current solution to initial values | Data Input
`XSLPsetdetrow, XPRSslpsetdetrow` | Set the determining row of a variable | Cascading, Data Input, SLP
`XSLPsetinitstepbounds, XPRSslpsetinitstepbounds` | Set the initial step bounds of columns | Data Input
`XSLPsetinitval, XPRSnlpsetinitval` | Set the initial value of columns | Data Input

##### Data Input controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_DEFAULTIV`, `NLPDEFAULTIV` | Default initial value for an SLP variable if none is explicitly given | Data Input

#### Section 18.8 Data Information


Reference section for functions, controls, and attributes related to querying information about auxiliary data.

##### Data Information library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPgetrowwt, XPRSslpgetrowwt` | Get the initial penalty error weight for a row | Data Information, SLP

##### Data Information attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_VARIABLES`, `NLPVARIABLES` | Number of SLP variables | Data Information, SLP

#### Section 18.9 Derivatives


Reference section for functions, controls, and attributes affecting the calculation of derivatives for the local solvers.

##### Derivatives controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_GRADOPT`, `KNITRO_PARAM_GRADOPT` | Specifies how to compute the gradients of the objective and constraint functions. | Derivatives, Knitro
`XKTR_PARAM_HESSOPT`, `KNITRO_PARAM_HESSOPT` | Specifies how to compute the \(approximate\) Hessian of the Lagrangian. | Derivatives, Knitro
`XSLP_DELTA_A`, `SLPDELTA_A` | Absolute perturbation of values for calculating numerical derivatives | Derivatives
`XSLP_DELTA_INFINITY`, `SLPDELTA_INFINITY` | Maximum value for partial derivatives | Derivatives
`XSLP_DELTA_R`, `SLPDELTA_R` | Relative perturbation of values for calculating numerical derivatives | Derivatives
`XSLP_DELTA_X`, `SLPDELTA_X` | Minimum absolute value of delta coefficients to be retained | Derivatives
`XSLP_DELTA_Z`, `SLPDELTA_Z` | Tolerance used when calculating derivatives | Derivatives, Tolerances
`XSLP_DELTA_ZERO`, `SLPDELTA_ZERO` | Absolute zero acceptance tolerance used when calculating derivatives | Derivatives, Tolerances
`XSLP_DERIVATIVES`, `NLPDERIVATIVES` | Bitmap describing the method of calculating derivatives | Derivatives
`XSLP_FUNCEVAL`, `NLPFUNCEVAL` | Bit map for determining the method of evaluating user functions and their derivatives | Derivatives, User Functions
`XSLP_HESSIAN`, `NLPHESSIAN` | Second order differentiation mode when using analytical derivatives | Derivatives
`XSLP_JACOBIAN`, `NLPJACOBIAN` | First order differentiation mode when using analytical derivatives | Derivatives

##### Derivatives attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_USEDERIVATIVES`, `NLPUSEDERIVATIVES` | Indicates whether numeric or analytic derivatives were used to create the linear approximations and solve the problem | Derivatives

#### Section 18.10 File IO


Reference section for functions, controls, and attributes related to File IO. Use these functions to write and read data from disk.

##### File IO library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPreadprob` | Read an Xpress NonLinear extended MPS format matrix from a file into an SLP problem | File IO, Problem Creation
`XSLPrestore` | Restore the Xpress NonLinear problem from a file created by `XSLPsave` | File IO, Save Restore
`XSLPsave` | Save the Xpress NonLinear problem to file | File IO, Save Restore
`XSLPsaveas` | Save the Xpress NonLinear problem to a named file | File IO, Save Restore
`XSLPsetlogfile` | Define an output file to be used to receive messages from Xpress NonLinear | File IO, Logging
`XSLPwriteprob` | Write the current problem to a file in extended MPS or text format | File IO, Problem Information
`XSLPwriteslxsol` | Write the current solution to an MPS like file format | File IO, Solution

##### File IO controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_IVNAME`, `NLPIVNAME` | Name of the set of initial values to be used | File IO
`XSLP_TOLNAME`, `SLPTOLNAME` | Name of the set of tolerance sets to be used | File IO, SLP

#### Section 18.11 Heuristics


Reference section for functions, controls, and attributes related to Primal Heuristics, which are auxiliary search algorithms for quickly finding improving solutions during the Branch and Bound Search.

##### Heuristics controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_MIP_HEURISTIC`, `KNITRO_PARAM_MIP_HEURISTIC` | Specifies which MIP heuristic search approach to apply to try to find an initial integer feasible point. | Heuristics, Knitro-MINLP
`XKTR_PARAM_MIP_HEURISTIC_MAXIT`, `KNITRO_PARAM_MIP_HEURISTIC_MAXIT` | Specifies the maximum number of iterations to allow for MIP heuristic, if one is enabled. | Heuristics, Knitro-MINLP
`XSLP_FINDIV`, `NLPFINDIV` | Option for running a heuristic to find a feasible initial point | Heuristics
`XSLP_GRIDHEURSELECT`, `SLPGRIDHEURSELECT` | Bit map selectin which heuristics to run if the problem has variable with an integer delta | Heuristics, SLP
`XSLP_HEURSTRATEGY`, `SLPHEURSTRATEGY` | Branch and Bound: This specifies the MINLP heuristic strategy. | Heuristics, SLP

#### Section 18.12 Knitro


Reference section for controls related to the Knitro solver.

##### Knitro controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_ALGORITHM`, `KNITRO_PARAM_ALGORITHM` | Indicates which algorithm to use to solve nonlinear problems | Knitro, Solution Process
`XKTR_PARAM_BAR_DIRECTINTERVAL`, `KNITRO_PARAM_BAR_DIRECTINTERVAL` | Controls the maximum number of consecutive conjugate gradient \(CG\) steps before Knitro will try to enforce that a step is taken using direct linear algebra. | Knitro, Limits
`XKTR_PARAM_BAR_FEASIBLE`, `KNITRO_PARAM_BAR_FEASIBLE` | Specifies whether special emphasis is placed on getting and staying feasible in the interior-point algorithms. | Knitro
`XKTR_PARAM_BAR_FEASMODETOL`, `KNITRO_PARAM_BAR_FEASMODETOL` | Specifies the tolerance in equation that determines whether Knitro will force subsequent iterates to remain feasible. | Knitro, Tolerances
`XKTR_PARAM_BAR_INITMU`, `KNITRO_PARAM_BAR_INITMU` | Specifies the initial value for the barrier parameter : _μ_  used with the barrier algorithms. | Knitro
`XKTR_PARAM_BAR_INITPT`, `KNITRO_PARAM_BAR_INITPT` | Indicates whether an initial point strategy is used with barrier algorithms. | Knitro
`XKTR_PARAM_BAR_MAXBACKTRACK`, `KNITRO_PARAM_BAR_MAXBACKTRACK` | Indicates the maximum allowable number of backtracks during the linesearch of the Interior/Direct algorithm before reverting to a CG step. | Knitro, Limits
`XKTR_PARAM_BAR_MAXCROSSIT`, `KNITRO_PARAM_BAR_MAXCROSSIT` | Specifies the maximum number of crossover iterations before termination. | Knitro, Limits
`XKTR_PARAM_BAR_MAXREFACTOR`, `KNITRO_PARAM_BAR_MAXREFACTOR` | Indicates the maximum number of refactorizations of the KKT system per iteration of the Interior/Direct algorithm before reverting to a CG step. | Knitro, Limits
`XKTR_PARAM_BAR_MURULE`, `KNITRO_PARAM_BAR_MURULE` | Indicates which strategy to use for modifying the barrier parameter mu in the barrier algorithms. | Knitro
`XKTR_PARAM_BAR_PENCONS`, `KNITRO_PARAM_BAR_PENCONS` | Indicates whether a penalty approach is applied to the constraints. | Knitro
`XKTR_PARAM_BAR_PENRULE`, `KNITRO_PARAM_BAR_PENRULE` | Indicates which penalty parameter strategy to use for determining whether or not to accept a trial iterate. | Knitro
`XKTR_PARAM_BAR_SWITCHRULE`, `KNITRO_PARAM_BAR_SWITCHRULE` | Indicates whether or not the barrier algorithms will allow switching from an optimality phase to a pure feasibility phase. | Knitro
`XKTR_PARAM_DELTA`, `KNITRO_PARAM_DELTA` | Specifies the initial trust region radius scaling factor used to determine the initial trust region size. | Knitro
`XKTR_PARAM_FEASTOL`, `KNITRO_PARAM_FEASTOL` | Specifies the final relative stopping tolerance for the feasibility error. | Knitro, Tolerances
`XKTR_PARAM_FEASTOLABS`, `KNITRO_PARAM_FEASTOLABS` | Specifies the final absolute stopping tolerance for the feasibility error. | Knitro, Tolerances
`XKTR_PARAM_GRADOPT`, `KNITRO_PARAM_GRADOPT` | Specifies how to compute the gradients of the objective and constraint functions. | Derivatives, Knitro
`XKTR_PARAM_HESSOPT`, `KNITRO_PARAM_HESSOPT` | Specifies how to compute the \(approximate\) Hessian of the Lagrangian. | Derivatives, Knitro
`XKTR_PARAM_HONORBNDS`, `KNITRO_PARAM_HONORBNDS` | Indicates whether or not to enforce satisfaction of simple variable bounds throughout the optimization. | Knitro
`XKTR_PARAM_INFEASTOL`, `KNITRO_PARAM_INFEASTOL` | Specifies the \(relative\) tolerance used for declaring infeasibility of a model. | Knitro, Tolerances
`XKTR_PARAM_LMSIZE`, `KNITRO_PARAM_LMSIZE` | Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option. | Knitro, Limits
`XKTR_PARAM_MAXCGIT`, `KNITRO_PARAM_MAXCGIT` | Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option. | Knitro, Limits
`XKTR_PARAM_MAXIT`, `KNITRO_PARAM_MAXIT` | Specifies the maximum number of iterations before termination. | Knitro, Limits
`XKTR_PARAM_MIP_INTEGERTOL`, `KNITRO_PARAM_INTEGERTOL` | This value specifies the threshold for deciding whether or not a variable is determined to be an integer. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPABS`, `KNITRO_PARAM_INTGAPABS` | The absolute integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPREL`, `KNITRO_PARAM_INTGAPREL` | The relative integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_OBJRANGE`, `KNITRO_PARAM_OBJRANGE` | Specifies the extreme limits of the objective function for purposes of determining unboundedness. | Knitro, Limits
`XKTR_PARAM_OPTTOL`, `KNITRO_PARAM_OPTTOL` | Specifies the final relative stopping tolerance for the KKT \(optimality\) error. | Knitro, Tolerances
`XKTR_PARAM_OPTTOLABS`, `KNITRO_PARAM_OPTTOLABS` | Specifies the final absolute stopping tolerance for the KKT \(optimality\) error. | Knitro, Tolerances
`XKTR_PARAM_OUTLEV`, `KNITRO_PARAM_OUTLEV` | Controls the level of output produced by Knitro. | Knitro, Logging
`XKTR_PARAM_PRESOLVE`, `KNITRO_PARAM_PRESOLVE` | Determine whether or not to use the Knitro presolver to try to simplify the model by removing variables or constraints. | Knitro, Presolve
`XKTR_PARAM_PRESOLVE_TOL`, `KNITRO_PARAM_PRESOLVE_TOL` | Determines the tolerance used by the Knitro presolver to remove variables and constraints from the model. | Knitro, Presolve, Tolerances
`XKTR_PARAM_SCALE`, `KNITRO_PARAM_SCALE` | Performs a scaling of the objective and constraint functions based on their values at the initial point. | Knitro, Numerics
`XKTR_PARAM_SOC`, `KNITRO_PARAM_SOC` | Specifies whether or not to try second order corrections \(SOC\). | Knitro
`XKTR_PARAM_SOLTYPE`, `KNITRO_PARAM_SOLTYPE` | This option specifies the solution returned by Knitro. | Knitro
`XKTR_PARAM_XTOL`, `KNITRO_PARAM_XTOL` | The optimization process will terminate if the relative change in all components of the solution point estimate is less than xtol. | Knitro, Tolerances

#### Section 18.13 Knitro-MINLP


Reference section for controls related to the MINLP solver in Knitro.

##### Knitro-MINLP controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_MIP_BRANCHRULE`, `KNITRO_PARAM_MIP_BRANCHRULE` | Specifies which branching rule to use for MIP branch and bound procedure. | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_GUB_BRANCH`, `KNITRO_PARAM_MIP_GUB_BRANCH` | Specifies whether or not to branch on generalized upper bounds \(GUBs\). | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_HEURISTIC`, `KNITRO_PARAM_MIP_HEURISTIC` | Specifies which MIP heuristic search approach to apply to try to find an initial integer feasible point. | Heuristics, Knitro-MINLP
`XKTR_PARAM_MIP_HEURISTIC_MAXIT`, `KNITRO_PARAM_MIP_HEURISTIC_MAXIT` | Specifies the maximum number of iterations to allow for MIP heuristic, if one is enabled. | Heuristics, Knitro-MINLP
`XKTR_PARAM_MIP_IMPLICATNS`, `KNITRO_PARAM_MIP_IMPLICATNS` | Specifies whether or not to add constraints to the MIP derived from logical implications. | Knitro-MINLP, Presolve
`XKTR_PARAM_MIP_INTEGERTOL`, `KNITRO_PARAM_INTEGERTOL` | This value specifies the threshold for deciding whether or not a variable is determined to be an integer. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPABS`, `KNITRO_PARAM_INTGAPABS` | The absolute integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPREL`, `KNITRO_PARAM_INTGAPREL` | The relative integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_KNAPSACK`, `KNITRO_PARAM_MIP_KNAPSACK` | Specifies rules for adding MIP knapsack cuts. | Cuts, Knitro-MINLP
`XKTR_PARAM_MIP_LPALG`, `KNITRO_PARAM_MIP_LPALG` | Specifies which algorithm to use for any linear programming \(LP\) subproblem solves that may occur in the MIP branch and bound procedure. | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_MAXNODES`, `KNITRO_PARAM_MIP_MAXNODES` | Specifies the maximum number of nodes explored. | Knitro-MINLP, Limits
`XKTR_PARAM_MIP_MAXSOLVES`, `KNITRO_PARAM_MIP_MAXSOLVES` | Specifies the maximum number of subproblem solves allowed \(0 means no limit\). | Knitro-MINLP, Limits
`XKTR_PARAM_MIP_METHOD`, `KNITRO_PARAM_MIP_METHOD` | Specifies which MIP method to use. | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_OUTINTERVAL`, `KNITRO_PARAM_MIP_OUTINTERVAL` | Specifies node printing interval for `XKTR_PARAM_MIP_OUTLEVEL` when `XKTR_PARAM_MIP_OUTLEVEL` > 0. | Knitro-MINLP, Logging
`XKTR_PARAM_MIP_OUTLEVEL`, `KNITRO_PARAM_MIP_OUTLEVEL` | Specifies how much MIP information to print. | Knitro-MINLP, Logging
`XKTR_PARAM_MIP_PSEUDOINIT`, `KNITRO_PARAM_MIP_PSEUDOINIT` | Specifies the method used to initialize pseudo-costs corresponding to variables that have not yet been branched on in the MIP method. | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_ROOTALG`, `KNITRO_PARAM_MIP_ROOTALG` | Specifies which algorithm to use for the root node solve in MIP \(same options as `XKTR_PARAM_ALGORITHM` user option\). | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_ROUNDING`, `KNITRO_PARAM_MIP_ROUNDING` | Specifies the MIP rounding rule to apply. | Knitro-MINLP
`XKTR_PARAM_MIP_SELECTRULE`, `KNITRO_PARAM_MIP_SELECTRULE` | Specifies the MIP select rule for choosing the next node in the branch and bound tree. | Knitro-MINLP
`XKTR_PARAM_MIP_STRONG_CANDLIM`, `KNITRO_PARAM_MIP_STRONG_CANDLIM` | Specifies the maximum number of candidates to explore for MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_LEVEL`, `KNITRO_PARAM_MIP_STRONG_LEVEL` | Specifies the maximum number of tree levels on which to perform MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_MAXIT`, `KNITRO_PARAM_MIP_STRONG_MAXIT` | Specifies the maximum number of iterations to allow for MIP strong branching solves. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_TERMINATE`, `KNITRO_PARAM_MIP_TERMINATE` | Specifies conditions for terminating the MIP algorithm. | Knitro-MINLP

#### Section 18.14 Licensing


Reference section for functions, controls, and attributes related to Licensing.

##### Licensing library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPfree` | Free any memory allocated by Xpress NonLinear and close any open Xpress NonLinear files | Licensing
`XSLPinit` | Initializes the Xpress NonLinear system | Licensing

#### Section 18.15 Limits


Reference section for controls and attributes related to the various limits for the solution process.

##### Limits controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_BAR_DIRECTINTERVAL`, `KNITRO_PARAM_BAR_DIRECTINTERVAL` | Controls the maximum number of consecutive conjugate gradient \(CG\) steps before Knitro will try to enforce that a step is taken using direct linear algebra. | Knitro, Limits
`XKTR_PARAM_BAR_MAXBACKTRACK`, `KNITRO_PARAM_BAR_MAXBACKTRACK` | Indicates the maximum allowable number of backtracks during the linesearch of the Interior/Direct algorithm before reverting to a CG step. | Knitro, Limits
`XKTR_PARAM_BAR_MAXCROSSIT`, `KNITRO_PARAM_BAR_MAXCROSSIT` | Specifies the maximum number of crossover iterations before termination. | Knitro, Limits
`XKTR_PARAM_BAR_MAXREFACTOR`, `KNITRO_PARAM_BAR_MAXREFACTOR` | Indicates the maximum number of refactorizations of the KKT system per iteration of the Interior/Direct algorithm before reverting to a CG step. | Knitro, Limits
`XKTR_PARAM_LMSIZE`, `KNITRO_PARAM_LMSIZE` | Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option. | Knitro, Limits
`XKTR_PARAM_MAXCGIT`, `KNITRO_PARAM_MAXCGIT` | Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option. | Knitro, Limits
`XKTR_PARAM_MAXIT`, `KNITRO_PARAM_MAXIT` | Specifies the maximum number of iterations before termination. | Knitro, Limits
`XKTR_PARAM_MIP_MAXNODES`, `KNITRO_PARAM_MIP_MAXNODES` | Specifies the maximum number of nodes explored. | Knitro-MINLP, Limits
`XKTR_PARAM_MIP_MAXSOLVES`, `KNITRO_PARAM_MIP_MAXSOLVES` | Specifies the maximum number of subproblem solves allowed \(0 means no limit\). | Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_CANDLIM`, `KNITRO_PARAM_MIP_STRONG_CANDLIM` | Specifies the maximum number of candidates to explore for MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_LEVEL`, `KNITRO_PARAM_MIP_STRONG_LEVEL` | Specifies the maximum number of tree levels on which to perform MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_MAXIT`, `KNITRO_PARAM_MIP_STRONG_MAXIT` | Specifies the maximum number of iterations to allow for MIP strong branching solves. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_OBJRANGE`, `KNITRO_PARAM_OBJRANGE` | Specifies the extreme limits of the objective function for purposes of determining unboundedness. | Knitro, Limits
`XSLP_BARLIMIT`, `SLPBARLIMIT` | Number of initial SLP iterations using the barrier method | Limits, Linearizations, SLP
`XSLP_BARSTALLINGLIMIT`, `SLPBARSTALLINGLIMIT` | Number of iterations to allow numerical failures in barrier before switching to dual | Limits, Linearizations, SLP
`XSLP_BARSTALLINGOBJLIMIT`, `SLPBARSTALLINGOBJLIMIT` | Number of iterations over which to measure the objective change for barrier iterations with no crossover | Limits, Linearizations, SLP
`XSLP_CASCADENLIMIT`, `SLPCASCADENLIMIT` | Maximum number of iterations for cascading with non-linear determining rows | Cascading, Limits, SLP
`XSLP_INFEASLIMIT`, `SLPINFEASLIMIT` | The maximum number of consecutive infeasible SLP iterations which can occur before Xpress-SLP terminates | Limits, SLP
`XSLP_ITERLIMIT`, `SLPITERLIMIT` | The maximum number of SLP iterations | Limits, SLP
`XSLP_LSITERLIMIT`, `SLPLSITERLIMIT` | Number of iterations in the line search | Limits, SLP
`XSLP_LSPATTERNLIMIT`, `SLPLSPATTERNLIMIT` | Number of iterations in the pattern search preceding the line search | Limits, SLP
`XSLP_LSZEROLIMIT`, `SLPLSZEROLIMIT` | Maximum number of zero length line search steps before line search is deactivated | Limits, SLP
`XSLP_MAXTIME`, `NLPMAXTIME` | The maximum time in seconds that the SLP optimization will run before it terminates | Limits
`XSLP_MIPCUTOFFCOUNT`, `SLPMIPCUTOFFCOUNT` | Number of SLP iterations to check when considering a node for cutting off | Limits, MISLP
`XSLP_MIPCUTOFFLIMIT`, `SLPMIPCUTOFFLIMIT` | Number of SLP iterations to check when considering a node for cutting off | Limits, MISLP
`XSLP_MIPITERLIMIT`, `SLPMIPITERLIMIT` | Maximum number of SLP iterations at each node | Limits, MISLP
`XSLP_MULTISTART_MAXSOLVES`, `MULTISTART_MAXSOLVES` | The maximum number of jobs to create during the multistart search. | Limits, Multistart
`XSLP_MULTISTART_MAXTIME`, `MULTISTART_MAXTIME` | The maximum total time to be spent in the mutlistart search. | Limits, Multistart
`XSLP_MULTISTART_POOLSIZE`, `MULTISTART_POOLSIZE` | The maximum number of problem objects allowed to pool up before synchronization in the deterministic multistart. | Limits, Multistart
`XSLP_XLIMIT`, `SLPXLIMIT` | Number of SLP iterations up to which static objective \(1\) convergence testing is performed | Limits, SLP, SLP-convergence
`XSLP_ZEROCRITERIONCOUNT`, `SLPZEROCRITERIONCOUNT` | Number of consecutive times a placeholder entry is zero before being considered for deletion | Limits, SLP

#### Section 18.16 Linearizations


Reference section for functions, controls, and attributes related to solving the linearizations in SLP.

##### Linearizations controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_BARCROSSOVERSTART`, `SLPBARCROSSOVERSTART` | Default crossover activation behaviour for barrier start | Linearizations, SLP
`XSLP_BARLIMIT`, `SLPBARLIMIT` | Number of initial SLP iterations using the barrier method | Limits, Linearizations, SLP
`XSLP_BARSTALLINGLIMIT`, `SLPBARSTALLINGLIMIT` | Number of iterations to allow numerical failures in barrier before switching to dual | Limits, Linearizations, SLP
`XSLP_BARSTALLINGOBJLIMIT`, `SLPBARSTALLINGOBJLIMIT` | Number of iterations over which to measure the objective change for barrier iterations with no crossover | Limits, Linearizations, SLP
`XSLP_BARSTALLINGTOL`, `SLPBARSTALLINGTOL` | Required change in the objective when progress is measured in barrier iterations without crossover | Linearizations, SLP
`XSLP_BARSTARTOPS`, `SLPBARSTARTOPS` | Controls behaviour when the barrier is used to solve the linearizations | Linearizations, SLP
`XSLP_FEASTOLTARGET`, `SLPFEASTOLTARGET` | When set, this defines a target feasibility tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_ITERFALLBACKOPS`, `SLPITERFALLBACKOPS` | Alternative LP level control values for numerically challenging problems | Linearizations, Numerics, SLP
`XSLP_MIPDEFAULTALGORITHM`, `SLPMIPDEFAULTALGORITHM` | Default algorithm to be used during the tree search in MISLP | Linearizations, MISLP
`XSLP_OPTIMALITYTOLTARGET`, `SLPOPTIMALITYTOLTARGET` | When set, this defines a target optimality tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_UNFINISHEDLIMIT`, `SLPUNFINISHEDLIMIT` | The number of consecutive SLP iterations that may have an unfinished status before the solve is terminated. | Linearizations, SLP

##### Linearizations attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_ECFCOUNT`, `SLPECFCOUNT` | Number of infeasible constraints found at the point of linearization | Linearizations, SLP

#### Section 18.17 Logging


Reference section for functions, controls, and attributes related to Logging.

##### Logging library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPprintevalinfo, XPRSnlpprintevalinfo` | Print a summary of any evaluation errors that may have occurred during solving a problem | Logging
`XSLPprintmemory` | Print the dimensions and memory allocations for a problem | Logging
`XSLPsetcbmessage` | Set a user callback to be called whenever Xpress NonLinear outputs a line of text according to `XSLP_ECHOXPRSMESSAGES`. | Callback, Logging
`XSLPsetlogfile` | Define an output file to be used to receive messages from Xpress NonLinear | File IO, Logging

##### Logging controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_MIP_OUTINTERVAL`, `KNITRO_PARAM_MIP_OUTINTERVAL` | Specifies node printing interval for `XKTR_PARAM_MIP_OUTLEVEL` when `XKTR_PARAM_MIP_OUTLEVEL` > 0. | Knitro-MINLP, Logging
`XKTR_PARAM_MIP_OUTLEVEL`, `KNITRO_PARAM_MIP_OUTLEVEL` | Specifies how much MIP information to print. | Knitro-MINLP, Logging
`XKTR_PARAM_OUTLEV`, `KNITRO_PARAM_OUTLEV` | Controls the level of output produced by Knitro. | Knitro, Logging
`XSLP_ANALYZE`, `SLPANALYZE` | Bit map activating additional options supporting model / solution path analysis | Bit-vector, Logging, SLP
`XSLP_AUTOSAVE`, `SLPAUTOSAVE` | Frequency with which to save the model | Logging, SLP
`XSLP_CASCADETOL_PA`, `SLPCASCADETOL_PA` | Absolute cascading print tolerance | Cascading, Logging, SLP
`XSLP_CASCADETOL_PR`, `SLPCASCADETOL_PR` | Relative cascading print tolerance | Cascading, Logging, SLP
`XSLP_DELTAFORMAT`, `SLPDELTAFORMAT` | Formatting string for creation of names for SLP delta vectors | Logging, SLP
`XSLP_DELTAOFFSET`, `SLPDELTAOFFSET` | Position of first character of SLP variable name used to create name of delta vector | Logging, SLP
`XSLP_ECHOXPRSMESSAGES` | Controls if the XSLP message callback should relay messages from the XPRS library. | Logging
`XSLP_ERROROFFSET`, `SLPERROROFFSET` | Position of first character of constraint name used to create name of penalty error vectors | Logging, SLP
`XSLP_LOG`, `NLPLOG` | Level of printing during SLP iterations | Logging, SLP
`XSLP_MINUSDELTAFORMAT`, `SLPMINUSDELTAFORMAT` | Formatting string for creation of names for SLP negative penalty delta vectors | Logging, SLP
`XSLP_MINUSERRORFORMAT`, `SLPMINUSERRORFORMAT` | Formatting string for creation of names for SLP negative penalty error vectors | Logging, SLP
`XSLP_MIPLOG`, `SLPMIPLOG` | Frequency with which MIP status is printed | Logging, MISLP
`XSLP_MULTISTART_LOG`, `MULTISTART_LOG` | The level of logging during the multistart run. | Logging, Multistart
`XSLP_PENALTYCOLFORMAT`, `SLPPENALTYCOLFORMAT` | Formatting string for creation of the names of the SLP penalty transfer vectors | Logging, SLP
`XSLP_PENALTYINFOSTART`, `SLPPENALTYINFOSTART` | Iteration from which to record row penalty information | Logging, SLP
`XSLP_PENALTYROWFORMAT`, `SLPPENALTYROWFORMAT` | Formatting string for creation of the names of the SLP penalty rows | Logging, SLP
`XSLP_PLUSDELTAFORMAT`, `SLPPLUSDELTAFORMAT` | Formatting string for creation of names for SLP positive penalty delta vectors | Logging, SLP
`XSLP_PLUSERRORFORMAT`, `SLPPLUSERRORFORMAT` | Formatting string for creation of names for SLP positive penalty error vectors | Logging, SLP
`XSLP_PRIMALINTEGRALALPHA`, `NLPPRIMALINTEGRALALPHA` | Decay term for primal integral computation | Logging
`XSLP_PRIMALINTEGRALREF`, `NLPPRIMALINTEGRALREF` | Reference solution value to take into account when calculating the primal integral | Logging
`XSLP_SBLOROWFORMAT`, `SLPSBLOROWFORMAT` | Formatting string for creation of names for SLP lower step bound rows | Logging, SLP
`XSLP_SBNAME`, `SLPSBNAME` | Name of the set of initial step bounds to be used | Logging, SLP
`XSLP_SBROWOFFSET`, `SLPSBROWOFFSET` | Position of first character of SLP variable name used to create name of SLP lower and upper step bound rows | Logging, SLP
`XSLP_SBUPROWFORMAT`, `SLPSBUPROWFORMAT` | Formatting string for creation of names for SLP upper step bound rows | Logging, SLP
`XSLP_SLPLOG`, `SLPLOG` | Frequency with which SLP status is printed | Logging, SLP
`XSLP_TRACEMASK`, `SLPTRACEMASK` | Mask of variable or row names that are to be traced through the SLP iterates | Logging, SLP
`XSLP_TRACEMASKOPS`, `SLPTRACEMASKOPS` | Controls the information printed for `XSLP_TRACEMASK`. | Bit-vector, Logging, SLP
`XSLP_UPDATEFORMAT`, `SLPUPDATEFORMAT` | Formatting string for creation of names for SLP update rows | Logging, SLP
`XSLP_UPDATEOFFSET`, `SLPUPDATEOFFSET` | Position of first character of SLP variable name used to create name of SLP update row | Logging, SLP

#### Section 18.18 Memory


Reference section for functions, controls, and attributes related to memory handling and usage.

##### Memory controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_MEMORYFACTOR` | Factor for expanding size of dynamic arrays in memory | Memory

#### Section 18.19 MISLP


Reference section for functions, controls, and attributes for using a combination of sequential linear programming, and branch and bound to solve MINLPs to local optimality.

##### MISLP library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbslpintsol` | Add a user callback to be called during MISLP when an integer solution is obtained | Callback, MISLP
`XPRSremovecbslpintsol` | Removes a callback function previously added by `XPRSaddcbslpintsol`. | Callback, MISLP
`XSLPsetcbintsol, XPRSsetcbslpintsol` | Set a user callback to be called during MISLP when an integer solution is obtained | Callback, MISLP
`XSLPsetcboptnode` | Set a user callback to be called during MISLP when an optimal SLP solution is obtained at a node | Callback, MISLP
`XSLPsetcbprenode` | Set a user callback to be called during MISLP after the set-up of the SLP problem to be solved at a node, but before SLP optimization | Callback, MISLP
`XSLPsetcbslpnode` | Set a user callback to be called during MISLP after the SLP optimization at each node. | Callback, MISLP

##### MISLP controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_CUTSTRATEGY`, `SLPCUTSTRATEGY` | Determines whihc cuts to apply in the MISLP search when the default SLP-in-MIP strategy is used. | Cuts, MISLP
`XSLP_DETERMINISTIC`, `NLPDETERMINISTIC` | Determines if the parallel features of SLP should be guaranteed to be deterministic | MISLP, Parallel, SLP
`XSLP_MIPALGORITHM`, `SLPMIPALGORITHM` | Bitmap describing the MISLP algorithms to be used | Bit-vector, MISLP
`XSLP_MIPCUTOFF_A`, `SLPMIPCUTOFF_A` | Absolute objective function cutoff for MIP termination | MISLP, Tolerances
`XSLP_MIPCUTOFF_R`, `SLPMIPCUTOFF_R` | Absolute objective function cutoff for MIP termination | MISLP, Tolerances
`XSLP_MIPCUTOFFCOUNT`, `SLPMIPCUTOFFCOUNT` | Number of SLP iterations to check when considering a node for cutting off | Limits, MISLP
`XSLP_MIPCUTOFFLIMIT`, `SLPMIPCUTOFFLIMIT` | Number of SLP iterations to check when considering a node for cutting off | Limits, MISLP
`XSLP_MIPDEFAULTALGORITHM`, `SLPMIPDEFAULTALGORITHM` | Default algorithm to be used during the tree search in MISLP | Linearizations, MISLP
`XSLP_MIPERRORTOL_A`, `SLPMIPERRORTOL_A` | Absolute penalty error cost tolerance for MIP cut-off | MISLP, Tolerances
`XSLP_MIPERRORTOL_R`, `SLPMIPERRORTOL_R` | Relative penalty error cost tolerance for MIP cut-off | MISLP, Tolerances
`XSLP_MIPFIXSTEPBOUNDS`, `SLPMIPFIXSTEPBOUNDS` | Bitmap describing the step-bound fixing strategy during MISLP | MISLP
`XSLP_MIPITERLIMIT`, `SLPMIPITERLIMIT` | Maximum number of SLP iterations at each node | Limits, MISLP
`XSLP_MIPLOG`, `SLPMIPLOG` | Frequency with which MIP status is printed | Logging, MISLP
`XSLP_MIPOCOUNT`, `SLPMIPOCOUNT` | Number of SLP iterations at each node over which to measure objective function variation | MISLP, SLP-convergence
`XSLP_MIPOTOL_A`, `SLPMIPOTOL_A` | Absolute objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MIPOTOL_R`, `SLPMIPOTOL_R` | Relative objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MIPRELAXSTEPBOUNDS`, `SLPMIPRELAXSTEPBOUNDS` | Bitmap describing the step-bound relaxation strategy during MISLP | MISLP

##### MISLP attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_MIPITER`, `SLPMIPITER` | Total number of SLP iterations in MISLP | MISLP
`XSLP_MIPNODES`, `SLPMIPNODES` | Number of nodes explored in SLP-in-MIP. | MISLP
`XSLP_MIPPROBLEM` | The underlying Optimizer MIP problem. | MISLP
`XSLP_MIPSOLS`, `SLPMIPSOLS` | Number of integer solutions found in MISLP. | MISLP, Solution

#### Section 18.20 Misc


Reference section for further miscellaneous functionality.

##### Misc library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPgetlasterror` | Retrieve the error message corresponding to the last Xpress NonLinear error during an SLP run | Misc
`XSLPsetfunctionerror, XPRSnlpsetfunctionerror` | Set the function error flag for the problem | Misc

##### Misc controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_CONTROL` | Bit map describing which Xpress NonLinear functions also activate the corresponding Optimizer Library function | Bit-vector, Misc
`XSLP_KEEPEQUALSCOLUMN`, `NLPKEEPEQUALSCOLUMN` | When set to a nonzero value, the MPS reader will keep the equals column in the problem | Misc

##### Misc attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_IFS`, `NLPIFS` | Number of internal functions | Misc
`XSLP_JOBID`, `NLPJOBID` | Unique identifier for the current job | Misc, Multistart
`XSLP_PRIMALINTEGRAL`, `NLPPRIMALINTEGRAL` | Local primal integral of the solve | Misc
`XSLP_VERSIONDATE` | Date of creation of Xpress NonLinear | Misc
`XSLP_XPRSPROBLEM` | The underlying Optimizer problem | Misc
`XSLP_XSLPPROBLEM` | The Xpress NonLinear problem | Misc

#### Section 18.21 Multistart


Reference section for functions, controls, and attributes for using multistart with the nonlinear local solvers.

##### Multistart library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbmsjobend` | Add a user callback to be called every time a new multistart job finishes. | Callback, Multistart
`XPRSaddcbmsjobstart` | Add a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied | Callback, Multistart
`XPRSaddcbmswinner` | Add a user callback to be called every time a multistart winner has been declared | Callback, Multistart
`XPRSremovecbmsjobend` | Removes a callback function previously added by `XPRSaddcbmsjobend`. | Callback, Multistart
`XPRSremovecbmsjobstart` | Removes a callback function previously added by `XPRSaddcbmsjobstart`. | Callback, Multistart
`XPRSremovecbmswinner` | Removes a callback function previously added by `XPRSaddcbmswinner`. | Callback, Multistart
`XSLPmsaddcustompreset, XPRSmsaddcustompreset` | A combined version of XSLPmsaddjob and XSLPmsaddpreset. | Data Input, Multistart
`XSLPmsaddjob, XPRSmsaddjob` | Adds a multistart job to the multistart pool | Data Input, Multistart
`XSLPmsaddpreset, XPRSmsaddpreset` | Loads a preset of jobs into the multistart job pool. | Data Input, Multistart
`XSLPmsclear, XPRSmsclear` | Removes all scheduled jobs from the multistart job pool | Multistart
`XSLPsetcbmsjobend, XPRSsetcbmsjobend` | Set a user callback to be called every time a new multistart job finishes. | Callback, Multistart
`XSLPsetcbmsjobstart, XPRSsetcbmsjobstart` | Set a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied | Callback, Multistart
`XSLPsetcbmswinner, XPRSsetcbmswinner` | Set a user callback to be called every time a multistart winner has been declared | Callback, Multistart

##### Multistart controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_MSMAXBOUNDRANGE`, `MSMAXBOUNDRANGE` | Defines the maximum range inside which initial points are generated by multistart presets | Multistart
`XSLP_MULTISTART`, `MULTISTART` | The multistart main control. | Multistart
`XSLP_MULTISTART_LOG`, `MULTISTART_LOG` | The level of logging during the multistart run. | Logging, Multistart
`XSLP_MULTISTART_MAXSOLVES`, `MULTISTART_MAXSOLVES` | The maximum number of jobs to create during the multistart search. | Limits, Multistart
`XSLP_MULTISTART_MAXTIME`, `MULTISTART_MAXTIME` | The maximum total time to be spent in the mutlistart search. | Limits, Multistart
`XSLP_MULTISTART_POOLSIZE`, `MULTISTART_POOLSIZE` | The maximum number of problem objects allowed to pool up before synchronization in the deterministic multistart. | Limits, Multistart
`XSLP_MULTISTART_SEED`, `MULTISTART_SEED` | Random seed used for the automatic generation of initial point when loading multistart presets | Multistart
`XSLP_MULTISTART_THREADS`, `MULTISTART_THREADS` | The maximum number of threads to be used in multistart | Multistart, Parallel

##### Multistart attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_JOBID`, `NLPJOBID` | Unique identifier for the current job | Misc, Multistart
`XSLP_MSSTATUS` | Status of the mutlistart search | Multistart

#### Section 18.22 Names Manager


Reference section for functions, controls, and attributes related to the Names Manager.

##### Names Manager library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPitemname` | Retrieves the name of an Xpress NonLinear entity or the value of a function token as a character string. | Names Manager

#### Section 18.23 Numerics


Reference section for functions, controls, and attributes related to Numerics.

##### Numerics library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbnlpcoefevalerror` | Add a user callback to be called when an evaluation of a coefficient fails during the solve | Callback, Numerics
`XPRSremovecbnlpcoefevalerror` | Removes a callback function previously added by `XPRSaddcbnlpcoefevalerror`. | Callback, Numerics
`XSLPscaling` | Analyze the current matrix for largest/smallest coefficients and ratios | Numerics
`XSLPsetcbcoefevalerror, XPRSsetcbnlpcoefevalerror` | Set a user callback to be called when an evaluation of a coefficient fails during the solve | Callback, Numerics

##### Numerics controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_SCALE`, `KNITRO_PARAM_SCALE` | Performs a scaling of the objective and constraint functions based on their values at the initial point. | Knitro, Numerics
`XSLP_INFINITY`, `NLPINFINITY` | Value returned by a divide-by-zero in a formula | Numerics
`XSLP_ITERFALLBACKOPS`, `SLPITERFALLBACKOPS` | Alternative LP level control values for numerically challenging problems | Linearizations, Numerics, SLP
`XSLP_SCALE`, `SLPSCALE` | When to re-scale the SLP problem | Numerics, SLP
`XSLP_SCALECOUNT`, `SLPSCALECOUNT` | Iteration limit used in determining when to re-scale the SLP matrix | Numerics, SLP

##### Numerics attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_TOTALEVALUATIONERRORS`, `NLPTOTALEVALUATIONERRORS` | The total number of evaluation errors during the solve | Numerics

#### Section 18.24 Parallel


Reference section for functionality around modern multi-core CPUs. By default, Xpress will detect how many cores are available in the system and try to use all of them. The controls in this section affect to which extent the solver uses the parallel hardware.

##### Parallel controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_CALCTHREADS`, `NLPCALCTHREADS` | Number of threads used for formula and derivatives evaluations | Parallel
`XSLP_DETERMINISTIC`, `NLPDETERMINISTIC` | Determines if the parallel features of SLP should be guaranteed to be deterministic | MISLP, Parallel, SLP
`XSLP_MULTISTART_THREADS`, `MULTISTART_THREADS` | The maximum number of threads to be used in multistart | Multistart, Parallel
`XSLP_THREADS`, `NLPTHREADS` | Default number of threads to be used | Parallel
`XSLP_THREADSAFEUSERFUNC`, `NLPTHREADSAFEUSERFUNC` | Defines if user functions are allowed to be called in parallel | Parallel, User Functions

#### Section 18.25 Presolve


Reference section for functions, controls, and attributes related to Presolve. Presolve is a collection of techniques to transform the input problem into an equivalent, but smaller problem by fixing or eliminating columns and rows.

##### Presolve library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPpostsolve, XPRSnlppostsolve` | Restores the problem to its pre-solve state | Presolve
`XSLPpresolve` | Perform a nonlinear presolve on the problem | Presolve

##### Presolve controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_MIP_IMPLICATNS`, `KNITRO_PARAM_MIP_IMPLICATNS` | Specifies whether or not to add constraints to the MIP derived from logical implications. | Knitro-MINLP, Presolve
`XKTR_PARAM_PRESOLVE`, `KNITRO_PARAM_PRESOLVE` | Determine whether or not to use the Knitro presolver to try to simplify the model by removing variables or constraints. | Knitro, Presolve
`XKTR_PARAM_PRESOLVE_TOL`, `KNITRO_PARAM_PRESOLVE_TOL` | Determines the tolerance used by the Knitro presolver to remove variables and constraints from the model. | Knitro, Presolve, Tolerances
`XSLP_BOUNDTHRESHOLD`, `SLPBOUNDTHRESHOLD` | The maximum size of a bound that can be introduced by nonlinear presolve. | Presolve, SLP
`XSLP_LINQUADBR`, `NLPLINQUADBR` | Use linear and quadratic constraints and objective function to further reduce bounds on all variables | Presolve
`XSLP_POSTSOLVE`, `NLPPOSTSOLVE` | This control determines whether postsolving should be performed automatically | Presolve
`XSLP_PRESOLVE`, `NLPPRESOLVE` | This control determines whether presolving should be performed on the nonlinear problem prior to starting the main algorithm | Presolve
`XSLP_PRESOLVE_ELIMTOL`, `NLPPRESOLVE_ELIMTOL` | Tolerance for nonlinear eliminations during SLP presolve | Presolve, Tolerances
`XSLP_PRESOLVELEVEL`, `NLPPRESOLVELEVEL` | This control determines the level of changes presolve may carry out on the problem and whether column/row indices may change | Presolve
`XSLP_PRESOLVEOPS`, `NLPPRESOLVEOPS` | Bitmap indicating the SLP presolve actions to be taken | Bit-vector, Presolve
`XSLP_PRESOLVEZERO`, `NLPPRESOLVEZERO` | Minimum absolute value for a variable which is identified as nonzero during SLP presolve | Presolve, Tolerances
`XSLP_PROBING`, `NLPPROBING` | This control determines whether probing on a subset of variables should be performed prior to starting the main algorithm. | Presolve
`XSLP_REFORMULATE`, `NLPREFORMULATE` | Controls the problem reformulations carried out before augmentation. | Presolve

##### Presolve attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_PRESOLVEELIMINATIONS`, `NLPPRESOLVEELIMINATIONS` | Number of SLP variables eliminated by `XSLPpresolve` | Presolve
`XSLP_PRESOLVESTATE` | Indicates if the problem is presolved | Presolve

#### Section 18.26 Problem Creation


Reference section for functions, controls, and attributes related to problem creation.

##### Problem Creation library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPcopyprob` | Copy an existing SLP problem to another | Problem Creation
`XSLPcreateprob` | Create a new SLP problem | Problem Creation
`XSLPdestroyprob` | Delete an SLP problem and release all the associated memory | Problem Creation
`XSLPreadprob` | Read an Xpress NonLinear extended MPS format matrix from a file into an SLP problem | File IO, Problem Creation

#### Section 18.27 Problem Information


Reference section for functions, controls, and attributes related to querying information about a problem.

##### Problem Information library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSnlpgetformulastr` | Retrieve a single matrix formula in a character string. | Problem Information
`XPRSslpgetcoefstr` | Retrieve a single matrix coefficient as a formula in a character string. | Problem Information, SLP
`XSLPgetcoefformula, XPRSslpgetcoefformula` | Retrieve a single matrix coefficient as a formula split into tokens. | Problem Information, SLP
`XSLPgetcoefs, XPRSslpgetcoefs` | Retrieve the list of positions of the nonlinear coefficients in the problem. | Problem Information, SLP
`XSLPgetformula, XPRSnlpgetformula` | Retrieve a single matrix formula as a formula split into tokens. | Problem Information
`XSLPgetformularows, XPRSnlpgetformularows` | Retrieve the list of positions of the nonlinear formulas in the problem | Problem Information
`XSLPgetindex` | Retrieve the index of an Xpress NonLinear entity with a given name | Problem Information, User Functions
`XSLPloadcoefs, XPRSslploadcoefs` | Load non-linear coefficients into the SLP problem. | Problem Information, SLP
`XSLPloadformulas, XPRSnlploadformulas` | Load non-linear formulas into the SLP problem | Problem Information
`XSLPwriteprob` | Write the current problem to a file in extended MPS or text format | File IO, Problem Information

##### Problem Information attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_COEFFICIENTS`, `SLPCOEFFICIENTS` | Number of nonlinear coefficients | Problem Information, SLP
`XSLP_DELTAS`, `SLPDELTAS` | Number of delta vectors created during augmentation | Problem Information, SLP
`XSLP_EQUALSCOLUMN`, `NLPEQUALSCOLUMN` | Index of the reserved "=" column | Problem Information
`XSLP_EXPLOREDELTAS`, `SLPEXPLOREDELTAS` | Number of variables with an exploration-type delta set up in the problem | Problem Information, SLP
`XSLP_IMPLICITVARIABLES`, `NLPIMPLICITVARIABLES` | Number of SLP variables appearing only in coefficients | Problem Information, SLP
`XSLP_INTEGERDELTAS`, `SLPINTEGERDELTAS` | Number of variables set up with an integer delta in the problem | Problem Information, SLP
`XSLP_MINUSPENALTYERRORS`, `SLPMINUSPENALTYERRORS` | Number of negative penalty error vectors | Problem Information, SLP
`XSLP_NONLINEARCONSTRAINTS`, `NONLINEARCONSTRAINTS` | Number of nonlinear constraints in the problem | Problem Information
`XSLP_ORIGINALCOLS`, `NLPORIGINALCOLS` | Number of model columns in the extended original problem | Problem Information
`XSLP_ORIGINALROWS`, `NLPORIGINALROWS` | Number of model rows in the extended original problem | Problem Information
`XSLP_PENALTYDELTACOLUMN`, `SLPPENALTYDELTACOLUMN` | Index of column costing the penalty delta row | Problem Information, SLP
`XSLP_PENALTYDELTAROW`, `SLPPENALTYDELTAROW` | Index of equality row holding the penalties for delta vectors | Problem Information, SLP
`XSLP_PENALTYDELTAS`, `SLPPENALTYDELTAS` | Number of penalty delta vectors | Problem Information, SLP
`XSLP_PENALTYERRORCOLUMN`, `SLPPENALTYERRORCOLUMN` | Index of column costing the penalty error row | Problem Information, SLP
`XSLP_PENALTYERRORROW`, `SLPPENALTYERRORROW` | Index of equality row holding the penalties for penalty error vectors | Problem Information, SLP
`XSLP_PENALTYERRORS`, `SLPPENALTYERRORS` | Number of penalty error vectors | Problem Information, SLP
`XSLP_PLUSPENALTYERRORS`, `SLPPLUSPENALTYERRORS` | Number of positive penalty error vectors | Problem Information, SLP
`XSLP_SEMICONTDELTAS`, `SLPSEMICONTDELTAS` | Number of variables with a minimum perturbation step set up in the problem | Problem Information, SLP

#### Section 18.28 Problem Modification


Reference section for functions, controls, and attributes related to Problem Modification after loading. Make adjustments to the current problem.

##### Problem Modification library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSnlpchgformulastr` | Add or replace a single matrix formula using a character string for the formula. | Problem Modification
`XPRSslpchgcoefstr` | Add or change a single matrix coefficient using a character string for the formula. | Problem Modification, SLP
`XSLPaddcoefs, XPRSslpaddcoefs` | Add non-linear coefficients to the SLP problem. | Problem Modification, SLP
`XSLPaddformulas, XPRSnlpaddformulas` | Add non-linear formulas to the SLP problem. | Problem Modification
`XSLPchgcoef, XPRSslpchgcoef` | Add or change a single matrix coefficient using a parsed or unparsed formula. | Problem Modification, SLP
`XSLPchgdeltatype, XPRSslpchgdeltatype` | Changes the type of the delta assigned to a nonlinear variable | Problem Modification, SLP
`XSLPchgformula, XPRSnlpchgformula` | Add or replace a single matrix formula using a parsed or unparsed formula | Problem Modification
`XSLPdelcoefs, XPRSslpdelcoefs` | Delete coefficients from the current problem. | Problem Modification, SLP
`XSLPdelformulas, XPRSnlpdelformulas` | Delete nonlinear formulas from the current problem | Problem Modification

#### Section 18.29 Save Restore


Reference section for functions, controls, and attributes related to the Save and Restore functionality.

##### Save Restore library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPrestore` | Restore the Xpress NonLinear problem from a file created by `XSLPsave` | File IO, Save Restore
`XSLPsave` | Save the Xpress NonLinear problem to file | File IO, Save Restore
`XSLPsaveas` | Save the Xpress NonLinear problem to a named file | File IO, Save Restore

#### Section 18.30 SLP


Reference section for functions, controls, and attributes that are specific to using the sequential linear programming solver SLP.

##### SLP library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbslpcascadeend` | Add a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadestart` | Add a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevar` | Add a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevarfail` | Add a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XPRSaddcbslpconstruct` | Add a user callback to be called during the Xpress-SLP augmentation process | Callback, SLP
`XPRSaddcbslpdrcol` | Add a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XPRSaddcbslpiterend` | Add a user callback to be called at the end of each SLP iteration | Callback, SLP
`XPRSaddcbslpiterstart` | Add a user callback to be called at the start of each SLP iteration | Callback, SLP
`XPRSaddcbslpitervar` | Add a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XPRSaddcbslppreupdatelinearization` | Add a user callback to be called before the linearization is updated | Callback, SLP
`XPRSremovecbslpcascadeend` | Removes a callback function previously added by `XPRSaddcbslpcascadeend`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadestart` | Removes a callback function previously added by `XPRSaddcbslpcascadestart`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevar` | Removes a callback function previously added by `XPRSaddcbslpcascadevar`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevarfail` | Removes a callback function previously added by `XPRSaddcbslpcascadevarfail`. | Callback, Cascading, SLP
`XPRSremovecbslpconstruct` | Removes a callback function previously added by `XPRSaddcbslpconstruct`. | Callback, SLP
`XPRSremovecbslpdrcol` | Removes a callback function previously added by `XPRSaddcbslpdrcol`. | Callback, Cascading, SLP
`XPRSremovecbslpiterend` | Removes a callback function previously added by `XPRSaddcbslpiterend`. | Callback, SLP
`XPRSremovecbslpiterstart` | Removes a callback function previously added by `XPRSaddcbslpiterstart`. | Callback, SLP
`XPRSremovecbslpitervar` | Removes a callback function previously added by `XPRSaddcbslpitervar`. | Callback, SLP, SLP-convergence
`XPRSremovecbslppreupdatelinearization` | Removes a callback function previously added by `XPRSaddcbslppreupdatelinearization`. | Callback, SLP
`XPRSslpchgcoefstr` | Add or change a single matrix coefficient using a character string for the formula. | Problem Modification, SLP
`XPRSslpgetcoefstr` | Retrieve a single matrix coefficient as a formula in a character string. | Problem Information, SLP
`XSLPaddcoefs, XPRSslpaddcoefs` | Add non-linear coefficients to the SLP problem. | Problem Modification, SLP
`XSLPcascade, XPRSslpcascade` | Re-calculate consistent values for SLP variables based on the current values of the remaining variables. | Cascading, SLP, Solution Process
`XSLPcascadeorder, XPRSslpcascadeorder` | Establish a re-calculation sequence for SLP variables with determining rows. | Data Input, SLP
`XSLPchgcascadenlimit, XPRSslpchgcascadenlimit` | Set a variable specific cascade iteration limit | Data Input, SLP
`XSLPchgcoef, XPRSslpchgcoef` | Add or change a single matrix coefficient using a parsed or unparsed formula. | Problem Modification, SLP
`XSLPchgdeltatype, XPRSslpchgdeltatype` | Changes the type of the delta assigned to a nonlinear variable | Problem Modification, SLP
`XSLPchgrowstatus, XPRSslpchgrowstatus` | Change the status setting of a constraint | Bit-vector, Data Input, SLP
`XSLPchgrowwt, XPRSslpchgrowwt` | Set or change the initial penalty error weight for a row | Data Input, SLP
`XSLPconstruct, XPRSslpconstruct` | Create the full augmented SLP matrix and data structures, ready for optimization | SLP, Solution Process
`XSLPdelcoefs, XPRSslpdelcoefs` | Delete coefficients from the current problem. | Problem Modification, SLP
`XSLPgetcoefformula, XPRSslpgetcoefformula` | Retrieve a single matrix coefficient as a formula split into tokens. | Problem Information, SLP
`XSLPgetcoefs, XPRSslpgetcoefs` | Retrieve the list of positions of the nonlinear coefficients in the problem. | Problem Information, SLP
`XSLPgetcolinfo, XPRSslpgetcolinfo` | Get current column information. | SLP, Solution
`XSLPgetrowinfo, XPRSslpgetrowinfo` | Get current row information. | SLP, Solution
`XSLPgetrowstatus, XPRSslpgetrowstatus` | Retrieve the status setting of a constraint | Bit-vector, SLP, Solution
`XSLPgetrowwt, XPRSslpgetrowwt` | Get the initial penalty error weight for a row | Data Information, SLP
`XSLPloadcoefs, XPRSslploadcoefs` | Load non-linear coefficients into the SLP problem. | Problem Information, SLP
`XSLPreinitialize, XPRSslpreinitialize` | Reset the SLP problem to match a just augmented system | SLP, Solution Process
`XSLPsetcbcascadeend, XPRSsetcbslpcascadeend` | Set a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadestart, XPRSsetcbslpcascadestart` | Set a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevar, XPRSsetcbslpcascadevar` | Set a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevarfail, XPRSsetcbslpcascadevarfail` | Set a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XSLPsetcbconstruct, XPRSsetcbslpconstruct` | Set a user callback to be called during the Xpress-SLP augmentation process | Callback, SLP
`XSLPsetcbdrcol, XPRSsetcbslpdrcol` | Set a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XSLPsetcbiterend, XPRSsetcbslpiterend` | Set a user callback to be called at the end of each SLP iteration | Callback, SLP
`XSLPsetcbiterstart, XPRSsetcbslpiterstart` | Set a user callback to be called at the start of each SLP iteration | Callback, SLP
`XSLPsetcbitervar, XPRSsetcbslpitervar` | Set a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XSLPsetcbpresolved` | Set a user callback to be called after the nonlinear presolver has been applied. | Callback, SLP
`XSLPsetcbpreupdatelinearization, XPRSsetcbslppreupdatelinearization` | Set a user callback to be called before the linearization is updated | Callback, SLP
`XSLPsetcbslpend` | Set a user callback to be called at the end of the SLP optimization | Callback, SLP
`XSLPsetcbslpstart` | Set a user callback to be called at the start of the SLP optimization | Callback, SLP
`XSLPsetdetrow, XPRSslpsetdetrow` | Set the determining row of a variable | Cascading, Data Input, SLP
`XSLPunconstruct, XPRSslpunconstruct` | Removes the augmentation and returns the problem to its pre-linearization state | SLP, Solution Process
`XSLPupdatelinearization, XPRSslpupdatelinearization` | Updates the current linearization | SLP, Solution Process

##### SLP controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_ALGORITHM`, `SLPALGORITHM` | Bit map describing the SLP algorithm\(s\) to be used | Bit-vector, SLP
`XSLP_ANALYZE`, `SLPANALYZE` | Bit map activating additional options supporting model / solution path analysis | Bit-vector, Logging, SLP
`XSLP_ATOL_A`, `SLPATOL_A` | Absolute delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ATOL_R`, `SLPATOL_R` | Relative delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_AUGMENTATION`, `SLPAUGMENTATION` | Bit map describing the SLP augmentation method\(s\) to be used | Bit-vector, SLP
`XSLP_AUTOSAVE`, `SLPAUTOSAVE` | Frequency with which to save the model | Logging, SLP
`XSLP_BARCROSSOVERSTART`, `SLPBARCROSSOVERSTART` | Default crossover activation behaviour for barrier start | Linearizations, SLP
`XSLP_BARLIMIT`, `SLPBARLIMIT` | Number of initial SLP iterations using the barrier method | Limits, Linearizations, SLP
`XSLP_BARSTALLINGLIMIT`, `SLPBARSTALLINGLIMIT` | Number of iterations to allow numerical failures in barrier before switching to dual | Limits, Linearizations, SLP
`XSLP_BARSTALLINGOBJLIMIT`, `SLPBARSTALLINGOBJLIMIT` | Number of iterations over which to measure the objective change for barrier iterations with no crossover | Limits, Linearizations, SLP
`XSLP_BARSTALLINGTOL`, `SLPBARSTALLINGTOL` | Required change in the objective when progress is measured in barrier iterations without crossover | Linearizations, SLP
`XSLP_BARSTARTOPS`, `SLPBARSTARTOPS` | Controls behaviour when the barrier is used to solve the linearizations | Linearizations, SLP
`XSLP_BOUNDTHRESHOLD`, `SLPBOUNDTHRESHOLD` | The maximum size of a bound that can be introduced by nonlinear presolve. | Presolve, SLP
`XSLP_CASCADE`, `SLPCASCADE` | Bit map describing the cascading to be used | Cascading, SLP
`XSLP_CASCADENLIMIT`, `SLPCASCADENLIMIT` | Maximum number of iterations for cascading with non-linear determining rows | Cascading, Limits, SLP
`XSLP_CASCADETOL_PA`, `SLPCASCADETOL_PA` | Absolute cascading print tolerance | Cascading, Logging, SLP
`XSLP_CASCADETOL_PR`, `SLPCASCADETOL_PR` | Relative cascading print tolerance | Cascading, Logging, SLP
`XSLP_CLAMPSHRINK`, `SLPCLAMPSHRINK` | Shrink ratio used to impose strict convergence on variables converged in extended criteria only | SLP
`XSLP_CLAMPVALIDATIONTOL_A`, `SLPCLAMPVALIDATIONTOL_A` | Absolute validation tolerance for applying `XSLP_CLAMPSHRINK` | SLP, Tolerances
`XSLP_CLAMPVALIDATIONTOL_R`, `SLPCLAMPVALIDATIONTOL_R` | Relative validation tolerance for applying `XSLP_CLAMPSHRINK` | SLP, Tolerances
`XSLP_CONVERGENCEOPS`, `SLPCONVERGENCEOPS` | Bit map describing which convergence tests should be carried out | Bit-vector, SLP, SLP-convergence
`XSLP_CTOL`, `SLPCTOL` | Closure convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_DAMP`, `SLPDAMP` | Damping factor for updating values of variables | SLP
`XSLP_DAMPEXPAND`, `SLPDAMPEXPAND` | Multiplier to increase damping factor during dynamic damping | SLP
`XSLP_DAMPMAX`, `SLPDAMPMAX` | Maximum value for the damping factor of a variable during dynamic damping | SLP
`XSLP_DAMPMIN`, `SLPDAMPMIN` | Minimum value for the damping factor of a variable during dynamic damping | SLP
`XSLP_DAMPSHRINK`, `SLPDAMPSHRINK` | Multiplier to decrease damping factor during dynamic damping | SLP
`XSLP_DAMPSTART`, `SLPDAMPSTART` | SLP iteration at which damping is activated | SLP
`XSLP_DEFAULTSTEPBOUND`, `SLPDEFAULTSTEPBOUND` | Minimum initial value for the step bound of an SLP variable if none is explicitly given | SLP
`XSLP_DELAYUPDATEROWS`, `SLPDELAYUPDATEROWS` | Number of SLP iterations before update rows are fully activated | SLP
`XSLP_DELTACOST`, `SLPDELTACOST` | Initial penalty cost multiplier for penalty delta vectors | SLP
`XSLP_DELTACOSTFACTOR`, `SLPDELTACOSTFACTOR` | Factor for increasing cost multiplier on total penalty delta vectors | SLP
`XSLP_DELTAFORMAT`, `SLPDELTAFORMAT` | Formatting string for creation of names for SLP delta vectors | Logging, SLP
`XSLP_DELTAMAXCOST`, `SLPDELTAMAXCOST` | Maximum penalty cost multiplier for penalty delta vectors | SLP
`XSLP_DELTAOFFSET`, `SLPDELTAOFFSET` | Position of first character of SLP variable name used to create name of delta vector | Logging, SLP
`XSLP_DELTAZLIMIT`, `SLPDELTAZLIMIT` | Number of SLP iterations during which to apply XSLP\_DELTA\_Z | SLP
`XSLP_DETERMINISTIC`, `NLPDETERMINISTIC` | Determines if the parallel features of SLP should be guaranteed to be deterministic | MISLP, Parallel, SLP
`XSLP_DJTOL`, `SLPDJTOL` | Tolerance on DJ value for determining if a variable is at its step bound | SLP, Tolerances
`XSLP_DRCOLDJTOL`, `SLPDRCOLDJTOL` | Reduced cost tolerance on the delta variable when fixing due to the determining column being below `XSLP_DRCOLTOL`. | Cascading, SLP, Tolerances
`XSLP_DRCOLTOL`, `SLPDRCOLTOL` | The minimum absolute magnitude of a determining column, for which the determined variable is still regarded as well defined | Cascading, SLP, Tolerances
`XSLP_DRFIXRANGE`, `SLPDRFIXRANGE` | The range around the previous value where variables are fixed in cascading if the determining column is below `XSLP_DRCOLTOL`. | Cascading, SLP
`XSLP_ECFCHECK`, `SLPECFCHECK` | Check feasibility at the point of linearization for extended convergence criteria | SLP, SLP-convergence
`XSLP_ECFTOL_A`, `SLPECFTOL_A` | Absolute tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ECFTOL_R`, `SLPECFTOL_R` | Relative tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ENFORCECOSTSHRINK`, `SLPENFORCECOSTSHRINK` | Factor by which to decrease the current penalty multiplier when enforcing rows. | SLP
`XSLP_ENFORCEMAXCOST`, `SLPENFORCEMAXCOST` | Maximum penalty cost in the objective before enforcing most violating rows | SLP
`XSLP_ERRORCOST`, `SLPERRORCOST` | Initial penalty cost multiplier for penalty error vectors | SLP
`XSLP_ERRORCOSTFACTOR`, `SLPERRORCOSTFACTOR` | Factor for increasing cost multiplier on total penalty error vectors | SLP
`XSLP_ERRORMAXCOST`, `SLPERRORMAXCOST` | Maximum penalty cost multiplier for penalty error vectors | SLP
`XSLP_ERROROFFSET`, `SLPERROROFFSET` | Position of first character of constraint name used to create name of penalty error vectors | Logging, SLP
`XSLP_ERRORTOL_A`, `SLPERRORTOL_A` | Absolute tolerance for error vectors | SLP, Tolerances
`XSLP_ERRORTOL_P`, `SLPERRORTOL_P` | Absolute tolerance for printing error vectors | SLP, Tolerances
`XSLP_ESCALATION`, `SLPESCALATION` | Factor for increasing cost multiplier on individual penalty error vectors | SLP
`XSLP_ETOL_A`, `SLPETOL_A` | Absolute tolerance on penalty vectors | SLP, Tolerances
`XSLP_ETOL_R`, `SLPETOL_R` | Relative tolerance on penalty vectors | SLP, Tolerances
`XSLP_EVTOL_A`, `SLPEVTOL_A` | Absolute tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_EVTOL_R`, `SLPEVTOL_R` | Relative tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_EXPAND`, `SLPEXPAND` | Multiplier to increase a step bound | SLP
`XSLP_FEASTOLTARGET`, `SLPFEASTOLTARGET` | When set, this defines a target feasibility tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_FILTER`, `SLPFILTER` | Bit map for controlling solution updates | Bit-vector, SLP, Solution
`XSLP_GRANULARITY`, `SLPGRANULARITY` | Base for calculating penalty costs | SLP
`XSLP_GRIDHEURSELECT`, `SLPGRIDHEURSELECT` | Bit map selectin which heuristics to run if the problem has variable with an integer delta | Heuristics, SLP
`XSLP_HEURSTRATEGY`, `SLPHEURSTRATEGY` | Branch and Bound: This specifies the MINLP heuristic strategy. | Heuristics, SLP
`XSLP_INFEASLIMIT`, `SLPINFEASLIMIT` | The maximum number of consecutive infeasible SLP iterations which can occur before Xpress-SLP terminates | Limits, SLP
`XSLP_ITERFALLBACKOPS`, `SLPITERFALLBACKOPS` | Alternative LP level control values for numerically challenging problems | Linearizations, Numerics, SLP
`XSLP_ITERLIMIT`, `SLPITERLIMIT` | The maximum number of SLP iterations | Limits, SLP
`XSLP_ITOL_A`, `SLPITOL_A` | Absolute impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ITOL_R`, `SLPITOL_R` | Relative impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_LOG`, `NLPLOG` | Level of printing during SLP iterations | Logging, SLP
`XSLP_LSITERLIMIT`, `SLPLSITERLIMIT` | Number of iterations in the line search | Limits, SLP
`XSLP_LSPATTERNLIMIT`, `SLPLSPATTERNLIMIT` | Number of iterations in the pattern search preceding the line search | Limits, SLP
`XSLP_LSSTART`, `SLPLSSTART` | Iteration in which to active the line search | SLP
`XSLP_LSZEROLIMIT`, `SLPLSZEROLIMIT` | Maximum number of zero length line search steps before line search is deactivated | Limits, SLP
`XSLP_MATRIXTOL`, `SLPMATRIXTOL` | Nonzero tolerance for dropping coefficients from the linearization. | SLP
`XSLP_MAXWEIGHT`, `SLPMAXWEIGHT` | Maximum penalty weight for delta or error vectors | SLP
`XSLP_MERITLAMBDA`, `NLPMERITLAMBDA` | Factor by which the net objective is taken into account in the merit function | SLP, Solution
`XSLP_MINSBFACTOR`, `SLPMINSBFACTOR` | Factor by which step bounds can be decreased beneath `XSLP_ATOL_A` | SLP
`XSLP_MINUSDELTAFORMAT`, `SLPMINUSDELTAFORMAT` | Formatting string for creation of names for SLP negative penalty delta vectors | Logging, SLP
`XSLP_MINUSERRORFORMAT`, `SLPMINUSERRORFORMAT` | Formatting string for creation of names for SLP negative penalty error vectors | Logging, SLP
`XSLP_MINWEIGHT`, `SLPMINWEIGHT` | Minimum penalty weight for delta or error vectors | SLP
`XSLP_MTOL_A`, `SLPMTOL_A` | Absolute effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MTOL_R`, `SLPMTOL_R` | Relative effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MVTOL`, `SLPMVTOL` | Marginal value tolerance for determining if a constraint is slack | SLP, SLP-convergence, Tolerances
`XSLP_OBJTHRESHOLD`, `SLPOBJTHRESHOLD` | Assumed maximum value of the objective function in absolute value. | SLP
`XSLP_OBJTOPENALTYCOST`, `SLPOBJTOPENALTYCOST` | Factor to estimate initial penalty costs from objective function | SLP
`XSLP_OCOUNT`, `SLPOCOUNT` | Number of SLP iterations over which to measure objective function variation for static objective \(2\) convergence criterion | SLP, SLP-convergence
`XSLP_OPTIMALITYTOLTARGET`, `SLPOPTIMALITYTOLTARGET` | When set, this defines a target optimality tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_OTOL_A`, `SLPOTOL_A` | Absolute static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_OTOL_R`, `SLPOTOL_R` | Relative static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_PENALTYCOLFORMAT`, `SLPPENALTYCOLFORMAT` | Formatting string for creation of the names of the SLP penalty transfer vectors | Logging, SLP
`XSLP_PENALTYINFOSTART`, `SLPPENALTYINFOSTART` | Iteration from which to record row penalty information | Logging, SLP
`XSLP_PENALTYROWFORMAT`, `SLPPENALTYROWFORMAT` | Formatting string for creation of the names of the SLP penalty rows | Logging, SLP
`XSLP_PLUSDELTAFORMAT`, `SLPPLUSDELTAFORMAT` | Formatting string for creation of names for SLP positive penalty delta vectors | Logging, SLP
`XSLP_PLUSERRORFORMAT`, `SLPPLUSERRORFORMAT` | Formatting string for creation of names for SLP positive penalty error vectors | Logging, SLP
`XSLP_SAMECOUNT`, `SLPSAMECOUNT` | Number of steps reaching the step bound in the same direction before step bounds are increased | SLP
`XSLP_SAMEDAMP`, `SLPSAMEDAMP` | Number of steps in same direction before damping factor is increased | SLP
`XSLP_SBLOROWFORMAT`, `SLPSBLOROWFORMAT` | Formatting string for creation of names for SLP lower step bound rows | Logging, SLP
`XSLP_SBNAME`, `SLPSBNAME` | Name of the set of initial step bounds to be used | Logging, SLP
`XSLP_SBROWOFFSET`, `SLPSBROWOFFSET` | Position of first character of SLP variable name used to create name of SLP lower and upper step bound rows | Logging, SLP
`XSLP_SBSTART`, `SLPSBSTART` | SLP iteration after which step bounds are first applied | SLP
`XSLP_SBUPROWFORMAT`, `SLPSBUPROWFORMAT` | Formatting string for creation of names for SLP upper step bound rows | Logging, SLP
`XSLP_SCALE`, `SLPSCALE` | When to re-scale the SLP problem | Numerics, SLP
`XSLP_SCALECOUNT`, `SLPSCALECOUNT` | Iteration limit used in determining when to re-scale the SLP matrix | Numerics, SLP
`XSLP_SHRINK`, `SLPSHRINK` | Multiplier to reduce a step bound | SLP
`XSLP_SHRINKBIAS`, `SLPSHRINKBIAS` | Defines an overwrite / adjustment of step bounds for improving iterations | SLP
`XSLP_SLPLOG`, `SLPLOG` | Frequency with which SLP status is printed | Logging, SLP
`XSLP_STOL_A`, `SLPSTOL_A` | Absolute slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOL_R`, `SLPSTOL_R` | Relative slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOPOUTOFRANGE`, `NLPSTOPOUTOFRANGE` | Stop optimization and return error code if internal function argument is out of range | SLP
`XSLP_TOLNAME`, `SLPTOLNAME` | Name of the set of tolerance sets to be used | File IO, SLP
`XSLP_TRACEMASK`, `SLPTRACEMASK` | Mask of variable or row names that are to be traced through the SLP iterates | Logging, SLP
`XSLP_TRACEMASKOPS`, `SLPTRACEMASKOPS` | Controls the information printed for `XSLP_TRACEMASK`. | Bit-vector, Logging, SLP
`XSLP_UNFINISHEDLIMIT`, `SLPUNFINISHEDLIMIT` | The number of consecutive SLP iterations that may have an unfinished status before the solve is terminated. | Linearizations, SLP
`XSLP_UPDATEFORMAT`, `SLPUPDATEFORMAT` | Formatting string for creation of names for SLP update rows | Logging, SLP
`XSLP_UPDATEOFFSET`, `SLPUPDATEOFFSET` | Position of first character of SLP variable name used to create name of SLP update row | Logging, SLP
`XSLP_VALIDATIONFACTOR`, `NLPVALIDATIONFACTOR` | Minimum improvement in validation targets to continue iterating | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_K`, `NLPVALIDATIONTARGET_K` | Optimality target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_R`, `NLPVALIDATIONTARGET_R` | Feasiblity target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTOL_A`, `NLPVALIDATIONTOL_A` | Absolute tolerance for the XSLPvalidate procedure | SLP, Tolerances
`XSLP_VALIDATIONTOL_K`, `NLPVALIDATIONTOL_K` | Relative tolerance for the XSLPvalidatekkt procedure | SLP, Tolerances
`XSLP_VCOUNT`, `SLPVCOUNT` | Number of SLP iterations over which to measure static objective \(3\) convergence | SLP, SLP-convergence
`XSLP_VLIMIT`, `SLPVLIMIT` | Number of SLP iterations after which static objective \(3\) convergence testing starts | SLP, SLP-convergence
`XSLP_VTOL_A`, `SLPVTOL_A` | Absolute static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VTOL_R`, `SLPVTOL_R` | Relative static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WCOUNT`, `SLPWCOUNT` | Number of SLP iterations over which to measure the objective for the extended convergence continuation criterion | SLP, SLP-convergence
`XSLP_WTOL_A`, `SLPWTOL_A` | Absolute extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WTOL_R`, `SLPWTOL_R` | Relative extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XCOUNT`, `SLPXCOUNT` | Number of SLP iterations over which to measure static objective \(1\) convergence | SLP, SLP-convergence
`XSLP_XLIMIT`, `SLPXLIMIT` | Number of SLP iterations up to which static objective \(1\) convergence testing is performed | Limits, SLP, SLP-convergence
`XSLP_XTOL_A`, `SLPXTOL_A` | Absolute static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XTOL_R`, `SLPXTOL_R` | Relative static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ZEROCRITERION`, `SLPZEROCRITERION` | Bitmap determining the behavior of the placeholder deletion procedure | Bit-vector, SLP
`XSLP_ZEROCRITERIONCOUNT`, `SLPZEROCRITERIONCOUNT` | Number of consecutive times a placeholder entry is zero before being considered for deletion | Limits, SLP
`XSLP_ZEROCRITERIONSTART`, `SLPZEROCRITERIONSTART` | SLP iteration at which criteria for deletion of placeholder entries are first activated. | SLP

##### SLP attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_COEFFICIENTS`, `SLPCOEFFICIENTS` | Number of nonlinear coefficients | Problem Information, SLP
`XSLP_CURRENTDELTACOST`, `SLPCURRENTDELTACOST` | Current value of penalty cost multiplier for penalty delta vectors | SLP, Solution
`XSLP_CURRENTERRORCOST`, `SLPCURRENTERRORCOST` | Current value of penalty cost multiplier for penalty error vectors | SLP, Solution
`XSLP_DELTAS`, `SLPDELTAS` | Number of delta vectors created during augmentation | Problem Information, SLP
`XSLP_ECFCOUNT`, `SLPECFCOUNT` | Number of infeasible constraints found at the point of linearization | Linearizations, SLP
`XSLP_ERRORCOSTS`, `SLPERRORCOSTS` | Total penalty costs in the solution | SLP, Solution
`XSLP_EXPLOREDELTAS`, `SLPEXPLOREDELTAS` | Number of variables with an exploration-type delta set up in the problem | Problem Information, SLP
`XSLP_IMPLICITVARIABLES`, `NLPIMPLICITVARIABLES` | Number of SLP variables appearing only in coefficients | Problem Information, SLP
`XSLP_INTEGERDELTAS`, `SLPINTEGERDELTAS` | Number of variables set up with an integer delta in the problem | Problem Information, SLP
`XSLP_KEEPBESTITER`, `NLPKEEPBESTITER` | The iteration in which the returned solution has been found. | SLP, Solution
`XSLP_MINUSPENALTYERRORS`, `SLPMINUSPENALTYERRORS` | Number of negative penalty error vectors | Problem Information, SLP
`XSLP_MODELCOLS`, `NLPMODELCOLS` | Number of model columns in the problem | SLP
`XSLP_MODELROWS`, `NLPMODELROWS` | Number of model rows in the problem | SLP
`XSLP_NONCONSTANTCOEFFS`, `SLPNONCONSTANTCOEFFS` | Number of coefficients in the augmented problem that might change between SLP iterations | SLP
`XSLP_PENALTYDELTACOLUMN`, `SLPPENALTYDELTACOLUMN` | Index of column costing the penalty delta row | Problem Information, SLP
`XSLP_PENALTYDELTAROW`, `SLPPENALTYDELTAROW` | Index of equality row holding the penalties for delta vectors | Problem Information, SLP
`XSLP_PENALTYDELTAS`, `SLPPENALTYDELTAS` | Number of penalty delta vectors | Problem Information, SLP
`XSLP_PENALTYDELTATOTAL`, `SLPPENALTYDELTATOTAL` | Total activity of penalty delta vectors | SLP, Solution
`XSLP_PENALTYDELTAVALUE`, `SLPPENALTYDELTAVALUE` | Total penalty cost attributed to penalty delta vectors | SLP, Solution
`XSLP_PENALTYERRORCOLUMN`, `SLPPENALTYERRORCOLUMN` | Index of column costing the penalty error row | Problem Information, SLP
`XSLP_PENALTYERRORROW`, `SLPPENALTYERRORROW` | Index of equality row holding the penalties for penalty error vectors | Problem Information, SLP
`XSLP_PENALTYERRORS`, `SLPPENALTYERRORS` | Number of penalty error vectors | Problem Information, SLP
`XSLP_PENALTYERRORTOTAL`, `SLPPENALTYERRORTOTAL` | Total activity of penalty error vectors | SLP, Solution
`XSLP_PENALTYERRORVALUE`, `SLPPENALTYERRORVALUE` | Total penalty cost attributed to penalty error vectors | SLP, Solution
`XSLP_PLUSPENALTYERRORS`, `SLPPLUSPENALTYERRORS` | Number of positive penalty error vectors | Problem Information, SLP
`XSLP_SBXCONVERGED`, `SLPSBXCONVERGED` | Number of step-bounded variables converged only on extended criteria | SLP, SLP-convergence
`XSLP_SEMICONTDELTAS`, `SLPSEMICONTDELTAS` | Number of variables with a minimum perturbation step set up in the problem | Problem Information, SLP
`XSLP_UCCONSTRAINEDCOUNT`, `SLPUCCONSTRAINEDCOUNT` | Number of unconverged variables with coefficients in constraining rows | SLP, SLP-convergence
`XSLP_UNCONVERGED`, `SLPUNCONVERGED` | Number of unconverged values | SLP, SLP-convergence
`XSLP_VARIABLES`, `NLPVARIABLES` | Number of SLP variables | Data Information, SLP
`XSLP_VSOLINDEX` | Vertex solution index | SLP, Solution
`XSLP_ZEROESRESET`, `SLPZEROESRESET` | Number of placeholder entries set to zero | SLP
`XSLP_ZEROESRETAINED`, `SLPZEROESRETAINED` | Number of potentially zero placeholders left untouched | SLP
`XSLP_ZEROESTOTAL`, `SLPZEROESTOTAL` | Number of potential zero placeholder entries | SLP

#### Section 18.31 SLP-convergence


Reference section for functions, controls, and attributes for convergence criteria within the sequential linear programming solver SLP.

##### SLP-convergence library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbslpitervar` | Add a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XPRSremovecbslpitervar` | Removes a callback function previously added by `XPRSaddcbslpitervar`. | Callback, SLP, SLP-convergence
`XSLPsetcbitervar, XPRSsetcbslpitervar` | Set a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence

##### SLP-convergence controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_ATOL_A`, `SLPATOL_A` | Absolute delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ATOL_R`, `SLPATOL_R` | Relative delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_CONVERGENCEOPS`, `SLPCONVERGENCEOPS` | Bit map describing which convergence tests should be carried out | Bit-vector, SLP, SLP-convergence
`XSLP_CTOL`, `SLPCTOL` | Closure convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ECFCHECK`, `SLPECFCHECK` | Check feasibility at the point of linearization for extended convergence criteria | SLP, SLP-convergence
`XSLP_ECFTOL_A`, `SLPECFTOL_A` | Absolute tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ECFTOL_R`, `SLPECFTOL_R` | Relative tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_EVTOL_A`, `SLPEVTOL_A` | Absolute tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_EVTOL_R`, `SLPEVTOL_R` | Relative tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_ITOL_A`, `SLPITOL_A` | Absolute impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ITOL_R`, `SLPITOL_R` | Relative impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MIPOCOUNT`, `SLPMIPOCOUNT` | Number of SLP iterations at each node over which to measure objective function variation | MISLP, SLP-convergence
`XSLP_MIPOTOL_A`, `SLPMIPOTOL_A` | Absolute objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MIPOTOL_R`, `SLPMIPOTOL_R` | Relative objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MTOL_A`, `SLPMTOL_A` | Absolute effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MTOL_R`, `SLPMTOL_R` | Relative effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MVTOL`, `SLPMVTOL` | Marginal value tolerance for determining if a constraint is slack | SLP, SLP-convergence, Tolerances
`XSLP_OCOUNT`, `SLPOCOUNT` | Number of SLP iterations over which to measure objective function variation for static objective \(2\) convergence criterion | SLP, SLP-convergence
`XSLP_OTOL_A`, `SLPOTOL_A` | Absolute static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_OTOL_R`, `SLPOTOL_R` | Relative static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOL_A`, `SLPSTOL_A` | Absolute slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOL_R`, `SLPSTOL_R` | Relative slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONFACTOR`, `NLPVALIDATIONFACTOR` | Minimum improvement in validation targets to continue iterating | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_K`, `NLPVALIDATIONTARGET_K` | Optimality target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_R`, `NLPVALIDATIONTARGET_R` | Feasiblity target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VCOUNT`, `SLPVCOUNT` | Number of SLP iterations over which to measure static objective \(3\) convergence | SLP, SLP-convergence
`XSLP_VLIMIT`, `SLPVLIMIT` | Number of SLP iterations after which static objective \(3\) convergence testing starts | SLP, SLP-convergence
`XSLP_VTOL_A`, `SLPVTOL_A` | Absolute static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VTOL_R`, `SLPVTOL_R` | Relative static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WCOUNT`, `SLPWCOUNT` | Number of SLP iterations over which to measure the objective for the extended convergence continuation criterion | SLP, SLP-convergence
`XSLP_WTOL_A`, `SLPWTOL_A` | Absolute extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WTOL_R`, `SLPWTOL_R` | Relative extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XCOUNT`, `SLPXCOUNT` | Number of SLP iterations over which to measure static objective \(1\) convergence | SLP, SLP-convergence
`XSLP_XLIMIT`, `SLPXLIMIT` | Number of SLP iterations up to which static objective \(1\) convergence testing is performed | Limits, SLP, SLP-convergence
`XSLP_XTOL_A`, `SLPXTOL_A` | Absolute static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XTOL_R`, `SLPXTOL_R` | Relative static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances

##### SLP-convergence attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_SBXCONVERGED`, `SLPSBXCONVERGED` | Number of step-bounded variables converged only on extended criteria | SLP, SLP-convergence
`XSLP_UCCONSTRAINEDCOUNT`, `SLPUCCONSTRAINEDCOUNT` | Number of unconverged variables with coefficients in constraining rows | SLP, SLP-convergence
`XSLP_UNCONVERGED`, `SLPUNCONVERGED` | Number of unconverged values | SLP, SLP-convergence

#### Section 18.32 Solution Process


Reference section for functions, controls, and attributes related to the invocation of a solution algorithm, and the most fundamental status information after the solver returns.

##### Solution Process library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPcascade, XPRSslpcascade` | Re-calculate consistent values for SLP variables based on the current values of the remaining variables. | Cascading, SLP, Solution Process
`XSLPconstruct, XPRSslpconstruct` | Create the full augmented SLP matrix and data structures, ready for optimization | SLP, Solution Process
`XSLPfixpenalties, XPRSslpfixpenalties` | Fixe the values of the error vectors | Solution Process
`XSLPinterrupt` | Interrupts the current SLP optimization | Solution Process
`XSLPnlpoptimize, XPRSnlpoptimize` | Maximize or minimize an SLP problem | Solution Process
`XSLPreinitialize, XPRSslpreinitialize` | Reset the SLP problem to match a just augmented system | SLP, Solution Process
`XSLPunconstruct, XPRSslpunconstruct` | Removes the augmentation and returns the problem to its pre-linearization state | SLP, Solution Process
`XSLPupdatelinearization, XPRSslpupdatelinearization` | Updates the current linearization | SLP, Solution Process

##### Solution Process controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_ALGORITHM`, `KNITRO_PARAM_ALGORITHM` | Indicates which algorithm to use to solve nonlinear problems | Knitro, Solution Process
`XKTR_PARAM_MIP_LPALG`, `KNITRO_PARAM_MIP_LPALG` | Specifies which algorithm to use for any linear programming \(LP\) subproblem solves that may occur in the MIP branch and bound procedure. | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_METHOD`, `KNITRO_PARAM_MIP_METHOD` | Specifies which MIP method to use. | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_ROOTALG`, `KNITRO_PARAM_MIP_ROOTALG` | Specifies which algorithm to use for the root node solve in MIP \(same options as `XKTR_PARAM_ALGORITHM` user option\). | Knitro-MINLP, Solution Process
`XSLP_NLPSOLVER`, `NLPSOLVER` | Controls whether to call FICO Xpress Global or one of the local solvers | Solution Process
`XSLP_SOLVER`, `LOCALSOLVER` | Selects the library to use for local solves | Solution Process

##### Solution Process attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_ITER`, `SLPITER` | SLP iteration count | Solution Process
`XSLP_NLPSTATUS`, `NLPSTATUS` | The solution status of the problem. | Solution Process
`XSLP_OPTTIME`, `NLPOPTTIME` | Time spent in optimization | Solution Process
`XSLP_SOLVERSELECTED`, `LOCALSOLVERSELECTED` | Includes information of which Xpress solver has been used to solve the problem | Solution Process
`XSLP_STATUS`, `SLPSTATUS` | Bitmap holding the problem convergence status | Solution Process
`XSLP_STOPSTATUS`, `NLPSTOPSTATUS` | Status of the optimization process. | Solution Process

#### Section 18.33 Solution


Reference section for functions, controls, and attributes related to the handling of optimal or intermediate solutions.

##### Solution library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPcalcslacks, XPRSnlpcalcslacks` | Calculate the slack values for the provided solution in the non-linear problem | Solution
`XSLPevaluatecoef, XPRSslpevaluatecoef` | Evaluate a coefficient using the current values of the variables | Solution
`XSLPevaluateformula, XPRSnlpevaluateformula` | Evaluate a formula using the current values of the variables | Solution
`XSLPgetcolinfo, XPRSslpgetcolinfo` | Get current column information. | SLP, Solution
`XSLPgetrowinfo, XPRSslpgetrowinfo` | Get current row information. | SLP, Solution
`XSLPgetrowstatus, XPRSslpgetrowstatus` | Retrieve the status setting of a constraint | Bit-vector, SLP, Solution
`XSLPvalidate, XPRSnlpvalidate` | Validate the feasibility of constraints in a converged solution | Solution
`XSLPvalidatekkt, XPRSnlpvalidatekkt` | Validates the first order optimality conditions also known as the Karush-Kuhn-Tucker \(KKT\) conditions versus the currect solution | Solution
`XSLPvalidateprob, XPRSnlpvalidateprob` | Validates the current problem formulation and statement | Solution
`XSLPvalidaterow, XPRSnlpvalidaterow` | Prints an extensive analysis on a given constraint of the SLP problem | Solution
`XSLPvalidatevector, XPRSnlpvalidatevector` | Validate the feasibility of constraints for a given solution | Solution
`XSLPwriteslxsol` | Write the current solution to an MPS like file format | File IO, Solution

##### Solution controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_FILTER`, `SLPFILTER` | Bit map for controlling solution updates | Bit-vector, SLP, Solution
`XSLP_MERITLAMBDA`, `NLPMERITLAMBDA` | Factor by which the net objective is taken into account in the merit function | SLP, Solution

##### Solution attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_CURRENTDELTACOST`, `SLPCURRENTDELTACOST` | Current value of penalty cost multiplier for penalty delta vectors | SLP, Solution
`XSLP_CURRENTERRORCOST`, `SLPCURRENTERRORCOST` | Current value of penalty cost multiplier for penalty error vectors | SLP, Solution
`XSLP_ERRORCOSTS`, `SLPERRORCOSTS` | Total penalty costs in the solution | SLP, Solution
`XSLP_KEEPBESTITER`, `NLPKEEPBESTITER` | The iteration in which the returned solution has been found. | SLP, Solution
`XSLP_MIPSOLS`, `SLPMIPSOLS` | Number of integer solutions found in MISLP. | MISLP, Solution
`XSLP_OBJVAL`, `NLPOBJVAL` | Objective function value excluding any penalty costs | Solution
`XSLP_PENALTYDELTATOTAL`, `SLPPENALTYDELTATOTAL` | Total activity of penalty delta vectors | SLP, Solution
`XSLP_PENALTYDELTAVALUE`, `SLPPENALTYDELTAVALUE` | Total penalty cost attributed to penalty delta vectors | SLP, Solution
`XSLP_PENALTYERRORTOTAL`, `SLPPENALTYERRORTOTAL` | Total activity of penalty error vectors | SLP, Solution
`XSLP_PENALTYERRORVALUE`, `SLPPENALTYERRORVALUE` | Total penalty cost attributed to penalty error vectors | SLP, Solution
`XSLP_SOLSTATUS`, `NLPSOLSTATUS` | Indicates the type of solution returned by the solver. | Solution
`XSLP_VALIDATIONINDEX_A`, `NLPVALIDATIONINDEX_A` | Absolute validation index | Solution
`XSLP_VALIDATIONINDEX_K`, `NLPVALIDATIONINDEX_K` | Relative first order optimality validation index | Solution
`XSLP_VALIDATIONINDEX_R`, `NLPVALIDATIONINDEX_R` | Relative validation index | Solution
`XSLP_VALIDATIONNETOBJ`, `NLPVALIDATIONNETOBJ` | Net objective as calculated by validation | Solution
`XSLP_VALIDATIONSTATUS`, `NLPVALIDATIONSTATUS` | Feasiblity status of the current solution. | Solution
`XSLP_VSOLINDEX` | Vertex solution index | SLP, Solution

#### Section 18.34 Tolerances


Reference section for functions, controls, and attributes related to feasibility and optimality tolerances.

##### Tolerances controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_BAR_FEASMODETOL`, `KNITRO_PARAM_BAR_FEASMODETOL` | Specifies the tolerance in equation that determines whether Knitro will force subsequent iterates to remain feasible. | Knitro, Tolerances
`XKTR_PARAM_FEASTOL`, `KNITRO_PARAM_FEASTOL` | Specifies the final relative stopping tolerance for the feasibility error. | Knitro, Tolerances
`XKTR_PARAM_FEASTOLABS`, `KNITRO_PARAM_FEASTOLABS` | Specifies the final absolute stopping tolerance for the feasibility error. | Knitro, Tolerances
`XKTR_PARAM_INFEASTOL`, `KNITRO_PARAM_INFEASTOL` | Specifies the \(relative\) tolerance used for declaring infeasibility of a model. | Knitro, Tolerances
`XKTR_PARAM_MIP_INTEGERTOL`, `KNITRO_PARAM_INTEGERTOL` | This value specifies the threshold for deciding whether or not a variable is determined to be an integer. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPABS`, `KNITRO_PARAM_INTGAPABS` | The absolute integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPREL`, `KNITRO_PARAM_INTGAPREL` | The relative integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_OPTTOL`, `KNITRO_PARAM_OPTTOL` | Specifies the final relative stopping tolerance for the KKT \(optimality\) error. | Knitro, Tolerances
`XKTR_PARAM_OPTTOLABS`, `KNITRO_PARAM_OPTTOLABS` | Specifies the final absolute stopping tolerance for the KKT \(optimality\) error. | Knitro, Tolerances
`XKTR_PARAM_PRESOLVE_TOL`, `KNITRO_PARAM_PRESOLVE_TOL` | Determines the tolerance used by the Knitro presolver to remove variables and constraints from the model. | Knitro, Presolve, Tolerances
`XKTR_PARAM_XTOL`, `KNITRO_PARAM_XTOL` | The optimization process will terminate if the relative change in all components of the solution point estimate is less than xtol. | Knitro, Tolerances
`XSLP_ATOL_A`, `SLPATOL_A` | Absolute delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ATOL_R`, `SLPATOL_R` | Relative delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_CDTOL_A`, `SLPCDTOL_A` | Absolute tolerance for deducing constant derivatives | Tolerances
`XSLP_CDTOL_R`, `SLPCDTOL_R` | Relative tolerance for deducing constant derivatives | Tolerances
`XSLP_CLAMPVALIDATIONTOL_A`, `SLPCLAMPVALIDATIONTOL_A` | Absolute validation tolerance for applying `XSLP_CLAMPSHRINK` | SLP, Tolerances
`XSLP_CLAMPVALIDATIONTOL_R`, `SLPCLAMPVALIDATIONTOL_R` | Relative validation tolerance for applying `XSLP_CLAMPSHRINK` | SLP, Tolerances
`XSLP_CTOL`, `SLPCTOL` | Closure convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_DELTA_Z`, `SLPDELTA_Z` | Tolerance used when calculating derivatives | Derivatives, Tolerances
`XSLP_DELTA_ZERO`, `SLPDELTA_ZERO` | Absolute zero acceptance tolerance used when calculating derivatives | Derivatives, Tolerances
`XSLP_DJTOL`, `SLPDJTOL` | Tolerance on DJ value for determining if a variable is at its step bound | SLP, Tolerances
`XSLP_DRCOLDJTOL`, `SLPDRCOLDJTOL` | Reduced cost tolerance on the delta variable when fixing due to the determining column being below `XSLP_DRCOLTOL`. | Cascading, SLP, Tolerances
`XSLP_DRCOLTOL`, `SLPDRCOLTOL` | The minimum absolute magnitude of a determining column, for which the determined variable is still regarded as well defined | Cascading, SLP, Tolerances
`XSLP_ECFTOL_A`, `SLPECFTOL_A` | Absolute tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ECFTOL_R`, `SLPECFTOL_R` | Relative tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ERRORTOL_A`, `SLPERRORTOL_A` | Absolute tolerance for error vectors | SLP, Tolerances
`XSLP_ERRORTOL_P`, `SLPERRORTOL_P` | Absolute tolerance for printing error vectors | SLP, Tolerances
`XSLP_ETOL_A`, `SLPETOL_A` | Absolute tolerance on penalty vectors | SLP, Tolerances
`XSLP_ETOL_R`, `SLPETOL_R` | Relative tolerance on penalty vectors | SLP, Tolerances
`XSLP_EVTOL_A`, `SLPEVTOL_A` | Absolute tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_EVTOL_R`, `SLPEVTOL_R` | Relative tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_FEASTOLTARGET`, `SLPFEASTOLTARGET` | When set, this defines a target feasibility tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_ITOL_A`, `SLPITOL_A` | Absolute impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ITOL_R`, `SLPITOL_R` | Relative impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MIPCUTOFF_A`, `SLPMIPCUTOFF_A` | Absolute objective function cutoff for MIP termination | MISLP, Tolerances
`XSLP_MIPCUTOFF_R`, `SLPMIPCUTOFF_R` | Absolute objective function cutoff for MIP termination | MISLP, Tolerances
`XSLP_MIPERRORTOL_A`, `SLPMIPERRORTOL_A` | Absolute penalty error cost tolerance for MIP cut-off | MISLP, Tolerances
`XSLP_MIPERRORTOL_R`, `SLPMIPERRORTOL_R` | Relative penalty error cost tolerance for MIP cut-off | MISLP, Tolerances
`XSLP_MIPOTOL_A`, `SLPMIPOTOL_A` | Absolute objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MIPOTOL_R`, `SLPMIPOTOL_R` | Relative objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MTOL_A`, `SLPMTOL_A` | Absolute effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MTOL_R`, `SLPMTOL_R` | Relative effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MVTOL`, `SLPMVTOL` | Marginal value tolerance for determining if a constraint is slack | SLP, SLP-convergence, Tolerances
`XSLP_OPTIMALITYTOLTARGET`, `SLPOPTIMALITYTOLTARGET` | When set, this defines a target optimality tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_OTOL_A`, `SLPOTOL_A` | Absolute static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_OTOL_R`, `SLPOTOL_R` | Relative static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_PRESOLVE_ELIMTOL`, `NLPPRESOLVE_ELIMTOL` | Tolerance for nonlinear eliminations during SLP presolve | Presolve, Tolerances
`XSLP_PRESOLVEZERO`, `NLPPRESOLVEZERO` | Minimum absolute value for a variable which is identified as nonzero during SLP presolve | Presolve, Tolerances
`XSLP_STOL_A`, `SLPSTOL_A` | Absolute slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOL_R`, `SLPSTOL_R` | Relative slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONFACTOR`, `NLPVALIDATIONFACTOR` | Minimum improvement in validation targets to continue iterating | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_K`, `NLPVALIDATIONTARGET_K` | Optimality target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_R`, `NLPVALIDATIONTARGET_R` | Feasiblity target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTOL_A`, `NLPVALIDATIONTOL_A` | Absolute tolerance for the XSLPvalidate procedure | SLP, Tolerances
`XSLP_VALIDATIONTOL_K`, `NLPVALIDATIONTOL_K` | Relative tolerance for the XSLPvalidatekkt procedure | SLP, Tolerances
`XSLP_VALIDATIONTOL_R`, `NLPVALIDATIONTOL_R` | Relative tolerance for the XSLPvalidate procedure | Tolerances
`XSLP_VTOL_A`, `SLPVTOL_A` | Absolute static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VTOL_R`, `SLPVTOL_R` | Relative static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WTOL_A`, `SLPWTOL_A` | Absolute extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WTOL_R`, `SLPWTOL_R` | Relative extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XTOL_A`, `SLPXTOL_A` | Absolute static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XTOL_R`, `SLPXTOL_R` | Relative static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ZERO`, `NLPZERO` | Absolute tolerance | Tolerances

#### Section 18.35 User Functions


Reference section for functions, controls, and attributes related to user functions \(compare [User Functions](#chapUserFunctions)\).

##### User Functions library functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLPadduserfunction, XPRSnlpadduserfunction` | Add user function definitions to an SLP problem. | User Functions
`XSLPdeluserfunction, XPRSnlpdeluserfunction` | Delete a user function from the current problem | User Functions
`XSLPgetindex` | Retrieve the index of an Xpress NonLinear entity with a given name | Problem Information, User Functions
`XSLPimportlibfunc, XPRSnlpimportlibfunc` | Imports a function from a library file to be called as a user function | User Functions

##### User Functions controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_EVALUATE`, `NLPEVALUATE` | Evaluation strategy for user functions | User Functions
`XSLP_FUNCEVAL`, `NLPFUNCEVAL` | Bit map for determining the method of evaluating user functions and their derivatives | Derivatives, User Functions
`XSLP_THREADSAFEUSERFUNC`, `NLPTHREADSAFEUSERFUNC` | Defines if user functions are allowed to be called in parallel | Parallel, User Functions

##### User Functions attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_UFINSTANCES` | Number of user function instances | User Functions
`XSLP_UFS`, `NLPUFS` | Number of user functions | User Functions
`XSLP_USERFUNCCALLS`, `NLPUSERFUNCCALLS` | Number of calls made to user functions | User Functions

### Chapter 19 Problem Attributes


During the optimization process, various properties of the problem being solved are stored and made available to users of the Xpress NonLinear Libraries in the form of _problem attributes_. These can be accessed in much the same manner as the controls. Examples of problem attributes include the sizes of arrays, for which library users may need to allocate space before the arrays themselves are retrieved. A full list of the attributes available and their types may be found in this chapter.

Library users are provided with the following functions for obtaining the values of attributes:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XSLPgetintattrib` | `XSLPgetdblattrib` | 
`XSLPgetptrattrib` | `XSLPgetstrattrib` | 

The attributes listed in this chapter are all prefixed with `XSLP_`. Most of them also exist within the Optimizer library with an NLP or SLP prefix, e.g., `XPRS_NLPSOLSTATUS`. It is possible to use the above functions with other attributes for the Xpress Optimizer \(attributes prefixed with `XPRS_`\). For details of the Optimizer attributes, see the Optimizer manual.

Example of the usage of the functions:

```
XSLPgetintattrib(Prob, XSLP_ITER, &nIter);
printf("The number of SLP iterations is %d\n", nIter);
XSLPgetdblattrib(Prob, XSLP_ERRORCOSTS, &Errors);
printf("and the total error cost is %lg\n", Errors);

```


The following is a list of all the Xpress NonLinear attributes:



_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_COEFFICIENTS`, `SLPCOEFFICIENTS` | Number of nonlinear coefficients | Problem Information, SLP
`XSLP_CURRENTDELTACOST`, `SLPCURRENTDELTACOST` | Current value of penalty cost multiplier for penalty delta vectors | SLP, Solution
`XSLP_CURRENTERRORCOST`, `SLPCURRENTERRORCOST` | Current value of penalty cost multiplier for penalty error vectors | SLP, Solution
`XSLP_DELTAS`, `SLPDELTAS` | Number of delta vectors created during augmentation | Problem Information, SLP
`XSLP_ECFCOUNT`, `SLPECFCOUNT` | Number of infeasible constraints found at the point of linearization | Linearizations, SLP
`XSLP_EQUALSCOLUMN`, `NLPEQUALSCOLUMN` | Index of the reserved "=" column | Problem Information
`XSLP_ERRORCOSTS`, `SLPERRORCOSTS` | Total penalty costs in the solution | SLP, Solution
`XSLP_EXPLOREDELTAS`, `SLPEXPLOREDELTAS` | Number of variables with an exploration-type delta set up in the problem | Problem Information, SLP
`XSLP_IFS`, `NLPIFS` | Number of internal functions | Misc
`XSLP_IMPLICITVARIABLES`, `NLPIMPLICITVARIABLES` | Number of SLP variables appearing only in coefficients | Problem Information, SLP
`XSLP_INTEGERDELTAS`, `SLPINTEGERDELTAS` | Number of variables set up with an integer delta in the problem | Problem Information, SLP
`XSLP_ITER`, `SLPITER` | SLP iteration count | Solution Process
`XSLP_JOBID`, `NLPJOBID` | Unique identifier for the current job | Misc, Multistart
`XSLP_KEEPBESTITER`, `NLPKEEPBESTITER` | The iteration in which the returned solution has been found. | SLP, Solution
`XSLP_MINUSPENALTYERRORS`, `SLPMINUSPENALTYERRORS` | Number of negative penalty error vectors | Problem Information, SLP
`XSLP_MIPITER`, `SLPMIPITER` | Total number of SLP iterations in MISLP | MISLP
`XSLP_MIPNODES`, `SLPMIPNODES` | Number of nodes explored in SLP-in-MIP. | MISLP
`XSLP_MIPPROBLEM` | The underlying Optimizer MIP problem. | MISLP
`XSLP_MIPSOLS`, `SLPMIPSOLS` | Number of integer solutions found in MISLP. | MISLP, Solution
`XSLP_MODELCOLS`, `NLPMODELCOLS` | Number of model columns in the problem | SLP
`XSLP_MODELROWS`, `NLPMODELROWS` | Number of model rows in the problem | SLP
`XSLP_MSSTATUS` | Status of the mutlistart search | Multistart
`XSLP_NLPSTATUS`, `NLPSTATUS` | The solution status of the problem. | Solution Process
`XSLP_NONCONSTANTCOEFFS`, `SLPNONCONSTANTCOEFFS` | Number of coefficients in the augmented problem that might change between SLP iterations | SLP
`XSLP_NONLINEARCONSTRAINTS`, `NONLINEARCONSTRAINTS` | Number of nonlinear constraints in the problem | Problem Information
`XSLP_OBJVAL`, `NLPOBJVAL` | Objective function value excluding any penalty costs | Solution
`XSLP_OPTTIME`, `NLPOPTTIME` | Time spent in optimization | Solution Process
`XSLP_ORIGINALCOLS`, `NLPORIGINALCOLS` | Number of model columns in the extended original problem | Problem Information
`XSLP_ORIGINALROWS`, `NLPORIGINALROWS` | Number of model rows in the extended original problem | Problem Information
`XSLP_PENALTYDELTACOLUMN`, `SLPPENALTYDELTACOLUMN` | Index of column costing the penalty delta row | Problem Information, SLP
`XSLP_PENALTYDELTAROW`, `SLPPENALTYDELTAROW` | Index of equality row holding the penalties for delta vectors | Problem Information, SLP
`XSLP_PENALTYDELTAS`, `SLPPENALTYDELTAS` | Number of penalty delta vectors | Problem Information, SLP
`XSLP_PENALTYDELTATOTAL`, `SLPPENALTYDELTATOTAL` | Total activity of penalty delta vectors | SLP, Solution
`XSLP_PENALTYDELTAVALUE`, `SLPPENALTYDELTAVALUE` | Total penalty cost attributed to penalty delta vectors | SLP, Solution
`XSLP_PENALTYERRORCOLUMN`, `SLPPENALTYERRORCOLUMN` | Index of column costing the penalty error row | Problem Information, SLP
`XSLP_PENALTYERRORROW`, `SLPPENALTYERRORROW` | Index of equality row holding the penalties for penalty error vectors | Problem Information, SLP
`XSLP_PENALTYERRORS`, `SLPPENALTYERRORS` | Number of penalty error vectors | Problem Information, SLP
`XSLP_PENALTYERRORTOTAL`, `SLPPENALTYERRORTOTAL` | Total activity of penalty error vectors | SLP, Solution
`XSLP_PENALTYERRORVALUE`, `SLPPENALTYERRORVALUE` | Total penalty cost attributed to penalty error vectors | SLP, Solution
`XSLP_PLUSPENALTYERRORS`, `SLPPLUSPENALTYERRORS` | Number of positive penalty error vectors | Problem Information, SLP
`XSLP_PRESOLVEELIMINATIONS`, `NLPPRESOLVEELIMINATIONS` | Number of SLP variables eliminated by `XSLPpresolve` | Presolve
`XSLP_PRESOLVESTATE` | Indicates if the problem is presolved | Presolve
`XSLP_PRIMALINTEGRAL`, `NLPPRIMALINTEGRAL` | Local primal integral of the solve | Misc
`XSLP_SBXCONVERGED`, `SLPSBXCONVERGED` | Number of step-bounded variables converged only on extended criteria | SLP, SLP-convergence
`XSLP_SEMICONTDELTAS`, `SLPSEMICONTDELTAS` | Number of variables with a minimum perturbation step set up in the problem | Problem Information, SLP
`XSLP_SOLSTATUS`, `NLPSOLSTATUS` | Indicates the type of solution returned by the solver. | Solution
`XSLP_SOLVERSELECTED`, `LOCALSOLVERSELECTED` | Includes information of which Xpress solver has been used to solve the problem | Solution Process
`XSLP_STATUS`, `SLPSTATUS` | Bitmap holding the problem convergence status | Solution Process
`XSLP_STOPSTATUS`, `NLPSTOPSTATUS` | Status of the optimization process. | Solution Process
`XSLP_TOTALEVALUATIONERRORS`, `NLPTOTALEVALUATIONERRORS` | The total number of evaluation errors during the solve | Numerics
`XSLP_UCCONSTRAINEDCOUNT`, `SLPUCCONSTRAINEDCOUNT` | Number of unconverged variables with coefficients in constraining rows | SLP, SLP-convergence
`XSLP_UFINSTANCES` | Number of user function instances | User Functions
`XSLP_UFS`, `NLPUFS` | Number of user functions | User Functions
`XSLP_UNCONVERGED`, `SLPUNCONVERGED` | Number of unconverged values | SLP, SLP-convergence
`XSLP_USEDERIVATIVES`, `NLPUSEDERIVATIVES` | Indicates whether numeric or analytic derivatives were used to create the linear approximations and solve the problem | Derivatives
`XSLP_USERFUNCCALLS`, `NLPUSERFUNCCALLS` | Number of calls made to user functions | User Functions
`XSLP_VALIDATIONINDEX_A`, `NLPVALIDATIONINDEX_A` | Absolute validation index | Solution
`XSLP_VALIDATIONINDEX_K`, `NLPVALIDATIONINDEX_K` | Relative first order optimality validation index | Solution
`XSLP_VALIDATIONINDEX_R`, `NLPVALIDATIONINDEX_R` | Relative validation index | Solution
`XSLP_VALIDATIONNETOBJ`, `NLPVALIDATIONNETOBJ` | Net objective as calculated by validation | Solution
`XSLP_VALIDATIONSTATUS`, `NLPVALIDATIONSTATUS` | Feasiblity status of the current solution. | Solution
`XSLP_VARIABLES`, `NLPVARIABLES` | Number of SLP variables | Data Information, SLP
`XSLP_VERSIONDATE` | Date of creation of Xpress NonLinear | Misc
`XSLP_VSOLINDEX` | Vertex solution index | SLP, Solution
`XSLP_XPRSPROBLEM` | The underlying Optimizer problem | Misc
`XSLP_XSLPPROBLEM` | The Xpress NonLinear problem | Misc
`XSLP_ZEROESRESET`, `SLPZEROESRESET` | Number of placeholder entries set to zero | SLP
`XSLP_ZEROESRETAINED`, `SLPZEROESRETAINED` | Number of potentially zero placeholders left untouched | SLP
`XSLP_ZEROESTOTAL`, `SLPZEROESTOTAL` | Number of potential zero placeholder entries | SLP

#### Section 19.1 Double problem attributes


#### XSLP_CURRENTDELTACOST, SLPCURRENTDELTACOST

_**Description:**_    Current value of penalty cost multiplier for penalty delta vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_CURRENTERRORCOST`

_**Category:**_ Attribute

#### XSLP_CURRENTERRORCOST, SLPCURRENTERRORCOST

_**Description:**_    Current value of penalty cost multiplier for penalty error vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_CURRENTDELTACOST`

_**Category:**_ Attribute

#### XSLP_ERRORCOSTS, SLPERRORCOSTS

_**Description:**_    Total penalty costs in the solution
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_OPTTIME, NLPOPTTIME

_**Description:**_    Time spent in optimization
 
_**Type:**_ Double

_**Topic area:**_ 
Solution Process

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_OBJVAL, NLPOBJVAL

_**Description:**_    Objective function value excluding any penalty costs
 
_**Type:**_ Double

_**Topic area:**_ 
Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_PENALTYDELTATOTAL, SLPPENALTYDELTATOTAL

_**Description:**_    Total activity of penalty delta vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_PENALTYDELTAVALUE, SLPPENALTYDELTAVALUE

_**Description:**_    Total penalty cost attributed to penalty delta vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_PENALTYERRORTOTAL, SLPPENALTYERRORTOTAL

_**Description:**_    Total activity of penalty error vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_PENALTYERRORVALUE, SLPPENALTYERRORVALUE

_**Description:**_    Total penalty cost attributed to penalty error vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_PRIMALINTEGRAL, NLPPRIMALINTEGRAL

_**Description:**_    Local primal integral of the solve
 
_**Type:**_ Double

_**Topic area:**_ 
Misc

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_VALIDATIONINDEX_A, NLPVALIDATIONINDEX_A

_**Description:**_    Absolute validation index
 
_**Type:**_ Double

_**Topic area:**_ 
Solution

_**Set by routines:**_ `XSLPvalidate`
_**Category:**_ Attribute

#### XSLP_VALIDATIONINDEX_K, NLPVALIDATIONINDEX_K

_**Description:**_    Relative first order optimality validation index
 
_**Type:**_ Double

_**Topic area:**_ 
Solution

_**Set by routines:**_ `XSLPvalidatekkt`
_**Category:**_ Attribute

#### XSLP_VALIDATIONINDEX_R, NLPVALIDATIONINDEX_R

_**Description:**_    Relative validation index
 
_**Type:**_ Double

_**Topic area:**_ 
Solution

_**Set by routines:**_ `XSLPvalidate`
_**Category:**_ Attribute

#### XSLP_VALIDATIONNETOBJ, NLPVALIDATIONNETOBJ

_**Description:**_    Net objective as calculated by validation
 
_**Type:**_ Double

_**Topic area:**_ 
Solution

_**Set by routines:**_ `XSLPvalidate`
_**Category:**_ Attribute

#### XSLP_VSOLINDEX

_**Description:**_    Vertex solution index
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Notes:**_

The _vertex solution index_ \( `VSOLINDEX`\) is a measure of how nearly the converged solution to a problem is at a vertex \(that is, at the intersection of a set of constraints\) of the feasible region.

Where the solution is in the middle of a face, the solution will in general have been achieved through the use of step bounds. The `VSOLINDEX` is the fraction of delta vectors which are _not_ at a bound in the solution. Therefore, a value of 1.0 means that no delta is at a step bound and therefore the solution is at a vertex of the feasible region. Smaller values indicate that there are deltas at step bounds and so the solution is further from being a vertex solution.

_**Category:**_ Attribute

#### Section 19.2 Integer problem attributes


#### XSLP_COEFFICIENTS, SLPCOEFFICIENTS

_**Description:**_    Number of nonlinear coefficients
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Note:**_
`XSLP_COEFFICIENTS` includes both coefficients \(nonlinear expressions multiplying a variable\) and formulas \(nonlinear expressions which do not multiply a variable\). See  _Coefficients and formulas_ for more information.

_**Set by routines:**_ `XSLPaddcoefs`,`XSLPchgcoef`,`XSLPloadcoefs`,`XSLPreadprob`
_**Category:**_ Attribute

#### XSLP_DELTAS, SLPDELTAS

_**Description:**_    Number of delta vectors created during augmentation
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_ECFCOUNT, SLPECFCOUNT

_**Description:**_    Number of infeasible constraints found at the point of linearization
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ECFCHECK`, `XSLP_ECFTOL_A`, `XSLP_ECFTOL_R`

_**Category:**_ Attribute

#### XSLP_EXPLOREDELTAS, SLPEXPLOREDELTAS

_**Description:**_    Number of variables with an exploration-type delta set up in the problem
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_EQUALSCOLUMN, NLPEQUALSCOLUMN

_**Description:**_    Index of the reserved "=" column
 
_**Type:**_ Integer

_**Topic area:**_ 
Problem Information

_**Note:**_
If there had been no "=" column present, it will be assumed that the user needs the index to add nonlinear terms into the problem that are not coefficients, and an "=" columns will be added to the problem, whose index is then returned. Please note, that this means that a call to XSLPgetintattrib with this attribute might make a slight modification to the problem itself.

_**Set by routines:**_ `XSLPconstruct`,`XSLPreadprob`
_**Category:**_ Attribute

#### XSLP_IFS, NLPIFS

_**Description:**_    Number of internal functions
 
_**Type:**_ Integer

_**Topic area:**_ 
Misc

_**Set by routines:**_ `XSLPcreateprob`
_**Category:**_ Attribute

#### XSLP_IMPLICITVARIABLES, NLPIMPLICITVARIABLES

_**Description:**_    Number of SLP variables appearing only in coefficients
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_INTEGERDELTAS, SLPINTEGERDELTAS

_**Description:**_    Number of variables set up with an integer delta in the problem
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_ITER, SLPITER

_**Description:**_    SLP iteration count
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_JOBID, NLPJOBID

_**Description:**_    Unique identifier for the current job
 
_**Type:**_ Integer

_**Topic areas:**_ 
Misc, Multistart

_**Note:**_
Assigned when a job is created, and can be used to identify jobs in callbacks. Note that all callback receives an optional job name that can be assigned at job creation time.

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_KEEPBESTITER, NLPKEEPBESTITER

_**Description:**_    The iteration in which the returned solution has been found.
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Solution

_**Note:**_
A zero value indicates no solution or the filter option is off. A value of '-1' indicates the initial solution has been returned.

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_MINUSPENALTYERRORS, SLPMINUSPENALTYERRORS

_**Description:**_    Number of negative penalty error vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_MIPITER, SLPMIPITER

_**Description:**_    Total number of SLP iterations in MISLP
 
_**Type:**_ Integer

_**Topic area:**_ 
MISLP

_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_MIPNODES, SLPMIPNODES

_**Description:**_    Number of nodes explored in SLP-in-MIP. This includes any nodes for which a non-linear solve has been carried out.
 
_**Type:**_ Integer

_**Topic area:**_ 
MISLP

_**Note:**_
Note that unlike `XPRS_NODES`, which can alternatively be queried after an SLP-in-MIP or an SLP-MIP-SLP solve, this only counts nodes for which SLP was called but not nodes that were cut off before solving the node relaxation. Therefore this may be smaller than the node numbers reported in the log.

_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_MIPSOLS, SLPMIPSOLS

_**Description:**_    Number of integer solutions found in MISLP. This includes solutions found during the tree search or any heuristics.
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Solution

_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_MODELCOLS, NLPMODELCOLS

_**Description:**_    Number of model columns in the problem
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Note:**_
This is the number of columns currently in the problem without any augmentation, i.e. the number of columns that describe the algebraic definition of the problem. These columns always precede the augmentation columns in order. If the problem is presolved, this may be smaller than the number of original columns in the problem. To access the number of original columns, use `XPRS_INPUTCOLS`.

_**See also:**_
`XSLP_MODELROWS`, `XPRS_INPUTROWS`, `XPRS_INPUTCOLS`.

_**Category:**_ Attribute

#### XSLP_MODELROWS, NLPMODELROWS

_**Description:**_    Number of model rows in the problem
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Note:**_
This is the number of rows currently in the problem without any augmentation, i.e. the number of rows that describe the algebraic definition of the problem. These rows always precede the augmentation rows in order. If the problem is presolved, this may be smaller than the number of original rows in the problem. To access the number of original rows, use `XPRS_INPUTROWS`.

_**See also:**_
`XSLP_MODELCOLS`, `XPRS_INPUTROWS`, `XPRS_INPUTCOLS`.

_**Category:**_ Attribute

#### XSLP_MSSTATUS

_**Description:**_    Status of the mutlistart search
 
_**Type:**_ Integer

_**Topic area:**_ 
Multistart

_**Note:**_
The value matches that of the winner job if the multistart search completes and a feasible solution has been found. If no solution is found, it is set to XSLP\_NLPSTATUS\_INFEASIBLE. If the search is terminated early, it is set to XSLP\_NLPSTATUS\_UNFINISHED \(thought in which case the winner if any is still synchronized to the base problem and the solution and `XSLP_NLPSTATUS` is available\).
_**Category:**_ Attribute

#### XSLP_NLPSTATUS, NLPSTATUS

_**Description:**_    The solution status of the problem.
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Optimization unstarted \( `XSLP_NLPSTATUS_UNSTARTED`\)
 `1`| Solution found \( `XSLP_NLPSTATUS_SOLUTION`\)
 `2`| Globally optimal \( `XSLP_NLPSTATUS_OPTIMAL`\)
 `3`| No solution found \( `XSLP_NLPSTATUS_NOSOLUTION`\)
 `4`| Proven infeasible \( `XSLP_NLPSTATUS_INFEASIBLE`\)
 `5`| Locally unbounded \( `XSLP_NLPSTATUS_UNBOUNDED`\)
 `6`| Not yet solved to completion \( `XSLP_NLPSTATUS_UNFINISHED`\)
 `7`| Could not be solved due to numerical issues \( `XSLP_NLPSTATUS_UNSOLVED`\)

_**Note:**_
`XSLP_NLPSTATUS_OPTIMAL` is only set when a globally optimal solution has been found, e.g., because the problem was convex, or because the global solver was used.

_**Note:**_
`XSLP_NLPSTATUS_SOLUTION` is set whenever a feasible solution was found. The solve may have been interrupted, or it completed without proving global optimality.

_**Note:**_
`XSLP_NLPSTATUS_NOSOLUTION` is set when the solve completed without finding a feasible solution, possibly because the problem is locally infeasible.

_**Note:**_
`XSLP_NLPSTATUS_UNFINISHED` indicates that the solve was interrupted without finding a feasible solution.

_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_NONCONSTANTCOEFFS, SLPNONCONSTANTCOEFFS

_**Description:**_    Number of coefficients in the augmented problem that might change between SLP iterations
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_NONLINEARCONSTRAINTS, NONLINEARCONSTRAINTS

_**Description:**_    Number of nonlinear constraints in the problem
 
_**Type:**_ Integer

_**Topic area:**_ 
Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_ORIGINALCOLS, NLPORIGINALCOLS

_**Description:**_    Number of model columns in the extended original problem
 
_**Type:**_ Integer

_**Topic area:**_ 
Problem Information

_**Note:**_
This includes columns introduced by transformations and reformulations carried out during nonlinear presolve, but does not include augmentation columns. To access the number of original columns, use `XPRS_INPUTCOLS`.

_**See also:**_
`XSLP_ORIGINALROWS`, `XSLP_MODELROWS`, `XSLP_MODELCOLS`, `XPRS_INPUTROWS`, `XPRS_INPUTCOLS`.

_**Category:**_ Attribute

#### XSLP_ORIGINALROWS, NLPORIGINALROWS

_**Description:**_    Number of model rows in the extended original problem
 
_**Type:**_ Integer

_**Topic area:**_ 
Problem Information

_**Note:**_
This includes rows introduced by transformations and reformulations carried out during nonlinear presolve, but does not include augmentation rows. To access the number of original rows, use `XPRS_INPUTROWS`.

_**See also:**_
`XSLP_ORIGINALCOLS`, `XSLP_MODELROWS`, `XSLP_MODELCOLS`, `XPRS_INPUTROWS`, `XPRS_INPUTCOLS`.

_**Category:**_ Attribute

#### XSLP_PENALTYDELTACOLUMN, SLPPENALTYDELTACOLUMN

_**Description:**_    Index of column costing the penalty delta row
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Note:**_
This index always counts from 1. It is zero if there is no penalty delta row.

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PENALTYDELTAROW, SLPPENALTYDELTAROW

_**Description:**_    Index of equality row holding the penalties for delta vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Note:**_
This index always counts from 1. It is zero if there are no penalty delta vectors.

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PENALTYDELTAS, SLPPENALTYDELTAS

_**Description:**_    Number of penalty delta vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PENALTYERRORCOLUMN, SLPPENALTYERRORCOLUMN

_**Description:**_    Index of column costing the penalty error row
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Note:**_
This index always counts from 1. It is zero if there is no penalty error row.

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PENALTYERRORROW, SLPPENALTYERRORROW

_**Description:**_    Index of equality row holding the penalties for penalty error vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Note:**_
This index always counts from 1. It is zero if there are no penalty error vectors.

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PENALTYERRORS, SLPPENALTYERRORS

_**Description:**_    Number of penalty error vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PLUSPENALTYERRORS, SLPPLUSPENALTYERRORS

_**Description:**_    Number of positive penalty error vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_PRESOLVEELIMINATIONS, NLPPRESOLVEELIMINATIONS

_**Description:**_    Number of SLP variables eliminated by`XSLPpresolve`
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Set by routines:**_ `XSLPpresolve`
_**Category:**_ Attribute

#### XSLP_PRESOLVESTATE

_**Description:**_    Indicates if the problem is presolved
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| The problem is not presolved
 `1`| The problem is presolved, but no columns or rows have been removed from the problem
 `2`| The problem is fully presolved, and the column and row indices do not match the original problem

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`,`XSLPpresolve`
_**Category:**_ Attribute

#### XSLP_SBXCONVERGED, SLPSBXCONVERGED

_**Description:**_    Number of step-bounded variables converged only on extended criteria
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_SEMICONTDELTAS, SLPSEMICONTDELTAS

_**Description:**_    Number of variables with a minimum perturbation step set up in the problem
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Problem Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_SOLVERSELECTED, LOCALSOLVERSELECTED

_**Description:**_    Includes information of which Xpress solver has been used to solve the problem
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Unset
 `0`| Xpress-SLP
 `1`| Knitro \(Artelys\)
 `2`| Xpress Optimizer

_**Note:**_

The following constants are provided:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
0 | `XSLP_SOLVER_XSLP` | 
1 | `XSLP_SOLVER_KNITRO` | 
2 | `XSLP_SOLVER_OPTIMIZER` | 



_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_SOLSTATUS, NLPSOLSTATUS

_**Description:**_    Indicates the type of solution returned by the solver.
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| No solution available.
 `1`| A solution with no dual information.
 `2`| A locally optimal solution with dual information.
 `3`| A globally optimal solution without dual information.
 `4`| A globally optimal solution with dual information.

_**Note:**_

The following constants are provided:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
0 | `XSLP_SOLSTATUS_NONE` | 
1 | `XSLP_SOLSTATUS_SOLUTION_NODUALS` | 
2 | `XSLP_SOLSTATUS_LOCALLYOPTIMAL_WITHDUALS` | 
3 | `XSLP_SOLSTATUS_GLOBALLYOPTIMAL_NODUALS` | 
4 | `XSLP_SOLSTATUS_GLOBALLYOPTIMAL_WITHDUALS` | 



_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_STATUS, SLPSTATUS

_**Description:**_    Bitmap holding the problem convergence status
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Converged on objective function with no unconverged values in active constraints.
 `1`| Converged on objective function with some variables converged on extended criteria only.
 `2`| LP solution is infeasible.
 `3`| LP solution is unfinished \(not optimal or infeasible\).
 `4`| SLP terminated on maximum SLP iterations.
 `5`| SLP is integer infeasible.
 `6`| SLP converged with residual penalty errors.
 `7`| Converged on objective.
 `9`| SLP terminated on max time.
 `10`| SLP terminated by user.
 `11`| Some variables are linked to active constraints.
 `12`| No unconverged values in active constraints.
 `13`| OTOL is satisfied - range of objective change small, active step bounds.
 `14`| VTOL is satisfied - range of objective change is small.
 `15`| XTOL is satisfied - range of objective change small, no unconverged in active.
 `16`| WTOL is satisfied - convergence continuation.
 `17`| ERRORTOL satisfied - penalties not increased further.
 `18`| EVTOL satisfied - penalties not increased further.
 `19`| There were iterations where the solution had to be polished.
 `20`| There were iterations where the solution polishing failed.
 `21`| There were iterations where rows were enforced.
 `22`| Terminated due to XSLP\_INFEASLIMIT.

_**Note:**_
A value of zero after SLP optimization means that the solution is fully converged.
The following constants are provided for checking these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_STATUS_CONVERGEDOBJUCC` | 
Setting bit 1 | `XSLP_STATUS_CONVERGEDOBJSBX` | 
Setting bit 2 | `XSLP_STATUS_LPINFEASIBLE` | 
Setting bit 3 | `XSLP_STATUS_LPUNFINISHED` | 
Setting bit 4 | `XSLP_STATUS_MAXSLPITERATIONS` | 
Setting bit 5 | `XSLP_STATUS_INTEGERINFEASIBLE` | 
Setting bit 6 | `XSLP_STATUS_RESIDUALPENALTIES` | 
Setting bit 7 | `XSLP_STATUS_CONVERGEDOBJOBJ` | 
Setting bit 9 | `XSLP_STATUS_MAXTIME` | 
Setting bit 10 | `XSLP_STATUS_USER` | 
Setting bit 11 | `XSLP_STATUS_VARSLINKEDINACTIVE` | 
Setting bit 12 | `XSLP_STATUS_NOVARSINACTIVE` | 
Setting bit 13 | `XSLP_STATUS_OTOL` | 
Setting bit 14 | `XSLP_STATUS_VTOL` | 
Setting bit 15 | `XSLP_STATUS_XTOL` | 
Setting bit 16 | `XSLP_STATUS_WTOL` | 
Setting bit 17 | `XSLP_STATUS_ERROTOL` | 
Setting bit 18 | `XSLP_STATUS_EVTOL` | 
Setting bit 19 | `XSLP_STATUS_POLISHED` | 
Setting bit 20 | `XSLP_STATUS_POLISH_FAILURE` | 
Setting bit 21 | `XSLP_STATUS_ENFORCED` | 
Setting bit 22 | `XSLP_STATUS_CONSECUTIVE_INFEAS` | 



_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_STOPSTATUS, NLPSTOPSTATUS

_**Description:**_    Status of the optimization process.
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Note:**_
Possible values are:

__Value__ | __Description__ | 
---------- |  ---------- | 
XSLP\_STOP\_NONE | no interruption - the solve completed normally | 
XSLP\_STOP\_TIMELIMIT | time limit hit | 
XSLP\_STOP\_CTRLC | control C hit | 
XSLP\_STOP\_NODELIMIT | node limit hit | 
XSLP\_STOP\_ITERLIMIT | iteration limit hit | 
XSLP\_STOP\_MIPGAP | MIP gap is sufficiently small | 
XSLP\_STOP\_SOLLIMIT | solution limit hit | 
XSLP\_STOP\_USER | user interrupt. | 


_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_TOLSETS, SLPTOLSETS

_**Description:**_    _This parameter is deprecated and will be removed in a future release._
   Number of tolerance sets.
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP-convergence

_**Set by routines:**_ `XSLPaddtolsets`,`XSLPchgtolset`,`XSLPloadtolsets`,`XSLPreadprob`
_**Category:**_ Attribute

#### XSLP_TOTALEVALUATIONERRORS, NLPTOTALEVALUATIONERRORS

_**Description:**_    The total number of evaluation errors during the solve
 
_**Type:**_ Integer

_**Topic area:**_ 
Numerics

_**Set by routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`.
_**Category:**_ Attribute

#### XSLP_UCCONSTRAINEDCOUNT, SLPUCCONSTRAINEDCOUNT

_**Description:**_    Number of unconverged variables with coefficients in constraining rows
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_UFINSTANCES

_**Description:**_    Number of user function instances
 
_**Type:**_ Integer

_**Topic area:**_ 
User Functions

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_UFS, NLPUFS

_**Description:**_    Number of user functions
 
_**Type:**_ Integer

_**Topic area:**_ 
User Functions

_**Set by routines:**_ `XSLPadduserfunction`,`XSLPdeluserfunction`,`XSLPreadprob`
_**Category:**_ Attribute

#### XSLP_UNCONVERGED, SLPUNCONVERGED

_**Description:**_    Number of unconverged values
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Note:**_
Prior to the first iteration this will return -1.

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_USEDERIVATIVES, NLPUSEDERIVATIVES

_**Description:**_    Indicates whether numeric or analytic derivatives were used to create the linear approximations and solve the problem
 
_**Type:**_ Integer

_**Topic area:**_ 
Derivatives

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| numeric derivatives.
 `1`| analytic derivatives for all formulae unless otherwise specified.

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_USERFUNCCALLS, NLPUSERFUNCCALLS

_**Description:**_    Number of calls made to user functions
 
_**Type:**_ Integer

_**Topic area:**_ 
User Functions

_**Set by routines:**_ `XSLPcascade`,`XSLPconstruct`,`XSLPevaluatecoef`,`XSLPevaluateformula`,`XSLPmaxim`,`XSLPminim`
_**Category:**_ Attribute

#### XSLP_VALIDATIONSTATUS, NLPVALIDATIONSTATUS

_**Description:**_    Feasiblity status of the current solution.
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `1`| Feasible.
 `4`| Infeasible.

_**Note:**_

The following constants are provided:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
1 | `XSLP_NLPSTATUS_SOLUTION` | 
4 | `XSLP_NLPSTATUS_INFEASIBLE` | 



_**Set by routines:**_ `XSLPvalidate`.
_**Category:**_ Attribute

#### XSLP_VARIABLES, NLPVARIABLES

_**Description:**_    Number of SLP variables
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Data Information

_**Set by routines:**_ `XSLPconstruct`
_**Category:**_ Attribute

#### XSLP_ZEROESRESET, SLPZEROESRESET

_**Description:**_    Number of placeholder entries set to zero
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Note:**_

For an explanation of deletion of placeholder entries in the matrix see  _Management of zero placeholder entries_.


_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ZEROCRITERIONCOUNT`, `XSLP_ZEROCRITERIONSTART`, `XSLP_ZEROESRETAINED`, `XSLP_ZEROESTOTAL`,  _Management of zero placeholder entries_

_**Category:**_ Attribute

#### XSLP_ZEROESRETAINED, SLPZEROESRETAINED

_**Description:**_    Number of potentially zero placeholders left untouched
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Note:**_

For an explanation of deletion of placeholder entries in the matrix see  _Management of zero placeholder entries_.


_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ZEROCRITERIONCOUNT`, `XSLP_ZEROCRITERIONSTART`, `XSLP_ZEROESRESET`, `XSLP_ZEROESTOTAL`,  _Management of zero placeholder entries_

_**Category:**_ Attribute

#### XSLP_ZEROESTOTAL, SLPZEROESTOTAL

_**Description:**_    Number of potential zero placeholder entries
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Note:**_

For an explanation of deletion of placeholder entries in the matrix see  _Management of zero placeholder entries_.


_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ZEROCRITERIONCOUNT`, `XSLP_ZEROCRITERIONSTART`, `XSLP_ZEROESRESET`, `XSLP_ZEROESRETAINED`,  _Management of zero placeholder entries_

_**Category:**_ Attribute

#### Section 19.3 Reference \(pointer\) problem attributes


The reference attributes are void pointers whose size \(32 or 64 bit\) depends on the platform.

#### XSLP_MIPPROBLEM

_**Description:**_    The underlying Optimizer MIP problem. `XSLP_MIPPROBLEM`is a reference of type XPRSprob, and should be used in MISLP callbacks to access MIP-specific Optimizer values \(such as node and parent numbers\).
 
_**Type:**_ Reference

_**Topic area:**_ 
MISLP

_**Set by routines:**_ `XSLPnlpoptimize`
_**Category:**_ Attribute

#### XSLP_XPRSPROBLEM

_**Description:**_    The underlying Optimizer problem
 
_**Type:**_ Reference

_**Topic area:**_ 
Misc

_**Set by routines:**_ `XSLPcreateprob`
_**Category:**_ Attribute

#### XSLP_XSLPPROBLEM

_**Description:**_    The Xpress NonLinear problem
 
_**Type:**_ Reference

_**Topic area:**_ 
Misc

_**Set by routines:**_ `XSLPcreateprob`
_**Category:**_ Attribute

#### Section 19.4 String problem attributes


#### XSLP_VERSIONDATE

_**Description:**_    Date of creation of Xpress NonLinear
 
_**Type:**_ String

_**Topic area:**_ 
Misc

_**Note:**_
The format of the date is dd mmm yyyy.

_**Set by routines:**_ `XSLPinit`
_**Category:**_ Attribute

### Chapter 20 Control Parameters


Various controls exist within Xpress NonLinear to govern the solution procedure and the form of the output. Some of these take integer values and act as switches between various types of behavior. Many are tolerances on values related to the convergence criteria; these are all double precision. There are also a few controls which are character strings, setting names for structures. Any of these may be altered by the user to enhance performance of the SLP algorithm. In most cases, the default values provided have been found to work well in practice over a range of problems and caution should be exercised if they are changed.

Users of the Xpress NonLinear function library are provided with the following set of functions for setting and obtaining control values:


| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
`XSLPgetintcontrol` | `XSLPgetdblcontrol` | `XSLPgetstrcontrol` | 
`XSLPsetintcontrol` | `XSLPsetdblcontrol` | `XSLPsetstrcontrol` | 

All the controls as listed in this chapter are prefixed with `XSLP_`. Most of them also exist within the Optimizer library with an NLP or SLP prefix, e.g., `XPRS_NLPPRESOLVE`. It is possible to use the above functions with other control parameters for the Xpress Optimizer \(controls prefixed with `XPRS_`\). For details of the Optimizer controls, see the Optimizer manual.

Example of the usage of the functions:

```
XSLPgetintcontrol(Prob, XSLP_PRESOLVE, &presolve);
printf("The value of PRESOLVE was %d\n", presolve);
XSLPsetintcontrol(Prob, XSLP_PRESOLVE, 1-presolve);
printf("The value of PRESOLVE is now %d\n", 1-presolve);

```


The following is a list of all the Xpress NonLinear controls:



_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XSLP_ALGORITHM`, `SLPALGORITHM` | Bit map describing the SLP algorithm\(s\) to be used | Bit-vector, SLP
`XSLP_ANALYZE`, `SLPANALYZE` | Bit map activating additional options supporting model / solution path analysis | Bit-vector, Logging, SLP
`XSLP_ATOL_A`, `SLPATOL_A` | Absolute delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ATOL_R`, `SLPATOL_R` | Relative delta convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_AUGMENTATION`, `SLPAUGMENTATION` | Bit map describing the SLP augmentation method\(s\) to be used | Bit-vector, SLP
`XSLP_AUTOSAVE`, `SLPAUTOSAVE` | Frequency with which to save the model | Logging, SLP
`XSLP_BARCROSSOVERSTART`, `SLPBARCROSSOVERSTART` | Default crossover activation behaviour for barrier start | Linearizations, SLP
`XSLP_BARLIMIT`, `SLPBARLIMIT` | Number of initial SLP iterations using the barrier method | Limits, Linearizations, SLP
`XSLP_BARSTALLINGLIMIT`, `SLPBARSTALLINGLIMIT` | Number of iterations to allow numerical failures in barrier before switching to dual | Limits, Linearizations, SLP
`XSLP_BARSTALLINGOBJLIMIT`, `SLPBARSTALLINGOBJLIMIT` | Number of iterations over which to measure the objective change for barrier iterations with no crossover | Limits, Linearizations, SLP
`XSLP_BARSTALLINGTOL`, `SLPBARSTALLINGTOL` | Required change in the objective when progress is measured in barrier iterations without crossover | Linearizations, SLP
`XSLP_BARSTARTOPS`, `SLPBARSTARTOPS` | Controls behaviour when the barrier is used to solve the linearizations | Linearizations, SLP
`XSLP_BOUNDTHRESHOLD`, `SLPBOUNDTHRESHOLD` | The maximum size of a bound that can be introduced by nonlinear presolve. | Presolve, SLP
`XSLP_CALCTHREADS`, `NLPCALCTHREADS` | Number of threads used for formula and derivatives evaluations | Parallel
`XSLP_CASCADE`, `SLPCASCADE` | Bit map describing the cascading to be used | Cascading, SLP
`XSLP_CASCADENLIMIT`, `SLPCASCADENLIMIT` | Maximum number of iterations for cascading with non-linear determining rows | Cascading, Limits, SLP
`XSLP_CASCADETOL_PA`, `SLPCASCADETOL_PA` | Absolute cascading print tolerance | Cascading, Logging, SLP
`XSLP_CASCADETOL_PR`, `SLPCASCADETOL_PR` | Relative cascading print tolerance | Cascading, Logging, SLP
`XSLP_CDTOL_A`, `SLPCDTOL_A` | Absolute tolerance for deducing constant derivatives | Tolerances
`XSLP_CDTOL_R`, `SLPCDTOL_R` | Relative tolerance for deducing constant derivatives | Tolerances
`XSLP_CLAMPSHRINK`, `SLPCLAMPSHRINK` | Shrink ratio used to impose strict convergence on variables converged in extended criteria only | SLP
`XSLP_CLAMPVALIDATIONTOL_A`, `SLPCLAMPVALIDATIONTOL_A` | Absolute validation tolerance for applying `XSLP_CLAMPSHRINK` | SLP, Tolerances
`XSLP_CLAMPVALIDATIONTOL_R`, `SLPCLAMPVALIDATIONTOL_R` | Relative validation tolerance for applying `XSLP_CLAMPSHRINK` | SLP, Tolerances
`XSLP_CONTROL` | Bit map describing which Xpress NonLinear functions also activate the corresponding Optimizer Library function | Bit-vector, Misc
`XSLP_CONVERGENCEOPS`, `SLPCONVERGENCEOPS` | Bit map describing which convergence tests should be carried out | Bit-vector, SLP, SLP-convergence
`XSLP_CTOL`, `SLPCTOL` | Closure convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_CUTSTRATEGY`, `SLPCUTSTRATEGY` | Determines whihc cuts to apply in the MISLP search when the default SLP-in-MIP strategy is used. | Cuts, MISLP
`XSLP_DAMP`, `SLPDAMP` | Damping factor for updating values of variables | SLP
`XSLP_DAMPEXPAND`, `SLPDAMPEXPAND` | Multiplier to increase damping factor during dynamic damping | SLP
`XSLP_DAMPMAX`, `SLPDAMPMAX` | Maximum value for the damping factor of a variable during dynamic damping | SLP
`XSLP_DAMPMIN`, `SLPDAMPMIN` | Minimum value for the damping factor of a variable during dynamic damping | SLP
`XSLP_DAMPSHRINK`, `SLPDAMPSHRINK` | Multiplier to decrease damping factor during dynamic damping | SLP
`XSLP_DAMPSTART`, `SLPDAMPSTART` | SLP iteration at which damping is activated | SLP
`XSLP_DEFAULTIV`, `NLPDEFAULTIV` | Default initial value for an SLP variable if none is explicitly given | Data Input
`XSLP_DEFAULTSTEPBOUND`, `SLPDEFAULTSTEPBOUND` | Minimum initial value for the step bound of an SLP variable if none is explicitly given | SLP
`XSLP_DELAYUPDATEROWS`, `SLPDELAYUPDATEROWS` | Number of SLP iterations before update rows are fully activated | SLP
`XSLP_DELTA_A`, `SLPDELTA_A` | Absolute perturbation of values for calculating numerical derivatives | Derivatives
`XSLP_DELTA_INFINITY`, `SLPDELTA_INFINITY` | Maximum value for partial derivatives | Derivatives
`XSLP_DELTA_R`, `SLPDELTA_R` | Relative perturbation of values for calculating numerical derivatives | Derivatives
`XSLP_DELTA_X`, `SLPDELTA_X` | Minimum absolute value of delta coefficients to be retained | Derivatives
`XSLP_DELTA_Z`, `SLPDELTA_Z` | Tolerance used when calculating derivatives | Derivatives, Tolerances
`XSLP_DELTA_ZERO`, `SLPDELTA_ZERO` | Absolute zero acceptance tolerance used when calculating derivatives | Derivatives, Tolerances
`XSLP_DELTACOST`, `SLPDELTACOST` | Initial penalty cost multiplier for penalty delta vectors | SLP
`XSLP_DELTACOSTFACTOR`, `SLPDELTACOSTFACTOR` | Factor for increasing cost multiplier on total penalty delta vectors | SLP
`XSLP_DELTAFORMAT`, `SLPDELTAFORMAT` | Formatting string for creation of names for SLP delta vectors | Logging, SLP
`XSLP_DELTAMAXCOST`, `SLPDELTAMAXCOST` | Maximum penalty cost multiplier for penalty delta vectors | SLP
`XSLP_DELTAOFFSET`, `SLPDELTAOFFSET` | Position of first character of SLP variable name used to create name of delta vector | Logging, SLP
`XSLP_DELTAZLIMIT`, `SLPDELTAZLIMIT` | Number of SLP iterations during which to apply XSLP\_DELTA\_Z | SLP
`XSLP_DERIVATIVES`, `NLPDERIVATIVES` | Bitmap describing the method of calculating derivatives | Derivatives
`XSLP_DETERMINISTIC`, `NLPDETERMINISTIC` | Determines if the parallel features of SLP should be guaranteed to be deterministic | MISLP, Parallel, SLP
`XSLP_DJTOL`, `SLPDJTOL` | Tolerance on DJ value for determining if a variable is at its step bound | SLP, Tolerances
`XSLP_DRCOLDJTOL`, `SLPDRCOLDJTOL` | Reduced cost tolerance on the delta variable when fixing due to the determining column being below `XSLP_DRCOLTOL`. | Cascading, SLP, Tolerances
`XSLP_DRCOLTOL`, `SLPDRCOLTOL` | The minimum absolute magnitude of a determining column, for which the determined variable is still regarded as well defined | Cascading, SLP, Tolerances
`XSLP_DRFIXRANGE`, `SLPDRFIXRANGE` | The range around the previous value where variables are fixed in cascading if the determining column is below `XSLP_DRCOLTOL`. | Cascading, SLP
`XSLP_ECFCHECK`, `SLPECFCHECK` | Check feasibility at the point of linearization for extended convergence criteria | SLP, SLP-convergence
`XSLP_ECFTOL_A`, `SLPECFTOL_A` | Absolute tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ECFTOL_R`, `SLPECFTOL_R` | Relative tolerance on testing feasibility at the point of linearization | SLP, SLP-convergence, Tolerances
`XSLP_ECHOXPRSMESSAGES` | Controls if the XSLP message callback should relay messages from the XPRS library. | Logging
`XSLP_ENFORCECOSTSHRINK`, `SLPENFORCECOSTSHRINK` | Factor by which to decrease the current penalty multiplier when enforcing rows. | SLP
`XSLP_ENFORCEMAXCOST`, `SLPENFORCEMAXCOST` | Maximum penalty cost in the objective before enforcing most violating rows | SLP
`XSLP_ERRORCOST`, `SLPERRORCOST` | Initial penalty cost multiplier for penalty error vectors | SLP
`XSLP_ERRORCOSTFACTOR`, `SLPERRORCOSTFACTOR` | Factor for increasing cost multiplier on total penalty error vectors | SLP
`XSLP_ERRORMAXCOST`, `SLPERRORMAXCOST` | Maximum penalty cost multiplier for penalty error vectors | SLP
`XSLP_ERROROFFSET`, `SLPERROROFFSET` | Position of first character of constraint name used to create name of penalty error vectors | Logging, SLP
`XSLP_ERRORTOL_A`, `SLPERRORTOL_A` | Absolute tolerance for error vectors | SLP, Tolerances
`XSLP_ERRORTOL_P`, `SLPERRORTOL_P` | Absolute tolerance for printing error vectors | SLP, Tolerances
`XSLP_ESCALATION`, `SLPESCALATION` | Factor for increasing cost multiplier on individual penalty error vectors | SLP
`XSLP_ETOL_A`, `SLPETOL_A` | Absolute tolerance on penalty vectors | SLP, Tolerances
`XSLP_ETOL_R`, `SLPETOL_R` | Relative tolerance on penalty vectors | SLP, Tolerances
`XSLP_EVALUATE`, `NLPEVALUATE` | Evaluation strategy for user functions | User Functions
`XSLP_EVTOL_A`, `SLPEVTOL_A` | Absolute tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_EVTOL_R`, `SLPEVTOL_R` | Relative tolerance on total penalty costs | SLP, SLP-convergence, Tolerances
`XSLP_EXPAND`, `SLPEXPAND` | Multiplier to increase a step bound | SLP
`XSLP_FEASTOLTARGET`, `SLPFEASTOLTARGET` | When set, this defines a target feasibility tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_FILTER`, `SLPFILTER` | Bit map for controlling solution updates | Bit-vector, SLP, Solution
`XSLP_FINDIV`, `NLPFINDIV` | Option for running a heuristic to find a feasible initial point | Heuristics
`XSLP_FUNCEVAL`, `NLPFUNCEVAL` | Bit map for determining the method of evaluating user functions and their derivatives | Derivatives, User Functions
`XSLP_GRANULARITY`, `SLPGRANULARITY` | Base for calculating penalty costs | SLP
`XSLP_GRIDHEURSELECT`, `SLPGRIDHEURSELECT` | Bit map selectin which heuristics to run if the problem has variable with an integer delta | Heuristics, SLP
`XSLP_HESSIAN`, `NLPHESSIAN` | Second order differentiation mode when using analytical derivatives | Derivatives
`XSLP_HEURSTRATEGY`, `SLPHEURSTRATEGY` | Branch and Bound: This specifies the MINLP heuristic strategy. | Heuristics, SLP
`XSLP_INFEASLIMIT`, `SLPINFEASLIMIT` | The maximum number of consecutive infeasible SLP iterations which can occur before Xpress-SLP terminates | Limits, SLP
`XSLP_INFINITY`, `NLPINFINITY` | Value returned by a divide-by-zero in a formula | Numerics
`XSLP_ITERFALLBACKOPS`, `SLPITERFALLBACKOPS` | Alternative LP level control values for numerically challenging problems | Linearizations, Numerics, SLP
`XSLP_ITERLIMIT`, `SLPITERLIMIT` | The maximum number of SLP iterations | Limits, SLP
`XSLP_ITOL_A`, `SLPITOL_A` | Absolute impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ITOL_R`, `SLPITOL_R` | Relative impact convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_IVNAME`, `NLPIVNAME` | Name of the set of initial values to be used | File IO
`XSLP_JACOBIAN`, `NLPJACOBIAN` | First order differentiation mode when using analytical derivatives | Derivatives
`XSLP_KEEPEQUALSCOLUMN`, `NLPKEEPEQUALSCOLUMN` | When set to a nonzero value, the MPS reader will keep the equals column in the problem | Misc
`XSLP_LINQUADBR`, `NLPLINQUADBR` | Use linear and quadratic constraints and objective function to further reduce bounds on all variables | Presolve
`XSLP_LOG`, `NLPLOG` | Level of printing during SLP iterations | Logging, SLP
`XSLP_LSITERLIMIT`, `SLPLSITERLIMIT` | Number of iterations in the line search | Limits, SLP
`XSLP_LSPATTERNLIMIT`, `SLPLSPATTERNLIMIT` | Number of iterations in the pattern search preceding the line search | Limits, SLP
`XSLP_LSSTART`, `SLPLSSTART` | Iteration in which to active the line search | SLP
`XSLP_LSZEROLIMIT`, `SLPLSZEROLIMIT` | Maximum number of zero length line search steps before line search is deactivated | Limits, SLP
`XSLP_MATRIXTOL`, `SLPMATRIXTOL` | Nonzero tolerance for dropping coefficients from the linearization. | SLP
`XSLP_MAXTIME`, `NLPMAXTIME` | The maximum time in seconds that the SLP optimization will run before it terminates | Limits
`XSLP_MAXWEIGHT`, `SLPMAXWEIGHT` | Maximum penalty weight for delta or error vectors | SLP
`XSLP_MEMORYFACTOR` | Factor for expanding size of dynamic arrays in memory | Memory
`XSLP_MERITLAMBDA`, `NLPMERITLAMBDA` | Factor by which the net objective is taken into account in the merit function | SLP, Solution
`XSLP_MINSBFACTOR`, `SLPMINSBFACTOR` | Factor by which step bounds can be decreased beneath `XSLP_ATOL_A` | SLP
`XSLP_MINUSDELTAFORMAT`, `SLPMINUSDELTAFORMAT` | Formatting string for creation of names for SLP negative penalty delta vectors | Logging, SLP
`XSLP_MINUSERRORFORMAT`, `SLPMINUSERRORFORMAT` | Formatting string for creation of names for SLP negative penalty error vectors | Logging, SLP
`XSLP_MINWEIGHT`, `SLPMINWEIGHT` | Minimum penalty weight for delta or error vectors | SLP
`XSLP_MIPALGORITHM`, `SLPMIPALGORITHM` | Bitmap describing the MISLP algorithms to be used | Bit-vector, MISLP
`XSLP_MIPCUTOFF_A`, `SLPMIPCUTOFF_A` | Absolute objective function cutoff for MIP termination | MISLP, Tolerances
`XSLP_MIPCUTOFF_R`, `SLPMIPCUTOFF_R` | Absolute objective function cutoff for MIP termination | MISLP, Tolerances
`XSLP_MIPCUTOFFCOUNT`, `SLPMIPCUTOFFCOUNT` | Number of SLP iterations to check when considering a node for cutting off | Limits, MISLP
`XSLP_MIPCUTOFFLIMIT`, `SLPMIPCUTOFFLIMIT` | Number of SLP iterations to check when considering a node for cutting off | Limits, MISLP
`XSLP_MIPDEFAULTALGORITHM`, `SLPMIPDEFAULTALGORITHM` | Default algorithm to be used during the tree search in MISLP | Linearizations, MISLP
`XSLP_MIPERRORTOL_A`, `SLPMIPERRORTOL_A` | Absolute penalty error cost tolerance for MIP cut-off | MISLP, Tolerances
`XSLP_MIPERRORTOL_R`, `SLPMIPERRORTOL_R` | Relative penalty error cost tolerance for MIP cut-off | MISLP, Tolerances
`XSLP_MIPFIXSTEPBOUNDS`, `SLPMIPFIXSTEPBOUNDS` | Bitmap describing the step-bound fixing strategy during MISLP | MISLP
`XSLP_MIPITERLIMIT`, `SLPMIPITERLIMIT` | Maximum number of SLP iterations at each node | Limits, MISLP
`XSLP_MIPLOG`, `SLPMIPLOG` | Frequency with which MIP status is printed | Logging, MISLP
`XSLP_MIPOCOUNT`, `SLPMIPOCOUNT` | Number of SLP iterations at each node over which to measure objective function variation | MISLP, SLP-convergence
`XSLP_MIPOTOL_A`, `SLPMIPOTOL_A` | Absolute objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MIPOTOL_R`, `SLPMIPOTOL_R` | Relative objective function tolerance for MIP termination | MISLP, SLP-convergence, Tolerances
`XSLP_MIPRELAXSTEPBOUNDS`, `SLPMIPRELAXSTEPBOUNDS` | Bitmap describing the step-bound relaxation strategy during MISLP | MISLP
`XSLP_MSMAXBOUNDRANGE`, `MSMAXBOUNDRANGE` | Defines the maximum range inside which initial points are generated by multistart presets | Multistart
`XSLP_MTOL_A`, `SLPMTOL_A` | Absolute effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MTOL_R`, `SLPMTOL_R` | Relative effective matrix element convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_MULTISTART`, `MULTISTART` | The multistart main control. | Multistart
`XSLP_MULTISTART_LOG`, `MULTISTART_LOG` | The level of logging during the multistart run. | Logging, Multistart
`XSLP_MULTISTART_MAXSOLVES`, `MULTISTART_MAXSOLVES` | The maximum number of jobs to create during the multistart search. | Limits, Multistart
`XSLP_MULTISTART_MAXTIME`, `MULTISTART_MAXTIME` | The maximum total time to be spent in the mutlistart search. | Limits, Multistart
`XSLP_MULTISTART_POOLSIZE`, `MULTISTART_POOLSIZE` | The maximum number of problem objects allowed to pool up before synchronization in the deterministic multistart. | Limits, Multistart
`XSLP_MULTISTART_SEED`, `MULTISTART_SEED` | Random seed used for the automatic generation of initial point when loading multistart presets | Multistart
`XSLP_MULTISTART_THREADS`, `MULTISTART_THREADS` | The maximum number of threads to be used in multistart | Multistart, Parallel
`XSLP_MVTOL`, `SLPMVTOL` | Marginal value tolerance for determining if a constraint is slack | SLP, SLP-convergence, Tolerances
`XSLP_NLPSOLVER`, `NLPSOLVER` | Controls whether to call FICO Xpress Global or one of the local solvers | Solution Process
`XSLP_OBJTHRESHOLD`, `SLPOBJTHRESHOLD` | Assumed maximum value of the objective function in absolute value. | SLP
`XSLP_OBJTOPENALTYCOST`, `SLPOBJTOPENALTYCOST` | Factor to estimate initial penalty costs from objective function | SLP
`XSLP_OCOUNT`, `SLPOCOUNT` | Number of SLP iterations over which to measure objective function variation for static objective \(2\) convergence criterion | SLP, SLP-convergence
`XSLP_OPTIMALITYTOLTARGET`, `SLPOPTIMALITYTOLTARGET` | When set, this defines a target optimality tolerance to which the linearizations are solved to | Linearizations, SLP, Tolerances
`XSLP_OTOL_A`, `SLPOTOL_A` | Absolute static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_OTOL_R`, `SLPOTOL_R` | Relative static objective \(2\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_PENALTYCOLFORMAT`, `SLPPENALTYCOLFORMAT` | Formatting string for creation of the names of the SLP penalty transfer vectors | Logging, SLP
`XSLP_PENALTYINFOSTART`, `SLPPENALTYINFOSTART` | Iteration from which to record row penalty information | Logging, SLP
`XSLP_PENALTYROWFORMAT`, `SLPPENALTYROWFORMAT` | Formatting string for creation of the names of the SLP penalty rows | Logging, SLP
`XSLP_PLUSDELTAFORMAT`, `SLPPLUSDELTAFORMAT` | Formatting string for creation of names for SLP positive penalty delta vectors | Logging, SLP
`XSLP_PLUSERRORFORMAT`, `SLPPLUSERRORFORMAT` | Formatting string for creation of names for SLP positive penalty error vectors | Logging, SLP
`XSLP_POSTSOLVE`, `NLPPOSTSOLVE` | This control determines whether postsolving should be performed automatically | Presolve
`XSLP_PRESOLVE`, `NLPPRESOLVE` | This control determines whether presolving should be performed on the nonlinear problem prior to starting the main algorithm | Presolve
`XSLP_PRESOLVE_ELIMTOL`, `NLPPRESOLVE_ELIMTOL` | Tolerance for nonlinear eliminations during SLP presolve | Presolve, Tolerances
`XSLP_PRESOLVELEVEL`, `NLPPRESOLVELEVEL` | This control determines the level of changes presolve may carry out on the problem and whether column/row indices may change | Presolve
`XSLP_PRESOLVEOPS`, `NLPPRESOLVEOPS` | Bitmap indicating the SLP presolve actions to be taken | Bit-vector, Presolve
`XSLP_PRESOLVEZERO`, `NLPPRESOLVEZERO` | Minimum absolute value for a variable which is identified as nonzero during SLP presolve | Presolve, Tolerances
`XSLP_PRIMALINTEGRALALPHA`, `NLPPRIMALINTEGRALALPHA` | Decay term for primal integral computation | Logging
`XSLP_PRIMALINTEGRALREF`, `NLPPRIMALINTEGRALREF` | Reference solution value to take into account when calculating the primal integral | Logging
`XSLP_PROBING`, `NLPPROBING` | This control determines whether probing on a subset of variables should be performed prior to starting the main algorithm. | Presolve
`XSLP_REFORMULATE`, `NLPREFORMULATE` | Controls the problem reformulations carried out before augmentation. | Presolve
`XSLP_SAMECOUNT`, `SLPSAMECOUNT` | Number of steps reaching the step bound in the same direction before step bounds are increased | SLP
`XSLP_SAMEDAMP`, `SLPSAMEDAMP` | Number of steps in same direction before damping factor is increased | SLP
`XSLP_SBLOROWFORMAT`, `SLPSBLOROWFORMAT` | Formatting string for creation of names for SLP lower step bound rows | Logging, SLP
`XSLP_SBNAME`, `SLPSBNAME` | Name of the set of initial step bounds to be used | Logging, SLP
`XSLP_SBROWOFFSET`, `SLPSBROWOFFSET` | Position of first character of SLP variable name used to create name of SLP lower and upper step bound rows | Logging, SLP
`XSLP_SBSTART`, `SLPSBSTART` | SLP iteration after which step bounds are first applied | SLP
`XSLP_SBUPROWFORMAT`, `SLPSBUPROWFORMAT` | Formatting string for creation of names for SLP upper step bound rows | Logging, SLP
`XSLP_SCALE`, `SLPSCALE` | When to re-scale the SLP problem | Numerics, SLP
`XSLP_SCALECOUNT`, `SLPSCALECOUNT` | Iteration limit used in determining when to re-scale the SLP matrix | Numerics, SLP
`XSLP_SHRINK`, `SLPSHRINK` | Multiplier to reduce a step bound | SLP
`XSLP_SHRINKBIAS`, `SLPSHRINKBIAS` | Defines an overwrite / adjustment of step bounds for improving iterations | SLP
`XSLP_SLPLOG`, `SLPLOG` | Frequency with which SLP status is printed | Logging, SLP
`XSLP_SOLVER`, `LOCALSOLVER` | Selects the library to use for local solves | Solution Process
`XSLP_STOL_A`, `SLPSTOL_A` | Absolute slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOL_R`, `SLPSTOL_R` | Relative slack convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_STOPOUTOFRANGE`, `NLPSTOPOUTOFRANGE` | Stop optimization and return error code if internal function argument is out of range | SLP
`XSLP_THREADS`, `NLPTHREADS` | Default number of threads to be used | Parallel
`XSLP_THREADSAFEUSERFUNC`, `NLPTHREADSAFEUSERFUNC` | Defines if user functions are allowed to be called in parallel | Parallel, User Functions
`XSLP_TOLNAME`, `SLPTOLNAME` | Name of the set of tolerance sets to be used | File IO, SLP
`XSLP_TRACEMASK`, `SLPTRACEMASK` | Mask of variable or row names that are to be traced through the SLP iterates | Logging, SLP
`XSLP_TRACEMASKOPS`, `SLPTRACEMASKOPS` | Controls the information printed for `XSLP_TRACEMASK`. | Bit-vector, Logging, SLP
`XSLP_UNFINISHEDLIMIT`, `SLPUNFINISHEDLIMIT` | The number of consecutive SLP iterations that may have an unfinished status before the solve is terminated. | Linearizations, SLP
`XSLP_UPDATEFORMAT`, `SLPUPDATEFORMAT` | Formatting string for creation of names for SLP update rows | Logging, SLP
`XSLP_UPDATEOFFSET`, `SLPUPDATEOFFSET` | Position of first character of SLP variable name used to create name of SLP update row | Logging, SLP
`XSLP_VALIDATIONFACTOR`, `NLPVALIDATIONFACTOR` | Minimum improvement in validation targets to continue iterating | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_K`, `NLPVALIDATIONTARGET_K` | Optimality target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTARGET_R`, `NLPVALIDATIONTARGET_R` | Feasiblity target tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VALIDATIONTOL_A`, `NLPVALIDATIONTOL_A` | Absolute tolerance for the XSLPvalidate procedure | SLP, Tolerances
`XSLP_VALIDATIONTOL_K`, `NLPVALIDATIONTOL_K` | Relative tolerance for the XSLPvalidatekkt procedure | SLP, Tolerances
`XSLP_VALIDATIONTOL_R`, `NLPVALIDATIONTOL_R` | Relative tolerance for the XSLPvalidate procedure | Tolerances
`XSLP_VCOUNT`, `SLPVCOUNT` | Number of SLP iterations over which to measure static objective \(3\) convergence | SLP, SLP-convergence
`XSLP_VLIMIT`, `SLPVLIMIT` | Number of SLP iterations after which static objective \(3\) convergence testing starts | SLP, SLP-convergence
`XSLP_VTOL_A`, `SLPVTOL_A` | Absolute static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_VTOL_R`, `SLPVTOL_R` | Relative static objective \(3\) convergence tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WCOUNT`, `SLPWCOUNT` | Number of SLP iterations over which to measure the objective for the extended convergence continuation criterion | SLP, SLP-convergence
`XSLP_WTOL_A`, `SLPWTOL_A` | Absolute extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_WTOL_R`, `SLPWTOL_R` | Relative extended convergence continuation tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XCOUNT`, `SLPXCOUNT` | Number of SLP iterations over which to measure static objective \(1\) convergence | SLP, SLP-convergence
`XSLP_XLIMIT`, `SLPXLIMIT` | Number of SLP iterations up to which static objective \(1\) convergence testing is performed | Limits, SLP, SLP-convergence
`XSLP_XTOL_A`, `SLPXTOL_A` | Absolute static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_XTOL_R`, `SLPXTOL_R` | Relative static objective function \(1\) tolerance | SLP, SLP-convergence, Tolerances
`XSLP_ZERO`, `NLPZERO` | Absolute tolerance | Tolerances
`XSLP_ZEROCRITERION`, `SLPZEROCRITERION` | Bitmap determining the behavior of the placeholder deletion procedure | Bit-vector, SLP
`XSLP_ZEROCRITERIONCOUNT`, `SLPZEROCRITERIONCOUNT` | Number of consecutive times a placeholder entry is zero before being considered for deletion | Limits, SLP
`XSLP_ZEROCRITERIONSTART`, `SLPZEROCRITERIONSTART` | SLP iteration at which criteria for deletion of placeholder entries are first activated. | SLP

#### Section 20.1 Double control parameters


#### XSLP_ATOL_A, SLPATOL_A

_**Description:**_    Absolute delta convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The absolute delta convergence criterion assesses the change in value of a variable \( _δX_ \) against the absolute delta convergence tolerance. If
 _δX<XSLP\_ATOL\_A_ 
then the variable has converged on the absolute delta convergence criterion.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**See also:**_
Convergence Criteria, `XSLP_ATOL_R`

_**Category:**_ Control

#### XSLP_ATOL_R, SLPATOL_R

_**Description:**_    Relative delta convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The relative delta convergence criterion assesses the change in value of a variable \( _δX_ \) relative to the value of the variable \( _X_ \), against the relative delta convergence tolerance. If
 _δX<X \* XSLP\_ATOL\_R_ 
then the variable has converged on the relative delta convergence criterion.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**See also:**_
Convergence Criteria, `XSLP_ATOL_A`

_**Category:**_ Control

#### XSLP_BARSTALLINGTOL, SLPBARSTALLINGTOL

_**Description:**_    Required change in the objective when progress is measured in barrier iterations without crossover
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Linearizations

_**Default value:**_ 0.05

_**Note:**_
Minumum objective variability change required in relation to control `XSLP_BARSTALLINGOBJLIMIT` for the iterations to be regarded as making progress. The net objective, error cost and error sum are taken into account.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_BARCROSSOVERSTART`, `XSLP_BARLIMIT`, `XSLP_BARSTARTOPS`, `XSLP_BARSTALLINGLIMIT`, `XSLP_BARSTALLINGOBJLIMIT`

_**Category:**_ Control

#### XSLP_BOUNDTHRESHOLD, SLPBOUNDTHRESHOLD

_**Description:**_    The maximum size of a bound that can be introduced by nonlinear presolve.
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Presolve

_**Default value:**_ 1.0e+10

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_CASCADETOL_PA, SLPCASCADETOL_PA

_**Description:**_    Absolute cascading print tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Cascading, Logging

_**Default value:**_ 0.01

_**Note:**_
The change to the value of a variable as a result of cascading is only printed if the change is deemed significant. The change is tested against: absolute and relative convergence tolerance and absolute and relative cascading print tolerance. The change is printed only if all tests fail. The absolute cascading print criterion measures the change in value of a variable \( _δX_ \) against the absolute cascading print tolerance. If
 _δX<XSLP\_CASCADETOL\_PA_ 
then the change is within the absolute cascading print tolerance and will not be printed. XSLP\_LOG must be at least 5 for this control to have an effect.

_**Affects routines:**_ `XSLPcascade`

_**See also:**_
Cascading, `XSLP_CASCADETOL_PR`

_**Category:**_ Control

#### XSLP_CASCADETOL_PR, SLPCASCADETOL_PR

_**Description:**_    Relative cascading print tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Cascading, Logging

_**Default value:**_ 0.01

_**Note:**_
The change to the value of a variable as a result of cascading is only printed if the change is deemed significant. The change is tested against: absolute and relative convergence tolerance and absolute and relative cascading print tolerance. The change is printed only if all tests fail. The relative cascading print criterion measures the change in value of a variable \( _δX_ \) relative to the value of the variable \( _X_ \), against the relative cascading print tolerance. If
 _δX<X \* XSLP\_CASCADETOL\_PR_ 
then the change is within the relative cascading print tolerance and will not be printed. XSLP\_LOG must be at least 5 for this control to have an effect.

_**Affects routines:**_ `XSLPcascade`

_**See also:**_
Cascading, `XSLP_CASCADETOL_PA`

_**Category:**_ Control

#### XSLP_CDTOL_A, SLPCDTOL_A

_**Description:**_    Absolute tolerance for deducing constant derivatives
 
_**Type:**_ Double

_**Topic area:**_ 
Tolerances

_**Default value:**_ 1.0e-08

_**Note:**_

The absolute tolerance test for constant derivatives is used as follows:
If the value of the user function at point _X<sub>0</sub>_ is _Y<sub>0</sub>_ and the values at _\(X<sub>0</sub>-δX\)_ and _\(X<sub>0</sub>+δX\)_ are _Y<sub>d</sub>_ and _Y<sub>u</sub>_ respectively, then the numerical derivatives at _X<sub>0</sub>_ are:
"down" derivative _D<sub>d</sub>= \(Y<sub>0</sub>- Y<sub>d</sub>\) /δX_ 
"up" derivative _D<sub>u</sub>= \(Y<sub>u</sub>- Y<sub>0</sub>\) /δX_ 

If _abs\(D<sub>d</sub>-D<sub>u</sub>\)≤XSLP\_CDTOL\_A_ 
then the derivative is regarded as constant.


_**See also:**_
`XSLP_CDTOL_R`

_**Category:**_ Control

#### XSLP_CDTOL_R, SLPCDTOL_R

_**Description:**_    Relative tolerance for deducing constant derivatives
 
_**Type:**_ Double

_**Topic area:**_ 
Tolerances

_**Default value:**_ 1.0e-08

_**Note:**_

The relative tolerance test for constant derivatives is used as follows:
If the value of the user function at point _X<sub>0</sub>_ is _Y<sub>0</sub>_ and the values at _\(X<sub>0</sub>-δX\)_ and _\(X<sub>0</sub>+δX\)_ are _Y<sub>d</sub>_ and _Y<sub>u</sub>_ respectively, then the numerical derivatives at _X<sub>0</sub>_ are:
"down" derivative _D<sub>d</sub>= \(Y<sub>0</sub>- Y<sub>d</sub>\) /δX_ 
"up" derivative _D<sub>u</sub>= \(Y<sub>u</sub>- Y<sub>0</sub>\) /δX_ 

If _abs\(D<sub>d</sub>-D<sub>u</sub>\)≤XSLP\_CDTOL\_R \* abs\(Y<sub>d</sub>+Y<sub>u</sub>\)/2_ 
then the derivative is regarded as constant.


_**See also:**_
`XSLP_CDTOL_A`

_**Category:**_ Control

#### XSLP_CLAMPSHRINK, SLPCLAMPSHRINK

_**Description:**_    Shrink ratio used to impose strict convergence on variables converged in extended criteria only
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0.3

_**Note:**_

If the solution has converged but there are variables converged on extended criteria only, the XSLP\_CLAMPSHRINK acts as a shrinking ratio on the step bounds and the problem is optimized \(if necessary multiple times\), with the purpose of expediting strict convergence on all variables. `XSLP_ALGORITHM` controls if this shrinking is applied at all, and if shrinking is applied to of the variables converged on extended criteria only with active step bounds only, or if on all variables.


_**See also:**_
`XSLP_ALGORITHM`, `XSLP_CLAMPVALIDATIONTOL_A`, `XSLP_CLAMPVALIDATIONTOL_R`

_**Category:**_ Control

#### XSLP_CLAMPVALIDATIONTOL_A, SLPCLAMPVALIDATIONTOL_A

_**Description:**_    Absolute validation tolerance for applying`XSLP_CLAMPSHRINK`
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 1.0e-06

_**Note:**_

If set and the absolute validation value is larger than this value, then control `XSLP_CLAMPSHRINK` is checked once the solution has converged, but there are variables converged on extended criteria only.


_**See also:**_
`XSLP_ALGORITHM`, `XSLP_CLAMPSHRINK`, `XSLP_CLAMPVALIDATIONTOL_R`

_**Category:**_ Control

#### XSLP_CLAMPVALIDATIONTOL_R, SLPCLAMPVALIDATIONTOL_R

_**Description:**_    Relative validation tolerance for applying`XSLP_CLAMPSHRINK`
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 1.0e-06

_**Note:**_

If set and the relative validation value is larger than this value, then control `XSLP_CLAMPSHRINK` is checked once the solution has converged, but there are variables converged on extended criteria only.


_**See also:**_
`XSLP_ALGORITHM`, `XSLP_CLAMPSHRINK`, `XSLP_CLAMPVALIDATIONTOL_A`

_**Category:**_ Control

#### XSLP_CTOL, SLPCTOL

_**Description:**_    Closure convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Notes:**_
The closure convergence criterion measures the change in value of a variable \( _δX_ \) relative to the value of its initial step bound \( _B_ \), against the closure convergence tolerance. If
 _δX<B \* XSLP\_CTOL_ 
then the variable has converged on the closure convergence criterion.
If no explicit initial step bound is provided, then the test will not be applied and the variable can never converge on the closure criterion.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**See also:**_
Convergence Criteria, `XSLP_ATOL_A`, `XSLP_ATOL_R`

_**Category:**_ Control

#### XSLP_DAMP, SLPDAMP

_**Description:**_    Damping factor for updating values of variables
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1

_**Note:**_
The damping factor sets the next _assumed value_ for a variable based on the previous assumed value \( _X<sub>0</sub>_ \) and the _actual value_ \( _X<sub>1</sub>_ \). The new assumed value is given by
 _X<sub>1</sub>\*XSLP\_DAMP + X<sub>0</sub>\*\(1-XSLP\_DAMP\)_ 

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
Xpress-SLP Solution Process, `XSLP_DAMPEXPAND` `XSLP_DAMPMAX`, `XSLP_DAMPMIN`, `XSLP_DAMPSHRINK`, `XSLP_DAMPSTART`

_**Category:**_ Control

#### XSLP_DAMPEXPAND, SLPDAMPEXPAND

_**Description:**_    Multiplier to increase damping factor during dynamic damping
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1

_**Note:**_
If dynamic damping is enabled, the damping factor for a variable will be increased if successive changes are in the same direction. More precisely, if there are `XSLP_SAMEDAMP` successive changes in the same direction for a variable, then the damping factor \( _D_ \) for the variable will be reset to
 _D\*XSLP\_DAMPEXPAND + XSLP\_DAMPMAX\*\(1-XSLP\_DAMPEXPAND\)_ 

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
Xpress-SLP Solution Process, `XSLP_ALGORITHM`, `XSLP_DAMP`, `XSLP_DAMPMAX`, `XSLP_DAMPMIN`, `XSLP_DAMPSHRINK`, `XSLP_DAMPSTART`, `XSLP_SAMEDAMP`

_**Category:**_ Control

#### XSLP_DAMPMAX, SLPDAMPMAX

_**Description:**_    Maximum value for the damping factor of a variable during dynamic damping
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1

_**Note:**_
If dynamic damping is enabled, the damping factor for a variable will be increased if successive changes are in the same direction. More precisely, if there are `XSLP_SAMEDAMP` successive changes in the same direction for a variable, then the damping factor \( _D_ \) for the variable will be reset to
 _D\*XSLP\_DAMPEXPAND + XSLP\_DAMPMAX\*\(1-XSLP\_DAMPEXPAND\)_ 

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
Xpress-SLP Solution Process, `XSLP_ALGORITHM`, `XSLP_DAMP`, `XSLP_DAMPEXPAND`, `XSLP_DAMPMIN`, `XSLP_DAMPSHRINK`, `XSLP_DAMPSTART`, `XSLP_SAMEDAMP`

_**Category:**_ Control

#### XSLP_DAMPMIN, SLPDAMPMIN

_**Description:**_    Minimum value for the damping factor of a variable during dynamic damping
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1

_**Note:**_
If dynamic damping is enabled, the damping factor for a variable will be decreased if successive changes are in the opposite direction. More precisely, the damping factor \( _D_ \) for the variable will be reset to
 _D\*XSLP\_DAMPSHRINK + XSLP\_DAMPMIN\*\(1-XSLP\_DAMPEXPAND\)_ 

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
Xpress-SLP Solution Process, `XSLP_ALGORITHM`, `XSLP_DAMP`, `XSLP_DAMPEXPAND`, `XSLP_DAMPMAX`, `XSLP_DAMPSHRINK`, `XSLP_DAMPSTART`

_**Category:**_ Control

#### XSLP_DAMPSHRINK, SLPDAMPSHRINK

_**Description:**_    Multiplier to decrease damping factor during dynamic damping
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1

_**Note:**_
If dynamic damping is enabled, the damping factor for a variable will be decreased if successive changes are in the opposite direction. More precisely, the damping factor \( _D_ \) for the variable will be reset to
 _D\*XSLP\_DAMPSHRINK + XSLP\_DAMPMIN\*\(1-XSLP\_DAMPEXPAND\)_ 

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
Xpress-SLP Solution Process, `XSLP_ALGORITHM`, `XSLP_DAMP`, `XSLP_DAMPEXPAND`, `XSLP_DAMPMAX`, `XSLP_DAMPMIN`, `XSLP_DAMPSTART`

_**Category:**_ Control

#### XSLP_DEFAULTIV, NLPDEFAULTIV

_**Description:**_    Default initial value for an SLP variable if none is explicitly given
 
_**Type:**_ Double

_**Topic area:**_ 
Data Input

_**Default value:**_ 100

_**Note:**_
If no initial value is given for an SLP variable, then the initial value provided for the "equals column" will be used. If no such value has been provided, then `XSLP_DEFAULTIV` will be used. If this is above the upper bound for the variable, then the upper bound will be used; if it is below the lower bound for the variable, then the lower bound will be used.

_**Affects routines:**_ `XSLPconstruct`
_**Category:**_ Control

#### XSLP_DEFAULTSTEPBOUND, SLPDEFAULTSTEPBOUND

_**Description:**_    Minimum initial value for the step bound of an SLP variable if none is explicitly given
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 16

_**Notes:**_
If no initial step bound value is given for an SLP variable, this will be used as a minimum value. If the algorithm is estimating step bounds, then the step bound actually used for a variable may be larger than the default.
A default initial step bound is ignored when testing for the closure tolerance `XSLP_CTOL`: if there is no specific value, then the test will not be applied.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_CTOL`

_**Category:**_ Control

#### XSLP_DELTA_A, SLPDELTA_A

_**Description:**_    Absolute perturbation of values for calculating numerical derivatives
 
_**Type:**_ Double

_**Topic area:**_ 
Derivatives

_**Default value:**_ 0.001

_**Note:**_
First-order derivatives are calculated by perturbing the value of each variable in turn by a small amount. The amount is determined by the absolute and relative delta factors as follows:
 _XSLP\_DELTA\_A + abs\(X\)\*XSLP\_DELTA\_R_ 
where \( _X_ \) is the current value of the variable. If the perturbation takes the variable outside a bound, then the perturbation normally made only in the opposite direction.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTA_R`

_**Category:**_ Control

#### XSLP_DELTA_INFINITY, SLPDELTA_INFINITY

_**Description:**_    Maximum value for partial derivatives
 
_**Type:**_ Double

_**Topic area:**_ 
Derivatives

_**Default value:**_ 1.0e+15

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_DELTA_R, SLPDELTA_R

_**Description:**_    Relative perturbation of values for calculating numerical derivatives
 
_**Type:**_ Double

_**Topic area:**_ 
Derivatives

_**Default value:**_ 0.001

_**Note:**_
First-order derivatives are calculated by perturbing the value of each variable in turn by a small amount. The amount is determined by the absolute and relative delta factors as follows:
 _XSLP\_DELTA\_A + abs\(X\)\*XSLP\_DELTA\_R_ 
where \( _X_ \) is the current value of the variable. If the perturbation takes the variable outside a bound, then the perturbation normally made only in the opposite direction.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTA_A`

_**Category:**_ Control

#### XSLP_DELTA_X, SLPDELTA_X

_**Description:**_    Minimum absolute value of delta coefficients to be retained
 
_**Type:**_ Double

_**Topic area:**_ 
Derivatives

_**Default value:**_ 1.0e-6

_**Notes:**_
If the value of a coefficient in a delta column is less than this value, it will be reset to zero.
Larger values of `XSLP_DELTA_X`will result in matrices with fewer elements, which may be easier to solve. However, there will be increased likelihood of local optima as some of the small relationships between variables and constraints are deleted. There may also be increased difficulties with singular bases resulting from deletion of pivot elements from the matrix.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_DELTA_Z, SLPDELTA_Z

_**Description:**_    Tolerance used when calculating derivatives
 
_**Type:**_ Double

_**Topic areas:**_ 
Derivatives, Tolerances

_**Default value:**_ 0.00001

_**Notes:**_
If the absolute value of a variable is less than this value, then a value of `XSLP_DELTA_Z` will be used instead for calculating derivatives.
If a nonzero derivative is calculated for a formula which always results in a matrix coefficient less than `XSLP_DELTA_Z`, then a larger value will be substituted so that at least one of the coefficients is `XSLP_DELTA_Z`in magnitude.
If `XSLP_DELTAZLIMIT`is set to a positive number, then when that number of iterations have passed, values smaller than `XSLP_DELTA_Z`will be set to zero.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTAZLIMIT`, `XSLP_DELTA_ZERO`

_**Category:**_ Control

#### XSLP_DELTA_ZERO, SLPDELTA_ZERO

_**Description:**_    Absolute zero acceptance tolerance used when calculating derivatives
 
_**Type:**_ Double

_**Topic areas:**_ 
Derivatives, Tolerances

_**Default value:**_ -1.0 \(not applied\)

_**Notes:**_
Provides an override value for the XSLP\_DELTA\_Z behavior. Derivatives smaller than XSLP\_DELTA\_ZERO will not be substituted by XSLP\_DELTA\_Z, defining a range in which derivatives are deemed nonzero and are affected by XSLP\_DELTA\_Z.
A negative value means that this tolerance will not be applied.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTAZLIMIT`, `XSLP_DELTA_Z`

_**Category:**_ Control

#### XSLP_DELTACOST, SLPDELTACOST

_**Description:**_    Initial penalty cost multiplier for penalty delta vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 200

_**Note:**_
If penalty delta vectors are used, this parameter sets the initial cost factor. If there are active penalty delta vectors, then the penalty cost may be increased.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_DELTACOSTFACTOR`, `XSLP_DELTAMAXCOST`, `XSLP_ERRORCOST`

_**Category:**_ Control

#### XSLP_DELTACOSTFACTOR, SLPDELTACOSTFACTOR

_**Description:**_    Factor for increasing cost multiplier on total penalty delta vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1.3

_**Note:**_
If there are active penalty delta vectors, then the penalty cost multiplier will be increased by a factor of `XSLP_DELTA COST FACTOR` up to a maximum of `XSLP_DELTA MAX COST`

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_DELTACOST`, `XSLP_DELTAMAXCOST`, `XSLP_ERRORCOST`

_**Category:**_ Control

#### XSLP_DELTAMAXCOST, SLPDELTAMAXCOST

_**Description:**_    Maximum penalty cost multiplier for penalty delta vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ XPRS\_PLUSINFINITY

_**Note:**_
If there are active penalty delta vectors, then the penalty cost multiplier will be increased by a factor of `XSLP_DELTA COST FACTOR` up to a maximum of `XSLP_DELTA MAX COST`

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_DELTACOST`, `XSLP_DELTACOSTFACTOR`, `XSLP_ERRORCOST`

_**Category:**_ Control

#### XSLP_DJTOL, SLPDJTOL

_**Description:**_    Tolerance on DJ value for determining if a variable is at its step bound
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 1.0e-6

_**Note:**_
If a variable is at its step bound and within the absolute delta tolerance `XSLP_ATOL_A` or closure tolerance `XSLP_CTOL` then the step bounds will not be further reduced. If the DJ is greater in magnitude than `XSLP_DJTOL` then the step bound may be relaxed if it meets the necessary criteria.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ATOL_A`, `XSLP_CTOL`

_**Category:**_ Control

#### XSLP_DRCOLDJTOL, SLPDRCOLDJTOL

_**Description:**_    Reduced cost tolerance on the delta variable when fixing due to the determining column being below`XSLP_DRCOLTOL`.
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Cascading, Tolerances

_**Default value:**_ 0.0

_**Affects routines:**_ `XSLPconstruct``XSLPcascade`
_**Category:**_ Control

#### XSLP_DRCOLTOL, SLPDRCOLTOL

_**Description:**_    The minimum absolute magnitude of a determining column, for which the determined variable is still regarded as well defined
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Cascading, Tolerances

_**Default value:**_ 1.0e-6

_**Notes:**_
This control affects the cascading procedure. Please see Chapter  _Cascading_ for more information.

_**Affects routines:**_ `XSLPconstruct``XSLPcascade`

_**See also:**_
`XSLP_CASCADE`

_**Category:**_ Control

#### XSLP_DRFIXRANGE, SLPDRFIXRANGE

_**Description:**_    The range around the previous value where variables are fixed in cascading if the determining column is below`XSLP_DRCOLTOL`.
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Cascading

_**Default value:**_ 0.1

_**Notes:**_
This control affects the cascading procedure. Please see Chapter  _Cascading_ for more information.

_**Affects routines:**_ `XSLPconstruct``XSLPcascade`

_**See also:**_
`XSLP_CASCADE` `XSLP_DRCOLTOL`

_**Category:**_ Control

#### XSLP_ECFTOL_A, SLPECFTOL_A

_**Description:**_    Absolute tolerance on testing feasibility at the point of linearization
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Notes:**_
The extended convergence criteria test how well the linearization approximates the true problem. They depend on the point of linearization being a reasonable approximation— in particular, that it should be reasonably close to feasibility. Each constraint is tested at the point of linearization, and the total positive and negative contributions to the constraint from the columns in the problem are calculated. A feasibility tolerance is calculated as the largest of _XSLP_ECFTOL_A_  and
 _max\(abs\(Positive\), abs\(Negative\)\) \* XSLP\_ECFTOL\_R_ 
If the calculated infeasibility is greater than the tolerance, the point of linearization is regarded as infeasible and the extended convergence criteria will not be applied.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-1 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
[Convergence criteria](#secConvergence), `XSLP_ECFCHECK`, `XSLP_ECFCOUNT`, `XSLP_ECFTOL_R`

_**Category:**_ Control

#### XSLP_ECFTOL_R, SLPECFTOL_R

_**Description:**_    Relative tolerance on testing feasibility at the point of linearization
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Notes:**_
The extended convergence criteria test how well the linearization approximates the true problem. They depend on the point of linearization being a reasonable approximation— in particular, that it should be reasonably close to feasibility. Each constraint is tested at the point of linearization, and the total positive and negative contributions to the constraint from the columns in the problem are calculated. A feasibility tolerance is calculated as the largest of _XSLP_ECFTOL_A_  and
 _max\(abs\(Positive\), abs\(Negative\)\) \* XSLP\_ECFTOL\_R_ 
If the calculated infeasibility is greater than the tolerance, the point of linearization is regarded as infeasible and the extended convergence criteria will not be applied.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-1 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
[Convergence criteria](#secConvergence), `XSLP_ECFCHECK`, `XSLP_ECFCOUNT`, `XSLP_ECFTOL_A`

_**Category:**_ Control

#### XSLP_ENFORCECOSTSHRINK, SLPENFORCECOSTSHRINK

_**Description:**_    Factor by which to decrease the current penalty multiplier when enforcing rows.
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0.00001

_**Notes:**_
When feasiblity of a row cannot be achieved by increasing the penalty cost on its error variable, removing the variable \(fixing it to zero\) can force the row to be satisfied, as set by `XSLP_ENFORCEMAXCOST`. After the error variables have been removed \(which is equivalent to setting to row to be enforced\) the penalties on the remaining error variables are rebalanced to allow for a reduction in the size of the penalties in the objective in order to achive better numerical behaviour.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ENFORCEMAXCOST`

_**Category:**_ Control

#### XSLP_ENFORCEMAXCOST, SLPENFORCEMAXCOST

_**Description:**_    Maximum penalty cost in the objective before enforcing most violating rows
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1.0e+11

_**Notes:**_
When feasiblity of a row cannot be achieved by increasing the penalty cost on its error variable, removing the variable \(fixing it to zero\) can force the row to be satisfied. After the error variables have been removed \(which is equivalent to setting to row to be enforced\) the penalties on the remaining error variables are rebalanced to allow for a reduction in the size of the penalties in the objective in order to achive better numerical behaviour, controlled by `XSLP_ENFORCECOSTSHRINK`.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ENFORCECOSTSHRINK`

_**Category:**_ Control

#### XSLP_ERRORCOST, SLPERRORCOST

_**Description:**_    Initial penalty cost multiplier for penalty error vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 200

_**Note:**_
If penalty error vectors are used, this parameter sets the initial cost factor. If there are active penalty error vectors, then the penalty cost may be increased.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_DELTACOST`, `XSLP_ERRORCOSTFACTOR`, `XSLP_ERRORMAXCOST`

_**Category:**_ Control

#### XSLP_ERRORCOSTFACTOR, SLPERRORCOSTFACTOR

_**Description:**_    Factor for increasing cost multiplier on total penalty error vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1.3

_**Note:**_
If there are active penalty error vectors, then the penalty cost multiplier will be increased by a factor of `XSLP_ERROR COST FACTOR` up to a maximum of `XSLP_ERROR MAX COST`

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_ERRORMAXCOST`

_**Category:**_ Control

#### XSLP_ERRORMAXCOST, SLPERRORMAXCOST

_**Description:**_    Maximum penalty cost multiplier for penalty error vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Let the solver decide.
 `>=0`| Maximum penalty cost multiplier.

_**Default value:**_ -1.0

_**Note:**_
If there are active penalty error vectors, then the penalty cost multiplier will be increased by a factor of `XSLP_ERROR COST FACTOR` up to a maximum of `XSLP_ERROR MAX COST`

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_ERRORCOSTFACTOR`

_**Category:**_ Control

#### XSLP_ERRORTOL_A, SLPERRORTOL_A

_**Description:**_    Absolute tolerance for error vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 0.00001

_**Note:**_
The solution will be regarded as having no active error vectors if one of the following applies:
every penalty error vector and penalty delta vector has an activity less than _XSLP\_ERRORTOL\_A_ ;
the sum of the cost contributions from all the penalty error and penalty delta vectors is less than _XSLP\_EVTOL\_A_ ;
the sum of the cost contributions from all the penalty error and penalty delta vectors is less than _XSLP\_EVTOL\_R \* Obj_ where _Obj_ is the current objective function value.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_EVTOL_A`, `XSLP_EVTOL_R`

_**Category:**_ Control

#### XSLP_ERRORTOL_P, SLPERRORTOL_P

_**Description:**_    Absolute tolerance for printing error vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 0.0001

_**Note:**_
The solution log includes a print of penalty delta and penalty error vectors with an activity greater than _XSLP\_ERRORTOL\_P_ .

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_ESCALATION, SLPESCALATION

_**Description:**_    Factor for increasing cost multiplier on individual penalty error vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1.25

_**Note:**_
If penalty cost escalation is activated in `XSLP_ALGORITHM` then the penalty cost multiplier will be increased by a factor of `XSLP_ESCALATION` for any active error vector up to a maximum of `XSLP_MAXWEIGHT`.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ALGORITHM`, `XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_MAXWEIGHT`

_**Category:**_ Control

#### XSLP_ETOL_A, SLPETOL_A

_**Description:**_    Absolute tolerance on penalty vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 0.0001

_**Note:**_
For each penalty error vector, the contribution to its constraint is calculated, together with the total positive and negative contributions to the constraint from other vectors. If its contribution is less than _XSLP\_ETOL\_A_  or less than _Positive\*XSLP\_ETOL\_R_  or less than _abs\(Negative\)\*XSLP\_ETOL\_R_  then it will be regarded as insignificant and will not have its penalty increased.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ETOL_R` `XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_ESCALATION`

_**Category:**_ Control

#### XSLP_ETOL_R, SLPETOL_R

_**Description:**_    Relative tolerance on penalty vectors
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 0.0001

_**Note:**_
For each penalty error vector, the contribution to its constraint is calculated, together with the total positive and negative contributions to the constraint from other vectors. If its contribution is less than _XSLP\_ETOL\_A_  or less than _Positive\*XSLP\_ETOL\_R_  or less than _abs\(Negative\)\*XSLP\_ETOL\_R_  then it will be regarded as insignificant and will not have its penalty increased.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ETOL_A` `XSLP_DELTACOST`, `XSLP_ERRORCOST`, `XSLP_ESCALATION`

_**Category:**_ Control

#### XSLP_EVTOL_A, SLPEVTOL_A

_**Description:**_    Absolute tolerance on total penalty costs
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The solution will be regarded as having no active error vectors if one of the following applies:
every penalty error vector and penalty delta vector has an activity less than _XSLP\_ERRORTOL\_A_ ;
the sum of the cost contributions from all the penalty error and penalty delta vectors is less than _XSLP\_EVTOL\_A_ ;
the sum of the cost contributions from all the penalty error and penalty delta vectors is less than _XSLP\_EVTOL\_R \* Obj_ where _Obj_ is the current objective function value.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-2 and 1e-6, but normally a magnitude larger than `XSLP_ETOL_A`.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ERRORTOL_A`, `XSLP_EVTOL_R`

_**Category:**_ Control

#### XSLP_EVTOL_R, SLPEVTOL_R

_**Description:**_    Relative tolerance on total penalty costs
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The solution will be regarded as having no active error vectors if one of the following applies:
every penalty error vector and penalty delta vector has an activity less than _XSLP\_ERRORTOL\_A_ ;
the sum of the cost contributions from all the penalty error and penalty delta vectors is less than _XSLP\_EVTOL\_A_ ;
the sum of the cost contributions from all the penalty error and penalty delta vectors is less than _XSLP\_EVTOL\_R \* Obj_ where _Obj_ is the current objective function value.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-2 and 1e-6, but normally a magnitude larger than `XSLP_ETOL_R`.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ERRORTOL_A`, `XSLP_EVTOL_A`

_**Category:**_ Control

#### XSLP_EXPAND, SLPEXPAND

_**Description:**_    Multiplier to increase a step bound
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 2

_**Note:**_
If step bounding is enabled, the step bound for a variable will be increased if successive changes are in the same direction. More precisely, if there are `XSLP_SAMECOUNT` successive changes reaching the step bound and in the same direction for a variable, then the step bound \( _B_ \) for the variable will be reset to
 _B\*XSLP\_EXPAND_ .

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SHRINK`, `XSLP_SHRINKBIAS`, `XSLP_SAMECOUNT`

_**Category:**_ Control

#### XSLP_FEASTOLTARGET, SLPFEASTOLTARGET

_**Description:**_    When set, this defines a target feasibility tolerance to which the linearizations are solved to
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Linearizations, Tolerances

_**Default value:**_ 0 \(ignored, not set\)

_**Note:**_
This is a soft version of XPRS\_FEASTOL, and will dynamically revert back to XPRS\_FEASTOL if the desired accuracy could not be achieved.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_OPTIMALITYTOLTARGET`,

_**Category:**_ Control

#### XSLP_GRANULARITY, SLPGRANULARITY

_**Description:**_    Base for calculating penalty costs
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 4

_**Note:**_
If `XSLP_GRANULARITY`> 1, then initial penalty costs will be powers of `XSLP_ GRANUL ARITY`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_MAXWEIGHT`, `XSLP_MINWEIGHT`

_**Category:**_ Control

#### XSLP_INFINITY, NLPINFINITY

_**Description:**_    Value returned by a divide-by-zero in a formula
 
_**Type:**_ Double

_**Topic area:**_ 
Numerics

_**Default value:**_ 1.0e+10
_**Category:**_ Control

#### XSLP_ITOL_A, SLPITOL_A

_**Description:**_    Absolute impact convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The absolute impact convergence criterion assesses the change in the effect of a coefficient in a constraint. The _effect_ of a coefficient is its value multiplied by the activity of the column in which it appears.

_E=X \* C_
where _X_ is the activity of the matrix column in which the coefficient appears, and _C_ is the value of the coefficient. The linearization approximates the effect of the coefficient as

_E<sub>1</sub>=X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>_
where _X_ is as before, _C<sub>0</sub>_ is the value of the coefficient _C_ calculated using the assumed values for the variables and _C'<sub>0</sub>_ is the value of _\(∂C\) / \(∂X\)_ calculated using the assumed values for the variables.
If _C<sub>1</sub>_ is the value of the coefficient _C_ calculated using the actual values for the variables, then the error in the effect of the coefficient is given by
_δE = X \* C<sub>1</sub>- \(X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>\)_
If _δE<XSLP\_ITOL\_A_ 
then the variable has passed the absolute impact convergence criterion for this coefficient.
If a variable which has not converged on strict \(closure or delta\) criteria passes the \(relative or absolute\) impact or matrix criteria for all the coefficients in which it appears, then it is deemed to have converged.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ITOL_R`, `XSLP_MTOL_A`, `XSLP_MTOL_R`, `XSLP_STOL_A`, `XSLP_STOL_R`

_**Category:**_ Control

#### XSLP_ITOL_R, SLPITOL_R

_**Description:**_    Relative impact convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The relative impact convergence criterion assesses the change in the effect of a coefficient in a constraint in relation to the magnitude of the constituents of the constraint. The _effect_ of a coefficient is its value multiplied by the activity of the column in which it appears.

_E=X \* C_
where _X_ is the activity of the matrix column in which the coefficient appears, and _C_ is the value of the coefficient. The linearization approximates the effect of the coefficient as

_E<sub>1</sub>=X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>_
where _X_ is as before, _C<sub>0</sub>_ is the value of the coefficient _C_ calculated using the assumed values for the variables and _C'<sub>0</sub>_ is the value of _\(∂C\) / \(∂X\)_ calculated using the assumed values for the variables.
If _C<sub>1</sub>_ is the value of the coefficient _C_ calculated using the actual values for the variables, then the error in the effect of the coefficient is given by
_δE = X \* C<sub>1</sub>- \(X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>\)_
All the elements of the constraint are examined, excluding delta and error vectors: for each, the contribution to the constraint is evaluated as the element multiplied by the activity of the vector in which it appears; it is then included in a _total positive contribution_or _total negative contribution_depending on the sign of the contribution. If the predicted effect of the coefficient is positive, it is tested against the total positive contribution; if the effect of the coefficient is negative, it is tested against the total negative contribution. If _T<sub>0</sub>_ is the total positive or total negative contribution to the constraint \(as appropriate\)
and _δE<T<sub>0</sub>\*XSLP\_ITOL\_R_ 
then the variable has passed the relative impact convergence criterion for this coefficient.
If a variable which has not converged on strict \(closure or delta\) criteria passes the \(relative or absolute\) impact or matrix criteria for all the coefficients in which it appears, then it is deemed to have converged.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ITOL_A`, `XSLP_MTOL_A`, `XSLP_MTOL_R`, `XSLP_STOL_A`, `XSLP_STOL_R`

_**Category:**_ Control

#### XSLP_MATRIXTOL, SLPMATRIXTOL

_**Description:**_    Nonzero tolerance for dropping coefficients from the linearization.
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0.0

_**Note:**_
Any value smaller than XSLP\_MATRIXTOL in magnitude will not be loaded into the linearization. This only applies to the matrix coefficients; bounds, right hand sides and objectives are not affected.

_**Affects routines:**_ `XSLPconstruct`,`XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_MAXWEIGHT, SLPMAXWEIGHT

_**Description:**_    Maximum penalty weight for delta or error vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 100

_**Note:**_
When penalty vectors are created, or when their weight is increased by escalation, the maximum weight that will be used is given by `XSLP_MAXWEIGHT`.

_**Affects routines:**_ `XSLPconstruct`,`XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ALGORITHM`, `XSLP_AUGMENTATION`, `XSLP_ESCALATION`, `XSLP_MINWEIGHT`

_**Category:**_ Control

#### XSLP_MEMORYFACTOR

_**Description:**_    Factor for expanding size of dynamic arrays in memory
 
_**Type:**_ Double

_**Topic area:**_ 
Memory

_**Default value:**_ 1.6

_**Note:**_
When a dynamic array has to be increased in size, the new space allocated will be `XSLP_MEMORYFACTOR` times as big as the previous size. A larger value may result in improved performance because arrays need to be re-sized and moved less frequently; however, more memory may be required under such circumstances because not all of the previous memory area can be re-used efficiently.

_**See also:**_
Memory control variables `XSLP_MEM*` Memory control variables `XSLP_MEM*`

_**Category:**_ Control

#### XSLP_MERITLAMBDA, NLPMERITLAMBDA

_**Description:**_    Factor by which the net objective is taken into account in the merit function
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Solution

_**Default value:**_ 0.0

_**Note:**_
The merit function is evaluated in the original, non-augmented / linearized space of the problem. A solution is deemed improved, if either feasibility improved, or if feasibility is not deteriorated but the net objective is improved, or if the combination of the two is improved, where the value of the XSLP\_MERITLAMBDA control is used to combine the two measures. A nonpositive value indicates that the combined effect should not be checked.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_FILTER` `XSLP_LSITERLIMIT` `XSLP_LSPATTERNLIMIT`

_**Category:**_ Control

#### XSLP_MINSBFACTOR, SLPMINSBFACTOR

_**Description:**_    Factor by which step bounds can be decreased beneath `XSLP_ATOL_A`
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1.0

_**Note:**_
Normally, step bounds are not decreased beneath `XSLP_ATOL_A`, as such variables are treated as converged. However, it may be beneficial to decrease step bounds further, as individual variable value changes might affect the convergence of other variables in the model, even if the variablke itself is deemed converged.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ATOL_A`

_**Category:**_ Control

#### XSLP_MINWEIGHT, SLPMINWEIGHT

_**Description:**_    Minimum penalty weight for delta or error vectors
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0.01

_**Note:**_
When penalty vectors are created, the minimum weight that will be used is given by `XSLP_MINWEIGHT`.

_**Affects routines:**_ `XSLPconstruct`,`XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_AUGMENTATION`, `XSLP_MAXWEIGHT`

_**Category:**_ Control

#### XSLP_MIPCUTOFF_A, SLPMIPCUTOFF_A

_**Description:**_    Absolute objective function cutoff for MIP termination
 
_**Type:**_ Double

_**Topic areas:**_ 
MISLP, Tolerances

_**Default value:**_ 0.00001

_**Note:**_
If the objective function is worse by a defined amount than the best integer solution obtained so far, then the SLP will be terminated \(and the node will be cut off\). The node will be cut off at the current SLP iteration if the objective function for the last `XSLP_MIPCUTOFFCOUNT` SLP iterations are all worse than the best obtained so far, and the difference is greater than _XSLP\_MIPCUTOFF\_A_  and _OBJ \* XSLP\_MIPCUTOFF\_R_  where _OBJ_  is the best integer solution obtained so far.
The MIP cutoff tests are only applied after `XSLP_MIPCUTOFFLIMIT`SLP iterations at the current node.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPCUTOFFCOUNT`, `XSLP_MIPCUTOFFLIMIT`, `XSLP_MIPCUTOFF_R`

_**Category:**_ Control

#### XSLP_MIPCUTOFF_R, SLPMIPCUTOFF_R

_**Description:**_    Absolute objective function cutoff for MIP termination
 
_**Type:**_ Double

_**Topic areas:**_ 
MISLP, Tolerances

_**Default value:**_ 0.00001

_**Note:**_
If the objective function is worse by a defined amount than the best integer solution obtained so far, then the SLP will be terminated \(and the node will be cut off\). The node will be cut off at the current SLP iteration if the objective function for the last `XSLP_MIPCUTOFFCOUNT` SLP iterations are all worse than the best obtained so far, and the difference is greater than _XSLP\_MIPCUTOFF\_A_  and _OBJ \* XSLP\_MIPCUTOFF\_R_  where _OBJ_  is the best integer solution obtained so far.
The MIP cutoff tests are only applied after `XSLP_MIPCUTOFFLIMIT`SLP iterations at the current node.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPCUTOFFCOUNT`, `XSLP_MIPCUTOFFLIMIT`, `XSLP_MIPCUTOFF_A`

_**Category:**_ Control

#### XSLP_MIPERRORTOL_A, SLPMIPERRORTOL_A

_**Description:**_    Absolute penalty error cost tolerance for MIP cut-off
 
_**Type:**_ Double

_**Topic areas:**_ 
MISLP, Tolerances

_**Default value:**_ 0 \(inactive\)

_**Note:**_
The penalty error cost test is applied at each node where there are active penalties in the solution. If `XSLP_MIPERRORTOL_A` is nonzero and the absolute value of the penalty costs is greater than `XSLP_MIPERRORTOL_A`, the node will be declared infeasible. If `XSLP_MIPERRORTOL_A` is zero then no test is made and the node will not be declared infeasible on this criterion.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPERRORTOL_R`

_**Category:**_ Control

#### XSLP_MIPERRORTOL_R, SLPMIPERRORTOL_R

_**Description:**_    Relative penalty error cost tolerance for MIP cut-off
 
_**Type:**_ Double

_**Topic areas:**_ 
MISLP, Tolerances

_**Default value:**_ 0 \(inactive\)

_**Note:**_
The penalty error cost test is applied at each node where there are active penalties in the solution. If `XSLP_MIPERRORTOL_R` is nonzero and the absolute value of the penalty costs is greater than _XSLP\_MIPERRORTOL\_R \* abs\(Obj\)_  where _Obj_  is the value of the objective function, then the node will be declared infeasible. If `XSLP_MIPERRORTOL_R` is zero then no test is made and the node will not be declared infeasible on this criterion.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPERRORTOL_A`

_**Category:**_ Control

#### XSLP_MIPOTOL_A, SLPMIPOTOL_A

_**Description:**_    Absolute objective function tolerance for MIP termination
 
_**Type:**_ Double

_**Topic areas:**_ 
MISLP, SLP-convergence, Tolerances

_**Default value:**_ 0.00001

_**Note:**_
The objective function test for MIP termination is applied only when step bounding has been applied \(or `XSLP_SBSTART` SLP iterations have taken place if step bounding is not being used\). The node will be terminated at the current SLP iteration if the range of the objective function values over the last `XSLP_MIPOCOUNT` SLP iterations is within _XSLP\_MIPOTOL\_A_  or within _OBJ \* XSLP\_MIPOTOL\_R_  where _OBJ_  is the average value of the objective function over those iterations.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPOCOUNT` `XSLP_MIPOTOL_R` `XSLP_SBSTART`

_**Category:**_ Control

#### XSLP_MIPOTOL_R, SLPMIPOTOL_R

_**Description:**_    Relative objective function tolerance for MIP termination
 
_**Type:**_ Double

_**Topic areas:**_ 
MISLP, SLP-convergence, Tolerances

_**Default value:**_ 0.00001

_**Note:**_
The objective function test for MIP termination is applied only when step bounding has been applied \(or `XSLP_SBSTART` SLP iterations have taken place if step bounding is not being used\). The node will be terminated at the current SLP iteration if the range of the objective function values over the last `XSLP_MIPOCOUNT` SLP iterations is within _XSLP\_MIPOTOL\_A_  or within _OBJ \* XSLP\_MIPOTOL\_R_  where _OBJ_  is the average value of the objective function over those iterations.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPOCOUNT` `XSLP_MIPOTOL_A` `XSLP_SBSTART`

_**Category:**_ Control

#### XSLP_MSMAXBOUNDRANGE, MSMAXBOUNDRANGE

_**Description:**_    Defines the maximum range inside which initial points are generated by multistart presets
 
_**Type:**_ Double

_**Topic area:**_ 
Multistart

_**Default value:**_ 1000

_**Note:**_
The is the maximum range in which initial points are generated; the actual range is expected to be smaller as bounds are domains are also considered.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART`

_**Category:**_ Control

#### XSLP_MTOL_A, SLPMTOL_A

_**Description:**_    Absolute effective matrix element convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The absolute effective matrix element convergence criterion assesses the change in the effect of a coefficient in a constraint. The _effect_ of a coefficient is its value multiplied by the activity of the column in which it appears.

_E=X \* C_
where _X_ is the activity of the matrix column in which the coefficient appears, and _C_ is the value of the coefficient. The linearization approximates the effect of the coefficient as

_E=X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>_
where _V_ is as before, _C<sub>0</sub>_ is the value of the coefficient _C_ calculated using the assumed values for the variables and _C'<sub>0</sub>_ is the value of _\(∂C\) / \(∂X\)_ calculated using the assumed values for the variables.
If _C<sub>1</sub>_ is the value of the coefficient _C_ calculated using the actual values for the variables, then the error in the effect of the coefficient is given by
_δE = X \* C<sub>1</sub>- \(X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>\)_
If _δE<X \* XSLP\_MTOL\_A_ 
then the variable has passed the absolute effective matrix element convergence criterion for this coefficient.
If a variable which has not converged on strict \(closure or delta\) criteria passes the \(relative or absolute\) impact or matrix criteria for all the coefficients in which it appears, then it is deemed to have converged.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ITOL_A`, `XSLP_ITOL_R`, `XSLP_MTOL_R`, `XSLP_STOL_A`, `XSLP_STOL_R`

_**Category:**_ Control

#### XSLP_MTOL_R, SLPMTOL_R

_**Description:**_    Relative effective matrix element convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The relative effective matrix element convergence criterion assesses the change in the effect of a coefficient in a constraint relative to the magnitude of the coefficient. The _effect_ of a coefficient is its value multiplied by the activity of the column in which it appears.

_E=X \* C_
where _X_ is the activity of the matrix column in which the coefficient appears, and _C_ is the value of the coefficient. The linearization approximates the effect of the coefficient as

_E<sub>1</sub>=X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>_
where _V_ is as before, _C<sub>0</sub>_ is the value of the coefficient _C_ calculated using the assumed values for the variables and _C'<sub>0</sub>_ is the value of _\(∂C\) / \(∂X\)_ calculated using the assumed values for the variables.
If _C<sub>1</sub>_ is the value of the coefficient _C_ calculated using the actual values for the variables, then the error in the effect of the coefficient is given by
_δE = X \* C<sub>1</sub>- \(X \* C<sub>0</sub>  +  δX \* C'<sub>0</sub>\)_
If _δE<E<sub>1</sub>\* XSLP\_MTOL\_R_ 
then the variable has passed the relative effective matrix element convergence criterion for this coefficient.
If a variable which has not converged on strict \(closure or delta\) criteria passes the \(relative or absolute\) impact or matrix criteria for all the coefficients in which it appears, then it is deemed to have converged.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ITOL_A`, `XSLP_ITOL_R`, `XSLP_MTOL_A`, `XSLP_STOL_A`, `XSLP_STOL_R`

_**Category:**_ Control

#### XSLP_MVTOL, SLPMVTOL

_**Description:**_    Marginal value tolerance for determining if a constraint is slack
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
If the absolute value of the marginal value of a constraint is less than `XSLP_MVTOL`, then
\(1\) the constraint is regarded as not constraining for the purposes of the slack tolerance convergence criteria;
\(2\) the constraint is not regarded as an _active constraint_when identifying unconverged variables in active constraints.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_STOL_A`, `XSLP_STOL_R`

_**Category:**_ Control

#### XSLP_OBJSENSE

_**Description:**_    _This parameter is deprecated and will be removed in a future release. Please use[`XPRSchgobjsense`](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSchgobjsense.html)instead._
   Objective function sense.
 
_**Type:**_ Double

_**Topic area:**_ 
Problem Modification

_**Default value:**_ +1

_**Note:**_
`XSLP_OBJSENSE` is set to +1 for minimization and to -1 for maximization. It is automatically set by `XSLPmaxim` and `XSLPminim`; it must be set by the user before calling `XSLPnlpoptimize`.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`,`XSLPnlpoptimize`

_**Set by routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_OBJTHRESHOLD, SLPOBJTHRESHOLD

_**Description:**_    Assumed maximum value of the objective function in absolute value.
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 1.0e+15

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_OBJTOPENALTYCOST, SLPOBJTOPENALTYCOST

_**Description:**_    Factor to estimate initial penalty costs from objective function
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0

_**Notes:**_
The setting of initial penalty error costs can affect the path of the optimization and, indeed, whether a solution is achieved at all. If the penalty costs are too low, then unbounded solutions may result although Xpress-SLP will increase the costs in an attempt to recover. If the penalty costs are too high, then the requirement to achieve feasibility of the linearized constraints may be too strong to allow the system to explore the nonlinear feasible region. Low penalty costs can result in many SLP iterations, as feasibility of the nonlinear constraints is not achieved until the penalty costs become high enough; high penalty costs force feasibility of the linearizations, and so tend to find local optima close to an initial feasible point. Xpress-SLP can analyze the problem to estimate the size of penalty costs required to avoid an initial unbounded solution. `XSLP_OBJTOPENALTYCOST` can be used in conjunction with this procedure to scale the costs and give an appropriate initial value for balancing the requirements of feasibility and optimality.
Not all models are amenable to the Xpress-SLP analysis. As the analysis is initially concerned with establishing a cost level to avoid unboundedness, a model which is sufficiently constrained will never show unboundedness regardless of the cost. Also, as the analysis is done at the start of the optimization to establish a penalty cost, significant changes in the coefficients, or a high degree of nonlinearity, may invalidate the initial analysis.
A setting for `XSLP_OBJ TO PENALTY COST`of zero disables the analysis. A setting of 3 or 4 has proved successful for many models. If `XSLP_OBJ TO PENALTY COST`cannot be used because of the problem structure, its effect can still be emulated by some initial experiments to establish the cost required to avoid unboundedness, and then manually applying a suitable factor. If the problem is initially unbounded, then the penalty cost will be increased until either it reaches its maximum or the problem becomes bounded.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_OPTIMALITYTOLTARGET, SLPOPTIMALITYTOLTARGET

_**Description:**_    When set, this defines a target optimality tolerance to which the linearizations are solved to
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Linearizations, Tolerances

_**Default value:**_ 0 \(ignored, not set\)

_**Note:**_
This is a soft version of XPRS\_ OPTIMALITYTOL, and will dynamically revert back to XPRS\_OPTIMALITYTOL if the desired accuracy could not be achieved.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_FEASTOLTARGET`,

_**Category:**_ Control

#### XSLP_OTOL_A, SLPOTOL_A

_**Description:**_    Absolute static objective \(2\) convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The static objective \(2\) convergence criterion does not measure convergence of individual variables. Instead, it measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables interacting with active constraints \(those that have a marginal value of at least `XSLP_MVTOL`\) have converged. The rationale is that if the remaining unconverged variables are not involved in active constraints and if the objective function is not changing significantly between iterations, then the solution is more-or-less practical.
The variation in the objective function is defined as
_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_OCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤XSLP\_OTOL\_A_ 
then the problem has converged on the absolute static objective \(2\) convergence criterion.
The static objective function \(2\) test is applied only if `XSLP_OCOUNT`is at least 2.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_OCOUNT`, `XSLP_OTOL_R`

_**Category:**_ Control

#### XSLP_OTOL_R, SLPOTOL_R

_**Description:**_    Relative static objective \(2\) convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The static objective \(2\) convergence criterion does not measure convergence of individual variables. Instead, it measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables interacting with active constraints \(those that have a marginal value of at least `XSLP_MVTOL`\) have converged. The rationale is that if the remaining unconverged variables are not involved in active constraints and if the objective function is not changing significantly between iterations, then the solution is more-or-less practical.
The variation in the objective function is defined as
_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_OCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\)\*XSLP\_OTOL\_R_ 
then the problem has converged on the relative static objective \(2\) convergence criterion.
The static objective function \(2\) test is applied only if `XSLP_OCOUNT`is at least 2.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_PRESOLVE_ELIMTOL, NLPPRESOLVE_ELIMTOL

_**Description:**_    Tolerance for nonlinear eliminations during SLP presolve
 
_**Type:**_ Double

_**Topic areas:**_ 
Presolve, Tolerances

_**Default value:**_ 0.001

_**Note:**_
Any eliminations on smaller coefficients will be rejected.

_**Affects routines:**_ `XSLPpresolve`
_**Category:**_ Control

#### XSLP_PRESOLVEZERO, NLPPRESOLVEZERO

_**Description:**_    Minimum absolute value for a variable which is identified as nonzero during SLP presolve
 
_**Type:**_ Double

_**Topic areas:**_ 
Presolve, Tolerances

_**Default value:**_ 1.0E-09

_**Note:**_
During the SLP \(nonlinear\)presolve, a variable may be identified as being nonzero \(for example, because it is used as a divisor\). A bound of plus or minus `XSLP_PRESOLVEZERO` will be applied to the variable if it is identified as non-negative or non-positive.

_**Affects routines:**_ `XSLPpresolve`
_**Category:**_ Control

#### XSLP_PRIMALINTEGRALALPHA, NLPPRIMALINTEGRALALPHA

_**Description:**_    Decay term for primal integral computation
 
_**Type:**_ Double

_**Topic area:**_ 
Logging

_**Default value:**_ 0

_**Note:**_
This control represents the exponential decay term for computing the `XSLP_PRIMALINTEGRAL`. The smaller it is, the more emphasis is put on the early part of the search. A value of 0 corresponds to computing a regular primal integral without exponential decay. For details see Berthold and Csizmadia: _The confined primal integral_, Mathematical Programming volume 188\(2\), pp. 523–537, 2021.
_**Category:**_ Control

#### XSLP_PRIMALINTEGRALREF, NLPPRIMALINTEGRALREF

_**Description:**_    Reference solution value to take into account when calculating the primal integral
 
_**Type:**_ Double

_**Topic area:**_ 
Logging

_**Default value:**_ XPRS\_PLUSINFINITY

_**Note:**_
When a global optimum is known, this can used to calculate a globally valid primal integral. It can also be used to indicate the target objective value still to be taken into account in the integral.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`
_**Category:**_ Control

#### XSLP_SHRINK, SLPSHRINK

_**Description:**_    Multiplier to reduce a step bound
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0.5

_**Note:**_
If step bounding is enabled, the step bound for a variable will be decreased if successive changes are in opposite directions. The step bound \( _B_ \) for the variable will be reset to
 _B\*XSLP\_SHRINK_ .
If the step bound is already below the strict \(delta or closure\) tolerances, it will not be reduced further.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_EXPAND`, `XSLP_SHRINKBIAS`, `XSLP_SAMECOUNT`

_**Category:**_ Control

#### XSLP_SHRINKBIAS, SLPSHRINKBIAS

_**Description:**_    Defines an overwrite / adjustment of step bounds for improving iterations
 
_**Type:**_ Double

_**Topic area:**_ 
SLP

_**Default value:**_ 0 \(ignored, not set\)

_**Note:**_
Positive values overwrite XSLP\_SHRINK only if the objective is improving. A negative value is used to scale all step bounds in improving iterations.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_SHRINK`, `XSLP_EXPAND`, `XSLP_SAMECOUNT`

_**Category:**_ Control

#### XSLP_STOL_A, SLPSTOL_A

_**Description:**_    Absolute slack convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The slack convergence criterion is identical to the impact convergence criterion, except that the tolerances used are `XSLP_STOL_A` \(instead of `XSLP_ITOL_A`\) and `XSLP_STOL_R` \(instead of `XSLP_ITOL_R`\). See `XSLP_ITOL_A` for a description of the test.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ITOL_A`, `XSLP_ITOL_R`, `XSLP_MTOL_A`, `XSLP_MTOL_R`, `XSLP_STOL_R`

_**Category:**_ Control

#### XSLP_STOL_R, SLPSTOL_R

_**Description:**_    Relative slack convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The slack convergence criterion is identical to the impact convergence criterion, except that the tolerances used are `XSLP_STOL_A` \(instead of `XSLP_ITOL_A`\) and `XSLP_STOL_R` \(instead of `XSLP_ITOL_R`\). See `XSLP_ITOL_R` for a description of the test.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the feasibility target `XSLP_VALIDATIONTARGET_R`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ITOL_A`, `XSLP_ITOL_R`, `XSLP_MTOL_A`, `XSLP_MTOL_R`, `XSLP_STOL_A`

_**Category:**_ Control

#### XSLP_VALIDATIONFACTOR, NLPVALIDATIONFACTOR

_**Description:**_    Minimum improvement in validation targets to continue iterating
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ 0.001

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_VALIDATIONTARGET_K` `XSLP_VALIDATIONTARGET_R`

_**Category:**_ Control

#### XSLP_VALIDATIONTARGET_R, NLPVALIDATIONTARGET_R

_**Description:**_    Feasiblity target tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ 1e-6

_**Note:**_
Primary feasiblity control for SLP. When the relevant feasibility based convergence controls are left at their default values, SLP will adjust their value to match the target. The control defines a target value, that may not necessarily be attainable.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_VALIDATIONTARGET_K`

_**Category:**_ Control

#### XSLP_VALIDATIONTARGET_K, NLPVALIDATIONTARGET_K

_**Description:**_    Optimality target tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ 1e-6

_**Note:**_
Primary optimality control for SLP. When the relevant optimality based convergence controls are left at their default values, SLP will adjust their value to match the target. The control defines a target value, that may not necessarily be attainable for problem with no strong constraint qualifications.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_VALIDATIONTARGET_R`

_**Category:**_ Control

#### XSLP_VALIDATIONTOL_A, NLPVALIDATIONTOL_A

_**Description:**_    Absolute tolerance for the XSLPvalidate procedure
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 0.00001

_**Note:**_
`XSLPvalidate` checks the feasibility of a converged solution against relative and absolute tolerances for each constraint. The left hand side and the right hand side of the constraint are calculated using the converged solution values. If the calculated values imply that the constraint is infeasible, then the difference \( _D_ \) is tested against the absolute and relative validation tolerances.
If _D<XSLP\_VALIDATIONTOL\_A_ 
then the constraint is within the absolute validation tolerance. The total positive \( _TPos_ \) and negative contributions \( _TNeg_ \) to the left hand side are also calculated.
If _D<MAX\(ABS\(TPos\), ABS\(TNeg\)\)\* XSLP\_VALIDATIONTOL\_A_ 
then the constraint is within the relative validation tolerance. For each constraint which is outside both the absolute and relative validation tolerances, validation factors are calculated which are the factors by which the infeasibility exceeds the corresponding validation tolerance; the smaller factor is printed in the validation report.
The validation index `XSLP_VALIDATIONINDEX_A`is the largest of these factors which is an absolute validation factor multiplied by the absolute validation tolerance; the validation index `XSLP_VALIDATIONINDEX_R`is the largest of these factors which is a relative validation factor multiplied by the relative validation tolerance.

_**Affects routines:**_ `XSLPvalidate`

_**See also:**_
`XSLP_VALIDATIONINDEX_A`, `XSLP_VALIDATIONINDEX_R`, `XSLP_VALIDATIONTOL_R`

_**Category:**_ Control

#### XSLP_VALIDATIONTOL_K, NLPVALIDATIONTOL_K

_**Description:**_    Relative tolerance for the XSLPvalidatekkt procedure
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, Tolerances

_**Default value:**_ 0.00001
_**Category:**_ Control

#### XSLP_VALIDATIONTOL_R, NLPVALIDATIONTOL_R

_**Description:**_    Relative tolerance for the XSLPvalidate procedure
 
_**Type:**_ Double

_**Topic area:**_ 
Tolerances

_**Default value:**_ 0.00001

_**Note:**_
`XSLPvalidate` checks the feasibility of a converged solution against relative and absolute tolerances for each constraint. The left hand side and the right hand side of the constraint are calculated using the converged solution values. If the calculated values imply that the constraint is infeasible, then the difference \( _D_ \) is tested against the absolute and relative validation tolerances.
If _D<XSLP\_VALIDATIONTOL\_A_ 
then the constraint is within the absolute validation tolerance. The total positive \( _TPos_ \) and negative contributions \( _TNeg_ \) to the left hand side are also calculated.
If _D<MAX\(ABS\(TPos\), ABS\(TNeg\)\)\* XSLP\_VALIDATIONTOL\_R_ 
then the constraint is within the relative validation tolerance. For each constraint which is outside both the absolute and relative validation tolerances, validation factors are calculated which are the factors by which the infeasibility exceeds the corresponding validation tolerance; the smaller factor is printed in the validation report.
The validation index `XSLP_VALIDATIONINDEX_A`is the largest of these factors which is an absolute validation factor multiplied by the absolute validation tolerance; the validation index `XSLP_VALIDATIONINDEX_R`is the largest of these factors which is a relative validation factor multiplied by the relative validation tolerance.

_**Affects routines:**_ `XSLPvalidate`

_**See also:**_
`XSLP_VALIDATIONINDEX_A`, `XSLP_VALIDATIONINDEX_R`, `XSLP_VALIDATIONTOL_A`

_**Category:**_ Control

#### XSLP_VTOL_A, SLPVTOL_A

_**Description:**_    Absolute static objective \(3\) convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The static objective \(3\) convergence criterion does not measure convergence of individual variables, and in fact does not in any way imply that the solution has converged. However, it is sometimes useful to be able to terminate an optimization once the objective function appears to have stabilized. One example is where a set of possible schedules are being evaluated and initially only a good estimate of the likely objective function value is required, to eliminate the worst candidates.
The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_ VCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤XSLP\_VTOL\_A_ 
then the problem has converged on the absolute static objective function \(3\) criterion.
The static objective function \(3\) test is applied only if after at least `XSLP_VLIMIT`+ `XSLP_SBSTART`SLP iterations have taken place and only if `XSLP_VCOUNT`is at least 2. Where step bounding is being used, this ensures that the test is not applied until after step bounding has been introduced.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SBSTART`, `XSLP_VCOUNT`, `XSLP_VLIMIT`, `XSLP_VTOL_R`

_**Category:**_ Control

#### XSLP_VTOL_R, SLPVTOL_R

_**Description:**_    Relative static objective \(3\) convergence tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_
The static objective \(3\) convergence criterion does not measure convergence of individual variables, and in fact does not in any way imply that the solution has converged. However, it is sometimes useful to be able to terminate an optimization once the objective function appears to have stabilized. One example is where a set of possible schedules are being evaluated and initially only a good estimate of the likely objective function value is required, to eliminate the worst candidates.
The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_ VCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_VTOL\_R_ 
then the problem has converged on the absolute static objective function \(3\) criterion.
The static objective function \(3\) test is applied only if after at least `XSLP_VLIMIT`+ `XSLP_SBSTART`SLP iterations have taken place and only if `XSLP_VCOUNT`is at least 2. Where step bounding is being used, this ensures that the test is not applied until after step bounding has been introduced.
When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SBSTART`, `XSLP_VCOUNT`, `XSLP_VLIMIT`, `XSLP_VTOL_A`

_**Category:**_ Control

#### XSLP_WTOL_A, SLPWTOL_A

_**Description:**_    Absolute extended convergence continuation tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration.

The extended convergence continuation criterion is applied after a converged solution has been found where at least one variable has converged on extended criteria and is at its step bound limit. The extended convergence continuation test measures whether any improvement is being achieved when additional SLP iterations are carried out. If not, then the last converged solution will be restored and the optimization will stop.
For a maximization problem, the improvement in the objective function at the current iteration compared to the objective function at the last converged solution is given by:
 _δObj = Obj - LastConvergedObj_ 
For a minimization problem, the sign is reversed.
If _δObj>XSLP\_WTOL\_A_ and
 _δObj>ABS\(ConvergedObj\) \* XSLP\_WTOL\_R_ then the solution is deemed to have a significantly better objective function value than the converged solution.

When a solution is found which converges on extended criteria and with active step bounds, the solution is saved and SLP optimization continues until one of the following:
\(1\) a new solution is found which converges on some other criterion, in which case the SLP optimization stops with this new solution;
\(2\) a new solution is found which converges on extended criteria and with active step bounds, and which has a significantly better objective function, in which case this is taken as the new saved solution;
\(3\) none of the `XSLP_WCOUNT`most recent SLP iterations has a significantly better objective function than the saved solution, in which case the saved solution is restored and the SLP optimization stops.

When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_WCOUNT`, `XSLP_WTOL_R`

_**Category:**_ Control

#### XSLP_WTOL_R, SLPWTOL_R

_**Description:**_    Relative extended convergence continuation tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration.

The extended convergence continuation criterion is applied after a converged solution has been found where at least one variable has converged on extended criteria and is at its step bound limit. The extended convergence continuation test measures whether any improvement is being achieved when additional SLP iterations are carried out. If not, then the last converged solution will be restored and the optimization will stop.
For a maximization problem, the improvement in the objective function at the current iteration compared to the objective function at the last converged solution is given by:
 _δObj = Obj - LastConvergedObj_ 
For a minimization problem, the sign is reversed.
If _δObj>XSLP\_WTOL\_A_ and
 _δObj>ABS\(ConvergedObj\) \* XSLP\_WTOL\_R_ then the solution is deemed to have a significantly better objective function value than the converged solution.

If `XSLP_WCOUNT` is greater than zero, and a solution is found which converges on extended criteria and with active step bounds, the solution is saved and SLP optimization continues until one of the following:
\(1\) a new solution is found which converges on some other criterion, in which case the SLP optimization stops with this new solution;
\(2\) a new solution is found which converges on extended criteria and with active step bounds, and which has a significantly better objective function, in which case this is taken as the new saved solution;
\(3\) none of the `XSLP_WCOUNT`most recent SLP iterations has a significantly better objective function than the saved solution, in which case the saved solution is restored and the SLP optimization stops.

When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-4 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_WCOUNT`, `XSLP_WTOL_A`

_**Category:**_ Control

#### XSLP_XTOL_A, SLPXTOL_A

_**Description:**_    Absolute static objective function \(1\) tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration. However, if the objective function has already been stable for several SLP iterations, then there is less likelihood of an improved result, and the converged solution can be accepted.

The static objective function \(1\) test measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. Because all the variables have converged, the solution is already converged but the fact that some variables are at their step bound limit suggests that the objective function could be improved by going further.

The variation in the objective function is defined as
 _δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_ 
where _Iter_ is the `XSLP_XCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.

If _ABS\(δObj\)≤XSLP\_XTOL\_A_ 
then the objective function is deemed to be static according to the absolute static objective function \(1\) criterion.
If _ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_XTOL\_R_ 
then the objective function is deemed to be static according to the relative static objective function \(1\) criterion.

The static objective function \(1\) test is applied only until `XSLP_XLIMIT` SLP iterations have taken place. After that, if all the variables have converged on strict or extended criteria, the solution is deemed to have converged.

If the objective function passes the relative or absolute static objective function \(1\) test then the solution is deemed to have converged.

When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-3 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_XCOUNT`, `XSLP_XLIMIT`, `XSLP_XTOL_R`

_**Category:**_ Control

#### XSLP_XTOL_R, SLPXTOL_R

_**Description:**_    Relative static objective function \(1\) tolerance
 
_**Type:**_ Double

_**Topic areas:**_ 
SLP, SLP-convergence, Tolerances

_**Default value:**_ -1.0

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration. However, if the objective function has already been stable for several SLP iterations, then there is less likelihood of an improved result, and the converged solution can be accepted.

The static objective function \(1\) test measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. Because all the variables have converged, the solution is already converged but the fact that some variables are at their step bound limit suggests that the objective function could be improved by going further.

The variation in the objective function is defined as
 _δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_ 
where _Iter_ is the `XSLP_XCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.

If _ABS\(δObj\)≤XSLP\_XTOL\_A_ 
then the objective function is deemed to be static according to the absolute static objective function \(1\) criterion.
If _ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_XTOL\_R_ 
then the objective function is deemed to be static according to the relative static objective function \(1\) criterion.

The static objective function \(1\) test is applied only until `XSLP_XLIMIT` SLP iterations have taken place. After that, if all the variables have converged on strict or extended criteria, the solution is deemed to have converged.

If the objective function passes the relative or absolute static objective function \(1\) test then the solution is deemed to have converged.

When the value is set to be negative, the value is adjusted automatically by SLP, based on the optimality target `XSLP_VALIDATIONTARGET_K`. Good values for the control are usually fall between 1e-4 and 1e-6.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_XCOUNT`, `XSLP_XLIMIT`, `XSLP_XTOL_A`

_**Category:**_ Control

#### XSLP_ZERO, NLPZERO

_**Description:**_    Absolute tolerance
 
_**Type:**_ Double

_**Topic area:**_ 
Tolerances

_**Default value:**_ 1.0E-15

_**Note:**_
If a value is below `XSLP_ZERO` in magnitude, then it will be regarded as zero in certain formula calculations:
an attempt to divide by such a value will give a "divide by zero" error;
an exponent of a negative number will produce a "negative number, fractional exponent" error if the exponent differs from an integer by more than `XSLP_ZERO`.

_**Affects routines:**_ `XSLPevaluatecoef`,`XSLPevaluateformula`
_**Category:**_ Control

#### Section 20.2 Integer control parameters


#### XSLP_ALGORITHM, SLPALGORITHM

_**Description:**_    Bit map describing the SLP algorithm\(s\) to be used
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Do not apply step bounds.
 `1`| Apply step bounds to SLP delta vectors only when required.
 `2`| Estimate step bounds from early SLP iterations.
 `3`| Use dynamic damping.
 `4`| Do not update values which are converged within strict tolerance.
 `5`| Retain previous value when cascading if determining row is zero.
 `6`| Reset XSLP\_DELTA\_Z to zero when converged and continue SLP.
 `7`| Quick convergence check.
 `8`| Escalate penalties.
 `9`| Use the primal simplex algorithm when all error vectors become inactive.
 `11`| Continue optimizing after penalty cost reaches maximum.
 `12`| Accept a solution which has converged even if there are still significant active penalty error vectors.
 `13`| Skip the solution polishing step if the LP postsolve returns a slightly infeasible, but claimed optimal solution.
 `14`| Step bounds are updated to accomodate cascaded values \(otherwise cascaded values are pushed to respect step bounds\).
 `15`| Apply clamping when converged on extended criteria only with some variables having active step bounds.
 `16`| Apply clamping when converged on extended criteria only.

_**Default value:**_ 166 \(sets bits 1, 2, 5, 7\)

_**Notes:**_

`Bit 0:` Do not apply step bounds. The default algorithm uses step bounds to force convergence. Step bounds may not be appropriate if dynamic damping is used.

`Bit 1:` Apply step bounds to SLP delta vectors only when required. Step bounds can be applied to all vectors simultaneously, or applied only when oscillation of the delta vector \(change in sign between successive SLP iterations\) is detected.

`Bit 2:` Estimate step bounds from early SLP iterations. If initial step bounds are not being explicitly provided, this gives a good method of calculating reasonable values. Values will tend to be larger rather than smaller, to reduce the risk of infeasibility caused by excessive tightness of the step bounds.

`Bit 3:` Use dynamic damping. Dynamic damping is sometimes an alternative to step bounding as a means of encouraging convergence, but it does not have the same power to force convergence as do step bounds.

`Bit 4:` Do not update values which are converged within strict tolerance. Models which are numerically unstable may benefit from this setting, which does not update values which have effectively hardly changed. If a variable subsequently does move outside its strict convergence tolerance, it will be updated as usual.

`Bit 5:` Retain previous value when cascading if determining row is zero. If the determining row is zero \(that is, all the coefficients interacting with it are either zero or in columns with a zero activity\), then it is impossible to calculate a new value for the vector being cascaded. The choice is to use the solution value as it is, or to revert to the assumed value

`Bit 6:` Reset `XSLP_DELTA_Z` to zero when converged and continue SLP. One of the mechanisms to avoid local optima is to retain small non-zero coefficients between delta vectors and constraints, even when the coefficient should strictly be zero. If this option is set, then a converged solution will be continued with zero coefficients as appropriate.

`Bit 7:` Quick convergence check. Normally, each variable is checked against all convergence criteria until either a criterion is found which it passes, or it is declared "not converged". Later \(extended convergence\) criteria are more expensive to test and, once an unconverged variable has been found, the overall convergence status of the solution has been established. The quick convergence check carries out checks on the strict criteria, but omits checks on the extended criteria when an unconverged variable has been found.

`Bit 8:` Escalate penalties. Constraint penalties are increased after each SLP iteration where penalty vectors are present in the solution. Escalation applies an additional scaling factor to the penalty costs for active errors. This helps to prevent successive solutions becoming "stuck" because of a particular constraint, because its cost will be raised so that other constraints may become more attractive to violate instead and thus open up a new region to explore.

`Bit 9:` Use the primal simplex algorithm when all error vectors become inactive. The primal simplex algorithm often performs better than dual during the final stages of SLP optimization when there are relatively few basis changes between successive solutions. As it is impossible to establish in advance when the final stages are being reached, the disappearance of error vectors from the solution is used as a proxy.

`Bit 11:` Continue optimizing after penalty cost reaches maximum. Normally if the penalty cost reaches its maximum \(by default the value of `XPRS_PLUSINFINITY`\), the optimization will terminate with an unconverged solution. If the maximum value is set to a smaller value, then it may make sense to continue, using other means to determine when to stop.

`Bit 12:` Accept a solution which has converged even if there are still significant active penalty error vectors. Normally, the optimization will continue if there are active penalty vectors in the solution. However, it may be that there is no feasible solution \(and so active penalties will always be present\). Setting bit 12 means that, if other convergence criteria are met, then the solution will be accepted as converged and the optimization will stop.

`Bit 13:` Due to the nature of the SLP linearizations, and in particular because of the large differences in the objective function \(model objective against penalty costs\) some dual reductions in the linear presolver might introduce numerically instable reductions that cause slight infeasibilities to appear in postsolve. It is typically more efficient to remove these infeasibilities with an extra call to the linear optimizer; compared to switching these reductions off, which usually has a significant cost in performance. This bit is provided for numerically very hard problems, when the polishing step proves to be too expensive \(XSLP will report these if any in the final log summary\).

`Bit 14:` Normally, cascading will respect the step bounds of the SLP variable being cascaded. However, allowing the cascaded value to fall outside the step bounds \(i.e. expanding the step bounds\) can lead to better linearizations, as cascading will set better values for the SLP variables regarding their determining rows; note, that this later strategy might interfere with convergence of the cascaded variables.

`Bit 15:` When clamping is applied, then in any iteration when the solution would normally be deemed converged on extended criteria only, an extra step bound shrinking step is applied to help imposing strict convergence. In this variant, clamping is only applied on variables that have converged on extended criteria only and have active step bounds.

`Bit 16:` When clamping is applied, then in any iteration when the solution would normally be deemed converged on extended criteria only, an extra step bound shrinking step is applied to help imposing strict convergence. In this variant, clamping is applied on all variables that have converged on extended criteria only.

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_NOSTEPBOUNDS` | 
Setting bit 1 | `XSLP_STEPBOUNDSASREQUIRED` | 
Setting bit 2 | `XSLP_ESTIMATESTEPBOUNDS` | 
Setting bit 3 | `XSLP_DYNAMICDAMPING` | 
Setting bit 4 | `XSLP_HOLDVALUES` | 
Setting bit 5 | `XSLP_RETAINPREVIOUSVALUE` | 
Setting bit 6 | `XSLP_RESETDELTAZ` | 
Setting bit 7 | `XSLP_QUICKCONVERGENCECHECK` | 
Setting bit 8 | `XSLP_ESCALATEPENALTIES` | 
Setting bit 9 | `XSLP_SWITCHTOPRIMAL` | 
Setting bit 11 | `XSLP_MAXCOSTOPTION` | 
Setting bit 12 | `XSLP_RESIDUALERRORS` | 
Setting bit 13 | `XSLP_NOLPPOLISHING` | 
Setting bit 14 | `XSLP_CASCADEDBOUNDS` | 
Setting bit 15 | `XSLP_CLAMPEXTENDEDACTIVESB` | 
Setting bit 16 | `XSLP_CLAMPEXTENDEDALL` | 


Recommended setting: Bits 1, 2, 5, 7 and usually bits 8 and 9.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTA_Z`, `XSLP_ERRORMAXCOST`, `XSLP_ESCALATION`, `XSLP_CLAMPSHRINK`

_**Category:**_ Control

#### XSLP_ANALYZE, SLPANALYZE

_**Description:**_    Bit map activating additional options supporting model / solution path analysis
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Bit-vector, Logging

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `3`| Include an extended iteration summary.
 `4`| Run infeasibility analysis on infeasible iterations.
 `6`| Write the linearizations to disk at every XSLP\_AUTOSAVE iterations.
 `7`| Write the initial basis of the linearizations to disk at every XSLP\_AUTOSAVE iterations.
 `8`| Create an XSLP save file at every XSLP\_AUTOSAVE iterations.

_**Default value:**_ 0

_**Note:**_
In most cases, the value of this control does not affect the solution process itself. However, bit 3 \(extended summary\) will cause SLP to do more function evaluations, and the presence of non-deterministic user functions might cause changes in the solution process. These options are off by default due to performance considerations.
The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 3 | `XSLP_ANALYZE_EXTENDEDFINALSUMMARY` | 
Setting bit 4 | `XSLP_ANALYZE_INFEASIBLE_ITERATION` | 
Setting bit 6 | `XSLP_ANALYZE_SAVELINEARIZATIONS` | 
Setting bit 7 | `XSLP_ANALYZE_SAVEITERBASIS` | 
Setting bit 8 | `XSLP_ANALYZE_SAVEFILE` | 



_**See also:**_
`XSLP_AUTOSAVE`

_**Category:**_ Control

#### XSLP_AUGMENTATION, SLPAUGMENTATION

_**Description:**_    Bit map describing the SLP augmentation method\(s\) to be used
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Minimum augmentation.
 `1`| Even handed augmentation.
 `2`| Penalty error vectors on all non-linear equality constraints.
 `3`| Penalty error vectors on all non-linear inequality constraints.
 `4`| Penalty vectors to exceed step bounds.
 `5`| Use arithmetic means to estimate penalty weights.
 `6`| Estimate step bounds from values of row coefficients.
 `7`| Estimate step bounds from absolute values of row coefficients.
 `8`| Row-based step bounds.
 `9`| Penalty error vectors on all constraints.
 `10`| Intial values do not imply an SLP variable.
 `12`| Avoid running an LP around fixed initial values trying to get feasible.

_**Default value:**_ 12 \(sets bits 2 and 3\)

_**Notes:**_

`Bit 0`: Minimum augmentation. Standard augmentation includes delta vectors for all variables involved in nonlinear terms \(in non-constant coefficients or as vectors containing non-constant coefficients\). Minimum augmentation includes delta vectors only for variables in non-constant coefficients. This produces a smaller linearization, but there is less control on convergence, because convergence control \(for example, step bounding\) cannot be applied to variables without deltas.

`Bit 1`: Even handed augmentation. Standard augmentation treats variables which appear in non-constant coefficients in a different way from those which contain non-constant coefficients. Even-handed augmentation treats them all in the same way by replacing each non-constant coefficient _C_  in a vector _V_  by a new coefficient _C*V_  in the "equals" column \(which has a fixed activity of 1\) and creating delta vectors for all types of variable in the same way.

`Bit 2`: Penalty error vectors on all non-linear equality constraints. The linearization of a nonlinear equality constraint is inevitably an approximation and so will not generally be feasible except at the point of linearization. Adding penalty error vectors allows the linear approximation to be violated at a cost and so ensures that the linearized constraint is feasible.

`Bit 3`: Penalty error vectors on all non-linear inequality constraints. The linearization of a nonlinear constraint is inevitably an approximation and so may not be feasible except at the point of linearization. Adding penalty error vectors allows the linear approximation to be violated at a cost and so ensures that the linearized constraint is feasible.

`Bit 4`: Penalty vectors to exceed step bounds. Although it has rarely been found necessary or desirable in practice, Xpress-SLP allows step bounds to be violated at a cost. This may help with feasibility but it generally slows down or prevents convergence, so it should be used only if found absolutely necessary.

`Bit 5`: Use arithmetic means to estimate penalty weights. Penalty weights are estimated from the magnitude of the elements in the constraint or interacting rows. Geometric means are normally used, so that a few excessively large or small values do not distort the weights significantly. Arithmetic means will value the coefficients more equally.

`Bit 6`: Estimate step bounds from values of row coefficients. If step bounds are to be imposed from the start, the best approach is to provide explicit values for the bounds. Alternatively, Xpress-SLP can estimate the values from the range of estimated coefficient sizes in the relevant rows.

`Bit 7`: Estimate step bounds from absolute values of row coefficients. If step bounds are to be imposed from the start, the best approach is to provide explicit values for the bounds. Alternatively, Xpress-SLP can estimate the values from the largest estimated magnitude of the coefficients in the relevant rows.

`Bit 8`: Row-based step bounds. Step bounds are normally applied as bounds on the delta variables. Some applications may find that using explicit rows to bound the delta vectors gives better results.

`Bit 9`: Penalty error vectors on all constraints. If the linear portion of the underlying model may actually be infeasible, then applying penalty vectors to all rows may allow identification of the infeasibility and may also allow a useful solution to be found.

`Bit 10`: Having an initial value will not cause the augmentation to include the corresponding delta variable; i.e. treat the variable as an SLP variable. Useful to provide initial values necessary in the first linearization in case of a minimal augmentation, or as a convenience option when it's easiest to set an initial value for all variables for some reason.

`Bit 12`: Unless this bit is set, if almost all variables have initial values, an LP can be solved with all variables with initial values fixed to those, to try to extend the partial initial solution to a feasible solution.

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_MINIMUMAUGMENTATION` | 
Setting bit 1 | `XSLP_EVENHANDEDAUGMENTATION` | 
Setting bit 2 | `XSLP_EQUALITYERRORVECTORS` | 
Setting bit 3 | `XSLP_ALLERRORVECTORS` | 
Setting bit 4 | `XSLP_PENALTYDELTAVECTORS` | 
Setting bit 5 | `XSLP_AMEANWEIGHT` | 
Setting bit 6 | `XSLP_SBFROMVALUES` | 
Setting bit 7 | `XSLP_SBFROMABSVALUES` | 
Setting bit 8 | `XSLP_STEPBOUNDROWS` | 
Setting bit 9 | `XSLP_ALLROWERRORVECTORS` | 
Setting bit 10 | `XSLP_NOUPDATEIFONLYIV` | 
Setting bit 12 | `XSLP_SKIPIVLPHEURISTICS` | 


The recommended setting is bits 2 and 3 \(penalty vectors on all nonlinear constraints\).


_**Affects routines:**_ `XSLPconstruct`
_**Category:**_ Control

#### XSLP_AUTOSAVE, SLPAUTOSAVE

_**Description:**_    Frequency with which to save the model
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 0

_**Note:**_
A value of zero means that the model will not automatically be saved. A positive value of `n` will save model information at every `n` th SLP iteration as requested by XSLP\_ANALYZE.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ANALYZE`

_**Category:**_ Control

#### XSLP_BARCROSSOVERSTART, SLPBARCROSSOVERSTART

_**Description:**_    Default crossover activation behaviour for barrier start
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations

_**Default value:**_ 0

_**Note:**_
When `XSLP_BARLIMIT` is set, `XSLP_BARCROSSOVERSTART` offers an overwrite control on when crossover is applied. A positive value indicates that crossover should be disabled in iterations smaller than `XSLP_BARCROSSOVERSTART` and should be enabled afterwards, or when stalling is detected as described in `XSLP_BARSTARTOPS`. A value of 0 indicates to respect the value of `XPRS_CROSSOVER` and only overwrite its value when stalling is detected. A value of -1 indicates to always rely on the value of `XPRS_CROSSOVER`.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_BARLIMIT`, `XSLP_BARSTARTOPS`, `XSLP_BARSTALLINGLIMIT`, `XSLP_BARSTALLINGOBJLIMIT`, `XSLP_BARSTALLINGTOL`

_**Category:**_ Control

#### XSLP_BARLIMIT, SLPBARLIMIT

_**Description:**_    Number of initial SLP iterations using the barrier method
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations, Limits

_**Default value:**_ 0

_**Note:**_
Particularly for larger models, using the Newton barrier method is faster in the earlier SLP iterations. Later on, when the basis information becomes more useful, a simplex method generally performs better. `XSLP_BARLIMIT` sets the number of SLP iterations which will be performed using the Newton barrier method.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_BARCROSSOVERSTART`, `XSLP_BARSTARTOPS`, `XSLP_BARSTALLINGLIMIT`, `XSLP_BARSTALLINGOBJLIMIT`, `XSLP_BARSTALLINGTOL`

_**Category:**_ Control

#### XSLP_BARSTALLINGLIMIT, SLPBARSTALLINGLIMIT

_**Description:**_    Number of iterations to allow numerical failures in barrier before switching to dual
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations, Limits

_**Default value:**_ 3

_**Note:**_
On large problems, it may be beneficial to warm start progress by running a number of iterations with the barrier solver as specified by `XSLP_BARLIMIT`. On some numerically difficult problems, the barrier may stop prematurely due to numerical issues. Such solves can sometimes be finished if crossover is applied. After `XSLP_BARSTALLINGLIMIT` such attempts, SLP will automatically switch to use the dual simplex.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_BARCROSSOVERSTART`, `XSLP_BARLIMIT`, `XSLP_BARSTARTOPS`, `XSLP_BARSTALLINGOBJLIMIT`, `XSLP_BARSTALLINGTOL`

_**Category:**_ Control

#### XSLP_BARSTALLINGOBJLIMIT, SLPBARSTALLINGOBJLIMIT

_**Description:**_    Number of iterations over which to measure the objective change for barrier iterations with no crossover
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations, Limits

_**Default value:**_ 3

_**Note:**_
On large problems, it may be beneficial to warm start progress by running a number of iterations with the barrier solver without crossover by setting `XSLP_BARLIMIT` to a positive value and setting `XPRS_CROSSOVER` to 0. A potential drawback is slower convergence due to the interior point provided by the barrier solve keeping a higher number of variables active. This may lead to stalling in progress, negating the benefit of using the barrier. When in the last `XSLP_BARSTALLINGOBJLIMIT` iterations no significant progress has been made, crossover is automatically enabled.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_BARCROSSOVERSTART`, `XSLP_BARLIMIT`, `XSLP_BARSTARTOPS`, `XSLP_BARSTALLINGLIMIT`, `XSLP_BARSTALLINGTOL`

_**Category:**_ Control

#### XSLP_BARSTARTOPS, SLPBARSTARTOPS

_**Description:**_    Controls behaviour when the barrier is used to solve the linearizations
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Check objective progress when no crossover is applied.
 `1`| Fall back to dual simplex if too many numerical problems are reported by the barrier.
 `2`| If a non-vertex converged solution found by barrier without crossover can be returned as a final solution.

_**Default value:**_ -1

_**Note:**_

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `BARSTARTOPS_STALLING_OBJECTIVE` | 
Setting bit 1 | `BARSTARTOPS_STALLING_NUMERICAL` | 
Setting bit 2 | `BARSTARTOPS_ALLOWINTERIORSOLUTION` | 



_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_BARCROSSOVERSTART`, `XSLP_BARLIMIT`, `XSLP_BARSTALLINGLIMIT`, `XSLP_BARSTALLINGOBJLIMIT`, `XSLP_BARSTALLINGTOL`

_**Category:**_ Control

#### XSLP_CALCTHREADS, NLPCALCTHREADS

_**Description:**_    Number of threads used for formula and derivatives evaluations
 
_**Type:**_ Integer

_**Topic area:**_ 
Parallel

_**Default value:**_ -1 \(determined by XSLP\_THREADS\)

_**Note:**_
When beneficial, SLP can calculate formula values and partial derivative information in parallel.

_**Affects routines:**_ `XSLPmaxim`,`XSLPmaxim`

_**See also:**_
`XSLP_THREADS`,

_**Category:**_ Control

#### XSLP_CASCADE, SLPCASCADE

_**Description:**_    Bit map describing the cascading to be used
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Cascading

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Apply cascading to all variables with determining rows.
 `1`| Apply cascading to SLP variables which appear in coefficients and which would change by more than `XPRS_FEASTOL`.
 `2`| Apply cascading to all SLP variables which appear in coefficients.
 `3`| Apply cascading to SLP variables which are structural and which would change by more than `XPRS_FEASTOL`.
 `4`| Apply cascading to all SLP variables which are structural.
 `5`| Create secondary order groupping DR rows with instantiated user functions together in the order.
 `6`| In cases where the determining column is below `XSLP_DRCOLTOL`, fix at the previous rather than current value.
 `7`| In cases where the determining column is below `XSLP_DRCOLTOL`, fix within a range `XSLP_DRFIXRANGE`of previous value.
 `8`| Automatically determine whether to apply cascading.

_**Default value:**_ 257

_**Note:**_
Normal cascading \(bit 0\) uses determining rows to recalculate the values of variables to be consistent with values already available or already recalculated.
Other bit settings are normally required only in quadratic programming where some of the SLP variables are in the objective function. The values of such variables may need to be corrected if the corresponding update row is slightly infeasible.
The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_CASCADE_ALL` | 
Setting bit 1 | `XSLP_CASCADE_COEF_VAR` | 
Setting bit 2 | `XSLP_CASCADE_ALL_COEF_VAR` | 
Setting bit 3 | `XSLP_CASCADE_STRUCT_VAR` | 
Setting bit 4 | `XSLP_CASCADE_ALL_STRUCT_VAR` | 
Setting bit 5 | `XSLP_CASCADE_SECONDARY_GROUPS` | 
Setting bit 6 | `XSLP_CASCADE_DRCOL_PREVOUSVALUE` | 
Setting bit 7 | `XSLP_CASCADE_DRCOL_PVRANGE` | 
Setting bit 8 | `XSLP_CASCADE_AUTOAPPLY` | 



_**Affects routines:**_ `XSLPcascade`

_**See also:**_
`XSLP_DRCOLTOL`, `XSLP_DRFIXRANGE`

_**Category:**_ Control

#### XSLP_CASCADENLIMIT, SLPCASCADENLIMIT

_**Description:**_    Maximum number of iterations for cascading with non-linear determining rows
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Cascading, Limits

_**Default value:**_ 10

_**Note:**_
Re-calculation of the value of a variable uses a modification of the Newton-Raphson method. The maximum number of steps in the method is set by `XSLP_ CASCADE NLIMIT`. If the maximum number of steps is taken without reaching a converged value, the best value found will be used.

_**Affects routines:**_ `XSLPcascade`

_**See also:**_
`XSLP_CASCADE`

_**Category:**_ Control

#### XSLP_CONTROL

_**Description:**_    Bit map describing which Xpress NonLinear functions also activate the corresponding Optimizer Library function
 
_**Type:**_ Integer

_**Topic areas:**_ 
Bit-vector, Misc

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Xpress NonLinear problem management functions do NOT invoke the corresponding Optimizer Library function for the underlying linear problem.
 `1`| `XSLPcopycontrols`does NOT invoke `XPRScopycontrols`.
 `2`| `XSLPcopycallbacks`does NOT invoke `XPRScopycallbacks`.
 `3`| `XSLPcopyprob`does NOT invoke `XPRScopyprob`.
 `4`| `XSLPsetdefaults`does NOT invoke `XPRSsetdefaults`.
 `5`| `XSLPsave`does NOT invoke `XPRSsave`.
 `6`| `XSLPrestore`does NOT invoke `XPRSrestore`.

_**Default value:**_ 0 \(no bits set\)

_**Note:**_
The problem management functions are:
 `XSLPcopyprob`to copy from an existing problem;
 `XSLPcopycontrols`and `XSLPcopycallbacks`to copy the current controls and callbacks from an existing problem;
 `XSLPsetdefaults`to reset the controls to their default values;
 `XSLPsave`and `XSLPrestore`for saving and restoring a problem.

_**Affects routines:**_ `XSLPcopycontrols`,`XSLPcopycallbacks`,`XSLPcopyprob`,`XSLPrestore`,`XSLPsave`,`XSLPsetdefaults`
_**Category:**_ Control

#### XSLP_CONVERGENCEOPS, SLPCONVERGENCEOPS

_**Description:**_    Bit map describing which convergence tests should be carried out
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Execute the closure tolerance checks.
 `1`| Execute the delta tolerance checks.
 `2`| Execute the matrix tolerance checks.
 `3`| Execute the impact tolerance checks.
 `4`| Execute the slack impact tolerance checks.
 `5`| Check for user provided convergence.
 `6`| Execute the objective range checks.
 `7`| Execute the objective range + constraint activity check.
 `8`| Execute the objective range + active step bound check.
 `9`| Execute the convergence continuation check.
 `10`| Take scaling of individual variables / rows into account.
 `11`| Execute the validation target convergence checks.
 `12`| Execute the first order optimality target convergence checks.
 `13`| Allow convex quadratic problems to converge on extended criteria.
 `15`| Do not declare converged if still sufficient improvement in objective.

_**Default value:**_ 39935 \(bits 0-9, 11-12, and 15 are set\)

_**Note:**_
Provides fine tuned control \(over setting the related convergence tolerances\) of which convergence checks are carried out.
The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_CONVERGEBIT_CTOL` | 
Setting bit 1 | `XSLP_CONVERGEBIT_ATOL` | 
Setting bit 2 | `XSLP_CONVERGEBIT_MTOL` | 
Setting bit 3 | `XSLP_CONVERGEBIT_ITOL` | 
Setting bit 4 | `XSLP_CONVERGEBIT_STOL` | 
Setting bit 5 | `XSLP_CONVERGEBIT_USER` | 
Setting bit 6 | `XSLP_CONVERGEBIT_VTOL` | 
Setting bit 7 | `XSLP_CONVERGEBIT_XTOL` | 
Setting bit 8 | `XSLP_CONVERGEBIT_OTOL` | 
Setting bit 9 | `XSLP_CONVERGEBIT_WTOL` | 
Setting bit 10 | `XSLP_CONVERGEBIT_EXTENDEDSCALING` | 
Setting bit 11 | `XSLP_CONVERGEBIT_VALIDATION` | 
Setting bit 12 | `XSLP_CONVERGEBIT_VALIDATION_K` | 
Setting bit 13 | `XSLP_CONVERGEBIT_NOQUADCHECK` | 
Setting bit 15 | `XSLP_CONVERGEBIT_REQUIRE_OTOL_R` | 



_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_CUTSTRATEGY, SLPCUTSTRATEGY

_**Description:**_    Determines whihc cuts to apply in the MISLP search when the default SLP-in-MIP strategy is used.
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Cuts

_**Default value:**_ 0

_**Note:**_
Cuts are derived from the linearizations and are local cuts in that they are valid in the linearization and not necessarily valid for the full problem. The values mirror that of XPRS\_CUTSTRATEGY.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`
_**Category:**_ Control

#### XSLP_DAMPSTART, SLPDAMPSTART

_**Description:**_    SLP iteration at which damping is activated
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 0

_**Note:**_
If damping is used as part of the SLP algorithm, it can be delayed until a specified SLP iteration. This may be appropriate when damping is used to encourage convergence after an un-damped algorithm has failed to converge.

_**Affects routines:**_ `XSLPmaxim`,`XSLPmaxim`

_**See also:**_
`XSLP_ALGORITHM`, `XSLP_DAMPEXPAND`, `XSLP_DAMPMAX`, `XSLP_DAMPMIN`, `XSLP_DAMPSHRINK`

_**Category:**_ Control

#### XSLP_DELAYUPDATEROWS, SLPDELAYUPDATEROWS

_**Description:**_    Number of SLP iterations before update rows are fully activated
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 2

_**Note:**_
During augmentation, one or more delta vectors are created for each SLP variable. The values of these are linked to that of the variable through an _update row_ which is created as part of the augmentation procedure.

_**Affects routines:**_ `XSLPmaxim`,`XSLPmaxim`
_**Category:**_ Control

#### XSLP_DELTAOFFSET, SLPDELTAOFFSET

_**Description:**_    Position of first character of SLP variable name used to create name of delta vector
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 0

_**Note:**_
During augmentation, a delta vector, and possibly penalty delta vectors, are created for each SLP variable. They are created with names derived from the corresponding SLP variable. Customized naming is possible using `XSLP_DELTAFORMAT` etc to define a format and `XSLP_DELTAOFFSET` to define the first character \(counting from zero\) of the variable name to be used.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_DELTAFORMAT`, `XSLP_MINUSDELTAFORMAT`, `XSLP_PLUSDELTAFORMAT`

_**Category:**_ Control

#### XSLP_DELTAZLIMIT, SLPDELTAZLIMIT

_**Description:**_    Number of SLP iterations during which to apply XSLP\_DELTA\_Z
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 0

_**Note:**_
`XSLP_DELTA_Z` is used to retain small derivatives which would otherwise be regarded as zero. This is helpful in avoiding local optima, but may make the linearized problem more difficult to solve because of the number of small nonzero elements in the resulting matrix. `XSLP_DELTAZLIMIT` can be set to a nonzero value, which is then the number of iterations for which `XSLP_DELTA_Z` will be used. After that, small derivatives will be set to zero. A negative value indicates no automatic perturbations to the derivatives in any situation.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_DELTA_Z`

_**Category:**_ Control

#### XSLP_DERIVATIVES, NLPDERIVATIVES

_**Description:**_    Bitmap describing the method of calculating derivatives
 
_**Type:**_ Integer

_**Topic area:**_ 
Derivatives

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| analytic derivatives where possible
 `1`| avoid embedding numerical derivatives of instantiated functions into analytic derivatives

_**Default value:**_ 1

_**Notes:**_
If no bits are set then numerical derivatives are calculated using finite differences.
Analytic derivatives cannot be used for formulae involving discontinuous functions. They may not work well with functions which are not smooth \(such as `MAX`\), or where the derivative changes very quickly with the value of the variable \(such as `LOG10`of small values\).
Both first and second order analytic derivatives can either be calculated as symbolic formulas, or by the means of auto-differentiation, with the exception that the second order symbolic derivatives require that the first order derivatives are also calculated using the symbolic method.

_**Affects routines:**_ `XSLPconstruct`,`XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_JACOBIAN`, `XSLP_HESSIAN`

_**Category:**_ Control

#### XSLP_DETERMINISTIC, NLPDETERMINISTIC

_**Description:**_    Determines if the parallel features of SLP should be guaranteed to be deterministic
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, MISLP, Parallel

_**Default value:**_ 1

_**Note:**_
Determinism can only be guaranteed if no callbacks are used, or if in the presence of callbacks the effect of the callbacks only depend on local information provided by SLP.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART_POOLSIZE`,

_**Category:**_ Control

#### XSLP_ECFCHECK, SLPECFCHECK

_**Description:**_    Check feasibility at the point of linearization for extended convergence criteria
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| no check \(extended criteria are always used\);
 `1`| check until one infeasible constraint is found;
 `2`| check all constraints.

_**Default value:**_ 1

_**Notes:**_
The extended convergence criteria measure the accuracy of the solution of the linear approximation compared to the solution of the original nonlinear problem. For this to work, the linear approximation needs to be reasonably good at the point of linearization. In particular, it needs to be reasonably close to feasibility.
 `XSLP_ECFCHECK`is used to determine what checking of feasibility is carried out at the point of linearization. If the point of linearization at the start of an SLP iteration is deemed to be infeasible, then the extended convergence criteria are not used to decide convergence at the end of that SLP iteration.
If all that is required is to decide that the point of linearization is not feasible, then the search can stop after the first infeasible constraint is found \(parameter is set to 1\). If the actual number of infeasible constraints is required, then `XSLP_ECFCHECK`should be set to 2, and all constraints will be checked.
The number of infeasible constraints found at the point of linearization is returned in `XSLP_ECFCOUNT`.

_**Affects routines:**_ Convergence criteria,`XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ECFCOUNT`, `XSLP_ECFTOL_A`, `XSLP_ECFTOL_R`

_**Category:**_ Control

#### XSLP_ECHOXPRSMESSAGES

_**Description:**_    Controls if the XSLP message callback should relay messages from the XPRS library.
 
_**Type:**_ Integer

_**Topic area:**_ 
Logging

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| automatic: if an XSLP message callback is not set, then messages from the nonlinear solver are sent to the XPRS message callback; if an XSLP message callback is set, then messages are not echoed.
 `0`| the XPRS and XSLP message callbacks are treated as independent.
 `1`| messages from the XPRS message callback are sent to the XSLP message callback.
 `2`| messages from the nonlinear solver are sent to the XPRS message callback.

_**Default value:**_ -1
_**Category:**_ Control

#### XSLP_ERROROFFSET, SLPERROROFFSET

_**Description:**_    Position of first character of constraint name used to create name of penalty error vectors
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 0

_**Note:**_
During augmentation, penalty error vectors may be created for some or all of the constraints. The vectors are created with names derived from the corresponding constraint name. Customized naming is possible using `XSLP_MINUSERRORFORMAT` and `XSLP_PLUSERRORFORMAT` to define a format and `XSLP_ ERROR OFFSET` to define the first character \(counting from zero\) of the constraint name to be used.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_MINUSERRORFORMAT`, `XSLP_PLUSERRORFORMAT`

_**Category:**_ Control

#### XSLP_EVALUATE, NLPEVALUATE

_**Description:**_    Evaluation strategy for user functions
 
_**Type:**_ Integer

_**Topic area:**_ 
User Functions

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| use derivatives where possible;
 `1`| always re-evaluate.

_**Default value:**_ 0

_**Note:**_
If a user function returns derivatives or returns more than one value, then it is possible for Xpress NonLinear to estimate the value of the function from its derivatives if the new point of evaluation is sufficiently close to the original. Setting `XSLP_EVALUATE` to 1 will force re-evaluation of all functions regardless of how much or little the point of evaluation has changed.

_**Affects routines:**_ `XSLPevaluatecoef`,`XSLPevaluateformula`

_**See also:**_
`XSLP_FUNCEVAL`

_**Category:**_ Control

#### XSLP_FILTER, SLPFILTER

_**Description:**_    Bit map for controlling solution updates
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Bit-vector, Solution

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| retain best solution according to the merit function.
 `1`| check cascaded solutions against improvements in the merit function.
 `2`| force minimum step sizes in line search.
 `3`| accept the trust region step is the line search returns a zero step size.

_**Default value:**_ 3 \(bit 0,1\)

_**Notes:**_
Bit 0 determines whether `XSLPgetslpsol` should return the final converged solution \(if the bit is off\), or the solution which had the best value according to the merit function \(if the bit is on, which is the default\).
If bit 1 is set, a cascaded solution which does not improve the merit function will be rejected \(XSLP will revert to the solution of the linearization\).
Bits 2-3 determine the strategy for when the step direction is not improving according to the merit function.

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_FILTER_KEEPBEST` | 
Setting bit 1 | `XSLP_FILTER_CASCADE` | 
Setting bit 2 | `XSLP_FILTER_ZEROLINESEARCH` | 
Setting bit 3 | `XSLP_FILTER_ZEROLINESEARCHTR` | 



_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`,`XSLPcascade`

_**See also:**_
`XSLP_MERITLAMBDA`, `XSLP_CASCADE`, `XSLP_LSSTART`, `XSLP_LSITERLIMIT`, `XSLP_LSPATTERNLIMIT`

_**Category:**_ Control

#### XSLP_FINDIV, NLPFINDIV

_**Description:**_    Option for running a heuristic to find a feasible initial point
 
_**Type:**_ Integer

_**Topic area:**_ 
Heuristics

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Automatic \(default\).
 `0`| Disable the heuristic.
 `1`| Enable the heuristic.

_**Default value:**_ -1

_**Notes:**_
The procedure uses bound reduction \(and, up to an extent, probing\) to obtain a point in the initial bounding box that is feasible for the bound reduction techniques.
If an initial point is already specified and is found not to violate bound reduction, then the heuristic is not run and the given point is used as the initial solution.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_FUNCEVAL, NLPFUNCEVAL

_**Description:**_    Bit map for determining the method of evaluating user functions and their derivatives
 
_**Type:**_ Integer

_**Topic areas:**_ 
User Functions, Derivatives

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `3`| evaluate function whenever independent variables change.
 `4`| evaluate function when independent variables change outside tolerances.
 `5`| application of bits 3-4: 0 = functions which do not have a defined re-evaluation mode;1 = all functions.
 `6`| tangential derivatives.
 `7`| forward derivatives
 `8`| application of bits 6-7: 0 = functions which do not have a defined derivative mode;1 = all functions.

_**Default value:**_ 0

_**Notes:**_
Bits 3-4 determine the type of function re-evaluation. If both bits are zero, then the settings for each individual function are used.
If bit 3 or bit 4 is set, then bit 5 defines which functions the setting applies to. If it is set to 1, then it applies to all functions. Otherwise, it applies only to functions which do not have an explicit setting of their own.
Bits 6-7 determine the type of calculation for numerical derivatives. If both bits are zero, then the settings for each individual function are used.
If bit 6 or bit 7 is set, then bit 8 defines which functions the setting applies to. If it is set to 1, then it applies to all functions. Otherwise, it applies only to functions which do not have an explicit setting of their own.
The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 3 | `XSLP_RECALC` | 
Setting bit 4 | `XSLP_TOLCALC` | 
Setting bit 5 | `XSLP_ALLCALCS` | 
Setting bit 6 | `XSLP_2DERIVATIVE` | 
Setting bit 7 | `XSLP_1DERIVATIVE` | 
Setting bit 8 | `XSLP_ALLDERIVATIVES` | 



_**Affects routines:**_ `XSLPevaluatecoef`,`XSLPevaluateformula`

_**See also:**_
`XSLP_EVALUATE`

_**Category:**_ Control

#### XSLP_GRIDHEURSELECT, SLPGRIDHEURSELECT

_**Description:**_    Bit map selectin which heuristics to run if the problem has variable with an integer delta
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Heuristics

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Enumeration: try all combinations.
 `1`| Simple search heuristics.
 `2`| Simulated annealing.

_**Default value:**_ 6

_**Note:**_
A value of 0 indicates that integer deltas are only taken into consideration during the SLP iterations.

_**Note:**_
The enumeration option can be useful for cases where the number of possible values of the variables with an integer delta is small.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_HEURSTRATEGY, SLPHEURSTRATEGY

_**Description:**_    Branch and Bound: This specifies the MINLP heuristic strategy. On some problems it is worth trying more comprehensive heuristic strategies by setting `HEURSTRATEGY`to 2 or 3.
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Heuristics

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Automatic selection of heuristic strategy \(depending on XPRS\_HEUREMPHASIS\).
 `0`| No heuristics.
 `1`| Basic heuristic strategy.
 `2`| Enhanced heuristic strategy.
 `3`| Extensive heuristic strategy.
 `4`| Run all heuristics without effort limits.

_**Default value:**_ `-1`

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`.
_**Category:**_ Control

#### XSLP_HESSIAN, NLPHESSIAN

_**Description:**_    Second order differentiation mode when using analytical derivatives
 
_**Type:**_ Integer

_**Topic area:**_ 
Derivatives

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1,0`| automatic selection
 `1`| numerical derivatives \(finite difference\)
 `2`| symbolic differentiation
 `3`| automatic differentiation

_**Default value:**_ -1

_**Note:**_
Symbolic mode differentiation for the second order derivatives is only available when `XSLP_JACOBIAN` is also set to symbolic mode.

_**See also:**_
`XSLP_DERIVATIVES`, `XSLP_JACOBIAN`

_**Category:**_ Control

#### XSLP_INFEASLIMIT, SLPINFEASLIMIT

_**Description:**_    The maximum number of consecutive infeasible SLP iterations which can occur before Xpress-SLP terminates
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Limits

_**Default value:**_ 3

_**Note:**_
An infeasible solution to an SLP iteration means that is likely that Xpress-SLP will create a poor linear approximation for the next SLP iteration. Sometimes, small infeasibilities arise because of numerical difficulties and do not seriously affect the solution process. However, if successive solutions remain infeasible, it is unlikely that Xpress-SLP will be able to find a feasible converged solution. `XSLP_INFEASLIMIT` sets the number of successive SLP iterations which must take place before Xpress-SLP terminates with a status of "infeasible solution".

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_ITERLIMIT, SLPITERLIMIT

_**Description:**_    The maximum number of SLP iterations
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Limits

_**Default value:**_ 1000

_**Note:**_
If Xpress-SLP reaches `XSLP_ITERLIMIT` without finding a converged solution, it will stop. For MISLP, the limit is on the number of SLP iterations at each node.

_**Affects routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_JACOBIAN, NLPJACOBIAN

_**Description:**_    First order differentiation mode when using analytical derivatives
 
_**Type:**_ Integer

_**Topic area:**_ 
Derivatives

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1,0`| automatic selection
 `1`| numerical derivatives \(finite difference\)
 `2`| symbolic differentiation
 `3`| automatic differentiation

_**Default value:**_ -1

_**Note:**_
Symbolic mode differentiation for the second order derivatives is only available when `XSLP_JACOBIAN` is set to symbolic mode.

_**See also:**_
`XSLP_DERIVATIVES`, `XSLP_HESSIAN`

_**Category:**_ Control

#### XSLP_KEEPEQUALSCOLUMN, NLPKEEPEQUALSCOLUMN

_**Description:**_    When set to a nonzero value, the MPS reader will keep the equals column in the problem
 
_**Type:**_ Integer

_**Topic area:**_ 
Misc

_**Default value:**_ 0

_**Note:**_
This control is provided mainly for backward compatibility.

_**Affects routines:**_ `XSLPreadprob`
_**Category:**_ Control

#### XSLP_LINQUADBR, NLPLINQUADBR

_**Description:**_    Use linear and quadratic constraints and objective function to further reduce bounds on all variables
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| automatic selection
 `0`| disable
 `1`| enable

_**Default value:**_ -1

_**Note:**_
While bound reduction is effective when performed on nonlinear, nonquadratic constraints and objective function, it can be useful to obtain tightened bounds from linear and quadratic constraints, as the corresponding variables may appear in other nonlinear constraints. This option then allows for a slightly more expensive bound reduction procedure, at the benefit of further reduction in the problem's bounds.

_**See also:**_
`XSLP_PRESOLVEOPS`, `XSLP_PROBING`

_**Category:**_ Control

#### XSLP_LOG, NLPLOG

_**Description:**_    Level of printing during SLP iterations
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| none
 `0`| minimal
 `1`| normal: iteration, penalty vectors
 `2`| omit from convergence log any variables which have converged
 `3`| omit from convergence log any variables which have already converged \(except variables on step bounds\)
 `4`| include all variables in convergence log
 `5`| include user function call communications in the log

_**Default value:**_ 0

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_LSITERLIMIT, SLPLSITERLIMIT

_**Description:**_    Number of iterations in the line search
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Limits

_**Default value:**_ 0

_**Notes:**_
The line search attempts to refine the step size suggested by the trust region step bounds. The line search is a local method; the control sets a maximum on the number of model evaluations during the line search.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_LSPATTERNLIMIT`, `XSLP_LSSTART`, `XSLP_LSZEROLIMIT`, `XSLP_FILTER`

_**Category:**_ Control

#### XSLP_LSPATTERNLIMIT, SLPLSPATTERNLIMIT

_**Description:**_    Number of iterations in the pattern search preceding the line search
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Limits

_**Default value:**_ 0

_**Notes:**_
When positive, defines the number of samples taken along the step size suggested by the trust region step bounds before initiating the line search. Useful for highly non-convex problems.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_LSITERLIMIT`, `XSLP_LSSTART`, `XSLP_LSZEROLIMIT`, `XSLP_FILTER`

_**Category:**_ Control

#### XSLP_LSSTART, SLPLSSTART

_**Description:**_    Iteration in which to active the line search
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 8

_**Notes:**_


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_LSITERLIMIT`, `XSLP_LSPATTERNLIMIT`, `XSLP_LSZEROLIMIT`, `XSLP_FILTER`

_**Category:**_ Control

#### XSLP_LSZEROLIMIT, SLPLSZEROLIMIT

_**Description:**_    Maximum number of zero length line search steps before line search is deactivated
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Limits

_**Default value:**_ 5

_**Notes:**_
When the line search repeatedly returns a zero step size, counteracted by bits set on `XSLP_FILTER`, the effort spent in line search is redundant, and line search will be deactivated after `XSLP_LSZEROLIMIT` consecutive such iteration.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_LSITERLIMIT`, `XSLP_LSPATTERNLIMIT`, `XSLP_LSSTART`, `XSLP_FILTER`

_**Category:**_ Control

#### XSLP_MAXTIME, NLPMAXTIME

_**Description:**_    The maximum time in seconds that the SLP optimization will run before it terminates
 
_**Type:**_ Integer

_**Topic area:**_ 
Limits

_**Default value:**_ 0

_**Notes:**_
The \(elapsed\) time is measured from the beginning of the first SLP optimization.
If `XSLP_MAXTIME`is negative, Xpress NonLinear will terminate after \( `-XSLP_MAXTIME`\) seconds. If it is positive, Xpress NonLinear will terminate in MISLP after `XSLP_MAXTIME`seconds or as soon as an integer solution has been found thereafter.

_**Affects routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_MIPALGORITHM, SLPMIPALGORITHM

_**Description:**_    Bitmap describing the MISLP algorithms to be used
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Solve initial SLP to convergence.
 `2`| Relax step bounds according to`XSLP_MIPRELAXSTEPBOUNDS`after initial node.
 `3`| Fix step bounds according to`XSLP_MIPFIXSTEPBOUNDS`after initial node.
 `4`| Relax step bounds according to`XSLP_MIPRELAXSTEPBOUNDS`at each node.
 `5`| Fix step bounds according to`XSLP_MIPFIXSTEPBOUNDS`at each node.
 `6`| Limit iterations at each node to`XSLP_MIPITERLIMIT`.
 `7`| Relax step bounds according to`XSLP_MIPRELAXSTEPBOUNDS`after MIP solution is found.
 `8`| Fix step bounds according to`XSLP_MIPFIXSTEPBOUNDS`after MIP solution is found.
 `9`| Use MIP at each SLP iteration instead of SLP at each node.
 `10`| Use MIP on converged SLP solution and then SLP on the resulting MIP solution.

_**Default value:**_ 17 \(bits 0 and4 are set\)

_**Notes:**_
`XSLP_MIPALGORITHM` determines the strategy of `XSLPnlpoptimize` for solving MINLP problems. The recommended approach is to solve the problem first without reference to the discrete variables. This can be handled automatically by setting bit 0 of `XSLP_MIPALGORITHM`; if done manually, then optimize using the "l" option to prevent the Optimizer presolve from changing the problem.
Some versions of the optimizer re-run the initial node as part of the tree search; it is possible to initiate a new SLP optimization at this point by relaxing or fixing step bounds \(use bits 2 and 3\). If step bounds are fixed for a class of variable, then the variables in that class will not change their value in any child node.
At each node, it is possible to relax or fix step bounds. It is recommended that step bounds are relaxed, so that the new problem can be solved starting from its parent, but without undue restrictions cased by step bounding \(use bit 4\). Exceptionally, it may be preferable to restrict the freedom of child nodes by relaxing fewer types of step bound or fixing the values of some classes of variable \(use bit 5\).
When the optimal node has been found, it is possible to fix the discrete variables and then re-optimize with SLP. Step bounds can be relaxed or fixed for this optimization as well \(use bits 7 and 8\).
Although it is ultimately necessary to solve the optimal node to convergence, individual nodes can be truncated after `XSLP_MIPITERLIMIT`SLP iterations. Set bit 6 to activate this feature.
The normal MISLP algorithm uses SLP at each node. One alternative strategy is to use the MIP optimizer for solving each SLP iteration. Set bit 9 to implement this strategy \("MIP within SLP"\).
Another strategy is to solve the problem to convergence ignoring the nature of the integer variables. Then, fixing the linearization, use MIP to find the optimal setting of the discrete variables. Then, fixing the discrete variables, but varying the linearization, solve to convergence. Set bit 10 to implement this strategy \("SLP then MIP"\).
For mode details about MISLP algorithms and strategies, see the separate section.
The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_MIPINITIALSLP` | 
Setting bit 2 | `XSLP_MIPINITIALRELAXSLP` | 
Setting bit 3 | `XSLP_MIPINITIALFIXSLP` | 
Setting bit 4 | `XSLP_MIPNODERELAXSLP` | 
Setting bit 5 | `XSLP_MIPNODEFIXSLP` | 
Setting bit 6 | `XSLP_MIPNODELIMITSLP` | 
Setting bit 7 | `XSLP_MIPFINALRELAXSLP` | 
Setting bit 8 | `XSLP_MIPFINALFIXSLP` | 
Setting bit 9 | `XSLP_MIPWITHINSLP` | 
Setting bit 10 | `XSLP_SLPTHENMIP` | 
Setting bit 11 | `XSLP_NOFINALROUNDING` | 



_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_ALGORITHM`, `XSLP_MIPFIXSTEPBOUNDS`, `XSLP_MIPITERLIMIT`, `XSLP_MIPRELAXSTEPBOUNDS`

_**Category:**_ Control

#### XSLP_MIPCUTOFFCOUNT, SLPMIPCUTOFFCOUNT

_**Description:**_    Number of SLP iterations to check when considering a node for cutting off
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Limits

_**Default value:**_ 5

_**Notes:**_
If the objective function is worse by a defined amount than the best integer solution obtained so far, then the SLP will be terminated \(and the node will be cut off\). The node will be cut off at the current SLP iteration if the objective function for the last `XSLP_MIPCUTOFFCOUNT` SLP iterations are all worse than the best obtained so far, and the difference is greater than _XSLP\_MIPCUTOFF\_\_A_  and _OBJ \* XSLP\_MIPCUTOFF\_\_R_  where _OBJ_  is the best integer solution obtained so far.
The test is not applied until at least `XSLP_MIPCUTOFFLIMIT`SLP iterations have been carried out at the current node.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPCUTOFF_A`, `XSLP_MIPCUTOFF_R`, `XSLP_MIPCUTOFFLIMIT`

_**Category:**_ Control

#### XSLP_MIPCUTOFFLIMIT, SLPMIPCUTOFFLIMIT

_**Description:**_    Number of SLP iterations to check when considering a node for cutting off
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Limits

_**Default value:**_ 10

_**Notes:**_
If the objective function is worse by a defined amount than the best integer solution obtained so far, then the SLP will be terminated \(and the node will be cut off\). The node will be cut off at the current SLP iteration if the objective function for the last `XSLP_MIPCUTOFFCOUNT` SLP iterations are all worse than the best obtained so far, and the difference is greater than _XSLP\_MIPCUTOFF\_\_A_  and _OBJ \* XSLP\_MIPCUTOFF\_\_R_  where _OBJ_  is the best integer solution obtained so far.
The test is not applied until at least `XSLP_MIPCUTOFFLIMIT`SLP iterations have been carried out at the current node.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPCUTOFF_A`, `XSLP_MIPCUTOFF_R`, `XSLP_MIPCUTOFFCOUNT`

_**Category:**_ Control

#### XSLP_MIPDEFAULTALGORITHM, SLPMIPDEFAULTALGORITHM

_**Description:**_    Default algorithm to be used during the tree search in MISLP
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Linearizations

_**Default value:**_ 3

_**Note:**_
The default algorithm used within SLP during the MISLP optimization can be set using `XSLP_MIPDEFAULTALGORITHM`. It will not necessarily be the same as the one best suited to the initial SLP optimization.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XPRS_DEFAULTALG`, `XSLP_MIPALGORITHM`

_**Category:**_ Control

#### XSLP_MIPFIXSTEPBOUNDS, SLPMIPFIXSTEPBOUNDS

_**Description:**_    Bitmap describing the step-bound fixing strategy during MISLP
 
_**Type:**_ Integer

_**Topic area:**_ 
MISLP

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Fix step bounds on structural SLP variables which are not in coefficients.
 `1`| Fix step bounds on all structural SLP variables.
 `2`| Fix step bounds on SLP variables appearing only in coefficients.
 `3`| Fix step bounds on SLP variables appearing in coefficients.

_**Default value:**_ 0

_**Note:**_
At any node \(including the initial and optimal nodes\) it is possible to fix the step bounds of classes of variables so that the variables themselves will not change. This may help with convergence, but it does increase the chance of a local optimum because of excessive artificial restrictions on the variables.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPALGORITHM`, `XSLP_MIPRELAXSTEPBOUNDS`

_**Category:**_ Control

#### XSLP_MIPITERLIMIT, SLPMIPITERLIMIT

_**Description:**_    Maximum number of SLP iterations at each node
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Limits

_**Default value:**_ 0

_**Note:**_
If bit 6 of `XSLP_MIPALGORITHM` is set, then the number of iterations at each node will be limited to `XSLP_MIPITERLIMIT`.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_ITERLIMIT`, `XSLP_MIPALGORITHM`

_**Category:**_ Control

#### XSLP_MIPLOG, SLPMIPLOG

_**Description:**_    Frequency with which MIP status is printed
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, Logging

_**Default value:**_ 0 \(deterministic logging\)

_**Note:**_
By default \(zero or negative value\) the MIP status is printed after syncronization points. If `XSLP_MIPLOG` is set to a positive integer, then the current MIP status \(node number, best value, best bound\) is printed every `XSLP_MIPLOG` nodes.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_LOG`, `XSLP_SLPLOG`

_**Category:**_ Control

#### XSLP_MIPOCOUNT, SLPMIPOCOUNT

_**Description:**_    Number of SLP iterations at each node over which to measure objective function variation
 
_**Type:**_ Integer

_**Topic areas:**_ 
MISLP, SLP-convergence

_**Default value:**_ 5

_**Note:**_
The objective function test for MIP termination is applied only when step bounding has been applied \(or `XSLP_SBSTART` SLP iterations have taken place if step bounding is not being used\). The node will be terminated at the current SLP iteration if the range of the objective function values over the last `XSLP_MIPOCOUNT` SLP iterations is within _XSLP\_MIPOTOL\_A_  or within _OBJ \* XSLP\_MIPOTOL\_R_  where _OBJ_  is the average value of the objective function over those iterations.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPOTOL_A` `XSLP_MIPOTOL_R` `XSLP_SBSTART`

_**Category:**_ Control

#### XSLP_MIPRELAXSTEPBOUNDS, SLPMIPRELAXSTEPBOUNDS

_**Description:**_    Bitmap describing the step-bound relaxation strategy during MISLP
 
_**Type:**_ Integer

_**Topic area:**_ 
MISLP

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Relax step bounds on structural SLP variables which are not in coefficients.
 `1`| Relax step bounds on all structural SLP variables.
 `2`| Relax step bounds on SLP variables appearing only in coefficients.
 `3`| Relax step bounds on SLP variables appearing in coefficients.

_**Default value:**_ 15 \(relax all types\)

_**Note:**_
At any node \(including the initial and optimal nodes\) it is possible to relax the step bounds of classes of variables so that the variables themselves are completely free to change. This may help with finding a global optimum, but it may also increase the solution time, because more SLP iterations are necessary at each node to obtain a converged solution.

_**Affects routines:**_ `XSLPnlpoptimize`

_**See also:**_
`XSLP_MIPALGORITHM`, `XSLP_MIPFIXSTEPBOUNDS`

_**Category:**_ Control

#### XSLP_MULTISTART, MULTISTART

_**Description:**_    The multistart main control. Defines if the multistart search is to be initiated, or if only the baseline model is to be solved.
 
_**Type:**_ Integer

_**Topic area:**_ 
Multistart

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Depends on if any multistart jobs have been added.
 `0`| Multistart is off.
 `1`| Multistart is on.

_**Default value:**_ -1

_**Note:**_
By default, the multistart search will always be initiated if multistart jobs have been added to the problem. The \(original\) base problem is not part of the multisearch job pool. To make it so, add an job with no extra settings \(template job\). It might be useful to load multiple template jobs, and customize them from callbacks.

_**Note:**_
[FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/) supports the solution of nonconvex problems to global optimality.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART_MAXSOLVES`, `XSLP_MULTISTART_MAXTIME`

_**Category:**_ Control

#### XSLP_MULTISTART_LOG, MULTISTART_LOG

_**Description:**_    The level of logging during the multistart run.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Multistart, Logging

_**Default value:**_ 0

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART`,

_**Category:**_ Control

#### XSLP_MULTISTART_MAXSOLVES, MULTISTART_MAXSOLVES

_**Description:**_    The maximum number of jobs to create during the multistart search.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Multistart, Limits

_**Default value:**_ -1 \(no upper limit\)

_**Note:**_
This control can be increased on the fly during the mutlistart search: for example, if a job gets refused by a user callback, the callback may increase this limit to account for the rejected job.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART`, `XSLP_MULTISTART_MAXTIME`

_**Category:**_ Control

#### XSLP_MULTISTART_MAXTIME, MULTISTART_MAXTIME

_**Description:**_    The maximum total time to be spent in the mutlistart search.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Multistart, Limits

_**Default value:**_ 0 \(no upper limit\)

_**Note:**_
`XSLP_MAXTIME` applies on a per job instance basis. There will be some time spent even after XSLP\_MULTISTART\_MAXTIME has elapsed, while the running jobs get terminated and their results collected.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART`, `XSLP_MULTISTART_MAXSOLVES`

_**Category:**_ Control

#### XSLP_MULTISTART_POOLSIZE, MULTISTART_POOLSIZE

_**Description:**_    The maximum number of problem objects allowed to pool up before synchronization in the deterministic multistart.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Multistart, Limits

_**Default value:**_ 2

_**Note:**_
Deterministic multistart is ensured by guaranteeing that the multistart solve results are evaluated in the same order every time. Solves that finish too soon can be pooled until all earlier started solves finish, allowing the system to start solving other multistart instances in the meantime on idle threads. Larger pool sizes will provide better speedups, but will require larger amounts of memory. Positive values are interpreted as a multiplier on the maximum number of active threads used, while negative values are interpreted as an absolute limit \(and the absolute value is used\). A value of zero will mean no result pooling.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART`, `XSLP_DETERMINISTIC`

_**Category:**_ Control

#### XSLP_MULTISTART_SEED, MULTISTART_SEED

_**Description:**_    Random seed used for the automatic generation of initial point when loading multistart presets
 
_**Type:**_ Integer

_**Topic area:**_ 
Multistart

_**Default value:**_ 0

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART`

_**Category:**_ Control

#### XSLP_NLPSOLVER, NLPSOLVER

_**Description:**_    Controls whether to call FICO Xpress Global or one of the local solvers
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| If the license allows and there are no user functions or multistart jobs, FICO Xpress Global will be called, otherwise a local solver.
 `1`| The algorithm selected by`XSLP_SOLVER`will be used to find a locally optimal solution
 `2`| FICO Xpress Global will be used to find a globally optimal solution

_**Default value:**_ -1

_**Note:**_

The following constants are provided for setting this control:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
-1 | `NLPSOLVER_AUTOMATIC` | 
1 | `NLPSOLVER_LOCAL` | 
2 | `NLPSOLVER_GLOBAL` | 


Note that in cases where the problem can be reformulated to a convex MIQCQP, the Optimizer may be called independent of this control.


_**See also:**_
`XSLP_SOLVER`

_**Category:**_ Control

#### XSLP_MULTISTART_THREADS, MULTISTART_THREADS

_**Description:**_    The maximum number of threads to be used in multistart
 
_**Type:**_ Integer

_**Topic areas:**_ 
Multistart, Parallel

_**Default value:**_ -1 \(determined by XSLP\_THREADS\)

_**Note:**_
The current hard upper limit on the number of threads to be used in multistart is 64.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`

_**See also:**_
`XSLP_MULTISTART` `XSLP_THREADS`

_**Category:**_ Control

#### XSLP_OCOUNT, SLPOCOUNT

_**Description:**_    Number of SLP iterations over which to measure objective function variation for static objective \(2\) convergence criterion
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Default value:**_ 5

_**Note:**_
The static objective \(2\) convergence criterion does not measure convergence of individual variables. Instead, it measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables interacting with active constraints \(those that have a marginal value of at least `XSLP_MVTOL`\) have converged. The rationale is that if the remaining unconverged variables are not involved in active constraints and if the objective function is not changing significantly between iterations, then the solution is more-or-less practical.
The variation in the objective function is defined as
_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_OCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤XSLP\_OTOL\_A_ 
then the problem has converged on the absolute static objective \(2\) convergence criterion.
The static objective function \(2\) test is applied only if `XSLP_OCOUNT`is at least 2.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_OTOL_A` `XSLP_OTOL_R`

_**Category:**_ Control

#### XSLP_PENALTYINFOSTART, SLPPENALTYINFOSTART

_**Description:**_    Iteration from which to record row penalty information
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 3

_**Note:**_
Information about the size \(current and total\) of active penalties of each row and the number of times a penalty vector has been active is recorded starting at the SLP iteration number given by `XSLP_PENALTYINFOSTART`.
_**Category:**_ Control

#### XSLP_POSTSOLVE, NLPPOSTSOLVE

_**Description:**_    This control determines whether postsolving should be performed automatically
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Postsolve if the problem could be solved to optimality/infeasibility.
 `0`| Do not automatically postsolve.
 `1`| Postsolve automatically.

_**Default value:**_ -1

_**See also:**_
`XSLP_PRESOLVE`

_**Category:**_ Control

#### XSLP_PRESOLVE, NLPPRESOLVE

_**Description:**_    This control determines whether presolving should be performed on the nonlinear problem prior to starting the main algorithm
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Disable nonlinear presolve if and only if Optimizer presolve is disabled.
 `0`| Disable nonlinear presolve.
 `1`| Activate nonlinear presolve.
 `2`| Low memory presolve. Original problem is not restored by postsolve and dual solution may not be completely postsolved.

_**Default value:**_ -1

_**Note:**_
The Xpress NonLinear nonlinear presolve \(which is carried out once, before augmentation in SLP or introducing auxiliaries in global\) is independent of the Optimizer presolve \(which is carried out during each SLP iteration or after introducing auxiliaries for a global solve\).

_**Affects routines:**_ `XSLPconstruct`,`XSLPpresolve`

_**See also:**_
`XSLP_PRESOLVELEVEL`, `XSLP_PRESOLVEOPS`, `XSLP_REFORMULATE`

_**Category:**_ Control

#### XSLP_PRESOLVELEVEL, NLPPRESOLVELEVEL

_**Description:**_    This control determines the level of changes presolve may carry out on the problem and whether column/row indices may change
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `1`| Individual rows only presolve, no dropped columns/rows or index changes, no nonlinear transformations \( `XSLP_PRESOLVELEVEL_LOCALIZED`\).
 `2`| All linear presolve that does not drop columns/rows, no index changes, no nonlinear transformations \( `XSLP_PRESOLVELEVEL_BASIC`\).
 `3`| Full linear presolve including dropping columns/rows and index changes, no nonlinear transformations \( `XSLP_PRESOLVELEVEL_LINEAR`\).
 `4`| Full presolve \( `XSLP_PRESOLVELEVEL_FULL`\).

_**Default value:**_ XSLP\_PRESOLVELEVEL\_FULL

_**Note:**_
`XSLP_PRESOLVEOPS` and `XSLP_REFORMULATE` controls the operations carried out in presolve. XSLP\_PRESOLVELEVEL controls how those operations may change the problem. `XSLP_PRESOLVE` controls whether presolve is performed at all.

_**Affects routines:**_ `XSLPconstruct`,`XSLPpresolve`

_**See also:**_
`XSLP_PRESOLVE`, `XSLP_PRESOLVEOPS`, `XSLP_REFORMULATE`

_**Category:**_ Control

#### XSLP_PRESOLVEOPS, NLPPRESOLVEOPS

_**Description:**_    Bitmap indicating the SLP presolve actions to be taken
 
_**Type:**_ Integer

_**Topic areas:**_ 
Presolve, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Generic SLP presolve.
 `1`| Explicitly fix columns identified as fixed to zero.
 `2`| Explicitly fix all columns identified as fixed.
 `3`| SLP bound tightening.
 `4`| MISLP bound tightening.
 `5`| Bound tightening based on function domains.
 `8`| Do not presolve coefficients.
 `9`| Do not remove delta variables.
 `10`| Avoid reductions that can not be dual postsolved.
 `11`| Allow eliminations on determined variables.
 `12`| Avoid performing linear reductions at the nlp level.
 `13`| Avoid simplifying nonlinear expressions.

_**Default value:**_ 2104

_**Note:**_
The Xpress NonLinear nonlinear presolve \(which is carried out once, before augmentation\) is independent of the Optimizer presolve \(which is carried out during each SLP iteration\). Linear reductions are performed according to `XPRS_PRESOLVEOPS` if bit 12 is not set.

_**Affects routines:**_ `XSLPconstruct`,`XSLPpresolve`

_**See also:**_
`XSLP_PRESOLVELEVEL`, `XSLP_PRESOLVE`, `XSLP_PRESOLVEOPS`, `XSLP_REFORMULATE`

_**Category:**_ Control

#### XSLP_PROBING, NLPPROBING

_**Description:**_    This control determines whether probing on a subset of variables should be performed prior to starting the main algorithm. Probing runs multiple times bound reduction in order to further tighten the bounding box.
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| Automatic.
 `0`| Disable SLP probing.
 `1`| Activate SLP probing only on binary variables.
 `2`| Activate SLP probing only on binary or unbounded integer variables.
 `3`| Activate SLP probing only on binary or integer variables.
 `4`| Activate SLP probing only on binary, integer variables, and unbounded continuous variables.
 `5`| Activate SLP probing on any variable.

_**Default value:**_ -1

_**Note:**_
The Xpress NonLinear nonlinear probing, which is carried out once, is independent of the Optimizer presolve \(which is carried out during each SLP iteration\). The probing level allows for probing on an expanding set of variables, allowing for probing on all variables \(level 5\) or only those for which probing is more likely to be useful \(binary variables\).

_**Affects routines:**_ `XSLPpresolve`

_**See also:**_
`XSLP_PRESOLVEOPS`,

_**Category:**_ Control

#### XSLP_REFORMULATE, NLPREFORMULATE

_**Description:**_    Controls the problem reformulations carried out before augmentation. This allows SLP to take advantage of dedicated algorithms for special problem classes.
 
_**Type:**_ Integer

_**Topic area:**_ 
Presolve

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| Solve convex quadratic objectives using the XPRS library .
 `1`| Convert non-convex quadratic objectives to SLP constructs .
 `2`| Solve convex quadratic constraints using the XPRS library.
 `3`| Convert non-convex QCQP constraints to SLP constructs.
 `4`| Keep second order cones in the XPRS problem to keep them in the linearizations.
 `5`| Convexity of a quadratic only problem may be checked by calling the optimizer to solve the instance.
 `6`| Convert pievewise linear functions to MIP constructs.
 `7`| Convert ABS functions to MIP constraints if the full problem can be made not nonlinear.
 `8`| Convert MIN and MAX functions to MIP expressions if the full problem can be made not nonlinear.
 `9`| Always convert ABS expressions.
 `10`| Always convert MIN and MAX expressions.

_**Default value:**_ `511`\(bits `0`— `8`incl. are set\)

_**Note:**_
The reformulation is part of XSLP presolve, and is only carried out if `XSLP_PRESOLVE` is nonzero.
The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_REFORMULATE_SLP2QP` | 
Setting bit 1 | `XSLP_REFORMULATE_QP2SLP` | 
Setting bit 2 | `XSLP_REFORMULATE_SLP2QCQP` | 
Setting bit 3 | `XSLP_REFORMULATE_QCQP2SLP` | 
Setting bit 4 | `XSLP_REFORMULATE_SOCP2SLP` | 
Setting bit 5 | `XSLP_REFORMULATE_QPSOLVE` | 
Setting bit 6 | `XSLP_REFORMULATE_PWL` | 
Setting bit 7 | `XSLP_REFORMULATE_ABS` | 
Setting bit 8 | `XSLP_REFORMULATE_MINMAX` | 
Setting bit 9 | `XSLP_REFORMULATE_ALLABS` | 
Setting bit 10 | `XSLP_REFORMULATE_ALLMINMAX` | 



_**Affects routines:**_ `XSLPconstruct`,`XSLPminim`,`XSLPmaxim`,`XSLPreminim`,`XSLPremaxim`,`XSLPnlpoptimize`
_**Category:**_ Control

#### XSLP_SAMECOUNT, SLPSAMECOUNT

_**Description:**_    Number of steps reaching the step bound in the same direction before step bounds are increased
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 3

_**Note:**_
If step bounding is enabled, the step bound for a variable will be increased if successive changes are in the same direction. More precisely, if there are `XSLP_SAMECOUNT` successive changes reaching the step bound and in the same direction for a variable, then the step bound \( _B_ \) for the variable will be reset to
 _B\*XSLP\_EXPAND_ .

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_EXPAND`

_**Category:**_ Control

#### XSLP_SAMEDAMP, SLPSAMEDAMP

_**Description:**_    Number of steps in same direction before damping factor is increased
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 3

_**Note:**_
If dynamic damping is enabled, the damping factor for a variable will be increased if successive changes are in the same direction. More precisely, if there are `XSLP_SAMEDAMP` successive changes in the same direction for a variable, then the damping factor \( _D_ \) for the variable will be reset to
 _D\*XSLP\_DAMPEXPAND + XSLP\_DAMPMAX\*\(1-XSLP\_DAMPEXPAND\)_ 

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
Xpress-SLP Solution Process, `XSLP_ALGORITHM`, `XSLP_DAMP`, `XSLP_DAMPMAX`

_**Category:**_ Control

#### XSLP_SBROWOFFSET, SLPSBROWOFFSET

_**Description:**_    Position of first character of SLP variable name used to create name of SLP lower and upper step bound rows
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 0

_**Note:**_
During augmentation, a delta vector is created for each SLP variable. Step bounds are provided for each delta variable, either using explicit bounds, or by using rows to provide lower and upper bounds. If such rows are used, they are created with names derived from the corresponding SLP variable. Customized naming is possible using `XSLP_SBLOROWFORMAT` and `XSLP_SBUPROWFORMAT` to define a format and `XSLP_SBROWOFFSET` to define the first character \(counting from zero\) of the variable name to be used.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_SBLOROWFORMAT`, `XSLP_SBUPROWFORMAT`

_**Category:**_ Control

#### XSLP_SBSTART, SLPSBSTART

_**Description:**_    SLP iteration after which step bounds are first applied
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 8

_**Note:**_
If step bounds are used, they can be applied for the whole of the SLP optimization process, or started after a number of SLP iterations. In general, it is better not to apply step bounds from the start unless one of the following applies:
\(1\) the initial estimates are known to be good, and explicit values can be provided for initial step bounds on all variables; or
\(2\) the problem is unbounded unless all variables are step-bounded.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_SCALE, SLPSCALE

_**Description:**_    When to re-scale the SLP problem
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Numerics

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| No re-scaling.
 `1`| Re-scale every SLP iteration up to`XSLP_SCALECOUNT`iterations after the end of barrier optimization.
 `2`| Re-scale every SLP iteration up to`XSLP_SCALECOUNT`iterations in total.
 `3`| Re-scale every SLP iteration until primal simplex is automatically invoked.
 `4`| Re-scale every SLP iteration.
 `5`| Re-scale every`XSLP_SCALECOUNT`SLP iterations.
 `6`| Re-scale every`XSLP_SCALECOUNT`SLP iterations after the end of barrier optimization.

_**Default value:**_ 1

_**Note:**_
During the SLP optimization, matrix entries can change considerably in magnitude, even when the formulae in the coefficients are not very nonlinear. Re-scaling of the matrix can reduce numerical errors, but may increase the time taken to achieve convergence.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SCALECOUNT`

_**Category:**_ Control

#### XSLP_SCALECOUNT, SLPSCALECOUNT

_**Description:**_    Iteration limit used in determining when to re-scale the SLP matrix
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Numerics

_**Default value:**_ 0

_**Notes:**_
If `XSLP_SCALE` is set to 1 or 2, then `XSLP_SCALECOUNT` determines the number of iterations \(after the end of barrier optimization or in total\) in which the matrix is automatically re-scaled.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SCALE`

_**Category:**_ Control

#### XSLP_SOLVER, LOCALSOLVER

_**Description:**_    Selects the library to use for local solves
 
_**Type:**_ Integer

_**Topic area:**_ 
Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `-1`| automatic selection, based on model characteristics and solver availability
 `0`| use Xpress-SLP \(always available\)
 `1`| use Knitro if available
 `2`| use Xpress-Optimizer if possible \(convex quadratic problems only\)

_**Default value:**_ -1

_**Note:**_

The presence of Knitro is detected automatically. Knitro can be used to solve any problem loaded into XSLP, independently from how the problem was loaded. `XSLP_SOLVER` is set to automatic, XSLP will be selected if any SLP specific construct has been loaded \(these are ignored if Knitro is selected manually\).

When solving problems to global optimality, the `XSLP_SOLVER` control is used to decide which local solver to call for reoptimizing NLP-infeasible solutions heuristically.


_**See also:**_
`XSLP_NLPSOLVER`

_**Category:**_ Control

#### XSLP_SLPLOG, SLPLOG

_**Description:**_    Frequency with which SLP status is printed
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 1

_**Note:**_
If `XSLP_LOG` is set to zero \(minimal logging\) then a nonzero value for `XSLP_SLPLOG` defines the frequency \(in SLP iterations\) when summary information is printed out.

_**Affects routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_LOG`, `XSLP_MIPLOG`

_**Category:**_ Control

#### XSLP_STOPOUTOFRANGE, NLPSTOPOUTOFRANGE

_**Description:**_    Stop optimization and return error code if internal function argument is out of range
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 0

_**Note:**_
If `XSLP_STOPOUTOFRANGE` is set to 1, then if an internal function receives an argument which is out of its allowable range \(for example, _LOG_  of a negative number\), an error code is set and the optimization is terminated.

_**Affects routines:**_ `XSLPevaluatecoef`,`XSLPevaluateformula``XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_THREADS, NLPTHREADS

_**Description:**_    Default number of threads to be used
 
_**Type:**_ Integer

_**Topic area:**_ 
Parallel

_**Default value:**_ -1 \(use XPRS\_THREADS value\)

_**Note:**_
Overall thread control value, used to determine the number of threads used where parallel calculations are possible.

_**Affects routines:**_ `XSLPmaxim`,`XSLPmaxim`

_**See also:**_
`XSLP_CALCTHREADS`, `XSLP_MULTISTART_THREADS`,

_**Category:**_ Control

#### XSLP_THREADSAFEUSERFUNC, NLPTHREADSAFEUSERFUNC

_**Description:**_    Defines if user functions are allowed to be called in parallel
 
_**Type:**_ Integer

_**Topic areas:**_ 
User Functions, Parallel

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| user function are not thread safe, and will not be called in parallel
 `1`| user functions are thread safe, and may be called in parallel

_**Default value:**_ 0 \(no parallel user function calls\)

_**Note:**_
Date and time printing can be useful for identifying slow procedures during the SLP optimization. Setting `XSLP_TIMEPRINT` to 1 prints times at additional points during the optimization.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_TRACEMASKOPS, SLPTRACEMASKOPS

_**Description:**_    Controls the information printed for`XSLP_TRACEMASK`. The order in which the information is printed is determined by the order of bits in`XSLP_TRACEMASKOPS`.
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| The variable name is used as a mask, not as an exact fit.
 `1`| Use mask to trace rows.
 `2`| Use mask to trace columns.
 `3`| Use mask to trace cascaded SLP variables.
 `4`| Show row / column category.
 `5`| Trace slack values.
 `6`| Trace dual values.
 `7`| Trace row penalty multiplier.
 `8`| Trace variable values \(as returned by the lineariation\).
 `9`| Trace reduced costs.
 `10`| Trace slp value \(value used in linearization and cascaded\).
 `11`| Trace step bounds.
 `12`| Trace convergence status.
 `13`| Trace line search.

_**Default value:**_ -1

_**Note:**_

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_TRACEMASK_GENERALFIT` | 
Setting bit 1 | `XSLP_TRACEMASK_ROWS` | 
Setting bit 2 | `XSLP_TRACEMASK_COLS` | 
Setting bit 3 | `XSLP_TRACEMASK_CASCADE` | 
Setting bit 4 | `XSLP_TRACEMASK_TYPE` | 
Setting bit 5 | `XSLP_TRACEMASK_SLACK` | 
Setting bit 6 | `XSLP_TRACEMASK_DUAL` | 
Setting bit 7 | `XSLP_TRACEMASK_WEIGHT` | 
Setting bit 8 | `XSLP_TRACEMASK_SOLUTION` | 
Setting bit 9 | `XSLP_TRACEMASK_REDUCEDCOST` | 
Setting bit 10 | `XSLP_TRACEMASK_SLPVALUE` | 
Setting bit 11 | `XSLP_TRACEMASK_STEPBOUND` | 
Setting bit 12 | `XSLP_TRACEMASK_CONVERGE` | 
Setting bit 13 | `XSLP_TRACEMASK_LINESEARCH` | 



_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`,`XSLPreminim`,`XSLPremaxim`,`XSLPnlpoptimize`
_**Category:**_ Control

#### XSLP_UNFINISHEDLIMIT, SLPUNFINISHEDLIMIT

_**Description:**_    The number of consecutive SLP iterations that may have an unfinished status before the solve is terminated.
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Linearizations

_**Default value:**_ 3

_**Note:**_
If the optimization of the current linear approximation terminates with an "unfinished" status, then first a number of strategies are applied to attempt a successful solve of the same linearization. If this fails, then a new iteration is started to change the linearization itself. This control limits the numner of such repeated attempts.

_**Affects routines:**_ `XSLPnlpoptimize`,`XSLPmaxim`,`XSLPminim`
_**Category:**_ Control

#### XSLP_UPDATEOFFSET, SLPUPDATEOFFSET

_**Description:**_    Position of first character of SLP variable name used to create name of SLP update row
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ 0

_**Note:**_
During augmentation, one or more delta vectors are created for each SLP variable. The values of these are linked to that of the variable through an _update row_ which is created as part of the augmentation procedure. Update rows are created with names derived from the corresponding SLP variable. Customized naming is possible using `XSLP_UPDATEFORMAT` to define a format and `XSLP_UPDATEOFFSET` to define the first character \(counting from zero\) of the variable name to be used.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_UPDATEFORMAT`

_**Category:**_ Control

#### XSLP_VCOUNT, SLPVCOUNT

_**Description:**_    Number of SLP iterations over which to measure static objective \(3\) convergence
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Default value:**_ 0

_**Note:**_
The static objective \(3\) convergence criterion does not measure convergence of individual variables, and in fact does not in any way imply that the solution has converged. However, it is sometimes useful to be able to terminate an optimization once the objective function appears to have stabilized. One example is where a set of possible schedules are being evaluated and initially only a good estimate of the likely objective function value is required, to eliminate the worst candidates.
The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_ VCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤XSLP\_VTOL\_A_ 
then the problem has converged on the absolute static objective function \(3\) criterion.
The static objective function \(3\) test is applied only if after at least `XSLP_VLIMIT`+ `XSLP_SBSTART`SLP iterations have taken place and only if `XSLP_VCOUNT`is at least 2. Where step bounding is being used, this ensures that the test is not applied until after step bounding has been introduced.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SBSTART`, `XSLP_VLIMIT`, `XSLP_VTOL_A`, `XSLP_VTOL_R`

_**Category:**_ Control

#### XSLP_VLIMIT, SLPVLIMIT

_**Description:**_    Number of SLP iterations after which static objective \(3\) convergence testing starts
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Default value:**_ 0

_**Note:**_
The static objective \(3\) convergence criterion does not measure convergence of individual variables, and in fact does not in any way imply that the solution has converged. However, it is sometimes useful to be able to terminate an optimization once the objective function appears to have stabilized. One example is where a set of possible schedules are being evaluated and initially only a good estimate of the likely objective function value is required, to eliminate the worst candidates.
The variation in the objective function is defined as

_δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_
where _Iter_ is the `XSLP_ VCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.
If _ABS\(δObj\)≤XSLP\_VTOL\_A_ 
then the problem has converged on the absolute static objective function \(3\) criterion.
The static objective function \(3\) test is applied only after at least `XSLP_VLIMIT`+ `XSLP_SBSTART`SLP iterations have taken place and only if `XSLP_VCOUNT`is at least 2. Where step bounding is being used, this ensures that the test is not applied until after step bounding has been introduced.

_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_SBSTART`, `XSLP_VCOUNT`, `XSLP_VTOL_A`, `XSLP_VTOL_R`

_**Category:**_ Control

#### XSLP_WCOUNT, SLPWCOUNT

_**Description:**_    Number of SLP iterations over which to measure the objective for the extended convergence continuation criterion
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Default value:**_ 0

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration.

The extended convergence continuation criterion is applied after a converged solution has been found where at least one variable has converged on extended criteria and is at its step bound limit. The extended convergence continuation test measures whether any improvement is being achieved when additional SLP iterations are carried out. If not, then the last converged solution will be restored and the optimization will stop.
For a maximization problem, the improvement in the objective function at the current iteration compared to the objective function at the last converged solution is given by:
 _δObj = Obj - LastConvergedObj_ 
For a minimization problem, the sign is reversed.
If _δObj>XSLP\_WTOL\_A_ and
 _δObj>ABS\(ConvergedObj\) \* XSLP\_WTOL\_R_ then the solution is deemed to have a significantly better objective function value than the converged solution.

When a solution is found which converges on extended criteria and with active step bounds, the solution is saved and SLP optimization continues until one of the following:
\(1\) a new solution is found which converges on some other criterion, in which case the SLP optimization stops with this new solution;
\(2\) a new solution is found which converges on extended criteria and with active step bounds, and which has a significantly better objective function, in which case this is taken as the new saved solution;
\(3\) none of the `XSLP_WCOUNT`most recent SLP iterations has a significantly better objective function than the saved solution, in which case the saved solution is restored and the SLP optimization stops.

If `XSLP_WCOUNT` is zero, then the extended convergence continuation criterion is disabled.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_WTOL_A`, `XSLP_WTOL_R`

_**Category:**_ Control

#### XSLP_XCOUNT, SLPXCOUNT

_**Description:**_    Number of SLP iterations over which to measure static objective \(1\) convergence
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence

_**Default value:**_ 5

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration. However, if the objective function has already been stable for several SLP iterations, then there is less likelihood of an improved result, and the converged solution can be accepted.

The static objective function \(1\) test measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. Because all the variables have converged, the solution is already converged but the fact that some variables are at their step bound limit suggests that the objective function could be improved by going further.

The variation in the objective function is defined as
 _δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_ 
where _Iter_ is the `XSLP_XCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.

If _ABS\(δObj\)≤XSLP\_XTOL\_A_ 
then the objective function is deemed to be static according to the absolute static objective function \(1\) criterion.
If _ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_XTOL\_R_ 
then the objective function is deemed to be static according to the relative static objective function \(1\) criterion.

The static objective function \(1\) test is applied only until `XSLP_XLIMIT` SLP iterations have taken place. After that, if all the variables have converged on strict or extended criteria, the solution is deemed to have converged.

If the objective function passes the relative or absolute static objective function \(1\) test then the solution is deemed to have converged.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_XLIMIT`, `XSLP_XTOL_A`, `XSLP_XTOL_R`

_**Category:**_ Control

#### XSLP_XLIMIT, SLPXLIMIT

_**Description:**_    Number of SLP iterations up to which static objective \(1\) convergence testing is performed
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, SLP-convergence, Limits

_**Default value:**_ 100

_**Note:**_

It may happen that all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. This means that, at least in the linearization, if the variable were to be allowed to move further the objective function would improve. This does not necessarily imply that the same is true of the original problem, but it is still possible that an improved result could be obtained by taking another SLP iteration. However, if the objective function has already been stable for several SLP iterations, then there is less likelihood of an improved result, and the converged solution can be accepted.

The static objective function \(1\) test measures the significance of the changes in the objective function over recent SLP iterations. It is applied when all the variables have converged, but some have converged on extended criteria and at least one of these variables is at its step bound. Because all the variables have converged, the solution is already converged but the fact that some variables are at their step bound limit suggests that the objective function could be improved by going further.

The variation in the objective function is defined as
 _δObj = MAX<sub>Iter</sub>\(Obj\) - MIN<sub>Iter</sub>\(Obj\)_ 
where _Iter_ is the `XSLP_XCOUNT`most recent SLP iterations and _Obj_ is the corresponding objective function value.

If _ABS\(δObj\)≤XSLP\_XTOL\_A_ 
then the objective function is deemed to be static according to the absolute static objective function \(1\) criterion.
If _ABS\(δObj\)≤AVG<sub>Iter</sub>\(Obj\) \* XSLP\_XTOL\_R_ 
then the objective function is deemed to be static according to the relative static objective function \(1\) criterion.

The static objective function \(1\) test is applied only until `XSLP_XLIMIT` SLP iterations have taken place. After that, if all the variables have converged on strict or extended criteria, the solution is deemed to have converged.

If the objective function passes the relative or absolute static objective function \(1\) test then the solution is deemed to have converged.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_XCOUNT`, `XSLP_XTOL_A`, `XSLP_XTOL_R`

_**Category:**_ Control

#### XSLP_ZEROCRITERION, SLPZEROCRITERION

_**Description:**_    Bitmap determining the behavior of the placeholder deletion procedure
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Bit-vector

_**Values:**_

_Bit_ | _Meaning_
---------- | ----------
 `0`| \(=1\) Remove placeholders in nonbasic SLP variables
 `1`| \(=2\) Remove placeholders in nonbasic delta variables
 `2`| \(=4\) Remove placeholders in a basic SLP variable if its update row is nonbasic
 `3`| \(=8\) Remove placeholders in a basic delta variable if its update row is nonbasic and the corresponding SLP variable is nonbasic
 `4`| \(=16\) Remove placeholders in a basic delta variable if the determining row for the corresponding SLP variable is nonbasic
 `5`| \(=32\) Print information about zero placeholders

_**Default value:**_ 0

_**Note:**_

For an explanation of deletion of placeholder entries in the matrix see  _Management of zero placeholder entries_.

The following constants are provided for setting these bits:



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Setting bit 0 | `XSLP_ZEROCRTIERION_NBSLPVAR` | 
Setting bit 1 | `XSLP_ZEROCRTIERION_NBDELTA` | 
Setting bit 2 | `XSLP_ZEROCRTIERION_SLPVARNBUPDATEROW` | 
Setting bit 3 | `XSLP_ZEROCRTIERION_DELTANBUPSATEROW` | 
Setting bit 4 | `XSLP_ZEROCRTIERION_DELTANBDRROW` | 
Setting bit 5 | `XSLP_ZEROCRTIERION_PRINT` | 



_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ZEROCRITERIONCOUNT`, `XSLP_ZEROCRITERIONSTART`,  _Management of zero placeholder entries_

_**Category:**_ Control

#### XSLP_ZEROCRITERIONCOUNT, SLPZEROCRITERIONCOUNT

_**Description:**_    Number of consecutive times a placeholder entry is zero before being considered for deletion
 
_**Type:**_ Integer

_**Topic areas:**_ 
SLP, Limits

_**Default value:**_ 0

_**Note:**_

For an explanation of deletion of placeholder entries in the matrix see  _Management of zero placeholder entries_.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ZEROCRITERION`, `XSLP_ZEROCRITERIONSTART`,  _Management of zero placeholder entries_

_**Category:**_ Control

#### XSLP_ZEROCRITERIONSTART, SLPZEROCRITERIONSTART

_**Description:**_    SLP iteration at which criteria for deletion of placeholder entries are first activated.
 
_**Type:**_ Integer

_**Topic area:**_ 
SLP

_**Default value:**_ 0

_**Note:**_

For an explanation of deletion of placeholder entries in the matrix see  _Management of zero placeholder entries_.


_**Affects routines:**_ `XSLPmaxim`,`XSLPminim`

_**See also:**_
`XSLP_ZEROCRITERION`, `XSLP_ZEROCRITERIONCOUNT`,  _Management of zero placeholder entries_

_**Category:**_ Control

#### Section 20.3 String control parameters


#### XSLP_DELTAFORMAT, SLPDELTAFORMAT

_**Description:**_    Formatting string for creation of names for SLP delta vectors
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pD\_%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for delta vectors. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_DELTAOFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_DELTAOFFSET`

_**Category:**_ Control

#### XSLP_ITERFALLBACKOPS, SLPITERFALLBACKOPS

_**Description:**_    Alternative LP level control values for numerically challenging problems
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Linearizations, Numerics

_**Default value:**_ none

_**Notes:**_

When set, this control provides alternative ways of solving a linearization called adaptive iteration solves. This can be useful for numerically challenging problems that either solve to a non-satisfactory accuracy \(relative to `XSLP_FEASTOLTARGET`\) with the default solves, or that can incorrectly report infeasibility or unboundedness. In such cases, the solve will try the controls listed by `XSLP_ITERFALLBACKOPS` until a satisfactory solution is found or all options are exhausted.

The individual controls for each solve are separated by a comma \(','\), while the set of controls for an attepmt by a colon \(':'\) . Example: 'XPRS\_DEFAULTALG=3 : XPRS\_BARORDER = 2, XPRS\_PRESOLVE = 0' will try primal in one solve, and the homogenous barrier with presolve turned off in an other. Optimizer flags are not inherited by the solve, so use XPRS\_DEFAULTALG for selecting an LP solver to use.

The resulting LP solves are carried out in a parallel manner, using `XSLP_MULTISTART_THREADS` number of threads.

The result of the adaptive solves are always deterministic.

Once a satisfactory solution is found, remaining solves are progressed only as far as necessary to guarantee determinism, so it is beneficial to list more promising control sets first.


_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`,`XSLPnlpoptimize`

_**See also:**_
`XSLP_FEASTOLTARGET`,

_**Category:**_ Control

#### XSLP_IVNAME, NLPIVNAME

_**Description:**_    Name of the set of initial values to be used
 
_**Type:**_ String

_**Topic area:**_ 
File IO

_**Default value:**_ none

_**Notes:**_
This variable may be required for input from a file using `XSLPreadprob` if there is more than one set of initial values in the file. If no name is set, then the first set of initial values will be used, and the name will be set accordingly.
This variable may also be required for output using `XSLPwriteprob`where initial values are included in the problem. If it is not set, then a default name will be used.

_**Affects routines:**_ `XSLPreadprob`,`XSLPwriteprob`

_**Set by routines:**_ `XSLPreadprob`

_**See also:**_
`XSLP_SBNAME`, `XSLP_TOLNAME`

_**Category:**_ Control

#### XSLP_MINUSDELTAFORMAT, SLPMINUSDELTAFORMAT

_**Description:**_    Formatting string for creation of names for SLP negative penalty delta vectors
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pD-%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for negative penalty delta vectors. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_DELTAOFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_DELTAOFFSET`

_**Category:**_ Control

#### XSLP_MINUSERRORFORMAT, SLPMINUSERRORFORMAT

_**Description:**_    Formatting string for creation of names for SLP negative penalty error vectors
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pE-%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for negative penalty error vectors. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_ERROROFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_ERROROFFSET`

_**Category:**_ Control

#### XSLP_PENALTYCOLFORMAT, SLPPENALTYCOLFORMAT

_**Description:**_    Formatting string for creation of the names of the SLP penalty transfer vectors
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pPC\_%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for the penalty transfer vectors which transfer penalty costs into the objective. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by "DELT" for the penalty delta transfer vector and "ERR" for the penalty error transfer vector.

_**Affects routines:**_ `XSLPconstruct`
_**Category:**_ Control

#### XSLP_PENALTYROWFORMAT, SLPPENALTYROWFORMAT

_**Description:**_    Formatting string for creation of the names of the SLP penalty rows
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pPR\_%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for the penalty rows which total the penalty costs for the objective. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by "DELT" for the penalty delta row and "ERR" for the penalty error row.

_**Affects routines:**_ `XSLPconstruct`
_**Category:**_ Control

#### XSLP_PLUSDELTAFORMAT, SLPPLUSDELTAFORMAT

_**Description:**_    Formatting string for creation of names for SLP positive penalty delta vectors
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pD+%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for positive penalty delta vectors. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_DELTAOFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_DELTAOFFSET`

_**Category:**_ Control

#### XSLP_PLUSERRORFORMAT, SLPPLUSERRORFORMAT

_**Description:**_    Formatting string for creation of names for SLP positive penalty error vectors
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pE+%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for positive penalty error vectors. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_ERROROFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_ERROROFFSET`

_**Category:**_ Control

#### XSLP_SBLOROWFORMAT, SLPSBLOROWFORMAT

_**Description:**_    Formatting string for creation of names for SLP lower step bound rows
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pSB-%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for lower limits on step bounds modeled as rows. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_SBROWOFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_SBROWOFFSET`

_**Category:**_ Control

#### XSLP_SBNAME, SLPSBNAME

_**Description:**_    Name of the set of initial step bounds to be used
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ none

_**Notes:**_
This variable may be required for input from a file using `XSLPreadprob` if there is more than one set of initial step bounds in the file. If no name is set, then the first set of initial step bounds will be used, and the name will be set accordingly.
This variable may also be required for output using `XSLPwriteprob`where initial step bounds are included in the problem. If it is not set, then a default name will be used.

_**Affects routines:**_ `XSLPreadprob`,`XSLPwriteprob`

_**Set by routines:**_ `XSLPreadprob`

_**See also:**_
`XSLP_IVNAME`, `XSLP_TOLNAME`

_**Category:**_ Control

#### XSLP_SBUPROWFORMAT, SLPSBUPROWFORMAT

_**Description:**_    Formatting string for creation of names for SLP upper step bound rows
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pSB+%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for upper limits on step bounds modeled as rows. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_SBROWOFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_SBROWOFFSET`

_**Category:**_ Control

#### XSLP_TOLNAME, SLPTOLNAME

_**Description:**_    Name of the set of tolerance sets to be used
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, File IO

_**Default value:**_ none

_**Notes:**_
This variable may be required for input from a file using `XSLPreadprob` if there is more than one set of tolerance sets in the file. If no name is set, then the first set of tolerance sets will be used, and the name will be set accordingly.
This variable may also be required for output using `XSLPwriteprob`where tolerance sets are included in the problem. If it is not set, then a default name will be used.

_**Affects routines:**_ `XSLPreadprob`,`XSLPwriteprob`

_**Set by routines:**_ `XSLPreadprob`

_**See also:**_
`XSLP_IVNAME`, `XSLP_SBNAME`

_**Category:**_ Control

#### XSLP_TRACEMASK, SLPTRACEMASK

_**Description:**_    Mask of variable or row names that are to be traced through the SLP iterates
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ none \(no tracing\)

_**Notes:**_
If the mask is nonempty, variables and rows matching the mask are listed after each SLP iteration and each cascade, allowing for a convenient means to observe how certain variables change through the iterates. This feasture is provided for tuning and model debugging purposes. The actual information printed is controlled by `XSLP_TRACEMASKOPS`.
The string in the tracemask may contain several variable or row names, separated by a whitespace. Wildcards may also be used.

_**Affects routines:**_ `XSLPminim`,`XSLPmaxim`,`XSLPreminim`,`XSLPremaxim`,`XSLPnlpoptimize`,

_**See also:**_
`XSLP_TRACEMASKOPS`

_**Category:**_ Control

#### XSLP_UPDATEFORMAT, SLPUPDATEFORMAT

_**Description:**_    Formatting string for creation of names for SLP update rows
 
_**Type:**_ String

_**Topic areas:**_ 
SLP, Logging

_**Default value:**_ pU\_%s

where p is a unique prefix for names in the current problem

_**Note:**_
This control can be used to create a specific naming structure for update rows. The structure follows the normal C-style printf form, and can contain printing characters plus one% s string. This will be replaced by sequential characters from the name of the variable starting at position `XSLP_UPDATEOFFSET`.

_**Affects routines:**_ `XSLPconstruct`

_**See also:**_
`XSLP_UPDATEOFFSET`

_**Category:**_ Control

#### Section 20.4 Knitro controls


All Knitro controls are available with an 'X' pre-tag. For example the Knitro integer control 'KTR\_PARAM\_ALGORITHM' can be set using XSLPsetintcontrol using the control ID defined as 'XKTR\_PARAM\_ALGORITHM'. Please refer to the Xpress Knitro manual for the description of the Knitro controls.



### Chapter 21 Library functions and the programming interface


#### Section 21.1 Counting


All Xpress NonLinear entities are numbered from 1. The 0<sup>th</sup> item is defined, and is an empty entity of the appropriate type. Therefore, whenever an Xpress NonLinear function returns a zero value, it means that there is no data of that type.

In parsed and unparsed function arrays, types `XSLP_COL` and `XSLP_ROW` use indices counted from zero, the same as the Xpress Optimizer library.

#### Section 21.2 The Xpress NonLinear problem pointer


Xpress NonLinear uses the same concept as the Optimizer library, with a "pointer to a problem". The optimizer problem must be initialized first in the normal way. Then the corresponding Xpress NonLinear problem must be initialized, including a pointer to the underlying optimizer problem. For example:

```
{
	...
	XPRSprob prob=NULL;
	XSLPprob SLPprob=NULL;

	XPRSinit("");
	XSLPinit();
	XPRScreateprob(&prob);
	XSLPcreateprob(&SLPprob,&prob);
	...
}
```


At the end of the program, the Xpress NonLinear problem should be destroyed. You are responsible for destroying the underlying XPRSprob linear problem afterwards. For example:

```
{
...
  XSLPdestroyprob(SLPprob);
  XPRSdestroyprob(prob);
  XSLPfree();
  XPRSfree();
  ...
}
```


The following functions are provided to manage Xpress NonLinear problems. See the documentation below on the individual functions for more details.

`XSLPcopycontrols` `(XSLPprob prob1, XSLPprob prob2)`

  Copy the settings of control variables

`XSLPcopycallbacks` `(XSLPprob prob1, XSLPprob prob2)`

  Copy the callback settings

`XSLPcopyprob` `(XSLPprob prob1, XSLPprob prob2, char *ProbName)`

  Copy a problem completely

`XSLPcreateprob` `(XSLPprob *prob1, XPRSprob *prob2)`

  Create an Xpress NonLinear problem

`XSLPdestroyprob` `(XSLPprob prob1)`

  Delete an Xpress NonLinear problem from memory

`XSLPrestore` `(XSLPprob prob1)`

  Restore Xpress NonLinear data structures from file

`XSLPsave` `(XSLPprob prob1)`

  Save Xpress NonLinear data structures to file

#### Section 21.3 The `load` functions


The `load` functions can be used to load an Xpress NonLinear problem directly into the Xpress data structures. Because there are so many additional items which can be loaded apart from the basic \(linear\) matrix, the loading process is divided into several functions.

The best practice is to load the linear part of the problem irst, using the normal Optimizer Library functions `XPRSloadlp` or `XPRSloadmip`. Then the appropriate parts of the Xpress NonLinear problem can be loaded. After all the `load` functions have been called, `XSLPconstruct` should be called to create the SLP matrix and data structures. If `XSLPconstruct` is not invoked before a call to one of the Xpress NonLinear optimization routines, then it will be called by the optimization routine itself.

All of these functions initialize their data areas. Therefore, if a second call is made to the same function for the same problem, the previous data will be deleted. If you want to include additional data of the same type, then use the corresponding `add` function.

It is possible to remove parts of the SLP strcutures with the various `XSLPdel` functions, and `XSLPunconstruct` can also be used to remove the augmentation.

Xpress NonLinear is compatible with the Xpress quadratic programming optimizer. `XPRSloadqp` and `XPRSloadmiqp` can be used to load quadratic problems \(or quadratically constrained problmes using `XPRSloadqcqp` and `XPRSloadmiqcqp`\). The quadratic objective will be optimized using the Xpress quadratic optimizer; the nonlinear constraints will be handled with the normal SLP procedures. Please note, that this separation is only useful for a convex quadratic objective and convex quadratic inequality constraints. All nonconvex quadratic matrices should be handled as SLP strctures.

For a description on when it's more beneficial to use the XPRS library to solve QP or QCQP problems, please see  _Selecting the right algorithm for a nonlinear problem - when to use the XPRS library instead of XSLP_.

#### Section 21.4 Library functions


A large number of routines are available for Library users of Xpress NonLinear, ranging from simple routines for the input and solution of problems from matrix files to sophisticated callback functions and greater control over the solution process. Library users have access to a set of functions providing advanced control over their program's interaction with the SLP module and catering for more complicated problem development. When called from the SLP library, these functions have an `XSLP` prefix and take an SLP problem as their first argument. They are also exported to the XPRS library, where they can be called on an XPRSprob without having to explicitly create an XSLPprob first.

_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRSaddcbmsjobend` | Add a user callback to be called every time a new multistart job finishes. | Callback, Multistart
`XPRSaddcbmsjobstart` | Add a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied | Callback, Multistart
`XPRSaddcbmswinner` | Add a user callback to be called every time a multistart winner has been declared | Callback, Multistart
`XPRSaddcbnlpcoefevalerror` | Add a user callback to be called when an evaluation of a coefficient fails during the solve | Callback, Numerics
`XPRSaddcbslpcascadeend` | Add a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadestart` | Add a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevar` | Add a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XPRSaddcbslpcascadevarfail` | Add a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XPRSaddcbslpconstruct` | Add a user callback to be called during the Xpress-SLP augmentation process | Callback, SLP
`XPRSaddcbslpdrcol` | Add a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XPRSaddcbslpintsol` | Add a user callback to be called during MISLP when an integer solution is obtained | Callback, MISLP
`XPRSaddcbslpiterend` | Add a user callback to be called at the end of each SLP iteration | Callback, SLP
`XPRSaddcbslpiterstart` | Add a user callback to be called at the start of each SLP iteration | Callback, SLP
`XPRSaddcbslpitervar` | Add a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XPRSaddcbslppreupdatelinearization` | Add a user callback to be called before the linearization is updated | Callback, SLP
`XPRSnlpchgformulastr` | Add or replace a single matrix formula using a character string for the formula. | Problem Modification
`XPRSnlpgetformulastr` | Retrieve a single matrix formula in a character string. | Problem Information
`XPRSremovecbmsjobend` | Removes a callback function previously added by `XPRSaddcbmsjobend`. | Callback, Multistart
`XPRSremovecbmsjobstart` | Removes a callback function previously added by `XPRSaddcbmsjobstart`. | Callback, Multistart
`XPRSremovecbmswinner` | Removes a callback function previously added by `XPRSaddcbmswinner`. | Callback, Multistart
`XPRSremovecbnlpcoefevalerror` | Removes a callback function previously added by `XPRSaddcbnlpcoefevalerror`. | Callback, Numerics
`XPRSremovecbslpcascadeend` | Removes a callback function previously added by `XPRSaddcbslpcascadeend`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadestart` | Removes a callback function previously added by `XPRSaddcbslpcascadestart`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevar` | Removes a callback function previously added by `XPRSaddcbslpcascadevar`. | Callback, Cascading, SLP
`XPRSremovecbslpcascadevarfail` | Removes a callback function previously added by `XPRSaddcbslpcascadevarfail`. | Callback, Cascading, SLP
`XPRSremovecbslpconstruct` | Removes a callback function previously added by `XPRSaddcbslpconstruct`. | Callback, SLP
`XPRSremovecbslpdrcol` | Removes a callback function previously added by `XPRSaddcbslpdrcol`. | Callback, Cascading, SLP
`XPRSremovecbslpintsol` | Removes a callback function previously added by `XPRSaddcbslpintsol`. | Callback, MISLP
`XPRSremovecbslpiterend` | Removes a callback function previously added by `XPRSaddcbslpiterend`. | Callback, SLP
`XPRSremovecbslpiterstart` | Removes a callback function previously added by `XPRSaddcbslpiterstart`. | Callback, SLP
`XPRSremovecbslpitervar` | Removes a callback function previously added by `XPRSaddcbslpitervar`. | Callback, SLP, SLP-convergence
`XPRSremovecbslppreupdatelinearization` | Removes a callback function previously added by `XPRSaddcbslppreupdatelinearization`. | Callback, SLP
`XPRSslpchgcoefstr` | Add or change a single matrix coefficient using a character string for the formula. | Problem Modification, SLP
`XPRSslpgetcoefstr` | Retrieve a single matrix coefficient as a formula in a character string. | Problem Information, SLP
`XSLPaddcoefs, XPRSslpaddcoefs` | Add non-linear coefficients to the SLP problem. | Problem Modification, SLP
`XSLPaddformulas, XPRSnlpaddformulas` | Add non-linear formulas to the SLP problem. | Problem Modification
`XSLPadduserfunction, XPRSnlpadduserfunction` | Add user function definitions to an SLP problem. | User Functions
`XSLPcalcslacks, XPRSnlpcalcslacks` | Calculate the slack values for the provided solution in the non-linear problem | Solution
`XSLPcascade, XPRSslpcascade` | Re-calculate consistent values for SLP variables based on the current values of the remaining variables. | Cascading, SLP, Solution Process
`XSLPcascadeorder, XPRSslpcascadeorder` | Establish a re-calculation sequence for SLP variables with determining rows. | Data Input, SLP
`XSLPchgcascadenlimit, XPRSslpchgcascadenlimit` | Set a variable specific cascade iteration limit | Data Input, SLP
`XSLPchgcoef, XPRSslpchgcoef` | Add or change a single matrix coefficient using a parsed or unparsed formula. | Problem Modification, SLP
`XSLPchgdeltatype, XPRSslpchgdeltatype` | Changes the type of the delta assigned to a nonlinear variable | Problem Modification, SLP
`XSLPchgformula, XPRSnlpchgformula` | Add or replace a single matrix formula using a parsed or unparsed formula | Problem Modification
`XSLPchgrowstatus, XPRSslpchgrowstatus` | Change the status setting of a constraint | Bit-vector, Data Input, SLP
`XSLPchgrowwt, XPRSslpchgrowwt` | Set or change the initial penalty error weight for a row | Data Input, SLP
`XSLPconstruct, XPRSslpconstruct` | Create the full augmented SLP matrix and data structures, ready for optimization | SLP, Solution Process
`XSLPcopycallbacks` | Copy the user-defined callbacks from one SLP problem to another | Callback
`XSLPcopycontrols` | Copy the values of the control variables from one SLP problem to another | Controls and Attributes
`XSLPcopyprob` | Copy an existing SLP problem to another | Problem Creation
`XSLPcreateprob` | Create a new SLP problem | Problem Creation
`XSLPdelcoefs, XPRSslpdelcoefs` | Delete coefficients from the current problem. | Problem Modification, SLP
`XSLPdelformulas, XPRSnlpdelformulas` | Delete nonlinear formulas from the current problem | Problem Modification
`XSLPdeluserfunction, XPRSnlpdeluserfunction` | Delete a user function from the current problem | User Functions
`XSLPdestroyprob` | Delete an SLP problem and release all the associated memory | Problem Creation
`XSLPevaluatecoef, XPRSslpevaluatecoef` | Evaluate a coefficient using the current values of the variables | Solution
`XSLPevaluateformula, XPRSnlpevaluateformula` | Evaluate a formula using the current values of the variables | Solution
`XSLPfixpenalties, XPRSslpfixpenalties` | Fixe the values of the error vectors | Solution Process
`XSLPfree` | Free any memory allocated by Xpress NonLinear and close any open Xpress NonLinear files | Licensing
`XSLPgetcoefformula, XPRSslpgetcoefformula` | Retrieve a single matrix coefficient as a formula split into tokens. | Problem Information, SLP
`XSLPgetcoefs, XPRSslpgetcoefs` | Retrieve the list of positions of the nonlinear coefficients in the problem. | Problem Information, SLP
`XSLPgetcolinfo, XPRSslpgetcolinfo` | Get current column information. | SLP, Solution
`XSLPgetdblattrib` | Retrieve the value of a double precision problem attribute | Controls and Attributes
`XSLPgetdblcontrol` | Retrieve the value of a double precision problem control | Controls and Attributes
`XSLPgetformula, XPRSnlpgetformula` | Retrieve a single matrix formula as a formula split into tokens. | Problem Information
`XSLPgetformularows, XPRSnlpgetformularows` | Retrieve the list of positions of the nonlinear formulas in the problem | Problem Information
`XSLPgetindex` | Retrieve the index of an Xpress NonLinear entity with a given name | Problem Information, User Functions
`XSLPgetintattrib` | Retrieve the value of an integer problem attribute | Controls and Attributes
`XSLPgetintcontrol` | Retrieve the value of an integer problem control | Controls and Attributes
`XSLPgetlasterror` | Retrieve the error message corresponding to the last Xpress NonLinear error during an SLP run | Misc
`XSLPgetptrattrib` | Retrieve the value of a problem pointer attribute | Controls and Attributes
`XSLPgetrowinfo, XPRSslpgetrowinfo` | Get current row information. | SLP, Solution
`XSLPgetrowstatus, XPRSslpgetrowstatus` | Retrieve the status setting of a constraint | Bit-vector, SLP, Solution
`XSLPgetrowwt, XPRSslpgetrowwt` | Get the initial penalty error weight for a row | Data Information, SLP
`XSLPgetstrattrib` | Retrieve the value of a string problem attribute | Controls and Attributes
`XSLPgetstrcontrol` | Retrieve the value of a string problem control | Controls and Attributes
`XSLPimportlibfunc, XPRSnlpimportlibfunc` | Imports a function from a library file to be called as a user function | User Functions
`XSLPinit` | Initializes the Xpress NonLinear system | Licensing
`XSLPinterrupt` | Interrupts the current SLP optimization | Solution Process
`XSLPitemname` | Retrieves the name of an Xpress NonLinear entity or the value of a function token as a character string. | Names Manager
`XSLPloadcoefs, XPRSslploadcoefs` | Load non-linear coefficients into the SLP problem. | Problem Information, SLP
`XSLPloadformulas, XPRSnlploadformulas` | Load non-linear formulas into the SLP problem | Problem Information
`XSLPmsaddcustompreset, XPRSmsaddcustompreset` | A combined version of XSLPmsaddjob and XSLPmsaddpreset. | Data Input, Multistart
`XSLPmsaddjob, XPRSmsaddjob` | Adds a multistart job to the multistart pool | Data Input, Multistart
`XSLPmsaddpreset, XPRSmsaddpreset` | Loads a preset of jobs into the multistart job pool. | Data Input, Multistart
`XSLPmsclear, XPRSmsclear` | Removes all scheduled jobs from the multistart job pool | Multistart
`XSLPnlpoptimize, XPRSnlpoptimize` | Maximize or minimize an SLP problem | Solution Process
`XSLPpostsolve, XPRSnlppostsolve` | Restores the problem to its pre-solve state | Presolve
`XSLPpresolve` | Perform a nonlinear presolve on the problem | Presolve
`XSLPprintevalinfo, XPRSnlpprintevalinfo` | Print a summary of any evaluation errors that may have occurred during solving a problem | Logging
`XSLPprintmemory` | Print the dimensions and memory allocations for a problem | Logging
`XSLPreadprob` | Read an Xpress NonLinear extended MPS format matrix from a file into an SLP problem | File IO, Problem Creation
`XSLPreinitialize, XPRSslpreinitialize` | Reset the SLP problem to match a just augmented system | SLP, Solution Process
`XSLPrestore` | Restore the Xpress NonLinear problem from a file created by `XSLPsave` | File IO, Save Restore
`XSLPsave` | Save the Xpress NonLinear problem to file | File IO, Save Restore
`XSLPsaveas` | Save the Xpress NonLinear problem to a named file | File IO, Save Restore
`XSLPscaling` | Analyze the current matrix for largest/smallest coefficients and ratios | Numerics
`XSLPsetcbcascadeend, XPRSsetcbslpcascadeend` | Set a user callback to be called at the end of the cascading process, after the last variable has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadestart, XPRSsetcbslpcascadestart` | Set a user callback to be called at the start of the cascading process, before any variables have been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevar, XPRSsetcbslpcascadevar` | Set a user callback to be called after each column has been cascaded | Callback, Cascading, SLP
`XSLPsetcbcascadevarfail, XPRSsetcbslpcascadevarfail` | Set a user callback to be called after cascading a column was not successful | Callback, Cascading, SLP
`XSLPsetcbcoefevalerror, XPRSsetcbnlpcoefevalerror` | Set a user callback to be called when an evaluation of a coefficient fails during the solve | Callback, Numerics
`XSLPsetcbconstruct, XPRSsetcbslpconstruct` | Set a user callback to be called during the Xpress-SLP augmentation process | Callback, SLP
`XSLPsetcbdestroy` | Set a user callback to be called when an SLP problem is about to be destroyed | Callback
`XSLPsetcbdrcol, XPRSsetcbslpdrcol` | Set a user callback used to override the update of variables with small determining column | Callback, Cascading, SLP
`XSLPsetcbintsol, XPRSsetcbslpintsol` | Set a user callback to be called during MISLP when an integer solution is obtained | Callback, MISLP
`XSLPsetcbiterend, XPRSsetcbslpiterend` | Set a user callback to be called at the end of each SLP iteration | Callback, SLP
`XSLPsetcbiterstart, XPRSsetcbslpiterstart` | Set a user callback to be called at the start of each SLP iteration | Callback, SLP
`XSLPsetcbitervar, XPRSsetcbslpitervar` | Set a user callback to be called after each column has been tested for convergence | Callback, SLP, SLP-convergence
`XSLPsetcbmessage` | Set a user callback to be called whenever Xpress NonLinear outputs a line of text according to `XSLP_ECHOXPRSMESSAGES`. | Callback, Logging
`XSLPsetcbmsjobend, XPRSsetcbmsjobend` | Set a user callback to be called every time a new multistart job finishes. | Callback, Multistart
`XSLPsetcbmsjobstart, XPRSsetcbmsjobstart` | Set a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied | Callback, Multistart
`XSLPsetcbmswinner, XPRSsetcbmswinner` | Set a user callback to be called every time a multistart winner has been declared | Callback, Multistart
`XSLPsetcboptnode` | Set a user callback to be called during MISLP when an optimal SLP solution is obtained at a node | Callback, MISLP
`XSLPsetcbprenode` | Set a user callback to be called during MISLP after the set-up of the SLP problem to be solved at a node, but before SLP optimization | Callback, MISLP
`XSLPsetcbpresolved` | Set a user callback to be called after the nonlinear presolver has been applied. | Callback, SLP
`XSLPsetcbpreupdatelinearization, XPRSsetcbslppreupdatelinearization` | Set a user callback to be called before the linearization is updated | Callback, SLP
`XSLPsetcbslpend` | Set a user callback to be called at the end of the SLP optimization | Callback, SLP
`XSLPsetcbslpnode` | Set a user callback to be called during MISLP after the SLP optimization at each node. | Callback, MISLP
`XSLPsetcbslpstart` | Set a user callback to be called at the start of the SLP optimization | Callback, SLP
`XSLPsetcurrentiv, XPRSnlpsetcurrentiv` | Transfer the current solution to initial values | Data Input
`XSLPsetdblcontrol` | Set the value of a double precision problem control | Controls and Attributes
`XSLPsetdefaultcontrol` | Set the values of one SLP control to its default value | Controls and Attributes
`XSLPsetdefaults` | Set the values of all SLP controls to their default values | Controls and Attributes
`XSLPsetdetrow, XPRSslpsetdetrow` | Set the determining row of a variable | Cascading, Data Input, SLP
`XSLPsetfunctionerror, XPRSnlpsetfunctionerror` | Set the function error flag for the problem | Misc
`XSLPsetinitstepbounds, XPRSslpsetinitstepbounds` | Set the initial step bounds of columns | Data Input
`XSLPsetinitval, XPRSnlpsetinitval` | Set the initial value of columns | Data Input
`XSLPsetintcontrol` | Set the value of an integer problem control | Controls and Attributes
`XSLPsetlogfile` | Define an output file to be used to receive messages from Xpress NonLinear | File IO, Logging
`XSLPsetparam` | Set the value of a control parameter by name | Controls and Attributes
`XSLPsetstrcontrol` | Set the value of a string problem control | Controls and Attributes
`XSLPunconstruct, XPRSslpunconstruct` | Removes the augmentation and returns the problem to its pre-linearization state | SLP, Solution Process
`XSLPupdatelinearization, XPRSslpupdatelinearization` | Updates the current linearization | SLP, Solution Process
`XSLPvalidate, XPRSnlpvalidate` | Validate the feasibility of constraints in a converged solution | Solution
`XSLPvalidatekkt, XPRSnlpvalidatekkt` | Validates the first order optimality conditions also known as the Karush-Kuhn-Tucker \(KKT\) conditions versus the currect solution | Solution
`XSLPvalidateprob, XPRSnlpvalidateprob` | Validates the current problem formulation and statement | Solution
`XSLPvalidaterow, XPRSnlpvalidaterow` | Prints an extensive analysis on a given constraint of the SLP problem | Solution
`XSLPvalidatevector, XPRSnlpvalidatevector` | Validate the feasibility of constraints for a given solution | Solution
`XSLPwriteprob` | Write the current problem to a file in extended MPS or text format | File IO, Problem Information
`XSLPwriteslxsol` | Write the current solution to an MPS like file format | File IO, Solution

#### XPRSaddcbmsjobend

_**Purpose:**_

   Add a user callback to be called every time a new multistart job finishes. Can be used to overwrite the default solution ranking function

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbmsjobend(XPRSprob prob,
int (XPRS_CC *msjobend)(XPRSprob cbprob, void *cbdata, void  *jobdata, const char *jobdesc, int *p_status),
void *data, int priority);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`msjobend` | The function to be called when a multistart job finishes 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbmsjobend`. 
`jobdata` | Job specific user-defined object, as specified by the multistart job creating API functions. 
`jobdesc` | The description of the problem as specified by the multistart job creating API functions. 
`p_status` | 
User return status variable:

0 - use the default evaluation of the finished job

1 - disregard the result and continue

2 - stop the multistart search
 
`data` | User data passed to the callback function. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
The multistart pool is dynamic, and this callback can be used to load new multistart jobs using the normal API functions.

_**Related topics:**_
`XPRSaddcbmsjobstart`, `XPRSaddcbmswinner` `XPRSremovecbmsjobend`

#### XPRSaddcbmsjobstart

_**Purpose:**_

   Add a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbmsjobstart(XPRSprob prob, int (XPRS_CC *msjobstart)(XPRSprob cbprob,
void *cbdata,void  *jobdata,const char *jobdesc,int *p_status), void *data, int priority);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`msjobstart` | The function to be called when a new multistart job is created 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbmsjobstart`. 
`jobdata` | Job specific user-defined object, as specified by the multistart job creating API functions. 
`jobdesc` | The description of the problem as specified by the multistart job creating API functions. 
`p_status` | 
User return status variable:

0 - normal return, solve the job,

1 - disregard this job and continue,

2 - Stop multistart.
 
`data` | User data passed to the callback function. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
All mulit-start jobs operate on an independent copy of the original problem, and any modification to the problem is allowed, including structural changes. Please note, however, that any modification will be carried over to the base problem, should a modified problem be declared the winner problem.

_**Related topics:**_
`XPRSaddcbmsjobend`, `XPRSaddcbmswinner` `XPRSremovecbmsjobstart`

#### XPRSaddcbmswinner

_**Purpose:**_

   Add a user callback to be called every time a multistart winner has been declared

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbmswinner(XPRSprob prob, int (XPRS_CC *mswinner)(XPRSprob cbprob,
void *cbdata,void  *jobdata,const char *jobdesc), void *data, int priority);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`mswinner` | The function to be called when a multistart winner is declared. The return code is used to indicate whether callbacks should be copied over from the winner \( `≠ 0`\) or not \( `0`\). 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbmswinner`. 
`jobdata` | Job specific user-defined object, as specified by the multistart job creating API functions. 
`jobdesc` | The description of the problem as specified by the multistart job creating API functions. 
`data` | User data passed to the callback function. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Related topics:**_
`XPRSaddcbmsjobstart`, `XPRSaddcbmsjobend` `XPRSremovecbmswinner`

#### XPRSaddcbnlpcoefevalerror

_**Purpose:**_

   Add a user callback to be called when an evaluation of a coefficient fails during the solve

_**Topic areas:**_ 
Callback, Numerics

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbnlpcoefevalerror(XPRSprob prob,
int (XPRS_CC *nlpcoefevalerror) (XPRSprob cbprob, void *cbdata, int row, int col),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`nlpcoefevalerror` | The function to be called when an evaluation fails. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbnlpcoefevalerror`. 
`row` | The row position of the coefficient. 
`col` | The column position of the coefficient. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `nlpcoefevalerror` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
This callback can be used to capture when an evaluation of a coefficient fails. The callback is called only once for each coefficient.

_**Related topics:**_
`XPRSnlpprintevalinfo` `XPRSremovecbnlpcoefevalerror`

#### XPRSaddcbslpcascadeend

_**Purpose:**_

   Add a user callback to be called at the end of the cascading process, after the last variable has been cascaded

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpcascadeend(XPRSprob prob,
int (XPRS_CC *slpcascadeend) (XPRSprob cbprob, void *cbdata),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadeend` | The function to be called at the end of the cascading process. `slpcascadeend` returns an integer value. If the return value is nonzero, the SLP iterations will stop. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpcascadeend`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpcascadeend` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed at the end of the cascading process which checks if any of the values have been changed significantly:

```
double *cSol;
XPRSaddcbslpcascadeend(prob, CBCascEnd, &cSol, 0);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBCascEnd(XPRSprob MyProb, void *Obj) {
  int iCol, nCol;
  double *cSol, Value;
  cSol = * (double **) Obj;
  XPRSgetintcontrol(MyProb, XPRS_COLS, &nCol);
  for (iCol=0;iCol<nCol;iCol++) {
    XPRSalltype alltype;
    XPRSslpgetcolinfo(prob, XSLP_COLINFO_VALUE, iCol, &alltype);
    Value = alltype.value.real;
    if (fabs(Value-cSol[iCol]) > .01)
      printf("\nCol %d changed from %lg to %lg",
             iCol, cSol[iCol], Value);
  }
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we assume has been populated with the original solution values.

_**Further information:**_
This callback can be used at the end of the cascading, when all the solution values have been recalculated.

_**Related topics:**_
`XPRSslpcascade`, `XPRSaddcbslpcascadestart`, `XPRSaddcbslpcascadevar`, `XPRSaddcbslpcascadevarfail` `XPRSremovecbslpcascadeend`

#### XPRSaddcbslpcascadestart

_**Purpose:**_

   Add a user callback to be called at the start of the cascading process, before any variables have been cascaded

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpcascadestart(XPRSprob prob,
int (XPRS_CC *slpcascadestart) (XPRSprob cbprob, void *cbdata),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadestart` | The function to be called at the start of the cascading process. `slpcascadestart` returns an integer value. If the return value is nonzero, the cascading process will be omitted for the current SLP iteration, but the optimization will continue. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpcascadestart`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpcascadestart` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed at the start of the cascading process to save the current values of the variables:

```
double *cSol;
XPRSaddcbslpcascadestart(prob, CBCascStart, &cSol, 0);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBCascStart(XPRSprob MyProb, void *Obj) {
  int iCol, nCol;
  double *cSol;
  cSol = * (double **) Obj;
  XPRSgetintcontrol(MyProb, XPRS_COLS, &nCol);
  for (iCol=0;iCol<nCol;iCol++) {
    XPRSalltype alltype;
    XPRSslpgetcolinfo(prob, XSLP_COLINFO_VALUE, iCol, &alltype);
    cSol[iCol] = alltype.value.real;
  }
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we populate with the solution values.

_**Further information:**_
This callback can be used at the start of the cascading, before any of the solution values have been recalculated.

_**Related topics:**_
`XPRSslpcascade`, `XPRSaddcbslpcascadeend`, `XPRSaddcbslpcascadevar`, `XPRSaddcbslpcascadevarfail` `XPRSremovecbslpcascadestart`

#### XPRSaddcbslpcascadevar

_**Purpose:**_

   Add a user callback to be called after each column has been cascaded

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpcascadevar(XPRSprob prob,
int (XPRS_CC *slpcascadevar) (XPRSprob cbprob, void *cbdata, int col),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadevar` | The function to be called after each column has been cascaded. `slpcascadevar` returns an integer value. If the return value is nonzero, the cascading process will be omitted for the remaining variables during the current SLP iteration, but the optimization will continue. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpcascadevar`. 
`col` | The number of the column which has been cascaded. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpcascadevar` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed after each variable has been cascaded:

```
double *cSol;
XPRSaddcbslpcascadevar(prob, CBCascVar, &cSol, 0);
```
 The following sample callback function stops the cascading process if the cascaded value is of the opposite sign to the original value:

```
int XPRS_CC CBCascVar(XPRSprob MyProb, void *Obj, int iCol) {
  XPRSalltype alltype;
  double *cSol;
  cSol = * (double **) Obj;
  XPRSslpgetcolinfo(MyProb, XSLP_COLINFO_VALUE, iCol, &alltype);
  if (alltype.value.real * cSol[iCol] < 0) {
    return 1;
  }
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we assume has been populated with the original solution values.

_**Further information:**_
This callback can be used after each variable has been cascaded and its new value has been calculated.

_**Related topics:**_
`XPRSslpcascade`, `XPRSaddcbslpcascadeend`, `XPRSaddcbslpcascadestart`, `XPRSaddcbslpcascadevarfail` `XPRSremovecbslpcascadevar`

#### XPRSaddcbslpcascadevarfail

_**Purpose:**_

   Add a user callback to be called after cascading a column was not successful

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpcascadevarfail(XPRSprob prob,
int (XPRS_CC *slpcascadevarfail) (XPRSprob cbprob, void *cbdata, int col),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadevarfail` | The function to be called after cascading a column was not successful. `slpcascadevarfail` returns an integer value. If the return value is nonzero, the cascading process will be omitted for the remaining variables during the current SLP iteration, but the optimization will continue. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpcascadevarfail`. 
`col` | The number of the column which has been cascaded. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpcascadevarfail` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Related topics:**_
`XPRSslpcascade`, `XPRSaddcbslpcascadeend`, `XPRSaddcbslpcascadestart`, `XPRSaddcbslpcascadevar` `XPRSremovecbslpcascadevarfail`

#### XPRSaddcbslpconstruct

_**Purpose:**_

   Add a user callback to be called during the Xpress-SLP augmentation process

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpconstruct(XPRSprob prob,
int (XPRS_CC *slpconstruct) (XPRSprob cbprob, void *cbdata),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpconstruct` | The function to be called during problem augmentation. `slpconstruct` returns an integer value. See below for an explanation of the values. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpconstruct`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpconstruct` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed during the Xpress-SLP problem augmentation:

```
double *cValue;
cValue = NULL;
XPRSaddcbslpconstruct(prob, CBConstruct, &cValue, 0);
```
 The following sample callback prints information about the number of rows and columns in the augmented problem.

```
int XPRS_CC CBConstruct(XPRSprob MyProb, void *Obj) {
  int ncol;
  int nrow;
  XPRSgetintattrib(MyProb, XPRS_COLS, &ncol);
  XPRSgetintattrib(MyProb, XPRS_ROWS, &nrow);
  printf("The augmented problem has %i rows and %i columns\n", nrow, ncol);
  return 0;
}
```
 
_**Further information:**_
1. This callback can be used during the problem augmentation, generally \(although not exclusively\) to change the initial values for the variables.
2. The following return codes are accepted:
 * `0`: Normal return: augmentation continues
 * `-1`: Return to recalculate matrix values
 * `-2`: Return to recalculate row weights and matrix entries
 * `other`: Error return: augmentation terminates, `XPRSslpconstruct` terminates with a nonzero error code.
3. The return values -1 and -2 will cause the callback to be called a second time after the matrix has been recalculated. It is the responsibility of the callback to ensure that it does ultimately exit with a return value of zero.

_**Related topics:**_
`XPRSslpconstruct` `XPRSremovecbslpconstruct`

#### XPRSaddcbslpdrcol

_**Purpose:**_

   Add a user callback used to override the update of variables with small determining column

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpdrcol(XPRSprob prob,
int (XPRS_CC *slpdrcol) (XPRSprob cbprob, void *data, int col, int detcol, double detval, double * p_value, double lb, double ub),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpdrcol` | The function to be called during cascading for each variable with a determining column `slpdrcol` returns an integer value. If the return value is positive, it will indicate that the value has been fixed, and cascading should be omitted for the variable. A negative value indicates that a previously fixed value has been relaxed. If no action is taken, a 0 return value should be used. 
`cbprob` | The problem passed to the callback function. 
`data` | The user-defined object passed as `data` to `XPRSaddcbslpcascadevar`. 
`col` | The index of the column for which the determining columns is checked. 
`detcol` | The index of the determining column for the column that is being updated. 
`detval` | The value of the determining column in the current SLP iteration. 
`p_value` | Used to return the new value for column `col`, should it need to be updated, in which case the callback must return a positive result to indicate that this value should be used. 
`lb` | The original lower bound of column `col`. The callback provides this value as a reference, should the bound be updated or changed during the solution process. 
`ub` | The original upper bound of column `col`. The callback provides this value as a reference, should the bound be updated or changed during the solution process. 
`data` | A user-defined object, which can be used for any purpose. by the function. `data` is passed to `slpdrcol` as `data`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
If set, this callback is called as part of the cascading procedure. Please see Chapter _Cascading_for more information.

_**Related topics:**_
`XSLP_DRCOLTOL`, `XPRSslpcascade`, `XPRSaddcbslpcascadeend`, `XPRSaddcbslpcascadestart` `XPRSremovecbslpdrcol`

#### XPRSaddcbslpintsol

_**Purpose:**_

   Add a user callback to be called during MISLP when an integer solution is obtained

_**Topic areas:**_ 
Callback, MISLP

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpintsol(XPRSprob prob,
int (XPRS_CC *slpintsol) (XPRSprob cbprob, void *cbdata),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpintsol` | The function to be called when an integer solution is obtained. `slpintsol` returns an integer value. At present, the return value is ignored. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpintsol`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpintsol` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed whenever an integer solution is found during MISLP:

```
double *cSol;
int nInputCol;
XPRSgetintattrib(prob, XPRS_INPUTCOLS, &nInputCol);
cSol = (double*)malloc(nInputCol * sizeof(double));
XPRSaddcbslpintsol(prob, CBIntSol, &cSol, 0);
```
 The following sample callback function saves the solution values for the integer solution just found:

```
int XPRS_CC CBIntSol(XPRSprob MyProb, void *Obj) {
  XPRSprob MyProb;
  int nInputCol;
  int solStatus;
  double *cSol;

  cSol = * (double **) Obj;
  XPRSgetintattrib(MyProb, XPRS_INPUTCOLS, &nInputCol);
  XPRSgetsolution(MyProb, &solStatus, cSol, 0, nInputCol-1);
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`.

_**Further information:**_
This callback must be used during MISLP instead of the `XPRSsetcbintsol`callback which is used for MIP problems.

_**Further information:**_
Note that for SLP-MIP-SLP \(see`XSLP_MIPALGORITHM`\), the slpintsol callback will only be fired once after the second SLP solve terminated, in which case the solution can also only be queried via `XPRSgetsolution`but not via `XPRSgetlpsol`\(unless postsolve is disabled\).

_**Related topics:**_
`XSLPsetcboptnode`, `XPRSremovecbslpintsol`

#### XPRSaddcbslpiterend

_**Purpose:**_

   Add a user callback to be called at the end of each SLP iteration

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpiterend(XPRSprob prob,
int (XPRS_CC *slpiterend) (XPRSprob cbprob, void *cbdata),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpiterend` | The function to be called at the end of each SLP iteration. `slpiterend` returns an integer value. If the return value is nonzero, the SLP iterations will stop. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpiterend`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpiterend` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed at the end of each SLP iteration. It records the number of LP iterations in the latest optimization and stops if there were fewer than 10:

```
XPRSaddcbslpiterend(prob, CBIterEnd, NULL, 0);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBIterEnd(XPRSprob MyProb, void *Obj) {
  int nIter;
  XPRSprob MyProb;
  XPRSgetintattrib(MyProb, XPRS_SIMPLEXITER, &nIter);
  if (nIter < 10) return 1;
  return 0;
}
```
 The `data`argument is not used here, and so is passed as `NULL`.

_**Further information:**_
This callback can be used at the end of each SLP iteration to carry out any further processing and/or stop any further SLP iterations.

_**Related topics:**_
`XPRSaddcbslpiterstart`, `XPRSaddcbslpitervar` `XPRSremovecbslpiterend`

#### XPRSaddcbslpiterstart

_**Purpose:**_

   Add a user callback to be called at the start of each SLP iteration

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpiterstart(XPRSprob prob,
int (XPRS_CC *slpiterstart) (XPRSprob cbprob, void *cbdata),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpiterstart` | The function to be called at the start of each SLP iteration. `slpiterstart` returns an integer value. If the return value is nonzero, the SLP iterations will stop. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslpiterstart`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpiterstart` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed at the start of the optimization to save to save the values of the variables from the previous iteration:

```
double *cSol;
XPRSaddcbslpiterstart(prob, CBIterStart, &cSol, 0);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBIterStart(XPRSprob MyProb, void *Obj) {
  XPRSprob MyProb;
  double *cSol;
  int nIter;
  cSol = * (double **) Obj;
  XPRSgetintattrib(MyProb, XSLP_ITER, &nIter);
  if (nIter == 0) return 0; /* no previous solution */
  XPRSgetlpsol(MyProb, cSol, NULL, NULL, NULL);
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we populate with the solution values.

_**Further information:**_
This callback can be used at the start of each SLP iteration before the optimization begins.

_**Related topics:**_
`XPRSaddcbslpiterend`, `XPRSaddcbslpitervar` `XPRSremovecbslpiterstart`

#### XPRSaddcbslpitervar

_**Purpose:**_

   Add a user callback to be called after each column has been tested for convergence

_**Topic areas:**_ 
Callback, SLP, SLP-convergence

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslpitervar(XPRSprob prob,
int (XPRS_CC *slpitervar) (XPRSprob cbprob, void *cbdata, int col),
void *data, int priority);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current problem. 
`slpitervar` |  | The function to be called after each column has been tested for convergence. `slpitervar`returns an integer value. The return value is interpreted as a convergence status. The possible values are:
&nbsp; | `< 0` | The variable has not converged;
&nbsp; | `0` | Keep the internal convergence status;
&nbsp; | `1 to 10` | The column has converged on a system-defined convergence criterion \(these values should not normally be returned\);
&nbsp; | `> 10` | The variable has converged on user criteria.
`cbprob` | | The problem passed to the callback function. 
`cbdata` | | The user-defined object passed as `data` to `XPRSaddcbslpitervar`. 
`col` | | The number of the column which has been tested for convergence. 
`data` | | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpitervar` as `cbdata`. 
`priority` | | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Example:**_
The following example sets up a callback to be executed after each variable has been tested for convergence. The user object `Important`is an integer array which has already been set up and holds a flag for each variable indicating whether it is important that it converges.

```
int *Important;
XPRSaddcbslpitervar(prob, CBIterVar, &Important, 0);
```
 The following sample callback function tests if the variable is already converged. If not, then it checks if the variable is important. If it is not important, the function returns a convergence status of 99.

```
int XPRS_CC CBIterVar(XPRSprob MyProb, void *Obj, int iCol) {
  int *Important, Converged;
  Important = *(int **) Obj;
  XPRSalltype alltype;
  XPRSslpgetcolinfo(MyProb, XSLP_COLINFO_CONVERGENCESTATUS, iCol, &alltype);
  if (alltype.value.integer != 0) return 0;
  if (!Important[iCol]) return 99;
  return -1;
}
```
 The `data`argument is used here to hold the address of the array `Important`.

_**Further information:**_
This callback can be used after each variable has been checked for convergence, and allows the convergence status to be reset if required.

_**Related topics:**_
`XPRSaddcbslpiterend`, `XPRSaddcbslpiterstart` `XPRSremovecbslpitervar`

#### XPRSaddcbslppreupdatelinearization

_**Purpose:**_

   Add a user callback to be called before the linearization is updated

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XPRSaddcbslppreupdatelinearization(XPRSprob prob,
int (XPRS_CC *slppreupdatelinearization) (XPRSprob cbprob, void *cbdata, int *when),
void *data, int priority);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slppreupdatelinearization` | The function to be called before the linearization is updated. `slppreupdatelinearization` returns an integer value. If the return value is nonzero, the optimization will return an error code and the "User Return Code" error will be set. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XPRSaddcbslppreupdatelinearization`. 
`ifrepeat` |  Indicates the call number, starting at 1. If returned nonzero, another call to the callback will be scheduled. If returned zero, a final call with `ifrepeat`set to `-1`will be made. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slppreupdatelinearization` as `cbdata`. 
`priority` | An integer that determines the order in which callbacks of this type will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
1. When the linearization is updated, all user functions are evaluated and their derivatives calculated at the current base point. In some models, it is cheaper to compute the derivatives for all user functions at the same time, thereby avoiding repeated calculations for each function. This callback is intended to be used in such cases.
2. During each SLP iteration, the callback is invoked repeatedly, with `*ifrepeat` indicating the current call number \(starting from 1\), until the callback indicates that no further calls are needed, by setting `*ifrepeat = 0`. Between each callback invocation, the solver evaluates the user functions without requesting derivatives. After the callback has set `*ifrepeat = 0`, the user functions are evaluated one more time, this time requesting derivatives, and then finally the callback is called with `*ifrepeat == -1`, marking the end of the linearization update. The only time derivatives will be requested outside of this sequence is during KKT validation. This can be disabled during the solve by clearing the `XSLP_CONVERGEBIT_VALIDATION_K` bit in `XSLP_CONVERGENCEOPS`, ensuring that derivatives can always be precomputed.
3. One way that this callback can be used to precompute derivatives for user functions is as follows:
 1. On each SLP iteration, the callback is first called with `*ifrepeat = 1`. This is a signal that derivatives will be needed soon. The callback sets a flag to indicate that user functions should capture their input values.
 2. When the callback returns, the user functions are evaluated without requesting derivatives. Each user function captures its input values somewhere, and returns the correct function value.
 3. The callback is called again, with `*ifrepeat == 2`. The callback now computes derivates for all user functions using the captured input values. The callback clears the flag so that user functions no longer capture their input values, and sets `*ifrepeat = 0` to indicate that no further calls are needed.
 4. When the callback returns, the user functions are evaluated again. Derivatives are requested, and the user functions return the precomputed derivative values.
 5. The callback is invoked one more time for this iteration with `*ifrepeat == -1`, marking the end of the linearization update. User functions should behave normally from this point.

_**Related topics:**_
[User functions](#secUserFunctions2), `XPRSnlpdeluserfunction`, `XPRSremovecbslppreupdatelinearization`

#### XSLPaddcoefs, XPRSslpaddcoefs

_**Purpose:**_

   Add non-linear coefficients to the SLP problem. For a simpler version of this function see`XSLPaddformulas`.

_**Topic areas:**_ 
SLP, Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPaddcoefs(XSLPprob prob, int ncoefs, const int[] rowind, 
const int[] colind, const double[] factor, const int[] formulastart, int parsed, 
const int[] type, const double[] value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ncoefs` | Number of non-linear coefficients to be added. 
`rowind` | Integer array holding index of row for the coefficient. 
`colind` | Integer array holding index of column for the coefficient. 
`factor` | Double array holding factor by which the formula is scaled. If this is `NULL`, then a value of 1.0 will be used. 
`formulastart` | Integer array of length `ncoefs+1` holding the start position in the arrays `type` and `value` of the formula for the coefficients. The last element should be set to the next position after the end of the last formula. 
`parsed` | Integer indicating whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the formula for each coefficient. 
`value` | Array of values corresponding to the types in `type`. 

_**Example:**_
Assume that the rows and columns of `prob`are named `Row1`, `Row2`..., `Col1`, `Col2`... The following example adds coefficients representing:

 `Col2 * Col3 + Col6 * Col2ˆ 2`into `Row1`and

 `Col2 ˆ  2`into `Row3`.

```
int rowind[3], colind[3], formulastart[4], type[8];
int n, ncoefs;
double value[8];

rowind[0] = 1; colind[0] = 2;
rowind[1] = 1; colind[1] = 6;
rowind[2] = 3; colind[2] = 2;

n = ncoefs = 0;
formulastart[ncoefs++] = n; 
type[n] = XSLP_COL; value[n++] = 3;
type[n++] = XSLP_EOF;

formulastart[ncoefs++] = n; 
type[n] = XSLP_COL; value[n++] = 2;
type[n] = XSLP_CON; value[n++] = 2;
type[n] = XSLP_OP;  value[n++] = XSLP_EXPONENT;
type[n++] = XSLP_EOF;

formulastart[ncoefs++] = n;
type[n] = XSLP_COL; value[n++] = 2;
type[n] = XSLP_CON; value[n++] = 2;
type[n] = XSLP_OP;  value[n++] = XSLP_EXPONENT;
type[n++] = XSLP_EOF;

formulastart[ncoefs] = n;

XSLPaddcoefs(prob, ncoefs, rowind, colind,
             NULL, formulastart, 1 /* reversed Polish */, type, value);
```
 
The first coefficient in `Row1` is in `Col2` and has the formula `Col3`, so it represents `Col2 * Col3`.

The second coefficient in `Row1` is in `Col6` and has the formula `Col2 * Col2` so it represents `Col6 * Col2ˆ 2`. The formulae are described as _parsed_ \( `parsed` =1\), so the formula is written as

 `Col2 Col2 *`

rather than the unparsed form

 `Col2 * Col2`

The last coefficient, in `Row3`, is in `Col2` and has the formula `Col2`, so it represents `Col2 * Col2`.


_**Further information:**_
1. The j<sup>th</sup> coefficient is made up of two parts: `factor` and `Formula`. `factor` is a constant multiplier, which can be provided in the `factor` array. If Xpress NonLinear can identify a constant factor in `Formula`, then it will use that as well, to minimize the size of the formula which has to be calculated. `Formula` is made up of a list of tokens in `type` and `value` starting at `formulastart[j]`. The tokens follow the rules for parsed or unparsed formulae as indicated by the setting of `parsed`. The formula must be terminated with an `XSLP_EOF` token. If several coefficients share the same formula, they can have the same value in `formulastart`. For possible token types and values see  _Xpress NonLinear Formulae_.
2. The `add` functions load additional items into the SLP problem. The corresponding `load` functions delete any existing items first.
3. The behaviour for existing coefficients is additive: the formula defined in the parameters are added to any existing formula coefficients. However, due to performance considerations, such duplications should be avoided when possible.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPaddformulas, XPRSnlpaddformulas

_**Purpose:**_

   Add non-linear formulas to the SLP problem.

_**Topic area:**_ 
Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPaddformulas(XSLPprob prob, int ncoefs, const int[] rowind, const int[] formulastart, int parsed, const int[] type, const double[] value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ncoefs` | Number of non-linear coefficients to be added. 
`rowind` | Integer array holding index of row for the coefficient. 
`formulastart` | Integer array of length `ncoefs+1` holding the start position in the arrays `type` and `value` of the formula for the coefficients. The last element should be set to the next position after the end of the last formula. 
`parsed` | Integer indicating whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the formula for each coefficient. 
`value` | Array of values corresponding to the types in `type`. 

_**Example:**_
Assume that the rows and columns of `prob`are named `Row0`, `Row1`..., `Col0`, `Col1`... The following example adds nonlinear formulas representing:

 `Col2 * Col3 * Col6ˆ 2`into `Row1`and

 `Col2 * Col3 ˆ  2`into `Row3`.

```
int rowind[2], formulastart[3], type[14];
int n, ncoefs;
double value[13];

rowind[0] = 1;
rowind[1] = 3;

n = ncoefs = 0;

formulastart[ncoefs++] = n; 
type[n] = XSLP_COL; value[n++] = 2;
type[n] = XSLP_COL; value[n++] = 3;
type[n] = XSLP_OP;  value[n++] = XSLP_MULTIPLY;
type[n] = XSLP_COL; value[n++] = 6;
type[n] = XSLP_CON; value[n++] = 2;
type[n] = XSLP_OP;  value[n++] = XSLP_EXPONENT;
type[n] = XSLP_OP;  value[n++] = XSLP_MULTIPLY;
type[n++] = XSLP_EOF;

formulastart[ncoefs++] = n;
type[n] = XSLP_COL; value[n++] = 2;
type[n] = XSLP_COL; value[n++] = 3;
type[n] = XSLP_CON; value[n++] = 2;
type[n] = XSLP_OP;  value[n++] = XSLP_EXPONENT;
type[n] = XSLP_OP;  value[n++] = XSLP_MULTIPLY;
type[n++] = XSLP_EOF;

formulastart[ncoefs] = n;

XSLPaddformulas(prob, ncoefs, rowind, formulastart, 1 /* reversed Polish */, type, value);
```
 
_**Further information:**_
1. The formula is made up of a list of tokens in `type` and `value` starting at `formulastart[j]`. The tokens follow the rules for parsed or unparsed formulae as indicated by the setting of `parsed`. The formula must be terminated with an `XSLP_EOF` token. If several rows share the same nonlinear expression, they can have the same value in `formulastart`. For possible token types and values see  _Xpress NonLinear Formulae_.
2. The `add` functions load additional items into the SLP problem. The corresponding `load` functions delete any existing items first.
3. The behaviour for existing formulas is additive: the formula defined in the parameters are added to any existing nonlinear expressions in the row. However, due to performance considerations, such duplications should be avoided when possible.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPadddfs

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Add a set of distribution factors.

_**Topic areas:**_ 
SLP, Data Input

_**Synopsis:**_

   `int XSLP_CC XSLPadddfs(XSLPprob prob, int ndf, const int *colind, const int *rowind, const double *value)`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ndf` | The number of distribution factors. 
`colind` | Array of indices of columns whose distribution factor is to be changed. 
`rowind` | Array of indices of the rows where each distribution factor applies. 
`value` | Array of double precision variables holding the new values of the distribution factors. 

_**Example:**_
The following example adds distribution factors as follows:

column 282 in row 134 = 0.1

column 282 in row 136 = 0.15

column 285 in row 133 = 1.0.

```
int colind[3], rowind[3];
double value[3];
colind[0] = 282;  rowind[0] = 134; value[0] = 0.1;
colind[1] = 282;  rowind[1] = 136; value[1] = 0.15;
colind[2] = 285;  rowind[2] = 133; value[2] = 1.0;
XSLPadddfs(prob,3,colind,rowind,value);
```
 
_**Further information:**_
1. The _distribution factor_ of a column in a row is the matrix coefficient of the corresponding delta vector in the row. Distribution factors are used in conventional recursion models, and are essentially normalized first-order derivatives. Xpress-SLP can accept distribution factors instead of initial values, provided that the values of the variables involved can all be calculated after optimization using determining rows, or by a callback.
2. The `add` functions load additional items into the SLP problem. The corresponding `load` functions delete any existing items first.

_**Related topics:**_
`XSLPchgdf`, `XSLPgetdf`, `XSLPloaddfs`

#### XSLPaddtolsets

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Add sets of standard tolerance values to an SLP problem.

_**Topic areas:**_ 
SLP, SLP-convergence

_**Synopsis:**_

   `int XPRS_CC XSLPaddtolsets(XSLPprob prob, int ntol, double *tol);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ntol` | The number of tolerance sets to be added. 
`tol` | Double array of \( `ntol * 9`\) items containing the 9 tolerance values for each set in order. 

_**Example:**_
The following example creates two tolerance sets: the first has values of 0.005 for all tolerances; the second has values of 0.001 for relative tolerances \(numbers 2,4,6,8\), values of 0.01 for absolute tolerances \(numbers 1,3,5,7\) and zero for the closure tolerance \(number 0\).

```
double tol[18];
for (i=0;i<9;i++) tol[i] = 0.005;
tol[9] = 0;
for (i=10;i<18;i=i+2) tol[i] = 0.01;
for (i=11;i<18;i=i+2) tol[i] = 0.001;
XSLPaddtolsets(prob, 2, tol);
```
 
_**Further information:**_
1. A tolerance set is an array of 9 values containing the following tolerances:

__Entry / Bit__ | __Tolerance__ | __XSLP constant__ | __XSLP bit constant__ | 
---------- |  ---------- | ---------- | ---------- | 
__0__ | Closure tolerance \(TC\) | `XSLP_TOLSET_TC` | `XSLP_TOLSETBIT_TC` | 
__1__ | Absolute delta tolerance \(TA\) | `XSLP_TOLSET_TA` | `XSLP_TOLSETBIT_TA` | 
__2__ | Relative delta tolerance \(RA\) | `XSLP_TOLSET_RA` | `XSLP_TOLSETBIT_RA` | 
__3__ | Absolute coefficient tolerance \(TM\) | `XSLP_TOLSET_TM` | `XSLP_TOLSETBIT_TM` | 
__4__ | Relative coefficient tolerance \(RM\) | `XSLP_TOLSET_RM` | `XSLP_TOLSETBIT_RM` | 
__5__ | Absolute impact tolerance \(TI\) | `XSLP_TOLSET_TI` | `XSLP_TOLSETBIT_TI` | 
__6__ | Relative impact tolerance \(RI\) | `XSLP_TOLSET_RI` | `XSLP_TOLSETBIT_RI` | 
__7__ | Absolute slack tolerance \(TS\) | `XSLP_TOLSET_TS` | `XSLP_TOLSETBIT_TS` | 
__8__ | Relative slack tolerance \(RS\) | `XSLP_TOLSET_RS` | `XSLP_TOLSETBIT_RS` | 

2. The XSLP\_TOLSET constants can be used to access the corresponding entry in the value arrays, while the XSLP\_TOLSETBIT constants are used to set or retrieve which tolerance values are used for a given SLP variable.
3. Once created, a tolerance set can be used to set the tolerances for any SLP variable.
4. If a tolerance value is zero, then the default tolerance will be used instead. To force the use of a tolerance, use the `XSLPchgtolset` function and set the `Status` variable appropriately.
5. See the section [Convergence criteria](#secConvergence) for a fuller description of tolerances and their uses.
6. The `add` functions load additional items into the SLP problem. The corresponding `load` functions delete any existing items first.

_**Related topics:**_
`XSLPchgtolset`, `XSLPdeltolsets`, `XSLPgettolset`, `XSLPloadtolsets`

#### XSLPadduserfunction, XPRSnlpadduserfunction

_**Purpose:**_

   Add user function definitions to an SLP problem.

_**Topic area:**_ 
User Functions

_**Synopsis:**_

   `int XPRS_CC XSLPadduserfunction(XSLPprob prob, const char * funcname, int functype, int nin, int  nout, int  options, XPRSfunctionptr function,void * data, int * p_type);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`funcname` | | The name of the function as it appears in text formula expressions. 
`functype` |  | The type of the user function, one of
&nbsp; | `1 (XSLP_USERFUNCTION_MAP)` | function takes double, returns double.
&nbsp; | `2 (XSLP_USERFUNCTION_VECMAP)` | function takes double array, returns double.
&nbsp; | `3 (XSLP_USERFUNCTION_MULTIMAP)` | function takes double array, returns double array.
&nbsp; | `4 (XSLP_USERFUNCTION_MAPDELTA)` | function takes double, returns double and delta.
&nbsp; | `5 (XSLP_USERFUNCTION_VECMAPDELTA)` | function takes double array, returns double and deltas.
&nbsp; | `6 (XSLP_USERFUNCTION_MULTIMAPDELTA)` | function takes double array, returns double array and deltas.
`nin` | | Number of arguments the user function takes. 
`nout` | | Number of return arguments for the function. 
`options` |  | options as a bitmap to the user function
&nbsp; | `XSLP_INSTANCEFUNCTION` | always instantiate the function.
`function` | | Pointer of the user function to call. 
`data` | | Context pointer to provide the user function with. 
`p_type` | | The token id of the user function added, to be used in the Value array when defining formulas and using with `XSLP_FUN`. 

_**Further information:**_
1. The type `XPRSfunctionptr` is a generic function pointer.
2. The function declarations expected for the user functions are defined by the `functype` argument.
3. The function of type `XSLP_USERFUNCTION_MAP` expects a function in the form of 'double XPRS\_CC F\(double Value, void \*Context\)'.
4. The function of type `XSLP_USERFUNCTION_VECMAP` expects a function in the form of 'double XPRS\_CC F\(double \*Value, void \*Context\)'.
5. The function of type `XSLP_USERFUNCTION_MULTIMAP` expects a function in the form of 'int XPRS\_CC F\(double \*Value, double \*Out, void \*Context\)'.
6. The function of type `XSLP_USERFUNCTION_MAPDELTA` expects a function in the form of 'int XPRS\_CC F\(double Value, double Delta, double \*Evaluation, double \*Partial, void \*Context\)'.
7. The function of type `XSLP_USERFUNCTION_VECMAPDELTA` expects a function in the form of 'int XPRS\_CC F\(double \*Value, double \*Deltas, double \*Evaluation, double \*Partials, void \*Context\)'.
8. The function of type `XSLP_USERFUNCTION_MULTIMAPDELTA` expects a function in the form of 'int XPRS\_CC F\(double \*Value, double \*Deltas, double \*Out, void \*Context\)'.

_**Related topics:**_
[User functions](#secUserFunctions2), `XSLPdeluserfunction`, `XSLPimportlibfunc`

#### XSLPaddvars

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Add SLP variables defined as matrix columns to an SLP problem.

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPaddvars(XSLPprob prob, int nvars, int *colind, 
int *coltype, int *detrow, int *seqnum, int *tolind, 
double *initial, double *stepbound);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`nvars` | | The number of SLP variables to be added. 
`colind` | | Integer array holding the index of the matrix column corresponding to each SLP variable. 
`coltype` |  | Bitmap giving information about the SLP variables, compare the variable status keys, in particular:
&nbsp; | `Bit 2 (XSLP_HASIV)` | Variable has an initial value;
&nbsp; |  | May be `NULL`if not required.
`detrow` | | Integer array holding the index of the determining row for each SLP variable \(a negative value means there is no determining row\)
&nbsp; | May be `NULL`if not required. 
`seqnum` | | Integer array holding the index sequence number for cascading for each SLP variable \(a zero value means there is no pre-defined order for this variable\)
&nbsp; | May be `NULL`if not required. 
`tolind` | | Integer array holding the index of the tolerance set for each SLP variable \(a zero value means the default tolerances are used\)
&nbsp; | May be `NULL`if not required. 
`initial` | | Double array holding the initial value for each SLP variable \(use the `coltype` bit map to indicate if a value is being provided\)
&nbsp; | May be `NULL`if not required. 
`stepbound` | | Double array holding the initial step bound size for each SLP variable \(a zero value means that no initial step bound size has been specified\). If a value of `XPRS_PLUSINFINITY` is used for a value in `stepbound`, the delta will never have step bounds applied, and will almost always be regarded as converged.
&nbsp; | May be `NULL`if not required. 

_**Example:**_
The following example loads two SLP variables into the problem. They correspond to columns 23 and 25 of the underlying LP problem. Column 25 has an initial value of 1.42; column 23 has no specific initial value

```

int colind[2], coltype[2];
double initial[2];

colind[0] = 23; coltype[0] = 0; initial[0] = 0.0;
colind[1] = 25; coltype[1] = XSLP_HASIV; initial[1] = 1.42;

XSLPaddvars(prob, 2, colind, coltype, NULL, NULL,
            NULL, initial, NULL);
```
 
Note that `initial` for the first variable will not actually be used, because the `XSLP_HASIV` flag is not set \( `coltype` = 0\). Setting the variable type to XSLP\_HASIV for the second variable indicates that the initial value has been set.

The arrays for determining rows, sequence numbers, tolerance sets and step bounds are not used at all, and so have been passed to the function as `NULL`.


_**Further information:**_
1. For adding determining rows, use `XSLPsetdetrow`. For adding initial values, use `XSLPsetinitval`. For adding initial stepbounds, use `XPRSslpsetinitstepbounds`.
2. The `add` functions load additional items into the SLP problem. The corresponding `load` functions delete any existing items first.

_**Related topics:**_
`XSLPchgvar`, `XSLPdelvars`, `XSLPgetvar`, `XSLPloadvars`, `XSLPsetdetrow`, `XPRSslpsetinitstepbounds`, `XSLPsetinitval`

#### XSLPcalcslacks, XPRSnlpcalcslacks

_**Purpose:**_

   Calculate the slack values for the provided solution in the non-linear problem

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPcalcslacks(XSLPprob prob, const double[] solution, double[] slack);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`solution` | The solution for which the slacks are requested. 
`slack` | Array of length `ROWS` to hold the slacks. 

_**Related topics:**_
`XSLPvalidate`, `XSLPvalidaterow`

#### XSLPcascade, XPRSslpcascade

_**Purpose:**_

   Re-calculate consistent values for SLP variables based on the current values of the remaining variables.

_**Topic areas:**_ 
SLP, Solution Process, Cascading

_**Synopsis:**_

   `int XPRS_CC XSLPcascade(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_

The following example changes the solution value for column 91, and then re-calculates the values of those dependent on it.


```
int ColNum;
double Value;

ColNum = 91;
XSLPgetvar(prob, ColNum, NULL, NULL, NULL, NULL, 
           NULL, NULL, &Value, NULL, NULL, NULL, 
           NULL, NULL, NULL, NULL, NULL);

Value = Value + 1.42;
XSLPchgvar(prob, ColNum, NULL, NULL, NULL, NULL, 
           NULL, NULL, &Value, NULL, NULL, NULL, 
           NULL);
XSLPcascade(prob);
```
 
`XSLPgetvar` and `XSLPchgvar` are being used to get and change the current value of a single variable.

Provided no other values have been changed since the last execution of `XSLPcascade`, values will be changed only for variables which depend on column 91.


_**Further information:**_
1. See the section on cascading for an extended discussion of the types of cascading which can be performed.
2. `XSLPcascade` is called automatically during the SLP iteration process and so it is not normally necessary to perform an explicit cascade calculation.
3. The variables are re-calculated in accordance with the order generated by `XSLPcascadeorder`.

_**Related topics:**_
`XSLPcascadeorder`, `XSLP_CASCADE`, `XSLP_CASCADENLIMIT`, `XSLP_CASCADETOL_PA`, `XSLP_CASCADETOL_PR`

#### XSLPcascadeorder, XPRSslpcascadeorder

_**Purpose:**_

   Establish a re-calculation sequence for SLP variables with determining rows.

_**Topic areas:**_ 
SLP, Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPcascadeorder(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_
Assuming that all variables are SLP variables, the following example sets default values for the variables, creates the re-calculation order and then calls`XSLPcascade`to calculate consistent values for the dependent variables.

```
int ColNum;
for (ColNum=1;ColNum<=nCol;ColNum++) 
  XSLPchgvar(prob, ColNum, NULL, NULL, NULL, NULL, 
             NULL, NULL, &DefaultValue[ColNum], NULL, NULL, NULL, 
             NULL);
XSLPcascadeorder(prob);
XSLPcascade(prob);
```
 

_**Further information:**_
`XSLPcascadeorder`is called automatically at the start of the SLP iteration process and so it is not normally necessary to perform an explicit cascade ordering.

_**Related topics:**_
`XSLPcascade`

#### XSLPchgcascadenlimit, XPRSslpchgcascadenlimit

_**Purpose:**_

   Set a variable specific cascade iteration limit

_**Topic areas:**_ 
SLP, Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPchgcascadenlimit(XSLPprob prob, int col, int limit);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`col` | The index of the column corresponding to the SLP variable for which the cascading limit is to be imposed. 
`limit` | The new cascading iteration limit. 

_**Further information:**_
A value set by this function will overwrite the value of`XSLP_CASCADENLIMIT`for this variable. To remove any previous value set by this function, use an iteration limit of 0.

_**Related topics:**_
`XSLPcascadeorder`, `XSLP_CASCADE`, `XSLP_CASCADENLIMIT`, `XSLP_CASCADETOL_PA`, `XSLP_CASCADETOL_PR`

#### XPRSslpchgcoefstr

_**Purpose:**_

   Add or change a single matrix coefficient using a character string for the formula. For a simpler version of this function see`XPRSnlpchgformulastr`.

_**Topic areas:**_ 
SLP, Problem Modification

_**Synopsis:**_

   `int XPRS_CC XPRSslpchgcoefstr(XPRSprob prob, int row, int col,
 const double *factor, const char *formula);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | The index of the matrix row for the coefficient. 
`col` | The index of the matrix column for the coefficient. 
`factor` | Address of a double precision variable holding the constant multiplier for the formula. If `factor` is `NULL`, a value of 1.0 will be used. 
`formula` | Character string holding the formula with the tokens separated by spaces. 

_**Example:**_
Assuming that the columns of the matrix are named `Col1`, `Col2`, etc, the following example puts the formula `2.5*sin(Col1)`into the coefficient in row 1, column 3.

```
char *formula="sin ( Col1 )";
double factor;

factor = 2.5;
XPRSslpchgcoefstr(prob, 1, 3, &factor, formula);

```
 Note that all the tokens in the formula \(including mathematical operators and separators\) are separated by one or more spaces.

_**Further information:**_
1. If the coefficient already exists as a constant or formula, it will be changed into the new coefficient. If it does not exist, it will be added to the problem.
2. A coefficient is made up of two parts: `factor` and `formula`. `factor` is a constant multiplier which can be provided in the `factor` variable. If Xpress NonLinear can identify a constant factor in the formula, then it will use that as well, to minimize the size of the formula which has to be calculated.
3. This function can only be used if all the operands in the formula can be correctly identified as constants, existing columns, character variables or functions. Therefore, if a formula refers to a new column, that new item must be added to the Xpress NonLinear problem first.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPchgccoef, XPRSslpchgccoef

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Use`XPRSslpchgcoefstr`instead._
   Add or change a single matrix coefficient using a character string for the formula. For a simpler version of this function see`XPRSnlpchgformulastr`.

_**Topic areas:**_ 
SLP, Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPchgccoef(XSLPprob prob, int row, int col,
 const double *factor, const char *formula);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row for the coefficient. 
`col` | The index of the matrix column for the coefficient. 
`factor` | Address of a double precision variable holding the constant multiplier for the formula. If `factor` is `NULL`, a value of 1.0 will be used. 
`formula` | Character string holding the formula with the tokens separated by spaces. 

_**Example:**_
Assuming that the columns of the matrix are named `Col1`, `Col2`, etc, the following example puts the formula `2.5*sin(Col1)`into the coefficient in row 1, column 3.

```
char *formula="sin ( Col1 )";
double factor;

factor = 2.5;
XSLPchgccoef(prob, 1, 3, &factor, formula);

```
 Note that all the tokens in the formula \(including mathematical operators and separators\) are separated by one or more spaces.

_**Further information:**_
1. If the coefficient already exists as a constant or formula, it will be changed into the new coefficient. If it does not exist, it will be added to the problem.
2. A coefficient is made up of two parts: `factor` and `formula`. `factor` is a constant multiplier which can be provided in the `factor` variable. If Xpress NonLinear can identify a constant factor in the formula, then it will use that as well, to minimize the size of the formula which has to be calculated.
3. This function can only be used if all the operands in the formula can be correctly identified as constants, existing columns, character variables or functions. Therefore, if a formula refers to a new column, that new item must be added to the Xpress NonLinear problem first.

_**Related topics:**_
`XPRSslpchgcoefstr`, `XPRSslpgetcoefstr`, `XPRSnlpgetformulastr`, `XPRSnlpchgformulastr`, `XSLPaddformulas`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPchgcoef, XPRSslpchgcoef

_**Purpose:**_

   Add or change a single matrix coefficient using a parsed or unparsed formula. For a simpler version of this function see`XSLPchgformula`.

_**Topic areas:**_ 
SLP, Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPchgcoef(XSLPprob prob, int row, int col, 
const double *factor, int parsed, const int[] type, const double[] value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row for the coefficient. 
`col` | The index of the matrix column for the coefficient. 
`factor` | Address of a double precision variable holding the constant multiplier for the formula. If `factor` is `NULL`, a value of 1.0 will be used. 
`parsed` | Integer indicating the whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the description and formula for each item. 
`value` | Array of values corresponding to the types in `type`. 

_**Example:**_
Assuming that the columns of the matrix are named `Col1`, `Col2`, etc, the following example puts the formula `2.5*sin(Col1)`into the coefficient in row 1, column 3.

```
int n, iSin, type[4];
double value[4];
double factor;

XSLPgetindex(prob, XSLP_INTERNALFUNCNAMESNOCASE,
             "sin", &iSin);

n = 0;
type[n] = XSLP_IFUN; value[n++] = iSin;
type[n] = XSLP_COL;  value[n++] = 0;
type[n++] = XSLP_RB;
type[n++] = XSLP_EOF;

factor = 2.5;
XSLPchgcoef(prob, 1, 3, &factor, 0, type, value);
```
 
`XSLPgetindex` is used to retrieve the index for the internal function `sin`. The "nocase" version matches the function name regardless of the \(upper or lower\) case of the name.

Token type `XSLP_COL` always counts from 0, so `Col1` is always 0.

The formula is written in unparsed form \( `parsed` = 0\) and so it is provided as tokens in the same order as they would appear if the formula were written in character form.


_**Further information:**_
1. If the coefficient already exists as a constant or formula, it will be changed into the new coefficient. If it does not exist, it will be added to the problem.
2. A coefficient is made up of two parts: `factor` and `Formula`. `factor` is a constant multiplier which can be provided in the `factor` variable. If Xpress NonLinear can identify a constant factor in the Formula, then it will use that as well, to minimize the size of the formula which has to be calculated.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPchgdeltatype, XPRSslpchgdeltatype

_**Purpose:**_

   Changes the type of the delta assigned to a nonlinear variable

_**Topic areas:**_ 
SLP, Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPchgdeltatype(XSLPprob prob, int nvars, const int[] varind, const int[] deltatypes, const double[] values);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`nvars` | | The number of SLP variables to change the delta type for. 
`varind` | | Indices of the variables to change the deltas for. 
`deltatypes` |  | Type of the delta variable:
&nbsp; | `0 (XSLP_DELTA_CONT)` | Differentiable variable, default.
&nbsp; | `1 (XSLP_DELTA_SEMICONT)` | Variable where a minimum perturbation size given in `values` may be required before a significant change in the problem is achieved.
&nbsp; | `2 (XSLP_DELTA_INTEGER)` | Variable defined over the grid size given in `values`.
&nbsp; | `3 (XSLP_DELTA_EXPLORE)` | Variable where a meaningful step size should automatically be detected, with an upper limit given in `values`.
`values` | | Grid or minimum step sizes for the variables. 

_**Further information:**_
Changing the delta type of a variables makes the variable nonlinear.

_**Related topics:**_
`XSLP_SEMICONTDELTAS`, `XSLP_INTEGERDELTAS`, `XSLP_EXPLOREDELTAS`

#### XSLPchgdf

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Set or change a distribution factor.

_**Topic areas:**_ 
SLP, Data Input

_**Synopsis:**_

   `int XSLP_CC XSLPchgdf(XSLPprob prob, int col, int row, const double *value)`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`col` | The index of the column whose distribution factor is to be set or changed. 
`row` | The index of the row where the distribution applies. 
`value` | Address of a double precision variable holding the new value of the distribution factor. May be `NULL` if not required. 

_**Example:**_
The following example retrieves the value of the distribution factor for column 282 in row 134 and changes it to be twice as large.

```
double value;
XSLPgetdf(prob,282,134,&value);
value = value * 2;
XSLPchgdf(prob,282,134,&value);
```
 

_**Further information:**_
The _distribution factor_of a column in a row is the matrix coefficient of the corresponding delta vector in the row. Distribution factors are used in conventional recursion models, and are essentially normalized first-order derivatives. Xpress NonLinear can accept distribution factors instead of initial values, provided that the values of the variables involved can all be calculated after optimization using determining rows, or by a callback.

_**Related topics:**_
`XSLPadddfs`, `XSLPgetdf`, `XSLPloaddfs`

#### XSLPchgformulastring, XPRSnlpchgformulastring

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Use`XPRSnlpchgformulastr`instead._
   Add or replace a single matrix formula using a character string for the formula.

_**Topic area:**_ 
Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPchgformulastring(XSLPprob prob, int row, const char *formula);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row for the coefficient. 
`formula` | Character string holding the formula with the tokens separated by spaces. 

_**Example:**_
Assuming that the columns of the matrix are named `Col1`, `Col2`, etc, the following example puts the formula `sin(Col1)`into row 1.

```
char *formula="sin ( Col1 )";
XSLPchgformulastring(prob, 1, formula);

```
 Note that all the tokens in the formula \(including mathematical operators and separators\) are separated by one or more spaces.

_**Further information:**_
1. If the coefficient already exists as a constant or formula, it will be changed into the new coefficient. If it does not exist, it will be added to the problem.
2. This function can only be used if all the operands in the formula can be correctly identified as constants, existing columns, character variables or functions. Therefore, if a formula refers to a new column, that new item must be added to the Xpress NonLinear problem first.

_**Related topics:**_
`XPRSnlpchgformulastr`, `XPRSnlpgetformulastr`, `XSLPaddformulas`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XPRSnlpchgformulastr

_**Purpose:**_

   Add or replace a single matrix formula using a character string for the formula.

_**Topic area:**_ 
Problem Modification

_**Synopsis:**_

   `int XPRS_CC XPRSnlpchgformulastr(XPRSprob prob, int row, const char *formula);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | The index of the matrix row for the coefficient. 
`formula` | Character string holding the formula with the tokens separated by spaces. 

_**Example:**_
Assuming that the columns of the matrix are named `Col1`, `Col2`, etc, the following example puts the formula `sin(Col1)`into row 1.

```
char *formula="sin ( Col1 )";
XPRSnlpchgformulastr(prob, 1, formula);

```
 Note that all the tokens in the formula \(including mathematical operators and separators\) are separated by one or more spaces.

_**Further information:**_
1. If the coefficient already exists as a constant or formula, it will be changed into the new coefficient. If it does not exist, it will be added to the problem.
2. This function can only be used if all the operands in the formula can be correctly identified as constants, existing columns, character variables or functions. Therefore, if a formula refers to a new column, that new item must be added to the Xpress NonLinear problem first.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPchgformula, XPRSnlpchgformula

_**Purpose:**_

   Add or replace a single matrix formula using a parsed or unparsed formula

_**Topic area:**_ 
Problem Modification

_**Synopsis:**_

   `int XPRS_CC XSLPchgformula(XSLPprob prob, int row, int parsed, const int[] type, const double []value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row for the coefficient. 
`parsed` | Integer indicating the whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the description and formula for each item. 
`value` | Array of values corresponding to the types in `type`. 

_**Example:**_
Assuming that the columns of the matrix are named `Col1`, `Col2`, etc, the following example puts the formula `sin(Col1)`into the coefficient in row 1.

```
int n, iSin, type[4];
double value[4];

XSLPgetindex(prob, XSLP_INTERNALFUNCNAMESNOCASE,
     "sin", &iSin);

n = 0;
type[n] = XSLP_IFUN; value[n++] = iSin;
type[n] = XSLP_COL;  value[n++] = 0;
type[n++] = XSLP_RB;
type[n++] = XSLP_EOF;

Factor = 2.5;
XSLPchgformula(prob, 1, 0, type, value);
```
 
`XSLPgetindex` is used to retrieve the index for the internal function `sin`. The "nocase" version matches the function name regardless of the \(upper or lower\) case of the name.

Token type `XSLP_COL` always counts from 0, so `Col1` is always 0.

The formula is written in unparsed form \( `parsed` = 0\) and so it is provided as tokens in the same order as they would appear if the formula were written in character form.


_**Further information:**_
If the row already has a nonlinear expression in it, it will be changed into the new formula. If it does not exist, it will be added to the problem.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPchgrowstatus, XPRSslpchgrowstatus

_**Purpose:**_

   Change the status setting of a constraint

_**Topic areas:**_ 
SLP, Data Input, Bit-vector

_**Synopsis:**_

   `int XPRS_CC XSLPchgrowstatus(XSLPprob prob, int row, const int *status);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`row` | | The index of the matrix row to be changed. 
`status` |  | Aninteger holding a bitmap with the new status settings. If the status is to be changed, always get the current status first \(use`XSLPgetrowstatus`\) and then change settings as required. The only settings likely to be changed are:
&nbsp; | `Bit 11` | Set if row must not have a penalty error vector. This is the equivalent of an enforced constraint \(SLPDATA type EC\).

_**Example:**_
The following example changes the status of row 9 to be an enforced constraint.

```
int row, status;
row = 9;
XSLPgetrowstatus(prob,row,&status);
status = status | (1<<11);
XSLPchgrowstatus(prob,row,&status);
```
 
_**Further information:**_
If `status`is `NULL`the current status will remain unchanged.

_**Related topics:**_
`XSLPgetrowstatus`

#### XSLPchgrowwt, XPRSslpchgrowwt

_**Purpose:**_

   Set or change the initial penalty error weight for a row

_**Topic areas:**_ 
SLP, Data Input

_**Synopsis:**_

   `int XSLP_CC XSLPchgrowwt(XSLPprob prob, int row, const double *weight);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the row whose weight is to be set or changed. 
`weight` | Address of a double precision variable holding the new value of the weight. May be `NULL` if not required. 

_**Example:**_
The following example sets the initial weight of row number 2 to a fixed value of 3.6 and the initial weight of row 4 to a value twice the calculated default value.

```
double weight;
weight = -3.6;
XSLPchgrowwt(prob,2,&weight);
weight = 2.0;
XSLPchgrowwt(prob,4,&weight);
```
 

_**Further information:**_
1. A positive value is interpreted as a multiplier of the default row weight calculated by Xpress-SLP.
2. A negative value is interpreted as a fixed value: the absolute value is used directly as the row weight.
3. The initial row weight is used only when the augmented structure is created.

_**Related topics:**_
`XSLPgetrowwt`

#### XSLPchgtolset

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Add or change a set of convergence tolerances used for SLP variables.

_**Topic areas:**_ 
SLP, SLP-convergence

_**Synopsis:**_

   `int XPRS_CC XSLPchgtolset(XSLPprob prob, int ntols, int *status, double *tols);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`tolset` | Tolerance set for which values are to be changed. A zero value for `tolset` will create a new set. 
`status` | Address of an integer holding a bitmap describing which tolerances are active in this set. See below for the settings. 
`tols` | Array of 9 double precision values holding the values for the corresponding tolerances. 

_**Example:**_
The following example creates a new tolerance set with the default values for all tolerances except the relative delta tolerance, which is set to 0.005. It then changes the value of the absolute delta and absolute impact tolerances in tolerance set 6 to 0.015

```
int status;
double tols[9];

tols[2] = 0.005;
status = 1<<2;
XSLPchgtolset(prob, 0, &status, tols);
tols[1] = tols[5] = 0.015;
status = 1<<1 | 1<<5;
XSLPchgtolset(prob, 6, &status, tols);
```
 
_**Further information:**_
The bits in `status`are set to indicate that the corresponding tolerance is to be changed in the tolerance set. The meaning of the bits is as follows:

__Entry / Bit__ | __Tolerance__ | __XSLP constant__ | __XSLP bit constant__ | 
---------- |  ---------- | ---------- | ---------- | 
__0__ | Closure tolerance \(TC\) | `XSLP_TOLSET_TC` | `XSLP_TOLSETBIT_TC` | 
__1__ | Absolute delta tolerance \(TA\) | `XSLP_TOLSET_TA` | `XSLP_TOLSETBIT_TA` | 
__2__ | Relative delta tolerance \(RA\) | `XSLP_TOLSET_RA` | `XSLP_TOLSETBIT_RA` | 
__3__ | Absolute coefficient tolerance \(TM\) | `XSLP_TOLSET_TM` | `XSLP_TOLSETBIT_TM` | 
__4__ | Relative coefficient tolerance \(RM\) | `XSLP_TOLSET_RM` | `XSLP_TOLSETBIT_RM` | 
__5__ | Absolute impact tolerance \(TI\) | `XSLP_TOLSET_TI` | `XSLP_TOLSETBIT_TI` | 
__6__ | Relative impact tolerance \(RI\) | `XSLP_TOLSET_RI` | `XSLP_TOLSETBIT_RI` | 
__7__ | Absolute slack tolerance \(TS\) | `XSLP_TOLSET_TS` | `XSLP_TOLSETBIT_TS` | 
__8__ | Relative slack tolerance \(RS\) | `XSLP_TOLSET_RS` | `XSLP_TOLSETBIT_RS` | 
The XSLP\_TOLSET constants can be used to access the corresponding entry in the value arrays, while the XSLP\_TOLSETBIT constants are used to set or retrieve which tolerance values are used for a given SLP variable.The members of the `tols`array corresponding to nonzero bit settings in `status`will be used to change the tolerance set. So, for example, if bit 3 is set in `status`, then `tols[3]`will replace the current value of the absolute coefficient tolerance. If a bit is not set in `status`, the value of the corresponding element of `tols`is unimportant.

_**Related topics:**_
`XSLPaddtolsets`, `XSLPdeltolsets`, `XSLPgettolset`, `XSLPloadtolsets`

#### XSLPchgvar

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Define a column as an SLP variable or change the characteristics and values of an existing SLP variable.

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPchgvar(XSLPprob prob, int col, int *detrow, 
double *initstepbound, double *stepbound, double *penalty, 
double *damp, double *initial, double *value, int *tolset, 
int *history, int *converged, int *vartype);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`col` | | The index of the matrix column. 
`detrow` | | Address of an integer holding the index of the determining row. Use -1 if there is no determining row. May be `NULL` if not required. 
`initstepbound` | | Address of a double precision variable holding the initial step bound size. May be `NULL` if not required. 
`stepbound` | | Address of a double precision variable holding the current step bound size. Use zero to disable the step bounds. May be `NULL` if not required. 
`penalty` | | Address of a double precision variable holding the weighting of the penalty cost for exceeding the step bounds. May be `NULL` if not required. 
`damp` | | Address of a double precision variable holding the damping factor for the variable. May be `NULL` if not required. 
`initial` | | Address of a double precision variable holding the initial value for the variable. May be `NULL` if not required. 
`value` | | Address of a double precision variable holding the current value for the variable. May be `NULL` if not required. 
`tolset` | | Address of an integer holding the index of the tolerance set for this variable. Use zero if there is no specific tolerance set. May be `NULL` if not required. 
`history` | | Address of an integer holding the history value for this variable. May be `NULL` if not required. 
`converged` | | Address of an integer holding the convergence status for this variable. May be `NULL` if not required. 
`vartype` |  | Address of an integer holding a bitmap defining the existence of certain properties for this variable:
&nbsp; | `Bit 1:` | Variable has a delta vector
&nbsp; | `Bit 2:` | Variable has an initial value
&nbsp; | `Bit 14:` | Variable is the reserved "=" column
&nbsp; |  | May be `NULL`if not required.

_**Example:**_
The following example sets an initial value of 1.42 and tolerance set 2 for column 25 in the matrix.

```
double InitialValue;
int vartype, tolset;

InitialValue = 1.42;
tolset = 2;
vartype = 1<<1 | 1<<2;

XSLPchgvar(prob, 25, NULL, NULL, NULL, NULL,
   NULL, &InitialValue, NULL, &tolset, 
   NULL, NULL, &vartype);

```
 Note that bits 1 and 2 of `vartype`are set, indicating that the variable has a delta vector and an initial value. For columns already defined as SLP variables, use`XSLPgetvar`to obtain the current value of `vartype`because other bits may already have been set by the system.

_**Further information:**_
1. If any of the arguments is `NULL` then the corresponding information for the variable will be left unaltered. If the information is new \(i.e. the column was not previously defined as an SLP variable\) then the default values will be used.
2. Changing `history` or `converged` is only effective during SLP iterations, changing `value` only during iterations and before calling functions that specifically use this like `XSLPcascade`.
3. Changing `initial` and `initstepbound` is only effective before `XSLPconstruct`.
4. If a value of `XPRS_PLUSINFINITY` is used in the value for `stepbound` or `initstepbound`, the delta will never have step bounds applied, and will almost always be regarded as converged.

_**Related topics:**_
`XSLPaddvars`, `XSLPdelvars`, `XSLPgetvar`, `XSLPloadvars`

#### XSLPconstruct, XPRSslpconstruct

_**Purpose:**_

   Create the full augmented SLP matrix and data structures, ready for optimization

_**Topic areas:**_ 
SLP, Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPconstruct(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_
The following example constructs the augmented matrix and then outputs the result in MPS format to a file called augment.mat

```
/* creation and/or loading of data */
/* precedes this segment of code   */
...
XSLPconstruct(prob);
XSLPwriteprob(prob,"augment","l");
```
 The "l" flag causes output of the current linear problem \(which is now the augmented structure and the current linearization\) rather than the original nonlinear problem.

_**Further information:**_
1. `XSLPconstruct` adds new rows and columns to the SLP matrix and calculates initial values for the non-linear coefficients. Which rows and columns are added will depend on the setting of `XSLP_AUGMENTATION`. Names for the new rows and columns are generated automatically, based on the existing names and the string controls such as `XSLP_DELTAFORMAT`.
2. Once `XSLPconstruct` has been called, no new rows, columns or non-linear coefficients can be added to the problem. Any rows or columns which will be required must be added first. Non-linear coefficients must not be changed; constant matrix elements can generally be changed after `XSLPconstruct`, but not after`XSLPpresolve`if used.
3. `XSLPconstruct` is called automatically by the SLP optimization procedure, and so only needs to be called explicitly if changes need to be made between the augmentation and the optimization.

_**Related topics:**_
 `XSLPpresolve`

#### XSLPcopycallbacks

_**Purpose:**_

   Copy the user-defined callbacks from one SLP problem to another

_**Topic area:**_ 
Callback

_**Synopsis:**_

   `int XPRS_CC XSLPcopycallbacks(XSLPprob dest, XSLPprob src);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The SLP problem to receive the callbacks. 
`src` | The SLP problem from which the callbacks are to be copied. 

_**Example:**_
The following example creates a new problem and copies only the Xpress NonLinear callbacks from the existing problem \(not the Optimizer library ones\).

```
XSLPprob nProb;
XPRSprob xProb;
int Control;

XSLPcreateprob(&nProb, &xProb);

Control = 1<<2;
XSLPsetintcontrol(Prob, XSLP_CONTROL, Control);
XSLPcopycallbacks(nProb, Prob);
```
 Note that`XSLP_CONTROL`is set in the _old_problem, not the new one.

_**Further information:**_
Normally `XSLPcopycallbacks`copies both the Xpress NonLinear callbacks and the Optimizer Library callbacks for the underlying problem. If only the Xpress NonLinear callbacks are required, set the integer control variable`XSLP_CONTROL`appropriately.

_**Related topics:**_
`XSLP_CONTROL`

#### XSLPcopycontrols

_**Purpose:**_

   Copy the values of the control variables from one SLP problem to another

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPcopycontrols(XSLPprob dest, XSLPprob src);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The SLP problem to receive the controls. 
`src` | The SLP problem from which the controls are to be copied. 

_**Example:**_
The following example creates a new problem and copies only the Xpress NonLinear controls from the existing problem \(not the Optimizer library ones\).

```
XSLPprob nProb;
XPRSprob xProb;
int Control;

XSLPcreateprob(&nProb, &xProb);

Control = 1<<1;
XSLPsetintcontrol(Prob, XSLP_CONTROL, Control);
XSLPcopycontrols(nProb, Prob);
```
 Note that`XSLP_CONTROL`is set in the _old_problem, not the new one.

_**Further information:**_
1. Normally `XSLPcopycontrols` copies both the Xpress NonLinear controls and the Optimizer Library controls for the underlying problem. If only the Xpress NonLinear controls are required, set the integer control variable `XSLP_CONTROL` appropriately.
2. Since the objective sense is a control in Xpress nonlinear, `XSLPcopycontrols` will also copy the objective sense from the source to the destination.

_**Related topics:**_
`XSLP_CONTROL`

#### XSLPcopyprob

_**Purpose:**_

   Copy an existing SLP problem to another

_**Topic area:**_ 
Problem Creation

_**Synopsis:**_

   `int XPRS_CC XSLPcopyprob(XSLPprob dest, XSLPprob src, char *probname);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The SLP problem to receive the copy. 
`src` | The SLP problem from which to copy. 
`probname` | The name to be given to the problem. 

_**Example:**_
The following example creates a new Xpress NonLinear problem and then copies an existing problem to it. The new problem is named "ANewProblem".

```
XSLPprob nProb;
XPRSprob xProb;

XSLPcreateprob(&nProb, &xProb);
XSLPcopyprob(nProb, Prob, "ANewProblem");
```
 
_**Further information:**_
1. Normally `XSLPcopyprob` copies both the Xpress NonLinear problem and the underlying Optimizer Library problem. If only the Xpress NonLinear problem is required, set the integer control variable `XSLP_CONTROL` appropriately.
2. This function does not copy callbacks. These must be copied separately using `XSLPcopycallbacks` if required.

_**Related topics:**_
`XSLP_CONTROL`

#### XSLPcreateprob

_**Purpose:**_

   Create a new SLP problem

_**Topic area:**_ 
Problem Creation

_**Synopsis:**_

   `int XPRS_CC XSLPcreateprob(XSLPprob *p_prob, XPRSprob *p_xprob);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`p_prob` | The address of the SLP problem variable. 
`p_xprob` | The address of the underlying Optimizer Library problem variable. 

_**Example:**_
The following example creates an optimizer problem, and then a new Xpress NonLinear problem.

```
XSLPprob nProb;
XPRSprob xprob;

XPRScreateprob(&xprob);
XSLPcreateprob(&nProb, &xprob);
```
 
_**Further information:**_
An Xpress NonLinear problem includes an underlying optimizer problem which is used to solve the successive linear approximations. The user is responsible for creating and destroying the underlying linear problem, and can also access it using the normal optimizer library functions. When an SLP problem is to be created, the underlying problem is created first, and the SLP problem is then created, knowing the address of the underlying problem.

_**Related topics:**_
`XSLPdestroyprob`

#### XSLPdelcoefs, XPRSslpdelcoefs

_**Purpose:**_

   Delete coefficients from the current problem. For a simpler version of this function see`XSLPdelformulas`.

_**Topic areas:**_ 
SLP, Problem Modification

_**Synopsis:**_

   `
    int XPRS_CC XSLPdelcoefs(XSLPprob prob, int ncoefs, const int[] rowind, const int[] colind);
  `

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ncoefs` | Number of SLP coefficients to delete. 
`rowind` | Row indices of the SLP coefficients to delete. 
`colind` | Column indices of the SLP coefficients to delete. 

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPdelformulas, XPRSnlpdelformulas

_**Purpose:**_

   Delete nonlinear formulas from the current problem

_**Topic area:**_ 
Problem Modification

_**Synopsis:**_

   `
    int XPRS_CC XSLPdelformulas(XSLPprob prob, int nformulas, const int[] rowind);
  `

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`nformulas` | Number of SLP nonlinear formulas to delete. 
`rowind` | Row indices of the SLP nonlinear formulas to delete. 

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPdeltolsets

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Delete tolerance sets from the current problem

_**Topic areas:**_ 
SLP, SLP-convergence

_**Synopsis:**_

   `
    int XPRS_CC XSLPdeltolsets(XSLPprob prob, int ntolsets, int *tolind);
  `

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ntolsets` | Number of tolerance sets to delete. 
`tolind` | Indices of tolerance sets to delete. 

_**Related topics:**_
`XSLPaddtolsets`, `XSLPchgtolset`, `XSLPgettolset`, `XSLPloadtolsets`

#### XSLPdeluserfunction, XPRSnlpdeluserfunction

_**Purpose:**_

   Delete a user function from the current problem

_**Topic area:**_ 
User Functions

_**Synopsis:**_

   `
    int XPRS_CC XSLPdeluserfunction(XSLPprob prob, int type);
  `

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`type` | The identifier of the user function as returned by `XSLPadduserfunction`. 

_**Related topics:**_
`XSLPadduserfunction`, `XSLPimportlibfunc`

#### XSLPdelvars

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Convert SLP variables to normal columns. Variables must not appear in SLP structures

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `
    int XPRS_CC XSLPdelvars(XSLPprob prob, int nvars, int *colind);
  `

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`nvars` | Number SLP variables to be converted to linear columns. 
`colind` | Column indices of the SLP vars to be converted to linear ones. 

_**Further information:**_
The SLP variables to be converted to linear, non SLP columns must not be in use by any other SLP structure \(coefficients, initial value formulae, delayed columns\). Use the appropriate deletion or change functions to remove them first.

_**Related topics:**_
`XSLPaddvars`, `XSLPchgvar`, `XSLPgetvar`, `XSLPloadvars`

#### XSLPdestroyprob

_**Purpose:**_

   Delete an SLP problem and release all the associated memory

_**Topic area:**_ 
Problem Creation

_**Synopsis:**_

   `int XPRS_CC XSLPdestroyprob(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The SLP problem. 

_**Example:**_
The following example creates an SLP problem and then destroys it together with the underlying optimizer problem.

```
XSLPprob nProb;
XPRSprob xProb;

XPRScreateprob(&xProb);
XSLPcreateprob(&nProb, &xProb);
...
XSLPdestroyprob(nProb);
XPRSdestroyprob(xProb);
```
 

_**Further information:**_
When you have finished with the SLP problem, it should be "destroyed" so that the memory used by the problem can be released. Note that this does not destroy the underlying optimizer problem, so a call to `XPRSdestroyprob`should follow `XSLPdestroyprob`as and when you have finished with the underlying optimizer problem.

_**Related topics:**_
`XSLPcreateprob`

#### XSLPevaluatecoef, XPRSslpevaluatecoef

_**Purpose:**_

   Evaluate a coefficient using the current values of the variables

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPevaluatecoef(XSLPprob prob, int row, int col, double *p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer index of the row. 
`col` | Integer index of the column. 
`p_value` | Address of a double precision value to receive the result of the calculation. 

_**Example:**_
The following example sets the value of column 5 to 1.42 and then calculates the coefficient in row 2, column 3. If the coefficient depends on column 5, then a value of 1.42 will be used in the calculation.

```
double value, dValue;

value = 1.42;
XSLPchgvar(prob, 5, NULL, NULL, NULL, NULL, 
           NULL, NULL, &value, NULL, NULL, NULL, 
           NULL);
XSLPevaluatecoef(prob, 2, 3, &dValue);
```
 

_**Further information:**_
The values of the variables are obtained from the solution, or from the `p_value`setting of an SLP variable \(see`XSLPchgvar`and`XSLPgetvar`\).

_**Related topics:**_
`XSLPchgvar`, `XSLPevaluateformula`, `XSLPgetvar`.

#### XSLPevaluateformula, XPRSnlpevaluateformula

_**Purpose:**_

   Evaluate a formula using the current values of the variables

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPevaluateformula(XSLPprob prob, int parsed, const int[] type, const double[] values, double *p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`parsed` | integer indicating whether the formula of the item is in internal unparsed format \( `parsed` =0\) or parsed \(reverse Polish\) format \( `parsed` =1\). 
`type` | Integer array of token types for the formula. 
`values` | Double array of values corresponding to `type`. 
`p_value` | Address of a double precision value to receive the result of the calculation. 

_**Example:**_
The following example calculates the value of column 3 divided by column 6.

```
int n, type[10];
double value, values[10];

n = 0;
type[n] = XSLP_COL; values[n++] = 3;
type[n] = XSLP_COL; values[n++] = 6;
type[n] = XSLP_OP;  values[n++] = XSLP_DIVIDE;
type[n++] = XSLP_EOF;

XSLPevaluateformula(prob, 1, type, values, &value);
```
 

_**Further information:**_
1. The formula in `type` and `values` must be terminated by an `XSLP_EOF` token.
2. The formula cannot include "complicated" functions, such as user functions which return more than one value

_**Related topics:**_
`XSLPevaluatecoef`

#### XSLPfixpenalties, XPRSslpfixpenalties

_**Purpose:**_

   Fixe the values of the error vectors

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `
  int XPRS_CC XSLPfixpenalties(XSLPprob prob, int *p_status);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`p_status` | Return status after fixing the penalty variables: 0 is successful, nonzero otherwise. 

_**Further information:**_
1. The function fixes the values of all error vectors on their current values. It also removes their objective cost contribution.
2. The function is intended to support post optimization analysis, by removing any possible direct effect of the error vectors from the dual and reduced cost values.
3. The XSLPfixpenalties will automatically reoptimize the linearization. However, as the XSLP convergence and infeasibility checks \(regarding the original non-linear problem\) will not be carried out, this function will not update the SLP solution itself. The updated values will be accessible using XPRSgetlpsol instead.

#### XSLPfree

_**Purpose:**_

   Free any memory allocated by Xpress NonLinear and close any open Xpress NonLinear files

_**Topic area:**_ 
Licensing

_**Synopsis:**_

   `int XPRS_CC XSLPfree(void); `

_**Example:**_
The following code frees the Xpress NonLinear memory and then frees the optimizer memory:

```
XSLPfree();
XPRSfree();
```
 
_**Further information:**_
A call to `XSLPfree`only frees the items specific to Xpress NonLinear. `XPRSfree`must be called after `XSLPfree`to free the optimizer structures.

_**Related topics:**_
`XSLPinit`

#### XSLPgetbanner

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   _This function is deprecated and may be removed in future releases._This function has the same effect as XPRSgetbanner

_**Topic area:**_ 
Logging

_**Synopsis:**_

   `int XPRS_CC XSLPgetbanner(char *banner);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`banner` | Character buffer to hold the banner. This will be at most 512 characters including the null terminator. 

#### XSLPgetccoef, XPRSslpgetccoef

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Use`XPRSslpgetcoefstr`instead._
   Retrieve a single matrix coefficient as a formula in a character string. For a simpler version of this function see`XPRSnlpgetformulastr`.

_**Topic areas:**_ 
SLP, Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPgetccoef(XSLPprob prob, int row, int col, 
double *p_factor, char *formula, int maxbytes);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the coefficient. 
`col` | Integer holding the column index for the coefficient. 
`p_factor` | Address of a double precision variable to receive the value of the constant factor multiplying the formula in the coefficient. 
`formula` | Character buffer in which the formula will be placed in the same format as used for input from a file. The formula will be null terminated. 
`maxbytes` | Maximum length of returned formula. 

_**Return value:**_

Value | Description
---------- | ---------- 
`0` | Normal return. 
`20` | formula is too long for the buffer and has been truncated. 
`other` | Error. 

_**Example:**_
The following example displays the formula for the coefficient of column 3 in row 2:

```
char Buffer[60];
double factor;
int Code;

Code = XSLPgetccoef(prob, 2, 3, &factor, Buffer, 60);
switch (Code) {
case 0:  printf("\nFormula is %s",Buffer);
         printf("\nFactor = %lg",factor);
         break;
case 20: printf("\nFormula is too long for the buffer");
         break;
default: printf("\nError accessing coefficient");
         break;
}
```
 
_**Further information:**_
1. If the requested coefficient is constant, then `p_factor` will be set to 1.0 and the value will be formatted in `formula`.
2. If the length of the formula would exceed `maxbytes-1`, the formula is truncated to the last token that will fit, and the \(partial\) formula is terminated with a null character.

_**Related topics:**_
`XPRSslpgetcoefstr`, `XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XPRSslpgetcoefstr

_**Purpose:**_

   Retrieve a single matrix coefficient as a formula in a character string. For a simpler version of this function see`XPRSnlpgetformulastr`.

_**Topic areas:**_ 
SLP, Problem Information

_**Synopsis:**_

   `int XPRS_CC XPRSslpgetcoefstr(XPRSprob prob, int row, int col, double *p_factor, char *formula, int maxbytes, int *p_nbytes);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the coefficient. 
`col` | Integer holding the column index for the coefficient. 
`p_factor` | Address of a double precision variable to receive the value of the constant factor multiplying the formula in the coefficient. 
`formula` | Character buffer in which the formula will be placed in the same format as used for input from a file. This argument may be `NULL` if `maxbytes` is zero. 
`maxbytes` | Length of the `formula` buffer. 
`p_nbytes` | Will be set to the length of the formula, not including the null terminator. 

_**Example:**_
The following example displays the formula for the coefficient of column 3 in row 2:

```
char *buffer;
double factor;
int len;

XPRSslpgetcoefstr(prob, 2, 3, &factor, NULL, 0, &len);
buffer = malloc(len + 1);
XPRSslpgetcoefstr(prob, 2, 3, &factor, buffer, len + 1, NULL);
printf("\nFormula is %s", buffer);
```
 
_**Further information:**_
1. If the requested coefficient is constant, then `p_factor` will be set to 1.0 and the value will be formatted in `formula`.
2. If the length of the formula would exceed `maxbytes-1`, the formula is truncated to the last token that will fit, and the \(partial\) formula is terminated with a null character.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPgetcoefformula, XPRSslpgetcoefformula

_**Purpose:**_

   Retrieve a single matrix coefficient as a formula split into tokens. For a simpler version of this function see`XSLPgetformula`.

_**Topic areas:**_ 
SLP, Problem Information

_**Synopsis:**_

   `
    int XPRS_CC XSLPgetcoefformula(XSLPprob prob, int row, int col,
    double *p_factor, int parsed, int maxtypes, int *p_ntypes, int[] type, double[] value);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the coefficient. 
`col` | Integer holding the column index for the coefficient. 
`p_factor` | Address of a double precision variable to receive the value of the constant factor multiplying the formula in the coefficient. 
`parsed` | Integer indicating whether the formula of the item is to be returned in internal unparsed format \( `parsed` =0\) or parsed \(reverse Polish\) format \( `parsed` =1\). 
`maxtypes` | Maximum number of tokens to return, i.e. length of the `type` and `value` arrays. 
`p_ntypes` | Number of tokens returned in type and value. 
`type` | Integer array to hold the token types for the formula. May be `NULL` if not required. 
`value` | Double array of values corresponding to `type`. May be `NULL` if not required. 

_**Example:**_
The following example displays the formula for the coefficient of column 3 in row 2 in unparsed form:

```
int n, type[10];
double value[10];
double factor;
int ntypes;

XSLPgetcoefformula(prob, 2, 3, &factor, 0, 10, &ntypes, type, value);

for (n=0;type[n] != XSLP_EOF;n++) 
  printf("\nType=%-3d  value=%lg",type[n],value[n]);
```
 
_**Further information:**_
1. The `type` and `value` arrays are terminated by an `XSLP_EOF` token.
2. If `type` and `value` are both null, the number of tokens available will be returned in `p_ntypes`.
3. If `type` or `value` are not null and the number of tokens available exceeds `maxtypes`, an error code will be returned: this behaviour may change in a future release. To determine the number of available tokens, pass null for these arrays.
4. If the requested coefficient is constant, then `p_factor` will be set to 1.0 and the value will be returned with token type `XSLP_CON`.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPgetcoefs, XPRSslpgetcoefs

_**Purpose:**_

   Retrieve the list of positions of the nonlinear coefficients in the problem. For a simpler version of this function see`XSLPgetformularows`.

_**Topic areas:**_ 
SLP, Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPgetcoefs(XSLPprob prob, int *p_ncoefs, int[] rowind, int[] colind);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`p_ncoefs` | Integer used to return the total number of nonlinear coefficients in the problem. 
`rowind` | Integer array used for returning the row positions of the coefficients. May be NULL if not required. 
`colind` | Integer array used for returning the column positions of the coefficients. May be NULL if not required. 

_**Related topics:**_
`XPRSslpgetcoefstr`, `XSLPgetcoefformula`

#### XSLPgetcolinfo, XPRSslpgetcolinfo

_**Purpose:**_

   Get current column information.

_**Topic areas:**_ 
SLP, Solution

_**Synopsis:**_

   `int XSLP_CC XSLPgetcolinfo(XSLPprob prob, int type, int col, XPRSalltype *p_info);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem 
`type` | Type of information \(see below\) 
`col` | Index of the column whose information is to be handled 
`p_info` | Pointer to a variable to receive the information 

_**Example:**_
The following example prints the current value of variable 3:

```
XPRSalltype alltype;
XSLPgetcolinfo(prob, XSLP_COLINFO_VALUE, 3, &alltype);
printf("value[3]=%f\n", alltype.value.real);
```
 
_**Further information:**_
1. If the data is not available, the type of the returned p\_info is set to `XPRStype_undefined`.
2. Please refer to the header file `xprs.h` for the definition of XPRSalltype.
3. The following constants are provided for column information handling:
 * `XSLP_COLINFO_VALUE`: Get the current value of the column
 * `XSLP_COLINFO_RDJ`: Get the current reduced cost of the column
 * `XSLP_COLINFO_DELTAINDEX`: Get the delta variable index associated to the column
 * `XSLP_COLINFO_DELTA`: Get the delta value \(change since previous value\) of the column
 * `XSLP_COLINFO_DELTADJ`: Get the delta variables reduced cost
 * `XSLP_COLINFO_UPDATEROW`: Get the index of the update \(or step bound\) row associated to the column
 * `XSLP_COLINFO_SB`: Get the step bound on the variable
 * `XSLP_COLINFO_SBDUAL`: Get the dual multiplier of the step bound row for the variable
 * `XSLP_COLINFO_DETROW`: The determining row for the variable \(or -1 if it is not determined\)
 * `XSLP_COLINFO_CONVERGENCESTATUS`: The convergence status of the variable \(0 if unconverged, 1-based index of the convergencetolerance that applied otherwise\)
4.  This function can be used to get the current SLP iteration solution in the case where this is not available using `XSLPgetslpsol` due to solution filtering via `XSLP_FILTER`.
5. The convergence status will be an item from the following list:



__convergencestatus__ | __Tolerance__ | 
---------- |  ---------- | 
__0__ | unconverged | 
__1__ | Closure tolerance \(TC\) | 
__2__ | Absolute delta tolerance \(TA\) | 
__3__ | Relative delta tolerance \(RA\) | 
__4__ | Absolute coefficient tolerance \(TM\) | 
__5__ | Relative coefficient tolerance \(RM\) | 
__6__ | Absolute impact tolerance \(TI\) | 
__7__ | Relative impact tolerance \(RI\) | 
__8__ | Absolute slack tolerance \(TS\) | 
__9__ | Relative slack tolerance \(RS\) | 
__other__ | user convergence | 


#### XSLPgetdblattrib

_**Purpose:**_

   Retrieve the value of a double precision problem attribute

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetdblattrib(XSLPprob prob, int attrib, double *p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`attrib` | attribute \(SLP or optimizer\) whose value is to be returned. 
`p_value` | Address of a double precision variable to receive the value. 

_**Example:**_
The following example retrieves the value of the Xpress NonLinear attribute`XSLP_CURRENTDELTACOST`and of the optimizer attribute `XPRS_LPOBJVAL`:

```
double DeltaCost, ObjVal;
XSLPgetdblattrib(prob, XSLP_CURRENTDELTACOST, &DeltaCost);
XSLPgetdblattrib(prob, XPRS_LPOBJVAL, &ObjVal);
```
 
_**Further information:**_
Both SLP and optimizer attributes can be retrieved using this function. If an optimizer attribute is requested, the return value will be the same as that from[XPRSgetdblattrib](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetdblattrib.html), which can similarly be used to obtain both Optimizer and SLP attributes.

_**Related topics:**_
`XSLPgetintattrib`, `XSLPgetstrattrib`

#### XSLPgetdblcontrol

_**Purpose:**_

   Retrieve the value of a double precision problem control

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetdblcontrol(XSLPprob prob, int control, double *p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | control \(SLP or optimizer\) whose value is to be returned. 
`p_value` | Address of a double precision variable to receive the value. 

_**Example:**_
The following example retrieves the value of the Xpress NonLinear control`XSLP_CTOL`and of the optimizer control `XPRS_FEASTOL`:

```
double CTol, FeasTol;
XSLPgetdblcontrol(prob, XSLP_CTOL, &CTol);
XSLPgetdblcontrol(prob, XPRS_FEASTOL, &FeasTol);
```
 
_**Further information:**_
Both SLP and optimizer controls can be retrieved using this function. If an optimizer control is requested, the return value will be the same as that from[XPRSgetdblcontrol](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetdblcontrol.html), which can similarly be used to obtain both Optimizer and SLP controls.

_**Related topics:**_
`XSLPgetintcontrol`, `XSLPgetstrcontrol`, `XSLPsetdblcontrol`

#### XSLPgetdf

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Get a distribution factor.

_**Topic areas:**_ 
SLP, Problem Information

_**Synopsis:**_

   `int XSLP_CC XSLPgetdf(XSLPprob prob, int col, int row, double *p_value)`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`col` | The index of the column whose distribution factor is to be retrieved. 
`row` | The index of the row from which the distribution factor is to be taken. 
`p_value` | Address of a double precision variable to receive the value of the distribution factor. May be `NULL` if not required. 

_**Example:**_
The following example retrieves the value of the distribution factor for column 282 in row 134 and changes it to be twice as large.

```
double value;
XSLPgetdf(prob,282,134,&value);
value = value * 2;
XSLPchgdf(prob,282,134,&value);
```
 
_**Further information:**_
The _distribution factor_of a column in a row is the matrix coefficient of the corresponding delta vector in the row. Distribution factors are used in conventional recursion models, and are essentially normalized first-order derivatives. Xpress-SLP can accept distribution factors instead of initial values, provided that the values of the variables involved can all be calculated after optimization using determining rows, or by a callback.

_**Related topics:**_
`XSLPadddfs`, `XSLPchgdf`, `XSLPloaddfs`

#### XSLPgetformula, XPRSnlpgetformula

_**Purpose:**_

   Retrieve a single matrix formula as a formula split into tokens.

_**Topic area:**_ 
Problem Information

_**Synopsis:**_

   `
    int XPRS_CC XSLPgetformula(XSLPprob prob, int row, int parsed, int maxtypes, int *p_ntypes, int[] type, double[] value);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the formula. 
`parsed` | Integer indicating whether the formula of the row is to be returned in internal unparsed format \( `parsed` =0\) or parsed \(reverse Polish\) format \( `parsed` =1\). 
`maxtypes` | Maximum number of tokens to return, i.e., the length of the type and value arrays. 
`p_ntypes` | Will be set to the length of the formula, including the `XSLP_EOF` token. 
`type` | Integer array to hold the token types for the formula. May be `NULL` if `maxtypes` is zero. 
`value` | Double array of values corresponding to `type`. May be `NULL` if `maxtypes` is zero. 

_**Example:**_
The following example displays the nonlinear formula in row 2, column 3 in unparsed form:

```
int ntypes, n;
int *type;
double *value;

XSLPgetformula(prob, 2, 0, 0, &ntypes, NULL, NULL);
type = malloc(ntypes * sizeof(int));
value = malloc(ntypes * sizeof(double));
XSLPgetformula(prob, 2, 0, 10, &ntypes, type, value);

for (n = 0; type[n] != XSLP_EOF; n++)
  printf("\nType=%-3d  value=%lg", type[n], value[n]);
```
 
_**Further information:**_
1. The `type` and `value` arrays are terminated by an `XSLP_EOF` token.
2. If `type` and `value` are both null, the number of tokens available will be returned in `p_ntypes`.
3. If `type` or `value` are not null and the number of tokens available exceeds `maxtypes`, an error code will be returned: this behaviour may change in a future release. To determine the number of available tokens, pass null for these arrays.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XPRSnlpgetformulastr

_**Purpose:**_

   Retrieve a single matrix formula in a character string.

_**Topic area:**_ 
Problem Information

_**Synopsis:**_

   `int XPRS_CC XPRSnlpgetformulastr(XPRSprob prob, int row, char *formula, int maxbytes, int *p_nbytes);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the formula. 
`formula` | Character buffer in which the formula will be placed in the same format as used for input from a file. This argument may be `NULL` if `maxbytes` is zero. 
`maxbytes` | Length of the `formula` buffer. 
`p_nbytes` | Will be set to the length of the formula, not including the null terminator. 

_**Example:**_
The following retrieves a formula in text form:

```
char *buffer;
int len;

XPRSnlpgetformulastr(prob, 2, NULL, 0, &len);
buffer = malloc(len + 1);
XPRSnlpgetformulastr(prob, 2, buffer, len + 1, NULL);
```
 
_**Further information:**_
If the length of the formula would exceed `maxbytes-1`, the formula is truncated to the last token that will fit, and the \(partial\) formula is terminated with a null character.

_**Related topics:**_
`XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPgetformulastring, XPRSnlpgetformulastring

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Use`XPRSnlpgetformulastr`instead._
   Retrieve a single matrix formula in a character string.

_**Topic area:**_ 
Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPgetformulastring(XSLPprob prob, int row, char *formula, int maxbytes);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the formula. 
`formula` | Character buffer in which the formula will be placed in the same format as used for input from a file. The formula will be null terminated. 
`maxbytes` | Maximum length of returned formula. 

_**Return value:**_

Value | Description
---------- | ---------- 
`0` | Normal return. 
`20` | Formula is too long for the buffer and has been truncated. 
`other` | Error. 

_**Example:**_
The following retrieves a formula in text form:

```
char Buffer[60];
int Code;

Code = XSLPgetformulastring(prob, 2, Buffer, 60);
switch (Code) {
case 0:  printf("\nFormula is %s",Buffer);
         break;
case 20: printf("\nFormula is too long for the buffer");
         break;
default: printf("\nError accessing formula");
         break;
}
```
 
_**Further information:**_
If the length of the formula would exceed `maxbytes-1`, the formula is truncated to the last token that will fit, and the \(partial\) formula is terminated with a null character.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPaddformulas`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPgetformularows, XPRSnlpgetformularows

_**Purpose:**_

   Retrieve the list of positions of the nonlinear formulas in the problem

_**Topic area:**_ 
Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPgetformularows(XSLPprob prob, int *p_nformulas, int[] rowind);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`p_nformulas` | Integer used to return the total number of nonlinear formulas in the problem. 
`rowind` | Integer array used for returning the row positions of the nonlinear formulas. May be NULL if not required. 

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPgetindex

_**Purpose:**_

   Retrieve the index of an Xpress NonLinear entity with a given name

_**Topic areas:**_ 
Problem Information, User Functions

_**Synopsis:**_

   `int XPRS_CC XSLPgetindex(XSLPprob prob, int type, char *name, int *p_index);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`type` |  | type of entity. The following are defined:
&nbsp; | `XSLP_USERFUNCNAMES` | `(=6)` User functions;
&nbsp; | `XSLP_INTERNALFUNCNAMES` | `(=7)` Internal functions;
&nbsp; | `XSLP_USERFUNCNAMESNOCASE` | `(=8)` User functions, case insensitive;
&nbsp; | `XSLP_INTERNALFUNCNAMESNOCASE` | `(=9)` Internal functions, case insensitive;
&nbsp; |  | 
The constants 1 \(for row names\) and 2 \(for column names\) may also be used.

`name` | | Character string containing the name, terminated by a null character. 
`p_index` | | Integer to receive the index of the item. 

_**Example:**_
The following example retrieves the index of the internal `SIN`function using both an upper-case and a lower case version of the name.

```
int UpperIndex, LowerIndex;
XSLPgetindex(prob, XSLP_INTERNALFUNCNAMESNOCASE,
             "SIN", &UpperIndex);
XSLPgetindex(prob, XSLP_INTERNALFUNCNAMESNOCASE,
             "sin", &LowerIndex);
```
 `UpperIndex`and `LowerIndex`will contain the same value because the search was made using case-insensitive matching.

_**Further information:**_
All entities count from 1. This includes the use of 1 or 2 \(row or column\) for `type`. A value of zero returned in `p_index`means there is no matching item. The case-insensitive types will find the first match regardless of the case of `name`or of the defined function.

#### XSLPgetintattrib

_**Purpose:**_

   Retrieve the value of an integer problem attribute

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetintattrib(XSLPprob prob, int attrib, int *p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`attrib` | attribute \(SLP or optimizer\) whose value is to be returned. 
`p_value` | Address of an integer variable to receive the value. 

_**Further information:**_
Both SLP and optimizer attributes can be retrieved using this function. If an optimizer attribute is requested, the return value will be the same as that from[XPRSgetintattrib](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetintattrib.html), which can similarly be used to obtain both Optimizer and SLP attributes.

_**Related topics:**_
`XSLPgetdblattrib`, `XSLPgetstrattrib`

#### XSLPgetintcontrol

_**Purpose:**_

   Retrieve the value of an integer problem control

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetintcontrol(XSLPprob prob, int control, int *p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | control \(SLP or optimizer\) whose value is to be returned. 
`p_value` | Address of an integer variable to receive the value. 

_**Example:**_
The following example retrieves the value of the Xpress NonLinear control`XSLP_ALGORITHM`and of the optimizer control `XPRS_DEFAULTALG`:

```
int Algorithm, DefaultAlg;
XSLPgetintcontrol(prob, XSLP_ALGORITHM, &Algorithm);
XSLPgetintcontrol(prob, XPRS_DEFAULTALG, &DefaultAlg);
```
 
_**Further information:**_
Both SLP and optimizer controls can be retrieved using this function. If an optimizer control is requested, the return value will be the same as that from[XPRSgetintcontrol](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetintcontrol.html), which can similarly be used to obtain both Optimizer and SLP controls.

_**Related topics:**_
`XSLPgetdblcontrol`, `XSLPgetstrcontrol`, `XSLPsetintcontrol`

#### XSLPgetlasterror

_**Purpose:**_

   Retrieve the error message corresponding to the last Xpress NonLinear error during an SLP run

_**Topic area:**_ 
Misc

_**Synopsis:**_

   `int XPRS_CC XSLPgetlasterror(XSLPprob prob, int *p_code, char *msg);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`p_code` | Address of an integer to receive the message number of the last error. May be `NULL` if not required. 
`msg` | Character buffer to receive the error message. The error message will never be longer than 256 characters. May be `NULL` if not required. 

_**Example:**_
The following example checks the return code from reading a matrix. If the code is nonzero then an error has occurred, and the error number is retrieved for further processing.

```
int Error, code;
if (Error=XSLPreadprob(prob, "Matrix", "")) {
  XSLPgetlasterror(prob, &code, NULL);
  MyErrorHandler(code);
}
```
 
_**Further information:**_
1. In general, Xpress NonLinear functions return a value of 32 to indicate a non-recoverable error. `XSLPgetlasterror` can retrieve the actual error number and message.
2. In case no SLP error code was returned, the function will check the underlying XPRS libary for any errors reported.

#### XSLPgetptrattrib

_**Purpose:**_

   Retrieve the value of a problem pointer attribute

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetptrattrib(XSLPprob prob, int attrib, void **p_value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`attrib` | attribute whose value is to be returned. 
`p_value` | Address of a pointer to receive the value. 

_**Example:**_
The following example retrieves the value of the Xpress NonLinear pointer attribute`XSLP_XPRSPROBLEM`which is the underlying optimizer problem pointer:

```
XPRSprob xprob;
XSLPgetptrattrib(prob, XSLP_XPRSPROBLEM, &xprob);
```
 
_**Further information:**_
This function is normally used to retrieve the underlying optimizer problem pointer, as shown in the example.

_**Related topics:**_
`XSLPgetdblattrib`, `XSLPgetintattrib`, `XSLPgetstrattrib`

#### XSLPgetrowinfo, XPRSslpgetrowinfo

_**Purpose:**_

   Get current row information.

_**Topic areas:**_ 
SLP, Solution

_**Synopsis:**_

   `int XSLP_CC XSLPgetrowinfo(XSLPprob prob, int type, int row, XPRSalltype *p_info);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem 
`type` | Type of information \(see below\) 
`row` | Index of the row whose information is to be handled 
`p_info` | Pointer to a variable to receive the information 

_**Example:**_
The following example prints the current penalty factor of row 1:

```
XPRSalltype alltype;
XSLPgetrowinfo(prob, XSLP_ROWINFO_CURRENTPENALTYFACTOR, 1, &alltype);
printf("penaltyfactor[1]=%f\n", alltype.value.real);
```
 
_**Further information:**_
1. If the data is not available, the type of the returned p\_info is set to `XPRStype_undefined`.
2. Please refer to the header file `xprs.h` for the definition of XPRSalltype.
3. The following constants are provided for row information handling:
 * `XSLP_ROWINFO_SLACK`: Get the current slack value of the row
 * `XSLP_ROWINFO_DUAL`: Get the current dual multiplier of the row
 * `XSLP_ROWINFO_NUMPENALTYERRORS`: Get the number of times the penalty error vector has been active for the row
 * `XSLP_ROWINFO_MAXPENALTYERROR`: Get the maximum size of the penalty error vector activity for the row
 * `XSLP_ROWINFO_TOTALPENALTYERROR`: Get the total size of the penalty error vector activity for the row
 * `XSLP_ROWINFO_CURRENTPENALTYERROR`: Get the size of the penalty error vector activity in the current iteration for the row
 * `XSLP_ROWINFO_CURRENTPENALTYFACTOR`: Set the size of the penalty error factor for the current iteration for the row
 * `XSLP_ROWINFO_PENALTYCOLUMNPLUS`: Get the index of the positive penalty column for the row \(+\)
 * `XSLP_ROWINFO_PENALTYCOLUMNPLUSVALUE`: Get the value of the positive penalty column for the row \(+\)
 * `XSLP_ROWINFO_PENALTYCOLUMNPLUSDJ`: Get the reduced cost of the positive penalty column for the row \(+\)
 * `XSLP_ROWINFO_PENALTYCOLUMNMINUS`: Get the index of the negative penalty column for the row \(-\)
 * `XSLP_ROWINFO_PENALTYCOLUMNMINUSVALUE`: Get the value of the negative penalty column for the row \(-\)
 * `XSLP_ROWINFO_PENALTYCOLUMNMINUSDJ`: Get the reduced cost of the negative penalty column for the row \(-\)
4.  This function can be used to get the current SLP iteration solution in the case where this is not available using `XSLPgetslpsol` due to solution filtering via `XSLP_FILTER`.

#### XSLPgetrowstatus, XPRSslpgetrowstatus

_**Purpose:**_

   Retrieve the status setting of a constraint

_**Topic areas:**_ 
SLP, Solution, Bit-vector

_**Synopsis:**_

   `int XPRS_CC XSLPgetrowstatus(XSLPprob prob, int row, int *p_status);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row whose data is to be obtained. 
`p_status` | Address of an integer to receive the status settings. 

_**Example:**_
This recovers the status of the rows of the matrix of the current problem and reports those which are flagged as enforced constraints.

```
int iRow, nRow, status;
XSLPgetintattrib(prob, XPRS_ROWS, &nRow);
for (iRow=0;iRow<nRow;iRow++) {
  XSLPgetrowstatus(prob, iRow, &status);
  if (status & 0x800) printf("\nRow %d is enforced");
}
```
 
_**Further information:**_
See the section on bitmap settings for details on the possible information in `p_status`.

_**Related topics:**_
`XSLPchgrowstatus`

#### XSLPgetrowwt, XPRSslpgetrowwt

_**Purpose:**_

   Get the initial penalty error weight for a row

_**Topic areas:**_ 
SLP, Data Information

_**Synopsis:**_

   `int XSLP_CC XSLPgetrowwt(XSLPprob prob, int row, double *p_weight)`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the row whose weight is to be retrieved. 
`p_weight` | Address of a double precision variable to receive the value of the weight. 

_**Example:**_
The following example gets the initial weight of row number 2.

```
double weight;
XSLPgetrowwt(prob,2,&weight)
```
 

_**Further information:**_
The initial row weight is used only when the augmented structure is created. After that, the current weighting can be accessed using`XSLPgetrowinfo`.

_**Related topics:**_
`XSLPchgrowwt`, `XSLPgetrowinfo`

#### XSLPgetslpsol, XPRSgetnlpsol

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Use[`XPRSgetsolution`](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetsolution.html)and related functions instead._
   Obtain the current SLP solution values

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPgetslpsol(XSLPprob prob, double *x, double *slack,
   double *duals, double *djs);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`x` | Double array of length `XSLP_ORIGINALCOLS` to hold the values of the primal variables. May be `NULL` if not required. 
`slack` | Double array of length `XSLP_ORIGINALROWS` to hold the values of the slack variables. May be `NULL` if not required. 
`duals` | Double array of length `XSLP_ORIGINALROWS` to hold the values of the dual variables. May be `NULL` if not required. 
`djs` | Double array of length `XSLP_ORIGINALCOLS` to hold the reduced costs of the primal variables. May be `NULL` if not required. 

_**Example:**_
The following code fragment recovers the values and reduced costs of the primal variables for the current SLP solution:

```
XSLPprob prob;
int nCol;
double *val, *djs;
XSLPgetintattrib(prob,XSLP_ORIGINALCOLS,&nCol);
val = malloc(nCol*sizeof(double));
djs = malloc(nCol*sizeof(double));
XSLPgetslpsol(prob,val,NULL,NULL,djs);

```
 
_**Further information:**_
1. The behavior of this function depends on the `XSLP_FILTER` control. If `XSLP_FILTER_KEEPBEST` is set \(which is the default\), then `XSLPgetslpsol` will return the best solution seen so far, otherwise the solution of the most recent SLP iteration will be returned. The current iteration solution \(in the presolved space\) can be obtained from `XSLPgetcolinfo`.
2. `XSLPgetslpsol` can be called at any time after an SLP iteration has completed, and will return the same values even if the problem is subsequently changed. `XSLPgetslpsol` returns the solution in the original space. To access the values of any augmentation columns or rows, use `XPRSgetlpsol`; accessing the augmented solution is only recommended if `XSLP_PRESOLVELEVEL` indicates that the problem dimensions should not be changed in presolve.

#### XSLPgetstrattrib

_**Purpose:**_

   Retrieve the value of a string problem attribute

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetstrattrib(XSLPprob prob, int attrib, char *value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`attrib` | attribute \(SLP or optimizer\) whose value is to be returned. 
`value` | Character buffer to receive the value. 

_**Example:**_
The following example retrieves the value of the Xpress NonLinear attribute`XSLP_VERSIONDATE`and of the optimizer attribute `XPRS_MATRIXNAME`:

```
char VersionDate[200], MatrixName[200];
XSLPgetstrattrib(prob, XSLP_VERSIONDATE, VersionDate);
XSLPgetstrattrib(prob, XPRS_MATRIXNAME, MatrixName);
```
 
_**Further information:**_
Both SLP and optimizer attributes can be retrieved using this function. If an optimizer attribute is requested, the return value will be the same as that from[XPRSgetstrattrib](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetstrattrib.html), which can similarly be used to obtain both Optimizer and SLP attributes.

_**Related topics:**_
`XSLPgetdblattrib`, `XSLPgetintattrib`

#### XSLPgetstrcontrol

_**Purpose:**_

   Retrieve the value of a string problem control

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPgetstrcontrol(XSLPprob prob, int control, char *value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | control \(SLP or optimizer\) whose value is to be returned. 
`value` | Character buffer to receive the value. 

_**Further information:**_
Both SLP and optimizer controls can be retrieved using this function. If an optimizer control is requested, the return value will be the same as that from[XPRSgetstrcontrol](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSgetstrcontrol.html), which can similarly be used to obtain both Optimizer and SLP controls.

_**Related topics:**_
`XSLPgetdblcontrol`, `XSLPgetintcontrol`, `XSLPsetstrcontrol`

#### XSLPgettolset

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Retrieve the values of a set of convergence tolerances for an SLP problem.

_**Topic areas:**_ 
SLP, SLP-convergence

_**Synopsis:**_

   `int XPRS_CC XSLPgettolset(XSLPprob prob, int tolset, int *p_status, double *tols);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`tolset` | The index of the tolerance set. 
`p_status` | Address of integer to receive the bit-map of status settings. May be `NULL` if not required. 
`tols` | Array of 9 double-precision values to hold the tolerances. May be `NULL` if not required. 

_**Example:**_
The following example retrieves the values for tolerance set 3 and prints those which are set:

```
double tols[9];
int i, status;
XSLPgettolset(prob, 3, &status, tols);
for (i=0;i<9;i++) 
  if (status & (1<<i)) 
    printf("\nTolerance %d = %lg",i,tols[i]);
```
 
_**Further information:**_
1. If `p_status` or `tols` is `NULL`, then the corresponding information will not be returned.
2. If `tols` is not `NULL`, then a set of 9 values will always be returned. `p_status` indicates which of these values is active as follows. Bit `n` of `p_status` is set if `tols[n]` is active, where `n` is:



__Entry / Bit__ | __Tolerance__ | __XSLP constant__ | __XSLP bit constant__ | 
---------- |  ---------- | ---------- | ---------- | 
__0__ | Closure tolerance \(TC\) | `XSLP_TOLSET_TC` | `XSLP_TOLSETBIT_TC` | 
__1__ | Absolute delta tolerance \(TA\) | `XSLP_TOLSET_TA` | `XSLP_TOLSETBIT_TA` | 
__2__ | Relative delta tolerance \(RA\) | `XSLP_TOLSET_RA` | `XSLP_TOLSETBIT_RA` | 
__3__ | Absolute coefficient tolerance \(TM\) | `XSLP_TOLSET_TM` | `XSLP_TOLSETBIT_TM` | 
__4__ | Relative coefficient tolerance \(RM\) | `XSLP_TOLSET_RM` | `XSLP_TOLSETBIT_RM` | 
__5__ | Absolute impact tolerance \(TI\) | `XSLP_TOLSET_TI` | `XSLP_TOLSETBIT_TI` | 
__6__ | Relative impact tolerance \(RI\) | `XSLP_TOLSET_RI` | `XSLP_TOLSETBIT_RI` | 
__7__ | Absolute slack tolerance \(TS\) | `XSLP_TOLSET_TS` | `XSLP_TOLSETBIT_TS` | 
__8__ | Relative slack tolerance \(RS\) | `XSLP_TOLSET_RS` | `XSLP_TOLSETBIT_RS` | 

3. The XSLP\_TOLSET constants can be used to access the corresponding entry in the value arrays, while the XSLP\_TOLSETBIT constants are used to set or retrieve which tolerance values are used for a given SLP variable.

_**Related topics:**_

_**Related topics:**_
`XSLPaddtolsets`, `XSLPchgtolset`, `XSLPdeltolsets`, `XSLPloadtolsets`


#### XSLPgetvar

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Retrieve information about an SLP variable.

_**Topic area:**_ 
Data Information

_**Synopsis:**_

   `int XPRS_CC XSLPgetvar(XSLPprob prob, int col, int *p_detrow, 
double *p_initstepbound, double *p_stepbound, double *p_penalty, 
double *p_damp, double *p_initial, double *p_value, int *p_tolset, 
int *p_history, int *p_converged, int *p_vartype, int *p_delta, 
int *p_penaltydelta, int *p_updaterow,  double *p_old);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`col` | | The index of the column. 
`p_detrow` | | Address of an integer to receive the index of the determining row. May be `NULL` if not required. 
`p_initstepbound` | | Address of a double precision variable to receive the value of the initial step bound of the variable. May be `NULL` if not required. 
`p_stepbound` | | Address of a double precision variable to receive the value of the current step bound of the variable. May be `NULL` if not required. 
`p_penalty` | | Address of a double precision variable to receive the value of the penalty delta weighting of the variable. May be `NULL` if not required. 
`p_damp` | | Address of a double precision variable to receive the value of the current damping factor of the variable. May be `NULL` if not required. 
`p_initial` | | Address of a double precision variable to receive the value of the initial value of the variable. May be `NULL` if not required. 
`p_value` | | Address of a double precision variable to receive the current activity of the variable. May be `NULL` if not required. 
`p_tolset` | | Address of an integer to receive the index of the tolerance set of the variable. May be `NULL` if not required. 
`p_history` | | Address of an integer to receive the SLP history of the variable. May be `NULL` if not required. 
`p_converged` | | Address of an integer to receive the convergence status of the variable as defined in the "Convergence Criteria" section \(The returned value will match the numbering of the tolerances\). May be `NULL` if not required. 
`p_vartype` |  | Address of an integer to receive the status settings \(a bitmap defining the existence of certain properties for this variable\). The following bits are defined:
&nbsp; | `Bit 1:` | Variable has a delta vector
&nbsp; | `Bit 2:` | Variable has an initial value
&nbsp; | `Bit 14:` | Variable is the reserved "=" column
&nbsp; |  | Other bits are reserved for internal use. May be `NULL`if not required.
`p_delta` | | Address of an integer to receive the index of the delta vector for the variable. May be `NULL` if not required. 
`p_penaltydelta` | | Address of an integer to receive the index of the first penalty delta vector for the variable. The second penalty delta immediately follows the first. May be `NULL` if not required. 
`p_updaterow` | | Address of an integer to receive the index of the update row for the variable. May be `NULL` if not required. 
`p_old` | | Address of a double precision variable to receive the value of the variable at the previous SLP iteration. May be `NULL` if not required. 

_**Example:**_
The following example retrieves the current value, convergence history and status for column 3.

```
int converged, history;
double value;

XSLPgetvar(prob, 3, NULL, NULL, NULL, 
           NULL, NULL, NULL, &value,
           NULL, &history, &converged,
           NULL, NULL, NULL, NULL, NULL);
```
 
_**Further information:**_
1. If `col` refers to a column which is not an SLP variable, then all the return values will indicate that there is no corresponding data.
2. `p_detrow` will be set to -1 if there is no determining row.
3. `p_delta`, `p_penaltydelta` and `p_updaterow` will be set to -1 if there is no corresponding item.
4. Current values, deltas, step bounds, convergence status, update row and determining row can also be obtained individually through `XSLPgetcolinfo`.

_**Related topics:**_
`XSLPaddvars`, `XSLPgetcolinfo`, `XSLPchgvar`, `XSLPdelvars`, `XSLPloadvars`

#### XSLPimportlibfunc, XPRSnlpimportlibfunc

_**Purpose:**_

   Imports a function from a library file to be called as a user function

_**Topic area:**_ 
User Functions

_**Synopsis:**_

   `int XPRS_CC XSLPimportlibfunc(XSLPprob prob,const char * libname, const char * funcname, XPRSfunctionptraddr p_function, int * p_status );`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`libname` | | Filename of the library. 
`funcname` | | Fucntion name inside the library. 
`p_function` | | Function pointer to return the loaded function. 
`p_status` |  | Outcome of the load operation
&nbsp; | `0` | success.
&nbsp; | `1` | library file not found.
&nbsp; | `2` | library function in library file not found.

_**Further information:**_
On systems where necessary, Xpress will hold the handle of the library opened and free up when the problem object `prob`is destroyed. The type `XPRSfunctionptraddr`is a pointer to a generic function pointer.

_**Related topics:**_
`XSLPadduserfunction`, `XSLPdeluserfunction`

#### XSLPinit

_**Purpose:**_

   Initializes the Xpress NonLinear system

_**Topic area:**_ 
Licensing

_**Synopsis:**_

   `int XPRS_CC XSLPinit();`

_**Argument:**_

Name |  Description
---------- | ---------- 
`none` |  

_**Example:**_
The following example initiates the Xpress NonLinear system and prints the banner.

```
char Buffer[256];
XPRSinit();
XSLPinit();
XSLPgetbanner(Buffer);
```
 `XPRSinit`initializes the Xpress optimizer; `XSLPinit`then initializes the SLP module, so that the banner contains information from both systems.

_**Further information:**_
`XSLPinit`must be the first call to the Xpress NonLinear system except for `XSLP get banner`and `XSLP get version`. It initializes any global parts of the system if required. The call to `XSLPinit`must be preceded by a call to `XPRSinit`to initialize the Optimizer Library part of the system first.

_**Related topics:**_
`XSLPfree`

#### XSLPinterrupt

_**Purpose:**_

   Interrupts the current SLP optimization

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPinterrupt(int reason);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`reason` | Interrupt code to be propagated. 

_**Further information:**_
Provides functionality to stop the SLP optimization process from inside a callback.The following constants are provided for the parameter value:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
Value 1 | `XSLP_STOP_TIMELIMIT` | 
Value 2 | `XSLP_STOP_CTRLC` | 
Value 3 | `XSLP_STOP_NODELIMIT` | 
Value 4 | `XSLP_STOP_ITERLIMIT` | 
Value 5 | `XSLP_STOP_MIPGAP` | 
Value 6 | `XSLP_STOP_SOLLIMIT` | 
Value 9 | `XSLP_STOP_USER` | 


#### XSLPitemname

_**Purpose:**_

   Retrieves the name of an Xpress NonLinear entity or the value of a function token as a character string.

_**Topic area:**_ 
Names Manager

_**Synopsis:**_

   `int XPRS_CC XSLPitemname(XSLPprob prob, int type, double value, char *buffer);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`type` | Integer holding the type of Xpress NonLinear entity. This can be any one of the token types described in the section  _Xpress NonLinear Formulae_. 
`value` | Double precision value holding the index or value of the token. The use and meaning of the value is as described in the section  _Xpress NonLinear Formulae_. 
`buffer` | Character buffer to hold the result, which will be terminated with a null character. 

_**Example:**_
The following example displays the formula for the coefficient in row 2, column 3 in unparsed form:

```

int n, type[10];
double value[10];
char buffer[60];
int TokenCount;

XSLPgetcoefformula(prob, 2, 3, &Factor, 0, 10, &TokenCount, type, value);

printf("\n");
for (n=0;type[n] != XSLP_EOF;n++) {
  XSLPitemname(prob, type[n], value[n], buffer);
  printf(" %s", buffer);
}
```
 
_**Further information:**_
1. If a name has not been provided for an Xpress NonLinear entity, then an internally-generated name will be used.
2. Numerical values will be formatted as fixed-point or floating-point depending on their size.

#### XSLPloadcoefs, XPRSslploadcoefs

_**Purpose:**_

   Load non-linear coefficients into the SLP problem. For a simpler version of this function see`XSLPloadformulas`.

_**Topic areas:**_ 
SLP, Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPloadcoefs(XSLPprob prob, int ncoefs, const int[] rowind, 
const int[] colind, const double[] factor, const int[] formulastart, int parsed, 
const int[] type, const double[] coef);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ncoefs` | Number of non-linear coefficients to be loaded. 
`rowind` | Integer array holding index of row for the coefficient. 
`colind` | Integer array holding index of column for the coefficient. 
`factor` | Double array holding factor by which formula is scaled. If this is `NULL`, then a value of 1.0 will be used. 
`formulastart` | Integer array of length `ncoefs+1` holding the start position in the arrays `type` and `coef` of the formula for the coefficients. The last element should be set to the next position after the end of the last formula. 
`parsed` | Integer indicating whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the formula for each coefficient. 
`coef` | Array of values corresponding to the types in `type`. 

_**Example:**_
Assume that the rows and columns of `prob`are named `Row1`, `Row2`..., `Col1`, `Col2`... The following example loads coefficients representing:

 `Col2 * Col3 + Col6 * Col2ˆ 2`into `Row1`and

 `Col2 ˆ  2`into `Row3`.

```
int rowind[3], colind[3], formulastart[4], type[8];
int n, ncoefs;
double coef[8];

rowind[0] = 1; colind[0] = 2;
rowind[1] = 1; colind[1] = 6;
rowind[2] = 3; colind[2] = 2;

n = ncoefs = 0;
formulastart[ncoefs++] = n; 
type[n] = XSLP_COL; coef[n++] = 3;
type[n++] = XSLP_EOF;

formulastart[ncoefs++] = n; 
type[n] = XSLP_COL; coef[n++] = 2;
type[n] = XSLP_COL; coef[n++] = 2;
type[n] = XSLP_OP;  coef[n++] = XSLP_MULTIPLY;
type[n++] = XSLP_EOF;

formulastart[ncoefs++] = n;
type[n] = XSLP_COL; coef[n++] = 2;
type[n++] = XSLP_EOF;

formulastart[ncoefs] = n;

XSLPloadcoefs(prob, ncoefs, rowind, colind,
             NULL, formulastart, 1, type, coef);
```
 
The first coefficient in `Row1` is in `Col2` and has the formula `Col3`, so it represents `Col2 * Col3`.

The second coefficient in `Row1` is in `Col6` and has the formula `Col2 * Col2` so it represents `Col6 * Col2ˆ 2`. The formulae are described as _parsed_ \( `parsed` =1\), so the formula is written as

 `Col2 Col2 *`

rather than the unparsed form

 `Col2 * Col2`

The last coefficient, in `Row3`, is in `Col2` and has the formula `Col2`, so it represents `Col2 * Col2`.


_**Further information:**_
1. The j<sup>th</sup> coefficient is made up of two parts: `factor` and `Formula`. `factor` is a constant multiplier, which can be provided in the `factor` array. If Xpress NonLinear can identify a constant factor in `Formula`, then it will use that as well, to minimize the size of the formula which has to be calculated. `Formula` is made up of a list of tokens in `type` and `coef` starting at `formulastart[j]`. The tokens follow the rules for parsed or unparsed formulae as indicated by the setting of `parsed`. The formula must be terminated with an `XSLP_EOF` token. If several coefficients share the same formula, they can have the same value in `formulastart`. For possible token types and values see  _Xpress NonLinear Formulae_.
2. The `load` functions load items into the SLP problem. Any existing items of the same type are deleted first. The corresponding `add` functions add or replace items leaving other items of the same type unchanged.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPloaddfs

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Load a set of distribution factors.

_**Topic areas:**_ 
SLP, Data Input

_**Synopsis:**_

   `int XSLP_CC XSLPloaddfs(XSLPprob prob, int ndfs, const int *colind, const int *rowind, const double *value)`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ndfs` | The number of distribution factors. 
`colind` | Array of indices of columns whose distribution factor is to be changed. 
`rowind` | Array of indices of the rows where each distribution factor applies. 
`value` | Array of double precision variables holding the new values of the distribution factors. 

_**Example:**_
The following example loads distribution factors as follows:

column 282 in row 134 = 0.1

column 282 in row 136 = 0.15

column 285 in row 133 = 1.0.

Any other first-order derivative placeholders are set to`XSLP_DELTA_Z`.

```
int colind[3], rowind[3];
double value[3];
colind[0] = 282;  rowind[0] = 134; value[0] = 0.1;
colind[1] = 282;  rowind[1] = 136; value[1] = 0.15;
colind[2] = 285;  rowind[2] = 133; value[2] = 1.0;
XSLPloaddfs(prob,3,colind,rowind,value);
```
 
_**Further information:**_
1. The _distribution factor_ of a column in a row is the matrix coefficient of the corresponding delta vector in the row. Distribution factors are used in conventional recursion models, and are essentially normalized first-order derivatives. Xpress-SLP can accept distribution factors instead of initial values, provided that the values of the variables involved can all be calculated after optimization using determining rows, or by a callback.
2. The `add` functions load additional items into the SLP problem. The corresponding `load` functions delete any existing items first.

_**Related topics:**_
`XSLPadddfs`, `XSLPchgdf`, `XSLPgetdf`

#### XSLPloadformulas, XPRSnlploadformulas

_**Purpose:**_

   Load non-linear formulas into the SLP problem

_**Topic area:**_ 
Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPloadformulas(XSLPprob prob, int nnlpcoefs, const int[] rowind, const int[] formulastart, int parsed, const int[] type, const double[] value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`nnlpcoefs` | Number of non-linear coefficients to be loaded. 
`rowind` | Integer array holding index of row for the coefficient. 
`formulastart` | Integer array of length `nnlpcoefs+1` holding the start position in the arrays `type` and `value` of the formula for the coefficients. The last element should be set to the next position after the end of the last formula. 
`parsed` | Integer indicating whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the formula for each coefficient. 
`value` | Array of values corresponding to the types in `type`. 

_**Example:**_
Assume that the rows and columns of `prob`are named `Row0`, `Row1`..., `Col0`, `Col1`... The following example adds coefficients representing:

 `Col2 * Col3 * Col6ˆ 2`into `Row1`and

 `Col2 * Col3 ˆ  2`into `Row3`.

```
int rowind[3], formulastart[4], type[8];
int n, nnlpcoefs;
double value[8];

rowind[0] = 1; 
rowind[1] = 1; 
rowind[2] = 3; 

n = nnlpcoefs = 0;
formulastart[nnlpcoefs++] = n; 
type[n] = XSLP_COL; value[n++] = 3;
type[n++] = XSLP_EOF;

formulastart[nnlpcoefs++] = n; 
type[n] = XSLP_COL; value[n++] = 2;
type[n] = XSLP_COL; value[n++] = 3;
type[n] = XSLP_OP;  value[n++] = XSLP_MULTIPLY;
type[n] = XSLP_COL; value[n++] = 6;
type[n] = XSLP_CON; value[n++] = 2;
type[n] = XSLP_OP;  value[n++] = XSLP_EXPONENT;
type[n] = XSLP_OP;  value[n++] = XSLP_MULTIPLY;
type[n++] = XSLP_EOF;

formulastart[nnlpcoefs++] = n;
type[n] = XSLP_COL; value[n++] = 2;
type[n] = XSLP_COL; value[n++] = 3;
type[n] = XSLP_CON; value[n++] = 2;
type[n] = XSLP_OP;  value[n++] = XSLP_EXPONENT;
type[n] = XSLP_OP;  value[n++] = XSLP_MULTIPLY;
type[n++] = XSLP_EOF;

formulastart[nnlpcoefs] = n;

XSLPloadformulas(prob, nnlpcoefs, rowind, formulastart, 1, type, value);
```
 
_**Further information:**_
1. Formula `j` is made up of a list of tokens in `type` and `value` starting at `formulastart[j]`. The tokens follow the rules for parsed or unparsed formulae as indicated by the setting of `parsed`. The formula must be terminated with an `XSLP_EOF` token. If several formulas share the same nonlinear expressions, they can have the same value in `formulastart`. For possible token types and values see  _Xpress NonLinear Formulae_.
2. The `load` functions load items into the SLP problem. Any existing items of the same type are deleted first. The corresponding `add` functions add or replace items leaving other items of the same type unchanged.

_**Related topics:**_
`XPRSnlpgetformulastr`, `XSLPaddformulas`, `XPRSnlpchgformulastr`, `XSLPchgformula`, `XSLPloadformulas`, `XSLPgetformularows`, `XSLPgetformula`, `XSLPdelformulas`

#### XSLPloadtolsets

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Load sets of standard tolerance values into an SLP problem.

_**Topic areas:**_ 
SLP, SLP-convergence

_**Synopsis:**_

   `int XPRS_CC XSLPloadtolsets(XSLPprob prob, int ntolsets, double *tols);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ntolsets` | The number of tolerance sets to be loaded. 
`tols` | Double array of \( `ntolsets * 9`\) items containing the 9 tolerance values for each set in order. 

_**Example:**_
The following example creates two tolerance sets: the first has values of 0.005 for all tolerances; the second has values of 0.001 for relative tolerances \(numbers 2,4,6,8\), values of 0.01 for absolute tolerances \(numbers 1,3,5,7\) and zero for the closure tolerance \(number 0\).

```
double tols[18];
for (i=0;i<9;i++) tols[i] = 0.005;
tols[9] = 0;
for (i=10;i<18;i=i+2) tols[i] = 0.01;
for (i=11;i<18;i=i+2) tols[i] = 0.001;
XSLPloadtolsets(prob, 2, tols);
```
 
_**Further information:**_
1. A tolerance set is an array of 9 values containing the following tolerances:

__Entry / Bit__ | __Tolerance__ | __XSLP constant__ | __XSLP bit constant__ | 
---------- |  ---------- | ---------- | ---------- | 
__0__ | Closure tolerance \(TC\) | `XSLP_TOLSET_TC` | `XSLP_TOLSETBIT_TC` | 
__1__ | Absolute delta tolerance \(TA\) | `XSLP_TOLSET_TA` | `XSLP_TOLSETBIT_TA` | 
__2__ | Relative delta tolerance \(RA\) | `XSLP_TOLSET_RA` | `XSLP_TOLSETBIT_RA` | 
__3__ | Absolute coefficient tolerance \(TM\) | `XSLP_TOLSET_TM` | `XSLP_TOLSETBIT_TM` | 
__4__ | Relative coefficient tolerance \(RM\) | `XSLP_TOLSET_RM` | `XSLP_TOLSETBIT_RM` | 
__5__ | Absolute impact tolerance \(TI\) | `XSLP_TOLSET_TI` | `XSLP_TOLSETBIT_TI` | 
__6__ | Relative impact tolerance \(RI\) | `XSLP_TOLSET_RI` | `XSLP_TOLSETBIT_RI` | 
__7__ | Absolute slack tolerance \(TS\) | `XSLP_TOLSET_TS` | `XSLP_TOLSETBIT_TS` | 
__8__ | Relative slack tolerance \(RS\) | `XSLP_TOLSET_RS` | `XSLP_TOLSETBIT_RS` | 

2. The XSLP\_TOLSET constants can be used to access the corresponding entry in the value arrays, while the XSLP\_TOLSETBIT constants are used to set or retrieve which tolerance values are used for a given SLP variable.
3. Once created, a tolerance set can be used to set the tolerances for any SLP variable.
4. If a tolerance value is zero, then the default tolerance will be used instead. To force the use of a tolerance, use the `XSLPchgtolset` function and set the `Status` variable appropriately.
5. See the section "Convergence Criteria" for a fuller description of tolerances and their uses.
6. The `load` functions load items into the SLP problem. Any existing items of the same type are deleted first. The corresponding `add` functions add or replace items leaving other items of the same type unchanged.

_**Related topics:**_
`XSLPaddtolsets`, `XSLPdeltolsets`, `XSLPchgtolset`, `XSLPgettolset`

#### XSLPloadvars

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. _
   Load SLP variables defined as matrix columns into an SLP problem.

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPloadvars(XSLPprob prob, int nvars, int *colind, 
int *vartype, int *detrow, int *seqnum, int *tolind, 
double *initial, double *stepbound);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`nvars` | | The number of SLP variables to be loaded. 
`colind` | | Integer array holding the index of the matrix column corresponding to each SLP variable. 
`vartype` |  | Bitmap giving information about the SLP variable as follows:
&nbsp; | `Bit 1` | Variable has a delta vector;
&nbsp; | `Bit 2` | Variable has an initial value;
&nbsp; | `Bit 14` | Variable is the reserved "=" column;
&nbsp; |  | May be `NULL`if not required.
`detrow` | | Integer array holding the index of the determining row for each SLP variable \(a negative value means there is no determining row\)
&nbsp; | May be `NULL`if not required. 
`seqnum` | | Integer array holding the index sequence number for cascading for each SLP variable \(a zero value means there is no pre-defined order for this variable\)
&nbsp; | May be `NULL`if not required. 
`tolind` | | Integer array holding the index of the tolerance set for each SLP variable \(a zero value means the default tolerances are used\)
&nbsp; | May be `NULL`if not required. 
`initial` | | Double array holding the initial value for each SLP variable \(use the `vartype` bit map to indicate if a value is being provided\)
&nbsp; | May be `NULL`if not required. 
`stepbound` | | Double array holding the initial step bound size for each SLP variable \(a zero value means that no initial step bound size has been specified\). If a value of `XPRS_PLUSINFINITY` is used for a value in `stepbound`, the delta will never have step bounds applied, and will almost always be regarded as converged.
&nbsp; | May be `NULL`if not required. 

_**Example:**_
The following example loads two SLP variables into the problem. They correspond to columns 23 and 25 of the underlying LP problem. Column 25 has an initial value of 1.42; column 23 has no specific initial value

```

int colind[2], vartype[2];
double initial[2];

colind[0] = 23; vartype[0] = 0;
colind[1] = 25; vartype[1] = 4; initial[1] = 1.42;

XSLPloadvars(prob, 2, colind, vartype, NULL, NULL,
            NULL, initial, NULL);
```
 
`initial` is not set for the first variable, because it is not used \( `vartype` = 0\). Bit 1 of `vartype` is set for the second variable to indicate that the initial value has been set.

The arrays for determining rows, sequence numbers, tolerance sets and step bounds are not used at all, and so have been passed to the function as `NULL`.


_**Further information:**_
The `load`functions load items into the SLP problem. Any existing items of the same type are deleted first. The corresponding `add`functions add or replace items leaving other items of the same type unchanged.

_**Related topics:**_
`XSLPaddvars`, `XSLPchgvar`, `XSLPdelvars`, `XSLPgetvar`

#### XSLPmaxim

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Please call `XPRSchgobjsense`followed by `XSLPnlpoptimize`or `XPRSoptimize`\(noting that the latter will by default solve the MINLP if any integers are present unless providing the -l flag\) instead._
   Maximize an SLP problem

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPmaxim(XSLPprob prob, char *flags);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`flags` | These have the same meaning as for `XSLPnlpoptimize`. 

_**Related controls:**_

_Integer_
  
_Name_ | _Description_
---------- | ----------
`XSLP_ALGORITHM` | Bit map determining the SLP algorithm\(s\) used in the optimization.
`XSLP_AUGMENTATION` | Bit map determining the type of augmentation used to create the linearization.
`XSLP_CASCADE` | Bit map determining the type of cascading \(recalculation of SLP variable values\) used during the SLP optimization.
`XSLP_LOG` | Determines the amount of iteration logging information produced.
`XSLP_PRESOLVE` | Bit map determining the type of nonlinear presolve used before the SLP optimization starts.

_**Example:**_
The following example reads an SLP problem from file and then maximizes it using the primal simplex optimizer.

```
XSLPreadprob("Matrix","");
XSLPmaxim(prob,"p");
```
 
_**Further information:**_
If`XSLPconstruct`has not already been called, it will be called first, using the augmentation defined by the control variable`XSLP_AUGMENTATION`. If determining rows are provided, then cascading will be invoked in accordance with the setting of the control variable`XSLP_CASCADE`.

_**Related topics:**_
`XSLPconstruct`, `XSLPminim`, `XSLPnlpoptimize`, `XSLPpresolve`

#### XSLPminim

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Please call `XPRSchgobjsense`followed by `XSLPnlpoptimize`or `XPRSoptimize`\(noting that the latter will by default solve the MINLP if any integers are present unless providing the -l flag\) instead._
   Minimize an SLP problem

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPminim(XSLPprob prob, char *flags);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`flags` | These have the same meaning as for `XSLPnlpoptimize`. 

_**Related controls:**_

_Integer_
  
_Name_ | _Description_
---------- | ----------
`XSLP_ALGORITHM` | Bit map determining the SLP algorithm\(s\) used in the optimization.
`XSLP_AUGMENTATION` | Bit map determining the type of augmentation used to create the linearization.
`XSLP_CASCADE` | Bit map determining the type of cascading \(recalculation of SLP variable values\) used during the SLP optimization.
`XSLP_LOG` | Determines the amount of iteration logging information produced.
`XSLP_PRESOLVE` | Bit map determining the type of nonlinear presolve used before the SLP optimization starts.

_**Example:**_
The following example reads an SLP problem from file and then minimizes it using the Newton barrier optimizer.

```
XSLPreadprob("Matrix","");
XSLPminim(prob,"b");
```
 
_**Further information:**_
If`XSLPconstruct`has not already been called, it will be called first, using the augmentation defined by the control variable`XSLP_AUGMENTATION`. If determining rows are provided, then cascading will be invoked in accordance with the setting of the control variable`XSLP_CASCADE`.

_**Related topics:**_
`XSLPconstruct`, `XSLPmaxim`, `XSLPnlpoptimize`, `XSLPpresolve`

#### XSLPmsaddcustompreset, XPRSmsaddcustompreset

_**Purpose:**_

   A combined version of XSLPmsaddjob and XSLPmsaddpreset. The preset described is loaded, topped up with the specific settings supplied

_**Topic areas:**_ 
Multistart, Data Input

_**Synopsis:**_

   `
int XSLP_CC XSLPmsaddcustompreset( XSLPprob prob, const char *description, const int preset, const int maxjobs, const int ninitial, 
const int *colind, const double *initial, const int nintcontrols, 
const int *intcontrolid, const int *intcontrolval, const int ndblcontrols, 
const int *dblcontrolid, const double *dblcontrolval, void *data); 
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`description` | Text description of the job. Used for messaging, may be NULL if not required. 
`preset` | Which preset to load. 
`maxjobs` | Maximum number of jobs to be added to the multistart pool. 
`ninitial` | Number of initial values to set. 
`colind` | Indices of the variables for which to set an initial value. May be NULL if no initial values are provided. 
`initial` | Initial values for the variables for which to set an initial value. May be NULL if no initial values are provided. 
`nintcontrols` | Number of integer controls to set. 
`intcontrolid` | The indices of the integer controls to be set. May be NULL if nintcontrols is zero. 
`intcontrolval` | The values of the integer controls to be set. May be NULL if nintcontrols is zero. 
`ndblcontrols` | Number of double controls to set. 
`dblcontrolid` | The indices of the double controls to be set. May be NULL if ndblcontrols is zero. 
`dblcontrolval` | The values of the double controls to be set. May be NULL if ndblcontrols is zero. 
`data` | Job-specific user context object to be passed to the multistart callbacks. 

_**Further information:**_
1. This function allows for repeatedly calling the same multistart preset \(e.g. initial values\) using different basic controls.
2. The following presets are defined:
 * `XSLP_MSSET_INITIALVALUES`: generate maxjobs number of random base points.
 * `XSLP_MSSET_SOLVERS`: load all solvers.
 * `XSLP_MSSET_SLP_BASIC`: load the most typical SLP tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_SLP_EXTENDED`: load a comprehensive set of SLP tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_KNITRO_BASIC`: load the most typical Knitro tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_KNITRO_EXTENDED`: load a comprehensive set of Knitro tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_INITIALFILTERED`: generate maxjobs number of random base points, filtered by a merit function centred on initial feasibility.
3. See `XSLP_MSMAXBOUNDRANGE` for controlling the range in which initial values are generated.

_**Related topics:**_
`XSLPmsaddpreset`, `XSLPmsaddjob`, `XSLPmsclear`

#### XSLPmsaddjob, XPRSmsaddjob

_**Purpose:**_

   Adds a multistart job to the multistart pool

_**Topic areas:**_ 
Multistart, Data Input

_**Synopsis:**_

   `
int XSLP_CC XSLPmsaddjob( XSLPprob prob, const char *description, const int ninitial, 
const int *colind, const double *initial, const int nintcontrols, 
const int *intcontrolid, const int *intcontrolval, const int ndblcontrols, 
const int *dblcontrolid, const double *dblcontrolval, void *data); 
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`description` | Text description of the job. Used for messaging, may be NULL if not required. 
`ninitial` | Number of initial values to set. 
`colind` | Indices of the variables for which to set an initial value. May be NULL if no initial values are provided. 
`initial` | Initial values for the variables for which to set an initial value. May be NULL if no initial values are provided. 
`nintcontrols` | Number of integer controls to set. 
`intcontrolid` | The indices of the integer controls to be set. May be NULL if nintcontrols is zero. 
`intcontrolval` | The values of the integer controls to be set. May be NULL if nintcontrols is zero. 
`ndblcontrols` | Number of double controls to set. 
`dblcontrolid` | The indices of the double controls to be set. May be NULL if ndblcontrols is zero. 
`dblcontrolval` | The values of the double controls to be set. May be NULL if ndblcontrols is zero. 
`data` | Job-specific user context object to be passed to the multistart callbacks. 

_**Further information:**_
1. Adds a mutistart job, applying the specified initial point and option combinations on top of the base problem, i.e. the options and initial values specified to the function is applied on top of the existing settings.
2. See `XSLP_MSMAXBOUNDRANGE` for controlling the range in which initial values are generated.
3. This function allows for loading empty template jobs, that can then be identified using the data variable.

_**Related topics:**_
`XSLPmsaddpreset`, `XSLPmsaddcustompreset`, `XSLPmsclear`

#### XSLPmsaddpreset, XPRSmsaddpreset

_**Purpose:**_

   Loads a preset of jobs into the multistart job pool.

_**Topic areas:**_ 
Multistart, Data Input

_**Synopsis:**_

   `
int XSLP_CC XSLPmsaddpreset( XSLPprob prob, const char *description, const int preset, const int maxjobs, void *data); 
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`description` | Text description of the preset. Used for messaging, may be NULL if not required. 
`preset` | Which preset to load. 
`maxjobs` | Maximum number of jobs to be added to the multistart pool. 
`data` | Job-specific user context object to be passed to the multistart callbacks. 

_**Further information:**_
1. The following presets are defined:
 * `XSLP_MSSET_INITIALVALUES`: generate maxjobs number of random base points.
 * `XSLP_MSSET_SOLVERS`: load all solvers.
 * `XSLP_MSSET_SLP_BASIC`: load the most typical SLP tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_SLP_EXTENDED`: load a comprehensive set of SLP tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_KNITRO_BASIC`: load the most typical Knitro tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_KNITRO_EXTENDED`: load a comprehensive set of Knitro tuning settings. A maximum of maxjobs jobs are loaded.
 * `XSLP_MSSET_INITIALFILTERED`: generate maxjobs number of random base points, filtered by a merit function centred on initial feasibility.
2. See `XSLP_MSMAXBOUNDRANGE` for controlling the range in which initial values are generated.

_**Related topics:**_
`XSLPmsaddjob`, `XSLPmsaddcustompreset`, `XSLPmsclear`

#### XSLPmsclear, XPRSmsclear

_**Purpose:**_

   Removes all scheduled jobs from the multistart job pool

_**Topic area:**_ 
Multistart

_**Synopsis:**_

   `
int XSLP_CC XSLPmsclear( XSLPprob prob); 
`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Related topics:**_
`XSLPmsaddjob`, `XSLPmsaddpreset`, `XSLPmsaddcustompreset`

#### XSLPnlpoptimize, XPRSnlpoptimize

_**Purpose:**_

   Maximize or minimize an SLP problem

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPnlpoptimize(XSLPprob prob, const char *flags);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`flags` |  | Flags to pass to `XSLPnlpoptimize`. The default is `""`or `NULL`, in which case the solve stops after solving the root relaxation \(or a continuous problem to completion\) and it restarts the solve without continuing.
&nbsp; | `g` | Perform a branch and bound search if necessary to solve the problem;
&nbsp; | `c` | continue a previously interrupted solve.
&nbsp; |  | All other flags are passed to the Optimizer: see[`XPRSlpoptimize`](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSlpoptimize.html).

_**Related controls:**_

_Integer_
  
_Name_ | _Description_
---------- | ----------
`XSLP_ALGORITHM` | Bit map determining the SLP algorithm\(s\) used in the optimization.
`XSLP_AUGMENTATION` | Bit map determining the type of augmentation used to create the linearization.
`XSLP_CASCADE` | Bit map determining the type of cascading \(recalculation of SLP variable values\) used during the SLP optimization.
`XSLP_LOG` | Determines the amount of iteration logging information produced.
`XSLP_PRESOLVE` | Bit map determining the type of nonlinear presolve used before the SLP optimization starts.

_**Further information:**_
1. If `XSLPconstruct` has not already been called, it will be called first, using the augmentation defined by the control variable `XSLP_AUGMENTATION`.
2. If determining rows are provided, then cascading will be invoked in accordance with the setting of the control variable `XSLP_CASCADE`.

_**Related topics:**_
`XSLPconstruct`.

#### XSLPpostsolve, XPRSnlppostsolve

_**Purpose:**_

   Restores the problem to its pre-solve state

_**Topic area:**_ 
Presolve

_**Synopsis:**_

   `int XPRS_CC XSLPpostsolve(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Related controls:**_

_Integer_
  
_Name_ | _Description_
---------- | ----------
`XSLP_POSTSOLVE` | Determines if postsolve is applied automatically.

_**Further information:**_
If Xpress-SLP was used to solve the problem, postsolve will unconstruct the problem before postsolving \(including any reformulation that might have been applied\).

_**Related topics:**_
`XSLP_POSTSOLVE`

#### XSLPpresolve

_**Purpose:**_

   Perform a nonlinear presolve on the problem

_**Topic area:**_ 
Presolve

_**Synopsis:**_

   `int XPRS_CC XSLPpresolve(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Related controls:**_

_Integer_
  
_Name_ | _Description_
---------- | ----------
`XSLP_PRESOLVE` | Bitmap containing nonlinear presolve options.

_**Example:**_
The following example reads a problem from file, sets the presolve control, presolves the problem and then solves it \(using the "s" flag to enforce a local solve\).

```
XSLPreadprob(prob, "Matrix", "");
XSLPsetintcontrol(prob, XSLP_PRESOLVE, 1);
XSLPpresolve(prob);
XSLPnlpoptimize(prob, "s")
```
 
_**Further information:**_
If bit 1 of`XSLP_PRESOLVE`is not set, no nonlinear presolve will be performed. Otherwise, the presolve will be performed in accordance with the bit settings.. `XSLPpresolve`is called automatically by`XSLPconstruct`, so there is no need to call it explicitly unless there is a requirement to interrupt the process between presolve and optimization. `XSLPpresolve`must be called before`XSLPconstruct`or any of the SLP optimization procedures..

_**Related topics:**_
`XSLP_PRESOLVE`

#### XSLPprintmemory

_**Purpose:**_

   Print the dimensions and memory allocations for a problem

_**Topic area:**_ 
Logging

_**Synopsis:**_

   `int XPRS_CC XSLPprintmemory(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_
The following example loads a problem from file and then prints the dimensions of the arrays.

```
XSLPreadprob(prob, "Matrix1", "");
XSLPprintmemory(prob);
```
 The output is similar to the following:

```
Arrays and dimensions:
Array    Item  Used  Max  Allocated   Memory
         Size Items Items    Memory   Control
MemList    28   103   129        4K
String      1  8779 13107       13K   XSLP_MEM_STRING
Xv         16     2  1000       16K   XSLP_MEM_XV
Xvitem     48    11  1000       47K   XSLP_MEM_XVITEM
....
```




_**Further information:**_
`XSLPprintmemory`lists the current sizes and amounts used of the variable arrays in the current problem. For each array, the size of each item, the number used and the number allocated are shown, together with the size of memory allocated and, where appropriate, the name of the memory control variable to set the array size. Loading and execution of some problems can be speeded up by setting the memory controls immediately after the problem is created. If an array has to be moved to re-allocate it with a larger size, there may be insufficient memory to hold both the old and new versions; pre-setting the memory controls reduces the number of such re-allocations which take place and may allow larger problems to be solved.

#### XSLPprintevalinfo, XPRSnlpprintevalinfo

_**Purpose:**_

   Print a summary of any evaluation errors that may have occurred during solving a problem

_**Topic area:**_ 
Logging

_**Synopsis:**_

   `int XPRS_CC XSLPprintevalinfo(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Related topics:**_
`XSLPsetcbcoefevalerror`

#### XSLPreadprob

_**Purpose:**_

   Read an Xpress NonLinear extended MPS format matrix from a file into an SLP problem

_**Topic areas:**_ 
File IO, Problem Creation

_**Synopsis:**_

   `int XPRS_CC XSLPreadprob(XSLPprob prob, char *filename, char *flags);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`filename` | | Character string containing the name of the file from which the matrix is to be read. 
`flags` |  | Character string containing any flags needed for the input routine:
&nbsp; | `l` | only `filename.lp` is searched for;
&nbsp; | `v` | use the provided filename verbatim, without appending the `.mps`, `.mat` or `.lp` extension;
&nbsp; | `z` | read a compressed input file.

_**Example:**_
The following example reads the problem from file "Matrix.mat".

```
XSLPreadprob(prob, "Matrix", "");

```
 
_**Further information:**_
1. `XSLPreadprob` tries to open the file with an extension of "mat" or, failing that, an extension of "mps". If both fail, the file name will be tried with no extension.
2. `XSLPreadprob` is capable to read most Ampl .nl files. To specify that a .nl file is to be read, provide the full filename including the .nl extension.
3. For details of the format of the file, see the section on [Extended MPS file format](#chapExtMPSformat).

_**Related topics:**_
[Extended MPS file format](#chapExtMPSformat), `XSLPwriteprob`

#### XSLPremaxim

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Please use XSLPmaxim with the 'c' flag instead._
   Continue the maximization of an SLP problem.

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPremaxim(XSLPprob prob, char *flags);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`flags` | These have the same meaning as for `XSLPmaxim`. 

_**Example:**_
The following example optimizes the SLP problem for up to 10 SLP iterations. If it has not converged, it saves the file and continues for another 10.

```
int Status;

XSLPsetintcontrol(prob, XSLP_ITERLIMIT, 10);
XSLPmaxim(prob,"");
XSLPgetintattrib(prob, XSLP_STATUS, &Status);
if (Status & XSLP_MAXSLPITERATIONS) {
  XSLPsave(prob);
  XSLPsetintcontrol(prob, XSLP_ITERLIMIT, 20);
  XSLPremaxim(prob,"");
}
```
 
_**Further information:**_
This allows Xpress NonLinear to continue the maximization of a problem after it has been terminated, without re-initializing any of the parameters. In particular, the iteration count will resume at the point where it previously stopped, and not at 1.

_**Related topics:**_
`XSLPmaxim`, `XSLPreminim`

#### XSLPreminim

_**Purpose:**_

   _This subroutine is deprecated and will be removed in a future release. Please use XSLPminim with the 'c' flag instead._
   Continue the minimization of an SLP problem.

_**Topic area:**_ 
Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPreminim(XSLPprob prob, char *flags);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`flags` | These have the same meaning as for `XSLPminim`. 

_**Example:**_
The following example optimizes the SLP problem for up to 10 SLP iterations \(using the "s" flag to enforce a local solve\). If it has not converged, it saves the file and continues for another 10.

```
int Status;

XSLPsetintcontrol(prob, XSLP_ITERLIMIT, 10);
XSLPminim(prob,"s");
XSLPgetintattrib(prob, XSLP_STATUS, &Status);
if (Status & XSLP_MAXSLPITERATIONS) {
  XSLPsave(prob);
  XSLPsetintcontrol(prob, XSLP_ITERLIMIT, 20);
  XSLPreminim(prob,"s");
}
```
 
_**Further information:**_
This allows Xpress NonLinear to continue the minimization of a problem after it has been terminated, without re-initializing any of the parameters. In particular, the iteration count will resume at the point where it previously stopped, and not at 1.

_**Related topics:**_
`XSLPminim`, `XSLPremaxim`

#### XPRSremovecbmsjobend

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbmsjobend`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbmsjobend(XPRSprob prob, int (XPRS_CC *msjobend)(XPRSprob cbprob, void *cbdata, void  *jobdata, const char *jobdesc, int *p_status), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`msjobend` | The callback function to remove. If `NULL` then all msjobend callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all msjobend callbacks with the function `msjobend` will be removed. 

_**Related topics:**_
`XPRSaddcbmsjobend`

#### XPRSremovecbmsjobstart

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbmsjobstart`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbmsjobstart(XPRSprob prob,
int (XPRS_CC *msjobstart)(XPRSprob cbprob, void *cbdata, void *jobdata, const char *jobdesc, int *p_status),
void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`msjobstart` | The callback function to remove. If `NULL` then all msjobstart callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all msjobstart callbacks with the function `msjobstart` will be removed. 

_**Related topics:**_
`XPRSaddcbmsjobstart`

#### XPRSremovecbmswinner

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbmswinner`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbmswinner(XPRSprob prob,
int (XPRS_CC *mswinner)(XPRSprob cbprob, void *cbdata, void *jobdata, const char *jobdesc),
void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`mswinner` | The callback function to remove. If `NULL` then all mswinner callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all mswinner callbacks with the function `mswinner` will be removed. 

_**Related topics:**_
`XPRSaddcbmswinner`

#### XPRSremovecbnlpcoefevalerror

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbnlpcoefevalerror`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, Numerics

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbnlpcoefevalerror(XPRSprob prob, int (XPRS_CC *nlpcoefevalerror) (XPRSprob cbprob, void *cbdata, int row, int col), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`nlpcoefevalerror` | The callback function to remove. If `NULL` then all nlpcoefevalerror callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all nlpcoefevalerror callbacks with the function `nlpcoefevalerror` will be removed. 

_**Related topics:**_
`XPRSaddcbnlpcoefevalerror`

#### XPRSremovecbslpcascadeend

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpcascadeend`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpcascadeend(XPRSprob prob, int (XPRS_CC *slpcascadeend) (XPRSprob cbprob, void *cbdata), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadeend` | The callback function to remove. If `NULL` then all slpcascadeend callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpcascadeend callbacks with the function `slpcascadeend` will be removed. 

_**Related topics:**_
`XPRSaddcbslpcascadeend`

#### XPRSremovecbslpcascadestart

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpcascadestart`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpcascadestart(XPRSprob prob, int (XPRS_CC *slpcascadestart) (XPRSprob cbprob, void *cbdata), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadestart` | The callback function to remove. If `NULL` then all slpcascadestart callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpcascadestart callbacks with the function `slpcascadestart` will be removed. 

_**Related topics:**_
`XPRSaddcbslpcascadestart`

#### XPRSremovecbslpcascadevar

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpcascadevar`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpcascadevar(XPRSprob prob, int (XPRS_CC *slpcascadevar) (XPRSprob cbprob, void *cbdata, int col), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadevar` | The callback function to remove. If `NULL` then all slpcascadevar callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpcascadevar callbacks with the function `slpcascadevar` will be removed. 

_**Related topics:**_
`XPRSaddcbslpcascadevar`

#### XPRSremovecbslpcascadevarfail

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpcascadevarfail`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpcascadevarfail(XPRSprob prob, int (XPRS_CC *slpcascadevarfail) (XPRSprob cbprob, void *cbdata, int col), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpcascadevarfail` | The callback function to remove. If `NULL` then all slpcascadevarfail callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpcascadevarfail callbacks with the function `slpcascadevarfail` will be removed. 

_**Related topics:**_
`XPRSaddcbslpcascadevarfail`

#### XPRSremovecbslpconstruct

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpconstruct`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpconstruct(XPRSprob prob, int (XPRS_CC *slpconstruct) (XPRSprob cbprob, void *cbdata), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpconstruct` | The callback function to remove. If `NULL` then all slpconstruct callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpconstruct callbacks with the function `slpconstruct` will be removed. 

_**Related topics:**_
`XPRSaddcbslpconstruct`

#### XPRSremovecbslpdrcol

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpdrcol`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpdrcol(XPRSprob prob, int (XPRS_CC *slpdrcol) (XPRSprob prob, void *data, int col, int detcol, double detval, double * p_value, double lb, double ub), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpdrcol` | The callback function to remove. If `NULL` then all slpdrcol callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpdrcol callbacks with the function `slpdrcol` will be removed. 

_**Related topics:**_
`XPRSaddcbslpdrcol`

#### XPRSremovecbslpintsol

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpintsol`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, MISLP

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpintsol(XPRSprob prob, int (XPRS_CC *slpintsol) (XPRSprob cbprob, void *cbdata), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpintsol` | The callback function to remove. If `NULL` then all slpintsol callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpintsol callbacks with the function `slpintsol` will be removed. 

_**Related topics:**_
`XPRSaddcbslpintsol`

#### XPRSremovecbslpiterend

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpiterend`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpiterend(XPRSprob prob, int (XPRS_CC *slpiterend) (XPRSprob cbprob, void *cbdata), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpiterend` | The callback function to remove. If `NULL` then all slpiterend callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpiterend callbacks with the function `slpiterend` will be removed. 

_**Related topics:**_
`XPRSaddcbslpiterend`

#### XPRSremovecbslpiterstart

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpiterstart`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpiterstart(XPRSprob prob, int (XPRS_CC *slpiterstart) (XPRSprob cbprob, void *cbdata), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpiterstart` | The callback function to remove. If `NULL` then all slpiterstart callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpiterstart callbacks with the function `slpiterstart` will be removed. 

_**Related topics:**_
`XPRSaddcbslpiterstart`

#### XPRSremovecbslpitervar

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslpitervar`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP, SLP-convergence

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslpitervar(XPRSprob prob, int (XPRS_CC *slpitervar) (XPRSprob cbprob, void *cbdata, int col), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slpitervar` | The callback function to remove. If `NULL` then all slpitervar callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slpitervar callbacks with the function `slpitervar` will be removed. 

_**Related topics:**_
`XPRSaddcbslpitervar`

#### XPRSremovecbslppreupdatelinearization

_**Purpose:**_

   Removes a callback function previously added by`XPRSaddcbslppreupdatelinearization`. The specified callback function will no longer be called after it has been removed.

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `
int XPRS_CC XPRSremovecbslppreupdatelinearization(XPRSprob prob, int (XPRS_CC *slppreupdatelinearization) (XPRSprob cbprob, void *cbdata, int *ifrepeat), void* data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`slppreupdatelinearization` | The callback function to remove. If `NULL` then all slppreupdatelinearization callback functions added with the given user-defined data value will be removed. 
`data` | The data value that the callback was added with. If `NULL`, then the data value will not be checked and all slppreupdatelinearization callbacks with the function `slppreupdatelinearization` will be removed. 

_**Related topics:**_
`XPRSaddcbslppreupdatelinearization`

#### XSLPrestore

_**Purpose:**_

   Restore the Xpress NonLinear problem from a file created by`XSLPsave`

_**Topic areas:**_ 
File IO, Save Restore

_**Synopsis:**_

   `int XPRS_CC XSLPrestore(XSLPprob prob, char *filename);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`filename` | Character string containing the name of the problem which is to be restored. 

_**Example:**_
The following example restores a problem originally saved on file "MySave"

```
XSLPrestore(prob, "MySave");
```
 
_**Further information:**_
Normally `XSLPrestore`restores both the Xpress NonLinear problem and the underlying optimizer problem. If only the Xpress NonLinear problem is required, set the integer control variable`XSLP_CONTROL`appropriately.

_**Related topics:**_
`XSLP_CONTROL`, `XSLPsave`

#### XSLPreinitialize, XPRSslpreinitialize

_**Purpose:**_

   Reset the SLP problem to match a just augmented system

_**Topic areas:**_ 
SLP, Solution Process

_**Synopsis:**_

   `
      int XPRS_CC XSLPreinitialize(XSLPprob prob);
  `

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Further information:**_
Can be used to rerun the SLP optimization process with updated parameters, penalties or initial values, but unchanged augmentation.

_**Related topics:**_
`XSLPcreateprob`, `XSLPdestroyprob`, `XSLPunconstruct`, `XSLPsetcurrentiv`,

#### XSLPsave

_**Purpose:**_

   Save the Xpress NonLinear problem to file

_**Topic areas:**_ 
File IO, Save Restore

_**Synopsis:**_

   `int XPRS_CC XSLPsave(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Further information:**_
Normally `XSLPsave`saves both the Xpress NonLinear problem and the underlying optimizer problem. If only the Xpress NonLinear problem is required, set the integer control variable`XSLP_CONTROL`appropriately.

_**Related topics:**_
`XSLP_CONTROL`, `XSLPrestore` `XSLPsaveas`

#### XSLPsaveas

_**Purpose:**_

   Save the Xpress NonLinear problem to a named file

_**Topic areas:**_ 
File IO, Save Restore

_**Synopsis:**_

   `int XPRS_CC XSLPsaveas(XSLPprob prob, const char *filename);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`filename` | The name of the file \(without extension\) in which the problem is to be saved. 

_**Further information:**_
Normally `XSLPsaveas`saves both the Xpress NonLinear problem and the underlying optimizer problem. If only the Xpress NonLinear problem is required, set the integer control variable`XSLP_CONTROL`appropriately.

_**Related topics:**_
`XSLP_CONTROL`, `XSLPrestore` `XSLPsave`

#### XSLPscaling

_**Purpose:**_

   Analyze the current matrix for largest/smallest coefficients and ratios

_**Topic area:**_ 
Numerics

_**Synopsis:**_

   `int XPRS_CC XSLPscaling(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_
The following example analyzes the matrix

```
XSLPscaling(prob);
```
 
_**Further information:**_
1. The current matrix \(including augmentation if it has been carried out\) is scanned for the absolute and relative sizes of elements. The following information is reported:
 * Largest and smallest elements in the matrix;
 * Counts of the ranges of row ratios in powers of 10 \(e.g. number of rows with ratio between 1.0E+01 and 1.0E+02\);
 * List of the rows \(with largest and smallest elements\) which appear in the highest range;
 * Counts of the ranges of column ratios in powers of 10 \(e.g. number of columns with ratio between 1.0E+01 and 1.0E+02\);
 * List of the columns \(with largest and smallest elements\) which appear in the highest range;
 * Element ranges in powers of 10 \(e.g. number of elements between 1.0E+01 and 1.0E+02\).
2. Where any of the reported items \(largest or smallest element in the matrix or any reported row or column element\) is in a penalty error vector, the results are repeated, excluding all penalty error vectors.

#### XSLPsetcbcascadeend, XPRSsetcbslpcascadeend

_**Purpose:**_

   Set a user callback to be called at the end of the cascading process, after the last variable has been cascaded

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbcascadeend(XSLPprob prob,
int (XPRS_CC *cascadeend) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`cascadeend` | The function to be called at the end of the cascading process. `cascadeend` returns an integer value. If the return value is nonzero, the SLP iterations will stop. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb cascade end`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `cascadeend` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed at the end of the cascading process which checks if any of the values have been changed significantly:

```
double *cSol;
XSLPsetcbcascadeend(prob, CBCascEnd, &cSol);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBCascEnd(XSLPprob MyProb, void *Obj) {
  int iCol, nCol;
  double *cSol, Value;
  cSol = * (double **) Obj;
  XSLPgetintcontrol(MyProb, XPRS_COLS, &nCol);
  for (iCol=0;iCol<nCol;iCol++) {
    XSLPalltype alltype;
    XSLPgetcolinfo(prob, XSLP_COLINFO_VALUE, iCol, &alltype);
    Value = alltype.value.real;
    if (fabs(Value-cSol[iCol]) > .01)
      printf("\nCol %d changed from %lg to %lg",
             iCol, cSol[iCol], Value);
  }
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we assume has been populated with the original solution values.

_**Further information:**_
This callback can be used at the end of the cascading, when all the solution values have been recalculated.

_**Related topics:**_
`XSLPcascade`, `XSLPsetcbcascadestart`, `XSLPsetcbcascadevar`, `XSLPsetcbcascadevarfail`

#### XSLPsetcbcascadestart, XPRSsetcbslpcascadestart

_**Purpose:**_

   Set a user callback to be called at the start of the cascading process, before any variables have been cascaded

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbcascadestart(XSLPprob prob,
int (XPRS_CC *cascadestart) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`cascadestart` | The function to be called at the start of the cascading process. `cascadestart` returns an integer value. If the return value is nonzero, the cascading process will be omitted for the current SLP iteration, but the optimization will continue. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb cascade start`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `cascadestart` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed at the start of the cascading process to save the current values of the variables:

```
double *cSol;
XSLPsetcbcascadestart(prob, CBCascStart, &cSol);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBCascStart(XSLPprob MyProb, void *Obj) {
  int iCol, nCol;
  double *cSol;
  cSol = * (double **) Obj;
  XSLPgetintcontrol(MyProb, XPRS_COLS, &nCol);
  for (iCol=0;iCol<nCol;iCol++) {
    XSLPalltype alltype;
    XSLPgetcolinfo(prob, XSLP_COLINFO_VALUE, iCol, &alltype);
    cSol[iCol] = alltype.value.real;
  }
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we populate with the solution values.

_**Further information:**_
This callback can be used at the start of the cascading, before any of the solution values have been recalculated.

_**Related topics:**_
`XSLPcascade`, `XSLPsetcbcascadeend`, `XSLPsetcbcascadevar`, `XSLPsetcbcascadevarfail`

#### XSLPsetcbcascadevar, XPRSsetcbslpcascadevar

_**Purpose:**_

   Set a user callback to be called after each column has been cascaded

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbcascadevar(XSLPprob prob,
int (XPRS_CC *cascadevar) (XSLPprob cbprob, void *cbdata, int col),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`cascadevar` | The function to be called after each column has been cascaded. `cascadevar` returns an integer value. If the return value is nonzero, the cascading process will be omitted for the remaining variables during the current SLP iteration, but the optimization will continue. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb cascade var`. 
`col` | The number of the column which has been cascaded. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `cascadevar` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed after each variable has been cascaded:

```
double *cSol;
XSLPsetcbcascadevar(prob, CBCascVar, &cSol);
```
 The following sample callback function resets the value of the variable if the cascaded value is of the opposite sign to the original value:

```
int XPRS_CC CBCascVar(XSLPprob MyProb, void *Obj, int iCol) {
  double *cSol, Value;
  cSol = * (double **) Obj;
  XSLPgetvar(MyProb, iCol, NULL, NULL, NULL,
             NULL, NULL, NULL, &Value,
             NULL, NULL, NULL, NULL,
             NULL, NULL, NULL, NULL);
  if (Value * cSol[iCol] < 0) {
    Value = cSol[iCol];
    XSLPchgvar(MyProb, ColNum, NULL, NULL, NULL, NULL,
               NULL, NULL, &Value, NULL, NULL, NULL,
               NULL);
  }
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we assume has been populated with the original solution values.

_**Further information:**_
This callback can be used after each variable has been cascaded and its new value has been calculated.

_**Related topics:**_
`XSLPcascade`, `XSLPsetcbcascadeend`, `XSLPsetcbcascadestart`, `XSLPsetcbcascadevarfail`

#### XSLPsetcbcascadevarfail, XPRSsetcbslpcascadevarfail

_**Purpose:**_

   Set a user callback to be called after cascading a column was not successful

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbcascadevarfail(XSLPprob prob,
int (XPRS_CC *cascadevarfail) (XSLPprob cbprob, void *cbdata, int col),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`cascadevarfail` | The function to be called after cascading a column was not successful. `cascadevarfail` returns an integer value. If the return value is nonzero, the cascading process will be omitted for the remaining variables during the current SLP iteration, but the optimization will continue. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb cascade var fail`. 
`col` | The number of the column which has been cascaded. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `cascadevarfail` as `cbdata`. 

_**Further information:**_
This callback can be used to provide user defined updates for SLP variables having a determining row that were not successfully cascaded due to the determining row being close to singular around the current values. This callback will always be called in place of the cascadevar callback in such cases, and in no situation will both the cascadevar and the cascadevarfail callback be called in the same iteration for the same variable.

_**Related topics:**_
`XSLPcascade`, `XSLPsetcbcascadeend`, `XSLPsetcbcascadestart`, `XSLPsetcbcascadevar`

#### XSLPsetcbcoefevalerror, XPRSsetcbnlpcoefevalerror

_**Purpose:**_

   Set a user callback to be called when an evaluation of a coefficient fails during the solve

_**Topic areas:**_ 
Callback, Numerics

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbcoefevalerror(XSLPprob prob,
int (XPRS_CC *coefevalerror) (XSLPprob cbprob, void *cbdata, int row, int col),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`coefevalerror` | The function to be called when an evaluation fails. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb coef eval error`. 
`row` | The row position of the coefficient. 
`col` | The column position of the coefficient. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `coefevalerror` as `cbdata`. 

_**Further information:**_
This callback can be used to capture when an evaluation of a coefficient fails. The callback is called only once for each coefficient.

_**Related topics:**_
`XSLPprintevalinfo`

#### XSLPsetcbconstruct, XPRSsetcbslpconstruct

_**Purpose:**_

   Set a user callback to be called during the Xpress-SLP augmentation process

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbconstruct(XSLPprob prob,
int (XPRS_CC *construct) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`construct` | The function to be called during problem augmentation. `construct` returns an integer value. See below for an explanation of the values. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb construct`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `construct` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed during the Xpress-SLP problem augmentation:

```
double *cValue;
cValue = NULL;
XSLPsetcbconstruct(prob, CBConstruct, &cValue);
```
 The following sample callback function sets values for the variables the first time the function is called and returns to`XSLPconstruct`to recalculate the initial matrix. The second time it is called it frees the allocated memory and returns to`XSLPconstruct`to proceed with the rest of the augmentation.

```
int XPRS_CC CBConstruct(XSLPprob MyProb, void *Obj) {
  double *cValue;
  int i, n;
/* if data is NULL, this is first-time entry */
  if (*(void**)Obj == NULL) {
    XSLPgetintattrib(MyProb,XPRS_COLS,&n);
    cValue = malloc(n*sizeof(double));
/* ... initialize with values (not shown here) and then ... */
    for (i=0;i<n;i++)
/* store into SLP structures */
      XSLPchgvar(MyProb, i, NULL, NULL, NULL, NULL,
                 NULL, NULL, &cValue[i], NULL, NULL, NULL,
                 NULL);
/* set data non-null to indicate we have processed data */
    *(void**)Obj = cValue;
    return -1;
  }
  else {
/* free memory, clear marker and continue */
    free(*(void**)Obj);
    *(void**)Obj = NULL;
  }
  return 0;
}
```
 
_**Further information:**_
1. This callback can be used during the problem augmentation, generally \(although not exclusively\) to change the initial values for the variables.
2. The following return codes are accepted:
 * `0`: Normal return: augmentation continues
 * `-1`: Return to recalculate matrix values
 * `-2`: Return to recalculate row weights and matrix entries
 * `other`: Error return: augmentation terminates, `XSLPconstruct` terminates with a nonzero error code.
3. The return values -1 and -2 will cause the callback to be called a second time after the matrix has been recalculated. It is the responsibility of the callback to ensure that it does ultimately exit with a return value of zero.

_**Related topics:**_
`XSLPconstruct`

#### XSLPsetcbdestroy

_**Purpose:**_

   Set a user callback to be called when an SLP problem is about to be destroyed

_**Topic area:**_ 
Callback

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbdestroy(XSLPprob prob,
int (XPRS_CC *destroy) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`destroy` | The function to be called when the SLP problem is about to be destroyed. `destroy` returns an integer value. At present the return value is ignored. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb destroy`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `destroy` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed before the SLP problem is destroyed:

```
double *cSol;
XSLPsetcbdestroy(prob, CBDestroy, &cSol);
```
 The following sample callback function frees the memory associated with the user-defined object:

```
int XPRS_CC CBDestroy(XSLPprob MyProb, void *Obj) {
  if (*(void**)Obj) free(*(void**)Obj);
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we assume was assigned using one of the `malloc`functions.

_**Further information:**_
This callback can be used when the problem is about to be destroyed to free any user-defined resources which were allocated during the life of the problem.

_**Related topics:**_
`XSLPdestroyprob`

#### XSLPsetcbdrcol, XPRSsetcbslpdrcol

_**Purpose:**_

   Set a user callback used to override the update of variables with small determining column

_**Topic areas:**_ 
Callback, SLP, Cascading

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbdrcol(XSLPprob prob,
int (XPRS_CC *drcol) (XSLPprob prob, void *data, int col, int detcol, double detval, double * p_value, double lb, double ub),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`drcol` | The function to be called after each column has been cascaded. `drcol` returns an integer value. If the return value is positive, it will indicate that the value has been fixed, and cascading should be omitted for the variable. A negative value indicates that a previously fixed value has been relaxed. If no action is taken, a 0 return value should be used. 
`prob` | The problem passed to the callback function. 
`data` | The user-defined object passed as `data` to `XSLP set cb cascade var`. 
`col` | The index of the column for which the determining columns is checked. 
`detcol` | The index of the determining column for the column that is being updated. 
`detval` | The value of the determining column in the current SLP iteration. 
`p_value` | Used to return the new value for column `col`, should it need to be updated, in which case the callback must return a positive result to indicate that this value should be used. 
`lb` | The original lower bound of column `col`. The callback provides this value as a reference, should the bound be updated or changed during the solution process. 
`ub` | The original upper bound of column `col`. The callback provides this value as a reference, should the bound be updated or changed during the solution process. 
`data` | A user-defined object, which can be used for any purpose. by the function. `data` is passed to `drcol` as `data`. 

_**Further information:**_
If set, this callback is called as part of the cascading procedure. Please see Chapter _Cascading_for more information.

_**Related topics:**_
`XSLP_DRCOLTOL`, `XSLPcascade`, `XSLPsetcbcascadeend`, `XSLPsetcbcascadestart`

#### XSLPsetcbintsol, XPRSsetcbslpintsol

_**Purpose:**_

   Set a user callback to be called during MISLP when an integer solution is obtained

_**Topic areas:**_ 
Callback, MISLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbintsol(XSLPprob prob,
int (XPRS_CC *intsol) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`intsol` | The function to be called when an integer solution is obtained. `intsol` returns an integer value. At present, the return value is ignored. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb intsol`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `intsol` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed whenever an integer solution is found during MISLP:

```
double *cSol;
int nInputCol;
XPRSgetintattrib(xprob, XPRS_INPUTCOLS, &nInputCol);
cSol = (double*)malloc(nInputCol * sizeof(double));
XSLPsetcbintsol(prob, CBIntSol, &cSol);
```
 The following sample callback function saves the solution values for the integer solution just found:

```
int XPRS_CC CBIntSol(XSLPprob MyProb, void *Obj) {
  XPRSprob xprob;
  int nInputCol;
  int solStatus;
  double *cSol;

  cSol = * (double **) Obj;
  XSLPgetptrattrib(MyProb, XSLP_XPRSPROBLEM, &xprob);
  XPRSgetintattrib(xprob, XPRS_INPUTCOLS, &nInputCol);
  XPRSgetsolution(xprob, &solStatus, cSol, 0, nInputCol-1);
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`.

_**Further information:**_
This callback must be used during MISLP instead of the `XPRS set cb intsol`callback which is used for MIP problems.

_**Further information:**_
Note that for SLP-MIP-SLP \(see`XSLP_MIPALGORITHM`\), the intsol callback will only be fired once after the second SLP solve terminated, in which case the solution can also only be queried via `XPRSgetsolution`or`XSLPgetslpsol`but not via `XPRSgetlpsol`\(unless postsolve is disabled\).

_**Related topics:**_
`XSLPsetcboptnode`, `XSLPsetcbprenode`

#### XSLPsetcbiterend, XPRSsetcbslpiterend

_**Purpose:**_

   Set a user callback to be called at the end of each SLP iteration

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbiterend(XSLPprob prob,
int (XPRS_CC *iterend) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`iterend` | The function to be called at the end of each SLP iteration. `iterend` returns an integer value. If the return value is nonzero, the SLP iterations will stop. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb iter end`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `iterend` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed at the end of each SLP iteration. It records the number of LP iterations in the latest optimization and stops if there were fewer than 10:

```
XSLPsetcbiterend(prob, CBIterEnd, NULL);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBIterEnd(XSLPprob MyProb, void *Obj) {
  int nIter;
  XPRSprob xprob;
  XSLPgetptrattrib(MyProb, XSLP_XPRSPROBLEM, &xprob);
  XPRSgetintattrib(xprob, XPRS_SIMPLEXITER, &nIter);
  if (nIter < 10) return 1;
  return 0;
}
```
 The `data`argument is not used here, and so is passed as `NULL`.

_**Further information:**_
This callback can be used at the end of each SLP iteration to carry out any further processing and/or stop any further SLP iterations.

_**Related topics:**_
`XSLPsetcbiterstart`, `XSLPsetcbitervar`

#### XSLPsetcbiterstart, XPRSsetcbslpiterstart

_**Purpose:**_

   Set a user callback to be called at the start of each SLP iteration

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbiterstart(XSLPprob prob,
int (XPRS_CC *iterstart) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`iterstart` | The function to be called at the start of each SLP iteration. `iterstart` returns an integer value. If the return value is nonzero, the SLP iterations will stop. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb iter start`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `iterstart` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed at the start of the optimization to save to save the values of the variables from the previous iteration:

```
double *cSol;
XSLPsetcbiterstart(prob, CBIterStart, &cSol);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBIterStart(XSLPprob MyProb, void *Obj) {
  XPRSprob xprob;
  double *cSol;
  int nIter;
  cSol = * (double **) Obj;
  XSLPgetintattrib(MyProb, XSLP_ITER, &nIter);
  if (nIter == 0) return 0; /* no previous solution */
  XSLPgetptrattrib(MyProb, XSLP_XPRSPROBLEM, &xprob);
  XPRSgetlpsol(xprob, cSol, NULL, NULL, NULL);
  return 0;
}
```
 The `data`argument is used here to hold the address of the array `cSol`which we populate with the solution values.

_**Further information:**_
This callback can be used at the start of each SLP iteration before the optimization begins.

_**Related topics:**_
`XSLPsetcbiterend`, `XSLPsetcbitervar`

#### XSLPsetcbitervar, XPRSsetcbslpitervar

_**Purpose:**_

   Set a user callback to be called after each column has been tested for convergence

_**Topic areas:**_ 
Callback, SLP, SLP-convergence

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbitervar(XSLPprob prob,
int (XPRS_CC *itervar) (XSLPprob cbprob, void *cbdata, int col),
void *data);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`itervar` |  | The function to be called after each column has been tested for convergence. `itervar`returns an integer value. The return value is interpreted as a convergence status. The possible values are:
&nbsp; | `< 0` | The variable has not converged;
&nbsp; | `0` | Keep the internal convergence status;
&nbsp; | `1 to 10` | The column has converged on a system-defined convergence criterion \(these values should not normally be returned\);
&nbsp; | `> 10` | The variable has converged on user criteria.
`cbprob` | | The problem passed to the callback function. 
`cbdata` | | The user-defined object passed as `data` to `XSLP set cb iter var`. 
`col` | | The number of the column which has been tested for convergence. 
`data` | | A user-defined object, which can be used for any purpose by the function. `data` is passed to `itervar` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed after each variable has been tested for convergence. The user object `Important`is an integer array which has already been set up and holds a flag for each variable indicating whether it is important that it converges.

```
int *Important;
XSLPsetcbitervar(prob, CBIterVar, &Important);
```
 The following sample callback function tests if the variable is already converged. If not, then it checks if the variable is important. If it is not important, the function returns a convergence status of 99.

```
int XPRS_CC CBIterVar(XSLPprob MyProb, void *Obj, int iCol) {
  int *Important, Converged;
  Important = *(int **) Obj;
  XSLPalltype alltype;
  XSLPgetcolinfo(MyProb, XSLP_COLINFO_CONVERGENCESTATUS, iCol, &alltype);
  if (alltype.value.integer != 0) return 0;
  if (!Important[iCol]) return 99;
  return -1;
}
```
 The `data`argument is used here to hold the address of the array `Important`.

_**Further information:**_
This callback can be used after each variable has been checked for convergence, and allows the convergence status to be reset if required.

_**Related topics:**_
`XSLPsetcbiterend`, `XSLPsetcbiterstart`

#### XSLPsetcbmessage

_**Purpose:**_

   Set a user callback to be called whenever Xpress NonLinear outputs a line of text according to`XSLP_ECHOXPRSMESSAGES`.

_**Topic areas:**_ 
Callback, Logging

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbmessage(XSLPprob prob, void (XPRS_CC *message)
(XSLPprob cbprob, void *cbdata, char *msg, int msglen, int msgtype),
void *data);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`message` | | The function to be called whenever Xpress NonLinear outputs a line of text. `message` does not return a value. 
`cbprob` | | The problem passed to the callback function. 
`cbdata` | | The user-defined object passed as `data` to `XSLP set cb message`. 
`msg` | | Character buffer holding the string to be output. 
`msglen` | | Length in characters of `msg` excluding the null terminator. 
`msgtype` |  | Type of message. The following are system-defined:
&nbsp; | `1` | Information message
&nbsp; | `3` | Warning message
&nbsp; | `4` | Error message
&nbsp; |  | 
A negative value indicates that the Optimizer is about to finish and any buffers should be flushed at this time.

`data` | | A user-defined object, which can be used for any purpose by the function. `data` is passed to `message` as `cbdata`. 

_**Example:**_
The following example creates a log file into which all messages are placed. System messages are also printed on standard output:

```
FILE *logfile;
logfile = fopen("myLog","w");
XSLPsetcbmessage(prob, CBMessage, logfile);
```
 A suitable callback function could resemble the following:

```
void XPRS_CC CBMessage(XSLPprob prob, void *Obj,
                       char *msg, int msglen, int msgtype) {
  FILE *logfile;
  logfile = (FILE *) Obj;
  if (msgtype < 0) {
    fflush(stdout);
    if (logfile) fflush(logfile);
    return;
  }
  switch (msgtype) {
    case 1: /* information */
    case 3: /* warning */
    case 4: /* error */
      printf("%s\n",msg);
    default: /* user */
      if (logfile)
        fprintf(logfile,"%s\n",msg);
      break;
  }
  return;
}
```
 
_**Further information:**_
1. If a user message callback is defined then screen output is automatically disabled.
2. Output can be directed into a log file by using `XSLPsetlogfile`.

_**Related topics:**_
`XSLPsetlogfile`

#### XSLPsetcbmsjobend, XPRSsetcbmsjobend

_**Purpose:**_

   Set a user callback to be called every time a new multistart job finishes. Can be used to overwrite the default solution ranking function

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `int XSLP_CC XSLPsetcbmsjobend(XSLPprob prob,
int (XSLP_CC *msjobend)(XSLPprob cbprob, void *cbdata, void  *jobdata, const char *jobdesc, int *p_status),
void *data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`msjobend` | The function to be called when a multistart job finishes 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLPsetcbmsjobend`. 
`jobdata` | Job specific user-defined object, as specified by the multistart job creating API functions. 
`jobdesc` | The description of the problem as specified by the multistart job creating API functions. 
`p_status` | 
User return status variable:

0 - use the default evaluation of the finished job

1 - disregard the result and continue

2 - stop the multistart search
 
`data` | User data passed to the callback function. 

_**Further information:**_
The multistart pool is dynamic, and this callback can be used to load new multistart jobs using the normal API functions.

_**Related topics:**_
`XSLPsetcbmsjobstart`, `XSLPsetcbmswinner`

#### XSLPsetcbmsjobstart, XPRSsetcbmsjobstart

_**Purpose:**_

   Set a user callback to be called every time a new multistart job is created, and the pre-loaded settings are applied

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `int XSLP_CC XSLPsetcbmsjobstart(XSLPprob prob, int (XSLP_CC *msjobstart)(XSLPprob cbprob,
void *cbdata,void  *jobdata,const char *jobdesc,int *p_status), void *data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`msjobstart` | The function to be called when a new multistart job is created 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLPsetcbmsjobstart`. 
`jobdata` | Job specific user-defined object, as specified by the multistart job creating API functions. 
`jobdesc` | The description of the problem as specified by the multistart job creating API functions. 
`p_status` | 
User return status variable:

0 - normal return, solve the job,

1 - disregard this job and continue,

2 - Stop multistart.
 
`data` | User data passed to the callback function. 

_**Further information:**_
All mulit-start jobs operation on an independent copy of the original problem, and any modification to the problem is allowed, including structural changes. Please note however, that any modification will be carried over to the base problem, should a modified problem be declared the winner prob.

_**Related topics:**_
`XSLPsetcbmsjobend`, `XSLPsetcbmswinner`

#### XSLPsetcbmswinner, XPRSsetcbmswinner

_**Purpose:**_

   Set a user callback to be called every time a multistart winner has been declared

_**Topic areas:**_ 
Callback, Multistart

_**Synopsis:**_

   `int XSLP_CC XSLPsetcbmswinner(XSLPprob prob, int (XSLP_CC *mswinner)(XSLPprob cbprob,
void *cbdata,void  *jobdata,const char *jobdesc), void *data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`mswinner` | The function to be called when a multistart winner is declared. The return code is used to indicate whether callbacks should be copied over from the winner \( `≠ 0`\) or not \( `0`\). 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLPsetcbmswinner`. 
`jobdata` | Job specific user-defined object, as specified by the multistart job creating API functions. 
`jobdesc` | The description of the problem as specified by the multistart job creating API functions. 
`data` | User data passed to the callback function. 

_**Related topics:**_
`XSLPsetcbmsjobstart`, `XSLPsetcbmsjobend`

#### XSLPsetcboptnode

_**Purpose:**_

   Set a user callback to be called during MISLP when an optimal SLP solution is obtained at a node

_**Topic areas:**_ 
Callback, MISLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcboptnode(XSLPprob prob, int (XPRS_CC *optnode)
(XSLPprob cbprob, void *cbdata, int *p_infeasible), void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`optnode` | The function to be called when an optimal SLP solution is obtained at a node. `optnode` returns an integer value. If the return value is nonzero, or if the feasibility flag is set nonzero, then further processing of the node will be terminated \(it is declared infeasible\). 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb opt node`. 
`p_infeasible` | Address of an integer containing the feasibility flag. If `optnode` sets the flag nonzero, the node is declared infeasible. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `optnode` as `cbdata`. 

_**Example:**_
The following example defines a callback function to be executed at each node when an SLP optimal solution is found. If there are significant penalty errors in the solution, the node is declared infeasible.

```
XSLPsetcboptnode(prob, CBOptNode, NULL);
```
 A suitable callback function might resemble the following:

```
int XPRS_CC CBOptNode(XSLPprob cbprob, void *Obj, int *p_infeasible) {
  double Total, ObjVal;
  XSLPgetdblattrib(cbprob, XSLP_ERRORCOSTS, &Total);
  XSLPgetdblattrib(cbprob, XSLP_OBJVAL, &ObjVal);
  if (fabs(Total) > fabs(ObjVal) * 0.001 &&
    fabs(Total) > 1) *p_infeasible = 1;
  return 0;
```
 
_**Further information:**_
1. If a node is declared infeasible from the callback function, the cost of exploring the node further will be avoided.
2. This callback must be used in place of `XPRSsetcboptnode` when optimizing with MISLP.

_**Related topics:**_
`XSLPsetcbprenode`, `XSLPsetcbslpnode`

#### XSLPsetcbprenode

_**Purpose:**_

   Set a user callback to be called during MISLP after the set-up of the SLP problem to be solved at a node, but before SLP optimization

_**Topic areas:**_ 
Callback, MISLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbprenode(XSLPprob prob, int (XPRS_CC *prenode)
(XSLPprob cbprob, void *cbdata, int *p_infeasible), void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`prenode` | The function to be called after the set-up of the SLP problem to be solved at a node. `prenode` returns an integer value. If the return value is nonzero, or if the feasibility flag is set nonzero, then further processing of the node will be terminated \(it is declared infeasible\). 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb pre node`. 
`p_infeasible` | Address of an integer containing the feasibility flag. If `prenode` sets the flag nonzero, the node is declared infeasible. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `prenode` as `cbdata`. 

_**Example:**_
The following example sets up a callback function to be executed at each node before the SLP optimization starts. The array `IntList`contains a list of integer variables, and the function prints the bounds on these variables.

```
int *IntList;
XSLPsetcbprenode(prob, CBPreNode, IntList);
```
 A suitable callback function might resemble the following:

```
int XPRS_CC CBPreNode(XSLPprob cbprob, void *Obj, int *p_infeasible) {
  XPRSprob xprob;
  int i, *IntList;
  double LO, UP;
  IntList = (int *) Obj;
  XSLPgetptrattrib(cbprob, XSLP_XPRSPROBLEM, &xprob);
  for (i=0; IntList[i]>=0; i++) {
    XPRSgetlb(xprob,&LO,IntList[i],IntList[i]);
    XPRSgetub(xprob,&UP,IntList[i],IntList[i]);
    if (LO > 0 || UP < XPRS_PLUSINFINITY)
      printf("\nCol %d: %lg <= %lg",LO,UP);
  }
  return 0;
}
```
 
_**Further information:**_
1. If a node can be identified as infeasible by the callback function, then the initial optimization at the current node is avoided, as well as further exploration of the node.
2. This callback must be used in place of `XPRSsetcbprenode` when optimizing with MISLP.

_**Related topics:**_
`XSLPsetcboptnode`, `XSLPsetcbslpnode`

#### XSLPsetcbpreupdatelinearization, XPRSsetcbslppreupdatelinearization

_**Purpose:**_

   Set a user callback to be called before the linearization is updated

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbpreupdatelinearization(XSLPprob prob,
int (XPRS_CC *preupdatelinearization) (XSLPprob cbprob, void *cbdata, int *when),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`preupdatelinearization` | The function to be called before the linearization is updated. `preupdatelinearization` returns an integer value. If the return value is nonzero, the optimization will return an error code and the "User Return Code" error will be set. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLPsetcbpreupdatelinearization`. 
`when` | Indicates the call number, starting at 1. If returned nonzero, another call to the callback will be scheduled. If returned zero, a final call with `*when == -1` will be made. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `preupdatelinearization` as `cbdata`. 

_**Further information:**_
1. When the linearization is updated, all user functions are evaluated and their derivatives calculated at the current base point. In some models, it is cheaper to compute the derivatives for all user functions at the same time, thereby avoiding repeated calculations for each function. This callback is intended to be used in such cases.
2. During each SLP iteration, the callback is invoked repeatedly, with `*when` indicating the current call number \(starting from 1\), until the callback indicates that no further calls are needed, by setting `*when = 0`. Between each callback invocation, the solver evaluates the user functions without requesting derivatives. After the callback has set `*when = 0`, the user functions are evaluated one more time, this time requesting derivatives, and then finally the callback is called with `*when == -1`, marking the end of the linearization update. The only time derivatives will be requested outside of this sequence is during KKT validation. This can be disabled during the solve by clearing the `XSLP_CONVERGEBIT_VALIDATION_K` bit in `XSLP_CONVERGENCEOPS`, ensuring that derivatives can always be precomputed.
3. One way that this callback can be used to precompute derivatives for user functions is as follows:
 1. On each SLP iteration, the callback is first called with `*when = 1`. This is a signal that derivatives will be needed soon. The callback sets a flag to indicate that user functions should capture their input values.
 2. When the callback returns, the user functions are evaluated without requesting derivatives. Each user function captures its input values somewhere, and returns the correct function value.
 3. The callback is called again, with `*when == 2`. The callback now computes derivates for all user functions using the captured input values. The callback clears the flag so that user functions no longer capture their input values, and sets `*when = 0` to indicate that no further calls are needed.
 4. When the callback returns, the user functions are evaluated again. Derivatives are requested, and the user functions return the precomputed derivative values.
 5. The callback is invoked one more time for this iteration with `*when == -1`, marking the end of the linearization update. User functions should behave normally from this point.

_**Related topics:**_
[User functions](#secUserFunctions2), `XSLPdeluserfunction`, `XSLPimportlibfunc`

#### XSLPsetcbpresolved

_**Purpose:**_

   Set a user callback to be called after the nonlinear presolver has been applied.

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XSLP_CC XSLPsetcbpresolved(XSLPprob prob, int (XSLP_CC *presolved)(XSLPprob cbprob, void *cbdata), void *data);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`presolved` | The function to be invoked after the nlp presolver is completed. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object received by the callback. 
`data` | The user-defined object passed as `cbdata` to `presolved`. 

#### XSLPsetcbslpend

_**Purpose:**_

   Set a user callback to be called at the end of the SLP optimization

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbslpend(XSLPprob prob,
int (XPRS_CC *slpend) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`slpend` | The function to be called at the end of the SLP optimization. `slpend` returns an integer value. If the return value is nonzero, the optimization will return an error code and the "User Return Code" error will be set. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb slp end`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpend` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed at the end of the SLP optimization. It frees the memory allocated to the object created when the optimization began:

```
void *ObjData;
ObjData = NULL;
XSLPsetcbslpend(prob, CBSlpEnd, &ObjData);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBSlpEnd(XSLPprob MyProb, void *Obj) {
  void *ObjData;
  ObjData = * (void **) Obj;
  if (ObjData) free(ObjData);
  * (void **) Obj = NULL;
  return 0;
}
```
 
_**Further information:**_
This callback can be used at the end of the SLP optimization to carry out any further processing or housekeeping before the optimization function returns.

_**Related topics:**_
`XSLPsetcbslpstart`

#### XSLPsetcbslpnode

_**Purpose:**_

   Set a user callback to be called during MISLP after the SLP optimization at each node.

_**Topic areas:**_ 
Callback, MISLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbslpnode(XSLPprob prob, int (XPRS_CC *slpnode)
(XSLPprob cbprob, void *cbdata, int *p_infeasible), void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`slpnode` | The function to be called after the SLP optimization at a node. `slpnode` returns an integer value. If the return value is nonzero, or if the feasibility flag is set nonzero, then further processing of the node will be terminated \(it is declared infeasible\). 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb slp node`. 
`p_infeasible` | Address of an integer containing the feasibility flag. If `slpnode` sets the flag nonzero, the node is declared infeasible. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpnode` as `cbdata`. 

_**Example:**_
The following example sets up a callback function to be executed at each node after the SLP optimization finishes. If the solution value is worse than a target value \(referenced through the user object\), the node is cut off \(it is declared infeasible\).

```
double OBJtarget;
XSLPsetcbslpnode(prob, CBSLPNode, &OBJtarget);
```
 A suitable callback function might resemble the following:

```
int XPRS_CC CBSLPNode(XSLPprob cbprob, void *Obj, int *p_infeasible) {
  double TargetValue, LPValue;
  XSLPgetdblattrib(prob, XPRS_LPOBJVAL, &LPValue);
  TargetValue = * (double *) Obj;
  if (LPValue < TargetValue) *p_infeasible = 1;
  return 0;
}
```
 
_**Further information:**_
If a node can be cut off by the callback function, then further exploration of the node is avoided.

_**Related topics:**_
`XSLPsetcboptnode`, `XSLPsetcbprenode`

#### XSLPsetcbslpstart

_**Purpose:**_

   Set a user callback to be called at the start of the SLP optimization

_**Topic areas:**_ 
Callback, SLP

_**Synopsis:**_

   `int XPRS_CC XSLPsetcbslpstart(XSLPprob prob,
int (XPRS_CC *slpstart) (XSLPprob cbprob, void *cbdata),
void *data);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`slpstart` | The function to be called at the start of the SLP optimization. `slpstart` returns an integer value. If the return value is nonzero, the optimization will not be carried out. 
`cbprob` | The problem passed to the callback function. 
`cbdata` | The user-defined object passed as `data` to `XSLP set cb slp start`. 
`data` | A user-defined object, which can be used for any purpose by the function. `data` is passed to `slpstart` as `cbdata`. 

_**Example:**_
The following example sets up a callback to be executed at the start of the SLP optimization. It allocates memory to a user-defined object to be used during the optimization:

```
void *ObjData;
ObjData = NULL;
XSLPsetcbslpstart(prob, CBSlpStart, &ObjData);
```
 A suitable callback function might resemble this:

```
int XPRS_CC CBSlpStart(XSLPprob MyProb, void *Obj) {
  void *ObjData;
  ObjData = * (void **) Obj;
  if (ObjData) free(ObjData);
  * (void **) Obj = malloc(99*sizeof(double));
  return 0;
}
```
 
_**Further information:**_
This callback can be used at the start of the SLP optimization to carry out any housekeeping before the optimization actually starts. Note that a nonzero return code from the callback will terminate the optimization immediately.

_**Related topics:**_
`XSLPsetcbslpend`

#### XSLPsetcurrentiv, XPRSnlpsetcurrentiv

_**Purpose:**_

   Transfer the current solution to initial values

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `
    int XPRS_CC XSLPsetcurrentiv(XSLPprob prob);
  `

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Further information:**_
Provides a way to set the current iterates solution as initial values, make changes to parameters or to the underlying nonlinear problem and then rerun the SLP optimization process.

_**Related topics:**_
`XSLPreinitialize`, `XSLPunconstruct`

#### XSLPsetdblcontrol

_**Purpose:**_

   Set the value of a double precision problem control

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPsetdblcontrol(XSLPprob prob, int control, double value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | control \(SLP or optimizer\) whose value is to be returned. 
`value` | Double precision value to be set. 

_**Example:**_
The following example sets the value of the Xpress NonLinear control`XSLP_CTOL`and of the optimizer control `XPRS_FEASTOL`:

```
XSLPsetdblcontrol(prob, XSLP_CTOL, 0.001);
XSLPgetdblcontrol(prob, XPRS_FEASTOL, 0.005);
```
 
_**Further information:**_
Both SLP and optimizer controls can be set using this function. If an optimizer control is set, the return value will be the same as that from[XPRSsetdblcontrol](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSsetdblcontrol.html), which can similarly be used to set both Optimizer and SLP controls.

_**Related topics:**_
`XSLPgetdblcontrol`, `XSLPsetintcontrol`, `XSLPsetstrcontrol`

#### XSLPsetdefaultcontrol

_**Purpose:**_

   Set the values of one SLP control to its default value

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPsetdefaultcontrol(XSLPprob prob, int control);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | The number of the control to be reset to its default. 

_**Example:**_
The following example reads a problem from file, sets the XSLP\_LOG control, optimizes the problem \(using the "s" flag to enforce a local solve\) and then reads and optimizes another problem using the default setting.

```
XSLPreadprob(prob, "Matrix1", "");
XSLPsetintcontrol(prob, XSLP_LOG, 4);
XSLPnlpoptimize(prob, "s");
XSLPsetdefaultcontrol(prob,XSLP_LOG);
XSLPreadprob(prob, "Matrix2", "");
XSLPnlpoptimize(prob, "s");
```
 
_**Further information:**_
This also resets optimizer controls.

_**Related topics:**_
`XSLPsetdblcontrol`, `XSLPsetdefaults`, `XSLPsetintcontrol`, `XSLPsetstrcontrol`, `XSLP_CONTROL`

#### XSLPsetdefaults

_**Purpose:**_

   Set the values of all SLP controls to their default values

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPsetdefaults(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_
The following example reads a problem from file, sets some controls, optimizes the problem \(using the "s" flag to enforce a local solve\) and then reads and optimizes another problem using the default settings.

```
XSLPreadprob(prob, "Matrix1", "");
XSLPsetintcontrol(prob, XSLP_LOG, 4);
XSLPsetdblcontrol(prob, XSLP_CTOL, 0.001);
XSLPsetdblcontrol(prob, XSLP_ATOL_A, 0.005);
XSLPnlpoptimize(prob, "s");
XSLPsetdefaults(prob);
XSLPreadprob(prob, "Matrix2", "");
XSLPnlpoptimize(prob, "s");
```
 
_**Further information:**_
1. This function also resets all Knitro parameters to their default values.
2. This also resets optimizer controls unless bit 4 of `XSLP_CONTROL` is set.

_**Related topics:**_
`XSLPsetdblcontrol`, `XSLPsetintcontrol`, `XSLPsetstrcontrol`

#### XSLPsetdetrow, XPRSslpsetdetrow

_**Purpose:**_

   Set the determining row of a variable

_**Topic areas:**_ 
SLP, Cascading, Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPsetdetrow(XSLPprob prob, int nvars, const int[] colind, const int[] rowind);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`nvars` | The number of variables for which determining rows are set. 
`colind` | Array of length `nvars` with the index of the column for which the determining row is set. 
`rowind` | Array of length `nvars` with the index of the determining row. 

_**Related topics:**_
`XSLPsetinitval`

#### XSLPsetfunctionerror, XPRSnlpsetfunctionerror

_**Purpose:**_

   Set the function error flag for the problem

_**Topic area:**_ 
Misc

_**Synopsis:**_

   `int XPRS_CC XSLPsetfunctionerror(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Further information:**_
Once the function error has been set, calculations generally stop and the routines will return to their caller with a nonzero return code.

#### XSLPsetinitstepbounds, XPRSslpsetinitstepbounds

_**Purpose:**_

   Set the initial step bounds of columns

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPsetinistepbounds(XSLPprob prob, int ncols, const int[] colind, const double[] initial);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`ncols` | Number of columns for which the initial step bound is to be set. 
`colind` | Array of length `ncols` with index of the column for which the initial step bound is provided. 
`initial` | Array of length `ncols` with the initial step bounds. 

#### XSLPsetinitval, XPRSnlpsetinitval

_**Purpose:**_

   Set the initial value of columns

_**Topic area:**_ 
Data Input

_**Synopsis:**_

   `int XPRS_CC XSLPsetinitval(XSLPprob prob, int nvars, const int[] colind, const double[] initial);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`nvars` | Number of variables for which the initial value is to be set. 
`colind` | Array of length `nvars` with index of the column for which the initial value is provided. 
`initial` | Array of length `nvars` with the initial value. 

_**Related topics:**_
`XSLPsetdetrow`

#### XSLPsetintcontrol

_**Purpose:**_

   Set the value of an integer problem control

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPsetintcontrol(XSLPprob prob, int control, int value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | control \(SLP or optimizer\) whose value is to be returned. 
`value` | The value to be set. 

_**Example:**_
The following example sets the value of the Xpress NonLinear control`XSLP_ALGORITHM`and of the optimizer control `XPRS_DEFAULTALG`:

```
XSLPsetintcontrol(prob, XSLP_ALGORITHM, 934);
XSLPsetintcontrol(prob, XPRS_DEFAULTALG, 3);
```
 
_**Further information:**_
Both SLP and optimizer controls can be set using this function. If an optimizer control is set, the return value will be the same as that from[XPRSsetintcontrol](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSsetintcontrol.html), which can similarly be used to set both Optimizer and SLP controls.

_**Related topics:**_
`XSLPgetintcontrol`, `XSLPsetdblcontrol`, `XSLPsetintcontrol`, `XSLPsetstrcontrol`

#### XSLPsetlogfile

_**Purpose:**_

   Define an output file to be used to receive messages from Xpress NonLinear

_**Topic areas:**_ 
Logging, File IO

_**Synopsis:**_

   `int XPRS_CC XSLPsetlogfile(XSLPprob prob, char *Filename, int option);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`filename` | Character string containing the name of the file to be used for output. 
`option` | option to indicate whether the output is directed to the file only \( `option` =0\) or \(in console mode\) to the console as well \( `option` =1\). 

_**Example:**_
The following example defines a log file "MyLog1" and directs output to the file and to the console:

```
XSLPsetlogfile(prob, "MyLog1", 1);
```
 
_**Further information:**_
If `Filename`is `NULL`, the current log file \(if any\) will be closed, and message handling will revert to the default mechanism.

_**Related topics:**_
`XSLPsetcbmessage`

#### XSLPsetparam

_**Purpose:**_

   Set the value of a control parameter by name

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPsetparam(XSLPprob prob, const char *name,
  const char *value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`name` | Name of the control or attribute whose value is to be returned. 
`value` | Character buffer containing the value. 

_**Example:**_
The following example sets the value of XSLP\_ALGORITHM:

```
XSLPprob prob;
int Algorithm;
char Buffer[32];
Algorithm = 934;
sprintf(Buffer,"%d",Algorithm);
XSLPsetparam(prob, "XSLP_ALGORITHM", Buffer);
```
 
_**Further information:**_
This function can be used to set any Xpress NonLinear or Optimizer control. The value is always passed as a character string. It is the user's responsibility to create the character string in an appropriate format.

_**Related topics:**_
`XSLPsetdblcontrol`, `XSLPsetintcontrol`, `XSLPsetparam`, `XSLPsetstrcontrol`

#### XSLPsetstrcontrol

_**Purpose:**_

   Set the value of a string problem control

_**Topic area:**_ 
Controls and Attributes

_**Synopsis:**_

   `int XPRS_CC XSLPsetstrcontrol(XSLPprob prob, int control,
const char *value);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`control` | control \(SLP or optimizer\) whose value is to be returned. 
`value` | Character buffer containing the value. 

_**Further information:**_
Both SLP and optimizer controls can be set using this function. If an optimizer control is set, the return value will be the same as that from[XPRSsetstrcontrol](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/XPRSsetstrcontrol.html), which can similarly be used to set both Optimizer and SLP controls.

_**Related topics:**_
`XSLPgetstrcontrol`, `XSLPsetdblcontrol`, `XSLPsetintcontrol`, `XSLPsetstrcontrol`

#### XSLPunconstruct, XPRSslpunconstruct

_**Purpose:**_

   Removes the augmentation and returns the problem to its pre-linearization state

_**Topic areas:**_ 
SLP, Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPunconstruct(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Further information:**_
Only limited changes are allowed to an augmented problem.

_**Related topics:**_
`XSLPconstruct`

#### XSLPupdatelinearization, XPRSslpupdatelinearization

_**Purpose:**_

   Updates the current linearization

_**Topic areas:**_ 
SLP, Solution Process

_**Synopsis:**_

   `int XPRS_CC XSLPupdatelinearization(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Further information:**_
1. Updates the augmented problem \(the linearization\) to match the current base point. The base point is the current SLP solution.The values of the SLP variables can be changed using`XSLPchgvar`.
2. The linearization must be present, and this function can only be called after the problem has been augmented by `XSLPconstruct`.

_**Related topics:**_
`XSLPconstruct`

#### XSLPvalidate, XPRSnlpvalidate

_**Purpose:**_

   Validate the feasibility of constraints in a converged solution

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPvalidate(XSLPprob prob);`

_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Example:**_
The following example sets the validation tolerance parameters, validates the converged solution and retrieves the validation indices.

```
double IndexA, IndexR;
XSLPsetdblcontrol(prob, XSLP_VALIDATIONTOL_A, 0.001);
XSLPsetdblcontrol(prob, XSLP_VALIDATIONTOL_R, 0.001);
XSLPvalidate(prob);
XSLPgetdblattrib(prob, XSLP_VALIDATIONINDEX_A, &IndexA);
XSLPgetdblattrib(prob, XSLP_VALIDATIONINDEX_R, &IndexR);
```
 

_**Further information:**_
`XSLPvalidate`checks the feasibility of a converged solution against relative and absolute tolerances for each constraint. The left hand side and the right hand side of the constraint are calculated using the converged solution values. If the calculated values imply that the constraint is infeasible, then the difference \( _D_ \) is tested against the absolute and relative validation tolerances.

If _D<XSLP\_VALIDATIONTOL\_A_ 

then the constraint is within the absolute validation tolerance. The total positive \( _TPos_ \) and negative contributions \( _TNeg_ \) to the left hand side are also calculated.

If _D<MAX\(ABS\(TPos\), ABS\(TNeg\)\)\* XSLP\_VALIDATIONTOL\_R_ 

then the constraint is within the relative validation tolerance. For each constraint which is outside both the absolute and relative validation tolerances, validation factors are calculated which are the factors by which the infeasibility exceeds the corresponding validation tolerance; the smallest factor is printed in the validation report.

The validation index`XSLP_VALIDATIONINDEX_A`is the largest absolute validation factor multiplied by the absolute validation tolerance; the validation index`XSLP_VALIDATIONINDEX_R`is the largest relative validation factor multiplied by the relative validation tolerance.

_**Related topics:**_
`XSLP_VALIDATIONINDEX_A`, `XSLP_VALIDATIONINDEX_R`, `XSLP_VALIDATIONTOL_A`, `XSLP_VALIDATIONTOL_R`

#### XSLPvalidatekkt, XPRSnlpvalidatekkt

_**Purpose:**_

   Validates the first order optimality conditions also known as the Karush-Kuhn-Tucker \(KKT\) conditions versus the currect solution

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPvalidatekkt(XSLPprob prob, int mode, int respectbasis, int updatemult, double violtarget);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`mode` |  | The calculation mode can be:
&nbsp; | `0` | recalculate the reduced costs at the current solution using the current dual solution.
&nbsp; | `1` | minimize the sum of KKT violations by adjusting the dual solution.
&nbsp; | `2` | perform both.
`respectbasis` |  | The following ways are defined to assess if a constraint is active:
&nbsp; | `0` | evaluate the recalculated slack activity versus `XSLP_ECFTOL_R`.
&nbsp; | `1` | use the basis status of the slack in the linearized problem if available.
&nbsp; | `2` | use both.
`updatemult` |  | The calculated values can be:
&nbsp; | `0` | only used to calculate the `XSLP_VALIDATIONINDEX_K` measure.
&nbsp; | `1` | used to update the current dual solution and reduced costs.
`violtarget` | | When calculating the best KKT multipliers, it is possible to enforce an even distribution of reduced costs violations by enforcing a bound on them. 

_**Further information:**_
The bounds enforced by violtarget are automatically relaxed if the desired accuracy cannot be achieved.

#### XSLPvalidateprob, XPRSnlpvalidateprob

_**Purpose:**_

   Validates the current problem formulation and statement

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPvalidateprob(XSLPprob prob, int *p_nerrors, int *p_nwarnings);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`p_nerrors` | Returns the number of errors found in the problem. Errors are expected to make the problem not solve. 
`p_nwarnings` | Returns the number of potential issues found in the problem. The solver may be able to automatically recover during the solve. 

_**Further information:**_
This function is expected to be used in the development stage of a model.

#### XSLPvalidaterow, XPRSnlpvalidaterow

_**Purpose:**_

   Prints an extensive analysis on a given constraint of the SLP problem

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPvalidaterow(XSLPprob prob, int row);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the row to be analyzed 

_**Further information:**_
The analysis will include the readable format of the original constraint and the augmented constraint. For infeasible constraints, the absolute and relative infeasibility is calculated. Variables in the constraints are listed including their value in the solution of the last linearization, the internal value \(e.g. cascaded\), reduced cost, step bound and convergence status. Scaling analysis is also provided.

#### XSLPvalidatevector, XPRSnlpvalidatevector

_**Purpose:**_

   Validate the feasibility of constraints for a given solution

_**Topic area:**_ 
Solution

_**Synopsis:**_

   `int XPRS_CC XSLPvalidatevector(XSLPprob prob, const double[] solution, double *p_suminf, double *p_sumscaledinf, double *p_objval);`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`solution` | A vector of length `XPRS_COLS` containing the solution vector to be checked. 
`p_suminf` | Pointer to double in which the sum of infeasibility will be returned. May be NULL if not required. 
`p_sumscaledinf` | Pointer to double in which the sum of scaled \(relative\) infeasibility will be returned. May be NULL if not required. 
`p_objval` | Pointer to double in which the net objective will be returned. May be NULL if not required. 

_**Further information:**_
`XSLPvalidatevector`works the same way as`XSLPvalidate`, and will update`XSLP_VALIDATIONINDEX_A`and`XSLP_VALIDATIONINDEX_R`.

_**Related topics:**_
`XSLP_VALIDATIONINDEX_A`, `XSLP_VALIDATIONINDEX_R`, `XSLP_VALIDATIONTOL_A`, `XSLP_VALIDATIONTOL_R`

#### XSLPwriteprob

_**Purpose:**_

   Write the current problem to a file in extended MPS or text format

_**Topic areas:**_ 
File IO, Problem Information

_**Synopsis:**_

   `int XPRS_CC XSLPwriteprob(XSLPprob prob, char *filename, char *flags);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`filename` | | Character string holding the name of the file to receive the output. The extension ".mat" will automatically be appended to the file name, except for LP format when ".lp" will be appended. 
`flags` |  | The following flags can be used:
&nbsp; | `a` | write the current approximation \(linearized\) matrix \(the default is to write the non-linear matrix including formulae\);
&nbsp; | `o` | one coefficient per line \(the default is up to two numbers or one formula per line\);
&nbsp; | `l` | write the matrix in LP format, similar to the LP format written by XPRSwriteprob, with more SLP specific information
&nbsp; | `s` | "scrambled" names \(the default is to use the names provided on input\);
&nbsp; | `v` | use the provided filename verbatim, without appending the `.mps` or `.lp` extension;
&nbsp; | `z` | write a compressed file.

_**Example:**_
The following example reads a problem from file, augments it and writes the augmented \(linearized\) matrix in text form to file "output.lp":

```
XSLPreadprob(prob, "Matrix", "");
XSLPconstruct(prob);
XSLPwriteprob(prob, "output", "l");
```
 
_**Related topics:**_
`XSLPreadprob`

#### XSLPwriteslxsol

_**Purpose:**_

   Write the current solution to an MPS like file format

_**Topic areas:**_ 
File IO, Solution

_**Synopsis:**_

   `int XPRS_CC XSLPwriteslxsol(XSLPprob prob, char *filename, char *flags);`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`prob` | | The current SLP problem. 
`filename` | | Character string holding the name of the file to receive the output. The extension ".slx" will automatically be appended to the file name, unless an extension is already specified in the filename. 
`flags` |  | The following flags can be used:
&nbsp; | `p` | use double precision numbers;
&nbsp; | `v` | use the provided filename verbatim, without appending the `.slx` extension;
&nbsp; | `z` | write a compressed file.

### Chapter 22 Internal Functions


Xpress NonLinear provides a set of standard functions for use in formulae. Many are standard mathematical functions; there are a few which are intended for specialized applications.

The following is a list of all the Xpress NonLinear internal functions:



_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`ABS` | Absolute value
`ARCCOS` | Arc cosine trigonometric function
`ARCSIN` | Arc sine trigonometric function
`ARCTAN` | Arc tangent trigonometric function
`COS` | Cosine trigonometric function
`ERF` | The error function
`ERFC` | The complementary error function
`EXP` | Exponential function \(e raised to the power\)
`LN` | Natural logarithm
`LOG10` | Logarithm to base 10
`MAX` | Maximum value of two or more expressions
`MIN` | Minimum value of two or more expressions
`PWL` | The piecewise linear function
`SIGN` | The sign function
`SIN` | Sine trigonometric function
`SQRT` | Square root
`TAN` | Tangent trigonometric function

#### Section 22.1 Trigonometric functions


The trigonometric functions `SIN`, `COS` and `TAN` return the value corresponding to their argument in radians. `SIN` and `COS` are well-defined, continuous and differentiable for all values of their arguments; care must be exercised when using `TAN` because it is discontinuous.

The inverse trigonometric functions `ARCSIN` and `ARCCOS` are undefined for arguments outside the range -1 to +1 and special care is required to ensure that no attempt is made to evaluate them outside this range. Derivatives for the inverse trigonometric functions are always calculated numerically.

#### ARCCOS

_**Purpose:**_

   Arc cosine trigonometric function

_**Synopsis:**_

   `ARCSIN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Return value:**_
A value in the range _0_ to _+π_ .

_**Further information:**_
`value`must be in the range -1 to +1. Values outside the range will return zero and produce an appropriate error message. If`XSLP_STOPOUTOFRANGE`is set then the function error flag will be set.

#### ARCSIN

_**Purpose:**_

   Arc sine trigonometric function

_**Synopsis:**_

   `ARCSIN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Return value:**_
A value in the range _-π/2_ to _+π/2_ .

_**Further information:**_
`value`must be in the range -1 to +1. Values outside the range will return zero and produce an appropriate error message. If`XSLP_STOPOUTOFRANGE`is set then the function error flag will be set.

#### ARCTAN

_**Purpose:**_

   Arc tangent trigonometric function

_**Synopsis:**_

   `ARCTAN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Return value:**_
A value in the range _-π/2_ to _+π/2_ .

#### COS

_**Purpose:**_

   Cosine trigonometric function

_**Synopsis:**_

   `COS(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### SIN

_**Purpose:**_

   Sine trigonometric function

_**Synopsis:**_

   `SIN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### TAN

_**Purpose:**_

   Tangent trigonometric function

_**Synopsis:**_

   `TAN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### Section 22.2 Other mathematical functions


Most of the mathematical functions are differentiable, although care should be taken in using analytic derivatives where the derivative is changing rapidly.

#### ABS

_**Purpose:**_

   Absolute value

_**Synopsis:**_

   `ABS(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Further information:**_
`ABS`is not always differentiable and so alternative modeling approaches should be used where possible.

#### ERF

_**Purpose:**_

   The error function

_**Synopsis:**_

   `ERF(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### ERFC

_**Purpose:**_

   The complementary error function

_**Synopsis:**_

   `ERFC(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### EXP

_**Purpose:**_

   Exponential function \(e raised to the power\)

_**Synopsis:**_

   `EXP(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### LN

_**Purpose:**_

   Natural logarithm

_**Synopsis:**_

   `LN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Further information:**_
`value`must be strictly positive \(greater than 1.0E-300\).

#### LOG10

_**Purpose:**_

   Logarithm to base 10

_**Synopsis:**_

   `LOG10(value)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Further information:**_
`value`must be strictly positive \(greater than 1.0E-300\).

#### MAX

_**Purpose:**_

   Maximum value of two or more expressions

_**Synopsis:**_

   `MAX(value1, value2)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value1, value2` | Each argument is one of the following: a constant; a variable; a formula evaluating to a single value 

_**Further information:**_
1. `MAX` is not always differentiable and so alternative modeling approaches should be used where possible.
2. In mmxnlp, `fmax` is used to represent the max function.

#### MIN

_**Purpose:**_

   Minimum value of two or more expressions

_**Synopsis:**_

   `MIN(value1, value2)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value1, value2` | Each argument is one of the following: a constant; a variable; a formula evaluating to a single value 

_**Further information:**_
1. `MIN` is not always differentiable and so alternative modeling approaches should be used where possible.
2. In mmxnlp, `fmin` is used to represent the min function.

#### PWL

_**Purpose:**_

   The piecewise linear function

_**Synopsis:**_

   `PWL( variable, x1, y1, ..., xk, yk )`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`variable` | is a single variable that describes where the pwl shold be evaluated. 
`x1,y2, ..., xk, yk` | are the k breakpoints of the piecewise linear function. The pwl is extended to minus and plus infinity using the first and last 2 breakpoints respectively. 

#### SIGN

_**Purpose:**_

   The sign function

_**Synopsis:**_

   `SIGN(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

#### SQRT

_**Purpose:**_

   Square root

_**Synopsis:**_

   `SQRT(value)`

_**Argument:**_

Name |  Description
---------- | ---------- 
`value` | One of the following: a constant; a variable; a formula evaluating to a single value 

_**Further information:**_
`value`must be non-negative.

### Chapter 23 Error Messages


If the optimization procedure or some other library function encounters an error, then the procedure normally terminates with a nonzero return code and sets an error code. For most functions, the return code is 32 for an error; those functions which can return Optimizer return codes \(such as the functions for accessing attributes and controls\) will return the Optimizer code in such circumstances.

If an error message is produced, it will normally be output to the message handler; for console-based output, it will appear on the console. The error message and the error code can also be obtained using the function `XSLPgetlasterror`. This allows the user to retrieve the message number and/or the message text. The format is:

```
XSLPgetlasterror(Prob, &ErrorCode, &ErrorMessage);

```


The following is a list of the error codes and an explanation of the message. In the list, error numbers are prefixed by _E-_ and warnings by _W-_. The printed messages are generally prefixed by _Xpress NonLinear error_ and _Xpress NonLinear warning_ respectively.

 * __E-12001__   __*invalid parameter number `num`*__
   This message is produced by the functions which access SLP or Optimizer controls and attributes. The parameter numbers for SLP are given in the header file `xslp.h`. The parameter is of the wrong type for the function, or cannot be changed by the user.
 * __E-12002__   __*internal hash error*__
   This is a non-recoverable program error. If this error is encountered, please contact your local Xpress support office.
 * __E-12003__   __*XSLPprob problem pointer is NULL*__
   The problem pointer has not been initialized and contains a zero address. Initialize the problem using `XSLPcreateprob`.
 * __E-12004__   __*XSLPprob is corrupted or is not a valid problem*__
   The problem pointer is not the address of a valid problem. The problem pointer has been corrupted, and no longer contains the correct address; or the problem has not been initialized correctly; or the problem has been corrupted in memory. Check that your program is using the correct pointer and is not overwriting part of the memory area.
 * __E-12005__   __*memory manager error - allocation error*__
   This message normally means that the system has run out of memory when trying to allocate or reallocate arrays. Use `XSLPprintmemory` to obtain a list of the arrays and amounts of memory allocated by the system. Ensure that any memory allocated by user programs is freed at the appropriate time.
 * __E-12006__   __*memory manager error - `Array`expansion size \( `num`\)≤0*__
   This may be caused by incorrect setting of the `XSLP_EXTRA*` control parameters to negative numbers. Use `XSLPprintmemory` to obtain a list of the arrays and amounts of memory allocated by the system for the specified array. If the problem persists, please contact your local Xpress support office.
 * __E-12007__   __*memory manager error - object `Obj`size not defined*__
   This is a non-recoverable program error. If this error is encountered, please contact your local Xpress support office.
 * __E-12008__   __*cannot open file `name`*__
   This message appears when Xpress NonLinear is required to open a file of any type and encounters an error while doing so. Check that the file name is spelt correctly \(including the path, directory or folder\) and that it is accessible \(for example, not locked by another application\).
 * __E-12009__   __*cannot open problem file `name`*__
   This message is produced by `XSLPreadprob` if it cannot find `name.mat`, `name.mps` or `name`. Note that "lp" format files are not accepted for SLP input.
 * __E-12010__   __*internal I/O error*__
   This error is produced by `XSLPreadprob` if it is unable to read or write intermediate files required for input.
 * __E-12011__   __*XSLPreadprob unknown record type `name`*__
   This error is produced by `XSLPreadprob` if it encounters a record in the file which is not identifiable. It may be out of place \(for example, a matrix entry in the _BOUNDS_ section\), or it may be a completely invalid record type.
 * __E-12012__   __*XSLPreadprob invalid function argument type `name`*__
   This error is produced by `XSLPreadprob` if it encounters a user function definition with an argument type that is not one of `NULL`, `DOUBLE`, `INTEGER`, `CHAR` or `VARIANT`.
 * __E-12013__   __*XSLPreadprob invalid function linkage type `name`*__
   This error is produced by `XSLPreadprob` if it encounters a user function with a linkage type that is not one of `DLL`, `XLS`, `XLF`, `MOSEL` or `COM`.
 * __E-12014__   __*XSLPreadprob unrecognized function `name`*__
   This error is produced by `XSLPreadprob` if it encounters a function reference in a formula which is not a pre-defined internal function nor a defined user function. Check the formula and the function name, and define the function if required.
 * __E-12015__   __*`func`: `item` `num`out of range*__
   This message is produced by the Xpress NonLinear function `func` which is referencing the SLP `item` \(row, column variable, etc\). The index provided is out of range \(less than 1 unless zero is explicitly allowed, or greater than the current number of items of that type\). Remember that most Xpress NonLinear items count from 1.
 * __E-12016__   __*missing left bracket in formula*__
   This message is produced during parsing of formulae provided in character or unparsed internal format. A right bracket is not correctly paired with a corresponding left bracket. Check the formulae.
 * __E-12017__   __*missing left operand in formula*__
   This message is produced during parsing of formulae provided in character or unparsed internal format. An operator which takes two operands is missing the left hand one \(and so immediately follows another operator or a bracket\). Check the formulae.
 * __E-12018__   __*missing right operand in formula*__
   This message is produced during parsing of formulae provided in character or unparsed internal format. An operator is missing the right hand \(following\) operand \(and so is immediately followed by another operator or a bracket\). Check the formulae.
 * __E-12019__   __*missing right bracket in formula*__
   This message is produced during parsing of formulae provided in character or unparsed internal format. A left bracket is not correctly paired with a corresponding right bracket. Check the formulae.
 * __E-12020__   __*column\#  `n`is defined more than once as an SLP variable*__
   This message is produced by `XSLPaddvars` or `XSLPloadvars` if the same column appears more than once in the list, or has already been defined as an SLP variable. Although `XSLPchgvar` is less efficient, it can be used to set the properties of an SLP variable whether or not it has already been declared.
 * __E-12022__   __*undefined tolerance type `name`*__
   This error is produced by `XSLPreadprob` if it encounters a tolerance which is not one of the 9 defined types \( `TC`, `TA`, `TM`, `TI`, `TS`, `RA`, `RM`, `RI`, `RS`\). Check the two-character code for the tolerance.
 * __W-12023__   __*`name`has been given a tolerance but is not an SLP variable*__
   This error is produced by `XSLPreadprob` if it encounters a tolerance for a variable which is not an SLP variable \(it is not in a coefficient, it does not have a non-constant coefficient and it has not been given an initial value\). If the tolerance is required \(that is, if the variable is to be monitored for convergence\) then give it an initial value so that it becomes an SLP variable. Otherwise, the tolerance will be ignored.
 * __W-12024__   __*`name`has been given SLP data of type `ty`but is not an SLP variable*__
   This error is produced by `XSLPreadprob` if it encounters _SLPDATA_ for a variable which has not been defined as an SLP variable. Typically, this is because the variable would only appear in coefficients, and the relevant coefficients are missing. The data item will be ignored.
 * __E-12025__   __*`func`has the same source and destination problems*__
   This message is produced by `XSLPcopycallbacks`, `XSLPcopycontrols` and `XSLPcopyprob` if the source and destination problems are the same. If they are the same, then there is no point in copying them.
 * __E-12026__   __*invalid or corrupt SAVE file*__
   This message is produced by `XSLPrestore` if the SAVE file header is not valid, or if internal consistency checks fail. Check that the file exists and was created by `XSLPsave`.
 * __E-12027__   __*SAVE file version is too old*__
   This message is produced by `XSLPrestore` if the SAVE file was produced by an earlier version of Xpress NonLinear. In general, it is not possible to restore a file except with the same version of the program as the one which SAVEd it.
 * __W-12028__   __*problem already has augmented SLP structure*__
   This message is produced by `XSLPconstruct` if it is called for a second time for the same problem. The problem can only be augmented once, which must be done after all the variables and coefficients have been loaded. `XSLPconstruct` is called automatically by `XSLPmaxim` and `XSLPminim` if it has not been called earlier.
 * __E-12029__   __*zero divisor*__
   This message is produced by the formula evaluation routines if an attempt is made to divide by a value less than `XSLP_ZERO`. A value of +/- `XSLP_INFINITY` is returned as the result and the calculation continues.
 * __E-12030__   __*negative number, fractional exponent - truncated to integer*__
   This message is produced by the formula evaluation routines if an attempt is made to raise a negative number to a non-integer exponent. The exponent is truncated to an integer value and the calculation continues.
 * __E-12031__   __*binary search failed*__
   This is a non-recoverable program error. If this error is encountered, please contact your local Xpress support office.
 * __E-12032__   __*wrong number \( `num`\) of arguments to function `func`*__
   This message is produced by the formula evaluation routines if a formula contains the wrong number of arguments for an internal function \(for example, _SIN(A,B)_ \). Correct the formula.
 * __E-12033__   __*argument `value`out of range in function `func`*__
   This message is produced by the formula evaluation routines if an internal function is called with an argument outside the allowable range \(for example, `LOG` of a negative number\). The function will normally return zero as the result and, if `XSLP_STOPOUTOFRANGE` is set, will set the function error flag.
 * __W-12034__   __*terminated following user return code `num`*__
   This message is produced by `XSLPmaxim` and `XSLPminim` if a nonzero value is returned by the callback defined by `XSLPsetcbiterend` or `XSLPsetcbslpend`.
 * __E-12037__   __*failed to load library/file/program " `name`" containing function " `func`"*__
   This message is produced if a user function is defined to be in a file, but Xpress NonLinear cannot the specified file. Check that the correct file name is specified \(also check the search paths such as$ PATH and% path% if necessary\).
   *  This message may also be produced if the specified library exists but is dependent on another library which is missing.
 * __E-12038__   __*function " `func`" is not correctly defined or is not in the specified location*__
   This message is produced if a user function is defined to be in a file, but Xpress NonLinear cannot find it in the file. Check that the number and type of the arguments is correct, and that the \(external\) name of the user function matches the name by which it is known in the file.
 * __E-12084__   __*Xpress NonLinear has not been initialized*__
   An attempt has been made to use Xpress NonLinear functions without a previous call to `XSLPinit`. Only a very few functions can be called before initialization. Check the sequence of calls to ensure that `XSLPinit` is called first, and that it completed successfully. _This error message normally produces return code 279._
 * __E-12085__   __*Xpress NonLinear has not been licensed for use here*__
   Either Xpress NonLinear is not licensed at all \(although the Xpress Optimizer may be licensed\), or the particular feature \(such as MISLP\) is not licensed. Check the license and contact the local Fair Isaac sales office if necessary. _This error message normally produces return code 352_.
 * __E-12105__   __*Xpress NonLinear error: I/O error on `file`*__
   The message is produced by `XSLPsave` or `XSLPwriteprob` if there is an I/O error when writing the output file \(usually because there is insufficient space to write the file\).
 * __E-12107__   __*Xpress NonLinear error: user function type `name`not supported on this platform*__
   This message is produced if a user function defined as being of type _XLS_, _XLF_ or _COM_ and is run on a non-Windows platform.
 * __E-12110__   __*Xpress NonLinear error: unidentified section in REVISE: `name`*__
   The file provided to XSLPrevise contains an unsupported MPS section.
 * __E-12111__   __*Xpress NonLinear error: unidentified row type in REVISE: `name`*__
   The file provided to XSLPrevise contains an unsupported row type.
 * __E-12112__   __*Xpress NonLinear error: unidentified row in REVISE: `name`*__
   The file provided to XSLPrevise contains a row name not found in the current problem.
 * __E-12113__   __*Xpress NonLinear error: unidentified bound in REVISE: `name`*__
   The file provided to XSLPrevise contains an unsupported bound type.
 * __E-12114__   __*Xpress NonLinear error: unidentified column in REVISE: `name`*__
   The file provided to XSLPrevise contains a column name not found in the current problem.
 * __E-12121__   __*Xpress NonLinear error: bad return code `num`from user function `func`*__
   This message is produced during evaluation of a complicated user function if it returns a value \(-1\) indicating that the system should estimate the result from a previous function call, but there has been no previous function call.
 * __E-12124__   __*Xpress NonLinear error: augmented problem not set up*__
   The message is produced by `XSLPvalidate` if an attempt is made to validate the problem without a preceding call to `XSLPconstruct`. In fact, unless a solution to the linearized problem is available, `XSLPvalidate` will not be able to give useful results.
 * __E-12125__   __*Xpress NonLinear error: user function `func`terminated with errors*__
   This message is produced during evaluation of a user function if it sets the function error flag \(see `XSLPsetfunctionerror`\).
 * __W-12142__   __*Xpress NonLinear warning: invalid record: `text`*__
   This error is produced by `XSLPreadprob` if it encounters a record in the file which is identifiable but invalid \(for example, a _BOUNDS_ record without a bound set name\). The record is ignored.
 * __E-12147__   __*Xpress NonLinear error: incompatible arguments in user function `func`*__
   This message is produced if a user function is called without providing the arguments required by the function.
 * __E-12151__   __*Xpress NonLinear error: `column`is not defined for formula in row*__
   This error is produced when an mps file has an incomplete or incorrect record for a nonlinear formula.
 * __E-12156__   __*Xpress NonLinear error: invalid double value*__
   This error is produced when a string value that was expected to represent a double does not.
 * __E-12157__   __*Xpress NonLinear error: invalid integer value*__
   This error is produced when a string value that was expected to represent an integer does not.
 * __E-12150__   __*Xpress NonLinear error: problem contains undefined user functions*__
   This error is produced if an mps or lp file is read that contains user functions that are later not defined before optimization.
 * __E-12158__   __*Xpress NonLinear error: unknown parameter name `name`*__
   This message is produced if an attempt is made to set or retrieve a value for a control parameter or attribute given by name where the name is incorrect.
 * __E-12159__   __*Xpress NonLinear error: unknown parameter type `name`*__
   A parameter has an unexpected type and cannot be retrieved. This is an internal error, please contanct FICO support.
 * __E-12159__   __*Xpress NonLinear error: parameter `number`is not writable*__
   This message is produced if an attempt is made to set a value for an attribute.
 * __E-12160__   __*Xpress NonLinear error: parameter `num`is not available*__
   This message is produced if an attempt is made to retrieve a value for a control or attribute which is not readable
 * __E-12161__   __*Xpress NonLinear error: parameter `num`is not available*__
   The parameter corresponding to the provided ID is aninternal, not readable parameter.
 * __E-12163__   __*Xpress NonLinear error: PWL functions can only take constant values following the determining variable: PWL\(x, base1, value1, ..., basek, valuek\)*__
   The values following the variable in a piecewise linear function \(PWL\) describe the breakpoints of the PWL, and so can only be constants.
 * __E-12164__   __*Xpress NonLinear error: PWL functions must take an odd number of arguments: PWL\(x, base1, value1, ..., basek, valuek\)*__
   The values following the variable in a piecewise linear function \(PWL\) describe the breakpoints of the PWL in pairs, making the total number of arguments odd.
 * __E-12165__   __*Xpress NonLinear error: PWL functions must take the following form: PWL\(x, base1, value1, ..., basek, valuek\)*__
   The piecewise linear function \(PWL\) defined is likely missing any break points, or has unexpected tokens.
 * __E-12166__   __*Xpress NonLinear error: PWL functions's first argument must be a variable: PWL\(x, base1, value1, ..., basek, valuek\)*__
   A piecewise linear function \(PWL\) argument list must start with the determining variable.
 * __E-12167__   __*Xpress NonLinear error: The base points of a PWL function must be monotonically increasing*__
   A piecewise linear function \(PWL\) must list its breakpoints first values in monotonically increasing order.
 * __E-12168__   __*Xpress NonLinear error: NLP with general constraints and piecewise linear not allowed with presolve off*__
   A model with general constraints and piecewise linear functions depends on presolve for reformulation.
 * __E-12169__   __*Xpress NonLinear error: error removing columns in unconstruct*__
   A call to unconstruct failed to remove columns added by construct. This is an unexpected error, please contact FICO support.
 * __E-12170__   __*Xpress NonLinear error: error removing rows in unconstruct*__
   A call to unconstruct failed to remove rows added by construct. This is an unexpected error, please contact FICO support.
 * __E-12171__   __*Xpress NonLinear error: compute server returned an error*__
   An error occured while solving remotely using a compute server.
 * __E-12173__   __*Xpress NonLinear error: Multistart is not supported in compute mode*__
   Multistart is currently not supported in compute mode.
 * __E-12174__   __*Xpress NonLinear error: User functions with named arguments are no longer supported*__
   User functions with named input and output arguments are no longer supported in the C API.
 * __E-12192__   __*Xpress NonLinear error: no problem or solution read*__
   No problem or solution has been read. If a problem read fails, it is not valid to continue with any problem building or solving functions.
 * __E-12193__   __*Xpress NonLinear error: this version of SLP requires XPRS version `num`or newer*__
   Altough not recommended, Xpress SLP can work with different xprs library versions. This error is issued when a tool old xpres library is found.
 * __E-12194__   __*Xpress NonLinear error: provided buffer is too short*__
   The provided buffer is too short. This error may occur if a formula is retrieved from Xpress, into a buffer that is not large enough.
 * __E-12195__   __*Xpress NonLinear error: `type`index `value`is invalid*__
   The index provided is not valid for the this type.
 * __E-12196__   __*Xpress NonLinear error: error in problem transformation*__
   An error occurred while the problem was attempted to be reformulated as part of the nonlinear presolver. Please contact FICO support.
 * __E-12197__   __*Xpress NonLinear error: `request` `index` `invalid`*__
   The requested information cannot be retrieved as it is not valid or not availanble.
 * __E-12198__   __*Xpress NonLinear error: error while cascading. Cannot evaluate coefficient at row _rowname_column.*__
   Evaluating an expression in cascading has returned an error. There is likely a user function in the expression returning an error.
 * __E-12199__   __*Xpress NonLinear error: nonlinear coefficient in neutral objective row ' _rowname_'. Please use an objective transfer row instead.*__
   A nonlinear objective function in SLP needs to be modelled using an objective transfer row.
 * __E-12200__   __*Xpress NonLinear error: problem is not augmented.*__
   The operation is only valid for augmented problems. Please call the construct method first, or solve using SLP.
 * __E-12201__   __*Xpress NonLinear error: an internal error has occured.*__
   An internal error has occured that is not expected to have been caused by incorrect input. Please contact FICO support.
 * __E-12202__   __*Xpress NonLinear error: attribute `i`cannot be changed.*__
   Attributes normally cannot be changed, as they are set up by the solver. There are a few exceptions to this rule, the requested attribute is not among the exceptions.
 * __E-12203__   __*Xpress NonLinear error: no problem or solution written.*__
   No problem or solution was written to disk due to an error processing the data.
 * __E-12204__   __*Xpress NonLinear error: Unexpected token `name`in formula.*__
   An unexpected token was encountered when parsing a string formula.
 * __E-12205__   __*Xpress NonLinear error: Duplicate user function names `name`are not allowed.*__
   A user function with this name was added twice. User function names have to be unique.
 * __E-12206__   __*Xpress NonLinear error: User function name `name`conflicts with an internal function name.*__
   The name of a user function conflicts with an internal function name \(sin, cos, ...\), it has to be different from all internal functions.
 * __E-12207__   __*Xpress NonLinear error: User function name `name`rejected: `reason`.*__
   A user function name was rejected due to invalid characters, for example whitespace, certain mathematical or control characters or due to starting with a digit.
 * __E-12208__   __*Xpress NonLinear error: cannot continue from current state. Consider disabling postsolve.*__
   The nonlinear solve could not be continued. A typical reason for this is that the problem was already postsolved.
 * __E-12209__   __*Xpress NonLinear error: bad flags `flag`.*__
   An invalid combination of flags was provided to a function.
 * __E-12210__   __*Xpress NonLinear error: `feature`is not supported in this release.*__
   This feature is not supported for global solves in the current release.

### Chapter 24 Xpress Knitro Control Parameters


This chapter provides a full list of the controls accepted by Xpress for setting Knitro parameters. Knitro has a great number and variety of user option settings and although it tries to choose the best settings by default, often significant performance improvements can be realized by choosing some non-default option settings.

_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XKTR_PARAM_ALGORITHM`, `KNITRO_PARAM_ALGORITHM` | Indicates which algorithm to use to solve nonlinear problems | Knitro, Solution Process
`XKTR_PARAM_BAR_DIRECTINTERVAL`, `KNITRO_PARAM_BAR_DIRECTINTERVAL` | Controls the maximum number of consecutive conjugate gradient \(CG\) steps before Knitro will try to enforce that a step is taken using direct linear algebra. | Knitro, Limits
`XKTR_PARAM_BAR_FEASIBLE`, `KNITRO_PARAM_BAR_FEASIBLE` | Specifies whether special emphasis is placed on getting and staying feasible in the interior-point algorithms. | Knitro
`XKTR_PARAM_BAR_FEASMODETOL`, `KNITRO_PARAM_BAR_FEASMODETOL` | Specifies the tolerance in equation that determines whether Knitro will force subsequent iterates to remain feasible. | Knitro, Tolerances
`XKTR_PARAM_BAR_INITMU`, `KNITRO_PARAM_BAR_INITMU` | Specifies the initial value for the barrier parameter : _μ_  used with the barrier algorithms. | Knitro
`XKTR_PARAM_BAR_INITPT`, `KNITRO_PARAM_BAR_INITPT` | Indicates whether an initial point strategy is used with barrier algorithms. | Knitro
`XKTR_PARAM_BAR_MAXBACKTRACK`, `KNITRO_PARAM_BAR_MAXBACKTRACK` | Indicates the maximum allowable number of backtracks during the linesearch of the Interior/Direct algorithm before reverting to a CG step. | Knitro, Limits
`XKTR_PARAM_BAR_MAXCROSSIT`, `KNITRO_PARAM_BAR_MAXCROSSIT` | Specifies the maximum number of crossover iterations before termination. | Knitro, Limits
`XKTR_PARAM_BAR_MAXREFACTOR`, `KNITRO_PARAM_BAR_MAXREFACTOR` | Indicates the maximum number of refactorizations of the KKT system per iteration of the Interior/Direct algorithm before reverting to a CG step. | Knitro, Limits
`XKTR_PARAM_BAR_MURULE`, `KNITRO_PARAM_BAR_MURULE` | Indicates which strategy to use for modifying the barrier parameter mu in the barrier algorithms. | Knitro
`XKTR_PARAM_BAR_PENCONS`, `KNITRO_PARAM_BAR_PENCONS` | Indicates whether a penalty approach is applied to the constraints. | Knitro
`XKTR_PARAM_BAR_PENRULE`, `KNITRO_PARAM_BAR_PENRULE` | Indicates which penalty parameter strategy to use for determining whether or not to accept a trial iterate. | Knitro
`XKTR_PARAM_BAR_SWITCHRULE`, `KNITRO_PARAM_BAR_SWITCHRULE` | Indicates whether or not the barrier algorithms will allow switching from an optimality phase to a pure feasibility phase. | Knitro
`XKTR_PARAM_DELTA`, `KNITRO_PARAM_DELTA` | Specifies the initial trust region radius scaling factor used to determine the initial trust region size. | Knitro
`XKTR_PARAM_FEASTOL`, `KNITRO_PARAM_FEASTOL` | Specifies the final relative stopping tolerance for the feasibility error. | Knitro, Tolerances
`XKTR_PARAM_FEASTOLABS`, `KNITRO_PARAM_FEASTOLABS` | Specifies the final absolute stopping tolerance for the feasibility error. | Knitro, Tolerances
`XKTR_PARAM_GRADOPT`, `KNITRO_PARAM_GRADOPT` | Specifies how to compute the gradients of the objective and constraint functions. | Derivatives, Knitro
`XKTR_PARAM_HESSOPT`, `KNITRO_PARAM_HESSOPT` | Specifies how to compute the \(approximate\) Hessian of the Lagrangian. | Derivatives, Knitro
`XKTR_PARAM_HONORBNDS`, `KNITRO_PARAM_HONORBNDS` | Indicates whether or not to enforce satisfaction of simple variable bounds throughout the optimization. | Knitro
`XKTR_PARAM_INFEASTOL`, `KNITRO_PARAM_INFEASTOL` | Specifies the \(relative\) tolerance used for declaring infeasibility of a model. | Knitro, Tolerances
`XKTR_PARAM_LMSIZE`, `KNITRO_PARAM_LMSIZE` | Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option. | Knitro, Limits
`XKTR_PARAM_MAXCGIT`, `KNITRO_PARAM_MAXCGIT` | Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option. | Knitro, Limits
`XKTR_PARAM_MAXIT`, `KNITRO_PARAM_MAXIT` | Specifies the maximum number of iterations before termination. | Knitro, Limits
`XKTR_PARAM_MIP_BRANCHRULE`, `KNITRO_PARAM_MIP_BRANCHRULE` | Specifies which branching rule to use for MIP branch and bound procedure. | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_GUB_BRANCH`, `KNITRO_PARAM_MIP_GUB_BRANCH` | Specifies whether or not to branch on generalized upper bounds \(GUBs\). | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_HEURISTIC`, `KNITRO_PARAM_MIP_HEURISTIC` | Specifies which MIP heuristic search approach to apply to try to find an initial integer feasible point. | Heuristics, Knitro-MINLP
`XKTR_PARAM_MIP_HEURISTIC_MAXIT`, `KNITRO_PARAM_MIP_HEURISTIC_MAXIT` | Specifies the maximum number of iterations to allow for MIP heuristic, if one is enabled. | Heuristics, Knitro-MINLP
`XKTR_PARAM_MIP_IMPLICATNS`, `KNITRO_PARAM_MIP_IMPLICATNS` | Specifies whether or not to add constraints to the MIP derived from logical implications. | Knitro-MINLP, Presolve
`XKTR_PARAM_MIP_INTEGERTOL`, `KNITRO_PARAM_INTEGERTOL` | This value specifies the threshold for deciding whether or not a variable is determined to be an integer. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPABS`, `KNITRO_PARAM_INTGAPABS` | The absolute integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_INTGAPREL`, `KNITRO_PARAM_INTGAPREL` | The relative integrality gap stop tolerance for MIP. | Knitro, Knitro-MINLP, Tolerances
`XKTR_PARAM_MIP_KNAPSACK`, `KNITRO_PARAM_MIP_KNAPSACK` | Specifies rules for adding MIP knapsack cuts. | Cuts, Knitro-MINLP
`XKTR_PARAM_MIP_LPALG`, `KNITRO_PARAM_MIP_LPALG` | Specifies which algorithm to use for any linear programming \(LP\) subproblem solves that may occur in the MIP branch and bound procedure. | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_MAXNODES`, `KNITRO_PARAM_MIP_MAXNODES` | Specifies the maximum number of nodes explored. | Knitro-MINLP, Limits
`XKTR_PARAM_MIP_MAXSOLVES`, `KNITRO_PARAM_MIP_MAXSOLVES` | Specifies the maximum number of subproblem solves allowed \(0 means no limit\). | Knitro-MINLP, Limits
`XKTR_PARAM_MIP_METHOD`, `KNITRO_PARAM_MIP_METHOD` | Specifies which MIP method to use. | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_OUTINTERVAL`, `KNITRO_PARAM_MIP_OUTINTERVAL` | Specifies node printing interval for `XKTR_PARAM_MIP_OUTLEVEL` when `XKTR_PARAM_MIP_OUTLEVEL` > 0. | Knitro-MINLP, Logging
`XKTR_PARAM_MIP_OUTLEVEL`, `KNITRO_PARAM_MIP_OUTLEVEL` | Specifies how much MIP information to print. | Knitro-MINLP, Logging
`XKTR_PARAM_MIP_PSEUDOINIT`, `KNITRO_PARAM_MIP_PSEUDOINIT` | Specifies the method used to initialize pseudo-costs corresponding to variables that have not yet been branched on in the MIP method. | Branching, Knitro-MINLP
`XKTR_PARAM_MIP_ROOTALG`, `KNITRO_PARAM_MIP_ROOTALG` | Specifies which algorithm to use for the root node solve in MIP \(same options as `XKTR_PARAM_ALGORITHM` user option\). | Knitro-MINLP, Solution Process
`XKTR_PARAM_MIP_ROUNDING`, `KNITRO_PARAM_MIP_ROUNDING` | Specifies the MIP rounding rule to apply. | Knitro-MINLP
`XKTR_PARAM_MIP_SELECTRULE`, `KNITRO_PARAM_MIP_SELECTRULE` | Specifies the MIP select rule for choosing the next node in the branch and bound tree. | Knitro-MINLP
`XKTR_PARAM_MIP_STRONG_CANDLIM`, `KNITRO_PARAM_MIP_STRONG_CANDLIM` | Specifies the maximum number of candidates to explore for MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_LEVEL`, `KNITRO_PARAM_MIP_STRONG_LEVEL` | Specifies the maximum number of tree levels on which to perform MIP strong branching. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_STRONG_MAXIT`, `KNITRO_PARAM_MIP_STRONG_MAXIT` | Specifies the maximum number of iterations to allow for MIP strong branching solves. | Branching, Knitro-MINLP, Limits
`XKTR_PARAM_MIP_TERMINATE`, `KNITRO_PARAM_MIP_TERMINATE` | Specifies conditions for terminating the MIP algorithm. | Knitro-MINLP
`XKTR_PARAM_OBJRANGE`, `KNITRO_PARAM_OBJRANGE` | Specifies the extreme limits of the objective function for purposes of determining unboundedness. | Knitro, Limits
`XKTR_PARAM_OPTTOL`, `KNITRO_PARAM_OPTTOL` | Specifies the final relative stopping tolerance for the KKT \(optimality\) error. | Knitro, Tolerances
`XKTR_PARAM_OPTTOLABS`, `KNITRO_PARAM_OPTTOLABS` | Specifies the final absolute stopping tolerance for the KKT \(optimality\) error. | Knitro, Tolerances
`XKTR_PARAM_OUTLEV`, `KNITRO_PARAM_OUTLEV` | Controls the level of output produced by Knitro. | Knitro, Logging
`XKTR_PARAM_PRESOLVE`, `KNITRO_PARAM_PRESOLVE` | Determine whether or not to use the Knitro presolver to try to simplify the model by removing variables or constraints. | Knitro, Presolve
`XKTR_PARAM_PRESOLVE_TOL`, `KNITRO_PARAM_PRESOLVE_TOL` | Determines the tolerance used by the Knitro presolver to remove variables and constraints from the model. | Knitro, Presolve, Tolerances
`XKTR_PARAM_SCALE`, `KNITRO_PARAM_SCALE` | Performs a scaling of the objective and constraint functions based on their values at the initial point. | Knitro, Numerics
`XKTR_PARAM_SOC`, `KNITRO_PARAM_SOC` | Specifies whether or not to try second order corrections \(SOC\). | Knitro
`XKTR_PARAM_SOLTYPE`, `KNITRO_PARAM_SOLTYPE` | This option specifies the solution returned by Knitro. | Knitro
`XKTR_PARAM_XTOL`, `KNITRO_PARAM_XTOL` | The optimization process will terminate if the relative change in all components of the solution point estimate is less than xtol. | Knitro, Tolerances

#### Section 24.1 Double control parameters


These double control parameters can be set using XSLPsetdblcontrol using the Xpress NonLinear API, XNLPsetsolverdoublecontrol using the XNLP API and setparam in Mosel using module mmxnlp.

#### XKTR_PARAM_BAR_FEASMODETOL, KNITRO_PARAM_BAR_FEASMODETOL

_**Description:**_    Specifies the tolerance in equation that determines whether Knitro will force subsequent iterates to remain feasible.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 1.0e-4

_**Note:**_
The tolerance applies to all inequality constraints in the problem. This option only has an effect if option `XKTR_PARAM_BAR_FEASIBLE` = stay or `XKTR_PARAM_BAR_FEASIBLE` = get\_stay.
_**Category:**_ Control

#### XKTR_PARAM_BAR_INITMU, KNITRO_PARAM_BAR_INITMU

_**Description:**_    Specifies the initial value for the barrier parameter : _μ_ used with the barrier algorithms. This option has no effect on the Active Set algorithm.
 
_**Type:**_ Double

_**Topic area:**_ 
Knitro

_**Default value:**_ 1.0e-1
_**Category:**_ Control

#### XKTR_PARAM_DELTA, KNITRO_PARAM_DELTA

_**Description:**_    Specifies the initial trust region radius scaling factor used to determine the initial trust region size.
 
_**Type:**_ Double

_**Topic area:**_ 
Knitro

_**Default value:**_ 1.0e0
_**Category:**_ Control

#### XKTR_PARAM_FEASTOL, KNITRO_PARAM_FEASTOL

_**Description:**_    Specifies the final relative stopping tolerance for the feasibility error.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 1.0e-6

_**Note:**_
Smaller values of feastol result in a higher degree of accuracy in the solution with respect to feasibility.
_**Category:**_ Control

#### XKTR_PARAM_FEASTOLABS, KNITRO_PARAM_FEASTOLABS

_**Description:**_    Specifies the final absolute stopping tolerance for the feasibility error.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 0.0e0

_**Note:**_
Smaller values of feastol\_abs result in a higher degree of accuracy in the solution with respect to feasibility.
_**Category:**_ Control

#### XKTR_PARAM_INFEASTOL, KNITRO_PARAM_INFEASTOL

_**Description:**_    Specifies the \(relative\) tolerance used for declaring infeasibility of a model.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 1.0e-8

_**Note:**_
Smaller values of infeastol make it more difficult to satisfy the conditions Knitro uses for detecting infeasible models. If you believe Knitro incorrectly declares a model to be infeasible, then you should try a smaller value for infeastol.
_**Category:**_ Control

#### XKTR_PARAM_MIP_INTEGERTOL, KNITRO_PARAM_INTEGERTOL

_**Description:**_    This value specifies the threshold for deciding whether or not a variable is determined to be an integer.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Knitro-MINLP, Tolerances

_**Default value:**_ 1.0e-8
_**Category:**_ Control

#### XKTR_PARAM_MIP_INTGAPABS, KNITRO_PARAM_INTGAPABS

_**Description:**_    The absolute integrality gap stop tolerance for MIP.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Knitro-MINLP, Tolerances

_**Default value:**_ 1.0e-6
_**Category:**_ Control

#### XKTR_PARAM_MIP_INTGAPREL, KNITRO_PARAM_INTGAPREL

_**Description:**_    The relative integrality gap stop tolerance for MIP.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Knitro-MINLP, Tolerances

_**Default value:**_ 1.0e-6
_**Category:**_ Control

#### XKTR_PARAM_OBJRANGE, KNITRO_PARAM_OBJRANGE

_**Description:**_    Specifies the extreme limits of the objective function for purposes of determining unboundedness.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Limits

_**Default value:**_ 1.0e20

_**Note:**_
If the magnitude of the objective function becomes greater than objrange for a feasible iterate, then the problem is determined to be unbounded and Knitro proceeds no further.
_**Category:**_ Control

#### XKTR_PARAM_OPTTOL, KNITRO_PARAM_OPTTOL

_**Description:**_    Specifies the final relative stopping tolerance for the KKT \(optimality\) error.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 1.0e-6

_**Note:**_
Smaller values of opttol result in a higher degree of accuracy in the solution with respect to optimality.
_**Category:**_ Control

#### XKTR_PARAM_OPTTOLABS, KNITRO_PARAM_OPTTOLABS

_**Description:**_    Specifies the final absolute stopping tolerance for the KKT \(optimality\) error.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 0.0e0

_**Note:**_
Smaller values of opttol\_abs result in a higher degree of accuracy in the solution with respect to optimality.
_**Category:**_ Control

#### XKTR_PARAM_PRESOLVE_TOL, KNITRO_PARAM_PRESOLVE_TOL

_**Description:**_    Determines the tolerance used by the Knitro presolver to remove variables and constraints from the model.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Presolve, Tolerances

_**Default value:**_ 1.0e-6

_**Note:**_
If you believe the Knitro presolver is incorrectly modifying the model, use a smaller value for this tolerance \(or turn the presolver off\).
_**Category:**_ Control

#### XKTR_PARAM_XTOL, KNITRO_PARAM_XTOL

_**Description:**_    The optimization process will terminate if the relative change in all components of the solution point estimate is less than xtol.
 
_**Type:**_ Double

_**Topic areas:**_ 
Knitro, Tolerances

_**Default value:**_ 1.0e-15

_**Note:**_
If using the Interior/Direct or Interior/CG algorithm and the barrier parameter is still large, Knitro will first try decreasing the barrier parameter before terminating.
_**Category:**_ Control

#### Section 24.2 Integer control parameters


These integer control parameters can be set using XSLPsetintcontrol using the Xpress NonLinear API, XNLPsetsolverintcontrol using the XNLP API and setparam in Mosel using module mmxnlp.

#### XKTR_PARAM_ALGORITHM, KNITRO_PARAM_ALGORITHM

_**Description:**_    Indicates which algorithm to use to solve nonlinear problems
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) let Knitro automatically choose an algorithm, based on the problem characteristics.
 `1`| \(direct\) use the Interior/Direct algorithm.
 `2`| \(cg\) use the Interior/CG algorithm.
 `3`| \(active\) use the Active Set algorithm.
 `4`| \(sqp\) use the SQP algorithm.
 `5`| \(multi\) run all algorithms, perhaps in parallel.
 `6`| \(al\) use the Augmented Lagrangian algorithm.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_BAR_DIRECTINTERVAL, KNITRO_PARAM_BAR_DIRECTINTERVAL

_**Description:**_    Controls the maximum number of consecutive conjugate gradient \(CG\) steps before Knitro will try to enforce that a step is taken using direct linear algebra.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Default value:**_ 10

_**Note:**_
This option is only valid for the Interior/Direct algorithm and may be useful on problems where Knitro appears to be taking lots of conjugate gradient steps. Setting bar\_directinterval to 0 will try to enforce that only direct steps are taken which may produce better results on some problems.
_**Category:**_ Control

#### XKTR_PARAM_BAR_FEASIBLE, KNITRO_PARAM_BAR_FEASIBLE

_**Description:**_    Specifies whether special emphasis is placed on getting and staying feasible in the interior-point algorithms.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(no\) No special emphasis on feasibility.
 `1`| \(stay\) Iterates must satisfy inequality constraints once they become sufficiently feasible.
 `2`| \(get\) Special emphasis is placed on getting feasible before trying to optimize.
 `3`| \(get\_stay\) Implement both options 1 and 2 above.

_**Default value:**_ 0

_**Note:**_
This option can only be used with the Interior/Direct and Interior/CG algorithms. If bar\_feasible = stay or bar\_feasible = get\_stay, this will activate the feasible version of Knitro. The feasible version of Knitro will force iterates to strictly satisfy inequalities, but does not require satisfaction of equality constraints at intermediate iterates. This option and the honorbnds option may be useful in applications where functions are undefined outside the region defined by inequalities. The initial point must satisfy inequalities to a sufficient degree; if not, Knitro may generate infeasible iterates and does not switch to the feasible version until a sufficiently feasible point is found. Sufficient satisfaction occurs at a point x if it is true for all inequalities that cl + tol _≤_  c\(x\) _≤_  cu - tol The constant tol is determined by the option bar\_feasmodetol. If bar\_feasible = get or bar\_feasible = get\_stay, Knitro will place special emphasis on first trying to get feasible before trying to optimize.
_**Category:**_ Control

#### XKTR_PARAM_BAR_INITPT, KNITRO_PARAM_BAR_INITPT

_**Description:**_    Indicates whether an initial point strategy is used with barrier algorithms.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose the strategy.
 `1`| \(yes\) Shift the initial slacks and multipliers to improve barrier algorithm performance.
 `2`| \(no\) Do no alter the initial slacks and multipliers.

_**Default value:**_ 0

_**Note:**_
This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_BAR_MAXBACKTRACK, KNITRO_PARAM_BAR_MAXBACKTRACK

_**Description:**_    Indicates the maximum allowable number of backtracks during the linesearch of the Interior/Direct algorithm before reverting to a CG step.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Default value:**_ 3

_**Note:**_
Increasing this value will make the Interior/Direct algorithm less likely to take CG steps. If the Interior/Direct algorithm is taking a large number of CG steps \(as indicated by a positive value for 'Gits' in the output\), this may improve performance. This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_BAR_MAXCROSSIT, KNITRO_PARAM_BAR_MAXCROSSIT

_**Description:**_    Specifies the maximum number of crossover iterations before termination.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Default value:**_ 0

_**Note:**_
If the value is positive and the algorithm in operation is Interior/Direct or Interior/CG, then Knitro will crossover to the Active Set algorithm near the solution. The Active Set algorithm will then perform at most bar\_maxcrossit iterations to get a more exact solution. If the value is 0, no Active Set crossover occurs and the interior-point solution is the final result. If Active Set crossover is unable to improve the approximate interior-point solution, then Knitro will restore the interior-point solution. In some cases \(especially on large-scale problems or difficult degenerate problems\) the cost of the crossover procedure may be significant - for this reason, crossover is disabled by default. Enabling crossover generally provides a more accurate solution than Interior/Direct or Interior/CG.
_**Category:**_ Control

#### XKTR_PARAM_BAR_MAXREFACTOR, KNITRO_PARAM_BAR_MAXREFACTOR

_**Description:**_    Indicates the maximum number of refactorizations of the KKT system per iteration of the Interior/Direct algorithm before reverting to a CG step.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Default value:**_ -1

_**Note:**_
These refactorizations are performed if negative curvature is detected in the model. Rather than reverting to a CG step, the Hessian matrix is modified in an attempt to make the subproblem convex and then the KKT system is refactorized. Increasing this value will make the Interior/Direct algorithm less likely to take CG steps. If the Interior/Direct algorithm is taking a large number of CG steps \(as indicated by a positive value for "CGits" in the output\), this may improve performance. This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_BAR_MURULE, KNITRO_PARAM_BAR_MURULE

_**Description:**_    Indicates which strategy to use for modifying the barrier parameter mu in the barrier algorithms.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose the strategy.
 `1`| \(monotone\) Monotonically decrease the barrier parameter. Available for both barrier algorithms.
 `2`| \(adaptive\) Use an adaptive rule based on the complementarity gap to determine the value of the barrier parameter. Available for both barrier algorithms.
 `3`| \(probing\) Use a probing \(affine-scaling\) step to dynamically determine the barrier parameter. Available only for the Interior/Direct algorithm.
 `4`| \(dampmpc\) Use a Mehrotra predictor-corrector type rule to determine the barrier parameter, with safeguards on the corrector step. Available only for the Interior/Direct algorithm.
 `5`| \(fullmpc\) Use a Mehrotra predictor-corrector type rule to determine the barrier parameter, without safeguards on the corrector step. Available only for the Interior/Direct algorithm.
 `6`| \(quality\) Minimize a quality function at each iteration to determine the barrier parameter. Available only for the Interior/Direct algorithm.

_**Default value:**_ 0

_**Note:**_
Not all strategies are available for both barrier algorithms. This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_BAR_PENCONS, KNITRO_PARAM_BAR_PENCONS

_**Description:**_    Indicates whether a penalty approach is applied to the constraints.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose the strategy.
 `1`| \(none\) No constraints are penalized.
 `2`| \(all\) A penalty approach is applied to all general constraints.

_**Default value:**_ 0

_**Note:**_
Using a penalty approach may be helpful when the problem has degenerate or difficult constraints. It may also help to more quickly identify infeasible problems, or achieve feasibility in problems with difficult constraints. This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_BAR_PENRULE, KNITRO_PARAM_BAR_PENRULE

_**Description:**_    Indicates which penalty parameter strategy to use for determining whether or not to accept a trial iterate.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose the strategy.
 `1`| \(single\) Use a single penalty parameter in the merit function to weight feasibility versus optimality.
 `2`| \(flex\) Use a more tolerant and flexible step acceptance procedure based on a range of penalty parameter values.

_**Default value:**_ 0

_**Note:**_
This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_BAR_SWITCHRULE, KNITRO_PARAM_BAR_SWITCHRULE

_**Description:**_    Indicates whether or not the barrier algorithms will allow switching from an optimality phase to a pure feasibility phase.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro determine the switching procedure.
 `1`| \(never\) Never switch to feasibility phase.
 `2`| \(level1\) Allow switches to feasibility phase.
 `3`| \(level2\) Use a more aggressive switching rule.

_**Default value:**_ 0

_**Note:**_
This option has no effect on the Active Set algorithm.
_**Category:**_ Control

#### XKTR_PARAM_GRADOPT, KNITRO_PARAM_GRADOPT

_**Description:**_    Specifies how to compute the gradients of the objective and constraint functions.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Derivatives

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `1`| \(exact\) User provides a routine for computing the exact gradients.
 `2`| \(forward\) Knitro computes gradients by forward finite-differences.
 `3`| \(central\) Knitro computes gradients by central finite differences.

_**Default value:**_ 1

_**Note:**_
It is highly recommended to provide exact gradients if at all possible as this greatly impacts the performance of the code.
_**Category:**_ Control

#### XKTR_PARAM_HESSOPT, KNITRO_PARAM_HESSOPT

_**Description:**_    Specifies how to compute the \(approximate\) Hessian of the Lagrangian.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Derivatives

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro make an automatic choice.
 `1`| \(exact\) User provides a routine for computing the exact Hessian.
 `2`| \(bfgs\) Knitro computes a \(dense\) quasi-Newton BFGS Hessian.
 `3`| \(sr1\) Knitro computes a \(dense\) quasi-Newton SR1 Hessian.
 `4`| \(finite\_diff\) Knitro computes Hessian-vector products using finite-differences.
 `5`| \(product\) User provides a routine to compute the Hessian-vector products.
 `6`| \(lbfgs\) Knitro computes a limited-memory quasi-Newton BFGS Hessian \(its size is determined by the option lmsize\).
 `7`| \(gauss\_newton\) Knitro computes a Gauss-Newton approximation of the hessian \(available for least-squares only, and default value for least-squares\)

_**Default value:**_ 0

_**Note:**_
Options hessopt = 4 and hessopt = 5 are not available with the Interior/Direct algorithm. Knitro usually performs best when the user provides exact Hessians \(hessopt = 1\) or exact Hessian-vector products \(hessopt = 5\). If neither can be provided but exact gradients are available \(i.e., gradopt = 1\), then hessopt = 4 is recommended. This option is comparable in terms of robustness to the exact Hessian option and typically not much slower in terms of time, provided that gradient evaluations are not a dominant cost. If exact gradients cannot be provided, then one of the quasi-Newton options is preferred. Options hessopt = 2 and hessopt = 3 are only recommended for small problems \(n _≤_  1000\) since they require working with a dense Hessian approximation. Option hessopt = 6 should be used for large problems.
_**Category:**_ Control

#### XKTR_PARAM_HONORBNDS, KNITRO_PARAM_HONORBNDS

_**Description:**_    Indicates whether or not to enforce satisfaction of simple variable bounds throughout the optimization.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(no\) Knitro does not require that the bounds on the variables be satisfied at intermediate iterates.
 `1`| \(always\) Knitro enforces that the initial point and all subsequent solution estimates satisfy the bounds on the variables.
 `2`| \(initpt\) Knitro enforces that the initial point satisfies the bounds on the variables.

_**Default value:**_ 2

_**Note:**_
This option and the bar\_feasible option may be useful in applications where functions are undefined outside the region defined by inequalities.
_**Category:**_ Control

#### XKTR_PARAM_LMSIZE, KNITRO_PARAM_LMSIZE

_**Description:**_    Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Default value:**_ 10

_**Note:**_
The value must be between 1 and 100 and is only used with `XKTR_PARAM_HESSOPT` = 6. Larger values may give a more accurate, but more expensive, Hessian approximation. Smaller values may give a less accurate, but faster, Hessian approximation. When using the limited memory BFGS approach it is recommended to experiment with different values of this parameter.
_**Category:**_ Control

#### XKTR_PARAM_MAXCGIT, KNITRO_PARAM_MAXCGIT

_**Description:**_    Specifies the number of limited memory pairs stored when approximating the Hessian using the limited-memory quasi-Newton BFGS option.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Let Knitro automatically choose a value based on the problem size.
 `n`| At most n>0 CG iterations may be performed during one minor iteration of Knitro.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MAXIT, KNITRO_PARAM_MAXIT

_**Description:**_    Specifies the maximum number of iterations before termination.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Limits

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Let Knitro automatically choose a value based on the problem type. Currently Knitro sets this value to 10000 for LPs/NLPs and 3000 for MIP problems.
 `n`| At most n>0 iterations may be performed before terminating.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_BRANCHRULE, KNITRO_PARAM_MIP_BRANCHRULE

_**Description:**_    Specifies which branching rule to use for MIP branch and bound procedure.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Branching

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose the branching rule.
 `1`| \(most\_frac\) Use most fractional \(most infeasible\) branching.
 `2`| \(pseudcost\) Use pseudo-cost branching.
 `3`| \(strong\) Use strong branching \(see options`XKTR_PARAM_MIP_STRONG_CANDLIM`,`XKTR_PARAM_MIP_STRONG_LEVEL`,`XKTR_PARAM_MIP_STRONG_MAXIT`for further control of strong branching procedure\).

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_GUB_BRANCH, KNITRO_PARAM_MIP_GUB_BRANCH

_**Description:**_    Specifies whether or not to branch on generalized upper bounds \(GUBs\).
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Branching

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(no\) Do not branch on GUBs.
 `1`| \(yes\) Allow branching on GUBs.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_HEURISTIC, KNITRO_PARAM_MIP_HEURISTIC

_**Description:**_    Specifies which MIP heuristic search approach to apply to try to find an initial integer feasible point.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Heuristics

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro choose the heuristic to apply \(if any\).
 `1`| \(none\) No heuristic search applied.
 `2`| \(feaspump\) Apply feasibility pump heuristic.
 `3`| \(mpec\) Apply heuristic based on MPEC formulation.

_**Default value:**_ 0

_**Note:**_
If a heuristic search procedure is enabled, it will run for at most mip\_heuristic\_maxit iterations, before starting the branch and bound procedure.
_**Category:**_ Control

#### XKTR_PARAM_MIP_HEURISTIC_MAXIT, KNITRO_PARAM_MIP_HEURISTIC_MAXIT

_**Description:**_    Specifies the maximum number of iterations to allow for MIP heuristic, if one is enabled.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Heuristics

_**Default value:**_ 100
_**Category:**_ Control

#### XKTR_PARAM_MIP_IMPLICATNS, KNITRO_PARAM_MIP_IMPLICATNS

_**Description:**_    Specifies whether or not to add constraints to the MIP derived from logical implications.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(no\) Do not add constraints from logical implications.
 `1`| \(yes\) Knitro adds constraints from logical implications.

_**Default value:**_ 1
_**Category:**_ Control

#### XKTR_PARAM_MIP_KNAPSACK, KNITRO_PARAM_MIP_KNAPSACK

_**Description:**_    Specifies rules for adding MIP knapsack cuts.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Cuts

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(none\) Do not add knapsack cuts.
 `1`| \(ineqs\) Add cuts derived from inequalities only.
 `2`| \(ineqs\_eqs\) Add cuts derived from both inequalities and equalities.

_**Default value:**_ 1
_**Category:**_ Control

#### XKTR_PARAM_MIP_LPALG, KNITRO_PARAM_MIP_LPALG

_**Description:**_    Specifies which algorithm to use for any linear programming \(LP\) subproblem solves that may occur in the MIP branch and bound procedure.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose an algorithm, based on the problem characteristics.
 `1`| \(direct\) Use the Interior/Direct \(barrier\) algorithm.
 `2`| \(cg\) Use the Interior/CG \(barrier\) algorithm.
 `3`| \(active\) Use the Active Set \(simplex\) algorithm.

_**Default value:**_ 0

_**Note:**_
LP subproblems may arise if the problem is a mixed integer linear program \(MILP\), or if using `XKTR_PARAM_MIP_METHOD` = HQG. \(Nonlinear programming subproblems use the algorithm specified by the algorithm option.\)
_**Category:**_ Control

#### XKTR_PARAM_MIP_MAXNODES, KNITRO_PARAM_MIP_MAXNODES

_**Description:**_    Specifies the maximum number of nodes explored.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Limits

_**Default value:**_ 100000

_**Note:**_
Zero vealue means no limit.
_**Category:**_ Control

#### XKTR_PARAM_MIP_MAXSOLVES, KNITRO_PARAM_MIP_MAXSOLVES

_**Description:**_    Specifies the maximum number of subproblem solves allowed \(0 means no limit\).
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Limits

_**Default value:**_ 200000
_**Category:**_ Control

#### XKTR_PARAM_MIP_METHOD, KNITRO_PARAM_MIP_METHOD

_**Description:**_    Specifies which MIP method to use.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Solution Process

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro automatically choose the method.
 `1`| \(BB\) Use the standard branch and bound method.
 `2`| \(HQG\) Use the hybrid Quesada-Grossman method \(for convex, nonlinear problems only\).

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_OUTINTERVAL, KNITRO_PARAM_MIP_OUTINTERVAL

_**Description:**_    Specifies node printing interval for`XKTR_PARAM_MIP_OUTLEVEL`when`XKTR_PARAM_MIP_OUTLEVEL`> 0.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Logging

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Print output every node.
 `2`| Print output every 2nd node.
 `N`| Print output every Nth node.

_**Default value:**_ 10
_**Category:**_ Control

#### XKTR_PARAM_MIP_OUTLEVEL, KNITRO_PARAM_MIP_OUTLEVEL

_**Description:**_    Specifies how much MIP information to print.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Logging

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(none\) Do not print any MIP node information.
 `1`| \(iters\) Print one line of output for every node.

_**Default value:**_ 1
_**Category:**_ Control

#### XKTR_PARAM_MIP_PSEUDOINIT, KNITRO_PARAM_MIP_PSEUDOINIT

_**Description:**_    Specifies the method used to initialize pseudo-costs corresponding to variables that have not yet been branched on in the MIP method.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Branching

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Let Knitro automatically choose the method.
 `1`| Initialize using the average value of computed pseudo-costs.
 `2`| Initialize using strong branching.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_ROOTALG, KNITRO_PARAM_MIP_ROOTALG

_**Description:**_    Specifies which algorithm to use for the root node solve in MIP \(same options as`XKTR_PARAM_ALGORITHM`user option\).
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Solution Process

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_ROUNDING, KNITRO_PARAM_MIP_ROUNDING

_**Description:**_    Specifies the MIP rounding rule to apply.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro-MINLP

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro choose the rounding rule.
 `1`| \(none\) Do not round if a node is infeasible.
 `2`| \(heur\_only\) Round using a fast heuristic only.
 `3`| \(nlp\_sometimes\) Round and solve a subproblem if likely to succeed.
 `4`| \(nlp\_always\) Always round and solve a subproblem.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_SELECTRULE, KNITRO_PARAM_MIP_SELECTRULE

_**Description:**_    Specifies the MIP select rule for choosing the next node in the branch and bound tree.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro-MINLP

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(auto\) Let Knitro choose the node selection rule.
 `1`| \(depth\_first\) Search the tree using a depth first procedure.
 `2`| \(best\_bound\) Select the node with the best relaxation bound.
 `3`| \(combo\_1\) Use depth first unless pruned, then best bound.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_MIP_STRONG_CANDLIM, KNITRO_PARAM_MIP_STRONG_CANDLIM

_**Description:**_    Specifies the maximum number of candidates to explore for MIP strong branching.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Branching, Limits

_**Default value:**_ 10
_**Category:**_ Control

#### XKTR_PARAM_MIP_STRONG_LEVEL, KNITRO_PARAM_MIP_STRONG_LEVEL

_**Description:**_    Specifies the maximum number of tree levels on which to perform MIP strong branching.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Branching, Limits

_**Default value:**_ 10
_**Category:**_ Control

#### XKTR_PARAM_MIP_STRONG_MAXIT, KNITRO_PARAM_MIP_STRONG_MAXIT

_**Description:**_    Specifies the maximum number of iterations to allow for MIP strong branching solves.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro-MINLP, Branching, Limits

_**Default value:**_ 1000
_**Category:**_ Control

#### XKTR_PARAM_MIP_TERMINATE, KNITRO_PARAM_MIP_TERMINATE

_**Description:**_    Specifies conditions for terminating the MIP algorithm.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro-MINLP

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(optimal\) Terminate at optimum.
 `1`| \(feasible\) Terminate at first integer feasible point.

_**Default value:**_ 0
_**Category:**_ Control

#### XKTR_PARAM_OUTLEV, KNITRO_PARAM_OUTLEV

_**Description:**_    Controls the level of output produced by Knitro.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Logging

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(none\) Printing of all output is suppressed.
 `1`| \(summary\) Print only summary information.
 `2`| \(iter\_10\) Print basic information every 10 iterations.
 `3`| \(iter\) Print basic information at each iteration.
 `4`| \(iter\_verbose\) Print basic information and the function count at each iteration.
 `5`| \(iter\_x\) Print all the above, and the values of the solution vector x.
 `6`| \(all\) Print all the above, and the values of the constraints c at x and the Lagrange multipliers lambda.

_**Default value:**_ 2
_**Category:**_ Control

#### XKTR_PARAM_PRESOLVE, KNITRO_PARAM_PRESOLVE

_**Description:**_    Determine whether or not to use the Knitro presolver to try to simplify the model by removing variables or constraints. Specifies conditions for terminating the MIP algorithm.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Presolve

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(none\) Do not use Knitro presolver.
 `1`| \(basic\) Use the Knitro basic presolver.

_**Default value:**_ 1
_**Category:**_ Control

#### XKTR_PARAM_SCALE, KNITRO_PARAM_SCALE

_**Description:**_    Performs a scaling of the objective and constraint functions based on their values at the initial point.
 
_**Type:**_ Integer

_**Topic areas:**_ 
Knitro, Numerics

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(no\) No scaling is performed.
 `1`| \(yes\) Knitro is allowed to scale the objective function and constraints.

_**Default value:**_ 1

_**Note:**_
If scaling is performed, all internal computations, including the stopping tests, are based on the scaled values.
_**Category:**_ Control

#### XKTR_PARAM_SOC, KNITRO_PARAM_SOC

_**Description:**_    Specifies whether or not to try second order corrections \(SOC\).
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(no\) No second order correction steps are attempted.
 `1`| \(maybe\) Second order correction steps may be attempted on some iterations.
 `2`| \(yes\) Second order correction steps are always attempted if the original step is rejected and there are nonlinear constraints.

_**Default value:**_ 1

_**Note:**_
A second order correction may be beneficial for problems with highly nonlinear constraints.
_**Category:**_ Control

#### XKTR_PARAM_SOLTYPE, KNITRO_PARAM_SOLTYPE

_**Description:**_    This option specifies the solution returned by Knitro. Generally, the solution converged to by Knitro is a locally optimal solution that corresponds to the best feasible solution found. However, on rare occasions, Knitro may enounter a feasible solution during the optimization process that has a better objective value than the final solution converged to by Knitro. Setting soltype = 1 in this case will return this iterate.
 
_**Type:**_ Integer

_**Topic area:**_ 
Knitro

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| \(final\) Always return the final solution to which Knitro converges.
 `1`| \(bestfeas\) Always return the best feasible solution encountered during the optimization.

_**Default value:**_ 0
_**Category:**_ Control

## Part D Appendix


### Chapter 25 The Xpress-SLP Log


The Xpress-SLP log consists of log lines of two different types: the output of the underlying XPRS optimizer, and the log of XSLP itself.

By default, messages produced by the nonlinear code are sent to the normal XPRS message callback as controlled by `XSLP_ECHOXPRSMESSAGES`. It may also be intercepted by a user function using the user output callback; see `XSLPsetcbmessage`. Users need to define a callback function and print messages to the screen themselves if they wish output to be displayed.

#### Logging controls


**General SLP logging** 



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XPRS_OUTPUTLOG` | Logging level of the underlying XPRS problem | 
`XPRS_LPLOG` | Logging frequency for solving the linearization | 
`XPRS_MIPLOG` | Logging frequency for the MIP solver | 


**Logging for the underlying XPRS problem** 



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XSLP_LOG` | Level of SLP logging \(iteration, penalty, convergence\) | 
`XSLP_SLPLOG` | Logging frequency for SLP iterations | 
`XSLP_MIPLOG` | MI-SLP specific logging | 


**Special logging settings** 



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`XPRS_DCLOG` | Logging of delayed constraint activation | 
`XSLP_ERRORTOL_P` | Absolute tolerance for printing error vectors | 


#### The structure of the log


The typical log with the default settings starts with statistics about the problem sizes. On the Polygon1.mps example, using the Xpress console program to read the problem prints the following:

```

[xpress mps] readprob Polygon1.mps
Reading Problem Polygon
Problem Statistics
          10 (      1 spare) rows
          10 (      4 spare) structural columns
           7 (      1 spare) non-zero elements
MIP Entity Statistics
           0 entities        0 sets        0 set members
    DR:       0     SB:       0     EC:       0
    IV:       0     RX:       0     TX:       0   Form:       7
    UF:       0     WT:       0     Total:       0
Xpress-NLP Statistics:
           7 coefficients
           9 NLP variables
          25 mul             0 div         0 sqrt
           0 exp             0 log        12 pow
           3 sin             6 cos         0 tan


```


The standard XPRS optimizer problem loading statistics is extended with a report about the special structures possibly present in the problem, including DR \(determining rows\), SB \(initial step bounds\), EC \(enforced constraints\), IV \(initial values\), RX/TX \(relative and absolute tolerances\), Form \(formula tokens\), UF \(user functions\), WT \(initial row weights\), followed by statistics about the number of NLP coefficients, NLP variables, and the types of nonlinear operations present \( `mul`, `div`, `sqrt`, `exp`, `log`, `pow`, `sin`, `cos`, `tan`\). Other operations such as `arcsin`, `arccos`, `arctan`, `abs`, `sign`, `erfs`, `minmax`, `pwl`, and `ufun` also exist. Only rows with nonzero counts are displayed.

When the SLP algorithm is started after setting the appropriate controls, the default log contains the following information:

```

[xpress mps] nlpsolver=1
[xpress mps] localsolver=0
[xpress mps] optimize
...
Minimizing problem using Xpress-SLP
Xpress-SLP Augmentation Statistics:
  Columns:
           4 implicit SLP variables
           8 delta vectors
           8 penalty error vectors (1 positive, 7 negative)
  Rows:
           7 nonlinear constraints
           8 update rows
           1 penalty error rows
  Coefficients:
          47 non-constant coefficients

 It LP    NetObj   ValObj ErrorSum ErrorCost Validate   KKT Unconv  Ext Action T
  1 O -3.673E-04  1.4E-07      .00      .00      .00  2.0E-05    0    0 K*     0
  2 O -6.277E-05  1.4E-07      .00      .00      .00  2.0E-05    0    0 *      0
Returning final converged solution

Xpress-SLP stopped after 2 iterations. 0 unconverged items
Problem solved using Xpress-NLP SLP
No unconverged values in active constraints
Problem is nonlinear postsolved
Heap usage: 1246KB (peak 5618KB, 145KB system)
Observed Lipschitz constant:  4.99E-05

Final NLP objective (local optimum)   : 1.499999749999847e-07
  Max validation error      (abs/rel) :      .000 /      .000
  Max primal violation      (abs/rel) : 1.102e-16 / 3.509e-17
  Observed primal integral            :   83.818%
  Total / SLP / LP time               :     .065s /  5.99E-03s /  2.00E-03s
  Work / work units per second        :      0.00 /      0.00
*** Search completed ***

```


The default solution log shows the SLP augmentation statistics \(columns, rows, and coefficients added for the SLP algorithm\), followed by the iteration summary table showing convergence progress, and the final solution statistics.

**Note:**  Setting `XSLP_LOG` to 1 or higher will also display the LP solver logs for each SLP iteration, which can be useful for debugging but may produce verbose output.

The final iteration summary contains the following fields:

**It** : The iteration number.

**LP** : The LP status of the linearization, which can take the following values:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`O` | Linearization is optimal | 
`I` | Linearization is infeasible | 
`U` | Linearization is unbounded | 
`X` | Solving the linearization was interrupted | 


**NetObj** : The net objective of the SLP iteration, excluding penalty costs associated with constraint violations. This represents what the current linearization predicted the objective to be.

**ValObj** : The validated objective function value as defined by the original problem formulation. This is the actual nonlinear objective value evaluated at the current iteration's solution. Note that this value may not always be available, for example if the solution is infeasible.

**ErrorSum** : Sum of the error delta variables. A measure of infeasibility.

**ErrorCost** : The value of the weighted error delta variables in the objective. A measure of the effort needed to push the model towards feasibility.

**Validate** : The validation error indicating the maximum absolute difference between the linearized and actual nonlinear function values.

**KKT** : The Karush-Kuhn-Tucker optimality measure, indicating how close the current solution is to satisfying optimality conditions.

**Unconv** : The number of SLP variables that are not converged.

**Ext** : The number of SLP variables that are converged, but only by extended criteria.

**T** : Timing information for the iteration.

**Action** : The special actions that happened in the iteration. These can be:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`*` | A new incumbent solution was found | 
`0` | Failed line search \(non-improving\) | 
`A` | Adaptive iterations were enabled | 
`B` | Enforcing step bounds | 
`C` | Variable clamping was applied | 
`D` | The determining column filter was applied | 
`E` | Some infeasible rows were enforced | 
`F` | Function evaluation error | 
`G` | Discrete variables were fixed | 
`I` | At least one working problem was unexpectedly infeasible | 
`K` | Optimality validation induces further iterations | 
`P` | The solution needed polishing, postsolve instability | 
`P!` | Solution polishing failed | 
`R` | Penalty error vectors were removed | 
`s` | Switching to primal simplex | 
`S` | Step bound induced infeasibility was repaired | 
`V` | Feasiblity validation induces further iterations | 


The presence of a `P!` suggests that the problem is particularly hard to solve without postsolve, and the model might benefit from setting `XSLP_NOLPPOLISHING` on `XSLP_ALGORITHM` \(please note, that this should only be considered if the solution polishing features is very slow or fails, as the numerical inaccuracies it aims to remove can cause other problems to the solution process\).

After the iteration summary, the log contains a final report about the solution, including the final objective value, validation error, primal violation, primal integral, timing information, and work units.

### Chapter 26 Selecting the right algorithm for a nonlinear problem - when to use the XPRS library instead of XSLP


This chapter focuses on the nonlinear capabilities of the FICO Xpress Optimizer. While Xpress XSLP is able to efficiently solve most nonlinear problems to local optimality, there are two reasons to use other Xpress libraries:
 * Subclasses of nonlinear problems for which the Xpress Optimizer features specialized algorithms that are able to solve those problems more efficiently and in larger sizes. These are notably convex quadratic programming and convex quadratically constrained problems and their mixed integer counterparts.
 * Situations in which a global optimum of a nonlinear problem is required. The functionality of [FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/) allows to also solve nonconvex QPs, MIQPs, NLPs and MINLPs to proven global optimality.


It is also possible to separate the convex quadratic information from the rest of XSLP, and let the Xpress XPRS optimizer handle those directly. Doing so is good modelling practice, but emphasis must be placed on that the Optimizer can only handle convex quadratic constraints, unless a license for FICO Xpress Global is present.

#### Convex Quadratic Programs \(QPs\)


Convex Quadratic Programming\( QP\) problems are an extension of Linear Programming\( LP\) problems where the objective function may include a second order polynomial. The FICO Xpress Optimizer can be used directly for solving QP problems \(and the Mixed Integer version MIQP\).

If there are no other nonlinearities in the problem, the XPRS library provides specialized algorithms for the solution of convex QP \(and MIQP\) problems, that are much more efficient than solving the problem as a general nonlinear problem with XSLP.

#### Convex Quadratically Constrained Quadratic Programs \(QCQPs\)


 Quadratically Constrained Quadratic Programs\( QCQPs\) are an extension of the Quadratic Programming\( QP\) problem where the constraints may also include second order polynomials.

A QCQP problem may be written as:


| &nbsp; | &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | ---------- | 
minimize: | c<sub>1</sub>x<sub>1</sub>+...+c<sub>n</sub>x<sub>n</sub>+x<sup>T</sup>Q<sub>0</sub>x |  |  | 
subject to: | a<sub>11</sub>x<sub>1</sub>+...+a<sub>1n</sub>x<sub>n</sub>+x<sup>T</sup>Q<sub>1</sub>x | ≤ | b<sub>1</sub> | 
|  | ... |  |  | 
|  | a<sub>m1</sub>x<sub>1</sub>+...+a<sub>mn</sub>x<sub>n</sub>+x<sup>T</sup>Q<sub>m</sub>x | ≤ | b<sub>m</sub> | 
|  | l<sub>1</sub>≤x<sub>1</sub>≤u<sub>1</sub>,...,l<sub>n</sub>≤x<sub>n</sub>≤u<sub>n</sub> |  |  | 

where any of the lower or upper bounds _l<sub>i</sub>_  or _u<sub>i</sub>_  may be infinite.

If there are no other nonlinearities in the problem, the XPRS library povides specialized algorithms for the solution of convex QCQP \(and the integer counterpart MIQCQP\) problems, that are much more efficient than solving the problem as a general nonlinear problem with XSLP.

#### Convexity


A fundamental property for nonlinear optimization problems, thus in QCQP as well, is convexity. A region is called _convex_, if for any two points from the region the connecting line segment is also part of the region.

The lack of convexity may give rise to several unfavorable model properties. Lack of convexity in the objective may introduce the phenomenon of locally optimal solutions that are not global ones\( a local optimal solution is one for which a neighborhood in the feasible region exists in which that solution is the best\). While the lack of convexity in constraints can also give rise to local optimums, they may even introduce non– connected feasible regions as shown in Figure  _Non-connected feasible regions_.

![Non-connected feasible regions images/qcqp2.png](Graphic/images/qcqp2.png)

    
  **Figure 26.1:** Non-connected feasible regions 


In this example, the feasible region is divided into two parts. Over feasible region B, the objective function has two alterative local optimal solutions, while over feasible region A the objective is not even bounded.

For convex problems, each locally optimal solution is a global one, making the characterization of the optimal solution efficient.

#### Characterizing Convexity in Quadratic Constraints


A quadratic constraint of form

_a<sub>1</sub>x<sub>1</sub>+...+a<sub>n</sub>x<sub>n</sub>+x<sup>T</sup>Qx≤b_

defines a convex region if and only if _Q_  is a so– called _positive semi– definite_\( PSD\) matrix.

A rectangular matrix _Q_  is PSD by definition if for any vector\( not restricted to the feasible set of a problem\) _x_  it holds that _x<sup>T</sup>Qx≥0_ .

It follows that for greater or equal constraints

_a<sub>1</sub>x<sub>1</sub>+...+a<sub>n</sub>x<sub>n</sub>-x<sup>T</sup>Qx≥b_

the negative of Q shall be PSD.

A nontrivial quadratic equality constraint\( one for which not every coefficient is zero\) always defines a nonconvex region, therefore those must be modelled as XSLP structures.

There is no straightforward way of checking if a matrix is PSD or not. An intuitive way of checking this property, is that the quadratic part shall always only make a constraint harder to satisfy\( i.e. taking the quadratic part away shall always be a relaxation of the original problem\).

There are certain constructs however, that can easily be recognized as being non convex:

 1. the product of two variables say _xy_  without having both _x<sup>2</sup>_  and _y<sup>2</sup>_  defined;
 2. having _- x<sup>2</sup>_  in any quadratic expression in a less or equal, or having _x<sup>2</sup>_  in any greater or equal row.

As a general rule, a convex quadratic objective and convex quadratic constraints are best handled by the XPRS library; while all nonconvex counterparts should be modelled as XSLP structures. It then depends on the application whether FICO Xpress Nonlinear is required \(e.g., because of user functions\) or [FICO Xpress Global](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/globalsolver/HTML/) is the necessary solver \(e.g., because a bound on the optimal objective is needed\). Both use the same modelling API and, license and required features permitting, users can seamlessly switch between one solver or the other.

### Chapter 27 Files used by Xpress NonLinear


Most of the data used by Xpress NonLinear is held in memory. However, there are a few files which are written, either automatically or on demand, in addition to those created by the Xpress Optimizer.



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_LOGFILE_ | Created by:`XSLPsetlogfile` | 
|  | The file name and location are user-defined. | 
|  |  | 
_NAME_.mps | Created by:`XSLPwriteprob` | 
|  | This is the matrix file in extended MPS format. The name is user-defined. The extension _.mps_is appended automatically. | 
|  |  | 
_NAME_.lp | Created by:`XSLPwriteprob` | 
|  | This is the matrix file in human-readable "text". The name is user-defined. The extension _.lp_is appended automatically. | 
|  |  | 

