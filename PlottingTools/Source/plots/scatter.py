from .plot import Plot
#from seaborn import scatterplot
import matplotlib.pyplot as plt

from typing import Optional, Literal

class ScatterPlot(Plot):
    """Helper object for creating plots"""
    
    def __init__(self, data, x, y, z : Optional[str] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}, projection: Optional[Literal['2d', '3d']] = '2d'):
        """
            :param data
            :param: x, value to be plotted on x scale
        """
        
        super().__init__(data, xlabel, ylabel, title, rc_params)
                
        if projection == '2d':
            if len(yerr) or len(xerr):
                self.plot = self.ax.errorbar(x = data[x], y = data[y], yerr=yerr if len(yerr) else None, xerr=xerr if len(xerr) else None, fmt='o')
            self.plot = self.ax.scatter(x = data[x], y = data[y])
            
        elif projection == '3d':
            self.fig.clear()
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(projection="3d")
            self.plot = self.ax.scatter(xs = data[x], ys = data[y], zs = data[z])
            