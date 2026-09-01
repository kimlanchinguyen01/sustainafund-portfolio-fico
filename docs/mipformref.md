# FICO® Xpress Optimization

# MIP formulations and linearizations
## Quick reference


#### Release 9.9


#### __Last update 20 August, 2026__



(C) 2009-2026 Fair Isaac Corporation. All rights reserved. 
This documentation is the property of Fair Isaac Corporation ("FICO"). Receipt or possession of this documentation does not convey rights to disclose, reproduce, make derivative works, use, or allow others to use it except solely for internal evaluation purposes to determine whether to purchase a license to the software described in this documentation, or as otherwise set forth in a written software license agreement between you and FICO (or a FICO affiliate).  Use of this documentation and the software described in it must conform strictly to the foregoing permitted uses, and no other use is permitted.

The information in this documentation is subject to change without notice. If you find any problems in this documentation, please report them to us in writing. Neither FICO nor its affiliates warrant that this documentation is error-free, nor are there any other warranties with respect to the documentation except as may be provided in the license agreement. FICO and its affiliates specifically disclaim any warranties, express or implied, including, but not limited to, non-infringement, merchantability and fitness for a particular purpose. Portions of this documentation and the software described in it may contain copyright of various authors and may be licensed under certain third-party licenses identified in the software, documentation, or both.

In no event shall FICO or its affiliates be liable to any person for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this documentation or the software described in it, even if FICO or its affiliates have been advised of the possibility of such damage. FICO and its affiliates have no obligation to provide maintenance, support, updates, enhancements, or modifications except as required to licensed users under a license agreement.

FICO is a registered trademark of Fair Isaac Corporation in the United States and may be a registered trademark of Fair Isaac Corporation in other countries. Other product and company names herein may be trademarks of their respective owners.

