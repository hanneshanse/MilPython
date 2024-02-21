'''
This is a basic example for the milpython-framework.
This example contains a small buliding-energy-system.
It consits of a building with a battery and a constant electrical load.
The electricity price oscillates.
The total electricity cost is getting optimized

This example demonstrates how to change solver-settings
'''
# %%
# Imports
import numpy as np
import timeit
from MilPython import *
from LPObjects import *
# %%
# instanciating objects
steps=100
inputdata_dict = {'electricity_price':-np.sin(np.linspace(0, 10*np.pi, steps)) + 2,  # electricity price oscillates around 1
                  'electricity_demand':np.full(steps,500)}                           # constant electricity demand
inputdata = LPInputdata(data=inputdata_dict,dt_h=10/60)
buil = Building(inputdata)

# %%
# Use different solvers
buil.optimize(solver=Solver.GUROBI) # Standard-Solver
buil.optimize(solver=Solver.CPLEX) 
buil.optimize(solver=Solver.SCIPY) # free but slow


# %% compare runtimes of different solvers
t_gurobi = timeit.timeit('buil.optimize(solver=Solver.GUROBI)', globals=globals(), number=1)
t_cplex = timeit.timeit('buil.optimize(solver=Solver.CPLEX)', globals=globals(), number=1)
t_scipy = timeit.timeit('buil.optimize(solver=Solver.SCIPY)', globals=globals(), number=1)
print(f'Gurobi-Runtime: {t_gurobi}\nCPlex-Runtime: {t_cplex}\nScipy-Runtime: {t_scipy}')

# %%
# change mipgap
buil.optimize(mipGap=0.0001)
# %%
# Changing the objective to maximizing the targetfunction
# Note: maximizing is not supperted by the scipy-solver
buil.optimize(objective=Obj.MAXIMIZE)
# %%
