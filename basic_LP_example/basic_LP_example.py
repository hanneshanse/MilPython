# %%
# Imports
import pandas as pd
import numpy as np
from MilPython import *
from LPObjects import *
# %%
# Objekte anlegen
steps=5
inputdata_dict = {'temp_a':np.zeros(steps), # Außentemperatur 0 Grad
             'electricity_price':-np.sin(np.linspace(0, 10*np.pi, steps)) + 1,  # electricity price oscillates around 1
             'electricity_demand':np.full(steps,500),                           # constant electricity demand
            }
inputdata = LPInputdata(data=inputdata_dict,dt_h=10/60)
buil = Building(inputdata)

# %%
# Solve
buil.optimize()

#%%
# Use results
a = buil.bat.E.result

# %%
# View results
buil.bat.E.plot_result()
plot_sum(buil.netz.p_consumption,buil.netz.p_feed)

# %%
