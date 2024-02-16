# %%
# Imports
import pandas as pd
import numpy as np
from MilPython import *
from LPObjects import *
# %%
# Objekte anlegen
steps=5
inputdata = {'temp_a':np.zeros(steps), # Außentemperatur 0 Grad
             'strompreis':-np.sin(np.linspace(0, 10*np.pi, steps)) + 1,  # strompreis: erstmal sinus, der um 1 oszilliert
             'strombedarf':np.random.uniform(500, 500, steps),          # random Strombedarf
             'waermebedarf':np.random.uniform(500,500,steps),           # random Heizwärmebedarf
             'twwBedarf':np.random.uniform(500,500,steps),           # random TWW-Bedarf
            }
eingangsdaten = LPInputdata(data=inputdata,dt_h=10/60)
geb = Gebaeude(eingangsdaten)

# %%
# Solve
geb.optimize()

#%%
# Use results
a = geb.bat.E_el_t.result

# %%
# View results
geb.bat.E_el_t.plot_result()
plot_sum(geb.netz.P_el_bezug_t,geb.netz.P_el_abgabe_t)

# %%
