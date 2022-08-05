from .plot import Plot
import matplotlib.pyplot as plt
from typing import Optional

from .styles.filter_color_scheme import COLOR_SCHEME

import numpy as np 
import seaborn as sns

class ViolinPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, plot_info : dict = {}, library: Optional[str] = "seaborn", cache_data: Optional[bool] = False, position: Optional[list] = None):
        super().__init__(data, xlabel, ylabel, title, library, cache_data) 
        
        
        
        
         
        self.x = x
        self.y = y
        
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        if not position:    
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
                    self.plot = sns.violinplot(data = data, x = x, y = y, ax = self.ax)
                    self.plot.set(xlabel = None, ylabel = None)
                else:
                    self.plot = self.ax.violinplot(dataset = data, vert=False)
        else:
            self.data = data
            self.position = position
            
    def create_plot(self, ax):
        self.ax = ax

        self.plot = sns.violinplot(data = self.data, x = self.x, y = self.y, ax = self.ax)
        self.plot.set(xlabel = self.xlabel, ylabel = self.ylabel)
            
            
            
    
        
    