from .plot import Plot
import matplotlib.pyplot as plt

from .styles.filter_color_scheme import COLOR_SCHEME

import numpy as np 

class ViolinPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, plot_info : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params, plot_info) 
        
        self.x = x
        self.y = y
        
        if not y:
            self.plot = self.ax.violinplot(dataset = data[self.x], vert=False)
            
            
        elif not x:
            self.plot = self.ax.violinplot(dataset = data[self.y], vert=True)
            
        else:
            self.plot = self.ax.violinplot(dataset = data, vert=False)
            
            
            
            
    
        
    