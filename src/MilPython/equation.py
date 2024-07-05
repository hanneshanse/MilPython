from .lpStateVar import LPStateVar
class Equation:
    '''Simple class for new equations. The Format is alway: Sum(stateVar*factor) >sense< b'''
    def __init__(self,var_lst:list,sense:str,b:float,description:str):
        """
        Args:
            var_lst (list): each items of the list represents one variable in equation, format of each item (time dependent): [stateVar,factor,timestep]; for additional variables: [stateVar,factor] 
            sense (str): ">","=" or "<"
            b (float): right side of equation
        """        
        self.var_lst = var_lst
        self.sense = sense
        self.b = b
        self.description=description