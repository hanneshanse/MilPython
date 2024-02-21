from scipy.sparse import vstack
import gurobipy as gp
import numpy as np
from .lpObject import LPObject
from .lpStateVar import LPStateVar,LPStateVar_timedep,LPStateVar_add
from .lpInputdata import LPInputdata
from scipy.sparse import coo_matrix, csc_matrix, vstack
from .tools import Solver,Obj

class LPMain:
    '''
    (Abstract) main class for running the linear optimization
    Here the equation systems are prepared for optimization and the optimization is executed
    '''
    def __init__(self,inputdata:LPInputdata):
        """This is the init-fun of the abstract class LPMain. This code has to be run by inheriting class by >LPMain().__init__(self,inputdata)"""        
        if self.__class__.__name__ == 'LPMain':
            raise Exception('This is an abstract class. Please only instantiate objects of the inheriting class.')
        self.Aeq = None
        self.beq = []
        self.senses = []
        self.inputdata = inputdata
        self.make_stateVarLst()
        self.def_pos()
        self.def_bounds()
        self.def_vtypes()
        self.def_eqs()
        self.init_targetfun()
        self.def_targetfun()
    
    def def_eqs(self):
        """Defines the equation system. Calls the def_equation function for all LPObjects in self.obj_lst and extends Aeq,beq and senses by the equations of the objects"""        
        self.obj_lst[0].def_equations()
        self.Aeq,self.beq,self.senses = self.obj_lst[0].return_eqs()
        for obj in self.obj_lst[1:]:
            obj.def_equations()
            self.extend_matrices(obj.return_eqs())
    
    def extend_matrices(self,eq_lst):
        '''Appends equations from other classes to the equation system of the LPMain object'''
        self.Aeq = vstack([self.Aeq,eq_lst[0]])
        self.beq.extend(eq_lst[1])
        self.senses.extend(eq_lst[2])
    
    def make_stateVarLst(self):
        '''
        Creates lists containing all status variables of all objects belonging to the system.
        Divided into time-dependent variables and additional variables
        '''
        self.stateVars:list[LPStateVar]=[]
        for obj in self.obj_lst:
            self.stateVars.extend(obj.getStateVars())
        self.stateVars_timedep = [var for var in self.stateVars if isinstance(var,LPStateVar_timedep)]
        self.stateVars_add = [var for var in self.stateVars if isinstance(var,LPStateVar_add)]
           
    def def_pos(self):
        '''
        Defines the positions of all state variables within the Aeq matrix.
        - For time-dependent variables, the position of the variable is saved for the first time step
        - Additional variables are at the end of the list
        '''
        idx_pos=0
        for var in self.stateVars_timedep:
            var.pos = idx_pos
            idx_pos += 1
        idx_pos = len(self.stateVars_timedep)*self.inputdata.steps
        for var in self.stateVars_add:
            var.pos = idx_pos
            idx_pos += 1        
        self.inputdata.num_vars=idx_pos
        self.inputdata.num_vars_timedep=len(self.stateVars_timedep)

    def def_bounds(self):
        '''
        Creates lists containing the upper and lower limits of all state variables.
        The order corresponds to the positions assigned to the variables
        '''
        num_vars_timedep = len(self.stateVars_timedep)*self.inputdata.steps
        num_vars_add = len(self.stateVars_add)
        num_vars = num_vars_timedep + num_vars_add
        self.lb=np.zeros(num_vars)
        self.ub=np.zeros(num_vars)
        
        lb_timedep = []
        ub_timedep = []
        for var in self.stateVars_timedep:
            lb_timedep.append(var.lb)   
            ub_timedep.append(var.ub)   
        self.lb[0:num_vars_timedep] = lb_timedep*self.inputdata.steps
        self.ub[0:num_vars_timedep] = ub_timedep*self.inputdata.steps
                
        lb_add=[]
        ub_add=[]
        for var in self.stateVars_add:
            lb_add.append(var.lb)
            ub_add.append(var.ub)
        self.lb[num_vars_timedep:] = lb_add
        self.ub[num_vars_timedep:] = ub_add
    
    def def_vtypes(self):
        '''
        Creates lists containing the variable type of all state variables.
        The order corresponds to the positions assigned to the variables
        '''
        num_vars_timedep = len(self.stateVars_timedep)*self.inputdata.steps
        num_vars_add = len(self.stateVars_add)
        num_vars = num_vars_timedep + num_vars_add
        self.vtypes = []
        
        vtypes_timedep = []
        for var in self.stateVars_timedep:
            vtypes_timedep.append(var.vtype)   
        self.vtypes.extend(vtypes_timedep*self.inputdata.steps)                
        vtypes_add=[]
        for var in self.stateVars_add:
            vtypes_add.append(var.vtype)
        self.vtypes[num_vars_timedep:] = vtypes_add
        
    def init_targetfun(self):
        '''Inialization of the target functions with a zero vector'''
        self.f = np.zeros(self.inputdata.num_vars)
    
    def def_targetfun(self):
        pass
    
    def add_var_targetfun(self,var:LPStateVar,value,step=0):
        '''
        Adds a variable to the target function
        To do this, the StateVar, the desired time step and the weighting for the target function must be transferred
        For additional variables: don't add a variable for step
        '''
        self.f[var.pos+step*len(self.stateVars_timedep)]=value
        
        
    def optimize(self,mipGap=0.00,solver:Solver=Solver.GUROBI,objective:Obj=Obj.MINIMIZE):
        '''Performs the linear optimization of the system of equations set up'''
        if solver == Solver.GUROBI:
            x=self.solver_gurobi(mipGap,objective)
        elif solver == Solver.SCIPY:
            x=self.solver_scipy(mipGap,objective)
        elif solver == Solver.CPLEX:
            x=self.solver_cplex(mipGap,objective)
        else:
            raise Exception('This Solver is not implemented')
        self.assign_results(x)
    
    def assign_results(self,x):
        '''Assigns the results of the result vector x to the state variables'''
        self.x = x
        num_vars_timedep = len(self.stateVars_timedep)
        for var in self.stateVars_timedep:
            var.result = x[:num_vars_timedep*self.inputdata.steps][var.pos::num_vars_timedep]
        for var in self.stateVars_add:
            var.result = x[var.pos]
    
