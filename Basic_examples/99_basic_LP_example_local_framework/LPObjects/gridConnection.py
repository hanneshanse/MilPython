import sys 
sys.path.append('....src.MilPython')
from MilPython import *

class GridConnection(LPObject):
    '''Defines the grid connection of a building'''
    def __init__(self,inputdata,name='',comment=''):
        super().__init__(inputdata,name,comment)
        self.p_consumption = self.add_time_var('Power taken','W',ub=16*230)
        self.p_feed = self.add_time_var('Power fed into grid','W',ub=16*230)