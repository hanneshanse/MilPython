import numpy as np
from .lpStateVar import LPStateVar, LPStateVar_timedep,LPStateVar_add
from .lpInputdata import LPInputdata
from scipy.sparse import coo_matrix, csc_matrix
from .equation import Equation as Eq
from collections import defaultdict
import sympy as sp

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
    
    def add_eq(self,var_lst,sense='E',b=0,description=''):
        """Adds an equation to the equation system; automatically adds eq to eq_lst of this object

        Args:
            var_lst (list): each items of the list represents one variable in equation, format of each item (time dependent): [stateVar,factor,timestep]; for additional variables: [stateVar,factor] 
            sense (str): ">","=" or "<"
            b (float): right side of equation
            description (str): optiional short description of equation
        """        
        self.eq_lst.append(Eq(var_lst,sense,b,description))
    
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
     
    
    def str_equation(self,equation):
        min_time_step = min(time_step for _, _, time_step in equation.var_lst)
        sorted_var_lst = sorted(equation.var_lst, key=lambda x: x[0].name)  # sort by variable name
        str_lst = [f"{var_state.name},{str(var_coef)},{str(time_step - min_time_step)}" for var_state, var_coef, time_step in sorted_var_lst]
        return ','.join(str_lst) + equation.sense + str(equation.b)


    def return_grouped_eqs(self):
        grouped = defaultdict(list)
        for eqn in self.eq_lst:
            key = self.str_equation(eqn)
            grouped[key].append(eqn)
        grouped_lst = list(grouped.values())
        return grouped_lst
    
    def round_scientific(self,number):
        # Konvertiere die Zahl zuerst in eine wissenschaftliche Darstellung
        scientific_str = "{:e}".format(number)

        # Zerlege die formatierte Zahl in Mantisse und Exponent
        mantissa_str, exponent_str = scientific_str.split('e')

        # Umwandle die Teile wieder in Zahlen
        mantissa = float(mantissa_str)
        exponent = int(exponent_str)

        # Runde die Mantisse auf 3 Nachkommastellen
        mantissa_rounded = round(mantissa, 5)

        # Setze die gerundete wissenschaftliche Darstellung zusammen
        rounded_scientific = "{}e{:02d}".format(mantissa_rounded, exponent)

        return float(rounded_scientific)
    
    def summarize_intervals(self,lst):
        output = []
        i = 0
        while i < len(lst):
            start = lst[i]
            while i+1 < len(lst) and lst[i+1] == lst[i]+1:
                i += 1
            end = lst[i]
            if start == end:
                output.append(str(start))
            else:
                output.append(f'{start}-{end}')
            i += 1
        return ', '.join(output)
    
    def format_string(self,s):
        if "_" in s:
            parts = s.split('_', 1)
            parts[1] = parts[1].replace('_', ',')
            return parts[0] + "_{" + parts[1] + "}"
        else:
            return s   # Wenn kein Unterstrich vorhanden ist, geben wir den Ursprungsstring zurück

