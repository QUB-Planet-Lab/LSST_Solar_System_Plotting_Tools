from .plot import Plot
#from seaborn import scatterplot
import matplotlib.pyplot as plt

class ScatterPlot(Plot):
    """Helper object for creating plots"""
    
    def __init__(self, data, x, y, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}):
        """
            :param data
            :param: x, value to be plotted on x scale
        """
        super().__init__(data, xlabel, ylabel, title, rc_params)
        if len(yerr) or len(xerr):
            self.plot = self.ax.errorbar(x = data[x], y = data[y], yerr=yerr if len(yerr) else None, xerr=xerr if len(xerr) else None, fmt='o')
        self.plot = self.ax.scatter(x = data[x], y = data[y])