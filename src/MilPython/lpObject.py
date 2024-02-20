import numpy as np
from .lpStateVar import LPStateVar, LPStateVar_timedep,LPStateVar_add
from .lpInputdata import LPInputdata
from scipy.sparse import coo_matrix, csc_matrix
from .equation import Equation as Eq

class LPObject:
    def __init__(self,inputdata:LPInputdata,name:str,comment:str):
        '''Constructor of the general Linear Programming Object'''
        if self.__class__.__name__ == 'LPObject':
            raise Exception('This is an abstract class. Please only create objects of the inheriting class')
        self.inputdata = inputdata
        self.name = name
        self.comment = comment
        self.stateVar_lst:list[LPStateVar]=[]
        self.eq_lst=[]

    def add_time_var(self,name:str,unit:str='',lb:float=0,ub:float=np.inf,vtype='C',comment:str='')->LPStateVar_timedep:
        """adds a new timedependent statevariable to the LPObject; returns the statvar-object, which should be saved as a variable in the LPObject

        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Returns:
            LPStateVar_timedep: _description_
        """      
        var = LPStateVar_timedep(name,unit,lb,ub,vtype,comment)
        self.stateVar_lst.append(var)
        return var
    
    def add_additional_var(self,name:str,unit:str='',lb:float=0,ub:float=np.inf,vtype='C',comment:str='')->LPStateVar_add:
        """adds a new additional, time-independent statevariable to the LPObject; returns the statvar-object, which should be saved as a variable in the LPObject

        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Returns:
            LPStateVar_add: _description_
        """        
        var = LPStateVar_add(name,unit,lb,ub,vtype,comment)
        self.stateVar_lst.append(var)
        return var
    
    def add_eq(self,var_lst,sense='E',b=0):
        """Adds an equation to the equation system; automatically adds eq to eq_lst of this object

        Args:
            var_lst (list): each items of the list represents one variable in equation, format of each item (time dependent): [stateVar,factor,timestep]; for additional variables: [stateVar,factor] 
            sense (str): ">","=" or "<"
            b (float): right side of equation
        """        
        self.eq_lst.append(Eq(var_lst,sense,b))
    
    def getStateVars(self)->list[LPStateVar]:
        '''greturns list of state_vars'''
        return self.stateVar_lst
                
    def def_equations(self):
        '''Has to be overritten by inheriting class'''
        pass
    
    def return_eqs(self):
        '''Changes format of local equations so lpmain can take them'''
        num_vars = sum(len(eq.var_lst) for eq in self.eq_lst)
        self.idx=0
        self.eq_nr=0
        self.row = np.zeros(shape=(num_vars,))
        self.col = np.zeros(shape=(num_vars,))
        self.data = np.zeros(shape=(num_vars,))
        self.senses=[]
        self.beq = []
        
        for eq in self.eq_lst:
            for var in eq.var_lst: 
                if len(var) == 2:
                    var.append(0)
                self.row[self.idx] = self.eq_nr
                self.col[self.idx] = var[0].pos + var[2] * self.inputdata.num_vars_timedep
                self.data[self.idx] = var[1]
                self.idx+=1
            self.senses.append(eq.sense)
            self.beq.append(eq.b)
            self.eq_nr+=1
        Aeq_temp = coo_matrix((self.data,(self.row,self.col)),shape=(self.eq_nr,self.inputdata.num_vars))
        return Aeq_temp,self.beq,self.senses   
