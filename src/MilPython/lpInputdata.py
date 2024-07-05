class LPInputdata:
    '''
    Class, that contains all input data for the optimization.
    Contains time series as dict
    In der Initialisierung des LPMain-Objekts wird dieser Klasse außerdem die Gesamtanzahl an Variablen zugewiesen
    '''
    def __init__(self,data:dict,dt_h:float,verbose=True):
        """
        Args:
            data (dict): dictionary of all important input data
            dt_h (float): stepsize in hours
        """        
        self.data = data                            # dict containing time series input data
        self.steps=len(next(iter(data.items()))[1]) # number of steps                           #! leads to error if first item in data is no time series
        self.dt_h = dt_h                            # stepsize in hours
        self.num_vars=None                          # total number of stateVariables
        self.num_vars_timedep=None                  # number of time dependent stateVars
        self.verbose=verbose                        #verbosity of optimization