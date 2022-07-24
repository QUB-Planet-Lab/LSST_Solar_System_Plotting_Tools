from .plot import Plot
import matplotlib.pyplot as plt
from typing import Optional

from .styles.filter_color_scheme import COLOR_SCHEME

import numpy as np 
import seaborn as sns

class ViolinPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, plot_info : dict = {}, library: Optional[str] = "seaborn"):
        super().__init__(data, xlabel, ylabel, title, library) 
        
        
        
        # need to work on data formating here
        # list of lists for matplotlib, dataframe for seaborn
         
        self.x = x
        self.y = y
                
        if not y:
            if library == "seaborn":
                # Look into this further.
                print("Seaborn not available. Reverting to matplotlib")
            self.plot = self.ax.violinplot(dataset = data[self.x], vert=False)
            
            
        elif not x:
            if library == "seaborn":
                print("Seaborn not available. Reverting to matplotlib")
            self.plot = self.ax.violinplot(dataset = data[self.y], vert=True)
            
        else:
            if library == "seaborn":
                self.plot = sns.violinplot(data = data, x = x, y = y, ax = self.ax).set(xlabel = None, ylabel = None)
            else:
                self.plot = self.ax.violinplot(dataset = data, vert=False)
            
            
            
            
    
        
    