# FICO® Xpress Optimization

# R interface reference manual
## API reference manual


#### Release 47.01


#### __Last update 20 August, 2026__



(C) 1983-2026 Fair Isaac Corporation. All rights reserved. 
This documentation is the property of Fair Isaac Corporation ("FICO"). Receipt or possession of this documentation does not convey rights to disclose, reproduce, make derivative works, use, or allow others to use it except solely for internal evaluation purposes to determine whether to purchase a license to the software described in this documentation, or as otherwise set forth in a written software license agreement between you and FICO (or a FICO affiliate).  Use of this documentation and the software described in it must conform strictly to the foregoing permitted uses, and no other use is permitted.

The information in this documentation is subject to change without notice. If you find any problems in this documentation, please report them to us in writing. Neither FICO nor its affiliates warrant that this documentation is error-free, nor are there any other warranties with respect to the documentation except as may be provided in the license agreement. FICO and its affiliates specifically disclaim any warranties, express or implied, including, but not limited to, non-infringement, merchantability and fitness for a particular purpose. Portions of this documentation and the software described in it may contain copyright of various authors and may be licensed under certain third-party licenses identified in the software, documentation, or both.

In no event shall FICO or its affiliates be liable to any person for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this documentation or the software described in it, even if FICO or its affiliates have been advised of the possibility of such damage. FICO and its affiliates have no obligation to provide maintenance, support, updates, enhancements, or modifications except as required to licensed users under a license agreement.

FICO is a registered trademark of Fair Isaac Corporation in the United States and may be a registered trademark of Fair Isaac Corporation in other countries. Other product and company names herein may be trademarks of their respective owners.