Patent(s): [www.fico.com/en/patents](https://www.fico.com/en/patents})

FICO® Xpress Optimization 9.9

Deliverable Version: A

Last Revised: 20 August, 2026


## Section 1 Introduction


This quick reference guide presents a collection of MIP model formulations for Xpress Optimizer, including standard linearization techniques involving binary variables, the use of more specific modeling objects such as SOS and partial integer variables, and reformulations of logic constraints through indicator constraints.

### Integer Programming entities supported in Xpress


 * _Binary variables (BV)_– decision variables that must take either the value 0 or the value 1, sometimes called 0/1 variables;
 * _Integer variables (UI)_– decision variables that must take on integer values. Some upper limit must be specified;
 * _Partial integer variables (PI)_– decision variables that must take integer values below a specified limit but can take any value above that limit;
 * _Semi-continuous variables (SC)_– decision variables that must take on either the value 0, or any value in a range whose lower an upper limits are specified. SCs help model situations where, if a variable is to be used at all, it has to be at some minimum level;
 * _Semi-continuous integer variables (SI)_– decision variables that must take either the value 0, or any integer value in a range whose lower and upper limits are specified;
 * _Special ordered sets of type one (SOS1)_– an ordered set of variables of which at most one can take a nonzero value;
 * _Special ordered sets of type two (SOS2)_– an ordered set of variables of which at most two can be nonzero, and if two are nonzero, they must be consecutive in their ordering.

**Remarks** 

 * The solution values of binary and integer variables are real valued, not integer valued.
 * At an optimal MIP solution, the actual values of the binary and integer variables will be integer– to within a certain tolerance.

### Integer Programming entities in Mosel


**Definition** : integer programming types are defined as unary constraints on previously declared decision variables of type `mpvar`; name the constraints if you want to be able to access/modify them.

```
model "intromip"
 uses "mmxprs"
 declarations
  d: mpvar
  ifmake: array(PRODS,LINES) of mpvar
  x: mpvar
 end-declarations

 d is_binary                      ! Single binary variable
 forall(p in PRODS, l in LINES)
  ifmake(p,l) is_binary           ! An array of binaries

 ACtr:= x is_integer              ! An integer variable
 x >= MINVAL                      ! Lower bound on the variable
 x <= MAXVAL                      ! Upper bound on the variable
 ! MINVAL,MAXVAL: values between -MAX_REAL and MAX_REAL
 ...
 ACtr:= x is_partint 10           ! Change type to partial integer
 ...
 ACtr:= 0                         ! Delete constraint
! Equivalently:
 ACtr:= x is_continuous           ! Change type to continuous
 ...
```


**Solving** : with Xpress Solver \(Mosel modules _mmxprs_ or _mmxnlp_\) any problem containing integer programming entities is automatically solved as a MIP problem, to solve just the LP relaxation set the control `XPRS_MIPSTOPSTAGE` \(if following up with MIP search\) or use the option `XPRS_LIN` \(ignore all MIP information\) for `maximize` / `minimize`.

```

 minimize(d)                      ! Solve the MIP problem
 minimize(XPRS_LIN, d)            ! Solve as LP problem

 setparam("XPRS_MIPSTOPSTAGE", XPRS_MIPSTOPSTAGE_INITIALRELAXATION) 
 minimize(d)                      ! Solve the LP relaxation...
 setparam("XPRS_MIPSTOPSTAGE", XPRS_MIPSTOPSTAGE_NONE) 
 minimize(XPRS_CONT, d)           ! ...continue with MIP solving
```


**Accessing the solution** : for obtaining solution values of decision variables and linear expressions use `getsol` \(alternative syntax: `.sol`\); the solution status is returned by the function `getparam("XPRS_SOLSTATUS")`

```
 case getparam("XPRS_SOLSTATUS") of
   XPRS_SOLSTATUS_UNBOUNDED:  writeln("LP unbounded")
   XPRS_SOLSTATUS_NOTFOUND:   writeln("No solution available")
   XPRS_SOLSTATUS_INFEAS:     writeln("Problem is infeasible")
   XPRS_SOLSTATUS_FEASIBLE,
     XPRS_SOLSTATUS_OPTIMAL:  writeln("MIP solution: ", getobjval)
 end-case

 writeln("x: ", getsol(x))
 writeln("d: ", d.sol)
```


### Integer Programming entities in the Xpress Python API


**Definition** : Integer Programming types are specified when creating decision variables; types may be changed with `vartype`.

```
import xpress as xp

MAXVAL = 50
NP = 5
NL = 6

p = xp.problem()

# A single binary variable
d = p.addVariable(vartype=xp.binary, name="d")                      

# A NumPy array of variables
ifmake = p.addVariables(NP, NL, vartype=xp.binary, name="ifmake")   

 # An integer variable with an upper bound
x = p.addVariable(lb=0, ub=MAXVAL, vartype=xp.integer, name="x")

x.vartype = xp.partiallyinteger    # Change type to partial integer
x.threshold = 10

x.vartype = xp.continuous          # Change type to continuous
```


**Solving** : to solve a MIP problem use method `optimize` of `xp.problem`. This call is usually preceded by the definition of the objective function via `setObjective` that also allows you to change the sense of the optimization \(the default optimization direction is minimization\).

```
p.setObjective(d)
p.optimize()
```


**Accessing the solution** : for obtaining solution values of decision variables use `getSolution`; the MIP problem status is returned by `p.attributes.solstatus`. Import `SolStatus` from `xpress.enums` at the top of the script to access the possible solution values.

```
from xpress.enums import SolStatus

match p.attributes.solstatus:
    case SolStatus.FEASIBLE | SolStatus.OPTIMAL:
        print("MIP solution: ", p.attributes.objval())
    case SolStatus.INFEASIBLE:
        print("Problem is infeasible")
    case SolStatus.UNBOUNDED:
        print("LP unbounded")
    case SolStatus.NOTFOUND:
        print("Solution not found")

print(x.name,": ",p.getSolution(x))

```


### Integer Programming entities in the Xpress C++ API


The code extracts for the object-oriented APIs of Xpress Solver shown in this document are formulated for the C++ interface. The other object-oriented APIs \(Java, C\#\) work similarly, please refer to the [Xpress Java API user guide](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/java_objects_ug/dhtml) and [Xpress C\#API user guide](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/net_objects_ug/dhtml) for further detail.

**Definition** : Integer Programming types are specified when creating decision variables; types may be changed with `setType`.

```
# include <iostream>
# include <xpress.hpp>
using namespace xpress;
using namespace xpress::objects;
using namespace std;

int main()
{
  XpressProblem prob;

  Variable d = prob.addVariable(ColumnType::Binary, "d"); // Single binary variable

  auto ifmake = prob.addVariables(NP, NL)  // 2-dim array of binary variables
    .withType(ColumnType::Binary)
    .withName("ifmake_% d_% d")    .toArray();

  // An integer variable
  Variable x = prob.addVariable(0, MAXVAL, ColumnType::Integer, "x");
  ...
  x.setType(ColumnType::PartialInteger);   // Change type to partial integer
  x.setLimit(10);                          // Set the partial integer limit value
  ...
  x.setType(ColumnType::Continuous);       // Change type to continuous
  ...
```


**Solving** : to solve a MIP problem use method `optimize` of `XpressProblem`. This call is usually preceded by the definition of the objective function via `setObjective` that also allows you to change the sense of the optimization \(the default optimization direction is minimization\). To solve just the LP relaxation use `lpOptimize`.

```
  prob.setObjective(d, ObjSense::Maximize);
  prob.optimize();
```


**Accessing the solution** : for obtaining solution values of decision variables use `getSolution`; the MIP problem status is returned by the attribute `getMipStatus`.

```
  auto mipStatus = prob.attributes.getMipStatus();
  switch (mipStatus) {
    case MIPStatus::NotLoaded:
    case MIPStatus::LPNotOptimal:
      cout << "Solving not started" << endl;
      break;
    case MIPStatus::LPOptimal:
      cout << "Root LP solved" << endl;
      break;
    case MIPStatus::Unbounded:
      cout << "LP unbounded" << endl;
      break;
    case MIPStatus::NoSolutionFound:
    case MIPStatus::Infeasible:
      cout << "MIP search started, no solution" << endl;
      break;
    case MIPStatus::Solution:
    case MIPStatus::Optimal:
      cout << "MIP solution: " << prob.attributes.getObjVal() << endl;
      break;
  }

  cout << x.getName() << ": " << x.getSolution() << endl;

```


## Section 2 Binary variables


_Binary decision variables_
 * take value 0 or 1
 * model a discrete decision
     * yes/no
     * on/off
     * open/close
     * build or don't build
     * strategy A or strategy B



### Logical conditions


Projects A, B, C, D, ... with associated binary variables _a_ , _b_ , _c_ , _d_ , ... which are 1 if we decide to do the project and 0 if we decide not to do the project.


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
At most N of A, B, C,... | _a + b + c + ...≤N_ | 
At least N of A, B, C,... | _a + b + c + ...≥N_ | 
Exactly N of A, B, C,... | _a + b + c + ... = N_ | 
If A then B | _b≥a_ | 
Not B | _not(b) = 1-b_ | 
If A then not B | _a + b≤1_ | 
If not A then B | _a + b≥1_ | 
If A then B, and if B then A | _a = b_ | 
If A then B and C; A only if B and C | _b≥a_ and _c≥a_ | 
|  | or alternatively: _a≤\(b + c\)/2_ | 
If A then B or C | _b + c≥a_ | 
If B or C then A | _a≥b_ and _a≥c_ | 
|  | or alternatively: _a≥\(1\) / \(2\)·\(b+c\)_ | 
If B and C then A | _a≥b + c - 1_ | 
If two or more of B, C, D or E then A | _a≥\(1\) / \(3\)·\(b + c + d + e - 1\)_ | 
If M or more of N projects \(B, C, D, ...\) then A | _a≥\(b + c + d + ... -M +1\) / \(N-M+1\)_ | 

### Minimum values


_**y = min\{ x<sub>1</sub>, x<sub>2</sub>\}** _  for two continuous variables _x<sub>1</sub>, x<sub>2</sub>_ 

 * Must know lower and upper bounds

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_L<sub>1</sub>≤x<sub>1</sub>≤U<sub>1</sub>_ | \[1.1\] | 
_L<sub>2</sub>≤x<sub>2</sub>≤U<sub>2</sub>_ | \[1.2\] | 

 * Introduce binary variables _d<sub>1</sub>, d<sub>2</sub>_  to mean

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_d<sub>i</sub>_ | 1 if _x<sub>i</sub>_ is the minimum value; | 
|  | 0 otherwise | 

 * MIP formulation:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_y≤x<sub>1</sub>_ | \[2.1\] | 
_y≤x<sub>2</sub>_ | \[2.2\] | 
_y≥x<sub>1</sub>- \(U<sub>1</sub>- L<sub>min</sub>\)·\(1 - d<sub>1</sub>\)_ | \[3.1\] | 
_y≥x<sub>2</sub>- \(U<sub>2</sub>- L<sub>min</sub>\)·\(1 - d<sub>2</sub>\)_ | \[3.2\] | 
_d<sub>1</sub>+ d<sub>2</sub>= 1_ | \[4\] | 

 * Generalization to _**y = min\{ x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>n</sub>\}** _ 

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_L<sub>i</sub>≤x<sub>i</sub>≤U<sub>i</sub>_ | \[1.i\] | 
_y≤x<sub>i</sub>_ | \[2.i\] | 
_y≥x<sub>i</sub>- \(U<sub>i</sub>- L<sub>min</sub>\)·\(1 - d<sub>i</sub>\)_ | \[3.i\] | 
_∑<sub>i</sub>d<sub>i</sub>= 1_ | \[4\] | 

 * See Section  _General constraints_ for an alternative formulation via general constraints

### Maximum values


_**y = max\{ x<sub>1</sub>, x<sub>2</sub>, ..., x<sub>n</sub>\}** _  for continuous variables _x<sub>1</sub>, ..., x<sub>n</sub>_ 

 * Must know lower and upper bounds

_L<sub>i</sub>≤x<sub>i</sub>≤U<sub>i</sub>_ \[1.i\] 

 * Introduce binary variables _d<sub>1</sub>, ..., d<sub>n</sub>_ 
   *   _d<sub>i</sub>=1_ if _x<sub>i</sub>_ is the maximum value, 0 otherwise

 * MIP formulation

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_L<sub>i</sub>≤x<sub>i</sub>≤U<sub>i</sub>_ | \[1.i\] | 
_y≥x<sub>i</sub>_ | \[2.i\] | 
_y≤x<sub>i</sub>+ \(U<sub>max</sub>- L<sub>i</sub>\)·\(1 - d<sub>i</sub>\)_ | \[3.i\] | 
_∑<sub>i</sub>d<sub>i</sub>= 1_ | \[4\] | 


 * See Section  _General constraints_ for an alternative formulation via general constraints

### Absolute values


_**y = &#124; x<sub>1</sub> - x<sub>2</sub> &#124;** _  for two variables _x<sub>1</sub>, x<sub>2</sub>_  with _0≤x<sub>i</sub>≤U_ 

 * Introduce binary variables _d<sub>1</sub>, d<sub>2</sub>_  to mean

| &nbsp; | 
---------- | 
_d<sub>1</sub>_ : 1 if _x<sub>1</sub>- x<sub>2</sub>_ is the positive value | 
_d<sub>2</sub>_ : 1 if _x<sub>2</sub>- x<sub>1</sub>_ is the positive value | 

 * MIP formulation

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_0≤x<sub>i</sub>≤U_ | \[1.i\] | 
_0≤y - \(x<sub>1</sub>-x<sub>2</sub>\)≤2·U·d<sub>2</sub>_ | \[2\] | 
_0≤y - \(x<sub>2</sub>-x<sub>1</sub>\)≤2·U·d<sub>1</sub>_ | \[3\] | 
_d<sub>1</sub>+ d<sub>2</sub>= 1_ | \[4\] | 

 * See Section  _General constraints_ for an alternative formulation via general constraints

### Logical AND


_**d = min\{ d<sub>1</sub>, d<sub>2</sub>\}** _  for two binary variables _d<sub>1</sub>, d<sub>2</sub>_ , or equivalently

 _**d = d<sub>1</sub>· d<sub>2</sub>** _ \(see Section  _Product values_\), or

 _**d = d<sub>1</sub>AND d<sub>2</sub>** _ as a logical expression

 * IP formulation

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_d≤d<sub>1</sub>_ | \[1.1\] | 
_d≤d<sub>2</sub>_ | \[1.2\] | 
_d≥d<sub>1</sub>+ d<sub>2</sub>- 1_ | \[2\] | 
_d≥0_ | \[3\] | 

 * Generalization to _**d = min\{ d<sub>1</sub>, d<sub>2</sub>, ..., d<sub>n</sub>\}** _ 

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_d≤d<sub>i</sub>_ | \[1.i\] | 
_d≥ ∑<sub>i</sub>d<sub>i</sub>- \(n - 1\)_ | \[2\] | 
_d≥0_ | \[3\] | 
 Note: equivalent to _**d = d<sub>1</sub>· d<sub>2</sub>·...· d<sub>n</sub>** _ 
   *  and \(as a logical expression\): _**d = d<sub>1</sub>AND d<sub>2</sub>AND ... AND d<sub>n</sub>** _ 

 * See Section  _Boolean variables and logical constraints_ for an alternative formulation via Boolean variables

### Logical OR


_**d = max\{ d<sub>1</sub>, d<sub>2</sub>\}** _  for two binary variables _d<sub>1</sub>, d<sub>2</sub>_ , or

 _**d = d<sub>1</sub>OR d<sub>2</sub>** _ as a logical expression

 * IP formulation

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_d≥d<sub>1</sub>_ | \[1.1\] | 
_d≥d<sub>2</sub>_ | \[1.2\] | 
_d≤d<sub>1</sub>+ d<sub>2</sub>_ | \[2\] | 
_d≤1_ | \[3\] | 

 * Generalization to _**d = max\{ d<sub>1</sub>, d<sub>2</sub>, ..., d<sub>n</sub>\}** _ 

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_d≥d<sub>i</sub>_ | \[1.i\] | 
_d≤ ∑<sub>i</sub>d<sub>i</sub>_ | \[2.i\] | 
_d≤1_ | \[3\] | 
 Note: equivalent to _**d = d<sub>1</sub>OR d<sub>2</sub>...OR d<sub>n</sub>** _ 
 * See Section  _Boolean variables and logical constraints_ for an alternative formulation via Boolean variables

### Logical NOT


_**d =NOT d<sub>1</sub>** _  for one binary variable _d<sub>1</sub>_ 

 * IP formulation

_d = 1 - d<sub>1</sub>_ 


### Product values


_**y = x· d** _  for one continuous variable _x_ , one binary variable _d_ 

 * Must know lower and upper bounds

_L≤x≤U_ 

 * MIP formulation:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_L·d≤y≤U·d_ | \[1\] | 
_L·\(1 - d\)≤x - y≤U·\(1 - d\)_ | \[2\] | 


Product of two binaries: _**d<sub>3</sub> = d<sub>1</sub>· d<sub>2</sub>** _ 

 * MIP formulation:

| &nbsp; | 
---------- | 
_d<sub>3</sub>≤d<sub>1</sub>_ | 
_d<sub>3</sub>≤d<sub>2</sub>_ | 
_d<sub>3</sub>≥d<sub>1</sub>+ d<sub>2</sub>-1_ | 


### Disjunctions


**Either  _**5≤ x≤ 10** _  or  _**80≤ x≤ 100** _ ** 

 * Introduce a new binary variable:
   *   _ifupper_ : 0 if _5≤x≤10_ ; 1 if _80≤x≤100_ 

 * MIP formulation:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_x≤10 + \(100 - 10\)·ifupper_ | \[1\] | 
_x≥5 + \( 80 - 5\)·ifupper_ | \[2\] | 


 * Generalization to **Either  _**L<sub>1</sub>≤∑<sub>i</sub> A<sub>i</sub>· x<sub>i</sub>≤ U<sub>1</sub>** _  or  _**L<sub>2</sub>≤∑<sub>i</sub> A<sub>i</sub>· x<sub>i</sub>≤ U<sub>2</sub>** _  \(with  _**U<sub>1</sub>≤ L<sub>2</sub>** _ \)** 

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_∑<sub>i</sub>A<sub>i</sub>·x<sub>i</sub>≤U<sub>1</sub>+ \(U<sub>2</sub>- U<sub>1</sub>\)·ifupper_ | \[1\] | 
_∑<sub>i</sub>A<sub>i</sub>·x<sub>i</sub>≥L<sub>1</sub>+ \(L<sub>2</sub>- L<sub>1</sub>\)·ifupper_ | \[2\] | 


### Minimum activity level


Continuous production rate _make_  that may be 0 \(the plant is not operating\) or between allowed production limits _MAKEMIN_  and _MAKEMAX_ 

 * Introduce a binary variable _ifmake_  to mean

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_ifmake_ : | 0 if plant is shut | 
|  | 1 plant is open | 
 MIP formulation:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_make≥MAKEMIN·ifmake_ | \[1\] | 
_make≤MAKEMAX·ifmake_ | \[2\] | 
 Note: see Section  _Minimum activity level_ for an alternative formulation using semi-continuous variables
 * The _ifmake_  binary variable also allows us to model fixed costs
     * _FCOST_ : fixed production cost
     * _VCOST_ : variable production cost
 MIP formulation:

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_cost = FCOST·ifmake + VCOST·make_ | \[3\] | 
_make≥MAKEMIN·ifmake_ | \[1\] | 
_make≤MAKEMAX·ifmake_ | \[2\] | 


## Section 3 MIP formulations using other entities


In principle, all you need in building MIP models are continuous variables and binary variables. But it is convenient to extend the set of modeling entities to embrace objects that frequently occur in practice.

_Integer decision variables_
 * values 0, 1, 2, ... up to small upper bound
 * model discrete quantities
 * try to use _partial integer variables_ instead of integer variables with a very large upper bound


_Semi-continuous variable_
 * may be zero, or any value between the intermediate bound and the upper bound
 * _Semi-continuous integer variables_ also available: may be zero, or any integer value between the intermediate bound and the upper bound


_Special ordered sets_
 * set of decision variables
 * each variable has a different ordering value, which orders the set
 * Special ordered sets of type 1 \(SOS1\): at most one variable may be non-zero
 * Special ordered sets of type 2 \(SOS2\): at most two variables may be non-zero; the non-zero variables must be adjacent in ordering


_Indicator constraints_
 * associate a binary variable with a linear or nonlinear constraint
 * model an implication: the constraint is active only if the condition is true


_General constraints_
 * specific constraint relations that are recognized by MIP solvers
 * piecewise linear: can be used in place of SOS-2 formulations
 * absolute value, minimum value, maximum value of discrete or continuous decision variables
 * logical constraints: 'and' and 'or' over binary variables


### Batch sizes


Must deliver in batches of 10, 20, 30, ...

 * Decision variables

| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_nship_ | number of batches delivered: integer | 
_ship_ | quantity delivered: continuous | 

 * Constraint formulation

_ship = 10·nship_ 


### Ordered alternatives


Suppose you have _N_  possible investments of which at most one can be selected. The capital cost is _CAP<sub>i</sub>_  and the expected return is _RET<sub>i</sub>_ .

 * Often use binary variables to choose between alternatives. However, SOS1 are more efficient to choose between a set of graded \(ordered\) alternatives.
 * Define a variable _d<sub>i</sub>_  to represent the decision, _d<sub>i</sub>= 1_  if investment _i_  is picked
 * Binary variable \(standard\) formulation
   *  
   *  d<sub>i</sub>: binary variables

| &nbsp; | 
---------- | 
_Maximize:ret = ∑<sub>i</sub>RET<sub>i</sub>·d<sub>i</sub>_ | 
_∑<sub>i</sub>d<sub>i</sub>≤1_ | 
_∑<sub>i</sub>CAP<sub>i</sub>·d<sub>i</sub>≤MAXCAP_ | 


 * SOS1 formulation
   *  
   *  \{d<sub>i</sub>; ordering value CAP<sub>i</sub>\}: SOS1

| &nbsp; | 
---------- | 
_Maximize:ret = ∑<sub>i</sub>RET<sub>i</sub>·d<sub>i</sub>_ | 
_∑<sub>i</sub>d<sub>i</sub>≤1_ | 
_∑<sub>i</sub>CAP<sub>i</sub>·d<sub>i</sub>≤MAXCAP_ | 


**Special ordered sets in Mosel** 
 * special ordered sets are a special type of linear constraint
 * the set includes all variables in the constraint
 * the coefficient of a variable is used as the ordering value \( _i.e._ , each value must be unique\)


```
declarations
  I=1..4
  d: array(I) of mpvar
  CAP: array(I) of real
  My_Set, Ref_row: linctr
end-declarations

My_Set:= sum(i in I) CAP(i)*d(i) is_sos1
```


or alternatively \(must be used if a coefficient is 0\):

```
Ref_row:= sum(i in I) CAP(i)*d(i)
makesos1(My_Set, union(i in I) {d(i)}, Ref_row)
```


**Special ordered sets in the Python API** 
 * special ordered sets are defined as constraints, specifying the set type \('1' or '2'\), a list of variables and the corresponding weight coefficients


```
import xpress as xp

I = range(4)
CAP = [10, 20, 100, 250]

p = xp.problem()

# Create the decision variables
d = [prob.addVariable(name="d_{} ".format(i)) for i in I]

# Define a SOS-1 with weights CAP
p.addSOS(d, CAP, name="My_Set", type=1)
```


**Special ordered sets in the C++ API** 
 * special ordered sets are defined as constraints, specifying the set type \('SOS1' or 'SOS2'\), a list of variables and the corresponding weight coefficients


```
static std::vector<int> I = {0, 1, 2, 3};
int main()
{
  XpressProblem prob;
  std::vector<double> CAP = {10, 20, 100, 250};

  // Create the decision variables
  auto d = prob.addVariables(I.size()).withName("d_% d").toArray();

  // Define a SOS-1 with weights CAP
  prob.addConstraint(SOS::sos(SetType::SOS1, d, CAP, "My_Set"));
```


### Price breaks


#### All items discount


**All items discount** : when buying a certain number of items we get discounts on _all_ items that we buy if the quantity we buy lies in certain price bands.

![Intro/pricebreakai](Graphic/Intro/pricebreakai.png)



| &nbsp; | &nbsp; | 
---------- |  ---------- | 
less than _B<sub>1</sub>_ | _COST<sub>1</sub>_ each | 
_≥B<sub>1</sub>_ and _<B<sub>2</sub>_ | _COST<sub>2</sub>_ each | 
_≥B<sub>2</sub>_ and _<B<sub>3</sub>_ | _COST<sub>3</sub>_ each | 

Formulation with binary variables or Special Ordered Sets of type 1 \(SOS1\):

 * Define binary variables _b<sub>i</sub>_  \(i=1,2,3\), where _b<sub>i</sub>_  is 1 if we pay a unit cost of _COST<sub>i</sub>_ .
 * Real decision variables _xp<sub>i</sub>_  represent the number of items bought at price _COST<sub>i</sub>_ .
 * The quantity bought is given by _x= ∑<sub>i</sub>xp<sub>i</sub>_ , with a total price of _∑<sub>i</sub>COST<sub>i</sub>·xp<sub>i</sub>_ 
 * MIP formulation :

| &nbsp; | 
---------- | 
_∑<sub>i</sub>b<sub>i</sub>= 1_ | 
_xp<sub>1</sub>≤B<sub>1</sub>·b<sub>1</sub>_ | 
_B<sub>i-1</sub>·b<sub>i</sub>≤xp<sub>i</sub>≤B<sub>i</sub>·b<sub>i</sub>_ for _i=2,3_ | 
 where the variables _b<sub>i</sub>_  are either defined as binaries, or they form a Special Ordered Set of type 1 \(SOS1\), where the order is given by the values of the breakpoints _B<sub>i</sub>_ .

Formulation as piecewise linear expression:

 * Specification as list of piecewise linear segments with associated intervals:

_⋃<sub>i=1,2,3</sub>\[B<sub>i-1</sub>,B<sub>i</sub>\[ : COST<sub>i</sub>·x_ 

```
TotalCost:= pwlin(union(i in 1..3) [pws(B(i-1), COST(i)*x)])
```


```
totalcost = xp.pwl({(B[i-1],B[i]): COST[i]*x[i] for i in range(1,3)})
```


 * Specification as list of points:

_⋃<sub>i=1,2,3</sub>\[B<sub>i-1</sub>,COST<sub>i</sub>·B<sub>i-1</sub>,B<sub>i</sub>,COST<sub>i</sub>·B<sub>i</sub>]_ 

```
TotalCost:= pwlin(x, union(i in 1..3) [B(i-1), COST(i)*B(i-1), B(i), COST(i)*B(i)])
```


In Python, it is possible to specify piecewise linear functions as a list of points using the `problem.addpwlcons` method. The example assumes that `B` and `COST` are array \(lists\) containing the x-values and y-values of the breakpoints, respectively.

```
prob.addpwlcons([x], [totalcost], [0], B, COST)
```


```
Variable x = prob.addVariable();
Variable fx = prob.addVariable();
std::vector<double> B = ...;
std::vector<double> COST = ...;
std::vector<double> breakX = {0, B[0], B[0], B[1], B[1], B[2]};
std::vector<double> breakY = {0, B[0]*COST[0], B[0]*COST[1], B[1]*COST[1],
                              B[1]*COST[2], B[2]*COST[2]};
prob.addConstraint(fx.pwlOf(x, breakX, breakY));
```



#### Incremental pricebreaks


**Incremental pricebreaks** : when buying a certain number of items we get discounts incrementally. The unit cost for items between 0 and _B<sub>1</sub>_  is _COST<sub>1</sub>_ , items between _B<sub>1</sub>_  and _B<sub>2</sub>_  cost _COST<sub>2</sub>_  each, _etc._ 

![Intro/pricebrinc2](Graphic/Intro/pricebrinc2.png)


Formulation with Special Ordered Sets of type 2 \(SOS2\):

 * Associate real valued decision variables _w<sub>i</sub>_  \( _i=0,1,2,3_ \) with the quantity break points _B<sub>0</sub>= 0_ , _B<sub>1</sub>_ , _B<sub>2</sub>_  and _B<sub>3</sub>_ .
 * Cost break points _CBP<sub>i</sub>_  \(=total cost of buying quantity _B<sub>i</sub>_ \):

| &nbsp; | 
---------- | 
_CBP<sub>0</sub>=0_ | 
_CBP<sub>i</sub>= CBP<sub>i-1</sub>+COST<sub>i</sub>·\(B<sub>i</sub>-B<sub>i-1</sub>\)_ for _i=1,2,3_ | 

 * Constraint formulation:

| &nbsp; | 
---------- | 
_∑<sub>i</sub>w<sub>i</sub>=1_ | 
_TotalCost = ∑<sub>i</sub>CBP<sub>i</sub>·w<sub>i</sub>_ | 
_x = ∑<sub>i</sub>B<sub>i</sub>·w<sub>i</sub>_ | 
 where the _w<sub>i</sub>_  form a SOS2 with reference row coefficients given by the coefficients in the definition of the total amount _x_ .
   *  For a solution to be valid, at most two of the _w<sub>i</sub>_ can be non-zero, and if there are two non-zero they must be contiguous, thus defining one of the line segments.

`is_sos2`  cannot be used here due to the 0-valued coefficient of  _w<sub>0</sub>_ 

```
  Defx := x = sum(i in 1..3) B(i)*w(i)
  makesos2(My_Set, union(i in 0..3) {w(i)}, Defx)
  sum(i in 1..3) w(i) = 1
```


```
p.addSOS(w, B, type=2)
p.addConstraint(xp.Sum(w) == 1)
```


```
  std::vector<int> I = {0, 1, 2};
  std::vector<double> B = ...;
  auto x = prob.addVariable();
  auto w = prob.addVariables(I.size()).withName("w_% d").toArray();
  prob.addConstraint(SOS::sos(SetType::SOS2, w, B, "Defx"));
  prob.addConstraint(sum(I, [&](auto i) { return w[i];}) == 1.0);
```


Formulation using binaries:

 * Define binary variables _b<sub>i</sub>_  \(i=1,2,3\), where _b<sub>i</sub>_  is 1 if we have bought any items at a unit cost of _COST<sub>i</sub>_ .
 * Real decision variables _xp<sub>i</sub>_  \(i=1,..3\) for the number of items bought at price _COST<sub>i</sub>_ .
 * Total amount bought: x =∑<sub>i</sub> xp<sub>i</sub>
 * Constraint formulation:

| &nbsp; | 
---------- | 
_\(B<sub>i</sub>-B<sub>i-1</sub>\)·b<sub>i+1</sub>≤xp<sub>i</sub>≤\(B<sub>i</sub>-B<sub>i-1</sub>\)·b<sub>i</sub>_ for _i=1,2_ | 
_xp<sub>3</sub>≤\(B<sub>3</sub>-B<sub>2</sub>\)·b<sub>3</sub>_ | 
_b<sub>1</sub>≥b<sub>2</sub>≥b<sub>3</sub>_ | 


Formulation as piecewise linear expression:

 * Specification as list of slopes with associated intervals:

_⋃<sub>i=1,2,3</sub>\[B<sub>i-1</sub>,B<sub>i</sub>\[ : COST<sub>i</sub>_ 

Only points of slope changes are specified, start value is 0

```
TotalCost:= pwlin(x, union(i in 1..2) [B(i)], union(i in 1..3) [COST(i)])
```


**Python**  does not support specifying piecewise linear functions as a list of slopes

 * Specification as list of piecewise linear segments with associated intervals:

_⋃<sub>i=1,2,3</sub>\[B<sub>i-1</sub>,B<sub>i</sub>\[ : CBP<sub>i-1</sub>+COST<sub>i</sub>·\(x-B<sub>i-1</sub>\)_ 

```
TotalCost:= pwlin(union(i in 1..3) [pws(B(i-1), CBP(i-1)+COST(i)*(x-B(i-1)))])
```


```
totalcost = xp.pwl({(B[i-1],B[i]): COST[i-1]+COST[i]*(x[i]-B[i-1])) for i in range(1,3)})
```


 * Specification as list of points:

_⋃<sub>i=0,1,2,3</sub>\[B<sub>i</sub>,CBP<sub>i</sub>]_ 

```
TotalCost:= pwlin(x, union(i in 0..3) [B(i), CBP(i)])
```


In Python, it is possible to specify piecewise linear functions as a list of points using the `problem.addpwlcons` method. The example assumes that `B` and `CBP` are array \(lists\) containing the x-values and y-values of the breakpoints, respectively.

```
prob.addpwlcons([x], [totalcost], [0], B, CBP)
```


```
Variable x = prob.addVariable();
Variable fx = prob.addVariable();
int npieces = 3;
std::vector<double> B = ...;
std::vector<double> COST = ...;
std::vector<double> breakX = {0, B[0], B[1], B[2]};
std::vector<double> breakY = {0};
for (int i = 1; i <= npieces; i++)  breakY[i] = breakY[i-1] + COST[i-1]*(B[i] - B[i-1]);
prob.addConstraint(fx.pwlOf(x, breakX, breakY));

```



### Non-linear functions


Can model non-linear functions in the same way as incremental pricebreaks
 * approximate the non-linear function with a piecewise linear function
 * use an SOS2 to model the piecewise linear function
 * alternatively, formulate as piecewise linear expression by specifying a list of points
 * note that certain nonlinear functions \(  _e.g._  absolute value, minimum value, maximum value\) are recognized by MIP solvers and can be used directly in the formulation of MIP models, see Section  _General constraints_


#### Non-linear function in a single variable


![Intro/soslin2](Graphic/Intro/soslin2.png)


 * x-coordinates of the points: _R<sub>1</sub>_ , ..., _R<sub>4</sub>_ 
   *  y-coordinates _FR<sub>1</sub>_ , ..., _FR<sub>4</sub>_ . So point 1 is _\(R<sub>1</sub>,FR<sub>1</sub>\)_  _etc._ 

 * Let weights \(decision variables\) associated with point _i_  be _w<sub>i</sub>_  \(i=1,...,4\)

 * Form convex combinations of the points using weights _w<sub>i</sub>_  to get a combination point \(x,y\):

| &nbsp; | 
---------- | 
_x = ∑<sub>i</sub>w<sub>i</sub>·R<sub>i</sub>_ | 
_y = ∑<sub>i</sub>w<sub>i</sub>·FR<sub>i</sub>_ | 
_∑<sub>i</sub>w<sub>i</sub>= 1_ | 
 where the variables _w<sub>i</sub>_  form an SOS2 set with ordering coefficients defined by values _R<sub>i</sub>_ .

**Mosel implementation (SOS-2):** 

```
 declarations
  I=1..4
  x,y: mpvar
  w: array(I) of mpvar
  R,FR: array(I) of real
 end-declarations

! ...assign values to arrays R and FR...

! Define the SOS-2 with "reference row" coefficients from R
 Defx:= sum(i in I) R(i)*w(i) is_sos2
 sum(i in I) w(i) = 1

! The variable and the corresponding function value we want to approximate
 x = Defx
 y = sum(i in I) FR(i)*w(i)
```


**Mosel implementation (piecewise linear):** 

```
 uses "mmxnlp"
 declarations
  I=1..4
  x,y: mpvar
  R,FR: array(I) of real
 end-declarations

! ...assign values to arrays R and FR...

! Define the piecewise linear expression
 y = pwlin(x, sum(i in I) [R(i), FR(i)])

! Only consider the x-values interval defined by the breakpoints
 setrange(x, R(1), R(4))
```


**Python implementation (SOS-2):** 

```
import xpress as xp

I = range(4)
R = [1, 2.5, 4.5, 6.5]
FR = [1.5, 6, 3.5, 2.5]

p = xp.problem()

# Create the decision variables
x = p.addVariable(lb=R[0],ub=R[3],name="x") # x-values interval defined by the breakpoints
y = p.addVariable(name="y")
w = [p.addVariable(name="w{ 0} ".format(i)) for i in I]

# Define the SOS-2 with weights R
p.addSOS(w, R, name="Defx", type=2)

# Weights must sum up to 1
p.addConstraint(xp.Sum(w[i] for i in I) == 1.0)

# The variable and the corresponding function value we want to approximate
p.addConstraint(x == xp.Sum(R[i]*w[i] for i in I))
p.addConstraint(y == xp.Sum(FR[i]*w[i] for i in I))
...
```


**C++ implementation (SOS-2):** 

```
# include <iostream>
# include <xpress.hpp>
using namespace xpress;
using namespace xpress::objects;
using xpress::objects::utils::sum;
using namespace std;

static std::vector<int> I = {0, 1, 2, 3};

int main()
{
  XpressProblem prob;
  std::vector<double> R = {1, 2.5, 4.5, 6.5};
  std::vector<double> FR = {1.5, 6, 3.5, 2.5};

  // Create the decision variables
  auto x = prob.addVariable(R[0], R[3], ColumnType::Continuous, "x");
                            // x-values interval defined by the breakpoints
  auto y = prob.addVariable("y");
  auto w = prob.addVariables(I.size()).withName("w_% d").toArray();

  // Define the SOS-2 with weights R
  prob.addConstraint(SOS::sos(SetType::SOS2, w, R, "Defx"));

  // Weights must sum up to 1
  prob.addConstraint(sum(I, [&](auto i) { return w[i];}) == 1.0);

  // The variable and the corresponding function value we want to approximate
  prob.addConstraint(x == sum(I, [&](auto i) { return R[i]*w[i];}));
  prob.addConstraint(y == sum(I, [&](auto i) { return FR[i]*w[i];}));
...
```


#### Non-linear function in two variables


Interpolation of a function _f_  in two variables: approximate _f_  at a point _P_  by the corners C of the enclosing square of a rectangular grid \(NB: the representation of P=\(x,y\) by the four points C obviously means a fair amount of degeneracy\).

![Intro/sosquad2](Graphic/Intro/sosquad2.png)


 * x-coordinates of grid points: _X<sub>1</sub>_ , ..., _X<sub>n</sub>_ 
   *  y-coordinates of grid points: _Y<sub>1</sub>_ , ..., _Y<sub>m</sub>_ . So grid points are _\(X<sub>i</sub>,Y<sub>j</sub>\)_ .

 * Function evaluation at grid points: _FXY<sub>11</sub>_ , ..., _FXY<sub>nm</sub>_ 

 * Define weights \(decision variables\) associated with x and y coordinates, _wx<sub>i</sub>_  respectively _wy<sub>j</sub>_ , and for each grid point _(X(i),Y(j))_  define a variable _wxy<sub>ij</sub>_ 

 * Form convex combinations of the points using the weights to get a combination point \(x,y\) and the corresponding function approximation:

| &nbsp; | 
---------- | 
_x = ∑<sub>i</sub>wx<sub>i</sub>·X<sub>i</sub>_ | 
_y = ∑<sub>j</sub>wy<sub>j</sub>·Y<sub>j</sub>_ | 
_f = ∑<sub>ij</sub>wxy<sub>ij</sub>·FXY<sub>ij</sub>_ | 
_∀i=1,...,n: ∑<sub>j</sub>wxy<sub>ij</sub>= wx<sub>i</sub>_ | 
_∀j=1,...,m: ∑<sub>i</sub>wxy<sub>ij</sub>= wy<sub>j</sub>_ | 
_∑<sub>i</sub>wx<sub>i</sub>= 1_ | 
_∑<sub>j</sub>wy<sub>j</sub>= 1_ | 
 where the variables _wx<sub>i</sub>_  form an SOS2 set with ordering coefficients defined by values _X<sub>i</sub>_ , and the variables _wy<sub>j</sub>_  are a second SOS2 set with coordinate values _Y<sub>j</sub>_  as ordering coefficients.

```
 declarations
  RX,RY:range
  X: array(RX) of real          ! x coordinate values of grid points
  Y: array(RY) of real          ! y coordinate values of grid points
  FXY: array(RX,RY) of real     ! Function evaluation at grid points
 end-declarations

! ... initialize data 

 declarations
  wx: array(RX) of mpvar        ! Weight on x coordinate
  wy: array(RY) of mpvar        ! Weight on y coordinate
  wxy: array(RX,RY) of mpvar    ! Weight on (x,y) coordinates
  x,y,f: mpvar
 end-declarations

! Definition of SOS (assuming coordinate values <> 0)
 sum(i in RX) X(i)*wx(i) is_sos2
 sum(j in RY) Y(j)*wy(j) is_sos2

! Constraints 
 forall(i in RX) sum(j in RY) wxy(i,j) = wx(i)
 forall(j in RY) sum(i in RX) wxy(i,j) = wy(j)
 sum(i in RX) wx(i) = 1
 sum(j in RY) wy(j) = 1

! Then x, y and f can be calculated using 
 x = sum(i in RX)  X(i)*wx(i)
 y = sum(j in RY)  Y(j)*wy(j)
 f = sum(i in RX,j in RY) FXY(i,j)*wxy(i,j)

! f can take negative or positive values (unbounded variable)
 f is_free

```


```
import xpress as xp

NX = 10
NY = 10
RX = range(NX)
RY = range(NY)

X = [i+1 for i in RX]
Y = [j+1 for j in RY]
FXY = [[(i-4)*(j-4) for i in RX] for j in RY]

p = xp.problem()

# Create the decision variables
x = p.addVariable(name="x")
y = p.addVariable(name="y")
f = p.addVariable(lb=-xp.infinity, ub=xp.infinity, name="f")
wx = [p.addVariable(name="wx_{} ".format(i)) for i in RX]
wy = [p.addVariable(name="wy_{} ".format(i)) for i in RY]
wxy = [[p.addVariable(name="wxy_{} _{} ".format(i,j)) for i in RX] for j in RY]

# Define the SOS-2 for coordinate x 
p.addSOS(wx, X, name="sos_x", type=2)
# Define the SOS-2 for coordinate y 
p.addSOS(wy, Y, name="sos_y", type=2)

# Weights must sum up to 1 along the two coordinates 
p.addConstraint(xp.Sum(wx[i] for i in RX) == 1.0)
p.addConstraint(xp.Sum(wy[j] for j in RY) == 1.0)

# wx, wy and wxy must be consistent
p.addConstraint(wx[i] == xp.Sum(wxy[i][j] for j in  RY) for i in RX)
p.addConstraint(wy[j] == xp.Sum(wxy[i][j] for i in  RX) for j in RY)

# The coordinates and the corresponding function value we want to approximate
p.addConstraint(x == xp.Sum(X[i]*wx[i] for i in RX))
p.addConstraint(y == xp.Sum(Y[j]*wy[j] for j in RY))
p.addConstraint(f == xp.Sum(FXY[i][j]*wxy[i][j] for i in RX for j in RY))
```


```
# include <iostream>
# include <xpress.hpp>
using namespace xpress;
using namespace xpress::objects;
using xpress::objects::utils::sum;
using namespace std;

int main()
{
  XpressProblem prob;

  // Problem data
  static const int NX = 10;
  static const int NY = 10;

  std::array<double,NX> X;
  for (int i = 0; i < NX; i++)  X[i] = (double)(i+1);
  std::array<double,NY> Y;
  for (int j = 0; j < NY; j++)  Y[j] = (double)(j+1);
  std::array<std::array<double,NY>, NX> FXY;
  for (int i = 0; i < NX; i++) {
    for (int j = 0; j < NY; j++) {
      FXY[i][j] = (double)(i-4)*(j-4);
    }
  }

  // Create the decision variables
  auto x = prob.addVariable("x");
  auto y = prob.addVariable("y");
  auto f =
    prob.addVariable(XPRS_MINUSINFINITY, XPRS_PLUSINFINITY, ColumnType::Continuous, "f");
  auto wx = prob.addVariables(NX).withName("wx_% d").toArray();
  auto wy = prob.addVariables(NY).withName("wy_% d").toArray();
  auto wxy = prob.addVariables(NX, NY).withName("wxy_% d_% d").toArray();

  // Define the SOS-2 for coordinate x
  prob.addConstraint(SOS::sos(SetType::SOS2, wx, X, "sos_x"));
  // Define the SOS-2 for coordinate y
  prob.addConstraint(SOS::sos(SetType::SOS2, wy, Y, "sos_y"));

  // Weights must sum up to 1 along the two coordinates
  prob.addConstraint(sum(NX, [&](auto i) { return wx[i]; }) == 1.0);
  prob.addConstraint(sum(NY, [&](auto j) { return wy[j]; }) == 1.0);

  // wx, wy and wxy must be consistent
  prob.addConstraints(NX, [&](auto i) {
    return wx[i] == sum(NY, [&](auto j) { return wxy[i][j]; });
  });
  prob.addConstraints(NY, [&](auto j) {
    return wy[j] == sum(NX, [&](auto i) { return wxy[i][j]; });
  });

  // The coordinates and the corresponding function value we want to approximate
  prob.addConstraint(x == sum(NX, [&](auto i) { return X[i]*wx[i]; }));
  prob.addConstraint(y == sum(NY, [&](auto j) { return Y[j]*wy[j]; }));
  prob.addConstraint(f == sum(NX, [&](auto i) {
    return sum(NY, [&](auto j) { return FXY[i][j]*wxy[i][j]; });
  }));
...
```


### Minimum activity level


Continuous production rate _make_ . May be 0 \(the plant is not operating\) or between allowed production limits _MAKEMIN_  and _MAKEMAX_ 

 * Can impose using a _semi-continuous variable_: may be zero, or any value between the intermediate bound and the upper bound
 * Semi-continuous variables are slightly more efficient than the alternative binary variable formulation that we saw before. But if you incur fixed costs on any non-zero activity, you must use the binary variable formulation \(see Section  _Minimum activity level_\).

```
make is_semcont MAKEMIN
make <= MAKEMAX
```


```
make = p.addVariable(vartype=xp.semicontinuous, threshold=MAKEMIN, ub=MAKEMAX, name="make")

```


```
auto make = prob.addVariable(0, MAKEMAX, ColumnType::SemiContinuous, "make");
make.setLimit(MAKEMIN);
```


### Partial integer variables


 * In general, try to keep the upper bound on integer variables as small as possible. This reduces the number of possible integer values, and so reduces the time to solve the problem.
 * Sometimes this is not possible– a variable has a large upper bound and must take integer values.
   *  ⇒Try to use _partial integer variables_instead of integer variables with a very large upper bound: takes integer values for small values, where it is important to be precise, but takes real values for larger values, where it is OK to round the value afterwards.

 * For example, it may be important to clarify whether the value is 0, 1, 2, ..., 10, but above 10 it is OK to get a real value and round it.

```
x is_partint 10        ! x is integer valued from 0 to 10
x <= 20                ! x takes real values from 10 to 20
```


```
make = p.addVariable(vartype=xp.partiallyinteger, threshold=10, ub=20, name="make")

```


```
auto x = prob.addVariable(0, 20, ColumnType::PartialInteger, "x");   // x has upper bound 20
x.setLimit(10);                                          // x is integer valued from 0 to 10
```


### General constraints


Certain nonlinear constraint relations \(refered to as _general constraints_\) are recognized by MIP solvers and they are treated as MIP modeling constructs. These include

 * piecewise linear expressions \(see examples in Sections  _Price breaks_ and  _Non-linear functions_ above\)
 * absolute value, minimum value, maximum value of discrete or continuous decision variables
 * logical constraints: 'and' and 'or' over binary variables \(see Section  _Boolean variables and logical constraints_\)

The Mosel implementation of the numerical constraints `abs`, `fmin` and `fmax` makes it possible to use linear expressions as argument to these functions. Note that models using these general constraints need to load the _mmxnlp_ module in addition to _mmxprs_ although the problems will be solved by the Xpress MIP solver.

```
 uses "mmxnlp"

 public declarations
   R=1..3
   x: array(R) of mpvar
   y,z: mpvar
 end-declarations

 forall(i in R) x(i) <= 20
 abs(x(1)-2*x(2)) <= 10                     ! Absolute value constraint
 MinCtr:= fmin(union(i in R) [x(i)]) >= 5   ! Minimum value constraint
 y = fmax(x(3), 20, x(1)-z)                 ! Maximum value constraint

 maximize(sum(i in R) x(i))                 ! Solve as MIP problem
 if getprobstat=XPRS_OPT then               ! Solution reporting
   writeln("Solution: ", getobjval)
   forall(i in R) write("x", i, "=", x(i).sol, ", ")
   writeln("y=", y.sol, ", z=", z.sol)
   writeln("abs=", getsol(abs(x(1)-2*x(2))), ", Min of x(i)=", MinCtr.sol+5)
 else
   writeln("No solution")
 end-if
```


The Python implementation of the numerical constraints `xp.abs`, `xp.min` and `xp.max` makes it possible to use linear expressions as argument to these functions.

```
import xpress as xp

R = range(3)

p = xp.problem()

x = [p.addVariable(name="x_{} ".format(i)) for i in R]
y = p.addVariable()
z = p.addVariable()

p.addConstraint(x[i] <= 20 for i in R)
p.addConstraint(xp.abs(x[0] - 2*x[1]) <= 10)      # Absolute value constraint
p.addConstraint(xp.min(x) >= 5)                   # Minimum value constraint
p.addConstraint(y == xp.max(x[2], 20, x[0]-z))    # Maximum value constraint

p.setObjective(xp.Sum(x), sense=xp.maximize)

p.optimize()                                      # Solve as MIP problem

if p.attributes.solstatus in [SolStatus.FEASIBLE",SolStatus."OPTIMAL"]:
    print("Solution:", p.attributes.objval())
    for i in R:
        print(x[i].name,"=",p.getSolution(x[i]))
    print("y=", p.getSolution(y), ", z=", p.getSolution(z))
    print("abs=", p.getSolution(xp.abs(x[0]-2*x[1])), ", Min of x(i)=", min(p.getSolution(x)))
else:
    print("No solution")
```


The implementation of general constraints with the C++ API introduces auxiliary variables for the formulation of the constraints since `absOf` / `minOf` / `maxOf` are not defined for expressions, they expect decision variables as their arguments.

```
using namespace xpress;
using namespace xpress::objects;
using xpress::objects::utils::sum;
using namespace std;

int main()
{
  XpressProblem prob;

  // Create the decision variables
  auto x = prob.addVariables(3).withName("x_% d").withUB(20).toArray();
  auto y = prob.addVariable("y");
  auto z = prob.addVariable("z");

  // abs(x_0 - 2*x_1) < = 10
  auto diff1 = prob.addVariable("diff1");
  auto absOfDiff1 = prob.addVariable("absOfDiff1");
  prob.addConstraint(diff1 == x[0] - 2*x[1]);
  prob.addConstraint(absOfDiff1.absOf(diff1));
  absOfDiff1.setUB(10);

  // min(x_i) >= 5
  auto minOfX = prob.addVariable("minOfX");
  prob.addConstraint(minOfX.minOf(x));
  minOfX.setLB(5);

  // y = max(x_2, 20, x_0 - z)
  auto diff2 = prob.addVariable("diff2");
  prob.addConstraint(diff2 == x[0] - z);
  std::array<Variable,2> maxVarArgs = {x[2], diff2};
  prob.addConstraint(y.maxOf(maxVarArgs, 20));

  // Objective
  prob.setObjective(sum(x), ObjSense::Maximize);

  // Solve the problem
  prob.optimize();
...
```


## Section 4 Indicator constraints


 * Indicator constraints associate a binary variable _b_  with a linear or nonlinear constraint _C_ .
 * An indicator constraint models an implication:
   *  'if _b=1_ then _C_ ', in symbols: _b→C_ , or
   *  'if _b=0_ then _C_ ', in symbols: _not\(b\)→C_ 
   *  \(the constraint _C_ is active only if the condition is true\)

 * Indicator constraints can be used for the composition of logic expressions.

**Indicator constraints in Mosel:**  for the definition of indicator constraints \(function `indicator` of module _mmxprs_\) you need a binary variable \(type `mpvar`\) and a linear or nonlinear constraint \(type `linctr` or `nlctr`\). You also have to specify the type of the implication \(1 for _b→C_  and -1 for _not\(b\)→C_ \). The subroutine `indicator` returns a new constraint of type `logctr` \(the type `logctr` and the corresponding subroutines including `indicator` are documented in the chapter _mmxprs_ of the [Mosel Language Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/mosel_lang/dhtml/)\).

```
 uses "mmxprs"

 declarations
  R=1..2
  C: array(range) of linctr
  L: array(range) of logctr
  x, b: array(R) of mpvar
 end-declarations

 forall(i in R) b(i) is_binary   ! Variables for indicator constraints

 C(2):= x(2)<=5

! Define 2 indicator constraints
 L(1):= indicator(1, b(1), x(1)+x(2)>=12)    ! b(1)=1 ->  x(1)+x(2)> =12
 indicator(-1, b(2), C(2))                   ! b(2)=0 ->  x(2)< =5

 C(2):=0                         ! Delete auxiliary constraint definition
```


The module _mmxnlp_ must be used in place of _mmxprs_ if the indicator constraints are defined over nonlinear constraints:

```
 uses "mmxnlp"

 declarations
  R=1..2
  C: array(range) of nlctr
  L: array(range) of logctr
  x, b: array(R) of mpvar
 end-declarations

 forall(i in R) b(i) is_binary   ! Variables for indicator constraints

 C(2):= sin(x(2))>=0.5

! Define 2 indicator constraints
 L(1):= indicator(1, b(1), x(1)*x(2)>=12)    ! b(1)=1 ->  x(1)*x(2)=12
 indicator(-1, b(2), C(2))                   ! b(2)=0 ->  sin(x(2))> =0.5

 C(2):=0                         ! Delete auxiliary constraint definition
```


**Indicator constraints in the Python API:**  indicator constraints are defined via the method `addIndicator` of `xp.problem`. All arguments can be single indicator constraints or lists, tuples, or NumPy arrays created as indicator constraints. An indicator constraint is a tuple of two elements, the first being a condition \(i.e. a binary variable being 0 or 1\) and the second being the constraint.

```
import xpress as xp

N = 2

p = xp.problem()

# Create the decision variables
x = [p.addVariable(name="x_{} ".format(i),vartype=xp.continuous) for i in range(N)]
b = [p.addVariable(name="b_{} ".format(i),vartype=xp.binary) for i in range(N)]

# b[0] = 1 ->  x[0]+x[1] > = 12
p.addIndicator(b[0] == 1, x[0] + x[1] >= 12)
# b[1] = 0 ->  x[1] < = 5
p.addIndicator(b[1] == 0, x[1] <= 5)

```


**Indicator constraints in the C++ API:**  indicator constraints are defined via the method `addConstraint` of `XpressProblem`.The type of the implication is specified by using either `ifThen` \(for _b→C_ \) or `ifNotThen` \(for _not\(b\)→C_ \).

```
  XpressProblem prob;

  // Create the decision variables
  auto x = prob.addVariables(N).withType(ColumnType::Continuous).withName("x_% d").toArray();
  auto b = prob.addVariables(N).withType(ColumnType::Binary).withName("b_% d").toArray();

  // Define 2 indicator constraints:
  // b[0] = 1 ->  x[0]+x[1] >= 12
  prob.addConstraint(b[0].ifThen(x[0] + x[1] >= 12));
  // b[1] = 0 ->  x[1] < = 5
  prob.addConstraint(b[1].ifNotThen(x[1] <= 5));
```


### Inverse implication


_b←a·x≥c_ 

 * Model as

_not\(b\)→a·x≤c-m_ 
 where _m_  is a sufficiently small value \(slightly larger than the feasibility tolerance\)

_b←a·x≤c_ 

 * Model as

_not\(b\)→a·x≥c+m_ 


_b←a·x = c_ 

 * Model as

| &nbsp; | 
---------- | 
_not\(b\)→b<sub>1</sub>+ b<sub>2</sub>= 1_ | 
_b<sub>1</sub>→a·x≥c+m_ | 
_b<sub>2</sub>→a·x≤c-m_ | 


### Logical constructs


Indicator constraints can be used for the formulation of logical constructs composed of linear or nonlinear equality or inequality constraints and the logic functions 'implies', 'not', 'and', 'or', or 'xor' by applying a set of _recipes_.

In the following we shall be using the following definitions:

 * _C \(constraint\)_: a linear or nonlinear equality or inequality constraint
 * _IC \(indicator constraint\)_: can be either like _y→C_  or _not\(y\)→C_ 
 * _LE \(logical expression\)_: either a C or one of the following functions \(of C's or LE's\): AND, OR, XOR, NOT, IMPLIES, such as `IMPLIES(x(1)>=10, AND(x(1)+x(2)>=12, NOT(x(2)< =5)))`

To model logical constructs we associate a binary indicator variable _y(e)_  to each LE _e_ , representing its truth value. For each pair _(y(e), e)_ , we may need to enforce either that _y\(e\)→e_  or _y\(e\)←e_  or both, that is, _y\(e\)↔e_ .

We will write

 * _is(e)_  \(for **I**  mplie **S** \) to refer to the implication _y\(e\)→e_ , and
 * _id(e)_  \(for **I**  mplie **D** \) to refer to the implication _y\(e\)←e_  which is equivalent to _not\(y\(e\)\)→not\(e\)_ .

To model a logical construct, we proceed recursively from the _outer LE_. Let _e_  be the outer LE, then we can model it as follows:


add constraint _y(e) = 1_ 

model _is(e)_ where the recipe to "model _is(e)_ " is given below.

#### Rules to model logical constructs


The following set of rules can be applied to model each type of LE \(with _y_  being its associated indicator variable\).

 * C \(  _e.g._  _a·x≥b_ \)
     * _is_ direction

model it in the obvious way as an indicator constraint \(  _e.g._  _y→a·x≥b_ \)

     * _id_ direction

model it as an inverse implication \(  _e.g._  _not\(y\)→a·x≤b-m_ \)
 Here _m_  is a parameter whose default value should be somewhat larger than the feasibility tolerance. When the involved constraints are all integer, _m_  could be set equal to 1.

 * AND _\(e<sub>1</sub>, e<sub>2</sub>,...,e<sub>n</sub>\)_ 
     * _is_ direction

add _n_  constraints: _y→y\(e<sub>i</sub>\) = 1∀i_ 
   *  model _is\(e<sub>i</sub>\)∀i_ 

     * _id_ direction

add constraint: _not\(y\)→ ∑<sub>i=1</sub><sup>n</sup>y\(e<sub>i</sub>\)≤n- 1_ 
   *  model _id\(e<sub>i</sub>\)∀i_ 


 * OR _\(e<sub>1</sub>, e<sub>2</sub>,...,e<sub>n</sub>\)_ 
     * _is_ direction

add constraint: _y→ ∑<sub>i=1</sub><sup>n</sup>y\(e<sub>i</sub>\)≥1_ 
   *  model _is\(e<sub>i</sub>\)∀i_ 

     * _id_ direction

add constraint: _not\(y\)→ ∑<sub>i=1</sub><sup>n</sup>y\(e<sub>i</sub>\) = 0_ 
   *  model _id\(e<sub>i</sub>\)∀i_ 


 * XOR _\(e<sub>1</sub>, e<sub>2</sub>,...,e<sub>n</sub>\)_ 
     * _is_ direction

add constraint: _y→ ∑<sub>i=1</sub><sup>n</sup>y\(e<sub>i</sub>\) = 1_ 
   *  model _is\(e<sub>i</sub>\)_ and _id\(e<sub>i</sub>\)∀i_ 

     * _id_ direction

add two auxiliary variables _y'_  and _y"_  and the constraints
   *   _y'→ ∑<sub>i=1</sub><sup>n</sup>y\(e<sub>i</sub>\) = 0_ 
   *   _y"→ ∑<sub>i=1</sub><sup>n</sup>y\(e<sub>i</sub>\)≥2_ 
   *   _not\(y\)→y' + y" = 1_ 
   *  model _is\(e<sub>i</sub>\)_ and _id\(e<sub>i</sub>\)∀i_ 


 * NOT _(e)_ 
     * _is_ direction

add constraint: _y + y(e) = 1_ 
   *  model _id(e)_ 

     * _id_ direction

add constraint: _y + y(e) = 1_ 
   *  model _is(e)_ 


 * IMPLIES _\(e<sub>1</sub>, e<sub>2</sub>\)_  \(same as: _e<sub>1</sub>→e<sub>2</sub>_ \)
     * _is_ direction

add constraint: _y→y\(e<sub>1</sub>\)≤y\(e<sub>2</sub>\)_ 
   *  model _id\(e<sub>1</sub>\)_ and _is\(e<sub>2</sub>\)_ 

     * _id_ direction

add constraints:
   *   _not\(y\)→y\(e<sub>1</sub>\) = 1_ 
   *   _not\(y\)→y\(e<sub>2</sub>\) = 0_ 
   *  model _is\(e<sub>1</sub>\)_ and _id\(e<sub>2</sub>\)_ 



#### Example


By applying the reformulation rules from the previous section to an expression `LE` that is defined as `LE = IMPLIES(x(1)>=10, AND(x(1)+x(2)>=12, NOT(x(2)< =5)))` we obtain the following:

```
start:
  associate y to the outermost expression "LE=IMPLIES(...)"
  add constraint: y = 1
  model is(LE)

model is(LE) yields:
  associate y1 to "e1=x(1)>=10" and y2 to "e2=AND(...)"
  add constraint: y -> y1 = y2
  model id(e1) and is(e2)

model id(e1) yields:
  add constraint: not(y1) -> x(1)=10-m

model is(e2) yields:
  associate y3 to "e3=x(1)+x(2)>=12" and y4 to "e4=NOT(x(2)=5)"
  add constraints:
  y2 -> y3=1
  y2 -> y4=1
  model is(e3) and is(e4)

model is(e3) yields:
  add constraint: y3 -> x(1)+x(2)>=12

model is(e4) yields:
  associate y5 with "e5=x(2)=5"
  add constraint: y4 + y5 = 1
  model id(e5)

model id(e5) yields:
  add constraint: not(y5) -> x(2)>=5+m

```


In summary, the resulting model formulation is as follows \(where the outer fixed indicator constraint can be removed\):

```
 binaries y, y1, y2, y3, y4, y5
 y = 1
 y -> y1 = y2
 not(y1) -> x(1)=10-m
 y2 -> y3=1
 y2 -> y4=1
 y3 -> x(1)+x(2)>=12
 y4 + y5 = 1
 not(y5) -> x(2)>=5+m

```


## Section 5 Boolean variables and logical constraints


The Mosel module _mmxprs_ defines the entity type `boolvar` for representing a _pseudo boolean decision variable_. This type supports the operators `and`, `or` and `not` for building logical expressions and can be combined with ordinary Boolean variables \(type `boolean`\). A logical constraint is specified either by associating a pseudo boolean variable to a logical expression or by forcing the truth value \(i.e. true or false\) of an expression as shown in the code example below. When a logical expression is used on its own as a statement it is implicitly turned into a constraint \(forced to `true`\) and added to the constraint store.

```
 uses "mmxprs"

 public declarations
   R=1..5
   bv: array(R) of boolvar
   LC1, LC2: logctr
 end-declarations

! Simple clause, same as:  bv(1) and not bv(5) = true
 bv(1) and not bv(5)

! Association of clauses
 bv(3)=(not bv(4))

! The opposite of 'bv(1) or bv(3)' must be false
 (not (bv(1) or bv(3)))=false

! Defining a logic expression (not recorded in the constraint store)
 LC1:= and(i in 1..3) bv(i) or and(i in 4..5) not bv(i)

! Turn expression into a constraint
 LC1:= LC1=true

! A named logic expression (this defines a constraint)
 LC2:= (or(i in 1..3) not bv(i)) = false

! Solve as feasibility (SAT) problem
 maximise(0)
 if getprobstat=XPRS_OPT then
   writeln("Problem is feasible")
 else
   writeln("Problem is unsatisfiable")
 end-if
```


### Correspondence with MIP


Each `boolvar` is represented in the MIP problem by two binary variables \( `mpvar`\): one for the value itself and second one for its negation. These decision variables can be accessed from the model using the function `getvar` such that they can be used in linear constraints. The solution value of a `boolvar` is of type `boolean` and can be obtained using `getsol`.

```
! Retrieve associated binary variables for formulation of an objective function
 Obj:=sum(i in R) bv(i).var

! Solve as optimization problem
 maximise(Obj)
 if getprobstat=XPRS_OPT then
   writeln("Solution: ", getobjval)
   forall(i in R) writeln(i, ": ", bv(i).sol)
 end-if
```


The problem matrix can be output from the solver to inspect the resulting formulation: note that the logic relations are represented via _general constraints_ by the MIP solver.

```
 loadprob(Obj)
 writeprob("testout.lp","l")
```

