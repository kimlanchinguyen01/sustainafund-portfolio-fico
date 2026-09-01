# FICO® Xpress Optimization

# MIP Solution Pool
## Reference manual


#### Release 47.01


#### __Last update 20 August, 2026__



(C) 1983-2026 Fair Isaac Corporation. All rights reserved. 
This documentation is the property of Fair Isaac Corporation ("FICO"). Receipt or possession of this documentation does not convey rights to disclose, reproduce, make derivative works, use, or allow others to use it except solely for internal evaluation purposes to determine whether to purchase a license to the software described in this documentation, or as otherwise set forth in a written software license agreement between you and FICO (or a FICO affiliate).  Use of this documentation and the software described in it must conform strictly to the foregoing permitted uses, and no other use is permitted.

The information in this documentation is subject to change without notice. If you find any problems in this documentation, please report them to us in writing. Neither FICO nor its affiliates warrant that this documentation is error-free, nor are there any other warranties with respect to the documentation except as may be provided in the license agreement. FICO and its affiliates specifically disclaim any warranties, express or implied, including, but not limited to, non-infringement, merchantability and fitness for a particular purpose. Portions of this documentation and the software described in it may contain copyright of various authors and may be licensed under certain third-party licenses identified in the software, documentation, or both.

In no event shall FICO or its affiliates be liable to any person for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this documentation or the software described in it, even if FICO or its affiliates have been advised of the possibility of such damage. FICO and its affiliates have no obligation to provide maintenance, support, updates, enhancements, or modifications except as required to licensed users under a license agreement.

FICO is a registered trademark of Fair Isaac Corporation in the United States and may be a registered trademark of Fair Isaac Corporation in other countries. Other product and company names herein may be trademarks of their respective owners.

