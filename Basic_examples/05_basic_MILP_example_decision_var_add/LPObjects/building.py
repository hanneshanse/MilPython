from MilPython import *
from .battery import Battery
from .gridConnection import GridConnection

class Building(LPObject,LPMain):
    '''
    Defines the building. 
    The building contains all other LPObjects and is itself an LPObject which, among other things, creates the energy balance of the overall system.
    The building is also the LPMain class of this energy system. The entire equation structure and optimization therefore run via this class.
    '''
    def __init__(self, inputdata: LPInputdata,name='',comment='',bat_price=1):
        # For all LPObjects, LPObject.init must be called as the first step of init
        LPObject.__init__(self,inputdata,name,comment)
        
        # The LPMain-Object must contain a list called self.obj_lst containing all LPObjects of the system (including itself)        
        self.bat = Battery(inputdata)
        self.grid = GridConnection(inputdata)
        self.obj_lst:list[LPObject]=[self,self.bat,self.grid]
        
        self.bat_price = bat_price # battery price per Wh
        self.grid.p_feed.ub=0 # # No feed-back into the grid for now
        
        #The LPMain-init must be called in the init after the ob_lst has been created
        LPMain.__init__(self,inputdata) 
       
    def def_equations(self):
        '''Defines the system of equations for the overall system'''
        # Electrical energy balance -> feed into building node is positive 
        for t in range(self.inputdata.steps):
            self.add_eq(var_lst=[[self.grid.p_feed,-1,t],               # Output of electrical power to higher-level grid
                                 [self.grid.p_consumption,1,t],         # Power consumption from higher-level grid
                                 [self.bat.p_charge,-1,t],              # Charging the battery storage
                                 [self.bat.p_discharge,1,t],            # Discharging the battery storage
                                 ],
                        sense='E',
                        b=self.inputdata.data['electricity_demand'][t]) # Electricity demand of the building

    def def_targetfun(self):
        '''
        Defines the targetfunction of the optimization
        This method must be defined in the class inheriting from LPMain
        '''
        for t in range(self.inputdata.steps):
            self.add_var_targetfun(var=self.grid.p_consumption,
                                   value=self.inputdata.data['electricity_price'][t],
                                   step=t
                                   )
        self.add_var_targetfun(var=self.bat.bat_choice.price,value=1)