# %% Funktion Solver
    def solver_gurobi(self,mipGab,objective):
        '''
        The solver_gurobi function transfers the optimization model to the Gurobi solver, performs the optimization and returns the result.
        Aeq, beq, senses: Matrix or vector of equations with the comparison operator of each equation
        ctype, lb, ub: Type and upper and lower limits of the variables
        f: target function
        '''
        # Transfer the optimization problem to the Gurobi API.
        # Create an empty problem
        problem = gp.Model()
        # add variables
        x = problem.addMVar(shape=self.inputdata.num_vars,lb=self.lb,ub=self.ub,vtype=self.vtypes)
        # x = problem.addMVar(shape=self.inputdata.num_vars,lb=self.lb,ub=self.ub,vtype=['C' for _ in range(self.inputdata.num_vars)])
        # Pass target function
        
        if objective == Obj.MINIMIZE:
            problem.setObjective(self.f @ x, gp.GRB.MINIMIZE)    
        else:
            problem.setObjective(self.f @ x, gp.GRB.MAXIMIZE)    
        # pass equations
        problem.addMConstr(self.Aeq.tocsr(), x, self.senses, self.beq)
        # optimize problem
        problem.setParam('MIPGap', mipGab)  # Percentage distance to the optimum solution
        problem.optimize()
        x = x.X
        return x
    
    def solver_scipy(self,mipGap,objective):
        '''
        The solver_scipy function transfers the optimization model to the scipy milp solver, performs the optimization and returns the result.
        Note: This solver is free but very slow
        
        Aeq, beq, senses: Matrix or vector of equations with the comparison operator of each equation
        ctype, lb, ub: Type and upper and lower limits of the variables
        f: target function
        '''
        if objective == Obj.MINIMIZE:
            pass   
        else:
            raise Exception('The scipy-Solver only allows minimizing')  
        b_l=[]
        b_u=[]
        for idx,sense in enumerate(self.senses):
            if sense == 'E' or sense == '=':
                b_l.append(self.beq[idx])
                b_u.append(self.beq[idx])
            elif sense == '<':
                b_l.append(-np.inf)
                b_u.append(self.beq[idx])
            elif sense == '>':
                b_l.append(self.beq[idx])
                b_u.append(np.inf)
            else:
                raise Exception(f'Unknown Sense {sense}')
        # vtypes / integrality
        integrality=[]
        for idx,vtype in enumerate(self.vtypes):
            if vtype == 'C':
                integrality.append(0)
            elif vtype == 'I':
                integrality.append(1)
            elif vtype == 'S':
                integrality.append(2)
            elif vtype == 'N':
                integrality.append(3)#
            elif vtype == 'B':#
                integrality.append(1)
                self.lb[idx]=0
                self.ub[idx]=1
            else:
                print('unknown vtype')
        from scipy.optimize import LinearConstraint
        constraints = LinearConstraint(self.Aeq,b_l,b_u)
        # %%
        from scipy.optimize import milp
        res = milp(c=self.f,constraints=constraints,integrality=integrality,options={'mip_rel_gap':mipGap})
        return res.x

    def solver_cplex(self,mipgap,objective):
        '''
        The solver_cplex() function transfers the optimization model to the cplex solver, performs the optimization and returns the result.
        Aeq, beq, senses: Matrix or vector of equations with the comparison operator of each equation
        ctype, lb, ub: Type and upper and lower limits of the variables
        f: target function
        '''
        import cplex
        # nbew empty problem
        problem = cplex.Cplex()

        # Adding variables
        problem.variables.add(names=['x' + str(i) for i in range(self.inputdata.num_vars)])

        # formatting the variable-type-list to fit cplex
        types = [(i, problem.variables.type.continuous) if vtype_i == 'C' 
                    else (i, problem.variables.type.binary) if vtype_i == 'B'
                    else (i, problem.variables.type.semi_continuous) if vtype_i == 'S'
                    else (i, problem.variables.type.semi_integer) if vtype_i == 'N'
                    else (i, problem.variables.type.integer) for i, vtype_i in enumerate(self.vtypes)]
        problem.variables.set_types(types)

        # Setting lower and upper bounds
        problem.variables.set_lower_bounds(list(enumerate(self.lb)))
        problem.variables.set_upper_bounds(list(enumerate(self.ub)))

        # set targetfunction
        problem.objective.set_linear(list(enumerate(self.f)))
        # set objective
        if objective == Obj.MINIMIZE:
            problem.objective.set_sense(problem.objective.sense.minimize)    
        else:
            problem.objective.set_sense(problem.objective.sense.maximize)    

        # prepare equations
        Aeq_rows = self.Aeq.row.tolist()
        Aeq_cols = self.Aeq.col.tolist()
        Aeq_vals = self.Aeq.data.tolist()
        beq_rows = [i for i in range(len(self.beq))]
        beq_vals = np.array(self.beq,dtype=float)

        # cplex need var-names
        problem.linear_constraints.add(names=['c' + str(i) for i in range(np.shape(self.Aeq)[0])])
        # setting Aeq
        problem.linear_constraints.set_coefficients(zip(Aeq_rows, Aeq_cols, Aeq_vals))
        # setting beq
        problem.linear_constraints.set_rhs(zip(beq_rows, beq_vals))

        # preparing and setting senses
        senses =[]
        for sense in self.senses:
            if sense == '<':
                senses.append('L')
            elif sense == '=':
                senses.append('E')
            elif sense == '>':
                senses.append('G')
            else:
                senses.append(sense)
        problem.linear_constraints.set_senses(list(enumerate(senses)))
            
        # setting mipgap
        problem.parameters.mip.tolerances.mipgap.set(float(mipgap))

        del Aeq_rows, Aeq_cols, Aeq_vals, beq_rows, beq_vals

        # Solver
        problem.solve()

        # Returning result vector
        x = np.array(problem.solution.get_values())
        return x