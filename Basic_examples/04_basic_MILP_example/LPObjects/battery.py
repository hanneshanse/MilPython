from MilPython import *

class Battery(LPObject):
    '''Defines a simple battery storage system with a power-independent efficiency level'''
    def __init__(self, inputdata:LPInputdata,eta_charge=1,eta_discharge=1,name='',comment=''):
        super().__init__(inputdata,name,comment)
        self.p_charge_max = 3000
        self.p_discharge_max = 3000
        self.eta_charge=eta_charge
        self.eta_discharge=eta_discharge
        
        # p_charge and p_discharge are now semi-continuous, so 0 and all values between lower bound (lb) and upper bound (ub) are allowed
        # in this case: it must be charged or discharged with at least 100 watts
        self.p_discharge = self.add_time_var('P el entladen','W',lb=100,ub=self.p_discharge_max,vtype='S')
        self.p_charge = self.add_time_var('P el laden','W',lb=100,ub=self.p_charge_max,vtype='S') 
        
        self.E = self.add_time_var('E el t','Wh',ub=6000)
        
        # Binary variable for switching between charging and discharging: Charging = 1; Discharging = 0
        self.charge_switch = self.add_time_var('charging - discharging switch',vtype='B') 
        
    
    def def_equations(self):
        # Energy balance
        # Bat level in the time step - bat level in the last time step - Charging power * DeltaT * eta + Discharging power * DeltaT / eta = 0
        # First time step
        self.add_eq(var_lst=[[self.E,1,0],
                             [self.p_charge,- self.inputdata.dt_h * self.eta_charge,0],
                             [self.p_discharge,self.inputdata.dt_h * self.eta_discharge,0]],
                    sense='E',
                    b=0)
        # All further time steps
        for t in range(1,self.inputdata.steps):
            self.add_eq(var_lst=[[self.E,1,t],
                                 [self.E,-1,t-1],
                                 [self.p_charge,- self.inputdata.dt_h * self.eta_charge,t],
                                 [self.p_discharge,self.inputdata.dt_h * self.eta_discharge,t]],
                        sense='E',
                        b=0)
            
            # Restriction that charging and discharging cannot take place at the same time using binary variable self.charge_switch 
            self.add_eq(var_lst=[[self.charge_switch,self.p_charge_max,t],
                                 [self.p_charge,-1,t]],
                        sense='>',b=0)
            self.add_eq(var_lst=[[self.charge_switch,self.p_discharge_max,t],
                                 [self.p_discharge,1,t]],
                        sense='<',b=self.p_discharge_max)