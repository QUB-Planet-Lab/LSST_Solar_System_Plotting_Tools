from .plot import Plot
import matplotlib.pyplot as plt

from typing import Optional

import seaborn as sns

from .styles.filter_color_scheme import COLOR_SCHEME


LIBARIES = ["seaborn"] # , "matplotlib"] # support seaborn currently

class BoxPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None, library: Optional[str] = "seaborn", cache_data: Optional[bool] = False, position : Optional[list] = None):
        super().__init__(data, xlabel, ylabel, title, library, cache_data)
        
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        
        if not position:       
            if not y:
                self.plot = self.ax.boxplot(x = data[self.x], labels=[''], vert=False, patch_artist = True)

            elif not x:
                self.plot = self.ax.boxplot(x = data[self.y], vert=True, patch_artist=True, labels=[''])

            else:
                # add optionality to have the boxes vertically aligned?

                if library == "seaborn":
                    self.plot = sns.boxplot(data = data, x = self.x, y = self.y, ax = self.ax)
                    self.plot.set(xlabel = xlabel, ylabel = ylabel)
                    self.ax.set_xlabel(None) # needs fixed
                    self.ax.set_ylabel(None)
                else: 
                    self.plot = self.ax.boxplot(x = data, vert=False, patch_artist=True)
        else:
            self.data = data
            self.position = position

            
    def create_plot(self, ax):
        self.ax = ax

        self.plot = sns.boxplot(data = self.data, x = self.x, y = self.y, ax = self.ax)
        self.plot.set(xlabel = self.xlabel, ylabel = self.ylabel)
            
            
class BoxenPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None, library : Optional[str] = "seaborn", cache_data: Optional[bool] = False, position : Optional[list] = None):
        super().__init__(data, xlabel, ylabel, title, library, cache_data)
        
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        if not position:
            if not y:
                self.plot = sns.boxenplot(x = data[self.x], ax = self.ax).set(xlabel="", ylabel="")
            elif not x:
                self.plot = sns.boxenplot(y = data[self.y], ax = self.ax)
                self.plot.set(xlabel="", ylabel="")

            else:
                self.plot = sns.boxenplot(x = data[self.x], y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")
        else:
            self.data = data
            self.position = position
            
    def create_plot(self, ax):
        self.ax = ax

        self.plot = sns.boxenplot(data = self.data, x = self.x, y = self.y, ax = self.ax)
        self.plot.set(xlabel = self.xlabel, ylabel = self.ylabel)
         
        
        


            
        
 