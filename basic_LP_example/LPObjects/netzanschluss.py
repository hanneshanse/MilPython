from MilPython import *

class Netzanschluss(LPObject):
    '''Definiert den Netzanschluss des Gebäudes'''
    def __init__(self,inputdata,name='',comment=''):
        super().__init__(inputdata,name,comment)
        self.P_el_bezug_t = self.add_time_var('P Netzbezug','W',ub=16*230)
        self.P_el_abgabe_t = self.add_time_var('P Einspeisung','W',ub=16*230)