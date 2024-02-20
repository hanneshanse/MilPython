from scipy.sparse import vstack
import gurobipy as gp
import numpy as np
from .lpObject import LPObject
from .lpStateVar import LPStateVar,LPStateVar_timedep,LPStateVar_add
from .lpInputdata import LPInputdata
from scipy.sparse import coo_matrix, csc_matrix, vstack

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
        
        
    def optimize(self):
        '''Performs the linear optimization of the system of equations set up'''
        x=self.solver_gurobi()
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
    def solver_gurobi(self):
        '''The solver_gurobi function transfers the optimization model to the Gurobi solver, performs the optimization and returns the result.
        Aeq, beq, senses: Matrix or vector of equations with the comparison operator of each equation
        ctype, lb, ub: Type and upper and lower limits of the variables
        f: target function'''
        # Transfer the optimization problem to the Gurobi API.
        # Create an empty problem
        problem = gp.Model()
        # add variables
        x = problem.addMVar(shape=self.inputdata.num_vars,lb=self.lb,ub=self.ub,vtype=self.vtypes)
        # x = problem.addMVar(shape=self.inputdata.num_vars,lb=self.lb,ub=self.ub,vtype=['C' for _ in range(self.inputdata.num_vars)])
        # Pass target function
        problem.setObjective(self.f @ x, gp.GRB.MINIMIZE)    
        # pass equations
        problem.addMConstr(self.Aeq.tocsr(), x, self.senses, self.beq)
        # optimize problem
        problem.setParam('MIPGap', 0.00)  # Percentage distance to the optimum solution
        problem.optimize()
        x = x.X
        return x