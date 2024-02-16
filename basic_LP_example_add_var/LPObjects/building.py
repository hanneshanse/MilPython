from MilPython import *
from .battery import Battery
from .gridConnection import GridConnection

class Building(LPObject,LPMain):
    '''
    Definiert das Gebäude. 
    Das Gebäude beinhaltet alle weiteren LPObjects und ist selbst ein LPObjekt, das u.a. die Energiebilanz des Gesamtsystems bildet.
    Das Gebäude ist außerdem die LPMain-Klasse dieses Energiesystems. Der gesamte Gleichungsaufbau und die Optimierung laufen somit über diese Klasse.
    '''
    def __init__(self, inputdata: LPInputdata,name='',comment='',bat_price=1):
        LPObject.__init__(self,inputdata,name,comment)
        
        self.bat = Battery(inputdata)
        self.grid = GridConnection(inputdata)
        self.obj_lst:list[LPObject]=[self,self.bat,self.grid]
        self.bat_price = bat_price # battery price per Wh
        self.grid.p_feed.ub=0 # keine Einspeisung ins Netz (for now)#TODO Rückeinspeisung ins Netz
        LPMain.__init__(self,inputdata) 
       
    def def_equations(self):
        '''Definiert das Gleichungssystem für das Gesamtsystem'''
        # elektrische Energiebilanz -> einspeisung in Gebäudeknoten positiv
        for t in range(self.inputdata.steps):
            self.add_eq(var_lst=[[self.grid.p_feed,-1,t],     # Abgabe el. Leistung an übergeordnetes Netz
                                 [self.grid.p_consumption,1,t],       # Leistungsbezug aus übergeordnetem Netz
                                 [self.bat.p_charge,-1,t],       # Laden des Batteriespeichers
                                 [self.bat.p_discharge,1,t],     # Entladen des Batteriespeichers
                                 ],
                        sense='E',
                        b=self.inputdata.data['electricity_demand'][t])# Strombedarf im Gebäude

    def def_targetfun(self):
        '''Definiert die Zielfunktion der Optimierung'''
        for t in range(self.inputdata.steps):
            self.add_var_targetfun(var=self.grid.p_consumption,
                                   value=self.inputdata.data['electricity_price'][t],
                                   step=t
                                   )
            self.add_var_targetfun(var=self.bat.E_max,
                                   value=self.bat_price)