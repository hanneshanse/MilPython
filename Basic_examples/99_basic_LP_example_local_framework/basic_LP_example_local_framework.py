'''
This is a basic example for the milpython-framework.
This example contains a small buliding-energy-system.
It consits of a building with a battery and a constant electrical load.
The electricity price oscillates.
The total electricity cost is getting optimized

This version of example 01: "basic_LP_example" uses the local version of the MilPython-Framework found at src/MilPython
Using a local version of the framework instead of using the package via "pip install milpython" can be usefull if a customization of the framework is necessary
'''
# %%
# Imports
import numpy as np
import sys 
sys.path.append('...src.MilPython')
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
# Use results
a = buil.bat.E.result

# %%
# View results
buil.bat.E.plot_result()
plot_sum(buil.grid.p_consumption,buil.grid.p_feed)

# %%
# Save results to Excel
buil.results_to_excel('results.xlsx')

# %%
