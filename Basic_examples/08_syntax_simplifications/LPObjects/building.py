from MilPython import *
from .battery import Battery
from .gridConnection import GridConnection

class Building(LPObject,LPMain):
    '''
    Defines the building. 
    The building contains all other LPObjects and is itself an LPObject which, among other things, creates the energy balance of the overall system.
    The building is also the LPMain class of this energy system. The entire equation structure and optimization therefore run via this class.
    '''
    def __init__(self, inputdata: LPInputdata,name='',comment=''):
        # For all LPObjects, LPObject.init must be called as the first step of init
        LPObject.__init__(self,inputdata,name,comment)
        
        # The LPMain-Object must contain a list called self.obj_lst containing all LPObjects of the system (including itself)        
        self.bat = Battery(inputdata)
        self.grid = GridConnection(inputdata)
        
        self.grid.p_feed.ub=0 # No feed-back into the grid for now
        
        #The LPMain-init must be called in the init after the ob_lst has been created
        LPMain.__init__(self,inputdata) 
       
    def def_equations(self):
        '''Defines the system of equations for the overall system'''
        # Electrical energy balance -> feed into building node is positive 
        
        #If an equation containing time dependent variables has to be defined or all time steps and each equation does not contain more than one time step, no iteration over the time steps is necessary.
        # The syntax is then the same as for additional variables.
        # The factor and right side of the equation may also be a list of values, which are then assigned to the respective time steps.
        
        self.add_eq(var_lst=[[self.grid.p_feed,-1],               # Output of electrical power to higher-level grid
                                [self.grid.p_consumption,1],         # Power consumption from higher-level grid
                                [self.bat.p_charge,-1],              # Charging the battery storage
                                [self.bat.p_discharge,1],            # Discharging the battery storage
                                ],
                    sense='E',
                    b=self.inputdata.data['electricity_demand']) # Electricity demand of the building

    def def_targetfun(self):
        '''
        Defines the targetfunction of the optimization
        This method must be defined in the class inheriting from LPMain
        '''
        
        # if the variable added to the target-function it can also be added without the time steps. The value can be a single value or a list of values.
        # The time steps are then assigned automatically.
        self.add_var_targetfun(var=self.grid.p_consumption,
                                value=self.inputdata.data['electricity_price'])