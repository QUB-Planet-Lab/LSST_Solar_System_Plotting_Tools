from .plot import Plot
from seaborn import boxenplot
import matplotlib.pyplot as plt

from typing import Optional

import seaborn as sns

from .styles.filter_color_scheme import COLOR_SCHEME


LIBARIES = ["seaborn", "matplotlib"]

class BoxPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None, library: Optional[str] = "seaborn"):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        self.x = x
        self.y = y
             
        if not y:
            self.plot = self.ax.boxplot(x = data[self.x], labels=[''], vert=False, patch_artist = True)
             
                
        elif not x:
            self.plot = self.ax.boxplot(x = data[self.y], vert=True, patch_artist=True, labels=[''])
                   
        else:
            # add optionality to have the boxes vertically aligned?
            
            
            if library == "seaborn":
                self.plot = sns.boxplot(data = data, x = self.x, y = self.y, ax = self.ax)
            else: 
                self.plot = self.ax.boxplot(x = data, vert=False, patch_artist=True)
            
            
    
class BoxenPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None, library : Optional[str] = "seaborn"):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        self.x = x
        self.y = y
       
        if not y:
            self.plot = boxenplot(x = data[self.x], ax = self.ax).set(xlabel="", ylabel="")
        elif not x:
            self.plot = boxenplot(y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")
            
        else:
            self.plot = boxenplot(x = data[self.x], y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")

        
        
 