Patent(s): [www.fico.com/en/patents](https://www.fico.com/en/patents})

Xpress-Optimizer 47.01 (FICO® Xpress 9.9)

Deliverable Version: A

Last Revised: 20 August, 2026


## Part A MIP Solution Pool


### Chapter 1 Introduction


#### Section 1.1 Overview


The MIP solution pool \( `XPRSmipsolpool`\) stores the column solution values for multiple solutions. No slack or dual information is stored with the solutions. The solutions will usually be for MIP problems although the pool will store any arbitrary length vector of double values. Solutions can be read into the MIP solution pool by the user via the file reader routine `XPRS_msp_readslxsol` or from memory via the `XPRS_msp_loadsol` routine. Solutions can also be captured automatically from problems \( `XPRSprob`\) as they are found during a search.

Since the `XPRSprob` problems only store the best MIP solution the MIP solution pool is useful when the user is interested in more than one MIP solution for a problem. This can happen when there are constraints or costs not reflected in the problem that the user wants to use to select a solution from a set that have been found by the FICO Xpress Optimizer.

Once a MIP solution pool contains some solutions the user can query for the solution values and also for more abstract attributes such as the objective value of the solution with respect to a given problem. Apart from querying information for a single solution the user has various options for managing the set of stored solutions. The user can query for lists of stored solutions. They may delete solutions from the pool and output solutions to file. Also, a set of policies are available to the user for automatically handling the exclusion of solutions that are duplicated.

The following sections discuss the MIP solution pool functionality and provide some hints on usage.

#### Section 1.2 Data Model


The UML diagram in Figure  __ outlines the relationships the `XPRSmipsolpool` has with some other data entities.



![ mspuml.png](Graphic/mspuml.png)

    
  **Figure 1.1:**  


Starting from the bottom right the diagram shows that the `XPRSmipsolpool` contains 0 or more solutions. Solutions are loaded into the MIP solution pool as a dense vector of double values. Solution vectors of varying length can be stored in the same MIP solution pool so each solution stores the number of columns `nCols` for the solution. When solutions are loaded they are stored with a name and an ID number. The names of the stored solutions are maintained so they are unique among the current set of stored solutions. The IDs are generated using a counter starting from 1 and are therefore unique over all solutions ever to be stored in the MIP solution pool. Note that no mapping of column names to column index values is stored with the solutions. Therefore, the solutions are stored as plain vectors of implicitly indexed values. Note that although the array of solution values `Vals` is represented in the Solution object in the diagram as a dense array of doubles the solutions are stored in a compact form.

Moving to the top right the diagram shows that the `XPRSmipsolpool` references 0 or more `XPRSprob` problems and that an `XPRSprob` references at most 1 `XPRSmipsolpool`. This relationship is managed through the "attaching" of problems to the MIP solution pool, which we discuss in section "Attaching problems". Note that by attaching problems it is possible, for example, to automatically capture MIP solutions from the problems as they are found by the solver.

Finally, moving to the top left the diagram shows the object defining the MIP entities for a problem. Clearly the `XPRSprob` has one of these \(even if it is empty in the case of an LP problem\). The `XPRSmipsolpool` may capture one of these from an attached problem and uses it only to detect duplicate solutions. We discuss duplicate solutions in section "Duplicate solutions".

Once the MIP solution pool contains some solutions the user can administer the stored solutions using the following functionality:-


 * Solution names can be changed using the routine `XPRS_msp_setsolname`.
 * Solutions can be deleted from the MIP solution pool by calling `XPRS_msp_delsol` with the ID of the solution to delete.
 * A mapping between solution name and ID is provided with the routines `XPRS_msp_findsolbyname` and `XPRS_msp_getsolname`.
 * Attributes of the solutions can be accessed using routines `XPRS_msp_getsol`, `XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribsol`, `XPRS_msp_getintattribsol`, `XPRS_msp_getdblattribprob`, `XPRS_msp_getintattribprob`, `XPRS_msp_getdblattribprobextreme` and `XPRS_msp_getintattribprobextreme`.
 * Lists of solution IDs can be generated based on attributes of the solutions with respect to a given problem using the routine `XPRS_msp_getsollist`.


#### Section 1.3 Solution input


Solutions can be input into the MIP solution pool from file, from memory and they can be captured automatically by the MIP solution pool directly from `XPRSprob` problems. The following two sections discuss this functionality.

##### Attaching problems


Of the more useful features of the MIP solution pool type has the ability to 'attach' `XPRSprob` problems to a MIP solution pool with a call to `XPRS_msp_probattach`. Once a problem is attached to a MIP solution pool they interact automatically with useful functions. For example, when an attached problem finds a solution it automatically stores the solution into the MIP solution pool.

As illustrated in the UML data model diagram a MIP solution pool can have one or more attached problems although a problem can only be attached to at most one MIP solution pool. The attached problems do not need to be copies of each other and they do not need to have the same number of columns.

The MIP solution pool ensures each solution is automatically loaded to all attached problems with the same number of columns as the solution. Solutions are loaded to a problem when the solver is running the problem with [`XPRSlpoptimize`](../../HTML/optimizer?scroll=XPRSlpoptimize) / [`XPRSmipoptimize`](../../HTML/optimizer?scroll=XPRSmipoptimize). The solver can then use the loaded solutions to update the best solution and/or as a seed for heuristic searches.

Solutions loaded directly from attached problems \(compared with solutions loaded by the user from file or from memory\) are marked with the `MSP_SOL_ISUSERSOLUTION` solution attribute set to 0.

Note that problems are automatically detached from their MIP solution pool when they are destroyed \(with a call to [`XPRSdestroyprob`](../../HTML/optimizer?scroll=XPRSdestroyprob). A MIP solution pool automatically detaches all problems when it is destroyed \(with a call to `XPRS_msp_destroy`\).

Example:-

```
#include <stdio.h>
#include <stdio.h>
#include "xprs.h"

int main(int argc, char **argv) {
  XPRSprob prob;
  XPRSmipsolpool msp;
  int i, nSols, nCols, iSolutionId, iSolutionIdStatus;
  double dObj, dSol;
  const char *sProblem = argv[1];

  XPRSinit(NULL);

  XPRScreateprob(&prob);

  XPRSreadprob(prob, sProblem, "");

  XPRS_msp_create(&msp);

  XPRS_msp_probattach(msp, prob);

  XPRSmaxim(prob, "g");

  XPRS_msp_getintattrib(msp, XPRS_MSP_SOLUTIONS, &nSols);

  if(nSols) {

    XPRS_msp_getdblattribprobextreme(msp, prob, 0, &iSolutionId, XPRS_MSP_SOLPRB_OBJ, 
                                     &dObj);

    printf("Optimal Solution ID: %i\n", iSolutionId);
    printf("Optimal Objective  : %12.5f\n", dObj);

    XPRS_msp_getintattribsol(msp, iSolutionId, &iSolutionIdStatus, XPRS_MSP_SOL_COLS, 
                             &nCols);

    for(i = 0; i < nCols; i++) {
      XPRS_msp_getsol(msp, iSolutionId, &iSolutionIdStatus, &dSol, i, i, NULL);
      printf("%3i = %12.5f\n", i, dSol);
    }

  }

  XPRSdestroyprob(prob);

  XPRS_msp_destroy(msp);

  XPRSfree();
}

```


##### Input from file and from memory


Solutions can be input into the MIP solution pool via the file reader routine `XPRS_msp_readslxsol` or from memory via the `XPRS_msp_loadsol` routine. When solutions are loaded in these ways the user is returned the ID\(s\) of the stored solutions. When solutions are input from memory via `XPRS_msp_loadsol` only one solution is stored per call and the user is returned the ID of the stored solution each time. When solutions are input from file via `XPRS_msp_readslxsol` the user is returned the first and last ID of the set of solutions that were successfully stored.

Note that solutions are not stored with a mapping of column name to solution index. Therefore, once a solution is stored the user is responsible for mapping the solution values against any column names. The indexing of the solution values is determined when the solution is loaded. When loading solutions from memory with a call to `XPRS_msp_loadsol`, the solution values are indexed by their position in the dense array. Similarly, solutions loaded automatically to the MIP solution pool from a problem are also indexed in this way.

When loading solutions from .slx file using `XPRS_msp_readslxsol` the file format has column name/solution value pairs. Solution values may be mapped to solution index using a runtime supplied name map object of type `XPRSnamelist` passed in the call to `XPRS_msp_readslxsol`. The `XPRSnamelist` object is typically obtained from an `XPRSprob` by calling [`XPRSgetnamelistobject`](../../HTML/optimizer?scroll=XPRSgetnamelistobject) on the problem to get the column name list \(type 2\). If the `XPRSnamelist` object is passed as NULL the solution values are indexed by the order they are encountered in the file.

Solutions loaded by the user from file or from memory \(compared with solutions loaded directly from attached problems\) are marked with the `MSP_SOL_ISUSERSOLUTION` solution attribute set to 1.

#### Section 1.4 Solution querying


Generally, users will want to query stored solutions for their solution values. The values for solutions can be written to file or passed to the user in memory using the `XPRS_msp_writeslxsol` and `XPRS_msp_getsol` calls, respectively.

The user may be interested in abstract attributes of the solutions and the MIP solution pool itself. For example, the user may want to know the number of solutions stored in the solution pool or the number of non-zero values in a solution. They may also be interested in the objective value of a solution with respect to a given problem or they may want to know how many feasible solutions the MIP solution pool contains for a given problem. The user may perhaps also want to get the list of solutions that are feasible for a given problem. The following sections discuss the various classes of these attributes and how they are accessed.

##### Solution value output to file and memory


The solution values are accessed in two ways. They are written to file using the routine `XPRS_msp_writeslxsol` and they are retrieved in memory using the routine `XPRS_msp_getsol`.

The routine `XPRS_msp_writeslxsol` allows one or more solution to be written to file. If `XPRS_msp_writeslxsol` is passed with a problem \( `XPRSprob`\) pointer then the user can specify that \(i\) a particular solution is written out, \(ii\) the best solution for the problem is written out or \(iii\) all feasible solutions for the problem are written out. If no problem pointer is provided then the user can specify that \(i\) a particular solution is written out or \(ii\) all solutions are written out. The output .slx file has a format based on the MPS format. Each solution has a section in the `.slx` file starting with the string ' `NAME` ' followed on the same line by the name of the solution. The records of each section each correspond to the solution value at the associated position in the solution array. If a problem is provided in the call then the column name is taken from the given problem for the index position and is written out followed by the solution value; otherwise column names are generated automatically based on a one-based indexing of the solution values.

The routine `XPRS_msp_getsol` provides in memory access to the values of a particular solution. The routine can return all solution values or solution values over a range of indices.

##### Attributes


A MIP solution pool and its set of stored solutions have various attributes the user can query. For example, the user can query the number of solutions stored in the solution pool or the number of non-zeros in a solution. They may also, for example, query the objective value of a solution with respect to a given problem or how many feasible solutions the MIP solution pool contains for a given problem.

There are four classes of attributes:-


 * MIP solution pool attributes.
 * Solution attributes.
 * Solution and problem pair attributes.
 * Problem attributes.


Each class relates to a different set of entities in the data model of the MIP solution pool and has a particular associated routine for accessing the attribute values. The following sections discuss the attributes.

##### MIP solution pool attributes


These are attributes relating to the MIP solution pool as a whole. For example, the number of solutions stored in the solution pool. These attributes are accessed using routines `XPRS_msp_getintattrib` and `XPRS_msp_getdblattrib`.

##### Solution attributes


These are attributes relating to a particular solution. For example, the number of non-zero values in a solution. These attributes are accessed using routines `XPRS_msp_getintattribsol` and `XPRS_msp_getdblattribsol`.

##### Problem attributes


These are attributes relating to the set of solutions with respect to a particular problem. For example, how many solutions the MIP solution pool contains that have the same number of columns as a given problem. These attributes are accessed using routines `XPRS_msp_getintattribprob` and `XPRS_msp_getdblattribprob`.

##### Solution and problem pair attributes


These are attributes relating to a solution and problem pair. For example, the objective value of a solution with respect to a given problem. These attributes are accessed using routines `XPRS_msp_getintattribprobsol` and `XPRS_msp_getdblattribprobsol`.

The attributes here are a function of a solution and problem pair. However, the user may be interested in the maximum or minimum value of an attribute over all solutions for a given problem. For example, the minimum objective value of any stored solution with respect to a given problem. The values for the attributes in this case are accessed using routines `XPRS_msp_getintattribprobextreme` and `XPRS_msp_getdblattribprobextreme`. These routines are special in that, as well as the returning attribute value, they also return the ID of a solution that achieves the attribute value.

#### Section 1.5 Getting lists of solutions


Apart from just getting an attribute value for a given solution and problem \(using the functions `XPRS_msp_getintattribprobsol` and `XPRS_msp_getdblattribprobsol`\) the user may also be interested in how an attribute behaves over a set of solutions. For example, the user may want the objective function values for the solutions with respect to a given problem. Another example may be that the user wants the MIP infeasibilities of the solutions with respect to a given problem.

The function `XPRS_msp_getsollist` is used to query for a list of solutions based on an attribute. The solutions are returned as a list of solution IDs. The user can choose to rank the returned solutions by their attribute values and they may also choose to return solutions in a range of the ranked ordering of the solutions. The user can, for example, get the objective functions of the solutions ranked in ascending order so they can find the one \(or more\) solutions that have the minimum objective value.

Note that `XPRS_msp_getsollist` will only return solutions for which the attribute is relevant. For example, if the user queries on the objective function values then only feasible solutions of the problem are returned. If, for example, the users queries on MIP infeasibilities then only those solutions with any MIP infeasibilities are returned.

A function `XPRS_msp_getsollist2`, similar to `XPRS_msp_getsollist`, provides the user with additional filtering control on the returned list of solution IDs.

#### Section 1.6 Control options


##### Duplicate solutions


Handling solution duplicates is an issue of particular relevance to the storage of solutions. Firstly, it is an issue with regards to the efficient use of the storage memory. It is also an issue with regards to how the set of stored solutions for a problem reflects the properties of the problem. For example, consider that we query, using `XPRS_msp_getsollist`, the solution pool looking for MIP solutions of a problem and we find 10 solutions with the same, optimal MIP objective for the problem. We may believe that the problem has multiple optimal MIP solutions. However, if these solutions are all duplicates then there is only one solution and we do not have proof the problem has multiple optimal solutions.

The MIP solution pool provides a set of policies the user can choose as an integer control parameter `MSP_DUPLICATESOLUTIONSPOLICY` for automatically handling the exclusion of solutions that are duplicated. These are:-


 * Keep all: There is no checking for duplicate solutions.
 * Exact: Solution pairs are the same if all variables have exactly the same value. Duplicates solutions are discarded.
 * Exact and rounded: Solution pairs are the same if all continuous variables have exactly the same value and the discrete component of the solution matches i.e., matches within tolerance. Duplicates solutions are discarded.
 * Rounded only: Solution pairs are the same if the discrete components of the solutions match. Duplicates solutions are discarded.


When the policy requires duplicate solutions be discarded the MIP solution pool compares all pairs of solutions to determine duplicates. If a solution is found to be duplicated by another solution then the solution with the larger solution id value is discarded i.e., a solution that is stored earlier is kept in place of a later, duplicate solution.

The discrete component of the solutions is determined by the MIP model of one of the 'attached' problems. The attached problem that defines the MIP model is the first problem to be attached to the MIP solution pool once the MIP model is undefined. The MIP model is undefined when the MIP solution pool is first created and after the problem currently defining the MIP model is 'detached'.

When comparing the discrete component of two solutions there are two types of tolerance used. The `MIPTOL` tolerance is used to define the rounded values of the variables and the `FEASTOL` tolerance is used to define when solution values are zero. Each solution has a control for each of these tolerances identified by `MSP_SOL_MIPTOL` and `MSP_SOL_FEASTOL`. The user can access these control values for a solution using `XPRS_msp_getdblcontrolsol` and `XPRS_msp_setdblcontrolsol`.

The discrete component of a solution \(assuming it is MIP feasible with respect to the MIP model\) is insensitive to small floating point variations in the values of the double solution variables e.g., a binary variable in a solution pair is compared as if the double solution value was rounded to 0 or 1. Therefore, comparing the discrete components of two solutions will match more readily than comparing the variable values with exact matches. As a result there will be no fewer solutions discarded using the discrete components comparison than there will be discarded using exact value matches \(and likely there will be more solutions discarded\). For this reason it is important to use care when using the policies that include discrete component comparisons since it is possible that solutions of interest may be deleted from the pool. Note that this may be a problem in the case where there is more than one MIP model for the solutions being stored in the MIP solution pool. We may delete solutions that are considered to be duplicates with regards to the MIP model used by the pool but are not considered duplicates by the other MIP model.

### Chapter 2 MSP Functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRS_msp_addcbmsghandler` | Declares an output callback function, called every time a line of message text is output by the MIP solution pool. This callback function will be called in addition to any output callbacks already added by `XPRS_msp_addcbmsghandler`.
`XPRS_msp_create` | Sets up a new MIP solution pool object.
`XPRS_msp_delsol` | Deletes a solution from the pool.
`XPRS_msp_destroy` | Destroys a MIP solution pool object and its resources. The object will generally be created by a call to the function `XPRS_msp_create`.
`XPRS_msp_findsolbyname` | Finds the id of a solution given the solution's name.
`XPRS_msp_getcbmsghandler` | Get the output callback function, as set by `XPRS_msp_setcbmsghandler`.
`XPRS_msp_getdblattrib` | Provides read access to the values of double attributes associated with the MIP solution pool.
`XPRS_msp_getdblattribprob` | Provides read access to the values of double attributes associated with the MIP solution pool with respect to the given problem.
`XPRS_msp_getdblattribprobextreme` | Retrieves the extreme value of a double attribute associated with the set of solutions stored in the MIP solution pool evaluated with respect to the given problem. For example, the minim of the objective values of feasible solutions for the problem across the solutions stored in the MIP solution pool.
`XPRS_msp_getdblattribprobsol` | Provides read access to the values of double attributes associated with the MIP solution pool with respect to the given solution stored in the MIP solution pool and the given problem. For example, the objective value of the given solution with respect to the given problem.
`XPRS_msp_getdblattribsol` | Provides read access to the values of double attributes associated a solution stored in the MIP solution pool.
`XPRS_msp_getdblcontrol` | Retrieves the value of a given double control parameter.
`XPRS_msp_getdblcontrolsol` | Retrieves the value of a given double control parameter.
`XPRS_msp_getintattrib` | Provides read access to the values of integer attributes associated with the MIP solution pool.
`XPRS_msp_getintattribprob` | Provides read access to the values of integer attributes associated with the MIP solution pool with respect to the given problem. For example, the number of solutions in the MIP solution pool that are feasible for the problem.
`XPRS_msp_getintattribprobextreme` | Retrieves the extreme value of an integer attribute associated with the set of solutions stored in the MIP solution pool evaluated with respect to the given problem. For example, the minim of the count of column bound infeasibilities for solutions of the problem taken across solutions stored in the MIP solution pool that have at least one column bound infeasibility for the problem.
`XPRS_msp_getintattribprobsol` | Provides read access to the values of integer attributes associated with the MIP solution pool with respect to the given solution stored in the MIP solution pool and the given problem. For example, the count of column bound infeasibilities for solutions of the problem.
`XPRS_msp_getintattribsol` | Provides read access to the values of integer attributes associated with a solution stored in the MIP solution pool. For example, the number of columns in the solution.
`XPRS_msp_getintcontrol` | Retrieves the value of a given integer control parameter.
`XPRS_msp_getintcontrolsol` | Retrieves the value of a given integer control parameter.
`XPRS_msp_getlasterror` | Gets the last error message.
`XPRS_msp_getsol` | Returns the solution values for a solution stored in the MIP solution pool.
`XPRS_msp_getsollist` | Returns a list of solution ids of solutions with the same number of columns as `prob_to_rank_against`. The list may be sorted by the value of some attribute of the solutions e.g., the objective function. The list may be filtered to contain either only feasible solutions or only infeasible solutions.
`XPRS_msp_getsollist2` | Returns a list of solution ids of solutions with the same number of columns as `prob_to_rank_against`. The list may be sorted by the value of some attribute of the solutions e.g., the objective function. The list may be filtered to contain either only feasible solutions or only infeasible solutions. This function is the same as `XPRS_msp_getsollist` in terms of the purpose described so far. The additional functionality provided by `XPRS_msp_getsollist2` is to allow the returned solutions to be filtered logically on the values of `MSP_SOL_BITFIELDSSYS` and `MSP_SOL_BITFIELDSUSR`.
`XPRS_msp_getsolname` | Gets the name of a solution stored in a MIP solution pool.
`XPRS_msp_loadsol` | Loads a solution into a MIP solution pool.
`XPRS_msp_probattach` | Attaches a problem to a MIP solution pool.
`XPRS_msp_probdetach` | Detaches a problem from a MIP solution pool that was previously attached with a call to `XPRS_msp_probattach`.
`XPRS_msp_readslxsol` | Reads one or more solutions from an ASCII solution file \( `.slx`\). Solution files can be created with a call to `XPRS_msp_writeslxsol`.
`XPRS_msp_removecbmsghandler` | Removes an output callback function previously added by `XPRS_msp_addcbmsghandler`. The specified callback function will no longer be called after it has been removed.
`XPRS_msp_setcbmsghandler` | Declares an output callback function, called every time a line of message text is output by a MIP solution pool object.
`XPRS_msp_setdblcontrol` | Sets the value of a given double control parameter.
`XPRS_msp_setdblcontrolsol` | Sets the value of a given double control parameter.
`XPRS_msp_setintcontrol` | Sets the value of a given integer control parameter.
`XPRS_msp_setintcontrolsol` | Sets the value of a given integer control parameter.
`XPRS_msp_setsolname` | Changes the name of a solution stored in the MIP solution pool.
`XPRS_msp_writeslxsol (MSP_WRITESLXSOL)` | Creates an ASCII solution file \( `.slx`\) using a similar format to MPS files. The file can contain one or more solutions. These files can be read back into a MIP solution pool using the `XPRS_msp_readslxsol` function.

#### XPRS_msp_addcbmsghandler

_**Purpose:**_

   Declares an output callback function, called every time a line of message text is output by the MIP solution pool. This callback function will be called in addition to any output callbacks already added by `XPRS_msp_addcbmsghandler`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_addcbmsghandler(XPRSmipsolpool msp, int (XPRS_CC *f_msghandler) (XPRSobject vXPRSObject, void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void * p, int priority);
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool 
`f_msghandler` | | The callback function which takes six arguments, `vXPRSObject`, `vUserContext`, `vSystemThreadId`, `sMsg`, `iMsgType` and `iMsgNumber`. Use a NULL value to cancel a callback function. 
`vXPRSObject` | | The object sending the message. Use [`XPRSgetobjecttypename`](../../HTML/optimizer?scroll=XPRSgetobjecttypename) to get the name of the object type. 
`vUserContext` | | The user-defined object passed to the callback function. 
`vSystemThreadId` | | The system id of the thread sending the message caste to a void \*. 
`sMsg` | | A null terminated character array \(string\) containing the message, which may simply be a new line. When the callback is called for the first time `sMsg` will be a NULL pointer. 
`iMsgType` |  | Indicates the type of output message:
&nbsp; | `1` | information messages;
&nbsp; | `2` | \(not used\);
&nbsp; | `3` | warning messages;
&nbsp; | `4` | error messages.
&nbsp; |  | A negative value means the callback is being called for the first time.
`iMsgNumber` | | The number associated with the message. If the message is an error or a warning then you can look up the number in the section Optimizer Error and Warning Messages for advice on what it means and how to resolve the associated issue. 
`p` | | A user-defined object to be passed to the callback function. 
`priority` | | An integer that determines the order in which multiple output callbacks will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
To send messages to a log file the built in message handler `XPRSlogfilehandler`can be used. This can be done with:


```
XPRS_msp_addcbmsghandler(msp, XPRSlogfilehandler, "log.txt");

```



_**Related topics:**_
`XPRS_msp_removecbmsghandler`, [`XPRSgetobjecttypename`](../../HTML/optimizer?scroll=XPRSgetobjecttypename).

#### XPRS_msp_create

_**Purpose:**_

   Sets up a new MIP solution pool object.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_create(XPRSmipsolpool *msp)
`

_**Argument:**_

Name |  Description
---------- | ---------- 
`msp` | Pointer to a variable holding the new MIP solution pool. 

_**Further information:**_
1. Calls to `XPRS_msp_create` must be made after the call to [`XPRSinit`](../../HTML/optimizer?scroll=XPRSinit).
2. All MIP solution pools created using a call to `XPRS_msp_create` should be disposed of with a call to `XPRS_msp_destroy`.

_**Related topics:**_
[`XPRSinit`](../../HTML/optimizer?scroll=XPRSinit), `XPRS_msp_destroy`.

#### XPRS_msp_delsol

_**Purpose:**_

   Deletes a solution from the pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_delsol(XPRSmipsolpool msp, const int iSolutionId, int * const iSolutionIdStatus)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution to be deleted. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution which is deleted.

_**Further information:**_
The user will obtain the solution id `iSolutionId`from interaction with the MIP solution pool via functions such as`XPRS_msp_findsolbyname`,`XPRS_msp_getdblattribprobextreme`,`XPRS_msp_getintattribprobextreme`and`XPRS_msp_getsollist`.

_**Related topics:**_
`XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_destroy

_**Purpose:**_

   Destroys a MIP solution pool object and its resources. The object will generally be created by a call to the function`XPRS_msp_create`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_destroy(XPRSmipsolpool msp)
`

_**Argument:**_

Name |  Description
---------- | ---------- 
`msp` | MIP solution pool to be destroyed. 

_**Related topics:**_
`XPRS_msp_create`.

#### XPRS_msp_findsolbyname

_**Purpose:**_

   Finds the id of a solution given the solution's name.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_findsolbyname(XPRSmipsolpool msp, const char *sSolutionName, int *const iSolutionId)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`sSolutionName` | A null terminated string containing the name of the solution to find. 
`iSolutionId` | Pointer to the integer where the solution id will be returned. A value of 0 will be returned if the solution name does not exist. 

_**Further information:**_
Names of solutions enter the MIP solution pool via functions such as`XPRS_msp_loadsol`,`XPRS_msp_setsolname`and`XPRS_msp_readslxsol`. Solutions entering the MIP solution pool directly from attached problems are given automatic names.

_**Related topics:**_
`XPRS_msp_loadsol`, `XPRS_msp_setsolname`, `XPRS_msp_getsolname`, `XPRS_msp_readslxsol`.

#### XPRS_msp_getcbmsghandler

_**Purpose:**_

   Get the output callback function, as set by`XPRS_msp_setcbmsghandler`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getcbmsghandler(XPRSmipsolpool msp, int (XPRS_CC **r_f_msghandler) (XPRSobject vXPRSObject, void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void **object);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`r_f_msghandler` | Pointer to the memory where the callback function will be returned. 

_**Related topics:**_
`XPRS_msp_setcbmsghandler`.

#### XPRS_msp_getdblattrib

_**Purpose:**_

   Provides read access to the values of double attributes associated with the MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblattrib(XPRSmipsolpool msp, const int iAttribId, double * const Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iAttribId` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Val` | Pointer to a double where the value of the attribute will be returned. 

_**Related topics:**_
`XPRS_msp_getintattrib`

#### XPRS_msp_getdblattribprob

_**Purpose:**_

   Provides read access to the values of double attributes associated with the MIP solution pool with respect to the given problem.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblattribprob(XPRSmipsolpool msp, XPRSprob prob, const int iAttribId, double * const Dst)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob` | Problem for which the attribute is required to be evaluated. 
`iAttribId` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Dst` | Pointer to a double where the value of the attribute will be returned. 

_**Related topics:**_
`XPRS_msp_getintattribprob`.

#### XPRS_msp_getdblattribprobextreme

_**Purpose:**_

   Retrieves the extreme value of a double attribute associated with the set of solutions stored in the MIP solution pool evaluated with respect to the given problem. For example, the minim of the objective values of feasible solutions for the problem across the solutions stored in the MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblattribprobextreme(XPRSmipsolpool msp, XPRSprob prob_to_rank_against, const int 
bGet_Max_Otherwise_Min, int * const iSolutionId, const int iAttribId, double * const ExtremeVal)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob_to_rank_against` | Problem for which the attribute is required to be evaluated. 
`bGet_Max_Otherwise_Min` | If set to a non-zero value the routine will return the maximum attribute value; otherwise the minim attribute value will be returned. 
`iAttribId` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`iSolutionId` | The id of the solution for which the returned attribute value was evaluated with the problem `prob_to_rank_against`. 
`ExtremeVal` | Pointer to a double where the value of the attribute will be returned. 

_**Further information:**_
1. This function returns objective values only for feasible solutions. For attributes representing infeasibility this function returns a meaningful value only if there any solutions with an infeasibility associated with the attribute. For example, if the attribute represents the sum of column bound infeasibilities for solutions in the MIP solution pool then a meaningful value is only returned if there are any solutions with column bound infeasibilities for the problem.
2. The attributes accessed by this function are the same as those available through `XPRS_msp_getdblattribprobsol`. That is, double attributes relating to a problem and solution pair, e.g., the objective function value of a solution to the problem
3. If there is no value returned then the value of `iSolutionId` is set to 0; otherwise it will be the positive id of the solution with the returned attribute value.

_**Related topics:**_
`XPRS_msp_getintattribprobextreme`, `XPRS_msp_getdblattribprobsol`.

#### XPRS_msp_getdblattribprobsol

_**Purpose:**_

   Provides read access to the values of double attributes associated with the MIP solution pool with respect to the given solution stored in the MIP solution pool and the given problem. For example, the objective value of the given solution with respect to the given problem.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblattribprobsol(MipSolPool msp, XPRSprob prob_to_rank_against, const int iSolutionId, int * const 
iSolutionIdStatus, const int iAttribId, double * const Dst)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`prob_context` | | Problem for which the attribute `iAttribId` is required to be evaluated using solution `iSolutionId`. 
`iSolutionId` | | The id of the solution for which the attribute `iAttribId` is evaluated with respect to the problem `prob_context`. 
`iSolutionIdStatus` |  | Pointer to an int where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iAttribId` | | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Dst` | | Pointer to a double where the value of the attribute will be returned. 

_**Further information:**_
1. The user will obtain the solution id `iSolutionId` from interaction with the MIP solution pool via functions such as `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme` and `XPRS_msp_getsollist`.
2. The attributes accessed by this function are the same as those available through `XPRS_msp_getdblattribprobextreme`. That is, double attributes relating to a problem and solution pair, e.g., the objective function value of a solution to the problem

_**Related topics:**_
`XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_findsolbyname`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_getdblattribsol

_**Purpose:**_

   Provides read access to the values of double attributes associated a solution stored in the MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblattribsol(XPRSmipsolpool msp, const int iSolutionId, int * const iSolutionIdStatus, const int iAttribId, 
double * const Dst)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution for which the attribute is to be returned. 
`iSolutionIdStatus` |  | Pointer to an int where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iAttribId` | | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Dst` | | Pointer to a double where the value of the attribute will be returned. 

_**Further information:**_
The user will obtain the solution id `iSolutionId`from interaction with the MIP solution pool via functions such as`XPRS_msp_findsolbyname`,`XPRS_msp_getdblattribprobextreme`,`XPRS_msp_getintattribprobextreme`and`XPRS_msp_getsollist`.

_**Related topics:**_
`XPRS_msp_getintattribsol`, `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_getdblcontrol

_**Purpose:**_

   Retrieves the value of a given double control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblcontrol(XPRSmipsolpool msp, const int iControlId, double * const Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iControlId` | Id of control whose value is to be returned. A full list of all available controls may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Val` | Pointer to a double where the value of the control will be returned. 

_**Related topics:**_
`XPRS_msp_getintcontrol`, `XPRS_msp_setdblcontrol`, `XPRS_msp_setintcontrol`.

#### XPRS_msp_getdblcontrolsol

_**Purpose:**_

   Retrieves the value of a given double control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblcontrolsol(XPRSmipsolpool msp, int iSolutionId, int * iSolutionIdStatus, const int iControlId, double * 
const Val)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution for which the control is to be returned. 
`iSolutionIdStatus` |  | Pointer to an int where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iControlId` | | Id of control whose value is to be returned. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | | Pointer to a double where the value of the control will be returned. 

_**Related topics:**_
`XPRS_msp_getintcontrolsol`, `XPRS_msp_setdblcontrolsol`, `XPRS_msp_setintcontrolsol`.

#### XPRS_msp_getintattrib

_**Purpose:**_

   Provides read access to the values of integer attributes associated with the MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getintattrib(XPRSmipsolpool msp, const int iAttribId, int * const Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iAttribId` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Val` | Pointer to an integer where the value of the attribute will be returned. 

_**Related topics:**_
`XPRS_msp_getdblattrib`.

#### XPRS_msp_getintattribprob

_**Purpose:**_

   Provides read access to the values of integer attributes associated with the MIP solution pool with respect to the given problem. For example, the number of solutions in the MIP solution pool that are feasible for the problem.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getintattribprob(XPRSmipsolpool msp, XPRSprob prob, const int iAttribId, int * const Dst)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob` | Problem for which the attribute is required to be evaluated. 
`iAttribId` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Dst` | Pointer to an integer where the value of the attribute will be returned. 

_**Related topics:**_
`XPRS_msp_getdblattribprob`.

#### XPRS_msp_getintattribprobextreme

_**Purpose:**_

   Retrieves the extreme value of an integer attribute associated with the set of solutions stored in the MIP solution pool evaluated with respect to the given problem. For example, the minim of the count of column bound infeasibilities for solutions of the problem taken across solutions stored in the MIP solution pool that have at least one column bound infeasibility for the problem.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getintattribprobextreme(XPRSmipsolpool msp, XPRSprob prob_to_rank_against, const int 
bGet_Max_Otherwise_Min, int * const iSolutionId, const int iAttribId, int * const ExtremeVal)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob_to_rank_against` | Problem for which the attribute is required to be evaluated. 
`bGet_Max_Otherwise_Min` | If set to a non-zero value the routine will return the maximum attribute value; otherwise the minim attribute value will be returned. 
`iAttribId` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`iSolutionId` | The id of the solution for which the returned attribute value was evaluated with the problem `prob_to_rank_against`. 
`ExtremeVal` | Pointer to an integer where the value of the attribute will be returned. 

_**Further information:**_
1. For attributes representing infeasibility this function returns a meaningful value only if there any solutions with an infeasibility associated with the attribute. For example, if the attribute represents the count of column bound infeasibilities for solutions in the MIP solution pool then a meaningful value is only returned if there are any solutions with column bound infeasibilities for the problem.
2. The attributes accessed by this function are the same as those available through `XPRS_msp_getintattribprobsol`. That is, integer attributes relating to a problem and solution pair, e.g., the count of column bound infeasibilities for solutions of the problem.
3. If there is no value returned then the value of `iSolutionId` is set to 0; otherwise it will be the positive id of the solution with the returned attribute value.

_**Related topics:**_
`XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobsol`.

#### XPRS_msp_getintattribprobsol

_**Purpose:**_

   Provides read access to the values of integer attributes associated with the MIP solution pool with respect to the given solution stored in the MIP solution pool and the given problem. For example, the count of column bound infeasibilities for solutions of the problem.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getdblattribprobsol(MipSolPool msp, XPRSprob prob_to_rank_against, const int iSolutionId, int * const 
iSolutionIdStatus, const int iAttribId, double * const Dst)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`prob_context` | | Problem for which the attribute `iAttribId` is required to be evaluated using solution `iSolutionId`. 
`iSolutionId` | | The id of the solution for which the attribute `iAttribId` is evaluated with respect to the problem `prob_context`. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iAttribId` | | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Dst ` | | Pointer to an integer where the value of the attribute will be returned. 

_**Further information:**_
1. The user will obtain the solution id iSolutionId from interaction with the MIP solution pool via functions such as `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme` and `XPRS_msp_getsollist`.
2. The attributes accessed by this function are the same as those available through `XPRS_msp_getintattribprobextreme`. That is, integer attributes relating to a problem and solution pair, e.g., the count of column bound infeasibilities for solutions of the problem.

_**Related topics:**_
`XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_getintattribsol

_**Purpose:**_

   Provides read access to the values of integer attributes associated with a solution stored in the MIP solution pool. For example, the number of columns in the solution.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getintattribsol(XPRSmipsolpool msp, const int iSolutionId, int * const iSolutionIdStatus, const int iAttribId, int 
* const Dst)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution for which the attribute is to be returned. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iAttribId` | | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. 
`Dst` | | Pointer to an integer where the value of the attribute will be returned. 

_**Further information:**_
The user will obtain the solution id iSolutionId from interaction with the MIP solution pool via functions such as`XPRS_msp_findsolbyname`,`XPRS_msp_getdblattribprobextreme`,`XPRS_msp_getintattribprobextreme`and`XPRS_msp_getsollist`.

_**Related topics:**_
`XPRS_msp_getdblattribsol`, `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_getintcontrol

_**Purpose:**_

   Retrieves the value of a given integer control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getintcontrol(XPRSmipsolpool msp, const int iControlId, int * const Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iControlId` | Id of control whose value is to be returned. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | Pointer to an integer where the value of the control will be returned. 

_**Related topics:**_
`XPRS_msp_getdblcontrol`, `XPRS_msp_setdblcontrol`, `XPRS_msp_setintcontrol`.

#### XPRS_msp_getintcontrolsol

_**Purpose:**_

   Retrieves the value of a given integer control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getintcontrolsol(XPRSmipsolpool msp, int iSolutionId, int * iSolutionIdStatus, const int iControlId, int * const 
Val)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution for which the control is to be returned. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iControlId` | | Id of control whose value is to be returned. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | | Pointer to an integer where the value of the control will be returned. 

_**Related topics:**_
`XPRS_msp_getdblcontrolsol`, `XPRS_msp_setdblcontrolsol`, `XPRS_msp_setintcontrolsol`.

#### XPRS_msp_getlasterror

_**Purpose:**_

   Gets the last error message.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getlasterror(XPRSmipsolpool msp, int * iMsgNumber, char * msg, int iStringBufferBytes, int * 
iBytesInInternalString)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution pool. 
`iMsgNumber ` | A pointer to an integer to return the number of the last error message. Can be NULL if not required. Refer to Chapter _9 of the Optimizer Reference Manual_ for a list of possible error numbers, the errors and warnings that they indicate, and advice on what they mean and how to resolve them. 
`msg` | A character buffer of length at least `iStringBufferBytes` to return the error message. Can be NULL if not required. 
`iStringBufferBytes` | The length of the `msg` buffer. 
`iBytesInInternalString` | A pointer to an integer to return the number of bytes required to store the error message. Can be NULL if not required. 

_**Related topics:**_
Chapter _9 of the Optimizer Reference Manual_, `XPRS_msp_setcbmsghandler`.

#### XPRS_msp_getsol

_**Purpose:**_

   Returns the solution values for a solution stored in the MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getsol(XPRSmipsolpool msp, const int iSolutionId, int * const iSolutionIdStatus, double x[], const int iColFirst, 
const int iColLast, int * const nValuesReturned)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`Msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the required solution. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`x` | | Double array where the values of the solution will be returned. May be NULL if not required. 
`iColFirst` | | Index of the column whose solution value is to be returned in the first element of array `x`. If `iColLast > iColFirst` then any subsequent columns are to have their values written to the subsequent elements of `x`. 
`iColLast` | | If `x` is non-NULL then at most `iColLast - iColFirst + 1` solution values will be written to `x`. There will be fewer solution values written if `iColLast` is greater than or equal to the number of columns in the solution. 
`nValuesReturned` | | Pointer to an integer where the number of solution values that were available to be written is returned. This number will always be less than or equal to `iColLast - iColFirst + 1`. A value is returned for this parameter regardless of whether `x` is passed as NULL. May be NULL if not required. 

_**Further information:**_
1. It is an error condition if `iColLast <  iColFirst` or `iColFirst <  0` or if `iColFirst` is greater than or equal to the number of columns in the solution.
2. The user will obtain the solution id `iSolutionId` from interaction with the MIP solution pool via functions such as `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme` and `XPRS_msp_getsollist`.
3. By passing `x` as NULL and setting `iColFirst` to 0 and `iColLast` to a large positive integer it is possible to use `XPRS_msp_getsol` to obtain in the `nValuesReturned` parameter the number of columns in the solution.

_**Related topics:**_
`XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_getsollist

_**Purpose:**_

   Returns a list of solution ids of solutions with the same number of columns as `prob_to_rank_against`. The list may be sorted by the value of some attribute of the solutions e.g., the objective function. The list may be filtered to contain either only feasible solutions or only infeasible solutions.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getsollist(XPRSmipsolpool msp, XPRSprob prob_to_rank_against, const int iRankAttrib, const int 
bRankAscending, const int iRankFirstIndex, const int iRankLastIndex, int iSolutionIds_Zb[], int * const nReturnedSolIds, int * const 
nSols)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob_to_rank_against` | Problem for which the attribute `iRankAttrib` is evaluated in order to rank the solution ids returned in the `iSolutionIds` array. Only solutions with the same number of columns as `prob_to_rank_against` are considered when generating the list of solution ids. May be NULL if the IDs of all solutions are to be returned. 
`iRankAttrib` | Id of the attribute whose value is used to rank the solution ids returned in the `iSolutionIds` array. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. If the attribute represents infeasibility then only infeasible solutions will be returned; otherwise only feasible solutions will be returned. If `iRankAttrib` is passed in as 0, or if it is not a valid attribute id, then the solution ids of feasible solutions for the problem will be returned unranked. If iRankAttrib is not a valid attribute id then a warning is logged. This argument is ignored if prob\_to\_rank\_against is passed as NULL. 
`bRankAscending` | If set to a non-zero value the function returns the solution ids ordered in ascending order of the attribute value; otherwise the solution ids are returned in descending order. This argument is ignored if `prob_to_rank_against` is passed as NULL or if `iRankAttrib` is passed in as 0, or if it is not a valid attribute id. 
`iRankFirstIndex` | Index \(one-based\) in the rank order of solutions for which the associated solution's id number, if there is a solution at this index, is to be returned in the first element of array `iSolutionId` s. If `iRankLastIndex > iRankFirstIndex` then any subsequent solutions in the rank ordering are to have their solution ids written to the subsequent elements of `iSolutionIds`. 
`iRankLastIndex` | If iSolutionIds is non-NULL then at most `iRankLastIndex - iRankFirstIndex + 1` solution ids will be written to `iSolutionIds`. There will be fewer solution ids written if `iRankLastIndex` is greater than the number of solutions in the MIP solution pool. 
`iSolutionIds` | Integer array where the solution ids will be returned. May be NULL if not required. 
`nReturnedSolIds` | Pointer to an integer where the number of solution ids that were available to be written is returned. This number will always be less than or equal to `iRankLastIndex - iRankFirstIndex + 1`. A value is returned for this parameter regardless of whether `iSolutionIds` is passed as NULL. May be NULL if not required. 
`nSols` | Pointer to an integer where the total number of solution ids that could possibly be written is returned. May be NULL if not required. 

_**Further information:**_
1. If `iRankFirstIndex` > `iRankLastIndex` and the `nSols` argument is passed down as NULL then the routine will return with no solution ids written.
2. Information about the solution with respect to the problem can be obtained via routines `XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribsol` and `XPRS_msp_getintattribsol`. The solution values can be obtained via the routine `XPRS_msp_getsol`.

_**Related topics:**_
`XPRS_msp_getsollist2`, `XPRS_msp_getsol`, `XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribsol`, `XPRS_msp_getintattribsol`.

#### XPRS_msp_getsollist2

_**Purpose:**_

   Returns a list of solution ids of solutions with the same number of columns as `prob_to_rank_against`. The list may be sorted by the value of some attribute of the solutions e.g., the objective function. The list may be filtered to contain either only feasible solutions or only infeasible solutions. This function is the same as`XPRS_msp_getsollist`in terms of the purpose described so far. The additional functionality provided by`XPRS_msp_getsollist2`is to allow the returned solutions to be filtered logically on the values of`MSP_SOL_BITFIELDSSYS`and`MSP_SOL_BITFIELDSUSR`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getsollist2(XPRSmipsolpool msp, XPRSprob prob_to_rank_against, int iRankAttrib, int bRankAscending, int 
iRankFirstIndex_Ob, int iRankLastIndex_Ob, int bUseUserBitFilter, int iUserBitMask, int iUserBitPattern, int bUseInternalBitFilter, int 
iInternalBitMask, int iInternalBitPattern, int iSolutionIds_Zb[], int * nReturnedSolIds, int * nSols)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob_to_rank_against` | Problem for which the attribute `iRankAttrib` is evaluated in order to rank the solution ids returned in the `iSolutionIds` array. Only solutions with the same number of columns as `prob_to_rank_against` are considered when generating the list of solution ids. May be NULL if the IDs of all solutions are to be returned. 
`iRankAttrib` | Id of the attribute whose value is used to rank the solution ids returned in the `iSolutionIds` array. A full list of all available attributes may be found in Chapter  _MSP Attributes_, or from the list in the `xprs.h` header file. If the attribute represents infeasibility then only infeasible solutions will be returned; otherwise only feasible solutions will be returned. If `iRankAttrib` is passed in as 0, or if it is not a valid attribute id, then the solution ids of feasible solutions for the problem will be returned unranked. If `iRankAttrib` is not a valid attribute id then a warning is logged. This argument is ignored if `prob_to_rank_against` is passed as NULL. 
`bRankAscending` | If set to a non-zero value the function returns the solution ids ordered in ascending order of the attribute value; otherwise the solution ids are returned in descending order. This argument is ignored if `prob_to_rank_against` is passed as NULL or if `iRankAttrib` is passed in as 0, or if it is not a valid attribute id. 
`iRankFirstIndex` | Index \(one-based\) in the rank order of solutions for which the associated solution's id number, if there is a solution at this index, is to be returned in the first element of array `iSolutionId` s. If `iRankLastIndex > iRankFirstIndex` then any subsequent solutions in the rank ordering are to have their solution ids written to the subsequent elements of `iSolutionIds`. 
`iRankLastIndex` | If `iSolutionIds` is non-NULL then at most `iRankLastIndex -  iRankFirstIndex + 1` solution ids will be written to `iSolutionIds`. There will be fewer solution ids written if `iRankLastIndex` is greater than the number of solutions in the MIP solution pool. 
`bUseUserBitFilter` | Set this value to 1 if the solutions should be filtered by their `MSP_SOL_BITFIELDSUSR` control values using the values of `iUserBitMask` and `iUserBitPattern`. If we let `iBitFieldUser` be the value of the `MSP_SOL_BITFIELDSUSR` control for a solution then the solution will not be returned in the list if \( `iBitFieldUser &  iUserBitMask`\) `!= iUserBitPattern`. Set to 0 if filtering is not required on the `MSP_SOL_BITFIELDSUSR` control values. 
`iUserBitMask` | Bit mask used to filter solutions by their `MSP_SOL_BITFIELDSUSR` control values. 
`iUserBitPattern` | Bit pattern used to filter solutions by their `MSP_SOL_BITFIELDSUSR` control values. 
`bUseInternalBitFilter` | Set this value to 1 if the solutions should be filtered by their `MSP_SOL_BITFIELDSSYS` attribute values using the values of `iInternalBitMask` and `iInternalBitPattern`. If we let `iBitFieldSys` be the value of the `MSP_SOL_BITFIELDSSYS` attribute for a solution then the solution will not be returned in the list if \( `iBitFieldUser`& `iInternalBitMask`\) `!= iInternalBitPattern`. Set to 0 if filtering is not required on the `MSP_SOL_BITFIELDSSYS` attribute values. 
`iInternalBitMask` | Bit mask used to filter solutions by `MSP_SOL_BITFIELDSSYS` attribute values. 
`iInternalBitPattern` | Bit pattern used to filter solutions by `MSP_SOL_BITFIELDSSYS` attribute values. 
`iSolutionIds` | Integer array where the solution ids will be returned. May be NULL if not required. 
`nReturnedSolIds` | Pointer to an integer where the number of solution ids that were available to be written is returned. This number will always be less than or equal to `iRankLastIndex - iRankFirstIndex + 1`. A value is returned for this parameter regardless of whether `iSolutionIds` is passed as NULL. May be NULL if not required. 
`nSols` | Pointer to an integer where the total number of solution ids that could possibly be written is returned. May be NULL if not required. 

_**Further information:**_
1. If `iRankFirstIndex > iRankLastIndex` and the `nSols` argument is passed down as NULL then the routine will return with no solution ids written.
2. Information about the solution with respect to the problem can be obtained via routines `XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribsol` and `XPRS_msp_getintattribsol`. The solution values can be obtained via the routine `XPRS_msp_getsol`.

_**Related topics:**_
`XPRS_msp_getsollist`, `XPRS_msp_getsol`, `XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribsol`, `XPRS_msp_getintattribsol`.

#### XPRS_msp_getsolname

_**Purpose:**_

   Gets the name of a solution stored in a MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_getsolname(XPRSmipsolpool msp, const int iSolutionId, char *sname, const int iStringBufferBytes, int * const 
iBytesInInternalString, int * const iSolutionIdStatus)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | Id of the solution whose name is to be retrieved. 
`sname` | | Pointer to a string where the name of the solution \(plus null terminator\) will be returned. This argument can be passed with NULL. 
`iStringBufferBytes` | | Maximum number of bytes to be returned in sname. 
`iBytesInInternalString` | | Pointer to the integer where the number of bytes required storing the name \(including null terminator\) will be returned. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.

_**Further information:**_
1. Names of solutions stored in a MIP solution pool are unique.
2. The user will obtain the solution id `iSolutionId` from interaction with the MIP solution pool via functions such as `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme` and `XPRS_msp_getsollist`.
3. Names of solutions enter the MIP solution pool via functions such as `XPRS_msp_loadsol`, `XPRS_msp_setsolname` and `XPRS_msp_readslxsol`. Solutions entering the MIP solution pool directly from attached problems are given automatic names.

_**Related topics:**_
`XPRS_msp_setsolname`, `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_loadsol

_**Purpose:**_

   Loads a solution into a MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_loadsol(XPRSmipsolpool msp, int * const iSolutionId, const double x[], const int nCols, const char 
*sSolutionName, int * const bNameModifiedForUniqueness, int * const bSolutionNotLoadedBecauseOfDuplication)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iSolutionId` | Pointer to the integer where the id of the loaded solution will be returned. 
`x` | Double array of length `nCols` containing the solution to be stored. 
`nCols` | The number of elements in the solution array `x`. 
`sSolutionName` | The name to use to identify the solution to be stored. If the given name already exists then the name to be stored will have characters appended to ensure the resulting name is unique among the stored solutions. If `sSolutionName` is passed as NULL then a unique name will be generated automatically for the solution. 
`bNameModifiedForUniqueness` | Pointer to an integer returning 1 if it was necessary for the given solution name `sNewSolutionBaseName` to be modified to maintain uniqueness of solution names; 0 otherwise. 
`bSolutionNotLoadedBecauseOfDuplication` | Pointer to an integer returning 1 if the solution was rejected because it was found to a duplicate of an existing solution; 0 otherwise. 

_**Further information:**_
Information about the solution with respect to a problem can be obtained via routines`XPRS_msp_getdblattribprobsol`,`XPRS_msp_getintattribprobsol`,`XPRS_msp_getdblattribsol`and`XPRS_msp_getintattribsol`.

_**Related topics:**_
`XPRS_msp_getdblattribprobsol`, `XPRS_msp_getintattribprobsol`, `XPRS_msp_getdblattribsol`, `XPRS_msp_getintattribsol`.

#### XPRS_msp_probattach

_**Purpose:**_

   Attaches a problem to a MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_probattach(XPRSmipsolpool msp, XPRSprob prob)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob` | Problem to be attached to the MIP solution pool. 

_**Further information:**_
1. The function will return successfully if the solution is already attached to the MIP solution pool.
2. One or more problems can be attached to the MIP solution pool. A problem can only be attached to one MIP solution pool.
3. The function will return an error if the problem is already attached to another MIP solution pool.
4. The user can detach the problem from the MIP solution pool with a call to `XPRS_msp_probdetach`.
5. A problem is automatically detached from a MIP solution pool when it is destroyed. A MIP solution pool automatically detaches all problems when it is destroyed.

_**Related topics:**_
`XPRS_msp_probdetach`.

#### XPRS_msp_probdetach

_**Purpose:**_

   Detaches a problem from a MIP solution pool that was previously attached with a call to`XPRS_msp_probattach`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_probdetach(XPRSmipsolpool msp, XPRSprob prob)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`prob` | Problem to be detached from the MIP solution pool. 

_**Further information:**_
The function will return successfully if the solution is not attached to the MIP solution pool.

_**Related topics:**_
`XPRS_msp_probattach`.

#### XPRS_msp_readslxsol

_**Purpose:**_

   Reads one or more solutions from an ASCII solution file \( `.slx`\). Solution files can be created with a call to`XPRS_msp_writeslxsol`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_readslxsol(XPRSmipsolpool msp, XPRSnamelist col_name_list, const char * sFileName, const char *sFlags, 
int * const iSolutionId_Beg, int * const iSolutionId_End)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`col_name_list` | | An object used to map column names on to solution indices. May be NULL if not required. 
`sFileName` | | Null terminated string containing the file name from which the solution\(s\) are to be read. 
`sFlags` |  | Flags for`XPRS_msp_readslxsol`:
&nbsp; | `v` | use the provided filename verbatim, without appending the `.slx` extension;
&nbsp; | `z` | read a compressed input file.
`iSolutionId_Beg` | | Pointer to an integer returning the solution ID of the first solution successfully loaded from the file. May be NULL if not required. 
`iSolutionId_End` | | Pointer to an integer returning the solution ID of the last solution successfully loaded from the file. May be NULL if not required. 

_**Further information:**_
1. The user can obtain a reference to the object mapping column names to indices for a problem by calling [`XPRSgetnamelistobject`](../../HTML/optimizer?scroll=XPRSgetnamelistobject) with type 2. Passing this object down to `XPRS_msp_readslxsol` means that only solutions in the `.slx` file with column names contained in the mapping are loaded into the MIP solution pool. The loaded solutions will have the same column count as the mapping. The values for any columns that do not have an entry in the `.slx` file for a solution are set to zero.
2. If `col_name_list` is passed as NULL then all solutions are read into the MIP solution pool using the position of the solution value in the file section as the solution index.

_**Related topics:**_
`XPRS_msp_writeslxsol`.

#### XPRS_msp_removecbmsghandler

_**Purpose:**_

   Removes an output callback function previously added by`XPRS_msp_addcbmsghandler`. The specified callback function will no longer be called after it has been removed.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_removecbmsghandler(XPRSmipsolpool msp, int (XPRS_CC *f_msghandler) (XPRSobject vXPRSObject, void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void* object);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`f_msghandler` | The callback function to remove. If NULL then all output callback functions added with the given user-defined object value will be removed. 
`object` | The object value that the callback was added with. If NULL, then the object value will not be checked and all variable branching callbacks with the function pointer `f_chgbranch` will be removed. 

_**Related topics:**_
`XPRS_msp_addcbmsghandler`.

#### XPRS_msp_setcbmsghandler

_**Purpose:**_

   Declares an output callback function, called every time a line of message text is output by a MIP solution pool object.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_setcbmsghandler(XPRSmipsolpool msp, int (XPRS_CC *f_msghandler)(XPRSobject vXPRSObject, void * 
vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgCode), void * p)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`f_msghandler` | | The callback function which takes six arguments, `vXPRSObject`, `vUserContext`, `vSystemThreadId`, `sMsg`, `iMsgType` and `iMsgCode`. Use a NULL value to cancel a callback function. 
`vXPRSObject` | | A generic pointer to the msp object sending the message. 
`vUserContext` | | The user-defined object passed to the callback function. 
`vSystemThreadId` | | The system id of the thread sending the message caste to a void \*. 
`sMsg` | | A null terminated character array \(string\) containing the message, which may simply be a new line. When the callback is called for the first time sMsg will be a NULL pointer. 
`iMsgType` |  | Indicates the type of output message:
&nbsp; | `1` | information messages;
&nbsp; | `2` | \(not used\);
&nbsp; | `3` | warning messages;
&nbsp; | `4` | error messages.
&nbsp; |  | A negative value means the callback is being called for the first time.
`iMsgCode ` | | The code associated with the message. If the message is an error or a warning then you can look up the code in Chapter _9 of the Optimizer Reference Manual_ for advice on what it means and how to resolve the associated issue. 
`p` | | A user-defined object to be passed to the callback function. 

_**Further information:**_
1. To send all messages to a log file the built in message handler `XPRSlogfilehandler` can be used. This can be done with:


```
XPRS_msp_setcbmsghandler(msp, XPRSlogfilehandler, "log.txt");

```


2. The return value for this callback is ignored.

_**Related topics:**_
None.

#### XPRS_msp_setdblcontrol

_**Purpose:**_

   Sets the value of a given double control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_setdblcontrol(XPRSmipsolpool msp, const int iControlId, const double Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iControlId` | Id of control whose value is to be set. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | Value to which the control parameter is to be set. 

_**Related topics:**_
`XPRS_msp_getdblcontrol`, `XPRS_msp_setintcontrol`, `XPRS_msp_getintcontrol`.

#### XPRS_msp_setdblcontrolsol

_**Purpose:**_

   Sets the value of a given double control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_setdblcontrolsol(XPRSmipsolpool msp, int iSolutionId, int * iSolutionIdStatus, const int iControlId, const 
double Val)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution for which the control is to be set. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iControlId` | | Id of control whose value is to be set. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | | Value to which the control parameter is to be set. 

_**Related topics:**_
`XPRS_msp_getdblcontrolsol`, `XPRS_msp_setintcontrolsol`, `XPRS_msp_getintcontrolsol`.

#### XPRS_msp_setintcontrol

_**Purpose:**_

   Sets the value of a given integer control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_setintcontrol(XPRSmipsolpool msp, const int iControlId, const int Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`msp` | The current MIP solution pool. 
`iControlId` | Id of control whose value is to be set. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | Value to which the control parameter is to be set. 

_**Related topics:**_
`XPRS_msp_getintcontrol`, `XPRS_msp_setdblcontrol`, `XPRS_msp_getdblcontrol`.

#### XPRS_msp_setintcontrolsol

_**Purpose:**_

   Sets the value of a given integer control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_setintcontrolsol(XPRSmipsolpool msp, int iSolutionId, int * iSolutionIdStatus, const int iControlId, const int 
Val)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | The id of the solution for which the control is to be set. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iControlId` | | Id of control whose value is to be set. A full list of all available controls may be found in Chapter  _MSP Control Parameters_, or from the list in the `xprs.h` header file. 
`Val` | | Value to which the control parameter is to be set. 

_**Related topics:**_
`XPRS_msp_getintcontrolsol`, `XPRS_msp_getdblcontrolsol`, `XPRS_msp_setdblcontrolsol`.

#### XPRS_msp_setsolname

_**Purpose:**_

   Changes the name of a solution stored in the MIP solution pool.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_setsolname(XPRSmipsolpool msp, const int iSolutionId, const char *sNewSolutionBaseName, int * const gbNameModifiedForUniqueness, int * const iSolutionIdStatus)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`iSolutionId` | | Id of the solution whose name is to be changed. 
`sNewSolutionBaseName` | | The new name to use to identify the solution. If the given name already exists and is used by another solution then the name to be stored will have characters appended to ensure the resulting name is unique among the stored solutions. If `sNewSolutionBaseName` is passed as NULL then a unique name will be generated automatically for the solution. 
`bNameModifiedForUniqueness` | | Pointer to an integer returning 1 if it was necessary for the given solution name `sNewSolutionBaseName` to be modified to maintain uniqueness of solution names; 0 otherwise. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.

_**Further information:**_
The user will obtain the solution id `iSolutionId`from interaction with the MIP solution pool via functions such as`XPRS_msp_findsolbyname`,`XPRS_msp_getdblattribprobextreme`,`XPRS_msp_getintattribprobextreme`and`XPRS_msp_getsollist`.

_**Related topics:**_
`XPRS_msp_getsolname`, `XPRS_msp_findsolbyname`, `XPRS_msp_getdblattribprobextreme`, `XPRS_msp_getintattribprobextreme`, `XPRS_msp_getsollist`.

#### XPRS_msp_writeslxsol  MSP_WRITESLXSOL

_**Purpose:**_

   Creates an ASCII solution file \( `.slx`\) using a similar format to MPS files. The file can contain one or more solutions. These files can be read back into a MIP solution pool using the`XPRS_msp_readslxsol`function.

_**Synopsis:**_

   `
int XPRS_CC XPRS_msp_writeslxsol(XPRSmipsolpool msp, XPRSprob prob_context, int iSolutionId, int * iSolutionIdStatus, const char * sFileName, const char * sFlags)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`msp` | | The current MIP solution pool. 
`prob_context` | | Pointer to a problem. Can be NULL. See table below for interpretation in terms of function behaviour. 
`iSolutionId` | | The id of a solution to write; otherwise a flag. See table below for interpretation in terms of function behaviour. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`sFileName` | | Null terminated string containing the file name to which the solution\(s\) is to be written. 
`sFlags` |  | Flags for`XPRS_msp_writeslxsol`:
&nbsp; | `p` | use full precision for numerical values;
&nbsp; | `v` | use the provided filename verbatim, without appending the `.slx` extension;
&nbsp; | `z` | compress the output file.

_**Further information:**_
This table defines the interpretation of the values of arguments `prob_context`and `iSolutionId`in terms of the behaviour of `XPRS_msp_writeslxsol`.





| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
_prob_context_ | _iSolutionId_ | _Behaviour_ | 
Non-NULL | < 0 | Write out all feasible solutions to `prob_context`. Use the column names in `prob_context`. | 
Non-NULL | 0 | Write out a feasible solution to `prob_context`with the best objective \(given the[`OBJSENSE`](../../HTML/optimizer?scroll=OBJSENSE)value of `prob_context`\). Use the column names in `prob_context`. | 
Non-NULL | > 0 | Write out the solution with ID `iSolutionId`. It is an error if the solution does not have the same number of columns as `prob_context`. Use the column names in `prob_context`. | 
NULL | ≤0 | Write out all solutions. Use automatically generated column names. | 
NULL | > 0 | Write out the solution with ID `iSolutionId`. Use automatically generated column names. | 


_**Related topics:**_
`XPRS_msp_readslxsol`.

### Chapter 3 MSP Control Parameters


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`MSP_DEFAULTUSERSOLFEASTOL` | This is the tolerance on the value of integer, semi-continuous, partial and semi-continuos integer variables and SOS variables. If one of these is less than or equal to [`FEASTOL`](../../HTML/optimizer?scroll=FEASTOL) in absolute value, it is treated as zero.
`MSP_DEFAULTUSERSOLMIPTOL` | This is the tolerance within which a decision variable's value is considered to be integral. It is the default value for the tolerance `MSP_SOL_MIPTOL` when a solution is added by the user via routines `XPRS_msp_loadsol` and `XPRS_msp_readslxsol`.
`MSP_DUPLICATESOLUTIONSPOLICY` | Policy to use when handling storage of duplicate solutions.
`MSP_INCLUDEPROBNAMEINLOGGING` | Controls whether or not the MIP solution pool logging uses the problem name when a message references a problem.
`MSP_SOL_BITFIELDSUSR` | A user-definable bit map to be stored with a solution. This bit map can be used to define subsets of solutions returned by the `XPRS_msp_getsollist2` function.
`MSP_SOL_FEASTOL` | This is the tolerance on the value of integer, semi-continuous, partial and semi-continuos integer variables and SOS variables. If one of these is less than or equal to [`FEASTOL`](../../HTML/optimizer?scroll=FEASTOL) in absolute value, it is treated as zero.
`MSP_SOL_MIPTOL` | This is the tolerance within which a decision variable's value is considered to be integral.

#### MSP_DEFAULTUSERSOLFEASTOL

_**Description:**_    This is the tolerance on the value of integer, semi-continuous, partial and semi-continuos integer variables and SOS variables. If one of these is less than or equal to[`FEASTOL`](../../HTML/optimizer?scroll=FEASTOL)in absolute value, it is treated as zero.
 
_**Type:**_ Double

_**Default value:**_ 1.0E-06

#### MSP_DEFAULTUSERSOLMIPTOL

_**Description:**_    This is the tolerance within which a decision variable's value is considered to be integral. It is the default value for the tolerance`MSP_SOL_MIPTOL`when a solution is added by the user via routines`XPRS_msp_loadsol`and`XPRS_msp_readslxsol`.
 
_**Type:**_ Double

_**Default value:**_ 5.0E-06

#### MSP_DUPLICATESOLUTIONSPOLICY

_**Description:**_    Policy to use when handling storage of duplicate solutions.
 
_**Type:**_ Integer

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Keep all: All solutions are kept including duplicates.
 `1`| Continuous: All variables are compared with an exact match. Duplicate solutions are discarded.
 `2`| Discrete and continuous separate: Both the discrete component of a solution pair and the continuous solution variables are compared. The continuous variables are compared with an exact match. Duplicate solutions are discarded.
 `3`| Discrete only: Only the discrete component of a solution pair is compared. Duplicate solutions are discarded.

_**Default value:**_ 3

#### MSP_INCLUDEPROBNAMEINLOGGING

_**Description:**_    Controls whether or not the MIP solution pool logging uses the problem name when a message references a problem.
 
_**Type:**_ Integer

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| The problem name is not included.
 `1`| The problem name is included.

_**Default value:**_ 1

#### MSP_SOL_BITFIELDSUSR

_**Description:**_    A user-definable bit map to be stored with a solution. This bit map can be used to define subsets of solutions returned by the`XPRS_msp_getsollist2`function.
 
_**Type:**_ Integer

_**Default value:**_ 0

_**Affects routines:**_ `XPRS_msp_getintcontrolsol`,`XPRS_msp_setintcontrolsol`.

_**See also:**_
`XPRS_msp_getsollist2`.


#### MSP_SOL_FEASTOL

_**Description:**_    This is the tolerance on the value of integer, semi-continuous, partial and semi-continuos integer variables and SOS variables. If one of these is less than or equal to[`FEASTOL`](../../HTML/optimizer?scroll=FEASTOL)in absolute value, it is treated as zero.
 
_**Type:**_ Double

_**Default value:**_ 1.0E-06

#### MSP_SOL_MIPTOL

_**Description:**_    This is the tolerance within which a decision variable's value is considered to be integral.
 
_**Type:**_ Double

_**Default value:**_ 5.0E-06

### Chapter 4 MSP Attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`MSP_PRB_FEASIBLESOLS` | Number of feasible solutions for the problem.
`MSP_PRB_VALIDSOLS` | Number of solutions with the same number of columns as the problem.
`MSP_SOL_BITFIELDSSYS` | A bit map with fields containing the logical attribute values for the solution e.g., `MSP_SOL_ISREPROCESSEDUSERSOLUTION` and `MSP_SOL_ISUSERSOLUTION`.
`MSP_SOL_COLS` | Number of columns in the solution.
`MSP_SOL_ISREPROCESSEDUSERSOLUTION` | Whether or not the solution arises from a user solution \(i.e., passed in by the user via `XPRS_msp_loadsol` or `XPRS_msp_readslxsol`\) being loaded into an attached problem and the resulting "cleaned up" solution being loaded back into the MIP solution pool.
`MSP_SOL_ISUSERSOLUTION` | Whether or not the solution was passed in by the user \(via `XPRS_msp_loadsol` or `XPRS_msp_readslxsol`\) or whether the solution was loaded internally from an attached problem.
`MSP_SOL_NONZEROS` | Number of non-zeros in the solution.
`MSP_SOLPRB_INFCNT_BIN` | Number of binary variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_COLUMN` | Number of column bound infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_DELAYEDROW` | Number of delayed row infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_INT` | Number of integer variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_MIP` | Number of MIP infeasibilities that the solution has with respect to the problem.
`MSP_SOLPRB_INFCNT_PI` | Number of partial integer variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_PRIMAL` | Number of primal infeasibilities that the solution has with respect to the problem. This count includes the column bound infeasibilities and both the row and delayed row infeasibilities.
`MSP_SOLPRB_INFCNT_SC` | Number of semi-continuous variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_SET1` | Number of SOS1 set MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_SET2` | Number of SOS2 set MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_SI` | Number of semi-continuous integer variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFCNT_SLACK` | Number of rows of the problem that are violated for the solution.
`MSP_SOLPRB_INFEASCOUNT` | The sum of the MIP and primal infeasibility counts for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_BIN` | Maximum binary variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_COLUMN` | Maximum column bound infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_DELAYEDROW` | Maximum delayed row infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_INT` | Maximum integer variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_PI` | Maximum partial integer variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_SC` | Maximum semi-continuous variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_SET1` | Maximum variable value causing a SOS1 set MIP infeasibility.
`MSP_SOLPRB_INFMAX_SET2` | Maximum variable value causing a SOS2 set MIP infeasibility.
`MSP_SOLPRB_INFMAX_SI` | Maximum semi-continuous integer variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMAX_SLACK` | Maximum row infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_BIN` | Index of a column achieving the maximum binary variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_COLUMN` | Index of a column achieving the maximum column bound infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_DELAYEDROW` | Index of a delayed row achieving the maximum delayed row infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_INT` | Index of a column achieving the maximum integer variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_PI` | Index of a column achieving the maximum partial integer variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_SC` | Index of a column achieving the maximum semi-continuous variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_SET1` | Index of a set that has the maximum SOS1 set MIP infeasibility.
`MSP_SOLPRB_INFMXI_SET2` | Index of a set that has the maximum SOS2 set MIP infeasibility.
`MSP_SOLPRB_INFMXI_SI` | Index of a column achieving the maximum semi-continuous integer variable MIP infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFMXI_SLACK` | Index of a row achieving the maximum row infeasibility for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_BIN` | Sum of binary variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_COLUMN` | Sum of column bound infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_DELAYEDROW` | Sum of delayed row infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_INT` | Sum of integer variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_MIP` | Sum of MIP infeasibilities that the solution has with respect to the problem.
`MSP_SOLPRB_INFSUM_PI` | Sum of partial integer variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_PRIMAL` | Sum of primal infeasibilities that the solution has with respect to the problem. This sum includes the column bound infeasibilities and both the row and delayed row infeasibilities.
`MSP_SOLPRB_INFSUM_SC` | Sum of semi-continuous variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_SET1` | Sum of SOS1 set MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_SET2` | Sum of SOS2 set MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_SI` | Sum of semi-continuous integer variable MIP infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_INFSUM_SLACK` | Sum of row infeasibilities for the solution with respect to the problem.
`MSP_SOLPRB_OBJ` | Objective value of the solution with the problem.
`MSP_SOLUTIONS` | The number of solutions stored by the MIP solution pool.

#### MSP_PRB_FEASIBLESOLS

_**Description:**_    Number of feasible solutions for the problem.
 
_**Type:**_ Integer

#### MSP_PRB_VALIDSOLS

_**Description:**_    Number of solutions with the same number of columns as the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_BIN

_**Description:**_    Number of binary variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_COLUMN

_**Description:**_    Number of column bound infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_DELAYEDROW

_**Description:**_    Number of delayed row infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_INT

_**Description:**_    Number of integer variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_MIP

_**Description:**_    Number of MIP infeasibilities that the solution has with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_PI

_**Description:**_    Number of partial integer variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_PRIMAL

_**Description:**_    Number of primal infeasibilities that the solution has with respect to the problem. This count includes the column bound infeasibilities and both the row and delayed row infeasibilities.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_SC

_**Description:**_    Number of semi-continuous variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_SET1

_**Description:**_    Number of SOS1 set MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_SET2

_**Description:**_    Number of SOS2 set MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_SI

_**Description:**_    Number of semi-continuous integer variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFCNT_SLACK

_**Description:**_    Number of rows of the problem that are violated for the solution.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFEASCOUNT

_**Description:**_    The sum of the MIP and primal infeasibility counts for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMAX_BIN

_**Description:**_    Maximum binary variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_COLUMN

_**Description:**_    Maximum column bound infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_DELAYEDROW

_**Description:**_    Maximum delayed row infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_INT

_**Description:**_    Maximum integer variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_PI

_**Description:**_    Maximum partial integer variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_SC

_**Description:**_    Maximum semi-continuous variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_SET1

_**Description:**_    Maximum variable value causing a SOS1 set MIP infeasibility.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_SET2

_**Description:**_    Maximum variable value causing a SOS2 set MIP infeasibility.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_SI

_**Description:**_    Maximum semi-continuous integer variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMAX_SLACK

_**Description:**_    Maximum row infeasibility for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFMXI_BIN

_**Description:**_    Index of a column achieving the maximum binary variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_COLUMN

_**Description:**_    Index of a column achieving the maximum column bound infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_DELAYEDROW

_**Description:**_    Index of a delayed row achieving the maximum delayed row infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_INT

_**Description:**_    Index of a column achieving the maximum integer variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_PI

_**Description:**_    Index of a column achieving the maximum partial integer variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_SC

_**Description:**_    Index of a column achieving the maximum semi-continuous variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_SET1

_**Description:**_    Index of a set that has the maximum SOS1 set MIP infeasibility.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_SET2

_**Description:**_    Index of a set that has the maximum SOS2 set MIP infeasibility.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_SI

_**Description:**_    Index of a column achieving the maximum semi-continuous integer variable MIP infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFMXI_SLACK

_**Description:**_    Index of a row achieving the maximum row infeasibility for the solution with respect to the problem.
 
_**Type:**_ Integer

#### MSP_SOLPRB_INFSUM_BIN

_**Description:**_    Sum of binary variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_COLUMN

_**Description:**_    Sum of column bound infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_DELAYEDROW

_**Description:**_    Sum of delayed row infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_INT

_**Description:**_    Sum of integer variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_MIP

_**Description:**_    Sum of MIP infeasibilities that the solution has with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_PI

_**Description:**_    Sum of partial integer variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_PRIMAL

_**Description:**_    Sum of primal infeasibilities that the solution has with respect to the problem. This sum includes the column bound infeasibilities and both the row and delayed row infeasibilities.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_SC

_**Description:**_    Sum of semi-continuous variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_SET1

_**Description:**_    Sum of SOS1 set MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_SET2

_**Description:**_    Sum of SOS2 set MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_SI

_**Description:**_    Sum of semi-continuous integer variable MIP infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_INFSUM_SLACK

_**Description:**_    Sum of row infeasibilities for the solution with respect to the problem.
 
_**Type:**_ Double

#### MSP_SOLPRB_OBJ

_**Description:**_    Objective value of the solution with the problem.
 
_**Type:**_ Double

_**Note:**_
For infeasible solutions, the objective value returned is infinity.
Calling [`XPRSfixmipentities`](../../HTML/optimizer?scroll=XPRSfixmipentities) will invalidate a solution in the pool if any of the discrete variables in the solution are rounded and if this happens the objective will be returned as infinity.


#### MSP_SOLUTIONS

_**Description:**_    The number of solutions stored by the MIP solution pool.
 
_**Type:**_ Integer

#### MSP_SOL_BITFIELDSSYS

_**Description:**_    A bit map with fields containing the logical attribute values for the solution e.g.,`MSP_SOL_ISREPROCESSEDUSERSOLUTION`and`MSP_SOL_ISUSERSOLUTION`.
 
_**Type:**_ Integer

#### MSP_SOL_COLS

_**Description:**_    Number of columns in the solution.
 
_**Type:**_ Integer

#### MSP_SOL_ISREPROCESSEDUSERSOLUTION

_**Description:**_    Whether or not the solution arises from a user solution \(i.e., passed in by the user via`XPRS_msp_loadsol`or`XPRS_msp_readslxsol`\) being loaded into an attached problem and the resulting "cleaned up" solution being loaded back into the MIP solution pool.
 
_**Type:**_ Integer

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| The solution was not derived from a user solution i.e., it is a user solution or it is a solution found by an attached `XPRSprob`problem.
 `1`| The solution was derived from a user solution.

#### MSP_SOL_ISUSERSOLUTION

_**Description:**_    Whether or not the solution was passed in by the user \(via`XPRS_msp_loadsol`or`XPRS_msp_readslxsol`\) or whether the solution was loaded internally from an attached problem.
 
_**Type:**_ Integer

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| The solution was loaded internally from an attached problem.
 `1`| The solution was loaded by the user via`XPRS_msp_loadsol`or`XPRS_msp_readslxsol`.

#### MSP_SOL_NONZEROS

_**Description:**_    Number of non-zeros in the solution.
 
_**Type:**_ Integer

## Part B MIP Solution Enumerator


### Chapter 5 Introduction


#### Section 5.1 Overview


The MIP solution enumerator \( `XPRSmipsolenum`\) runs a customized MIP search on a user provided problem \( `XPRSprob`\). The search is customized such that nodes are not cut-off by bounding and integer solution nodes are branched. The MIP solution enumerator marshals the solutions found to storage in a user provided MIP solution pool \( `XPRSmipsolpool`\).

In general the MIP solution enumerator is useful for generating a set of solutions for a problem. In particular, the MIP solution enumerator can be used to generate the n-best solutions to a problem. The user will typically be interested in such a set when there are constraints and/or costs not reflected in the problem and the user wants a set of solutions from which a final solution can be selected that best meets the external constraints and objective.

#### Section 5.2 Applications: N-Best Solutions Example


A typical use of the MIP solution enumerator is to generate the set of n-best solutions. The following example shows how this can be done:-

```
#include <stdio.h>
#include "xprs.h"
#include "xprs_mse_defaulthandler.h"

int main(int argc, char **argv)
{
  XPRSprob prob;
  XPRSmipsolpool msp;
  XPRSmipsolenum mse;
  int nMaxSols;
  int i, j, nSols, nCols, iSolutionId, iSolutionIdStatus;
  double dObj, dSol;
  int iPresolveOps;
  const char *sProblem = argv[1];

  XPRSinit(NULL);
  XPRScreateprob(&prob);
  XPRSreadprob(prob, sProblem, "");

  XPRS_msp_create(&msp);

  XPRS_mse_create(&mse);

  XPRSgetintattrib(prob, XPRS_COLS, &nCols);

  /* Disable heuristics to avoid duplicate solutions being stored */
  XPRSsetintcontrol(prob, XPRS_HEUREMPHASIS, 0);

  XPRSgetintcontrol(prob, XPRS_PRESOLVEOPS, &iPresolveOps);  
  iPresolveOps &= ~(1 << 3); /* Disable dual reduction operations */
  iPresolveOps &= ~(1 << 5); /* Disable duplicate column removal  */
  XPRSsetintcontrol(prob, XPRS_PRESOLVEOPS, iPresolveOps);  

  /* Run the enumeration */
  nMaxSols = 10;
  XPRS_mse_maxim(mse, prob, msp, XPRS_mse_defaulthandler, NULL, &nMaxSols);

  /* Print out the solutions found */
  XPRS_mse_getintattrib(mse, XPRS_MSE_SOLUTIONS, &nSols);
  for(i = 1; i <= nSols; i++) {
    XPRS_mse_getsollist(mse, XPRS_MSE_METRIC_MIPOBJECT, i, i, &iSolutionId, NULL, NULL);
    XPRS_mse_getsolmetric(mse, iSolutionId, &iSolutionIdStatus, XPRS_MSE_METRIC_MIPOBJECT, &dObj);
    printf("--------\n%3i = %12.5f\n", i, dObj);
    for(j = 0; j < nCols; j++) {
      XPRS_msp_getsol(msp, iSolutionId, &iSolutionIdStatus, &dSol, j, j, NULL);
      printf("%3i = %12.5f\n", j, dSol);
    }
  }

  XPRS_msp_destroy(msp);
  XPRSdestroyprob(prob);
  XPRS_mse_destroy(mse);

  XPRSfree();
}

```


In the example we use the `XPRS_mse_defaulthandler` function to manage the storage of at most `nMaxSols` \( = 10\) solutions. The code for the `XPRS_mse_defaulthandler` callback is provided in the FICO Xpress Optimizer. Using the default control settings when a solution is found and there are `nMaxSols` \( = 10\) solutions stored the `XPRS_mse_defaulthandler` callback will either reject the current solution or delete the worst existing solution depending on their objective values \(when there is a tie the current solution is rejected\). In this way the MIP solution enumerator will generate the set of `` n-best solutions.

It is important to note that duplicate solutions can potentially be stored in the cases where the MIP solution pool contains initial solutions prior to the enumeration run or if heuristics are activated in the `XPRSprob`. In the example we have disabled heuristics and the MIP solution pool does not contain any solutions prior to the enumeration run so there is no need to check for duplicates. The management of duplicate solutions is left to the MIP solution pool functionality which is discussed in [Duplicate Solutions](#section5Subsection0).

It is also important to note that it is sometimes necessary to disable certain FICO Xpress Optimizer presolve operations \(i.e., setting the integer control `PRESOLVEOPS` in the example\) to avoid spurious deletion of solutions from the enumeration search space. This is discussed in the following section [Presolve considerations](#section11.1).

In the event that initial solutions are contained in the MIP solution pool prior to the enumeration run the MIP solution enumerator will load the set of feasible solutions \(with the same number of columns as the `XPRSprob`\) from the initial set of solutions as if they were found during the MIP search on the `XPRSprob`. Note that new versions of these solutions are created and the original versions are deleted from the MIP solution pool.

Once the enumeration run terminates the example demonstrates simple retrieval of the solution information. Note that the solution values are stored in the MIP solution pool and the metric information for the solutions is stored in the MIP solution enumerator.

#### Section 5.3 Presolve considerations


The default control settings of the FICO Xpress Optimizer presolver assume that the user is satisfied if the MIP search finds a single solution with the best objective. The choice of the default presolve settings attempts to improve the efficiency of this type of search by cutting off MIP solutions from the feasible region that are either degenerate \(i.e., that have equivalent representations with different feasible values of the variables\) or dominated \(i.e., that can be deduced to be worse than solutions contained in the remaining feasible region\) or symmetric to another solution. The user must take care to disable these default presolve operations when solutions may be removed from the enumeration search space that are of interest. Also, the user should be aware that disabling these presolve operations can significantly increase the enumeration runtime.

Presolve operations removing dominated MIP solutions are collectively referred to as dual reduction operations. To disable duplicate column detection the user must unset bit 5 of the integer control `PRESOLVEOPS`. To disable all dual reduction operations the user must unset bit 3 of `PRESOLVEOPS`. See the [Applications: N-Best Solutions Example](#section11) for an example of how to unset these bits.

To disable FICO Xpress Optimizer from removing symmetric solutions, set the `SYMMETRY` control to `0`.

#### Section 5.4 Basic customization


By customizing the controls for the `XPRS_mse_defaulthandler` callback \(i.e., setting `MSE_CALLBACKCULLSOLS_MIPOBJECT` and/or `MSE_CALLBACKCULLSOLS_DIVERSITY`\) the user can modify the behavior of the callback when the number of solutions exceeds the maximum. The user can delete p solutions based on the MIP objective values and then delete q of the remaining `nMaxSols - p` solutions based on the diversity metric \(see below\). The current solution will be rejected if it is no better than any of the solutions that were deleted. In this way the user has simple control of how the solution set is generated.

In addition to the MIP objective the MIP solution enumerator provides a metric for solutions based on the 'diversity' of the solution with respect to the other stored solutions. The diversity metric for a solution is the sum of difference metrics between the solution and the other stored solutions. By default the difference value between two solutions is calculated by the MIP solution enumerator using a simple difference metric that considers only the MIP entities in the solution. Note that for the MIP solution enumerator to calculate the diversity metrics a problem needs to be attached to the MIP solution pool \(see 'Duplicate solutions'\). This is because the discrete structure of the solution variables is required for the difference metric calculation. The user will typically attach to the MIP solution pool the `XPRSprob` to be used to run the enumeration. Finally, note that the user can provide their own difference metric calculation for solution pairs in a callback defined with a call to `XPRS_mse_setcbgetsolutiondiff` \(in this case there does not need to be a problem attached to the MIP solution pool\).

#### Section 5.5 Advanced customization


By providing a customized version of the `XPRS_mse_defaulthandler` the user can define a modified objective value for solutions. Typically this value reflects the 'true' objective of the solution in cases where the MIP objective does not completely model the user's problem. The modified objective value is stored with the solution and can be used to obtain a ranked order of solutions in the case where the user wishes to delete solutions based on this metric \(see `XPRS_mse_getcullchoice`\). Also with a customized callback the user is able to arbitrarily accept or reject the current solution. Typically the user will want to do this in cases where the constraints and/or objective of the MIP problem do not completely model the user's problem.

From the customized `XPRS_mse_defaulthandler` callback the user is able to set a return value that causes the MIP solution enumerator to set the cut-off for the search to the worst MIP objective of the active solutions. This can be useful to improve the run time of the enumeration. Note that the default `n-best` search uses this to improve the enumeration performance.

#### Section 5.6 Data Model


The following UML diagram outlines the relationships the `XPRSmipsolenum` has with some other data entities.



![ mseuml.png](Graphic/mseuml.png)

    
  **Figure 5.1:**  


Starting from the top left the diagram shows the `XPRSprob` referenced by the `XPRSmipsolenum` in the top middle. The `XPRSmipsolenum` references the `XPRSprob` only for the duration of the enumeration-run routines `XPRS_mse_minim`, `XPRS_mse_maxim` and `XPRS_mse_opt`. The `XPRSmipsolenum` sets certain controls on the `XPRSprob`, registers an internal callback to receive solutions found during the enumeration and calls the relevant optimization function to execute the enumeration.

Moving to the top right the diagram shows the `XPRSmipsolpool` referenced by the `XPRSmipsolenum`. The `XPRSmipsolenum` references the `XPRSmipsolpool` only for the duration of the enumeration-run routines \(in the same way as the `XPRSprob`\).

While running the enumeration the `XPRSmipsolenum` maintains storage of additional information for each solution found that cannot be stored by the `XPRSmipsolpool`. The additional information is the MIP objective value \( `MIPObject`\) of the solution, any user-defined objective function value \( `ModObject`\) for the solution and a diversity-metric \( `Diversity`\) for the solution that measures how different the solution is with respect to the other solutions in storage. As indicated by the dashed line in the diagram, the solution ID is used to link the information stored separately in the `XPRSmipsolenum` and the `XPRSmipsolpool`.

Since a parallel storage of solution information is required the `XPRSmipsolenum` marshals the storage of solutions to the `XPRSmipsolpool`. To do this the `XPRSmipsolenum` registers an internal callback with the `XPRSmipsolpool` to track when solutions are deleted by the user from the `XPRSmipsolpool`. It is also necessary that the `XPRSmipsolenum` loads the solutions found during the enumeration directly into the `XPRSmipsolpool` overriding the automatic loading of solutions from the `XPRSprob` to `XPRSmipsolpool` in the situation where the user has attached the `XPRSprob` to the `XPRSmipsolpool` prior to the enumeration run.

Once the enumeration run terminates the MIP solutions are stored in the `XPRSmipsolpool` and the additional information for the solutions is stored in the `XPRSmipsolenum`. At this point the solution information is linked only by the solution ID.

### Chapter 6 MSE Functions


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`XPRS_mse_addcbmsghandler` | Declares an output callback function, called every time a line of message text is output by the MIP solution enumerator. This callback function will be called in addition to any output callbacks already added by `XPRS_mse_addcbmsghandler`.
`XPRS_mse_create` | Sets up a new MIP solution enumerator object.
`XPRS_mse_defaulthandler` | A routine defined in xprs\_mse\_defaulthandler.h intended only to be passed as a callback into the enumeration-run routines `XPRS_mse_minim`, `XPRS_mse_maxim` and `XPRS_mse_opt`. When used to run an enumeration this routine is called each time a solution is found in the enumeration. This routine provides simple functionality to manage common strategies for keeping a 'good' set of solutions found during enumeration and controlling the enumeration run e.g., n-best solutions. The user may wish to base any customized version of the callback on the contents of this routine.
`XPRS_mse_destroy` | Destroys a MIP solution enumerator object and its resources. The object will generally be created by a call to the function `XPRS_mse_create`.
`XPRS_mse_getcbmsghandler` | Get the output callback function, as set by `XPRS_mse_setcbmsghandler`.
`XPRS_mse_getcullchoice` | Generates a list of solution ids for solutions recommended to be dropped assuming that the given number of solutions are required to be dropped and the solutions are to be compared with each other with respect to the given metric. This function also decides whether a given, new solution defined by its metric value \(or its solution values\) should also be dropped given that the returned list of solutions are recommended to be dropped.
`XPRS_mse_getdblattrib` | Provides read access to the values of double attributes associated with the MIP solution enumerator.
`XPRS_mse_getdblcontrol` | Retrieves the value of a given double control parameter.
`XPRS_mse_getintattrib` | Provides read access to the values of integer attributes associated with the MIP solution enumerator.
`XPRS_mse_getintcontrol` | Retrieves the value of a given integer control parameter.
`XPRS_mse_getlasterror` | Gets the last error message.
`XPRS_mse_getsolbasename` | Gets the name currently used as a prefix for solutions found during the enumeration run.
`XPRS_mse_getsollist` | Returns a list of solution ids of solutions found during the enumeration. The list is sorted by the value of some attribute of the solutions e.g., the MIP objective value.
`XPRS_mse_getsolmetric` | Gets the value of a metric for a solution.
`XPRS_mse_maxim (MSE_MAXIM)` | One of three routines to run the enumeration. This routine starts the enumeration run on the problem by calling [`XPRSmaxim`](../../HTML/optimizer?scroll=XPRSmaxim).
`XPRS_mse_minim (MSE_MINIM)` | One of three routines to run the enumeration. This routine starts the enumeration run on the problem by calling [`XPRSminim`](../../HTML/optimizer?scroll=XPRSminim).
`XPRS_mse_opt` | One of three routines to run the enumeration. This routine starts the enumeration run on the problem by calling [`XPRSmipoptimize`](../../HTML/optimizer?scroll=XPRSmipoptimize).
`XPRS_mse_removecbmsghandler` | Removes an output callback function previously added by `XPRS_mse_addcbmsghandler`. The specified callback function will no longer be called after it has been removed.
`XPRS_mse_setcbgetsolutiondiff` | Declares a user-defined solution difference calculation routine, called each time a new pair of solutions are required to have a difference metric calculated. This functionality is required when the `MSE_METRIC_DIVERSITY` metric is applied to the set of stored solutions with a call to `XPRS_mse_getcullchoice` and `XPRS_mse_getsolmetric`.
`XPRS_mse_setcbmsghandler` | Declares an output callback function, called every time a line of message text is output by a MIP solution enumerator object.
`XPRS_mse_setdblcontrol` | Sets the value of a given double control parameter.
`XPRS_mse_setintcontrol` | Sets the value of a given integer control parameter.
`XPRS_mse_setsolbasename` | Sets the name to be used as a prefix for solutions found during the enumeration run.

#### XPRS_mse_addcbmsghandler

_**Purpose:**_

   Declares an output callback function, called every time a line of message text is output by the MIP solution enumerator. This callback function will be called in addition to any output callbacks already added by `XPRS_mse_addcbmsghandler`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_addcbmsghandler(XPRSmipsolenum mse, int (XPRS_CC *f_msghandler) (XPRSobject vXPRSObject, void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void * p, int priority);
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`mse` | | The current MIP solution enumerator 
`f_msghandler` | | The callback function which takes six arguments, `vXPRSObject`, `vUserContext`, `vSystemThreadId`, `sMsg`, `iMsgType` and `iMsgNumber`. Use a NULL value to cancel a callback function. 
`vXPRSObject` | | The object sending the message. Use [`XPRSgetobjecttypename`](../../HTML/optimizer?scroll=XPRSgetobjecttypename) to get the name of the object type. 
`vUserContext` | | The user-defined object passed to the callback function. 
`vSystemThreadId` | | The system id of the thread sending the message caste to a void \*. 
`sMsg` | | A null terminated character array \(string\) containing the message, which may simply be a new line. When the callback is called for the first time `sMsg` will be a NULL pointer. 
`iMsgType` |  | Indicates the type of output message:
&nbsp; | `1` | information messages;
&nbsp; | `2` | \(not used\);
&nbsp; | `3` | warning messages;
&nbsp; | `4` | error messages.
&nbsp; |  | A negative value means the callback is being called for the first time.
`iMsgNumber` | | The number associated with the message. If the message is an error or a warning then you can look up the number in the section Optimizer Error and Warning Messages for advice on what it means and how to resolve the associated issue. 
`p` | | A user-defined object to be passed to the callback function. 
`priority` | | An integer that determines the order in which multiple output callbacks will be invoked. The callback added with a higher priority will be called before a callback with a lower priority. Set to 0 if not required. 

_**Further information:**_
To send messages to a log file the built in message handler `XPRSlogfilehandler`can be used. This can be done with:


```
XPRS_mse_addcbmsghandler(msp, XPRSlogfilehandler, "log.txt");

```



_**Related topics:**_
`XPRS_mse_removecbmsghandler`, [`XPRSgetobjecttypename`](../../HTML/optimizer?scroll=XPRSgetobjecttypename).

#### XPRS_mse_create

_**Purpose:**_

   Sets up a new MIP solution enumerator object.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_create(XPRSmipsolenum * mse)
`

_**Argument:**_

Name |  Description
---------- | ---------- 
`mse` | Pointer to a variable holding the new MIP solution enumerator. 

_**Further information:**_
1. Calls to `XPRS_mse_create` must be made after the call to [`XPRSinit`](../../HTML/optimizer?scroll=XPRSinit).
2. All MIP solution enumerators created using a call to `XPRS_mse_create` should be disposed of with a call to `XPRS_mse_destroy`.

_**Related topics:**_
[`XPRSinit`](../../HTML/optimizer?scroll=XPRSinit), `XPRS_mse_destroy`.

#### XPRS_mse_defaulthandler

_**Purpose:**_

   A routine defined in xprs\_mse\_defaulthandler.h intended only to be passed as a callback into the enumeration-run routines`XPRS_mse_minim`,`XPRS_mse_maxim`and`XPRS_mse_opt`. When used to run an enumeration this routine is called each time a solution is found in the enumeration. This routine provides simple functionality to manage common strategies for keeping a 'good' set of solutions found during enumeration and controlling the enumeration run e.g., n-best solutions. The user may wish to base any customized version of the callback on the contents of this routine.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_defaulthandler(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, void *ctx, int *const 
nMaxSols, const double *const x, const int nCols, const double dMipObject, double *const dModifiedObject, int *const 
bRejectSoln, int *const bUpdateMipAbsCutOffOnCurrentSet)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`prob` | The problem used to enumerate solutions. 
`msp` | The MIP solution pool used to store the solutions found during enumeration. 
`ctx` | The user-defined object passed into the enumeration-run routine that started this run \(i.e., `XPRS_mse_minim`, `XPRS_mse_maxim` or `XPRS_mse_opt`\). 
`nMaxSols` | The integer pointer passed into the enumeration-run routine that started this run \(i.e., `XPRS_mse_minim`, `XPRS_mse_maxim` or `XPRS_mse_opt`\). Note that this pointer is only used by the callback and is intended to store the maximum number of solutions the user is prepared to capture during the enumeration. 
`x` | A dense solution array of doubles containing the `nCols` solution values of the new solution. 
`nCols` | The number elements in `x`. This is the same as the column dimension of the problem when the enumeration was started. 
`dMipObject` | A double with the value of the MIP objective of the solution. 
`dModifiedObject` | A pointer to a double that contains, on entry to the routine, the MIP objective. The user can assign it a new value that reflects the 'true' objective of the solution in cases where the MIP objective does not completely model the user's problem. The returned value is stored as the `MSE_METRIC_MODOBJECT` metric of the solution. 
`bRejectSoln` | A pointer to an integer that is at value zero on entry to the routine. The solution will not be stored if the user returns this variable at a non-zero value. 
`bUpdateMipAbsCutOffOnCurrentSet` | A pointer to an integer that is at value zero on entry to the routine. If the user returns this variable with a non-zero value then the MIP solution enumerator will update the `MIPABSCUTOFF` of the problem to reflect the worst MIP objective of the stored solutions \(including the new solution if it is not rejected\). 

_**Further information:**_
This simple routine uses only four different API function calls. These calls are to the MIP solution enumerator routines`XPRS_mse_getcullchoice`,`XPRS_mse_getintattrib`and`XPRS_mse_getintcontrol`and the MIP solution pool routine`XPRS_msp_delsol`.

_**Related topics:**_
`XPRS_mse_minim`, `XPRS_mse_maxim`, `XPRS_mse_opt`, `XPRS_mse_getcullchoice`, `XPRS_mse_getintattrib`, `XPRS_mse_getintcontrol`, `XPRS_msp_delsol`.

#### XPRS_mse_destroy

_**Purpose:**_

   Destroys a MIP solution enumerator object and its resources. The object will generally be created by a call to the function`XPRS_mse_create`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_destroy(XPRSmipsolenum mse)
`

_**Argument:**_

Name |  Description
---------- | ---------- 
`mse` | MIP solution enumerator to be destroyed. 

_**Related topics:**_
`XPRS_mse_create`.

#### XPRS_mse_getcbmsghandler

_**Purpose:**_

   Get the output callback function, as set by`XPRS_mse_setcbmsghandler`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getcbmsghandler(XPRSmipsolenum mse, int (XPRS_CC **r_f_msghandler) (XPRSobject vXPRSObject, void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void **object);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator 
`r_f_msghandler` | Pointer to the memory where the callback function will be returned. 

_**Related topics:**_
`XPRS_mse_setcbmsghandler`.

#### XPRS_mse_getcullchoice

_**Purpose:**_

   Generates a list of solution ids for solutions recommended to be dropped assuming that the given number of solutions are required to be dropped and the solutions are to be compared with each other with respect to the given metric. This function also decides whether a given, new solution defined by its metric value \(or its solution values\) should also be dropped given that the returned list of solutions are recommended to be dropped.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getcullchoice(XPRSmipsolenum mse, int iMetricId, int cull_sol_id_list[], int nMaxSolsToCull, int * 
nSolsToCull, double dNewSolMetric, const double x[], int nCols, int * bRejectSoln)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iMetricId` | Id of metric for which the solutions should be compared e.g., the MIP objective value is used when `MSE_METRIC_MIPOBJECT` is passed down. A full list of all available metrics may be found in Chapter  _MSE Attributes_, or from the list in the `xprs.h` header file. 
`cull_sol_id_list` | Integer array where the solution ids will be returned. May be NULL if not required. 
`nMaxSolsToCull` | The maximum number of solutions required to be returned in `cull_sol_id_list`. 
`nSolsToCull` | Pointer to an integer where the number of solution ids that were written to `cull_sol_id_list` is returned. May be NULL if not required. 
`dNewSolMetric` | The metric value for the new solution for the metric identified by iMetricId. It is assumed that the user wishes to decide whether or not to keep the new solution given that solutions in the returned list `cull_sol_id_list` are recommended to be dropped. 
`x` | The solution values of the new solution. The diversity metric \( `MSE_METRIC_DIVERSITY`\) requires the solution values in order to calculate the new solution's metric with respect to the currently stored solutions. Other metrics simply use `dNewSolMetric` and do not require the solution values. May be NULL if not required. 
`nCols` | The number of columns in the solution array x. This must be the same as the number of \(initial\) columns in the enumeration problem. 
`bRejectSoln` | If this is passed down as NULL or if its value is non-zero then the given new solution is ignored. 

_**Further information:**_
1. If `cull_sol_id_list` is NULL or `nMaxSolsToCull` is zero or `nSolsToCull` is NULL \(i.e., a list of solution ids cannot be returned\) then the routine simply decides whether or not to reject the new solution based on the assumption that no currently existing solutions are to be dropped.
2. The user can drop solutions by calling `XPRS_msp_delsol` on the MIP solution pool being used by the enumerator.
3. To call the routine ignoring the new solution the user can pass the argument `bRejectSoln` as NULL. Note that if the new solution is not to be ignored then the user must pass `bRejectSoln` as non-NULL with an initial value of zero.

_**Related topics:**_
`XPRS_msp_delsol`.

#### XPRS_mse_getdblattrib

_**Purpose:**_

   Provides read access to the values of double attributes associated with the MIP solution enumerator.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getdblattrib(XPRSmipsolenum mse, int iAttribId, double * Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iAttribId ` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSE Attributes_, or from the list in the `xprs.h` header file. 
`Val ` | Pointer to an double where the value of the attribute will be returned. 

_**Related topics:**_
`XPRS_mse_getintattrib`.

#### XPRS_mse_getdblcontrol

_**Purpose:**_

   Retrieves the value of a given double control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getdblcontrol(XPRSmipsolenum mse, int iControlId, double * Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iControlId` | Id of control whose value is to be returned. A full list of all available controls may be found in Chapter  _MSE Controls_, or from the list in the `xprs.h` header file. 
`Val` | Pointer to a double where the value of the control will be returned. 

_**Related topics:**_
`XPRS_mse_getintcontrol`, `XPRS_mse_setdblcontrol`, `XPRS_mse_setintcontrol`.

#### XPRS_mse_getintattrib

_**Purpose:**_

   Provides read access to the values of integer attributes associated with the MIP solution enumerator.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getintattrib(XPRSmipsolenum mse, int iAttribId, int * Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iAttribId ` | Id of attribute whose value is to be returned. A full list of all available attributes may be found in Chapter  _MSE Attributes_, or from the list in the `xprs.h` header file. 
`Val ` | Pointer to an integer where the value of the attribute will be returned. 

_**Related topics:**_
`XPRS_mse_getdblattrib`.

#### XPRS_mse_getintcontrol

_**Purpose:**_

   Retrieves the value of a given integer control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getintcontrol(XPRSmipsolenum mse, int iControlId, int * Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iControlId` | Id of control whose value is to be returned. A full list of all available controls may be found in Chapter  _MSE Controls_, or from the list in the `xprs.h` header file. 
`Val` | Pointer to a integer where the value of the control will be returned. 

_**Related topics:**_
`XPRS_mse_getdblcontrol`, `XPRS_mse_setdblcontrol`, `XPRS_mse_setintcontrol`.

#### XPRS_mse_getlasterror

_**Purpose:**_

   Gets the last error message.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getlasterror(XPRSmipsolenum mse, int * iMsgNumber, char * msg, int iStringBufferBytes, int * 
iBytesInInternalString)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iMsgNumber ` | A pointer to an integer to return the number of the last error message. Can be NULL if not required. Refer to Chapter _9 of the Optimizer Reference Manual_ for a list of possible error numbers, the errors and warnings that they indicate, and advice on what they mean and how to resolve them. 
`msg` | A character buffer of length at least `iStringBufferBytes` to return the error message. Can be NULL if not required. 
`iStringBufferBytes` | The length of the `msg` buffer. 
`iBytesInInternalString` | A pointer to an integer to return the number of bytes required to store the error message. Can be NULL if not required. 

_**Related topics:**_
Chapter _9 of the Optimizer Reference Manual_, `XPRS_mse_setcbmsghandler`.

#### XPRS_mse_getsolbasename

_**Purpose:**_

   Gets the name currently used as a prefix for solutions found during the enumeration run.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getsolbasename(XPRSmipsolenum mse, char * sname, int iStringBufferBytes, int * 
iBytesInInternalString)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`sname ` | A character buffer of length at least `iStringBufferBytes` to return the name. Can be NULL if not required. 
`iStringBufferBytes ` | The length of the `sname` buffer. 
`iBytesInInternalString ` | A pointer to an integer to return the number of bytes required to store the name. Can be NULL if not required. 

_**Related topics:**_
`XPRS_mse_setsolbasename`.

#### XPRS_mse_getsollist

_**Purpose:**_

   Returns a list of solution ids of solutions found during the enumeration. The list is sorted by the value of some attribute of the solutions e.g., the MIP objective value.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getsollist(XPRSmipsolenum mse, int iMetricId, int iRankFirstIndex, int iRankLastIndex, int 
iSolutionIds[], int * nReturnedSolIds, int * nSols)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iMetricId ` | Id of the attribute whose value is used to rank the solution ids returned in the iSolutionIds array e.g., the MIP objective value is used when `MSE_METRIC_MIPOBJECT` is passed down. A full list of all available attributes may be found in Chapter  _MSE Attributes_, or from the list in the `xprs.h` header file. 
`iRankFirstIndex` | Index \(one-based\) in the rank order of solutions for which the associated solution's id number, if there is a solution at this index, is to be returned in the first element of array `iSolutionIds`. If `iRankLastIndex > iRankFirstIndex` then any subsequent solutions in the rank ordering are to have their solution ids written to the subsequent elements of `iSolutionIds`. 
`iRankLastIndex` | If `iSolutionIds` is non-NULL then at most `iRankLastIndex -  iRankFirstIndex + 1` solution ids will be written to `iSolutionIds`. There will be fewer solution ids written if `iRankLastIndex` is greater than the number of solutions registered in the MIP solution enumerator. 
`iSolutionIds` | Integer array where the solution ids will be returned. May be NULL if not required. 
`nReturnedSolIds` | Pointer to an integer where the number of solution ids that were available to be written is returned. This number will always be less than or equal to `iRankLastIndex - iRankFirstIndex + 1`. A value is returned for this parameter regardless of whether `iSolutionIds` is passed as NULL. May be NULL if not required. 
`nSols` | Pointer to an integer where the total number of solution ids that could possibly be written is returned. May be NULL if not required. 

_**Related topics:**_
`XPRS_mse_opt`, `XPRS_mse_minim`, `XPRS_mse_maxim`.

#### XPRS_mse_getsolmetric

_**Purpose:**_

   Gets the value of a metric for a solution.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_getsolmetric(XPRSmipsolenum mse, int iSolutionId, int * iSolutionIdStatus, int iMetricId, double * 
dMetric)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`mse` | | The current MIP solution enumerator. 
`iSolutionId` | | The id of the solution for which the metric is to be returned. 
`iSolutionIdStatus` |  | Pointer to an `int`where the status of the `iSolutionId`will be returned. The returned value is one of:
&nbsp; | `-2` | Solution id does not exist;
&nbsp; | `-1` | Solution with the given id is already deleted;
&nbsp; | `0` | Solution id was for an active solution.
`iMetricId ` | | Id of metric whose value is to be returned. A full list of all available metrics may be found in Chapter  _MSE Attributes_, or from the list in the `xprs.h` header file. 
`dMetric ` | | Pointer to a double where the value of the metric will be returned. 

_**Further information:**_
1. The user will obtain the solution id `iSolutionId` from interaction with the MIP solution enumerator via functions such as `XPRS_mse_getsollist` and `XPRS_mse_getcullchoice`.
2. If `iSolutionId` is passed in as less than or equal to zero then the routine returns the worst value of the metric for the current set of solutions.

_**Related topics:**_
`XPRS_mse_getsollist`, `XPRS_mse_getcullchoice`.

#### XPRS_mse_maxim  MSE_MAXIM

_**Purpose:**_

   One of three routines to run the enumeration. This routine starts the enumeration run on the problem by calling[`XPRSmaxim`](../../HTML/optimizer?scroll=XPRSmaxim).

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_maxim(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, int (XPRS_CC * 
f_mse_handler)(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, void *ctx, int * const nMaxSols, const double * 
const x, const int nCols, const double dMipObject, double * const dModifiedObject, int * const bRejectSoln, int * const 
bUpdateMipAbsCutOffOnCurrentSet), void * p, int * nMaxSols)
`

_**Further information:**_
See`XPRS_mse_minim`for details.

_**Related topics:**_
[`XPRSmaxim`](../../HTML/optimizer?scroll=XPRSmaxim), `XPRS_mse_minim`, `XPRS_mse_opt`.

#### XPRS_mse_minim  MSE_MINIM

_**Purpose:**_

   One of three routines to run the enumeration. This routine starts the enumeration run on the problem by calling[`XPRSminim`](../../HTML/optimizer?scroll=XPRSminim).

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_minim(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, int (XPRS_CC * 
f_mse_handler)(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, void *ctx, int * const nMaxSols, const double * 
const x, const int nCols, const double dMipObject, double * const dModifiedObject, int * const bRejectSoln, int * const 
bUpdateMipAbsCutOffOnCurrentSet), void * p, int * nMaxSols)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`prob` | The problem used to enumerate solutions. 
`msp` | The MIP solution pool used to store the solutions found during enumeration. 
`f_mse_handler` | A callback function to handle the event that a MIP feasible solution is found in the enumeration. 
`p` | The user-defined object to be passed to the callback function `f_mse_handler`. 
`nMaxSols` | A pointer to an integer to be passed to the callback function `f_mse_handler` \(and used only by the callback function\) that is intended to store the maximum number of solutions the user is prepared to capture during the enumeration. 

_**Further information:**_
1. Although the callback function `f_mse_handler` may be user-defined a simple version \( `XPRS_mse_defaulthandler`\) is provided in the FICO Xpress Optimizer that can be used to manage common strategies for keeping a 'good' set of solutions found during enumeration and controlling the enumeration run e.g., `n-best` solutions.
2. The value returned by callback function `f_mse_handler` is interpreted as error code, with zero indicating success.
3. Any MIP feasible solutions to `prob` stored in the MIP solution pool prior to the enumeration run are passed through the callback `f_mse_handler` as if they were found during the MIP search on the `prob`. Note that new versions of these solutions are created and the original versions are deleted from the MIP solution pool.
4. The integer pointer `nMaxSols` is used only by the callback function `f_mse_handler`.

_**Related topics:**_
[`XPRSminim`](../../HTML/optimizer?scroll=XPRSminim), `XPRS_mse_maxim`, `XPRS_mse_opt`, `XPRS_mse_defaulthandler`.

#### XPRS_mse_opt

_**Purpose:**_

   One of three routines to run the enumeration. This routine starts the enumeration run on the problem by calling[`XPRSmipoptimize`](../../HTML/optimizer?scroll=XPRSmipoptimize).

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_opt(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, int (XPRS_CC * 
f_mse_handler)(XPRSmipsolenum mse, XPRSprob prob, XPRSmipsolpool msp, void *ctx, int * const nMaxSols, const double * 
const x, const int nCols, const double dMipObject, double * const dModifiedObject, int * const bRejectSoln, int * const 
bUpdateMipAbsCutOffOnCurrentSet), void * p, int * nMaxSols)
`

_**Further information:**_
See`XPRS_mse_minim`for details.

_**Related topics:**_
[`XPRSmipoptimize`](../../HTML/optimizer?scroll=XPRSmipoptimize), `XPRS_mse_minim`, `XPRS_mse_maxim`.

#### XPRS_mse_removecbmsghandler

_**Purpose:**_

   Removes an output callback function previously added by `XPRS_mse_addcbmsghandler`. The specified callback function will no longer be called after it has been removed.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_removecbmsghandler(XPRSmipsolenum mse, int (XPRS_CC *f_msghandler) (XPRSobject vXPRSObject, void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void* object);
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator 
`f_msghandler` | The callback function to remove. If NULL then all output callback functions added with the given user-defined object value will be removed. 
`object` | The object value that the callback was added with. If NULL, then the object value will not be checked and all variable branching callbacks with the function pointer `f_chgbranch` will be removed. 

_**Related topics:**_
`XPRS_mse_addcbmsghandler`.

#### XPRS_mse_setcbgetsolutiondiff

_**Purpose:**_

   Declares a user-defined solution difference calculation routine, called each time a new pair of solutions are required to have a difference metric calculated. This functionality is required when the`MSE_METRIC_DIVERSITY`metric is applied to the set of stored solutions with a call to`XPRS_mse_getcullchoice`and`XPRS_mse_getsolmetric`.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_setcbgetsolutiondiff(XPRSmipsolenum mse, int (XPRS_CC * f_mse_getsolutiondiff)(XPRSmipsolenum 
mse, void * vContext, int nCols, int iSolutionId_1, int iElemCount_1, double dMipObj_1, const double * Vals_1, const int * 
iSparseIndices_1, int iSolutionId_2, int iElemCount_2, double dMipObj_2, const double * Vals_2, const int * iSparseIndices_2, 
double * dDiffMetric), void * p)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`f_mse_getsolutiondiff` | The callback function which takes 14 arguments, `mse`, `vContext`, `nCols`, `iSolutionId_1`, `iElemCount_1`, `dMipObj_1`, `Vals_1`, `iSparseIndices_1`, `iSolutionId_2`, `iElemCount_2`, `dMipObj_2`, `Vals_2`, `iSparseIndices_2` and `dDiffMetric`. Use a NULL value to cancel a callback function. 
`mse` | The current MIP solution enumerator. 
`vContext` | The user-defined object passed to the callback function. 
`nCols` | The number of columns in the solutions. This is the same as the column dimension of the problem when the enumeration was started. 
`iSolutionId_1` | The solution id of the first of the solution pair. This may be -1 in which case the solution has not yet be stored in the MIP solution pool. This happens when the user passes a new solution to `XPRS_mse_getcullchoice` using the diversity metric \( `MSE_METRIC_DIVERSITY`\). 
`iElemCount_1` | The number of non-zero elements in the first solution. 
`dMipObj_1` | The MIP objective value of the first solution. 
`Vals_1` | A sparse array of doubles of length `iElemCount_1` containing the first solution's solution values. 
`iSparseIndices_1` | A sparse array of integers of length `iElemCount_1` containing the first solution's column indices. 
`iSolutionId_2` | The solution id of the second of the solution pair. 
`iElemCount_2` | The number of non-zero elements in the second solution. 
`dMipObj_2` | The MIP objective value of the second solution. 
`Vals_2` | A sparse array of doubles of length `iElemCount_2` containing the second solution's solution values. 
`iSparseIndices_2` | A sparse array of integers of length `iElemCount_2` containing the second solution's column indices. 
`dDiffMetric` | A pointer to a double to return the metric of the difference between the two solutions. 
`p` | A user-defined object to be passed to the callback function. 

_**Further information:**_
1. If the user does not provide this callback function then the MIP solution enumerator uses a simple difference metric that considers only the MIP entities in the solution.
2. If the callback function returns nonzero then this is interpreted as an error and optimization is stopped.

_**Related topics:**_
`XPRS_mse_getcullchoice`, `XPRS_mse_getsolmetric`.

#### XPRS_mse_setcbmsghandler

_**Purpose:**_

   Declares an output callback function, called every time a line of message text is output by a MIP solution enumerator object.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_setcbmsghandler(XPRSmipsolenum mse, int (XPRS_CC *f_msghandler)(XPRSobject vXPRSObject, 
void * vUserContext, void * vSystemThreadId, const char * sMsg, int iMsgType, int iMsgNumber), void * p)
`

_**Arguments:**_

Name | Value |  Description
---------- | ---------- | ----------
`mse` | | The current MIP solution enumerator. 
`f_msghandler` | | The callback function which takes six arguments, `vXPRSObject`, `vUserContext`, `vSystemThreadId`, `sMsg`, `iMsgType` and `iMsgNumber`. Use a NULL value to cancel a callback function. 
`vXPRSObject` | | A generic pointer to the mse object sending the message. 
`vUserContext` | | The user-defined object passed to the callback function. 
`vSystemThreadId` | | The system id of the thread sending the message caste to a void \*. 
`sMsg` | | A null terminated character array \(string\) containing the message, which may simply be a new line. When the callback is called for the first time `sMsg` will be a NULL pointer. 
`iMsgType` |  | Indicates the type of output message:
&nbsp; | `1` | information messages;
&nbsp; | `2` | \(not used\);
&nbsp; | `3` | warning messages;
&nbsp; | `4` | error messages.
&nbsp; |  | A negative value means the callback is being called for the first time.
`iMsgNumber ` | | The number associated with the message. If the message is an error or a warning then you can look up the number in Chapter _9 of the Optimizer Reference Manual_ for advice on what it means and how to resolve the associated issue. 
`p` | | A user-defined object to be passed to the callback function. 

_**Further information:**_
To send all messages to a log file the built in message handler `XPRSlogfilehandler`can be used. This can be done with:


```
XPRS_mse_setcbmsghandler(mse, XPRSlogfilehandler, "log.txt");

```



_**Related topics:**_
None.

#### XPRS_mse_setdblcontrol

_**Purpose:**_

   Sets the value of a given double control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_setdblcontrol(XPRSmipsolenum mse, int iControlId, double Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iControlId` | Id of control whose value is to be set. A full list of all available controls may be found in Chapter  _MSE Controls_, or from the list in the `xprs.h` header file. 
`Val` | Value to which the control parameter is to be set. 

_**Related topics:**_
`XPRS_mse_getdblcontrol`, `XPRS_mse_setintcontrol`, `XPRS_mse_getintcontrol`.

#### XPRS_mse_setintcontrol

_**Purpose:**_

   Sets the value of a given integer control parameter.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_setintcontrol(XPRSmipsolenum mse, int iControlId, int Val)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`iControlId` | Id of control whose value is to be set. A full list of all available controls may be found in Chapter  _MSE Controls_, or from the list in the `xprs.h` header file. 
`Val` | Value to which the control parameter is to be set. 

_**Related topics:**_
`XPRS_mse_getintcontrol`, `XPRS_mse_setdblcontrol`, `XPRS_mse_getdblcontrol`.

#### XPRS_mse_setsolbasename

_**Purpose:**_

   Sets the name to be used as a prefix for solutions found during the enumeration run.

_**Synopsis:**_

   `
int XPRS_CC XPRS_mse_setsolbasename(XPRSmipsolenum mse, const char * sSolutionBaseName)
`

_**Arguments:**_

Name |  Description
---------- | ---------- 
`mse` | The current MIP solution enumerator. 
`sSolutionBaseName` | A null terminated string containing the name to use as a prefix for the solution names. 

_**Related topics:**_
`XPRS_mse_getsolbasename`.

### Chapter 7 MSE Controls


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`MSE_CALLBACKCULLSOLS_DIVERSITY` | This control is used only by the callback passed to the enumeration-run routines `XPRS_mse_minim`, `XPRS_mse_maxim` and `XPRS_mse_opt`. If the user passes the default callback `XPRS_mse_defaulthandler` then the control is used to decide how many solutions to discard based on the diversity metric values. See `XPRS_mse_defaulthandler` for details of how the control is used. If the user provides a customized version of `XPRS_mse_defaulthandler` to use in the enumeration-run then the user is free to interpret this control value.
`MSE_CALLBACKCULLSOLS_MIPOBJECT` | This control is used only by the callback passed to the enumeration-run routines XPRS\_mse\_minum, `XPRS_mse_maxim` and `XPRS_mse_opt`. If the user passes the default callback `XPRS_mse_defaulthandler` then the control is used to decide how many solutions to discard based on the MIP objective values. See `XPRS_mse_defaulthandler` for details of how the control is used. If the user provides a customized version of `XPRS_mse_defaulthandler` to use in the enumeration-run then the user is free to interpret this control value.
`MSE_CALLBACKCULLSOLS_MODOBJECT` | This control is used only by the callback passed to the enumeration-run routines `XPRS_mse_minim`, `XPRS_mse_maxim` and `XPRS_mse_opt`. If the user passes the default callback `XPRS_mse_defaulthandler` then the control is used to decide how many solutions to discard based on the user's modified objective values. See `XPRS_mse_defaulthandler` for details of how the control is used. If the user provides a customized version of `XPRS_mse_defaulthandler` to use in the enumeration-run then the user is free to interpret this control value.
`MSE_OPTIMIZEDIVERSITY` | Controls whether or not the values returned by `XPRS_mse_getcullchoice` for the diversity metric are defined by simply sorting the diversity values or if an optimization-based heuristic is to be used.
`MSE_OUTPUTTOL` | Tolerance on print values.

#### MSE_CALLBACKCULLSOLS_DIVERSITY

_**Description:**_    This control is used only by the callback passed to the enumeration-run routines`XPRS_mse_minim`,`XPRS_mse_maxim`and`XPRS_mse_opt`. If the user passes the default callback`XPRS_mse_defaulthandler`then the control is used to decide how many solutions to discard based on the diversity metric values. See`XPRS_mse_defaulthandler`for details of how the control is used. If the user provides a customized version of`XPRS_mse_defaulthandler`to use in the enumeration-run then the user is free to interpret this control value.
 
_**Type:**_ Integer

_**Default value:**_ -1

_**Affects routines:**_ `XPRS_msp_getintcontrol`,`XPRS_msp_setintcontrol`.

_**See also:**_
`MSE_METRIC_DIVERSITY`


#### MSE_CALLBACKCULLSOLS_MIPOBJECT

_**Description:**_    This control is used only by the callback passed to the enumeration-run routines XPRS\_mse\_minum,`XPRS_mse_maxim`and`XPRS_mse_opt`. If the user passes the default callback`XPRS_mse_defaulthandler`then the control is used to decide how many solutions to discard based on the MIP objective values. See`XPRS_mse_defaulthandler`for details of how the control is used. If the user provides a customized version of`XPRS_mse_defaulthandler`to use in the enumeration-run then the user is free to interpret this control value.
 
_**Type:**_ Integer

_**Default value:**_ -1

_**Affects routines:**_ `XPRS_msp_getintcontrol`,`XPRS_msp_setintcontrol`

_**See also:**_
`XPRS_mse_defaulthandler`, `XPRS_mse_getcullchoice`, `MSE_METRIC_MODOBJECT`.


#### MSE_CALLBACKCULLSOLS_MODOBJECT

_**Description:**_    This control is used only by the callback passed to the enumeration-run routines`XPRS_mse_minim`,`XPRS_mse_maxim`and`XPRS_mse_opt`. If the user passes the default callback`XPRS_mse_defaulthandler`then the control is used to decide how many solutions to discard based on the user's modified objective values. See`XPRS_mse_defaulthandler`for details of how the control is used. If the user provides a customized version of`XPRS_mse_defaulthandler`to use in the enumeration-run then the user is free to interpret this control value.
 
_**Type:**_ Integer

_**Default value:**_ -1

#### MSE_OPTIMIZEDIVERSITY

_**Description:**_    Controls whether or not the values returned by`XPRS_mse_getcullchoice`for the diversity metric are defined by simply sorting the diversity values or if an optimization-based heuristic is to be used.
 
_**Type:**_ Integer

_**Values:**_

_Value_ | _Meaning_
---------- | ----------
 `0`| Sorting is used.
 `1`| An optimization-based heuristic is used.

_**Default value:**_ 0

_**Affects routines:**_ `XPRS_msp_getintcontrol`,`XPRS_msp_setintcontrol`

_**See also:**_
`MSE_METRIC_DIVERSITY`, `XPRS_mse_getcullchoice`.


#### MSE_OUTPUTTOL

_**Description:**_    Tolerance on print values.
 
_**Type:**_ Double

_**Default value:**_ 1.0E-05

### Chapter 8 MSE Attributes


_Name_ | _Description_ | _Topics_ 
---------- | ---------- | ---------- 
`MSE_DIVERSITYSUM` | Sum of diversity metrics for the current set of solutions.
`MSE_METRIC_DIVERSITY` | The diversity metric for a solution is the sum of difference metrics between the solution and all others in the current set. The difference value between two solutions is either calculated internally by the MIP solution enumerator \(using a simple difference metric that considers only the MIP entities in the solution\) or else by the user in a callback defined with a call to `XPRS_mse_setcbgetsolutiondiff`.
`MSE_METRIC_MIPOBJECT` | MIP objective value.
`MSE_METRIC_MODOBJECT` | User-defined modified objective. The user can assign a solution with an objective value that reflects the 'true' objective of the solution in cases where the MIP objective does not completely model the user's problem. The user needs to return this value from a callback passed to the enumeration-run routines `XPRS_mse_minim`, `XPRS_mse_maxim` and `XPRS_mse_opt`. This routine will be some customized version of the `XPRS_mse_defaulthandler` routine provided with the FICO Xpress Optimizer.
`MSE_SOLUTIONS` | The number of solutions found and currently stored by the MIP solution enumerator.

#### MSE_DIVERSITYSUM

_**Description:**_    Sum of diversity metrics for the current set of solutions.
 
_**Type:**_ Double

_**Set by routines:**_ `XPRS_msp_getdblattrib`

_**See also:**_
`MSE_METRIC_DIVERSITY`


#### MSE_METRIC_DIVERSITY

_**Description:**_    The diversity metric for a solution is the sum of difference metrics between the solution and all others in the current set. The difference value between two solutions is either calculated internally by the MIP solution enumerator \(using a simple difference metric that considers only the MIP entities in the solution\) or else by the user in a callback defined with a call to`XPRS_mse_setcbgetsolutiondiff`.
 
_**Type:**_ Double

_**Set by routines:**_ `XPRS_mse_getsolmetric`

_**See also:**_
`XPRS_mse_setcbgetsolutiondiff`


#### MSE_METRIC_MIPOBJECT

_**Description:**_    MIP objective value.
 
_**Type:**_ Double

#### MSE_METRIC_MODOBJECT

_**Description:**_    User-defined modified objective. The user can assign a solution with an objective value that reflects the 'true' objective of the solution in cases where the MIP objective does not completely model the user's problem. The user needs to return this value from a callback passed to the enumeration-run routines`XPRS_mse_minim`,`XPRS_mse_maxim`and`XPRS_mse_opt`. This routine will be some customized version of the`XPRS_mse_defaulthandler`routine provided with the FICO Xpress Optimizer.
 
_**Type:**_ Double

_**Set by routines:**_ `XPRS_mse_getsolmetric`

_**See also:**_
`XPRS_mse_defaulthandler`, `XPRS_mse_minim`, `XPRS_mse_maxim`, `XPRS_mse_opt`.


#### MSE_SOLUTIONS

_**Description:**_    The number of solutions found and currently stored by the MIP solution enumerator.
 
_**Type:**_ Integer

_**Set by routines:**_ `XPRS_msp_getintattrib`

_**See also:**_
`XPRS_mse_defaulthandler`


## Part C Appendix


### Chapter 9 Error codes


Following an error exit from a function call to the MIP solution pool or the MIP solution enumerator library users may access the error code and a short string description of the error using the functions `XPRS_msp_getlasterror` or `XPRS_mse_getlasterror`. The following sections list the error codes returned by calls to the MIP solution pool and MIP solution enumerator functions. The main Optimizer Reference manual contains the list of error codes returned by the rest of the API.



#### Section 9.1 MIP Solution Pool errors

 * __800__   __*First index outside bounds:<col\_index>not in \[0,<num\_cols>- 1\]*__
   The index col\_index of the first column passed to `XPRS_msp_getsol` is outside the range \[0,< num\_cols> - 1\]
 * __801__   __*First index greater than last*__
   The index of the first column passed to `XPRS_msp_getsol` is greater than the index of the last column.
 * __802__   __*Attempt to attach problem more than one XPRSmipsolpool: Attach failed*__
   A problem cannot be attached to more than one MIP solution pool.
 * __804__   __*Unable to check if loaded sol is dupld: No MIP model avail*__
   A check if the solution being loaded is a duplicate of an existing solution cannot be made since no MIP model is available. No model is available because no problem has been attached to the MIP solution pool.
 * __805__   __*Unable to check if loaded sol is dupld: Memory allocation failure*__
   A check if the solution being loaded is a duplicate of an existing solution failed because of a memory allocation failure.
 * __806__   __*Unable to check if loaded sol is dupld: Incompat src prob*__
   A check if the solution being loaded is a duplicate of an existing solution cannot be made because the problem from which the solution originates does not match the MIP model used for duplicate checking.
 * __807__   __*Unable to check if loaded sol is dupld: MIP model unreliable*__
   A check if the solution being loaded is a duplicate of an existing solution cannot be made because a required update of the MIP model could not be made reliably.
 * __808__   __*Unable to check if loaded sol is dupld: MIP model reqd but inaccessible*__
   A check if the solution being loaded is a duplicate of an existing solution cannot be made because a required update of the MIP model could not be made.
 * __809__   __*Duplicate sol chck may not work: MIP model inaccessible in attaching prob*__
   A check if the solution being loaded is a duplicate of an existing solution cannot be made because a required capture of the MIP model could not be made from the problem being attached.
 * __810__   __*Destroying XPRSmipsolpool with problems still attached: Probs detached automatically*__
   The MIP solution pool is being destroyed and problems are still attached. This should be ok although the user should be aware. This message can be avoided by detaching the attached problems before destroying the MIP solution pool.
 * __812__   __*Compl duplicate sol chck: Failed*__
   A reset operation for the duplicate solution information failed. The duplicate solution checking may now not work reliably.
 * __814__   __*Failed to capture solution information*__
   Failure calculating the information for a solution with respect to a problem.
 * __815__   __*Failed to generate solution check sum*__
   A check of the problem state information failed when trying to calculate a check sum.
 * __816__   __*Failed to capture solution*__
   An unexpected failure when attempting to capture a solution.
 * __817__   __*Failure in internal event registration*__
   An object failed to register to receive system events.
 * __818__   __*Failure in internal event deregistration*__
   An object failed to deregister the receipt of system events.
 * __821__   __*Unrecoverable memory allocation failure*__
   A call made by the user failed because of a memory allocation failure.
 * __822__   __*Recoverable memory allocation failure:<operation\_attempted>*__
   A memory allocation failed when attempting the operation< operation\_attempted>. The system may still continue to function normally.
 * __826__   __*Soln col count does not match prob:<prob\_id\_string>:<solution\_id>*__
   The numbers of columns of solution< solution\_id> and of problem< prob\_id\_string> are required to be the equal \(but they are not\).
 * __827__   __*Soln is deleted and no longer available:<solution\_id>*__
   The user has attempted to access information for the solution with id< solution\_id> but the solution has been deleted.
 * __829__   __*Soln id does not exist:<solution\_id>*__
   The user has attempted to access information for the solution with id< solution\_id> but the id is for a solution that does not exist.
 * __830__   __*Unable to make a reliable list of sols for prob:<prob\_id\_string>: Unable to access prob state*__
   An attempt to make a list of solutions that relate to problem< prob\_id\_string> failed because state information of the problem could not be reliably accessed.
 * __831__   __*Unrecognized attribute id<attribute\_id>: Solutions will not be sorted*__
   The user seems to want a list of solutions sorted by some attribute but the attribute id is not recognized.
 * __835__   __*Column count does not match prob:<num\_solution\_cols>:<num\_prob\_cols>*__
   The numbers of columns of a given solution vector and of a given problem are required to be the equal \(but they are not\).
 * __836__   __*Failure writing solution to file:<file\_name>*__
   An unexpected failure was encountered writing solution\(s\) to file< file\_name>.
 * __837__   __*Failure opening file for writing:<file\_name>*__
   An unexpected failure was encountered opening file< file\_name> for writing.
 * __838__   __*Failure opening file for reading:<file\_name>*__
   An unexpected failure was encountered opening file< file\_name> for reading.
 * __839__   __*Loading sol failed :<prob\_id\_string>: id=<solution\_id><message>*__
   A failure occurred when loading solution< solution\_id> into problem< prob\_id\_string>. The failure is described in string< message>.
 * __842__   __*Loading sol interrupted:<prob\_id\_string>: id=<solution\_id>*__
   Loading was interrupted of solution< solution\_id> into problem< prob\_id\_string>.
 * __851__   __*Unrecognized duplicate solution policy id:<policy\_id>*__
   The user has attempted to set an unrecognized value< policy\_id> for the control `MSP_DUPLICATESOLUTIONSPOLICY`.
 * __852__   __*Reading solution skipped: \`<solution\_name>'*__
   The solution named< solution\_name> was skipped while reading solutions from file. A previous message describes why the solution could not be read.
 * __853__   __*Error detected in debug duplicate solution check:<message>*__
   A rigorous duplicate solution checking routine found an anomaly described in< message>.
 * __855__   __*Changing<tolerance\_name>for solution \`<solution\_name>' captured from problem:<system\_tol\_value>-><user\_tol\_value>*__
   A warning that the user is changing the tolerance< tolerance\_name> \(MIPTOL or FEASTOL\) for a solution from the value it was set to by the system< system\_tol\_value> to a different value< user\_tol\_value>.
 * __859__   __*No solutions written*__
   No solutions were written in a call to `XPRS_msp_writeslxsol`.
 * __868__   __*<operation\_name>is only allowed for attached problems*__
   The operation< operation\_name> is only allowed for problems attached to the MIP solution pool.
 * __869__   __*Soln is deleted and no longer available:<solution\_id>*__
   The user has attempted to access information for the solution with id< solution\_id> but the solution seems to have been deleted.
 * __870__   __*Soln id does not exist:<solution\_id>*__
   The user has attempted to access information for the solution with id< solution\_id> but the id is for a solution that has not yet been encountered.
 * __871__   __*Unrecoverable memory allocation failure*__
   A call made by the user failed because of a memory allocation failure.
 * __874__   __*Unrecognized solution metric id:<metric\_id>*__
   The metric id< metric\_id> passed by the user is unrecognized.
 * __875__   __*No solutions available*__
   The user is attempting to access information about the stored solutions but the solution storage is empty.
 * __876__   __*Enumerator is already running*__
   The user is attempting to run the enumeration while the enumeration is already running.
 * __875__   __*Failed to access XPRSmipsolpool state:<access\_operation>*__
   The MIP solution enumerator failed accessing the MIP solution pool state with access operation< access\_operation>.
 * __878__   __*Failed to access XPRSprob state:<access\_operation>*__
   The MIP solution enumerator failed accessing the problem state with access operation< access\_operation>.
 * __879__   __*Failed to allocate memory*__
   The MIP solution enumerator failed to allocate memory.
 * __882__   __*Missing required arguments for running enumerator*__
   Arguments passed to the enumeration-run routine \(e.g., XPRS\_mse\_minim\) were required to be non-NULL but were passed as NULL.
 * __883__   __*Problem no longer has the same number of columns*__
   The column dimension of the problem used by the MIP solution enumerator was changed by user.
 * __885__   __*Failure storing solution with memory allocation failure*__
   A memory allocation failure meant that a solution could not be captured.
 * __886__   __*Failure storing solution\(s\) with failed access to XPRSmipsolpool state:<access\_operation>*__
   A solution could not be captured because of a failure accessing the state of the MIP solution pool with access operation< access\_operation>.
 * __887__   __*Failure storing solution\(s\) with failed access to XPRSprob state:<access\_operation>*__
   A solution could not be captured because of a failure accessing the state of the problem with access operation< access\_operation>.
 * __1000__   __*Invalid parameter access :<error\_message>\(<routine\_name>\)*__
   Access to a parameter with a call to routine< routine\_name> failed because of error described in< error\_message>.
 * __1006__   __*Failed to capture solution information from problem*__
   Failure calculating the information for a solution with respect to a problem.
 * __1012__   __*Problem<prob\_id\_string>detached unexpectedly*__
   A problem< prob\_id\_string> attached to the MIP solution pool was unexpectedly detached by the user.
 * __1013__   __*Cannot attach thread problem to MIP solution pool*__
   The user has attempted to attach an internal problem being solved by the parallel MIP search to a MIP solution pool.
 * __1014__   __*Column count mismatch:<num\_solution\_cols>\!=<num\_row\_vector\_cols>*__
   A row vector of length< num\_row\_vector\_cols> passed to the MIP solution pool for evaluation against a solution does not contain the same number of columns as the solution< num\_solution\_cols>.

#### Section 9.2 MIP Solution Enumerator errors

 * __869__   __*Soln is deleted and no longer available:<solution\_id>*__
   The user has attempted to access information for the solution with id< solution\_id> but the solution seems to have been deleted.
 * __870__   __*Soln id does not exist:<solution\_id>*__
   The user has attempted to access information for the solution with id< solution\_id> but the id is for a solution that has not yet been encountered.
 * __871__   __*Unrecoverable memory allocation failure*__
   A call made by the user failed because of a memory allocation failure.
 * __874__   __*Unrecognized solution metric id:<metric\_id>*__
   The metric id< metric\_id> passed by the user is unrecognized.
 * __875__   __*No solutions available*__
   The user is attempting to access information about the stored solutions but the solution storage is empty.
 * __876__   __*Enumerator is already running*__
   The user is attempting to run the enumeration while the enumeration is already running.
 * __877__   __*Failed to access XPRSmipsolpool state:<access\_operation>*__
   The MIP solution enumerator failed accessing the MIP solution pool state with access operation< access\_operation>.
 * __878__   __*Failed to access XPRSprob state:<access\_operation>*__
   The MIP solution enumerator failed accessing the problem state with access operation< access\_operation>.
 * __879__   __*Failed to allocate memory*__
   The MIP solution enumerator failed to allocate memory.
 * __882__   __*Missing required arguments for running enumerator*__
   Arguments passed to the enumeration-run routine \(e.g., `XPRS_mse_minim`\) were required to be non-NULL but were passed as NULL.
 * __883__   __*Problem no longer has the same number of columns*__
   The column dimension of the problem used by the MIP solution enumerator was changed by user.
 * __885__   __*Failure storing solution with memory allocation failure*__
   A memory allocation failure meant that a solution could not be captured.
 * __886__   __*Failure storing solution\(s\) with failed access to `XPRSmipsolpool`state:<access\_operation>*__
   A solution could not be captured because of a failure accessing the state of the MIP solution pool with access operation< access\_operation>.
 * __887__   __*Failure storing solution\(s\) with failed access to XPRSprob state:<access\_operation>*__
   A solution could not be captured because of a failure accessing the state of the problem with access operation< access\_operation>.
 * __1000__   __*Invalid parameter access :<error\_message>\(<routine\_name>\)*__
   Access to a parameter with a call to routine< routine\_name> failed because of error described in< error\_message>.
 * __1007__   __*Unexpected failure evaluating solution difference metric*__
   An unexpected failure occurred while evaluating difference metrics for solutions.
 * __1008__   __*Solution difference metric value is reserved : -1.7976931348623158e+308*__
   The double value -1.7976931348623158e+308 to be assigned for a difference metric between two solutions is reserved by the system.
 * __1009__   __*Unexpected failure evaluating solution differences*__
   An unexpected error occurred while evaluating the diversity of the stored solutions.
 * __1010__   __*User signaled failure in solution difference metric callback*__
   The user signaled a failure in the callback defined by a call to `XPRS_mse_setcbgetsolutiondiff`.
 * __1011__   __*Cannot evaluate diversity of new solution: Column number mismatch:<num\_solution\_cols>\!=<num\_prob\_cols>*__
   The solution passed down to `XPRS_mse_getcullchoice` for the diversity metric does not have the same number of columns as the problem used in the enumeration run.
 * __1015__   __*Destroying while enumeration running*__
   The user is attempting to destroy the MIP solution enumerator while it is running.
 * __1016__   __*Failed to update MIPABSCUTOFF*__
   The MIP solution enumerator failed to update the `MIPABSCUTOFF` on the problem running the enumeration.
 * __1017__   __*Unable to check if loaded sol is dupld: Sol cols \(num\_solution\_cols\) does not match MIP model \(num\_global\_model\_cols\)*__
   A check if the solution being loaded is a duplicate of an existing solution cannot be made because the solution array does not have the same number of columns as the MIP model used for duplicate checking.
 * __1018__   __*MIP model unavailable for diversity: <reason\_string>*__
   The MIP solution enumerator is setup such that internal solution diversity calculations may be made although this will fail because it requires that an appropriate problem is attached to the MIP solution pool \(see <reason\_string> for details\).
 * __1019__   __*Cannot handle diversity: <reason\_string>*__
   The user has called a function that requires solution diversity calculations to be made internally by the MIP solution enumerator and this has failed because it requires that an appropriate problem is attached to the MIP solution pool \(see <reason\_string> for details\).
