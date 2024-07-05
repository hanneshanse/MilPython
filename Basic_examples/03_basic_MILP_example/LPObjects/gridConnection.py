from MilPython import *

class GridConnection(LPObject):
    '''Defines the grid connection of a building'''
    def __init__(self,inputdata,name='',comment=''):
        super().__init__(inputdata,name,comment)
        self.p_consumption = self.add_time_var('P_grid_taken','W',ub=16*230)
        self.p_feed = self.add_time_var('P_grid_feed','W',ub=16*230)
        
        self.p_consumption_increment=200
        self.consumption_int = self.add_time_var('int_incremet',vtype='I')
    
    def def_equations(self):
        # the power consumed from the grid must be a multiple of 200 watts at each time step
        for t in range(self.inputdata.steps):
            self.add_eq(var_lst=[[self.p_consumption,1,t],
                                 [self.consumption_int,-self.p_consumption_increment,t]],
                        sense='=',b=0)