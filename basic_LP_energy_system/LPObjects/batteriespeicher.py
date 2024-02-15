from MilPython import *

class Batteriespeicher(LPObject):
    '''Definiert einen einfachen Batteriespeicher mit einem leistungsunabhängigen Wirkungsgrad'''
    def __init__(self, inputdata:LPInputdata,eta_laden=1,eta_entladen=1,name='',comment=''): #TODO Literaturwerte für Lade- und Entladewirkungsgrad
        super().__init__(inputdata,name,comment)
        self.P_el_t_entladen = self.add_time_var('P el entladen','W',ub=3000)
        self.P_el_t_laden = self.add_time_var('P el laden','W',ub=3000)
        self.E_el_t = self.add_time_var('E el t','Wh') #,ub=6000
        # self.E_max = self.add_additional_var('E_max','Wh',lb=30,ub=30)  
        self.eta_laden=eta_laden
        self.eta_entladen=eta_entladen
    
    def def_equations(self):
        # Energiebilanz
        # Energieinhalt im Zeitschritt - Energieinhalt im letzten Zeitschritt - Ladeleistung * DeltaT * eta + Entladeleistung * DeltaT / eta = 0
        # Erster Zeitschritt
        self.add_eq(var_lst=[[self.E_el_t,1,0],
                             [self.P_el_t_laden,- self.inputdata.dt_h * self.eta_laden,0],
                             [self.P_el_t_entladen,self.inputdata.dt_h * self.eta_entladen,0]],
                    sense='E',
                    b=0)
        # Alle weiteren Zeitschritte
        for t in range(1,self.inputdata.steps):
            self.add_eq(var_lst=[[self.E_el_t,1,t],
                                 [self.E_el_t,-1,t-1],
                                 [self.P_el_t_laden,- self.inputdata.dt_h * self.eta_laden,t],
                                 [self.P_el_t_entladen,self.inputdata.dt_h * self.eta_entladen,t]],
                        sense='E',
                        b=0)
        
        # for t in range(self.inputdata.steps): #TODO: nur im bsp. zur optimierung der Speichergröße  
        #     self.add_eq([[self.E_max,1],
        #                  [self.E_el_t,-1,t]],
        #                 sense='>',b=0)
        
        