Patent(s): [www.fico.com/en/patents](https://www.fico.com/en/patents})

Xpress Optimizer 47.01 (FICO® Xpress 9.9)

Deliverable Version: A

Last Revised: 20 August, 2026


## Chapter 1 Introduction


The `xpress package` provides an R interface to the FICO Xpress optimizer. The interface consists of two parts:

 * a thin wrapper for the C library. All the solver functionality is available through this wrapper.
 * a set of convenience function that allow a more “R-like” experience when interacting with the solver.

### Thin Wrapper API

The lowest level of the optimizer’s R interface is a thin wrapper for the C library. People familiar with the C API of the solver will find that things look pretty similar to C. There are a few differences, though:

 * In case of error, functions do not return non-zero status codes. Instead they raise an error by calling `stop()` with an appropriate error message.
 * Functions that have more than one output do not return these outputs via output parameters but instead return a list that contains all the output arguments.
 * Functions that don’t have an explicit return value return the problem object. This way you can easily chain function calls, for example by using the `%>%` operator from the `magrittr` package.

Note that the C library does not operate with vectors and matrices like R does. Instead it works with arrays of indices and non-zero values. Indexing in these arrays is 0-based, so that the first variable, constraint, … will have index 0. This is in contrast to R matrices and vectors for which indexing is 1-based. This must be kept in mind and taken care of when passing data to the optimizer and reading back results.

The convenience functions listed in the next section allow to directly exchange R matrices and vectors with the solver.

### Creation and Deletion of Problems

In order to interact with the solver, a problem object is required. These problems are created by means of the `createprob()` function:

```
prob <- createprob()
```


Note that `createprob()` implicity calls `init("")` in order to initialize licensing if that did not happen yet.

Attached to the problem object are native resources, i.e., resources that are not managed by R. It is thus the user’s responsibility to free the problem object when it is no longer needed. The object is freed using function `destroyprob()`. Good ways to make sure the object is deleted is to use `on.exit()` or `tryCatch`:

```
prob <- createprob()
# make sure problem is deleted when function exits
on.exit(destroyprob(prob))
# or alternatively, execute code in a tryCatch:
tryCatch({ ... },
         finally = { destroyprob(prob) })
```


### Callbacks

The low-level API supports callback. There is one caveat, though: Since R is inherently single-threaded and cannot be called back into from other threads than the main thread, all callback invocations have to be routed through the main thread. The Xpress optimizer supports this by setting the `XPRS_CALLBACKFROMMAINTHREAD` control to 1. This may result in some performance degradation, though.

A callback in the Xpress R interface is just a function or closure with the correct number of arguments. Please refer to the \(C\) reference documentation to learn what callbacks exist, how many arguments the functions require and what the callbacks can do.

A callback may return one of the following:

 * `NULL` or `NA`. These values are just ignored.
 * A length-one integer vector. If the corresponding C callback allows returning a value \(usually in order to stop the search or indicate some other action\) then this value is passed back to the optimizer, otherwise is is ignored.
 * A list. If the corresponding C callback allows returning values then those values are read from the list and returned to the optimizer. The list may also contain a field “ret”, which must be an integer and is treated the same as the single integer return value described above.

A warning is issued in case a callback returns something else or returns a list with unknown elements.

### Convenience Functions

The FICO Xpress optimizer interface provides a set of convenience functions that are based on the thin wrapper described above but allow directly using R data structures like vectors and matrices directly.

Please refer to the documentation for functions `xprs_loadproblemdata` and `xprs_optimize` for further details. These functions allow using R matrices and vectors directly in order to solve optimization problems.

### Installation

Please refer to the INSTALL.txt in the R directory of your Xpress installation for installation instructions.

### Licensing

To run the Optimizer from the R interface it is necessary to have a valid licence file, “xpauth.xpr”. Please see the [license chapter](https://www.fico.com/fico-xpress-optimization/docs/latest/installguide/dhtml/chapinst2.html) of the FICO Xpress Online Documentation for more information on licensing options.

The FICO Xpress licensing system is highly flexible and is easily configurable to cater for the user’s requirements. The system can allow the Optimizer to be run on a specific machine, on a machine with a specific ethernet address or on a machine connected to an authorized hardware dongle.

On Unix systems it is necessary to set the `XPAUTH_PATH` environment variable to the full path to the license file. For ease of support it is recommended that the license file is placed in the bin directory within your Xpress installation and the `XPAUTH_PATH` environment variable is set accordingly before launching an R session , e.g.,

```
export XPAUTH_PATH=/opt/xpressmp/bin/xpauth.xpr
R
```


An alternative is to provide the path by calling the `init` function with the path to the license inside R:

```
library(xpress)
init("/opt/xpressmp/bin/xpauth.xpr")
```


Another alternative is to place the file “xpauth.xpr” into your current working directory before starting your R session, from where it will be picked up automatically.

On Windows operating systems the Optimizer searches for the license file in the directory containing the Xpress libraries, which are installed by default into the “C:\\xpressmp\\bin” folder. To avoid unnecessary licensing problems, it is recommended that the `XPAUTH_PATH`environment variable is not set on Windows.

### A First LP Problem

For starters, we solve the following 2-variable model from R using the Xpress-R interface.

<span> 
\begin{aligned}[t]
&   \min &  x_1 +    x_2 \\
&        & 5 x_1 + x_2 & \geq 7 \\
&        &   x_1 + 4 x_2 & \geq 9 \\
&        & x_1, x_2 & \geq 0
\end{aligned}
 </span>
  

```
suppressMessages(library(xpress))# create a list object to hold all inputproblemdata <-list()# objective coefficientsproblemdata$objcoef <-c(1, 1)# row coefficients as a single matrix objectproblemdata$A <-matrix(c(5, 1, 1, 4), nrow =2, byrow =TRUE)# right-hand sideproblemdata$rhs <-c(7, 9)# row senseproblemdata$rowtype <-c("G", "G")# lower bounds (automatically 0 if not present)problemdata$lb <-c(0, 0)# upper bounds(automatically inferred if not present)problemdata$ub <-c(Inf, Inf)# names for writing to MPS/LP filesproblemdata$colname <-c("x_1", "x_2")# Problem Name displayed when the solver solves the problem.problemdata$probname <-"FirstExample"
```


We now load everything into a new XPRSprob ‘p’. `xprs_loadproblemdata` can be used to load all problem data at once into an existing or new problem object. In this case, we have no existing XPRSprob object. `xprs_loadproblemdata` creates one for us. For convenience and the use inside pipes, xprs\_loadproblemdata returns the prob pointer.

```
prob <-xprs_loadproblemdata(problemdata = problemdata)# You may also use the equivalent# prob <- createprob()# xprs_loadproblemdata(prob, problemdata = problemdata)
```


The newly created XPRSprob object supports the `print` and `summary` statements. Let’s get an overview of the optimization problem loaded into prob

```
print(prob)
```


```
## XPRESS problem object FirstExample
##      2 rows         2 cols        4 elems
##      0 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
```


We use `xprs_optimize` to solve the model. This again returns ‘prob’, which can be summarized using the base function `summary`

```
summary(xprs_optimize(prob))
```


```
## 
## Objective value                     : 3.00000e+00
## Max primal violation      (abs/rel) : 0 / 0
## Max dual violation        (abs/rel) : 0 / 0
## LPSTATUS: 1
```


It may be useful for further processing to convert the solution into a data frame.

```
print(data.frame(Variable = problemdata$colname, Value =getsolution(prob)$x))
```


```
##   Variable Value
## 1      x_1     1
## 2      x_2     2
```


## Chapter 2 Problem Creation Reference


 * [Mixed Integer Programs \(MIP\)](#mixed-integer-programs-mip)
     * [The Problem Data Representation](#the-problem-data-representation)
     * [Working With R Matrices](#working-with-r-matrices)
     * [Incremental Formulation](#incremental-formulation)

 * [Mixed Integer Quadratically Constrained Programs \(MIQCQP\)](#mixed-integer-quadratically-constrained-programs-miqcqp)
     * [The Problem Data Representation](#the-problem-data-representation-1)
     * [Working With R Matrices](#working-with-r-matrices-1)
     * [Incremental Formulation](#incremental-formulation-1)

 * [Problems With Special Constraints And Variables](#problems-with-special-constraints-and-variables)
     * [Indicator Constraints](#indicator-constraints)
     * [General Constraints](#general-constraints)
     * [Piecewise Linear Constraints](#piecewise-linear-constraints)
     * [Special Ordered Set Of Type 1 \(SOS1\)](#special-ordered-set-of-type-1-sos1)
     * [Special Ordered Set Of Type 2 \(SOS2\)](#special-ordered-set-of-type-2-sos2)
     * [Semi-Continuous Variables](#semi-continuous-variables)
     * [Semi-continuous Integer Variables](#semi-continuous-integer-variables)
     * [Partial Integer Variables](#partial-integer-variables)


There are two possibilities to input a problem into the FICO Xpress optimizer from R. The problem can be either incrementally formulated, for example by specifying each row separately, or by loading the entire problem at once. The FICO Xpress R interface provides a convenience function for loading an entire problem at once, which accepts R matrices as input for the various matrices that may describe the linear and quadratic constraint parts.

The `xprs_loadproblemdata` function accepts as input a list of named properties to declare all input at once. Internally, it uses the Xpress functions `XPRSloadmip`, `XPRSloadmiqp` etc. to translate the problem data into the internal formulation. The advantage of using a problem data object is that it lets the R user input matrices instead of sparse matrix representations for declaring linear and quadratic terms in the objective and constraints.

This page illustrates the two methods of formulating optimization problems for the FICO Xpress optimizer using an example of a mixed integer problem \(MIP\) and a mixed-integer quadratically constrained optimization problem \(MIQCQP\). As to the method that loads problem data at once, different ways of constructing matrices are discussed as well.

This page also shows the input of problems that contain some special constraints or variables, such as indicator constraints and semi-continuous variables, etc. It serves as a quick guide for the different elements of optimization problems and the interface functions to declare them.

### Mixed Integer Programs \(MIP\)

We assume familiarity with the basic concepts of mathematical programming and its constraint notation. A mixed integer program is an optimization problem of the form

<span> 
\begin{aligned}[t]
  &\min &   cx\\
  & \text{s.t.}&                           Ax &\{=, \leq,
\geq\} b\\
  & &                                   \ell &\leq x \leq
u\\
  & &                          x_j &\in \{0, 1\} &
\forall j \in \mathcal{B} \\
  & &                          x_j &\in \mathbb{Z} &
\forall j \in \mathcal{I}\\
  & &                          \\
\end{aligned}
 </span>
  

#### The Problem Data Representation

We use a simple MIP example to illustrate the two methods of loading problem data into the FICO Xpress optimizer.

<span> 
\begin{aligned}[t]
  &\min  &       2x_1 & +x_2 + 3x_3\\
  & \text{s.t.}&                  3x_1 & +2x_3 \geq\ 5\\
  & &                             6x_2 & -7x_3 \geq\ 8\\
  & & &                             x_1\in \{0, 1\}\\
  & & &                            x_2, x_3 \in \mathbb{Z}
\\
  & &                0 \leq x_2 &< \infty, 0 \leq x_3
< \infty\\
  & &                          \\
\end{aligned}
 </span>
  

The first way to input a problem into the FICO Xpress optimizer is to load the entire data at once using the function `xprs_loadproblemdata`. To realize this, we can write the constraint coefficients into an R matrix \(in different ways, see next section\), and then use the `xprs_loadproblemdata` function to load all data. Here we write the matrix in the example as a dense matrix and show the usage of `xprs_loadproblemdata`.

```
# create a list to store the problem dataproblemdata <-list()# write the constraint coefficients into a dense matrixcoefmatrix <-matrix(c(3, 0, 2, 0, 6,-7), nrow =2, byrow =TRUE)# load the matrix into the list as row coefficientsproblemdata$A <- coefmatrix# objective coefficientsproblemdata$objcoef <-c(2, 1, 3)# right-hand-side of the constraintsproblemdata$rhs <-c(5, 8)# row senseproblemdata$rowtype <-c("G", "G")# specify all column types, where 'B' means 'binary' and 'I' means 'integer'problemdata$coltype <-c('B', 'I', 'I')#specify the indices of the binary and integer variables (use 0-based indexing)problemdata$entind <-0:2# specify lower bounds and upper bounds for the columnsproblemdata$lb <-c(0, 0, 0)problemdata$ub <-c(1, Inf, Inf)# specify the column namesproblemdata$colname <-c("x_1", "x_2", "x_3")# specify the row namesproblemdata$rowname <-c("row1", "row2")# problem name displayed when the solver solves the problemproblemdata$probname <-"MIPexample"# load the problemdata into a problem 'p'p <-xprs_loadproblemdata(problemdata = problemdata)print(p)# an alternative and equivalent way to do this is:# p <- createprob()# xprs_loadproblemdata(p, problemdata = problemdata)
```


```
## XPRESS problem object MIPexample
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
```


```
# use `xprs_optimize` to solve the problem and see the resultssummary(xprs_optimize(p))print(data.frame(Variable = problemdata$colname, Value =getsolution(p)$x))
```


```
## 
## Final MIP objective                   :                    8
## Final MIP bound                       :                    8
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         2 /        0
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     1
## 2      x_2     3
## 3      x_3     1
```


#### Working With R Matrices

There are several ways to represent the matrices in R according to the nature of the matrices. For low-dimensional matrices with mostly nonzero elements, we can use a dense specification as shown above, where every entry is specified.

Most high-dimensional matrices occurring in optimization problems are usually very sparse, i.e., most of the coefficients are zero. This fact is widely used in sparse matrix representations, which only store the nonzero coefficients of each column of a matrix together with an index into the rows that correspond to those nonzero entries. Using a sparse representation for such matrices saves a lot of memory. As a rule of thumb, we create sparse matrices when the problem data is too large to store every single of the `ROWS` <span>\( \times \)</span>  `COLS` coefficients, or the matrix contains mostly 0 coefficients.

There are many ways to create sparse matrices. Here we still use the same MIP example to illustrate some possible methods to construct sparse matrices.

The first method only works for small-sized matrices because at creation we actually specify every element of the matrix.

We can always convert a sparse matrix back to a dense matrix:

```
# create a sparse matrixcoefmatrix_sparse1 <-Matrix(c(3, 0, 2, 0, 6,-7),nrow =2,byrow =TRUE,sparse =TRUE)coefmatrix_sparse1# a sparse matrix can be converted to a dense matrixcoefmatrix_dense <-as.matrix(coefmatrix_sparse1)print("The sparse matrix can be converted into a dense matrix:")coefmatrix_dense
```


```
## 2 x 3 sparse Matrix of class "dgCMatrix"
##            
## [1,] 3 .  2
## [2,] . 6 -7
## [1] "The sparse matrix can be converted into a dense matrix:"
##      [,1] [,2] [,3]
## [1,]    3    0    2
## [2,]    0    6   -7
```


In the second chunk, we first create a sparse matrix containing only 0’s, and then assign the nonzero elements:

```
# first create a sparse matrix containing only 0 valuescoefmatrix_sparse2 <-Matrix(0, nrow =2, ncol =3, byrow =TRUE, sparse =TRUE,doDiag =FALSE)# then assign the nonzero valuescoefmatrix_sparse2[1, c(1, 3)] <-c(3, 2)coefmatrix_sparse2[2, 2:3] <-c(6, -7)coefmatrix_sparse2
```


```
## 2 x 3 sparse Matrix of class "dgCMatrix"
##            
## [1,] 3 .  2
## [2,] . 6 -7
```


The third one, which creates a sparse matrix in triplet format:

```
# create a sparse matirx in triplet formatcoefmatrix_sparse3 <-sparseMatrix(i =c(1, 1, 2, 2),j =c(1, 3, 2:3),x =c(3, 2, 6,-7),dims =c(2, 3)  )coefmatrix_sparse3
```


```
## 2 x 3 sparse Matrix of class "dgCMatrix"
##            
## [1,] 3 .  2
## [2,] . 6 -7
```


#### Incremental Formulation

Another way to input problem data into Xpress optimizer is to add the problem data incrementally. We can use the convenience functions `xprs_addrow` and `xprs_addcol`, which are exclusive to the R interface, or `addrows` and `addcols` to realize this. One difference between these two pairs of functions is that, for `xprs_addrow` and `xprs_addcol`, row type, row name, column type and column name can be specified inside these functions, whereas for `addrows` and `addcols`, row type can be defined inside function `addrows`, the other three features need to be specified using `chgcoltype` and `addnames`. Another difference is that `xprs_addrow` and `xprs_addcol` only add a single row and a single column, while `addrows` and `addcols` can add multiple rows and columns.

Of course, it is possible to mix the use of these functions to formulate problems.

Firstly we show how to use `xprs_addcol` and `xprs_addrow` to incrementally add the data.

```
# firstly, create a new empty problem 'prob1'prob1 <-createprob()# add the columnsxprs_addcol(prob1, lb =0, ub =1, coltype ='B', name ="x_1", objcoef =2)xprs_addcol(prob1, lb =0, ub =Inf, coltype ='I', name ="x_2", objcoef =1)xprs_addcol(prob1, lb =0, ub =Inf, coltype ='I', name ="x_3", objcoef =3)# add the rowsxprs_addrow(prob1,rowtype ="G",rhs =5,name ="row1",colind =c(0, 2),rowcoef =c(3, 2),       )xprs_addrow(prob1,rowtype ="G",rhs =8,name ="row2",colind =c(1, 2),rowcoef =c(6, -7),       )# specify the name of the problemsetprobname(prob1, "MIPexample")
```


```
# show the problem createdprint(prob1)
```


```
## XPRESS problem object MIPexample
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
```


Next we show how to use `addrows` and `addcols` to incrementally add the problem data.

```
# firstly, create a new empty problem 'prob2'prob2 <-createprob()# add the columnsaddcols(prob2,objcoef =c(2, 1, 3),start =c(0, 1, 2),rowind =NULL,rowcoef =NULL,lb =c(0, 0, 0),ub =c(1, Inf, Inf))# specify the column typeschgcoltype(prob2, c(0, 1, 2), c('B', 'I', 'I'), ncols =3)# specify the column namesaddnames(prob2, 2, c("x_1", "x_2", "x_3"), 0, 2)# add the rowsaddrows(prob2,rowtype ="G",rhs =5,start =0,colind =c(0, 2),rowcoef =c(3, 2)       )addrows(prob2,rowtype ="G",rhs =8,start=0,colind =c(1, 2),rowcoef =c(6, -7)       )# specify the row namesaddnames(prob2, 1, c("row1", "row2"), 0, 1)# specify the name of the problemsetprobname(prob2, "MIPexample")
```


```
# show the problem createdprint(prob2)
```


```
## XPRESS problem object MIPexample
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
```


### Mixed Integer Quadratically Constrained Programs \(MIQCQP\)

Mixed Integer Quadratically Constrained Programming \(MIQCQP\) problems are an extension of Mixed Integer Programming \(MIP\) problems where the objective function and constraints may include a second order polynomial.

<span> 
\begin{aligned}[t]
  &\min & \frac{1}{2} x^t Q_0 x + cx &\\
  & \text{s.t.}&                           Ax + Q(x)&\{=,
\leq, \geq\} b\\
  & &                \ell \leq x &\leq u\\
  & &                          x_j &\in \{0, 1\} &
\forall j \in \mathcal{B} \\
  & &                          x_j &\in \mathbb{Z} &
\forall j \in \mathcal{I}\\
  & &                          \\
\end{aligned}
 </span>
  

The function <span>\( Q:\mathbb{R}^n \rightarrow
\mathbb{R}^m \)</span> , <span>\( Q(x) := (x^t Q_1x,
x^t Q_2x, \dots, x^t Q_m x)^t \)</span>  is shorthand for the quadratic parts of the constraints.

The sets <span>\( \mathcal{B} \)</span>  and <span>\( \mathcal{I} \)</span>  denote the subsets of the columns \(of <span>\( A \)</span> \) that are restricted to binary or integer values, respectively. There are also some more advanced column types such as semi-continuous, semi-integer, and partial integer columns that are explained below.

#### The Problem Data Representation

As for MIP, there are two possibilities to input a problem into the FICO Xpress optimizer: loading at once and incremental formulation. To illustrate this, we use the example below, which extends the MIP example by some quadratic terms.

<span> 
\begin{aligned}[t]
  &\min & \ x_1^2 + 2x_3^2+2x_1+x_2 -3x_3\\
  & \text{s.t.}&                 3x_1 + 2x_3^2 \leq\ 5\\
  & &                             x_1^2  -7x_3 \leq\ 8\\
  & &                            x_1\in \{0, 1\}\\
  & &                            x_2, x_3 \in \mathbb{Z} \\
  & &               0 \leq x_2 < \infty, 0 \leq x_3 <
\infty\\
  & &                          \\
\end{aligned}
 </span>
  

In this example, the matrix <span>\( Q_0 \)</span>  in the objective is:<span> 
\begin{aligned}[t]
  && Q_0 = \begin{bmatrix} 2 & 0 & 0 \\ 0 & 0 &
0 \\ 0 & 0 & 4\end{bmatrix}
  & &                          \\
\end{aligned}
 </span>
  

The matrix <span>\( Q_1 \)</span>  in the first row is:<span> 
\begin{aligned}[t]
  && Q_1 = \begin{bmatrix} 0 & 0 & 0 \\ 0 & 0 &
0 \\ 0 & 0 & 2\end{bmatrix}
  & &                          \\
\end{aligned}
 </span>
  

The matrix <span>\( Q_2 \)</span>  in the second row is:

<span> 
\begin{aligned}[t]
  && Q_2 = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 0 &
0 \\ 0 & 0 & 0\end{bmatrix}
  & &                          \\
\end{aligned}
 </span>
  

The first way we load the problem into the FICO Xpress optimizer at once is to use the function `xprs_loadproblemdata`.

```
qproblemdata <-list()# objective coefficientsqproblemdata$objcoef <-c(2, 1, -3)# write the constraint coefficients into a dense matrixcoefmatrix <-matrix(c(3, 0, 0, 0, 0,-7), nrow =2, byrow =TRUE)# load the matrix into the list as row coefficientsqproblemdata$A <- coefmatrix# right-hand-side of the constraintsqproblemdata$rhs <-c(5, 8)# row senseqproblemdata$rowtype <-c("L", "L")# specify all column types, where 'B' means 'binary' and 'I' means 'integer'qproblemdata$coltype <-c('B', 'I', 'I')#specify the indices of the binary and integer variables (use 0-based indexing)qproblemdata$entind <-0:2# specify lower bounds and upper bounds for the columnsqproblemdata$lb <-c(0, 0, 0)qproblemdata$ub <-c(1, Inf, Inf)# specify the column namesqproblemdata$colname <-c("x_1", "x_2", "x_3")# specify the row namesqproblemdata$rowname <-c("row1", "row2")# problem Name displayed when the solver solves the problemqproblemdata$probname <-"MIQCQPexample"# # quadratic part in objective# # 1.C-Style notation# qproblemdata$nobjqcoef <- 2# qproblemdata$objqcol1 <- c(0, 2)# qproblemdata$objqcol2 <- c(0, 2)# qproblemdata$objqcoef <- c(2, 4)# 2.Matrix notationqproblemdata$Qobj <-Matrix(c(2, 0, 0, 0, 0, 0, 0, 0, 4),nrow =3,byrow =TRUE,sparse =TRUE,doDiag =FALSE  )# # quadratic part in constraints# # 1.C-Style notation# qproblemdata$nqrows <- 2# qproblemdata$qrowind <- c(0, 1)# qproblemdata$nrowqcoefs <- c(1, 1)# qproblemdata$rowqcol1 <- c(2, 0)# qproblemdata$rowqcol2 <- c(2, 0)# qproblemdata$rowqcoef <- c(2, 1)# 2.Matrix notationqproblemdata$Qrowlist <-list()qproblemdata$Qrowlist[[1]] <-Matrix(c(0, 0, 0, 0, 0, 0, 0, 0, 2),nrow =3,byrow =TRUE,sparse =TRUE,doDiag =FALSE  )qproblemdata$Qrowlist[[2]] <-Matrix(c(1, 0, 0, 0, 0, 0, 0, 0, 0),nrow =3,byrow =TRUE,sparse =TRUE,doDiag =FALSE  )# load the problemdata into a problem 'qcqp'qcqp <-xprs_loadproblemdata(problemdata = qproblemdata)
```


```
## 'as(<dsCMatrix>, "dgTMatrix")' is deprecated.
## Use 'as(as(., "generalMatrix"), "TsparseMatrix")' instead.
## See help("Deprecated") and help("Matrix-deprecated").
```


```
print(qcqp)# an alternative and equivalent way to do this is:# p <- createprob()# xprs_loadproblemdata(p, problemdata=qproblemdata)
```


```
## XPRESS problem object MIQCQPexample
##      2 rows         3 cols        2 elems
##      3 entities      0 sets        0 indicators
##      2 qelems        2 qcelems
##      0 gencons       0 pwlcons
```


```
# use `xprs_optimize` to solve the problem and see the resultssummary(xprs_optimize(qcqp))print(data.frame(Variable = qproblemdata$colname, Value =getsolution(qcqp)$x))
```


```
## 
## Final MIP objective                   :                   -1
## Final MIP bound                       :                   -1
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     0
## 2      x_2     0
## 3      x_3     1
```


#### Working With R Matrices

Like for the linear part of the constraints \(matrix <span>\( A \)</span> \) and the quadratic objective matrix and the quadratic terms in constraints can be specified as matrices in sparse or dense representation.

In the above section, we specify all the matrices as dense matrices, and now we show how to construct them as sparse matrices.

The first way:

```
# create sparse matrixqobjmat_sparse1 <-Matrix(c(2, 0, 0, 0, 0, 0, 0, 0, 4),nrow =3,byrow =TRUE,sparse =TRUE  )qobjmat_sparse1qrowmat1_sparse1 <-Matrix(c(0, 0, 0, 0, 0, 0, 0, 0, 2),nrow =3,byrow =TRUE,sparse =TRUE  )qrowmat1_sparse1qrowmat2_sparse1 <-Matrix(c(1, 0, 0, 0, 0, 0, 0, 0, 0),nrow =3,byrow =TRUE,sparse =TRUE  )qrowmat2_sparse1
```


```
## 3 x 3 diagonal matrix of class "ddiMatrix"
##      [,1] [,2] [,3]
## [1,]    2    .    .
## [2,]    .    0    .
## [3,]    .    .    4
## 3 x 3 diagonal matrix of class "ddiMatrix"
##      [,1] [,2] [,3]
## [1,]    0    .    .
## [2,]    .    0    .
## [3,]    .    .    2
## 3 x 3 diagonal matrix of class "ddiMatrix"
##      [,1] [,2] [,3]
## [1,]    1    .    .
## [2,]    .    0    .
## [3,]    .    .    0
```


The second way:

```
# first create sparse matrices containing only 0 valuesqobjmat_sparse2 <-Matrix(0,nrow =3,ncol =3,byrow =TRUE,sparse =TRUE,doDiag =FALSE  )qrowmat1_sparse2 <-Matrix(0,nrow =3,ncol =3,byrow =TRUE,sparse =TRUE,doDiag =FALSE  )qrowmat2_sparse2 <-Matrix(0,nrow =3,ncol =3,byrow =TRUE,sparse =TRUE,doDiag =FALSE  )# then assign the nonzero valuesqobjmat_sparse2[1, 1] <-2qobjmat_sparse2[3, 3] <-4qrowmat1_sparse2[3, 3] <-2qrowmat2_sparse2[1, 1] <-1qobjmat_sparse2qrowmat1_sparse2qrowmat2_sparse2
```


```
## 3 x 3 sparse Matrix of class "dsCMatrix"
##           
## [1,] 2 . .
## [2,] . . .
## [3,] . . 4
## 3 x 3 sparse Matrix of class "dsCMatrix"
##           
## [1,] . . .
## [2,] . . .
## [3,] . . 2
## 3 x 3 sparse Matrix of class "dsCMatrix"
##           
## [1,] 1 . .
## [2,] . . .
## [3,] . . .
```


The third way:

```
# create sparse matrices in triplet formatqobjmat_sparse3 <-sparseMatrix(i =c(1, 3),j =c(1, 3),x =c(2, 4),dims =c(3, 3)  )qobjmat_sparse3qrowmat1_sparse3 <-sparseMatrix(i =3,j =3,x =2,dims =c(3, 3)  )qrowmat1_sparse3qrowmat2_sparse3 <-sparseMatrix(i =1,j =1,x =1,dims =c(3, 3)  )qrowmat2_sparse3
```


```
## 3 x 3 sparse Matrix of class "dgCMatrix"
##           
## [1,] 2 . .
## [2,] . . .
## [3,] . . 4
## 3 x 3 sparse Matrix of class "dgCMatrix"
##           
## [1,] . . .
## [2,] . . .
## [3,] . . 2
## 3 x 3 sparse Matrix of class "dgCMatrix"
##           
## [1,] 1 . .
## [2,] . . .
## [3,] . . .
```


#### Incremental Formulation

We can also formulate the MIQCQP example incrementally, and same as MIP, we can use the functions `xprs_addrow` and `xprs_addcol`, or `addrows` and `addcols` to realize this. The differences between these two pairs of functions are described in the MIP section. Here, we only show the usage of the convenience functions `xprs_addrow` and `xprs_addcol`.

As for the quadratic terms, we always use `chgmqobj` to add quadratic terms to the objective and `addqmatrix` to add quadratic terms to constraints.

```
# firstly, create a new empty problem 'qcqp1'qcqp1 <-createprob()# add the columnsxprs_addcol(qcqp1, lb =0, ub =1, coltype ='B', name ="x_1", objcoef =2)xprs_addcol(qcqp1, lb =0, ub =Inf, coltype ='I', name ="x_2", objcoef =1)xprs_addcol(qcqp1, lb =0, ub =Inf, coltype ='I', name ="x_3", objcoef =-3)# add the quadratic terms in objective# since the quadratic matrix is assumed to be symmetric, so specifying the upper# diagonal part of the matrix is enough, and the off-diagonal coefficients can be# specified as they are.chgmqobj(qcqp1, c(0, 2), c(0, 2), c(2, 4), 2)# add the rowsxprs_addrow(qcqp1,rowtype ="L",rhs =5,name ="row1",colind =0,rowcoef =3,       )xprs_addrow(qcqp1,rowtype ="L",rhs =8,name ="row2",colind =2,rowcoef =-7,       )# add quadratic terms in the constraintsaddqmatrix(qcqp1,row =0,rowqcol1 =2,rowqcol2 =2,rowqcoef =2           )addqmatrix(qcqp1,row =1,rowqcol1 =0,rowqcol2 =0,rowqcoef =1           )# specify the name of the problemsetprobname(qcqp1, "MIQCQPexample")
```


```
# show the problem createdprint(qcqp1)
```


```
## XPRESS problem object MIQCQPexample
##      2 rows         3 cols        2 elems
##      3 entities      0 sets        0 indicators
##      2 qelems        2 qcelems
##      0 gencons       0 pwlcons
```


```
# use `xprs_optimize` to solve the problem and see the resultssummary(xprs_optimize(qcqp1))print(data.frame(Variable=c("x_1", "x_2", "x_3"), Value=getsolution(qcqp1)$x))
```


```
## 
## Final MIP objective                   :                   -1
## Final MIP bound                       :                   -1
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     0
## 2      x_2     0
## 3      x_3     1
```


### Problems With Special Constraints And Variables

In this section, we display some examples that contain special constraints or variables and show how to input them into the FICO Xpress optimizer. To see how these special constraints or variables can have effect on the solutions, we use examples based on the MIP example so that we can compare the new solutions obtained with the MIP solution. For convenience, we create a function `load_MIP_example` to load the MIP example and we will use this function at the begining of each sub-section and then make adjustments on the MIP example incrementally \(adding constraints or changing variable types, etc.\).

```
load_MIP_example =function(){# firstly, create a new empty problem 'prob'  prob <-createprob()# add the columnsxprs_addcol(prob, lb =0, ub =1, coltype ='B', name ="x_1", objcoef =2)xprs_addcol(prob, lb =0, ub =Inf, coltype ='I', name ="x_2", objcoef =1)xprs_addcol(prob, lb =0, ub =Inf, coltype ='I', name ="x_3", objcoef =3)# add the rowsxprs_addrow(prob,rowtype ="G",rhs =5,name ="row1",colind =c(0, 2),rowcoef =c(3, 2),              )xprs_addrow(prob,rowtype ="G",rhs =8,name ="row2",colind =c(1, 2),rowcoef =c(6, -7),              )# return 'prob'  prob}
```


Notice that for the constraints and special variables that will be discussed in this section, ‘Indicator Constraints’, ‘General Constraints’ and ‘Piecewise Linear Constraints’ cannot be specified when using the function `xprs_loadproblemdata` to load the problem at once. Instead, they need to be added using corresponding functions.

#### Indicator Constraints

Indicator constraints are constraints each with a specified associated binary ‘controlling’ variable where we assume the constraint must be satisfied when the binary variable is at a specified binary value; otherwise the constraint does not need to be satisfied.

We use an extension of the MIP example to show the formulation of problems with indicator constraints. Based on the MIP example, we add the constraint that if the binary variable <span>\( x_1 \)</span>  takes value 1, then integer variable <span>\( x_3 \)</span>  must be 0. Mathematically, we want to impose the implication:

<span> 
\begin{aligned}[t]
x_1 = 1 \Rightarrow x_3 = 0
\end{aligned}
 </span>
  

To add this constraint, we first add a new row <span>\( x_3 = 0 \)</span> , and then use the function `setindicators` to specify the indicator constraint.

```
# firstly, load the MIP example to a problem 'probIndicator'probIndicator <-load_MIP_example()# add the new row x_3 = 0xprs_addrow(probIndicator,rowtype ="E",rhs =0,name ="row3",colind =2,rowcoef =1,       )# add the indicator implication between variable x_1 and the new rowsetindicators(probIndicator,rowind =2,colind =0,complement =1# row is active when x_1 = 1  )# specify the name of the problemsetprobname(probIndicator, "IndicatorConstraintExample")
```


Now we solve this example. We see that the solution satisfies the indicator constraint, where <span>\( x_1 \)</span>  takes 0 and thus <span>\( x_3 \)</span>  can take nonzero value 3.

```
# show the problem createdprint(probIndicator)summary(xprs_optimize(probIndicator))print(data.frame(Variable =c("x1", "x2", "x3"),Value =getsolution(probIndicator)$x))
```


```
## XPRESS problem object IndicatorConstraintExample
##      3 rows         3 cols        5 elems
##      3 entities      0 sets        1 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
## 
## Final MIP objective                   :                   14
## Final MIP bound                       :                   14
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1       x1     0
## 2       x2     5
## 3       x3     3
```


#### General Constraints

General constraints are specific type of MIP constraints to model `min`, `max`, `and`, `or`, and `absolute value` relationships between two or more variables.

Here we still use the MIP example and add a general constraint that <span>\( x_3 \)</span>  takes the minimum value between 2 and <span>\( x_2 \)</span> , mathematically, we require:

<span> 
\begin{aligned}[t]
x_3 = \min \left\{ x_2, 2 \right\}
\end{aligned}
 </span>
  

We use the function `addgencons` to add this general constraint:

```
# firstly, load the MIP example to a problem 'probGeneral'probGeneral <-load_MIP_example()# set the general constraint:addgencons(probGeneral,contype =1,resultant =2,colstart =0,colind =1,valstart =0,val =2)# specify the name of the problemsetprobname(probGeneral, "GeneralConstraintExample")
```


Now we solve this example. We see that the solution satisfies the general constraint, because <span>\( x_3 \)</span>  takes the value <span>\( \min \left\{ x_2=4, \ 2
\right\}=2 \)</span> .

```
# show the problem createdprint(probGeneral)summary(xprs_optimize(probGeneral))print(data.frame(Variable =c("x1", "x2", "x3"),Value =getsolution(probGeneral)$x))
```


```
## XPRESS problem object GeneralConstraintExample
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      1 gencons       0 pwlcons
## 
## Final MIP objective                   :                   12
## Final MIP bound                       :                   12
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1       x1     1
## 2       x2     4
## 3       x3     2
```


#### Piecewise Linear Constraints

Piecewise linear constraints are constraints that define a piecewise linear relationship between two variables. These are defined via a set of breakpoints with linearly interpolated values between and beyond them \(with the slope before the first and after the last point continuing the slope between the first/last two points\). The piece-wise linear functions are allowed to be discontinuous by defining multiple points with the same value of the input variable x, in which case the output variable y is allowed to take any value between the corresponding y-values of these breakpoints, while the first of them will define the slope before and the last will define the slope after this x-value.

Based on the MIP example, we add a piecewise linear constraint between <span>\( x_2 \)</span>  and <span>\( x_3 \)</span> : <span>\( x_2 =
f(x_3) \)</span> , where:

<span> 
\begin{aligned}[t]
x_2 = f\left( x_3 \right)= \left\{
\begin{array}{lr} 2x_3, & \textsf{if}\ 0\leq x_3\leq 2\\
\frac{1}{2}\ x_3+3,   & \textsf{if}\ 2< x_3<\infty \\
\end{array} \right.
\end{aligned}
 </span>
  

This function can be defined using the breakpoints `(0, 0)`, `(2, 4)`, and `(4, 5)`. Note that the last breakpoint could also be replaced, e.g., by `(3, 4.5)`. We will use the function `addpwlcons` to add this piecewise linear constraint.

```
# firstly, load the MIP example to a problem 'probPWL'probPWL <-load_MIP_example()# set the piecewise linear constraint:addpwlcons(probPWL,colind =2,resultant =1,start =0,xval =c(0, 2, 4),yval =c(0, 4, 5))# specify the name of the problemsetprobname(probPWL, "PWLExample")
```


Now we solve this example. We see that the solution satisfies the piecewise linear constraint, where <span>\( x_3=2 \)</span>  and thus <span>\( x_2=2x_3=4 \)</span> .

```
# show the problem createdprint(probPWL)summary(xprs_optimize(probPWL))print(data.frame(Variable =c("x1", "x2", "x3"),Value =getsolution(probPWL)$x))
```


```
## XPRESS problem object PWLExample
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       1 pwlcons
## 
## Final MIP objective                   :                   12
## Final MIP bound                       :                   12
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1       x1     1
## 2       x2     4
## 3       x3     2
```


#### Special Ordered Set Of Type 1 \(SOS1\)

SOS1 is a set of decision variables ordered by a set of specified continuous values \(or reference values\) of which at most one can take a nonzero value. Note that SOS constraints must be input in sparse row representation.

We illustrate the input of SOS1 by an extension of the MIP example. Here we only allow one of the three decision variables to assume a nonzero value by imposing the restriction

<span> 
  \begin{aligned}[t]
    \text{SOS1}\left(x_1, x_2, x_3\right)
  \end{aligned}
 </span>
   A mathematically equivalent formulation of this SOS1 restriction requires auxiliary binary variables. We introduce one auxiliary binary variables for each decision variable to indicate whether they are 0 or nonzero. We restrict the sum of these auxiliary binary variables to 1 to ensure only one variable takes nonzero value. Since <span>\( x_1 \)</span>  itself is a binary variable, we only need two binary variables <span>\( a_2 \)</span>  and <span>\( a_3 \)</span>  for <span>\( x_2 \)</span>  and <span>\( x_3 \)</span>  such that:

<span> 
\begin{aligned}[t]
x_j= 0 \Leftrightarrow a_j = 0 \quad \text{ for } j \in \{2, 3\}
\end{aligned}
 </span>
   Note that this relationship can only be imposed through a linear constraint if the variable <span>\( x_j \)</span>  has afinite upper bound.

Finally, we restrict the sum of these binary variables:

<span> 
\begin{aligned}[t]
x_1 + a_2 + a_3 \leq 1
\end{aligned}
 </span>
  

If we add this constraint to the original MIP example, the problem will be infeasible. So we change the row coefficient for <span>\( x_3 \)</span>  in the second row “row2” from ‘-7’ to ‘7’, and keep everything else the same.

SOS-type constraints are called “Sets” in Xpress terminology. To add this SOS1 restriction, we use the function `addsets`.

```
# firstly, load the MIP example to a problem 'probSOS1'probSOS1 <-load_MIP_example()# change the row coefficient of x_3 in the second row from '-7' to 7chgcoef(probSOS1, 1, 2, 7)# add the SOS1 setaddsets(probSOS1,settype ='1',start =0,colind =c(0, 1, 2),refval =c(1, 2, 3))# specify the name of the problemsetprobname(probSOS1, "SOS1Example")
```


Now we solve this example. We see that the solution satisfies the SOS1 restriction, where only <span>\( x_3 \)</span>  takes nonzero value 3.

```
# show the problem createdprint(probSOS1)summary(xprs_optimize(probSOS1))print(data.frame(Variable =c("x1", "x2", "x3"),Value =getsolution(probSOS1)$x))
```


```
## XPRESS problem object SOS1Example
##      2 rows         3 cols        4 elems
##      3 entities      1 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
## 
## Final MIP objective                   :                    9
## Final MIP bound                       :                    9
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1       x1     0
## 2       x2     0
## 3       x3     3
```


SOS1 can also be specified when loading the problem at once, so next we will show how to add SOS1 when using function `xprs_loadproblemdata`.

```
# create a list to store the problem datapSOS1data <-list()# write the constraint coefficients into a dense matrixcoefmatrix <-matrix(c(3, 0, 2, 0, 6, 7), nrow =2, byrow =TRUE)# load the matrix into the list as row coefficientspSOS1data$A <- coefmatrix# objective coefficientspSOS1data$objcoef <-c(2, 1, 3)# right-hand-side of the constraintspSOS1data$rhs <-c(5, 8)# row sensepSOS1data$rowtype <-c("G", "G")# specify all column types, where 'B' means 'binary' and 'I' means 'integer'pSOS1data$coltype <-c('B', 'I', 'I')#specify the indices of the binary and integer variables (use 0-based indexing)pSOS1data$entind <-0:2# specify lower bounds and upper bounds for the columnspSOS1data$lb <-c(0, 0, 0)pSOS1data$ub <-c(1, Inf, Inf)# specify the column namespSOS1data$colname <-c("x_1", "x_2", "x_3")# specify the row namespSOS1data$rowname <-c("row1", "row2")# problem Name displayed when the solver solves the problempSOS1data$probname <-"SOS1Example"# specify SOS1pSOS1data$settype <-'1'pSOS1data$setstart <-c(0, 3)pSOS1data$setind <-c(0, 1, 2)pSOS1data$refval <-c(1, 2, 3)# load the problemdata into a problem 'pSOS1'pSOS1 <-xprs_loadproblemdata(problemdata=pSOS1data)print(pSOS1)
```


```
## XPRESS problem object SOS1Example
##      2 rows         3 cols        4 elems
##      3 entities      1 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
```


We solve this example and we get the same solution as before.

```
# use `xprs_optimize` to solve the problem and see the resultssummary(xprs_optimize(pSOS1))print(data.frame(Variable = pSOS1data$colname, Value =getsolution(pSOS1)$x))
```


```
## 
## Final MIP objective                   :                    9
## Final MIP bound                       :                    9
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     0
## 2      x_2     0
## 3      x_3     3
```


#### Special Ordered Set Of Type 2 \(SOS2\)

SOS2 is a set of variables ordered by a set of specified continuous values \(or reference values\) of which at most two can be nonzero, and if two are nonzero then they must be consecutive in their ordering. Note that SOS constraints must be input in sparse row representation.

We illustrate the input of SOS2 by an extension of the MIP example as well, here we only allow two consecutive decision variables to take nonzero values and we change the upper bounds of <span>\( x_2 \)</span>  and <span>\( x_3 \)</span>  both from infinity to 10.

As for SOS1, an alternative, mathematically equivalent representation of an SOS2 constraint, requires auxiliary binary variables <span>\( a_2 \)</span>  and <span>\( a_3 \)</span> , of which at most can be set to 1:<span> 
\begin{aligned}[t]
x_1 + a_2 + a_3 \leq 1
\end{aligned}
 </span>
  

But this time, we set the constraints for each variable in this way:

<span> 
\begin{aligned}[t]
&&  x_1\leq x_1\cdot1 \\
&&  x_2\leq (x_1 + a_2)\cdot 10 \\
&&  x_3\leq (a_2 + a_3)\cdot 10
\end{aligned}
 </span>
  

So for example, if the constraint enforces <span>\( a_2 \)</span>  to be 1, then <span>\( x_1 \)</span>  must be 0, and <span>\( x_2 \)</span>  and <span>\( x_3 \)</span>  are allowed to take nonzero values, which satisfy the SOS2 restriction.

To add this SOS2 restriction, we use again the function `addsets` with the appropriate set type.

```
# firstly, load the MIP example to a problem 'probSOS2'probSOS2 <-load_MIP_example()# change the upper bounds for both x_2 and x_3chgbounds(probSOS2,colind =c(1, 2),bndtype =c('U', 'U'),bndval =c(10, 10))# add the SOS2 setaddsets(probSOS2,settype ='2',start =0,colind =c(0, 1, 2),refval =c(1, 2, 3))# specify the name of the problemsetprobname(probSOS2, "SOS2Example")
```


Now we solve this example. We see that the solution satisfies the SOS2 restriction, where only <span>\( x_2 \)</span>  and <span>\( x_3 \)</span>  take nonzero values 5 and 3.

```
# show the problem createdprint(probSOS2)summary(xprs_optimize(probSOS2))print(data.frame(Variable =c("x_1", "x_2", "x_3"),Value =getsolution(probSOS2)$x))
```


```
## XPRESS problem object SOS2Example
##      2 rows         3 cols        4 elems
##      3 entities      1 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
## 
## Final MIP objective                   :                   14
## Final MIP bound                       :                   14
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     0
## 2      x_2     5
## 3      x_3     3
```


SOS2 can also be specified when loading the problem at once, so next we will show how to add SOS2 when using function `xprs_loadproblemdata`.

```
# create a list to store the problem datapSOS2data <-list()# write the constraint coefficients into a dense matrixcoefmatrix <-matrix(c(3, 0, 2, 0, 6,-7), nrow =2, byrow =TRUE)# load the matrix into the list as row coefficientspSOS2data$A <- coefmatrix# objective coefficientspSOS2data$objcoef <-c(2, 1, 3)# right-hand-side of the constraintspSOS2data$rhs <-c(5, 8)# row sensepSOS2data$rowtype <-c("G", "G")# specify all column types, where 'B' means 'binary' and 'I' means 'integer'pSOS2data$coltype <-c('B', 'I', 'I')#specify the indices of the binary and integer variables (use 0-based indexing)pSOS2data$entind <-0:2# specify lower bounds and upper bounds for the columnspSOS2data$lb <-c(0, 1, 1)pSOS2data$ub <-c(1, 10, 10)# specify the column namespSOS2data$colname <-c("x_1", "x_2", "x_3")# specify the row namespSOS2data$rowname <-c("row1", "row2")# problem Name displayed when the solver solves the problempSOS2data$probname <-"SOS2Example"# specify SOS2pSOS2data$settype <-'2'pSOS2data$setstart <-c(0, 3)pSOS2data$setind <-c(0, 1, 2)pSOS2data$refval <-c(1, 2, 3)# load the problemdata into a problem 'p'pSOS2 <-xprs_loadproblemdata(problemdata = pSOS2data)print(pSOS2)
```


```
## XPRESS problem object SOS2Example
##      2 rows         3 cols        4 elems
##      3 entities      1 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
```


We solve this example and we get the same solution as before.

```
# use `xprs_optimize` to solve the problem and see the resultssummary(xprs_optimize(pSOS2))print(data.frame(Variable =c("x_1", "x_2", "x_3"),Value =getsolution(pSOS2)$x))
```


```
## 
## Final MIP objective                   :                   14
## Final MIP bound                       :                   14
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     0
## 2      x_2     5
## 3      x_3     3
```


#### Semi-Continuous Variables

Semi-continuous variables are decision variables that either have value 0, or a continuous value above a specified nonnegative limit. To show how we specify semi-continuous variables when formulating problems, we use the MIP example but change the variable type of <span>\( x_3 \)</span>  from integer to semi-continuous, and set the nonzero limit of <span>\( x_3 \)</span>  as 2:

<span> 
\begin{aligned}[t]
  &\min  &       2x_1 & +x_2 + 3x_3\\
  & \text{s.t.}&                  3x_1 & +2x_3 \geq\ 5\\
  & &                             6x_2 & -7x_3 \geq\ 8\\
  & & &                             x_1\in \{0, 1\}\\
  & & &                            x_2 \in \mathbb{Z}\ , 0
\leq x_2 < \infty \\
  & & &              x_3\in \mathcal{S}, \ x_3=0 \ \text{or
} \ 2\leq x_3 < \infty \ \ and\  \ x_3 \in \mathbb{R}\\
  & &                          \\
\end{aligned}
 </span>
  

Firstly we load the MIP example, then use `chgcoltype` to change the type of <span>\( x_3 \)</span>  and use `chglblimit` to specify the nonzero limit of <span>\( x_3 \)</span> .

```
# firstly, load the MIP example to a problem 'problemS'problemS <-load_MIP_example()# change the type of x_3chgcoltype(problemS, 2, 'S')# set the lower bound for semi-continuous variable x_3chgglblimit(problemS, 2, 2)# specify the name of the problemsetprobname(problemS, "MIPExampleWithS")
```


Notice that for setting a semi-continuous variable, we can directly declare its type as ‘S’ when adding the column. Or when we incrementally formulate the problem, we can declare a semi-continuous variable by function `xprs_addcol` or `adcols` and set ‘coltype’ as ‘S’.

Now we solve this example. We see that the solution satisfies the semi-continuous restriction on <span>\( x_3 \)</span> , whose value changed from 1 to 2.

```
# show the problem createdprint(problemS)summary(xprs_optimize(problemS))print(data.frame(Variable =c("x_1", "x_2", "x_3"),Value =getsolution(problemS)$x))
```


```
## XPRESS problem object MIPExampleWithS
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
## 
## Final MIP objective                   :                   12
## Final MIP bound                       :                   12
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     1
## 2      x_2     4
## 3      x_3     2
```


More functions to interact with semi-continuous variables are: `chgbounds`, `chgcoef`, `chgobj`, `delcols` and `getcoltype`.

#### Semi-continuous Integer Variables

Semi-continuous integer variables are decision variables that either have value 0, or an integer value above a specified nonnegative limit. To show how we specify semi-continuous integer when formulating problems, we use the MIP example but change the variable type of <span>\( x_3 \)</span>  from integer to semi-continuous integer, and set the nonzero limit of <span>\( x_3 \)</span>  as 2:

<span> 
\begin{aligned}[t]
  &\min  &       2x_1 & +x_2 + 3x_3\\
  & \text{s.t.}&                  3x_1 & +2x_3 \geq\ 5\\
  & &                             6x_2 & -7x_3 \geq\ 8\\
  & & &                             x_1\in \{0, 1\}\\
  & & &                            x_2 \in \mathbb{Z}\ , 0
\leq x_2 < \infty \\
  & & &               x_3\in \mathcal{R}, \ x_3=0 \ \text{or
} \ 2\leq x_3 < \infty \ and \ x_3 \in \mathbb{Z}\\
  & &                          \\
\end{aligned}
 </span>
  

Firstly, we load the MIP example, then use `chgcoltype` to change the type of <span>\( x_3 \)</span>  and use `chglblimit` to specify the nonzero limit of <span>\( x_3 \)</span> .

```
# firstly, load the MIP example to a problem 'problemR'problemR <-load_MIP_example()# change the type of x_3chgcoltype(problemR, 2, 'R')# set the lower bound for semi-continuous integer variable x_3chgglblimit(problemR, 2, 2)# specify the name of the problemsetprobname(problemR, "MIPExampleWithR")
```


Notice that for setting a semi-continuous integer variable, we can directly declare its type as ‘R’ when adding the column. Or when we incrementally formulate the problem, we can declare a semi-continuous variable by function `xprs_addcol` or `adcols` and set ‘coltype’ as ‘R’.

Now we solve this example. We see that the solution satisfies the semi-continuous integer restriction on <span>\( x_3 \)</span> , whose value changed from 1 to 2.

```
# show the problem createdprint(problemR)summary(xprs_optimize(problemR))print(data.frame(Variable =c("x_1", "x_2", "x_3"),Value =getsolution(problemR)$x))
```


```
## XPRESS problem object MIPExampleWithR
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
## 
## Final MIP objective                   :                   12
## Final MIP bound                       :                   12
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         1 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1     1
## 2      x_2     4
## 3      x_3     2
```


More functions to interact with semi-continuous integer variables are: `chgbounds`, `chgcoef`, `chgobj`, `delcols`, and `getcoltype`.

#### Partial Integer Variables

Partial integer variables are decision variables that have integer values below a specified limit and continuous values above the limit. To show how we specify partial integer variables when formulating problems, we use a modification of the MIP example where we change the variable type of <span>\( x_2 \)</span>  from integer to partial integer, and set the specified limit of <span>\( x_2 \)</span>  as 2:

<span> 
\begin{aligned}[t]
  &\min  &       2x_1 & +x_2 + 3x_3\\
  & \text{s.t.}&                  3x_1 & +2x_3 \geq\ 5\\
  & &                             6x_2 & -7x_3 \geq\ 8\\
  & & &                             x_1\in \{0, 1\}\\
  & & &   x_2 \in \mathcal{P}\ , \ \ x_2\in \mathbb{Z} \ \ \
\text{if} \  0\leq x_2\leq 2, \
          \text{and}\ \  x_2\in \mathbb{R}\  \ \text{if} \  x_2> 2\\
  & & &               x_3\in \mathbb{Z}, \ 0 \leq x_3 <
\infty\\
  & &                          \\
\end{aligned}
 </span>
  

Firstly, we load the MIP example, then use `chgcoltype` to change the type of <span>\( x_2 \)</span>  and use `chglblimit` to specify the nonzero limit of <span>\( x_2 \)</span> .

```
# firstly, load the MIP example to a  problem 'problemP'problemP <-load_MIP_example()# change the type of x_2chgcoltype(problemP, 1, 'P')# set the specified limit for partial integer variable x_2chgglblimit(problemP, 1, 2)# specify the name of the problemsetprobname(problemP, "MIPExampleWithP")
```


Notice that for setting a partial integer variable, we can directly declare its type as ‘P’ when adding the column. Or when we incrementally formulate the problem, we can declare a partial integer variable by function `xprs_addcol` or `adcols` and set ‘coltype’ as ‘P’.

Now we solve this example. We see that the solution satisfies the partial integer restriction on <span>\( x_2 \)</span> , whose value changed from 3 to 2.5.

```
# show the problem createdprint(problemP)summary(xprs_optimize(problemP))print(data.frame(Variable =c("x_1", "x_2", "x_3"),Value =getsolution(problemP)$x))
```


```
## XPRESS problem object MIPExampleWithP
##      2 rows         3 cols        4 elems
##      3 entities      0 sets        0 indicators
##      0 qelems        0 qcelems
##      0 gencons       0 pwlcons
## 
## Final MIP objective                   :                  7.5
## Final MIP bound                       :                  7.5
## Solution time / primaldual integral   :        0s /     0.00%
## Number of solutions found / nodes     :         3 /        1
## MIPSTATUS: 6
##   Variable Value
## 1      x_1   1.0
## 2      x_2   2.5
## 3      x_3   1.0
```


More functions to interact with partial integer variables are: `chgbounds`, `chgobj`, `chgcoef`, `delcols`, and `getcoltype`.

## Chapter 3 R interface reference manual


This chapter provides a list of functions available through the Xpress R interface. For each function, the synopsis and an example are given.

#### addcbafterobjective

_**Purpose:**_

   Declares a callback which will be called after each objective in a multi-objective problem is solved.

_**Synopsis:**_

   `
addcbafterobjective(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The afterobjective callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `afterobjective`.
The afterobjective callback does not have any output arguments.

#### addcbbariteration

_**Purpose:**_

   Declares a barrier iteration callback function, called after each iteration during the interior point algorithm, with the ability to access the current barrier solution/slack/duals or reduced cost values, and to ask barrier to stop.

_**Synopsis:**_

   `
addcbbariteration(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The bariteration callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `bariteration`.
The bariteration callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `action`: Defines a return value controlling barrier:
     * `<0`: continue with the next iteration;
     * `=0`: let barrier decide \(use default stopping criteria\);
     * `1`: barrier stops with status not defined;
     * `2`: barrier stops with optimal status;
     * `3`: barrier stops with dual infeasible status;
     * `4`: barrier stops wih primal infeasible status.


#### addcbbarlog

_**Purpose:**_

   Declares a barrier log callback function, called at each iteration during the interior point algorithm.

_**Synopsis:**_

   `
addcbbarlog(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The barlog callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `barlog`.
The barlog callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.

#### addcbbeforeobjective

_**Purpose:**_

   Declares a callback which will be called before each objective in a multi-objective problem is solved.

_**Synopsis:**_

   `
addcbbeforeobjective(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The beforeobjective callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `beforeobjective`.
The beforeobjective callback does not have any output arguments.

#### addcbchecktime

_**Purpose:**_

   Declares a callback function which is called every time the Optimizer checks if the time limit has been reached.

_**Synopsis:**_

   `
addcbchecktime(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The checktime callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `checktime`.
The checktime callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.

#### addcbchgbranchobject

_**Purpose:**_

   Declares a callback function that will be called after the selection of a MIP entity to branch on.

_**Synopsis:**_

   `
addcbchgbranchobject(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The chgbranchobject callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `chgbranchobject`.
 * `branch`: The candidate branching data selected by the Optimizer. Will be `NULL` if no candidates exist.
The chgbranchobject callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `newbranch`: Optional new branching data to replace the Optimizer's selection.

#### addcbcomputerestart

_**Purpose:**_

   Declares a callback to be called when a solve executed in compute mode needs to be restarted.

_**Synopsis:**_

   `
addcbcomputerestart(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The computerestart callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `computerestart`.
The computerestart callback does not have any output arguments.

#### addcbcutlog

_**Purpose:**_

   Declares a cut log callback function, called each time the cut log is printed.

_**Synopsis:**_

   `
addcbcutlog(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The cutlog callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `cutlog`.
The cutlog callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.

#### addcbcutround

_**Purpose:**_

   Declares a callback function that is called when the Optimizer could separate cutting planes during the branch and bound search.

_**Synopsis:**_

   `
addcbcutround(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The cutround callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `cutround`.
 * `ifxpresscuts`: An integer set to 1 if the Optimizer will apply a round of cuts after this callback. 0 otherwise.
 * `action`: An integer return value that specifies the action the Optimizer should take:
     * `-1`: Continue unchanged. The default action.
     * `0`: No further rounds of cuts should be applied on this node.
     * `1`: The Optimizer should apply one more round of cutting, regardless of the value of `ifxpresscuts`
     * `2`: The Optimizer should process any changes applied during this callback and fire the callback again, but skip any Optimizer cutting.

The cutround callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `action`: An integer return value that specifies the action the Optimizer should take:
     * `-1`: Continue unchanged. The default action.
     * `0`: No further rounds of cuts should be applied on this node.
     * `1`: The Optimizer should apply one more round of cutting, regardless of the value of `ifxpresscuts`
     * `2`: The Optimizer should process any changes applied during this callback and fire the callback again, but skip any Optimizer cutting.


#### addcbdestroymt

_**Purpose:**_

   Declares a destroy MIP thread callback function, called every time a MIP thread is destroyed by the parallel MIP code.

_**Synopsis:**_

   `
addcbdestroymt(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The destroymt callback supports the following input arguments \(in this order\):
 * `cbprob`: The thread problem passed to the callback function.
The destroymt callback does not have any output arguments.

#### addcbgapnotify

_**Purpose:**_

   Declares a gap notification callback, to be called when a MIP solve reaches a predefined target, set using the MIPRELGAPNOTIFY, MIPABSGAPNOTIFY, MIPABSGAPNOTIFYOBJ and/or MIPABSGAPNOTIFYBOUND controls.

_**Synopsis:**_

   `
addcbgapnotify(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The gapnotify callback supports the following input arguments \(in this order\):
 * `cbprob`: The current problem.
 * `relgapnotifytarget`: The value the MIPRELGAPNOTIFY control will be set to after this callback. May be modified within the callback in order to set a new notification target.
 * `absgapnotifytarget`: The value the MIPABSGAPNOTIFY control will be set to after this callback. May be modified within the callback in order to set a new notification target.
 * `absgapnotifyobjtarget`: The value the MIPABSGAPNOTIFYOBJ control will be set to after this callback. May be modified within the callback in order to set a new notification target.
 * `absgapnotifyboundtarget`: The value the MIPABSGAPNOTIFYBOUND control will be set to after this callback. May be modified within the callback in order to set a new notification target.
The gapnotify callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `relgapnotifytarget`: The value the MIPRELGAPNOTIFY control will be set to after this callback.
 * `absgapnotifytarget`: The value the MIPABSGAPNOTIFY control will be set to after this callback.
 * `absgapnotifyobjtarget`: The value the MIPABSGAPNOTIFYOBJ control will be set to after this callback.
 * `absgapnotifyboundtarget`: The value the MIPABSGAPNOTIFYBOUND control will be set to after this callback.

#### addcbgloballog

_**Purpose:**_

   Declares a MIP log callback function, called each time the MIP log is printed.

_**Synopsis:**_

   `
addcbgloballog(prob, cb, prio = 0)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``addcbmiplog``

#### addcbinfnode

_**Purpose:**_

   Declares a user infeasible node callback function, called after the current node has been found to be infeasible during the Branch and Bound search. The callback is also invoked if the current node gets cut off, i.e., if its objective is proven to exceed the current primal bound.

_**Synopsis:**_

   `
addcbinfnode(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The infnode callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `infnode`.
The infnode callback does not have any output arguments.

#### addcbintsol

_**Purpose:**_

   Declares a user integer solution callback function, called every time an integer solution is found by heuristics or during the Branch and Bound search.

_**Synopsis:**_

   `
addcbintsol(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The intsol callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `intsol`.
The intsol callback does not have any output arguments.

#### addcblplog

_**Purpose:**_

   Declares a simplex log callback function which is called after every `LPLOG`iterations of the simplex algorithm.

_**Synopsis:**_

   `
addcblplog(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The lplog callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `lplog`.
The lplog callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.

#### addcbmessage

_**Purpose:**_

   Declares an output callback function, called every time a text line relating to the given problem is output by the Optimizer.

_**Synopsis:**_

   `
addcbmessage(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The message callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function.
 * `msg`: A null terminated character array \(string\) containing the message, which may simply be a new line. The total number of bytes \(including `NUL` terminator\) will not exceed `MAXMESSAGELENGTH`. If a message needs to be truncated to meet this limit, the last four bytes in `msg` are set to "...0".
 * `msgtype`: Indicates the type of output message:
     * `1`: information messages;
A negative value indicates that the Optimizer is about to finish and the buffers should be flushed at this time if the output is being redirected to a file.     * `2`: \(not used\);
     * `3`: warning messages;
     * `4`: error messages.

The message callback does not have any output arguments.

#### addcbmiplog

_**Purpose:**_

   Declares a MIP log callback function, called each time the MIP log is printed.

_**Synopsis:**_

   `
addcbmiplog(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The miplog callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `miplog`.
The miplog callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.

#### addcbmipthread

_**Purpose:**_

   Declares a MIP thread callback function, called every time a MIP worker problem is created by the parallel MIP code.

_**Synopsis:**_

   `
addcbmipthread(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The mipthread callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function.
 * `threadprob`: The new problem for the MIP thread
The mipthread callback does not have any output arguments.

#### addcbnewnode

_**Purpose:**_

   Declares a callback function that will be called every time a new node is created during the branch and bound search.

_**Synopsis:**_

   `
addcbnewnode(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The newnode callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `newnode`.
 * `parentnode`: Unique identifier for the parent of the new node.
 * `node`: Unique identifier assigned to the new node.
 * `branch`: The sequence number of the new node amongst the child nodes of `parentnode`. For regular branches on a MIP entity this will be either `0` or `1`.
The newnode callback does not have any output arguments.

#### addcbnlpcoefevalerror

_**Purpose:**_

   Add a user callback to be called when an evaluation of a coefficient fails during the solve

_**Synopsis:**_

   `
addcbnlpcoefevalerror(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The nlpcoefevalerror callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function.
 * `col`: The column position of the coefficient.
 * `row`: The row position of the coefficient.
The nlpcoefevalerror callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.

#### addcbnodecutoff

_**Purpose:**_

   Declares a user node cutoff callback function, called every time a node is cut off as a result of an improved integer solution being found during the branch and bound search.

_**Synopsis:**_

   `
addcbnodecutoff(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The nodecutoff callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `nodecutoff`.
 * `node`: The node id of the node that is cut off. This id cannot be queried from the CURRENTNODE attribute as for other callbacks since this callback is not invoked in the context of the node being cutoff.
The nodecutoff callback does not have any output arguments.

#### addcbnodelpsolved

_**Purpose:**_

   Declares a callback function, called during the branch and bound search, after the LP relaxation has been solved for the current node, but before any internal cuts and heuristics have been applied.

_**Synopsis:**_

   `
addcbnodelpsolved(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The nodelpsolved callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `nodelpsolved`.
The nodelpsolved callback does not have any output arguments.

#### addcboptnode

_**Purpose:**_

   Declares an optimal node callback function, called during the branch and bound search, after the LP relaxation has been solved for the current node, and after any internal cuts and heuristics have been applied, but before the Optimizer checks if the current node should be branched.

_**Synopsis:**_

   `
addcboptnode(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The optnode callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `optnode`.
The optnode callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `infeasible`: The feasibility status.

#### addcbpreintsol

_**Purpose:**_

   Declares a user integer solution callback function, called when an integer solution is found by heuristics or during the branch and bound search, but before it is accepted by the Optimizer.

_**Synopsis:**_

   `
addcbpreintsol(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The preintsol callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `preintsol`.
 * `soltype`: The type of MIP solution that has been found:
     * `0`: The continuous relaxation solution to the current node of the tree search, which has been found to be integer feasible.
     * `1`: A MIP solution found by a heuristic.
     * `2`: A MIP solution provided by the user.

 * `cutoff`: The new cutoff value that the Optimizer will use if the solution is accepted. If `cutoff` is assigned a value, the new value will be used instead. The cutoff value will not be updated if the solution is rejected.
The preintsol callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `reject`: Set this to 1 if the solution should be rejected.
 * `cutoff`: The new cutoff value that the Optimizer will use if the solution is accepted.

#### addcbprenode

_**Purpose:**_

   Declares a preprocess node callback function, called before the LP relaxation of a node has been optimized, so the solution at the node will not be available.

_**Synopsis:**_

   `
addcbprenode(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The prenode callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `prenode`.
The prenode callback supports the following output arguments:
 * `ret`: An integer that will interrupt the search if non-zero.
 * `infeasible`: The feasibility status.

#### addcbpresolve

_**Purpose:**_

   Declares a callback to be called after presolve has been performed.

_**Synopsis:**_

   `
addcbpresolve(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The presolve callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function.
The presolve callback does not have any output arguments.

#### addcbusersolnotify

_**Purpose:**_

   Declares a callback function to be called each time a solution added by XPRSaddmipsol has been processed.

_**Synopsis:**_

   `
addcbusersolnotify(prob, cb, prio = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer to which the callback is added. 
`cb` | The callback function to add. 
`prio` | The priority of the callback. If multiple callbacks are registered for the same event then they are invoked according to their priority ordering. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Note the general callback conventions:
 * a callback function may return either an integer or a list.
 * if the C callback function has an integer return type then the value returned to the optimizer is the integer value returned or the list's "ret" element \(if it exists\).
 * if the C callback function has output arguments then these arguments are taken from the list that is returned by the callback function.
 * the R callback function will only receive the input arguments of the C callback
The usersolnotify callback supports the following input arguments \(in this order\):
 * `cbprob`: The problem passed to the callback function, `usersolnotify`.
 * `solname`: The string name assigned to the solution when it was loaded into the Optimizer using addmipsol.
The usersolnotify callback does not have any output arguments.

#### addcols

_**Purpose:**_

   Adds columns to the optimizer matrix.

_**Synopsis:**_

   `
addcols(


  prob,


  objcoef = NULL,


  start = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  ncoefs = x_max_vec_length(rowind, rowcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients of the new columns. 
`start` | Integer array of length `ncols` containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`rowind` | Integer array of length `ncoefs` containing the row indices for the elements in each column. 
`rowcoef` | Double array of length `ncoefs` containing the element values. 
`lb` | Double array of length `ncols` containing the lower bounds on the added columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the added columns. 
`ncols` | Number of new columns. 
`ncoefs` | Number of new nonzeros in the added columns. 

_**Return value:**_
The input argument `prob`.

#### addcuts

_**Purpose:**_

   Adds cuts directly to the matrix at the current node.

The cuts will automatically be added to the cut pool. Cuts added to a node will automatically be inherited on any descendant node, unless explicitly deleted with a call to delcuts.

_**Synopsis:**_

   `
addcuts(


  prob,


  cuttype,


  rowtype,


  rhs,


  start,


  colind,


  cutcoef,


  ncuts = x_max_vec_length(cuttype, rowtype, rhs)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cuttype` | Integer array of length `ncuts` containing the user assigned cut types. 
`rowtype` | Character array of length `ncuts` containing the row types:
 * `L`: indicates a `<=` row;
 * `G`: indicates a `>=` row;
 * `E`: indicates an = row.
 
`rhs` | Double array of length `ncuts` containing the right hand side elements for the cuts. 
`start` | Integer array containing offset into the `colind` and `cutcoef` arrays indicating the start of each cut. 
`colind` | Integer array of length `start[ncuts]` containing the column indices in the cuts. 
`cutcoef` | Double array of length `start[ncuts]` containing the matrix values for the cuts. 
`ncuts` | Number of cuts to add. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addgencons

_**Purpose:**_

   Adds one or more general constraints to the problem.

Each general constraint `y = f(x1, ..., xn, c1, ..., cn)`consists of one or more \(input\) columns xi, zero or more constant values ci and a resultant \(output column\) y, different from all xi. General constraints include `maximum`and `minimum`\(arbitrary number of input columns of any type and arbitrary number of input values, at least one total\), `and`and `or`\(at least one binary input column, no constant values, binary resultant\) and `absolute value`\(exactly one input column of arbitrary type, no constant values\).

_**Synopsis:**_

   `
addgencons(


  prob,


  contype,


  resultant,


  colstart,


  colind,


  valstart,


  val,


  ncons = x_max_vec_length(contype, resultant, colstart, valstart),


  ncols = x_max_vec_length(colind),


  nvals = x_max_vec_length(val)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`contype` | Integer array of length `ncons` containing the types of the general constraints:
 * `_GENCONS_MAX (0)`: indicates a `maximum` constraint;
 * `_GENCONS_MIN (1)`: indicates a `minimum` constraint;
 * `_GENCONS_AND (2)`: indicates an `and` constraint.
 * `_GENCONS_OR (3)`: indicates an `or` constraint;
 * `_GENCONS_ABS (4)`: indicates an `absolute value` constraint.
 
`resultant` | Integer array of length `ncons` containing the indices of the output variables of the general constraints. 
`colstart` | Integer array of length `ncons` containing the start index of each general constraint in the `colind` array. 
`colind` | Integer array of length `ncols` containing the input variables in all general constraints. 
`valstart` | Integer array of length `ncons` containing the start index of each general constraint in the `val` array \(may be `NULL` if `nvals = 0`\). 
`val` | Double array of length `nvals` containing the constant values in all general constraints \(may be `NULL` if `nvals = 0`\). 
`ncons` | The number of general constraints to add. 
`ncols` | The total number of input variables in general constraints that should be added. 
`nvals` | The total number of constant values in general constraints that should be added. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addmanagedcuts

_**Purpose:**_

   Adds cuts to the Optimizer's internal cut pool from within the cutround callback set by addcbcutround.

The cuts will be added to an internal pool of cuts managed by the Optimizer. The Optimizer will use internal priorities to dynamically load violated cuts from this pool into branch-and-bound node problems and remove inactive cuts. Cuts can be either local or global. Cuts flagged as local are assumed to be valid only for the the current node of the branch-and-bound search or any of its descendants. Global cuts are assumed to be valid for the whole problem and might be used on any node of the branch-and-bound search tree. The cuts should be formulated in the original space of variables and will automatically be presolved.

_**Synopsis:**_

   `
addmanagedcuts(


  prob,


  globalvalid,


  rowtype,


  rhs,


  start,


  colind,


  cutcoef,


  ncuts = x_max_vec_length(rowtype, rhs)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`globalvalid` | Nonzero if the cuts should be assumed to be valid for the whole problem. 
`rowtype` | Character array of length `ncuts` containing the row types:
 * `L`: indicates a `<=` row;
 * `G`: indicates a `>=` row;
 * `E`: indicates an = row.
 
`rhs` | Double array of length `ncuts` containing the right hand side elements for the cuts. 
`start` | Integer array containing offset into the `colind` and `cutcoef` arrays indicating the start of each cut. 
`colind` | Integer array of length `start[ncuts]` containing the column indices in the cuts. 
`cutcoef` | Double array of length `start[ncuts]` containing the matrix values for the cuts. 
`ncuts` | Number of cuts to add. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addmipsol

_**Purpose:**_

   Adds a new feasible, infeasible or partial MIP solution for the problem to the Optimizer.

_**Synopsis:**_

   `
addmipsol(


  prob,


  solval,


  colind = NULL,


  name = "",


  length = x_max_vec_length(solval, colind)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`solval` | Double array of length `length` containing solution values. 
`colind` | Optional integer array of length `length` containing column indices from `0` to INPUTCOLS `-1`, for the solution values provided in `solval`. 
`name` | An optional name to associate with the solution. 
`length` | Number of columns for which a value is provided. 

_**Return value:**_
The input argument `prob`.

#### addnames

_**Purpose:**_

   When a model is loaded, the rows, columns, sets, piecewise linear and general constraints of the model may not have names associated with them.

This may not be important as the rows, columns, sets, piecewise linear and general constraints can be referred to by their sequence numbers. However, if you wish row, column, set, piecewise linear and general constraint names to appear in the ASCII solutions files, the names for a range of rows/columns/... can be added with `addnames`.

_**Synopsis:**_

   `
addnames(prob, type, names, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`type` | 
 * `_NAMES_ROW`: `(=1)` for row names;
 * `_NAMES_COLUMN`: `(=2)` for column names;
 * `_NAMES_SET`: `(=3)` for set names;
 * `_NAMES_PWLCONS`: `(=4)` for piecewise linear constraint names;
 * `_NAMES_GENCONS`: `(=5)` for general constraint names;
 * `_NAMES_OBJECTIVE`: `(=6)` for objective names.
 
`names` | Character buffer containing the null-terminated string names. 
`first` | Start of the range of rows, columns, sets, piecewise linear constraints, general constraints or objectives. 
`last` | End of the range of rows, columns, sets, piecewise linear constraints, general constraints or objectives. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addobj

_**Purpose:**_

   Appends an objective function with the given coefficients to a multi-objective problem.

The weight and priority of the objective are set to the given values.

_**Synopsis:**_

   `
addobj(


  prob,


  colind,


  objcoef,


  priority = 0,


  weight = 1,


  ncols = x_max_vec_length(colind, objcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the indices of the columns whose objective coefficients will change. 
`objcoef` | Double array of length `ncols` giving the new objective function coefficients. 
`priority` | An integer defining the relative priority for the new objective \(only relevant for multi-objective problems\). 
`weight` | A double defining the weight for the new objective \(only relevant for multi-objective problems\). 
`ncols` | Number of objective function coefficient elements to add. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addpwlcons

_**Purpose:**_

   Adds one or more piecewise linear constraints to the problem.

Each piecewise linear constraint `y = f(x)`consists of an \(input\) column x, a \(different\) resultant \(output column\) y and a piecewise linear function f. The piecewise linear function f is described by at least two breakpoints, which are given as combinations of x- and y-values. Discontinuous piecewise linear functions are supported, in this case both the left and right limit at a given point need to be entered as breakpoints. To differentiate between left and right limit, the breakpoints need to be given as a list with non-decreasing x-values.

_**Synopsis:**_

   `
addpwlcons(


  prob,


  colind,


  resultant,


  start,


  xval,


  yval,


  npwls = x_max_vec_length(colind, resultant, start),


  npoints = x_max_vec_length(xval, yval)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `npwls` containing the indices of the input variables x of the piecewise linear functions. 
`resultant` | Integer array of length `npwls` containing the indices of the output variables y of the piecewise linear functions. 
`start` | Integer array of length `npwls` containing the start index of each piecewise linear constraint in the `xval` and `yval` arrays. 
`xval` | Double array of length `npoints` containing the x-values of the breakpoints. 
`yval` | Double array of length `npoints` containing the y-values of the breakpoints. 
`npwls` | The number of piecewise linear constraints to add. 
`npoints` | The total number of breakpoints of all piecewise linear constraints that should be added. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addqmatrix

_**Purpose:**_

   Adds a new quadratic matrix into a row defined by triplets.

_**Synopsis:**_

   `
addqmatrix(


  prob,


  row,


  rowqcol1,


  rowqcol2,


  rowqcoef,


  ncoefs = x_max_vec_length(rowqcol1, rowqcol2, rowqcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Index of the row where the quadratic matrix is to be added. 
`rowqcol1` | First index in the triplets. 
`rowqcol2` | Second index in the triplets. 
`rowqcoef` | Coefficients in the triplets. 
`ncoefs` | Number of triplets used to define the quadratic matrix. 

_**Return value:**_
The input argument `prob`.

#### addrows

_**Purpose:**_

   Adds rows to the optimizer matrix.

_**Synopsis:**_

   `
addrows(


  prob,


  rowtype,


  rhs,


  rng = NULL,


  start = NULL,


  colind = NULL,


  rowcoef = NULL,


  nrows = x_max_vec_length(rowtype, rhs, rng),


  ncoefs = x_max_vec_length(colind, rowcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowtype` | Character array of length nrows containing the row types:
 * `L`: indicates a `<=` row;
 * `G`: indicates `>=` row;
 * `E`: indicates an = row.
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side elements. 
`rng` | Double array of length `nrows` containing the row range elements. 
`start` | Integer array of length `nrows` containing the offsets in the `colind` and `rowcoef` arrays of the start of the elements for each row. 
`colind` | Integer array of length `ncoefs` containing the \(contiguous\) column indices for the elements in each row. 
`rowcoef` | Double array of length `ncoefs` containing the \(contiguous\) element values. 
`nrows` | Number of new rows. 
`ncoefs` | Number of new nonzeros in the added rows. 

_**Return value:**_
The input argument `prob`.

#### addsetnames

_**Purpose:**_

   \*\*Deprecated\*\* Use addnames instead.

When a model with MIP entities is loaded, any special ordered sets may not have names associated with them. If you wish names to appear in the ASCII solutions files, the names for a range of sets can be added with this function.

_**Synopsis:**_

   `
addsetnames(prob, names, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`names` | Character buffer containing the null-terminated string names. 
`first` | Start of the range of sets. 
`last` | End of the range of sets. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### addsets

_**Purpose:**_

   Allows sets to be added to the problem after passing it to the Optimizer using the input routines.

_**Synopsis:**_

   `
addsets(


  prob,


  settype,


  start,


  colind,


  refval,


  nsets = x_max_vec_length(settype),


  nelems = x_max_vec_length(colind, refval)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`settype` | Character array of length nsets containing the set types:
 * `1`: indicates a SOS1;
 * `2`: indicates a SOS2;
 
`start` | Integer array of length `nsets` containing the offsets in the `colind` and `refval` arrays of the start of the elements for each set. 
`colind` | Integer array of length `nelems` containing the \(contiguous\) column indices for the elements in each set. 
`refval` | Double array of length `nelems` containing the \(contiguous\) reference values. 
`nsets` | Number of new sets. 
`nelems` | Number of new nonzeros in the added sets. 

_**Return value:**_
The input argument `prob`.

#### alter

_**Purpose:**_

   \*\*Deprecated\*\* To change matrix coefficients, use chgmcoef.

To change column bounds, use chgbounds. To change constraint right-hand side values, use chgrhs. To change constraint types, use chgrowtype. To change objective coefficients, use chgobj. Alters or changes matrix elements, right hand sides and constraint senses in the current problem.

_**Synopsis:**_

   `
alter(prob, filename)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters specifying the file to be read. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### basisstability

_**Purpose:**_

   Calculates various measures for the stability of the current basis, including the basis condition number.

_**Synopsis:**_

   `
basisstability(prob, type, norm, scaled)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`type` | 
 * `0`: Condition number of the basis.
 * `1`: Stability measure for the solution relative to the current basis.
 * `2`: Stability measure for the duals relative to the current basis.
 * `3`: Stability measure for the right hand side relative to the current basis.
 * `4`: Stability measure for the basic part of the objective relative to the current basis.
 
`norm` | 
 * `0`: Use the infinity norm.
 * `1`: Use the 1 norm.
 * `2`: Use the Euclidian norm for vectors, and the Frobenius norm for matrices.
 
`scaled` | If the stability values are to be calculated in the scaled, or the unscaled matrix. 

_**Return value:**_
The calculated value.

#### beginlicensing

_**Purpose:**_

   Wraps callable C library function XPRSbeginlicensing.

Please refer to the OEM guide for details.

_**Synopsis:**_

   `
beginlicensing()` 


#### bndsa

_**Purpose:**_

   Returns upper and lower sensitivity ranges for specified variables' lower and upper bounds.

If the bounds are varied within these ranges the current basis remains optimal and feasible.

_**Synopsis:**_

   `
bndsa(prob, colind, ncols = x_max_vec_length(colind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the indices of the columns whose bounds' ranges are required. 
`ncols` | Number of variables whose sensitivity is sought. 

_**Return value:**_
A list with the following elements:
 * `lblower`: Double array of length `ncols` containing the variable lower bound lower range values.
 * `lbupper`: Double array of length `ncols` containing the variable lower bound upper range values.
 * `ublower`: Double array of length `ncols` containing the variable upper bound lower range values.
 * `ubupper`: Double array of length `ncols` containing the variable upper bound upper range values.


_**Further information:**_
Please refer to the C documentation for more details.

#### bo_addbounds

_**Purpose:**_

   Adds new bounds to a branch of a user branching object.

_**Synopsis:**_

   `
bo_addbounds(


  bo,


  branch,


  bndtype,


  colind,


  bndval,


  nbounds = x_max_vec_length(bndtype, colind, bndval)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to modify. 
`branch` | The number of the branch to add the new bounds for. 
`bndtype` | Character array of length `nbounds` indicating the type of bounds to add:
 * `L`: Lower bound.
 * `U`: Upper bound.
 
`colind` | Integer array of length `nbounds` containing the column indices for the new bounds. 
`bndval` | Double array of length `nbounds` giving the bound values. 
`nbounds` | Number of new bounds to add. 

_**Return value:**_
The input argument `bo`.

#### bo_addbranches

_**Purpose:**_

   Adds new, empty branches to a user defined branching object.

_**Synopsis:**_

   `
bo_addbranches(bo, nbranches)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to modify. 
`nbranches` | Number of new branches to create. 

_**Return value:**_
The input argument `bo`.

#### bo_addcuts

_**Purpose:**_

   Adds stored user cuts as new constraints to a branch of a user branching object.

_**Synopsis:**_

   `
bo_addcuts(bo, branch, cutind, ncuts = x_max_vec_length(cutind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to modify. 
`branch` | The number of the branch to add the cuts for. 
`cutind` | Array of length `ncuts` containing the user cut objects that should be added to the branch. 
`ncuts` | Number of cuts to add. 

_**Return value:**_
The input argument `bo`.

#### bo_addrows

_**Purpose:**_

   Adds new constraints to a branch of a user branching object.

_**Synopsis:**_

   `
bo_addrows(


  bo,


  branch,


  rowtype,


  rhs,


  start,


  colind,


  rowcoef,


  nrows = x_max_vec_length(rowtype, rhs, start),


  ncoefs = x_max_vec_length(colind, rowcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to modify. 
`branch` | The number of the branch to add the new constraints for. 
`rowtype` | Character array of length `nrows` indicating the type of constraints to add:
 * `L`: Less than type.
 * `G`: Greater than type.
 * `E`: Equality type.
 
`rhs` | Double array of length `nrows` containing the right hand side values. 
`start` | Integer array of length `nrows` containing the offsets of the `colind` and `rowcoef` arrays of the start of the non zero coefficients in the new constraints. 
`colind` | Integer array of length `ncoefs` containing the column indices for the non zero coefficients. 
`rowcoef` | Double array of length `ncoefs` containing the non zero coefficient values. 
`nrows` | Number of new constraints to add. 
`ncoefs` | Number of non-zero coefficients in all new constraints. 

_**Return value:**_
The input argument `bo`.

#### bo_create

_**Purpose:**_

   Creates a new user defined branching object for the Optimizer to branch on.

This function should be called only from within one of the callback functions set by addcboptnode, addcbchgbranchobject, or addcbpreintsol \(only if the `soltype`is 0\).

_**Synopsis:**_

   `
bo_create(prob, isoriginal)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem structure that the branching object should be created for. 
`isoriginal` | If the branching object will be set up for the original matrix, which determines how column indices are interpreted when adding bounds and rows to the object:
 * `0`: Column indices should refer to the current \(presolved\) node problem.
 * `1`: Column indices should refer to the original matrix.
 

_**Return value:**_
The new object.

_**Further information:**_
Please refer to the C documentation for more details.

#### bo_destroy

_**Purpose:**_

   Frees all memory for a user branching object, when the object was not stored with the Optimizer.

_**Synopsis:**_

   `
bo_destroy(bo)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to free. 

_**Return value:**_
The input argument `bo`.

#### bo_getbounds

_**Purpose:**_

   Returns the bounds for a branch of a user branching object.

_**Synopsis:**_

   `
bo_getbounds(bo, branch)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The branching object to inspect. 
`branch` | The number of the branch to get the bounds for. 

_**Return value:**_
A list with the following elements:
 * `nbounds`: The number of bounds for the given branch.
 * `bndtype`: Character array of length `maxbounds` containing the types of bounds:
     * `L`: Lower bound.
     * `U`: Upper bound.

 * `colind`: Integer array of length `maxbounds` containing the column indices.
 * `bndval`: Double array of length `maxbounds` containing the bound values.


#### bo_getbranches

_**Purpose:**_

   Returns the number of branches of a branching object.

_**Synopsis:**_

   `
bo_getbranches(bo)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to inspect. 

_**Return value:**_
The number of branches.

#### bo_getid

_**Purpose:**_

   Returns the unique identifier assigned to a branching object.

_**Synopsis:**_

   `
bo_getid(bo)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bo` | A branching object. 

_**Return value:**_
The identifier.

#### bo_getlasterror

_**Purpose:**_

   Returns the last error encountered during a call to the given branch object.

_**Synopsis:**_

   `
bo_getlasterror(bo)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bo` | The branch object. 

_**Return value:**_
A list with the following elements:
 * `msgcode`: The error code.
 * `msg`: The last error message relating to the given branching object.


#### bo_getrows

_**Purpose:**_

   Returns the constraints for a branch of a user branching object.

_**Synopsis:**_

   `
bo_getrows(bo, branch)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object to inspect. 
`branch` | The number of the branch to get the constraints from. 

_**Return value:**_
A list with the following elements:
 * `nrows`: The number of rows.
 * `ncoefs`: The number of non zero coefficients in the constraints.
 * `rowtype`: Character array of length `maxrows` containing the types of the rows:
     * `L`: Less than type.
     * `G`: Greater than type.
     * `E`: Equality type.

 * `rhs`: Double array of length `maxrows` containing the right hand side values.
 * `start`: Integer array of length `maxrows` containing the offsets of the `colind` and `rowcoef` arrays of the start of the non zero coefficients in the returned constraints.
 * `colind`: Integer array of length `maxcoefs` containing the column indices for the non zero coefficients.
 * `rowcoef`: Double array of length `maxcoefs` containing the non zero coefficient values.


#### bo_setpreferredbranch

_**Purpose:**_

   Specifies which of the child nodes corresponding to the branches of the object should be explored first.

_**Synopsis:**_

   `
bo_setpreferredbranch(bo, branch)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object. 
`branch` | The number of the branch to mark as preferred. 

_**Return value:**_
The input argument `bo`.

#### bo_setpriority

_**Purpose:**_

   Sets the priority value of a user branching object.

_**Synopsis:**_

   `
bo_setpriority(bo, priority)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`bo` | The user branching object. 
`priority` | The new priority value to assign to the branching object, which must be a number from 0 to 1000. 

_**Return value:**_
The input argument `bo`.

#### bo_store

_**Purpose:**_

   Adds a new user branching object to the Optimizer's list of candidates for branching.

This function is available only through the callback functions set by addcboptnode or addcbpreintsol \(if the `soltype`is 0\).

_**Synopsis:**_

   `
bo_store(bo)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bo` | The new user branching object to store. 

_**Return value:**_
The returned status from checking the provided branching object:
 * `0`: The object was accepted successfully.
The object was not added to the candidate list if a non zero status is returned. * `1`: Failed to presolve the object due to dual reductions in presolve.
 * `2`: Failed to presolve the object due to duplicate column reductions in presolve.
 * `3`: The object contains an empty branch.
 * `4`: Failed to presolve the object due to presolve operations requiring relaxation of a row.
 * `5`: Failed to presolve the object due to it becoming nonlinear due to nonlinear eliminations.


_**Further information:**_
Please refer to the C documentation for more details.

#### bo_validate

_**Purpose:**_

   Verifies that a given branching object is valid for branching on the current branch-and-bound node of a MIP solve.

The function will check that all branches are non-empty, and if required, verify that the branching object can be presolved.

_**Synopsis:**_

   `
bo_validate(bo)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bo` | A branching object. 

_**Return value:**_
The returned status from checking the provided branching object:
 * `0`: The object is acceptable.
 * `1`: Failed to presolve the object due to dual reductions in presolve.
 * `2`: Failed to presolve the object due to duplicate column reductions in presolve.
 * `3`: The object contains an empty branch.
 * `4`: Failed to presolve the object due to presolve operations requiring relaxation of a row.
 * `5`: Failed to presolve the object due to it becoming nonlinear due to nonlinear eliminations.


_**Further information:**_
Please refer to the C documentation for more details.

#### calcobjective

_**Purpose:**_

   Calculates the objective value of a given solution.

_**Synopsis:**_

   `
calcobjective(prob, solution)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`solution` | Double array of length COLS that holds the solution. 

_**Return value:**_
The calculated objective value.

#### calcobjn

_**Purpose:**_

   Calculates the objective value of the given objective function in a multi-objective problem.

_**Synopsis:**_

   `
calcobjn(prob, objidx, solution = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective function to calculate. 
`solution` | Double array of length `COLS` that holds the solution. 

_**Return value:**_
The calculated objective value.

#### calcreducedcosts

_**Purpose:**_

   Calculates the reduced cost values for a given \(row\) dual solution.

_**Synopsis:**_

   `
calcreducedcosts(prob, duals, solution = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`duals` | Double array of length `ORIGINALROWS` that holds the dual solution to calculate the reduced costs for. 
`solution` | Double array of length `ORIGINALCOLS` that holds the primal solution. 

_**Return value:**_
Double array of length `ORIGINALCOLS`containing the calculated reduced costs.

#### calcslacks

_**Purpose:**_

   Calculates the row slack values for a given solution.

_**Synopsis:**_

   `
calcslacks(prob, solution)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`solution` | Double array of length `ORIGINALCOLS` that holds the solution to calculate the slacks for. 

_**Return value:**_
Double array of length `ORIGINALROWS`containing the calculated row slacks.

#### calcsolinfo

_**Purpose:**_

   Calculates the required property of a solution, like maximum infeasibility of a given primal and dual solution.

_**Synopsis:**_

   `
calcsolinfo(prob, property, solution = NULL, duals = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`property` | Defined the property to be calculated.
 * `_SOLINFO_ABSPRIMALINFEAS`: the calculated maximum absolute primal infeasibility is returned.
 * `_SOLINFO_RELPRIMALINFEAS`: the calculated maximum relative primal infeasibility is returned.
 * `_SOLINFO_ABSDUALINFEAS`: the calculated maximum absolute dual infeasibility is returned.
 * `_SOLINFO_RELDUALINFEAS`: the calculated maximum relative dual infeasibility is returned.
 * `_SOLINFO_MAXMIPFRACTIONAL`: the calculated maximum absolute MIP fractionality or SOS infeasibility.
 * `_SOLINFO_ABSMIPINFEAS`: the calculated maximum absolute MIP infeasibility \(including delayed rows, indicators, general and piecewise linear constraints\) is returned.
 * `_SOLINFO_RELMIPINFEAS`: the calculated maximum relative MIP infeasibility \(including delayed rows, indicators, general and piecewise linear constraints\) is returned.
 
`solution` | Double array of length `ORIGINALCOLS` that holds the solution. 
`duals` | Double array of length `ORIGINALROWS` that holds the dual solution. 

_**Return value:**_
The calculated value.

#### chgbounds

_**Purpose:**_

   Used to change the bounds on columns in the matrix.

_**Synopsis:**_

   `
chgbounds(


  prob,


  colind,


  bndtype,


  bndval,


  nbounds = x_max_vec_length(colind, bndtype, bndval)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of size `nbounds` containing the indices of the columns on which the bounds will change. 
`bndtype` | Character array of length `nbounds` indicating the type of bound to change:
 * `U`: indicates change the upper bound;
 * `L`: indicates change the lower bound;
 * `B`: indicates change both bounds, i.e. fix the column.
 
`bndval` | Double array of length `nbounds` giving the new bound values. 
`nbounds` | Number of bounds to change. 

_**Return value:**_
The input argument `prob`.

#### chgcoef

_**Purpose:**_

   Used to change a single coefficient in the matrix.

If the coefficient does not already exist, a new coefficient will be added to the matrix. If many coefficients are being added to a row of the matrix, it may be more efficient to delete the old row of the matrix and add a new row.

_**Synopsis:**_

   `
chgcoef(prob, row, col, coef)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Row index for the coefficient. 
`col` | Column index for the coefficient. 
`coef` | New value for the coefficient. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### chgcoltype

_**Purpose:**_

   Used to change the type of a specified set of columns in the matrix.

_**Synopsis:**_

   `
chgcoltype(prob, colind, coltype, ncols = x_max_vec_length(colind, coltype))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the indices of the columns. 
`coltype` | Character array of length `ncols` giving the new column types:
 * `C`: indicates a continuous column;
 * `B`: indicates a binary column;
 * `I`: indicates an integer column.
 * `S`: indicates a semicontinuous column. The semicontinuous lower bound will be set to `1.0`.
 * `R`: indicates a semiinteger column. The semiinteger lower bound will be set to `1.0`.
 * `P`: indicates a partial integer column. The partial integer limit will be set to `1.0`.
 
`ncols` | Number of columns to change. 

_**Return value:**_
The input argument `prob`.

#### chgglblimit

_**Purpose:**_

   Used to change semi-continuous or semi-integer lower bounds, or upper limits on partial integers.

_**Synopsis:**_

   `
chgglblimit(prob, colind, limit, ncols = x_max_vec_length(colind, limit))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of size `ncols` containing the indices of the semi-continuous, semi-integer or partial integer columns that should have their limits changed. 
`limit` | Double array of length `ncols` giving the new limit values. 
`ncols` | Number of column limits to change. 

_**Return value:**_
The input argument `prob`.

#### chgmcoef

_**Purpose:**_

   Used to change multiple coefficients in the matrix.

If any coefficient does not already exist, it will be added to the matrix. If many coefficients are being added to a row of the matrix, it may be more efficient to delete the old row of the matrix and add a new one.

_**Synopsis:**_

   `
chgmcoef(


  prob,


  rowind,


  colind,


  rowcoef,


  ncoefs = x_max_vec_length(rowind, colind, rowcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `ncoefs` containing the row indices of the coefficients to be changed. 
`colind` | Integer array of length `ncoefs` containing the column indices of the coefficients to be changed. 
`rowcoef` | Double array of length `ncoefs` containing the new coefficient values. 
`ncoefs` | Number of new coefficients. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### chgmqobj

_**Purpose:**_

   Used to change multiple quadratic coefficients in the objective function.

If any of the coefficients does not exist already, new coefficients will be added to the objective function.

_**Synopsis:**_

   `
chgmqobj(


  prob,


  objqcol1,


  objqcol2,


  objqcoef,


  ncoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objqcol1` | Integer array of size `ncoefs` containing the column index of the first variable in each quadratic term. 
`objqcol2` | Integer array of size `ncoefs` containing the column index of the second variable in each quadratic term. 
`objqcoef` | New values for the coefficients. 
`ncoefs` | The number of coefficients to change. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### chgobj

_**Purpose:**_

   Used to change the objective function coefficients.

_**Synopsis:**_

   `
chgobj(prob, colind, objcoef, ncols = x_max_vec_length(colind, objcoef))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the indices of the columns whose objective coefficients will change. 
`objcoef` | Double array of length `ncols` giving the new objective function coefficients. 
`ncols` | Number of objective function coefficient elements to change. 

_**Return value:**_
The input argument `prob`.

#### chgobjn

_**Purpose:**_

   Modifies one or more coefficients of an objective function in a multi-objective problem.

If the objective already exists, any coefficients not present in the `colind`and `objcoef`arrays will unchanged. If the objective does not exist, it will be added to the problem.

_**Synopsis:**_

   `
chgobjn(


  prob,


  objidx,


  colind,


  objcoef,


  ncols = x_max_vec_length(colind, objcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective function to add or modify. 
`colind` | Integer array of length `ncols` containing the indices of the columns whose objective coefficients will change. 
`objcoef` | Double array of length `ncols` giving the new objective function coefficients. 
`ncols` | Number of objective function coefficient elements to change. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### chgobjsense

_**Purpose:**_

   Changes the problem's objective function sense to minimize or maximize.

_**Synopsis:**_

   `
chgobjsense(prob, objsense)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objsense` | `OBJ_MINIMIZE` to change into a minimization, or `OBJ_MAXIMIZE` to change into a maximization problem. 

_**Return value:**_
The input argument `prob`.

#### chgqobj

_**Purpose:**_

   Used to change a single quadratic coefficient in the objective function corresponding to the variable pair `(objqcol1,objqcol2)`of the Hessian matrix.

_**Synopsis:**_

   `
chgqobj(prob, objqcol1, objqcol2, objqcoef)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objqcol1` | Column index for the first variable in the quadratic term. 
`objqcol2` | Column index for the second variable in the quadratic term. 
`objqcoef` | New value for the coefficient in the quadratic Hessian matrix. 

_**Return value:**_
The input argument `prob`.

#### chgqrowcoeff

_**Purpose:**_

   Changes a single quadratic coefficient in a row.

_**Synopsis:**_

   `
chgqrowcoeff(prob, row, rowqcol1, rowqcol2, rowqcoef)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Index of the row where the quadratic matrix is to be changed. 
`rowqcol1` | First index of the coefficient to be changed. 
`rowqcol2` | Second index of the coefficient to be changed. 
`rowqcoef` | The new coefficient. 

_**Return value:**_
The input argument `prob`.

#### chgrhs

_**Purpose:**_

   Used to change righthand side values of the problem.

_**Synopsis:**_

   `
chgrhs(prob, rowind, rhs, nrows = x_max_vec_length(rowind, rhs))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `nrows` containing the indices of the rows on which the right hand side values will change. 
`rhs` | Double array of length `nrows` giving the right hand side values. 
`nrows` | Number of right hand side values to change. 

_**Return value:**_
The input argument `prob`.

#### chgrhsrange

_**Purpose:**_

   Used to change the range for a row of the problem matrix.

_**Synopsis:**_

   `
chgrhsrange(prob, rowind, rng, nrows = x_max_vec_length(rowind, rng))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `nrows` containing the indices of the rows on which the range elements will change. 
`rng` | Double array of length `nrows` giving the range values. 
`nrows` | Number of range elements to change. 

_**Return value:**_
The input argument `prob`.

#### chgrowtype

_**Purpose:**_

   Used to change the type of a row in the matrix.

_**Synopsis:**_

   `
chgrowtype(prob, rowind, rowtype, nrows = x_max_vec_length(rowind, rowtype))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `nrows` containing the indices of the rows. 
`rowtype` | Character array of length `nrows` giving the new row types:
 * `L`: indicates a `<=` row;
 * `E`: indicates an = row;
 * `G`: indicates a `>=` row;
 * `R`: indicates a range row;
 * `N`: indicates a free row.
 
`nrows` | Number of rows to change. 

_**Return value:**_
The input argument `prob`.

#### chk_min_length

_**Purpose:**_

   Check that an array has at least a certain length

Returns TRUE if the array has the required length, or if the array is optional and NULL

_**Synopsis:**_

   `
chk_min_length(arr, expected_len, is_optional = FALSE)` 


#### clearrowflags

_**Purpose:**_

   Clears extra information attached to a range of rows.

_**Synopsis:**_

   `
clearrowflags(prob, flags, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem 
`flags` | Integer array of length `last-first+1` including type of extra information to remove \(see below\) 
`first` | First row index to be checked 
`last` | Last row index to be checked 

_**Return value:**_
The input argument `prob`.

#### copycallbacks

_**Purpose:**_

   Copies callback functions defined for one problem to another.

_**Synopsis:**_

   `
copycallbacks(dest, src)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The problem to which the callbacks are copied. 
`src` | The problem from which the callbacks are copied. 

_**Return value:**_
The input argument `dest`.

#### copycontrols

_**Purpose:**_

   Copies controls defined for one problem to another.

_**Synopsis:**_

   `
copycontrols(dest, src)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The problem to which the controls are copied. 
`src` | The problem from which the controls are copied. 

_**Return value:**_
The input argument `dest`.

#### copyprob

_**Purpose:**_

   Copies information defined for one problem to another.

_**Synopsis:**_

   `
copyprob(dest, src, name)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The new problem pointer to which information is copied. 
`src` | The old problem pointer from which information is copied. 
`name` | A string of up to 1024 characters including `NULL` terminator containing the name for the problem copy. 

_**Return value:**_
The input argument `dest`.

#### createprob

_**Purpose:**_

   Sets up a new problem within the Optimizer.

_**Synopsis:**_

   `
createprob()` 


_**Return value:**_
The new problem.

#### crossoverlpsol

_**Purpose:**_

   Provides a basic optimal solution for a given solution of an LP problem.

This function behaves like the crossover after the barrier algorithm.

_**Synopsis:**_

   `
crossoverlpsol(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The status. The status is one of:
 * `0`: The crossover is successful.
 * `1`: The crossover is not performed because the problem has no solution.


_**Further information:**_
Please refer to the C documentation for more details.

#### delcols

_**Purpose:**_

   Delete columns from a matrix.

_**Synopsis:**_

   `
delcols(prob, colind, ncols = x_max_vec_length(colind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the columns to delete. 
`ncols` | Number of columns to delete. 

_**Return value:**_
The input argument `prob`.

#### delcpcuts

_**Purpose:**_

   During the branch and bound search, cuts are stored in the cut pool to be applied at descendant nodes.

These cuts may be removed from a given node using delcuts, but if this is to be applied in a large number of cases, it may be preferable to remove the cut completely from the cut pool. This is achieved using `delcpcuts`.

_**Synopsis:**_

   `
delcpcuts(


  prob,


  cuttype = 0,


  interp = -1,


  cutind = NULL,


  ncuts = x_max_vec_length(cutind)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cuttype` | User defined cut type to match against. 
`interp` | Way in which the cut `cuttype` is interpreted:
 * `-1`: match all cut types;
 * `1`: treat cut types as numbers;
 * `2`: treat cut types as bit-vectors \(compare Section \) - delete if any bit matches any bit set in `cuttype`;
 * `3`: treat cut types as bit-vectors \(compare Section \) - delete if all bits match those set in `cuttype`.
 
`cutind` | Array of length `ncuts` containing the cuts which are to be deleted. 
`ncuts` | The number of cuts to delete. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### delcuts

_**Purpose:**_

   Deletes cuts from the matrix at the current node.

Cuts from the parent node which have been automatically restored may be deleted as well as cuts added to the current node using addcuts or loadcuts. The cuts to be deleted can be specified in a number of ways. If a cut is ruled out by any one of the criteria it will not be deleted.

_**Synopsis:**_

   `
delcuts(


  prob,


  basis,


  cuttype = 0,


  interp = -1,


  delta = -Inf,


  ncuts = -1,


  cutind = NULL


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`basis` | Ensures the basis will be valid if set to `1`. 
`cuttype` | User defined type of the cut to be deleted. 
`interp` | Way in which the cut `cuttype` is interpreted:
 * `-1`: match all cut types;
 * `1`: treat cut types as numbers;
 * `2`: treat cut types as bit-vectors \(compare Section \) - delete if any bit matches any bit set in `cuttype`;
 * `3`: treat cut types as bit-vectors \(compare Section \) - delete if all bits match those set in `cuttype`.
 
`delta` | Only delete cuts with an absolute slack value greater than `delta`. 
`ncuts` | Number of cuts to drop if a list of cuts is provided. 
`cutind` | Array of length `ncuts` containing the cuts which are to be deleted. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### delgencons

_**Purpose:**_

   Delete general constraints from a problem.

_**Synopsis:**_

   `
delgencons(prob, conind, ncons = x_max_vec_length(conind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`conind` | An integer array of length `ncons` containing the general constraints to delete. 
`ncons` | Number of general constraints to delete. 

_**Return value:**_
The input argument `prob`.

#### delindicators

_**Purpose:**_

   Delete indicator constraints.

This turns the specified rows into normal rows \(not controlled by indicator variables\).

_**Synopsis:**_

   `
delindicators(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the range. 
`last` | Last row in the range \(inclusive\). 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### delobj

_**Purpose:**_

   Removes an objective function from the problem.

Any objectives with `index > objidx`will be shifted down.

_**Synopsis:**_

   `
delobj(prob, objidx)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective to remove. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### delpwlcons

_**Purpose:**_

   Delete piecewise linear constraints from a problem.

_**Synopsis:**_

   `
delpwlcons(prob, pwlind, npwls = x_max_vec_length(pwlind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`pwlind` | An integer array of length `npwls` containing the piecewise linear constraints to delete. 
`npwls` | Number of piecewise linear constraints to delete. 

_**Return value:**_
The input argument `prob`.

#### delqmatrix

_**Purpose:**_

   Deletes the quadratic part of a row or of the objective function.

_**Synopsis:**_

   `
delqmatrix(prob, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Index of row from which the quadratic part is to be deleted. 

_**Return value:**_
The input argument `prob`.

#### delrows

_**Purpose:**_

   Delete rows from a matrix.

_**Synopsis:**_

   `
delrows(prob, rowind, nrows = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | An integer array of length `nrows` containing the rows to delete. 
`nrows` | Number of rows to delete. 

_**Return value:**_
The input argument `prob`.

#### delsets

_**Purpose:**_

   Delete sets from a problem.

_**Synopsis:**_

   `
delsets(prob, setind, nsets = x_max_vec_length(setind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`setind` | An integer array of length `nsets` containing the sets to delete. 
`nsets` | Number of sets to delete. 

_**Return value:**_
The input argument `prob`.

#### destroyprob

_**Purpose:**_

   Removes a given problem and frees any memory associated with it following manipulation and optimization.

_**Synopsis:**_

   `
destroyprob(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to be destroyed. 

_**Return value:**_
The input argument `prob`.

#### dumpcontrols

_**Purpose:**_

   Displays the list of controls and their current value for those controls that have been set to a non default value.

_**Synopsis:**_

   `
dumpcontrols(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem for which controls are dumped. 

_**Return value:**_
The input argument `prob`.

#### endlicensing

_**Purpose:**_

   Wraps callable C library function XPRSendlicensing.

Please refer to the OEM guide for details.

_**Synopsis:**_

   `
endlicensing()` 


#### estimaterowdualranges

_**Purpose:**_

   Performs a dual side range sensitivity analysis, i.e. calculates estimates for the possible ranges for dual values.

_**Synopsis:**_

   `
estimaterowdualranges(prob, rowind, iterlim, nrows = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Row indices to analyze. 
`iterlim` | Effort limit expressed as simplex iterations per row. 
`nrows` | The number of rows to analyze. 

_**Return value:**_
A list with the following elements:
 * `mindual`: Estimated lower bounds on the possible dual ranges.
 * `maxdual`: Estimated upper bounds on the possible dual ranges.


#### featurequery

_**Purpose:**_

   Checks if the provided feature is available in the current license used by the optimizer.

_**Synopsis:**_

   `
featurequery(feature)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`feature` | The feature string to be checked in the license. 

_**Return value:**_
Return status of the check, a value of 1 indicates the feature is available.

#### fixglobals

_**Purpose:**_

   Fixes all the MIP entities to the values of the last found MIP solution.

_**Synopsis:**_

   `
fixglobals(prob, options)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``fixmipentities``

#### fixmipentities

_**Purpose:**_

   Fixes all the MIP entities to the values of the last found MIP solution.

This is useful for finding the reduced costs for the continuous variables after the integer variables have been fixed to their optimal values.

_**Synopsis:**_

   `
fixmipentities(prob, options)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`options` | Options how to fix the MIP entities.
 * `0`: If all MIP entities should be rounded to the nearest discrete value in the solution before being fixed.
 * `1`: If piecewise linear and general constraints as well as partial integers should be kept in the problem with only the non-convex decisions \(i.e. which part of a non-convex piecewise linear function, which variable attains a maximum or the integer part of the partial integer\) fixed. Otherwise all variables appearing in piecewise linear or general constraints and all partial integers will be fixed.
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### free

_**Purpose:**_

   Frees any allocated memory and closes all open files.

_**Synopsis:**_

   `
free()` 


#### ge_getcomputeallowed

_**Purpose:**_

   Query whether the current application is allowed to use the Insight Compute interface.

_**Synopsis:**_

   `
ge_getcomputeallowed()` 


_**Return value:**_
The value. Value will equal one of the following constants.
 * `_ALLOW_COMPUTE_ALWAYS`: Always allow solves to be sent to Compute.
 * `_ALLOW_COMPUTE_NEVER`: Never allow solves to be sent to Compute.
 * `_ALLOW_COMPUTE_DEFAULT`: Allow solves to be sent to Compute only from non-OEM applications.


#### ge_getdebugmode

_**Purpose:**_

   Wraps callable C library function XPRS\_ge\_getdebugmode.

_**Synopsis:**_

   `
ge_getdebugmode()` 


#### ge_getlasterror

_**Purpose:**_

   Returns the last error encountered during a call to the Xpress global environment.

_**Synopsis:**_

   `
ge_getlasterror()` 


_**Return value:**_
A list with the following elements:
 * `msgcode`: The error code.
 * `msg`: The last error message relating to the global environment.


#### ge_setarchconsistency

_**Purpose:**_

   \*\*Deprecated\*\* Sets whether to force the same execution path on various x64 CPU architecture extensions, in particular \(pre-\)AVX and AVX2.

_**Synopsis:**_

   `
ge_setarchconsistency(consistent)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`consistent` | Whether to force the same execution path:
 * `0`: Do not force the same execution path;
 * `1`: Force the same execution path \(default behavior\).
 

_**Return value:**_
Always returns 0 \(zero\).

#### ge_setcomputeallowed

_**Purpose:**_

   Set whether the current application is allowed to use the Insight Compute interface.

_**Synopsis:**_

   `
ge_setcomputeallowed(allow)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`allow` | Whether the Insight Compute interface may be used; must be one of the following constants:
 * `_ALLOW_COMPUTE_ALWAYS`: Always allow solves to be sent to Compute.
 * `_ALLOW_COMPUTE_NEVER`: Never allow solves to be sent to Compute.
 * `_ALLOW_COMPUTE_DEFAULT`: Allow solves to be sent to Compute only from non-OEM applications.
 

_**Return value:**_
Always returns 0 \(zero\).

#### ge_setdebugmode

_**Purpose:**_

   Wraps callable C library function XPRS\_ge\_setdebugmode.

_**Synopsis:**_

   `
ge_setdebugmode(debugmode)` 


#### getattribinfo

_**Purpose:**_

   Accesses the id number and the type information of an attribute given its name.

An attribute name may be for example `ROWS`. Names are case-insensitive and may or may not have the `_`prefix. The id number is the constant used to identify the attribute in the C API. The type information returned will be one of the below integer constants. The function will return an id number of 0 and a type value of `TYPE_NOTDEFINED`if the name is not recognized as an attribute name. Note that this will occur if the name is a control name and not an attribute name.

_**Synopsis:**_

   `
getattribinfo(prob, name)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`name` | The name of the attribute to be queried. 

_**Return value:**_
A list with the following elements:
 * `id`: The id number.
 * `type`: The type id.


_**Further information:**_
Please refer to the C documentation for more details.

#### getbanner

_**Purpose:**_

   Returns the banner and copyright message.

_**Synopsis:**_

   `
getbanner()` 


_**Return value:**_
The null terminated banner string.

#### getbarnumstability

_**Purpose:**_

   Wraps callable C library function XPRSgetbarnumstability.

_**Synopsis:**_

   `
getbarnumstability(prob)` 


#### getbasis

_**Purpose:**_

   Returns the current basis into the user's data arrays.

_**Synopsis:**_

   `
getbasis(prob, rowstat = TRUE, colstat = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowstat` | Flag to indicate whether the output list should contain `rowstat`. 
`colstat` | Flag to indicate whether the output list should contain `colstat`. 

_**Return value:**_
A list with the following elements:
 * `rowstat`: Integer array of length ORIGINALROWS containing the basis status of the slack, surplus or artificial variable associated with each row. The status will be one of:
     * `_BASISSTATUS_NONBASIC_LOWER (0)`: slack, surplus or artificial is non-basic at lower bound;
     * `_BASISSTATUS_BASIC (1)`: slack, surplus or artificial is basic;
     * `_BASISSTATUS_NONBASIC_UPPER (2)`: slack or surplus is non-basic at upper bound.
     * `_BASISSTATUS_SUPERBASIC (3)`: slack or surplus is super-basic.

 * `colstat`: Integer array of length ORIGINALCOLS containing the basis status of the columns in the constraint matrix. The status will be one of:
     * `_BASISSTATUS_NONBASIC_LOWER (0)`: variable is non-basic at lower bound, or superbasic at zero if the variable has no lower bound;
     * `_BASISSTATUS_BASIC (1)`: variable is basic;
     * `_BASISSTATUS_NONBASIC_UPPER (2)`: variable is non-basic at upper bound;
     * `_BASISSTATUS_SUPERBASIC (3)`: variable is super-basic.



#### getbasisval

_**Purpose:**_

   Returns the current basis status for a specific column or row.

_**Synopsis:**_

   `
getbasisval(prob, row, col)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Row index to get the row basis status for. 
`col` | Column index to get the column basis status for. 

_**Return value:**_
A list with the following elements:
 * `rowstat`: The row basis status.
 * `colstat`: The column basis status.


#### getcallbackduals

_**Purpose:**_

   Returns the dual values from the solution associated with the current callback.

_**Synopsis:**_

   `
getcallbackduals(


  prob,


  first = 0,


  last = getintattrib(prob, xpress:::INPUTROWS) - 1


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row whose dual value to return. 
`last` | Last row whose dual value to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a dual solution is available.
 * `duals`: Double array of length `last-first+1` containing the values of the dual variables.


#### getcallbackpresolveduals

_**Purpose:**_

   Returns the dual values from the solution to the presolved problem associated with the current callback.

_**Synopsis:**_

   `
getcallbackpresolveduals(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row whose dual value to return. 
`last` | Last row whose dual value to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a dual solution is available.
 * `duals`: Double array of length `last-first+1` containing the values of the dual variables.


#### getcallbackpresolveredcosts

_**Purpose:**_

   Returns the reduced costs from the solution to the presolved problem associated with the current callback.

_**Synopsis:**_

   `
getcallbackpresolveredcosts(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column whose reduced cost to return. 
`last` | Last column whose reduced cost to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a dual solution is available.
 * `djs`: Double array of length `last-first+1` containing the reduced costs of the variables.


#### getcallbackpresolveslacks

_**Purpose:**_

   Returns the slack values from the solution to the presolved problem associated with the current callback.

_**Synopsis:**_

   `
getcallbackpresolveslacks(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row whose slack value to return. 
`last` | Last row whose slack value to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a solution is available.
 * `slacks`: Double array of length `last-first+1` containing the values of the slack variables.


#### getcallbackpresolvesolution

_**Purpose:**_

   Returns the solution to the presolved problem associated with the current callback.

_**Synopsis:**_

   `
getcallbackpresolvesolution(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the solution to return. 
`last` | Last column in the solution to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a solution is available.
 * `x`: Double array of length `last-first+1` containing the values of the primal variables.


#### getcallbackredcosts

_**Purpose:**_

   Returns the reduced costs from the solution associated with the current callback.

_**Synopsis:**_

   `
getcallbackredcosts(


  prob,


  first = 0,


  last = getintattrib(prob, xpress:::INPUTCOLS) - 1


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column whose reduced cost to return. 
`last` | Last column whose reduced cost to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a dual solution is available.
 * `djs`: Double array of length `last-first+1` containing the reduced costs of the variables.


#### getcallbackslacks

_**Purpose:**_

   Returns the slack values from the solution associated with the current callback.

_**Synopsis:**_

   `
getcallbackslacks(


  prob,


  first = 0,


  last = getintattrib(prob, xpress:::INPUTROWS) - 1


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row whose slack value to return. 
`last` | Last row whose slack value to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a solution is available.
 * `slacks`: Double array of length `last-first+1` containing the values of the slack variables.


#### getcallbacksolution

_**Purpose:**_

   Returns the primal values from the solution associated with the current callback.

_**Synopsis:**_

   `
getcallbacksolution(


  prob,


  first = 0,


  last = getintattrib(prob, xpress:::INPUTCOLS) - 1


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the solution to return. 
`last` | Last column in the solution to return. 

_**Return value:**_
A list with the following elements:
 * `available`: This variable will be set to 1 if a solution is available.
 * `x`: Double array of length `last-first+1` containing the values of the primal variables.


#### getcheckedmode

_**Purpose:**_

   You can use this function to interrogate whether checking and validation of all Optimizer function calls is enabled for the current process.

Checking and validation is enabled by default but can be disabled by setcheckedmode.

_**Synopsis:**_

   `
getcheckedmode()` 


_**Return value:**_
0 If checking and validation of Optimizer function calls is disabled for the current process, non-zero otherwise.

_**Further information:**_
Please refer to the C documentation for more details.

#### getcoef

_**Purpose:**_

   Returns a single coefficient in the constraint matrix.

_**Synopsis:**_

   `
getcoef(prob, row, col)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Row of the constraint matrix. 
`col` | Column of the constraint matrix. 

_**Return value:**_
The coefficient.

#### getcols

_**Purpose:**_

   Returns the nonzeros in the constraint matrix for the columns in a given range.

_**Synopsis:**_

   `
getcols(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
A list with the following elements:
 * `start`: Integer array containing the indices indicating the starting offsets in the `rowind` and `rowcoef` arrays for each requested column.
 * `rowind`: Integer array of length `maxcoefs` containing the row indices of the nonzero coefficents for each column.
 * `rowcoef`: Double array of length `maxcoefs` containing the nonzero coefficient values.


#### getcoltype

_**Purpose:**_

   Returns the column types for the columns in a given range.

_**Synopsis:**_

   `
getcoltype(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
Character array of length `last-first+1`containing the column types:
 * `C`: indicates a continuous variable;
 * `I`: indicates an integer variable;
 * `B`: indicates a binary variable;
 * `S`: indicates a semi-continuous variable;
 * `R`: indicates a semi-continuous integer variable;
 * `P`: indicates a partial integer variable.


#### getcontrolinfo

_**Purpose:**_

   Accesses the id number and the type information of a control given its name.

A control name may be for example `PRESOLVE`. Names are case-insensitive and may or may not have the `_`prefix. The id number is the constant used to identify the control in the C API. The type information returned will be one of the below integer constants. The function will return an id number of `0`and a type value of `TYPE_NOTDEFINED`if the name is not recognized as a control name. Note that this will occur if the name is an attribute name and not a control name.

_**Synopsis:**_

   `
getcontrolinfo(prob, name)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`name` | The name of the control to be queried. 

_**Return value:**_
A list with the following elements:
 * `id`: The id number.
 * `type`: The type information.


_**Further information:**_
Please refer to the C documentation for more details.

#### getcpcutlist

_**Purpose:**_

   Returns a list of cut indices from the cut pool.

_**Synopsis:**_

   `
getcpcutlist(prob, cuttype = 0, interp = -1, delta = -Inf)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cuttype` | The user defined type of the cuts to be returned. 
`interp` | Way in which the cut type is interpreted:
 * `-1`: get all cuts;
 * `1`: treat cut types as numbers;
 * `2`: treat cut types as bit-vectors \(compare Section \) - get cut if any bit matches any bit set in `cuttype`;
 * `3`: treat cut types as bit-vectors \(compare Section \) - get cut if all bits match those set in `cuttype`.
 
`delta` | Only those cuts with a signed violation greater than delta will be returned. 

_**Return value:**_
A list with the following elements:
 * `ncuts`: The number of cuts of type `cuttype` in the cut pool.
 * `cutind`: Array of length `maxcuts` containing the cut objects.
 * `viol`: Double array of length `maxcuts` containing the values of the signed violations of the cuts.


#### getcpcuts

_**Purpose:**_

   Returns cuts from the cut pool.

_**Synopsis:**_

   `
getcpcuts(prob, rowind, ncuts = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Array of length `ncuts` containing the cut objects. 
`ncuts` | Number of cuts to be returned. 

_**Return value:**_
A list with the following elements:
 * `cuttype`: Integer array of length `ncuts` containing the cut types.
 * `rowtype`: Character array of length `ncuts` containing the sense of the cuts \( `L`, `G`, or `E`\).
 * `start`: Integer array of length `ncuts+1` containing the offsets into the `colind` and `cutcoef` arrays.
 * `colind`: Integer array of length `maxcoefs` containing the column indices of the cuts.
 * `cutcoef`: Double array of length `maxcoefs` containing the matrix values.
 * `rhs`: Double array of length `ncuts` containing the right hand side elements for the cuts.


#### getcutlist

_**Purpose:**_

   Retrieves a list of cut objects for the cuts active at the current node.

_**Synopsis:**_

   `
getcutlist(prob, cuttype = 0, interp = -1)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cuttype` | User defined type of the cuts to be returned. 
`interp` | Way in which the cut type is interpreted:
 * `-1`: get all cuts;
 * `1`: treat cut types as numbers;
 * `2`: treat cut types as bit-vectors \(compare Section \) - get cut if any bit matches any bit set in `cuttype`;
 * `3`: treat cut types as bit-vectors \(compare Section \) - get cut if all bits match those set in `cuttype`.
 

_**Return value:**_
A list with the following elements:
 * `ncuts`: The number of active cuts of type `cuttype`.
 * `cutind`: Array of length `maxcuts` containing the cut objects.


#### getcutmap

_**Purpose:**_

   Used to return in which rows a list of cuts are currently loaded into the Optimizer.

This is useful for example to retrieve the duals associated with active cuts.

_**Synopsis:**_

   `
getcutmap(prob, cutind, ncuts = x_max_vec_length(cutind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cutind` | Array of length `ncuts` containing the cut objects for which the row index is requested. 
`ncuts` | Number of cuts in the cutind array. 

_**Return value:**_
Integer array of length `ncuts`, containing the row indices.

_**Further information:**_
Please refer to the C documentation for more details.

#### getcutslack

_**Purpose:**_

   Used to calculate the slack value of a cut with respect to the current LP relaxation solution.

The slack is calculated from the cut itself, and might be requested for any cut \(even if it is not currently loaded into the problem\).

_**Synopsis:**_

   `
getcutslack(prob, cutind)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cutind` | Cut object for which the slack is to be calculated. 

_**Return value:**_
The slack.

_**Further information:**_
Please refer to the C documentation for more details.

#### getdaysleft

_**Purpose:**_

   Returns the number of days left until the license expires.

_**Synopsis:**_

   `
getdaysleft()` 


_**Return value:**_
The number of days.

#### getdblattrib

_**Purpose:**_

   Enables users to retrieve the values of various double problem attributes.

Problem attributes are set during loading and optimization of a problem.

_**Synopsis:**_

   `
getdblattrib(prob, attrib)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`attrib` | Problem attribute whose value is to be returned. 

_**Return value:**_
The value of the problem attribute.

_**Further information:**_
Please refer to the C documentation for more details.

#### getdblcontrol

_**Purpose:**_

   Retrieves the value of a given double control parameter.

_**Synopsis:**_

   `
getdblcontrol(prob, control)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Control parameter whose value is to be returned. 

_**Return value:**_
The control value.

#### getdirs

_**Purpose:**_

   Used to return the directives that have been loaded into a matrix.

Priorities, forced branching directions and pseudo costs can be returned. If called after presolve, `getdirs`will get the directives for the presolved problem.

_**Synopsis:**_

   `
getdirs(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `ndir`: The number of directives.
 * `indices`: Integer array of length `ndir` containing the column numbers \( `0`, `1`, `2`,...\) or negative values corresponding to special ordered sets \(the first set numbered `-1`, the second numbered `-2`,...\).
 * `prios`: Integer array of length `ndir` containing the priorities for the columns and sets, where columns/sets with smallest priority will be branched on first.
 * `branchdirs`: Character array of length `ndir` containing the branching direction for each column or set:
     * `U`: the entity is to be forced up;
     * `D`: the entity is to be forced down;
     * `N`: not specified.

 * `uppseudo`: Double array of length `ndir` containing the up pseudo costs for the columns and sets.
 * `downpseudo`: Double array of length `ndir` containing the down pseudo costs for the columns and sets.


_**Further information:**_
Please refer to the C documentation for more details.

#### getdualray

_**Purpose:**_

   Retrieves a dual ray \(dual unbounded direction\) for the current problem, if the problem is found to be infeasible.

_**Synopsis:**_

   `
getdualray(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `ray`: Double array of length ROWS containing the ray.
 * `hasray`: This variable will be set to 1 if the Optimizer is able to return a dual ray, 0 otherwise.


#### getduals

_**Purpose:**_

   Returns the dual values from the incumbent solution during or after optimization of a continuous problem with optimize, lpoptimize or nlpoptimize.

_**Synopsis:**_

   `
getduals(prob, first = 0, last = getintattrib(prob, xpress:::INPUTROWS) - 1)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the dual solution. 
`last` | Last row in the dual solution. 

_**Return value:**_
A list with the following elements:
 * `status`: Information about the dual solution returned.
 * `duals`: Double array of length `last-first+1` containing the values of the dual variables.


#### getgencons

_**Purpose:**_

   Returns the general constraints `y = f(x1, ..., xn, c1, ..., cm)`in a given range.

_**Synopsis:**_

   `
getgencons(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First general constraint in the range. 
`last` | Last general constraint in the range. 

_**Return value:**_
A list with the following elements:
 * `contype`: An integer array of length `last-first+1` containing the types of the general constraints:
     * `_GENCONS_MAX (0)`: indicates a `maximum` constraint;
     * `_GENCONS_MIN (1)`: indicates a `minimum` constraint;
     * `_GENCONS_AND (2)`: indicates an `and` constraint.
     * `_GENCONS_OR (3)`: indicates an `or` constraint;
     * `_GENCONS_ABS (4)`: indicates an `absolute value` constraint.

 * `resultant`: Integer array containing the indices of the output variables `y`.
 * `colstart`: Integer array of length `last-first+2` containing the start index of each general constraint in the `colind` array.
 * `colind`: Integer array containing the indices of the input variables `xi`.
 * `ncols`: The number of input columns in the `colind` array.
 * `valstart`: Integer array of length `last-first+2` containing the start index of each general constraint in the `val` array.
 * `val`: Integer array containing the constant values `ci`.
 * `nvals`: The number of constant values in the `val` array.


#### getglobal

_**Purpose:**_

   Retrieves integer and entity information about a problem.

_**Synopsis:**_

   `
getglobal(prob)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``getmipentities``

#### getiisdata

_**Purpose:**_

   Returns information for an Irreducible Infeasible Set: size, variables and constraints \(row and column vectors\), and conflicting sides of the variables.

For pure linear problems there is also information on duals, reduced costs and isolations.

_**Synopsis:**_

   `
getiisdata(prob, iis)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`iis` | The ordinal number of the IIS to get data for. 

_**Return value:**_
A list with the following elements:
 * `nrows`: The number of rows in the IIS.
 * `ncols`: The number of bounds in the IIS.
 * `rowind`: Indices of rows/sets/piecewise linear constraints/general constraints in the IIS.
 * `colind`: Indices of bounds \(columns\) in the IIS.
 * `contype`: Sense of rows in the IIS:
     * `L`: for less or equal row;
     * `G`: for greater or equal row.
     * `E`: for an equality row \(for a non LP IIS\);
     * `1`: for a SOS1 row;
     * `2`: for a SOS2 row;
     * `W`: for a piecewise linear constraint;
     * `X`: for a general constraint;
     * `I`: for an indicator row.

 * `bndtype`: Sense of bound in the IIS:
     * `U`: for upper bound;
     * `L`: for lower bound.
     * `F`: for fixed columns \(for a non LP IIS\);
     * `B`: for a binary column;
     * `I`: for an integer column;
     * `P`: for a partial integer columns;
     * `S`: for a semi-continuous column;
     * `R`: for a semi-continuous integer column.

 * `duals`: The dual multipliers associated with the rows.
 * `djs`: The dual multipliers \(reduced costs\) associated with the bounds.
 * `isolationrows`: The isolation status of the rows:
     * `-1`: if isolation information is not available for row \(run iis isolations\);
     * `0`: if row is not in isolation;
     * `1`: if row is in isolation.

 * `isolationcols`: The isolation status of the bounds:
     * `-1`: if isolation information is not available for column \(run iis isolations\);
     * `0`: if column is not in isolation;
     * `1`: if column is in isolation.



_**Further information:**_
Please refer to the C documentation for more details.

#### getindex

_**Purpose:**_

   Returns the index for a specified row or column name.

_**Synopsis:**_

   `
getindex(prob, type, name)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`type` | 
 * `_NAMES_ROW`: `(=1)` if row index is required;
 * `_NAMES_COLUMN`: `(=2)` if column index is required;
 * `_NAMES_SET`: `(=3)` if set index is required;
 * `_NAMES_PWLCONS`: `(=4)` if piecewise linear constraint index is required;
 * `_NAMES_GENCONS`: `(=5)` if general constraint index is required;
 * `_NAMES_OBJECTIVE`: `(=6)` if objective index is required;
 * `_NAMES_USERFUNC`: `(=7)` if user function index is required;
 * `_NAMES_INTERNALFUNC`: `(=8)` if an internal function index is required.
 
`name` | Null terminated string. 

_**Return value:**_
The row or column index number.

#### getindicators

_**Purpose:**_

   Returns the indicator constraint condition \(indicator variable and complement flag\) associated to the rows in a given range.

_**Synopsis:**_

   `
getindicators(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the range. 
`last` | Last row in the range \(inclusive\). 

_**Return value:**_
A list with the following elements:
 * `colind`: Integer array of length `last-first+1` containing the column indices of the indicator variables.
 * `complement`: Integer array of length `last-first+1` containing the indicator complement flags:
     * `0`: not an indicator constraint \(in this case the corresponding entry in the `colind` array is ignored\);
     * `1`: for indicator constraints with condition " `bin = 1` ";
     * `-1`: for indicator constraints with condition " `bin = 0` ".



#### getinfeas

_**Purpose:**_

   Returns a list of infeasible primal and dual variables.

_**Synopsis:**_

   `
getinfeas(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `nprimalcols`: The number of primal infeasible variables.
 * `nprimalrows`: The number of primal infeasible rows.
 * `ndualrows`: The number of dual infeasible rows.
 * `ndualcols`: The number of dual infeasible variables.
 * `x`: Integer array of length `nprimalcols` containing the indices of the primal infeasible variables.
 * `slack`: Integer array of length `nprimalrows` containing the indices of the primal infeasible rows.
 * `duals`: Integer array of length `ndualrows` containing the indices of the dual infeasible rows.
 * `djs`: Integer array of length `ndualcols` containing the indices of the dual infeasible variables.


#### getintattrib

_**Purpose:**_

   Enables users to recover the values of various integer problem attributes.

Problem attributes are set during loading and optimization of a problem.

_**Synopsis:**_

   `
getintattrib(prob, attrib)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`attrib` | Problem attribute whose value is to be returned. 

_**Return value:**_
The value of the problem attribute.

_**Further information:**_
Please refer to the C documentation for more details.

#### getintcontrol

_**Purpose:**_

   Enables users to recover the values of various integer control parameters

_**Synopsis:**_

   `
getintcontrol(prob, control)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Control parameter whose value is to be returned. 

_**Return value:**_
The value of the control.

#### getlastbarsol

_**Purpose:**_

   Used to obtain the last barrier solution values following optimization that used the barrier solver.

_**Synopsis:**_

   `
getlastbarsol(prob, x = TRUE, slack = TRUE, duals = TRUE, djs = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`x` | Flag to indicate whether the output list should contain `x`. 
`slack` | Flag to indicate whether the output list should contain `slack`. 
`duals` | Flag to indicate whether the output list should contain `duals`. 
`djs` | Flag to indicate whether the output list should contain `djs`. 

_**Return value:**_
A list with the following elements:
 * `x`: Double array of length ORIGINALCOLS containing the values of the primal variables.
 * `slack`: Double array of length ORIGINALROWS containing the values of the slack variables.
 * `duals`: Double array of length `ORIGINALROWS` containing the values of the dual variables \(cBTB-1\).
 * `djs`: Double array of length `ORIGINALCOLS` containing the reduced cost for each variable \(cT-cBTB-1A\).
 * `status`: Status of the last barrier solve.


#### getlasterror

_**Purpose:**_

   Returns the error message corresponding to the last error encountered by a library function.

_**Synopsis:**_

   `
getlasterror(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A 512 character buffer containing the last error message.

#### getlb

_**Purpose:**_

   Returns the lower bounds for the columns in a given range.

_**Synopsis:**_

   `
getlb(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
Double array of length `last-first+1`containing the lower bounds.

#### getlicerrmsg

_**Purpose:**_

   Retrieves an error message describing the last licensing error, if any occurred.

_**Synopsis:**_

   `
getlicerrmsg(maxbytes = 2048)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`maxbytes` | Length of the buffer. 

_**Return value:**_
The error message.

#### getlpsol

_**Purpose:**_

   Used to obtain the LP solution values following optimization.

_**Synopsis:**_

   `
getlpsol(prob, x = TRUE, slack = TRUE, duals = TRUE, djs = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`x` | Flag to indicate whether the output list should contain `x`. 
`slack` | Flag to indicate whether the output list should contain `slack`. 
`duals` | Flag to indicate whether the output list should contain `duals`. 
`djs` | Flag to indicate whether the output list should contain `djs`. 

_**Return value:**_
A list with the following elements:
 * `x`: Double array of length ORIGINALCOLS containing the values of the primal variables.
 * `slack`: Double array of length ORIGINALROWS containing the values of the slack variables.
 * `duals`: Double array of length `ORIGINALROWS` containing the values of the dual variables \(cBTB-1\).
 * `djs`: Double array of length `ORIGINALCOLS` containing the reduced cost for each variable \(cT-cBTB-1A\).


#### getlpsolval

_**Purpose:**_

   \*\*Deprecated\*\* Use getsolution or getcallbacksolution and related functions instead.

Used to obtain a single LP solution value following optimization.

_**Synopsis:**_

   `
getlpsolval(prob, col, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`col` | Column index of the variable for which to return the solution value. 
`row` | Row index of the constraint for which to return the solution value. 

_**Return value:**_
A list with the following elements:
 * `x`: The primal variable.
 * `slack`: The slack variable.
 * `dual`: The dual variable \(cBTB-1\).
 * `dj`: Reduced costs for the variable \(cT-cBTB-1A\).


_**Further information:**_
Please refer to the C documentation for more details.

#### getmessagestatus

_**Purpose:**_

   Retrieves the current suppression status of a message.

_**Synopsis:**_

   `
getmessagestatus(prob, msgcode)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to check for the suppression status of the message error code. 
`msgcode` | The id number of the message. 

_**Return value:**_
Non-zero if the message is not suppressed; `0`otherwise.

#### getmipentities

_**Purpose:**_

   Retrieves integr and entity information about a problem.

It must be called before mipoptimize if the presolve option is used.

_**Synopsis:**_

   `
getmipentities(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `nentities`: The number of binary, integer, semi-continuous, semi-continuous integer and partial integer entities.
 * `nsets`: The number of SOS1 and SOS2 sets.
 * `coltype`: Character array of length `MIPENTS` containing the entity types. The types will be one of:
     * `B`: binary variables;
     * `I`: integer variables;
     * `P`: partial integer variables;
     * `S`: semi-continuous variables;
     * `R`: semi-continuous integer variables.

 * `colind`: Integer array of length `MIPENTS` containing the column indices of the MIP entities.
 * `limit`: Double array of length `MIPENTS` containing the limits for the partial integer variables and lower bounds for the semi-continuous and semi-continuous integer variables \(any entries in the positions corresponding to binary and integer variables will be meaningless\).
 * `settype`: Character array of length `SETS` containing the set types. The set types will be one of:
     * `1`: SOS1 type sets;
     * `2`: SOS2 type sets.

 * `start`: Integer array containing the offsets into the `setcols` and `refval` arrays indicating the start of each set.
 * `setcols`: Integer array of length `SETMEMBERS` containing the columns in each set.
 * `refval`: Double array of length `SETMEMBERS` containing the reference row entries for each member of the sets.


_**Further information:**_
Please refer to the C documentation for more details.

#### getmipsol

_**Purpose:**_

   \*\*Deprecated\*\* Use getsolution and getslacks instead.

Used to obtain the solution values of the last MIP solution that was found.

_**Synopsis:**_

   `
getmipsol(prob, x = TRUE, slack = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`x` | Flag to indicate whether the output list should contain `x`. 
`slack` | Flag to indicate whether the output list should contain `slack`. 

_**Return value:**_
A list with the following elements:
 * `x`: Double array of length ORIGINALCOLS containing the values of the primal variables.
 * `slack`: Double array of length ORIGINALROWS containing the values of the slack variables.


_**Further information:**_
Please refer to the C documentation for more details.

#### getmipsolval

_**Purpose:**_

   \*\*Deprecated\*\* Use getsolution and getslacks instead.

Used to obtain a single solution value of the last MIP solution that was found.

_**Synopsis:**_

   `
getmipsolval(prob, col, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`col` | Column index of the variable for which to return the solution value. 
`row` | Row index of the constraint for which to return the solution value. 

_**Return value:**_
A list with the following elements:
 * `x`: The primal variable.
 * `slack`: The slack variable.


_**Further information:**_
Please refer to the C documentation for more details.

#### getmqobj

_**Purpose:**_

   Returns the nonzeros in the quadratic objective coefficients matrix for the columns in a given range.

To achieve maximum efficiency, `getmqobj`returns the lower triangular part of this matrix only.

_**Synopsis:**_

   `
getmqobj(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
A list with the following elements:
 * `start`: Integer array of length `last-first+2` containing indices indicating the starting offsets in the `colind` and `objqcoef` arrays for each requested column.
 * `colind`: Integer array of length `maxcoefs` containing the column indices of the nonzero elements in the lower triangular part of `Q`.
 * `objqcoef`: Double array of length `maxcoefs` containing the nonzero element values.


_**Further information:**_
Please refer to the C documentation for more details.

#### getnamelist

_**Purpose:**_

   Returns the names for the rows, columns, sets, piecewise linear constraints, general constraints or objectives in a given range.

_**Synopsis:**_

   `
getnamelist(prob, type, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`type` | 
 * `_NAMES_ROW`: `(=1)` if row names are required;
 * `_NAMES_COLUMN`: `(=2)` if column names are required;
 * `_NAMES_SET`: `(=3)` if set names are required;
 * `_NAMES_PWLCONS`: `(=4)` if piecewise linear constraint names are required;
 * `_NAMES_GENCONS`: `(=5)` if general constraint names are required;
 * `_NAMES_OBJECTIVE`: `(=6)` if objective function names are required.
 
`first` | First row, column, set, piecewise linear or general constraint in the range. 
`last` | Last row, column, set, piecewise linear or general constraint in the range. 

_**Return value:**_
The names.

#### getnamelistobject

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

Returns the `namelist`object for the rows, columns or sets of a problem. The names stored in this object can be queried using the `_nml_`functions.

_**Synopsis:**_

   `
getnamelistobject(prob, type)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`type` | 
 * `_NAMES_ROW`: `(=1)` if the row name list is required;
 * `_NAMES_COLUMN`: `(=2)` if the column name list is required;
 * `_NAMES_SET`: `(=3)` if the set name list is required;
 * `_NAMES_PWLCONS`: `(=4)` if piecewise linear constraint name list is required;
 * `_NAMES_GENCONS`: `(=5)` if general constraint name list is required;
 * `_NAMES_OBJECTIVE`: `(=6)` if objective name list is required.
 

_**Return value:**_
The name list contained by the problem.

_**Further information:**_
Please refer to the C documentation for more details.

#### getnames

_**Purpose:**_

   \*\*Deprecated\*\* Use getnamelist instead.

Returns the names for the rows, columns, sets, piecewise linear constraints, general constraints or objectives in a given range. The names will be returned in a character buffer, each name being separated by a null character.

_**Synopsis:**_

   `
getnames(prob, type, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`type` | 
 * `_NAMES_ROW`: `(=1)` if row names are required;
 * `_NAMES_COLUMN`: `(=2)` if column names are required;
 * `_NAMES_SET`: `(=3)` if set names are required;
 * `_NAMES_PWLCONS`: `(=4)` if piecewise linear constraint names are required;
 * `_NAMES_GENCONS`: `(=5)` if general constraint names are required;
 * `_NAMES_OBJECTIVE`: `(=6)` if objective function names are required;
 
`first` | First row, column, set, piecewise linear or general constraint in the range. 
`last` | Last row, column, set, piecewise linear or general constraint in the range. 

_**Return value:**_
The names.

_**Further information:**_
Please refer to the C documentation for more details.

#### getobj

_**Purpose:**_

   Returns the objective function coefficients for the columns in a given range.

_**Synopsis:**_

   `
getobj(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
Double array of length `last-first+1`containing the objective function coefficients.

#### getobjdblattrib

_**Purpose:**_

   Retrieves the value of a given double attribute associated with a multi-objective solve.

When solving a multi-objective problem, several objectives might be optimized in sequence. After each solve, the problem attributes are captured so that they can be queried afterwards.

_**Synopsis:**_

   `
getobjdblattrib(prob, solveidx, attrib)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`solveidx` | Index of the solve to query. 
`attrib` | Problem attribute whose value is to be returned. 

_**Return value:**_
Attribute value.

_**Further information:**_
Please refer to the C documentation for more details.

#### getobjdblcontrol

_**Purpose:**_

   Retrieves the value of a given double control parameter associated with an objective function.

These parameters control how the objective is treated during multi-objective optimization.

_**Synopsis:**_

   `
getobjdblcontrol(prob, objidx, control)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective to query. 
`control` | Control parameter whose value is to be returned. Can be any solver control, or one of:
 * `_OBJECTIVE_WEIGHT`: get the weight of the given objective;
 * `_OBJECTIVE_ABSTOL`: get the absolute tolerance of the given objective;
 * `_OBJECTIVE_RELTOL`: get the relative tolerance of the given objective;
 * `_OBJECTIVE_RHS`: get the constant term of the given objective.
 

_**Return value:**_
The control value.

_**Further information:**_
Please refer to the C documentation for more details.

#### getobjintattrib

_**Purpose:**_

   Retrieves the value of a given integer attribute associated with a multi-objective solve.

When solving a multi-objective problem, several objectives might be optimized in sequence. After each solve, the problem attributes are captured so that they can be queried afterwards.

_**Synopsis:**_

   `
getobjintattrib(prob, solveidx, attrib)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`solveidx` | Index of the solve to query. 
`attrib` | Problem attribute whose value is to be returned. 

_**Return value:**_
Attribute value.

_**Further information:**_
Please refer to the C documentation for more details.

#### getobjintcontrol

_**Purpose:**_

   Retrieves the value of a given integer control parameter associated with an objective.

These parameters control how the objective is treated during multi-objective optimization.

_**Synopsis:**_

   `
getobjintcontrol(prob, objidx, control)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective to query. 
`control` | Control parameter whose value is to be returned. Can be any solver control, or one of:
 * `_OBJECTIVE_PRIORITY`: get the priority of the given objective.
 

_**Return value:**_
The control value.

_**Further information:**_
Please refer to the C documentation for more details.

#### getobjn

_**Purpose:**_

   For a given objective function, returns the objective coefficients for the columns in a given range.

_**Synopsis:**_

   `
getobjn(prob, objidx, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective function whose coefficients to return. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
Double array of length `last-first+1`containing the objective function coefficients.

#### getpivotorder

_**Purpose:**_

   Returns the pivot order of the basic variables.

_**Synopsis:**_

   `
getpivotorder(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
Integer array of length ROWS containing the pivot order.

#### getpivots

_**Purpose:**_

   Returns a list of potential leaving variables if a specified variable enters the basis.

_**Synopsis:**_

   `
getpivots(prob, enter)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`enter` | Index of the specified row or column to enter basis. 

_**Return value:**_
A list with the following elements:
 * `outlist`: Integer array of length `maxpivots` containing list of potential leaving variables.
 * `x`: Double array of length ROWS `+` SPAREROWS `+` COLS containing the values of all the variables that would result if `enter` entered the basis.
 * `objval`: The objective function value that would result if `enter` entered the basis.
 * `npivots`: The actual number of potential leaving variables.


#### getpresolvebasis

_**Purpose:**_

   Returns the current basis from memory into the user's data areas.

If the problem is presolved, the presolved basis will be returned. Otherwise the original basis will be returned.

_**Synopsis:**_

   `
getpresolvebasis(prob, rowstat = TRUE, colstat = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowstat` | Flag to indicate whether the output list should contain `rowstat`. 
`colstat` | Flag to indicate whether the output list should contain `colstat`. 

_**Return value:**_
A list with the following elements:
 * `rowstat`: Integer array of length ROWS containing the basis status of the stack, surplus or artificial variable associated with each row. The status will be one of:
     * `_BASISSTATUS_NONBASIC_LOWER (0)`: slack, surplus or artificial is non-basic at lower bound;
     * `_BASISSTATUS_BASIC (1)`: slack, surplus or artificial is basic;
     * `_BASISSTATUS_NONBASIC_UPPER (2)`: slack or surplus is non-basic at upper bound.

 * `colstat`: Integer array of length COLS containing the basis status of the columns in the constraint matrix. The status will be one of:
     * `_BASISSTATUS_NONBASIC_LOWER (0)`: variable is non-basic at lower bound, or superbasic at zero if the variable has no lower bound;
     * `_BASISSTATUS_BASIC (1)`: variable is basic;
     * `_BASISSTATUS_NONBASIC_UPPER (2)`: variable is at upper bound;
     * `_BASISSTATUS_SUPERBASIC (3)`: variable is super-basic.



_**Further information:**_
Please refer to the C documentation for more details.

#### getpresolvemap

_**Purpose:**_

   Returns the mapping of the row and column numbers from the presolve problem back to the original problem.

_**Synopsis:**_

   `
getpresolvemap(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `rowmap`: Integer array of length ROWS containing the row maps.
 * `colmap`: Integer array of length COLS containing the column maps.


#### getpresolvesol

_**Purpose:**_

   Returns the solution for the presolved problem from memory.

_**Synopsis:**_

   `
getpresolvesol(prob, x = TRUE, slack = TRUE, duals = TRUE, djs = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`x` | Flag to indicate whether the output list should contain `x`. 
`slack` | Flag to indicate whether the output list should contain `slack`. 
`duals` | Flag to indicate whether the output list should contain `duals`. 
`djs` | Flag to indicate whether the output list should contain `djs`. 

_**Return value:**_
A list with the following elements:
 * `x`: Double array of length COLS containing the values of the primal variables.
 * `slack`: Double array of length ROWS containing the values of the slack variables.
 * `duals`: Double array of length `ROWS` containing the values of the dual variables.
 * `djs`: Double array of length `COLS` containing the reduced cost for each variable.


#### getprimalray

_**Purpose:**_

   Retrieves a primal ray \(primal unbounded direction\) for the current problem, if the problem is found to be unbounded.

_**Synopsis:**_

   `
getprimalray(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `ray`: Double array of length COLS containing the ray.
 * `hasray`: This variable will be set to 1 if the Optimizer is able to return a primal ray, 0 otherwise.


#### getprobname

_**Purpose:**_

   Returns the current problem name.

_**Synopsis:**_

   `
getprobname(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A buffer of MAXPROBNAMELENGTH+1 bytes to contain the current problem name.

#### getpwlcons

_**Purpose:**_

   Returns the piecewise linear constraints `y = f(x)`in a given range.

_**Synopsis:**_

   `
getpwlcons(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First piecewise linear constraint in the range. 
`last` | Last piecewise linear constraint in the range. 

_**Return value:**_
A list with the following elements:
 * `colind`: Integer array containing the indices of the input variables `x`.
 * `resultant`: Integer array containing the indices of the output variables `y`.
 * `start`: Integer array containing the start indices of the different constraints in the breakpoint arrays.
 * `xval`: Double array of length `maxpoints` containing the `x` -values of the breakpoints.
 * `yval`: Double array of length `maxpoints` containing the `y` -values of the breakpoints.
 * `npoints`: The number of breakpoints in the selected constraints.


#### getqobj

_**Purpose:**_

   Returns a single quadratic objective function coefficient corresponding to the variable pair `(objqcol1, objqcol2)`of the Hessian matrix.

_**Synopsis:**_

   `
getqobj(prob, objqcol1, objqcol2)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objqcol1` | Column index for the first variable in the quadratic term. 
`objqcol2` | Column index for the second variable in the quadratic term. 

_**Return value:**_
The objective function coefficient.

#### getqrowcoeff

_**Purpose:**_

   Returns a single quadratic constraint coefficient corresponding to the variable pair \( `rowqcol1`, `rowqcol2`\) of the Hessian of a given constraint.

_**Synopsis:**_

   `
getqrowcoeff(prob, row, rowqcol1, rowqcol2)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | The quadratic row where the coefficient is to be looked up. 
`rowqcol1` | Column index for the first variable in the quadratic term. 
`rowqcol2` | Column index for the second variable in the quadratic term. 

_**Return value:**_
The objective function coefficient.

#### getqrowqmatrix

_**Purpose:**_

   Returns the nonzeros in a quadratic constraint coefficients matrix for the columns in a given range.

To achieve maximum efficiency, `getqrowqmatrix`returns the lower triangular part of this matrix only.

_**Synopsis:**_

   `
getqrowqmatrix(prob, row, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Index of the row for which the quadratic coefficients are to be returned. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
A list with the following elements:
 * `start`: Integer array containing indices indicating the starting offsets in the `colind` and `rowqcoef` arrays for each requested column.
 * `colind`: Integer array of length maxcoefs containing the column indices of the nonzero elements in the lower triangular part of Q.
 * `rowqcoef`: Double array of length maxcoefs containing the nonzero element values.


_**Further information:**_
Please refer to the C documentation for more details.

#### getqrowqmatrixtriplets

_**Purpose:**_

   Returns the nonzeros in a quadratic constraint coefficients matrix as triplets \(index pairs with coefficients\).

To achieve maximum efficiency, `getqrowqmatrixtriplets`returns the lower triangular part of this matrix only.

_**Synopsis:**_

   `
getqrowqmatrixtriplets(prob, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | Index of the row for which the quadratic coefficients are to be returned. 

_**Return value:**_
A list with the following elements:
 * `ncoefs`: Argument used to return the number of quadratic coefficients in the row.
 * `rowqcol1`: First index in the triplets.
 * `rowqcol2`: Second index in the triplets.
 * `rowqcoef`: Coefficients in the triplets.


_**Further information:**_
Please refer to the C documentation for more details.

#### getqrows

_**Purpose:**_

   Returns the list indices of the rows that have quadratic coefficients.

_**Synopsis:**_

   `
getqrows(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `nrows`: Used to return the number of quadratic constraints in the matrix.
 * `rowind`: Array of length `QCONSTRAINTS` containing the indices of rows with quadratic coefficients in them.


#### getredcosts

_**Purpose:**_

   Returns the reduced costs from the incumbent solution during or after optimization of a continuous problem with optimize, lpoptimize or nlpoptimize.

_**Synopsis:**_

   `
getredcosts(prob, first = 0, last = getintattrib(prob, xpress:::INPUTCOLS) - 1)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the reduced costs. 
`last` | Last column in the reduced costs. 

_**Return value:**_
A list with the following elements:
 * `status`: Information about the reduced costs returned.
 * `djs`: Double array of length `last-first+1` containing the reduced costs for the variables.


#### getrhs

_**Purpose:**_

   Returns the right hand side elements for the rows in a given range.

_**Synopsis:**_

   `
getrhs(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the range. 
`last` | Last row in the range. 

_**Return value:**_
Double array of length `last-first+1`containing the right hand side elements.

#### getrhsrange

_**Purpose:**_

   Returns the right hand side range values for the rows in a given range.

_**Synopsis:**_

   `
getrhsrange(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the range. 
`last` | Last row in the range. 

_**Return value:**_
Double array of length `last-first+1`containing the right hand side range values.

#### getrowflags

_**Purpose:**_

   Retrieve if a range of rows have been set up as special rows.

_**Synopsis:**_

   `
getrowflags(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem 
`first` | First row index to be checked 
`last` | Last row index to be checked 

_**Return value:**_
Integer array of length `last-first+1`containing type of information \(see below\)

#### getrows

_**Purpose:**_

   Returns the nonzeros in the constraint matrix for the rows in a given range.

_**Synopsis:**_

   `
getrows(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the range. 
`last` | Last row in the range. 

_**Return value:**_
A list with the following elements:
 * `start`: Integer array containing the indices indicating the starting offsets in the `colind` and `colcoef` arrays for each requested row.
 * `colind`: Integer array of length `maxcoefs` containing the column indices of the nonzero elements for each row.
 * `colcoef`: Double array of length `maxcoefs` containing the nonzero element values.


#### getrowtype

_**Purpose:**_

   Returns the row types for the rows in a given range.

_**Synopsis:**_

   `
getrowtype(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the range. 
`last` | Last row in the range. 

_**Return value:**_
Character array of length `last-first+1`characters containing the row types:
 * `N`: indicates a free constraint;
 * `L`: indicates a `<=` constraint;
 * `E`: indicates an = constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint.


#### getscale

_**Purpose:**_

   Returns the the current scaling of the matrix.

_**Synopsis:**_

   `
getscale(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `rowscale`: Integer array of size ROWS that will contain the powers of `2` with which the rows are currently scaled.
 * `colscale`: Integer array of size COLS that will contain the powers of `2` with which the columns are currently scaled.


#### getscaledinfeas

_**Purpose:**_

   Returns a list primal and dual variables that are infeasible for the scaled original problem.

If the problem is currently presolved, it is postsolved before the function returns.

_**Synopsis:**_

   `
getscaledinfeas(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `nprimalcols`: Number of primal infeasible variables.
 * `nprimalrows`: Number of primal infeasible rows.
 * `ndualrows`: Number of dual infeasible rows.
 * `ndualcols`: Number of dual infeasible variables.
 * `x`: Integer array of length `nprimalcols` containing the indices of the primal infeasible variables.
 * `slack`: Integer array of length `nprimalrows` containing the indices of the primal infeasible rows.
 * `duals`: Integer array of length `ndualrows` containing the indices of the dual infeasible rows.
 * `djs`: Integer array of length `ndualcols` containing the indices of the dual infeasible variables.


_**Further information:**_
Please refer to the C documentation for more details.

#### getslacks

_**Purpose:**_

   Returns the slack values from the incumbent solution during or after optimization with optimize, mipoptimize, lpoptimize or nlpoptimize.

_**Synopsis:**_

   `
getslacks(prob, first = 0, last = getintattrib(prob, xpress:::INPUTROWS) - 1)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First row in the slacks. 
`last` | Last row in the slacks. 

_**Return value:**_
A list with the following elements:
 * `status`: Information about the slacks returned.
 * `slacks`: Double array of length `last-first+1` containing the value of the slack variables.


#### getsolution

_**Purpose:**_

   Returns the incumbent solution during or after optimization with optimize, mipoptimize, lpoptimize or nlpoptimize.

_**Synopsis:**_

   `
getsolution(prob, first = 0, last = getintattrib(prob, xpress:::INPUTCOLS) - 1)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the solution. 
`last` | Last column in the solution. 

_**Return value:**_
A list with the following elements:
 * `status`: Information about the solution returned.
 * `x`: Double array of length `last-first+1` containing the value of the primal variables.


#### getstrattrib

_**Purpose:**_

   Get string attribute.

This is the same as `getstringattrib`.

_**Synopsis:**_

   `
getstrattrib(prob, index)` 


#### getstrcontrol

_**Purpose:**_

   Get string control.

This is the same as `getstringcontrol`.

_**Synopsis:**_

   `
getstrcontrol(prob, index)` 


#### getstringattrib

_**Purpose:**_

   Enables users to recover the values of various string problem attributes.

Problem attributes are set during loading and optimization of a problem.

_**Synopsis:**_

   `
getstringattrib(prob, attrib)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`attrib` | Problem attribute whose value is to be returned. 

_**Return value:**_
The value of the attribute.

_**Further information:**_
Please refer to the C documentation for more details.

#### getstringcontrol

_**Purpose:**_

   Returns the value of a given string control parameters.

_**Synopsis:**_

   `
getstringcontrol(prob, control)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Control parameter whose value is to be returned. 

_**Return value:**_
The value of the control.

#### getub

_**Purpose:**_

   Returns the upper bounds for the columns in a given range.

_**Synopsis:**_

   `
getub(prob, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`first` | First column in the range. 
`last` | Last column in the range. 

_**Return value:**_
Double array of length `last-first+1`containing the upper bounds.

#### getunbvec

_**Purpose:**_

   Returns the index vector which causes the primal simplex or dual simplex algorithm to determine that a matrix is primal or dual unbounded respectively.

_**Synopsis:**_

   `
getunbvec(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The vector causing the problem to be detected as being primal or dual unbounded.

#### getversion

_**Purpose:**_

   Returns the full Optimizer version number in the form 15.10.03, where 15 is the major release, 10 is the minor release, and 03 is the build number.

_**Synopsis:**_

   `
getversion()` 


_**Return value:**_
The version string.

#### getversionnumbers

_**Purpose:**_

   Returns the Optimizer version numbers split into major, minor, and build number.

_**Synopsis:**_

   `
getversionnumbers()` 


_**Return value:**_
A list with the following elements:
 * `major`: The major version number.
 * `minor`: The minor version number.
 * `build`: The build number.


#### handlectrlc

_**Purpose:**_

   Handle Ctrl-C signals.

The function installs or removes a Ctrl-C handler that interacts with `prob`. Such a handler will invoke `XPRSinterrupt()`on `prob`if Ctrl-C is pressed. Note that there can be only one such handler at any time. If `handle`is `NULL`then a new handler is installed and the function returns an object that represents the previously installed handler. If `handle`is not `NULL`then the function assumes that the object was returned by a previous call to this function. In that case the previous handler is returned.

_**Synopsis:**_

   `
handlectrlc(prob, handle)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem object with which to handler should interact. 
`handle` | `NULL` to install a new handler, non- `NULL` to restore a previous handler. 

_**Return value:**_
A description of the previous handler if a new handler was installed, `NULL`otherwise.

#### handleintr

_**Purpose:**_

   Install or remove a handler for interruption.

This function installs or removes a function that is invoked periodically by the solver to check whether R has requested an interruption. If such a request is detected then the solver will interrupt itself at the next opportunitiy and will return gracefully to R.

_**Synopsis:**_

   `
handleintr(prob, set)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem into which the handler should be installed or from which it should be removed. 
`set` | `TRUE` to install a handler, `FALSE` to remove it. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Attention\! Checking for an interrupt may result in performance degradation, that is why interrupt checking is not enabled by default. Do not call this function while a solve is in progress, i.e., do not call it from a callback.

#### iisall

_**Purpose:**_

   Performs an automated search for independent Irreducible Infeasible Sets \(IIS\) in an infeasible problem.

_**Synopsis:**_

   `
iisall(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The input argument `prob`.

#### iisclear

_**Purpose:**_

   Resets the search for Irreducible Infeasible Sets \(IIS\).

_**Synopsis:**_

   `
iisclear(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The input argument `prob`.

#### iisfirst

_**Purpose:**_

   Initiates a search for an Irreducible Infeasible Set \(IIS\) in an infeasible problem.

_**Synopsis:**_

   `
iisfirst(prob, mode)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`mode` | The IIS search mode:
 * `0`: stops after finding the initial infeasible subproblem;
 * `1`: find an IIS, emphasizing simplicity of the IIS;
 * `2`: find an IIS, emphasizing a quick result.
 

_**Return value:**_
The status after the search:
 * `0`: success;
 * `1`: feasible problem;
 * `2`: error;
 * `3`: timeout or interruption.


#### iisisolations

_**Purpose:**_

   Performs the isolation identification procedure for an Irreducible Infeasible Set \(IIS\).

This function applies only to linear problems.

_**Synopsis:**_

   `
iisisolations(prob, iis)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`iis` | The number of the IIS identified by either iisfirst \(IIS\), iisnext \(IIS `-n`\) or iisall \(IIS `-a`\) in which the isolations should be identified. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### iisnext

_**Purpose:**_

   Continues the search for further Irreducible Infeasible Sets \(IIS\), or calls iisfirst \(IIS\) if no IIS has been identified yet.

_**Synopsis:**_

   `
iisnext(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The status after the search:
 * `0`: success;
 * `1`: no more IIS could be found, or problem is feasible if no iisfirst call preceded;
 * `2`: on error \(when the function returns nonzero\).


#### iisprint

_**Purpose:**_

   Prints a given Irreducible Infeasible Set \(IIS\) in the log.

If 0 is passed as the IIS number parameter, the initial infeasible subproblem is printed.

_**Synopsis:**_

   `
iisprint(prob, iis)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`iis` | The ordinal number of the IIS to be printed. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### iisstatus

_**Purpose:**_

   Returns statistics on the Irreducible Infeasible Sets \(IIS\) found so far by iisfirst \(IIS\), iisnext \(IIS `-n`\) or iisall \(IIS `-a`\).

_**Synopsis:**_

   `
iisstatus(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
A list with the following elements:
 * `niis`: The number of IISs found so far.
 * `nrows`: Array containing the number of rows in each IIS.
 * `ncols`: Array containing the number of bounds in each IIS.
 * `suminfeas`: Array containing the sum of infeasibilities in each IIS after the first phase simplex.
 * `numinfeas`: Array containing the number of infeasible variables in each IIS after the first phase simplex.


#### iiswrite

_**Purpose:**_

   Writes an LP/MPS/CSV file containing a given Irreducible Infeasible Set \(IIS\).

If 0 is passed as the IIS number parameter, the initial infeasible subproblem is written.

_**Synopsis:**_

   `
iiswrite(prob, iis, filetype, filename = NULL, flags = "lp")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`iis` | The ordinal number of the IIS to be written. 
`filetype` | Type of file to be created:
 * `0`: creates an lp/mps file containing the IIS as a linear programming problem;
 * `1`: creates a comma separated \(csv\) file containing the description and supplementary information on the given IIS.
 
`filename` | The name of the file to be created. 
`flags` | Flags passed to the writeprob function. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### init

_**Purpose:**_

   Initializes the Optimizer library.

This must be called before any other library routines.

_**Synopsis:**_

   `
init(path = "")` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`path` | The directory where the FICO Xpress license file is located. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Please refer to the C documentation for more details.

#### interrupt

_**Purpose:**_

   Interrupts the Optimizer algorithms.

_**Synopsis:**_

   `
interrupt(prob, reason = 9)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`reason` | The reason for stopping. Possible reasons are:
 * `_STOP_NONE`: do not stop;
 * `_STOP_TIMELIMIT`: time limit hit;
 * `_STOP_WORKLIMIT`: work limit hit;
 * `_STOP_CTRLC`: control C hit;
 * `_STOP_NODELIMIT`: node limit hit;
 * `_STOP_ITERLIMIT`: iteration limit hit;
 * `_STOP_MIPGAP`: MIP gap is sufficiently small;
 * `_STOP_SOLLIMIT`: solution limit hit;
 * `_STOP_USER`: user interrupt;
 * `_STOP_NEXTOBJECTIVE`: stop the current solve, but continue with solving the next objective \(see below\);
 * `>= 1000`: user defined value.
 

_**Return value:**_
The input argument `prob`.

#### license

_**Purpose:**_

   Wraps callable C library function XPRSlicense.

Please refer to the OEM guide for details.

_**Synopsis:**_

   `
license(i, c)` 


#### loadbasis

_**Purpose:**_

   Loads a basis from the user's areas.

_**Synopsis:**_

   `
loadbasis(prob, rowstat, colstat)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowstat` | Integer array of length ORIGINALROWS containing the basis status of the slack, surplus or artificial variable associated with each row. The status must be one of:
 * `_BASISSTATUS_NONBASIC_LOWER (0)`: slack, surplus or artificial is non-basic at lower bound;
 * `_BASISSTATUS_BASIC (1)`: slack, surplus or artificial is basic;
 * `_BASISSTATUS_NONBASIC_UPPER (2)`: slack or surplus is non-basic at upper bound.
 * `_BASISSTATUS_SUPERBASIC (3)`: slack or surplus is super-basic.
 
`colstat` | Integer array of length ORIGINALCOLS containing the basis status of each of the columns in the constraint matrix. The status must be one of:
 * `_BASISSTATUS_NONBASIC_LOWER (0)`: variable is non-basic at lower bound or superbasic at zero if the variable has no lower bound;
 * `_BASISSTATUS_BASIC (1)`: variable is basic;
 * `_BASISSTATUS_NONBASIC_UPPER (2)`: variable is at upper bound;
 * `_BASISSTATUS_SUPERBASIC (3)`: variable is super-basic.
 

_**Return value:**_
The input argument `prob`.

#### loadbranchdirs

_**Purpose:**_

   Loads directives into the current problem to specify which MIP entities the Optimizer should continue to branch on when a node solution is integer feasible.

_**Synopsis:**_

   `
loadbranchdirs(prob, colind, dir = NULL, ncols = x_max_vec_length(colind, dir))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the column numbers. 
`dir` | Integer array of length `ncols` containing either 0 or 1 for the entities given in `colind`. 
`ncols` | Number of directives. 

_**Return value:**_
The input argument `prob`.

#### loadcuts

_**Purpose:**_

   Loads cuts from the cut pool into the matrix.

Without calling `loadcuts`the cuts will remain in the cut pool but will not be active at the node. Cuts loaded at a node remain active at all descendant nodes unless they are deleted using delcuts.

_**Synopsis:**_

   `
loadcuts(


  prob,


  cutind,


  cuttype = 0,


  interp = -1,


  ncuts = x_max_vec_length(cutind)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`cutind` | Array of length `ncuts` containing the cuts to be loaded into the matrix. 
`cuttype` | Cut type. 
`interp` | The way in which the cut type is interpreted:
 * `-1`: load all cuts;
 * `1`: treat cut types as numbers;
 * `2`: treat cut types as bit-vectors \(compare Section \) - load cut if any bit matches any bit set in `cuttype`;
 * `3`: treat cut types as bit-vectors \(compare Section \) - `0` load cut if all bits match those set in `cuttype`.
 
`ncuts` | Number of cuts to load. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loaddelayedrows

_**Purpose:**_

   Specifies that a set of rows in the matrix will be treated as delayed rows during a tree search.

These are rows that must be satisfied for any integer solution, but will not be loaded into the active set of constraints until required.

_**Synopsis:**_

   `
loaddelayedrows(prob, rowind, nrows = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | An array of row indices to treat as delayed rows. 
`nrows` | The number of delayed rows. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loaddirs

_**Purpose:**_

   Loads directives into the matrix.

_**Synopsis:**_

   `
loaddirs(


  prob,


  colind,


  priority = NULL,


  dir = NULL,


  uppseudo = NULL,


  downpseudo = NULL,


  ndirs = x_max_vec_length(colind, priority, dir, uppseudo, downpseudo)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ndirs` containing the column numbers. 
`priority` | Integer array of length `ndirs` containing the priorities for the columns or sets. 
`dir` | Character array of length `ndirs` specifying the branching direction for each column or set:
 * `U`: the entity is to be forced up;
May be `NULL`if not required. * `D`: the entity is to be forced down;
 * `N`: not specified.
 
`uppseudo` | Double array of length `ndirs` containing the up pseudo costs for the columns or sets. 
`downpseudo` | Double array of length `ndirs` containing the down pseudo costs for the columns or sets. 
`ndirs` | Number of directives. 

_**Return value:**_
The input argument `prob`.

#### loadglobal

_**Purpose:**_

   Used to load a MIP problem into the Optimizer data structures.

_**Synopsis:**_

   `
loadglobal(


  prob,


  probname,


  rowtype,


  rhs,


  rng,


  objcoef,


  start,


  collen,


  rowind,


  rowcoef,


  lb,


  ub,


  coltype,


  entind,


  limit,


  settype,


  setstart,


  setind,


  refval,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nentities = x_max_vec_length(coltype, entind, limit),


  nsets = x_max_vec_length(settype)


)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``loadmip``

#### loadlp

_**Purpose:**_

   Enables the user to pass a matrix directly to the Optimizer, rather than reading the matrix from a file.

_**Synopsis:**_

   `
loadlp(


  prob,


  probname = "",


  rowtype = NULL,


  rhs = NULL,


  rng = NULL,


  objcoef = NULL,


  start = NULL,


  collen = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing a name for the problem. 
`rowtype` | Character array of length `nrows` containing the row types:
 * `L`: indicates a `<=` constraint;
May be `NULL`if the problem contains no rows. * `E`: indicates an = constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side coefficients of the rows. 
`rng` | Double array of length `nrows` containing the range values for range rows. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients. 
`start` | Integer array containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`collen` | Integer array of length `ncols` containing the number of nonzero elements in each column. 
`rowind` | Integer array containing the row indices for the nonzero elements in each column. 
`rowcoef` | Double array containing the nonzero element values; length as for `rowind`. 
`lb` | Double array of length `ncols` containing the lower bounds on the columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the columns. 
`ncols` | Number of structural columns in the matrix. 
`nrows` | Number of rows in the matrix \(not including the objective\). 

_**Return value:**_
The input argument `prob`.

#### loadlpsol

_**Purpose:**_

   Loads an LP solution for the problem into the Optimizer.

_**Synopsis:**_

   `
loadlpsol(prob, x = NULL, slack = NULL, duals = NULL, djs = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`x` | Optional: Double array of length COLS \(for the original problem and not the presolve problem\) containing the values of the variables. 
`slack` | Optional: double array of length ROWS containing the values of slack variables. 
`duals` | Optional: double array of length ROWS containing the values of dual variables. 
`djs` | Optional: double array of length COLS containing the values of reduced costs. 

_**Return value:**_
The status. The status is one of:
 * `0`: Solution is loaded.
 * `1`: Solution is not loaded because the problem is in presolved status.


#### loadmip

_**Purpose:**_

   Used to load a MIP problem into the Optimizer data structures.

Integer, binary, partial integer, semi-continuous and semi-continuous integer variables can be defined, together with sets of type 1 and 2. The reference row values for the set members are passed as an array rather than specifying a reference row.

_**Synopsis:**_

   `
loadmip(


  prob,


  probname = "",


  rowtype = NULL,


  rhs = NULL,


  rng = NULL,


  objcoef = NULL,


  start = NULL,


  collen = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  coltype = NULL,


  entind = NULL,


  limit = NULL,


  settype = NULL,


  setstart = NULL,


  setind = NULL,


  refval = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nentities = x_max_vec_length(coltype, entind, limit),


  nsets = x_max_vec_length(settype)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing a name for the problem. 
`rowtype` | Character array of length `nrows` containing the row types:
 * `L`: indicates a `<=` constraint;
May be `NULL`if the problem contains no rows. * `E`: indicates an = constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side coefficients of the rows. 
`rng` | Double array of length `nrows` containing the range values for range rows. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients. 
`start` | Integer array containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`collen` | Integer array of length `ncols` containing the number of nonzero elements in each column. 
`rowind` | Integer array containing the row indices for the nonzero elements in each column. 
`rowcoef` | Double array containing the nonzero element values; length as for `rowind`. 
`lb` | Double array of length `ncols` containing the lower bounds on the columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the columns. 
`coltype` | Character array of length `nentities` containing the entity types:
 * `B`: binary variables;
May be `NULL`if all variables are continuous. * `I`: integer variables;
 * `P`: partial integer variables;
 * `S`: semi-continuous variables;
 * `R`: semi-continuous integer variables.
 
`entind` | Integer array of length `nentities` containing the column indices of the MIP entities. 
`limit` | Double array of length `nentities` containing the integer limits for the partial integer variables and lower bounds for semi-continuous and semi-continuous integer variables \(any entries in the positions corresponding to binary and integer variables will be ignored\). 
`settype` | Character array of length `nsets` containing the set types:
 * `1`: SOS1 type sets;
May be `NULL`if not required. * `2`: SOS2 type sets.
 
`setstart` | Integer array containing the offsets in the `setind` and `refval` arrays indicating the start of each set. 
`setind` | Integer array of length `setstart[nsets]-1` containing the columns in each set. 
`refval` | Double array of length `setstart[nsets]-1` containing the reference row entries for each member of the sets. 
`ncols` | Number of structural columns in the matrix. 
`nrows` | Number of rows in the matrix not \(including the objective row\). 
`nentities` | Number of binary, integer, semi-continuous, semi-continuous integer and partial integer entities. 
`nsets` | Number of SOS1 and SOS2 sets. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loadmipsol

_**Purpose:**_

   Loads a starting MIP solution for the problem into the Optimizer.

_**Synopsis:**_

   `
loadmipsol(prob, x)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`x` | Double array of length COLS \(for the original problem and not the presolve problem\) containing the values of the variables. 

_**Return value:**_
The status. The status is one of:
 * `-1`: Solution rejected because an error occurred;
 * `0`: Solution accepted.


#### loadmiqcqp

_**Purpose:**_

   Used to load a mixed integer quadratic problem with quadratic constraints into the Optimizer data structure.

Such a problem may have quadratic terms in its objective function as well as in its constraints. Integer, binary, partial integer, semi-continuous and semi-continuous integer variables can be defined, together with sets of type 1 and 2. The reference row values for the set members are passed as an array rather than specifying a reference row.

_**Synopsis:**_

   `
loadmiqcqp(


  prob,


  probname = "",


  rowtype = NULL,


  rhs = NULL,


  rng = NULL,


  objcoef = NULL,


  start = NULL,


  collen = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  objqcol1 = NULL,


  objqcol2 = NULL,


  objqcoef = NULL,


  qrowind = NULL,


  nrowqcoefs = NULL,


  rowqcol1 = NULL,


  rowqcol2 = NULL,


  rowqcoef = NULL,


  coltype = NULL,


  entind = NULL,


  limit = NULL,


  settype = NULL,


  setstart = NULL,


  setind = NULL,


  refval = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nobjqcoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef),


  nqrows = x_max_vec_length(qrowind, nrowqcoefs),


  nentities = x_max_vec_length(coltype, entind, limit),


  nsets = x_max_vec_length(settype)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing a name for the problem. 
`rowtype` | Character array of length `nrows` containing the row types:
 * `L`: indicates a `<=` constraint \(use this one for quadratic constraints as well\);
May be `NULL`if the problem contains no rows. * `E`: indicates an `=` constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side coefficients of the rows. 
`rng` | Double array of length `nrows` containing the range values for range rows. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients. 
`start` | Integer array containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`collen` | Integer array of length `ncols` containing the number of nonzero elements in each column. 
`rowind` | Integer array containing the row indices for the nonzero elements in each column. 
`rowcoef` | Double array containing the nonzero element values; length as for `rowind`. 
`lb` | Double array of length `ncols` containing the lower bounds on the columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the columns. 
`objqcol1` | Integer array of size `nobjqcoefs` containing the column index of the first variable in each quadratic term. 
`objqcol2` | Integer array of size `nobjqcoefs` containing the column index of the second variable in each quadratic term. 
`objqcoef` | Double array of size `nobjqcoefs` containing the quadratic coefficients. 
`qrowind` | Integer array of size `nqrows`, containing the indices of rows with quadratic matrices in them. 
`nrowqcoefs` | Integer array of size `nqrows`, containing the number of nonzeros in each quadratic constraint matrix. 
`rowqcol1` | Integer array of size `nqcelem`, where `nqcelem` equals the sum of the elements in `nrowqcoefs` \(i.e. the total number of quadratic matrix elements in all the constraints\). 
`rowqcol2` | Integer array of size `nqcelem`, containing the second index for the quadratic constraint matrices. 
`rowqcoef` | Integer array of size `nqcelem`, containing the coefficients for the quadratic constraint matrices. 
`coltype` | Character array of length `nentities` containing the entity types:
 * `B`: binary variables;
May be `NULL`if all variables are continuous. * `I`: integer variables;
 * `P`: partial integer variables;
 * `S`: semi-continuous variables;
 * `R`: semi-continuous integer variables.
 
`entind` | Integer array of length `nentities` containing the column indices of the MIP entities. 
`limit` | Double array of length `nentities` containing the integer limits for the partial integer variables and lower bounds for semi-continuous and semi-continuous integer variables \(any entries in the positions corresponding to binary and integer variables will be ignored\). 
`settype` | Character array of length `nsets` containing the set types:
 * `1`: SOS1 type sets;
May be `NULL`if not required. * `2`: SOS2 type sets.
 
`setstart` | Integer array containing the offsets in the `setind` and `refval` arrays indicating the start of each set. 
`setind` | Integer array of length `setstart[nsets]-1` containing the columns in each set. 
`refval` | Double array of length `setstart[nsets]-1` containing the reference row entries for each member of the sets. 
`ncols` | Number of structural columns in the matrix. 
`nrows` | Number of rows in the matrix \(not including the objective row\). 
`nobjqcoefs` | Number of quadratic terms. 
`nqrows` | Number of rows containing quadratic matrices. 
`nentities` | Number of binary, integer, semi-continuous, semi-continuous integer and partial integer entities. 
`nsets` | Number of SOS1 and SOS2 sets. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loadmiqp

_**Purpose:**_

   Used to load a MIQP problem, hence a MIP with quadratic objective coefficients, into the Optimizer data structures.

Integer, binary, partial integer, semi-continuous and semi-continuous integer variables can be defined, together with sets of type 1 and 2. The reference row values for the set members are passed as an array rather than specifying a reference row.

_**Synopsis:**_

   `
loadmiqp(


  prob,


  probname = "",


  rowtype = NULL,


  rhs = NULL,


  rng = NULL,


  objcoef = NULL,


  start = NULL,


  collen = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  objqcol1 = NULL,


  objqcol2 = NULL,


  objqcoef = NULL,


  coltype = NULL,


  entind = NULL,


  limit = NULL,


  settype = NULL,


  setstart = NULL,


  setind = NULL,


  refval = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nobjqcoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef),


  nentities = x_max_vec_length(coltype, entind, limit),


  nsets = x_max_vec_length(settype)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing a name for the problem. 
`rowtype` | Character array of length `nrows` containing the row type:
 * `L`: indicates a `<=` constraint;
May be `NULL`if the problem contains no rows. * `E`: indicates an = constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side coefficients of the rows. 
`rng` | Double array of length `nrows` containing the range values for range rows. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients. 
`start` | Integer array containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`collen` | Integer array of length `ncols` containing the number of nonzero elements in each column. 
`rowind` | Integer array containing the row indices for the nonzero elements in each column. 
`rowcoef` | Double array containing the nonzero element values; length as for `rowind`. 
`lb` | Double array of length `ncols` containing the lower bounds on the columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the columns. 
`objqcol1` | Integer array of size `nobjqcoefs` containing the column index of the first variable in each quadratic term. 
`objqcol2` | Integer array of size `nobjqcoefs` containing the column index of the second variable in each quadratic term. 
`objqcoef` | Double array of size `nobjqcoefs` containing the quadratic coefficients. 
`coltype` | Character array of length `nentities` containing the entity types:
 * `B`: binary variables;
May be `NULL`if all variables are continuous. * `I`: integer variables;
 * `P`: partial integer variables;
 * `S`: semi-continuous variables;
 * `R`: semi-continuous integers.
 
`entind` | Integer array of length `nentities` containing the column indices of the MIP entities. 
`limit` | Double array of length `nentities` containing the integer limits for the partial integer variables and lower bounds for semi-continuous and semi-continuous integer variables \(any entries in the positions corresponding to binary and integer variables will be ignored\). 
`settype` | Character array of length `nsets` containing:
 * `1`: SOS1 type sets;
May be `NULL`if not required. * `2`: SOS2 type sets.
 
`setstart` | Integer array containing the offsets in the `setind` and `refval` arrays indicating the start of each set. 
`setind` | Integer array of length `setstart[nsets]-1` containing the columns in each set. 
`refval` | Double array of length `setstart[nsets]-1` containing the reference row entries for each member of the sets. 
`ncols` | Number of structural columns in the matrix. 
`nrows` | Number of rows in the matrix \(not including the objective\). 
`nobjqcoefs` | Number of quadratic terms. 
`nentities` | Number of binary, integer, semi-continuous, semi-continuous integer and partial integer entities. 
`nsets` | Number of SOS1 and SOS2 sets. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loadmodelcuts

_**Purpose:**_

   Specifies that a set of rows in the matrix will be treated as model cuts.

_**Synopsis:**_

   `
loadmodelcuts(prob, rowind, nrows = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | An array of row indices to be treated as cuts. 
`nrows` | The number of model cuts. 

_**Return value:**_
The input argument `prob`.

#### loadpresolvebasis

_**Purpose:**_

   Loads a presolved basis from the user's areas.

_**Synopsis:**_

   `
loadpresolvebasis(prob, rowstat, colstat)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowstat` | Integer array of length ROWS containing the basis status of the slack, surplus or artificial variable associated with each row. The status must be one of:
 * `_BASISSTATUS_NONBASIC_LOWER (0)`: slack, surplus or artificial is non-basic at lower bound;
 * `_BASISSTATUS_BASIC (1)`: slack, surplus or artificial is basic;
 * `_BASISSTATUS_NONBASIC_UPPER (2)`: slack or surplus is non-basic at upper bound.
 
`colstat` | Integer array of length COLS containing the basis status of each of the columns in the matrix. The status must be one of:
 * `_BASISSTATUS_NONBASIC_LOWER (0)`: variable is non-basic at lower bound or superbasic at zero if the variable has no lower bound;
 * `_BASISSTATUS_BASIC (1)`: variable is basic;
 * `_BASISSTATUS_NONBASIC_UPPER (2)`: variable is at upper bound;
 * `_BASISSTATUS_SUPERBASIC (3)`: variable is super-basic.
 

_**Return value:**_
The input argument `prob`.

#### loadpresolvedirs

_**Purpose:**_

   Loads directives into the presolved matrix.

_**Synopsis:**_

   `
loadpresolvedirs(


  prob,


  colind,


  priority = NULL,


  dir = NULL,


  uppseudo = NULL,


  downpseudo = NULL,


  ndirs = x_max_vec_length(colind, priority, dir, uppseudo, downpseudo)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ndirs` containing the column numbers. 
`priority` | Integer array of length `ndirs` containing the priorities for the columns or sets. 
`dir` | Character array of length `ndirs` specifying the branching direction for each column or set:
 * `U`: the entity is to be forced up;
May be `NULL`if not required. * `D`: the entity is to be forced down;
 * `N`: not specified.
 
`uppseudo` | Double array of length `ndirs` containing the up pseudo costs for the columns or sets. 
`downpseudo` | Double array of length `ndirs` containing the down pseudo costs for the columns or sets. 
`ndirs` | Number of directives. 

_**Return value:**_
The input argument `prob`.

#### loadqcqp

_**Purpose:**_

   Used to load a quadratic problem with quadratic side constraints into the Optimizer data structure.

Such a problem may have quadratic terms in its objective function as well as in its constraints.

_**Synopsis:**_

   `
loadqcqp(


  prob,


  probname = "",


  rowtype = NULL,


  rhs = NULL,


  rng = NULL,


  objcoef = NULL,


  start = NULL,


  collen = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  objqcol1 = NULL,


  objqcol2 = NULL,


  objqcoef = NULL,


  qrowind = NULL,


  nrowqcoefs = NULL,


  rowqcol1 = NULL,


  rowqcol2 = NULL,


  rowqcoef = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nobjqcoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef),


  nqrows = x_max_vec_length(qrowind, nrowqcoefs)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing a name for the problem. 
`rowtype` | Character array of length `nrows` containing the row types:
 * `L`: indicates a `<=` constraint \(use this one for quadratic constraints as well\);
May be `NULL`if the problem contains no rows. * `E`: indicates an `=` constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side coefficients of the rows. 
`rng` | Double array of length `nrows` containing the range values for range rows. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients. 
`start` | Integer array containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`collen` | Integer array of length `ncols` containing the number of nonzero elements in each column. 
`rowind` | Integer array containing the row indices for the nonzero elements in each column. 
`rowcoef` | Double array containing the nonzero element values; length as for `rowind`. 
`lb` | Double array of length `ncols` containing the lower bounds on the columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the columns. 
`objqcol1` | Integer array of size `nobjqcoefs` containing the column index of the first variable in each quadratic term. 
`objqcol2` | Integer array of size `nobjqcoefs` containing the column index of the second variable in each quadratic term. 
`objqcoef` | Double array of size `nobjqcoefs` containing the quadratic coefficients. 
`qrowind` | Integer array of size `nqrows`, containing the indices of rows with quadratic matrices in them. 
`nrowqcoefs` | Integer array of size `nqrows`, containing the number of nonzeros in each quadratic constraint matrix. 
`rowqcol1` | Integer array of size `nqcelem`, where `nqcelem` equals the sum of the elements in `nrowqcoefs` \(i.e. the total number of quadratic matrix elements in all the constraints\). 
`rowqcol2` | Integer array of size `nqcelem`, containing the second index for the quadratic constraint matrices. 
`rowqcoef` | Integer array of size `nqcelem`, containing the coefficients for the quadratic constraint matrices. 
`ncols` | Number of structural columns in the matrix. 
`nrows` | Number of rows in the matrix \(not including the objective row\). 
`nobjqcoefs` | Number of quadratic terms. 
`nqrows` | Number of rows containing quadratic matrices. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loadqcqpglobal

_**Purpose:**_

   Used to load a mixed integer quadratic problem with quadratic constraints into the Optimizer data structure.

_**Synopsis:**_

   `
loadqcqpglobal(


  prob,


  probname,


  rowtype,


  rhs,


  rng,


  objcoef,


  start,


  collen,


  rowind,


  rowcoef,


  lb,


  ub,


  objqcol1,


  objqcol2,


  objqcoef,


  qrowind,


  nrowqcoefs,


  rowqcol1,


  rowqcol2,


  rowqcoef,


  nentities,


  nsets,


  coltype,


  entind,


  limit,


  settype,


  setstart,


  setind,


  refval,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nobjqcoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef),


  nqrows = x_max_vec_length(qrowind, nrowqcoefs)


)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``loadmiqcqp``

#### loadqglobal

_**Purpose:**_

   Used to load a MIQP problem, hence a MIP with quadratic objective coefficients, into the Optimizer data structures.

_**Synopsis:**_

   `
loadqglobal(


  prob,


  probname,


  rowtype,


  rhs,


  rng,


  objcoef,


  start,


  collen,


  rowind,


  rowcoef,


  lb,


  ub,


  objqcol1,


  objqcol2,


  objqcoef,


  nentities,


  nsets,


  coltype,


  entind,


  limit,


  settype,


  setstart,


  setind,


  refval,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nobjqcoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef)


)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``loadmiqp``

#### loadqp

_**Purpose:**_

   Used to load a quadratic problem into the Optimizer data structure.

Such a problem may have quadratic terms in its objective function, although not in its constraints.

_**Synopsis:**_

   `
loadqp(


  prob,


  probname = "",


  rowtype = NULL,


  rhs = NULL,


  rng = NULL,


  objcoef = NULL,


  start = NULL,


  collen = NULL,


  rowind = NULL,


  rowcoef = NULL,


  lb = NULL,


  ub = NULL,


  objqcol1 = NULL,


  objqcol2 = NULL,


  objqcoef = NULL,


  ncols = x_max_vec_length(objcoef, lb, ub),


  nrows = x_max_vec_length(rowtype, rhs, rng),


  nobjqcoefs = x_max_vec_length(objqcol1, objqcol2, objqcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing a name for the problem. 
`rowtype` | Character array of length `nrows` containing the row types:
 * `L`: indicates a `<=` constraint;
May be `NULL`if the problem contains no rows. * `E`: indicates an = constraint;
 * `G`: indicates a `>=` constraint;
 * `R`: indicates a range constraint;
 * `N`: indicates a nonbinding constraint.
 
`rhs` | Double array of length `nrows` containing the right hand side coefficients of the rows. 
`rng` | Double array of length `nrows` containing the range values for range rows. 
`objcoef` | Double array of length `ncols` containing the objective function coefficients. 
`start` | Integer array containing the offsets in the `rowind` and `rowcoef` arrays of the start of the elements for each column. 
`collen` | Integer array of length `ncols` containing the number of nonzero elements in each column. 
`rowind` | Integer array containing the row indices for the nonzero elements in each column. 
`rowcoef` | Double array containing the nonzero element values; length as for `rowind`. 
`lb` | Double array of length `ncols` containing the lower bounds on the columns. 
`ub` | Double array of length `ncols` containing the upper bounds on the columns. 
`objqcol1` | Integer array of size `nobjqcoefs` containing the column index of the first variable in each quadratic term. 
`objqcol2` | Integer array of size `nobjqcoefs` containing the column index of the second variable in each quadratic term. 
`objqcoef` | Double array of size `nobjqcoefs` containing the quadratic coefficients. 
`ncols` | Number of structural columns in the matrix. 
`nrows` | Number of rows in the matrix \(not including the objective row\). 
`nobjqcoefs` | Number of quadratic terms. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### loadsecurevecs

_**Purpose:**_

   Allows the user to mark rows and columns in order to prevent the presolve removing these rows and columns from the matrix.

_**Synopsis:**_

   `
loadsecurevecs(


  prob,


  rowind = NULL,


  colind = NULL,


  nrows = x_max_vec_length(rowind),


  ncols = x_max_vec_length(colind)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `nrows` containing the rows to be marked. 
`colind` | Integer array of length `ncols` containing the columns to be marked. 
`nrows` | Number of rows to be marked. 
`ncols` | Number of columns to be marked. 

_**Return value:**_
The input argument `prob`.

#### lpoptimize

_**Purpose:**_

   This function begins a search for the optimal continuous \(LP\) solution.

The direction of optimization is given by OBJSENSE. The status of the problem when the function completes can be checked using LPSTATUS. Any MIP entities in the problem will be ignored.

_**Synopsis:**_

   `
lpoptimize(prob, flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`flags` | Flags to pass to `lpoptimize` \( `LPOPTIMIZE`\). The default is `""` or `NULL`, in which case the algorithm used is determined by the DEFAULTALG control. If the argument includes:
 * `b`: the problem will be solved using the Newton barrier method, or the Hybrid gradient method if BARALG is set to 4 or 5;
 * `p`: the problem will be solved using the primal simplex algorithm;
 * `d`: the problem will be solved using the dual simplex algorithm;
 * `n`: the network part of the problem will be identified and solved using the network simplex algorithm;
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### mipoptimize

_**Purpose:**_

   This function begins a tree search for the optimal MIP solution.

The direction of optimization is given by OBJSENSE. The status of the problem when the function completes can be checked using MIPSTATUS.

_**Synopsis:**_

   `
mipoptimize(prob, flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`flags` | Flags to pass to mipoptimize \(MIPOPTIMIZE\), which specifies how to solve the initial continuous problem where the MIP entities are relaxed. The default is `""` or `NULL`, in which case the choice of the LP algorithm is left to the solver. If the argument includes:
 * `b`: the initial continuous relaxation will be solved using the Newton barrier method \(or the hybrid gradient method if BARALG is set to 4 or 5\);
 * `p`: the initial continuous relaxation will be solved using the primal simplex algorithm;
 * `d`: the initial continuous relaxation will be solved using the dual simplex algorithm;
 * `n`: the network part of the initial continuous relaxation will be identified and solved using the network simplex algorithm;
 * `l`: \(deprecated\) stop after having solved the initial continous relaxation. This flag is deprecated, use the MIPSTOPSTAGE control instead.
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### nlpaddformulas

_**Purpose:**_

   Add non-linear formulas to the SLP problem.

_**Synopsis:**_

   `
nlpaddformulas(


  prob,


  rowind,


  formulastart,


  parsed,


  type,


  value,


  ncoefs = x_max_vec_length(rowind)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`rowind` | Integer array holding index of row for the coefficient. 
`formulastart` | Integer array of length `ncoefs+1` holding the start position in the arrays `type` and `value` of the formula for the coefficients. 
`parsed` | Integer indicating whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the formula for each coefficient. 
`value` | Array of values corresponding to the types in `type`. 
`ncoefs` | Number of non-linear coefficients to be added. 

_**Return value:**_
The input argument `prob`.

#### nlpchgformula

_**Purpose:**_

   Add or replace a single matrix formula using a parsed or unparsed formula

_**Synopsis:**_

   `
nlpchgformula(prob, row, parsed, type, value)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row for the coefficient. 
`parsed` | Integer indicating the whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the description and formula for each item. 
`value` | Array of values corresponding to the types in `type`. 

_**Return value:**_
The input argument `prob`.

#### nlpchgformulastr

_**Purpose:**_

   Add or replace a single matrix formula using a character string for the formula.

_**Synopsis:**_

   `
nlpchgformulastr(prob, row, formula)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`row` | The index of the matrix row for the coefficient. 
`formula` | Character string holding the formula with the tokens separated by spaces. 

_**Return value:**_
The input argument `prob`.

#### nlpdelformulas

_**Purpose:**_

   Delete nonlinear formulas from the current problem

_**Synopsis:**_

   `
nlpdelformulas(prob, rowind, nformulas = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`rowind` | Row indices of the SLP nonlinear formulas to delete. 
`nformulas` | Number of SLP nonlinear formulas to delete. 

_**Return value:**_
The input argument `prob`.

#### nlpevaluateformula

_**Purpose:**_

   Evaluate a formula using the current values of the variables

_**Synopsis:**_

   `
nlpevaluateformula(prob, parsed, type, values)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`parsed` | integer indicating whether the formula of the item is in internal unparsed format \( `parsed` =0\) or parsed \(reverse Polish\) format \( `parsed` =1\). 
`type` | Integer array of token types for the formula. 
`values` | Double array of values corresponding to `type`. 

_**Return value:**_
The result of the calculation.

#### nlpgetformula

_**Purpose:**_

   Retrieve a single matrix formula as a formula split into tokens.

_**Synopsis:**_

   `
nlpgetformula(prob, row, parsed)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the formula. 
`parsed` | Integer indicating whether the formula of the row is to be returned in internal unparsed format \( `parsed` =0\) or parsed \(reverse Polish\) format \( `parsed` =1\). 

_**Return value:**_
A list with the following elements:
 * `ntypes`: Will be set to the length of the formula, including the `XSLP_EOF` token.
 * `type`: Integer array containing the token types for the formula.
 * `value`: Double array of values corresponding to `type`.


#### nlpgetformularows

_**Purpose:**_

   Retrieve the list of positions of the nonlinear formulas in the problem

_**Synopsis:**_

   `
nlpgetformularows(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
A list with the following elements:
 * `nformulas`: Integer used to return the total number of nonlinear formulas in the problem.
 * `rowind`: Integer array used for returning the row positions of the nonlinear formulas.


#### nlpgetformulastr

_**Purpose:**_

   Retrieve a single matrix formula in a character string.

_**Synopsis:**_

   `
nlpgetformulastr(prob, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | Integer holding the row index for the formula. 

_**Return value:**_
Character buffer containing the formula in the same format as used for input from a file.

#### nlploadformulas

_**Purpose:**_

   Load non-linear formulas into the SLP problem

_**Synopsis:**_

   `
nlploadformulas(


  prob,


  rowind,


  formulastart,


  parsed,


  type,


  value,


  nnlpcoefs = x_max_vec_length(rowind)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`rowind` | Integer array holding index of row for the coefficient. 
`formulastart` | Integer array of length `nnlpcoefs+1` holding the start position in the arrays `type` and `value` of the formula for the coefficients. 
`parsed` | Integer indicating whether the token arrays are formatted as internal unparsed \( `parsed` =0\) or internal parsed reverse Polish \( `parsed` =1\). 
`type` | Array of token types providing the formula for each coefficient. 
`value` | Array of values corresponding to the types in `type`. 
`nnlpcoefs` | Number of non-linear coefficients to be loaded. 

_**Return value:**_
The input argument `prob`.

#### nlpoptimize

_**Purpose:**_

   Maximize or minimize an SLP problem

_**Synopsis:**_

   `
nlpoptimize(prob, flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`flags` | Flags to pass to `XSLPnlpoptimize`. The default is `""` or `NULL`, in which case the solve stops after solving the root relaxation \(or a continuous problem to completion\) and it restarts the solve without continuing.
 * `g`: Perform a branch and bound search if necessary to solve the problem;
All other flags are passed to the Optimizer: see lpoptimize. * `c`: continue a previously interrupted solve.
 

_**Return value:**_
The input argument `prob`.

#### nlppostsolve

_**Purpose:**_

   Restores the problem to its pre-solve state

_**Synopsis:**_

   `
nlppostsolve(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### nlpprintevalinfo

_**Purpose:**_

   Print a summary of any evaluation errors that may have occurred during solving a problem

_**Synopsis:**_

   `
nlpprintevalinfo(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### nlpsetcurrentiv

_**Purpose:**_

   Transfer the current solution to initial values

_**Synopsis:**_

   `
nlpsetcurrentiv(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### nlpsetfunctionerror

_**Purpose:**_

   Set the function error flag for the problem

_**Synopsis:**_

   `
nlpsetfunctionerror(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### nlpsetinitval

_**Purpose:**_

   Set the initial value of columns

_**Synopsis:**_

   `
nlpsetinitval(prob, colind, initial, nvars = x_max_vec_length(colind, initial))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`colind` | Array of length `nvars` with index of the column for which the initial value is provided. 
`initial` | Array of length `nvars` with the initial value. 
`nvars` | Number of variables for which the initial value is to be set. 

_**Return value:**_
The input argument `prob`.

#### nlpvalidate

_**Purpose:**_

   Validate the feasibility of constraints in a converged solution

_**Synopsis:**_

   `
nlpvalidate(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### nlpvalidatekkt

_**Purpose:**_

   Validates the first order optimality conditions also known as the Karush-Kuhn-Tucker \(KKT\) conditions versus the currect solution

_**Synopsis:**_

   `
nlpvalidatekkt(prob, mode, respectbasis, updatemult, violtarget)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`mode` | The calculation mode can be:
 * `0`: recalculate the reduced costs at the current solution using the current dual solution.
 * `1`: minimize the sum of KKT violations by adjusting the dual solution.
 * `2`: perform both.
 
`respectbasis` | The following ways are defined to assess if a constraint is active:
 * `0`: evaluate the recalculated slack activity versus XSLP\_ECFTOL\_R.
 * `1`: use the basis status of the slack in the linearized problem if available.
 * `2`: use both.
 
`updatemult` | The calculated values can be:
 * `0`: only used to calculate the XSLP\_VALIDATIONINDEX\_K measure.
 * `1`: used to update the current dual solution and reduced costs.
 
`violtarget` | When calculating the best KKT multipliers, it is possible to enforce an even distribution of reduced costs violations by enforcing a bound on them. 

_**Return value:**_
The input argument `prob`.

#### nlpvalidaterow

_**Purpose:**_

   Prints an extensive analysis on a given constraint of the SLP problem

_**Synopsis:**_

   `
nlpvalidaterow(prob, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the row to be analyzed 

_**Return value:**_
The input argument `prob`.

#### nlpvalidatevector

_**Purpose:**_

   Validate the feasibility of constraints for a given solution

_**Synopsis:**_

   `
nlpvalidatevector(prob, solution)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`solution` | A vector of length `COLS` containing the solution vector to be checked. 

_**Return value:**_
A list with the following elements:
 * `suminf`: The sum of infeasibility.
 * `sumscaledinf`: The sum of scaled \(relative\) infeasibility.
 * `objval`: The net objective.


#### nml_addnames

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. Use the `_nml_addnames`to add names to a name list, or modify existing names on a namelist.

_**Synopsis:**_

   `
nml_addnames(nml, names, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`nml` | The name list to which you want to add names. 
`names` | Character buffer containing the null-terminated string names. 
`first` | The index of the first name to add/replace. 
`last` | The index of the last name to add/replace. 

_**Return value:**_
The input argument `nml`.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_copynames

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. `_nml_copynames`allows you to copy all the names from one name list to another. As name lists representing row/column names cannot be modified, `_nml_copynames`will be most often used to copy such names to a namelist where they can be modified, for some later use.

_**Synopsis:**_

   `
nml_copynames(dest, src)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`dest` | The namelist object to copy names to. 
`src` | The namelist object from which all the names should be copied. 

_**Return value:**_
The input argument `dest`.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_create

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. `_nml_create`will create a new namelist to which the user can add, remove and otherwise modify names.

_**Synopsis:**_

   `
nml_create()` 


_**Return value:**_
The new namelist.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_destroy

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

Destroys a namelist and frees any memory associated with it. Note you need only destroy namelists created by `_nml_destroy`- those returned by getnamelistobject are automatically destroyed when you destroy the problem object.

_**Synopsis:**_

   `
nml_destroy(nml)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`nml` | The namelist to be destroyed. 

_**Return value:**_
The input argument `nml`.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_findname

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. `_nml_findname`returns the index of the given name in the given name list.

_**Synopsis:**_

   `
nml_findname(nml, name)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`nml` | The namelist in which to look for the name. 
`name` | Null-terminated string containing the name for which to search. 

_**Return value:**_
The index of the name is returned, or in which -1 if the name is not found in the namelist.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_getlasterror

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

Returns the last error encountered during a call to a namelist object.

_**Synopsis:**_

   `
nml_getlasterror(nml)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`nml` | The namelist object. 

_**Return value:**_
A list with the following elements:
 * `msgcode`: The error code.
 * `msg`: The last error message relating to this namelist.


_**Further information:**_
Please refer to the C documentation for more details.

#### nml_getmaxnamelen

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. `_nml_getmaxnamelen`returns the length of the longest name in the namelist.

_**Synopsis:**_

   `
nml_getmaxnamelen(nml)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`nml` | The namelist object. 

_**Return value:**_
The length of the longest name.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_getnamecount

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. `_nlm_getnamecount`returns the number of names in the namelist.

_**Synopsis:**_

   `
nml_getnamecount(nml)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`nml` | The namelist object. 

_**Return value:**_
The number of names.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_getnames

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. The `_nml_getnames`function returns some of the names held in the name list. The names shall be returned in a character buffer, and with each name being separated by a `NULL`character.

_**Synopsis:**_

   `
nml_getnames(nml, first, last, pad = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`nml` | The namelist object. 
`first` | The index of the first name in the namelist to return. 
`last` | The index of the last name in the namelist to return. 
`pad` | The minimum length of each name. 

_**Return value:**_
The names.

_**Further information:**_
Please refer to the C documentation for more details.

#### nml_removenames

_**Purpose:**_

   \*\*Deprecated\*\* The names list API is scheduled for removal.

The `_nml_*`functions provide a simple, generic interface to lists of names, which may be names of rows/columns on a problem or may be a list of arbitrary names provided by the user. `_nml_removenames`will remove the specified names from the name list. Any subsequent names will be moved down to replace the removed names.

_**Synopsis:**_

   `
nml_removenames(nml, first, last)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`nml` | The name list from which you want to remove names. 
`first` | The index of the first name to remove. 
`last` | The index of the last name to remove. 

_**Return value:**_
The input argument `nml`.

_**Further information:**_
Please refer to the C documentation for more details.

#### objsa

_**Purpose:**_

   Returns upper and lower sensitivity ranges for specified objective function coefficients.

If the objective coefficients are varied within these ranges the current basis remains optimal and the reduced costs remain valid.

_**Synopsis:**_

   `
objsa(prob, colind, ncols = x_max_vec_length(colind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of length `ncols` containing the indices of the columns whose objective function coefficients sensitivity ranges are required. 
`ncols` | Number of objective function coefficients whose sensitivity is sought. 

_**Return value:**_
A list with the following elements:
 * `lower`: Double array of length `ncols` containing the objective function lower range values.
 * `upper`: Double array of length `ncols` containing the objective function upper range values.


_**Further information:**_
Please refer to the C documentation for more details.

#### optimize

_**Purpose:**_

   This function begins a search for the optimal solution of the problem.

The direction of optimization is given by OBJSENSE.

_**Synopsis:**_

   `
optimize(prob, flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`flags` | Flags to pass to `optimize` \( `OPTIMIZE`\). The default is `""` or `NULL`. If the argument includes:
 * `s`: solve the problem to local optimality;
 * `x`: solve the problem to global optimality;
 * `l`: \(deprecated\) if a branch and bound search is necessary to solve the problem, stop after solving the root node. This flag is deprecated, use the MIPSTOPSTAGE control instead.
 

_**Return value:**_
A list with the following elements:
 * `solvestatus`: The solve status after termination.
 * `solstatus`: The solution status after termination.


_**Further information:**_
Please refer to the C documentation for more details.

#### pivot

_**Purpose:**_

   Performs a simplex pivot by bringing variable `enter`into the basis and removing `leave`.

_**Synopsis:**_

   `
pivot(prob, enter, leave)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`enter` | Index of row or column to enter basis. 
`leave` | Index of row or column to leave basis. 

_**Return value:**_
The input argument `prob`.

#### postsolve

_**Purpose:**_

   Postsolve the current matrix when it is in a presolved state.

_**Synopsis:**_

   `
postsolve(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The input argument `prob`.

#### postsolvesol

_**Purpose:**_

   Postsolves a primal solution formulated in the presolved space into the corresponding solution formulated in the input space.

The problem itself is unchanged.

_**Synopsis:**_

   `
postsolvesol(prob, prex)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`prex` | Double array of length COLS with the values of the primal variables in the presolved space. 

_**Return value:**_
Double array of length INPUTCOLS containing the values of the primal variables.

_**Further information:**_
Please refer to the C documentation for more details.

#### presolverow

_**Purpose:**_

   Presolves a row formulated in terms of the original variables such that it can be added to a presolved matrix.

_**Synopsis:**_

   `
presolverow(


  prob,


  rowtype,


  origcolind,


  origrowcoef,


  origrhs,


  norigcoefs = x_max_vec_length(origcolind, origrowcoef)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowtype` | The type of the row:
 * `L`: indicates a `<=` row;
 * `G`: indicates a `>=` row.
 * `E`: indicates a `>=` row.
 
`origcolind` | Integer array of length `norigcoefs` containing the column indices of the row to presolve. 
`origrowcoef` | Double array of length `norigcoefs` containing the non-zero coefficients of the row to presolve. 
`origrhs` | The right-hand side constant of the row to presolve. 
`norigcoefs` | Number of elements in the `origcolind` and `origrowcoef` arrays. 

_**Return value:**_
A list with the following elements:
 * `ncoefs`: The number of non-zero elements in the presolved row \(this may be bigger than `maxcoefs`\).
 * `colind`: Integer array of length `maxcoefs` containing the column indices of the presolved row.
 * `rowcoef`: Double array of length `maxcoefs` containing the coefficients of the presolved row.
 * `rhs`: The presolved right-hand side.
 * `status`: Status of the presolved row:
     * `-5`: Failed to presolve the row due to presolve operations making the row nonlinear;
     * `-4`: Failed to presolve the equality row due to presolve operations requiring relaxation of the row;
     * `-3`: Failed to presolve the row due to presolve dual reductions;
     * `-2`: Failed to presolve the row due to presolve duplicate column reductions;
     * `-1`: Failed to presolve the row due to an error. Check the Optimizer error code for the cause;
     * `0`: The row was successfully presolved;
     * `1`: The row was presolved, but may be relaxed.



#### presolvesol

_**Purpose:**_

   Presolves a primal solution formulated in the input space into the corresponding solution formulated in the presolved space.

The problem itself is unchanged.

_**Synopsis:**_

   `
presolvesol(prob, origx)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`origx` | Double array of length INPUTCOLS with the values of the primal variables in the input space. 

_**Return value:**_
Double array of length COLS containing the values of the primal variables.

_**Further information:**_
Please refer to the C documentation for more details.

#### print.XPRSboundsRef

_**Purpose:**_

   Print an XPRESS bound reference.

_**Synopsis:**_

   `
print.XPRSboundsRef(bnd, ...)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`bnd` | The bound reference to print. 

#### print.XPRSbranchobject

_**Purpose:**_

   Print an XPRESS branching object.

_**Synopsis:**_

   `
print.XPRSbranchobject(obj, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`obj` | The branching object to be printed. 
`...` | Further arguments passed from other methods, ignored 

#### print.XPRScut

_**Purpose:**_

   Print an XPRESS cut.

_**Synopsis:**_

   `
print.XPRScut(cut, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`cut` | The cut to print. 
`...` | Further arguments passed from other methods, ignored 

#### print.XPRSnamelist

_**Purpose:**_

   Print an XPRESS name list.

_**Synopsis:**_

   `
print.XPRSnamelist(namelist, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`namelist` | The name list to print. 
`...` | Further arguments passed from other methods, ignored 

#### print.XPRSprob

_**Purpose:**_

   Print an XPRESS problem.

_**Synopsis:**_

   `
print.XPRSprob(prob, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to be printed 
`...` | Further arguments passed from other methods, ignored 

#### print.XPRSvoid

_**Purpose:**_

   Print an external generic pointer.

_**Synopsis:**_

   `
print.XPRSvoid(ptr, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`ptr` | The pointer to print 
`...` | Further arguments passed from other methods, ignored 

#### problemdata_validation_list

_**Purpose:**_

   List of input names allowed for problemdata.

We allow either Matrix Style or C API Style for the inputs.

_**Synopsis:**_

   `
problemdata_validation_list` 


_**Further information:**_
This is a list of lists, which splits all acceptable arguments into C-Style Xpress and Matrix-style The validation code checks that only names from this list appear, and that the mutually exclusive alternatives are not mixed

#### readbasis

_**Purpose:**_

   Instructs the Optimizer to read in a previously saved basis from a file.

_**Synopsis:**_

   `
readbasis(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name from which the basis is to be read. 
`flags` | Flags to pass to `readbasis` \( `READBASIS`\): CPLEX compatibility; \(no effect, kept for compatibility\);
 * `n`: input basis file containing basic solution values;
 * `t`: input a compact advanced form of the basis;
 * `v`: use the provided filename verbatim, without appending the `.bss` extension;
 * `z`: read a compressed input file.
 

_**Return value:**_
The input argument `prob`.

#### readbinsol

_**Purpose:**_

   Reads a solution from a binary solution file.

_**Synopsis:**_

   `
readbinsol(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name from which the solution is to be read. 
`flags` | Flags to pass to `readbinsol` \( `READBINSOL`\):
 * `m`: load the solution as a solution for the MIP;
 * `x`: load the solution as a solution for the LP;
 * `v`: use the provided filename verbatim, without appending the `.sol` extension;
 * `z`: read a compressed input file.
 

_**Return value:**_
The input argument `prob`.

#### readdirs

_**Purpose:**_

   Reads a directives file to help direct the tree search.

_**Synopsis:**_

   `
readdirs(prob, filename = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name from which the directives are to be read. 

_**Return value:**_
The input argument `prob`.

#### readprob

_**Purpose:**_

   Reads an \(X\)MPS or LP format matrix from file.

_**Synopsis:**_

   `
readprob(prob, filename, flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | The path and file name from which the problem is to be read. 
`flags` | Flags to be passed:
 * `l`: only `filename.lp` is searched for;
 * `v`: use the provided filename verbatim, without appending the `.mps`, `.mat` or `.lp` extension;
 * `z`: read a compressed input file.
 

_**Return value:**_
The input argument `prob`.

#### readslxsol

_**Purpose:**_

   Reads an ASCII solution file `.slx`created by the writeslxsol function.

_**Synopsis:**_

   `
readslxsol(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which the solution is to be read. 
`flags` | Flags to pass to `readslxsol` \( `READSLXSOL`\): non-breaking-whitespace conversion;
 * `l`: read the solution as an LP solution in case of a MIP problem;
 * `m`: read the solution as a solution for the MIP problem;
 * `a`: read multiple MIP solutions from the `.slx` file and add them to the MIP problem;
 * `v`: use the provided filename verbatim, without appending the `.slx` extension;
 * `z`: read a compressed input file.
 

_**Return value:**_
The input argument `prob`.

#### removecbafterobjective

_**Purpose:**_

   Remove all `afterobjective`callbacks.

Removes any callback function registered for `afterobjective`events from `prob`.

_**Synopsis:**_

   `
removecbafterobjective(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbbariteration

_**Purpose:**_

   Remove all `bariteration`callbacks.

Removes any callback function registered for `bariteration`events from `prob`.

_**Synopsis:**_

   `
removecbbariteration(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbbarlog

_**Purpose:**_

   Remove all `barlog`callbacks.

Removes any callback function registered for `barlog`events from `prob`.

_**Synopsis:**_

   `
removecbbarlog(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbbeforeobjective

_**Purpose:**_

   Remove all `beforeobjective`callbacks.

Removes any callback function registered for `beforeobjective`events from `prob`.

_**Synopsis:**_

   `
removecbbeforeobjective(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbchecktime

_**Purpose:**_

   Remove all `checktime`callbacks.

Removes any callback function registered for `checktime`events from `prob`.

_**Synopsis:**_

   `
removecbchecktime(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbchgbranchobject

_**Purpose:**_

   Remove all `chgbranchobject`callbacks.

Removes any callback function registered for `chgbranchobject`events from `prob`.

_**Synopsis:**_

   `
removecbchgbranchobject(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbcomputerestart

_**Purpose:**_

   Remove all `computerestart`callbacks.

Removes any callback function registered for `computerestart`events from `prob`.

_**Synopsis:**_

   `
removecbcomputerestart(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbcutlog

_**Purpose:**_

   Remove all `cutlog`callbacks.

Removes any callback function registered for `cutlog`events from `prob`.

_**Synopsis:**_

   `
removecbcutlog(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbcutround

_**Purpose:**_

   Remove all `cutround`callbacks.

Removes any callback function registered for `cutround`events from `prob`.

_**Synopsis:**_

   `
removecbcutround(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbdestroymt

_**Purpose:**_

   Remove all `destroymt`callbacks.

Removes any callback function registered for `destroymt`events from `prob`.

_**Synopsis:**_

   `
removecbdestroymt(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbgapnotify

_**Purpose:**_

   Remove all `gapnotify`callbacks.

Removes any callback function registered for `gapnotify`events from `prob`.

_**Synopsis:**_

   `
removecbgapnotify(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbgloballog

_**Purpose:**_

   Remove all `miplog`callbacks.

_**Synopsis:**_

   `
removecbgloballog(prob)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``removecbmiplog``

#### removecbinfnode

_**Purpose:**_

   Remove all `infnode`callbacks.

Removes any callback function registered for `infnode`events from `prob`.

_**Synopsis:**_

   `
removecbinfnode(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbintsol

_**Purpose:**_

   Remove all `intsol`callbacks.

Removes any callback function registered for `intsol`events from `prob`.

_**Synopsis:**_

   `
removecbintsol(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecblplog

_**Purpose:**_

   Remove all `lplog`callbacks.

Removes any callback function registered for `lplog`events from `prob`.

_**Synopsis:**_

   `
removecblplog(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbmessage

_**Purpose:**_

   Remove all `message`callbacks.

Removes any callback function registered for `message`events from `prob`.

_**Synopsis:**_

   `
removecbmessage(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbmiplog

_**Purpose:**_

   Remove all `miplog`callbacks.

Removes any callback function registered for `miplog`events from `prob`.

_**Synopsis:**_

   `
removecbmiplog(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbmipthread

_**Purpose:**_

   Remove all `mipthread`callbacks.

Removes any callback function registered for `mipthread`events from `prob`.

_**Synopsis:**_

   `
removecbmipthread(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbnewnode

_**Purpose:**_

   Remove all `newnode`callbacks.

Removes any callback function registered for `newnode`events from `prob`.

_**Synopsis:**_

   `
removecbnewnode(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbnlpcoefevalerror

_**Purpose:**_

   Remove all `nlpcoefevalerror`callbacks.

Removes any callback function registered for `nlpcoefevalerror`events from `prob`.

_**Synopsis:**_

   `
removecbnlpcoefevalerror(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbnodecutoff

_**Purpose:**_

   Remove all `nodecutoff`callbacks.

Removes any callback function registered for `nodecutoff`events from `prob`.

_**Synopsis:**_

   `
removecbnodecutoff(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbnodelpsolved

_**Purpose:**_

   Remove all `nodelpsolved`callbacks.

Removes any callback function registered for `nodelpsolved`events from `prob`.

_**Synopsis:**_

   `
removecbnodelpsolved(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecboptnode

_**Purpose:**_

   Remove all `optnode`callbacks.

Removes any callback function registered for `optnode`events from `prob`.

_**Synopsis:**_

   `
removecboptnode(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbpreintsol

_**Purpose:**_

   Remove all `preintsol`callbacks.

Removes any callback function registered for `preintsol`events from `prob`.

_**Synopsis:**_

   `
removecbpreintsol(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbprenode

_**Purpose:**_

   Remove all `prenode`callbacks.

Removes any callback function registered for `prenode`events from `prob`.

_**Synopsis:**_

   `
removecbprenode(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbpresolve

_**Purpose:**_

   Remove all `presolve`callbacks.

Removes any callback function registered for `presolve`events from `prob`.

_**Synopsis:**_

   `
removecbpresolve(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### removecbusersolnotify

_**Purpose:**_

   Remove all `usersolnotify`callbacks.

Removes any callback function registered for `usersolnotify`events from `prob`.

_**Synopsis:**_

   `
removecbusersolnotify(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer from which callbacks are removed. 

_**Return value:**_
Always returns 0 \(zero\).

#### repairinfeas

_**Purpose:**_

   Provides a simplified interface for repairweightedinfeas.

_**Synopsis:**_

   `
repairinfeas(


  prob,


  penalty,


  phase2,


  flags,


  lepref,


  gepref,


  lbpref,


  ubpref,


  delta


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`penalty` | The type of penalties created from the preferences:
 * `c`: each penalty is the reciprocal of the preference \(default\);
 * `s`: the penalties are placed in the scaled problem.
 
`phase2` | Controls the second phase of optimization:
 * `o`: use the objective sense of the original problem \(default\);
 * `x`: maximize the relaxed problem using the original objective;
 * `f`: skip optimization regarding the original objective;
 * `n`: minimize the relaxed problem using the original objective;
 * `i`: if the relaxation is infeasible, generate an irreducible infeasible subset for the analysis of the problem;
 * `a`: if the relaxation is infeasible, generate all irreducible infeasible subsets for the analysis of the problem.
 
`flags` | Specifies flags to be passed to optimize. 
`lepref` | Preference for relaxing the less or equal side of row. 
`gepref` | Preference for relaxing the greater or equal side of a row. 
`lbpref` | Preferences for relaxing lower bounds. 
`ubpref` | Preferences for relaxing upper bounds. 
`delta` | The relaxation multiplier in the second phase -1. 

_**Return value:**_
The status after the relaxation:
 * `0`: relaxed optimum found;
 * `1`: relaxed problem is infeasible;
 * `2`: relaxed problem is unbounded;
 * `3`: solution of the relaxed problem regarding the original objective is nonoptimal;
 * `4`: error \(when return code is nonzero\);
 * `5`: numerical instability;
 * `6`: analysis of an infeasible relaxation was performed, but the relaxation is feasible.


#### repairweightedinfeas

_**Purpose:**_

   By relaxing a set of selected constraints and bounds of an infeasible problem, it attempts to identify a 'solution' that violates the selected set of constraints and bounds minimally, while satisfying all other constraints and bounds.

Among such solution candidates, it selects one that is optimal regarding the original objective function.

_**Synopsis:**_

   `
repairweightedinfeas(


  prob,


  lepref,


  gepref,


  lbpref,


  ubpref,


  phase2,


  delta,


  flags


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`lepref` | Array of size `ROWS` containing the preferences for relaxing the less or equal side of row. 
`gepref` | Array of size `ROWS` containing the preferences for relaxing the greater or equal side of a row. 
`lbpref` | Array of size `COLS` containing the preferences for relaxing lower bounds. 
`ubpref` | Array of size `COLS` containing preferences for relaxing upper bounds. 
`phase2` | Controls the second phase of optimization:
 * `o`: use the objective sense of the original problem \(default\);
 * `x`: maximize the relaxed problem using the original objective;
 * `f`: skip optimization regarding the original objective;
 * `n`: minimize the relaxed problem using the original objective;
 * `i`: if the relaxation is infeasible, generate an irreducible infeasible subset for the analysis of the problem;
 * `a`: if the relaxation is infeasible, generate all irreducible infeasible subsets for the analysis of the problem.
 
`delta` | The relaxation multiplier in the second phase -1. 
`flags` | Specifies flags to be passed to optimize. 

_**Return value:**_
The status after the relaxation:
 * `0`: relaxed optimum found;
 * `1`: relaxed problem is infeasible;
 * `2`: relaxed problem is unbounded;
 * `3`: solution of the relaxed problem regarding the original objective is nonoptimal;
 * `4`: error \(when return code is nonzero\);
 * `5`: numerical instability;
 * `6`: analysis of an infeasible relaxation was performed, but the relaxation is feasible.


_**Further information:**_
Please refer to the C documentation for more details.

#### repairweightedinfeasbounds

_**Purpose:**_

   An extended version of repairweightedinfeas that allows for bounding the level of relaxation allowed.

_**Synopsis:**_

   `
repairweightedinfeasbounds(


  prob,


  lepref,


  gepref,


  lbpref,


  ubpref,


  lerelax,


  gerelax,


  lbrelax,


  ubrelax,


  phase2,


  delta,


  flags


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`lepref` | Array of size `ROWS` containing the preferences for relaxing the less or equal side of row. 
`gepref` | Array of size `ROWS` containing the preferences for relaxing the greater or equal side of a row. 
`lbpref` | Array of size `COLS` containing the preferences for relaxing lower bounds. 
`ubpref` | Array of size `COLS` containing preferences for relaxing upper bounds. 
`lerelax` | Array of size `ROWS` containing the upper bounds on the amount the less or equal side of a row can be relaxed. 
`gerelax` | Array of size `ROWS` containing the upper bounds on the amount the greater or equal side of a row can be relaxed. 
`lbrelax` | Array of size `COLS` containing the upper bounds on the amount the lower bounds can be relaxed. 
`ubrelax` | Array of size `COLS` containing the upper bounds on the amount the upper bounds can be relaxed. 
`phase2` | Controls the second phase of optimization:
 * `o`: use the objective sense of the original problem \(default\);
 * `x`: maximize the relaxed problem using the original objective;
 * `f`: skip optimization regarding the original objective;
 * `n`: minimize the relaxed problem using the original objective;
 * `i`: if the relaxation is infeasible, generate an irreducible infeasible subset for the analysis of the problem;
 * `a`: if the relaxation is infeasible, generate all irreducible infeasible subsets for the analysis of the problem.
 
`delta` | The relaxation multiplier in the second phase -1. 
`flags` | Specifies flags to be passed to optimize. 

_**Return value:**_
The status after the relaxation:
 * `0`: relaxed optimum found;
 * `1`: relaxed problem is infeasible;
 * `2`: relaxed problem is unbounded;
 * `3`: solution of the relaxed problem regarding the original objective is nonoptimal;
 * `4`: error \(when return code is nonzero\);
 * `5`: numerical instability;
 * `6`: analysis of an infeasible relaxation was performed, but the relaxation is feasible.


#### restore

_**Purpose:**_

   Restores the Optimizer's data structures from a file created by saveas \(SAVE\).

Optimization may then recommence from the point at which the file was created.

_**Synopsis:**_

   `
restore(prob, probname = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing the problem name. 
`flags` | Additional flags force \(no effect, kept for compatibility\);
 * `h`: Do not restore hardware information from the file;
 * `v`: use the provided filename verbatim, without appending the `.svf` extension.
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### rhssa

_**Purpose:**_

   Returns upper and lower sensitivity ranges for specified right hand side \(RHS\) function coefficients.

If the RHS coefficients are varied within these ranges the current basis remains optimal and the reduced costs remain valid.

_**Synopsis:**_

   `
rhssa(prob, rowind, nrows = x_max_vec_length(rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `nrows` containing the indices of the rows whose RHS coefficients sensitivity ranges are required. 
`nrows` | The number of RHS coefficients for which sensitivity ranges are required. 

_**Return value:**_
A list with the following elements:
 * `lower`: Double array of length `nrows` containing the RHS lower range values.
 * `upper`: Double array of length `nrows` containing the RHS upper range values.


_**Further information:**_
Please refer to the C documentation for more details.

#### save

_**Purpose:**_

   Saves the current data structures, i.e. matrices, control settings and problem attribute settings to file and terminates the run so that optimization can be resumed later.

_**Synopsis:**_

   `
save(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The input argument `prob`.

#### saveas

_**Purpose:**_

   Saves the current data structures, i.e. matrices, control settings and problem attribute settings to file and terminates the run so that optimization can be resumed later.

_**Synopsis:**_

   `
saveas(prob, filename = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | The name of the file \(without .svf\) to save to. 

_**Return value:**_
The input argument `prob`.

#### scale

_**Purpose:**_

   Re-scales the current matrix.

_**Synopsis:**_

   `
scale(prob, rowscale, colscale)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowscale` | Integer array of size ROWS containing the powers of `2` with which to scale the rows, or `NULL` if not required. 
`colscale` | Integer array of size COLS containing the powers of `2` with which to scale the columns, or `NULL` if not required. 

_**Return value:**_
The input argument `prob`.

#### setcheckedmode

_**Purpose:**_

   You can use this function to disable some of the checking and validation of function calls and function call parameters for calls to the Xpress Optimizer API.

This checking is relatively lightweight but disabling it can improve performance in cases where non-intensive Xpress Optimizer functions are called repeatedly in a short space of time. Please note: after disabling function call checking and validation, invalid usage of Xpress Optimizer functions may not be detected and may cause the Xpress Optimizer process to behave unexpectedly or crash. It is not recommended that you disable function call checking and validation during application development.

_**Synopsis:**_

   `
setcheckedmode(checkedmode)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`checkedmode` | Pass as 0 to disable much of the validation for all Xpress function calls from the current process. 

_**Return value:**_
Always returns 0 \(zero\).

_**Further information:**_
Please refer to the C documentation for more details.

#### setdblcontrol

_**Purpose:**_

   Sets the value of a given double control parameter.

_**Synopsis:**_

   `
setdblcontrol(prob, control, value)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Control parameter whose value is to be set. 
`value` | Value to which the control parameter is to be set. 

_**Return value:**_
The input argument `prob`.

#### setdefaultcontrol

_**Purpose:**_

   Sets a single control to its default value.

_**Synopsis:**_

   `
setdefaultcontrol(prob, control)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Integer, double or string control parameter whose default value is to be set. 

_**Return value:**_
The input argument `prob`.

#### setdefaults

_**Purpose:**_

   Sets all controls to their default values.

_**Synopsis:**_

   `
setdefaults(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The input argument `prob`.

#### setindicators

_**Purpose:**_

   Specifies that a set of rows in the matrix will be treated as indicator constraints during a tree search.

An indicator constraint is made of a `condition`and a `constraint`. The `condition`is of the type "bin = value", where `bin`is a binary variable and `value`is either 0 or 1. The `constraint`is any matrix row \(may be linear, quadratic or general nonlinear\). During tree search, a row configured as an indicator constraint is enforced only when condition holds, that is only if the indicator variable `bin`has the specified value. Note that every row may only get assigned a single indicator variable and term. If a row needs to be activated by multiple different terms, the row needs to be duplicated so that each term can be assigned to a distinct row. If the indicator variable should be changed, the old term needs to be deleted first \(by calling delindicators or by calling this function with a comps argument of 0\) before assigning a new one.

_**Synopsis:**_

   `
setindicators(


  prob,


  rowind,


  colind,


  complement,


  nrows = x_max_vec_length(rowind, colind, complement)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`rowind` | Integer array of length `nrows` containing the indices of the rows that define the constraint part for the indicator constraints. 
`colind` | Integer array of length `nrows` containing the column indices of the indicator variables. 
`complement` | Integer array of length `nrows` with the complement flags:
 * `0`: not an indicator constraint \(in this case the corresponding entry in the `colind` array is ignored\);
 * `1`: for indicator constraints with condition " `bin = 1` ";
 * `-1`: for indicator constraints with condition " `bin = 0` ".
 
`nrows` | The number of indicator constraints. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### setintcontrol

_**Purpose:**_

   Sets the value of a given integer control parameter.

_**Synopsis:**_

   `
setintcontrol(prob, control, value)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Control parameter whose value is to be set. 
`value` | Value to which the control parameter is to be set. 

_**Return value:**_
The input argument `prob`.

#### setlogfile

_**Purpose:**_

   This directs all Optimizer output to a log file.

_**Synopsis:**_

   `
setlogfile(prob, filename)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which all logging output should be written. 

_**Return value:**_
The input argument `prob`.

#### setmessage

_**Purpose:**_

   Set message verbosity for optimizer.

The function registers a `message`callback with `prob`. All enabled messages are printed using the `cat`function.

_**Synopsis:**_

   `
setmessage(prob, info, warn = TRUE, err = TRUE)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem object for which messages should be enabled. 
`info` | `TRUE` to enable info messages, `FALSE` to disable them. 
`warn` | `TRUE` to enable warning messages, `FALSE` to disable them. 
`err` | `TRUE` to enable error messages, `FALSE` to disable them. 

_**Return value:**_
Always returns `prob`.

#### setmessagestatus

_**Purpose:**_

   Manages suppression of messages.

_**Synopsis:**_

   `
setmessagestatus(prob, msgcode, status)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem for which message `msgcode` is to have its suppression status changed; pass `NULL` if the message should have the status apply globally to all problems. 
`msgcode` | The id number of the message. 
`status` | Non-zero if the message is not suppressed; `0` otherwise. 

_**Return value:**_
The input argument `prob`.

#### setobjdblcontrol

_**Purpose:**_

   Sets the value of an double control parameter associated with an objective.

These control values will only be applied when solving the given objective during multi-objective optimization.

_**Synopsis:**_

   `
setobjdblcontrol(prob, objidx, control, value)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective to modify. 
`control` | Control parameter whose value is to be modified. Can be any solver control, or one of:
 * `_OBJECTIVE_WEIGHT`: set the weight of the given objective;
 * `_OBJECTIVE_ABSTOL`: set the absolute tolerance of the given objective;
 * `_OBJECTIVE_RELTOL`: set the relative tolerance of the given objective;
 * `_OBJECTIVE_RHS`: set the constant term of the given objective.
 
`value` | Value to which the control parameter is to be set. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### setobjintcontrol

_**Purpose:**_

   Sets the value of an integer control parameter associated with an objective.

These control values will only be applied when solving the given objective during multi-objective optimization.

_**Synopsis:**_

   `
setobjintcontrol(prob, objidx, control, value)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`objidx` | Index of the objective to modify. 
`control` | Control parameter whose value is to be modified. Can be any solver control, or one of:
 * `_OBJECTIVE_PRIORITY`: set the priority of the given objective.
 
`value` | Value to which the control parameter is to be set. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### setoutput

_**Purpose:**_

   Convenience function to redirect optimizer messages.

The function can be used to redirect optimizer messages to `stdin`or `stderr`. The values for `info`, `warn`, `err`can be 0 \(zero\) to suppress the respective messages, 1 \(one\) to redirect the respective messages to `stdout`, 2 to redirect them to `stderr`and 3 to redirect them to both. Any previous redirection set with this function is removed.

_**Synopsis:**_

   `
setoutput(prob, info = 1L, warn = 2L, err = 2L)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem pointer for which messages should be redirected. 
`info` | Specifies redirection of info messages. 
`warn` | Specifies redirection of warning messages. 
`err` | Specifies redurection of error messages. 

_**Return value:**_
Always returns `prob`.

#### setprobname

_**Purpose:**_

   Sets the current problem name.

_**Synopsis:**_

   `
setprobname(prob, probname)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`probname` | A string of up to MAXPROBNAMELENGTH characters containing the problem name. 

_**Return value:**_
The input argument `prob`.

#### setstrcontrol

_**Purpose:**_

   Used to set the value of a given string control parameter.

_**Synopsis:**_

   `
setstrcontrol(prob, control, value)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`control` | Control parameter whose value is to be set. 
`value` | A string containing the value to which the control is to be set. 

_**Return value:**_
The input argument `prob`.

#### slpcascade

_**Purpose:**_

   Re-calculate consistent values for SLP variables based on the current values of the remaining variables.

_**Synopsis:**_

   `
slpcascade(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### slpcascadeorder

_**Purpose:**_

   Establish a re-calculation sequence for SLP variables with determining rows.

_**Synopsis:**_

   `
slpcascadeorder(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### slpchgcascadenlimit

_**Purpose:**_

   Set a variable specific cascade iteration limit

_**Synopsis:**_

   `
slpchgcascadenlimit(prob, col, limit)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`col` | The index of the column corresponding to the SLP variable for which the cascading limit is to be imposed. 
`limit` | The new cascading iteration limit. 

_**Return value:**_
The input argument `prob`.

#### slpchgdeltatype

_**Purpose:**_

   Changes the type of the delta assigned to a nonlinear variable

_**Synopsis:**_

   `
slpchgdeltatype(


  prob,


  varind,


  deltatypes,


  values,


  nvars = x_max_vec_length(varind, deltatypes, values)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`varind` | Indices of the variables to change the deltas for. 
`deltatypes` | Type of the delta variable:
 * `0 (XSLP_DELTA_CONT)`: Differentiable variable, default.
 * `1 (XSLP_DELTA_SEMICONT)`: Variable where a minimum perturbation size given in `values` may be required before a significant change in the problem is achieved.
 * `2 (XSLP_DELTA_INTEGER)`: Variable defined over the grid size given in `values`.
 * `3 (XSLP_DELTA_EXPLORE)`: Variable where a meaningful step size should automatically be detected, with an upper limit given in `values`.
 
`values` | Grid or minimum step sizes for the variables. 
`nvars` | The number of SLP variables to change the delta type for. 

_**Return value:**_
The input argument `prob`.

#### slpchgrowstatus

_**Purpose:**_

   Change the status setting of a constraint

_**Synopsis:**_

   `
slpchgrowstatus(prob, row, status)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row to be changed. 
`status` | Address of an integer holding a bitmap with the new status settings. If the status is to be changed, always get the current status first \(use XSLPgetrowstatus\) and then change settings as required. The only settings likely to be changed are:
 * `Bit 11`: Set if row must not have a penalty error vector. This is the equivalent of an enforced constraint \(SLPDATA type EC\).
 

_**Return value:**_
The input argument `prob`.

#### slpchgrowwt

_**Purpose:**_

   Set or change the initial penalty error weight for a row

_**Synopsis:**_

   `
slpchgrowwt(prob, row, weight)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the row whose weight is to be set or changed. 
`weight` | Address of a double precision variable holding the new value of the weight. 

_**Return value:**_
The input argument `prob`.

#### slpconstruct

_**Purpose:**_

   Create the full augmented SLP matrix and data structures, ready for optimization

_**Synopsis:**_

   `
slpconstruct(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### slpfixpenalties

_**Purpose:**_

   Fixe the values of the error vectors

_**Synopsis:**_

   `
slpfixpenalties(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
Return status after fixing the penalty variables: 0 is successful, nonzero otherwise.

#### slpgetrowstatus

_**Purpose:**_

   Retrieve the status setting of a constraint

_**Synopsis:**_

   `
slpgetrowstatus(prob, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the matrix row whose data is to be obtained. 

_**Return value:**_
The status settings.

#### slpgetrowwt

_**Purpose:**_

   Get the initial penalty error weight for a row

_**Synopsis:**_

   `
slpgetrowwt(prob, row)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`row` | The index of the row whose weight is to be retrieved. 

_**Return value:**_
The value of the weight.

#### slpreinitialize

_**Purpose:**_

   Reset the SLP problem to match a just augmented system

_**Synopsis:**_

   `
slpreinitialize(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### slpsetdetrow

_**Purpose:**_

   Set the determining row of a variable

_**Synopsis:**_

   `
slpsetdetrow(prob, colind, rowind, nvars = x_max_vec_length(colind, rowind))` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`colind` | Array of length `nvars` with the index of the column for which the determining row is set. 
`rowind` | Array of length `nvars` with the index of the determining row. 
`nvars` | The number of variables for which determining rows are set. 

_**Return value:**_
The input argument `prob`.

#### slpsetinitstepbounds

_**Purpose:**_

   Set the initial step bounds of columns

_**Synopsis:**_

   `
slpsetinitstepbounds(


  prob,


  colind,


  initial,


  ncols = x_max_vec_length(colind, initial)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 
`colind` | Array of length `ncols` with index of the column for which the initial step bound is provided. 
`initial` | Array of length `ncols` with the initial step bounds. 
`ncols` | Number of columns for which the initial step bound is to be set. 

_**Return value:**_
The input argument `prob`.

#### slpunconstruct

_**Purpose:**_

   Removes the augmentation and returns the problem to its pre-linearization state

_**Synopsis:**_

   `
slpunconstruct(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### slpupdatelinearization

_**Purpose:**_

   Updates the current linearization

_**Synopsis:**_

   `
slpupdatelinearization(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current SLP problem. 

_**Return value:**_
The input argument `prob`.

#### storecuts

_**Purpose:**_

   Stores cuts into the cut pool, but does not apply them to the current node.

These cuts must be explicitly loaded into the matrix using loadcuts before they become active.

_**Synopsis:**_

   `
storecuts(


  prob,


  nodups,


  cuttype,


  rowtype,


  rhs,


  start,


  colind,


  cutcoef,


  ncuts = x_max_vec_length(cuttype, rowtype, rhs)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`nodups` | 
 * `0`: do not exclude duplicates from the cut pool;
 * `1`: duplicates are to be excluded from the cut pool;
 * `2`: duplicates are to be excluded from the cut pool, ignoring cut type.
 
`cuttype` | Integer array of length `ncuts` containing the cut types. 
`rowtype` | Character array of length `ncuts` containing the row types:
 * `L`: indicates a `<=` row;
 * `E`: indicates an = row;
 * `G`: indicates a `>=` row.
 
`rhs` | Double array of length `ncuts` containing the right hand side elements for the cuts. 
`start` | Integer array containing offsets into the `colind` and `dmtval` arrays indicating the start of each cut. 
`colind` | Integer array of length `start[ncuts]` containing the column indices in the cuts. 
`cutcoef` | Double array of length `start[ncuts]` containing the matrix values for the cuts. 
`ncuts` | Number of cuts to add. 

_**Return value:**_
Array of length `ncuts`containing the cut objects.

_**Further information:**_
Please refer to the C documentation for more details.

#### strongbranch

_**Purpose:**_

   Performs strong branching iterations on all specified bound changes.

For each candidate bound change, `strongbranch`performs dual simplex iterations starting from the current optimal solution of the base LP, and returns both the status and objective value reached after these iterations.

_**Synopsis:**_

   `
strongbranch(


  prob,


  colind,


  bndtype,


  bndval,


  iterlim,


  nbounds = x_max_vec_length(colind, bndtype, bndval)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of size `nbounds` containing the indices of the columns on which the bounds will change. 
`bndtype` | Character array of length `nbounds` indicating the type of bound to change:
 * `U`: indicates change the upper bound;
 * `L`: indicates change the lower bound;
 * `B`: indicates change both bounds, i.e. fix the column.
 
`bndval` | Double array of length `nbounds` giving the new bound values. 
`iterlim` | Maximum number of LP iterations to perform for each bound change. 
`nbounds` | Number of bound changes to try. 

_**Return value:**_
A list with the following elements:
 * `objval`: Objective value of each LP after performing the strong branching iterations.
 * `status`: Status of each LP after performing the strong branching iterations, as detailed for the LPSTATUS attribute.


_**Further information:**_
Please refer to the C documentation for more details.

#### strongbranchcb

_**Purpose:**_

   Performs strong branching iterations on all specified bound changes.

For each candidate bound change, `strongbranchcb`performs dual simplex iterations starting from the current optimal solution of the base LP, and returns both the status and objective value reached after these iterations.

_**Synopsis:**_

   `
strongbranchcb(


  prob,


  colind,


  bndtype,


  bndval,


  iterlim,


  callback,


  nbounds = x_max_vec_length(colind, bndtype, bndval)


)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`colind` | Integer array of size `nbounds` containing the indices of the columns on which the bounds will change. 
`bndtype` | Character array of length `nbounds` indicating the type of bound to change:
 * `U`: indicates change the upper bound;
 * `L`: indicates change the lower bound;
 * `B`: indicates change both bounds, i.e. fix the column.
 
`bndval` | Double array of length `nbounds` giving the new bound values. 
`iterlim` | Maximum number of LP iterations to perform for each bound change. 
`callback` | Function to be called after each strong branch has been reoptimized. 
`nbounds` | Number of bound changes to try. 

_**Return value:**_
A list with the following elements:
 * `objval`: Array of objective values of each LP after performing the strong branching iterations.
 * `status`: Array of statuses of each LP after performing the strong branching iterations, as detailed for the LPSTATUS attribute.


_**Further information:**_
Please refer to the C documentation for more details.

#### summary.XPRSprob

_**Purpose:**_

   Print a summary for an XPRESS problem.

_**Synopsis:**_

   `
summary.XPRSprob(prob, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem for which the summary should be printed. 
`...` | Further arguments passed from other methods, ignored 

#### triggerrestart

_**Purpose:**_

   Triggers a restart of the MIP search process.

_**Synopsis:**_

   `
triggerrestart(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
Memory to return whether the restart request was accepted \(0\) or denied \(1\).

#### tune

_**Purpose:**_

   This function begins a tuner session for the current problem.

The tuner will solve the problem multiple times while evaluating a list of control settings and promising combinations of them. When finished, the tuner will select and set the best control setting on the problem. Note that the direction of optimization is given by OBJSENSE.

_**Synopsis:**_

   `
tune(prob, flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`flags` | Flags to pass to tune, which specify whether to tune the current problem as an LP or a MIP problem, and the algorithm for solving the LP problem or the initial LP relaxation of the MIP. The flags are optional. If the argument includes:
 * `l`: will tune the problem as an LP \(mutually exclusive with flag `g`\);
 * `g`: will tune the problem as a MIP \(mutually exclusive with flag `l`\);
 * `x`: will tune the problem as a Global Optimization problem with Xpress Global;
 * `d`: will use the dual simplex method;
 * `p`: will use the primal simplex method;
 * `b`: will use the barrier method;
 * `n`: will use the network simplex method.
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### tuneprobsetfile

_**Purpose:**_

   This function begins a tuner session for a set of problems.

The tuner will solve the problems multiple times while evaluating a list of control settings and promising combinations of them. When finished, the tuner will select and set the best control setting on the problems.

_**Synopsis:**_

   `
tuneprobsetfile(prob, setfile, ifmip = -1, sense = 0)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`setfile` | A plain text file which contains a list of problem filenames. 
`ifmip` | 
 * `-1`: to automatically determine whether to solve the problem set as LP or MIP;
 * `0`: to force the tuner to tune the problem set as LP;
 * `1`: to force the tuner to tune the problem set as MIP.
 
`sense` | 
 * `0`: to automatically determine the sense of each problem;
 * `1`: to force the tuner to minimize each problem;
 * `-1`: to force the tuner to maximize each problem.
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### tunerreadmethod

_**Purpose:**_

   This function loads a user defined tuner method from the given file.

_**Synopsis:**_

   `
tunerreadmethod(prob, methodfile)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`methodfile` | The method file name, from which the tuner can load a user-defined tuner method. 

_**Return value:**_
The input argument `prob`.

#### tunerwritemethod

_**Purpose:**_

   This function writes the current tuner method to a given file or prints it to the console.

_**Synopsis:**_

   `
tunerwritemethod(prob, methodfile)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`methodfile` | The method file name, to which the tuner will write the current tuner method. 

_**Return value:**_
The input argument `prob`.

#### unloadprob

_**Purpose:**_

   \*\*Deprecated\*\* Call loadlp with all `NULL`arguments to reset the problem to an empty problem.

Unloads and frees all memory associated with the current problem. It also invalidates the current problem \(as opposed to reading in an empty problem\).

_**Synopsis:**_

   `
unloadprob(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### writebasis

_**Purpose:**_

   Writes the current basis to a file for later input into the Optimizer.

_**Synopsis:**_

   `
writebasis(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name from which the basis is to be written. 
`flags` | Flags to pass to `writebasis` \( `WRITEBASIS`\): scrambled vector names; output values in hexadecimal; output in a format compatible with CPLEX;
 * `i`: output the internal presolved basis;
 * `t`: output a compact advanced form of the basis;
 * `n`: output basis file containing current solution values;
 * `h`: output values in single precision;
 * `p`: output values in full precision \(obsolete as this is now default behavior\);
 * `v`: use the provided filename verbatim, without appending the `.bss` extension;
 * `z`: compress the output file.
 

_**Return value:**_
The input argument `prob`.

#### writebinsol

_**Purpose:**_

   Writes the current MIP or LP solution to a binary solution file for later input into the Optimizer.

_**Synopsis:**_

   `
writebinsol(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which the solution is to be written. 
`flags` | Flags to pass to `writebinsol` \( `WRITEBINSOL`\):
 * `m`: output the MIP solution;
 * `x`: output the LP solution;
 * `v`: use the provided filename verbatim, without appending the `.sol` extension;
 * `z`: compress the output file.
 

_**Return value:**_
The input argument `prob`.

#### writedirs

_**Purpose:**_

   Writes the tree search directives from the current problem to a directives file.

_**Synopsis:**_

   `
writedirs(prob, filename = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which the directives should be written. 

_**Return value:**_
The input argument `prob`.

#### writeprob

_**Purpose:**_

   Writes the current problem to an MPS or LP file.

_**Synopsis:**_

   `
writeprob(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters to contain the file name to which the problem is to be written. 
`flags` | Flags, which can be one or more of the following: output in a format compatible with CPLEX;
 * `o`: one element per line;
 * `n`: output the scaled problem;
 * `s`: scrambled vector names;
 * `l`: output in LP format;
 * `p`: output values in full precision \(obsolete as this is now default behavior\);
 * `t`: omit the Xpress header in LP or MPS format;
 * `v`: use the provided filename verbatim, without appending the `.mps` or `.lp` extension;
 * `z`: compress the output file.
 

_**Return value:**_
The input argument `prob`.

#### writeprtsol

_**Purpose:**_

   Writes the current solution to a fixed format ASCII file, problem\_name `.prt`.

_**Synopsis:**_

   `
writeprtsol(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which the solution is to be written. 
`flags` | Flags for `writeprtsol` \( `WRITEPRTSOL`\) are: print the solution to the screen \(via the message callback\) instead of writing to a file;
 * `x`: write the LP solution instead of the current MIP solution;
 * `v`: use the provided filename verbatim, without appending the `.prt` extension;
 * `z`: write a compressed output file;
 * `s`: include classical sensitivity analysis.
 

_**Return value:**_
The input argument `prob`.

#### writeslxsol

_**Purpose:**_

   Creates an ASCII solution file \( `.slx`\) using a similar format to MPS files.

These files can be read back into the Optimizer using the readslxsol function.

_**Synopsis:**_

   `
writeslxsol(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which the solution is to be written. 
`flags` | Flags to pass to `writeslxsol` \( `WRITESLXSOL`\):
 * `l`: write the LP solution in case of a MIP problem;
 * `m`: write the MIP solution;
 * `p`: use full precision for numerical values \(obsolete as this is now default behavior\);
 * `s`: including slack variables;
 * `d`: LP solution only: including dual variables;
 * `r`: LP solution only: including reduced cost;
 * `v`: use the provided filename verbatim, without appending the `.slx` extension;
 * `z`: compress the output file.
 

_**Return value:**_
The input argument `prob`.

_**Further information:**_
Please refer to the C documentation for more details.

#### writesol

_**Purpose:**_

   Writes the current solution to a CSV format ASCII file, problem\_name `.asc`\(and `.hdr`\).

_**Synopsis:**_

   `
writesol(prob, filename = "", flags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The current problem. 
`filename` | A string of up to MAXPROBNAMELENGTH characters containing the file name to which the solution is to be written. 
`flags` | Flags to control which optional fields are output:
 * `s`: sequence number;
If no flags are specified, all fields are output.Additional flags: * `n`: name;
 * `t`: type;
 * `b`: basis status;
 * `a`: activity;
 * `c`: cost \(columns\), slack \(rows\);
 * `l`: lower bound;
 * `u`: upper bound;
 * `d`: dj \(column; reduced costs\), dual value \(rows; shadow prices\);
 * `r`: right hand side \(rows\).
 * `p`: outputs in full precision;
 * `q`: only outputs vectors with nonzero optimum value;
 * `x`: output the current LP solution instead of the MIP solution;
 * `z`: compress the output file.
 

_**Return value:**_
The input argument `prob`.

#### x_max_vec_length

_**Purpose:**_

   returns the maximum length of all input vectors

_**Synopsis:**_

   `
x_max_vec_length(...)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`...` | an arbitrary list of vectors, some of which may be NULL 

_**Return value:**_
maximum length of all input vectors. Note that NULL has a length of 0.

_**Example:**_

```


x_max_vec_length(1:3, 1:4)
# 4
x_max_vec_length(1:3, 1:4, 1:2)
4
x_max_vec_length(1:3, 1:4, NULL)
# 4

```
 
#### x_to_column_major_matrix

_**Purpose:**_

   Conversion to sparse matrix in column major form

convert an input matrix into a column major form with slots i, p, and x

_**Synopsis:**_

   `
x_to_column_major_matrix(mat)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`mat` | matrix object, either dense or sparse 

_**Return value:**_
converted mat in sparse column major form

#### x_to_sparse_triplet_matrix

_**Purpose:**_

   Conversion to sparse triplet matrix

convert an input matrix into a sparse triplet matrix with slots i, j, and x

_**Synopsis:**_

   `
x_to_sparse_triplet_matrix(mat)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`mat` | matrix object, either dense or sparse 

_**Return value:**_
converted mat in sparse triplet form

#### x_validate_length

_**Purpose:**_

   Validates that all non-NULL input vectors hold at least n elements

_**Synopsis:**_

   `
x_validate_length(n, ...)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`n` | an integer length 
`...` | an arbitrary list of vectors, some of which may be NULL 

_**Return value:**_
logical: TRUE if all input vectors have length\(\) at least n

_**Example:**_

```


x_validate_length(3, 1:2, 1:3)
# FALSE
x_validate_length(2, 1:2, 1:3)
# TRUE
x_validate_length(2, 1:2, 1:3, 1:4, 1:5)
# TRUE
x_validate_length(4, 1:8, 1:3, 1:4, 1:5)
# FALSE
x_validate_length(4, 1:8, NULL, 1:4, 1:5)
# TRUE

```
 
#### x_validate_problemdata

_**Purpose:**_

   Validate the problem data

Run a couple of sanity checks on the problem data to verify that no two descriptions \(C-style or R style\) are given. If problemdata violates any condition, an error is thrown.

_**Synopsis:**_

   `
x_validate_problemdata(prob, problemdata)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | prob an XPRSprob object 
`problemdata` | list object with attributes describing the input optimization problem. 

#### xprs_add_names_type

_**Purpose:**_

   adds a type of names \(rows, columns etc\) to the optimizer

_**Synopsis:**_

   `
xprs_add_names_type(prob, charvec, itype)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | XPRSprob pointer 
`charvec` | character vector or NULL, in which case, the function adds nothing 
`itype` | See the XPRSaddnames documention 

_**Return value:**_
the prob pointer, for possible data pipelines

#### xprs_addcol

_**Purpose:**_

   Create and add a new empty column to the problem.

This is a variant of `addcols()`that only adds a single column and also allows specifying type and name of the column.

_**Synopsis:**_

   `
xprs_addcol(prob, lb, ub, coltype = NULL, name = NULL, objcoef = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to which the column is to be added. 
`lb` | The lower bound for the new column. 
`ub` | The upper bound for the new column. 
`coltype` | Character specifying the column type. If this is `NULL` then the default Xpress column type is used \(continuous\). Possible values are:
 * `C`: indicates a continuous column.
 * `B`: indicates a binary column.
 * `I`: indicates an integer column.
 * `S`: indicates a semicontinuous column.
 * `R`: indicates a semiinteger column.
 * `P`: indicates a partial integer column.
 
`name` | The name for the new column. 
`objcoef` | The objective coefficient for the new column. 

_**Return value:**_
The function always returns `prob`.

#### xprs_addrow

_**Purpose:**_

   Create and add a new row to a problem.

This is a variant of `addrows()`that only adds a single row and also allows specifying the name of the row.

_**Synopsis:**_

   `
xprs_addrow(prob, colind, rowcoef, rowtype, rhs, name = NULL, rng = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to which the row is to be added. 
`colind` | The variable indices for the variables in the new row. 
`rowcoef` | The coefficients for the variables in the new row. 
`rowtype` | Character specifying the type of the new row. Possible values are:
 * `L`: indicates a `<=` row.
 * `G`: indicates `>=` row.
 * `E`: indicates an `=` row.
 * `R`: indicates a range constraint.
 * `N`: indicates a nonbinding constraint.
 
`rhs` | The right-hand side of the new row. 
`name` | The name of the new row. 
`rng` | The range value for the new row. 

_**Return value:**_
The function always returns `prob`.

#### xprs_getdoubleattributes

_**Purpose:**_

   Get a list of all attributes of type `double`.

_**Synopsis:**_

   `
xprs_getdoubleattributes()` 


_**Return value:**_
A list of all attributes of type `double`

_**Example:**_

```


prob <- createprob()
attrib_names = names(xprs_getdoubleattributes())

```
 
#### xprs_getdoublecontrols

_**Purpose:**_

   Get a list of all controls of type `double`.

_**Synopsis:**_

   `
xprs_getdoublecontrols()` 


_**Return value:**_
A list of all controls of type `double`

_**Example:**_

```


prob <- createprob()
control_names = names(xprs_getdoublecontrols())

```
 
#### xprs_getintattributes

_**Purpose:**_

   Get a list of all attributes of type `int`.

_**Synopsis:**_

   `
xprs_getintattributes()` 


_**Return value:**_
A list of all attributes of type `int`

_**Example:**_

```


prob <- createprob()
attrib_names = names(xprs_getintattributes())

```
 
#### xprs_getintcontrols

_**Purpose:**_

   Get a list of all controls of type `int`.

_**Synopsis:**_

   `
xprs_getintcontrols()` 


_**Return value:**_
A list of all controls of type `int`

_**Example:**_

```


prob <- createprob()
control_names = names(xprs_getintcontrols())

```
 
#### xprs_getsolution

_**Purpose:**_

   returns the optimal or best known solution of a solution process.

It is an error to invoke xprs\_getsolution\(\) before an optimization process was started using xprs\_optimize\(\), mipoptimize\(\), or lpoptimize\(\).

_**Synopsis:**_

   `
xprs_getsolution(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | the XPRSprob object holding the result of the optimization 

_**Return value:**_
Numeric vector of length COLS containing the optimal or best known solution for 'prob', or NULL if no such solution exists. In this case, a warning is raised.

#### xprs_getstringattributes

_**Purpose:**_

   Get a list of all attributes of type `string`.

_**Synopsis:**_

   `
xprs_getstringattributes()` 


_**Return value:**_
A list of all attributes of type `string`

_**Example:**_

```


prob <- createprob()
attrib_names = names(xprs_getstringattributes())

```
 
#### xprs_getstringcontrols

_**Purpose:**_

   Get a list of all controls of type `string`.

_**Synopsis:**_

   `
xprs_getstringcontrols()` 


_**Return value:**_
A list of all controls of type `string`

_**Example:**_

```


prob <- createprob()
control_names = names(xprs_getstringcontrols())

```
 
#### xprs_hasglobals

_**Purpose:**_

   Does the currently loaded optimization problem have MIP entities?

_**Synopsis:**_

   `
xprs_hasglobals(prob)` 


_**Further information:**_
This function is deprecated and will be removed from future releases. Please use ``xprs_hasmipentities``

#### xprs_hasmipentities

_**Purpose:**_

   Does the currently loaded optimization problem have MIP entities?

MIP entities comprise non-continuous column types such as integer or binary variables, but also indicator constraints, general constraints, and piecewise linear constructs.

_**Synopsis:**_

   `
xprs_hasmipentities(prob)` 


_**Argument:**_

Name |  Description
---------- | ---------- 
`prob` | XPRSprob pointer with an already loaded problem 

_**Return value:**_
TRUE if 'prob' has any form of MIP entities, FALSE otherwise

#### xprs_loadproblemdata

_**Purpose:**_

   Loads a new optimization problem into the optimizer

_**Synopsis:**_

   `
xprs_loadproblemdata(prob = NULL, problemdata)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | an XPRSprob object, or NULL to create a new one 
`problemdata` | a named list that describes the input data. The 'problemdata' understands all input arguments of the function XPRSloadmiqcqp. See the details below. 

_**Return value:**_
the XPRSprob object with the given optimization model loaded; this is either the `prob`passed to the call, or a newly created XPRSprob object.

_**Example:**_

```


# We load and solve the following Linear Program with 2 variables and 2 constraints.
#      min   x_1 +    x_2
#          5 x_1 +    x_2  >= 7
#            x_1 +  4 x_2  >= 9
#                 x_1,x_2  >= 0
library(xpress)
# create a list object to hold all input
problemdata <- list()
# objective coefficients
problemdata$objcoef <- c(1,1)
# row coefficients
problemdata$A <- matrix(c(5,1,1,4), nrow=2, byrow=TRUE)
# right-hand side
problemdata$rhs <- c(7,9)
# row sense
problemdata$rowtype <- c("G", "G")
# lower bounds (defaulting to 0 if unspecified)
problemdata$lb <- c(0,0)
# upper bounds(defaulting to Inf if unspecified)
problemdata$ub <- c(Inf,Inf)
# names for writing to MPS/LP files
problemdata$colname <- c("x_1", "x_2")
# Problem Name displayed when the solver solves the problem.
problemdata$probname <- "FirstExample"
# load everything into a new XPRSprob 'p'. You may also use the equivalent
#
# p <- createprob()
# xprs_loadproblemdata(p, problemdata=problemdata)
#
# for convenience and the use inside pipes,
# xprs_loadproblemdata returns the prob pointer.
#
p <- xprs_loadproblemdata(problemdata=problemdata)

```
 
_**Further information:**_
The data of a new optimization model is passed as a list object. Each named property declares parts of the input data for the FICO Xpress Optimizer. The linear part of the constraints, usually denoted by a coefficient matrix A, can be specified in two alternative ways through 'problemdata'. Either as a dense or sparse matrix object, or in the classical column-major representation of the C-API of Xpress. The C-style input should specify the following attributes in 'problemdata'. Note that all index vectors must be 0-based, which is different from the usual R-convention\! All names of the C-style input come from `XPRSloadmiqcqp()`.
 * `ncols`: Number of structural columns in the matrix. This is optional and usually inferred from 'lb', 'ub', and 'objcoef' problemdata attributes
 * `nrows`: Number of rows in the matrix \(not including the objective row\). This is optional and usually inferred from 'rowtype', 'rhs', and 'rng' problemdata attributes
 * `start`: 0-based\(\!\) integer array containing the offsets in the rowind and rowcoef arrays of the start of the elements for each column. This array is of length ncols or, if collen is NULL, length ncols+1. If collen is NULL the extra entry of start, start\[ncols+1\], contains the position in the rowind and rowcoef arrays at which an extra column would start, if it were present. In C, this value is also the length of the rowind and rowcoef arrays
 * `collen`: Integer array of length ncols containing the number of nonzero elements in each column. May be NULL if all elements are contiguous and start\[ncols+1\] contains the offset where the elements for column ncols+1 would start. This array is not required if the non-zero coefficients in the rowind and rowcoef arrays are continuous, and the start array has ncols+1 entries as described above. It may be NULL if not required
 * `rowind`: Integer array containing the 0-based\(\!\) row indices for the nonzero elements in each column. If the indices are input contiguously, with the columns in ascending order, the length of the rowind is start\[ncols\]+collen\[ncols\] or, if collen is NULL, start\[ncols+1\].
 * `rowcoef`: Double array containing the nonzero element values; length as for rowind
Alternatively, A can be specified directly as matrix input.
 * `A`: a dense or sparse matrix \(column major or sparse triplet format\) to input the linear constraint coefficients.
It is an error to specify A _and_any of the C-style input. The \(in-\)equalities are further described by a right-hand-side vector \(usually denoted as b\), the type of each constraint, and an optional rng vector.
 * `rhs`: Double array of length nrows containing the right hand side coefficients of the rows. The right hand side value for a rng row gives the upper bound on the row
 * `rowtype`: String array of length 'nrows' containing the row types:
     * `"L"`: indicates a '<=' constraint \(use this one for quadratic constraints as well\)
     * `"E"`: indicates an '=' constraint
     * `"G"`: indicates a '>=' constraint
     * `"R"`: indicates a rng constraint
     * `"N"`: indicates a nonbinding constraint

 * `rng`: Double array of length nrows containing the rng values for rng rows. Values for all other rows will be ignored. May be NULL if there are no ranged constraints. The lower bound on a rng row is the right hand side value minus the rng value. The sign of the rng value is ignored - the absolute value is used in all cases
Column properties are lower bounds, upper bounds, and objective coefficients.
 * `objcoef`: Double array of length 'ncols' containing the objective function coefficients
 * `lb`: Double array of length 'ncols' containing the lower bounds on the columns. Use XPRS\_MINUSINFINITY to represent a lower bound of minus infinity
 * `ub`: Double array of length 'ncols' containing the upper bounds on the columns. Use XPRS\_PLUSINFINITY to represent an upper bound of plus infinity
Column types can be specified for all columns. By default, all columns are continuous. However, columns can also have various discrete types. This happens either by indexing those columns that should be non-continuous in C-style, or by providing the "columntypes" \(and optionally, a "columnlimits"\)-vector, thereby avoiding any 0 vs. 1-based index confusion.
 * `nentities`: Number of binary, integer, semi-continuous, semi-continuous integer and partial integer entities. This is optional, as it can be inferred from 'gqtype', and 'entind'
 * `coltype`: Character array of length nentities containing the entity types
     * `"B"`: binary variables
     * `"I"`: integer variables
     * `"P"`: partial integer variables
     * `"S"`: semi-continuous variables
     * `"R"`: semi-continuous integer variables

 * `entind`: Integer array of length nentities containing the column indices of the MIP entities
 * `limit`: Double array of length nentities containing the integer limits for the partial integer variables and lower bounds for semi-continuous and semi-continuous integer variables \(any entries in the positions corresponding to binary and integer variables will be ignored\). May be NULL if not required
 _Or_full column type specification:
 * `columntypes`: A single character array of length 'ncols'. Besides the column types for 'coltype', specify all continuous columns by "C"
 * `columnlimits`: A single numeric array of length 'ncols' to specify limits for partial integer variables and lower bounds for semi-continuous and semi-continuous integer variables. This is not needed if no such types are present
It is an error if problemdata mixes columntypes in both representations, C-style and full column types style. A quadratic objective matrix can be specified as single \(sparse or dense\) matrix input 'Qobj', or in C-style notation. As matrix 'Qobj', in which case no index confusion between 0- and 1-based indexing can occur
 * `Qobj`: a dense or sparse matrix \(column major or sparse triplet format\) to input the quadratic objective terms
 _Or_C-style input:
 * `nobjqcoef`: Number of quadratic terms of the objective
 * `objqcol1`: Integer array of size nobjqcoef containing the 0-based\(\!\) column index of the first variable in each quadratic objective term
 * `objqcol2`: Integer array of size nobjqcoef containing the 0-based\(\!\) column index of the second variable in each quadratic objective term
 * `objqcoef`: Double vector of size nobjqcoef containing the quadratic objective coefficients
The same for quadratic terms in constraints. Specify them in C-style notation, or as a single list 'Qrowlist' of length 'nrows' of matrix objects, sparse or dense, with NULL elements for the rows that do not have quadratic terms. The matrix-style input argument:
 * `Qrowlist`: list of dense or sparse numeric matrices \(column major or sparse triplet format\) of length 'nrows' that define the quadratic terms in each constraint.
Alternatively, use the classic C-style input variant:
 * `nqrows`: Number of rows containing quadratic matrices
 * `qrowind`: Integer vector of size qmn, containing the indices of rows with quadratic matrices in them. Note that the rows are expected to be defined in rowtype as type L
 * `nrowqcoefs`: Integer vector of size qmn, containing the number of nonzeros in each quadratic constraint matrix
 * `rowqcol1`: Integer vector of size nqcelem, where nqcelem equals the sum of the elements in nrowqcoefs \(i.e. the total number of quadratic matrix elements in all the constraints\). It contains the first column indices of the quadratic matrices. Indices for the first matrix are listed from 0 to qcnquads\[0\]-1, for the second matrix from qcnquads\[0\] to qcnquads\[0\]+ qcnquads\[1\]-1, etc
 * `rowqcol2`: Integer array of size nqcelem, containing the second index for the quadratic constraint matrices
 * `rowqcoef`: Double array of size nqcelem, containing the coefficients for the quadratic constraint matrices
Special Ordered Sets \(SOS\) restrict the number of columns with a nonzero solution value. SOS constraints must be input in sparse row representation. Each row represents one SOS constraint whose member columns are given as indices together with a reference row value. It is also necessary to specify the type of each set using the 'settype' argument.
 * `settype`: Character array of length nsets containing the set types:
     * `1`: SOS1 type sets
     * `2`: SOS2 type sets

 * `nsets`: Number of SOS1 and SOS2 sets. This is readily inferred from settype and need not be specified.
 * `setstart`: Integer array containing the offsets in the setind and refval arrays indicating the start of the sets. This array is of length nsets+1, the last member containing the offset where set nsets+1 would start
 * `setind`: Integer array of length setstart\[nsets\]-1 containing the columns in each set
 * `refval`: Double array of length setstart\[nsets\]-1 containing the reference row entries for each member of the sets

 * `probname`: A string of up to MAXPROBNAMELENGTH characters containing a name for the problem
 * `colname`: \(optional\) a vector specifying a name for each column of the problem
 * `rowname`: \(optional\) a vector specifying a name for each row of the problem

#### xprs_newcol

_**Purpose:**_

   Create and add a new empty column to a problem.

This function is similar to `xprs_addcol`but instead of returning the `prob`object, it returns the index of the newly created column.

_**Synopsis:**_

   `
xprs_newcol(prob, lb, ub, coltype = NULL, name = NULL, objcoef = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to which the column is to be added. 
`lb` | The lower bound for the new column. 
`ub` | The upper bound for the new column. 
`coltype` | Character specifying the column type. If this is `NULL` then the default Xpress column type is used \(continuous\). Possible values are:
 * `C`: indicates a continuous column.
 * `B`: indicates a binary column.
 * `I`: indicates an integer column.
 * `S`: indicates a semicontinuous column.
 * `R`: indicates a semiinteger column.
 * `P`: indicates a partial integer column.
 
`name` | The name for the new column. 
`objcoef` | The objective coefficient for the new column. 

_**Return value:**_
The index of the newly created column.

_**Further information:**_
This is a variant of `addcols()`that only adds a single column and also allows specifying type and name of the column.

#### xprs_newrow

_**Purpose:**_

   Create and add a new row to a problem.

This function is similar to `xprs_addrow`but instead of returning the `prob`object, it returns the index of the newly created row.

_**Synopsis:**_

   `
xprs_newrow(prob, colind, rowcoef, rowtype, rhs, name = NULL, rng = NULL)` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | The problem to which the row is to be added. 
`colind` | The variable indices for the variables in the new row. 
`rowcoef` | The coefficients for the variables in the new row. 
`rowtype` | Character specifying the type of the new row. Possible values are:
 * `L`: indicates a `<=` row.
 * `G`: indicates `>=` row.
 * `E`: indicates an `=` row.
 * `R`: indicates a range constraint.
 * `N`: indicates a nonbinding constraint.
 
`rhs` | The right-hand side of the new row. 
`name` | The name of the new row. 
`rng` | The range value for the new row. 

_**Return value:**_
The index of the newly created row.

_**Further information:**_
This is a variant of `addrows()`that only adds a single row and also allows specifying the name of the row.

#### xprs_optimize

_**Purpose:**_

   Invoke a solution process with the FICO Xpress Optimizer

This function will invoke the suitable optimization routine for an XPRSprob object which holds an already loaded optimization problem. The actual solving behavior is similar to that of ``optimize``. However, this function allows to specify the solution method of the initial LP relaxation via flags and returns the prob object itself, making it suitable for usage with pipes.

_**Synopsis:**_

   `
xprs_optimize(prob, sflags = "")` 


_**Arguments:**_

Name |  Description
---------- | ---------- 
`prob` | an XPRSprob object, into which a problem has been loaded already. 
`sflags` | Flags to pass to the optimization method, which specifies how to solve the initial continuous problem where the MIP entities are relaxed. 

_**Return value:**_
the XPRSprob object

_**Example:**_

```


problemdata <- list()
problemdata$A <- matrix(c(1,0,0,1),nrow=2)
problemdata$rhs <- c(1,2)
problemdata$objcoef <- c(1,2)
problemdata$lb <- c(0,0)
problemdata$ub <- c(Inf,Inf)
problemdata$rowtype <- c("G", "E")
prob <- xprs_loadproblemdata(problemdata=problemdata)
xprs_optimize(prob)

```
 