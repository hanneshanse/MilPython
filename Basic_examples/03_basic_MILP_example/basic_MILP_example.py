'''
This is a basic example for the milpython-framework.
This example contains a small buliding-energy-system.
It consits of a building with a battery and a constant electrical load.
The electricity price oscillates.
The total electricity cost is getting optimized

To demonstrate mixed integer variables, the following conditions have been added:
- The power consumed from the grid must be a multiple of 200 watts (integer variable)
- The charging and discharging power of the battery can either be 0 or lie between the limits lb and ub (semi-continuous variable)
- The battery cannot be charged and discharged at the same time (binary variable)
'''
# %%
# Imports
import numpy as np
from MilPython import *
from LPObjects import *
# %%
# instanciating objects
steps=5
inputdata_dict = {'electricity_price':-np.sin(np.linspace(0, 10*np.pi, steps)) + 2,  # electricity price oscillates around 1
                  'electricity_demand':np.full(steps,500)}                           # constant electricity demand
inputdata = LPInputdata(data=inputdata_dict,dt_h=10/60)
buil = Building(inputdata)

# %%
# Display the LP-system
buil.show_lp_system()

# %%
# Solve
buil.optimize()

#%%
# The power consumed from the grid must be a multiple of 200 watts (integer variable)
buil.grid.p_consumption.plot_result()

# %%
# - The charging and discharging power of the battery can either be 0 or lie between the limits lb and ub (semi-continuous variable)
# - The battery cannot be charged and discharged at the same time (binary variable)
buil.bat.p_charge.plot_result()
buil.bat.p_discharge.plot_result()

# %%
# Save results to Excel
buil.results_to_excel('results.xlsx')
# %%
