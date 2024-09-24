from MilPython import *

class GridConnection(LPObject):
    '''Defines the grid connection of a building'''
    def __init__(self,inputdata,name='',comment=''):
        super().__init__(inputdata,name,comment)
        self.p_consumption = self.add_time_var('P_grid_taken','W')
        self.p_feed = self.add_time_var('P_grid_feed','W',ub=16*230)
        
        self.connection_choice = self.add_decision_var_timedep(name='connection_choice',decision_dict={'opt1':{'price':100,'p_max':500},'opt2':{'price':200,'p_max':1000},'opt3':{'price':50,'p_max':200}},inputdata=inputdata)
        
    def def_equations(self):
         for t in range(self.inputdata.steps):
             self.add_eq([[self.connection_choice.p_max,1,t],
                          [self.p_consumption,-1,t]],'>',0)