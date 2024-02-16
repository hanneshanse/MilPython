from MilPython import *
from .batteriespeicher import Batteriespeicher
from .netzanschluss import Netzanschluss

class Gebaeude(LPObject,LPMain):
    '''
    Definiert das Gebäude. 
    Das Gebäude beinhaltet alle weiteren LPObjects und ist selbst ein LPObjekt, das u.a. die Energiebilanz des Gesamtsystems bildet.
    Das Gebäude ist außerdem die LPMain-Klasse dieses Energiesystems. Der gesamte Gleichungsaufbau und die Optimierung laufen somit über diese Klasse.
    '''
    def __init__(self, inputdata: LPInputdata,name='',comment=''):
        LPObject.__init__(self,inputdata,name,comment)
        
        self.bat = Batteriespeicher(inputdata)
        self.netz = Netzanschluss(inputdata)
        self.obj_lst:list[LPObject]=[self,self.bat,self.netz]
        
        self.netz.P_el_abgabe_t.ub=0 # keine Einspeisung ins Netz (for now)#TODO Rückeinspeisung ins Netz
        LPMain.__init__(self,inputdata) 
       
    def def_equations(self):
        '''Definiert das Gleichungssystem für das Gesamtsystem'''
        # elektrische Energiebilanz -> einspeisung in Gebäudeknoten positiv
        for t in range(self.inputdata.steps):
            self.add_eq(var_lst=[[self.netz.P_el_abgabe_t,-1,t],     # Abgabe el. Leistung an übergeordnetes Netz
                                 [self.netz.P_el_bezug_t,1,t],       # Leistungsbezug aus übergeordnetem Netz
                                 [self.bat.P_el_t_laden,-1,t],       # Laden des Batteriespeichers
                                 [self.bat.P_el_t_entladen,1,t],     # Entladen des Batteriespeichers
                                 ],
                        sense='E',
                        b=self.inputdata.data['strombedarf'][t])# Strombedarf im Gebäude

    def def_targetfun(self):
        '''Definiert die Zielfunktion der Optimierung'''
        for t in range(self.inputdata.steps):
            self.add_var_targetfun(var=self.netz.P_el_bezug_t,
                                   value=self.inputdata.data['strompreis'][t],
                                   step=t
                                   )