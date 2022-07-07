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
            for pc in self.plot['bodies']:
                pc.set_edgecolor("black") # add custom color here
            self.ax.set_yticks([1], [''])
            
        elif not x:
            self.plot = self.ax.violinplot(dataset = data[self.y], vert=True)
            for pc in self.plot['bodies']:
                pc.set_edgecolor("blue") # add custom color here
            self.ax.set_xticks([1], [''])
            
        else:
            
            filter_x = []
            cols = list(data[self.y].unique())
            for col in cols:
                filter_x.append(data[data[self.y] == col][self.x])
                
            
            self.plot = self.ax.violinplot(dataset = filter_x, vert=False)
            
            self.ax.set_yticks(np.arange(1, len(cols) + 1), cols)
            
            for i, pc in enumerate(self.plot['bodies']):
                pc.set_facecolor(COLOR_SCHEME[cols[i]])
                pc.set_edgecolor('black')
    
        for partname in ('cbars','cmins','cmaxes'):
            vp = self.plot[partname]
            vp.set_edgecolor("black")
            vp.set_linewidth(1)
    