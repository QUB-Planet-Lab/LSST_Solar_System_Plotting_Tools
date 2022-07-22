from .plot import Plot
import matplotlib.pyplot as plt

from typing import Optional

import seaborn as sns

from .styles.filter_color_scheme import COLOR_SCHEME


LIBARIES = ["seaborn", "matplotlib"]

class BoxPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None, library: Optional[str] = "seaborn"):
        super().__init__(data, xlabel, ylabel, title, library)
        
        self.x = x
        self.y = y
             
        if not y:
            self.plot = self.ax.boxplot(x = data[self.x], labels=[''], vert=False, patch_artist = True)
             s
                
        elif not x:
            self.plot = self.ax.boxplot(x = data[self.y], vert=True, patch_artist=True, labels=[''])
                   
        else:
            # add optionality to have the boxes vertically aligned?
            
            
            if library == "seaborn":
                self.plot = sns.boxplot(data = data, x = self.x, y = self.y, ax = self.ax).set(xlabel = None, ylabel = None)
                
            else: 
                self.plot = self.ax.boxplot(x = data, vert=False, patch_artist=True)
            
            
    
class BoxenPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None, library : Optional[str] = "seaborn"):
        super().__init__(data, xlabel, ylabel, title, library)
        
        self.x = x
        self.y = y
       
        if not y:
            self.plot = sns.boxenplot(x = data[self.x], ax = self.ax).set(xlabel="", ylabel="")
        elif not x:
            self.plot = sns.boxenplot(y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")
            
        else:
            self.plot = sns.boxenplot(x = data[self.x], y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")

        
        
 