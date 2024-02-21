'''
This example extends the basic_LP_example by an additional variable (independent of time).
In this case the add. variable is the max. capacity of the battery. 
Battery capacity comes with a price.
The total costs for electricity and batery capacity are getting optimized.
'''
# %%
# Imports
import pandas as pd
import numpy as np
from MilPython import *
from LPObjects import *
# %%
# instanciating objects
steps=5
inputdata_dict = {'electricity_price':-np.sin(np.linspace(0, 10*np.pi, steps)) + 2,  # electricity price oscillates around 1
                  'electricity_demand':np.full(steps,500)}                           # constant electricity demand
inputdata = LPInputdata(data=inputdata_dict,dt_h=10/60)
buil = Building(inputdata,bat_price=10)

# %%
# Solve
buil.optimize()
print(f'Lowest total cost with {buil.bat.E_max.result} Wh battery storage for 10 € / Wh')
buil.bat.E.plot_result()

#%%
buil2 = Building(inputdata,bat_price=1)
buil2.optimize()
print(f'Lowest total cost with {buil2.bat.E_max.result} Wh battery storage for 1 € / Wh')
buil2.bat.E.plot_result()
# %%
