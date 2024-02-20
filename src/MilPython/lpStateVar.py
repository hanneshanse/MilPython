import matplotlib.pyplot as plt

class LPStateVar:
    '''
    Abstract class (only create objects of the inheriting classes)
    Defines state variables for linear optimization
    Contains name, unit, lower and upper bound and space for comments
    when optimizing, the optimized results for the variable are stored under self.result
    '''
    def __init__(self,name:str,unit:str=None,lb:float=0,ub:float=float('inf'),vtype='C',comment:str=None):
        """Init-Method for abstract LPStateVar-class. Has to be run by inheriting classes init-fun

        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.

        Raises:
            Exception: Only create objects of the inheriting classes
        """        
        if self.__class__.__name__ == 'LPStateVar':
            raise Exception('This class is abstract and is not used for instantiation. Please create objects of the inheriting classes time or addition')
        self.pos:int=None
        self.name:str=name
        self.lb:float=lb
        self.ub:float=ub
        self.vtype:chr=vtype
        self.unit:str=unit
        self.result = None
        self.comment:str=comment
    
    def __repr__(self):
        return f"StateVar(name='{self.name}')"
    
class LPStateVar_timedep(LPStateVar):
    '''
    Class for time-dependent state variables
    A variable of this type is automatically created for each time step
    self.pos corresponds to the position of the variable in time step zero.
    '''
    def __init__(self, name, unit=None,  lb=0, ub=float('inf'),vtype='C', comment=None):
        """
        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.
        """        
        super().__init__(name, unit, lb, ub, vtype, comment)
    
    def plot_result(self):
        '''Simple method for plotting the time histories of the optimization result for this variable'''
        if self.result is None:
            print('The optimization must be performed first')
            return
        plt.plot(self.result)
        plt.title(self.name)
        plt.ylabel(self.unit)
        plt.xlabel('steps')
        plt.show()
    
    def __repr__(self):
        if self.result is not None:
            self.plot_result()
        return f"StateVar(name='{self.name}')"

class LPStateVar_add(LPStateVar):
    '''Class for additional variables that only occur once (and not in every time step) '''
    def __init__(self, name, unit=None, lb=0, ub=float('inf'),vtype='C', comment=None):
        """
        Args:
            name (str): name of variable
            unit (str, optional): store variable unit here. Defaults to ''.
            lb (float, optional): lowest allowed value for var. Defaults to 0.
            ub (float, optional): highest allowed value for var. Defaults to np.inf.
            comment (str, optional): optional space for comment, store sign convention here. Defaults to ''.
        """        
        super().__init__(name, unit, lb, ub, vtype, comment)