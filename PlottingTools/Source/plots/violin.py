from .plot import Plot
from seaborn import violinplot

class ViolinPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, plot_info : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params, plot_info) 
        
        self.x = x
        self.y = y
        
        if not y:
            self.plot = violinplot(x = data[self.x], ax = self.ax).set(xlabel="", ylabel="")
        elif not x:
            self.plot = violinplot(y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")
        else:
            self.plot = violinplot(x = data[self.x], y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")
