from .plot import Plot
from seaborn import violinplot

class ViolinPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None):
        super().__init__(data, xlabel, ylabel, title, rc_params) 
        
        self.x = x
        self.y = y
        
        if ax:
            self.plot = violinplot(x = data[self.x], y = data[self.y], ax = ax)
        else:
            if not y:
                self.plot = violinplot(x = data[self.x])
            elif not x:
                self.plot = violinplot(y = data[self.y])
            else:
                self.plot = violinplot(x = data[self.x], y = data[self.y])
            